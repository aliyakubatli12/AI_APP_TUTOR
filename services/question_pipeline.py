"""
Generator -> reviewer -> reviser loop.

Moved here from tests/test_generation.py so the pipeline lives in
application code; tests/test_generation.py now only re-exports it.
Every LLM call goes through llm_client.call_llm with a step name, and
every step is written to a per-request trace (services/trace.py).
"""

import json
import re
import time

from config import get_pipeline_config
from llm_client import call_llm
from prompts.question_generator import generate_question_response
from prompts.reviewer import build_reviewer_prompt
from prompts.revision_generator import build_revision_prompt
from services.generation_request import build_generation_request
from services.trace import Trace, hash_text
from tools.normalazation.clean_json import clean_llm_json

PIPELINE_CONFIG = get_pipeline_config()
MAX_REVIEW_ROUNDS = PIPELINE_CONFIG["max_review_rounds"]


USER_REJECTED_MESSAGE = (
    "We couldn't generate good enough questions for this topic right now. "
    "Please try again, or choose a different topic or difficulty."
)

USER_BUDGET_MESSAGE = (
    "Generating questions is taking longer than expected. "
    "Please try again in a moment."
)


class QuestionsRejectedError(Exception):
    """Raised when the reviewer still rejects the questions after max_rounds."""

    def __init__(self, issues):
        self.issues = issues
        self.user_message = USER_REJECTED_MESSAGE   # safe to show to the user
        super().__init__("Questions rejected by reviewer: " + "; ".join(issues))


class RequestBudgetExceededError(Exception):
    """Raised when a request hits its LLM call count or wall-clock limit."""

    def __init__(self, reason: str):
        self.reason = reason
        self.user_message = USER_BUDGET_MESSAGE     # safe to show to the user
        super().__init__(f"Request budget exceeded: {reason}")


class RequestBudget:
    """Caps total LLM calls and total seconds for one request."""

    def __init__(self, max_calls: int, max_seconds: float):
        self.max_calls = max_calls
        self.max_seconds = max_seconds
        self.calls = 0
        self.started = time.monotonic()

    def elapsed(self) -> float:
        return time.monotonic() - self.started

    def before_call(self) -> None:
        if self.calls >= self.max_calls:
            raise RequestBudgetExceededError(f"max {self.max_calls} LLM calls")
        if self.elapsed() >= self.max_seconds:
            raise RequestBudgetExceededError(f"max {self.max_seconds}s")
        self.calls += 1


def extract_json_object(text: str) -> str:
    text = text.strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in LLM response:\n{text}")

    return match.group(0)


def parse_llm_questions(raw_response: str):
    if not isinstance(raw_response, str):
        raise ValueError(f"LLM response is not a string: {type(raw_response)}")

    cleaned_response = clean_llm_json(raw_response)
    json_text = extract_json_object(cleaned_response)

    try:
        parsed_response = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse extracted JSON: {e}\n\nExtracted JSON:\n{json_text}"
        )

    questions = parsed_response.get("questions", [])
    if not isinstance(questions, list):
        raise ValueError("'questions' must be a list")

    return questions


def _try_parse_questions(raw_response: str):
    """Parse result for the trace only; never raises."""
    try:
        return {"ok": True, "question_count": len(parse_llm_questions(raw_response))}
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def _call_step(prompt: str, step: str, budget: RequestBudget, trace: Trace, difficulty: str | None = None) -> str:
    budget.before_call()
    return call_llm(prompt, step=step, difficulty=difficulty, trace=trace)


def review_questions(raw_response: str, selected_topic: str, difficulty: str,
                     budget: RequestBudget | None = None, trace: Trace | None = None,
                     round_no: int | None = None) -> dict:
    """Ask the reviewer LLM to judge the questions; returns {"status", "issues"}."""
    budget = budget or RequestBudget(PIPELINE_CONFIG["max_llm_calls_per_request"], PIPELINE_CONFIG["max_seconds_per_request"])
    trace = trace or Trace()

    reviewer_prompt = build_reviewer_prompt(raw_response, selected_topic, difficulty)
    review_response = _call_step(reviewer_prompt, "reviewer", budget, trace)
    print("Reviewer Raw Response:\n", review_response)

    try:
        review = json.loads(extract_json_object(clean_llm_json(review_response)))
    except (ValueError, json.JSONDecodeError):
        trace.log("reviewer", round=round_no, output=review_response, parse_ok=False)
        raise ValueError(f"Reviewer output is not valid JSON:\n{review_response}")

    if review.get("status") not in {"accepted", "revise", "rejected"}:
        trace.log("reviewer", round=round_no, output=review_response, parse_ok=True,
                  validation_ok=False, status=review.get("status"))
        raise ValueError(f"Unexpected reviewer status: {review.get('status')}")
    review.setdefault("issues", [])

    trace.log("reviewer", round=round_no, output=review_response, parse_ok=True,
              validation_ok=True, status=review["status"], issues=review["issues"])
    return review


def generate_questions(result, selected_topic, difficulty, max_rounds: int = MAX_REVIEW_ROUNDS,
                       trace: Trace | None = None):
    """Generator -> reviewer -> reviser loop.

    Each round the reviewer checks the latest questions. If they are accepted
    they are returned; otherwise the reviser rewrites them from the reviewer's
    issues and the new version is reviewed again, up to max_rounds reviews.
    The whole request is also capped by LLM call count and total seconds.
    """
    trace = trace or Trace()
    budget = RequestBudget(PIPELINE_CONFIG["max_llm_calls_per_request"], PIPELINE_CONFIG["max_seconds_per_request"])

    request = build_generation_request(result, selected_topic, difficulty)
    trace.log("request", request=request, extracted_topics=result, max_rounds=max_rounds)

    prompt = generate_question_response(request)
    difficulty_lower = difficulty.lower()

    try:
        # 1) First generation
        raw_response = _call_step(prompt, "generator", budget, trace, difficulty_lower)
        print("Generator Raw Response:\n", raw_response)
        trace.log("generator", round=0, input_hash=hash_text(prompt), output=raw_response,
                  parse=_try_parse_questions(raw_response))

        review = {"status": "revise", "issues": []}
        for round_no in range(1, max_rounds + 1):
            # 2) Review the latest version
            review = review_questions(raw_response, selected_topic, difficulty, budget, trace, round_no)
            print(f"Round {round_no}: {review['status']} ({len(review['issues'])} issues)")

            # 3) Accepted -> done
            if review["status"] == "accepted":
                output = {
                    "approved": True,
                    "rounds": round_no,
                    "questions": parse_llm_questions(raw_response),
                    "issues": [],
                    "trace_id": trace.trace_id,
                }
                trace.log("result", approved=True, rounds=round_no, llm_calls=budget.calls,
                          seconds=round(budget.elapsed(), 3))
                return output

            # 4) Last round used up -> stop revising
            if round_no == max_rounds:
                break

            # 5) Revise using the reviewer's issues, then loop back to review
            revision_prompt = build_revision_prompt(request, review)
            raw_response = _call_step(revision_prompt, "reviser", budget, trace, difficulty_lower)
            print("Revised Raw Response:\n", raw_response)
            trace.log("reviser", round=round_no, input_hash=hash_text(revision_prompt), output=raw_response,
                      parse=_try_parse_questions(raw_response))

    except RequestBudgetExceededError as e:
        trace.log("result", approved=False, error="budget_exceeded", reason=e.reason,
                  llm_calls=budget.calls, seconds=round(budget.elapsed(), 3))
        raise
    except Exception as e:
        trace.log("result", approved=False, error=type(e).__name__, detail=str(e),
                  llm_calls=budget.calls, seconds=round(budget.elapsed(), 3))
        raise

    # Never approved within max_rounds.
    # Rejected output is never shown to the user.
    if review["status"] == "rejected":
        trace.log("result", approved=False, status="rejected", rounds=max_rounds, issues=review["issues"],
                  llm_calls=budget.calls, seconds=round(budget.elapsed(), 3))
        raise QuestionsRejectedError(review["issues"])

    # "revise" on the last round: return it, but clearly marked as not approved.
    print(f"Max review rounds ({max_rounds}) reached without approval.")
    output = {
        "approved": False,
        "rounds": max_rounds,
        "questions": parse_llm_questions(raw_response),
        "issues": review["issues"],
        "trace_id": trace.trace_id,
    }
    trace.log("result", approved=False, status="revise", rounds=max_rounds, issues=review["issues"],
              llm_calls=budget.calls, seconds=round(budget.elapsed(), 3))
    return output
