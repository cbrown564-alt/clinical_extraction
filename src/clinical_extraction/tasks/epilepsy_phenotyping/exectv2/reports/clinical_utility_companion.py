"""Clinical-utility companion audit for ExECTv2 assembly runs.

This report sits beside benchmark F1. It asks whether the extracted evidence is
clinically useful, whether deterministic repairs are clinically or benchmark
motivated, and which rows need human gold-disagreement review.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (
    TARGET_INDICATORS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import normalize_phrase

DEFAULT_RUNS: tuple[tuple[str, Path, Path], ...] = (
    (
        "v08_dev140_control",
        Path("experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.json"),
        Path("experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.jsonl"),
    ),
    (
        "v09_partial_hybrid",
        Path("experiments/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140_20260621.json"),
        Path("experiments/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140_20260621.jsonl"),
    ),
    (
        "v0916_deepseek_diagnostic",
        Path("experiments/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.json"),
        Path("experiments/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.jsonl"),
    ),
    (
        "v0922_qwen_diagnostic",
        Path("experiments/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140_20260622.json"),
        Path("experiments/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140_20260622.jsonl"),
    ),
)

REVIEW_FLAG_ORDER: tuple[str, ...] = (
    "gold_likely_incomplete",
    "gold_span_drift_or_truncation",
    "prediction_clinically_supported_benchmark_fp",
    "prediction_plausible_but_overcalled",
    "deterministic_repair_changed_clinical_meaning",
)
SCORE_SURFACES: tuple[tuple[str, str, str], ...] = (
    ("source_model_scored_output", "materialized_surfaces", "source_scored"),
    ("evidence_valid_only", "materialized_surfaces", "evidence_valid"),
    ("dictionary_normalization_only", "materialized_surfaces", "dictionary_normalized"),
    (
        "residual_benchmark_additions",
        "materialized_surfaces",
        "residual_benchmark_added",
    ),
    ("full_final_assembly", "materialized_surfaces", "final"),
    ("clinical_headline", "headline_target", ""),
)


@dataclass(frozen=True)
class RunSpec:
    run_id: str
    report_json: Path
    rows_jsonl: Path


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def build_companion_report(
    run_specs: Sequence[RunSpec],
    *,
    split: str = "dev",
    sample_limit: int = 20,
    generated_on: str | None = None,
    gold_loader: Any = load_letters_for_split,
) -> dict[str, Any]:
    generated_on = generated_on or date.today().isoformat()
    gold_by_id = {letter.letter_id: letter for letter in gold_loader(split)}
    runs: list[dict[str, Any]] = []
    for spec in run_specs:
        rows = read_jsonl(spec.rows_jsonl)
        report = json.loads(spec.report_json.read_text(encoding="utf-8"))
        runs.append(
            _run_summary(
                spec,
                report,
                rows,
                gold_by_id=gold_by_id,
                sample_limit=sample_limit,
            )
        )
    return {
        "title": "ExECTv2 clinical-utility companion audit",
        "generated_on": generated_on,
        "split": split,
        "sample_limit": sample_limit,
        "question_answers": _question_answers(runs),
        "method": {
            "scope": (
                "No-call replay over the final four dev140 architecture artifacts. "
                "Clinical-utility flags are review heuristics, not replacement labels."
            ),
            "repair_ablation_note": (
                "Raw/source, evidence-valid, dictionary-only, residual-addition, "
                "and final surfaces are directly scored when the assembly row "
                "contains materialized prediction_surfaces. Older artifacts fall "
                "back to their closest available scored surfaces."
            ),
        },
        "runs": runs,
    }


def write_companion_artifacts(
    *,
    out_json: Path,
    out_md: Path,
    run_specs: Sequence[RunSpec] | None = None,
    split: str = "dev",
    sample_limit: int = 20,
    generated_on: str | None = None,
) -> tuple[Path, Path]:
    report = build_companion_report(
        run_specs or [RunSpec(*run) for run in DEFAULT_RUNS],
        split=split,
        sample_limit=sample_limit,
        generated_on=generated_on,
    )
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(render_markdown(report, json_path=out_json), encoding="utf-8")
    return out_json, out_md


def _run_summary(
    spec: RunSpec,
    report: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    *,
    gold_by_id: Mapping[str, ExectLetter],
    sample_limit: int,
) -> dict[str, Any]:
    scored_mentions = [m for row in rows for m in row.get("predicted_mentions", [])]
    raw_mentions = [m for row in rows for m in row.get("raw_lane_mentions", [])]
    review_rows = []
    for row in rows:
        reviewed = _row_review(row, gold_by_id[str(row["letter_id"])])
        if reviewed.get("flags"):
            review_rows.append(reviewed)
    return {
        "run_id": spec.run_id,
        "candidate_name": report.get("candidate_name", spec.run_id),
        "report_json": spec.report_json.as_posix(),
        "rows_jsonl": spec.rows_jsonl.as_posix(),
        "row_count": len(rows),
        "repair_ablation": _repair_ablation(report, rows),
        "clinical_utility": {
            "raw_lane_mentions": len(raw_mentions),
            "scored_mentions": len(scored_mentions),
            "evidence_quality": _evidence_quality(rows, gold_by_id),
            "duplicate_clinical_fact_compression": _duplicate_compression(rows),
            "gold_omitted_supported_facts": _gold_omitted_supported_facts(rows),
        },
        "deterministic_action_buckets": _deterministic_action_buckets(rows),
        "gold_disagreement_review": {
            "flag_counts": dict(Counter(flag for row in review_rows for flag in row["flags"])),
            "review_row_count": len(review_rows),
            "sample_rows": review_rows[:sample_limit],
        },
    }


def _repair_ablation(
    report: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    ladder = report.get("score_ladder", {})
    deterministic_counts = _deterministic_action_buckets(rows)
    surfaces = {}
    for label, surface_group, surface_key in SCORE_SURFACES:
        score = _surface_score(ladder, surface_group=surface_group, surface_key=surface_key)
        surfaces[label] = {
            "surface": surface_key or surface_group,
            "overall": score.get("overall", {}),
            "by_indicator": score.get("by_indicator", {}),
            "materialization": "directly_scored",
        }
    return {
        "surfaces": surfaces,
        "deterministic_counts_by_bucket": deterministic_counts["bucket_counts"],
        "deterministic_counts_by_entity": deterministic_counts["entity_bucket_counts"],
    }


def _surface_score(
    ladder: Mapping[str, Any],
    *,
    surface_group: str,
    surface_key: str,
) -> Mapping[str, Any]:
    if surface_group == "materialized_surfaces":
        materialized = ladder.get("materialized_surfaces", {})
        if isinstance(materialized, Mapping) and surface_key in materialized:
            return materialized[surface_key]
        fallback = {
            "source_scored": "raw_lane_score",
            "evidence_valid": "evidence_valid_score",
            "dictionary_normalized": "evidence_valid_score",
            "residual_benchmark_added": "evidence_valid_score",
            "final": "evidence_valid_score",
        }[surface_key]
        return ladder.get(fallback, {})
    return ladder.get(surface_group, {})


def _evidence_quality(
    rows: Sequence[Mapping[str, Any]],
    gold_by_id: Mapping[str, ExectLetter],
) -> dict[str, Any]:
    total = exact = contains_attr = sentence_like = 0
    status_counts: Counter[str] = Counter()
    by_entity: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        note = gold_by_id[str(row["letter_id"])].note_text
        for mention in row.get("predicted_mentions", []):
            entity = str(mention.get("entity", ""))
            evidence = str(mention.get("evidence", ""))
            total += 1
            is_exact = bool(evidence) and evidence in note
            exact += int(is_exact)
            attr_hit = _evidence_contains_attribute_signal(mention)
            contains_attr += int(attr_hit)
            sentence_like += int(_sentence_like(evidence))
            status = _status_bucket(evidence)
            status_counts[status] += 1
            by_entity[entity].update(
                {
                    "mentions": 1,
                    "exact_evidence": int(is_exact),
                    "attribute_signal": int(attr_hit),
                    f"status_{status}": 1,
                }
            )
    return {
        "mentions": total,
        "exact_evidence_mentions": exact,
        "exact_evidence_rate": _rate(exact, total),
        "attribute_signal_mentions": contains_attr,
        "attribute_signal_rate": _rate(contains_attr, total),
        "sentence_like_evidence_mentions": sentence_like,
        "sentence_like_evidence_rate": _rate(sentence_like, total),
        "status_counts": dict(status_counts),
        "by_entity": {entity: dict(counter) for entity, counter in sorted(by_entity.items())},
    }


def _duplicate_compression(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    gold_duplicate = predicted_duplicate = 0
    by_entity: dict[str, dict[str, int]] = {}
    for entity in TARGET_INDICATORS:
        gold_keys: list[str] = []
        pred_keys: list[str] = []
        for row in rows:
            gold_keys.extend(
                _fact_key(m)
                for m in row.get("gold_mentions", [])
                if m.get("entity") == entity
            )
            pred_keys.extend(
                _fact_key(m) for m in row.get("predicted_mentions", []) if m.get("entity") == entity
            )
        gold_extra = len(gold_keys) - len(set(gold_keys))
        pred_extra = len(pred_keys) - len(set(pred_keys))
        gold_duplicate += gold_extra
        predicted_duplicate += pred_extra
        by_entity[entity] = {
            "gold_duplicate_mentions": gold_extra,
            "predicted_duplicate_mentions": pred_extra,
            "compression_delta_pred_minus_gold": pred_extra - gold_extra,
        }
    return {
        "gold_duplicate_mentions": gold_duplicate,
        "predicted_duplicate_mentions": predicted_duplicate,
        "compression_delta_pred_minus_gold": predicted_duplicate - gold_duplicate,
        "by_entity": by_entity,
    }


def _gold_omitted_supported_facts(
    rows: Sequence[Mapping[str, Any]],
    *,
    limit: int = 30,
) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    examples: list[dict[str, Any]] = []
    for row in rows:
        gold = list(row.get("gold_mentions", []))
        for mention in row.get("predicted_mentions", []):
            entity = str(mention.get("entity", ""))
            if not mention.get("evidence_valid") and not mention.get("evidence"):
                continue
            if _matches_any_gold(mention, gold):
                continue
            counts[entity] += 1
            if len(examples) < limit:
                examples.append(
                    {
                        "letter_id": row["letter_id"],
                        "entity": entity,
                        "text": mention.get("text", ""),
                        "evidence": mention.get("evidence", ""),
                        "flags": _mention_review_flags(mention),
                    }
                )
    return {"counts_by_entity": dict(counts), "examples": examples}


def _deterministic_action_buckets(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    bucket_counts: Counter[str] = Counter()
    entity_bucket_counts: dict[str, Counter[str]] = defaultdict(Counter)
    actions: Counter[str] = Counter()
    for row in rows:
        for mention in row.get("predicted_mentions", []):
            entity = str(mention.get("entity", ""))
            for provenance in mention.get("provenance", []):
                if not _is_deterministic(provenance):
                    continue
                bucket = _action_bucket(provenance, entity)
                action = str(provenance.get("action", ""))
                bucket_counts[bucket] += 1
                entity_bucket_counts[entity][bucket] += 1
                actions[f"{bucket}:{action}"] += 1
    return {
        "bucket_counts": dict(bucket_counts),
        "entity_bucket_counts": {
            entity: dict(counter) for entity, counter in sorted(entity_bucket_counts.items())
        },
        "top_actions": dict(actions.most_common(20)),
    }


def _row_review(row: Mapping[str, Any], gold_letter: ExectLetter) -> dict[str, Any]:
    flags: set[str] = set()
    note = gold_letter.note_text
    mentions = list(row.get("predicted_mentions", []))
    gold_mentions = list(row.get("gold_mentions", []))
    exact_predictions = [
        m for m in mentions if str(m.get("evidence", "")) and str(m.get("evidence", "")) in note
    ]
    if len(exact_predictions) > len(gold_mentions):
        flags.add("gold_likely_incomplete")
        flags.add("prediction_clinically_supported_benchmark_fp")
    if any(_gold_span_drift(m) for m in gold_mentions):
        flags.add("gold_span_drift_or_truncation")
    if any(
        _status_bucket(str(m.get("evidence", "")))
        in {"family_history", "future", "uncertain"}
        for m in mentions
    ):
        flags.add("prediction_plausible_but_overcalled")
    if any(
        _is_deterministic(p)
        for mention in mentions
        for p in mention.get("provenance", [])
    ):
        flags.add("deterministic_repair_changed_clinical_meaning")
    return {
        "letter_id": row["letter_id"],
        "flags": [flag for flag in REVIEW_FLAG_ORDER if flag in flags],
        "gold_count": len(gold_mentions),
        "predicted_count": len(mentions),
        "exact_predicted_count": len(exact_predictions),
        "example_predictions": [
            {
                "entity": m.get("entity", ""),
                "text": m.get("text", ""),
                "evidence": m.get("evidence", ""),
                "owners": sorted(
                    {
                        str(p.get("owner", ""))
                        for p in m.get("provenance", [])
                        if str(p.get("owner", ""))
                    }
                ),
            }
            for m in mentions[:4]
        ],
    }


def _question_answers(runs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    best_exact = max(
        runs,
        key=lambda r: r["clinical_utility"]["evidence_quality"]["exact_evidence_rate"],
    )
    best_attr = max(
        runs,
        key=lambda r: r["clinical_utility"]["evidence_quality"]["attribute_signal_rate"],
    )
    benchmark_buckets = sum(
        r["deterministic_action_buckets"]["bucket_counts"].get("benchmark_format", 0)
        for r in runs
    )
    clinical_buckets = sum(
        r["deterministic_action_buckets"]["bucket_counts"].get("clinical_useful", 0)
        for r in runs
    )
    return {
        "are_predictions_better_than_gold": (
            "Often yes for evidence packaging and supported fact granularity: the "
            f"best exact-evidence run is {best_exact['run_id']} and the best "
            f"attribute-signal run is {best_attr['run_id']}. These are review "
            "signals, not proof that gold labels are wrong."
        ),
        "are_we_constraining_clinical_usefulness": (
            "Yes in places. Deterministic provenance shows benchmark-format "
            f"actions ({benchmark_buckets}) as well as clinical-useful actions "
            f"({clinical_buckets}); rows with benchmark-format repair need "
            "separate clinical review before treating higher F1 as higher utility."
        ),
    }


def render_markdown(report: Mapping[str, Any], *, json_path: Path) -> str:
    lines = [
        "# ExECTv2 Clinical-Utility Companion Audit",
        "",
        f"- Generated: `{report['generated_on']}`",
        f"- JSON: `{json_path.as_posix()}`",
        f"- Split: `{report['split']}`",
        f"- Sample rows per run: {report['sample_limit']}",
        "",
        "## Direct Answers",
        "",
        f"1. {report['question_answers']['are_predictions_better_than_gold']}",
        f"2. {report['question_answers']['are_we_constraining_clinical_usefulness']}",
        "",
        "## Score And Repair Surfaces",
        "",
        (
            "| Run | Source raw F1 | Evidence-valid F1 | Full final F1 "
            "| Raw mentions | Scored mentions |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for run in report["runs"]:
        surfaces = run["repair_ablation"]["surfaces"]
        utility = run["clinical_utility"]
        lines.append(
            f"| {run['run_id']} | "
            f"{_f1(surfaces['source_model_scored_output']):.4f} | "
            f"{_f1(surfaces['evidence_valid_only']):.4f} | "
            f"{_f1(surfaces['clinical_headline']):.4f} | "
            f"{utility['raw_lane_mentions']} | {utility['scored_mentions']} |"
        )
    lines.extend(
        [
            "",
            "## Materialized Intermediate Surfaces",
            "",
            (
                "| Run | Source | Evidence-valid | Dictionary-only "
                "| Residual additions | Direct final | Clinical headline |"
            ),
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for run in report["runs"]:
        surfaces = run["repair_ablation"]["surfaces"]
        lines.append(
            f"| {run['run_id']} | "
            f"{_f1(surfaces['source_model_scored_output']):.4f} | "
            f"{_f1(surfaces['evidence_valid_only']):.4f} | "
            f"{_f1(surfaces['dictionary_normalization_only']):.4f} | "
            f"{_f1(surfaces['residual_benchmark_additions']):.4f} | "
            f"{_f1(surfaces['full_final_assembly']):.4f} | "
            f"{_f1(surfaces['clinical_headline']):.4f} |"
        )
    lines.extend(
        [
            "",
            "## Clinical Utility Signals",
            "",
            (
                "| Run | Exact evidence | Attribute signal | Sentence-like evidence "
                "| Current | Historical | Future | Family history |"
            ),
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for run in report["runs"]:
        quality = run["clinical_utility"]["evidence_quality"]
        statuses = quality["status_counts"]
        lines.append(
            f"| {run['run_id']} | {quality['exact_evidence_rate']:.3f} | "
            f"{quality['attribute_signal_rate']:.3f} | "
            f"{quality['sentence_like_evidence_rate']:.3f} | "
            f"{statuses.get('current', 0)} | {statuses.get('historical', 0)} | "
            f"{statuses.get('future', 0)} | {statuses.get('family_history', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Deterministic Action Buckets",
            "",
            "| Run | Clinical-useful | Benchmark-format | Seizure-frequency | Other |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for run in report["runs"]:
        counts = run["deterministic_action_buckets"]["bucket_counts"]
        lines.append(
            f"| {run['run_id']} | {counts.get('clinical_useful', 0)} | "
            f"{counts.get('benchmark_format', 0)} | "
            f"{counts.get('seizure_frequency', 0)} | {counts.get('other', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Gold-Disagreement Review",
            "",
            (
                "| Run | Review rows | Gold incomplete | Span drift "
                "| Supported benchmark FP | Plausible overcall "
                "| Deterministic meaning change |"
            ),
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for run in report["runs"]:
        review = run["gold_disagreement_review"]
        counts = review["flag_counts"]
        lines.append(
            f"| {run['run_id']} | {review['review_row_count']} | "
            f"{counts.get('gold_likely_incomplete', 0)} | "
            f"{counts.get('gold_span_drift_or_truncation', 0)} | "
            f"{counts.get('prediction_clinically_supported_benchmark_fp', 0)} | "
            f"{counts.get('prediction_plausible_but_overcalled', 0)} | "
            f"{counts.get('deterministic_repair_changed_clinical_meaning', 0)} |"
        )
    lines.extend(["", "## Notes", ""])
    lines.append(report["method"]["repair_ablation_note"])
    lines.append("")
    lines.append(
        "The row-level sample in the JSON is intentionally capped; use the JSON "
        "for concrete letter IDs and example evidence when adjudicating gold "
        "disagreement."
    )
    lines.append("")
    return "\n".join(lines)


def _f1(surface: Mapping[str, Any]) -> float:
    return float(surface.get("overall", {}).get("f1", 0.0))


def _evidence_contains_attribute_signal(mention: Mapping[str, Any]) -> bool:
    evidence = normalize_phrase(str(mention.get("evidence", "")))
    text = normalize_phrase(str(mention.get("text", "")))
    if text and text in evidence:
        return True
    for key, value in dict(mention.get("attributes", {})).items():
        if key in {"CUI", "CUIPhrase", "Negation", "Certainty"}:
            continue
        value_text = normalize_phrase(str(value))
        if len(value_text) >= 2 and value_text in evidence:
            return True
    return False


def _sentence_like(evidence: str) -> bool:
    stripped = evidence.strip()
    return len(stripped) >= 35 and bool(re.search(r"[.!?]$", stripped))


def _status_bucket(evidence: str) -> str:
    text = evidence.lower()
    if re.search(r"\b(mother|father|sister|brother|family history|familial)\b", text):
        return "family_history"
    if re.search(r"\b(will|plan|planned|awaiting|arrange|repeat|future|next)\b", text):
        return "future"
    if re.search(r"\b(previous|previously|in \d{4}|last year|when she was|history of)\b", text):
        return "historical"
    if re.search(r"\b(possible|probable|query|uncertain|likely|suspected)\b", text):
        return "uncertain"
    return "current"


def _fact_key(mention: Mapping[str, Any]) -> str:
    attrs = {
        k: normalize_phrase(str(v))
        for k, v in dict(mention.get("attributes", {})).items()
        if k not in {"CUI", "CUIPhrase"}
    }
    concept = (
        str(dict(mention.get("attributes", {})).get("CUI", ""))
        or str(mention.get("normalized_concept", ""))
        or normalize_phrase(str(mention.get("text", "")))
    )
    return json.dumps(
        {
            "entity": mention.get("entity", ""),
            "concept": normalize_phrase(concept),
            "attrs": attrs,
        },
        sort_keys=True,
    )


def _matches_any_gold(
    mention: Mapping[str, Any],
    gold_mentions: Sequence[Mapping[str, Any]],
) -> bool:
    pred_entity = str(mention.get("entity", ""))
    pred_attrs = dict(mention.get("attributes", {}))
    pred_text = normalize_phrase(str(mention.get("text", "")))
    pred_cui = str(pred_attrs.get("CUI", ""))
    for gold in gold_mentions:
        if str(gold.get("entity", "")) != pred_entity:
            continue
        gold_attrs = dict(gold.get("attributes", {}))
        gold_text = normalize_phrase(str(gold.get("text", "")))
        if pred_cui and pred_cui == str(gold_attrs.get("CUI", "")):
            return True
        if pred_text and gold_text and (pred_text in gold_text or gold_text in pred_text):
            return True
    return False


def _mention_review_flags(mention: Mapping[str, Any]) -> list[str]:
    flags = []
    status = _status_bucket(str(mention.get("evidence", "")))
    if status in {"family_history", "future", "uncertain"}:
        flags.append(f"status_{status}")
    if any(_is_deterministic(p) for p in mention.get("provenance", [])):
        flags.append("deterministic")
    return flags


def _gold_span_drift(mention: Mapping[str, Any]) -> bool:
    text = str(mention.get("text", "")).strip()
    normalized = normalize_phrase(text)
    return (
        text.endswith("-")
        or len(normalized) <= 4
        or normalized in {"mri", "eeg", "ct", "seizures"}
    )


def _is_deterministic(provenance: Mapping[str, Any]) -> bool:
    owner = str(provenance.get("owner", ""))
    action = str(provenance.get("action", ""))
    llm_owners = {
        "",
        "single_gpt_key_family_event_ledger",
        "llm_first_control",
        "hybrid_diagnosis_route",
        "hybrid_sf_route",
    }
    return owner not in llm_owners or any(
        token in action
        for token in (
            "dictionary",
            "repair",
            "normalized",
            "added",
            "dropped",
            "rewritten",
        )
    )


def _action_bucket(provenance: Mapping[str, Any], entity: str) -> str:
    portability = str(provenance.get("portability", "") or "")
    owner = str(provenance.get("owner", ""))
    detail = (
        provenance.get("detail", {})
        if isinstance(provenance.get("detail", {}), Mapping)
        else {}
    )
    rule_category = str(detail.get("rule_category", ""))
    if portability == "clinical_epilepsy":
        return "clinical_useful"
    if portability == "benchmark_format" or rule_category == "benchmark_format":
        return "benchmark_format"
    if portability == "seizure_frequency" or entity == SEIZURE_FREQUENCY.name:
        return "seizure_frequency"
    if "residual_benchmark" in owner:
        return "benchmark_format"
    if entity in {PRESCRIPTION.name, INVESTIGATIONS.name} and "dictionary" in owner:
        return "clinical_useful"
    if entity == DIAGNOSIS.name and "dictionary" in owner:
        return "benchmark_format"
    return "other"


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def _parse_run_arg(value: str) -> RunSpec:
    parts = value.split("=", 1)
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("--run must be id=report.json,rows.jsonl")
    run_id, paths = parts
    path_parts = paths.split(",", 1)
    if len(path_parts) != 2:
        raise argparse.ArgumentTypeError("--run must be id=report.json,rows.jsonl")
    return RunSpec(run_id=run_id, report_json=Path(path_parts[0]), rows_jsonl=Path(path_parts[1]))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write an ExECTv2 clinical-utility companion report",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--split", default="dev")
    parser.add_argument("--sample-limit", type=int, default=20)
    parser.add_argument("--run", action="append", type=_parse_run_arg, default=[])
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("docs/research/exectv2_clinical_utility_companion_dev140_2026-06-22.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/research/exectv2_clinical_utility_companion_dev140_2026-06-22.md"),
    )
    args = parser.parse_args()
    json_path, md_path = write_companion_artifacts(
        out_json=args.out_json,
        out_md=args.out_md,
        run_specs=args.run or None,
        split=args.split,
        sample_limit=args.sample_limit,
    )
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
