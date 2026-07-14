"""Snapshot tests that pin model-facing prompt/schema contracts.

Guardrail FM4 (``docs/research/predecessor_lessons/01_failure_modes_and_guardrails.md``):
prompt and schema contract bugs can dominate architecture. The recorded
predecessor disaster was a verifier prompt that silently changed medication
output from structured objects to flat strings, collapsing medication
full-tuple F1 from ~0.60 to 0.018 (a 33x collapse) with no architectural
change. The existing ``test_gan2026_llm_prompt_hygiene`` suite checks that
model-facing text does not *leak internal protocol language*, but nothing
guards against a contract *drifting* (an output schema field disappearing, an
adapter clause being dropped, a dedup rule being reworded). These snapshot
tests close that gap: they render each deterministic, no-LLM prompt builder
against a fixed fixture and diff it against a committed snapshot, so any change
to a model-facing contract becomes a reviewable diff in the pull request.

To intentionally update a contract: review the diff, then regenerate with

    UPDATE_PROMPT_SNAPSHOTS=1 uv run pytest tests/test_prompt_contract_snapshots.py

and commit the updated ``tests/snapshots/prompt_contracts/*.txt`` files
alongside the code change.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from pathlib import Path

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    diagnosis_decomposer as exectv2_diagnosis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as exectv2_structured,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    hybrid_structured_events,
    llm_only_canonical_pipeline,
)

SNAPSHOT_DIR = Path(__file__).parent / "snapshots" / "prompt_contracts"
UPDATE_ENV_VAR = "UPDATE_PROMPT_SNAPSHOTS"

# A single fixed note shared by every fixture so a snapshot diff reflects a
# contract change, never input drift. Kept deliberately small but exercising
# seizure-type, frequency, and temporal cues.
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


# Each entry renders one model-facing contract from a fixed fixture with no LLM
# call. Name -> zero-arg callable returning the payload (str or JSON-able dict).
PROMPT_BUILDERS: dict[str, Callable[[], str | dict[str, object]]] = {
    # Gan 2026 seizure-frequency surfaces.
    "gan2026__hybrid_structured_events": lambda: hybrid_structured_events.build_prompt_input(
        _gan_record()
    ),
    "gan2026__llm_only_canonical_pipeline": lambda: llm_only_canonical_pipeline.build_prompt_input(
        _gan_record()
    ),
    # ExECTv2 broad-phenotyping surfaces.
    "exectv2__structured_key_families": lambda: exectv2_structured.build_prompt_input(
        _exect_letter()
    ),
    "exectv2__diagnosis_decomposer": lambda: exectv2_diagnosis.build_prompt_input(
        _exect_letter(), []
    ),
}


def _normalize(payload: str | dict[str, object]) -> str:
    """Render a payload to stable, human-reviewable snapshot text.

    Dict payloads and JSON-string payloads are pretty-printed with sorted keys
    so a contract diff reads line-by-line. Non-JSON strings are stored verbatim.
    """
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
    # Render a second time to catch per-call non-determinism (set ordering,
    # dict insertion order, timestamps) before it is baked into a snapshot.
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
