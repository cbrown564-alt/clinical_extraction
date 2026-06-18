# Gold Label Audit

Date: 2026-05-14

## Context

A 5-document pilot of Phase 1A (primary sweep, `--limit 5`) produced scores well below expectation:
`medication_name` ~0.65, `seizure_type` ~0.41, `benchmark_collapsed` ~0.35. Expected baseline is ≥0.80
for established tasks. Investigation revealed the gap is **not model quality** — it is a combination of
fundamental flaws in how the gold labels are loaded and represented. Several problems silently produce
wrong gold records without raising errors.

---

## Markup CSV Schema (observed)

The gold labels are sourced from
`data/raw/exect_v2/MarkupOutput_200_SyntheticEpilepsyLetters/`. None of the CSVs have a header row.
Column indices are assumed by the loader. Below is the observed schema from direct inspection.

### MarkupDiagnosis.csv (572 rows)

| col | content | example |
|-----|---------|---------|
| 0 | Letter ID (filename with `.txt`) | `EA0008.txt` |
| 1 | Start char offset | `136` |
| 2 | End char offset | `173` |
| 3 | CUI (leading space present) | ` C0270834` |
| 4 | CUIPhrase (canonical hyphenated form) | `focal-seizures-with-altered-awareness` |
| 5 | Surface text | `focal-seizures-with-altered-awareness` |
| 6 | Negation | `Affirmed` / `Negated` |
| 7 | DiagCategory | `Epilepsy` / `MultipleSeizures` / `SingleSeizure` / `null` |
| 8 | Certainty | `5` (scale unclear) |

**DiagCategory distribution**: `Epilepsy` 310, `MultipleSeizures` 238, `SingleSeizure` 21, `null` 2.

### MarkupSeizureFrequency.csv (263 rows)

| col | content | example |
|-----|---------|---------|
| 0 | Letter ID | `EA0001.txt` |
| 1 | Start char offset | `239` |
| 2 | End char offset | `276` |
| 3 | CUI | ` C0270834` |
| 4 | Surface text of the span | `focal-seizures-with-altered-awarenes` |
| 5 | CUIPhrase | `focal-seizures-with-altered-awareness` |
| 6 | FrequencyChange | `Increased` / `Decreased` / `null` |
| 7 | NumberOfSeizures (lower bound) | `0`–`15` / `null` |
| 8 | NumberOfSeizures (upper or exact) | numeric / `null` |
| 9–24 | Time period fields, qualifiers | various |

**Key**: col6 is a `FrequencyChange` qualifier, not a count. When col6 is non-null (e.g. `Increased`),
the row is a qualitative frequency change note, not a quantified frequency record. The seizure type in
col4/col5 is the span the annotator tagged, not a canonical type classification.

### MarkupPrescriptions.csv (294 rows)

| col | content | example |
|-----|---------|---------|
| 0 | Letter ID | `EA0008.txt` |
| 1 | Start char offset | `189` |
| 2 | End char offset | `254` |
| 3 | CUI | `C0064636` |
| 4 | Drug CUIPhrase (canonical) | `lamotrigine` |
| 5 | Surface drug name | `lamotrigine` |
| 6 | Dose | `75` |
| 7 | Dose unit | `mg` |
| 8 | Frequency code | `2` (twice daily) |
| 9 | Context span | `Current-anti-epileptic-medication:-lamotrigine-75mg-bd-...` |

**No temporality column exists**. The file has no field that distinguishes current from planned or
previous medications. All entries were assumed current by the original annotators, but the letters
contain planned ("To start X") and tapering ("reduce and stop") prescriptions that are also tagged.

### Other files (not yet audited for gold use)

- `MarkupPatientHistory.csv` (656 rows) — likely contains historical medication mentions and clinical history; not currently used
- `MarkupInvestigations.csv` (183 rows) — EEG/MRI results; partially used but 166/183 rows have `null` in col7
- `MakupBirthHist.csv` (47 rows) — birth/onset history; not currently used
- `MarkupEpiCause.csv` (36 rows) — aetiology annotations; not currently used
- `MarkupOnset.csv` (24 rows) — age/date of onset; not currently used
- `MarkupWhenDiag.csv` (17 rows) — date of diagnosis; not currently used

---

## Bugs Found in the Original Loader (`datasets/exect.py`)

### Bug 1 — Seizure types sourced from the wrong file (critical)

**Original behaviour**: `seizure_types` were populated from `MarkupSeizureFrequency.csv` by reading
col4/col5 and calling `canonical_seizure_type()`.

**Correct source**: Seizure type classifications live in `MarkupDiagnosis.csv` under DiagCategory
`MultipleSeizures` and `SingleSeizure`. These are the annotated, CUI-grounded seizure type labels.

`MarkupSeizureFrequency` records *how often* seizures happen and *which span* was tagged for the
frequency. It is not a seizure type registry. Using it as one causes two classes of error:

1. **FrequencyChange rows produce spurious gold types.** When col6 is `Increased`/`Decreased`,
   the span (col4/col5) is a generic term like `"seizure"` or `"seizures-have-returned"`. These
   pass the `if seizure_type:` guard and enter the gold as `"seizure"`, `"seizures"`, or
   `"seizures have returned"` — strings no model would emit as a seizure type classification.

2. **Specific seizure types from MarkupDiagnosis are silently ignored.** The 238 `MultipleSeizures`
   and 21 `SingleSeizure` rows in MarkupDiagnosis are never read for seizure_types. For EA0008 the
   gold seizure type *should* come from MarkupDiagnosis (`focal-seizures-with-altered-awareness`)
   but instead comes from MarkupSeizureFrequency where the same span happens to also appear — along
   with the FrequencyChange row that injects `"seizure"` as a second gold type.

**Impact**: Every document where seizures are mentioned narratively (returning, increasing, etc.)
gets a spurious generic gold seizure type, producing systematic FN against every model.
`seizure` alone appears 21 times and `seizures` 31 times as col4 values across the 263 frequency rows.

**Status**: Fixed. See Implementation section below.

### Bug 2 — `planned_medications` empty for all documents

**Original behaviour**: `planned_medications` is populated only by `apply_temporality_gold()`, which
reads a separate challenge set CSV. For the 5 pilot documents this produced empty lists for all docs.

**Root cause**: `MarkupPrescriptions.csv` has no temporality column. All prescription rows are loaded
as `current_medications` regardless of context. The source text for EA0008 includes:

> "To start levetiracetam as detailed below"

Levetiracetam appears in the text and the .ann file as a Prescription span, but it is absent from
`MarkupPrescriptions.csv` for EA0008. This appears to be an annotation decision (the annotators may
have only tagged the drug in its dose-instruction context, not the "to start" span), or a loader
bug that silently dropped the row.

As a result: levetiracetam is correctly identified as planned by the model but scores as a false
positive because it is neither in `current_medications` nor in `planned_medications` in the gold.

**Scope unknown**: It is unclear how many documents across the 200-letter set have planned or
tapering medications that are mislabelled as current, or silently absent.

**Status**: Partially addressed — prescriptions now loaded from JSON (more reliable source), but
the absence of a temporality column in the annotation data is a fundamental limitation. The
temporality challenge set remains the only source of planned/previous annotations.

### Bug 3 — EA0016 has no gold record at all

`load_exect_gold` returns an empty `GoldDocument` for EA0016 (no medications, no seizure types,
no diagnosis). The document is in the validation split and is processed by the runner, but since
`errors.json` records `"missing_gold": false`, the runner does not flag it as missing gold — it
simply scores everything as FP/FN against an empty gold set.

**Root cause identified**: EA0016 has two `SingleSeizure` Diagnosis annotations in the JSON
(`focal-seizure`, certainty=5, affirmed), but no `Epilepsy`-category diagnosis and no prescriptions.
The original loader only read MarkupDiagnosis for `DiagCategory="Epilepsy"` rows and never loaded
seizure types from `MultipleSeizures`/`SingleSeizure` rows, so EA0016 produced nothing. Since its
medications and frequency CSVs are also empty, the document appeared completely unannotated.

**Status**: Fixed. EA0016 now correctly has `seizure_types: ["focal seizure"]`, empty medications
(correct — no drugs annotated), and empty diagnoses (correct — single focal seizure event, not
established epilepsy). The `abstention` metric for EA0016 is now scored correctly.

### Bug 4 — Duplicate and mixed-specificity diagnoses

EA0029's gold diagnoses load as `['epilepsy', 'juvenile myoclonic epilepsy']` — both a generic and a
specific label for the same diagnosis. A model that correctly outputs `"juvenile myoclonic epilepsy"`
still incurs FN=1 for not also outputting `"epilepsy"`. The gold loader does not deduplicate across
specificity levels, and the `canonical_diagnosis()` function maps both raw forms to distinct outputs
rather than collapsing the generic under the specific.

The root cause is that MarkupDiagnosis can have multiple `Epilepsy`-category rows for the same letter
at different levels of specificity, all of which pass the `affirmed` + `epilepsy` filter and are
appended to the diagnosis list.

**Status**: Flagged via `ambiguous_gold` warning in `GoldDocument.warnings`. Resolution requires an
explicit policy decision. See Open Design Questions below.

### Bug 5 — Encoding failures silently drop rows

The markup CSVs are latin-1 encoded but were opened with `utf-8-sig` in the original exploration,
causing `UnicodeDecodeError` on multi-byte characters. The current loader uses a lower-level
`read_csv_rows` helper — its encoding handling needs explicit confirmation. Silent drops due to
encoding errors could explain Bug 3 (EA0016) and may affect other documents.

**Status**: Resolved by primary source switch. Diagnoses, prescriptions, and investigations now load
from UTF-8 JSON files. The only remaining CSV is `MarkupSeizureFrequency.csv`, now opened explicitly
with `encoding="latin-1"`.

### Bug 6 — `evidence_support` reporting appears broken but is actually categorical

`evidence_support` records have `weighted_mean=` (blank) in all reporting tables. This is not a
bug in scoring — evidence support statuses are categorical strings (`supported_by_gold_span`,
`valid_quote_no_gold_overlap`, `no_quote`, etc.) and the aggregation correctly omits `weighted_mean`
for non-numeric values. The data is in `category_counts` and is present. However:

1. The reporting tables do not surface `category_counts` in a readable column, so the metric looks
   absent when it is not.
2. The distinction between `valid_quote_no_gold_overlap` (valid quote, but annotators didn't mark
   a span there) and `supported_by_gold_span` depends on gold spans existing — if gold spans are
   wrong (Bug 1) then evidence support classification is also wrong.

**Status**: Not yet addressed. Secondary to Bugs 1–3. Will improve automatically once the gold
span loading is stable.

---

## Implementation (Phase C complete)

### Primary source switch: CSV → JSON

`datasets/exect.py` was rewritten to use the per-document JSON annotation files at
`data/raw/exect_v2/Json/EA*.json` as the primary source for:

- **Diagnoses** (entity type `Diagnosis`, DiagCategory `Epilepsy`, Certainty ≥ 4, Negation=Affirmed)
- **Seizure types** (entity type `Diagnosis`, DiagCategory `MultipleSeizures` or `SingleSeizure`,
  Certainty ≥ 4, Negation=Affirmed)
- **Prescriptions** (entity type `Prescription`, using `DrugName`/`DrugDose`/`DoseUnit`/`Frequency`
  attributes directly rather than column indices)
- **Investigations** (entity type `Investigations`, using structured `EEG_Results`/`MRI_Results`
  attributes rather than keyword-matching the normalised CUIPhrase string)

`MarkupSeizureFrequency.csv` is retained as the source for `seizure_frequencies` only (it has richer
count/period structure than the JSON). The CSV is opened with `encoding="latin-1"`. Seizure types
are no longer derived from it.

### Certainty filter

All seizure type and diagnosis extraction from JSON requires `Certainty ≥ 4` (probable/definite on
the 1–5 annotation scale). This excludes certainty=3 "possibly X" annotations that were previously
entering the gold silently. The threshold is parameterised as `_MIN_CERTAINTY = 4` in `exect.py`.

### Prescription normalization fix

The JSON `DrugName` attribute uses CamelCase concatenation for multi-word drug names
(`"SodiumValproate"`, `"EslicarbazepineAcetate"`). `canonical_medication_name()` lowercases these
to single tokens that do not match the `ASM_SYNONYMS` dictionary (which uses space-separated keys
like `"sodium valproate"`). The `CUIPhrase` attribute uses the correct hyphen-separated form
(`"sodium-valproate"`, `"eslicarbazepine"`) which normalises correctly. The loader now prefers
`CUIPhrase` over `DrugName` as the name source.

### Diagnosis specificity hierarchy

When multiple `Epilepsy`-category Diagnosis annotations exist for the same document at different
specificity levels, the gold `epilepsy_diagnosis_type` field now keeps only the most specific label.
The hierarchy is encoded in `_DIAGNOSIS_PARENT` in `exect.py`:

- `focal epilepsy` → parent: `epilepsy`
- `generalized epilepsy` → parent: `epilepsy`
- `juvenile myoclonic epilepsy` → parent: `generalized epilepsy`

`_collapse_diagnoses_to_most_specific()` removes any label whose more specific descendant is also
present. Applied in `gold_document_to_record()` so the raw loaded diagnoses are preserved for
inspection. `_validate_gold_document()` emits a `specificity_collapsed` warning recording what
was dropped and what remains.

### Gold quality warning system

`GoldDocument` carries a `warnings: list[str]` field populated by `_validate_gold_document()`.
Warning codes:

- `missing_gold` — no medications, seizure types, or diagnoses after loading
- `gold_noise` — seizure types list contains generic terms ("seizure", "seizures")
- `specificity_collapsed` — one or more generic diagnoses removed by the hierarchy

Warnings flow into `GoldRecord.quality_flags["gold_warnings"]` for downstream inspection.

**Corpus-level results** (all 200 documents):
- `missing_gold`: 6 documents (EA0023, EA0024, EA0073, EA0076, EA0078, EA0100)
- `specificity_collapsed`: 55 documents
- `gold_noise`: 0 documents (generic seizure terms eliminated by source fix)

---

## Smoke Test Results (Phase D)

5-document pilot re-run using `core_qwen35_current_relaxed` (qwen3.6:35b, validation split,
`--limit 5`) after the gold loader fix. Documents: EA0008, EA0016, EA0018, EA0026, EA0029.

Runs: `gold_fix_smoke_v1` (source fix + certainty filter only), `gold_fix_smoke_v2` (+ CUIPhrase
normalization fix + specificity collapse).

| Metric | Before fix | v1 (source+certainty) | v2 (+ CUIPhrase + Q1) | Total change |
|---|---|---|---|---|
| `seizure_type` F1 | 0.133 | 0.733 | **0.733** | +0.600 |
| `seizure_type` TP (sum) | 1 | 5 | 5 | +4 |
| `seizure_type` FP (sum) | 7 | 3 | 3 | −4 |
| `benchmark_collapsed` F1 | 0.133 | 0.933 | **0.933** | +0.800 |
| `benchmark_collapsed` precision | 0.200 | 1.000 | 1.000 | +0.800 |
| `benchmark_collapsed` recall | 0.100 | 0.900 | 0.900 | +0.800 |
| `medication_name` F1 | 0.693 | 0.593 | **0.693** | 0.000 |
| `abstention_decision_correct` | 0.800 | 1.000 | **1.000** | +0.200 |

The +0.60 seizure_type swing comes entirely from fixing the gold source (Bug 1 + Bug 3). EA0016
moved from all-FP (model correct, gold empty) to all-TP. The v1 medication drop (−0.10) was a
regression from CamelCase `DrugName` normalisation failure on `SodiumValproate` in EA0026; the
CUIPhrase fix in v2 restores it to the pre-fix baseline.

`benchmark_collapsed` precision is 1.00 across 5 documents — zero false positives. The remaining
0.10 recall gap is a genuine model miss, not a gold artefact.

The pre-fix `benchmark_collapsed` F1 of 0.133 is confirmed as a **gold-standard fidelity ceiling**,
not a model-capacity ceiling. The audit's predicted achievable ceiling of 0.92–0.95 appears
reachable given the current 0.93 result on 5 documents.

---

## Design Decisions

### Q1 — Mixed-specificity diagnosis deduplication (resolved)

**Decision**: Keep the most specific diagnosis per document using a formal specificity hierarchy.
When both `'epilepsy'` and `'focal epilepsy'` are present in gold, keep only `'focal epilepsy'`.

**Implementation**: `_DIAGNOSIS_PARENT` in `exect.py` defines the hierarchy (`focal epilepsy →
epilepsy`, `generalized epilepsy → epilepsy`, `juvenile myoclonic epilepsy → generalized
epilepsy`). `_collapse_diagnoses_to_most_specific()` removes any label whose more specific
descendant is present. Applied in `gold_document_to_record()`. 55 of 200 documents were affected.

**Key examples** (see `data/raw/exect_v2/Json/`):
- `EA0029.json`: `['epilepsy', 'juvenile myoclonic epilepsy']` → `['juvenile myoclonic epilepsy']` —
  two separate annotation positions; "epilepsy" at offset 358, "jme" at offset 258.
- `EA0004.json`: `['epilepsy', 'focal epilepsy']` → `['focal epilepsy']` — overlapping spans at
  offset 21; annotator tagged both "epilepsy" (21–30) and "epilepsy – probable focal" (21–46).
- `EA0011.json`: `['epilepsy', 'focal epilepsy']` → `['focal epilepsy']` — clean separation;
  "temporal-lobe-epilepsy" at offset 12 (diagnosis line) and "epilepsy" at offset 578 (narrative).

### Q2 — Certainty representation (decided)

**Decision**: Threshold at Certainty > 3 (i.e., ≥ 4) for the primary sweep. Certainty=3
("possibly X") annotations are excluded from the flat gold set. Full certainty field representation
is deferred to the annotation-reproduction experiment where it is a first-class feature.

**Rationale**: The primary sweep measures extraction accuracy against definite annotations. The
interesting question — whether models correctly calibrate uncertainty on Certainty=3 cases — is
better answered by an experiment that explicitly asks for it, not by silently including uncertain
annotations in a flat gold.

**Key example** (`EA0026.json`): The only `Epilepsy`-category Diagnosis entry is `"JME"` at
Certainty=3, filtered by the threshold. Gold `diagnoses` is empty. The letter contains GTCS
(MultipleSeizures, Certainty=5) and myoclonic jerks (PatientHistory), which together constitute
the JME triad. A model reasoning from the clinical picture outputs `'juvenile myoclonic epilepsy'`
and scores FP=1 against an empty gold. This is the intended trade-off: the primary sweep measures
definite annotation reproduction; the annotation-reproduction experiment measures clinical
reasoning under uncertainty.

### Q3 — Medication normalization (resolved)

**Root cause**: JSON `DrugName` attribute uses CamelCase (`"SodiumValproate"`,
`"EslicarbazepineAcetate"`). `canonical_medication_name()` lowercases without splitting, producing
`"sodiumvalproate"` — not a key in `ASM_SYNONYMS` (which has `"sodium valproate"` with a space).
`CUIPhrase` uses hyphen-separated canonical form (`"sodium-valproate"`) that normalises correctly.

**Fix**: Loader now uses `CUIPhrase` as primary name source, falling back to `DrugName` only when
`CUIPhrase` is absent. Medication F1 restored to 0.693 (baseline level) after this fix.

**Key example** (`EA0026.json`): `DrugName="SodiumValproate"` vs `CUIPhrase="sodium-valproate"`.
Also affects `EA0011.json`: `DrugName="EslicarbazepineAcetate"` vs `CUIPhrase="eslicarbazepine"`.

### Q4 — Multiple seizure types and frequency (design decision, schema work pending)

**Decision**: The existing gold and schema do not give models adequate guidance when a patient has
multiple active seizure types with different frequencies. Two approaches are needed at different
schema complexity levels.

**The problem** (`EA0011.json`): Two distinct seizure types annotated with different temporal
status. `"focal-seizures-with-altered-awareness"` (MultipleSeizures, Certainty=5) has a frequency
of 1 per 2 weeks (ongoing, no YearDate). `"focal-to-bilateral-convulsive-seizures"` (MultipleSeizures,
Certainty=5) has `NumberOfSeizures=0, YearDate=2017, TimeSince="Since"` — seizure-free for that
type since Christmas 2017. The current schema collapses both into a flat `seizure_types` list with
a single `seizure_frequency` field, forcing the model to either pick one type's frequency or blend
them — neither of which represents the clinical situation accurately.

**Simple schema approach** (schema ladder Steps 3–4): Instruct the model to identify the most
clinically current seizure type and report only its frequency. For EA0011 this would be the focal
seizures (ongoing, biweekly) rather than the convulsive type (resolved 2017). Task guidance needs
an explicit instruction: *"When multiple seizure types are present, report the frequency for the
most recently active type. Report 'seizure free' only when all types are resolved."* The gold
`seizure_frequency` field should be linked to the corresponding `seizure_type` in evaluation.

**Complex schema approach** (annotation-reproduction probe or a new schema ladder step): Each
seizure type carries its own frequency, including `"unknown"` where the letter mentions the type
but not its rate. Schema shape:

```json
{
  "seizure_types": [
    {"type": "focal impaired awareness seizure", "frequency": "twice weekly"},
    {"type": "focal to bilateral tonic clonic seizure", "frequency": "seizure free since 2017"}
  ]
}
```

Gold for this schema can be constructed by cross-referencing Diagnosis and SeizureFrequency JSON
entities matched on CUI. Where no SeizureFrequency entry matches a Diagnosis CUI, the gold
frequency for that type is `"unknown"`. This schema requires changes to the task definition,
schema contract, and scorer — `"unknown"` must be a valid output that scores neither as TP nor FP.

**What is pending**:
1. Add per-type frequency instruction to the Step 3 and Step 4 task guidance in `configs/tasks.yaml`
   (simple approach — guidance change only, no schema change).
2. Define the complex schema contract for the annotation-reproduction probe.
3. Implement per-type frequency gold construction using CUI cross-referencing in the loader.

---

## Future Directions

### Annotation-reproduction experiment

The natural extension of the schema ladder is a step that asks: *if the model is given the v9
annotation guidelines and asked to produce the same structured output as the trained annotators,
how faithfully can it reproduce the annotation decisions?*

Gold for this task is the JSON annotation files directly — including DiagCategory, Certainty,
Negation, temporal scope, and the multi-attribute prescription and frequency records. This is the
most rigorous and most expansive schema in the project.

This experiment is interesting for three reasons:

1. **It makes the annotation policy explicit as a task requirement.** The guidelines explicitly
   instruct annotators to ignore temporal scope for seizure types. A model that follows the
   guidelines faithfully matches the gold; a model that applies clinical judgment diverges. The
   divergence is measurable and attributable to a specific guideline instruction, not to model
   error. This is a direct empirical test of annotation-faithful vs. clinically-faithful behaviour.

2. **It reveals which schema elements add vs. harm clinical value.** The richer annotation schema
   includes fields that are clinically meaningful (DiagCategory distinguishing MultipleSeizures
   from SingleSeizure; Certainty capturing diagnostic confidence) and fields that introduce
   clinical error (the temporal blindness instruction; the absence of a family-history field).
   Running both annotation-faithful scoring and a corrected-gold scoring on the same outputs
   quantifies each element's net contribution to measurement quality.

3. **It is the hardest version of the task.** All current schema ladder steps simplify or collapse
   the annotation schema. Reproducing the full schema tests whether scaling model capability or
   prompt complexity improves performance at the annotation-fidelity ceiling — distinct from
   whether it improves clinical extraction accuracy.

This would fit naturally as a new run group (`annotation_reproduction_probe`), separate from
`schema_ladder_sweep`, with its own gold loading path that uses the JSON entities without the
current specificity/certainty simplifications.

---

## What Not to Fix Yet

- Do not add per-type frequency guidance to the task configs (Q4 simple approach) until the
  schema_ladder_sweep baseline results are in — the change affects how models are scored on Steps
  3 and 4, so it should not be introduced mid-sweep.
- Do not implement the complex per-type frequency schema (Q4 complex approach) until the simple
  approach is validated and the annotation-reproduction probe is formally scoped.
- Do not change scoring aggregation to surface `category_counts` in the main tables (Bug 6) until
  evidence support quality is confirmed — secondary to completing the primary sweep.
- Do not run the annotation-reproduction experiment until schema_ladder_sweep results are stable —
  the ladder characterises the task space that the reproduction experiment is compared against.
