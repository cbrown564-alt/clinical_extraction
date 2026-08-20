"""Pin named development rung scores. Not holdout."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_gan_dev750_rungs_use_selected_evidence_as_format() -> None:
    payload = json.loads(
        (
            ROOT / "paper_experiments/gan/rungs/grok46/dev750/comparison.json"
        ).read_text(encoding="utf-8")
    )
    check = payload["format_only_check"]
    assert check["selected_event_id_changes"] == 0
    assert check["used_as_rung_3"] is True
    assert check["repair_mode"] == "selected_evidence_derivation"
    rungs = payload["rungs"]
    assert rungs["llm_schema"]["purist_correct"] == 371
    assert rungs["llm_format"]["purist_correct"] == 603
    assert rungs["llm_post"]["purist_correct"] == 671
    assert rungs["rules_only"]["purist_correct"] == 669
    assert payload["shared_raw_output"] == "gan_llm_with_rules"
    assert payload["claim_boundary"].startswith("Gan development")


def test_exect_dev140_rungs_score_format_render_not_materialized_format_only() -> None:
    payload = json.loads(
        (
            ROOT / "paper_experiments/exect/rungs/grok46/dev140/comparison.json"
        ).read_text(encoding="utf-8")
    )
    check = payload["format_only_check"]
    assert check["surface"] == "format_render"
    assert check["materialized_format_only_differs_from_rung3"]
    assert "SF projection and unknown suppression off" in check["note"]
    rungs = payload["rungs"]
    assert rungs["llm_schema"]["clinical_fact_f1"] == 0.8212
    assert rungs["llm_format"]["clinical_fact_f1"] == 0.8212
    assert rungs["llm_post"]["clinical_fact_f1"] == 0.904
    assert rungs["rules_only"]["clinical_fact_f1"] == 0.9042
    assert rungs["llm_pre_post"]["clinical_fact_f1"] == 0.8998
    assert payload["shared_raw_output"] == "exect_llm_only"
    assert payload["claim_boundary"].startswith("ExECT development")
