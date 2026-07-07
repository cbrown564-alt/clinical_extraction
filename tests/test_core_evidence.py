from clinical_extraction.core.evidence import (
    clean_semantically_neutral_text_artifacts,
    locate_evidence,
    repair_evidence_text_if_source_exact,
)


def test_clean_semantically_neutral_text_artifacts_removes_null_bytes() -> None:
    assert clean_semantically_neutral_text_artifacts("abc\x00def") == "abcdef"


def test_repair_evidence_text_if_source_exact_uses_null_byte_cleanup() -> None:
    note_text = "abc def"
    evidence = "abc\x00 def"

    assert repair_evidence_text_if_source_exact(evidence, note_text) == note_text


def test_repair_evidence_text_if_source_exact_repairs_case_and_whitespace() -> None:
    note_text = "Diagnosis:\tProbable focal epilepsy"
    evidence = "diagnosis: Probable Focal Epilepsy"

    assert repair_evidence_text_if_source_exact(evidence, note_text) == note_text


def test_repair_evidence_text_if_source_exact_repairs_escaped_newline() -> None:
    note_text = "Medication:\n•\tLevetiracetam 250mgs once a day"
    evidence = "Medication:\\n•\\tLevetiracetam 250mgs once a day"

    assert repair_evidence_text_if_source_exact(evidence, note_text) == note_text


def test_repair_evidence_text_if_source_exact_repairs_bounded_ellipsis_span() -> None:
    note_text = (
        "Medication:\tLamotrigine 50mg am, 75mg pm increasing by 25mg "
        "increments every 2 weeks to 75mg am, 100mg pm"
    )
    evidence = "Medication:\t...Lamotrigine 50mg am, 75mg pm increasing by 25mg"

    repaired = repair_evidence_text_if_source_exact(evidence, note_text)

    assert repaired == note_text[: note_text.index(" increments")]


def test_repair_evidence_text_if_source_exact_repairs_section_header_list_item() -> None:
    note_text = (
        "Investigations:\tMRI 2016 normal\n"
        "\t\tEEG 2016 normal\n"
        "\t\tEEG 2015 frequent generalised spike and wave\n\n"
        "I reviewed this patient today."
    )
    evidence = "Investigations:\t\tEEG 2015 frequent generalised spike and wave"

    repaired = repair_evidence_text_if_source_exact(evidence, note_text)

    assert repaired == (
        "Investigations:\tMRI 2016 normal\n"
        "\t\tEEG 2016 normal\n"
        "\t\tEEG 2015 frequent generalised spike and wave"
    )


def test_repair_evidence_text_if_source_exact_repairs_header_with_numbered_item() -> None:
    note_text = (
        "Diagnosis\t1. Dissociative seizures\n"
        "\t\t2. Symptomatic structural epilepsy secondary to previous cerebral abcess\n\n"
        "Medication:\tLevetiracetam 1000mg bd"
    )
    evidence = "Diagnosis\t2. Symptomatic structural epilepsy secondary to previous cerebral abcess"

    repaired = repair_evidence_text_if_source_exact(evidence, note_text)

    assert repaired == (
        "Diagnosis\t1. Dissociative seizures\n"
        "\t\t2. Symptomatic structural epilepsy secondary to previous cerebral abcess"
    )


def test_repair_evidence_text_if_source_exact_does_not_repair_unresolved_ellipsis() -> None:
    note_text = "Medication:\tLamotrigine 50mg am"
    evidence = "Medication:\t...Zonisamide 50mg bd"

    assert repair_evidence_text_if_source_exact(evidence, note_text) == evidence


def test_locate_evidence_uses_repaired_exact_match() -> None:
    note_text = "abc def"
    evidence = "abc\x00 def"

    assert locate_evidence(note_text, evidence) == (0, len(note_text))


def test_locate_evidence_does_not_match_empty_cleaned_evidence() -> None:
    assert locate_evidence("abc", "\x00") is None
    assert locate_evidence("", "\x00") is None
