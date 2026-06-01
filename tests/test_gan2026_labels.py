from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import convert_to_categories
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist


def test_purist_category_boundaries() -> None:
    assert map_purist(0) == "currently_no_seizure"
    assert map_purist(1000) == "seizure_freq_unknown"
    assert map_purist(0.16) == "seizure_freq_1_per_yr"
    assert map_purist(1.0) == "seizure_freq_1_per_mon"
    assert map_purist(4.0) == "seizure_freq_1_per_week"
    assert map_purist(30.0) == "seizure_freq_1ormore_daily"


def test_pragmatic_category_boundaries() -> None:
    assert map_pragmatic(0) == "currently_no_seizure"
    assert map_pragmatic(1000) == "seizure_freq_unknown"
    assert map_pragmatic(1.0) == "seizure_infrequent"
    assert map_pragmatic(2.0) == "seizure_frequent"


def test_convert_to_categories() -> None:
    assert convert_to_categories([0, 1.0, 4.0], method="purist") == [
        "currently_no_seizure",
        "seizure_freq_1_per_mon",
        "seizure_freq_1_per_week",
    ]
