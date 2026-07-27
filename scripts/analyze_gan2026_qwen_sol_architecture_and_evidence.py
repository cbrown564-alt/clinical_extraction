from __future__ import annotations

# ruff: noqa: E501
import argparse
import difflib
import json
import re
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.core.evidence import EvidenceGrade, grade_evidence, is_grounded
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import (
    convert_to_categories,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    label_to_frequency_record,
)

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "experiments" / "gan2026_six_model_validation_20260718"
ATTRIBUTION = ROOT / "experiments" / "gan2026_six_model_post_panel_attribution_20260720.json"
COMPARISON = ROOT / "experiments" / "gan2026_six_model_validation_comparison_20260718.json"

ARCHITECTURE_PROTOCOL = (
    "docs/experiments/gan2026/"
    "gan2026_qwen_sol_architecture_interaction_protocol_2026-07-27.md"
)
EVIDENCE_PROTOCOL = (
    "docs/experiments/gan2026/"
    "gan2026_dev750_exact_evidence_and_repair_protocol_2026-07-27.md"
)
ARCHITECTURE_JSON = ROOT / "experiments/gan2026_qwen_sol_architecture_interaction_20260727.json"
EVIDENCE_JSON = ROOT / "experiments/gan2026_dev750_exact_evidence_and_repair_20260727.json"
ARCHITECTURE_REPORT = (
    ROOT
    / "docs/research/gan2026_qwen_sol_architecture_interaction_report_2026-07-27.md"
)
EVIDENCE_REPORT = (
    ROOT / "docs/research/gan2026_dev750_exact_evidence_and_repair_report_2026-07-27.md"
)

MODELS = {
    "gpt41mini": "GPT-4.1-mini",
    "gpt56luna": "GPT-5.6 Luna",
    "gpt56sol": "GPT-5.6 Sol",
    "deepseek_v4_flash": "DeepSeek V4 Flash",
    "qwen36_35b": "Qwen 3.6:35B",
    "gemma4_26b": "Gemma 4 26B",
}
PRIMARY_MODELS = ("qwen36_35b", "gpt56sol")
METHODS = ("llm_only", "llm_with_rules")


def _load_jsonl(path: Path) -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            index = int(row["source_row_index"])
            if index in rows:
                raise ValueError(f"duplicate source_row_index {index} in {path}")
            rows[index] = row
    return rows


def _compact(value: Any) -> str:
    return " ".join(str(value or "").split())


def _md(value: Any) -> str:
    return _compact(value).replace("|", "\\|")


def _clip(value: Any, limit: int = 180) -> str:
    text = _compact(value)
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _note(row: Mapping[str, Any]) -> str:
    try:
        return str(json.loads(str(row.get("prompt_input_json") or "{}")).get("note_text") or "")
    except json.JSONDecodeError:
        return ""


def _purist_category(label: Any) -> str | None:
    text = _compact(label)
    if not text:
        return None
    try:
        monthly = float(label_to_frequency_record(text).monthly_frequency)
    except (TypeError, ValueError):
        return None
    return str(convert_to_categories([monthly], method="purist")[0])


def _label_family(label: Any) -> str:
    text = _compact(label).lower()
    if not text:
        return "missing"
    if "no seizure frequency reference" in text or text == "no_reference":
        return "no_reference"
    if "unknown" in text or "unresolved" in text:
        return "unknown"
    if "seizure free" in text or "seizure-free" in text:
        return "seizure_free"
    if "cluster" in text:
        return "cluster"
    return "frequency"


def _raw_label(row: Mapping[str, Any], method: str) -> str:
    trace = row.get("row_trace") or {}
    record = (trace.get("model_prediction") or {}).get("record") or {}
    if method == "llm_only":
        return _compact(record.get("final_label"))
    return _compact((record.get("selection") or {}).get("final_label"))


def _final_label(row: Mapping[str, Any], method: str) -> str:
    trace = row.get("row_trace") or {}
    if method == "llm_only":
        record = (trace.get("model_prediction") or {}).get("record") or {}
        adapter = trace.get("deterministic_adapter") or {}
        return _compact(adapter.get("after_label") or record.get("final_label"))
    semantic = trace.get("deterministic_semantic") or {}
    selection = ((row.get("structured_record") or {}).get("selection") or {})
    return _compact(semantic.get("after_label") or selection.get("final_label"))


def _selected_evidence(row: Mapping[str, Any], method: str) -> str:
    trace = row.get("row_trace") or {}
    record = (trace.get("model_prediction") or {}).get("record") or {}
    if method == "llm_only":
        return str(record.get("evidence") or "")
    return str((record.get("selection") or {}).get("evidence") or "")


def _semantic_events(row: Mapping[str, Any], method: str) -> list[str]:
    trace = row.get("row_trace") or {}
    key = "deterministic_adapter" if method == "llm_only" else "deterministic_semantic"
    return [_compact(event) for event in (trace.get(key) or {}).get("events") or []]


def _format_events(row: Mapping[str, Any]) -> list[str]:
    trace = row.get("row_trace") or {}
    return [_compact(event) for event in (trace.get("format_repair") or {}).get("events") or []]


def _correct(row: Mapping[str, Any]) -> bool:
    return bool((row.get("comparison") or {}).get("purist_correct"))


def _transition(raw_correct: bool, final_correct: bool) -> str:
    if raw_correct and final_correct:
        return "unchanged_correct"
    if raw_correct and not final_correct:
        return "correct_to_wrong"
    if not raw_correct and final_correct:
        return "wrong_to_correct"
    return "unchanged_wrong"


def _outcome(qwen_correct: bool, sol_correct: bool) -> str:
    if qwen_correct and sol_correct:
        return "both_correct"
    if qwen_correct:
        return "qwen_only_correct"
    if sol_correct:
        return "sol_only_correct"
    return "both_wrong"


def _answer_owner(raw_label: str, final_label: str, semantic_events: Sequence[str]) -> str:
    raw_category = _purist_category(raw_label)
    final_category = _purist_category(final_label)
    if not semantic_events and raw_label == final_label:
        return "model_selection_preserved"
    if raw_category != final_category:
        return "deterministic_prediction_bearing_change"
    if raw_label != final_label:
        return "deterministic_same_category_rendering"
    return "model_selection_preserved"


def _selected_event_evidence(row: Mapping[str, Any]) -> dict[str, Any]:
    record = (row.get("structured_record") or {})
    selection = record.get("selection") or {}
    selected_ids = set(selection.get("selected_event_ids") or [])
    note = _note(row)
    selected = [
        event
        for event in record.get("events") or []
        if str(event.get("event_id")) in selected_ids
    ]
    grades = [grade_evidence(note, str(event.get("evidence") or "")) for event in selected]
    return {
        "selected_event_count": len(selected),
        "selected_event_exact_count": sum(grade == EvidenceGrade.EXACT for grade in grades),
        "selected_event_grounded_count": sum(is_grounded(grade) for grade in grades),
        "all_selected_events_exact": bool(selected)
        and all(grade == EvidenceGrade.EXACT for grade in grades),
        "all_selected_events_grounded": bool(selected)
        and all(is_grounded(grade) for grade in grades),
        "any_selected_event_exact": any(grade == EvidenceGrade.EXACT for grade in grades),
        "any_selected_event_grounded": any(is_grounded(grade) for grade in grades),
        "selected_event_grades": [str(grade) for grade in grades],
    }


def _strip_wrapping_quotes(text: str) -> str:
    stripped = text.strip()
    pairs = (('"', '"'), ("'", "'"), ("“", "”"), ("‘", "’"))
    for left, right in pairs:
        if stripped.startswith(left) and stripped.endswith(right) and len(stripped) >= 2:
            return stripped[1:-1]
    return stripped


def _normalized_copy(text: str) -> str:
    text = text.casefold()
    text = text.replace("‑", "-").replace("–", "-").replace("—", "-")
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _evidence_failure_mechanism(
    note_text: str, evidence: str, grade: EvidenceGrade, final_label: str
) -> str:
    if grade == EvidenceGrade.EXACT:
        return "exact"
    grade_names = {
        EvidenceGrade.REPAIRED_ARTIFACT: "neutral_encoding_artifact",
        EvidenceGrade.REPAIRED_CASE: "case_only_copy_drift",
        EvidenceGrade.REPAIRED_WHITESPACE: "whitespace_only_copy_drift",
        EvidenceGrade.REPAIRED_ELLIPSIS: "bounded_multi_span_ellipsis",
        EvidenceGrade.REPAIRED_SECTION: "section_header_item_join",
        EvidenceGrade.EMPTY: "empty_selection_evidence",
    }
    if grade in grade_names:
        return grade_names[grade]

    stripped = _strip_wrapping_quotes(evidence)
    if stripped != evidence and stripped in note_text:
        return "added_wrapping_quotes"
    if (
        _label_family(final_label) == "no_reference"
        and any(
            marker in evidence.casefold()
            for marker in ("no_reference", "no mention", "no seizure frequency evidence")
        )
    ):
        return "synthesized_absence_statement"

    segments = [
        segment.strip(" \"'“”‘’")
        for segment in re.split(r"(?:\.{3}|…|;\s+)", evidence)
        if segment.strip(" \"'“”‘’")
    ]
    if len(segments) >= 2 and sum(segment in note_text for segment in segments) >= 2:
        return "unrecognized_multi_span_synthesis"

    normalized_note = _normalized_copy(note_text)
    normalized_evidence = _normalized_copy(stripped)
    if normalized_evidence and normalized_evidence in normalized_note:
        return "punctuation_or_unicode_copy_drift"

    match = difflib.SequenceMatcher(
        None, evidence.casefold(), note_text.casefold()
    ).find_longest_match(0, len(evidence), 0, len(note_text))
    coverage = match.size / max(1, len(evidence))
    if coverage >= 0.85:
        return "minor_source_mutation"
    if "..." in evidence or "…" in evidence or len(segments) >= 2:
        return "unverified_multi_span_or_summary"
    return "paraphrase_or_source_synthesis"


def _counts(items: Iterable[str]) -> dict[str, int]:
    return dict(sorted(Counter(items).items()))


def _build_sources() -> tuple[
    dict[str, dict[str, dict[int, dict[str, Any]]]],
    dict[tuple[str, str, int], dict[str, Any]],
]:
    source: dict[str, dict[str, dict[int, dict[str, Any]]]] = {}
    expected: set[int] | None = None
    for slug in MODELS:
        source[slug] = {}
        for method in METHODS:
            path = PANEL / f"{slug}--{method}.jsonl"
            rows = _load_jsonl(path)
            if len(rows) != 750:
                raise ValueError(f"{path} contains {len(rows)} rows, expected 750")
            indices = set(rows)
            if expected is None:
                expected = indices
            elif indices != expected:
                raise ValueError(f"row indices do not align for {path}")
            source[slug][method] = rows

    attribution_doc = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    attribution = {
        (str(row["model_slug"]), str(row["method"]), int(row["source_row_index"])): row
        for row in attribution_doc["rows"]
    }
    if len(attribution) != 9000:
        raise ValueError(f"attribution contains {len(attribution)} unique rows, expected 9000")
    return source, attribution


def build_architecture(
    source: Mapping[str, Mapping[str, Mapping[int, dict[str, Any]]]],
    attribution: Mapping[tuple[str, str, int], dict[str, Any]],
) -> dict[str, Any]:
    indices = sorted(source["qwen36_35b"]["llm_with_rules"])
    rows: list[dict[str, Any]] = []
    for index in indices:
        model_rows: dict[str, Any] = {}
        for slug in PRIMARY_MODELS:
            methods: dict[str, Any] = {}
            for method in METHODS:
                row = source[slug][method][index]
                attr = attribution[(slug, method, index)]
                raw_label = _raw_label(row, method)
                final_label = _final_label(row, method)
                semantic_events = _semantic_events(row, method)
                methods[method] = {
                    "raw_label": raw_label,
                    "raw_purist_category": _purist_category(raw_label),
                    "raw_purist_correct": bool(attr["model_boundary_purist_correct"]),
                    "final_label": final_label,
                    "final_purist_category": (row.get("comparison") or {}).get(
                        "predicted_purist_category"
                    ),
                    "final_purist_correct": _correct(row),
                    "transition": _transition(
                        bool(attr["model_boundary_purist_correct"]), _correct(row)
                    ),
                    "exact_selected_evidence": bool(attr["evidence_valid"]),
                    "first_failure_owner": attr["first_failure_owner"],
                    "clinical_subproblem": attr["clinical_subproblem"],
                    "semantic_events": semantic_events,
                    "format_events": _format_events(row),
                    "answer_owner": _answer_owner(raw_label, final_label, semantic_events),
                    "extracted_event_count": len(
                        (row.get("structured_record") or {}).get("events") or []
                    )
                    if method == "llm_with_rules"
                    else None,
                    "selected_event_count": len(
                        ((row.get("structured_record") or {}).get("selection") or {}).get(
                            "selected_event_ids"
                        )
                        or []
                    )
                    if method == "llm_with_rules"
                    else None,
                }
            model_rows[slug] = methods

        q_final = model_rows["qwen36_35b"]["llm_with_rules"]["final_purist_correct"]
        s_final = model_rows["gpt56sol"]["llm_with_rules"]["final_purist_correct"]
        reference = source["qwen36_35b"]["llm_with_rules"][index]["reference"]
        rows.append(
            {
                "source_row_index": index,
                "gold_label": _compact(reference.get("gold_label")),
                "gold_family": _label_family(reference.get("gold_label")),
                "gold_purist_category": (
                    source["qwen36_35b"]["llm_with_rules"][index].get("comparison") or {}
                ).get("gold_purist_category"),
                "llm_with_rules_outcome": _outcome(q_final, s_final),
                "models": model_rows,
            }
        )

    aggregate: dict[str, Any] = {}
    for slug in PRIMARY_MODELS:
        model_aggregate: dict[str, Any] = {"model": MODELS[slug]}
        for method in METHODS:
            stages = [row["models"][slug][method] for row in rows]
            model_aggregate[method] = {
                "raw_correct": sum(stage["raw_purist_correct"] for stage in stages),
                "final_correct": sum(stage["final_purist_correct"] for stage in stages),
                "transitions": _counts(stage["transition"] for stage in stages),
                "answer_owner": _counts(stage["answer_owner"] for stage in stages),
                "exact_selected_evidence": sum(
                    stage["exact_selected_evidence"] for stage in stages
                ),
            }
        aggregate[slug] = model_aggregate

    outcome_counts = _counts(row["llm_with_rules_outcome"] for row in rows)
    outcome_breakdowns: dict[str, Any] = {}
    for outcome in ("qwen_only_correct", "sol_only_correct", "both_wrong"):
        selected = [row for row in rows if row["llm_with_rules_outcome"] == outcome]
        wrong_slug = "gpt56sol" if outcome == "qwen_only_correct" else "qwen36_35b"
        if outcome == "both_wrong":
            owner_counts = {
                slug: _counts(
                    row["models"][slug]["llm_with_rules"]["first_failure_owner"]
                    for row in selected
                )
                for slug in PRIMARY_MODELS
            }
            subproblem_counts = {
                slug: _counts(
                    row["models"][slug]["llm_with_rules"]["clinical_subproblem"]
                    for row in selected
                )
                for slug in PRIMARY_MODELS
            }
        else:
            owner_counts = _counts(
                row["models"][wrong_slug]["llm_with_rules"]["first_failure_owner"]
                for row in selected
            )
            subproblem_counts = _counts(
                row["models"][wrong_slug]["llm_with_rules"]["clinical_subproblem"]
                for row in selected
            )
        outcome_breakdowns[outcome] = {
            "rows": len(selected),
            "source_row_indices": [row["source_row_index"] for row in selected],
            "gold_family": _counts(row["gold_family"] for row in selected),
            "wrong_model_first_failure_owner": owner_counts,
            "wrong_model_clinical_subproblem": subproblem_counts,
        }

    shared_regressions = []
    for row in rows:
        regressed = [
            slug
            for slug in PRIMARY_MODELS
            if row["models"][slug]["llm_with_rules"]["transition"] == "correct_to_wrong"
        ]
        if regressed:
            shared_regressions.append(
                {
                    "source_row_index": row["source_row_index"],
                    "gold_label": row["gold_label"],
                    "regressed_models": regressed,
                    "qwen_raw_to_final": [
                        row["models"]["qwen36_35b"]["llm_with_rules"]["raw_label"],
                        row["models"]["qwen36_35b"]["llm_with_rules"]["final_label"],
                    ],
                    "sol_raw_to_final": [
                        row["models"]["gpt56sol"]["llm_with_rules"]["raw_label"],
                        row["models"]["gpt56sol"]["llm_with_rules"]["final_label"],
                    ],
                    "qwen_events": row["models"]["qwen36_35b"]["llm_with_rules"][
                        "semantic_events"
                    ],
                    "sol_events": row["models"]["gpt56sol"]["llm_with_rules"][
                        "semantic_events"
                    ],
                }
            )

    return {
        "schema_version": "gan2026.qwen_sol_architecture_interaction.v1",
        "protocol": ARCHITECTURE_PROTOCOL,
        "dataset": "Gan 2026",
        "split": "dev750",
        "split_manifest": "gan2026_split_v1",
        "row_policy": "development_row_level",
        "replay_mode": "saved_outputs_no_call",
        "scorer": "Gan Purist primary; Pragmatic secondary",
        "repair_policy": "retained hybrid_full_stack outputs and row traces",
        "aggregate": aggregate,
        "llm_with_rules_head_to_head": outcome_counts,
        "outcome_breakdowns": outcome_breakdowns,
        "same_event_ledger_raw_correct_to_final_wrong": shared_regressions,
        "rows": rows,
        "claim_boundary": (
            "Development mechanism evidence only. The two methods use different prompts and "
            "representations; test450 is aggregate-only and was not inspected."
        ),
    }


def build_evidence(
    source: Mapping[str, Mapping[str, Mapping[int, dict[str, Any]]]],
    attribution: Mapping[tuple[str, str, int], dict[str, Any]],
) -> dict[str, Any]:
    comparison_doc = json.loads(COMPARISON.read_text(encoding="utf-8"))
    recorded_conditions = {
        str(condition["model_slug"]): condition
        for condition in comparison_doc["conditions"]
        if condition["method"] == "llm_with_rules"
    }
    evidence_rows: list[dict[str, Any]] = []
    summaries: dict[str, Any] = {}
    for slug, model_name in MODELS.items():
        rows = source[slug]["llm_with_rules"]
        model_evidence_rows: list[dict[str, Any]] = []
        for index in sorted(rows):
            row = rows[index]
            attr = attribution[(slug, "llm_with_rules", index)]
            note_text = _note(row)
            evidence = _selected_evidence(row, "llm_with_rules")
            grade = grade_evidence(note_text, evidence)
            if (grade == EvidenceGrade.EXACT) != bool(attr["evidence_valid"]):
                raise ValueError(
                    f"exact-evidence replay disagrees with attribution for {slug} row {index}"
                )
            raw_label = _raw_label(row, "llm_with_rules")
            final_label = _final_label(row, "llm_with_rules")
            events = _semantic_events(row, "llm_with_rules")
            event_evidence = _selected_event_evidence(row)
            parse_errors = [_compact(item) for item in row.get("parse_errors") or []]
            repair_events = [
                item for item in parse_errors if item.startswith("final_label_repaired:")
            ]
            result = {
                "model_slug": slug,
                "model": model_name,
                "source_row_index": index,
                "gold_label": _compact((row.get("reference") or {}).get("gold_label")),
                "raw_label": raw_label,
                "final_label": final_label,
                "raw_purist_correct": bool(attr["model_boundary_purist_correct"]),
                "final_purist_correct": _correct(row),
                "transition": _transition(
                    bool(attr["model_boundary_purist_correct"]), _correct(row)
                ),
                "selected_evidence": evidence,
                "exact_selected_evidence": grade == EvidenceGrade.EXACT,
                "evidence_grade": str(grade),
                "evidence_grounded": is_grounded(grade),
                "failure_mechanism": _evidence_failure_mechanism(
                    note_text, evidence, grade, final_label
                ),
                "answer_owner": _answer_owner(raw_label, final_label, events),
                "semantic_events": events,
                "format_events": _format_events(row),
                "repair_note_count": len(repair_events),
                "has_repair_note": bool(repair_events),
                "first_failure_owner": attr["first_failure_owner"],
                "clinical_subproblem": attr["clinical_subproblem"],
                **event_evidence,
            }
            evidence_rows.append(result)
            model_evidence_rows.append(result)

        exact = [row for row in model_evidence_rows if row["exact_selected_evidence"]]
        nonexact = [row for row in model_evidence_rows if not row["exact_selected_evidence"]]
        summaries[slug] = {
            "model": model_name,
            "rows": len(model_evidence_rows),
            "exact_selected_evidence": len(exact),
            "grounded_selected_evidence": sum(
                row["evidence_grounded"] for row in model_evidence_rows
            ),
            "evidence_grades": _counts(row["evidence_grade"] for row in model_evidence_rows),
            "nonexact_failure_mechanisms": _counts(
                row["failure_mechanism"] for row in nonexact
            ),
            "purist_correct": sum(row["final_purist_correct"] for row in model_evidence_rows),
            "correct_with_exact": sum(row["final_purist_correct"] for row in exact),
            "correct_without_exact": sum(row["final_purist_correct"] for row in nonexact),
            "nonexact_answer_owner": _counts(row["answer_owner"] for row in nonexact),
            "nonexact_transitions": _counts(row["transition"] for row in nonexact),
            "nonexact_any_selected_event_exact": sum(
                row["any_selected_event_exact"] for row in nonexact
            ),
            "nonexact_all_selected_events_exact": sum(
                row["all_selected_events_exact"] for row in nonexact
            ),
            "repair_rows": sum(row["has_repair_note"] for row in model_evidence_rows),
            "repair_events": sum(row["repair_note_count"] for row in model_evidence_rows),
            "repair_events_per_row": _counts(
                str(row["repair_note_count"]) for row in model_evidence_rows
            ),
            "repair_rows_correct": sum(
                row["has_repair_note"] and row["final_purist_correct"]
                for row in model_evidence_rows
            ),
            "repair_rows_exact": sum(
                row["has_repair_note"] and row["exact_selected_evidence"]
                for row in model_evidence_rows
            ),
        }
        recorded = recorded_conditions[slug]
        if summaries[slug]["exact_selected_evidence"] != recorded["evidence_valid"]:
            raise ValueError(f"exact-evidence total disagrees with retained summary for {slug}")
        if summaries[slug]["repair_rows"] != recorded["deterministic_repair_rows"]:
            raise ValueError(f"repair-row total disagrees with retained summary for {slug}")

    return {
        "schema_version": "gan2026.dev750_exact_evidence_and_repair.v1",
        "protocol": EVIDENCE_PROTOCOL,
        "dataset": "Gan 2026",
        "split": "dev750",
        "split_manifest": "gan2026_split_v1",
        "row_policy": "development_row_level",
        "replay_mode": "saved_outputs_no_call",
        "method": "llm_with_rules",
        "comparison_reconciliation": (
            "All six exact-evidence and repair-row totals reproduce the retained "
            "gan2026_six_model_validation_comparison_20260718.json condition summaries."
        ),
        "exact_evidence_definition": (
            "bool(selection.evidence) and selection.evidence in note_text; case-sensitive, "
            "character-for-character contiguous Python substring"
        ),
        "repair_note_definition": (
            "A row counted once when parse_errors contains at least one item beginning "
            "final_label_repaired:. Multiple such events on one row still contribute one "
            "to the retained summary repair_notes field."
        ),
        "summaries": summaries,
        "rows": evidence_rows,
        "claim_boundary": (
            "Exact substring presence is textual provenance, not clinical support. "
            "Development rows only; no test450 row inspection."
        ),
    }


def _format_counts(counts: Mapping[str, int]) -> str:
    return ", ".join(f"`{key}` {value}" for key, value in counts.items()) or "none"


def render_architecture(doc: Mapping[str, Any]) -> str:
    q = doc["aggregate"]["qwen36_35b"]
    s = doc["aggregate"]["gpt56sol"]
    head = doc["llm_with_rules_head_to_head"]
    rows = doc["rows"]
    qwins = doc["outcome_breakdowns"]["qwen_only_correct"]
    swins = doc["outcome_breakdowns"]["sol_only_correct"]
    both_wrong = doc["outcome_breakdowns"]["both_wrong"]

    lines = [
        "# Why Qwen leads GPT-5.6 Sol in the Gan 2026 LLM-with-rules pipeline",
        "",
        "Date: 2026-07-27  ",
        "Status: no-call `dev750` development mechanism report",
        "",
        "## Answer",
        "",
        "The retained evidence does **not** show that the deterministic rule stack is "
        "optimized for Qwen. On the same saved event-ledger output, fixed processing "
        f"rescues {q['llm_with_rules']['transitions'].get('wrong_to_correct', 0)} Qwen "
        f"rows and {s['llm_with_rules']['transitions'].get('wrong_to_correct', 0)} Sol "
        f"rows, while regressing {q['llm_with_rules']['transitions'].get('correct_to_wrong', 0)} "
        f"Qwen rows and {s['llm_with_rules']['transitions'].get('correct_to_wrong', 0)} Sol rows. "
        "The same-output net benefit is therefore larger for Sol, not Qwen.",
        "",
        "The apparent reversal comes from comparing two different model tasks. "
        "`llm_only` asks for one direct final label. `llm_with_rules` asks for an event "
        "ledger plus a selected answer, then applies deterministic processing. Qwen is "
        "weaker on the direct-label task but interacts better with the event-ledger "
        "representation on particular Gan families. In the final event-ledger pipeline, "
        f"Qwen is uniquely correct on {head.get('qwen_only_correct', 0)} rows and Sol is "
        f"uniquely correct on {head.get('sol_only_correct', 0)} rows: the 12-row net "
        "difference exactly explains 667 versus 655.",
        "",
        "This is a development answer, not proof that no validation overfitting exists. "
        "The deterministic policy was developed on Gan validation data, and the two "
        "methods are not a same-prompt or same-raw-output architecture ablation.",
        "",
        "## What was compared",
        "",
        "| Layer | Qwen | Sol | Interpretation |",
        "| --- | ---: | ---: | --- |",
        f"| Direct-label raw model boundary | {q['llm_only']['raw_correct']}/750 | "
        f"{s['llm_only']['raw_correct']}/750 | Scorer-facing raw label before the direct adapter |",
        f"| Direct-label final | {q['llm_only']['final_correct']}/750 | "
        f"{s['llm_only']['final_correct']}/750 | The report's `llm_only` condition |",
        f"| Event-ledger raw model boundary | {q['llm_with_rules']['raw_correct']}/750 | "
        f"{s['llm_with_rules']['raw_correct']}/750 | Model-selected label before fixed processing |",
        f"| Event-ledger final | {q['llm_with_rules']['final_correct']}/750 | "
        f"{s['llm_with_rules']['final_correct']}/750 | The report's `llm_with_rules` condition |",
        "",
        "Raw-boundary accuracy is not a pure clinical-selection measure. Source-near Sol "
        "labels are often Purist-unscorable until canonicalized, while some vague labels "
        "can map to a scorer sentinel. It is retained here to measure transitions, not to "
        "rank the raw models.",
        "",
        "## The headline gain is a model-by-method interaction",
        "",
        "| Model | Direct-label final | Event-ledger final | Difference | Wrong→correct | Correct→wrong |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        f"| Qwen 3.6:35B | {q['llm_only']['final_correct']}/750 | "
        f"{q['llm_with_rules']['final_correct']}/750 | "
        f"+{q['llm_with_rules']['final_correct'] - q['llm_only']['final_correct']} | "
        f"{sum(1 for row in rows if not row['models']['qwen36_35b']['llm_only']['final_purist_correct'] and row['models']['qwen36_35b']['llm_with_rules']['final_purist_correct'])} | "
        f"{sum(1 for row in rows if row['models']['qwen36_35b']['llm_only']['final_purist_correct'] and not row['models']['qwen36_35b']['llm_with_rules']['final_purist_correct'])} |",
        f"| GPT-5.6 Sol | {s['llm_only']['final_correct']}/750 | "
        f"{s['llm_with_rules']['final_correct']}/750 | "
        f"+{s['llm_with_rules']['final_correct'] - s['llm_only']['final_correct']} | "
        f"{sum(1 for row in rows if not row['models']['gpt56sol']['llm_only']['final_purist_correct'] and row['models']['gpt56sol']['llm_with_rules']['final_purist_correct'])} | "
        f"{sum(1 for row in rows if row['models']['gpt56sol']['llm_only']['final_purist_correct'] and not row['models']['gpt56sol']['llm_with_rules']['final_purist_correct'])} |",
        "",
        "Because the prompt, requested schema, and division of work all change, the "
        "102-versus-65 difference cannot be attributed to rules alone.",
        "",
        "## Same-saved-output effect of fixed processing",
        "",
        "| Model and method | Raw correct | Final correct | Wrong→correct | Correct→wrong | Net |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for slug, aggregate in (("qwen36_35b", q), ("gpt56sol", s)):
        for method, label in (
            ("llm_only", "direct-label"),
            ("llm_with_rules", "event-ledger"),
        ):
            stage = aggregate[method]
            transitions = stage["transitions"]
            net = transitions.get("wrong_to_correct", 0) - transitions.get(
                "correct_to_wrong", 0
            )
            lines.append(
                f"| {MODELS[slug]} {label} | {stage['raw_correct']}/750 | "
                f"{stage['final_correct']}/750 | "
                f"{transitions.get('wrong_to_correct', 0)} | "
                f"{transitions.get('correct_to_wrong', 0)} | {net:+d} |"
            )

    lines.extend(
        [
            "",
            "The event-ledger fixed code gives Sol 51 more net scorer rescues than Qwen "
            "(+387 versus +336). That directly contradicts the narrow hypothesis that the "
            "rule stack succeeds because it was tailored to Qwen's output form.",
            "",
            "## Final head-to-head result",
            "",
            "| Outcome | Rows |",
            "| --- | ---: |",
            f"| Both correct | {head.get('both_correct', 0)} |",
            f"| Qwen only correct | {head.get('qwen_only_correct', 0)} |",
            f"| Sol only correct | {head.get('sol_only_correct', 0)} |",
            f"| Both wrong | {head.get('both_wrong', 0)} |",
            "",
            "### Where Qwen's 44 unique wins come from",
            "",
            f"- Gold families: {_format_counts(qwins['gold_family'])}.",
            f"- Sol first-failure owners: {_format_counts(qwins['wrong_model_first_failure_owner'])}.",
            f"- Sol clinical subproblems: {_format_counts(qwins['wrong_model_clinical_subproblem'])}.",
            "",
            "### Where Sol's 32 unique wins come from",
            "",
            f"- Gold families: {_format_counts(swins['gold_family'])}.",
            f"- Qwen first-failure owners: {_format_counts(swins['wrong_model_first_failure_owner'])}.",
            f"- Qwen clinical subproblems: {_format_counts(swins['wrong_model_clinical_subproblem'])}.",
            "",
            "### Shared residual failures",
            "",
            f"Both models are wrong on {both_wrong['rows']} rows. Qwen ownership on those "
            f"rows: {_format_counts(both_wrong['wrong_model_first_failure_owner']['qwen36_35b'])}. "
            f"Sol ownership: {_format_counts(both_wrong['wrong_model_first_failure_owner']['gpt56sol'])}.",
            "",
            "## What is and is not optimized for Qwen",
            "",
            "| Hypothesis | Verdict from `dev750` | Evidence |",
            "| --- | --- | --- |",
            "| Fixed rules preferentially rescue Qwen output | Contradicted | Same-output net rescue is +336 for Qwen and +387 for Sol. |",
            "| Fixed rules overwrite Qwen less often | Partly supported, too small to explain the lead | Seven Qwen and two Sol event-ledger raw-correct answers become wrong; the difference is five rows, not twelve, and several are shared policy defects. |",
            "| Event-ledger prompting suits Qwen better than direct-label prompting | Supported on this development distribution | Qwen's between-method gain is +102 versus +65 for Sol, concentrated in cluster/diary and seizure-free cases in the retained comparison. |",
            "| The architecture is optimized for local models | Unmeasured | Local execution is confounded with model identity; only Qwen and Gemma are local and no matched hosted/local route ablation exists. |",
            "| The architecture is optimized for smaller models | Unmeasured | Parameter count is confounded with model family, training, serving route, and output behavior. |",
            "| Sol is under-optimized | Plausible, not demonstrated | Sol had fewer costly iterations, but no Sol-specific prompt or adapter candidate was predeclared and replayed here. |",
            "| Sol should necessarily remain best after rules because it is best LLM-only | Rejected as an assumption | The methods ask the model to solve different representation and selection tasks; rank preservation is not guaranteed. |",
            "",
            "## Unique failure modes and first decision owner",
            "",
            "The useful optimization target is not “make the rules more Sol-like.” It is "
            "the first stage that loses the correct fact:",
            "",
            "- `llm_clinical_selection`: the event ledger or selected event is already wrong.",
            "- `evidence_selection`: the selected quotation is missing or not an exact source span.",
            "- `deterministic_semantic`: fixed selection or aggregation changes a usable model answer.",
            "- `format_or_schema`: output cannot be retained without structural repair.",
            "",
            "Qwen's distinctive weakness is evidence copying, documented separately. Sol's "
            "event-ledger labels are more often source-near and initially Purist-unscorable, "
            "so deterministic canonicalization produces more same-output rescues. The final "
            "12-row Qwen lead is produced by the balance of 44 versus 32 unique wins, not by "
            "one Qwen-specific rule.",
            "",
            "## Deterministic raw-correct regressions",
            "",
            "These are every event-ledger row where either model is scorer-correct at the "
            "model boundary and wrong after fixed processing. They are the strongest direct "
            "evidence of over-rule on permitted development data.",
            "",
            "| Row | Gold | Regressed model(s) | Qwen raw → final | Sol raw → final |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for item in doc["same_event_ledger_raw_correct_to_final_wrong"]:
        lines.append(
            f"| {item['source_row_index']} | `{_md(item['gold_label'])}` | "
            f"{', '.join(MODELS[slug] for slug in item['regressed_models'])} | "
            f"`{_md(item['qwen_raw_to_final'][0])}` → `{_md(item['qwen_raw_to_final'][1])}` | "
            f"`{_md(item['sol_raw_to_final'][0])}` → `{_md(item['sol_raw_to_final'][1])}` |"
        )

    lines.extend(
        [
            "",
            "The existing row audit records the clinical interpretation of these cases. "
            "Clear shared defects include historical diary counts overriding an explicit "
            "current seizure-free statement and incorrect observation-window denominators. "
            "These are policy defects, not evidence that Qwen was favored.",
            "",
            "## Decision",
            "",
            "Do not assume that a Sol-specific tuning pass will make Sol win, and do not "
            "promote a model-specific rule branch from this result. The next defensible study "
            "is a frozen Sol-focused development candidate that changes one component at a "
            "time: event-ledger prompt wording, clinical selection, or deterministic "
            "aggregation. It must replay the same `dev750` rows, report Qwen as a fixed "
            "regression comparator, and require exact selected evidence on every claimed "
            "changed-row win.",
            "",
            "## Exhaustive final divergence and failure appendix",
            "",
            "The table below contains every row where the final Qwen and Sol "
            "`llm_with_rules` correctness differs or both are wrong. Rows where both are "
            "correct are omitted because they do not explain the ranking or residual errors.",
            "",
            "| Row | Outcome | Gold | Qwen raw → final | Sol raw → final | Qwen owner/subproblem | Sol owner/subproblem |",
            "| ---: | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        if row["llm_with_rules_outcome"] == "both_correct":
            continue
        q_stage = row["models"]["qwen36_35b"]["llm_with_rules"]
        s_stage = row["models"]["gpt56sol"]["llm_with_rules"]
        lines.append(
            f"| {row['source_row_index']} | `{row['llm_with_rules_outcome']}` | "
            f"`{_md(row['gold_label'])}` | `{_md(q_stage['raw_label'])}` → "
            f"`{_md(q_stage['final_label'])}` | `{_md(s_stage['raw_label'])}` → "
            f"`{_md(s_stage['final_label'])}` | `{q_stage['first_failure_owner']}` / "
            f"`{q_stage['clinical_subproblem']}` | `{s_stage['first_failure_owner']}` / "
            f"`{s_stage['clinical_subproblem']}` |"
        )

    lines.extend(
        [
            "",
            "## Reproducibility and limits",
            "",
            f"- Protocol: `{ARCHITECTURE_PROTOCOL}`",
            f"- Machine artifact: `{ARCHITECTURE_JSON.relative_to(ROOT).as_posix()}`",
            "- Inputs: four retained 750-row JSONL files plus the retained post-panel attribution artifact.",
            "- Calls: none; all results are saved-output replay and analysis.",
            "- Scorer: Gan Purist primary; Pragmatic is not used to define the row sets.",
            "- Split: `dev750`; retained identifiers say `validation750`.",
            "- `test450`: aggregate context only; no test row was opened.",
            "- Exact evidence is textual substring provenance, not clinical semantic validation.",
            "",
        ]
    )
    return "\n".join(lines)


def render_evidence(doc: Mapping[str, Any]) -> str:
    summaries = doc["summaries"]
    q = summaries["qwen36_35b"]
    s = summaries["gpt56sol"]
    nonexact_rows = [
        row
        for row in doc["rows"]
        if row["model_slug"] == "qwen36_35b" and not row["exact_selected_evidence"]
    ]

    lines = [
        "# Exact evidence and deterministic repair in the Gan 2026 dev750 panel",
        "",
        "Date: 2026-07-27  ",
        "Status: no-call `dev750` evidence and provenance report",
        "",
        "## Answer",
        "",
        "“Exact evidence” has a narrow implemented meaning: the selected evidence "
        "string must be non-empty and occur as a case-sensitive, character-for-character, "
        "contiguous Python substring of the source note. It does not test whether the quote "
        "is clinically decisive, and it does not inspect all event evidence.",
        "",
        f"On `dev750`, Qwen has {q['exact_selected_evidence']}/750 exact selected "
        f"evidence, compared with {s['exact_selected_evidence']}/750 for Sol. Most of "
        "Qwen's gap is a citation-style behavior: it frequently joins two source spans "
        "with an ellipsis. The repository's later groundedness grader verifies "
        f"{q['grounded_selected_evidence']}/750 Qwen selections after neutral copy repair, "
        f"including {q['evidence_grades'].get('REPAIRED_ELLIPSIS', 0)} bounded-ellipsis "
        "cases. That improves textual provenance but still leaves absent or empty evidence, "
        "and it does not convert a quotation into clinical validation.",
        "",
        "The non-exact Qwen answers are not mostly replaced wholesale by deterministic "
        "rules. The report distinguishes three cases: model selection preserved, "
        "same-category deterministic rendering, and a prediction-bearing category change. "
        f"Across Qwen's {750 - q['exact_selected_evidence']} non-exact rows: "
        f"{_format_counts(q['nonexact_answer_owner'])}.",
        "",
        f"Under the strict scorer-layer definition, fixed code does change the Purist "
        f"category on {q['nonexact_answer_owner'].get('deterministic_prediction_bearing_change', 0)}"
        f"/{750 - q['exact_selected_evidence']} non-exact Qwen rows, a slim majority. "
        "That is not the same as choosing the clinical fact from scratch: "
        f"{q['nonexact_any_selected_event_exact']}/{750 - q['exact_selected_evidence']} "
        "have at least one exactly cited selected event, and "
        f"{q['nonexact_all_selected_events_exact']}/{750 - q['exact_selected_evidence']} "
        "have exact evidence for every selected event.",
        "",
        "“Repair notes” are also narrower than the comparison table suggests. The retained "
        "summary increments once per row if `parse_errors` contains at least one "
        "`final_label_repaired:` entry. It is therefore a count of affected rows, not the "
        "number of events, not parse failures, and not the number of wrong answers. A row "
        "may contain two or three repair events and still contribute one repair note.",
        "",
        "## Exact selected evidence: all six models",
        "",
        "| Model | Exact | Grounded after neutral repair | Absent/empty | Purist correct |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for slug in MODELS:
        summary = summaries[slug]
        absent_empty = summary["evidence_grades"].get(
            "ABSENT", 0
        ) + summary["evidence_grades"].get("EMPTY", 0)
        lines.append(
            f"| {summary['model']} | {summary['exact_selected_evidence']}/750 | "
            f"{summary['grounded_selected_evidence']}/750 | {absent_empty}/750 | "
            f"{summary['purist_correct']}/750 |"
        )

    lines.extend(
        [
            "",
            "### Exact versus grounded",
            "",
            "The original Gan row trace uses only `evidence_is_substring(note, evidence)`: "
            "no lowercasing, whitespace normalization, punctuation normalization, ellipsis "
            "handling, or semantic comparison. The later groundedness grader is a separate "
            "diagnostic. It accepts only source-verifiable neutral repairs such as case, "
            "whitespace, bounded ellipsis, and encoding cleanup.",
            "",
            "Qwen evidence grades:",
            "",
            f"- {_format_counts(q['evidence_grades'])}.",
            "",
            "Sol evidence grades:",
            "",
            f"- {_format_counts(s['evidence_grades'])}.",
            "",
            "Sol's 750/750 exact result means its selected quotation is copied contiguously "
            "on every development row. It does not mean every Sol answer is correct or that "
            "the quote is the decisive clinical evidence.",
            "",
            "## Why Qwen is different",
            "",
            f"Every non-exact Qwen row was classified. Mechanisms: "
            f"{_format_counts(q['nonexact_failure_mechanisms'])}.",
            "",
            "The dominant behavior is selection-level evidence synthesis: Qwen often quotes "
            "two true but non-contiguous note fragments separated by `...`. This fails the "
            "strict contiguous-substring metric even when both ends are found in the note. "
            "Other rows add quotation marks, change punctuation or wording, summarize "
            "absence of evidence, paraphrase the source, or leave the selection evidence empty.",
            "",
            "### Do selected event citations survive?",
            "",
            f"Among the {len(nonexact_rows)} Qwen rows without exact selection evidence, "
            f"{q['nonexact_any_selected_event_exact']} contain at least one selected event "
            f"whose own evidence is an exact source substring, and "
            f"{q['nonexact_all_selected_events_exact']} have exact evidence for every "
            "selected event. This shows why selection-level failure does not always mean the "
            "event ledger is ungrounded. It also shows why the current single Boolean is too "
            "coarse for component attribution.",
            "",
            "## What happens when exact selected evidence is absent",
            "",
            "| Model | Non-exact rows | Final correct | Raw→final transitions | Final answer ownership |",
            "| --- | ---: | ---: | --- | --- |",
            f"| Qwen 3.6:35B | {750 - q['exact_selected_evidence']} | "
            f"{q['correct_without_exact']} | {_format_counts(q['nonexact_transitions'])} | "
            f"{_format_counts(q['nonexact_answer_owner'])} |",
            f"| GPT-5.6 Sol | {750 - s['exact_selected_evidence']} | "
            f"{s['correct_without_exact']} | {_format_counts(s['nonexact_transitions'])} | "
            f"{_format_counts(s['nonexact_answer_owner'])} |",
            "",
            "A `wrong_to_correct` transition means fixed processing changes a raw "
            "scorer-wrong label into the correct Purist category. It does not automatically "
            "mean the deterministic code discovered the clinical fact: the model may already "
            "have exposed the correct event in an exact event-level citation, while the fixed "
            "code only renders or aggregates it. Conversely, `correct_to_wrong` is a direct "
            "deterministic regression.",
            "",
            "## What a repair note means",
            "",
            "Implementation:",
            "",
            "```python",
            "repair_notes = sum(",
            "    any(str(error).startswith(\"final_label_repaired:\") for error in row[\"parse_errors\"])",
            "    for row in rows",
            ")",
            "```",
            "",
            "Consequences:",
            "",
            "- `366 repair notes` in the Sol `test450` report means 366 of 450 rows had at "
            "least one final-label repair entry.",
            "- It does not mean 366 errors, 366 failed parses, 366 semantic overrides, or "
            "366 manual repairs.",
            "- Multiple repair events on one row still count once in the published summary.",
            "- A repair can be harmless canonicalization (`2 months` → `2 month`), a "
            "score-enabling rewrite, or a prediction-bearing clinical change. The summary "
            "field alone does not distinguish them.",
            "",
            "### Development repair accounting",
            "",
            "| Model | Rows with ≥1 repair note | Total repair events | 0 / 1 / 2 / 3 events per row | Correct repair rows | Exact-evidence repair rows |",
            "| --- | ---: | ---: | --- | ---: | ---: |",
        ]
    )
    for slug in MODELS:
        summary = summaries[slug]
        dist = summary["repair_events_per_row"]
        distribution = " / ".join(str(dist.get(str(n), 0)) for n in range(4))
        lines.append(
            f"| {summary['model']} | {summary['repair_rows']} | "
            f"{summary['repair_events']} | {distribution} | "
            f"{summary['repair_rows_correct']} | {summary['repair_rows_exact']} |"
        )

    lines.extend(
        [
            "",
            f"Sol has {s['repair_rows']} affected development rows but "
            f"{s['repair_events']} individual repair events. Qwen has {q['repair_rows']} "
            f"affected rows and {q['repair_events']} events. Sol's higher repair count is "
            "consistent with source-near labels needing canonical rendering; it is not "
            "evidence that Sol is less reliable.",
            "",
            "## Component interpretation",
            "",
            "The current trace records exactness only for the selection citation. For strong "
            "component claims, future artifacts should retain separately:",
            "",
            "1. exact and grounded evidence for every extracted event;",
            "2. exact and grounded evidence for the selected event set;",
            "3. whether the selection citation is one contiguous quote or a verified set of spans;",
            "4. whether fixed code changes only rendering, changes the Purist category, or "
            "selects a different clinical fact; and",
            "5. whether the cited text is clinically decisive, which requires a separate "
            "review rather than substring matching.",
            "",
            "## Decision",
            "",
            "Do not penalize bounded, source-verifiable multi-span Qwen citations as if they "
            "were fabricated, but do not relabel them `exact`. Report both exact and grounded "
            "rates. For any Sol-versus-Qwen architecture promotion claim, require exact or "
            "grounded evidence at the event and selected-operand levels and exclude absent or "
            "empty citations from changed-row wins.",
            "",
            "## Exhaustive Qwen non-exact-evidence appendix",
            "",
            "This table contains all Qwen `llm_with_rules` development rows whose selected "
            "evidence is not a strict exact substring.",
            "",
            "| Row | Grade/mechanism | Gold | Raw → final | Transition / owner | Selected-event evidence | Selected evidence |",
            "| ---: | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in nonexact_rows:
        selected_event_status = (
            f"{row['selected_event_exact_count']}/{row['selected_event_count']} exact; "
            f"{row['selected_event_grounded_count']}/{row['selected_event_count']} grounded"
        )
        lines.append(
            f"| {row['source_row_index']} | `{row['evidence_grade']}` / "
            f"`{row['failure_mechanism']}` | `{_md(row['gold_label'])}` | "
            f"`{_md(row['raw_label'])}` → `{_md(row['final_label'])}` | "
            f"`{row['transition']}` / `{row['answer_owner']}` | "
            f"{selected_event_status} | {_md(_clip(row['selected_evidence'], 150))} |"
        )

    lines.extend(
        [
            "",
            "## Reproducibility and limits",
            "",
            f"- Protocol: `{EVIDENCE_PROTOCOL}`",
            f"- Machine artifact: `{EVIDENCE_JSON.relative_to(ROOT).as_posix()}`",
            "- Inputs: all six retained 750-row `llm_with_rules` JSONL files and the retained post-panel attribution artifact.",
            "- Calls: none; all results are saved-output analysis.",
            "- Split: `dev750`; retained identifiers say `validation750`.",
            "- `test450`: only the published aggregate meaning of the summary field is explained; no test row was opened.",
            "- Exact and grounded evidence establish textual provenance, not clinical support or clinical validity.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_json(doc: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Verify outputs are reproducible")
    args = parser.parse_args(argv)

    source, attribution = _build_sources()
    architecture = build_architecture(source, attribution)
    evidence = build_evidence(source, attribution)
    architecture_text = render_architecture(architecture)
    evidence_text = render_evidence(evidence)

    outputs: list[tuple[Path, str]] = [
        (ARCHITECTURE_JSON, json.dumps(architecture, indent=2, ensure_ascii=False) + "\n"),
        (EVIDENCE_JSON, json.dumps(evidence, indent=2, ensure_ascii=False) + "\n"),
        (ARCHITECTURE_REPORT, architecture_text),
        (EVIDENCE_REPORT, evidence_text),
    ]
    if args.check:
        mismatches = [
            str(path.relative_to(ROOT))
            for path, expected in outputs
            if not path.exists() or path.read_text(encoding="utf-8") != expected
        ]
        if mismatches:
            raise SystemExit("non-reproducible outputs: " + ", ".join(mismatches))
        print("verified: generated architecture and evidence outputs are reproducible")
        return 0

    for path, content in outputs:
        _write_text(content, path)
    print(
        json.dumps(
            {
                "architecture_rows": len(architecture["rows"]),
                "evidence_rows": len(evidence["rows"]),
                "outputs": [str(path.relative_to(ROOT)) for path, _ in outputs],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
