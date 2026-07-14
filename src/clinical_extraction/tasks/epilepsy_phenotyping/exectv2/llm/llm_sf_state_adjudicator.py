"""Candidate-span SeizureFrequency adjudicator over the v0.5 structured draft."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

import dspy

from clinical_extraction.core.run_resume import merge_rows, pending_items, read_completed
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_verifier as verifier_base,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    MentionRecord,
    _has_blocking_parse_issue,
    check_evidence,
    parse_extraction_json,
    repair_attributes,
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    benchmark_config_for,
    score_entity,
    score_frequency_state,
    semantic_config_for,
    source_near_diagnostic,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm


def _confidence(value: object) -> Literal["low", "medium", "high"]:
    normalized = str(value)
    if normalized not in {"low", "medium", "high"}:
        return "medium"
    return cast(Literal["low", "medium", "high"], normalized)


PROMPT_VERSION = "exectv2_hybrid_sf_state_adjudicator_v0.5"
PIPELINE_FAMILY = "exectv2_hybrid_sf_state_adjudicator"
COMPONENT_OWNER = "hybrid_sf_state_adjudicator"

_SEIZURE_RE = re.compile(
    r"\b("
    r"seizure(?:s|-free| free)?|absen(?:ce|ces)|myoclonic|tonic(?:-| )clonic|"
    r"tonic(?:-| )chronic|convulsive|focal|dyscognitive|complex partial|"
    r"cluster of seizures|jerks"
    r")\b",
    re.IGNORECASE,
)
_STATE_RE = re.compile(
    r"\b("
    r"\d+|one|two|three|four|five|six|seven|eight|nine|ten|few|several|many|"
    r"total|per|every|daily|weekly|monthly|yearly|week|month|year|day|"
    r"frequent|infrequent|occasional|returned|return|improved|improvement|"
    r"worse|increased|decreased|controlled|under control|seizure[- ]free|"
    r"not had|no further|last event|last seizure|last seizures|since|cluster"
    r")\b",
    re.IGNORECASE,
)
_BLOCKING_CONTEXT_RE = re.compile(
    r"\b(family history|no history of|single focal seizure|diagnosis|diagnosed with)\b",
    re.IGNORECASE,
)
_DIRECT_SPAN_RES = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"(?:the\s+)?seizures?\s+have\s+returned",
        r"not\s+had\s+any\s+further\s+seizures?[^.!\n\r]*",
        r"not\s+had\s+any\s+more\s+seizures?[^.!\n\r]*",
        r"no\s+further\s+seizures?[^.!\n\r]*",
        r"seizure[- ]free\s+for\s+[^.!\n\r]*",
        r"(?:a\s+)?total\s+of\s+\d+\s+in\s+\d{4}",
        r"(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+"
        r"seizures?\s+(?:a|per|every)\s+[^.!\n\r,;]*",
        r"\d+\s*(?:-|to)\s*\d+\s+[^.!\n\r,;]*seizures?[^.!\n\r,;]*",
        r"(?:very\s+)?frequent\s+myoclonic\s+jerks",
        r"infrequent\s+[^.!\n\r,;]*seizures?",
        r"focal\s+seizures?\s+are\s+completely\s+under\s+control",
        r"last\s+seizures?\s+were\s+in\s+[^.!\n\r,;]*",
        r"[^.!\n\r,;]*last\s+event\s+[^.!\n\r,;]*\d{4}",
    ]
]


@dataclass(frozen=True)
class CandidateSpan:
    """One exact source span offered to the LLM as possible SF evidence."""

    candidate_id: str
    evidence: str
    state_hint: str
    text_hint: str
    candidate_type: str
    decision_lane: str
    source: str
    start: int
    end: int

    def as_payload(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "evidence": self.evidence,
            "state_hint": self.state_hint,
            "text_hint": self.text_hint,
            "candidate_type": self.candidate_type,
            "decision_lane": self.decision_lane,
            "source": self.source,
        }


class ExECTv2SFStateAdjudicatorSignature(dspy.Signature):
    """Review a clinical letter and candidate seizure-frequency spans."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter, draft SF mentions, candidate spans, and rules."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            'One strict JSON object: {"mentions": [{"text": ..., '
            '"attributes": {...}, "evidence": ..., "confidence": ..., '
            '"rationale": ...}, ...]}'
        )
    )


class DspySFStateAdjudicator(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2SFStateAdjudicatorSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def draft_mentions_by_letter(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    return verifier_base.draft_mentions_by_letter(rows)


def read_draft_rows(path: Path | None) -> list[dict[str, Any]]:
    return verifier_base.read_draft_rows(path)


def candidate_spans_for_letter(
    letter: ExectLetter,
    draft_mentions: Sequence[Mapping[str, Any]] = (),
    *,
    max_candidates: int = 24,
) -> list[CandidateSpan]:
    text = letter.note_text
    spans: list[CandidateSpan] = []
    seen: set[str] = set()

    def add(evidence: str, source: str, start: int | None = None, end: int | None = None) -> None:
        clean = evidence.strip()
        if not clean or clean not in text:
            return
        normalized = re.sub(r"\s+", " ", clean.lower())
        if normalized in seen:
            return
        if start is None or end is None:
            start = text.index(clean)
            end = start + len(clean)
        seen.add(normalized)
        spans.append(
            CandidateSpan(
                candidate_id=f"C{len(spans)}",
                evidence=clean,
                state_hint=_state_hint(clean),
                text_hint=_text_hint(clean),
                candidate_type=_candidate_type(clean),
                decision_lane=_decision_lane(clean),
                source=source,
                start=start,
                end=end,
            )
        )

    for draft in draft_mentions:
        evidence = str(draft.get("evidence", "")).strip()
        if evidence:
            add(evidence, "draft")

    for pattern in _DIRECT_SPAN_RES:
        for match in pattern.finditer(text):
            add(match.group(0), "candidate-pattern", match.start(), match.end())

    for sentence, start, end in _sentence_spans(text):
        if _SEIZURE_RE.search(sentence) and _STATE_RE.search(sentence):
            add(sentence, "candidate-sentence", start, end)

    return spans[:max_candidates]


def build_prompt_input(
    letter: ExectLetter,
    draft_mentions: Sequence[Mapping[str, Any]],
    candidate_spans: Sequence[CandidateSpan] | None = None,
    timeline_context: str | None = None,
) -> str:
    candidates = (
        list(candidate_spans)
        if candidate_spans is not None
        else candidate_spans_for_letter(letter, draft_mentions)
    )
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Review the clinical letter, the draft SeizureFrequency mentions, "
            "and the candidate evidence spans. Return final SeizureFrequency "
            "mentions only. The candidate spans are possible evidence anchors; "
            "keep, reject, split, merge, or add mentions based on the letter."
        ),
        "output_schema": {
            "mentions": [
                {
                    "text": "Clean seizure/event type anchor phrase owned by you.",
                    "attributes": {
                        "NumberOfSeizures": "string count, including 0 for seizure-free",
                        "LowerNumberOfSeizures": "lower bound count",
                        "UpperNumberOfSeizures": "upper bound count",
                        "NumberOfTimePeriods": "period count",
                        "LowerNumberOfTimePeriods": "lower bound period count",
                        "UpperNumberOfTimePeriods": "upper bound period count",
                        "TimePeriod": "Day | Week | Month | Year",
                        "TimeSince_or_TimeOfEvent": "Since | During",
                        "FrequencyChange": ("Decreased | Frequent | Increased | Infrequent | Same"),
                        "PointInTime": (
                            "Birthday | DrugChange | LastClinic | Last_Month | "
                            "Last_Week | Last_Year | Surgery"
                        ),
                        "DayDate": "day number",
                        "MonthDate": "month number",
                        "YearDate": "year number",
                        "AgeLower": "lower age",
                        "AgeUpper": "upper age",
                        "AgeUnit": "Year | Month",
                    },
                    "evidence": "Exact source substring supporting text and attributes.",
                    "confidence": "low | medium | high",
                    "rationale": "One brief sentence explaining the decision.",
                }
            ]
        },
        "draft_seizure_frequency_mentions": list(draft_mentions),
        "candidate_evidence_spans": [candidate.as_payload() for candidate in candidates],
        "typed_candidate_guide": _typed_candidate_guide(),
        "state_decision_guide": _state_decision_guide(),
        "generic_seizure_policy": _generic_seizure_policy(),
        "seizure_free_anchor_guide": _seizure_free_anchor_guide(),
        "unknown_change_recovery_lane": _unknown_change_recovery_lane(),
        "attribute_vocabulary": verifier_base._attribute_vocabulary(),
        "clinical_rules": _clinical_rules(),
        "worked_examples": _worked_examples(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    if timeline_context is not None:
        # Optional pre-extraction context (Phase C, see
        # docs/plans/supervisor_brief_gap_closure_plan_2026-07-01.md). Only
        # added to the payload when the caller opts in, so the prompt/JSONL
        # produced for existing runs is byte-identical when unset.
        payload["timeline_context"] = timeline_context
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _clinical_rules() -> list[str]:
    return [
        (
            "Candidate spans are not predictions. Reject any candidate that is "
            "diagnosis-only, family-history-only, unlabelled episodes/events, or "
            "a bare seizure type without frequency state."
        ),
        (
            "Prefer candidate evidence when it exactly supports a final mention, "
            "but you may use another exact substring from the letter when the "
            "candidate list misses a better span."
        ),
        (
            "A candidate with state_hint='reject' should usually be omitted unless "
            "the letter clearly contains a count, seizure-free target, last-event "
            "anchor, or frequency-change statement."
        ),
        (
            "Use candidate_type and decision_lane before deciding. generic_active_rate "
            "and named_active_rate are different decisions; do not add generic "
            "seizures when a named_active_rate already owns the count."
        ),
        (
            "candidate_type='prior_event_reference' is usually not an active-rate "
            "mention. It may support seizure-free only when the annotation scheme "
            "has a clear last-event anchor and no newer seizure contradicts it."
        ),
        (
            "For seizure_free candidates, apply seizure_free_anchor_guide before "
            "rendering. Current no-further-seizure, last-event duration/date, "
            "medication-change, surgery, and last-clinic anchors usually keep "
            "NumberOfSeizures='0'. Historical-before-newer-event and "
            "best-period-only anchors usually reject."
        ),
        (
            "A source phrase like 'last seizure was on 15 April' or 'last event "
            "10 years ago' is a seizure-free anchor, not a one-seizure active "
            "rate. Render NumberOfSeizures='0' and the date/duration attributes "
            "that the evidence supports."
        ),
        (
            "Do not emit a generic seizures active-rate when the evidence names a "
            "specific seizure type such as generalised tonic clonic, focal motor, "
            "absence, dyscognitive, or focal-to-bilateral convulsive seizures. Use "
            "the named seizure type only unless the source separately gives a "
            "generic seizure frequency."
        ),
        (
            "Do not convert unlabelled attacks, episodes, events, stares, turns, "
            "jerks, or loss-of-consciousness counts into generic SeizureFrequency "
            "unless the same evidence explicitly calls them seizures."
        ),
        (
            "Do not emit seizure-free states for historical best periods, previous "
            "events before a recent seizure, driving-advice requirements, or bare "
            "longest-period-without-seizures statements."
        ),
        (
            "Do not emit generic unknown/change states from epilepsy stability, "
            "control, or treatment-response wording unless the evidence explicitly "
            "states seizure frequency changed."
        ),
        (
            "Unknown/change-state recovery is a separate lane from active-rate. "
            "If one span says seizures improved/worsened/returned/remain well "
            "controlled/are frequent, emit a generic seizures FrequencyChange "
            "mention even when another nearby span also gives a numeric rate."
        ),
        (
            "When a span has both a change phrase and a numeric rate, split them "
            "if possible: use the change phrase as evidence for FrequencyChange "
            "and the numeric phrase as evidence for active-rate only when both "
            "are independently asserted."
        ),
        (
            "For named seizure-type change wording, emit the named type when the "
            "change attaches to that type, and also emit generic seizures when "
            "the source sentence says generic seizures changed before naming "
            "the type."
        ),
    ] + verifier_base._clinical_rules()


def _generic_seizure_policy() -> dict[str, list[str]]:
    return {
        "keep_generic_active_rate": [
            "The evidence itself says seizure or seizures and gives a current count/rate.",
            "The evidence gives a generic seizure count since a point in time.",
            "The evidence says a few/several seizures per day/week/month/year.",
        ],
        "reject_generic_active_rate": [
            "The evidence says only episodes, attacks, events, turns, stares, jerks, or blackouts.",
            (
                "The evidence names a specific seizure type; emit that named "
                "type, not an extra generic duplicate."
            ),
            (
                "The evidence is historical onset, febrile childhood history, "
                "previous event, or one-off single seizure context."
            ),
        ],
        "keep_generic_seizure_free": [
            "No further seizures since a visit, medication change, surgery, date, or age range.",
            "Last seizures were at a date or age range and no recent seizure contradicts it.",
            "The evidence says seizures stopped after reaching a current medication dose.",
            "The evidence says no more seizures since the last clinic/review.",
        ],
        "reject_generic_seizure_free": [
            "Driving advice or legal requirement to be seizure free.",
            "Historical best/longest seizure-free period when the patient now has seizures.",
            "Previous event before a recent seizure.",
        ],
        "keep_generic_unknown": [
            (
                "The evidence explicitly says seizures returned, increased, "
                "decreased, improved, frequent, or infrequent."
            ),
        ],
        "reject_generic_unknown": [
            ("Epilepsy is stable, controlled, or improved without explicitly naming seizure(s)."),
            "Jerks or stares improved without a scored seizure type.",
        ],
    }


def _seizure_free_anchor_guide() -> dict[str, list[str]]:
    return {
        "keep_current_no_further": [
            (
                "has had no further/no more seizures since clinic, review, "
                "medication change, surgery, or another current anchor"
            ),
            "seizures have stopped since reaching the current dose",
            "remains seizure free after surgery or since last review",
        ],
        "keep_last_event_anchor": [
            (
                "last seizure/event was on a date or N years/months ago, when "
                "there is no newer seizure in the letter"
            ),
            (
                "named seizure type plus last event date/duration, e.g. focal "
                "to bilateral seizures, last event 10 years ago"
            ),
        ],
        "rendering": [
            "Use NumberOfSeizures='0' for all kept seizure-free anchors.",
            (
                "Use text='seizures' for generic no-further-seizure evidence; "
                "use the named seizure type for named last-event anchors."
            ),
            (
                "For 'last seizure was on 15 April', do not set "
                "NumberOfSeizures='1'; extract DayDate/MonthDate when supported."
            ),
        ],
        "reject": [
            "before the recent seizure she had been seizure free",
            "last seizure before this was in 2006",
            "up to five weeks seizure free while current seizures continue",
            "driving or legal advice requiring seizure freedom",
            "no further episodes/collapses when the evidence does not call them seizures",
        ],
    }


def _typed_candidate_guide() -> dict[str, list[str]]:
    return {
        "generic_active_rate": [
            "Generic seizure(s) plus a count/rate/current period.",
            "Emit only when the count belongs to generic seizure(s), not a named seizure type.",
        ],
        "named_active_rate": [
            "A named seizure type plus count/rate/current period.",
            (
                "Prefer the named type and suppress duplicate generic seizures "
                "unless separately stated."
            ),
        ],
        "generic_seizure_free_anchor": [
            "No further seizures, last seizure(s), seizure-free since a supported anchor.",
            (
                "Reject driving advice, historical best periods, or "
                "previous-event-before-newer-seizure spans."
            ),
        ],
        "named_seizure_free_anchor": [
            "Named seizure type plus last-event/seizure-free anchor.",
            "Render the named type when the last-event anchor attaches to that type.",
        ],
        "generic_qualitative_change": [
            "Generic seizures improved/worsened/returned/frequent/infrequent/controlled.",
            "Use FrequencyChange and no numeric seizure count.",
        ],
        "named_qualitative_change": [
            "Named seizure type improved/worsened/frequent/infrequent/controlled.",
            "Use the named type only when the change attaches to it directly.",
        ],
        "prior_event_reference": [
            "Previous event before a recent seizure or 'last had a seizure before this'.",
            (
                "Usually reject as active-rate; consider seizure-free only for true "
                "last-event anchors."
            ),
        ],
        "unlabelled_episode_event": [
            "Episodes/events/blackouts/stares/jerks without explicit seizure wording.",
            "Reject unless the evidence itself names a scored seizure type.",
        ],
        "diagnosis_or_context": [
            "Diagnosis, family history, no-history, or context-only seizure wording.",
            "Reject as SeizureFrequency.",
        ],
    }


def _unknown_change_recovery_lane() -> dict[str, list[str]]:
    return {
        "generic_seizures_frequency_change": [
            "seizures have returned -> FrequencyChange='Increased'",
            "increasing seizures or seizures have been worse -> FrequencyChange='Increased'",
            "fairly frequent/frequent seizures -> FrequencyChange='Frequent'",
            "seizures improved or have significantly improved -> FrequencyChange='Infrequent'",
            "seizures remain well controlled -> FrequencyChange='Same'",
        ],
        "split_from_numeric_rate": [
            (
                "If 'improved her seizures' and '2 seizures in five months' both "
                "appear, emit the improvement/change state and only emit the "
                "numeric rate if the source independently frames it as a rate."
            ),
            (
                "If 'seizures have been worse' is followed by 'generalised tonic "
                "clonic seizures', emit generic seizures Increased from the first "
                "clause; optionally emit the named type only if its own change or "
                "rate is explicit."
            ),
        ],
        "reject": [
            "epilepsy is stable without saying seizures are stable",
            "control improved to odd stares only, unless the text calls those stares seizures",
            "jerks improved unless the evidence says myoclonic jerks",
        ],
    }


def _state_decision_guide() -> dict[str, list[str]]:
    return {
        "active-rate": [
            "Nonzero count or range with a seizure/event type.",
            "Rate such as per day, per week, per month, per year, or every N weeks.",
            "A dated historical count that the annotation scheme treats as an event frequency.",
        ],
        "seizure-free": [
            "NumberOfSeizures='0'.",
            "Last-event/last-seizure anchors such as last event July 2016.",
            "No further seizures since a supported point in time.",
        ],
        "unknown": [
            (
                "Relative or qualitative change without a count, such as "
                "returned, frequent, improved, or controlled."
            ),
            "Use FrequencyChange and omit numeric seizure-count fields.",
        ],
        "reject": [
            "Diagnosis or seizure type with no frequency state.",
            (
                "Family history, no history, or unlabelled episodes/events not "
                "explicitly scored as seizures."
            ),
        ],
    }


def _worked_examples() -> list[dict[str, Any]]:
    return [
        {
            "note_fragment": (
                "Increasing her tegretol has improved her seizures. Hannah thinks "
                "that she has had 2 seizures in the last five months which is good for her."
            ),
            "draft": [{"text": "seizures", "attributes": {"NumberOfSeizures": "2"}}],
            "correct": [
                {
                    "text": "seizures",
                    "attributes": {
                        "FrequencyChange": "Infrequent",
                        "PointInTime": "DrugChange",
                    },
                    "evidence": "improved her seizures",
                    "confidence": "medium",
                    "rationale": "Drug-change improvement is a generic seizure change state.",
                }
            ],
        },
        {
            "note_fragment": (
                "Unfortunately seizures have been worse in the last year. She is "
                "having quite a number of generalised tonic clonic seizures."
            ),
            "draft": [{"text": "generalised tonic clonic seizures"}],
            "correct": [
                {
                    "text": "seizures",
                    "attributes": {
                        "FrequencyChange": "Increased",
                        "PointInTime": "Last_Year",
                    },
                    "evidence": "seizures have been worse in the last year",
                    "confidence": "medium",
                    "rationale": "The generic seizure change is explicit before the named type.",
                }
            ],
        },
        {
            "note_fragment": "Richard's seizures remain well controlled.",
            "draft": [],
            "correct": [
                {
                    "text": "seizures",
                    "attributes": {"FrequencyChange": "Same"},
                    "evidence": "seizures remain well controlled",
                    "confidence": "medium",
                    "rationale": "Well-controlled seizures imply stable seizure frequency.",
                }
            ],
        },
        {
            "note_fragment": (
                "He gets around 1 generalised tonic clonic seizure in his sleep per month."
            ),
            "draft": [{"text": "seizures"}],
            "candidate_span": (
                "He gets around 1 generalised tonic clonic seizure in his sleep per month"
            ),
            "correct": [
                {
                    "text": "generalised tonic clonic seizure",
                    "attributes": {
                        "NumberOfSeizures": "1",
                        "NumberOfTimePeriods": "1",
                        "TimePeriod": "Month",
                    },
                    "evidence": (
                        "around 1 generalised tonic clonic seizure in his sleep per month"
                    ),
                    "confidence": "high",
                    "rationale": (
                        "The evidence names the seizure type, so no extra generic "
                        "seizures mention is emitted."
                    ),
                }
            ],
        },
        {
            "note_fragment": (
                "Once commenced on sodium valproate 400mg twice daily, she has "
                "had no further seizures."
            ),
            "draft": [{"text": "no further seizures"}],
            "correct": [
                {
                    "text": "seizures",
                    "attributes": {
                        "NumberOfSeizures": "0",
                        "PointInTime": "DrugChange",
                        "TimeSince_or_TimeOfEvent": "Since",
                    },
                    "evidence": (
                        "Once commenced on sodium valproate 400mg twice daily, "
                        "she has had no further seizures."
                    ),
                    "confidence": "high",
                    "rationale": (
                        "Current no-further-seizure evidence is generic "
                        "seizure freedom after a medication change."
                    ),
                }
            ],
        },
        {
            "note_fragment": (
                "Rachel said that her last seizure was on the 15th April in her home."
            ),
            "draft": [{"text": "last seizure", "attributes": {"NumberOfSeizures": "1"}}],
            "correct": [
                {
                    "text": "seizure",
                    "attributes": {
                        "NumberOfSeizures": "0",
                        "DayDate": "15",
                        "MonthDate": "4",
                    },
                    "evidence": "last seizure was on the 15th April",
                    "confidence": "high",
                    "rationale": (
                        "A last-seizure date is a seizure-free anchor, not a "
                        "one-seizure active-rate count."
                    ),
                }
            ],
        },
        {
            "note_fragment": (
                "There is also a history of staring episodes which last up to 2 minutes. "
                "They occur 3 to 5 times a week."
            ),
            "draft": [{"text": "seizures"}],
            "correct": [],
        },
        {
            "note_fragment": ("Before the recent seizure she had been seizure free for 3 years."),
            "draft": [{"text": "seizure free"}],
            "correct": [],
        },
        {
            "note_fragment": "His epilepsy has been stable over the last few years.",
            "draft": [{"text": "seizures", "attributes": {"FrequencyChange": "Same"}}],
            "correct": [],
        },
    ] + verifier_base._worked_examples()


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


def _state_hint(evidence: str) -> str:
    lower = evidence.lower()
    if _BLOCKING_CONTEXT_RE.search(lower):
        return "reject"
    if re.search(r"\b(seizure[- ]free|not had|no further|last event|last seizures?)\b", lower):
        return "seizure-free"
    if re.search(
        r"\b(returned|increased|decreased|frequent|infrequent|improved|improvement)\b",
        lower,
    ):
        return "unknown"
    if re.search(
        r"\b("
        r"\d+|one|two|three|four|five|six|seven|eight|nine|ten|few|several|"
        r"total|per|every|cluster"
        r")\b",
        lower,
    ):
        return "active-rate"
    return "reject"


def _candidate_type(evidence: str) -> str:
    lower = evidence.lower()
    if _BLOCKING_CONTEXT_RE.search(lower):
        return "diagnosis_or_context"
    if re.search(r"\b(episodes?|events?|blackouts?|stares?|turns?)\b", lower) and not re.search(
        r"\bseizures?\b", lower
    ):
        return "unlabelled_episode_event"
    if re.search(r"\b(previous event|seizure before this|before the recent seizure)\b", lower):
        return "prior_event_reference"
    named = _has_named_seizure_type(lower)
    seizure_free = re.search(
        r"\b(seizure[- ]free|not had|no further|last event|last seizures?)\b",
        lower,
    )
    change = re.search(
        r"\b(returned|increased|decreased|frequent|infrequent|improved|"
        r"improvement|worse|controlled|under control)\b",
        lower,
    )
    rate = re.search(
        r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|few|several|total|per|every|cluster)\b",
        lower,
    )
    if seizure_free:
        return "named_seizure_free_anchor" if named else "generic_seizure_free_anchor"
    if change:
        return "named_qualitative_change" if named else "generic_qualitative_change"
    if rate:
        return "named_active_rate" if named else "generic_active_rate"
    return "diagnosis_or_context"


def _decision_lane(evidence: str) -> str:
    candidate_type = _candidate_type(evidence)
    if candidate_type in {"generic_active_rate", "named_active_rate"}:
        return "active_rate"
    if candidate_type in {"generic_seizure_free_anchor", "named_seizure_free_anchor"}:
        return "seizure_free"
    if candidate_type in {"generic_qualitative_change", "named_qualitative_change"}:
        return "qualitative_change"
    if candidate_type == "prior_event_reference":
        return "reject_or_seizure_free"
    return "reject"


def _has_named_seizure_type(lower: str) -> bool:
    return bool(
        re.search(
            r"\b("
            r"generalised\s+tonic\s+(?:clonic|chronic)|"
            r"generalized\s+tonic\s+(?:clonic|chronic)|"
            r"tonic\s+(?:clonic|chronic)|"
            r"focal\s+to\s+bilateral|"
            r"focal\s+(?:motor\s+)?seizures?|"
            r"complex\s+partial|dyscognitive|absence|absences|"
            r"myoclonic\s+jerks|convulsive\s+seizures?"
            r")\b",
            lower,
        )
    )


def _text_hint(evidence: str) -> str:
    lower = evidence.lower()
    ordered = [
        (
            r"focal\s+to\s+bilateral\s+convulsive\s+seizures?",
            "focal to bilateral convulsive seizures",
        ),
        (
            r"generalised\s+tonic\s+(?:clonic|chronic)\s+seizures?",
            "generalised tonic clonic seizures",
        ),
        (
            r"generalized\s+tonic\s+(?:clonic|chronic)\s+seizures?",
            "generalised tonic clonic seizures",
        ),
        (r"tonic\s+(?:clonic|chronic)\s+seizures?", "tonic clonic seizures"),
        (r"complex\s+partial\s+seizures?", "complex partial seizures"),
        (r"dyscognitive\s+seizures?", "dyscognitive seizures"),
        (r"absence\s+like\s+seizures?", "absence like seizures"),
        (r"absence\s+seizures?", "absence seizures"),
        (r"\babsences\b", "absences"),
        (r"myoclonic\s+jerks", "myoclonic jerks"),
        (r"focal\s+seizures?", "focal seizures"),
        (r"convulsive\s+seizures?", "convulsive seizures"),
        (r"cluster\s+of\s+seizures", "cluster of seizures"),
        (r"\bseizure[- ]free\b", "seizures"),
        (r"\bseizures\b", "seizures"),
        (r"\bseizure\b", "seizure"),
    ]
    for pattern, hint in ordered:
        if re.search(pattern, lower):
            return hint
    return "seizures"


def to_predicted_letter(
    letter_id: str,
    mentions: list[MentionRecord],
    *,
    note_text: str,
) -> tuple[PredictedLetter, list[str]]:
    all_warnings: list[str] = []
    evidence_valid, evidence_invalid, ev_warnings = check_evidence(mentions, note_text=note_text)
    all_warnings.extend(ev_warnings)

    predicted_mentions: list[PredictedMention] = []
    spec = ENTITY_REGISTRY[SEIZURE_FREQUENCY.name]
    for mention in evidence_valid:
        attrs = dict(mention.attributes)
        for key in ("CUI", "CUIPhrase"):
            if key in attrs:
                attrs.pop(key)
                all_warnings.append(
                    f"{SEIZURE_FREQUENCY.name}: "
                    f"dropped_model_supplied_projection_attribute: {key!r}"
                )
        repaired_attrs, attr_warnings = repair_attributes(attrs, spec=spec)
        all_warnings.extend(f"{SEIZURE_FREQUENCY.name}: {warning}" for warning in attr_warnings)
        predicted_mentions.append(
            PredictedMention(
                entity=SEIZURE_FREQUENCY.name,
                text=mention.text,
                attributes=repaired_attrs,
                evidence=mention.evidence,
                confidence=mention.confidence,
                rationale=mention.rationale,
                component_owner=COMPONENT_OWNER,
            )
        )

    return (
        project_cuis(
            PredictedLetter(
                letter_id=letter_id,
                mentions=tuple(predicted_mentions),
                diagnostics={
                    "prompt_version": PROMPT_VERSION,
                    "pipeline_family": PIPELINE_FAMILY,
                    "n_evidence_invalid": len(evidence_invalid),
                    "attribute_warnings": all_warnings,
                },
            )
        ),
        all_warnings,
    )


def run_split(
    letters: Sequence[ExectLetter],
    *,
    draft_rows: Sequence[Mapping[str, Any]] = (),
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
    timeline_context_by_letter: Mapping[str, str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    program = DspySFStateAdjudicator()
    if mode == "live":
        dspy.configure(
            lm=build_dspy_lm(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=dspy_cache,
                api_base=api_base,
            )
        )

    drafts = draft_mentions_by_letter(draft_rows)
    order = [letter.letter_id for letter in letters]
    requested = set(order)
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None, key="letter_id"
    )
    rows: list[dict[str, Any]] = [r for r in existing_rows if r.get("letter_id") in requested]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    for letter in todo:
        draft_mentions = drafts.get(letter.letter_id, [])
        candidate_spans = candidate_spans_for_letter(letter, draft_mentions)
        timeline_context = (
            timeline_context_by_letter.get(letter.letter_id)
            if timeline_context_by_letter is not None
            else None
        )
        prompt_input_json = build_prompt_input(
            letter, draft_mentions, candidate_spans, timeline_context=timeline_context
        )
        raw_output = ""
        call_error: str | None = None
        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"

        extraction, parse_errors = (
            parse_extraction_json(raw_output) if raw_output else (None, ["not_run"])
        )
        mentions = extraction.mentions if extraction else []
        predicted_letter, gate_warnings = to_predicted_letter(
            letter.letter_id,
            mentions,
            note_text=letter.note_text,
        )
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "prompt_version": PROMPT_VERSION,
                "pipeline_family": PIPELINE_FAMILY,
                "model": model,
                "mode": mode,
                "draft_mentions": list(draft_mentions),
                "candidate_spans": [candidate.as_payload() for candidate in candidate_spans],
                "timeline_context_used": timeline_context is not None,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "gate_warnings": gate_warnings,
                "n_draft_mentions": len(draft_mentions),
                "n_candidate_spans": len(candidate_spans),
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(predicted_letter.mentions),
                "n_evidence_invalid": len(mentions) - len(predicted_letter.mentions),
                "predicted_mentions": [_mention_to_row(m) for m in predicted_letter.mentions],
                "gold_mentions": [
                    {"text": a.text, "attributes": dict(a.attributes)}
                    for a in letter.entities(SEIZURE_FREQUENCY.name)
                ],
            }
        )

        if progress_every and (len(rows) - n_resumed) % progress_every == 0:
            _emit_checkpoint(
                rows,
                total=len(letters),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
                split=split,
                model=model,
                mode=mode,
            )

    rows = merge_rows(rows, order, key="letter_id")
    metadata = {
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": mode,
        "split": split,
        "n_letters": len(letters),
        "n_resumed": n_resumed,
        "dspy_version": getattr(dspy, "__version__", "unknown"),
    }
    metadata["summary"] = summarize_rows(rows)
    return rows, metadata


def summarize_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"examples": 0}
    gold_letters = _reconstruct_gold_letters(rows)
    pred_letters = _reconstruct_pred_letters(rows)
    phrase = score_entity(
        gold_letters,
        pred_letters,
        SEIZURE_FREQUENCY.name,
        PHRASE_ONLY,
    )
    semantic = score_entity(
        gold_letters,
        pred_letters,
        SEIZURE_FREQUENCY.name,
        semantic_config_for(SEIZURE_FREQUENCY.name),
    )
    benchmark = score_entity(
        gold_letters,
        pred_letters,
        SEIZURE_FREQUENCY.name,
        benchmark_config_for(SEIZURE_FREQUENCY.name),
    )
    source_near = source_near_diagnostic(
        gold_letters,
        pred_letters,
        [SEIZURE_FREQUENCY.name],
        semantic_config_for,
    ).per_entity[SEIZURE_FREQUENCY.name]
    frequency = score_frequency_state(gold_letters, pred_letters)
    n_mentions_raw = sum(int(r.get("n_mentions_raw", 0)) for r in rows)
    n_evidence_invalid = sum(int(r.get("n_evidence_invalid", 0)) for r in rows)

    return {
        "examples": len(rows),
        "call_failures": sum(bool(r.get("call_error")) for r in rows),
        "parse_failures": sum(_has_blocking_parse_issue(r.get("parse_errors")) for r in rows),
        "n_draft_mentions": sum(int(r.get("n_draft_mentions", 0)) for r in rows),
        "n_candidate_spans": sum(int(r.get("n_candidate_spans", 0)) for r in rows),
        "n_mentions_raw": n_mentions_raw,
        "n_mentions_scored": sum(int(r.get("n_mentions_scored", 0)) for r in rows),
        "n_evidence_invalid": n_evidence_invalid,
        "evidence_validity_rate": (
            (n_mentions_raw - n_evidence_invalid) / n_mentions_raw if n_mentions_raw else 1.0
        ),
        "phrase_only": phrase.model_dump(),
        "semantic": semantic.model_dump(),
        "benchmark": benchmark.model_dump(),
        "source_near": source_near.model_dump(),
        "clinical_recovery": {
            "seizure_frequency": frequency.clinical_headline.model_dump(),
            "active_rate": frequency.active_rate.model_dump(),
            "seizure_free": frequency.seizure_free.model_dump(),
            "unknown": frequency.unknown.model_dump(),
            "target_headline_f1": 0.8,
        },
    }


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = metadata.get("summary", {})
    clinical = summary.get("clinical_recovery", {}).get("seizure_frequency", {})
    source_near = summary.get("source_near", {})
    lines = [
        "# ExECTv2 SeizureFrequency Candidate-Span State Adjudicator",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Prompt version: `{metadata.get('prompt_version')}`",
        f"- Pipeline family: `{metadata.get('pipeline_family')}`",
        f"- Split: `{metadata.get('split')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Letters: {metadata.get('n_letters')}",
        "",
        "## Gate Summary",
        "",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema failures: {summary.get('parse_failures', 0)}",
        f"- Draft SF mentions: {summary.get('n_draft_mentions', 0)}",
        f"- Candidate spans: {summary.get('n_candidate_spans', 0)}",
        f"- Mentions raw: {summary.get('n_mentions_raw', 0)}",
        f"- Mentions scored: {summary.get('n_mentions_scored', 0)}",
        f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
        f"- Evidence validity rate: {summary.get('evidence_validity_rate', 0):.4f}",
        "",
        "## SeizureFrequency Clinical-Recovery Headline",
        "",
        "| Target F1 | F1 | P | R | TP | FP | FN |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| 0.80 | {clinical.get('f1', 0):.3f} | "
            f"{clinical.get('precision', 0):.3f} | {clinical.get('recall', 0):.3f} | "
            f"{clinical.get('tp', 0)} | {clinical.get('fp', 0)} | "
            f"{clinical.get('fn', 0)} |"
        ),
        "",
        "## Source-Near Diagnostic",
        "",
        (
            f"- Overlap F1={source_near.get('overlap', {}).get('f1', 0):.3f} "
            f"R={source_near.get('overlap', {}).get('recall', 0):.3f}"
        ),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _mention_to_row(mention: PredictedMention) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "confidence": mention.confidence,
        "rationale": mention.rationale,
    }


def _reconstruct_gold_letters(rows: Sequence[dict[str, Any]]) -> list[ExectLetter]:
    return [
        ExectLetter(
            letter_id=row["letter_id"],
            note_text="",
            annotations=tuple(
                ExectAnnotation(
                    entity=SEIZURE_FREQUENCY.name,
                    text=str(m["text"]),
                    attributes={str(k): str(v) for k, v in dict(m.get("attributes") or {}).items()},
                )
                for m in row.get("gold_mentions", [])
            ),
        )
        for row in rows
    ]


def _reconstruct_pred_letters(rows: Sequence[dict[str, Any]]) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        pred = PredictedLetter(
            letter_id=row["letter_id"],
            mentions=tuple(
                PredictedMention(
                    entity=SEIZURE_FREQUENCY.name,
                    text=str(m["text"]),
                    attributes={str(k): str(v) for k, v in dict(m.get("attributes") or {}).items()},
                    evidence=str(m.get("evidence", "")),
                    confidence=_confidence(m.get("confidence", "medium")),
                    rationale=str(m.get("rationale", "")),
                )
                for m in row.get("predicted_mentions", [])
            ),
        )
        letters.append(to_exect_letter(pred))
    return letters


def _emit_checkpoint(
    rows: Sequence[dict[str, Any]],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
    split: str,
    model: str,
    mode: str,
) -> None:
    if jsonl_path:
        write_jsonl(rows, jsonl_path)
    metadata = {
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "model": model,
        "mode": mode,
        "split": split,
        "n_letters": total,
        "summary": summarize_rows(rows),
    }
    if report_path:
        write_report(rows, metadata, report_path, jsonl_path=jsonl_path or Path(""))
    summary_value = metadata["summary"]
    summary = summary_value if isinstance(summary_value, Mapping) else {}
    print(
        json.dumps(
            {
                "processed": len(rows),
                "total": total,
                "call_failures": summary.get("call_failures", 0),
                "parse_failures": summary.get("parse_failures", 0),
                "n_mentions_scored": summary.get("n_mentions_scored", 0),
            },
            sort_keys=True,
        ),
        flush=True,
    )
