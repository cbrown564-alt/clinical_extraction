from clinical_extraction.core.evidence import (
    EvidenceGrade,
    grade_evidence,
    is_grounded,
    score_evidence_set,
)


def test_grade_evidence_exact() -> None:
    note_text = "On the accommodation logs, the observed frequency is noted as ≤ four per day."
    evidence = "observed frequency is noted as ≤ four per day"
    assert grade_evidence(note_text, evidence) == EvidenceGrade.EXACT
    assert is_grounded(EvidenceGrade.EXACT)


def test_grade_evidence_repaired_artifact_mojibake_leq() -> None:
    note_text = "overall a frequency of ≤ four seizures per week"
    evidence = "overall a frequency of \x026 four seizures per week"
    assert grade_evidence(note_text, evidence) == EvidenceGrade.REPAIRED_ARTIFACT
    assert is_grounded(EvidenceGrade.REPAIRED_ARTIFACT)


def test_grade_evidence_repaired_case() -> None:
    note_text = "No tongue biting or urinary incontinence reported in recent episodes"
    evidence = "no tongue biting or urinary incontinence reported in recent episodes"
    assert grade_evidence(note_text, evidence) == EvidenceGrade.REPAIRED_CASE
    assert is_grounded(EvidenceGrade.REPAIRED_CASE)


def test_grade_evidence_repaired_whitespace() -> None:
    note_text = "Medication:\n•\tLevetiracetam 250mgs once a day"
    evidence = "Medication: • Levetiracetam 250mgs once a day"
    assert grade_evidence(note_text, evidence) == EvidenceGrade.REPAIRED_WHITESPACE
    assert is_grounded(EvidenceGrade.REPAIRED_WHITESPACE)


def test_grade_evidence_repaired_ellipsis() -> None:
    note_text = "five focal onset seizures in last month on current dose"
    evidence = "five focal onset seizures ... in last month"
    assert grade_evidence(note_text, evidence) == EvidenceGrade.REPAIRED_ELLIPSIS
    assert is_grounded(EvidenceGrade.REPAIRED_ELLIPSIS)


def test_grade_evidence_repaired_section() -> None:
    note_text = (
        "Investigations:\tMRI 2016 normal\n"
        "\t\tEEG 2016 normal\n"
        "\t\tEEG 2015 frequent generalised spike and wave\n\n"
        "I reviewed this patient today."
    )
    evidence = "Investigations:\t\tEEG 2015 frequent generalised spike and wave"
    assert grade_evidence(note_text, evidence) == EvidenceGrade.REPAIRED_SECTION
    assert is_grounded(EvidenceGrade.REPAIRED_SECTION)


def test_grade_evidence_absent_hallucination() -> None:
    note_text = "He has been largely stable for the past 18 months on sodium valproate."
    evidence = "six drop attacks in the past two months"
    assert grade_evidence(note_text, evidence) == EvidenceGrade.ABSENT
    assert not is_grounded(EvidenceGrade.ABSENT)


def test_grade_evidence_empty() -> None:
    assert grade_evidence("any note", "") == EvidenceGrade.EMPTY
    assert grade_evidence("any note", "   ") == EvidenceGrade.EMPTY
    assert not is_grounded(EvidenceGrade.EMPTY)


def test_score_evidence_set_grounded_and_exact_rates() -> None:
    note_text = (
        "overall a frequency of ≤ four seizures per week. "
        "he and his partner report that the seizures occur every four months"
    )
    evidence_items = (
        "overall a frequency of \x026 four seizures per week",
        "he and his partner report that the seizures occur every four months",
        "six drop attacks in the past two months",
    )
    scored = score_evidence_set(note_text, evidence_items)
    assert scored.total == 3
    assert scored.grounded == 2
    assert scored.exact == 1
    assert scored.grounded_rate == 0.6667
    assert scored.exact_rate == 0.3333
    assert scored.by_grade[EvidenceGrade.REPAIRED_ARTIFACT] == 1
    assert scored.by_grade[EvidenceGrade.EXACT] == 1
    assert scored.by_grade[EvidenceGrade.ABSENT] == 1
