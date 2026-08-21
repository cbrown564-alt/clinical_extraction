"""Pin named development cell scores. Not holdout.

Sealed comparison.json may still use pre-2026-08-21 identity strings;
normalize on read.
"""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.paper.rungs import (
    normalize_cell_id,
    normalize_repair_mode,
    normalize_rungs_payload,
)

ROOT = Path(__file__).resolve().parents[1]


def test_gan_dev750_rungs_use_selected_evidence_as_encode() -> None:
    payload = json.loads(
        (
            ROOT / "paper_experiments/gan/rungs/grok46/dev750/comparison.json"
        ).read_text(encoding="utf-8")
    )
    check = payload["format_only_check"]
    assert check["selected_event_id_changes"] == 0
    assert check["used_as_rung_3"] is True
    assert normalize_repair_mode(check["repair_mode"]) == "llm_encode"
    rungs = normalize_rungs_payload(payload["rungs"])
    assert rungs["llm_extract"]["purist_correct"] == 371
    assert rungs["llm_encode"]["purist_correct"] == 603
    assert rungs["llm_select"]["purist_correct"] == 671
    assert rungs["rules_only"]["purist_correct"] == 669
    assert payload["shared_raw_output"] == "gan_llm_with_rules"
    assert payload["claim_boundary"].startswith("Gan development")
    # Sealed file may still emit the old string.
    assert check["repair_mode"] in {
        "llm_encode",
        "encode",
        "selected_evidence_derivation",
    }
    assert normalize_cell_id("llm_format") == "llm_encode"


def test_exect_dev140_rungs_score_format_render_not_materialized_format_only() -> None:
    payload = json.loads(
        (
            ROOT / "paper_experiments/exect/rungs/grok46/dev140/comparison.json"
        ).read_text(encoding="utf-8")
    )
    check = payload["format_only_check"]
    assert check["surface"] == "format_render"
    assert check["same_as_schema"] is False
    assert "same-fact format" in check["note"]
    rungs = normalize_rungs_payload(payload["rungs"])
    assert rungs["llm_extract"]["clinical_fact_f1"] == 0.6485
    assert rungs["llm_encode"]["clinical_fact_f1"] == 0.8197
    assert rungs["llm_select"]["clinical_fact_f1"] == 0.904
    assert rungs["rules_only"]["clinical_fact_f1"] == 0.9042
    assert rungs["llm_pre_post"]["clinical_fact_f1"] == 0.8998
    assert payload["shared_raw_output"] == "exect_llm_only"
    assert payload["claim_boundary"].startswith("ExECT development")
