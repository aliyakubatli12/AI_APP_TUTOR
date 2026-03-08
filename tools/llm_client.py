import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"


def call_llm(prompt: str, model: str = "llama-3.1-8b-instant", temperature: float = 0.2) -> str:
    if not API_KEY:
        raise ValueError("GROQ_API_KEY not found")

    payload = { # type: ignore
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(URL, headers=headers, json=payload, timeout=30) # type: ignore
    response.raise_for_status()

    result = response.json()

    if "choices" not in result or not result["choices"]:
        raise ValueError(f"Unexpected API response: {result}")

    return result["choices"][0]["message"]["content"].strip()  # type: ignore