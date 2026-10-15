from prompts.question_generator import generate_question_response
from llm_client import call_llm
from services.generation_request import build_generation_request
from tools.normalazation.clean_json import clean_llm_json
from prompts.reviewer import build_reviewer_prompt
from prompts.revision_generator import build_revision_prompt

import json
import re


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


MAX_REVIEW_ROUNDS = 3


class QuestionsRejectedError(Exception):
    """Raised when the reviewer still rejects the questions after max_rounds."""

    def __init__(self, issues):
        self.issues = issues
        super().__init__("Questions rejected by reviewer: " + "; ".join(issues))


def review_questions(raw_response: str, selected_topic: str, difficulty: str) -> dict:
    """Ask the reviewer LLM to judge the questions; returns {"status", "issues"}."""
    reviewer_prompt = build_reviewer_prompt(raw_response, selected_topic, difficulty)
    review_response = call_llm(reviewer_prompt, temperature=0.2)
    print("Reviewer Raw Response:\n", review_response)

    try:
        review = json.loads(extract_json_object(clean_llm_json(review_response)))
    except (ValueError, json.JSONDecodeError):
        raise ValueError(f"Reviewer output is not valid JSON:\n{review_response}")

    if review.get("status") not in {"accepted", "revise", "rejected"}:
        raise ValueError(f"Unexpected reviewer status: {review.get('status')}")
    review.setdefault("issues", [])
    return review


def test_generation(result, selected_topic, difficulty, max_rounds: int = MAX_REVIEW_ROUNDS):
    """Generator -> reviewer -> reviser loop.

    Each round the reviewer checks the latest questions. If they are accepted
    they are returned; otherwise the reviser rewrites them from the reviewer's
    issues and the new version is reviewed again, up to max_rounds reviews.
    """
    request = build_generation_request(result, selected_topic, difficulty)
    prompt = generate_question_response(request)

    difficulty_lower = difficulty.lower()

    if difficulty_lower == "easy":
        temperature = 0.3
    elif difficulty_lower == "medium":
        temperature = 0.5
    elif difficulty_lower == "hard":
        temperature = 0.7
    else:
        raise ValueError(f"Invalid difficulty: {difficulty}")

    # 1) First generation
    raw_response = call_llm(prompt, temperature=temperature)
    print("Generator Raw Response:\n", raw_response)

    review = {"status": "revise", "issues": []}
    for round_no in range(1, max_rounds + 1):
        # 2) Review the latest version
        review = review_questions(raw_response, selected_topic, difficulty)
        print(f"Round {round_no}: {review['status']} ({len(review['issues'])} issues)")

        # 3) Accepted -> done
        if review["status"] == "accepted":
            return {
                "approved": True,
                "rounds": round_no,
                "questions": parse_llm_questions(raw_response),
                "issues": [],
            }

        # 4) Last round used up -> stop revising
        if round_no == max_rounds:
            break

        # 5) Revise using the reviewer's issues, then loop back to review
        revision_prompt = build_revision_prompt(request, review)
        raw_response = call_llm(revision_prompt, temperature=temperature)
        print("Revised Raw Response:\n", raw_response)

    # Never approved within max_rounds.
    # Rejected output is never shown to the user.
    if review["status"] == "rejected":
        raise QuestionsRejectedError(review["issues"])

    # "revise" on the last round: return it, but clearly marked as not approved.
    print(f"Max review rounds ({max_rounds}) reached without approval.")
    return {
        "approved": False,
        "rounds": max_rounds,
        "questions": parse_llm_questions(raw_response),
        "issues": review["issues"],
    }


if __name__ == "__main__":
    result = {
        "specific_topics": ["Kruskal", "Fibonacci"],
        "general_topics": ["Graph Algorithms"]
    }

    difficulty = "Medium"

    try:
        output = test_generation(result, "Kruskal", difficulty)
    except QuestionsRejectedError as e:
        print("\nQuestions were rejected and will not be shown.")
        for issue in e.issues:
            print(" -", issue)
        raise SystemExit(1)

    if not output["approved"]:
        print("\nWARNING: not approved by the reviewer. Open issues:")
        for issue in output["issues"]:
            print(" -", issue)

    for i, q in enumerate(output["questions"], start=1):
        print(f"\nQuestion {i}:")
        print("Title:", q.get("title", "Untitled"))
        print("Text:", q.get("question_text", ""))
