"""Deterministic prescription extraction rules."""

from __future__ import annotations

import re
from collections.abc import Sequence

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    PRESCRIPTION_CONCEPT_BY_PHRASE,
    PRESCRIPTION_SURFACE_FORMS,
    BenchmarkConcept,
    attach_benchmark_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.drug_lexicon import (
    DRUG_SURFACE_ALIASES,
    EXTERNAL_ASM_BRAND_ALIASES,
    EXTERNAL_ASM_GENERICS,
    resolve_drug_surface,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import PRESCRIPTION
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase

from ..mention_identity import match_span
from ..rule_metadata import Portability, RuleGroup
from .common import _owner, _right_context_until_separator
from .text import _frequency_from_text

_MEDICATION_LEXICON = PRESCRIPTION_CONCEPT_BY_PHRASE
_MEDICATION_PATTERN = re.compile(
    r"\b("
    + "|".join(
        re.escape(name)
        for name in sorted(
            [*PRESCRIPTION_SURFACE_FORMS, *DRUG_SURFACE_ALIASES],
            key=len,
            reverse=True,
        )
    )
    + r")\b",
    re.IGNORECASE,
)
_DOSE_PATTERN = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(mg|mgs|mgms|milligrams?|milligrammes?|g|grams?)\b",
    re.IGNORECASE,
)
_PRESCRIPTION_NEGATIVE_CONTEXT = re.compile(
    r"\b(?:previously|prior|past|trial(?:s|led)?|tried|not\s+previously\s+taken|"
    r"has\s+not\s+previously\s+taken|discontinued|stopped|withdrawn|allerg(?:y|ic))\b",
    re.IGNORECASE,
)
_PRESCRIPTION_PLAN_CONTEXT = re.compile(
    r"\b(?:commence|start(?:ing)?|increase|increasing|titrate|titration|reduce|"
    r"reducing|target\s+dose|consider|future|option|every\s+(?:two\s+)?weeks|"
    r"every\s+fortnight|until)\b",
    re.IGNORECASE,
)
_PRESCRIPTION_FUTURE_LEFT_CONTEXT = re.compile(
    r"\b(?:should\s+be\s+increased|so\s+that\s+(?:he|she|they)\s+is\s+on|"
    r"suggest\s+adding|suggested\s+adding|suggest\s+introducing|"
    r"suggested\s+introducing|to\s+start\s+treatment\s+with|"
    r"to\s+start\b|commence\s+(?:him|her|them)?\s*(?:on|of)|"
    r"suggest\s+we\s+start|suggest\s+maybe|"
    r"please\s+(?:can\s+you\s+)?prescribe|"
    r"Plan\s*:\s*Week|\bWeek\s+\d+\s*(?:&|and)\s*(?:Continue|Week))\b",
    re.IGNORECASE,
)
_PRESCRIPTION_WEIGHT_BASED_CONTEXT = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mg|mgs|mgms|g|grams?)\s*/?\s*kg(?:\s*/?\s*day)?\b",
    re.IGNORECASE,
)
_PRESCRIPTION_ACTIVE_CONTEXT = re.compile(
    r"\b(?:current|currently|medications?\b:?|antiepileptic|anti-epileptic|"
    r"anti\s+convulsant|anticonvulsant|taking|takes|on|prescribed|regimen|"
    r"continue|remains\s+on|is\s+on|she\s+is\s+on|he\s+is\s+on|rescue)\b",
    re.IGNORECASE,
)
_DOSE_CONNECTOR = re.compile(r"(?:[/,+&]|\band\b|\bplus\b|\bthen\b)\s*$", re.IGNORECASE)
_TRAILING_CONNECTOR = re.compile(r"\s+(?:and|as well as|plus)$", re.IGNORECASE)
_LEFT_DOSE_BEFORE_MEDICATION = re.compile(
    r"(?P<dose>\b\d+(?:\.\d+)?\s*(?:mg|mgs|mgms|milligrams?|milligrammes?|g|grams?))"
    r"(?:\s+(?:bd|b\.d\.|twice\s+(?:a\s+)?day|twice\s+daily|od|o\.d\.|"
    r"once\s+(?:a\s+)?day|once\s+daily|daily|mane|nocte|nightly|am|pm))?"
    r"\s+of\s+$",
    re.IGNORECASE,
)


def _extract_prescriptions(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    medication_matches = tuple(_MEDICATION_PATTERN.finditer(text))
    for index, match in enumerate(medication_matches):
        if _is_parenthetical_alias(text, match):
            continue
        surface = match.group(1)
        entry = _MEDICATION_LEXICON[resolve_drug_surface(surface)]
        evidence = _prescription_context(text, match, medication_matches[index + 1 :])
        if not _is_prescription_context(text, match, evidence):
            continue
        for attrs, phrase_text in _prescription_attribute_sets(surface, entry, evidence):
            mentions.append(
                PredictedMention(
                    entity=PRESCRIPTION.name,
                    text=phrase_text,
                    attributes=attrs,
                    evidence=evidence,
                    evidence_span=match_span(match),
                    component_owner=_owner(
                        "prescription_regimen",
                        RuleGroup.ANCHOR_PHRASE,
                        Portability.CLINICAL_EPILEPSY,
                        Portability.BENCHMARK_FORMAT,
                    ),
                )
            )
    return tuple(mentions)


def _prescription_attribute_sets(
    surface: str,
    entry: BenchmarkConcept,
    evidence: str,
) -> tuple[tuple[dict[str, str], str], ...]:
    dose_matches = tuple(_DOSE_PATTERN.finditer(evidence))
    base_attrs = attach_benchmark_concept({}, entry, canonical_key="DrugName")
    rescue_range = re.search(r"\b\d+\s*-\s*\d+\s*(?:mg|mgs|mgms)\b", evidence, re.IGNORECASE)
    if rescue_range and _frequency_from_text(evidence) == "As_Required":
        return (({**base_attrs, "Frequency": "As_Required"}, surface),)
    if not dose_matches:
        frequency = _frequency_from_text(evidence)
        if frequency == "As_Required":
            if _future_plan_before_medication(evidence):
                return ()
            return (({**base_attrs, "Frequency": frequency}, surface),)
        return ()

    slash_schedule_default = "/" in evidence and len(dose_matches) > 1

    items: list[tuple[dict[str, str], str]] = []
    for dose_index, dose in enumerate(dose_matches):
        if evidence[dose.end() : dose.end() + 4].lower().startswith("/kg"):
            continue
        local_right = (
            dose_matches[dose_index + 1].start()
            if dose_index + 1 < len(dose_matches)
            else len(evidence)
        )
        # P7 (2026-07-02): scoped to this dose's own clause (its match start
        # through the next dose, or end of evidence). The prior whole-evidence
        # search let a weight-based restatement of ANY dose (e.g. a trailing
        # "(8mg/kg/day)" total) silently drop every OTHER, unrelated current
        # dose in the same multi-dose evidence blob before scoring ever saw
        # them. ``search(evidence, pos, endpos)`` (not a sliced substring) so
        # ``\b`` still sees the real surrounding characters at the window edge.
        if _PRESCRIPTION_WEIGHT_BASED_CONTEXT.search(evidence, dose.start(), local_right):
            continue
        between = evidence[dose.end() : local_right]
        prior_dose_region = evidence[dose_matches[0].end() : dose.start()]
        if dose_index > 0 and _PRESCRIPTION_PLAN_CONTEXT.search(prior_dose_region):
            break
        if dose_index > 0 and not _is_continuing_same_medication_dose(evidence, dose.start()):
            break
        frequency = (
            _frequency_from_text(between)
            or _frequency_from_text(evidence[dose.end() :])
            or ("1" if slash_schedule_default else None)
        )
        if not frequency:
            continue
        unit = _canonical_dose_unit(dose.group(2))
        attrs = {
            **base_attrs,
            "DrugDose": dose.group(1),
            "DoseUnit": unit,
            "Frequency": frequency,
        }
        phrase_text = _trim_planned_regimen_tail(
            _dose_phrase_text(surface, evidence, dose, between)
        )
        if _is_planned_dose_phrase(phrase_text):
            continue
        items.append((attrs, phrase_text))

    return tuple(items)


def _dose_phrase_text(
    surface: str,
    evidence: str,
    dose: re.Match[str],
    between: str,
) -> str:
    left = evidence[: dose.start()]
    if normalize_phrase(surface) in normalize_phrase(left):
        start = max(0, left.lower().rfind(surface.lower()))
    else:
        start = 0
    end = dose.end() + len(between)
    return evidence[start:end].strip(" ,;")


def _trim_planned_regimen_tail(text: str) -> str:
    trimmed = re.split(
        r"\s*(?:\((?:to|please|increase|increasing|reduce|reducing)\b|"
        r"\bincreasing\s+by\b|\breducing\s+by\b)",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    return trimmed.strip(" ,;")


def _canonical_dose_unit(unit: str) -> str:
    lowered = unit.lower()
    if lowered.startswith("g"):
        return "g"
    return "mg"


def _is_continuing_same_medication_dose(evidence: str, dose_start: int) -> bool:
    between = evidence[:dose_start]
    last_med = max(
        (match.start() for match in _MEDICATION_PATTERN.finditer(between)),
        default=-1,
    )
    connector_region = between[last_med + 1 if last_med != -1 else 0 :]
    return bool(
        _DOSE_CONNECTOR.search(connector_region)
        or "/" in connector_region[-16:]
        or _frequency_from_text(connector_region[-32:]) is not None
    )


def _is_planned_dose_phrase(phrase_text: str) -> bool:
    lowered = phrase_text.lower()
    if re.search(r"\b\w+\s+to\s+\d+(?:\.\d+)?\s*(?:mg|mgs|mgms|g)\b", lowered):
        return True
    if re.search(r"\bshould\s+be\s+\d+(?:\.\d+)?\s*(?:mg|mgs|mgms|g)\b", lowered):
        return True
    if re.search(r"\b(?:is\s+)?increased\s+to\s+\d+(?:\.\d+)?\s*(?:mg|mgs|mgms|g)\b", lowered):
        return True
    if "increasing after" in lowered or "in steps of" in lowered or "as per plan" in lowered:
        return True
    if "increasing by" in lowered and "," not in lowered:
        return True
    return False


def _is_parenthetical_alias(text: str, match: re.Match[str]) -> bool:
    left = text[max(0, match.start() - 24) : match.start()]
    right = text[match.end() : match.end() + 2]
    if "(" not in left or ")" not in right:
        return False
    return bool(_MEDICATION_PATTERN.search(left))


def _prescription_context(
    text: str,
    match: re.Match[str],
    following_matches: Sequence[re.Match[str]],
) -> str:
    start = _prescription_context_start(text, match)
    tail = text[start:]
    stop = len(tail)
    for separator in ("\n\n", "\n-", "\n", "."):
        idx = tail.find(separator)
        if idx != -1:
            stop = min(stop, idx)
    for next_match in following_matches:
        if next_match.start() <= match.end():
            continue
        if _is_parenthetical_alias(text, next_match):
            continue
        stop = min(stop, next_match.start() - start)
        break
    return _TRAILING_CONNECTOR.sub("", tail[:stop].strip(" ,;")).strip(" ,;")


def _prescription_context_start(text: str, match: re.Match[str]) -> int:
    left = text[max(0, match.start() - 50) : match.start()]
    dose_before = _LEFT_DOSE_BEFORE_MEDICATION.search(left)
    if dose_before:
        return match.start() - (len(left) - dose_before.start("dose"))
    return match.start()


def _is_prescription_context(text: str, match: re.Match[str], evidence: str) -> bool:
    local_left = text[max(0, match.start() - 180) : match.start()]
    sentence_left = text[max(0, text.rfind(".", 0, match.start()) + 1) : match.start()]
    if _PRESCRIPTION_NEGATIVE_CONTEXT.search(sentence_left) and not _active_after_negative_context(
        sentence_left
    ):
        return False
    has_complete_regimen = bool(
        _DOSE_PATTERN.search(evidence)
        and (
            _frequency_from_text(evidence)
            or ("/" in evidence and len(_DOSE_PATTERN.findall(evidence)) > 1)
        )
    )
    has_prn_rescue = _frequency_from_text(evidence) == "As_Required"
    if not (has_complete_regimen or has_prn_rescue):
        return False

    first_dose = _DOSE_PATTERN.search(evidence)
    pre_dose = evidence[: first_dose.start()] if first_dose else evidence
    planned_left = re.search(
        r"\b(?:start(?:ing)?|commence|increase|increasing|titrate|reduce|reducing|"
        r"target|maintenance\s+of|to|by)\s*$",
        local_left,
        re.IGNORECASE,
    )
    planned_prefix = re.search(
        r"\b(?:starting\s+at|commence|start|increase\s+to|titrate|target\s+dose|by)\b",
        pre_dose,
        re.IGNORECASE,
    )
    planned_increment = re.search(
        r"\b(?:increasing|reduce|reducing)\s+by\b|\bevery\s+(?:two\s+)?weeks\b|\bevery\s+fortnight\b",
        evidence,
        re.IGNORECASE,
    )
    active_left = _PRESCRIPTION_ACTIVE_CONTEXT.search(local_left)
    if _PRESCRIPTION_FUTURE_LEFT_CONTEXT.search(local_left):
        return False
    if planned_prefix or planned_left:
        return False
    if planned_increment and not active_left:
        return False
    return True


def _active_after_negative_context(text: str) -> bool:
    negative = list(_PRESCRIPTION_NEGATIVE_CONTEXT.finditer(text))
    if not negative:
        return False
    return _PRESCRIPTION_ACTIVE_CONTEXT.search(text[negative[-1].end() :]) is not None


def _future_plan_before_medication(evidence: str) -> bool:
    first_med = _MEDICATION_PATTERN.search(evidence)
    if first_med is None:
        return False
    return _PRESCRIPTION_FUTURE_LEFT_CONTEXT.search(evidence[: first_med.start()]) is not None


# --- Recall-first prescription recogniser (2026-08-27 restructure) ---

_EXTERNAL_ASM_PATTERN = re.compile(
    r"\b("
    + "|".join(
        re.escape(name)
        for name in sorted(
            [*EXTERNAL_ASM_GENERICS, *EXTERNAL_ASM_BRAND_ALIASES],
            key=len,
            reverse=True,
        )
    )
    + r")\b",
    re.IGNORECASE,
)
_RESCUE_CONTEXT = re.compile(r"\bbuccal\b|\brescue\b", re.IGNORECASE)
_BULLET_LINE = re.compile(r"^\s*(?:[•\-*\u2022]|\d+\.)\s*")
_KNOWN_DRUG_VOCABULARY: tuple[str, ...] = tuple(
    sorted(
        {
            *(name.lower() for name in PRESCRIPTION_SURFACE_FORMS if " " not in name),
            *EXTERNAL_ASM_GENERICS,
        }
    )
)
_TYPO_TOKEN = re.compile(r"\b[a-z]{7,}\b", re.IGNORECASE)


def _within_edit_distance_one(word: str, target: str) -> bool:
    if word == target:
        return True
    len_diff = len(word) - len(target)
    if abs(len_diff) > 1:
        return False
    if len_diff == 0:
        return sum(a != b for a, b in zip(word, target, strict=True)) == 1
    shorter, longer = (word, target) if len_diff < 0 else (target, word)
    for index in range(len(longer)):
        if shorter == longer[:index] + longer[index + 1 :]:
            return True
    return False


def _typo_drug_matches(text: str) -> tuple[tuple[re.Match[str], str], ...]:
    """Word tokens one edit away from a known ASM generic (recall-first)."""

    matched: list[tuple[re.Match[str], str]] = []
    for token_match in _TYPO_TOKEN.finditer(text):
        word = token_match.group(0).lower()
        if word in _KNOWN_DRUG_VOCABULARY:
            continue
        for target in _KNOWN_DRUG_VOCABULARY:
            if _within_edit_distance_one(word, target):
                matched.append((token_match, target))
                break
    return tuple(matched)


def _line_bounds(text: str, position: int) -> tuple[int, int]:
    start = text.rfind("\n", 0, position) + 1
    end = text.find("\n", position)
    return start, end if end != -1 else len(text)


def _recall_first_rx_attrs(surface: str) -> dict[str, str]:
    key = resolve_drug_surface(surface)
    key = EXTERNAL_ASM_BRAND_ALIASES.get(key, key)
    entry = _MEDICATION_LEXICON.get(key)
    if entry is not None:
        return attach_benchmark_concept({}, entry, canonical_key="DrugName")
    return {"DrugName": key.replace(" ", "-")}


def recall_first_rx_candidates(note_text: str):
    """Recall-first prescriptions the gated direct path misses.

    Relaxed line-scoped parse for every known, external, or typo-matched
    drug surface without a direct mention: dose plus frequency anywhere on
    the line, a list-item default frequency of once daily, and a rescue
    ``As_Required`` for dose-less buccal/rescue mentions. No plan/negation
    context gates; Select owns precision.
    """

    from ..recognise_ledger import RX_RECALL_EXPANSION, RecogniseCandidate

    covered = {
        mention.attributes.get("DrugName")
        for mention in _extract_prescriptions(note_text)
    }
    seen: set[str] = {name for name in covered if name}
    candidates: list[RecogniseCandidate] = []

    drug_matches: list[tuple[re.Match[str], str]] = [
        (match, match.group(1))
        for match in (*_MEDICATION_PATTERN.finditer(note_text),
                      *_EXTERNAL_ASM_PATTERN.finditer(note_text))
        if not _is_parenthetical_alias(note_text, match)
    ]
    drug_matches.extend(_typo_drug_matches(note_text))
    drug_starts = sorted(match.start() for match, _surface in drug_matches)

    for match, surface in drug_matches:
        base_attrs = _recall_first_rx_attrs(surface)
        drug = base_attrs["DrugName"]
        if drug in seen:
            continue
        line_start, line_end = _line_bounds(note_text, match.start())
        line = note_text[line_start:line_end]
        region_end = min(
            (start for start in drug_starts if start > match.end() and start < line_end),
            default=line_end,
        )
        region = note_text[match.end() : region_end]
        dose = _DOSE_PATTERN.search(region)
        frequency = _frequency_from_text(region)
        attrs: dict[str, str] | None = None
        if dose is not None and frequency:
            attrs = {
                **base_attrs,
                "DrugDose": dose.group(1),
                "DoseUnit": _canonical_dose_unit(dose.group(2)),
                "Frequency": frequency,
            }
        elif dose is not None and _BULLET_LINE.match(line):
            attrs = {
                **base_attrs,
                "DrugDose": dose.group(1),
                "DoseUnit": _canonical_dose_unit(dose.group(2)),
                "Frequency": "1",
            }
        elif dose is None and _RESCUE_CONTEXT.search(line):
            attrs = {**base_attrs, "Frequency": "As_Required"}
        if attrs is None:
            continue
        seen.add(drug)
        candidates.append(
            RecogniseCandidate(
                mention=PredictedMention(
                    entity=PRESCRIPTION.name,
                    text=line.strip(),
                    attributes=attrs,
                    evidence=line.strip(),
                    evidence_span=match_span(match),
                    component_owner=_owner(
                        "prescription_recall_expansion",
                        RuleGroup.ANCHOR_PHRASE,
                        Portability.CLINICAL_EPILEPSY,
                    ),
                ),
                candidate_class=RX_RECALL_EXPANSION,
                rule_id="recognise.rx_recall_expansion",
            )
        )
    return tuple(candidates)


def _legacy_extract_prescriptions(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    for match in _MEDICATION_PATTERN.finditer(text):
        surface = match.group(1)
        entry = _MEDICATION_LEXICON[normalize_phrase(surface)]
        evidence = _right_context_until_separator(text, match.start())
        attrs = attach_benchmark_concept({}, entry, canonical_key="DrugName")
        dose = _DOSE_PATTERN.search(evidence)
        if dose:
            attrs["DrugDose"] = dose.group(1)
            attrs["DoseUnit"] = _canonical_dose_unit(dose.group(2))
        frequency = _frequency_from_text(evidence)
        if frequency:
            attrs["Frequency"] = frequency
        phrase_text = _prescription_phrase_text(surface, evidence, attrs)
        mentions.append(
            PredictedMention(
                entity=PRESCRIPTION.name,
                text=phrase_text,
                attributes=attrs,
                evidence=evidence,
                component_owner=_owner(
                    "prescription_medication",
                    RuleGroup.ANCHOR_PHRASE,
                    Portability.CLINICAL_EPILEPSY,
                    Portability.BENCHMARK_FORMAT,
                ),
            )
        )
    return tuple(mentions)


def _prescription_phrase_text(surface: str, evidence: str, attrs: dict[str, str]) -> str:
    if "DrugDose" in attrs or "Frequency" in attrs:
        return evidence
    return surface
