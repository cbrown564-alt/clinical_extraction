"""Shared regex constants for the legacy SF convention implementation (Stack B).

.. deprecated::
    Internal constants extracted from ``_legacy_impl`` so each module stays
    under the line-count gate. Behavior-preserving; do not edit logic here.
"""

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.patterns import (
    CONTEXTUAL_RATE_NOISE as _SF_CONTEXTUAL_RATE_NOISE_RE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.patterns import (
    DATED_GTC as _SF_DATED_GTC_RE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.patterns import (
    GTC_FOUR_LAST_THREE_WEEKS as _SF_GTC_FOUR_LAST_THREE_WEEKS_RE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.patterns import (
    GTC_FURTHER_SINCE as _SF_GTC_FURTHER_SINCE_RE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.patterns import (
    GTC_PER_MONTH as _SF_GTC_PER_MONTH_RE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.patterns import (
    GTC_RANGE_PER_WEEK as _SF_GTC_RANGE_PER_WEEK_RE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.patterns import (
    GTCS_ACTIVE_WITHOUT_COUNT as _SF_GTCS_ACTIVE_WITHOUT_COUNT_RE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.patterns import (
    NO_FURTHER_GTC_SINCE as _SF_NO_FURTHER_GTC_SINCE_RE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.patterns import (
    NO_FURTHER_SINCE as _SF_GENERIC_NO_FURTHER_SINCE_RE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.patterns import (
    SEIZURES_EVERY_RANGE_WEEKS as _SF_GENERIC_EVERY_RANGE_RE,
)

_REWRITE_THESE_SEIZURES_RE = re.compile(r"10-15 of these seizures over 2 days", re.IGNORECASE)
_REWRITE_UP_TO_RANGE_RE = re.compile(r"up to 2 or 3 times per month", re.IGNORECASE)
_SF_VAGUE_EPISODE_RE = re.compile(
    r"\b(?:episodes?(?:\s+around\s+twice\s+a\s+week)?|episodes?\s+of\s+loss\s+of\s+"
    r"consciousness)\b",
    re.IGNORECASE,
)
_SF_RISK_COUNSELLING_RE = re.compile(
    r"\b(?:at\s+risk\s+of\s+further\s+seizures|risk\s+of\s+further\s+seizures|"
    r"only\s+had\s+one\s+seizure)\b",
    re.IGNORECASE,
)
_SF_CONTEXTUAL_SEIZURE_FREE_RE = re.compile(
    r"\bremains\s+seizure\s+free\s+and\s+is\s+now\s+driving\b",
    re.IGNORECASE,
)
_SF_HISTORICAL_COMPARATOR_RE = re.compile(
    r"\blast\s+(?:had\s+a\s+)?seizure\s+before\s+this\b",
    re.IGNORECASE,
)
_SF_GENERIC_PER_MONTH_RANGE_RE = re.compile(
    r"\b(?:currently\s+)?(?:she|he|they)?\s*(?:gets?|has|have)?\s*"
    r"(?:around|about|approximately)?\s*(?P<low>\d+)\s*[-–]\s*(?P<high>\d+)\s+"
    r"seizures?\s+per\s+month\b",
    re.IGNORECASE,
)
_SF_GENERIC_OVER_MONTHS_RE = re.compile(
    r"\b(?P<count>\d+)\s+seizures?\s+(?:over|in)\s+(?P<months>\d+)\s+months?\b",
    re.IGNORECASE,
)
_SF_GENERIC_SINGLE_LAST_WEEK_RE = re.compile(
    r"\b(?:has|had)\s+(?:had\s+)?a\s+(?:generalised\s+tonic\s+clonic\s+)?"
    r"seizure\s+last\s+week\b",
    re.IGNORECASE,
)
_SF_GENERIC_TOTAL_YEAR_RE = re.compile(
    r"\btotal\s+of\s+(?P<count>\d+)\s+(?:seizures?\s+)?in\s+(?P<year>\d{4})\b",
    re.IGNORECASE,
)
_SF_BROAD_SEIZURE_FREE_RE = re.compile(
    r"\b(?:has|have|had)\s+been\s+seizure[-\s]+free\s+since\b|"
    r"\bseizure[-\s]+free\s+for\s+more\s+than\s+\w+\s+years?\b|"
    r"\byear\s+free\s+of\s+seizures\b",
    re.IGNORECASE,
)
_SF_LAST_SEIZURE_MONTHS_RE = re.compile(
    r"\blast\s+seizure\s+(?:now\s+)?was\s+(?P<months>\d+)\s+months?\s+ago\b",
    re.IGNORECASE,
)
_SF_GTC_SINCE_PREVIOUS_RE = re.compile(
    r"\bgeneralised\s+tonic\s+clonic\s+seizures?,\s*"
    r"(?P<count>\d+)\s+since\s+previous\s+appointment\b",
    re.IGNORECASE,
)
_SF_ABSENCE_LIKE_YEAR_RE = re.compile(
    r"\babsence like seizures\s+(?P<year>\d{4})\b",
    re.IGNORECASE,
)
_SF_FSAW_FORTNIGHT_RE = re.compile(
    r"\bfocal seizures with altered awareness approximately 1 per fortnight\b",
    re.IGNORECASE,
)
_SF_FSAW_EVERY_WEEKS_RE = re.compile(
    r"\bfocal seizures with altered awareness every (?P<weeks>\d+) weeks?\b",
    re.IGNORECASE,
)
_SF_FSAW_SEVERAL_MONTH_RE = re.compile(
    r"\bfocal seizures with altered awareness,\s*several per month\b",
    re.IGNORECASE,
)
_SF_SECONDARY_PER_PERIOD_RE = re.compile(
    r"\bsecondary generalised seizures?,?\s*(?P<count>\d+)(?:\s*[-–]\s*(?P<high>\d+))?"
    r"\s+per\s+(?P<period>month|year)\b",
    re.IGNORECASE,
)
_SF_SECONDARY_AROUND_PER_YEAR_RE = re.compile(
    r"\baround\s+(?P<count>\d+)\s+secondary\s+generalised\s+seizures?\s+per\s+year\b",
    re.IGNORECASE,
)
_SF_MYCLONIC_UNKNOWN_RE = re.compile(
    r"\b(?:myoclonic jerks weekly|very frequent myoclonic jerks)\b",
    re.IGNORECASE,
)
_SF_ABSENCE_UNKNOWN_RE = re.compile(
    r"\b(?:occasional absences|typical absences|absences continue)\b",
    re.IGNORECASE,
)
_SF_SEIZURES_RETURNED_RE = re.compile(
    r"\bseizures have returned\b",
    re.IGNORECASE,
)
_SF_CLUSTER_AUGUST_RE = re.compile(
    r"\bcluster of seizures in August,\s*(?P<year>\d{4})\b",
    re.IGNORECASE,
)
_SF_FTB_LAST_EVENT_RE = re.compile(
    r"\bFocal to bilateral convulsive seizures, last event around Christmas (?P<year>\d{4})",
    re.IGNORECASE,
)
_SF_FTB_GENERIC_LAST_EVENT_RE = re.compile(
    r"\bfocal to bilateral convulsive seizures?,?\s+last event\s+"
    r"(?P<when>(?:\d+\s+years?\s+ago)|(?:\d{4})|(?:Christmas day \d{4}))\b",
    re.IGNORECASE,
)
_SF_FTB_EVENTS_IN_TOTAL_LAST_EVENT_RE = re.compile(
    r"\bfocal to bilateral seizures\s+\d+\s+events?\s+in\s+total,\s+last event\s+"
    r"\d+\s+years?\s+ago\b",
    re.IGNORECASE,
)
_SF_SINGLE_CONVULSIVE_LAST_EVENT_RE = re.compile(
    r"\bconvulsive seizure in (?P<year>\d{4})\b",
    re.IGNORECASE,
)
_SF_UP_TO_SEIZURE_FREE_RE = re.compile(
    r"\bhad\s+up\s+to\s+\w+\s+weeks?\s+seizure\s+free\b",
    re.IGNORECASE,
)
_SF_RECENT_LAST_SEIZURE_RE = re.compile(
    r"\b(?:his|her)\s+seizure\s+was\s+about\s+\d+\s+months?\s+ago\b|"
    r"\bsingle\s+seizure\s+some\s+\d+\s+weeks?\s+ago\b",
    re.IGNORECASE,
)
_SF_REMAINS_SEIZURE_FREE_RE = re.compile(
    r"\bremains\s+seiz(?:ure|ures|rue)\s+free\b",
    re.IGNORECASE,
)
_SF_SEIZURES_HAVE_STOPPED_RE = re.compile(
    r"\bseizures\s+have\s+stopped\s+since\b",
    re.IGNORECASE,
)
_SF_NO_EVENTS_SINCE_SURGERY_RE = re.compile(
    r"\bno\s+events\s+since\s+surgery\b|\bno\s+further\s+seizures\s+since\s+her\s+surgery\b",
    re.IGNORECASE,
)
_SF_LAST_SEIZURES_TEENAGE_RE = re.compile(
    r"\blast seizures were in (?:his|her) teenage years\b",
    re.IGNORECASE,
)
_SF_CURRENT_SEIZURES_TIMES_MONTH_RE = re.compile(
    r"\b(?:currently\s+)?(?:his|her|the)?\s*seizures\s+"
    r"(?:occur|is|are)\s+(?P<low>\d+|once|one)\s+(?:or|to)\s+"
    r"(?P<high>\d+|twice|two)\s+times?\s+per\s+month\b",
    re.IGNORECASE,
)
_SF_ONE_SEIZURE_PER_YEAR_RE = re.compile(
    r"\bone seizure a year\b",
    re.IGNORECASE,
)
_SF_ONE_SEIZURE_PER_WEEK_TO_MONTH_RE = re.compile(
    r"\b1 seizure per week to 1 seizure every month\b",
    re.IGNORECASE,
)
_SF_AROUND_N_SEIZURES_PER_MONTH_RE = re.compile(
    r"\baround\s+(?P<count>\d+)\s+seizures?\s+per\s+month\b",
    re.IGNORECASE,
)
_SF_HAD_N_SEIZURES_RE = re.compile(
    r"\b(?:has\s+had|had)\s+(?P<count>\d+)\s+seizures?\b",
    re.IGNORECASE,
)
_SF_FREQUENT_SEIZURES_UNKNOWN_RE = re.compile(
    r"\b(?:fairly\s+frequent|frequent|infrequent)\s+seizures\b|"
    r"\bseizures\s+began\s+last\s+year\b|"
    r"\bseizures\s+have(?:n't| not)\s+been\s+witnessed\b",
    re.IGNORECASE,
)
_SF_GTC_ONE_TO_TWO_MONTH_RE = re.compile(
    r"\bgeneralised\s+tonic\s+clonic\s+seizures?\s+"
    r"(?P<low>\d+|one)\s+to\s+(?P<high>\d+|two)\s+every\s+month\b",
    re.IGNORECASE,
)
_SF_FSAW_ONE_PER_WEEK_RE = re.compile(
    r"\bfocal seizures with altered awareness[\s\S]{0,120}\b1 per week\b",
    re.IGNORECASE,
)
_SF_FSAW_PROBABLY_SEVERAL_WEEK_RE = re.compile(
    r"\bfocal seizures with altered awareness probably several times per week\b",
    re.IGNORECASE,
)
_SF_FOCAL_MOTOR_ACTIVE_RE = re.compile(
    r"\b(?:one focal motor seizure|focal motor seizures?[^.\n]{0,60}every 2 weeks)\b",
    re.IGNORECASE,
)
_SF_FOCAL_MOTOR_FREE_RE = re.compile(
    r"\bfocal motor seizures?[\s\S]{0,280}has not had a seizure like this\b",
    re.IGNORECASE,
)
_SF_ABSENCES_ACTIVE_RE = re.compile(
    r"\babsences?[^.\n]{0,80}(?:several times a day|2-3 per day)\b",
    re.IGNORECASE,
)
_SF_GENERIC_BETWEEN_PER_WEEK_RE = re.compile(
    r"\bnow\s+(?:she|he|they)\s+is\s+having\s+between\s+"
    r"(?P<low>\d+)\s+and\s+(?P<high>\d+)\s+per\s+week\b",
    re.IGNORECASE,
)
_SF_GENERIC_SEVERAL_PER_WEEK_RE = re.compile(
    r"\bsince\s+\w+\s+(?:she|he|they)\s+has\s+been\s+having\s+several\s+per\s+week\b",
    re.IGNORECASE,
)
_SF_GENERIC_EVERY_WEEKS_RE = re.compile(
    r"\bseizure\s+frequency\s+is\s+roughly\s+every\s+(?P<weeks>\d+)\s+weeks\b",
    re.IGNORECASE,
)
_SF_GENERIC_LAST_MONTH_RE = re.compile(
    r"\bhad\s+a\s+seizure\s+last\s+month\b",
    re.IGNORECASE,
)
_SF_GTC_LAST_WEEK_RE = re.compile(
    r"\bhad a generalised tonic clonic seizure\b[^.\n]{0,80}\blast week\b|"
    r"\blast week\b[^.\n]{0,80}\bhad a generalised tonic clonic seizure\b",
    re.IGNORECASE,
)
_SF_GTC_DAY_BURST_RE = re.compile(
    r"\bOn\s+Sunday\s+and\s+Monday,\s+he\s+was\s+having\s+generalised\s+tonic\s+"
    r"clonic\s+seizures\s+in\s+the\s+night\b",
    re.IGNORECASE,
)
_SF_FTB_DATED_EVENTS_RE = re.compile(
    r"\bfocal to bilateral convulsive seizures August (?P<year1>\d{4}) "
    r"and September (?P<year2>\d{4})\b",
    re.IGNORECASE,
)
_SF_SECONDARY_LAST_CHRISTMAS_RE = re.compile(
    r"\bsecondary generalised seizures[\s\S]{0,120}last one was on Christmas day (?P<year>\d{4})\b",
    re.IGNORECASE,
)
_SF_MYCLONIC_DAILY_RE = re.compile(r"\bmyoclonic jerks daily\b", re.IGNORECASE)
_SF_MYCLONIC_ONE_WEEK_RE = re.compile(
    r"\bmyoclonic\s+jerks[\s\S]{0,160}\babout\s+one\s+a\s+week\b",
    re.IGNORECASE,
)
_SF_ABSENCES_FREQUENT_RE = re.compile(
    r"\babsences continue fairly frequent\b|"
    r"\bfrequent\s+drops\s+and\s+absences\s+throughout\s+the\s+day\b",
    re.IGNORECASE,
)
_SF_WEEKLY_SEIZURES_RE = re.compile(
    r"\bcurrently having seizures on a weekly basis\b",
    re.IGNORECASE,
)
_SF_SEIZURE_INCREASE_RE = re.compile(
    r"\bincrease\s+in\s+(?:her|his|their)\s+seizures\b|"
    r"\bincrease\s+in\s+seizures\s+frequency\b",
    re.IGNORECASE,
)
_SF_SEIZURE_FREQUENCY_REDUCED_RE = re.compile(
    r"\bseizure\s+frequency\s+has\s+reduced\b",
    re.IGNORECASE,
)
_SF_NOT_HAD_ANY_MORE_RE = re.compile(
    r"\bhas not had any more seizures\b|"
    r"\bhe has not had any more seizures\b",
    re.IGNORECASE,
)
_SF_SINGLE_SEIZURE_WEEKS_AGO_RE = re.compile(
    r"\bsingle seizure some (?P<weeks>\d+) weeks? ago\b",
    re.IGNORECASE,
)
_SF_TYPICAL_ABSENCES_SINCE_RE = re.compile(
    r"\bmore of his typical absences since the last clinic appointment\b",
    re.IGNORECASE,
)
_SF_COMPLEX_PARTIAL_PER_MONTH_RE = re.compile(
    r"\bComplex partial seizures[^.\n]{0,80}1-2 per month\b",
    re.IGNORECASE,
)
_SF_SECONDARY_ONCE_MONTH_RE = re.compile(
    r"\bAbout\s+once\s+a\s+month\s+(?:she|he)\s+will\s+have\s+a\s+"
    r"secondary\s+generalised\s+seizure\b",
    re.IGNORECASE,
)
_SF_FTB_LAST_ONE_CHRISTMAS_RE = re.compile(
    r"\bfocal\s+to\s+bilateral\s+convulsive\s+seizures[\s\S]{0,120}"
    r"last\s+one\s+was\s+on\s+Christmas\s+day\s+(?P<year>\d{4})\b",
    re.IGNORECASE,
)
_SF_SEIZURE_EVERY_YEAR_RANGE_RE = re.compile(
    r"\b1\s+seizure\s+every\s+(?P<low>\d+|one|two|three)\s+to\s+"
    r"(?P<high>\d+|one|two|three)\s+years?\b",
    re.IGNORECASE,
)


_SF_SMALL_NUMBERS = {
    "once": "1",
    "one": "1",
    "twice": "2",
    "two": "2",
    "three": "3",
    "four": "4",
}


__all__ = [
    "_SF_CONTEXTUAL_RATE_NOISE_RE",
    "_SF_DATED_GTC_RE",
    "_SF_GTC_FOUR_LAST_THREE_WEEKS_RE",
    "_SF_GTC_FURTHER_SINCE_RE",
    "_SF_GTC_PER_MONTH_RE",
    "_SF_GTC_RANGE_PER_WEEK_RE",
    "_SF_GTCS_ACTIVE_WITHOUT_COUNT_RE",
    "_SF_NO_FURTHER_GTC_SINCE_RE",
    "_SF_GENERIC_NO_FURTHER_SINCE_RE",
    "_SF_GENERIC_EVERY_RANGE_RE",
    "_REWRITE_THESE_SEIZURES_RE",
    "_REWRITE_UP_TO_RANGE_RE",
    "_SF_VAGUE_EPISODE_RE",
    "_SF_RISK_COUNSELLING_RE",
    "_SF_CONTEXTUAL_SEIZURE_FREE_RE",
    "_SF_HISTORICAL_COMPARATOR_RE",
    "_SF_GENERIC_PER_MONTH_RANGE_RE",
    "_SF_GENERIC_OVER_MONTHS_RE",
    "_SF_GENERIC_SINGLE_LAST_WEEK_RE",
    "_SF_GENERIC_TOTAL_YEAR_RE",
    "_SF_BROAD_SEIZURE_FREE_RE",
    "_SF_LAST_SEIZURE_MONTHS_RE",
    "_SF_GTC_SINCE_PREVIOUS_RE",
    "_SF_ABSENCE_LIKE_YEAR_RE",
    "_SF_FSAW_FORTNIGHT_RE",
    "_SF_FSAW_EVERY_WEEKS_RE",
    "_SF_FSAW_SEVERAL_MONTH_RE",
    "_SF_SECONDARY_PER_PERIOD_RE",
    "_SF_SECONDARY_AROUND_PER_YEAR_RE",
    "_SF_MYCLONIC_UNKNOWN_RE",
    "_SF_ABSENCE_UNKNOWN_RE",
    "_SF_SEIZURES_RETURNED_RE",
    "_SF_CLUSTER_AUGUST_RE",
    "_SF_FTB_LAST_EVENT_RE",
    "_SF_FTB_GENERIC_LAST_EVENT_RE",
    "_SF_FTB_EVENTS_IN_TOTAL_LAST_EVENT_RE",
    "_SF_SINGLE_CONVULSIVE_LAST_EVENT_RE",
    "_SF_UP_TO_SEIZURE_FREE_RE",
    "_SF_RECENT_LAST_SEIZURE_RE",
    "_SF_REMAINS_SEIZURE_FREE_RE",
    "_SF_SEIZURES_HAVE_STOPPED_RE",
    "_SF_NO_EVENTS_SINCE_SURGERY_RE",
    "_SF_LAST_SEIZURES_TEENAGE_RE",
    "_SF_CURRENT_SEIZURES_TIMES_MONTH_RE",
    "_SF_ONE_SEIZURE_PER_YEAR_RE",
    "_SF_ONE_SEIZURE_PER_WEEK_TO_MONTH_RE",
    "_SF_AROUND_N_SEIZURES_PER_MONTH_RE",
    "_SF_HAD_N_SEIZURES_RE",
    "_SF_FREQUENT_SEIZURES_UNKNOWN_RE",
    "_SF_GTC_ONE_TO_TWO_MONTH_RE",
    "_SF_FSAW_ONE_PER_WEEK_RE",
    "_SF_FSAW_PROBABLY_SEVERAL_WEEK_RE",
    "_SF_FOCAL_MOTOR_ACTIVE_RE",
    "_SF_FOCAL_MOTOR_FREE_RE",
    "_SF_ABSENCES_ACTIVE_RE",
    "_SF_GENERIC_BETWEEN_PER_WEEK_RE",
    "_SF_GENERIC_SEVERAL_PER_WEEK_RE",
    "_SF_GENERIC_EVERY_WEEKS_RE",
    "_SF_GENERIC_LAST_MONTH_RE",
    "_SF_GTC_LAST_WEEK_RE",
    "_SF_GTC_DAY_BURST_RE",
    "_SF_FTB_DATED_EVENTS_RE",
    "_SF_SECONDARY_LAST_CHRISTMAS_RE",
    "_SF_MYCLONIC_DAILY_RE",
    "_SF_MYCLONIC_ONE_WEEK_RE",
    "_SF_ABSENCES_FREQUENT_RE",
    "_SF_WEEKLY_SEIZURES_RE",
    "_SF_SEIZURE_INCREASE_RE",
    "_SF_SEIZURE_FREQUENCY_REDUCED_RE",
    "_SF_NOT_HAD_ANY_MORE_RE",
    "_SF_SINGLE_SEIZURE_WEEKS_AGO_RE",
    "_SF_TYPICAL_ABSENCES_SINCE_RE",
    "_SF_COMPLEX_PARTIAL_PER_MONTH_RE",
    "_SF_SECONDARY_ONCE_MONTH_RE",
    "_SF_FTB_LAST_ONE_CHRISTMAS_RE",
    "_SF_SEIZURE_EVERY_YEAR_RANGE_RE",
    "_SF_SMALL_NUMBERS",
]
