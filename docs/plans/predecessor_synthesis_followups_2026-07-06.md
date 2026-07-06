# Implementation plan — predecessor-synthesis follow-ups (7 items)

Status: **IN PROGRESS — items 1, 2, 3, 4, 6, 7 done; 5 pending.** Date: 2026-07-06.
Owner: ExECTv2 + Gan2026 workstreams.
Branch context: `exectv2-capacity-execution-gap-generalization`.
Provenance: triggered by the 2026-07-06 read of the four predecessor-lessons
docs (`dissertation_clean`, `dissertation-experiments`, `dissertation-recursive`,
`dspy_extraction`) under `docs/research/predecessor_lessons/`. Each item below
cites the specific predecessor finding that motivates it.

This plan sets up seven follow-ups. **Items 6 and 7 are quick audits that may
reshape the framing of 2 and 3** — they should land first even though they are
listed later, because their outcomes change how the experimental items are
predeclared. Items 1 and 5 are documentation/infrastructure; 2, 3, 4 are
experiments that each warrant their **own separately-frozen predeclaration**
(this plan is the umbrella, not the predeclarations). Split discipline per the
research protocol: dev140 / labelled synthetic panel only; Gan test450 and
ExECT holdout/full-200 row-level inspection remain blocked.

> **Status snapshot (2026-07-06 close):** items **1** (`/gold-noise` tab),
> **6** (`multiple` sentinel audit), **7** (policy-wall audit), **2**
> (closed-option direction selector), **4** (no-model medication oracle), and
> **3** (retrieval-highlight salience priming) are **complete**. Item 5 remains
> pending. The three headline outcomes so far: **item 2 refutes the
> "fundamental" framing** of the SF capacity-vs-execution gap (closed-option
> recovers +0.0552 dev140 `state_profile_directional` where the free-write
> family regressed); **item 4 confirms the dspy medication-ceiling framing** —
> deterministic-only (`_extract_prescriptions` as the final system, zero LLM)
> reproduces the cited hybrid `clinical_headline` **exactly** (0.9615 dev140 /
> 0.9278 full-200, gap +0.0000 on both), so the LLM contributes **zero** to the
> Prescription headline; **item 3 is the diversifying negative on the input
> axis** — retrieval-highlight priming does *not* move direction (Arm B − Arm A
> = −0.0068 dev140 `state_profile_directional`, < the +0.02 kill band), so the
> gap **survives a change of input** even though item 2 showed it does *not*
> survive a change of generation contract. Combined cross-family claim: the
> SF-direction gap is **contract-sensitive but input-robust** (not fundamental;
> the lever is the closed-option contract, not input salience-priming; on this
> surface retrieval works by lookup, not priming). See the per-item status
> stamps and outcome notes below, and the linked audit/experiment docs.
> Remaining: item 5 (raw-vs-projected decomposition, zero LLM).

---

## How the seven items relate (read this first)

The seven items are not independent. They form three groups plus two audits:

- **Group A — the SF-direction research bet (items 2 + 3).** Both test whether
  the capacity-vs-execution gap, previously bounded by four measured negatives
  *all in the free-write-then-arbitrate architecture family*, survives a
  *different* architecture. Item 2 = closed-option selector (dspy pattern) —
  **DONE 2026-07-06, REFUTES "fundamental"** (+0.0552; the gap does not survive a
  change of *generation contract*); item 3 = retrieval-highlight input-priming
  (dissertation-recursive pattern) — **DONE 2026-07-06, HIGHLIGHT IS NOT THE
  LEVER** (Arm B − Arm A = −0.0068 < the +0.02 kill band; the gap **does** survive
  a change of *input*). The two legs have **opposite outcomes on the two axes**:
  contract-sensitive, input-robust. Combined claim: the gap is not fundamental;
  the lever that deploys the capacity is the closed-option contract, not input
  salience-priming (on this surface retrieval works by lookup, not priming).
- **Group B — honest-headline infrastructure (items 1, 4, 5).** Item 5
  decomposes the cited 0.9189 into raw-LLM vs deterministic; item 4 establishes
  the no-model medication ceiling — **DONE 2026-07-06, confirms dspy framing
  (deterministic-only == cited hybrid headline, gap +0.0000 on both splits)**;
  item 1 surfaces all gold-quality evidence in a dedicated frontend tab —
  **DONE 2026-07-06**. Together they answer the dspy "bridge-inflation" critique
  and make the gold-noise story (corroborated at ~28–29% across three codebases)
  inspectable rather than merely cited.
- **The two audits (items 6, 7).** Both are cheap, both can change framing, so
  both ran before the Group A predeclarations were finalized. **Both DONE
  2026-07-06.** Item 6's outcome (unknown-vs-counted divergence dominates, not
  2-vs-3) is absorbed into item 2's predeclaration; item 7's outcome (2 of 32
  evolved seeds clear the policy wall; research-only, not the production path)
  bounds item 2's framing to the un-walled raw program.

Sequencing recommendation (original): **6 → 7 → 5 → 4 → 1 (parallel) → 2
(predeclare) → 3 (predeclare).** Items 1 and 5 have no LLM cost and no
split-discipline risk; item 4 is a zero-LLM ceiling probe; items 2 and 3 are the
only costed, fresh-protocol experiments. **Actual execution order:** 6 → 7 → 2
(per the user's "run 6 & 7 first" direction); items 1 and 4 landed separately
earlier on 2026-07-06. Items 5 (zero-LLM) and item 3 (costed) remain.

---

## Item 1 — Dedicated "gold noise" frontend tab  ✅ DONE (2026-07-06)

Landed as the read-only `/gold-noise` route. Backend:
`src/clinical_extraction/observatory/routers/gold_noise.py` (5 GET endpoints
over the 4 ExECT ledgers + Gan RQ10 audit + gold-data issues + hypothesis
registry, behind a unified `GoldNoiseItem` adapter) + response models in
`responses.py` + registration in `api.py`. Frontend: `app/gold-noise/page.tsx`
+ `components/observatory/GoldNoisePanel.tsx` (orchestrator) +
`GoldNoiseViews.tsx` (matrix/views, split to respect the 600-line frontend
gate) + types in `lib/types/observatory.ts` + fetchers in `lib/api/index.ts` +
mock data under `frontend/public/mock-data/gold-noise/` + Navbar chip.
**Implementation note:** the spec's four "ceiling" percentages are the live
`verdict == "gold_right"` fraction of each ledger (SF 19/64=29.7%, Dx
31/199=15.6%, Rx 26/36=72.2%, Inv 23/35=65.7%), derived at request time rather
than hard-coded — verified to reproduce against the on-disk ledgers. 12 pytest
cases in `tests/test_observatory_gold_noise.py`; tsc/eslint/jest green.

---

**Motivating predecessor finding.** All four predecessors independently report
that SF gold is noisy: dissertation-recursive 29.2% oracle failure; dspy 13.13%
G1 mismatches + `multiple` sentinel problems + specific defective rows
(GAN009937, GAN000174); dissertation-experiments names further defensible-model-
wrong-gold cases. Our own ceilings (SF 28.8% / 29.7%, Dx 14.8%/15.6%, Rx 72.2%,
Inv 65.7%) corroborate this in a third codebase. **This is the strongest external
validation we have, and it is currently cited as four percentages in
`PROJECT_STATUS.md` rather than made inspectable.** dspy's emphasis on "benchmark
labels are not clinical truth" as a *protected rule* is the framing to match.

**What already exists (do not rebuild).**
- The four `experiments/gold_case_ledger_{diagnosis,seizurefrequency,prescription,investigations}.jsonl`
  files (199 / 64 / 36 / 35 rows) are pure JSONL and already JSON-serializable
  via `GoldCaseRow.to_json_record()` in `experiments/exectv2_ledger/schema.py`.
  Each row embeds the letter text + gold/pred mentions + `mechanism` +
  `verdict` + `provenance{reason}`. This is the per-item evidence backbone.
- `experiments/gold_data_issues.jsonl` (currently 1 row, EA0146) is the right
  schema for a "genuine gold defects" list.
- `experiments/gan2026_rq10_gold_scorer_ambiguity_audit_2026-06-04.json` already
  carries Gan summary + `by_hidden_family` + `by_first_failure_owner` + source-
  row-index lists — group-capable out of the box.
- `experiments/hypothesis_registry.jsonl` (31 entries) maps to a per-family
  hypothesis-history table; `render_dossier.py` already renders it.
- The existing `/gold-audit` tab + `GoldAuditPanel.tsx` is the **canonical
  template** (Pattern B standalone route). It implements the exact UX this tab
  needs: prioritized queue + per-item document inspection + classification +
  write-back + keyboard triage. Clone it; do not invent a new pattern.
- The backend contract to mirror: `src/clinical_extraction/observatory/routers/gold_audit.py`
  + `src/clinical_extraction/observatory/gan2026/gold_audit_store.py`.

**What we build.** A new standalone route `/gold-noise` (Pattern B), backed by
a new FastAPI router that serves the four ExECT ledgers + the Gan RQ10 audit +
`gold_data_issues.jsonl` + the hypothesis registry, behind a unified adapter.

Three inspection levels (the user's explicit requirement):

1. **Summary at scale** — top of page. Per-family ceiling tiles (the four
   percentages with honest numerators: SF 19/64, Dx 31/199, Rx 26/36, Inv
   23/35), cross-project corroboration strip ("dissertation-recursive 29.2%;
   dspy 13.13% G1; this repo 29.7% — three independent codebases"), and a
   stacked-bar of `verdict` × `family` (genuine_model_error / gold_ambiguity /
   metric_convention / instrumentation).
2. **Grouped by issue** — a filterable matrix: rows = `mechanism` (the 7-value
   `Mechanism` enum) or `rq10_class`; columns = family; cells = counts, click-
   through to the item list. Plus a "by letter" grouping (which letters
   accumulate the most gold issues across families — the corpus-property view).
3. **Item-level** — clicking any cell or row opens the existing
   `LetterRenderer` with the gold mention + pred mention highlighted (reuse the
   `findHighlightSpans` pattern from `GoldAuditPanel.tsx:54-75`), the
   `provenance.reason`, the mechanism/verdict badges, and a deep-link into the
   per-letter markdown dossier if present.

**Backend work.**
- New router `src/clinical_extraction/observatory/routers/gold_noise.py`
  exposing `GET /gold-noise/ledgers` (loads the 4 JSONL via the existing
  `load_gold_case_ledger`), `GET /gold-noise/gan-audit` (serves the RQ10 JSON),
  `GET /gold-noise/issues` (`gold_data_issues.jsonl`), `GET /gold-noise/row`
  (single ledger row by family + row_id), `GET /gold-noise/hypotheses`. No
  write endpoint in v1 (unlike `/gold-audit`, this tab is read-only
  inspection — the ledgers are produced by the offline adjudicators, not by
  this tab).
- A unified response model that normalizes the ExECT `GoldCaseRow` and the Gan
  RQ10 rows to a common `GoldNoiseItem` shape `{family, letter_id, kind,
  mechanism, severity, gold, pred, evidence, reason, source}`. The two source
  schemas are incompatible today; the adapter is the main new code.

**Frontend work.**
- `app/gold-noise/page.tsx` (thin `<Suspense>` wrapper, mirroring
  `app/gold-audit/page.tsx`).
- `components/observatory/GoldNoisePanel.tsx` — the panel, modeled on
  `GoldAuditPanel.tsx` but read-only and three-level.
- New fetchers in `lib/api/index.ts` (`fetchGoldNoiseLedgers`,
  `fetchGoldNoiseGanAudit`, `fetchGoldNoiseRow`, `fetchGoldNoiseHypotheses`).
- Types in `lib/types/observatory.ts` next to `GoldAuditRow`.
- Mock JSON under `frontend/public/mock-data/gold-noise/` (ledger sample, gan
  audit, issues) + a branch in `lib/api/mock.ts`'s ladder.
- Navbar registration as a manual chip in `components/Navbar.tsx` (the gold-audit
  pattern, lines 56-66), tone `error` or a new `gold-noise` token.
- No new charting library — hand-rolled Tailwind divs per house style
  (`ConfusionMatrix.tsx` is the model).

**Honest-data caveats the tab must surface (not hide).**
- The Dx 14.8% vs 15.6% discrepancy: 14.8% is the 209-row original canonical
  adjudication; 15.6% is the 199-row consolidated ledger. The tab shows both
  with numerators, not a single rounded number.
- The SF 28.8% → 29.7% drift (pre- vs post-07-03). Show the timestamp.
- Gan RQ10 uses a different class taxonomy than ExECT's `Mechanism` enum — they
  are not directly commensurable and the tab must label the mode, never mix.
  (This mirrors dissertation_clean's "two scoring engines" rule.)

**Success criterion.** A reader can land on `/gold-noise`, see the four ceilings
with numerators, drill into any family → mechanism → individual letter, and read
the gold vs pred mention with the adjudication reason. No new LLM calls. No
change to any ledger, scorer, or projection.

**Out of scope for v1.** Write-back / new adjudication from the tab (the
ledgers are owned by the offline canonical adjudicators); parsing the per-letter
markdown dossiers into structured fields (the ledger rows already embed the
letter text, so dossiers are supplementary).

---

## Item 2 — Build our own candidate-substrate (closed-option selector) for ExECTv2 SF direction  ✅ DONE (2026-07-06) — REFUTES "fundamental"

> **Outcome.** The closed-option selector recovered **+0.0552** dev140
> `state_profile_directional` (0.6552 → 0.7103, +8/30 gold-directional facts)
> with `state_profile` byte-identical (0.7483, no regression), clearing the
> predeclared +0.05 threshold. **Per the frozen predeclaration this REFUTES the
> "fundamental" framing:** the SF capacity-vs-execution gap was an artifact of
> the *free-write generation contract*, not a capacity limit. All four prior
> negatives lived in the free-write-then-arbitrate family; this is a fifth
> measurement in a different family (closed-option select-or-abstain) and it is
> positive. The dspy G32 principle (closed-option > free-write-then-arbitrate)
> transfers to the ExECTv2 SF direction surface. The "fundamental" claim is
> downgraded to **"free-write-family-specific."** Lands between B1 free-write
> post-hoc (+0.07) and B2 free-write hard-emission (−0.0775); succeeds where the
> architecturally-comparable B2 failed because the closed menu avoids the
> cognitive load B2's free-write direction field imposed on the other SF axes.
>
> **Design note (deviation from the umbrella text above).** The plan's described
> menu (`{Increasing, Decreasing, Stable, Same, None}`) used a vocab that does
> not exist in this codebase; the actual closed gold vocab everywhere in
> code/gold/scorer is `{Decreased, Frequent, Increased, Infrequent, Same}`
> (`change.py:3`, `frequency_state_directional`). The frozen predeclaration and
> the driver use the real 5-value vocab, with `Same` doubling as the abstain
> outcome. Additionally the menu was made to carry the **full** 5-label vocab +
> ABSTAIN always (not a regex-gated subset): `rules/change.py` regexes match
> only 7/28 disagreement letters, so gating would have collapsed the experiment
> into a no-op for 21 letters. The closed-option contract constrains the
> *output* (pick from the menu, never free-write), not the *options* — that is
> the honest test of the G32 principle.
>
> **Framing absorbed from prerequisite audits.** Item 6 (unknown-vs-counted
> divergence dominates cross-project comparison, not 2-vs-3) → item 2's claim is
> stated in within-architecture-delta terms (raw 0.6552 → closed-option 0.7103),
> not vs dspy's 90.3% absolute rate. Item 7 (2 evolved seeds clear the policy
> wall; research-only, not the production path) → item 2 ran on the *raw*
> SF-verify program (no evolved seed), so the four motivating negatives are not
> policy-wall artifacts and the refute is clean.
>
> **Artifacts.** Predeclaration:
> `docs/experiments/exectv2/seizure_frequency/exectv2_sf_closed_option_direction_predeclaration_2026-07-06.md`;
> results:
> `docs/experiments/exectv2/seizure_frequency/exectv2_sf_closed_option_direction_results_2026-07-06.md`;
> driver: `scripts/run_exectv2_sf_closed_option_direction_probe.py`;
> hypothesis `sf_closed_option_direction_selector_2026-07-06` (registry entry
> 32). 28 gpt-4.1-mini calls, dev140 only, cached.

**Motivating predecessor finding.** dspy's G32 architecture rests on a principle
we have never tested: **the LLM never free-writes a rate; it picks a label
verbatim from a deterministic candidate menu or abstains to one of two special
labels.** G32 cleared 90.3% monthly on Gan validation. Critically, our four
measured negatives for the SF-direction capacity-vs-execution gap (B2
hard-emission −0.0775, schema-rescue −0.0351, per-key decoupled −0.0142, and
the three-family Phase-0 degeneracy) **all share one architecture family**:
free-write-then-arbitrate. The per-key CORRECT/WRONG adjudicator we tested is
*not* a closed-option selector — it is a keep/drop judge over free-written
tokens. **This is the cross-family test that converts "fundamental within one
architecture family" into either "refuted across families" or "fundamental
across two architecture families."** For the manuscript the latter is
dramatically stronger; the experiment is worth running either way.

**What already exists (the substrate is built — this is a transfer experiment).**
The closed-option pattern is **already implemented in the gan2026 stack** under
different names:
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/candidate_set.py`
  — `CandidateSet`, `ExtractedCandidate` with a closed `CandidateKind` Literal
  (6 values), a `@model_validator` enforcing exactly one detail object matches
  the kind.
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/selected_fact.py`
  — `SelectedCandidateDecision` with `SelectionMode ∈ {single_candidate,
  related_candidate_group, no_reliable_candidate, ambiguous, conflict}` and a
  validator enforcing that defer modes don't select ids. **This is the
  abstention primitive.**
- `.../gan2026/llm/assessment_probe_signature.py` — the LLM signature
  `Gan2026CandidateSetClinicalAssessmentSignature` already enforces "Use only
  candidate_id values that appear in the provided CandidateSet. Never invent,
  renumber, or guess candidate ids" and forbids parser-like normalization.
- `.../gan2026/deterministic/clinical_assessment_assembly.py` —
  `assemble_clinical_assessment` owns the final scored values deterministically.
- The ExECTv2 substrate analogue: `.../exectv2/hybrid/candidate_set.py`
  `build_candidate_set` + `candidate_set_as_payload` (emits
  `{candidate_id, anchor_text, evidence, span, suggested_attributes}`).

**What we build.** A closed-option direction selector for the ExECTv2 SF
direction surface — the exact surface where the gap is bounded by four
negatives. The design:
1. Build a deterministic candidate menu per SF mention of **direction labels**
   `{Increasing, Decreasing, Stable, Same, None}` plus an abstain option —
   sourced from `rules/change.py`'s closed vocab and the surrounding context
   cues, NOT from the LLM. (This reuses the existing `RuleGroup.FREQUENCY_CHANGE`
   builder vocabulary; the new work is emitting a *menu* the LLM selects from
   rather than an `AttributeExtraction` the deterministic layer applies
   directly.)
2. An LLM selector constrained to return a `candidate_id` verbatim OR abstain
   to `None` — never free-write a direction. Mirror the
   `SelectedCandidateDecision` validator (defer modes can't select ids).
3. Deterministic assembly maps the selected id to the final direction.

**Experimental design (the cross-family test).** Same disagreement set as the
existing four SF-direction designs (the 30 gold-directional changed facts across
28 dev140 letters). Predeclare two outcomes before running:
- **REFUTES "fundamental":** the closed-option selector recovers direction at
  ≥ the B1 post-hoc recovery rate (+0.07 dev140). The gap was an artifact of
  the free-write architecture, not a fundamental capacity limit. This is the
  dspy outcome and it would be a major finding.
- **CONFIRMS "fundamental across families":** the closed-option selector also
  fails (regresses or does not recover). This becomes the **fifth** negative,
  from a *different architecture family*, promoting "fundamental" from "4
  negatives in one family" to "5 negatives across two families."

**Split discipline & cost.** dev140 only (the gap is two-split confirmed, so
dev140 is the development surface; test59 frozen). The disagreement set is 30
facts / 28 letters, so the selector arm is ~28–56 LLM calls (one or two per
letter). Cheap relative to the value.

**Why this is the single highest-leverage follow-up.** It is the only item that
can change the *status* of our central claim (from "fundamental within one
family" to either "refuted" or "fundamental across families"). Every other item
strengthens surrounding evidence; this one can move the core thesis.

**Predeclaration requirements (own doc, not this plan).** Hypothesis id, kill
criterion (e.g., "closed-option selector recovers ≥ +0.05 dev140 directional →
refutes fundamental; < +0.02 → confirms across families; in-between →
inconclusive, run the per-key analogue"), frozen seeds, model (gpt-4.1-mini
temp 0 to match B1/B2), and a row-level before/after ledger.

---

## Item 3 — Retrieval-highlight salience priming  ✅ DONE (2026-07-06)

Landed as `scripts/run_exectv2_sf_retrieval_highlight_probe.py` (3-arm probe,
~84 gpt-4.1-mini calls, dev140, temp 0, cached) + predeclaration
(`exectv2_sf_retrieval_highlight_predeclaration_2026-07-06.md`) + results
(`exectv2_sf_retrieval_highlight_results_2026-07-06.md`) + registry entry 33.
**Outcome: HIGHLIGHT IS NOT THE LEVER (diversifying negative on the input
axis).** Arm B (full letter + deterministic `CHANGE_RULES`/`TEMPORAL_RULES`
spans wrapped in `[[HL]]...[[/HL]]`) scored 0.7211 dev140
`state_profile_directional` vs Arm A (raw-letter control, B1 reproduction)
0.7279 — delta **−0.0068**, well inside the `< +0.02` kill band; `state_profile`
byte-identical (0.7483) across all arms (no regression). Arm A reproduced B1
(0.7254 → 0.7279, tp 107 = 107), so the within-run control is valid. Arm C
(highlight-only ablation) 0.6966 — Arm C − Arm B = −0.0245 (within ~0.05) →
**LOOKUP, not priming**: retrieval works by direct lookup on this surface
(different from dissertation-recursive's −32pp priming signature). Mechanism:
the deterministic `CHANGE_RULES` emit `attributes={"FrequencyChange":"..."}`
verbatim, so highlighting a span that *states* the direction for an LLM that
then free-writes the same label is ~no-op (cue and conclusion are the same
string); cue coverage is also partial (11/28 letters, 17/35 mentions). Combined
with item 2, the cross-family claim is now precise: the SF-direction gap is
**contract-sensitive (item 2 refutes) but input-robust (item 3 survives)** — not
fundamental; the lever is the closed-option generation contract, not input
salience-priming. Item 6/7 framings absorbed (within-architecture delta; raw
not policy-walled surface). 12 pytest cases for the deterministic span helpers
(`tests/test_exectv2_sf_retrieval_highlight_probe.py`).

> **Status note (post item 2).** Item 2 already delivered the cross-family
> *refute* of the "fundamental" claim via the closed-option contract. Item 3 is
> therefore now the **diversifying second leg** — it tests the same null
> hypothesis ("the gap is fundamental") along an orthogonal axis (input priming
> vs generation contract). Running it would give a *second* cross-family data
> point from an independent lever. Its value is now corroborative rather than
> thesis-moving: item 2 already changed the claim's status. It remains the only
> other costed fresh-protocol experiment in this plan (~84 calls, dev140).

**Motivating predecessor finding.** dissertation-recursive's Gan winner was
`gpt_5_5 + Gan_retrieval_highlight` (Pragmatic µF1 0.840 vs 0.760 for
cot_label). The decisive evidence is the ablation: `Gan_retrieval_only_ablation`
(spans only, no full letter) scored 0.520 vs 0.840 for highlight — a **−32pp
drop proving retrieval works by salience-priming the input, not by direct
lookup.** Every decoupling mechanism we tested for the SF-direction gap
restructures the *call* (B2 coupled, per-key decoupled, per-letter B1). **None
restructure the *input*.** This is an untested, theoretically-motivated lever:
if the gap is specifically about *coupling cognitive load*, priming the
relevant spans *before* the coupled extraction call could deploy the capacity
that call-restructuring cannot.

**What already exists.** dissertation-recursive used a deterministic regex bank
`_FREQUENCY_SENTENCE_PATTERNS` + `retrieve_frequency_spans()` to select
sentence spans, then fed the whole letter *plus* highlighted spans to the LLM.
Our ExECTv2 substrate has the analogous ingredient:
`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/rules/change.py`
already identifies the `FrequencyChange` cue spans. The new work is to *surface*
those spans to the LLM as highlighted salience cues in the prompt rather than
consuming them deterministically.

**What we build.** A retrieval-highlight variant of the ExECTv2 SF producer:
1. Deterministic span selection: reuse `rules/change.py` matches (and the
   `temporal.py` context anchors) to identify the spans relevant to direction.
2. Prompt augmentation: feed the full letter with the selected spans wrapped in
   explicit highlight markers (e.g., `[[HL]]...[[/HL]]` or a sentence-level
   "↑ salient for direction" tag). Instruction: "the highlighted spans are the
   clinically relevant direction cues; weigh them when extracting." The LLM
   still free-writes the extraction (this is *not* a closed-option selector —
   that's item 2; the two items are independent levers and should not be
   conflated).
3. Three-arm study on the same SF disagreement set:
   - **Arm A (baseline):** current producer, no highlights.
   - **Arm B (highlight):** full letter + highlighted spans.
   - **Arm C (highlight-only ablation):** only the highlighted spans, no full
     letter. This is the dissertation-recursive ablation that proved the
     priming mechanism (−32pp). If Arm C ≈ Arm B, retrieval works by direct
     lookup here too; if Arm C ≪ Arm B, it works by priming — replicating
     dissertation-recursive's mechanism result on a different surface.

**Predeclared outcomes.**
- Highlight recovers direction ≥ +0.05 dev140 → input-scaffolding deploys the
  capacity call-restructuring couldn't; gap is partly about input salience, not
  fundamental.
- Highlight ≈ baseline → input-scaffolding is not the lever for ExECTv2
  direction (Gan finding does not transfer); strengthens "fundamental" along a
  different axis than item 2.
- Arm C ≈ Arm B → retrieval works by lookup here (different from Gan); worth
  reporting as a cross-surface mechanism difference.

**Split discipline & cost.** dev140 only. Three arms × ~28 letters ≈ 84 calls.
Cheap. Own predeclaration doc.

**Relationship to item 2.** Items 2 and 3 are **independent architecture-family
tests of the same null hypothesis** ("the gap is fundamental"). Item 2 changes
the *generation contract* (closed-option vs free-write); item 3 changes the
*input* (primed vs unprimed). Running both gives two cross-family negatives (or
two refutations) from orthogonal directions — the strongest possible design for
the manuscript's "fundamental" claim. If only one is run, item 2 is higher
leverage (it is the direct dspy analogue); item 3 is the diversifying second
leg.

---

## Item 4 — Our own no-model medication oracle  ✅ DONE (2026-07-06)

Landed as a zero-LLM deterministic replay probe
(`experiments/exectv2_medication_no_model_oracle_2026-07-06.py`) + results doc
(`docs/experiments/exectv2/prescription/exectv2_medication_no_model_oracle_2026-07-06.md`).
**Outcome: dspy framing confirmed, and sharper than the plan anticipated.** Two
surfaces scored through the same scorers as the hybrid lane: `gold_as_prediction`
(gold copied through the pipeline) = **1.0000** on both splits (scorer-integrity
ceiling holds — the 206 dev140 / 293 full-200 gold counts are preserved
end-to-end); `deterministic_only` (`_extract_prescriptions` run as the final
system, no lens/bridge/LLM) = **0.9615 dev140 / 0.9278 full-200** — **identical
to the cited hybrid `clinical_headline` on both splits (gap +0.0000 / +0.0000).**
The LLM lane contributes **zero** to the Prescription `clinical_headline` on
either split; the cited headline is deterministic-owned to four decimals. dspy's
framing ("deterministic solves it; the LLM sits at-or-below the oracle")
transfers; the literal 47/47 / 100% does not, and the difference is traced:
dev140 residual is 6 FN + 10 FP across 13 letters, one of which (EA0146) is an
irrecoverable gold defect (DrugName says perampanel, every other field says
brivaracetam — see `gold_data_issues.jsonl`), the rest are deterministic
lexicon/context limits the LLM-tuned arm does *not* clear on dev140 either
(comparator: LLM 0.9526 < deterministic 0.9615). The LLM's genuine medication
value is a **full-200 precision** effect (FP 19→7), localized to non-AED
comorbidity over-capture — not a headline contribution. Manuscript reframing
required: Prescription is a deterministic-owned ceiling, not an LLM extraction
result.

**Motivating predecessor finding.** dspy reports that a **no-model annotation-
derived payload reproduces 47/47 medication gold labels (100% F1)** — an
isolated ceiling showing the medication task is essentially solved by
deterministic annotation lookup, with models sitting *below* the oracle (S1 GPT
92.8%, S5 GPT 88.7%). The implication is sharp: if our deterministic medication
extractor can already hit ~100% on the gold, then our medication story needs to
be framed as "deterministic solves it; the LLM underperforms the oracle" rather
than "the LLM extracts medications." We currently cite Prescription
`clinical_headline` 0.9615 (dev140) / 0.9278 (full-200) without an oracle
decomposition. dspy's framing is the challenge.

**What already exists.** Our deterministic medication extractor is
`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/all_entities/prescription.py`
(`_extract_prescriptions`, line 108), backed by `PRESCRIPTION_SURFACE_FORMS` +
`DRUG_SURFACE_ALIASES` lexicons and `_DOSE_PATTERN` / `_FREQUENCY_PATTERNS`. The
future/weight predicates (`_is_future_medication`, `_is_weight_based_dosing`)
live in the scorer (`.../scoring/prescription.py`). There is no current
"annotation-derived no-model oracle" run that scores the deterministic
extractor's output against gold *as though it were the final system*.

**What we build.** A zero-LLM ceiling probe, parallel to dspy's E6:
1. Run `_extract_prescriptions` over the dev140 (and optionally full-200) gold
   letters, producing a deterministic-only medication payload.
2. Score that payload through the *same* `score_prescription_components` /
   `score_prescription_benchmark_projection` scorer used for the hybrid lanes —
   no special-casing.
3. Report: deterministic-only F1, deterministic-only precision/recall, and the
   gap to the hybrid lane (0.9615 dev140). If deterministic-only ≈ 1.0, dspy's
   framing applies and our manuscript must say so; if deterministic-only ≪ 1.0,
   the LLM is genuinely contributing recall/specificity beyond the lexicon and
   we have a positive LLM-value story for medications.

**Why this matters beyond medications.** It establishes the methodology for
isolated-component ceilings — the dspy move of separating "stacked baseline"
from "isolated ceiling." Once we have the medication oracle, the same probe
shape applies to Investigations (where dspy found 90.4–96.7% near-ceiling) and
to the SF candidate substrate (where dspy's E1 broad payload covers 100% of gold
at 22.2% precision, localizing the problem to adjudication). The medication
probe is the template; the larger ceiling-registry is the payoff.

**Split discipline & cost.** Zero LLM calls. dev140 + full-200 both fine
(no live predictions — deterministic replay over gold text). No split risk.

**Output.** A new E-series result doc (e.g.
`docs/experiments/exectv2/prescription/exectv2_medication_no_model_oracle_2026-07.md`)
plus, if the oracle is ≥0.95, a manuscript framing note stating the medication
ceiling is deterministic-owned and the LLM lane's value is elsewhere.

---

## Item 5 — State the raw-extraction number alongside the headline  ⏳ PENDING (zero LLM)

**Motivating predecessor finding.** dspy's most uncomfortable finding for us:
**raw S1 extraction is 68.6% micro-F1; after benchmark bridges the same surface
reaches 92.3%** — a ~24-point bridge contribution "too large to call raw
extraction 'solved.'" They explicitly warn: "benchmark-aligned numbers are real
and useful, but the open work is raw ceilings, not stack polishing."
dissertation-recursive reinforces this with its "scorer was materially broken
for the first half of the project" story — projection-heavy numbers can mislead
for a long time. **Our `clinical_headline` 0.9189 (dev140) / 0.8680 (full-200)
is a de-duplicated, projection-bearing recovery surface. How much of it is raw
LLM extraction vs deterministic projection/bridge? If we can't decompose that,
dspy's critique applies directly to our headline.**

**What already exists (the decomposition entry points).**
- The assembly layer is `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/assembly/`
  — `pipeline.py`, `producers.py`, `views.py`, and `lenses/{diagnosis,prescription}.py`.
  This is where deterministic lenses reconcile producer findings into final
  clinical findings.
- `benchmark_projection.py` is the bridge layer that maps raw LLM surfaces onto
  the audited benchmark label set.
- The research-protocol skill's attribution rule is explicit: "An LLM-first
  claim requires showing what the model selected before deterministic semantic
  repair." We have the discipline stated; we need the number.
- The P7 propagation run (2026-07-02) already produced a same-day
  baseline+treatment pair isolating one producer's effect — the same pattern
  (swap one producer, hold the rest) extends to a full raw-vs-projected
  decomposition.

**What we build.** A one-number-per-family decomposition report:
1. For each family (Dx, SF, Prescription, Inv), score three surfaces through
   the *same* scorer:
   - **Raw LLM output** (pre-lens, pre-bridge, pre-projection) — the model's
     selected facts as emitted.
   - **Post-lens** (after deterministic reconciliation, pre-bridge).
   - **Headline** (current `clinical_headline`, post-bridge + de-dup) — the
     cited 0.9189.
2. Report the three numbers per family. The gap (raw → headline) is the
   deterministic-contribution magnitude. If raw ≈ headline, the LLM owns the
   result and dspy's critique does not apply. If raw ≪ headline, we state the
   raw number alongside the headline and frame the deterministic layer's
   contribution honestly (it is a *contribution*, not a fig leaf — but it must
   be visible).

**Why this is high priority and low cost.** It is the defensibility question
for the manuscript. It costs zero new LLM calls (it is a re-scoring of existing
saved artifacts through different projection surfaces). It directly answers the
strongest critique in the predecessor set. And it forces the attribution
discipline the research protocol already requires.

**Output.** A manuscript-ready table (raw / post-lens / headline × 4 families)
+ a paragraph for §4 stating the deterministic contribution explicitly. If the
raw number is uncomfortably low, that is *more* reason to state it — hiding it
inherits dspy's critique; surfacing it preempts the critique.

---

## Item 6 — Resolve the "multiple" sentinel contradiction (RUN EARLY)  ✅ DONE (2026-07-06)

> **Outcome (framing-changing).** The cross-project divergence is **not** the
> 2-vs-3 distinction this section originally emphasized — it is the
> **unknown-vs-counted** distinction. This repo resolves bare
> `multiple per <period>` to the **unknown** bin (monthly 1000.0,
> `FrequencyLabelKind.UNRESOLVED_MULTIPLE`); both predecessors assign a real
> count (dissertation-recursive 2.0, dissertation-experiments/dspy 3.0).
> Measured on Gan **validation750** (predictions held fixed; gold re-resolved
> three ways): the unknown-vs-counted axis moves Purist accuracy **~5pp** /
> Pragmatic **~4.8pp**; the 2-vs-3 axis moves **<0.3pp Purist / 0pp Pragmatic**.
> Of 46 fixed-2 bin-crossers, 41 are bare `multiple per <period>` rows (the
> unknown-vs-counted axis); only 3 are cluster-format rows (the period-dependent
> axis). Our cluster-format resolution is additionally period-dependent
> ({2,8,18,2} by week/month/year/day) — a third scheme neither predecessor uses
> — but it affects only 5 validation rows. **Conclusion:** our Gan numbers are
> not directly comparable to dspy's 90.3% without disclosing the resolution
> rule. Cite `../dissertation-recursive/src/gan_frequency.py:66` (2.0) and
> `../dissertation-experiments/src/clinical_extraction/normalizers/seizure_frequency.py:21,36`
> (3.0, Gan §2.6.1).
>
> **Note on the original plan text.** This section below describes the audit as
> it was scoped; the executed audit matched that scope (end-to-end trace,
> sensitivity re-scoring, disclosure note) but its headline finding re-prioritized
> which axis matters. The recommended disclosure language lives in the audit
> doc. **Correction to the plan's loose "Gan validation set" phrasing:** the
> audit used **validation750**, not test450 (test450 is frozen/blocked per split
> discipline).
>
> **Artifacts.** `docs/research/gan_multiple_sentinel_audit_2026-07.md`;
> driver: `scripts/run_gan_multiple_sentinel_audit.py`. Zero LLM calls.

**Motivating predecessor finding.** The four predecessors disagree on the
`multiple` count sentinel: dspy and dissertation-experiments use **3.0** ("Gan
§2.6.1: keyword 'multiple' = 3 seizures"); dissertation-recursive uses **2.0**
explicitly "for Gan comparability" while noting "the minimal-repo parser uses
3.0." A 2.0-vs-3.0 difference moves cluster-format rows across pragmatic bins
and silently changes scores. This is exactly the parser-contract drift that
makes cross-project comparison false — and the kind of bug
dissertation-recursive's "data-integrity finding" section shows can persist
undetected.

**What I found in this repo (run before predeclaring items 2/3).** This codebase
uses a **third scheme entirely**: *dynamic contextual resolution*. In
`src/clinical_extraction/tasks/shared/epilepsy/normalization.py:208-217`,
`_replace_multiple_cluster_count` maps `multiple cluster per {week,month,year,day}`
to **{2, 8, 18, 2}** respectively — i.e., the count of clusters is inferred from
the period (more clusters over a year than a week). And `_expand_cluster_label`
(line 180) maps `multiple per cluster → 2 per cluster`. There is no single
`MULTIPLE_VALUE` constant. This is more sophisticated than either predecessor's
fixed sentinel, but it means **our Gan scores are not directly comparable to
either predecessor's without disclosing the resolution rule.**

**What we do (audit, not experiment).**
1. Trace the `multiple` resolution end-to-end: gold-label loading →
   `label_to_monthly_frequency` → pragmatic/purist binning → final score.
   Confirm which resolution applies at each stage and that there is no second
   code path using a different value.
2. Compute the sensitivity: take the Gan validation set, score it once with our
   dynamic resolution and once with each predecessor's fixed value (2.0 and
   3.0). Report the pragmatic/purist accuracy delta. If the delta is nonzero,
   document it; if rows cross bin boundaries, list them.
3. Write a one-page note (`docs/research/gan_multiple_sentinel_audit_2026-07.md`)
   stating: our resolution rule, the cross-project divergence, the sensitivity,
   and the recommended disclosure language for any cross-paper comparison.

**Cost.** Zero LLM calls. This is a deterministic re-scoring + a documentation
pass. Should land before items 2/3 are predeclared because the framing of
"how our Gan numbers compare to dspy's 90.3%" depends on it.

**Why it can change framing.** If our dynamic resolution materially changes
which rows are correct vs dspy's fixed-3.0, then "we beat / match dspy's 90.3%"
is not a clean comparison without the disclosure. Better to know now.

---

## Item 7 — Did our evolved seed land on a policy-wall? (RUN EARLY)  ✅ DONE (2026-07-06)

> **Outcome (yes, but narrower than the plan implies).** **2 of 32** evolved
> GEPA seeds clear dspy's 14,639-char policy wall:
> `exectv2_gepa_multistage_verifystage_dedup_gpt41mini_20260701.instruction.txt`
> (18,638 chars / 125 policy-clauses) and
> `exectv2_gepa_multistage_dedup_gpt41mini_20260628.instruction.txt`
> (16,119 chars / 101 clauses) — both multistage combined 8-block artifacts.
> GEPA grew the verify-stage seed from ~0.7k chars / 3 clauses → 18.6k / 125
> (~25× length, ~40× clause density) — the policy-wall signature in pure form.
> Both over-threshold seeds embed dev-set-specific drug+dose worked examples
> ("Levetiracetam 750mg", "Carbamazepine 400mg", "Valproate 500mg"…) — the
> overfit shape dissertation-experiments warned about. Notably the largest
> (18,638) is the same seed the root-cause doc flagged as having "drifted into
> reformatting, not verifying" — a direct policy-wall signature.
>
> **Scope correction.** The evolved seeds are **research-workstream artifacts
> only** — the v08 production hybrid does not consume them (confirmed by
> exhaustive grep). So the policy-wall does **not** contaminate the 0.9189
> headline or any cited hybrid number; it reframes the GEPA close-out (the
> ~0.18 gap to hybrid is partly an overfitting artifact, not purely a capacity
> gap). **Cross-check nuance:** the root-cause doc's "producer evidence-recall"
> verdict is itself partially retracted for SF (representation, not recall) and
> Dx (gold multiplicity), so the cross-check's spine is weaker than the plan
> assumes — the GEPA plateau is *over-determined* by overfitting mechanisms,
> none a fundamental capacity limit.
>
> **Implication absorbed into item 2.** Item 2 runs on the *raw* SF-verify
> program (no evolved seed), so its four motivating negatives are not policy-
> wall artifacts and its refute is clean.
>
> **Artifacts.** `docs/research/exectv2_gepa_policy_wall_audit_2026-07.md`;
> driver: `scripts/run_gepa_policy_wall_audit.py`;
> `experiments/gepa_policy_wall_audit_2026-07-06.json`. Zero LLM calls.
> Tokenization via `tiktoken cl100k_base` (a transitive dep of `dspy>=2.5.0`,
> not pinned in `pyproject.toml`).

**Motivating predecessor finding.** dspy **rejected G30 GEPA** (scored 41/50 on
std50) specifically because "its accepted instruction ballooned to 14,639
characters (a 'policy wall')" and was gated behind compact-delta/latency/no-
overlap criteria. Our GEPA plateau is ~0.74 (mini) / ~0.65 (Qwen) on dev140,
root-caused (per `docs/research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md`)
to producer evidence-recall, not verify/arbitrate. **The two root-causes may be
two faces of the same phenomenon:** a GEPA-optimized instruction that
overfits to dev-set cues (policy-wall) tends to plateau because it cannot
generalize. dissertation-experiments independently found that *targeted mapping
examples beat generic example policies* — the lever is example-richness, not
policy-length.

**What we do (measurement + diagnosis, not a new GEPA run).**
1. Locate the current evolved seed instruction(s) — the GEPA-optimized
   producer prompts under the exectv2 assembly/producers path and the
   `prescription_repair_v03` producer. Measure: total character count, token
   count, and the count of distinct "rules"/"policy clauses" (heuristically:
   numbered/lettered list items or imperative sentences).
2. Compare against the dspy policy-wall threshold (14,639 chars) and against
   the *un-evolved* baseline seed. If our evolved seed is in the same order of
   magnitude as dspy's rejected wall, flag it.
3. Diagnostic: does the evolved seed contain dev-set-specific cues (specific
   drug names, specific letter constructions) that read as overfit? The
   dissertation-experiments finding suggests the productive direction is
   *targeted examples* (which generalize) over *policy clauses* (which
   overfit). If our seed is policy-clause-heavy and example-light, that is the
   policy-wall signature.
4. Cross-check against the existing root-cause doc: if the seed is policy-wall-
   shaped AND the plateau is producer-evidence-recall, the two diagnoses are
   consistent (the wall overfits to cues the producer can recall, plateauing on
   cues it can't). If the seed is compact and the plateau persists, the
   policy-wall hypothesis is refuted for us and the plateau is genuinely about
   evidence recall.

**Cost.** Zero LLM calls. Static analysis of existing prompt files + a
documentation pass.

**Why it can change framing.** If we are sitting on a policy-wall, the GEPA
plateau is not a fundamental capacity limit but an overfitting artifact — and
the fix (compact targeted examples, per dissertation-experiments) is different
from the fix the current root-cause doc implies (evidence-recall producer
redesign). This reframes a closed-negative workstream (GEPA) as a
diagnosed-negative with a known alternative. Items 2 and 3 should know this
before they predeclare, because if GEPA's plateau is policy-wall-shaped, the
"fundamental gap" framing inherits that doubt.

---

## Sequencing, dependencies, and cost summary

| Item | Type | LLM cost | Split risk | Depends on | Status | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| 6 — `multiple` sentinel audit | Audit | 0 | none | — | ✅ DONE 2026-07-06 | Dominant axis is unknown-vs-counted (~5pp), not 2-vs-3 (<0.3pp); disclosure needed for dspy comparison |
| 7 — policy-wall check | Audit | 0 | none | — | ✅ DONE 2026-07-06 | 2/32 evolved seeds clear the 14,639-char wall (18,638 / 16,119); research-only, not production path |
| 1 — gold-noise frontend tab | Infra | 0 | none | — | ✅ DONE 2026-07-06 | `/gold-noise` route landed (read-only, 3 levels) |
| 2 — closed-option SF-direction selector | Experiment | 28 calls (ran) | dev140 only | 6, 7 | ✅ DONE 2026-07-06 | **REFUTES "fundamental"** — +0.0552 dev140 directional, no regression |
| 5 — raw-extraction decomposition | Infra | 0 | none (re-score) | — | ⏳ PENDING | — |
| 4 — no-model medication oracle | Ceiling probe | 0 | none (replay) | — | ✅ DONE 2026-07-06 | **Confirms dspy framing** — deterministic-only == cited hybrid headline (0.9615 dev / 0.9278 full, gap +0.0000 both); LLM adds zero to Rx headline |
| 3 — retrieval-highlight priming | Experiment | 84 calls (ran) | dev140 only | 6, 7 | ✅ DONE 2026-07-06 | **HIGHLIGHT IS NOT THE LEVER** — Arm B − Arm A = −0.0068 dev140 directional (< +0.02 kill band); gap survives input change; LOOKUP not priming (Arm C ≈ Arm B) |

Only items 2 and 3 are costed fresh-protocol experiments; both are spent (item 2
28 calls, item 3 84 calls). Everything else is zero-LLM audit/infrastructure;
item 5 remains. The two audits (6, 7) ran first per design and their outcomes
were absorbed into item 2's frozen predeclaration: item 6's unknown-vs-counted
finding → item 2 states its claim in within-architecture-delta terms; item 7's
policy-wall finding (research-only) → item 2 ran on the un-walled raw program,
so its refute is clean.

## Cross-cutting research-protocol compliance

- **Split discipline.** Items 2 and 3 are dev140-only (the gap is two-split
  confirmed, so dev140 is the development surface; test59 frozen, no row-level
  inspection). Items 4 and 5 are deterministic re-scoring of existing saved
  artifacts — no live predictions, no split risk. Item 1 is read-only frontend.
- **Attribution discipline.** Item 5 *is* the attribution-discipline deliverable
  — its output is the raw-vs-projected decomposition the protocol requires.
  Items 2 and 3 must stamp provenance (selector-source / highlight-source) on
  every score line per the protocol's "keep the prediction-bearing source
  clear" rule.
- **Predeclaration.** Items 2 and 3 each get their own predeclaration doc
  (hypothesis id, kill criterion, frozen seeds, model, before/after ledger)
  before any LLM call. This plan is the umbrella, not the predeclarations.
- **Near-ceiling caution.** Per the protocol's "near-ceiling validation F1 is
  especially incomplete" rule, items 2 and 3 are designed as targeted
  disagreement-set studies (30 facts / 28 letters), not broad validation250
  reruns. The signal is in the hard-case recovery rate, not the aggregate.
- **Gold as controlled variable.** Items 2 and 3 use the *existing* frozen gold;
  item 1 surfaces gold quality but does not change it. No gold-loader edits in
  any item.

## Open questions for the user before predeclaring items 2/3

1. **Item 2 scope:** ~~build the closed-option direction selector as a standalone
   probe (cleanest attribution), or wire it into the existing gan2026
   `CandidateSet` substrate?~~ **RESOLVED 2026-07-06 — standalone probe chosen
   and run.** It worked (+0.0552, refutes "fundamental"), so per the original
   recommendation the substrate-integration follow-up is now candidate work:
   wire the closed-option selector into gan2026's `CandidateSet` as a candidate
   direction source feeding the hybrid arbitration, and re-score against the
   0.8897 hybrid reference. Not started.
2. **Item 3 ablation:** ~~include Arm C (highlight-only) to replicate
   dissertation-recursive's −32pp mechanism result, or run only A vs B to save
   calls?~~ **RESOLVED 2026-07-06 — Arm C included, per the original
   recommendation.** It was decisive for the *mechanism* reading: Arm C ≈ Arm B
   (−0.0245, within ~0.05) → LOOKUP, not priming — a cross-surface mechanism
   difference from dissertation-recursive (whose −32pp drop signaled priming).
   Without Arm C the run would only say "highlight doesn't help"; with it, the run
   also localizes *why* (the deterministic spans state the direction verbatim, so
   retrieval is lookup on this surface).
3. **Item 4 extent:** ~~medication oracle only (parallel to dspy E6), or extend
   the same probe to Investigations and the SF candidate substrate in one pass?~~
   **RESOLVED 2026-07-06 — medication only, per the original recommendation.**
   The probe validated the template (the dspy E6 isolated-ceiling shape works in
   this codebase) and produced a sharper-than-anticipated result
   (deterministic-only *equals* the cited hybrid headline on both splits, not
   just approaches it). The extension to Investigations (where dspy found
   90.4–96.7% near-ceiling) and the SF candidate substrate is now candidate work
   — the medication probe's two-surface design (`gold_as_prediction` scorer
   ceiling + `deterministic_only` extraction ceiling) is the reusable template.
   Not started.
