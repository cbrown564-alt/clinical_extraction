"""Run the forced-choice verifier variant over the clean Gan 2026 validation V6 surface."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    selective_verifier_experiment,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DATE = "2026-06-06"
MODEL = "openai/gpt-4.1-mini"
POLICY_ID = "gan2026_clinical_assessment_forced_choice_verifier_v0"

DEFAULT_INPUT_JSONL_PATH = Path(
    "experiments/gan2026_validation750_first_verifier_experiment_input_clean29_context_repair_v6_2026-06-06.jsonl"
)
DEFAULT_ACTION_ONLY_JSONL_PATH = Path(
    "experiments/gan2026_validation750_first_verifier_live_clean29_context_repair_v6_2026-06-06.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_validation750_forced_choice_verifier_live_clean29_context_repair_v6_2026-06-06.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_validation750_forced_choice_verifier_live_clean29_context_repair_v6_2026-06-06.json"
)
DEFAULT_REPORT_PATH = Path(
    "docs/research/gan2026_validation750_forced_choice_verifier_live_clean29_context_repair_v6_2026-06-06.md"
)

def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

SYSTEM_PROMPT = (
    "You are a clinical seizure-frequency verifier. Review the routed case and select exactly "
    "one choice from the allowed_choices list. The allowed_choices consist of the candidate_ids "
    "from candidate_evidence_packets, plus 'none', 'unknown', 'human_review', and 'abstain'. "
    "Choose the candidate_id that best represents the patient's current, primary seizure frequency "
    "burden. If no candidate_id is correct, choose 'none'. If it is completely unknown, choose "
    "'unknown'. If it is too ambiguous, choose 'human_review'. If you cannot decide, choose 'abstain'. "
    "Return only JSON."
)


class ForcedChoiceVerifierOutput(BaseModel):
    selected_choice: str
    rationale: str = ""
    cited_source_ids: list[str] = Field(default_factory=list)


def _extract_json_object(text: str) -> str:
    import re
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, flags=re.DOTALL)
    if match:
        return match.group(1)
    first = stripped.find("{")
    last = stripped.rfind("}")
    if first >= 0 and last > first:
        return stripped[first : last + 1]
    raise ValueError("no JSON object found")


def parse_output(raw_output: str, allowed_choices: set[str]) -> tuple[ForcedChoiceVerifierOutput | None, list[str]]:
    try:
        payload = json.loads(_extract_json_object(raw_output))
        parsed = ForcedChoiceVerifierOutput.model_validate(payload)
    except (json.JSONDecodeError, ValidationError, ValueError) as exc:
        return None, [f"{type(exc).__name__}: {exc}"]
    
    errors = []
    if parsed.selected_choice not in allowed_choices:
        errors.append(f"unsupported_choice:{parsed.selected_choice}")
    return (None, errors) if errors else (parsed, [])


def run_experiment(
    input_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    max_tokens: int,
    progress_every: int = 10,
) -> list[dict[str, Any]]:
    rows = []
    sorted_rows = sorted(input_rows, key=lambda row: int(row["source_row_index"]))
    for index, row in enumerate(sorted_rows, 1):
        rows.append(_run_row(row, model=model, max_tokens=max_tokens))
        if progress_every and index % progress_every == 0:
            print(f"processed={index}/{len(input_rows)}")
    return rows


def _run_row(
    row: Mapping[str, Any],
    *,
    model: str,
    max_tokens: int,
) -> dict[str, Any]:
    verification_case = row["verifier_model_input"]["verification_case"]
    candidate_packets = verification_case["candidate_evidence_packets"]
    candidate_ids = [str(packet["candidate_id"]) for packet in candidate_packets]
    allowed_choices = set(candidate_ids) | {"none", "unknown", "human_review", "abstain"}

    model_input = {
        "verification_case": verification_case,
        "allowed_choices": sorted(allowed_choices),
        "output_schema": {
            "selected_choice": "One value copied from allowed_choices.",
            "rationale": "Brief evidence-grounded rationale.",
            "cited_source_ids": ["Source ids or spans cited from the provided row-local evidence."],
        }
    }

    call_errors: list[str] = []
    usage: dict[str, Any] = {}
    latency_seconds: float | None = None
    raw_output = ""
    call_status = "ok"

    try:
        raw_output, usage, latency_seconds = selective_verifier_experiment._call_openai_responses(
            SYSTEM_PROMPT,
            model_input,
            model=model,
            max_tokens=max_tokens,
        )
    except Exception as exc:
        call_status = "error"
        call_errors.append(f"{type(exc).__name__}: {exc}")

    parsed, parse_errors = (
        parse_output(raw_output, allowed_choices)
        if raw_output
        else (None, [])
    )
    if parsed is None and not call_errors and not parse_errors:
        parse_errors = ["empty_output"]

    # Map selected_choice to an equivalent action
    action = "abstain"
    if parsed is not None:
        choice = parsed.selected_choice
        primary_ids = set(verification_case["clinical_assessment"]["primary_candidate_ids"])
        if choice in primary_ids:
            action = "affirm"
        elif choice in allowed_choices - {"none", "unknown", "human_review", "abstain"}:
            action = "reject"  # selected a different candidate ID
        elif choice == "none":
            action = "reject"
        elif choice == "unknown":
            action = "abstain"
        elif choice == "human_review":
            action = "human_review"
        elif choice == "abstain":
            action = "abstain"

    return {
        "artifact_kind": "gan2026_validation750_forced_choice_verifier_live_clean29_row",
        "source_row_index": int(row["source_row_index"]),
        "split": row.get("split", "validation"),
        "split_manifest": row.get("split_manifest", "gan2026_split_v1"),
        "route_bucket": row["route_bucket"],
        "report_section": row["report_section"],
        "provenance_sidecar_present": bool(row.get("provenance_sidecar_present")),
        "appendix_policy": dict(row.get("appendix_policy") or {}),
        "model": model,
        "prompt_version": POLICY_ID,
        "call_status": call_status,
        "call_errors": call_errors,
        "latency_seconds": latency_seconds,
        "usage": usage,
        "raw_model_output": raw_output,
        "parse_errors": parse_errors,
        "parsed_output": parsed.model_dump(mode="json") if parsed else None,
        "verifier_decision": {
            "action": action,
            "selected_choice": parsed.selected_choice if parsed else "parse_error",
            "rationale": parsed.rationale if parsed else "",
            "cited_source_ids": parsed.cited_source_ids if parsed else [],
        },
        "claim_boundary": "validation_development_forced_choice_verifier_live_clean29_v6",
    }


def compare_and_summarize(
    forced_rows: Sequence[Mapping[str, Any]],
    action_only_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    action_by_row = {r["source_row_index"]: r for r in action_only_rows}
    
    comparisons = []
    agree_count = 0
    disagree_count = 0

    for f_row in forced_rows:
        source_row_index = f_row["source_row_index"]
        a_row = action_by_row.get(source_row_index)
        if a_row is None:
            continue
        
        f_action = f_row["verifier_decision"]["action"]
        a_action = a_row["verifier_decision"]["action"]
        
        agree = f_action == a_action
        if agree:
            agree_count += 1
        else:
            disagree_count += 1
            
        comparisons.append({
            "source_row_index": source_row_index,
            "route_bucket": f_row["route_bucket"],
            "report_section": f_row["report_section"],
            "action_only_action": a_action,
            "forced_choice_choice": f_row["verifier_decision"]["selected_choice"],
            "forced_choice_equivalent_action": f_action,
            "agree": agree,
            "rationale": f_row["verifier_decision"]["rationale"]
        })

    action_counts = Counter(r["verifier_decision"]["action"] for r in forced_rows)
    choice_counts = Counter(r["verifier_decision"]["selected_choice"] for r in forced_rows)

    return {
        "artifact_kind": "gan2026_validation750_forced_choice_verifier_live_clean29_summary",
        "date": DATE,
        "model": MODEL,
        "prompt_version": POLICY_ID,
        "metrics": {
            "total_rows": len(forced_rows),
            "agreement_rows": agree_count,
            "disagreement_rows": disagree_count,
            "agreement_rate": agree_count / len(forced_rows) if forced_rows else 0.0,
            "affirm_rows": action_counts["affirm"],
            "reject_rows": action_counts["reject"],
            "abstain_rows": action_counts["abstain"],
            "human_review_rows": action_counts["human_review"],
        },
        "action_counts": dict(sorted(action_counts.items())),
        "choice_counts": dict(sorted(choice_counts.items())),
        "comparisons": comparisons,
    }


def write_report(
    summary: Mapping[str, Any],
    report_path: Path,
) -> None:
    metrics = summary["metrics"]
    lines = [
        "# Gan 2026 Validation750 Forced-Choice Verifier Live Run Clean29 V6",
        "",
        "Validation-development forced-choice verifier run over the clean 56-row V6 surface.",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total Rows | {metrics['total_rows']} |",
        f"| Agreement Rows | {metrics['agreement_rows']} |",
        f"| Disagreement Rows | {metrics['disagreement_rows']} |",
        f"| Agreement Rate | {metrics['agreement_rate']:.4f} |",
        f"| Affirm Rows | {metrics['affirm_rows']} |",
        f"| Reject Rows | {metrics['reject_rows']} |",
        f"| Abstain Rows | {metrics['abstain_rows']} |",
        f"| Human Review Rows | {metrics['human_review_rows']} |",
        "",
        "## Action Counts (Forced-Choice Equivalent)",
        "",
        "| Action | Count |",
        "| --- | ---: |",
    ]
    for action, count in summary["action_counts"].items():
        lines.append(f"| `{action}` | {count} |")
    
    lines.extend([
        "",
        "## Choice Counts",
        "",
        "| Choice | Count |",
        "| --- | ---: |",
    ])
    for choice, count in summary["choice_counts"].items():
        lines.append(f"| `{choice}` | {count} |")

    lines.extend([
        "",
        "## Comparison Table",
        "",
        "| Row | Route Bucket | Action-Only Action | Forced Choice | Equivalent Action | Agree? | Rationale |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ])
    for comp in summary["comparisons"]:
        if comp["report_section"] == "main_ambiguity_score_table":
            lines.append(
                f"| {comp['source_row_index']} | `{comp['route_bucket']}` | "
                f"`{comp['action_only_action']}` | `{comp['forced_choice_choice']}` | "
                f"`{comp['forced_choice_equivalent_action']}` | "
                f"{'yes' if comp['agree'] else 'no'} | {comp['rationale']} |"
            )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl-path", type=Path, default=DEFAULT_INPUT_JSONL_PATH)
    parser.add_argument("--action-only-jsonl-path", type=Path, default=DEFAULT_ACTION_ONLY_JSONL_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--max-tokens", type=int, default=800)
    args = parser.parse_args(argv)

    input_rows = load_jsonl_rows(args.input_jsonl_path)
    action_only_rows = load_jsonl_rows(args.action_only_jsonl_path)

    forced_rows = run_experiment(
        input_rows,
        model=args.model,
        max_tokens=args.max_tokens,
    )
    summary = compare_and_summarize(forced_rows, action_only_rows)

    write_jsonl_rows(forced_rows, args.jsonl_path)
    write_summary_json(summary, args.json_path)
    write_report(summary, args.report_path)

    print(json.dumps(summary["metrics"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
