# Longitudinal prototype evaluation

Version 0.1, 2026-09-11. Mode: full working prototype. This document owns the
Phase 4 development comparison. It does not freeze a Phase 7 benchmark evaluation.
The task definition owns the five queries and date arithmetic; the annotation
guide owns the provisional reference. Neither is changed by this study.

## Question and inputs

Can evidence-supported linking and temporal query rules produce an inspectable
patient history in both views, and which failures arise before versus after
linking? Use the twelve Phase 2 authored development patients for the demonstration
and both the authored and Phase 3 generated packs for query-mechanism checks.
All 480 fixed requests stay in the diagnostic denominator. No benchmark source,
locked split, hidden authoring history or reference answer enters prediction.

The main extraction condition replays the 48 previously attempted, physically
filtered agy tasks (44 successful, four failed), model requested
`gemini-3.8-flash-medium`. These are actual saved model extractions, not a new
per-letter extraction experiment. Their original questions were visible during
extraction; do not claim extraction independent of query context. Verify the
saved input and letter hashes before reuse. Preserve the original response and
capture failure; do not use the model's query answers as pipeline output.

Keep raw extraction, exact quote offset normalization, deterministic semantic
rules, linking, history assembly and query selection separate. Missing quotes
or malformed structures fail visibly. Exact quote offset correction is format
repair only; no clinical field is silently corrected. New model calls and paid
fallback are outside this prototype. The replay adapter must reject unseen or
changed input rather than substitute a reference annotation.

## Comparisons and attribution

Run the same query policy with: (1) provisional reference facts and reference
links, (2) reference facts and inferred links, (3) reference facts without links,
and (4) saved predicted facts and inferred links. Remove existing links before
running the new linker. Compare linking on reference facts against the supplied
links, reporting supported-link precision/recall and unaligned endpoints instead
of treating identical assertion IDs across extractors as semantic equality.
For predicted facts, map only uniquely matching same-letter content with grounded
evidence; report alignment coverage and link denominators. Same-model saved-output
comparisons isolate downstream code, while reference-versus-predicted comparisons
also include extraction and representation differences.

Record each request's output, supporting spans, rule IDs, status agreement and
first failing condition: extraction/format, linking or query policy. Report both
views, query, patient, each status, and model failures. A failed capture is a
failure, not an indeterminate prediction and not an excluded patient. State
denominators explicitly. Link omissions, unsupported definitive answers and
regressions against the frozen Phase 2/3 diagnostic remain visible.

The declared mechanism checks are the eleven Phase 2 gaps and 33 Phase 3
mismatches. Pin conservative counterexamples: unknown or boundary-overlapping
time, one-day gaps in negative coverage, copied text, uncertain identity, disputed
events, plan versus use and result date versus availability. Keep qualitative
holiday inclusion separate from stored date bounds. No date midpoint is invented.
Rules derived from these examples are synthetic-development rules, not evidence
of generalization. No treatment-causality rule is implemented.

## Prototype and completion evidence

Provide a patient selector, ordered permitted letters, both views, two index dates,
the five cohort questions and evidence navigation in the existing frontend. Show
provisional reference facts separately from saved model predictions. Support empty
cohorts, unavailable extractions, loading, failure and retry. A later correction
must visibly change the retrospective answer while leaving the visit answer intact.

Save versioned outputs, hashes, configuration, rule categories, comparison rows,
link alignment, failure records and browser QA under
`results/longitudinal/prototype_v0.1/`; local work/logs stay under ignored `runs/`.
Stop when the complete twelve-patient loop, focused research-validity tests,
frontend interaction checks and documented broad checks have run and remaining
limitations are reported. Record frontend desktop/mobile/keyboard checks and the
exact scripted cutoff example. No expert validation, release, deployment or
large-scale generation is authorized or implied by completion.

## Execution interpretation

The completed [Phase 4 record](../../results/longitudinal/prototype_v0.1/README.md)
reports reference-supported edge precision/recall alongside exact edge agreement.
Equivalent endpoints use reference identity paths and co-located source accounts;
unaligned predicted edges remain in the precision denominator. This is support
relative to provisional annotations, not clinical adjudication. First-condition
attribution retains `predicted_input_or_linking` when the same linker succeeds
with reference input: that comparison cannot by itself distinguish a missing
clinical fact from a linker that depends on its representation. Capture failures
are separately attributed to extraction/format. The remaining definitive error
and the repaired narrow-quotation disagreement mechanism have explicit reviews.
