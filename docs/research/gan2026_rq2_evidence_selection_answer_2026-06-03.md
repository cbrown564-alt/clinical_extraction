# Gan 2026 RQ2 Evidence-Selection Answer

Date: 2026-06-03

Supersession note, 2026-06-03: this report is retained as a diagnostic baseline
audit, not a completed RQ2 research answer. Its deterministic-default conclusion
falls into the validation-tuned selector trap described in
`docs/research/gan2026_research_question_retrospective_2026-06-03.md` and is
superseded by
`docs/research/gan2026_llm_component_mechanics_synthesis_2026-06-03.md`.

## Answer

RQ2 is answered for saved validation replay as a development-control question.

The best evidence-selection component in the saved validation artifacts is the
hybrid adjudicator selected-evidence layer: 750/750 exact selected-evidence rows
and 750/750 valid selected-source-id rows on validation750. It does not improve
the deterministic top label substrate, though: its supported label is Purist
correct on 693/750 rows versus 697/750 for deterministic top, and its four
changed rows are all deterministic-correct regressions.

The practical RQ2 answer is therefore:

- Use deterministic top / rules-only evidence as the default safe substrate for
  label-bearing selection.
- Use hybrid adjudicator selected evidence as the strongest source-grounded
  evidence span selector when the task is to attach exact evidence and source ids
  to an already safe candidate.
- Treat LLM-heavy typed selected facts and claim-table final queries as useful
  diagnostic evidence selectors, not as default replacement selectors.
- Do not use raw LLM candidate selection as a replacement component: it selects
  mostly exact evidence but changes too many deterministic answers and creates
  many regressions.

## Supporting Artifacts

Protocol:
`docs/research/gan2026_rq2_evidence_selection_protocol_2026-06-03.md`

Matrix report:
`experiments/gan2026_rq2_evidence_selection_matrix_2026-06-03.md`

Machine-readable matrix:
`experiments/gan2026_rq2_evidence_selection_matrix_2026-06-03.jsonl`

Builder:
`src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/evidence_selection_matrix.py`

The matrix has 3,489 component rows over 750 validation source rows. It replays
saved validation artifacts only; it makes no new model calls.

## Component Trade-Offs

| Component | Surface | Exact evidence | Source-id valid | Purist correct | Changed vs deterministic | Wrong-to-correct | Correct-to-wrong |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Hybrid adjudicator raw | validation750 | 750/750 | 750/750 | 693/750 | 4 | 0 | 4 |
| Deterministic top | validation750 | 635/750 | 750/750 | 697/750 | 0 | 0 | 0 |
| State graph projection | validation750 | 633/750 | 750/750 | 655/750 | 49 | 0 | 42 |
| Raw LLM candidate selector | validation750 | 727/739 | 738/738 | 107/161 judged | 724 | 7 | 49 |
| Claim-table final query | validation250 | 246/250 | 248/248 | 223/242 judged | not comparable | not comparable | not comparable |
| LLM-heavy selected fact | validation250 | 242/250 | not instrumented | 203/240 judged | not comparable | not comparable | not comparable |

The hybrid adjudicator clearly wins the narrow evidence-span and source-id task.
That win is not a final clinical-selection win, because every changed row moves
in the wrong direction relative to the deterministic top comparator.

The deterministic top component remains the best default because it has the best
validated correctness and no changed-row regression risk. Its lower exact-span
rate mostly reflects shorter deterministic snippets and replay instrumentation,
not a reason to replace the clinical decision.

The claim-table final query is strong on validation250 evidence exactness and
selected-claim trace, but it lacks same-row deterministic comparison in this
matrix. It is promising for RQ3/RQ4-style schema and projection questions, not a
standalone RQ2 promotion.

The LLM-heavy selected fact has good evidence exactness and 227/250 complete
typed operand rows, but no source-id trace and weaker selected-label correctness.
It should feed adapter/schema diagnostics, not default evidence selection.

## Hidden-Family Readout

Only the LLM-heavy selected-fact validation250 artifact currently carries hidden
family tags in the atlas lookup. Within that surface, exact evidence remains
high across most families, but correctness and operand completeness expose the
fragile areas:

- Current-versus-historical: 160/167 exact evidence, 140/163 Purist-correct
  judged rows, 155/167 operand-complete rows.
- Rate bucket or denominator: 77/80 exact evidence, 63/75 Purist-correct judged
  rows, 74/80 operand-complete rows.
- Seizure-free duration: 40/42 exact evidence, 36/42 Purist-correct judged rows,
  38/42 operand-complete rows.
- Cluster burden: 49/52 exact evidence, 37/49 Purist-correct judged rows, 44/52
  operand-complete rows.
- Unknown boundary: 22/23 exact evidence, but only 8/18 Purist-correct judged
  rows and 12/23 operand-complete rows.
- Uncertainty or ambiguity: 25/26 exact evidence, but only 11/21 Purist-correct
  judged rows and 15/26 operand-complete rows.

This says the LLM often points to the right text even when its state, operand, or
boundary interpretation is wrong. Those failures belong to RQ3, RQ4, and RQ10
more than to RQ2.

## Transfer Confidence

Development confidence is high for the narrow claim that hybrid adjudicator
selected evidence can be made exact and source-traced on saved validation replay.

Holdout-transfer confidence is low to moderate. The finding is mechanistically
plausible because exact substring and source-id gates are simple, but the
component was evaluated on saved validation artifacts after substantial
validation work. It is not a holdout-transfer claim.

Before holdout-facing use, freeze a source-id/evidence-only policy that cannot
change deterministic clinical labels, then run a predeclared changed-evidence
audit. If the policy is allowed to change labels, it must satisfy changed-row
exact evidence, wrong-to-correct accounting, and deterministic-correct regression
constraints before any locked-test use.

## Metadata And Instrumentation Gaps

- Claim-table and LLM-heavy selected-fact artifacts are validation250, not full
  validation750 same-surface comparisons.
- LLM-heavy selected facts do not record selected source ids, so they cannot
  support an exact-source-id claim.
- Hidden-family tags are not complete for every artifact in the matrix.
- Deterministic exact evidence can be undercounted when the saved evidence span
  is a compact snippet rather than the full source sentence.
- RQ2 still cannot by itself decide schema representation, projection, rendering,
  or gold/scorer ambiguity.

## Decision

RQ2 is answered for saved validation replay:

- Default evidence-bearing clinical substrate: deterministic top candidate.
- Best exact/source-traced evidence span selector: hybrid adjudicator raw
  selected evidence, only when label changes are blocked or separately gated.
- Best diagnostic schema source: claim-table final query and LLM-heavy selected
  fact, with source-id instrumentation required before promotion.
- Rejected as a replacement selector: raw LLM candidate selector.

## Next Action

Move the active question to RQ4 projection over fixed candidates/states. The
reason is that RQ2 shows selected evidence can be exact and source-traced, but
the remaining regressions arise when components project, render, or reinterpret
the selected state into a final label.
