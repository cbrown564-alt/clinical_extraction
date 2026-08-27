#!/usr/bin/env python3
"""Aggregate-only test60 replay for ACCEPTED_THREE_STAGE_CONFIG.

Protocol: docs/research/exectv2/exect_rules_only_three_stage_test60_aggregate_protocol_2026-08-27.md
Gate A (dev140 parity) must pass before running this script.
Do not inspect or quote holdout rows from the sealed output.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.rules import (
    ACCEPTED_THREE_STAGE_CONFIG,
    run_letter,
    run_letter_retune_stack,
    run_letter_three_stage,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (
    TARGET_INDICATORS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    aggregate_scores,
    exact_clinical_inventory_scores,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/exectv2/"
    "exect_rules_only_three_stage_test60_aggregate_protocol_2026-08-27.md"
)
OUT_JSON = (
    REPO_ROOT / "experiments/exect_rules_only_three_stage_test60_aggregate_20260827.json"
)
SEALED_ROOT = REPO_ROOT / "scratch/holdout/exect_rules_only_three_stage_test60_20260827"
LETTER_ID_RE = re.compile(r"\bEA\d{4}\b")
TEST_ROW_COUNT = 59


def main() -> None:
    letters = sorted(load_letters_for_split("test"), key=lambda item: item.letter_id)
    if len(letters) != TEST_ROW_COUNT:
        raise RuntimeError(f"expected {TEST_ROW_COUNT} test letters, found {len(letters)}")
    gold = [_gold_view(letter) for letter in letters]
    comparator_preds = [_predict_comparator(letter) for letter in letters]
    candidate_preds = [_predict_candidate(letter) for letter in letters]
    payload = _build_payload(gold, comparator_preds, candidate_preds)
    sealed_path = _write_sealed(comparator_preds, candidate_preds)
    payload["sealed_predictions"] = {
        "local_path": sealed_path.relative_to(REPO_ROOT).as_posix(),
        "sha256": _sha256(sealed_path),
        "bytes": sealed_path.stat().st_size,
        "note": "Sealed under scratch/holdout; not for row inspection or public copy.",
    }
    _assert_aggregate_only(payload)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    _assert_no_letter_ids(text, "public JSON")
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(text, encoding="utf-8")
    print(OUT_JSON)
    for arm in ("comparator", "candidate"):
        overall = payload["arms"][arm]["overall"]
        print(
            f"{arm}: F1 {overall['f1']:.4f} "
            f"P {overall['precision']:.4f} R {overall['recall']:.4f}"
        )


def _gold_view(letter: ExectLetter) -> ExectLetter:
    return ExectLetter(
        letter_id=letter.letter_id,
        note_text=letter.note_text,
        annotations=tuple(
            annotation
            for annotation in letter.annotations
            if annotation.entity in TARGET_INDICATORS
        ),
    )


def _predict_comparator(letter: ExectLetter) -> ExectLetter:
    result = run_letter_retune_stack(letter)
    return _to_exect(letter.letter_id, result.comparison_projection.mentions)


def _predict_candidate(letter: ExectLetter) -> ExectLetter:
    result = run_letter_three_stage(letter, ACCEPTED_THREE_STAGE_CONFIG)
    return _to_exect(letter.letter_id, result.comparison_projection.mentions)


def _to_exect(letter_id: str, mentions: tuple[PredictedMention, ...]) -> ExectLetter:
    return ExectLetter(
        letter_id=letter_id,
        note_text="",
        annotations=tuple(
            ExectAnnotation(
                entity=mention.entity,
                text=mention.text,
                attributes=dict(mention.attributes),
            )
            for mention in mentions
            if mention.entity in TARGET_INDICATORS
        ),
    )


def _score_arm(
    gold: list[ExectLetter], predictions: list[ExectLetter]
) -> dict[str, object]:
    by_family = exact_clinical_inventory_scores(gold, predictions)
    return {
        "overall": aggregate_scores(by_family.values()),
        "by_family": by_family,
    }


def _family_delta(
    comparator: dict[str, object], candidate: dict[str, object]
) -> dict[str, dict[str, float]]:
    comp_families = comparator["by_family"]
    cand_families = candidate["by_family"]
    deltas: dict[str, dict[str, float]] = {}
    for family in TARGET_INDICATORS:
        comp = comp_families[family]
        cand = cand_families[family]
        deltas[family] = {
            "f1_delta": round(float(cand["f1"]) - float(comp["f1"]), 4),
            "precision_delta": round(
                float(cand["precision"]) - float(comp["precision"]), 4
            ),
            "recall_delta": round(float(cand["recall"]) - float(comp["recall"]), 4),
        }
    return deltas


def _build_payload(
    gold: list[ExectLetter],
    comparator_preds: list[ExectLetter],
    candidate_preds: list[ExectLetter],
) -> dict[str, object]:
    comparator = _score_arm(gold, comparator_preds)
    candidate = _score_arm(gold, candidate_preds)
    comp_overall = comparator["overall"]
    cand_overall = candidate["overall"]
    return {
        "schema_version": "exect.rules_only.three_stage_test60_aggregate.v1",
        "protocol": PROTOCOL,
        "generated_on": date.today().isoformat(),
        "split": "test60",
        "split_loader": "test",
        "row_count": len(gold),
        "row_policy": "aggregate_only",
        "holdout_loaded": True,
        "model_calls": 0,
        "scorer": "clinical_inventory_unit_keys",
        "candidate_config": "ACCEPTED_THREE_STAGE_CONFIG",
        "comparator": "run_letter accepted 2026-08-27 retune stack",
        "cited_comparator_f1": 0.7725,
        "arms": {
            "comparator": comparator,
            "candidate": candidate,
        },
        "deltas": {
            "overall": {
                "f1_delta": round(float(cand_overall["f1"]) - float(comp_overall["f1"]), 4),
                "precision_delta": round(
                    float(cand_overall["precision"]) - float(comp_overall["precision"]),
                    4,
                ),
                "recall_delta": round(
                    float(cand_overall["recall"]) - float(comp_overall["recall"]), 4,
                ),
            },
            "by_family": _family_delta(comparator, candidate),
        },
        "supersedes_cited_comparator": True,
        "claim_boundary": (
            "Aggregate-only holdout replay of ACCEPTED_THREE_STAGE_CONFIG. "
            "Family P/R expectations were predeclared in the protocol before "
            "execution. No letter identifiers or row mechanisms in public "
            "artifacts. Not clinical validation."
        ),
    }


def _write_sealed(
    comparator_preds: list[ExectLetter],
    candidate_preds: list[ExectLetter],
) -> Path:
    SEALED_ROOT.mkdir(parents=True, exist_ok=True)
    path = SEALED_ROOT / "inventory_predictions.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for comp, cand in zip(comparator_preds, candidate_preds, strict=True):
            row = {
                "letter_id": comp.letter_id,
                "comparator_annotations": [
                    {
                        "entity": ann.entity,
                        "text": ann.text,
                        "attributes": dict(ann.attributes),
                    }
                    for ann in comp.annotations
                ],
                "candidate_annotations": [
                    {
                        "entity": ann.entity,
                        "text": ann.text,
                        "attributes": dict(ann.attributes),
                    }
                    for ann in cand.annotations
                ],
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return path


def _assert_aggregate_only(payload: dict[str, object]) -> None:
    forbidden = {
        "rows",
        "letters",
        "predictions",
        "traces",
        "letter_id",
        "note_text",
    }
    leaked = sorted(forbidden.intersection(payload))
    if leaked:
        raise ValueError(f"public payload contains forbidden keys: {leaked}")


def _assert_no_letter_ids(text: str, label: str) -> None:
    hits = LETTER_ID_RE.findall(text)
    if hits:
        raise ValueError(f"{label} leaked letter ids: {hits[:5]}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
