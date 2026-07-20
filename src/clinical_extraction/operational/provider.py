"""Connectivity check for an OpenAI-compatible chat-completions endpoint."""

from __future__ import annotations

from typing import Any

from clinical_extraction.operational.runtime import RuntimeConfig


def probe_endpoint(runtime: RuntimeConfig) -> dict[str, Any]:
    from openai import OpenAI

    client = OpenAI(
        api_key=runtime.api_key,
        base_url=runtime.base_url,
        timeout=runtime.timeout_seconds,
    )
    response = client.chat.completions.create(
        model=runtime.api_model,
        messages=[
            {
                "role": "user",
                "content": (
                    "Reply with a JSON object whose only field is ok "
                    "and whose value is true."
                ),
            }
        ],
        temperature=0,
        max_tokens=32,
        response_format={"type": "json_object"},
    )
    message = response.choices[0].message
    return {
        "status": "ok",
        "base_url": runtime.base_url,
        "requested_model": runtime.api_model,
        "response_model": getattr(response, "model", None),
        "content": message.content,
        "reasoning_content_present": bool(
            (getattr(message, "model_extra", None) or {}).get("reasoning_content")
        ),
    }
