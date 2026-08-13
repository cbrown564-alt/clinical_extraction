#!/usr/bin/env python3
"""Build a gold-only ExECTv2 phrase-variant inventory from development letters.

Pairs each four-family gold mention with the dataset ``raw_text`` span and
assigns a first-cut source-construction and transform class. Locked ``test``
letters are never loaded. No model predictions.

Regenerate::

    python scripts/build_exectv2_gold_phrase_variant_inventory.py
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from clinical_extraction.core.evidence import clean_semantically_neutral_text_artifacts
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.drug_lexicon import (
    DRUG_SURFACE_ALIASES,
    canonicalize_medication_name,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    DEFAULT_JSON_DIR,
    DEFAULT_SPLIT_MANIFEST,
    DEFAULT_TEXT_DIR,
    ExectAnnotation,
    ExectLetter,
    load_annotations,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DATE_STAMP = "20260813"
REPORT_DATE = "2026-08-13"
DEV_SPLIT = "dev"
KEY_FAMILIES = (
    "Diagnosis",
    "SeizureFrequency",
    "Prescription",
    "Investigations",
)

_NUMBER_WORDS = (
    "once|twice|thrice|one|two|three|four|five|six|seven|eight|nine|ten|"
    "eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
    "nineteen|twenty|thirty|couple|few"
)
_UNITS = r"day|days|night|nights|week|weeks|wk|wks|month|months|mo|year|years|yr|yrs"
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

_DIAGNOSIS_HEADING_RE = re.compile(
    r"\bdiagnosis\s*[:–—-]",
    re.IGNORECASE,
)
_HEDGE_RE = re.compile(
    r"\b(?:probable|probably|possible|possibly|unclassified|"
    r"likely|suspected|query)\b",
    re.IGNORECASE,
)
_LEGACY_TERM_RE = re.compile(
    r"\b(?:grand mal|petit mal|complex partial|simple partial|"
    r"secondary generalised|secondarily generalised|secondly generalised|"
    r"cps|gtcs?|absences?)\b",
    re.IGNORECASE,
)
_SITE_RE = re.compile(
    r"\b(?:temporal|frontal|occipital|parietal|left|right)\b",
    re.IGNORECASE,
)
_TYPO_RE = re.compile(
    r"\b(?:chronic seizures?|clinic seizures?|tonic tonic|"
    r"secondly generalised|epileps\b|seizur\b|awarenes\b)\b",
    re.IGNORECASE,
)
_CLUSTER_RE = re.compile(r"\bclusters?\b", re.IGNORECASE)
_FREE_RE = re.compile(
    r"\b(?:seizure[-\s]?free|no further (?:seizures?|events?|absences?)|"
    r"no (?:seizures?|events?|absences?) since|none since|"
    r"has not had any further|remained (?:well|stable) without)\b",
    re.IGNORECASE,
)
_CHANGE_RE = re.compile(
    r"\b(?:returned|increased|decreased|improved|worse|infrequent|frequent|"
    r"better|reduction|reduced|well[-\s]?controlled|more often|less frequent|"
    r"having more)\b",
    re.IGNORECASE,
)
_CADENCE_RE = re.compile(
    rf"\bevery\s+(?:\d+\s*(?:to|-|–)\s*)?(?:\d+\s+)?(?:{_UNITS}|fortnight)\b|"
    rf"\b(?:once|twice|thrice)\s+(?:a|per|each)\s+(?:{_UNITS})\b|"
    rf"\b(?:per|times?\s+(?:a|per)|{_NUMBER_WORDS})\s+"
    rf"(?:{_UNITS}|day|week|month|year|fortnight)\b|"
    rf"\b(?:daily|nightly|weekly|monthly|yearly|fortnightly)\b|"
    rf"\b(?:\d+|{_NUMBER_WORDS})\s*[-–to]+\s*(?:\d+|{_NUMBER_WORDS})\s+"
    rf"(?:seizures?|events?|absences?|jerks?)?\s*(?:per|a|each|/)\b|"
    rf"\b(?:\d+|{_NUMBER_WORDS})\s+(?:seizures?|events?|absences?|jerks?)\s+"
    rf"(?:per|a|each|/)\s+(?:{_UNITS}|fortnight)\b|"
    rf"\b\d+\s+per\s+(?:{_UNITS}|fortnight)\b",
    re.IGNORECASE,
)
_WINDOW_RE = re.compile(
    r"\b(?:in (?:the )?(?:last|past)|over the past|so far this|"
    r"since (?:last|the last|her last|his last)|"
    r"last (?:clinic|visit|review|week|month|year)|"
    r"years? ago|"
    r"in (?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|"
    r"dec(?:ember)?)|"
    r"during|in 20\d{2})\b",
    re.IGNORECASE,
)
_DATE_RE = re.compile(
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|"
    r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|"
    r"dec(?:ember)?)\s+\d{1,2},?\s+\d{2,4}\b|"
    r"\b20\d{2}\b",
    re.IGNORECASE,
)
_TITRATION_RE = re.compile(
    r"\b(?:increase|increasing|reduce|reducing|start(?:ing)?|commence|"
    r"to be increased|target dose|every (?:two )?weeks|fortnight|"
    r"to reduce and stop)\b",
    re.IGNORECASE,
)
_PRN_RE = re.compile(
    r"\b(?:as required|as needed|when required|p\.?r\.?n\.?|prn|rescue)\b",
    re.IGNORECASE,
)
_SPLIT_DOSE_RE = re.compile(
    r"\b(?:mane|nocte|morning|night|evening)\b.+\b(?:mane|nocte|morning|night|evening)\b",
    re.IGNORECASE | re.DOTALL,
)
_DOSE_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mgs?|mgms?|milligrams?|milligrammes?|g)\b",
    re.IGNORECASE,
)
_FREQ_TOKEN_RE = re.compile(
    r"\b(?:bd|b\.d\.|od|o\.d\.|tds|t\.d\.s\.|qds|q\.d\.s\.|"
    r"twice (?:a day|daily)|once (?:a day|daily)|three times|"
    r"daily|mane|nocte)\b",
    re.IGNORECASE,
)
_EEG_TYPE_RE = re.compile(
    r"\b(?:video(?:\s+telemetry)?|sleep[-\s]?deprived|telemetry)\b",
    re.IGNORECASE,
)
_RESULT_WORD_RE = re.compile(
    r"\b(?:normal|abnormal|abnormalit(?:y|ies)|negative|unremarkable|"
    r"showed|demonstrated|revealed|gliosis|lesion)\b",
    re.IGNORECASE,
)
_MODALITY_RE = re.compile(r"\b(?:mri|eeg|ct)s?\b", re.IGNORECASE)
_POSSESSIVE_RE = re.compile(
    r"\b(?:her|his|their)\s+\w|\b(?:she|he)['’]s got\b",
    re.IGNORECASE,
)

CONSTRUCTION_DEFINITIONS = {
    "front_matter_diagnosis_line": (
        "A labelled diagnosis line (Diagnosis: / Diagnosis –) rather than "
        "embedded prose."
    ),
    "truncation_or_offset_drift": (
        "The official span is a truncated or hyphen-cut token "
        "(epileps, seizur, epilepsy-)."
    ),
    "spelling_or_typo_variant": (
        "A spelling artefact that gold repairs: chronic/clonic, secondly/"
        "secondary, doubled spaces."
    ),
    "hedged_or_probable_label": (
        "The source hedges the concept (probable, unclassified, likely)."
    ),
    "legacy_or_synonym_term": (
        "An older or alternate name: grand mal, complex partial, secondary "
        "generalised, petit mal."
    ),
    "laterality_or_site_qualifier": (
        "A site or laterality qualifier that gold may drop or split "
        "(occipital, temporal, frontal)."
    ),
    "canonical_concept_phrase": (
        "The official span already is, or contains, the gold CUIPhrase."
    ),
    "possessive_or_anaphoric": (
        "A possessive or anaphor (her epilepsy, she's got long standing "
        "epilepsy) rather than a standalone term."
    ),
    "seizure_type_as_diagnosis": (
        "A seizure-type phrase used as a Diagnosis mention."
    ),
    "umbrella_or_inventory_mismatch": (
        "The official span names a broader or different concept than the "
        "gold CUIPhrase (epilepsy → a specific syndrome or type)."
    ),
    "cluster_mention": (
        "The source names a cluster or run of events."
    ),
    "seizure_free_phrase": (
        "Quiet-interval or zero-count language: seizure-free, no further "
        "events, none since a date or visit."
    ),
    "qualitative_change": (
        "A direction or quality without a countable cadence: returned, "
        "increased, infrequent, well controlled."
    ),
    "numeric_cadence": (
        "An explicit N per unit, every-N, or daily/weekly cadence."
    ),
    "count_in_named_window": (
        "A count or range anchored to a date, month, year, or last visit, "
        "without a standing cadence."
    ),
    "type_token_only": (
        "The official span is only the seizure-type token; the scored state "
        "lives in surrounding letter language."
    ),
    "titration_or_future_plan": (
        "The span bundles a current dose with a titration or start/stop plan."
    ),
    "rescue_or_prn": (
        "As-required / PRN / rescue language."
    ),
    "brand_name": (
        "A brand or spelling alias (Epilim, Tegretol, Keppra, Lamictal)."
    ),
    "split_daily_dose": (
        "A split mane/nocte or morning/night dose line."
    ),
    "complete_regimen_line": (
        "Drug, dose, and frequency are all present in the source span."
    ),
    "drug_name_only_span": (
        "The official span is just the drug name; dose and frequency sit "
        "elsewhere in the letter."
    ),
    "eeg_type_named": (
        "The source names an EEG type: video, sleep-deprived, telemetry."
    ),
    "modality_plus_result": (
        "The source span already carries a result word with the modality."
    ),
    "finding_in_prose": (
        "A finding or abnormality is described in prose rather than a "
        "normal/abnormal token."
    ),
    "dated_investigation": (
        "The investigation is dated or sequenced (last MRI in January 2018)."
    ),
    "modality_token": (
        "The official span is only MRI / EEG / CT; gold still encodes "
        "performed and result."
    ),
    "other_paraphrase": (
        "Residual paraphrases that do not match a more specific construction."
    ),
}

TRANSFORM_DEFINITIONS = {
    "identity_or_near_copy": "Gold concept or finding is already in the source.",
    "hyphen_unfold": "Hyphenated markup unfolds to the gold phrase.",
    "alias_to_canonical_concept": (
        "A synonym, typo, truncation, or hedge maps to the gold CUIPhrase."
    ),
    "assign_diag_category": (
        "The source names a concept; gold also requires Epilepsy / "
        "MultipleSeizures / SingleSeizure."
    ),
    "inventory_selection": (
        "The letter names a broader or competing concept; gold keeps a "
        "specific inventory item."
    ),
    "project_state_from_context": (
        "The official span is a type token; the scored SF state is assembled "
        "from nearby letter language."
    ),
    "cadence_to_state": "An N-per-unit or every-N phrase becomes an SF state.",
    "windowed_count_to_state": (
        "A dated or last-visit count becomes a named-window state."
    ),
    "qualitative_change_to_state": (
        "Returned / increased / infrequent language becomes FrequencyChange."
    ),
    "zero_count_to_seizure_free": (
        "Quiet-interval language becomes a zero-count seizure-free state."
    ),
    "cluster_to_windowed_state": (
        "A cluster mention becomes a dated or windowed SF state."
    ),
    "parse_regimen_slots": (
        "A regimen line is split into drug, dose, unit, and frequency."
    ),
    "brand_to_generic": "A brand or alias becomes the gold generic.",
    "frequency_token_to_count": "bd / twice daily / nocte becomes Frequency=N.",
    "rescue_as_required": "PRN language becomes Frequency=As_Required.",
    "current_dose_from_titration_span": (
        "A titration line still golds the current dose, not the target."
    ),
    "modality_to_finding_component": (
        "A modality token becomes performed + result (MRI → mri-abnormal)."
    ),
    "result_word_to_component": (
        "A result or finding word is projected onto the investigation "
        "component."
    ),
    "other_semantic_map": "Residual mapping not covered by a named transform.",
}


def _unfold(text: str | None) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("-", " ")).strip()


def _content_tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if token not in _STOPWORDS and len(token) > 1
    }


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [part.strip() for part in parts if part.strip()]


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
    if not collapsed_needle:
        return None
    idx = collapsed_note.lower().find(collapsed_needle.lower())
    if idx >= 0:
        return collapsed_note[idx : idx + len(collapsed_needle)]
    return None


def _containing_sentence(note: str, span: str) -> str | None:
    if not span:
        return None
    idx = note.lower().find(span.lower())
    if idx < 0:
        collapsed = re.sub(r"\s+", " ", note)
        idx = collapsed.lower().find(re.sub(r"\s+", " ", span).lower())
        if idx < 0:
            return None
        note = collapsed
    start = idx
    end = idx + len(span)
    while start > 0 and note[start - 1] not in ".\n!?":
        start -= 1
    while end < len(note) and note[end] not in ".\n!?":
        end += 1
    window = re.sub(r"\s+", " ", note[start:end]).strip(" \t-:;")
    return window[:400] if window else None


def _reference_status(reference: str, note_text: str) -> str:
    unfolded = _unfold(reference)
    if not unfolded:
        return "empty_official_span"
    if reference in note_text or unfolded in note_text:
        return "verbatim_in_note"
    if reference.lower() in note_text.lower() or unfolded.lower() in note_text.lower():
        return "casefold_in_note"
    collapsed = re.sub(r"\s+", " ", unfolded).strip()
    collapsed_note = re.sub(r"\s+", " ", note_text)
    if collapsed and collapsed in collapsed_note:
        return "whitespace_normalized_in_note"
    if collapsed.lower() in collapsed_note.lower():
        return "whitespace_casefold_in_note"
    return "not_in_note"


def _sf_mention_bucket(attributes: dict[str, str]) -> str:
    count_values = [
        attributes[key]
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
        )
        if key in attributes
    ]
    has_count = bool(count_values)
    has_cadence = "TimePeriod" in attributes or any(
        "TimePeriod" in key for key in attributes
    )
    has_change = "FrequencyChange" in attributes
    has_anchor = any(
        key in attributes
        for key in (
            "PointInTime",
            "TimeSince_or_TimeOfEvent",
            "YearDate",
            "MonthDate",
            "DayDate",
        )
    )
    if has_count and all(value in {"", "0"} for value in count_values):
        return "seizure_free"
    if has_count and has_cadence:
        return "numeric_cadence_rate"
    if has_count and has_anchor and not has_cadence:
        return "count_in_named_window"
    if has_change and not has_count:
        return "qualitative_frequency_change"
    if has_change and has_count:
        return "numeric_plus_frequency_change"
    if has_count:
        return "count_without_cadence_or_anchor"
    return "sparse_or_other"


def _render_count(attributes: dict[str, str]) -> str:
    if attributes.get("NumberOfSeizures"):
        return attributes["NumberOfSeizures"]
    lower = attributes.get("LowerNumberOfSeizures")
    upper = attributes.get("UpperNumberOfSeizures")
    if lower and upper and lower != upper:
        return f"{lower} to {upper}"
    return lower or upper or "N"


def _render_period(attributes: dict[str, str]) -> str:
    unit = (attributes.get("TimePeriod") or "period").lower()
    if attributes.get("NumberOfTimePeriods"):
        n = attributes["NumberOfTimePeriods"]
        return unit if n == "1" else f"{n} {unit}"
    lower = attributes.get("LowerNumberOfTimePeriods")
    upper = attributes.get("UpperNumberOfTimePeriods")
    if lower and upper and lower != upper:
        return f"{lower} to {upper} {unit}"
    if lower or upper:
        return f"{lower or upper} {unit}"
    return unit


def _render_anchor(attributes: dict[str, str]) -> str:
    if attributes.get("PointInTime"):
        return attributes["PointInTime"]
    year = attributes.get("YearDate")
    month = attributes.get("MonthDate")
    if year and month:
        return f"{year}-{month.zfill(2)}"
    if year:
        return year
    if attributes.get("TimeSince_or_TimeOfEvent"):
        return attributes["TimeSince_or_TimeOfEvent"]
    return "named window"


def _frequency_word(value: str | None) -> str:
    mapping = {
        "1": "once daily",
        "2": "twice daily",
        "3": "three times daily",
        "4": "four times daily",
        "as_required": "as required",
    }
    if not value:
        return "unspecified frequency"
    return mapping.get(value.lower(), value)


def _gold_type_phrase(annotation: ExectAnnotation) -> str:
    phrase = annotation.attributes.get("CUIPhrase") or annotation.text
    return _unfold(phrase) or "unspecified"


def diagnosis_gold_key(annotation: ExectAnnotation) -> str:
    concept = _gold_type_phrase(annotation)
    category = annotation.attributes.get("DiagCategory") or "missing"
    return f"{concept} (DiagCategory={category})"


def diagnosis_template(annotation: ExectAnnotation) -> str:
    category = annotation.attributes.get("DiagCategory") or "missing"
    return f"concept (DiagCategory={category})"


def sf_gold_key(annotation: ExectAnnotation) -> str:
    typ = _gold_type_phrase(annotation)
    bucket = _sf_mention_bucket(dict(annotation.attributes))
    attrs = dict(annotation.attributes)
    if bucket == "seizure_free":
        return f"{typ}: seizure-free"
    if bucket == "qualitative_frequency_change":
        change = (attrs.get("FrequencyChange") or "change").lower()
        return f"{typ}: frequency {change}"
    if bucket == "numeric_cadence_rate":
        return f"{typ}: {_render_count(attrs)} per {_render_period(attrs)}"
    if bucket == "count_in_named_window":
        return f"{typ}: {_render_count(attrs)} in {_render_anchor(attrs)}"
    if bucket == "numeric_plus_frequency_change":
        change = (attrs.get("FrequencyChange") or "change").lower()
        return f"{typ}: {_render_count(attrs)}, frequency {change}"
    if bucket == "count_without_cadence_or_anchor":
        return f"{typ}: {_render_count(attrs)}"
    return f"{typ}: {bucket}"


def sf_template(annotation: ExectAnnotation) -> str:
    bucket = _sf_mention_bucket(dict(annotation.attributes))
    attrs = dict(annotation.attributes)
    if bucket == "seizure_free":
        return "type: seizure-free"
    if bucket == "qualitative_frequency_change":
        change = (attrs.get("FrequencyChange") or "change").lower()
        return f"type: frequency {change}"
    if bucket == "numeric_cadence_rate":
        count = _render_count(attrs)
        count_shape = "range" if " to " in count else "N"
        period = _render_period(attrs)
        period_shape = re.sub(r"\d+", "N", period)
        return f"type: {count_shape} per {period_shape}"
    if bucket == "count_in_named_window":
        return "type: N in named window"
    return f"type: {bucket}"


def rx_gold_key(annotation: ExectAnnotation) -> str:
    attrs = dict(annotation.attributes)
    raw_drug = attrs.get("DrugName") or attrs.get("CUIPhrase") or annotation.text
    drug = _unfold(canonicalize_medication_name(raw_drug))
    freq = attrs.get("Frequency")
    if freq and freq.lower() == "as_required":
        return f"{drug} as required"
    dose = attrs.get("DrugDose")
    unit = attrs.get("DoseUnit")
    parts = [drug]
    if dose and unit:
        parts.append(f"{dose} {unit}")
    elif dose:
        parts.append(dose)
    parts.append(_frequency_word(freq))
    return " ".join(parts)


def rx_template(annotation: ExectAnnotation) -> str:
    freq = annotation.attributes.get("Frequency")
    if freq and freq.lower() == "as_required":
        return "drug as required"
    if annotation.attributes.get("DrugDose"):
        return "drug N unit frequency"
    return "drug frequency"


def inv_gold_key(annotation: ExectAnnotation) -> str:
    attrs = dict(annotation.attributes)
    parts: list[str] = []
    for modality in ("MRI", "CT", "EEG"):
        performed = attrs.get(f"{modality}_Performed")
        result = attrs.get(f"{modality}_Results")
        if not performed and not result:
            continue
        chunk = modality
        if result:
            chunk += f" {result.lower()}"
        elif performed:
            chunk += f" performed={performed.lower()}"
        if modality == "EEG" and attrs.get("EEG_Type"):
            chunk += f" ({attrs['EEG_Type']})"
        parts.append(chunk)
    if parts:
        return "; ".join(parts)
    return _unfold(attrs.get("CUIPhrase") or annotation.text) or "investigation"


def inv_template(annotation: ExectAnnotation) -> str:
    attrs = dict(annotation.attributes)
    parts: list[str] = []
    for modality in ("MRI", "CT", "EEG"):
        result = attrs.get(f"{modality}_Results")
        performed = attrs.get(f"{modality}_Performed")
        if not performed and not result:
            continue
        chunk = f"{modality} {{result}}" if result else f"{modality} performed"
        if modality == "EEG" and attrs.get("EEG_Type"):
            chunk += " (type)"
        parts.append(chunk)
    return "; ".join(parts) if parts else "investigation"


def gold_key_for(annotation: ExectAnnotation) -> str:
    if annotation.entity == "Diagnosis":
        return diagnosis_gold_key(annotation)
    if annotation.entity == "SeizureFrequency":
        return sf_gold_key(annotation)
    if annotation.entity == "Prescription":
        return rx_gold_key(annotation)
    if annotation.entity == "Investigations":
        return inv_gold_key(annotation)
    return _unfold(annotation.text)


def gold_template_for(annotation: ExectAnnotation) -> str:
    if annotation.entity == "Diagnosis":
        return diagnosis_template(annotation)
    if annotation.entity == "SeizureFrequency":
        return sf_template(annotation)
    if annotation.entity == "Prescription":
        return rx_template(annotation)
    if annotation.entity == "Investigations":
        return inv_template(annotation)
    return "other"


def gold_subtype_for(annotation: ExectAnnotation) -> str:
    if annotation.entity == "Diagnosis":
        return annotation.attributes.get("DiagCategory") or "missing"
    if annotation.entity == "SeizureFrequency":
        return _sf_mention_bucket(dict(annotation.attributes))
    if annotation.entity == "Prescription":
        if (annotation.attributes.get("Frequency") or "").lower() == "as_required":
            return "rescue_as_required"
        if all(
            annotation.attributes.get(key)
            for key in ("DrugName", "DrugDose", "DoseUnit", "Frequency")
        ):
            return "complete_regimen"
        return "incomplete_or_partial"
    if annotation.entity == "Investigations":
        for modality in ("MRI", "CT", "EEG"):
            if annotation.attributes.get(f"{modality}_Performed") or annotation.attributes.get(
                f"{modality}_Results"
            ):
                return modality
        return "unspecified"
    return "other"


def recover_letter_span(
    note_text: str,
    annotation: ExectAnnotation,
) -> tuple[str, str]:
    """Return (span, recovery_method). Never uses test letters."""
    candidates = [
        annotation.raw_text or "",
        _unfold(annotation.raw_text),
        annotation.text,
        _unfold(annotation.text),
        annotation.attributes.get("CUIPhrase") or "",
        _unfold(annotation.attributes.get("CUIPhrase")),
    ]
    seen: set[str] = set()
    for needle in candidates:
        key = needle.lower()
        if not needle or key in seen:
            continue
        seen.add(key)
        found = _find_span(note_text, needle)
        if not found:
            continue
        sentence = _containing_sentence(note_text, found)
        if sentence and len(sentence) > len(found) + 8:
            return sentence, "official_span_expanded_to_sentence"
        return found, "official_reference_in_letter"

    family_hints = {
        "Diagnosis": r"\bdiagnos|epilep|seizure|absence|myoclonic|tonic|focal\b",
        "SeizureFrequency": (
            r"seizure|absence|jerk|cluster|per |daily|weekly|monthly|"
            r"seizure-free|frequency|since last"
        ),
        "Prescription": r"\bmg\b|twice daily|\bbd\b|medication|lamotrigine|valproate",
        "Investigations": r"\bmri\b|\beeg\b|\bct\b|normal|abnormal|scan",
    }
    hint = re.compile(family_hints.get(annotation.entity, r"."), re.I)
    target_tokens = _content_tokens(
        " ".join(
            [
                _unfold(annotation.raw_text),
                _unfold(annotation.attributes.get("CUIPhrase")),
                _gold_type_phrase(annotation),
            ]
        )
    )
    gold_nums = set(re.findall(r"\d+", " ".join(annotation.attributes.values())))
    best: tuple[int, str] | None = None
    for sent in _sentences(note_text):
        if len(sent) < 12:
            continue
        sent_tokens = _content_tokens(sent)
        overlap = len(target_tokens & sent_tokens)
        num_hit = sum(1 for number in gold_nums if number in sent)
        hinted = 1 if hint.search(sent) else 0
        if hinted == 0 and overlap < 2:
            continue
        score = overlap * 2 + num_hit * 3 + hinted * 2
        if score > 0 and (best is None or score > best[0]):
            best = (score, sent)
    if best is None:
        return "", "no_span_recovered"
    span = re.sub(r"\s+", " ", best[1]).strip()[:400]
    if best[0] >= 5:
        return span, "scored_justifying_sentence"
    return span, "weak_justifying_sentence"


def _is_brand(text: str) -> bool:
    tokens = normalize_phrase(text)
    if tokens in DRUG_SURFACE_ALIASES:
        return True
    for key in DRUG_SURFACE_ALIASES:
        if re.search(rf"\b{re.escape(key)}\b", tokens):
            return True
    return False


def _classify_diagnosis(span: str, annotation: ExectAnnotation) -> str:
    raw = _unfold(annotation.raw_text)
    cui = _unfold(annotation.attributes.get("CUIPhrase"))
    evidence = span or raw
    low = evidence.lower()
    raw_norm = normalize_phrase(raw)
    cui_norm = normalize_phrase(cui)
    if _DIAGNOSIS_HEADING_RE.search(evidence):
        return "front_matter_diagnosis_line"
    if raw.endswith("-") or re.search(r"\b(?:epileps|seizur|seizures e)\b", raw, re.I):
        return "truncation_or_offset_drift"
    if _TYPO_RE.search(raw) or "tonic   clonic" in raw.lower() or "tonic chronic" in raw.lower():
        return "spelling_or_typo_variant"
    if _HEDGE_RE.search(evidence):
        return "hedged_or_probable_label"
    if _LEGACY_TERM_RE.search(evidence) and raw_norm != cui_norm:
        return "legacy_or_synonym_term"
    if _SITE_RE.search(raw) and raw_norm != cui_norm:
        return "laterality_or_site_qualifier"
    if raw_norm == cui_norm or (cui and cui.lower() in low):
        return "canonical_concept_phrase"
    if _POSSESSIVE_RE.search(evidence):
        return "possessive_or_anaphoric"
    category = annotation.attributes.get("DiagCategory") or ""
    if category in {"MultipleSeizures", "SingleSeizure"} and re.search(
        r"\b(?:seizure|absence|jerk|tonic|clonic|focal|generalised)\b",
        low,
    ):
        return "seizure_type_as_diagnosis"
    if raw_norm and cui_norm and raw_norm != cui_norm:
        return "umbrella_or_inventory_mismatch"
    return "other_paraphrase"


def _classify_sf(span: str, annotation: ExectAnnotation) -> str:
    evidence = span or _unfold(annotation.raw_text)
    raw = _unfold(annotation.raw_text)
    if _CLUSTER_RE.search(evidence):
        return "cluster_mention"
    if _FREE_RE.search(evidence):
        return "seizure_free_phrase"
    if _CADENCE_RE.search(evidence):
        return "numeric_cadence"
    if _WINDOW_RE.search(evidence) or _DATE_RE.search(evidence):
        return "count_in_named_window"
    if _CHANGE_RE.search(evidence):
        return "qualitative_change"
    type_norm = normalize_phrase(annotation.attributes.get("CUIPhrase") or annotation.text)
    raw_norm = normalize_phrase(raw)
    if raw_norm == type_norm or len(raw.split()) <= 3:
        return "type_token_only"
    if not any(
        pattern.search(evidence)
        for pattern in (_CADENCE_RE, _WINDOW_RE, _CHANGE_RE, _FREE_RE, _CLUSTER_RE)
    ):
        return "type_token_only"
    return "other_paraphrase"


def _classify_rx(span: str, annotation: ExectAnnotation) -> str:
    evidence = span or _unfold(annotation.raw_text)
    raw = _unfold(annotation.raw_text)
    frequency = (annotation.attributes.get("Frequency") or "").lower()
    if _PRN_RE.search(evidence) or frequency == "as_required":
        if _PRN_RE.search(evidence) or len(raw.split()) <= 2:
            return "rescue_or_prn"
    if _TITRATION_RE.search(evidence):
        return "titration_or_future_plan"
    if _is_brand(raw) or _is_brand(evidence):
        return "brand_name"
    if _SPLIT_DOSE_RE.search(evidence):
        return "split_daily_dose"
    if _DOSE_RE.search(evidence) and _FREQ_TOKEN_RE.search(evidence):
        return "complete_regimen_line"
    if not _DOSE_RE.search(raw) and len(raw.split()) <= 3:
        return "drug_name_only_span"
    if _DOSE_RE.search(evidence):
        return "complete_regimen_line"
    return "other_paraphrase"


def _classify_inv(span: str, annotation: ExectAnnotation) -> str:
    evidence = span or _unfold(annotation.raw_text)
    raw = _unfold(annotation.raw_text)
    if _EEG_TYPE_RE.search(evidence):
        return "eeg_type_named"
    if _RESULT_WORD_RE.search(raw):
        return "modality_plus_result"
    if _RESULT_WORD_RE.search(evidence) and not _RESULT_WORD_RE.search(raw):
        return "finding_in_prose"
    if _DATE_RE.search(evidence) or re.search(r"\blast\b", evidence, re.I):
        return "dated_investigation"
    if _MODALITY_RE.fullmatch(raw) or len(raw.split()) <= 2:
        return "modality_token"
    if _RESULT_WORD_RE.search(evidence):
        return "modality_plus_result"
    return "other_paraphrase"


def classify_construction(span: str, annotation: ExectAnnotation) -> str:
    if annotation.entity == "Diagnosis":
        return _classify_diagnosis(span, annotation)
    if annotation.entity == "SeizureFrequency":
        return _classify_sf(span, annotation)
    if annotation.entity == "Prescription":
        return _classify_rx(span, annotation)
    if annotation.entity == "Investigations":
        return _classify_inv(span, annotation)
    return "other_paraphrase"


def classify_transform(
    *,
    annotation: ExectAnnotation,
    span: str,
    construction: str,
    gold: str,
) -> str:
    evidence = (span or _unfold(annotation.raw_text)).lower()
    gold_low = gold.lower()
    cui = _unfold(annotation.attributes.get("CUIPhrase")).lower()
    family = annotation.entity

    if family == "Diagnosis":
        if construction == "canonical_concept_phrase" and cui and cui in evidence:
            return "identity_or_near_copy"
        if construction == "truncation_or_offset_drift" and (
            _unfold(annotation.raw_text).endswith("-")
            or "-" in (annotation.raw_text or "")
        ):
            return "hyphen_unfold"
        if construction in {
            "truncation_or_offset_drift",
            "spelling_or_typo_variant",
            "legacy_or_synonym_term",
            "hedged_or_probable_label",
            "laterality_or_site_qualifier",
        }:
            return "alias_to_canonical_concept"
        if construction == "umbrella_or_inventory_mismatch":
            return "inventory_selection"
        if construction in {"front_matter_diagnosis_line", "possessive_or_anaphoric"}:
            if cui and cui in evidence:
                return "identity_or_near_copy"
            return "alias_to_canonical_concept"
        if construction == "seizure_type_as_diagnosis":
            return "assign_diag_category"
        if cui and cui in evidence:
            return "identity_or_near_copy"
        return "other_semantic_map"

    if family == "SeizureFrequency":
        if construction == "type_token_only":
            return "project_state_from_context"
        if construction == "numeric_cadence":
            return "cadence_to_state"
        if construction == "count_in_named_window":
            return "windowed_count_to_state"
        if construction == "qualitative_change":
            return "qualitative_change_to_state"
        if construction == "seizure_free_phrase":
            return "zero_count_to_seizure_free"
        if construction == "cluster_mention":
            return "cluster_to_windowed_state"
        return "other_semantic_map"

    if family == "Prescription":
        if construction == "brand_name":
            return "brand_to_generic"
        if construction == "rescue_or_prn":
            return "rescue_as_required"
        if construction == "titration_or_future_plan":
            return "current_dose_from_titration_span"
        if construction == "complete_regimen_line":
            if _FREQ_TOKEN_RE.search(evidence):
                return "frequency_token_to_count"
            return "parse_regimen_slots"
        if construction == "split_daily_dose":
            return "parse_regimen_slots"
        if construction == "drug_name_only_span":
            return "parse_regimen_slots"
        return "other_semantic_map"

    if family == "Investigations":
        if construction == "modality_token":
            return "modality_to_finding_component"
        if construction in {"modality_plus_result", "finding_in_prose", "eeg_type_named"}:
            return "result_word_to_component"
        if construction == "dated_investigation":
            if _RESULT_WORD_RE.search(evidence):
                return "result_word_to_component"
            return "modality_to_finding_component"
        if gold_low.split("(")[0].strip() in evidence:
            return "identity_or_near_copy"
        return "other_semantic_map"

    return "other_semantic_map"


def load_dev140_letters() -> list[ExectLetter]:
    """Load only the development split. Test JSON files are never opened."""
    manifest = json.loads(DEFAULT_SPLIT_MANIFEST.read_text(encoding="utf-8"))
    letter_ids = list(manifest["splits"][DEV_SPLIT]["letter_ids"])
    if any(letter_id.startswith("LOCKED") for letter_id in letter_ids):
        raise RuntimeError("dev split contains unexpected locked ids")
    letters: list[ExectLetter] = []
    for letter_id in letter_ids:
        json_path = DEFAULT_JSON_DIR / f"{letter_id}.json"
        text_path = DEFAULT_TEXT_DIR / f"{letter_id}.txt"
        note_text = (
            clean_semantically_neutral_text_artifacts(text_path.read_text(encoding="utf-8"))
            if text_path.exists()
            else ""
        )
        letters.append(
            ExectLetter(
                letter_id=letter_id,
                note_text=note_text,
                annotations=load_annotations(json_path),
            )
        )
    letters.sort(key=lambda letter: letter.letter_id)
    if len(letters) != 140:
        raise RuntimeError(f"expected 140 development letters, got {len(letters)}")
    return letters


def _row_payload(
    letter: ExectLetter,
    annotation: ExectAnnotation,
    mention_index: int,
) -> dict[str, Any]:
    official = annotation.raw_text or ""
    status = _reference_status(official, letter.note_text)
    recovered, recovery_method = recover_letter_span(letter.note_text, annotation)
    official_construction = classify_construction(_unfold(official), annotation)
    evidence = recovered if recovered else _unfold(official)
    construction = classify_construction(evidence, annotation)
    gold = gold_key_for(annotation)
    transform = classify_transform(
        annotation=annotation,
        span=evidence,
        construction=construction,
        gold=gold,
    )
    cui_phrase = _unfold(annotation.attributes.get("CUIPhrase"))
    return {
        "letter_id": letter.letter_id,
        "mention_index": mention_index,
        "split": DEV_SPLIT,
        "family": annotation.entity,
        "gold_key": gold,
        "gold_template": gold_template_for(annotation),
        "gold_subtype": gold_subtype_for(annotation),
        "cui_phrase": cui_phrase,
        "cui": annotation.attributes.get("CUI") or "",
        "official_raw_text": official,
        "official_raw_unfolded": _unfold(official),
        "recovered_letter_span": recovered,
        "span_recovery_method": recovery_method,
        "reference_status": status,
        "source_construction": construction,
        "official_reference_construction": official_construction,
        "transform": transform,
        "attributes": dict(annotation.attributes),
        "flags": {
            "gold_key_in_official": gold.lower() in _unfold(official).lower(),
            "cui_phrase_in_official": bool(cui_phrase)
            and cui_phrase.lower() in _unfold(official).lower(),
            "cui_phrase_in_letter": bool(cui_phrase)
            and cui_phrase.lower() in letter.note_text.lower(),
            "gold_key_in_letter": gold.lower() in letter.note_text.lower(),
            "official_is_short_token": len(_unfold(official).split()) <= 2,
        },
    }


def _letter_composition(letters: list[ExectLetter]) -> dict[str, Any]:
    family_present = Counter()
    family_absent = Counter()
    four_counts: list[int] = []
    empty_sf = 0
    for letter in letters:
        present = [family for family in KEY_FAMILIES if letter.entities(family)]
        four_counts.append(len(present))
        for family in KEY_FAMILIES:
            if letter.entities(family):
                family_present[family] += 1
            else:
                family_absent[family] += 1
        if not letter.entities("SeizureFrequency"):
            empty_sf += 1
    return {
        "n_letters": len(letters),
        "letters_with_family": dict(family_present),
        "letters_without_family": dict(family_absent),
        "four_family_count_per_letter": dict(Counter(four_counts).most_common()),
        "letters_empty_sf": empty_sf,
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
        pair = (row["gold_key"], row["official_raw_text"].lower())
        if pair in seen[value]:
            continue
        if len(grouped[value]) >= limit:
            continue
        seen[value].add(pair)
        grouped[value].append(
            {
                "letter_id": row["letter_id"],
                "family": row["family"],
                "gold_key": row["gold_key"],
                "official_raw_text": row["official_raw_text"],
                "recovered_letter_span": row["recovered_letter_span"],
                "reference_status": row["reference_status"],
            }
        )
    return dict(grouped)


def build_inventory() -> dict[str, Any]:
    letters = load_dev140_letters()
    rows: list[dict[str, Any]] = []
    for letter in letters:
        mention_index = 0
        for annotation in letter.annotations:
            if annotation.entity not in KEY_FAMILIES:
                continue
            rows.append(_row_payload(letter, annotation, mention_index))
            mention_index += 1

    family_c = Counter(row["family"] for row in rows)
    key_c = Counter(row["gold_key"] for row in rows)
    template_c = Counter((row["family"], row["gold_template"]) for row in rows)
    raw_c = Counter(row["official_raw_unfolded"].lower() for row in rows)
    construction_c = Counter(row["source_construction"] for row in rows)
    transform_c = Counter(row["transform"] for row in rows)
    status_c = Counter(row["reference_status"] for row in rows)
    recovery_c = Counter(row["span_recovery_method"] for row in rows)
    subtype_c = Counter((row["family"], row["gold_subtype"]) for row in rows)

    refs_by_key: dict[str, list[str]] = defaultdict(list)
    seen_ref: dict[str, set[str]] = defaultdict(set)
    family_by_key: dict[str, str] = {}
    template_by_key: dict[str, str] = {}
    for row in rows:
        family_by_key[row["gold_key"]] = row["family"]
        template_by_key[row["gold_key"]] = row["gold_template"]
        key = row["official_raw_unfolded"].lower()
        if key in seen_ref[row["gold_key"]]:
            continue
        seen_ref[row["gold_key"]].add(key)
        refs_by_key[row["gold_key"]].append(row["official_raw_text"])

    label_index = [
        {
            "family": family_by_key[key],
            "gold_key": key,
            "gold_template": template_by_key[key],
            "n_mentions": key_c[key],
            "n_distinct_references": len(refs_by_key[key]),
            "distinct_references": refs_by_key[key],
        }
        for key, _n in key_c.most_common()
    ]

    template_index = []
    for (family, template), n in template_c.most_common():
        labels = [
            item["gold_key"]
            for item in label_index
            if item["gold_template"] == template and item["family"] == family
        ]
        template_index.append(
            {
                "family": family,
                "template": template,
                "n_mentions": n,
                "n_distinct_keys": len(labels),
                "keys": labels,
            }
        )

    family_summaries: dict[str, Any] = {}
    for family in KEY_FAMILIES:
        family_rows = [row for row in rows if row["family"] == family]
        family_keys = Counter(row["gold_key"] for row in family_rows)
        family_raws = Counter(row["official_raw_unfolded"].lower() for row in family_rows)
        family_cuis = Counter(row["cui_phrase"] for row in family_rows)
        family_summaries[family] = {
            "n_mentions": len(family_rows),
            "n_letters": len({row["letter_id"] for row in family_rows}),
            "n_unique_gold_keys": len(family_keys),
            "n_singleton_gold_keys": sum(1 for n in family_keys.values() if n == 1),
            "n_unique_official_spans": len(family_raws),
            "n_unique_cui_phrases": len(family_cuis),
            "n_cui_phrase_in_letter": sum(
                1 for row in family_rows if row["flags"]["cui_phrase_in_letter"]
            ),
            "n_gold_key_in_official": sum(
                1 for row in family_rows if row["flags"]["gold_key_in_official"]
            ),
            "n_short_official_token": sum(
                1 for row in family_rows if row["flags"]["official_is_short_token"]
            ),
            "construction_counts": dict(
                Counter(row["source_construction"] for row in family_rows)
            ),
            "transform_counts": dict(Counter(row["transform"] for row in family_rows)),
            "subtype_counts": dict(Counter(row["gold_subtype"] for row in family_rows)),
        }

    return {
        "schema_version": "exectv2_gold_phrase_variant_inventory.v1",
        "date": REPORT_DATE,
        "claim_boundary": {
            "splits": [DEV_SPLIT],
            "excluded_split": "test",
            "row_inspection": (
                "development only; locked test letters were not loaded"
            ),
            "predictions": "none; gold mentions and official raw_text only",
            "surface": "four-family clinical fact surface only",
            "reference_field": (
                "official_raw_text is the dataset annotated span. Offsets "
                "drifted after spelling correction and are not used for "
                "matching. Recovered letter spans live in the workbook."
            ),
            "taxonomy": (
                "source_construction is assigned from the recovered letter "
                "span when one exists, otherwise from official raw_text"
            ),
        },
        "summary": {
            "n_letters": len(letters),
            "n_mentions": len(rows),
            "n_unique_gold_keys": len(key_c),
            "n_singleton_gold_keys": sum(1 for n in key_c.values() if n == 1),
            "n_unique_official_spans": len(raw_c),
            "n_unique_templates": len(template_c),
            "n_other_paraphrase": construction_c.get("other_paraphrase", 0),
            "other_paraphrase_share": round(
                construction_c.get("other_paraphrase", 0) / max(len(rows), 1),
                4,
            ),
            "family_counts": dict(family_c),
            "construction_counts": dict(construction_c),
            "transform_counts": dict(transform_c),
            "reference_status_counts": dict(status_c),
            "span_recovery_method_counts": dict(recovery_c),
            "subtype_counts": {
                f"{family}:{subtype}": n for (family, subtype), n in subtype_c.items()
            },
        },
        "letter_composition": _letter_composition(letters),
        "family_summaries": family_summaries,
        "construction_definitions": CONSTRUCTION_DEFINITIONS,
        "transform_definitions": TRANSFORM_DEFINITIONS,
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
        "# ExECTv2 gold phrase-variant catalog",
        "",
        f"Date: {REPORT_DATE}  ",
        "Status: generated development catalog; first draft  ",
        "Parent: [phrase-variant argument](exect_gold_phrase_variants_2026-08-13.md)  ",
        f"Artifact: [`experiments/exectv2_gold_phrase_variant_inventory_{DATE_STAMP}.json`]"
        f"(../../../experiments/exectv2_gold_phrase_variant_inventory_{DATE_STAMP}.json)  ",
        "Regenerator: `python scripts/build_exectv2_gold_phrase_variant_inventory.py`",
        "",
        "Every distinct official `raw_text` for every four-family gold mention",
        "on ExECT `dev140`. Locked `test` letters were not loaded. Official",
        "spans are the dataset field; they are often a type or modality token",
        "rather than the full justifying sentence. Recovered letter spans live",
        "in the [workbook](../artifacts/exect_gold_phrase_variants_2026-08-13.xlsx).",
        "This catalog is exhaustive for development gold keys on the four-family",
        "surface. It is not a performance table and not a holdout sample.",
        "",
    ]
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in inventory["label_index"]:
        by_family[item["family"]].append(item)

    for family in KEY_FAMILIES:
        family_items = by_family.get(family, [])
        n_mentions = sum(item["n_mentions"] for item in family_items)
        lines.append(f"## {family}")
        lines.append("")
        lines.append(
            f"{n_mentions} mentions · {len(family_items)} distinct gold keys"
        )
        lines.append("")
        by_template: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in family_items:
            by_template[item["gold_template"]].append(item)
        family_templates = [
            row
            for row in inventory["templates"]
            if row["family"] == family
        ]
        for template_row in family_templates:
            template = template_row["template"]
            lines.append(f"### `{_md_escape(template)}`")
            lines.append("")
            lines.append(
                f"{template_row['n_mentions']} mentions · "
                f"{template_row['n_distinct_keys']} distinct keys"
            )
            lines.append("")
            for item in by_template[template]:
                lines.append(
                    f"#### `{_md_escape(item['gold_key'])}` "
                    f"({item['n_mentions']} mentions, "
                    f"{item['n_distinct_references']} distinct references)"
                )
                lines.append("")
                for ref in item["distinct_references"]:
                    lines.append(f"- {_md_escape(_unfold(ref) or ref)}")
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
    header_cells = "".join(cell(i, 1, header) for i, header in enumerate(headers))
    lines.append(f'<row r="1">{header_cells}</row>')
    for row_number, values in enumerate(rows, start=2):
        body = "".join(cell(i, row_number, value) for i, value in enumerate(values))
        lines.append(f'<row r="{row_number}">{body}</row>')
    lines.extend(["</sheetData>", "</worksheet>"])
    return "\n".join(lines)


def write_xlsx(path: Path, inventory: dict[str, Any]) -> None:
    import zipfile

    headers = [
        "letter_id",
        "mention_index",
        "split",
        "family",
        "gold_key",
        "gold_template",
        "gold_subtype",
        "cui_phrase",
        "official_raw_text",
        "recovered_letter_span",
        "span_recovery_method",
        "source_construction",
        "official_reference_construction",
        "transform",
        "reference_status",
        "cui",
    ]
    body = [
        [
            row["letter_id"],
            row["mention_index"],
            row["split"],
            row["family"],
            row["gold_key"],
            row["gold_template"],
            row["gold_subtype"],
            row["cui_phrase"],
            row["official_raw_text"],
            row["recovered_letter_span"],
            row["span_recovery_method"],
            row["source_construction"],
            row["official_reference_construction"],
            row["transform"],
            row["reference_status"],
            row["cui"],
        ]
        for row in inventory["rows"]
    ]
    construction_headers = [
        "source_construction",
        "family_scope",
        "n_mentions",
        "share",
        "definition",
    ]
    n_rows = inventory["summary"]["n_mentions"]
    construction_rows = []
    family_scope = {
        "front_matter_diagnosis_line": "Diagnosis",
        "truncation_or_offset_drift": "Diagnosis",
        "spelling_or_typo_variant": "Diagnosis",
        "hedged_or_probable_label": "Diagnosis",
        "legacy_or_synonym_term": "Diagnosis",
        "laterality_or_site_qualifier": "Diagnosis",
        "canonical_concept_phrase": "Diagnosis",
        "possessive_or_anaphoric": "Diagnosis",
        "seizure_type_as_diagnosis": "Diagnosis",
        "umbrella_or_inventory_mismatch": "Diagnosis",
        "cluster_mention": "SeizureFrequency",
        "seizure_free_phrase": "SeizureFrequency",
        "qualitative_change": "SeizureFrequency",
        "numeric_cadence": "SeizureFrequency",
        "count_in_named_window": "SeizureFrequency",
        "type_token_only": "SeizureFrequency",
        "titration_or_future_plan": "Prescription",
        "rescue_or_prn": "Prescription",
        "brand_name": "Prescription",
        "split_daily_dose": "Prescription",
        "complete_regimen_line": "Prescription",
        "drug_name_only_span": "Prescription",
        "eeg_type_named": "Investigations",
        "modality_plus_result": "Investigations",
        "finding_in_prose": "Investigations",
        "dated_investigation": "Investigations",
        "modality_token": "Investigations",
        "other_paraphrase": "all families",
    }
    counts = inventory["summary"]["construction_counts"]
    for name, count in Counter(counts).most_common():
        construction_rows.append(
            [
                name,
                family_scope.get(name, ""),
                count,
                round(count / n_rows, 4),
                inventory["construction_definitions"].get(name, ""),
            ]
        )

    workbook = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets>
<sheet name="mentions" sheetId="1" r:id="rId1"/>
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
    serializable = dict(inventory)
    payload = json.dumps(serializable, indent=2, ensure_ascii=True) + "\n"
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
        / f"exectv2_gold_phrase_variant_inventory_{DATE_STAMP}.json",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=(
            REPO_ROOT
            / "docs"
            / "research"
            / "paper"
            / "exect_gold_phrase_variant_catalog_2026-08-13.md"
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
            / "exect_gold_phrase_variants_2026-08-13.xlsx"
        ),
    )
    args = parser.parse_args()
    inventory = build_inventory()
    write_outputs(inventory, args.output, args.catalog, args.workbook)
    summary = inventory["summary"]
    print(f"wrote {args.output}")
    print(f"wrote {args.catalog}")
    print(f"wrote {args.workbook}")
    print(
        f"letters={summary['n_letters']} mentions={summary['n_mentions']} "
        f"keys={summary['n_unique_gold_keys']} "
        f"spans={summary['n_unique_official_spans']} "
        f"templates={summary['n_unique_templates']}"
    )
    print("families:")
    for name, n in Counter(summary["family_counts"]).most_common():
        print(f"  {n:4d}  {name}")
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
