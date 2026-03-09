import re 

def normalize_topic(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-zA-Z0-9\s\-\+\*]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text