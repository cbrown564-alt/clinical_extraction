# Gan 2026 Hybrid Adjudicator V0.2 Audit-Trail Interpretation

Date: 2026-06-01

Primary run:
`experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_gpt41mini_v02_live_2026-06-01.md`

Component ablation:
`experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_v02_live_component_ablation_2026-06-01.md`

This is a validation development interpretation on `gan2026_split_v1`. It is
not a holdout result, benchmark claim, or basis for test-set tuning.

## Question

The validation250 aggregate was low-information because deterministic V1 was
already saturated on this surface. The useful question is therefore not whether
the LLM adjudicator improved performance by a small amount. It did not. The
question is what the LLM added to the pipeline beyond the metric delta:

1. Did it add useful semantic review signal?
2. Did it improve the audit trail?
3. Did it mostly add noise and attribution risk?

## Decision

Keep v0.2 as a diagnostic artifact only. Do not promote it as a
prediction-bearing adjudicator.

The LLM added semantic dissent and row-review commentary, but it did not add a
reliable final-selection layer. The current audit trail is mixed: richer
rationales are available, but evidence validity and final-label accountability
are weaker than the deterministic trace. In production or paper-facing
language, v0.2 should be described as a saturated-surface diagnostic probe, not
as an improved hybrid extractor.

## Metric Context

| Condition | Purist | Pragmatic | Changed | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| Deterministic top | 246/250 | 246/250 | 0 | 0 | 0 |
| Raw LLM adjudicator | 245/250 | 246/250 | 9 | 1 | 2 |
| Conservative gated final | 244/250 | 245/250 | 8 | 0 | 2 |

The conservative gated final produced no Purist corrections over deterministic
top and introduced two deterministic-correct regressions. The only raw
LLM-improved row, row 3356, was blocked by the conservative overreach gate and
fell back to the deterministic answer.

The ablation table also shows an important audit asymmetry. The deterministic
conditions report `1.0000` evidence validity on this surface. The raw and gated
LLM adjudicator rows do not have an independently scored evidence-validity
column in the component ablation. That makes the adjudicator harder to audit
than the deterministic comparator despite having more natural-language
rationale text.

## What The LLM Added

The LLM did add a useful kind of semantic dissent. Its rationales often
distinguish cases that the scorer treats similarly but a reviewer may want to
separate:

- `no seizure frequency reference` versus `unknown`;
- current seizure activity without a normalized rate;
- candidate evidence that is present but too weak or too header-like;
- possible mismatch between current and historical frequency;
- cases where a candidate label is too specific, too broad, or tied to the
  wrong seizure/event target.

This is real information, especially for designing hard slices. It suggests
that the LLM can act as a reviewer that flags "the deterministic label may be
scorer-compatible but clinically underspecified." That is different from being
a good final-label adjudicator.

The changed-label rows make this distinction visible:

| Row | Deterministic | Raw LLM | Gated final | Gold | Interpretation |
| ---: | --- | --- | --- | --- | --- |
| 338 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | multiple per month | Raw rationale argued for a frequency-like answer, but parser repair collapsed it back to the deterministic label. This is signal about missing evidence, but not a clean final-label trace. |
| 743 | no seizure frequency reference | unknown | unknown | multiple per week | Boundary change only; still scorer-correct because both map to the broad unknown category. Useful review signal, not metric gain. |
| 744 | multiple per week | 1 per 8 week | 1 per 8 week | multiple per week | Harmful selection. The LLM preferred a specific lower-rate event over the deterministic unresolved-multiple answer. |
| 816 | 1 per month | 4 per year | 4 per year | 1 per month | Harmful temporal/currentness selection. The LLM selected a different window than the scorer/gold. |
| 2166 | no seizure frequency reference | unknown | unknown | unknown | Boundary change only; useful distinction between no reference and unclear frequency, but no score movement. |
| 3356 | seizure free for multiple year | unknown | seizure free for multiple year | unknown | Raw LLM caught a deterministic overreach, but the conservative gate blocked the correction. |
| 3493 | no seizure frequency reference | unknown | unknown | unknown | Boundary change only; semantically reviewable but scorer-equivalent. |
| 4771 | no seizure frequency reference | unknown | unknown | unknown | Boundary change only; LLM flags seizure discussion without a normalized candidate. |
| 5490 | no seizure frequency reference | unknown | unknown | unknown | Boundary change only; LLM captures uncertainty rather than absence. |
| 5507 | no seizure frequency reference | unknown | unknown | unknown | Boundary change only; same pattern. |

## Audit-Trail Assessment

V0.2 improves the human-readable audit trail in one narrow sense: it gives a
semantic explanation for accepting or rejecting the deterministic candidate. A
reviewer can read the rationale and understand why the model was tempted to
change the answer.

It weakens the audit trail in the more important prediction-bearing sense:

- the final LLM output is not tied to an independently scored exact evidence
  trace in the ablation;
- accepted/rejected event IDs are not enough when the model also reasons from
  note content outside the deterministic candidate set;
- parser repair can turn an LLM rationale that argues for one semantic answer
  into a different final scorer label;
- the gate policy can suppress the one useful raw correction while allowing
  harmful deterministic-correct regressions;
- many changed labels are scorer-equivalent boundary substitutions, making the
  row table look busier without adding measurable correctness.

So the audit trail is richer but less disciplined. It is better for exploratory
review and worse for a final accountable extraction pipeline.

## What This Says About The LLM Role

The LLM is not yet a high-precision adjudicator over deterministic candidates.
On this surface, the deterministic head's remaining errors are too sparse and
too idiosyncratic for broad validation250 to measure improvement. The LLM mostly
relabels boundary states or over-selects plausible but wrong candidate events.

The promising role is selective semantic triage:

- flag deterministic outputs that look clinically underspecified;
- distinguish `unknown` from `no seizure frequency reference` for review;
- identify candidate-set recall failures where no candidate supports the
  frequency described in the note;
- propose hard-slice definitions for future experiments;
- produce row-review notes without changing the final label by default.

That role should be evaluated with selective-action metrics, not ordinary
aggregate F1. The relevant question is: when the LLM says "the deterministic
answer is suspicious," how often is that flag correct and actionable?

## Implications For Next Experiments

Do not spend more hosted calls on broad validation250 or validation750 for this
version. The next useful surface should force the adjudicator to show precision
on named failure modes:

1. hard cases where deterministic V1 is known to over-select seizure-free or
   no-reference labels;
2. boundary slices for `unknown` versus `no seizure frequency reference`;
3. temporal/window conflict slices where current and historical rates compete;
4. candidate-set recall failures where the correct semantic category is absent;
5. selective-action evaluation where the LLM may abstain, flag for review, or
   change the final label under strict evidence requirements.

The prediction path should require stricter accountability before another
promotion attempt:

- exact selected evidence for every LLM-supported change;
- named failure family for every proposed change;
- explicit candidate IDs and whether the model is staying inside or outside the
  deterministic candidate set;
- separate scores for "flag only" and "changed final label";
- changed-label precision reported as wrong-to-correct, correct-to-wrong, and
  scorer-equivalent boundary substitutions.

## Conclusion

V0.2 answers a useful research question, but not the one the aggregate metric
was built to answer. The LLM adds semantic dissent and review text. It does not
add a trustworthy final-selection layer on this saturated surface.

The report should be carried forward as evidence for a controlled hybrid thesis:
LLMs may be useful as source-near reviewers, uncertainty explainers, and
hard-slice generators, while deterministic extraction remains the accountable
prediction source unless an LLM component proves high changed-label precision
under strict evidence tracing.
