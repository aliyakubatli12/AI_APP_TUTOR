import os
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Read the API key from environment variables
API_KEY = os.getenv("GROQ_API_KEY")

# Groq OpenAI-compatible API endpoint
url = "https://api.groq.com/openai/v1/chat/completions"

# Request payload sent to the LLM API
# It contains the model name and the conversation messages
payload = { # type: ignore
    "model": "llama-3.1-8b-instant",
    "messages": [
        {"role": "user", "content": "Who is hitler?"}
    ]
}

# HTTP headers for authentication and content type
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Send POST request to the API
response = requests.post(url, json=payload, headers=headers) # type: ignore

# Convert response JSON into Python dictionary
data = response.json()

# Print the model's generated response
print(data["choices"][0]["message"]["content"])