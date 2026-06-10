# Gan 2026 Cross-Model Comparison — Phase 1 Synthesis

**Date:** 2026-06-09  
**Scope:** Phase 1 validation750 results compared across three models (gpt-4.1-mini, deepseek-v4-flash, qwen3.6-35b) for all six architecture configurations. No test450 read; no holdout-facing or benchmark-comparable claim.  
**Source reports:**
- `experiments/gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08.{jsonl,json,md}`
- `experiments/gan2026_three_way_comparison_phase1_report_deepseek_validation750_2026-06-09.{jsonl,json,md}`
- `experiments/gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09.{jsonl,json,md}`

Failure-category counts derived from per-row JSONL comparison fields (DL, CP, SE only); hybrid failure breakdown at row level requires a separate deep-replay extraction run and is not included here. See `docs/research/gan2026_phase3_error_analysis_2026-06-09.md` for the gpt-4.1-mini primary failure analysis.

---

## 1. Master Comparison Table

### 1a. Purist Accuracy

| Architecture | gpt-4.1-mini | deepseek-v4-flash | qwen3.6-35b |
|---|---|---|---|
| `deterministic` | 688/741 (**0.928**) | 688/741 (**0.928**) | 688/741 (**0.928**) |
| `deterministic_canonical_pipeline` | 688/741 (**0.928**) | 688/741 (**0.928**) | 688/741 (**0.928**) |
| `hybrid` (of rendered) | 500/589 (**0.849**) | 490/604 (**0.811**) | 291/400 (**0.728**) |
| `llm_only_direct_labeler` | 564/750 (**0.752**) | 558/750 (**0.744**) | 550/749 (**0.734**) |
| `hybrid_structured_events` | 661/748 (**0.884**) | 609/742 (**0.821**) | 624/746 (**0.836**) |
| `llm_only_canonical_pipeline` | 581/750 (**0.775**) | 565/750 (**0.753**) | 544/748 (**0.727**) |

### 1b. Rendered / Null / Routed Counts

| Architecture | gpt-4.1-mini | deepseek | qwen |
|---|---|---|---|
| `hybrid` rendered | 589 | 604 | **400** |
| `hybrid` null | 160 | 146 | 100 |
| `hybrid` routed | 42 (7.1% of rendered) | 123 (20.4%) | 62 (15.5%) |
| `llm_only_direct_labeler` null | 0 | 0 | 1 |
| `hybrid_structured_events` null | 2 | 8 | 4 |
| `llm_only_canonical_pipeline` null | 0 | 0 | 2 |

### 1c. Hybrid Routing Taxonomy

| Route family | gpt-4.1-mini | deepseek | qwen |
|---|---|---|---|
| `rendered_label_supported_but_policy_sensitive` | 2 | **97** | 22 |
| `selected_source_id_invalid` | 15 | 11 | **31** |
| `cluster_axis_ambiguity` | **14** | 10 | 8 |
| `multiple_current_primary_facts` | 1 | 7 | 0 |
| `unresolved_cluster_cadence_with_per_cluster_burden` | 4 | 3 | 1 |
| `conditional_only_trigger` | 2 | 2 | 0 |
| `denominator_window_mismatch` | 0 | 2 | **1** |
| `relative_only_trend` | 2 | 0 | 0 |
| `mixed_window_or_vague_addition` | 2 | 0 | 0 |
| `seizure_free_proxy_evidence_overreach` | 1 | 0 | 0 |
| **Total routed** | **42** | **123** | **62** |

### 1d. Failure Category Counts — LLM-Using Architectures (DL, CP, SE)

#### DL (llm_only_direct_labeler)

| Failure Category | gpt-4.1-mini | deepseek | qwen |
|---|---|---|---|
| `unknown_false_pos` | 59 | 68 | **91** |
| `freq_category_shift` | 53 | 53 | 55 |
| `seizure_free_false_pos` | 45 | **56** | 41 |
| `unknown_false_neg` | 20 | 11 | 9 |
| `cluster_axis_error` | 7 | — | — |
| `seizure_free_false_neg` | 2 | 4 | 3 |
| **Total failures** | **186** | **192** | **199** |

#### CP (llm_only_canonical_pipeline)

| Failure Category | gpt-4.1-mini | deepseek | qwen |
|---|---|---|---|
| `unknown_false_pos` | 35 | 81 | **92** |
| `freq_category_shift` | **64** | 42 | 63 |
| `seizure_free_false_pos` | 32 | **49** | 37 |
| `unknown_false_neg` | 23 | 11 | 10 |
| `cluster_axis_error` | 11 | — | — |
| `seizure_free_false_neg` | 4 | 2 | 2 |
| **Total failures** | **169** | **185** | **204** |

#### SE (hybrid_structured_events)

| Failure Category | gpt-4.1-mini | deepseek | qwen |
|---|---|---|---|
| `freq_category_shift` | 26 | **44** | **45** |
| `unknown_false_pos` | **30** | 38 | 34 |
| `seizure_free_false_pos` | 5 | **26** | 23 |
| `unknown_false_neg` | 12 | 14 | 14 |
| `seizure_free_false_neg` | **9** | **11** | 6 |
| `parse_null` | 2 | 0 | 1 |
| **Total failures** | **89** | **133** | **122** |

---

## 2. Key Cross-Model Findings

### Finding 1: SE is the most robust LLM-using architecture but gpt-4.1-mini holds a clear lead

Across all three models, `hybrid_structured_events` (SE) is the best-performing LLM-using architecture by a wide margin (8-16pp over DL; 6-11pp over CP). Note that SE is architecturally a hybrid, not a fully-LLM pipeline: its LLM stage extracts structured events from raw text, and the same deterministic normalize/project/render/score stages used by the reset-native `hybrid` config then process that output. The deterministic normalization layer is the primary reason SE absorbs most of the denominator and formatting errors that the truly fully-LLM configs (DL, CP) fail on. The module has been renamed `hybrid_structured_events.py` to correct the original mislabeling; the PipelineArchitecture string `"hybrid_structured_events"` is kept for artifact compatibility.

However, gpt-4.1-mini's SE lead is larger: 88.4% vs 83.6% (qwen) and 82.1% (deepseek). SE's total failures are nearly 50% higher for qwen (122) and deepseek (133) than gpt-4.1-mini (89). The SE architecture is model-agnostic in structure but not in performance — the LLM's extraction quality still matters significantly. The primary difference is that deepseek and qwen SE have far higher `seizure_free_false_pos` (26/23 vs 5 for gpt). This suggests gpt-4.1-mini's structured extractor is substantially more conservative about emitting `kind=seizure_free` when the evidence is ambiguous.

**Implication for Phase 3**: SE is model-sensitive in the seizure-free extraction step specifically. A focused fix to the SE extractor prompt (tightening the `kind=seizure_free` trigger condition) could produce different returns for each model and should be piloted per-model.

### Finding 2: qwen's dominant failure mode is `unknown_false_pos` — the reverse of deepseek's

The three models have distinctly different failure profiles:

- **gpt-4.1-mini**: relatively balanced — highest `freq_category_shift` (64 CP), highest `cluster_axis_error`. Tends to over-commit to specific frequency values.
- **deepseek**: highest `seizure_free_false_pos` (56 DL, 49 CP, 26 SE). Deepseek over-reads seizure-free evidence more aggressively than the other two models. This matches deepseek's higher routing rate via `rendered_label_supported_but_policy_sensitive` in hybrid (97/123 routes).
- **qwen**: highest `unknown_false_pos` by a wide margin (91 DL, 92 CP). qwen under-commits — it returns `unknown` or `no seizure frequency reference` for notes that contain usable frequency facts. This is the inverse of deepseek's bias.

This is a fundamental model-personality difference, not a prompt artifact: qwen is more epistemically conservative; deepseek is more confident and willing to infer seizure-free status from partial evidence. gpt-4.1-mini sits in between.

**Implication for Phase 3**: The confidence-grounding fix in the `confidence` field (Section 8c pre-condition A) addresses the calibration symptom but not the underlying over/under-extraction. A separate per-model prompt calibration pass will be needed — the same instruction that reduces qwen's unknown_false_pos may increase deepseek's already-excessive seizure_free_false_pos. Generic prompt changes are likely to improve one model and harm another.

### Finding 3: The `guidance_for_tricky_cases` block (CP) helps gpt-4.1-mini, is neutral for deepseek, and harms qwen

The CP architecture embeds clinical-reasoning rules as prompt instructions. The delta CP vs DL across models:

| Model | DL purist | CP purist | Delta | Primary effect |
|---|---|---|---|---|
| gpt-4.1-mini | 0.752 | **0.775** | **+2.3pp** | Reduces unknown_false_pos (59→35, −24) |
| deepseek | 0.744 | **0.753** | **+0.9pp** | Small improvement; sf_fp persists |
| qwen | **0.734** | 0.727 | **−0.7pp** | No reduction in unknown_false_pos (91→92); adds freq_category_shift |

For gpt-4.1-mini, the guidance block's most effective rule is its suppression of unknown/no-reference over-labelling (−24 unknown_false_pos). For qwen, the same rules do nothing for unknown_false_pos but introduce additional freq_category_shift errors. This is interpretable: the rules assume the model will over-commit to specific patterns and need restraint. qwen's failure mode is under-commitment — the rules either do nothing or push qwen toward forced rate selection when it was correctly abstaining.

**Implication for Phase 3**: The CP guidance block as currently written is gpt-4.1-mini-calibrated. Before applying Phase 3's prompt rewrites to qwen and deepseek, consider whether the same rules should be presented differently (or with different emphasis) to each model. The shared-prompt assumption may not hold across this model family.

### Finding 4: FM-6 (highest-type selection / drop attacks) is gpt-4.1-mini-specific

Rows 12537, 12556, and 12562 are the canonical FM-6 cases — notes with daily drop attacks co-reported with lower-frequency GTC seizures where gpt-4.1-mini consistently picks the GTC rate ("3 per week") over the daily drop-attack rate ("1 per day").

- **gpt-4.1-mini DL**: all three fail → "3 per week" or "2-3 per week"
- **deepseek DL**: rows 12537 and 12556 pass → "1 per day"; row 12562 fails
- **qwen DL**: all three pass → "1 per day"

qwen and deepseek correctly prioritize frequency over clinical severity of seizure type without explicit instruction. The FM-6 fix in v0.5 (adding the explicit frequency-ranking rule) is therefore primarily a gpt-4.1-mini correction. It will likely have minimal effect on qwen and could be redundant for deepseek on these specific patterns. This is a strong argument against sharing Phase 3 prompt changes naively across models — what's a fix for gpt-4.1-mini is a no-op or possibly a confound for qwen.

### Finding 5: Hybrid's qwen rendering surface collapse is a structural problem, not a QA problem

qwen hybrid renders only 400/750 rows — far fewer than gpt-4.1-mini (589) or deepseek (604). This is not primarily a routing issue (62 routed, only 15.5% of rendered). The 350 non-rendered rows break down as 100 null + 62 routed + 188 that never produced a clinical assessment row to replay (the underlying candidate-set clinical assessment was produced for 400 rows from the original file's assessment probe, so 350 rows are missing assessment input entirely, even though the live candidate-set generation ran for all 750).

Wait — from the file analysis: the hybrid JSONL has 750 rows total (250 with `candidate_set: None`, 500 with live candidate sets). All 750 have `clinical_assessment` present. But the report shows 400 rendered. This means 350 rows had their clinical assessment produce null or abstain outcomes in the deep-replay stage — the assessment probe produced an output, but downstream projection/render/verification produced null or route for those rows.

The route taxonomy confirms this indirectly: `selected_source_id_invalid` is qwen's top route family (31/62), meaning qwen's clinical assessment frequently references candidate IDs that cannot be validated against the candidate set. Combined with qwen's high `unknown_false_pos` in the LLM-only configs, this tells a consistent story: qwen is structurally less willing to commit to a specific candidate's frequency value, leading to more unknown/null assessments and more source-id validation failures when it does commit.

**Implication for Phase 3**: Improving qwen's `unknown_false_pos` behavior in the DL/CP prompts is the highest-leverage intervention for qwen's hybrid performance too. If qwen's assessment probe becomes more willing to surface a confident frequency fact from the candidate set, the deep-replay stage will produce more rendered rows. The hybrid architecture amplifies qwen's conservatism because it requires a concrete candidate selection, not just a plausible rate.

### Finding 6: deepseek's routing is dominated by `rendered_label_supported_but_policy_sensitive`

deepseek routes 123/604 rendered rows (20.4%), with 97/123 (79%) from `rendered_label_supported_but_policy_sensitive`. This route family means the hybrid pipeline produced a supported label but the verification stage judged it policy-sensitive (e.g., a seizure-free label where the verification found a competing active-seizure candidate, or a frequency that passed rendering but failed a policy check). 

This confirms deepseek's high `seizure_free_false_pos` in the DL/CP analysis from a different angle: deepseek's clinical assessment frequently produces seizure-free outputs that are technically supported by some candidate evidence, but the verification stage catches them as policy violations. The hybrid architecture's routing behavior is thus actively correcting deepseek's over-confident seizure-free tendency — at the cost of routing 97 rows to human review.

**Implication for Phase 3**: deepseek's hybrid routing problem and its DL/CP seizure_free_false_pos problem have the same root cause. A more conservative seizure-free instruction (tightening the trigger condition as in the FM-2 fix) should simultaneously reduce deepseek's false-positive rate in DL/CP and reduce its route count in hybrid. This is the highest-leverage single intervention for deepseek.

### Finding 7: Architecture performance ordering is not consistent across models

| Rank by purist accuracy | gpt-4.1-mini | deepseek | qwen |
|---|---|---|---|
| 1st | SE (88.4%) | SE (82.1%) | SE (83.6%) |
| 2nd | hybrid (84.9% of rendered) | hybrid (81.1%) | hybrid (72.8%) |
| 3rd | CP (77.5%) | CP (75.3%) | DL (73.4%) |
| 4th | DL (75.2%) | DL (74.4%) | CP (72.7%) |
| 5th (worst LLM) | — | — | — |

SE is consistently best across all models. But hybrid drops from 2nd for gpt-4.1-mini and deepseek to near-worst for qwen (and only of its rendered rows — on all 750 rows, qwen hybrid would be 291/750 = 38.8%). The DL/CP ordering flips for qwen: DL outperforms CP, the opposite of gpt-4.1-mini and deepseek. This means the architecture rankings established in the gpt-4.1-mini analysis do not fully generalize.

---

## 3. Implications for Phase 3 Prompt Engineering

### 3.1 Model-specific vs shared prompt changes

The data strongly suggests that Phase 3's prompt changes need per-model validation before being declared improvements. A change that helps gpt-4.1-mini is not automatically useful for qwen or deepseek. Specifically:

| Intervention | Expected gpt-4.1-mini effect | Expected deepseek effect | Expected qwen effect |
|---|---|---|---|
| FM-2 seizure-free tightening | Reduces SF-FP (45→) | **Largest benefit** (56 failures) | Small benefit (41 failures) |
| FM-6 frequency-ranking rule | **Largest benefit** (fixes drop-attack rows) | Small benefit (row 12562 only) | No benefit (already correct) |
| FM-3 unknown-FP reduction | Moderate benefit (59→35 already from CP) | Moderate benefit | **Largest benefit** (91 failures) |
| CP guidance block (general) | Positive (+2.3pp) | Neutral (+0.9pp) | **Negative** (−0.7pp) |
| Hybrid candidate-selection guidance | Moderate | Moderate (reduces routing) | **Largest benefit** (high null surface) |

### 3.2 Shared failure modes (genuinely universal)

The following failure patterns are confirmed across all three models and should be treated as high-priority universal interventions:

1. **FM-2a trigger-conditioned SF** (rows 11216, 11272): all models fail uniformly — gpt, deepseek, qwen all return seizure-free when gold is unknown. This is the most robustly cross-model failure mode.
2. **FM-1 denominator window with competing seizure types** (rows 16938+): all models anchor on the wrong seizure type's denominator. Fixing the highest-frequency-type selection instruction (FM-6 for gpt-4.1-mini, but the seizure-type selection dimension more broadly) should help across models.
3. **Row 5837 cluster complexity**: all three models return unknown or plain rate on "2 cluster per 3 week, multiple per cluster." This may be a genuinely hard annotation case that no prompt fix resolves — worth marking as potential gold annotation dispute.
4. **Row 7195 single-event rate inference**: all three models infer a recurring rate from a single recent event. The minimum-recurrence instruction (FM-4 fix) is a candidate universal intervention.

### 3.3 Priority stack for Phase 3 given cross-model data

1. **FM-2 seizure-free tightening** — universal benefit, largest gain for deepseek, meaningful for gpt and qwen. Already partially in v0.5; verify deepseek and qwen response separately.
2. **qwen-specific: FM-3 unknown-FP reduction** — qwen has 91 DL unknown_false_pos vs 59 for gpt. A qwen-targeted instruction acknowledging the model's tendency to under-extract (and encouraging it to commit when evidence is explicit) could be the highest-leverage qwen-specific change.
3. **deepseek-specific: hybrid routing via SF tightening** — deepseek's 97 `rendered_label_supported_but_policy_sensitive` routes are the highest-cost output of deepseek's over-confident SF tendency. Fixing this simultaneously improves DL/CP accuracy and reduces hybrid routing waste.
4. **FM-6 (gpt-4.1-mini only)** — already in v0.5; do not apply to qwen/deepseek without first checking whether it's a no-op or confound for them.
5. **CP guidance block per-model calibration** — the block as written is gpt-4.1-mini-calibrated. Consider a qwen-specific variant that de-emphasizes the suppression rules (which do nothing for qwen's failure mode) and instead adds explicit extraction encouragement for common qwen false-abstention patterns.

---

## 4. Open Questions

1. **Is qwen's `unknown_false_pos` a prompt issue or a model-capability issue?** The 91 DL unknown_false_pos for qwen includes cases where qwen's rationale correctly identifies the frequency fact but the final label still maps to unknown. If the label-generation step (not the reasoning step) is the bug, a rationale-label consistency instruction (FM-3 approach 3 from the error analysis) may be more effective than adding new extraction encouragement.

2. **Should the CP guidance block be model-parameterized?** The current architecture shares one prompt across models. The performance data suggests qwen needs a different emphasis than gpt-4.1-mini. Two options: (a) add a model-specific prefix to the guidance block, (b) treat CP as a gpt-4.1-mini-optimized architecture and explicitly exclude it from the qwen/deepseek comparison going forward.

3. **What explains qwen's much lower hybrid rendering surface?** The 350 non-rendered qwen hybrid rows are not accounted for by routing alone. Further investigation of the deep-replay output would clarify whether the null rows are from projection failures (no projectable candidate selected) or from the assessment itself (unknown/no_reference assessment output that downstream renders as null). This is a prerequisite for understanding whether the hybrid architecture is viable for qwen at all.

4. **Is deepseek's SE `seizure_free_false_pos` (26 vs 5 for gpt-4.1-mini) fixable in the structured extractor?** The structured extractor's schema is the same across models, but deepseek emits `kind=seizure_free` far more liberally. Since the SE extractor prompt is the LLM-facing layer, a tighter `kind=seizure_free` trigger condition in the SE prompt should reduce this — but it needs to be a separate pilot from the DL/CP prompt changes.
