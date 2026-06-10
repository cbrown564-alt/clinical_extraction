from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from clinical_extraction.core.evidence import clean_semantically_neutral_text_artifacts

DEFAULT_DATA_DIR = Path("data/ExECTv2 (2025)")
DEFAULT_JSON_DIR = DEFAULT_DATA_DIR / "Json"
DEFAULT_TEXT_DIR = DEFAULT_DATA_DIR / "Gold1-200_corrected_spelling"
DEFAULT_SPLITS_DIR = DEFAULT_DATA_DIR / "splits"
DEFAULT_SPLIT_MANIFEST = DEFAULT_SPLITS_DIR / "exectv2_split_v1.json"

SEIZURE_FREQUENCY = "SeizureFrequency"
DIAGNOSIS = "Diagnosis"

# Entities whose gold ``text`` is repaired to its ``CUIPhrase`` at load time.
# The gold JSON was derived from the benchmark MarkupOutput CSVs, which carry two
# phrase columns: col5 (the raw covered span) → ``text`` and col6 (the clean
# canonical term) → ``CUIPhrase``. col5 is offset-drift–corrupted (truncations,
# over-captures, spelling); col6 is the authoritative clean phrase the published
# system was scored against. For these entities col6 is unambiguously the clean
# seizure-/diagnosis-term phrase, so matching on it is both correct and
# benchmark-faithful (see docs/research/exectv2_data_discoveries_log.md D16).
#
# Deliberately NOT every entity: for Investigations col6 encodes the finding
# (``EEG``→``abnormal-eeg``), and for Prescription/WhenDiagnosed it is an ontology
# concept stripped of dose/date — there col6 is a semantic change, not a repair,
# and is held for a per-entity decision (D17).
_CUIPHRASE_REPAIR_ENTITIES = frozenset({SEIZURE_FREQUENCY, DIAGNOSIS})


@dataclass(frozen=True)
class ExectAnnotation:
    """One gold entity mention in an ExECTv2 letter.

    ``text`` is the phrase used for label matching. For entities in
    ``_CUIPHRASE_REPAIR_ENTITIES`` (SeizureFrequency, Diagnosis) it is the clean
    canonical term (``CUIPhrase`` / MarkupOutput col6); for all other entities it
    is the raw annotated span as stored in the gold JSON. ``raw_text`` always
    preserves the original stored span (col5) for provenance — for repaired
    mentions it is the corrupt phrase, for the rest it equals ``text``. Spaces are
    rendered as hyphens in both.

    ``start_index``/``end_index`` are the gold character offsets, retained for
    provenance but DELIBERATELY NOT USED for matching: spelling was corrected in
    the letters after annotation without updating the offsets, so they drift
    against ``note_text`` (see docs/design/reliability_thesis.md). Scoring matches
    on labels, not spans."""

    entity: str
    text: str
    attributes: Mapping[str, str]
    start_index: int | None = None
    end_index: int | None = None
    raw_text: str | None = None


@dataclass(frozen=True)
class ExectLetter:
    letter_id: str
    note_text: str
    annotations: tuple[ExectAnnotation, ...] = field(default_factory=tuple)

    def entities(self, entity: str) -> tuple[ExectAnnotation, ...]:
        return tuple(a for a in self.annotations if a.entity == entity)


def load_annotations(path: Path) -> tuple[ExectAnnotation, ...]:
    """Load the gold entity mentions from one ExECTv2 letter JSON file."""

    rows = json.loads(path.read_text(encoding="utf-8"))
    annotations: list[ExectAnnotation] = []
    for row in rows:
        entity = str(row["entity"])
        raw_text = str(row["text"])
        attributes = {str(k): str(v) for k, v in dict(row["attributes"]).items()}
        cui_phrase = attributes.get("CUIPhrase")
        text = (
            cui_phrase
            if entity in _CUIPHRASE_REPAIR_ENTITIES and cui_phrase
            else raw_text
        )
        annotations.append(
            ExectAnnotation(
                entity=entity,
                text=text,
                attributes=attributes,
                start_index=_optional_int(row.get("start_index")),
                end_index=_optional_int(row.get("end_index")),
                raw_text=raw_text,
            )
        )
    return tuple(annotations)


def load_letters(
    json_dir: Path = DEFAULT_JSON_DIR,
    text_dir: Path = DEFAULT_TEXT_DIR,
) -> list[ExectLetter]:
    """Load all ExECTv2 letters with their gold annotations, ordered by id."""

    letters: list[ExectLetter] = []
    for json_path in sorted(json_dir.glob("*.json")):
        letter_id = json_path.stem
        text_path = text_dir / f"{letter_id}.txt"
        note_text = (
            clean_semantically_neutral_text_artifacts(text_path.read_text(encoding="utf-8"))
            if text_path.exists()
            else ""
        )
        letters.append(
            ExectLetter(
                letter_id=letter_id,
                note_text=note_text,
                annotations=load_annotations(json_path),
            )
        )
    return letters


def load_letters_for_split(
    split: str,
    manifest_path: Path = DEFAULT_SPLIT_MANIFEST,
    json_dir: Path = DEFAULT_JSON_DIR,
    text_dir: Path = DEFAULT_TEXT_DIR,
) -> list[ExectLetter]:
    """Load only the letters belonging to ``split`` ("dev" or "test").

    Per docs/plans/exectv2/05_experiment_harness_and_loops.md and
    06_evaluation_and_benchmark_protocol.md: develop only on "dev"; "test" is
    a locked holdout for a single confirmatory read once dev is locked. The
    full 200-letter corpus (``load_letters``) is reserved for the Phase 7
    frozen, benchmark-comparable audit.
    """

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    try:
        letter_ids = set(manifest["splits"][split]["letter_ids"])
    except KeyError as exc:
        raise ValueError(f"Unknown split {split!r} in {manifest_path}") from exc

    return [
        letter
        for letter in load_letters(json_dir=json_dir, text_dir=text_dir)
        if letter.letter_id in letter_ids
    ]


def _optional_int(value: object) -> int | None:
    if value is None or value == "":
        return None
    return int(value)
