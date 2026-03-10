import json 
from .normalize_topic import normalize_topic

# Load topic definitions from JSON files
# general_topics.json -> list of general topics
# specific_topics.json -> list of specific topics
# topic_mapping.json -> maps specific topics to their general category

with open("topics/general_topics.json") as f:
    GENERAL_TOPICS = json.load(f)

with open("topics/specific_topics.json") as f:
    SPECIFIC_TOPICS = json.load(f)

with open("topics/topic_mapping.json") as f:
    TOPIC_MAPPING = json.load(f)


# Create normalized lookup dictionaries
# key   -> normalized topic (lowercase)
# value -> canonical topic name

GENERAL_TOPICS_NORM = {topic.lower(): topic for topic in GENERAL_TOPICS}
SPECIFIC_TOPICS_NORM = {topic.lower(): topic for topic in SPECIFIC_TOPICS}


# Match extracted text parts with known topics
# Example input:
# ["bfs", "dfs", "dynamic programming"]

def match_topics(parts: list[str]) -> dict[str, list[str]]: 
    
    # Lists that will store detected topics
    specific_topics: list[str] = []
    general_topics: list[str] = []

    for part in parts:

        # Normalize input text
        # Example: "BFS " -> "bfs"
        norm = normalize_topic(part)

        # Check if the normalized text matches a specific topic
        if norm in SPECIFIC_TOPICS_NORM:

            # Get canonical specific topic name
            # Example: "bfs" -> "BFS"
            canonical_specific = SPECIFIC_TOPICS_NORM[norm]

            specific_topics.append(canonical_specific)
        
            # Find corresponding general topic
            # Example: "BFS" -> "Graph Algorithms"
            mapped_general = TOPIC_MAPPING.get(canonical_specific)

            if mapped_general is not None and mapped_general not in general_topics:
                general_topics.append(mapped_general)

        # If not a specific topic, check if it matches a general topic
        elif norm in GENERAL_TOPICS_NORM:

            canonical_general = GENERAL_TOPICS_NORM[norm]

            if canonical_general not in general_topics:
                general_topics.append(canonical_general)


    # Remove duplicates while preserving order
    # dict.fromkeys keeps insertion order
    return {
        "specific_topics": list(dict.fromkeys(specific_topics)),
        "general_topics": list(dict.fromkeys(general_topics))
    }