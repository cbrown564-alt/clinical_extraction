"""Contract tests for the six-model Compact-ledger dev140 runner."""

from __future__ import annotations

import json

import pytest

from clinical_extraction.core.six_model_roster import SUCCESSOR_SIX_MODELS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from scripts.run_exectv2_compact_ledger_six_model_dev140 import (
    HOSTED_LIVE_SLUGS,
    HOSTED_TEST60_SLUGS,
    LOCAL_SLUGS,
    MODELS,
    PROTOCOL,
    ROOT,
    STUDY_DIR,
    TEST60_CONTROLS,
    TEST60_PROTOCOL,
    TEST60_STUDY_DIR,
    verify_study,
)

pytestmark = pytest.mark.local_corpus


def _exect_dev140_controls() -> dict[str, object]:
    sources = json.loads((ROOT / "experiments/current_stack/SOURCES.json").read_text())
    return sources["cells"]["exect_dev140"]["sources"]


def test_roster_matches_successor_six_models() -> None:
    assert tuple(MODELS) == tuple(item["slug"] for item in SUCCESSOR_SIX_MODELS)
    for item in SUCCESSOR_SIX_MODELS:
        spec = MODELS[item["slug"]]
        assert spec.model == item["model"]
        assert spec.label == item["label"]


def test_controls_are_selected_full_ledger_sidecars() -> None:
    controls = _exect_dev140_controls()
    for slug, spec in MODELS.items():
        source = controls[slug]
        assert source["selected"] is True
        assert spec.control_structured == ROOT / source["structured"]
        assert spec.control_structured.is_file()
        assert "test60" not in spec.control_structured.as_posix()


def test_luna_is_replay_and_hosted_live_slugs_are_fixed() -> None:
    assert MODELS["gpt56luna"].candidate_structured is not None
    assert MODELS["gpt56luna"].candidate_structured.is_file()
    assert HOSTED_LIVE_SLUGS == ("gpt56sol", "gemini37flash", "deepseek_v4_flash")
    assert LOCAL_SLUGS == ("qwen36_35b", "gemma4_26b")
    for slug in HOSTED_LIVE_SLUGS + LOCAL_SLUGS:
        assert MODELS[slug].candidate_structured is None


def test_verify_study_does_not_change_default_or_authorize_test60() -> None:
    before = structured.PROMPT_VERSION
    payload = verify_study()
    assert payload["ok"] is True
    assert payload["n_rules"] == 67
    assert payload["n_examples"] == 0
    assert payload["split"] == "dev140"
    assert payload["test60_authorized"] is False
    assert payload["protocol"] == PROTOCOL
    assert payload["study_dir"] == STUDY_DIR.relative_to(ROOT).as_posix()
    assert structured.PROMPT_VERSION == before == structured.COMPACT_LEDGER


def test_test60_verify_is_aggregate_only_for_authorized_hosted_models() -> None:
    before = structured.PROMPT_VERSION
    payload = verify_study(split="test60")
    assert payload["ok"] is True
    assert payload["split"] == "test60"
    assert payload["row_count"] == 59
    assert payload["row_policy"] == "aggregate_only"
    assert payload["test60_authorized"] is True
    assert payload["protocol"] == TEST60_PROTOCOL
    assert payload["study_dir"] == TEST60_STUDY_DIR.relative_to(ROOT).as_posix()
    assert payload["hosted_live"] == list(HOSTED_TEST60_SLUGS)
    assert HOSTED_TEST60_SLUGS == (
        "gpt56luna",
        "gemini37flash",
        "gpt56sol",
        "deepseek_v4_flash",
    )
    assert structured.PROMPT_VERSION == before == structured.COMPACT_LEDGER


def test_test60_controls_are_selected_current_stack_sidecars() -> None:
    sources = json.loads((ROOT / "experiments/current_stack/SOURCES.json").read_text())
    test_sources = sources["cells"]["exect_test60"]["sources"]
    assert TEST60_CONTROLS["deepseek_v4_flash"] == (
        ROOT / test_sources["deepseek_v4_flash_0731"]["structured"]
    )
    for slug in HOSTED_TEST60_SLUGS:
        key = "deepseek_v4_flash_0731" if slug == "deepseek_v4_flash" else slug
        source = test_sources[key]
        assert source["selected"] is True
        assert TEST60_CONTROLS[slug] == ROOT / source["structured"]
        assert TEST60_CONTROLS[slug].is_file()
