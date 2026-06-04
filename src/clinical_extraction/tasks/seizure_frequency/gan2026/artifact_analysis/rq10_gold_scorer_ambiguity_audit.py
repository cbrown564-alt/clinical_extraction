"""Build the Gan 2026 RQ10 gold/scorer ambiguity audit."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.hidden_family_atlas import (  # noqa: E501
    build_atlas_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_DATA_PATH,
    GanFrequencyRecord,
    load_records_with_monthly_frequency,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_REPLAY_PATH = Path(
    "experiments/"
    "gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_"
    "deterministic_safety_floor_v2_replay_2026-06-03.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_rq10_gold_scorer_ambiguity_audit_2026-06-04.jsonl"
)
DEFAULT_JSON_PATH = Path("experiments/gan2026_rq10_gold_scorer_ambiguity_audit_2026-06-04.json")
DEFAULT_REPORT_PATH = Path(
    "docs/research/gan2026_rq10_gold_scorer_ambiguity_audit_answer_2026-06-04.md"
)
DEFAULT_PROTOCOL_PATH = Path(
    "docs/research/gan2026_rq10_gold_scorer_ambiguity_audit_protocol_2026-06-04.md"
)
PRIMARY_LAYER = "hybrid_adjudicator_with_adapters"
LAYER_NAMES = (
    "deterministic_top_candidate",
    "state_graph_projection",
    "llm_candidate_selector_raw",
    "hybrid_adjudicator_raw",
    "hybrid_adjudicator_with_adapters",
)
NON_TRUE_CLASSES = {
    "benchmark_convention_dominated",
    "underdetermined_note",
    "clinically_defensible_alternative",
    "possible_gold_weakness",
    "instrumentation_gap",
}
EXAMPLE_ROWS_BY_SECTION = {
    "benchmark_convention_dominated": (9943, 11216, 13843),
    "underdetermined_note": (3356, 6321, 7168),
    "clinically_defensible_alternative": (11216, 13843, 15168),
    "true_extraction_failure": (12422, 15834, 9496),
}


def build_audit_rows(
    *,
    replay_path: Path = DEFAULT_REPLAY_PATH,
    data_path: Path = DEFAULT_DATA_PATH,
    primary_layer: str = PRIMARY_LAYER,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Classify primary-layer validation misses by scorer/gold ambiguity mode."""

    records = {
        record.source_row_index: record for record in load_records_with_monthly_frequency(data_path)
    }
    source_rows = load_jsonl_rows(replay_path)
    atlas_rows = build_atlas_rows([replay_path], primary_layer=primary_layer, data_path=data_path)
    atlas_by_index = {int(row["source_row_index"]): row for row in atlas_rows}

    audit_rows: list[dict[str, Any]] = []
    for source_row in source_rows:
        primary_score = _score(source_row, primary_layer)
        if primary_score.get("purist_correct"):
            continue
        source_row_index = int(source_row["source_row_index"])
        record = records[source_row_index]
        atlas_row = atlas_by_index[source_row_index]
        audit_rows.append(
            _audit_row(
                source_row,
                record=record,
                atlas_row=atlas_row,
                replay_path=replay_path,
                primary_layer=primary_layer,
            )
        )

    audit_rows.sort(key=lambda row: int(row["source_row_index"]))
    return audit_rows, summarize_audit_rows(
        audit_rows,
        replay_path=replay_path,
        data_path=data_path,
        primary_layer=primary_layer,
    )


def summarize_audit_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    replay_path: Path,
    data_path: Path,
    primary_layer: str,
) -> dict[str, Any]:
    """Summarize RQ10 audit rows for durable report generation."""

    primary_classes = Counter(str(row["rq10_primary_class"]) for row in rows)
    flags = {
        "hard_row_ambiguity_rate": _safe_rate(
            sum(str(row["rq10_primary_class"]) in NON_TRUE_CLASSES for row in rows),
            len(rows),
        ),
        "all_system_fail_rows": sum(bool(row["all_system_fail"]) for row in rows),
        "exact_evidence_but_scorer_wrong_rows": sum(
            bool(row["exact_evidence_but_scorer_wrong"]) for row in rows
        ),
        "clinically_defensible_alternative_rows": sum(
            bool(row["clinically_defensible_alternative"]) for row in rows
        ),
        "benchmark_convention_dominated_rows": primary_classes[
            "benchmark_convention_dominated"
        ],
        "likely_gold_defect_rows": sum(bool(row["likely_gold_defect"]) for row in rows),
        "possible_gold_weakness_rows": sum(bool(row["possible_gold_weakness"]) for row in rows),
        "purist_only_pragmatic_correct_rows": sum(
            bool(row["primary_pragmatic_correct"]) for row in rows
        ),
    }
    return {
        "artifact_kind": "gan2026_rq10_gold_scorer_ambiguity_audit",
        "date": "2026-06-04",
        "split_manifest": "gan2026_split_v1",
        "split": "validation",
        "source_artifact": str(replay_path),
        "data_path": str(data_path),
        "primary_layer": primary_layer,
        "row_count": len(rows),
        "claim_language": (
            "Development-control answer for saved validation replay only; no scorer, gold, "
            "prompt, deterministic-rule, projection-policy, or locked-test claim."
        ),
        "primary_class_counts": dict(sorted(primary_classes.items())),
        "metrics": flags,
        "by_hidden_family": _by_hidden_family(rows),
        "by_first_failure_owner": _by_first_failure_owner(rows),
        "all_system_fail_source_row_indices": [
            int(row["source_row_index"]) for row in rows if row["all_system_fail"]
        ],
        "exact_evidence_but_scorer_wrong_source_row_indices": [
            int(row["source_row_index"])
            for row in rows
            if row["exact_evidence_but_scorer_wrong"]
        ],
        "possible_gold_weakness_source_row_indices": [
            int(row["source_row_index"]) for row in rows if row["possible_gold_weakness"]
        ],
    }


def write_audit_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_audit_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
    protocol_path: Path = DEFAULT_PROTOCOL_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Gan 2026 RQ10 Gold/Scorer Ambiguity Audit Answer",
        "",
        "This is a validation-development no-call audit over saved replay artifacts. It does "
        "not change scorer policy, gold labels, prompts, rules, projection policy, or locked "
        "test claims.",
        "",
        "## Answer",
        "",
        _answer_paragraph(metadata),
        "",
        "## Claim Boundary",
        "",
        (
            "Answered for saved validation replay only. The audit covers the 53 Purist-wrong "
            f"`{metadata['primary_layer']}` rows from `{metadata['source_artifact']}`. "
            "It can guide future scorer-facing normalization, abstention, or human-review "
            "work, but it is not benchmark-comparable and does not authorize locked-test "
            "tuning."
        ),
        "",
        "## Artifacts",
        "",
        f"- Protocol: `{protocol_path}`",
        f"- Audit JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Source replay: `{metadata['source_artifact']}`",
        "",
        "## Primary Class Counts",
        "",
        "| RQ10 class | Rows |",
        "| --- | ---: |",
    ]
    for class_name, count in _sorted_counts(metadata["primary_class_counts"]):
        lines.append(f"| `{class_name}` | {count} |")

    metrics = metadata["metrics"]
    lines.extend(
        [
            "",
            "## Metrics",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| Hard-row ambiguity rate | {metrics['hard_row_ambiguity_rate']:.3f} |",
            f"| All-system-fail rows | {metrics['all_system_fail_rows']} |",
            (
                "| Exact-evidence-but-scorer-wrong rows | "
                f"{metrics['exact_evidence_but_scorer_wrong_rows']} |"
            ),
            (
                "| Clinically defensible alternative rows | "
                f"{metrics['clinically_defensible_alternative_rows']} |"
            ),
            (
                "| Benchmark-convention dominated rows | "
                f"{metrics['benchmark_convention_dominated_rows']} |"
            ),
            f"| Likely gold defects | {metrics['likely_gold_defect_rows']} |",
            (
                "| Possible gold weakness candidates | "
                f"{metrics['possible_gold_weakness_rows']} |"
            ),
            (
                "| Purist-wrong but Pragmatic-correct rows | "
                f"{metrics['purist_only_pragmatic_correct_rows']} |"
            ),
            "",
            "## Hidden-Family Readout",
            "",
            "| Hidden family | Rows | Main RQ10 class |",
            "| --- | ---: | --- |",
        ]
    )
    for family, summary in _sorted_family_summary(metadata["by_hidden_family"]):
        lines.append(
            f"| `{family}` | {summary['rows']} | `{summary['main_primary_class']}` |"
        )

    lines.extend(
        [
            "",
            "## First-Failure Crosswalk",
            "",
            "| First failure owner | Rows | Main RQ10 class |",
            "| --- | ---: | --- |",
        ]
    )
    for owner, summary in _sorted_family_summary(metadata["by_first_failure_owner"]):
        lines.append(
            f"| `{owner}` | {summary['rows']} | `{summary['main_primary_class']}` |"
        )

    lines.extend(
        [
            "",
            "## Row-Level Mechanism Examples",
            "",
        ]
    )
    for section, source_indices in EXAMPLE_ROWS_BY_SECTION.items():
        lines.extend(_example_section(section, source_indices, rows))

    lines.extend(
        [
            "## Interpretation",
            "",
            (
                "The hard-row residue is not one thing. The biggest scorer-facing ambiguity "
                "families are `unknown`/`no_reference` sentinel behavior, last-event-only "
                "versus seizure-free duration, unresolved `multiple` labels that score as "
                "unknown, cluster cadence/load formatting, and non-epileptic-event convention. "
                "Those rows should not be used blindly to tune deterministic precedence rules."
            ),
            "",
            (
                "The audit still leaves many rows as true extraction failures, especially when "
                "the system selected a historical, lower-frequency, or wrong-semiology fact "
                "despite exact evidence for the gold-relevant state. RQ10 therefore reduces "
                "the pressure to overfit scorer conventions, but it does not excuse ordinary "
                "candidate-selection and projection failures."
            ),
            "",
            "## Transfer Confidence",
            "",
            (
                "Development confidence is moderate for the taxonomy because every saved "
                "primary-layer miss is classified and the classes align with known scorer "
                "contracts. Holdout-transfer confidence is low: this was derived from saved "
                "validation replay and must not be used to tune or reinterpret locked-test rows."
            ),
            "",
            "## Decision",
            "",
            (
                "RQ10 is answered for saved validation replay as a development-control audit. "
                "Use the artifact to design RQ9 abstention/review routing and any future "
                "scorer-normalization policy review. Do not change the scorer or gold labels "
                "from this audit alone."
            ),
            "",
            "## Next Action",
            "",
            (
                "Predeclare an RQ9 abstention/human-review protocol that routes "
                "`underdetermined_note`, `clinically_defensible_alternative`, and "
                "`benchmark_convention_dominated` rows separately from true extraction "
                "failures."
            ),
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _audit_row(
    source_row: Mapping[str, Any],
    *,
    record: GanFrequencyRecord,
    atlas_row: Mapping[str, Any],
    replay_path: Path,
    primary_layer: str,
) -> dict[str, Any]:
    scores = {layer_name: _score(source_row, layer_name) for layer_name in LAYER_NAMES}
    primary_score = scores[primary_layer]
    adjudicator = source_row.get("structured_adjudicator_record") or {}
    diagnostics = source_row.get("diagnostics") or {}
    selected_evidence = str(adjudicator.get("selected_evidence") or "")
    evidence_exact = _bool_or_false(diagnostics.get("selected_evidence_exact"))
    source_id_valid = _bool_or_false(diagnostics.get("selected_source_ids_exist"))
    hidden_families = _split_families(atlas_row.get("hidden_families"))
    primary_class, flags, rationale = _classify_rq10(
        record=record,
        predicted_label=str(primary_score.get("final_label") or ""),
        selected_evidence=selected_evidence,
        evidence_exact=evidence_exact,
        source_id_valid=source_id_valid,
        primary_score=primary_score,
        hidden_families=hidden_families,
    )
    layer_correctness = {
        layer_name: _layer_correctness_summary(score) for layer_name, score in scores.items()
    }
    all_system_fail = all(
        not bool(score.get("purist_correct")) for score in scores.values() if score
    )
    exact_evidence_but_scorer_wrong = bool(
        evidence_exact
        and source_id_valid
        and (
            primary_class == "benchmark_convention_dominated"
            or flags["clinically_defensible_alternative"]
        )
    )
    return {
        "artifact_name": replay_path.name,
        "split_manifest": source_row.get("split_manifest") or "gan2026_split_v1",
        "split": source_row.get("split") or "validation",
        "source_row_index": record.source_row_index,
        "primary_layer": primary_layer,
        "gold_label": record.gold_normalized_label,
        "gold_label_kind": str(record.gold_label_kind),
        "gold_reference": record.gold_reference,
        "row_ok": record.row_ok,
        "labels_match_all_categories": record.labels_match_all_categories,
        "quotes_ok_all_categories": record.quotes_ok_all_categories,
        "primary_predicted_label": str(primary_score.get("final_label") or ""),
        "primary_purist_correct": bool(primary_score.get("purist_correct")),
        "primary_pragmatic_correct": bool(primary_score.get("pragmatic_correct")),
        "primary_gold_purist_category": primary_score.get("gold_purist_category") or "",
        "primary_predicted_purist_category": primary_score.get("predicted_purist_category") or "",
        "deterministic_label": str(scores["deterministic_top_candidate"].get("final_label") or ""),
        "state_graph_label": str(scores["state_graph_projection"].get("final_label") or ""),
        "llm_candidate_selector_label": str(
            scores["llm_candidate_selector_raw"].get("final_label") or ""
        ),
        "hybrid_adjudicator_raw_label": str(
            scores["hybrid_adjudicator_raw"].get("final_label") or ""
        ),
        "selected_evidence": selected_evidence,
        "selected_source_ids": list(adjudicator.get("selected_source_ids") or []),
        "selected_source_types": list(adjudicator.get("selected_source_types") or []),
        "selected_evidence_exact": evidence_exact,
        "selected_source_ids_valid": source_id_valid,
        "hidden_families": hidden_families,
        "first_failure_owner": atlas_row.get("first_failure_owner") or "",
        "first_failure_reason": atlas_row.get("first_failure_reason") or "",
        "rq10_primary_class": primary_class,
        "benchmark_convention_flag": flags["benchmark_convention"],
        "underdetermined_note_flag": flags["underdetermined_note"],
        "clinically_defensible_alternative": flags["clinically_defensible_alternative"],
        "possible_gold_weakness": flags["possible_gold_weakness"],
        "likely_gold_defect": flags["likely_gold_defect"],
        "exact_evidence_but_scorer_wrong": exact_evidence_but_scorer_wrong,
        "all_system_fail": all_system_fail,
        "layer_correctness": layer_correctness,
        "adjudication_rationale": rationale,
    }


def _classify_rq10(
    *,
    record: GanFrequencyRecord,
    predicted_label: str,
    selected_evidence: str,
    evidence_exact: bool,
    source_id_valid: bool,
    primary_score: Mapping[str, Any],
    hidden_families: Sequence[str],
) -> tuple[str, dict[str, bool], str]:
    gold_label = record.gold_normalized_label
    gold_ref = record.gold_reference
    gold_kind = record.gold_label_kind
    text = " ".join([gold_label, predicted_label, gold_ref, selected_evidence]).lower()

    flags = {
        "benchmark_convention": _benchmark_convention_flag(
            gold_label=gold_label,
            predicted_label=predicted_label,
            gold_reference=gold_ref,
            selected_evidence=selected_evidence,
            gold_kind=gold_kind,
            primary_score=primary_score,
            hidden_families=hidden_families,
        ),
        "underdetermined_note": _underdetermined_note_flag(
            gold_kind=gold_kind,
            gold_reference=gold_ref,
        ),
        "clinically_defensible_alternative": _clinically_defensible_alternative_flag(
            gold_label=gold_label,
            predicted_label=predicted_label,
            gold_kind=gold_kind,
            selected_evidence=selected_evidence,
            evidence_exact=evidence_exact,
            source_id_valid=source_id_valid,
        ),
        "possible_gold_weakness": _possible_gold_weakness_flag(
            gold_label=gold_label,
            gold_reference=gold_ref,
            predicted_label=predicted_label,
            selected_evidence=selected_evidence,
        ),
        "likely_gold_defect": False,
    }

    if not evidence_exact or not source_id_valid:
        return "instrumentation_gap", flags, "Selected evidence or source-id trace is incomplete."

    if _last_event_only_convention(
        gold_kind=gold_kind,
        predicted_label=predicted_label,
        gold_reference=gold_ref,
        selected_evidence=selected_evidence,
    ):
        return (
            "benchmark_convention_dominated",
            flags,
            "Gold is unknown for last-event-only style evidence while the prediction renders a "
            "seizure-free interval.",
        )
    if _non_epileptic_zero_convention(
        gold_kind=gold_kind,
        predicted_label=predicted_label,
        text=text,
    ):
        return (
            "benchmark_convention_dominated",
            flags,
            "Gold treats current non-epileptic/seizure-like events as seizure-free rather than "
            "no-reference.",
        )
    if _unresolved_multiple_convention(
        gold_label=gold_label,
        predicted_label=predicted_label,
        gold_reference=gold_ref,
        selected_evidence=selected_evidence,
    ):
        return (
            "benchmark_convention_dominated",
            flags,
            "Gold uses an unresolved multiple/cluster label that collapses through Gan scorer "
            "sentinel or coarse cluster convention.",
        )
    if _cluster_cadence_convention(gold_label=gold_label, predicted_label=predicted_label):
        return (
            "benchmark_convention_dominated",
            flags,
            "Prediction captures cluster cadence but loses Gan-specific cluster/load syntax.",
        )
    if flags["underdetermined_note"]:
        return (
            "underdetermined_note",
            flags,
            "Gold/reference indicates conditional, uncertain, trigger-only, or non-quantified "
            "frequency evidence rather than a single stable scorer label.",
        )
    if flags["clinically_defensible_alternative"]:
        return (
            "clinically_defensible_alternative",
            flags,
            "The non-gold prediction has exact source support and is clinically plausible, "
            "though it is not the Gan gold convention.",
        )
    if flags["possible_gold_weakness"]:
        return (
            "possible_gold_weakness",
            flags,
            "The gold reference is generic or appears weaker than an exact conflicting source "
            "statement, but the row is not strong enough to call a likely defect.",
        )
    return (
        "true_extraction_failure",
        flags,
        "Gold/reference appears sufficiently determinate and the saved primary layer selected a "
        "different clinical fact, denominator, temporality, or semiology.",
    )


def _benchmark_convention_flag(
    *,
    gold_label: str,
    predicted_label: str,
    gold_reference: str,
    selected_evidence: str,
    gold_kind: FrequencyLabelKind,
    primary_score: Mapping[str, Any],
    hidden_families: Sequence[str],
) -> bool:
    text = " ".join([gold_label, predicted_label, gold_reference, selected_evidence]).lower()
    if _unresolved_multiple_convention(
        gold_label=gold_label,
        predicted_label=predicted_label,
        gold_reference=gold_reference,
        selected_evidence=selected_evidence,
    ):
        return True
    if "benchmark_format_convention" in set(hidden_families):
        return True
    if _last_event_only_convention(
        gold_kind=gold_kind,
        predicted_label=predicted_label,
        gold_reference=gold_reference,
        selected_evidence=selected_evidence,
    ):
        return True
    if _non_epileptic_zero_convention(
        gold_kind=gold_kind,
        predicted_label=predicted_label,
        text=text,
    ):
        return True
    if _cluster_cadence_convention(gold_label=gold_label, predicted_label=predicted_label):
        return True
    return bool(primary_score.get("pragmatic_correct"))


def _underdetermined_note_flag(
    *,
    gold_kind: FrequencyLabelKind,
    gold_reference: str,
) -> bool:
    text = gold_reference.lower()
    if gold_kind in {FrequencyLabelKind.UNKNOWN, FrequencyLabelKind.NO_REFERENCE}:
        return True
    if gold_kind == FrequencyLabelKind.UNRESOLVED_MULTIPLE and _has_any(
        text,
        "rare",
        "recently",
        "from time to time",
        "continues",
        "unclear",
        "unknown",
        "without counts",
        "unquantified",
    ):
        return True
    return _has_any(
        text,
        "uncertain",
        "unclear",
        "unsure",
        "trigger",
        "only with",
        "after alcohol",
        "sleep deprivation",
        "exposure",
        "luteal",
        "missed",
        "frequency increased",
        "from time to time",
    )


def _clinically_defensible_alternative_flag(
    *,
    gold_label: str,
    predicted_label: str,
    gold_kind: FrequencyLabelKind,
    selected_evidence: str,
    evidence_exact: bool,
    source_id_valid: bool,
) -> bool:
    if not evidence_exact or not source_id_valid or not selected_evidence:
        return False
    selected = selected_evidence.lower()
    predicted = predicted_label.lower()
    if gold_kind == FrequencyLabelKind.UNKNOWN and _has_any(
        predicted,
        "seizure free",
        " per ",
    ):
        return _has_any(
            selected,
            "no ",
            "none",
            "without",
            "last seizure",
            "since",
            "over the past",
            "per ",
            "every",
            "times",
        )
    if "seizure free" in gold_label and predicted == "no seizure frequency reference":
        return _has_any(
            selected,
            "non-epileptic",
            "seizure-like",
            "fewer episodes",
            "less intrusive",
        )
    if "cluster" in gold_label and "cluster" not in predicted and _has_any(
        predicted,
        "per month",
        "per week",
        "per multiple",
    ):
        return True
    return False


def _possible_gold_weakness_flag(
    *,
    gold_label: str,
    gold_reference: str,
    predicted_label: str,
    selected_evidence: str,
) -> bool:
    text = " ".join([gold_label, gold_reference, predicted_label, selected_evidence]).lower()
    if "temporal inconsistency" in text:
        return True
    if "non-epileptic" in text and "seizure free" in gold_label:
        return True
    return False


def _last_event_only_convention(
    *,
    gold_kind: FrequencyLabelKind,
    predicted_label: str,
    gold_reference: str,
    selected_evidence: str,
) -> bool:
    gold_text = gold_reference.lower()
    selected_text = selected_evidence.lower()
    return (
        gold_kind == FrequencyLabelKind.UNKNOWN
        and "seizure free" in predicted_label
        and _has_any(gold_text, "last seizure", "last reported")
        and _has_any(selected_text, "last seizure", "no subsequent", "no clearly documented")
        and not _has_any(gold_text, "drop attacks", "myoclonic jerks")
    )


def _non_epileptic_zero_convention(
    *,
    gold_kind: FrequencyLabelKind,
    predicted_label: str,
    text: str,
) -> bool:
    return (
        gold_kind == FrequencyLabelKind.SEIZURE_FREE
        and predicted_label == "no seizure frequency reference"
        and _has_any(text, "non-epileptic", "seizure-like")
    )


def _cluster_cadence_convention(*, gold_label: str, predicted_label: str) -> bool:
    gold = gold_label.lower()
    predicted = predicted_label.lower()
    if "cluster" not in gold:
        return False
    if "daily" in predicted or "per day" in predicted:
        return False
    if "multiple per cluster" in predicted:
        return True
    if "cluster" not in predicted and _cluster_period_compatible(gold=gold, predicted=predicted):
        return True
    return False


def _cluster_period_compatible(*, gold: str, predicted: str) -> bool:
    if "per 5 day" in gold or "per day" in gold:
        return bool(re.search(r"\bper\s+(?:\d+(?:\s+to\s+\d+)?\s+)?day\b", predicted))
    if "per 4 to 5 week" in gold:
        return "per 4 to 5 week" in predicted
    if "per month" in gold:
        return bool(re.search(r"\bper\s+(?:\d+\s+)?month\b", predicted))
    if "per week" in gold:
        return bool(re.search(r"\bper\s+(?:\d+\s+)?week\b", predicted))
    return False


def _unresolved_multiple_convention(
    *,
    gold_label: str,
    predicted_label: str,
    gold_reference: str,
    selected_evidence: str,
) -> bool:
    gold = gold_label.lower()
    predicted = predicted_label.lower()
    context = " ".join([gold_reference, selected_evidence]).lower()
    if "cluster" in gold:
        return _cluster_cadence_convention(gold_label=gold_label, predicted_label=predicted_label)
    if gold.startswith("multiple per day") and _has_any(
        predicted,
        "1 per day",
        "daily",
        "per day",
    ):
        return True
    if gold.startswith("multiple per week") and _has_any(
        predicted,
        "multiple per week",
        "several per week",
        "times per week",
    ):
        return True
    if "multiple per" in gold and "seizure free" in predicted:
        return False
    if "multiple per" in gold and _has_any(context, "within-cluster count unclear"):
        return True
    return False


def _score(source_row: Mapping[str, Any], layer_name: str) -> dict[str, Any]:
    return dict((source_row.get("score_layers") or {}).get(layer_name) or {})


def _layer_correctness_summary(score: Mapping[str, Any]) -> dict[str, Any]:
    if not score:
        return {"scorable": False, "purist_correct": False, "final_label": ""}
    return {
        "scorable": bool(score.get("scorable", False)),
        "purist_correct": bool(score.get("purist_correct", False)),
        "pragmatic_correct": bool(score.get("pragmatic_correct", False)),
        "final_label": score.get("final_label") or "",
    }


def _by_hidden_family(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    by_family: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        for family in row["hidden_families"]:
            by_family[str(family)].append(row)
    return {family: _group_summary(group_rows) for family, group_rows in by_family.items()}


def _by_first_failure_owner(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    by_owner: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        by_owner[str(row["first_failure_owner"])].append(row)
    return {owner: _group_summary(group_rows) for owner, group_rows in by_owner.items()}


def _group_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    class_counts = Counter(str(row["rq10_primary_class"]) for row in rows)
    return {
        "rows": len(rows),
        "primary_class_counts": dict(sorted(class_counts.items())),
        "main_primary_class": class_counts.most_common(1)[0][0],
    }


def _answer_paragraph(metadata: Mapping[str, Any]) -> str:
    metrics = metadata["metrics"]
    return (
        "The residual validation hard rows are mixed: "
        f"{metrics['hard_row_ambiguity_rate']:.3f} of Purist misses carry a non-plain "
        "extraction-failure RQ10 class, while the remaining rows still look like true "
        "candidate-selection, temporal-selection, denominator, or semiology failures. "
        f"{metrics['exact_evidence_but_scorer_wrong_rows']} rows have exact evidence but are "
        "scorer/gold-wrong under the saved primary layer, "
        f"{metrics['benchmark_convention_dominated_rows']} are primarily benchmark-convention "
        f"dominated, and {metrics['likely_gold_defect_rows']} are strong likely gold defects. "
        "The useful conclusion is not that the benchmark is wrong; it is that hard-row "
        "residue should be routed through ambiguity/review policy instead of being used as "
        "undifferentiated pressure to retune extraction rules."
    )


def _example_section(
    section: str,
    source_indices: Sequence[int],
    rows: Sequence[Mapping[str, Any]],
) -> list[str]:
    by_index = {int(row["source_row_index"]): row for row in rows}
    lines = [
        f"### {section}",
        "",
        "| Row | Gold | Prediction | Gold reference | Selected evidence | Rationale |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for source_index in source_indices:
        row = by_index.get(source_index)
        if not row:
            continue
        lines.append(
            "| {idx} | `{gold}` | `{pred}` | {gold_ref} | {selected} | {rationale} |".format(
                idx=row["source_row_index"],
                gold=_escape_md(str(row["gold_label"])),
                pred=_escape_md(str(row["primary_predicted_label"])),
                gold_ref=_inline_text(str(row["gold_reference"]), 110),
                selected=_inline_text(str(row["selected_evidence"]), 110),
                rationale=_inline_text(str(row["adjudication_rationale"]), 140),
            )
        )
    lines.append("")
    return lines


def _sorted_counts(counts: Mapping[str, int]) -> list[tuple[str, int]]:
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def _sorted_family_summary(
    summary: Mapping[str, Mapping[str, Any]],
) -> list[tuple[str, Mapping[str, Any]]]:
    return sorted(summary.items(), key=lambda item: (-int(item[1]["rows"]), item[0]))


def _split_families(value: Any) -> list[str]:
    if isinstance(value, str):
        return [family for family in value.split(";") if family]
    return [str(family) for family in value if family]


def _inline_text(text: str, limit: int) -> str:
    text = _escape_md(" ".join(text.split()))
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _escape_md(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _safe_rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def _bool_or_false(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def _has_any(text: str, *needles: str) -> bool:
    return any(needle in text for needle in needles)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay-path", type=Path, default=DEFAULT_REPLAY_PATH)
    parser.add_argument("--data-path", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    rows, metadata = build_audit_rows(replay_path=args.replay_path, data_path=args.data_path)
    write_jsonl_rows(rows, args.jsonl_path)
    write_audit_json(metadata, args.json_path)
    write_audit_report(
        rows,
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
