"""Angle 2 (ceiling) multi-agent architectures for Gan 2026.

Two candidates, per `docs/experiments/gan2026/agentic/gan2026_agentic_redo_predeclaration_2026-07-01.md`:

- `multi_agent_d3_static`: resurrects the project's own never-run D3 design
  (2026-06-12) — three bounded specialist roles, always all run, feeding a
  resolver. Specialists emit typed evidence only; the DSPy output schema
  has no `final_label`/`answer_kind` field, so they structurally cannot
  emit a final answer, unlike 06-12's `multi_agent_matched` (four identical
  final-labelers wearing role costumes).
- `multi_agent_dynamic_orchestrator`: the same three specialists wrapped as
  callable tools (each makes its own LM call when invoked and returns
  evidence, never a label), given to a `dspy.ReAct` orchestrator that
  decides which to consult based on the letter, then resolves itself.
"""
from __future__ import annotations

import json
from typing import Any

import dspy

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.contracts import (
    AgentBudget,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.tools import (
    parse_seizure_frequency_candidates,
    read_boundary_guide,
)

CONDITION_D3_STATIC = "multi_agent_d3_static"
CONDITION_DYNAMIC_ORCHESTRATOR = "multi_agent_dynamic_orchestrator"
PROMPT_VERSION = "gan2026_multi_agent_ceiling_v0_1"

# D3-static: 3 specialist calls + 1 resolver call, always run. Not
# budget-matched to Angle 1 (Angle 2 is explicitly exploratory), but capped
# and reported per predeclaration.
D3_STATIC_BUDGET = AgentBudget(
    model_calls_per_row=4,
    prompt_token_budget=3_500,
    max_completion_tokens_per_call=600,
    max_tool_calls_per_row=0,
    max_tool_output_tokens_per_row=0,
    aggregation_budget_model_calls=1,
)

# Dynamic orchestrator: up to 6 ReAct turns (each may trigger 0-1 specialist
# LM call) + 1 final extraction call = worst case ~13 model calls; actual
# per-row cost is measured and reported, not assumed.
ORCHESTRATOR_MAX_ITERS = 6


class FrequencyFactListerSignature(dspy.Signature):
    """List current frequency-bearing seizure facts and active semiologies
    found in the letter. Do not decide a final seizure-frequency label or
    answer kind; list evidence only."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON prompt payload with task instructions and note text."
    )
    frequency_facts_json: str = dspy.OutputField(
        desc=(
            'Strict JSON object: {"facts": [{"evidence": str, '
            '"seizure_type": str|null, "rate_text": str|null, '
            '"time_window": str|null}]}. No final_label or answer_kind field.'
        )
    )


class BoundaryHazardListerSignature(dspy.Signature):
    """List seizure-free, unknown-frequency, no-reference, negation, and
    historical-hazard evidence found in the letter. Do not decide a final
    seizure-frequency label or answer kind; list evidence only."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON prompt payload with task instructions and note text."
    )
    boundary_hazards_json: str = dspy.OutputField(
        desc=(
            'Strict JSON object: {"hazards": [{"evidence": str, '
            '"hazard_kind": "seizure_free"|"unknown"|"no_reference"|'
            '"negation"|"historical"}]}. No final_label or answer_kind field.'
        )
    )


class ClusterBurdenListerSignature(dspy.Signature):
    """List cluster cadence and events-per-cluster evidence found in the
    letter, and whether cluster burden would change the final label. Do
    not decide a final seizure-frequency label or answer kind; list
    evidence only."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON prompt payload with task instructions and note text."
    )
    cluster_burden_json: str = dspy.OutputField(
        desc=(
            'Strict JSON object: {"cluster_evidence": [{"evidence": str, '
            '"cluster_cadence": str|null, "events_per_cluster": str|null}], '
            '"changes_final_label": bool}. No final_label or answer_kind field.'
        )
    )


class ResolverSignature(dspy.Signature):
    """Given the letter and three specialists' evidence listings, choose
    exactly one final seizure-frequency label. Cite which specialist
    evidence informed the decision, and explicitly reject any lower-burden
    or boundary alternative you did not choose."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON prompt payload with task instructions and note text."
    )
    frequency_facts_json: str = dspy.InputField(
        desc="Output from the frequency-fact-lister specialist."
    )
    boundary_hazards_json: str = dspy.InputField(
        desc="Output from the boundary-hazard-lister specialist."
    )
    cluster_burden_json: str = dspy.InputField(
        desc="Output from the cluster-burden-lister specialist."
    )
    decision_json: str = dspy.OutputField(
        desc=(
            "Strict JSON object with final_label, evidence, answer_kind, "
            "selected_seizure_type, time_window, confidence, rationale, "
            "cited_specialists (list of specialist names whose evidence "
            "informed the decision), and rejected_alternatives (list of "
            "alternative labels considered and why each was rejected)."
        )
    )


def run_d3_static(prompt_input_json: str) -> dict[str, Any]:
    """Always run all three specialists, then the resolver. 4 model calls."""
    frequency = dspy.Predict(FrequencyFactListerSignature)(
        prompt_input_json=prompt_input_json
    )
    boundary = dspy.Predict(BoundaryHazardListerSignature)(
        prompt_input_json=prompt_input_json
    )
    cluster = dspy.Predict(ClusterBurdenListerSignature)(
        prompt_input_json=prompt_input_json
    )
    resolver = dspy.Predict(ResolverSignature)(
        prompt_input_json=prompt_input_json,
        frequency_facts_json=str(frequency.frequency_facts_json),
        boundary_hazards_json=str(boundary.boundary_hazards_json),
        cluster_burden_json=str(cluster.cluster_burden_json),
    )
    return {
        "frequency_facts_json": str(frequency.frequency_facts_json),
        "boundary_hazards_json": str(boundary.boundary_hazards_json),
        "cluster_burden_json": str(cluster.cluster_burden_json),
        "decision_json": str(resolver.decision_json),
        "specialists_run": [
            "frequency_fact_lister",
            "boundary_hazard_lister",
            "cluster_burden_lister",
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
    specialists (each an LM call when invoked, never a label) plus the
    existing deterministic parser/boundary-guide tools. The orchestrator
    decides which to consult, then resolves to a final label itself.
    """
    from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.react_single_agent import (
        bound_parser_tool,
        read_boundary_guide_tool,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.runner import (
        AgenticDecisionSignature,
    )

    tools = [
        _bound_specialist_tool(
            prompt_input_json,
            name="frequency_fact_lister",
            signature=FrequencyFactListerSignature,
            output_field="frequency_facts_json",
        ),
        _bound_specialist_tool(
            prompt_input_json,
            name="boundary_hazard_lister",
            signature=BoundaryHazardListerSignature,
            output_field="boundary_hazards_json",
        ),
        _bound_specialist_tool(
            prompt_input_json,
            name="cluster_burden_lister",
            signature=ClusterBurdenListerSignature,
            output_field="cluster_burden_json",
        ),
        bound_parser_tool(note_text),
        read_boundary_guide_tool,
    ]
    return dspy.ReAct(
        AgenticDecisionSignature,
        tools=tools,
        max_iters=ORCHESTRATOR_MAX_ITERS,
    )


def run_dynamic_orchestrator_row(prompt_input_json: str, *, note_text: str) -> dspy.Prediction:
    agent = build_dynamic_orchestrator_agent(prompt_input_json, note_text)
    return agent(prompt_input_json=prompt_input_json)
