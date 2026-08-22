"""Conservative encode rules for an LLM that already writes Gan codebook labels."""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    normalize_frequency_label,
    repair_prediction_label_format_preserving,
)

from .selected_evidence_derivation import prediction_label_from_selected_evidence
from .selected_evidence_monthly_diary import monthly_diary_label_from_text
from .selected_evidence_text import words_to_numbers

CODEBOOK_ENCODE_RULE_IDS = frozenset(
    {
        "gan.encode.codebook.monthly_diary",
        "gan.encode.codebook.hourly_rate",
        "gan.encode.codebook.single_last_period",
        "gan.encode.codebook.vague_periodic_cadence",
        "gan.encode.codebook.complete_cluster_cadence",
        "gan.encode.codebook.explicit_cluster_interval",
        "gan.encode.codebook.drop_unknown_wrapper",
        "gan.encode.codebook.year_to_date_window",
    }
)

_MONTH = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"
_COUNT = r"\d+|a|an|no|zero"
_INTERVAL = r"\d+(?:\s+to\s+\d+)?"
_UNIT = r"day|week|month|year"


@dataclass(frozen=True)
class CodebookEncodeEvent:
    rule_id: str
    before: str
    after: str
    effect_class: str
    portability: str


@dataclass(frozen=True)
class CodebookEncodeTrace:
    raw_label: str | None
    final_label: str | None
    events: tuple[CodebookEncodeEvent, ...]


@dataclass(frozen=True)
class _CodebookEncodeContext:
    raw_label: str
    evidence: str
    normalized_evidence: str
    selected_event_kinds: frozenset[str]
    context_text: str | None

    def evidence_label(self) -> str | None:
        label = prediction_label_from_selected_evidence(self.evidence, self.context_text)
        return _canonical_label(label)


RuleFunction = Callable[[_CodebookEncodeContext], str | None]


@dataclass(frozen=True)
class _CodebookEncodeRule:
    rule_id: str
    effect_class: str
    portability: str
    apply: RuleFunction


def repair_codebook_label_with_evidence(
    raw: str | None,
    evidence: str,
    *,
    selected_event_kinds: Sequence[str] = (),
    context_text: str | None = None,
    enabled_rule_ids: frozenset[str] | None = None,
) -> CodebookEncodeTrace:
    """Apply high-precision repairs without broadly re-deriving a parsed label."""

    if raw is None:
        return CodebookEncodeTrace(raw_label=None, final_label=None, events=())
    raw_label = str(raw).strip()
    if not raw_label:
        return CodebookEncodeTrace(raw_label=raw, final_label=raw_label, events=())
    enabled = CODEBOOK_ENCODE_RULE_IDS if enabled_rule_ids is None else enabled_rule_ids
    unknown = enabled - CODEBOOK_ENCODE_RULE_IDS
    if unknown:
        raise ValueError(f"unknown codebook encode rule ids: {sorted(unknown)}")
    context = _CodebookEncodeContext(
        raw_label=raw_label,
        evidence=str(evidence or ""),
        normalized_evidence=normalize_frequency_label(
            words_to_numbers(str(evidence or ""))
        ),
        selected_event_kinds=frozenset(str(kind) for kind in selected_event_kinds),
        context_text=context_text,
    )
    for rule in _CODEBOOK_ENCODE_RULES:
        if rule.rule_id not in enabled:
            continue
        candidate = rule.apply(context)
        if candidate is None:
            continue
        if candidate == raw_label:
            return CodebookEncodeTrace(
                raw_label=raw,
                final_label=raw_label,
                events=(),
            )
        event = CodebookEncodeEvent(
            rule_id=rule.rule_id,
            before=raw_label,
            after=candidate,
            effect_class=rule.effect_class,
            portability=rule.portability,
        )
        return CodebookEncodeTrace(
            raw_label=raw,
            final_label=candidate,
            events=(event,),
        )
    return CodebookEncodeTrace(raw_label=raw, final_label=raw_label, events=())


def _canonical_label(label: str | None) -> str | None:
    if label is None:
        return None
    return repair_prediction_label_format_preserving(label)


def _count_value(text: str) -> int:
    if text in {"a", "an"}:
        return 1
    if text in {"no", "zero"}:
        return 0
    return int(text)


def _monthly_count_sequence(context: _CodebookEncodeContext) -> str | None:
    counts: dict[str, int] = {}
    patterns = (
        rf"\b(?P<count>{_COUNT})\s+(?:[a-z-]+\s+){{0,6}}seizures?\s+"
        rf"(?:so\s+far|to\s+date)\s+in\s+(?P<month>{_MONTH})\b",
        rf"\b(?P<count>{_COUNT})\s+(?:seizures?\s+)?in\s+(?P<month>{_MONTH})\b",
    )
    for pattern in patterns:
        for count_match in re.finditer(pattern, context.normalized_evidence):
            month = count_match.group("month")[:3]
            counts.setdefault(month, _count_value(count_match.group("count")))

    current_count: int | None = None
    current_patterns = (
        rf"\b(?P<count>{_COUNT})\s+(?:seizures?|events?)?\s*"
        r"so\s+far\s+this\s+month\b",
        rf"\bthis\s+month\s+so\s+far[^.;]{{0,40}}\b(?P<count>{_COUNT})\s+"
        r"seizures?\b",
    )
    for pattern in current_patterns:
        match = re.search(pattern, context.normalized_evidence)
        if match:
            current_count = _count_value(match.group("count"))
            break
    if current_count is None and re.search(
        r"\bthis\s+month\s+so\s+far[^.;]{0,40}\b"
        r"(?:has|had|reports?)\s+no\s+seizures?\b",
        context.normalized_evidence,
    ):
        current_count = 0
    if current_count is not None:
        counts["this_month"] = current_count
    if len(counts) < 2:
        return None
    return _canonical_label(f"{sum(counts.values())} per {len(counts)} month")


def _monthly_diary(context: _CodebookEncodeContext) -> str | None:
    sequence = _monthly_count_sequence(context)
    if sequence is not None:
        return sequence
    return _canonical_label(monthly_diary_label_from_text(context.evidence))


def _hourly_rate(context: _CodebookEncodeContext) -> str | None:
    if context.raw_label != "unknown":
        return None
    if not re.search(
        r"\b(?:\d+|multiple|several)\s*(?:/|per)\s*(?:h|hr|hour)\b",
        context.normalized_evidence,
    ):
        return None
    return context.evidence_label()


def _single_last_period(context: _CodebookEncodeContext) -> str | None:
    if context.raw_label != "unknown":
        return None
    if not re.search(
        rf"\b(?:single|one|1)\b.{{0,50}}\b(?:last|past)\s+(?:{_UNIT})\b",
        context.normalized_evidence,
    ):
        return None
    return context.evidence_label()


def _vague_periodic_cadence(context: _CodebookEncodeContext) -> str | None:
    if context.raw_label != "unknown":
        return None
    evidence = context.normalized_evidence
    if not (
        re.search(r"\bmost\s+weekdays\b", evidence)
        or re.search(
            r"\bmultiple\s+days\b.{0,40}\b(?:past|last)\s+week\b",
            evidence,
        )
    ):
        return None
    return context.evidence_label()


def _complete_cluster_cadence(context: _CodebookEncodeContext) -> str | None:
    if "cluster_frequency" not in context.selected_event_kinds:
        return None
    if not (
        context.raw_label == "unknown"
        or context.raw_label == "unknown cluster count"
        or context.raw_label.startswith("unknown,")
    ):
        return None
    candidate = context.evidence_label()
    if candidate is None or "cluster per" not in candidate:
        return None
    return candidate


def _explicit_cluster_interval(context: _CodebookEncodeContext) -> str | None:
    if not context.raw_label.startswith("unknown"):
        return None
    match = re.search(
        rf"\bclusters?\b.{{0,80}}?\b(?:generally\s+)?"
        rf"(?:spaced\s+|every\s+)(?P<interval>{_INTERVAL})\s+"
        rf"(?P<unit>{_UNIT})s?\b",
        context.normalized_evidence,
    )
    if not match:
        return None
    return _canonical_label(
        f"1 per {match.group('interval')} {match.group('unit')}"
    )


def _drop_unknown_wrapper(context: _CodebookEncodeContext) -> str | None:
    if context.raw_label != "unknown, 1 per day":
        return None
    candidate = context.evidence_label()
    return candidate if candidate == "1 per day" else None


def _year_to_date_window(context: _CodebookEncodeContext) -> str | None:
    if not re.search(
        r"\b(?:so\s+far\s+this\s+year|this\s+year\s+to\s+date|\d{4}\s+so\s+far)\b",
        context.normalized_evidence,
    ):
        return None
    return context.evidence_label()


_CODEBOOK_ENCODE_RULES = (
    _CodebookEncodeRule(
        rule_id="gan.encode.codebook.monthly_diary",
        effect_class="semantic_deterministic_repair",
        portability="seizure_frequency",
        apply=_monthly_diary,
    ),
    _CodebookEncodeRule(
        rule_id="gan.encode.codebook.hourly_rate",
        effect_class="semantic_deterministic_repair",
        portability="seizure_frequency",
        apply=_hourly_rate,
    ),
    _CodebookEncodeRule(
        rule_id="gan.encode.codebook.single_last_period",
        effect_class="semantic_deterministic_repair",
        portability="seizure_frequency",
        apply=_single_last_period,
    ),
    _CodebookEncodeRule(
        rule_id="gan.encode.codebook.vague_periodic_cadence",
        effect_class="semantic_deterministic_repair",
        portability="seizure_frequency",
        apply=_vague_periodic_cadence,
    ),
    _CodebookEncodeRule(
        rule_id="gan.encode.codebook.complete_cluster_cadence",
        effect_class="semantic_deterministic_repair",
        portability="seizure_frequency",
        apply=_complete_cluster_cadence,
    ),
    _CodebookEncodeRule(
        rule_id="gan.encode.codebook.explicit_cluster_interval",
        effect_class="semantic_deterministic_repair",
        portability="seizure_frequency",
        apply=_explicit_cluster_interval,
    ),
    _CodebookEncodeRule(
        rule_id="gan.encode.codebook.drop_unknown_wrapper",
        effect_class="semantic_deterministic_repair",
        portability="benchmark_format",
        apply=_drop_unknown_wrapper,
    ),
    _CodebookEncodeRule(
        rule_id="gan.encode.codebook.year_to_date_window",
        effect_class="semantic_deterministic_repair",
        portability="seizure_frequency",
        apply=_year_to_date_window,
    ),
)
