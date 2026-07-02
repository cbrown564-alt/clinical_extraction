# Implementation plan — ExECTv2 pipeline assumption audit ("once and for all")

Status: **COMPLETE.** Date: 2026-07-02. Owner: ExECTv2 workstream. All phases
executed (Phase 2 costed probes run with user go-ahead; parallel sub-agents).
- Phase 0 DONE (`docs/research/exectv2_pipeline_assumption_audit_2026-07-02.md`):
  shared PRF1 reduction proved correct, seed defect *class* found in every family.
- Phase 1 DONE, all 4 measurement bugs
  (`..._phase1_2026-07-02.md` + `..._d1_diagnosis_2026-07-02.md`):
  Prescription P1/P2/P3 (0.8766→0.9073), SF-1 (0.5921→0.5982), I1 (latent),
  **D1 Diagnosis hierarchy-match now landed** (concept_only 0.6617→0.6779, +5
  ancestor/descendant recoveries, 0 spurious cross-credits, kill criterion met).
- Phase 2 DONE (costed, `docs/experiments/exectv2/prescription/exectv2_rx_extraction_probes_2026-07-02.md`):
  #2 current-vs-future CONFIRMED (+0.0322), #3 AED-only CONFIRMED (+0.0277,
  precision-driven, honest recall cost — needs a tighter gate in production).
- Phase 3 DONE (`..._phase3_2026-07-02.md`): drug-lexicon valproate/brand gaps
  (Rx 0.9073→0.9122), P4 note-window scope (headline-neutral), gold-data-issue
  log stood up (`experiments/gold_data_issues.jsonl`, EA0146).
- Phase 4 DONE (`..._phase4_guardrail_2026-07-02.md`): scorer scope-invariant +
  scorer↔projection consistency property tests, edit-triggers-predeclaration
  gate (`scripts/check_scorer_edit_predeclaration.py` + runbook), mechanism-
  taxonomy standing lens, and the "all cited runs" re-score sweep
  (`..._rescore_sweep_2026-07-02.md`, 13 dev140 + 1 full-200-aggregate re-scores).
Citation policy = overwrite-with-disclosure (registry `primary_metrics` +
disclosure, all four dossiers, frontend snapshot, manuscript §4.2 footnote + the
Diagnosis gold-quality passages all updated). Canonical run overall
`clinical_headline` 0.7313→0.7416→**0.7491**. Parked (diagnostic-scoped / needs
re-prediction or schema change, documented in the Phase 4 guardrail doc): P6,
SF-2, F2, P7, SF-5.

**Parked items closed out 2026-07-02** (all 5, none costed, none touch a
currently-cited headline number): **P6** (Rx `future_medication`/
`weight_based_dosing` diagnostic-key clause scope) fixed and unit-tested;
zero-impact on this run's diagnostic components (matches its own "no citation
at risk" framing). **F2** (`match.py` greedy `_first_overlapping_prediction` →
maximum-cardinality `_match_gold_to_predictions`) fixed after two design
iterations (an exact-phrase-priority tie-break was tried and rejected — it
degraded Prescription attribute-agreement by scrambling same-drug
repeated-mention pairing; switched to list-position proximity, which recovers
the old algorithm's Prescription pairing exactly while still fixing genuine
cardinality loss); SF `source_near` recall 0.6150→0.6203 (+1 case, `EA0143`),
zero change elsewhere. **SF-2** (direction-aware state schema + metric) added
`frequency_state_directional` + a new `state_profile_directional` companion
metric (additive-only, `clinical_headline`/`state_profile` untouched);
dev140 F1 0.6810 vs `state_profile`'s 0.7200, making the SF Phase-6
"model defaults every direction to Same" finding visible as a score delta.
**P7** (Rx multi-dose weight-context whole-evidence bug) — the guardrail
doc's own "needs re-prediction" classification was **wrong**: the producer
operates on static gold-letter text, not live LLM output, so this was a free
replay; fixed, isolated rules-only Prescription `clinical_headline`
0.9386→0.9615 (+9 tp/-9 fn, dev140), 11 dose-iterations recovered across 7
letters. **SF-5** (producer-side state-definition reconciliation) — same
wrong-classification pattern as P7, both modules are documented replay layers;
`sf_state_projection.py` reconciled to the canonical `frequency_state_faithful`
(also incidentally fixes a pre-SF-1-era zero-count precedence bug in its local
copy), zero regressions. `sf_unknown_suppression.py` deliberately **not**
reconciled — its suppression predicate is keyed on the *old* "unknown"
classification as a proxy for "this FrequencyChange is a false positive
(drug-response/historical-context evidence)"; widening its state definition
would silently disable suppression rather than improve it, a genuine
predicate-redesign need distinct from the guardrail doc's original framing.
Neither `sf_state_projection.py` nor `sf_unknown_suppression.py` feeds any
currently-cited number (only the retired v01–v05 finding-assembly manifests
reference them; v08/v09 use a different SF producer).
All five: dev140-replay-verified (zero new LLM calls throughout), unit-tested,
hypothesis-registry-recorded (all `CONFIRMED` except SF-5 `PARTIAL`), dossiers
regenerated.

**P7 v08 propagation — DONE 2026-07-02, same day, user go-ahead:** the
"deliberately not attempted" item above (re-running the full v08 hybrid
assembly to see whether P7's fix moves the manuscript's cited headline
numbers) was actioned as an explicit follow-up. Regenerated
`prescription_repair_v03` for dev140 and full-200 (zero new LLM calls, never
overwriting the archived artifact in place — that dev140 file is shared by
five other manifests), swapped only that producer into the existing v08
manifest, and built a same-day baseline+treatment pair on each split through
today's scorer to isolate P7's effect. dev140 `0.9130`→`0.9189` (+0.0059,
Prescription `0.9386`→`0.9615`); full-200 `0.8616`→`0.8680` (+0.0064,
Prescription `0.9033`→`0.9278`); Diagnosis/SF/Investigations byte-identical to
baseline on both splits. New hypothesis
`rx_p7_v08_hybrid_headline_propagation_2026-07-02` (CONFIRMED), two new
registry entries (dev140 is the first-ever registry-tracked v08 dev140
number — the historical "0.9155" was never itself registry-tracked), prior
full-200 currentcode entry marked superseded, `docs/canon/08_gepa.md` +
`10_paper_provenance.md` + `PROJECT_STATUS.md` citations corrected with
disclosure. Script: `scripts/run_exectv2_v08_p7_prescription_refresh_audit.py`.

Working tree not yet committed (this P7-propagation follow-up; the five
parked-item fixes above were committed separately at `c4a65e75`).

## Why this plan exists

The 2026-07-02 gold case ledger row-adjudicated Prescription and Investigations
at the actual scored `clinical_headline` layer for the first time and surfaced
four medication follow-ups (see `PROJECT_STATUS.md` → Next, and
`docs/canon/workstreams/PRESCRIPTION_CANONICAL_LEDGER_CANON.md`). One of them is
not a gold-quality artifact or a model weakness — it is a **genuine correctness
bug in the scorer** (`_is_future_medication`/`_is_weight_based_dosing` in
`scoring/prescription.py` match the *entire* gold annotation span, so a gold span
bundling a current dose with titration language is silently dropped from
`clinical_headline` scoring — 11/48 = 22.9% of Prescription's disagreements).

That is alarming for a reason bigger than Prescription F1: **the measurement
instrument itself has a latent correctness defect, and we found it only because
we happened to dig into one family after a run.** This is the fourth time this
project has discovered a load-bearing issue reactively — after a run completes,
by deep-diving a single area:

- SF "plateau" → gold-quality ceiling (found digging SF, Phases 4–7)
- Diagnosis gap → 85.2% gold multiplicity artifacts (found digging Dx, 06-30)
- Evidence-recall gaps → cardinality/typo artifacts (found digging Rx/Inv, 06-30)
- Prescription F1 → a real **scorer bug** (found digging Rx, 07-02)

Each dig used its own bespoke script until the gold case ledger consolidated the
mechanism taxonomy. But the *discovery* is still reactive and one-family-at-a-
time. **We have never proactively audited the pipeline's own assumptions across
all families and all layers at once.** The favorable families (Dx 85% artifacts,
SF gold-ceiling) have *not* been stress-tested for scorer bugs the way
Prescription just was — so we cannot currently rule out that some of those
favorable conclusions are themselves partly measurement artifacts.

This plan converts the reactive, ad-hoc pattern into (A) one deliberate holistic
audit, (B) the gated closure of the four known medication items inside that
frame, and (C) a standing guardrail so the *next* latent bug is caught at
commit time, not after a run. "Once and for all" means the guardrail (Phase 4),
not the four fixes.

## The concrete evidence that this is systemic, not a one-off

The same "future / titration / weight-based" concept is implemented **three
times, in three layers, with inconsistent scope**:

| Layer | Symbol | Scope of the text it matches |
| --- | --- | --- |
| Scorer | `scoring/prescription.py` `_is_future_medication` (L308) | **entire `annotation.text`** — the bug |
| Deterministic assembly | `deterministic/all_entities/prescription.py` (`_is_future_medication`/`_is_weight_based_dosing`) | (audit) — likely same span assumption |
| Deterministic convention | `deterministic/conventions/prescription.py` `_PRESCRIPTION_RESIDUAL_FUTURE_CUE_RE` (L62) | **clause-scoped** — `segment[: future.start()]` (L268) |

The convention layer already does the *right* thing (truncates at the future
cue, keeping only the current-dose clause). The scorer does the naive full-span
match. **Two layers of our own pipeline disagree on how to handle the exact same
phenomenon, and nobody reconciled them.** That is the signature of the whole
problem class: assumptions encoded implicitly, locally, and never cross-checked.
It also means the scorer fix has a ready-made reference implementation sitting in
the convention layer.

## Goal and non-goals

**Goal:** a single, deliberate pass that (1) inventories every implicit
assumption in the ExECTv2 scoring + projection + contract + extraction stack,
(2) sorts each into one of three routes — *measurement bug* (fix regardless),
*genuine model weakness* (gated improvement target), *gold-quality artifact*
(document, not fixable by us) — and (3) leaves a guardrail that keeps the
inventory true as code changes.

**Non-goals:**

- Not a rewrite. Most assumptions will turn out to be correct; the deliverable
  is the *catalogue and the routing*, plus fixes only where a defect is proven.
- Not a re-litigation of settled findings (SF gold-ceiling, Dx artifacts) —
  except to confirm those conclusions survive a scorer-correctness check they
  were never subjected to.
- Not holdout/full-200 row inspection. All row-level work stays on dev140, per
  the standing protocol (`PROJECT_STATUS.md` → Blocked/Guardrails).

## Three routes every finding must be sorted into

This is the spine of the audit. The Prescription dig already shows all three
coexist in one family, which is exactly why one-at-a-time digging keeps missing
things:

1. **Measurement bug** — the scorer / projection produces a wrong number
   independent of model or gold quality (e.g. the full-span regex). **Must be
   fixed regardless of score impact**, because it corrupts every historical
   citation. Gated as a scorer edit (predeclare + replay + citation update).
2. **Genuine model weakness** — the model really does extract wrong (Rx current-
   vs-future conflation, non-AED over-extraction, Inv MRI-crowds-EEG). A
   legitimate improvement target, pursued only through the gated probe
   discipline (predeclared hypothesis, kill-criterion, dev140 replay).
3. **Gold-quality / IAA artifact** — not fixable by us; document and discount.

The audit's job is to route *every* latent issue, in *every* family, into one of
these — not to keep finding them by accident.

---

## Phase 0 — Assumption inventory (free, no LLM runs, no code changes)

Deliberately enumerate, for each of the four families, every place an *implicit
assumption about gold / text / scope / cardinality* is encoded. This is the
holistic re-assessment the user asked for, done once on purpose instead of
incidentally over months.

**Scope of the sweep (all four families, equal rigor):**

- **Scorer layer** (`scoring/{prescription,seizure_frequency,investigations}.py`
  + `scoring/match.py`, `scoring/normalize.py`): every key-construction
  function. For each, record: what text scope does it read to build/gate a key?
  Does a fact's membership in `clinical_headline` depend on text *outside the
  fact's own clause*? (That is the seed defect — find every instance of it.)
  Does any multiset/dedup convention differ from the family's own gold
  convention? Diagnosis is scored via the shared `match.py` path — audit that
  path too; it has never had a prescription-style dig.
- **Deterministic projection layer** (`deterministic/conventions/*`,
  `deterministic/all_entities/*`, `deterministic/target_projection/*`,
  `deterministic/sf_state_projection.py`): every heuristic that decides whether a
  candidate is current/future/rescue/weight-based/active/changed. Cross-check
  each against its scorer twin (the table above is the first row of this cross-
  check). Flag every disagreement in scope or logic between projection and
  scorer.
- **Contract / lexicon layer** (`contract/drug_lexicon.py`,
  `contract/text.py`, `contract/validate.py`, `deterministic/concept_normalizer.py`,
  `deterministic/normalization.py`): canonicalization coverage and known gaps
  (bare "valproate" ≠ "sodium valproate"), the in-sample gold-derived
  normalizer stub, any place normalization silently changes a scored key.
- **Extraction / prompt layer** (v08 hybrid producer signatures + the GEPA-
  evolved instructions currently in use): the *behavioral* assumptions —
  "current medication" framing vs titration/target, AED-vs-comorbidity scope,
  investigation co-occurrence handling.

**Deliverable:** `docs/research/exectv2_pipeline_assumption_audit_2026-07-02.md`
— one row per assumption with columns: `layer | family | symbol:line | assumption
| route (bug/weakness/gold) | risk (H/M/L) | evidence | proposed action`. Plus a
short executive summary answering the user's actual question: *how many latent
measurement bugs exist beyond the one we already found, and do any of them touch
the favorable-family conclusions (Dx/SF) we currently treat as settled?*

**Kill/scope note:** Phase 0 is pure reading. It produces the catalogue and the
prioritized queue for Phases 1–3. If it finds *zero* additional measurement bugs
beyond the known prescription one, that is a real and reassuring result and
should be reported as such (not padded).

---

## Phase 1 — Scorer correctness sweep + item #1 (gated; highest priority)

The measurement instrument comes first because bugs here contaminate everything
downstream, including the favorable-family narratives.

**1a. Fix the known prescription regex-scope bug**
(`rx_future_medication_regex_scope_bug_2026-07-02`, OPEN in
`experiments/hypothesis_registry.jsonl`).

- Scope `_is_future_medication`/`_is_weight_based_dosing` to the **clause
  containing the scored dose**, not the full `annotation.text`. Reuse the
  convention layer's clause-truncation approach (`deterministic/conventions/
  prescription.py` L266–268) so scorer and projection finally agree.
- **Predeclare** the change and its expected direction before running.
- **dev140 replay** proving two things, not one: (i) it recovers the wrongly-
  excluded current-dose facts; (ii) it still excludes spans that are genuinely
  future/weight-based *for their whole clause* (no regression). Enumerate the
  letters in each set explicitly.
- **Citation impact:** this retroactively changes historical Prescription
  `clinical_headline` F1 (currently cited as 0.8766 for
  `exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628`, and elsewhere).
  Grep every doc that cites a Prescription F1, quantify the delta, and update or
  annotate each. Do **not** silently ship a scorer change that moves a number
  the manuscript depends on.
- Record verdict + downstream corrections back into the hypothesis registry and
  regenerate the Prescription dossier (`render_dossier.py`, never hand-edit).

**1b. Sweep every other scorer for the same class of defect** (from the Phase 0
catalogue). For each confirmed measurement bug found: same gated procedure
(predeclare → replay → citation update → registry). For each cleared assumption:
record it as *checked and correct* so it never has to be re-dug. **Explicitly
include Diagnosis and SF** — the point is to subject the favorable families to
the correctness check they have never had.

**1c. Reconcile scorer ↔ projection twins.** Where Phase 0 found the two layers
disagree (future/weight-based is the first known case), decide the single
correct scope and make both layers use it. A shared helper is preferable to two
copies of the regex.

---

## Phase 2 — Extraction-behavior probes (gated; costed — needs go-ahead)

Items #2 and #3 are the same *class* (genuine model weakness in extraction
behavior) and share a probe harness.

- **#2 current-vs-future dose conflation**
  (`rx_current_vs_future_dose_conflation_2026-07-02`, OPEN): a hand-tuned or
  GEPA instruction probe teaching the extractor to assert the *current*
  prescription, not the proposed target (EA0021: model emits 800mg-bd; true
  current is 700mg-AM + 800mg-nocte). Predeclared kill-criterion on dev140
  Prescription `clinical_headline`.
- **#3 non-AED over-extraction**
  (`rx_non_aed_over_extraction_2026-07-02`, OPEN): an explicit "AED-only"
  scoping instruction (model tags clopidogrel/ramipril/metformin; gold tags only
  AEDs). Low-risk; predeclared, dev140-measured.
- **Generalize the probe, don't silo it:** Phase 0's extraction-behavior rows
  will likely show analogs in other families (Investigations MRI-crowds-EEG is
  an *under*-extraction analog of #3's *over*-extraction; SF direction-blindness
  is a temporal-framing analog of #2). Design the probe harness once so these
  can be tested with the same instrument rather than re-built per family.

**Gating:** any live LLM run costs real money and touches GEPA/hand-tune infra.
**Do not launch Phase 2 runs without explicit go-ahead.** Sequence Phase 2 after
Phase 1b, because #2's measured effect is only trustworthy on a *corrected*
scorer — running a behavior probe against a buggy scorer would confound the
result.

---

## Phase 3 — Contract / lexicon + gold-data hygiene (mostly free)

- **#4a drug-lexicon gap:** add bare "valproate" → "sodium valproate"
  unification to `contract/drug_lexicon.py`; from the Phase 0 lexicon audit, add
  any other canonicalization gaps found in the same pass (don't fix only the one
  that happened to surface).
- **#4b gold-data correction ticket:** EA0146's gold `DrugName` says
  "Perampanel" while its own `CUIPhrase`/`CUI` resolve to brivaracetam. File
  this as a tracked gold-data issue (below), do **not** edit the frozen corpus
  silently.
- **Stand up a gold-data-issue log.** Gold errors keep being found ad-hoc
  (EA0146 here; the SF/Dx under-annotations earlier). Give them one home —
  either a `gold_data_issues.jsonl` alongside the hypothesis registry, or a
  dedicated section of the ledger — so the count is visible and citable rather
  than scattered across prose. This is itself an anti-recurrence measure.

---

## Phase 4 — Standing guardrail (the "once and for all")

Without this, we will re-run this discovery in three weeks against a different
family. Build the mechanisms that make latent assumptions surface at commit time.

- **Scorer-invariant property tests.** Encode the seed defect as a general
  invariant and test every family's scorer against it: *a fact's membership in
  `clinical_headline` must not change when text outside its own clause is
  altered.* Add round-trip / perturbation tests (append future-language to a
  clean current-dose span → membership must be unchanged). This catches the
  full-span class structurally for every scorer, present and future.
- **Scorer/projection consistency test.** A test that fails if a
  future/weight-based (or equivalent) decision is made at a different text scope
  in the scorer than in its projection twin — so the two layers can never
  silently drift apart again.
- **Edit-triggers-predeclaration gate.** A CI/pre-commit check (or a documented
  runbook step) that any diff touching `scoring/`, `deterministic/*projection*`,
  or `contract/drug_lexicon.py` must reference a predeclared hypothesis + a
  dev140 replay, matching the discipline this project already applies by
  convention but does not enforce.
- **Drive `unadjudicated → 0` across *cited* runs, not one run per family.** The
  ledger currently adjudicates one run per family. Extend coverage so every run
  whose F1 the manuscript cites has an adjudicated disagreement set — otherwise a
  scorer bug in an un-adjudicated cited run stays invisible exactly as this one
  did.
- **Make the mechanism taxonomy the standing lens.** Future digs extend
  `experiments/exectv2_ledger/mechanism.py` and feed the shared ledger rather
  than inventing a new local script — closing the loop that created the bespoke-
  script sprawl in the first place.

---

## Sequencing, cost, and gates

| Phase | Cost | Gate | Depends on |
| --- | --- | --- | --- |
| 0 — inventory | free (reading) | none | — |
| 1 — scorer sweep + #1 | free (replays, no new LLM) | predeclare + citation update per fix | 0 |
| 2 — behavior probes #2/#3 | **costed (live LLM)** | **explicit go-ahead**; run after 1b | 0, 1b |
| 3 — lexicon + gold hygiene | mostly free | gold corpus not edited silently | 0 |
| 4 — guardrail | free (tests/CI) | none | 1 (invariants derived from real fixes) |

**Recommended order:** 0 → 1 → 3 → 4, with 2 pulled in after 1b once a corrected
scorer exists and go-ahead is given. Phases 1, 3, 4 are all free and unblock on
Phase 0. Only Phase 2 spends money.

## Success criteria

1. Every latent assumption in the four-family scoring/projection/contract/
   extraction stack is catalogued and routed (bug / weakness / gold), with the
   favorable families (Dx, SF) subjected to the same scorer-correctness check
   Prescription just received.
2. The known prescription scorer bug and any others Phase 1 finds are fixed
   under full gating, with every affected historical citation updated — no
   silently-moved numbers.
3. Items #2/#3/#4 are either closed (verdict recorded in the registry) or
   explicitly parked with a reason.
4. A guardrail exists that would have caught the full-span defect at commit time,
   so the reactive-discovery pattern is structurally, not just intentionally,
   ended.

## Registry / provenance touchpoints

- OPEN hypotheses to resolve: `rx_future_medication_regex_scope_bug_2026-07-02`,
  `rx_current_vs_future_dose_conflation_2026-07-02`,
  `rx_non_aed_over_extraction_2026-07-02`
  (`experiments/hypothesis_registry.jsonl`).
- New hypotheses Phase 0/1b will likely add (one per additional scorer defect or
  cleared-assumption cluster).
- Dossiers regenerated via `experiments/exectv2_ledger/render_dossier.py` — never
  hand-edited.
- `PROJECT_STATUS.md` → Next updated to point at this plan as the owning frame
  for the four follow-ups (replacing the current loose "open queue" bullet).

## Companions

- `PROJECT_STATUS.md` (Next / Done Recently — 2026-07-02 ledger entry)
- `docs/canon/workstreams/PRESCRIPTION_CANONICAL_LEDGER_CANON.md`
- `docs/canon/workstreams/INVESTIGATIONS_CANONICAL_LEDGER_CANON.md`
- `experiments/exectv2_ledger/` (schema, mechanism taxonomy, dossier renderer)
- `docs/canon/04_scoring.md`, `docs/canon/05_ceilings_wall.md`
