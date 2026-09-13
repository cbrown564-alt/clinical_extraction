"""Half-price provider batch lanes for Luna (OpenAI) and Gemini (OpenRouter)."""

from __future__ import annotations

import json
import os
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import httpx

OPENAI_BATCH_BASE = "https://api.openai.com/v1"
OPENROUTER_BATCH_BASE = "https://openrouter.ai/api"
OPENAI_BATCH_MODEL = "gpt-5.6-luna"
OPENROUTER_GEMINI_MODEL = "google/gemini-3.7-flash"
BATCH_SLUGS = frozenset({"gpt56luna", "gemini37flash"})
TERMINAL = frozenset({"completed", "failed", "cancelled", "expired"})


class BatchModel(Protocol):
    """Living paper model fields needed to choose a batch lane."""

    @property
    def slug(self) -> str: ...

    @property
    def model(self) -> str: ...

    @property
    def temperature(self) -> float: ...

    @property
    def reasoning_effort(self) -> str | None: ...

    @property
    def credential_env(self) -> tuple[str, ...]: ...


@dataclass(frozen=True)
class BatchChatItem:
    """One chat-completion request inside a provider batch."""

    custom_id: str
    messages: Sequence[Mapping[str, Any]]


def uses_provider_batch(slug: str) -> bool:
    """Return whether a living paper slug should use a provider batch API."""

    return slug in BATCH_SLUGS


def chat_completion_body(
    spec: BatchModel,
    *,
    messages: Sequence[Mapping[str, Any]],
    max_tokens: int,
) -> dict[str, Any]:
    """Build one chat-completion body for the model's native batch API."""

    if spec.slug == "gpt56luna":
        return {
            "model": OPENAI_BATCH_MODEL,
            "messages": list(messages),
            "temperature": spec.temperature,
            "max_completion_tokens": max_tokens,
            "reasoning_effort": spec.reasoning_effort or "low",
        }
    if spec.slug == "gemini37flash":
        return {
            "model": OPENROUTER_GEMINI_MODEL,
            "messages": list(messages),
            "temperature": spec.temperature,
            "max_tokens": max_tokens,
            "reasoning": {"effort": spec.reasoning_effort or "low"},
        }
    raise ValueError(f"{spec.slug} has no provider batch lane")


def openrouter_batch_payload(
    spec: BatchModel,
    items: Sequence[BatchChatItem],
    *,
    max_tokens: int,
) -> dict[str, Any]:
    """OpenRouter requires endpoint and model before the requests array."""

    return {
        "endpoint": "/v1/chat/completions",
        "model": OPENROUTER_GEMINI_MODEL,
        "requests": [
            {
                "custom_id": item.custom_id,
                "body": chat_completion_body(
                    spec, messages=item.messages, max_tokens=max_tokens
                ),
            }
            for item in items
        ],
    }


def openai_batch_jsonl(
    spec: BatchModel,
    items: Sequence[BatchChatItem],
    *,
    max_tokens: int,
) -> str:
    """Serialize OpenAI Batch JSONL for /v1/chat/completions."""

    lines = []
    for item in items:
        lines.append(
            json.dumps(
                {
                    "custom_id": item.custom_id,
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": chat_completion_body(
                        spec, messages=item.messages, max_tokens=max_tokens
                    ),
                },
                sort_keys=True,
            )
        )
    return "\n".join(lines) + "\n"


def extract_assistant_text(body: Mapping[str, Any]) -> str:
    """Read the first assistant content string from a chat completion body."""

    choices = body.get("choices") or []
    if not choices:
        raise RuntimeError("batch chat completion has no choices")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("batch chat completion has empty assistant content")
    return content


def complete_chat_batch(
    spec: BatchModel,
    items: Sequence[BatchChatItem],
    *,
    work_dir: Path,
    max_tokens: int,
    client: httpx.Client | None = None,
    sleep: Callable[[float], None] = time.sleep,
    poll_seconds: int = 30,
    api_key: str | None = None,
    overwrite: bool = False,
) -> dict[str, str]:
    """Submit one batch, poll until terminal, and return custom_id -> raw text."""

    if spec.slug not in BATCH_SLUGS:
        raise ValueError(f"{spec.slug} has no provider batch lane")
    if not items:
        return {}
    work_dir.mkdir(parents=True, exist_ok=True)
    state_path = work_dir / "batch.json"
    if overwrite and state_path.exists():
        state_path.unlink()
    owns_client = client is None
    if client is None:
        client = httpx.Client(timeout=60.0)
    try:
        if spec.slug == "gpt56luna":
            raws = _complete_openai(
                spec,
                items,
                work_dir=work_dir,
                max_tokens=max_tokens,
                client=client,
                sleep=sleep,
                poll_seconds=poll_seconds,
                api_key=api_key,
                state_path=state_path,
            )
            transport = "openai_batch"
        else:
            raws = _complete_openrouter(
                spec,
                items,
                max_tokens=max_tokens,
                client=client,
                sleep=sleep,
                poll_seconds=poll_seconds,
                api_key=api_key,
                state_path=state_path,
            )
            transport = "openrouter_batch"
        missing = [item.custom_id for item in items if item.custom_id not in raws]
        if missing:
            raise RuntimeError(f"batch results missing custom_ids: {missing[:8]}")
    finally:
        if owns_client:
            client.close()
    prior = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    state_path.write_text(
        json.dumps(
            {
                "transport": transport,
                "model": spec.model,
                "batch_id": prior.get("batch_id"),
                "custom_ids": [item.custom_id for item in items],
                "completed": True,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return raws


def _headers(api_key: str, *, json_content: bool = True) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {api_key}"}
    if json_content:
        headers["Content-Type"] = "application/json"
    return headers


def _existing_batch_id(state_path: Path, transport: str) -> str | None:
    if not state_path.exists():
        return None
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    if payload.get("transport") != transport:
        return None
    batch_id = payload.get("batch_id")
    if not batch_id:
        return None
    return str(batch_id)


def _poll_json(
    client: httpx.Client,
    url: str,
    *,
    headers: Mapping[str, str],
    sleep: Callable[[float], None],
    poll_seconds: int,
    not_found_retries: int = 10,
) -> dict[str, Any]:
    unseen = 0
    while True:
        response = client.get(url, headers=headers)
        if response.status_code == 404 and unseen < not_found_retries:
            unseen += 1
            sleep(poll_seconds)
            continue
        response.raise_for_status()
        payload = response.json()
        status = str(payload.get("status") or "")
        if status in TERMINAL:
            return payload
        unseen = 0
        sleep(poll_seconds)


def _require_key(spec: BatchModel, api_key: str | None) -> str:
    if api_key:
        return api_key
    for name in spec.credential_env:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    names = " or ".join(spec.credential_env)
    raise RuntimeError(f"{names} is missing; stopping before any batch submit")


def _complete_openrouter(
    spec: BatchModel,
    items: Sequence[BatchChatItem],
    *,
    max_tokens: int,
    client: httpx.Client,
    sleep: Callable[[float], None],
    poll_seconds: int,
    api_key: str | None,
    state_path: Path,
) -> dict[str, str]:
    key = _require_key(spec, api_key)
    batch_id = _existing_batch_id(state_path, "openrouter_batch")
    if batch_id is None:
        created = client.post(
            f"{OPENROUTER_BATCH_BASE}/beta/batches",
            headers=_headers(key),
            json=openrouter_batch_payload(spec, items, max_tokens=max_tokens),
        )
        created.raise_for_status()
        batch_id = str(created.json()["id"])
        _write_state(state_path, "openrouter_batch", batch_id)
        print(f"openrouter batch submitted: {batch_id}", flush=True)
    else:
        print(f"openrouter batch resumed: {batch_id}", flush=True)
    payload = _poll_json(
        client,
        f"{OPENROUTER_BATCH_BASE}/beta/batches/{batch_id}",
        headers=_headers(key, json_content=False),
        sleep=sleep,
        poll_seconds=poll_seconds,
    )
    status = str(payload.get("status") or "")
    if status != "completed":
        raise RuntimeError(f"OpenRouter batch {batch_id} ended as {status}")
    return _raws_from_openrouter_results(payload.get("results") or [])


def _complete_openai(
    spec: BatchModel,
    items: Sequence[BatchChatItem],
    *,
    work_dir: Path,
    max_tokens: int,
    client: httpx.Client,
    sleep: Callable[[float], None],
    poll_seconds: int,
    api_key: str | None,
    state_path: Path,
) -> dict[str, str]:
    key = _require_key(spec, api_key)
    jsonl = openai_batch_jsonl(spec, items, max_tokens=max_tokens)
    input_path = work_dir / "batch_input.jsonl"
    input_path.write_text(jsonl, encoding="utf-8")
    batch_id = _existing_batch_id(state_path, "openai_batch")
    if batch_id is None:
        uploaded = client.post(
            f"{OPENAI_BATCH_BASE}/files",
            headers={"Authorization": f"Bearer {key}"},
            files={"file": ("batch_input.jsonl", jsonl, "application/jsonl")},
            data={"purpose": "batch"},
        )
        uploaded.raise_for_status()
        created = client.post(
            f"{OPENAI_BATCH_BASE}/batches",
            headers=_headers(key),
            json={
                "input_file_id": uploaded.json()["id"],
                "endpoint": "/v1/chat/completions",
                "completion_window": "24h",
            },
        )
        created.raise_for_status()
        batch_id = str(created.json()["id"])
        _write_state(state_path, "openai_batch", batch_id)
        print(f"openai batch submitted: {batch_id}", flush=True)
    else:
        print(f"openai batch resumed: {batch_id}", flush=True)
    payload = _poll_json(
        client,
        f"{OPENAI_BATCH_BASE}/batches/{batch_id}",
        headers=_headers(key, json_content=False),
        sleep=sleep,
        poll_seconds=poll_seconds,
    )
    status = str(payload.get("status") or "")
    if status != "completed":
        raise RuntimeError(f"OpenAI batch {batch_id} ended as {status}")
    output_id = payload.get("output_file_id")
    if not output_id:
        raise RuntimeError(f"OpenAI batch {batch_id} completed without output")
    content = client.get(
        f"{OPENAI_BATCH_BASE}/files/{output_id}/content",
        headers={"Authorization": f"Bearer {key}"},
    )
    content.raise_for_status()
    return _raws_from_openai_jsonl(content.text)


def _write_state(path: Path, transport: str, batch_id: str) -> None:
    path.write_text(
        json.dumps(
            {"transport": transport, "batch_id": batch_id, "completed": False},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _raws_from_openrouter_results(results: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    raws: dict[str, str] = {}
    for item in results:
        custom_id = str(item["custom_id"])
        if item.get("error"):
            raise RuntimeError(f"OpenRouter batch item {custom_id} failed: {item['error']}")
        response = item.get("response") or {}
        if int(response.get("status_code") or 0) != 200:
            raise RuntimeError(f"OpenRouter batch item {custom_id} status {response}")
        raws[custom_id] = extract_assistant_text(response.get("body") or {})
    return raws


def _raws_from_openai_jsonl(text: str) -> dict[str, str]:
    raws: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        custom_id = str(item["custom_id"])
        if item.get("error"):
            raise RuntimeError(f"OpenAI batch item {custom_id} failed: {item['error']}")
        response = item.get("response") or {}
        if int(response.get("status_code") or 0) != 200:
            raise RuntimeError(f"OpenAI batch item {custom_id} status {response}")
        raws[custom_id] = extract_assistant_text(response.get("body") or {})
    return raws
