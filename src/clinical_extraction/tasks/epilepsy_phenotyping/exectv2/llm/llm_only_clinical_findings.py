"""ExECTv2 llm_only clinical-findings SeizureFrequency extractor.

The model emits source-near clinical findings. Code then performs only
format-preserving projection into ExECTv2 attribute names, exact evidence
validation, finite CUI lookup from the model-emitted concept phrase, and
scoring. It does not select candidates or derive clinical facts from the note.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.core.run_resume import (
    merge_rows,
    pending_items,
    read_completed,
)
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalizer import (
    normalize_count,
    normalize_month,
    normalize_unit,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    SF_BENCHMARK,
    SF_SEMANTIC,
    EntityScore,
    canonicalize_attribute_value,
    score_entity,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.dspy_runner import (
    emit_run_checkpoint,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    loads_json_or_literal,
)

PROMPT_VERSION = "exectv2_llm_only_sf_clinical_findings_v0.19"
PIPELINE_FAMILY = "exectv2_llm_only_clinical_findings"
ENTITY_NAME = SEIZURE_FREQUENCY.name

_OUTPUT_LAYERS: tuple[str, ...] = ("format_projected", "cui_projected")
PLAN11_EVENT_STATE_ROUTE_VERSION = "exectv2_plan11_sf_event_state_route_v0.1"
PLAN11_EVENT_STATE_LAYER_LADDER: tuple[dict[str, str], ...] = (
    {
        "layer": "raw_event_frames",
        "owner": "llm",
        "allowed_behavior": "Event/state inventory, target status, operands, and evidence.",
        "claim_role": "Audit substrate for model-owned coverage and target selection.",
    },
    {
        "layer": "raw_findings",
        "owner": "llm",
        "allowed_behavior": "Final model-owned target findings.",
        "claim_role": "Primary clinical headline before deterministic adapters.",
    },
    {
        "layer": "schema_valid_findings",
        "owner": "deterministic_schema",
        "allowed_behavior": "Parse JSON, coerce scalar schema transport, drop invalid records.",
        "claim_role": "Transport health only.",
    },
    {
        "layer": "evidence_validated",
        "owner": "deterministic_validator",
        "allowed_behavior": "Exact source-substring evidence gate.",
        "claim_role": "Grounding gate.",
    },
    {
        "layer": "format_projected",
        "owner": "deterministic_adapter",
        "allowed_behavior": "Map emitted fields to ExECTv2 attributes without adding facts.",
        "claim_role": "Primary LLM-first scorer layer.",
    },
    {
        "layer": "cui_projected",
        "owner": "deterministic_benchmark_format",
        "allowed_behavior": "Attach CUI/CUIPhrase from the model-emitted phrase.",
        "claim_role": "Companion benchmark-format score only.",
    },
    {
        "layer": "certainty_projected",
        "owner": "deterministic_guideline_adapter",
        "allowed_behavior": "No-op sidecar for SeizureFrequency.",
        "claim_role": "Outside the model-owned SF headline.",
    },
    {
        "layer": "post_llm_state_policy",
        "owner": "deterministic_state_policy",
        "allowed_behavior": "Only named, predeclared post-LLM state policy actions.",
        "claim_role": "Declared sidecar; not hidden adapter behavior.",
    },
    {
        "layer": "benchmark_rendered",
        "owner": "deterministic_adapter",
        "allowed_behavior": "Render accepted mention dictionaries for the legacy scorer.",
        "claim_role": "Benchmark reproduction / continuity layer.",
    },
)
_DISALLOWED_MODEL_PROJECTION_FIELDS: frozenset[str] = frozenset(
    {"CUI", "CUIPhrase", "Certainty", "Negation"}
)

_SCALAR_FINDING_FIELDS: frozenset[str] = frozenset({
    "text",
    "evidence",
    "clinical_kind",
    "frequency_statement_type",
    "source_role",
    "count",
    "count_low",
    "count_high",
    "period_count",
    "period_low",
    "period_high",
    "period_unit",
    "time_relation",
    "point_in_time",
    "day",
    "month",
    "year",
    "age_low",
    "age_high",
    "age_unit",
    "frequency_change",
    "confidence",
    "rationale",
})

_SCALAR_EVENT_FRAME_FIELDS: frozenset[str] = _SCALAR_FINDING_FIELDS | frozenset({
    "event_id",
    "seizure_phrase",
    "target_status",
    "statement_family",
    "finding_text",
})

_TIME_RELATION_ALIASES: Mapping[str, str] = {
    "during": "During",
    "in": "During",
    "on": "During",
    "since": "Since",
    "after": "Since",
    "following": "Since",
    "from": "Since",
}

_POINT_IN_TIME_ALIASES: Mapping[str, str] = {
    "birthday": "Birthday",
    "birth day": "Birthday",
    "drug change": "DrugChange",
    "medication change": "DrugChange",
    "medicine change": "DrugChange",
    "dose change": "DrugChange",
    "last clinic": "LastClinic",
    "last appointment": "LastClinic",
    "last review": "LastClinic",
    "last month": "Last_Month",
    "last week": "Last_Week",
    "last year": "Last_Year",
    "surgery": "Surgery",
    "operation": "Surgery",
}

_FREQUENCY_CHANGE_ALIASES: Mapping[str, str] = {
    "decreased": "Decreased",
    "less frequent": "Decreased",
    "reduced": "Decreased",
    "better": "Decreased",
    "frequent": "Frequent",
    "increased": "Increased",
    "more frequent": "Increased",
    "worse": "Increased",
    "infrequent": "Infrequent",
    "rare": "Infrequent",
    "same": "Same",
    "unchanged": "Same",
    "stable": "Same",
}

_CLINICAL_KIND_VALUES: frozenset[str] = frozenset({
    "frequency_rate",
    "seizure_free",
    "frequency_change",
    "dated_count",
    "last_event",
    "cluster_frequency",
    "other_frequency",
})

_STATEMENT_TYPE_TO_KIND: Mapping[str, str] = {
    "header_count_since_anchor": "dated_count",
    "calendar_count": "dated_count",
    "calendar_occurrence_no_count": "dated_count",
    "recurrence_interval": "frequency_rate",
    "last_event_date": "last_event",
    "background_rate": "frequency_rate",
    "seizure_free_duration": "seizure_free",
    "current_control_no_duration": "seizure_free",
    "current_zero_no_duration": "seizure_free",
    "change_only": "frequency_change",
    "other_frequency": "other_frequency",
}


class ClinicalFindingRecord(BaseModel):
    """One source-near seizure frequency finding emitted by the model."""

    model_config = ConfigDict(extra="ignore")

    text: str
    evidence: str
    clinical_kind: Literal[
        "frequency_rate",
        "seizure_free",
        "frequency_change",
        "dated_count",
        "last_event",
        "cluster_frequency",
        "other_frequency",
    ]
    frequency_statement_type: Literal[
        "header_count_since_anchor",
        "calendar_count",
        "calendar_occurrence_no_count",
        "recurrence_interval",
        "last_event_date",
        "background_rate",
        "seizure_free_duration",
        "current_control_no_duration",
        "current_zero_no_duration",
        "change_only",
        "other_frequency",
    ] = "other_frequency"
    source_role: Literal["compact_section", "narrative", "both"] = "narrative"
    count: str | None = None
    count_low: str | None = None
    count_high: str | None = None
    period_count: str | None = None
    period_low: str | None = None
    period_high: str | None = None
    period_unit: str | None = None
    time_relation: str | None = None
    point_in_time: str | None = None
    day: str | None = None
    month: str | None = None
    year: str | None = None
    age_low: str | None = None
    age_high: str | None = None
    age_unit: str | None = None
    frequency_change: str | None = None
    confidence: Literal["low", "medium", "high"] = "medium"
    rationale: str = ""


class FindingFamilyChecklist(BaseModel):
    """Model-owned note-level seizure-frequency family checklist."""

    model_config = ConfigDict(extra="ignore")

    has_compact_section: bool = False
    has_current_rate: bool = False
    has_dated_count: bool = False
    has_last_event: bool = False
    has_zero_status: bool = False
    has_frequency_change: bool = False
    has_cluster: bool = False
    has_non_target_episode: bool = False
    checklist_rationale: str = ""


class EventFrameRecord(BaseModel):
    """One model-owned clinical event frame used before ExECT projection."""

    model_config = ConfigDict(extra="ignore")

    event_id: str = ""
    evidence: str
    seizure_phrase: str
    target_status: Literal[
        "target_epileptic_seizure_frequency",
        "non_target_episode",
        "history_context_only",
        "diagnosis_without_frequency",
        "future_risk_or_driving",
        "uncertain_not_scored",
    ] = "target_epileptic_seizure_frequency"
    statement_family: str = "other_frequency"
    source_role: Literal["compact_section", "narrative", "both"] = "narrative"
    count: str | None = None
    count_low: str | None = None
    count_high: str | None = None
    period_count: str | None = None
    period_low: str | None = None
    period_high: str | None = None
    period_unit: str | None = None
    time_relation: str | None = None
    point_in_time: str | None = None
    day: str | None = None
    month: str | None = None
    year: str | None = None
    age_low: str | None = None
    age_high: str | None = None
    age_unit: str | None = None
    frequency_change: str | None = None
    finding_text: str | None = None
    include_as_finding: bool = True
    rationale: str = ""


class ClinicalFindingsRecord(BaseModel):
    """Full model output for one letter."""

    model_config = ConfigDict(extra="ignore")

    family_checklist: FindingFamilyChecklist = Field(default_factory=FindingFamilyChecklist)
    event_frames: list[EventFrameRecord] = Field(default_factory=list)
    findings: list[ClinicalFindingRecord] = Field(default_factory=list)


class VerificationDecisionRecord(BaseModel):
    """One model-owned decision about a raw finding."""

    model_config = ConfigDict(extra="ignore")

    raw_index: int
    action: Literal["keep", "remove", "revise"] = "keep"
    target_status: Literal[
        "target_epileptic_seizure_frequency",
        "non_target_episode",
        "history_context_only",
        "diagnosis_without_frequency",
        "future_risk_or_driving",
        "uncertain_not_scored",
    ] = "target_epileptic_seizure_frequency"
    text: str | None = None
    evidence: str | None = None
    clinical_kind: str | None = None
    frequency_statement_type: str | None = None
    source_role: str | None = None
    count: str | None = None
    count_low: str | None = None
    count_high: str | None = None
    period_count: str | None = None
    period_low: str | None = None
    period_high: str | None = None
    period_unit: str | None = None
    time_relation: str | None = None
    point_in_time: str | None = None
    day: str | None = None
    month: str | None = None
    year: str | None = None
    age_low: str | None = None
    age_high: str | None = None
    age_unit: str | None = None
    frequency_change: str | None = None
    rationale: str = ""


class VerificationDecisionList(BaseModel):
    """Model-owned final-selection decisions for one letter."""

    model_config = ConfigDict(extra="ignore")

    decisions: list[VerificationDecisionRecord] = Field(default_factory=list)
    findings_to_add: list[ClinicalFindingRecord] = Field(default_factory=list)


class ExECTv2ClinicalFindingsSFSignature(dspy.Signature):
    """Read one clinical letter and return seizure frequency findings as JSON.

    Return a strict JSON object with key 'findings'. No markdown wrapper.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and task instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"event_frames\": [{\"event_id\": ..., "
            "\"evidence\": ..., \"seizure_phrase\": ..., \"target_status\": ..., "
            "\"statement_family\": ...}], \"findings\": [{\"text\": ..., "
            "\"evidence\": ..., \"clinical_kind\": ..., "
            "\"frequency_statement_type\": ..., \"source_role\": ..., "
            "\"count\": ..., \"period_unit\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )


class ExECTv2ClinicalFindingsVerifierSignature(dspy.Signature):
    """Review one letter and raw findings, then return edit decisions.

    Return a strict JSON object with keys 'decisions' and 'findings_to_add'.
    No markdown wrapper.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter, raw findings, and review instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"decisions\": [{\"raw_index\": 0, "
            "\"target_status\": ..., \"action\": \"keep|remove|revise\", \"text\": ..., "
            "\"evidence\": ..., \"rationale\": ...}], "
            "\"findings_to_add\": [...]}"
        )
    )


class ExECTv2ClinicalFindingsFinalizerSignature(dspy.Signature):
    """Rewrite raw findings into the final scored seizure-frequency findings.

    Return a strict JSON object with key 'findings'. No markdown wrapper.
    """

    prompt_input_json: str = dspy.InputField(
        desc=(
            "JSON containing one clinical letter, raw findings, output schema, "
            "and finalization instructions."
        )
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"findings\": [{\"text\": ..., "
            "\"evidence\": ..., \"clinical_kind\": ..., "
            "\"frequency_statement_type\": ..., \"source_role\": ..., "
            "\"count\": ..., \"period_unit\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )


class DspyClinicalFindingsSFExtractor(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2ClinicalFindingsSFSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


class DspyClinicalFindingsSFVerifier(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2ClinicalFindingsVerifierSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


class DspyClinicalFindingsSFFinalizer(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2ClinicalFindingsFinalizerSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def build_prompt_input(letter: ExectLetter) -> str:
    """Build the clinical-findings prompt payload for one letter."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Read the clinical letter and list each seizure type or seizure-free "
            "state that has frequency information. First enumerate model-owned "
            "event_frames for every possible seizure-frequency or non-target episode "
            "fact, then convert only target event_frames into the final 'findings' "
            "list. Return one JSON object."
        ),
        "event_frame_schema": {
            "event_id": "Short stable id such as e1, e2, e3.",
            "evidence": (
                "Exact source substring containing the seizure-frequency or "
                "non-target episode fact."
            ),
            "seizure_phrase": (
                "Exact source-near phrase naming the seizure type, seizure-free "
                "state, or non-target episode. Do not include context words that "
                "describe preserved awareness, triggers, symptoms, or uncertainty "
                "unless they are part of the scored seizure-type phrase."
            ),
            "target_status": (
                "target_epileptic_seizure_frequency, non_target_episode, "
                "history_context_only, diagnosis_without_frequency, "
                "future_risk_or_driving, or uncertain_not_scored."
            ),
            "statement_family": (
                "header_count_since_anchor, calendar_count, "
                "calendar_occurrence_no_count, recurrence_interval, last_event_date, "
                "background_rate, seizure_free_duration, current_control_no_duration, "
                "current_zero_no_duration, change_only, cluster, non_target, or "
                "other_frequency."
            ),
            "source_role": "compact_section, narrative, or both.",
            "count": "Single seizure count when stated or implied by one event.",
            "count_low": "Lower seizure count when a range is stated.",
            "count_high": "Upper seizure count when a range is stated.",
            "period_count": "Number of denominator time periods, usually 1.",
            "period_low": "Lower denominator period count when a range is stated.",
            "period_high": "Upper denominator period count when a range is stated.",
            "period_unit": "day, week, month, or year when stated.",
            "time_relation": "during or since when explicitly stated.",
            "point_in_time": "Clinical anchor such as last clinic or medication change.",
            "day/month/year": "Calendar date fields when explicitly stated.",
            "age_low/age_high/age_unit": "Age anchor when explicitly stated.",
            "frequency_change": "decreased, frequent, increased, infrequent, or same.",
            "finding_text": (
                "Exact text that should be used in findings if include_as_finding is "
                "true. This may be shorter than seizure_phrase when evidence includes "
                "context such as 'without change in awareness'."
            ),
            "include_as_finding": (
                "true only for event_frames that should become scored findings."
            ),
            "rationale": "One concise clinical reading of this event frame.",
        },
        "output_schema": {
            "text": (
                "Exact short phrase from the letter naming the seizure type or "
                "seizure-free state, such as 'focal seizures', 'absences', "
                "'generalised tonic-clonic seizures', or 'seizure free'."
            ),
            "evidence": (
                "Exact substring from the letter that supports this finding. Use "
                "the smallest clause or sentence that includes the frequency."
            ),
            "clinical_kind": (
                "One of frequency_rate, seizure_free, frequency_change, dated_count, "
                "last_event, cluster_frequency, other_frequency."
            ),
            "frequency_statement_type": (
                "Classify the statement before filling fields: header_count_since_anchor, "
                "calendar_count, calendar_occurrence_no_count, recurrence_interval, "
                "last_event_date, background_rate, seizure_free_duration, "
                "current_control_no_duration, current_zero_no_duration, change_only, "
                "or other_frequency."
            ),
            "source_role": (
                "compact_section, narrative, or both. Use compact_section for facts "
                "listed in short headed lines such as seizure type and frequency."
            ),
            "count": (
                "Single seizure count when stated. For every 3 to 4 weeks, "
                "the count is 1."
            ),
            "count_low": "Lower seizure count when a range is stated.",
            "count_high": "Upper seizure count when a range is stated.",
            "period_count": "Number of time periods, usually 1.",
            "period_low": "Lower time-period count when a period range is stated.",
            "period_high": "Upper time-period count when a period range is stated.",
            "period_unit": "day, week, month, or year when stated.",
            "time_relation": "during or since when explicitly stated.",
            "point_in_time": (
                "Clinical anchor when explicitly stated, for example medication "
                "change, last clinic, last month, last week, last year, surgery, "
                "or birthday."
            ),
            "day": "Day of month when explicitly stated.",
            "month": "Month when explicitly stated.",
            "year": "Year when explicitly stated.",
            "age_low": "Lower patient age when an age or age range is stated.",
            "age_high": "Upper patient age when an age range is stated.",
            "age_unit": "year or month when age_low or age_high is stated.",
            "frequency_change": (
                "decreased, frequent, increased, infrequent, or same when a change "
                "or relative frequency is stated."
            ),
            "confidence": "high, medium, or low.",
            "rationale": "One concise sentence explaining the clinical reading.",
        },
        "required_keys_per_finding": [
            "text",
            "evidence",
            "clinical_kind",
            "frequency_statement_type",
            "source_role",
            "count",
            "count_low",
            "count_high",
            "period_count",
            "period_low",
            "period_high",
            "period_unit",
            "time_relation",
            "point_in_time",
            "day",
            "month",
            "year",
            "age_low",
            "age_high",
            "age_unit",
            "frequency_change",
            "confidence",
            "rationale",
        ],
        "clinical_rules": [
            (
                "Fill event_frames before findings. Each event_frame is a model-owned "
                "clinical reading of one possible seizure-frequency, seizure-free, "
                "last-event, change, cluster, or non-target episode fact."
            ),
            (
                "Use event_frames to separate coverage from scoring: include target "
                "epileptic seizure-frequency frames in findings, but keep non-target "
                "episode/history/driving/diagnosis frames out of findings."
            ),
            (
                "Every finding should correspond to one target event_frame. If a "
                "target event_frame has include_as_finding true, copy its exact "
                "finding_text when supplied; otherwise copy its seizure_phrase. Also "
                "copy evidence, statement family, count, period, and time fields "
                "unless there is a clear reason not to score it."
            ),
            (
                "event_frames are planning and audit output, not a shortcut. Do not "
                "invent a finding without exact source evidence, and do not let a "
                "non-target event_frame become a scored finding."
            ),
            (
                "Every finding must include frequency_statement_type and source_role. "
                "Use null for unknown optional numeric/date fields, but do not omit keys."
            ),
            (
                "Use one finding per seizure type. If the letter separately describes "
                "focal seizures and tonic-clonic seizures, return two findings."
            ),
            (
                "Pay close attention to compact sections headed seizure type and "
                "frequency. Treat comma-separated items in those sections as findings, "
                "not only the prose paragraphs."
            ),
            (
                "If the same seizure type has two distinct frequency facts with "
                "different time context, return two findings for that same text."
            ),
            (
                "If a compact frequency section states a fact and a later narrative "
                "sentence repeats the same fact, return both findings with their own "
                "exact evidence strings."
            ),
            (
                "A current seizure-free or controlled statement does not replace "
                "historical compact-section seizure-frequency facts. If a compact "
                "section lists dated seizure-type facts and the narrative later says "
                "the patient remains seizure free, return the dated facts as findings "
                "and treat the current-control statement separately."
            ),
            (
                "Both text and evidence must be copied exactly from the letter. If no "
                "exact phrase can be copied, omit that finding."
            ),
            (
                "Prefer source-near wording. Do not rewrite the seizure type into a "
                "different clinical concept."
            ),
            (
                "For rates such as 2 to 3 per month, set count_low, count_high, "
                "period_count, and period_unit."
            ),
            (
                "For header counts anchored to clinic review, such as several "
                "seizures since clinic review, set frequency_statement_type to "
                "header_count_since_anchor, count to 3 when the word is several, "
                "time_relation to since, and point_in_time to last clinic."
            ),
            (
                "For dated counts such as in March she had 2 to 3 seizures, set "
                "clinical_kind to dated_count, fill month and time_relation, and "
                "do not fill period_count or period_unit unless words like per "
                "month or every month are present."
            ),
            (
                "For a dated occurrence with no explicit count, such as absence "
                "like seizures in 2018, set frequency_statement_type to "
                "calendar_occurrence_no_count, clinical_kind to dated_count, "
                "year to 2018, and time_relation to during."
            ),
            (
                "For every 2 to 3 weeks, set count to 1, period_low to 2, "
                "period_high to 3, and period_unit to week."
            ),
            (
                "For seizure-free duration, set clinical_kind to seizure_free and "
                "fill period_count and period_unit when stated."
            ),
            (
                "For last-event statements such as last event July 2016, use the "
                "seizure type as text, clinical_kind last_event, count 0, "
                "time_relation since, and fill month and year."
            ),
            (
                "For vague counts, use these conventions: few or couple is 2, "
                "several is 3, and none or no is 0. Do not turn these words into "
                "count ranges."
            ),
            (
                "If evidence says generic seizures, keep text as seizures even if "
                "the diagnosis names a more specific seizure syndrome elsewhere. "
                "Do not replace generic seizures with the diagnosis term."
            ),
            (
                "If the evidence says focal seizures with altered, impaired, or "
                "lost awareness, keep that awareness modifier in text."
            ),
            (
                "If the evidence says focal seizures without change in awareness, "
                "use text focal seizures. Without change in awareness is context, "
                "not an impaired-awareness seizure-type modifier."
            ),
            (
                "Do not extract migraine/headache frequency, febrile-seizure history, "
                "family history, driving rules, future risk statements, or medication "
                "titration intervals."
            ),
            (
                "Do not extract blackouts, loss of consciousness episodes, dizzy "
                "spells, dissociative seizures, nonepileptic events, or generic events "
                "unless the evidence itself states these are epileptic seizures."
            ),
            (
                "Do not convert a diagnostic episode description into a seizure-frequency "
                "finding just because another sentence says the clinician suspects "
                "epilepsy or thinks the episodes may be seizures. The frequency evidence "
                "itself must name epileptic seizures or a seizure type."
            ),
            (
                "Do not extract minor seizures as target frequency when the evidence "
                "describes dizzy spells, headache, nausea, unresponsiveness, shaking, "
                "or other nonspecific episodes rather than a scored seizure type."
            ),
            (
                "Do not extract minor seizures, jerks, or episodes as scored seizure "
                "frequency even when a rate is stated, unless the same frequency clause "
                "itself explicitly names epileptic seizures or a standard seizure type "
                "such as focal seizures, absences, tonic-clonic seizures, myoclonic "
                "jerks, or convulsive seizures."
            ),
            (
                "Do not treat 'continues to get seizures' as a scored frequency-change "
                "finding unless the same evidence gives a count, rate, date, last-event "
                "anchor, or explicit qualitative change word such as increased, "
                "decreased, frequent, or infrequent."
            ),
            (
                "For a first or single diagnostic seizure encounter, do not score "
                "no previous seizures, no further episodes, future risk of seizures, "
                "or driving-clearance seizure windows as seizure-frequency findings."
            ),
            (
                "For last-event summaries, extract the most recent last event only. "
                "Do not add previous events as separate last-event findings."
            ),
            (
                "If a compact line says last event plus previous event, return the "
                "last event and do not return the older previous event. The previous "
                "event is context for the last-event summary, not another scored "
                "last-event finding."
            ),
            (
                "For a rate stated during a finite episode, keep the denominator "
                "separate from the episode duration. In '6-9 seizures every week "
                "for 3 weeks', the period_count is 1 and period_unit is week; the "
                "3 weeks is the duration of that episode, not the rate denominator."
            ),
            (
                "For cluster wording such as a cluster of seizures in August where "
                "seizures happened 6-9 every week, return one dated cluster-of-seizures "
                "finding and one separate within-cluster seizure-rate finding."
            ),
            (
                "When evidence says seizures have returned after seizure freedom, "
                "return a frequency_change finding with frequency_change increased "
                "if there is no exact count in that phrase."
            ),
            (
                "When evidence says a seizure type is infrequent, return a "
                "frequency_change finding with frequency_change infrequent. Do not "
                "turn older historical counts such as two in the year of diagnosis "
                "into a current rate unless the same clause gives a current period."
            ),
            (
                "For no further seizures or epileptic seizures under control, return "
                "a zero-count finding. If control follows a drug increase or medication "
                "change, set point_in_time to medication change."
            ),
            (
                "Do not score a bare current statement such as he remains seizure free "
                "or she remains seizure free when there is no duration, no date, no "
                "medication-change/surgery/clinic anchor, and no wording such as no "
                "further seizures. Put it in event_frames as current_control_no_duration "
                "with include_as_finding false."
            ),
            (
                "Use current_control_no_duration only for vague diagnosis-level phrases "
                "such as epilepsy seems under control, especially when no seizure type "
                "or no further seizures phrase is stated. For a specific seizure type "
                "or epileptic seizures completely under control after a medication "
                "increase, use current_zero_no_duration with count 0 and point_in_time "
                "medication change."
            ),
            (
                "For no further seizures, use text seizures and count 0. Do not rewrite "
                "the source phrase to seizure free unless the letter itself says seizure "
                "free."
            ),
            (
                "For last seizures in teenage years, use text seizures, count 0, "
                "time_relation since, age_low 13, age_high 19, and age_unit year. "
                "Do not extract accompanying migraine or febrile-seizure counts."
            ),
            (
                "Do not return a current seizure-free finding unless a duration, date, "
                "or clinical anchor is explicitly stated."
            ),
            (
                "For change-only statements, set clinical_kind to frequency_change "
                "and fill frequency_change."
            ),
            (
                "Only fill time_relation, point_in_time, day, month, or year when "
                "that context is explicitly stated in the letter."
            ),
            (
                "If the letter has no seizure frequency information, return "
                "{\"event_frames\": [], \"findings\": []}."
            ),
            "Return exactly one JSON object. No markdown code fences.",
        ],
        "event_frame_examples": [
            {
                "note_fragment": (
                    "In March she had 2 to 3 of her focal seizures without change "
                    "in awareness."
                ),
                "event_frames": [
                    {
                        "event_id": "e1",
                        "evidence": (
                            "In March she had 2 to 3 of her focal seizures without "
                            "change in awareness"
                        ),
                        "seizure_phrase": "focal seizures",
                        "target_status": "target_epileptic_seizure_frequency",
                        "statement_family": "calendar_count",
                        "source_role": "narrative",
                        "count_low": "2",
                        "count_high": "3",
                        "time_relation": "during",
                        "month": "March",
                        "finding_text": "focal seizures",
                        "include_as_finding": True,
                        "rationale": (
                            "Without change in awareness is context, so the scored "
                            "seizure phrase is focal seizures."
                        ),
                    }
                ],
            },
            {
                "note_fragment": (
                    "Seizure type and frequency: Generalised tonic clonic seizure-"
                    "last event July 2016. Previous event December 2015."
                ),
                "event_frames": [
                    {
                        "event_id": "e1",
                        "evidence": "Generalised tonic clonic seizure-last event July 2016",
                        "seizure_phrase": "Generalised tonic clonic seizure",
                        "target_status": "target_epileptic_seizure_frequency",
                        "statement_family": "last_event_date",
                        "source_role": "compact_section",
                        "count": "0",
                        "time_relation": "since",
                        "month": "July",
                        "year": "2016",
                        "finding_text": "Generalised tonic clonic seizure",
                        "include_as_finding": True,
                        "rationale": "The most recent last-event date is a scored finding.",
                    },
                    {
                        "event_id": "e2",
                        "evidence": "Previous event December 2015",
                        "seizure_phrase": "event",
                        "target_status": "history_context_only",
                        "statement_family": "last_event_date",
                        "source_role": "compact_section",
                        "count": "0",
                        "time_relation": "since",
                        "month": "December",
                        "year": "2015",
                        "include_as_finding": False,
                        "rationale": (
                            "Older previous event is context once a newer last event "
                            "is given."
                        ),
                    },
                ],
            },
            {
                "note_fragment": (
                    "Seizure type and frequency: 2 generalised tonic clonic seizures "
                    "2014, absence like seizures 2014. He remains seizure free."
                ),
                "event_frames": [
                    {
                        "event_id": "e1",
                        "evidence": "2 generalised tonic clonic seizures 2014",
                        "seizure_phrase": "generalised tonic clonic seizures",
                        "target_status": "target_epileptic_seizure_frequency",
                        "statement_family": "calendar_count",
                        "source_role": "compact_section",
                        "count": "2",
                        "time_relation": "during",
                        "year": "2014",
                        "finding_text": "generalised tonic clonic seizures",
                        "include_as_finding": True,
                        "rationale": "Historical dated compact-section count is scored.",
                    },
                    {
                        "event_id": "e2",
                        "evidence": "absence like seizures 2014",
                        "seizure_phrase": "absence like seizures",
                        "target_status": "target_epileptic_seizure_frequency",
                        "statement_family": "calendar_occurrence_no_count",
                        "source_role": "compact_section",
                        "time_relation": "during",
                        "year": "2014",
                        "finding_text": "absence like seizures",
                        "include_as_finding": True,
                        "rationale": "Dated occurrence without count is scored as one occurrence.",
                    },
                    {
                        "event_id": "e3",
                        "evidence": "He remains seizure free",
                        "seizure_phrase": "seizure free",
                        "target_status": "uncertain_not_scored",
                        "statement_family": "current_control_no_duration",
                        "source_role": "narrative",
                        "include_as_finding": False,
                        "rationale": (
                            "Bare remains seizure free has no duration, date, or "
                            "clinical anchor, so it is not a scored finding."
                        ),
                    },
                ],
            },
            {
                "note_fragment": (
                    "She gets dizzy episodes twice a week. These are thought to be "
                    "nonepileptic events."
                ),
                "event_frames": [
                    {
                        "event_id": "e1",
                        "evidence": "dizzy episodes twice a week",
                        "seizure_phrase": "dizzy episodes",
                        "target_status": "non_target_episode",
                        "statement_family": "non_target",
                        "source_role": "narrative",
                        "count": "2",
                        "period_count": "1",
                        "period_unit": "week",
                        "include_as_finding": False,
                        "rationale": "The frequency belongs to non-target dizzy episodes.",
                    }
                ],
            },
        ],
        "worked_examples": [
            {
                "note_fragment": (
                    "She has 2 to 3 focal seizures with impaired awareness per month "
                    "since the medication change."
                ),
                "correct": {
                    "text": "focal seizures with impaired awareness",
                    "evidence": (
                        "2 to 3 focal seizures with impaired awareness per month "
                        "since the medication change"
                    ),
                    "clinical_kind": "frequency_rate",
                    "frequency_statement_type": "background_rate",
                    "source_role": "narrative",
                    "count_low": "2",
                    "count_high": "3",
                    "period_count": "1",
                    "period_unit": "month",
                    "time_relation": "since",
                    "point_in_time": "medication change",
                    "confidence": "high",
                    "rationale": "Focal seizures occur 2 to 3 per month since medication change.",
                },
            },
            {
                "note_fragment": (
                    "In April she had 2 to 3 of her focal seizures without change "
                    "in awareness."
                ),
                "correct": {
                    "text": "focal seizures",
                    "evidence": (
                        "In April she had 2 to 3 of her focal seizures without "
                        "change in awareness"
                    ),
                    "clinical_kind": "dated_count",
                    "frequency_statement_type": "calendar_count",
                    "source_role": "narrative",
                    "count_low": "2",
                    "count_high": "3",
                    "time_relation": "during",
                    "month": "April",
                    "confidence": "high",
                    "rationale": "The count is stated during April, not as a per-month rate.",
                },
            },
            {
                "note_fragment": "He has been seizure free for 6 months after surgery.",
                "correct": {
                    "text": "seizure free",
                    "evidence": "seizure free for 6 months after surgery",
                    "clinical_kind": "seizure_free",
                    "frequency_statement_type": "seizure_free_duration",
                    "source_role": "narrative",
                    "period_count": "6",
                    "period_unit": "month",
                    "time_relation": "since",
                    "point_in_time": "surgery",
                    "confidence": "high",
                    "rationale": "Seizure-free state has lasted 6 months since surgery.",
                },
            },
            {
                "note_fragment": (
                    "Seizure frequency: several seizures since clinic review, "
                    "a few seizures per year."
                ),
                "correct": [
                    {
                        "text": "seizures",
                        "evidence": "several seizures since clinic review",
                        "clinical_kind": "dated_count",
                        "frequency_statement_type": "header_count_since_anchor",
                        "source_role": "compact_section",
                        "count": "3",
                        "time_relation": "since",
                        "point_in_time": "last clinic",
                        "confidence": "medium",
                        "rationale": "Several means 3 seizures since clinic review.",
                    },
                    {
                        "text": "seizures",
                        "evidence": "a few seizures per year",
                        "clinical_kind": "frequency_rate",
                        "frequency_statement_type": "background_rate",
                        "source_role": "compact_section",
                        "count": "2",
                        "period_count": "1",
                        "period_unit": "year",
                        "confidence": "medium",
                        "rationale": "Few means 2 seizures per year.",
                    },
                ],
            },
            {
                "note_fragment": (
                    "Seizure type and frequency: seizures every 3 to 4 weeks. "
                    "She currently has seizures every 3 to 4 weeks."
                ),
                "correct": [
                    {
                        "text": "seizures",
                        "evidence": "seizures every 3 to 4 weeks",
                        "clinical_kind": "frequency_rate",
                        "frequency_statement_type": "recurrence_interval",
                        "source_role": "compact_section",
                        "count": "1",
                        "period_low": "3",
                        "period_high": "4",
                        "period_unit": "week",
                        "confidence": "high",
                        "rationale": (
                            "The compact section states one seizure interval every "
                            "3 to 4 weeks."
                        ),
                    },
                    {
                        "text": "seizures",
                        "evidence": "seizures every 3 to 4 weeks",
                        "clinical_kind": "frequency_rate",
                        "frequency_statement_type": "recurrence_interval",
                        "source_role": "narrative",
                        "count": "1",
                        "period_low": "3",
                        "period_high": "4",
                        "period_unit": "week",
                        "confidence": "high",
                        "rationale": "The narrative repeats the same seizure interval.",
                    },
                ],
            },
            {
                "note_fragment": (
                    "Diagnosis: generalised epilepsy. He has had roughly two "
                    "seizures per year."
                ),
                "correct": {
                    "text": "seizures",
                    "evidence": "roughly two seizures per year",
                    "clinical_kind": "frequency_rate",
                    "frequency_statement_type": "background_rate",
                    "source_role": "narrative",
                    "count": "2",
                    "period_count": "1",
                    "period_unit": "year",
                    "confidence": "high",
                    "rationale": (
                        "The evidence says generic seizures, so the text remains "
                        "seizures."
                    ),
                },
            },
            {
                "note_fragment": (
                    "His last seizures were in his teenage years. He had migraines "
                    "three times per month and febrile seizures as a child."
                ),
                "correct": {
                    "text": "seizures",
                    "evidence": "His last seizures were in his teenage years",
                    "clinical_kind": "last_event",
                    "frequency_statement_type": "last_event_date",
                    "source_role": "narrative",
                    "count": "0",
                    "time_relation": "since",
                    "age_low": "13",
                    "age_high": "19",
                    "age_unit": "year",
                    "confidence": "medium",
                    "rationale": (
                        "Last seizures were in teenage years; migraine and febrile "
                        "history are not target frequency facts."
                    ),
                },
            },
            {
                "note_fragment": "Seizure type and frequency: absence like seizures 2018",
                "correct": {
                    "text": "absence like seizures",
                    "evidence": "absence like seizures 2018",
                    "clinical_kind": "dated_count",
                    "frequency_statement_type": "calendar_occurrence_no_count",
                    "source_role": "compact_section",
                    "year": "2018",
                    "time_relation": "during",
                    "confidence": "medium",
                    "rationale": "The line records an occurrence in 2018 without an exact count.",
                },
            },
            {
                "note_fragment": (
                    "Seizure type and frequency: 2 generalised tonic clonic seizures "
                    "2018, absence like seizures 2018. He remains seizure free."
                ),
                "correct": [
                    {
                        "text": "generalised tonic clonic seizures",
                        "evidence": "2 generalised tonic clonic seizures 2018",
                        "clinical_kind": "dated_count",
                        "frequency_statement_type": "calendar_count",
                        "source_role": "compact_section",
                        "count": "2",
                        "year": "2018",
                        "time_relation": "during",
                        "confidence": "high",
                        "rationale": (
                            "The compact section states a dated count of generalised "
                            "tonic clonic seizures."
                        ),
                    },
                    {
                        "text": "absence like seizures",
                        "evidence": "absence like seizures 2018",
                        "clinical_kind": "dated_count",
                        "frequency_statement_type": "calendar_occurrence_no_count",
                        "source_role": "compact_section",
                        "year": "2018",
                        "time_relation": "during",
                        "confidence": "medium",
                        "rationale": (
                            "The compact section records absence like seizures in "
                            "2018 without an exact count."
                        ),
                    },
                ],
            },
            {
                "note_fragment": (
                    "Seizure type and frequency: Generalised tonic clonic seizure-last "
                    "event July 2016. Previous event December 2015."
                ),
                "correct": {
                    "text": "Generalised tonic clonic seizure",
                    "evidence": "Generalised tonic clonic seizure-last event July 2016.",
                    "clinical_kind": "last_event",
                    "frequency_statement_type": "last_event_date",
                    "source_role": "compact_section",
                    "count": "0",
                    "month": "July",
                    "year": "2016",
                    "time_relation": "since",
                    "confidence": "high",
                    "rationale": (
                        "The July 2016 last event is the most recent event; the "
                        "older previous event is context."
                    ),
                },
            },
            {
                "note_fragment": (
                    "She had a cluster of seizures in August 2017 where she had "
                    "6-9 seizures every week for 3 weeks."
                ),
                "correct": [
                    {
                        "text": "cluster of seizures",
                        "evidence": "a cluster of seizures in August 2017",
                        "clinical_kind": "cluster_frequency",
                        "frequency_statement_type": "calendar_occurrence_no_count",
                        "source_role": "narrative",
                        "count": "1",
                        "month": "August",
                        "year": "2017",
                        "time_relation": "during",
                        "confidence": "high",
                        "rationale": "The cluster itself is a dated occurrence.",
                    },
                    {
                        "text": "seizures",
                        "evidence": "6-9 seizures every week for 3 weeks",
                        "clinical_kind": "frequency_rate",
                        "frequency_statement_type": "background_rate",
                        "source_role": "narrative",
                        "count_low": "6",
                        "count_high": "9",
                        "period_count": "1",
                        "period_unit": "week",
                        "month": "August",
                        "year": "2017",
                        "time_relation": "during",
                        "confidence": "high",
                        "rationale": (
                            "The rate is every week; the 3 weeks is episode duration."
                        ),
                    },
                ],
            },
            {
                "note_fragment": (
                    "The seizures have returned. He can get infrequent focal to "
                    "bilateral convulsive seizures having around two in the year "
                    "of his diagnosis."
                ),
                "correct": [
                    {
                        "text": "seizures",
                        "evidence": "The seizures have returned",
                        "clinical_kind": "frequency_change",
                        "frequency_statement_type": "change_only",
                        "source_role": "narrative",
                        "frequency_change": "increased",
                        "confidence": "medium",
                        "rationale": (
                            "Seizures returning after seizure freedom is an increase."
                        ),
                    },
                    {
                        "text": "focal to bilateral convulsive seizures",
                        "evidence": "infrequent focal to bilateral convulsive seizures",
                        "clinical_kind": "frequency_change",
                        "frequency_statement_type": "change_only",
                        "source_role": "narrative",
                        "frequency_change": "infrequent",
                        "confidence": "medium",
                        "rationale": (
                            "Infrequent is a qualitative frequency-change statement; "
                            "the old count at diagnosis is not a current rate."
                        ),
                    },
                ],
            },
            {
                "note_fragment": (
                    "The epilepsy seems to be under control on levetiracetam. "
                    "I will review her again in nine months."
                ),
                "correct": [],
                "rationale": (
                    "Vague diagnosis-level control without a seizure type, count, "
                    "date, duration, or no-further-seizures phrase is not scored."
                ),
            },
            {
                "note_fragment": (
                    "There has been significant improvement since increasing lamotrigine. "
                    "The focal seizures are completely under control on lamotrigine."
                ),
                "correct": [
                    {
                        "text": "focal seizures",
                        "evidence": "The focal seizures are completely under control",
                        "clinical_kind": "seizure_free",
                        "frequency_statement_type": "current_zero_no_duration",
                        "source_role": "narrative",
                        "count": "0",
                        "point_in_time": "medication change",
                        "confidence": "high",
                        "rationale": (
                            "A specific seizure type is completely controlled after "
                            "a medication increase."
                        ),
                    },
                    {
                        "text": "seizures",
                        "evidence": (
                            "There has been significant improvement since increasing "
                            "lamotrigine"
                        ),
                        "clinical_kind": "frequency_change",
                        "frequency_statement_type": "change_only",
                        "source_role": "narrative",
                        "frequency_change": "infrequent",
                        "point_in_time": "medication change",
                        "confidence": "medium",
                        "rationale": (
                            "Improvement since medication increase means seizure "
                            "frequency became infrequent."
                        ),
                    },
                ],
            },
            {
                "note_fragment": (
                    "She has not had any further seizures on levetiracetam."
                ),
                "correct": {
                    "text": "seizures",
                    "evidence": "has not had any further seizures",
                    "clinical_kind": "seizure_free",
                    "frequency_statement_type": "current_zero_no_duration",
                    "source_role": "narrative",
                    "count": "0",
                    "confidence": "high",
                    "rationale": (
                        "The source says no further seizures, so text remains seizures."
                    ),
                },
            },
            {
                "note_fragment": (
                    "She has episodes twice a week of deja vu. I think these are "
                    "focal seizures."
                ),
                "correct": [],
                "rationale": (
                    "The frequency clause names episodes, and the seizure interpretation "
                    "is separate diagnostic reasoning rather than a source-near seizure "
                    "frequency statement."
                ),
            },
            {
                "note_fragment": (
                    "Despite medication she continues to get general and complex "
                    "partial seizures. She continues to get chronic daily headaches."
                ),
                "correct": [],
                "rationale": (
                    "Continues to get seizures is not a scored frequency without a "
                    "count, rate, date, or explicit qualitative frequency change."
                ),
            },
            {
                "note_fragment": (
                    "He developed some minor seizures. The episodes last no longer "
                    "than 3 minutes and occur 4 to 5 times a year."
                ),
                "correct": [],
                "rationale": (
                    "The rate belongs to nonspecific minor episodes rather than a "
                    "standard scored seizure type."
                ),
            },
            {
                "note_fragment": (
                    "Diagnosis: single focal seizure. He has not had any previous "
                    "seizures and is at risk of further seizures."
                ),
                "correct": [],
                "rationale": (
                    "A single diagnostic seizure encounter plus no previous seizures "
                    "or future risk is not scored as recurrent seizure frequency."
                ),
            },
            {
                "note_fragment": (
                    "Diagnosis: generalised tonic clonic seizures with myoclonic jerks. "
                    "She is still having approximately 15 seizures over 4 months."
                ),
                "correct": {
                    "text": "seizures",
                    "evidence": "approximately 15 seizures over 4 months",
                    "clinical_kind": "frequency_rate",
                    "frequency_statement_type": "background_rate",
                    "source_role": "narrative",
                    "count": "15",
                    "period_count": "4",
                    "period_unit": "month",
                    "confidence": "high",
                    "rationale": (
                        "The frequency evidence says generic seizures, so text "
                        "remains seizures."
                    ),
                },
            },
        ],
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def build_verification_prompt_input(
    letter: ExectLetter,
    raw_findings: Sequence[ClinicalFindingRecord],
    event_frames: Sequence[EventFrameRecord] | None = None,
) -> str:
    """Build the second-pass clinical review payload for one letter."""

    payload = {
        "prompt_version": f"{PROMPT_VERSION}_verification",
        "task": (
            "Review the clinical letter and raw seizure-frequency findings. "
            "Return model decisions as one JSON object with a 'decisions' list and "
            "a 'findings_to_add' list."
        ),
        "raw_findings": [finding.model_dump(mode="json") for finding in raw_findings],
        "event_frames": [
            frame.model_dump(mode="json") for frame in (event_frames or [])
        ],
        "decision_schema": {
            "raw_index": "Zero-based index into raw_findings.",
            "target_status": (
                "Optional clinical category: target_epileptic_seizure_frequency, "
                "non_target_episode, history_context_only, diagnosis_without_frequency, "
                "future_risk_or_driving, or uncertain_not_scored."
            ),
            "action": "keep, remove, or revise.",
            "text": "Only for revise: corrected exact source phrase.",
            "evidence": "Only for revise: corrected exact supporting substring.",
            "clinical_kind": "Only for revise when the raw kind is clinically wrong.",
            "frequency_statement_type": (
                "Only for revise when the raw statement type is clinically wrong."
            ),
            "source_role": "Only for revise when the raw source role is clinically wrong.",
            "count/date/period fields": (
                "Only for revise when raw numeric, date, period, time_relation, "
                "point_in_time, age, or frequency_change fields are clinically wrong. "
                "Omit fields that should be preserved."
            ),
            "rationale": "Brief clinical reason for the decision.",
        },
        "required_keys_per_finding": [
            "text",
            "evidence",
            "clinical_kind",
            "frequency_statement_type",
            "source_role",
            "count",
            "count_low",
            "count_high",
            "period_count",
            "period_low",
            "period_high",
            "period_unit",
            "time_relation",
            "point_in_time",
            "day",
            "month",
            "year",
            "age_low",
            "age_high",
            "age_unit",
            "frequency_change",
            "confidence",
            "rationale",
        ],
        "review_checks": [
            "Return exactly one decision for every raw finding.",
            (
                "Use event_frames as the model's first-pass clinical map. If a target "
                "event_frame has include_as_finding true but raw_findings omit it, add "
                "a complete finding in findings_to_add when exact supporting evidence "
                "exists."
            ),
            (
                "If an event_frame has target_status non_target_episode, "
                "history_context_only, diagnosis_without_frequency, "
                "future_risk_or_driving, or uncertain_not_scored, verify that no "
                "matching raw finding is kept unless the frame is actually a target "
                "epileptic seizure-frequency fact."
            ),
            (
                "Do not blindly trust an event_frame phrase if it copied contextual "
                "words into the seizure type. For focal seizures without change in "
                "awareness, revise the raw text to focal seizures even when the "
                "event_frame used the longer phrase."
            ),
            (
                "Use a brief final rationale only. Do not discuss alternatives or "
                "write step-by-step deliberation."
            ),
            (
                "Several seizures since last clinic and a few seizures per year are "
                "target epileptic seizure-frequency findings, even if the note also "
                "uses the word uncertain."
            ),
            (
                "Do not use uncertain_not_scored merely because a section heading says "
                "uncertain. Use uncertain_not_scored only when the evidence gives no "
                "count, rate, dated occurrence, last-event date, or zero-seizure status."
            ),
            (
                "Target epileptic seizure-frequency findings include historical dated "
                "counts, dated occurrences, last-event dates, recurrent rates, and "
                "zero-seizure status. Do not remove a finding merely because it is "
                "historical; ExECTv2 scores dated historical seizure-frequency facts."
            ),
            (
                "Keep compact-section dated seizure-type facts even when later prose "
                "says the patient is currently seizure free or controlled. Current "
                "control and historical dated counts are distinct clinical facts."
            ),
            (
                "Keep only epileptic seizure-frequency findings. Remove migraine, "
                "headache, blackout, dissociative, nonepileptic, dizzy spell, "
                "loss-of-consciousness, febrile-history, family-history, driving-rule, "
                "future-risk, and medication-titration facts unless the evidence itself "
                "states an epileptic seizure frequency."
            ),
            (
                "Keep generic wording generic. If the evidence says seizures, use "
                "text 'seizures' even when a diagnosis elsewhere names a specific "
                "seizure syndrome."
            ),
            (
                "Classify a single first seizure or one-off diagnostic encounter "
                "without recurrent epilepsy frequency as diagnosis_without_frequency "
                "unless the evidence states current seizure frequency."
            ),
            (
                "Classify minor seizures, jerks, blackouts, dizzy spells, loss of "
                "consciousness, episodes, events, and spells as non_target_episode "
                "unless the evidence explicitly says epileptic seizure frequency."
            ),
            (
                "Remove minor seizures, jerks, or episodes even when a rate is stated "
                "if the frequency evidence describes nonspecific spells rather than "
                "a standard scored seizure type."
            ),
            (
                "A diagnostic episode description plus a separate clinician impression "
                "that episodes may be seizures is not enough for a target finding. "
                "Remove it unless the frequency evidence itself names epileptic seizures "
                "or a seizure type."
            ),
            (
                "Remove vague ongoing-seizure statements such as continues to get "
                "seizures when the evidence does not give a count, rate, date, "
                "last-event anchor, or explicit qualitative change word."
            ),
            (
                "Remove vague diagnosis-level control such as epilepsy seems under "
                "control when there is no seizure type, count, date, duration, or "
                "no-further-seizures phrase."
            ),
            (
                "Remove bare remains seizure free findings when there is no duration, "
                "date, medication-change/surgery/clinic anchor, or no-further-seizures "
                "wording. Historical compact-section seizure counts remain scored."
            ),
            (
                "Classify febrile seizures, childhood febrile history, family history, "
                "and old background context as history_context_only unless the finding "
                "is a last-seizure status for the patient."
            ),
            (
                "If target_status is non_target_episode, history_context_only, "
                "diagnosis_without_frequency, future_risk_or_driving, or "
                "uncertain_not_scored, the action should usually be remove. Keep is "
                "reserved for target_epileptic_seizure_frequency."
            ),
            (
                "Classify driving clearance windows, no-seizure requirements for "
                "driving, medication titration intervals, and future-risk statements "
                "as future_risk_or_driving."
            ),
            (
                "Keep source-near seizure-type modifiers. If the evidence says focal "
                "seizures with altered awareness, keep that full phrase."
            ),
            (
                "If compact-section evidence says absence like seizures, keep text "
                "absence like seizures. Do not revise it to absence-like episodes."
            ),
            (
                "If a raw text includes focal seizures without change in awareness, "
                "revise text to focal seizures. Without change in awareness is context, "
                "not an impaired-awareness seizure-type modifier."
            ),
            (
                "For cluster sentences, return both the cluster mention and the "
                "within-cluster seizure rate when both are explicitly stated."
            ),
            (
                "For compact-section and narrative repeats, include both only when "
                "both evidence strings are present in the letter."
            ),
            (
                "For last-event summaries, keep the most recent last event. Do not "
                "add older previous-event rows."
            ),
            (
                "For no further seizures, no seizures, or seizures controlled, return "
                "a scored zero-count finding only when the evidence is about epileptic "
                "seizures, not a general diagnosis or non-target event."
            ),
            (
                "For no further seizures, text should be seizures unless the exact "
                "evidence says seizure free."
            ),
            (
                "Both text and evidence must be exact substrings from the letter. "
                "If a raw finding has the right clinical idea but the text is too "
                "specific or too broad, use action revise and provide corrected text."
            ),
            (
                "Do not copy all numeric/date fields into a revise decision. If a raw "
                "finding's counts, dates, or periods are already correct, leave those "
                "fields absent from the decision so they are preserved."
            ),
            (
                "If a raw finding has the wrong count, date, period, time_relation, "
                "point_in_time, age, or frequency_change, use action revise and include "
                "only the corrected fields. Omit fields that should stay unchanged."
            ),
            (
                "If a compact line has a last event plus a previous event, keep the "
                "last event and remove the older previous-event finding."
            ),
            (
                "For focal seizures without change in awareness, revise text to focal "
                "seizures even if the raw finding copied the full context phrase."
            ),
            (
                "Use findings_to_add only for a seizure-frequency finding that is "
                "clearly present in the letter but missing from raw_findings."
            ),
            "Return exactly one JSON object. No markdown code fences.",
        ],
        "decision_examples": [
            {
                "raw_finding": {
                    "text": "seizures",
                    "evidence": "several seizures since the last clinic appointment",
                },
                "decision": {
                    "raw_index": 0,
                    "target_status": "target_epileptic_seizure_frequency",
                    "action": "keep",
                    "rationale": "Counted seizures since last clinic are target frequency.",
                },
            },
            {
                "raw_finding": {
                    "text": "seizures",
                    "evidence": "definitely having a few seizures per year",
                },
                "decision": {
                    "raw_index": 1,
                    "target_status": "target_epileptic_seizure_frequency",
                    "action": "keep",
                    "rationale": "A few seizures per year is a target frequency estimate.",
                },
            },
            {
                "raw_finding": {
                    "text": "blackouts",
                    "evidence": "unwitnessed blackouts after reducing alcohol",
                },
                "decision": {
                    "raw_index": 2,
                    "target_status": "non_target_episode",
                    "action": "remove",
                    "rationale": "Blackouts are not stated as epileptic seizures.",
                },
            },
            {
                "raw_finding": {
                    "text": "generalised tonic clonic seizures",
                    "evidence": "2 generalised tonic clonic seizures 2018",
                    "clinical_kind": "dated_count",
                    "frequency_statement_type": "calendar_count",
                    "source_role": "compact_section",
                    "count": "2",
                    "year": "2018",
                },
                "decision": {
                    "raw_index": 3,
                    "target_status": "target_epileptic_seizure_frequency",
                    "action": "keep",
                    "rationale": (
                        "Historical dated seizure counts are target "
                        "seizure-frequency findings."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "Generalised tonic clonic seizure",
                    "evidence": "Generalised tonic clonic seizure-last event July 2016.",
                    "clinical_kind": "last_event",
                    "frequency_statement_type": "last_event_date",
                    "month": "July",
                    "year": "2016",
                },
                "decision": {
                    "raw_index": 4,
                    "target_status": "target_epileptic_seizure_frequency",
                    "action": "keep",
                    "rationale": (
                        "Last-event dates are target seizure-frequency findings."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "generalised tonic clonic seizure",
                    "evidence": "had a generalised tonic clonic seizure",
                    "clinical_kind": "dated_count",
                    "frequency_statement_type": "calendar_count",
                },
                "decision": {
                    "raw_index": 5,
                    "target_status": "target_epileptic_seizure_frequency",
                    "action": "revise",
                    "evidence": "last week and had a generalised tonic clonic seizure",
                    "time_relation": "during",
                    "point_in_time": "last week",
                    "rationale": (
                        "The event occurred last week, so the time anchor belongs "
                        "on the finding."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "focal seizures without change in awareness",
                    "evidence": (
                        "In March she had 2 to 3 of her focal seizures without "
                        "change in awareness"
                    ),
                    "clinical_kind": "dated_count",
                    "frequency_statement_type": "calendar_count",
                },
                "decision": {
                    "raw_index": 6,
                    "target_status": "target_epileptic_seizure_frequency",
                    "action": "revise",
                    "text": "focal seizures",
                    "rationale": (
                        "Without change in awareness is context, not an "
                        "impaired-awareness seizure type."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "Generalised tonic clonic seizure",
                    "evidence": "Previous event December 2015.",
                    "clinical_kind": "last_event",
                    "frequency_statement_type": "last_event_date",
                },
                "decision": {
                    "raw_index": 7,
                    "target_status": "history_context_only",
                    "action": "remove",
                    "rationale": (
                        "An older previous event is context when a newer last-event "
                        "date is also present."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "seizure free",
                    "evidence": "The epilepsy seems to be under control on levetiracetam.",
                    "clinical_kind": "frequency_change",
                    "frequency_statement_type": "change_only",
                },
                "decision": {
                    "raw_index": 8,
                    "target_status": "diagnosis_without_frequency",
                    "action": "remove",
                    "rationale": (
                        "Vague epilepsy control is not a source-near seizure-frequency "
                        "finding."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "episodes",
                    "evidence": "episodes around twice a week of an unusual thought",
                    "clinical_kind": "frequency_rate",
                    "frequency_statement_type": "background_rate",
                },
                "decision": {
                    "raw_index": 9,
                    "target_status": "non_target_episode",
                    "action": "remove",
                    "rationale": (
                        "The frequency clause names episodes, not epileptic seizures."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "minor seizures",
                    "evidence": (
                        "minor seizures. The episodes last no longer than 3 minutes "
                        "and occur 4 to 5 times a year"
                    ),
                    "clinical_kind": "frequency_rate",
                    "frequency_statement_type": "background_rate",
                    "count_low": "4",
                    "count_high": "5",
                    "period_count": "1",
                    "period_unit": "year",
                },
                "decision": {
                    "raw_index": 10,
                    "target_status": "non_target_episode",
                    "action": "remove",
                    "rationale": (
                        "The frequency belongs to nonspecific minor episodes rather "
                        "than a standard scored seizure type."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "general and complex partial seizures",
                    "evidence": "she continues to get general and complex partial seizures",
                    "clinical_kind": "frequency_change",
                    "frequency_statement_type": "change_only",
                },
                "decision": {
                    "raw_index": 11,
                    "target_status": "uncertain_not_scored",
                    "action": "remove",
                    "rationale": (
                        "Continues to get seizures is not a scored frequency without "
                        "a count, rate, date, or qualitative change word."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "focal seizure",
                    "evidence": "He has not had any previous seizures.",
                    "clinical_kind": "seizure_free",
                    "frequency_statement_type": "current_zero_no_duration",
                    "count": "0",
                },
                "decision": {
                    "raw_index": 12,
                    "target_status": "diagnosis_without_frequency",
                    "action": "remove",
                    "rationale": (
                        "No previous seizures in a single diagnostic seizure encounter "
                        "is not recurrent seizure frequency."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "generalised tonic clonic seizures",
                    "evidence": "approximately 15 seizures over 4 months",
                    "clinical_kind": "frequency_rate",
                    "frequency_statement_type": "background_rate",
                    "count": "15",
                    "period_count": "4",
                    "period_unit": "month",
                },
                "decision": {
                    "raw_index": 13,
                    "target_status": "target_epileptic_seizure_frequency",
                    "action": "revise",
                    "text": "seizures",
                    "rationale": (
                        "The frequency evidence says generic seizures, so the text "
                        "should stay generic."
                    ),
                },
            },
        ],
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def build_finalization_prompt_input(
    letter: ExectLetter,
    raw_findings: Sequence[ClinicalFindingRecord],
) -> str:
    """Build the second-pass final-findings rewrite payload for one letter."""

    payload = {
        "prompt_version": f"{PROMPT_VERSION}_finalizer",
        "task": (
            "Review the clinical letter and raw seizure-frequency findings. "
            "Return the complete final model-owned findings list as one JSON "
            "object with key 'findings'. Do not return edit decisions."
        ),
        "raw_findings": [finding.model_dump(mode="json") for finding in raw_findings],
        "output_schema": {
            "text": (
                "Exact short phrase from the letter naming the seizure type or "
                "seizure-free state."
            ),
            "evidence": (
                "Exact substring from the letter that supports this finding. Use "
                "the smallest clause or sentence that includes the frequency."
            ),
            "clinical_kind": (
                "One of frequency_rate, seizure_free, frequency_change, dated_count, "
                "last_event, cluster_frequency, other_frequency."
            ),
            "frequency_statement_type": (
                "header_count_since_anchor, calendar_count, "
                "calendar_occurrence_no_count, recurrence_interval, last_event_date, "
                "background_rate, seizure_free_duration, current_control_no_duration, "
                "current_zero_no_duration, change_only, or other_frequency."
            ),
            "source_role": "compact_section, narrative, or both.",
            "count": "Single seizure count when stated.",
            "count_low": "Lower seizure count when a range is stated.",
            "count_high": "Upper seizure count when a range is stated.",
            "period_count": "Number of time periods, usually 1.",
            "period_low": "Lower time-period count when a period range is stated.",
            "period_high": "Upper time-period count when a period range is stated.",
            "period_unit": "day, week, month, year, or fortnight when stated.",
            "time_relation": "during or since when explicitly stated.",
            "point_in_time": (
                "Clinical anchor when explicitly stated, for example medication "
                "change, last clinic, last week, surgery, or birthday."
            ),
            "day": "Day of month when explicitly stated.",
            "month": "Month when explicitly stated.",
            "year": "Year when explicitly stated.",
            "age_low": "Lower patient age when an age or age range is stated.",
            "age_high": "Upper patient age when an age range is stated.",
            "age_unit": "year or month when age_low or age_high is stated.",
            "frequency_change": (
                "decreased, frequent, increased, infrequent, or same when a change "
                "or relative frequency is stated."
            ),
            "confidence": "high, medium, or low.",
            "rationale": "One concise sentence explaining the final clinical reading.",
        },
        "required_keys_per_finding": [
            "text",
            "evidence",
            "clinical_kind",
            "frequency_statement_type",
            "source_role",
            "count",
            "count_low",
            "count_high",
            "period_count",
            "period_low",
            "period_high",
            "period_unit",
            "time_relation",
            "point_in_time",
            "day",
            "month",
            "year",
            "age_low",
            "age_high",
            "age_unit",
            "frequency_change",
            "confidence",
            "rationale",
        ],
        "finalization_checks": [
            (
                "Return the final findings list, not a list of decisions. If a raw "
                "finding is wrong, omit it. If a missing finding is present in the "
                "letter, add a complete finding. If an attribute is wrong, return the "
                "correct full finding."
            ),
            (
                "Use raw_findings as the starting point. When a raw finding is target "
                "and its fields are clinically correct, copy the entire raw finding "
                "object into final findings with all numeric, date, time_relation, "
                "point_in_time, source_role, confidence, and rationale fields preserved."
            ),
            (
                "Do not drop fields that were correct in raw_findings. In particular, "
                "preserve month, year, time_relation, count, count_low, count_high, "
                "period_count, period_unit, frequency_change, and point_in_time unless "
                "you are intentionally correcting that field."
            ),
            (
                "Every final finding object must contain all required keys, using null "
                "for unknown optional fields. A kept finding should look like the raw "
                "finding object, not a shortened summary."
            ),
            (
                "Keep target epileptic seizure-frequency findings: dated counts, "
                "dated occurrences, last-event dates, recurrent rates, current zero "
                "seizure status, and frequency-change-only statements."
            ),
            (
                "Remove non-target findings: migraine/headache frequency, blackouts, "
                "dizzy spells, dissociative or nonepileptic events, febrile history, "
                "family history, driving rules, medication titration intervals, vague "
                "diagnosis-level epilepsy control, and diagnostic episode descriptions "
                "whose frequency clause does not itself name seizures."
            ),
            (
                "Preserve source wording. If the evidence says seizures, text should "
                "be seizures even when the diagnosis names a specific seizure type. "
                "If the evidence says no further seizures, text should be seizures."
            ),
            (
                "If the evidence says focal seizures without change in awareness, "
                "text should be focal seizures. If it says focal seizures with "
                "altered or impaired awareness, keep that modifier."
            ),
            (
                "For compact-section and narrative repeats, include both findings "
                "when both source statements are present. Do not collapse repeated "
                "annotatable facts solely because they refer to the same seizure type."
            ),
            (
                "A current controlled or seizure-free statement does not replace "
                "historical dated compact-section facts; return both when both are "
                "target findings."
            ),
            (
                "For last-event plus previous-event summaries, return the most recent "
                "last event and do not return the older previous-event row."
            ),
            (
                "For a recent event such as last week or last month, set "
                "time_relation during and point_in_time to last week or last month."
            ),
            (
                "For has not had any further seizures, return text seizures, "
                "clinical_kind seizure_free, frequency_statement_type "
                "current_zero_no_duration, and count 0."
            ),
            (
                "For specific epileptic seizures completely under control after a "
                "medication increase, return the specific seizure zero-count finding "
                "and a separate seizures frequency_change infrequent finding when "
                "the improvement since medication change is stated."
            ),
            (
                "For a cluster of seizures in a dated month where a within-cluster "
                "rate is also stated, return both the cluster occurrence and the "
                "within-cluster seizure rate."
            ),
            (
                "For 6-9 seizures every week for 3 weeks, period_count is 1 and "
                "period_unit is week; 3 weeks is episode duration, not denominator."
            ),
            (
                "Use null for unknown optional fields, but every final finding should "
                "include all required keys. Return {\"findings\": []} when no target "
                "seizure-frequency finding is present."
            ),
            "Return exactly one JSON object. No markdown code fences.",
        ],
        "worked_examples": [
            {
                "note_fragment": "She has not had any further seizures.",
                "final_findings": [
                    {
                        "text": "seizures",
                        "evidence": "has not had any further seizures",
                        "clinical_kind": "seizure_free",
                        "frequency_statement_type": "current_zero_no_duration",
                        "source_role": "narrative",
                        "count": "0",
                        "count_low": None,
                        "count_high": None,
                        "period_count": None,
                        "period_low": None,
                        "period_high": None,
                        "period_unit": None,
                        "time_relation": None,
                        "point_in_time": None,
                        "day": None,
                        "month": None,
                        "year": None,
                        "age_low": None,
                        "age_high": None,
                        "age_unit": None,
                        "frequency_change": None,
                        "confidence": "high",
                        "rationale": "The source states no further seizures.",
                    }
                ],
            },
            {
                "note_fragment": (
                    "The epilepsy seems to be under control on medication. "
                    "Review in nine months."
                ),
                "final_findings": [],
            },
            {
                "note_fragment": (
                    "Diagnosis: generalised tonic clonic seizures. She is still "
                    "having approximately 15 seizures over 4 months."
                ),
                "final_findings": [
                    {
                        "text": "seizures",
                        "evidence": "approximately 15 seizures over 4 months",
                        "clinical_kind": "frequency_rate",
                        "frequency_statement_type": "background_rate",
                        "source_role": "narrative",
                        "count": "15",
                        "count_low": None,
                        "count_high": None,
                        "period_count": "4",
                        "period_low": None,
                        "period_high": None,
                        "period_unit": "month",
                        "time_relation": None,
                        "point_in_time": None,
                        "day": None,
                        "month": None,
                        "year": None,
                        "age_low": None,
                        "age_high": None,
                        "age_unit": None,
                        "frequency_change": None,
                        "confidence": "high",
                        "rationale": (
                            "The frequency evidence says generic seizures, so text "
                            "remains seizures."
                        ),
                    }
                ],
            },
        ],
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_clinical_findings_json(
    raw_output: str,
) -> tuple[ClinicalFindingsRecord | None, list[str]]:
    """Parse and schema-validate one model output string."""

    payload, load_errors = loads_json_or_literal(raw_output)
    if payload is None:
        return None, load_errors

    payload, coerce_notes = _coerce_payload(payload)
    errors: list[str] = [
        *load_errors,
        *_dropped_projection_field_notes(payload),
        *coerce_notes,
    ]

    try:
        record = ClinicalFindingsRecord.model_validate(payload)
    except ValidationError as exc:
        return None, [f"schema_validation_error: {exc.errors()[0]['msg']}"]

    return record, errors


def _dropped_projection_field_notes(payload: Any) -> list[str]:
    """Report model-supplied benchmark/guideline fields ignored by the schema."""

    if not isinstance(payload, dict):
        return []
    notes: list[str] = []
    for collection_name in ("event_frames", "findings"):
        records = payload.get(collection_name)
        if not isinstance(records, list):
            continue
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            for key in sorted(_DISALLOWED_MODEL_PROJECTION_FIELDS & record.keys()):
                notes.append(
                    "dropped_model_supplied_projection_field: "
                    f"{collection_name}[{index}] {key!r}"
                )
    return notes


def parse_verification_decisions_json(
    raw_output: str,
) -> tuple[VerificationDecisionList | None, list[str]]:
    """Parse and schema-validate one verifier output string."""

    payload, load_errors = loads_json_or_literal(raw_output)
    if payload is None:
        return None, load_errors
    payload, coerce_notes = _coerce_verification_payload(payload)
    errors = [*load_errors, *coerce_notes]

    try:
        record = VerificationDecisionList.model_validate(payload)
    except ValidationError as exc:
        return None, [*errors, f"schema_validation_error: {exc.errors()[0]['msg']}"]

    return record, errors


def _coerce_verification_payload(payload: Any) -> tuple[Any, list[str]]:
    notes: list[str] = []
    if not isinstance(payload, dict):
        return payload, notes

    additions = payload.get("findings_to_add")
    if not isinstance(additions, list):
        return payload, notes

    kept: list[Any] = []
    for i, addition in enumerate(additions):
        if not isinstance(addition, dict):
            kept.append(addition)
            continue
        if addition.get("text") and addition.get("clinical_kind"):
            kept.append(addition)
            continue
        notes.append(
            f"dropped_invalid_findings_to_add_record: index={i} "
            "missing text/clinical_kind"
        )
    return {**payload, "findings_to_add": kept}, notes


def apply_verification_decisions(
    raw_findings: Sequence[ClinicalFindingRecord],
    decisions: VerificationDecisionList,
) -> tuple[list[ClinicalFindingRecord], list[str]]:
    """Apply model-authored verifier decisions to first-pass findings."""

    warnings: list[str] = []
    by_index = {decision.raw_index: decision for decision in decisions.decisions}
    final_findings: list[ClinicalFindingRecord] = []

    for index, finding in enumerate(raw_findings):
        decision = by_index.get(index)
        if decision is None:
            warnings.append(f"verification_missing_decision_kept: raw_index={index}")
            final_findings.append(finding)
            continue
        if decision.action == "remove":
            warnings.append(f"verification_removed: raw_index={index}")
            continue
        if decision.action == "keep":
            final_findings.append(finding)
            continue

        revisable_fields = _SCALAR_FINDING_FIELDS - {"confidence"}
        updates = {
            key: getattr(decision, key)
            for key in revisable_fields
            if key in decision.model_fields_set
        }
        if "rationale" in updates and not updates["rationale"]:
            updates.pop("rationale")
        try:
            final_findings.append(
                ClinicalFindingRecord.model_validate({
                    **finding.model_dump(mode="json"),
                    **updates,
                })
            )
        except ValidationError as exc:
            warnings.append(
                f"verification_revise_invalid_kept: raw_index={index} "
                f"{exc.errors()[0]['msg']}"
            )
            final_findings.append(finding)

    for extra in decisions.findings_to_add:
        final_findings.append(extra)
        warnings.append(f"verification_added: text={extra.text!r}")

    return final_findings, warnings


def _coerce_payload(payload: Any) -> tuple[Any, list[str]]:
    notes: list[str] = []
    if not isinstance(payload, dict):
        return payload, notes
    findings_raw = payload.get("findings")
    if findings_raw is None and isinstance(payload.get("mentions"), list):
        findings_raw = payload.get("mentions")
        notes.append("coerced_mentions_key_to_findings")
    coerced_payload = dict(payload)

    if isinstance(findings_raw, list):
        coerced_payload["findings"] = _coerce_record_list(
            findings_raw,
            scalar_fields=_SCALAR_FINDING_FIELDS,
            notes=notes,
            record_name="finding",
            coerce_statement_type=True,
        )

    event_frames_raw = payload.get("event_frames")
    if isinstance(event_frames_raw, list):
        coerced_payload["event_frames"] = _coerce_record_list(
            event_frames_raw,
            scalar_fields=_SCALAR_EVENT_FRAME_FIELDS,
            notes=notes,
            record_name="event_frame",
            coerce_statement_type=False,
        )

    return coerced_payload, notes


def _coerce_record_list(
    records: Sequence[Any],
    *,
    scalar_fields: frozenset[str],
    notes: list[str],
    record_name: str,
    coerce_statement_type: bool,
) -> list[Any]:
    coerced_records: list[Any] = []
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            coerced_records.append(record)
            continue
        new_record = dict(record)
        clinical_kind = str(new_record.get("clinical_kind", ""))
        if (
            coerce_statement_type
            and clinical_kind
            and clinical_kind not in _CLINICAL_KIND_VALUES
            and clinical_kind in _STATEMENT_TYPE_TO_KIND
        ):
            new_record.setdefault("frequency_statement_type", clinical_kind)
            new_record["clinical_kind"] = _STATEMENT_TYPE_TO_KIND[clinical_kind]
            notes.append(
                f"coerced_statement_type_from_clinical_kind: {record_name}[{i}] "
                f"{clinical_kind!r}"
            )
        for key, value in record.items():
            if key not in scalar_fields or value is None:
                continue
            if not isinstance(value, str):
                new_record[key] = str(value)
                notes.append(
                    f"coerced_field_value: {record_name}[{i}] {key!r} "
                    f"{value!r} -> {new_record[key]!r}"
                )
        coerced_records.append(new_record)
    return coerced_records


def project_finding_to_attributes(
    finding: ClinicalFindingRecord,
    *,
    include_cui: bool,
) -> tuple[dict[str, str], list[str]]:
    """Project explicit model-emitted finding fields to ExECTv2 attributes."""

    attrs: dict[str, str] = {}
    warnings: list[str] = []

    count_low = _normalized_count_or_none(finding.count_low)
    count_high = _normalized_count_or_none(finding.count_high)
    if count_low is not None and count_high is not None and count_low == count_high:
        attrs["NumberOfSeizures"] = count_low
    else:
        _add_count(attrs, "NumberOfSeizures", finding.count)
        if count_low is not None:
            attrs["LowerNumberOfSeizures"] = count_low
        if count_high is not None:
            attrs["UpperNumberOfSeizures"] = count_high

    period_low = _normalized_count_or_none(finding.period_low)
    period_high = _normalized_count_or_none(finding.period_high)
    period_has_range = period_low is not None or period_high is not None
    if not period_has_range:
        _add_count(attrs, "NumberOfTimePeriods", finding.period_count)
    elif period_low is not None and period_high is not None and period_low == period_high:
        attrs["NumberOfTimePeriods"] = period_low
    elif period_low is not None and period_high is None:
        attrs["NumberOfTimePeriods"] = period_low
    elif period_high is not None and period_low is None:
        attrs["NumberOfTimePeriods"] = period_high
    else:
        attrs["LowerNumberOfTimePeriods"] = period_low or ""
        attrs["UpperNumberOfTimePeriods"] = period_high or ""

    if finding.clinical_kind == "seizure_free" and not any(
        key in attrs
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
        )
    ):
        attrs["NumberOfSeizures"] = "0"
    elif finding.clinical_kind == "last_event" and not any(
        key in attrs
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
        )
    ):
        attrs["NumberOfSeizures"] = "0"
    elif finding.frequency_statement_type == "calendar_occurrence_no_count" and any(
        _filled(value) for value in (finding.day, finding.month, finding.year)
    ):
        attrs["NumberOfSeizures"] = "1"
    elif not any(
        key in attrs
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
        )
    ) and any(
        key in attrs
        for key in (
            "NumberOfTimePeriods",
            "LowerNumberOfTimePeriods",
            "UpperNumberOfTimePeriods",
        )
    ):
        attrs["NumberOfSeizures"] = "1"

    if _filled(finding.period_unit):
        period_unit = (finding.period_unit or "").strip().lower()
        if period_unit in {"fortnight", "fortnights"}:
            attrs["TimePeriod"] = "Week"
            attrs["NumberOfTimePeriods"] = "2"
        else:
            attrs["TimePeriod"] = normalize_unit(finding.period_unit or "")
        if (
            finding.frequency_statement_type == "background_rate"
            and "NumberOfTimePeriods" not in attrs
            and "LowerNumberOfTimePeriods" not in attrs
            and "UpperNumberOfTimePeriods" not in attrs
        ):
            attrs["NumberOfTimePeriods"] = "1"
    if _filled(finding.time_relation):
        mapped = _map_alias(finding.time_relation, _TIME_RELATION_ALIASES)
        if (
            mapped == "Since"
            and finding.frequency_statement_type == "background_rate"
            and not _filled(finding.point_in_time)
        ):
            warnings.append("dropped_unanchored_background_rate_since")
        elif mapped:
            attrs["TimeSince_or_TimeOfEvent"] = mapped
        else:
            warnings.append(f"dropped_unmapped_time_relation: {finding.time_relation!r}")
    elif finding.frequency_statement_type == "header_count_since_anchor":
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
    elif finding.clinical_kind == "last_event" and any(
        _filled(value) for value in (finding.day, finding.month, finding.year)
    ):
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
    elif finding.clinical_kind == "dated_count" and any(
        _filled(value) for value in (finding.day, finding.month, finding.year)
    ):
        attrs["TimeSince_or_TimeOfEvent"] = "During"
    if _filled(finding.point_in_time):
        mapped = _map_alias(finding.point_in_time, _POINT_IN_TIME_ALIASES)
        if mapped:
            attrs["PointInTime"] = mapped
        else:
            warnings.append(f"dropped_unmapped_point_in_time: {finding.point_in_time!r}")
    elif finding.frequency_statement_type == "header_count_since_anchor":
        attrs["PointInTime"] = "LastClinic"
    if _filled(finding.frequency_change):
        mapped = _map_alias(finding.frequency_change, _FREQUENCY_CHANGE_ALIASES)
        if mapped:
            attrs["FrequencyChange"] = mapped
        else:
            warnings.append(f"dropped_unmapped_frequency_change: {finding.frequency_change!r}")

    if _filled(finding.day):
        attrs["DayDate"] = normalize_count(finding.day or "")
    if _filled(finding.month):
        attrs["MonthDate"] = normalize_month(finding.month or "")
    if _filled(finding.year):
        attrs["YearDate"] = str(finding.year).strip()
    if _filled(finding.age_low):
        attrs["AgeLower"] = normalize_count(finding.age_low or "")
    if _filled(finding.age_high):
        attrs["AgeUpper"] = normalize_count(finding.age_high or "")
    if _filled(finding.age_unit):
        attrs["AgeUnit"] = normalize_unit(finding.age_unit or "")

    repaired, warnings = _repair_projected_attributes(attrs, warnings)
    if not include_cui:
        return repaired, warnings

    projected = project_cuis(
        PredictedLetter(
            letter_id="projection-preview",
            mentions=(
                PredictedMention(
                    entity=ENTITY_NAME,
                    text=finding.text,
                    attributes=repaired,
                    evidence=finding.evidence,
                ),
            ),
        )
    )
    projected_attrs = dict(projected.mentions[0].attributes)
    if "CUI" not in projected_attrs:
        warnings.append(f"cui_not_mapped: {finding.text!r}")
    return projected_attrs, warnings


def _add_count(attrs: dict[str, str], key: str, value: str | None) -> None:
    if _filled(value):
        attrs[key] = normalize_count(value or "")


def _normalized_count_or_none(value: str | None) -> str | None:
    if not _filled(value):
        return None
    return normalize_count(value or "")


def _filled(value: str | None) -> bool:
    return bool(value and value.strip())


def _map_alias(value: str | None, aliases: Mapping[str, str]) -> str | None:
    if not value:
        return None
    compact = re.sub(r"[\s_-]+", " ", value.strip().lower()).strip()
    return aliases.get(compact) or aliases.get(value.strip().lower())


def _repair_projected_attributes(
    attrs: dict[str, str], warnings: list[str]
) -> tuple[dict[str, str], list[str]]:
    spec = ENTITY_REGISTRY[ENTITY_NAME]
    repaired: dict[str, str] = {}
    for key, value in attrs.items():
        if key in spec.noise_attributes:
            continue
        if key not in spec.legal_attributes:
            warnings.append(f"dropped_illegal_attribute: {key!r}")
            continue
        normalized_value = canonicalize_attribute_value(key, value)
        if normalized_value != value:
            warnings.append(
                f"normalized_attribute_value: {key!r}={value!r} -> {normalized_value!r}"
            )
        if key in spec.closed_vocab and normalized_value not in spec.closed_vocab[key]:
            warnings.append(
                f"dropped_illegal_value: {key!r}={normalized_value!r}"
            )
            continue
        repaired[key] = normalized_value
    return repaired, warnings


def to_predicted_letters(
    letter_id: str,
    findings: list[ClinicalFindingRecord],
    *,
    note_text: str,
) -> tuple[dict[str, PredictedLetter], list[str]]:
    """Build format-only and CUI-projected prediction layers."""

    warnings: list[str] = []
    layer_mentions: dict[str, list[PredictedMention]] = {
        layer: [] for layer in _OUTPUT_LAYERS
    }

    for finding in findings:
        if finding.frequency_statement_type == "current_control_no_duration":
            warnings.append(f"model_excluded_current_control_no_duration: text={finding.text!r}")
            continue
        if not finding.evidence:
            warnings.append(f"dropped_empty_evidence: text={finding.text!r}")
            continue
        if not evidence_is_substring(note_text, finding.evidence):
            warnings.append(f"dropped_evidence_not_substring: text={finding.text!r}")
            continue

        attrs, attr_warnings = project_finding_to_attributes(finding, include_cui=False)
        warnings.extend(f"format_projected: {w}" for w in attr_warnings)
        layer_mentions["format_projected"].append(
            PredictedMention(
                entity=ENTITY_NAME,
                text=finding.text,
                attributes=attrs,
                evidence=finding.evidence,
                confidence=finding.confidence,
                rationale=finding.rationale,
                component_owner="llm_only_clinical_findings",
            )
        )

    format_projected = PredictedLetter(
        letter_id=letter_id,
        mentions=tuple(layer_mentions["format_projected"]),
        diagnostics={"prompt_version": PROMPT_VERSION, "layer": "format_projected"},
    )
    cui_projected = project_cuis(format_projected)
    layers = {
        "format_projected": format_projected,
        "cui_projected": cui_projected.model_copy(
            update={
                "diagnostics": {
                    **dict(format_projected.diagnostics),
                    "layer": "cui_projected",
                    "source_layer": "format_projected",
                    "cui_projected_mentions": cui_projected.diagnostics[
                        "cui_projected_mentions"
                    ],
                }
            }
        ),
    }
    return layers, warnings


def build_plan11_event_state_route(
    letter_id: str,
    record: ClinicalFindingsRecord,
    *,
    note_text: str,
) -> tuple[dict[str, PredictedLetter], dict[str, Any], list[str]]:
    """Run the documented Plan 11 SF event/state ladder over model output.

    The helper intentionally consumes only model-owned ``findings`` for scored
    mentions. ``event_frames`` are audit substrate and never become scored
    findings here, which keeps deterministic code from acting as a hidden
    clinical selector.
    """

    layers, warnings = to_predicted_letters(letter_id, record.findings, note_text=note_text)
    policy_counts = _post_llm_state_policy_counts(warnings)
    diagnostics = {
        "route_version": PLAN11_EVENT_STATE_ROUTE_VERSION,
        "route_contract": (
            "LLM owns raw_event_frames and raw_findings; deterministic code is "
            "limited to schema transport, evidence validation, format projection, "
            "CUI sidecar projection, no-op SF certainty sidecar, and explicitly "
            "named post-LLM state policy."
        ),
        "aggregate_ownership": (
            "llm_first"
            if not policy_counts
            else "llm_first_with_declared_post_llm_state_policy"
        ),
        "deterministic_clinical_selection": False,
        "deterministic_selection_actions": [],
        "post_llm_state_policy_counts": policy_counts,
        "layers": _plan11_layer_rows(record, layers, warnings, policy_counts),
    }
    return layers, diagnostics, warnings


def _post_llm_state_policy_counts(warnings: Sequence[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for warning in warnings:
        if warning.startswith("model_excluded_current_control_no_duration"):
            key = "current_control_no_duration_excluded"
            counts[key] = counts.get(key, 0) + 1
    return counts


def _plan11_layer_rows(
    record: ClinicalFindingsRecord,
    layers: Mapping[str, PredictedLetter],
    warnings: Sequence[str],
    policy_counts: Mapping[str, int],
) -> list[dict[str, Any]]:
    evidence_invalid = sum(
        1
        for warning in warnings
        if warning.startswith(("dropped_empty_evidence", "dropped_evidence_not_substring"))
    )
    counts = {
        "raw_event_frames": len(record.event_frames),
        "raw_findings": len(record.findings),
        "schema_valid_findings": len(record.findings),
        "evidence_validated": len(layers["format_projected"].mentions),
        "format_projected": len(layers["format_projected"].mentions),
        "cui_projected": len(layers["cui_projected"].mentions),
        "certainty_projected": 0,
        "post_llm_state_policy": sum(policy_counts.values()),
        "benchmark_rendered": len(layers["cui_projected"].mentions),
    }
    diagnostics = {
        "evidence_validated": {
            "evidence_invalid": evidence_invalid,
            "input_findings": len(record.findings),
        },
        "post_llm_state_policy": {"actions": dict(policy_counts)},
        "certainty_projected": {"sf_policy": "no_op"},
    }
    return [
        {
            **layer,
            "count": counts[layer["layer"]],
            "diagnostics": diagnostics.get(layer["layer"], {}),
        }
        for layer in PLAN11_EVENT_STATE_LAYER_LADDER
    ]


def run_split(
    letters: Sequence[ExectLetter],
    *,
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
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the clinical-findings extractor over a split."""

    program = DspyClinicalFindingsSFExtractor()
    verifier = DspyClinicalFindingsSFVerifier()
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

    order = [letter.letter_id for letter in letters]
    requested = set(order)
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None, key="letter_id"
    )
    rows: list[dict[str, Any]] = [
        r for r in existing_rows if r.get("letter_id") in requested
    ]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    for letter in todo:
        prompt_input_json = build_prompt_input(letter)
        raw_output = ""
        call_error: str | None = None

        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"

        extraction, parse_errors = (
            parse_clinical_findings_json(raw_output)
            if raw_output
            else (None, ["not_run"])
        )
        findings = extraction.findings if extraction else []
        event_frames = extraction.event_frames if extraction else []

        verification_prompt_input_json = ""
        verification_raw_output = ""
        verification_call_error: str | None = None
        verification_parse_errors: list[str] = []
        verified_findings: list[ClinicalFindingRecord] = []
        verification_decisions: VerificationDecisionList | None = None
        verification_warnings: list[str] = []
        final_findings = findings

        if mode == "live" and findings:
            verification_prompt_input_json = build_verification_prompt_input(
                letter,
                findings,
                event_frames,
            )
            try:
                verification_prediction = verifier(
                    prompt_input_json=verification_prompt_input_json
                )
                verification_raw_output = str(verification_prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                verification_call_error = f"{type(exc).__name__}: {exc}"

            verification_decisions, verification_parse_errors = (
                parse_verification_decisions_json(verification_raw_output)
                if verification_raw_output
                else (None, ["not_run"])
            )
            if verification_decisions is not None:
                verified_findings, verification_warnings = apply_verification_decisions(
                    findings,
                    verification_decisions,
                )
                final_findings = verified_findings
        elif mode == "prompt-only":
            verification_parse_errors = ["not_run"]

        final_record = ClinicalFindingsRecord(
            family_checklist=(
                extraction.family_checklist
                if extraction is not None
                else FindingFamilyChecklist()
            ),
            event_frames=event_frames,
            findings=final_findings,
        )
        layers, route_diagnostics, projection_warnings = build_plan11_event_state_route(
            letter.letter_id, final_record, note_text=letter.note_text
        )

        gold_sf = letter.entities(ENTITY_NAME)
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "pipeline_family": PIPELINE_FAMILY,
                "prompt_version": PROMPT_VERSION,
                "model": model,
                "mode": mode,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "verification_prompt_input_json": verification_prompt_input_json,
                "verification_raw_output": verification_raw_output,
                "verification_call_error": verification_call_error,
                "verification_parse_errors": verification_parse_errors,
                "verification_warnings": verification_warnings,
                "projection_warnings": projection_warnings,
                "plan11_event_state_route": route_diagnostics,
                "event_frames": [
                    frame.model_dump(mode="json") for frame in event_frames
                ],
                "raw_extraction_findings": [
                    finding.model_dump(mode="json") for finding in findings
                ],
                "verified_model_findings": [
                    finding.model_dump(mode="json") for finding in verified_findings
                ],
                "verification_decisions": (
                    verification_decisions.model_dump(mode="json")
                    if verification_decisions is not None
                    else None
                ),
                "raw_model_findings": [
                    finding.model_dump(mode="json") for finding in final_findings
                ],
                "n_event_frames": len(event_frames),
                "n_extraction_findings": len(findings),
                "n_verified_findings": len(verified_findings),
                "n_mentions_raw": len(final_findings),
                "n_mentions_scored": len(layers["cui_projected"].mentions),
                "n_format_projected_mentions": len(layers["format_projected"].mentions),
                "n_cui_projected_mentions": len(layers["cui_projected"].mentions),
                "n_evidence_invalid": (
                    len(final_findings) - len(layers["format_projected"].mentions)
                ),
                "format_projected_mentions": _letter_mentions_to_rows(
                    layers["format_projected"]
                ),
                "cui_projected_mentions": _letter_mentions_to_rows(
                    layers["cui_projected"]
                ),
                "predicted_mentions": _letter_mentions_to_rows(
                    layers["cui_projected"]
                ),
                "gold_mentions": [
                    {"text": a.text, "attributes": dict(a.attributes)}
                    for a in gold_sf
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
        "pipeline_family": PIPELINE_FAMILY,
        "prompt_version": PROMPT_VERSION,
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


def _letter_mentions_to_rows(letter: PredictedLetter) -> list[dict[str, Any]]:
    return [
        {
            "text": m.text,
            "attributes": dict(m.attributes),
            "evidence": m.evidence,
            "confidence": m.confidence,
            "rationale": m.rationale,
        }
        for m in letter.mentions
    ]


def summarize_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate statistics and F1 scores across all rows and layers."""

    n = len(rows)
    if n == 0:
        return {"examples": 0}

    call_failures = sum(bool(r.get("call_error")) for r in rows)
    verification_call_failures = sum(bool(r.get("verification_call_error")) for r in rows)
    parse_failures = sum(_has_blocking_parse_issue(r.get("parse_errors")) for r in rows)
    verification_parse_failures = sum(
        _has_blocking_parse_issue(r.get("verification_parse_errors")) for r in rows
    )
    n_event_frames = sum(int(r.get("n_event_frames", 0)) for r in rows)
    n_mentions_raw = sum(int(r.get("n_mentions_raw", 0)) for r in rows)
    n_extraction_findings = sum(int(r.get("n_extraction_findings", 0)) for r in rows)
    n_verified_findings = sum(int(r.get("n_verified_findings", 0)) for r in rows)
    n_evidence_invalid = sum(int(r.get("n_evidence_invalid", 0)) for r in rows)

    layer_summaries = {
        layer: _score_layer(rows, mention_field=f"{layer}_mentions")
        for layer in _OUTPUT_LAYERS
    }
    primary = layer_summaries["cui_projected"]
    route_summary = _plan11_route_summary(rows)

    return {
        "examples": n,
        "call_failures": call_failures,
        "verification_call_failures": verification_call_failures,
        "parse_failures": parse_failures,
        "verification_parse_failures": verification_parse_failures,
        "n_event_frames": n_event_frames,
        "n_extraction_findings": n_extraction_findings,
        "n_verified_findings": n_verified_findings,
        "n_mentions_raw": n_mentions_raw,
        "n_mentions_scored": primary["n_mentions_scored"],
        "n_format_projected_mentions": layer_summaries["format_projected"][
            "n_mentions_scored"
        ],
        "n_cui_projected_mentions": primary["n_mentions_scored"],
        "n_evidence_invalid": n_evidence_invalid,
        "evidence_validity_rate": (
            round((n_mentions_raw - n_evidence_invalid) / n_mentions_raw, 4)
            if n_mentions_raw
            else 1.0
        ),
        "scores": primary["scores"],
        "attribution_layers": layer_summaries,
        "plan11_event_state_route": route_summary,
    }


def _plan11_route_summary(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    layer_counts = {layer["layer"]: 0 for layer in PLAN11_EVENT_STATE_LAYER_LADDER}
    policy_counts: dict[str, int] = {}
    deterministic_selection_rows = 0
    ownerships: set[str] = set()
    for row in rows:
        route = row.get("plan11_event_state_route") or {}
        ownership = route.get("aggregate_ownership")
        if ownership:
            ownerships.add(str(ownership))
        if route.get("deterministic_clinical_selection"):
            deterministic_selection_rows += 1
        for layer in route.get("layers") or []:
            name = str(layer.get("layer", ""))
            if name in layer_counts:
                layer_counts[name] += int(layer.get("count", 0))
        for key, count in (route.get("post_llm_state_policy_counts") or {}).items():
            policy_counts[str(key)] = policy_counts.get(str(key), 0) + int(count)

    if deterministic_selection_rows:
        aggregate = "hybrid_or_diagnostic_required"
    elif policy_counts:
        aggregate = "llm_first_with_declared_post_llm_state_policy"
    else:
        aggregate = "llm_first"
    return {
        "route_version": PLAN11_EVENT_STATE_ROUTE_VERSION,
        "aggregate_ownership": aggregate,
        "row_ownerships": sorted(ownerships),
        "deterministic_clinical_selection_rows": deterministic_selection_rows,
        "post_llm_state_policy_counts": policy_counts,
        "layer_counts": layer_counts,
        "layer_ladder": list(PLAN11_EVENT_STATE_LAYER_LADDER),
    }


def _score_layer(
    rows: Sequence[dict[str, Any]], *, mention_field: str
) -> dict[str, Any]:
    gold_letters = _reconstruct_gold_letters(rows)
    pred_letters = _reconstruct_pred_letters(rows, mention_field=mention_field)
    scores: dict[str, Any] = {}
    for config_name, config in [
        ("phrase_only", PHRASE_ONLY),
        ("sf_semantic", SF_SEMANTIC),
        ("sf_benchmark", SF_BENCHMARK),
    ]:
        entity_score: EntityScore = score_entity(
            gold_letters, pred_letters, ENTITY_NAME, config
        )
        scores[config_name] = {
            "per_item": {
                "precision": round(entity_score.per_item.precision, 4),
                "recall": round(entity_score.per_item.recall, 4),
                "f1": round(entity_score.per_item.f1, 4),
                "tp": entity_score.per_item.tp,
                "fp": entity_score.per_item.fp,
                "fn": entity_score.per_item.fn,
            },
            "per_letter": {
                "precision": round(entity_score.per_letter.precision, 4),
                "recall": round(entity_score.per_letter.recall, 4),
                "f1": round(entity_score.per_letter.f1, 4),
                "tp": entity_score.per_letter.tp,
                "fp": entity_score.per_letter.fp,
                "fn": entity_score.per_letter.fn,
            },
        }
    return {
        "n_mentions_scored": sum(
            len(r.get(mention_field) or []) for r in rows
        ),
        "scores": scores,
    }


def _reconstruct_gold_letters(rows: Sequence[dict[str, Any]]) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        annotations = tuple(
            ExectAnnotation(
                entity=ENTITY_NAME,
                text=m["text"],
                attributes=m["attributes"],
            )
            for m in (row.get("gold_mentions") or [])
        )
        letters.append(
            ExectLetter(
                letter_id=row["letter_id"],
                note_text="",
                annotations=annotations,
            )
        )
    return letters


def _reconstruct_pred_letters(
    rows: Sequence[dict[str, Any]], *, mention_field: str
) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        pred_letter = PredictedLetter(
            letter_id=row["letter_id"],
            mentions=tuple(
                PredictedMention(
                    entity=ENTITY_NAME,
                    text=m["text"],
                    attributes=m["attributes"],
                    evidence=m.get("evidence", ""),
                    confidence=m.get("confidence", "medium"),
                    rationale=m.get("rationale", ""),
                )
                for m in (row.get(mention_field) or [])
            ),
        )
        letters.append(to_exect_letter(pred_letter))
    return letters


def write_jsonl(rows: Sequence[dict[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: dict[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    """Write a concise Markdown run report."""

    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary") or summarize_rows(rows)
    lines = [
        "# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Pipeline family: `{metadata.get('pipeline_family', PIPELINE_FAMILY)}`",
        f"- Prompt version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- Split: `{metadata.get('split')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Letters: {summary.get('examples', 0)}",
        "",
        "## Gate Summary",
        "",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Verification call failures: {summary.get('verification_call_failures', 0)}",
        f"- Parse/schema failures: {summary.get('parse_failures', 0)}",
        f"- Verification parse/schema failures: {summary.get('verification_parse_failures', 0)}",
        f"- Event frames: {summary.get('n_event_frames', 0)}",
        f"- First-pass findings: {summary.get('n_extraction_findings', 0)}",
        f"- Verified findings: {summary.get('n_verified_findings', 0)}",
        f"- Final model findings: {summary.get('n_mentions_raw', 0)}",
        f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
        f"- Format-projected mentions: {summary.get('n_format_projected_mentions', 0)}",
        f"- CUI-projected mentions: {summary.get('n_cui_projected_mentions', 0)}",
        (
            f"- Evidence validity rate: "
            f"{summary.get('evidence_validity_rate', 0.0):.4f}"
        ),
        "",
        "## Plan 11 Event/State Route",
        "",
    ]
    route = summary.get("plan11_event_state_route", {})
    lines.extend(
        [
            f"- Route version: `{route.get('route_version', PLAN11_EVENT_STATE_ROUTE_VERSION)}`",
            f"- Aggregate ownership: `{route.get('aggregate_ownership', 'llm_first')}`",
            (
                "- Deterministic clinical-selection rows: "
                f"{route.get('deterministic_clinical_selection_rows', 0)}"
            ),
            (
                "- Post-LLM state policy actions: "
                f"{route.get('post_llm_state_policy_counts', {})}"
            ),
            "",
            "| Layer | Owner | Count | Claim role |",
            "| --- | --- | ---: | --- |",
        ]
    )
    layer_counts = route.get("layer_counts", {})
    for layer in route.get("layer_ladder", PLAN11_EVENT_STATE_LAYER_LADDER):
        name = layer["layer"]
        lines.append(
            f"| `{name}` | `{layer['owner']}` | {layer_counts.get(name, 0)} "
            f"| {layer['claim_role']} |"
        )
    lines.extend(
        [
            "",
        "## Attribution Layers",
        "",
        ]
    )
    layers = summary.get("attribution_layers", {})
    for layer in _OUTPUT_LAYERS:
        layer_summary = layers.get(layer, {})
        scores = layer_summary.get("scores", {})
        lines.extend([f"### {layer}", ""])
        for config_name in ("phrase_only", "sf_semantic", "sf_benchmark"):
            s = scores.get(config_name, {})
            pi = s.get("per_item", {})
            pl = s.get("per_letter", {})
            lines.append(
                f"- {config_name} per-item F1={pi.get('f1', 0):.3f} "
                f"(P={pi.get('precision', 0):.3f} R={pi.get('recall', 0):.3f}); "
                f"per-letter F1={pl.get('f1', 0):.3f}"
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _has_blocking_parse_issue(errors: Any) -> bool:
    return any(
        str(e).startswith(("invalid_json:", "schema_validation_error:", "not_run"))
        for e in (errors or [])
    )


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
    emit_run_checkpoint(
        rows,
        total=total,
        jsonl_path=jsonl_path,
        report_path=report_path,
        metadata={
            "pipeline_family": PIPELINE_FAMILY,
            "prompt_version": PROMPT_VERSION,
            "split": split,
            "model": model,
            "mode": mode,
        },
        summarize_rows=summarize_rows,
        write_jsonl=write_jsonl,
        write_report=write_report,
    )
