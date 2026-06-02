"""Hosted boundary-state graph-builder diagnostic for Gan 2026."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments import (
    synthetic_hard_case_component_stress as hard_cases,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_raw_outputs_by_source_index,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_v1_unknown_recall"
DEFAULT_JSONL_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_smoke_2026-06-02.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_smoke_2026-06-02.md"
)
VALIDATION_MISSING_REPRESENTABILITY_SOURCE_ROW_INDICES: tuple[int, ...] = (
    338,
    743,
    869,
    1317,
    1695,
    1707,
    2080,
    2149,
    2166,
    3356,
    3436,
    3468,
    3493,
    3507,
    3512,
    3528,
    3532,
    3600,
    4690,
    4694,
    4700,
    4709,
    4731,
    4732,
    4771,
    5476,
    5490,
    5491,
    5504,
    5507,
    5534,
)
SYNTHETIC_UNKNOWN_STRESS_SOURCE_ROW_INDICES: tuple[int, ...] = (
    900016,
    900017,
    900019,
    900021,
    900022,
    900028,
    900030,
    900044,
)


class BoundaryStateNodeRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    semantic_kind: Literal["unknown", "unresolved_multiple"]
    evidence: str
    node_normalized_label: str | None = None
    temporality: str = "current"
    assertion_status: str = "asserted"
    certainty: str = "unknown"
    rationale: str


class BoundaryStateBuilderRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodes: list[BoundaryStateNodeRecord] = Field(default_factory=list)
    no_reference_vs_unknown_rationale: str | None = None


class BoundaryStateGraphBuilderSignature(dspy.Signature):
    """Construct source-evidenced unknown/unresolved-multiple graph nodes."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON with one note, graph-builder instructions, and no gold labels."
    )
    boundary_state_graph_builder_json: str = dspy.OutputField(
        desc="Strict JSON object with nodes only; no final Gan label."
    )


class DspyBoundaryStateGraphBuilder(dspy.Module):
    """DSPy wrapper for the hosted boundary-state graph-builder prompt."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(BoundaryStateGraphBuilderSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def select_validation_missing_rows(
    records: Sequence[GanFrequencyRecord],
) -> list[GanFrequencyRecord]:
    """Select the 31 validation hard-slice rows missing gold representability."""

    target = set(VALIDATION_MISSING_REPRESENTABILITY_SOURCE_ROW_INDICES)
    return [record for record in records if record.source_row_index in target]


def select_synthetic_unknown_stress_rows(
    records: Sequence[GanFrequencyRecord],
) -> list[GanFrequencyRecord]:
    """Select the 8 synthetic unknown rows used as stress-only diagnostics."""

    target = set(SYNTHETIC_UNKNOWN_STRESS_SOURCE_ROW_INDICES)
    return [record for record in records if record.source_row_index in target]


def build_prompt_input(record: GanFrequencyRecord, *, surface_role: str) -> str:
    """Build the hosted graph-builder prompt payload without gold labels."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": "hybrid_clinical_frequency_state_graph",
        "component_role": "boundary_state_graph_node_builder",
        "surface_role": surface_role,
        "source_row_index": record.source_row_index,
        "allowed_node_semantic_kinds": ["unknown", "unresolved_multiple"],
        "forbidden_output_keys": [
            "final_label",
            "gold_label",
            "prediction",
            "projection",
            "selected_node_ids",
            "top_level",
        ],
        "instructions": (
            "Construct only candidate clinical frequency state-graph nodes for "
            "unknown or unresolved_multiple boundary states. Do not emit a final "
            "Gan label, do not choose the best answer, and do not adjudicate "
            "projection. Return one JSON object whose root keys are exactly "
            "nodes and no_reference_vs_unknown_rationale; never wrap the object "
            "inside top_level. Every evidence value must be an exact substring "
            "copied from the note. Use unknown when patient seizure occurrence "
            "or seizure frequency is present but not convertible: unclear "
            "frequency, cannot estimate how often, no reliable count, rare but "
            "unmapped, worsening frequency without count, clusters with no "
            "seizure count, or typical frequency not known. Use "
            "unresolved_multiple only when the text states a recurring multiple "
            "or vague count with a single recoverable time unit such as day, "
            "week, month, or year. Separate no-reference from unknown in the "
            "rationale."
        ),
        "unknown_state_examples": [
            "seizures continue but frequency is unclear",
            "cannot estimate how often they happen",
            "seizures occur with missed doses",
            "without a reliable count",
            "rare nocturnal seizures",
            "no count of seizures within the cluster is available",
            "uncertain number of seizures",
            "typical frequency is not known",
        ],
        "output_schema": {
            "type": "object",
            "required_root_keys": [
                "nodes",
                "no_reference_vs_unknown_rationale",
            ],
            "nodes": "list of boundary-state graph nodes at the JSON root",
            "no_reference_vs_unknown_rationale": "short rationale or null at the JSON root",
            "node": {
                "semantic_kind": "unknown or unresolved_multiple",
                "node_normalized_label": (
                    "unknown, multiple per day/week/month/year, or null when not recoverable"
                ),
                "evidence": "exact note substring",
                "temporality": "current, recent, historical, or unclear",
                "assertion_status": "asserted, negated, hypothetical, or unknown",
                "certainty": "low, medium, high, or unknown",
                "rationale": "brief source-near reason for this node",
            },
        },
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_boundary_state_builder_json(
    raw_output: str,
    *,
    note_text: str,
) -> tuple[dict[str, Any] | None, list[str]]:
    """Parse and validate hosted boundary-state output."""

    errors: list[str] = []
    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        return None, [f"json_decode_error:{exc.msg}"]
    if not isinstance(data, dict):
        return None, ["top_level_not_object"]
    if "final_label" in data:
        errors.append("final_label_emitted")
    data = {
        key: value
        for key, value in data.items()
        if key in {"nodes", "no_reference_vs_unknown_rationale"}
    }
    try:
        record = BoundaryStateBuilderRecord.model_validate(data)
    except ValidationError as exc:
        return None, [*errors, f"schema_validation_error:{exc.errors()}"]

    for index, node in enumerate(record.nodes):
        if not evidence_is_substring(note_text, node.evidence):
            errors.append(f"node[{index}].evidence_not_exact")
        if node.semantic_kind == "unknown" and node.node_normalized_label not in {
            None,
            "unknown",
        }:
            errors.append(f"node[{index}].unknown_label_not_unknown")
        if node.semantic_kind == "unresolved_multiple":
            _validate_unresolved_multiple_node_label(node, errors, index)
    return record.model_dump(mode="json"), errors


def run_boundary_state_graph_builder_split(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    reuse_raw_outputs: Mapping[int, str] | None = None,
    reuse_source: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run or replay the hosted boundary-state graph-builder diagnostic."""

    reuse_raw_outputs = reuse_raw_outputs or {}
    metadata = build_run_metadata(
        mode=mode,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        prompt_version=PROMPT_VERSION,
        dspy_version=getattr(dspy, "__version__", "unknown"),
        split=split,
        split_manifest=split_manifest,
        api_base=api_base,
        row_count=len(records),
        extra={
            "artifact_kind": "gan2026_boundary_state_graph_builder_diagnostic",
            "pipeline_family": "hybrid_clinical_frequency_state_graph",
            "component_role": "boundary_state_graph_node_builder",
            "claim_language": (
                "Hosted graph-builder diagnostic only. It constructs exact-evidence "
                "unknown/unresolved-multiple nodes and emits no final Gan label."
            ),
        },
    )
    metadata["dspy_cache"] = dspy_cache
    metadata["reuse_source"] = reuse_source
    program = DspyBoundaryStateGraphBuilder()
    if mode == "live":
        dspy.configure(
            lm=build_dspy_lm(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=dspy_cache,
                api_base=api_base,
            )
        )

    rows: list[dict[str, Any]] = []
    for record in records:
        surface_role = _surface_role(record.source_row_index)
        prompt_input_json = build_prompt_input(record, surface_role=surface_role)
        raw_output = reuse_raw_outputs.get(record.source_row_index, "")
        call_error: str | None = None
        reused_raw_output = raw_output != ""
        if mode == "live" and not reused_raw_output:
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.boundary_state_graph_builder_json)
            except Exception as exc:  # pragma: no cover - live API dependent.
                call_error = f"{type(exc).__name__}: {exc}"

        structured_record, parse_errors = (
            parse_boundary_state_builder_json(raw_output, note_text=record.note_text)
            if raw_output
            else (None, ["not_run"])
        )
        evidence_summary = _evidence_summary(record.note_text, structured_record)
        rows.append(
            {
                "source_row_index": record.source_row_index,
                "split": split,
                "split_manifest": split_manifest,
                "surface_role": surface_role,
                "pipeline_name": PROMPT_VERSION,
                "prompt_version": PROMPT_VERSION,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "reused_raw_output": reused_raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "structured_record": structured_record,
                "evidence_summary": evidence_summary,
                "representability_gain_candidate": _representability_gain_candidate(
                    record,
                    structured_record,
                    parse_errors,
                ),
                "reference": {
                    "gold_label": record.gold_label,
                    "gold_normalized_label": record.gold_normalized_label,
                    "gold_label_kind": record.gold_label_kind.value,
                    "row_ok": record.row_ok,
                },
            }
        )

    metadata["summary"] = summarize_rows(rows)
    return rows, metadata


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize graph-builder smoke results."""

    row_count = len(rows)
    return {
        "row_count": row_count,
        "schema_valid_rows": sum(not row.get("parse_errors") for row in rows),
        "call_failures": sum(bool(row.get("call_error")) for row in rows),
        "reused_raw_outputs": sum(bool(row.get("reused_raw_output")) for row in rows),
        "exact_evidence_valid": sum(
            int((row.get("evidence_summary") or {}).get("exact_evidence_valid", 0))
            for row in rows
        ),
        "exact_evidence_total": sum(
            int((row.get("evidence_summary") or {}).get("exact_evidence_total", 0))
            for row in rows
        ),
        "representability_gain_candidates": sum(
            bool(row.get("representability_gain_candidate")) for row in rows
        ),
    }


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    """Write a compact graph-builder run report."""

    summary = metadata["summary"]
    lines = [
        "# Gan 2026 Boundary-State Graph Builder Smoke",
        "",
        "This is a hosted graph-builder diagnostic, not a benchmark result.",
        "",
        f"- Prompt version: `{PROMPT_VERSION}`",
        f"- Mode: `{metadata['mode']}`",
        f"- Model: `{metadata['model']}`",
        f"- Split: `{metadata['split']}`",
        f"- Split manifest: `{metadata['split_manifest']}`",
        f"- Rows: {summary['row_count']}",
        f"- JSONL artifact: `{jsonl_path}`",
        "",
        "## Smoke Summary",
        "",
        f"- Schema-valid rows: {summary['schema_valid_rows']}/{summary['row_count']}",
        f"- Call failures: {summary['call_failures']}",
        f"- Reused raw outputs: {summary['reused_raw_outputs']}",
        f"- Exact evidence: {summary['exact_evidence_valid']}/"
        f"{summary['exact_evidence_total']}",
        f"- Representability gain candidates: "
        f"{summary['representability_gain_candidates']}/{summary['row_count']}",
        "",
        "## Rows",
        "",
        "| Source row | Surface role | Gold kind | Parse errors | Gain candidate |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for row in rows:
        errors = ", ".join(row.get("parse_errors") or []) or "none"
        reference = row.get("reference") or {}
        lines.append(
            f"| {row['source_row_index']} | {row['surface_role']} | "
            f"{reference.get('gold_label_kind')} | {errors} | "
            f"{bool(row.get('representability_gain_candidate'))} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _validate_unresolved_multiple_node_label(
    node: BoundaryStateNodeRecord,
    errors: list[str],
    index: int,
) -> None:
    if not node.node_normalized_label:
        errors.append(f"node[{index}].unresolved_multiple_label_missing")
        return
    try:
        parsed = label_to_frequency_record(node.node_normalized_label)
    except ValueError as exc:
        errors.append(f"node[{index}].unresolved_multiple_label_invalid:{exc}")
        return
    if parsed.kind is not FrequencyLabelKind.UNRESOLVED_MULTIPLE:
        errors.append(f"node[{index}].unresolved_multiple_label_kind_mismatch")


def _evidence_summary(
    note_text: str,
    structured_record: Mapping[str, Any] | None,
) -> dict[str, int]:
    nodes = list((structured_record or {}).get("nodes") or [])
    return {
        "exact_evidence_total": len(nodes),
        "exact_evidence_valid": sum(
            evidence_is_substring(note_text, str(node.get("evidence") or ""))
            for node in nodes
        ),
    }


def _representability_gain_candidate(
    record: GanFrequencyRecord,
    structured_record: Mapping[str, Any] | None,
    parse_errors: Sequence[str],
) -> bool:
    if parse_errors or not structured_record:
        return False
    for node in structured_record.get("nodes") or []:
        if record.gold_label_kind is FrequencyLabelKind.UNKNOWN:
            if node.get("semantic_kind") == "unknown":
                return True
        elif record.gold_label_kind is FrequencyLabelKind.UNRESOLVED_MULTIPLE:
            if node.get("node_normalized_label") == record.gold_normalized_label:
                return True
    return False


def _surface_role(source_row_index: int) -> str:
    if source_row_index in SYNTHETIC_UNKNOWN_STRESS_SOURCE_ROW_INDICES:
        return "synthetic_unknown_stress"
    return "validation_boundary_missing"


def _load_surface_records(args: argparse.Namespace) -> tuple[list[GanFrequencyRecord], str, str]:
    if args.surface == "synthetic_unknown_stress":
        cases = hard_cases.load_synthetic_hard_cases(args.hard_cases_jsonl)
        records = select_synthetic_unknown_stress_rows(
            hard_cases.synthetic_records_from_cases(cases)
        )
        return records, hard_cases.SYNTHETIC_SPLIT_NAME, hard_cases.SYNTHETIC_SPLIT_MANIFEST

    records = select_validation_missing_rows(load_records_for_split("validation"))
    manifest = load_split_manifest()
    return records, "validation_hard_slices", str(
        manifest.get("manifest_version", "gan2026_split_v1")
    )


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run/replay the Gan 2026 boundary-state graph-builder smoke."
    )
    parser.add_argument(
        "--surface",
        choices=("validation_boundary_missing", "synthetic_unknown_stress"),
        default="validation_boundary_missing",
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=700)
    parser.add_argument("--mode", choices=("live", "prompt-only"), default="prompt-only")
    parser.add_argument("--reuse-raw-outputs", type=Path, default=None)
    parser.add_argument(
        "--hard-cases-jsonl",
        type=Path,
        default=hard_cases.DEFAULT_HARD_CASES_JSONL_PATH,
    )
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    records, split, split_manifest = _load_surface_records(args)
    if args.limit is not None:
        records = records[: args.limit]
    reuse_raw_outputs = (
        load_raw_outputs_by_source_index(args.reuse_raw_outputs)
        if args.reuse_raw_outputs
        else {}
    )
    rows, metadata = run_boundary_state_graph_builder_split(
        records,
        split=split,
        split_manifest=split_manifest,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        mode=args.mode,
        dspy_cache=True,
        api_base=args.api_base,
        reuse_raw_outputs=reuse_raw_outputs,
        reuse_source=str(args.reuse_raw_outputs) if args.reuse_raw_outputs else None,
    )
    write_jsonl_rows(rows, args.jsonl)
    write_report(rows, metadata, args.markdown, jsonl_path=args.jsonl)
    print(json.dumps(metadata["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
