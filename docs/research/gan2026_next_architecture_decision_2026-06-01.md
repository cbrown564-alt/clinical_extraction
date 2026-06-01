# Gan 2026 Next Architecture Decision

Date: 2026-06-01

This is a development-planning decision for `gan2026_split_v1`. It is not a
holdout result or benchmark-comparison claim.

## Decision

Select the section-and-claim-table architecture as the next LLM-first comparison
surface.

The first implementation should be a deliberately small flat claim table, not a
full graph. The LLM should produce source-near seizure-frequency claims with
section or zone, evidence, temporality, assertion status, semiology, frequency
surface, anchor text, and uncertainty. A separate query step should choose the
Gan-facing answer from that table while preserving the claim rows used for the
decision.

## Why This Branch

The clean attribution ladder shows that the current structured selector has
excellent evidence substrings but weak raw clinical selection on the first 50
validation rows:

| Condition | Purist | Pragmatic | Parse/schema/label failures |
| --- | ---: | ---: | ---: |
| Raw model selection | 34 / 50 = 0.6800 | 36 / 50 = 0.7200 | 10 |
| Strict format-only | 41 / 50 = 0.8200 | 43 / 50 = 0.8600 | 3 |
| Frozen clean policy | 43 / 50 = 0.8600 | 46 / 50 = 0.9200 | 0 |

The remaining development question is therefore not just label formatting. It is
whether a different task decomposition can expose temporal, conflict, and
evidence-state decisions before they collapse into one final label.

The section-and-claim-table branch keeps the prediction-bearing reasoning on the
model side while making the intermediate clinical state inspectable. It is a
better next LLM-first comparison than an LLM-extractor plus deterministic
selector, because that alternative immediately makes deterministic selection a
prediction-bearing component and would shift the claim to an explicit hybrid
architecture.

## Experiment Unit

Hypothesis: a flat section-and-claim table will make temporal and conflict
failures more inspectable than direct structured final-label selection, while
preserving exact evidence traces and keeping deterministic code limited to schema
validation, evidence checks, Gan-compatible formatting, arithmetic over selected
facts, and scoring.

Minimal implementation:

- Add a new claim-table pipeline separate from the current structured selector.
- Keep deterministic V1 out of the prompt and out of candidate generation.
- Emit claim rows before the final Gan query.
- Record the final query's selected claim IDs and rationale.
- Reuse the shared Gan LLM CLI runner so split, cache, reuse, and report metadata
  stay comparable.

Data surface: validation prefix only on `gan2026_split_v1`.

Initial run surface: 25 validation rows. Do not run 50 rows until the 25-row
artifact shows stable schema, exact evidence behavior adequate for row review,
and interpretable failures.

Scorer: Gan-compatible Purist first, Pragmatic as side-car.

Comparator: `gan2026_clean_policy_freeze_ladder_v0` and the current structured
LLM raw/strict/clean conditions, especially the 50-row first-prefix result.

## Claim And Repair Boundary

Claim type: `llm_first` diagnostic candidate.

Prediction-bearing component: the model-produced claim table plus model query
selection. Deterministic code may reject invalid structures, validate evidence
substrings, normalize scorer-compatible label grammar, and do arithmetic over a
selected fact. It may not introduce deterministic temporal selection, evidence
state reclassification, diary reconstruction, cluster reconstruction, or
seizure-free/no-reference overrides without a named ablated module.

Repair policy for the first 25 rows:

- allowed: schema validation, evidence substring validation, strict
  format-preserving Gan label repair, and the frozen clean scorer-facing policy
- disallowed: upper-bound semantic conversion, diary/calendar arithmetic,
  deterministic temporal selection, no-reference or seizure-free semantic
  conversion, selected-evidence repair, and cluster reconstruction

## First Artifact Must Report

- Structured claim-table records and call failures.
- Exact evidence substring count for claim rows and selected final evidence.
- Raw final-query score before downstream repair.
- Strict-format and frozen-clean scores, if repair is needed.
- Rows changed by each downstream repair layer.
- Raw-wrong to repaired-correct improvements and raw-correct to repaired-wrong
  regressions.
- Failure slices separating segmentation/sectioning, claim extraction,
  temporality/conflict, final query, parse/schema, and scorer-format failures.

## Stop Conditions

Promote to a 50-row comparison only if the 25-row run has no systemic call or
schema failures, evidence behavior is reviewable, and failures localize to
meaningful components rather than an opaque final-label mistake.

Revise the schema before any 50-row run if claim rows cannot represent multiple
semiologies, current versus historical statements, seizure-free statements,
last-event-only evidence, or no-reference administrative letters.

Pause this branch if the final query needs deterministic semantic repair to
produce interpretable scores; in that case, reclassify the work as a named hybrid
architecture before continuing.
