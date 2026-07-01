"""Genuine LM-decided tool-use single agent for ExECTv2 SeizureFrequency
(`dspy.ReAct`). Ports the Gan 2026 fix (see
`tasks.seizure_frequency.gan2026.agentic.react_single_agent`) to ExECTv2:
the model itself chooses whether/when to call
`check_evidence_in_letter`/`read_sf_boundary_guide`, stopping on its own
`finish`, rather than a scripted tool sequence.
"""
from __future__ import annotations

import dspy

from clinical_extraction.core.agentic_contracts import AgentBudget
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.agentic.tools import (
    bound_evidence_check_tool,
    read_sf_boundary_guide,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    ExECTv2SinglePassSFSignature,
)

CONDITION_NAME = "single_agent_tools_react"
PROMPT_VERSION = "exectv2_sf_react_single_agent_v0_1"

# Same shape as the Gan 2026 redo: 3 ReAct turns + dspy.ReAct's own 1
# final-extraction call = 4 model calls, up to 2 tool calls per turn.
REACT_MAX_ITERS = 3
BUDGET = AgentBudget(
    model_calls_per_row=4,
    prompt_token_budget=3_000,
    max_completion_tokens_per_call=800,
    max_tool_calls_per_row=3,
    max_tool_output_tokens_per_row=700,
    aggregation_budget_model_calls=1,
)


def build_react_agent(note_text: str) -> dspy.ReAct:
    """Build a fresh, row-scoped ReAct agent (evidence tool bound to this
    letter; boundary-guide tool is static, no binding needed)."""
    return dspy.ReAct(
        ExECTv2SinglePassSFSignature,
        tools=[bound_evidence_check_tool(note_text), read_sf_boundary_guide],
        max_iters=REACT_MAX_ITERS,
    )


def run_single_row(prompt_input_json: str, *, note_text: str) -> dspy.Prediction:
    """Run the genuine tool-using agent for one letter. `prompt_input_json`
    should be built the same way as `single_greedy`
    (`llm_only_single_pass.build_prompt_input`), so only the tool-use
    mechanism differs. Returns `.extraction_json` (parseable the same way
    as `single_greedy`'s output) and `.trajectory`."""
    agent = build_react_agent(note_text)
    return agent(prompt_input_json=prompt_input_json)
