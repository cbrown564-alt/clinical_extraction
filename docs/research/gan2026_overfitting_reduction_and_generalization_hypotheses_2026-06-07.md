# Gan 2026 Overfitting Reduction and Generalization Hypotheses Synthesis

Date: 2026-06-07
Author: Antigravity

Status: Living research synthesis. Documents the successful reduction of validation-test gap under the reset-native composable pipeline and establishes clean, non-overfitting hypotheses for future accuracy improvements.

---

## 1. Executive Summary

A comparison of the newly completed **Reset ClinicalAssessment Pipeline** (`validation750_gpt41mini_v0` vs. `test450_gpt41mini_v0`) against historical baselines confirms major progress in eliminating validation-specific overfitting:

* **Validation-Test Gap Collapse**: The Purist accuracy gap between validation and test has collapsed from **17.47%** (under the previous full-repair ladder) to just **5.55%** (84.14% validation vs. 78.59% test).
* **Holdout Score Stabilization**: Despite stripping away high-yield validation-tuned adapters, the holdout test score remained stable at **78.59% Purist / 82.11% Pragmatic**, indicating that we removed metric inflation without degrading true generalization performance.
* **Paradigm Shift**: Future gains must be achieved by resolving fundamental clinical and temporal anchoring limits rather than expanding post-hoc semantic repairs.

---

## 2. Mechanical Analysis of Overfitting Reduction

The previous architecture suffered from a **semantic-repair policy failure (H5)**, where deterministic adapter layers translated raw LLM selections to align with validation annotations:

```text
[Raw LLM Candidate] -> [Deterministic Semantic Repair (Tuned to Val Examples)] -> [Artificially Inflated Val Score]
```

This propped up validation performance (adding **+23.20%** accuracy) but failed to transfer to the locked test set (adding only **+3.33%**).

By transitioning to the **Reset-Native Composable Pipeline**, we restructured the logic into stage-owned, explicit projection and rendering rules:

1. **Isolation of Fallbacks**: We removed broad sentinel demotions and undocumented label-switching rules.
2. **Explicit Null/Route Visibility**: Non-renderable or ambiguous states are routed transparently to nulls or routed-abstain paths, exposing the true accuracy of the underlying extractor rather than masking errors through complex patching.
3. **Metric Alignment**: The validation score naturally declined to reflect the real clinical-state representation, matching the test set’s behavior and closing the generalization gap.

---

## 3. Generalization Hypotheses (Non-Overfitting Pathways)

To improve overall scores for both validation and test sets without falling back into the overfitting trap, we must focus on **structural inputs** and **clinical representation rules** that are independent of individual validation rows. 

The following four hypotheses target the largest error clusters identified in the recent run:

### Hypothesis G1: Date-Anchored Temporal Arithmetic (YTD Calibration)
* **Underlying Error**: 54 errors (58.7% of scored errors) are due to Rate/Denominator mismatches. Most occur when "this year so far" is projected literally as "per year" instead of resolving the fraction of the year elapsed based on the clinic date (e.g. 6 events by April should project as `6 per 4 month`).
* **Mechanism**: In the projection stage, when a candidate indicates YTD temporality, dynamically compute the delta in months between January 1st of the clinic year and the clinic date month. Normalize the denominator by this delta.
* **Why it avoids overfitting**: It relies on universal calendar math anchored to the document's metadata rather than hardcoded phrase maps.

### Hypothesis G2: Explicit Default Cluster Cadence mapping
* **Underlying Error**: 22 errors (23.9% of scored errors) are due to Missed Cluster Semantics. The pipeline currently projects clusters without explicit sizes (e.g., "two clusters over three weeks") as a simple rate (`2 per 3 week`). The gold standard expects these to default to `multiple per cluster` (e.g., `2 cluster per 3 week, multiple per cluster`).
* **Mechanism**: Update `cluster_cadence_as_event_rate_when_size_absent_v0` to render clusters with unspecified event counts as `X cluster per Y period, multiple per cluster`.
* **Why it avoids overfitting**: It establishes a consistent clinical default matching the annotation protocol, rather than tuning on a case-by-case basis.

### Hypothesis G3: Multi-Encounter Anchor Linking for Seizure Freedom
* **Underlying Error**: 75 null renders (44.1% of nulls) occur under `seizure_free_duration_required_v0` due to relative anchors (e.g. "since last visit" or "since last appointment") that cannot be resolved. 39 of these have the gold label `seizure free for multiple month`.
* **Mechanism**: Map relative visit anchor phrases to the date of the prior encounter in `candidate_set.row_context.prior_encounter` (if available), and compute the month delta between the prior encounter date and the current clinic date.
* **Why it avoids overfitting**: It uses explicit cross-encounter metadata rather than manual heuristics to calculate duration.

### Hypothesis G4: Standardized Representation for Catamenial and Sleep Patterns
* **Underlying Error**: 18 null renders (10.6% of nulls) occur under `cluster_cadence_values_required_v0` due to incomplete menstrual/sleep patterns (e.g., "perimenstrual clustering").
* **Mechanism**: Route catamenial and sleep-restricted patterns to dedicated high-precision sentinel representation classes or map them to structured cadence ranges instead of raising value-incomplete errors.
* **Why it avoids overfitting**: It expands the schema's expressiveness systematically for cyclic variants rather than writing custom exceptions for individual phrases.

---

## 4. Verification and Guardrail Protocol

Every hypothesis must be tested using the following multi-tiered validation approach:

1. **Template Consistency Check**: Run the synthetic minimal-pair stress panel to verify that changes do not introduce template brittleness or language-sensitivity.
2. **H6 Control Verification**: Ensure that the selective-action control arm maintains zero regressions on previously verified rows.
3. **Dual-Split Diagnostic Run**: Execute validation750 and test450 in parallel, verifying that accuracy improvements are balanced across both splits, keeping the validation-test gap $\le 8\%$.
