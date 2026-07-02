# Pipeline assumption audit — Phase 3 contract/lexicon + gold hygiene + P4 (result)

Date: 2026-07-02. Owner: ExECTv2 workstream.
Plan: `docs/plans/exectv2_pipeline_assumption_audit_plan_2026-07-02.md` (Phase 3, and the P4 row of Phase 0/1c).
Phase 0 inventory: `docs/research/exectv2_pipeline_assumption_audit_2026-07-02.md`.
Phase 1 result: `docs/research/exectv2_pipeline_assumption_audit_phase1_2026-07-02.md`.

All measurements are dev140 re-scores of the cached predictions for
`exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628` (zero new LLM calls),
replaying via `experiments/exectv2_ledger/match_replay.py` and self-validating the
aggregate against `score_prescription_components(...).clinical_headline`. The
post-Phase-1 baseline for Prescription `clinical_headline` is **0.9073**
(tp=186 fp=18 fn=20), reproduced exactly before any Phase 3 change.

## Summary of what landed

| Item | Change | Before → After | Kill criterion |
| --- | --- | --- | --- |
| **#4a lexicon** (`rx_drug_lexicon_valproate_brand_gaps_2026-07-02`) | 12 aliases added to `DRUG_SURFACE_ALIASES` (bare valproate + chemical variants → sodium valproate; 8 brand→generic; spaced eslicarbazepine acetate) | Rx `clinical_headline` **0.9073 → 0.9122** (tp 186→187, fp 18→17, fn 20→19) | **MET** — recall-positive; +1 TP, no TP lost |
| **P4** (`rx_frequency_source_note_window_2026-07-02`) | `_has_source_stated_frequency` scoped to the annotation's own span; ±48/+128-char note window removed | Rx `clinical_headline` **0.9122 → 0.9122** (byte-identical) | **MET** — no `clinical_headline` key changed |
| **#4b gold ticket** (EA0146) | logged, corpus NOT edited | — | frozen corpus untouched |

Net Prescription `clinical_headline` after both Phase 3 changes: **0.9073 → 0.9122**
(the lexicon carries the whole move; P4 is diagnostic-scoped and moves no headline key).

---

## Gold-data-issue log schema (`experiments/gold_data_issues.jsonl`)

One JSON object per line. Standing home for concretely-identified gold-corpus
defects (a specific letter + field whose value conflicts with its own
co-annotated evidence), so the count is visible and citable rather than scattered
across prose. The frozen corpus is **never** edited in place; entries record the
conflict and its scoring effect, and are resolved by convention/annotation, not by
mutating the letters.

| Field | Meaning |
| --- | --- |
| `letter_id` | dev/holdout letter id (e.g. `EA0146`) |
| `entity` | ExECTv2 entity family (`Prescription`, `Diagnosis`, …) |
| `field` | the gold attribute/field in conflict (e.g. `DrugName`) |
| `gold_value` | the value currently recorded in the frozen corpus |
| `conflicting_evidence` | the co-annotated fields (and/or span text) that contradict `gold_value` |
| `resolution_status` | `open` \| `resolved` \| `wontfix` |
| `date` | date the issue was logged (ISO) |
| `notes` | how/where it was found + its scoring effect + any resolution reasoning |

Seeded with one entry (EA0146). No other letter+field gold conflict is
concretely named in the Phase 0/1 docs, so nothing else was invented.

---

## Subtask 1 — #4a drug-lexicon gaps

### Predeclaration — `rx_drug_lexicon_valproate_brand_gaps_2026-07-02`

- **Family:** Prescription.
- **Statement:** `DRUG_SURFACE_ALIASES` does not unify bare `valproate` /
  `valproic acid` / `valproate semisodium` with `sodium valproate`, and omits
  eight brand→generic aliases (`lyrica`→pregabalin, `topamax`→topiramate,
  `vimpat`→lacosamide, `briviact`→brivaracetam, `frisium`→clobazam,
  `trileptal`→oxcarbazepine, `neurontin`→gabapentin, `buccolam`→midazolam) and
  the spaced form `eslicarbazepine acetate`→eslicarbazepine, even though those
  generics are already present in the concept lexicon. Adding these aliases
  unifies the affected `DrugName` keys and can only convert a name-mismatch
  false-positive/false-negative pair into a true positive; it cannot break an
  existing match because none of the alias *targets* is itself a gold `DrugName`
  surface that another fact relies on.
- **Kill criterion:** dev140 Prescription `clinical_headline` replay on
  `exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628` must **not LOSE any
  true positive**; net effect recall-neutral-or-positive.
- **Predeclaration doc:** this file.

### Result — NOT latent; +1 TP, kill criterion met

The change is **not** latent on this run. The predictions contain exactly one
bare-`valproate` `DrugName`; all other valproate surfaces (`epilim`, `eplim`,
`sodium valproate`, `sodiumvalproate`) already canonicalize to `sodium-valproate`.

- **EA0093** — pred `DrugName='valproate'`, DrugDose=500, DoseUnit=mg,
  Frequency=1, CUI=C0037567 (its own `CUIPhrase` is already `sodium-valproate`).
  Gold `DrugName='SodiumValproate'` (`CUIPhrase='episenta'`), same dose/frequency/CUI.
  Before: pred keyed to `valproate`, gold to `sodium-valproate` → 1 FP + 1 FN.
  After the `valproate → sodium valproate` alias: both key to `sodium-valproate`
  → 1 TP.

**Rx `clinical_headline`: 0.9073 → 0.9122** (P=0.9118→0.9167, R=0.9029→0.9078;
tp 186→187, fp 18→17, fn 20→19). Exactly one FP+FN pair collapsed to a TP; TP
count strictly increased, so no true positive was lost — kill criterion met. The
other eleven aliases are **latent on dev140** (their surfaces do not appear in
this run's gold or predictions); they are defensive corrections that unify future
brand/variant spellings and reconcile the scorer's `canonicalize_medication_name`
with the concept lexicon (Phase 0 P5 / scorer↔projection reconciliation).

Replay self-validated: decomposition tp/fp/fn matched
`score_prescription_components(...).clinical_headline` exactly (0.9122).

---

## Subtask 2 — P4 (`rx_frequency_source_note_window_2026-07-02`)

`_has_source_stated_frequency` previously searched, in addition to the
annotation's own text, a ±48/+128-char window of the full note around the drug
phrase (`_note_windows_for_annotation_phrase` / `_annotation_frequency_search_phrases`).
That let a **neighbouring** prescription's cadence word reclassify this fact as
source-stated. The fix scopes the search to the annotation's own span only
(`annotation.text`/`raw_text` and their de-hyphenated variants); the two
note-window helpers are removed. `note_text` is retained on the signature for
call-site symmetry but is no longer consulted.

### `clinical_headline` unchanged (kill criterion met)

`clinical_headline` is built from `rescue_regimen`/`ordinary_complete` →
`complete` → `name`/`dose`/`frequency`; **none** of these call
`_has_source_stated_frequency`, so the headline key set is *structurally*
independent of P4. Empirically confirmed: `clinical_headline` is byte-identical
across the change — tp=187 fp=17 fn=19, F1=**0.9122** both before and after P4
(measured on top of the #4a lexicon change). `frequency` is likewise unchanged
(0.9220, tp=189 fp=15 fn=17).

### Diagnostic-metric change (the intended effect)

Only the two diagnostic components move (they are diagnostic-scoped by design —
they feed `source_stated_frequency` / `guideline_defaulted_frequency` and the
benchmark projection, not the headline):

| Diagnostic | Before P4 | After P4 |
| --- | --- | --- |
| `source_stated_frequency` | tp=0 fp=0 fn=206 (F1 0) | tp=0 fp=0 **fn=120** (F1 0) |
| `guideline_defaulted_frequency` | tp=0 **fp=204** fn=0 (F1 0) | **tp=74** fp=130 fn=12 (F1 **0.5103**) |

Reading: 86 gold facts (206→120) that were being credited as *source-stated* only
because a cadence appeared elsewhere in the note now fall to *guideline-defaulted*
where their own span states no cadence — which is the correct own-span
classification. `guideline_defaulted_frequency` goes from structurally-degenerate
(zero gold keys, so tp=0 by construction) to functional (tp=74).

**Replay-harness caveat (not caused by P4):** in this cached replay the predicted
letters carry `note_text=""` (predictions are stored as mentions only), so the
note window never fired on the *pred* side even before P4 — every pred frequency
fact was already `guideline_defaulted`. P4's measurable movement is therefore
entirely on the gold side. The pred-side asymmetry is a property of the
mention-only prediction cache used by `match_replay.py` /
`exectv2_rx_inv_canonical_row_analysis.py`, not of the fix; end-to-end scoring
where preds carry `note_text` would see the symmetric effect. Either way,
`clinical_headline` — the only headline-affecting surface — is untouched.

---

## Subtask 3 — #4b gold-data issue (EA0146)

Confirmed on the frozen dev140 corpus. EA0146's second Prescription annotation:

```
DrugName='Perampanel'   CUIPhrase='brivaracetam'   CUI='C1699861'   span text='Brivetiracetam-'
```

Every field except `DrugName` resolves to brivaracetam (the span text is a typo
of brivaracetam; `CUIPhrase` names it outright; the CUI is the brivaracetam
concept). `DrugName='Perampanel'` is the lone outlier and is almost certainly a
gold transcription error. Effect on scoring: the gold `clinical_headline` name
key is `perampanel`, so a model prediction that correctly reads the span
(`Brivetiracetam`→`brivaracetam`) can never be a true positive — the gold defect
mislabels a defensible prediction as FP+FN. **The frozen corpus was NOT edited.**
Logged in `experiments/gold_data_issues.jsonl` with `resolution_status="open"`.

---

## Subtask 4 — gold-data-issue log stood up

`experiments/gold_data_issues.jsonl` created (schema above), seeded with the
EA0146 entry. This is the anti-recurrence home the plan's Phase 3 asked for:
future gold defects append a line here rather than being buried in prose.

---

## Files changed

- `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/contract/drug_lexicon.py`
  — 12 aliases added to `DRUG_SURFACE_ALIASES` (+ key/value convention comment).
- `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/prescription.py`
  — `_has_source_stated_frequency` scoped to own span; `_prescription_frequency_source_candidates`
  no longer takes/uses `note_text`; `_note_windows_for_annotation_phrase` and
  `_annotation_frequency_search_phrases` removed (dead after P4).
- `experiments/gold_data_issues.jsonl` — new; EA0146 entry.
- `tests/test_exectv2_scoring.py` — added `test_canonicalize_medication_name_unifies_valproate_and_brand_gaps`;
  updated the three source-frequency tests that encoded the removed note-window
  contract to assert the new own-span behaviour
  (`..._ignores_note_only_cadence`, `..._neighbour_cadence_does_not_leak`,
  `..._reads_cadence_from_own_span`).

## Test status

- Prescription/lexicon/scoring selection green:
  `tests/test_exectv2_scoring.py`, `tests/test_exectv2_prescription_projection_pilot.py`,
  `tests/test_core_scoring.py`, `tests/test_exectv2_deterministic_all9.py`,
  `tests/test_exectv2_projection_gap_ledger.py`, and the three Investigations
  suites — **all pass** (100 in the broad selection; 12 prescription/lexicon-specific).
- Two pre-existing, unrelated collection errors remain (`tests/test_doc_hygiene.py`
  missing `scripts.check_doc_hygiene`; a gan2026 registry import) — untouched.

## Out of scope / not done here

- Registry writes: this doc supplies the REGISTRY PATCH SPEC (new hypothesis
  `rx_drug_lexicon_valproate_brand_gaps_2026-07-02` verdict + P4 verdict); the
  registry files themselves are updated by the owning caller.
- Dossier/frontend/manuscript re-scoring for the +0.0049 Rx `clinical_headline`
  move belongs to the Phase 4 "all cited runs" citation sweep, not Phase 3.
- The durable structural fix (route `canonicalize_medication_name` through the
  concept lexicon instead of a parallel `DRUG_SURFACE_ALIASES` table) is left as a
  Phase 4 reconciliation item; Phase 3 only closes the enumerated gaps.
