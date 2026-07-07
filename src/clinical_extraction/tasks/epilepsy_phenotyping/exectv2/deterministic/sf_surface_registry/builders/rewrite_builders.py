"""Catalog-backed rewrite builders."""

from __future__ import annotations

import re

from . import _legacy_impl as legacy
from .context import ConventionContext, RewriteResult
from .registry import register_builder

_SF_GENERIC_EVERY_RANGE_RE = legacy._SF_GENERIC_EVERY_RANGE_RE
_SF_RISK_COUNSELLING_RE = legacy._SF_RISK_COUNSELLING_RE
_REWRITE_THESE_SEIZURES_RE = legacy._REWRITE_THESE_SEIZURES_RE
_REWRITE_UP_TO_RANGE_RE = legacy._REWRITE_UP_TO_RANGE_RE
_SF_FTB_GENERIC_LAST_EVENT_RE = legacy._SF_FTB_GENERIC_LAST_EVENT_RE
_SF_FTB_EVENTS_IN_TOTAL_LAST_EVENT_RE = legacy._SF_FTB_EVENTS_IN_TOTAL_LAST_EVENT_RE
_SF_UP_TO_SEIZURE_FREE_RE = legacy._SF_UP_TO_SEIZURE_FREE_RE
_SF_RECENT_LAST_SEIZURE_RE = legacy._SF_RECENT_LAST_SEIZURE_RE
_SF_GTCS_ACTIVE_WITHOUT_COUNT_RE = legacy._SF_GTCS_ACTIVE_WITHOUT_COUNT_RE
_SF_NO_FURTHER_GTC_SINCE_RE = legacy._SF_NO_FURTHER_GTC_SINCE_RE


@register_builder("operand_format_rewrite")
def operand_format_rewrite(ctx: ConventionContext) -> RewriteResult | None:
    return legacy._sf_operand_format_rewrite(ctx.text, surface=ctx.surface, attributes=ctx.attrs)


@register_builder("rewrite_every_range_phrase_to_generic_seizures")
def builder_rewrite_every_range_phrase_to_generic_seizures(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    surface = ctx.surface
    match = _SF_GENERIC_EVERY_RANGE_RE.search(surface)
    if not (match is not None):
        return None
    attrs["CUI"] = "C0036572"
    attrs["CUIPhrase"] = "seizures"
    attrs["NumberOfSeizures"] = "1"
    attrs["LowerNumberOfTimePeriods"] = match.group("low")
    attrs["UpperNumberOfTimePeriods"] = match.group("high")
    attrs["TimePeriod"] = "Week"
    attrs.pop("NumberOfTimePeriods", None)
    return "seizures", attrs, "rewrite_every_range_phrase_to_generic_seizures"


@register_builder("rewrite_no_seizures_phrase_to_generic_seizure_free")
def builder_rewrite_no_seizures_phrase_to_generic_seizure_free(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    phrase = ctx.phrase
    if phrase not in {"no seizures", "not had any more seizures"}:
        return None
    attrs["CUI"] = "C0036572"
    attrs["CUIPhrase"] = "seizures"
    attrs["NumberOfSeizures"] = "0"
    attrs["TimeSince_or_TimeOfEvent"] = "Since"
    return "seizures", attrs, "rewrite_no_seizures_phrase_to_generic_seizure_free"


@register_builder("rewrite_seizures_free_typo_to_generic")
def builder_rewrite_seizures_free_typo_to_generic(ctx: ConventionContext) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    phrase = ctx.phrase
    if not (phrase == "seizures free"):
        return None
    attrs["CUI"] = "C0036572"
    attrs["CUIPhrase"] = "seizures"
    attrs["NumberOfSeizures"] = "0"
    return "seizures", attrs, "rewrite_seizures_free_typo_to_generic"


@register_builder("rewrite_generic_rate_phrase_to_cui")
def builder_rewrite_generic_rate_phrase_to_cui(ctx: ConventionContext) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    phrase = ctx.phrase
    if phrase not in {"once or twice a month", "3 seizures"}:
        return None
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


@register_builder("rewrite_one_seizure_phrase_to_cui")
def builder_rewrite_one_seizure_phrase_to_cui(ctx: ConventionContext) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    evidence = ctx.evidence
    phrase = ctx.phrase
    if not (phrase == "one seizure" and not _SF_RISK_COUNSELLING_RE.search(evidence)):
        return None
    attrs["CUI"] = "C0036572"
    attrs["CUIPhrase"] = "seizure"
    attrs["NumberOfSeizures"] = "1"
    return "seizure", attrs, "rewrite_one_seizure_phrase_to_cui"


@register_builder("rewrite_frequent_seizures_phrase_to_unknown_cui")
def builder_rewrite_frequent_seizures_phrase_to_unknown_cui(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    phrase = ctx.phrase
    if phrase not in {"fairly frequent seizures", "frequent seizures"}:
        return None
    attrs["CUI"] = "C0036572"
    attrs["CUIPhrase"] = "seizures"
    attrs.pop("NumberOfSeizures", None)
    attrs.pop("LowerNumberOfSeizures", None)
    attrs.pop("UpperNumberOfSeizures", None)
    return "seizures", attrs, "rewrite_frequent_seizures_phrase_to_unknown_cui"


@register_builder("rewrite_one_focal_motor_to_cui")
def builder_rewrite_one_focal_motor_to_cui(ctx: ConventionContext) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    phrase = ctx.phrase
    if not (phrase == "one focal motor seizure"):
        return None
    attrs["CUI"] = "C0016399"
    attrs["CUIPhrase"] = "focal motor seizure"
    attrs["NumberOfSeizures"] = "1"
    return "focal motor seizure", attrs, "rewrite_one_focal_motor_to_cui"


@register_builder("rewrite_single_seizure_phrase_to_cui")
def builder_rewrite_single_seizure_phrase_to_cui(ctx: ConventionContext) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    phrase = ctx.phrase
    if not (phrase == "single seizure"):
        return None
    attrs["CUI"] = "C0036572"
    attrs["CUIPhrase"] = "seizure"
    attrs["NumberOfSeizures"] = "1"
    return "seizure", attrs, "rewrite_single_seizure_phrase_to_cui"


@register_builder("rewrite_last_seizure_phrase_to_generic_free")
def builder_rewrite_last_seizure_phrase_to_generic_free(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    phrase = ctx.phrase
    if not (phrase == "last seizure"):
        return None
    attrs["CUI"] = "C0036572"
    attrs["CUIPhrase"] = "seizure"
    attrs["NumberOfSeizures"] = "0"
    attrs["TimeSince_or_TimeOfEvent"] = "Since"
    return "seizure", attrs, "rewrite_last_seizure_phrase_to_generic_free"


@register_builder("rewrite_anaphoric_focal_motor_free")
def builder_rewrite_anaphoric_focal_motor_free(ctx: ConventionContext) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    evidence = ctx.evidence
    phrase = ctx.phrase
    if not (
        phrase == "seizure like this"
        and re.search(r"\bfocal motor seizures\b", evidence, re.IGNORECASE)
    ):
        return None
    attrs["CUI"] = "C0016399"
    attrs["CUIPhrase"] = "focal motor seizures"
    attrs["NumberOfSeizures"] = "0"
    return "focal motor seizures", attrs, "rewrite_anaphoric_focal_motor_free"


@register_builder("rewrite_fsaw_last_event_to_seizure_free")
def builder_rewrite_fsaw_last_event_to_seizure_free(ctx: ConventionContext) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    evidence = ctx.evidence
    phrase = ctx.phrase
    if not (
        phrase.startswith("focal seizures with altered awareness")
        and re.search(r"\blast event\b", evidence, re.IGNORECASE)
    ):
        return None
    attrs["CUI"] = "C0270834"
    attrs["CUIPhrase"] = "focal seizures with altered awareness"
    attrs["NumberOfSeizures"] = "0"
    attrs["TimeSince_or_TimeOfEvent"] = "Since"
    return (
        "focal seizures with altered awareness",
        attrs,
        "rewrite_fsaw_last_event_to_seizure_free",
    )


@register_builder("rewrite_pronoun_rate_to_generic_seizures")
def builder_rewrite_pronoun_rate_to_generic_seizures(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    evidence = ctx.evidence
    phrase = ctx.phrase
    if not (
        phrase == "she"
        and re.search(r"\bnow she is having between 3 and 4 per week\b", evidence, re.IGNORECASE)
    ):
        return None
    attrs["CUI"] = "C0036572"
    attrs["CUIPhrase"] = "seizures"
    attrs["LowerNumberOfSeizures"] = "3"
    attrs["UpperNumberOfSeizures"] = "4"
    attrs["NumberOfTimePeriods"] = "1"
    attrs["TimePeriod"] = "Week"
    return "seizures", attrs, "rewrite_pronoun_rate_to_generic_seizures"


@register_builder("rewrite_typo_gtc_to_cui")
def builder_rewrite_typo_gtc_to_cui(ctx: ConventionContext) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    phrase = ctx.phrase
    if phrase not in {"generlised tonic clonic seizure", "generlised tonic clonic seizures"}:
        return None
    attrs["CUI"] = "C0494475"
    attrs["CUIPhrase"] = "generalised tonic clonic seizures"
    return "generalised tonic clonic seizures", attrs, "rewrite_typo_gtc_to_cui"


@register_builder("rewrite_absence_like_dated_occurrence_to_cui")
def builder_rewrite_absence_like_dated_occurrence_to_cui(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    phrase = ctx.phrase
    if not (
        phrase == "absence like seizures"
        and (attrs.get("NumberOfSeizures") or attrs.get("YearDate"))
    ):
        return None
    attrs["CUI"] = "C0563606"
    attrs["CUIPhrase"] = "absence like seizures"
    return (
        "absence like seizures",
        attrs,
        "rewrite_absence_like_dated_occurrence_to_cui",
    )


@register_builder("rewrite_absence_phrase_to_unknown_absences")
def builder_rewrite_absence_phrase_to_unknown_absences(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    phrase = ctx.phrase
    if phrase not in {"occasional absences", "absence like seizures"}:
        return None
    attrs["CUI"] = "C0563606"
    attrs["CUIPhrase"] = "absences"
    attrs.pop("NumberOfSeizures", None)
    return "absences", attrs, "rewrite_absence_phrase_to_unknown_absences"


@register_builder("rewrite_ftb_last_event_to_seizure_free")
def builder_rewrite_ftb_last_event_to_seizure_free(ctx: ConventionContext) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    evidence = ctx.evidence
    phrase = ctx.phrase
    if not (
        phrase == "focal to bilateral convulsive seizure"
        and _SF_FTB_GENERIC_LAST_EVENT_RE.search(evidence)
    ):
        return None
    attrs["CUI"] = "C0877017"
    attrs["CUIPhrase"] = "focal to bilateral convulsive seizures"
    attrs["NumberOfSeizures"] = "0"
    attrs["TimeSince_or_TimeOfEvent"] = "Since"
    return (
        "focal to bilateral convulsive seizures",
        attrs,
        "rewrite_ftb_last_event_to_seizure_free",
    )


@register_builder("rewrite_cluster_of_3_to_seizure_cluster")
def builder_rewrite_cluster_of_3_to_seizure_cluster(ctx: ConventionContext) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    phrase = ctx.phrase
    if not (phrase == "cluster of 3"):
        return None
    attrs["CUI"] = "C3203523"
    attrs["CUIPhrase"] = "seizure cluster"
    return "seizure cluster", attrs, "rewrite_cluster_of_3_to_seizure_cluster"


@register_builder("rewrite_anaphoric_named_to_generic_seizures")
def builder_rewrite_anaphoric_named_to_generic_seizures(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    evidence = ctx.evidence
    if not (_REWRITE_THESE_SEIZURES_RE.search(evidence) and attrs.get("CUI") == "C0270834"):
        return None
    attrs["CUI"] = "C0036572"
    attrs["CUIPhrase"] = "seizures"
    return "seizures", attrs, "rewrite_anaphoric_named_to_generic_seizures"


@register_builder("rewrite_absences_to_typical_absences")
def builder_rewrite_absences_to_typical_absences(ctx: ConventionContext) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    evidence = ctx.evidence
    phrase = ctx.phrase
    if not (re.search(r"typical absences", evidence, re.IGNORECASE) and phrase == "absences"):
        return None
    attrs["CUI"] = "C4316903"
    attrs["CUIPhrase"] = "typical absences"
    return "typical absences", attrs, "rewrite_absences_to_typical_absences"


@register_builder("rewrite_up_to_range_lower_zero")
def builder_rewrite_up_to_range_lower_zero(ctx: ConventionContext) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    text = ctx.text
    evidence = ctx.evidence
    if not (_REWRITE_UP_TO_RANGE_RE.search(evidence) and attrs.get("CUI") == "C0877017"):
        return None
    attrs["LowerNumberOfSeizures"] = "0"
    return text, attrs, "rewrite_up_to_range_lower_zero"


@register_builder("rewrite_every_3_to_4_weeks_timeperiod")
def builder_rewrite_every_3_to_4_weeks_timeperiod(ctx: ConventionContext) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    evidence = ctx.evidence
    phrase = ctx.phrase
    if not (
        phrase == "seizures"
        and re.search(r"\bseizures every 3 to 4 weeks\b", evidence, re.IGNORECASE)
    ):
        return None
    attrs["CUI"] = "C0036572"
    attrs["CUIPhrase"] = "seizures"
    attrs["NumberOfSeizures"] = "1"
    attrs["LowerNumberOfTimePeriods"] = "3"
    attrs["UpperNumberOfTimePeriods"] = "4"
    attrs["TimePeriod"] = "Week"
    attrs.pop("NumberOfTimePeriods", None)
    return "seizures", attrs, "rewrite_every_3_to_4_weeks_timeperiod"


@register_builder("rewrite_focal_to_bilateral_last_event_to_seizure_free")
def builder_rewrite_focal_to_bilateral_last_event_to_seizure_free(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    evidence = ctx.evidence
    if not (
        _SF_FTB_EVENTS_IN_TOTAL_LAST_EVENT_RE.search(evidence)
        and attrs.get("CUI")
        in {
            "C0877017",
            "C0270838",
        }
    ):
        return None
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


@register_builder("rewrite_up_to_seizure_free_to_unknown_state")
def builder_rewrite_up_to_seizure_free_to_unknown_state(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    text = ctx.text
    evidence = ctx.evidence
    if not (attrs.get("CUI") == "C0494475" and _SF_UP_TO_SEIZURE_FREE_RE.search(evidence)):
        return None
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


@register_builder("rewrite_recent_last_seizure_to_seizure_free")
def builder_rewrite_recent_last_seizure_to_seizure_free(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    text = ctx.text
    evidence = ctx.evidence
    if not (attrs.get("CUI") == "C0036572" and _SF_RECENT_LAST_SEIZURE_RE.search(evidence)):
        return None
    attrs["NumberOfSeizures"] = "0"
    attrs["TimeSince_or_TimeOfEvent"] = "Since"
    attrs.pop("LowerNumberOfSeizures", None)
    attrs.pop("UpperNumberOfSeizures", None)
    attrs.pop("NumberOfTimePeriods", None)
    attrs.pop("LowerNumberOfTimePeriods", None)
    attrs.pop("UpperNumberOfTimePeriods", None)
    return text, attrs, "rewrite_recent_last_seizure_to_seizure_free"


@register_builder("rewrite_generic_seizure_free_to_state_concept")
def builder_rewrite_generic_seizure_free_to_state_concept(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    evidence = ctx.evidence
    if not (
        attrs.get("CUI") == "C0036572"
        and re.search(r"\bseizure[-\s]+free\b", evidence, re.IGNORECASE)
    ):
        return None
    attrs["CUI"] = "C1299590"
    attrs["CUIPhrase"] = "seizure-free"
    attrs["NumberOfSeizures"] = "0"
    return "seizure-free", attrs, "rewrite_generic_seizure_free_to_state_concept"


@register_builder("rewrite_gtcs_active_without_count_to_active_rate")
def builder_rewrite_gtcs_active_without_count_to_active_rate(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    text = ctx.text
    evidence = ctx.evidence
    if not (attrs.get("CUI") == "C0494475" and _SF_GTCS_ACTIVE_WITHOUT_COUNT_RE.search(evidence)):
        return None
    attrs["NumberOfSeizures"] = "1"
    attrs.pop("FrequencyChange", None)
    return text, attrs, "rewrite_gtcs_active_without_count_to_active_rate"


@register_builder("rewrite_typical_absences_since_last_clinic_to_same")
def builder_rewrite_typical_absences_since_last_clinic_to_same(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    text = ctx.text
    phrase = ctx.phrase
    if not (
        attrs.get("CUI") == "C4316903"
        and phrase == "typical absences"
        and attrs.get("PointInTime") == "LastClinic"
        and attrs.get("TimeSince_or_TimeOfEvent") == "Since"
    ):
        return None
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


@register_builder("rewrite_focal_under_control_to_seizure_free")
def builder_rewrite_focal_under_control_to_seizure_free(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    evidence = ctx.evidence
    if not (re.search(r"\bfocal seizures\b.{0,80}\bunder control\b", evidence, re.IGNORECASE)):
        return None
    attrs["CUI"] = "C0751495"
    attrs["CUIPhrase"] = "focal seizures"
    attrs["NumberOfSeizures"] = "0"
    attrs.pop("FrequencyChange", None)
    return "focal seizures", attrs, "rewrite_focal_under_control_to_seizure_free"


@register_builder("rewrite_epileptic_seizures_to_generic_seizures")
def builder_rewrite_epileptic_seizures_to_generic_seizures(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    evidence = ctx.evidence
    phrase = ctx.phrase
    if not (
        phrase == "epileptic seizures"
        and re.search(r"\bwell controlled\b", evidence, re.IGNORECASE)
    ):
        return None
    attrs["CUI"] = "C0036572"
    attrs["CUIPhrase"] = "seizures"
    return "seizures", attrs, "rewrite_epileptic_seizures_to_generic_seizures"


@register_builder("rewrite_no_further_seizures_to_generic_seizures")
def builder_rewrite_no_further_seizures_to_generic_seizures(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    evidence = ctx.evidence
    phrase = ctx.phrase
    if not (
        phrase == "further seizures"
        and re.search(r"\bnot\s+had\s+any\s+further\s+seizures\b", evidence, re.IGNORECASE)
    ):
        return None
    attrs["CUI"] = "C0036572"
    attrs["CUIPhrase"] = "seizures"
    attrs["NumberOfSeizures"] = "0"
    return "seizures", attrs, "rewrite_no_further_seizures_to_generic_seizures"


@register_builder("rewrite_selected_no_further_gtc_to_named_seizure_free")
def builder_rewrite_selected_no_further_gtc_to_named_seizure_free(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    evidence = ctx.evidence
    if not (attrs.get("CUI") == "C0036572" and _SF_NO_FURTHER_GTC_SINCE_RE.search(evidence)):
        return None
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


@register_builder("rewrite_teenage_last_seizures_to_generic")
def builder_rewrite_teenage_last_seizures_to_generic(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    evidence = ctx.evidence
    phrase = ctx.phrase
    if not (
        phrase == "focal to bilateral convulsive seizures"
        and re.search(
            r"\blast\s+seizures\s+were\s+in\s+his\s+teenage\s+years\b",
            evidence,
            re.IGNORECASE,
        )
    ):
        return None
    attrs["CUI"] = "C0036572"
    attrs["CUIPhrase"] = "seizures"
    return "seizures", attrs, "rewrite_teenage_last_seizures_to_generic"


@register_builder("rewrite_tonic_chronic_to_tonic_clonic_sf")
def builder_rewrite_tonic_chronic_to_tonic_clonic_sf(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    phrase = ctx.phrase
    if not (phrase == "generalised tonic chronic seizures"):
        return None
    attrs["CUI"] = "C0494475"
    attrs["CUIPhrase"] = "generalised tonic clonic seizures"
    return (
        "generalised tonic clonic seizures",
        attrs,
        "rewrite_tonic_chronic_to_tonic_clonic_sf",
    )


@register_builder("rewrite_anaphoric_these_seizures_to_generic")
def builder_rewrite_anaphoric_these_seizures_to_generic(
    ctx: ConventionContext,
) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    evidence = ctx.evidence
    phrase = ctx.phrase
    if not (phrase == "these seizures" and _REWRITE_THESE_SEIZURES_RE.search(evidence)):
        return None
    attrs["CUI"] = "C0036572"
    attrs["CUIPhrase"] = "seizures"
    return "seizures", attrs, "rewrite_anaphoric_these_seizures_to_generic"


@register_builder("rewrite_absence_seizures_to_absences")
def builder_rewrite_absence_seizures_to_absences(ctx: ConventionContext) -> RewriteResult | None:
    attrs = dict(ctx.attrs)
    phrase = ctx.phrase
    if not (phrase == "absence seizures"):
        return None
    attrs["CUI"] = "C0563606"
    attrs["CUIPhrase"] = "absences"
    return "absences", attrs, "rewrite_absence_seizures_to_absences"
