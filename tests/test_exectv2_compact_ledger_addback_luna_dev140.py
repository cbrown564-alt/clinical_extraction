"""Contract tests for the Compact add-back Luna dev140 runner."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from scripts.run_exectv2_compact_ledger_addback_luna_dev140 import (
    decide_arm,
    verify_payload,
)


def test_addback_payload_check_does_not_change_default() -> None:
    before = structured.PROMPT_VERSION
    payload = verify_payload()
    assert payload["ok"] is True
    assert payload["control"] == structured.COMPACT_LEDGER
    assert payload["default_prompt_version"] == structured.COMPACT_LEDGER
    assert structured.PROMPT_VERSION == before == structured.COMPACT_LEDGER
    chars = payload["payload_chars"]
    assert chars["compact"] < chars["plus_encoding"] < chars["plus_encoding_examples"]


def test_revise_when_parse_or_schema_fails() -> None:
    assert decide_arm({"parse": 1, "schema": 0}) == "revise"
    assert decide_arm({"parse": 0, "schema": 2}) == "revise"
    assert decide_arm({"parse": 0, "schema": 0}) == "descriptive"
