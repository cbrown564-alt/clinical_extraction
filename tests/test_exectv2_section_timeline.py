"""Unit tests for the deterministic section/timeline module (Phase C, see
docs/plans/supervisor_brief_gap_closure_plan_2026-07-01.md). Letter excerpts
below are drawn from real ExECTv2 corpus letters
(data/ExECTv2 (2025)/Gold1-200_corrected_spelling/EA0001.txt, EA0030.txt,
EA0075.txt) with content preserved verbatim for the fields under test.
"""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.section_timeline import (
    build_timeline,
    render_context_block,
    segment_letter,
)

EA0001 = """Dear Dr,

Diagnosis: symptomatic, structural right temporal lobe epilepsy
Subarachnoid haemorrhage (right MCA) 2017

Current antiepileptic medication: lamotrigine 75 mg twice a day (to increase as stated below)
seizure type and frequency: focal seizures with loss of awareness(Unusual smell) approximately 2 to 3 per month.

Investigations: CT head 2017 collier in situ plus low density right temporal lobe

I reviewed this 57 year old man in clinic today. He injured his right elbow in a seizure last year.
"""

EA0030 = """Diagnosis: probable JME

Investigations: EEG 1992: frequent bursts of spike and wave and polyspike
      \t\tMRI 1993: mild cerebellar atrophy

Medication: lamotrigine 250 milligrams twice a day
Keppra 1000 milligrams twice a day

Further to my previous letter I can report that she is doing very well on the above dose of medication.
"""

EA0075 = """The epilepsy service
Our Ref:\tX20150
NHS No:\t496 111 3459
Date: \t\t29/4/2020
Clinic Date \t25/4/2020

Dear Dr

Miss Lewis was reviewed in the Neurology clinic today via telephone consultation.
She was diagnosed with Epilepsy at the age of 18 whilst living in London. Her MRI brain and EEG
were normal at the time of diagnosis.
Plan
1. Continue Sodium Valproate 400mg twice daily
"""

NO_HEADINGS = """Dear colleague, thank you for referring this patient. She was seen in clinic
today and reports no further events since last clinic. We will review again in due course.
"""


def test_segment_letter_recognizes_headings() -> None:
    sections = segment_letter(EA0001)
    labels = [s.label for s in sections]
    assert "Diagnosis" in labels
    assert "Medication" in labels
    assert "SeizureFrequency" in labels
    assert "Investigations" in labels
    diagnosis = next(s for s in sections if s.label == "Diagnosis")
    assert "symptomatic, structural right temporal lobe epilepsy" in diagnosis.text


def test_segment_letter_handles_indented_continuation() -> None:
    sections = segment_letter(EA0030)
    investigations = next(s for s in sections if s.label == "Investigations")
    assert "EEG 1992" in investigations.text
    assert "MRI 1993" in investigations.text


def test_segment_letter_falls_back_to_narrative_when_no_headings() -> None:
    sections = segment_letter(NO_HEADINGS)
    assert all(s.label == "Narrative" for s in sections)
    assert sections
    assert "no further events since last clinic" in sections[0].text


def test_segment_letter_recognizes_bare_plan_heading() -> None:
    sections = segment_letter(EA0075)
    labels = [s.label for s in sections]
    assert "Plan" in labels
    plan = next(s for s in sections if s.label == "Plan")
    assert "Continue Sodium Valproate" in plan.text


def test_build_timeline_extracts_and_sorts_labelled_years() -> None:
    events = build_timeline(EA0030)
    years = [e.year for e in events if e.year is not None]
    assert years == sorted(years)
    assert 1992 in years
    assert 1993 in years


def test_build_timeline_extracts_month_and_dmy_dates() -> None:
    events = build_timeline(EA0075)
    dated = [e for e in events if e.year is not None]
    assert any(e.year == 2020 and e.month == 4 for e in dated)


def test_build_timeline_extracts_relative_anchors() -> None:
    events = build_timeline(EA0075)
    anchors = [e.anchor for e in events if e.anchor is not None]
    assert "at age N" in anchors
    assert "at time of diagnosis" in anchors


def test_build_timeline_no_relative_false_positive_without_signal() -> None:
    events = build_timeline(EA0001)
    anchors = [e.anchor for e in events if e.anchor is not None]
    assert "last year" in anchors
    assert "since last clinic" not in anchors


def test_build_timeline_empty_for_letter_with_no_dates_or_anchors() -> None:
    events = build_timeline("The patient is well. No further comments.")
    assert events == []


def test_render_context_block_includes_structure_and_timeline() -> None:
    sections = segment_letter(EA0030)
    timeline = build_timeline(EA0030)
    block = render_context_block(sections, timeline)
    assert "LETTER STRUCTURE" in block
    assert "TIMELINE" in block
    assert "1992" in block


def test_render_context_block_respects_max_chars() -> None:
    sections = segment_letter(EA0001)
    timeline = build_timeline(EA0001)
    block = render_context_block(sections, timeline, max_chars=40)
    assert len(block) <= 40 + len(" (truncated)")


def test_render_context_block_empty_inputs_produce_empty_string() -> None:
    assert render_context_block([], []) == ""
