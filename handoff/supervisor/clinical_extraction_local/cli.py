"""Command-line interface for the readable supervisor handoff."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from .config import EndpointConfig
from .errors import HandoffError, safe_error
from .input import InputNote, read_notes
from .versions import version_record

SYNTHETIC_CHECK_NOTE = InputNote(
    note_id="synthetic-endpoint-check",
    text="Synthetic note: the patient currently has two seizures per month.",
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("show-config")
    validate = commands.add_parser("validate-input")
    validate.add_argument("--input", type=Path, required=True)
    commands.add_parser("check")
    for command in ("seizure-frequency", "clinical-findings", "all"):
        child = commands.add_parser(command)
        child.add_argument("--input", type=Path, required=True)
        child.add_argument("--output", type=Path, required=True)
        child.add_argument("--trace-output", type=Path)
        child.add_argument("--resume", action="store_true")
        child.add_argument("--retry-failed", action="store_true")
        child.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "validate-input":
            notes = read_notes(args.input)
            print(json.dumps({"status": "ok", "notes": len(notes)}))
            return 0
        config = EndpointConfig.from_env()
        if args.command == "show-config":
            public = {**config.public_dict(), **version_record()}
            print(json.dumps(public, indent=2, sort_keys=True))
            return 0
        from . import _disable_dspy_cache, _prepare_internal_import

        _prepare_internal_import()
        from .client import VLLMClient
        from .extractor import ClinicalExtractor

        _disable_dspy_cache()
        client = VLLMClient(config)
        extractor = ClinicalExtractor(client, config.settings)
        if args.command == "check":
            output = extractor.run_workflow(
                "seizure_frequency",
                note_id=SYNTHETIC_CHECK_NOTE.note_id,
                text=SYNTHETIC_CHECK_NOTE.text,
            )
            response = output.model_response
            print(
                json.dumps(
                    {
                        "status": "ok",
                        "requested_model": response.requested_model,
                        "response_model": response.response_model,
                        "json_mode": response.structured_output_mode,
                        "schema_satisfied": True,
                        "thinking_configured": config.settings.thinking,
                        "reasoning_content_present": response.reasoning_content_present,
                        "finish_reason": response.finish_reason,
                        "truncated": response.finish_reason == "length",
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        notes = read_notes(args.input)
        workflows = {
            "seizure-frequency": ("seizure_frequency",),
            "clinical-findings": ("clinical_findings",),
            "all": ("seizure_frequency", "clinical_findings"),
        }[args.command]
        _print_preflight(notes, workflows, config)
        if args.trace_output:
            print("WARNING: the trace file contains private note and model content.")
        from .batch import run_batch

        summary = run_batch(
            extractor=extractor,
            config=config,
            notes=notes,
            workflows=workflows,
            output=args.output,
            trace_output=args.trace_output,
            resume=args.resume,
            retry_failed=args.retry_failed,
            overwrite=args.overwrite,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 1 if summary["failed"] else 0
    except (HandoffError, FileExistsError) as exc:
        parser.error(json.dumps(safe_error(exc)))
    return 2


def _print_preflight(
    notes: list[InputNote], workflows: tuple[str, ...], config: EndpointConfig
) -> None:
    labels = ", ".join(name.replace("_", "-") for name in workflows)
    print(f"Notes: {len(notes)}")
    print(f"Workflows: {labels}")
    print(f"Expected normal model calls: {len(notes) * len(workflows)}")
    print(f"Endpoint: {config.public_dict()['endpoint']}")
    print(f"Model: {config.model}")
    print(f"Thinking: {'enabled' if config.settings.thinking else 'disabled'}")
    print("Cache: disabled")
