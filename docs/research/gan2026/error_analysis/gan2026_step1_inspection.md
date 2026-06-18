# Gan 2026 Step 1 Reproduction Inspection

Date: 2026-05-31

## Reproduced Surface

- Loaded all 1,500 rows from `data/Gan (2026)/synthetic_data_subset_1500.json`.
- Exposed source row identity, full note text, gold seizure-frequency label, gold evidence/reference, and author quality flags.
- Parsed all 1,500 gold labels into the monthly numeric values used by the evaluation category mapper.
- Verified the local evaluator with focused tests and simple constant baselines.

## Observed Distribution

- `row_ok=True`: 1,435 rows.
- `row_ok=False`: 65 rows.
- `row_ok=False` label breakdown:
  - `no seizure frequency reference`: 54
  - 11 remaining rows contain parseable frequency or seizure-free labels.
- Unique gold seizure-frequency labels: 404.
- Purist category distribution:
  - `seizure_freq_unknown`: 340
  - `seizure_freq_more1week_less1day`: 327
  - `currently_no_seizure`: 223
  - `seizure_freq_more1mon_less1week`: 214
  - `seizure_freq_more1per6mon_less1mon`: 157
  - `seizure_freq_1ormore_daily`: 128
  - `seizure_freq_1_per_mon`: 69
  - `seizure_freq_1_per_week`: 20
  - `seizure_freq_1_per_yr`: 14
  - `seizure_freq_1_per_6mon`: 8

## Simple Baseline Checks

These are reproduction sanity checks, not model results.

- Constant `unknown` prediction, Purist:
  - micro F1 / accuracy: 0.2267
  - macro F1: 0.0370
  - weighted F1: 0.0838
- Constant seizure-free prediction, Purist:
  - micro F1 / accuracy: 0.1487
  - macro F1: 0.0259
  - weighted F1: 0.0385

## Contradictions And Ambiguities

- The JSON field named `clinic_date` contains the full clinic letter, not only a date. The loader now names this `note_text`, but the raw field remains misleading.
- The canonical gold label is embedded at `check__Seizure Frequency Number.seizure_frequency_number[0]`; the surrounding object also contains analysis text and references. This should stay explicit because future tasks may have similar category-specific check fields.
- The author scripts contain two cluster interpretations:
  - `z_step3_csv2json_and_get_freq.py` drops the trailing `per cluster` detail when parsing bounds.
  - `e_evaluation_synthetic_results.py` expands cluster labels by multiplying cluster count by seizures per cluster.
  - Decision: the local scoring path follows the evaluation script for monthly frequency because that is the value used for model scoring.
- Month normalization uses a 30-day month and then divides yearly values by 12. Therefore `1 per month` becomes `365 / 30 / 12`, approximately `1.0139`, not exactly `1.0`.
- `unknown`, `no seizure frequency reference`, `multiple per ...`, and unresolved cluster unknowns all collapse to the numeric sentinel `1000` before category mapping. This preserves author scoring behavior but loses clinically important distinctions.
- Decision: include the 65 `row_ok=False` rows in the evaluation surface. Most are no-reference examples, which are useful negative controls against a model that always asserts seizure frequency exists. Retain `row_ok` for stratified error analysis because the flag is not perfectly equivalent to no-reference.

## Implications

- Any benchmark-facing result should state that it uses the evaluation-script cluster expansion rather than the CSV-prep parser's cluster-count-only behavior.
- The next normalization work should separate raw semantic label, parsed bounds, scoring sentinel, and final category so we can preserve clinical distinctions while staying compatible with Gan scoring.
- Deterministic baseline work should not start from free-form label strings alone; it needs an explicit conversion policy for sentinels, ranges, clusters, and `multiple`.
