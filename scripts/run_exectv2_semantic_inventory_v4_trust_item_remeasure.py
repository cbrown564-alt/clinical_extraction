"""No-call remasure of saved v4 raws through the trust-item projector."""

from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.semantic_inventory import (
    HYBRID_METHOD,
    LLM_METHOD,
    materialize_inventory,
    parse_inventory_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    clinical_headline_unit_keys,
    score_concept_identity,
    score_frequency_state,
    score_investigations_components,
    score_overall,
    score_prescription_components,
    semantic_config_for,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/exectv2/"
    "semantic_inventory_v4_trust_item_luna_dev140_protocol_2026-08-16.md"
)
SOURCE_ROWS = (
    ROOT
    / "experiments/exectv2_semantic_inventory_v4_projection_damage_luna_dev140_20260816"
    / "rows.jsonl"
)
STUDY_DIR = (
    ROOT / "experiments/exectv2_semantic_inventory_v4_trust_item_luna_dev140_20260816"
)
FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")
WORD_COUNTS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
}
TYPED_SF = re.compile(
    r"focal seizures|secondary generalised|generalised tonic|absence|"
    r"myoclonic|focal to bilateral|complex partial|focal motor",
    re.I,
)
DURATION_YEARS = re.compile(
    r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+years?\b",
    re.I,
)
DRUGS = re.compile(
    r"\b(lamotrigine|levetiracetam|carbamazepine|topiramate|clobazam|"
    r"zonisamide|perampanel|lacosamide|phenytoin|midazolam)\b",
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
    predictions: dict[str, dict[str, list[PredictedLetter]]] = {
        "v4": {LLM_METHOD: [], HYBRID_METHOD: []},
        "trust_item": {LLM_METHOD: [], HYBRID_METHOD: []},
        "control": {LLM_METHOD: [], HYBRID_METHOD: []},
    }
    gold_in_order: list[ExectLetter] = []
    with SOURCE_ROWS.open(encoding="utf-8") as handle:
        for line in handle:
            saved = json.loads(line)
            letter = by_id[saved["letter_id"]]
            gold_in_order.append(letter)
            row = _rematerialize_row(letter, saved)
            rows.append(row)
            for policy in ("v4", "trust_item"):
                for method in (LLM_METHOD, HYBRID_METHOD):
                    predictions[policy][method].append(
                        PredictedLetter.model_validate(
                            row["methods"][method][policy]["prediction"]
                        )
                    )
            predictions["control"][LLM_METHOD].append(
                PredictedLetter.model_validate(saved["controls"]["llm"])
            )
            predictions["control"][HYBRID_METHOD].append(
                PredictedLetter.model_validate(saved["controls"]["llm_with_rules"])
            )

    methods = {
        "control_llm": _score_method(gold_in_order, predictions["control"][LLM_METHOD]),
        "control_llm_with_rules": _score_method(
            gold_in_order, predictions["control"][HYBRID_METHOD]
        ),
        "v4_llm": _score_method(gold_in_order, predictions["v4"][LLM_METHOD]),
        "v4_llm_with_rules": _score_method(gold_in_order, predictions["v4"][HYBRID_METHOD]),
        "trust_item_llm": _score_method(gold_in_order, predictions["trust_item"][LLM_METHOD]),
        "trust_item_llm_with_rules": _score_method(
            gold_in_order, predictions["trust_item"][HYBRID_METHOD]
        ),
    }
    catalogs = {
        "v4": _catalog(rows, policy="v4"),
        "trust_item": _catalog(rows, policy="trust_item"),
    }
    leftover = _leftover_census(
        gold_in_order,
        predictions["v4"],
        predictions["trust_item"],
        catalogs["trust_item"],
    )
    stop_checks = _stop_checks(rows, leftover)
    artifact = {
        "schema_version": "exectv2.v4_trust_item_remeasure.v1",
        "status": "revise" if stop_checks["triggered"] else "complete",
        "protocol": PROTOCOL,
        "split": "dev140",
        "row_count": len(rows),
        "model_calls": 0,
        "prompt_version": "exectv2_semantic_inventory_v4",
        "projection": "trust_item",
        "claim_boundary": (
            "GPT-5.6 Luna ExECT development remasure on saved v4 raws. "
            "test60 sealed. Not a Decision 0050 change."
        ),
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "methods": methods,
        "catalog_summary": {
            policy: catalog["summary"] for policy, catalog in catalogs.items()
        },
        "leftover": leftover,
        "stop_checks": stop_checks,
    }
    (STUDY_DIR / "comparison.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (STUDY_DIR / "damage_catalog.json").write_text(
        json.dumps(catalogs, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (STUDY_DIR / "leftover_census.json").write_text(
        json.dumps(leftover, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (STUDY_DIR / "rows.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "model_calls": 0,
                "row_count": len(rows),
                "status": artifact["status"],
                "methods": {
                    name: {
                        "clinical_headline_f1": summary["clinical_headline_f1"],
                        "clinical_headline_family_f1": summary[
                            "clinical_headline_family_f1"
                        ],
                    }
                    for name, summary in methods.items()
                },
                "catalog_summary": artifact["catalog_summary"],
                "stop_checks": stop_checks,
                "leftover_letters_still_in_class": leftover[
                    "letters_still_in_a_catalog_class"
                ],
            },
            indent=2,
        )
    )


def _rematerialize_row(letter: ExectLetter, saved: dict[str, Any]) -> dict[str, Any]:
    row = {
        "letter_id": letter.letter_id,
        "split": "dev140",
        "model_calls": 0,
        "prompt_version": "exectv2_semantic_inventory_v4",
        "methods": {},
    }
    for method in (LLM_METHOD, HYBRID_METHOD):
        raw = str(saved["methods"][method]["raw_output"])
        parsed = parse_inventory_json(raw, method=method)
        method_row: dict[str, Any] = {
            "raw_output": raw,
            "parse_errors": parsed.errors,
            "forbidden_model_fields": parsed.forbidden_fields,
        }
        for policy in ("v4", "trust_item"):
            if parsed.record is None:
                materialized_prediction = PredictedLetter(
                    letter_id=letter.letter_id, mentions=()
                )
                semantic_facts: list[dict[str, Any]] = []
                rule_trace: list[dict[str, Any]] = []
                evidence_invalid = 0
            else:
                materialized = materialize_inventory(
                    letter,
                    parsed.record,
                    method=method,
                    projection=policy,  # type: ignore[arg-type]
                )
                materialized_prediction = materialized.prediction
                semantic_facts = materialized.semantic_facts
                rule_trace = materialized.rule_trace
                evidence_invalid = materialized.evidence_invalid
            method_row[policy] = {
                "semantic_facts": semantic_facts,
                "rule_trace": rule_trace,
                "evidence_invalid": evidence_invalid,
                "prediction": materialized_prediction.model_dump(mode="json"),
            }
        row["methods"][method] = method_row
    return row


def _score_method(
    gold: list[ExectLetter], predictions: list[PredictedLetter]
) -> dict[str, Any]:
    pred_letters = [to_exect_letter(prediction) for prediction in predictions]
    semantic = score_overall(gold, pred_letters, FAMILIES, semantic_config_for)
    headline_scores = {
        "Diagnosis": score_concept_identity(gold, pred_letters, "Diagnosis").concept_only,
        "SeizureFrequency": score_frequency_state(gold, pred_letters).clinical_headline,
        "Prescription": score_prescription_components(gold, pred_letters).clinical_headline,
        "Investigations": score_investigations_components(
            gold, pred_letters
        ).clinical_headline,
    }
    return {
        "semantic_f1": round(semantic.per_item.f1, 4),
        "semantic_family_f1": {
            family: round(score.per_item.f1, 4)
            for family, score in semantic.per_entity.items()
        },
        "clinical_headline_f1": round(_aggregate_f1(headline_scores.values()), 4),
        "clinical_headline_family_f1": {
            family: round(score.f1, 4) for family, score in headline_scores.items()
        },
        "semantic_counts": {
            "tp": int(semantic.per_item.tp),
            "fp": int(semantic.per_item.fp),
            "fn": int(semantic.per_item.fn),
        },
    }


def _aggregate_f1(scores: Iterable[Any]) -> float:
    tp = fp = fn = 0
    for score in scores:
        tp += int(score.tp)
        fp += int(score.fp)
        fn += int(score.fn)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def _catalog(rows: list[dict[str, Any]], *, policy: str) -> dict[str, Any]:
    classes: dict[str, dict[str, Any]] = {}
    examples: dict[str, list[dict[str, str]]] = {}

    def add(class_id: str, letter_id: str, detail: str) -> None:
        payload = classes.setdefault(class_id, {"count": 0, "letters": []})
        payload["count"] += 1
        if letter_id not in payload["letters"]:
            payload["letters"].append(letter_id)
        bucket = examples.setdefault(class_id, [])
        if len(bucket) < 5:
            bucket.append({"letter_id": letter_id, "detail": detail})

    for row in rows:
        letter_id = row["letter_id"]
        for method in (LLM_METHOD, HYBRID_METHOD):
            method_row = row["methods"][method][policy]
            pred_inv = [
                mention
                for mention in method_row["prediction"]["mentions"]
                if mention["entity"] == "Investigations"
            ]
            pred_rx = [
                str(mention["text"]).lower()
                for mention in method_row["prediction"]["mentions"]
                if mention["entity"] == "Prescription"
            ]
            for fact in method_row["semantic_facts"]:
                family = fact.get("family")
                event = fact.get("event") or ""
                event_l = event.lower()
                attrs = fact.get("attributes") or {}
                scorer_text = str(fact.get("scorer_text") or "").lower()
                legacy = fact.get("legacy_attributes") or {}
                if family == "SeizureFrequency":
                    typed = TYPED_SF.search(event) or TYPED_SF.search(
                        str(attrs.get("type", ""))
                    )
                    if typed and scorer_text in {"seizures", "seizure"}:
                        add(
                            f"{method}.sf_generic_span_over_typed",
                            letter_id,
                            f"{event[:100]} -> {scorer_text}",
                        )
                    type_attr = str(attrs.get("type") or "")
                    if (
                        method == LLM_METHOD
                        and type_attr
                        and type_attr.lower() not in {"", "seizures", "seizure"}
                        and scorer_text in {"seizures", "seizure"}
                    ):
                        add(
                            f"{method}.sf_type_attribute_ignored",
                            letter_id,
                            f"type={type_attr} -> {scorer_text}",
                        )
                    word = next(
                        (item for item in WORD_COUNTS if re.search(rf"\b{item}\b", event_l)),
                        None,
                    )
                    has_num = any(
                        legacy.get(key)
                        for key in (
                            "NumberOfSeizures",
                            "LowerNumberOfSeizures",
                            "UpperNumberOfSeizures",
                        )
                    )
                    if word and not has_num and "seizure" in event_l:
                        add(
                            f"{method}.sf_word_count_unparsed",
                            letter_id,
                            f"{word} in {event[:90]}",
                        )
                    if (
                        method == LLM_METHOD
                        and attrs.get("count")
                        and not legacy.get("NumberOfSeizures")
                        and str(attrs.get("state", "")).lower() not in {"historical"}
                    ):
                        add(
                            f"{method}.sf_count_attribute_unmapped",
                            letter_id,
                            f"count={attrs.get('count')} state={attrs.get('state')}",
                        )
                if family == "Investigations":
                    result = str(attrs.get("result") or "").lower()
                    name = str(attrs.get("name") or "")
                    if method == LLM_METHOD and result in {"abnormal", "normal"}:
                        mapped = any(
                            mention["attributes"].get(key) == result.title()
                            for mention in pred_inv
                            for key in ("MRI_Results", "EEG_Results", "CT_Results")
                        )
                        if not mapped:
                            add(
                                f"{method}.inv_result_attribute_dropped",
                                letter_id,
                                f"name={name} result={result}",
                            )
                    if (
                        method == HYBRID_METHOD
                        and re.search(
                            r"showed|shows|demonstrated|revealed|high[- ]|gliosis|infarct|spike",
                            event_l,
                        )
                        and not re.search(r"\b(normal|abnormal)\b", event_l)
                    ):
                        results = [
                            mention["attributes"].get("MRI_Results")
                            or mention["attributes"].get("EEG_Results")
                            or mention["attributes"].get("CT_Results")
                            for mention in pred_inv
                        ]
                        if "Unknown" in results:
                            add(
                                f"{method}.inv_described_finding_forced_unknown",
                                letter_id,
                                event[:100],
                            )
                if family == "Prescription" and method == HYBRID_METHOD:
                    named = DRUGS.findall(event_l)
                    if len(set(named)) >= 2:
                        missing = [name for name in set(named) if name not in pred_rx]
                        if missing:
                            add(
                                f"{method}.rx_bundled_event_keeps_first_drug",
                                letter_id,
                                f"{named} -> {pred_rx}",
                            )
            if method == HYBRID_METHOD:
                for trace in method_row.get("rule_trace") or []:
                    if trace.get("action") == "encoding.last_clinic_frame" and not (
                        trace.get("after") or {}
                    ).get("NumberOfSeizures"):
                        add(
                            f"{method}.sf_last_clinic_frame_without_count",
                            letter_id,
                            str(trace.get("after")),
                        )
    summary = {
        class_id: {
            "fact_count": payload["count"],
            "letter_count": len(payload["letters"]),
        }
        for class_id, payload in classes.items()
    }
    return {
        "schema_version": "exectv2.v4_projection_damage.v1",
        "split": "dev140",
        "projection": policy,
        "row_count": len(rows),
        "summary": summary,
        "examples": examples,
        "classes": classes,
    }


def _leftover_census(
    gold: list[ExectLetter],
    v4_predictions: dict[str, list[PredictedLetter]],
    trust_predictions: dict[str, list[PredictedLetter]],
    catalog: dict[str, Any],
) -> dict[str, Any]:
    remaining_letters = sorted(
        {
            letter_id
            for payload in catalog["classes"].values()
            for letter_id in payload["letters"]
        }
    )
    family_rows: list[dict[str, Any]] = []
    empty_gold_extra_letters: dict[str, list[str]] = {family: [] for family in FAMILIES}
    leftover_miss_letters: dict[str, list[str]] = {family: [] for family in FAMILIES}
    changed = {"improved": 0, "regressed": 0, "unchanged": 0}
    for index, letter in enumerate(gold):
        v4_letter = to_exect_letter(v4_predictions[HYBRID_METHOD][index])
        trust_letter = to_exect_letter(trust_predictions[HYBRID_METHOD][index])
        v4_net = 0
        trust_net = 0
        for family in FAMILIES:
            gold_keys = set(
                clinical_headline_unit_keys(
                    family, letter.entities(family), letter.note_text
                )
            )
            v4_keys = set(
                clinical_headline_unit_keys(
                    family, v4_letter.entities(family), letter.note_text
                )
            )
            trust_keys = set(
                clinical_headline_unit_keys(
                    family, trust_letter.entities(family), letter.note_text
                )
            )
            extras = trust_keys - gold_keys
            misses = gold_keys - trust_keys
            v4_net += len(gold_keys & v4_keys) - len(v4_keys - gold_keys) - len(
                gold_keys - v4_keys
            )
            trust_net += len(gold_keys & trust_keys) - len(extras) - len(misses)
            if extras or misses:
                family_rows.append(
                    {
                        "letter_id": letter.letter_id,
                        "family": family,
                        "gold": len(gold_keys),
                        "trust_item": len(trust_keys),
                        "extras": len(extras),
                        "misses": len(misses),
                    }
                )
            if not gold_keys and extras:
                empty_gold_extra_letters[family].append(letter.letter_id)
            if misses:
                leftover_miss_letters[family].append(letter.letter_id)
        if trust_net > v4_net:
            changed["improved"] += 1
        elif trust_net < v4_net:
            changed["regressed"] += 1
        else:
            changed["unchanged"] += 1
    return {
        "letters_still_in_a_catalog_class": len(remaining_letters),
        "remaining_class_letters": remaining_letters,
        "hybrid_changed_row_direction": changed,
        "empty_gold_extra_letter_counts": {
            family: len(ids) for family, ids in empty_gold_extra_letters.items()
        },
        "empty_gold_extra_letters": empty_gold_extra_letters,
        "leftover_miss_letter_counts": {
            family: len(ids) for family, ids in leftover_miss_letters.items()
        },
        "leftover_miss_letters": leftover_miss_letters,
        "family_mismatch_rows": family_rows,
    }


def _stop_checks(rows: list[dict[str, Any]], leftover: dict[str, Any]) -> dict[str, Any]:
    ecg_letters: list[str] = []
    duration_count_letters: list[str] = []
    for row in rows:
        letter_id = row["letter_id"]
        for method in (LLM_METHOD, HYBRID_METHOD):
            mentions = row["methods"][method]["trust_item"]["prediction"]["mentions"]
            if any(
                "ECG" in str(mention.get("text") or "").upper()
                or any(key.upper().startswith("ECG") for key in mention.get("attributes") or {})
                for mention in mentions
            ):
                if letter_id not in ecg_letters:
                    ecg_letters.append(letter_id)
            for fact in row["methods"][method]["trust_item"]["semantic_facts"]:
                event = str(fact.get("event") or "")
                duration = DURATION_YEARS.search(event)
                count = str((fact.get("legacy_attributes") or {}).get("NumberOfSeizures") or "")
                if duration is None or not count:
                    continue
                mapped = WORD_COUNTS.get(duration.group(1), duration.group(1))
                if count == mapped:
                    if letter_id not in duration_count_letters:
                        duration_count_letters.append(letter_id)
    triggered = bool(ecg_letters or duration_count_letters)
    return {
        "triggered": triggered,
        "ecg_emitted_letters": ecg_letters,
        "duration_token_became_count_letters": duration_count_letters,
        "empty_gold_extra_letter_counts": leftover["empty_gold_extra_letter_counts"],
    }


def _provenance() -> dict[str, Any]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return {
        "git_head": commit,
        "working_tree": "dirty_trust_item_remeasure",
        "source_rows": str(SOURCE_ROWS.relative_to(ROOT)),
    }


if __name__ == "__main__":
    main()
