from __future__ import annotations

from enum import StrEnum


class SeizureFrequencyCategory(StrEnum):
    CURRENTLY_NO_SEIZURE = "currently_no_seizure"
    SEIZURE_FREQ_UNKNOWN = "seizure_freq_unknown"
    SEIZURE_FREQ_1_PER_YR = "seizure_freq_1_per_yr"
    SEIZURE_FREQ_1_PER_6MON = "seizure_freq_1_per_6mon"
    SEIZURE_FREQ_MORE1PER6MON_LESS1MON = "seizure_freq_more1per6mon_less1mon"
    SEIZURE_FREQ_1_PER_MON = "seizure_freq_1_per_mon"
    SEIZURE_FREQ_MORE1MON_LESS1WEEK = "seizure_freq_more1mon_less1week"
    SEIZURE_FREQ_1_PER_WEEK = "seizure_freq_1_per_week"
    SEIZURE_FREQ_MORE1WEEK_LESS1DAY = "seizure_freq_more1week_less1day"
    SEIZURE_FREQ_1ORMORE_DAILY = "seizure_freq_1ormore_daily"
    SEIZURE_INFREQUENT = "seizure_infrequent"
    SEIZURE_FREQUENT = "seizure_frequent"


def map_purist(per_month: float) -> str:
    if per_month == 0:
        return SeizureFrequencyCategory.CURRENTLY_NO_SEIZURE
    if per_month == 1000:
        return SeizureFrequencyCategory.SEIZURE_FREQ_UNKNOWN
    if 0 < per_month <= 0.16:
        return SeizureFrequencyCategory.SEIZURE_FREQ_1_PER_YR
    if 0.16 < per_month <= 0.18:
        return SeizureFrequencyCategory.SEIZURE_FREQ_1_PER_6MON
    if 0.18 < per_month <= 0.99:
        return SeizureFrequencyCategory.SEIZURE_FREQ_MORE1PER6MON_LESS1MON
    if 0.99 < per_month <= 1.1:
        return SeizureFrequencyCategory.SEIZURE_FREQ_1_PER_MON
    if 1.1 < per_month <= 3.9:
        return SeizureFrequencyCategory.SEIZURE_FREQ_MORE1MON_LESS1WEEK
    if 3.9 < per_month <= 4.1:
        return SeizureFrequencyCategory.SEIZURE_FREQ_1_PER_WEEK
    if 4.1 < per_month <= 29:
        return SeizureFrequencyCategory.SEIZURE_FREQ_MORE1WEEK_LESS1DAY
    if 29 < per_month <= 999:
        return SeizureFrequencyCategory.SEIZURE_FREQ_1ORMORE_DAILY
    return SeizureFrequencyCategory.SEIZURE_FREQ_UNKNOWN


def map_pragmatic(per_month: float) -> str:
    if per_month == 0:
        return SeizureFrequencyCategory.CURRENTLY_NO_SEIZURE
    if per_month == 1000:
        return SeizureFrequencyCategory.SEIZURE_FREQ_UNKNOWN
    if 0 < per_month <= 1.1:
        return SeizureFrequencyCategory.SEIZURE_INFREQUENT
    if 1.1 < per_month <= 999:
        return SeizureFrequencyCategory.SEIZURE_FREQUENT
    return SeizureFrequencyCategory.SEIZURE_FREQ_UNKNOWN

