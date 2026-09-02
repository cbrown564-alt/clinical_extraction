#!/usr/bin/env python3
"""Aggregate-only test60 stage rungs for the promoted rules program.

Protocol: docs/research/exectv2/exect_rules_only_stage_rungs_protocol_2026-08-27.md
The dev140 gate must pass before running this script.
Do not inspect or quote holdout rows from the sealed output.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
)
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
    three_stage_stop_mentions,
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
    "docs/research/exectv2/exect_rules_only_stage_rungs_protocol_2026-08-27.md"
)
OUT_JSON = (
    REPO_ROOT / "experiments/exect_rules_only_stage_rungs_test60_aggregate_20260827.json"
)
SEALED_ROOT = REPO_ROOT / "scratch/holdout/exect_rules_only_stage_rungs_test60_20260827"
LETTER_ID_RE = re.compile(r"\bEA\d{4}\b")
TEST_ROW_COUNT = 59
STOPS = ("find", "encode", "select")
EXPECTED_SELECT_F1 = 0.8018


def main() -> None:
    letters = sorted(load_letters_for_split("test"), key=lambda item: item.letter_id)
    if len(letters) != TEST_ROW_COUNT:
        raise RuntimeError(f"expected {TEST_ROW_COUNT} test letters, found {len(letters)}")
    gold = [_gold_view(letter) for letter in letters]

    stop_preds: dict[str, list[ExectLetter]] = {stop: [] for stop in STOPS}
    for letter in letters:
        stops = three_stage_stop_mentions(letter, ACCEPTED_THREE_STAGE_CONFIG)
        if stops.select != run_letter(letter).comparison_projection.mentions:
            raise RuntimeError("select stop diverges from run_letter on a test letter")
        find_non_diagnosis = tuple(
            m for m in stops.find if m.entity != DIAGNOSIS.name
        )
        encode_non_diagnosis = tuple(
            m for m in stops.encode if m.entity != DIAGNOSIS.name
        )
        if find_non_diagnosis != encode_non_diagnosis:
            raise RuntimeError("encode stop changed a non-Diagnosis family on a test letter")
        stop_preds["find"].append(_to_exect(letter.letter_id, stops.find))
        stop_preds["encode"].append(_to_exect(letter.letter_id, stops.encode))
        stop_preds["select"].append(_to_exect(letter.letter_id, stops.select))

    stage_rungs: dict[str, object] = {}
    for stop in STOPS:
        by_family = exact_clinical_inventory_scores(gold, stop_preds[stop])
        stage_rungs[stop] = {
            "overall": aggregate_scores(by_family.values()),
            "by_family": by_family,
        }

    select_f1 = stage_rungs["select"]["overall"]["f1"]
    if round(float(select_f1), 4) != EXPECTED_SELECT_F1:
        raise RuntimeError(
            f"select stop F1 {select_f1} does not reproduce promoted {EXPECTED_SELECT_F1}"
        )

    payload: dict[str, object] = {
        "schema_version": "exect.rules_only.stage_rungs.test60_aggregate.v1",
        "protocol": PROTOCOL,
        "generated_on": date.today().isoformat(),
        "split": "test60",
        "split_loader": "test",
        "row_count": len(gold),
        "row_policy": "aggregate_only",
        "holdout_loaded": True,
        "model_calls": 0,
        "scorer": "clinical_inventory_unit_keys",
        "program": "run_letter_three_stage(ACCEPTED_THREE_STAGE_CONFIG)",
        "gates": {
            "select_stop_mention_identical_to_run_letter": True,
            "encode_stop_non_diagnosis_identical_to_find": True,
            "select_stop_reproduces_promoted_f1": EXPECTED_SELECT_F1,
        },
        "stage_rungs": stage_rungs,
        "claim_boundary": (
            "Aggregate-only stage-stop instrumentation of the frozen promoted "
            "rules program on test60. Find/encode rungs are ablation "
            "views of the cited select stop, not new methods. No letter "
            "identifiers in public files. Not clinical validation."
        ),
    }
    sealed_path = _write_sealed(stop_preds)
    payload["sealed_predictions"] = {
        "local_path": sealed_path.relative_to(REPO_ROOT).as_posix(),
        "sha256": _sha256(sealed_path),
        "bytes": sealed_path.stat().st_size,
        "note": "Sealed under scratch/holdout; not for row inspection or public copy.",
    }
    _assert_aggregate_only(payload)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    _assert_no_letter_ids(text, "public JSON")
    OUT_JSON.write_text(text, encoding="utf-8")
    print(OUT_JSON)
    for stop in STOPS:
        overall = stage_rungs[stop]["overall"]
        print(
            f"{stop}: F1 {overall['f1']:.4f} "
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


def _write_sealed(stop_preds: dict[str, list[ExectLetter]]) -> Path:
    SEALED_ROOT.mkdir(parents=True, exist_ok=True)
    path = SEALED_ROOT / "stage_stop_predictions.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for find_stop, encode, select in zip(
            stop_preds["find"],
            stop_preds["encode"],
            stop_preds["select"],
            strict=True,
        ):
            row = {
                "letter_id": find_stop.letter_id,
                "stops": {
                    "find": _annotations_view(find_stop),
                    "encode": _annotations_view(encode),
                    "select": _annotations_view(select),
                },
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return path


def _annotations_view(letter: ExectLetter) -> list[dict[str, object]]:
    return [
        {
            "entity": annotation.entity,
            "text": annotation.text,
            "attributes": dict(annotation.attributes),
        }
        for annotation in letter.annotations
    ]


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
