# Project Status

Last updated: 2026-06-01

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that can reach at least 0.9000 Purist F1 on development surfaces while preserving enough structure for future clinical extraction tasks.

The paper-facing target is a hybrid deterministic-LLM system with transparent evidence trails, component-level ablations, and conservative benchmark language.

## Current Strategy

Use Gan 2026 as the first controlled extraction surface. Keep data loading, label normalization, scoring, split discipline, and deterministic-rule behavior explicit before optimizing LLM or DSPy components.

Deterministic V1 is frozen as a controlled comparator, not an expanding solution.
New candidate work should stay LLM-first: model extraction and clinical
selection produce the prediction-bearing interpretation; deterministic code is
limited to schema validation, evidence validation, Gan-compatible normalization,
strict benchmark-format repair, arithmetic repair, and explicitly ablated named
modules.

## Recent Context

- Core Gan 2026 loading, split handling, scoring, semantic labels, prediction repair, and local `.venv` setup are in place under tests.
- Locked split manifest: `data/Gan (2026)/splits/gan2026_split_v1.json` with 300 train, 750 validation, and 450 final holdout rows. Development stays on train/validation.
- Deterministic V1 is implemented in `gan2026.pipeline_v1`, with candidate
  events, normalization, final-selection diagnostics, rule metadata, ablations,
  and exact selected-evidence validation.
- Deterministic V1 is frozen. Current validation baseline is 0.9293 Purist
  micro F1/accuracy and 0.9387 Pragmatic, with 750/750 exact evidence validity.
  Its one locked-test evaluation was 0.7600 Purist and 0.7867 Pragmatic, so it is
  overfit to validation and must not drive further holdout analysis.
- The LLM/DSPy validation ladder is 25-row smoke, 50-row meaningful signal, then
  250-row development result after a decision gate. Full 750-row validation runs
  are rare and require an artifact-level reason that 250 rows are insufficient.
- Direct note-to-label GPT-4.1 mini extraction is rejected as the final
  architecture: a full 750-row validation diagnostic reached 0.6733 Purist,
  0.7253 Pragmatic, and 41 schema/parse failures.
- The staged structured LLM pipeline uses a slim source-near event schema, LLM
  clinical selection, shared schema repair, and Gan-compatible label repair. Its
  strongest standard-gate result is the v0.2 250-row reparse at 0.9800 Purist
  and 0.9840 Pragmatic, with 0 parse/schema failures and 242/250 exact selected
  evidence substrings.
- A rare structured full-validation v0.5 completion hit the numeric threshold:
  675/750 Purist correct = 0.9000, 690/750 Pragmatic = 0.9200, 0 call failures,
  0 parse/schema failures, and 714/750 exact selected-evidence substrings. Repair
  audit and retrospective classify this as a repair-heavy hybrid development
  artifact, not clean LLM-first objective completion.
- Repair-family ablation defines claim language: raw LLM final-label selection is the attribution baseline; only strict format-preserving benchmark normalization belongs on the clean LLM-first path. Selected-evidence repair, monthly diary arithmetic, and clinical-selection overrides are separate deterministic modules.
- Strict format-preserving repair is separated from the prior full basic family. After sentinel-preservation fixes, replay over 650 saved v0.5 validation-development rows reports raw model selection at 394/650 Purist correct = 0.6062 and strict format-preserving repair at 413/650 = 0.6354, with 19 improvements and 0 regressions versus raw.
- V0.4 structured selector guidance is diagnostic, not promoted: live 250-row development reached 0.9480 Purist/Pragmatic, and no-call reparse reached 0.9520 Purist and 0.9560 Pragmatic.

## Key References

- Split protocol: `docs/design/gan2026_split_protocol.md`
- Model strategy: `docs/design/model_strategy.md`
- Deterministic rule review: `docs/research/gan2026_deterministic_rule_review_2026-05-31.md`
- Frozen V1 test holdout: `experiments/gan2026_v1_test_holdout_2026-05-31.md`
- LLM validation ladder and CLI runner: `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_pipeline_cli.py`
- Structured LLM pipeline: `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_structured.py`
- Direct note-to-label diagnostic: `experiments/gan2026_llm_first_validation750_gpt41mini_v01_2026-06-01.md`
- Structured 250-row standard-gate reparse: `experiments/gan2026_llm_structured_validation250_gpt41mini_v02_reparse_current_2026-06-01.md`
- Structured rare 750-row completion: `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion5_2026-06-01.md`
- Repair audit, retrospective, and ablations: `experiments/gan2026_llm_structured_validation750_v05_repair_audit_2026-06-01.md`, `experiments/gan2026_llm_structured_decision_retrospective_2026-06-01.md`, `experiments/gan2026_llm_structured_validation750_v05_repair_ablation_2026-06-01.md`, `experiments/gan2026_llm_structured_validation750_v05_basic_split_repair_ablation_2026-06-01.md`, `experiments/gan2026_llm_structured_validation750_v05_strict_format_regression_audit_2026-06-01.md`

## Active Priorities

1. Keep deterministic V1 frozen; put new deterministic behavior into separately named and ablated candidates.
2. Enforce the architecture gate before the metric gate: semantic-state-changing
   repair cannot satisfy the LLM-first objective without separate naming,
   ablation, and claim language.
3. Re-run the validation ladder on the cleaned attribution condition: raw
   structured model selection plus strict format-preserving basic repair only.
4. Use the mined ablation dev set and structured-pipeline failures to target
   residual reasoning families: temporal/current-versus-historical selection,
   seizure-free versus unknown/no-reference assertions, trigger-conditioned
   events, semiology reconciliation, non-epileptic or EEG-only mapping, and
   cluster-detail interpretation.
5. Maintain conservative benchmark language. The test split has been touched once for frozen-context evaluation and must not become a tuning surface.

## Work Board

### Now

- Run the cleaned 25-row validation smoke with raw structured model selection plus `basic_label_repair=True`, `basic_label_repair_format_only=True`, and all later repair families disabled.
- If the smoke is clean, continue the same attribution condition through the
  50-row and 250-row ladder; stop for error-family inspection before any rare
  750-row validation escalation.
- Keep the staged output contract: minimal source-near event facts first,
  deterministic normalization/validation second, and LLM clinical selection last.

### Next

- After the cleaned attribution run is completed or explicitly suspended, make
  `docs/research/gan2026_architecture_space_2026-06-01.md` the next
  architecture-planning control doc: use its promotion contract, claim-type
  labels, and stricter 25/50/250 gates before promoting a new branch.
- Compare v0.2 and v0.4 structured-pipeline error families row-by-row before
  adopting selector guidance more broadly.
- Add paraphrase and adversarial tests for portable-rate expressions and seizure-free/no-event assertions.
- Start a living notebook for loading, gold-label distribution, scoring, and failure slices.
- Prepare controlled model-comparison scaffolding with exact model metadata in every run artifact.

### Blocked

- Final benchmark-comparison language is blocked until the replication surface and paper comparability are explicit.
- Further holdout analysis is blocked by locked-test discipline; do not inspect test-row failures during candidate development.

### Backlog

- Add run-record metadata templates under `experiments/`.
- Refine heuristic row-level error slices into audited causal labels with examples.
- Add broader DSPy event extraction and clinical reasoner modules after the first cleaned reasoning experiment.
- Run controlled local-model comparisons after model-comparison scaffolding is ready.
- Consider DSPy GEPA only after stable artifacts and failure slices exist.

### Done Recently

- 2026-06-01: Re-established the Gan LLM runner as a general CLI harness with raw-output reuse, DSPy cache control, progress emission, and 10-row checkpointing.
- 2026-06-01: Rejected direct note-to-label extraction after the rare 750-row diagnostic exposed low accuracy and schema brittleness.
- 2026-06-01: Added and evaluated the staged structured LLM extractor through
  the 25/50/250 ladder, then completed one rare 750-row validation run that hit
  0.9000 Purist only with repair-heavy hybrid behavior.
- 2026-06-01: Audited and ablated structured repair families, splitting clean
  strict format-preserving repair from semantic repair families for claim
  language.
- 2026-06-01: Fixed strict-format sentinel corruption and confirmed strict format-preserving repair improves over raw model selection with 0 regressions on the saved 650-row replay surface.
- 2026-06-01: Replaced deterministic V1's implicit final-selection tuple key with
  an explicit `SelectionPriority` record and `selected_decision` diagnostic.

## Immediate Next Step

Run the cleaned 25-row validation smoke with raw structured model selection plus
strict format-preserving basic repair only, then inspect whether the remaining
strict-format behavior is narrow enough before continuing to 50 and 250 rows.
