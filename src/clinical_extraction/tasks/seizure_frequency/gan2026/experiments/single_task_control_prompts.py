"""Frozen prompt/schema stubs for Gan 2026 RQ1/RQ2 single-task controls."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord

FROZEN_PROMPT_FAMILY = "gan2026_rq1_rq2_single_task_controls"
PROMPT_FREEZE_DATE = "2026-06-04"
PANEL_ID = "balanced_validation50"
SPLIT_MANIFEST = "gan2026_split_v1"
REPRESENTATION_TYPE = "single_task_control_stub"
NO_FREQUENCY_LABEL_INSTRUCTION = "Do not provide a seizure-frequency label."

PROMPT_VERSIONS = {
    "candidate_only": "gan2026_candidate_only_v0_frozen_2026_06_04",
    "gold_query_evidence_only": "gan2026_gold_query_evidence_only_v0_frozen_2026_06_04",
    "candidate_conditioned_evidence_only": (
        "gan2026_candidate_conditioned_evidence_only_v0_frozen_2026_06_04"
    ),
    "projection_only": "gan2026_projection_only_v0_frozen_2026_06_04",
    "projection_only_instruction_heavy": (
        "gan2026_projection_only_instruction_heavy_v0_frozen_2026_06_04"
    ),
    "candidate_plus_evidence": "gan2026_candidate_plus_evidence_v0_frozen_2026_06_04",
    "evidence_plus_projection": "gan2026_evidence_plus_projection_v0_frozen_2026_06_04",
    "candidate_plus_evidence_plus_projection": (
        "gan2026_candidate_plus_evidence_plus_projection_v0_frozen_2026_06_04"
    ),
}

STOP_RULES = {
    "panel_first": "Run balanced_validation50 before hidden_family_hard_panel.",
    "validation_only": "Use validation rows only; locked test row-level inspection is excluded.",
    "one_task": "Each prompt optimizes only its named component task.",
    "component_first": "Interpret component metrics before final-label correctness.",
    "evidence_exactness": "Every evidence span must be an exact source substring when present.",
}


CandidateKind = Literal[
    "frequency_rate",
    "cluster_frequency",
    "seizure_free",
    "last_event_only",
    "unknown_frequency",
    "no_reference",
]
Temporality = Literal["current", "recent", "historical", "future", "unclear"]
AssertionStatus = Literal["asserted", "negated", "hypothetical", "uncertain"]
EvidenceRole = Literal[
    "decisive",
    "supporting_context",
    "conflicting",
    "historical",
    "future_planned",
    "non_seizure_or_indirect_context",
    "ambiguous",
    "insufficient",
]
CandidateSupportStatus = Literal[
    "supports_candidate",
    "contradicts_candidate",
    "incompletely_supports_candidate",
    "not_applicable",
]
ProjectionDecisionKind = Literal[
    "frequency",
    "seizure_free",
    "unknown",
    "no_reference",
    "unresolved_multiple",
    "abstain",
]
FrequencyComponentName = Literal[
    "count",
    "timeframe",
    "unit",
    "rate_time_basis",
    "cluster_cadence",
    "per_cluster_burden",
    "seizure_free_duration",
]


class FrequencyComponents(BaseModel):
    """Structured pieces of a documented seizure-frequency expression."""

    model_config = ConfigDict(extra="forbid", frozen=True, title="FrequencyComponents")

    count: str | None = Field(
        default=None,
        description="Documented count or quantity, such as '2', 'several', or 'none'.",
    )
    timeframe: str | None = Field(
        default=None,
        description="Documented time interval or duration, such as 'per week' or '6 months'.",
    )
    unit: str | None = Field(
        default=None,
        description="Documented event unit, such as 'seizures', 'clusters', or 'episodes'.",
    )
    rate_time_basis: str | None = Field(
        default=None,
        description="Time basis for a rate, such as 'day', 'week', 'month', or 'year'.",
    )
    cluster_cadence: str | None = Field(
        default=None,
        description="How often seizure clusters occur, when documented.",
    )
    per_cluster_burden: str | None = Field(
        default=None,
        description="How many seizures occur within each cluster, when documented.",
    )
    seizure_free_duration: str | None = Field(
        default=None,
        description="Duration of seizure freedom, when documented.",
    )


class FrozenCandidateOnlyCandidate(BaseModel):
    """One documented seizure-frequency fact."""

    model_config = ConfigDict(extra="forbid", frozen=True, title="Candidate")

    candidate_id: str = Field(description="Stable id such as c1, c2, or c3.")
    source_id: str = Field(description="Identifier of the source document containing the evidence.")
    evidence: str = Field(description="Exact substring copied from the source document.")
    candidate_kind: CandidateKind = Field(description="Type of seizure-frequency fact.")
    temporality: Temporality = Field(
        description="Whether the fact is current, recent, old, planned, or unclear."
    )
    assertion_status: AssertionStatus = Field(
        description=(
            "Whether the note asserts, negates, hypothesizes, or is uncertain about the fact."
        )
    )
    applies_to: str | None = Field(
        default=None,
        description="Seizure type, event type, or clinical target the fact describes.",
    )
    components: FrequencyComponents = Field(
        description="Structured pieces explicitly documented in the evidence."
    )
    ambiguity_reasons: tuple[str, ...] = Field(
        description="Short reasons the fact may be vague, competing, old, or uncertain."
    )
    normalization_note: str | None = Field(
        default=None,
        description=(
            "Brief note about count, timeframe, or duration wording; do not infer beyond the text."
        ),
    )
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence that this candidate faithfully reflects the note."
    )
    rationale: str = Field(description="Brief explanation tied to the copied evidence.")


class FrozenCandidateOnlyPacket(BaseModel):
    """Collection of documented seizure-frequency facts."""

    model_config = ConfigDict(extra="forbid", frozen=True, title="CandidatePacket")

    candidates: tuple[FrozenCandidateOnlyCandidate, ...] = Field(
        description="All documented seizure-frequency facts found in the note."
    )
    note_level_ambiguity_reasons: tuple[str, ...] = Field(
        description="Uncertainties affecting the whole note, if any."
    )


class FrozenEvidenceOnlySpan(BaseModel):
    """Evidence span with frequency components."""

    model_config = ConfigDict(extra="forbid", frozen=True, title="EvidenceSpan")

    evidence_id: str = Field(description="Stable id such as e1, e2, or e3.")
    source_id: str = Field(description="Identifier of the source document containing the evidence.")
    evidence: str = Field(description="Exact substring copied from the source document.")
    role: EvidenceRole = Field(description="How this evidence relates to seizure frequency.")
    support_status: CandidateSupportStatus = Field(
        description=(
            "How this evidence relates to the supplied candidate, or not_applicable "
            "when no candidate was supplied."
        )
    )
    applies_to: str | None = Field(
        default=None,
        description="Seizure type, event type, or clinical target the evidence describes.",
    )
    extracted_components: FrequencyComponents = Field(
        description=(
            "Count, timeframe, unit, and related components explicitly present in the evidence."
        )
    )
    missing_components: tuple[FrequencyComponentName, ...] = Field(
        description="Components needed for interpretation but absent from the evidence."
    )
    conflict_notes: tuple[str, ...] = Field(
        description="Brief notes about conflicting or competing evidence."
    )
    ambiguity_reasons: tuple[str, ...] = Field(
        description="Short reasons the evidence is vague, incomplete, old, or uncertain."
    )
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence that the evidence was selected and classified correctly."
    )
    rationale: str = Field(description="Brief explanation tied to the copied evidence.")


class FrozenEvidenceOnlyPacket(BaseModel):
    """Collection of selected evidence spans."""

    model_config = ConfigDict(extra="forbid", frozen=True, title="EvidencePacket")

    selected_evidence: tuple[FrozenEvidenceOnlySpan, ...] = Field(
        description="Evidence spans relevant to the current seizure-frequency question."
    )
    insufficient_evidence_reason: str | None = Field(
        default=None,
        description="Why the note does not provide enough evidence, if applicable.",
    )


class FrozenProjectionOnlyDecision(BaseModel):
    """Frequency interpretation from supplied candidates and exact evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True, title="ProjectionDecision")

    decision_kind: ProjectionDecisionKind
    selected_candidate_ids: tuple[str, ...] = Field(
        description="Ids of supplied candidates used for the interpretation."
    )
    seizure_frequency_label: str | None = Field(
        default=None,
        description="Concise frequency label supported by the supplied information, or null.",
    )
    abstention_reason: str | None = Field(
        default=None,
        description="Reason no frequency label can be provided, if applicable.",
    )
    uncertainty_reasons: tuple[str, ...] = Field(
        description="Short reasons the supplied information remains uncertain or competing."
    )
    decision_notes: tuple[str, ...] = Field(
        description="Brief notes explaining important interpretation choices."
    )
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence in the interpretation."
    )
    rationale: str = Field(description="Brief explanation tied to the supplied evidence.")


class FrozenCandidatePlusEvidencePacket(BaseModel):
    """Candidate facts plus selected evidence for each fact."""

    model_config = ConfigDict(extra="forbid", frozen=True, title="CandidatePlusEvidencePacket")

    candidates: tuple[FrozenCandidateOnlyCandidate, ...] = Field(
        description="Documented seizure-frequency facts found in the note."
    )
    selected_evidence: tuple[FrozenEvidenceOnlySpan, ...] = Field(
        description="Exact evidence spans supporting or contextualizing the candidates."
    )
    note_level_ambiguity_reasons: tuple[str, ...] = Field(
        description="Uncertainties affecting the whole note, if any."
    )
    insufficient_evidence_reason: str | None = Field(
        default=None,
        description="Why the note does not provide enough evidence, if applicable.",
    )


class FrozenEvidencePlusProjectionPacket(BaseModel):
    """Selected evidence plus a projection decision."""

    model_config = ConfigDict(extra="forbid", frozen=True, title="EvidencePlusProjectionPacket")

    selected_evidence: tuple[FrozenEvidenceOnlySpan, ...] = Field(
        description="Evidence spans relevant to the supplied candidate and final interpretation."
    )
    projection_decision: FrozenProjectionOnlyDecision = Field(
        description="Final interpretation from the selected evidence."
    )
    insufficient_evidence_reason: str | None = Field(
        default=None,
        description="Why the note does not provide enough evidence, if applicable.",
    )


class FrozenCandidateEvidenceProjectionPacket(BaseModel):
    """Candidate facts, evidence, and a projection decision."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        title="CandidateEvidenceProjectionPacket",
    )

    candidates: tuple[FrozenCandidateOnlyCandidate, ...] = Field(
        description="Documented seizure-frequency facts found in the note."
    )
    selected_evidence: tuple[FrozenEvidenceOnlySpan, ...] = Field(
        description="Evidence spans supporting or contextualizing the candidates."
    )
    projection_decision: FrozenProjectionOnlyDecision = Field(
        description="Final interpretation from the selected candidates and evidence."
    )
    note_level_ambiguity_reasons: tuple[str, ...] = Field(
        description="Uncertainties affecting the whole note, if any."
    )
    insufficient_evidence_reason: str | None = Field(
        default=None,
        description="Why the note does not provide enough evidence, if applicable.",
    )


def build_candidate_only_prompt_input(
    record: GanFrequencyRecord,
    *,
    row_panel_id: str = PANEL_ID,
    source_id: str = "note",
) -> str:
    """Prepare instructions for extracting documented seizure-frequency facts."""

    payload = _base_payload(record)
    payload.update(
        {
            "task": "Extract documented seizure-frequency facts from the note.",
            "instructions": [
                "Read the full note.",
                (
                    "Return factual statements that closely match the wording and context "
                    "in the note."
                ),
                (
                    "Use multiple candidates when the note contains multiple plausible "
                    "current, recent, or competing facts."
                ),
                (
                    "Mark unsupported, vague, competing, historical, future, and indirect "
                    "context explicitly."
                ),
                (
                    "Indirect context means non-seizure information that may affect "
                    "interpretation, such as rescue-medication use, medication changes, "
                    "injuries, or safety advice."
                ),
                ("Use 'no_reference' only when the note has no usable seizure-frequency evidence."),
                "Every evidence value must be an exact substring from the note.",
                (
                    "Use normalization_note only for count, duration, or timeframe wording "
                    "that is explicitly present in the text."
                ),
                "Return exactly one JSON object matching candidate_only_schema.",
            ],
            "source_documents": [{"source_id": source_id, "text": record.note_text}],
            "candidate_only_schema": _schema_stub(FrozenCandidateOnlyPacket),
        }
    )
    return _json(payload)


def build_gold_query_evidence_only_prompt_input(
    record: GanFrequencyRecord,
    *,
    row_panel_id: str = PANEL_ID,
    source_id: str = "note",
) -> str:
    """Prepare instructions for selecting seizure-frequency evidence from a note."""

    payload = _base_payload(record)
    payload.update(
        {
            "task": "Select evidence relevant to the current seizure-frequency question.",
            "query": (
                "What evidence in this note is decisive or relevant for current seizure frequency?"
            ),
            "instructions": [
                (
                    "Select decisive evidence and any necessary supporting, conflicting, "
                    "ambiguous, or historical context."
                ),
                (
                    "Classify each evidence span's role and list missing components such "
                    "as count, timeframe, or units."
                ),
                "Do not invent components that are absent from the text.",
                "Every evidence value must be an exact substring from the note.",
                NO_FREQUENCY_LABEL_INSTRUCTION,
                "Return exactly one JSON object matching evidence_only_schema.",
            ],
            "source_documents": [{"source_id": source_id, "text": record.note_text}],
            "evidence_only_schema": _schema_stub(FrozenEvidenceOnlyPacket),
        }
    )
    return _json(payload)


def build_candidate_conditioned_evidence_only_prompt_input(
    record: GanFrequencyRecord,
    candidate: Mapping[str, Any],
    *,
    row_panel_id: str = PANEL_ID,
    source_id: str = "note",
) -> str:
    """Prepare instructions for checking evidence against one supplied candidate."""

    payload = _base_payload(record)
    payload.update(
        {
            "task": (
                "Judge whether exact note evidence supports, contradicts, or only partly "
                "supports the supplied seizure-frequency candidate."
            ),
            "instructions": [
                "Use the supplied candidate as the target for evidence review.",
                (
                    "Select exact evidence spans that support, contradict, incompletely "
                    "support, or contextualize the candidate."
                ),
                ("Classify role, support status, missing components, conflicts, and ambiguity."),
                "Every evidence value must be an exact substring from the note.",
                NO_FREQUENCY_LABEL_INSTRUCTION,
                "Return exactly one JSON object matching evidence_only_schema.",
            ],
            "candidate": dict(candidate),
            "source_documents": [{"source_id": source_id, "text": record.note_text}],
            "evidence_only_schema": _schema_stub(FrozenEvidenceOnlyPacket),
        }
    )
    return _json(payload)


def build_projection_only_prompt_input(
    record: GanFrequencyRecord,
    candidates: Sequence[Mapping[str, Any]],
    evidence: Sequence[Mapping[str, Any]],
    *,
    row_panel_id: str = PANEL_ID,
    input_source: str,
) -> str:
    """Prepare instructions for choosing an interpretation from supplied evidence."""

    payload = _base_payload(record)
    payload.update(
        {
            "task": (
                "Choose the current seizure-frequency interpretation supported by the "
                "supplied candidates and evidence."
            ),
            "instructions": [
                "Use only the supplied candidates and evidence.",
                (
                    "Prefer current or recent seizure-frequency states over historical, "
                    "future, hypothetical, medication, rescue-medication, or indirect-only "
                    "states."
                ),
                (
                    "Preserve uncertainty when supplied candidates are genuinely competing "
                    "or missing count, timeframe, or unit details needed for a frequency "
                    "label."
                ),
                (
                    "When a supplied candidate clearly states a frequency in ordinary "
                    "language, express it as a concise seizure-frequency label."
                ),
                ("Return seizure_frequency_label only when the supplied information supports one."),
                "Return exactly one JSON object matching projection_only_schema.",
            ],
            "input_source": input_source,
            "candidates": [dict(candidate) for candidate in candidates],
            "evidence": [dict(evidence_item) for evidence_item in evidence],
            "projection_only_schema": _schema_stub(FrozenProjectionOnlyDecision),
        }
    )
    return _json(payload)


def build_projection_only_instruction_heavy_prompt_input(
    record: GanFrequencyRecord,
    candidates: Sequence[Mapping[str, Any]],
    evidence: Sequence[Mapping[str, Any]],
    *,
    row_panel_id: str = PANEL_ID,
    input_source: str,
) -> str:
    """Prepare a principle-heavy projection prompt for fixed candidates/evidence."""

    payload = _base_payload(record)
    payload.update(
        {
            "task": (
                "Choose the current seizure-frequency interpretation supported by the "
                "supplied candidates and evidence."
            ),
            "instructions": [
                "Use only the supplied candidates and evidence.",
                (
                    "This task requires a policy choice. Different reviewers may choose "
                    "different answers unless the policy is stated, so apply the principles "
                    "below consistently."
                ),
                (
                    "Prefer the current or recent overall seizure state over older history, "
                    "future plans, medication context, safety advice, or indirect context."
                ),
                (
                    "When a current explicit summary conflicts with an older or derived "
                    "rate, choose the current explicit summary unless the supplied evidence "
                    "shows it is not about seizures."
                ),
                (
                    "Do not choose seizure freedom when any supplied current or recent "
                    "asserted seizure, cluster, spell, or event candidate remains active."
                ),
                (
                    "A statement that one seizure type is absent does not prove overall "
                    "seizure freedom if another seizure type or spell is current or recent."
                ),
                (
                    "Conditional events, such as events only with missed sleep or other "
                    "triggers, are still events. If their rate cannot be stated, choose "
                    "'unknown' rather than seizure freedom."
                ),
                (
                    "Cluster information can describe two separate things: how often "
                    "clusters happen and how many seizures happen inside each cluster. "
                    "If only the number inside each cluster is supplied, keep that visible "
                    "and mark the overall rate as uncertain."
                ),
                (
                    "If the supplied evidence says there were multiple seizures in a day "
                    "or other time period, a precise numeric count is not required. Use an "
                    "unresolved-multiple decision and render a concise label such as "
                    "'multiple per day' when the time period is clear."
                ),
                (
                    "If a count and time basis are explicitly supplied in ordinary language, "
                    "render the concise label even when the wording is approximate, bounded, "
                    "or phrased as 'up to'."
                ),
                (
                    "Use 'unknown' when seizure-frequency evidence exists but the current "
                    "rate cannot be chosen because the supplied candidates are conditional, "
                    "competing, vague, or incomplete."
                ),
                (
                    "Use 'no_reference' only when the supplied candidates and evidence contain "
                    "no usable seizure-frequency information."
                ),
                (
                    "Abstain only when the supplied candidates or evidence are internally "
                    "invalid for this task, not merely because the clinical answer is uncertain."
                ),
                (
                    "Return seizure_frequency_label when the decision can be expressed as a "
                    "concise label; otherwise explain the uncertainty or abstention."
                ),
                "Return exactly one JSON object matching projection_only_schema.",
            ],
            "input_source": input_source,
            "candidates": [dict(candidate) for candidate in candidates],
            "evidence": [dict(evidence_item) for evidence_item in evidence],
            "projection_only_schema": _schema_stub(FrozenProjectionOnlyDecision),
        }
    )
    return _json(payload)


def build_candidate_plus_evidence_prompt_input(
    record: GanFrequencyRecord,
    *,
    row_panel_id: str = PANEL_ID,
    source_id: str = "note",
) -> str:
    """Prepare instructions for combined candidate and evidence extraction."""

    payload = _base_payload(record)
    payload.update(
        {
            "task": (
                "Extract documented seizure-frequency candidates and select exact "
                "evidence for them."
            ),
            "instructions": [
                "Read the full note.",
                "Return all documented current, recent, or competing seizure-frequency facts.",
                "For each important fact, select exact evidence spans from the note.",
                "Preserve ambiguity instead of choosing a final benchmark label.",
                "Do not invent components that are absent from the text.",
                "Every evidence value must be an exact substring from the note.",
                NO_FREQUENCY_LABEL_INSTRUCTION,
                "Return exactly one JSON object matching candidate_plus_evidence_schema.",
            ],
            "source_documents": [{"source_id": source_id, "text": record.note_text}],
            "candidate_plus_evidence_schema": _schema_stub(FrozenCandidatePlusEvidencePacket),
        }
    )
    return _json(payload)


def build_evidence_plus_projection_prompt_input(
    record: GanFrequencyRecord,
    candidate: Mapping[str, Any],
    *,
    row_panel_id: str = PANEL_ID,
    source_id: str = "note",
) -> str:
    """Prepare instructions for combined evidence selection and projection."""

    payload = _base_payload(record)
    payload.update(
        {
            "task": (
                "Select exact evidence for the supplied candidate and choose the current "
                "seizure-frequency interpretation."
            ),
            "instructions": [
                "Use the supplied candidate as the target for evidence review.",
                "Select exact evidence spans that support, contradict, or contextualize it.",
                (
                    "Then choose the current interpretation from that evidence, preserving "
                    "uncertainty when operands are missing or genuinely competing."
                ),
                "Do not invent components that are absent from the text.",
                "Every evidence value must be an exact substring from the note.",
                "Return exactly one JSON object matching evidence_plus_projection_schema.",
            ],
            "candidate": dict(candidate),
            "source_documents": [{"source_id": source_id, "text": record.note_text}],
            "evidence_plus_projection_schema": _schema_stub(FrozenEvidencePlusProjectionPacket),
        }
    )
    return _json(payload)


def build_candidate_plus_evidence_plus_projection_prompt_input(
    record: GanFrequencyRecord,
    *,
    row_panel_id: str = PANEL_ID,
    source_id: str = "note",
) -> str:
    """Prepare instructions for bundled candidate, evidence, and projection output."""

    payload = _base_payload(record)
    payload.update(
        {
            "task": (
                "Extract seizure-frequency candidates, select exact evidence, and choose "
                "the current interpretation."
            ),
            "instructions": [
                "Read the full note.",
                "Return documented seizure-frequency candidates before making a decision.",
                "Select exact evidence spans supporting or contextualizing those candidates.",
                (
                    "Choose a final interpretation only after preserving ambiguity and "
                    "competing current facts."
                ),
                "Do not invent components that are absent from the text.",
                "Every evidence value must be an exact substring from the note.",
                "Return exactly one JSON object matching candidate_evidence_projection_schema.",
            ],
            "source_documents": [{"source_id": source_id, "text": record.note_text}],
            "candidate_evidence_projection_schema": _schema_stub(
                FrozenCandidateEvidenceProjectionPacket
            ),
        }
    )
    return _json(payload)


def _base_payload(record: GanFrequencyRecord) -> dict[str, Any]:
    return {
        "source_row_index": record.source_row_index,
    }


def _schema_stub(model: type[BaseModel]) -> dict[str, Any]:
    schema = deepcopy(model.model_json_schema())
    _rename_schema_defs(schema)
    _strip_schema_titles_only(schema)
    return schema


def _rename_schema_defs(schema: dict[str, Any]) -> None:
    defs = schema.get("$defs")
    if not isinstance(defs, dict):
        return
    replacements = {
        "FrozenCandidateOnlyCandidate": "Candidate",
        "FrozenEvidenceOnlySpan": "EvidenceSpan",
    }
    for old_name, new_name in replacements.items():
        if old_name in defs:
            defs[new_name] = defs.pop(old_name)
            _replace_schema_refs(schema, f"#/$defs/{old_name}", f"#/$defs/{new_name}")


def _replace_schema_refs(value: Any, old_ref: str, new_ref: str) -> None:
    if isinstance(value, dict):
        if value.get("$ref") == old_ref:
            value["$ref"] = new_ref
        for child in value.values():
            _replace_schema_refs(child, old_ref, new_ref)
    elif isinstance(value, list):
        for child in value:
            _replace_schema_refs(child, old_ref, new_ref)


def _strip_schema_titles_only(value: Any) -> None:
    if isinstance(value, dict):
        value.pop("title", None)
        for child in value.values():
            _strip_schema_titles_only(child)
    elif isinstance(value, list):
        for child in value:
            _strip_schema_titles_only(child)


def _json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
