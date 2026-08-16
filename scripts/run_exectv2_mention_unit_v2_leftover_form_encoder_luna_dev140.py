"""No-call remasure of saved mention-unit v2 hybrid raws through leftover-form."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit import (
    HYBRID_METHOD,
    LLM_METHOD,
    MENTION_UNIT_PROMPT_VERSION,
    materialize_mention_unit,
    parse_mention_unit_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit_leftover_form import (
    ENCODER_VERSION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
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
    "mention_unit_v2_leftover_form_encoder_luna_dev140_protocol_2026-08-16.md"
)
SOURCE_ROWS = ROOT / "experiments/exectv2_mention_unit_v2_luna_dev140_20260816" / "rows.jsonl"
STUDY_DIR = (
    ROOT / "experiments/exectv2_mention_unit_v2_leftover_form_encoder_luna_dev140_20260816"
)
FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")
COUNT_ATTRS = {
    "LowerNumberOfSeizures",
    "NumberOfSeizures",
    "UpperNumberOfSeizures",
}
RESULT_ATTRS = ("MRI_Results", "EEG_Results", "CT_Results")
SAVED_HYBRID_SF_WITH_COUNT = 58
SAVED_HYBRID_IX_UNKNOWN = 61


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
    predictions: dict[str, list[PredictedLetter]] = {
        "llm": [],
        "landed": [],
        "leftover_form": [],
        "saved_hybrid": [],
    }
    gold_in_order: list[ExectLetter] = []
    with SOURCE_ROWS.open(encoding="utf-8") as handle:
        for line in handle:
            saved = json.loads(line)
            letter = by_id[saved["letter_id"]]
            gold_in_order.append(letter)
            row = _rematerialize_row(letter, saved)
            rows.append(row)
            predictions["llm"].append(
                PredictedLetter.model_validate(saved["methods"][LLM_METHOD]["prediction"])
            )
            predictions["saved_hybrid"].append(
                PredictedLetter.model_validate(
                    saved["methods"][HYBRID_METHOD]["prediction"]
                )
            )
            predictions["landed"].append(
                PredictedLetter.model_validate(row["hybrid"]["landed"]["prediction"])
            )
            predictions["leftover_form"].append(
                PredictedLetter.model_validate(
                    row["hybrid"]["leftover_form"]["prediction"]
                )
            )

    methods = {
        "llm": _score_method(gold_in_order, predictions["llm"]),
        "saved_hybrid": _score_method(gold_in_order, predictions["saved_hybrid"]),
        "landed": _score_method(gold_in_order, predictions["landed"]),
        "leftover_form": _score_method(gold_in_order, predictions["leftover_form"]),
    }
    form = {
        name: _form_census(predictions[name])
        for name in ("llm", "saved_hybrid", "landed", "leftover_form")
    }
    catalogs = {
        "landed": _catalog(rows, encoder="landed"),
        "leftover_form": _catalog(rows, encoder="leftover_form"),
    }
    stop_checks = _stop_checks(form, methods, catalogs)
    verdict = _verdict(form, stop_checks)
    artifact = {
        "schema_version": "exectv2.mention_unit_v2_leftover_form.v1",
        "status": verdict["status"],
        "mechanism": verdict["mechanism"],
        "protocol": PROTOCOL,
        "split": "dev140",
        "row_count": len(rows),
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "encoder": ENCODER_VERSION,
        "claim_boundary": (
            "GPT-5.6 Luna ExECT mention-unit v2 leftover-form remasure on saved "
            "hybrid raws. test60 sealed. Not a Decision 0050 change."
        ),
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "methods": methods,
        "form_census": form,
        "catalog_summary": {
            encoder: catalog["class_counts"] for encoder, catalog in catalogs.items()
        },
        "stop_checks": stop_checks,
        "verdict": verdict,
    }
    (STUDY_DIR / "comparison.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (STUDY_DIR / "damage_catalog.json").write_text(
        json.dumps(catalogs, indent=2, sort_keys=True) + "\n", encoding="utf-8"
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
                "mechanism": artifact["mechanism"],
                "form_census": form,
                "catalog_summary": artifact["catalog_summary"],
                "clinical_headline": {
                    name: {
                        "clinical_headline_f1": summary["clinical_headline_f1"],
                        "clinical_headline_family_f1": summary[
                            "clinical_headline_family_f1"
                        ],
                    }
                    for name, summary in methods.items()
                },
                "stop_checks": stop_checks,
            },
            indent=2,
        )
    )


def _rematerialize_row(letter: ExectLetter, saved: dict[str, Any]) -> dict[str, Any]:
    raw = str(saved["methods"][HYBRID_METHOD]["raw_output"])
    parsed = parse_mention_unit_json(raw, method=HYBRID_METHOD)
    hybrid: dict[str, Any] = {}
    for encoder in ("landed", "leftover_form"):
        if parsed.record is None:
            prediction = PredictedLetter(letter_id=letter.letter_id, mentions=())
            semantic_facts: list[dict[str, Any]] = []
            rule_trace: list[dict[str, Any]] = []
            warnings: list[str] = []
            evidence_invalid = 0
        else:
            materialized = materialize_mention_unit(
                letter,
                parsed.record,
                method=HYBRID_METHOD,
                encoder=encoder,  # type: ignore[arg-type]
            )
            prediction = materialized.prediction
            semantic_facts = materialized.semantic_facts
            rule_trace = materialized.rule_trace
            warnings = materialized.warnings
            evidence_invalid = materialized.evidence_invalid
        hybrid[encoder] = {
            "semantic_facts": semantic_facts,
            "rule_trace": rule_trace,
            "warnings": warnings,
            "evidence_invalid": evidence_invalid,
            "prediction": prediction.model_dump(mode="json"),
        }
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
        "empty_gold_sf_extras": _empty_gold_sf_extras(gold, predictions),
        "nontarget_mentions": _nontarget_mentions(predictions),
    }


def _form_census(predictions: list[PredictedLetter]) -> dict[str, int]:
    census = {
        "sf_mentions": 0,
        "sf_with_count": 0,
        "ix_mentions": 0,
        "ix_known": 0,
        "ix_unknown": 0,
    }
    for prediction in predictions:
        for mention in prediction.mentions:
            if mention.entity == "SeizureFrequency":
                census["sf_mentions"] += 1
                census["sf_with_count"] += int(_has_count(mention))
            if mention.entity == "Investigations":
                census["ix_mentions"] += 1
                result = _ix_result(mention)
                if result == "Unknown":
                    census["ix_unknown"] += 1
                elif result:
                    census["ix_known"] += 1
    return census


def _catalog(rows: list[dict[str, Any]], *, encoder: str) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    name_kept = 0
    name_rewritten = 0
    last_event_zero = 0
    for row in rows:
        hybrid = row["hybrid"][encoder]
        warnings = hybrid.get("warnings") or []
        prediction = PredictedLetter.model_validate(hybrid["prediction"])
        for mention in prediction.mentions:
            if mention.entity == "SeizureFrequency" and not _has_count(mention):
                items.append(
                    {
                        "letter_id": row["letter_id"],
                        "class": "count_unparsed",
                        "clinical_name": mention.text,
                        "evidence": mention.evidence,
                    }
                )
            if mention.entity == "Investigations" and _ix_result(mention) == "Unknown":
                items.append(
                    {
                        "letter_id": row["letter_id"],
                        "class": "result_unknown",
                        "clinical_name": mention.text,
                        "evidence": mention.evidence,
                    }
                )
        for fact in hybrid.get("semantic_facts") or []:
            if fact.get("family") != "SeizureFrequency":
                continue
            name = str(fact.get("clinical_name") or fact.get("text") or "")
            scorer = str(fact.get("scorer_text") or "")
            if scorer and _norm(scorer) == _norm(name):
                name_kept += 1
            elif scorer:
                name_rewritten += 1
                items.append(
                    {
                        "letter_id": row["letter_id"],
                        "class": "name_rewritten",
                        "clinical_name": name,
                        "scorer_text": scorer,
                    }
                )
            index = fact.get("fact_index")
            if any(f"item[{index}]: text_not_substring" in warning for warning in warnings):
                items.append(
                    {
                        "letter_id": row["letter_id"],
                        "class": "text_not_substring_drop",
                        "clinical_name": name,
                    }
                )
        for trace in hybrid.get("rule_trace") or []:
            action = str(trace.get("action") or "")
            if action == "encoding.last_event_zero" or action == "leftover_form.sf_zero":
                last_event_zero += 1
            if action != "suppress_uncoded_or_noise_sf":
                continue
            items.append(
                {
                    "letter_id": row["letter_id"],
                    "class": "suppress_uncoded_sf",
                    "clinical_name": str((trace.get("before") or {}).get("text") or ""),
                    "evidence": trace.get("evidence"),
                }
            )
    class_counts = dict(Counter(item["class"] for item in items))
    return {
        "encoder": encoder,
        "class_counts": class_counts,
        "name_kept": name_kept,
        "name_rewritten": name_rewritten,
        "last_event_zero": last_event_zero,
        "items": items,
    }


def _stop_checks(
    form: dict[str, dict[str, int]],
    methods: dict[str, dict[str, Any]],
    catalogs: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    landed_reproduces = (
        form["landed"]["sf_with_count"] == SAVED_HYBRID_SF_WITH_COUNT
        and form["landed"]["ix_unknown"] == SAVED_HYBRID_IX_UNKNOWN
    )
    extras_rose = (
        methods["leftover_form"]["empty_gold_sf_extras"]["mention_count"]
        > methods["landed"]["empty_gold_sf_extras"]["mention_count"]
    )
    names_rewritten_more = catalogs["leftover_form"]["name_rewritten"] > catalogs["landed"][
        "name_rewritten"
    ]
    ecg = bool(methods["leftover_form"]["nontarget_mentions"])
    return {
        "landed_reproduces_saved_form": landed_reproduces,
        "empty_gold_sf_extras_rose": extras_rose,
        "names_rewritten_more": names_rewritten_more,
        "ecg_or_nontarget": ecg,
        "triggered": extras_rose or names_rewritten_more or ecg or not landed_reproduces,
    }


def _verdict(
    form: dict[str, dict[str, int]],
    stop_checks: dict[str, Any],
) -> dict[str, str]:
    if not stop_checks["landed_reproduces_saved_form"]:
        return {
            "status": "blocked_by_instrumentation",
            "mechanism": "landed_rematerialization_mismatch",
        }
    if (
        stop_checks["empty_gold_sf_extras_rose"]
        or stop_checks["names_rewritten_more"]
        or stop_checks["ecg_or_nontarget"]
    ):
        return {"status": "revise", "mechanism": "leftover_form_side_effect"}
    recovered_count = form["leftover_form"]["sf_with_count"] > form["landed"]["sf_with_count"]
    recovered_result = form["leftover_form"]["ix_unknown"] < form["landed"]["ix_unknown"]
    if recovered_count or recovered_result:
        return {"status": "answer", "mechanism": "leftover_form_recovered"}
    return {"status": "reject", "mechanism": "leftover_form_no_move"}


def _empty_gold_sf_extras(
    gold: list[ExectLetter], predictions: list[PredictedLetter]
) -> dict[str, Any]:
    letters: list[str] = []
    mention_count = 0
    for letter, prediction in zip(gold, predictions, strict=True):
        if letter.entities("SeizureFrequency"):
            continue
        extras = [
            mention
            for mention in prediction.mentions
            if mention.entity == "SeizureFrequency"
        ]
        if extras:
            letters.append(letter.letter_id)
            mention_count += len(extras)
    return {"letter_count": len(letters), "mention_count": mention_count, "letters": letters}


def _nontarget_mentions(predictions: list[PredictedLetter]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for prediction in predictions:
        for mention in prediction.mentions:
            if mention.entity == "Investigations" and mention.text.upper() in {"ECG", "EKG"}:
                out.append(
                    {"letter_id": prediction.letter_id, "text": mention.text}
                )
    return out


def _has_count(mention: Any) -> bool:
    return bool(COUNT_ATTRS.intersection(mention.attributes or {}))


def _ix_result(mention: Any) -> str:
    for key in RESULT_ATTRS:
        value = (mention.attributes or {}).get(key)
        if value:
            return str(value)
    return ""


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.casefold())


def _aggregate_f1(scores: Iterable[Any]) -> float:
    tp = fp = fn = 0
    for score in scores:
        tp += int(score.tp)
        fp += int(score.fp)
        fn += int(score.fn)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def _provenance() -> dict[str, Any]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    return {
        "git_head": commit,
        "working_tree": "dirty" if dirty else "clean",
    }


if __name__ == "__main__":
    main()
