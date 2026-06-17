"""First deterministic all-entity baseline for ExECTv2.

This module composes the mature SeizureFrequency deterministic extractor with
high-precision rules for the first structured entities named in the GPT-first
strategy: Prescription, Investigations, and Diagnosis. It is intentionally a
transparent floor and candidate source, not a benchmark-complete solution.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    DIAGNOSIS_SURFACE_FORMS,
    PRESCRIPTION_CONCEPT_BY_PHRASE,
    PRESCRIPTION_SURFACE_FORMS,
    BenchmarkConcept,
    attach_benchmark_concept,
    diagnosis_concept,
    investigation_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    SEIZURE_FREQUENCY,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import normalize_phrase

from .pipeline import extract_seizure_frequency
from .rule_metadata import Portability, RuleGroup

ACTIVE_DETERMINISTIC_ENTITIES: tuple[str, ...] = (
    PRESCRIPTION.name,
    INVESTIGATIONS.name,
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY,
)

_OWNER_PREFIX = "deterministic"
_MEDICATION_LEXICON = PRESCRIPTION_CONCEPT_BY_PHRASE
_MEDICATION_PATTERN = re.compile(
    r"\b("
    + "|".join(
        re.escape(name) for name in sorted(PRESCRIPTION_SURFACE_FORMS, key=len, reverse=True)
    )
    + r")\b",
    re.IGNORECASE,
)
_DOSE_PATTERN = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(mg|mgs|mgms|milligrams?|milligrammes?|g|grams?)\b",
    re.IGNORECASE,
)
_FREQUENCY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"\b(?:prn|p\.r\.n\.|as\s+required|when\s+required|as\s+needed|"
            r"rescue|for\s+seizure\s+clusters?)\b",
            re.IGNORECASE,
        ),
        "As_Required",
    ),
    (
        re.compile(
            r"\b(?:bd|b\.d\.|twice\s+(?:a\s+)?day|twice\s+daily|twice\s+today)\b",
            re.IGNORECASE,
        ),
        "2",
    ),
    (
        re.compile(
            r"\b(?:od|o\.d\.|once\s+(?:a\s+)?day|once\s+daily|daily|mane|nocte|"
            r"nightly|morning|afternoon|evening|am|pm|at\s+night|"
            r"in\s+the\s+(?:morning|afternoon|night|evening)|on|nokte)\b",
            re.IGNORECASE,
        ),
        "1",
    ),
    (re.compile(r"\b(?:tds|t\.d\.s\.|tid|three\s+times\s+(?:a\s+)?day)\b", re.IGNORECASE), "3"),
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
_PRESCRIPTION_ACTIVE_CONTEXT = re.compile(
    r"\b(?:current|currently|medications?:|antiepileptic|anti-epileptic|"
    r"anti\s+convulsant|anticonvulsant|taking|takes|on|prescribed|regimen|"
    r"continue|remains\s+on|is\s+on|she\s+is\s+on|he\s+is\s+on|rescue)\b",
    re.IGNORECASE,
)
_DOSE_CONNECTOR = re.compile(r"(?:[/,+&]|\band\b|\bplus\b|\bthen\b)\s*$", re.IGNORECASE)
_TRAILING_CONNECTOR = re.compile(r"\s+(?:and|as well as|plus)$", re.IGNORECASE)
_LEFT_DOSE_BEFORE_MEDICATION = re.compile(
    r"(?P<dose>\b\d+(?:\.\d+)?\s*(?:mg|mgs|mgms|milligrams?|milligrammes?|g|grams?))"
    r"\s+of\s+$",
    re.IGNORECASE,
)

_DIAGNOSIS_PATTERN = re.compile(
    r"\b("
    + "|".join(re.escape(name) for name in sorted(DIAGNOSIS_SURFACE_FORMS, key=len, reverse=True))
    + r")\b",
    re.IGNORECASE,
)

_INVESTIGATION_PATTERN = re.compile(r"\b(EEGs?|MRI|CT)(?:\s+(?:brain|scan|head))?\b", re.IGNORECASE)
_RESULT_NORMAL = re.compile(r"\b(?:normal|negative|unremarkable)\b", re.IGNORECASE)
_RESULT_ABNORMAL = re.compile(
    r"\b(?:abnormal|abnormalities|lesion|infarct|sclerosis|dysplasia)\b",
    re.IGNORECASE,
)
_EEG_TYPE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bsleep\s*deprived\b", re.IGNORECASE), "SleepDeprived"),
    (re.compile(r"\bvideo\s*telemetry\b", re.IGNORECASE), "VideoTelemetry"),
)

def extract_deterministic_all9(letter: ExectLetter) -> PredictedLetter:
    """Extract the active deterministic baseline entities from one letter."""

    sf_prediction = extract_seizure_frequency(letter)
    mentions = (
        *_extract_diagnoses(letter.note_text),
        *_extract_investigations(letter.note_text),
        *_extract_prescriptions(letter.note_text),
        *sf_prediction.mentions,
    )
    mentions = _dedupe_mentions(mentions)
    counts = {
        entity: sum(1 for mention in mentions if mention.entity == entity)
        for entity in ACTIVE_DETERMINISTIC_ENTITIES
    }
    return PredictedLetter(
        letter_id=letter.letter_id,
        mentions=mentions,
        diagnostics={
            "architecture_track": "rules_only",
            "rule_set": "deterministic_all9_v0_active_structured_plus_sf",
            "active_entities": ACTIVE_DETERMINISTIC_ENTITIES,
            "entity_counts": counts,
            "sf_diagnostics": sf_prediction.diagnostics,
            "rule_families": _rule_family_summary(),
        },
    )


def run_all9_on_letters(letters: Sequence[ExectLetter]) -> list[PredictedLetter]:
    """Run the deterministic active all-entity baseline over letters."""

    return [extract_deterministic_all9(letter) for letter in letters]


def _extract_prescriptions(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    medication_matches = tuple(_MEDICATION_PATTERN.finditer(text))
    for index, match in enumerate(medication_matches):
        if _is_parenthetical_alias(text, match):
            continue
        surface = match.group(1)
        entry = _MEDICATION_LEXICON[normalize_phrase(surface)]
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
        phrase_text = _dose_phrase_text(surface, evidence, dose, between)
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
    if _PRESCRIPTION_NEGATIVE_CONTEXT.search(sentence_left):
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
    if planned_prefix or planned_left:
        return False
    if planned_increment and not active_left:
        return False
    return True


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


def _extract_investigations(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    for match in _INVESTIGATION_PATTERN.finditer(text):
        modality = _canonical_modality(match.group(1))
        evidence = _sentence_window(text, match.start(), match.end())
        result = _investigation_result(evidence)
        attrs = {f"{modality}_Performed": "Yes"}
        if result:
            attrs[f"{modality}_Results"] = result
        if modality == "EEG":
            eeg_type = _eeg_type(evidence)
            if eeg_type:
                attrs["EEG_Type"] = eeg_type
        concept = investigation_concept(modality, result)
        if concept:
            attrs = attach_benchmark_concept(attrs, concept)
        mentions.append(
            PredictedMention(
                entity=INVESTIGATIONS.name,
                text=modality,
                attributes=attrs,
                evidence=evidence,
                component_owner=_owner(
                    "investigation_result",
                    RuleGroup.ANCHOR_PHRASE,
                    Portability.CLINICAL_EPILEPSY,
                    Portability.BENCHMARK_FORMAT,
                ),
            )
        )
    return tuple(mentions)


def _extract_diagnoses(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    occupied: list[tuple[int, int]] = []
    matches = sorted(
        _DIAGNOSIS_PATTERN.finditer(text),
        key=lambda m: m.end() - m.start(),
        reverse=True,
    )
    for match in matches:
        if any(_overlaps(match.span(), span) for span in occupied):
            continue
        phrase = match.group(1)
        concept = diagnosis_concept(phrase)
        if concept is None:
            continue
        attrs = {
            "DiagCategory": concept.canonical,
            "Certainty": "5",
            "Negation": "Affirmed",
        }
        attrs = attach_benchmark_concept(attrs, concept)
        mentions.append(
            PredictedMention(
                entity=DIAGNOSIS.name,
                text=phrase,
                attributes=attrs,
                evidence=phrase,
                component_owner=_owner(
                    "deterministic_diagnosis_phrase",
                    RuleGroup.ANCHOR_PHRASE,
                    Portability.CLINICAL_EPILEPSY,
                    Portability.BENCHMARK_FORMAT,
                ),
            )
        )
        occupied.append(match.span())
    mentions.sort(key=lambda mention: text.lower().find(mention.evidence.lower()))
    return tuple(mentions)


def _frequency_from_text(text: str) -> str | None:
    for pattern, value in _FREQUENCY_PATTERNS:
        if pattern.search(text):
            return value
    return None


def _investigation_result(text: str) -> str | None:
    if _RESULT_ABNORMAL.search(text):
        return "Abnormal"
    if _RESULT_NORMAL.search(text):
        return "Normal"
    return None


def _eeg_type(text: str) -> str | None:
    for pattern, value in _EEG_TYPE_PATTERNS:
        if pattern.search(text):
            return value
    return None


def _canonical_modality(surface: str) -> str:
    upper = surface.upper()
    if upper.startswith("EEG"):
        return "EEG"
    if upper.startswith("MRI"):
        return "MRI"
    return "CT"


def _right_context_until_separator(text: str, start: int) -> str:
    tail = text[start:]
    stop = len(tail)
    for separator in (" and ", ";", "\n", "."):
        idx = tail.find(separator)
        if idx != -1:
            stop = min(stop, idx)
    return tail[:stop].strip(" ,;")


def _sentence_window(text: str, start: int, end: int) -> str:
    left = max(text.rfind(".", 0, start), text.rfind("\n", 0, start))
    right_candidates = [idx for idx in (text.find(".", end), text.find("\n", end)) if idx != -1]
    right = min(right_candidates) if right_candidates else len(text)
    return text[left + 1 : right].strip(" ,;")


def _dedupe_mentions(mentions: Iterable[PredictedMention]) -> tuple[PredictedMention, ...]:
    seen: set[tuple[str, str, tuple[tuple[str, str], ...]]] = set()
    deduped: list[PredictedMention] = []
    for mention in mentions:
        key = (
            mention.entity,
            normalize_phrase(mention.text),
            tuple(sorted(dict(mention.attributes).items())),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(mention)
    return tuple(deduped)


def _overlaps(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] < right[1] and right[0] < left[1]


def _owner(
    rule_id: str,
    group: RuleGroup,
    portability: Portability,
    *extra_portability: Portability,
) -> str:
    parts = [_OWNER_PREFIX, rule_id, group.value, portability.value]
    parts.extend(item.value for item in extra_portability)
    return ":".join(parts)


def _rule_family_summary() -> dict[str, dict[str, str]]:
    return {
        "prescription_medication": {
            "entity": PRESCRIPTION.name,
            "group": RuleGroup.ANCHOR_PHRASE.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
            "phrase_scope_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "investigation_result": {
            "entity": INVESTIGATIONS.name,
            "group": RuleGroup.ANCHOR_PHRASE.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "diagnosis_phrase": {
            "entity": DIAGNOSIS.name,
            "group": RuleGroup.ANCHOR_PHRASE.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "seizure_frequency": {
            "entity": SEIZURE_FREQUENCY,
            "group": "see deterministic.pipeline diagnostics",
            "portability": Portability.SEIZURE_FREQUENCY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
        },
    }
