# Gan 2026 Agentic Pipeline Phase Plan

Date: 2026-06-12

Status: Phase 5 contracts implemented; Phase 6 prompt-only runner surface implemented.
Live Phase 6 prediction-bearing comparisons are next. This plan supersedes the
previous assumption that Gan 2026 should close immediately after the
`hybrid_structured_events` close-off report. It does not authorize new holdout
use, test-row inspection, or benchmark-facing claims.

Phase 5 implementation note: the tested contract surface lives in
`docs/design/gan2026_agentic_phase5_contracts.md`,
`src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/`, and
`tests/test_gan2026_agentic_phase5_contracts.py`.

Phase 6 implementation note: the first shared runner surface is
`agentic_matched_budget` on the existing `gan2026-llm-experiment` CLI. The
validation25 prompt-only/no-call smoke artifact is
`experiments/gan2026_agentic_matched_budget_validation25_prompt_only_2026-06-12.md`;
it records matched budgets, planned model calls, parser/guide tool traces, and
`no_prediction` attribution for all five initial conditions.

## Decision

Gan 2026 has two remaining paper-relevant phases before ExECTv2 becomes the
primary workstream again:

1. **Phase 5 - agent concept and matched-budget protocol.** Define what this
   repo means by an agent, select a minimal agent implementation pattern, and
   predeclare matched-budget comparison conditions.
2. **Phase 6 - tool-using single-agent versus multi-agent evaluation.** Compare
   single-agent self-consistency, tool-using single-agent extraction, and
   multi-agent pipelines under the same model-call, token, tool-call, and
   aggregation budget.

The starting hypothesis is that a smaller prompt plus dynamic tool use may
generalize better than a large prompt that preloads many boundary-case
instructions. This is especially relevant for Gan 2026 because prior prompt
iterations improved some hard cases while increasing over-fire risk on easy
cases.

## Working Definitions

For this project, a **non-agentic LLM pipeline** is a fixed model call or fixed
sequence of calls where application code decides when every component runs.

An **augmented LLM** is a model call with access to tools, retrieval, memory, or
structured output, but still inside a mostly fixed application path.

A **single agent** is one LLM-owned decision loop with instructions, state,
structured output, and optional tools. The model may decide whether to call a
tool and which tool output to use before emitting the prediction-bearing
clinical interpretation.

A **multi-agent pipeline** is more than one specialist LLM role, with explicit
handoff or conversation structure. The research claim is not "more calls are
better"; the claim must be tested against a single-agent condition with the same
budget.

Sources used for this framing:

- OpenAI Agents SDK docs define agents as applications that plan, call tools,
  collaborate across specialists, and keep enough state for multi-step work:
  https://developers.openai.com/api/docs/guides/agents
- OpenAI tools docs frame tool use as built-in tools, function calling, tool
  search, and remote MCP servers that extend model responses and agents:
  https://developers.openai.com/api/docs/guides/tools
- Anthropic's agent guidance distinguishes workflows, where code orchestrates
  fixed paths, from agents, where the LLM dynamically directs process and tool
  use: https://www.anthropic.com/engineering/building-effective-agents
- Anthropic's tool-design guidance emphasizes choosing the right tools,
  namespacing, returning meaningful context, token-efficient tool outputs, and
  evaluating whether agents can use the tools effectively:
  https://www.anthropic.com/engineering/writing-tools-for-agents
- Self-consistency samples multiple reasoning paths and selects the most
  consistent answer; here it becomes the matched-budget single-agent comparator:
  https://arxiv.org/abs/2203.11171
- ReAct motivates interleaving reasoning and actions so models can retrieve or
  compute information while solving a task:
  https://arxiv.org/abs/2210.03629

## Research Questions

1. Does single-agent self-consistency improve Gan 2026 seizure-frequency
   extraction over one deterministic-temperature `hybrid_structured_events`
   pass when the prompt is held constant?
2. Does cross-model self-consistency using the same prompt across GPT, DeepSeek,
   and Qwen produce a more robust answer than same-model temperature diversity?
3. Does giving the single agent callable tools reduce boundary-case over-fire
   compared with cramming all boundary instructions into the initial prompt?
4. Does a multi-agent pipeline add value beyond a matched-budget single-agent
   ensemble, or does it mostly spend extra calls to reproduce the same signal?
5. Which component owns the final clinical interpretation: raw model selection,
   tool-returned candidates, deterministic normalization, or an adjudicator?

## Matched-Budget Conditions

Every comparison must report:

- model calls per row;
- model identifiers and temperatures;
- prompt version and prompt token budget;
- maximum completion tokens per call;
- maximum tool calls per row;
- maximum tool-output tokens returned to the model;
- aggregation method and whether aggregation is deterministic or LLM-mediated;
- wall-clock time, call failures, parse failures, and retry policy.

Initial conditions:

| Condition | Purpose | Budget rule |
| --- | --- | --- |
| `single_greedy` | Current-style baseline | 1 model call, no optional tools |
| `single_self_consistency_temperature` | Same model, same prompt, varied decoding | N calls; deterministic vote or one budget-matched adjudication call |
| `single_self_consistency_cross_model` | Same prompt across GPT, DeepSeek, Qwen | One call per model; deterministic vote or one budget-matched adjudication call |
| `single_agent_tools` | One agent dynamically chooses tools | Same total model-call cap as the self-consistency condition; bounded tool calls |
| `multi_agent_matched` | Specialist agents plus coordinator | Same total model-call cap as the selected single-agent comparator |

Aggregation should start with deterministic normalized-label voting. If an LLM
adjudicator is used, the single-agent comparator and multi-agent condition must
receive the same adjudication budget.

## Tool Categories

### Tool A - Regex Parser Tool

Give the model a callable deterministic parser instead of applying the parser
automatically as post-processing.

Tool contract:

- Input: source note text or a bounded excerpt selected by the agent.
- Output: source-near candidate events, evidence spans, parser rule IDs, rule
  portability categories, and parse warnings.
- The tool must not return gold labels, split metadata, row IDs, or scoring
  hints.
- The model owns whether to call the parser and which returned candidates
  support the final answer.

Attribution:

- Candidate discovery may be deterministic-tool-owned.
- Final clinical selection is model-owned only if the model explicitly selects
  among candidates or rejects them with evidence.
- Normalization and Gan label rendering remain deterministic and must be
  reported separately from clinical selection.

### Tool B - Boundary Guide Reader

Give the model a bounded retrieval/file-reader tool over curated guidance
documents for boundary cases, rather than placing every boundary rule in the
initial prompt.

Initial guide set:

- multiple current seizure events and aggregation;
- seizure-free period plus seizure event conflict;
- cluster frequency versus incidental clustering;
- last-event-only versus recurring rate;
- unknown frequency versus no seizure-frequency reference;
- current versus historical window selection;
- multiple semiologies with different burdens.

Tool contract:

- The agent requests a guide by scenario name or short trigger description.
- The tool returns a compact, versioned excerpt with examples and decision
  criteria.
- Guide documents must be split-neutral and must not contain validation or test
  row answers.
- Tool responses should be short enough to make dynamic retrieval cheaper than
  prompt stuffing.

## Implementation Best Practices

Start simple. The first implementation should be a transparent while-loop or
repo-native runner around existing model-call wrappers, not a new framework
unless the framework materially improves tracing, handoffs, or tool execution.

Keep tools ergonomic for models:

- specific names, such as `parse_seizure_frequency_candidates` and
  `read_boundary_guide`;
- small schemas with required fields;
- explicit error and no-result cases;
- short, structured outputs optimized for downstream model use;
- tests that show the tool output is useful without overexposing internals.

Record traces as first-class artifacts:

- per-row tool calls requested;
- tool inputs and outputs;
- final selected evidence;
- ensemble votes or handoff decisions;
- final normalized label;
- attribution layer: raw model, tool-assisted model, adjudicator, or
  deterministic normalization.

## Evaluation Protocol

Development defaults to `gan2026_split_v1` validation. Because Gan validation is
already high-performing and has shown validation-to-test drift, broad
validation250 aggregates are not the first choice.

Recommended ladder:

1. Contract smoke: validation25, focused on tool-call schema, parse failures,
   trace completeness, and obvious over-fire.
2. Mechanism panels: synthetic and validation hard slices for the boundary
   cases above.
3. Matched-budget validation50 or validation250 only after the hard-slice
   question is predeclared.
4. Full validation750 only for a stable paper-facing comparison.
5. Locked test450 only after candidate, budget, prompts, tools, aggregation,
   scorer, and inspection policy are frozen and explicitly authorized.

Report at least:

- Purist and Pragmatic correctness of rendered rows;
- rendered/null/parse-failure rows;
- evidence-validity rate, using architecture-specific definitions;
- tool-call rate and tool-call usefulness;
- label vote entropy or model disagreement;
- wrong-to-correct and correct-to-wrong transitions against the promoted
  `hybrid_structured_events` comparator;
- latency and cost per row.

## Deliverables

Phase 5 is complete when:

- this plan is accepted as the controlling phase document;
- the agent definition, budget accounting, tool categories, and evaluation
  ladder are reflected in `PROJECT_STATUS.md`;
- the parser-tool and guide-reader contracts are specified enough to test.

Phase 6 is complete when:

- the repo can run the matched-budget conditions above from a single experiment
  surface;
- tool traces and ensemble decisions are saved as comparable artifacts;
- a comparison report answers whether tool-using single agents or multi-agent
  orchestration add evidence beyond matched-budget self-consistency;
- any holdout-facing claim is either explicitly deferred or run under a fresh
  frozen protocol with user authorization.

## Guardrails

- Do not inspect Gan test-row failures while designing tools, guides, prompts,
  or aggregation.
- Do not treat parser tool output as LLM-owned clinical discovery.
- Do not let file retrieval leak gold labels, row IDs, split membership, or
  validation/test-specific fixes.
- Do not compare multi-agent pipelines against a weaker single-agent baseline
  with fewer calls or less context.
- Do not report tool-assisted success as fully LLM-only.
- Do not add broad boundary-case instructions to the main prompt without also
  preserving the smaller prompt plus dynamic-retrieval condition.
