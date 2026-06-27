"""Diagnosis verifier prompt content and scoring."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    _has_blocking_parse_issue,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.runner import (
    reconstruct_gold_letters,
    reconstruct_pred_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompts.diagnosis_verification.loader import (
    load_verifier_clinical_rules,
    load_verifier_worked_examples,
)

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    benchmark_config_for,
    score_concept_identity,
    score_entity,
    semantic_config_for,
    source_near_diagnostic,
)

PROMPT_VERSION = "exectv2_llm_diagnosis_verifier_v0.6"
PIPELINE_FAMILY = "exectv2_llm_diagnosis_verifier"
COMPONENT_OWNER = "llm_diagnosis_verifier"

TASK_TEXT = (
    "Review the clinical letter and the draft Diagnosis mentions from the "
    "single structured key-entity extractor. Return the final Diagnosis "
    "mentions only. You may keep, delete, edit, or add mentions, but every "
    "final mention must be supported by exact source evidence."
)

OUTPUT_SCHEMA = {
    "mentions": [
        {
            "text": "Clean core Diagnosis concept phrase owned by the verifier.",
            "attributes": {
                "DiagCategory": "Epilepsy | MultipleSeizures | SingleSeizure",
                "Certainty": "1 | 2 | 3 | 4 | 5",
                "Negation": "Affirmed | Negated",
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

    return attribute_vocabulary(DIAGNOSIS.name)


class ExECTv2DiagnosisVerifierSignature(dspy.Signature):
    """Review one clinical letter and a draft Diagnosis list.

    Return exactly one JSON object with a 'mentions' list. No markdown wrapper.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter, draft Diagnosis mentions, and rules."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"mentions\": [{\"text\": ..., "
            "\"attributes\": {...}, \"evidence\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )


def _clinical_rules() -> list[str]:
    return load_verifier_clinical_rules()


def _worked_examples() -> list[dict[str, Any]]:
    return load_verifier_worked_examples()


def summarize_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    if n == 0:
        return {"examples": 0}
    n_mentions_raw = sum(int(r.get("n_mentions_raw", 0)) for r in rows)
    n_evidence_invalid = sum(int(r.get("n_evidence_invalid", 0)) for r in rows)
    gold_letters = reconstruct_gold_letters(rows, entity_name=DIAGNOSIS.name)
    pred_letters = reconstruct_pred_letters(rows, entity_name=DIAGNOSIS.name)

    phrase = score_entity(gold_letters, pred_letters, DIAGNOSIS.name, PHRASE_ONLY)
    semantic = score_entity(
        gold_letters,
        pred_letters,
        DIAGNOSIS.name,
        semantic_config_for(DIAGNOSIS.name),
    )
    benchmark = score_entity(
        gold_letters,
        pred_letters,
        DIAGNOSIS.name,
        benchmark_config_for(DIAGNOSIS.name),
    )
    source_near = source_near_diagnostic(
        gold_letters,
        pred_letters,
        [DIAGNOSIS.name],
        semantic_config_for,
    ).per_entity[DIAGNOSIS.name]
    clinical = score_concept_identity(
        gold_letters,
        pred_letters,
        DIAGNOSIS.name,
    ).concept_assertion

    return {
        "examples": n,
        "call_failures": sum(bool(r.get("call_error")) for r in rows),
        "parse_failures": sum(_has_blocking_parse_issue(r.get("parse_errors")) for r in rows),
        "n_draft_mentions": sum(int(r.get("n_draft_mentions", 0)) for r in rows),
        "n_mentions_raw": n_mentions_raw,
        "n_mentions_scored": sum(int(r.get("n_mentions_scored", 0)) for r in rows),
        "n_evidence_invalid": n_evidence_invalid,
        "evidence_validity_rate": (
            round((n_mentions_raw - n_evidence_invalid) / n_mentions_raw, 4)
            if n_mentions_raw
            else 1.0
        ),
        "scores": {
            "phrase_only": _entity_score_to_dict(phrase),
            "semantic": _entity_score_to_dict(semantic),
            "benchmark": _entity_score_to_dict(benchmark),
        },
        "source_near": {
            "overlap": _prf1_to_dict(source_near.overlap),
            "attribute_agreement_tp": source_near.attribute_agreement_tp,
            "attribute_agreement_total": source_near.attribute_agreement_total,
            "attribute_agreement_rate": round(source_near.attribute_agreement_rate, 4),
        },
        "clinical_recovery": {
            "target_headline_f1": 0.80,
            "diagnosis": _prf1_to_dict(clinical),
        },
    }


def _entity_score_to_dict(score: Any) -> dict[str, Any]:
    return {
        "per_item": _prf1_to_dict(score.per_item),
        "per_letter": _prf1_to_dict(score.per_letter),
    }


def _prf1_to_dict(score: Any) -> dict[str, Any]:
    return {
        "precision": round(score.precision, 4),
        "recall": round(score.recall, 4),
        "f1": round(score.f1, 4),
        "tp": score.tp,
        "fp": score.fp,
        "fn": score.fn,
    }
