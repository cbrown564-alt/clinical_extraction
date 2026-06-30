# A5 probe — DeepSeek precision prompt profile (dev140, bounded single-model)

Status: **CLOSED (small positive, mechanistically clean; bounded per stop rule).** Date: 2026-06-30.

Predecessor-lessons avenue A5 (model-specific prompt profiles,
`docs/research/predecessor_lessons/03_promising_unfinished_avenues.md`) was confirmed fully
unbuilt before this probe. The GEPA workstream's Phase 0c finding
(`docs/plans/exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md` §6b) named a sharp,
single, model-specific failure mode: DeepSeek-chat retrieves more evidence than gpt-4.1-mini
on the per-family producer but keys it worse (over-emits, costing precision). This probe is the
first test of whether a targeted, single-sentence precision clause — added to the existing
mini-evolved instructions, nothing else changed — closes that gap, per A5's safe-protocol-shape
(one model, one named failure mode, scorer/slice/architecture fixed).

Model: `deepseek/deepseek-chat`. Seed instructions: the mini-evolved per-family 0.731 run
(`exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628.instruction.txt`), unchanged except
for the addendum below. Architecture: `GepaPerFamilyExtractor`
(`gepa/program_multifamily.py`), reused verbatim via `run_gepa._evaluate_program` — no GEPA
optimization loop, a single hand-authored A/B comparison.

Added clause (every family, appended verbatim): "Precision discipline: only emit a fact when
the evidence text itself directly states or unambiguously implies the specific value you are
claiming -- do not emit a fact from a borderline, generic, or loosely-related mention. When in
doubt, omit it rather than guess."

## Result

| condition | overall F1 | precision | recall | Diagnosis | SeizureFrequency | Prescription | Investigations | ev-recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline (mini instructions verbatim) | 0.7255 | 0.6804 | 0.7771 | 0.6378 | 0.5515 | 0.8873 | 0.9288 | 0.7388 |
| + precision addendum | 0.7401 | 0.7066 | 0.7771 | 0.6533 | 0.5625 | 0.9144 | 0.9195 | 0.7366 |

Delta (overall F1): **+0.0146**.

**The mechanism predicted by Phase 0c is exactly what fired.** Precision improved
(0.6804 → 0.7066, **+0.0262**) while recall held **exactly flat** (0.7771 → 0.7771, bit-for-bit
identical) and evidence-recall barely moved (0.7388 → 0.7366, −0.0022, within noise). This is
not a generic "model got better" effect — it is the precision-targeted clause fixing the
precision-specific weakness the doc named, without touching retrieval. Diagnosis and
Prescription both gained (+0.0155, +0.0271); Investigations gave a little back (−0.0093),
consistent with a precision-favoring clause trading a small amount of recall-adjacent coverage
in the family that was already near-ceiling (0.9288).

## A discrepancy worth flagging

This probe's own **baseline** replication (0.7255, same instructions, same model, same
architecture, same dev140 split) does not match the previously-reported Phase 0c "model-swap
only" number (**0.681**). Both runs claim to be "the existing `program_multifamily` re-run with
`task_model=deepseek/deepseek-chat`, same instructions, no schema change." The gap is large
enough (+0.044) that it should not be silently absorbed into the addendum's apparent lift —
possible causes (not diagnosed further here, out of this probe's bounded scope): a DeepSeek
model-version drift between the two runs (no pinned snapshot id), a different `max_tokens`
budget, or the Phase 0c number actually coming from a slightly different config than its own
write-up states. **The internally-controlled comparison in this probe (baseline vs addendum,
identical script, same session, same model snapshot) is unaffected by this discrepancy** — both
arms ran under matched conditions — but the cross-session "0.681 → 0.7401, +0.059" framing
should not be cited; only the same-session **+0.0146** delta is attributable to the addendum.

## Comparators

- mini per-family baseline (same instructions, gpt-4.1-mini): 0.7313
- DeepSeek Phase 0c (model-swap only, prior report, see discrepancy note above): 0.681
- This probe's own DeepSeek baseline (same-session re-measurement): 0.7255

Under the same-session baseline, the addendum (0.7401) **slightly exceeds the mini per-family
reference (0.7313)** on this identical architecture — a single sentence closes what was
previously read as a meaningful cross-model gap.

## Verdict

**Small positive, mechanistically clean.** The effect size (+0.0146 overall F1) is modest and
does not clear a "large win" bar, but it is not noise: it is concentrated exactly where
predicted (precision, not recall), reproducible within the controlled A/B, and free (one
sentence, zero added latency/cost). Worth keeping as the default DeepSeek profile for this
architecture if DeepSeek is used as a producer model again; not worth a further wording-tuning
loop.

## Scope and stop rule

Per A5's safe-protocol-shape: one model, one pre-named failure mode, scorer/slice/projection
held fixed, reported as a model-specific result, not a universal prompt change (no claim is
made about gpt-4.1-mini or Qwen, and the addendum was never tried on either). This is a single
bounded comparison; per the predeclared stop rule, no further iteration on the addendum wording
follows. The baseline-discrepancy question above is noted as an open item, not chased further
here — it is a measurement-hygiene question (model-version pinning), not part of this probe's
question.
