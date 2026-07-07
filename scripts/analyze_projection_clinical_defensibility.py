"""Audit projection outputs for clinical defensibility rather than label agreement."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import dspy
from tqdm import tqdm

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments import (
    run_single_task_controls,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import (
    Gan2026PipelineV1,
)

DEFAULT_MATRIX_PATH = Path("experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.jsonl")
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_projection_instruction_heavy_clinical_defensibility_2026-06-04.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_projection_instruction_heavy_clinical_defensibility_2026-06-04.md"
)

DEFENSIBILITY_VALUES = {
    "clinically_defensible",
    "clinically_debatable",
    "not_clinically_defensible",
    "insufficient_information_to_judge",
}
ERROR_FAMILIES = {
    "none_defensible",
    "reasonable_alternative_to_answer_key",
    "null_or_abstention_when_statement_supported",
    "no_reference_collapse",
    "seizure_free_overreach",
    "ignores_active_events_or_spells",
    "wrong_rate_or_over_specific_label",
    "wrong_time_basis_or_currentness",
    "cluster_cadence_or_burden_confusion",
    "conditional_event_mishandled",
    "competing_semiology_mishandled",
    "input_target_distractor",
    "rationale_label_mismatch",
    "other",
}


class ProjectionClinicalDefensibilitySignature(dspy.Signature):
    """Judge whether a seizure-frequency projection is clinically defensible."""

    audit_input_json: str = dspy.InputField(
        desc="JSON with a clinical note, fixed projection input, and model output."
    )
    audit_output_json: str = dspy.OutputField(
        desc="One JSON object matching the requested audit schema."
    )


class ProjectionClinicalDefensibilityJudge(dspy.Module):
    def __init__(self) -> None:
        self.predict = dspy.Predict(ProjectionClinicalDefensibilitySignature)

    def forward(self, audit_input_json: str) -> dspy.Prediction:
        return self.predict(audit_input_json=audit_input_json)


def build_audit_input(
    *,
    record: Any,
    row: Mapping[str, Any],
    candidate: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> str:
    payload = {
        "task": (
            "Judge whether the model's selected seizure-frequency statement is clinically "
            "defensible from the full note and from the fixed candidate/evidence input."
        ),
        "instructions": [
            (
                "Clinically defensible means a clinician could reasonably state it from the "
                "note without ignoring material contradictory seizure-frequency information."
            ),
            (
                "Do not judge by agreement with an answer key. A different statement can be "
                "clinically defensible if it is supported by the note."
            ),
            (
                "Separate full-note defensibility from fixed-input defensibility. If the "
                "fixed input points at a distractor but the full note contradicts it, mark "
                "input_relative_defensibility as clinically_defensible or clinically_debatable "
                "and note_relative_defensibility as not_clinically_defensible."
            ),
            (
                "Treat null or abstained labels as clinically defensible only when no useful "
                "current seizure-frequency statement is supportable."
            ),
            (
                "Treat seizure freedom as not clinically defensible when current or recent "
                "events, clusters, spells, or another active seizure type remain present."
            ),
            (
                "Treat conditional events as events. If the rate is not stated, unknown can "
                "be defensible, but seizure freedom is not."
            ),
            (
                "For clusters, distinguish how often clusters happen from how many seizures "
                "occur inside a cluster."
            ),
            (
                "Return exactly one JSON object. Keep rationales short and cite short exact "
                "phrases from the note or fixed evidence when helpful."
            ),
        ],
        "allowed_defensibility_values": sorted(DEFENSIBILITY_VALUES),
        "allowed_error_families": sorted(ERROR_FAMILIES),
        "output_schema": {
            "clinical_statement_selected": "Brief statement of what the model selected.",
            "note_relative_defensibility": sorted(DEFENSIBILITY_VALUES),
            "input_relative_defensibility": sorted(DEFENSIBILITY_VALUES),
            "primary_error_family": sorted(ERROR_FAMILIES),
            "secondary_error_families": "List of zero or more allowed error families.",
            "clinically_defensible_even_if_different": "Boolean.",
            "projection_error": (
                "Boolean; true when note_relative_defensibility is not clinically_defensible."
            ),
            "input_problem": (
                "Boolean; true when fixed candidate/evidence is a distractor or incomplete target."
            ),
            "supporting_evidence": "Short exact phrase or empty string.",
            "contradicting_evidence": "Short exact phrase or empty string.",
            "rationale": "Two short sentences or fewer.",
        },
        "source_row_index": row["source_row_index"],
        "panel_id": row["row_panel_id"],
        "full_note": record.note_text,
        "fixed_candidate": dict(candidate),
        "fixed_evidence": dict(evidence),
        "model_projection_output": row.get("component_output") or {},
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def run_audit(
    *,
    matrix_path: Path = DEFAULT_MATRIX_PATH,
    condition_id: str = "projection_only_instruction_heavy",
    model: str = "openai/gpt-4.1-mini",
    temperature: float = 0.0,
    max_tokens: int = 1200,
    force: bool = False,
    output_jsonl_path: Path = DEFAULT_JSONL_PATH,
) -> list[dict[str, Any]]:
    lm = build_dspy_lm(model, temperature=temperature, max_tokens=max_tokens, cache=True)
    dspy.configure(lm=lm)
    judge = ProjectionClinicalDefensibilityJudge()
    pipeline = Gan2026PipelineV1()
    records = {record.source_row_index: record for record in load_records_for_split("validation")}
    matrix_rows = [
        row
        for row in load_jsonl_rows(matrix_path)
        if row.get("condition_id") == condition_id and row.get("component_output")
    ]
    existing_by_key = {}
    if output_jsonl_path.exists() and not force:
        existing_by_key = {
            (row["condition_id"], row["row_panel_id"], int(row["source_row_index"])): row
            for row in load_jsonl_rows(output_jsonl_path)
        }

    audit_rows: list[dict[str, Any]] = []
    for row in tqdm(matrix_rows, desc="Auditing clinical defensibility"):
        key = (row["condition_id"], row["row_panel_id"], int(row["source_row_index"]))
        if key in existing_by_key:
            audit_rows.append(existing_by_key[key])
            continue
        record = records[int(row["source_row_index"])]
        result = pipeline.run(record)
        diagnostics = result.diagnostics
        final_selection = diagnostics["final_selection"]
        candidate_event = next(
            (
                candidate
                for candidate in diagnostics["candidate_events"]
                if candidate["event_id"] == final_selection.get("event_id")
            ),
            diagnostics["candidate_events"][0],
        )
        normalized_event = next(
            (
                event
                for event in diagnostics["normalized_events"]
                if event["event_id"] == candidate_event["event_id"]
            ),
            diagnostics["normalized_events"][0],
        )
        candidate = run_single_task_controls.map_candidate_to_schema(
            candidate_event, normalized_event
        )
        evidence = run_single_task_controls.map_evidence_to_schema(
            final_selection, candidate_event, normalized_event
        )
        audit_input = build_audit_input(
            record=record,
            row=row,
            candidate=candidate,
            evidence=evidence,
        )
        raw_output = str(judge(audit_input_json=audit_input).audit_output_json)
        parsed = parse_audit_output(raw_output)
        audit_rows.append(
            {
                "artifact_kind": "gan2026_projection_clinical_defensibility_row",
                "condition_id": condition_id,
                "row_panel_id": row["row_panel_id"],
                "source_row_index": int(row["source_row_index"]),
                "split": row.get("split"),
                "gold_label_reference_only": row.get("gold_label"),
                "gold_kind_reference_only": row.get("gold_kind"),
                "hidden_families": row.get("hidden_families") or [],
                "model_projection_output": row.get("component_output") or {},
                "fixed_candidate": candidate,
                "fixed_evidence": evidence,
                "audit_model": model,
                "audit_prompt_boundary": (
                    "Clinical defensibility audit; answer-key label is metadata only "
                    "and is not sent to the judge."
                ),
                "clinical_defensibility_audit": parsed,
                "raw_audit_output": raw_output,
            }
        )
        write_jsonl_rows(audit_rows, output_jsonl_path)
    write_jsonl_rows(audit_rows, output_jsonl_path)
    return audit_rows


def parse_audit_output(raw_output: str) -> dict[str, Any]:
    clean = raw_output.strip()
    if clean.startswith("```"):
        clean = clean.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        parsed = json.loads(clean)
    except json.JSONDecodeError as exc:
        return {
            "clinical_statement_selected": "",
            "note_relative_defensibility": "insufficient_information_to_judge",
            "input_relative_defensibility": "insufficient_information_to_judge",
            "primary_error_family": "other",
            "secondary_error_families": ["other"],
            "clinically_defensible_even_if_different": False,
            "projection_error": True,
            "input_problem": False,
            "supporting_evidence": "",
            "contradicting_evidence": "",
            "rationale": f"Audit JSON parse failed: {exc.msg}",
        }
    return normalize_audit(parsed)


def normalize_audit(parsed: Mapping[str, Any]) -> dict[str, Any]:
    note_def = _allowed(
        parsed.get("note_relative_defensibility"),
        DEFENSIBILITY_VALUES,
        "insufficient_information_to_judge",
    )
    input_def = _allowed(
        parsed.get("input_relative_defensibility"),
        DEFENSIBILITY_VALUES,
        "insufficient_information_to_judge",
    )
    primary = _allowed(parsed.get("primary_error_family"), ERROR_FAMILIES, "other")
    secondaries = [
        _allowed(item, ERROR_FAMILIES, "other")
        for item in parsed.get("secondary_error_families") or []
    ]
    return {
        "clinical_statement_selected": str(parsed.get("clinical_statement_selected") or ""),
        "note_relative_defensibility": note_def,
        "input_relative_defensibility": input_def,
        "primary_error_family": primary,
        "secondary_error_families": sorted(set(secondaries)),
        "clinically_defensible_even_if_different": bool(
            parsed.get("clinically_defensible_even_if_different")
        ),
        "projection_error": _is_projection_error(note_def),
        "input_problem": bool(parsed.get("input_problem")),
        "supporting_evidence": str(parsed.get("supporting_evidence") or ""),
        "contradicting_evidence": str(parsed.get("contradicting_evidence") or ""),
        "rationale": str(parsed.get("rationale") or ""),
    }


def write_report(
    rows: Sequence[Mapping[str, Any]],
    *,
    path: Path = DEFAULT_REPORT_PATH,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
) -> None:
    audits = [row["clinical_defensibility_audit"] for row in rows]
    by_note_def = Counter(audit["note_relative_defensibility"] for audit in audits)
    by_input_def = Counter(audit["input_relative_defensibility"] for audit in audits)
    error_rows = [
        row
        for row in rows
        if _is_projection_error(row["clinical_defensibility_audit"]["note_relative_defensibility"])
    ]
    non_error_rows = [
        row
        for row in rows
        if not _is_projection_error(
            row["clinical_defensibility_audit"]["note_relative_defensibility"]
        )
    ]
    by_error = Counter(
        row["clinical_defensibility_audit"]["primary_error_family"] for row in error_rows
    )
    by_non_error_family = Counter(
        row["clinical_defensibility_audit"]["primary_error_family"] for row in non_error_rows
    )
    by_panel: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        by_panel[str(row["row_panel_id"])].append(row)

    lines = [
        "# Projection Clinical Defensibility Audit",
        "",
        "Question: when the instruction-heavy projection prompt disagrees with the "
        "reference label, is the selected clinical statement still defensible?",
        "",
        f"- JSONL artifact: `{jsonl_path}`",
        f"- Rows audited: {len(rows)}",
        f"- Full-note projection errors: {len(error_rows)}",
        f"- Full-note clinically defensible or debatable: {len(non_error_rows)}",
        (
            "- Full-note errors that were defensible or debatable from the fixed input: "
            f"{_input_defensible_note_error_count(rows)}"
        ),
        "- Scope: validation-development rows only; reference labels are metadata, "
        "not the judge target.",
        "",
        "## Defensibility Counts",
        "",
        "| Defensibility | Full note | Fixed input |",
        "| --- | ---: | ---: |",
    ]
    for key in sorted(DEFENSIBILITY_VALUES):
        lines.append(f"| `{key}` | {by_note_def[key]} | {by_input_def[key]} |")
    lines.extend(
        [
            "",
            "## Panel Summary",
            "",
            "| Panel | Rows | Clinically defensible | Debatable | Not defensible | Input problem |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for panel, panel_rows in sorted(by_panel.items()):
        panel_audits = [row["clinical_defensibility_audit"] for row in panel_rows]
        defensible = sum(
            audit["note_relative_defensibility"] == "clinically_defensible"
            for audit in panel_audits
        )
        debatable = sum(
            audit["note_relative_defensibility"] == "clinically_debatable" for audit in panel_audits
        )
        not_defensible = sum(
            audit["note_relative_defensibility"] == "not_clinically_defensible"
            for audit in panel_audits
        )
        input_problem = sum(audit["input_problem"] for audit in panel_audits)
        lines.append(
            f"| `{panel}` | {len(panel_rows)} | {defensible} | {debatable} | "
            f"{not_defensible} | {input_problem} |"
        )
    lines.extend(
        [
            "",
            "## Primary Error Families For Full-Note Errors",
            "",
            "| Family | Rows |",
            "| --- | ---: |",
        ]
    )
    for family, count in by_error.most_common():
        lines.append(f"| `{family}` | {count} |")
    lines.extend(
        [
            "",
            "## Non-Error Clinical Patterns",
            "",
            "| Family | Rows |",
            "| --- | ---: |",
        ]
    )
    for family, count in by_non_error_family.most_common():
        lines.append(f"| `{family}` | {count} |")
    lines.extend(["", "## Representative Rows", ""])
    for family, _ in by_error.most_common():
        examples = [
            row
            for row in error_rows
            if row["clinical_defensibility_audit"]["primary_error_family"] == family
        ][:5]
        lines.append(f"### `{family}`")
        lines.append("")
        lines.append("| Row | Panel | Selected statement | Full-note defensibility | Rationale |")
        lines.append("| ---: | --- | --- | --- | --- |")
        for row in examples:
            audit = row["clinical_defensibility_audit"]
            lines.append(
                f"| {row['source_row_index']} | `{row['row_panel_id']}` | "
                f"{_md(audit['clinical_statement_selected'])} | "
                f"`{audit['note_relative_defensibility']}` | {_md(audit['rationale'])} |"
            )
        lines.append("")
    lines.append("## Representative Defensible Rows")
    lines.append("")
    lines.append("| Row | Panel | Selected statement | Family | Rationale |")
    lines.append("| ---: | --- | --- | --- | --- |")
    for row in non_error_rows[:12]:
        audit = row["clinical_defensibility_audit"]
        lines.append(
            f"| {row['source_row_index']} | `{row['row_panel_id']}` | "
            f"{_md(audit['clinical_statement_selected'])} | "
            f"`{audit['primary_error_family']}` | {_md(audit['rationale'])} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _allowed(value: Any, allowed: set[str], fallback: str) -> str:
    text = str(value or "").strip()
    return text if text in allowed else fallback


def _md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def _input_defensible_note_error_count(rows: Sequence[Mapping[str, Any]]) -> int:
    return sum(
        _is_projection_error(row["clinical_defensibility_audit"]["note_relative_defensibility"])
        and row["clinical_defensibility_audit"]["input_relative_defensibility"]
        in {"clinically_defensible", "clinically_debatable"}
        for row in rows
    )


def _is_projection_error(note_relative_defensibility: str) -> bool:
    return note_relative_defensibility in {
        "not_clinically_defensible",
        "insufficient_information_to_judge",
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix-path", type=Path, default=DEFAULT_MATRIX_PATH)
    parser.add_argument(
        "--condition-id",
        default="projection_only_instruction_heavy",
    )
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1200)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    rows = run_audit(
        matrix_path=args.matrix_path,
        condition_id=args.condition_id,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        force=args.force,
        output_jsonl_path=args.output_jsonl_path,
    )
    write_report(rows, path=args.report_path, jsonl_path=args.output_jsonl_path)
    print(f"Wrote {len(rows)} clinical defensibility audit rows to {args.output_jsonl_path}")
    print(f"Wrote report to {args.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
