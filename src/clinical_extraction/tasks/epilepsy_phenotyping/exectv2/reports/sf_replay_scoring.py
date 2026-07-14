"""Shared row scoring for retained SeizureFrequency replay layers."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    _has_blocking_parse_issue,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    benchmark_config_for,
    score_entity,
    score_frequency_state,
    semantic_config_for,
    source_near_diagnostic,
)

from ..replay_rows import (
    reconstruct_gold_letters,
    reconstruct_pred_letters,
)


def summarize_sf_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Score saved or deterministically transformed SeizureFrequency rows."""

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
    n_mentions_raw = sum(int(row.get("n_mentions_raw", 0)) for row in rows)
    n_evidence_invalid = sum(int(row.get("n_evidence_invalid", 0)) for row in rows)

    return {
        "examples": len(rows),
        "call_failures": sum(bool(row.get("call_error")) for row in rows),
        "parse_failures": sum(
            _has_blocking_parse_issue(row.get("parse_errors")) for row in rows
        ),
        "n_draft_mentions": sum(int(row.get("n_draft_mentions", 0)) for row in rows),
        "n_candidate_spans": sum(int(row.get("n_candidate_spans", 0)) for row in rows),
        "n_mentions_raw": n_mentions_raw,
        "n_mentions_scored": sum(int(row.get("n_mentions_scored", 0)) for row in rows),
        "n_evidence_invalid": n_evidence_invalid,
        "evidence_validity_rate": (
            (n_mentions_raw - n_evidence_invalid) / n_mentions_raw
            if n_mentions_raw
            else 1.0
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
