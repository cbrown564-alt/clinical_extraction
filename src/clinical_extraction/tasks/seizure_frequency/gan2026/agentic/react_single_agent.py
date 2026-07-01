"""Genuine LM-decided tool-use single agent for Gan 2026 (`dspy.ReAct`).

Fixes the 2026-06-12 `single_agent_tools` condition's core flaw: that
version hard-coded exactly which tools ran, in Python, for every row
(`runner.py::_tool_calls`), so the model never actually decided whether or
when to call a tool. This module uses `dspy.ReAct`, where the model itself
chooses `next_tool_name`/`next_tool_args` each turn and stops on its own
`finish`. See `docs/plans/proud-bubbling-ocean.md` (Phase 0/1) and
`docs/experiments/gan2026/agentic/` for the predeclaration this condition
answers to.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

import dspy

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.contracts import (
    AgentBudget,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.runner import (
    AgenticDecisionSignature,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.tools import (
    parse_seizure_frequency_candidates,
    read_boundary_guide,
)

CONDITION_NAME = "single_agent_tools_react"
PROMPT_VERSION = "gan2026_react_single_agent_v0_1"

# Matches the 2026-06-12 matched-budget shape exactly (4 model calls, 3 tool
# calls) so hard50 results stay directly comparable to that run: max_iters=3
# ReAct turns (each 1 model call) plus dspy.ReAct's own final-extraction
# call = 4 model calls total. See dspy/predict/react.py: ReAct.forward()
# always issues one extra `self.extract` call after the loop ends.
REACT_MAX_ITERS = 3
BUDGET = AgentBudget(
    model_calls_per_row=4,
    prompt_token_budget=2_500,
    max_completion_tokens_per_call=600,
    max_tool_calls_per_row=3,
    max_tool_output_tokens_per_row=700,
    aggregation_budget_model_calls=1,
)


def bound_parser_tool(note_text: str) -> Callable[[], dict[str, Any]]:
    """Build a parser tool bound to one letter's text.

    The tool takes no arguments (the letter is already fixed for this row)
    rather than requiring the model to retransmit the full note text as a
    `next_tool_args` value, which would be expensive and risks transcription
    drift on a several-paragraph clinical letter.
    """

    def parse_seizure_frequency_candidates_in_this_letter() -> dict[str, Any]:
        """Return source-near seizure-frequency candidates already found in
        the current letter (parser output, not a clinical decision)."""
        return parse_seizure_frequency_candidates(note_text).model_dump()

    return parse_seizure_frequency_candidates_in_this_letter


def read_boundary_guide_tool(query: str) -> dict[str, Any]:
    """Look up a compact, split-neutral clinical boundary decision guide by
    ID, title, or trigger phrase (e.g. "cluster frequency", "seizure free
    conflict"). Raises if the query does not match a known guide; retry
    with a different query or stop using this tool."""
    return read_boundary_guide(query).model_dump()


def build_react_agent(note_text: str) -> dspy.ReAct:
    """Build a fresh, row-scoped ReAct agent with tools bound to one letter.

    A new agent per row (rather than one shared instance) keeps tool state
    isolated between rows and matches `AgenticDecisionSignature`'s existing
    single-row `prompt_input_json -> decision_json` contract used by the
    other conditions in `runner.py`, so scoring/parsing stays identical.
    """
    return dspy.ReAct(
        AgenticDecisionSignature,
        tools=[bound_parser_tool(note_text), read_boundary_guide_tool],
        max_iters=REACT_MAX_ITERS,
    )


def run_single_row(prompt_input_json: str, *, note_text: str) -> dspy.Prediction:
    """Run the genuine tool-using agent for one row.

    `prompt_input_json` should be built the same way as the other
    conditions' payloads (`runner._build_prompt_input`), so the model sees
    an equivalent prompt; only the tool-use mechanism differs. Returns the
    `dspy.Prediction` with `.decision_json` (parseable the same way as the
    other conditions' raw output) and `.trajectory` (the tool-call trace,
    for auditing whether/how the model actually used its tools).
    """
    agent = build_react_agent(note_text)
    return agent(prompt_input_json=prompt_input_json)
