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


def test_generation(result, selected_topic, difficulty):
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

    # 2) Build reviewer prompt
    reviewer_prompt = build_reviewer_prompt(raw_response, selected_topic, difficulty)

    # 3) Call reviewer
    review_response = call_llm(reviewer_prompt, temperature=0.2)
    print("Reviewer Raw Response:\n", review_response)

    # 4) Parse reviewer output
    import json
    try:
        review = json.loads(review_response)
    except json.JSONDecodeError:
        raise ValueError("Reviewer output is not valid JSON.")

    # 5) If accepted, return original generated questions
    if review["status"] == "accepted":
        return parse_llm_questions(raw_response)

    # 6) If revise or rejected, build revision prompt
    revision_prompt = build_revision_prompt(request, review)

    # 7) Call generator again with revision prompt
    revised_response = call_llm(revision_prompt, temperature=temperature)
    print("Revised Raw Response:\n", revised_response)

    return revised_response


    


if __name__ == "__main__":
    result = {
        "specific_topics": ["Kruskal", "Fibonacci"],
        "general_topics": ["Graph Algorithms"]
    }

    difficulty = "Medium"

    questions = test_generation(result, "Kruskal", difficulty)

    for i, q in enumerate(questions, start=1):
        print(f"\nQuestion {i}:")
        print("Title:", q.get("title", "Untitled"))
        print("Text:", q.get("question_text", ""))