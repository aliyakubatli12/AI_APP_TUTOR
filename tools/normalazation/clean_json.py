
def clean_llm_json(raw_text: str) -> str:
    raw_text = raw_text.strip()

    if raw_text.startswith("```json"):
        raw_text = raw_text[len("```json"):].strip()
    elif raw_text.startswith("```"):
        raw_text = raw_text[len("```"):].strip()

    if raw_text.endswith("```"):
        raw_text = raw_text[:-3].strip()

    return raw_text