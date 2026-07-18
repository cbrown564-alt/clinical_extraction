"""Verify one local Ollama tag can return usable structured output."""

from __future__ import annotations

import argparse
import json
import urllib.request
from typing import Any

from clinical_extraction.core.local_structured_output import (
    ollama_structured_probe_request,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-base", default="http://localhost:11434")
    args = parser.parse_args()

    strict_payload = ollama_structured_probe_request(args.model)
    strict_response = _post_chat(args.api_base, strict_payload)
    strict_ok, strict_failure = _validate_response(strict_response)
    if strict_ok:
        _print_result(
            model=args.model,
            status="pass",
            structured_output_mode="native_schema_constraint",
            schema_constraint_enforced=True,
        )
        return

    fallback_payload = ollama_structured_probe_request(
        args.model, explicit_json_instruction=True
    )
    fallback_response = _post_chat(args.api_base, fallback_payload)
    fallback_ok, fallback_failure = _validate_response(fallback_response)
    if not fallback_ok:
        raise SystemExit(
            "Ollama structured-output probe failed in native and prompt-enforced "
            f"modes: native={strict_failure}; fallback={fallback_failure}"
        )
    _print_result(
        model=args.model,
        status="pass_with_prompt_fallback",
        structured_output_mode="prompt_plus_shared_parser",
        schema_constraint_enforced=False,
        native_constraint_failure=strict_failure,
    )


def _post_chat(api_base: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{api_base.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=300) as response:  # noqa: S310
        return json.load(response)


def _validate_response(payload: dict[str, Any]) -> tuple[bool, str | None]:
    message = payload.get("message") or {}
    content = str(message.get("content") or "")
    reasoning = str(message.get("thinking") or message.get("reasoning") or "")
    if not content:
        failure = "reasoning_only" if reasoning else "empty_content"
        return False, failure
    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        return False, f"invalid_json:{exc.msg}; content={content!r}"
    if result != {"status": "ok", "values": [1, 2]}:
        return False, f"schema_mismatch:{result!r}"
    return True, None


def _print_result(
    *,
    model: str,
    status: str,
    structured_output_mode: str,
    schema_constraint_enforced: bool,
    native_constraint_failure: str | None = None,
) -> None:
    print(
        json.dumps(
            {
                "model": model,
                "status": status,
                "think": False,
                "native_chat": True,
                "structured_output_mode": structured_output_mode,
                "schema_constraint_enforced": schema_constraint_enforced,
                "native_constraint_failure": native_constraint_failure,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
