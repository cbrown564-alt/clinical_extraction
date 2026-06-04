"""Run the predeclared selective boundary-candidate proposer experiment."""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    selective_boundary_candidate_predeclaration as predecl,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_selective_boundary_candidate_experiment_2026-06-04.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_selective_boundary_candidate_experiment_2026-06-04.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_selective_boundary_candidate_experiment_2026-06-04.md"
)
DEFAULT_PREDECLARATION_JSONL_PATH = predecl.DEFAULT_JSONL_PATH
PROMPT_VERSION = predecl.PROMPT_VERSION


class BoundaryCandidateSignature(dspy.Signature):
    """Extract hard seizure-frequency candidate facts from one note."""

    boundary_candidate_input_json: str = dspy.InputField(
        desc="JSON containing one clinical note, plain instructions, and output schema."
    )
    boundary_candidate_output_json: str = dspy.OutputField(
        desc="One strict JSON object with a candidates list."
    )


class BoundaryCandidateProgram(dspy.Module):
    """DSPy wrapper for the selective boundary-candidate proposer."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(BoundaryCandidateSignature)

    def forward(self, boundary_candidate_input_json: str) -> dspy.Prediction:
        return self.predict(boundary_candidate_input_json=boundary_candidate_input_json)


class RatePayload(BaseModel):
    """Structured rate fields emitted by the proposer."""

    model_config = ConfigDict(extra="allow")

    count_low: float | None = None
    count_high: float | None = None
    count_is_multiple: bool | None = None
    time_count_low: float | None = None
    time_count_high: float | None = None
    time_unit: Literal["day", "week", "month", "year"] | None = None
    rate_text: str | None = None


class ClusterPayload(BaseModel):
    """Structured cluster fields emitted by the proposer."""

    model_config = ConfigDict(extra="allow")

    has_cluster_pattern: bool | None = None
    cluster_cadence_text: str | None = None
    seizures_per_cluster_low: float | None = None
    seizures_per_cluster_high: float | None = None
    cluster_uncertainty: str | None = None


class SeizureFreePayload(BaseModel):
    """Structured seizure-free fields emitted by the proposer."""

    model_config = ConfigDict(extra="allow")

    has_no_event_claim: bool | None = None
    duration_count: float | None = None
    duration_unit: Literal["day", "week", "month", "year"] | None = None
    applies_to_all_seizure_types: bool | None = None
    has_recent_events_or_conditions: bool | None = None
    boundary_note: str | None = None


class BoundaryCandidatePayload(BaseModel):
    """One proposed boundary candidate."""

    model_config = ConfigDict(extra="allow")

    candidate_kind: Literal[
        "frequency_rate",
        "cluster_frequency",
        "seizure_free",
        "unknown_frequency",
        "no_reference",
        "conditional_frequency",
    ]
    evidence_quote: str
    currentness: Literal["current", "recent", "historical", "unclear"]
    assertion_status: Literal["asserted", "negated", "uncertain", "conditional"]
    seizure_type: str | None = None
    rate: RatePayload = Field(default_factory=RatePayload)
    cluster: ClusterPayload = Field(default_factory=ClusterPayload)
    seizure_free: SeizureFreePayload = Field(default_factory=SeizureFreePayload)
    conditionality_note: str | None = None
    competing_state_summary: str | None = None
    ambiguity_flags: list[str] = []
    reason: str


class BoundaryCandidateOutput(BaseModel):
    """Top-level proposer output."""

    model_config = ConfigDict(extra="allow")

    candidates: list[BoundaryCandidatePayload]


def run_experiment(
    predeclared_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    temperature: float,
    max_tokens: int,
    cache: bool,
    api_base: str | None = None,
    provider: str = "dspy",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    program: BoundaryCandidateProgram | None = None
    if provider == "dspy":
        lm = build_dspy_lm(
            model,
            temperature=temperature,
            max_tokens=max_tokens,
            cache=cache,
            api_base=api_base,
        )
        dspy.configure(lm=lm)
        program = BoundaryCandidateProgram()
    rows: list[dict[str, Any]] = []
    for predeclared in predeclared_rows:
        rows.append(_run_row(predeclared, program=program, model=model, provider=provider))
    return rows, summarize_experiment(
        rows, model=model, temperature=temperature, max_tokens=max_tokens
    )


def summarize_experiment(
    rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    candidate_counts = [len(row["retained_candidates"]) for row in rows]
    call_ok_rows = sum(row["call_status"] == "ok" for row in rows)
    parse_ok_rows = sum(row["call_status"] == "ok" and not row["parse_errors"] for row in rows)
    exact_rows = sum(row["row_metrics"]["all_retained_evidence_exact"] for row in rows)
    exact_match_rows = sum(row["row_metrics"]["gold_exact_label_recall"] for row in rows)
    purist_match_rows = sum(row["row_metrics"]["gold_purist_recall"] for row in rows)
    saved_overlap_rows = sum(row["row_metrics"]["saved_rescue_evidence_overlap"] for row in rows)
    rejected = [candidate for row in rows for candidate in row["rejected_candidates"]]
    gate_failures = Counter(
        failure for candidate in rejected for failure in candidate["gate_failures"]
    )
    return {
        "artifact_kind": "gan2026_selective_boundary_candidate_experiment",
        "date": "2026-06-04",
        "split_manifest": "gan2026_split_v1",
        "split": "validation",
        "source_artifact": str(DEFAULT_PREDECLARATION_JSONL_PATH),
        "row_count": len(rows),
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "prompt_version": PROMPT_VERSION,
        "claim_language": (
            "Validation-development controlled component experiment only. Outputs are "
            "candidate proposals, not final labels; no locked-test inspection, "
            "whole-pipeline promotion, or benchmark-comparable claim is authorized."
        ),
        "metrics": {
            "call_ok_rows": call_ok_rows,
            "call_error_rows": len(rows) - call_ok_rows,
            "parse_ok_rows": parse_ok_rows,
            "parse_error_rows": sum(bool(row["parse_errors"]) for row in rows),
            "rows_with_retained_candidate": sum(bool(row["retained_candidates"]) for row in rows),
            "rows_with_gold_exact_label_recall": exact_match_rows,
            "rows_with_gold_purist_recall": purist_match_rows,
            "rows_with_saved_rescue_evidence_overlap": saved_overlap_rows,
            "rows_all_retained_evidence_exact": exact_rows,
            "total_retained_candidates": sum(candidate_counts),
            "median_retained_candidates": _median(candidate_counts),
            "p90_retained_candidates": _percentile(candidate_counts, 90),
            "total_rejected_candidates": len(rejected),
        },
        "gate_failure_counts": dict(sorted(gate_failures.items())),
        "hard_family_summary": _hard_family_summary(rows),
        "candidate_kind_counts": dict(
            sorted(
                Counter(
                    c["candidate_kind"] for row in rows for c in row["retained_candidates"]
                ).items()
            )
        ),
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
        "# Gan 2026 Selective Boundary-Candidate Experiment",
        "",
        "This controlled validation-development run uses the predeclared 22-row "
        "boundary-candidate rescue slice. The model proposes candidate facts only; "
        "candidate outputs are gated and deterministically normalized for component "
        "accounting, not used as final labels.",
        "",
        "## Outcome",
        "",
        (
            f"The live proposer produced parseable outputs for {metrics['parse_ok_rows']}/"
            f"{metadata['row_count']} rows and retained at least one gated candidate for "
            f"{metrics['rows_with_retained_candidate']}/{metadata['row_count']} rows. "
            f"Exact-label candidate recall was {metrics['rows_with_gold_exact_label_recall']}/"
            f"{metadata['row_count']}; Purist-category candidate recall was "
            f"{metrics['rows_with_gold_purist_recall']}/{metadata['row_count']}."
        ),
        "",
        "## Claim Boundary",
        "",
        str(metadata["claim_language"]),
        "",
        "## Artifacts",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Predeclaration: `{metadata['source_artifact']}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(["", "## Gate Failures", "", "| Failure | Count |", "| --- | ---: |"])
    for key, value in metadata["gate_failure_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Row Outcomes",
            "",
            "| Row | Gold | Exact recall | Purist recall | Retained | Rejected | Notes |",
            "| ---: | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in rows:
        metrics_row = row["row_metrics"]
        notes = "; ".join(row["parse_errors"] or row["call_errors"] or [])
        lines.append(
            f"| {row['source_row_index']} | `{row['gold_label']}` | "
            f"{_yes(metrics_row['gold_exact_label_recall'])} | "
            f"{_yes(metrics_row['gold_purist_recall'])} | "
            f"{len(row['retained_candidates'])} | {len(row['rejected_candidates'])} | "
            f"{notes} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Promote only as a candidate-proposal component if exact evidence remains high "
            "and retained candidates cover the missed gold states without excess burden.",
            "- Do not treat this as final-label performance. Any downstream label effect must "
            "be measured by a separate selected-state replay over the gated union.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _run_row(
    predeclared: Mapping[str, Any],
    *,
    program: BoundaryCandidateProgram | None,
    model: str,
    provider: str,
) -> dict[str, Any]:
    model_input = predeclared["model_input"]
    raw_output = ""
    call_errors: list[str] = []
    try:
        if provider == "openai-responses":
            raw_output = _call_openai_responses(
                model_input,
                model=model,
                max_tokens=3000,
            )
        else:
            if program is None:
                raise ValueError(f"unsupported provider: {provider}")
            prediction = program(
                boundary_candidate_input_json=json.dumps(
                    model_input, ensure_ascii=False, sort_keys=True
                )
            )
            raw_output = str(prediction.boundary_candidate_output_json)
        call_status = "ok"
    except Exception as exc:  # pragma: no cover - exercised only by live call failure
        call_status = "error"
        call_errors.append(f"{type(exc).__name__}: {exc}")

    parsed, parse_errors = _parse_output(raw_output) if raw_output else (None, [])
    retained: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    if parsed is not None:
        for index, candidate in enumerate(parsed.candidates, start=1):
            materialized = _materialize_candidate(
                candidate, index=index, note_text=model_input["note_text"]
            )
            if materialized["gate_failures"]:
                rejected.append(materialized)
            else:
                retained.append(materialized)
    if len(retained) > int(model_input["max_candidates"]):
        overflow = retained[int(model_input["max_candidates"]) :]
        for candidate in overflow:
            candidate["gate_failures"].append("candidate_burden_overflow")
        rejected.extend(overflow)
        retained = retained[: int(model_input["max_candidates"])]

    gold_label = predeclared["development_accounting"]["gold_label"]
    saved_evidence = [
        str(candidate.get("evidence") or "")
        for candidate in predeclared.get("saved_rescue_proposals", [])
    ]
    return {
        "artifact_kind": "gan2026_selective_boundary_candidate_experiment_row",
        "source_row_index": int(predeclared["source_row_index"]),
        "split": predeclared.get("split", "validation"),
        "split_manifest": predeclared.get("split_manifest", "gan2026_split_v1"),
        "hard_families": list(predeclared.get("hard_families") or []),
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "call_status": call_status,
        "call_errors": call_errors,
        "raw_model_output": raw_output,
        "parse_errors": parse_errors,
        "retained_candidates": retained,
        "rejected_candidates": rejected,
        "gold_label": gold_label,
        "deterministic_top_label": predeclared["development_accounting"]["deterministic_top_label"],
        "saved_rescue_evidence": saved_evidence,
        "row_metrics": _row_metrics(retained, gold_label=gold_label, saved_evidence=saved_evidence),
        "claim_boundary": "validation_development_candidate_proposals_not_final_labels",
    }


def _parse_output(raw_output: str) -> tuple[BoundaryCandidateOutput | None, list[str]]:
    try:
        payload = _repair_singleton_enum_lists(json.loads(_extract_json_object(raw_output)))
        return BoundaryCandidateOutput.model_validate(payload), []
    except (json.JSONDecodeError, ValidationError, ValueError) as exc:
        return None, [f"{type(exc).__name__}: {exc}"]


def _extract_json_object(text: str) -> str:
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


def _call_openai_responses(
    model_input: Mapping[str, Any],
    *,
    model: str,
    max_tokens: int,
) -> str:
    api_key = os.environ["OPENAI_API_KEY"].strip()
    body = {
        "model": model.removeprefix("openai/"),
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": json.dumps(
                            model_input,
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                    }
                ],
            }
        ],
        "temperature": 0,
        "max_output_tokens": max_tokens,
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            payload = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"OpenAI HTTP {exc.code}") from exc
    texts = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                texts.append(str(text))
    output_text = str(payload.get("output_text") or "\n".join(texts)).strip()
    if not output_text:
        raise RuntimeError("OpenAI response contained no output text")
    return output_text


def _repair_singleton_enum_lists(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    for candidate in payload.get("candidates", []):
        if not isinstance(candidate, dict):
            continue
        for key in ("candidate_kind", "currentness", "assertion_status"):
            value = candidate.get(key)
            if isinstance(value, list) and len(value) == 1:
                candidate[key] = value[0]
        for key in ("rate", "cluster", "seizure_free"):
            if candidate.get(key) is None:
                candidate[key] = {}
    return payload


def _materialize_candidate(
    candidate: BoundaryCandidatePayload,
    *,
    index: int,
    note_text: str,
) -> dict[str, Any]:
    normalized_label, normalization_errors = _candidate_label(candidate)
    evidence = candidate.evidence_quote
    gate_failures = list(normalization_errors)
    if not evidence:
        gate_failures.append("missing_evidence")
    elif evidence not in note_text:
        gate_failures.append("non_exact_evidence")
    return {
        "candidate_id": f"live-boundary-{index:03d}",
        "candidate_kind": candidate.candidate_kind,
        "evidence": evidence,
        "exact_evidence": bool(evidence and evidence in note_text),
        "source_id": "note" if evidence else "",
        "source_id_status": "valid" if evidence else "missing",
        "currentness": candidate.currentness,
        "assertion_status": candidate.assertion_status,
        "semiology": candidate.seizure_type,
        "normalized_label": normalized_label,
        "metadata": candidate.model_dump(mode="json"),
        "provenance": ["live_llm_boundary_proposal"],
        "gate_failures": gate_failures,
    }


def _candidate_label(candidate: BoundaryCandidatePayload) -> tuple[str | None, list[str]]:
    if candidate.candidate_kind == "no_reference":
        return "no seizure frequency reference", []
    if candidate.candidate_kind in {"unknown_frequency", "conditional_frequency"}:
        return "unknown", []
    if candidate.candidate_kind == "seizure_free":
        duration = candidate.seizure_free.duration_count
        unit = candidate.seizure_free.duration_unit
        if duration and unit:
            return _validated_label(f"seizure free for {_format_number(duration)} {unit}")
        return "unknown", ["missing_seizure_free_duration"]
    if candidate.candidate_kind == "cluster_frequency" and candidate.cluster.has_cluster_pattern:
        cluster_label = _cluster_label(candidate)
        if cluster_label:
            return _validated_label(cluster_label)
    rate_label = _rate_label(candidate.rate)
    if rate_label:
        return _validated_label(rate_label)
    return None, ["unrenderable_candidate"]


def _cluster_label(candidate: BoundaryCandidatePayload) -> str | None:
    rate = candidate.rate
    cluster = candidate.cluster
    if not rate.time_unit or not rate.time_count_low:
        return None
    cluster_count = rate.count_low or 1
    period = _period_text(rate.time_count_low, rate.time_unit)
    low = cluster.seizures_per_cluster_low
    high = cluster.seizures_per_cluster_high
    if low and high and low != high:
        burden = f"{_format_number(low)} to {_format_number(high)} per cluster"
    elif low:
        burden = f"{_format_number(low)} per cluster"
    else:
        return None
    return f"{_format_number(cluster_count)} cluster per {period}, {burden}"


def _rate_label(rate: RatePayload) -> str | None:
    if not rate.time_unit:
        return None
    period_count = rate.time_count_low or 1
    period = _period_text(period_count, rate.time_unit)
    if rate.count_is_multiple:
        return f"multiple per {period}"
    if rate.count_low and rate.count_high and rate.count_low != rate.count_high:
        return f"{_format_number(rate.count_low)} to {_format_number(rate.count_high)} per {period}"
    if rate.count_low:
        return f"{_format_number(rate.count_low)} per {period}"
    return None


def _validated_label(label: str) -> tuple[str | None, list[str]]:
    try:
        return label_to_frequency_record(label).normalized_label, []
    except ValueError as exc:
        return label, [f"label_parse_error:{exc}"]


def _row_metrics(
    retained: Sequence[Mapping[str, Any]],
    *,
    gold_label: str,
    saved_evidence: Sequence[str],
) -> dict[str, Any]:
    gold = label_to_frequency_record(gold_label)
    gold_purist = map_purist(gold.monthly_frequency)
    gold_pragmatic = map_pragmatic(gold.monthly_frequency)
    candidate_records = []
    for candidate in retained:
        label = candidate.get("normalized_label")
        if not label:
            continue
        try:
            candidate_records.append(label_to_frequency_record(str(label)))
        except ValueError:
            continue
    return {
        "gold_exact_label_recall": any(
            record.normalized_label == gold.normalized_label for record in candidate_records
        ),
        "gold_purist_recall": any(
            map_purist(record.monthly_frequency) == gold_purist for record in candidate_records
        ),
        "gold_pragmatic_recall": any(
            map_pragmatic(record.monthly_frequency) == gold_pragmatic
            for record in candidate_records
        ),
        "saved_rescue_evidence_overlap": any(
            _evidence_overlap(str(candidate.get("evidence") or ""), saved)
            for candidate in retained
            for saved in saved_evidence
        ),
        "all_retained_evidence_exact": all(
            candidate.get("exact_evidence") for candidate in retained
        )
        if retained
        else False,
    }


def _evidence_overlap(left: str, right: str) -> bool:
    if not left or not right:
        return False
    left_norm = " ".join(left.lower().split())
    right_norm = " ".join(right.lower().split())
    return left_norm in right_norm or right_norm in left_norm


def _hard_family_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, Counter[str]] = {}
    for row in rows:
        for family in row.get("hard_families") or ["unclassified"]:
            counts = summary.setdefault(str(family), Counter())
            counts["rows"] += 1
            if row["row_metrics"]["gold_exact_label_recall"]:
                counts["exact_recall_rows"] += 1
            if row["row_metrics"]["gold_purist_recall"]:
                counts["purist_recall_rows"] += 1
    return {family: dict(counts) for family, counts in sorted(summary.items())}


def _period_text(count: float, unit: str) -> str:
    if count == 1:
        return unit
    return f"{_format_number(count)} {unit}"


def _format_number(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else str(value)


def _median(values: Sequence[int]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[midpoint])
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2


def _percentile(values: Sequence[int], percentile: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round((percentile / 100) * (len(ordered) - 1))))
    return float(ordered[index])


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _yes(value: bool) -> str:
    return "yes" if value else "no"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--predeclaration-jsonl-path", type=Path, default=DEFAULT_PREDECLARATION_JSONL_PATH
    )
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=3000)
    parser.add_argument("--api-base")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument(
        "--provider",
        choices=["dspy", "openai-responses"],
        default="dspy",
    )
    args = parser.parse_args(argv)

    predeclared_rows = load_jsonl_rows(args.predeclaration_jsonl_path)
    rows, metadata = run_experiment(
        predeclared_rows,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        cache=not args.no_cache,
        api_base=args.api_base,
        provider=args.provider,
    )
    metadata = {
        **metadata,
        "source_artifact": str(args.predeclaration_jsonl_path),
    }
    write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(
        rows, metadata, args.report_path, jsonl_path=args.jsonl_path, json_path=args.json_path
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
