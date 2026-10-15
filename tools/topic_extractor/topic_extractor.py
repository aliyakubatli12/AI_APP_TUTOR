

import json
from llm_client import call_llm
from prompts.topic_prompt import build_topic_prompt
from .topic_regex_finder import looks_like_topic_list 
from .topic_matching import match_topics
import re
import os

# Main function to extract topics from raw text
# Example input:
# "BFS\nDFS\nDynamic Programming"
# or
# "Today we studied BFS and Dijkstra's algorithm"

current_dir = os.path.dirname(os.path.abspath(__file__))

json_path = os.path.join(current_dir, "..", "..", "topics", "topic_mapping.json")

try:
    with open(json_path, "r", encoding="utf-8") as f:
        topic_mapping = json.load(f)
except FileNotFoundError:
    print(f"ERROR: {json_path} file not found!")
    topic_mapping = {}

aliases_path = os.path.join(current_dir, "..", "..", "topics", "topic_aliases.json")

try:
    with open(aliases_path, "r", encoding="utf-8") as f:
        topic_aliases = json.load(f)
except FileNotFoundError:
    print(f"ERROR: {aliases_path} file not found!")
    topic_aliases = {}

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

        for i, part in enumerate(parts):
            norm_part = part.lower()
            # Check if the part matches any known topic alias
            for canonical, aliases in topic_aliases.items():
                if norm_part in aliases:
                    parts[i] = canonical  # Replace with canonical topic name
                    break
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

    for i, topic in enumerate(specific_topics):  # type: ignore
        for canonical, aliases in topic_aliases.items():
            if topic.lower() in aliases:
                specific_topics[i] = canonical
                break

    for i, topic in enumerate(general_topics):  # type: ignore
        for canonical, aliases in topic_aliases.items():
            if topic.lower() in aliases:
                general_topics[i] = canonical
                break


    specific_keys= set(topic_mapping.keys()) # type: ignore
    general_keys = set(topic_mapping.values())

    corrected_specific_topics = []
    corrected_general_topics = list(general_topics)  # type: ignore # Start with original general topics    
   
    #if llm puts general topic to specific topic but it is in general topics
    for topic in specific_topics: # type: ignore
        if topic in general_keys:
            if topic not in corrected_general_topics:
                corrected_general_topics.append(topic) # type: ignore
        else:
            corrected_specific_topics.append(topic) # type: ignore
    #if llm puts specific topic to general topic but it is in specific topics
    for topic in general_topics:#  type: ignore
        if topic in specific_keys:
            if topic not in corrected_specific_topics:
                corrected_specific_topics.append(topic) # type: ignore
            corrected_general_topics.remove(topic)  # type: ignore
        else:
            if topic not in corrected_general_topics:
                corrected_general_topics.append(topic) # type: ignore




    # Return validated topic dictionary
    return {"specific_topics": corrected_specific_topics, "general_topics": corrected_general_topics}  # type: ignore