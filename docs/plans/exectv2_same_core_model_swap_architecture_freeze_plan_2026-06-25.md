> **Status: HISTORICAL** — design record only. See [`ACTIVE_ROADMAP.md`](ACTIVE_ROADMAP.md) and [`recent_plan_rationalisation_2026-06-25.md`](recent_plan_rationalisation_2026-06-25.md).

# ExECTv2 Same-Core Model-Swap Architecture Freeze Plan

Date: 2026-06-25  
Scope: ExECTv2 DeepSeek, Qwen, and GPT-4.1-mini architecture alignment before final reliability-scorecard incorporation  
Protocol boundary: dev140 development comparison first; any full-200 use must be predeclared aggregate-only with no full-200 or holdout row-level failure inspection

Rationalisation status, 2026-06-25: dev140 complete; the fresh aggregate-only
full-200 predeclaration for GPT-4.1-mini plus DeepSeek is complete at
`docs/experiments/exectv2/reliability/exectv2_same_core_full200_predeclaration_2026-06-25.md`.
Qwen is diagnostic unless a separate predeclared repair passes dev140. See
`docs/plans/recent_plan_rationalisation_2026-06-25.md`.

## Objective

Freeze a single ExECTv2 core architecture and evaluate GPT-4.1-mini, DeepSeek,
and Qwen as model swaps over that architecture. The goal is to stop mixing
older model-specific architecture rows with the newer GPT-4.1-mini reliability
architecture, then incorporate only same-core rows into the final reliability
scorecard.

The core principle is:

```text
model swap after architecture freeze, not architecture swap disguised as model comparison
```

Model-specific prompt adapters are allowed. Model-specific architecture changes
are not allowed in the final comparison unless they are explicitly labelled as
separate diagnostic architectures.

## Completion Status

Updated: 2026-06-25

Completed:

- Wrote the freeze memo at
  `docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_freeze_2026-06-25.md`.
- Added frozen model-swap configs for GPT-4.1-mini, DeepSeek chat, and Qwen 3.6
  35B under `configs/exectv2/model_swap/`.
- Added a no-call/readiness artifact builder and a single-run model-swap runner.
- Materialized the GPT-4.1-mini dev140 same-core reference row from saved
  producer artifacts: overall `clinical_headline` F1 `0.8396`, Diagnosis
  `0.8573`, SeizureFrequency `0.7645`, Prescription `0.8895`, Investigations
  `0.8347`, with `0` call failures, `0` parse/schema failures, and `1.0000`
  minimum exact evidence rate.
- Generated the dev140 readiness report at
  `docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_dev140_2026-06-25.md`
  plus `experiments/exectv2_same_core_model_swap_dev140_20260625.json` and
  `.jsonl`.
- Ran the DeepSeek chat and Qwen 3.6 35B live dev140 same-core configs with
  DSPy cache disabled, preserving the frozen component graph and dev140-only
  inspection boundary.
- Completed the dev140 same-core readout: DeepSeek `0.8596`, GPT-4.1-mini
  `0.8396`, and Qwen `0.8018` overall `clinical_headline` F1, all with
  `1.0000` exact evidence.
- Refreshed the reliability scorecard/status language so older DeepSeek/Qwen
  rows are explicitly historical diagnostics, not final same-core model-swap
  evidence.

Still pending:

- Execute and report the optional full-200 aggregate-only comparison only from
  the frozen predeclaration if that comparison is still needed.
- Keep Qwen excluded from operational full-200 promotion unless a separate
  Qwen-specific repair is predeclared and passes dev140.

## Why This Plan Exists

The current reliability scorecard and surrounding reports preserve several
useful DeepSeek/Qwen results, but they are not all on the same architectural
surface:

| Row family | Current role | Problem for final comparison |
| --- | --- | --- |
| `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | Rich-schema DeepSeek diagnostic | Older rich-schema standard-dictionary row; not the GPT reliability architecture. |
| `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | Rich-schema Qwen diagnostic | Older residual-repair row; includes architecture-specific repair behavior. |
| `exectv2_holistic_finding_assembly_v0924_qwencompact_schemaoperand_dev140` | Later direct compact Qwen diagnostic | Newer than v0922, but still not the GPT 2-call reliability architecture. |
| `exectv2_holistic_finding_assembly_v05_qwen_relaxed_actions_dev140` | Candidate-backed Qwen selector diagnostic | Strong, but prediction-bearing facts originate in upstream candidates; not model-generated fact recovery. |
| `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator` | Accepted GPT-4.1-mini lean reliability candidate | Current reliability-assessment architecture; no same-core DeepSeek/Qwen rows yet. |

The scorecard may keep the older rows as historical path evidence, but the final
architecture comparison should not use them as if they were model swaps.

## Research Claim Protected

This plan protects three project claims:

- **Generalisation discipline:** model choice should be evaluated against a
  fixed architecture, not against model-specific rescue stacks.
- **Transparency:** every row should preserve producer ownership, deterministic
  actions, evidence validity, and scorer surface.
- **Component attribution:** reliability evidence and component-impact evidence
  must remain separate. A model-specific scorecard row should state what the
  model generated and what deterministic code projected or repaired.

## Canonical Core Architecture

Canonical candidate id:

```text
exectv2_2call_no_sf_adjudicator_model_swap
```

The common core should match the accepted GPT-4.1-mini lean reliability
candidate:

| Component | Common role |
| --- | --- |
| `structured_key_family_event_ledger` | Model-generated all-family structured draft. |
| `diagnosis_decomposer` | Model-generated Diagnosis decomposition. |
| `sf_structured_direct_adapter` | Extract SeizureFrequency from the structured draft; no SF adjudicator call. |
| `sf_state_projection` | Deterministic SF state projection from selected structured facts. |
| `sf_unknown_suppression` | Deterministic suppression policy for unsupported unknowns. |
| `sf_union_arbitration` | Deterministic union/arbitration over structured-direct SF outputs. |
| `prescription_deterministic_repair` | Deterministic Prescription regimen repair. |
| `finding_assembly` | Same assembly object model, lenses, views, and scorer. |

Required views:

- `raw_candidate`
- `evidence_valid`
- `clinical_headline`
- `fidelity_companion`
- `benchmark_cui`

Primary reporting surface:

```text
clinical_headline de-duplicated clinical recovery
```

Strict benchmark/CUI remains diagnostic and should not drive promotion.

## Allowed Model-Specific Differences

The model swap may vary only:

- runtime model identifier and endpoint;
- temperature, token budget, context budget, and provider settings;
- prompt wording needed for the model to satisfy the same output contract;
- JSON/schema compatibility repair that is format-preserving;
- endpoint/runtime telemetry, including local Qwen model digest and hardware notes.

The model swap may not vary:

- component graph;
- producer ownership;
- scoring view;
- entity lenses;
- deterministic SF projection/suppression/union logic;
- deterministic Prescription repair;
- review-routing, calibration, or robustness rules used in the scorecard;
- row-inspection boundary.

If a model requires a different architecture, record it as a diagnostic
variant, not as a same-core model-swap row.

## Model Rows To Build

| Model | Candidate id | Initial surface | Notes |
| --- | --- | --- | --- |
| GPT-4.1-mini | `exectv2_2call_no_sf_adjudicator_gpt41mini_dev140` | dev140 replay or matched rerun | Reference row aligned with the accepted full-200 reliability candidate. |
| DeepSeek | `exectv2_2call_no_sf_adjudicator_deepseek_dev140` | dev140 live or replay if available | Should use the same structured draft plus Diagnosis decomposer architecture; prompt adapter allowed. |
| Qwen 3.6 35B | `exectv2_2call_no_sf_adjudicator_qwen36_dev140` | dev140 live or replay if available | Should use native Ollama chat, `think=false`, Qwen-specific JSON compactness rules, and the same component graph. |

The existing `v0916`, `v0922`, `v0924`, and `v05` rows remain useful but should
move to historical or diagnostic comparison slots once same-core rows exist.

## Attribution Boundaries

### Same-Core Eligible

A row is same-core eligible when:

- the model emits the structured all-family draft;
- the model emits the Diagnosis decomposer output;
- SeizureFrequency is derived from the model's structured draft through the
  shared deterministic SF adapter/projection/suppression/union stack;
- Prescription repair is deterministic and labelled as such;
- Investigations come from the model structured draft through the same lens;
- no candidate-backed keep/reject selector replaces model-generated facts.

### Diagnostic Only

These remain diagnostic unless the final architecture is deliberately redefined:

- Qwen relaxed or strict candidate-action selectors;
- any candidate where prediction-bearing facts originate from deterministic or
  hybrid upstream candidate bundles;
- any row whose headline score depends on residual semantic rescue not present
  in the common core;
- any row produced by a different call graph, such as older rich-schema
  residual-repair stacks.

## Development Ladder

### Phase 0: Architecture Freeze Memo

Write a short freeze memo under `docs/experiments/exectv2/reliability/` that
declares:

- canonical core id;
- component graph;
- allowed model-specific adapter differences;
- scorer and views;
- split ladder;
- row-inspection policy;
- promotion gates;
- claim language for scorecard use.

Completion gate:

- The memo makes clear that old DeepSeek/Qwen rows are historical diagnostics,
  not the final same-core comparison.

### Phase 1: Config Backfill

Create one config per model-swap row.

Expected config shape should mirror the accepted GPT simplification frontier
manifest:

```text
configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_gpt41mini_dev140.json
configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_deepseek_dev140.json
configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_qwen36_dev140.json
```

Each config must declare:

- `candidate_id`
- `model`
- `architecture_core_id`
- `live_call_components`
- `replayed_components`
- producer artifacts;
- lenses;
- views;
- split;
- row count;
- claim boundary;
- call/parse/evidence telemetry fields.

Completion gate:

- All three configs have identical component graph and differ only in model
  adapter fields or source artifact paths.

### Phase 2: Dev140 Same-Core Runs

Run or replay dev140 same-core rows for all three models before touching
full-200.

Minimum report fields:

- overall `clinical_headline` F1, precision, recall, TP, FP, FN;
- per-family F1, precision, recall, TP, FP, FN;
- strict benchmark/CUI diagnostic F1;
- exact evidence rate and evidence-invalid counts;
- call failures;
- parse/schema failures;
- producer ownership by family;
- deterministic action counts for SF and Prescription;
- runtime metadata by model.

Completion gate:

- The three rows are comparable without changing the core architecture.
- Any model-specific failure is categorized as model behavior, prompt adapter
  behavior, endpoint/runtime behavior, or output-contract behavior.

### Phase 3: Same-Core Scorecard Readiness Review

Before updating the reliability scorecard, produce a readiness table:

| Gate | Requirement |
| --- | --- |
| Architecture parity | Same component graph across GPT-4.1-mini, DeepSeek, and Qwen. |
| Attribution clarity | Model-generated facts and deterministic projection/repair separated. |
| Evidence validity | Exact evidence rate reported for every model. |
| Operational stability | Call and parse/schema failures reported and bounded. |
| Family parity | Per-family F1 and residual risks reported. |
| Claim boundary | Dev140, full-200, and holdout surfaces not blended. |

Completion gate:

- The old scorecard rows are either replaced by same-core rows or explicitly
  demoted to historical diagnostics.

### Phase 4: Optional Full-200 Aggregate Audit

Phase 3 has produced a dev140 readiness report, and the frozen aggregate-only
full-200 audit predeclaration now exists for same-core model-swap rows at
`docs/experiments/exectv2/reliability/exectv2_same_core_full200_predeclaration_2026-06-25.md`.

The predeclaration includes:

- exact candidate ids;
- scorer and views;
- split/surface;
- stop rule;
- row-inspection boundary;
- model-specific runtime settings;
- whether all three models are run or only the promoted subset;
- allowed aggregate outputs.

No full-200 row-level failure ledgers should be generated or inspected.

Completion gate:

- Aggregate full-200 results can be incorporated into reliability claims without
  changing prompts, scorers, or repair policy after seeing the result.

## Promotion And Stop Rules

### Dev140 Promotion To Full-200 Audit

A model-swap row may advance to aggregate full-200 audit if:

- it uses the frozen common core;
- call failures are zero or operationally explained;
- parse/schema failures are low enough that the score is interpretable;
- evidence validity is comparable to the GPT reference;
- no family collapse makes the row uninformative as a final comparator;
- the result is strong enough to matter for the paper-facing comparison.

Suggested quantitative guide:

- overall `clinical_headline` F1 within `0.03` of the GPT same-core dev140 row,
  or a clearly useful family-specific advantage;
- SeizureFrequency not materially worse than the GPT same-core row unless the
  model is retained only as an operational/local diagnostic;
- no unexplained parse/schema failure pattern.

### Stop Conditions

Stop model-specific prompt iteration when any of these occur:

- The architecture has to change to make the model work.
- Improvements depend on deterministic semantic rescue outside the common core.
- A dev25 or dev140 result shows the same route-level limitation already seen in
  earlier LLM-only work.
- Qwen requires candidate-backed selection to be competitive and the target
  remains model-generated fact recovery.
- DeepSeek or Qwen cannot satisfy the output contract without semantic repair.

If a stop condition fires, freeze the model row as a diagnostic same-core
attempt rather than continuing prompt search.

## Reliability Scorecard Integration

After same-core rows exist, update the scorecard in these areas:

| Dimension | Integration rule |
| --- | --- |
| Task correctness | Use same-core model rows only for final model comparison. |
| Factuality and over-inference | Report per-family miss and over-emission rates from same-core rows. |
| Faithfulness / exact evidence | Report exact evidence and evidence-invalid counts by model. |
| Calibration | Do not transfer GPT calibration claims to DeepSeek/Qwen unless the same frozen scoring rule is audited on those rows. |
| Review routing | Do not promote model-specific routing claims without a frozen operating-point audit. |
| Robustness | Keep robustness claims tied to the audited current-code GPT row unless same-core model rows are run through the same aggregate hard-slice audit. |
| Consistency | Report model-swap cross-model agreement; within-model repeat consistency needs saved live repeats per model. |
| Family parity | Use same-core per-family F1 and residual risks, not older rich-schema rows. |
| Operational reliability | Report hosted/local endpoint telemetry, parse/schema failures, and call failures separately from scoring. |

The reliability scorecard should preserve two separate sections:

- **Final same-core model comparison:** GPT-4.1-mini, DeepSeek, Qwen on the
  frozen core.
- **Historical diagnostic rows:** v0916 DeepSeek, v0922 Qwen, v0924 Qwen,
  candidate-backed Qwen action selector, and Phase 6 direct LLM-only transfer
  rows.

## Component Impact Relationship

The same-core model-swap comparison is not, by itself, component-impact
evidence. Component impact still requires ablations or stage-ladder deltas.

However, once same-core rows exist, the component-impact payload can add a model
axis if:

- each model has the same layer ladder;
- the layer definitions are identical;
- deterministic projection and semantic rescue remain separated;
- the frontend labels the rows as model swaps, not new architectures.

## Expected Artifacts

Architecture/freeze docs:

```text
docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_freeze_2026-06-25.md
docs/plans/exectv2_same_core_model_swap_architecture_freeze_plan_2026-06-25.md
```

Configs:

```text
configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_gpt41mini_dev140.json
configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_deepseek_dev140.json
configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_qwen36_dev140.json
```

Reports:

```text
docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_dev140_2026-06-25.md
experiments/exectv2_same_core_model_swap_dev140_20260625.json
experiments/exectv2_same_core_model_swap_dev140_20260625.jsonl
```

Scorecard refresh:

```text
docs/experiments/exectv2/reliability/exectv2_cross_model_reliability_scorecard_2026-06-22.md
frontend/public/mock-data/exectv2/reliability-scorecard.json
```

## Open Questions

1. Should the same-core comparison now be executed/reported on full-200 from the
   frozen aggregate-only predeclaration, or remain dev140 evidence for the paper
   draft?
2. Should DeepSeek use chat or reasoner mode for ExECTv2, given the need for
   stable structured output and no hidden architecture changes?
3. Should Qwen use the compact v0924-style prompt adapter or a direct port of
   the GPT structured/decomposer prompts with only JSON compactness changes?
4. Should the candidate-backed Qwen action-selector become a separate hybrid
   architecture family, or stay diagnostic until after the same-core model swap?
5. What threshold defines a useful model-specific row: parity with GPT,
   family-specific advantage, operational/local deployment value, or all three?

## Not In Scope

- Gan 2026 holdout reruns or test-row inspection.
- ExECTv2 full-200 or holdout row-level failure analysis.
- Treating candidate-backed Qwen action selection as model-generated fact
  recovery.
- Updating paper-facing claims before same-core rows exist.
- Using reliability evidence as proof that a component caused a performance
  delta.

## Immediate Next Action

If the same-core full-200 comparison is still needed, execute and report only
from
`docs/experiments/exectv2/reliability/exectv2_same_core_full200_predeclaration_2026-06-25.md`.
Otherwise, proceed to registry-driven run surfacing with the dev140 same-core
rows and the frozen full-200 predeclaration as the claim boundary.
