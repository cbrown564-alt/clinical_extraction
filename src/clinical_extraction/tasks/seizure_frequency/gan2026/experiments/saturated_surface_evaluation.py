"""Saturated-surface hard-slice and selective-action tooling for Gan 2026."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_DATA_PATH,
    DEFAULT_SPLIT_MANIFEST_PATH,
    GanFrequencyRecord,
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

DEFAULT_HYBRID_V02_JSONL_PATH = Path(
    "experiments/"
    "gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_gpt41mini_v02_live_"
    "2026-06-01.jsonl"
)
DEFAULT_SLICES_JSON_PATH = Path(
    "experiments/gan2026_hybrid_adjudicator_v02_validation_hard_slices_2026-06-01.json"
)
DEFAULT_SELECTIVE_JSON_PATH = Path(
    "experiments/gan2026_hybrid_adjudicator_v02_selective_action_report_2026-06-01.json"
)
DEFAULT_SELECTIVE_REPORT_PATH = Path(
    "experiments/gan2026_hybrid_adjudicator_v02_selective_action_report_2026-06-01.md"
)


SLICE_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "slice_name": "deterministic_miss",
        "membership_rule": (
            "Artifact row is validation, gold row_ok=True, and deterministic top is Purist-wrong."
        ),
        "primary_metric": "wrong-to-correct rate and evidence validity",
    },
    {
        "slice_name": "temporal_conflict",
        "membership_rule": (
            "Validation note contains current/recent/now language plus historical/previous/stale "
            "frequency language."
        ),
        "primary_metric": "regression-controlled correction rate",
    },
    {
        "slice_name": "seizure_free_overreach",
        "membership_rule": (
            "Deterministic top predicts seizure-free/no-event while gold is not seizure-free, or "
            "text combines seizure-free language with breakthrough/event language."
        ),
        "primary_metric": "overreach correction precision",
    },
    {
        "slice_name": "unknown_no_reference_boundary",
        "membership_rule": (
            "Deterministic top predicts no seizure frequency reference while seizure/event "
            "discussion is present, or the LLM changes no-reference to unknown."
        ),
        "primary_metric": "flag precision and scorer-equivalent churn",
    },
    {
        "slice_name": "cluster_or_diary",
        "membership_rule": (
            "Gold label or text contains cluster, diary, month-list, calendar, cumulative count, "
            "or distributed-count signals."
        ),
        "primary_metric": "hard-slice F1 plus correction precision",
    },
    {
        "slice_name": "shorthand_interval_range",
        "membership_rule": (
            "Text contains q-interval shorthand, every-interval, inter-seizure interval, range, "
            "or maximum-burden language."
        ),
        "primary_metric": "format-normalization correction precision",
    },
    {
        "slice_name": "candidate_absent_or_weak",
        "membership_rule": (
            "Deterministic top is Purist-wrong and the candidate-recall proxy does not recall the "
            "gold Purist category."
        ),
        "primary_metric": "flag-only utility, not final-label promotion",
    },
)


def build_saturated_surface_result(
    rows: Sequence[Mapping[str, Any]],
    *,
    slices: Mapping[str, Any],
    artifact_path: str | None = None,
) -> dict[str, Any]:
    """Build one report payload over saved v0.2 adjudicator rows and hard slices."""

    split = _first_value(rows, "split", "validation")
    split_manifest = _first_value(rows, "split_manifest", "gan2026_split_v1")
    return {
        "artifact_kind": "gan2026_hybrid_adjudicator_saturated_surface_selective_actions",
        "candidate": "hybrid_rules_candidates_llm_adjudicator_v0.2",
        "split": split,
        "split_manifest": split_manifest,
        "source_artifact": artifact_path,
        "row_count": len(rows),
        "inspection_policy": (
            "Validation-only hard-slice and selective-action analysis over saved v0.2 artifacts; "
            "no locked-test row inspection and no hosted calls."
        ),
        "selective_actions": summarize_selective_actions(rows),
        "slice_selective_actions": {
            slice_record["slice_name"]: summarize_selective_actions(
                _rows_for_source_indices(
                    rows,
                    [member["source_row_index"] for member in slice_record["members"]],
                )
            )
            for slice_record in slices.get("slices", [])
        },
        "validation_hard_slices": slices,
        "stop_rule": (
            "Promote only if changed-label precision is high on dominant deterministic-miss "
            "families with evidence-valid accepted changes and low regression cost; otherwise "
            "revise, keep diagnostic, or reject added complexity."
        ),
    }


def summarize_selective_actions(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize raw-change, gated-change, and flag-only behavior against deterministic top."""

    return {
        "raw_change": _summarize_mode(rows, mode="raw_change"),
        "gated_change": _summarize_mode(rows, mode="gated_change"),
        "flag_only": _summarize_mode(rows, mode="flag_only"),
    }


def build_validation_hard_slices(
    records: Sequence[GanFrequencyRecord],
    rows: Sequence[Mapping[str, Any]],
    *,
    split: str = "validation",
    split_manifest: str = "gan2026_split_v1",
    source_artifact: str | None = None,
) -> dict[str, Any]:
    """Create reproducible validation hard-slice membership from records and saved rows."""

    rows_by_index = {int(row["source_row_index"]): row for row in rows}
    members_by_slice: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        row = rows_by_index.get(record.source_row_index)
        if row is None:
            continue
        for slice_name, triggers in _slice_triggers(record, row).items():
            if triggers:
                members_by_slice[slice_name].append(
                    {
                        "source_row_index": record.source_row_index,
                        "triggers": sorted(set(triggers)),
                        "deterministic_label": _score_label(row, "deterministic_top"),
                        "raw_adjudicator_label": _score_label(row, "raw_adjudicator"),
                        "gated_label": _score_label(row, "conservative_adjudicator"),
                        "gold_label": record.gold_label,
                    }
                )

    slices = []
    for definition in SLICE_DEFINITIONS:
        members = sorted(
            members_by_slice.get(definition["slice_name"], []),
            key=lambda member: member["source_row_index"],
        )
        slices.append({**definition, "row_count": len(members), "members": members})
    return {
        "artifact_kind": "gan2026_validation_hard_slices",
        "candidate": "hybrid_rules_candidates_llm_adjudicator_v0.2",
        "split": split,
        "split_manifest": split_manifest,
        "source_artifact": source_artifact,
        "row_policy": "validation rows only; row_ok filter applies to deterministic_miss",
        "slice_definitions": list(SLICE_DEFINITIONS),
        "slices": slices,
    }


def write_saturated_surface_json(result: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_validation_hard_slices_json(result: Mapping[str, Any], path: Path) -> None:
    write_saturated_surface_json(result, path)


def write_saturated_surface_report(result: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 Hybrid Adjudicator V0.2 Selective-Action Report",
        "",
        "This is a validation-development artifact over saved v0.2 rows. It is not a "
        "holdout result, benchmark claim, or permission to inspect locked-test rows.",
        "",
        f"- Candidate: `{result['candidate']}`",
        f"- Split: `{result['split']}`",
        f"- Split manifest: `{result['split_manifest']}`",
        f"- Rows: {result['row_count']}",
        f"- Source artifact: `{result.get('source_artifact') or 'in-memory rows'}`",
        "",
        "## Selective-Action Summary",
        "",
        "| Mode | Action rate | Actions | Wrong-to-correct | Correct-to-wrong | "
        "Precision | Recall | Boundary churn | Evidence-valid changes | Fallback/abstain |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mode, summary in result["selective_actions"].items():
        lines.append(_summary_row(mode, summary))

    lines.extend(
        [
            "",
            "## Validation Hard Slices",
            "",
            "| Slice | Rows | Raw precision | Raw W->C | Raw C->W | Gated precision | "
            "Gated W->C | Gated C->W | Flag precision |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    slices = {
        slice_record["slice_name"]: slice_record
        for slice_record in result["validation_hard_slices"].get("slices", [])
    }
    for slice_name, summaries in result["slice_selective_actions"].items():
        slice_record = slices[slice_name]
        raw = summaries["raw_change"]
        gated = summaries["gated_change"]
        flag = summaries["flag_only"]
        lines.append(
            f"| {slice_name} | {slice_record['row_count']} | "
            f"{_fmt_float(raw['changed_label_precision'])} | {raw['wrong_to_correct']} | "
            f"{raw['correct_to_wrong']} | {_fmt_float(gated['changed_label_precision'])} | "
            f"{gated['wrong_to_correct']} | {gated['correct_to_wrong']} | "
            f"{_fmt_float(flag['flag_precision_for_deterministic_miss'])} |"
        )

    lines.extend(["", "## Slice Definitions", ""])
    for slice_record in result["validation_hard_slices"].get("slices", []):
        lines.extend(
            [
                f"### {slice_record['slice_name']}",
                "",
                f"- Rows: {slice_record['row_count']}",
                f"- Membership: {slice_record['membership_rule']}",
                f"- Primary metric: {slice_record['primary_metric']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Interpretation",
            "",
            _interpret_selective_actions(result["selective_actions"]),
            "",
            "Stop rule: " + str(result["stop_rule"]),
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build saturated-surface validation hard slices and selective-action reports "
            "from saved Gan 2026 hybrid adjudicator artifacts."
        )
    )
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_HYBRID_V02_JSONL_PATH)
    parser.add_argument("--split", choices=("validation",), default="validation")
    parser.add_argument("--data-path", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--manifest-path", type=Path, default=DEFAULT_SPLIT_MANIFEST_PATH)
    parser.add_argument("--slices-json", type=Path, default=DEFAULT_SLICES_JSON_PATH)
    parser.add_argument("--json", type=Path, default=DEFAULT_SELECTIVE_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_SELECTIVE_REPORT_PATH)
    args = parser.parse_args(argv)

    rows = load_jsonl_rows(args.jsonl)
    records = load_records_for_split(args.split, args.data_path, args.manifest_path)
    manifest = load_split_manifest(args.manifest_path)
    split_manifest = str(manifest.get("manifest_version", "gan2026_split_v1"))
    slices = build_validation_hard_slices(
        records,
        rows,
        split=args.split,
        split_manifest=split_manifest,
        source_artifact=str(args.jsonl),
    )
    result = build_saturated_surface_result(rows, slices=slices, artifact_path=str(args.jsonl))
    write_validation_hard_slices_json(slices, args.slices_json)
    write_saturated_surface_json(result, args.json)
    write_saturated_surface_report(result, args.markdown)
    print(
        json.dumps(
            {
                "rows": len(rows),
                "slices_json": str(args.slices_json),
                "json": str(args.json),
                "markdown": str(args.markdown),
            },
            sort_keys=True,
        )
    )


def _summarize_mode(rows: Sequence[Mapping[str, Any]], *, mode: str) -> dict[str, Any]:
    action_count = 0
    non_equivalent_changes = 0
    wrong_to_correct = 0
    correct_to_wrong = 0
    boundary_churn = 0
    evidence_valid_changes = 0
    fallback_or_abstention = 0
    flagged_deterministic_misses = 0
    deterministic_misses = 0
    deterministic_correct_touched = 0
    for row in rows:
        deterministic = _score(row, "deterministic_top")
        candidate = _candidate_score_for_mode(row, mode)
        if not deterministic.get("purist_correct"):
            deterministic_misses += 1
        action = _action_for_mode(row, mode, deterministic, candidate)
        if not action:
            continue
        action_count += 1
        if not deterministic.get("purist_correct"):
            flagged_deterministic_misses += 1
        if deterministic.get("purist_correct"):
            deterministic_correct_touched += 1
        if mode == "flag_only":
            continue
        same_purist = deterministic.get("purist_correct") == candidate.get("purist_correct")
        same_pragmatic = deterministic.get("pragmatic_correct") == candidate.get(
            "pragmatic_correct"
        )
        if same_purist and same_pragmatic:
            boundary_churn += 1
        else:
            non_equivalent_changes += 1
        if not deterministic.get("purist_correct") and candidate.get("purist_correct"):
            wrong_to_correct += 1
        if deterministic.get("purist_correct") and not candidate.get("purist_correct"):
            correct_to_wrong += 1
        if _selected_evidence_valid(row):
            evidence_valid_changes += 1
        if _used_fallback_or_abstained(row, mode):
            fallback_or_abstention += 1

    total = len(rows)
    return {
        "rows": total,
        "changed_or_flagged": action_count,
        "action_rate": round(action_count / total, 4) if total else 0.0,
        "non_equivalent_changes": non_equivalent_changes,
        "wrong_to_correct": wrong_to_correct,
        "correct_to_wrong": correct_to_wrong,
        "changed_label_precision": (
            round(wrong_to_correct / non_equivalent_changes, 4)
            if non_equivalent_changes
            else None
        ),
        "changed_label_recall": (
            round(wrong_to_correct / deterministic_misses, 4) if deterministic_misses else None
        ),
        "regression_rate_touched": (
            round(correct_to_wrong / deterministic_correct_touched, 4)
            if deterministic_correct_touched
            else None
        ),
        "scorer_equivalent_boundary_churn": boundary_churn,
        "evidence_valid_changes": evidence_valid_changes,
        "evidence_valid_change_rate": (
            round(evidence_valid_changes / action_count, 4) if action_count else None
        ),
        "fallback_or_abstention": fallback_or_abstention,
        "flagged_deterministic_misses": flagged_deterministic_misses,
        "deterministic_misses": deterministic_misses,
        "flag_precision_for_deterministic_miss": (
            round(flagged_deterministic_misses / action_count, 4) if action_count else None
        ),
    }


def _slice_triggers(
    record: GanFrequencyRecord,
    row: Mapping[str, Any],
) -> dict[str, list[str]]:
    note = record.note_text.lower()
    deterministic = _score(row, "deterministic_top")
    raw = _score(row, "raw_adjudicator")
    triggers: dict[str, list[str]] = {
        definition["slice_name"]: [] for definition in SLICE_DEFINITIONS
    }
    if record.row_ok and deterministic.get("purist_correct") is False:
        triggers["deterministic_miss"].append("deterministic_purist_wrong")
    if _has_temporal_conflict(note):
        triggers["temporal_conflict"].append("current_and_historical_frequency_language")
    deterministic_label = str(deterministic.get("final_label") or "").lower()
    if (
        ("seizure free" in deterministic_label or "no seizure" in deterministic_label)
        and record.gold_label.lower() not in {"seizure free", "0 per month"}
    ):
        triggers["seizure_free_overreach"].append("deterministic_no_event_prediction")
    if _has_seizure_free_breakthrough(note):
        triggers["seizure_free_overreach"].append("seizure_free_plus_breakthrough_text")
    if (
        deterministic_label == "no seizure frequency reference"
        and _contains_any(note, ("seizure", "event", "episode", "spell"))
    ):
        triggers["unknown_no_reference_boundary"].append(
            "deterministic_no_reference_with_event_discussion"
        )
    if (
        deterministic_label == "no seizure frequency reference"
        and str(raw.get("final_label") or "").lower() == "unknown"
    ):
        triggers["unknown_no_reference_boundary"].append("raw_llm_no_reference_to_unknown")
    if _has_cluster_diary_context(note + " " + record.gold_label.lower()):
        triggers["cluster_or_diary"].append("cluster_or_diary_text")
    if _has_month_list_count_context(note):
        triggers["cluster_or_diary"].append("month_list_text")
    if _has_shorthand_or_interval(note):
        triggers["shorthand_interval_range"].append("shorthand_interval_or_range_text")
    recall = row.get("candidate_recall") or {}
    if (
        deterministic.get("purist_correct") is False
        and recall.get("purist_category_recalled") is False
    ):
        triggers["candidate_absent_or_weak"].append("candidate_recall_proxy_missed_gold")
    return triggers


def _has_temporal_conflict(note: str) -> bool:
    current = ("current", "currently", "now", "recent", "recently", "today", "this month")
    historical = ("histor", "previous", "prior", "formerly", "used to", "last year", "baseline")
    return _contains_any(note, current) and _contains_any(note, historical)


def _has_seizure_free_breakthrough(note: str) -> bool:
    free = ("seizure free", "no seizures", "without seizures")
    breakthrough = ("breakthrough", "since then", "last week", "last month", "had a seizure")
    return _contains_any(note, free) and _contains_any(note, breakthrough)


def _has_shorthand_or_interval(note: str) -> bool:
    if re.search(r"\bq\d", note) or re.search(r"\bq\s*\d", note):
        return True
    if re.search(r"\bevery\s+\d+", note):
        return True
    if re.search(r"\b\d+\s*(?:-|to)\s*\d+\s*(?:per|/|x)", note):
        return True
    return _contains_any(note, ("inter-seizure", "interseizure", "interval", "maximum", "max "))


def _has_cluster_diary_context(note: str) -> bool:
    return bool(
        re.search(r"\bclusters?\b", note)
        or re.search(r"\bdiar(?:y|ies)\b", note)
        or re.search(r"\bcalendars?\b", note)
        or re.search(r"\bcharts?\b", note)
        or re.search(r"\blogs?\b", note)
    )


def _has_month_list_count_context(note: str) -> bool:
    month_mentions = re.findall(
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\b",
        note,
    )
    if len(month_mentions) < 2:
        return False
    return bool(
        re.search(
            r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\b"
            r".{0,80}\b(?:seizure|event|episode|spell|count|total|cluster)",
            note,
        )
        or re.search(
            r"\b(?:seizure|event|episode|spell|count|total|cluster).{0,80}"
            r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\b",
            note,
        )
    )


def _contains_any(text: str, needles: Sequence[str]) -> bool:
    return any(needle in text for needle in needles)


def _candidate_score_for_mode(row: Mapping[str, Any], mode: str) -> Mapping[str, Any]:
    if mode == "raw_change":
        return _score(row, "raw_adjudicator")
    if mode == "gated_change":
        return _score(row, "conservative_adjudicator")
    if mode == "flag_only":
        return _score(row, "deterministic_top")
    raise ValueError(f"Unknown selective-action mode: {mode}")


def _action_for_mode(
    row: Mapping[str, Any],
    mode: str,
    deterministic: Mapping[str, Any],
    candidate: Mapping[str, Any],
) -> bool:
    if mode in {"raw_change", "gated_change"}:
        return _normalized_label(deterministic) != _normalized_label(candidate)
    gate = row.get("conservative_gate") or {}
    raw = _score(row, "raw_adjudicator")
    return bool(
        _normalized_label(deterministic) != _normalized_label(raw)
        or gate.get("fired_gates")
        or row.get("parse_errors")
        or row.get("call_error")
    )


def _selected_evidence_valid(row: Mapping[str, Any]) -> bool:
    decision = row.get("decision_record") or {}
    selected_event_ids = (
        decision.get("selected_event_ids") or decision.get("accepted_event_ids") or []
    )
    if not selected_event_ids:
        return False
    diagnostics = row.get("deterministic_diagnostics") or {}
    events = diagnostics.get("candidate_events") or []
    evidence_by_id = {
        str(event.get("event_id")): str(event.get("evidence") or "")
        for event in events
        if isinstance(event, Mapping)
    }
    return all(evidence_by_id.get(str(event_id), "").strip() for event_id in selected_event_ids)


def _used_fallback_or_abstained(row: Mapping[str, Any], mode: str) -> bool:
    gate = row.get("conservative_gate") or {}
    if mode == "gated_change":
        return bool(gate.get("used_deterministic_fallback"))
    decision = row.get("decision_record") or {}
    return str(decision.get("final_label") or "").lower() in {"", "unknown"}


def _score(row: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    scores = row.get("scores")
    if not isinstance(scores, Mapping):
        return {}
    score = scores.get(key)
    if isinstance(score, Mapping):
        return score
    if key == "conservative_adjudicator":
        fallback = scores.get("adjudicator")
        if isinstance(fallback, Mapping):
            return fallback
    return {}


def _score_label(row: Mapping[str, Any], key: str) -> str | None:
    label = _score(row, key).get("final_label")
    return str(label) if label is not None else None


def _normalized_label(score: Mapping[str, Any]) -> str:
    label = score.get("final_label")
    return str(label).strip().lower() if label is not None else ""


def _rows_for_source_indices(
    rows: Sequence[Mapping[str, Any]],
    source_indices: Sequence[int],
) -> list[Mapping[str, Any]]:
    wanted = set(source_indices)
    return [row for row in rows if int(row["source_row_index"]) in wanted]


def _first_value(rows: Sequence[Mapping[str, Any]], key: str, default: str) -> str:
    for row in rows:
        value = row.get(key)
        if value is not None:
            return str(value)
    return default


def _summary_row(mode: str, summary: Mapping[str, Any]) -> str:
    return (
        f"| {mode} | {_fmt_float(summary['action_rate'])} | "
        f"{summary['changed_or_flagged']} | {summary['wrong_to_correct']} | "
        f"{summary['correct_to_wrong']} | {_fmt_float(summary['changed_label_precision'])} | "
        f"{_fmt_float(summary['changed_label_recall'])} | "
        f"{summary['scorer_equivalent_boundary_churn']} | "
        f"{summary['evidence_valid_changes']} | {summary['fallback_or_abstention']} |"
    )


def _fmt_float(value: Any) -> str:
    if value is None:
        return ""
    return f"{float(value):.4f}"


def _interpret_selective_actions(summary: Mapping[str, Mapping[str, Any]]) -> str:
    raw = summary["raw_change"]
    gated = summary["gated_change"]
    if raw["wrong_to_correct"] == 0 and gated["wrong_to_correct"] == 0:
        return (
            "The saved v0.2 rows do not show prediction-bearing correction signal on this "
            "surface. Treat the adjudicator as diagnostic or revise-only unless hard slices "
            "show stronger selective action."
        )
    if gated["correct_to_wrong"] > gated["wrong_to_correct"]:
        return (
            "The gated final still regresses more deterministic-correct rows than it fixes. "
            "Keep v0.2 out of prediction-bearing promotion and inspect hard-slice behavior."
        )
    return (
        "There is some selective-action signal. Promotion still depends on hard-slice precision, "
        "evidence validity, and regression cost under the predeclared stop rules."
    )


if __name__ == "__main__":
    main()
