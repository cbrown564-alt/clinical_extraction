"""Agent-callable tool contracts for Gan 2026 Phase 5."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.core.evidence import locate_evidence
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic import (
    deterministic_extraction,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
)

ParserPortability = Literal[
    "general",
    "clinical_epilepsy",
    "seizure_frequency",
    "gan2026_specific",
    "benchmark_format",
    "unknown",
]


class ParserCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    candidate_kind: str
    evidence_text: str
    start_char: int | None
    end_char: int | None
    rule_id: str
    rule_group: str
    portability: ParserPortability
    match_groups: dict[str, str | None] = Field(default_factory=dict)


class ParserToolResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: Literal["parse_seizure_frequency_candidates"] = (
        "parse_seizure_frequency_candidates"
    )
    schema_version: Literal["gan2026_agent_parser_tool_v0"] = "gan2026_agent_parser_tool_v0"
    candidates: list[ParserCandidate]
    parse_warnings: list[str] = Field(default_factory=list)


class BoundaryGuideResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: Literal["read_boundary_guide"] = "read_boundary_guide"
    schema_version: Literal["gan2026_boundary_guide_v0"] = "gan2026_boundary_guide_v0"
    guide_id: str
    version: str
    title: str
    decision_criteria: list[str]
    examples: list[str]
    cautions: list[str]
    max_output_tokens: int


def parse_seizure_frequency_candidates(
    note_text: str,
    *,
    max_candidates: int = 12,
    ablation_config: AblationConfig | None = None,
) -> ParserToolResult:
    """Return source-near parser candidates without labels, row IDs, split data, or gold."""

    raw_candidates = deterministic_extraction._extract_candidates(
        note_text, ablation_config or AblationConfig()
    )
    candidates: list[ParserCandidate] = []
    warnings: list[str] = []
    if len(raw_candidates) > max_candidates:
        warnings.append("candidate_limit_applied")
    for index, raw_candidate in enumerate(raw_candidates[:max_candidates], start=1):
        span = locate_evidence(note_text, raw_candidate.evidence)
        start_char, end_char = span if span else (None, None)
        if span is None:
            warnings.append(f"evidence_span_unresolved:{index}")
        candidates.append(
            ParserCandidate(
                candidate_id=f"parser_candidate_{index}",
                candidate_kind=raw_candidate.kind.value,
                evidence_text=raw_candidate.evidence,
                start_char=start_char,
                end_char=end_char,
                rule_id=raw_candidate.rule_id,
                rule_group=(
                    raw_candidate.rule_group.value
                    if raw_candidate.rule_group is not None
                    else "unknown"
                ),
                portability=(
                    raw_candidate.portability.value
                    if raw_candidate.portability is not None
                    else "unknown"
                ),
                match_groups=dict(raw_candidate.match_groups),
            )
        )
    if not candidates:
        warnings.append("no_candidates_found")
    return ParserToolResult(candidates=candidates, parse_warnings=warnings)


def read_boundary_guide(query: str) -> BoundaryGuideResult:
    """Return a compact, split-neutral guide selected by ID, title, or trigger phrase."""

    normalized_query = _normalize_key(query)
    guide_id = _GUIDE_ALIASES.get(normalized_query)
    if guide_id is None:
        guide_id = next(
            (
                candidate_id
                for candidate_id, guide in _GUIDES.items()
                if normalized_query in _normalize_key(guide.title)
                or any(normalized_query in _normalize_key(alias) for alias in guide.aliases)
            ),
            None,
        )
    if guide_id is None:
        available = ", ".join(sorted(_GUIDES))
        raise KeyError(f"Unknown boundary guide: {query!r}. Available guides: {available}")
    return _GUIDES[guide_id].to_result()


class _BoundaryGuide(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    guide_id: str
    version: str = "2026-06-12.phase5"
    title: str
    aliases: tuple[str, ...]
    decision_criteria: tuple[str, ...]
    examples: tuple[str, ...]
    cautions: tuple[str, ...]
    max_output_tokens: int = 260

    def to_result(self) -> BoundaryGuideResult:
        return BoundaryGuideResult(
            guide_id=self.guide_id,
            version=self.version,
            title=self.title,
            decision_criteria=list(self.decision_criteria),
            examples=list(self.examples),
            cautions=list(self.cautions),
            max_output_tokens=self.max_output_tokens,
        )


def _normalize_key(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", " ").replace("-", " ").split())


_GUIDES: dict[str, _BoundaryGuide] = {
    "multiple_current_events_aggregation": _BoundaryGuide(
        guide_id="multiple_current_events_aggregation",
        title="Multiple current seizure events and aggregation",
        aliases=("multiple current seizure events", "aggregation", "multiple semiologies"),
        decision_criteria=(
            "Identify current or recent recurring seizure burdens before historical burdens.",
            "When semiologies have different current rates, preserve the highest current burden.",
            "Do not add unrelated event counts unless the note gives a shared time window.",
        ),
        examples=(
            "Focal events twice weekly plus tonic-clonic events yearly supports the weekly burden.",
            "Two event types in separate windows need separate candidates before selection.",
        ),
        cautions=(
            "Avoid converting a list of isolated dates into a recurring rate without a window.",
        ),
    ),
    "seizure_free_event_conflict": _BoundaryGuide(
        guide_id="seizure_free_event_conflict",
        title="Seizure-free period plus seizure event conflict",
        aliases=("seizure free conflict", "no events conflict"),
        decision_criteria=(
            "Check whether no-event language applies to all seizures or only one semiology.",
            "Prefer explicit current events over broad control language when both are current.",
            "Preserve seizure-free only when the event mention is historical or negated.",
        ),
        examples=(
            "No tonic-clonic seizures but weekly focal events is not globally seizure-free.",
        ),
        cautions=("Do not erase a current frequency-bearing event with a generic stable phrase.",),
    ),
    "cluster_frequency_vs_incidental_clustering": _BoundaryGuide(
        guide_id="cluster_frequency_vs_incidental_clustering",
        title="Cluster frequency versus incidental clustering",
        aliases=("cluster frequency versus incidental clustering", "cluster frequency"),
        decision_criteria=(
            "Use a cluster label only when the note gives cluster cadence or count in a period.",
            "Keep incidental descriptions of events occurring close together as ordinary evidence.",
            "Require enough text to distinguish cluster count from events per cluster.",
        ),
        examples=(
            "Two clusters per month with three events each supports a cluster-frequency candidate.",
            "Several seizures clustered together last weekend is not a recurring cluster cadence.",
        ),
        cautions=("Do not infer events per cluster from the word cluster alone.",),
    ),
    "last_event_only_vs_recurring_rate": _BoundaryGuide(
        guide_id="last_event_only_vs_recurring_rate",
        title="Last-event-only versus recurring rate",
        aliases=("last event only", "last seizure only", "recurring rate"),
        decision_criteria=(
            "Treat a last-event date as timing evidence, not a recurring frequency by itself.",
            "Use recurring rates only when the note states repeated events over a period.",
            "A last event can support seizure-free duration only when absence since then is clear.",
        ),
        examples=("Last seizure in March without a rate remains last-event-only.",),
        cautions=(
            "Do not divide one event by time since it unless policy explicitly allows it.",
        ),
    ),
    "unknown_frequency_vs_no_reference": _BoundaryGuide(
        guide_id="unknown_frequency_vs_no_reference",
        title="Unknown frequency versus no seizure-frequency reference",
        aliases=("unknown versus no reference", "no seizure frequency reference"),
        decision_criteria=(
            "Use unknown when seizure-frequency evidence exists but cannot be converted.",
            "Use no-reference only when no seizure-frequency evidence is present.",
            "Qualitative change or vague burden is evidence, even when no numeric rate is present.",
        ),
        examples=("Seizures occur occasionally supports unknown rather than no-reference.",),
        cautions=("Do not use no-reference as a fallback for hard-to-normalize evidence.",),
    ),
    "current_vs_historical_window": _BoundaryGuide(
        guide_id="current_vs_historical_window",
        title="Current versus historical window selection",
        aliases=("current historical window", "historical frequency"),
        decision_criteria=(
            "Prefer the current assessment window over remote historical baselines.",
            "Use historical rates only when no current burden is stated.",
            "Keep improved or worsened temporal qualifiers with the candidate evidence.",
        ),
        examples=("Previously daily, now monthly supports the current monthly burden.",),
        cautions=("Do not average historical and current windows into one rate.",),
    ),
    "different_semiology_burdens": _BoundaryGuide(
        guide_id="different_semiology_burdens",
        title="Multiple semiologies with different burdens",
        aliases=("different semiology burdens", "multiple semiologies"),
        decision_criteria=(
            "Create separate candidates when seizure types carry different frequencies.",
            "Select the clinically prediction-bearing burden according to the experiment policy.",
            "Keep semiology text in evidence so later adjudication can inspect the choice.",
        ),
        examples=("Absences daily and focal events monthly should remain distinct candidates.",),
        cautions=("Do not collapse semiologies before the agent has made a selection.",),
    ),
}

_GUIDE_ALIASES = {
    _normalize_key(guide_id): guide_id
    for guide_id in _GUIDES
} | {alias: guide_id for guide_id, guide in _GUIDES.items() for alias in guide.aliases}
