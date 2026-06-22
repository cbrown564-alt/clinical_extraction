# Cross-Dataset Model Deep Dive: Gan Frequency And ExECTv2

Generated: 2026-06-22

Scope: evidence accumulation across existing `gan_frequency` / Gan 2026 and
ExECTv2 artifacts that permit direct or near-direct comparison of
GPT-4.1-mini, Qwen3.6:35b, and DeepSeek. No new model calls were run for this
report. Fresh analysis is limited to validation/dev artifacts; locked Gan
test450 evidence is reported only from aggregate summaries, with no test-row
failure inspection.

## Claim Boundaries

- Gan 2026 validation750 is the cleanest three-model side-by-side comparison
  for seizure-frequency classification architectures.
- Gan 2026 test450 contains aggregate-only GPT, DeepSeek, and Qwen
  structured-event evidence, but Qwen required technical recovery and
  deterministic repair attribution; its final number is a hybrid artifact, not
  a raw-Qwen result.
- ExECTv2 has a strong GPT-4.1-mini dev140 control plus completed final dev140
  DeepSeek and Qwen diagnostic replays. The non-GPT dev140 rows are valuable
  transfer and reliability evidence, but both final reports keep
  `do-not-promote` gate decisions.
- Deterministic repair, evidence validation, CUI projection, and family-specific
  lenses are part of the measured systems. Scores must be read as architecture
  scores, not pure model ability, unless a run is explicitly labeled raw/model
  only.

## Evidence Sources

Primary Gan sources:

- `experiments/gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08.md`
- `experiments/gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09.md`
- `experiments/gan2026_three_way_comparison_phase1_report_deepseek_validation750_2026-06-09.md`
- `experiments/gan2026_three_way_comparison_phase3_report_gpt41mini_validation750_2026-06-09.md`
- `experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.md`
- `experiments/gan2026_v06_validation750_hybrid_structured_events_deepseek_2026-06-12.md`
- `experiments/gan2026_v06_test450_hybrid_structured_events_deepseek_2026-06-14.md`
- `experiments/gan2026_v06_validation750_hybrid_structured_events_qwen3635b_2026-06-12.md`
- `experiments/gan2026_v06_validation750_hybrid_structured_events_qwen3635b_replay_repairfix_2026-06-21.md`
- `experiments/gan2026_v06_validation750_qwen3635b_repairfix_attribution_2026-06-21.md`
- `experiments/gan2026_v06_test450_qwen3635b_repairfix_frozen_aggregate_summary_2026-06-21.md`
- `experiments/gan2026_reliability_master_scorecard_2026-06-17.md`

Primary ExECTv2 sources:

- `docs/experiments/exectv2/key_entities/exectv2_cross_model_closeout_2026-06-22.md`
- `docs/experiments/exectv2/reliability/exectv2_cross_model_reliability_scorecard_2026-06-22.md`
- `docs/research/final_architecture_selection_2026-06-22.md`
- `experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.json`
- `experiments/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140_20260621.json`
- `experiments/exectv2_holistic_finding_assembly_v097_deepseek_dev25_20260622.json`
- `experiments/exectv2_holistic_finding_assembly_v096_schema_repair_qwen_reparse_dev25_20260622.json`
- `experiments/exectv2_holistic_finding_assembly_v097_qwencompact_dictrepair_dev25_20260622.json`
- `experiments/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.md`
- `experiments/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.json`
- `experiments/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140_20260622.md`
- `experiments/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140_20260622.json`
- `experiments/exectv2_holistic_finding_assembly_v099_deepseek_dev25_20260622.json`
- `experiments/exectv2_holistic_finding_assembly_v0910_qwencompact_dictionary_replay_dev25_20260622.json`
- `experiments/RUN_INDEX.md`
- `experiments/registry.jsonl`

## Gan 2026 Architecture Evidence

### Phase 1 Validation750: Same Architectures, Three Models

All rows below are validation750 and use the same split. Deterministic rows are
model-independent common comparators.

| Architecture | GPT-4.1-mini Purist / Prag | Qwen3.6:35b Purist / Prag | DeepSeek Purist / Prag | Notes |
|---|---:|---:|---:|---|
| Deterministic / canonical deterministic pipeline | 0.928 / 0.938 | 0.928 / 0.938 | 0.928 / 0.938 | Common non-LLM baseline; 741 rendered, 9 null. |
| Hybrid candidate-set + LLM adjudication | 0.849 / 0.891 | 0.728 / 0.797 | 0.811 / 0.861 | Strong GPT lift, DeepSeek usable, Qwen weak and low evidence. |
| LLM-only direct labeler | 0.752 / 0.799 | 0.734 / 0.776 | 0.744 / 0.781 | Direct labels are consistently worse than structured-event hybrid. |
| Hybrid structured events | 0.884 / 0.908 | 0.836 / 0.866 | 0.821 / 0.854 | Best LLM-backed shape in the initial three-way comparison. |
| LLM-only canonical pipeline | 0.775 / 0.835 | 0.727 / 0.778 | 0.753 / 0.781 | Canonicalization alone does not recover enough signal. |

Main read: for Gan frequency, asking the model to emit source-near structured
events, then using deterministic normalization/projection, is the best
cross-model LLM architecture. Direct answer labeling is brittle for all three
models. The candidate-set adjudication architecture depends heavily on the
model's ability to choose among pre-generated spans and is much less portable to
Qwen.

### Later Structured-Event Runs: Best Comparable LLM-Backed Gan Architecture

| Model / run | Split | Purist | Pragmatic | Evidence valid | Operational notes |
|---|---:|---:|---:|---:|---|
| GPT-4.1-mini structured events v0.5 | validation750 | 0.8813 | 0.9053 | 0.9213 | 748/750 structured; 0 call failures; 2 null comparisons. |
| GPT-4.1-mini structured events v0.5 | test450 aggregate | 0.8089 | 0.8467 | 0.9289 | 448/450 rendered; 0 call failures; 2 parse/schema/label issues. |
| DeepSeek structured events v0.6 | validation750 | 0.8293 | 0.8613 | 0.9587 | 745/750 structured; 0 call failures; 5 null comparisons. |
| DeepSeek structured events v0.6 | test450 aggregate | 0.7867 | 0.8178 | 0.9778 | 446/450 structured; 0 call failures; 4 parse/schema/label issues. |
| Qwen structured events v0.6 baseline | validation750 | 0.8507 | 0.8747 | 0.7747 | 4 parse/schema issues; 746 JSON dialect repairs. |
| Qwen structured events v0.6 repairfix | validation750 | 0.8827 | 0.9053 | 0.7787 | No-call replay; 749/750 structured; 749 JSON dialect repairs. |
| Qwen structured events v0.6 repairfix | test450 aggregate | 0.8133 | 0.8467 | 0.8156 | Recovered frozen aggregate; 449/450 structured; 0 call failures; 1 parse/schema/label issue. |

The Qwen test aggregate clears the 0.8 Purist target and slightly exceeds the
GPT structured-event test Purist score, but the interpretation is very
different: GPT is the cleaner balanced reference; Qwen is a hybrid repairfix
candidate whose output becomes competitive only after extensive deterministic
JSON dialect, selected-evidence, and label repair.

### Qwen Same-Raw Repair Attribution

The strongest Qwen validation result is repair-dependent:

| Lens over same Qwen raw outputs | Purist | Pragmatic | Parse/schema issues | Interpretation |
|---|---:|---:|---:|---|
| Strict JSON raw model | 0.0000 | 0.0000 | 750 | Raw output cannot be claimed as usable strict JSON. |
| JSON dialect only / raw model | 0.4920 | 0.5213 | 232 | Dialect repair recovers structure but not final task quality. |
| Strict format | 0.5360 | 0.5667 | 196 | Schema-compatible output remains weak. |
| Selected-evidence derivation | 0.8040 | 0.8360 | 1 | Most of the useful lift comes from deterministic derivation. |
| Hybrid full stack | 0.8827 | 0.9053 | 1 | Competitive score, but not LLM-first. |

Repair accounting showed 508 changed labels in the full-stack lens: 301
raw-wrong to full-correct, 8 raw-correct to full-wrong, 143 correct-to-correct,
and 56 wrong-to-wrong. This is a large positive deterministic contribution, and
it is the reason Qwen should be discussed as a repair-sensitive local-model
condition rather than as a clean raw model replacement.

### Fresh Validation750 Agreement Slice

Fresh script over the three structured-event validation JSONL files aligned all
models by `source_row_index` across the same 750 rows.

| Model | Purist | Pragmatic | Evidence valid | Structured | Call failures | Rows with parse notes |
|---|---:|---:|---:|---:|---:|---:|
| GPT-4.1-mini SE v0.5 | 661/750 = 0.8813 | 679/750 = 0.9053 | 691/750 = 0.9213 | 748 | 0 | 528 |
| DeepSeek SE v0.6 | 622/750 = 0.8293 | 646/750 = 0.8613 | 719/750 = 0.9587 | 745 | 0 | 505 |
| Qwen SE v0.6 repairfix | 662/750 = 0.8827 | 679/750 = 0.9053 | 584/750 = 0.7787 | 749 | 0 | 750 |

Three-way Purist correctness patterns:

| Pattern | Rows |
|---|---:|
| All three correct | 568 |
| None correct | 36 |
| GPT + Qwen only | 49 |
| GPT + DeepSeek only | 29 |
| Qwen only | 28 |
| DeepSeek + Qwen only | 17 |
| GPT only | 15 |
| DeepSeek only | 8 |

Pairwise Purist comparison on the same rows:

| Pair | Both correct | First only | Second only | Neither |
|---|---:|---:|---:|---:|
| GPT vs DeepSeek | 597 | 64 | 25 | 64 |
| GPT vs Qwen | 617 | 44 | 45 | 44 |
| DeepSeek vs Qwen | 585 | 37 | 77 | 51 |

Category recall on common rows:

| Gold category | n | GPT | DeepSeek | Qwen repairfix |
|---|---:|---:|---:|---:|
| `seizure_freq_unknown` | 170 | 0.906 | 0.859 | 0.859 |
| `seizure_freq_more1week_less1day` | 162 | 0.858 | 0.846 | 0.901 |
| `currently_no_seizure` | 112 | 0.920 | 0.866 | 0.955 |
| `seizure_freq_more1mon_less1week` | 106 | 0.887 | 0.783 | 0.877 |
| `seizure_freq_more1per6mon_less1mon` | 76 | 0.895 | 0.829 | 0.803 |
| `seizure_freq_1ormore_daily` | 63 | 0.841 | 0.746 | 0.937 |
| `seizure_freq_1_per_mon` | 35 | 0.886 | 0.829 | 0.914 |
| `seizure_freq_1_per_week` | 13 | 0.846 | 0.846 | 0.846 |

Fresh slice interpretation:

- GPT and Qwen repairfix are effectively tied on validation Purist/Pragmatic,
  but the route differs: GPT is more faithful, Qwen is more repair-mediated.
- DeepSeek has the cleanest exact-evidence profile on validation and test, but
  lower final category accuracy, especially around current active burden and
  remission/unknown boundaries.
- Qwen repairfix is strongest in several concrete-rate categories, including
  daily and currently-no-seizure, but weakest in evidence validity and still
  vulnerable on unknown-boundary rows.
- GPT's remaining misses include active high-frequency rows predicted as
  unknown, plus unknown rows converted to concrete frequencies or seizure-free.
- The 36 rows missed by all three are the best candidates for deterministic
  taxonomy/label-boundary review rather than additional prompt tuning.

## ExECTv2 Evidence

### Final Dev140 Cross-Model / Architecture Comparison

| Run | Rows | Overall F1 | Dx | SF | Rx | Inv | SF active-rate fidelity | Evidence-valid overall | Operational notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| GPT v08 holistic assembly, performance control | 140 | 0.9152 | 0.9083 | 0.9053 | 0.9357 | 0.9132 | 0.5969 | 0.8872 | No-call replay; 0 call failures; 0 parse/schema failures. |
| GPT v09 partial hybrid simplification | 140 | 0.9059 | 0.9083 | 0.9053 | 0.9357 | 0.8549 | 0.5969 | 0.8779 | Simplifies architecture, but Investigations drops. |
| DeepSeek v0.9.16 reparse dev140 | 140 | 0.9010 | 0.8828 | 0.8675 | 0.9430 | 0.9231 | 0.6057 | 0.8554 | `do-not-promote`; 0 call failures; 0 parse/schema failures. |
| Qwen v0.9.22 compact residual-repair dev140 | 140 | 0.9001 | 0.8563 | 0.8908 | 0.9343 | 0.9579 | 0.3618 | 0.8567 | `do-not-promote`; 0 call failures; 10 parse/schema failures reported on each shared lane. |

Final ExECTv2 read:

- GPT v08 is the only all-four-family dev140 control above 0.900.
- GPT v09 is a credible simplification, but not a replacement if
  Investigations parity matters.
- DeepSeek v0.9.16 is the cleanest final non-GPT dev140 diagnostic:
  operationally stable, strong on Prescription and Investigations, and close to
  GPT v09 overall. It still trails GPT v08 on Diagnosis and SeizureFrequency
  headline scores and remains `do-not-promote`.
- Qwen v0.9.22 reaches a similar overall score through compact local-model
  output plus standard dictionary and residual-repair lenses. Its headline SF
  F1 is close to GPT, and Investigations is the best row in the table, but
  active-rate fidelity remains poor and schema repair burden remains visible.
- The non-GPT dev140 rows now make the comparison stronger than the earlier
  dev25 diagnostics, but they do not change the performance-control selection:
  GPT v08 remains the highest and most balanced ExECTv2 dev140 architecture.

### Final Dev140 Non-GPT Architectures

Both completed non-GPT rows are structural replays over frozen v0.9.10 source
artifacts. They introduce no live model calls at assembly time.

| Model row | Source artifact | Lenses | Ownership label | Claim boundary |
|---|---|---|---|---|
| DeepSeek v0.9.16 reparse dev140 | `experiments/exectv2_llm_only_key_entities_structured_v0910_dev140_deepseek_chat_20260622.jsonl` | `diagnosis_convention_dictionary_v09`, `sf_convention_dictionary_v09`, `prescription_dictionary_v09`, `investigations_convention_dictionary_v09` | `single_gpt+standard_dictionary_*` | `diagnostic-same-raw-deepseek-v0910-through-v0916-dictionary-dev140` |
| Qwen v0.9.22 compact residual-repair dev140 | `experiments/exectv2_llm_only_key_entities_structured_v0910_qwencompact_dev140_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl` | `diagnosis_convention_dictionary_v09`, `sf_convention_dictionary_v09`, `prescription_dictionary_v09`, `investigations_convention_dictionary_v09` | `single_gpt+standard_dictionary_*` | `local-qwen-v0910-qwen-compact-live-dev140-ctx12288-maxtok2500-standard-dictionary-residual-repair-v13` |

Important architecture caveat: the `raw_candidate` score view is `0.0000` in
both final non-GPT reports. The meaningful reported scores are the
evidence-valid / benchmark-CUI / clinical-headline views rendered after the
standard dictionary lenses and residual repairs. This reinforces the report's
main attribution rule: these are architecture results, not raw-model-only
results.

### Prior ExECTv2 Diagnostics / Non-Promotion Evidence

| Run | Rows | Overall F1 | Dx | SF | Rx | Inv | SF active-rate fidelity | Evidence-valid overall | Claim boundary |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| DeepSeek v0.9.7 selected diagnostic | 25 | 0.8707 | 0.8456 | 0.7586 | 0.9610 | 0.9091 | 0.7879 | 0.8524 | Earlier selected dev25 comparator before final dev140 reparse. |
| Qwen v0.9.6 selected no-call schema-repair reparse | 25 | 0.8082 | 0.8112 | 0.6429 | 0.8608 | 0.9268 | 0.3750 | 0.7899 | Earlier best selected Qwen dev25 reparse. |
| Qwen v0.9.7 compact dictrepair | 25 | 0.7995 | 0.7755 | 0.5882 | 0.9487 | 0.8163 | 0.2424 | 0.7888 | Earlier compact Qwen diagnostic. |
| DeepSeek v0.9.9 observed | 25 | 0.9206 | 0.9250 | 0.7925 | 0.9744 | 0.9756 | 0.8125 | 0.9012 | Strong dev25 successor candidate; not dev140 promotion evidence. |
| DeepSeek v0.9.8 observed | 25 | 0.8736 | 0.8235 | 0.7500 | 0.9620 | 0.9756 | 0.8235 | 0.8550 | Similar to v0.9.7 overall; SF remains limiting. |
| Qwen v0.9.10 dictionary replay observed | 25 | 0.8474 | 0.8355 | 0.5882 | 0.9487 | 1.0000 | 0.2424 | 0.8359 | Assembly replay over checkpointed compact source; not canonical. |

These rows explain the path to the final dev140 diagnostics. DeepSeek v0.9.9
was the strongest dev25 signal and motivated the final dev140 same-raw reparse.
Qwen v0.9.10 showed dictionary/replay lift but did not solve active-rate
fidelity; the final v0.9.22 row preserves that pattern at dev140 scale.

### Earlier ExECTv2 Seizure-Frequency Transfer Evidence

The ExECTv2 SF-only hybrid dev140 comparison is useful because it directly
contrasts GPT and Qwen on the same hybrid architecture:

| Run | Phrase-only per-item / per-letter | SF semantic benchmark per-item / per-letter | Operational note |
|---|---:|---:|---|
| GPT-4.1-mini hybrid dev140 | 0.585 / 0.781 | 0.327 / 0.578 | 0 call failures; 0 parse failures. |
| Qwen3.6:35b hybrid dev140 | 0.498 / 0.730 | 0.228 / 0.451 | 0 call failures; 1 parse failure from truncation. |

This prefigures the later holistic result: GPT and Qwen can both find surface
phrases, but attribute-aware seizure-frequency semantics are much less portable,
and Qwen degrades more sharply when asked to preserve the active-rate state.

## Cross-Task Model Profiles

### GPT-4.1-mini

Strengths:

- Best balanced ExECTv2 architecture: v08 clears all four families on dev140.
- Strong Gan structured-event reference with stable test450 aggregate behavior.
- Lower dialect/schema burden than Qwen and stronger overall evidence validity
  than Qwen in Gan validation.
- Reliability package exists: abstention/external-corroboration analyses,
  robustness probes, and documented held-out performance.

Failure modes:

- Direct label and LLM-only canonical architectures underperform; GPT still
  needs the structured-event/hybrid shape.
- In Gan, high-frequency or active-burden rows can be over-abstained into
  unknown, while unknown rows can still be over-read into concrete rates or
  seizure-free states.
- In ExECTv2, the headline SF F1 hides weak active-rate fidelity
  (0.5969 in v08/v09), so active-rate/state selection remains a clinical
  reliability issue.
- Self-confidence is not useful: the Gan reliability scorecard found degenerate
  confidence and better signal from external corroboration / risk routing.

Compensation:

- Keep structured-event extraction plus deterministic normalization for Gan.
- Keep ExECTv2 family-specific lanes/lenses rather than relying on one
  monolithic extraction call.
- Use external agreement and deterministic contradiction checks for unknown,
  seizure-free, and current-rate boundaries.

### DeepSeek

Strengths:

- Operationally clean in the reviewed Gan and ExECTv2 runs: no call failures in
  the key structured-event runs and in the final v0.9.16 ExECTv2 dev140
  reparse.
- Strong evidence validity in Gan: 0.9587 validation and 0.9778 test450
  aggregate for structured events.
- Final ExECTv2 v0.9.16 dev140 is close to the GPT simplification control:
  overall 0.9010, Prescription 0.9430, Investigations 0.9231, and exact
  evidence rate 1.0000 across all lanes.
- DeepSeek is now the cleanest non-GPT ExECTv2 dev140 diagnostic architecture:
  no parse/schema burden, good family balance, but still `do-not-promote`.

Failure modes:

- Gan final category accuracy lags GPT/Qwen repairfix despite high evidence
  validity, implying that evidence selection and exact substrings are not enough
  for final frequency-class projection.
- ExECTv2 SeizureFrequency remains below GPT v08 at dev140 scale: DeepSeek
  v0.9.16 headline SF is 0.8675 versus GPT v08 at 0.9053, and the evidence-valid
  SF/CUI view is only 0.6549.
- Diagnosis also trails GPT v08 at dev140 scale: 0.8828 versus 0.9083, with the
  changed-row accounting still dominated by assertion/negation and
  hierarchy/duplicate-collapse behavior.

Compensation:

- Pair DeepSeek with deterministic active-rate/state arbitration.
- Treat v0.9.16 as final dev140 transfer/reliability evidence, not a replacement
  claim, unless future work explicitly clears family-specific gates.
- Use it as an agreement partner: its evidence discipline may be valuable even
  when final label projection is weaker.

### Qwen3.6:35b

Strengths:

- Can reach GPT-level Gan structured-event validation/test aggregate accuracy
  after repairfix: validation Purist 0.8827 and test450 aggregate Purist 0.8133.
- Strong in several concrete Gan frequency categories after repairfix, including
  daily and currently-no-seizure categories in the fresh validation slice.
- Final ExECTv2 v0.9.22 dev140 reaches overall 0.9001 with strong Prescription
  0.9343 and the best Investigations row in the final table at 0.9579.
- Qwen's final ExECTv2 headline SeizureFrequency score is much stronger than
  its earlier dev25 compact diagnostics: 0.8908 on dev140 versus 0.5882 on the
  compact v0.9.7 dev25 row.
- Local model condition is valuable for portability and operational learning.

Failure modes:

- JSON dialect/schema is the dominant operational burden. In Gan repairfix,
  749/750 validation rows required JSON dialect repair; strict JSON raw model
  scored 0 because all rows failed strict parsing.
- Much of the Gan lift is deterministic: selected-evidence derivation alone
  moves the same raw outputs to 0.804 Purist, and full-stack repair to 0.8827.
- Evidence validity is weak relative to GPT/DeepSeek in Gan: 0.7787 validation
  and 0.8156 test450 aggregate for the repairfix candidate.
- ExECTv2 SF active-rate fidelity remains poor even after the final dev140
  residual-repair row: 0.3618, despite a headline SF F1 of 0.8908.
- The final Qwen ExECTv2 source still carries schema burden: 10 parse/schema
  failures are reported on each shared lane, while the raw-candidate score view
  remains 0.0000.
- Local operational stability matters: the first Qwen test450 repairfix run had
  severe Ollama/CUDA failures before technical recovery.

Compensation:

- Treat Qwen as a repair-sensitive local-model system, not a strict model-only
  extractor.
- Preserve dialect repair, schema alias repair, short-rationale prompting, and
  deterministic selected-evidence derivation as explicit architecture
  components.
- Do not promote compact/residual-repair prompts on headline F1 alone; require
  active-rate fidelity, evidence-valid SF, and schema stability to improve.
- Separate local runtime reliability from model quality in reports.

## Key Cross-Cutting Insights

1. Architecture dominates model selection.

   Across Gan, structured events beat direct labels and LLM-only canonical
   outputs for all three models. Across ExECTv2, the family-lane assembly beats
   pure single-pass simplifications. Model choice matters, but only inside a
   disciplined extraction/normalization architecture.

2. Seizure frequency is the least portable semantic task.

   Gan frequency and ExECTv2 SeizureFrequency both punish the same abilities:
   current-vs-historical arbitration, seizure-free-vs-active-event precedence,
   unknown boundaries, multiple semiology burden selection, and rate-window
   projection. DeepSeek and Qwen can extract evidence or phrases, but final
   active-rate semantics degrade sharply without deterministic help.

3. Evidence faithfulness and answer correctness are separable.

   DeepSeek has better Gan evidence validity than GPT and Qwen, but lower final
   category accuracy. Qwen repairfix has high final accuracy but weak evidence
   validity. GPT sits in the best balance. Reports should continue to show both
   exact-evidence/fidelity scores and target-label scores.

4. Qwen competitiveness is real but repair-mediated.

   The Qwen Gan repairfix result should not be dismissed: after recovery it
   matches GPT's validation Pragmatic score and clears test450 Purist. But the
   same-raw attribution proves the score belongs to a hybrid system with large
   deterministic repair contribution. The final ExECTv2 v0.9.22 result repeats
   the same lesson: excellent headline Investigations and near-control headline
   SF, but poor active-rate fidelity and visible parse/schema repair burden.
   That is useful engineering evidence, not a pure local-model parity claim.

5. DeepSeek is the cleanest non-GPT reliability partner.

   DeepSeek is operationally cleaner than Qwen and has strong evidence behavior.
   The final ExECTv2 v0.9.16 dev140 result is now the strongest signal that a
   hosted non-GPT model can approach the GPT controls on a full dev140
   diagnostic replay. The missing pieces are still family-specific: Diagnosis
   trails GPT v08, and SF headline/evidence-valid views still need stronger
   active-rate semantics before replacement language is justified.

6. GPT-4.1-mini remains the best controlled reference.

   GPT v08 is still the ExECTv2 control because it clears all four dev140
   families. In Gan, GPT is not always the highest aggregate number after Qwen
   repairfix, but it has the cleaner balance of accuracy, evidence validity,
   operational stability, and reliability analysis.

7. Self-reported model confidence should not drive review routing.

   Gan reliability work found model confidence to be degenerate, while external
   corroboration and abstention curves were informative. The cross-model
   evidence supports this: disagreement and evidence/answer mismatch are better
   review signals than confidence labels.

8. Promotion claims need family-specific gates.

   Overall F1 can hide the clinically important failure. ExECTv2 v09 preserves
   overall >0.900 while Investigations drops. DeepSeek v0.9.16 reaches 0.9010
   overall but remains below GPT v08 on Diagnosis and SF. Qwen v0.9.22 reaches
   0.9001 overall and 0.9579 Investigations, while leaving SF active-rate
   fidelity at only 0.3618.

## Practical Recommendations

- Use GPT v08 as the ExECTv2 performance control and GPT v09 as the
  simplification/control-ablation row.
- Treat DeepSeek v0.9.16 reparse dev140 as the final clean non-GPT ExECTv2
  diagnostic: strong transfer evidence, but still `do-not-promote`.
- Treat Qwen v0.9.22 compact residual-repair dev140 as the final local-model
  ExECTv2 diagnostic: headline-competitive in places, but blocked from
  promotion by active-rate fidelity and schema/dialect burden.
- For Gan, report GPT structured-events as the clean reference and Qwen
  repairfix as a strong hybrid-repair replication, with DeepSeek as the
  high-faithfulness but lower-label-accuracy comparator.
- Build review routing around disagreement, invalid evidence, unknown/seizure-free
  conflict, and active-rate/state transitions.
- Preserve deterministic repair attribution in all paper-facing tables. Hidden
  repair makes Qwen look like a raw model win and makes GPT/DeepSeek/Qwen
  comparisons scientifically muddy.
