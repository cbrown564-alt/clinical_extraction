#!/usr/bin/env python3
"""Build a gold-only Gan 2026 phrase-variant inventory from development rows.

Pairs each gold label with the dataset ``gold_reference`` field and assigns a
first-cut source-construction and transform class. Locked ``test`` rows are
never loaded. No model predictions.

Regenerate::

    python scripts/build_gan2026_gold_phrase_variant_inventory.py
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import boundary_band

REPO_ROOT = Path(__file__).resolve().parents[1]
DATE_STAMP = "20260813"
REPORT_DATE = "2026-08-13"

_NUMBER_WORDS = (
    "once|twice|thrice|one|two|three|four|five|six|seven|eight|nine|ten|"
    "eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
    "nineteen|twenty|thirty|couple|few"
)
_UNITS = r"day|days|night|nights|week|weeks|wk|wks|month|months|mo|year|years|yr|yrs"
_CADENCE_WORDS = (
    "daily|nightly|weekly|monthly|bimonthly|bi-monthly|fortnightly|"
    "quarterly|annually|yearly"
)
_SHORTHAND_RE = re.compile(
    r"(?:\b(?:sz|abs|tc|gtcs?|gtc|foc(?:al)?|sps|cps|myoclonic)\b.{0,12}"
    r"(?:[/x*×]|q\d))|"
    r"\bqhs\b|\bq\d|\bsz\s+[x*]|\babs\s+[x*]|"
    r"\bq(?:one|two|three|four|five|six|\d+)\s*[-–to]*\s*"
    r"(?:one|two|three|four|five|six|\d+)?\s*(?:d|wk|w|mo|h)\b|"
    r"\bseizure frequency\s+\d+\s*/\s*\d+\b",
    re.IGNORECASE,
)
_SLASH_RATE_RE = re.compile(
    rf"\bseizure frequency\s+(?:\d+|{_NUMBER_WORDS})\s*/\s*\d+\b|"
    rf"\b(?:\d+|{_NUMBER_WORDS})\s*/\s*(?:7|30|31)\b(?!/\d)",
    re.IGNORECASE,
)
_SUMMED_TYPES_RE = re.compile(
    rf"\b(?:\d+|{_NUMBER_WORDS})\s+\w[\w\s-]{{0,40}}?\s+and\s+"
    rf"(?:\d+|{_NUMBER_WORDS})\b",
    re.IGNORECASE,
)
_WINDOWED_COUNT_RE = re.compile(
    rf"\b(?:\d+|{_NUMBER_WORDS})\s+"
    r"[\w\s-]{0,60}?"
    r"(?:in (?:the )?(?:last|past)|over the past|so far this|this year|"
    r"documented (?:this|in)|yesterday|last night)\b",
    re.IGNORECASE,
)
_INTERVAL_RE = re.compile(
    r"\b(?:inter[-\s]?seizure interval|interval between (?:seizures|events))\b|"
    r"\bmedian\s+inter",
    re.IGNORECASE,
)
_ADJECTIVE_CADENCE_RE = re.compile(
    rf"\b(?:{_CADENCE_WORDS}|every (?:day|night|week|month|year))\b",
    re.IGNORECASE,
)
_THEME_TAG_RE = re.compile(
    r"\b(?:well[-\s]?controlled|sleep deprivation|daytime naps?|screen time|"
    r"caffeine|missed (?:asm )?doses?|tongue biting|incontinence|"
    r"startle[-\s]?induced|exercise[-\s]?induced|postpartum|"
    r"predominantly daytime|waxing and waning|fluctuates|"
    r"therapeutic levels|symptom-free intervals|"
    r"stable seizure control|seizure events (?:persist|continue)|"
    r"injury related|only with|rare brief|nocturnal predominance|"
    r"sleep onset|alcohol intake|stress-related|photosensitive|"
    r"flicker exposure|skipping meals|jet lag|"
    r"clustering followed by quiescence|late luteal|work days|"
    r"partial response|tolerability-limited|autonomic spells|"
    r"behavioral arrest|home video|not captured on eeg|"
    r"spells concerning|second half of the night|"
    r"semiology evolving|nocturnal hypermotor|"
    r"unclear direction)\b",
    re.IGNORECASE,
)
_DATE_RE = re.compile(
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|"
    r"\b\d{1,2}\s+"
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|"
    r"dec(?:ember)?)\s+\d{2,4}\b|"
    r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|"
    r"dec(?:ember)?)\s+\d{1,2},?\s+\d{2,4}\b",
    re.IGNORECASE,
)
_DIARY_RE = re.compile(
    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s*x\s*\d+\b|"
    r"\bseizure:\s*\d{4}:",
    re.IGNORECASE,
)
_EVERY_N_RE = re.compile(
    rf"\bevery\s+(?:other|couple(?:\s+of)?|\d+|{_NUMBER_WORDS})\s+(?:{_UNITS})\b",
    re.IGNORECASE,
)
_RANGE_RE = re.compile(
    rf"\b(?:\d+|{_NUMBER_WORDS})\s*(?:to|-|–|—|or)\s*(?:\d+|{_NUMBER_WORDS})\b",
    re.IGNORECASE,
)
_COUNT_PER_RE = re.compile(
    rf"\b(?:\d+|{_NUMBER_WORDS})\s+per\s+"
    rf"(?:(?:\d+|{_NUMBER_WORDS})\s+)?(?:{_UNITS})\b|"
    rf"\b(?:once|twice|thrice)\s+(?:per|a|an|/)\s+(?:{_UNITS})\b|"
    rf"\b(?:\d+|{_NUMBER_WORDS})\s+"
    rf"(?:[\w-]+\s+){{0,4}}"
    rf"(?:seizures?|events?|episodes?|spells?|absences?|attacks?|times?)\s+"
    rf"(?:per|a|an|/|each)\s+(?:\d+\s+)?(?:{_UNITS}|month|day|week|year)\b",
    re.IGNORECASE,
)
_MONTH_NAME = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|"
    r"dec(?:ember)?)"
)
_MONTH_BY_MONTH_RE = re.compile(
    rf"\b(?:in|so far in)\s+{_MONTH_NAME}\b.{{0,80}}\b(?:in|and)\s+{_MONTH_NAME}\b|"
    rf"\b{_MONTH_NAME}\b.{{0,40}}\b(?:in|and)\s+{_MONTH_NAME}\b.{{0,20}}"
    rf"\b(?:in|and)\s+{_MONTH_NAME}\b",
    re.IGNORECASE | re.DOTALL,
)
_DATED_EVENT_SEQUENCE_RE = re.compile(
    r"\b(?:first|initial)\s+(?:seizure|event)\b|"
    r"\bfirst experienced a seizure\b",
    re.IGNORECASE,
)
_SECOND_EVENT_RE = re.compile(
    r"\b(?:second|next|third)\s+(?:seizure|event)\b|"
    r"\bnext seizure came\b|"
    r"\bsecond and third event\b",
    re.IGNORECASE,
)
_POST_CHANGE_BURST_RE = re.compile(
    rf"\b(?:withdrew from|stopped on|discontinued)\b.{{0,120}}"
    rf"\b(?:had|experienced)\s+(?:\d+|{_NUMBER_WORDS}|multiple)\s+seizures?\b",
    re.IGNORECASE | re.DOTALL,
)
_LAST_THEN_QUIET_RE = re.compile(
    r"\blast (?:reported |such )?(?:event|episode|seizure)\b.{0,80}"
    r"\b(?:stable|well|no further|remained|since then|has been)\b",
    re.IGNORECASE | re.DOTALL,
)
_QUIET_THEN_BREAKTHROUGH_RE = re.compile(
    r"\bseizure[-\s]?free for\b.{0,40}\buntil\b",
    re.IGNORECASE,
)
_CLUSTER_PARAPHRASE_RE = re.compile(
    r"\b(?:batches|day of clustering|day with multiple events|"
    r"followed by a day with multiple|in a brief series|"
    r"run of (?:\d+|{_NUMBER_WORDS}) seizures?)\b",
    re.IGNORECASE,
)
_ELECTROGRAPHIC_RE = re.compile(
    r"\belectrographic seizures\b|\b~\s*\d+\s*/\s*h\b|\b\d+\s*/\s*h\b",
    re.IGNORECASE,
)
_COUPLE_WINDOW_RE = re.compile(
    rf"\ba couple of\b.{{0,40}}\b(?:last|past|this)\s+(?:{_UNITS})\b",
    re.IGNORECASE,
)
_LAST_MAJOR_PLUS_SINCE_RE = re.compile(
    r"\blast tonic[-\s]?clonic\b.{0,60}\bsince then\b|"
    r"\bno further tonic[-\s]?clonic\b.{0,60}\balthough\b",
    re.IGNORECASE,
)
_HEDGE_RE = re.compile(
    r"\b(?:up to|less than|at most|approximately|roughly|about|around|nearly|"
    r"almost|upto|≤|>=|≤|≥)\b",
    re.IGNORECASE,
)
_VAGUE_RE = re.compile(
    r"\b(?:several|multiple|frequent|many|numerous|recurrent|occasional|"
    r"sporadic|variable|fluctuating)\b",
    re.IGNORECASE,
)
_SITUATIONAL_RE = re.compile(
    r"\b(?:on awakening|after (?:tired|lack of sleep|sleep|illness)|"
    r"during (?:illness|intercurrent|sleep|naps?|certain)|"
    r"when tired|after tired|triggered|precipitated)\b",
    re.IGNORECASE,
)
_SOFT_RE = re.compile(
    r"\b(?:suspected|not confirmed|unconfirmed|possible|under review|"
    r"may represent|uncertain|unclear)\b",
    re.IGNORECASE,
)
_QUALITATIVE_FREE_RE = re.compile(
    r"\b(?:complete control|durable (?:seizure )?control|"
    r"sustained control|event-free|no recurrence|no seizure recurrence|"
    r"remains seizure freedom|seizure freedom|"
    r"interval history negative|no seizures documented|"
    r"seizure-free on current|non-epileptic seizures only)\b",
    re.IGNORECASE,
)
_FREE_DURATION_RE = re.compile(
    r"\b(?:seizure[-\s]?free|no (?:seizures?|events?|recurrence)|"
    r"event-free|no further (?:seizures?|events?))\b",
    re.IGNORECASE,
)
_CLUSTER_RE = re.compile(r"\bclusters?\b", re.IGNORECASE)
_WORD_NUMBER_RE = re.compile(rf"\b(?:{_NUMBER_WORDS})\b", re.IGNORECASE)
_CADENCE_ONLY_RE = re.compile(rf"^(?:{_CADENCE_WORDS})$", re.IGNORECASE)
_PROMPT_RE = re.compile(r"^create a reasonable\b", re.IGNORECASE)

CONSTRUCTION_ORDER = (
    "admin_or_generation_prompt",
    "clinical_shorthand",
    "slash_or_fraction_rate",
    "diary_or_calendar_log",
    "month_by_month_count",
    "cluster_structure",
    "cluster_paraphrase",
    "electrographic_rate",
    "post_change_burst",
    "dated_event_sequence",
    "last_event_then_quiet",
    "quiet_then_breakthrough",
    "last_major_plus_since",
    "couple_in_window",
    "summed_type_counts_in_window",
    "count_in_named_window",
    "interseizure_interval",
    "seizure_free_since_date",
    "last_event_date",
    "seizure_free_duration_or_interval",
    "qualitative_control",
    "situational_or_triggered",
    "soft_or_unconfirmed",
    "non_rate_theme_tag",
    "cadence_token",
    "adjective_cadence",
    "every_n_interval",
    "range_or_bound",
    "count_per_period",
    "vague_multiple",
    "non_rate_unknown_statement",
    "other_paraphrase",
)

CONSTRUCTION_DEFINITIONS = {
    "admin_or_generation_prompt": (
        "The official reference is a generation instruction or administrative "
        "task, not a frequency statement from the letter."
    ),
    "clinical_shorthand": (
        "Compact chart notation: seizure-type abbreviation plus count/unit "
        "(sz X1/d, abs *monthly) or q-interval notation (qhs, q2wk, qtwo-threewk)."
    ),
    "slash_or_fraction_rate": (
        "A compact fraction such as 6/7 or eight/30, usually meaning N days "
        "in a week or N events in a 30-day month."
    ),
    "diary_or_calendar_log": (
        "A month-by-month or dated count list that must be aggregated into "
        "one windowed rate."
    ),
    "month_by_month_count": (
        "Separate month names each with a count, which gold sums into one "
        "window: 'In Oct … 2 … In Nov … 5' → 8 per 2 month."
    ),
    "cluster_structure": (
        "The source describes clusters. Gold usually needs the two-part "
        "N cluster per T, M per cluster grammar."
    ),
    "cluster_paraphrase": (
        "Cluster meaning without the word cluster: batches, a day of multiple "
        "events, or a run of seizures after a quiet interval."
    ),
    "electrographic_rate": (
        "EEG or device hourly burden, usually golded as multiple per day."
    ),
    "post_change_burst": (
        "A counted burst at a medication change, then a quiet interval. Gold "
        "often uses the burst count over a later window."
    ),
    "dated_event_sequence": (
        "A first event on one date and a later event on another. Gold is the "
        "count over the span between them."
    ),
    "last_event_then_quiet": (
        "A last-event date plus a statement that the patient has been stable "
        "since. Gold is often 1 per month or 1 per N month."
    ),
    "quiet_then_breakthrough": (
        "A seizure-free interval ended by a later event: 'seizure-free for 4 "
        "months until … two Thursdays ago'."
    ),
    "last_major_plus_since": (
        "A last major seizure date plus residual smaller events since then."
    ),
    "couple_in_window": (
        "'A couple of' events in a named window, usually golded as multiple."
    ),
    "summed_type_counts_in_window": (
        "Two or more typed counts in one window that gold adds together: "
        "'one absence and four petit mal in last month' → 5 per month."
    ),
    "count_in_named_window": (
        "A count over a named observation window: N events in the last T, "
        "so far this year, yesterday. Gold may keep or recode the window."
    ),
    "interseizure_interval": (
        "A typical gap between events (median inter-seizure interval ≈ five "
        "months) inverted to 1 per N unit."
    ),
    "seizure_free_since_date": (
        "A seizure-free claim anchored to a calendar date. Gold is a duration "
        "label that requires elapsed-time arithmetic against the clinic date."
    ),
    "last_event_date": (
        "A last-seizure or last-event date without an explicit free-interval "
        "phrase. Gold still renders a seizure-free duration."
    ),
    "seizure_free_duration_or_interval": (
        "A quiet interval stated as a duration or as silence since the last "
        "visit, without a calendar date in the reference."
    ),
    "qualitative_control": (
        "Control or remission language with no countable rate: complete "
        "control, event-free, no recurrence, durable control."
    ),
    "situational_or_triggered": (
        "Events described only in relation to a trigger or setting "
        "(on awakening, during illness, after poor sleep)."
    ),
    "soft_or_unconfirmed": (
        "The reference marks the events as suspected, unconfirmed, or under "
        "review rather than stating a committed rate."
    ),
    "non_rate_theme_tag": (
        "The official reference names a trigger, setting, or quality "
        "(sleep deprivation, caffeine, well-controlled) that is not itself a "
        "rate. Gold is still a specific rate; the justifying count is elsewhere "
        "in the letter."
    ),
    "cadence_token": (
        "The official reference is a single cadence word such as daily, "
        "weekly, monthly, bimonthly, or quarterly. The letter phrasing is "
        "often longer and more specific."
    ),
    "adjective_cadence": (
        "A cadence adjective inside a longer phrase: yearly seizures, "
        "focal seizure monthly, events occurring every night."
    ),
    "every_n_interval": (
        "An every-N construction: every 3 months, every other day, every "
        "couple of months. Gold inverts this to 1 per N unit."
    ),
    "range_or_bound": (
        "A numeric or verbal range, or an upper bound (1 to 2, 3 or 4, up to "
        "4, ≤ once)."
    ),
    "count_per_period": (
        "An explicit count and period: once a week, 2 per month, three times "
        "a day."
    ),
    "vague_multiple": (
        "Several / multiple / frequent / many without a specific integer."
    ),
    "non_rate_unknown_statement": (
        "Gold is unknown. The official reference is a clinical statement that "
        "does not express a countable current rate (improvement, injury, EEG "
        "finding, unsure of last date)."
    ),
    "other_paraphrase": (
        "Residual paraphrases that do not match a more specific construction."
    ),
}


def _cluster_template(label: str) -> str:
    """Collapse cluster gold into unit x per-cluster-burden templates.

    Digit counts, 1-vs-N periods, period ranges, and cluster-count ranges
    are dropped. ``N cluster per 3 to 4 week, 2 to 4 per cluster`` and
    ``1 cluster per week, 4 per cluster`` therefore share a template.
    """
    text = label.lower()
    if re.search(r"\bdays?\b", text):
        unit = "day"
    elif re.search(r"\bweeks?\b", text):
        unit = "week"
    else:
        unit = "month"
    if re.search(r"\bmultiple per cluster\b", text):
        burden = "multiple per cluster"
    elif re.search(r"\bto\b.+\bper cluster\b", text):
        burden = "range per cluster"
    else:
        burden = "N per cluster"
    return f"cluster per {unit}, {burden}"


def _label_template(label: str) -> str:
    text = label.lower().strip()
    if "cluster" in text and not text.startswith("unknown"):
        return _cluster_template(text)
    return re.sub(r"\b\d+(?:\.\d+)?\b", "N", text)


def _gan_bucket(kind: str, label: str) -> str:
    text = label.lower().strip()
    if kind == "frequency" and "cluster" in text:
        return "cluster_burden"
    if kind == "frequency" and " to " in text:
        return "range_rate"
    if kind == "frequency" and re.search(r"\bmultiple\b", text):
        return "multiple_word_frequency"
    if kind == "frequency":
        return "ordinary_point_rate"
    if kind == "seizure_free":
        return "seizure_free"
    if kind == "unknown":
        return "unknown_sentinel"
    if kind == "no_reference":
        return "no_reference_sentinel"
    if kind == "unresolved_multiple":
        return "unresolved_multiple"
    return "other"


def _reference_status(reference: str, note_text: str) -> str:
    if reference in note_text:
        return "verbatim_in_note"
    if reference.lower() in note_text.lower():
        return "casefold_in_note"
    collapsed = re.sub(r"\s+", " ", reference).strip()
    collapsed_note = re.sub(r"\s+", " ", note_text)
    if collapsed and collapsed in collapsed_note:
        return "whitespace_normalized_in_note"
    if collapsed.lower() in collapsed_note.lower():
        return "whitespace_casefold_in_note"
    return "not_in_note"


def _classify_construction(reference: str, gold_label: str) -> str:
    ref = reference.strip()
    low = ref.lower()
    gold_low = gold_label.lower()
    sentinels = {"unknown", "no seizure frequency reference"}
    gold_is_rate = gold_low not in sentinels and not gold_low.startswith("seizure free")
    gold_is_free = gold_low.startswith("seizure free")
    gold_is_unknown = gold_low == "unknown" or gold_low.startswith("unknown,")

    if _PROMPT_RE.search(ref) or gold_low == "no seizure frequency reference":
        return "admin_or_generation_prompt"
    if _SHORTHAND_RE.search(ref):
        return "clinical_shorthand"
    if _SLASH_RATE_RE.search(ref):
        return "slash_or_fraction_rate"
    if _DIARY_RE.search(ref):
        return "diary_or_calendar_log"
    if _MONTH_BY_MONTH_RE.search(ref):
        return "month_by_month_count"
    if _CLUSTER_RE.search(ref):
        return "cluster_structure"
    if _CLUSTER_PARAPHRASE_RE.search(ref):
        return "cluster_paraphrase"
    if _ELECTROGRAPHIC_RE.search(ref):
        return "electrographic_rate"
    if _POST_CHANGE_BURST_RE.search(ref):
        return "post_change_burst"
    if _DATED_EVENT_SEQUENCE_RE.search(ref) and _SECOND_EVENT_RE.search(ref):
        return "dated_event_sequence"
    if _LAST_THEN_QUIET_RE.search(ref):
        return "last_event_then_quiet"
    if _QUIET_THEN_BREAKTHROUGH_RE.search(ref):
        return "quiet_then_breakthrough"
    if _LAST_MAJOR_PLUS_SINCE_RE.search(ref):
        return "last_major_plus_since"
    if _COUPLE_WINDOW_RE.search(ref):
        return "couple_in_window"
    if _SUMMED_TYPES_RE.search(ref) and re.search(r"\b(?:last|past|month|week|year)\b", low):
        return "summed_type_counts_in_window"
    if _INTERVAL_RE.search(ref):
        return "interseizure_interval"
    if _WINDOWED_COUNT_RE.search(ref) and gold_is_rate:
        return "count_in_named_window"
    if gold_is_free and _DATE_RE.search(ref) and re.search(r"\blast (?:seizure|event)\b", low):
        return "last_event_date"
    if _FREE_DURATION_RE.search(ref) and _DATE_RE.search(ref):
        return "seizure_free_since_date"
    if gold_is_free and _DATE_RE.search(ref):
        if re.search(r"\blast\b", low):
            return "last_event_date"
        return "seizure_free_since_date"
    if gold_is_free and re.search(r"\bfree of seizures\b|\blast seizure\b", low):
        if _DATE_RE.search(ref):
            return "last_event_date"
        return "seizure_free_duration_or_interval"
    if _QUALITATIVE_FREE_RE.search(ref) and not re.search(r"\d", ref):
        return "qualitative_control"
    if gold_is_free and _FREE_DURATION_RE.search(ref):
        return "seizure_free_duration_or_interval"
    if gold_is_free and not re.search(r"\d", ref):
        return "qualitative_control"
    if gold_is_unknown and _SITUATIONAL_RE.search(ref):
        return "situational_or_triggered"
    if _SOFT_RE.search(ref) and (gold_is_unknown or gold_low == "no seizure frequency reference"):
        return "soft_or_unconfirmed"
    theme_only = gold_is_rate and _THEME_TAG_RE.search(ref) and not re.search(r"\d", ref)
    if theme_only and not _COUNT_PER_RE.search(ref):
        return "non_rate_theme_tag"
    if _CADENCE_ONLY_RE.match(ref) or low in {
        "every day",
        "every night",
        "once daily",
        "once weekly",
        "once monthly",
    }:
        return "cadence_token"
    if _ADJECTIVE_CADENCE_RE.search(ref) and gold_is_rate:
        return "adjective_cadence"
    if _EVERY_N_RE.search(ref):
        return "every_n_interval"
    if _RANGE_RE.search(ref) or _HEDGE_RE.search(ref):
        return "range_or_bound"
    if _COUNT_PER_RE.search(ref):
        return "count_per_period"
    if _VAGUE_RE.search(ref) and not re.search(r"\d", ref):
        return "vague_multiple"
    if gold_is_unknown:
        return "non_rate_unknown_statement"
    return "other_paraphrase"


def _classify_transform(
    *,
    gold_label: str,
    reference: str,
    construction: str,
    reference_status: str,
) -> str:
    gold_low = gold_label.lower()
    ref_low = reference.lower()

    if gold_low in ref_low.replace("-", " "):
        return "identity_or_near_copy"
    if construction == "admin_or_generation_prompt":
        return "assert_no_reference"
    if construction == "diary_or_calendar_log":
        return "diary_window_aggregation"
    if construction == "month_by_month_count":
        return "diary_window_aggregation"
    if construction in {"cluster_structure", "cluster_paraphrase"}:
        return "cluster_two_part_render"
    if construction == "electrographic_rate":
        return "vague_to_multiple_sentinel"
    if construction == "post_change_burst":
        return "burst_then_quiet_to_rate"
    if construction == "dated_event_sequence":
        return "dated_sequence_to_rate"
    if construction == "last_event_then_quiet":
        return "last_event_to_rate"
    if construction == "quiet_then_breakthrough":
        return "quiet_interval_as_denominator"
    if construction == "last_major_plus_since":
        return "residual_events_since_major"
    if construction == "couple_in_window":
        return "vague_to_multiple_sentinel"
    if construction == "seizure_free_since_date":
        return "date_elapsed_arithmetic"
    if construction == "qualitative_control":
        return "qualitative_to_free_sentinel"
    if construction == "situational_or_triggered" or (
        construction == "soft_or_unconfirmed" and gold_low == "unknown"
    ):
        return "abstain_to_unknown"
    if gold_low == "unknown":
        return "abstain_to_unknown"
    if construction == "every_n_interval":
        return "interval_inversion"
    if construction == "cadence_token":
        return "cadence_expansion"
    if construction == "clinical_shorthand":
        return "shorthand_expansion"
    if construction == "slash_or_fraction_rate":
        return "fraction_to_rate"
    if construction == "summed_type_counts_in_window":
        return "sum_typed_counts"
    if construction == "count_in_named_window":
        return "windowed_count_to_rate"
    if construction == "interseizure_interval":
        return "interval_inversion"
    if construction == "last_event_date":
        return "date_elapsed_arithmetic"
    if construction == "non_rate_theme_tag":
        return "theme_tag_not_the_rate"
    if construction == "adjective_cadence":
        return "cadence_expansion"
    if construction == "non_rate_unknown_statement":
        return "abstain_to_unknown"
    if _HEDGE_RE.search(reference) and gold_low[:1].isdigit():
        return "hedge_or_bound_dropped"
    if "multiple" in gold_low and _VAGUE_RE.search(reference):
        return "vague_to_multiple_sentinel"
    if construction == "seizure_free_duration_or_interval":
        return "duration_normalization"
    if reference_status == "not_in_note" and _CADENCE_ONLY_RE.match(reference.strip()):
        return "compressed_token_to_specific_rate"
    if _WORD_NUMBER_RE.search(reference) and re.search(r"\d", gold_label):
        return "word_number_to_digit"
    if construction == "count_per_period" or construction == "range_or_bound":
        return "rate_dialect_normalization"
    return "other_semantic_map"


_STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "in",
    "on",
    "for",
    "with",
    "has",
    "had",
    "have",
    "been",
    "was",
    "were",
    "this",
    "that",
    "from",
    "after",
    "before",
    "she",
    "he",
    "her",
    "his",
    "they",
    "their",
    "but",
}
_FREQ_HINT_RE = re.compile(
    r"seizure|cluster|per |daily|weekly|monthly|nightly|bimonth|quarter|"
    r"seizure-free|seizure free|frequency|diary|interval|yesterday|"
    r"awakening|every |batch|recurrence|event-free",
    re.IGNORECASE,
)


def _content_tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if token not in _STOPWORDS and len(token) > 1
    }


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [part.strip() for part in parts if part.strip()]


def _usable_letter_sentence(sent: str) -> bool:
    compact = sent.strip()
    if len(compact) < 24:
        return False
    if re.fullmatch(r"[\d\s/-]+", compact):
        return False
    if re.search(
        r"\b(?:clinic date|sent:|hospital no|nhs no\.?|dob:)\b",
        compact,
        re.I,
    ):
        return False
    if re.match(r"^\d{6,}$", compact):
        return False
    if re.search(
        r"\b(?:flat|close|road|street|lane|hospital|denmark hill)\b",
        compact,
        re.I,
    ) and not _FREQ_HINT_RE.search(compact):
        return False
    return True


def _find_span(note: str, needle: str) -> str | None:
    if not needle:
        return None
    idx = note.find(needle)
    if idx >= 0:
        return note[idx : idx + len(needle)]
    idx = note.lower().find(needle.lower())
    if idx >= 0:
        return note[idx : idx + len(needle)]
    collapsed_note = re.sub(r"\s+", " ", note)
    collapsed_needle = re.sub(r"\s+", " ", needle).strip()
    idx = collapsed_note.lower().find(collapsed_needle.lower())
    if idx >= 0:
        return collapsed_note[idx : idx + len(collapsed_needle)]
    return None


def recover_letter_span(
    note_text: str,
    reference: str,
    gold_label: str,
) -> tuple[str, str]:
    """Return (span, recovery_method) from the letter. Never uses test rows."""
    in_letter = _find_span(note_text, reference)
    if in_letter:
        return in_letter, "official_reference_in_letter"

    if _PROMPT_RE.search(reference) or gold_label == "no seizure frequency reference":
        return "", "admin_or_no_frequency_letter"

    for length in (80, 48, 28):
        head = reference[:length].strip()
        if len(head) < 20:
            continue
        found = _find_span(note_text, head)
        if found:
            idx = note_text.lower().find(head.lower())
            end = min(len(note_text), idx + max(len(reference), 200))
            window = re.sub(r"\s+", " ", note_text[idx:end]).strip()
            return window[:400], "reference_prefix_in_letter"

    ref_tokens = _content_tokens(reference)
    gold_nums = set(re.findall(r"\d+", gold_label))
    cadence = bool(_CADENCE_ONLY_RE.match(reference.strip()))
    best: tuple[int, str] | None = None
    for sent in _sentences(note_text):
        if not _usable_letter_sentence(sent):
            continue
        sent_tokens = _content_tokens(sent)
        overlap = len(ref_tokens & sent_tokens)
        num_hit = sum(1 for number in gold_nums if number in sent)
        freq = 1 if _FREQ_HINT_RE.search(sent) else 0
        if freq == 0 and overlap < 3 and num_hit == 0:
            continue
        score = overlap * 2 + num_hit * 3 + freq * 2
        if re.search(r"\b\d+\s*mg\b|\btwice daily\b|\bb\.d\.", sent, re.I):
            score -= 8
            continue
        token = reference.strip().lower()
        if cadence and token in {"monthly", "bimonthly", "quarterly"}:
            if re.search(r"\b(?:month|week)\b", sent, re.I) or _EVERY_N_RE.search(sent):
                score += 6
        elif cadence and token == "weekly" and re.search(r"\bweek", sent, re.I):
            score += 6
        elif cadence and token in {"daily", "nightly", "every day", "every night"}:
            if re.search(r"\b(?:day|night|evening)\b", sent, re.I):
                score += 6
        elif cadence and (_ADJECTIVE_CADENCE_RE.search(sent) or _EVERY_N_RE.search(sent)):
            score += 4
        if gold_label.lower().startswith("seizure free") and _FREE_DURATION_RE.search(
            sent
        ):
            score += 4
        if "cluster" in gold_label.lower() and (
            _CLUSTER_RE.search(sent) or _CLUSTER_PARAPHRASE_RE.search(sent)
        ):
            score += 4
        if score > 0 and (best is None or score > best[0]):
            best = (score, sent)

    if best is None:
        return "", "no_span_recovered"
    span = re.sub(r"\s+", " ", best[1]).strip()[:400]
    if best[0] >= 5:
        return span, "scored_frequency_sentence"
    return span, "weak_frequency_sentence"


def _flags(reference: str, gold_label: str, note_text: str) -> dict[str, bool]:
    ref = reference
    return {
        "has_digit": bool(re.search(r"\d", ref)),
        "has_word_number": bool(_WORD_NUMBER_RE.search(ref)),
        "has_hedge": bool(_HEDGE_RE.search(ref)),
        "has_date": bool(_DATE_RE.search(ref)),
        "has_cluster_word": bool(_CLUSTER_RE.search(ref) or "cluster" in gold_label.lower()),
        "has_competing_rate_hint": bool(
            re.search(
                r"\bbut\b|\bhowever\b|\balthough\b|\bpreviously\b|\bhistorically\b",
                ref,
                re.I,
            )
        ),
        "gold_label_in_reference": gold_label.lower() in ref.lower(),
        "gold_label_in_note": gold_label.lower() in note_text.lower(),
    }


def _row_payload(record: Any, split: str) -> dict[str, Any]:
    reference = (record.gold_reference or "").strip()
    status = _reference_status(reference, record.note_text)
    recovered, recovery_method = recover_letter_span(
        record.note_text,
        reference,
        record.gold_label,
    )
    official_construction = _classify_construction(reference, record.gold_label)
    evidence_for_class = recovered if recovered else reference
    construction = _classify_construction(evidence_for_class, record.gold_label)
    transform = _classify_transform(
        gold_label=record.gold_label,
        reference=evidence_for_class,
        construction=construction,
        reference_status=status,
    )
    kind = str(record.gold_label_kind)
    return {
        "source_row_index": record.source_row_index,
        "split": split,
        "gold_label": record.gold_label,
        "gold_reference": reference,
        "recovered_letter_span": recovered,
        "span_recovery_method": recovery_method,
        "gold_label_kind": kind,
        "gold_bucket": _gan_bucket(kind, record.gold_label),
        "gold_template": _label_template(record.gold_label),
        "gold_monthly_frequency": record.gold_monthly_frequency,
        "boundary_band": boundary_band(record.gold_monthly_frequency),
        "reference_status": status,
        "source_construction": construction,
        "official_reference_construction": official_construction,
        "transform": transform,
        "flags": _flags(reference, record.gold_label, record.note_text),
        "row_ok": record.row_ok,
        "quotes_ok_all_categories": record.quotes_ok_all_categories,
    }


def _group_examples(
    rows: list[dict[str, Any]],
    key: str,
    limit: int = 6,
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for row in rows:
        value = row[key]
        pair = (row["gold_label"], row["gold_reference"].lower())
        if pair in seen[value]:
            continue
        if len(grouped[value]) >= limit:
            continue
        seen[value].add(pair)
        grouped[value].append(
            {
                "source_row_index": row["source_row_index"],
                "split": row["split"],
                "gold_label": row["gold_label"],
                "gold_reference": row["gold_reference"],
                "recovered_letter_span": row["recovered_letter_span"],
                "reference_status": row["reference_status"],
            }
        )
    return dict(grouped)


def build_inventory() -> dict[str, Any]:
    split_rows: dict[str, list[dict[str, Any]]] = {}
    for split in ("train", "validation"):
        loaded = load_records_for_split(split)
        split_rows[split] = [_row_payload(record, split) for record in loaded]
    rows = split_rows["train"] + split_rows["validation"]

    label_c = Counter(row["gold_label"] for row in rows)
    template_c = Counter(row["gold_template"] for row in rows)
    ref_c = Counter(row["gold_reference"] for row in rows)
    construction_c = Counter(row["source_construction"] for row in rows)
    transform_c = Counter(row["transform"] for row in rows)
    status_c = Counter(row["reference_status"] for row in rows)
    recovery_c = Counter(row["span_recovery_method"] for row in rows)
    bucket_c = Counter(row["gold_bucket"] for row in rows)

    refs_by_label: dict[str, list[str]] = defaultdict(list)
    seen_ref: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        key = row["gold_reference"].lower()
        if key in seen_ref[row["gold_label"]]:
            continue
        seen_ref[row["gold_label"]].add(key)
        refs_by_label[row["gold_label"]].append(row["gold_reference"])

    label_index = [
        {
            "gold_label": label,
            "n_rows": label_c[label],
            "n_distinct_references": len(refs_by_label[label]),
            "template": _label_template(label),
            "distinct_references": refs_by_label[label],
        }
        for label, _n in label_c.most_common()
    ]

    template_index = []
    labels_by_template: dict[str, list[str]] = defaultdict(list)
    for label, _n in label_c.most_common():
        labels_by_template[_label_template(label)].append(label)
    for template, n in template_c.most_common():
        template_index.append(
            {
                "template": template,
                "n_rows": n,
                "n_distinct_labels": len(labels_by_template[template]),
                "labels": labels_by_template[template],
            }
        )

    return {
        "schema_version": "gan2026_gold_phrase_variant_inventory.v1",
        "date": REPORT_DATE,
        "claim_boundary": {
            "splits": ["train", "validation"],
            "excluded_split": "test",
            "row_inspection": "development only; locked test rows were not loaded",
            "predictions": "none; gold label and gold_reference only",
            "reference_field": (
                "gold_reference is the dataset reference field. It is a verbatim "
                "letter span on most rows, but it can also be a compressed "
                "annotation token, a paraphrase, or a generation prompt."
            ),
            "taxonomy": (
                "source_construction is assigned from the recovered letter "
                "span when one exists, otherwise from gold_reference"
            ),
        },
        "summary": {
            "n_rows": len(rows),
            "n_train": len(split_rows["train"]),
            "n_validation": len(split_rows["validation"]),
            "n_unique_labels": len(label_c),
            "n_singleton_labels": sum(1 for n in label_c.values() if n == 1),
            "n_unique_references": len(ref_c),
            "n_unique_templates": len(template_c),
            "n_gold_label_substring_of_reference": sum(
                1 for row in rows if row["flags"]["gold_label_in_reference"]
            ),
            "n_gold_label_substring_of_note": sum(
                1 for row in rows if row["flags"]["gold_label_in_note"]
            ),
            "reference_status_counts": dict(status_c),
            "span_recovery_method_counts": dict(recovery_c),
            "n_other_paraphrase": construction_c.get("other_paraphrase", 0),
            "other_paraphrase_share": round(
                construction_c.get("other_paraphrase", 0) / max(len(rows), 1),
                4,
            ),
            "construction_counts": dict(construction_c),
            "transform_counts": dict(transform_c),
            "bucket_counts": dict(bucket_c),
        },
        "construction_definitions": CONSTRUCTION_DEFINITIONS,
        "construction_order": list(CONSTRUCTION_ORDER),
        "construction_examples": _group_examples(rows, "source_construction"),
        "transform_examples": _group_examples(rows, "transform"),
        "templates": template_index,
        "label_index": label_index,
        "rows": rows,
    }


def _md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def write_catalog_markdown(inventory: dict[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 gold phrase-variant catalog",
        "",
        f"Date: {REPORT_DATE}  ",
        "Status: generated development catalog; first draft  ",
        "Parent: [phrase-variant argument](gan_gold_phrase_variants_2026-08-13.md)  ",
        f"Artifact: [`experiments/gan2026_gold_phrase_variant_inventory_{DATE_STAMP}.json`]"
        f"(../../../experiments/gan2026_gold_phrase_variant_inventory_{DATE_STAMP}.json)  ",
        "Regenerator: `python scripts/build_gan2026_gold_phrase_variant_inventory.py`",
        "",
        "Every distinct official `gold_reference` for every gold label on Gan",
        "`train` + `validation` (1,050 rows). Locked `test` rows were not loaded.",
        "References are the dataset field; they are not always a verbatim letter span.",
        "Recovered letter spans live in the",
        "[workbook](../artifacts/gan_gold_phrase_variants_2026-08-13.xlsx).",
        "This catalog is exhaustive for development gold strings. It is not a",
        "performance table and not a holdout sample.",
        "",
    ]
    by_template: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in inventory["label_index"]:
        by_template[item["template"]].append(item)

    for template_row in inventory["templates"]:
        template = template_row["template"]
        lines.append(f"## `{_md_escape(template)}`")
        lines.append("")
        lines.append(
            f"{template_row['n_rows']} rows · "
            f"{template_row['n_distinct_labels']} distinct labels"
        )
        lines.append("")
        for item in by_template[template]:
            lines.append(
                f"### `{_md_escape(item['gold_label'])}` "
                f"({item['n_rows']} rows, {item['n_distinct_references']} distinct references)"
            )
            lines.append("")
            for ref in item["distinct_references"]:
                lines.append(f"- {_md_escape(ref)}")
            lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _xlsx_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _sheet_xml(headers: list[str], rows: list[list[Any]]) -> str:
    def cell(column: int, row_number: int, value: Any) -> str:
        ref = f"{chr(ord('A') + column)}{row_number}"
        if isinstance(value, int) and not isinstance(value, bool):
            return f'<c r="{ref}" t="n"><v>{value}</v></c>'
        if isinstance(value, float):
            return f'<c r="{ref}" t="n"><v>{value}</v></c>'
        text = _xlsx_escape("" if value is None else str(value))
        return f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{text}</t></is></c>'

    lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
        "<sheetData>",
    ]
    header_cells = "".join(cell(i, 1, name) for i, name in enumerate(headers))
    lines.append(f'<row r="1">{header_cells}</row>')
    for offset, row in enumerate(rows, start=2):
        body = "".join(cell(i, offset, value) for i, value in enumerate(row))
        lines.append(f'<row r="{offset}">{body}</row>')
    lines.extend(["</sheetData>", "</worksheet>"])
    return "\n".join(lines)


def _workbook_has_user_layout(path: Path) -> bool:
    import zipfile

    if not path.exists():
        return False
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
    return any(name.startswith("xl/pivotTables/") for name in names)


def _shared_strings(sst_xml: str) -> list[str]:
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    root = ET.fromstring(sst_xml)
    values: list[str] = []
    for item in root.findall("m:si", ns):
        values.append(
            "".join(
                node.text or ""
                for node in item.iter(
                    "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"
                )
            )
        )
    return values


def _append_shared_strings(sst_xml: str, new_values: list[str]) -> str:
    if not new_values:
        return sst_xml
    count_match = re.search(r'\bcount="(\d+)"', sst_xml)
    unique_match = re.search(r'\buniqueCount="(\d+)"', sst_xml)
    if not count_match or not unique_match:
        raise ValueError("sharedStrings.xml is missing count attributes")
    old_unique = int(unique_match.group(1))
    sst_xml = sst_xml.replace(
        f'count="{count_match.group(1)}"',
        f'count="{int(count_match.group(1)) + len(new_values)}"',
        1,
    )
    sst_xml = sst_xml.replace(
        f'uniqueCount="{unique_match.group(1)}"',
        f'uniqueCount="{old_unique + len(new_values)}"',
        1,
    )
    extras = "".join(f"<si><t>{_xlsx_escape(value)}</t></si>" for value in new_values)
    return sst_xml.replace("</sst>", extras + "</sst>", 1)


def _patch_gold_templates_in_workbook(path: Path, inventory: dict[str, Any]) -> None:
    """Update gold_template values without rewriting pivot, hidden cols, or order."""
    import zipfile

    by_index = {row["source_row_index"]: row["gold_template"] for row in inventory["rows"]}
    with zipfile.ZipFile(path) as archive:
        sst_xml = archive.read("xl/sharedStrings.xml").decode("utf-8")
        sheet_xml = archive.read("xl/worksheets/sheet2.xml").decode("utf-8")
        other_files = {
            name: archive.read(name)
            for name in archive.namelist()
            if name not in {"xl/sharedStrings.xml", "xl/worksheets/sheet2.xml"}
        }

    strings = _shared_strings(sst_xml)
    index_of = {value: i for i, value in enumerate(strings)}
    pending: list[str] = []

    def sst_index(value: str) -> int:
        if value in index_of:
            return index_of[value]
        index_of[value] = len(strings) + len(pending)
        pending.append(value)
        return index_of[value]

    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    sheet = ET.fromstring(sheet_xml)
    header = sheet.find("m:sheetData/m:row", ns)
    if header is None:
        raise ValueError("rows sheet has no header")
    columns: dict[str, str] = {}
    for cell in header:
        ref = cell.attrib.get("r", "")
        letter = re.match(r"[A-Z]+", ref)
        value_node = cell.find("m:v", ns)
        if letter is None or value_node is None or value_node.text is None:
            continue
        if cell.attrib.get("t") == "s":
            columns[strings[int(value_node.text)]] = letter.group(0)
    if "source_row_index" not in columns or "gold_template" not in columns:
        raise ValueError("rows sheet is missing source_row_index or gold_template")
    index_col = columns["source_row_index"]
    template_col = columns["gold_template"]

    replacements: dict[str, int] = {}
    for row in sheet.findall("m:sheetData/m:row", ns)[1:]:
        cells = {}
        for cell in row:
            ref = cell.attrib.get("r", "")
            match = re.match(r"([A-Z]+)(\d+)", ref)
            if match:
                cells[match.group(1)] = cell
        index_cell = cells.get(index_col)
        template_cell = cells.get(template_col)
        if index_cell is None or template_cell is None:
            continue
        index_text = index_cell.findtext("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")
        if index_text is None:
            continue
        source_row_index = int(float(index_text))
        template = by_index.get(source_row_index)
        if template is None:
            continue
        replacements[template_cell.attrib["r"]] = sst_index(template)

    sst_xml = _append_shared_strings(sst_xml, pending)
    for ref, new_index in replacements.items():
        sheet_xml = re.sub(
            rf'(<c r="{ref}"[^>]*>\s*<v>)(\d+)(</v>)',
            rf"\g<1>{new_index}\g<3>",
            sheet_xml,
            count=1,
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in other_files.items():
            archive.writestr(name, payload)
        archive.writestr("xl/sharedStrings.xml", sst_xml)
        archive.writestr("xl/worksheets/sheet2.xml", sheet_xml)


def write_xlsx(path: Path, inventory: dict[str, Any]) -> None:
    import zipfile

    if _workbook_has_user_layout(path):
        _patch_gold_templates_in_workbook(path, inventory)
        return


    headers = [
        "source_row_index",
        "split",
        "gold_label",
        "gold_reference",
        "recovered_letter_span",
        "span_recovery_method",
        "source_construction",
        "official_reference_construction",
        "transform",
        "gold_template",
        "gold_bucket",
        "gold_label_kind",
        "boundary_band",
        "reference_status",
        "gold_monthly_frequency",
        "row_ok",
    ]
    body = [
        [
            row["source_row_index"],
            row["split"],
            row["gold_label"],
            row["gold_reference"],
            row["recovered_letter_span"],
            row["span_recovery_method"],
            row["source_construction"],
            row["official_reference_construction"],
            row["transform"],
            row["gold_template"],
            row["gold_bucket"],
            row["gold_label_kind"],
            row["boundary_band"],
            row["reference_status"],
            row["gold_monthly_frequency"],
            row["row_ok"],
        ]
        for row in inventory["rows"]
    ]
    construction_headers = ["source_construction", "n_rows", "share", "definition"]
    construction_rows = []
    n_rows = inventory["summary"]["n_rows"]
    counts = inventory["summary"]["construction_counts"]
    for name, count in Counter(counts).most_common():
        construction_rows.append(
            [
                name,
                count,
                round(count / n_rows, 4),
                inventory["construction_definitions"].get(name, ""),
            ]
        )

    workbook = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets>
<sheet name="rows" sheetId="1" r:id="rId1"/>
<sheet name="constructions" sheetId="2" r:id="rId2"/>
</sheets>
</workbook>
"""
    pkg_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    od_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Relationships xmlns="{pkg_ns}">'
        f'<Relationship Id="rId1" Type="{od_ns}/officeDocument" '
        'Target="xl/workbook.xml"/>'
        "</Relationships>"
    )
    wb_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Relationships xmlns="{pkg_ns}">'
        f'<Relationship Id="rId1" Type="{od_ns}/worksheet" '
        'Target="worksheets/sheet1.xml"/>'
        f'<Relationship Id="rId2" Type="{od_ns}/worksheet" '
        'Target="worksheets/sheet2.xml"/>'
        "</Relationships>"
    )
    ss_main = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"
    )
    ss_sheet = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" '
        'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        f'<Override PartName="/xl/workbook.xml" ContentType="{ss_main}"/>'
        f'<Override PartName="/xl/worksheets/sheet1.xml" ContentType="{ss_sheet}"/>'
        f'<Override PartName="/xl/worksheets/sheet2.xml" ContentType="{ss_sheet}"/>'
        "</Types>"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", wb_rels)
        archive.writestr("xl/worksheets/sheet1.xml", _sheet_xml(headers, body))
        archive.writestr(
            "xl/worksheets/sheet2.xml",
            _sheet_xml(construction_headers, construction_rows),
        )


def write_outputs(
    inventory: dict[str, Any],
    output_path: Path,
    catalog_path: Path,
    workbook_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(inventory, indent=2, ensure_ascii=True) + "\n"
    output_path.write_text(payload, encoding="utf-8")
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    write_catalog_markdown(inventory, catalog_path)
    write_xlsx(workbook_path, inventory)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT
        / "experiments"
        / f"gan2026_gold_phrase_variant_inventory_{DATE_STAMP}.json",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=(
            REPO_ROOT
            / "docs"
            / "research"
            / "paper"
            / "gan_gold_phrase_variant_catalog_2026-08-13.md"
        ),
    )
    parser.add_argument(
        "--workbook",
        type=Path,
        default=(
            REPO_ROOT
            / "docs"
            / "research"
            / "artifacts"
            / "gan_gold_phrase_variants_2026-08-13.xlsx"
        ),
    )
    args = parser.parse_args()
    inventory = build_inventory()
    write_outputs(inventory, args.output, args.catalog, args.workbook)
    summary = inventory["summary"]
    print(f"wrote {args.output}")
    print(f"wrote {args.catalog}")
    print(f"wrote {args.workbook}")
    print(f"rows={summary['n_rows']} labels={summary['n_unique_labels']} "
          f"refs={summary['n_unique_references']} templates={summary['n_unique_templates']}")
    print("constructions:")
    for name, n in Counter(summary["construction_counts"]).most_common():
        print(f"  {n:4d}  {name}")
    print("transforms:")
    for name, n in Counter(summary["transform_counts"]).most_common():
        print(f"  {n:4d}  {name}")
    print("reference status:")
    for name, n in Counter(summary["reference_status_counts"]).most_common():
        print(f"  {n:4d}  {name}")
    print("span recovery:")
    for name, n in Counter(summary["span_recovery_method_counts"]).most_common():
        print(f"  {n:4d}  {name}")
    print(
        "other_paraphrase="
        f"{summary['n_other_paraphrase']} "
        f"({summary['other_paraphrase_share']:.1%})"
    )


if __name__ == "__main__":
    main()
