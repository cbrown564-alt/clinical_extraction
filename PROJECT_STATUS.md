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

- Gan 2026 loading, split handling, scoring, semantic labels, prediction repair,
  and local `.venv` setup are in place under tests. Locked split:
  `gan2026_split_v1` with 300 train, 750 validation, and 450 final holdout rows.
- Deterministic V1 is frozen as a controlled comparator: 0.9293 Purist/0.9387
  Pragmatic on validation, but 0.7600/0.7867 on its one locked-test evaluation,
  so it is overfit and must not drive further holdout analysis.
- The LLM/DSPy validation ladder is 25-row smoke, 50-row meaningful signal, then
  250-row development result after a decision gate. Full 750-row validation runs
  are rare and require an artifact-level reason that 250 rows are insufficient.
- Direct note-to-label GPT-4.1 mini extraction is rejected as the final architecture: a full 750-row validation diagnostic reached 0.6733 Purist, 0.7253 Pragmatic, and 41 schema/parse failures.
- The staged structured LLM pipeline uses source-near events plus LLM clinical
  selection. Strong reference points: v0.2 250-row reparse at
  0.9800/0.9840 Purist/Pragmatic; v0.4 selector guidance at 0.9480 live and
  0.9520/0.9560 no-call reparse.
- A rare structured full-validation v0.5 completion hit the numeric threshold:
  675/750 Purist correct = 0.9000, 690/750 Pragmatic = 0.9200, 0 call failures,
  0 parse/schema failures, and 714/750 exact selected-evidence substrings. Repair
  audit and retrospective classify this as a repair-heavy hybrid development
  artifact, not clean LLM-first objective completion.
- Repair-family ablation defines claim language: raw LLM final-label selection is the attribution baseline; only strict format-preserving benchmark normalization belongs on the clean LLM-first path. Selected-evidence repair, monthly diary arithmetic, and clinical-selection overrides are separate deterministic modules.
- Strict format-preserving repair is separated from the prior full basic family.
  After sentinel fixes, 650-row replay gives raw model selection at 394/650
  Purist and strict format-preserving repair at 413/650, with 19 improvements
  and 0 regressions versus raw.
- Strict-format attribution policy is explicit: upper-bound forms (`up to`,
  `<=`/`≤`, `or less`) and `per quarter` are benchmark-format normalization;
  cluster-only labels remain raw attribution failures unless named. The no-call
  25-row replay improved to 22/25 Purist/Pragmatic with 2 intentional cluster
  parse failures and 25/25 exact evidence substrings.

## Key References

- Protocol/design: `docs/design/gan2026_split_protocol.md`, `docs/design/model_strategy.md`, `docs/research/gan2026_architecture_space_2026-06-01.md`
- Core code: `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_pipeline_cli.py`, `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_structured.py`
- Frozen V1 and rule review: `experiments/gan2026_v1_test_holdout_2026-05-31.md`, `docs/research/gan2026_deterministic_rule_review_2026-05-31.md`
- Structured LLM artifacts: `experiments/gan2026_llm_structured_validation250_gpt41mini_v02_reparse_current_2026-06-01.md`, `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion5_2026-06-01.md`, `experiments/gan2026_llm_structured_decision_retrospective_2026-06-01.md`, `experiments/gan2026_llm_structured_validation25_gpt41mini_v05_strict_format_replay2_2026-06-01.md`

## Active Priorities

1. Keep deterministic V1 frozen; put new deterministic behavior into separately named and ablated candidates.
2. Enforce the architecture gate before the metric gate: semantic-state-changing
   repair cannot satisfy the LLM-first objective without separate naming,
   ablation, and claim language.
3. Use the cleaned attribution replay as the raw-selection baseline before
   promoting any semantic repair or selector-guidance branch.
4. Target residual reasoning families with named, ablated modules or prompts:
   temporal selection, seizure-free/no-reference assertions, semiology
   reconciliation, non-epileptic or EEG-only mapping, and cluster interpretation.
5. Maintain conservative benchmark language; the test split has been touched once and must not become a tuning surface.

## Work Board

### Now

- Make `docs/research/gan2026_architecture_space_2026-06-01.md` the
  architecture-planning control doc: use its promotion contract, claim-type
  labels, and stricter 25/50/250 gates before promoting a new branch.
- Decide whether the next branch is a named cluster module, selector-guidance
  comparison, or another LLM-first reasoning prompt before any 50-row escalation.
- Keep the staged output contract: minimal source-near event facts first,
  deterministic normalization/validation second, and LLM clinical selection last.

### Next

- Compare v0.2 and v0.4 structured-pipeline error families row-by-row before
  adopting selector guidance more broadly.
- Continue the cleaned attribution condition to 50 rows only if the architecture
  control doc treats the two cluster-only failures as acceptable raw-attribution
  failures rather than unresolved format issues.
- Add paraphrase/adversarial tests for portable-rate expressions and seizure-free/no-event assertions.
- Start a living notebook for loading, gold-label distribution, scoring, and failure slices.

### Blocked

- Final benchmark-comparison language is blocked until the replication surface and paper comparability are explicit.
- Further holdout analysis is blocked by locked-test discipline; do not inspect test-row failures during candidate development.

### Backlog

- Refine heuristic row-level error slices into audited causal labels with examples.
- Add broader DSPy event extraction and clinical reasoner modules after the first cleaned reasoning experiment.
- Prepare controlled model/local-model comparison scaffolding with exact metadata.
- Consider DSPy GEPA only after stable artifacts and failure slices exist.

### Done Recently

- 2026-06-01: Added and evaluated the staged structured LLM extractor through
  the 25/50/250 ladder, then completed one rare 750-row validation run that hit
  0.9000 Purist only with repair-heavy hybrid behavior.
- 2026-06-01: Audited and ablated structured repair families, splitting clean
  strict format-preserving repair from semantic repair families; fixed sentinel
  corruption and confirmed 0 regressions on the saved 650-row replay surface.
- 2026-06-01: Classified strict-format smoke failures, added focused tests, kept cluster-only labels as raw attribution failures, and reran the 25-row no-call replay at 22/25 Purist/Pragmatic with 2 intentional cluster parse failures.
- 2026-06-01: Replaced deterministic V1's implicit final-selection tuple key with
  an explicit `SelectionPriority` record and `selected_decision` diagnostic.

## Immediate Next Step

Use `docs/research/gan2026_architecture_space_2026-06-01.md` to choose and name
the next development branch before any 50-row escalation.
