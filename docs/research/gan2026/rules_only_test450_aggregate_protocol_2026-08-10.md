# Protocol: Gan 2026 Rules-Only test450 Aggregate

Date: 2026-08-10
Status: **Gate A PASSED 2026-08-11 against the refreshed reference — `test450`
still NOT run.** See the original
[Gate A failure](rules_only_validation750_gate_a_2026-08-10.md), the
[reference refresh](rules_only_reference_refresh_2026-08-10.md) that
resolved it, and the
[Gate A](rules_only_validation750_gate_a_2026-08-10.md)
that confirms current HEAD reproduces the refreshed reference exactly (0
label diffs across 750 rows). Gate B (holdout execution) has not been
entered; it requires a separate explicit step under this protocol's
sealed-rows procedure.
Dataset: Gan 2026 Seizure Frequency (`test450` locked split)

## Primary question

What is the Purist accuracy of the Gan rules-only pipeline (no model calls) on
the locked `test450` split?

This is a fill for a single missing cell, not a comparison study. Paper
provenance owns Gan `test450` results for `llm_only` (Sol 0.74) and
`llm_with_rules` (Sol 381/450 = 0.85), and owns rules-only on `validation750`
only. The rules-only holdout cell is empty and is explicitly named as absent in
two current source documents:

- `docs/research/paper/gan_story_2026-08-10.md:21`
- `docs/research/paper/evidence_exploration_brief_2026-08-09.md:533`

ExECT already owns the equivalent cell (`test60` rules-only four-family
clinical-fact F1 `0.7154`, artifact
`experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260801.json`),
so this study makes the two tasks symmetric in what they can show.

## Why this study is cheap and why that does not make it free

The rules-only lane makes zero model calls
(`gan2026_rules_reference.model: "none (deterministic rules pipeline; no LLM
calls)"`). The cost is therefore not tokens; it is one consumption of the locked
`test450` split. That is the scarce resource this predeclaration protects.

## Ruleset identity: a constraint, not a defect to fix

The retained rules-only reference is
`prompt_program_version: three-way phase-1 deterministic canonical pipeline,
2026-06-07`. The Gan `llm_with_rules` `test450` line is a no-call replay through
the final 2026-07-31 ruleset.

These are **not** the same ruleset, and they cannot be made the same. The
2026-07-31 and 2026-08-10 rule work (`repair.breakthrough`,
`repair.typical_over_ytd`, `repair.non_epileptic`, cluster-burden tuning) is
implemented in `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py`
and operates on LLM-produced structured events. The rules-only lane
(`orchestration/rules.py` → `deterministic_canonical_stages.py`) has no such
stages and never did. There is no configuration under which rules-only runs "the
final ruleset."

Consequence, predeclared before seeing any number: the resulting figure is a
**standalone rules-only holdout result**. It is not a ruleset-matched
counterfactual for the hybrid row, and the difference between them is not a
measurement of what the final ruleset contributed.

## Scope and fixed conditions

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 Seizure Frequency |
| Holdout split | `test450` (locked, aggregate-only, 450 notes) |
| Split manifest | `data/Gan (2026)/splits/gan2026_split_v1.json` |
| Method | `deterministic_canonical_pipeline` (`PIPELINE_METHOD` → `rules_only`) |
| Entry point | `runners/split.py:run_split` → `_run_deterministic_split` |
| Configuration | `PipelineConfiguration(architecture="deterministic_canonical_pipeline")` with default `AblationConfig()` — all rule groups and portability classes enabled, `disabled_rule_ids` empty |
| Models | None. Zero LLM calls. `model` field is inert for this lane and is recorded as `none`. |
| Primary metric | Purist label accuracy, count out of 450 |
| Secondary metrics | Pragmatic label accuracy; rendered-row count; evidence-valid row count |
| Runs | Exactly one execution against `test450` |
| Row policy | `aggregate_only` |

## Gate A — replay parity on the open split (precondition)

`test450` is not touched until this passes.

The rules-only lane has been through several structural refactors since
2026-06-07 (`c3a6fbb7`, `024b2c5a`, `234cd62e`, `887961e3` among others). Current
HEAD is therefore not assumed to be behaviourally identical to the retained
reference.

Run current-HEAD rules-only on `validation750` (an open split, row inspection
permitted) and compare against the retained reference:

| Parity target | Source | Value |
| --- | --- | --- |
| Purist correct of rendered | `retained_evidence_manifest.json` → `gan2026_rules_reference.result_summary` | 688 |
| Rendered rows | same | 741 |
| Evidence-valid rows | same | 750 |
| Purist correct (verification block) | same cell, `verification.expected` | 697 |
| Pragmatic correct (verification block) | same cell, `verification.expected` | 704 |

The manifest carries two Purist figures against different denominators
(`688` of `741` rendered vs `697` of `750`). Reconciling those two accountings is
part of Gate A, and the `test450` artifact must state which denominator it
reports. Publishing a holdout number whose denominator convention is unresolved
is a failure mode this gate exists to prevent.

**Gate A passes** if current HEAD reproduces the retained validation750 figures
exactly on all five rows above.

**If Gate A fails**, `test450` is not run under this predeclaration. The
divergence is investigated and reported on `validation750` alone, and a fresh
predeclaration is written for whatever configuration is then proposed. Refactor
drift is diagnosed on the open split; it is never diagnosed on the holdout.

## Gate B — holdout execution

One run. `split="test"`, 450 rows.

`_run_deterministic_split` emits per-row `source_row_index`, `diagnostics`,
`final_label`, and `reference.gold_label`. Under
`scripts/check_locked_aggregate_safety.py` these are all forbidden in a public
artifact (`FORBIDDEN_KEYS`, plus any `rows` collection). Therefore:

- The row-level JSONL is written to
  `scratch/holdout/gan2026_rules_only_test450_20260810/` and sealed — recorded in
  the public artifact by path, `sha256`, and byte count only, following the
  ExECT `test60` `sealed_predictions` pattern.
- The public artifact contains aggregates only.
- No row text, row index, label, diagnostic, or failure case from `test450` is
  read, quoted, summarized, or used to motivate any subsequent change.
- `scripts/check_locked_aggregate_safety.py` is extended with the new artifact
  path and must pass before the result is cited anywhere.

## Predeclared reporting

The number is reported as-is. There is no confirmation criterion, no threshold,
and no pass/fail — this study fills a descriptive cell and cannot be "failed" by
an unfavourable value.

Predeclared before execution, to remove any post-hoc framing freedom:

- **If rules-only lands well below the Sol hybrid `test450` row**, that is
  reported as the gap between two differently-configured lanes, with the ruleset
  asymmetry stated in the same sentence.
- **If rules-only lands at or above the Sol LLM-only `test450` row (0.74)**, that
  is reported plainly and is not softened, re-run, or supplemented.
- **If rules-only lands close to the hybrid row**, that is reported plainly and
  does not license a claim that the models are unnecessary — the hybrid row
  carries repair stages the rules-only lane does not have, so the comparison is
  not an ablation.
- **Development-to-holdout movement** relative to validation750 is reported as a
  single descriptive delta. It is not attributed to overfitting, generalization,
  or split difficulty without a separate study.

## What this result may and may not support

May support:

- A Gan rules-only `test450` Purist figure, aggregate-only, at the same
  evidentiary altitude as the existing Gan `test450` rows.
- A three-method Gan holdout row set (rules-only / LLM-only / LLM-with-rules)
  in the parallel two-task view, provided each bar names its ruleset identity.
- Removal of the "no comparable rules-only fill" caveats at
  `gan_story_2026-08-10.md:21` and
  `evidence_exploration_brief_2026-08-09.md:533`.

May not support:

- Any statement that the deterministic stages "contribute" a measured amount to
  the hybrid result. That is a leave-one-stage-out question and this is not that
  design.
- Revision of C16, C18, C19, or Decision 0046 fills.
- Promotion of the Gan matched-method development result over the rules-only
  comparator — `docs/canon/10_paper_provenance.md:94` blocks this for reasons
  this study does not address.
- Reopening Gan `llm_with_rules` tuning. `10_paper_provenance.md:102` requires a
  separate predeclared study for that, and this result is not the trigger.

## Artifacts and outputs

| Kind | Path |
| --- | --- |
| Public aggregate artifact | `experiments/gan2026_rules_only_test450_20260810.json` |
| Sealed row-level predictions | `scratch/holdout/gan2026_rules_only_test450_20260810/rows.jsonl` (not committed) |
| Gate A parity artifact | `experiments/gan2026_rules_only_validation750_parity_20260810.json` |
| Report | `docs/research/gan2026/rules_only_test450_aggregate_2026-08-10.md` |
| Runner | `scripts/build_gan2026_rules_only_test450_aggregate.py` |
| Safety check | `scripts/check_locked_aggregate_safety.py` (extended with the new path) |

Public artifact schema: `gan2026.rules_only.test450.v1`, carrying `protocol`,
`split`, `row_count`, `row_policy`, `method` (architecture, ablation config,
model `none`), `purist` / `pragmatic` counts and rates with a named denominator,
`rendered_rows`, `evidence_valid_rows`, `sealed_predictions`, and
`claim_boundary`.

## Registry and manifest updates on completion

### The sibling cell is an evidence package, not a seventh reference cell

Decided before execution. `gan2026_rules_reference` is not extended: its
`row_inspection_policy` is `validation750_rows_permitted` and its
`claim_boundary` is validation-scoped, and widening either in place would
silently grant holdout rows a permission they must not have.

The sibling is registered as an **evidence package**, not as a reference cell,
for two structural reasons:

1. **Reference cells carry executable replay.** All six existing cells have a
   `verification` block that `scripts/verify_reference_evidence.py` runs against
   a committed row-level artifact — for Gan, `replay: gan_saved_comparisons`
   over a `git_path` JSONL. This study's rows are sealed under
   `scratch/holdout/` and are never committed, so no such replay can exist. A
   reference cell with an unrunnable verification block would be a false
   guarantee.
2. **The reference-cell list is inside the architecture freeze.**
   `architecture_freeze.reference_cell_ids` enumerates exactly six ids under
   `freeze_id: retained_comparison_architecture_20260720`. Adding a seventh
   mutates the frozen object. The freeze's own `mutation_policy` reserves that
   for semantic prompt, scorer, split, repair, route, or component-graph
   changes requiring a new freeze ID and complete replay. This study is none of
   those and should not force a re-freeze.

The precedent is `gan2026_holdout_quality_and_efficiency_subject`, already in
`evidence_packages` with `split: test`, `row_count: 450`,
`row_inspection_policy: aggregate_only`, hashed artifacts, and no `verification`
block. The new cell follows that shape exactly.

Proposed id: `gan2026_rules_only_holdout_subject`.

| Field | Value |
| --- | --- |
| `task` | `gan2026` |
| `architecture_family` | `rules_only` |
| `split` / `row_count` | `test` / `450` |
| `row_inspection_policy` | `aggregate_only` |
| `model` | `none (deterministic rules pipeline; no LLM calls)` |
| `cache_replay_mode` | `no-call deterministic execution; aggregate-only holdout summary` |
| `prompt_program_version` | resolved by Gate A — the ruleset identity current HEAD is confirmed to reproduce |
| `story_ids` | `S1`, `S2`, `S6` (matching `gan2026_rules_reference`) |
| `artifacts` | the public aggregate JSON and this protocol, hashed as `git_path`; sealed rows referenced by hash only |
| `claim_boundary` | standalone rules-only holdout figure; not ruleset-matched to the `llm_with_rules` row; not a stage-contribution measurement |

The existing `gan2026_rules_reference` cell gains a cross-reference to the
sibling id and nothing else.

### Freeze compatibility

`architecture_freeze.execution_policy.model_calls` states the freeze does not
authorize new model calls. This study makes zero, so it is compatible without a
new freeze ID. That compatibility depends entirely on Gate A confirming HEAD
reproduces the retained rules-only behaviour; if Gate A fails, HEAD has drifted
from the frozen architecture and the freeze question reopens as a separate
matter.

### Remaining updates

- New row in `experiments/registry.jsonl` with `split: test`, `row_count: 450`,
  `architecture_family: rules_only`, `model_role: none`, `mode: no-call`.
- New headline row in `docs/canon/10_paper_provenance.md`.
- Caveat removal in the two source documents named above.
- `scripts/check_retained_evidence_manifest.py` and
  `scripts/check_locked_aggregate_safety.py` must both pass.
