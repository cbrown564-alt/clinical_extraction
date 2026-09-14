"""Strict one-call paper conditions; never use the historical repair parser."""

from __future__ import annotations

import json
import math
import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_extract_encode_select as historical,
)
from clinical_extraction.tasks.shared.epilepsy.normalization import label_to_frequency_record

VERSION = "one_shot_frequency_v1"
Condition = Literal["rich", "simple"]
CONDITIONS: tuple[Condition, ...] = ("rich", "simple")


class StrictRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Answer(StrictRecord):
    label: str
    evidence: str | None


class Finding(StrictRecord):
    finding_id: str
    kind: Literal[
        "frequency_rate",
        "cluster_frequency",
        "seizure_free",
        "last_event_only",
        "unknown_frequency",
    ]
    raw_value: str
    seizure_type: str | None
    time_window: str | None
    temporality: Literal["current", "recent", "historical", "future", "unclear"]
    certainty: Literal["asserted", "uncertain"]
    negated: bool
    evidence: str


class Simple(StrictRecord):
    answer: Answer


class Rich(Simple):
    findings: list[Finding]
    selected_finding_ids: list[str]


MODELS: dict[str, type[Simple]] = {"rich": Rich, "simple": Simple}
COMMON = [
    "Determine the patient's current seizure frequency from the whole note.",
    "Return exactly one JSON object following the supplied schema, with every required field.",
    "The answer label is mandatory, including unknown and no seizure frequency reference.",
    "Use unknown when seizures are discussed but a current frequency cannot be determined. "
    "Use no seizure frequency reference only when no seizure-frequency information is present.",
    "Copy the answer evidence exactly from the note. It may cover several adjacent statements. "
    "Only no seizure frequency reference has null answer evidence; never invent an absence quote.",
    "Do not treat uncertain events as definite or planned events as current. Select the stated "
    "current pattern, retaining uncertainty in your interpretation. Do not infer seizure freedom "
    "from improved wellbeing or absence of rescue medication.",
    "For competing current seizure types, use the most frequent current pattern, unless a "
    "cluster pattern describes grouped events separated by intervals; preserve cluster cadence. "
    "Do not sum independently reported types without an explicit combined total.",
    "When current statements conflict and cannot be resolved, write unknown with the "
    "conflicting source passage as evidence. Do not manufacture a numeric answer.",
]
RICH_SCOPE = [
    "Also return every seizure-frequency finding, including historical, uncertain, negated, "
    "last-event and future statements. These are findings about frequency, not all clinical facts.",
    "For each finding retain its exact raw wording, seizure type, timeframe, temporality, "
    "certainty, negation and exact source quotation. Do not drop unnormalizable findings.",
    "Use unique finding IDs and link the answer to the relevant IDs. For no frequency "
    "information, return findings [] and selected_finding_ids [] with the no-reference answer. "
    "Otherwise include at least one finding and select at least one existing ID.",
]


def fictional_cases() -> list[dict[str, Any]]:
    """Authored notes, shared verbatim between conditions; never sourced from the corpus."""
    specs = [
        (
            "numeric",
            "She currently has two seizures per month.",
            "2 per month",
            "frequency_rate",
            "asserted",
            False,
        ),
        (
            "uncertain",
            "Possible seizures continue, but their frequency is unclear.",
            "unknown",
            "unknown_frequency",
            "uncertain",
            False,
        ),
        (
            "seizure_free",
            "She has had no seizures for six months.",
            "seizure free for 6 months",
            "seizure_free",
            "asserted",
            True,
        ),
        (
            "cluster",
            "She has one cluster per week, with three seizures per cluster.",
            "1 cluster per week, 3 per cluster",
            "cluster_frequency",
            "asserted",
            False,
        ),
    ]
    cases = []
    for name, note, label, kind, certainty, negated in specs:
        cases.append(
            {
                "name": name,
                "note_text": note,
                "output": {
                    "answer": {"label": label, "evidence": note},
                    "findings": [
                        {
                            "finding_id": "f1",
                            "kind": kind,
                            "raw_value": note,
                            "seizure_type": "seizures",
                            "time_window": None,
                            "temporality": "current",
                            "certainty": certainty,
                            "negated": negated,
                            "evidence": note,
                        }
                    ],
                    "selected_finding_ids": ["f1"],
                },
            }
        )
    note = "Previously she had one seizure per day. Now she has two seizures per month."
    cases.append(
        {
            "name": "multiple_statements",
            "note_text": note,
            "output": {
                "answer": {
                    "label": "2 per month",
                    "evidence": "Now she has two seizures per month.",
                },
                "findings": [
                    {
                        "finding_id": "f1",
                        "kind": "frequency_rate",
                        "raw_value": "one seizure per day",
                        "seizure_type": "seizures",
                        "time_window": None,
                        "temporality": "historical",
                        "certainty": "asserted",
                        "negated": False,
                        "evidence": "Previously she had one seizure per day.",
                    },
                    {
                        "finding_id": "f2",
                        "kind": "frequency_rate",
                        "raw_value": "two seizures per month",
                        "seizure_type": "seizures",
                        "time_window": None,
                        "temporality": "current",
                        "certainty": "asserted",
                        "negated": False,
                        "evidence": "Now she has two seizures per month.",
                    },
                ],
                "selected_finding_ids": ["f2"],
            },
        }
    )
    cases.append(
        {
            "name": "no_reference",
            "note_text": "Blood pressure was checked today.",
            "output": {
                "answer": {"label": "no seizure frequency reference", "evidence": None},
                "findings": [],
                "selected_finding_ids": [],
            },
        }
    )
    return cases


def messages(note: str, condition: Condition) -> list[dict[str, str]]:
    if condition not in MODELS:
        raise ValueError("Unknown condition")
    payload = {
        "task": "Current seizure-frequency extraction",
        "instructions": COMMON,
        "label_rules": historical.LABEL_FORM_RULES,
        "label_forms": historical.LABEL_FORMS,
        "selection_guidance": [case["instruction"] for case in historical.CASES],
        "scope": RICH_SCOPE
        if condition == "rich"
        else ["Return only the current-frequency answer and its supporting quotation."],
        "output_schema": MODELS[condition].model_json_schema(),
        "examples": [
            {
                "note_text": c["note_text"],
                "output": c["output"] if condition == "rich" else {"answer": c["output"]["answer"]},
            }
            for c in fictional_cases()
        ],
    }
    return [
        {"role": "system", "content": json.dumps(payload, ensure_ascii=False)},
        {"role": "user", "content": json.dumps({"note_text": note}, ensure_ascii=False)},
    ]


_NUMBER = r"(?:\d+(?:\.\d+)?)"
_RANGE = rf"{_NUMBER}(?: to {_NUMBER})?"
_UNIT = r"(?:day|week|month|year)s?"
_PERIOD = rf"(?:(?:{_RANGE}|multiple) )?{_UNIT}"
_RATE = rf"(?:{_RANGE}|multiple) per {_PERIOD}"
_LABEL = re.compile(
    rf"(?:{_RATE}|(?:{_RANGE}|multiple) cluster per {_PERIOD}, "
    rf"(?:{_RANGE}|multiple) per cluster|unknown, (?:{_RANGE}|multiple) per cluster|"
    rf"seizure free(?: for (?:{_RANGE}|multiple) {_UNIT})?|unknown|"
    r"no seizure frequency reference)"
)


def native_categories(label: str) -> dict[str, str]:
    """Read-only native scoring projection; never writes back a normalized label."""
    if not _LABEL.fullmatch(label):
        raise ValueError("Label is outside the declared grammar")
    if any(float(n) <= 0 for n in re.findall(_NUMBER, label)):
        raise ValueError("Counts and denominators must be positive")
    for left, right in re.findall(rf"({_NUMBER}) to ({_NUMBER})", label):
        if float(left) > float(right):
            raise ValueError("Reversed bounds")
    frequency = label_to_frequency_record(label).monthly_frequency
    if not math.isfinite(frequency):
        raise ValueError("Non-finite frequency")
    return {"purist": str(map_purist(frequency)), "pragmatic": str(map_pragmatic(frequency))}


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def inspect_output(
    raw: str | None,
    note: str,
    condition: Condition,
    *,
    finish_reason: str | None = "stop",
) -> dict[str, Any]:
    """Strict first-pass result plus independent exact-quote diagnostics."""
    result: dict[str, Any] = {
        "received": raw is not None,
        "schema_valid": False,
        "failure": None,
        "label": None,
        "categories": None,
        "quote_slots": 0,
        "exact_quotes": 0,
        "all_quotes_exact": False,
        "no_evidence_state": False,
        "finding_count": None,
        "finding_types": [],
        "finding_certainties": [],
        "finding_temporalities": [],
    }
    if finish_reason == "length":
        result["failure"] = "truncation"
        return result
    if raw is None or not raw.strip():
        result["failure"] = "no_response"
        return result
    try:
        payload = json.loads(raw, object_pairs_hook=_unique_object)
    except (ValueError, TypeError):
        result["failure"] = "invalid_syntax"
        return result
    # Quote diagnostics include missing slots even in parseable schema-invalid objects.
    if isinstance(payload, dict):
        answer = payload.get("answer")
        answer = answer if isinstance(answer, dict) else {}
        no_reference = answer.get("label") == "no seizure frequency reference"
        quotes = [] if no_reference else [answer.get("evidence")]
        if condition == "rich" and isinstance(payload.get("findings"), list):
            quotes.extend(
                f.get("evidence") if isinstance(f, dict) else None for f in payload["findings"]
            )
        result["quote_slots"] = len(quotes)
        result["exact_quotes"] = sum(
            isinstance(q, str) and bool(q.strip()) and q in note for q in quotes
        )
        result["all_quotes_exact"] = bool(quotes) and len(quotes) == result["exact_quotes"]
    try:
        output = MODELS[condition].model_validate(payload)
        if isinstance(output, Rich):
            ids = [f.finding_id for f in output.findings]
            if (
                len(ids) != len(set(ids))
                or any(not i.strip() for i in ids)
                or len(output.selected_finding_ids) != len(set(output.selected_finding_ids))
                or not set(output.selected_finding_ids) <= set(ids)
            ):
                raise ValueError("Invalid finding references")
            no_reference = output.answer.label == "no seizure frequency reference"
            if no_reference and (ids or output.selected_finding_ids):
                raise ValueError("No-reference state must have empty findings")
            if not no_reference and (not ids or not output.selected_finding_ids):
                raise ValueError("Answer must reference at least one finding")
    except (ValidationError, ValueError):
        result["failure"] = "invalid_schema"
        return result
    result["schema_valid"] = True
    result["label"] = output.answer.label
    if isinstance(output, Rich):
        result["finding_count"] = len(output.findings)
        result["finding_types"] = [f.kind for f in output.findings]
        result["finding_certainties"] = [f.certainty for f in output.findings]
        result["finding_temporalities"] = [f.temporality for f in output.findings]
    try:
        result["categories"] = native_categories(output.answer.label)
    except (ValueError, ZeroDivisionError, OverflowError):
        result["failure"] = "invalid_target_label"
        return result
    result["no_evidence_state"] = output.answer.label == "no seizure frequency reference"
    evidence = output.answer.evidence
    missing = (
        evidence is not None
        if result["no_evidence_state"]
        else evidence is None or not evidence.strip()
    )
    if isinstance(output, Rich):
        missing |= any(not f.evidence.strip() for f in output.findings)
    if missing:
        result["failure"] = "absent_required_evidence"
    return result
