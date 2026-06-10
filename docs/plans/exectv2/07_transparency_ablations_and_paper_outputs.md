# Satellite 07 — Transparency, Ablations & Error Analysis

Parent: [[00_overarching_implementation_plan]] · Phases 5 & 8 (cross-cutting)
Status: planning. Dev-split only until authorized.

## Purpose

Produce the artifacts that make the reliability/transparency claim — not as a
final write-up step, but continuously, so they drive optimization. These are the
black-box-busting outputs the paper rests on.

## 1. Per-prediction transparency

Every `PredictedMention` already carries evidence span, rationale,
`component_owner`, confidence, and uncertainty flags (satellite 01). The
deliverable here is to **surface** them:

- A per-letter trace view (reuse/extend the observatory) showing, for each
  mention: source span, normalized attributes, which component produced it, and
  the gate outcomes (schema valid? evidence substring?).
- Stored intermediate state (candidates, assessment, normalization), not just
  final mentions — so any prediction is fully reconstructable.

## 2. Corpus error taxonomy

Clinically-meaningful failure-mode categories per entity, with counts and
examples, built from dev-split row-level errors. Seed SF categories from the Gan
2026 failure modes (they transfer): seizure-free false pos/neg, current-vs-
historical confusion, cluster-cadence vs intra-cluster rate, denominator-window
mismatch, range/window rendering, missed mention (recall), spurious mention
(precision). Add ExECTv2-specific categories as they appear (e.g. attribute
mis-assignment, entity-type confusion between SeizureFrequency and PatientHistory
on the same span — visible already in EA0006).

Each error is attributed to a **component** (rule family / prompt block / stage),
which is what makes the taxonomy actionable rather than descriptive.

## 3. Ablations

- **Component ablation**: remove/replace each named stage (e.g. hybrid without
  routing; LLM-only without the hard-case guidance) and measure the dev delta.
- **Rule-category ablation**: drop each portability class
  (`general`/`clinical_epilepsy`/`seizure_frequency`/`exectv2_specific`/
  `benchmark_format`) and measure the dev delta — this is the
  generalizability-vs-overfit evidence, and the direct analogue of the Gan 2026
  Phase 2 work.
- **Match-policy sensitivity** (phrase-only / +features / +CUI) — owned by
  satellite 06 but reported here too.
- **Model ablation**: same pipeline across gpt-4.1-mini / qwen3.6-35b / deepseek.

Every ablation is one switch, dev-split, registered, reported as a table row.

## 4. Uncertainty calibration

Apply the Gan 2026 uncertainty harmonization to ExECTv2 from the start, so we do
not repeat the degenerate-`confidence` problem:

- `confidence` defined operationally in prompts (pre-condition A).
- `uncertainty_flags` from a **closed vocabulary** shared across architectures
  (pre-condition B) — plain, clinically meaningful flag names, aggregatable
  across models, linked to the routing taxonomy.
- `aggregation_policy`-style decisions governed by an in-prompt decision table
  (pre-condition C).
- Report a calibration view: accuracy by confidence level, flag frequency by
  model, and whether low-confidence concentrates the errors.

## 5. The three-way comparison (Phase 5, then again at all-9)

The comparison is itself a transparency artifact: it states, with evidence, what
the LLM adds, what generalizes, and what only fit the local set. Build it on SF
first, then rebuild over all 9 entities for the paper.

## 6. Deliverables

- Observatory trace view for ExECTv2 letters
- `exectv2_error_taxonomy_<date>.md` per phase, with counts + examples +
  component attribution
- Component, rule-category, model, and match-policy ablation tables
- Uncertainty calibration report
- Three-way comparison reports (SF and all-9)

## 7. Exit criteria

- Every dev read ships with a row-level error list and updates the taxonomy.
- By Phase 8, the full ablation + calibration + comparison set exists for all
  three architectures over all nine entities, ready to become paper tables.
