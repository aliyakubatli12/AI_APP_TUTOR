import json
from tools.llm_client import call_llm
from prompts.topic_prompt import build_topic_prompt
from .topic_regex_finder import looks_like_topic_list 
from .topic_matching import match_topics
import re

def extract_topics(raw_text: str) -> dict[str, list[str]]:
    if(looks_like_topic_list(raw_text)):
        print("REGEX USED ")
        parts = re.split(r"[\n;/|]+", raw_text)
        parts = [p.strip() for p in parts if p.strip()]
        return match_topics(parts) # type: ignore
    else:

        prompt = build_topic_prompt(raw_text)
        content = call_llm(prompt, temperature=0.0)

        try:
            topics_json = json.loads(content)
        except json.JSONDecodeError:
            raise ValueError(f"Model did not return valid JSON:\n{content}")

        if not isinstance(topics_json, dict):
            raise ValueError("Response is not a JSON object")

        if "specific_topics" not in topics_json or "general_topics" not in topics_json:
            raise ValueError("Missing 'specific_topics' or 'general_topics' key")

        if not isinstance(topics_json["specific_topics"], list) or not isinstance(topics_json["general_topics"], list):
            raise ValueError("'specific_topics' and 'general_topics' must be lists")

        if not all(isinstance(item, str) for item in topics_json["specific_topics"]) or not all(isinstance(item, str) for item in topics_json["general_topics"]): # type: ignore
            raise ValueError("All topics must be strings")

        return topics_json # type: ignore