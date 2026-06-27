"""SeizureFrequency verifier prompt content and scoring."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    _has_blocking_parse_issue,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.runner import (
    reconstruct_gold_letters,
    reconstruct_pred_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompts.entity_verifier.loader import (
    load_sf_clinical_rules,
    load_sf_worked_examples,
)

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    benchmark_config_for,
    score_entity,
    score_frequency_state,
    semantic_config_for,
    source_near_diagnostic,
)

PROMPT_VERSION = "exectv2_llm_sf_verifier_v0.4"
PIPELINE_FAMILY = "exectv2_llm_sf_verifier"
COMPONENT_OWNER = "llm_sf_verifier"

TASK_TEXT = (
    "Review the clinical letter and draft SeizureFrequency mentions from "
    "the single structured key-entity extractor. Return the final "
    "SeizureFrequency mentions only. You may keep, delete, edit, or add "
    "mentions, but every final mention must be supported by exact source "
    "evidence."
)

OUTPUT_SCHEMA = {
    "mentions": [
        {
            "text": "Clean seizure/event type anchor phrase owned by the verifier.",
            "attributes": {
                "NumberOfSeizures": "string count, including 0 for seizure-free",
                "LowerNumberOfSeizures": "lower bound count",
                "UpperNumberOfSeizures": "upper bound count",
                "NumberOfTimePeriods": "period count",
                "LowerNumberOfTimePeriods": "lower bound period count",
                "UpperNumberOfTimePeriods": "upper bound period count",
                "TimePeriod": "Day | Week | Month | Year",
                "TimeSince_or_TimeOfEvent": "Since | During",
                "FrequencyChange": (
                    "Decreased | Frequent | Increased | Infrequent | Same"
                ),
                "PointInTime": (
                    "Birthday | DrugChange | LastClinic | Last_Month | "
                    "Last_Week | Last_Year | Surgery"
                ),
                "DayDate": "day number",
                "MonthDate": "month number",
                "YearDate": "year number",
                "AgeLower": "lower age",
                "AgeUpper": "upper age",
                "AgeUnit": "Year | Month",
            },
            "evidence": "Exact source substring supporting text and attributes.",
            "confidence": "low | medium | high",
            "rationale": "One brief sentence explaining the decision.",
        }
    ]
}


def _attribute_vocabulary() -> dict[str, Any]:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.prompt import (
        attribute_vocabulary,
    )

    return attribute_vocabulary(SEIZURE_FREQUENCY.name)


class ExECTv2SFVerifierSignature(dspy.Signature):
    """Review one clinical letter and a draft SeizureFrequency list."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter, draft SF mentions, and rules."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"mentions\": [{\"text\": ..., "
            "\"attributes\": {...}, \"evidence\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )

def _clinical_rules() -> list[str]:
    return load_sf_clinical_rules()


def _worked_examples() -> list[dict[str, Any]]:
    return load_sf_worked_examples()


def summarize_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"examples": 0}
    gold_letters = reconstruct_gold_letters(rows, entity_name=SEIZURE_FREQUENCY.name)
    pred_letters = reconstruct_pred_letters(rows, entity_name=SEIZURE_FREQUENCY.name)
    phrase = score_entity(
        gold_letters,
        pred_letters,
        SEIZURE_FREQUENCY.name,
        PHRASE_ONLY,
    )
    semantic = score_entity(
        gold_letters,
        pred_letters,
        SEIZURE_FREQUENCY.name,
        semantic_config_for(SEIZURE_FREQUENCY.name),
    )
    benchmark = score_entity(
        gold_letters,
        pred_letters,
        SEIZURE_FREQUENCY.name,
        benchmark_config_for(SEIZURE_FREQUENCY.name),
    )
    source_near = source_near_diagnostic(
        gold_letters,
        pred_letters,
        [SEIZURE_FREQUENCY.name],
        semantic_config_for,
    ).per_entity[SEIZURE_FREQUENCY.name]
    frequency = score_frequency_state(gold_letters, pred_letters)
    n_mentions_raw = sum(int(r.get("n_mentions_raw", 0)) for r in rows)
    n_evidence_invalid = sum(int(r.get("n_evidence_invalid", 0)) for r in rows)

    return {
        "examples": len(rows),
        "call_failures": sum(bool(r.get("call_error")) for r in rows),
        "parse_failures": sum(_has_blocking_parse_issue(r.get("parse_errors")) for r in rows),
        "n_draft_mentions": sum(int(r.get("n_draft_mentions", 0)) for r in rows),
        "n_mentions_raw": n_mentions_raw,
        "n_mentions_scored": sum(int(r.get("n_mentions_scored", 0)) for r in rows),
        "n_evidence_invalid": n_evidence_invalid,
        "evidence_validity_rate": (
            (n_mentions_raw - n_evidence_invalid) / n_mentions_raw if n_mentions_raw else 1.0
        ),
        "phrase_only": phrase.model_dump(),
        "semantic": semantic.model_dump(),
        "benchmark": benchmark.model_dump(),
        "source_near": source_near.model_dump(),
        "clinical_recovery": {
            "seizure_frequency": frequency.clinical_headline.model_dump(),
            "active_rate": frequency.active_rate.model_dump(),
            "seizure_free": frequency.seizure_free.model_dump(),
            "unknown": frequency.unknown.model_dump(),
            "target_headline_f1": 0.8,
        },
    }
