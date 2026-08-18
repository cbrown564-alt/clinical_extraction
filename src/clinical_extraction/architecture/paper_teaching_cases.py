"""Paper flagship letters as explainer teaching cases.

Gan rows replay Grok 4.6 from the local paper stream. ExECT letters replay
Luna Compact from ``paper_experiments`` (Grok Compact is not on disk yet).
All four letters are development-split. No locked rows are read.
"""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.architecture.teaching_case import (
    GanCaseSpec,
    TeachingCase,
    _exect_llm_only_run,
    _exect_llm_with_rules_run,
    _exect_rules_only_run,
    _gan_case,
)
from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
)

ROOT = discover_repo_root(start=Path(__file__))

GAN_LLM_ONLY_ROWS = (
    ROOT / "experiments/paper/gan_llm_only/grok46/dev750/rows.jsonl"
)
GAN_HYBRID_ROWS = (
    ROOT / "experiments/paper/gan_llm_with_rules/grok46/dev750/rows.jsonl"
)
EXECT_COMPACT_ROWS = (
    ROOT
    / "paper_experiments/exect/exect_llm_with_rules/gpt56luna/dev140/structured.jsonl"
)

GAN_FIXTURE_NOTE = (
    "Development letter from Gan 2026 dev750. Model outputs are a Grok 4.6 "
    "replay; no live call is made. Downstream stages are the selected "
    "implementation."
)
EXECT_FIXTURE_NOTE = (
    "Development letter from ExECTv2 dev140. Model outputs are a Luna "
    "Compact replay; Grok Compact is not on disk yet. No live call is made. "
    "Downstream stages are the selected implementation."
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
        hybrid_raw_output=_raw_output_by_row(GAN_HYBRID_ROWS, source_row_index),
        llm_only_raw_output=_raw_output_by_row(GAN_LLM_ONLY_ROWS, source_row_index),
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
    raw_output = _raw_output_by_letter(EXECT_COMPACT_ROWS, letter_id)
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
    case.runs = [
        _exect_rules_only_run(letter),
        _exect_llm_only_run(letter, raw_output),
        _exect_llm_with_rules_run(letter, raw_output),
    ]
    return case


def build_paper_teaching_letters() -> tuple[TeachingCase, ...]:
    """Flagship G1, G3, E1, and E2 as explainer cases."""

    g1 = _gan_paper_spec(
        case_id="gan2026_cluster_vs_quiet_interval",
        source_row_index=15431,
        story=(
            "Quiet interval and cluster grammar compete; this Grok replay "
            "does not assemble the two-part gold."
        ),
        gold_note=(
            "Gold is the two-part cluster label "
            "`1 cluster per 4 month, 5 per cluster`."
        ),
        card_why={
            "rules": "Rules match the cluster count to the four-month quiet window.",
            "llm": (
                "The model kept only `5 per cluster`; selected-evidence repair "
                "emptied that to no seizure frequency reference."
            ),
            "llm_with_rules": (
                "The model wrote a cluster-after-quiet phrase; selected-evidence "
                "repair then kept only the quiet interval."
            ),
        },
        mechanism_title="Quiet interval versus cluster grammar",
        mechanism=(
            "The letter states a seizure-free interval of up to four months and "
            "clusters of five seizures in a day. Gold needs both parts. On this "
            "Grok replay, rules get the two-part label; the model-led methods "
            "collapse to the cluster count or the quiet interval."
        ),
    )
    g3 = _gan_paper_spec(
        case_id="gan2026_unknown_vs_qualitative_frequency",
        source_row_index=2166,
        story=(
            "Qualitative 'frequent' has no countable rate; gold is unknown."
        ),
        gold_note="Gold is the unknown sentinel: the letter has no countable rate.",
        card_why={
            "rules": "Rules find no countable rate and abstain.",
            "llm": "The model abstains with unknown.",
            "llm_with_rules": (
                "Normalize and selected-evidence turn `frequent` into "
                "`multiple per day`; the unknown bucket still matches gold."
            ),
        },
        mechanism_title="Abstain when the letter has no countable rate",
        mechanism=(
            "The letter says frequent petit mal and increasing absences, with no "
            "number. Gold is unknown. Rules and the one-call model abstain. The "
            "hybrid path renders a qualitative daily rate; that still sits in "
            "the unknown bucket on this scorer."
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
            "llm": "One call proposes four-family findings as written.",
            "llm_with_rules": (
                "Lenses run on the four families after flatten and store."
            ),
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
            "llm": "The model may attach the weekly rate to epilepsy.",
            "llm_with_rules": (
                "The diagnosis lens rewrites the structural-epilepsy phrase; "
                "the other three families assemble without a further rewrite."
            ),
        },
        mechanism_title="Which rate belongs to which diagnosis",
        mechanism=(
            "The letter states structural epilepsy that is now quiet and "
            "dissociative attacks twice a week. A model that puts the weekly "
            "rate on epilepsy has mixed the two diagnoses. The diagnosis and "
            "seizure-frequency lenses exist to keep those facts apart."
        ),
    )
    return (_gan_case(g1), _gan_case(g3), e1, e2)
