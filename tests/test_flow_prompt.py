from prompts.question_generator import generate_question_response
from llm_client import call_llm
from services.generation_request import build_generation_request
from prompts.reviewer import build_reviewer_prompt
from prompts.revision_generator import build_revision_prompt
import json


req = {
    "specific_topic": "Binary Search Trees",
    "general_topic": "Data Structures",
    "difficulty": "medium",
    "question_count": 2
}

review_text = """
{
  "questions": [
    {
      "title": "Merge Sort Split Step",
      "question_text": "Explain how merge sort recursively divides an array into smaller parts."
    }
  ]
}
"""

reviewer_prompt = build_reviewer_prompt(review_text, "Binary Search Trees", "medium")
# print(reviewer_prompt)

review_raw = call_llm(reviewer_prompt, temperature=0.2)
print(review_raw)

review_data = json.loads(review_raw)
revised_prompt = build_revision_prompt(req, review_data)
revised_answer = call_llm(revised_prompt, temperature=0.5)
print(revised_answer)
