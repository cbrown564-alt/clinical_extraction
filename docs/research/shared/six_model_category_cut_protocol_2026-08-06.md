# Protocol: six-model performance by gold task categories

Date: 2026-08-06; ExECT subtype correction predeclared 2026-08-08
Status: answered; extended 2026-08-08 with rules surface and corrected ExECT subtypes
Parent framework: [task-shape framework](task_shape_framework_2026-08-06.md)

## Primary question

### ExECT correction (2026-08-08)

The primary ExECT categories are **gold-defined subtypes within each clinical
family**, not whole-letter mixtures such as `multi_mention_with_sf`. The four
families remain the score boundary from Decision 0046, but each family is cut
by the kind of fact it asks the extractor to recover:

- Diagnosis: gold `DiagCategory` (`Epilepsy`, `MultipleSeizures`,
  `SingleSeizure`);
- SeizureFrequency: numeric cadence, count in a named window, qualitative
  frequency change, and the smaller supported attribute shapes;
- Prescription: complete regimen versus `As_Required` rescue;
- Investigations: modality and result state (`MRI` / `CT` / `EEG` ×
  normal / abnormal / unknown).

Family absence remains a secondary false-positive / exact-empty lens in the
whole-family error roll-up.
Whole-letter family-count and multiplicity buckets may remain in the artifact
as secondary workload descriptors, but they must not drive x/y/z conclusions,
the error catalogue, or representative-example coverage.

The corrected development score uses the gold subtype to select permitted
development letters, then applies the unchanged `clinical_headline` scorer to
the named family only on those letters. Predicted subtype attributes do not
define cohort membership and no new scoring requirement is introduced.
Categories may overlap because one letter can contain several subtypes; no
facts from another clinical family enter the category score.

Required artifact fields are family, subtype, gold mention count, letter count,
scorer counts, precision/recall/F1 for rules/LLM/hybrid, and six-model lens or
single-system band. The existing `dev140` rows and retained prediction fields
are replayed without calls. No `test60` rows are opened.

Stop when all observed gold subtypes are inventoried, primary subtype tables
are generated for all three methods, whole-letter buckets are visibly
secondary, and focused tests pin subtype classification and score isolation.
The result is a development answer only and does not rewrite Decision 0046
headline fills or authorize subtype holdout claims.

On gold-defined task categories, which parts do **all** six models complete
well (**x**), which parts **separate** models (**y**), and which parts are
**shared difficulty** (**z**)—and how does the single-system **rules-only**
method score on the same categories?

This fills the lenses defined in the task-shape framework. It does not invent
new gold, scorers, prompts, or rules.

## Why it matters

The six-model comparison already shows a modest absolute holdout band. Without
category cuts, that looks like uniform competence. Category cuts show whether
the band is carried by an easy mass, whether ranks are category-shaped, and
where every model still fails. Adding rules-only separates “post-LLM hybrid
rules create competence” from “the independent deterministic method already
owns the category.”

## Data, split, row policy

| Track | Split | Row policy | Prediction sources |
| --- | --- | --- | --- |
| Gan 2026 | `dev750` (`validation`) | development review permitted | `rules` = retained three-way deterministic JSONL; `llm_only` JSONL in `experiments/gan2026_six_model_validation_20260718/`; `llm_with_rules` = matched v0.5 attribution + current-floors changed-row patch |
| ExECTv2 | `dev140` | development review permitted | `rules` = regenerated four-family letter scores (`scripts/build_exectv2_rules_only_four_family_letter_scores_dev140.py`); assembled JSONL `predicted_mentions` (llm_with_rules); `raw_lane_mentions` scored with the clinical-headline helper (llm surface) |
| Holdout | `test450` / `test60` | **aggregate-only** | No sealed row files opened. Holdout discussion uses panel aggregates + gold mix only |

No new model calls. No locked-test row inspection. ExECT rules-only letter
scores are a no-call deterministic regeneration.

## Categories

Use regenerable gold categories from
`scripts/build_gold_task_taxonomy_inventories.py` and the shared within-family
classifier:

- Gan: `a_priori_buckets` (+ optional `boundary_band`)
- ExECT primary: Diagnosis `DiagCategory`; SF attribute shape; Prescription
  regimen type; Investigation modality × result state.
- ExECT secondary only: `a_priori_letter_buckets`, Diagnosis multiplicity, SF
  presence, and other cross-family composition descriptors.

## Metrics

| Track | Method surfaces | Metric |
| --- | --- | --- |
| Gan | `rules`, `llm`, `llm_with_rules` | Purist accuracy on rows in the bucket |
| ExECT | `rules`, `llm` (raw lane via clinical-headline helper), `llm_with_rules` (final predicted mentions) | Named-family clinical fact F1 on letters selected by the gold subtype; whole-family and four-family roll-ups secondary |

ExECT `llm_with_rules` must reproduce Sol `dev140` panel overall `0.8920`.
ExECT `llm` and ExECT `rules` use the same clinical-headline helper for
surface parity; absolute levels may differ slightly from architecture ladders
(`/panel raw_lane_score`; Decision 0046 `headline_target` 0.8160). Relative
bucket ordering under one fixed helper is the claim object for category cuts.
Decision 0046 primary fills are unchanged. The subtype classifier selects the
gold cohort; it does not add predicted subtype attributes to the scorer.

## x / y / z assignment rule (six-model surfaces)

Apply the same thresholds independently on **`llm` and `llm_with_rules`**, for
each bucket with denominator ≥ 20 (Gan rows) or ≥ 10 letters (ExECT):

| Lens | Rule |
| --- | --- |
| **x** | minimum model score ≥ 0.85 and (max − min) ≤ 0.08 |
| **z** | maximum model score ≤ 0.75 |
| **y** | neither x nor z (models separate, or mid band) |

## Single-system bands (rules surface)

`rules` is one deterministic method, not six models. Do **not** assign x/y/z.
For the same denominator floors, report absolute score and:

| Band | Rule |
| --- | --- |
| **high** | score ≥ 0.85 |
| **floor** | score ≤ 0.75 |
| **mid** | neither |

Buckets below the denominator floor are reported but not assigned a band.
Thresholds are descriptive cut-points for this study, not clinical standards.

## Required outputs

1. Machine artifact with per-model × method × bucket scores and lens labels
   for `llm` and `llm_with_rules`, plus single-system rules bucket/family
   scores and high/mid/floor bands.
2. Narrative report answering x / y / z for Gan buckets and ExECT within-family
   subtypes on llm and hybrid, with a three-way rules / llm / llm_with_rules
   side-by-side.
3. Short note on whether gold mix alone could explain holdout gaps (no row
   holdout cuts).

## Stop rule

- **Answer** if x/y/z can be stated with regenerable numbers on development
  for llm and llm_with_rules, and rules-only category scores are regenerable.
- **Blocked** only if retained prediction files cannot reconstruct panel
  development aggregates for llm_with_rules (and Gan llm), or ExECT rules
  letter scores cannot be regenerated.

## Claim boundary

- Development category competence, not sealed holdout category competence.
- Not a rewrite of Decision 0046 method fills.
- Not cross-task numerical comparison of Gan Purist vs ExECT F1.
- DeepSeek Gan `llm` `dev750` remains pre-0731 (panel note).
- Rules-only bands are single-system competence, not multi-model agreement.
