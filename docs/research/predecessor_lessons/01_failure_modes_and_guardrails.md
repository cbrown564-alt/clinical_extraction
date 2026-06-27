# Failure Modes And Guardrails From Predecessor Repos

Date: 2026-06-27

Purpose: preserve the concrete failures that should shape final-phase judgment
in `clinical_extraction/`. Each record includes enough detail to stand alone
without opening the predecessor repo.

## FM1. Evidence Presence Is Not Evidence Support

Historical source:
`dissertation/docs/run_logs/20260426T190914Z_h005_evidence_required_null_result.md`

Evidence record:

- Date: 2026-04-26.
- Experiment: `h005_multi_agent_evidence_required_llm`, an evidence-requiring
  verifier added after the `h004` role-separated LLM pipeline.
- Slice: n=100 synthetic seizure-frequency rows.
- Result: rejected as a quality gate. The verifier fired zero times because the
  model populated evidence text for every non-unknown prediction, including
  wrong ones.
- Metrics: identical to `h004`.
- Additional finding: wrong non-unknown predictions had mean confidence `0.95`;
  correct predictions had mean confidence `0.85`. A confidence threshold would
  have removed more correct answers than wrong answers.

Interpretation:

Evidence-like text and model confidence can be actively misleading. A quote can
be present, parseable, and nearby while failing to support the value, status,
temporality, or normalization claim.

Guardrail for `clinical_extraction/`:

- Keep evidence validity and evidence support separate.
- Do not report quote presence as grounding.
- Any verifier or reviewer should ask whether the evidence supports the claim,
  not whether the model supplied a string.
- Confidence or self-rated certainty should not be used as a review-routing
  gate without calibration evidence.

## FM2. Self-Consistency Bought Reliability At High Cost, But Did Not Fix Structural Errors

Historical sources:

- `dissertation/docs/run_logs/20260426T192738Z_h006_self_consistency_k3_result.md`
- `dissertation/docs/run_logs/20260426T195844Z_h007_self_consistency_k5_result.md`

Evidence record:

- Date: 2026-04-26.
- Task: synthetic seizure-frequency anchor task.
- `h006`: self-consistency with `k=3`, temperature `0.3`.
  - Pragmatic micro F1 improved from `0.50` for `h004` to `0.53`.
  - Unknown-class F1 improved by `+0.05`.
  - Infrequent-class F1 improved by `+0.09`.
  - Persistent infrequent-to-seizure-free hard rows remained: `9` in `h006`
    versus `8` in `h004`.
  - Cost: `3x` the per-row LLM calls.
- `h007`: self-consistency with `k=5`, temperature `0.3`.
  - Pragmatic micro F1 reached `0.55`, matching the deterministic multi-agent
    baseline `h002`.
  - Cost: `5x` the `h004` LLM calls.
  - Exact accuracy remained `0.19`, and monthly 15 percent accuracy remained
    `0.42`, both below deterministic `h002` (`0.31` exact, `0.48` monthly).
  - Reported runtime: about 37 minutes for n=100, or 500 LLM calls.

Interpretation:

Self-consistency improved class reliability but did not resolve the core
temporal ambiguity: letters with explicit seizure-free language plus recent
counts still drove consistent wrong answers. More samples amplify a model's
decision distribution; they do not invent missing task logic.

Guardrail for `clinical_extraction/`:

- Treat self-consistency as a budget-quality frontier, not as a default fix.
- Compare same-budget and higher-budget results separately.
- For review routing or selective verification, evaluate conditional behavior:
  what happens when the base output is correct versus when it is wrong?
- Do not expect sampling to fix deterministic policy gaps, benchmark label
  mismatches, or structural temporal reasoning failures.

## FM3. Decomposition Can Destroy Context

Historical source:
`dissertation/docs/run_logs/20260427T140000Z_h010_h011_architecture_decision.md`

Evidence record:

- Date: 2026-04-27.
- Goal: resolve whether broad-field extraction needed a joint prompt, a
  seizure-frequency anchor, or a two-stage decomposition.
- Slice: n=50.
- Four-harness comparison:
  - `h008` joint extraction: seizure-frequency micro F1 `0.30`; medication
    abstention `0.08`; seizure-type abstention `0.04`; investigation
    abstention `0.28`.
  - `h009` two-stage broad-only extraction: seizure-frequency micro F1 `0.54`;
    medication abstention `0.96`; seizure-type abstention `0.92`;
    investigation abstention `0.96`.
  - `h010` anchored joint prompt: seizure-frequency micro F1 `0.20`;
    broader-field coverage remained good, but anti-abstention language caused
    over-prediction of seizure-free labels.
  - `h011` context-injected two-stage extraction: seizure-frequency micro F1
    `0.54`; medication abstention `0.98`; seizure-type abstention `0.96`;
    investigation abstention `0.98`.
- Decision: reject `h010` and `h011`; accept `h008` for broader-field
  feasibility despite its seizure-frequency tradeoff.

Interpretation:

The decomposition recovered seizure-frequency behavior but removed the joint
clinical framing needed for broad-field coverage. Injecting the seizure-frequency
label as context did not recreate the broader extraction effect. Architecture
changed what the model attended to.

Guardrail for `clinical_extraction/`:

- Treat decomposition as an intervention with field-specific tradeoffs, not as a
  quality-improving default.
- If adding a stage, state which failure mode it targets and which fields it is
  allowed to harm.
- Use per-family metrics, not only aggregate scores, before promoting a
  decomposed pipeline.

## FM4. Prompt And Schema Contract Bugs Can Dominate Architecture

Historical sources:

- `dissertation-experiments/docs/prompt_design_gap_report.md`
- `dissertation-recursive/docs/53_multi_agent_phase_synthesis_gaps.md`

Evidence record:

- The prompt design gap report found that the experiment axes were sensible
  on paper - task, dataset policy, guideline, prompt strategy, schema contract,
  evidence policy, example policy, projection policy, scoring view, model, and
  orchestration policy - but that several axes were under-specified in the
  model-facing prompt.
- It warned that phrases such as "benchmark-comparable clinical facts" are
  useful to experimenters but not useful clinical guidance for a model.
- It identified evidence wording such as "Evidence quotes are optional for this
  condition" as confusing; if evidence is not required, the prompt should omit
  evidence instructions entirely.
- The multi-agent synthesis gaps document records a concrete contract collapse:
  a verifier prompt changed medication output from structured medication objects
  to flat medication-name strings. Medication full-tuple F1 fell from roughly
  `0.60` to `0.018`, a 30-35x collapse. The failure was a prompt/schema contract
  bug, not proof that the architecture was bad.

Interpretation:

When prompts expose internal harness concepts, omit allowed labels, blur
evidence policy, or mismatch the expected schema, the result measures prompt
ambiguity and parser compatibility more than clinical extraction capability.

Guardrail for `clinical_extraction/`:

- Every reportable condition should render as a standalone clinical extraction
  instruction.
- Audit metadata, scorer names, projection policy, and benchmark-comparison
  language should stay out of model-facing text unless deliberately tested.
- Add prompt snapshot tests for high-risk prompt changes.
- Before scaling a verifier/corrector, test malformed and edge-case outputs
  against the exact schema expected by downstream scoring.

## FM5. Scorer And Gold-Data Bugs Can Invert The Project Story

Historical sources:

- `dissertation-recursive/docs/50_synthesis_report.md`
- `dissertation-recursive/docs/33_gold_audit_synthesis.md`
- `dissertation-experiments/docs/schema_ladder_sweep_findings.md`

Evidence record:

- The recursive synthesis reported that the original `final_validation`
  medication full-tuple F1 (`0.386/0.343/0.400`) understated true performance by
  `70-85%` relative after scoring repair.
- It also reported that original seizure-frequency score `0.000` was a gold
  loader bug, and original seizure-type F1 around `0.187-0.200` reflected a
  taxonomy mismatch.
- The ExECT gold audit found that an apparent `13.5%` span-boundary error rate
  was mostly spelling-correction offset drift, not annotator error.
- The same audit found `57` stale CSV rows with offsets from before spelling
  correction. These rows were silently ignored by evaluation code that read CSVs
  rather than `.ann` files.
- Gan audit finding: `31/1500` labels (`2.1%`) were unparsable by the project
  label parser even though they were not unknown/no-reference labels.
- Gan seizure-free audit finding: among all `132` "seizure free for multiple
  month/year" cases, `36` (`27.3%`) applied a seizure-free label to periods
  explicitly shorter than the written 6-month threshold.
- Schema-ladder sweep finding: two scoring bugs were corrected before reporting,
  including a frequency scorer bug where wrapped `{value, evidence}` outputs
  were treated as non-strings and mapped to no-reference.

Interpretation:

Several apparent model failures were measurement failures. Several apparent gold
label errors were schema or tooling artefacts. Scorer repair was not bookkeeping;
it changed the scientific interpretation.

Guardrail for `clinical_extraction/`:

- Treat scorer and gold-loader integrity as first-class research evidence.
- Never compare historical metrics without knowing the scorer version and
  projection path.
- Preserve current frozen aggregate reports and their companion machine-readable
  artifacts.
- When a model appears to fail dramatically, check scorer, parser, projection,
  and gold representation before changing the model or prompt.

## FM6. Benchmark-Label Alignment Can Masquerade As Clinical Capability

Historical source:
`dissertation-experiments/docs/primary_sweep_error_analysis.md`

Evidence record:

- Date: 2026-05-16.
- Runs: Qwen and Gemini full ExECT validation conditions plus a minimal Qwen
  reference.
- Seizure type raw metrics:
  - Qwen best-config F1 `0.409`.
  - Gemini best-config F1 `0.554`.
- Simulated coarse remapping of ILAE-specific focal labels to the benchmark's
  coarser `focal seizure` label:
  - Qwen improved from `0.409` to `0.549` (`+0.140`).
  - Gemini improved from `0.554` to `0.653` (`+0.099`).
  - Qwen minimal improved from `0.435` to `0.565` (`+0.130`).
- Diagnosis error analysis showed a repeated "modifier capture" pattern:
  diagnosis lines containing symptomatic/structural focal epilepsy were mapped
  by the model to `symptomatic`, while gold collapsed to `focal epilepsy`.
- The report concluded that the dominant seizure-type problem was not
  comprehension failure but label granularity mismatch between ILAE-aligned
  model labels and coarser benchmark gold labels.

Interpretation:

A model can be clinically reasonable and benchmark-wrong, or benchmark-aligned
and clinically less specific. Label granularity and scoring views are part of
the experiment, not passive measurement.

Guardrail for `clinical_extraction/`:

- Keep `clinical_headline`, strict benchmark, CUI, benchmark-collapsed, Purist,
  and Pragmatic views separate.
- Do not report strict benchmark/CUI scores as the same thing as clinical
  recovery.
- If a deterministic bridge improves a benchmark score, state whether it changed
  semantic selection, label formatting, or scoring alignment.

## FM7. Optimizers Are Bounded Probes, Not Default Progress

Historical sources:

- `dspy-extraction/docs/workstreams/optimizer/dspy_optimizer_vs_manual_engineering_audit_20260520.md`
- `dspy-extraction/docs/workstreams/hybrid/hybrid_deterministic_placement_research_synthesis_20260521.md`

Evidence record:

- The optimizer audit found strong use of DSPy signatures, modules, structured
  output, artifacts, and scorer separation, but weak use of compile loops on
  ExECT. Gan had optimizer experiments; ExECT did not.
- The runner explicitly gated optimizer support to Gan experiments in that repo.
- Gan GEPA produced prompt bloat: one recorded Qwen path grew from `508` to
  `1,819` words and regressed labels.
- Semantic BootstrapFewShot and semantic GEPA failed cap-25 comparisons against
  verify-repair/temporal-candidate approaches.
- Qwen GEPA compile took about `536` seconds and produced non-canonical labels.
- The hybrid placement synthesis concluded that Gan benefited most from
  deterministic temporal preconditioning plus LLM adjudication, whereas ExECT S1
  performance depended on benchmark policy during extraction and deterministic
  bridges after extraction.

Interpretation:

Optimizer failure did not mean DSPy failed; program decomposition and component
placement were the relevant levers. Optimizers helped where the failure mode was
demo/instruction selection, but not where the bottleneck was temporal
aggregation, label policy, or benchmark bridge behavior.

Guardrail for `clinical_extraction/`:

- Do not restart optimizer loops in the closing phase by default.
- If an optimizer baseline is scientifically needed, make it narrow, validation
  only, and explicitly compare it to a frozen non-optimized control.
- Keep optimizer metrics separate from benchmark and clinical recovery metrics.

## FM8. Agent-Generated Artifacts Are Leads, Not Evidence

Historical sources:

- `dspy-extraction/docs/workstreams/cursor_sdk/cursor_sdk_final_value_report_20260525.md`
- `dspy-extraction-cursor-pilot-artifacts/20260524T082000Z_mutation_test_report.md`

Evidence record:

- Cursor SDK final report decision: retire active usage. It was useful for
  checklists, source maps, contradiction-finding passes, and focused leads, but
  not reliable enough as active implementation or paper-prose dependency.
- The report states that unreviewed paper prose drafts were useful as source
  maps and discrepancy checklists, but not safe as manuscript text.
- It records at least one runner-level "success" that produced a zero-byte
  draft, reinforcing that SDK success status was not substantive evidence.
- Mutation pilot:
  - Existing tests: `49/49` passed before and after mutation.
  - Enriched Gan slice improved from `23/25` to `25/25`.
  - Residual slice stayed `24/30`.
  - Workspace rollback succeeded; diff was discarded.
  - The promoted value was a narrow future lead, not direct code promotion.

Interpretation:

External/agent-generated research ops can accelerate search, but it increases
review burden and can create false confidence. Disposable mutation is valuable
only when rollback, diff capture, and tests are mandatory.

Guardrail for `clinical_extraction/`:

- Agent drafts should carry source-status labels: lead, verified, promoted, or
  rejected.
- Do not cite agent-generated prose or SDK reports as evidence unless every
  claim is promoted from primary artifacts.
- Any future mutation-agent work should happen in disposable worktrees with a
  clean state, captured diff, tests, and rollback.

## FM9. Split Names Drift Across Repos

Historical and current sources:

- `dspy-extraction/tests/test_dataset_splits_policy.py`
- `clinical_extraction/docs/design/gan2026_split_protocol.md`
- `clinical_extraction/tests/test_gan2026_validation_test_gap_protocol.py`
- `clinical_extraction/tests/test_gan2026_validation_test_surface_map.py`

Evidence record:

- The DSPy-era split-policy test asserted that fixed split files must contain
  exactly `train`, `validation`, and `test`, and must not contain
  `development`.
- Current Gan 2026 protocol defines:
  - train: `300` rows, optimizer-only;
  - validation: `750` rows, primary development surface;
  - test: `450` rows, locked holdout.
- Current validation/test gap tests require protocol text that blocks locked-test
  row-level tuning, permits only aggregate summaries and predeclared-slice
  summaries, and prevents first-wave analysis from introducing a new
  prediction-bearing architecture.
- Current surface-map tests assert that locked-test reports are aggregate-only
  and do not expose locked-test row-level failures.

Interpretation:

The same word can mean different things across attempts. Earlier train,
validation, development, test, and full-dataset roles are not automatically
comparable to current `clinical_extraction/` roles.

Guardrail for `clinical_extraction/`:

- Every historical comparison must name the local split protocol.
- Do not compare a predecessor "validation" number to a current validation,
  full-200, dev, or holdout number without checking the row set and inspection
  rights.
- Treat current Gan `test450` and ExECTv2 full-200/holdout surfaces as protected
  under current protocols, regardless of what older repos allowed.

## Summary Guardrail Table

The third column records, as of 2026-06-27, whether the current
`clinical_extraction/` checkout already operationalizes the guardrail. This is a
grounded snapshot (verified against current tests, `PROJECT_STATUS.md`, and
source modules), not an aspiration. Re-check it before citing, since the closing
phase may move items from open to absorbed.

| Failure mode | Practical final-phase rule | Status in `clinical_extraction/` (2026-06-27) |
| --- | --- | --- |
| Evidence presence | Score support quality, not quote existence. | Partial — `core/evidence_validity_audit.py` and `experiments/reconcile_evidence_groundedness_registry.py` audit validity/groundedness; a separate support-quality scoring view is not yet standard. |
| Confidence gates | Require calibration evidence before using confidence for routing. | Absorbed — calibration probe found joint self-confidence dead; confidence kept as a decoupled, non-gating shadow stage. |
| Self-consistency | Report budget separately; expect structural errors to persist. | Absorbed as guardrail — sampling/self-consistency treated as a bounded budget-quality probe, not a default fix. |
| Decomposition | Add stages only with a predeclared failure mode and per-field gates. | Absorbed — per-family metrics are the standard reporting unit for ExECTv2 and Gan. |
| Prompt/schema bugs | Snapshot and test model-facing contracts before scale-up. | Absorbed (2026-06-27) — `tests/test_prompt_contract_snapshots.py` pins 10 model-facing contracts (both tasks plus the primary `clinical_headline` dedup `output_schema`/`adapter_contract`); a drifted contract fails with a reviewable diff. Negative control confirmed the guard fires. |
| Scorer/gold bugs | Audit scorer and projection before interpreting a metric collapse. | Absorbed — scoring-mechanics + gold-representation docs and the frozen evidence manifest pin scorer/projection versions. |
| Benchmark mismatch | Keep clinical and strict benchmark views separate. | Absorbed — `clinical_headline` recovery is primary; strict benchmark/CUI stays diagnostic per `PROJECT_STATUS.md`. |
| Optimizers | Use as bounded probes, not default final-phase work. | Absorbed — GEPA from-scratch run as a bounded validation probe on both tasks (`gepa/run_gepa.py`); result negative-on-goal with a length-penalty win, not a reopened loop. |
| Agent drafts | Treat as leads until primary-source promotion. | Absorbed as discipline — this packet is itself a memory/lead layer; Cursor SDK active usage retired. |
| Split drift | Interpret every number inside its original split protocol. | Absorbed — enforced by `tests/test_gan2026_validation_test_gap_protocol.py` and `tests/test_gan2026_validation_test_surface_map.py`; locked surfaces named in `PROJECT_STATUS.md` Blocked. |
