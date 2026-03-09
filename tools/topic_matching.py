import json 
from .normalize_topic import normalize_topic

with open("topics/general_topics.json") as f:
    GENERAL_TOPICS = json.load(f)
with open("topics/specific_topics.json") as f:
    SPECIFIC_TOPICS = json.load(f)
with open("topics/topic_mapping.json") as f:
    TOPIC_MAPPING = json.load(f)

GENERAL_TOPICS_NORM = {topic.lower(): topic for topic in GENERAL_TOPICS}
SPECIFIC_TOPICS_NORM = {topic.lower(): topic for topic in SPECIFIC_TOPICS}

def match_topics(parts: list[str]) -> dict[str, list[str]]: 
    

    specific_topics: list[str] = []
    general_topics: list[str] = []

    for part in parts:
        norm=normalize_topic(part)
        if norm in SPECIFIC_TOPICS_NORM:
            canonical_specific = SPECIFIC_TOPICS_NORM[norm]
            specific_topics.append(canonical_specific)
        
            mapped_general = TOPIC_MAPPING.get(canonical_specific)
            if mapped_general and mapped_general not in general_topics:
                general_topics.append(mapped_general)
        elif norm in GENERAL_TOPICS_NORM:
            canonical_general = GENERAL_TOPICS_NORM[norm]
            if canonical_general not in general_topics:
                general_topics.append(canonical_general)

    return {
        "specific_topics": list(dict.fromkeys(specific_topics)),
        "general_topics": list(dict.fromkeys(general_topics))
    }
