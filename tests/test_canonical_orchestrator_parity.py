from __future__ import annotations

from pathlib import Path

from scripts import check_canonical_orchestrator_parity as parity


def test_parity_report_compares_preserved_legacy_paths() -> None:
    report = parity.build_parity_report()

    assert report["legacy_parity"] == {
        "exect_structured_prompt_only_rows": True,
        "gan_hybrid_saved_output_rows": True,
        "gan_llm_only_saved_output_rows": True,
    }
    assert report["verification_state"] == "verified"
    assert report["verification_gates"]["retained_historical_reference"]["passed"]
    assert report["verification_gates"]["architecture_drift"]["passed"]
    assert "retained historical reference replay" not in report["unverified_gates"]


def test_artifact_check_ignores_only_the_self_referential_source_commit() -> None:
    expected = {
        "source_commit": "generation-base",
        "implementation_hashes": {"source.py": "abc"},
    }
    actual = {
        "source_commit": "commit-containing-artifact",
        "implementation_hashes": {"source.py": "abc"},
    }

    assert parity.reports_match(expected, actual)

    actual["implementation_hashes"]["source.py"] = "changed"
    assert not parity.reports_match(expected, actual)


def test_compatibility_row_projection_ignores_only_canonical_family_identity() -> None:
    legacy = {
        "label": "1 per month",
        "row_trace": {"method": "legacy_hybrid", "after_label": "1 per month"},
    }
    canonical = {
        **legacy,
        "pipeline_family": "llm_with_rules",
    }

    assert parity._compatibility_rows_match([legacy], [canonical])

    changed = {
        **canonical,
        "row_trace": {"method": "legacy_hybrid", "after_label": "2 per month"},
    }
    assert not parity._compatibility_rows_match([legacy], [changed])


def test_text_hash_is_stable_across_windows_line_endings(tmp_path: Path) -> None:
    lf = tmp_path / "lf.py"
    crlf = tmp_path / "crlf.py"
    lf.write_bytes(b"first\nsecond\n")
    crlf.write_bytes(b"first\r\nsecond\r\n")

    assert parity._hash_file(lf) == parity._hash_file(crlf)
