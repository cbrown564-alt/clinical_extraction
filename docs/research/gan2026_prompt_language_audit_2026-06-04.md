# Gan 2026 Prompt Language Audit

Date: 2026-06-04

Status: prompt-language catalogue and remediation plan. This document audits
model-facing prompt text, schema text, and DSPy task instructions for clarity,
minimalism, and jargon leakage. It does not change experiment scores or make
new benchmark claims.

## Standard

Model-facing prompts should be clear, precise, plain-language instructions with
enough information to complete the task effectively, and no more.

Examples-heavy or instruction-heavy prompts are allowed only when the experiment
is explicitly testing that prompt shape. Otherwise, default to minimal prompts,
plain field names, short field descriptions, and visible separation between
model-facing instructions and research metadata.

## Audit Method

Searched prompt-bearing Python surfaces for prompt builders, DSPy signatures,
task instructions, schema text, and rendered-payload fields. The audit focused
on source code under `src/clinical_extraction/tasks/seizure_frequency/gan2026`
and tests that assert prompt text.

Search terms included: `build_prompt_input`, `build_*prompt`,
`task_instructions`, `instructions`, `prompt_input_json`, `Signature`,
`source-near`, `operands`, `proxy`, `denominator`, `final_label`,
`prompt_version`, `pipeline_family`, `Gan 2026`, `component`,
`selector_decision`, `cluster_axis`, `boundary_state`, and `schema`.

## Cross-Cutting Findings

1. Internal metadata leaks into model-facing payloads.

Several prompts include `prompt_version`, `pipeline_family`, `Gan 2026`, run
family names, component roles, or experiment labels beside the actual task. This
is useful for artifacts but usually irrelevant to the model.

2. Internal terms are treated as if they were natural language.

Recurring examples include `source-near`, `operands`, `denominator`, `proxy`,
`boundary_state`, `cluster_axis`, `selector_decision`, `raw_llm_final_label`,
and `prediction-bearing`. Some are acceptable as parser-facing field names, but
they need plain descriptions or cleaner names when exposed to the model.

3. Prompts often overfit by accumulating prohibitions.

The claim-table and LLM-heavy prompts contain many narrow "do not" rules. Some
are justified by known failure families, but the result is hard to distinguish
from prompt overload without a predeclared reason for each block.

4. Schema text and instructions blur together.

Some prompts use schema dictionaries as both parser contracts and model
instructions. Others strip or omit field descriptions, leaving ambiguous field
names to do too much work.

5. Tests sometimes preserve bad prompt language.

Several tests assert exact internal wording such as `source-near`,
`prompt_version`, `pipeline_family`, or prompt-policy phrasing. Those tests
should shift toward rendered-payload discipline: no gold labels, no internal
metadata in model-facing sections, clear schema descriptions, and expected task
coverage.

## Catalogue

| Surface | Prompt role | Main issues | Severity | Recommended action |
| --- | --- | --- | --- | --- |
| `llm/llm_only_direct_labeler.py` | Direct note-to-label extraction | Model sees `Gan 2026`, `prompt_version`, `final_label`, `denominator`; docstring mentions prompt/gold | Medium | Keep as historical baseline unless rerun; if reused, separate metadata and rename model-facing fields/descriptions. |
| `llm/llm_only_minimal_evidence_selector.py` | Minimal evidence selector | Uses `source-near`, `final_query`, `non_seizure_or_proxy`, `proxy-only`; schema is string-description based | High | Next remediation target because it is intended to be minimal but still carries jargon. |
| `llm/llm_only_structured_events.py` | Event extraction plus selection | Uses `source-near`, `final_label`, `Gan 2026`; mixes extraction and selection instructions | High | Rewrite if reused for single-task controls; split extraction from selection or justify combined task. |
| `llm/llm_only_claim_table_selector.py` | Claim table plus final selector | Very instruction-heavy; includes `source-near`, `selector_decision`, `cluster_axis`, `boundary_state`, `final_label`, `denominator`, `proxy`; many narrow rules | High | Treat as controlled-experiment prompt only. Do not use as default style. Build a smaller successor with typed schema descriptions. |
| `llm/llm_heavy_clinical_frequency_reasoner.py` | Multi-stage extraction/selection/rendering | Uses stages, "model owns", `operands`, `raw_llm_final_label`, `denominator`, schema-rendering terms | High | Preserve as historical LLM-heavy condition; do not add more rules without a predeclared claim. |
| `llm/llm_heavy_evidence_selection_with_deterministic_adapters.py` | Evidence selection with adapter-visible typed fields | Uses adapter/benchmark/operand language and internal typed-output metadata | High | Audit before any new calls; distinguish model-facing clinical task from adapter metadata. |
| `llm/llm_only_typed_adapter_reasoner.py` | Typed DSPy extraction/rendering | Uses `source-near`, `raw_llm_final_label`, rendering operands, opaque JSON phrasing, metadata in output contract | Medium | Keep typed contract, but rewrite task instructions and hide metadata from model-facing input where possible. |
| `llm/llm_only_typed_operations_reasoner.py` | Typed operation extraction | Uses `source-near`, `operations`, `operands`, `denominators`, internal output contract fields | Medium | Rename/descriptively define operation components before reuse; avoid teaching parser vocabulary as task vocabulary. |
| `llm/llm_only_sparse_operands_selected_state_reasoner.py` | One selected state with sparse components | Uses `source-near`, `operands`, `raw_llm_final_label`, `proxy-only`, `uncertainty_flags` | Medium | Good candidate for cleanup because task is narrow; replace jargon with field descriptions. |
| `llm/llm_only_simplified_selected_state_reasoner.py` | Simplified selected state | Similar selected-state jargon plus metadata in output contract | Medium | Apply same selected-state cleanup as sparse operands surface. |
| `hybrid/hybrid_parallel_state_candidate_reasoner.py` | Independent candidate selector plus adjudicator | Exposes `Gan 2026`, `pipeline_family`, `source-near`, deterministic/state graph/LLM source labels, `final_label` | High | Split model-facing task from provenance metadata; avoid asking the model to reason over internal source classes unless the experiment tests adjudication. |
| `hybrid/hybrid_rules_candidates_llm_adjudicator.py` | Final adjudication over candidates | Uses benchmark-facing and proxy language; asks model to adjudicate internal candidate/provenance structures | High | Treat as controlled hybrid experiment. Add model-facing definitions for any candidate-source fields. |
| `experiments/boundary_state_graph_builder.py` | Boundary-state graph node builder | Exposes `component_role`, `pipeline_family`, graph/node language, `final_label` guard | Medium | Keep graph terms only if the model is truly building graph nodes; otherwise translate to "facts" and keep graph metadata outside. |
| `experiments/single_task_control_prompts.py` | Candidate, evidence, and projection controls | Recently remediated; still intentionally has parser-facing condition names in code constants, not model-facing payload | Low | Use as the current style reference for rendered-payload separation and field descriptions. |
| `experiments/run_single_task_controls.py` | Runner for single-task prompts | Uses generic prompt input/output wrapper | Low | Ensure it records prompt versions in artifacts without injecting them into rendered prompt text. |
| `experiments/prompt_devset.py` | Builds prompt-development examples | Not a live model prompt, but names `final_selection_adjudication` and deterministic diagnostics | Low | Keep as development artifact; avoid reusing example text as model instructions without cleanup. |
| `artifact_analysis/*matrix.py`, `component_projection_panel.py`, `llm_component_mechanics.py`, `rq*_control_panels.py` | Analysis artifacts and synthetic control rows | Mostly artifact labels, not direct prompts; may contain predeclared prompt names | Low | Do not treat these as model-facing unless their rows are later embedded in a prompt. |
| Tests under `tests/test_gan2026_*llm*.py` | Prompt contract tests | Assert specific prompt text including internal terms and metadata | Medium | Convert to rendered-payload quality tests and allow wording changes that improve prompt clarity. |

## Immediate Remediation Order

1. Keep `single_task_control_prompts.py` as the style baseline.
2. Add prompt-discipline tests for rendered payloads:
   - no `source-near`, `operands`, `proxy`, `denominator`, `prompt_version`,
     `pipeline_family`, `Gan 2026`, `benchmark`, or `component` in model-facing
     sections unless explicitly justified;
   - non-obvious schema fields have descriptions;
   - metadata appears in artifacts, not model-facing instructions.
3. Rewrite `llm_only_minimal_evidence_selector.py`, because its purpose is
   minimalism but it still contains several persistent jargon failures.
4. Audit selected-state surfaces next:
   `llm_only_sparse_operands_selected_state_reasoner.py`,
   `llm_only_simplified_selected_state_reasoner.py`,
   `llm_only_typed_adapter_reasoner.py`, and
   `llm_only_typed_operations_reasoner.py`.
5. Treat claim-table and LLM-heavy prompts as controlled historical prompt
   families. Do not extend them without a stated experiment claim and explicit
   prompt-length justification.

## Follow-Up Remediation

Completed on 2026-06-04:

- Rewrote `llm/llm_only_minimal_evidence_selector.py` model-facing payload to
  remove prompt/run metadata from the rendered prompt. `prompt_version` remains
  in run rows and metadata, not in the model-facing JSON.
- Replaced model-facing `Gan 2026`, `source-near`, and `proxy` language with
  plain task wording and short schema descriptions.
- Renamed the model-facing answer-state enum from `non_seizure_or_proxy` to
  `not_seizure_frequency`, while retaining parser repair for old saved outputs
  that still use the previous value.
- Updated the focused minimal-selector prompt test to assert rendered-payload
  discipline and added a compatibility test for the old state alias.
- Verified the rendered minimal-selector prompt against the audit terms:
  `source-near`, `operands`, `proxy`, `denominator`, `prompt_version`,
  `pipeline_family`, `Gan 2026`, `benchmark`, and `component`.

Validation:

- `python -m pytest tests/test_gan2026_llm_only_minimal_evidence_selector.py`
- `python -m pytest tests/test_gan2026_llm_prompt_hygiene.py`

## New Preventive Control

Created personal Codex skill:
`/Users/cobro/.codex/skills/plain-language-prompt-auditor/SKILL.md`.

Use it whenever creating, editing, reviewing, or auditing:

- LLM prompts;
- prompt payload builders;
- DSPy signatures and task inputs;
- model-facing schema names and descriptions;
- tests that assert prompt content.

Acceptance checklist from the skill:

- rendered prompt inspected;
- model-facing text is plain language;
- internal metadata is separated from model-facing text;
- non-obvious schema fields have descriptions;
- jargon terms are removed or defined;
- prompt length matches the experiment's purpose;
- controlled-experiment deviations are explicitly justified.
