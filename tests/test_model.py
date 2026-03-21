"""
Simple script to test a request to the Groq LLM API.

Loads the API key from the environment, sends a prompt to the model,
and prints the generated response from the assistant.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

url = "https://api.groq.com/openai/v1/chat/completions"


payload = { # type: ignore
    "model": "llama-3.1-8b-instant",
    "messages": [
        {"role": "user", "content": "Who is Atatürk?"}
    ]
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers) # type: ignore

data = response.json()

print(data["choices"][0]["message"]["content"])