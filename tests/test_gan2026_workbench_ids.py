from clinical_extraction.trace_explorer.gan2026_comparison import (
    paper_identity_from_run_id,
    paper_run_id,
)


def test_paper_run_id_keeps_legacy_suffixes_and_names_five_cell_rows() -> None:
    assert paper_run_id("gan_llm_extract_raw", "grok46") == (
        "gan2026_validation750_grok46_llm_with_rules"
    )
    assert paper_run_id("gan_llm_only", "grok46") == "gan2026_validation750_grok46_llm_only"
    assert paper_run_id("llm_encode", "gemini37flash") == (
        "gan2026_validation750_gemini37flash_llm_encode"
    )
    assert paper_run_id("llm_extract", "gemini37flash") == (
        "gan2026_validation750_gemini37flash_llm_extract"
    )


def test_paper_identity_reads_five_cell_and_legacy_suffixes() -> None:
    assert paper_identity_from_run_id("gan2026_validation750_gemini37flash_llm_encode") == (
        "gan_llm_encode",
        "gemini37flash",
    )
    assert paper_identity_from_run_id("gan2026_validation750_grok46_llm_with_rules") == (
        "gan_llm_extract_raw",
        "grok46",
    )
    assert paper_identity_from_run_id("rules") is None
