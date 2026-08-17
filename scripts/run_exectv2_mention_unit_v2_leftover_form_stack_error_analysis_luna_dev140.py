"""No-call leftover catalog of stacked leftover-form on saved dev140 raws."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from collections.abc import Hashable, Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.core.scoring import multiset_prf1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit import (
    _fold_span,
    _span_in_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    concept_keys,
    frequency_state_faithful,
    frequency_state_keys,
    investigation_component_keys,
    prescription_component_keys,
    score_concept_identity,
    score_frequency_state,
    score_investigations_components,
    score_prescription_components,
)
from scripts.run_exectv2_mention_unit_v2_leftover_form_v3_luna_dev140 import (
    _catalog,
    _form_census,
)
from scripts.run_exectv2_mention_unit_v2_luna import DEV20_IDS

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/exectv2/"
    "mention_unit_v2_leftover_form_stack_error_analysis_luna_dev140_protocol_2026-08-17.md"
)
STUDY_DIR = (
    ROOT / "experiments/exectv2_mention_unit_v2_leftover_form_stack_luna_dev140_20260817"
)
ROWS = STUDY_DIR / "rows.jsonl"
OUT = STUDY_DIR / "error_analysis.json"
CANDIDATE = "leftover_form_span_fold_fortnight_v10"
FORM = "leftover_form_intervening_v3"
CONTROL = "landed"
FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")
DEV20 = frozenset(DEV20_IDS)
COUNT_ATTRS = {
    "LowerNumberOfSeizures",
    "NumberOfSeizures",
    "UpperNumberOfSeizures",
}
_DATE_RE = re.compile(
    r"\b(?:january|february|march|april|may|june|july|august|september|"
    r"october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec|"
    r"\d{1,2}\s+(?:january|february|march|april|may|june|july|august|"
    r"september|october|november|december))\b",
    re.I,
)
_AGE_RE = re.compile(r"\bage(?:\s+of)?\b", re.I)
_DURATION_RE = re.compile(
    r"\b(?:for|ago|since|without having|now for around)\b.{0,24}"
    r"(?:day|week|month|year)s?\b|"
    r"\b(?:day|week|month|year)s?\s+ago\b",
    re.I,
)
_QUALITATIVE_RE = re.compile(
    r"\b(?:worse|better|improved|deteriorat|quite a number|several|"
    r"multiple|a few|a couple|occasional|frequent|infrequent|rare|"
    r"well[- ]managed|controlled|ongoing|continues|returned|recurrent)\b",
    re.I,
)
_LAST_EVENT_RE = re.compile(
    r"\b(?:last (?:seizure|event|month|week|year)|no further|none since|"
    r"not had any|seizure[- ]free|no seizures?|no absences|no events?)\b",
    re.I,
)
_RISK_RE = re.compile(r"\b(?:risk|possibility|likely to|may have)\b", re.I)
_COLLAPSE_RE = re.compile(r"\bcollapse\b", re.I)
_CHANGE_RE = re.compile(
    r"\b(?:increased|decreased|more|fewer|less|same|unchanged)\b", re.I
)
_IMPLICIT_PERIOD_RE = re.compile(
    r"\b(?:daily|weekly|monthly|yearly|on a weekly basis|"
    r"every\s+(?:day|week|month|year)s?|happening weekly)\b",
    re.I,
)
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


def main() -> None:
    if not ROWS.exists():
        raise SystemExit(f"missing remasure rows: {ROWS}")
    letters = list(load_letters_for_split("dev"))
    if len(letters) != 140:
        raise SystemExit(f"expected 140 development letters, found {len(letters)}")
    by_id = {letter.letter_id: letter for letter in letters}
    started = datetime.now(UTC).isoformat()
    rows: list[dict[str, Any]] = []
    gold_in_order: list[ExectLetter] = []
    predictions: dict[str, list[PredictedLetter]] = {
        name: [] for name in ("llm", CONTROL, FORM, CANDIDATE)
    }
    with ROWS.open(encoding="utf-8") as handle:
        for line in handle:
            saved = json.loads(line)
            letter = by_id[str(saved["letter_id"])]
            gold_in_order.append(letter)
            rows.append(saved)
            predictions["llm"].append(
                PredictedLetter.model_validate(saved["llm_prediction"])
            )
            for encoder in (CONTROL, FORM, CANDIDATE):
                predictions[encoder].append(
                    PredictedLetter.model_validate(
                        saved["hybrid"][encoder]["prediction"]
                    )
                )
    catalogs = {encoder: _catalog(rows, encoder=encoder) for encoder in (CONTROL, FORM, CANDIDATE)}
    leftover = _leftover_buckets(rows, by_id, catalogs[CANDIDATE])
    family_gaps = {
        encoder: _family_gaps(gold_in_order, predictions[encoder])
        for encoder in ("llm", CONTROL, FORM, CANDIDATE)
    }
    letter_modes = _letter_modes(gold_in_order, predictions[CANDIDATE])
    next_rules = _rank_next_rules(leftover, family_gaps[CANDIDATE], letter_modes)
    artifact = {
        "schema_version": "exectv2.mention_unit_v2_leftover_form_stack.error_analysis.v1",
        "status": "complete",
        "protocol": PROTOCOL,
        "split": "dev140",
        "row_count": len(rows),
        "model_calls": 0,
        "candidate": CANDIDATE,
        "control": CONTROL,
        "form_context": FORM,
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "claim_boundary": (
            "GPT-5.6 Luna ExECT leftover-form stacked-encoder error catalog "
            "on frozen mention-unit v2 dev140 hybrid raws. Not holdout, not a "
            "Decision 0050 change, and not selected-stack parity."
        ),
        "catalog_summary": {
            encoder: catalog["class_counts"] for encoder, catalog in catalogs.items()
        },
        "form_census": {
            encoder: _form_census(predictions[encoder])
            for encoder in ("llm", CONTROL, FORM, CANDIDATE)
        },
        "family_gaps": family_gaps,
        "leftover_buckets": leftover,
        "letter_modes": letter_modes,
        "next_rules": next_rules,
    }
    OUT.write_text(json.dumps(artifact, indent=2, default=_json_default) + "\n", encoding="utf-8")
    print(json.dumps({"artifact": str(OUT), "next_rules": next_rules}, indent=2, default=_json_default))


def _family_gaps(
    gold: list[ExectLetter], predictions: list[PredictedLetter]
) -> dict[str, Any]:
    pred_letters = [to_exect_letter(prediction) for prediction in predictions]
    out: dict[str, Any] = {}
    for family in FAMILIES:
        gold_keys: list[Hashable] = []
        pred_keys: list[Hashable] = []
        misses: list[dict[str, Any]] = []
        extras: list[dict[str, Any]] = []
        for letter, pred in zip(gold, pred_letters, strict=True):
            g_keys = _family_keys(family, letter.entities(family), letter.note_text)
            p_keys = _family_keys(family, pred.entities(family), letter.note_text)
            gold_keys.extend(g_keys)
            pred_keys.extend(p_keys)
            g_count = Counter(g_keys)
            p_count = Counter(p_keys)
            for key, count in (g_count - p_count).items():
                misses.append(
                    {
                        "letter_id": letter.letter_id,
                        "key": key,
                        "count": count,
                        "slice": "dev20" if letter.letter_id in DEV20 else "rest120",
                    }
                )
            for key, count in (p_count - g_count).items():
                extras.append(
                    {
                        "letter_id": letter.letter_id,
                        "key": key,
                        "count": count,
                        "empty_gold": not bool(letter.entities(family)),
                        "slice": "dev20" if letter.letter_id in DEV20 else "rest120",
                    }
                )
        scores = _family_score(family, gold, pred_letters)
        out[family] = {
            "tp": scores.tp,
            "fp": scores.fp,
            "fn": scores.fn,
            "f1": round(scores.f1, 4),
            "gold_units": len(gold_keys),
            "pred_units": len(pred_keys),
            "miss_count": sum(item["count"] for item in misses),
            "extra_count": sum(item["count"] for item in extras),
            "empty_gold_extra_count": sum(
                item["count"] for item in extras if item["empty_gold"]
            ),
            "gold_letter_extra_count": sum(
                item["count"] for item in extras if not item["empty_gold"]
            ),
            "miss_key_counts": _key_counts(misses),
            "extra_key_counts": _key_counts(extras),
            "misses": misses,
            "extras": extras,
        }
    return out


def _family_keys(family: str, annotations: Iterable[Any], note_text: str) -> list[Hashable]:
    if family == "Diagnosis":
        return concept_keys(annotations, "Diagnosis", "concept")
    if family == "SeizureFrequency":
        return frequency_state_keys(annotations, "clinical_headline")
    if family == "Prescription":
        return prescription_component_keys(annotations, "clinical_headline", note_text)
    return investigation_component_keys(annotations, "clinical_headline")


def _family_score(family: str, gold: list[ExectLetter], pred: list[ExectLetter]) -> Any:
    if family == "Diagnosis":
        return score_concept_identity(gold, pred, "Diagnosis").concept_only
    if family == "SeizureFrequency":
        return score_frequency_state(gold, pred).clinical_headline
    if family == "Prescription":
        return score_prescription_components(gold, pred).clinical_headline
    return score_investigations_components(gold, pred).clinical_headline


def _leftover_buckets(
    rows: list[dict[str, Any]],
    letters: dict[str, ExectLetter],
    catalog: dict[str, Any],
) -> dict[str, Any]:
    items_by_class: dict[str, list[dict[str, Any]]] = {}
    for item in catalog["items"]:
        items_by_class.setdefault(item["class"], []).append(item)
    drops = [_classify_drop(item, letters[item["letter_id"]]) for item in items_by_class.get("text_not_substring_drop", [])]
    unparsed = [
        _classify_unparsed(item, letters[item["letter_id"]])
        for item in items_by_class.get("count_unparsed", [])
    ]
    suppressions = [
        _classify_suppression(item, letters[item["letter_id"]])
        for item in items_by_class.get("suppress_uncoded_sf", [])
    ]
    unknown = items_by_class.get("result_unknown", [])
    rewrites = items_by_class.get("name_rewritten", [])
    warning_drops = _warning_drops(rows, letters)
    gold_letter_sf_extras = _gold_letter_sf_extras(rows, letters)
    return {
        "text_not_substring_drop": {
            "count": len(drops),
            "class_counts": dict(Counter(item["drop_class"] for item in drops)),
            "items": drops,
        },
        "count_unparsed": {
            "count": len(unparsed),
            "class_counts": dict(Counter(item["unparsed_class"] for item in unparsed)),
            "do_not_parse_count": sum(1 for item in unparsed if item["do_not_parse"]),
            "items": unparsed,
        },
        "suppress_uncoded_sf": {
            "count": len(suppressions),
            "class_counts": dict(Counter(item["suppress_class"] for item in suppressions)),
            "items": suppressions,
        },
        "result_unknown": {"count": len(unknown), "items": unknown},
        "name_rewritten": {"count": len(rewrites), "items": rewrites},
        "warning_drops": warning_drops,
        "gold_letter_sf_extras": gold_letter_sf_extras,
    }


def _classify_drop(item: dict[str, Any], letter: ExectLetter) -> dict[str, Any]:
    name = str(item.get("clinical_name") or "")
    folded = _fold_span(name)
    in_letter_exact = _span_in_letter(letter.note_text, name, mode="exact")
    in_letter_fold = _span_in_letter(letter.note_text, name, mode="span_fold")
    singular = _singularize(folded)
    in_letter_singular = singular != folded and singular in _fold_span(letter.note_text)
    gold_sf = [ann.text for ann in letter.entities("SeizureFrequency")]
    gold_dx = [ann.text for ann in letter.entities("Diagnosis")]
    drop_class = "paraphrase_absent"
    if in_letter_fold:
        drop_class = "should_have_passed_span_fold"
    elif in_letter_singular:
        drop_class = "singular_plural"
    elif any(_fold_span(text) == folded for text in gold_sf):
        drop_class = "gold_sf_wording_absent_from_letter"
    elif any(_fold_span(text) == folded for text in gold_dx):
        drop_class = "diagnosis_name_as_sf"
    elif "jerk" in folded or "myoclon" in folded:
        drop_class = "phenomenology_paraphrase"
    elif folded.endswith("seizure") or folded.endswith("seizures"):
        drop_class = "seizure_name_paraphrase"
    return {
        **item,
        "drop_class": drop_class,
        "in_letter_exact": in_letter_exact,
        "in_letter_fold": in_letter_fold,
        "in_letter_singular": in_letter_singular,
        "empty_gold_sf": not bool(letter.entities("SeizureFrequency")),
        "gold_sf": gold_sf,
        "slice": "dev20" if letter.letter_id in DEV20 else "rest120",
    }


def _classify_unparsed(item: dict[str, Any], letter: ExectLetter) -> dict[str, Any]:
    haystack = f"{item.get('clinical_name') or ''} {item.get('evidence') or ''}"
    unparsed_class = "no_count_language"
    do_not_parse = False
    if _DATE_RE.search(haystack) and re.search(r"\b\d{1,2}\b", haystack):
        unparsed_class = "calendar_date"
        do_not_parse = True
    elif _IMPLICIT_PERIOD_RE.search(haystack):
        unparsed_class = "implicit_period"
    elif _COLLAPSE_RE.search(haystack):
        unparsed_class = "collapse"
        do_not_parse = True
    elif _RISK_RE.search(haystack):
        unparsed_class = "risk_sentence"
        do_not_parse = True
    elif _AGE_RE.search(haystack):
        unparsed_class = "age"
        do_not_parse = True
    elif re.search(r"\bquite a number\b", haystack, re.I):
        unparsed_class = "quite_a_number"
        do_not_parse = True
    elif _DURATION_RE.search(haystack) and _LAST_EVENT_RE.search(haystack):
        unparsed_class = "last_event_duration"
        do_not_parse = True
    elif _LAST_EVENT_RE.search(haystack):
        unparsed_class = "last_event_or_zero"
    elif _DURATION_RE.search(haystack):
        unparsed_class = "duration_or_ago"
        do_not_parse = True
    elif _CHANGE_RE.search(haystack) or re.search(r"\bworse\b", haystack, re.I):
        unparsed_class = "qualitative_change"
        do_not_parse = unparsed_class == "qualitative_change" and bool(
            re.search(r"\bworse\b", haystack, re.I)
        )
    elif _QUALITATIVE_RE.search(haystack):
        unparsed_class = "qualitative_or_vague"
    elif re.search(r"\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b", haystack, re.I):
        unparsed_class = "digit_or_word_present"
    return {
        **item,
        "unparsed_class": unparsed_class,
        "do_not_parse": do_not_parse,
        "empty_gold_sf": not bool(letter.entities("SeizureFrequency")),
        "slice": "dev20" if letter.letter_id in DEV20 else "rest120",
    }


def _classify_suppression(item: dict[str, Any], letter: ExectLetter) -> dict[str, Any]:
    name = _fold_span(str(item.get("clinical_name") or ""))
    gold_sf = [_fold_span(ann.text) for ann in letter.entities("SeizureFrequency")]
    suppress_class = "uncoded_phenomenology"
    if name in gold_sf or any(name and name in gold_name for gold_name in gold_sf):
        suppress_class = "gold_sf_name_suppressed"
    elif "absence" in name:
        suppress_class = "absences_not_in_phrase_list"
    return {
        **item,
        "suppress_class": suppress_class,
        "matches_gold_sf": name in gold_sf,
        "empty_gold_sf": not bool(letter.entities("SeizureFrequency")),
        "slice": "dev20" if letter.letter_id in DEV20 else "rest120",
    }


def _warning_drops(
    rows: list[dict[str, Any]], letters: dict[str, ExectLetter]
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for row in rows:
        hybrid = row["hybrid"][CANDIDATE]
        warnings = hybrid.get("warnings") or []
        facts = hybrid.get("semantic_facts") or []
        letter = letters[row["letter_id"]]
        for fact in facts:
            index = fact.get("fact_index")
            warning = next(
                (
                    flag
                    for flag in (
                        "childhood_febrile_history",
                        "negated_unused_type",
                        "text_not_substring",
                        "evidence_not_substring",
                    )
                    if f"item[{index}]: {flag}" in warnings
                ),
                "",
            )
            if not warning:
                continue
            items.append(
                {
                    "letter_id": row["letter_id"],
                    "warning": warning,
                    "clinical_name": fact.get("clinical_name") or fact.get("text"),
                    "evidence": fact.get("evidence"),
                    "family": fact.get("family"),
                    "empty_gold_sf": not bool(letter.entities("SeizureFrequency")),
                    "slice": "dev20" if row["letter_id"] in DEV20 else "rest120",
                }
            )
    return {
        "count": len(items),
        "class_counts": dict(Counter(item["warning"] for item in items)),
        "items": items,
    }


def _gold_letter_sf_extras(
    rows: list[dict[str, Any]], letters: dict[str, ExectLetter]
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for row, prediction in (
        (
            row,
            PredictedLetter.model_validate(row["hybrid"][CANDIDATE]["prediction"]),
        )
        for row in rows
    ):
        letter = letters[row["letter_id"]]
        gold = letter.entities("SeizureFrequency")
        if not gold:
            continue
        gold_keys = Counter(frequency_state_keys(gold, "clinical_headline"))
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
            extra_class = _gold_letter_extra_class(mention.text, mention.evidence, mention.attributes)
            items.append(
                {
                    "letter_id": row["letter_id"],
                    "clinical_name": mention.text,
                    "evidence": mention.evidence,
                    "state": frequency_state_faithful(mention.attributes or {}),
                    "extra_class": extra_class,
                    "key": key[0],
                    "slice": "dev20" if row["letter_id"] in DEV20 else "rest120",
                }
            )
    return {
        "count": len(items),
        "class_counts": dict(Counter(item["extra_class"] for item in items)),
        "items": items,
    }


def _gold_letter_extra_class(text: str, evidence: str, attributes: dict[str, str] | None) -> str:
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


def _letter_modes(
    gold: list[ExectLetter], predictions: list[PredictedLetter]
) -> dict[str, Any]:
    pred_letters = [to_exect_letter(prediction) for prediction in predictions]
    modes: dict[str, list[str]] = {
        "exact_all_families": [],
        "sf_miss_only": [],
        "sf_extra_only": [],
        "sf_mixed": [],
        "dx_gap": [],
        "rx_gap": [],
        "ix_gap": [],
    }
    per_letter: list[dict[str, Any]] = []
    for letter, pred in zip(gold, pred_letters, strict=True):
        family_prf = {}
        for family in FAMILIES:
            g_keys = _family_keys(family, letter.entities(family), letter.note_text)
            p_keys = _family_keys(family, pred.entities(family), letter.note_text)
            score = multiset_prf1(g_keys, p_keys)
            family_prf[family] = {
                "tp": score.tp,
                "fp": score.fp,
                "fn": score.fn,
                "f1": round(score.f1, 4),
            }
        exact = all(family_prf[family]["fn"] == 0 and family_prf[family]["fp"] == 0 for family in FAMILIES)
        sf = family_prf["SeizureFrequency"]
        if exact:
            modes["exact_all_families"].append(letter.letter_id)
        elif sf["fn"] and not sf["fp"] and all(
            family_prf[family]["fn"] == 0 and family_prf[family]["fp"] == 0
            for family in FAMILIES
            if family != "SeizureFrequency"
        ):
            modes["sf_miss_only"].append(letter.letter_id)
        elif sf["fp"] and not sf["fn"] and all(
            family_prf[family]["fn"] == 0 and family_prf[family]["fp"] == 0
            for family in FAMILIES
            if family != "SeizureFrequency"
        ):
            modes["sf_extra_only"].append(letter.letter_id)
        elif sf["fn"] or sf["fp"]:
            modes["sf_mixed"].append(letter.letter_id)
        if family_prf["Diagnosis"]["fn"] or family_prf["Diagnosis"]["fp"]:
            modes["dx_gap"].append(letter.letter_id)
        if family_prf["Prescription"]["fn"] or family_prf["Prescription"]["fp"]:
            modes["rx_gap"].append(letter.letter_id)
        if family_prf["Investigations"]["fn"] or family_prf["Investigations"]["fp"]:
            modes["ix_gap"].append(letter.letter_id)
        per_letter.append(
            {
                "letter_id": letter.letter_id,
                "slice": "dev20" if letter.letter_id in DEV20 else "rest120",
                "exact": exact,
                "families": family_prf,
            }
        )
    return {
        "mode_counts": {name: len(ids) for name, ids in modes.items()},
        "modes": modes,
        "letters": per_letter,
    }


def _rank_next_rules(
    leftover: dict[str, Any],
    family_gaps: dict[str, Any],
    letter_modes: dict[str, Any],
) -> list[dict[str, Any]]:
    drop_counts = leftover["text_not_substring_drop"]["class_counts"]
    unparsed_counts = leftover["count_unparsed"]["class_counts"]
    extra_counts = leftover["gold_letter_sf_extras"]["class_counts"]
    suppress_counts = leftover["suppress_uncoded_sf"]["class_counts"]
    rules = [
        {
            "rank": 1,
            "rule": "implicit_period_v4_on_stack",
            "status": "test_next",
            "reason": (
                "Nine remaining unparsed mentions already use daily, weekly, "
                "every month, or every year. Implicit period v4 answered that "
                "contract on leftover-form v3 and was not stacked. Test it "
                "alone on leftover_form_span_fold_fortnight_v10. Do not bundle "
                "last-event v4."
            ),
            "support": unparsed_counts.get("implicit_period", 0),
        },
        {
            "rank": 2,
            "rule": "absences_keep_when_leftover_form_can_attach",
            "status": "test_next",
            "reason": (
                "Six of seven suppressions are absences. absences is not in "
                "the leftover-form phrase list, so leftover-form never runs. "
                "Keep absences unless the evidence is a negated-history "
                "sentence (EA0128). Do not keep drop attacks."
            ),
            "support": suppress_counts.get("absences_not_in_phrase_list", 0)
            + suppress_counts.get("gold_sf_name_suppressed", 0),
        },
        {
            "rank": 3,
            "rule": "childhood_febrile_predicate_widen",
            "status": "test_next",
            "reason": (
                "The age-of drop already fired on seven rows. Two febrile "
                "extras remain because the cue is 'the age of' without 'at' "
                "(EA0125) or 'between the ages of' (EA0190)."
            ),
            "support": extra_counts.get("febrile_history", 0),
        },
        {
            "rank": 4,
            "rule": "empty_gold_casefold_keep_gate",
            "status": "do_not_test",
            "reason": (
                "The extras rise is the leftover-form v2 casefold side effect "
                "(EA0021, EA0045, EA0185). Those recovered names already have "
                "counts. The stack protocol forbids retuning span-fold from "
                "those three letters."
            ),
            "support": 3,
        },
        {
            "rank": 5,
            "rule": "last_event_zero_without_v4_once_false_read",
            "status": "hold",
            "reason": (
                "Last-event language remains in count_unparsed, but last-event "
                "v4 revised because Once commenced became 1. Do not reopen."
            ),
            "support": unparsed_counts.get("last_event_or_zero", 0),
        },
        {
            "rank": 6,
            "rule": "qualitative_change_or_vague_count",
            "status": "do_not_test",
            "reason": (
                "worse, quite a number, collapse, dates, ages, and "
                "duration/ago are rejected leftover-form v2 false-read classes."
            ),
            "support": leftover["count_unparsed"]["do_not_parse_count"],
        },
        {
            "rank": 7,
            "rule": "singularize_or_stem_name_gate",
            "status": "do_not_test",
            "reason": (
                "Remaining text_not_substring drops are paraphrases or "
                "singular/plural. Prior leftover-form studies forbid stemming "
                "and singularizing."
            ),
            "support": drop_counts.get("singular_plural", 0)
            + drop_counts.get("seizure_name_paraphrase", 0)
            + drop_counts.get("phenomenology_paraphrase", 0),
        },
        {
            "rank": 8,
            "rule": "prescription_or_diagnosis_name_recovery",
            "status": "later",
            "reason": (
                "SF remains the weak family. Diagnosis and Prescription gaps "
                "are smaller and are not leftover-form count leftovers."
            ),
            "support": family_gaps["Diagnosis"]["miss_count"]
            + family_gaps["Prescription"]["miss_count"],
        },
    ]
    rules.append(
        {
            "rank": 0,
            "rule": "letter_mode_context",
            "status": "context",
            "reason": "Stacked-v10 letter modes on clinical_headline keys.",
            "support": letter_modes["mode_counts"],
        }
    )
    return rules


def _key_counts(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter(str(item["key"]) for item in items)
    return [
        {"key": key, "count": count}
        for key, count in counts.most_common(20)
    ]


def _singularize(text: str) -> str:
    if text.endswith("ses"):
        return text[:-2]
    if text.endswith("ies"):
        return text[:-3] + "y"
    if text.endswith("s") and not text.endswith("ss"):
        return text[:-1]
    return text


def _json_default(value: Any) -> Any:
    if isinstance(value, tuple):
        return list(value)
    return str(value)


def _provenance() -> dict[str, Any]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    return {"git_head": commit, "dirty_tree": bool(dirty)}


if __name__ == "__main__":
    main()
