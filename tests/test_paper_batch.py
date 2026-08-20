"""Provider batch transport for hosted paper cells that do not need a live reply."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from clinical_extraction.paper.batch import (
    OPENAI_BATCH_MODEL,
    OPENROUTER_GEMINI_MODEL,
    BatchChatItem,
    chat_completion_body,
    complete_chat_batch,
    extract_assistant_text,
    openai_batch_jsonl,
    openrouter_batch_payload,
    uses_provider_batch,
)
from clinical_extraction.paper.exect import MODELS
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    hybrid_structured_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import llm as gan_llm_only


def test_luna_and_gemini_use_provider_batch_grok_does_not() -> None:
    assert uses_provider_batch("gpt56luna") is True
    assert uses_provider_batch("gemini37flash") is True
    assert uses_provider_batch("grok46") is False
    assert uses_provider_batch("deepseek_v4_flash") is False


def test_luna_batch_body_uses_native_openai_model() -> None:
    body = chat_completion_body(
        MODELS["gpt56luna"],
        messages=[{"role": "user", "content": "hi"}],
        max_tokens=1200,
    )
    assert body["model"] == OPENAI_BATCH_MODEL == "gpt-5.6-luna"
    assert body["max_completion_tokens"] == 1200
    assert "max_tokens" not in body
    assert body["reasoning_effort"] == "low"
    assert body["temperature"] == 1.0


def test_gemini_batch_body_uses_openrouter_slug() -> None:
    body = chat_completion_body(
        MODELS["gemini37flash"],
        messages=[{"role": "user", "content": "hi"}],
        max_tokens=5000,
    )
    assert body["model"] == OPENROUTER_GEMINI_MODEL == "google/gemini-3.7-flash"
    assert body["max_tokens"] == 5000
    assert body["reasoning"] == {"effort": "low"}
    assert body["temperature"] == 0.0


def test_openrouter_payload_puts_endpoint_and_model_before_requests() -> None:
    item = BatchChatItem(
        custom_id="11",
        messages=[{"role": "user", "content": "note"}],
    )
    payload = openrouter_batch_payload(
        MODELS["gemini37flash"],
        [item],
        max_tokens=5000,
    )
    assert list(payload)[:3] == ["endpoint", "model", "requests"]
    assert payload["endpoint"] == "/v1/chat/completions"
    assert payload["model"] == OPENROUTER_GEMINI_MODEL
    assert payload["requests"][0]["custom_id"] == "11"
    assert payload["requests"][0]["body"]["messages"][0]["content"] == "note"


def test_openai_jsonl_uses_chat_completions_batch_lines() -> None:
    item = BatchChatItem(
        custom_id="11",
        messages=[{"role": "user", "content": "note"}],
    )
    line = openai_batch_jsonl(MODELS["gpt56luna"], [item], max_tokens=1200)
    row = json.loads(line.strip())
    assert row["method"] == "POST"
    assert row["url"] == "/v1/chat/completions"
    assert row["custom_id"] == "11"
    assert row["body"]["model"] == OPENAI_BATCH_MODEL


def test_extract_assistant_text_from_chat_completion() -> None:
    text = extract_assistant_text(
        {
            "choices": [
                {"message": {"role": "assistant", "content": '{"events": []}'}}
            ]
        }
    )
    assert text == '{"events": []}'


def test_gan_extractors_render_dspy_messages_without_a_model_call() -> None:
    hybrid = hybrid_structured_events.DspyStructuredExtractor()
    only = gan_llm_only.DspyCanonicalLlmExtractor()
    prompt = '{"note_text":"two seizures per month"}'
    hybrid_messages = hybrid.render_messages(prompt_input_json=prompt)
    only_messages = only.render_messages(prompt_input_json=prompt)
    assert any(prompt in str(message.get("content")) for message in hybrid_messages)
    assert any(prompt in str(message.get("content")) for message in only_messages)


def test_openrouter_batch_completes_from_inlined_results(tmp_path: Path) -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(f"{request.method} {request.url.path}")
        if request.method == "POST" and request.url.path == "/api/beta/batches":
            payload = json.loads(request.content)
            assert list(payload)[0] == "endpoint"
            return httpx.Response(202, json={"id": "batch_or_1", "status": "validating"})
        if request.method == "GET" and request.url.path == "/api/beta/batches/batch_or_1":
            return httpx.Response(
                200,
                json={
                    "id": "batch_or_1",
                    "status": "completed",
                    "results": [
                        {
                            "custom_id": "11",
                            "response": {
                                "status_code": 200,
                                "body": {
                                    "choices": [
                                        {
                                            "message": {
                                                "role": "assistant",
                                                "content": '{"ok": true}',
                                            }
                                        }
                                    ]
                                },
                            },
                            "error": None,
                        }
                    ],
                },
            )
        return httpx.Response(404, json={"error": "missing"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    raws = complete_chat_batch(
        MODELS["gemini37flash"],
        [
            BatchChatItem(
                custom_id="11",
                messages=[{"role": "user", "content": "note"}],
            )
        ],
        work_dir=tmp_path,
        max_tokens=5000,
        client=client,
        sleep=lambda _seconds: None,
        poll_seconds=0,
        api_key="or-test",
    )
    assert raws == {"11": '{"ok": true}'}
    assert (tmp_path / "batch.json").is_file()
    assert calls[0] == "POST /api/beta/batches"


def test_openai_batch_uploads_jsonl_and_reads_output_file(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/v1/files":
            return httpx.Response(200, json={"id": "file_in"})
        if request.method == "POST" and request.url.path == "/v1/batches":
            payload = json.loads(request.content)
            assert payload["endpoint"] == "/v1/chat/completions"
            assert payload["input_file_id"] == "file_in"
            return httpx.Response(200, json={"id": "batch_oa_1", "status": "validating"})
        if request.method == "GET" and request.url.path == "/v1/batches/batch_oa_1":
            return httpx.Response(
                200,
                json={
                    "id": "batch_oa_1",
                    "status": "completed",
                    "output_file_id": "file_out",
                },
            )
        if request.method == "GET" and request.url.path == "/v1/files/file_out/content":
            line = {
                "custom_id": "11",
                "response": {
                    "status_code": 200,
                    "body": {
                        "choices": [
                            {"message": {"content": '{"final_label":"2 per month"}'}}
                        ]
                    },
                },
                "error": None,
            }
            return httpx.Response(200, text=json.dumps(line) + "\n")
        return httpx.Response(404, json={"error": str(request.url)})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    raws = complete_chat_batch(
        MODELS["gpt56luna"],
        [
            BatchChatItem(
                custom_id="11",
                messages=[{"role": "user", "content": "note"}],
            )
        ],
        work_dir=tmp_path,
        max_tokens=1200,
        client=client,
        sleep=lambda _seconds: None,
        poll_seconds=0,
        api_key="oa-test",
    )
    assert raws == {"11": '{"final_label":"2 per month"}'}


def test_openrouter_retries_not_found_then_completes(tmp_path: Path) -> None:
    seen = {"gets": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            return httpx.Response(202, json={"id": "batch_or_2", "status": "validating"})
        if request.method == "GET":
            seen["gets"] += 1
            if seen["gets"] == 1:
                return httpx.Response(404, json={"error": "not ready"})
            return httpx.Response(
                200,
                json={
                    "id": "batch_or_2",
                    "status": "completed",
                    "results": [
                        {
                            "custom_id": "11",
                            "response": {
                                "status_code": 200,
                                "body": {
                                    "choices": [{"message": {"content": '{"ok": true}'}}]
                                },
                            },
                            "error": None,
                        }
                    ],
                },
            )
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    raws = complete_chat_batch(
        MODELS["gemini37flash"],
        [BatchChatItem(custom_id="11", messages=[{"role": "user", "content": "note"}])],
        work_dir=tmp_path,
        max_tokens=5000,
        client=client,
        sleep=lambda _seconds: None,
        poll_seconds=0,
        api_key="or-test",
    )
    assert raws == {"11": '{"ok": true}'}
    assert seen["gets"] == 2


def test_openrouter_resumes_existing_batch_id(tmp_path: Path) -> None:
    (tmp_path / "batch.json").write_text(
        json.dumps(
            {
                "transport": "openrouter_batch",
                "batch_id": "batch_or_3",
                "completed": False,
            }
        ),
        encoding="utf-8",
    )
    posts = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            posts["n"] += 1
            return httpx.Response(500, json={"error": "should not submit"})
        return httpx.Response(
            200,
            json={
                "id": "batch_or_3",
                "status": "completed",
                "results": [
                    {
                        "custom_id": "11",
                        "response": {
                            "status_code": 200,
                            "body": {
                                "choices": [{"message": {"content": '{"resumed": true}'}}]
                            },
                        },
                        "error": None,
                    }
                ],
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    raws = complete_chat_batch(
        MODELS["gemini37flash"],
        [BatchChatItem(custom_id="11", messages=[{"role": "user", "content": "note"}])],
        work_dir=tmp_path,
        max_tokens=5000,
        client=client,
        sleep=lambda _seconds: None,
        poll_seconds=0,
        api_key="or-test",
    )
    assert posts["n"] == 0
    assert raws == {"11": '{"resumed": true}'}


def test_complete_chat_batch_rejects_grok() -> None:
    with pytest.raises(ValueError, match="no provider batch"):
        complete_chat_batch(
            MODELS["grok46"],
            [],
            work_dir=Path("/tmp"),
            max_tokens=1200,
        )
