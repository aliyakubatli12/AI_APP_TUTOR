# Function to normalize topic text before using it in topic_matching function
# Example:
# "BFS" -> "bfs"
# " Dynamic Programming!! " -> "dynamic programming"

import re 

def normalize_topic(text: str) -> str:

    # Convert text to lowercase and remove leading/trailing spaces
    text = text.lower().strip()

    # Replace characters that are not letters, numbers, spaces, -, +, *
    # Example: "BFS!!!" -> "bfs   "
    text = re.sub(r"[^a-zA-Z0-9\s\-\+\*]", " ", text)

    # Replace multiple spaces with a single space
    # Example: "dynamic     programming" -> "dynamic programming"
    text = re.sub(r"\s+", " ", text).strip()

    return text