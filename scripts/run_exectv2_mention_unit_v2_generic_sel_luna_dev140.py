"""No-call catalog of remaining generic-seizure extras on febrile v14."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit import (
    HYBRID_METHOD,
    MENTION_UNIT_PROMPT_VERSION,
    _fold_span,
    materialize_mention_unit,
    parse_mention_unit_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    frequency_state_faithful,
    frequency_state_keys,
)
from scripts.run_exectv2_mention_unit_v2_leftover_form_stack_error_analysis_luna_dev140 import (
    _gold_letter_extra_class,
)
from scripts.run_exectv2_mention_unit_v2_leftover_form_v3_luna_dev140 import (
    _empty_gold_sf_extras,
)
from scripts.run_exectv2_mention_unit_v2_luna import DEV20_IDS

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/exectv2/"
    "mention_unit_v2_generic_sel_luna_dev140_protocol_2026-08-17.md"
)
REPORT = ROOT / (
    "docs/research/exectv2/mention_unit_v2_generic_sel_luna_dev140_2026-08-17.md"
)
SOURCE_ROWS = ROOT / "experiments/exectv2_mention_unit_v2_luna_dev140_20260816" / "rows.jsonl"
V10_CATALOG = (
    ROOT
    / "experiments/exectv2_mention_unit_v2_leftover_form_stack_luna_dev140_20260817"
    / "error_analysis.json"
)
STUDY_DIR = ROOT / "experiments/exectv2_mention_unit_v2_generic_sel_luna_dev140_20260817"
CONTROL = "leftover_form_span_fold_febrile_v14"
CANDIDATE_IDENTITY = "leftover_form_span_fold_generic_sel_v16"
DEV20 = frozenset(DEV20_IDS)
COUNT_ATTRS = {
    "LowerNumberOfSeizures",
    "NumberOfSeizures",
    "UpperNumberOfSeizures",
}
GENERIC_NAMES = frozenset({"seizure", "seizures"})
GOLD_GENERIC_OR_FREEDOM = frozenset(
    {
        "seizure",
        "seizures",
        "seizure-free",
        "seizure-freedom",
        "seizure free",
    }
)
V10_EXAMPLE_IDS = (
    "EA0008",
    "EA0035",
    "EA0038",
    "EA0039",
    "EA0084",
    "EA0096",
    "EA0102",
    "EA0117",
    "EA0142",
    "EA0156",
    "EA0162",
    "EA0176",
    "EA0182",
    "EA0190",
    "EA0195",
)


def main() -> None:
    if not SOURCE_ROWS.exists():
        raise SystemExit(f"missing saved raws: {SOURCE_ROWS}")
    letters = list(load_letters_for_split("dev"))
    if len(letters) != 140:
        raise SystemExit(f"expected 140 development letters, found {len(letters)}")
    by_id = {letter.letter_id: letter for letter in letters}
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()

    gold_in_order: list[ExectLetter] = []
    predictions: list[PredictedLetter] = []
    with SOURCE_ROWS.open(encoding="utf-8") as handle:
        for line in handle:
            saved = json.loads(line)
            letter = by_id[str(saved["letter_id"])]
            gold_in_order.append(letter)
            predictions.append(_rematerialize(letter, saved))

    extras = _gold_letter_sf_extras(gold_in_order, predictions)
    generic = [item for item in extras["items"] if item["extra_class"] == "generic_seizure_name"]
    letter_structure = _letter_structure(gold_in_order, predictions, generic)
    predicates = _predicate_review(generic, letter_structure)
    empty_gold = _empty_gold_slice(gold_in_order, predictions)
    v10_generic_ids, v10_generic_count = _v10_generic()
    v14_ids = {item["letter_id"] for item in generic}
    decision = {
        "status": "reject",
        "mechanism": "no_gold_free_generic_selection_predicate",
        "candidate_implemented": False,
        "candidate_identity": CANDIDATE_IDENTITY,
        "v10_generic_seizure_name": v10_generic_count,
        "v10_generic_letters": len(v10_generic_ids),
        "v14_generic_seizure_name": len(generic),
        "v14_generic_letters": sorted(v14_ids),
        "left_since_v10": sorted(v10_generic_ids - v14_ids),
        "new_since_v10": sorted(v14_ids - v10_generic_ids),
        "empty_gold_sf_extras": empty_gold["all140"]["mention_count"],
        "rest120_empty_gold_sf_extras": empty_gold["rest120"]["mention_count"],
        "predicates_considered": [row["name"] for row in predicates],
        "unsafe_reasons": [row["unsafe_reason"] for row in predicates],
    }
    artifact = {
        "schema_version": "exectv2.mention_unit_v2_generic_sel.dev140.v1",
        "status": "complete",
        "protocol": PROTOCOL,
        "split": "dev140",
        "row_count": len(predictions),
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "control": CONTROL,
        "candidate_identity": CANDIDATE_IDENTITY,
        "candidate_implemented": False,
        "gold_letter_sf_extras": extras,
        "generic_extras": generic,
        "letter_structure": letter_structure,
        "predicates_considered": predicates,
        "empty_gold_sf_extras": empty_gold,
        "v10_example_status": _example_status(generic, v14_ids),
        "decision": decision,
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "claim_boundary": (
            "GPT-5.6 Luna ExECT leftover-form generic-selection catalog on "
            "frozen mention-unit v2 dev140 hybrid raws. Not holdout, not a "
            "Decision 0050 change, and not selected-stack parity."
        ),
    }
    (STUDY_DIR / "catalog.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (STUDY_DIR / "comparison.json").write_text(
        json.dumps(
            {
                "schema_version": artifact["schema_version"],
                "status": "complete",
                "protocol": PROTOCOL,
                "control": CONTROL,
                "candidate_implemented": False,
                "decision": decision,
                "empty_gold_sf_extras": empty_gold,
                "model_calls": 0,
                "claim_boundary": artifact["claim_boundary"],
                "provenance": artifact["provenance"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    if not REPORT.exists():
        REPORT.write_text(_render_report(artifact), encoding="utf-8")
    print(json.dumps({"model_calls": 0, "decision": decision}, indent=2))


def _rematerialize(letter: ExectLetter, saved: dict[str, Any]) -> PredictedLetter:
    raw = str(saved["methods"][HYBRID_METHOD]["raw_output"])
    parsed = parse_mention_unit_json(raw, method=HYBRID_METHOD)
    if parsed.record is None:
        return PredictedLetter(letter_id=letter.letter_id, mentions=())
    materialized = materialize_mention_unit(
        letter,
        parsed.record,
        method=HYBRID_METHOD,
        encoder=CONTROL,
    )
    return materialized.prediction


def _gold_letter_sf_extras(
    gold: list[ExectLetter], predictions: list[PredictedLetter]
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for letter, prediction in zip(gold, predictions, strict=True):
        gold_sf = letter.entities("SeizureFrequency")
        if not gold_sf:
            continue
        gold_keys = Counter(frequency_state_keys(gold_sf, "clinical_headline"))
        pred_mentions = [
            mention for mention in prediction.mentions if mention.entity == "SeizureFrequency"
        ]
        pred_letter = to_exect_letter(prediction)
        pred_keys = Counter(
            frequency_state_keys(pred_letter.entities("SeizureFrequency"), "clinical_headline")
        )
        extra_keys = pred_keys - gold_keys
        if not extra_keys:
            continue
        for mention in pred_mentions:
            key = frequency_state_keys(
                to_exect_letter(
                    PredictedLetter(letter_id=prediction.letter_id, mentions=(mention,))
                ).entities("SeizureFrequency"),
                "clinical_headline",
            )
            if not key or key[0] not in extra_keys:
                continue
            items.append(
                {
                    "letter_id": letter.letter_id,
                    "clinical_name": mention.text,
                    "evidence": mention.evidence,
                    "state": frequency_state_faithful(mention.attributes or {}),
                    "extra_class": _gold_letter_extra_class(
                        mention.text, mention.evidence, mention.attributes
                    ),
                    "counted": _has_count(mention),
                    "generic": _fold_span(mention.text) in GENERIC_NAMES,
                    "key": key[0],
                    "slice": "dev20" if letter.letter_id in DEV20 else "rest120",
                }
            )
    return {
        "count": len(items),
        "class_counts": dict(Counter(item["extra_class"] for item in items)),
        "items": items,
    }


def _letter_structure(
    gold: list[ExectLetter],
    predictions: list[PredictedLetter],
    generic: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_id = {
        letter.letter_id: (letter, prediction)
        for letter, prediction in zip(gold, predictions, strict=True)
    }
    rows: list[dict[str, Any]] = []
    for letter_id in sorted({item["letter_id"] for item in generic}):
        letter, prediction = by_id[letter_id]
        pred_sf = [
            mention for mention in prediction.mentions if mention.entity == "SeizureFrequency"
        ]
        typed = [mention for mention in pred_sf if _fold_span(mention.text) not in GENERIC_NAMES]
        counted = [mention for mention in pred_sf if _has_count(mention)]
        extras = [item for item in generic if item["letter_id"] == letter_id]
        gold_names = [_fold_span(entity.text) for entity in letter.entities("SeizureFrequency")]
        rows.append(
            {
                "letter_id": letter_id,
                "slice": "dev20" if letter_id in DEV20 else "rest120",
                "pred_sf_count": len(pred_sf),
                "typed_present": bool(typed),
                "counted_present": bool(counted),
                "generic_only": bool(pred_sf) and not typed,
                "sole_generic": len(pred_sf) == 1
                and _fold_span(pred_sf[0].text) in GENERIC_NAMES,
                "gold_has_generic_or_freedom": any(
                    name in GOLD_GENERIC_OR_FREEDOM or name.startswith("seizure")
                    for name in gold_names
                ),
                "gold_names": gold_names,
                "typed_names": [mention.text for mention in typed],
                "extras": [
                    {
                        "clinical_name": item["clinical_name"],
                        "evidence": item["evidence"],
                        "state": item["state"],
                        "counted": item["counted"],
                    }
                    for item in extras
                ],
                "pred_mentions": [_mention_row(mention, extras) for mention in pred_sf],
            }
        )
    return rows


def _mention_row(mention: PredictedMention, extras: list[dict[str, Any]]) -> dict[str, Any]:
    extra = any(
        item["evidence"] == mention.evidence and item["clinical_name"] == mention.text
        for item in extras
    )
    return {
        "clinical_name": mention.text,
        "evidence": mention.evidence,
        "generic": _fold_span(mention.text) in GENERIC_NAMES,
        "counted": _has_count(mention),
        "state": frequency_state_faithful(mention.attributes or {}),
        "extra": extra,
    }


def _predicate_review(
    generic: list[dict[str, Any]], structure: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_id = {row["letter_id"]: row for row in structure}
    typed_drop_all = []
    typed_or_other_counted = []
    typed_drop_uncounted = []
    for item in generic:
        row = by_id[item["letter_id"]]
        if row["typed_present"]:
            typed_drop_all.append(item)
            if not item["counted"]:
                typed_drop_uncounted.append(item)
        other_counted = row["counted_present"] and not row["sole_generic"]
        if row["typed_present"] or other_counted:
            typed_or_other_counted.append(item)
    return [
        {
            "name": "typed_present_drop_all_generics",
            "would_drop": _drop_summary(typed_drop_all, by_id),
            "unsafe_reason": (
                "Drops EA0008 returned generic (gold FrequencyChange), "
                "EA0190 current seizure-free generic, and last-event "
                "generics on EA0137 / EA0186 that are gold units."
            ),
        },
        {
            "name": "typed_or_other_counted_drop_generics",
            "would_drop": _drop_summary(typed_or_other_counted, by_id),
            "unsafe_reason": (
                "Same typed-present injuries, plus historical-versus-current "
                "generic pairs (EA0142, EA0162) and uncounted generics on "
                "letters whose current mention is already a generic."
            ),
        },
        {
            "name": "typed_present_drop_uncounted_generics",
            "would_drop": _drop_summary(typed_drop_uncounted, by_id),
            "unsafe_reason": (
                "Keeps EA0008 because that extra is counted, but still drops "
                "last-event gold units on EA0137 and EA0186. Last-event v4 "
                "is banned; dropping those mentions is a current-unit loss."
            ),
        },
    ]


def _drop_summary(
    items: list[dict[str, Any]], structure: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    letters = sorted({item["letter_id"] for item in items})
    gold_unit_risk = [
        letter_id
        for letter_id in letters
        if structure[letter_id]["gold_has_generic_or_freedom"]
        or structure[letter_id]["sole_generic"]
    ]
    return {
        "extra_count": len(items),
        "letters": letters,
        "gold_unit_risk_letters": gold_unit_risk,
    }


def _empty_gold_slice(
    gold: list[ExectLetter], predictions: list[PredictedLetter]
) -> dict[str, Any]:
    rest_gold = [letter for letter in gold if letter.letter_id not in DEV20]
    rest_pred = [
        prediction
        for letter, prediction in zip(gold, predictions, strict=True)
        if letter.letter_id not in DEV20
    ]
    return {
        "all140": _empty_gold_sf_extras(gold, predictions),
        "rest120": _empty_gold_sf_extras(rest_gold, rest_pred),
    }


def _v10_generic() -> tuple[set[str], int]:
    catalog = json.loads(V10_CATALOG.read_text(encoding="utf-8"))
    items = [
        item
        for item in catalog["leftover_buckets"]["gold_letter_sf_extras"]["items"]
        if item.get("extra_class") == "generic_seizure_name"
    ]
    return {str(item["letter_id"]) for item in items}, len(items)


def _example_status(generic: list[dict[str, Any]], v14_ids: set[str]) -> list[dict[str, Any]]:
    remaining = {
        (item["letter_id"], item["evidence"])
        for item in generic
    }
    return [
        {
            "letter_id": letter_id,
            "still_generic_extra": letter_id in v14_ids,
        }
        for letter_id in V10_EXAMPLE_IDS
    ] + [
        {
            "letter_id": "remaining_evidence_count",
            "still_generic_extra": len(remaining),
        }
    ]


def _has_count(mention: PredictedMention) -> bool:
    return bool(COUNT_ATTRS & set((mention.attributes or {}).keys()))


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


def _render_report(artifact: dict[str, Any]) -> str:
    decision = artifact["decision"]
    return (
        "# ExECT leftover-form generic-`seizures` selection, "
        "mention-unit v2 `dev140`\n\n"
        f"Date: 2026-08-17  \n"
        f"Status: complete; **{decision['status']}**  \n"
        f"Protocol: [generic selection `dev140`]({Path(PROTOCOL).name})  \n"
        "Parent: [error analysis `dev140`]"
        "(mention_unit_v2_leftover_form_stack_error_analysis_luna_dev140_2026-08-17.md)\n\n"
        "`model_calls`: 0. Draft rendered by the catalog script. "
        "Replace with the inspected report.\n"
    )


if __name__ == "__main__":
    main()
