# Gan 2026 Failure-Mode Comparison Table

Date: 2026-06-12

Status: paper-facing consolidation from existing artifacts. This document does
not introduce a new run, authorize new holdout use, inspect locked-test row
failures, or make a benchmark-comparable claim.

## Purpose

Compress the current Gan 2026 architecture evidence into a failure-mode table
for close-off. The promoted direction remains `hybrid_structured_events`: LLM
structured-event extraction followed by deterministic normalization,
projection, rendering, and scoring.

Primary sources:

- `docs/research/gan2026_closeoff_report_2026-06-12.md`
- `docs/research/gan2026_phase3_error_analysis_2026-06-09.md`
- `experiments/gan2026_three_way_comparison_phase3_report_gpt41mini_validation750_2026-06-09.md`
- `experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.md`
- `experiments/gan2026_agentic_matched_budget_validation_hard50_active_conditions_live_prompt_v1_2026-06-12.md`

## Compact Architecture Table

Validation rows are from `gan2026_split_v1` validation750 unless noted. The
locked `test450` column is aggregate-only and must not be read as row-level
failure evidence.

| Architecture | Ownership pattern | Validation signal | Locked aggregate signal | Dominant failure modes | Close-off reading |
| --- | --- | ---: | ---: | --- | --- |
| `deterministic_canonical_pipeline` | Deterministic rules own extraction, selection, normalization, and rendering. | `673/741` Purist rendered-correct; evidence substring metric `750/750`. | `329/450` Purist, `341/450` Pragmatic. | Strong validation fit, but large validation-to-test drop; remaining errors expose rule-portability and split-generalization risk rather than schema failure. | Keep as a comparator and generalization lesson. High validation accuracy alone is incomplete evidence. |
| `llm_only_direct_labeler` | One LLM call owns direct final-label selection. | `564/750` to `575/750` Purist depending source row/report convention; Phase 3 taxonomy counts `186` failures. | Not included in frozen Phase 4 audit by design; consistently below CP/SE on validation. | `unknown_false_pos` 59, `freq_category_shift` 53, `seizure_free_false_pos` 45, `unknown_false_neg` 20. | Useful lower-bound LLM-only comparator. Single final-label prediction is too lossy for this task. |
| `llm_only_canonical_pipeline` | One LLM call owns final-label selection with boundary guidance; deterministic code validates/parses only. | `582/750` Purist rendered-correct; Phase 3 taxonomy counts `169` failures. | `326/450` Purist, `346/450` Pragmatic. | `freq_category_shift` 64, `unknown_false_pos` 35, `seizure_free_false_pos` 32, `unknown_false_neg` 23, `cluster_axis_error` 11. Guidance reduces some unknown over-fire but introduces rate-selection errors. | Stronger fully LLM baseline than direct labeler, but still below hybrid structured events and not robust enough to promote. |
| `hybrid_structured_events` | LLM extracts structured events; deterministic stages normalize, project, render, and score. | `661/748` Purist rendered-correct; Phase 3 taxonomy counts `89` failures plus `2` parse nulls. | `364/448` Purist, `381/448` Pragmatic, best current aggregate among audited candidates. | `unknown_false_pos` 30, `freq_category_shift` 26, `unknown_false_neg` 12, `seizure_free_false_neg` 9, `seizure_free_false_pos` 5, `cluster_axis_error` 5, `parse_null` 2. Distinct weakness: last-event-only records can miss seizure-free state. | Promote for close-off. It retains high coverage and the best frozen aggregate while making model and deterministic ownership explicit. |
| Reset-native `hybrid` / CandidateSet assessment | Deterministic CandidateSet generation plus LLM clinical assessment, then deterministic downstream. | `526/597` or `500/589` Purist rendered-correct depending replay source; high precision among rendered rows but many null/routed rows. | `269/334` Purist, `281/334` Pragmatic; `116` null rows. | Among rendered validation failures: `freq_category_shift` 42, `seizure_free_false_pos` 15, `cluster_axis_error` 11, `unknown_false_pos` 8, `unknown_false_neg` 8. Routing families include selected-source invalidity and cluster ambiguity. | Scientifically valuable for auditability, but not the operational headline because coverage/null burden is too large. |
| `single_agent_tools` on validation hard50 | Single model-owned loop with parser/guide tools under matched budget. | Hard50: `20/50` Purist, `22/50` Pragmatic. | No holdout use. | Compared with same-model self-consistency: `0` wins, `12` losses; regressions cluster around seizure-free/current-history confusion, competing semiologies, rate-denominator selection, and cluster-burden handling. | Revise/reject as currently shaped. Tool context harms the hard slice instead of making high-precision corrections. |
| `multi_agent_matched` on validation hard50 | Specialist roles plus coordinator under same model-call, tool-call, token, and aggregation budget as the single-agent comparator. | Hard50: `22/50` Purist, `24/50` Pragmatic. | No holdout use. | Compared with same-model self-consistency: `0` wins, `10` losses; similar failure families to `single_agent_tools`, especially seizure-free over-selection and rate/cluster burden confusion. | No multi-agent superiority claim. Do not escalate without redesigned role/tool policy and a repeat on the fixed hard50 slice. |

## Failure-Mode Counts From Phase 3

The table below uses the Phase 3 validation750 gpt-4.1-mini taxonomy. Counts are
row-level validation-development evidence only.

| Failure category | Direct labeler | Canonical LLM | `hybrid_structured_events` | CandidateSet hybrid | Close-off implication |
| --- | ---: | ---: | ---: | ---: | --- |
| `freq_category_shift` | 53 | 64 | 26 | 42 | Deterministic normalization absorbs many denominator/format errors for SE, but wrong primary-event selection remains. |
| `unknown_false_pos` | 59 | 35 | 30 | 8 | Fully LLM direct labeling overuses unknown/no-reference; guidance helps GPT but not all models. |
| `seizure_free_false_pos` | 45 | 32 | 5 | 15 | Structured event extraction strongly suppresses seizure-free over-fire for GPT-4.1-mini. |
| `unknown_false_neg` | 20 | 23 | 12 | 8 | All model-owned selection variants can over-compute a rate from uncertain or single-event evidence. |
| `cluster_axis_error` | 7 | 11 | 5 | 11 | Cluster handling remains a shared hard family; CandidateSet assessment can over-promote cluster language. |
| `seizure_free_false_neg` | 2 | 4 | 9 | 4 | SE-specific gap: `last_event_only` can fail to become a seizure-free state when no-events-since language is present. |
| `parse_null` | 0 | 0 | 2 | 0 | SE has rare schema/null failures, but they are small relative to its accuracy and coverage gains. |

## Hard50 Agentic Gate

The validation25 smoke surface saturated, so the fixed validation hard50 slice
is the current decision gate for agentic variants. On that slice:

| Condition | Purist | Pragmatic | Reading |
| --- | ---: | ---: | --- |
| `single_greedy` | `34/50` | `36/50` | Best condition-final performer on the hard slice. |
| `single_self_consistency_temperature` | `32/50` | `34/50` | Matched single-agent comparator; still ahead of tool/multi conditions. |
| `single_agent_tools` | `20/50` | `22/50` | `0` wins and `12` losses versus self-consistency; revise/reject. |
| `multi_agent_matched` | `22/50` | `24/50` | `0` wins and `10` losses versus self-consistency; no superiority claim. |

The hard50 result is the decisive agentic addition to close-off: current
tool-using and multi-agent designs do not improve the promoted direction's hard
families and should not receive full-validation escalation without redesign.

## Paper-Facing Takeaways

1. `hybrid_structured_events` is the best current Gan 2026 close-off candidate
   because it has near-complete rendering, the strongest frozen aggregate read,
   and a clear attribution boundary between LLM extraction and deterministic
   normalization/projection.
2. Fully LLM final-label prediction is a necessary comparator, but the failure
   profile shows that a single final label is too lossy: unknown over-fire,
   seizure-free over-fire, and denominator/category shifts dominate.
3. The deterministic comparator remains important precisely because it exposes
   the validation-to-test generalization problem. Its validation lead does not
   survive the locked aggregate audit.
4. The reset-native CandidateSet hybrid is more auditable but currently pays
   too much in null/routed coverage to become the headline implementation.
5. Agentic tool and multi-agent variants are diagnostic negative controls for
   this cycle. They preserve useful trace contracts, but current prompts/tools
   regress on the fixed hard slice.

## Claim Boundaries

- Validation750 and hard50 findings are validation-development evidence.
- Locked `test450` findings are aggregate-only; this document performs no
  row-level holdout analysis.
- Evidence metrics differ by architecture and should not be compared as a
  single common metric.
- `hybrid_structured_events` must be described as hybrid LLM extraction plus
  deterministic normalization/projection, not as fully LLM-only.
