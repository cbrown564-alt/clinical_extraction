"""No-call catalog of leftover-form v14 empty-gold SeizureFrequency extras."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit import (
    HYBRID_METHOD,
    LLM_METHOD,
    MENTION_UNIT_PROMPT_VERSION,
    MentionUnitEncoder,
    materialize_mention_unit,
    parse_mention_unit_json,
)
from scripts.run_exectv2_mention_unit_v2_leftover_form_v3_luna_dev140 import (
    _form_census,
    _score_method,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/exectv2/"
    "mention_unit_v2_empty_gold_v14_luna_dev140_protocol_2026-08-17.md"
)
REPORT = ROOT / (
    "docs/research/exectv2/mention_unit_v2_empty_gold_v14_luna_dev140_2026-08-17.md"
)
SOURCE_ROWS = ROOT / "experiments/exectv2_mention_unit_v2_luna_dev140_20260816" / "rows.jsonl"
STUDY_DIR = (
    ROOT / "experiments/exectv2_mention_unit_v2_empty_gold_v14_luna_dev140_20260817"
)
ENCODER: MentionUnitEncoder = "leftover_form_span_fold_febrile_v14"
FAMILY = "SeizureFrequency"
PREDECLARED_EXTRAS = 54
SPAN_FOLD_LETTERS = frozenset({"EA0021", "EA0045", "EA0185"})
DROPPED_FEBRILE_LETTER = "EA0100"
DROPPED_FEBRILE_CUE = "at the ages of 3 and 5"
COUNT_ATTRS = {
    "LowerNumberOfSeizures",
    "NumberOfSeizures",
    "UpperNumberOfSeizures",
}
FREQUENCY_ATTRS = {
    "FrequencyChange",
    "LowerNumberOfSeizures",
    "MonthDate",
    "NumberOfSeizures",
    "NumberOfTimePeriods",
    "PointInTime",
    "TimePeriod",
    "TimeSince_or_TimeOfEvent",
    "UpperNumberOfSeizures",
    "YearDate",
}
FREQUENCY_WORD_RE = re.compile(
    r"\b(twice|couple|few|several|occasional|rare|frequent|week|month|year|"
    r"years|seizure[- ]free|not had|no further|stopped|times|episodes?|"
    r"last|ago|since|cluster|most days|developed|helped|collapse|"
    r"january|february|march|april|may|june|july|august|september|"
    r"october|november|december|further|previous|subsequent|never had|"
    r"no (?:focal|seizures?|absences?|events?))\b",
    re.IGNORECASE,
)
FEBRILE_RE = re.compile(r"\bfebrile\b|\bage of\b|\bat the ages?\b", re.IGNORECASE)


def main() -> None:
    if not SOURCE_ROWS.exists():
        raise SystemExit(f"missing saved raws: {SOURCE_ROWS}")
    letters = list(load_letters_for_split("dev"))
    if len(letters) != 140:
        raise SystemExit(f"expected 140 development letters, found {len(letters)}")
    by_id = {letter.letter_id: letter for letter in letters}
    empty_gold = {
        letter.letter_id for letter in letters if not letter.entities(FAMILY)
    }
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()

    rows: list[dict[str, Any]] = []
    gold_in_order: list[ExectLetter] = []
    predictions: dict[str, list[PredictedLetter]] = {"llm": [], ENCODER: []}
    with SOURCE_ROWS.open(encoding="utf-8") as handle:
        for line in handle:
            saved = json.loads(line)
            letter = by_id[str(saved["letter_id"])]
            gold_in_order.append(letter)
            row = _rematerialize_row(letter, saved)
            rows.append(row)
            predictions["llm"].append(
                PredictedLetter.model_validate(saved["methods"][LLM_METHOD]["prediction"])
            )
            predictions[ENCODER].append(
                PredictedLetter.model_validate(row["hybrid"][ENCODER]["prediction"])
            )

    scored = {name: _score_method(gold_in_order, preds) for name, preds in predictions.items()}
    form = {name: _form_census(preds) for name, preds in predictions.items()}
    extras = _catalog_extras(gold_in_order, predictions[ENCODER], empty_gold)
    named = _named_letters(extras)
    decision = _decision(scored, extras, named)
    artifact = {
        "schema_version": "exectv2.mention_unit_v2_empty_gold_v14.dev140.v1",
        "status": "complete",
        "protocol": PROTOCOL,
        "split": "dev140",
        "row_count": len(rows),
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "encoder": ENCODER,
        "empty_gold_sf_letters": len(empty_gold),
        "predeclared_extras": PREDECLARED_EXTRAS,
        "dropped_febrile_mention": {
            "letter_id": DROPPED_FEBRILE_LETTER,
            "cue": DROPPED_FEBRILE_CUE,
        },
        "methods": scored,
        "form_census": form,
        "letter_count": extras["letter_count"],
        "mention_count": extras["mention_count"],
        "class_counts": extras["class_counts"],
        "drop_reason_counts": extras["drop_reason_counts"],
        "same_evidence_copy": extras["same_evidence_copy"],
        "named_letters": named,
        "decision": decision,
        "extras": extras["items"],
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "claim_boundary": (
            "GPT-5.6 Luna ExECT leftover-form v14 empty-gold SeizureFrequency "
            "catalog on frozen mention-unit v2 dev140 hybrid raws. Not holdout, "
            "not a Decision 0050 change, and not a selected encoder."
        ),
    }
    (STUDY_DIR / "extras_catalog.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (STUDY_DIR / "comparison.json").write_text(
        json.dumps(
            {
                key: artifact[key]
                for key in (
                    "schema_version",
                    "status",
                    "protocol",
                    "split",
                    "row_count",
                    "model_calls",
                    "encoder",
                    "empty_gold_sf_letters",
                    "predeclared_extras",
                    "dropped_febrile_mention",
                    "methods",
                    "form_census",
                    "letter_count",
                    "mention_count",
                    "class_counts",
                    "drop_reason_counts",
                    "named_letters",
                    "decision",
                    "claim_boundary",
                    "started_utc",
                    "finished_utc",
                    "provenance",
                )
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    with (STUDY_DIR / "rows.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    if not REPORT.exists():
        REPORT.write_text(_render_draft(artifact), encoding="utf-8")
    print(
        json.dumps(
            {
                "model_calls": 0,
                "decision": decision,
                "mention_count": extras["mention_count"],
                "letter_count": extras["letter_count"],
                "class_counts": extras["class_counts"],
                "drop_reason_counts": extras["drop_reason_counts"],
                "named_letters": named,
            },
            indent=2,
        )
    )


def _rematerialize_row(letter: ExectLetter, saved: dict[str, Any]) -> dict[str, Any]:
    raw = str(saved["methods"][HYBRID_METHOD]["raw_output"])
    parsed = parse_mention_unit_json(raw, method=HYBRID_METHOD)
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
            encoder=ENCODER,
        )
        payload = {
            "semantic_facts": materialized.semantic_facts,
            "rule_trace": materialized.rule_trace,
            "warnings": materialized.warnings,
            "evidence_invalid": materialized.evidence_invalid,
            "prediction": materialized.prediction.model_dump(mode="json"),
        }
    return {
        "letter_id": letter.letter_id,
        "split": "dev140",
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "raw_output": raw,
        "parse_errors": parsed.errors,
        "hybrid": {ENCODER: payload},
        "llm_prediction": saved["methods"][LLM_METHOD]["prediction"],
    }


def _catalog_extras(
    gold: list[ExectLetter],
    predictions: list[PredictedLetter],
    empty_gold: set[str],
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    letters_with_extras: list[str] = []
    for letter, prediction in zip(gold, predictions, strict=True):
        if letter.letter_id not in empty_gold:
            continue
        mentions = [
            mention
            for mention in prediction.mentions
            if mention.entity == FAMILY
        ]
        if not mentions:
            continue
        letters_with_extras.append(letter.letter_id)
        evidence_counts = Counter(_norm(mention.evidence or "") for mention in mentions)
        for mention in mentions:
            attributes = dict(mention.attributes or {})
            evidence = mention.evidence or ""
            classified = _classify(mention.text, evidence, attributes)
            item = {
                "letter_id": letter.letter_id,
                "clinical_name": mention.text,
                "evidence": evidence,
                "attributes": attributes,
                "class": classified,
                "has_count": bool(COUNT_ATTRS.intersection(attributes)),
                "same_evidence_copy": evidence_counts[_norm(evidence)] > 1,
            }
            item["drop_reason"] = _drop_reason(item)
            items.append(item)
    class_counts = dict(Counter(item["class"] for item in items))
    drop_reason_counts = dict(Counter(item["drop_reason"] for item in items))
    return {
        "letter_count": len(letters_with_extras),
        "mention_count": len(items),
        "letters": letters_with_extras,
        "class_counts": class_counts,
        "drop_reason_counts": drop_reason_counts,
        "same_evidence_copy": sum(1 for item in items if item["same_evidence_copy"]),
        "items": items,
    }


def _classify(text: str, evidence: str, attributes: dict[str, Any]) -> str:
    haystack = f"{text} {evidence}"
    if FEBRILE_RE.search(haystack):
        return "remote_childhood"
    if FREQUENCY_ATTRS.intersection(attributes) or FREQUENCY_WORD_RE.search(haystack):
        return "frequency_statement"
    if text.strip():
        return "seizure_story"
    return "other"


def _drop_reason(item: dict[str, Any]) -> str:
    if item["letter_id"] in SPAN_FOLD_LETTERS:
        return "span_fold_casefold_side_effect"
    if item["has_count"]:
        return "counted_frequency_statement"
    if item["class"] == "remote_childhood":
        return "already_answered_remote_childhood"
    if item["class"] == "frequency_statement":
        return "already_answered_catalog_class"
    return "gold_free_drop_candidate"


def _named_letters(extras: dict[str, Any]) -> dict[str, Any]:
    by_letter: dict[str, list[dict[str, Any]]] = {}
    for item in extras["items"]:
        by_letter.setdefault(item["letter_id"], []).append(item)
    remaining = {
        letter_id: [
            {
                "clinical_name": item["clinical_name"],
                "evidence": item["evidence"],
                "has_count": item["has_count"],
                "class": item["class"],
                "drop_reason": item["drop_reason"],
            }
            for item in items
        ]
        for letter_id, items in by_letter.items()
        if letter_id in SPAN_FOLD_LETTERS
    }
    ea0100 = by_letter.get(DROPPED_FEBRILE_LETTER, [])
    febrile_still_present = any(
        DROPPED_FEBRILE_CUE.casefold() in item["evidence"].casefold() for item in ea0100
    )
    return {
        "ea0021_present": "EA0021" in by_letter,
        "ea0045_present": "EA0045" in by_letter,
        "ea0185_present": "EA0185" in by_letter,
        "ea0100_letter_still_has_extras": bool(ea0100),
        "ea0100_febrile_mention_absent": not febrile_still_present,
        "span_fold_letters": remaining,
    }


def _decision(
    scored: dict[str, dict[str, Any]],
    extras: dict[str, Any],
    named: dict[str, Any],
) -> dict[str, Any]:
    mention_count = extras["mention_count"]
    class_counts = extras["class_counts"]
    drop_reason_counts = extras["drop_reason_counts"]
    gold_free = drop_reason_counts.get("gold_free_drop_candidate", 0)
    three_remain = (
        named["ea0021_present"] and named["ea0045_present"] and named["ea0185_present"]
    )
    partitions = not class_counts.get("seizure_story") and not class_counts.get("other")
    if mention_count != PREDECLARED_EXTRAS or not three_remain or not partitions:
        status = "revise"
        mechanism = "empty_gold_v14_catalog_mismatch"
    elif gold_free:
        status = "answer"
        mechanism = "unexpected_gold_free_drop"
    else:
        status = "reject"
        mechanism = "remaining_empty_gold_extras_are_counted_or_already_answered"
    return {
        "status": status,
        "mechanism": mechanism,
        "do_not_test_encoder_change": status != "answer",
        "mention_count": mention_count,
        "letter_count": extras["letter_count"],
        "predeclared_extras": PREDECLARED_EXTRAS,
        "three_span_fold_letters_remain": three_remain,
        "ea0100_febrile_mention_absent": named["ea0100_febrile_mention_absent"],
        "partitions": partitions,
        "gold_free_drop_candidates": gold_free,
        "class_counts": class_counts,
        "drop_reason_counts": drop_reason_counts,
        "candidate_headline_140": scored[ENCODER]["clinical_headline_f1"],
        "candidate_sf_140": scored[ENCODER]["clinical_headline_family_f1"]["SeizureFrequency"],
        "empty_gold_sf_extras": scored[ENCODER]["empty_gold_sf_extras"]["mention_count"],
        "saved_llm_empty_gold_sf_extras": scored["llm"]["empty_gold_sf_extras"][
            "mention_count"
        ],
    }


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


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


def _render_draft(artifact: dict[str, Any]) -> str:
    decision = artifact["decision"]
    return (
        "# ExECT leftover-form v14 empty-gold SF extras, mention-unit v2 `dev140`\n\n"
        f"Date: 2026-08-17  \n"
        f"Status: complete; **{decision['status']}**  \n"
        f"Protocol: [empty-gold v14 `dev140`]({Path(PROTOCOL).name})  \n"
        "Parent: [febrile widen `dev140`]"
        "(mention_unit_v2_febrile_widen_luna_dev140_2026-08-17.md)\n\n"
        "`model_calls`: 0. Draft rendered by the catalog script. "
        "Replace with the inspected report.\n"
    )


if __name__ == "__main__":
    main()
