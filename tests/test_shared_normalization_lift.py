"""Guard: shared normalization is byte-identical to original label_parser exports."""
from clinical_extraction.tasks.seizure_frequency.gan2026.contract import (
    label_parser as shim,
)
from clinical_extraction.tasks.shared.epilepsy import normalization as shared


def test_shim_exports_match_shared_module():
    """Every public name the shim re-exports resolves to the shared implementation."""
    assert shim.FrequencyLabelKind is shared.FrequencyLabelKind
    assert shim.FrequencyLabelRecord is shared.FrequencyLabelRecord
    assert shim.normalize_frequency_label is shared.normalize_frequency_label
    assert shim.label_to_frequency_record is shared.label_to_frequency_record
    assert shim.label_to_monthly_frequency is shared.label_to_monthly_frequency
    assert shim.parse_label_bounds is shared.parse_label_bounds
    assert shim.DAY_IN_YEAR == shared.DAY_IN_YEAR
    assert shim.DAYS_PER == shared.DAYS_PER


def test_shim_frequency_results_identical_to_shared():
    cases = [
        "2 per month",
        "seizure free for multiple year",
        "unknown",
        "no seizure frequency reference",
        "3 cluster per month, 2 per cluster",
        "1 to 3 per week",
    ]
    for label in cases:
        via_shim = shim.label_to_frequency_record(label)
        via_shared = shared.label_to_frequency_record(label)
        assert via_shim == via_shared, f"mismatch for {label!r}"


def test_shim_parse_bounds_identical():
    cases = [
        "seizure free for 3 month",
        "2 per week",
        "4 to 6 per month",
        "10 per year",
    ]
    for label in cases:
        assert shim.parse_label_bounds(label) == shared.parse_label_bounds(label)
