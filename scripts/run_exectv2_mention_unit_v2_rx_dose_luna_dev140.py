"""No-call catalog of remaining Prescription dose misses on febrile v14."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.drug_lexicon import (
    canonicalize_medication_name,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.conventions import (
    shared as rx_shared,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit import (
    HYBRID_METHOD,
    LLM_METHOD,
    MENTION_UNIT_PROMPT_VERSION,
    MentionUnitEncoder,
    materialize_mention_unit,
    parse_mention_unit_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit_shared import (
    _NONCURRENT_RE,
    _prescription_mention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    prescription_component_keys,
)
from scripts.run_exectv2_mention_unit_v2_leftover_form_stack_error_analysis_luna_dev140 import (
    _family_gaps,
)
from scripts.run_exectv2_mention_unit_v2_leftover_form_v3_luna_dev140 import (
    _form_census,
    _score_method,
)
from scripts.run_exectv2_mention_unit_v2_luna import DEV20_IDS

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/exectv2/"
    "mention_unit_v2_rx_dose_luna_dev140_protocol_2026-08-17.md"
)
REPORT = ROOT / (
    "docs/research/exectv2/mention_unit_v2_rx_dose_luna_dev140_2026-08-17.md"
)
SOURCE_ROWS = ROOT / "experiments/exectv2_mention_unit_v2_luna_dev140_20260816" / "rows.jsonl"
STUDY_DIR = ROOT / "experiments/exectv2_mention_unit_v2_rx_dose_luna_dev140_20260817"
CONTROL: MentionUnitEncoder = "leftover_form_span_fold_febrile_v14"
CANDIDATE: MentionUnitEncoder = "leftover_form_span_fold_rx_dose_v21"
ENCODERS: tuple[MentionUnitEncoder, ...] = (CONTROL, CANDIDATE)
DEV20 = frozenset(DEV20_IDS)
V14_EMPTY_GOLD_SF = 54
V14_REST120_EMPTY_GOLD_SF = 51
_DOSE_IN_TEXT_RE = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(mg|mgs|mgms|milligrams?|milligrammes?|g|grams?)\b",
    re.I,
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

    rows: list[dict[str, Any]] = []
    gold_in_order: list[ExectLetter] = []
    predictions: dict[str, list[PredictedLetter]] = {
        name: [] for name in ("llm", CONTROL, CANDIDATE)
    }
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
            for encoder in ENCODERS:
                predictions[encoder].append(
                    PredictedLetter.model_validate(row["hybrid"][encoder]["prediction"])
                )
    slices = {
        "all140": [letter.letter_id for letter in gold_in_order],
        "dev20": [letter.letter_id for letter in gold_in_order if letter.letter_id in DEV20],
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
    family_gaps = {
        name: _family_gaps(gold_in_order, predictions[name])
        for name in ("llm", CONTROL, CANDIDATE)
    }
    miss_catalog = _miss_catalog(gold_in_order, rows, family_gaps[CONTROL]["Prescription"])
    next_rules = _rank_next_rules(miss_catalog, family_gaps[CONTROL]["Prescription"])
    decision = _decision(
        scored,
        family_gaps[CONTROL]["Prescription"],
        family_gaps[CANDIDATE]["Prescription"],
        next_rules,
    )
    artifact = {
        "schema_version": "exectv2.mention_unit_v2_rx_dose.dev140.v1",
        "status": "complete",
        "protocol": PROTOCOL,
        "split": "dev140",
        "row_count": len(rows),
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "control": CONTROL,
        "candidate": CANDIDATE,
        "candidate_implemented": True,
        "slices": {
            name: {
                "letter_count": len(letter_ids),
                "methods": scored[name]["methods"],
                "form_census": scored[name]["form_census"],
            }
            for name, letter_ids in slices.items()
        },
        "family_gaps": {
            name: {
                family: {
                    key: value
                    for key, value in payload[family].items()
                    if key not in {"misses", "extras"}
                }
                for family in payload
            }
            for name, payload in family_gaps.items()
        },
        "miss_catalog_summary": {
            "class_counts": miss_catalog["class_counts"],
            "gold_free_named_class": miss_catalog["gold_free_named_class"],
        },
        "next_rules": next_rules,
        "decision": decision,
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "claim_boundary": (
            "GPT-5.6 Luna ExECT leftover-form Prescription dose-recovery "
            "catalog on frozen mention-unit v2 dev140 hybrid raws. Not "
            "holdout, not a Decision 0050 change, and not selected-stack "
            "parity."
        ),
    }
    (STUDY_DIR / "comparison.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (STUDY_DIR / "miss_catalog.json").write_text(
        json.dumps(miss_catalog, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (STUDY_DIR / "rows.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    REPORT.write_text(_render_report(artifact, miss_catalog), encoding="utf-8")
    print(
        json.dumps(
            {
                "model_calls": 0,
                "decision": decision,
                "prescription_v14": {
                    "miss": family_gaps[CONTROL]["Prescription"]["miss_count"],
                    "extra": family_gaps[CONTROL]["Prescription"]["extra_count"],
                    "empty_gold_extra": family_gaps[CONTROL]["Prescription"][
                        "empty_gold_extra_count"
                    ],
                    "f1": family_gaps[CONTROL]["Prescription"]["f1"],
                },
                "prescription_v21": {
                    "miss": family_gaps[CANDIDATE]["Prescription"]["miss_count"],
                    "extra": family_gaps[CANDIDATE]["Prescription"]["extra_count"],
                    "empty_gold_extra": family_gaps[CANDIDATE]["Prescription"][
                        "empty_gold_extra_count"
                    ],
                    "f1": family_gaps[CANDIDATE]["Prescription"]["f1"],
                },
                "class_counts": miss_catalog["class_counts"],
                "next_rules": next_rules,
            },
            indent=2,
        )
    )


def _rematerialize_row(letter: ExectLetter, saved: dict[str, Any]) -> dict[str, Any]:
    raw = str(saved["methods"][HYBRID_METHOD]["raw_output"])
    parsed = parse_mention_unit_json(raw, method=HYBRID_METHOD)
    hybrid: dict[str, Any] = {}
    for encoder in ENCODERS:
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
                encoder=encoder,
            )
            payload = {
                "semantic_facts": materialized.semantic_facts,
                "rule_trace": materialized.rule_trace,
                "warnings": materialized.warnings,
                "evidence_invalid": materialized.evidence_invalid,
                "prediction": materialized.prediction.model_dump(mode="json"),
            }
        hybrid[encoder] = payload
    return {
        "letter_id": letter.letter_id,
        "split": "dev140",
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "raw_output": raw,
        "parse_errors": parsed.errors,
        "hybrid_items": [
            {
                "family": item.family,
                "clinical_name": item.text,
                "evidence": item.evidence,
            }
            for item in (parsed.record.items if parsed.record is not None else [])
        ],
        "hybrid": hybrid,
        "llm_prediction": saved["methods"][LLM_METHOD]["prediction"],
    }


def _slice(
    gold: list[ExectLetter],
    predictions: dict[str, list[PredictedLetter]],
    letter_ids: list[str],
) -> tuple[list[ExectLetter], dict[str, list[PredictedLetter]]]:
    wanted = set(letter_ids)
    keep = [index for index, letter in enumerate(gold) if letter.letter_id in wanted]
    return (
        [gold[index] for index in keep],
        {name: [rows[index] for index in keep] for name, rows in predictions.items()},
    )


def _miss_catalog(
    gold: list[ExectLetter],
    rows: list[dict[str, Any]],
    rx_gaps: dict[str, Any],
) -> dict[str, Any]:
    by_id = {letter.letter_id: letter for letter in gold}
    row_by_id = {row["letter_id"]: row for row in rows}
    items: list[dict[str, Any]] = []
    for miss in rx_gaps["misses"]:
        letter = by_id[miss["letter_id"]]
        row = row_by_id[miss["letter_id"]]
        items.append(_classify_miss(letter, row, miss))
    extras = [
        _classify_extra(by_id[item["letter_id"]], row_by_id[item["letter_id"]], item)
        for item in rx_gaps["extras"]
    ]
    class_counts = dict(Counter(item["mechanism"] for item in items))
    gold_free = _gold_free_named_class(items)
    return {
        "control": CONTROL,
        "miss_count": rx_gaps["miss_count"],
        "extra_count": rx_gaps["extra_count"],
        "empty_gold_extra_count": rx_gaps["empty_gold_extra_count"],
        "f1": rx_gaps["f1"],
        "class_counts": class_counts,
        "gold_free_named_class": gold_free,
        "items": items,
        "extras": extras,
        "miss_key_counts": rx_gaps["miss_key_counts"],
        "extra_key_counts": rx_gaps["extra_key_counts"],
    }


def _classify_miss(
    letter: ExectLetter, row: dict[str, Any], miss: dict[str, Any]
) -> dict[str, Any]:
    key = tuple(miss["key"])
    gold_kind = str(key[0])
    gold_drug = str(key[1])
    gold_dose = str(key[2]) if gold_kind == "ordinary" else ""
    gold_unit = str(key[3]) if gold_kind == "ordinary" else ""
    gold_schedule = str(key[4]) if gold_kind == "ordinary" else str(key[2])
    hybrid_items = [
        item
        for item in row["hybrid_items"]
        if item["family"] == "Prescription" and _same_drug(item["clinical_name"], gold_drug)
    ]
    prediction = PredictedLetter.model_validate(row["hybrid"][CONTROL]["prediction"])
    pred_mentions = [
        mention
        for mention in prediction.mentions
        if mention.entity == "Prescription" and _same_drug(mention.text, gold_drug)
    ]
    traces = [
        trace
        for trace in row["hybrid"][CONTROL].get("rule_trace") or []
        if str(trace.get("action") or "") == "suppress_noncurrent_or_unparsed_prescription"
        and _same_drug(str((trace.get("before") or {}).get("text") or ""), gold_drug)
    ]
    gold_anns = [
        ann
        for ann in letter.entities("Prescription")
        if canonicalize_medication_name(str(ann.attributes.get("DrugName") or ann.text))
        == gold_drug
    ]
    gold_spans = [ann.text for ann in gold_anns]
    evidence_blobs = [
        f"{item['clinical_name']} {item['evidence']}".strip() for item in hybrid_items
    ]
    letter_has_dose = bool(
        gold_dose
        and _dose_mentioned(letter.note_text, gold_dose, gold_unit)
    )
    evidence_has_dose = any(
        gold_dose and _dose_mentioned(blob, gold_dose, gold_unit) for blob in evidence_blobs
    )
    parsed = [
        {
            "clinical_name": item["clinical_name"],
            "evidence": item["evidence"],
            "parsed": _parsed_rx(item["clinical_name"], item["evidence"]),
            "noncurrent": bool(
                _NONCURRENT_RE.search(f"{item['clinical_name']} {item['evidence']}")
            ),
        }
        for item in hybrid_items
    ]
    pred_keys = [
        prescription_component_keys([to_exect_letter(PredictedLetter(
            letter_id=letter.letter_id,
            mentions=(mention,),
        )).entities("Prescription")[0]], "clinical_headline", letter.note_text)
        for mention in pred_mentions
    ]
    pred_attrs = [
        {
            "text": mention.text,
            "dose": mention.attributes.get("DrugDose"),
            "unit": mention.attributes.get("DoseUnit"),
            "schedule": mention.attributes.get("Frequency"),
            "evidence": mention.evidence,
        }
        for mention in pred_mentions
    ]
    mechanism = _mechanism(
        gold_kind=gold_kind,
        hybrid_items=hybrid_items,
        pred_mentions=pred_mentions,
        pred_attrs=pred_attrs,
        parsed=parsed,
        traces=traces,
        evidence_has_dose=evidence_has_dose,
        letter_has_dose=letter_has_dose,
        gold_dose=gold_dose,
        gold_unit=gold_unit,
        gold_schedule=gold_schedule,
    )
    return {
        "letter_id": letter.letter_id,
        "slice": miss["slice"],
        "count": miss["count"],
        "key": list(key),
        "mechanism": mechanism,
        "gold_spans": gold_spans,
        "hybrid_items": hybrid_items,
        "parsed": parsed,
        "pred_attrs": pred_attrs,
        "pred_keys": [list(keys[0]) if keys else [] for keys in pred_keys],
        "noncurrent_traces": len(traces),
        "letter_has_dose": letter_has_dose,
        "evidence_has_dose": evidence_has_dose,
        "empty_gold": not bool(letter.entities("Prescription")),
    }


def _classify_extra(
    letter: ExectLetter, row: dict[str, Any], extra: dict[str, Any]
) -> dict[str, Any]:
    key = tuple(extra["key"])
    prediction = PredictedLetter.model_validate(row["hybrid"][CONTROL]["prediction"])
    matches = [
        {
            "text": mention.text,
            "dose": mention.attributes.get("DrugDose"),
            "unit": mention.attributes.get("DoseUnit"),
            "schedule": mention.attributes.get("Frequency"),
            "evidence": mention.evidence,
        }
        for mention in prediction.mentions
        if mention.entity == "Prescription"
        and _same_drug(mention.text, str(key[1]))
    ]
    return {
        "letter_id": letter.letter_id,
        "slice": extra["slice"],
        "count": extra["count"],
        "key": list(key),
        "empty_gold": extra["empty_gold"],
        "pred_attrs": matches,
    }


def _mechanism(
    *,
    gold_kind: str,
    hybrid_items: list[dict[str, Any]],
    pred_mentions: list[Any],
    pred_attrs: list[dict[str, Any]],
    parsed: list[dict[str, Any]],
    traces: list[dict[str, Any]],
    evidence_has_dose: bool,
    letter_has_dose: bool,
    gold_dose: str,
    gold_unit: str,
    gold_schedule: str,
) -> str:
    if gold_kind == "rescue" and not gold_dose:
        return "rescue_no_stated_dose"
    if not hybrid_items:
        return "unread_drug"
    if traces and not pred_mentions:
        return "noncurrent_drop"
    if any(item["noncurrent"] for item in parsed) and not pred_mentions:
        return "noncurrent_drop"
    if not pred_mentions:
        if any(item["parsed"] is None for item in parsed):
            return "name_unparsed"
        return "projection_drop"
    if evidence_has_dose:
        attached = any(
            str(item.get("dose") or "") == gold_dose
            and str(item.get("unit") or "").lower() == gold_unit
            for item in pred_attrs
        )
        if not attached:
            schedule_only = any(
                str(item.get("dose") or "") == gold_dose
                and str(item.get("unit") or "").lower() == gold_unit
                and str(item.get("schedule") or "") != gold_schedule
                for item in pred_attrs
            )
            if schedule_only:
                return "schedule_mismatch"
            unit_only = any(
                str(item.get("dose") or "") == gold_dose
                and str(item.get("unit") or "").lower() != gold_unit
                for item in pred_attrs
            )
            if unit_only:
                return "unit_mismatch"
            return "dose_in_evidence_unattached"
    if letter_has_dose and not evidence_has_dose:
        return "dose_in_letter_not_in_evidence"
    schedule_hit = any(
        str(item.get("dose") or "") == gold_dose
        and str(item.get("unit") or "").lower() == gold_unit
        and str(item.get("schedule") or "") != gold_schedule
        for item in pred_attrs
    )
    if schedule_hit:
        return "schedule_mismatch"
    if any(
        str(item.get("dose") or "") and str(item.get("dose") or "") != gold_dose
        for item in pred_attrs
    ):
        return "wrong_dose_attached"
    if any(not item.get("dose") for item in pred_attrs):
        return "dose_absent_from_projection"
    return "other_mismatch"


def _gold_free_named_class(items: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(item["mechanism"] for item in items)
    attachable = [
        item
        for item in items
        if item["mechanism"] == "dose_in_evidence_unattached"
        and item["parsed"]
        and all(
            parsed.get("parsed")
            and str((parsed["parsed"] or {}).get("dose") or "") != str(item["key"][2])
            for parsed in item["parsed"]
        )
    ]
    # A gold-free class must be writable from emitted name+evidence only.
    # dose_in_evidence_unattached is gold-using unless the parser can see a
    # local dose next to the emitted name without choosing among gold keys.
    local_first_dose = [
        item
        for item in items
        if item["mechanism"] in {"dose_in_evidence_unattached", "wrong_dose_attached"}
        and _local_dose_differs_from_first(item)
    ]
    return {
        "implement": True,
        "class_id": "split_once_daily_before_future_plan",
        "reason": (
            "One gold-free class: two stated once-daily time-of-day doses on "
            "the same emitted item, truncated at a future-plan cue. Both "
            "doses are already in evidence. Titration tails stay unsplit."
        ),
        "attachable_count": len(attachable),
        "local_first_dose_count": len(local_first_dose),
        "dominant": counts.most_common(3),
    }


def _local_dose_differs_from_first(item: dict[str, Any]) -> bool:
    gold_dose = str(item["key"][2]) if item["key"][0] == "ordinary" else ""
    for parsed in item.get("parsed") or []:
        blob = f"{parsed.get('clinical_name') or ''} {parsed.get('evidence') or ''}"
        first = rx_shared.dose_from_text(blob)
        local = _dose_after_name(parsed.get("clinical_name") or "", parsed.get("evidence") or "")
        if local and first and local[0] != first[0] and local[0] == gold_dose:
            return True
    return False


def _dose_after_name(name: str, evidence: str) -> tuple[str, str] | None:
    haystack = f"{name} {evidence}"
    folded_name = canonicalize_medication_name(name).replace("-", " ")
    match = re.search(re.escape(folded_name), haystack, re.I)
    window = haystack[match.end() : match.end() + 40] if match else haystack
    found = _DOSE_IN_TEXT_RE.search(window)
    if found is None:
        return None
    return found.group(1), rx_shared.normalize_dose_unit(found.group(2))


def _parsed_rx(name: str, evidence: str) -> dict[str, str] | None:
    mention = _prescription_mention(f"{name} {evidence}".strip())
    if mention is None:
        return None
    attrs = mention.get("attributes") or {}
    return {
        "text": str(mention.get("text") or ""),
        "dose": str(attrs.get("DrugDose") or ""),
        "unit": str(attrs.get("DoseUnit") or ""),
        "schedule": str(attrs.get("Frequency") or ""),
    }


def _same_drug(surface: str, gold_drug: str) -> bool:
    if not surface:
        return False
    return canonicalize_medication_name(surface) == gold_drug


def _dose_mentioned(text: str, dose: str, unit: str) -> bool:
    if not dose:
        return False
    unit_pat = r"mg|mgs|mgms|milligrams?|milligrammes?|g|grams?" if unit == "mg" else r"g|grams?"
    return bool(re.search(rf"\b{re.escape(dose)}\s*(?:{unit_pat})\b", text, re.I))


def _rank_next_rules(
    catalog: dict[str, Any], rx_gaps: dict[str, Any]
) -> list[dict[str, Any]]:
    counts = catalog["class_counts"]
    ranked: list[dict[str, Any]] = []
    ranked.append(
        {
            "id": "split_once_daily_before_future_plan",
            "action": "tested",
            "reason": (
                "Two stated once-daily time-of-day doses on one emitted "
                "item, truncated at a future-plan cue. Implemented as "
                "leftover_form_span_fold_rx_dose_v21."
            ),
            "n": counts.get("dose_in_evidence_unattached", 0),
        }
    )
    if counts.get("dose_in_evidence_unattached") or counts.get("wrong_dose_attached"):
        ranked.append(
            {
                "id": "local_dose_after_name",
                "action": "do_not_test",
                "reason": (
                    "Nearest-dose-to-name on multi-drug evidence is a "
                    "second class. Do not stack it on this remasure."
                ),
                "n": counts.get("projection_drop", 0),
            }
        )
    if counts.get("unread_drug"):
        ranked.append(
            {
                "id": "unread_name_recovery",
                "action": "do_not_test",
                "reason": (
                    "Unread drugs are a selection leftover. Recovering them "
                    "requires searching the letter, which leftover-form must "
                    "not do."
                ),
                "n": counts.get("unread_drug", 0),
            }
        )
    if counts.get("schedule_mismatch"):
        ranked.append(
            {
                "id": "schedule_default_or_bd_od",
                "action": "do_not_test",
                "reason": (
                    "Schedule mismatches are mixed od/bd and defaulted "
                    "frequency. A schedule rewrite would invent cadence when "
                    "the emitted evidence is silent or contradictory."
                ),
                "n": counts.get("schedule_mismatch", 0),
            }
        )
    if counts.get("dose_in_letter_not_in_evidence"):
        ranked.append(
            {
                "id": "search_letter_for_dose",
                "action": "do_not_test",
                "reason": (
                    "The prompt already says leave the drug out when the "
                    "letter says the same dose and does not state it. "
                    "Searching the letter for a dose is out of contract."
                ),
                "n": counts.get("dose_in_letter_not_in_evidence", 0),
            }
        )
    if counts.get("rescue_no_stated_dose"):
        ranked.append(
            {
                "id": "invent_rescue_dose",
                "action": "do_not_test",
                "reason": "Rescue may lack a dose. Do not invent one.",
                "n": counts.get("rescue_no_stated_dose", 0),
            }
        )
    if counts.get("noncurrent_drop"):
        ranked.append(
            {
                "id": "keep_noncurrent",
                "action": "do_not_test",
                "reason": "Current anti-seizure medicines only.",
                "n": counts.get("noncurrent_drop", 0),
            }
        )
    if not ranked:
        ranked.append(
            {
                "id": "no_named_class",
                "action": "do_not_test",
                "reason": "No remaining miss class is gold-free and predeclarable.",
                "n": rx_gaps["miss_count"],
            }
        )
    return ranked


def _decision(
    scored: dict[str, dict[str, Any]],
    control_rx: dict[str, Any],
    candidate_rx: dict[str, Any],
    next_rules: list[dict[str, Any]],
) -> dict[str, Any]:
    all140 = scored["all140"]["methods"]
    rest = scored["rest120"]["methods"]
    extras = all140[CANDIDATE]["empty_gold_sf_extras"]["mention_count"]
    control_extras = all140[CONTROL]["empty_gold_sf_extras"]["mention_count"]
    rest_extras = rest[CANDIDATE]["empty_gold_sf_extras"]["mention_count"]
    rest_control_extras = rest[CONTROL]["empty_gold_sf_extras"]["mention_count"]
    rx_extras_rose = candidate_rx["extra_count"] > control_rx["extra_count"]
    extras_rose = (
        extras > control_extras
        or rest_extras > rest_control_extras
        or extras > V14_EMPTY_GOLD_SF
        or rest_extras > V14_REST120_EMPTY_GOLD_SF
        or rx_extras_rose
    )
    headline = all140[CANDIDATE]["clinical_headline_f1"]
    control_headline = all140[CONTROL]["clinical_headline_f1"]
    rx = all140[CANDIDATE]["clinical_headline_family_f1"]["Prescription"]
    control_rx_f1 = all140[CONTROL]["clinical_headline_family_f1"]["Prescription"]
    if extras_rose:
        status = "revise"
        mechanism = "rx_dose_v21_extras_rose"
    elif candidate_rx["miss_count"] >= control_rx["miss_count"]:
        status = "reject"
        mechanism = "rx_dose_v21_named_class_unmoved"
    elif headline > control_headline or rx > control_rx_f1:
        status = "answer"
        mechanism = "split_once_daily_second_dose_recovered"
    else:
        status = "negative_result"
        mechanism = "rx_dose_v21_headline_unchanged"
    return {
        "status": status,
        "mechanism": mechanism,
        "candidate_implemented": True,
        "control_prescription_miss": control_rx["miss_count"],
        "control_prescription_extra": control_rx["extra_count"],
        "control_prescription_empty_gold_extra": control_rx["empty_gold_extra_count"],
        "control_prescription_f1": control_rx["f1"],
        "prescription_miss": candidate_rx["miss_count"],
        "prescription_extra": candidate_rx["extra_count"],
        "prescription_empty_gold_extra": candidate_rx["empty_gold_extra_count"],
        "prescription_f1": candidate_rx["f1"],
        "empty_gold_sf_extras": extras,
        "control_empty_gold_sf_extras": control_extras,
        "rest120_empty_gold_sf_extras": rest_extras,
        "rest120_control_empty_gold_sf_extras": rest_control_extras,
        "extras_rose": extras_rose,
        "rx_extras_rose": rx_extras_rose,
        "headline_140": headline,
        "control_headline_140": control_headline,
        "sf_140": all140[CANDIDATE]["clinical_headline_family_f1"]["SeizureFrequency"],
        "rx_140": rx,
        "control_rx_140": control_rx_f1,
        "next_rules": next_rules,
    }


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


def _render_report(artifact: dict[str, Any], catalog: dict[str, Any]) -> str:
    decision = artifact["decision"]
    counts = catalog["class_counts"]
    return (
        "# ExECT leftover-form Prescription dose recovery, "
        "mention-unit v2 `dev140`\n\n"
        f"Date: 2026-08-17  \n"
        f"Status: complete; **{decision['status']}**  \n"
        f"Protocol: [rx dose `dev140`]({Path(PROTOCOL).name})  \n"
        "Parent: [febrile widen `dev140`]"
        "(mention_unit_v2_febrile_widen_luna_dev140_2026-08-17.md)\n\n"
        "`model_calls`: 0. Draft rendered by the remasure script. "
        "Replace with the inspected report.\n\n"
        f"Control Prescription miss/extra/F1: {decision['control_prescription_miss']} / "
        f"{decision['control_prescription_extra']} / {decision['control_prescription_f1']}. "
        f"Candidate: {decision['prescription_miss']} / {decision['prescription_extra']} / "
        f"{decision['prescription_f1']}. "
        f"v14 miss classes: {counts}.\n"
    )


if __name__ == "__main__":
    main()
