"""Deterministic investigations extraction rules.

Standalone rules-only Investigations recovers completed EEG / MRI / CT
facts with a Normal / Abnormal / Unknown result. The scorer's clinical
headline is (modality, performed, result). Official gold spans are often
just the modality token; the result lives in nearby prose (ExECT List 9).

This extractor therefore:
- binds a result to the nearest modality in the sentence
- shares a trailing result across a coordinated pair ("MRI and EEG have
  been normal")
- reads an anaphoric next sentence ("MRI in 2016. This does show...")
- drops planned / requested tests
- treats negated finding language as Normal
- emits only mentions that have a result
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    attach_benchmark_concept,
    investigation_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import INVESTIGATIONS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)

from ..mention_identity import match_span
from ..rule_metadata import Portability, RuleGroup
from .common import _canonical_modality, _owner, _sentence_window

_INVESTIGATION_PATTERN = re.compile(
    r"\b(?:VEEG|video[-\s]+EEG|EEGs?|MRI|MR\s+brain|CT)(?:\s+(?:brain|scan|head))?\b",
    re.IGNORECASE,
)
_PLANNED = re.compile(
    r"\b(?:arrang(?:e|ed|ing)|request(?:ed|ing)?|await(?:ed|ing)|pending|"
    r"will\s+(?:arrange|request|get|repeat|organise|organize)|"
    r"to\s+(?:arrange|request|get|repeat)|"
    r"repeat\s+(?:MRI|EEG|CT)|with\s+the\s+results)\b",
    re.IGNORECASE,
)
_COMPLETED = re.compile(
    r"\b(?:showed|shown|shows|showing|did\s+show|has\s+shown|have\s+shown|"
    r"has\s+been|have\s+been|had\s+been|was|were|reported|"
    r"performed|last\s+(?:MRI|EEG|CT)|previous)\b|"
    r"\b(?:19|20)\d{2}\b",
    re.IGNORECASE,
)
_UNKNOWN = re.compile(
    r"\b(?:do\s+not\s+have|don't\s+have|not\s+have)\b.{0,80}\b(?:results?|reports?)\b|"
    r"\b(?:results?|reports?)\b.{0,80}\b(?:do\s+not\s+have|don't\s+have|"
    r"not\s+available|unavailable|unknown|pending)\b|"
    r"\b(?:have\s+not\s+seen|has\s+not\s+seen|not\s+seen)\b.{0,40}\b(?:results?|reports?)\b|"
    r"\b(?:not\s+available|unavailable|unknown)\b",
    re.IGNORECASE,
)
_NORMAL = re.compile(
    r"\b(?:normal|negative|unremarkable|"
    r"no\s+significant\s+findings|no\s+changes|"
    r"did\s+not\s+capture\s+any\s+events|"
    r"did\s+not\s+identify\s+any\s+acute\s+pathology|"
    r"epileptic\s+activity\s+was\s+not\s+seen|"
    r"did\s+not\s+show\s+any\s+epileptic(?:\s+activity)?|"
    r"normal\s+apart\s+from|"
    r"no\s+epileptiform|no\s+EEG\s+changes|"
    r"failed\s+to\s+alter|"
    r"(?:non[-\s]*epileptic|psychogenic|dissociative|functional|pnes|nead).{0,60}"
    r"(?:confirmed|shown)\s+(?:on|by|in)\s+(?:an?\s+)?(?:EEG|video[-\s]*EEG|VEEG))\b",
    re.IGNORECASE,
)
# List 9 finding language, minus standalone words that fire on ordinary clinic
# prose (epileptic, sharp, irregular, unstable).
_ABNORMAL = re.compile(
    r"\b(?:abnormal(?:ities|ity)?|abnormal\s+signal|signal\s+abnormality|"
    r"lesions?|infarct(?:s|ion)?|sclerosis|dysplasia|"
    r"gliosis|glioma|atrophy|atrophic\s+changes|"
    r"cavernoma|meningioma|astrocytoma|haemangioma|"
    r"haemorrhage|hemorrhage|encephalomalacia|"
    r"cortical\s+dysplasia|brain\s+asymmetry|"
    r"cerebral\s+(?:oedema|edema|ischaemia|ischemia|artery\s+occlusion)|"
    r"white[-\s]matter\s+(?:changes|hyperintensities)|"
    r"high\s+intensity\s+signal|hyperintensit(?:y|ies)|"
    r"hippocamp(?:us|al)|"
    r"malformations?|mass\s+effect|heterotopic|"
    r"tumou?r|dnet|cva|avm|"
    r"epileptiform|epileptogenic|evidence\s+of\s+epilepsy|"
    r"captured\s+on\s+(?:an\s+)?EEG|"
    r"spike(?:s|\s+and\s+wave|\s+wave|\-wave)?|"
    r"polyspikes?|poly\-spikes?|"
    r"slow(?:ing|\s+wave|\s+spike)|"
    r"sharp(?:ened)?\s+wave(?:s|forms?)?|"
    r"discharges?|photoparoxysmal|photosensit(?:ive|ivity)|"
    r"hypsarrhythmia|burst\s+suppression|dysrhythmic|"
    r"ictal\s+rhythms?|paroxysmal\s+fast|"
    r"(?:lobe\s+)?focus|"
    r"temporal\s+intermittent\s+rhythmic\s+delta)\b",
    re.IGNORECASE,
)
_NEGATED_FINDING = re.compile(
    r"\b(?:no|not|without|never|failed\s+to|did\s+not)\b.{0,40}\b"
    r"(?:abnormal(?:ities|ity)?|epileptiform|epileptogenic|lesions?|"
    r"discharges?|spikes?|changes?|correlate|pathology)\b",
    re.IGNORECASE,
)
_ANAPHORA = re.compile(
    r"^\s*(?:it|this|these|they|both|"
    r"the\s+(?:scan|scans|report|imaging|study|EEG|MRI|CT))\b",
    re.IGNORECASE,
)
_ECG_NORMAL = re.compile(
    r"\bnormal\s+(?:QT|QRS|sinus|heart)\b",
    re.IGNORECASE,
)
_ECG_ONLY_NORMAL = re.compile(
    r"\b(?:ECG|electrocardiogram)\b(?![\s\S]{0,80}\b(?:EEG|MRI|CT)\b).{0,80}\bnormal\b",
    re.IGNORECASE,
)
_COORD_GAP = re.compile(
    r"^\s*(?:brain|scan|head)?\s*(?:,|and|and\s+an?)\s*$",
    re.IGNORECASE,
)
_SHARED_AS_WAS = re.compile(
    r"\b(?:normal|negative|unremarkable)\s+as\s+was\s+an?\s+"
    r"(?:EEG|MRI|CT)\b",
    re.IGNORECASE,
)
_TOKEN_TAIL = re.compile(
    r"^(?:\s+(?:of\s+the\s+)?(?:brain|scan|head))?"
    r"(?:\s+(?:in|from|on|around)\s+\d[\w/]*|\s+\d{1,2}/\d{1,2}/\d{2,4}|"
    r"\s+(?:19|20)\d{2}|\s+(?:last|this)\s+year)?"
    r"(?:\s+(?:was|were|is|are|had\s+been|"
    r"has\s+been(?:\s+reported(?:\s+as)?)?|"
    r"have\s+been(?:\s+reported(?:\s+as)?)?|"
    r"reported(?:\s+as)?|showed|shown|did\s+show|does\s+show))?"
    r"(?:\s+(?:normal|negative|abnormal(?:ities|ity)?|unremarkable|clear))?",
    re.IGNORECASE,
)
_EEG_TYPE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bsleep\s*deprived\b", re.IGNORECASE), "SleepDeprived"),
    (re.compile(r"\bvideo\s*telemetry\b", re.IGNORECASE), "VideoTelemetry"),
    (re.compile(r"\b(?:video[-\s]+EEG|VEEG)\b", re.IGNORECASE), "VideoTelemetry"),
)


def _extract_investigations(text: str) -> tuple[PredictedMention, ...]:
    matches = list(_INVESTIGATION_PATTERN.finditer(text))
    if not matches:
        return ()

    mentions: list[PredictedMention] = []
    for index, match in enumerate(matches):
        modality = _canonical_modality(match.group(0))
        sent_left, sent_right = _sentence_bounds(text, match.start())
        local = _local_window(text, matches, index, sent_left, sent_right)
        if _is_planned(local) and not _COMPLETED.search(local):
            continue
        if _is_planned(local) and not (_NORMAL.search(local) or _ABNORMAL.search(local)):
            continue

        evidence = local
        result = _investigation_result(local, modality)
        if result is None:
            following = _anaphoric_followup(text, sent_right, matches, index)
            if following:
                result = _investigation_result(following, modality)
                if result is not None:
                    evidence = f"{local} {following}".strip()
        if result is None:
            continue

        attrs = {
            f"{modality}_Performed": "Yes",
            f"{modality}_Results": result,
        }
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
                evidence=_sentence_window(text, match.start(), match.end())
                if result and evidence == local
                else evidence,
                evidence_span=match_span(match),
                component_owner=_owner(
                    "investigation_result",
                    RuleGroup.ANCHOR_PHRASE,
                    Portability.CLINICAL_EPILEPSY,
                    Portability.BENCHMARK_FORMAT,
                ),
            )
        )
    return _collapse_same_result(mentions)


def _sentence_bounds(text: str, pos: int) -> tuple[int, int]:
    left = max(text.rfind(".", 0, pos), text.rfind("\n", 0, pos)) + 1
    rights = [idx for idx in (text.find(".", pos), text.find("\n", pos)) if idx != -1]
    right = min(rights) if rights else len(text)
    return left, right


def _local_window(
    text: str,
    matches: Sequence[re.Match[str]],
    index: int,
    sent_left: int,
    sent_right: int,
) -> str:
    match = matches[index]
    prev_same = _previous_in_sentence(matches, index, sent_left)
    next_same = _next_in_sentence(matches, index, sent_right)

    if prev_same is not None:
        comma = text.rfind(",", prev_same.end(), match.start())
        if comma != -1:
            left = comma + 1
        else:
            left = max(prev_same.end(), match.start() - 24)
    else:
        left = max(sent_left, match.start() - 80)

    if next_same is not None:
        gap = text[match.end() : next_same.start()]
        if _COORD_GAP.match(gap):
            right = sent_right
        else:
            tail = _TOKEN_TAIL.match(gap)
            right = match.end() + (tail.end() if tail else 0)
            extended = text[left : next_same.start()].strip(" ,;")
            if _investigation_result(text[left:right], _canonical_modality(match.group(0))) is None:
                cue = _nearest_result_cue(extended, match.start() - left)
                next_at = next_same.start() - left
                if cue is not None and abs(cue - (match.start() - left)) <= abs(cue - next_at):
                    right = next_same.start()
    else:
        right = sent_right
    window = text[left:right].strip(" ,;")
    if next_same is None and _SHARED_AS_WAS.search(text[sent_left:sent_right]):
        return text[sent_left:sent_right].strip(" ,;")
    return window


def _previous_in_sentence(
    matches: Sequence[re.Match[str]], index: int, sent_left: int
) -> re.Match[str] | None:
    if index == 0:
        return None
    previous = matches[index - 1]
    return previous if previous.start() >= sent_left else None


def _next_in_sentence(
    matches: Sequence[re.Match[str]], index: int, sent_right: int
) -> re.Match[str] | None:
    if index + 1 >= len(matches):
        return None
    following = matches[index + 1]
    return following if following.start() <= sent_right else None


def _anaphoric_followup(
    text: str,
    sent_right: int,
    matches: Sequence[re.Match[str]],
    index: int,
) -> str | None:
    next_left = sent_right + 1
    if next_left >= len(text):
        return None
    next_left, next_right = _sentence_bounds(text, next_left)
    following = text[next_left:next_right].strip(" ,;")
    if not following or not _ANAPHORA.search(following):
        return None
    later = [item for item in matches[index + 1 :] if next_left <= item.start() < next_right]
    if later and any(
        not _is_planned(_local_window(text, matches, matches.index(item), next_left, next_right))
        for item in later
    ):
        return None
    return following


def _is_planned(window: str) -> bool:
    return _PLANNED.search(window) is not None


def _investigation_result(text: str, modality: str) -> str | None:
    del modality
    working = _ECG_NORMAL.sub(" ", text)
    working = _ECG_ONLY_NORMAL.sub(" ", working)
    if _NEGATED_FINDING.search(working) and not _ABNORMAL.search(working):
        return "Normal"
    if re.search(r"\bnormal\s+apart\s+from\b", working, re.IGNORECASE):
        return "Normal"
    if _ABNORMAL.search(working) and not _NEGATED_FINDING.search(working):
        return "Abnormal"
    if _NEGATED_FINDING.search(working):
        return "Normal"
    if _NORMAL.search(working):
        return "Normal"
    if _UNKNOWN.search(working):
        return "Unknown"
    return None


def _nearest_result_cue(text: str, origin: int) -> int | None:
    positions: list[int] = []
    for pattern in (_NORMAL, _ABNORMAL, _UNKNOWN, _NEGATED_FINDING):
        positions.extend(match.start() for match in pattern.finditer(text))
    if not positions:
        return None
    return min(positions, key=lambda pos: abs(pos - origin))


def _eeg_type(text: str) -> str | None:
    for pattern, value in _EEG_TYPE_PATTERNS:
        if pattern.search(text):
            return value
    if re.search(
        r"\b(?:standard|routine)\s+EEG\b|\bsingle\s+burst\s+of\s+"
        r"(?:generalised|generalized)?\s*spike\s+and\s+wave\b",
        text,
        re.IGNORECASE,
    ):
        return "Standard"
    return None


def _collapse_same_result(
    mentions: Sequence[PredictedMention],
) -> tuple[PredictedMention, ...]:
    kept: list[PredictedMention] = []
    seen: set[tuple[str, str]] = set()
    for mention in mentions:
        modality = next(
            (
                name
                for name in ("EEG", "MRI", "CT")
                if mention.attributes.get(f"{name}_Performed") == "Yes"
            ),
            mention.text,
        )
        result = str(mention.attributes.get(f"{modality}_Results") or "")
        key = (modality, result)
        if key in seen:
            continue
        seen.add(key)
        kept.append(mention)
    return tuple(kept)


def investigation_result_from_span(text: str) -> str | None:
    """Classify List 9 finding language on an already-selected span."""

    return _investigation_result(text, modality="")
