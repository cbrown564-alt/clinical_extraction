import time

from clinical_extraction.core.evidence import (
    clean_semantically_neutral_text_artifacts,
    locate_evidence,
    repair_evidence_text_if_source_exact,
)


def test_clean_semantically_neutral_text_artifacts_removes_null_bytes() -> None:
    assert clean_semantically_neutral_text_artifacts("abc\x00def") == "abcdef"


def test_repair_evidence_text_if_source_exact_repairs_case_and_whitespace() -> None:
    note_text = "Diagnosis:\tProbable focal epilepsy"
    evidence = "diagnosis: Probable Focal Epilepsy"

    assert repair_evidence_text_if_source_exact(evidence, note_text) == note_text


def test_locate_evidence_uses_repaired_exact_match() -> None:
    note_text = "abc def"
    evidence = "abc\x00 def"

    assert locate_evidence(note_text, evidence) == (0, len(note_text))


def test_repair_evidence_whitespace_handles_long_whitespace_runs_without_backtracking() -> None:
    prefix = "MRI 2006, essentially normal apart from tiny scattered "
    note_text = prefix + ("\xa0" * 80) + " hyperintensities"
    evidence = prefix + (" " * 80) + " hyperintensities"

    started = time.perf_counter()
    assert repair_evidence_text_if_source_exact(evidence, note_text) == note_text
    assert time.perf_counter() - started < 0.5

