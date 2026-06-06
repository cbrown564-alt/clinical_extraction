---
name: clinical-extraction-research-protocol
description: Guide research framing, ablation design, rule-taxonomy discipline, transparency claims, and paper-facing documentation in the clinical-extraction repo. Use when updating contribution thesis docs, designing experiments intended for publication, categorizing deterministic rules, creating ablation/error-analysis plans, auditing LLM attribution or post-processing repair, or checking whether implementation choices support project research claims.
---

# Clinical Extraction Research Protocol

Use this skill to keep implementation choices aligned with the intended paper contribution, not only the next metric bump.

## Environment

For any command-backed research audit, ablation design check, notebook, or
artifact generation, use the `clinical-extraction-env` skill so results come from
the repo `.venv` and editable package install.

## Required Context

Read the relevant current docs before changing research-facing behavior:

- `docs/research/contribution_thesis.md`
- `docs/design/architecture.md`
- `docs/design/gan2026_split_protocol.md` when Gan 2026 experiments, claims, or evaluation surfaces are involved
- `docs/design/gan2026_saturated_validation_protocol.md` when a validation
  surface is near ceiling or a known validation/test gap makes another aggregate
  validation run low-information
- `docs/design/gan2026_pipeline_v1.md`
- `PROJECT_STATUS.md`
- `literature/hybrid_seizure_phenotype_literature_review.pdf` only when the task needs literature-grounded claims

## Research Claims To Protect

- Modular breadth and depth: the system should support deep seizure-frequency extraction without blocking broader clinical phenotyping later.
- Generalisation discipline: separate reusable clinical logic from dataset-specific and benchmark-specific behavior.
- Transparency: preserve event-level schemas, evidence, rationale, row-level errors, and ablation artifacts.
- Deterministic rules as controlled variables: rules should be explicit, categorized, testable, and ablatable.
- Attribution discipline: keep the prediction-bearing source clear. An
  LLM-first claim requires showing what the model selected before deterministic
  semantic repair.
- Split discipline: Gan 2026 validation is for development, train is optimizer-only,
  and test is a locked final holdout that must not be tuned on.

## Workflow

1. Identify which research claim the task touches.
2. Classify affected code or docs as architecture, rule taxonomy, experiment design, error analysis, reporting, or claim language.
3. Preserve the immediate Gan 2026 objective unless the user explicitly shifts priorities.
4. For rules, assign a portability category before implementation:
   - `general`
   - `clinical_epilepsy`
   - `seizure_frequency`
   - `gan2026_specific`
   - `benchmark_format`
5. For experiments, specify the ablation or comparison needed to show component effect.
6. Before approving another aggregate validation run, ask whether the surface is
   saturated. If so, require a hard-case, hard-slice, robustness,
   selective-action, or frozen-test generalization plan instead of a broad
   validation250 comparison.
7. For transparency work, ensure outputs support both per-note inspection and corpus-level summaries.
8. Update docs or status when a durable research decision is made.

## Attribution Rules

- Classify post-LLM behavior by effect, not by module name. If code derives,
  overrides, or changes the selected clinical event or benchmark label, it is a
  deterministic rule even when it lives in `normalize.py`, `schema_repair.py`,
  or a parser helper.
- Restrict normalization claims to format-preserving changes: accepted-label
  grammar, unit spelling, JSON/schema compatibility, parser syntax, and
  arithmetic over the already selected fact.
- Require a named ablation for each semantic repair family before using it to
  support a research claim.
- Treat mixed-prompt, mixed-raw-output, cached-reparse, and exact-threshold
  artifacts as diagnostic until same-raw-output attribution is reported.

## Guardrails

- Do not let Gan-specific synthetic-letter patterns masquerade as general clinical logic.
- Do not describe a component as improving generalisation without cross-surface evidence or a clearly limited claim.
- Do not present full-dataset Gan iteration as a clean development protocol; use the
  locked split manifest and name the split in claims.
- Do not inspect Gan test-set row-level failures as part of ordinary error analysis.
- Do not hide deterministic preprocessing/post-processing as incidental implementation detail.
- Prefer clinically meaningful rule groups over a flat pile of regexes.
- Treat aggregate F1 as incomplete without failure slices, evidence validity, and component ablations.
- Treat near-ceiling validation F1 as especially incomplete. Once validation is
  saturated, broad aggregate comparisons are usually weaker evidence than
  targeted hard-case panels, validation hard slices, adversarial/paraphrase
  robustness, selective-action analysis, or frozen test generalization.
- Do not let caveated documentation coexist with a stronger completion claim.
  If architecture validity is unresolved, record the result as hybrid or
  diagnostic rather than achieved.

## Paper-Facing Outputs

When useful, shape work toward artifacts that can become paper tables or figures:

- component ablation table
- deterministic-rule category ablation table
- failure-mode taxonomy with counts and examples
- per-label Purist and Pragmatic performance
- evidence-validity and schema-validity summaries
- examples of successful and failed temporal reasoning
