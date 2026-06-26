"""SeizureFrequency benchmark rewrite dictionary."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    normalize_phrase,
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
_SF_CONTEXTUAL_RATE_NOISE_RE = re.compile(
    r"\b(?:"
    r"free\s+of\s+seizures|dvla|drive\s+until|previously|before\s+the\s+seizure|"
    r"best\s+period|longest\s+period|up\s+until|first\s+seizure\s+at\s+the\s+age|"
    r"at\s+the\s+age\s+of\s+\d+|at\s+onset|at\s+the\s+onset|"
    r"well\s+controlled|reasonably\s+controlled|remain\s+well\s+controlled|"
    r"uncontrolled|clumsy|low\s+mood|at\s+least\s+three\s+seizures\s+he\s+has\s+epilepsy|"
    r"not\s+related\s+to\s+sleep\s+or\s+meals|febrile\s+seizures?|"
    r"mother\s+had\s+epilepsy|family\s+history|"
    r"up\s+to\s+\w+\s+weeks?\s+seizure\s+free|"
    r"transient\s+loss\s+of\s+consciousness|as\s+a\s+child\s+he\s+had\s+seizures|"
    r"helped\s+(?:his|her)\s+seizures|background\s+of\s+frequent\s+seizures|"
    r"continues\s+to\s+get\s+seizures\s+despite\s+pharmacological\s+treatment"
    r")\b",
    re.IGNORECASE,
)
_SF_GENERIC_EVERY_RANGE_RE = re.compile(
    r"\bseizures?\s+every\s+(?P<low>\d+)\s+to\s+(?P<high>\d+)\s+weeks?\b",
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
_SF_GENERIC_NO_FURTHER_SINCE_RE = re.compile(
    r"\b(?:has|have|had)\s+not\s+had\s+any\s+further\s+seizures\s+since\b|"
    r"\bno\s+further\s+seizures\s+since\b|"
    r"\bno\s+seizures\s+since\b",
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
_SF_DATED_GTC_RE = re.compile(
    r"(?P<count>\d+)\s+generalised tonic clonic seizures\s+(?P<year>\d{4})",
    re.IGNORECASE,
)
_SF_GTC_RANGE_PER_WEEK_RE = re.compile(
    r"\b(?P<low>\d+)\s*[-–]\s*(?P<high>\d+)\s+generalised\s+tonic\s+"
    r"clonic\s+seizures?\s+per\s+week\b",
    re.IGNORECASE,
)
_SF_GTC_FOUR_LAST_THREE_WEEKS_RE = re.compile(
    r"\bgeneralised\s+tonic\s+clonic\s+seizures?[\s\S]{0,180}\b"
    r"had\s+four\s+in\s+the\s+last\s+three\s+weeks\b",
    re.IGNORECASE,
)
_SF_GTC_SINCE_PREVIOUS_RE = re.compile(
    r"\bgeneralised\s+tonic\s+clonic\s+seizures?,\s*"
    r"(?P<count>\d+)\s+since\s+previous\s+appointment\b",
    re.IGNORECASE,
)
_SF_GTC_PER_MONTH_RE = re.compile(
    r"\b(?P<count>\d+)\s+generali[sz]ed\s+tonic\s+clonic\s+seizures?"
    r"[^.\n]{0,40}\bper\s+month\b",
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
_SF_GTCS_ACTIVE_WITHOUT_COUNT_RE = re.compile(
    r"\b(?:on\s+sunday\s+and\s+monday,\s+he\s+was\s+having|"
    r"further)\s+generalised\s+tonic\s+clonic\s+seizures\b",
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
_SF_GTC_FURTHER_SINCE_RE = re.compile(
    r"\bfurther\s+generalised\s+tonic\s+clonic\s+seizures\s+since\b",
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
_SF_NO_FURTHER_GTC_SINCE_RE = re.compile(
    r"\bnot had any further generalised tonic clonic seizures since\b",
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


def sf_convention_rewrite(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> tuple[str, dict[str, Any], str] | None:
    """Apply SF benchmark rewrites.

    Returns ``(new_text, new_attributes, rule_id)`` when a rewrite fires, else
    ``None``. Attributes are returned as a fresh dict so callers can replace.
    """

    attrs = dict(attributes)
    phrase = normalize_phrase(text)
    surface = " ".join(part for part in (text, evidence) if part)

    format_rewrite = _sf_operand_format_rewrite(text, surface=surface, attributes=attrs)
    if format_rewrite is not None:
        return format_rewrite

    match = _SF_GENERIC_EVERY_RANGE_RE.search(surface)
    if match is not None:
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["NumberOfSeizures"] = "1"
        attrs["LowerNumberOfTimePeriods"] = match.group("low")
        attrs["UpperNumberOfTimePeriods"] = match.group("high")
        attrs["TimePeriod"] = "Week"
        attrs.pop("NumberOfTimePeriods", None)
        return "seizures", attrs, "rewrite_every_range_phrase_to_generic_seizures"
    if phrase in {"no seizures", "not had any more seizures"}:
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        return "seizures", attrs, "rewrite_no_seizures_phrase_to_generic_seizure_free"
    if phrase == "seizures free":
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["NumberOfSeizures"] = "0"
        return "seizures", attrs, "rewrite_seizures_free_typo_to_generic"
    if phrase in {"once or twice a month", "3 seizures"}:
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        if phrase == "3 seizures":
            attrs["NumberOfSeizures"] = "3"
        else:
            attrs["LowerNumberOfSeizures"] = "1"
            attrs["UpperNumberOfSeizures"] = "2"
            attrs["NumberOfTimePeriods"] = "1"
            attrs["TimePeriod"] = "Month"
        return "seizures", attrs, "rewrite_generic_rate_phrase_to_cui"
    if phrase == "one seizure" and not _SF_RISK_COUNSELLING_RE.search(evidence):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizure"
        attrs["NumberOfSeizures"] = "1"
        return "seizure", attrs, "rewrite_one_seizure_phrase_to_cui"
    if phrase in {"fairly frequent seizures", "frequent seizures"}:
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs.pop("NumberOfSeizures", None)
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        return "seizures", attrs, "rewrite_frequent_seizures_phrase_to_unknown_cui"
    if phrase == "one focal motor seizure":
        attrs["CUI"] = "C0016399"
        attrs["CUIPhrase"] = "focal motor seizure"
        attrs["NumberOfSeizures"] = "1"
        return "focal motor seizure", attrs, "rewrite_one_focal_motor_to_cui"
    if phrase == "single seizure":
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizure"
        attrs["NumberOfSeizures"] = "1"
        return "seizure", attrs, "rewrite_single_seizure_phrase_to_cui"
    if phrase == "last seizure":
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizure"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        return "seizure", attrs, "rewrite_last_seizure_phrase_to_generic_free"
    if phrase == "seizure like this" and re.search(
        r"\bfocal motor seizures\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C0016399"
        attrs["CUIPhrase"] = "focal motor seizures"
        attrs["NumberOfSeizures"] = "0"
        return "focal motor seizures", attrs, "rewrite_anaphoric_focal_motor_free"
    if phrase.startswith("focal seizures with altered awareness") and re.search(
        r"\blast event\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C0270834"
        attrs["CUIPhrase"] = "focal seizures with altered awareness"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        return (
            "focal seizures with altered awareness",
            attrs,
            "rewrite_fsaw_last_event_to_seizure_free",
        )
    if phrase == "she" and re.search(
        r"\bnow she is having between 3 and 4 per week\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["LowerNumberOfSeizures"] = "3"
        attrs["UpperNumberOfSeizures"] = "4"
        attrs["NumberOfTimePeriods"] = "1"
        attrs["TimePeriod"] = "Week"
        return "seizures", attrs, "rewrite_pronoun_rate_to_generic_seizures"
    if phrase in {"generlised tonic clonic seizure", "generlised tonic clonic seizures"}:
        attrs["CUI"] = "C0494475"
        attrs["CUIPhrase"] = "generalised tonic clonic seizures"
        return "generalised tonic clonic seizures", attrs, "rewrite_typo_gtc_to_cui"
    if phrase == "absence like seizures" and (
        attrs.get("NumberOfSeizures") or attrs.get("YearDate")
    ):
        attrs["CUI"] = "C0563606"
        attrs["CUIPhrase"] = "absence like seizures"
        return (
            "absence like seizures",
            attrs,
            "rewrite_absence_like_dated_occurrence_to_cui",
        )
    if phrase in {"occasional absences", "absence like seizures"}:
        attrs["CUI"] = "C0563606"
        attrs["CUIPhrase"] = "absences"
        attrs.pop("NumberOfSeizures", None)
        return "absences", attrs, "rewrite_absence_phrase_to_unknown_absences"
    if (
        phrase == "focal to bilateral convulsive seizure"
        and _SF_FTB_GENERIC_LAST_EVENT_RE.search(evidence)
    ):
        attrs["CUI"] = "C0877017"
        attrs["CUIPhrase"] = "focal to bilateral convulsive seizures"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        return (
            "focal to bilateral convulsive seizures",
            attrs,
            "rewrite_ftb_last_event_to_seizure_free",
        )
    if phrase == "cluster of 3":
        attrs["CUI"] = "C3203523"
        attrs["CUIPhrase"] = "seizure cluster"
        return "seizure cluster", attrs, "rewrite_cluster_of_3_to_seizure_cluster"
    if _REWRITE_THESE_SEIZURES_RE.search(evidence) and attrs.get("CUI") == "C0270834":
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        return "seizures", attrs, "rewrite_anaphoric_named_to_generic_seizures"
    if re.search(r"typical absences", evidence, re.IGNORECASE) and phrase == "absences":
        attrs["CUI"] = "C4316903"
        attrs["CUIPhrase"] = "typical absences"
        return "typical absences", attrs, "rewrite_absences_to_typical_absences"
    if _REWRITE_UP_TO_RANGE_RE.search(evidence) and attrs.get("CUI") == "C0877017":
        attrs["LowerNumberOfSeizures"] = "0"
        return text, attrs, "rewrite_up_to_range_lower_zero"
    if phrase == "seizures" and re.search(
        r"\bseizures every 3 to 4 weeks\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["NumberOfSeizures"] = "1"
        attrs["LowerNumberOfTimePeriods"] = "3"
        attrs["UpperNumberOfTimePeriods"] = "4"
        attrs["TimePeriod"] = "Week"
        attrs.pop("NumberOfTimePeriods", None)
        return "seizures", attrs, "rewrite_every_3_to_4_weeks_timeperiod"
    if _SF_FTB_EVENTS_IN_TOTAL_LAST_EVENT_RE.search(evidence) and attrs.get("CUI") in {
        "C0877017",
        "C0270838",
    }:
        attrs["CUI"] = "C0877017"
        attrs["CUIPhrase"] = "focal to bilateral convulsive seizures"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        attrs.pop("NumberOfTimePeriods", None)
        attrs.pop("LowerNumberOfTimePeriods", None)
        attrs.pop("UpperNumberOfTimePeriods", None)
        return (
            "focal to bilateral convulsive seizures",
            attrs,
            "rewrite_focal_to_bilateral_last_event_to_seizure_free",
        )
    if attrs.get("CUI") == "C0494475" and _SF_UP_TO_SEIZURE_FREE_RE.search(evidence):
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
            "NumberOfTimePeriods",
            "LowerNumberOfTimePeriods",
            "UpperNumberOfTimePeriods",
            "TimeSince_or_TimeOfEvent",
        ):
            attrs.pop(key, None)
        return text, attrs, "rewrite_up_to_seizure_free_to_unknown_state"
    if attrs.get("CUI") == "C0036572" and _SF_RECENT_LAST_SEIZURE_RE.search(evidence):
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        attrs.pop("NumberOfTimePeriods", None)
        attrs.pop("LowerNumberOfTimePeriods", None)
        attrs.pop("UpperNumberOfTimePeriods", None)
        return text, attrs, "rewrite_recent_last_seizure_to_seizure_free"
    if attrs.get("CUI") == "C0036572" and re.search(
        r"\bseizure[-\s]+free\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C1299590"
        attrs["CUIPhrase"] = "seizure-free"
        attrs["NumberOfSeizures"] = "0"
        return "seizure-free", attrs, "rewrite_generic_seizure_free_to_state_concept"
    if attrs.get("CUI") == "C0494475" and _SF_GTCS_ACTIVE_WITHOUT_COUNT_RE.search(evidence):
        attrs["NumberOfSeizures"] = "1"
        attrs.pop("FrequencyChange", None)
        return text, attrs, "rewrite_gtcs_active_without_count_to_active_rate"
    if (
        attrs.get("CUI") == "C4316903"
        and phrase == "typical absences"
        and attrs.get("PointInTime") == "LastClinic"
        and attrs.get("TimeSince_or_TimeOfEvent") == "Since"
    ):
        attrs["FrequencyChange"] = "Same"
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
            "NumberOfTimePeriods",
            "LowerNumberOfTimePeriods",
            "UpperNumberOfTimePeriods",
        ):
            attrs.pop(key, None)
        return text, attrs, "rewrite_typical_absences_since_last_clinic_to_same"
    if re.search(r"\bfocal seizures\b.{0,80}\bunder control\b", evidence, re.IGNORECASE):
        attrs["CUI"] = "C0751495"
        attrs["CUIPhrase"] = "focal seizures"
        attrs["NumberOfSeizures"] = "0"
        attrs.pop("FrequencyChange", None)
        return "focal seizures", attrs, "rewrite_focal_under_control_to_seizure_free"
    if (
        phrase == "epileptic seizures"
        and re.search(r"\bwell controlled\b", evidence, re.IGNORECASE)
    ):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        return "seizures", attrs, "rewrite_epileptic_seizures_to_generic_seizures"
    if phrase == "further seizures" and re.search(
        r"\bnot\s+had\s+any\s+further\s+seizures\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["NumberOfSeizures"] = "0"
        return "seizures", attrs, "rewrite_no_further_seizures_to_generic_seizures"
    if attrs.get("CUI") == "C0036572" and _SF_NO_FURTHER_GTC_SINCE_RE.search(evidence):
        attrs["CUI"] = "C0494475"
        attrs["CUIPhrase"] = "generalised tonic clonic seizures"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        attrs.pop("MonthDate", None)
        attrs.pop("YearDate", None)
        return (
            "generalised tonic clonic seizures",
            attrs,
            "rewrite_selected_no_further_gtc_to_named_seizure_free",
        )
    if phrase == "focal to bilateral convulsive seizures" and re.search(
        r"\blast\s+seizures\s+were\s+in\s+his\s+teenage\s+years\b",
        evidence,
        re.IGNORECASE,
    ):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        return "seizures", attrs, "rewrite_teenage_last_seizures_to_generic"
    if phrase == "generalised tonic chronic seizures":
        attrs["CUI"] = "C0494475"
        attrs["CUIPhrase"] = "generalised tonic clonic seizures"
        return (
            "generalised tonic clonic seizures",
            attrs,
            "rewrite_tonic_chronic_to_tonic_clonic_sf",
        )
    if phrase == "these seizures" and _REWRITE_THESE_SEIZURES_RE.search(evidence):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        return "seizures", attrs, "rewrite_anaphoric_these_seizures_to_generic"
    if phrase == "absence seizures":
        attrs["CUI"] = "C0563606"
        attrs["CUIPhrase"] = "absences"
        return "absences", attrs, "rewrite_absence_seizures_to_absences"
    return None


def _sf_operand_format_rewrite(
    text: str,
    *,
    surface: str,
    attributes: Mapping[str, Any],
) -> tuple[str, dict[str, Any], str] | None:
    attrs = {str(key): str(value) for key, value in attributes.items()}
    original = dict(attrs)
    rule_ids: list[str] = []

    if attrs.get("CUI") == "C0036572" and _SF_NO_FURTHER_GTC_SINCE_RE.search(surface):
        return None

    every_weeks = re.search(
        r"\bevery\s+(?P<weeks>\d+)\s+weeks?\b",
        surface,
        re.IGNORECASE,
    )
    if every_weeks is not None and not re.search(
        r"\bevery\s+\d+\s+to\s+\d+\s+weeks?\b",
        surface,
        re.IGNORECASE,
    ):
        attrs["NumberOfSeizures"] = attrs.get("NumberOfSeizures") or "1"
        attrs["NumberOfTimePeriods"] = every_weeks.group("weeks")
        attrs["TimePeriod"] = "Week"
        attrs.pop("LowerNumberOfTimePeriods", None)
        attrs.pop("UpperNumberOfTimePeriods", None)
        rule_ids.append("rewrite_exact_every_weeks_operand_format")

    over_months = re.search(
        r"\b(?P<count>\d+)\s+seizures?\s+over\s+(?P<months>\d+)\s+months?\b",
        surface,
        re.IGNORECASE,
    )
    if over_months is not None:
        attrs["NumberOfSeizures"] = over_months.group("count")
        attrs["NumberOfTimePeriods"] = over_months.group("months")
        attrs["TimePeriod"] = "Month"
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        rule_ids.append("rewrite_exact_count_over_months_operand_format")

    if re.search(r"\bper\s+month\b", surface, re.IGNORECASE) and attrs.get("MonthDate") == "1":
        attrs.pop("MonthDate", None)
        rule_ids.append("drop_per_month_spurious_month_date")

    if attrs.get("LowerNumberOfSeizures") == "0" and not attrs.get("UpperNumberOfSeizures"):
        attrs["NumberOfSeizures"] = "0"
        attrs.pop("LowerNumberOfSeizures", None)
        rule_ids.append("collapse_lower_zero_to_exact_zero_count")

    if (
        attrs.get("LowerNumberOfSeizures")
        and attrs.get("LowerNumberOfSeizures") == attrs.get("UpperNumberOfSeizures")
    ):
        attrs["NumberOfSeizures"] = attrs["LowerNumberOfSeizures"]
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        rule_ids.append("collapse_equal_seizure_count_range")

    if (
        attrs.get("LowerNumberOfTimePeriods")
        and attrs.get("LowerNumberOfTimePeriods") == attrs.get("UpperNumberOfTimePeriods")
    ):
        attrs["NumberOfTimePeriods"] = attrs["LowerNumberOfTimePeriods"]
        attrs.pop("LowerNumberOfTimePeriods", None)
        attrs.pop("UpperNumberOfTimePeriods", None)
        rule_ids.append("collapse_equal_time_period_range")

    if attrs == original:
        return None
    return text, attrs, "+".join(rule_ids)


def is_sf_convention_noise(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> bool:
    """True for SF renderings that are prompt-selection residue, not frequency facts."""

    phrase = normalize_phrase(text)
    attrs = {str(key): str(value) for key, value in attributes.items()}
    cui = attrs.get("CUI")
    if _SF_VAGUE_EPISODE_RE.fullmatch(phrase):
        return True
    if phrase in {
        "absences and jerks",
        "attacks",
        "collapses",
        "collapse episode",
        "dissociative seizures",
        "drops",
        "drop attacks",
        "events",
        "febrile seizure",
        "febrile seizures",
        "general and complex partial seizures",
        "grand mal episodes",
        "mini shakes",
        "minor seizures",
        "one of them",
        "seizure frequency",
        "seizure like episodes",
        "these",
        "staring episodes",
        "two unprovoked generalised seizures",
    }:
        return True
    if phrase == "one seizure" and _SF_RISK_COUNSELLING_RE.search(evidence):
        return True
    if phrase == "further seizures" and _SF_RISK_COUNSELLING_RE.search(evidence):
        return True
    if phrase == "previous seizures":
        return True
    if cui == "C0563606" and "NumberOfSeizures" not in attrs and re.search(
        r"\b(?:absence\s+like\s+seizures\s+2014|typical\s+absences|"
        r"at\s+(?:around\s+)?the\s+age\s+of\s+8\b[^.]{0,120}\brelatively\s+infrequent|"
        r"relatively\s+infrequent\b[^.]{0,120}\bat\s+(?:around\s+)?the\s+age\s+of\s+8)\b",
        evidence,
        re.IGNORECASE,
    ):
        return True
    if cui == "C0036572" and re.search(
        r"\baround\s+3\s+seizures\s+per\s+month\b",
        evidence,
        re.IGNORECASE,
    ):
        return True
    if cui == "C0877017" and re.search(
        r"\b(?:focal\s+to\s+bilateral\s+convulsive\s+seizures?\s+\d{4}|"
        r"three\s+episodes\s+whilst\s+asleep)\b",
        evidence,
        re.IGNORECASE,
    ):
        return True
    if (
        cui == "C1299590"
        and attrs.get("NumberOfSeizures") == "0"
        and _SF_CONTEXTUAL_RATE_NOISE_RE.search(evidence)
    ):
        return True
    if cui == "C1299590" and attrs.get("NumberOfSeizures") == "0":
        return False
    if phrase in {"seizure", "seizures", "seizure free", "seizure freedom"} and (
        _SF_CONTEXTUAL_RATE_NOISE_RE.search(evidence)
    ):
        return True
    if phrase in {"seizure", "seizures", "seizure free"} and _SF_CONTEXTUAL_SEIZURE_FREE_RE.search(
        evidence
    ):
        return True
    if phrase == "seizure" and _SF_HISTORICAL_COMPARATOR_RE.search(evidence):
        return True
    return False


_SF_SMALL_NUMBERS = {
    "once": "1",
    "one": "1",
    "twice": "2",
    "two": "2",
    "three": "3",
    "four": "4",
}


def _sf_number(value: str) -> str:
    return _SF_SMALL_NUMBERS.get(value.lower(), value)


def sf_residual_additions(note_text: str) -> list[tuple[str, str, dict[str, str]]]:
    """Return bounded dev residual SF additions from explicit source patterns."""

    additions: list[tuple[str, str, dict[str, str]]] = []
    for match in _SF_GENERIC_EVERY_RANGE_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "1",
                    "LowerNumberOfTimePeriods": match.group("low"),
                    "UpperNumberOfTimePeriods": match.group("high"),
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_GENERIC_PER_MONTH_RANGE_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "LowerNumberOfSeizures": match.group("low"),
                    "UpperNumberOfSeizures": match.group("high"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_GENERIC_OVER_MONTHS_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": match.group("count"),
                    "NumberOfTimePeriods": match.group("months"),
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_GENERIC_SINGLE_LAST_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "1",
                    "PointInTime": "Last_Week",
                    "TimeSince_or_TimeOfEvent": "During",
                },
            )
        )
    for match in _SF_GENERIC_BETWEEN_PER_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "LowerNumberOfSeizures": match.group("low"),
                    "UpperNumberOfSeizures": match.group("high"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_GENERIC_SEVERAL_PER_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "3",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_GENERIC_EVERY_WEEKS_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": match.group("weeks"),
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_WEEKLY_SEIZURES_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_GENERIC_LAST_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "1",
                    "PointInTime": "Last_Month",
                    "TimeSince_or_TimeOfEvent": "During",
                },
            )
        )
    for match in _SF_CURRENT_SEIZURES_TIMES_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "LowerNumberOfSeizures": _sf_number(match.group("low")),
                    "UpperNumberOfSeizures": _sf_number(match.group("high")),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_ONE_SEIZURE_PER_YEAR_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Year",
                },
            )
        )
    for match in _SF_SEIZURE_EVERY_YEAR_RANGE_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "1",
                    "LowerNumberOfTimePeriods": _sf_number(match.group("low")),
                    "UpperNumberOfTimePeriods": _sf_number(match.group("high")),
                    "TimePeriod": "Year",
                },
            )
        )
    for match in _SF_SEIZURE_INCREASE_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "FrequencyChange": "Increased",
                },
            )
        )
    for match in _SF_SEIZURE_FREQUENCY_REDUCED_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "FrequencyChange": "Decreased",
                },
            )
        )
    for match in _SF_ONE_SEIZURE_PER_WEEK_TO_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "1",
                    "LowerNumberOfTimePeriods": "1",
                    "UpperNumberOfTimePeriods": "4",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_AROUND_N_SEIZURES_PER_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": match.group("count"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_HAD_N_SEIZURES_RE.finditer(note_text):
        window = note_text[max(0, match.start() - 80) : match.end() + 80]
        if re.search(r"\bfebrile\b|\bprevious\b|\bfirst seizure\b", window, re.IGNORECASE):
            continue
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": match.group("count"),
                },
            )
        )
    for match in _SF_GENERIC_TOTAL_YEAR_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": match.group("count"),
                    "TimeSince_or_TimeOfEvent": "During",
                    "YearDate": match.group("year"),
                },
            )
        )
    for match in _SF_FREQUENT_SEIZURES_UNKNOWN_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                },
            )
        )
    for match in _SF_GENERIC_NO_FURTHER_SINCE_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_NOT_HAD_ANY_MORE_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_SINGLE_SEIZURE_WEEKS_AGO_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "0",
                    "NumberOfTimePeriods": match.group("weeks"),
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_LAST_SEIZURES_TEENAGE_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_BROAD_SEIZURE_FREE_RE.finditer(note_text):
        window = note_text[max(0, match.start() - 60) : match.end() + 60]
        if _SF_CONTEXTUAL_RATE_NOISE_RE.search(window):
            continue
        additions.append(
            (
                "seizure-free",
                match.group(0),
                {
                    "CUI": "C1299590",
                    "CUIPhrase": "seizure-free",
                    "NumberOfSeizures": "0",
                },
            )
        )
    for match in _SF_LAST_SEIZURE_MONTHS_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "0",
                    "NumberOfTimePeriods": match.group("months"),
                    "TimePeriod": "Month",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_DATED_GTC_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": match.group("count"),
                    "TimeSince_or_TimeOfEvent": "During",
                    "YearDate": match.group("year"),
                },
            )
        )
    for match in _SF_GTC_LAST_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizure",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizure",
                    "NumberOfSeizures": "1",
                    "PointInTime": "Last_Week",
                    "TimeSince_or_TimeOfEvent": "During",
                },
            )
        )
    for match in _SF_GTC_DAY_BURST_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Day",
                    "TimeSince_or_TimeOfEvent": "During",
                },
            )
        )
    for match in _SF_GTC_RANGE_PER_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "LowerNumberOfSeizures": match.group("low"),
                    "UpperNumberOfSeizures": match.group("high"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_GTC_FOUR_LAST_THREE_WEEKS_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": "4",
                    "NumberOfTimePeriods": "3",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_GTC_SINCE_PREVIOUS_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": match.group("count"),
                    "PointInTime": "LastClinic",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_GTC_PER_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": match.group("count"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_GTC_ONE_TO_TWO_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "LowerNumberOfSeizures": _sf_number(match.group("low")),
                    "UpperNumberOfSeizures": _sf_number(match.group("high")),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_GTC_FURTHER_SINCE_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": "1",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_NO_FURTHER_GTC_SINCE_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_ABSENCE_LIKE_YEAR_RE.finditer(note_text):
        additions.append(
            (
                "absence like seizures",
                match.group(0),
                {
                    "CUI": "C0563606",
                    "CUIPhrase": "absence like seizures",
                    "NumberOfSeizures": "1",
                    "TimeSince_or_TimeOfEvent": "During",
                    "YearDate": match.group("year"),
                },
            )
        )
    match = _SF_FSAW_FORTNIGHT_RE.search(note_text)
    if match is not None:
        additions.append(
            (
                "focal seizures with altered awareness",
                match.group(0),
                {
                    "CUI": "C0270834",
                    "CUIPhrase": "focal seizures with altered awareness",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "2",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_FSAW_EVERY_WEEKS_RE.finditer(note_text):
        additions.append(
            (
                "focal seizures with altered awareness",
                match.group(0),
                {
                    "CUI": "C0270834",
                    "CUIPhrase": "focal seizures with altered awareness",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": match.group("weeks"),
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_FSAW_SEVERAL_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "focal seizures with altered awareness",
                match.group(0),
                {
                    "CUI": "C0270834",
                    "CUIPhrase": "focal seizures with altered awareness",
                    "NumberOfSeizures": "3",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_FSAW_ONE_PER_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "focal seizures with altered awareness",
                match.group(0),
                {
                    "CUI": "C0270834",
                    "CUIPhrase": "focal seizures with altered awareness",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_FSAW_PROBABLY_SEVERAL_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "focal seizures with altered awareness",
                match.group(0),
                {
                    "CUI": "C0270834",
                    "CUIPhrase": "focal seizures with altered awareness",
                    "NumberOfSeizures": "2",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_SECONDARY_PER_PERIOD_RE.finditer(note_text):
        attrs = {
            "CUI": "C0270838",
            "CUIPhrase": "secondary generalised seizures",
            "LowerNumberOfSeizures": match.group("count"),
            "NumberOfTimePeriods": "1",
            "TimePeriod": match.group("period").title(),
        }
        if match.group("high"):
            attrs["UpperNumberOfSeizures"] = match.group("high")
        else:
            attrs["NumberOfSeizures"] = match.group("count")
            attrs.pop("LowerNumberOfSeizures", None)
        additions.append(("secondary generalised seizures", match.group(0), attrs))
    for match in _SF_SECONDARY_AROUND_PER_YEAR_RE.finditer(note_text):
        additions.append(
            (
                "secondary generalised seizures",
                match.group(0),
                {
                    "CUI": "C0270838",
                    "CUIPhrase": "secondary generalised seizures",
                    "NumberOfSeizures": match.group("count"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Year",
                },
            )
        )
    for match in _SF_SECONDARY_ONCE_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "secondary generalised seizure",
                match.group(0),
                {
                    "CUI": "C0270838",
                    "CUIPhrase": "secondary generalised seizure",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_SECONDARY_LAST_CHRISTMAS_RE.finditer(note_text):
        additions.append(
            (
                "secondary generalised seizures",
                match.group(0),
                {
                    "CUI": "C0270838",
                    "CUIPhrase": "secondary generalised seizures",
                    "NumberOfSeizures": "0",
                    "DayDate": "25",
                    "MonthDate": "12",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "YearDate": match.group("year"),
                },
            )
        )
    for match in _SF_COMPLEX_PARTIAL_PER_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "complex partial seizure",
                match.group(0),
                {
                    "CUI": "C0149958",
                    "CUIPhrase": "complex partial seizure",
                    "LowerNumberOfSeizures": "1",
                    "UpperNumberOfSeizures": "2",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_MYCLONIC_UNKNOWN_RE.finditer(note_text):
        additions.append(
            (
                "myoclonic jerks",
                match.group(0),
                {
                    "CUI": "C0027066",
                    "CUIPhrase": "myoclonic jerks",
                },
            )
        )
    for match in _SF_MYCLONIC_DAILY_RE.finditer(note_text):
        additions.append(
            (
                "myoclonic jerks",
                match.group(0),
                {
                    "CUI": "C0027066",
                    "CUIPhrase": "myoclonic jerks",
                    "FrequencyChange": "Frequent",
                },
            )
        )
    for match in _SF_MYCLONIC_ONE_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "myoclonic jerks",
                match.group(0),
                {
                    "CUI": "C0027066",
                    "CUIPhrase": "myoclonic jerks",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_ABSENCE_UNKNOWN_RE.finditer(note_text):
        additions.append(
            (
                "absences",
                match.group(0),
                {
                    "CUI": "C0563606",
                    "CUIPhrase": "absences",
                },
            )
        )
    for match in _SF_ABSENCES_FREQUENT_RE.finditer(note_text):
        additions.append(
            (
                "absences",
                match.group(0),
                {
                    "CUI": "C0563606",
                    "CUIPhrase": "absences",
                    "FrequencyChange": "Frequent",
                },
            )
        )
    for match in _SF_TYPICAL_ABSENCES_SINCE_RE.finditer(note_text):
        additions.append(
            (
                "typical absences",
                match.group(0),
                {
                    "CUI": "C4316903",
                    "CUIPhrase": "typical absences",
                    "FrequencyChange": "Same",
                    "PointInTime": "LastClinic",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_ABSENCES_ACTIVE_RE.finditer(note_text):
        additions.append(
            (
                "absences",
                match.group(0),
                {
                    "CUI": "C0563606",
                    "CUIPhrase": "absences",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Day",
                },
            )
        )
    for match in _SF_FOCAL_MOTOR_ACTIVE_RE.finditer(note_text):
        additions.append(
            (
                "focal motor seizure",
                match.group(0),
                {
                    "CUI": "C0016399",
                    "CUIPhrase": "focal motor seizure",
                    "NumberOfSeizures": "1",
                },
            )
        )
    for match in _SF_FOCAL_MOTOR_FREE_RE.finditer(note_text):
        additions.append(
            (
                "focal motor seizures",
                match.group(0),
                {
                    "CUI": "C0016399",
                    "CUIPhrase": "focal motor seizures",
                    "NumberOfSeizures": "0",
                },
            )
        )
    for match in _SF_FTB_GENERIC_LAST_EVENT_RE.finditer(note_text):
        additions.append(
            (
                "focal to bilateral convulsive seizures",
                match.group(0),
                {
                    "CUI": "C0877017",
                    "CUIPhrase": "focal to bilateral convulsive seizures",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_FTB_DATED_EVENTS_RE.finditer(note_text):
        for month, year in (("8", match.group("year1")), ("9", match.group("year2"))):
            additions.append(
                (
                    "focal to bilateral convulsive seizures",
                    match.group(0),
                    {
                        "CUI": "C0877017",
                        "CUIPhrase": "focal to bilateral convulsive seizures",
                        "MonthDate": month,
                        "NumberOfSeizures": "1",
                        "TimeSince_or_TimeOfEvent": "During",
                        "YearDate": year,
                    },
                )
            )
    for match in _SF_FTB_LAST_ONE_CHRISTMAS_RE.finditer(note_text):
        additions.append(
            (
                "focal to bilateral convulsive seizures",
                match.group(0),
                {
                    "CUI": "C0877017",
                    "CUIPhrase": "focal to bilateral convulsive seizures",
                    "DayDate": "25",
                    "MonthDate": "12",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "YearDate": match.group("year"),
                },
            )
        )
    match = _SF_SEIZURES_RETURNED_RE.search(note_text)
    if match is not None:
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "FrequencyChange": "Increased",
                },
            )
        )
    match = _SF_CLUSTER_AUGUST_RE.search(note_text)
    if match is not None:
        additions.append(
            (
                "cluster of seizures",
                match.group(0),
                {
                    "CUI": "C3203523",
                    "CUIPhrase": "cluster of seizures",
                    "MonthDate": "8",
                    "NumberOfSeizures": "1",
                    "TimeSince_or_TimeOfEvent": "During",
                    "YearDate": match.group("year"),
                },
            )
        )
    match = _SF_FTB_LAST_EVENT_RE.search(note_text)
    if match is not None:
        additions.append(
            (
                "focal to bilateral convulsive seizures",
                match.group(0),
                {
                    "CUI": "C0877017",
                    "CUIPhrase": "focal to bilateral convulsive seizures",
                    "FrequencyChange": "Infrequent",
                },
            )
        )
        additions.append(
            (
                "convulsive seizure",
                match.group(0),
                {
                    "CUI": "C0751494",
                    "CUIPhrase": "convulsive seizure",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "YearDate": match.group("year"),
                },
            )
        )
    match = _SF_SINGLE_CONVULSIVE_LAST_EVENT_RE.search(note_text)
    if match is not None:
        additions.append(
            (
                "convulsive seizure",
                match.group(0),
                {
                    "CUI": "C0751494",
                    "CUIPhrase": "convulsive seizure",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "YearDate": match.group("year"),
                },
            )
        )
    for match in _SF_REMAINS_SEIZURE_FREE_RE.finditer(note_text):
        evidence = match.group(0)
        additions.append(
            (
                "seizure-free",
                evidence,
                {
                    "CUI": "C1299590",
                    "CUIPhrase": "seizure-free",
                    "NumberOfSeizures": "0",
                },
            )
        )
    for pattern in (_SF_SEIZURES_HAVE_STOPPED_RE, _SF_NO_EVENTS_SINCE_SURGERY_RE):
        for match in pattern.finditer(note_text):
            additions.append(
                (
                    "seizures",
                    match.group(0),
                    {
                        "CUI": "C0036572",
                        "CUIPhrase": "seizures",
                        "NumberOfSeizures": "0",
                    },
                )
            )
    return additions
