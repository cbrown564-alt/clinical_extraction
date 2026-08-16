"""Candidate/high-priority evidence ledgers and prompt-content helpers.

Pure relocation from ``llm_only_key_entities_structured``. No logic changes.
"""

from __future__ import annotations

import re
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompts.key_entities.loader import (
    load_worked_examples,
)

from ....deterministic.sf_surface_registry.adapters.convention import (
    residual_candidates_adapter,
)
from .constants import (
    _DIAGNOSIS_RE,
    _INVESTIGATION_RE,
    _MEDICATION_RE,
    _SEIZURE_STATE_RE,
    KEY_ENTITY_NAMES,
)


def high_priority_evidence_ledger_for_letter(letter: ExectLetter) -> list[dict[str, Any]]:
    """Source-bound cue rows for facts Qwen must select itself.

    The rows intentionally avoid scorer-ready attributes. They tell the model
    where high-yield evidence lives, while the model still owns the final
    keep/reject, family, text, and attribute rendering.
    """

    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    def add(*, family: str, evidence: str, anchor_hint: str, lane_hint: str) -> None:
        clean = " ".join(evidence.strip().split())
        if not clean or clean not in letter.note_text:
            return
        key = (family, clean.lower(), anchor_hint.lower())
        if key in seen:
            return
        seen.add(key)
        rows.append(
            {
                "priority_id": f"HP{len(rows)}",
                "family": family,
                "evidence": clean,
                "anchor_hint": anchor_hint,
                "lane_hint": lane_hint,
                "source": "source-bound-standard-dictionary-cue",
            }
        )

    for text, evidence in sd.diagnosis_residual_additions(letter.note_text):
        add(
            family="diagnosis",
            evidence=evidence,
            anchor_hint=text,
            lane_hint="diagnosis_assertion",
        )
    for text, evidence, _attrs in residual_candidates_adapter(letter.note_text):
        add(
            family="seizure_frequency",
            evidence=evidence,
            anchor_hint=text,
            lane_hint=_seizure_frequency_lane_hint(evidence.lower()),
        )
    for text, evidence, _attrs in sd.prescription_residual_additions(letter.note_text):
        add(
            family="medication",
            evidence=evidence,
            anchor_hint=text,
            lane_hint=_medication_lane_hint(evidence.lower()),
        )
    for text, evidence, _attrs in sd.investigation_residual_additions(letter.note_text):
        add(
            family="investigation",
            evidence=evidence,
            anchor_hint=text,
            lane_hint=_investigation_lane_hint(evidence.lower()),
        )
    return rows[:32]


def candidate_evidence_ledger_for_letter(
    letter: ExectLetter,
    *,
    max_items: int = 48,
) -> list[dict[str, Any]]:
    """Build source-near candidate spans used only as prompt attention scaffolding."""

    candidates: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    def add(
        *,
        family: str,
        evidence: str,
        source: str,
        lane_hint: str,
        anchor_hint: str,
    ) -> None:
        clean = " ".join(evidence.strip().split())
        if not clean or clean not in letter.note_text:
            return
        key = (family, clean.lower())
        if key in seen:
            return
        seen.add(key)
        candidates.append(
            {
                "candidate_id": f"K{len(candidates)}",
                "family": family,
                "evidence": clean,
                "anchor_hint": anchor_hint,
                "lane_hint": lane_hint,
                "source": source,
            }
        )

    for sentence, _, _ in _sentence_spans(letter.note_text):
        lower = sentence.lower()
        if _MEDICATION_RE.search(sentence):
            add(
                family="medication",
                evidence=sentence,
                source="sentence-medication-trigger",
                lane_hint=_medication_lane_hint(lower),
                anchor_hint=_first_match_text(_MEDICATION_RE, sentence),
            )
        if _INVESTIGATION_RE.search(sentence):
            add(
                family="investigation",
                evidence=sentence,
                source="sentence-investigation-trigger",
                lane_hint=_investigation_lane_hint(lower),
                anchor_hint=_first_match_text(_INVESTIGATION_RE, sentence),
            )
        if _DIAGNOSIS_RE.search(sentence):
            add(
                family="diagnosis",
                evidence=sentence,
                source="sentence-diagnosis-trigger",
                lane_hint=_diagnosis_lane_hint(lower),
                anchor_hint=_first_match_text(_DIAGNOSIS_RE, sentence),
            )
        if _SEIZURE_STATE_RE.search(sentence) and re.search(r"\bseizure", lower):
            add(
                family="seizure_frequency",
                evidence=sentence,
                source="sentence-seizure-state-trigger",
                lane_hint=_seizure_frequency_lane_hint(lower),
                anchor_hint=_seizure_anchor_hint(sentence),
            )

    return candidates[:max_items]


def _decision_procedure() -> list[str]:
    return [
        ("Scan the letter globally for the four key families; do not stop at section headers."),
        (
            "Use candidate_evidence_ledger rows as likely evidence anchors, but "
            "do not emit a row unless the full sentence supports a requested family."
        ),
        (
            "For each candidate, choose a lane, then keep/reject/split/merge. "
            "Write the lane decision into event_state when it helps transparency."
        ),
        (
            "Render final mentions only after the source-near event state "
            "is clear. Counts, dates, result status, dose, and certainty belong in "
            "attributes, not in improvised text."
        ),
        (
            "Before returning JSON, remove duplicates and remove events whose "
            "evidence or mention text is not an exact source substring."
        ),
    ]


def _event_lane_guide() -> dict[str, list[str]]:
    return {
        "medication": [
            "current_regimen: current/taking/on medication with dose or frequency",
            "rescue_regimen: as required, if necessary, or for clusters",
            "future_or_historical_medication: start/introduce/increase/previous/stopped/trial",
            "reject: non-anti-seizure medication or unsupported plan",
        ],
        "diagnosis": [
            "diagnosis_assertion: patient-level epilepsy syndrome or named seizure type",
            "diagnosis_context_only: discussion, family history, risk, SUDEP, or education",
            "symptom_or_nonepileptic: blackout, collapse, anxiety, dissociative event, aura only",
            "reject: no explicit epileptic diagnosis or named epileptic seizure type",
        ],
        "seizure_frequency": [
            "active_rate: count/rate/current cadence for generic or named seizures",
            "seizure_free_anchor: no further seizures, seizure-free, last seizure/event date",
            "qualitative_change: frequent/infrequent/increased/decreased/returned/controlled",
            "reject: diagnosis-only, family history, unlabelled events, historical best period",
        ],
        "investigation": [
            "performed_investigation: completed MRI/CT/EEG/telemetry, especially with result",
            "not_performed: never had/no MRI/no EEG/no CT",
            "planned_investigation: arrange/request/repeat/future/follow-up",
            "reject: bare modality without performed/result/not-performed status",
        ],
    }


def _sentence_spans(text: str) -> list[tuple[str, int, int]]:
    spans: list[tuple[str, int, int]] = []
    for match in re.finditer(r"[^.!?\n\r]+(?:[.!?]+|$)", text):
        start, end = match.span()
        raw = match.group(0)
        leading = len(raw) - len(raw.lstrip())
        trailing = len(raw.rstrip())
        clean = raw.strip()
        if clean:
            spans.append((clean, start + leading, start + trailing))
    return spans


def _first_match_text(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return match.group(0) if match else ""


def _medication_lane_hint(lower: str) -> str:
    if re.search(r"\b(previous|previously|stopped|withdrawn|trial|allergic)\b", lower):
        return "future_or_historical_medication"
    if re.search(r"\b(start|commence|introduce|increase|target|plan|consider|if further)\b", lower):
        return "future_or_historical_medication"
    if re.search(r"\b(as required|prn|if necessary|rescue|clusters?)\b", lower):
        return "rescue_regimen"
    return "current_regimen"


def _investigation_lane_hint(lower: str) -> str:
    if re.search(r"\b(arrange|request|repeat|plan|organise|follow[- ]up|will have)\b", lower):
        return "planned_investigation"
    if re.search(r"\b(no|never had|not had|not performed)\b", lower):
        return "not_performed"
    if re.search(
        r"\b(normal|abnormal|show|showed|shown|shows|demonstrated|revealed|captured|done|had)\b",
        lower,
    ):
        return "performed_investigation"
    return "reject"


def _diagnosis_lane_hint(lower: str) -> str:
    if re.search(
        r"\b(family history|discussion|risk|sudep|education|brother|mother|father)\b",
        lower,
    ):
        return "diagnosis_context_only"
    if re.search(
        r"\b("
        r"not had any events|no events|no history|without seizures|"
        r"blackout|collapse|anxiety|dissociative|non[- ]epileptic|aura"
        r")\b",
        lower,
    ):
        return "symptom_or_nonepileptic"
    return "diagnosis_assertion"


def _seizure_frequency_lane_hint(lower: str) -> str:
    if re.search(
        r"\b(febrile seizures|family history|risk of seizures|previous event)\b",
        lower,
    ):
        return "reject"
    if re.search(
        r"\b(not had any events|no events which resemble|no history of seizures)\b",
        lower,
    ):
        return "reject"
    if re.search(
        r"\b(seizure[- ]free|no further|no more|not had|last seizure|last event)\b",
        lower,
    ):
        return "seizure_free_anchor"
    if re.search(
        r"\b(returned|frequent|infrequent|controlled|under control|increased|decreased)\b",
        lower,
    ):
        return "qualitative_change"
    if re.search(
        r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|few|several|per|every|cluster)\b",
        lower,
    ):
        return "active_rate"
    return "reject"


def _seizure_anchor_hint(text: str) -> str:
    ordered = [
        r"focal\s+to\s+bilateral\s+convulsive\s+seizures?",
        r"generalised\s+tonic[- ](?:clonic|chronic)\s+seizures?",
        r"generalized\s+tonic[- ](?:clonic|chronic)\s+seizures?",
        r"tonic[- ](?:clonic|chronic)\s+seizures?",
        r"complex\s+partial\s+seizures?",
        r"dyscognitive\s+seizures?",
        r"absence[- ]like\s+seizures?",
        r"absence\s+seizures?",
        r"focal\s+seizures?",
        r"cluster\s+of\s+seizures",
        r"seizure[- ]free",
        r"seizures?",
    ]
    for pattern in ordered:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return "seizures"


def _family_guidance() -> dict[str, str]:
    return {
        "medication": (
            "Anti-seizure medication events. Render Prescription mentions with "
            "DrugName, DrugDose, DoseUnit, and Frequency when stated. The rendered "
            "text should preserve the medication item's annotation-facing span: "
            "full compact regimen when present in a medication list, bare drug name "
            "when that is all the note states."
        ),
        "diagnosis": (
            "Diagnostic concepts such as epilepsy, focal epilepsy, seizure disorder, "
            "or named seizure types. Render atomic Diagnosis mentions with "
            "DiagCategory, Certainty, and Negation. Preserve uncertainty words and "
            "avoid vague symptoms or non-epileptic differentials unless they are "
            "explicitly asserted as epileptic diagnoses, even when they appear in a "
            "Diagnosis/problem-list section. Mention text should be the clean core "
            "concept span; hedging belongs in Certainty."
        ),
        "seizure_frequency": (
            "How often a seizure type occurs, including seizure-free duration, "
            "ranges, interval cadence, cluster counts, dated counts, and frequency "
            "change. Preserve the stated seizure anchor and temporal frame instead "
            "of converting it into a guessed rate; exclude non-epileptic events and "
            "blackouts unless the letter states they are epileptic seizures."
        ),
        "investigation": (
            "EEG, MRI, CT, telemetry, and related investigation statements. Render "
            "Investigations with performed/result/type attributes only for completed "
            "or resulted tests, not planned repeats or bare modality references."
        ),
    }


def _attribute_vocabulary() -> dict[str, dict[str, Any]]:
    vocab: dict[str, dict[str, Any]] = {}
    for entity_name in KEY_ENTITY_NAMES:
        spec = ENTITY_REGISTRY[entity_name]
        attrs: dict[str, Any] = {}
        for attr in sorted(spec.legal_attributes):
            if attr in {"CUI", "CUIPhrase"}:
                continue
            if attr in spec.closed_vocab:
                attrs[attr] = sorted(spec.closed_vocab[attr])
            else:
                attrs[attr] = "string copied or normalized from the letter."
        vocab[entity_name] = attrs
    return vocab


def _worked_examples() -> list[dict[str, Any]]:
    return load_worked_examples()
