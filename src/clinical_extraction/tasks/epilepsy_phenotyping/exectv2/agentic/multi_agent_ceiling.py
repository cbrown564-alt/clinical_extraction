"""Angle 2 (ceiling) multi-agent architectures for ExECTv2 SeizureFrequency.

Ports `tasks.seizure_frequency.gan2026.agentic.multi_agent_ceiling`'s
pattern: three bounded specialist roles whose output schema cannot contain
a `mentions`/final-answer field (structurally, not just by instruction),
feeding a resolver that alone may emit the final SF extraction. See
docs/experiments/exectv2/seizure_frequency/exectv2_sf_agentic_redo_predeclaration_2026-07-01.md.

Specialists target SF's two documented weak spots specifically: cluster-
axis ambiguity and the direction-blind "changed" class (see
docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md).
"""
from __future__ import annotations

import json
from typing import Any

import dspy

from clinical_extraction.core.agentic_contracts import AgentBudget

CONDITION_D3_STATIC = "multi_agent_d3_static"
CONDITION_DYNAMIC_ORCHESTRATOR = "multi_agent_dynamic_orchestrator"
PROMPT_VERSION = "exectv2_sf_multi_agent_ceiling_v0_1"

D3_STATIC_BUDGET = AgentBudget(
    model_calls_per_row=4,
    prompt_token_budget=4_000,
    max_completion_tokens_per_call=800,
    max_tool_calls_per_row=0,
    max_tool_output_tokens_per_row=0,
    aggregation_budget_model_calls=1,
)

ORCHESTRATOR_MAX_ITERS = 6


class ActiveRateFactListerSignature(dspy.Signature):
    """List current frequency-bearing seizure facts (count, range, period)
    found in the letter, per seizure type. Do not decide final attributes
    or emit a mentions list; list evidence only."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON prompt payload with task instructions and letter text."
    )
    active_rate_facts_json: str = dspy.OutputField(
        desc=(
            'Strict JSON object: {"facts": [{"seizure_type": str, '
            '"evidence": str, "rate_text": str}]}. No "mentions" field, no '
            "final attributes."
        )
    )


class SeizureFreeHazardListerSignature(dspy.Signature):
    """List seizure-free, historical, negated, or superseded seizure-
    frequency evidence found in the letter. Do not decide final attributes
    or emit a mentions list; list evidence only."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON prompt payload with task instructions and letter text."
    )
    seizure_free_hazards_json: str = dspy.OutputField(
        desc=(
            'Strict JSON object: {"hazards": [{"seizure_type": str|null, '
            '"evidence": str, "hazard_kind": "seizure_free"|"historical"|'
            '"negated"|"superseded"}]}. No "mentions" field.'
        )
    )


class ClusterOrChangeListerSignature(dspy.Signature):
    """List cluster cadence / events-per-cluster evidence AND frequency-
    CHANGE evidence (increased, decreased, same) found in the letter. Do
    not decide final attributes or emit a mentions list; list evidence
    only."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON prompt payload with task instructions and letter text."
    )
    cluster_or_change_json: str = dspy.OutputField(
        desc=(
            'Strict JSON object: {"entries": [{"seizure_type": str|null, '
            '"evidence": str, "kind": "cluster"|"frequency_change", '
            '"detail": str}]}. No "mentions" field.'
        )
    )


class SFResolverSignature(dspy.Signature):
    """Given the letter and three specialists' evidence listings, produce
    the final SeizureFrequency mentions list (same schema the standard
    single-pass extractor uses: text, attributes, evidence, confidence,
    rationale per mention). Cite in each mention's rationale which
    specialist evidence informed it, and explicitly note in rationale when
    you reject a specialist's finding (e.g. a seizure-free hazard that is
    actually superseded by a more recent active-rate fact)."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON prompt payload with task instructions and letter text."
    )
    active_rate_facts_json: str = dspy.InputField(
        desc="Output from the active-rate-fact-lister specialist."
    )
    seizure_free_hazards_json: str = dspy.InputField(
        desc="Output from the seizure-free-hazard-lister specialist."
    )
    cluster_or_change_json: str = dspy.InputField(
        desc="Output from the cluster-or-change-lister specialist."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            'Strict JSON object: {"mentions": [{"text": ..., '
            '"attributes": {...}, "evidence": ..., "confidence": ..., '
            '"rationale": ..., "cited_specialists": [...]}]}. Same schema '
            "as the standard extractor plus cited_specialists per mention."
        )
    )


def run_d3_static(prompt_input_json: str) -> dict[str, Any]:
    """Always run all three specialists, then the resolver. 4 model calls."""
    active_rate = dspy.Predict(ActiveRateFactListerSignature)(
        prompt_input_json=prompt_input_json
    )
    seizure_free = dspy.Predict(SeizureFreeHazardListerSignature)(
        prompt_input_json=prompt_input_json
    )
    cluster_change = dspy.Predict(ClusterOrChangeListerSignature)(
        prompt_input_json=prompt_input_json
    )
    resolver = dspy.Predict(SFResolverSignature)(
        prompt_input_json=prompt_input_json,
        active_rate_facts_json=str(active_rate.active_rate_facts_json),
        seizure_free_hazards_json=str(seizure_free.seizure_free_hazards_json),
        cluster_or_change_json=str(cluster_change.cluster_or_change_json),
    )
    return {
        "active_rate_facts_json": str(active_rate.active_rate_facts_json),
        "seizure_free_hazards_json": str(seizure_free.seizure_free_hazards_json),
        "cluster_or_change_json": str(cluster_change.cluster_or_change_json),
        "extraction_json": str(resolver.extraction_json),
        "specialists_run": [
            "active_rate_fact_lister",
            "seizure_free_hazard_lister",
            "cluster_or_change_lister",
        ],
    }


def _bound_specialist_tool(
    prompt_input_json: str,
    *,
    name: str,
    signature: type[dspy.Signature],
    output_field: str,
) -> Any:
    def specialist_tool() -> dict[str, Any]:
        prediction = dspy.Predict(signature)(prompt_input_json=prompt_input_json)
        raw = str(getattr(prediction, output_field))
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"raw": raw, "parse_error": True}

    specialist_tool.__name__ = name
    specialist_tool.__doc__ = signature.__doc__
    return specialist_tool


def build_dynamic_orchestrator_agent(prompt_input_json: str, note_text: str) -> dspy.ReAct:
    """Build a fresh, row-scoped orchestrator whose tools are the three
    specialists (each an LM call when invoked, never a mentions list) plus
    the existing deterministic evidence-check/boundary-guide tools. The
    orchestrator decides which to consult, then resolves to the final
    SeizureFrequency mentions list itself.
    """
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.agentic.tools import (
        bound_evidence_check_tool,
        read_sf_boundary_guide,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
        ExECTv2SinglePassSFSignature,
    )

    tools = [
        _bound_specialist_tool(
            prompt_input_json,
            name="active_rate_fact_lister",
            signature=ActiveRateFactListerSignature,
            output_field="active_rate_facts_json",
        ),
        _bound_specialist_tool(
            prompt_input_json,
            name="seizure_free_hazard_lister",
            signature=SeizureFreeHazardListerSignature,
            output_field="seizure_free_hazards_json",
        ),
        _bound_specialist_tool(
            prompt_input_json,
            name="cluster_or_change_lister",
            signature=ClusterOrChangeListerSignature,
            output_field="cluster_or_change_json",
        ),
        bound_evidence_check_tool(note_text),
        read_sf_boundary_guide,
    ]
    return dspy.ReAct(
        ExECTv2SinglePassSFSignature,
        tools=tools,
        max_iters=ORCHESTRATOR_MAX_ITERS,
    )


def run_dynamic_orchestrator_row(prompt_input_json: str, *, note_text: str) -> dspy.Prediction:
    agent = build_dynamic_orchestrator_agent(prompt_input_json, note_text)
    return agent(prompt_input_json=prompt_input_json)
