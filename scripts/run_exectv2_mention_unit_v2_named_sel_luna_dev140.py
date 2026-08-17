"""No-call catalog of remaining named-type extras on febrile v14."""

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
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters_for_split
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
from scripts.run_exectv2_mention_unit_v2_luna import DEV20_IDS

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/exectv2/"
    "mention_unit_v2_named_sel_luna_dev140_protocol_2026-08-17.md"
)
SOURCE_ROWS = ROOT / "experiments/exectv2_mention_unit_v2_luna_dev140_20260816" / "rows.jsonl"
STUDY_DIR = ROOT / "experiments/exectv2_mention_unit_v2_named_sel_luna_dev140_20260817"
CONTROL = "leftover_form_span_fold_febrile_v14"
DEV20 = frozenset(DEV20_IDS)
_HISTORY_RE = re.compile(
    r"\b(?:childhood|febrile|family history|teenage|teens|adolescence|"
    r"school years|at the age of)\b",
    re.I,
)
_NEGATION_RE = re.compile(
    r"\b(?:has|have|had)\s+not\b|\bno\s+(?:events?|seizures?|absences?)\b|"
    r"\bnot\s+had\b|\bnever\b|\bdenied\b",
    re.I,
)
# Inspection labels only. Not a drop predicate.
_INSPECTED: tuple[tuple[str, str, str, str], ...] = (
    ("EA0005", "Previous event December 2015", "last_event", "dated_previous_event"),
    ("EA0006", "he remains seizure free", "seizure_free_state", "seizure_free_name"),
    ("EA0009", "bilateral convulsive seizure", "current_but_not_gold", "cluster_phenomenology"),
    ("EA0011", "year of his diagnosis", "old_type", "historical_rate_at_diagnosis"),
    ("EA0011", "last one being around Christmas", "last_event", "dated_last_one"),
    ("EA0022", "completely under control", "current_but_not_gold", "controlled_plus_dose"),
    ("EA0034", "convulsive seizure 2019", "calendar_date_false_read", "year_as_count"),
    ("EA0047", "absences and jerks", "current_but_not_gold", "joined_name"),
    ("EA0057", "used to gets these every month", "old_type", "historical_monthly_rate"),
    ("EA0057", "last one was on Christmas day 2009", "last_event", "dated_last_one"),
    ("EA0057", "dissociative seizures around twice", "current_but_not_gold", "type_not_in_gold"),
    ("EA0075", "two unprovoked generalised seizures", "old_type", "onset_history"),
    ("EA0132", "They are happening weekly", "current_but_not_gold", "current_name_mismatch"),
    ("EA0132", "only ever had one", "last_event", "lifetime_single"),
    ("EA0133", "before the carbamazepine", "old_type", "historical_rate_before_rx"),
    ("EA0143", "used to happen weekly", "last_event", "remote_last_event_zero"),
    ("EA0143", "last event was more than five years", "last_event", "remote_last_event_zero"),
    ("EA0143", "only every had one secondarily", "last_event", "lifetime_single"),
    ("EA0169", "Last week she had around 10-15", "current_but_not_gold", "cluster_name_mismatch"),
    ("EA0181", "Last week she had around 10-15", "current_but_not_gold", "cluster_name_mismatch"),
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
    extras: list[dict[str, Any]] = []
    empty_gold_mentions = 0
    empty_gold_letters: set[str] = set()
    with SOURCE_ROWS.open(encoding="utf-8") as handle:
        for line in handle:
            saved = json.loads(line)
            letter = by_id[str(saved["letter_id"])]
            prediction = _rematerialize(letter, saved)
            gold = letter.entities("SeizureFrequency")
            pred_mentions = [
                mention
                for mention in prediction.mentions
                if mention.entity == "SeizureFrequency"
            ]
            if not gold:
                if pred_mentions:
                    empty_gold_letters.add(letter.letter_id)
                    empty_gold_mentions += len(pred_mentions)
                continue
            extras.extend(_gold_letter_extras(letter, prediction, gold, pred_mentions))
    named = [item for item in extras if item["extra_class"] == "named_type_or_state_extra"]
    unlabeled = [item for item in named if item["inspected_subclass"] == "unlabeled"]
    if unlabeled:
        raise SystemExit(f"unlabeled named extras: {unlabeled}")
    subclass_counts = dict(Counter(item["inspected_subclass"] for item in named))
    decision = {
        "status": "reject",
        "mechanism": "named_type_extras_mixed_no_shared_drop",
        "named_type_or_state_extra_v14": len(named),
        "named_type_or_state_extra_v10": 18,
        "inspected_subclass_counts": subclass_counts,
        "empty_gold_sf_extras": empty_gold_mentions,
        "empty_gold_sf_extra_letters": len(empty_gold_letters),
        "control_empty_gold_sf_extras": 54,
        "implemented_encoder": None,
        "predicate_tested": None,
    }
    artifact = {
        "schema_version": "exectv2.mention_unit_v2_named_sel.dev140.v1",
        "status": "complete",
        "protocol": PROTOCOL,
        "split": "dev140",
        "row_count": 140,
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "control": CONTROL,
        "candidate": None,
        "gold_letter_extra_class_counts": dict(Counter(item["extra_class"] for item in extras)),
        "named_type_or_state_extra": {
            "count": len(named),
            "v10_count": 18,
            "inspected_subclass_counts": subclass_counts,
            "items": named,
        },
        "empty_gold_sf_extras": {
            "mention_count": empty_gold_mentions,
            "letter_count": len(empty_gold_letters),
            "letters": sorted(empty_gold_letters),
        },
        "decision": decision,
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "claim_boundary": (
            "GPT-5.6 Luna ExECT leftover-form named-type extra catalog on "
            "frozen mention-unit v2 dev140 hybrid raws. Not holdout, not a "
            "Decision 0050 change, and not selected-stack parity."
        ),
    }
    (STUDY_DIR / "catalog.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    scratch = STUDY_DIR / "_catalog_v14_named.py"
    if scratch.exists():
        scratch.unlink()
    print(json.dumps({"model_calls": 0, "decision": decision}, indent=2))


def _rematerialize(letter: Any, saved: dict[str, Any]) -> PredictedLetter:
    raw = str(saved["methods"][HYBRID_METHOD]["raw_output"])
    parsed = parse_mention_unit_json(raw, method=HYBRID_METHOD)
    if parsed.record is None:
        return PredictedLetter(letter_id=letter.letter_id, mentions=())
    return materialize_mention_unit(
        letter,
        parsed.record,
        method=HYBRID_METHOD,
        encoder=CONTROL,
    ).prediction


def _gold_letter_extras(
    letter: Any,
    prediction: PredictedLetter,
    gold: Any,
    pred_mentions: list[Any],
) -> list[dict[str, Any]]:
    gold_keys = Counter(frequency_state_keys(gold, "clinical_headline"))
    pred_letter = to_exect_letter(prediction)
    pred_keys = Counter(
        frequency_state_keys(pred_letter.entities("SeizureFrequency"), "clinical_headline")
    )
    extra_keys = pred_keys - gold_keys
    if not extra_keys:
        return []
    gold_units = [
        {
            "text": entity.text,
            "state": frequency_state_faithful(entity.attributes or {}),
        }
        for entity in gold
    ]
    items: list[dict[str, Any]] = []
    for mention in pred_mentions:
        key = frequency_state_keys(
            to_exect_letter(
                PredictedLetter(letter_id=prediction.letter_id, mentions=(mention,))
            ).entities("SeizureFrequency"),
            "clinical_headline",
        )
        if not key or key[0] not in extra_keys:
            continue
        extra_class = _gold_letter_extra_class(
            mention.text, mention.evidence, mention.attributes
        )
        subclass, note = _inspected_subclass(letter.letter_id, mention.evidence)
        items.append(
            {
                "letter_id": letter.letter_id,
                "clinical_name": mention.text,
                "evidence": mention.evidence,
                "state": frequency_state_faithful(mention.attributes or {}),
                "extra_class": extra_class,
                "inspected_subclass": subclass,
                "inspection_note": note,
                "gold_units": gold_units,
                "slice": "dev20" if letter.letter_id in DEV20 else "rest120",
            }
        )
    return items


def _gold_letter_extra_class(
    text: str, evidence: str, attributes: dict[str, str] | None
) -> str:
    haystack = f"{text} {evidence}"
    if "febrile" in _fold_span(text):
        return "febrile_history"
    if _HISTORY_RE.search(haystack):
        return "remote_history"
    if _NEGATION_RE.search(haystack) and not (attributes or {}).get("NumberOfSeizures") == "0":
        return "negated_or_unused_type"
    if _fold_span(text) in {"seizure", "seizures"}:
        return "generic_seizure_name"
    if frequency_state_faithful(attributes or {}) == "unknown":
        return "unknown_state_name"
    return "named_type_or_state_extra"


def _inspected_subclass(letter_id: str, evidence: str) -> tuple[str, str]:
    haystack = evidence.casefold()
    for item_id, cue, subclass, note in _INSPECTED:
        if item_id == letter_id and cue.casefold() in haystack:
            return subclass, note
    return "unlabeled", ""


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
