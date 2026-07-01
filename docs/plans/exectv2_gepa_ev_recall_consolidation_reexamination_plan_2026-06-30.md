> **Status: HISTORICAL** — design record only. See [`ACTIVE_ROADMAP.md`](ACTIVE_ROADMAP.md) and [`recent_plan_rationalisation_2026-06-25.md`](recent_plan_rationalisation_2026-06-25.md).

# Plan — does gold-consolidation inflate the GEPA-vs-hybrid evidence-recall gap?

Status: **EXECUTED, ALL FOUR PHASES COMPLETE (2026-06-30) — the full KEY_FAMILIES sweep is done.**
Diagnosis (Phase 1): H-inflated CONFIRMED (86/92 = 93.5%, well above the ≥50% threshold). Full
result: `docs/experiments/exectv2/diagnosis/exectv2_dx_ev_recall_consolidation_check_2026-06-30.md`.
Phase 2 propagation done: status-correction notes added to
`exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md` and
`exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md`. **Phase 3 (SF extension) PURSUED and
CLOSED same-day**, per a fresh predeclaration written into §5 below (Phase 1's method does not
port directly — see that section): H-inflated CONFIRMED for SF too under both a strict and a plain
reading (83.3% / 61.1%, both >> 50%), but with a materially larger genuine-error residual than Dx's
(38.9% vs 7.6%). Full result:
`docs/experiments/exectv2/seizure_frequency/exectv2_sf_ev_recall_consolidation_check_2026-06-30.md`.
**Phase 4 (Prescription + Investigations extension) PURSUED and CLOSED same-day**, per a fresh
predeclaration written into §5 below (user-requested completion of the sweep): a SPLIT result —
Investigations is a clean negative (H-genuine stands, 25.9–29.6%, both readings, the lowest
H-inflated share of any family, no correction needed) while Prescription crosses the H-inflated
threshold but only barely (52.2%, one case from the null) and via a different, unanticipated
mechanism (spelling/transcription divergence, not gold multiplicity). Full result:
`docs/experiments/exectv2/exectv2_rx_inv_ev_recall_consolidation_check_2026-06-30.md`. Same
propagation pattern applied to both docs above, extending (not replacing) the Dx+SF banners.
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

### Phase 3 — SF extension (PURSUED 2026-06-30; fresh predeclaration per this section)

Phase 1's mechanism was confirmed and strong (93.5% >> 50%), triggering this follow-up per §5's
condition. Executed same-day as a self-contained predeclaration, per the original §5's instruction
not to port Phase 1's method directly.

**Why Phase 1's method does not port directly.** Phase 1 started from `clinical_headline`
(concept-key) misses — a population *upstream* of `source_near` — and asked whether those same
misses were *also* `source_near` FNs. SF's scored metric, `state_profile`, operates at a completely
different unit (a per-letter, type/count-agnostic set of 4 states: seizure-free / active-rate /
changed / unknown) than `source_near`'s per-annotation phrase-overlap matching; there is no
annotation-level correspondence between a `state_profile` miss and an individual gold
`SeizureFrequency` mention, so Phase 1's "start from the scored metric's miss list" step has no SF
analog. The existing SF adjudication (`_sf_canonical/_adjudication.csv`, Phase 7, 2026-06-29) is
keyed at the *letter* level (53 letters with a `state_profile` mismatch, one verdict per letter) on
a *different model run* (`exectv2_gepa_sf_verify_gpt41mini_20260628`, the two-stage SF-verify
program) than the GEPA-best run (`exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628`) the
evidence-decomposition doc's 0.694 figure is computed on — so it cannot be cross-referenced against
individual `source_near` misses on the relevant run either by unit or by population.

**Reframed mechanism hypothesis (SF-specific).** Apply the H1/H2 split directly to SF's own
`source_near` FN population (there is no intermediate metric layer to filter through first):

- **H1_CARDINALITY** — for a missed gold `SeizureFrequency` annotation, an overlapping predicted
  `SeizureFrequency` phrase exists but was already claimed by another gold annotation in the same
  letter (`used_pred` exhaustion). Because this can only happen when *multiple* gold annotations
  compete for the same predicted text, an H1 case is itself direct evidence of the same
  gold-multiplicity pattern Phase 1 found for Diagnosis (one underlying clinical fact, multiple gold
  tags), now observed structurally rather than inferred from an adjudication.
  - **H2_GENUINE_DIVERGENCE** — no overlapping `SeizureFrequency` prediction exists at all, with or
    without cardinality.

Each case (H1 and H2 alike) is then given a **fresh** 3-way clinical verdict (`GOLD_RIGHT` /
`MODEL_DEFENSIBLE` / `BOTH_DEFENSIBLE`), using the exact verdict taxonomy already validated and
reused across the Dx canonical adjudication and the SF Phase 7 adjudication (defined in
`experiments/exectv2_sf_canonical_adjudication.py`'s docstring) — there is no existing verdict for
this exact population (annotation-level `source_near` FNs on the GEPA-best run), so this is a new,
bounded adjudication pass, not a re-read of an old one.

**Population, scope, kill-criterion.** GEPA-best run, dev140, `SeizureFrequency` only. Official
`source_near` SeizureFrequency: tp=115, fp=48, **fn=72**, recall=0.6150 (reproduced live by the
Phase-3 script as its own self-validation gate, mirroring Phase 1's discipline). All 72 FNs are
adjudicated (comparable size to Dx's 92, full coverage rather than a sample). Same kill-criterion as
§3, applied to this SF-specific 72-case population: H-inflated (H1 + H2-but-defensible) ≥50%
confirms, <30% the null stands, 30–50% is a reported partial. Zero new LLM calls for the mechanical
H1/H2 split; the clinical verdicts are produced by attentive reading of each case's full
letter-text + gold/prediction substrate (the same kind of judgment call Phase 7 and the Dx
adjudication made), not a model call against the task's own LM.

**Result:** see `docs/experiments/exectv2/seizure_frequency/exectv2_sf_ev_recall_consolidation_check_2026-06-30.md`.

### Phase 4 — Prescription + Investigations extension (PURSUED 2026-06-30; fresh predeclaration)

User-requested completion of the sweep across all four `KEY_FAMILIES` after Dx (Phase 1) and SF
(Phase 3) both confirmed H-inflated. Originally out of scope (§3/§7 non-goals: "no adjudication
data exists for Rx/Inv... a candidate for a separate future plan, not bundled in here") — scoped
here as that separate plan, mirroring Phase 3's structure.

**Why this might NOT generalize (the live open question).** Both Dx and SF are the two
`clinical_headline` entities in `_DEDUPING_HEADLINE_ENTITIES` (`scoring/match.py`) — the headline
metric **collapses** same-unit gold duplicates within a letter for these two families only.
Prescription and Investigations are counted **per-occurrence** instead (no collapsing). The
cardinality-artifact mechanism (H1) found in both prior phases is plausibly *caused* by the
deduping convention: annotators are free to tag a clinical fact exhaustively/multiply because
scoring will later collapse it, which is exactly the setup that produces sibling gold annotations
competing for one predicted phrase. Rx/Inv lack that incentive structure, so this phase may
legitimately return a clean negative (mechanism doesn't transfer) rather than a third confirmation
— that is itself a useful, completing result, not a failure of the check.

**Mechanism hypothesis:** identical structural definition to Phase 3 (H1/H2 applied directly to
each family's own `source_near` FN population, no `clinical_headline`-level intermediate list,
since neither family's headline unit is annotation-keyed the same way Dx's concept-key is). Fresh
clinical adjudication required (no prior per-case verdict exists for either population), same
`GOLD_RIGHT` / `MODEL_DEFENSIBLE` / `BOTH_DEFENSIBLE` taxonomy.

**Population, scope, kill-criterion.** GEPA-best run (`exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628`),
dev140. Official `source_near`: Prescription tp=183/fp=21/**fn=23**/recall=0.888; Investigations
tp=109/fp=2/**fn=27**/recall=0.801 (both reproduced live as the self-validation gate). All 50 cases
adjudicated (full coverage, both families small enough not to need sampling). Same kill-criterion
as §3/Phase 3, applied **per family** (not pooled, since the two families' headline conventions
differ from each other as well as from Dx/SF): ≥50% confirms H-inflated for that family, <30% the
null stands, 30–50% partial. Zero new LLM calls for the mechanical split; fresh clinical adjudication
for verdicts, same discipline as Phase 3 (parallel independent reviewers, full letter substrate,
judge fresh from the letter not from the mechanism label).

**Result:** see `docs/experiments/exectv2/exectv2_rx_inv_ev_recall_consolidation_check_2026-06-30.md`.

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
- No `test60` or full-200/holdout inspection.
- These non-goals reflect the plan's ORIGINAL scope (Diagnosis-only). Both deferrals named here were
  later superseded by fresh, separately-predeclared extensions, executed same-day: the SF deferral by
  §5 Phase 3, and the "no Prescription/Investigations extension" item by §5 Phase 4. See the status
  line at the top of this document for the executed results.
