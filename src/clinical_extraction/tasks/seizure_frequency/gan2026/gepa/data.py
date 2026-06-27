"""Build GEPA train/val sets from the frozen Gan 2026 split protocol.

Split intent (``gan2026_split_v1``) is honored exactly:

* ``train`` (300)      optimizer training only -> GEPA trainset.
* ``validation`` (750) development surface     -> GEPA valset (Pareto) + final eval.
* ``test`` (450)       locked holdout          -> never touched here.
"""

from __future__ import annotations

import dspy

from clinical_extraction.tasks.seizure_frequency.gan2026 import data as gan_data
from clinical_extraction.tasks.seizure_frequency.gan2026.gepa.program import OUTPUT_SCHEMA_JSON
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import boundary_band, map_purist


def _example(record: gan_data.GanFrequencyRecord) -> dspy.Example:
    return dspy.Example(
        note_text=record.note_text,
        output_schema=OUTPUT_SCHEMA_JSON,
        source_row_index=record.source_row_index,
        gold_label=record.gold_label,
        gold_monthly_frequency=record.gold_monthly_frequency,
        gold_purist_category=str(map_purist(record.gold_monthly_frequency)),
        gold_band=boundary_band(record.gold_monthly_frequency),
    ).with_inputs("note_text", "output_schema")


def load_examples(split: str, *, limit: int | None = None) -> list[dspy.Example]:
    """Load scorable rows for a split as input-tagged ``dspy.Example`` objects."""

    records = [r for r in gan_data.load_records_for_split(split) if r.row_ok]
    if limit is not None:
        records = records[:limit]
    return [_example(r) for r in records]


def load_trainset(*, limit: int | None = None) -> list[dspy.Example]:
    return load_examples("train", limit=limit)


def load_valset(*, limit: int | None = None) -> list[dspy.Example]:
    return load_examples("validation", limit=limit)
