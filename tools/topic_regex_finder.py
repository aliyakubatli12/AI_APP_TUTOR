import re

# Common stopwords that usually appear in sentences
# If a text contains too many of these, it probably is not a topic list
STOPWORDS = {
    "a", "an", "the", "and", "or", "but",
    "we", "you", "they", "he", "she", "it",
    "is", "are", "was", "were", "be", "been",
    "in", "on", "at", "to", "from", "of", "for", "with",
    "today", "yesterday", "this", "that", "these", "those",
    "studied", "learned", "covered", "discussed"
}


# Detect whether the input text looks like a list of topics
# Example (True):
# "BFS\nDFS\nDynamic Programming"
#
# Example (False):
# "Today we studied BFS and DFS in class"

def looks_like_topic_list(text: str) -> bool:

    # Remove leading/trailing spaces
    text = text.strip()

    # Empty text cannot be a topic list
    if not text:
        return False

    # Split text by newline, ; / or |
    # Example: "BFS\nDFS;Dijkstra" -> ["BFS","DFS","Dijkstra"]
    parts = re.split(r'[\n;/|]+', text)

    # Remove empty elements and extra spaces
    parts = [p.strip() for p in parts if p.strip()]
    
    # Extract all words from the text
    # Example: "Today we studied BFS" -> ["Today","we","studied","BFS"]
    words = re.findall(r"[a-zA-Z]+(?:'[a-zA-Z]+)?", text)

    # If there are no words, it is not a valid topic list
    if not words:
        return False

    # Count how many words are stopwords
    stopword_count = sum(1 for word in words if word.lower() in STOPWORDS)

    # If more than 50% of the words are stopwords,
    # the text likely is a sentence rather than a topic list
    if stopword_count / len(words) > 0.5:
        return False

    # Topic lists should contain at least 2 items
    if len(parts) < 2:
        return False
  
    # Count how many parts are short (typical topic length)
    short_count = 0

    for part in parts:

        # Count number of words in each part
        # Example: "Dynamic Programming" -> 2
        word_count = len(part.split())

        # Most topics are short phrases (1–4 words)
        if 1 <= word_count <= 4:
            short_count += 1

    # If at least 80% of the parts are short phrases,
    # we consider the text to be a topic list
    return short_count / len(parts) >= 0.8