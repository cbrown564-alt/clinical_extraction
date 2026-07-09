# SF point/range shape-equivalence scorer fix (result)

Date: 2026-07-08. Owner: ExECTv2 SF inspection workstream.
Trigger: user review of the SF inspection tab (`/exectv2-sf-inspection`) surfaced two
letters (EA0005, EA0008) where a gold bare count/cadence and a model prediction
expressing the identical value as a degenerate (`lower == upper`) range were
scored as unrelated attributes.

## Root cause

`SEIZURE_FREQUENCY` (and, identically, `ONSET`/`PATIENT_HISTORY` for age) lets an
annotator express one quantity two ways: a bare attribute (`NumberOfSeizures`,
`NumberOfTimePeriods`, `Age`), or a `Lower*`/`Upper*` split pair. Nothing in the
scorer recognized the equivalence: `match.py:match_key`/`_attribute_key` and
`seizure_frequency.py:_frequency_active_rate_keys` all built literal
`(key, value)` tuples straight off the raw attribute dict, so `NumberOfSeizures=2`
(gold) and `LowerNumberOfSeizures=2, UpperNumberOfSeizures=2` (pred, same value)
produced different tuples and scored FP+FN for a fact both sides state
identically.

`clinical_headline`/`state_profile`/`state_profile_directional`/
`state_profile_direction_deconf`/`state_profile_magnitude` are **not** affected:
they key on `_count_based_state` (`seizure_frequency.py:270-289`), which checks
only "is any count field present," never the exact value or shape. This is why
the bug was invisible in the primary cited numbers and only showed up in the
`active_rate_fidelity` companion metric and the "Strict" (`exact_semantic`/
`benchmark_with_cui`) lens — both of which do a literal attribute-tuple
comparison and exist specifically to *not* be as forgiving as the headline key.

## Fix

- `scoring/normalize.py`: new `resolve_point_range(attributes, triple)` —
  collapses a `(bare, lower, upper)` triple to `("point", value)`, `("range",
  lower, upper)` (a genuine, non-degenerate range — never equal to a point from
  the other side), or `("conflict", ...)` (bare disagrees with the bounds — left
  unresolved on purpose). New `canonicalize_point_range_attributes` rewrites a
  degenerate range onto its bare key for the scorer's dict-based key builders.
- `contract/entities.py`: new `POINT_RANGE_TRIPLES` registry — every
  `EntitySpec` was checked; only SeizureFrequency (`NumberOfSeizures`,
  `NumberOfTimePeriods`) and the shared Onset/PatientHistory `Age` triple have
  this duality.
- `match.py:match_key`/`_attribute_key` and
  `seizure_frequency.py:_frequency_active_rate_keys` canonicalize through the
  registry before building their tuples.
- `sf_inspection.py:_attr_pair` (the frontend's own Layer A display) gets a
  non-destructive companion, `_point_range_match_overrides`: it computes the
  same triple-level verdict via `resolve_point_range` but does **not** rewrite
  the displayed gold/pred values, so the UI still shows "gold said a bare count,
  pred said a range" — it just no longer marks that shape difference itself as
  an error. `frontend/lib/sfSchema.ts:describePairDivergence` needed no changes:
  it already only treats `match === "bad"` rows as divergent.

## Effect (dev140, `exectv2_sf_magnitude_complement_dev140_20260708.jsonl`, zero new LLM calls)

| Metric | Before | After | Δ |
| --- | --- | --- | --- |
| `clinical_headline` | 0.9290 | 0.9290 | 0 (unaffected, as predicted) |
| `state_profile` | 0.9338 | 0.9338 | 0 |
| `state_profile_directional` | 0.8602 | 0.8602 | 0 |
| `state_profile_magnitude` | 0.9244 | 0.9244 | 0 |
| `active_rate_fidelity` | 0.6774 (tp63/fp38/fn22) | **0.7865** (tp70/fp23/fn15) | **+0.1091** |
| `exact_semantic` / `benchmark_with_cui` | 0.4333 (tp99/fp171/fn88) | **0.4551** (tp104/fp166/fn83) | **+0.0218** |

`sf_inspection.py`'s faithfulness gate (which hard-asserts `state_profile`/
`state_profile_directional`/`state_profile_magnitude` reproduce the anchors
within 1e-4) passes unchanged. `n_with_errors` (letters with ≥1 component error)
drops 94 → 91.

Other pipelines that exercise this code path also moved, confirming the fix
generalizes across configs, not just the one artifact measured above (frozen
test baselines updated with inline disclosure, see
`tests/test_exectv2_clinical_finding_assembly.py::test_holistic_manifest_reproduces_dev140_score_ladder`
and `tests/test_exectv2_sf_surface_registry.py::test_p1_v09_dev140_sf_scores_match_frozen_baseline`):
the v01 dev140 holistic manifest's `benchmark["raw"]` moved 0.2968 → 0.3094,
`benchmark["after_cui_projection"]` 0.3786 → 0.3912, and its SF
`active_rate_fidelity` companion 0.3908 → 0.5632; the archived v09
partial-hybrid manifest's SF `active_rate_fidelity` companion moved
0.5907 → 0.6919. `assembly/pipeline.py:BASELINE_SF_ACTIVE_RATE_FIDELITY = 0.2887`
is a `>=` regression floor, not an equality target — the fix only ever raises
`active_rate_fidelity`, so the floor stays safe (if now conservative) and needs
no numeric change; a disclosure comment was added in place.

## Explicitly out of scope

- **EA0005's residual divergence** (a `TimeSince_or_TimeOfEvent=Since` the
  prediction adds that gold never stated) is a *different* mention/attribute in
  this letter, not resolved by this fix, and deliberately not folded in: whether
  a correct-but-unrequested temporal anchor should count against precision at
  all is a separate policy question.
- **EA0008's residual `FrequencyChange` divergence** (`Increased` vs `Same`) is
  the already-tracked SF-2/SF-3 direction/magnitude axis, untouched by this fix.
- No re-run of the historical experiment markdown files (`active_rate_fidelity`
  is cited with a number in 59 archived docs) — those are point-in-time records;
  only the live regression-gate constant and the canonical dev140 test
  baselines were updated, per the project's overwrite-with-disclose convention.

## Companion: gold-data-error surfacing (a distinct bug class)

While auditing the same tab, EA0079 looked like a plain FP ("he gets around 1
generlised tonic clonic seizure in his sleep per month" scored as unmatched) but
is a **different** defect: gold's own T2 mention (offsets 621-651, over this
exact sentence) codes `TimePeriod=Year, NumberOfTimePeriods=2` — "1 per 2
years" — which has no textual basis anywhere near the span; the prediction's
`NumberOfSeizures=1, NumberOfTimePeriods=1, TimePeriod=Month` is the textually
correct reading. This is not a point/range duality (no Lower/Upper involved) and
not a gold omission (a mention exists) — it's a genuine gold value error, the
same class already tracked for one Prescription case (EA0146) in
`experiments/gold_data_issues.jsonl`. Logged as a new entry there.

The existing `experiments/gold_case_ledger_seizurefrequency.jsonl` (64 rows,
`verdict ∈ {gold_right, model_defensible, both_defensible}`) and
`gold_data_issues.jsonl` were, until now, read only by the separate `/gold-noise`
Observatory tab — completely disconnected from the SF inspection tab the user
was actually using. `sf_inspection.py` now loads both (best-effort: the ledger
was adjudicated against a different run, `exectv2_gepa_sf_verify_gpt41mini_20260628`,
than the one this module scores, so its rows are surfaced at the letter level as
prior-adjudication context, not claimed to match one exact mention; the
`gold_data_issues` entries are precise per-fact and attach directly to the
disputed mention). Frontend: a `SfGoldAdvisory`/`SfGoldCaseLedgerRow` pair of
types, a gold-toned advisory banner on the disputed Layer A pair
(`SfInspectionLayerA.tsx`), and a per-letter "prior gold-quality adjudication"
note (`SfInspectionViews.tsx:GoldCaseLedgerNote`). Scored PRF1 is unchanged by
this wiring — it is display-only disclosure, not a scoring reclassification.

Not done (flagged as a follow-up, not silently skipped): a fresh Phase-6/7-style
multi-agent adjudication of every currently-unledgered FP/FN in the *current*
`20260708` run. That is comparable cost to the original 42-53-letter,
5-parallel-agent effort already on record and needs its own authorization.
