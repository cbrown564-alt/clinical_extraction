# A mechanical (zero-LLM) heuristic for orthographic gold-inflation — does edit distance find Prescription's typo cases without false-alarming on Investigations?

Status: **CLOSED. PRIMARY KILL-CRITERION PASSES CLEANLY** (Prescription 7/7 genuine typo
cases recovered, 0/19 Investigations false positives) **but the heuristic does NOT generalize
as an all-purpose "H-inflation detector"** — extending it past its intended scope surfaces a
real, honest failure mode: on the two `clinical_headline`-deduping families (Diagnosis,
SeizureFrequency), whose vocabulary is dominated by inflections of a handful of clinical stems
("seizure"/"seizures"/"seizure-free"/"seizure-cluster"), the same threshold fires 13 times and
**zero of those 13 are genuine spelling/transcription typos** on manual reading of the existing
adjudicator reasoning — they are stem collisions that coincide with (but do not explain) an
already-known, different mechanism (phrase-normalization / concept consolidation). Date:
2026-07-01. Owner: ExECTv2 workstream.

Executes: Item 4,
`docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md`.

Companions:
- `docs/experiments/exectv2/exectv2_rx_inv_ev_recall_consolidation_check_2026-06-30.md` — source
  of the 8 (7 genuine + 1 brand/generic) Prescription cases this heuristic targets, lines 81-93.
- `docs/experiments/exectv2/seizure_frequency/exectv2_sf_ev_recall_consolidation_check_2026-06-30.md`
- `docs/experiments/exectv2/diagnosis/exectv2_dx_ev_recall_consolidation_check_2026-06-30.md`
- Script: `experiments/exectv2_gold_inflation_mechanical_heuristic.py`
- Output: `experiments/exectv2_gold_inflation_mechanical_heuristic_output.csv` (112 rows, one per
  `H2_GENUINE_DIVERGENCE` case across all four families)

## 1. Question

The four family `source_near` evidence-recall adjudications (Diagnosis, SeizureFrequency,
Prescription, Investigations) each split misses into `H1_CARDINALITY` (gold multiplicity) and
`H2_GENUINE_DIVERGENCE` (no mechanical explanation found, adjudicated case by case). Prescription's
adjudication found an *unanticipated third mechanism* buried inside its `H2_GENUINE_DIVERGENCE`
bucket: 7 of its 8 `MODEL_DEFENSIBLE` H2 cases are not genuine misses at all — they are
spelling/transcription typos (in the gold span or in the source letter) that break
`source_near`'s literal substring match even though the model's prediction carries an identical
CUI/dose/frequency. No `mechanism` value or field anywhere in the codebase captures this; it exists
only as free-text prose in the adjudicators' `reason` column.

Can a **mechanical, pre-adjudication-usable** heuristic (edit distance between the missed gold span
and the model's own same-letter, same-family predictions) recover this bucket automatically, well
enough to be trusted as a pre-flight signal before spending adjudication budget on a new entity
family?

## 2. Method

`experiments/exectv2_gold_inflation_mechanical_heuristic.py`, zero LLM calls, pure re-analysis of
artifacts already on disk. No existing adjudication file is modified; output goes to a new file.

**Diagnosis path resolution (task step 1):** Diagnosis has no standalone
`_dx_ev_recall/_adjudication.csv`. Reading `experiments/exectv2_dx_evidence_recall_consolidation_check.py`
confirms it writes only `experiments/exectv2_dx_evidence_recall_consolidation_check.json` (a
`rows` list of `{letter_id, concept, mechanism, adjudication_verdict}`), reusing
`_dx_canonical/_adjudication.csv` for verdicts and `_dx_canonical/_index.json` for the
canonicalized concept labels it works over. That JSON's `rows` list is the Diagnosis equivalent of
the other three families' adjudication CSV and is what this script reads.

**Per-family inputs joined** (all pre-existing, zero new computation of predictions/adjudications):

| family | adjudication source | missed-span source | same-letter candidate spans |
| --- | --- | --- | --- |
| SeizureFrequency | `_sf_ev_recall/_adjudication.csv` | `_sf_ev_recall/_cases.json` `gold_missed.text` | `_cases.json` `pred_sf_all[].text` |
| Prescription | `_rx_inv_ev_recall/_adjudication.csv` (entity=Prescription) | `_cases.json` `gold_missed.text` | `_cases.json` `pred_family_all[].text` |
| Investigations | `_rx_inv_ev_recall/_adjudication.csv` (entity=Investigations) | `_cases.json` `gold_missed.text` | `_cases.json` `pred_family_all[].text` |
| Diagnosis | `experiments/exectv2_dx_evidence_recall_consolidation_check.json` `rows` | raw gold `ExectAnnotation.text` for that letter+concept, via `gepa_data.load_dev_letters()` + `canonicalize_diagnosis_concept()` (concept itself is already canonicalized, not a raw span) | cached GEPA prediction jsonl (`exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628.jsonl`), Diagnosis `predicted_mentions[].text` for that letter |

Diagnosis needed one extra hop (back to the raw gold annotations and the cached prediction jsonl,
both already-on-disk deterministic artifacts read the same way the Dx ev-recall script itself reads
them) because its stored adjudication rows only carry the canonicalized concept string, not the raw
span text the `source_near` substring check actually operates over.

**The heuristic itself.** For each `H2_GENUINE_DIVERGENCE` row (H1 rows untouched, per the task):

1. Normalize both the missed span and every candidate span with the repo's own
   `normalize_phrase` (lowercase, hyphens→spaces, whitespace-collapse — the exact normalization
   `source_near` itself uses).
2. Extract "content tokens": whitespace tokens with ≥4 alphabetic characters, so dose/unit/frequency
   noise ("250mg", "bd", "twice") doesn't dominate the comparison; falls back to the unfiltered
   token list when nothing survives (needed for short entity names like "MRI"/"EEG"/"CT" in
   Investigations).
3. Compute edit distance (optimal string alignment — Levenshtein plus adjacent-transposition,
   implemented directly; no fuzzy-matching package is installed in this environment) across every
   `(missed token, candidate token)` pair, take the global minimum.
4. Flag `H3_ORTHOGRAPHIC` if the minimum distance is **> 0** and (**≤ 2** absolute, OR **≤ 15%** of
   the longer token's length). The absolute floor catches single-edit typos on short words where
   15% would be too strict (e.g., a 5-letter word); the relative ceiling catches proportionally
   small edits on longer names.
5. Secondary, retrospective-only signal: does the adjudicator's `reason` text contain
   `spell|typo|misspel|transcri|orthograph`? This is **not** part of the pre-flight-usable verdict
   (reason text doesn't exist until adjudication has already been paid for) — it is reported only
   as a corroboration/recall check on the mechanical signal.

Thresholds were fixed before looking at family-level results beyond Prescription (the family the
plan already named as the target); they were not retuned afterward to improve the picture — see
§3.3 for what that produced.

## 3. Result

### 3.1 Per-family H2 → H3 reclassification

| family | n_H2 (before) | n_H3 flagged | n_H2 residual | flagged-and-genuinely-typo (manual read of `reason`) |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 51 | 3 | 48 | **0 / 3** |
| SeizureFrequency | 23 | 10 | 13 | **0 / 10** |
| Prescription | 19 | 7 | 12 | **7 / 7** |
| Investigations | 19 | 0 | 19 | n/a |
| **Total** | **112** | **20** | **92** | **7 / 20 (35%)** |

Full before/after context including the untouched `H1_CARDINALITY` bucket (and Diagnosis's third
`NOT_SOURCE_NEAR_FN` bucket, informational, not part of H1/H2):

| family | H1 (unchanged) | H2 before | H3 (new) | H2 after | other |
| --- | ---: | ---: | ---: | ---: | --- |
| Diagnosis | 13 | 51 | 3 | 48 | NOT_SOURCE_NEAR_FN=28 |
| SeizureFrequency | 49 | 23 | 10 | 13 | — |
| Prescription | 4 | 19 | 7 | 12 | — |
| Investigations | 8 | 19 | 0 | 19 | — |

### 3.2 The kill-criterion, exactly as specified

Target set: Prescription's 8 `H2_GENUINE_DIVERGENCE` + `MODEL_DEFENSIBLE` cases (case_ids 1, 8,
9, 10, 11, 13, 17, 23 / letters EA0014, EA0056, EA0061, EA0072, EA0093, EA0117, EA0152, EA0199 —
confirmed against the source doc, lines 81-93). Of these 8, only **7 are genuine
spelling/transcription typos**; the 8th (`EA0093`, case_id 11) is a **brand/generic name split**
(gold tagged "Episenta", the model predicted the generic "Valproate" named in the same sentence) —
not an orthographic variant of the same string at all (`Episenta` vs `Valproate`: edit distance 8,
89% of the longer token — nowhere near either threshold). A correct edit-distance heuristic should
recover the 7 and leave the 8th alone.

| case_id | letter | missed span | best same-letter candidate | distance | ratio | result |
| --- | --- | --- | --- | ---: | ---: | --- |
| 1 | EA0014 | `zobisamide` | `Zonisamide` | 1 | 0.100 | RECOVERED |
| 8 | EA0056 | `Oxcarbazine-` | `Oxcarbazepine` | 2 | 0.154 | RECOVERED |
| 9 | EA0061 | `lamtorigine-250mg-bd` | `lamotrigine` | 1 | 0.091 | RECOVERED |
| 10 | EA0072 | `Lamotrigne` | `Lamotrigine` | 1 | 0.091 | RECOVERED |
| 13 | EA0117 | `Lacosmaide` | `Lacosamide` | 1 | 0.100 | RECOVERED |
| 17 | EA0152 | `Carbmazapine-` | `Carbamazapine` | 1 | 0.077 | RECOVERED |
| 23 | EA0199 | `EPlim` | `Epilim` | 1 | 0.167† | RECOVERED |
| 11 | EA0093 | `-Episenta-500mg` | `Valproate` | 8 | 0.889 | **not flagged (correct)** |

†0.167 is above the 0.15 relative threshold but the case is still flagged because it clears the
absolute floor (distance = 1 ≤ 2).

**Recovered 7/7 (100%) of the genuine typo cases. The brand/generic outlier is correctly left
unflagged.** Within Prescription's other 11 `GOLD_RIGHT` H2 cases (real, unambiguous misses — an
entire second/third drug absent from the prediction list) **0/11 were falsely flagged**.

**Investigations (the required clean-negative check): 0/19 `H2_GENUINE_DIVERGENCE` cases flagged.**
Investigations' H2 bucket is 100% `GOLD_RIGHT` per the source adjudication (every case an absent
EEG mention in an MRI+EEG letter), so any flag there would have been an unambiguous false positive.
There were none.

**Verdict: the kill-criterion as literally specified in the plan PASSES, cleanly, with no
threshold-tuning required to get there.**

### 3.3 What happens when you don't stop at the kill-criterion (the honest part)

The task asked this heuristic to double as a general "does this family's inflation run through the
typo mechanism" pre-flight tool. Applying it to Diagnosis and SeizureFrequency (the two families it
was *not* predeclared against) shows it does **not** generalize as such:

- **SeizureFrequency: 10/23 H2 rows flagged, 0 are genuine typos.** All 10 hits are single-edit
  collisions on the shared stem "seizure" — `seizure-free` vs `seizures` (distance 1, ratio 0.125),
  `seizure-cluster` vs `seizures`, `seizure-freedom` vs `seizures`, `seizures` vs a `seizure` buried
  inside `generalised tonic clonic seizure`. Reading the adjudicator's `reason` text for the 5 hits
  that land on `MODEL_DEFENSIBLE` (EA0084, EA0088, EA0127, EA0156, EA0168) shows the real mechanism
  is a **different, already-documented one**: the model predicts the correct `state=seizure-free`
  attribute but anchors it to a generic `seizures` `CUIPhrase` instead of gold's specific
  `seizure-free` text span — a phrase-normalization/state-tagging convention gap, not a spelling
  error. The other 5 hits land on `GOLD_RIGHT` (EA0005, EA0038, EA0102, EA0110, EA0195) — confirmed
  false positives: these are real, adjudicated-genuine extraction misses (e.g. EA0005: "the model's
  lone prediction ... never mentions [the ongoing rate] in any form") that happen to share the word
  "seizure" with something else the model did predict in the same letter.
- **Diagnosis: 3/51 H2 rows flagged, 0 are genuine typos.** Same "seizure" stem-collision pattern
  (`temporal-lobe-onset-seizure` vs `focal impaired awareness seizures`, etc.); reading the reasons
  shows uncertainty-hedging and narrative-restatement, not spelling. This is a useful **consistency
  check**, not a success: Diagnosis's dominant inflation mechanism was already established
  separately (the 2026-06-30 Dx canonical row-adjudication) to be gold multiplicity/consolidation,
  not orthography — so finding ~0 genuine orthographic hits here is exactly what should happen, and
  the 3 raw flags the heuristic does produce are noise, not signal.

So the raw mechanical signal's **precision as an orthography detector, measured against manual
reading of the adjudicator's own reasoning, is 7/20 = 35% globally** — 100% (7/7) within
Prescription, 0% (0/13) within the two seizure/epilepsy-stem-narrow families. The failure mode is
specific and explicable: Prescription's vocabulary (drug names) is lexically diverse, so an
edit-distance-1/2 neighbor is highly specific to a true typo; SeizureFrequency's and Diagnosis's
vocabulary is dominated by inflections/compounds of a handful of clinical stems ("seizure" above
all), so the same threshold collides on morphology rather than transcription error.

**A related false-negative mode**, found via the secondary reason-keyword signal (recall this is
*not* part of the pre-flight-usable verdict, only a retrospective corroboration check): 3 rows
across SF (EA0025, EA0128) and Diagnosis (EA0040) have `reason` text explicitly describing a
genuine near-typo/wording-variant (`tonic chronic` vs `tonic-clonic`, `generalized` vs
`generalised`, `secondarily generalised` vs `secondary generalised`) that the mechanical signal
**missed**. In each case the phrase contains a common filler token ("tonic", "clonic", "seizures")
that matches a candidate at distance 0, and the global-minimum-over-all-token-pairs design picks
that trivial exact match instead of surfacing the real, non-zero-distance divergence on the
meaningful token. Against the 10 reason-keyword-flagged rows total (7 Prescription + 2 SF + 1 Dx)
as a weak ground truth, the mechanical signal's **recall is 7/10 = 70%** (all 3 misses are this
same masking artifact, all outside Prescription).

## 4. Interpretation

The literal kill-criterion the plan specified — recover Prescription's typo cases, don't false-alarm
on Investigations — **passes outright, no hedging needed.** Prescription's vocabulary (proper-noun
drug names) is exactly the regime this kind of edit-distance check is built for, and it performs
perfectly there: 100% recall of the 7 genuine cases, 0 false positives anywhere in Prescription or
Investigations.

But the deeper, more useful finding is the boundary condition this exposes: **edit distance over
short content tokens is a good orthography detector only when the family's vocabulary is lexically
diverse.** SeizureFrequency and Diagnosis are precisely the two families whose annotation convention
is already known (from prior work) to route real H-inflation through gold multiplicity and
phrase-normalization rather than spelling — and this heuristic, run naively on those families, would
have reported a false "orthographic" story if its raw flag count were trusted rather than
cross-checked line-by-line. That cross-check is exactly the step a pre-flight tool exists to avoid
having to do (by hand, per case) before deciding whether adjudication budget is worth spending — so
a naive read of this heuristic's flag rate would have been actively misleading for those two
families.

## 5. Pre-flight decision rule

Before spending adjudication budget on a new entity family's `source_near` evidence-recall gap:

1. **Run this heuristic's mechanical span-similarity check** (edit distance ≤2 absolute or ≤15%
   relative, over ≥4-letter content tokens, missed span vs. same-letter same-family predictions) on
   whatever `H2_GENUINE_DIVERGENCE`-equivalent miss population exists (or, pre-adjudication, on the
   full FN population before any H1/H2 split has even been done).
2. **Before trusting the hit count, check the family's vocabulary diversity first.** A rough,
   cheap proxy: sample same-family predicted spans within a handful of letters and check whether
   they share a common short stem (as SF's "seizure*" and Dx's "*seizure*"/"*epilepsy*" do) or are
   lexically distinct proper nouns/labels (as Prescription's drug names and Investigations' test-type
   labels are).
   - **Lexically diverse vocabulary** (drug names, test-type labels, proper nouns): trust the raw
     hit rate. A high share of flagged misses (this run: 7/19 = 37% of Prescription's H2 population)
     is a real, actionable signal that `source_near`'s literal substring match — not the model or the
     annotation — is the bottleneck, and building/rebuilding a normalized surface-matching layer
     (fuzzy match, canonical drug-name dictionary) is worth doing before paying for adjudication.
   - **Narrow/stem-sharing vocabulary** (this run: SeizureFrequency, Diagnosis — anything built
     around a small set of clinical-event nouns with many inflected/compound forms): **do not trust
     the raw hit rate as an orthography signal.** Expect a meaningful false-positive rate (this run:
     SeizureFrequency + Diagnosis produced 13 combined flags — 0/13 genuine typos on manual read;
     5/13 landed on already-`GOLD_RIGHT` rows, confirmed false positives against the existing
     verdict; the other 8/13 landed on `MODEL_DEFENSIBLE`/`BOTH_DEFENSIBLE` rows but on inspection
     encode a different, already-documented mechanism, not orthography). A hit in this regime is weak
     evidence of *some* representation mismatch worth a human glance, not evidence of a typo
     specifically — route it to the phrase-normalization/consolidation hypothesis first, orthography
     second.
3. Either way, this check is near-zero marginal cost (no LLM calls, runs in well under a second per
   family) and should run **before** committing a 4-reviewer adjudication pass, not as a replacement
   for one — it tells you which mechanism hypothesis to predeclare, not the final verdict.
