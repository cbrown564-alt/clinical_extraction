# ExECTv2 Reliability-Audit Protocol Predeclaration

Date: 2026-06-24

Status: frozen protocol for the next reliability-audit workstream. This document
is binding for calibration, review-routing, robustness, and consistency upgrades
that build on the 2026-06-24 refresh of
`docs/experiments/exectv2/reliability/exectv2_cross_model_reliability_scorecard_2026-06-22.md`.

## Purpose

The refreshed scorecard is strong dev140 trust evidence, not validated
calibration or deployment triage evidence. This protocol freezes the audit
surface before further optimization so that a lower-burden review policy,
calibrated risk model, robustness panel, or same-prompt consistency panel can be
reported without drifting into post-hoc tuning.

## Frozen Surfaces

Two surfaces may be audited, but they must not be blended:

| Surface | Primary scorer | Current role |
| --- | --- | --- |
| Rich-schema holistic assembly reliability scorecard | `headline_target` family-cell correctness from the final-consolidation / cross-model reliability payload | Same-surface dev140 reliability evidence across v08, v09, DeepSeek, and Qwen. |
| Active LLM-only de-duplicated facts | `clinical_headline` de-duplicated clinical-fact recovery | Phase 3-6 LLM-only transfer/plateau evidence; strict benchmark F1 remains diagnostic only. |

Any audit report must name exactly one of these surfaces in its title, methods,
and artifact names. If both are shown, they are separate sections with separate
promotion decisions.

## Split And Artifact Policy

| Artifact/split | Allowed use | Not allowed |
| --- | --- | --- |
| `dev140` saved artifacts | Design and freeze candidate risk features, review triggers, perturbation templates, consistency prompts, and report schema. Dev140 results may be labeled training/development evidence only. | Claim validation, tune after seeing validation/full-200 outcomes, or promote a dev-tuned operating point as validated. |
| `full-200` / benchmark-facing corpus | Aggregate-only validation after the code hash, scorer, thresholds, and stop rule are frozen. Reports may include overall/family metrics, calibration bins, review burden/catch, false-alarm counts, and perturbation/consistency aggregates. | Manual row-level inspection of notes, gold labels, predictions, evidence spans, rationales, residual examples, or selected failures unless a separate row-inspection protocol explicitly authorizes it. |
| Holdout or external locked artifacts | Confirmatory aggregate-only read after a candidate has passed the full-200 gate. Use once per frozen candidate. | Any development, threshold tuning, prompt editing, rerun selection, or row-level inspection. |

If a script must compute row-level correctness internally to produce aggregate
metrics, it may do so only from frozen artifacts and may persist a machine-readable
aggregate summary. It must not emit row-level examples, identifiers tied to
errors, note text, evidence text, rationales, or failure ledgers for full-200 or
holdout artifacts.

## Stop Rule

For each candidate audit:

1. Freeze the candidate definition, code hash, input artifact list, scorer,
   thresholds, and report template in the preflight section of the audit report.
2. Run the validation once.
3. If the candidate fails any promotion gate, stop and report the null result.
   Any threshold, prompt, perturbation, or feature change starts a new
   predeclared candidate on dev140 only.
4. A rerun is allowed only for infrastructure failure before metrics are read,
   such as corrupted input, parser crash, or missing artifact. The rerun reason
   must be recorded.

## Promotion Gates

### Calibration

Promote a calibration upgrade only if all are true on the validation split:

- ECE improves over the dev-only proxy baseline of `0.1456`.
- Brier score is reported and improves over a constant base-rate comparator.
- Reliability bins are monotone enough to be clinically interpretable: at least
  four populated bins and no adjacent-bin reversal larger than `0.10`.
- Per-family ECE is reported for Diagnosis, SeizureFrequency, Prescription, and
  Investigations; no family may be hidden behind an overall improvement.

Passing this gate permits claiming improved calibration evidence, not a
deployment-ready probability.

### Review Routing

Promote a review-routing operating point only if all are true on the validation
split:

- Review burden is at least `0.15` absolute lower than the high-recall dev140
  trigger set (`0.9408` burden), or the report explicitly keeps the high-recall
  policy as the selected operating point.
- Overall error catch is at least `0.80`.
- Every family reports eligible cells, error cells, caught errors, missed errors,
  false alarms, review burden, and catch rate.
- No family with at least ten error cells has catch below `0.70`.
- False-alarm cost is reported as false alarms per caught error and is lower than
  the high-recall trigger set.

The dev candidate currently at `0.7567` burden / `0.8028` catch is a candidate
to validate, not a promoted policy.

### Robustness

Promote a robustness upgrade only if a frozen panel is run without changing the
candidate after results are read. The minimum panel covers:

- SeizureFrequency current-vs-historical/current-vs-future state perturbations.
- Prescription current-vs-plan ambiguity.
- Investigations normal/abnormal/result-pending ambiguity.
- Diagnosis assertion, hierarchy, and alias-convention pressure cases.
- Evidence paraphrase/deletion stress tests that preserve the clinical fact.

Report overall and per-family score deltas, schema-validity rate,
evidence-validity rate, and perturbation family counts. A robustness claim may
not be made from cherry-picked successful perturbation types.

### Same-Prompt Consistency

Promote a consistency upgrade only if the same prompt, model, temperature,
schema, and evidence gate are frozen before calls begin. Report:

- number of seeds / repeats,
- call failures,
- schema-validity rate,
- evidence-validity rate,
- within-model pairwise clinical-headline Jaccard,
- exact family-cell agreement,
- per-family disagreement rates.

Deterministic replay stability, cross-model agreement, and same-prompt
resampling are separate evidence types and must remain separated in the
scorecard.

## Reporting Contract

Every reliability-audit report must include:

- surface and scorer,
- split and artifact list,
- code hash or command provenance,
- row-inspection boundary,
- stop-rule outcome,
- promotion-gate table,
- whether the result is dev-only, validation, full-200, holdout, or external.

Scorecard coverage may increase only when the report names the validation split
and passes the relevant gate. Failed gates should still be linked from the
scorecard as null reliability evidence.

## Guardrails

- Do not inspect ExECTv2 full-200 or holdout row-level failures under this
  protocol.
- Do not use strict benchmark F1 as the headline for de-duplicated
  `clinical_headline` LLM-only runs.
- Do not treat deterministic projection or repair as LLM clinical extraction.
- Do not merge rich-schema holistic assembly evidence with LLM-only
  de-duplicated-fact evidence in a single promotion decision.
