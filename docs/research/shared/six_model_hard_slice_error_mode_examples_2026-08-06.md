# Illustrated examples for hard-slice error modes

Date: 2026-08-06  
Status: development illustration from retained no-call artifacts  
Paper-library role: detailed case record; use the [row-evidence workbook](../artifacts/paper_source_row_evidence_2026-08-10.xlsx) for filtering

Protocol: [examples protocol](six_model_hard_slice_error_mode_examples_protocol_2026-08-06.md)  
Parent: [hard-slice error modes](six_model_hard_slice_error_modes_2026-08-06.md)  
Artifact: [`experiments/six_model_hard_slice_error_mode_examples_20260806.json`](../../experiments/six_model_hard_slice_error_mode_examples_20260806.json)

## How to read this

Every primary mode from the parent study appears below with up to two
development examples. Preference: consensus-wrong ids, then Sol/Luna when
available. Evidence strings are **model-selected spans** from saved artifacts,
not full notes. Holdout sealed.

Regenerate: `python scripts/build_six_model_hard_slice_error_mode_examples.py`

---

## 1. Gan ordinary rates (`llm`)

### `over_abstain_unknown`

Gold has a countable point rate; scored prediction is `unknown`.

- **Row 13051 / Sol.** Gold `2 per 8 month` → `unknown`.  
  Evidence: “a generalised tonic-clonic seizure 3 Tuesdays ago, preceded by a
  cluster of absences.” Rationale treats the recent event as non-recurring.
- **Row 13178 / Sol.** Gold `1 per 6 month` → `unknown`.  
  Evidence: “he was seizure-free for 6 months, until a focal impaired-awareness
  seizure occurred 2 Thursdays ago.”

### `wrong_point_rate_selection`

Gold and prediction are both ordinary point rates, but Purist bands differ.

- **Row 12788 / Sol.** Gold `6 per 4 month` → scored `6 per year`
  (boundary raw was `unknown`; format repair built the year total).  
  Evidence: “with only six focal impaired-awareness seizures reported so far
  this year.” Hybrid rescues back to `6 per 4 month`.
- **Row 12810 / Sol.** Gold `5 per 2 month` → `5 per year`.  
  Evidence: “just five generalised tonic-clonic seizures documented this year
  to date.” Hybrid rescues to gold.

### `false_seizure_free`

Quiet/post-treatment interval wins over an active gold rate.

- **Row 14540 / Sol.** Gold `2 per 8 month` → `seizure free for multiple year`.  
  Evidence: “Since commencing Levetiracetam he has not had further events.”
- **Row 14581 / Sol.** Gold `2 per 3 month` → `seizure free for multiple year`.  
  Evidence: “He has had no further events since surgical intervention and
  initiation of Levetiracetam.”

### `over_abstain_no_reference`

Boundary often emits an illegal cluster fragment; adapter collapses to
no-reference.

- **Row 13122 / Sol.** Gold `3 per year`; boundary `3 per cluster` → scored
  `no seizure frequency reference`. Hybrid rescues to `3 per 1 year`.  
  Evidence: three tonic seizures after a quiet year on valproate.
- **Row 14332 / Sol.** Gold `5 per 2 month`; boundary `5 per cluster` → scored
  `no seizure frequency reference`. Hybrid rescues to gold.

### `false_range`

Model (or repair) emits a range where gold is a single point rate.

- **Row 12823 / Sol.** Gold `9 per month` → `1 per 3 to 4 week`.  
  Evidence: “occurring roughly once every three to four weeks.” Hybrid
  rescues to `9 per month` (Pragmatic already near-miss).
- **Row 13209 / Sol.** Gold `1 per 8 month` → `1 per 4 to 5 week`
  (boundary said `1 cluster every 4 to 5 weeks`).

### `false_multiple_word`

Model substitutes vague `multiple per …` for a numeric point rate.

- **Row 13114 / Sol.** Gold `1 per year` → `multiple per day`.  
  Evidence: “brief morning myoclonic jerks on the preceding two days.”
- **Row 1880 / Sol.** Gold `8 per 2 month` → `multiple per week`.  
  Evidence: events “occurring several times per week” (competing semiology /
  reading). Consensus six-model wrong.

### `parse_or_call_failure`

No usable scored label (schema/JSON failure). Rare; both retained examples are
Qwen.

- **Row 16719 / Qwen.** Gold `7 per 6 month`; empty prediction.  
  Parse: `schema_validation_error: Field required`.
- **Row 16839 / Qwen.** Gold `9 per 4 month`; empty prediction.  
  Parse: `invalid_json: Unterminated string…`.

### Boundary-only ordinary modes

These appear at the model boundary before llm-only format repair.

#### `false_cluster_structure`

- **Row 13122 / Sol.** Gold ordinary `3 per year`; boundary `3 per cluster`
  (later becomes no-reference).
- **Row 13209 / Sol.** Gold `1 per 8 month`; boundary `1 cluster every 4 to 5
  weeks` (later smooth range).

#### `other_malformed_or_unparsed`

- **Row 12788 / mini.** Boundary `6 so far this year` → scored `6 per year`.
- **Row 12827 / mini.** Boundary `5 so far this year` → scored `5 per year`.

---

## 2. Gan clusters (`llm`)

### Model-boundary diagnostic: `incomplete_cluster_grammar`

This is the key mechanism before scoring. Models say “N clusters per month”
without `, M per cluster`.

- **Row 10097 / Sol.** Gold `3 cluster per month, multiple per cluster`;
  boundary `3 clusters per month` → scored `unknown`.  
  Evidence: “nocturnal clusters 3×/month.”
- **Row 10237 / Sol.** Gold `4 cluster per month, multiple per cluster`;
  boundary `4 clusters per month` → scored `unknown`.

### Scored `collapse_to_unknown`

Same rows after format adapter reject incomplete cluster grammar.

- **Row 10097 / Sol** and **10237 / Sol** as above: clinically near-right
  cluster cadence becomes Purist `unknown`.

### Scored `collapse_to_no_reference`

Cluster half without cadence collapses to no-reference.

- **Row 15404 / Sol.** Gold `1 cluster per 4 month, 3 to 4 per cluster`;
  boundary `3 to 4 per cluster` → `no seizure frequency reference`.  
  Evidence: “clusters of three - four seizures in a single day.”
- **Row 15429 / Sol.** Gold `1 cluster per 2 month, 4 per cluster`;
  boundary `4 per cluster` → `no seizure frequency reference`.

### Scored `dropped_to_smooth_rate`

Cluster structure discarded; only a smooth rate remains.

- **Row 9943 / Sol.** Gold `1 cluster per 4 to 5 week, multiple per cluster`
  → `1 per 4 to 5 week` (boundary still said “cluster”).  
  Evidence: events “group together … every four to five weeks.”
- **Row 10434 / Luna.** Gold `multiple cluster per week, 2 to 3 per cluster`
  → `multiple per week`.  
  Evidence: “occurring on several mornings each week.”

### Scored `wrong_cluster_parameters`

Fullish cluster grammar, wrong counts/cadence.

- **Row 17135 / Sol.** Gold `5 cluster per month, multiple per cluster` →
  `1 cluster per month, multiple per cluster`.  
  Evidence: “clusters of absence seizures on five days each month”
  (five *days* misread as one cluster-month pattern).
- **Row 10965 / Sol.** Gold `2 cluster per month, 4 to 5 per cluster` →
  `2 cluster per month, multiple per cluster` (loses the 4–5 count).

### Rare scored modes

- **`false_seizure_free` (1 retained example):** row **15519 / mini**. Gold
  `1 cluster per 4 day, 3 per cluster` → `seizure free for multiple year`
  after a long boundary string about 4-day quiet intervals and batching.
- **`parse_or_call_failure` (1 retained example):** same row **15519** under
  another model’s empty/failed comparison path in the pooled inventory.

---

## 3. Gan clusters (`llm_with_rules`)

Incomplete grammar is gone from finals. Residuals are quote-backed selection /
projection failures.

### `collapse_to_unknown`

- **Row 10673 / Sol.** Gold `1 cluster per month, multiple per cluster` →
  `unknown`. Boundary had “approximately 1 seizure cluster per month.” Exact
  evidence present.
- **Row 17110 / Sol.** Gold `4 to 5 cluster per week, multiple per cluster` →
  `unknown`. Boundary: “clusters on 4 to 5 days per week.”

### `dropped_to_smooth_rate`

- **Row 10434 / Sol.** Gold `multiple cluster per week, 2 to 3 per cluster` →
  `multiple per week`. Boundary mentioned “sometimes 2 to 3 per morning” but
  final drops cluster grammar.
- **Row 9943 / Sol.** Gold `1 cluster per 4 to 5 week, multiple per cluster` →
  `1 per 4 to 5 week`. Consensus hybrid wrong.

### `wrong_cluster_parameters`

- **Row 17135 / Sol.** Same five-days-per-month misread as under hybrid:
  gold `5 cluster per month…` → `1 cluster per month…`.
- **Row 10965 / Sol.** Gold `2 cluster per month, 4 to 5 per cluster` →
  `2 cluster per month, multiple per cluster`.

### `collapse_to_no_reference`

- **Row 11109 / Luna.** Gold `2 cluster per month, 5 per cluster` →
  `no seizure frequency reference`. Boundary/evidence center on “5 or more
  seizures in 24 h” without keeping monthly cluster cadence.
- **Row 15497 / Luna.** Gold `1 cluster per 4 to 5 day, 5 per cluster` →
  `no seizure frequency reference` from a “5 in 24 hours” reading.

### `false_seizure_free`

Quiet intervals between clusters promoted to seizure-free.

- **Row 15593 / Sol.** Gold `1 cluster per 5 day, 2 to 4 per cluster` →
  `seizure free for multiple year`. Evidence: “occasionally manage five days
  without seizures, though this is usually followed by a day of clustering.”
- **Row 15513 / mini.** Gold `1 cluster per 4 to 5 day, 2 to 3 per cluster` →
  `seizure free for multiple year` from the same quiet-interval pattern.

---

## 4. ExECT SeizureFrequency

Letter-exact unit-key failures. Mention texts/attributes are from saved
predictions; states are the coarse clinical-headline states.

### `empty_gold_spurious`

Gold SF empty; model emits active-rate.

- **EA0092 / Sol (`llm` and hybrid).** Gold `[]` → pred active-rate mention
  “cluster of complex partial seizures” (`NumberOfSeizures: 1`).
- **EA0148 / Sol (`llm`).** Gold `[]` → pred “seizures” with
  `NumberOfSeizures: 2`.

### `extra_states_only`

Gold state set recovered, plus extras (usually active-rate).

- **EA0142 / Sol (`llm`).** Gold `{seizure-free}` →
  `{active-rate, seizure-free}` (historical/count mention added).
- **EA0162 / Sol (hybrid).** Gold `{seizure-free}` →
  `{active-rate, seizure-free}` (adds a December 3-in-1-day active-rate).

### `missed_states_only`

Subset of gold keys missing; no extras.

- **EA0022 / Sol (both surfaces).** Gold `{seizure-free, unknown}` →
  `{seizure-free}` only (drops the separate infrequent/unknown inventory item).
- **EA0025 / Sol (hybrid).** Gold `{active-rate, unknown}` → `{active-rate}`
  (keeps GTC rate, drops myoclonic `FrequencyChange: Frequent` unknown/active
  companion).

### `missed_all_sf`

Gold has SF; prediction emits none.

- **EA0176 / Sol (both surfaces).** Gold seizure-free mention → pred `[]`.
- **EA0139 / mini.** Gold active-rate (“generalised”, 2 since last clinic) →
  pred `[]`.

### `substituted_or_mixed`

Both false positives and false negatives on unit keys.

- **EA0011 / Sol (both surfaces).** Gold states include
  `{active-rate, seizure-free, unknown}`; pred keeps active-rate +
  seizure-free but misses/mismatches the third inventory item (unit-key
  identity), so the letter is imperfect despite looking partly right.
- **EA0038 / Sol (hybrid).** Gold active-rate (1 GTC per year) → pred
  seizure-free (3 years) — state substitution, not a near paraphrase.

---

## Coverage checklist

| Slice / surface | Modes illustrated |
| --- | --- |
| Ordinary `llm` scored | all 7 |
| Ordinary `llm` boundary-only | `false_cluster_structure`, `other_malformed_or_unparsed` |
| Cluster `llm` scored | all 6 (2 rare modes have only one retained example each) |
| Cluster `llm` boundary | `incomplete_cluster_grammar` (+ overlapping scored modes) |
| Cluster hybrid | all 5 |
| ExECT SF `llm` | all 5 imperfect modes |
| ExECT SF hybrid | all 5 imperfect modes |

## Supersession

Prefer the full catalogs (every Gan bucket; every ExECT family) with summary
and examples together:

- [Gan category error catalog](../gan2026/category_error_catalog_2026-08-06.md)
- [ExECT family error catalog](../exectv2/family_error_catalog_2026-08-06.md)

## Claim boundary

Development illustration of named hard-slice modes. Not clinical validation,
not sealed holdout inspection, and not a Decision 0046 rewrite. Do not tune
prompts or rules from these exemplars without a new predeclared study.
