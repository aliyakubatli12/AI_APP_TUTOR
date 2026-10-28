"""
Loads per-step LLM settings from config/llm_steps.json.

Changing a model or temperature for a step is a config change,
not a code change.
"""

import json
import os
from typing import Any

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "llm_steps.json")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    _CONFIG: dict[str, Any] = json.load(f)


def get_step_config(step: str, difficulty: str | None = None) -> dict[str, Any]:
    """Return defaults merged with the step's own settings.

    If the step defines temperature_by_difficulty, difficulty is required
    and picks the temperature.
    """
    if step not in _CONFIG["steps"]:
        raise ValueError(f"Unknown LLM step: {step}")

    step_config = dict(_CONFIG["defaults"])
    step_config.update(_CONFIG["steps"][step])

    by_difficulty = step_config.pop("temperature_by_difficulty", None)
    if by_difficulty is not None:
        if difficulty is None or difficulty.lower() not in by_difficulty:
            raise ValueError(f"Invalid difficulty for step '{step}': {difficulty}")
        step_config["temperature"] = by_difficulty[difficulty.lower()]

    step_config["step"] = step
    return step_config


def get_defaults() -> dict[str, Any]:
    return dict(_CONFIG["defaults"])


def get_pipeline_config() -> dict[str, Any]:
    return dict(_CONFIG["pipeline"])
