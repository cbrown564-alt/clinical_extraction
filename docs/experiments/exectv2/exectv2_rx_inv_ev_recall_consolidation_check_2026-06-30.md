# Does gold-consolidation inflate the GEPA-vs-hybrid evidence-recall gap? — Prescription + Investigations check

Status: **CLOSED. SPLIT RESULT: Prescription H-inflated CONFIRMED, but barely and via a
DIFFERENT mechanism than Dx/SF (52.2%, driven mostly by annotation/letter typos, not gold
multiplicity); Investigations H-genuine STANDS, the first clean negative in this plan's four-family
sweep (25.9–29.6%, both readings < 30%).** Date: 2026-06-30. Owner: ExECTv2 GEPA workstream /
predecessor-lessons application follow-up.

**Follow-up (2026-07-01): the §4 MRI-anchoring hypothesis was tested and is a NEGATIVE.** A
dedicated GEPA lane (`experiments/gepa_investigations_lane_deepseek_reasoner_exectv2.py`,
run `exectv2_gepa_investigations_lane_deepseekreasoner_20260630`) reseeded ONLY the
Investigation predictor with an explicit "check each modality independently, don't let MRI
crowd out EEG" instruction, task model `deepseek/deepseek-reasoner`, Diagnosis/SF/Prescription
frozen at their unchanged seeds via a single-predictor GEPA component selector. Result:
Investigations headline 0.9254 / `source_near` recall 0.9412 — statistically indistinguishable
from the existing DeepSeek-chat baseline that used NO Investigation-specific instruction at all
(`exectv2_gepa_baseline_multifamily_deepseekchat_20260628`: headline 0.9259 / recall 0.9412,
identical to 4 decimals), despite ~2.5h/~4x the wall-clock (reasoning tokens genuinely engaged,
not a routing no-op). **Conclusion: the DeepSeek model-family swap itself, not a targeted
instruction or extra reasoning compute, is what closed Investigations' MRI/EEG gap** — the
mini-era anchoring bias this doc diagnosed does not require dedicated engineering to fix once
the task model changes off gpt-4.1-mini. No further Investigations-lane work is planned.

Executes: `docs/plans/exectv2_gepa_ev_recall_consolidation_reexamination_plan_2026-06-30.md` Phase 4
(Prescription + Investigations extension, fresh predeclaration written into that plan's Phase 4
section, user-requested completion of the sweep across all four `KEY_FAMILIES` after Dx and SF both
confirmed H-inflated).

Companions:
- `docs/experiments/exectv2/diagnosis/exectv2_dx_ev_recall_consolidation_check_2026-06-30.md` —
  Phase 1, Diagnosis (93.5% H-inflated).
- `docs/experiments/exectv2/seizure_frequency/exectv2_sf_ev_recall_consolidation_check_2026-06-30.md`
  — Phase 3, SeizureFrequency (83.3% / 61.1% H-inflated, two readings).
- `docs/research/exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md` — the doc whose
  evidence-recall framing this extends to the remaining two families.

## 1. Question

Phase 1 (Dx) and Phase 3 (SF) both found the cardinality/gold-multiplicity mechanism inflates
`source_near` evidence-recall misses for the two `clinical_headline`-**deduping** entities
(`_DEDUPING_HEADLINE_ENTITIES = {"Diagnosis", "SeizureFrequency"}` in `scoring/match.py` — the
headline metric collapses same-unit gold duplicates within a letter for these two families only).
Prescription and Investigations are scored **per-occurrence** instead — no collapsing. The plan's
Phase 4 predeclaration named the live open question directly: the cardinality-artifact mechanism
(H1) is plausibly *caused* by the deduping convention (annotators tag exhaustively because scoring
will later collapse it), and Rx/Inv lack that incentive — so this phase might legitimately return a
**clean negative** rather than a third confirmation, and that would itself be a useful, completing
result rather than a failure of the check.

## 2. Method

`experiments/exectv2_rx_inv_evidence_recall_consolidation_check.py` (mechanical H1/H2 split per
family, zero LLM calls, structurally identical to the SF Phase 3 script — applies the split directly
to each family's own `source_near` FN population since neither family has a `clinical_headline`-level
intermediate annotation-keyed miss list the way Dx's does) +
`experiments/exectv2_rx_inv_evidence_recall_finalize.py` (merge + per-family cross-tab; case IDs are
only unique *within* a family, so all matching is keyed on `(entity, case_id)`).

**Self-validation gate (both families, GEPA-best run
`exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628`):** the script's own
`_first_overlapping_prediction`-respecting trace reproduces the official `source_near` figures
exactly — Prescription tp=183/fp=21/**fn=23**/recall=0.8883, Investigations
tp=109/fp=2/**fn=27**/recall=0.8015 — **PASS** for both.

For each FN, classified the mechanism (identical definition to SF Phase 3):

- **H1_CARDINALITY** — an overlapping predicted phrase exists but was claimed by a sibling gold
  annotation of the same family first.
- **H2_GENUINE_DIVERGENCE** — no overlapping same-family predicted phrase exists at all.

No prior per-case clinical verdict exists for either population (the plan's original non-goals
explicitly excluded Rx/Inv for this reason). All 50 cases (23 Rx + 27 Inv, full coverage, no
sampling) were given a full substrate (letter text, the missed gold mention, all gold and predicted
same-family mentions in that letter, other-entity gold context) and freshly adjudicated by 4 parallel
reviewers (general-purpose agents, one family-and-range each: Rx 1–12, Rx 13–23, Inv 1–14, Inv
15–27) using the same 3-way taxonomy as the Dx and SF adjudications — `GOLD_RIGHT` / `MODEL_DEFENSIBLE`
/ `BOTH_DEFENSIBLE` — explicitly instructed to judge each case fresh from the letter, not from the
mechanism label.

## 3. Result

### Prescription (23 `source_near` FNs)

| mechanism | GOLD_RIGHT | MODEL_DEFENSIBLE | BOTH_DEFENSIBLE | total |
| --- | ---: | ---: | ---: | ---: |
| H1_CARDINALITY | 0 | 4 | 0 | 4 (17.4%) |
| H2_GENUINE_DIVERGENCE | 11 | 8 | 0 | 19 (82.6%) |
| **TOTAL** | **11 (47.8%)** | **12 (52.2%)** | **0** | **23** |

Predeclared formula and plain-verdict-only reading **coincide exactly** here (H1's
`GOLD_RIGHT` subset is 0/4, so there is no divergence between the two formulas): **H-inflated =
12/23 = 52.2%**, **H-genuine = 11/23 = 47.8%**. **VERDICT: H-inflated CONFIRMED, but by a single
case** — the result sits on a knife's edge of the ≥50% threshold (flipping one case's verdict would
cross back under it).

**This is not the same mechanism as Dx/SF.** Of the 12 "inflated" cases, only 4 (33%) are
H1_CARDINALITY (the dedup-linked cardinality pattern: gold double-tags one drug at a header mention
and a narrative restatement — e.g. `EA0047`'s Clobazam and Sodium Valproate, `EA0104`'s
Lamotrigine, `EA0182`'s Lamotrigine — and the model's one consolidated prediction reasonably covers
both). The other 8 (67%) are an **unanticipated mechanism specific to Prescription**: the
`source_near` substring check fails because of a **spelling/transcription typo**, not gold
multiplicity — either the gold annotation span itself is mis-typed (`Lamotrigne`, `Lacosmaide`,
`Carbmazapine`, `EPlim`, `zobisamide`) or the source letter itself misspells the drug
(`lamtorigine`, `oxcarbazine`) and the model normalized to the correct spelling — in every case the
model's prediction carries an identical CUI/dose/frequency to gold, just under different surface
text that the literal substring check can't bridge. One further case (`EA0093`) is a brand/generic
name split (gold tagged the brand "Episenta", the model predicted the generic "Valproate" named in
the same sentence) — also not cardinality-related.

The 11 genuine misses are clean: every one is a **second or third drug entirely absent** from the
model's Prescription predictions for that letter in a polypharmacy list (e.g. `EA0038`'s
Carbamazepine alongside Zonisamide+Clobazam; `EA0158`'s Perampanel alongside three other AEDs;
`EA0121`/`EA0158`'s Midazolam rescue medication never predicted in any form).

### Investigations (27 `source_near` FNs)

| mechanism | GOLD_RIGHT | MODEL_DEFENSIBLE | BOTH_DEFENSIBLE | total |
| --- | ---: | ---: | ---: | ---: |
| H1_CARDINALITY | 1 | 7 | 0 | 8 (29.6%) |
| H2_GENUINE_DIVERGENCE | 19 | 0 | 0 | 19 (70.4%) |
| **TOTAL** | **20** | **7** | **0** | **27** |

- **Predeclared formula**: H-inflated = 8/27 = **29.6%**, H-genuine = 19/27 = **70.4%**.
- **Plain verdict-only reading** (the one H1 case that flipped to `GOLD_RIGHT`, `EA0156`, moves
  buckets): H-inflated = 7/27 = **25.9%**, H-genuine = 20/27 = **74.1%**.

**Both readings land just under the < 30% threshold. VERDICT: H-genuine STANDS for
Investigations** — the cleanest negative result in this plan's four-family sweep (Dx 93.5%,
SF 83.3%/61.1%, Rx 52.2%, Inv 25.9–29.6%, monotonically decreasing toward the null).

Every H2_GENUINE_DIVERGENCE case (19/19) was adjudicated `GOLD_RIGHT` — none were
`MODEL_DEFENSIBLE`, the cleanest mechanism-verdict correlation of any family/bucket examined across
this whole plan. The dominant pattern, present in the large majority of the 20 genuine misses: in a
letter reporting **both** an MRI and an EEG, the model's Investigations predictions contain an MRI
mention but **zero EEG mentions of any form** — not a mis-keyed or consolidated EEG, an absent one
(e.g. `EA0004`, `EA0005`, `EA0026`, `EA0033`, `EA0044`×2, `EA0049`, `EA0050`, `EA0067`, `EA0079`,
`EA0111`, `EA0123`, `EA0127`, `EA0131`, `EA0179`, `EA0188`, `EA0200`×2). This is a structural,
test-type-specific extraction gap (MRI-biased, EEG-under-extracted), not a representation or
keying problem. The 7 H1_CARDINALITY-and-`MODEL_DEFENSIBLE` cases are the expected
header+narrative-restatement duplicate pattern (e.g. `EA0046`'s and `EA0132`'s repeated mention of
one abnormal finding). One case (`EA0156`) was structurally H1_CARDINALITY but on fresh reading
covered two clinically distinct EEGs (a normal recent one and an abnormal historical one from 2002)
that the model only partially captured — correctly overridden to `GOLD_RIGHT`, the only
mechanism/verdict divergence found for Investigations (the reviewer flagged this explicitly as the
fresh-judgment check working as intended).

## 4. Interpretation

**The plan's "live open question" is answered with a genuine split, not a clean third
confirmation or a clean third negative — and the split is informative in its own right.**

- **Investigations is the cleanest negative across the whole plan.** No deduping-headline
  convention applies to it, and unlike Prescription, no rescuing alternative artifact (typos,
  synonyms) is propping up the inflated bucket either: 19/19 of its "no overlap anywhere" cases are
  genuine model errors. This directly corroborates the plan's mechanism hypothesis (§2 of the parent
  plan) in the *negative* direction it predicted: without the dedup incentive, `source_near`
  evidence-recall on Investigations is measuring what it claims to measure. **No correction is
  needed** to the evidence-decomposition doc's framing for Investigations.
- **Prescription is a genuine partial result, not a confirmation of the Dx/SF mechanism.** It
  crosses the ≥50% threshold by a single case, but the inflation is mostly **not** the
  gold-multiplicity/cardinality mechanism the parent plan hypothesized — H1_CARDINALITY contributes
  only 4 of the 12 inflated cases. The majority (8/12) is a *different*, previously
  unobserved-in-this-plan artifact: substring-overlap matching is fragile to spelling/transcription
  divergence between gold, the model, and (in two cases) the source letter itself. This is a
  **measurement-mechanics finding distinct from the gold-consolidation finding**, worth its own
  note: `source_near`'s phrase-substring check has no fuzzy-matching tolerance, so a single
  transposed letter in either the gold span or the model's output produces a false "the model never
  retrieved this" reading even when every structured attribute (CUI, dose, frequency) matches
  exactly. A partial correction is warranted for Prescription's evidence-recall framing, but the
  prescription is different from Dx/SF's "re-keying lever" — it points toward **fuzzy/CUI-based
  evidence matching** (already effectively how the *scored* metrics work via CUI, just not how
  `source_near`'s diagnostic checks evidence presence) rather than consolidation-aware projection.
- **Investigations' genuine residual has a specific, actionable shape**, unlike the more diffuse
  "the model didn't retrieve this" framing the evidence-decomposition doc used in aggregate: it is
  concentrated in **EEG under-extraction specifically when an MRI is also present in the same
  letter**, not a general retrieval weakness across all Investigations content. This is a sharper,
  more useful target than "build more retrieval lanes" in general — it suggests the Investigations
  producer lane specifically should be checked for an MRI-anchoring bias that crowds out EEG
  extraction, a concrete, testable hypothesis for a future GEPA Investigations-lane iteration (out of
  scope here — this plan does not propose new runs). **Tested 2026-07-01, NEGATIVE: see the status
  banner at the top of this doc** — a dedicated MRI/EEG-targeted lane matched but did not beat the
  existing untargeted DeepSeek-chat baseline; the model swap, not the instruction, did the work.
- **Across all four families, the share of H-inflated falls monotonically with how strongly the
  family is tied to the headline-dedup convention**: Diagnosis 93.5% (full dedup entity, dominant
  consolidation pattern) > SeizureFrequency 61.1–83.3% (full dedup entity, larger genuine residual
  already known from Phase 7's gold-IAA ceiling) > Prescription 52.2% (no dedup entity, inflation
  driven by an unrelated typo-matching artifact) > Investigations 25.9–29.6% (no dedup entity, clean
  negative). This ordering is consistent with — though not fully explained by — the dedup-incentive
  hypothesis: it correctly predicts the *direction* (dedup families inflate more) but Prescription's
  intermediate position is explained by a mechanism the plan did not anticipate, not by a weaker
  version of the same one.

## 5. Scope and caveats

- Prescription + Investigations only, dev140, GEPA-best multi-family run, zero new LLM calls for the
  mechanical split. Full coverage (all 23 + 27 FNs), no sampling.
- The fresh adjudication was done by 4 independent parallel reviewers, one scoped to each
  family-and-case-range rather than spanning both families per reviewer; each reviewer flagged
  mechanism/verdict divergences transparently (one in Prescription's batch — `EA0056`'s structurally
  H2-labeled case turned out to be a narrative/header spelling divergence rather than a true
  miss, consistent with the instruction that the mechanism label shouldn't predict the verdict; one
  in Investigations' batch, `EA0156`, described above).
- Zero `BOTH_DEFENSIBLE` verdicts were assigned across all 50 cases — notably different from SF's
  11.1% `BOTH_DEFENSIBLE` share, consistent with Prescription/Investigations being lower-IAA-ambiguity,
  more factually-binary entity types (a drug was or wasn't mentioned; a test was or wasn't performed)
  than SeizureFrequency's inherently fuzzier rate/direction judgments.
- This does not revise the SF Phase 4–7 `state_profile` ceiling findings or the Dx canonical
  row-adjudication, which used their own adjudication-based methodology on different metrics/runs.
- No deterministic repairs, no GEPA optimization, no prompt changes — pure re-analysis plus one
  bounded fresh clinical adjudication, per the plan's scope discipline.
- Prescription's 52.2% result is reported with explicit knife's-edge framing (§3) rather than a flat
  "CONFIRMED" — per this plan's own discipline (Dx/SF docs) of reporting partial/marginal results
  transparently rather than forcing a clean binary narrative onto a one-case margin.

## 6. Propagation

- Status-correction note added to
  `docs/research/exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md`, extending the
  existing Dx+SF correction banner: Investigations' framing is **validated, not corrected**
  (the only family in the doc's original claim that survives unrevised); Prescription gets a
  **partial, differently-mechanized** correction noting the typo/substring-matching artifact
  rather than gold consolidation as the dominant cause of its inflated share.
- Status note added to `docs/plans/exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md`'s existing
  correction banner, extending the Dx+SF pattern to note the four-family sweep is now complete and
  summarizing the split outcome.
- Plan status line in
  `docs/plans/exectv2_gepa_ev_recall_consolidation_reexamination_plan_2026-06-30.md` updated to
  reflect Phase 4 as executed.

## 7. Artifacts

- `experiments/exectv2_rx_inv_evidence_recall_consolidation_check.py` — Phase 0/1 mechanical split +
  substrate dump for both families, committed, reusable, zero-LLM.
- `experiments/exectv2_rx_inv_evidence_recall_finalize.py` — merges adjudication batches, computes
  the per-family cross-tab and both decision-number readings, writes
  `_rx_inv_ev_recall/_adjudication.csv`.
- `experiments/exectv2_rx_inv_evidence_recall_consolidation_check.json` — full per-case data
  (mechanism, verdict, reason, substrate) and final per-family tallies.
- `_rx_inv_ev_recall/` — 50 per-case adjudication substrate `.md` files (split into `prescription/`
  and `investigations/` subdirectories) + `_adjudication.csv` (case-level CSV: entity, letter,
  mechanism, verdict, missed text, reason).
