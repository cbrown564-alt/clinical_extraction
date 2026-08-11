from __future__ import annotations

import re

from ._shared_tokens import GAP_WORDS_TOKEN
from .selected_evidence_text import (
    format_prediction_rate as _format_prediction_rate,
)


def cluster_label_from_selected_evidence(text: str) -> str | None:
    if "fortnight" in text and "cluster" in text:
        text_norm = re.sub(r"\bfortnights?\b", "2 week", text)
        fortnight_cluster = re.search(
            r"\bclusters?\b.{0,80}\b(?:on\s+)?(?:several|multiple|\d+)\s+"
            r"(?:evenings?|mornings?|days?)\s+(?:per|each)\s+(?:fortnight|2\s+week)\b",
            text_norm,
        ) or re.search(
            r"\b(?:several|multiple|\d+)\s+(?:evenings?|mornings?|days?)\s+"
            r"(?:per|each)\s+(?:fortnight|2\s+week)\b.{0,80}\bclusters?\b",
            text_norm,
        )
        if fortnight_cluster:
            per_m = re.search(
                r"\b(?P<per>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+(?:short-lived\s+)?"
                r"(?:spells?|seizures?|events?)\s+(?:per\s+cluster|with\s+brief\s+recovery)\b",
                text_norm,
            ) or re.search(
                r"\beach\s+cluster\s+involves\s+(?:roughly\s+|about\s+)?"
                r"(?P<per>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\b",
                text_norm,
            )
            if per_m:
                per_str = re.sub(r"\s*(?:-|–|—)\s*", " to ", per_m.group("per"))
            else:
                per_str = "multiple"
            return f"multiple cluster per 2 week, {per_str} per cluster"

    if re.search(
        r"\bclusters?\s+of\s+(?:jumps?|jerks?)\b.{0,40}\b(?:almost\s+)?daily\b",
        text,
    ):
        return "1 per day"
    if re.search(
        r"\bclusters?\s+of\s+(?:jumps?|jerks?)\b.{0,40}\balmost\s+1\s+per\s+day\b",
        text,
    ):
        return "1 per day"

    recurrence_cluster = re.search(
        r"\b(?:go|remain|stretches?)\b.{0,50}"
        r"\b(?:nearly|almost|about|around|up to\s+)?"
        r"(?P<interval>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?P<unit>day|week|month)s?\b.{0,80}"
        r"\b(?:when they recur|then)\b.{0,80}"
        r"\b(?P<per>\d+(?:\s*(?:to|-|–|—|and)\s*\d+)?)\b"
        r".{0,30}\b(?:one|1)\s+day\b",
        text,
    )
    if recurrence_cluster:
        per_cluster = re.sub(r"\s*(?:-|–|—|and)\s*", " to ", recurrence_cluster.group("per"))
        return (
            f"1 cluster per {recurrence_cluster.group('interval')} "
            f"{recurrence_cluster.group('unit')}, {per_cluster} per cluster"
        )
    recurrence_cluster_between = re.search(
        r"\b(?:go|remain|stretches?)\b.{0,50}"
        r"\b(?:nearly|almost|about|around|up to\s+)?"
        r"(?P<interval>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?P<unit>day|week|month)s?\b.{0,120}"
        r"\b(?:between|often between)\s+"
        r"(?P<per>\d+(?:\s*(?:to|-|–|—|and)\s*\d+)?)\b",
        text,
    )
    if recurrence_cluster_between:
        per_cluster = re.sub(
            r"\s*(?:-|–|—|and)\s*",
            " to ",
            recurrence_cluster_between.group("per"),
        )
        return (
            f"1 cluster per {recurrence_cluster_between.group('interval')} "
            f"{recurrence_cluster_between.group('unit')}, {per_cluster} per cluster"
        )

    seizure_free_cluster_day = re.search(
        r"\b(?:seizure-free|without\s+seizures?)\s+for\s+"
        r"(?P<interval>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:consecutive\s+)?(?P<unit>day|week|month)s?\b.{0,120}"
        r"\b(?:followed\s+by|then)\s+(?:a\s+)?day\b.{0,100}"
        r"\b(?:multiple|several|batches?|clusters?|clustering)\b.{0,80}"
        r"\b(?:typically\s+)?(?P<per>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\b",
        text,
    )
    if seizure_free_cluster_day:
        per_cluster = re.sub(
            r"\s*(?:-|–|—|and)\s*",
            " to ",
            seizure_free_cluster_day.group("per"),
        )
        return (
            f"1 cluster per {seizure_free_cluster_day.group('interval')} "
            f"{seizure_free_cluster_day.group('unit')}, {per_cluster} per cluster"
        )

    seizure_free_batch = re.search(
        r"\b(?:go|manage|remain)\b.{0,30}"
        r"(?P<interval>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?P<unit>day|week|month)s?\s+without\s+seizures?\b.{0,140}"
        r"\b(?:batches?|clusters?|clustering)\b.{0,80}?"
        r"\b(?:with\s+)?(?P<per>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\b"
        r".{0,40}\b(?:within\s+24\s+hours?|events?)\b",
        text,
    )
    if seizure_free_batch:
        per_cluster = re.sub(
            r"\s*(?:-|–|—|and)\s*",
            " to ",
            seizure_free_batch.group("per"),
        )
        return (
            f"1 cluster per {seizure_free_batch.group('interval')} "
            f"{seizure_free_batch.group('unit')}, {per_cluster} per cluster"
        )

    cluster_multiple_days = re.search(
        r"\b(?:past|last)\s+month\b.{0,120}\bclusters?\b.{0,80}"
        r"\b(?:on|over)\s+multiple\s+days?\b",
        text,
    )
    if cluster_multiple_days and _evidence_implies_multiple_per_cluster(text):
        return "multiple cluster per month, multiple per cluster"

    monthly_cluster = re.search(r"\bmonthly\s+clusters?\b", text)
    if monthly_cluster:
        monthly_per_cluster_match = re.search(
            r"\b(?P<count>\d+(?:\s*to\s*\d+)?)\s+"
            rf"(?={GAP_WORDS_TOKEN}"
            r"(?:seizure|absence|attack|convulsion|spasm|event|mal))",
            text[monthly_cluster.end() :],
        )
        if monthly_per_cluster_match:
            return f"1 cluster per month, {monthly_per_cluster_match.group('count')} per cluster"
        if _evidence_implies_multiple_per_cluster(text):
            return "1 cluster per month, multiple per cluster"

    monthly_burst = re.search(
        r"\b(?:clusters?|bursts?)\b.*\b(?:once\s+each|1\s+each|once\s+per|1\s+per)\s+month\b",
        text,
    )
    if monthly_burst and _evidence_implies_multiple_per_cluster(text):
        return "1 cluster per month, multiple per cluster"

    weekly_cluster = re.search(r"\bweekly\b.*\bclusters?\b", text)
    if weekly_cluster and _evidence_implies_multiple_per_cluster(text):
        return "1 cluster per week, multiple per cluster"
    cluster_weekly_per_cluster = re.search(
        r"\bclusters?\b.*\b(?:now\s+)?weekly\b.*?"
        r"\b(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:or\s+more\s+)?(?:events?|seizures?)?(?:\s+within\b.*)?"
        r"(?:per\s+cluster)?\b",
        text,
    )
    if cluster_weekly_per_cluster:
        return f"1 cluster per week, {cluster_weekly_per_cluster.group('count')} per cluster"
    weekly_cluster_count = re.search(
        r"\bweekly\b.*\bclusters?\b.*?"
        r"\b(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:or\s+more\s+)?(?:events?|seizures?)\b",
        text,
    )
    if weekly_cluster_count:
        return f"1 cluster per week, {weekly_cluster_count.group('count')} per cluster"
    weekly_per_cluster_reversed = re.search(
        r"\bweekly\b.{0,40}?\b(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+per\s+cluster\b",
        text,
    )
    if weekly_per_cluster_reversed:
        per_str = re.sub(
            r"\s*(?:-|–|—)\s*", " to ", weekly_per_cluster_reversed.group("count")
        )
        return f"1 cluster per week, {per_str} per cluster"

    cluster_days_month = re.search(
        r"\b(?:cluster\s+days?|clusters?)\s+"
        r"(?:(?P<count_word>twice)|(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?))\s+"
        r"this\s+month\b.*?"
        r"(?:sizes?\s+unrecorded|typically\s+(?P<per>\d+(?:\s*(?:to|-|–|—|or)\s*\d+)?)"
        r"(?:\s+or\s+more)?\s+(?:seizures?|events?)\s+in\s+24\s*h)",
        text,
    )
    if cluster_days_month:
        count_text = (
            "2" if cluster_days_month.group("count_word") else cluster_days_month.group("count")
        )
        per_cluster = cluster_days_month.group("per") or "multiple"
        return f"{count_text} cluster per month, {per_cluster} per cluster"

    cluster_days_month_reversed = re.search(
        r"\b(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+cluster\s+days?\s+"
        r"this\s+month\b.*?(?:sizes?\s+unrecorded|typically\s+"
        r"(?P<per>\d+(?:\s*(?:to|-|–|—|or)\s*\d+)?)"
        r"(?:\s+or\s+more)?\s+(?:seizures?|events?)\s+in\s+24\s*h)",
        text,
    )
    if cluster_days_month_reversed:
        per_cluster = cluster_days_month_reversed.group("per") or "multiple"
        return (
            f"{cluster_days_month_reversed.group('count')} cluster per month, "
            f"{per_cluster} per cluster"
        )

    cluster_days_month_simple = re.search(
        r"\b(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+cluster\s+days?\s+"
        r"this\s+month\b",
        text,
    )
    if cluster_days_month_simple:
        return f"{cluster_days_month_simple.group('count')} cluster per month, multiple per cluster"

    clusters_x_month = re.search(
        r"\bclusters?\s+(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s*×\s*/\s*month\b"
        r".*?(?P<per>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+events?\b",
        text,
    )
    if clusters_x_month:
        return (
            f"{clusters_x_month.group('count')} cluster per month, "
            f"{clusters_x_month.group('per')} per cluster"
        )

    quarterly_cluster = re.search(
        r"\bquarterly\s+clusters?\b.*?\b(?P<per>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:convulsions?|seizures?|events?)\s+per\s+episode\b",
        text,
    )
    if quarterly_cluster:
        return f"1 cluster per 3 month, {quarterly_cluster.group('per')} per cluster"

    burst_monthly = re.search(
        r"\b(?:bursts?|clusters?)\b.*\b(?:around\s+the\s+beginning\s+of\s+most|"
        r"roughly\s+(?:once|1)\s+a|(?:once|1)\s+a|each)\s+month\b",
        text,
    )
    if burst_monthly:
        return "1 cluster per month, multiple per cluster"

    grouped_weekly = re.search(
        r"\b(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:nights?|mornings?|evenings?)\s+per\s+week\b.*\b"
        r"(?:several|multiple|grouped|clusters?|bursts?)\b",
        text,
    )
    if grouped_weekly:
        return f"{grouped_weekly.group('count')} cluster per week, multiple per cluster"

    several_per_fortnight = re.search(
        r"\bclusters?\s+arise\s+on\s+several\s+(?:evenings?|mornings?|days?)\s+"
        r"per\s+fortnight\b.*?\b(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:spells?|seizures?|events?)\b",
        text,
    )
    if several_per_fortnight:
        return f"multiple cluster per 2 week, {several_per_fortnight.group('count')} per cluster"

    every_cluster = re.search(
        r"\b(?:clusters?|bursts?)\b.*\bevery\s+"
        r"(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?P<unit>day|week|month|year)s?\b",
        text,
    )
    if every_cluster:
        if _evidence_implies_multiple_per_cluster(text):
            return (
                f"1 cluster per {every_cluster.group('count')} "
                f"{every_cluster.group('unit')}, multiple per cluster"
            )
        return _format_prediction_rate(
            f"1 per {every_cluster.group('count')}",
            every_cluster.group("unit"),
        )

    cluster_days = re.search(
        r"\bclusters?\b.{0,60}\b(?:on\s+)?(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+days?\s+(?:each|per|this)\s+(?P<unit>day|week|month|year)\b",
        text,
    )
    if cluster_days:
        unit = cluster_days.group("unit")
        count = cluster_days.group("count")
        return f"{count} cluster per {unit}, multiple per cluster"

    clusters_x_standalone = re.search(
        r"\bclusters?\s+(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s*×\s*/\s*(?P<unit>day|week|month|year)\b",
        text,
    )
    if clusters_x_standalone:
        count_str = clusters_x_standalone.group("count")
        unit_str = clusters_x_standalone.group("unit")
        return f"{count_str} cluster per {unit_str}, multiple per cluster"

    ratio_match = re.search(
        r"\b(?P<count>\d+)\s+(?:[a-z-]+(?:\s+[a-z-]+)?\s+)?clusters?\s+"
        r"(?:in|over)\s+(?:the\s+past\s+)?(?P<period>\d+)\s+(?P<unit>day|week|month|year)s?\b",
        text,
    )
    ratio_match_reversed = re.search(
        r"\b(?:over|in|during)\s+(?:the\s+past\s+)?(?P<period>\d+)\s+"
        r"(?P<unit>day|week|month|year)s?\b.{0,40}?"
        r"\b(?:≈|~|about\s+|approximately\s+|around\s+)?(?P<count>\d+)\s+"
        r"(?:[a-z-]+(?:\s+[a-z-]+)?\s+)?clusters?\b",
        text,
    )
    if not ratio_match and ratio_match_reversed:
        ratio_match = ratio_match_reversed
    if ratio_match:
        count = int(ratio_match.group("count"))
        period = int(ratio_match.group("period"))
        unit = ratio_match.group("unit")

        tail = text[ratio_match.end() :]
        per_match = re.search(
            r"\b(?:each\s+(?:comprising|involving|having|with)?|per\s+cluster)\s+"
            r"(?:≈|~|about\s+|approximately\s+|around\s+)?(?P<per>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\b",
            tail,
        )
        if per_match:
            per_str = re.sub(r"\s*(?:-|–|—)\s*", " to ", per_match.group("per"))
        else:
            per_str = "multiple"

        if period % count == 0:
            new_period = period // count
            den = f"{new_period} " if new_period > 1 else ""
            return f"1 cluster per {den}{unit}, {per_str} per cluster"
        else:
            return f"{count} cluster per {period} {unit}, {per_str} per cluster"

    cluster_match = re.search(
        r"\b(?:≈|~|about\s+|approximately\s+|around\s+)?"
        r"(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+(?:[a-z-]+(?:\s+[a-z-]+)?\s+)?clusters?\s+"
        r"(?:(?:per|every)\s+(?:(?P<den>\d+)\s+)?(?P<unit>day|week|month|year)"
        r"|(?:this|past|last)\s+(?P<period>day|week|month|year|quarter))\b",
        text,
    )
    last_period_cluster = re.search(
        r"\b(?:this|past|last)\s+(?P<unit>day|week|month|year)\b.{0,40}?"
        r"\b(?:≈|~|about\s+|approximately\s+|around\s+)?(?P<count>\d+)\s+"
        r"(?:[a-z-]+(?:\s+[a-z-]+)?\s+)?clusters?\b",
        text,
    )
    if cluster_match:
        tail_start = cluster_match.end()
        denominator = cluster_match.group("den") or "1"
        unit = cluster_match.group("unit") or cluster_match.group("period")
        count = cluster_match.group("count")
    elif last_period_cluster:
        tail_start = last_period_cluster.end()
        denominator = "1"
        unit = last_period_cluster.group("unit")
        count = last_period_cluster.group("count")
    else:
        return None

    tail = text[tail_start:]
    per_cluster_match = re.search(
        r"\b(?:each|per\s+cluster|per\s+episode|cluster(?:s)?\s+(?:with|of|having))\s+"
        r"(?:≈|~|about\s+|approximately\s+|around\s+)?(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        rf"(?={GAP_WORDS_TOKEN}"
        r"(?:seizure|absence|attack|convulsion|spasm|event|episode|spell|mal))",
        tail,
    )
    if unit == "quarter":
        denominator = "3"
        unit = "month"
    den_text = f"{denominator} " if denominator != "1" else ""
    if not per_cluster_match:
        return f"{count} cluster per {den_text}{unit}, multiple per cluster"
    per_str = re.sub(r"\s*(?:-|–|—)\s*", " to ", per_cluster_match.group("count"))
    return f"{count} cluster per {den_text}{unit}, {per_str} per cluster"


def _evidence_implies_multiple_per_cluster(text: str) -> bool:
    return bool(
        re.search(
            r"\b(?:several|multiple|bursts?|flurries|episodes?\s+"
            r"(?:a\s+)?few\s+days|over\s+(?:several|multiple)\s+days|"
            r"lasting\s+\d+\s*(?:to|-|–|—)\s*\d+\s+days|"
            r"number\s+per\s+cluster\s+not\s+documented|"
            r"imprecise\s+number\s+of\s+events\s+per\s+burst)\b",
            text,
        )
    )
