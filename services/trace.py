"""
Per-request trace: every pipeline step appends one JSON line to
traces/<trace_id>.jsonl so a bad question can be traced back to the
step where it went wrong, without guessing.
"""

import hashlib
import json
import os
import time
import uuid
from typing import Any

TRACES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "traces")


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


class Trace:
    def __init__(self, trace_id: str | None = None, traces_dir: str = TRACES_DIR):
        self.trace_id = trace_id or uuid.uuid4().hex
        self.path = os.path.join(traces_dir, f"{self.trace_id}.jsonl")
        os.makedirs(traces_dir, exist_ok=True)

    def log(self, event: str, **fields: Any) -> None:
        record = {"trace_id": self.trace_id, "ts": time.time(), "event": event, **fields}
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
