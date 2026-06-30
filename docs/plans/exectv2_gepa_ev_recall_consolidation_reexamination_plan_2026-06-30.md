# Plan — does gold-consolidation inflate the GEPA-vs-hybrid evidence-recall gap?

Status: **EXECUTED (2026-06-30). H-inflated CONFIRMED (86/92 = 93.5%, well above the ≥50%
threshold).** Full result:
`docs/experiments/exectv2/diagnosis/exectv2_dx_ev_recall_consolidation_check_2026-06-30.md`.
Phase 2 propagation done: status-correction notes added to
`exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md` and
`exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md`. Phase 3 (SF extension) not pursued —
deferred as a separate, future predeclared plan per §5.
Owner: ExECTv2 GEPA workstream / predecessor-lessons application follow-up. Date: 2026-06-30.

Follows from: `docs/experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md`
(the Diagnosis gold-quality finding) and
`docs/research/exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md` (the doc whose central
evidence-recall claim this plan re-examines). See [[project_predecessor_lessons_application]] and
[[project_exectv2_gepa_workstream]].

## 1. Why this exists

The evidence-decomposition doc's central, still-active claim: the GEPA-vs-hybrid gap
(`clinical_headline` 0.731 → 0.920, +0.189) is *almost entirely LLM evidence retrieval* —
evidence-presence recall (`source_near_diagnostic`, same-entity phrase-substring overlap,
representation-agnostic) is **GEPA 0.694 vs hybrid 0.883** (+0.190 ≈ the F1 gap). That number is
the reason the active GEPA strategy (`exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md`) bets
its budget on **recall-oriented producers** ("make each lane retrieve exhaustively") rather than on
re-keying or scoring fixes.

On 2026-06-30, the Diagnosis canonical row-adjudication found that **85.2%** of the *scored*
`clinical_headline` gap for Diagnosis is not genuine model error but **gold multiplicity**: gold
tags both a generic/parent concept and a specific/co-present concept (or splits one compound
phrase into atomic fragments) from a single diagnostic statement, and the model's reasonable
one-tag consolidation is scored as both a miss and a false positive.

**The open question this plan tests:** evidence-recall and `clinical_headline` are *different
metrics* computed by *different matching logic* — `clinical_headline`/`concept_only` matches by
canonical concept key with an entity-agnostic recall pool, while `source_near_diagnostic` matches
by phrase-substring overlap, same-entity only, with greedy 1:1 prediction consumption
(`_first_overlapping_prediction`, `used_pred` set). It is not yet known whether the same gold
multiplicity that inflates the *scored* gap also inflates the *evidence-recall* gap, or whether
evidence-recall is a genuinely separate, real measurement that the consolidation finding does not
touch. If it does inflate it, the focused-lanes plan's "build more retrieval" lever is partly
mis-targeted — the cleaner win would look more like Phase 3's deterministic re-keying (Dx
0.703→0.792 from re-keying alone, no new retrieval) than like more producer lanes.

## 2. The specific mechanism hypothesis

Reading `_first_overlapping_prediction` (`scoring/match.py:543`) closely: for each gold Diagnosis
annotation, it greedily claims the first **unused** predicted Diagnosis annotation whose
normalized phrase is a substring (either direction) of the gold phrase. When gold splits one
underlying diagnostic statement into multiple separate annotations (the exact pattern the
adjudication found, e.g. "focal epilepsy" + "temporal lobe epilepsy" from one phrase) and the
model emits a single consolidated prediction, two distinct candidate mechanisms can produce an
evidence-recall **false negative** that has nothing to do with the model failing to find anything:

- **H1 — cardinality/greedy-exhaustion artifact.** The model's one prediction's phrase *does*
  substring-overlap more than one of gold's split annotations, but `used_pred` only lets it match
  the first one encountered; the second+ gold annotation registers as an unmatched FN even though
  the model's text was right there.
- **H2 — genuine phrase divergence.** Gold's second annotation has different surface text than
  anything the model predicted (e.g. the model said "epilepsy", gold separately annotated
  "temporal lobe epilepsy" over different characters) — no text-overlap exists regardless of
  cardinality. This is a real retrieval gap by `source_near`'s own definition, but it may still
  correlate with the adjudication's `MODEL_DEFENSIBLE` verdict (the model said something
  defensible, just never produced text overlapping that specific gold span) rather than genuine
  extraction failure.

Only the residual — H2 cases that are *also* adjudicated `GOLD_RIGHT` (genuine model error) — is
unambiguously "the model didn't retrieve this and it should have." That residual, not the raw
0.694, is the number that should drive the focused-lanes plan's prioritization.

## 3. Goal, hypotheses, kill-criterion

- **Goal:** decompose Diagnosis's evidence-recall false negatives (the gold-side misses inside the
  0.694 GEPA figure) into {H1 cardinality artifact} / {H2 genuine-divergence but
  `MODEL_DEFENSIBLE`/`BOTH_DEFENSIBLE`} / {H2 genuine-divergence and `GOLD_RIGHT`}, and recompute
  what fraction of Diagnosis's contribution to the GEPA→hybrid evidence-recall gap survives in the
  last bucket alone.
- **H-inflated (primary):** a majority of Diagnosis's `source_near` FNs fall in H1 or
  `MODEL_DEFENSIBLE`-H2 — i.e., the same consolidation mechanism that inflates the scored
  `clinical_headline` gap also inflates the evidence-recall gap, and the genuine-retrieval residual
  is materially smaller than 0.694 suggests.
- **H-genuine (the null the plan is testing against):** most Diagnosis `source_near` FNs are H2 and
  `GOLD_RIGHT` — the model really did not produce any text near those gold concepts, and
  evidence-recall is measuring a real, separate retrieval gap that the consolidation finding does
  not explain away.
- **Kill-criterion / decision threshold:** if H1 + `MODEL_DEFENSIBLE`-H2 account for **< 30%** of
  Diagnosis's `source_near` FNs, H-genuine stands — the focused-lanes plan's framing is reinforced
  for Diagnosis specifically and this plan ends with a confirmatory negative (a useful result: it
  rules out the inflation hypothesis rather than leaving it as an open doubt). If **≥ 50%**,
  H-inflated is confirmed and this materially revises the "build more retrieval" priority — write a
  status-correction note on the evidence-decomposition doc and the focused-lanes plan (mirroring
  the status note already added to `exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md`),
  and reframe the next GEPA-workstream lever toward consolidation-aware keying. Between 30–50% is
  a genuine partial result — report both numbers, do not force a binary verdict.

## 4. Scope: Diagnosis only, dev140, zero new LLM calls

- **Task surface:** dev140 Diagnosis family, on the SAME cached GEPA per-family run used by both
  the evidence-decomposition doc and the canonical row-analysis
  (`exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628`, registry-confirmed
  `clinical_headline_diagnosis_f1=0.6617`). No new model calls — this is pure re-analysis of
  predictions, gold, and the adjudication CSV already on disk.
- **Why Diagnosis only:** it is the family with fresh, granular, per-concept adjudication data
  (209 verdicts, today). SF's Phase 6/7 adjudication exists but is keyed on a different metric
  (state-presence, not phrase-substring concept identity) and the cardinality-artifact mechanism
  (H1) is specific to entity-tagged phrase matching — it does not obviously transfer to SF's
  representation. Prescription and Investigations have no adjudication data at all (would need a
  fresh adjudication pass — out of scope, a candidate for a separate future plan, not bundled in
  here per BP2's escalate-only-when-needed discipline).
- **Deterministic repairs allowed:** none — this is read-only diagnosis of an existing metric's
  mechanics, not a fix.
- **Split/inspection rights:** dev140 only (already authorized); `test60` untouched.
- **No GEPA optimization, no prompt changes.** This plan only re-interprets numbers that already
  exist; it does not propose any new run.

## 5. Method (phased)

### Phase 0 — instrumentation (no new measurement, just wiring)

Write `experiments/exectv2_dx_evidence_recall_consolidation_check.py`, zero-LLM, reusing:

- `gepa_data.load_dev_letters()` + the existing `_pred_letters(run_id)` loader pattern (already
  built in `exectv2_dx_canonical_row_analysis.py` and `exectv2_genuine_recall_analysis.py`) for
  gold/pred `ExectLetter` objects.
- `_dx_canonical/_index.json`'s `missed_concepts` per letter (the 92 Dx misses) as the universe to
  classify.
- `_dx_canonical/_adjudication.csv`'s verdict per `(letter, MISSED, concept)` (already computed
  today) as the ground-truth label for each miss.
- `scoring/match.py`'s `_first_overlapping_prediction` logic, called twice per gold Diagnosis
  annotation: once as the library does it (respecting `used_pred`, reproducing the official 0.694
  Dx ev-recall figure as a sanity check), and once **ignoring `used_pred`** (does *any* predicted
  Diagnosis annotation's phrase overlap at all, regardless of whether another gold annotation
  already claimed it). The difference between these two checks isolates **H1** cleanly: "matched
  without cardinality constraint, unmatched with it" = a cardinality-artifact FN.
- For gold annotations that are FN even with `used_pred` ignored (no overlapping predicted
  Diagnosis phrase exists at all): this is **H2**. Cross-reference against the entity-agnostic
  check too (any predicted annotation of *any* entity overlapping, not just home-tagged Diagnosis)
  to note — but not act on — cases where the model retrieved the text under a different entity
  label (a related, smaller effect; report separately, do not fold into the H1/H2 split).

**Gate:** the `used_pred`-respecting reproduction must match the registry's recorded Dx
`source_near` figure (or the per-family figure computed live by
`exectv2_gepa_vs_hybrid_evidence_decomposition.py`) before trusting the H1/H2 split — same
self-validation discipline as the canonical row-analysis scripts.

### Phase 1 — the decomposition (the decisive measurement)

For each of the 92 Diagnosis `missed_concepts` (mapped back to the underlying gold
`ExectAnnotation`(s) via the same `_anns_for_keys`-style lookup used in
`exectv2_dx_canonical_row_analysis.py`), classify into exactly one of:

- `H1_CARDINALITY` — overlap exists when `used_pred` is ignored, absent when respected.
- `H2_GENUINE_DIVERGENCE` — no overlap exists either way.

Then cross-tabulate against the adjudication verdict (`GOLD_RIGHT` / `MODEL_DEFENSIBLE` /
`BOTH_DEFENSIBLE`) already recorded for that exact `(letter, MISSED, concept)` triple. Report the
2×3 table (mechanism × verdict) and the single number that answers the kill-criterion: the share
of the 92 misses in `H1_CARDINALITY` + (`H2_GENUINE_DIVERGENCE` ∩ `MODEL_DEFENSIBLE` or
`BOTH_DEFENSIBLE`) versus the share in `H2_GENUINE_DIVERGENCE` ∩ `GOLD_RIGHT` (the only
unambiguous "real, attributable retrieval miss" bucket).

**This phase is the whole plan's decision point.** Apply §3's kill-criterion and stop — no second
round of refinement, no new hypothesis chase, regardless of outcome (BP9/BP2 discipline: one
bounded measurement, write the result).

### Phase 2 — propagation (only if H-inflated is confirmed or partially confirmed, ≥30%)

- Add a status-correction note to `exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md`
  (same pattern as the note already added to the plateau synthesis doc on 2026-06-30: preserve the
  original doc's text as history, append a dated correction banner, do not rewrite it).
- Revise the priority framing in `exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md`'s open
  status: if a material share of "missing retrieval" was actually present-but-mis-keyed, that
  argues for investing further in the deterministic-projection / consolidation-aware-keying lever
  (which Phase 3 of that plan already validated as cheap and effective for Dx, 0.703→0.792) ahead
  of further recall-lane GEPA optimization, rather than as an equal-weight alternative.
- No manuscript change is anticipated from this phase alone — the manuscript already states the
  GEPA workstream's numbers as development-surface, non-paper-comparable diagnostics (per
  `PROJECT_STATUS.md`); this plan's output stays inside the GEPA-workstream research docs unless
  it changes a number the manuscript actually cites.

### Phase 3 — optional SF extension (only if Phase 1 clearly generalizes and budget allows)

Not committed to. If Phase 1's mechanism is confirmed and strong, a parallel check on SF using the
existing Phase 7 adjudication (`_sf_canonical/_adjudication.csv`) is a natural follow-up, but SF's
metric (`state_profile`, type-agnostic per-letter state presence) does not share the same
phrase-substring/`used_pred` matching logic, so it needs its own mechanism hypothesis rather than a
direct port of Phase 1's method. Scope this as a fresh, separate predeclaration if pursued — do not
fold it into this plan's stop rule.

## 6. Output

- `experiments/exectv2_dx_evidence_recall_consolidation_check.py` (committed, reusable).
- A short doc, `docs/experiments/exectv2/diagnosis/exectv2_dx_ev_recall_consolidation_check_<date>.md`,
  reporting: the self-validation check (reproduces 0.694), the 2×3 mechanism×verdict table, the
  single decision number, and the verdict against §3's kill-criterion.
- Status-correction notes on the two GEPA-workstream docs named in Phase 2, conditional on outcome.

## 7. Non-goals (explicit, to keep this bounded)

- No new GEPA optimization run, no prompt changes, no new model calls.
- No re-litigation of the Diagnosis adjudication verdicts themselves (treat today's 209 verdicts as
  given ground truth for this plan; if they are later revised, this plan's numbers would need a
  re-run, but that is not anticipated here).
- No Prescription/Investigations extension (no adjudication data exists for them).
- No `test60` or full-200/holdout inspection.
- SF extension is explicitly deferred to a future, separately-predeclared plan (§5 Phase 3), not
  assumed.
