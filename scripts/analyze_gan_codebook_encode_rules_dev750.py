#!/usr/bin/env python3
"""Audit conservative Gan encode rules on the saved codebook-extract dev750 raw."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.gan_cell_replay import score_label
from clinical_extraction.paper.methods import gan_machine_split
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    classify_boundary_families,
    map_pragmatic,
    map_purist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredExtractionRecord,
    StructuredRepairConfig,
    parse_structured_json_with_trace,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label_format_preserving,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence import (
    selected_evidence_derivation,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence.codebook_encode import (
    CODEBOOK_ENCODE_RULE_IDS,
    CodebookEncodeTrace,
    repair_codebook_label_with_evidence,
)

ROOT = discover_repo_root(start=Path(__file__))
SOURCE_ROWS = (
    ROOT
    / "experiments/paper/gan_llm_extract/gemini37flash/dev750/rows.jsonl"
)
OUT_DIR = ROOT / "experiments/gan_codebook_encode_rule_development_20260822"
PROTOCOL = (
    "docs/research/gan2026/"
    "gan_codebook_encode_rule_development_protocol_2026-08-22.md"
)
MODEL = "gemini/gemini-3.7-flash"
PROMPT_VERSION = "gan_llm_extract"
SCORER = "Gan Purist category accuracy; exact normalized label is diagnostic"
MANUAL_SCORER_GOLD_ROWS = frozenset({190, 10481})
MANUAL_SELECT_ROWS = frozenset({13889})


def _git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _package_version(package: str) -> str:
    try:
        return version(package)
    except PackageNotFoundError:
        return "not-installed"


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _score(record: GanFrequencyRecord, label: str | None) -> dict[str, Any]:
    scored = score_label(record, label)
    payload = dict(scored)
    payload["exact_label_correct"] = bool(
        scored["scorable"]
        and scored.get("predicted_label") == record.gold_normalized_label
    )
    if scored["scorable"]:
        parsed = label_to_frequency_record(str(label))
        payload["predicted_monthly_frequency"] = parsed.monthly_frequency
        payload["predicted_purist_category"] = str(
            map_purist(parsed.monthly_frequency)
        )
        payload["predicted_pragmatic_category"] = str(
            map_pragmatic(parsed.monthly_frequency)
        )
    else:
        payload["predicted_monthly_frequency"] = None
        payload["predicted_purist_category"] = "unscorable"
        payload["predicted_pragmatic_category"] = "unscorable"
    return payload


def _arm_summary(rows: Sequence[Mapping[str, Any]], arm: str) -> dict[str, Any]:
    scores = [row["arms"][arm] for row in rows]
    n = len(scores)
    purist = sum(bool(score["purist_correct"]) for score in scores)
    pragmatic = sum(bool(score["pragmatic_correct"]) for score in scores)
    exact = sum(bool(score["exact_label_correct"]) for score in scores)
    scorable = sum(bool(score["scorable"]) for score in scores)
    kinds = Counter(str(score.get("predicted_kind") or "unscorable") for score in scores)
    return {
        "purist_correct": purist,
        "purist_accuracy": round(purist / n, 4),
        "pragmatic_correct": pragmatic,
        "pragmatic_accuracy": round(pragmatic / n, 4),
        "exact_label_correct": exact,
        "exact_label_accuracy": round(exact / n, 4),
        "scorable": scorable,
        "predicted_kinds": dict(kinds),
    }


def _transition(before: Mapping[str, Any], after: Mapping[str, Any], key: str) -> str:
    before_ok = bool(before[key])
    after_ok = bool(after[key])
    if after_ok and not before_ok:
        return "rescue"
    if before_ok and not after_ok:
        return "harm"
    return "correct_stay" if after_ok else "wrong_stay"


def _change_shape(before: str | None, after: str | None) -> str:
    if before == after:
        return "unchanged"
    before_kind = selected_evidence_derivation.parsed_frequency_kind(before)
    after_kind = selected_evidence_derivation.parsed_frequency_kind(after)
    if before_kind != after_kind:
        return "semantic_kind_change"
    before_text = str(before or "")
    after_text = str(after or "")
    if ("cluster" in before_text) != ("cluster" in after_text):
        return "cluster_structure_change"
    before_numbers = [part for part in before_text.split() if part.isdigit()]
    after_numbers = [part for part in after_text.split() if part.isdigit()]
    if before_numbers != after_numbers:
        return "count_or_window_change"
    return "same_kind_form_change"


def _selected_event_kinds(extraction: StructuredExtractionRecord) -> tuple[str, ...]:
    selected = set(extraction.selection.selected_event_ids)
    return tuple(
        str(event.kind) for event in extraction.events if event.event_id in selected
    )


def _candidate_trace(
    extraction: StructuredExtractionRecord,
    record: GanFrequencyRecord,
    enabled_rule_ids: frozenset[str] | None = None,
) -> CodebookEncodeTrace:
    return repair_codebook_label_with_evidence(
        extraction.selection.final_label,
        extraction.selection.evidence,
        selected_event_kinds=_selected_event_kinds(extraction),
        context_text=record.note_text,
        enabled_rule_ids=enabled_rule_ids,
    )


def _parse(
    raw_output: str,
    record: GanFrequencyRecord,
    mode: str,
) -> tuple[
    StructuredExtractionRecord | None,
    list[dict[str, Any]],
    list[str],
    dict[str, Any],
]:
    extraction, normalized, errors, trace = parse_structured_json_with_trace(
        raw_output,
        note_text=record.note_text,
        repair_config=StructuredRepairConfig.for_mode(mode),
    )
    return extraction, [item.model_dump() for item in normalized], errors, trace


def _event_has_gold_category(
    record: GanFrequencyRecord,
    normalized_events: Sequence[Mapping[str, Any]],
) -> bool:
    for event in normalized_events:
        label = event.get("normalized_label")
        if label and _score(record, str(label))["purist_correct"]:
            return True
    return False


def _residual_owner(
    source_row_index: int,
    *,
    candidate_score: Mapping[str, Any],
    full_select_score: Mapping[str, Any],
    normalized_events: Sequence[Mapping[str, Any]],
) -> tuple[str, str]:
    if candidate_score["purist_correct"]:
        return "none", "candidate is Purist-correct"
    if source_row_index in MANUAL_SCORER_GOLD_ROWS:
        return (
            "scorer_gold_convention",
            "The source-preserving model form conflicts with the Gan gold projection.",
        )
    if source_row_index in MANUAL_SELECT_ROWS:
        return (
            "select_revision",
            "Changing unknown to seizure-free for current non-epileptic events is selection.",
        )
    if full_select_score["purist_correct"]:
        return (
            "select_revision",
            "The existing semantic select stack repairs the saved extract on this row.",
        )
    if _event_has_gold_category(
        _RECORDS_BY_INDEX[source_row_index],
        normalized_events,
    ):
        return (
            "selection",
            "A selected-event candidate reaches the gold category, but the "
            "extract answer does not.",
        )
    return (
        "extract_or_unresolved",
        "No normalized selected-event candidate reaches the gold category; "
        "the saved extraction lacks a demonstrated safe encode repair.",
    )


def _row_artifact(
    record: GanFrequencyRecord,
    source_row: Mapping[str, Any],
) -> dict[str, Any]:
    raw_output = str(source_row.get("raw_output") or "")
    raw, _, raw_errors, raw_trace = _parse(raw_output, record, "raw_model")
    current, current_events, current_errors, current_trace = _parse(
        raw_output, record, "llm_encode"
    )
    candidate, candidate_events, candidate_errors, candidate_trace = _parse(
        raw_output, record, "gan_rules_encode"
    )
    full_select, _, full_select_errors, _ = _parse(raw_output, record, "llm_select")

    if raw is None:
        arms = {
            name: _score(record, None)
            for name in (
                "identity",
                "format_only",
                "current_rule_encode",
                "candidate_rule_encode",
                "full_select_diagnostic",
            )
        }
        return {
            "schema_version": "gan2026.codebook_encode_rule_row.dev750.v1",
            "dataset": "Gan 2026 synthetic",
            "split": "dev750",
            "row_policy": "development_review_permitted",
            "data_text_policy": "synthetic_development_raw_text_diagnostic",
            "source_row_index": record.source_row_index,
            "note_text": record.note_text,
            "gold": _gold_payload(record),
            "model_selection": None,
            "arms": arms,
            "parse_errors": raw_errors,
            "current_rule": None,
            "candidate_rule": None,
            "failure_bucket": "extract_parse_failure",
            "first_failure_owner": "extract_parse",
            "first_failure_reason": "Saved raw output did not parse into the extract schema.",
        }

    identity_label = raw.selection.final_label
    format_label = repair_prediction_label_format_preserving(identity_label)
    current_label = current.selection.final_label if current else None
    candidate_label = candidate.selection.final_label if candidate else None
    full_select_label = full_select.selection.final_label if full_select else None
    arms = {
        "identity": _score(record, identity_label),
        "format_only": _score(record, format_label),
        "current_rule_encode": _score(record, current_label),
        "candidate_rule_encode": _score(record, candidate_label),
        "full_select_diagnostic": _score(record, full_select_label),
    }
    pure_candidate = _candidate_trace(raw, record)
    if pure_candidate.final_label != candidate_label:
        raise RuntimeError(
            f"candidate pipeline/pure mismatch on {record.source_row_index}: "
            f"{pure_candidate.final_label!r} != {candidate_label!r}"
        )
    current_changed_hops = [
        hop
        for hop in current_trace.get("answer_states", [])
        if hop.get("before") != hop.get("after")
        and hop.get("stage_id") != "gan.model.selection"
    ]
    candidate_changed_hops = [
        hop
        for hop in candidate_trace.get("answer_states", [])
        if hop.get("before") != hop.get("after")
        and hop.get("stage_id") != "gan.model.selection"
    ]
    owner, reason = _residual_owner(
        record.source_row_index,
        candidate_score=arms["candidate_rule_encode"],
        full_select_score=arms["full_select_diagnostic"],
        normalized_events=candidate_events,
    )
    candidate_purist_direction = _transition(
        arms["identity"], arms["candidate_rule_encode"], "purist_correct"
    )
    if arms["candidate_rule_encode"]["purist_correct"]:
        failure_bucket = (
            "candidate_rescue"
            if candidate_purist_direction == "rescue"
            else "candidate_correct_stay"
        )
    else:
        failure_bucket = f"candidate_residual:{owner}"
    return {
        "schema_version": "gan2026.codebook_encode_rule_row.dev750.v1",
        "dataset": "Gan 2026 synthetic",
        "split": "dev750",
        "row_policy": "development_review_permitted",
        "data_text_policy": "synthetic_development_raw_text_diagnostic",
        "source_row_index": record.source_row_index,
        "note_text": record.note_text,
        "gold": _gold_payload(record),
        "boundary_families": list(
            classify_boundary_families(
                note_text=record.note_text,
                gold_per_month=record.gold_monthly_frequency,
            )
        ),
        "model_selection": {
            "selected_event_ids": list(raw.selection.selected_event_ids),
            "final_kind": str(raw.selection.final_kind),
            "final_label": identity_label,
            "confidence": str(raw.selection.confidence),
            "evidence": raw.selection.evidence,
            "evidence_exact": evidence_is_substring(
                record.note_text, raw.selection.evidence
            ),
            "selected_event_kinds": list(_selected_event_kinds(raw)),
            "events": [event.model_dump() for event in raw.events],
        },
        "arms": arms,
        "labels": {
            "identity": identity_label,
            "format_only": format_label,
            "current_rule_encode": current_label,
            "candidate_rule_encode": candidate_label,
            "full_select_diagnostic": full_select_label,
        },
        "parse_errors": {
            "identity": raw_errors,
            "current_rule_encode": current_errors,
            "candidate_rule_encode": candidate_errors,
            "full_select_diagnostic": full_select_errors,
        },
        "current_rule": {
            "changed": identity_label != current_label,
            "purist_direction": _transition(
                arms["identity"], arms["current_rule_encode"], "purist_correct"
            ),
            "exact_label_direction": _transition(
                arms["identity"],
                arms["current_rule_encode"],
                "exact_label_correct",
            ),
            "change_shape": _change_shape(identity_label, current_label),
            "changed_hops": current_changed_hops,
            "selected_event_ids_changed": (
                current is not None
                and current.selection.selected_event_ids
                != raw.selection.selected_event_ids
            ),
        },
        "candidate_rule": {
            "changed": identity_label != candidate_label,
            "purist_direction": candidate_purist_direction,
            "exact_label_direction": _transition(
                arms["identity"],
                arms["candidate_rule_encode"],
                "exact_label_correct",
            ),
            "change_shape": _change_shape(identity_label, candidate_label),
            "rule_ids": [event.rule_id for event in pure_candidate.events],
            "events": [event.__dict__ for event in pure_candidate.events],
            "changed_hops": candidate_changed_hops,
            "selected_event_ids_changed": (
                candidate is not None
                and candidate.selection.selected_event_ids
                != raw.selection.selected_event_ids
            ),
        },
        "normalized_selected_events": {
            "current_rule_encode": current_events,
            "candidate_rule_encode": candidate_events,
        },
        "identity_trace": raw_trace,
        "failure_bucket": failure_bucket,
        "first_failure_owner": owner,
        "first_failure_reason": reason,
    }


def _gold_payload(record: GanFrequencyRecord) -> dict[str, Any]:
    return {
        "label": record.gold_label,
        "normalized_label": record.gold_normalized_label,
        "label_kind": str(record.gold_label_kind),
        "monthly_frequency": record.gold_monthly_frequency,
        "purist_category": str(map_purist(record.gold_monthly_frequency)),
        "pragmatic_category": str(map_pragmatic(record.gold_monthly_frequency)),
        "row_ok": record.row_ok,
    }


def _candidate_labels_for_rules(
    rows: Sequence[Mapping[str, Any]],
    enabled_rule_ids: frozenset[str],
) -> dict[int, str | None]:
    labels: dict[int, str | None] = {}
    for row in rows:
        source_row_index = int(row["source_row_index"])
        selection = row.get("model_selection")
        if not isinstance(selection, Mapping):
            labels[source_row_index] = None
            continue
        record = _RECORDS_BY_INDEX[source_row_index]
        raw = _SOURCE_BY_INDEX[source_row_index]
        extraction, _, _, _ = _parse(str(raw["raw_output"]), record, "raw_model")
        if extraction is None:
            labels[source_row_index] = None
            continue
        labels[source_row_index] = _candidate_trace(
            extraction,
            record,
            enabled_rule_ids=enabled_rule_ids,
        ).final_label
    return labels


def _labels_summary(labels: Mapping[int, str | None]) -> dict[str, Any]:
    n = len(_RECORDS_BY_INDEX)
    purist = pragmatic = exact = scorable = 0
    for source_row_index, record in _RECORDS_BY_INDEX.items():
        scored = _score(record, labels.get(source_row_index))
        purist += int(scored["purist_correct"])
        pragmatic += int(scored["pragmatic_correct"])
        exact += int(scored["exact_label_correct"])
        scorable += int(scored["scorable"])
    return {
        "purist_correct": purist,
        "purist_accuracy": round(purist / n, 4),
        "pragmatic_correct": pragmatic,
        "pragmatic_accuracy": round(pragmatic / n, 4),
        "exact_label_correct": exact,
        "exact_label_accuracy": round(exact / n, 4),
        "scorable": scorable,
    }


def _rule_ablation(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    all_rules = frozenset(CODEBOOK_ENCODE_RULE_IDS)
    isolated: dict[str, Any] = {}
    leave_one_out: dict[str, Any] = {}
    for rule_id in sorted(all_rules):
        isolated[rule_id] = _labels_summary(
            _candidate_labels_for_rules(rows, frozenset({rule_id}))
        )
        leave_one_out[rule_id] = _labels_summary(
            _candidate_labels_for_rules(rows, all_rules - {rule_id})
        )
    return {"isolated": isolated, "leave_one_out": leave_one_out}


def _change_summary(
    rows: Sequence[Mapping[str, Any]],
    field: str,
) -> dict[str, Any]:
    changed = [
        row
        for row in rows
        if isinstance(row.get(field), Mapping) and row[field].get("changed")
    ]
    return {
        "changed_rows": len(changed),
        "purist_directions": dict(
            Counter(str(row[field]["purist_direction"]) for row in changed)
        ),
        "exact_label_directions": dict(
            Counter(str(row[field]["exact_label_direction"]) for row in changed)
        ),
        "change_shapes": dict(
            Counter(str(row[field]["change_shape"]) for row in changed)
        ),
        "rule_ids": dict(
            Counter(
                rule_id
                for row in changed
                for rule_id in row[field].get("rule_ids", [])
            )
        ),
        "selected_event_id_changes": sum(
            bool(row[field].get("selected_event_ids_changed")) for row in changed
        ),
    }


def _label_change_summary(
    rows: Sequence[Mapping[str, Any]],
    *,
    before_arm: str,
    after_arm: str,
) -> dict[str, Any]:
    changed = [
        row
        for row in rows
        if row.get("labels")
        and row["labels"].get(before_arm) != row["labels"].get(after_arm)
    ]
    return {
        "changed_rows": len(changed),
        "purist_directions": dict(
            Counter(
                _transition(
                    row["arms"][before_arm],
                    row["arms"][after_arm],
                    "purist_correct",
                )
                for row in changed
            )
        ),
        "exact_label_directions": dict(
            Counter(
                _transition(
                    row["arms"][before_arm],
                    row["arms"][after_arm],
                    "exact_label_correct",
                )
                for row in changed
            )
        ),
        "change_shapes": dict(
            Counter(
                _change_shape(
                    row["labels"].get(before_arm),
                    row["labels"].get(after_arm),
                )
                for row in changed
            )
        ),
    }


def _head_to_head(
    rows: Sequence[Mapping[str, Any]],
    *,
    first_arm: str,
    second_arm: str,
    key: str,
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        first_ok = bool(row["arms"][first_arm][key])
        second_ok = bool(row["arms"][second_arm][key])
        if first_ok and second_ok:
            counts["both_correct"] += 1
        elif first_ok:
            counts[f"{first_arm}_only"] += 1
        elif second_ok:
            counts[f"{second_arm}_only"] += 1
        else:
            counts["neither_correct"] += 1
    return dict(counts)


def _candidate_rule_contributions(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    contributions: dict[str, Any] = {}
    for rule_id in sorted(CODEBOOK_ENCODE_RULE_IDS):
        changed = [
            row
            for row in rows
            if isinstance(row.get("candidate_rule"), Mapping)
            and rule_id in row["candidate_rule"].get("rule_ids", [])
        ]
        contributions[rule_id] = {
            "changed_rows": len(changed),
            "purist_directions": dict(
                Counter(row["candidate_rule"]["purist_direction"] for row in changed)
            ),
            "exact_label_directions": dict(
                Counter(
                    row["candidate_rule"]["exact_label_direction"] for row in changed
                )
            ),
        }
    return contributions


def _boundary_slice_results(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    families = sorted(
        {
            str(family)
            for row in rows
            for family in row.get("boundary_families", [])
        }
    )
    results: dict[str, Any] = {}
    for family in families:
        slice_rows = [
            row for row in rows if family in row.get("boundary_families", [])
        ]
        results[family] = {
            "row_count": len(slice_rows),
            "purist": {
                arm: {
                    "correct": sum(
                        bool(row["arms"][arm]["purist_correct"]) for row in slice_rows
                    ),
                    "accuracy": round(
                        sum(
                            bool(row["arms"][arm]["purist_correct"])
                            for row in slice_rows
                        )
                        / len(slice_rows),
                        4,
                    ),
                }
                for arm in (
                    "identity",
                    "current_rule_encode",
                    "candidate_rule_encode",
                )
            },
            "candidate_changed_purist_directions": dict(
                Counter(
                    str(row["candidate_rule"]["purist_direction"])
                    for row in slice_rows
                    if isinstance(row.get("candidate_rule"), Mapping)
                    and row["candidate_rule"].get("changed")
                )
            ),
        }
    return results


def main() -> None:
    if not SOURCE_ROWS.is_file():
        raise FileNotFoundError(f"missing saved codebook extract rows: {SOURCE_ROWS}")
    if set(_SOURCE_BY_INDEX) != set(_RECORDS_BY_INDEX):
        raise RuntimeError("saved extract source indices do not match dev750")
    if len(_RECORDS_BY_INDEX) != 750:
        raise RuntimeError(f"expected 750 dev rows, found {len(_RECORDS_BY_INDEX)}")

    rows = [
        _row_artifact(record, _SOURCE_BY_INDEX[source_row_index])
        for source_row_index, record in sorted(_RECORDS_BY_INDEX.items())
    ]
    current_changes = _change_summary(rows, "current_rule")
    candidate_changes = _change_summary(rows, "candidate_rule")
    candidate_harms = [
        row["source_row_index"]
        for row in rows
        if isinstance(row.get("candidate_rule"), Mapping)
        and row["candidate_rule"].get("purist_direction") == "harm"
    ]
    candidate_exact_harms = [
        row["source_row_index"]
        for row in rows
        if isinstance(row.get("candidate_rule"), Mapping)
        and row["candidate_rule"].get("exact_label_direction") == "harm"
    ]
    if candidate_harms or candidate_exact_harms:
        raise RuntimeError(
            "candidate regression audit failed: "
            f"{candidate_harms=} {candidate_exact_harms=}"
        )
    if candidate_changes["selected_event_id_changes"]:
        raise RuntimeError("candidate encode changed selected event ids")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    changes = [
        row
        for row in rows
        if isinstance(row.get("candidate_rule"), Mapping)
        and row["candidate_rule"].get("changed")
    ]
    residuals = [
        row for row in rows if not row["arms"]["candidate_rule_encode"]["purist_correct"]
    ]
    write_jsonl_rows(rows, OUT_DIR / "rows.jsonl")
    write_jsonl_rows(changes, OUT_DIR / "changes.jsonl")
    write_jsonl_rows(residuals, OUT_DIR / "residuals.jsonl")

    summary = {
        "schema_version": "gan2026.codebook_encode_rule_development.dev750.v1",
        "generated_utc": datetime.now(UTC).isoformat(),
        "protocol": PROTOCOL,
        "dataset": "Gan 2026 synthetic",
        "split": "dev750",
        "split_manifest": "gan2026_split_v1",
        "row_count": len(rows),
        "source_indices_match": True,
        "row_policy": "development_review_permitted",
        "holdout_policy": "test450_not_loaded_or_inspected",
        "data_text_policy": "synthetic_development_raw_text_diagnostic",
        "source_extract": SOURCE_ROWS.relative_to(ROOT).as_posix(),
        "source_extract_sha256": _file_sha256(SOURCE_ROWS),
        "model": MODEL,
        "prompt_version": PROMPT_VERSION,
        "program": "Gan structured events plus selection",
        "model_calls": 0,
        "replay_state": "saved_raw_output_no_call_deterministic_replay",
        "scorer": SCORER,
        "repair_policy": (
            "preserve parsed model codebook labels; apply only independently "
            "switchable high-precision gap repairs"
        ),
        "git_head": _git_output("rev-parse", "HEAD"),
        "dirty_tree": bool(_git_output("status", "--short")),
        "runtime": {
            "python": sys.version.split()[0],
            "pydantic": _package_version("pydantic"),
            "dspy": _package_version("dspy"),
        },
        "implementation_sha256": {
            path.relative_to(ROOT).as_posix(): _file_sha256(path)
            for path in (
                Path(__file__),
                ROOT
                / "src/clinical_extraction/tasks/seizure_frequency/gan2026/"
                "selected_evidence/codebook_encode.py",
                ROOT
                / "src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/"
                "hybrid_structured_events.py",
            )
        },
        "gold_purist_distribution": dict(
            Counter(row["gold"]["purist_category"] for row in rows)
        ),
        "gold_pragmatic_distribution": dict(
            Counter(row["gold"]["pragmatic_category"] for row in rows)
        ),
        "arms": {
            arm: _arm_summary(rows, arm)
            for arm in (
                "identity",
                "format_only",
                "current_rule_encode",
                "candidate_rule_encode",
                "full_select_diagnostic",
            )
        },
        "current_rule_change_analysis": current_changes,
        "format_only_change_analysis": _label_change_summary(
            rows,
            before_arm="identity",
            after_arm="format_only",
        ),
        "candidate_rule_change_analysis": candidate_changes,
        "candidate_rule_contributions": _candidate_rule_contributions(rows),
        "current_vs_candidate": {
            "purist": _head_to_head(
                rows,
                first_arm="current_rule_encode",
                second_arm="candidate_rule_encode",
                key="purist_correct",
            ),
            "exact_label": _head_to_head(
                rows,
                first_arm="current_rule_encode",
                second_arm="candidate_rule_encode",
                key="exact_label_correct",
            ),
        },
        "candidate_rule_ids": sorted(CODEBOOK_ENCODE_RULE_IDS),
        "candidate_ablation": _rule_ablation(rows),
        "boundary_slice_results": _boundary_slice_results(rows),
        "residual_count": len(residuals),
        "residual_failure_buckets": dict(
            Counter(str(row["failure_bucket"]) for row in residuals)
        ),
        "residual_first_failure_owners": dict(
            Counter(str(row["first_failure_owner"]) for row in residuals)
        ),
        "candidate_regressions": {
            "purist": candidate_harms,
            "exact_label": candidate_exact_harms,
        },
        "claim_boundary": (
            "Inspected development evidence on the saved Gemini "
            "gan_llm_extract dev750 raw distribution. "
            "Not holdout evidence or clinical validation."
        ),
        "artifacts": {
            "rows": "rows.jsonl",
            "changes": "changes.jsonl",
            "residuals": "residuals.jsonl",
        },
    }
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


_RECORDS_BY_INDEX = {
    record.source_row_index: record
    for record in load_records_for_split(gan_machine_split("dev750"))
}
_SOURCE_BY_INDEX = {
    int(row["source_row_index"]): row for row in load_jsonl_rows(SOURCE_ROWS)
}


if __name__ == "__main__":
    main()
