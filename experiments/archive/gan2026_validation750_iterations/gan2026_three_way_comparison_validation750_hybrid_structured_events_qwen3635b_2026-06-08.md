# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-08

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 750 rows.
Rare full-validation reason: Phase 1 three-way architecture comparison (gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07): RESUME of full validation750 run, qwen3.6:35b pass via local Ollama, covering the three remaining architectures (deterministic, deterministic_canonical_pipeline, and hybrid already completed cleanly and are NOT re-run here). All prior fixes are now permanent in source: (1)+(2) llm_only_direct_labeler/llm_only_canonical_pipeline answer_kind enum communication, (3) schema_repair.py _ASSERTION_ALIASES 'unknown'->'unclear' corruption, (4)+(5) llm_only_canonical_pipeline shared dialect-repair switch + max_tokens 1200->2400 + strict=False literal-control-character fallback + 'ration'->'rationale' typo repair. NEW Bug #6 found mid-run: llm_only_direct_labeler showed a climbing failure trend (0,0,0,1,4 across the first 50/750 rows, all truncation: 'LM response was truncated due to exceeding max_tokens=900'). Root-caused via two-stage re-pilot: (a) raising max_tokens alone (900->2400) was INSUFFICIENT -- the same 4/50 failures persisted, just shifting from truncation-induced JSON errors to malformed-JSON errors ('Expecting property name enclosed in double quotes', 'Invalid control character'), proving qwen's verbose chain-of-thought reasoning embeds unescaped quotes/newlines in JSON string values; (b) the actual gap was that parse_decision_json used raw json.loads instead of the shared parse_json_payload_with_schema_repair helper (missing dialect repair + strict=False fallback) -- switching to the shared helper (matching llm_only_canonical_pipeline's fix) brought failures down to 3/50 (6%). The residual 3/50 is the SAME fundamental pattern already characterized and accepted for llm_only_canonical_pipeline: certain ambiguous notes push qwen into a structurally-fragile output style embedding unescaped quotes and raw newlines inside JSON string values, breaking JSON beyond what can be safely auto-repaired without risking corruption of clinical content (two of the three failing rows, 960 and 987, reproduced identically across all three re-pilot attempts -- genuinely fragile notes, not a fixable systemic gap). This ~6% rate is consistent with llm_only_canonical_pipeline's documented ~4-8% accepted noise and is being accepted on the same basis: comparable in magnitude to baseline noise (~1-4%) elsewhere, and itself a meaningful comparison data point about this architecture's robustness to verbose local-model output styles. max_tokens for llm_only_direct_labeler is raised to 2400 (matching hybrid/llm_only_canonical_pipeline) for this run. A SEVENTH bug (#7) was found immediately after relaunching with the Bug #6 fixes in place: 2 of the first 7/150 failures were a NEW error type, 'schema_validation_error: Input should be low, medium or high', caused by qwen emitting a stringified numeric confidence value (e.g. confidence: '0.8' or '0.85' as a JSON string) instead of the categorical low/medium/high label. The existing _repair_numeric_confidence helper in schema_repair.py only coerced bare int/float values, not numeric strings -- extended it to also parse and bucket stringified numerics (>=0.8 high, >=0.45 medium, else low), leaving non-numeric strings untouched. This is a fix to the SHARED repair_decision_payload path, so it benefits llm_only_canonical_pipeline and any other architecture using it too. Verified via a 150-row re-pilot with --disable-dspy-cache: zero schema_validation_error/confidence failures recurred; only the previously-characterized invalid_json residual noise (rows 960, 987, 2554, 2558, 2678, 338 -- qwen embedding unescaped quotes/raw newlines in verbose chain-of-thought reasoning, breaking JSON beyond safe auto-repair) reproduced, at 6/150 (4%), squarely within the accepted ~4-8% noise band documented for llm_only_canonical_pipeline. An EIGHTH bug (#8) was found mid-run at row 350/750 of the resumed run: 7 of 15 failures (47%) were a NEW error type, 'schema_validation_error: Input should be a valid string', root-caused to qwen legitimately emitting a JSON null for the time_window field (e.g. when answer_kind is 'unknown'/'no_reference' and no specific time window applies), whereas the LlmOnlyDirectLabelerDecisionRecord and LlmOnlyCanonicalPipelineDecisionRecord schemas declared time_window as a required str. gpt-4.1-mini never emits null here (it always emits a string, often '' for the same semantic case), which is why this never surfaced in the gpt-4.1-mini pass -- but null is an equally valid representation of 'no time window applies', matching the precedent already set by hybrid_structured_events's time_window: str | None field. Fixed by changing time_window from 'str' to 'str | None = None' in BOTH llm_only_direct_labeler.py and llm_only_canonical_pipeline.py (a shared schema fix benefiting both architectures still queued in this run -- canonical_pipeline was about to inherit the identical defect). Verified two ways: (a) directly re-parsing all 7 previously-failing raw_outputs (rows 5996, 6087, 6192, 6967, 7290, 7389, 7506) confirmed each now produces time_window=None with zero errors; (b) a fresh 50-row live re-pilot with --disable-dspy-cache reproduced ONLY the two already-characterized accepted-noise rows (960, 987 -- the same fragile-JSON pattern), with zero schema_validation_error recurrences. All 30 regression tests pass including two new guards (test_parse_decision_json_accepts_null_time_window_and_seizure_type in both llm_only_direct_labeler and llm_only_canonical_pipeline test suites). A NINTH bug (#9) was found in the v3 relaunch at row 500/750: 24 of 34 failures (71%) were the SAME error message, 'schema_validation_error: Input should be a valid string', but for a DIFFERENT field -- selected_seizure_type, root-caused identically to Bug #8: qwen legitimately emits JSON null for selected_seizure_type when answer_kind is 'no_reference' (the note contains no seizure-frequency information at all, so there is no seizure type to identify), where gpt-4.1-mini always emits a string (often '' or a descriptive phrase) for the same semantic situation -- confirmed via a full scan of both models' validation750 direct_labeler runs (gpt-4.1-mini: zero nulls across 750 rows for either field; qwen: 37 nulls in time_window, 24 in selected_seizure_type, with the 24 selected_seizure_type nulls mapping 1:1 onto the 24 new failures). Fixed identically to Bug #8: changed selected_seizure_type from 'str' to 'str | None = None' in BOTH llm_only_direct_labeler.py and llm_only_canonical_pipeline.py (the SAME two files, alongside the already-fixed time_window -- both fields now correctly nullable, matching hybrid_structured_events's existing pattern). Verified by directly re-parsing all 24 previously-failing raw_outputs: all 24 now produce valid decisions with selected_seizure_type=None and zero schema errors (2 carry only benign final_label_repaired notes, the same normalization-repair category seen throughout this run, not failures). All 30 regression tests pass, including updated guards (test_parse_decision_json_accepts_null_time_window_and_seizure_type) verifying BOTH nullable fields together in the realistic no_reference payload shape qwen actually emits. A TENTH finding (#10) emerged from investigating a climbing failure trend in the v4 relaunch: between rows 500-700/750, failures jumped from 10 to 24 (14 new failures in 190 rows, ~7.4% local rate vs ~2% baseline), coinciding with newly-appearing 'LM response was truncated due to exceeding max_tokens=2400' warnings -- suggesting a max_tokens defect. This hypothesis was DISPROVEN by direct experiment: raising max_tokens 2400->4000 and re-running the exact same failing rows with --disable-dspy-cache produced BYTE-IDENTICAL raw_output for every one of them (same length, same content, same invalid_json error), proving the model's own natural stopping point for these notes sits below even the 2400 ceiling -- the truncation warnings were a coincidental, separate phenomenon (likely silently absorbed by the existing repair fallback) and not the driver of the failure climb. Sampling the actual raw_outputs revealed the true cause: neither llm_only_direct_labeler.py nor llm_only_canonical_pipeline.py gave qwen ANY guidance on how to write the rationale field, so it filled it with verbose step-by-step deliberation -- e.g. "Is '4 per month' definitely allowed? The examples are '1 per day', '2 to 3 per month'. '4 per month' is structurally identical... I will proceed with '4 per month'." -- embedding nested quotes, question marks, run-on punctuation, and self-questioning that broke JSON parsing ('Invalid control character', "Expecting ',' delimiter", 'Unterminated string', and sometimes left the JSON object never closed at all). This is the SAME root-cause family as the already-characterized 'verbose CoT breaks JSON' noise, just manifesting as a locally denser cluster because rows in this region of validation750 happen to be longer/more ambiguous notes that invite more deliberation. FIXED at the prompt level (not schema/parsing): added an explicit instruction to both prompts -- 'Write rationale as one short, plain-language sentence stating only the deciding evidence and label... Do not show step-by-step reasoning, alternative options you considered and rejected, or self-questioning; state only the final justification' -- with a concrete example, bumping PROMPT_VERSION v0.1->v0.2 in both llm_only_direct_labeler.py and llm_only_canonical_pipeline.py. Verified via a targeted re-pilot that dropped and regenerated the previously-failing rows (source_row_index>=11000) fresh under the new prompt: 0/40 failures (vs the expected ~3/40 under the prior ~7% local rate), with direct sampling of 15+ raw rationale values confirming qwen now reliably produces single short plain-language sentences (e.g. "The note explicitly states 'several focal impaired-awareness spells per week', which maps directly to the normalized label 'multiple per week'.") and zero step-by-step narration; pragmatic/purist accuracy (0.85/0.825) remained consistent with the v0.1 baseline (~0.88/0.86), confirming no quality regression from the terser rationale style. max_tokens was also raised 2400->4000 for both architectures as a no-downside precaution (the byte-identical-output experiment proved it doesn't change behavior for rows that don't need the extra headroom, while still eliminating the handful of genuine truncation events observed, even though they were not the actual driver of this finding). Because PROMPT_VERSION changed, this run restarts llm_only_direct_labeler from scratch with --overwrite-existing -- the prior partial results used the v0.1 prompt and are not comparable. All 32 regression tests pass, including two new guards (test_build_prompt_input_instructs_short_plain_rationale in both llm_only_direct_labeler and llm_only_canonical_pipeline test suites) asserting the short-rationale instruction text is present in the prompt payload.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `ollama_chat/qwen3.6:35b`
- Provider/execution: native Ollama chat endpoint via DSPy/LiteLLM: `http://localhost:11434`
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_hybrid_structured_events_v0.5`
- Temperature: `0.0`
- Max tokens: `5000`
- Mode: `live`
- DSPy cache enabled: `True`
- Ollama Qwen thinking mode: `disabled` (`think=false`)
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-08T12:06:51.831653+00:00`
- Run finished UTC: `2026-06-08T19:35:25.525981+00:00`
- Wall-clock elapsed: `26912.592` seconds (`448.543` minutes)
- Throughput: `0.027868` rows/sec (`35.883` sec/row)
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=False`, `breakthrough_repair=True`, `clean_scorer_facing_gold_policy=False`, `dated_sequence_repair=True`, `elapsed_anchor_repair=True`, `json_dialect_repair=True`, `monthly_diary_repair=True`, `non_epileptic_repair=True`, `post_change_burst_repair=True`, `repair_mode=None`, `residual_jerk_repair=True`, `selected_evidence_repair=True`, `usual_interval_repair=True`
- Git commit: `f9845eb`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_qwen3635b_2026-06-08.jsonl`

## Summary

- Structured records: 746 / 750
- Call failures: 1
- Parse/schema/label issues: 4
- JSON dialect repairs: 744
- Deterministic repair notes: 497
- Exact selection evidence substrings: 561 / 750
- Purist validation accuracy/micro F1 proxy: 0.8320 (624 / 750)
- Pragmatic validation accuracy/micro F1 proxy: 0.8613 (646 / 750)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: '≤ 4 per day' -> '4 per day' |
| 40 | 4 per week | 4 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: '≤ 4 per week' -> '4 per week' |
| 79 | 6 to 7 per year | 6 to 7 per year | yes | json_dialect_repaired: python_literal; final_label_repaired: '≤ 6 to 7 per year' -> '6 to 7 per year' |
| 103 | 2 to 4 per year | 2 to 4 per year | yes | json_dialect_repaired: python_literal; final_label_repaired: '≤ 2 to 4 per year' -> '2 to 4 per year' |
| 128 | 17 per month | 17 per month | yes | json_dialect_repaired: python_literal |
| 156 | 1 per 6 day | 1 per 6 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 6 days' -> '1 per 6 day' |
| 180 | 1 per 7 day | 1 per 7 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per week' -> '1 per 7 day' |
| 182 | 1 per 2 day | 1 per 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'every 2 days' -> '1 per 2 day' |
| 187 | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 per 7 to 9 day'; evidence_not_exact_substring |
| 190 | 1 per 4 week | 1 per 4 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per month' -> '1 per 4 week' |
| 198 | 1 per 4 week | 1 per 4 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per month' -> '1 per 4 week' |
| 212 | 1 to 2 per month | 1 per 3 to 4 week | yes | json_dialect_repaired: python_literal |
| 218 | 1 per 3 week | 1 per 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 month | 1 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 278 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal |
| 280 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal |
| 338 | multiple per month | multiple per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'many per month' -> 'multiple per month' |
| 409 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '≤ 1 per month' -> '1 per month' |
| 419 | 2 per year | 2 per year | yes | json_dialect_repaired: python_literal |
| 446 | 15 per 3 month | 2 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: '≤ 2 per week' -> '2 per week'; final_label_repaired: '2 per week' -> '15 per 3 month' |
| 466 | 21 to 28 per month | 21 to 28 per month | yes | json_dialect_repaired: python_literal |
| 467 | 9 per month | 9 per month | yes | json_dialect_repaired: python_literal |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '12 to 30 per quarter' -> '12 to 30 per 3 month' |
| 598 | 2 per 16 month | 1 per 8 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per eight months' -> '2 per 16 month'; evidence_not_exact_substring |
| 659 | 2 per 4 day | 2 per 4 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 4 days' -> '2 per 4 day' |
| 665 | 2 per 2 week | 2 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 2 weeks' -> '2 per 2 week' |
| 678 | 2 per 4 month | 2 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 694 | 1 per week | 1 per week | yes | json_dialect_repaired: python_literal |
| 704 | 2 per month | 2 per month | yes | json_dialect_repaired: python_literal |
| 725 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'daily' -> '1 per day' |
| 731 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'daily' -> '1 per day' |
| 743 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal |
| 744 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal |
| 763 | 1 per week | 1 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'weekly' -> '1 per week'; evidence_not_exact_substring |
| 790 | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per week' -> '1 per 7 to 10 day' |
| 816 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 849 | 1 per year | 1 per year | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 854 | 1 per year | 1 per year | yes | json_dialect_repaired: python_literal |
| 869 | multiple per day | multiple per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per month' -> 'multiple per day' |
| 891 | 1 per 2 day | 1 per 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'every other day' -> '1 per 2 day' |
| 899 | 1 per 2 week | 1 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 959 | 1 per 2 month | 1 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 3 per month' -> '1 per 2 month' |
| 960 | 1 per 2 month | 1 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per month' -> '1 per 2 month' |
| 978 | 1 per 2 month | 1 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 987 | 1 per 2 month | 1 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per month' -> '1 per 2 month'; evidence_not_exact_substring |
| 1030 | 1 per month | 1 to 3 per month | no | json_dialect_repaired: python_literal; final_label_repaired: '1 to 3 per month (uncertain)' -> '1 per month'; evidence_not_exact_substring |
| 1046 | 3 to 5 per month | 3 to 5 per month | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 1070 | 3 to 4 per week | 3 to 4 per week | yes | json_dialect_repaired: python_literal |
| 1094 | 3 to 5 per week | 3 to 5 per week | yes | json_dialect_repaired: python_literal |
| 1165 | seizure free for multiple year | 5 to 7 per 3 week | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 6 weeks' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 1171 | 9 per 3 week | 7 to 9 per 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '9 per 3 week' |
| 1207 | 7 to 9 per week | 21 to 28 per 3 month | no | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 1223 | 3 to 4 per week | 3 to 4 per week | yes | json_dialect_repaired: python_literal |
| 1249 | 2 to 4 per week | 2 to 4 per week | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 1281 | 5 to 7 per 10 month | 5 to 7 per year | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 to 7 per year' -> '5 to 7 per 10 month' |
| 1317 | unknown | unknown, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day (cluster)' -> 'unknown' |
| 1357 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal |
| 1363 | 1 per day | 3 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day (cluster) and 1-2 per week' -> '1 per day'; evidence_not_exact_substring |
| 1413 | 9 per month | 9 per month | yes | json_dialect_repaired: python_literal |
| 1454 | 7 per week | 7 per week | yes | json_dialect_repaired: python_literal |
| 1486 | 2 per month | 3 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per month' -> '2 per month' |
| 1573 | 11 per week | 11 per week | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 1591 | 5 per month | 11 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '11 per month' -> '5 per month' |
| 1596 | 12 per week | 12 per week | yes | json_dialect_repaired: python_literal |
| 1597 | 12 per month | 12 per month | yes | json_dialect_repaired: python_literal |
| 1636 | 5 per month | 5 per month | yes | json_dialect_repaired: python_literal |
| 1640 | 5 per week | 5 per week | yes | json_dialect_repaired: python_literal |
| 1687 | multiple per day | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> 'multiple per day'; evidence_not_exact_substring |
| 1694 | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per 2 weeks' -> '3 per 2 week' |
| 1695 | seizure free for 1 month | multiple per month | no | json_dialect_repaired: python_literal |
| 1706 | multiple cluster per month, multiple per cluster | multiple cluster per month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> 'multiple cluster per month, multiple per cluster' |
| 1707 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal |
| 1772 | 11 per 6 month | 11 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '11 events in 6 months' -> '11 per 6 month' |
| 1773 | 11 per 3 month | 11 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '11 seizures in 3 months' -> '11 per 3 month' |
| 1790 | 8 per 4 month | 8 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '8 seizures in 4 months' -> '8 per 4 month' |
| 1794 | 8 per 2 month | 8 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '8 events in 2 months' -> '8 per 2 month' |
| 1866 | 8 per 2 month | 8 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '8 seizures in 2 months' -> '8 per 2 month' |
| 1880 | multiple per week | 8 per 2 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (including 7 convulsions and 1 drop attack in past 2 months)' -> 'multiple per week'; evidence_not_exact_substring |
| 1887 | 4 per 3 month | 4 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 seizures in 3 months' -> '4 per 3 month' |
| 1914 | 7 per 3 month | 7 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '7 seizures per 3 months' -> '7 per 3 month' |
| 1922 | 7 per 3 month | 7 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '7 seizures in 3 months' -> '7 per 3 month' |
| 1923 | 7 per 6 month | 7 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '7 seizures in 6 months' -> '7 per 6 month' |
| 1979 | 3 per 2 month | 6 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '3 per 2 month' |
| 1980 | 6 per 3 month | 6 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '6 per 3 months' -> '6 per 3 month' |
| 2023 | 5 per month | 5 per month | yes | json_dialect_repaired: python_literal |
| 2080 | multiple per day | multiple per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'multiple per day'; evidence_not_exact_substring |
| 2094 | multiple per month | multiple per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'multiple per month' |
| 2114 | multiple per month | multiple per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per month' -> 'multiple per month' |
| 2149 | multiple per week | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 2166 | multiple per day | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'frequent' -> 'multiple per day' |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '3 to 5 per 2 week' |
| 2233 | 6 to 7 per 2 month | 6 to 7 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '6 to 7 per 2 months' -> '6 to 7 per 2 month' |
| 2245 | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '7 to 8 per 3 week' |
| 2259 | 6 to 8 per 3 month | 6 to 8 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '6 to 8 per 3 months' -> '6 to 8 per 3 month' |
| 2354 | 6 to 7 per week | 6 to 7 per week | yes | json_dialect_repaired: python_literal |
| 2366 | 2 to 4 per year | 2 to 4 per year | yes | json_dialect_repaired: python_literal |
| 2369 | 3 to 4 per month | 3 to 4 per month | yes | json_dialect_repaired: python_literal |
| 2374 | 7 to 9 per month | 7 to 9 per month | yes | json_dialect_repaired: python_literal |
| 2425 | 6 to 8 per month | 6 to 8 per month | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 2427 | 3 to 5 per month | 3 to 5 per month | yes | json_dialect_repaired: python_literal |
| 2435 | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '5 to 7 per 2 week' |
| 2437 | 2 to 3 per 2 month | 2 to 3 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 3 per 2 months' -> '2 to 3 per 2 month' |
| 2440 | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 to 7 per 2 months' -> '5 to 7 per 2 month' |
| 2456 | 6 to 7 per 2 week | 6 to 7 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '6-7 per 2 weeks' -> '6 to 7 per 2 week' |
| 2459 | 5 per 5 month | 7 to 9 per 2 week | no | json_dialect_repaired: python_literal; final_label_repaired: '7 to 9 per 2 weeks' -> '7 to 9 per 2 week'; final_label_repaired: '7 to 9 per 2 week' -> '5 per 5 month' |
| 2487 | 2 to 3 per month | 2 to 3 per 3 month | no | json_dialect_repaired: python_literal |
| 2513 | 2 to 3 per 2 week | 2 to 3 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 3 per 2 weeks' -> '2 to 3 per 2 week'; evidence_not_exact_substring |
| 2541 | 8 to 9 per 2 week | 8 to 9 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '8 to 9 per 2 weeks' -> '8 to 9 per 2 week'; evidence_not_exact_substring |
| 2548 | 5 to 6 per 2 month | 5 to 6 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 to 6 per 2 months' -> '5 to 6 per 2 month' |
| 2554 | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 to 10 per 2 months' -> '1 to 10 per 2 month' |
| 2558 | 3 to 4 per 2 month | 3 to 4 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 to 4 per 2 months' -> '3 to 4 per 2 month' |
| 2609 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per night' -> '1 per day' |
| 2622 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day' |
| 2628 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day' |
| 2678 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day'; evidence_not_exact_substring |
| 2681 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal |
| 2698 | 1 per 2 day | 1 per 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'every other day' -> '1 per 2 day'; evidence_not_exact_substring |
| 2731 | 1 per 2 week | 1 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 2740 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 2748 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 2759 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 2762 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 2765 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 2776 | 1 per week | 1 per week | yes | json_dialect_repaired: python_literal |
| 2789 | 1 per week | 1 per week | yes | json_dialect_repaired: python_literal |
| 2812 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'daily' -> '1 per day' |
| 2822 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'daily' -> '1 per day' |
| 2824 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal |
| 2877 | 2 per year | 2 per year | yes | json_dialect_repaired: python_literal |
| 2887 | 2 per week | 2 per week | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 2907 | seizure free for multiple year | seizure free for 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 2932 | 13 per 2 month | seizure free for 9 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since 29/09/2017' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '13 per 2 month'; evidence_not_exact_substring |
| 2938 | seizure free for multiple year | seizure free for 8 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 2965 | seizure free for multiple year | seizure free for 16 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since 03-Sep-2017' -> 'seizure free for multiple year' |
| 2992 | 1 per 8 month | seizure free for 7 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 8 month' |
| 3015 | 1 per 13 month | seizure free for 12 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 1 year' -> '1 per 13 month' |
| 3048 | seizure free for 16 month | seizure free for 16 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 16 months' -> 'seizure free for 16 month' |
| 3058 | seizure free for 12 month | seizure free for 12 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 3082 | seizure free for 10 month | seizure free for 10 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 10 months' -> 'seizure free for 10 month' |
| 3095 | seizure free for 12 month | seizure free for 12 month | yes | json_dialect_repaired: python_literal |
| 3113 | seizure free for 14 month | seizure free for 14 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 3118 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 3137 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 3224 | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '6 to 7 per month' -> '1 cluster per month, 6 to 7 per cluster' |
| 3242 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 clusters per month' -> '2 cluster per month, 5 per cluster' |
| 3261 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 3 per week' -> '2 cluster per month, 4 per cluster' |
| 3262 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 clusters per month, ~5 events per cluster' -> '2 cluster per month, 5 per cluster' |
| 3281 | 8 per month | 8 per month | yes | json_dialect_repaired: python_literal |
| 3297 | 6 per month | 6 per month | yes | json_dialect_repaired: python_literal |
| 3325 | 3 per week | 3 per week | yes | json_dialect_repaired: python_literal |
| 3356 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 3371 | seizure free for multiple year | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 8 weeks' -> 'seizure free for multiple year' |
| 3436 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 3468 | unknown | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'perimenstrual cluster' -> 'unknown' |
| 3469 | unknown | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'perimenstrual cluster' -> 'unknown' |
| 3482 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'perimenstrual only' -> 'no seizure frequency reference' |
| 3493 | multiple per week | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (clustered peri-menstrually)' -> 'multiple per week'; evidence_not_exact_substring |
| 3507 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 3512 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal |
| 3528 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'increased frequency (relative)' -> 'no seizure frequency reference' |
| 3532 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'increased frequency (approx 20% increase over 3 weeks)' -> 'no seizure frequency reference' |
| 3534 | seizure free for 7 month | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 7 months' -> 'seizure free for 7 month' |
| 3600 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 3623 | 7 per week | 7 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (up to 7)' -> '7 per week'; evidence_not_exact_substring |
| 3643 | 7 per week | 7 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'up to 7 clusters per week' -> '7 per week' |
| 3681 | 9 per month | 9 per month | yes | json_dialect_repaired: python_literal |
| 3682 | 6 per month | 6 per month | yes | json_dialect_repaired: python_literal |
| 3710 | multiple per week | 5 per week | no | json_dialect_repaired: python_literal |
| 3753 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'daily' -> '1 per day'; evidence_not_exact_substring |
| 3766 | 8 per year | 8 per year | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 3774 | 9 per year | 9 per year | yes | json_dialect_repaired: python_literal |
| 3791 | 10 per year | 10 per year | yes | json_dialect_repaired: python_literal |
| 3801 | 9 per month | 9 per month | yes | json_dialect_repaired: python_literal |
| 3806 | 6 per month | 6 per month | yes | json_dialect_repaired: python_literal |
| 3827 | 7 per month | 7 per month | yes | json_dialect_repaired: python_literal |
| 3846 | 2 per day | 2 per day | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 3849 | 3 per day | 3 per day | yes | json_dialect_repaired: python_literal |
| 3889 | 8 per year | 8 per year | yes | json_dialect_repaired: python_literal |
| 3892 | 3 per year | 3 per year | yes | json_dialect_repaired: python_literal |
| 3940 | 4 per week | 4 per week | yes | json_dialect_repaired: python_literal |
| 3949 | 4 per week | 4 per week | yes | json_dialect_repaired: python_literal |
| 3988 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several times per week' -> 'multiple per week' |
| 3995 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 3999 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 4022 | 8 per month | 8 per month | yes | json_dialect_repaired: python_literal |
| 4026 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 4092 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 3 per week' -> '1 per 2 to 3 week' |
| 4100 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 every 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4110 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 to 2 per day' -> '1 per 1 to 2 day'; evidence_not_exact_substring |
| 4116 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per 1 to 2 day'; evidence_not_exact_substring |
| 4173 | 1 per 2 week | 1 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 4243 | multiple per week | 1 per 2 to 3 week | no | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 4258 | 4 per week | 4 per week | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 4337 | 3 per 1 month | 3 per 3 month | no | json_dialect_repaired: python_literal; final_label_repaired: '3 events in recent months' -> '3 per 3 month'; final_label_repaired: '3 per 3 month' -> '3 per 1 month' |
| 4345 | 4 per 5 month | 4 per month | no | json_dialect_repaired: python_literal; final_label_repaired: '4 per month' -> '4 per 5 month'; evidence_not_exact_substring |
| 4368 | 5 per 2 month | 5 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '5 per 2 month' |
| 4402 | 14 per 14 month | 7 per 7 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per month (historical average)' -> '1 per month'; final_label_repaired: '1 per month' -> '14 per 14 month'; evidence_not_exact_substring |
| 4410 | 4 per 7 month | 4 per 7 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week to multiple per month' -> '4 per 7 month'; evidence_not_exact_substring |
| 4478 | 19 per week | 19 per week | yes | json_dialect_repaired: python_literal |
| 4480 | 3 to 5 per week | 3 to 5 per week | yes | json_dialect_repaired: python_literal |
| 4496 | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '7-8 per quarter' -> '7 to 8 per 3 month' |
| 4562 | 1 per 6 week | 1 per 6 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 6 weeks' -> '1 per 6 week' |
| 4563 | 1 per 4 month | 1 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 4574 | 1 per 4 week | 1 per 4 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per month' -> '1 per 4 week' |
| 4592 | 1 per 2 month | 1 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 4597 | 1 per 3 week | 1 per 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 4624 | 3 to 4 per month | 1 per 3 to 4 day | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '3 to 4 per month'; evidence_not_exact_substring |
| 4631 | 1 per 14 to 21 day | 1 per 14 to 21 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per month' -> '1 per 14 to 21 day' |
| 4690 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal; final_label_repaired: '~10 per hour' -> 'multiple per day' |
| 4694 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per hour' -> 'multiple per day' |
| 4700 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per hour' -> 'multiple per day' |
| 4709 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal; final_label_repaired: '~6 per hour' -> 'multiple per day' |
| 4731 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 4732 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 4771 | multiple per week | unknown | yes | evidence_not_exact_substring |
| 4839 | 1 per 5 month | seizure free for multiple month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 4+ months' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 5 month' |
| 4842 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 4910 | seizure free for 2 year | seizure free for 2 year | yes | json_dialect_repaired: python_literal |
| 4919 | seizure free for 2 year | seizure free for 2 year | yes | json_dialect_repaired: python_literal |
| 4926 | seizure free for 1 year | seizure free for 1 year | yes | json_dialect_repaired: python_literal |
| 4951 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since February 2025' -> 'seizure free for multiple year' |
| 4956 | seizure free for 7 month | seizure free for 7 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 7 months' -> 'seizure free for 7 month' |
| 4992 | seizure free for 6 month | seizure free for 11 month | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 4994 | seizure free for 6 month | seizure free for 6 month | yes | json_dialect_repaired: python_literal |
| 5040 | seizure free for multiple year | seizure free for 6 months | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since 10 March 2025' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 5082 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5092 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 5110 | seizure free for 3 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 5121 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5136 | seizure free for 3 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; evidence_not_exact_substring |
| 5141 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since early August' -> 'seizure free for multiple year' |
| 5197 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5210 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5221 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for >1 year' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 5248 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5331 | seizure free for 12 month | seizure free for 12 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 5345 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 5351 | seizure free for 18 month | seizure free for 18 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 18 months' -> 'seizure free for 18 month' |
| 5379 | seizure free for 3 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 5406 | seizure free for 2 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month'; evidence_not_exact_substring |
| 5476 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 5490 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 5491 | multiple per week | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 5504 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 5507 | multiple per week | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 5528 | seizure free for 6 month | 1 per month | no | json_dialect_repaired: python_literal |
| 5534 |  | 1 per multiple month | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 5551 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per day' -> 'multiple per day'; evidence_not_exact_substring |
| 5567 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per week' -> 'multiple per week' |
| 5584 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per week' -> 'multiple per week' |
| 5624 | 1 per 10 day | 1 per 10 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 10 days' -> '1 per 10 day' |
| 5652 | 1 per 8 day | 1 per 8 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per week' -> '1 per 8 day' |
| 5682 | 2 to 4 per month | 2 to 4 per month | yes | json_dialect_repaired: python_literal |
| 5696 | 3 per 4 month | 3 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 5763 | 2 per 3 month | 2 per month | no | json_dialect_repaired: python_literal; final_label_repaired: '6 seizures in 3 months' -> '2 per 3 month' |
| 5767 | 2 per month | 1 per 1 to 2 week | yes | json_dialect_repaired: python_literal |
| 5791 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 5827 | multiple per day | multiple per week | yes | json_dialect_repaired: python_literal |
| 5837 | multiple per week | 2 cluster per 3 week, multiple per cluster | no | json_dialect_repaired: python_literal |
| 5866 | no seizure frequency reference | 4 per 6 week | no | json_dialect_repaired: python_literal; final_label_repaired: '4 in 6 weeks' -> 'no seizure frequency reference' |
| 5873 | multiple per day | multiple per week | yes | json_dialect_repaired: python_literal |
| 5921 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 5954 | 2 per week | 2 per week | yes | json_dialect_repaired: python_literal |
| 5961 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 5974 | seizure free for multiple year | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5977 | multiple per 6 week | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per 6 weeks' -> 'multiple per 6 week'; evidence_not_exact_substring |
| 5995 | 3 per 7 month | 1 per 3 months | yes | json_dialect_repaired: python_literal; final_label_repaired: 'infrequent' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 7 month' |
| 5996 | 2 to 3 per week | unknown | no | json_dialect_repaired: python_literal |
| 6026 | 3 per 2 month | 3 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 events per 2 months' -> '3 per 2 month' |
| 6029 | unknown | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (clustering)' -> 'unknown'; evidence_not_exact_substring |
| 6034 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 6065 | 12 per 3 month | 5 per month | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '12 per 3 month' |
| 6077 | seizure free for 8 month | unknown | no | json_dialect_repaired: python_literal |
| 6087 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 6094 | 4 per 2 month | 3 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 recent events (3 in September, 2 in early October)' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '4 per 2 month' |
| 6112 | 3 to 5 per month | 3 to 5 per month | yes | json_dialect_repaired: python_literal |
| 6131 | 1 per 5 month | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 12 month' -> '1 per 5 month'; evidence_not_exact_substring |
| 6137 | 1 per 2 to 3 week | 1 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2-3 weeks' -> '1 per 2 to 3 week' |
| 6153 | 9 per 4 week | 9 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '9 seizures in 4 weeks' -> '9 per 4 week' |
| 6180 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 6192 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 6204 | 1 to 2 per week | 2 per month | no | json_dialect_repaired: python_literal |
| 6209 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'daily' -> 'multiple per day' |
| 6244 | 2 per week | unknown | no | json_dialect_repaired: python_literal |
| 6251 | 1 per month | 1 per 1 to 2 month | no | json_dialect_repaired: python_literal |
| 6273 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 6319 | 1 per week | 1 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'roughly weekly' -> '1 per week' |
| 6321 | 2 per year | unknown | no | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 6331 | 2 per 6 week | 2 per 6 weeks | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 6 weeks' -> '2 per 6 week' |
| 6358 | 1 per 16 month | seizure free for 15 to 16 months | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 6 month' -> '1 per 16 month'; evidence_not_exact_substring |
| 6368 | 1 per 1 to 2 week | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: '1 per 1-2 weeks' -> '1 per 1 to 2 week' |
| 6395 | 1 to 2 per month | 1 to 2 per month | yes | json_dialect_repaired: python_literal |
| 6501 | unknown | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'clusters every few weeks' -> 'unknown'; evidence_not_exact_substring |
| 6509 | 2 per 2 week | 1 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 2 weeks' -> '2 per 2 week' |
| 6571 | 1 per 4 month | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since June 2025' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 4 month' |
| 6607 | unknown | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (clusters) and occasional prolonged events' -> 'unknown' |
| 6684 | 3 per 4 month | 3 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 6701 | no seizure frequency reference | 4 per 3 week | no | json_dialect_repaired: python_literal; final_label_repaired: '4 in 3 weeks' -> 'no seizure frequency reference' |
| 6738 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 6-8 weeks' -> '1 per 6 to 8 week' |
| 6852 | 4 to 6 per month | 4 to 6 per month | yes | json_dialect_repaired: python_literal |
| 6889 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several times per week' -> 'multiple per week'; evidence_not_exact_substring |
| 6952 | 2 per week | 2 per week | yes | json_dialect_repaired: python_literal |
| 6967 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 6987 |  | unknown | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 7093 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 7126 | multiple per week | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (peri-mid-cycle)' -> 'multiple per week' |
| 7141 | multiple per week | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 7167 | unknown | 1 cluster per 2 weeks, 2 to 4 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: '3 clusters per 6 weeks (2-4 seizures per cluster)' -> 'unknown' |
| 7168 | multiple per week | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 7192 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several times per week' -> 'multiple per week' |
| 7195 | 1 per month | unknown | no | json_dialect_repaired: python_literal |
| 7196 | 6 per 6 week | 1 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: '6 per 6 weeks' -> '6 per 6 week' |
| 7198 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 in August and September 2025' -> 'no seizure frequency reference' |
| 7275 | 3 per 12 week | 1 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 in 3 months' -> '3 per 12 week' |
| 7290 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 7316 | 1 to 2 per month | 1 to 2 per month | yes | json_dialect_repaired: python_literal |
| 7389 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 7392 | 2 to 4 per week | 2 to 4 per week | yes | json_dialect_repaired: python_literal |
| 7401 | multiple per week | 2 cluster per 6 week, 1 to 2 per cluster | no | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 7409 | multiple per week | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'most weeks' -> 'multiple per week' |
| 7455 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 7475 | 2 per 4 month | 2 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 6 months' -> '2 per 6 month'; final_label_repaired: '2 per 6 month' -> '2 per 4 month'; evidence_not_exact_substring |
| 7491 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 7506 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 7573 | 1 per 2 week | 1 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 7581 | 2 to 3 per week | 2 to 3 per week | yes | json_dialect_repaired: python_literal |
| 7615 | 2 per 10 month | 3 to 7 per month | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '2 per 10 month'; evidence_not_exact_substring |
| 7650 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 7738 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 7785 | seizure free for 12 month | seizure free for 12 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 7818 | seizure free for multiple year | seizure free for 2 years | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since August 2023' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 7834 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7859 | seizure free for multiple year | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for several weeks' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 7872 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7911 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7961 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 8002 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 6-8 weeks' -> '1 per 6 to 8 week' |
| 8006 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 8079 | seizure free for 6 month | seizure free for 18 month | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 8089 | seizure free for multiple year | seizure free for 16 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for >1 year' -> 'seizure free for multiple year' |
| 8124 | seizure free for 13 month | seizure free for 13 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 13 months' -> 'seizure free for 13 month' |
| 8144 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8145 | seizure free for multiple year | seizure free for 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8160 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8180 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since April 2025' -> 'seizure free for multiple year' |
| 8188 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8203 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 8224 | seizure free for 3 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8235 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8264 | seizure free for 4 month | seizure free for 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 8265 | seizure free for 6 month | seizure free for 6 month | yes | json_dialect_repaired: python_literal |
| 8354 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 8355 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 12+ months' -> 'seizure free for multiple year' |
| 8400 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 8419 | multiple per week | 1 to 2 per week | no | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 8474 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 8512 | seizure free for 3 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8564 | seizure free for 6 month | seizure free for 6 month | yes | json_dialect_repaired: python_literal |
| 8577 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8581 | 1 per 4 month | seizure free for multiple month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since June 2025' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 4 month'; evidence_not_exact_substring |
| 8593 | seizure free for 14 month | seizure free for 14 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 8596 | seizure free for 11 month | seizure free for 11 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 11 months' -> 'seizure free for 11 month' |
| 8674 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 8724 | seizure free for 3 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; evidence_not_exact_substring |
| 8730 | seizure free for 6 month | seizure free for 6 month | yes | json_dialect_repaired: python_literal |
| 8794 | seizure free for 6 month | seizure free for 6 month | yes | json_dialect_repaired: python_literal |
| 8802 | seizure free for multiple year | seizure free for 12 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 8805 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 8808 | 0 per 10 month | seizure free for 10 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 10 months' -> '0 per 10 month'; evidence_not_exact_substring |
| 8820 | seizure free for multiple year | seizure free for 7 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8835 | seizure free for multiple year | seizure free for 10 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 8854 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 8893 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 8922 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8924 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8938 | seizure free for 6 month | seizure free for 10 month | yes | json_dialect_repaired: python_literal |
| 8949 | seizure free for 6 month | seizure free for 6 month | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 8969 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 9002 | seizure free for 6 month | 7 per year | no | json_dialect_repaired: python_literal |
| 9063 | seizure free for multiple year | seizure free for 8 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9103 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'infrequent' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 9163 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9190 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9215 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 9238 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9250 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 9259 | seizure free for 1 year | seizure free for 1 year | yes | json_dialect_repaired: python_literal |
| 9287 | 3 to 5 per week | 3 to 5 per week | yes | json_dialect_repaired: python_literal |
| 9299 | 5 per week | 5 per week | yes | json_dialect_repaired: python_literal |
| 9300 | 2 to 4 per week | 2 to 4 per week | yes | json_dialect_repaired: python_literal |
| 9344 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per day' -> 'multiple per day'; evidence_not_exact_substring |
| 9365 | 1 per 2 day | 1 per 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 9368 | 1 per 2 day | 1 per 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'once every two days' -> '1 per 2 day' |
| 9391 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 9397 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 9449 | 8 per 9 month | 4 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per month' -> '4 per 6 month'; final_label_repaired: '4 per 6 month' -> '8 per 9 month' |
| 9462 | 14 per 22 month | 7 per 11 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '8 per year' -> '7 per 11 month'; final_label_repaired: '7 per 11 month' -> '14 per 22 month' |
| 9496 | 12 per 24 month | 6 per 12 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'low frequency' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '12 per 24 month' |
| 9547 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'infrequent' -> 'no seizure frequency reference' |
| 9588 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 9704 | multiple per day | unknown | yes | json_dialect_repaired: python_literal |
| 9815 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per hour' -> 'multiple per day' |
| 9877 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 9879 | multiple per week | unknown | yes | json_dialect_repaired: python_literal |
| 9888 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 9912 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'sporadic' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 9937 | multiple per week | 1 cluster per month, multiple per cluster | no | json_dialect_repaired: python_literal |
| 9943 | 1 per 4 to 5 week | 1 cluster per 4 to 5 week, multiple per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 per 4 to 5 week' |
| 9955 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per month' -> '1 cluster per month, multiple per cluster' |
| 10003 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'weekly' -> '1 cluster per week, multiple per cluster' |
| 10047 | 2 cluster per 3 month, multiple per cluster | 2 cluster per 3 month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 clusters per quarter' -> '2 cluster per 3 month, multiple per cluster' |
| 10063 | 3 cluster per 3 month, multiple per cluster | 3 cluster per 3 month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per quarter' -> '3 cluster per 3 month, multiple per cluster' |
| 10097 | 3 per month | 3 cluster per month, multiple per cluster | no | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 10147 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 10183 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 10189 | multiple per week | unknown, 3 to 4 per cluster | yes | json_dialect_repaired: python_literal |
| 10200 | no seizure frequency reference | unknown, 2 to 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 4 per cluster' -> 'no seizure frequency reference' |
| 10237 | unknown | 4 cluster per month, multiple per cluster | no | json_dialect_repaired: python_literal |
| 10245 | 2 per 6 month | 3 cluster per month, multiple per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '2 per 6 month' |
| 10260 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 10264 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 10266 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 10268 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 10371 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 10383 | 1 cluster per week, 5 per cluster | 1 cluster per week, 5 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 per week' -> '1 cluster per week, 5 per cluster' |
| 10386 | 1 cluster per week, 2 to 3 per cluster | 1 cluster per week, 2 to 3 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'weekly, 2 to 3 per cluster' -> '1 cluster per week, 2 to 3 per cluster' |
| 10434 | multiple per week | multiple cluster per week, 2 to 3 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'several per week' -> 'multiple per week' |
| 10481 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10487 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10509 | unknown | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (clusters)' -> 'unknown'; evidence_not_exact_substring |
| 10517 | 3 to 4 cluster per week, multiple per cluster | 3 to 4 cluster per week, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '3 to 4 cluster per week, multiple per cluster' |
| 10542 | 2 to 4 per 3 month | unknown, 2 to 4 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '2 to 4 per 3 month'; evidence_not_exact_substring |
| 10578 | unknown | unknown, 3 to 4 per cluster | yes | json_dialect_repaired: python_literal |
| 10583 | multiple per week | unknown, 2 to 3 per cluster | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 10594 | unknown | unknown, 2 per cluster | yes | json_dialect_repaired: python_literal |
| 10618 | unknown | unknown, 4 to 6 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '4-6 per cluster, occurring on some days with several days between clusters' -> 'unknown' |
| 10629 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 10630 | unknown | multiple cluster per 2 week, 5 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple clusters per fortnight, ~5 spells per cluster' -> 'unknown'; evidence_not_exact_substring |
| 10673 | multiple per month | 1 cluster per month, multiple per cluster | no | json_dialect_repaired: python_literal |
| 10677 | 1 per month | 1 cluster per month, multiple per cluster | no | json_dialect_repaired: python_literal |
| 10753 | multiple per month | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'occasional' -> 'multiple per month'; evidence_not_exact_substring |
| 10807 | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 cluster days per month' -> '2 cluster per month, multiple per cluster' |
| 10829 | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 clusters per month' -> '2 cluster per month, multiple per cluster' |
| 10862 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10865 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10873 | 1 cluster per week, 6 per cluster | 1 cluster per week, 6 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (cluster frequency)' -> '1 cluster per week, 6 per cluster' |
| 10894 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 per week' -> '1 cluster per week, 4 per cluster' |
| 10896 | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'weekly clusters of 3-4 seizures' -> '1 cluster per week, 3 to 4 per cluster' |
| 10902 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 cluster per week, 4 per cluster' |
| 10933 | 2 to 3 cluster per month, 5 per cluster | 2 to 3 cluster per month, 5 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '10 to 15 per month' -> '2 to 3 cluster per month, 5 per cluster' |
| 10942 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 clusters per month, approx 10 seizures total' -> '2 cluster per month, 5 per cluster' |
| 10965 | 2 to 3 per week | 2 cluster per month, 4 to 5 per cluster | yes | json_dialect_repaired: python_literal |
| 10967 | multiple per week | 3 cluster per month, 4 to 5 per cluster | no | json_dialect_repaired: python_literal |
| 10984 | 3 cluster per month, 3 to 4 per cluster | 3 cluster per month, 3 to 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per month' -> '3 cluster per month, 3 to 4 per cluster' |
| 10996 | 1 to 2 cluster per month, 4 per cluster | 1 to 2 cluster per month, 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 to 2 per month' -> '1 to 2 cluster per month, 4 per cluster' |
| 11002 | 2 to 4 cluster per month, 5 per cluster | 2 to 4 cluster per month, 5 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 4 per month' -> '2 to 4 cluster per month, 5 per cluster' |
| 11035 | 1 cluster per 3 month, 1 per cluster | 1 cluster per 3 month, 1 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per quarter' -> '1 cluster per 3 month, 1 per cluster'; evidence_not_exact_substring |
| 11109 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (with clusters of 5+)' -> '2 cluster per month, 5 per cluster' |
| 11118 | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 clusters per month, ~6 seizures per cluster day' -> '2 cluster per month, 6 per cluster' |
| 11131 | 2 cluster per month, 3 to 4 per cluster | 2 cluster per month, 3 to 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '2 cluster per month, 3 to 4 per cluster' |
| 11197 | 1 cluster per month, 4 to 6 per cluster | 1 cluster per month, 4 to 6 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per month with 4 to 6 seizures per cluster' -> '1 cluster per month, 4 to 6 per cluster' |
| 11216 | seizure free for multiple year | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 11254 | seizure free for multiple year | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since 31-May' -> 'seizure free for multiple year' |
| 11259 | seizure free for multiple year | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 11262 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 11272 | seizure free for multiple year | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 11282 | 1 per 4 month | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 4 month' |
| 11337 | 1 per 8 week | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: '1 in 8 weeks' -> '1 per 8 week'; evidence_not_exact_substring |
| 11350 | multiple per week | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 11380 | multiple per day | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> 'multiple per day'; evidence_not_exact_substring |
| 11389 | 1 per year | unknown | no | json_dialect_repaired: python_literal |
| 11400 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 11405 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11408 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11409 | unknown | no seizure frequency reference | yes | json_dialect_repaired: python_literal; final_label_repaired: 'occasional clusters' -> 'unknown' |
| 11411 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11434 | unknown | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11463 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11562 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 11585 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 11606 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 11614 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11632 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11640 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 11658 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11681 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11706 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11711 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 11728 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11734 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11737 | seizure free for multiple year | no seizure frequency reference | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 11752 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 11756 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 11763 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11804 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 11824 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11841 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11852 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 12036 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal |
| 12041 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 12046 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal |
| 12051 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal |
| 12111 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several times per week' -> 'multiple per week' |
| 12127 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per week' -> 'multiple per week' |
| 12130 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per week' -> 'multiple per week' |
| 12139 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per week' -> 'multiple per week' |
| 12145 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per week' -> 'multiple per week' |
| 12192 | multiple per day | 1 per day | no | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 12218 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'daily' -> '1 per day' |
| 12236 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'daily' -> '1 per day' |
| 12246 | 1 to 2 per day | 1 to 2 per day | yes | json_dialect_repaired: python_literal |
| 12314 | multiple per week | 3 per week | no | json_dialect_repaired: python_literal |
| 12366 | 4 per day | 4 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple seizure types with high frequency (simple partial 4/day)' -> '4 per day' |
| 12378 | multiple per day | 4 per day | no | json_dialect_repaired: python_literal |
| 12383 | multiple per day | 4 per day | no | json_dialect_repaired: python_literal |
| 12403 | multiple per day | 2 to 3 per day | no | json_dialect_repaired: python_literal |
| 12412 | multiple per day | 2 per day | no | json_dialect_repaired: python_literal |
| 12422 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day' |
| 12438 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'nightly' -> '1 per day' |
| 12456 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'nightly' -> '1 per day' |
| 12460 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'nightly' -> '1 per day' |
| 12468 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'nightly' -> '1 per day' |
| 12484 | 1 cluster per month, multiple per cluster | 3 to 4 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 cluster per month, multiple per cluster'; evidence_not_exact_substring |
| 12502 | 1 cluster per month, multiple per cluster | 4 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 cluster per month, multiple per cluster'; evidence_not_exact_substring |
| 12506 | multiple per day | 4 per day | no | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 12537 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day'; evidence_not_exact_substring |
| 12548 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'daily' -> '1 per day' |
| 12551 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'daily' -> '1 per day' |
| 12556 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day'; evidence_not_exact_substring |
| 12562 | 3 to 4 per 6 month | 1 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '3 to 4 per 6 month'; evidence_not_exact_substring |
| 12573 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'daily' -> '1 per day' |
| 12584 | 1 per 3 month | 1 per week | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 per 3 month'; evidence_not_exact_substring |
| 12641 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day'; evidence_not_exact_substring |
| 12665 | 1 to 2 per 6 month | 1 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple seizure types present (daily absences, 1-2 GTCS/month, focal/non-motor q3-4wks)' -> '1 to 2 per 6 month'; evidence_not_exact_substring |
| 12667 | 1 per 3 to 4 week | 1 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 per 3 to 4 week'; evidence_not_exact_substring |
| 12676 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'daily' -> '1 per day'; evidence_not_exact_substring |
| 12679 | 1 to 2 per 6 month | 1 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple seizure types present: 1-2 GTCs/month, daily absences, focal non-motor q3-4wks, drop attacks' -> '1 to 2 per 6 month'; evidence_not_exact_substring |
| 12749 | 2 per month | 3 to 4 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '2 per month'; evidence_not_exact_substring |
| 12751 | 2 per month | 4 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '2 per month'; evidence_not_exact_substring |
| 12788 | 6 per 4 month | 6 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '6 per year' -> '6 per 4 month' |
| 12810 | 5 per 2 month | 5 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '7 per year' -> '5 per 2 month' |
| 12823 | 9 per month | 9 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '9 per year (GTC), ~1-2 per month (focal)' -> '9 per month' |
| 12827 | 5 per 5 month | 5 per 5 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 per year' -> '5 per 5 month' |
| 12835 | 4 per month | 4 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 per year' -> '4 per month' |
| 12877 | 10 per 4 month | 10 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '10 per year' -> '10 per 4 month' |
| 12882 | 7 per 4 month | 7 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '7 per year (GTC), 1-2 per month (focal)' -> '7 per 4 month' |
| 12901 | 8 per 5 month | 8 per 5 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '8 per year' -> '8 per 5 month' |
| 12949 | 9 per 6 month | 9 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '9 per year' -> '9 per 6 month' |
| 12950 | 7 per 3 month | 7 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '7 per 3 month'; evidence_not_exact_substring |
| 12963 | seizure free for multiple year | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 10 weeks' -> 'seizure free for multiple year' |
| 12979 | 3 per 4 month | 3 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per year' -> '3 per 4 month' |
| 13008 | 4 per month | 4 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 per year' -> '4 per month' |
| 13011 | 3 per 4 month | 3 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per year' -> '3 per 4 month' |
| 13051 | seizure free for multiple year | 2 per 8 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since last event' -> 'seizure free for multiple year' |
| 13058 | multiple per week | 2 per 7 month | no | json_dialect_repaired: python_literal |
| 13114 | 2 per 1 year | 1 per year | no | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per week' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 1 year' |
| 13122 | 3 per 1 year | 3 per year | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per week' -> 'unknown'; final_label_repaired: 'unknown' -> '3 per 1 year'; evidence_not_exact_substring |
| 13149 | seizure free for multiple year | 3 per year | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year' |
| 13178 | 1 per 6 month | 1 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 6 months' -> '1 per 6 month' |
| 13190 | unknown | 1 per 5 month | no | json_dialect_repaired: python_literal |
| 13209 | 1 per 4 to 5 week | 1 per 8 month | no | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per month' -> '1 per 4 to 5 week'; evidence_not_exact_substring |
| 13267 | multiple per week | 2 per 5 month | no | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 13290 | 2 per 2 week | 4 per 6 month | no | json_dialect_repaired: python_literal; final_label_repaired: '2 per 2 weeks' -> '2 per 2 week' |
| 13327 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13336 | seizure free for 1.5 year | seizure free for 1.5 year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 1.5 years' -> 'seizure free for 1.5 year' |
| 13349 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13385 | seizure free for 18 month | seizure free for 1.5 year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 18 months' -> 'seizure free for 18 month' |
| 13450 | seizure free for 1 year | seizure free for 1 year | yes | json_dialect_repaired: python_literal |
| 13471 | seizure free for 5 year | seizure free for 5 year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 5 years' -> 'seizure free for 5 year' |
| 13478 | seizure free for 1 year | seizure free for 1 year | yes | json_dialect_repaired: python_literal |
| 13485 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for over several years' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13487 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for over several years' -> 'seizure free for multiple year' |
| 13513 | seizure free for 18 month | seizure free for 1.5 year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 18 months' -> 'seizure free for 18 month'; evidence_not_exact_substring |
| 13574 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13595 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13598 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13608 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13627 | 20 per 3 month | 64 per 12 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '64 per 12 month'; final_label_repaired: '64 per 12 month' -> '20 per 3 month' |
| 13635 | 30 per 5 month | 47 per 7 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '47 per 7 month'; final_label_repaired: '47 per 7 month' -> '30 per 5 month' |
| 13711 | 28 per 6 month | 76 per 12 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '28 per 6 month' |
| 13721 | 26 per 6 month | 77 per 12 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '77 per 12 month'; final_label_repaired: '77 per 12 month' -> '26 per 6 month' |
| 13732 | 16 per 3 month | 52 per 8 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> 'multiple per day'; final_label_repaired: 'multiple per day' -> '16 per 3 month' |
| 13843 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13858 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 13889 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 13893 | seizure free for multiple year | 2 per year | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 13922 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 since medication increase' -> 'no seizure frequency reference' |
| 14002 | multiple per day | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> 'multiple per day'; evidence_not_exact_substring |
| 14025 | 2 per 6 week | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: '2 per 6 weeks' -> '2 per 6 week' |
| 14029 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 14040 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 14076 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 14092 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 since last review' -> 'no seizure frequency reference' |
| 14096 | 5 per month | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: '5' -> '5 per month' |
| 14137 | 3 to 4 per month | unknown | no | json_dialect_repaired: python_literal |
| 14146 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 total since beginning Clobazam' -> 'no seizure frequency reference' |
| 14187 | 2 to 3 per 1 month | 2 to 3 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 to 3 per 1 month' |
| 14214 | seizure free for multiple year | 2 to 4 per month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 14250 | seizure free for multiple year | 2 per month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 14282 | seizure free for multiple year | multiple per month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 14284 | 2 to 3 per 1 month | 2 to 3 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 to 3 per 1 month' |
| 14317 | 4 per 2 month | 4 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '4 per 2 month'; evidence_not_exact_substring |
| 14332 | 5 per 2 month | 5 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 2 month' -> '5 per 2 month'; evidence_not_exact_substring |
| 14335 | 3 to 4 per 8 week | 3 to 4 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 8 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 to 4 per 8 week'; evidence_not_exact_substring |
| 14383 | 3 to 4 per 3 month | 3 to 4 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 to 4 per 3 month'; evidence_not_exact_substring |
| 14454 | 2 per 1 month | 2 per 2 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 1 month'; evidence_not_exact_substring |
| 14524 | unknown | 2 per 6 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'occasional clusters' -> 'unknown' |
| 14530 | 2 per 2 month | 2 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since May 2019' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 2 month'; evidence_not_exact_substring |
| 14540 | 2 per 8 month | 2 per 8 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 8 month' |
| 14562 | 3 per 6 month | 3 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since July 2021' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 per 6 month' |
| 14567 | 3 per 3 month | 3 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since January 2018' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 per 3 month'; evidence_not_exact_substring |
| 14581 | 2 per 3 month | 2 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 3 month' |
| 14587 | 2 per 3 month | 2 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 3 months' -> '2 per 3 month' |
| 14592 | multiple per week | 3 per 5 month | no | json_dialect_repaired: python_literal |
| 14611 | 2 per 4 month | 2 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 4 month' |
| 14628 | 2 per 2 month | 2 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 events in recent months' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '6 per 3 month'; final_label_repaired: '6 per 3 month' -> '2 per 2 month'; evidence_not_exact_substring |
| 14635 | 5 per 5 month | 5 per 4 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '5 per 5 month' |
| 14645 | 2 per 6 month | 2 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 6 month'; evidence_not_exact_substring |
| 14662 | 3 per 4 month | 3 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '3 per 4 month'; evidence_not_exact_substring |
| 14672 | 3 per 8 month | 3 per 8 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 per 8 month' |
| 14706 | 2 per 5 month | 2 per 5 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 5 months' -> '2 per 5 month' |
| 14765 | 1 per 1 month | 1 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month' |
| 14806 | 1 per 2 month | 1 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 1 month' -> '1 per 2 month' |
| 14810 | 1 per 1 month | 1 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 4 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14821 | 1 per 1 month | 1 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since 24 Jul' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14872 | 1 per 1 month | 1 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14943 | 1 per 3 month | 1 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since 21 Feb' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month' |
| 14949 | 1 per 1 month | 1 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14965 | 1 per 3 month | 1 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since 20/May' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month' |
| 14973 | 1 per 1 month | 1 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 6 month' -> '1 per 1 month' |
| 15004 | 1 per 3 month | 1 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month' |
| 15012 | 1 per 2 month | 1 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 2 month' |
| 15021 | 1 per 3 month | 1 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 3 months' -> '1 per 3 month' |
| 15029 | 1 per 3 month | 1 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month' |
| 15094 | 3 per 13 month | 4 per 13 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 since Apr/2022' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 13 month' |
| 15108 |  | 3 to 4 per 15 month | no | not_run; AdapterParseError: Adapter JSONAdapter failed to parse the LM response. 

LM Response: {
        "applies_to": "tonic-clonic seizure",
        "assertion_status": "historical",
        "event_id": "e1",
        "evidence": "Last tonic-clonic seizure was in 1 - 2024",
        "kind": "last_event_only",
        "notes": null,
        "raw_value": "1 - 2024",
        "temporality": "historical",
        "time_window": "historical"
      } 

Expected to find output fields in the LM response: [structured_json] 

Actual output fields parsed from the LM response: [] 

; evidence_not_exact_substring |
| 15127 | 4 per 13 month | 5 per 13 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 events since last major seizure' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '4 per 13 month' |
| 15129 | 4 per 15 month | 4 per 15 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 since 3/2015' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '4 per 15 month' |
| 15141 | 3 to 4 per 15 month | 4 to 5 per 15 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 to 4 per month' -> '3 to 4 per 15 month' |
| 15168 | multiple per month | multiple per 15 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'occasional' -> 'multiple per month'; evidence_not_exact_substring |
| 15193 | unknown | multiple per 13 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown frequency (from time to time)' -> 'unknown' |
| 15242 | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'occasional clusters per week/month' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 15 month, multiple per cluster' |
| 15262 | multiple cluster per 13 month, multiple per cluster | multiple cluster per 13 month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 13 month, multiple per cluster' |
| 15267 | 3 per year | 3 per 14 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per year (historical context) / current stability with rare jerks' -> '3 per year' |
| 15306 | 2 to 3 per 15 month | 2 to 3 per 15 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 3 per month' -> '2 to 3 per 15 month' |
| 15317 | 2 to 3 per 15 month | 2 to 3 per 15 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 3 per month' -> '2 to 3 per 15 month' |
| 15376 | 1 cluster per 2 week, 4 to 6 per cluster | 1 cluster per 2 week, 4 to 6 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per day (often 4-6)' -> '1 cluster per 2 week, 4 to 6 per cluster' |
| 15404 | 3 to 4 per day | 1 cluster per 4 month, 3 to 4 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'clusters of 3-4 seizures per day' -> '3 to 4 per day' |
| 15429 | 4 per 2 month | 1 cluster per 2 month, 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 per day (in clusters)' -> 'unknown'; final_label_repaired: 'unknown' -> '4 per 2 month' |
| 15431 | seizure free for 3 month | 1 cluster per 4 month, 5 per cluster | no | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 15442 | 1 cluster per 4 day, 2 per cluster | 1 cluster per 4 day, 2 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 cluster per 4 day, 2 per cluster' |
| 15470 | multiple per day | 1 cluster per 5 day, multiple per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> 'multiple per day' |
| 15479 | 1 cluster per 4 to 5 day, 2 per cluster | 1 cluster per 4 to 5 day, 2 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (clustered)' -> '1 cluster per 4 to 5 day, 2 per cluster' |
| 15497 | 1 cluster per 5 day, 5 per cluster | 1 cluster per 4 to 5 day, 5 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 cluster per 5 day, 5 per cluster' |
| 15503 | 1 cluster per 5 day, 3 to 4 per cluster | 1 cluster per 5 day, 3 to 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (clusters of 3-4 daily)' -> '1 cluster per 5 day, 3 to 4 per cluster' |
| 15513 | seizure free for multiple year | 1 cluster per 4 to 5 day, 2 to 3 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 10 days' -> 'seizure free for multiple year' |
| 15519 | 1 cluster per 4 day, 3 per cluster | 1 cluster per 4 day, 3 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per day (in clusters)' -> '1 cluster per 4 day, 3 per cluster' |
| 15529 | 1 cluster per 3 day, 4 per cluster | 1 cluster per 3 day, 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week (clusters of 4)' -> '1 cluster per 3 day, 4 per cluster' |
| 15593 | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 4 per cluster' -> '1 cluster per 5 day, 2 to 4 per cluster' |
| 15614 | 3 per week | 3 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 times per week' -> '3 per week' |
| 15628 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several times per week' -> 'multiple per week' |
| 15639 | 2 per week | 2 per week | yes | json_dialect_repaired: python_literal |
| 15642 | 2 to 4 per week | 2 to 4 per week | yes | json_dialect_repaired: python_literal |
| 15650 | 3 to 4 per day | 3 to 4 per day | yes | json_dialect_repaired: python_literal |
| 15672 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'almost daily' -> '1 per day' |
| 15697 | multiple per week | 1 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'almost 1 per day' -> 'multiple per week'; evidence_not_exact_substring |
| 15715 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'almost 1 per day' -> '1 per day' |
| 15745 | 2 to 3 per week | 2 to 3 per week | yes | json_dialect_repaired: python_literal |
| 15766 | 4 per week | 4 per week | yes | json_dialect_repaired: python_literal |
| 15768 | 2 to 3 per week | 2 to 3 per week | yes | json_dialect_repaired: python_literal |
| 15771 | 3 per week | 3 per week | yes | json_dialect_repaired: python_literal |
| 15772 | multiple per week | 2 per week | no | json_dialect_repaired: python_literal |
| 15774 | 2 per week | 2 per week | yes | json_dialect_repaired: python_literal |
| 15783 | 2 to 3 per week | 2 to 3 per week | yes | json_dialect_repaired: python_literal |
| 15802 | 7 per week | 7 per week | yes | json_dialect_repaired: python_literal |
| 15831 | 2 to 4 per day | 2 to 4 per day | yes | json_dialect_repaired: python_literal |
| 15834 | 5 per week | 5 per week | yes | json_dialect_repaired: python_literal |
| 15964 | 11 per 3 month | 11 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '6 per month' -> '11 per 3 month' |
| 15965 | 13 per 2 month | 13 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '6 per month' -> '13 per 2 month'; evidence_not_exact_substring |
| 15966 | 5 per 3 month | 5 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 3 per month' -> '5 per 3 month'; evidence_not_exact_substring |
| 15982 | 9 per 2 month | 9 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '8 per month' -> '9 per 2 month' |
| 15986 | 11 per 3 month | 11 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per month' -> '11 per 3 month'; evidence_not_exact_substring |
| 15992 | 7 per 2 month | 7 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per month' -> '7 per 2 month' |
| 15997 | 10 per 3 month | 10 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '6 per month' -> '10 per 3 month' |
| 16021 | 9 per 3 month | 9 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 per month' -> '9 per 3 month' |
| 16041 | 9 per 3 month | 9 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 per month' -> '9 per 3 month' |
| 16084 | 8 per 4 month | 8 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 1 month' -> '8 per 4 month'; evidence_not_exact_substring |
| 16091 | 1 per 2 month | 3 per 3 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per month' -> '3 per 3 month'; final_label_repaired: '3 per 3 month' -> '1 per 2 month' |
| 16097 | 17 per 4 month | 17 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '17 per 4 month' |
| 16107 | 8 per 3 month | 8 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 per month' -> '8 per 3 month' |
| 16108 | 13 per 4 month | 12 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '12 per 4 month'; final_label_repaired: '12 per 4 month' -> '13 per 4 month' |
| 16132 | 13 per 2 month | 15 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '13 per 2 month' |
| 16133 | 18 per 4 month | 18 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '18 per 4 month' |
| 16161 | 15 per 3 month | 18 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '7 per month' -> '18 per 3 month'; final_label_repaired: '18 per 3 month' -> '15 per 3 month' |
| 16162 | 11 per 3 month | 11 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '6 per month' -> '11 per 3 month' |
| 16181 | 15 per 4 month | 15 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '15 per 4 month' |
| 16195 | 10 per 3 month | 16 per 4 month | no | json_dialect_repaired: python_literal; final_label_repaired: '6 per month' -> '10 per 3 month' |
| 16203 | 8 per 2 month | 9 per 3 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '8 per 2 month' |
| 16204 | 4 per 2 month | 5 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 seizures in 3 months (Jul-Sep)' -> '5 per 3 month'; final_label_repaired: '5 per 3 month' -> '4 per 2 month'; evidence_not_exact_substring |
| 16220 | 11 per 2 month | 11 per 4 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for current month' -> '11 per 4 month'; final_label_repaired: '11 per 4 month' -> '11 per 2 month' |
| 16324 | 7 per 2 month | 10 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '7 per 2 month' |
| 16335 | 7 per 3 month | 7 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '7 per 3 month' |
| 16356 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: '1 cluster per 4 days' -> '1 per 4 day' |
| 16394 | 1 per 2 to 4 day | 1 per 2 to 4 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per 2 to 4 days' -> '1 per 2 to 4 day' |
| 16408 | 1 per 3 day | 1 per 3 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per 3 day' |
| 16429 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per 2 to 3 day' |
| 16432 | 1 per 2 day | 1 per 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2 days (escalating to daily)' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per 2 day' |
| 16450 | 1 per multiple day | 1 per multiple day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per multiple day' |
| 16529 | 1 per 5 day | 1 per 5 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster every 5 days' -> '1 per 5 day' |
| 16557 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'every 2 to 3 days' -> '1 per 2 to 3 day' |
| 16574 | multiple per week | 1 per 4 day | no | json_dialect_repaired: python_literal |
| 16590 | 1 per 4 to 5 day | 1 per 4 to 5 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster every 4-5 days' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 4 to 5 day' |
| 16618 | multiple per week | 1 per 5 day | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week to daily' -> 'multiple per week' |
| 16645 | 5 per 4 month | 5 per 7 month | no | json_dialect_repaired: python_literal; final_label_repaired: '1 per month' -> '5 per 4 month' |
| 16674 | 6 per 4 month | 7 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'fewer events' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '6 per 4 month'; evidence_not_exact_substring |
| 16685 | 10 per 3 month | 10 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '9 per 2 month'; final_label_repaired: '9 per 2 month' -> '10 per 3 month'; evidence_not_exact_substring |
| 16697 | 2 per 3 month | 3 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 seizures in 6 months' -> '3 per 6 month'; final_label_repaired: '3 per 6 month' -> '2 per 3 month'; evidence_not_exact_substring |
| 16704 | 9 per 6 month | 9 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '7 per month' -> '9 per 6 month' |
| 16714 | 5 per 4 month | 5 per 6 month | no | json_dialect_repaired: python_literal; final_label_repaired: '3 events in 6 months (Nov, Feb, Apr)' -> '3 per 6 month'; final_label_repaired: '3 per 6 month' -> '5 per 4 month'; evidence_not_exact_substring |
| 16717 | 5 per 6 month | 5 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 seizures in 6 months' -> '4 per 6 month'; final_label_repaired: '4 per 6 month' -> '5 per 6 month' |
| 16719 | 7 per 4 month | 7 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '7 per 4 month' |
| 16728 | 4 per 4 month | 4 per 6 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '4 per 4 month'; evidence_not_exact_substring |
| 16750 | 6 per 7 month | 6 per 7 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since late August' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '6 per 7 month' |
| 16757 | 13 per 6 month | 13 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '13 per 6 month'; evidence_not_exact_substring |
| 16758 | 8 per 4 month | 9 per 5 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per month' -> '8 per 4 month' |
| 16772 | 8 per 2 month | 9 per 5 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 6 month' -> '8 per 2 month'; evidence_not_exact_substring |
| 16774 | 19 per 4 month | 19 per 7 month | no | json_dialect_repaired: python_literal; final_label_repaired: '3 per month' -> '19 per 4 month' |
| 16780 | 3 per 7 month | 3 per 7 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '3 per 7 month'; evidence_not_exact_substring |
| 16824 | 11 per 3 month | 11 per 5 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per month' -> '11 per 3 month' |
| 16833 | 8 per 6 month | 8 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per month' -> '8 per 6 month' |
| 16839 | 9 per 3 month | 9 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'variable frequency (sometimes)' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '9 per 3 month' |
| 16867 | 5 per 4 month | 6 per 7 month | no | json_dialect_repaired: python_literal; final_label_repaired: '6 seizures in the last 6 months' -> '6 per 6 month'; final_label_repaired: '6 per 6 month' -> '5 per 4 month' |
| 16907 | 8 per 4 month | 9 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per month' -> '8 per 4 month'; evidence_not_exact_substring |
| 16938 | 1 per 2 month | 2 per week | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 per 2 month' |
| 16947 | 1 per 2 month | 2 per week | no | json_dialect_repaired: python_literal; final_label_repaired: '4 per 2 months' -> '1 per 2 month' |
| 16961 |  | 2 per week | no | schema_validation_error: Field required; evidence_not_exact_substring |
| 16983 | 2 to 3 per week | 2 to 3 per week | yes | json_dialect_repaired: python_literal |
| 16990 | 4 to 5 per week | 4 to 5 per week | yes | json_dialect_repaired: python_literal |
| 17001 | 5 per week | 5 per week | yes | json_dialect_repaired: python_literal |
| 17003 | 3 to 4 per month | 3 to 4 per month | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 17110 | 4 to 5 per week | 4 to 5 cluster per week, multiple per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: '4 to 5 days per week' -> '4 to 5 per week' |
| 17135 | 1 cluster per month, multiple per cluster | 5 cluster per month, multiple per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: '5 days per month' -> '1 cluster per month, multiple per cluster' |
| 17146 | multiple per week | 1 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'daily' -> 'multiple per week'; evidence_not_exact_substring |
| 17167 | multiple per week | 1 per week | no | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 17189 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 6 months (GTC), 1 per month (myoclonic)' -> '1 per month' |
| 17200 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 6 months (tonic-clonic), monthly (myoclonic)' -> '1 per month' |
| 17201 | 4 per month | 4 per month | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 17273 | 1 per 2 day | 1 per 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2 days' -> '1 per 2 day'; evidence_not_exact_substring |
| 17279 | 1 per 4 to 5 week | 1 per 4 to 5 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 4-5 weeks (absence); occasional (myoclonic)' -> '1 per 4 to 5 week'; evidence_not_exact_substring |
| 17287 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 1-2 days (absence), occasional (myoclonic)' -> '1 per 1 to 2 day'; evidence_not_exact_substring |
