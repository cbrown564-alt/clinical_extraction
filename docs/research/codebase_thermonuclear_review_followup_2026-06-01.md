# Codebase Thermonuclear Review Follow-Up

Date: 2026-06-01

## Purpose

This report records the important component changes made after
`docs/research/codebase_thermonuclear_review_2026-06-01.md`.

The original review found that the project's research instincts were strong but
that the source architecture was absorbing too much behavior too quickly. The
follow-up work was deliberately behavior-preserving: fix the red test surface,
make attribution boundaries mechanical, split large concept warehouses, improve
static checks, and make experiment artifacts easier to navigate.

This is a reference map for future work. It is not a new benchmark claim.

## Verification State

After the follow-up consolidation and Gan 2026 package reorganization, using
macOS/Linux shell activation:

```shell
source .venv/bin/activate
python -m pytest -q
python -m mypy src
python -m ruff check .
```

On Windows PowerShell, activate with `.\.venv\Scripts\Activate.ps1` before the
same `python -m ...` commands.

Current result:

- Pytest: 606 passed.
- Mypy: no issues across 74 source files.
- Ruff: passed.

For comparison, the original review recorded 578 passing tests, 4 failing schema
repair tests, and 31 mypy errors.

## Package Organization

The Gan 2026 package now follows the package-boundary decision in
`docs/decisions/0004-gan2026-package-organization.md`.

Top-level task contracts remain at:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/data.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/labels.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/evaluate.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/normalize.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/pipeline_v1.py`

Implementation modules now live under:

- `contract/`
- `deterministic/`
- `selected_evidence/`
- `llm/`
- `hybrid/`
- `reports/`
- `experiments/`
- `cli/`

Why this matters:

The directory structure now mirrors the research decomposition. Someone reading
the code can tell whether a component owns benchmark contract, deterministic
rules, selected-evidence derivation, LLM prediction behavior, hybrid behavior,
reporting, artifacts, or CLI orchestration before opening the file.

## Component Changes

### Shared Schema Repair

New home:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/schema_repair.py`

What changed:

- Shared schema repair is alias-only again.
- `repair_decision_payload()` no longer adds broad clinical defaults such as
  unknown target/window/rationale fields.
- Parser-owned defaults moved to the parser that owns the schema, especially
  the hybrid adjudicator parser.

Why it matters:

This fixed the original P0 failure. Shared model-output repair now repairs
shape and aliases without silently changing clinical content. That keeps
parse-failure and schema-robustness summaries more trustworthy.

### Gan Label Contract And Gold Policy

New homes:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/label_parser.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/gold_policy.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/benchmark_prediction_repair.py`

Top-level compatibility/contract surface:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/normalize.py`

What changed:

- Gan label grammar, yearly/monthly conversion, sentinels, clean scorer-facing
  gold policy, and benchmark prediction repair were split out of
  `normalize.py`.
- `normalize.py` remains the public normalization surface, but it no longer owns
  every underlying concept.

Why it matters:

The original review warned that label parsing, benchmark repair, gold policy,
and selected-evidence derivation sharing one file made attribution blurry.
Those concepts now have named homes, making it easier to distinguish clinical
state, benchmark formatting, and scorer-facing policy.

### Deterministic V1

New homes:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/deterministic/`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/deterministic/rules/`

Important modules:

- `deterministic/deterministic_extraction.py`
- `deterministic/deterministic_rate_extraction.py`
- `deterministic/deterministic_selection.py`
- `deterministic/deterministic_candidate_pruning.py`
- `deterministic/deterministic_text.py`
- `deterministic/deterministic_frequency_tokens.py`
- `deterministic/deterministic_rate_terms.py`
- `deterministic/deterministic_rate_distractors.py`
- `deterministic/temporal.py`
- `deterministic/rule_metadata.py`

What changed:

- `pipeline_v1.py` became a shell for schemas, run orchestration, candidate
  event materialization, normalization, and final selection wiring.
- Deterministic candidate discovery, rate extraction, pruning, evidence text
  cleanup, temporal helpers, rate vocabulary, distractor filtering, and final
  selection moved into owned modules.
- Rule registries remain explicit and ablatable under `deterministic/rules/`.

Why it matters:

Deterministic V1 remains frozen as the `rules_only_v1` comparator. The split did
not bless new deterministic behavior; it made the existing frozen behavior more
inspectable and safer to use as a baseline or diagnostic source.

### Selected-Evidence Derivation

New home:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/selected_evidence/`

Important modules:

- `selected_evidence/selected_evidence_derivation.py`
- `selected_evidence/selected_evidence_rate.py`
- `selected_evidence/selected_evidence_cluster.py`
- `selected_evidence/selected_evidence_monthly_diary.py`
- `selected_evidence/selected_evidence_window.py`
- `selected_evidence/selected_evidence_text.py`

What changed:

- Selected-evidence monthly diary parsing, cluster derivation, count-over-window
  logic, year-to-date elapsed-month derivation, rate idioms, and shared text
  formatting were split into focused helpers.
- `selected_evidence_derivation.py` remains the orchestration surface for
  deriving Gan-compatible labels from model-selected evidence.

Why it matters:

Selected-evidence derivation is central to attribution risk. The stronger
structured-LLM metrics depend on deterministic work over selected evidence, so
that work now has a clearly named package rather than being hidden inside
normalization.

### LLM-Only Structured Events

New home:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_only_structured_events.py`

Related modules:

- `llm/llm_structured_repair_families.py`
- `llm/llm_structured_temporal.py`
- `llm/llm_structured_monthly_diary.py`
- `llm/llm_only_structured_events_repair_ablation.py`
- `reports/llm_structured_events_report.py`

What changed:

- Named repair modes were introduced:
  `raw_model`, `strict_format`, `clean_scorer_facing`,
  `selected_evidence_derivation`, `hybrid_full_stack`, and `custom`.
- Structured-events repair ablations now report the resolved mode.
- Semantic repair families such as usual interval, breakthrough, non-epileptic
  override, residual jerk, post-change burst, dated sequence, and elapsed
  anchor moved out of the runner.
- Report rendering moved to `reports/llm_structured_events_report.py`.

Why it matters:

The original review flagged repair attribution as a central scientific risk.
The code now makes it harder to accidentally describe full-stack deterministic
repair as a clean LLM-only result.

### LLM Claim-Table Selector

New home:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_only_claim_table_selector.py`

Related modules:

- `llm/claim_table_parser.py`
- `reports/claim_table_report.py`

What changed:

- Claim-table Pydantic records, model-shape/schema repair, and selected-claim
  validation moved into `claim_table_parser.py`.
- Markdown report writing and review-table formatting moved into
  `reports/claim_table_report.py`.
- The runner now focuses on prompt, run, scoring, and orchestration.

Why it matters:

The selector is a useful diagnostic but not a promotion candidate after
full-validation collapse. Keeping parser, runner, and report responsibilities
separate makes the next v5 redesign easier to reason about.

### Hybrid Rules-Candidates LLM Adjudicator

New home:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/hybrid/hybrid_rules_candidates_llm_adjudicator.py`

Related modules:

- `hybrid/hybrid_adjudicator_parser.py`
- `reports/hybrid_adjudicator_report.py`

What changed:

- Hybrid adjudicator Pydantic decision records, parser-owned defaults,
  model-shape/schema repair, final-label repair, and scorable-label validation
  moved into `hybrid_adjudicator_parser.py`.
- Hybrid Markdown reports moved into `reports/hybrid_adjudicator_report.py`.
- The hybrid runner now owns prompt/run/scoring orchestration and deterministic
  candidate packaging.

Why it matters:

Hybrid v0.1 is a revise candidate, not a holdout candidate. This split makes
the semantic ownership explicit: deterministic candidate generation and LLM
adjudication both matter, and parser repair is not hidden in the run loop.

### Shared LLM Experiment CLI

New home:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/cli/llm_pipeline_cli.py`

Entry point:

- `gan2026-llm-experiment`

What changed:

- Routine LLM and hybrid experiments share one CLI with `--pipeline` selection.
- The CLI enforces the validation ladder: validation runs above 250 rows require
  `--escalation-reason`.
- The `pyproject.toml` console-script entry now points to the `cli/` package.

Why it matters:

This directly addresses the review's validation-ladder guardrail. Full
validation should be rare and justified, not an accidental default.

### Report Writers

New home:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/reports/`

Important modules:

- `reports/base.py`
- `reports/claim_table_report.py`
- `reports/hybrid_adjudicator_report.py`
- `reports/llm_structured_events_report.py`

What changed:

- Common report provenance/rendering helpers moved to `reports/base.py`.
- Pipeline-specific Markdown report writers moved out of runner modules.

Why it matters:

Report wording is part of claim discipline. Moving report rendering out of
pipeline code makes it easier to review whether the text matches the actual
component ownership and repair mode.

### Experiment Artifacts And Registry

New home:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/experiments/`

Important modules:

- `experiments/artifact_io.py`
- `experiments/run_metadata.py`
- `experiments/run_registry.py`
- `experiments/run_registry_report.py`
- `experiments/ablation_analysis.py`
- `experiments/prompt_devset.py`
- `experiments/error_analysis.py`
- `artifact_analysis/architecture_component_ablation.py`
- `artifact_analysis/claim_table_component_ablation.py`
- `artifact_analysis/projection_arbitration_ablation.py`
- `artifact_analysis/boundary_state_graph_replay.py`
- `artifact_analysis/seizure_free_duration_node_replay.py`
- `artifact_analysis/seizure_free_duration_projection_ablation.py`

Artifacts:

- `experiments/registry.jsonl`
- `experiments/RUN_INDEX.md`
- `experiments/README.md`

What changed:

- Shared row-oriented JSONL writing moved into `artifact_io.py`; raw-output
  reuse loading and saved-output replay analyses now live under
  `artifact_analysis/`.
- Run registry entries are typed, JSONL-backed, validate duplicate IDs and
  artifact paths, and render to a Markdown index.
- Component-ablation tooling now normalizes rules-only, LLM-only, and hybrid
  artifacts into comparable condition summaries.

Why it matters:

The original review warned that "latest" was becoming ambiguous in
`experiments/`. The registry does not index every historical file, but it gives
canonical/high-signal runs a durable navigation surface with decision status,
repair config, cache/reuse source, metrics, and conservative claim notes.

### Core Boundary

Relevant file:

- `src/clinical_extraction/core/schemas.py`

What changed:

- `SeizureEvent` was removed from `core`.
- `core/` remains task-neutral.

Why it matters:

This protects the intended architecture: general clinical extraction primitives
belong in `core`, while Gan/seizure-specific schemas and policy belong under
the task package.

### Static Typing And Test Surface

What changed:

- Mypy went from 31 errors to clean.
- The test suite now passes after the schema repair and reorganization.
- Focused tests were updated to use the new package boundaries.

Why it matters:

The next phase will continue moving code by ownership. A clean static/type
baseline and green test suite make those moves much less fragile.

## Current Boundary Map

Use this map when deciding where new work belongs:

| Work type | Preferred home |
| --- | --- |
| Gan label parsing, sentinel grammar, benchmark repair | `gan2026/contract/` |
| Scorer-facing normalization public surface | `gan2026/normalize.py` |
| Rules-only extraction and deterministic helper logic | `gan2026/deterministic/` |
| Rule registries and ablation config | `gan2026/deterministic/rule_metadata.py` and `gan2026/deterministic/rules/` |
| Derivation from model-selected evidence | `gan2026/selected_evidence/` |
| LLM-only runners and LLM structured repair helpers | `gan2026/llm/` |
| Deterministic-plus-LLM semantic pipelines | `gan2026/hybrid/` |
| Markdown/provenance report rendering | `gan2026/reports/` |
| Artifact IO, run registry, prompt devset, ablations, error analysis | `gan2026/experiments/` |
| Routine command-line experiment harnesses | `gan2026/cli/` |

## Remaining Caveats

- The run registry is selective. It indexes canonical/high-signal runs first,
  not every historical artifact.
- Deterministic V1 is still a frozen comparator with known validation-overfit
  risk. The reorganization made it easier to inspect; it did not make it more
  general.
- Structured-events high scores remain repair-heavy hybrid diagnostics unless a
  named mode and ablation demonstrate otherwise.
- The package layout is now cleaner, but future changes must still avoid
  sneaking semantic benchmark repair into code described as LLM-only.

## Suggested Future Use

Before adding a new Gan 2026 feature, ask:

1. Is this contract, deterministic, selected-evidence, LLM, hybrid, report, or
   artifact behavior?
2. Does it change scoring, repair semantics, split policy, prompt behavior, or
   claim language?
3. Which focused test should fail if the boundary is crossed?
4. Which run metadata field or report section will make the component ownership
   visible?

If the answer is not clear, write a small design note before adding code.
