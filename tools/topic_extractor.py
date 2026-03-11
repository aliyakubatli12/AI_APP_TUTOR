"""
Extracts computer science topics from raw text.

Uses a two-stage approach:
1. If the text looks like a simple topic list → regex + dictionary matching.
2. Otherwise → calls an LLM to extract topics and validates the JSON output.
"""

import json
from tools.llm_client import call_llm
from prompts.topic_prompt import build_topic_prompt
from .topic_regex_finder import looks_like_topic_list 
from .topic_matching import match_topics
import re

# Main function to extract topics from raw text
# Example input:
# "BFS\nDFS\nDynamic Programming"
# or
# "Today we studied BFS and Dijkstra's algorithm"

def extract_topics(raw_text: str) -> dict[str, list[str]]:

    # If the text already looks like a topic list
    # Example:
    # "BFS\nDFS\nDynamic Programming"
    # then we skip the LLM and use regex + direct matching
    if(looks_like_topic_list(raw_text)):
        print("REGEX USED ")

        # Split topics by newline, ; / or |
        # Example: "BFS\nDFS;Dijkstra" -> ["BFS","DFS","Dijkstra"]
        parts = re.split(r"[\n;/|]+", raw_text)

        # Remove empty values and extra spaces
        parts = [p.strip() for p in parts if p.strip()]

        # Match extracted parts with known topic lists
        return match_topics(parts) # type: ignore

    else:

        specific_topics: list[str] = []
        general_topics: list[str] = []
        # Build prompt for the LLM
        # The prompt instructs the model to extract topics
        prompt = build_topic_prompt(raw_text)

        # Call LLM with deterministic output
        content = call_llm(prompt, temperature=0.0)

        try:
            # Convert model response from JSON string to Python dict
            topics_json = json.loads(content)

        except json.JSONDecodeError:
            # Raise error if model response is not valid JSON
            raise ValueError(f"Model did not return valid JSON:\n{content}")

        # Ensure response is a dictionary
        if not isinstance(topics_json, dict):
            raise ValueError("Response is not a JSON object")

        # Ensure required keys exist
        if "specific_topics" not in topics_json or "general_topics" not in topics_json:
            raise ValueError("Missing 'specific_topics' or 'general_topics' key")

        # Ensure both values are lists
        if not isinstance(topics_json["specific_topics"], list) or not isinstance(topics_json["general_topics"], list):
            raise ValueError("'specific_topics' and 'general_topics' must be lists")

    # Ensure every element inside the lists is a string
    if not all(isinstance(item, str) for item in topics_json["specific_topics"]) or not all(isinstance(item, str) for item in topics_json["general_topics"]): # type: ignore
        raise ValueError("All topics must be strings")
    
    specific_topics = topics_json.get("specific_topics", [])  # type: ignore
    general_topics = topics_json.get("general_topics", [])    # type: ignore

    if specific_topics and general_topics:
        # If a topic appears in both specific_topics and general_topics, keep it only in general_topics
        specific_topics = [
            topic for topic in specific_topics  # type: ignore
            if topic not in general_topics
        ]

    # Return validated topic dictionary
    return {"specific_topics": specific_topics, "general_topics": general_topics}  # type: ignore