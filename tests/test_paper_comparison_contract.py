"""Always-on firewall for the living paper comparison envelope."""

from __future__ import annotations

import pytest

from clinical_extraction.paper.comparison_contract import (
    EXECT_SCORER,
    FORBIDDEN_LIVING_PRIMARY,
    GAN_SCORER,
    HEADLINE_STAGE,
    LIVING_SCHEMA_VERSION,
    adapt_legacy_comparison,
    attach_living_envelope,
    exect_stage,
    gan_stage,
    living_exect_stages_from_surfaces,
    stage_metric,
    validate_living_comparison,
)


def test_living_gan_envelope_names_select_as_headline() -> None:
    n = 450
    stages = {
        "extract": gan_stage(purist_correct=354, n=n, pragmatic_correct=366),
        "encode": gan_stage(purist_correct=359, n=n, pragmatic_correct=370),
        "select": gan_stage(purist_correct=373, n=n, pragmatic_correct=380),
    }
    payload = attach_living_envelope(
        {
            "model_slug": "gemini37flash",
            "split": "test450",
            "row_policy": "aggregate_only",
        },
        method="gan_llm_extract",
        stages=stages,
        replay_mode="live",
        prompt_version="gan_llm_extract",
    )
    validate_living_comparison(payload)
    assert payload["living_schema_version"] == LIVING_SCHEMA_VERSION
    assert payload["task"] == "gan2026"
    assert payload["cell"] == 3
    assert payload["headline"] == HEADLINE_STAGE
    assert payload["scorer"] == GAN_SCORER
    assert payload["score"]["purist_correct"] == 373
    assert payload["score"]["purist_accuracy"] == 0.8289


def test_living_exect_envelope_forbids_headline_primary_names() -> None:
    stages = {
        "extract": exect_stage(four_family_micro_f1=0.8491),
        "encode": exect_stage(four_family_micro_f1=0.8491),
        "select": exect_stage(four_family_micro_f1=0.8674),
    }
    payload = attach_living_envelope(
        {
            "model_slug": "gemini37flash",
            "split": "test60",
            "row_policy": "aggregate_only",
        },
        method="exect_llm_extract",
        stages=stages,
        replay_mode="live",
        prompt_version="exect_llm_extract",
    )
    assert payload["scorer"] == EXECT_SCORER
    assert payload["score"]["four_family_micro_f1"] == 0.8674
    assert FORBIDDEN_LIVING_PRIMARY.isdisjoint(payload["score"])
    with pytest.raises(ValueError, match="four_family_headline_f1"):
        validate_living_comparison(
            {
                **payload,
                "score": {"four_family_headline_f1": 0.8674},
            }
        )


def test_adapter_reads_legacy_exect_hybrid_headline_as_select() -> None:
    adapted = adapt_legacy_comparison(
        {
            "method": "exect_llm_extract",
            "model_slug": "deepseek_v4_flash",
            "split": "dev140",
            "row_count": 140,
            "row_policy": "development_review_permitted",
            "live": True,
            "prompt_version": "exect_llm_extract",
            "scorer": "clinical_inventory_unit_keys",
            "arms": {
                "exect_llm_extract": {
                    "raw_headline_f1": 0.7907,
                    "hybrid_headline_f1": 0.8397,
                    "raw_family_f1": {"Diagnosis": 0.6878},
                    "hybrid_family_f1": {"Diagnosis": 0.779},
                }
            },
        }
    )
    assert adapted is not None
    assert stage_metric(adapted, "extract") == 0.7907
    assert stage_metric(adapted, "select") == 0.8397
    assert adapted["score"]["four_family_micro_f1"] == 0.8397


def test_live_exect_surfaces_become_extract_and_select_stops() -> None:
    stages = living_exect_stages_from_surfaces(
        {
            "raw_headline_f1": 0.7907,
            "hybrid_headline_f1": 0.8397,
            "raw_family_f1": {"Diagnosis": 0.6878},
            "hybrid_family_f1": {"Diagnosis": 0.779},
        }
    )
    payload = attach_living_envelope(
        {
            "model_slug": "deepseek_v4_flash",
            "split": "dev140",
            "row_policy": "development_review_permitted",
        },
        method="exect_llm_extract",
        stages=stages,
        replay_mode="live",
        prompt_version="exect_llm_extract",
    )
    assert payload["stages"]["extract"]["four_family_micro_f1"] == 0.7907
    assert payload["stages"]["encode"]["four_family_micro_f1"] == 0.7907
    assert payload["stages"]["select"]["four_family_micro_f1"] == 0.8397
    assert payload["headline"] == "select"
