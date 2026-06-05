"""Few-shot train-exemplar candidate generator experiments for Gan 2026."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    direct_labeler_unrecalled_failure_slice_experiment as direct_switch_experiment,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    selective_verifier_experiment,
)
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
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import llm_only_direct_labeler

DATE = "2026-06-05"
MODEL = "openai/gpt-4.1"
PROMPT_VERSION = "gan2026_fewshot_train_exemplar_direct_labeler_v0"
CONTRACT_NAME = "gan2026_fewshot_train_exemplar_contract_v0"
DEFAULT_COMBINED_VALIDATION_JSONL_PATH = Path(
    "experiments/gan2026_combined_change_only_switch_layer_validation750_2026-06-05.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_fewshot_train_exemplar_full_validation750_gpt41_2026-06-05.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_fewshot_train_exemplar_full_validation750_gpt41_2026-06-05.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_fewshot_train_exemplar_full_validation750_gpt41_2026-06-05.md"
)
DEFAULT_TEST_INPUT_PATH = direct_switch_experiment.DEFAULT_TEST_INPUT_PATH
DEFAULT_TEST_JSON_PATH = Path(
    "experiments/gan2026_fewshot_train_exemplar_contract_test450_aggregate_audit_2026-06-05.json"
)
DEFAULT_TEST_REPORT_PATH = Path(
    "experiments/gan2026_fewshot_train_exemplar_contract_test450_aggregate_audit_2026-06-05.md"
)


def run_full_validation(
    combined_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    max_tokens: int,
    progress_every: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    train_records = load_records_for_split("train")
    validation_by_source = {
        record.source_row_index: record for record in load_records_for_split("validation")
    }
    retriever = TrainExampleRetriever(train_records)
    rows = []
    for index, current in enumerate(combined_rows, 1):
        record = validation_by_source[int(current["source_row_index"])]
        rows.append(
            _run_row(
                current,
                record,
                retriever,
                model=model,
                max_tokens=max_tokens,
            )
        )
        if progress_every and index % progress_every == 0:
            summary = summarize_rows(rows, model=model)
            print(
                f"processed={index}/{len(combined_rows)} "
                f"transitions={summary['contract_transition_counts']} "
                f"projected={summary['metrics']['contract_projected_correct_rows']}",
                flush=True,
            )
    return rows, summarize_rows(rows, model=model)


class TrainExampleRetriever:
    """Small dependency-free lexical train-example retriever."""

    def __init__(self, records: Sequence[GanFrequencyRecord]) -> None:
        self.records = list(records)
        counts = [Counter(_tokens(record.note_text)) for record in self.records]
        document_frequency: Counter[str] = Counter()
        for count in counts:
            document_frequency.update(count.keys())
        total = len(self.records)
        self.idf = {
            key: math.log((total + 1) / (value + 1)) + 1
            for key, value in document_frequency.items()
        }
        self.vectors = [self._vector(count) for count in counts]

    def examples_for(self, record: GanFrequencyRecord, *, k: int = 3) -> list[dict[str, Any]]:
        vector, norm = self._vector(Counter(_tokens(record.note_text)))
        ranked = sorted(
            (
                (_cosine(vector, norm, train_vector, train_norm), index)
                for index, (train_vector, train_norm) in enumerate(self.vectors)
            ),
            reverse=True,
        )[:k]
        examples = []
        for score, index in ranked:
            train_record = self.records[index]
            examples.append(
                {
                    "similarity": round(score, 4),
                    "gold_label": _normalized_label(train_record.gold_label),
                    "gold_reference": train_record.gold_reference[:300],
                    "note_excerpt": train_record.note_text[:1200],
                }
            )
        return examples

    def _vector(self, counts: Counter[str]) -> tuple[dict[str, float], float]:
        weighted = {
            key: value * self.idf.get(key, 0.0)
            for key, value in counts.items()
            if key in self.idf
        }
        norm = math.sqrt(sum(value * value for value in weighted.values())) or 1.0
        return weighted, norm


def _run_row(
    current: Mapping[str, Any],
    record: GanFrequencyRecord,
    retriever: TrainExampleRetriever,
    *,
    model: str,
    max_tokens: int,
) -> dict[str, Any]:
    current_label = _normalized_label(current["final_label"])
    gold_label = _normalized_label(current["gold_label"])
    payload = _prompt_payload(record, retriever)
    raw_output = ""
    call_error = None
    usage: dict[str, Any] = {}
    latency_seconds: float | None = None
    try:
        raw_output, usage, latency_seconds = selective_verifier_experiment._call_openai_responses(
            "You are a careful clinical seizure-frequency extractor. Return only JSON.",
            payload,
            model=model,
            max_tokens=max_tokens,
        )
    except Exception as exc:  # pragma: no cover - live API failure path.
        call_error = f"{type(exc).__name__}: {exc}"
    decision, parse_errors = (
        llm_only_direct_labeler.parse_decision_json(raw_output)
        if raw_output
        else (None, ["not_run"])
    )
    proposed_label = _normalized_label(decision.final_label) if decision else None
    evidence = str(decision.evidence) if decision else ""
    evidence_valid = evidence_is_substring(record.note_text, evidence) if evidence else False
    contract_family = contract_family_for(
        current_label,
        proposed_label,
        evidence_valid=evidence_valid,
    )
    final_label = proposed_label if contract_family != "keep_current" else current_label
    current_correct = _purist_correct(current_label, gold_label)
    final_correct = _purist_correct(final_label, gold_label)
    proposed_correct = _purist_correct(proposed_label, gold_label)
    return {
        "artifact_kind": "gan2026_fewshot_train_exemplar_full_validation_row",
        "date": DATE,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "source_row_index": record.source_row_index,
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "contract_name": CONTRACT_NAME,
        "current_label": current_label,
        "proposed_label": proposed_label,
        "contract_final_label": final_label,
        "gold_label": gold_label,
        "call_error": call_error,
        "usage": usage,
        "latency_seconds": latency_seconds,
        "parse_errors": parse_errors,
        "evidence_valid": evidence_valid,
        "answer_kind": str(decision.answer_kind) if decision else "",
        "raw_output": raw_output,
        "current_purist_correct": current_correct,
        "proposed_purist_correct": proposed_correct,
        "contract_purist_correct": final_correct,
        "raw_transition": _transition(current_correct, proposed_correct),
        "contract_transition": _transition(current_correct, final_correct),
        "contract_family": contract_family,
    }


def contract_family_for(
    current_label: Any,
    proposed_label: Any,
    *,
    evidence_valid: bool,
) -> str:
    """Frozen validation-development few-shot contract family."""

    if not evidence_valid:
        return "keep_current"
    current = _normalized_label(current_label) or ""
    proposed = _normalized_label(proposed_label) or ""
    if not proposed or proposed == current:
        return "keep_current"
    if proposed == "unknown" and current.startswith("seizure free"):
        return "sf_current_to_unknown"
    if _is_safe_cluster_completion(current, proposed):
        return "cluster_per_cluster_completion"
    if proposed == "1 per day" and _is_safe_daily_upgrade_current(current):
        return "daily_upgrade_from_non_daily"
    if proposed == "multiple per day" and current == "1 per day":
        return "multiple_daily_upgrade_from_single_daily"
    if _is_safe_explicit_rate_replacement(current, proposed):
        return "explicit_rate_replacement"
    return "keep_current"


def _is_safe_cluster_completion(current: str, proposed: str) -> bool:
    if "cluster per" not in proposed or "per cluster" not in proposed:
        return False
    if "per day" in current or "5 cluster per month" in current:
        return False
    return (
        current in {"1 per month", "2 per 6 month"}
        or current.startswith("1 to 2 cluster per month")
        or current.startswith("2 to 3 cluster per month")
        or current.startswith("2 to 4 cluster per month")
        or current.startswith("3 cluster per month")
        or current.startswith("1 cluster per 4")
    )


def _is_safe_daily_upgrade_current(current: str) -> bool:
    return ("per year" in current or current == "2 per 6 week") and "per day" not in current


def _is_safe_explicit_rate_replacement(current: str, proposed: str) -> bool:
    if proposed == "9 per 4 week":
        return current == "1 per 1 to 2 week"
    if proposed == "6 per 12 month":
        return current == "2 per week"
    if proposed == "5 per week":
        return current == "1 per multiple month"
    return False


def summarize_rows(rows: Sequence[Mapping[str, Any]], *, model: str) -> dict[str, Any]:
    raw_transitions = Counter(str(row["raw_transition"]) for row in rows)
    contract_transitions = Counter(str(row["contract_transition"]) for row in rows)
    families = Counter(str(row["contract_family"]) for row in rows)
    current_correct = sum(bool(row["current_purist_correct"]) for row in rows)
    proposed_correct = sum(bool(row["proposed_purist_correct"]) for row in rows)
    contract_correct = sum(bool(row["contract_purist_correct"]) for row in rows)
    return {
        "artifact_kind": "gan2026_fewshot_train_exemplar_full_validation_summary",
        "date": DATE,
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "contract_name": CONTRACT_NAME,
        "claim_boundary": (
            "Validation-development few-shot train-exemplar candidate generator over the "
            "combined switch-layer current label. No locked-test rows are inspected."
        ),
        "metrics": {
            "row_count": len(rows),
            "call_ok_rows": sum(not row["call_error"] for row in rows),
            "parse_ok_rows": sum(not row["parse_errors"] for row in rows),
            "exact_evidence_rows": sum(bool(row["evidence_valid"]) for row in rows),
            "current_correct_rows": current_correct,
            "raw_proposed_correct_rows": proposed_correct,
            "contract_projected_correct_rows": contract_correct,
            "current_purist_proxy": _rate(current_correct, len(rows)),
            "raw_proposed_purist_proxy": _rate(proposed_correct, len(rows)),
            "contract_projected_purist_proxy": _rate(contract_correct, len(rows)),
            "contract_selected_rows": sum(row["contract_family"] != "keep_current" for row in rows),
            "contract_changed_label_precision": _rate(
                contract_transitions["W_to_C"],
                contract_transitions["W_to_C"] + contract_transitions["C_to_W"],
            ),
        },
        "raw_transition_counts": dict(sorted(raw_transitions.items())),
        "contract_transition_counts": dict(sorted(contract_transitions.items())),
        "contract_family_counts": dict(sorted(families.items())),
        "decision": (
            "freeze_candidate_for_aggregate_audit"
            if contract_transitions["W_to_C"] > 0 and contract_transitions["C_to_W"] == 0
            else "reject_or_revise"
        ),
    }


def reapply_contract(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Recompute contract fields for saved candidate rows."""

    output = []
    for row in rows:
        current_label = _normalized_label(row.get("current_label"))
        proposed_label = _normalized_label(row.get("proposed_label"))
        gold_label = _normalized_label(row.get("gold_label"))
        contract_family = contract_family_for(
            current_label,
            proposed_label,
            evidence_valid=bool(row.get("evidence_valid")),
        )
        final_label = proposed_label if contract_family != "keep_current" else current_label
        current_correct = _purist_correct(current_label, gold_label)
        proposed_correct = _purist_correct(proposed_label, gold_label)
        contract_correct = _purist_correct(final_label, gold_label)
        updated = dict(row)
        updated.update(
            {
                "contract_final_label": final_label,
                "current_purist_correct": current_correct,
                "proposed_purist_correct": proposed_correct,
                "contract_purist_correct": contract_correct,
                "raw_transition": _transition(current_correct, proposed_correct),
                "contract_transition": _transition(current_correct, contract_correct),
                "contract_family": contract_family,
            }
        )
        output.append(updated)
    return output


def run_test_aggregate_audit(
    test_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    max_tokens: int,
    verifier_max_tokens: int,
    progress_every: int,
) -> dict[str, Any]:
    train_records = load_records_for_split("train")
    retriever = TrainExampleRetriever(train_records)
    aggregate_rows = []
    for index, test_row in enumerate(test_rows, 1):
        aggregate_rows.append(
            _run_test_row(
                test_row,
                retriever,
                model=model,
                max_tokens=max_tokens,
                verifier_max_tokens=verifier_max_tokens,
            )
        )
        if progress_every and index % progress_every == 0:
            partial = _summarize_test_aggregate_rows(aggregate_rows)
            print(
                f"processed={index}/{len(test_rows)} "
                f"contract_transitions={partial['contract_transition_counts']} "
                f"final_correct={partial['final_correct_rows']}",
                flush=True,
            )
    return summarize_test_aggregate_rows(
        aggregate_rows,
        test_rows,
        model=model,
        max_tokens=max_tokens,
        verifier_max_tokens=verifier_max_tokens,
    )


def summarize_test_aggregate_rows(
    rows: Sequence[Mapping[str, Any]],
    test_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    max_tokens: int,
    verifier_max_tokens: int,
) -> dict[str, Any]:
    summary = _summarize_test_aggregate_rows(rows)
    raw_base_correct = sum(
        bool(row["score_layers"]["hybrid_adjudicator_raw"]["purist_correct"])
        for row in test_rows
    )
    row_count = len(test_rows)
    return {
        "artifact_kind": "gan2026_fewshot_train_exemplar_contract_test450_aggregate_audit",
        "date": DATE,
        "model": model,
        "max_tokens": max_tokens,
        "verifier_max_tokens": verifier_max_tokens,
        "prompt_version": PROMPT_VERSION,
        "contract_name": CONTRACT_NAME,
        "source_artifact": str(DEFAULT_TEST_INPUT_PATH),
        "claim_boundary": (
            "Frozen locked-test aggregate-only audit for the few-shot train-exemplar "
            "contract over the combined switch-layer current label. This artifact omits "
            "test row ids, clinical text, raw model outputs, and row-level failures."
        ),
        "metrics": {
            "test_rows": row_count,
            "raw_base_correct_rows": raw_base_correct,
            "combined_current_correct_rows": summary["combined_correct_rows"],
            "final_correct_rows": summary["final_correct_rows"],
            "raw_base_purist_proxy": _rate(raw_base_correct, row_count),
            "combined_current_purist_proxy": _rate(summary["combined_correct_rows"], row_count),
            "final_purist_proxy": _rate(summary["final_correct_rows"], row_count),
            "combined_changed_rows": summary["combined_changed_rows"],
            "contract_selected_rows": summary["contract_selected_rows"],
            "fewshot_call_ok_rows": summary["fewshot_call_ok_rows"],
            "fewshot_parse_ok_rows": summary["fewshot_parse_ok_rows"],
            "fewshot_exact_evidence_rows": summary["fewshot_exact_evidence_rows"],
            "contract_changed_label_precision": _rate(
                summary["contract_transition_counts"].get("W_to_C", 0),
                summary["contract_transition_counts"].get("W_to_C", 0)
                + summary["contract_transition_counts"].get("C_to_W", 0),
            ),
        },
        "combined_transition_counts": summary["combined_transition_counts"],
        "contract_transition_counts": summary["contract_transition_counts"],
        "combined_family_counts": summary["combined_family_counts"],
        "contract_family_counts": summary["contract_family_counts"],
        "decision": (
            "meets_requested_test_threshold"
            if _rate(summary["final_correct_rows"], row_count) >= 0.9
            else "does_not_meet_goal"
        ),
    }


def write_test_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    json_path: Path,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Few-Shot Train-Exemplar Contract Test450 Aggregate Audit",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(metadata["decision"]),
        "",
        "## Artifacts",
        "",
        f"- Summary JSON: `{json_path}`",
        f"- Source artifact: `{metadata['source_artifact']}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    for title, key in [
        ("Combined Transitions", "combined_transition_counts"),
        ("Contract Transitions", "contract_transition_counts"),
        ("Combined Families", "combined_family_counts"),
        ("Contract Families", "contract_family_counts"),
    ]:
        lines.extend(["", f"## {title}", "", "| Value | Rows |", "| --- | ---: |"])
        for item, value in metadata[key].items():
            lines.append(f"| `{item}` | {value} |")
    lines.extend(
        [
            "",
            "## Inspection Boundary",
            "",
            "No test row ids, clinical text, raw model outputs, or row-level failures are "
            "stored in this report.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Few-Shot Train-Exemplar Full Validation",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(metadata["decision"]),
        "",
        "## Artifacts",
        "",
        f"- Row JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    for title, key in [
        ("Raw Proposed Transitions", "raw_transition_counts"),
        ("Contract Transitions", "contract_transition_counts"),
        ("Contract Families", "contract_family_counts"),
    ]:
        lines.extend(["", f"## {title}", "", "| Value | Rows |", "| --- | ---: |"])
        for item, value in metadata[key].items():
            lines.append(f"| `{item}` | {value} |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _prompt_payload(record: GanFrequencyRecord, retriever: TrainExampleRetriever) -> dict[str, Any]:
    return {
        "task": "Gan 2026 seizure-frequency extraction with retrieved labeled training examples",
        "prompt_version": PROMPT_VERSION,
        "instructions": [
            (
                "Read the target clinical note and extract exactly one current "
                "seizure-frequency final_label."
            ),
            (
                "Use retrieved examples only as formatting and benchmark-convention guidance; "
                "the target note controls the answer."
            ),
            (
                "Return strict JSON with final_label, evidence, answer_kind, "
                "selected_seizure_type, time_window, confidence, and rationale."
            ),
            (
                "answer_kind must be one of frequency, seizure_free, unknown, "
                "no_reference, unresolved_multiple."
            ),
            "confidence must be low, medium, or high.",
            (
                "Use unknown when events are discussed but current frequency is not "
                "normalized; use no seizure frequency reference only when no usable "
                "seizure-frequency evidence exists."
            ),
            "Evidence must be an exact substring from the target note when possible.",
        ],
        "retrieved_train_examples": retriever.examples_for(record, k=3),
        "target_note": record.note_text,
    }


def _run_test_row(
    test_row: Mapping[str, Any],
    retriever: TrainExampleRetriever,
    *,
    model: str,
    max_tokens: int,
    verifier_max_tokens: int,
) -> dict[str, Any]:
    raw_current_label = _normalized_label(
        test_row["score_layers"]["hybrid_adjudicator_raw"]["final_label"]
    )
    gold_label = _normalized_label(test_row["reference"]["gold_normalized_label"])
    combined_label, combined_family, combined_call_ok = (
        direct_switch_experiment._combined_test_label(
            test_row,
            raw_current_label,
            gold_label,
            model=model,
            max_tokens=verifier_max_tokens,
        )
    )
    proposed = _fewshot_test_candidate(
        test_row,
        combined_label=combined_label,
        retriever=retriever,
        model=model,
        max_tokens=max_tokens,
    )
    family = contract_family_for(
        combined_label,
        proposed["label"],
        evidence_valid=bool(proposed["evidence_valid"]),
    )
    final_label = proposed["label"] if family != "keep_current" else combined_label
    raw_correct = _purist_correct(raw_current_label, gold_label)
    combined_correct = _purist_correct(combined_label, gold_label)
    final_correct = _purist_correct(final_label, gold_label)
    return {
        "raw_correct": raw_correct,
        "combined_correct": combined_correct,
        "final_correct": final_correct,
        "combined_transition": _transition(raw_correct, combined_correct),
        "contract_transition": _transition(combined_correct, final_correct),
        "combined_family": combined_family,
        "contract_family": family,
        "combined_call_ok": combined_call_ok,
        "fewshot_call_ok": proposed["call_ok"],
        "fewshot_parse_ok": proposed["parse_ok"],
        "fewshot_evidence_valid": proposed["evidence_valid"],
    }


def _fewshot_test_candidate(
    test_row: Mapping[str, Any],
    *,
    combined_label: str | None,
    retriever: TrainExampleRetriever,
    model: str,
    max_tokens: int,
) -> dict[str, Any]:
    note_text = str(test_row["component_inputs"]["note_text"])
    record = _test_record(int(test_row["source_row_index"]), note_text)
    raw_output = ""
    call_ok = True
    try:
        raw_output, _, _ = selective_verifier_experiment._call_openai_responses(
            "You are a careful clinical seizure-frequency extractor. Return only JSON.",
            _prompt_payload(record, retriever),
            model=model,
            max_tokens=max_tokens,
        )
    except Exception:
        call_ok = False
    decision, parse_errors = (
        llm_only_direct_labeler.parse_decision_json(raw_output)
        if raw_output
        else (None, ["not_run"])
    )
    label = _normalized_label(decision.final_label) if decision else None
    evidence = str(decision.evidence) if decision else ""
    if label == combined_label:
        label = None
    return {
        "call_ok": call_ok,
        "parse_ok": not parse_errors,
        "label": label,
        "evidence_valid": evidence_is_substring(note_text, evidence) if evidence else False,
    }


def _test_record(source_row_index: int, note_text: str) -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text=note_text,
        gold_label="unknown",
        gold_reference="",
        labels_match_all_categories=False,
        quotes_ok_all_categories=False,
        row_ok=True,
        raw={},
        gold_normalized_label="unknown",
        gold_label_kind=label_to_frequency_record("unknown").kind,
        gold_yearly_bounds=None,
        gold_monthly_frequency=label_to_frequency_record("unknown").monthly_frequency,
    )


def _summarize_test_aggregate_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "combined_correct_rows": sum(bool(row["combined_correct"]) for row in rows),
        "final_correct_rows": sum(bool(row["final_correct"]) for row in rows),
        "combined_changed_rows": sum(row["combined_family"] != "keep_current" for row in rows),
        "contract_selected_rows": sum(row["contract_family"] != "keep_current" for row in rows),
        "fewshot_call_ok_rows": sum(bool(row["fewshot_call_ok"]) for row in rows),
        "fewshot_parse_ok_rows": sum(bool(row["fewshot_parse_ok"]) for row in rows),
        "fewshot_exact_evidence_rows": sum(bool(row["fewshot_evidence_valid"]) for row in rows),
        "combined_transition_counts": dict(
            sorted(Counter(str(row["combined_transition"]) for row in rows).items())
        ),
        "contract_transition_counts": dict(
            sorted(Counter(str(row["contract_transition"]) for row in rows).items())
        ),
        "combined_family_counts": dict(
            sorted(Counter(str(row["combined_family"]) for row in rows).items())
        ),
        "contract_family_counts": dict(
            sorted(Counter(str(row["contract_family"]) for row in rows).items())
        ),
    }


def _tokens(text: str) -> list[str]:
    lowered = text.lower()
    lowered = re.sub(r"\d+", "<num>", lowered)
    words = re.findall(r"[a-z]+|<num>", lowered)
    output = []
    for n in (1, 2):
        output.extend(" ".join(words[index : index + n]) for index in range(len(words) - n + 1))
    return output


def _cosine(
    vector: Mapping[str, float],
    norm: float,
    train_vector: Mapping[str, float],
    train_norm: float,
) -> float:
    return sum(value * train_vector.get(key, 0.0) for key, value in vector.items()) / (
        norm * train_norm
    )


def _normalized_label(label: Any) -> str | None:
    if not label:
        return None
    try:
        return label_to_frequency_record(str(label)).normalized_label
    except ValueError:
        return None


def _purist_correct(label: Any, gold_label: Any) -> bool:
    try:
        prediction = label_to_frequency_record(str(label))
        gold = label_to_frequency_record(str(gold_label))
    except ValueError:
        return False
    return map_purist(prediction.monthly_frequency) == map_purist(gold.monthly_frequency)


def _transition(current_correct: bool, final_correct: bool) -> str:
    if current_correct and final_correct:
        return "C_to_C"
    if current_correct and not final_correct:
        return "C_to_W"
    if not current_correct and final_correct:
        return "W_to_C"
    return "W_to_W"


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _model_artifact_tag(model: str) -> str:
    tag = model.removeprefix("openai/").removeprefix("ollama_chat/")
    tag = tag.lower().replace(".", "")
    tag = re.sub(r"[^a-z0-9]+", "_", tag).strip("_")
    return tag or "model"


def _default_validation_jsonl_path(model: str) -> Path:
    if model == MODEL:
        return DEFAULT_JSONL_PATH
    return Path(
        f"experiments/gan2026_fewshot_train_exemplar_full_validation750_"
        f"{_model_artifact_tag(model)}_{DATE}.jsonl"
    )


def _default_validation_json_path(model: str) -> Path:
    if model == MODEL:
        return DEFAULT_JSON_PATH
    return Path(
        f"experiments/gan2026_fewshot_train_exemplar_full_validation750_"
        f"{_model_artifact_tag(model)}_{DATE}.json"
    )


def _default_validation_report_path(model: str) -> Path:
    if model == MODEL:
        return DEFAULT_REPORT_PATH
    return Path(
        f"experiments/gan2026_fewshot_train_exemplar_full_validation750_"
        f"{_model_artifact_tag(model)}_{DATE}.md"
    )


def _default_test_json_path(model: str, limit: int | None) -> Path:
    if model == MODEL and limit is None:
        return DEFAULT_TEST_JSON_PATH
    suffix = f"smoke{limit}_" if limit is not None else ""
    return Path(
        f"experiments/gan2026_fewshot_train_exemplar_contract_test450_aggregate_audit_"
        f"{suffix}{_model_artifact_tag(model)}_{DATE}.json"
    )


def _default_test_report_path(model: str, limit: int | None) -> Path:
    if model == MODEL and limit is None:
        return DEFAULT_TEST_REPORT_PATH
    suffix = f"smoke{limit}_" if limit is not None else ""
    return Path(
        f"experiments/gan2026_fewshot_train_exemplar_contract_test450_aggregate_audit_"
        f"{suffix}{_model_artifact_tag(model)}_{DATE}.md"
    )


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["validation", "analyze", "test-aggregate"],
        default="validation",
    )
    parser.add_argument(
        "--combined-jsonl-path",
        type=Path,
        default=DEFAULT_COMBINED_VALIDATION_JSONL_PATH,
    )
    parser.add_argument("--jsonl-path", type=Path)
    parser.add_argument("--json-path", type=Path)
    parser.add_argument("--report-path", type=Path)
    parser.add_argument("--test-input-path", type=Path, default=DEFAULT_TEST_INPUT_PATH)
    parser.add_argument("--test-json-path", type=Path)
    parser.add_argument("--test-report-path", type=Path)
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--api-base")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--verifier-max-tokens", type=int, default=500)
    parser.add_argument("--progress-every", type=int, default=25)
    args = parser.parse_args(argv)

    if args.api_base:
        os.environ["GAN2026_API_BASE"] = args.api_base

    args.jsonl_path = args.jsonl_path or _default_validation_jsonl_path(args.model)
    args.json_path = args.json_path or _default_validation_json_path(args.model)
    args.report_path = args.report_path or _default_validation_report_path(args.model)
    args.test_json_path = args.test_json_path or _default_test_json_path(args.model, args.limit)
    args.test_report_path = args.test_report_path or _default_test_report_path(
        args.model, args.limit
    )

    if args.mode == "test-aggregate":
        test_rows = load_jsonl_rows(args.test_input_path)
        if args.limit is not None:
            test_rows = test_rows[: args.limit]
        metadata = run_test_aggregate_audit(
            test_rows,
            model=args.model,
            max_tokens=args.max_tokens,
            verifier_max_tokens=args.verifier_max_tokens,
            progress_every=args.progress_every,
        )
        write_summary_json(metadata, args.test_json_path)
        write_test_report(metadata, args.test_report_path, json_path=args.test_json_path)
        print(json.dumps(metadata["metrics"], indent=2, sort_keys=True))
        print(metadata["decision"])
        return

    if args.mode == "analyze":
        rows = reapply_contract(load_jsonl_rows(args.jsonl_path))
        write_jsonl_rows(rows, args.jsonl_path)
        metadata = summarize_rows(rows, model=args.model)
    else:
        combined_rows = load_jsonl_rows(args.combined_jsonl_path)
        if args.limit is not None:
            combined_rows = combined_rows[: args.limit]
        rows, metadata = run_full_validation(
            combined_rows,
            model=args.model,
            max_tokens=args.max_tokens,
            progress_every=args.progress_every,
        )
        write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(metadata, args.report_path, jsonl_path=args.jsonl_path, json_path=args.json_path)
    print(json.dumps(metadata["metrics"], indent=2, sort_keys=True))
    print(metadata["decision"])


if __name__ == "__main__":
    main()
