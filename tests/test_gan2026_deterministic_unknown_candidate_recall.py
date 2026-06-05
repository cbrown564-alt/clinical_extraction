from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic import (
    deterministic_extraction,
)


def test_deterministic_extraction_adds_unknown_candidate_for_vague_month_count() -> None:
    candidates = deterministic_extraction._extract_candidates(  # noqa: SLF001
        "Since then he tells me there were a few events in the preceding month."
    )

    assert any(
        candidate.kind.value == "unknown_frequency"
        and candidate.evidence == "a few events in the preceding month"
        for candidate in candidates
    )


def test_deterministic_extraction_adds_unknown_candidate_for_most_weekdays() -> None:
    candidates = deterministic_extraction._extract_candidates(  # noqa: SLF001
        "She reports brief absences occurring on most weekdays."
    )

    assert any(
        candidate.kind.value == "unknown_frequency"
        and candidate.evidence == "brief absences occurring on most weekdays"
        for candidate in candidates
    )


def test_deterministic_extraction_adds_unknown_candidate_for_several_last_week() -> None:
    candidates = deterministic_extraction._extract_candidates(  # noqa: SLF001
        "The patient reports several focal seizures last week."
    )

    assert any(
        candidate.kind.value == "unknown_frequency"
        and candidate.evidence == "several focal seizures last week"
        for candidate in candidates
    )
