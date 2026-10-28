"""
Offline tests for llm_client retry/timeout behaviour and the pipeline's
trace + request budget. requests.post and call_llm are mocked; no network.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
import requests

import llm_client
from config import get_step_config
from services import question_pipeline
from services.trace import Trace


def _response(status: int, content: str = "ok", headers: dict | None = None):
    resp = MagicMock()
    resp.status_code = status
    resp.headers = headers or {}
    resp.json.return_value = {
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
    }
    if status >= 400:
        resp.raise_for_status.side_effect = requests.HTTPError(f"HTTP {status}")
    else:
        resp.raise_for_status.return_value = None
    return resp


@pytest.fixture(autouse=True)
def _fake_key_and_no_sleep(monkeypatch):
    monkeypatch.setattr(llm_client, "API_KEY", "test-key")
    monkeypatch.setattr(llm_client.time, "sleep", lambda s: None)


def test_step_config_by_difficulty():
    assert get_step_config("generator", "Hard")["temperature"] == 0.7
    assert get_step_config("topic_extraction")["temperature"] == 0.0
    with pytest.raises(ValueError):
        get_step_config("generator")


def test_old_signature_uses_defaults():
    with patch.object(llm_client.requests, "post", return_value=_response(200, " hi ")) as post:
        assert llm_client.call_llm("p", temperature=0.0) == "hi"
    payload = post.call_args.kwargs["json"]
    assert payload["model"] == "openai/gpt-oss-20b"
    assert payload["temperature"] == 0.0
    assert post.call_args.kwargs["timeout"] == 30


def test_retries_on_429_then_succeeds():
    responses = [_response(429, headers={"retry-after": "1"}), _response(503), _response(200, "done")]
    with patch.object(llm_client.requests, "post", side_effect=responses) as post:
        assert llm_client.call_llm("p", step="reviewer") == "done"
    assert post.call_count == 3


def test_retries_on_timeout_then_gives_up():
    with patch.object(llm_client.requests, "post", side_effect=requests.Timeout("slow")) as post:
        with pytest.raises(requests.Timeout):
            llm_client.call_llm("p", step="reviewer")
    assert post.call_count == 1 + get_step_config("reviewer")["max_retries"]


def test_no_retry_on_400():
    with patch.object(llm_client.requests, "post", return_value=_response(400)) as post:
        with pytest.raises(requests.HTTPError):
            llm_client.call_llm("p", step="reviewer")
    assert post.call_count == 1


def test_trace_records_tokens(tmp_path):
    trace = Trace(traces_dir=str(tmp_path))
    with patch.object(llm_client.requests, "post", return_value=_response(200)):
        llm_client.call_llm("p", step="generator", difficulty="easy", trace=trace)
    record = json.loads(open(trace.path).read().splitlines()[0])
    assert record["event"] == "llm_call"
    assert record["step"] == "generator"
    assert record["temperature"] == 0.3
    assert record["input_tokens"] == 10


QUESTIONS = json.dumps({"questions": [{"title": "t", "question_text": "q"}]})
TOPICS = {"specific_topics": ["Kruskal"], "general_topics": ["Graph Algorithms"]}


def _fake_llm(outputs):
    calls = []

    def fake(prompt, step=None, difficulty=None, trace=None, **kwargs):
        calls.append(step)
        return outputs.pop(0)

    return fake, calls


def test_pipeline_revise_then_accept_writes_trace(tmp_path):
    fake, calls = _fake_llm([
        QUESTIONS,
        json.dumps({"status": "revise", "issues": ["cycle in Kruskal example"]}),
        QUESTIONS,
        json.dumps({"status": "accepted", "issues": []}),
    ])
    trace = Trace(traces_dir=str(tmp_path))
    with patch.object(question_pipeline, "call_llm", fake):
        out = question_pipeline.generate_questions(TOPICS, "Kruskal", "Medium", trace=trace)

    assert out["approved"] and out["rounds"] == 2
    assert calls == ["generator", "reviewer", "reviser", "reviewer"]
    events = [json.loads(line)["event"] for line in open(trace.path)]
    assert events == ["request", "generator", "reviewer", "reviser", "reviewer", "result"]


def test_pipeline_rejected_after_max_rounds(tmp_path):
    rejected = json.dumps({"status": "rejected", "issues": ["off-topic"]})
    fake, _ = _fake_llm([QUESTIONS, rejected, QUESTIONS, rejected, QUESTIONS, rejected])
    with patch.object(question_pipeline, "call_llm", fake):
        with pytest.raises(question_pipeline.QuestionsRejectedError):
            question_pipeline.generate_questions(TOPICS, "Kruskal", "easy", trace=Trace(traces_dir=str(tmp_path)))


def test_pipeline_call_budget(tmp_path, monkeypatch):
    monkeypatch.setitem(question_pipeline.PIPELINE_CONFIG, "max_llm_calls_per_request", 2)
    revise = json.dumps({"status": "revise", "issues": ["x"]})
    fake, calls = _fake_llm([QUESTIONS, revise, QUESTIONS, revise])
    trace = Trace(traces_dir=str(tmp_path))
    with patch.object(question_pipeline, "call_llm", fake):
        with pytest.raises(question_pipeline.RequestBudgetExceededError):
            question_pipeline.generate_questions(TOPICS, "Kruskal", "easy", trace=trace)
    assert len(calls) == 2
    last = json.loads(open(trace.path).read().splitlines()[-1])
    assert last["error"] == "budget_exceeded"


def test_ui_import_still_works():
    from tests.test_generation import test_generation, QuestionsRejectedError  # noqa: F401
