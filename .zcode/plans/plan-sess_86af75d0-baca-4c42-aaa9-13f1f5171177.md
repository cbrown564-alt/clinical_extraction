## Goal
A standalone, self-contained HTML inspection report: gold vs. prediction for **every** dev140 letter, **SeizureFrequency only**, broken into (a) each schema attribute and (b) each of the 11 scoring components, with the full prediction-transformation chain (validation → normalization → canonicalization → state projection → key construction) rendered for every mention so you can see exactly where the model is right and wrong.

## Data sources (strongest LLM-based SF run)
- **Predictions**: `experiments/exectv2_sf_magnitude_complement_dev140_20260708.jsonl` (gpt-4.1-mini magnitude-complement; top LLM arm: directional F1 0.8602, magnitude F1 0.9244).
- **Gold**: `load_letters_for_split('dev')` (the canonical source; 140 letters, 187 SF gold mentions). The artifact's `gold_mentions` field is NOT SF-filtered, so gold comes from the loader.
- **Provenance cross-ref**: `experiments/exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl` (baseline) to detect exactly which mentions had `FrequencyChange` overwritten by the LLM magnitude selector.

## Deliverables
1. **`scripts/render_exectv2_sf_inspection_html.py`** — a generator script (mirrors the repo's `run_exectv2_*.py` convention) that imports the *real* scoring/state/normalize/validate functions, computes everything per letter, and emits the HTML. Using a generator (not hand-writing) guarantees the stages shown match the code.
2. **`experiments/exectv2_sf_inspection_dev140_20260708.html`** — the standalone artifact.

## Faithfulness contract (built into the script)
Before writing any HTML, the script re-scores all 140 letters and **asserts** the aggregate F1 reproduces the published summary (0.9338 state_profile / 0.8602 directional / 0.9244 magnitude within 1e-4). If reproduction fails, it aborts and writes nothing — so the report can never silently drift from the scorer.

## Per-letter rendering (two layers, per your "Both" choice)

### Layer A — Schema attributes (per mention, gold vs pred)
Pair gold↔pred SF mentions using the real `_match_gold_to_predictions` (max-cardinality phrase-overlap matcher from `match.py`). For each pair, show every `SEIZURE_FREQUENCY` attribute (NumberOfSeizures, Lower/Upper, NumberOfTimePeriods + Lower/Upper, TimePeriod, TimeSince_or_TimeOfEvent, FrequencyChange, PointInTime, dates, ages, CUI/CUIPhrase, Certainty, Negation) with the **prediction pipeline** rendered as a left→right chain:
`raw value → closed-vocab validity (validate_mention) → canonicalized (canonicalize_attribute_value) → gold value → ✓/✗`
Unpaired gold mentions = FN, unpaired pred = FP (shown in dedicated bands). Illegal/out-of-vocab values flagged red.

### Layer B — Scoring components (the 11 FrequencyStateScores)
For each letter, for each of the 11 components (`clinical_headline`, `state_profile`, `state_profile_directional`, `state_profile_direction_deconf`, `state_profile_magnitude`, `active_rate`, `active_rate_fidelity`, `seizure_free`, `unknown`, `exact_semantic`, `benchmark_with_cui`), show:
- each gold mention's attributes → `_count_based_state` → the component's state projection → final hashable key
- each pred mention's same cascade → final key
- the multiset comparison for THIS letter: gold-key set, pred-key set, **matched (TP)**, **pred-only (FP)**, **gold-only (FN)** — color-coded so right/wrong is immediate

This is where "stages of normalisation, dictionary mapping and scoring rules applied to the prediction before determining an answer" is most legible: each component projects through a different rule, and you'll see e.g. a gold `increased` vs pred `same` surface as an FP+FN on `directional` but a match on `state_profile` (the count-based bucket both collapse to).

### "Dictionary mapping" illustration (honest, from stored lineage)
- Show `candidate_spans` → `predicted_mentions` for the letter, documenting that the deterministic `SeizureFrequencyDictionaryLens` (phrase→CUI, count/range extraction, seizure-free/active inference) bridged them.
- Where the LLM magnitude selector overwrote `FrequencyChange` (detected by diffing complement vs baseline v08), render that as an explicit highlighted override row with old→new value and provenance "LLM magnitude complement".
- A note in the report header states SF `draft_mentions` are empty in this lineage (rules-owned) so no raw-LLM-draft stage is shown — no fabricated intermediates.

## HTML structure
- **Self-contained**: inline `<style>` + inline `<script>`, no external requests, opens in any browser.
- **Header**: run metadata (artifact, model, split, date) + the 11 aggregate F1s as a scorecard + a legend (gold/pred/TP/FP/FN color coding, closed-vocab/illegal flags).
- **Sticky nav**: list of all 140 `EA####` ids with per-letter error badges (e.g. "3 FP, 1 FN" on directional) and quick-jump anchors; filter toggles ("only letters with errors", and a per-component filter).
- **140 per-letter sections** (collapsible; collapsed by default except for error-bearing letters): Layer A (attributes) then Layer B (11 components). Letters with zero SF in both gold and pred get a one-line "no SeizureFrequency activity" row so *every* letter is represented, as asked.
- Dense, readable, monospace-leaning clinical-audit aesthetic (dark text on light, semantic color only).

## Execution order
1. Write `scripts/render_exectv2_sf_inspection_html.py` (reusing real functions; no reimplementation of scoring logic).
2. Run it; it asserts reproduction then writes the HTML.
3. Open/spot-check a few known-error letters (EA0008, EA0022, EA0050 — directional disagreements I already located) to confirm the right/wrong rendering is correct, and report the file path + headline scorecard.