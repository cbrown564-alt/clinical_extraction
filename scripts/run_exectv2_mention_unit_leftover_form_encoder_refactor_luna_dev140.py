"""No-call remasure that form_recovery keeps the finished leftover-form scores."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit import (
    HYBRID_METHOD,
    LLM_METHOD,
    MENTION_UNIT_PROMPT_VERSION,
    materialize_mention_unit,
    parse_mention_unit_json,
)
from scripts.run_exectv2_mention_unit_v2_leftover_form_v3_luna_dev140 import (
    _form_census,
    _score_method,
)
from scripts.run_exectv2_mention_unit_v2_luna import DEV20_IDS

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/exectv2/mention_unit_leftover_form_encoder_refactor_2026-08-17.md"
)
SOURCE_ROWS = ROOT / "experiments/exectv2_mention_unit_v2_luna_dev140_20260816" / "rows.jsonl"
STUDY_DIR = (
    ROOT / "experiments/exectv2_mention_unit_leftover_form_encoder_refactor_luna_dev140_20260817"
)
ARMS: tuple[bool, ...] = (False, True)
DEV20 = frozenset(DEV20_IDS)
EA0010_CUE = (
    "His last seizures were in his teenage years where he probably "
    "had around 3 or 4 focal to bilateral convulsive seizures."
)
EA0011_CUE = (
    "he did have around 3 febrile seizures between the age of 1 year "
    "and 30 months."
)
EA0158_CUE = (
    "Jennifer’s seizures started at the age of 2 years and have continued every since."
)
EXPECTED = {
    "off": {
        "headline_140": 0.6255,
        "sf_with_count": 58,
    },
    "on": {
        "headline_140": 0.811,
        "sf_f1": 0.567,
        "prescription_f1": 0.9002,
        "empty_gold_sf_extras": 54,
        "rest120_empty_gold_sf_extras": 51,
    },
}


def _arm_key(form_recovery: bool) -> str:
    return "on" if form_recovery else "off"


def main() -> None:
    if not SOURCE_ROWS.exists():
        raise SystemExit(f"missing saved raws: {SOURCE_ROWS}")
    letters = list(load_letters_for_split("dev"))
    if len(letters) != 140:
        raise SystemExit(f"expected 140 development letters, found {len(letters)}")
    by_id = {letter.letter_id: letter for letter in letters}
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()

    rows: list[dict[str, Any]] = []
    gold_in_order = []
    predictions: dict[str, list[PredictedLetter]] = {
        _arm_key(form_recovery): [] for form_recovery in ARMS
    }
    with SOURCE_ROWS.open(encoding="utf-8") as handle:
        for line in handle:
            saved = json.loads(line)
            letter = by_id[str(saved["letter_id"])]
            gold_in_order.append(letter)
            row = _rematerialize_row(letter, saved)
            rows.append(row)
            for form_recovery in ARMS:
                key = _arm_key(form_recovery)
                predictions[key].append(
                    PredictedLetter.model_validate(row["hybrid"][key]["prediction"])
                )
    slices = {
        "all140": [letter.letter_id for letter in gold_in_order],
        "rest120": [
            letter.letter_id for letter in gold_in_order if letter.letter_id not in DEV20
        ],
    }
    scored: dict[str, dict[str, Any]] = {}
    for slice_name, letter_ids in slices.items():
        gold, preds = _slice(gold_in_order, predictions, letter_ids)
        scored[slice_name] = {
            "methods": {name: _score_method(gold, preds[name]) for name in preds},
            "form_census": {name: _form_census(preds[name]) for name in preds},
        }
    observed = _observed(scored)
    named = _named_leftovers(rows)
    mismatches = _mismatches(observed, named)
    artifact = {
        "schema_version": "exectv2.mention_unit_leftover_form_encoder_refactor.dev140.v1",
        "status": "match" if not mismatches else "drift",
        "protocol": PROTOCOL,
        "split": "dev140",
        "row_count": len(rows),
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "form_recovery": list(ARMS),
        "expected": EXPECTED,
        "observed": observed,
        "named_leftovers": named,
        "mismatches": mismatches,
        "slices": {
            name: {
                "letter_count": len(letter_ids),
                "methods": scored[name]["methods"],
                "form_census": scored[name]["form_census"],
            }
            for name, letter_ids in slices.items()
        },
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "claim_boundary": (
            "Code-structure remasure of form_recovery on frozen mention-unit v2 "
            "dev140 hybrid raws. Not a score claim, not holdout evidence, and "
            "not a Decision 0050 change."
        ),
    }
    (STUDY_DIR / "comparison.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {"model_calls": 0, "status": artifact["status"], "mismatches": mismatches},
            indent=2,
        )
    )
    if mismatches:
        sys.exit(1)


def _rematerialize_row(letter: Any, saved: dict[str, Any]) -> dict[str, Any]:
    raw = str(saved["methods"][HYBRID_METHOD]["raw_output"])
    parsed = parse_mention_unit_json(raw, method=HYBRID_METHOD)
    hybrid: dict[str, Any] = {}
    for form_recovery in ARMS:
        key = _arm_key(form_recovery)
        if parsed.record is None:
            prediction = PredictedLetter(letter_id=letter.letter_id, mentions=())
            payload = {
                "semantic_facts": [],
                "rule_trace": [],
                "warnings": [],
                "evidence_invalid": 0,
                "prediction": prediction.model_dump(mode="json"),
            }
        else:
            materialized = materialize_mention_unit(
                letter,
                parsed.record,
                method=HYBRID_METHOD,
                form_recovery=form_recovery,
            )
            payload = {
                "semantic_facts": materialized.semantic_facts,
                "rule_trace": materialized.rule_trace,
                "warnings": materialized.warnings,
                "evidence_invalid": materialized.evidence_invalid,
                "prediction": materialized.prediction.model_dump(mode="json"),
            }
        hybrid[key] = payload
    return {
        "letter_id": letter.letter_id,
        "split": "dev140",
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "raw_output": raw,
        "parse_errors": parsed.errors,
        "hybrid": hybrid,
        "llm_prediction": saved["methods"][LLM_METHOD]["prediction"],
    }


def _observed(scored: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    all140 = scored["all140"]
    rest = scored["rest120"]
    observed: dict[str, dict[str, Any]] = {}
    for form_recovery in ARMS:
        key = _arm_key(form_recovery)
        methods = all140["methods"][key]
        row: dict[str, Any] = {
            "headline_140": methods["clinical_headline_f1"],
            "empty_gold_sf_extras": methods["empty_gold_sf_extras"]["mention_count"],
            "rest120_empty_gold_sf_extras": rest["methods"][key]["empty_gold_sf_extras"][
                "mention_count"
            ],
            "sf_with_count": all140["form_census"][key]["sf_with_count"],
            "sf_f1": methods["clinical_headline_family_f1"]["SeizureFrequency"],
            "prescription_f1": methods["clinical_headline_family_f1"]["Prescription"],
        }
        observed[key] = row
    return observed


def _named_leftovers(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {row["letter_id"]: row for row in rows}
    key = "on"
    return {
        "ea0010_dropped": _mention_with_cue(by_id["EA0010"], key, EA0010_CUE) is None,
        "ea0011_dropped": _mention_with_cue(by_id["EA0011"], key, EA0011_CUE) is None,
        "ea0158_kept": _mention_with_cue(by_id["EA0158"], key, EA0158_CUE) is not None,
    }


def _mismatches(
    observed: dict[str, dict[str, Any]], named: dict[str, Any]
) -> list[dict[str, Any]]:
    mismatches: list[dict[str, Any]] = []
    for arm, expected in EXPECTED.items():
        for key, value in expected.items():
            got = observed[arm][key]
            if got != value:
                mismatches.append(
                    {
                        "form_recovery": arm,
                        "metric": key,
                        "expected": value,
                        "observed": got,
                    }
                )
    for key, value in named.items():
        if value is not True:
            mismatches.append(
                {
                    "form_recovery": True,
                    "metric": key,
                    "expected": True,
                    "observed": value,
                }
            )
    return mismatches


def _slice(
    gold: list[Any],
    predictions: dict[str, list[PredictedLetter]],
    letter_ids: list[str],
) -> tuple[list[Any], dict[str, list[PredictedLetter]]]:
    wanted = set(letter_ids)
    keep = [index for index, letter in enumerate(gold) if letter.letter_id in wanted]
    return (
        [gold[index] for index in keep],
        {name: [rows[index] for index in keep] for name, rows in predictions.items()},
    )


def _mention_with_cue(row: dict[str, Any], arm: str, cue: str) -> Any | None:
    prediction = PredictedLetter.model_validate(row["hybrid"][arm]["prediction"])
    matches = [
        mention
        for mention in prediction.mentions
        if mention.entity == "SeizureFrequency"
        and cue.casefold() in mention.evidence.casefold()
    ]
    return matches[0] if matches else None


def _provenance() -> dict[str, Any]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    dirty = bool(
        subprocess.run(
            ["git", "status", "--porcelain"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout.strip()
    )
    return {"git_head": commit, "dirty_tree": dirty}


if __name__ == "__main__":
    main()
