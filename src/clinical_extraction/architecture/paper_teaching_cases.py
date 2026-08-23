"""Paper flagship letters as explainer teaching cases.

Gan codebook extract prefers Grok 4.6 on dev750. Cell 2 pre-post and cell 5
select replay Gemini Flash. ExECT extract and pre-post replay Luna Compact;
later-stage encode/select replay Gemini. No live calls, no locked rows.
"""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.architecture.paper_cell_teaching import (
    EXECT_ENCODE_RAW,
    EXECT_ONLY_RAW,
    EXECT_PRE_POST_RAW,
    EXECT_SELECT_RAW,
    GAN_EXTRACT_RAW,
    GAN_PRE_POST_RAW,
    GAN_SELECT_RAW,
    exect_paper_runs,
    gan_paper_runs,
)
from clinical_extraction.architecture.teaching_case import GanCaseSpec, TeachingCase
from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
)

ROOT = discover_repo_root(start=Path(__file__))

GAN_FIXTURE_NOTE = (
    "Development letter from Gan 2026 dev750. Cell 3 extract is a Grok 4.6 "
    "replay; cell 2 pre-post and cell 5 select replay Gemini Flash. No live "
    "call is made. Cell 4 uses the same codebook extract (encode already wrote "
    "the form)."
)
EXECT_FIXTURE_NOTE = (
    "Development letter from ExECTv2 dev140. Extract and pre-post replay Luna "
    "Compact; later-stage encode and select replay Gemini Flash. No live call "
    "is made."
)


def _raw_output_by_row(path: Path, source_row_index: int) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if int(row["source_row_index"]) == source_row_index:
            raw = row.get("raw_output")
            if not raw:
                raise ValueError(f"{path}: row {source_row_index} has no raw_output")
            return str(raw)
    raise KeyError(f"{path}: missing source_row_index {source_row_index}")


def _raw_output_by_letter(path: Path, letter_id: str) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("letter_id") == letter_id:
            raw = row.get("raw_output")
            if not raw:
                raise ValueError(f"{path}: {letter_id} has no raw_output")
            return str(raw)
    raise KeyError(f"{path}: missing letter_id {letter_id}")



def _row_by_letter(path: Path, letter_id: str) -> dict:
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("letter_id") == letter_id:
            return row
    raise KeyError(f"{path}: missing letter_id {letter_id}")

def _gan_record(source_row_index: int):
    for record in load_records_for_split("validation"):
        if record.source_row_index == source_row_index:
            return record
    raise KeyError(f"dev750 does not contain source_row_index {source_row_index}")


def _exect_letter(letter_id: str):
    for letter in load_letters_for_split("dev"):
        if letter.letter_id == letter_id:
            return letter
    raise KeyError(f"dev140 does not contain letter_id {letter_id}")


def _gan_paper_spec(
    *,
    case_id: str,
    source_row_index: int,
    story: str,
    gold_note: str,
    card_why: dict[str, str],
    mechanism_title: str,
    mechanism: str,
) -> GanCaseSpec:
    record = _gan_record(source_row_index)
    return GanCaseSpec(
        case_id=case_id,
        letter_id=f"GAN-{source_row_index}",
        note_text=record.note_text,
        gold=record.gold_label,
        gold_reference=record.gold_reference,
        gold_note=gold_note,
        story=story,
        card_why=card_why,
        mechanism_title=mechanism_title,
        mechanism=mechanism,
        hybrid_raw_output=_raw_output_by_row(GAN_EXTRACT_RAW, source_row_index),
        llm_only_raw_output=_raw_output_by_row(GAN_EXTRACT_RAW, source_row_index),
        extract_label_forms_raw=_raw_output_by_row(GAN_EXTRACT_RAW, source_row_index),
        pre_post_label_forms_raw=_raw_output_by_row(GAN_PRE_POST_RAW, source_row_index),
        select_from_extract_raw=_raw_output_by_row(GAN_SELECT_RAW, source_row_index),
        source_row_index=source_row_index,
        fixture_note=GAN_FIXTURE_NOTE,
    )


def _exect_paper_case(
    *,
    case_id: str,
    letter_id: str,
    story: str,
    gold_note: str,
    card_why: dict[str, str],
    mechanism_title: str,
    mechanism: str,
) -> TeachingCase:
    letter = _exect_letter(letter_id)
    case = TeachingCase(
        case_id=case_id,
        task="exectv2",
        task_label="ExECTv2",
        letter_id=letter.letter_id,
        note_text=letter.note_text,
        gold=f"{len(letter.annotations)} gold annotations",
        gold_note=gold_note,
        fixture_note=EXECT_FIXTURE_NOTE,
        story=story,
        gold_reference="",
        card_why=card_why,
        mechanism_title=mechanism_title,
        mechanism=mechanism,
    )
    case.runs = exect_paper_runs(
        letter,
        pre_post_raw=_raw_output_by_letter(EXECT_PRE_POST_RAW, letter_id),
        only_raw=_raw_output_by_letter(EXECT_ONLY_RAW, letter_id),
        encode_row=_row_by_letter(EXECT_ENCODE_RAW, letter_id),
        select_row=_row_by_letter(EXECT_SELECT_RAW, letter_id),
    )
    return case


def _gan_paper_case(spec: GanCaseSpec) -> TeachingCase:
    case = TeachingCase(
        case_id=spec.case_id,
        task="gan2026",
        task_label="Gan 2026",
        letter_id=spec.letter_id,
        note_text=spec.note_text,
        gold=spec.gold,
        gold_note=spec.gold_note,
        fixture_note=spec.fixture_note or GAN_FIXTURE_NOTE,
        story=spec.story,
        gold_reference=spec.gold_reference,
        card_why=spec.card_why,
        mechanism_title=spec.mechanism_title,
        mechanism=spec.mechanism,
    )
    case.runs = gan_paper_runs(spec)
    return case


def build_paper_teaching_letters() -> tuple[TeachingCase, ...]:
    """Flagship G1, G3, E1, and E2 as explainer cases."""

    g1 = _gan_paper_spec(
        case_id="gan2026_cluster_vs_quiet_interval",
        source_row_index=15431,
        story=(
            "Quiet interval and cluster grammar compete; codebook extract "
            "does not assemble the two-part gold."
        ),
        gold_note=(
            "Gold is the two-part cluster label "
            "`1 cluster per 4 month, 5 per cluster`."
        ),
        card_why={
            "rules": "Rules match the cluster count to the four-month quiet window.",
            "llm_pre_post": "Both-extract then rules on the label-forms pre-post raw.",
            "llm_extract": "Gemini codebook extract, then rule encode and select.",
            "llm_encode": "Same codebook extract; the extract already wrote the form.",
            "llm_select": "Gemini later-stage select on the extract ledger.",
        },
        mechanism_title="Quiet interval versus cluster grammar",
        mechanism=(
            "The letter states a seizure-free interval of up to four months and "
            "clusters of five seizures in a day. Gold needs both parts. Rules "
            "get the two-part label; model-led cells collapse toward one part."
        ),
    )
    g3 = _gan_paper_spec(
        case_id="gan2026_unknown_vs_qualitative_frequency",
        source_row_index=2166,
        story="Qualitative 'frequent' has no countable rate; gold is unknown.",
        gold_note="Gold is the unknown sentinel: the letter has no countable rate.",
        card_why={
            "rules": "Rules find no countable rate and abstain.",
            "llm_pre_post": "Both-extract then rules still sit in the unknown bucket.",
            "llm_extract": "Codebook extract, then rule encode and select.",
            "llm_encode": "Same extract; encode already wrote the form.",
            "llm_select": "Later-stage select on the extract ledger.",
        },
        mechanism_title="Abstain when the letter has no countable rate",
        mechanism=(
            "The letter says frequent petit mal and increasing absences, with no "
            "number. Gold is unknown. Rules abstain. Model-led cells may render "
            "a qualitative rate that still sits in the unknown bucket."
        ),
    )
    e1 = _exect_paper_case(
        case_id="exectv2_four_family_named_windows",
        letter_id="EA0186",
        story=(
            "All four families are present; seizure-frequency windows must stay "
            "named, not become a monthly rate."
        ),
        gold_note=(
            "Gold covers diagnosis, dated seizure-frequency windows, lamotrigine, "
            "and abnormal MRI/EEG."
        ),
        card_why={
            "rules": "Nine-entity extractors fill the all-nine baseline.",
            "llm_pre_post": "Gemini pre-post, then rule encode and select.",
            "llm_extract": "Gemini extract, then rule encode and select.",
            "llm_encode": "Later-stage Gemini encode, then accepted select rules.",
            "llm_select": "Later-stage Gemini select on the encode ledger.",
        },
        mechanism_title="Four families and named time windows",
        mechanism=(
            "The letter has diagnosis, several dated seizure statements, a "
            "current regimen, and completed tests. The hard part is binding "
            "'last month' and '10 months ago' to counts, not to a recurring rate."
        ),
    )
    e2 = _exect_paper_case(
        case_id="exectv2_epileptic_vs_dissociative",
        letter_id="EA0057",
        story=(
            "Epileptic and dissociative diagnoses share the letter; rates must "
            "stay attached to the right one."
        ),
        gold_note=(
            "Gold separates symptomatic structural epilepsy from dissociative "
            "attacks and keeps each frequency on its own diagnosis."
        ),
        card_why={
            "rules": "Rules extract both diagnoses and their separate rates.",
            "llm_pre_post": "The diagnosis lens rewrites the structural-epilepsy phrase.",
            "llm_extract": "Gemini extract, then rule encode and select.",
            "llm_encode": "Later-stage Gemini encode, then accepted select rules.",
            "llm_select": "Later-stage Gemini select on the encode ledger.",
        },
        mechanism_title="Which rate belongs to which diagnosis",
        mechanism=(
            "The letter states structural epilepsy that is now quiet and "
            "dissociative attacks twice a week. A model that puts the weekly "
            "rate on epilepsy has mixed the two diagnoses."
        ),
    )
    return (_gan_paper_case(g1), _gan_paper_case(g3), e1, e2)
