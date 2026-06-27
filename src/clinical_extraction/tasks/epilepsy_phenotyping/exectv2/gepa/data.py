"""Build GEPA train/val sets from the frozen ExECTv2 split protocol.

``exectv2_split_v1`` only defines ``dev`` (140) and ``test`` (60). Mirroring the
Gan intent ("train = optimizer-only, test untouched"), this module sub-splits the
development surface deterministically into:

* GEPA ``trainset``   optimizer training only (default first 90 of a seeded shuffle).
* GEPA ``valset``      Pareto/candidate selection (default next 50).

The locked ``test`` split is NEVER loaded here. Final evaluation runs over the
full ``dev`` surface (a superset of the valset, so the headline is mildly
optimistic versus a fully disjoint split — recorded as a development-only number).
"""

from __future__ import annotations

import random

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program import OUTPUT_SCHEMA_JSON

#: Deterministic sub-split of the 140-letter dev surface.
DEV_SUBSPLIT_SEED = 20260627
DEFAULT_TRAINSET_SIZE = 90


def _example(letter: ExectLetter) -> dspy.Example:
    example = dspy.Example(
        letter_text=letter.note_text,
        output_schema=OUTPUT_SCHEMA_JSON,
        letter_id=letter.letter_id,
        # The full gold letter is carried for the metric: it supplies note_text for
        # evidence gating and the gold key-entity annotations for clinical_headline
        # scoring. It is not an input field, so the optimizer never sees the gold.
        letter=letter,
    ).with_inputs("letter_text", "output_schema")
    return example


def _shuffled_dev() -> list[ExectLetter]:
    letters = sorted(load_letters_for_split("dev"), key=lambda letter: letter.letter_id)
    rng = random.Random(DEV_SUBSPLIT_SEED)
    rng.shuffle(letters)
    return letters


def load_trainset(*, trainset_size: int = DEFAULT_TRAINSET_SIZE) -> list[dspy.Example]:
    """First ``trainset_size`` letters of the seeded dev shuffle (optimizer-only)."""

    return [_example(letter) for letter in _shuffled_dev()[:trainset_size]]


def load_valset(
    *,
    trainset_size: int = DEFAULT_TRAINSET_SIZE,
    limit: int | None = None,
) -> list[dspy.Example]:
    """Letters after the trainset boundary of the seeded dev shuffle (selection)."""

    valset = [_example(letter) for letter in _shuffled_dev()[trainset_size:]]
    if limit is not None:
        valset = valset[:limit]
    return valset


def load_dev_letters() -> list[ExectLetter]:
    """Full dev surface (140), id-ordered, for final evaluation. NOT the test split."""

    return sorted(load_letters_for_split("dev"), key=lambda letter: letter.letter_id)
