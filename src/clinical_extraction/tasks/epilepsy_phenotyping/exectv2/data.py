from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from clinical_extraction.core.evidence import clean_semantically_neutral_text_artifacts
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.evaluation import (
    uses_cuiphrase_as_gold_text,
)

DEFAULT_DATA_DIR = Path("data/ExECTv2 (2025)")
DEFAULT_JSON_DIR = DEFAULT_DATA_DIR / "Json"
DEFAULT_TEXT_DIR = DEFAULT_DATA_DIR / "Gold1-200_corrected_spelling"
DEFAULT_SPLITS_DIR = DEFAULT_DATA_DIR / "splits"
DEFAULT_SPLIT_MANIFEST = DEFAULT_SPLITS_DIR / "exectv2_split_v1.json"

SEIZURE_FREQUENCY = "SeizureFrequency"
DIAGNOSIS = "Diagnosis"

# The per-entity phrase target is declared in ``contract.evaluation``. The notes
# below document the source provenance behind that policy.
# The gold JSON was derived from the benchmark MarkupOutput CSVs. Invariant across
# all entities: ``CUIPhrase`` is the clean canonical concept and gold ``text`` is
# the raw offset-covered span (drift-corrupted: truncations, over-captures,
# spelling). The clean CUIPhrase is the authoritative phrase the published system
# was scored against; for these two entities it is unambiguously the clean
# seizure-/diagnosis-term, so matching on it is both correct and benchmark-faithful
# (discoveries log D16).
#
# Which physical CSV column holds each field varies by file — do not generalize a
# column index. Verified against the raw CSVs (``file,start,end,CUI,…``):
#   - SeizureFrequency: col5 = raw span → ``text``, col6 = clean → ``CUIPhrase``.
#   - The other seven (BirthHistory, Diagnosis, EpilepsyCause, Investigations, Onset,
#     PatientHistory, WhenDiagnosed): order flipped — col5 = clean → ``CUIPhrase``,
#     col6 = raw span → ``text``.
#   - Prescription: col5 = ``CUIPhrase``, col6 = ``DrugName``, col10 (full regimen
#     markup span, e.g. ``carbamazepine-``) → ``text``.
# The code reads JSON fields, not columns, so the per-file order does not affect it.
#
# Repair is deliberately NOT every entity: for Investigations CUIPhrase encodes the
# finding (``EEG``→``abnormal-eeg``), and for Prescription/WhenDiagnosed it is an
# ontology concept stripped of dose/date — there CUIPhrase is a semantic change, not
# a repair, and is held for a per-entity decision (D17). Prescription's ``text`` span
# altitude is also inconsistent in the gold itself (~70% of offsets cover the full
# regimen, ~30% just the drug name), so it has no single clean phrase target and is
# scored on its clinical components (see the all-9 layered error analysis, Finding 1).


@dataclass(frozen=True)
class ExectAnnotation:
    """One gold entity mention in an ExECTv2 letter.

    ``text`` is the phrase used for label matching. For entities whose
    ``EntityEvaluationPolicy.phrase_target`` is ``cuiphrase`` it is the clean
    canonical term; for all other entities it is the raw annotated span as stored
    in the gold JSON. ``raw_text`` always preserves the original stored span for
    provenance. Spaces are rendered as hyphens in both.

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
            if uses_cuiphrase_as_gold_text(entity) and cui_phrase
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
