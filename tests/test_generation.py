"""
Manual run of the question pipeline (needs GROQ_API_KEY).

The pipeline itself moved to services/question_pipeline.py; the names below
are re-exported so existing imports (e.g. tools/UI.py) keep working.
"""

from services.question_pipeline import (
    MAX_REVIEW_ROUNDS,
    USER_REJECTED_MESSAGE,
    QuestionsRejectedError,
    RequestBudgetExceededError,
    extract_json_object,
    generate_questions,
    parse_llm_questions,
    review_questions,
)

# This is a manual script, not a pytest module.
__test__ = False


def test_generation(result, selected_topic, difficulty, max_rounds: int = MAX_REVIEW_ROUNDS):
    return generate_questions(result, selected_topic, difficulty, max_rounds)


if __name__ == "__main__":
    result = {
        "specific_topics": ["Kruskal", "Fibonacci"],
        "general_topics": ["Graph Algorithms"]
    }

    difficulty = "Medium"

    try:
        output = test_generation(result, "Kruskal", difficulty)
    except (QuestionsRejectedError, RequestBudgetExceededError) as e:
        print("\n" + e.user_message)              # message for the user
        if isinstance(e, QuestionsRejectedError):
            print("\n[debug] Reviewer issues:")   # details for the developer
            for issue in e.issues:
                print(" -", issue)
        raise SystemExit(1)

    print("\nTrace:", output["trace_id"])

    if not output["approved"]:
        print("\nWARNING: not approved by the reviewer. Open issues:")
        for issue in output["issues"]:
            print(" -", issue)

    for i, q in enumerate(output["questions"], start=1):
        print(f"\nQuestion {i}:")
        print("Title:", q.get("title", "Untitled"))
        print("Text:", q.get("question_text", ""))
