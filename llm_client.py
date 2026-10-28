import os
import requests
import base64
import io
import logging
import random
import time
from dotenv import load_dotenv
from typing import Any
from typing import Dict

from config import get_defaults, get_step_config

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

logger = logging.getLogger("llm_client")

# Transient failures worth retrying; any other 4xx is a request error and is raised at once.
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


# NOT (Ali -> Mehmet): call_llm'i ben (Ali) yeniden yazdım; imza geriye uyumlu,
# senin pdf_service.py'deki call_llm(prompt, temperature=0.0) çağrın aynen çalışır.
# Yeni olan: 429/5xx/timeout'ta retry, print yerine logging. call_vision_llm'e dokunmadım.
def call_llm(
    prompt: str,
    model: str | None = None,
    temperature: float | None = None,
    step: str | None = None,
    difficulty: str | None = None,
    trace: Any = None,
    prompt_version: str | None = None,
) -> str:
    """Single gateway for text LLM calls.

    If step is given, model/temperature/timeout/retries come from
    config/llm_steps.json; explicit model/temperature arguments override it.
    Without step, the config defaults are used (old behaviour).
    """
    if not API_KEY:
        raise ValueError("GROQ_API_KEY not found")

    settings = get_step_config(step, difficulty) if step else get_defaults()
    if model is not None:
        settings["model"] = model
    if temperature is not None:
        settings["temperature"] = temperature

    payload : Dict[str,Any] = {
        "model": settings["model"],
        "temperature": settings["temperature"],
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }


    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    max_retries = settings["max_retries"]
    started = time.monotonic()
    attempt = 0

    while True:
        attempt += 1
        error: str | None = None
        try:
            response = requests.post(URL, headers=headers, json=payload, timeout=settings["timeout_seconds"])
            if response.status_code in RETRYABLE_STATUS and attempt <= max_retries:
                error = f"HTTP {response.status_code}"
                delay = _retry_delay(attempt, settings, response.headers.get("retry-after"))
            else:
                response.raise_for_status()
                break
        except (requests.Timeout, requests.ConnectionError) as e:
            if attempt > max_retries:
                _log_call(settings, prompt_version, attempt, started, None, repr(e), trace)
                raise
            error = repr(e)
            delay = _retry_delay(attempt, settings, None)
        except requests.HTTPError as e:
            _log_call(settings, prompt_version, attempt, started, None, repr(e), trace)
            raise

        logger.warning("step=%s attempt=%d failed (%s), retrying in %.1fs", settings.get("step"), attempt, error, delay)
        time.sleep(delay)

    result = response.json()

    if "choices" not in result or not result["choices"]:
        _log_call(settings, prompt_version, attempt, started, result.get("usage"), "no choices in response", trace)
        raise ValueError(f"Unexpected API response: {result}")

    _log_call(settings, prompt_version, attempt, started, result.get("usage"), None, trace)
    return result["choices"][0]["message"]["content"].strip()


def _retry_delay(attempt: int, settings: Dict[str, Any], retry_after: str | None) -> float:
    """Exponential backoff with full jitter; honours Retry-After when the server sends it."""
    if retry_after:
        try:
            return min(float(retry_after), settings["backoff_max_seconds"])
        except ValueError:
            pass
    cap = min(settings["backoff_max_seconds"], settings["backoff_base_seconds"] * 2 ** (attempt - 1))
    return random.uniform(0, cap)


def _log_call(settings, prompt_version, attempts, started, usage, error, trace) -> None:
    record = {
        "step": settings.get("step"),
        "model": settings["model"],
        "temperature": settings["temperature"],
        "prompt_version": prompt_version,
        "attempts": attempts,
        "duration_seconds": round(time.monotonic() - started, 3),
        "input_tokens": (usage or {}).get("prompt_tokens"),
        "output_tokens": (usage or {}).get("completion_tokens"),
        "error": error,
    }
    if error:
        logger.error("llm_call %s", record)
    else:
        logger.info("llm_call %s", record)
    if trace is not None:
        trace.log("llm_call", **record)

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