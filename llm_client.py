import os
import requests
import base64
import io
from dotenv import load_dotenv
from typing import Any
from typing import Dict

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"


def call_llm(prompt: str, model: str = "llama-3.1-8b-instant", temperature: float = 0.2) -> str:

    if not API_KEY:
        raise ValueError("GROQ_API_KEY not found")

    payload : Dict[str,Any] = {  
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

    response = requests.post(URL, headers=headers, json=payload, timeout=30) 
    print("Status code:", response.status_code)
    response.raise_for_status()

    result = response.json()

    if "choices" not in result or not result["choices"]:
        raise ValueError(f"Unexpected API response: {result}")

    return result["choices"][0]["message"]["content"].strip()

# Simple test to verify the LLM client works when running this file 
# this block will execute first to test the LLM client delete hashtags
#if __name__ == "__main__":
#    test_prompt = "Say hello in one sentence."
#    result = call_llm(test_prompt)
#    print("FINAL RESULT:", result)

def call_vision_llm(image_bytes: bytes, prompt: str, model: str = "llama-3.2-11b-vision-preview", temperature: float = 0.0) -> str:
    """Specialized function for Vision LLM tasks using image-capable models."""
    if not API_KEY:
        raise ValueError("GROQ_API_KEY not found")

    # Convert image bytes to base64 string
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    payload = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()