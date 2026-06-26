# Gan 2026 LLM-Only Canonical-Pipeline Validation Run

Date: 2026-06-08

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: the 'purest form' fully-LLM comparator — a single DSPy call that collapses extract/select/normalize/project/render into one pass, with the now-mature deterministic/hybrid clinical-reasoning rule taxonomy embedded as prompt instructions rather than pre/post processing — can produce a directly scorable, fully rendered label without any deterministic normalization or projection stage downstream.

Minimal change: add an `llm_only_canonical_pipeline` runner alongside (not replacing) `llm_only_direct_labeler` and `hybrid_structured_events`. No deterministic `CandidateSet` is built or consumed; final_label is the model's directly rendered answer.

Data surface: `validation` split, `gan2026_split_v1`, 750 rows.
Rare full-validation reason: Phase 1 three-way architecture comparison (gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07): RESUME of full validation750 run, qwen3.6:35b pass via local Ollama, covering the three remaining architectures (deterministic, deterministic_canonical_pipeline, and hybrid already completed cleanly and are NOT re-run here). All prior fixes are now permanent in source: (1)+(2) llm_only_direct_labeler/llm_only_canonical_pipeline answer_kind enum communication, (3) schema_repair.py _ASSERTION_ALIASES 'unknown'->'unclear' corruption, (4)+(5) llm_only_canonical_pipeline shared dialect-repair switch + max_tokens 1200->2400 + strict=False literal-control-character fallback + 'ration'->'rationale' typo repair. NEW Bug #6 found mid-run: llm_only_direct_labeler showed a climbing failure trend (0,0,0,1,4 across the first 50/750 rows, all truncation: 'LM response was truncated due to exceeding max_tokens=900'). Root-caused via two-stage re-pilot: (a) raising max_tokens alone (900->2400) was INSUFFICIENT -- the same 4/50 failures persisted, just shifting from truncation-induced JSON errors to malformed-JSON errors ('Expecting property name enclosed in double quotes', 'Invalid control character'), proving qwen's verbose chain-of-thought reasoning embeds unescaped quotes/newlines in JSON string values; (b) the actual gap was that parse_decision_json used raw json.loads instead of the shared parse_json_payload_with_schema_repair helper (missing dialect repair + strict=False fallback) -- switching to the shared helper (matching llm_only_canonical_pipeline's fix) brought failures down to 3/50 (6%). The residual 3/50 is the SAME fundamental pattern already characterized and accepted for llm_only_canonical_pipeline: certain ambiguous notes push qwen into a structurally-fragile output style embedding unescaped quotes and raw newlines inside JSON string values, breaking JSON beyond what can be safely auto-repaired without risking corruption of clinical content (two of the three failing rows, 960 and 987, reproduced identically across all three re-pilot attempts -- genuinely fragile notes, not a fixable systemic gap). This ~6% rate is consistent with llm_only_canonical_pipeline's documented ~4-8% accepted noise and is being accepted on the same basis: comparable in magnitude to baseline noise (~1-4%) elsewhere, and itself a meaningful comparison data point about this architecture's robustness to verbose local-model output styles. max_tokens for llm_only_direct_labeler is raised to 2400 (matching hybrid/llm_only_canonical_pipeline) for this run. A SEVENTH bug (#7) was found immediately after relaunching with the Bug #6 fixes in place: 2 of the first 7/150 failures were a NEW error type, 'schema_validation_error: Input should be low, medium or high', caused by qwen emitting a stringified numeric confidence value (e.g. confidence: '0.8' or '0.85' as a JSON string) instead of the categorical low/medium/high label. The existing _repair_numeric_confidence helper in schema_repair.py only coerced bare int/float values, not numeric strings -- extended it to also parse and bucket stringified numerics (>=0.8 high, >=0.45 medium, else low), leaving non-numeric strings untouched. This is a fix to the SHARED repair_decision_payload path, so it benefits llm_only_canonical_pipeline and any other architecture using it too. Verified via a 150-row re-pilot with --disable-dspy-cache: zero schema_validation_error/confidence failures recurred; only the previously-characterized invalid_json residual noise (rows 960, 987, 2554, 2558, 2678, 338 -- qwen embedding unescaped quotes/raw newlines in verbose chain-of-thought reasoning, breaking JSON beyond safe auto-repair) reproduced, at 6/150 (4%), squarely within the accepted ~4-8% noise band documented for llm_only_canonical_pipeline. An EIGHTH bug (#8) was found mid-run at row 350/750 of the resumed run: 7 of 15 failures (47%) were a NEW error type, 'schema_validation_error: Input should be a valid string', root-caused to qwen legitimately emitting a JSON null for the time_window field (e.g. when answer_kind is 'unknown'/'no_reference' and no specific time window applies), whereas the LlmOnlyDirectLabelerDecisionRecord and LlmOnlyCanonicalPipelineDecisionRecord schemas declared time_window as a required str. gpt-4.1-mini never emits null here (it always emits a string, often '' for the same semantic case), which is why this never surfaced in the gpt-4.1-mini pass -- but null is an equally valid representation of 'no time window applies', matching the precedent already set by hybrid_structured_events's time_window: str | None field. Fixed by changing time_window from 'str' to 'str | None = None' in BOTH llm_only_direct_labeler.py and llm_only_canonical_pipeline.py (a shared schema fix benefiting both architectures still queued in this run -- canonical_pipeline was about to inherit the identical defect). Verified two ways: (a) directly re-parsing all 7 previously-failing raw_outputs (rows 5996, 6087, 6192, 6967, 7290, 7389, 7506) confirmed each now produces time_window=None with zero errors; (b) a fresh 50-row live re-pilot with --disable-dspy-cache reproduced ONLY the two already-characterized accepted-noise rows (960, 987 -- the same fragile-JSON pattern), with zero schema_validation_error recurrences. All 30 regression tests pass including two new guards (test_parse_decision_json_accepts_null_time_window_and_seizure_type in both llm_only_direct_labeler and llm_only_canonical_pipeline test suites). A NINTH bug (#9) was found in the v3 relaunch at row 500/750: 24 of 34 failures (71%) were the SAME error message, 'schema_validation_error: Input should be a valid string', but for a DIFFERENT field -- selected_seizure_type, root-caused identically to Bug #8: qwen legitimately emits JSON null for selected_seizure_type when answer_kind is 'no_reference' (the note contains no seizure-frequency information at all, so there is no seizure type to identify), where gpt-4.1-mini always emits a string (often '' or a descriptive phrase) for the same semantic situation -- confirmed via a full scan of both models' validation750 direct_labeler runs (gpt-4.1-mini: zero nulls across 750 rows for either field; qwen: 37 nulls in time_window, 24 in selected_seizure_type, with the 24 selected_seizure_type nulls mapping 1:1 onto the 24 new failures). Fixed identically to Bug #8: changed selected_seizure_type from 'str' to 'str | None = None' in BOTH llm_only_direct_labeler.py and llm_only_canonical_pipeline.py (the SAME two files, alongside the already-fixed time_window -- both fields now correctly nullable, matching hybrid_structured_events's existing pattern). Verified by directly re-parsing all 24 previously-failing raw_outputs: all 24 now produce valid decisions with selected_seizure_type=None and zero schema errors (2 carry only benign final_label_repaired notes, the same normalization-repair category seen throughout this run, not failures). All 30 regression tests pass, including updated guards (test_parse_decision_json_accepts_null_time_window_and_seizure_type) verifying BOTH nullable fields together in the realistic no_reference payload shape qwen actually emits. A TENTH finding (#10) emerged from investigating a climbing failure trend in the v4 relaunch: between rows 500-700/750, failures jumped from 10 to 24 (14 new failures in 190 rows, ~7.4% local rate vs ~2% baseline), coinciding with newly-appearing 'LM response was truncated due to exceeding max_tokens=2400' warnings -- suggesting a max_tokens defect. This hypothesis was DISPROVEN by direct experiment: raising max_tokens 2400->4000 and re-running the exact same failing rows with --disable-dspy-cache produced BYTE-IDENTICAL raw_output for every one of them (same length, same content, same invalid_json error), proving the model's own natural stopping point for these notes sits below even the 2400 ceiling -- the truncation warnings were a coincidental, separate phenomenon (likely silently absorbed by the existing repair fallback) and not the driver of the failure climb. Sampling the actual raw_outputs revealed the true cause: neither llm_only_direct_labeler.py nor llm_only_canonical_pipeline.py gave qwen ANY guidance on how to write the rationale field, so it filled it with verbose step-by-step deliberation -- e.g. "Is '4 per month' definitely allowed? The examples are '1 per day', '2 to 3 per month'. '4 per month' is structurally identical... I will proceed with '4 per month'." -- embedding nested quotes, question marks, run-on punctuation, and self-questioning that broke JSON parsing ('Invalid control character', "Expecting ',' delimiter", 'Unterminated string', and sometimes left the JSON object never closed at all). This is the SAME root-cause family as the already-characterized 'verbose CoT breaks JSON' noise, just manifesting as a locally denser cluster because rows in this region of validation750 happen to be longer/more ambiguous notes that invite more deliberation. FIXED at the prompt level (not schema/parsing): added an explicit instruction to both prompts -- 'Write rationale as one short, plain-language sentence stating only the deciding evidence and label... Do not show step-by-step reasoning, alternative options you considered and rejected, or self-questioning; state only the final justification' -- with a concrete example, bumping PROMPT_VERSION v0.1->v0.2 in both llm_only_direct_labeler.py and llm_only_canonical_pipeline.py. Verified via a targeted re-pilot that dropped and regenerated the previously-failing rows (source_row_index>=11000) fresh under the new prompt: 0/40 failures (vs the expected ~3/40 under the prior ~7% local rate), with direct sampling of 15+ raw rationale values confirming qwen now reliably produces single short plain-language sentences (e.g. "The note explicitly states 'several focal impaired-awareness spells per week', which maps directly to the normalized label 'multiple per week'.") and zero step-by-step narration; pragmatic/purist accuracy (0.85/0.825) remained consistent with the v0.1 baseline (~0.88/0.86), confirming no quality regression from the terser rationale style. max_tokens was also raised 2400->4000 for both architectures as a no-downside precaution (the byte-identical-output experiment proved it doesn't change behavior for rows that don't need the extra headroom, while still eliminating the handful of genuine truncation events observed, even though they were not the actual driver of this finding). Because PROMPT_VERSION changed, this run restarts llm_only_direct_labeler from scratch with --overwrite-existing -- the prior partial results used the v0.1 prompt and are not comparable. All 32 regression tests pass, including two new guards (test_build_prompt_input_instructs_short_plain_rationale in both llm_only_direct_labeler and llm_only_canonical_pipeline test suites) asserting the short-rationale instruction text is present in the prompt payload.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `ollama_chat/qwen3.6:35b`
- Provider/execution: native Ollama chat endpoint via DSPy/LiteLLM: `http://localhost:11434`
- Model role: LLM-only canonical-pipeline single-shot extract/select/normalize/project/render extractor
- Prompt/program version: `gan2026_llm_only_canonical_pipeline_v0.2`
- Temperature: `0.0`
- Max tokens: `4000`
- Mode: `live`
- DSPy cache enabled: `True`
- Ollama Qwen thinking mode: `disabled` (`think=false`)
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-08T19:35:33.528189+00:00`
- Run finished UTC: `2026-06-08T22:25:00.059982+00:00`
- Wall-clock elapsed: `10166.532` seconds (`169.442` minutes)
- Throughput: `0.073771` rows/sec (`13.555` sec/row)
- Optimizer: none
- Deterministic rule configuration: none as pre/post processing; the deterministic/hybrid rule taxonomy is embedded as prompt instructions only, and deterministic code is limited to label repair, evidence text-containment checking, and scoring.
- Git commit: `c11e96c`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_qwen3635b_2026-06-08.jsonl`

## Summary

- Decision records: 748 / 750
- Call failures: 0
- Parse/schema/label issues: 2
- Deterministic repair notes: 264
- Evidence text-containment (free-text evidence found verbatim in note, the comparator-appropriate metric in place of `CandidateSet` source-id validity rate): 574 / 750 (0.7653)
- Purist validation accuracy/micro F1 proxy: 0.7253 (544 / 750)
- Pragmatic validation accuracy/micro F1 proxy: 0.7760 (582 / 750)

## Applied Rule-Taxonomy Families (Self-Reported)

These counts reflect which embedded rule-taxonomy families the model itself reported as shaping its answer (`applied_rule_families`); they are a prompt-compliance signal, not a verified trace.

- `cluster_axis_ambiguity`: 123
- `concrete_frequency_precedence`: 145
- `conditional_only_trigger`: 56
- `conditional_only_trigger and relative_only_trend`: 3
- `denominator_window_mismatch`: 293
- `dominant_vague_current_burden`: 106
- `medication_cadence_ambiguity`: 3
- `multiple_current_primary_facts`: 30
- `relative_only_trend`: 1
- `same_window_additive_frequency`: 32
- `seizure_free_conflict`: 149
- `seizure_free_proxy_evidence_overreach`: 77
- `unknown_cadence_cluster_burden`: 21

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '4 per day' |
| 40 | 4 per week | 4 per week | yes |  |
| 79 | 6 to 7 per year | 6 to 7 per year | yes |  |
| 103 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 128 | 17 per month | 17 per month | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | yes | final_label_repaired: '1 per 6 days' -> '1 per 6 day' |
| 180 | 1 per 7 day | 1 per 7 day | yes | final_label_repaired: '1 per week' -> '1 per 7 day' |
| 182 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: 'multiple per day' -> '1 per 2 day' |
| 187 | 1 to 2 per week | 1 per 7 to 9 day | no | evidence_not_text_contained |
| 190 | 1 per 4 week | 1 per 4 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per month' -> '1 per 4 week' |
| 198 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per month' -> '1 per 4 week' |
| 212 | 1 to 2 per month | 1 per 3 to 4 week | yes |  |
| 218 | 1 per 3 week | 1 per 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 month | 1 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 278 | multiple per day | multiple per week | yes | json_dialect_repaired: python_literal |
| 280 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal |
| 338 | multiple per month | multiple per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'multiple per month' |
| 409 | 1 per month | 1 per month | yes |  |
| 419 | 2 per year | 2 per year | yes |  |
| 446 | 2 per week | 2 per week | yes |  |
| 466 | 21 to 28 per month | 21 to 28 per month | yes |  |
| 467 | 9 per month | 9 per month | yes |  |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | final_label_repaired: '4 to 10 per month' -> '12 to 30 per 3 month' |
| 598 | 2 per 16 month | 1 per 8 month | yes | final_label_repaired: '1 per 8 months' -> '2 per 16 month' |
| 659 | 2 per 4 day | 2 per 4 day | yes | final_label_repaired: '2 per 4 days' -> '2 per 4 day' |
| 665 | 2 per 2 week | 2 per 2 week | yes | final_label_repaired: '1 per week' -> '2 per 2 week' |
| 678 | 2 per 4 month | 2 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 694 | 1 per week | 1 per week | yes |  |
| 704 | 2 per month | 2 per month | yes |  |
| 725 | multiple per day | 1 per day | no | evidence_not_text_contained |
| 731 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day' |
| 743 | multiple per day | multiple per week | yes |  |
| 744 | multiple per week | multiple per week | yes | final_label_repaired: 'multiple per day' -> 'multiple per week' |
| 763 | 1 per week | 1 per week | yes |  |
| 790 | 1 to 2 per week | 1 per 7 to 10 day | no |  |
| 816 | 4 per year | 1 per month | no | json_dialect_repaired: python_literal |
| 849 | 1 per year | 1 per year | yes |  |
| 854 | 1 per year | 1 per year | yes |  |
| 869 | unknown | multiple per month | yes | evidence_not_text_contained |
| 891 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: 'multiple per day' -> '1 per 2 day' |
| 899 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per week' -> '1 per 2 week' |
| 959 | 1 per 2 month | 1 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per month' -> '1 per 2 month' |
| 960 | 1 per 2 month | 1 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per month' -> '1 per 2 month' |
| 978 | 1 per 2 month | 1 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 987 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month'; evidence_not_text_contained |
| 1030 | 1 per month | 1 to 3 per month | no | final_label_repaired: 'unknown' -> '1 per month' |
| 1046 | unknown | 3 to 5 per month | no | json_dialect_repaired: python_literal |
| 1070 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1094 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 1165 | seizure free for multiple year | 5 to 7 per 3 week | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 6 week' -> 'seizure free for multiple year' |
| 1171 | 7 to 9 per 3 week | 7 to 9 per 3 week | yes | final_label_repaired: '7 to 9 per 3 weeks' -> '7 to 9 per 3 week' |
| 1207 | 7 to 9 per week | 21 to 28 per 3 month | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 1223 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1249 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 1281 | 5 to 7 per year | 5 to 7 per year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '5 to 7 per year' |
| 1317 | unknown | unknown, multiple per cluster | yes |  |
| 1357 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 per day'; evidence_not_text_contained |
| 1363 | unknown | 3 per day | no |  |
| 1413 | 9 per month | 9 per month | yes |  |
| 1454 | 7 per week | 7 per week | yes |  |
| 1486 | 2 per month | 3 per month | yes | final_label_repaired: '3 per month' -> '2 per month' |
| 1573 | 11 per week | 11 per week | yes |  |
| 1591 | 5 per month | 11 per month | yes | final_label_repaired: '11 per month' -> '5 per month' |
| 1596 | 12 per week | 12 per week | yes |  |
| 1597 | 12 per month | 12 per month | yes |  |
| 1636 | 5 per month | 5 per month | yes |  |
| 1640 | 5 per week | 5 per week | yes |  |
| 1687 | multiple per day | multiple per week | yes | final_label_repaired: 'unknown' -> 'multiple per day'; evidence_not_text_contained |
| 1694 | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per fortnight' -> '3 per 2 week' |
| 1695 | seizure free for 1 month | multiple per month | no |  |
| 1706 | unknown | multiple cluster per month, multiple per cluster | no |  |
| 1707 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'multiple per week' |
| 1772 | 11 per 6 month | 11 per 6 month | yes | final_label_repaired: '11 per 6 months' -> '11 per 6 month' |
| 1773 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '11 per 3 months' -> '11 per 3 month' |
| 1790 | 8 per 4 month | 8 per 4 month | yes | final_label_repaired: '8 per 4 months' -> '8 per 4 month' |
| 1794 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '8 per 2 months' -> '8 per 2 month' |
| 1866 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '8 per 2 months' -> '8 per 2 month' |
| 1880 | multiple per week | 8 per 2 month | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 1887 | 4 per 3 month | 4 per 3 month | yes | final_label_repaired: '1 per month' -> '4 per 3 month' |
| 1914 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '7 per 3 months' -> '7 per 3 month' |
| 1922 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '7 per 3 months' -> '7 per 3 month' |
| 1923 | 7 per 6 month | 7 per 6 month | yes | final_label_repaired: '7 per 6 months' -> '7 per 6 month' |
| 1979 | 3 per 2 month | 6 per 2 month | yes | final_label_repaired: '6 per 2 months' -> '3 per 2 month' |
| 1980 | 6 per 3 month | 6 per 3 month | yes | final_label_repaired: '6 per 3 months' -> '6 per 3 month' |
| 2023 | 5 per month | 5 per month | yes |  |
| 2080 | multiple per day | multiple per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'multiple per day' |
| 2094 | multiple per month | multiple per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'multiple per month' |
| 2114 | unknown | multiple per month | yes |  |
| 2149 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 2166 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | final_label_repaired: '3 to 5 per week' -> '3 to 5 per 2 week' |
| 2233 | 3 to 4 per month | 6 to 7 per 2 month | yes |  |
| 2245 | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | final_label_repaired: '7 to 8 per 3 weeks' -> '7 to 8 per 3 week' |
| 2259 | 2 to 3 per month | 6 to 8 per 3 month | yes |  |
| 2354 | 6 to 7 per week | 6 to 7 per week | yes |  |
| 2366 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 2369 | 3 to 4 per month | 3 to 4 per month | yes |  |
| 2374 | 7 to 9 per month | 7 to 9 per month | yes |  |
| 2425 | 6 to 8 per month | 6 to 8 per month | yes | evidence_not_text_contained |
| 2427 | 3 to 5 per month | 3 to 5 per month | yes | final_label_repaired: 'unknown' -> '3 to 5 per month' |
| 2435 | 10 to 14 per month | 5 to 7 per 2 week | yes |  |
| 2437 | 1 to 2 per week | 2 to 3 per 2 month | no |  |
| 2440 | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | final_label_repaired: '5 to 7 per 2 months' -> '5 to 7 per 2 month' |
| 2456 | 3 to 4 per week | 6 to 7 per 2 week | yes |  |
| 2459 | 7 to 9 per 2 week | 7 to 9 per 2 week | yes | final_label_repaired: '7 to 9 per 2 weeks' -> '7 to 9 per 2 week' |
| 2487 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | final_label_repaired: '2 to 3 per 3 months' -> '2 to 3 per 3 month' |
| 2513 | 4 to 6 per week | 2 to 3 per 2 week | yes | json_dialect_repaired: python_literal |
| 2541 | 16 to 18 per month | 8 to 9 per 2 week | yes |  |
| 2548 | 5 to 6 per 2 month | 5 to 6 per 2 month | yes | final_label_repaired: '5 to 6 per 2 months' -> '5 to 6 per 2 month' |
| 2554 | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | final_label_repaired: '1 to 10 per 2 months' -> '1 to 10 per 2 month' |
| 2558 | 3 to 4 per month | 3 to 4 per 2 month | yes | json_dialect_repaired: python_literal |
| 2609 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2622 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2628 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2678 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day'; evidence_not_text_contained |
| 2681 | 1 per day | 1 per day | yes |  |
| 2698 | 1 per 2 day | 1 per 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per 2 day' |
| 2731 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 2740 | 1 per month | 1 per month | yes | evidence_not_text_contained |
| 2748 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 2759 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 2762 | 1 per month | 1 per month | yes |  |
| 2765 | 1 per month | 1 per month | yes |  |
| 2776 | 1 per week | 1 per week | yes |  |
| 2789 | 1 per week | 1 per week | yes |  |
| 2812 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2822 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2824 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day' |
| 2877 | 2 per year | 2 per year | yes | json_dialect_repaired: python_literal |
| 2887 | 2 per week | 2 per week | yes |  |
| 2907 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 2932 | seizure free for 9 month | seizure free for 9 month | yes | json_dialect_repaired: python_literal |
| 2938 | seizure free for 8 month | seizure free for 8 month | yes |  |
| 2965 | seizure free for 6 month | seizure free for 16 month | yes |  |
| 2992 | seizure free for 6 month | seizure free for 7 month | yes | evidence_not_text_contained |
| 3015 | seizure free for 1 year | seizure free for 12 month | yes |  |
| 3048 | seizure free for 16 month | seizure free for 16 month | yes |  |
| 3058 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3082 | seizure free for 10 month | seizure free for 10 month | yes |  |
| 3095 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3113 | seizure free for 14 month | seizure free for 14 month | yes | json_dialect_repaired: python_literal |
| 3118 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 3137 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 3224 | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 cluster per month, 6 to 7 per cluster' |
| 3242 | 2 cluster per month, multiple per cluster | 2 cluster per month, 5 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: '2 clusters per month' -> '2 cluster per month, multiple per cluster' |
| 3261 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '2 cluster per month, 4 per cluster' |
| 3262 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '2 cluster per month, 5 per cluster' |
| 3281 | 8 per month | 8 per month | yes | final_label_repaired: 'multiple per day' -> '8 per month' |
| 3297 | 6 per month | 6 per month | yes |  |
| 3325 | 3 per week | 3 per week | yes |  |
| 3356 | unknown | unknown | yes |  |
| 3371 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free for 8 week' -> 'seizure free for multiple year' |
| 3436 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 3468 | unknown | unknown | yes |  |
| 3469 | unknown | unknown | yes |  |
| 3482 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 3493 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 3507 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 3512 | unknown | unknown | yes |  |
| 3528 | unknown | unknown | yes |  |
| 3532 | unknown | unknown | yes |  |
| 3534 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 3600 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 3623 | 7 per week | 7 per week | yes | final_label_repaired: 'unknown' -> '7 per week' |
| 3643 | 7 per week | 7 per week | yes | final_label_repaired: 'unknown' -> '7 per week' |
| 3681 | 9 per month | 9 per month | yes |  |
| 3682 | 6 per month | 6 per month | yes |  |
| 3710 | 5 per week | 5 per week | yes |  |
| 3753 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day'; evidence_not_text_contained |
| 3766 | 8 per year | 8 per year | yes |  |
| 3774 | 9 per year | 9 per year | yes | json_dialect_repaired: python_literal |
| 3791 | 10 per year | 10 per year | yes |  |
| 3801 | 9 per month | 9 per month | yes |  |
| 3806 | 6 per month | 6 per month | yes |  |
| 3827 | 7 per month | 7 per month | yes | json_dialect_repaired: python_literal |
| 3846 | multiple per day | 2 per day | no |  |
| 3849 | multiple per day | 3 per day | no | json_dialect_repaired: python_literal |
| 3889 | 8 per year | 8 per year | yes |  |
| 3892 | 3 per year | 3 per year | yes |  |
| 3940 | 4 per week | 4 per week | yes |  |
| 3949 | 4 per week | 4 per week | yes | json_dialect_repaired: python_literal |
| 3988 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal |
| 3995 | unknown | 1 per month | no |  |
| 3999 | unknown | 1 per month | no |  |
| 4022 | 8 per month | 8 per month | yes |  |
| 4026 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 4092 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '2 to 3 per week' -> '1 per 2 to 3 week' |
| 4100 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 to 2 per month' -> '1 per 2 to 3 week' |
| 4110 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: 'multiple per day' -> '1 per 1 to 2 day' |
| 4116 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 per 1 to 2 day' |
| 4173 | no seizure frequency reference | 1 per 2 week | no | final_label_repaired: '1 per fortnight' -> 'no seizure frequency reference' |
| 4243 | 1 to 2 per week | 1 per 2 to 3 week | no |  |
| 4258 | 4 per week | 4 per week | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 4337 | 3 per 3 month | 3 per 3 month | yes | final_label_repaired: 'unknown' -> '3 per 3 month'; evidence_not_text_contained |
| 4345 | 4 per month | 4 per month | yes | evidence_not_text_contained |
| 4368 | 5 per 2 month | 5 per 2 month | yes | final_label_repaired: '5 per month' -> '5 per 2 month' |
| 4402 | 7 per 7 month | 7 per 7 month | yes | final_label_repaired: 'unknown' -> '7 per 7 month' |
| 4410 | 1 per 2 to 3 month | 4 per 7 month | yes | final_label_repaired: 'unknown' -> '1 per 2 to 3 month'; evidence_not_text_contained |
| 4478 | 19 per week | 19 per week | yes |  |
| 4480 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 4496 | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '7 to 8 per quarter' -> '7 to 8 per 3 month' |
| 4562 | 1 per 6 week | 1 per 6 week | yes | final_label_repaired: '1 per 6 weeks' -> '1 per 6 week' |
| 4563 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 4574 | 1 per 4 week | 1 per 4 week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 per 4 week' |
| 4592 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 4597 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: 'unknown' -> '1 per 3 week' |
| 4624 | 2 per month | 1 per 3 to 4 day | no |  |
| 4631 | 1 per 14 to 21 day | 1 per 14 to 21 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 per 14 to 21 day' |
| 4690 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'multiple per day'; evidence_not_text_contained |
| 4694 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'multiple per day'; evidence_not_text_contained |
| 4700 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'multiple per day' |
| 4709 | unknown | multiple per day | yes |  |
| 4731 | unknown | unknown | yes | evidence_not_text_contained |
| 4732 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 4771 | unknown | unknown | yes | evidence_not_text_contained |
| 4839 | seizure free for 4 month | seizure free for multiple month | yes |  |
| 4842 | seizure free for 6 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 4910 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4919 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4926 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 4951 | seizure free for 6 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 4956 | seizure free for 7 month | seizure free for 7 month | yes |  |
| 4992 | seizure free for 6 month | seizure free for 11 month | yes |  |
| 4994 | seizure free for 6 month | seizure free for 6 month | yes | json_dialect_repaired: python_literal |
| 5040 | seizure free for 6 month | seizure free for 6 months | yes |  |
| 5082 | seizure free for 6 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 5092 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 5110 | seizure free for 3 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 5121 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 5136 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 5141 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 5197 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 5210 | seizure free for 6 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 5221 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 5248 | seizure free for 6 month | seizure free for multiple year | yes | evidence_not_text_contained |
| 5331 | seizure free for 12 month | seizure free for 12 month | yes | json_dialect_repaired: python_literal |
| 5345 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 5351 | seizure free for 18 month | seizure free for 18 month | yes | json_dialect_repaired: python_literal |
| 5379 | seizure free for 6 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 5406 | seizure free for 2 month | seizure free for multiple month | yes |  |
| 5476 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 5490 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 5491 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 5504 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 5507 | unknown | unknown | yes |  |
| 5528 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 5534 | unknown | 1 per multiple month | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 5551 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 5567 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal |
| 5584 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal |
| 5624 | 1 per 10 day | 1 per 10 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 10 days' -> '1 per 10 day' |
| 5652 | 1 per 8 day | 1 per 8 day | yes | final_label_repaired: '1 per 8 days' -> '1 per 8 day' |
| 5682 | 2 to 4 per month | 2 to 4 per month | yes |  |
| 5696 | 4 per 4 month | 3 per 4 month | no | final_label_repaired: '3 per 4 months' -> '4 per 4 month'; evidence_not_text_contained |
| 5763 | 6 per 3 month | 2 per month | yes | final_label_repaired: '6 per 3 months' -> '6 per 3 month' |
| 5767 | 2 per month | 1 per 1 to 2 week | yes | final_label_repaired: '2 to 3 per week' -> '2 per month' |
| 5791 | 3 per 3 month | 1 per month | yes | final_label_repaired: '3 per 3 months' -> '3 per 3 month' |
| 5827 | 1 per week | multiple per week | no |  |
| 5837 | unknown | 2 cluster per 3 week, multiple per cluster | no |  |
| 5866 | 4 per 6 week | 4 per 6 week | yes | final_label_repaired: '4 per 6 weeks' -> '4 per 6 week' |
| 5873 | multiple per day | multiple per week | yes | evidence_not_text_contained |
| 5921 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 5954 | 2 per week | 2 per week | yes |  |
| 5961 | 1 to 2 per week | 1 per 2 to 3 week | no |  |
| 5974 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 5977 | multiple per 6 week | unknown | yes | final_label_repaired: 'unknown' -> 'multiple per 6 week' |
| 5995 | unknown | 1 per 3 months | no |  |
| 5996 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 6026 | 3 per 2 month | 3 per 2 month | yes | final_label_repaired: '1.5 per month' -> '3 per 2 month' |
| 6029 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 6034 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 6065 | 12 per 3 month | 5 per month | no | final_label_repaired: '12 per 3 months' -> '12 per 3 month' |
| 6077 | 1 per 8 month | unknown | no | final_label_repaired: '1 per 8 months' -> '1 per 8 month'; evidence_not_text_contained |
| 6087 | unknown | unknown | yes | evidence_not_text_contained |
| 6094 | 5 per 6 week | 3 per month | yes | final_label_repaired: '5 per 6 weeks' -> '5 per 6 week' |
| 6112 | 3 to 5 per month | 3 to 5 per month | yes | json_dialect_repaired: python_literal |
| 6131 | unknown | unknown | yes | evidence_not_text_contained |
| 6137 | 1 to 2 per week | 1 per 2 week | no |  |
| 6153 | 9 per 4 week | 9 per month | yes | final_label_repaired: '9 per month' -> '9 per 4 week' |
| 6180 | multiple per week | multiple per week | yes | final_label_repaired: 'unknown' -> 'multiple per week'; evidence_not_text_contained |
| 6192 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 6204 | 1 per 3 to 4 week | 2 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 3 to 4 weeks' -> '1 per 3 to 4 week' |
| 6209 | multiple per day | multiple per day | yes |  |
| 6244 | unknown | unknown | yes | evidence_not_text_contained |
| 6251 | unknown | 1 per 1 to 2 month | no | evidence_not_text_contained |
| 6273 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 6319 | unknown | 1 per week | no | json_dialect_repaired: python_literal |
| 6321 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 6331 | 2 per 6 week | 2 per 6 weeks | yes | final_label_repaired: 'unknown' -> '2 per 6 week' |
| 6358 | seizure free for 6 month | seizure free for 15 to 16 months | yes |  |
| 6368 | multiple per day | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'multiple per day'; evidence_not_text_contained |
| 6395 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 6501 | unknown | unknown | yes | evidence_not_text_contained |
| 6509 | no seizure frequency reference | 1 per week | no | json_dialect_repaired: python_literal; final_label_repaired: '2 per fortnight' -> 'no seizure frequency reference' |
| 6571 | seizure free for 6 month | unknown | no | json_dialect_repaired: python_literal |
| 6607 | unknown | unknown | yes | evidence_not_text_contained |
| 6684 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 over 4 months' -> '3 per 4 month' |
| 6701 | 4 per 3 week | 4 per 3 week | yes | final_label_repaired: '4 per 3 weeks' -> '4 per 3 week' |
| 6738 | 1 to 2 per month | 1 per 6 to 8 week | no | json_dialect_repaired: python_literal |
| 6852 | 4 to 6 per month | 4 to 6 per month | yes |  |
| 6889 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'multiple per week'; evidence_not_text_contained |
| 6952 | 2 per week | 2 per week | yes |  |
| 6967 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 6987 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 7093 | unknown | unknown | yes | evidence_not_text_contained |
| 7126 | unknown | unknown | yes |  |
| 7141 | unknown | unknown | yes | evidence_not_text_contained |
| 7167 | unknown | 1 cluster per 2 weeks, 2 to 4 per cluster | no |  |
| 7168 | 2 per year | unknown | no |  |
| 7192 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'multiple per week' |
| 7195 | 1 per month | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 per month' |
| 7196 | 6 per 6 week | 1 per week | yes | final_label_repaired: '6 per 6 weeks' -> '6 per 6 week' |
| 7198 | unknown | unknown | yes |  |
| 7275 | 3 per 12 week | 1 per month | yes | final_label_repaired: '3 per month' -> '3 per 12 week' |
| 7290 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 7316 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 7389 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 7392 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 7401 | unknown | 2 cluster per 6 week, 1 to 2 per cluster | no | json_dialect_repaired: python_literal |
| 7409 | multiple per week | unknown | yes | final_label_repaired: 'unknown' -> 'multiple per week' |
| 7455 | multiple per day | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'multiple per day' |
| 7475 | unknown | 2 per 6 month | no | evidence_not_text_contained |
| 7491 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 7506 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 7573 | unknown | 1 per 2 week | no | json_dialect_repaired: python_literal |
| 7581 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 7615 | 3 to 6 per month | 3 to 7 per month | yes |  |
| 7650 | unknown | unknown | yes |  |
| 7738 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 7785 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 7818 | seizure free for 6 month | seizure free for 2 years | yes |  |
| 7834 | seizure free for 6 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 7859 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free for several weeks' -> 'seizure free for multiple year' |
| 7872 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 7911 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 7961 | 1 per day | seizure free for multiple year | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 6 month' -> '1 per day'; evidence_not_text_contained |
| 8002 | 1 to 2 per month | 1 per 6 to 8 week | no |  |
| 8006 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8079 | seizure free for 6 month | seizure free for 18 month | yes | evidence_not_text_contained |
| 8089 | seizure free for 16 month | seizure free for 16 month | yes | evidence_not_text_contained |
| 8124 | seizure free for 13 month | seizure free for 13 month | yes | json_dialect_repaired: python_literal |
| 8144 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 8145 | seizure free for 6 month | seizure free for 6 month | yes | json_dialect_repaired: python_literal |
| 8160 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 8180 | seizure free for 6 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 8188 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 8203 | seizure free for 6 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 8224 | seizure free for 3 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 8235 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8264 | seizure free for 4 month | seizure free for 4 month | yes | evidence_not_text_contained |
| 8265 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8354 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 8355 | 2 per year | seizure free for multiple year | no | final_label_repaired: 'seizure free for 12 month' -> '2 per year'; evidence_not_text_contained |
| 8400 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 8419 | unknown | 1 to 2 per week | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 8474 | seizure free for 6 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 8512 | seizure free for 3 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 8564 | seizure free for 6 month | seizure free for 6 month | yes | json_dialect_repaired: python_literal |
| 8577 | seizure free for 18 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 8581 | seizure free for 6 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 8593 | seizure free for 14 month | seizure free for 14 month | yes |  |
| 8596 | seizure free for 11 month | seizure free for 11 month | yes | json_dialect_repaired: python_literal |
| 8674 | seizure free for 6 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 8724 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8730 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8794 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8802 | seizure free for 12 month | seizure free for 12 month | yes | evidence_not_text_contained |
| 8805 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8808 | 0 per 10 month | seizure free for 10 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 10 month' -> '0 per 10 month' |
| 8820 | seizure free for 6 month | seizure free for 7 month | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 8835 | seizure free for 10 month | seizure free for 10 month | yes |  |
| 8854 | seizure free for 6 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 8893 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8922 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 8924 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 8938 | seizure free for 6 month | seizure free for 10 month | yes | json_dialect_repaired: python_literal |
| 8949 | seizure free for 6 month | seizure free for 6 month | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 8969 | seizure free for 6 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 9002 | 7 per year | 7 per year | yes | final_label_repaired: 'unknown' -> '7 per year' |
| 9063 | seizure free for 8 month | seizure free for 8 month | yes |  |
| 9103 | unknown | unknown | yes | evidence_not_text_contained |
| 9163 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 9190 | seizure free for 6 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 9215 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 9238 | seizure free for 6 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 9250 | seizure free for 6 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal |
| 9259 | seizure free for 6 month | seizure free for 1 year | yes |  |
| 9287 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 9299 | 5 per week | 5 per week | yes |  |
| 9300 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 9344 | unknown | multiple per day | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 9365 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per day' -> '1 per 2 day' |
| 9368 | 1 per 2 day | 1 per 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per day' -> '1 per 2 day' |
| 9391 | 1 per month | 1 per month | yes |  |
| 9397 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 9449 | 4 per 6 month | 4 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 per month' -> '4 per 6 month' |
| 9462 | 7 per 11 month | 7 per 11 month | yes | final_label_repaired: '8 per year' -> '7 per 11 month' |
| 9496 | 6 per 12 month | 6 per 12 month | yes | final_label_repaired: 'unknown' -> '6 per 12 month' |
| 9547 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 9588 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 9704 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 9815 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'multiple per day'; evidence_not_text_contained |
| 9877 | unknown | unknown | yes |  |
| 9879 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 9888 | unknown | unknown | yes |  |
| 9912 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 9937 | unknown | 1 cluster per month, multiple per cluster | no | json_dialect_repaired: python_literal |
| 9943 | unknown | 1 cluster per 4 to 5 week, multiple per cluster | no |  |
| 9955 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: 'unknown' -> '1 cluster per month, multiple per cluster' |
| 10003 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: 'unknown' -> '1 cluster per week, multiple per cluster' |
| 10047 | 2 cluster per 3 month, multiple per cluster | 2 cluster per 3 month, multiple per cluster | yes | final_label_repaired: 'unknown' -> '2 cluster per 3 month, multiple per cluster'; evidence_not_text_contained |
| 10063 | 3 cluster per 3 month, multiple per cluster | 3 cluster per 3 month, multiple per cluster | yes | final_label_repaired: 'unknown' -> '3 cluster per 3 month, multiple per cluster' |
| 10097 | 3 per month | 3 cluster per month, multiple per cluster | no |  |
| 10147 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 10183 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 10189 | unknown | unknown, 3 to 4 per cluster | yes | json_dialect_repaired: python_literal |
| 10200 | unknown | unknown, 2 to 4 per cluster | yes | json_dialect_repaired: python_literal |
| 10237 | unknown | 4 cluster per month, multiple per cluster | no | json_dialect_repaired: python_literal |
| 10245 | unknown | 3 cluster per month, multiple per cluster | no |  |
| 10260 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 10264 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 10266 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 10268 | unknown | unknown | yes | evidence_not_text_contained |
| 10371 | seizure free for 6 month | seizure free for multiple year | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 10383 | 1 cluster per week, 5 per cluster | 1 cluster per week, 5 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 5 per cluster' |
| 10386 | no seizure frequency reference | 1 cluster per week, 2 to 3 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: '2 to 3 per cluster' -> 'no seizure frequency reference' |
| 10434 | multiple per day | multiple cluster per week, 2 to 3 per cluster | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 10481 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '4 cluster per month, multiple per cluster' |
| 10487 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10509 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 10517 | 3 to 4 per week | 3 to 4 cluster per week, multiple per cluster | no | json_dialect_repaired: python_literal |
| 10542 | unknown | unknown, 2 to 4 per cluster | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 10578 | unknown | unknown, 3 to 4 per cluster | yes | json_dialect_repaired: python_literal |
| 10583 | unknown | unknown, 2 to 3 per cluster | yes |  |
| 10594 | unknown | unknown, 2 per cluster | yes | json_dialect_repaired: python_literal |
| 10618 | unknown | unknown, 4 to 6 per cluster | yes |  |
| 10629 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 10630 | unknown | multiple cluster per 2 week, 5 per cluster | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 10673 | unknown | 1 cluster per month, multiple per cluster | no |  |
| 10677 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 per month' -> '1 cluster per month, multiple per cluster' |
| 10753 | unknown | unknown | yes | evidence_not_text_contained |
| 10807 | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '2 cluster per month, multiple per cluster' |
| 10829 | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '2 cluster per month, multiple per cluster' |
| 10862 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10865 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 cluster per week, multiple per cluster'; evidence_not_text_contained |
| 10873 | 1 cluster per week, 6 per cluster | 1 cluster per week, 6 per cluster | yes | final_label_repaired: 'unknown' -> '1 cluster per week, 6 per cluster' |
| 10894 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 4 per cluster' |
| 10896 | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 3 to 4 per cluster' |
| 10902 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 4 per cluster' |
| 10933 | 2 to 3 cluster per month, 5 per cluster | 2 to 3 cluster per month, 5 per cluster | yes | final_label_repaired: '2 to 3 per month' -> '2 to 3 cluster per month, 5 per cluster' |
| 10942 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 5 per cluster' |
| 10965 | 2 to 3 per week | 2 cluster per month, 4 to 5 per cluster | yes |  |
| 10967 | unknown | 3 cluster per month, 4 to 5 per cluster | no | final_label_repaired: '3 clusters per month' -> 'unknown' |
| 10984 | 3 cluster per month, 3 to 4 per cluster | 3 cluster per month, 3 to 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 to 4 per month' -> '3 cluster per month, 3 to 4 per cluster' |
| 10996 | 1 to 2 cluster per month, 4 per cluster | 1 to 2 cluster per month, 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 to 2 per month' -> '1 to 2 cluster per month, 4 per cluster' |
| 11002 | 2 to 4 cluster per month, 5 per cluster | 2 to 4 cluster per month, 5 per cluster | yes | final_label_repaired: '2 to 4 per month' -> '2 to 4 cluster per month, 5 per cluster' |
| 11035 | 1 cluster per 3 month, 1 per cluster | 1 cluster per 3 month, 1 per cluster | yes | final_label_repaired: '1 cluster per quarter' -> '1 cluster per 3 month, 1 per cluster'; evidence_not_text_contained |
| 11109 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '2 cluster per month, 5 per cluster' |
| 11118 | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 3 per cluster' -> '2 cluster per month, 6 per cluster' |
| 11131 | 2 cluster per month, 3 to 4 per cluster | 2 cluster per month, 3 to 4 per cluster | yes | final_label_repaired: '3 to 4 per day' -> '2 cluster per month, 3 to 4 per cluster' |
| 11197 | unknown | 1 cluster per month, 4 to 6 per cluster | no | json_dialect_repaired: python_literal |
| 11216 | seizure free for 4 month | unknown | no |  |
| 11254 | seizure free for 6 month | unknown | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 11259 | unknown | unknown | yes |  |
| 11262 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 11272 | seizure free for 6 month | unknown | no | evidence_not_text_contained |
| 11282 |  | unknown | no | invalid_json: Expecting ',' delimiter; evidence_not_text_contained |
| 11337 | 1 per 8 week | unknown | no | final_label_repaired: 'unknown' -> '1 per 8 week'; evidence_not_text_contained |
| 11350 | multiple per day | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> 'multiple per day' |
| 11380 | multiple per day | unknown | yes | final_label_repaired: 'unknown' -> 'multiple per day'; evidence_not_text_contained |
| 11389 | unknown | unknown | yes | evidence_not_text_contained |
| 11400 | 1 per day | no seizure frequency reference | no | final_label_repaired: 'no seizure frequency reference' -> '1 per day'; evidence_not_text_contained |
| 11405 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11408 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11409 | unknown | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11411 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11434 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11463 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11562 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11585 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11606 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11614 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11632 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11640 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11658 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11681 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11706 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11711 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11728 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11734 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11737 | seizure free for 6 month | no seizure frequency reference | no |  |
| 11752 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11756 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 11763 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11804 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 11824 | 1 per day | no seizure frequency reference | no | final_label_repaired: 'no seizure frequency reference' -> '1 per day' |
| 11841 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11852 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 12036 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal |
| 12041 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal |
| 12046 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal |
| 12051 | multiple per day | multiple per day | yes |  |
| 12111 | multiple per week | multiple per week | yes |  |
| 12127 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal |
| 12130 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12139 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per week' -> 'multiple per week' |
| 12145 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per week' -> 'multiple per week' |
| 12192 | multiple per day | 1 per day | no | evidence_not_text_contained |
| 12218 | multiple per day | 1 per day | no | json_dialect_repaired: python_literal |
| 12236 | multiple per day | 1 per day | no | json_dialect_repaired: python_literal |
| 12246 | 1 to 2 per day | 1 to 2 per day | yes |  |
| 12314 | 3 per week | 3 per week | yes |  |
| 12366 | multiple per day | 4 per day | no |  |
| 12378 | multiple per day | 4 per day | no | json_dialect_repaired: python_literal |
| 12383 | multiple per day | 4 per day | no |  |
| 12403 | multiple per day | 2 to 3 per day | no |  |
| 12412 | multiple per day | 2 per day | no |  |
| 12422 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day' |
| 12438 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 3 per year' -> '1 per day' |
| 12456 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12460 | 1 per day | 1 per day | yes | final_label_repaired: '2 per year' -> '1 per day' |
| 12468 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day' |
| 12484 | 3 to 4 per day | 3 to 4 per day | yes | json_dialect_repaired: python_literal |
| 12502 | 1 cluster per month, multiple per cluster | 4 per day | no | final_label_repaired: 'unknown' -> '1 cluster per month, multiple per cluster' |
| 12506 | 1 cluster per month, multiple per cluster | 4 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 cluster per month, multiple per cluster' |
| 12537 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day' |
| 12548 | 3 per 6 month | 1 per day | no | final_label_repaired: 'unknown' -> '3 per 6 month'; evidence_not_text_contained |
| 12551 | 12 per 6 month | 1 per day | no | final_label_repaired: 'unknown' -> '12 per 6 month' |
| 12556 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day' |
| 12562 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day' |
| 12573 | 2 per 6 month | 1 per day | no | final_label_repaired: 'unknown' -> '2 per 6 month'; evidence_not_text_contained |
| 12584 | 1 per 3 month | 1 per week | no | final_label_repaired: '1 per 3 months' -> '1 per 3 month' |
| 12641 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day'; evidence_not_text_contained |
| 12665 | 1 to 2 per month | 1 per day | no |  |
| 12667 | 1 to 2 per month | 1 per day | no | json_dialect_repaired: python_literal |
| 12676 | 1 to 2 per 6 month | 1 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 to 2 per 6 month'; evidence_not_text_contained |
| 12679 | 1 to 2 per month | 1 per day | no |  |
| 12749 | 3 to 4 per day | 3 to 4 per day | yes | json_dialect_repaired: python_literal |
| 12751 | unknown | 4 per day | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 12788 | 6 per year | 6 per 4 month | no | json_dialect_repaired: python_literal |
| 12810 | 5 per year | 5 per 2 month | no |  |
| 12823 | 9 per year | 9 per month | no | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '9 per year'; evidence_not_text_contained |
| 12827 | 5 per year | 5 per 5 month | no |  |
| 12835 | 4 per year | 4 per month | no |  |
| 12877 | 10 per year | 10 per 4 month | no | json_dialect_repaired: python_literal |
| 12882 | 7 per year | 7 per 4 month | no | json_dialect_repaired: python_literal |
| 12901 | 8 per year | 8 per 5 month | no |  |
| 12949 | 9 per year | 9 per 6 month | no |  |
| 12950 | 1 per 2 to 3 week | 7 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 per 2 to 3 week' |
| 12963 | unknown | unknown | yes |  |
| 12979 | 3 per year | 3 per 4 month | yes | json_dialect_repaired: python_literal |
| 13008 | 4 per year | 4 per month | no |  |
| 13011 | 3 per year | 3 per 4 month | yes |  |
| 13051 | unknown | 2 per 8 month | no | evidence_not_text_contained |
| 13058 | unknown | 2 per 7 month | no | evidence_not_text_contained |
| 13114 | unknown | 1 per year | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 13122 | unknown | 3 per year | no | json_dialect_repaired: python_literal |
| 13149 | unknown | 3 per year | no | evidence_not_text_contained |
| 13178 | seizure free for 6 month | 1 per 6 month | no |  |
| 13190 | unknown | 1 per 5 month | no | json_dialect_repaired: python_literal |
| 13209 | 1 per year | 1 per 8 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 per year' |
| 13267 | unknown | 2 per 5 month | no | evidence_not_text_contained |
| 13290 | 2 per month | 4 per 6 month | no |  |
| 13327 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13336 | seizure free for 1.5 year | seizure free for 1.5 year | yes | json_dialect_repaired: python_literal |
| 13349 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13385 | seizure free for 18 month | seizure free for 1.5 year | yes | json_dialect_repaired: python_literal |
| 13450 | seizure free for 6 month | seizure free for 1 year | yes |  |
| 13471 | seizure free for 5 year | seizure free for 5 year | yes |  |
| 13478 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 13485 | seizure free for 6 month | seizure free for multiple year | yes | evidence_not_text_contained |
| 13487 | seizure free for 6 month | seizure free for multiple year | yes | json_dialect_repaired: python_literal |
| 13513 | seizure free for 6 month | seizure free for 1.5 year | yes |  |
| 13574 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13595 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13598 | seizure free for multiple year | seizure free for multiple year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13608 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13627 | 64 per 12 month | 64 per 12 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '64 per 12 month' |
| 13635 | 47 per 7 month | 47 per 7 month | yes | final_label_repaired: 'unknown' -> '47 per 7 month'; evidence_not_text_contained |
| 13711 | 76 per 12 month | 76 per 12 month | yes | final_label_repaired: 'unknown' -> '76 per 12 month' |
| 13721 | 24 per 4 month | 77 per 12 month | yes | final_label_repaired: 'unknown' -> '24 per 4 month'; evidence_not_text_contained |
| 13732 | multiple per day | 52 per 8 month | no | final_label_repaired: 'unknown' -> 'multiple per day' |
| 13843 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13858 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13889 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13893 | 2 per year | 2 per year | yes | final_label_repaired: 'unknown' -> '2 per year'; evidence_not_text_contained |
| 13922 | unknown | unknown | yes |  |
| 14002 | multiple per day | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'multiple per day' |
| 14025 | unknown | unknown | yes |  |
| 14029 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 14040 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 14076 | unknown | unknown | yes |  |
| 14092 | 5 per month | unknown | no |  |
| 14096 | unknown | unknown | yes |  |
| 14137 | 3 to 4 per month | unknown | no |  |
| 14146 | unknown | unknown | yes |  |
| 14187 | seizure free for 6 month | 2 to 3 per month | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 14214 | seizure free for 6 month | 2 to 4 per month | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 14250 | seizure free for 6 month | 2 per month | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 14282 | seizure free for 6 month | multiple per month | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 14284 | seizure free for 6 month | 2 to 3 per month | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 14317 | seizure free for 2 month | 4 per 2 month | no | evidence_not_text_contained |
| 14332 | seizure free for 6 month | 5 per 2 month | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 14335 | seizure free for multiple year | 3 to 4 per 2 month | no | final_label_repaired: 'seizure free for 8 week' -> 'seizure free for multiple year' |
| 14383 | seizure free for 6 month | 3 to 4 per 3 month | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 14454 | seizure free for 6 month | 2 per 2 month | no | evidence_not_text_contained |
| 14524 | unknown | 2 per 6 month | no | json_dialect_repaired: python_literal |
| 14530 | unknown | 2 per 2 month | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 14540 | seizure free for 6 month | 2 per 8 month | no |  |
| 14562 | unknown | 3 per 6 month | no | evidence_not_text_contained |
| 14567 | unknown | 3 per 3 month | no | evidence_not_text_contained |
| 14581 | seizure free for 6 month | 2 per 3 month | no | json_dialect_repaired: python_literal |
| 14587 | unknown | 2 per 3 month | no | evidence_not_text_contained |
| 14592 | unknown | 3 per 5 month | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 14611 | seizure free for 6 month | 2 per 4 month | no |  |
| 14628 | unknown | 2 per 2 month | no | evidence_not_text_contained |
| 14635 | seizure free for 6 month | 5 per 4 month | no |  |
| 14645 | seizure free for 6 month | 2 per 6 month | no | evidence_not_text_contained |
| 14662 | unknown | 3 per 4 month | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 14672 | seizure free for 6 month | 3 per 8 month | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 14706 | no seizure frequency reference | 2 per 5 month | no | final_label_repaired: '2 over 5 months' -> 'no seizure frequency reference' |
| 14765 | seizure free for 1 month | 1 per month | no |  |
| 14806 | seizure free for 1 month | 1 per 2 month | no | json_dialect_repaired: python_literal |
| 14810 | seizure free for multiple year | 1 per month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 4 week' -> 'seizure free for multiple year' |
| 14821 | seizure free for multiple year | 1 per month | no | final_label_repaired: 'seizure free for 3 week' -> 'seizure free for multiple year' |
| 14872 | seizure free for multiple year | 1 per month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 2 week' -> 'seizure free for multiple year' |
| 14943 | seizure free for 6 month | 1 per 3 month | no |  |
| 14949 | 1 per month | 1 per month | yes |  |
| 14965 | unknown | 1 per 3 month | no |  |
| 14973 | unknown | 1 per month | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 15004 | seizure free for 6 month | 1 per 3 month | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 15012 | seizure free for 6 month | 1 per 2 month | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 15021 | 1 per 3 month | 1 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 3 months' -> '1 per 3 month' |
| 15029 | seizure free for 6 month | 1 per 3 month | no | json_dialect_repaired: python_literal |
| 15094 | unknown | 4 per 13 month | no | json_dialect_repaired: python_literal |
| 15108 | 2 to 3 per day | 3 to 4 per 15 month | no | json_dialect_repaired: python_literal |
| 15127 | unknown | 5 per 13 month | no | json_dialect_repaired: python_literal |
| 15129 | unknown | 4 per 15 month | no | evidence_not_text_contained |
| 15141 | unknown | 4 to 5 per 15 month | no |  |
| 15168 | unknown | multiple per 15 month | yes | json_dialect_repaired: python_literal |
| 15193 | unknown | multiple per 13 month | yes | json_dialect_repaired: python_literal |
| 15242 | unknown | multiple cluster per 15 month, multiple per cluster | no | evidence_not_text_contained |
| 15262 | unknown | multiple cluster per 13 month, multiple per cluster | no | json_dialect_repaired: python_literal |
| 15267 | unknown | 3 per 14 month | no | json_dialect_repaired: python_literal |
| 15306 | unknown | 2 to 3 per 15 month | no | json_dialect_repaired: python_literal |
| 15317 | 2 to 3 per month | 2 to 3 per 15 month | no |  |
| 15376 | 1 cluster per 2 week, 4 to 6 per cluster | 1 cluster per 2 week, 4 to 6 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 cluster per 2 week, 4 to 6 per cluster' |
| 15404 | unknown | 1 cluster per 4 month, 3 to 4 per cluster | no | json_dialect_repaired: python_literal |
| 15429 | unknown | 1 cluster per 2 month, 4 per cluster | no | json_dialect_repaired: python_literal |
| 15431 | unknown | 1 cluster per 4 month, 5 per cluster | no | json_dialect_repaired: python_literal |
| 15442 | 1 cluster per 4 day, 2 per cluster | 1 cluster per 4 day, 2 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 cluster per 4 day, 2 per cluster' |
| 15470 | unknown | 1 cluster per 5 day, multiple per cluster | no | evidence_not_text_contained |
| 15479 | 1 cluster per 4 to 5 day, 2 per cluster | 1 cluster per 4 to 5 day, 2 per cluster | yes | final_label_repaired: 'unknown' -> '1 cluster per 4 to 5 day, 2 per cluster' |
| 15497 | 1 cluster per 5 day, 5 per cluster | 1 cluster per 4 to 5 day, 5 per cluster | yes | final_label_repaired: 'unknown' -> '1 cluster per 5 day, 5 per cluster' |
| 15503 | 1 cluster per 5 day, 3 to 4 per cluster | 1 cluster per 5 day, 3 to 4 per cluster | yes | final_label_repaired: 'unknown' -> '1 cluster per 5 day, 3 to 4 per cluster' |
| 15513 | 1 cluster per 5 day, 2 to 3 per cluster | 1 cluster per 4 to 5 day, 2 to 3 per cluster | yes | final_label_repaired: 'unknown' -> '1 cluster per 5 day, 2 to 3 per cluster'; evidence_not_text_contained |
| 15519 | 1 cluster per 4 day, 3 per cluster | 1 cluster per 4 day, 3 per cluster | yes | final_label_repaired: 'unknown' -> '1 cluster per 4 day, 3 per cluster' |
| 15529 | 1 cluster per 3 day, 4 per cluster | 1 cluster per 3 day, 4 per cluster | yes | final_label_repaired: 'unknown' -> '1 cluster per 3 day, 4 per cluster' |
| 15593 | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | yes | final_label_repaired: 'unknown' -> '1 cluster per 5 day, 2 to 4 per cluster' |
| 15614 | 3 per week | 3 per week | yes |  |
| 15628 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal |
| 15639 | 2 per week | 2 per week | yes |  |
| 15642 | 2 to 4 per week | 2 to 4 per week | yes | json_dialect_repaired: python_literal |
| 15650 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 15672 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day' |
| 15697 | multiple per week | 1 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'multiple per week'; evidence_not_text_contained |
| 15715 | multiple per month | 1 per day | no | final_label_repaired: 'unknown' -> 'multiple per month' |
| 15745 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15766 | multiple per day | 4 per week | no |  |
| 15768 | 2 to 3 per week | 2 to 3 per week | yes | json_dialect_repaired: python_literal |
| 15771 | multiple per day | 3 per week | no | evidence_not_text_contained |
| 15772 | unknown | 2 per week | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 15774 | 2 per week | 2 per week | yes | json_dialect_repaired: python_literal |
| 15783 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15802 | 7 per week | 7 per week | yes | json_dialect_repaired: python_literal |
| 15831 | 2 to 4 per day | 2 to 4 per day | yes |  |
| 15834 | 5 per week | 5 per week | yes | json_dialect_repaired: python_literal |
| 15964 | 11 per 2 month | 11 per 3 month | no | final_label_repaired: '10 per 2 months' -> '11 per 2 month' |
| 15965 | 13 per 2 month | 13 per 2 month | yes | final_label_repaired: '10 per 2 months' -> '13 per 2 month' |
| 15966 | 5 per 2 month | 5 per 3 month | yes | final_label_repaired: '5 per month' -> '5 per 2 month' |
| 15982 | 8 per month | 9 per 2 month | yes |  |
| 15986 | 11 per 2 month | 11 per 3 month | no | final_label_repaired: 'unknown' -> '11 per 2 month' |
| 15992 | 7 per 2 month | 7 per 2 month | yes | final_label_repaired: '7 per month' -> '7 per 2 month' |
| 15997 | 10 per 2 month | 10 per 3 month | no | final_label_repaired: 'unknown' -> '10 per 2 month' |
| 16021 | 9 per 2 month | 9 per 3 month | no | final_label_repaired: '8 per 2 months' -> '9 per 2 month' |
| 16041 | 9 per 2 month | 9 per 3 month | no | final_label_repaired: '7 per month' -> '9 per 2 month' |
| 16084 | 8 per 4 month | 8 per 4 month | yes | final_label_repaired: 'unknown' -> '8 per 4 month' |
| 16091 | 3 per 3 month | 3 per 3 month | yes | final_label_repaired: '3 per month' -> '3 per 3 month' |
| 16097 | 17 per 4 month | 17 per 4 month | yes | final_label_repaired: 'unknown' -> '17 per 4 month' |
| 16107 | 8 per 3 month | 8 per 3 month | yes | final_label_repaired: '4 per month' -> '8 per 3 month' |
| 16108 | 12 per 4 month | 12 per 4 month | yes | final_label_repaired: '12 per month' -> '12 per 4 month' |
| 16132 | 13 per 2 month | 15 per 3 month | yes | final_label_repaired: '15 per month' -> '13 per 2 month'; evidence_not_text_contained |
| 16133 | 18 per 4 month | 18 per 4 month | yes | final_label_repaired: 'unknown' -> '18 per 4 month' |
| 16161 | 18 per 3 month | 18 per 3 month | yes | final_label_repaired: '11 per month' -> '18 per 3 month' |
| 16162 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '6 per month' -> '11 per 3 month' |
| 16181 |  | 15 per 4 month | no | invalid_json: Expecting ',' delimiter; evidence_not_text_contained |
| 16195 | 6 per month | 16 per 4 month | no |  |
| 16203 | 8 per 2 month | 9 per 3 month | no | final_label_repaired: '13 per month' -> '8 per 2 month' |
| 16204 | 5 per 3 month | 5 per 3 month | yes | final_label_repaired: '5 per month' -> '5 per 3 month'; evidence_not_text_contained |
| 16220 | seizure free for 1 month | 11 per 4 month | no | json_dialect_repaired: python_literal |
| 16324 | 7 per 2 month | 10 per 3 month | yes | final_label_repaired: '10 per month' -> '7 per 2 month' |
| 16335 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: 'unknown' -> '7 per 3 month'; evidence_not_text_contained |
| 16356 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: 'unknown' -> '1 per 4 day' |
| 16394 | 1 per 2 to 4 day | 1 per 2 to 4 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 per 2 to 4 day' |
| 16408 | 1 per day | 1 per 3 day | no | final_label_repaired: 'multiple per day' -> '1 per day' |
| 16429 | 1 per day | 1 per 2 to 3 day | no | final_label_repaired: 'multiple per day' -> '1 per day' |
| 16432 | 1 per day | 1 per 2 day | no | final_label_repaired: 'multiple per day' -> '1 per day' |
| 16450 | 1 per day | 1 per multiple day | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 per day' |
| 16529 | 1 per 5 day | 1 per 5 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 per 5 day' |
| 16557 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 per 2 to 3 day' |
| 16574 | 1 cluster per month, multiple per cluster | 1 per 4 day | no | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 cluster per month, multiple per cluster'; evidence_not_text_contained |
| 16590 | unknown | 1 per 4 to 5 day | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 16618 | unknown | 1 per 5 day | no | json_dialect_repaired: python_literal |
| 16645 | 4 per 2 month | 5 per 7 month | no | final_label_repaired: 'unknown' -> '4 per 2 month' |
| 16674 | unknown | 7 per 6 month | no | evidence_not_text_contained |
| 16685 | 9 per 2 month | 10 per 3 month | no | final_label_repaired: 'unknown' -> '9 per 2 month' |
| 16697 | 3 per month | 3 per 6 month | no |  |
| 16704 | unknown | 9 per 6 month | no | json_dialect_repaired: python_literal |
| 16714 | unknown | 5 per 6 month | no | evidence_not_text_contained |
| 16717 | 5 per 6 month | 5 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 per 6 months' -> '5 per 6 month'; evidence_not_text_contained |
| 16719 | unknown | 7 per 6 month | no | evidence_not_text_contained |
| 16728 | unknown | 4 per 6 month | no | evidence_not_text_contained |
| 16750 | seizure free for 6 month | 6 per 7 month | no |  |
| 16757 | unknown | 13 per 6 month | no | evidence_not_text_contained |
| 16758 | unknown | 9 per 5 month | no |  |
| 16772 | unknown | 9 per 5 month | no | evidence_not_text_contained |
| 16774 | unknown | 19 per 7 month | no |  |
| 16780 | unknown | 3 per 7 month | no | json_dialect_repaired: python_literal; evidence_not_text_contained |
| 16824 | 10 per 2 month | 11 per 5 month | no | final_label_repaired: 'unknown' -> '10 per 2 month' |
| 16833 | unknown | 8 per 6 month | no | evidence_not_text_contained |
| 16839 | unknown | 9 per 4 month | no | evidence_not_text_contained |
| 16867 | unknown | 6 per 7 month | no |  |
| 16907 | unknown | 9 per 6 month | no | evidence_not_text_contained |
| 16938 | 1 per 2 month | 2 per week | no | json_dialect_repaired: python_literal; final_label_repaired: '2 to 3 per month' -> '1 per 2 month' |
| 16947 | 1 per 2 month | 2 per week | no | json_dialect_repaired: python_literal; final_label_repaired: '2 per month' -> '1 per 2 month' |
| 16961 | 1 per 3 month | 2 per week | no | final_label_repaired: '1 per month' -> '1 per 3 month' |
| 16983 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 16990 | 4 to 5 per week | 4 to 5 per week | yes | json_dialect_repaired: python_literal |
| 17001 | 5 per week | 5 per week | yes |  |
| 17003 | 3 to 4 per month | 3 to 4 per month | yes | evidence_not_text_contained |
| 17110 | 4 to 5 per week | 4 to 5 cluster per week, multiple per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: '4 to 5 days per week' -> '4 to 5 per week' |
| 17135 | 1 cluster per month, multiple per cluster | 5 cluster per month, multiple per cluster | no | final_label_repaired: '5 per month' -> '1 cluster per month, multiple per cluster' |
| 17146 | multiple per week | 1 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> 'multiple per week' |
| 17167 | 1 per 6 month | 1 per week | no | final_label_repaired: '1 per 6 months' -> '1 per 6 month' |
| 17189 | 1 per 6 month | 1 per month | no |  |
| 17200 | 1 per 6 month | 1 per month | no | json_dialect_repaired: python_literal; final_label_repaired: '1 per 6 months' -> '1 per 6 month' |
| 17201 | 4 per month | 4 per month | yes |  |
| 17273 | 1 per 2 day | 1 per 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '0.5 per day' -> '1 per 2 day' |
| 17279 | 1 per 4 to 5 week | 1 per 4 to 5 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 4 to 5 weeks' -> '1 per 4 to 5 week' |
| 17287 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '1 per 1 to 2 day'; evidence_not_text_contained |
