"""Contract tests for the local Compact Gemma then Qwen 3.8 queue."""

from __future__ import annotations

import pytest

from clinical_extraction.core.six_model_roster import SUCCESSOR_SIX_MODELS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from scripts.run_exectv2_compact_ledger_living_hosted_dev140 import (
    STUDY_DIR as HOSTED_STUDY_DIR,
)
from scripts.run_exectv2_compact_ledger_living_hosted_dev140 import (
    TEST60_STUDY_DIR as HOSTED_TEST60_STUDY_DIR,
)
from scripts.run_exectv2_compact_ledger_local_dev140 import (
    CANDIDATE_VERSION,
    LOCAL_SLUGS,
    MODELS,
    PROTOCOL,
    QUEUE,
    ROOT,
    STUDY_DIR,
    TEST60_CONTROLS,
    TEST60_PROTOCOL,
    TEST60_SCRATCH_DIR,
    TEST60_STUDY_DIR,
    control_path,
    verify_study,
)
from scripts.run_exectv2_compact_ledger_six_model_dev140 import (
    CANDIDATE_VERSION as DUMP_CANDIDATE_VERSION,
)
from scripts.run_exectv2_compact_ledger_six_model_dev140 import (
    STUDY_DIR as DUMP_STUDY_DIR,
)

pytestmark = pytest.mark.local_corpus


def test_living_compact_queue_is_gemma_then_qwen38() -> None:
    assert CANDIDATE_VERSION == structured.COMPACT_LEDGER
    assert DUMP_CANDIDATE_VERSION == (
        structured.PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES
    )
    assert LOCAL_SLUGS == ("gemma4_26b", "qwen38_27b")
    assert tuple(MODELS) == LOCAL_SLUGS
    assert QUEUE == (
        ("gemma4_26b", "dev140"),
        ("gemma4_26b", "test60"),
        ("qwen38_27b", "dev140"),
        ("qwen38_27b", "test60"),
    )
    assert MODELS["gemma4_26b"].model == "ollama_chat/gemma4:26b"
    assert MODELS["qwen38_27b"].model == "ollama_chat/qwen3.8:27b"
    assert MODELS["qwen38_27b"].label == "Qwen 3.8 27B"
    assert MODELS["qwen38_27b"].num_ctx == 32768
    assert MODELS["gemma4_26b"].num_ctx == 65536
    assert "qwen38_27b" not in {item["slug"] for item in SUCCESSOR_SIX_MODELS}
    assert STUDY_DIR != HOSTED_STUDY_DIR
    assert STUDY_DIR != DUMP_STUDY_DIR
    assert STUDY_DIR.name == "exectv2_compact_ledger_local_dev140_20260817"
    assert PROTOCOL.endswith("compact_ledger_local_gemma_qwen38_protocol_2026-08-17.md")


def test_verify_study_uses_authored_compact_and_does_not_change_default() -> None:
    before = structured.PROMPT_VERSION
    payload = verify_study()
    assert payload["ok"] is True
    assert payload["candidate"] == structured.COMPACT_LEDGER
    assert payload["n_rules"] == 67
    assert payload["n_examples"] == 0
    assert payload["authored_order"] is True
    assert payload["drops_research_metadata"] is True
    assert payload["split"] == "dev140"
    assert payload["test60_authorized"] is False
    assert payload["protocol"] == PROTOCOL
    assert payload["study_dir"] == STUDY_DIR.relative_to(ROOT).as_posix()
    assert payload["local"] == list(LOCAL_SLUGS)
    assert payload["default_prompt_version"] == structured.COMPACT_LEDGER
    assert structured.PROMPT_VERSION == before == structured.COMPACT_LEDGER
    assert control_path("gemma4_26b", "dev140") == MODELS["gemma4_26b"].control_structured
    assert control_path("qwen38_27b", "dev140") == MODELS["qwen38_27b"].control_structured


def test_test60_verify_is_aggregate_only_living_compact() -> None:
    before = structured.PROMPT_VERSION
    payload = verify_study(split="test60")
    assert payload["ok"] is True
    assert payload["candidate"] == structured.COMPACT_LEDGER
    assert payload["split"] == "test60"
    assert payload["row_count"] == 59
    assert payload["row_policy"] == "aggregate_only"
    assert payload["test60_authorized"] is True
    assert payload["protocol"] == TEST60_PROTOCOL
    assert payload["study_dir"] == TEST60_STUDY_DIR.relative_to(ROOT).as_posix()
    assert payload["scratch_dir"] == TEST60_SCRATCH_DIR.relative_to(ROOT).as_posix()
    assert TEST60_STUDY_DIR != HOSTED_TEST60_STUDY_DIR
    assert payload["local"] == list(LOCAL_SLUGS)
    assert payload["authored_order"] is True
    assert payload["drops_research_metadata"] is True
    assert payload["default_prompt_version"] == structured.COMPACT_LEDGER
    assert control_path("gemma4_26b", "test60") == TEST60_CONTROLS["gemma4_26b"]
    assert control_path("qwen38_27b", "test60") == TEST60_CONTROLS["qwen38_27b"]
    assert "test60" not in MODELS["gemma4_26b"].control_structured.as_posix()
    assert structured.PROMPT_VERSION == before == structured.COMPACT_LEDGER
