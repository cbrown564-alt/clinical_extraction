# Gan is the dissertation paper

Date: 2026-08-28
Status: current
Owner: [paper keep-set](../README.md)
Related: [holdout is aggregate-only](holdout-is-aggregate-only.md),
[living comparison contract](living-comparison-contract.md),
[claims](../claims.md)
Feasibility: [Gan inventory feasibility](../../research/gan2026/gan_inventory_feasibility_dev750_n100_2026-08-28.md)

## Decision

The dissertation paper cites **Gan 2026 only**. ExECTv2 is a later
paper. It is not a second evaluated task, a second headline table, or
a second locked-total column in this manuscript.

That cut is a writing and claim-scope choice. It does not delete ExECT
code, protocols, or `paper_experiments/` cells. Those remain repository
evidence for the later paper. They are not dissertation results.

Recent commits through 2026-08-28 still treated both tasks as
paper-primary: Gemini five-cell grids on both holdouts, the ExECT
cell-3 six-model roster, the three-stage ExECT rules promotion, and
draft results that place Gan Purist scores beside ExECT four-family
micro F1. This decision supersedes that dual-task paper identity. Those
ExECT artifacts stay valid for the later paper; they stop being
dissertation citations.

## Why

The two public golds answer different questions and use different
scorers. Gan asks for one current seizure-frequency state (Purist
micro-F1). ExECT asks for a complete four-family clinical inventory
(4-family micro F1). Scores do not move between tasks.

Keeping both as headline evaluations forced a compressed results
section and a cross-task claim the dissertation no longer needs to
carry. Focusing the manuscript on Gan leaves room for a fuller Gan
reading: the five-cell role allocation, class-level errors, and a
descriptive account of the broader clinical content in the same
synthetic letters.

ExECT remains the designed inventory schema and the planned later
evaluation. It is not abandoned. It is deferred.

## Consequences

- Dissertation methods, results, claims, and tables cite Gan splits
  (`dev750`, locked `test450`), the Gan five-cell grid, and the Gan
  cell-3 roster. They do not cite ExECT `dev140` / `test60` locked
  totals as dissertation performance.
- Draft keep-set files that still say “both tasks” or place ExECT
  columns beside Gan are stale for dissertation writing. Rewrite them
  from this decision; do not copy the dual-task sentence from
  [claims](../claims.md) or [results](../sections/results.md) into the
  manuscript.
- ExECT holdout stays sealed. Deferral is not permission to inspect
  `test60` rows, retune ExECT from holdout, or move ExECT scores onto
  Gan.
- Gemini remains the cited model for the Gan evaluation. Companion
  models stay cell-3 companions on Gan only.
- A later ExECT paper may reuse the living inventory cells. It starts
  from those owners, not from a dissertation rewrite of ExECT scores.

## Descriptive clinical-inventory feasibility study

The freed results space is used, in part, for a **descriptive
feasibility study** on Gan synthetic letters. It sits alongside the
evaluated seizure-frequency classification task. It is not a second
accuracy evaluation.

### Purpose

Show the broader clinical information available in the Gan synthetic
letters: whether an ExECT-style clinical-inventory schema can produce
structured descriptions of diagnoses, medicines, investigations, and
seizure-frequency statements from the same corpus.

### Design

- Select a prespecified, reproducible sample of **100** Gan synthetic
  letters.
- Draw that sample from **permitted** letters only (`dev750`). Do not
  use `test450`. The study will show letter-level examples; holdout
  row inspection remains forbidden.
- Apply the **frozen** clinical-inventory extraction pipeline and
  schema. Name the program, schema, and commit in the study protocol
  before the sample is drawn.
- Do not tune the pipeline on this sample after selection.
- Report only descriptive summaries of the extracted output.
- Use a small number of synthetic examples to illustrate multi-fact
  outputs.

### Reported outputs

For each major fact family—diagnoses, medications, investigations, and
seizure-frequency statements—report:

| Measure | Purpose |
| --- | --- |
| Letters containing at least one extracted fact | How often the schema yields each kind of information |
| Total extracted facts | Overall output volume |
| Median and range of facts per letter | Richness of individual-letter inventories |
| Common extracted subtypes | Clinical interpretability of the output |

A compact table can show these summaries, followed by two or three
synthetic examples that display the source letter at a high level and
its resulting structured inventory.

### Claim boundary

The study will not report precision, recall, accuracy, or clinical
validity. The Gan corpus has no expert reference labels for these
broader facts.

Its contribution is to show the range and structure of information
that can be represented and extracted from the synthetic letters, and
to motivate later expert annotation and evaluation on real clinical
correspondence.

Do not present the feasibility counts as ExECT benchmark performance,
as transfer of ExECT `test60` scores, or as evidence that the
inventory is clinically correct on Gan letters.

## What this does not change

- Gan `test450` remains locked and aggregate-only.
- Gan scoring, codebook encode, and five-cell identity stay on the
  existing Gan owners.
- ExECT inventory scoring and cells stay on their existing owners for
  the later paper.
- Component attribution, replay, and conservative claims still apply.
