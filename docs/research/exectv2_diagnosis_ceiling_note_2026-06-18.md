# ExECTv2 Diagnosis Ceiling Note

Date: 2026-06-18
Scope: Diagnosis reconciler v0.1 dev140, interpreted with the residual
convention decomposition.
Status: ceiling/characterization result; not a target-clearing plan.

## Decision

Stop ordinary Diagnosis target-chasing on the current candidate set. Diagnosis
should be reported as a transparent ceiling/annotation-scope result, not as a
near-miss that another verifier or accept/reject gate is expected to clear.

Current best Diagnosis dev140:

| Candidate | F1 | P | R | TP | FP | FN | Evidence-valid |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Diagnosis reconciler v0.1 | 0.658 | 0.658 | 0.658 | 243 | 126 | 126 | 99.5% |

## Why The Gate Is Not Legitimately Reachable

The residual convention decomposition asks how much of the Diagnosis gap is
recoverable by convention projection rather than by new clinical extraction.
The answer is not enough.

| Layer | F1 |
| --- | ---: |
| Base reconciler v0.1 | 0.658 |
| + assertion convention oracle | 0.713 |
| + hierarchy altitude oracle | 0.737 |
| + adjacent-family specificity oracle | 0.791 |

Even the generous oracle remains below `0.8`. The real system must sit below
that oracle because it cannot know every convention decision perfectly on unseen
letters without leaking benchmark labels. Therefore, another prompt/reject gate
over the same candidates is not a legitimate target-clearing plan.

## What The Residual Means

Diagnosis residuals are almost entirely grounded in real letter text: evidence
validity is `99.5%`, with zero call or parse failures. The problem is not
hallucination. It is a large grounded selection/scope disagreement with the
annotation target:

| Residual bucket | Events | Share |
| --- | ---: | ---: |
| assertion convention | 40 | 15.9% |
| hierarchy altitude | 18 | 7.1% |
| adjacent-family specificity | 40 | 15.9% |
| genuine grounded selection/scope residual | 154 | 61.1% |

The recurrent pattern is clinically real but benchmark-out-of-scope emission,
especially generic `epilepsy` and tonic-clonic concepts, paired with misses of
specific concepts such as focal epilepsy and secondary-generalised seizures.
Suppressing grounded emissions harder is the same move that previously caused
collateral verifier collapse in other family experiments; it is not a clean
generalization strategy.

## Paper-Facing Claim Language

Supported:

> Diagnosis evidence validity is high (`99.5%`), and a meaningful minority of
> residual events are annotation-convention disagreements. However, even a
> generous convention oracle reaches only `0.791`, so the dev140 `0.8` gate is
> not reachable through legitimate convention alignment over the current
> candidate set.

Supported:

> Diagnosis should be reported as a grounded clinical-selection and
> annotation-scope ceiling result, with semantic/concept-layer recovery and
> residual taxonomy shown separately from benchmark-F1.

Not supported:

> Diagnosis can clear benchmark-F1 `0.8` on dev140 with another verifier,
> reconciler, or accept/reject gate over the current candidate set.

Not supported:

> The Diagnosis residual is primarily hallucination or evidence failure.

## Next Use

Use this note to keep the final ExECTv2 architecture synthesis conservative:
two key families clear dev140, SF improves but remains below target after
state projection, and Diagnosis is a ceiling/characterization result. A future
Diagnosis attempt would need a genuinely new evidence-selection architecture or
a different evaluation target, not another local gate over the same residual.

## Artifacts

- Current candidate:
  `experiments/exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618.jsonl`
- Residual ledger:
  `experiments/exectv2_diagnosis_reconciler_v01_residual_ledger_dev140_20260618.md`
- Convention decomposition:
  `docs/research/exectv2_residual_convention_decomposition_2026-06-18.md`
- Parent architecture report:
  `docs/research/exectv2_key_entity_architecture_research_report_2026-06-18.md`
