"""Investigations verifier prompt content and scoring."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    INVESTIGATIONS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    _has_blocking_parse_issue,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.runner import (
    reconstruct_gold_letters,
    reconstruct_pred_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    benchmark_config_for,
    score_entity,
    score_investigations_components,
    semantic_config_for,
    source_near_diagnostic,
)

PROMPT_VERSION = "exectv2_llm_investigations_verifier_v0.1"
PIPELINE_FAMILY = "exectv2_llm_investigations_verifier"
COMPONENT_OWNER = "llm_investigations_verifier"

TASK_TEXT = (
    "Review the clinical letter and draft Investigations mentions from "
    "the single structured key-entity extractor. Return final "
    "Investigations mentions only. You may keep, delete, edit, or add "
    "mentions, but every final mention must be supported by exact source "
    "evidence."
)

OUTPUT_SCHEMA = {
    "mentions": [
        {
            "text": "Clean investigation phrase owned by the verifier.",
            "attributes": {
                "MRI_Performed": "Yes | No",
                "MRI_Results": "Normal | Abnormal | Unknown",
                "CT_Performed": "Yes | No",
                "CT_Results": "Normal | Abnormal | Unknown",
                "EEG_Performed": "Yes | No",
                "EEG_Results": "Normal | Abnormal | Unknown",
                "EEG_Type": "Standard | SleepDeprived | VideoTelemetry",
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

    return attribute_vocabulary(INVESTIGATIONS.name)


class ExECTv2InvestigationsVerifierSignature(dspy.Signature):
    """Review one clinical letter and draft Investigations mentions."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter, draft Investigations mentions, and rules."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"mentions\": [{\"text\": ..., "
            "\"attributes\": {...}, \"evidence\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )

def _clinical_rules() -> list[str]:
    return [
        "Return only Investigations mentions. Do not emit Prescription, Diagnosis, or SF.",
        "Every final evidence value must be an exact substring of the letter.",
        "Do not emit CUI or CUIPhrase; projection is a deterministic layer.",
        (
            "The clinical headline is one key per modality: MRI, CT, or EEG, with "
            "performed status plus result and EEG type when supported."
        ),
        (
            "Emit completed historical tests. Omit planned, requested, arranged, "
            "future, or recommended tests unless a separate completed test is also "
            "stated."
        ),
        (
            "Do not return modality-only mentions for planned tests such as 'I will "
            "arrange an MRI', 'request EEG', or 'organise CT'."
        ),
        (
            "When a completed test has an explicit result, include the result. "
            "Normal/unremarkable/no abnormality/no epileptiform correlate -> Normal. "
            "Spike and wave, epileptiform discharges, slowing, gliosis, lesion, "
            "atrophy, cortical or white matter changes, abnormality -> Abnormal."
        ),
        (
            "If the letter says a completed test was done but gives no result, "
            "emit Performed='Yes' without a result only when the source gives no "
            "result words nearby."
        ),
        (
            "For 'no MRI', 'never had MRI', or 'MRI not performed', emit "
            "MRI_Performed='No'. Use the same rule for CT and EEG."
        ),
        (
            "For video EEG, VEEG, video-telemetry, or telemetry, set "
            "EEG_Type='VideoTelemetry'. For sleep-deprived EEG, set "
            "EEG_Type='SleepDeprived'. Otherwise omit EEG_Type unless the source "
            "supports Standard."
        ),
        (
            "Do not merge different modalities into one mention unless the same "
            "source span explicitly states both and each has its own attributes."
        ),
        "Return exactly one JSON object. No markdown code fences.",
    ]

def _worked_examples() -> list[dict[str, Any]]:
    return [
        {
            "note_fragment": "I will arrange an MRI scan of the brain and an EEG.",
            "draft": [{"text": "MRI scan"}, {"text": "EEG"}],
            "correct": [],
        },
        {
            "note_fragment": "MRI 2016 showed left-sided gliosis. EEG was normal.",
            "draft": [],
            "correct": [
                {
                    "text": "MRI 2016 showed left-sided gliosis",
                    "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Abnormal"},
                    "evidence": "MRI 2016 showed left-sided gliosis",
                    "confidence": "high",
                    "rationale": "Gliosis is an abnormal MRI result.",
                },
                {
                    "text": "EEG was normal",
                    "attributes": {"EEG_Performed": "Yes", "EEG_Results": "Normal"},
                    "evidence": "EEG was normal",
                    "confidence": "high",
                    "rationale": "The EEG result is explicitly normal.",
                },
            ],
        },
        {
            "note_fragment": "EEG showed generalised spike and wave. MRI was normal.",
            "draft": [{"text": "EEG"}, {"text": "MRI"}],
            "correct": [
                {
                    "text": "EEG showed generalised spike and wave",
                    "attributes": {"EEG_Performed": "Yes", "EEG_Results": "Abnormal"},
                    "evidence": "EEG showed generalised spike and wave",
                    "confidence": "high",
                    "rationale": "Spike and wave is an abnormal EEG result.",
                },
                {
                    "text": "MRI was normal",
                    "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Normal"},
                    "evidence": "MRI was normal",
                    "confidence": "high",
                    "rationale": "The MRI result is explicitly normal.",
                },
            ],
        },
        {
            "note_fragment": "Video EEG captured events with no epileptiform correlate.",
            "draft": [],
            "correct": [
                {
                    "text": "Video EEG captured events with no epileptiform correlate",
                    "attributes": {
                        "EEG_Performed": "Yes",
                        "EEG_Results": "Normal",
                        "EEG_Type": "VideoTelemetry",
                    },
                    "evidence": "Video EEG captured events with no epileptiform correlate",
                    "confidence": "medium",
                    "rationale": (
                        "Video EEG is completed telemetry with no epileptiform "
                        "correlate."
                    ),
                }
            ],
        },
        {
            "note_fragment": "She has never had an MRI brain scan.",
            "draft": [],
            "correct": [
                {
                    "text": "never had an MRI brain scan",
                    "attributes": {"MRI_Performed": "No"},
                    "evidence": "never had an MRI brain scan",
                    "confidence": "medium",
                    "rationale": "The source explicitly says MRI was not performed.",
                }
            ],
        },
    ]

def summarize_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"examples": 0}
    gold_letters = reconstruct_gold_letters(rows, entity_name=INVESTIGATIONS.name)
    pred_letters = reconstruct_pred_letters(rows, entity_name=INVESTIGATIONS.name)
    investigations = score_investigations_components(gold_letters, pred_letters)
    source_near = source_near_diagnostic(
        gold_letters,
        pred_letters,
        [INVESTIGATIONS.name],
        semantic_config_for,
    ).per_entity[INVESTIGATIONS.name]
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
        "clinical_recovery": {
            "investigations": investigations.clinical_headline.model_dump(),
            "target_headline_f1": 0.8,
        },
        "source_near": source_near.model_dump(),
        "format_layers": {
            "phrase_only": score_entity(
                gold_letters,
                pred_letters,
                INVESTIGATIONS.name,
                PHRASE_ONLY,
            ).per_item.model_dump(),
            "semantic": score_entity(
                gold_letters,
                pred_letters,
                INVESTIGATIONS.name,
                semantic_config_for(INVESTIGATIONS.name),
            ).per_item.model_dump(),
            "benchmark": score_entity(
                gold_letters,
                pred_letters,
                INVESTIGATIONS.name,
                benchmark_config_for(INVESTIGATIONS.name),
            ).per_item.model_dump(),
        },
    }
