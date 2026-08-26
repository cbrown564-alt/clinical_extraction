from clinical_extraction.paper.exect_panel import (
    paper_exect_catalog_runs,
    paper_exect_identity,
    paper_exect_run_id,
)


def test_paper_exect_run_id_keeps_legacy_suffixes_and_names_five_cell_rows() -> None:
    assert paper_exect_run_id("gpt56luna", "llm_with_rules") == (
        "exectv2_dev140_gpt56luna_llm_plus_rules"
    )
    assert paper_exect_run_id("gemini37flash", "llm_encode") == (
        "exectv2_dev140_gemini37flash_llm_encode"
    )


def test_paper_exect_identity_reads_five_cell_and_legacy_suffixes() -> None:
    assert paper_exect_identity("exectv2_dev140_gemini37flash_llm_encode") == (
        "gemini37flash",
        "llm_encode",
    )
    assert paper_exect_identity("exectv2_dev140_gpt56luna_llm_plus_rules") == (
        "gpt56luna",
        "exect_llm_pre_post",
    )
    assert paper_exect_identity("exectv2_dev140_grok46_llm_only") == (
        "grok46",
        "exect_llm_only",
    )


def test_paper_exect_catalog_includes_gemini_five_cell_and_one_rules_lane() -> None:
    runs = paper_exect_catalog_runs()
    encode = next(
        run for run in runs if run["run_id"] == "exectv2_dev140_gemini37flash_llm_encode"
    )
    assert encode["paper_cell"] == "llm_encode"
    assert encode["model"] == "gemini/gemini-3.7-flash"
    assert encode["artifact_paths"]
    assert not any(
        run.get("paper_cell") == "rules_only" and run["model"] != "(model-independent)"
        for run in runs
    )
    assert not any(
        run.get("kind") == "llm" or run["run_id"].endswith("_llm_only")
        for run in runs
    )


def test_paper_exect_catalog_shows_select_stop_metrics_for_extract_cell() -> None:
    runs = paper_exect_catalog_runs()
    extract = next(
        run
        for run in runs
        if run["run_id"] == "exectv2_dev140_gemini37flash_llm_extract"
    )
    metrics = extract["metrics"]
    assert metrics["overall_f1"] == 0.8877
    assert metrics["families"]["Diagnosis"]["f1"] == 0.8413
    assert metrics["families"]["SeizureFrequency"]["f1"] == 0.8338
    assert metrics["families"]["Prescription"]["f1"] == 0.9604
    assert metrics["families"]["Investigations"]["f1"] == 0.9591

    encode = next(
        run
        for run in runs
        if run["run_id"] == "exectv2_dev140_gemini37flash_llm_encode"
    )
    assert encode["metrics"]["overall_f1"] == 0.8699
    assert encode["metrics"]["families"]["Diagnosis"]["f1"] == 0.8146

    pre_post = next(
        run
        for run in runs
        if run["run_id"] == "exectv2_dev140_gemini37flash_llm_plus_rules"
    )
    assert pre_post["metrics"]["families"]["Diagnosis"]["f1"] == 0.847
