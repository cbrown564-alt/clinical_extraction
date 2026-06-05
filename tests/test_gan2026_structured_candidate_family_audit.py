from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_candidate_family_audit,
)


def test_family_audit_finds_clean_seed_slices() -> None:
    rows = [
        _row(1, "seizure free for multiple year", "unknown", "W_to_C"),
        _row(2, "seizure free for multiple year", "unknown", "W_to_C"),
        _row(3, "1 per year", "1 per day", "W_to_C"),
        _row(4, "1 per month", "unknown", "C_to_W"),
        _row(5, "1 per month", "unknown", "C_to_C"),
    ]

    summary = structured_candidate_family_audit.summarize_family_audit(rows)

    clean = summary["clean_seed_slices"]
    assert clean[0]["slice_name"] == "current_to_proposed_family"
    assert clean[0]["slice_value"] == "seizure_free->unknown"
    assert clean[0]["w_to_c_rows"] == 2
    assert clean[0]["c_to_w_rows"] == 0
    assert summary["decision"] == "seed_slices_only_undercoverage"


def test_family_audit_rejects_when_no_clean_w_to_c_slice_exists() -> None:
    rows = [
        _row(1, "1 per month", "unknown", "C_to_W"),
        _row(2, "2 per month", "unknown", "C_to_W"),
    ]

    summary = structured_candidate_family_audit.summarize_family_audit(rows)

    assert summary["clean_seed_slices"] == []
    assert summary["decision"] == "no_clean_structured_seed_slice"


def _row(
    source_row_index: int,
    current_label: str,
    proposed_label: str,
    transition: str,
) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "prediction_bearing": True,
        "current_label": current_label,
        "proposed_label": proposed_label,
        "event_kind": "unknown_frequency" if proposed_label == "unknown" else "frequency_rate",
        "panel_role": "hard" if transition.startswith("W_") else "control",
        "transition": transition,
        "parse_ok": True,
        "exact_evidence": True,
        "contract_issues": [],
    }
