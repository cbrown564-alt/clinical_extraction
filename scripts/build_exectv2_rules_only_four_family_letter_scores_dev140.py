#!/usr/bin/env python3
"""Letter-level ExECT rules-only four-family scores on dev140.

Regenerates no-call rules-only predictions and scores them with the same
exact clinical-headline helper used by the six-model category-cut builder, so
letter buckets can include the active rules surface. Records the historical
Decision 0046 result as a reference, not as an expected current score.

No model calls. Development rows only.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.views import (
    build_scoring_views,
    mention_to_dict,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    run_all9_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (
    TARGET_INDICATORS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    aggregate_scores,
    exact_clinical_headline_scores,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DATE_STAMP = "20260806"
REPORT_DATE = "2026-08-06"
PROTOCOL = "docs/research/shared/six_model_category_cut_protocol_2026-08-06.md"
DECISION_0046 = "docs/decisions/0046-exect-primary-method-comparison-boundary.md"
DECISION_0046_REFERENCE_F1 = 0.8160
OUT_JSONL = (
    REPO_ROOT
    / f"experiments/exectv2_rules_only_four_family_letter_scores_dev140_{DATE_STAMP}.jsonl"
)
OUT_SUMMARY = (
    REPO_ROOT
    / f"experiments/exectv2_rules_only_four_family_letter_scores_dev140_{DATE_STAMP}.json"
)


def _gold_to_row(annotation: ExectAnnotation) -> dict[str, Any]:
    return {
        "entity": annotation.entity,
        "text": annotation.text,
        "attributes": dict(annotation.attributes),
    }


def _restrict_to_four_families(letter: PredictedLetter) -> PredictedLetter:
    return PredictedLetter(
        letter_id=letter.letter_id,
        mentions=tuple(m for m in letter.mentions if m.entity in TARGET_INDICATORS),
    )


def _predicted_letter_to_exect(letter: PredictedLetter) -> ExectLetter:
    return ExectLetter(
        letter_id=letter.letter_id,
        note_text="",
        annotations=tuple(
            ExectAnnotation(
                entity=mention.entity,
                text=mention.text,
                attributes={
                    str(key): str(value)
                    for key, value in mention.attributes.items()
                    if value is not None
                },
            )
            for mention in letter.mentions
        ),
    )


def _four_family_gold(letter: ExectLetter) -> ExectLetter:
    return ExectLetter(
        letter_id=letter.letter_id,
        note_text="",
        annotations=tuple(
            annotation
            for annotation in letter.annotations
            if annotation.entity in TARGET_INDICATORS
        ),
    )


def main() -> None:
    gold = load_letters_for_split("dev")
    if len(gold) != 140:
        raise ValueError(f"expected 140 dev letters, got {len(gold)}")

    all9 = tuple(
        run_all9_on_letters(
            gold,
            include_diagnosis_resolution_candidate=False,
            include_diagnosis_benchmark_residuals=False,
        )
    )
    restricted = tuple(_restrict_to_four_families(letter) for letter in all9)
    by_id = {letter.letter_id: letter for letter in restricted}

    rows: list[dict[str, Any]] = []
    gold_scored: list[ExectLetter] = []
    pred_scored: list[ExectLetter] = []
    for letter in gold:
        pred = by_id[letter.letter_id]
        gold_four = _four_family_gold(letter)
        pred_exect = _predicted_letter_to_exect(pred)
        gold_scored.append(gold_four)
        pred_scored.append(pred_exect)
        family_scores = exact_clinical_headline_scores([gold_four], [pred_exect])
        overall = aggregate_scores(family_scores.values())
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": "dev140",
                "pipeline_family": "rules_only",
                "method_id": "exectv2_rules_only",
                "mode": "no-call",
                "gold_mentions": [
                    _gold_to_row(annotation)
                    for annotation in letter.annotations
                    if annotation.entity in TARGET_INDICATORS
                ],
                "predicted_mentions": [
                    mention_to_dict(mention) for mention in pred.mentions
                ],
                "clinical_headline_letter": {
                    "f1": float(overall["f1"]),
                    "precision": float(overall["precision"]),
                    "recall": float(overall["recall"]),
                    "by_family": {
                        family: float(score["f1"])
                        for family, score in family_scores.items()
                    },
                },
            }
        )

    helper_family = exact_clinical_headline_scores(gold_scored, pred_scored)
    helper_overall = aggregate_scores(helper_family.values())

    _views, score_ladder, _headline = build_scoring_views(
        candidate_name="exectv2_rules_only_four_family_dev140_letter_scores",
        ownership="rules_only_restrict_and_rescore",
        gold_letters=gold,
        raw_predictions=restricted,
        scored_predictions=restricted,
    )
    headline = score_ladder["headline_target"]
    headline_f1 = float(headline["overall"]["f1"])

    summary: dict[str, Any] = {
        "schema_version": (
            "exectv2.rules_only_four_family_letter_scores.dev140.v1"
        ),
        "date": REPORT_DATE,
        "generated_on": date.today().isoformat(),
        "protocol": PROTOCOL,
        "decision": DECISION_0046,
        "split": "dev140",
        "row_count": len(rows),
        "row_policy": "dev140_rows_permitted_test60_forbidden",
        "method": {
            "pipeline": "deterministic_all9",
            "production_rule": "restrict_and_rescore",
            "scoring_helper": "exact_clinical_headline_scores",
            "decision_0046_surface": "assembly_headline_target",
            "include_diagnosis_resolution_candidate": False,
            "include_diagnosis_benchmark_residuals": False,
            "scored_families": list(TARGET_INDICATORS),
        },
        "clinical_headline_helper": {
            "f1": float(helper_overall["f1"]),
            "precision": float(helper_overall["precision"]),
            "recall": float(helper_overall["recall"]),
            "by_family": {
                family: {
                    "f1": float(values["f1"]),
                    "precision": float(values["precision"]),
                    "recall": float(values["recall"]),
                }
                for family, values in helper_family.items()
            },
        },
        "active_headline_target": {
            "f1": headline_f1,
            "precision": float(headline["overall"]["precision"]),
            "recall": float(headline["overall"]["recall"]),
            "by_family": {
                family: {
                    "f1": float(values["f1"]),
                    "precision": float(values["precision"]),
                    "recall": float(values["recall"]),
                }
                for family, values in headline["by_indicator"].items()
            },
        },
        "decision_0046_reference": {
            "f1": DECISION_0046_REFERENCE_F1,
            "matches_active": abs(headline_f1 - DECISION_0046_REFERENCE_F1) <= 1e-4,
        },
        "letter_scores_path": OUT_JSONL.relative_to(REPO_ROOT).as_posix(),
        "claim_boundary": (
            "Development letter-level rules-only four-family scores on ExECT "
            "dev140 for category-cut three-method packaging. The active-rules "
            "score is not a reproduction of the retained Decision 0046 result. "
            "Letter-bucket cuts use the exact clinical-headline helper for parity "
            "with llm / llm_with_rules surfaces in the category-cut artifact. "
            "Not holdout evidence."
        ),
    }

    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSONL.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=False) + "\n")
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSONL.relative_to(REPO_ROOT)}")
    print(f"wrote {OUT_SUMMARY.relative_to(REPO_ROOT)}")
    print(
        f"helper_f1={summary['clinical_headline_helper']['f1']:.4f} "
        f"headline_target_f1={headline_f1:.4f}"
    )


if __name__ == "__main__":
    main()
