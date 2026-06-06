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


def test_locate_evidence_uses_repaired_exact_match() -> None:
    note_text = "abc def"
    evidence = "abc\x00 def"

    assert locate_evidence(note_text, evidence) == (0, len(note_text))


def test_locate_evidence_does_not_match_empty_cleaned_evidence() -> None:
    assert locate_evidence("abc", "\x00") is None
    assert locate_evidence("", "\x00") is None
