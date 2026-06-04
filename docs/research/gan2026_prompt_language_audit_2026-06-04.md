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

Completed selected-state follow-up on 2026-06-04:

- Added rendered-payload prompt-discipline tests for selected-state surfaces:
  model-facing instructions must not contain the audited jargon terms, prompt
  metadata keys must not appear in model-facing payloads, and listed schema
  fields must have descriptions.
- Audited and remediated:
  `llm_only_sparse_operands_selected_state_reasoner.py`,
  `llm_only_simplified_selected_state_reasoner.py`,
  `llm_only_typed_adapter_reasoner.py`, and
  `llm_only_typed_operations_reasoner.py`.
- Removed `prompt_version`, `pipeline_family`, and typed schema version metadata
  from the selected-state model inputs. These remain available through run rows
  and run metadata.
- Rewrote selected-state task instructions away from `source-near`, `proxy`,
  `scorer-facing`, and parser vocabulary where plain clinical wording was
  sufficient.
- Added field-description dictionaries for non-obvious schema fields. Stable
  parser field names were retained where downstream typed parsing depends on
  them.

Selected-state validation:

- `python -m pytest tests/test_gan2026_llm_prompt_hygiene.py tests/test_gan2026_llm_only_simplified_selected_state_reasoner.py tests/test_gan2026_llm_only_sparse_operands_selected_state_reasoner.py tests/test_gan2026_llm_only_typed_adapter_reasoner.py tests/test_gan2026_llm_only_typed_operations_reasoner.py`
- `python -m ruff check tests/test_gan2026_llm_prompt_hygiene.py tests/test_gan2026_llm_only_simplified_selected_state_reasoner.py tests/test_gan2026_llm_only_sparse_operands_selected_state_reasoner.py tests/test_gan2026_llm_only_typed_adapter_reasoner.py tests/test_gan2026_llm_only_typed_operations_reasoner.py src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_only_simplified_selected_state_reasoner.py src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_only_sparse_operands_selected_state_reasoner.py src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_only_typed_adapter_reasoner.py src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_only_typed_operations_reasoner.py`

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

## Selective Verifier Follow-Up

Completed on 2026-06-04:

- Audited the rendered model-facing payloads for the selective-verifier path
  selected for staged-hybrid integration, including:
  `verifier_model_input` and `binary_quote_highest_answer_selector`.
- Removed research and implementation terms from the older verifier model
  input: `Gan`, `selected state`, `deterministic`, and `suspicious` no longer
  appear in rendered model-facing text.
- Reworded the verifier system prompt around a plain task:
  review a proposed seizure-frequency answer using only quoted supporting text,
  review notes, and listed competing possibilities.
- Renamed model-facing payload fields from implementation terms to
  `proposed_answer`, `proposed_evidence`, and `review_notes`.
- Kept parser-facing enum values such as `render_as_selected_state` stable for
  compatibility with existing verifier output parsing, but moved their
  explanation into plain model-facing wording.
- Rewrote the promoted binary verifier prompt to talk about a proposed answer
  rather than an internal selected label, and removed `task_design` from the
  model-facing payload.
- Added rendered-payload tests so verifier model inputs cannot silently
  reintroduce research metadata or prompt-jargon terms.

Rendered-payload audit terms checked for the active verifier surfaces:
`Gan`, `benchmark`, `scorer`, `source-near`, `operands`, `denominator`,
`proxy`, `final label`, `gold`, `frozen`, `control`, `stop rule`,
`selected state`, `deterministic`, `suspicious`, `task_design`, and `delta`.
The remediated `verifier_model_input` and
`binary_quote_highest_answer_selector` payloads had no hits.

Validation:

- `python -m pytest tests/test_gan2026_selective_verifier_predeclaration.py tests/test_gan2026_selective_verifier_prompt_design_experiment.py tests/test_gan2026_selective_verifier_experiment.py`

## Assembly Inventory Follow-Up

Completed on 2026-06-04:

- Added a validation750 input inventory for staged-hybrid assembly without
  creating any new model-facing prompt surface.
- Inspected the saved validation750 reasoner replay and found historical
  prompt payloads embedded in the saved artifact rows. Those payloads are
  retained as evidence of prior runs, not accepted as prompt text for new
  component work.
- Kept the inventory report model-free and claim-bounded: it records available
  component surfaces, missing module-shaped inputs, source artifacts, and the
  next assembly action.

Acceptance checklist:

- Rendered prompt inspected: not applicable; no new prompt is rendered.
- Model-facing text is plain language: not applicable for the new inventory.
- Internal metadata is separated from model-facing text: yes; inventory
  metadata is research-facing only.
- Non-obvious schema fields have descriptions: not applicable; no model schema
  was added.
- Jargon terms are removed or defined: yes for new human-facing report text.
- Prompt length matches the experiment's purpose: not applicable.
- Controlled-experiment deviations are explicitly justified: historical saved
  prompt payloads are documented as inherited artifacts only.

## Validation750 Assembly Follow-Up

Completed on 2026-06-04:

- Added validation750 assembly adapters for the saved reasoner replay,
  safety-floor gate, and RQ9 selective-action router.
- The assembly adapters do not create a new model-facing prompt surface.
- Historical reasoner prompt payload fields such as `prompt_input_json`,
  `prompt_version`, and `pipeline_family` are omitted from the assembled JSONL.
- The assembled rows keep compact status, candidate, scoring, gate, and router
  records only.

Validation:

- `python -m pytest tests/test_gan2026_staged_hybrid_assembly.py tests/test_gan2026_component_validation_surface_inventory.py`
- `python -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/hybrid/staged_hybrid_assembly.py tests/test_gan2026_staged_hybrid_assembly.py`

## Decision Layer Follow-Up

Completed on 2026-06-04:

- Added the `staged_decision_policy` component for the explicit
  prediction-bearing decision layer over assembled validation750 rows.
- The decision layer does not create a model-facing prompt surface.
- The decision JSONL was checked for inherited prompt payload fields:
  `prompt_input_json`, `prompt_version`, `pipeline_family`, and `raw_output`.
  No hits were found.
- The policy records `verifier_used: false` on every row; the promoted verifier
  remains slice-only until a separate full-validation protocol exists.

Validation:

- `python -m pytest tests/test_gan2026_component_staged_decision_policy.py tests/test_gan2026_staged_hybrid_assembly.py`
- `python -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/components/staged_decision_policy.py src/clinical_extraction/tasks/seizure_frequency/gan2026/hybrid/staged_hybrid_assembly.py tests/test_gan2026_component_staged_decision_policy.py tests/test_gan2026_staged_hybrid_assembly.py`

## Residual Non-Prediction Audit Follow-Up

Completed on 2026-06-04:

- Added the `residual_nonprediction_audit` component for the 34
  non-prediction rows from the staged decision layer.
- The audit does not create a model-facing prompt surface.
- The audit joins decision rows to assembled component rows so blocked source
  candidate labels and development correctness remain visible without copying
  historical prompt payloads.
- The audit recommends selective abstention-pressure review before
  full-validation verifier use or promotion.

Validation:

- `python -m pytest tests/test_gan2026_component_residual_nonprediction_audit.py`
- `python -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/components/residual_nonprediction_audit.py tests/test_gan2026_component_residual_nonprediction_audit.py`

## Selective Abstention-Pressure Follow-Up

Completed on 2026-06-04:

- Added the `selective_abstention_pressure` component for a no-call review of
  the 34 residual non-prediction rows.
- The pressure review does not create a model-facing prompt surface.
- The first pass was corrected so sentinel trigger rows such as `unknown` or
  `no seizure frequency reference` are not mislabeled as direct release
  candidates.
- The pressure review recommends a predeclared gold-blinded trigger-context
  release rule and a frozen last-event date policy before behavior changes.

Validation:

- `python -m pytest tests/test_gan2026_component_selective_abstention_pressure.py`
- `python -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/components/selective_abstention_pressure.py tests/test_gan2026_component_selective_abstention_pressure.py`

## Abstention Policy Predeclaration Follow-Up

Completed on 2026-06-04:

- Added the `abstention_policy_predeclaration` component for the next
  gold-blinded abstention-pressure policy work.
- The predeclaration does not create a model-facing prompt surface and does not
  change prediction-bearing behavior.
- The emitted JSON/Markdown artifacts were checked for inherited prompt payload
  fields: `prompt_input_json`, `prompt_version`, `pipeline_family`, and
  `raw_output`. No hits were found.
- The predeclaration freezes `trigger_context_release_rule_v0` and
  `last_event_date_policy_v0` as rule-design contracts with portability
  category `seizure_frequency`.

Validation:

- `python -m pytest tests/test_gan2026_component_abstention_policy_predeclaration.py`
- `python -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/components/abstention_policy_predeclaration.py tests/test_gan2026_component_abstention_policy_predeclaration.py`

## Trigger-Context Release Follow-Up

Completed on 2026-06-04:

- Added the `trigger_context_release_rule` component for the proposed
  gold-blinded trigger-context release layer.
- The release rule does not create a model-facing prompt surface.
- The proposed decision artifacts were checked for inherited prompt payload
  fields: `prompt_input_json`, `prompt_version`, `pipeline_family`, and
  `raw_output`. No hits were found.
- The rule releases only rows that pass the predeclared lane, non-sentinel
  label, event-target evidence, rate/window evidence, exact-source, and
  non-exclusive-trigger checks.

Validation:

- `python -m pytest tests/test_gan2026_component_trigger_context_release_rule.py`
- `python -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/components/trigger_context_release_rule.py tests/test_gan2026_component_trigger_context_release_rule.py`

## Last-Event Date Instrumentation Follow-Up

Completed on 2026-06-04:

- Added the `last_event_date_instrumentation` component for the
  `date_policy_needed` residual rows.
- The component does not create a model-facing prompt surface and does not
  change prediction-bearing behavior.
- The generated artifacts classify explicit date evidence only: full date,
  partial date missing a year, or no explicit date in selected evidence.
- The component now joins source records only to extract compact
  note/reference-date anchors; it does not copy note text into generated
  artifacts.
- Automatic release-ready rows remain 0 because auditable duration derivation
  and conflict checks are not implemented yet.
- The emitted JSON/Markdown artifacts were checked for inherited prompt payload
  fields: `prompt_input_json`, `prompt_version`, `pipeline_family`, and
  `raw_output`. No hits were found.

Validation:

- `python -m pytest tests/test_gan2026_component_last_event_date_instrumentation.py tests/test_gan2026_staged_hybrid_assembly.py`
- `python -m ruff check src/clinical_extraction/tasks/seizure_frequency/gan2026/components/last_event_date_instrumentation.py tests/test_gan2026_component_last_event_date_instrumentation.py`
