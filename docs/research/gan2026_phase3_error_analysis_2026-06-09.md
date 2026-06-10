# Gan 2026 Phase 3 Error Analysis — gpt-4.1-mini validation750 (with deepseek and qwen comparisons)

**Date:** 2026-06-09 (extended 2026-06-09 with deepseek and qwen cross-model failure data)
**Scope:** Phase 1 validation750 results, four architectures, gpt-4.1-mini primary pass; deepseek and qwen failure profiles added for three LLM-only architectures (DL, CP, SE) — hybrid row-level data not available for deepseek/qwen without a separate deep-replay run.
**Purpose:** Evidence base for Phase 3 prompt-engineering decisions. Diagnosis only — no prompt changes recommended here.

See `docs/research/gan2026_cross_model_comparison_2026-06-09.md` for the full cross-model synthesis and discussion.

---

## 1. Summary Table

### 1a. gpt-4.1-mini (primary analysis model)

| Architecture | Family | Total | Rendered | Purist Correct | Purist Accuracy | Failures |
|---|---|---|---|---|---|---|
| llm_only_direct_labeler | fully-LLM | 750 | 750 | 564 | 75.20% | 186 |
| llm_only_canonical_pipeline | fully-LLM | 750 | 750 | 581 | 77.47% | 169 |
| hybrid_structured_events | **hybrid** (LLM-extract + det-normalize) | 750 | 748 | 661 | 88.37% | 89 |
| hybrid_live_candidate_sets | **hybrid** (det-candidates + LLM-assess) | 750 | 589 | 500 | 84.89% of rendered | 88 |

**Notes on hybrid:** 160 of 750 rows are abstained (null rendered label) by the deterministic downstream stages. Purist accuracy is 84.89% of the 589 rendered rows, corresponding to 66.67% of all 750 rows if abstentions count as wrong. The 88 failures are among rendered rows only.

**Note on SE architecture**: `hybrid_structured_events` is architecturally a hybrid, not a fully-LLM pipeline. Its LLM stage extracts structured events from raw text; the same deterministic normalize/project/render/score stages then process that output. SE's lower failure count relative to DL/CP is primarily explained by the deterministic normalization absorbing denominator and formatting errors — not by the LLM stage alone. The module has been renamed `hybrid_structured_events.py` to correct the original mislabeling.

### 1b. Cross-Model Purist Accuracy Summary

| Architecture | gpt-4.1-mini | deepseek-v4-flash | qwen3.6-35b |
|---|---|---|---|
| `llm_only_direct_labeler` | 564/750 (75.2%) | 558/750 (74.4%) | 550/749 (73.4%) |
| `llm_only_canonical_pipeline` | 581/750 (77.5%) | 565/750 (75.3%) | 544/748 (72.7%) |
| `hybrid_structured_events` | 661/748 (88.4%) | 609/742 (82.1%) | 624/746 (83.6%) |
| `hybrid` (rendered rows) | 500/589 (84.9%) | 490/604 (81.1%) | 291/400 (72.8%) |
| `hybrid` (rendered/total) | 589/750 | 604/750 | 400/750 |

### 1c. Cross-Model Failure Category Comparison (DL, CP: fully-LLM; SE: hybrid LLM-extract + det-normalize)

#### DL (llm_only_direct_labeler)

| Failure Category | gpt-4.1-mini | deepseek | qwen |
|---|---|---|---|
| `unknown_false_pos` | 59 | 68 | **91** |
| `freq_category_shift` | 53 | 53 | 55 |
| `seizure_free_false_pos` | 45 | **56** | 41 |
| `cluster_axis_error` | 7 | 0† | 0† |
| `unknown_false_neg` | 20 | 11 | 9 |
| `seizure_free_false_neg` | 2 | 4 | 3 |
| **Total failures** | **186** | **192** | **199** |

†deepseek and qwen cluster failures are absorbed into `unknown_false_pos` or `freq_category_shift` — these models rarely return a cluster-category label.

#### CP (llm_only_canonical_pipeline)

| Failure Category | gpt-4.1-mini | deepseek | qwen |
|---|---|---|---|
| `unknown_false_pos` | 35 | 81 | **92** |
| `freq_category_shift` | **64** | 42 | 63 |
| `seizure_free_false_pos` | 32 | **49** | 37 |
| `unknown_false_neg` | 23 | 11 | 10 |
| `cluster_axis_error` | 11 | 0† | 0† |
| `seizure_free_false_neg` | 4 | 2 | 2 |
| **Total failures** | **169** | **185** | **204** |

Key finding: for gpt-4.1-mini, CP guidance reduces `unknown_false_pos` vs DL (59→35, −24). For deepseek, it increases it (68→81, +13). For qwen, it barely changes it (91→92) while adding freq_category_shift errors. The guidance block helps gpt-4.1-mini but is neutral-to-harmful for qwen/deepseek on this axis.

#### SE (hybrid_structured_events)

| Failure Category | gpt-4.1-mini | deepseek | qwen |
|---|---|---|---|
| `freq_category_shift` | 26 | **44** | **45** |
| `unknown_false_pos` | **30** | 38 | 34 |
| `seizure_free_false_pos` | 5 | **26** | 23 |
| `unknown_false_neg` | 12 | 14 | 14 |
| `seizure_free_false_neg` | **9** | **11** | **6** |
| `parse_null` | 2 | 0 | 1 |
| **Total failures** | **89** | **133** | **122** |

SE failure profiles are more similar across models than DL/CP, but deepseek/qwen still have notably higher `seizure_free_false_pos` (26/23 vs 5 for gpt-4.1-mini) — the structured extractor's output is the same schema, but the LLM component within SE still shows model-dependent seizure-free over-triggering.

### Failure Category Summary (gpt-4.1-mini, count per architecture — preserved for primary analysis below)

| Failure Category | DL | CP | SE | HYB | Total |
|---|---|---|---|---|---|
| `freq_category_shift` | 53 | 64 | 26 | 42 | 185 |
| `unknown_false_pos` | 59 | 35 | 30 | 8 | 132 |
| `seizure_free_false_pos` | 45 | 32 | 5 | 15 | 97 |
| `unknown_false_neg` | 20 | 23 | 12 | 8 | 63 |
| `cluster_axis_error` | 7 | 11 | 5 | 11 | 34 |
| `seizure_free_false_neg` | 2 | 4 | 9 | 4 | 19 |
| `parse_null` | 0 | 0 | 2 | 0 | 2 |

**Category definitions used in this document:**
- `seizure_free_false_pos`: predicted `currently_no_seizure`; gold was not `currently_no_seizure`
- `seizure_free_false_neg`: gold was `currently_no_seizure`; predicted anything else
- `unknown_false_pos`: predicted `seizure_freq_unknown`; gold was an actual frequency category
- `unknown_false_neg`: gold was `seizure_freq_unknown`; predicted a specific frequency
- `cluster_axis_error`: at least one side of the transition involves a cluster label
- `freq_category_shift`: frequency rate predicted but mapped to wrong category (no cluster/seizure-free/unknown dimension)
- `parse_null`: null structured_record / schema validation error (SE only)

---

## 2. Per-Architecture Failure Breakdown

### 2.1 llm_only_direct_labeler (186 failures)

Every row rendered (750/750). Top failure modes:

- **unknown_false_pos (59):** Model applies `answer_kind=frequency` in rationale but the final_label still lands in the unknown category because the predicted monthly_frequency is undefined — OR the model genuinely emits `answer_kind=unknown` / `no_reference` when there is a real rate in the note.
- **freq_category_shift (53):** Model identifies the correct event but uses the wrong denominator window (raw multi-period count kept as-is) or picks the wrong seizure type when multiple coexist.
- **seizure_free_false_pos (45):** Model applies seizure-free to: (a) trigger-conditioned events where seizures only occur in a specific window, (b) notes that mention a recent seizure-free run following an earlier burst, and (c) proxy evidence (no rescue medication, no admissions).
- **unknown_false_neg (20):** Model converts an explicitly uncertain or single-event "unknown" into a concrete rate by computing count/window from context clues.
- **cluster_axis_error (7):** Drops cluster wrapper from the label when note uses cluster language but model converts to plain rate.

### 2.2 llm_only_canonical_pipeline (169 failures)

Every row rendered (750/750). The `guidance_for_tricky_cases` block changes the distribution but does not eliminate the major failure modes.

- **freq_category_shift (64):** *Higher count than DL.* The `concrete_frequency_precedence` guidance fires in 64 failures (27.8% failure rate among its firings). The rule correctly identifies a concrete fact but picks the wrong one — e.g., a lower-burden GTC "per week" count over a co-reported "daily drop attack."
- **unknown_false_pos (35):** *Lower than DL* — the guidance block suppresses some of DL's unknown over-triggering.
- **seizure_free_false_pos (32):** `seizure_free_conflict` fires in 29 failures with a 42.6% failure rate (highest of any rule). The rule's presence appears to sometimes *increase* willingness to label seizure-free because the model cites it even while still choosing seizure-free.
- **unknown_false_neg (23):** `denominator_window_mismatch` and `concrete_frequency_precedence` together drive most of these — model applies the rule to justify computing a rate from context clues.
- **cluster_axis_error (11):** `cluster_axis_ambiguity` fires in 13 failures (24.1% rate); `cluster_cadence_as_event_rate` in 3 (23.1%).

**Rule failure rates (fires in failure / total fires):**
- `seizure_free_conflict`: 42.6% — highest risk rule
- `same_window_additive_frequency`: 34.7%
- `denominator_window_mismatch`: 30.3%
- `concrete_frequency_precedence`: 27.8%
- `cluster_axis_ambiguity`: 24.1%
- `seizure_free_proxy_evidence_overreach`: 12.6% — low risk, applied correctly most often

### 2.3 hybrid_structured_events (89 failures, 2 parse nulls)

Structured event extraction + deterministic normalization reduces errors dramatically. Failure modes shift:

- **unknown_false_pos (30):** The structured extractor emits `kind=frequency_rate` but the normalizer cannot parse the vague phrase; or the extractor emits `kind=unknown_frequency` / `kind=last_event_only` when the note has a usable frequency fact.
- **freq_category_shift (26):** Normalizer correctly parses the event but the structured record selected the wrong primary event (lower burden over higher burden).
- **unknown_false_neg (12):** Structured record converts "3 events since June" into a concrete date-counted rate.
- **seizure_free_false_neg (9):** This is *SE's worst relative weakness*. The structured extractor emits `kind=last_event_only` or a frequency event instead of `kind=seizure_free`, even when the note states clear seizure freedom. 8 of these 9 cases are where DL/CP pass — a structured-extractor-specific failure pattern.
- **parse_null (2):** Schema validation errors (rows 694 and 2354); both are recoverable.

### 2.4 hybrid_live_candidate_sets (88 failures among 589 rendered)

Hybrid adds a deterministic CandidateSet upstream. The 160 abstentions (null rows) represent rows where no confident candidate was available.

- **freq_category_shift (42):** Dominant failure mode. LLM assessment identifies a plausible fact but the projection stage maps it to a wrong rate — often because the assessment picked a supporting/contextual candidate as primary, or because the burden phrase was off.
- **seizure_free_false_pos (15):** LLM assessment marks `assessment_kind=seizure_free` on notes with trigger-conditioned or proxy evidence.
- **cluster_axis_error (11):** Two distinct patterns: (a) hybrid-specific — assessment uses `cluster_frequency` kind for plain cadence notes (rows 187, 190, 5921 — gold is plain "1 per 7-9 day"), and (b) assessment uses `frequency_rate` for cluster notes but the projection drops the cluster structure.
- **unknown_false_neg (8):** Assessment emits `frequency_rate` on notes where gold is `unknown`.
- **unknown_false_pos (8):** Assessment emits `unknown_frequency` on notes with a valid rate.

---

## 3. Row-by-Row Failure Tables

### 3.1 Direct Labeler — Selected Failures (full table: 186 rows)

Representative rows by failure category:

| Row | Gold Category | Pred Category | Gold Label | Pred Label | FM Cat | Rationale (first 120 chars) |
|---|---|---|---|---|---|---|
| 816 | seizure_freq_1_per_mon | seizure_freq_more1per6mon_less1mon | 1 per month | 4 per year | freq_category_shift | The note states 'only four brief seizures recorded in 2017 so far' indicating a frequency of 4 seizures per year |
| 1317 | seizure_freq_unknown | seizure_freq_1ormore_daily | unknown, multiple per cluster | 1 cluster per day, multiple per cluster | unknown_false_neg | The note explicitly states a cluster of events over a single day with multiple short episodes |
| 3262 | seizure_freq_more1week_less1day | seizure_freq_1_per_week | 2 cluster per month, 5 per cluster | 2 cluster per month, multiple per cluster | cluster_axis_error | Note states two clusters per month each with approximately five absence seizures |
| 3371 | seizure_freq_unknown | currently_no_seizure | unknown | seizure free for multiple year | seizure_free_false_pos | Seizures only occur when significantly short on sleep; outside those nights no events in past eight weeks |
| 3469 | seizure_freq_unknown | currently_no_seizure | unknown | seizure free for 6 month | seizure_free_false_pos | Seizures occur only perimenstrually (days -3 to +3); outside this window no events over last six months |
| 4173 | seizure_freq_more1mon_less1week | seizure_freq_unknown | 1 per 2 week | no seizure frequency reference | unknown_false_pos | Note states patient experiences a typical spell roughly once in a fortnight |
| 4478 | seizure_freq_1ormore_daily | seizure_freq_unknown | 19 per week | no seizure frequency reference | unknown_false_pos | Note states nineteen episodes of status epilepticus in the past week |
| 5507 | seizure_freq_unknown | seizure_freq_more1per6mon_less1mon | unknown | 3 per 4 month | unknown_false_neg | Three separate occasions since June; note date 02 Oct, so window is about 4 months |
| 5534 | seizure_freq_unknown | seizure_freq_more1mon_less1week | 1 per multiple month | 1 per 2 week | unknown_false_neg | Single event occurred a fortnight ago; described as very infrequent and isolated |
| 5763 | seizure_freq_more1mon_less1week | seizure_freq_more1per6mon_less1mon | 2 per month | 2 per 3 month | freq_category_shift | Two GCs and four FIA episodes over three months |
| 5791 | seizure_freq_1_per_mon | seizure_freq_more1mon_less1week | 1 per month | 2 to 3 per month | freq_category_shift | Two myoclonic jerks and one GTC over past three months normalises to 2-3 per month |
| 5996 | seizure_freq_unknown | seizure_freq_more1week_less1day | unknown | 2 to 3 per week | unknown_false_neg | Clobazam used as needed max 2-3 nights per week — model read medication cadence as seizure rate |
| 11216 | seizure_freq_unknown | currently_no_seizure | unknown | seizure free for 4 month | seizure_free_false_pos | Last seizure 25 Dec 2023, no subsequent events to 27 Apr 2024 |
| 12537 | seizure_freq_1ormore_daily | seizure_freq_more1week_less1day | 1 per day | 3 per week | freq_category_shift | Up to 3 GTC per week cited as highest burden; daily drop attacks present but not selected |
| 14187 | seizure_freq_more1mon_less1week | currently_no_seizure | 2 to 3 per month | seizure free for multiple year | seizure_free_false_pos | Had 2-3 seizures shortly after stopping valproate but remained seizure-free since |
| 16938 | seizure_freq_more1week_less1day | seizure_freq_more1per6mon_less1mon | 2 per week | 1 per 2 month | freq_category_shift | Note says two GTC every 2 months; model keeps that denominator unchanged |
| 17110 | seizure_freq_more1week_less1day | seizure_freq_unknown | 4 to 5 cluster per week, multiple per cluster | unknown | unknown_false_pos | Note says 4-5 cluster days per week; model emits unknown despite explicit cluster cadence |

### 3.2 Canonical Pipeline — Selected Failures (full table: 169 rows)

| Row | Gold Category | Pred Category | Gold Label | Pred Label | FM Cat | Applied Rules |
|---|---|---|---|---|---|---|
| 816 | seizure_freq_1_per_mon | seizure_freq_more1per6mon_less1mon | 1 per month | 4 per year | freq_category_shift | concrete_frequency_precedence |
| 2992 | currently_no_seizure | seizure_freq_1_per_yr | seizure free for 7 month | 1 per 7 month | seizure_free_false_neg | denominator_window_mismatch, seizure_free_conflict |
| 3469 | seizure_freq_unknown | currently_no_seizure | unknown | seizure free for 6 month | seizure_free_false_pos | conditional_only_trigger |
| 3534 | seizure_freq_unknown | currently_no_seizure | unknown | seizure free for 7 month | seizure_free_false_pos | seizure_free_proxy_evidence_overreach |
| 4624 | seizure_freq_more1week_less1day | seizure_freq_more1mon_less1week | 1 per 3 to 4 day | 2 per month | freq_category_shift | concrete_frequency_precedence |
| 5507 | seizure_freq_unknown | seizure_freq_more1per6mon_less1mon | unknown | 3 per 4 month | unknown_false_neg | denominator_window_mismatch |
| 5763 | seizure_freq_more1mon_less1week | seizure_freq_more1per6mon_less1mon | 2 per month | 2 per 3 month | freq_category_shift | denominator_window_mismatch, same_window_additive_frequency |
| 5827 | seizure_freq_unknown | seizure_freq_more1mon_less1week | multiple per week | 2 to 3 per month | unknown_false_neg | concrete_frequency_precedence |
| 5837 | seizure_freq_more1week_less1day | seizure_freq_unknown | 2 cluster per 3 week, multiple per cluster | unknown | unknown_false_pos | same_window_additive_frequency |
| 6065 | seizure_freq_more1week_less1day | seizure_freq_1_per_week | 5 per month | 12 per 3 month | freq_category_shift | denominator_window_mismatch, concrete_frequency_precedence |
| 6094 | seizure_freq_more1mon_less1week | seizure_freq_more1week_less1day | 3 per month | 5 per month | freq_category_shift | dominant_vague_current_burden |
| 6571 | seizure_freq_unknown | currently_no_seizure | unknown | seizure free for 4 month | seizure_free_false_pos | seizure_free_conflict, seizure_free_proxy_evidence_overreach |
| 7167 | seizure_freq_more1week_less1day | seizure_freq_unknown | 1 cluster per 2 weeks, 2 to 4 per cluster | no seizure frequency reference | unknown_false_pos | cluster_axis_ambiguity |
| 9943 | seizure_freq_more1mon_less1week | seizure_freq_more1per6mon_less1mon | 1 cluster per 4 to 5 week, multiple per cluster | 1 per 4 to 5 week | cluster_axis_error | cluster_axis_ambiguity, unknown_cadence_cluster_burden |
| 10097 | seizure_freq_more1week_less1day | seizure_freq_more1mon_less1week | 3 cluster per month, multiple per cluster | 3 per month | cluster_axis_error | cluster_cadence_as_event_rate |
| 11216 | seizure_freq_unknown | currently_no_seizure | unknown | seizure free for 4 month | seizure_free_false_pos | seizure_free_conflict |
| 12537 | seizure_freq_1ormore_daily | seizure_freq_more1per6mon_less1mon | 1 per day | 3 per 6 month | freq_category_shift | concrete_frequency_precedence |
| 12502 | seizure_freq_1ormore_daily | seizure_freq_more1mon_less1week | 4 per day | 1 cluster per month, multiple per cluster | freq_category_shift | same_window_additive_frequency |

### 3.3 Structured Events — Selected Failures (full table: 89 rows, 2 parse nulls)

| Row | Gold Category | Pred Category | Gold Label | Pred Label | FM Cat | Notes |
|---|---|---|---|---|---|---|
| 694 | seizure_freq_more1week_less1day | — | 1 per week | NULL | parse_null | schema_validation_error: Field required |
| 2354 | seizure_freq_more1week_less1day | — | 6 to 7 per week | NULL | parse_null | schema_validation_error: invalid answer_kind enum |
| 1573 | seizure_freq_1ormore_daily | seizure_freq_unknown | 11 per week | — | unknown_false_pos | Events clustered over two consecutive mornings; extractor emitted unknown |
| 2459 | seizure_freq_more1week_less1day | seizure_freq_1_per_mon | 7 to 9 per 2 week | — | freq_category_shift | label_repaired twice; underlying normalizer chained error |
| 2932 | currently_no_seizure | seizure_freq_more1week_less1day | seizure free for 9 month | — | seizure_free_false_neg | Structured record has seizure_free event but normalizer mapped to no_reference |
| 2992 | currently_no_seizure | seizure_freq_1_per_yr | seizure free for 7 month | — | seizure_free_false_neg | Extractor emitted last_event_only kind, not seizure_free |
| 3015 | currently_no_seizure | seizure_freq_1_per_yr | seizure free for 12 month | — | seizure_free_false_neg | Extractor emitted last_event_only kind |
| 4839 | currently_no_seizure | seizure_freq_1ormore_daily | seizure free for multiple month | — | seizure_free_false_neg | Record has cluster event from late 2024 selected as primary |
| 5791 | seizure_freq_1_per_mon | seizure_freq_more1per6mon_less1mon | 1 per month | — | unknown_false_pos | Events clustering during sleep; extractor emitted unknown_frequency |
| 5837 | seizure_freq_more1week_less1day | seizure_freq_more1mon_less1week | 2 cluster per 3 week, multiple per cluster | — | cluster_axis_error | |
| 9943 | seizure_freq_more1mon_less1week | seizure_freq_more1per6mon_less1mon | 1 cluster per 4 to 5 week, multiple per cluster | — | cluster_axis_error | |
| 11216 | seizure_freq_unknown | currently_no_seizure | unknown | — | seizure_free_false_pos | Seizure freedom stated in plan but gold is unknown |

### 3.4 Hybrid — Selected Failures (full table: 88 rows among rendered)

| Row | Gold Category | Pred Category | Gold Label | Pred Label | FM Cat | Assessment Kind | Proj Basis |
|---|---|---|---|---|---|---|---|
| 187 | seizure_freq_more1mon_less1week | seizure_freq_more1week_less1day | 1 per 7 to 9 day | 1 cluster per 7 to 9 day, multiple per cluster | cluster_axis_error | cluster_frequency | cluster_cadence_without_size |
| 190 | seizure_freq_1_per_mon | seizure_freq_more1mon_less1week | 1 per 4 week | 1 cluster per 4 week, multiple per cluster | cluster_axis_error | cluster_frequency | cluster_cadence_without_size |
| 3753 | seizure_freq_1ormore_daily | seizure_freq_more1mon_less1week | 1 per day | 2 per month | freq_category_shift | frequency_rate | frequency_rate |
| 4771 | seizure_freq_unknown | seizure_freq_more1mon_less1week | unknown | 2 per 6 week | unknown_false_neg | frequency_rate | frequency_rate |
| 5791 | seizure_freq_1_per_mon | seizure_freq_more1per6mon_less1mon | 1 per month | 2 per 3 month | freq_category_shift | frequency_rate | additive_same_window |
| 5837 | seizure_freq_more1week_less1day | seizure_freq_more1mon_less1week | 2 cluster per 3 week, multiple per cluster | 1 per 3 week | cluster_axis_error | frequency_rate | frequency_rate |
| 6077 | seizure_freq_unknown | currently_no_seizure | unknown | seizure free for 8 month | seizure_free_false_pos | seizure_free | single_fact |
| 9955 | seizure_freq_more1week_less1day | seizure_freq_more1mon_less1week | 1 cluster per month, multiple per cluster | 1 per month | cluster_axis_error | frequency_rate | frequency_rate |
| 10237 | seizure_freq_more1week_less1day | seizure_freq_unknown | 4 cluster per month, multiple per cluster | unknown | unknown_false_pos | unknown_frequency | unknown_due_to_ambiguity |
| 10245 | seizure_freq_more1week_less1day | seizure_freq_unknown | 3 cluster per month, multiple per cluster | unknown | unknown_false_pos | unknown_frequency | primary_with_context |
| 10933 | seizure_freq_more1week_less1day | seizure_freq_more1per6mon_less1mon | 2 to 3 cluster per month, 5 per cluster | 2 per year | cluster_axis_error | frequency_rate | frequency_rate |
| 11216 | seizure_freq_unknown | currently_no_seizure | unknown | seizure free for 4 month | seizure_free_false_pos | seizure_free | single_fact |
| 12537 | seizure_freq_1ormore_daily | seizure_freq_more1week_less1day | 1 per day | 3 per week | freq_category_shift | frequency_rate | frequency_rate |
| 17110 | seizure_freq_more1week_less1day | seizure_freq_unknown | 4 to 5 cluster per week, multiple per cluster | multiple per day | unknown_false_pos | frequency_rate | frequency_rate |
| 17135 | seizure_freq_more1week_less1day | seizure_freq_1_per_yr | 5 cluster per month, multiple per cluster | 1 per year | cluster_axis_error | frequency_rate | frequency_rate |

---

## 4. Thematic Failure Catalogue

### FM-1: Denominator Window Preservation Failure

**Definition:** The model quotes a multi-period count and preserves the raw denominator (e.g., "4 in 2017," "2 events over 3 months," "3 occasions since June") rather than identifying that the gold answer uses the stated denominator as-given or normalises to the predominant reporting window. Two directions of error exist: (a) model preserves raw count + raw denominator as the label, resulting in a lower-frequency category than gold; (b) model normalises a stated multi-period rate to a shorter window, inflating the frequency.

**Affected rows (examples):**
- Row 816: note says "four brief seizures recorded in 2017 so far" → model emits "4 per year" (DL, CP). Gold is "1 per month" (note is from mid-2017; the correct read is that this is the recent monthly rate).
- Row 5763: note says "two GCs and ~four FIA episodes over the past three months" → model emits "2 per 3 month" (DL, CP). Gold is "2 per month" (gold annotator normalised the dominant count to the monthly window).
- Row 7475: note says "two GTC in the last six months" → model emits "2 per 2 month" (DL). Gold is "2 per 6 month."
- Row 7196: note says "4 FIA and 2 auras over six weeks" → model emits "4 to 6 per 6 week" (DL). Gold is "1 per week."
- Row 6065: note says "3 in July, 4 in August, 5 in September" → model emits "12 per 3 month" (CP). Gold is "5 per month" (the most recent month's count).

**Count per architecture:** DL: ~29 of 53 freq-shift failures; CP: ~37 of 64 freq-shift failures; HYB: ~22 of 42 freq-shift failures. SE: 0 (normaliser handles this separately).

**Note excerpt (row 816):** `...only four brief seizures recorded in 2017 so far. This improvement has continued...`

**Note excerpt (row 5763):** `...events have been occurring intermittently over the past three months, with two generalised convulsions and approximately four focal impaired-awareness episodes...`

**Prompt linkage:**
- DL: The instruction "Preserve explicit count-and-window labels when possible instead of converting a stated multi-period count to a vague monthly bucket" partially addresses this but the ambiguity about *which* window to use when multiple windows appear in the same note is not resolved.
- CP: The `denominator_window_mismatch` guidance says "keep the stated count and the stated time-window denominator paired exactly" — but this fires in 33 of 169 failures (30.3% failure rate), meaning the rule is being applied but the model still picks the wrong window when multiple are present. The `concrete_frequency_precedence` rule exacerbates this: in 64 failures, the model cites this rule to justify picking a recent multi-event count over a stated per-visit rate.
- Hybrid: The assessment picks the raw count/window from the CandidateSet; downstream projection preserves it literally.

**Proposed approaches:**
1. **Explicit "most recent window" instruction:** Add a tiebreaker rule: when a note contains both a long-window total (e.g., "6 over the last year") and a shorter recent count (e.g., "2 in the last month"), prefer the most recent window's rate as the primary label, and cite the longer-window total only in rationale.
   - *Pros:* Directly addresses the most common subtype (model preserves YTD total over recency-preferred window).
   - *Cons:* May introduce a "recency bias" that's wrong when the longer window is the stated clinical answer; some gold labels are explicitly multi-month.
2. **Window normalisation post-hoc instruction:** Instruct the model to express the rate in the denominator that appears *most frequently* in the note (not the largest denominator), avoiding the conversion from stated-per-visit to yearly.
   - *Pros:* Reduces YTD-preservation errors.
   - *Cons:* Adds complexity; "most frequent denominator" is ambiguous in notes that use mixed language.
3. **Few-shot or in-prompt example:** Provide a negative example where "4 in 2017 so far" should NOT yield "4 per year" but rather the per-month rate used in context.
   - *Pros:* Concrete and learnable for the model.
   - *Cons:* A single example may not generalise to the diversity of multi-window note patterns.

---

### FM-2: Seizure-Free False Positive — Active-Frequency Notes

**Definition:** The model returns a seizure-free label when the gold annotation is an active frequency. This occurs in two subtypes:

- **FM-2a: Trigger-conditioned seizures:** The note describes seizures that only occur in a specific context (perimenstrual, sleep-deprivation, missed medication, situational stress). The note often explicitly says "outside this window, seizure-free" or "no events when compliant." Gold label is `unknown` because the overall current seizure state is not expressed as a simple unconditional rate. Model focuses on the "outside window" seizure-free duration.
- **FM-2b: Recent-post-burst seizure-free:** The note describes a prior burst of seizures (e.g., 2-4 seizures shortly after stopping valproate, or 5 events in October) followed by a seizure-free run of a few weeks to months. Gold annotation uses the burst frequency as the label; model uses the current seizure-free duration.

**Count per architecture:** DL: 45 (19 FM-2a + 26 FM-2b); CP: 32 (similar split); SE: 5; HYB: 15.

**Representative examples:**

*FM-2a examples:*
- Row 3371 (DL, CP both): note says "seizures only when significantly short on sleep; outside of those nights, no events in the past eight weeks." DL pred: "seizure free for multiple year." Gold: "unknown."
  - Rationale: "...outside of nights with curtailed rest, no events have occurred in the past eight weeks."
- Row 3469 (all architectures except SE): "Seizures happen when perimenstrual only (days -3 to +3). Outside this window she and the group report no events over the last six months." DL pred: "seizure free for 6 month." Gold: "unknown."
- Row 3534 (CP, SE): "Uses buccal midazolam 10 mg as rescue, not required in the past seven months." CP applied `seizure_free_proxy_evidence_overreach` but still emitted "seizure free for 7 month."

*FM-2b examples:*
- Row 14187: note says "patient had 2-3 seizures shortly after stopping valproate but has remained seizure-free since." DL pred: "seizure free for multiple year." Gold: "2 to 3 per month."
- Row 14214: "two to four seizures around 27 November, then remained seizure-free since early December." CP pred: "seizure free for multiple year." Gold: "2 to 4 per month."
- Row 14332: "five seizures around early October, no further events since." DL pred: "seizure free for 2 month." Gold: "5 per 2 month."

**Prompt linkage:**
- DL: The instruction "Use seizure-free only when the note asserts no seizures/events for a current duration; do not use seizure-free for a single semiology if other current seizure-like events remain" only covers the multi-semiology case, not the trigger-conditional case or the post-burst case.
- CP: `seizure_free_conflict` rule (42.6% failure rate) is meant to block seizure-free when active evidence remains, but the model applies it and still chooses seizure-free in cases like row 11216 ("given seizure freedom since 25 December 2023" in the plan — model cites the rule but still emits seizure-free because the plan text is affirmative).
- CP: `conditional_only_trigger` rule correctly suppresses seizure-free in some cases (12.6% failure rate) but fails in 8 cases, typically when the note frames the conditional as fact ("outside this window she remains seizure-free").
- CP: `seizure_free_proxy_evidence_overreach` (12.6% failure rate) handles the proxy-evidence case well in most rows but fails when no-rescue language is combined with a general statement of better control.
- Hybrid: The assessment probe `seizure_free_only_outside_cyclic_risk_window` uncertainty flag is available but not triggered in the failing hybrid rows (flags are absent), suggesting the model is not recognising the pattern.

**Proposed approaches:**
1. **Explicit "recent burst then seizure-free" instruction:** Add a rule: if the note describes a burst (multiple events in a short window) followed by seizure-freedom, report the burst frequency as the label — not the current seizure-free duration — unless the seizure-free duration is clinically the focus (e.g., long-term remission clearly stated).
   - *Pros:* Directly targets FM-2b, which accounts for more than half of FM-2 failures.
   - *Cons:* Requires the model to judge "clinical focus" which is ambiguous.
2. **Conditional window instruction:** Explicitly state: "If seizure events are only described as occurring within a conditional window (perimenstrual, sleep-deprived, missed-medication), the outside-window seizure-free duration must NOT be reported as the overall current frequency; use `unknown` unless the note gives an unconditional current rate."
   - *Pros:* Directly targets FM-2a.
   - *Cons:* "Only occurring within a conditional window" may be hard for the model to distinguish from ordinary trigger-modified frequency.
3. **Post-burst gold anchor instruction:** "A seizure-free label is only appropriate when the most recent clinical statement is primarily about the ongoing absence of seizures — not when the most recent clinical event was the end of a seizure burst and the note documents that burst."
   - *Pros:* Can be stated concisely.
   - *Cons:* Adds another judgement call; may suppress legitimate short-remission seizure-free labels.

---

### FM-3: Unknown False Positive — Rate Misidentified as Unknown or No Reference

**Definition:** The note contains a usable, explicit, concrete seizure-frequency rate, but the model returns `unknown` or `no seizure frequency reference`. This is the second-largest failure mode for DL.

**Count per architecture:** DL: 59; CP: 35; SE: 30; HYB: 8. The large improvement from DL to SE suggests that structured event extraction resolves many of these.

**Subtypes:**
- **FM-3a: Misidentification of event type:** Model reads the note correctly but decides the event described is not a "seizure" (e.g., notes about status epilepticus, drop attacks, or non-convulsive seizures).
- **FM-3b: Multi-seizure-type uncertainty:** Note has multiple seizure types; model returns unknown instead of picking the highest burden.
- **FM-3c: Cluster complexity → unknown:** Note describes cluster pattern but model cannot resolve axis, returns unknown even when cadence is explicitly stated.
- **FM-3d: Answer_kind vs label mismatch:** Model's rationale correctly identifies the rate and emits `answer_kind=frequency`, but the final_label is still something that maps to the `seizure_freq_unknown` category (extremely rare).

**Representative examples:**
- Row 4478 (DL): "nineteen episodes of status epilepticus in the past week." DL pred: "no seizure frequency reference." Rationale: model explicitly stated this is a clear countable frequency but still emitted no_reference. (Likely a label normalization failure — "19 per week" may have been outside allowed forms.)
- Row 4173 (DL): "he tends to experience a spell roughly once in a fortnight — phrased it as about every second week." DL pred: "no seizure frequency reference." Rationale correctly describes the fortnightly rate, suggesting the final_label was malformed.
- Row 5837 (DL, CP, SE, HYB — universal): "two myoclonic clusters over the past three weeks and one GTC." DL pred: "unknown." The cluster complexity prevents resolution. Gold: "2 cluster per 3 week, multiple per cluster."
- Row 17110 (universal): "clusters of absence seizures on four to five days each week." DL pred: "unknown." Rationale: "patient has clusters of absence seizures on four to five days each week, which is a clear and countable frequency." — the model identified the frequency correctly in the rationale but still returned unknown.
- Row 10237, 10245 (universal): "cluster frequency unclear this month; last month ≈4 clusters / ≈3 clusters." All four architectures return unknown/no_reference. These are genuine gold annotation disputes: the note says frequency is unclear this month but was N last month; gold annotated with last-month value.

**Prompt linkage:**
- DL: Instruction "Use unknown when seizures or seizure-like events are discussed but current frequency cannot be converted to a normalized rate" does not distinguish between genuinely unresolvable cases and cases where the model fails to parse a stated rate.
- DL: No instruction distinguishes "rate stated but in an unfamiliar form" from "rate genuinely absent."
- CP: `cluster_axis_ambiguity` rule (24.1% failure rate) overgeneralises — it fires on rows where the cluster cadence IS clearly stated.
- Both: no explicit instruction on status epilepticus or drop attacks as seizure types with countable rates.

**Proposed approaches:**
1. **Explicit seizure-type inclusion list:** State explicitly that drop attacks, status epilepticus episodes, myoclonic jerks, absence episodes, and behavioural arrest events all count as seizure events for frequency purposes.
   - *Pros:* Addresses FM-3a directly.
   - *Cons:* Long list; may cause false inclusions of non-epileptic events.
2. **Cluster cadence render instruction:** Clarify: "If the note explicitly states how often clusters occur (e.g., 'clusters every 3-4 weeks', 'clusters on 4-5 days per week'), that cadence IS a usable frequency fact even if per-cluster event count is unknown — emit the cadence as the label and leave per-cluster count as 'multiple' unless stated."
   - *Pros:* Reduces FM-3c and cluster_axis_error.
   - *Cons:* Changes behaviour for ambiguous cluster cadences.
3. **Rationale-label consistency check instruction:** Add: "Before returning the final answer, verify that your rationale's described rate matches your final_label. If your rationale states a concrete rate, your final_label must not be 'unknown' or 'no seizure frequency reference.'"
   - *Pros:* Catches the rationale-label mismatch cases.
   - *Cons:* Relies on the model's self-consistency, which is imperfect; may not fix the deeper classification issue.

---

### FM-4: Unknown False Negative — Rate Invented from Context Clues

**Definition:** Gold annotation is `unknown` (or a label in the `seizure_freq_unknown` category), but the model computes a concrete rate from context clues that do not constitute a stated current rate. Mechanisms include: (a) counting events from narrative context clues ("three occasions since June" → "3 per 4 month"), (b) treating a single reported event as a recurrent rate, (c) treating medication cadence as seizure rate, (d) computing date math from "last event" and clinic date.

**Count per architecture:** DL: 20; CP: 23; SE: 12; HYB: 8.

**Representative examples:**
- Row 5507 (DL, CP both): "three separate occasions since June" (clinic date 02 Oct). DL: "3 per 4 month," CP: "3 per 4 month." Gold: "unknown." Note does not state ongoing recurrent frequency — these are episodic presentations, not a regular rate.
- Row 5534 (DL, CP): "very infrequent, short event a fortnight ago, the first in several months." DL: "1 per 2 week," CP: "1 per 2 month." Gold: "1 per multiple month" (unknown category). A single event a fortnight ago does not establish a recurrent fortnightly rate.
- Row 5996 (DL): "Clobazam used as needed for clusters, max 2-3 nights per week." DL: "2 to 3 per week." Gold: "unknown." This is medication cadence, not seizure rate — the model confused medication use frequency with event frequency.
- Row 1317 (DL): note describes "a cluster of events over a single day" — one cluster occurrence reported. DL: "1 cluster per day, multiple per cluster." Gold: "unknown, multiple per cluster." The single cluster event does not establish a daily cadence.
- Row 3371 (CP): "seizures only when significantly short on sleep; last event 10 September, no events in past 8 weeks." CP: "1 per 8 week." Gold: "unknown." The 8-week gap is the observation window since the last trigger-event, not a recurrent rate.

**Prompt linkage:**
- DL: Instruction "For trigger-conditioned or provoked-only events, report the stated frequency if countable; otherwise use unknown" does not handle the "single event in observation window" case or the "events since date X" case.
- CP: `denominator_window_mismatch` (30.3% failure rate) is meant to prevent date-math-inferred rates but is being applied to justify them instead: in row 5507, the model applies the rule to note that it is computing "3 per 4 months" from the date gap, not suppressing that computation.
- CP: `conditional_only_trigger` correctly handles some cases but misses the "8-week gap since last trigger-event" case.
- Neither DL nor CP: No explicit instruction stating "a single reported event within an observation window does not establish a recurrent rate."

**Proposed approaches:**
1. **Minimum recurrence requirement:** Add: "A concrete current seizure frequency requires at least two events in the stated window, OR an explicit statement from the note that events recur at that rate. A single event reported as happening 'N weeks ago' or 'N times since date X' does not establish a recurrent rate — use `unknown` unless recurrence is explicitly asserted."
   - *Pros:* Directly addresses the "single event → rate" class of errors.
   - *Cons:* May suppress valid single-event-per-long-window labels (e.g., "1 per 6 months" is a valid label in the schema).
2. **"Since date X" is not a rate instruction:** Add: "The phrase 'N events since [date]' or 'N occasions since [month]' only establishes a total count, not a current recurrent rate, unless the note explicitly frames it as the ongoing frequency. Report such counts using the full window as the denominator (e.g., '3 per 4 month'), not as a monthly rate."
   - *Pros:* Separates the denominator-preservation issue from the recurrence issue.
   - *Cons:* This is exactly what the model currently does — and it results in wrong multi-month denominators. This instruction may reinforce the wrong behaviour.
3. **Explicit unknown triggers:** State: "Use unknown when: (a) only one event has been reported in the observation window, (b) events occur only when triggered and no unconditional rate is given, (c) the note states frequency has changed or is unclear and no specific new rate is given."
   - *Pros:* Clear enumeration of unknown triggers.
   - *Cons:* May over-suppress legitimate rate labels.

---

### FM-5: Cluster Axis Error

**Definition:** The cluster structure of the label is wrong — either dropped (cluster label reduced to plain rate), incorrectly added (plain rate inflated to cluster label), or wrong axis (cadence vs burden vs per-cluster count mismatch).

**Subtypes:**
- **FM-5a: Cluster dropped → plain rate:** Note describes explicit cluster pattern (e.g., "nocturnal clusters 3×/month"), model emits plain rate ("3 per month"). Occurs in DL, CP, SE.
- **FM-5b: Plain rate inflated to cluster:** Note describes plain periodic events (e.g., "events every 4 weeks"), model emits cluster label ("1 cluster per 4 week, multiple per cluster"). Hybrid-specific pattern.
- **FM-5c: Cluster count precision error:** Note states "approximately five events per cluster," model emits "multiple per cluster." Row 3262 (DL, CP both).
- **FM-5d: Cluster cadence only, missing per-cluster count:** Note has explicit cadence but model drops the per-cluster count entirely.

**Count per architecture:** DL: 7; CP: 11; SE: 5; HYB: 11. Hybrid has the highest absolute cluster error count, driven by FM-5b (hybrid-specific CandidateSet promotion of cluster_frequency assessment kind).

**Representative examples:**
- Row 3262 (DL): "two clusters per month, each with approximately five absence seizures." DL: "2 cluster per month, multiple per cluster." Gold: "2 cluster per month, 5 per cluster." The "approximately five" is mappable to "5 per cluster" but model used "multiple."
- Row 10097 (DL, CP): "nocturnal clusters 3×/month." DL: "3 per month." CP: "3 per month." Gold: "3 cluster per month, multiple per cluster." Both architectures strip the cluster wrapper.
- Row 187 (Hybrid only): note says events cluster "every seven to nine days" — hybrid emits "1 cluster per 7 to 9 day, multiple per cluster." DL/CP/SE correctly emit "1 per 7 to 9 day." The CandidateSet has a `cluster_frequency` candidate (from the word "clustering" in the note) which the assessment probe promotes.
- Row 17110 (universal): "clusters of absence seizures on four to five days each week." DL/CP: "unknown." Hybrid: "multiple per day." Gold: "4 to 5 cluster per week, multiple per cluster." The note uses "cluster" as a modifier, not a standalone pattern.
- Row 9943 (DL, CP, SE, Hybrid — 3-of-4): "events tend to group together over several days in a repeating pattern roughly every 4-5 weeks." All architectures fail. DL: "1 per 4 to 5 week" (drops cluster). CP: same, applied `cluster_axis_ambiguity`. Gold: "1 cluster per 4 to 5 week, multiple per cluster."

**Prompt linkage:**
- DL: The instruction "For cluster labels, include both cluster rate and events per cluster when both are stated" exists but does not handle FM-5a (plain rate stripping) or FM-5b.
- CP: `cluster_cadence_as_event_rate` guidance (23.1% failure rate) is meant to convert cluster cadence to plain rate only when no per-cluster burden is stated — but it misfires in both directions (converting when it shouldn't; not converting when it should).
- CP: `unknown_cadence_cluster_burden` (15.3% failure rate) is applied in cases where the cadence IS stated, not just when it's absent.
- Hybrid: The assessment probe's `cluster_frequency` kind is over-selected by the LLM when the CandidateSet includes any candidate with "cluster" in its source phrase — even if the cluster language is incidental ("clustering" used as a descriptor, not a cluster-cadence statement).

**Proposed approaches:**
1. **Cluster indicator list:** Define explicitly what constitutes a "cluster" label: "Use a cluster label only when the note describes grouped multi-event episodes that recur as a distinct clinical unit (e.g., 'seizure clusters', 'cluster days', 'clusters of events'). Do not use cluster labels when a note merely says events 'tend to group' or 'cluster together' without describing them as a clinical cluster pattern."
   - *Pros:* Reduces FM-5b.
   - *Cons:* May suppress legitimate cluster labels where the language is soft.
2. **Cluster precision instruction:** "When the note states the approximate number of events per cluster (e.g., 'approximately 5', 'three to four events'), use that number in the per-cluster field rather than 'multiple'."
   - *Pros:* Addresses FM-5c directly.
   - *Cons:* Requires confidence threshold — "approximately" is not the same as "exactly."
3. **Cluster cadence-as-plain-rate gate:** Reinforce: "Convert a cluster cadence to a plain rate ONLY when the note contains no event-per-cluster information AND the word 'cluster' is not used as a clinical descriptor (e.g., 'nocturnal clusters', 'cluster days'). If 'cluster' is used as a clinical descriptor, preserve the cluster label structure."
   - *Pros:* Addresses the FM-5a/FM-5b asymmetry.
   - *Cons:* The "clinical descriptor" distinction is exactly what the model struggles with.

---

### FM-6: Highest-Seizure-Type Selection Failure

**Definition:** The note describes multiple concurrent seizure types, one of which is more frequent than others. The gold annotation selects the highest-frequency type. The model picks a lower-frequency type.

**Count per architecture:** Estimated DL: ~8-12; CP: ~8-12; HYB: ~6-8 (overlap with freq_category_shift). Most notable examples involve daily drop attacks co-reported with lower-frequency GTC seizures.

**Representative examples:**
- Rows 12537, 12556, 12562 (DL, CP, SE, HYB — all fail): Note says "up to 3 GTC per week; also has daily drop attacks." DL/CP/HYB: "3 per week" (picks GTC). Gold: "1 per day" (picks daily drop attacks as highest burden). Note text: `...he continues to have up to three generalised tonic-clonic seizures per week, rarely achieving more than ten consecutive seizure-free days. He also has daily drop attacks.`
- Row 12665 (universal): Note says "1-2 GTC per month" but also mentions daily events. DL: "1 to 2 per month." Gold: "1 per day."
- Row 4624 (CP): Note says "1 per 3 to 4 day" for primary burden but also mentions "two focal events in the past month." CP: "2 per month." Gold: "1 per 3 to 4 day." CP applied `concrete_frequency_precedence` and selected the more recent, more explicit count over the overall rate.
- Row 12502, 12506 (CP): Note has "1-2 GTC per month, 4 absences per day, clusters of myoclonic." CP returns "1 cluster per month, multiple per cluster" (highest by cluster reasoning). Gold: "4 per day" (absences daily are highest burden).

**Note excerpt (12537):** `...he continues to have up to three generalised tonic-clonic seizures per week, rarely achieving more than ten consecutive seizure-free days. He also has daily drop attacks. Furthermore, focal impaired-awareness seizures...`

**Prompt linkage:**
- DL: Instruction "select the highest current seizure burden across seizure types" should handle this, but fails here because the model ranks GTC as the most clinically significant type, not daily drop attacks (which are higher frequency).
- CP: `dominant_vague_current_burden` guidance (17.7% failure rate) is a selection preference for high-frequency vague burdens over low-frequency concrete burdens. In the drop-attack cases, the opposite is needed.
- Both: Neither prompt explicitly states that "daily" or "multiple per day" events take precedence over lower-frequency event types regardless of seizure type severity.

**Proposed approaches:**
1. **Frequency-based priority over seizure-type severity:** Explicitly state: "When selecting the highest burden, use frequency (events per day/week) as the primary ranking criterion, not clinical severity. A daily drop attack takes precedence over a weekly GTC seizure for frequency labelling."
   - *Pros:* Directly addresses the ranking failure.
   - *Cons:* This is a gold annotation convention, not universal clinical practice; may confuse the model in contexts where clinical severity is genuinely the labelling intent.
2. **Explicit drop-attack / absence example:** Provide a concrete example: "If the note describes daily absence seizures and monthly convulsive seizures, the label is 'multiple per day' (or '1 per day'), not the convulsive frequency."
   - *Pros:* Very learnable from an in-context example.
   - *Cons:* Narrow; may not generalise to other seizure type combinations.

---

### FM-7: Seizure-Free False Negative

**Definition:** Gold annotation is seizure-free (currently_no_seizure category), but the model returns a non-seizure-free label. Less common but architecturally revealing.

**Count per architecture:** DL: 2; CP: 4; SE: 9; HYB: 4. SE has the highest count — a structured-extractor-specific failure.

**SE-specific pattern:** The structured event extractor emits `kind=last_event_only` or `kind=frequency_rate` instead of `kind=seizure_free` when the note describes the absence of seizures primarily through a "last event on date X" framing. In rows 2992 and 3015, the note says "his last seizure on 19-May-2024... no further events since" but the structured extractor captures this as `last_event_only` evidence, not a `seizure_free` state event. The downstream normalizer then fails to convert this to a seizure-free label.

**Representative examples:**
- Row 2992 (CP, SE): "last seizure on 19-May-2024; no further events since to clinic date 22 December 2024 (7 months)." CP: "1 per 7 month" (applied `seizure_free_conflict`, `denominator_window_mismatch`). SE: missed seizure-free entirely.
- Row 8400 (DL, CP both): "durable seizure control over past several months, with no convulsive events and only occasional brief warning episodes that do not progress." DL: "no seizure frequency reference." CP: "no seizure frequency reference" (applied `seizure_free_proxy_evidence_overreach`). Gold: "seizure free for multiple month." Model treated warning episodes as evidence of seizures, failing to recognise the overall seizure-free claim.

**Prompt linkage:**
- DL/CP: `seizure_free_proxy_evidence_overreach` rule is overapplied here — the gold note has an explicit seizure-free claim, not merely proxy evidence, but the model is using the rule to justify rejecting the claim because warning episodes exist.
- SE: The structured extractor's event schema has `kind=last_event_only` which the normalizer cannot map to seizure-free. No instruction in the assessment probe covers the "last event" → implicit-seizure-free inference.

**Proposed approaches:**
1. **"Last event + no events since" = seizure-free instruction:** Add to DL/CP: "If the note states the date of the last seizure and asserts no further events since that date, this constitutes a seizure-free duration claim — use seizure-free with the computed duration even if the note does not use the words 'seizure free.'"
   - *Pros:* Directly fixes the CP row 2992 pattern.
   - *Cons:* May over-trigger seizure-free on notes with single events in otherwise active patients.
2. **Warning episodes do not block seizure-free:** Add: "Aura, prodrome, or brief warning sensations that do not progress to a full clinical event do not constitute 'current seizures' for seizure-free determination. A patient with warnings but no events can be labelled as seizure-free."
   - *Pros:* Fixes the row 8400 pattern.
   - *Cons:* May suppress legitimate cases where warnings are the primary seizure burden.
3. **SE: seizure_free event kind for "last event only" with date gap:** Instruct the structured extractor to emit `kind=seizure_free` (not `kind=last_event_only`) whenever the note asserts no subsequent events after a stated last-seizure date.
   - *Pros:* Fixes the SE-specific pattern.
   - *Cons:* Changes SE extractor schema; requires a new structured event kind or disambiguation logic.

---

### FM-8: Frequency Category Shift — Adjacent Category (Non-Denominator)

**Definition:** Frequency is correctly identified as a rate (not cluster/unknown/seizure-free), but the output category is wrong by one or two adjacent bins. Does not fit the denominator-conversion pattern.

**Count per architecture:** DL: ~24 of 53 freq-shift; CP: ~27 of 64; HYB: ~20 of 42.

**Subtypes:**
- Over-counting: model uses additive logic to sum across seizure types when gold uses a single-type rate. Example: row 5791, note has "two myoclonic jerks and one GTC over three months" — model gives "2 to 3 per month" (arithmetic of 3/3); gold is "1 per month" (GTC only, monthly rate).
- Under-counting: model selects a conservative lower-frequency estimate when the note's primary statement gives a higher rate.
- Recent-period vs representative-period mismatch: notes with variable monthly counts (e.g., 3, 4, 5 across three months) — model picks the total, gold picks the most recent month.

**Representative examples:**
- Row 5791 (DL, CP, SE, HYB): "two myoclonic jerks on awakening and one GTC over past three months." DL: "2 to 3 per month" (arithmetic). Gold: "1 per month." Hybrid: "2 per 3 month." SE: uses additive. CP: applies `same_window_additive_frequency`.
- Row 6094 (CP, HYB): "five seizure events over approximately one month." CP: "5 per month." Gold: "3 per month" (gold uses an earlier stated frequency of 3 per month). Hybrid: "3 per week."
- Row 6065 (DL, CP): monthly counts given as 3, 4, 5 — model: "3 to 5 per month" (DL) or "12 per 3 month" (CP). Gold: "5 per month" (most recent month).

**Prompt linkage:**
- CP: `same_window_additive_frequency` (34.7% failure rate) is the highest-risk guidance note. When applied, the model often adds seizure types that the gold annotator considered separately.
- DL: The instruction "If several current seizure types are present, select the highest current seizure burden across seizure types" conflicts with the additive summing behaviour. The two instructions (select highest vs sum same-window) are not clearly prioritised.

**Proposed approaches:**
1. **Clarify additive vs selection priority:** Provide explicit guidance: "Sum same-window seizure counts ONLY when the note gives an explicit combined total or when the note clearly asks you to add (e.g., 'patient had X+Y seizures in total'). When the note lists each type separately, use the type with the highest frequency as the label, not the sum."
   - *Pros:* Reduces `same_window_additive_frequency` over-application.
   - *Cons:* May reduce precision on genuinely additive cases.
2. **Most recent period over cumulative period:** Add: "When the note provides monthly counts for several consecutive months, use the most recent month's count as the primary label, not the average or total."
   - *Pros:* Addresses the variable-monthly-count subtype.
   - *Cons:* May conflict with notes where the most recent month is atypically low.

---

## 5. Cross-Architecture Pattern Analysis

### 5.1 Universal Failures (all 4 architectures fail, gpt-4.1-mini)

20 rows fail in all four architectures. These represent genuinely hard annotation cases or systematic prompt/representation gaps.

Key universal failure types:
- **Rows 10237, 10245** (FM-3c + unknown_false_pos): Both notes explicitly say "cluster frequency unclear this month; last month ≈N clusters." Gold uses last month's count. All models use `unknown` because "unclear this month" dominates. This may be a gold annotation policy question: the gold annotator applies the most recent definite count; no architecture applies this policy. **qwen and deepseek also fail on row 10237 (all three → unknown).**
- **Rows 17110, 17135** (cluster axis): "Clusters of absence seizures on N days per week/month." All models fail to render the cluster label — either returning unknown or using plain rate.
- **Rows 12537, 12556, 12562, 12665** (FM-6 / highest burden selection): All gpt-4.1-mini architectures pick the GTC rate over the daily drop-attack rate. **This is a gpt-4.1-mini-specific failure**: qwen DL and CP correctly return "1 per day" for rows 12537 and 12556 (deepseek DL also correct for those two). This means FM-6 is not a universal model failure — gpt-4.1-mini has a specific bias toward clinical severity over frequency ranking that qwen and deepseek do not share. The v0.5 FM-6 fix primarily benefits gpt-4.1-mini.
- **Rows 16938, 16947, 16961** (FM-1 / denominator preservation): All architectures anchor on the GTC rate and miss the higher-frequency absence seizure. **qwen also fails on row 16938** (DL, CP, SE all return freq_category_shift).
- **Rows 11216, 11272** (FM-2a / seizure-free false pos): All architectures return seizure-free for notes where gold is `unknown`. **qwen DL, CP, SE all fail on both rows** (same pattern).
- **Row 5837** (cluster axis): All fail to render "2 cluster per 3 week, multiple per cluster." **qwen DL and CP return unknown; qwen SE also returns unknown** — universal failure confirmed across models.
- **Row 7195** (unknown_false_neg): Note has "a spike around childbirth but frequency settled back to baseline, only one possible brief event last month." All gpt-4.1-mini architectures emit "1 per month." **qwen DL, CP, SE all emit "1 per month"** — also a universal failure across models.

### 5.2 Architecture-Specific Failures

- **DL-specific (23 rows):** Mostly `seizure_free_false_pos` (8) and `unknown_false_neg` (6). DL lacks the `guidance_for_tricky_cases` block, so it over-triggers seizure-free on trigger-conditioned and post-burst notes more than CP. Also over-computes rates from context clues without the denominator_window_mismatch rule to slow it down.
- **CP-specific (16 rows):** Mostly `unknown_false_neg` (7). The `concrete_frequency_precedence` and `denominator_window_mismatch` rules appear to drive the model to compute rates more aggressively than DL — in cases where DL returns `unknown`, CP invents a rate. The guidance block paradoxically increases the model's confidence in rate computation.
- **SE-specific (23 rows):** Mostly `seizure_free_false_neg` (7) and `unknown_false_pos` (6). SE's structured extractor has a systematic gap around `seizure_free` kind: it uses `last_event_only` for notes describing absence-of-seizures via a last-event date, and this kind cannot be normalised to seizure-free. SE also fails on notes where the frequency fact is embedded in clinical context rather than stated explicitly (the extractor requires an event with a parseable `raw_value`).
- **Hybrid-specific (27 rows):** Mostly `freq_category_shift` (11) and `cluster_axis_error` (8). The hybrid's cluster_frequency assessment kind is over-promoted by the LLM assessor when CandidateSets contain any candidate with cluster language — including notes where the word "clustering" is incidental. This creates the FM-5b pattern (plain rate inflated to cluster label).

### 5.3 What DL fails that CP corrects

CP corrects 38 rows that DL fails. Breakdown of what CP fixed:
- `unknown_false_pos`: 14 rows — CP's guidance block suppresses the over-triggering of unknown/no-reference.
- `seizure_free_false_pos`: 9 rows — CP's `conditional_only_trigger` and `seizure_free_conflict` rules suppress some trigger-conditioned false positives.
- `unknown_false_neg`: 8 rows — partially, CP's guidance restrains some rate-invention cases.
- `freq_category_shift`: 6 rows.

What CP makes worse vs DL: CP has 64 `freq_category_shift` failures vs DL's 53 — the guidance block adds 11 extra frequency category errors, driven largely by `concrete_frequency_precedence` misapplication.

### 5.4 What structured_events corrects vs direct_labeler

SE corrects 125 rows that DL fails. Breakdown:
- `freq_category_shift`: 39 — the deterministic normaliser handles many denominator and window errors.
- `seizure_free_false_pos`: 35 — the structured event schema forces the model to commit to an event type; the `seizure_free` kind requires explicit seizure-free evidence.
- `unknown_false_pos`: 29 — structured extraction requires a parseable event; notes without clear frequency evidence return null rather than unknown.
- `unknown_false_neg`: 17 — extraction of explicit event attributes constrains rate invention.

SE introduces 9 `seizure_free_false_neg` failures not in DL (the `last_event_only` kind gap). SE also introduces 23 SE-specific failures.

### 5.5 Hybrid vs SE

Hybrid has 88 failures (among 589 rendered) vs SE's 89 (among 748 rendered). The raw counts are similar but hybrid's rendered rate is much lower (78.5% vs 99.7%). Among failures, hybrid has more `cluster_axis_error` (11 vs 5) and more `freq_category_shift` (42 vs 26) — the LLM assessment stage introduces errors that the structured SE extractor avoids. Hybrid's advantage is primarily in its abstention behaviour (not rendering when uncertain), which trades recall for precision.

---

## 6. Prompt Linkage Summary

| Failure Mode | DL Instruction Gap / Issue | CP Rule Gap / Issue | SE Instruction Gap | Hybrid Instruction Gap |
|---|---|---|---|---|
| FM-1 (Denominator) | "Preserve explicit count-and-window" does not specify which window when multiple coexist | `denominator_window_mismatch` fires but model computes rates anyway; `concrete_frequency_precedence` reinforces the behaviour | N/A (normalizer handles) | Assessment picks raw count from CandidateSet |
| FM-2a (Trigger-conditioned SF) | No instruction for conditional/outside-window seizure-free | `conditional_only_trigger` (12.6% failure rate) insufficient | N/A | uncertainty flag `seizure_free_only_outside_cyclic_risk_window` not reliably fired |
| FM-2b (Post-burst SF) | No instruction distinguishing recent seizure burst + current SF | No rule covers this pattern | N/A | No rule covers this pattern |
| FM-3 (Unknown FP) | No distinction between "unfamiliar rate form" and "genuinely absent rate" | `cluster_axis_ambiguity` overgeneralises | `last_event_only` kind inadequately mapped | Assessment over-selects unknown_frequency kind |
| FM-4 (Unknown FN) | "Trigger-conditioned: report frequency if countable" is too permissive | `denominator_window_mismatch` justifies rate computation; `concrete_frequency_precedence` reinforces | Extractor computes rates from event dates | Assessment emits frequency_rate for single-event notes |
| FM-5 (Cluster axis) | "Include both cluster rate and events per cluster when both stated" does not handle plain-rate promotion or FM-5b | `cluster_axis_ambiguity` over-fires; `cluster_cadence_as_event_rate` is directionally correct but mis-scoped | No cluster-vs-plain distinction | Assessment over-selects cluster_frequency kind |
| FM-6 (Highest type) | "Select highest burden" does not specify frequency-based ranking over clinical severity | `concrete_frequency_precedence` often selects lower-frequency event over higher-frequency type | N/A | Assessment anchors on GTC-type candidates |
| FM-7 (SF FN) | `seizure_free_proxy_evidence_overreach` over-applied to explicit SF claims | Same | `last_event_only` kind not mapped to seizure_free | No SF-inferencing from last-event candidates |

---

## 7. Priority Ranking by Improvement Potential

Ranking is based on: (a) failure count across architectures, (b) uniqueness to LLM stages (vs inherent annotation difficulty), (c) tractability of a prompt fix.

| Rank | Failure Mode | Total Failures | DL+CP Improvable | Tractability | Priority |
|---|---|---|---|---|---|
| 1 | FM-2 (Seizure-free FP, both subtypes) | 97 | High | Medium | **Highest** — 45+32=77 in DL+CP; FM-2b has a clear instruction fix |
| 2 | FM-1 (Denominator window) | 185 (subset) | High (~66) | Medium | **High** — "most recent window" rule would fix a large fraction |
| 3 | FM-3 (Unknown FP) | 132 | Medium (94) | Medium | **High** — cluster clarity instructions + type list |
| 4 | FM-6 (Highest type selection) | ~25 | High | Medium | **High** — frequency-ranking instruction is concrete; fixes universal failures |
| 5 | FM-4 (Unknown FN / rate invention) | 63 | Medium (43) | Medium | **Medium** — minimum-recurrence instruction helps but has edge cases |
| 6 | FM-5 (Cluster axis) | 34 | Medium (18) | Low-Medium | **Medium** — cluster label rules are complex; gains may be smaller |
| 7 | FM-8 (Freq shift, adjacent) | ~51 | Medium | Low | **Low** — many cases are genuine annotation ambiguity |
| 8 | FM-7 (SF FN) | 19 | Low-Medium | Low-Medium | **Lower** — small count; SE-specific fix needed separately |

**Note on universal failures:** 20 rows fail in all 4 architectures. Of these, ~8 are likely genuine gold annotation disputes or hard clinical notes. The remaining ~12 have a tractable instruction fix (FM-6 drop-attack ranking, FM-2b post-burst, FM-1 recency preference).

---

## Appendix A: Key Note Excerpts for Universal Failures

**Rows 12537/12556/12562 (FM-6 — drop attacks):**  
`...he continues to have up to three generalised tonic-clonic seizures per week, rarely achieving more than ten consecutive seizure-free days. He also has daily drop attacks. Furthermore, focal impaired-awareness seizures...`  
Gold: "1 per day." All models: "3 per week" or "2-3 per week."

**Rows 16938/16947/16961 (FM-1 — denominator with co-reported absence seizures):**  
Row 16938: `...she experiences two generalised tonic-clonic seizures every 2 months. Absence seizures remain infrequent, usually no more than twice weekly...`  
Gold: "2 per week" (the absence seizures, not the GTC). All models: "1 per 2 month" or similar GTC rate.

**Rows 10237/10245 (FM-3c — cluster frequency unclear this month):**  
Row 10237: `...Cluster frequency unclear this month; last month ≈4 clusters. The patient reports increased occupational stress...`  
Gold: "4 cluster per month, multiple per cluster" (uses last month's count). All models: "unknown."

**Rows 11216/11272 (FM-2a — seizure-free in plan section):**  
Row 11216: `...continue current anti-seizure medications unchanged for now given seizure freedom since 25 December 2023 and good tolerability...`  
Gold: "unknown." All models: "seizure free for 4 month."

**Row 5837 (FM-5/FM-3 — myoclonic cluster + GTC):**  
`...he reports an increase in brief absence episodes and two myoclonic clusters over the past three weeks...`  
Gold: "2 cluster per 3 week, multiple per cluster." DL: "unknown." CP: "unknown." SE: no label. HYB: "1 per 3 week."

---

## Appendix B: Structured Events Architecture — Seizure-Free Kind Gap

The SE extractor's event schema includes `kind=last_event_only` which is used when the note describes the last seizure date but does not use explicit seizure-free language. In 7 of 9 SE-specific seizure_free_false_neg failures, the structured record contains a `kind=last_event_only` or `kind=frequency_rate` event instead of `kind=seizure_free`. Example (row 2992):

```json
{"event_id": "e1", "kind": "last_event_only", "evidence": "his last seizure on 19-May-2024...", ...}
```

This event kind normalises to `unknown` rather than `seizure free for N month`. The gap is: no downstream rule converts a `last_event_only` event plus an observation window into a seizure-free duration.

---

## Appendix C: Canonical Pipeline Rule Performance

| Rule | Total Fires | Success | Fail | Fail Rate |
|---|---|---|---|---|
| seizure_free_conflict | 68 | 39 | 29 | 42.6% |
| same_window_additive_frequency | 49 | 32 | 17 | 34.7% |
| denominator_window_mismatch | 109 | 76 | 33 | 30.3% |
| concrete_frequency_precedence | 230 | 166 | 64 | 27.8% |
| cluster_axis_ambiguity | 54 | 41 | 13 | 24.1% |
| cluster_cadence_as_event_rate | 13 | 10 | 3 | 23.1% |
| conditional_only_trigger and relative_only_trend | 4 | 3 | 1 | 25.0% |
| dominant_vague_current_burden | 85 | 70 | 15 | 17.6% |
| unknown_cadence_cluster_burden | 59 | 50 | 9 | 15.3% |
| conditional_only_trigger | 63 | 55 | 8 | 12.7% |
| seizure_free_proxy_evidence_overreach | 111 | 97 | 14 | 12.6% |
| medication_cadence_ambiguity | 2 | 2 | 0 | 0.0% |

High failure-rate rules (>25%) represent guidance that the model applies but misapplies more than one in four times: `seizure_free_conflict`, `same_window_additive_frequency`, `denominator_window_mismatch`, `concrete_frequency_precedence`. These four rules account for 143 of 169 CP failures where a rule was applied.
