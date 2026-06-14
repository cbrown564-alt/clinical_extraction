# Project Status

Last updated: 2026-06-14

## Active Objective

Surpass `0.85` Purist accuracy on locked Gan 2026 `test450` with a frozen,
LLM-owned, evidence-grounded structured-event reasoning pipeline. Success
requires at least `383/450` Purist on one explicitly authorized aggregate-only
audit, with no deterministic final-label fallback and no tuning from test
row-level failures.

Latest frozen audit result: V12 `fresh_evidence_reasoner` v0.4,
`openai/gpt-4.1`, reached `379/450` Purist on the authorized aggregate-only
`test450` audit, below the `383/450` target. The goal is not achieved.

## Recent Context

- Follow-on plan:
  `docs/research/gan2026_llm_reasoning_agentic_test085_experiment_plan_2026-06-13.md`.
  It requires validation hard slices, validation250, full validation only for a
  freeze decision, then one frozen aggregate-only `test450` audit after explicit
  authorization.
- V12 `fresh_evidence_reasoner` is registered on the shared Gan CLI. It uses
  saved structured-event traces only as scaffolding; the model may keep the
  original GPT structured-event final or replace it with a raw-evidence-grounded
  final label. Deterministic code is limited to prompt assembly, schema/format
  repair, exact-substring evidence filtering, predeclared safety gates,
  rendering, and scoring.
- V12 v0.4 passed the ladder without test row inspection: validation25 `25/25`,
  fixed hard50 `42/50` versus V0 `39/50`, validation250 `242/250` versus V0
  `236/250`, and validation750 `682/750` versus V0 `661/750`. Validation750 had
  `0` call failures, `0` parse/schema/label failures, `42` wrong-to-correct,
  `22` correct-to-wrong, `703/750` exact evidence substrings, and final
  Pragmatic `698/750`.
- Frozen audit packet:
  `docs/research/gan2026_fresh_evidence_reasoner_frozen_test450_protocol_2026-06-13.md`.
  It pins the exact command, hashes, source substrate, aggregate-only readout,
  technical recovery policy, and stop rule. It is not authorization by itself.
- On 2026-06-14, the user explicitly authorized the one frozen V12 aggregate-only
  `test450` audit. The exact pinned command ran to completion with `450/450`
  rows, `0` call failures, and `0` parse/schema/label failures. The pinned
  aggregate-only readout helper reports final Purist `379/450` (`0.8422`),
  raw model Purist `372/450`, format-only Purist `372/450`, V0 Purist
  `364/450`, final Pragmatic `394/450`, exact evidence substrings `423/450`,
  and `target_reached=false`. No row-level holdout failures were inspected.
- Post-audit synthesis:
  `docs/research/gan2026_hybrid_structured_events_agentic_consensus_fresh_evidence_analysis_2026-06-14.md`
  records the architecture rationale, pipeline diagrams, validation/test
  performance, and major explored journeys for hybrid structured events,
  agentic/consensus variants, and V12 `fresh_evidence_reasoner`.
- The missing DeepSeek structured-events `test450` source artifact has now been
  filled. On 2026-06-14, the user authorized a live DeepSeek SE v0.6 full
  `test450` source-coverage run, producing
  `experiments/gan2026_v06_test450_hybrid_structured_events_deepseek_2026-06-14.jsonl`
  and `.md`. Aggregate health: `446/450` structured records, `0` call failures,
  `4` parse/schema/label issues, `440/450` exact evidence substrings, Purist
  `354/450`, Pragmatic `368/450`. This corrects the source-coverage gap for
  future frozen aggregate-only consensus/scaffolding audits; it is not a new
  promoted candidate and no row-level holdout failure analysis was performed.
- Current preflight:
  `python -m clinical_extraction.tasks.seizure_frequency.gan2026.cli.frozen_test_preflight --json`
  reports `"ok": true`. It verifies the exact live command, model/token budget,
  artifact hashes, split count, frozen GPT/Qwen test source hashes and coverage,
  explicit DeepSeek test-source unavailability, absence of V12 test and
  `.resume-part` outputs, prompt-input hygiene, and aggregate-only output
  redaction, including synthetic report compatibility with the pinned
  aggregate-only readout helper.
- Verification status before authorization: focused frozen-gate tests pass
  `72/72`, the full offline Gan pytest module suite passes `1172/1172`, Ruff is
  clean for the frozen V12/readout/CLI files, and the pinned V12 `test450`
  output/resume artifacts are still absent.
- Post-run first readout is also pinned:
  `python -m clinical_extraction.tasks.seizure_frequency.gan2026.cli.frozen_test_readout --json`
  reads only the pinned aggregate-only Markdown report, rejects alternate report
  paths, row-level sections, and unpinned JSONL-artifact markers, and reports
  whether final Purist reached `383/450`, with raw/format-only/final
  Purist/Pragmatic aggregate attribution counts, without opening the JSONL.
- The shared Gan LLM CLI requires `--confirm-test-audit` for `--split test`,
  requires live mode with temperature `0.0`, rejects partial test subsets,
  overwrites, source-artifact override flags (`--structured-event-jsonl`,
  `--candidate-set-jsonl`), prompt-only test mode, `--api-base`, and
  `--disable-dspy-cache`; for V12 it also rejects model/token drift from
  `openai/gpt-4.1` and `2800`, plus JSONL/Markdown output-path drift from the
  pinned frozen audit artifacts. It permits `--resume-existing` only for
  documented technical recovery with an existing JSONL.
- Prior aggregate-only structured-event consensus `test450` audit reached only
  `365/450` Purist. No row-level holdout failures were inspected or tuned.
  Earlier V1, V3, V4, V7, V8, V9, V10, and V11 branches are rejected for
  escalation except as historical comparison artifacts.

## Guardrails

- Gan split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
- Validation is development evidence. Locked `test450` is aggregate-only; no
  row-level holdout tuning or error inspection is authorized.
- New holdout-facing Gan work requires explicit frozen-protocol authorization.
- Keep evidence metrics architecture-specific: `evidence_valid`,
  `evidence_text_contained`, exact raw-note substring checks, and CandidateSet
  source-id validity are different.
- Do not claim multi-agent value without matched-budget single-agent evidence.
  V12 is a single-model fresh-evidence candidate.

## Active Priorities

1. Record the V12 `test450` audit as final-evaluation evidence, not a success.
2. Preserve the no-test-tuning boundary: do not inspect row-level holdout
   failures, rationales, evidence, selected events, or transitions.
3. If continuing toward the `>0.85` objective, start a new validation-only
   candidate cycle from validation artifacts and predeclare any later holdout
   protocol separately.

## Work Board

### Now

- Record the authorized V12 v0.4 aggregate-only `test450` audit as below target:
  final Purist `379/450` versus required `383/450`.

### Next

- If pursuing another attempt, open a new validation-only design cycle; do not
  tune prompts, gates, normalization, model choice, source artifacts, or scorer
  from the V12 holdout result.
- Populate the Architecture Thesis Scorecard from existing Gan artifacts.

### Blocked

- Any Gan holdout-facing rerun, row-level test analysis, or post-test tuning is
  blocked without explicit authorization and a frozen-protocol note.
- V1, V3, V4, V7, V8, V9, V10, V11, and historical E3/E4 live designs are
  blocked from escalation except as comparison artifacts.

### Backlog

- Optional: summarize V12 report profile dumps in future Markdown reports.
- Optional: add an Architecture Thesis Scorecard entry contrasting V12
  single-model fresh-evidence reasoning with saved-output consensus.

### Done Recently

- 2026-06-13: Added, tested, registered, and froze V12
  `fresh_evidence_reasoner`; completed validation25, hard50, family-slice,
  validation250, and validation750 gates without test row inspection.
- 2026-06-14: Ran the explicitly authorized V12 frozen aggregate-only `test450`
  audit and pinned readout. Result missed the goal: final Purist `379/450`
  (`target_reached=false`), final Pragmatic `394/450`, with `0` call failures
  and `0` parse/schema/label failures. No row-level holdout analysis was done.
- 2026-06-14: Added a detailed research synthesis covering hybrid structured
  events, early agentic/matched-budget variants, structured-event consensus,
  V1-V11 agentic variants, and V12 `fresh_evidence_reasoner`, with Mermaid
  pipeline diagrams and aggregate validation/test performance tables.
- 2026-06-14: Generated the missing DeepSeek SE v0.6 `test450` structured-event
  artifact as an aggregate-only source-coverage run: Purist `354/450`,
  Pragmatic `368/450`, `446/450` structured records, `0` call failures, and
  `440/450` exact evidence substrings.
- 2026-06-13: Hardened V12 frozen test preflight and shared CLI launch guards:
  split-matched GPT/Qwen test substrates, DeepSeek test-source caveat,
  live-mode, temperature, model, token-budget, API-base, and cache-policy locks,
  JSONL/Markdown output-path locks, singleton protocol command checks,
  source-override rejection, stale `.resume-part` rejection, prompt hygiene,
  aggregate-only redaction, pinned raw/format-only/final Purist/Pragmatic
  readout checks, synthetic readout-parser compatibility, and broad offline
  Gan test-suite verification.
- 2026-06-13: Built Stage 0 validation-only family hard-slice manifests and V0
  pure structured-event comparator report, then rejected prior agentic branches
  and the `365/450` structured-event consensus holdout result as insufficient.

## Core Artifacts

- `docs/research/gan2026_llm_reasoning_agentic_test085_experiment_plan_2026-06-13.md`
- `docs/research/gan2026_hybrid_structured_events_agentic_consensus_fresh_evidence_analysis_2026-06-14.md`
- `docs/research/gan2026_fresh_evidence_reasoner_frozen_test450_protocol_2026-06-13.md`
- `experiments/gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.md`
- `experiments/gan2026_fresh_evidence_reasoner_validation250_live_gpt41_v0_4_2026-06-13.md`
- `experiments/gan2026_fresh_evidence_reasoner_hard50_live_gpt41_v0_4_2026-06-13.md`
- `experiments/gan2026_v06_test450_hybrid_structured_events_deepseek_2026-06-14.md`
- `experiments/gan2026_llm_reasoning_stage0_v0_comparators_2026-06-13.md`
- `experiments/RUN_INDEX.md`
