"""Re-export shim: all normalization logic lives in tasks/shared/epilepsy/normalization.py.

Every existing import of this module continues to work unchanged.
"""

from clinical_extraction.tasks.shared.epilepsy.normalization import (  # noqa: F401
    DAY_IN_YEAR,
    DAYS_PER,
    FrequencyLabelKind,
    FrequencyLabelRecord,
    _normalize_period,
    _parse_range,
    label_to_frequency_record,
    label_to_monthly_frequency,
    normalize_frequency_label,
    parse_label_bounds,
)
