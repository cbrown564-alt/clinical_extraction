# ExECTv2 pipeline assumption audit — Phase 0 inventory

Date: 2026-07-02. Owner: ExECTv2 workstream.
Plan: `docs/plans/exectv2_pipeline_assumption_audit_plan_2026-07-02.md` (Phase 0).
Method: four parallel read-only audits (Prescription stack, SeizureFrequency
stack, Diagnosis+Investigations+concept path, shared matching machinery), each
confirming its findings with local dev140 probes. No files were edited and no
LLM runs were launched in this phase.

## Executive answer to the question that triggered this

The prescription dig raised the alarm: *is the measurement instrument itself
defective, and if so how much of the pipeline's reported evidence is corrupted?*
The audit answers both halves.

1. **The shared reduction is sound.** `core/scoring.py`
   (`multiset_prf1`/`sum_prf1`/`prf1_from_counts`) was verified correct across 8
   edge cases (both-empty, empty gold, empty pred, duplicate keys, partial
   overlap, 2-letter micro-sum). Micro-averaging sums tp/fp/fn then recomputes
   P/R/F1 (correct), not a mean-of-ratios; `safe_div` guards every degenerate
   denominator. **There is no cross-cutting bug silently corrupting all four
   families' headline F1.** This is the single most important reassurance: the
   reactive fear that "everything might be wrong" is not borne out at the level
   that would make everything wrong.

2. **But the defect class is systemic, not prescription-specific.** The seed
   bug's *class* — *a fact's scored `clinical_headline` membership depends on
   text or facts outside that fact's own scope* — recurs, in a different local
   form, in **every family**:

   | Family | Defect | ID | Risk | Direction of error |
   | --- | --- | --- | --- | --- |
   | Prescription | full-span future/weight regex drops correct current-dose facts | P1/P2/P3 | **H** | penalizes correct model + drops gold |
   | SeizureFrequency | zero-count precedence mislabels a variable rate `0–N` as seizure-free | SF-1 | M | penalizes correct model |
   | Diagnosis | independent per-side specificity-collapse zeroes a verbatim-correct match | D1 | M | **inflates** genuine-error residual (makes Dx look worse) |
   | Investigations | bare-word modality fallback emits FP-only keys | I1 | M | lowers precision on multi-modality spans |

   None of these is the *same code*, but they are the *same mistake*: a scored
   key is built with a wider scope than the fact it represents. That is exactly
   the pattern that one-family-at-a-time digging kept missing — and it is why the
   plan's holistic sweep was the right call.

3. **The favorable conclusions survive — two of them improve.** Fixing D1 can
   only *lower* Diagnosis's genuine-model-error share (it currently mis-charges a
   model for being more clinically specific than gold), so the "85.2% gold
   artifact" finding is reinforced, not threatened. The SF "gold-quality ceiling"
   survives: the SF *scorer* has no seed-class defect (all keys are own-scope);
   SF-1/SF-2 are a small measurement layer sitting on top of the IAA ceiling, not
   a hidden cap masquerading as one. Investigations' "genuine EEG-under-extraction"
   conclusion survives (the misses are real recall failures); I1/I3 only attach
   precision/convention caveats.

**Bottom line:** the instrument has several localized, same-class clause-scope
bugs worth fixing — but no systemic reduction-level corruption, and no fix
overturns a headline finding. The prescription bug was the loudest instance of a
real but bounded class.

## Consolidated findings, routed

Route legend: **BUG** = measurement bug, fix regardless of score impact;
**WEAK** = genuine model weakness (gated probe); **GOLD** = gold-quality/by-design,
document only; **CLEAR** = audited and confirmed correct.

### Route BUG — headline-affecting (Phase 1 targets)

| ID | Layer | Symbol | Mechanism | Risk |
| --- | --- | --- | --- | --- |
| **P1** | scoring/prescription.py | `_is_future_medication` (L308) gating `ordinary_complete`/`rescue_regimen` (L204/215) | future-plan cue matched anywhere in whole `annotation.text` nulls the entire fact from `clinical_headline`; contradicts the scorer's own `complete` diagnostic which keeps it | **H** |
| **P2** | scoring/prescription.py | `_is_weight_based_dosing` (L312) | `\d+mg/kg` anywhere in span nulls the whole fact | M |
| **P3** | scoring/prescription.py | `_prescription_component_key` (L198–227) | the cue that nulls a fact may belong to a *different downstream drug* in the same bundled span (`"lamotrigine 75mg bd, option of clobazam"` drops lamotrigine on clobazam's "option") | **H** |
| **SF-1** | scoring/seizure_frequency.py | `_frequency_state` (L230) | `any(count == "0")` has precedence over the nonzero test, so a variable rate `Lower=0/Upper=3` is labelled `seizure-free`; drops it from the active-rate slice and forgives a wrong magnitude in `active_rate_fidelity`. 1/187 in gold, unbounded on the pred side | M |
| **D1** | deterministic/normalization.py | `collapse_diagnoses_to_most_specific` (L288–302) via `_concept_keys` (match.py:442) | collapse runs independently on each side before intersecting, so gold `[epilepsy]` vs pred `[epilepsy, focal epilepsy]` scores F1=0 despite the model emitting `epilepsy` verbatim; 34/140 letters carry a parent+child gold pair | M |
| **I1** | scoring/investigations.py | `_investigation_modality_key` text fallback (L115–116) | `modality.lower() in span.split()` manufactures a `(MODALITY, None, None)` key that can never equal gold's attributed `(MODALITY, Yes, Result)` — structurally FP-only; fires on multi-modality prediction spans | M |

### Route BUG — diagnostic-scoped (do not affect headline F1, but affect cited diagnostics)

| ID | Layer | Symbol | Mechanism | Note |
| --- | --- | --- | --- | --- |
| P4 | scoring/prescription.py | `_has_source_stated_frequency` (L254) + note window (L285) | source-stated vs guideline-defaulted frequency decided from a ±48/+128-char note window; a neighbouring drug's cadence reclassifies this fact | feeds `source_stated_frequency`/`guideline_defaulted_frequency` diagnostics + benchmark projection, not `clinical_headline` |
| P6 | scoring/prescription.py | future/weight keys (L231–237) | keyed on whole-span phrase → gold full-regimen span vs pred trimmed span never match; systematic under-credit | `future_medication`/`weight_based_dosing` diagnostics only |
| SF-2 | scoring/seizure_frequency.py | `_frequency_state` vs `frequency_state_faithful` | direction present in gold (17.6% of facts) and producible by the model, scored by no metric; `state_profile` *forgives* wrong direction (inflation), `clinical_headline` conflates change with unknown (deflation) | reframes the SF direction slice as measurement, not gold ceiling |
| F2 | scoring/match.py | `_first_overlapping_prediction` (L543) greedy `used_pred` | a short generic gold phrase steals the prediction a longer specific gold would match exactly, inflating FN and mis-pairing the attribute-agreement comparison | distorts `source_near` overlap-recall + attribute-agreement rate **cited in the evidence-decomposition docs** — flag if those numbers are re-cited |

### Route BUG — producer-side (predict-time, ablatable; affect predictions not scoring)

| ID | Layer | Symbol | Mechanism | Note |
| --- | --- | --- | --- | --- |
| P7 | deterministic/all_entities/prescription.py | `_PRESCRIPTION_WEIGHT_BASED_CONTEXT.search(evidence)` (L162) | whole-evidence weight scope skips *every* dose in that evidence (over-broad vs the correct per-dose `/kg` check at L160) | can drop a real current dose before scoring ever sees it |
| P5 / SF-3 / SF-5 | producer↔scorer scope disagreements | see "scorer↔projection" below | the two layers encode the same concept at different scopes | reconcile in Phase 1c |

### Route WEAK — genuine model weakness (Phase 2 probes)

| ID | Family | Mechanism |
| --- | --- | --- |
| M1 | Prescription | asserts a proposed target dose as the current one (EA0021: emits 800mg-bd; true current 700mg-AM + 800mg-nocte) — `rx_current_vs_future_dose_conflation_2026-07-02` |
| M2 | Prescription | over-extracts non-AED comorbidity meds (clopidogrel/ramipril/metformin); the deterministic `_MEDICATION_PATTERN` only matches AEDs, so these originate from the LLM — `rx_non_aed_over_extraction_2026-07-02` |
| I4 | Investigations | genuine EEG-under-extraction when an MRI co-occurs (model emits no EEG token and no EEG attributes) — real recall miss, already known |

### Route GOLD / CLEAR — documented or confirmed correct

- **F1 (CLEAR):** core PRF1 math verified correct — the load-bearing reassurance.
- **C1 (CLEAR):** the in-sample gold-derived `InSampleConceptNormalizer` stub is
  **off every scored path** (referenced only in `agentic/tools.py` where it is
  explicitly rejected, one standalone ceiling probe, and one test) — verified by
  grep + `inspect.getsource`. No test-set contamination on scored numbers.
- **D4 (CLEAR):** `score_concept_identity` recall pooling is Counter-capped at the
  gold count; cannot double-count or leak across entities.
- **F6/F7/F8 (CLEAR):** benchmark/semantic ignore-attribute sets forgive only
  phrase-redundant fields (no load-bearing clinical attribute ignored); SF's
  extra `{Certainty, Negation}` ignore is the one judgment call and is
  guideline-documented (seizure-free still recovered from counts=0). The
  dedup-vs-per-occurrence convention split is applied consistently between
  `clinical_headline_unit_keys` and `headline_duplicate_tags`. The prescription
  `.replace("-", " ")` candidate builder is *required* (bypasses `normalize_phrase`
  which the regex's `\s+` needs), not a redundant inconsistency.
- **P8/P9 (GOLD):** unit-less / frequency-less current regimens are out-of-scope
  for the headline by design; Prescription gold-span altitude is inconsistent
  (~70% full-regimen, ~30% drug-name) — the enabling condition for P1/P2/P3, not
  fixable in gold but neutralized by the P1 fix.
- **I2/I3 (GOLD/convention):** dropping `EEG_Type` from the Investigations
  headline key is near-lossless (3 values in dev140); Investigations counts
  modality keys per-occurrence while Diagnosis dedups — a convention asymmetry
  worth verifying against the 7 dev letters with 2–3× identical gold modality
  keys, but not a correctness bug.
- **D2/D3 (low):** specificity collapse is not assertion-aware (negated parent +
  affirmed child); `headline_duplicate_tags` computes keys per-annotation and
  under-reports cross-annotation collapse (badge/tooling only, not on the Dx
  canonical adjudication path).
- **F3/F4/F5 (low/latent):** `normalize_phrase` false-splits surface variants
  (`nonepileptic` vs `non-epileptic`, `déjà vu` vs `deja vu`) — gold surface
  artifacts, not scorer defects; `CUI`/`Frequency` are case-sensitive in the
  generic `match_key` but no live loss found (CUI projected uppercase, Frequency
  lowercased in the prescription headline path).

## Scorer ↔ projection scope disagreements (Phase 1c reconciliation targets)

The clearest evidence the problem is architectural, not a typo: the same concept
is implemented at **different scopes in different layers**, and nobody reconciled
them.

1. **Future detection.** Scorer `_is_future_medication` matches the whole span
   and *nulls the fact*; the convention layer (`conventions/prescription.py:266–268`)
   *truncates* at the future cue and *keeps* the current-dose head; the
   `all_entities` producer trims only the planned tail. All three disagree — and
   the two producers are already correct. The scorer is the outlier.
2. **Weight-based detection.** Three different scopes for the identical regex:
   scorer whole-span (nulls fact), `all_entities` whole-evidence (skips all
   doses, P7), convention per-dose local window (correct).
3. **Drug-name canonicalization.** Scorer `canonicalize_medication_name`
   (flat `DRUG_SURFACE_ALIASES`) and producer `normalize_drug_name` (concept
   lexicon) diverge in both directions; the one that bites recall is bare
   `valproate` → not unified with `sodium valproate` (P5, also item #4a).
4. **SF state classification.** Scorer has two definitions (3-way count-only
   `_frequency_state` for five components, 4-way `frequency_state_faithful` for
   `state_profile`); both projection layers (`sf_state_projection`,
   `sf_unknown_suppression`) replicate the 3-way count-only definition, so they
   classify a `changed` fact as `unknown` and can suppress it — invisible to the
   metric that values it (SF-5).
5. **SF ownership CUI-strip vs scorer CUI-key** (SF-3): the projection strips a
   generic CUI expecting `assign_cui` to restore it; where the lexicon lacks the
   plural (`"convulsive seizures"`) the scorer's `_frequency_type_key` falls to a
   phrase key that cannot match all-CUI gold.

## Drug-lexicon gaps (Phase 3 targets)

- **Primary:** bare `valproate` does not unify with `sodium valproate` in the
  scorer (`canonicalize_medication_name("valproate") == "valproate"`), while the
  concept lexicon and producer *do* unify them — scorer/producer disagree
  whenever gold or pred carries "valproate". Also `valproic acid`,
  `valproate semisodium`.
- **Brand→generic omissions** (generics present in concept lexicon, aliases
  missing): `lyrica`→pregabalin, `topamax`→topiramate, `vimpat`→lacosamide,
  `briviact`→brivaracetam, `frisium`→clobazam, `trileptal`→oxcarbazepine,
  `neurontin`→gabapentin, `buccolam`→midazolam.
- **Spacing:** `"eslicarbazepine acetate"` (with space) → not aliased to
  eslicarbazepine.
- **Structural:** `DRUG_SURFACE_ALIASES` is a second, divergent authority from
  `PRESCRIPTION_CONCEPT_BY_PHRASE`. The durable fix is to route
  `canonicalize_medication_name` through the concept lexicon rather than maintain
  a parallel table.
- **Gold-data bug (separate ticket):** EA0146's gold `DrugName` says "Perampanel"
  while its own `CUIPhrase`/`CUI` resolve to brivaracetam.

## Prioritized Phase 1 queue (all free — replays, no LLM)

Ranked by risk × prevalence, each requiring predeclaration + dev140 replay +
citation update per the plan:

1. **P1/P2/P3 — prescription clause-scoping** (the seed; H; already predeclared
   as `rx_future_medication_regex_scope_bug_2026-07-02`). Reference
   implementation exists in the convention layer. Highest value.
2. **D1 — Diagnosis specificity-collapse hierarchy match** (M; touches the most
   populous family; the fix makes Dx *more* favorable so it is low-risk to the
   narrative but must still be replayed + citations updated).
3. **SF-1 — zero-count precedence** (M; small dev prevalence but a clean,
   unconditional correctness fix; unblocks the active-rate fidelity diagnostic).
4. **I1 — Investigations text-fallback gating** (M; precision-only, latent).
5. **P5 / lexicon reconciliation** (M; also closes item #4a) and **1c
   scorer↔projection reconciliation** (P7, SF-5) — group as a consistency pass.

Diagnostic-scoped bugs (P4, P6, SF-2, F2) are lower priority because they do not
move headline F1, but F2 must be flagged wherever the `source_near`
evidence-decomposition numbers are cited.

## New hypotheses registered from this audit

Added to `experiments/hypothesis_registry.jsonl` (OPEN):
`dx_specificity_collapse_cross_contamination_2026-07-02` (D1),
`sf_zero_count_precedence_2026-07-02` (SF-1),
`inv_text_fallback_fp_only_key_2026-07-02` (I1),
`rx_frequency_source_note_window_2026-07-02` (P4).
(P1/P2/P3 already tracked as `rx_future_medication_regex_scope_bug_2026-07-02`.)

## Probe scripts (read-only, scratchpad — not committed)

`probe_rx.py`, `probe_lex.py`, `probe_twin.py`, `sf_audit_probe.py`, and the
Diagnosis/Investigations/shared-machinery probes under the session scratchpad.
