"""Snapshot tests that pin model-facing prompt/schema contracts."""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from pathlib import Path

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as exectv2_structured,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    hybrid_structured_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm as llm_only_canonical_pipeline,
)

SNAPSHOT_DIR = Path(__file__).parent / "snapshots" / "prompt_contracts"
UPDATE_ENV_VAR = "UPDATE_PROMPT_SNAPSHOTS"

_NOTE_TEXT = (
    "Clinic note: known focal epilepsy. Two seizures per month over the last "
    "year. Last seizure was yesterday. Continues levetiracetam 500mg twice "
    "daily. MRI brain reported normal."
)


def _gan_record() -> GanFrequencyRecord:
    frequency_record = label_to_frequency_record("2 per month")
    return GanFrequencyRecord(
        source_row_index=1,
        note_text=_NOTE_TEXT,
        gold_label="2 per month",
        gold_reference="two seizures per month",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=frequency_record.normalized_label,
        gold_label_kind=frequency_record.kind,
        gold_yearly_bounds=frequency_record.yearly_bounds,
        gold_monthly_frequency=frequency_record.monthly_frequency,
    )


def _exect_letter() -> ExectLetter:
    return ExectLetter(letter_id="SNAP001", note_text=_NOTE_TEXT)


PROMPT_BUILDERS: dict[str, Callable[[], str | dict[str, object]]] = {
    "gan2026__hybrid_structured_events": lambda: hybrid_structured_events.build_prompt_input(
        _gan_record()
    ),
    "gan2026__hybrid_structured_events_v0.7": lambda: hybrid_structured_events.build_prompt_input(
        _gan_record(), prompt_version=hybrid_structured_events.PROMPT_VERSION_V0_7
    ),
    "gan2026__llm": lambda: llm_only_canonical_pipeline.build_prompt_input(
        _gan_record()
    ),
    "exectv2__structured_key_families": lambda: exectv2_structured.build_prompt_input(
        _exect_letter()
    ),
}


def _normalize(payload: str | dict[str, object]) -> str:
    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
        except (json.JSONDecodeError, ValueError):
            return payload if payload.endswith("\n") else payload + "\n"
        payload = parsed
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _snapshot_path(name: str) -> Path:
    return SNAPSHOT_DIR / f"{name}.txt"


def _updating() -> bool:
    return os.environ.get(UPDATE_ENV_VAR, "").lower() in {"1", "true", "yes"}


@pytest.mark.parametrize("name", sorted(PROMPT_BUILDERS))
def test_model_facing_contract_matches_snapshot(name: str) -> None:
    builder = PROMPT_BUILDERS[name]

    rendered = _normalize(builder())
    assert rendered == _normalize(builder()), f"{name}: builder output is non-deterministic"

    path = _snapshot_path(name)

    if _updating():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
        return

    assert path.exists(), (
        f"Missing snapshot for {name}: {path}. "
        f"Generate it with {UPDATE_ENV_VAR}=1 uv run pytest "
        "tests/test_prompt_contract_snapshots.py"
    )

    expected = path.read_text(encoding="utf-8")
    assert rendered == expected, (
        f"Model-facing contract '{name}' changed vs its committed snapshot.\n"
        "If this change is intentional, review the diff and regenerate with "
        f"{UPDATE_ENV_VAR}=1 uv run pytest tests/test_prompt_contract_snapshots.py"
    )


def test_every_builder_has_a_committed_snapshot() -> None:
    """No model-facing builder may be added without committing its snapshot."""
    if _updating():
        pytest.skip("snapshot update run")
    missing = [name for name in PROMPT_BUILDERS if not _snapshot_path(name).exists()]
    assert missing == [], f"builders without committed snapshots: {missing}"
