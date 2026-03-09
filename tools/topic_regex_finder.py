import re

STOPWORDS = {
    "a", "an", "the", "and", "or", "but",
    "we", "you", "they", "he", "she", "it",
    "is", "are", "was", "were", "be", "been",
    "in", "on", "at", "to", "from", "of", "for", "with",
    "today", "yesterday", "this", "that", "these", "those",
    "studied", "learned", "covered", "discussed"
}




def looks_like_topic_list(text: str) -> bool:
    text = text.strip()

    if not text:
        return False

    parts = re.split(r'[\n;/|]+', text)
    parts = [p.strip() for p in parts if p.strip()]
    
    words = re.findall(r"[a-zA-Z]+(?:'[a-zA-Z]+)?", text)

    if not words:
        return False

    stopword_count = sum(1 for word in words if word.lower() in STOPWORDS)
    if stopword_count / len(words) > 0.5:
        return False

    if len(parts) < 2:
        return False
  
    short_count = 0
    for part in parts:
        word_count = len(part.split())
        if 1 <= word_count <= 4:
            short_count += 1

    return short_count / len(parts) >= 0.8