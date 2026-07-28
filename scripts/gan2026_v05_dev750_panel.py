"""Reconcile, validate, summarize, and attribute the frozen Gan v0.5 dev750 panel."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.core.evidence import EvidenceGrade, grade_evidence, is_grounded
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import (
    convert_to_categories,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import hybrid_structured_events
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports import (
    llm_structured_events_report,
)

PROMPT_VERSION = hybrid_structured_events.PROMPT_VERSION_V0_5
TRACE_SCHEMA = "gan2026.row_trace.v1"
BLOCKING_PREFIXES = (
    "invalid_json:",
    "json_parse_error:",
    "schema_validation_error:",
    "unscorable_final_label:",
    "not_run",
)


@dataclass(frozen=True)
class ConditionSpec:
    slug: str
    model: str
    execution_group: str
    transport: str
    temperature: float | None
    cli_temperature: float
    max_tokens: int
    reuse_candidate: str | None
    resume_candidate: str | None


def load_config(path: Path) -> tuple[dict[str, Any], list[ConditionSpec]]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("prompt_version") != PROMPT_VERSION:
        raise ValueError(f"config prompt version is not frozen v0.5: {path}")
    if config.get("split") != "validation":
        raise ValueError(f"config split is not validation: {path}")
    if config.get("split_manifest") != "gan2026_split_v1":
        raise ValueError(f"config split manifest drifted: {path}")
    if config.get("pipeline") != "llm_with_rules":
        raise ValueError(f"config pipeline drifted: {path}")
    if config.get("repair_mode") != "hybrid_full_stack":
        raise ValueError(f"config repair mode drifted: {path}")
    if config.get("dspy_cache") is not False:
        raise ValueError(f"config must disable DSPy cache: {path}")
    conditions = []
    for raw in config["conditions"]:
        temperature = raw.get("temperature")
        cli_temperature = raw.get("cli_temperature", temperature)
        conditions.append(
            ConditionSpec(
                slug=str(raw["slug"]),
                model=str(raw["model"]),
                execution_group=str(raw["execution_group"]),
                transport=str(raw["transport"]),
                temperature=float(temperature) if temperature is not None else None,
                cli_temperature=float(cli_temperature) if cli_temperature is not None else 0.0,
                max_tokens=int(raw["max_tokens"]),
                reuse_candidate=(
                    str(raw["reuse_candidate"]) if raw.get("reuse_candidate") else None
                ),
                resume_candidate=(
                    str(raw["resume_candidate"]) if raw.get("resume_candidate") else None
                ),
            )
        )
    if len(conditions) != 6 or len({item.slug for item in conditions}) != 6:
        raise ValueError("v0.5 dev750 config must contain six unique conditions")
    return config, conditions


def validate_reuse_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    expected_indices: set[int],
    expected_prompt_inputs: Mapping[int, Mapping[str, Any]],
    require_complete: bool,
) -> dict[str, int]:
    indices = [int(row["source_row_index"]) for row in rows]
    unique_indices = set(indices)
    if len(indices) != len(unique_indices):
        raise ValueError("reuse artifact contains duplicate source_row_index values")
    if not unique_indices.issubset(expected_indices):
        raise ValueError("reuse artifact contains rows outside the validation manifest")
    if require_complete and unique_indices != expected_indices:
        raise ValueError("reuse artifact does not match the complete manifest")
    if not rows:
        raise ValueError("reuse artifact is empty")
    prompt_matches = 0
    raw_outputs = 0
    for row in rows:
        index = int(row["source_row_index"])
        if row.get("split") != "validation":
            raise ValueError(f"reuse row {index} has the wrong split")
        if row.get("split_manifest") != "gan2026_split_v1":
            raise ValueError(f"reuse row {index} has the wrong split manifest")
        if row.get("prompt_version") != PROMPT_VERSION:
            raise ValueError(f"reuse row {index} has the wrong prompt version")
        prompt = _json_mapping(row.get("prompt_input_json"))
        expected_prompt = expected_prompt_inputs.get(index)
        if expected_prompt is None or prompt != expected_prompt:
            raise ValueError(f"reuse row {index} prompt payload does not match frozen v0.5")
        prompt_matches += 1
        if not str(row.get("raw_output") or "").strip():
            raise ValueError(f"reuse row {index} has an empty raw model output")
        raw_outputs += 1
    return {
        "rows": len(rows),
        "unique_source_rows": len(unique_indices),
        "prompt_payload_matches": prompt_matches,
        "raw_outputs": raw_outputs,
    }


def reconcile_complete_condition(
    *,
    repo_root: Path,
    config_path: Path,
    slug: str,
    overwrite: bool = False,
) -> dict[str, Any]:
    config, conditions = load_config(config_path)
    _validate_prompt_snapshot(repo_root, config)
    condition = _condition_by_slug(conditions, slug)
    if not condition.reuse_candidate:
        raise ValueError(f"{slug} has no declared complete reuse candidate")
    source = repo_root / condition.reuse_candidate
    rows = load_jsonl_rows(source)
    records = load_records_for_split("validation")
    expected_indices = {int(record.source_row_index) for record in records}
    prompts = _expected_prompt_inputs(records)
    identity = validate_reuse_rows(
        rows,
        expected_indices=expected_indices,
        expected_prompt_inputs=prompts,
        require_complete=True,
    )
    output_dir = repo_root / str(config["artifact_root"]) / slug
    rows_path = output_dir / "validation750.rows.jsonl"
    report_path = output_dir / "validation750.report.md"
    provenance_path = output_dir / "validation750.provenance.json"
    if not overwrite and any(path.exists() for path in (rows_path, report_path, provenance_path)):
        raise FileExistsError(f"reconciliation output already exists for {slug}")

    raw_outputs = {
        int(row["source_row_index"]): str(row["raw_output"])
        for row in rows
    }
    hybrid_structured_events.set_active_prompt_version(PROMPT_VERSION)
    manifest = load_split_manifest()
    replay_rows, metadata = hybrid_structured_events.run_split(
        records,
        split="validation",
        split_manifest=str(manifest.get("manifest_version", "gan2026_split_v1")),
        model=condition.model,
        temperature=condition.cli_temperature,
        max_tokens=condition.max_tokens,
        mode="prompt-only",
        dspy_cache=False,
        escalation_reason="Predeclared Gan v0.5 dev750 saved-output reconciliation",
        reuse_raw_outputs=raw_outputs,
        reuse_source=str(source.relative_to(repo_root)),
        repair_config=hybrid_structured_events.StructuredRepairConfig.for_mode(
            "hybrid_full_stack"
        ),
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    hybrid_structured_events.write_jsonl(replay_rows, rows_path)
    llm_structured_events_report.write_report(
        replay_rows,
        metadata,
        report_path,
        jsonl_path=rows_path,
    )
    deltas = _replay_deltas(rows, replay_rows)
    provenance = {
        "schema_version": "gan2026.v05_dev750_reconciliation.v1",
        "condition": slug,
        "model": condition.model,
        "source_artifact": source.relative_to(repo_root).as_posix(),
        "source_sha256": _sha256(source),
        "output_artifact": rows_path.relative_to(repo_root).as_posix(),
        "output_sha256": _sha256(rows_path),
        "call_mode": "saved_raw_output_no_call",
        "prompt_version": PROMPT_VERSION,
        "prompt_snapshot_sha256": config["prompt_snapshot_sha256"],
        "repair_mode": config["repair_mode"],
        "identity": identity,
        "delta": deltas,
    }
    provenance_path.write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return provenance


def prepare_resume_candidate(
    *,
    repo_root: Path,
    config_path: Path,
    slug: str,
) -> dict[str, Any]:
    config, conditions = load_config(config_path)
    _validate_prompt_snapshot(repo_root, config)
    condition = _condition_by_slug(conditions, slug)
    if not condition.resume_candidate:
        raise ValueError(f"{slug} has no declared resume candidate")
    source = repo_root / condition.resume_candidate
    rows = load_jsonl_rows(source)
    records = load_records_for_split("validation")
    prompts = _expected_prompt_inputs(records)
    identity = validate_reuse_rows(
        rows,
        expected_indices={int(record.source_row_index) for record in records},
        expected_prompt_inputs=prompts,
        require_complete=False,
    )
    output = (
        repo_root
        / str(config["artifact_root"])
        / slug
        / "validation750.rows.jsonl"
    )
    provenance_path = output.with_name("validation750.resume-provenance.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        existing = load_jsonl_rows(output)
        existing_identity = validate_reuse_rows(
            existing,
            expected_indices={int(record.source_row_index) for record in records},
            expected_prompt_inputs=prompts,
            require_complete=False,
        )
        result = {
            "schema_version": "gan2026.v05_dev750_resume_provenance.v1",
            "state": "existing_target_preserved",
            "source": source.relative_to(repo_root).as_posix(),
            "source_sha256": _sha256(source),
            "target": output.relative_to(repo_root).as_posix(),
            "target_sha256_at_prepare": _sha256(output),
            "resumed_source_row_indices": sorted(
                int(row["source_row_index"]) for row in existing
            ),
            "identity": existing_identity,
        }
        provenance_path.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return result
    shutil.copy2(source, output)
    result = {
        "schema_version": "gan2026.v05_dev750_resume_provenance.v1",
        "state": "resume_candidate_copied",
        "source": source.relative_to(repo_root).as_posix(),
        "source_sha256": _sha256(source),
        "target": output.relative_to(repo_root).as_posix(),
        "target_sha256_at_prepare": _sha256(output),
        "resumed_source_row_indices": sorted(
            int(row["source_row_index"]) for row in rows
        ),
        "identity": identity,
    }
    provenance_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return result


def record_existing_partial_resume(
    *,
    repo_root: Path,
    config_path: Path,
    slug: str,
    reason: str,
) -> dict[str, Any]:
    config, conditions = load_config(config_path)
    _validate_prompt_snapshot(repo_root, config)
    _condition_by_slug(conditions, slug)
    target = (
        repo_root
        / str(config["artifact_root"])
        / slug
        / "validation750.rows.jsonl"
    )
    rows = load_jsonl_rows(target)
    records = load_records_for_split("validation")
    identity = validate_reuse_rows(
        rows,
        expected_indices={int(record.source_row_index) for record in records},
        expected_prompt_inputs=_expected_prompt_inputs(records),
        require_complete=False,
    )
    if identity["rows"] >= int(config["row_count"]):
        raise ValueError(f"{slug} is already complete; no partial resume to record")
    result = {
        "schema_version": "gan2026.v05_dev750_resume_provenance.v1",
        "state": "validated_existing_partial",
        "reason": reason,
        "source": target.relative_to(repo_root).as_posix(),
        "source_sha256_at_prepare": _sha256(target),
        "target": target.relative_to(repo_root).as_posix(),
        "resumed_source_row_indices": sorted(
            int(row["source_row_index"]) for row in rows
        ),
        "identity": identity,
    }
    provenance_path = target.with_name("validation750.resume-provenance.json")
    provenance_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return result


def classify_first_failure(
    *,
    call_error: str | None,
    parse_errors: Sequence[str],
    evidence_valid: bool,
    model_correct: bool,
    final_correct: bool,
) -> str:
    if call_error:
        return "model_transport"
    if any(str(error).startswith(BLOCKING_PREFIXES) for error in parse_errors):
        return "format_or_schema"
    if not evidence_valid:
        return "evidence_selection"
    if model_correct and not final_correct:
        return "deterministic_semantic"
    if not model_correct and not final_correct:
        return "llm_clinical_selection"
    return "none"


def summarize_condition_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    condition: ConditionSpec,
    expected_indices: set[int],
    gold_monthly: Mapping[int, float],
    rules_correct: Mapping[int, bool],
    artifact_sha256: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    indices = [int(row["source_row_index"]) for row in rows]
    unique_indices = set(indices)
    trace_rows = sum(
        (row.get("row_trace") or {}).get("schema_version") == TRACE_SCHEMA
        and (row.get("row_trace") or {}).get("method") == "llm_with_rules"
        for row in rows
    )
    counts: Counter[str] = Counter()
    first_failures: Counter[str] = Counter()
    subproblems: Counter[str] = Counter()
    details: list[dict[str, Any]] = []
    for row in rows:
        index = int(row["source_row_index"])
        raw_label = _model_boundary_label(row)
        final_label = _final_label(row)
        raw_correct = _purist_correct(raw_label, gold_monthly[index])
        final_correct = bool((row.get("comparison") or {}).get("purist_correct"))
        pragmatic_correct = bool((row.get("comparison") or {}).get("pragmatic_correct"))
        transition = _transition(raw_correct, final_correct)
        counts[f"transition:{transition}"] += 1
        counts["final_purist_correct"] += int(final_correct)
        counts["final_pragmatic_correct"] += int(pragmatic_correct)
        counts["model_boundary_purist_correct"] += int(raw_correct)
        counts["call_failures"] += int(bool(row.get("call_error")))
        parse_errors = [str(value) for value in row.get("parse_errors") or []]
        counts["blocking_parse_or_schema_failures"] += int(
            any(error.startswith(BLOCKING_PREFIXES) for error in parse_errors)
        )
        selection_evidence = _selected_evidence(row)
        note = str(_json_mapping(row.get("prompt_input_json")).get("note_text") or "")
        evidence_grade = grade_evidence(note, selection_evidence)
        evidence_exact = evidence_grade == EvidenceGrade.EXACT
        evidence_grounded = is_grounded(evidence_grade)
        counts["exact_selected_evidence"] += int(evidence_exact)
        counts["grounded_selected_evidence"] += int(evidence_grounded)
        semantic_events = [
            str(value)
            for value in (
                ((row.get("row_trace") or {}).get("deterministic_semantic") or {}).get(
                    "events"
                )
                or []
            )
        ]
        format_events = [
            str(value)
            for value in (
                ((row.get("row_trace") or {}).get("format_repair") or {}).get("events")
                or []
            )
        ]
        counts["semantic_repair_rows"] += int(bool(semantic_events))
        counts["format_repair_rows"] += int(bool(format_events))
        rules_was_correct = bool(rules_correct[index])
        counts["rules_correct_regressions"] += int(rules_was_correct and not final_correct)
        counts["rules_wrong_to_final_correct"] += int(
            not rules_was_correct and final_correct
        )
        failure_owner = classify_first_failure(
            call_error=str(row.get("call_error")) if row.get("call_error") else None,
            parse_errors=parse_errors,
            evidence_valid=evidence_exact,
            model_correct=raw_correct,
            final_correct=final_correct,
        )
        first_failures[failure_owner] += 1
        subproblem = _clinical_subproblem(selection_evidence, final_label, semantic_events)
        subproblems[subproblem] += 1
        details.append(
            {
                "model_slug": condition.slug,
                "model": condition.model,
                "source_row_index": index,
                "source_artifact_sha256": artifact_sha256,
                "raw_model_output_present": bool(str(row.get("raw_output") or "").strip()),
                "model_boundary_label": raw_label,
                "final_label": final_label,
                "model_boundary_purist_correct": raw_correct,
                "final_purist_correct": final_correct,
                "final_pragmatic_correct": pragmatic_correct,
                "score_layer_transition": transition,
                "selected_evidence": selection_evidence,
                "selected_evidence_grade": str(evidence_grade),
                "selected_evidence_exact": evidence_exact,
                "selected_evidence_grounded": evidence_grounded,
                "format_events": format_events,
                "semantic_events": semantic_events,
                "call_error": row.get("call_error"),
                "parse_errors": parse_errors,
                "rules_purist_correct": rules_was_correct,
                "rules_correct_regression": rules_was_correct and not final_correct,
                "first_failure_owner": failure_owner,
                "clinical_subproblem": subproblem,
            }
        )
    row_count = len(rows)
    summary = {
        "model_slug": condition.slug,
        "model": condition.model,
        "transport": condition.transport,
        "temperature": condition.temperature,
        "cli_temperature": condition.cli_temperature,
        "max_tokens": condition.max_tokens,
        "complete": (
            row_count == len(expected_indices)
            and unique_indices == expected_indices
            and trace_rows == row_count
        ),
        "row_count": row_count,
        "unique_source_rows": len(unique_indices),
        "trace_rows": trace_rows,
        "call_failures": counts["call_failures"],
        "blocking_parse_or_schema_failures": counts[
            "blocking_parse_or_schema_failures"
        ],
        "model_boundary_purist_correct": counts["model_boundary_purist_correct"],
        "final_purist_correct": counts["final_purist_correct"],
        "final_pragmatic_correct": counts["final_pragmatic_correct"],
        "exact_selected_evidence": counts["exact_selected_evidence"],
        "grounded_selected_evidence": counts["grounded_selected_evidence"],
        "format_repair_rows": counts["format_repair_rows"],
        "semantic_repair_rows": counts["semantic_repair_rows"],
        "deterministic_wrong_to_correct": counts["transition:wrong_to_correct"],
        "deterministic_correct_to_wrong": counts["transition:correct_to_wrong"],
        "deterministic_unchanged_correct": counts["transition:unchanged_correct"],
        "deterministic_unchanged_wrong": counts["transition:unchanged_wrong"],
        "rules_correct_regressions": counts["rules_correct_regressions"],
        "rules_wrong_to_final_correct": counts["rules_wrong_to_final_correct"],
        "first_failure_owner": dict(sorted(first_failures.items())),
        "clinical_subproblem": dict(sorted(subproblems.items())),
    }
    return summary, details


def build_panel(
    *,
    repo_root: Path,
    config_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    config, conditions = load_config(config_path)
    _validate_prompt_snapshot(repo_root, config)
    records = load_records_for_split("validation")
    expected_indices = {int(record.source_row_index) for record in records}
    gold_monthly = {
        int(record.source_row_index): float(record.gold_monthly_frequency)
        for record in records
    }
    rules_path = repo_root / (
        "experiments/gan2026_three_way_comparison_validation750_"
        "deterministic_canonical_pipeline_gpt41mini_2026-06-07.jsonl"
    )
    rules_rows = load_jsonl_rows(rules_path)
    rules_correct = {
        int(row["source_row_index"]): bool(
            (row.get("comparison") or {}).get("purist_correct")
        )
        for row in rules_rows
    }
    if set(rules_correct) != expected_indices:
        raise ValueError("deterministic rules comparator does not match dev750 manifest")
    summaries: list[dict[str, Any]] = []
    details: list[dict[str, Any]] = []
    for condition in conditions:
        relative = (
            Path(str(config["artifact_root"]))
            / condition.slug
            / "validation750.rows.jsonl"
        )
        path = repo_root / relative
        rows = load_jsonl_rows(path) if path.is_file() else []
        artifact_sha256 = _sha256(path) if path.is_file() else ""
        summary, condition_details = summarize_condition_rows(
            rows,
            condition=condition,
            expected_indices=expected_indices,
            gold_monthly=gold_monthly,
            rules_correct=rules_correct,
            artifact_sha256=artifact_sha256,
        )
        provenance_path = path.with_name("validation750.provenance.json")
        provenance = (
            json.loads(provenance_path.read_text(encoding="utf-8"))
            if provenance_path.is_file()
            else None
        )
        resume_provenance_path = path.with_name(
            "validation750.resume-provenance.json"
        )
        resume_provenance = (
            json.loads(resume_provenance_path.read_text(encoding="utf-8"))
            if resume_provenance_path.is_file()
            else None
        )
        controller_provenance_path = path.with_name(
            "validation750.controller-provenance.json"
        )
        controller_provenance = (
            json.loads(controller_provenance_path.read_text(encoding="utf-8"))
            if controller_provenance_path.is_file()
            else None
        )
        resumed_rows = len(
            (resume_provenance or {}).get("resumed_source_row_indices") or []
        )
        summaries.append(
            {
                **summary,
                "artifact": relative.as_posix(),
                "artifact_sha256": artifact_sha256 or None,
                "call_mode": (
                    "saved_raw_output_no_call"
                    if provenance
                    else "fresh_resume_across_sessions"
                    if resume_provenance
                    else "fresh_with_declared_resume_if_applicable"
                ),
                "replay_provenance": provenance,
                "resume_provenance": resume_provenance,
                "controller_provenance": controller_provenance,
                "resumed_existing_rows": resumed_rows,
                "fresh_rows": max(summary["row_count"] - resumed_rows, 0),
            }
        )
        details.extend(condition_details)
    generated = datetime.now(UTC).isoformat()
    panel = {
        "schema_version": "gan2026.v05_dev750_panel.v1",
        "generated_at_utc": generated,
        "protocol": config["protocol"],
        "configuration": config_path.relative_to(repo_root).as_posix(),
        "dataset": config["dataset"],
        "split": "validation750",
        "split_manifest": config["split_manifest"],
        "row_policy": config["row_policy"],
        "pipeline": config["pipeline"],
        "prompt_version": config["prompt_version"],
        "prompt_snapshot_sha256": config["prompt_snapshot_sha256"],
        "repair_mode": config["repair_mode"],
        "dspy_cache": config["dspy_cache"],
        "scorer": "Gan Purist primary; Pragmatic secondary",
        "trace_schema": config["row_trace_schema"],
        "complete_condition_count": sum(item["complete"] for item in summaries),
        "expected_condition_count": len(conditions),
        "conditions": summaries,
        "rules_comparator": {
            "artifact": rules_path.relative_to(repo_root).as_posix(),
            "artifact_sha256": _sha256(rules_path),
            "rows": len(rules_rows),
        },
        "claim_boundary": (
            "Development evidence for the named models, routes, v0.5 prompt, "
            "hybrid_full_stack repair, Gan scorers, and validation750 distribution; "
            "not clinical validation, a model-neutral ranking, or new holdout evidence."
        ),
    }
    attribution = {
        "schema_version": "gan2026.v05_dev750_row_attribution.v1",
        "generated_at_utc": generated,
        "protocol": config["protocol"],
        "panel_configuration": config_path.relative_to(repo_root).as_posix(),
        "dataset": config["dataset"],
        "split": "validation750",
        "split_manifest": config["split_manifest"],
        "row_policy": config["row_policy"],
        "pipeline": config["pipeline"],
        "prompt_version": config["prompt_version"],
        "prompt_snapshot_sha256": config["prompt_snapshot_sha256"],
        "repair_mode": config["repair_mode"],
        "scorer": "Gan Purist primary; Pragmatic secondary",
        "rules_comparator_sha256": _sha256(rules_path),
        "rows": details,
        "claim_boundary": panel["claim_boundary"],
    }
    return panel, attribution


def write_panel_report(panel: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 matched v0.5 six-model dev750 panel",
        "",
        f"Generated: {panel['generated_at_utc']}",
        "",
        (
            "Development evidence on `validation750`; the prompt, repair policy, "
            "scorers, and split are the frozen protocol values."
        ),
        "",
        "## Results",
        "",
        (
            "| Model | Rows | Purist | Pragmatic | Raw boundary | Exact evidence | "
            "Grounded evidence | W→C | C→W | Rules-correct regressions | Calls |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in panel["conditions"]:
        lines.append(
            f"| {item['model_slug']} | {item['row_count']} | "
            f"{item['final_purist_correct']}/750 | {item['final_pragmatic_correct']}/750 | "
            f"{item['model_boundary_purist_correct']}/750 | "
            f"{item['exact_selected_evidence']}/750 | "
            f"{item['grounded_selected_evidence']}/750 | "
            f"{item['deterministic_wrong_to_correct']} | "
            f"{item['deterministic_correct_to_wrong']} | "
            f"{item['rules_correct_regressions']} | {item['call_failures']} |"
        )
    lines.extend(
        [
            "",
            "## Attribution",
            "",
            (
                "The raw model boundary, format repair, deterministic semantic repair, "
                "final label, evidence grade, rules-control comparison, first failure, "
                "and clinical subproblem are retained per row in the companion artifact."
            ),
            "",
            "## Provenance",
            "",
        ]
    )
    for item in panel["conditions"]:
        controller_note = (
            f" controller event `{item['controller_provenance']['event']}`;"
            if item.get("controller_provenance")
            else ""
        )
        lines.append(
            f"- `{item['model_slug']}`: `{item['call_mode']}`; "
            f"{item['resumed_existing_rows']} resumed existing rows and "
            f"{item['fresh_rows']} fresh rows in the retained artifact;"
            f"{controller_note} "
            f"`{item['artifact_sha256']}`."
        )
    lines.extend(["", "## Claim boundary", "", str(panel["claim_boundary"])])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _expected_prompt_inputs(
    records: Sequence[GanFrequencyRecord],
) -> dict[int, Mapping[str, Any]]:
    return {
        int(record.source_row_index): json.loads(
            hybrid_structured_events.build_prompt_input(
                record,
                prompt_version=PROMPT_VERSION,
            )
        )
        for record in records
    }


def _condition_by_slug(
    conditions: Sequence[ConditionSpec], slug: str
) -> ConditionSpec:
    for condition in conditions:
        if condition.slug == slug:
            return condition
    raise ValueError(f"unknown condition: {slug}")


def _json_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    try:
        parsed = json.loads(str(value))
    except (TypeError, ValueError):
        return {}
    return parsed if isinstance(parsed, Mapping) else {}


def _model_boundary_label(row: Mapping[str, Any]) -> str | None:
    record = ((row.get("row_trace") or {}).get("model_prediction") or {}).get("record")
    if not isinstance(record, Mapping):
        return None
    selection = record.get("selection")
    value = selection.get("final_label") if isinstance(selection, Mapping) else None
    return str(value) if value is not None else None


def _final_label(row: Mapping[str, Any]) -> str | None:
    record = row.get("structured_record") or {}
    selection = record.get("selection") if isinstance(record, Mapping) else None
    value = selection.get("final_label") if isinstance(selection, Mapping) else None
    return str(value) if value is not None else None


def _selected_evidence(row: Mapping[str, Any]) -> str:
    record = ((row.get("row_trace") or {}).get("model_prediction") or {}).get("record")
    if not isinstance(record, Mapping):
        return ""
    selection = record.get("selection")
    return str(selection.get("evidence") or "") if isinstance(selection, Mapping) else ""


def _purist_correct(label: str | None, gold_monthly: float) -> bool:
    if not label:
        return False
    try:
        predicted = float(label_to_frequency_record(label).monthly_frequency)
    except (TypeError, ValueError):
        return False
    return (
        convert_to_categories([predicted], method="purist")[0]
        == convert_to_categories([gold_monthly], method="purist")[0]
    )


def _transition(raw_correct: bool, final_correct: bool) -> str:
    if raw_correct and final_correct:
        return "unchanged_correct"
    if raw_correct and not final_correct:
        return "correct_to_wrong"
    if not raw_correct and final_correct:
        return "wrong_to_correct"
    return "unchanged_wrong"


def _clinical_subproblem(
    evidence: str,
    label: str | None,
    semantic_events: Sequence[str],
) -> str:
    text = " ".join([evidence, label or "", *semantic_events]).lower()
    if "cluster" in text or "diary" in text:
        return "cluster_or_diary_aggregation"
    if "seizure free" in text or "seizure-free" in text or "no seizures" in text:
        return "seizure_free_boundary"
    if "unknown" in text or "uncertain" in text or "no reference" in text:
        return "uncertainty_boundary"
    if any(token in text for token in ("historical", "recent", "current", "since ")):
        return "temporal_selection"
    if any(token in text for token in (" per ", "daily", "weekly", "monthly", "yearly")):
        return "rate_denominator"
    return "competing_event_selection"


def _replay_deltas(
    before: Sequence[Mapping[str, Any]],
    after: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    before_by_index = {int(row["source_row_index"]): row for row in before}
    after_by_index = {int(row["source_row_index"]): row for row in after}
    if before_by_index.keys() != after_by_index.keys():
        raise ValueError("replay source IDs differ from the original artifact")
    counts: Counter[str] = Counter()
    for index, old in before_by_index.items():
        new = after_by_index[index]
        counts["changed_final_labels"] += int(_final_label(old) != _final_label(new))
        old_purist = bool((old.get("comparison") or {}).get("purist_correct"))
        new_purist = bool((new.get("comparison") or {}).get("purist_correct"))
        counts["purist_wrong_to_correct"] += int(not old_purist and new_purist)
        counts["purist_correct_to_wrong"] += int(old_purist and not new_purist)
        old_pragmatic = bool((old.get("comparison") or {}).get("pragmatic_correct"))
        new_pragmatic = bool((new.get("comparison") or {}).get("pragmatic_correct"))
        counts["pragmatic_wrong_to_correct"] += int(
            not old_pragmatic and new_pragmatic
        )
        counts["pragmatic_correct_to_wrong"] += int(
            old_pragmatic and not new_pragmatic
        )
    return {
        key: counts[key]
        for key in (
            "changed_final_labels",
            "purist_wrong_to_correct",
            "purist_correct_to_wrong",
            "pragmatic_wrong_to_correct",
            "pragmatic_correct_to_wrong",
        )
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_prompt_snapshot(
    repo_root: Path,
    config: Mapping[str, Any],
) -> None:
    snapshot = (
        repo_root
        / "tests"
        / "snapshots"
        / "prompt_contracts"
        / "gan2026__hybrid_structured_events_v0.5.txt"
    )
    actual = _sha256(snapshot)
    expected = str(config["prompt_snapshot_sha256"])
    if actual != expected:
        raise ValueError(
            f"frozen v0.5 prompt snapshot hash drifted: expected {expected}, got {actual}"
        )


def _comparable(value: Mapping[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != "generated_at_utc"}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/gan2026/six_model_v05_dev750_20260727.json"),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    reconcile = subparsers.add_parser("reconcile")
    reconcile.add_argument("--slug", required=True)
    reconcile.add_argument("--overwrite", action="store_true")
    resume = subparsers.add_parser("prepare-resume")
    resume.add_argument("--slug", required=True)
    record_resume = subparsers.add_parser("record-partial-resume")
    record_resume.add_argument("--slug", required=True)
    record_resume.add_argument("--reason", required=True)
    finalize = subparsers.add_parser("finalize")
    finalize.add_argument(
        "--panel-json",
        type=Path,
        default=Path("experiments/gan2026_matched_v05_dev750_panel_20260727.json"),
    )
    finalize.add_argument(
        "--attribution-json",
        type=Path,
        default=Path("experiments/gan2026_matched_v05_dev750_attribution_20260727.json"),
    )
    finalize.add_argument(
        "--markdown",
        type=Path,
        default=Path(
            "docs/experiments/gan2026/"
            "gan2026_matched_v05_dev750_panel_2026-07-27.md"
        ),
    )
    finalize.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = args.repo_root.resolve()
    config_path = args.config if args.config.is_absolute() else root / args.config
    if args.command == "reconcile":
        result = reconcile_complete_condition(
            repo_root=root,
            config_path=config_path,
            slug=args.slug,
            overwrite=args.overwrite,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.command == "prepare-resume":
        result = prepare_resume_candidate(
            repo_root=root,
            config_path=config_path,
            slug=args.slug,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.command == "record-partial-resume":
        result = record_existing_partial_resume(
            repo_root=root,
            config_path=config_path,
            slug=args.slug,
            reason=args.reason,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    panel, attribution = build_panel(repo_root=root, config_path=config_path)
    panel_path = args.panel_json if args.panel_json.is_absolute() else root / args.panel_json
    attribution_path = (
        args.attribution_json
        if args.attribution_json.is_absolute()
        else root / args.attribution_json
    )
    markdown_path = args.markdown if args.markdown.is_absolute() else root / args.markdown
    if args.check:
        expected_panel = json.loads(panel_path.read_text(encoding="utf-8"))
        expected_attribution = json.loads(attribution_path.read_text(encoding="utf-8"))
        if _comparable(panel) != _comparable(expected_panel):
            raise SystemExit(f"retained panel drift: {panel_path}")
        if _comparable(attribution) != _comparable(expected_attribution):
            raise SystemExit(f"retained attribution drift: {attribution_path}")
        print(f"Gan v0.5 dev750 panel valid: {panel_path.relative_to(root)}")
        return 0
    panel_path.parent.mkdir(parents=True, exist_ok=True)
    panel_path.write_text(
        json.dumps(panel, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    attribution_path.parent.mkdir(parents=True, exist_ok=True)
    attribution_path.write_text(
        json.dumps(attribution, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_panel_report(panel, markdown_path)
    print(
        json.dumps(
            {
                "complete": panel["complete_condition_count"],
                "expected": panel["expected_condition_count"],
                "rows": len(attribution["rows"]),
                "panel": str(panel_path),
                "attribution": str(attribution_path),
                "markdown": str(markdown_path),
            },
            sort_keys=True,
        )
    )
    return 0 if panel["complete_condition_count"] == panel["expected_condition_count"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
