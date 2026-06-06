"""Run the first action-only verifier over the clean Gan 2026 validation V6 surface."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    selective_verifier_experiment,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    clinical_assessment_first_verifier,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DATE = "2026-06-06"
MODEL = "openai/gpt-4.1-mini"
PROMPT_VERSION = clinical_assessment_first_verifier.POLICY_ID
DEFAULT_INPUT_JSONL_PATH = Path(
    "experiments/gan2026_validation750_first_verifier_experiment_input_clean29_context_repair_v6_2026-06-06.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_validation750_first_verifier_live_clean29_context_repair_v6_2026-06-06.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_validation750_first_verifier_live_clean29_context_repair_v6_2026-06-06.json"
)
DEFAULT_REPORT_PATH = Path(
    "docs/research/gan2026_validation750_first_verifier_live_clean29_context_repair_v6_2026-06-06.md"
)


def run_experiment(
    input_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    max_tokens: int,
    progress_every: int = 10,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = []
    sorted_rows = sorted(input_rows, key=lambda row: int(row["source_row_index"]))
    for index, row in enumerate(sorted_rows, 1):
        rows.append(_run_row(row, model=model, max_tokens=max_tokens))
        if progress_every and index % progress_every == 0:
            summary = clinical_assessment_first_verifier.summarize_rows(rows)
            print(
                f"processed={index}/{len(input_rows)} "
                f"actions={summary['action_counts']}"
            )
    return rows, summarize_results(rows, model=model, source_artifact=DEFAULT_INPUT_JSONL_PATH)


def summarize_results(
    rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    source_artifact: Path,
) -> dict[str, Any]:
    summary = clinical_assessment_first_verifier.summarize_rows(rows)
    action_counts = Counter(str(row["verifier_decision"]["action"]) for row in rows)
    main_rows = [row for row in rows if row["appendix_policy"]["main_score_table"]]
    appendix_rows = [row for row in rows if row["appendix_policy"]["appendix_only"]]
    changed_main_rows = [row for row in main_rows if row["verifier_vs_baseline"]["action_changed"]]
    return {
        "artifact_kind": "gan2026_validation750_first_verifier_live_clean29_summary",
        "date": DATE,
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "policy_name": clinical_assessment_first_verifier.POLICY_ID,
        "source_artifact": str(source_artifact),
        "claim_boundary": (
            "Validation-development first action-only verifier run over the clean 56-row "
            "V6 surface. This is not a scorer-label replacement protocol, does not "
            "authorize locked-test inspection, and keeps provenance-only rows out of the "
            "main table."
        ),
        "row_count": len(rows),
        "metrics": {
            "call_ok_rows": sum(row["call_status"] == "ok" for row in rows),
            "parse_ok_rows": sum(not row["parse_errors"] for row in rows),
            "parse_error_rows": sum(bool(row["parse_errors"]) for row in rows),
            "contract_ok_rows": summary["contract_ok_rows"],
            "contract_error_rows": summary["contract_error_rows"],
            "changed_action_rows": summary["changed_action_rows"],
            "main_score_table_rows": len(main_rows),
            "main_score_table_changed_action_rows": len(changed_main_rows),
            "appendix_rows": len(appendix_rows),
            "affirm_rows": action_counts["affirm"],
            "reject_rows": action_counts["reject"],
            "abstain_rows": action_counts["abstain"],
            "human_review_rows": action_counts["human_review"],
            "parse_error_action_rows": action_counts["parse_error"],
        },
        "action_counts": summary["action_counts"],
        "report_section_counts": summary["report_section_counts"],
        "appendix_action_counts": _section_action_counts(appendix_rows),
        "main_action_counts": _section_action_counts(main_rows),
        "usage": _usage_summary(rows),
        "decision": summary["decision"],
        "interpretation": _interpretation(summary, len(main_rows)),
    }


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Validation750 First Verifier Live Run Clean29 V6",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(metadata["interpretation"]),
        "",
        "## Artifacts",
        "",
        f"- Row JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Source input: `{metadata['source_artifact']}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(["", "## Main Table Actions", "", "| Action | Rows |", "| --- | ---: |"])
    for key, value in metadata["main_action_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(["", "## Appendix Actions", "", "| Action | Rows |", "| --- | ---: |"])
    for key, value in metadata["appendix_action_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Main Ambiguity Table",
            "",
            "| Row | Baseline | Verifier | Sidecar | Route bucket | Rationale |",
            "| ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        if not row["appendix_policy"]["main_score_table"]:
            continue
        decision = row["verifier_decision"]
        lines.append(
            f"| {row['source_row_index']} | `{decision['baseline_action']}` | "
            f"`{decision['action']}` | "
            f"{'present' if row['provenance_sidecar_present'] else 'absent'} | "
            f"`{row['route_bucket']}` | {(_single_line(decision['rationale']) or '').strip()} |"
        )
    lines.extend(
        [
            "",
            "## Appendix By Section",
            "",
            "| Section | Rows |",
            "| --- | ---: |",
        ]
    )
    for key, value in metadata["report_section_counts"].items():
        if key == "main_ambiguity_score_table":
            continue
        lines.append(f"| `{key}` | {value} |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _run_row(
    row: Mapping[str, Any],
    *,
    model: str,
    max_tokens: int,
) -> dict[str, Any]:
    model_input = dict(row["verifier_model_input"])
    system_prompt = str(model_input.pop("system_prompt"))
    call_errors: list[str] = []
    usage: dict[str, Any] = {}
    latency_seconds: float | None = None
    raw_output = ""
    call_status = "ok"
    try:
        raw_output, usage, latency_seconds = selective_verifier_experiment._call_openai_responses(
            system_prompt,
            model_input,
            model=model,
            max_tokens=max_tokens,
        )
    except Exception as exc:  # pragma: no cover - live failure path
        call_status = "error"
        call_errors.append(f"{type(exc).__name__}: {exc}")
    parsed, parse_errors = (
        clinical_assessment_first_verifier.parse_output(raw_output)
        if raw_output
        else (None, [])
    )
    if parsed is None and not call_errors and not parse_errors:
        parse_errors = ["empty_output"]
    decision = clinical_assessment_first_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=parse_errors,
    )
    return {
        "artifact_kind": "gan2026_validation750_first_verifier_live_clean29_row",
        "source_row_index": int(row["source_row_index"]),
        "split": row.get("split", "validation"),
        "split_manifest": row.get("split_manifest", "gan2026_split_v1"),
        "route_bucket": row["route_bucket"],
        "report_section": row["report_section"],
        "provenance_sidecar_present": bool(row.get("provenance_sidecar_present")),
        "provenance_sidecar_families": list(row.get("provenance_sidecar_families") or []),
        "appendix_policy": dict(row.get("appendix_policy") or {}),
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "call_status": call_status,
        "call_errors": call_errors,
        "latency_seconds": latency_seconds,
        "usage": usage,
        "raw_model_output": raw_output,
        "parse_errors": parse_errors,
        "parsed_output": parsed.model_dump(mode="json") if parsed else None,
        "verifier_decision": decision,
        "verifier_vs_baseline": {
            "action_changed": decision["action"] != decision["baseline_action"],
        },
        "claim_boundary": "validation_development_first_verifier_live_clean29_v6",
    }


def _section_action_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return dict(
        sorted(Counter(str(row["verifier_decision"]["action"]) for row in rows).items())
    )


def _usage_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    input_tokens = sum(int((row.get("usage") or {}).get("input_tokens") or 0) for row in rows)
    output_tokens = sum(int((row.get("usage") or {}).get("output_tokens") or 0) for row in rows)
    total_tokens = sum(int((row.get("usage") or {}).get("total_tokens") or 0) for row in rows)
    latency = sum(float(row.get("latency_seconds") or 0.0) for row in rows)
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "wall_clock_latency_seconds": latency,
    }


def _interpretation(summary: Mapping[str, Any], main_rows: int) -> str:
    if summary["decision"] == "contract_failures_present":
        return (
            "Do not treat this run as valid yet: at least one verifier output "
            "broke the row-local contract."
        )
    if summary["action_counts"].get("affirm", 0) or summary["action_counts"].get("reject", 0):
        return (
            "The first verifier produced non-abstain action decisions on the clean surface. "
            f"The primary table remains the {main_rows}-row ambiguity set."
        )
    return (
        "The first verifier stayed action-conservative on this surface and did "
        "not move beyond abstention/review."
    )


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _single_line(text: str) -> str:
    return " ".join(str(text).split())


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl-path", type=Path, default=DEFAULT_INPUT_JSONL_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--max-tokens", type=int, default=700)
    parser.add_argument("--progress-every", type=int, default=10)
    args = parser.parse_args(argv)

    rows, metadata = run_experiment(
        load_jsonl_rows(args.input_jsonl_path),
        model=args.model,
        max_tokens=args.max_tokens,
        progress_every=args.progress_every,
    )
    metadata = {**metadata, "source_artifact": str(args.input_jsonl_path)}
    write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(
        rows,
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )
    print(json.dumps(metadata["metrics"], indent=2, sort_keys=True))
    print(metadata["interpretation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
