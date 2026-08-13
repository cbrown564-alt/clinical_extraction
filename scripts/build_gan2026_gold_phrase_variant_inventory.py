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
    r"injury related|only with)\b",
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
    rf"\b(?:\d+|{_NUMBER_WORDS})\s+"
    rf"(?:seizures?|events?|episodes?|spells?|absences?|attacks?|times?)?\s*"
    rf"(?:per|a|an|/|each)\s+(?:{_UNITS}|month|day|week|year)\b|"
    rf"\b(?:once|twice|thrice)\s+(?:per|a|an|/)\s+(?:{_UNITS})\b",
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
    "cluster_structure",
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
    "cluster_structure": (
        "The reference describes clusters. Gold usually needs the two-part "
        "N cluster per T, M per cluster grammar."
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


def _label_template(label: str) -> str:
    return re.sub(r"\b\d+(?:\.\d+)?\b", "N", label.lower().strip())


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
    if _CLUSTER_RE.search(ref):
        return "cluster_structure"
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
    if construction == "cluster_structure":
        return "cluster_two_part_render"
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
    construction = _classify_construction(reference, record.gold_label)
    transform = _classify_transform(
        gold_label=record.gold_label,
        reference=reference,
        construction=construction,
        reference_status=status,
    )
    kind = str(record.gold_label_kind)
    return {
        "source_row_index": record.source_row_index,
        "split": split,
        "gold_label": record.gold_label,
        "gold_reference": reference,
        "gold_label_kind": kind,
        "gold_bucket": _gan_bucket(kind, record.gold_label),
        "gold_template": _label_template(record.gold_label),
        "gold_monthly_frequency": record.gold_monthly_frequency,
        "boundary_band": boundary_band(record.gold_monthly_frequency),
        "reference_status": status,
        "source_construction": construction,
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
            "taxonomy": "first-cut draft for review; constructions are mutually exclusive",
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


def write_outputs(inventory: dict[str, Any], output_path: Path, catalog_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(inventory, indent=2, ensure_ascii=True) + "\n"
    output_path.write_text(payload, encoding="utf-8")
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    write_catalog_markdown(inventory, catalog_path)


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
    args = parser.parse_args()
    inventory = build_inventory()
    write_outputs(inventory, args.output, args.catalog)
    summary = inventory["summary"]
    print(f"wrote {args.output}")
    print(f"wrote {args.catalog}")
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


if __name__ == "__main__":
    main()
