"""Report builders for ExECTv2 experiment artifacts."""

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.three_way_comparison import (
    ARCHITECTURE_FAMILY,
    FAMILY_ORDER,
    SF_BENCHMARK_PER_ITEM_F1,
    SF_BENCHMARK_PER_LETTER_F1,
    ComparisonRow,
    build_comparison_rows,
    compute_rules_row,
    render_comparison_markdown,
    write_comparison_report,
)

__all__ = [
    "ARCHITECTURE_FAMILY",
    "FAMILY_ORDER",
    "SF_BENCHMARK_PER_ITEM_F1",
    "SF_BENCHMARK_PER_LETTER_F1",
    "ComparisonRow",
    "build_comparison_rows",
    "compute_rules_row",
    "render_comparison_markdown",
    "write_comparison_report",
]
