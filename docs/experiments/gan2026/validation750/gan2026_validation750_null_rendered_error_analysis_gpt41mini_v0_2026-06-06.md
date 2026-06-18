# Gan 2026 Validation750 Null-Rendered Row Error Analysis

Date: 2026-06-06

Scope: the 234 rows in `gan2026_clinical_assessment_projection_render_validation750_gpt41mini_v0_2026-06-06.jsonl` with a `final_rendered_label` object whose `rendered_label` is null. This excludes the 18 invalid clinical-assessment rows that never reached projection/render.

This is a mechanics/error-analysis artifact over validation rows only. It is not a locked-test review or benchmark-comparable claim.

## Artifacts

- Row-level JSONL: `experiments\gan2026_validation750_null_rendered_row_error_analysis_gpt41mini_v0_2026-06-06.jsonl`
- Summary JSON: `experiments\gan2026_validation750_null_rendered_error_analysis_gpt41mini_v0_2026-06-06.json`
- Projection/render source: `experiments\gan2026_clinical_assessment_projection_render_validation750_gpt41mini_v0_2026-06-06.jsonl`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation750_gpt41mini_v3nested_v3_2026-06-06.jsonl`
- Candidate-set source: `experiments\gan2026_validation750_candidate_set_v3_nested_dedupe_2026-06-06.jsonl`
- Route source: `experiments\gan2026_validation750_verification_route_gpt41mini_v0_2026-06-06.jsonl`

## Theme Counts

- `seizure_free_duration_gap`: 114
- `frequency_operands_gap`: 77
- `additive_mixed_window_or_vague`: 24
- `cluster_axis_gap`: 12
- `cyclic_window_without_count`: 5
- `seizure_free_proxy_overreach`: 1
- `unresolved_multiple`: 1

## Theme Diagnoses And Fixes

### `seizure_free_duration_gap` (114)

Diagnosis: Seizure-free selected without renderable duration.

Suggested fix: Improve duration extraction/parsing, require duration-bearing primary candidates where available, and explicitly decide whether durationless seizure-free evidence should abstain or use a named benchmark policy.

### `frequency_operands_gap` (77)

Diagnosis: Frequency assessment lacks parseable count/period operands, often because source language is vague or the normalized phrase was not parser-friendly.

Suggested fix: Improve parser coverage and assessment repair from selected candidates; separate qualitative frequency from numeric renderable frequency.

### `additive_mixed_window_or_vague` (24)

Diagnosis: Additive assessment combines facts that are not safely additive because windows differ, counts are vague, or operands are incomplete.

Suggested fix: Constrain additive_same_window to parsed same-window facts; otherwise use primary_with_context or route as verifier work.

### `cluster_axis_gap` (12)

Diagnosis: Cluster facts lack enough cadence or burden axis information for the cluster renderer.

Suggested fix: Expand cluster-axis parsing and require the assessment to distinguish cluster cadence from events-per-cluster; route unresolved cluster-axis cases.

### `cyclic_window_without_count` (5)

Diagnosis: Cyclic vulnerability windows are selected as burden even though no event count is available.

Suggested fix: Extract the actual event burden inside the cyclic window or keep these rows routed/non-rendered.

### `seizure_free_proxy_overreach` (1)

Diagnosis: Seizure-free evidence is proxy/conditional rather than direct enough to render.

Suggested fix: Keep blocked unless a verifier or named policy accepts the evidence.

### `unresolved_multiple` (1)

Diagnosis: The assessment preserved multiple competing facts without a deterministic label choice.

Suggested fix: Use verifier/action policy; do not silently choose a replacement label.

## Route Coverage

- Routed null-rendered rows: 42 / 234
- `mixed_window_or_vague_addition`: 24
- `cluster_axis_ambiguity`: 12
- `cyclic_window_without_event_count`: 5
- `seizure_free_proxy_evidence_overreach`: 1

## Implementation Priority

1. Seizure-free duration extraction and projection repair.
   This is the largest single theme: 114 / 234 rows. The dominant pattern is a
   clinically valid seizure-free assessment with no renderer-ready duration.
   Examples include explicit date anchors such as "seizure-free since
   29/09/2017", explicit durations such as "over the last year", and vague
   follow-up intervals such as "since last visit". A date/duration parser plus
   an assessment repair that copies duration-bearing candidate evidence would
   address the most rows.

2. Frequency operand parser and assessment repair.
   This covers 77 / 234 rows, mostly ordinary `frequency_rate` rows where the
   source phrase is clinically interpretable but not parser-ready. Examples
   include "occurring once per night", "4 generalised tonic-clonic seizures in
   July", "5 seizure events documented recently", and electrographic rates like
   "~9/h". This is a deterministic normalization gap more than a verifier
   problem.

3. Additive-policy tightening.
   This covers 24 / 234 rows. The LLM often chose `additive_same_window` for
   mixed windows or mixed semiologies, such as daily absences plus monthly
   tonic-clonic seizures. The safest fix is to allow additive rendering only
   when all primary facts have parsed same-window operands; otherwise demote to
   `primary_with_context` or route.

4. Cluster-axis parser and router split.
   This covers 12 cluster-axis rows plus 5 cyclic-window rows. The cluster cases
   need a clearer split between cluster cadence and events-per-cluster. The
   cyclic-window rows should remain routed/non-rendered unless an actual event
   count is present.

5. Preserve verifier-only blockers.
   The single seizure-free proxy-overreach row and the single unresolved-multiple
   row are doing useful safety work. They should stay non-rendered unless a
   named verifier/action policy explicitly accepts them.

## Row-By-Row Diagnosis

| Row | Theme | Kind / Policy | Source phrase | Key issues | Routed | Gold label | Diagnosis | Suggested fix |
|---:|---|---|---|---|---|---|---|---|
| 1695 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no events have been recorded in the current month to date | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | multiple per month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 1706 | `cluster_axis_gap` | `cluster_frequency` / `single_fact` | cluster of short events on multiple days over the past month | vague_count; cluster_cadence_operands_incomplete; projection_semantics_missing | cluster_axis_ambiguity | multiple cluster per month, multiple per cluster | The assessment identified cluster frequency, but cluster cadence or events-per-cluster operands were incomplete/unparsed for rendering. | Expand cluster parser coverage and require cluster_axis only when cadence and burden axes are separable; otherwise project a rate if a direct event rate is pre… |
| 2609 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | occurring once per night | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 1 per day | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 2907 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | Seizure-free since 27 March 2024 | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 6 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 2932 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | seizure-free since 29/09/2017 | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 9 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 2938 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | Seizure-free since 13-Nov-2015 | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 8 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 2965 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | Last seizure on 03-Sep-2017 | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 16 month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 2992 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no seizures since 19-May-2024 | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 7 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 3015 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | no events over the last year | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 12 month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 3118 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | No seizures since last visit | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 3137 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no definite seizure events | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 3356 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | brief generalised tonic–clonic seizures occurring exclusively after nights of curtailed sleep over the past t… | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 3371 | `seizure_free_duration_gap` | `seizure_free` / `primary_with_context` | no events have occurred in the past eight weeks | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | unknown | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 3468 | `cyclic_window_without_count` | `cluster_frequency` / `single_fact` | perimenstrual only (days -2 to +2) | cluster_frequency_operands_unparsed; cluster_cadence_operands_incomplete; cyclic_window_without_event_count; projection_semantics… | cyclic_window_without_event_count | unknown | The row describes a cyclic/high-risk window but lacks a directly renderable event count and period. | Add extraction for actual event burden inside cyclic windows, or keep as abstain/human review when only vulnerability timing is present. |
| 3469 | `cyclic_window_without_count` | `cluster_frequency` / `primary_with_context` | perimenstrual clustering | cluster_frequency_operands_unparsed; cluster_cadence_operands_incomplete; cyclic_window_without_event_count; projection_semantics… | cyclic_window_without_event_count | unknown | The row describes a cyclic/high-risk window but lacks a directly renderable event count and period. | Add extraction for actual event burden inside cyclic windows, or keep as abstain/human review when only vulnerability timing is present. |
| 3482 | `cyclic_window_without_count` | `cluster_frequency` / `single_fact` | Seizures happen when perimenstrual only (days -3 to +3). | cluster_frequency_operands_unparsed; cluster_cadence_operands_incomplete; cyclic_window_without_event_count; projection_semantics… | cyclic_window_without_event_count | unknown | The row describes a cyclic/high-risk window but lacks a directly renderable event count and period. | Add extraction for actual event burden inside cyclic windows, or keep as abstain/human review when only vulnerability timing is present. |
| 3493 | `cyclic_window_without_count` | `cluster_frequency` / `single_fact` | the attacks cluster around her period | cluster_frequency_operands_unparsed; cluster_cadence_operands_incomplete; cyclic_window_without_event_count; projection_semantics… | cyclic_window_without_event_count | unknown | The row describes a cyclic/high-risk window but lacks a directly renderable event count and period. | Add extraction for actual event burden inside cyclic windows, or keep as abstain/human review when only vulnerability timing is present. |
| 3507 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | Frequency reduced by 0.3 after dose increase | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 3512 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | Frequency increased by approximately 20% after dose increase | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 3532 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | generalised tonic-clonic seizures predominantly from sleep with occasional brief absence episodes during the … | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 3534 | `seizure_free_proxy_overreach` | `seizure_free` / `seizure_free_state` | no seizures requiring rescue medication in the past seven months | seizure_free_proxy_evidence_overreach; projection_semantics_missing | seizure_free_proxy_evidence_overreach | unknown | Seizure-free projection was blocked because the support was proxy/conditional rather than direct seizure-frequency evidence. | Keep this routed for verifier/human review; do not render a seizure-free label unless direct seizure-free duration or last-event evidence is extracted. |
| 4345 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | 4 generalised tonic–clonic seizures in July | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 4 per month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 4368 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | 5 seizure events documented recently | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 5 per 2 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 4690 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | Electrographic seizures frequent on EEG (~ten/h) | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | multiple per day | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 4694 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | Electrographic seizures frequent on EEG (~9/h) | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | multiple per day | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 4700 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | Electrographic seizures frequent on EEG (~4/h) | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | multiple per day | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 4709 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | Electrographic seizures frequent on EEG (~6/h) | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | multiple per day | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 4842 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no seizures reported since last appointment | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 4951 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no events for many months | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 4992 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | Seizure-free interval since 12-Sep-2018 | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 11 month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 4994 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | seizure-free interval since 25/06/2021 | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 6 month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 5040 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no further episodes suggestive of seizures | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 6 months | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 5082 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | a sustained period without any recurrence of her typical events | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 5092 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | No clinical seizures observed since the initial referral | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 5110 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no witnessed convulsive episodes recorded by him or observers, nor any events he felt were likely to represen… | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 5121 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | denies blackouts, convulsions, brief lapses, or nocturnal events | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 5136 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | No recurrence | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 5141 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no further events suggestive of seizures since early August | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 5197 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | remain seizure-free since the last consultation | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 5210 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | Seizure freedom continues | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 5221 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no auras, warnings, or witnessed events for an extended period; she cannot recall any episodes since early 20… | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 5248 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | complete seizure control without breakthrough events, nocturnal episodes, or auras | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple year | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 5345 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | he has been free of events for several months | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 5476 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | sporadic epileptic spasms this year | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 5534 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | a very infrequent, short event a fortnight ago | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 1 per multiple month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 5551 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | several episodes per day, predominantly focal events, with occasional generalised breakthroughs approximately… | vague_count; frequency_rate_operands_unparsed; additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection… | mixed_window_or_vague_addition | multiple per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 5791 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | two brief myoclonic jerks on awakening and one generalised tonic–clonic event over the past three months | frequency_rate_operands_unparsed; additive_frequency_count_unparsed; frequency_rate_operands_incomplete; projection_semantics_mis… | mixed_window_or_vague_addition | 1 per month | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 5974 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | Seizures with missed ASM doses, typically occurring within 24–48 hours of a missed levetiracetam dose | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 5996 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | Recent breakthrough events predominantly following lapses in prescribed antiseizure medication | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 6029 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | Ongoing focal seizures less frequent between clusters but not absent | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 6077 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | one breakthrough seizure on 12/09/2025 | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 6131 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | infrequent generalised seizures provoked by patterned or flickering visual stimuli | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 6180 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | brief staring spells with loss of awareness on several occasions each week | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | multiple per week | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 6209 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | daily brief events and 2–3 longer episodes per month | additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | multiple per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 6358 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no events since June 2024 after moderating caffeine and improving sleep | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 15 to 16 months | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 6501 | `cluster_axis_gap` | `cluster_frequency` / `primary_with_context` | brief episodes occurring over 2–3 days | cluster_frequency_operands_unparsed; cluster_cadence_operands_incomplete; projection_semantics_missing | cluster_axis_ambiguity | unknown | The assessment identified cluster frequency, but cluster cadence or events-per-cluster operands were incomplete/unparsed for rendering. | Expand cluster parser coverage and require cluster_axis only when cadence and burden axes are separable; otherwise project a rate if a direct event rate is pre… |
| 6571 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | no further events reported | vague_count; seizure_free_duration_required; projection_semantics_missing |  | unknown | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 6889 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | brief morning myoclonic jerks several times per week; three generalised tonic–clonic seizures in the past six… | vague_count; additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | multiple per week | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 6952 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | approximately twice weekly | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 2 per week | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 7126 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | recurring mid-cycle surge in episodes approximately 10–14 days after menses onset | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 7168 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | intermittent morning myoclonic jerks day-to-day | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 7409 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | focal aware seizures most weeks, occasionally progressing to focal impaired awareness | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 7738 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no events since last notification period | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 7818 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no further events suggestive of seizures | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 2 years | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 7834 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | No further seizure episodes. | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 7859 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | recent period with essentially no breakthrough events | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | unknown | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 7872 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | complete control of seizures since his last review | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 7911 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | Seizures under sustained control | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 7961 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | a sustained period of seizure stability with no impairment of daily activities | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple year | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 8006 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | No seizures or breakthrough events over the past six months | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 8089 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | Sustained remission since 29-May-2023 | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 16 month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 8144 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | a sustained spell without clinical events | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 8145 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | a continued period without events | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 6 month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 8160 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | stable spell without witnessed convulsions | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 8180 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | he has not described any further events suggestive of seizures | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8188 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no episodes since | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8203 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | He described remaining free of his usual attacks over this interval | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8224 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | no witnessed convulsive events or absence episodes | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 8235 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no events recorded or witnessed over the current follow-up period | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8264 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no recorded events, either focal or generalised, during the period monitored | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 4 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8265 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | she has remained without seizures over this interval | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 6 month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 8400 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | durable seizure control over the past several months, with no convulsive events | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8474 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | No events suggestive of seizures | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8512 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | Interval history negative for seizures | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8577 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | no entries for events or auras since 09 March 2024 | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8581 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | absence of clinically concerning episodes over this period | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 8674 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | episode-free on her current routine | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8724 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | No episodes suggestive of seizures since titration to current antiepileptic dose | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8730 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no further episodes and there have been no witnessed attacks | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 6 month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 8794 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no detected seizures over the last 6 months | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 6 month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 8802 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no episodes suggestive of seizures since last review with no witnessed events, nocturnal disturbances, or pos… | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 12 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8805 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no convulsive seizures detected over the past six months | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 8808 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no definite seizures and no witnessed collapses | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 10 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8820 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | no seizures since 29-12-2023 | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 7 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8835 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no seizures since 12 June 2020 | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 10 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8854 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | Seizure cessation following initiation of last ASM | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8893 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | Seizure-free after dose escalation of ASM | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 8922 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | being without further seizures since the most recent dose increase | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 8924 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no recorded events since dose titration | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8938 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | Seizure-free off ASMs since 25 Jun 2015 | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 10 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 8949 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | Drug-free remission since 20-Jun-2021 following a gradual discontinuation of levetiracetam earlier in 2021 du… | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 6 month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 8969 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | Sustained postoperative seizure freedom | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 9063 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | No focal clonic seizures since 19-Mar-2017 | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 8 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 9103 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | infrequent generalised tonic–clonic seizures over the past year | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 9163 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | he is Seizure-free by patient report | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 9190 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no witnessed focal impaired-awareness events or convulsions since late February 2025 | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 9215 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no recognized seizures since early summer | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 9238 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | No definite seizures during this period | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 9250 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no clear-cut events to suggest recent seizures | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 9259 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | clear period without events | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for 1 year | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 9299 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | five focal automatisms per week | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 5 per week | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 9588 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | focal epileptic spasms freedom achieved, with the last brief event described in February 2025 | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 9815 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | generalised tonic–clonic seizures occurring rarely | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | multiple per day | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 9879 | `cluster_axis_gap` | `cluster_frequency` / `single_fact` | brief clusters of events over the past three months | cluster_frequency_operands_unparsed; cluster_cadence_operands_incomplete; projection_semantics_missing | cluster_axis_ambiguity | unknown | The assessment identified cluster frequency, but cluster cadence or events-per-cluster operands were incomplete/unparsed for rendering. | Expand cluster parser coverage and require cluster_axis only when cadence and burden axes are separable; otherwise project a rate if a direct event rate is pre… |
| 9888 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | sporadic complex partial seizures this year | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 9912 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | sporadic simple partial seizures this year | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 9937 | `cluster_axis_gap` | `cluster_frequency` / `single_fact` | periodic bursts roughly every few weeks | cluster_frequency_operands_unparsed; cluster_cadence_operands_incomplete; projection_semantics_missing | cluster_axis_ambiguity | 1 cluster per month, multiple per cluster | The assessment identified cluster frequency, but cluster cadence or events-per-cluster operands were incomplete/unparsed for rendering. | Expand cluster parser coverage and require cluster_axis only when cadence and burden axes are separable; otherwise project a rate if a direct event rate is pre… |
| 10371 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | Prior cluster pattern resolved since 11 Aug 2023 | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple year | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 10434 | `cluster_axis_gap` | `cluster_frequency` / `single_fact` | on several mornings each week | vague_count; cluster_cadence_operands_incomplete; projection_semantics_missing | cluster_axis_ambiguity | multiple cluster per week, 2 to 3 per cluster | The assessment identified cluster frequency, but cluster cadence or events-per-cluster operands were incomplete/unparsed for rendering. | Expand cluster parser coverage and require cluster_axis only when cadence and burden axes are separable; otherwise project a rate if a direct event rate is pre… |
| 10509 | `cyclic_window_without_count` | `cluster_frequency` / `single_fact` | clusters arising after nights of curtailed sleep | cluster_frequency_operands_unparsed; cluster_cadence_operands_incomplete; cyclic_window_without_event_count; projection_semantics… | cyclic_window_without_event_count | unknown | The row describes a cyclic/high-risk window but lacks a directly renderable event count and period. | Add extraction for actual event burden inside cyclic windows, or keep as abstain/human review when only vulnerability timing is present. |
| 10542 | `cluster_axis_gap` | `cluster_frequency` / `single_fact` | two to four absences per cluster over approximately 1 hour | cluster_frequency_operands_unparsed; cluster_cadence_operands_incomplete; projection_semantics_missing | cluster_axis_ambiguity | unknown, 2 to 4 per cluster | The assessment identified cluster frequency, but cluster cadence or events-per-cluster operands were incomplete/unparsed for rendering. | Expand cluster parser coverage and require cluster_axis only when cadence and burden axes are separable; otherwise project a rate if a direct event rate is pre… |
| 10578 | `cluster_axis_gap` | `cluster_frequency` / `single_fact` | three to four focal impaired-awareness seizures per cluster | cluster_frequency_operands_unparsed; cluster_cadence_operands_incomplete; projection_semantics_missing | cluster_axis_ambiguity | unknown, 3 to 4 per cluster | The assessment identified cluster frequency, but cluster cadence or events-per-cluster operands were incomplete/unparsed for rendering. | Expand cluster parser coverage and require cluster_axis only when cadence and burden axes are separable; otherwise project a rate if a direct event rate is pre… |
| 10630 | `cluster_axis_gap` | `cluster_frequency` / `single_fact` | several evenings per fortnight with roughly five short-lived spells per cluster | vague_count; cluster_cadence_operands_incomplete; projection_semantics_missing | cluster_axis_ambiguity | multiple cluster per 2 week, 5 per cluster | The assessment identified cluster frequency, but cluster cadence or events-per-cluster operands were incomplete/unparsed for rendering. | Expand cluster parser coverage and require cluster_axis only when cadence and burden axes are separable; otherwise project a rate if a direct event rate is pre… |
| 11216 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | seizure freedom since 25 December 2023 | vague_count; seizure_free_duration_required; projection_semantics_missing |  | unknown | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 11254 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | no further seizures recorded since last event on 31-May | vague_count; seizure_free_duration_required; projection_semantics_missing |  | unknown | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 11272 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no seizures since last seizure on 20/Dec | vague_count; seizure_free_duration_required; projection_semantics_missing |  | unknown | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 11337 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | one seizure on 06-Nov after missed doses and sleep deprivation | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 11389 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | one focal seizure on 21 December | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 12127 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | several focal non-motor seizures per week and two generalised convulsions per year | vague_count; additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | multiple per week | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12192 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | drop attack on a daily basis, twice weekly focal aware episodes, occasional generalised tonic-clonic seizures | frequency_rate_operands_unparsed; additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_mi… | mixed_window_or_vague_addition | 1 per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12236 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | daily absence seizures and occasional generalised tonic-clonic seizures | frequency_rate_operands_unparsed; additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_mi… | mixed_window_or_vague_addition | 1 per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12314 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | generalised tonic-clonic seizures three nights per week | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 3 per week | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 12366 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | simple partial seizures 4 times per day and tonic-clonic seizures 2 times per month | additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | 4 per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12378 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | focal clonic 4 times per day and tonic-clonic seizures 2 times per month | additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | 4 per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12383 | `unresolved_multiple` | `unresolved_multiple` / `additive_same_window` | focal onset seizures four times per day, drop attacks occurring in batches, tonic-clonic seizures 2 times per… | unresolved_multiple_not_renderable; projection_semantics_missing |  | 4 per day | The assessment preserved multiple competing current facts and no deterministic policy can choose one scorer-facing label. | Route to verifier as a selection/action case; only render after a policy chooses whether to abstain, review, or accept one candidate set. |
| 12403 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | focal aware seizures 2 to 3 times per day and tonic-clonic seizures 2 times per month | additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | 2 to 3 per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12422 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | nightly generalised convulsions seizures and intermittent tonic seizures four times per year | additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | 1 per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12456 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | nightly generalised tonic-clonic seizures plus intermittent tonic seizures three times per year | additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | 1 per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12460 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | nightly generalised convulsions seizures and intermittent tonic seizures two times per year | additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | 1 per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12484 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | one to two generalised tonic-clonic seizures yearly; three to four absences per day | additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | 3 to 4 per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12506 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | one to two generalised tonic-clonic seizures monthly plus 4 absences per day | additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | 4 per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12537 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | up to three generalised tonic-clonic seizures per week, daily drop attacks, and focal impaired-awareness seiz… | additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | 1 per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12551 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | up to 2 generalised tonic-clonic seizures per year; focal impaired-awareness seizures every 4 to 6 weeks; dai… | additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | 1 per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12556 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | 2-3 generalized tonic-clonic seizures per week, daily drop attacks, and focal impaired-awareness seizures eve… | additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | 1 per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12562 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | 3 to 4 generalized tonic-clonic seizures per week, daily drop attacks, and focal impaired-awareness seizures … | additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | 1 per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12573 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | up to two generalised tonic-clonic seizures per month, daily drop attacks, focal impaired-awareness seizures … | additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | 1 per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12584 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | one generalised tonic-clonic seizure every 3 months; weekly absences; atonic and focal impaired awareness sei… | vague_count; additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | 1 per week | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12641 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | one to two generalised tonic-clonic seizures per week; daily absences; focal sensory seizures every three to … | additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | 1 per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12676 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | one to two generalised tonic-clonic seizures per year; daily absences; focal myoclonic with disorientation ev… | additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | 1 per day | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12823 | `additive_mixed_window_or_vague` | `frequency_rate` / `additive_same_window` | nine generalised tonic-clonic seizures this year and focal impaired-awareness seizures every three to four we… | additive_frequency_period_mismatch; frequency_rate_operands_incomplete; projection_semantics_missing | mixed_window_or_vague_addition | 9 per month | The assessment tried to add multiple frequency facts, but the windows/counts were mixed, vague, or incomplete. | Tighten additive selection: only use additive_same_window for parsed same-window rates; otherwise select the dominant current burden as primary_with_context or… |
| 12963 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | episodes have become noticeably fewer | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 13051 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | one generalised tonic-clonic seizure 3 weeks ago after 8 months seizure-free on Levetiracetam | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 2 per 8 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 13114 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | one tonic seizure two weeks ago with preceding brief myoclonic jerks | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 1 per year | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 13190 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | seizure-free for 5 months, then 1 focal impaired-awareness seizure | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 1 per 5 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 13209 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | focal impaired-awareness seizure 2 weeks ago after 8 months seizure-free | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 1 per 8 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 13267 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | one drop attack 3 weeks ago after 5 month remission | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 2 per 5 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 13290 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | two generalised tonic-clonic seizures two Fridays ago, each preceded by myoclonic jerks | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 4 per 6 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 13327 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | seizure free for several years | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple year | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 13485 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | seizure free for a long duration with no reported seizures for several years | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple year | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 13487 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | seizure free for a long duration and has not reported seizures for over several years | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple year | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 13574 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | currently in long-term remission, having been seizure free for years | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple year | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 13595 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | currently in long-term remission, having been seizure free for years | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple year | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 13598 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | currently in long-term remission, having been seizure free for years | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple year | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 13608 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | currently in long-term remission, having been seizure free for years | vague_count; seizure_free_duration_required; projection_semantics_missing |  | seizure free for multiple year | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 13627 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | Seizures occurred on multiple days per month with intermittent clustering and nocturnal tendency. | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 64 per 12 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 13721 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | Seizures on multiple days each month from September 2024 to August 2025, with some months having up to 10 sei… | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 77 per 12 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 13732 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | Seizures occurred on 1 to 11 days per month from August 2024 to March 2025, mostly nocturnal in some months. | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 52 per 8 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 13922 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | she has had two seizures | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 14092 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | 5 myoclonic jerks since last clinic appointment, last on 7 April | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 14096 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | five myoclonic jerks | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 14137 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | 3 - 4 generalised tonic-clonic seizures | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 14146 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | 3 generalised tonic-clonic seizures since starting Clobazam, most recent on 13 October | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | unknown | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 14187 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | She has remained seizure-free since then. | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 2 to 3 per month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 14214 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | She has remained seizure-free since then. | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 2 to 4 per month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 14250 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | No further seizures have occurred since | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 2 per month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 14282 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | No further seizures have occurred since | vague_count; seizure_free_duration_required; projection_semantics_missing |  | multiple per month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 14284 | `seizure_free_duration_gap` | `seizure_free` / `primary_with_context` | No further seizures have occurred since | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 2 to 3 per month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 14317 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | has maintained seizure freedom since early April | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 4 per 2 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 14332 | `seizure_free_duration_gap` | `seizure_free` / `primary_with_context` | She has not had any further events since. | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | 5 per 2 month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 14335 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | three to four seizures around October | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 3 to 4 per 2 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 14383 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | seizure-free status since mid-January | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 3 to 4 per 3 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 14454 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | no seizures since | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 2 per 2 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 14530 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | Two seizures occurred in March and May 2019, both nocturnal | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 2 per 2 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 14540 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | No seizures since starting Levetiracetam | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 2 per 8 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 14562 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no further events reported | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 3 per 6 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 14567 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | three seizures over approximately three months | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 3 per 3 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 14581 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | No further seizures since surgery and initiation of Levetiracetam. | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 2 per 3 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 14587 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | Two nocturnal seizures within three months | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 2 per 3 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 14592 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | Two seizures in June 2024 during sleep | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 3 per 5 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 14611 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | no further episodes since May 2020 | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 2 per 4 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 14635 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no further seizures since starting current regimen at end of November | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 5 per 4 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 14645 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no further events recorded to date | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 2 per 6 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 14672 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | There have been no further episodes since starting her current regimen | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 3 per 8 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 14765 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | no seizures in the past month | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 1 per month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 14806 | `seizure_free_duration_gap` | `seizure_free` / `primary_with_context` | no further episodes in the past month | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | 1 per 2 month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 14810 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | seizure-free for over 4 weeks | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | 1 per month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 14821 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | seizure-free since 24 Jul | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 1 per month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 14872 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | free of seizures for two weeks | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | 1 per month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 14943 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | stable since 21 Feb with no recent seizures | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | 1 per 3 month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 14965 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | last seizure episode on 20 May, stable since | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 1 per 3 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 14973 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | no further absences since early February | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 1 per month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 15004 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | no recurrence for the past months | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 1 per 3 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 15012 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no recurrence of seizures since 31-May | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 1 per 2 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 15029 | `seizure_free_duration_gap` | `seizure_free` / `seizure_free_state` | no recurrence for the past months and overall stable epilepsy | vague_count; seizure_free_duration_required; projection_semantics_missing |  | 1 per 3 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 15094 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | 3 morning jerks since last tonic-clonic seizure in Apr 2022 | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 4 per 13 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 15108 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | 2 to 3 morning jerks since last tonic-clonic seizure in January 2024 | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 3 to 4 per 15 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 15127 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | 4 morning jerks since last tonic-clonic seizure in Feb 2020 | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 5 per 13 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 15129 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | four brief morning jerks since 3/2015 | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 4 per 15 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 15193 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | no generalised seizures since 9 - 2022 | vague_count; seizure_free_duration_required; projection_semantics_missing |  | multiple per 13 month | The LLM selected seizure freedom without a usable duration, so the renderer could not emit a Gan seizure-free interval label. | Require the assessment to select a duration-bearing seizure-free candidate when available; otherwise keep durationless seizure freedom as non-renderable or def… |
| 15242 | `cluster_axis_gap` | `cluster_frequency` / `primary_with_context` | occasional clusters of myoclonic jerks persisting | cluster_frequency_operands_unparsed; cluster_cadence_operands_incomplete; projection_semantics_missing | cluster_axis_ambiguity | multiple cluster per 15 month, multiple per cluster | The assessment identified cluster frequency, but cluster cadence or events-per-cluster operands were incomplete/unparsed for rendering. | Expand cluster parser coverage and require cluster_axis only when cadence and burden axes are separable; otherwise project a rate if a direct event rate is pre… |
| 15262 | `cluster_axis_gap` | `cluster_frequency` / `single_fact` | occasional clusters of myoclonic jerks persisting | cluster_frequency_operands_unparsed; cluster_cadence_operands_incomplete; projection_semantics_missing | cluster_axis_ambiguity | multiple cluster per 13 month, multiple per cluster | The assessment identified cluster frequency, but cluster cadence or events-per-cluster operands were incomplete/unparsed for rendering. | Expand cluster parser coverage and require cluster_axis only when cadence and burden axes are separable; otherwise project a rate if a direct event rate is pre… |
| 15267 | `seizure_free_duration_gap` | `seizure_free` / `single_fact` | No further tonic-clonic seizures have occurred since 06/2017 | seizure_free_duration_unparsed; seizure_free_duration_required; projection_semantics_missing |  | 3 per 14 month | The LLM selected seizure freedom, but the duration phrase was missing or not parsed into duration operands. | Improve seizure-free duration parsing from source_normalized_phrase and candidate evidence; add date/duration extraction when explicit last-event dates support… |
| 15317 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | 2 to 3 single jerks remain | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 2 to 3 per 15 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 15964 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | 3 seizures in sleep and 3 while awake in May | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 11 per 3 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 15966 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | 5 seizures during sleep over 2 months | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 5 per 3 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 15982 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | 8 seizures in July, including 3 nocturnal and 5 while awake | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 9 per 2 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 15986 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | In May she had no seizures during sleep and one while awake | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 11 per 3 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 15992 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | 3 to 4 daytime seizures per month, no nocturnal seizures | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 7 per 2 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 15997 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | Six seizures in January, including five nocturnal and one daytime | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 10 per 3 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 16021 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | five seizures in sleep in April, none while awake | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 9 per 3 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 16084 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | no seizures so far this month | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 8 per 4 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 16133 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | 6 seizure events in September | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 18 per 4 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 16195 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | 6 seizures so far this month | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 16 per 4 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 16220 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | no seizures this month so far | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 11 per 4 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 16450 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | events approximately every several days | vague_count; frequency_rate_operands_incomplete; projection_semantics_missing |  | 1 per multiple day | The row is a frequency-rate assessment with vague or qualitative count language that deterministic rendering cannot map to a number. | Add explicit vague-count policy for benchmark-compatible phrases where safe, and prompt/repair source_normalized_phrase to preserve parseable count+period when… |
| 16574 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | approximately one seizure cluster per month | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 1 per 4 day | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 16674 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | four short absences in a cluster in April, two brief absences in July, and one in September | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 7 per 6 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 16697 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | Three seizures recorded over six months: September, November, and February | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 3 per 6 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 16704 | `frequency_operands_gap` | `frequency_rate` / `single_fact` | seven myoclonic jerks documented in September over three months | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 9 per 6 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 16719 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | early morning myoclonus about once weekly | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 7 per 6 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 16758 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | 3 brief absences in Dec, 5 drop attacks in Mar, and 1 tonic seizure in Apr | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 9 per 5 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 16833 | `frequency_operands_gap` | `frequency_rate` / `primary_with_context` | 5 drop attacks in October, 2 myoclonic jerks in December, and a prolonged event in July | frequency_rate_operands_unparsed; frequency_rate_operands_incomplete; projection_semantics_missing |  | 8 per 6 month | The row is a frequency-rate assessment, but count or period operands were missing/unparsed. | Improve deterministic parsing of source_normalized_phrase and candidate source_phrase; add assessment repair that copies parseable operands from the selected c… |
| 16839 | `cluster_axis_gap` | `cluster_frequency` / `additive_same_window` | Clusters of 4 seizures in December and February | cluster_frequency_operands_unparsed; cluster_cadence_operands_incomplete; projection_semantics_missing | cluster_axis_ambiguity | 9 per 4 month | The assessment identified cluster frequency, but cluster cadence or events-per-cluster operands were incomplete/unparsed for rendering. | Expand cluster parser coverage and require cluster_axis only when cadence and burden axes are separable; otherwise project a rate if a direct event rate is pre… |
| 16907 | `cluster_axis_gap` | `cluster_frequency` / `primary_with_context` | run of six seizures within half an hour | cluster_frequency_operands_unparsed; cluster_cadence_operands_incomplete; projection_semantics_missing | cluster_axis_ambiguity | 9 per 6 month | The assessment identified cluster frequency, but cluster cadence or events-per-cluster operands were incomplete/unparsed for rendering. | Expand cluster parser coverage and require cluster_axis only when cadence and burden axes are separable; otherwise project a rate if a direct event rate is pre… |

## Evidence Appendix

### Row 1695 - `seizure_free_duration_gap`

- Gold label: `multiple per month`
- Gold reference: several focal seizures last month
- Assessment: The patient had a handful of short focal seizures in the previous month but has been seizure-free in the current month to date. Seizures remain brief, focal aware, and without secondary generalization. Triggers include sleep deprivation and stress related to caregiving demands. No injuries or hospital attendances reported. Safety measures and medication remain unchanged. Follow-up planned in six months or sooner if seizure frequency increases.
- Source normalized phrase: `no events have been recorded in the current month to date`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:1695:1` supporting, `unknown_frequency`, `recent`, `llm_candidate`: a handful of short focal events during the previous month
- `llm:1695:2` primary, `seizure_free`, `current`, `llm_candidate`: In the current month to date, no events have been recorded

### Row 1706 - `cluster_axis_gap`

- Gold label: `multiple cluster per month, multiple per cluster`
- Gold reference: several focal seizures last month
- Assessment: The patient reports clusters of brief seizures occurring on multiple days within the past month. No clear triggers identified. Medication adjustment planned with follow-up in 12 weeks.
- Source normalized phrase: `cluster of short events on multiple days over the past month`
- Projection issues: `vague_count, vague_count, cluster_cadence_operands_incomplete`
- Route families: `cluster_axis_ambiguity`

Candidate evidence:

- `det:1706:1` primary, `cluster_frequency`, `unclear`, `deterministic_candidate`: Over the past month, the patient reports a cluster of short events on multiple days

### Row 2609 - `frequency_operands_gap`

- Gold label: `1 per day`
- Gold reference: once per night
- Assessment: The patient reports nocturnal seizures occurring once per night on average over the past three months, with a suspected catamenial clustering pattern increasing frequency and intensity around menstruation. Daytime events are rare and absent in the last eight weeks. Current medication includes lamotrigine with no clear change in events. Ambulatory EEG planned to further characterize events and guide management.
- Source normalized phrase: `occurring once per night`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:2609:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: occurring once per night
- `llm:2609:1` supporting, `frequency_rate`, `recent`, `llm_candidate`: She reports nocturnal episodes occurring once per night on average for the past three months

### Row 2907 - `seizure_free_duration_gap`

- Gold label: `seizure free for 6 month`
- Gold reference: Seizure-free since 27 March 2024
- Assessment: Patient has been seizure-free since 27 March 2024 as per patient and collateral reports, indicating satisfactory current control. No recent seizures reported. Management includes ongoing antiseizure medication and monitoring.
- Source normalized phrase: `Seizure-free since 27 March 2024`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:2907:1` primary, `seizure_free`, `recent`, `llm_candidate`: Seizure-free since 27 March 2024 as per patient and collateral reports.

### Row 2932 - `seizure_free_duration_gap`

- Gold label: `seizure free for 9 month`
- Gold reference: Seizure-free since 29/09/2017
- Assessment: The patient has been seizure-free since 29/09/2017, representing a clear improvement compared to earlier in the year when multiple seizures occurred monthly. Historical seizure frequency in February included eight seizures and in March eight seizures, prior to dietary optimization and trigger avoidance.
- Source normalized phrase: `seizure-free since 29/09/2017`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:2932:1` primary, `seizure_free`, `recent`, `llm_candidate`: Importantly, Liam Carter has been seizure‑free since 29/09/2017.
- `llm:2932:2` supporting, `frequency_rate`, `historical`, `llm_candidate`: in February she had five seizures during sleep and three while awake

### Row 2938 - `seizure_free_duration_gap`

- Gold label: `seizure free for 8 month`
- Gold reference: Seizure-free since 13-Nov-2015
- Assessment: Patient reports being seizure-free since 13-Nov-2015 with prior occasional clusters related to sleep loss. Current management includes lamotrigine and trigger avoidance. No neurological deficits noted. No routine follow-up arranged; plan to review if breakthrough events occur.
- Source normalized phrase: `Seizure-free since 13-Nov-2015`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:2938:1` primary, `seizure_free`, `historical`, `llm_candidate`: He reports that he has been Seizure-free since 13-Nov-2015.

### Row 2965 - `seizure_free_duration_gap`

- Gold label: `seizure free for 16 month`
- Gold reference: Last seizure on 03-Sep-2017
- Assessment: The patient has sustained seizure freedom since September 2017, with no confirmed events reported since that date. Prior fluctuating seizure pattern is historical and not current. Improved sleep and reduced fatigue likely contribute to seizure stability.
- Source normalized phrase: `Last seizure on 03-Sep-2017`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:2965:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: Last seizure on 03-Sep-2017
- `det:2965:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no events since
- `llm:2965:2` supporting, `seizure_free`, `recent`, `llm_candidate`: Overall, his condition is improving, with sustained seizure freedom since September 2017, better sleep, reduced fatigue, and improved quality of life under the current regimen and work pattern.
- `det:2965:4` rejected, `frequency_rate`, `unclear`, `deterministic_candidate`: 4–5 times per week
- `det:2965:5` rejected, `unknown_frequency`, `unclear`, `deterministic_candidate`: Last seizure
- `llm:2965:1` rejected, `unknown_frequency`, `historical`, `llm_candidate`: he can sometimes go nearly a week without seizures, but when they recur he tends to have several in one day, often between 4 and 8.
- `llm:2965:3` supporting, `last_event_only`, `historical`, `llm_candidate`: Last seizure on 03-Sep-2017.

### Row 2992 - `seizure_free_duration_gap`

- Gold label: `seizure free for 7 month`
- Gold reference: Last seizure on 19-May-2024
- Assessment: The patient had a single seizure on 19-May-2024 and has had no further events since then. He continues on stable levetiracetam therapy with no rescue medication use required in the past year. Occupational triggers are managed with workplace adjustments and safety precautions. The patient is advised to report any recurrence, clustering, or generalization of events promptly.
- Source normalized phrase: `no seizures since 19-May-2024`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:2992:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: last seizure on 19-May-2024
- `llm:2992:2` primary, `seizure_free`, `recent`, `llm_candidate`: He has had no further events since that date
- `det:2992:3` rejected, `unknown_frequency`, `unclear`, `deterministic_candidate`: last seizure
- `llm:2992:1` supporting, `last_event_only`, `recent`, `llm_candidate`: his last seizure on 19-May-2024 occurred during rigging and programming with a rapid strobe sequence
- `llm:2992:3` supporting, `unknown_frequency`, `current`, `llm_candidate`: He works as a stage lighting technician with frequent exposure to strobe and high-intensity lights, and colleagues have occasionally witnessed events at work
- `llm:2992:4` supporting, `unknown_frequency`, `unclear`, `llm_candidate`: He knows to contact the clinic if symptoms return, particularly if events cluster or generalise

### Row 3015 - `seizure_free_duration_gap`

- Gold label: `seizure free for 12 month`
- Gold reference: Last seizure on 12-Apr-2023
- Assessment: The patient reports no seizures over the last year, with the last seizure on 12-Apr-2023. There have been no episodes of loss of awareness, injuries, or auras since that date. This indicates stable seizure freedom. The last seizure date is noted but not used as primary frequency evidence.
- Source normalized phrase: `no events over the last year`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:3015:1` primary, `seizure_free`, `recent`, `llm_candidate`: He reports no events over the last year, with the last seizure on 12-Apr-2023.
- `det:3015:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no episodes of loss of awareness, injuries, or auras since
- `det:3015:3` rejected, `unknown_frequency`, `unclear`, `deterministic_candidate`: last seizure
- `llm:3015:2` supporting, `last_event_only`, `recent`, `llm_candidate`: He reports no events over the last year, with the last seizure on 12-Apr-2023.

### Row 3118 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No seizures since last visit
- Assessment: Patient reports no seizures since last visit with good medication adherence and no adverse effects; stable on levetiracetam.
- Source normalized phrase: `No seizures since last visit`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:3118:1` primary, `seizure_free`, `recent`, `llm_candidate`: No seizures since last visit

### Row 3137 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No seizures since last visit
- Assessment: The patient reports no definite seizure events since the last appointment, feeling back to baseline with no witnessed episodes. Two recent ED presentations were for non-epileptic events (light-headedness and dissociation) with no epileptic features observed.
- Source normalized phrase: `no definite seizure events`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:3137:1` primary, `seizure_free`, `recent`, `llm_candidate`: Since the last appointment, the patient reports no definite seizure events; he describes feeling "back to baseline" with no witnessed episodes.
- `llm:3137:2` supporting, `unknown_frequency`, `recent`, `llm_candidate`: Two recent Emergency Department presentations were recorded in triage, primarily for light-headedness and a brief episode of dissociation while at work.

### Row 3356 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: Only with sleep deprivation
- Assessment: Seizures occur only after nights of curtailed sleep with no events reported when sleep is adequate, indicating a clear sleep-related trigger and otherwise stable control. The carer maintains a detailed seizure and sleep log. Medication adjustments aim to improve nocturnal coverage and minimize daytime sedation.
- Source normalized phrase: `brief generalised tonic–clonic seizures occurring exclusively after nights of curtailed sleep over the past three months`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:3356:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no events reported
- `llm:3356:1` primary, `frequency_rate`, `recent`, `llm_candidate`: brief generalised tonic–clonic seizures occurring exclusively after nights of curtailed sleep

### Row 3371 - `seizure_free_duration_gap`

- Gold label: `unknown`
- Gold reference: Only with sleep deprivation
- Assessment: The patient has been seizure-free for the past eight weeks except for focal impaired awareness seizures triggered by significant sleep deprivation, with the last event on 10 September 2025. No generalised tonic-clonic seizures reported.
- Source normalized phrase: `no events have occurred in the past eight weeks`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:3371:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: No generalised tonic–clonic seizures reported
- `det:3371:2` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: The last event was on 10 September
- `det:3371:3` supporting, `unknown_frequency`, `unclear`, `deterministic_candidate`: only when significantly short on sleep
- `llm:3371:1` primary, `frequency_rate`, `recent`, `llm_candidate`: outside of nights with curtailed rest, no events have occurred in the past eight weeks.
- `llm:3371:2` supporting, `last_event_only`, `recent`, `llm_candidate`: The last event was on 10 September 2025 after an overnight shift and early start the following day.

### Row 3468 - `cyclic_window_without_count`

- Gold label: `unknown`
- Gold reference: Seizures happen when perimenstrual only (days -2 to +2)
- Assessment: The patient experiences seizures exclusively during the perimenstrual period (days -2 to +2) with seizure freedom outside this window, consistent over six cycles and corroborated by her partner. This predictable catamenial clustering informs current management and follow-up plans.
- Source normalized phrase: `perimenstrual only (days -2 to +2)`
- Projection issues: `cluster_frequency_operands_unparsed, cluster_cadence_operands_incomplete, cyclic_window_without_event_count`
- Route families: `cyclic_window_without_event_count`

Candidate evidence:

- `llm:3468:1` primary, `cluster_frequency`, `current`, `llm_candidate`: Importantly, she observes a clear and consistent catamenial pattern: Seizures happen when perimenstrual only (days -2 to +2). Outside this window she remains seizure-free. She has tracked this pattern over the last six menstrual cycles, and
- `llm:3468:2` supporting, `seizure_free`, `current`, `llm_candidate`: Importantly, she observes a clear and consistent catamenial pattern: Seizures happen when perimenstrual only (days -2 to +2). Outside this window she remains seizure-free. She has tracked this pattern over the last six menstrual cycles, and

### Row 3469 - `cyclic_window_without_count`

- Gold label: `unknown`
- Gold reference: Seizures happen when perimenstrual only (days -3 to +3)
- Assessment: Seizures occur exclusively during the perimenstrual window with no events reported outside this period over the last six months. Peer observations describe brief behavioural arrest events. No consistent aura reported. Safety measures and further EEG investigations planned.
- Source normalized phrase: `perimenstrual clustering`
- Projection issues: `cluster_frequency_operands_unparsed, cluster_cadence_operands_incomplete, cyclic_window_without_event_count`
- Route families: `cyclic_window_without_event_count`

Candidate evidence:

- `det:3469:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no events over the last six months
- `det:3469:2` rejected, `seizure_free`, `unclear`, `deterministic_candidate`: No consistent aura reported
- `det:3469:3` supporting, `unknown_frequency`, `unclear`, `deterministic_candidate`: Seizures happen when perimenstrual only (days -3 to +3)
- `llm:3469:1` primary, `cluster_frequency`, `current`, `llm_candidate`: Given the clear perimenstrual clustering, we will ask her to maintain a detailed diary aligned to cycle days and to share peer-witnessed descriptions where available.
- `llm:3469:2` supporting, `frequency_rate`, `recent`, `llm_candidate`: Outside this window she and the group report no events over the last six months.

### Row 3482 - `cyclic_window_without_count`

- Gold label: `unknown`
- Gold reference: Seizures happen when perimenstrual only (days -3 to +3)
- Assessment: The patient's seizures occur exclusively during the perimenstrual window (days -3 to +3), indicating a clear cyclical cluster pattern. No seizures occur outside this window. The candidate indicating seizures every 12 weeks is rejected as it refers to review frequency, not seizure frequency. The perimenstrual pattern candidate is supported as context.
- Source normalized phrase: `Seizures happen when perimenstrual only (days -3 to +3).`
- Projection issues: `cluster_frequency_operands_unparsed, cluster_cadence_operands_incomplete, cyclic_window_without_event_count`
- Route families: `cyclic_window_without_event_count`

Candidate evidence:

- `det:3482:1` rejected, `frequency_rate`, `unclear`, `deterministic_candidate`: every 12 weeks
- `det:3482:2` supporting, `unknown_frequency`, `unclear`, `deterministic_candidate`: Seizures happen when perimenstrual only (days -3 to +3)
- `llm:3482:1` primary, `cluster_frequency`, `current`, `llm_candidate`: Seizures happen when perimenstrual only (days -3 to +3).

### Row 3493 - `cyclic_window_without_count`

- Gold label: `unknown`
- Gold reference: Seizures happen when perimenstrual only (days -3 to +3)
- Assessment: The patient experiences recurrent seizure-like events that cluster temporally around her menstrual period, with a vulnerability window starting a few days before bleeding and extending to three days after. Outside this peri-menstrual interval, events are rare. This cyclical pattern is corroborated by her partner's observations and her own tracking logs. Further ambulatory EEG and MRI are planned to better characterize the events and confirm the pattern.
- Source normalized phrase: `the attacks cluster around her period`
- Projection issues: `cluster_frequency_operands_unparsed, cluster_cadence_operands_incomplete, cyclic_window_without_event_count`
- Route families: `cyclic_window_without_event_count`

Candidate evidence:

- `llm:3493:1` primary, `cluster_frequency`, `current`, `llm_candidate`: She notes that the attacks cluster around her period, with the window of vulnerability beginning a few days prior to bleeding and extending into the early days thereafter. Outside that peri-period interval, she seldom experiences events. Sh

### Row 3507 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: Frequency reduced by 0.3 after dose increase
- Assessment: The patient's seizure frequency has decreased by 0.3 following an increase in lamotrigine dosage, indicating improved control. No new adverse effects reported; occupational health confirms fewer near-miss episodes at work.
- Source normalized phrase: `Frequency reduced by 0.3 after dose increase`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:3507:1` primary, `frequency_rate`, `recent`, `llm_candidate`: Frequency reduced by 0.3 after dose increase

### Row 3512 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: Frequency increased by ~20% after dose increase
- Assessment: The patient reports a 20% increase in seizure frequency following a recent antiseizure medication dose increase. Events remain brief with preserved awareness in some instances and no associated injury or new neurological deficits. No emergency interventions or status epilepticus have occurred. Triggers include poor sleep and intercurrent illness as previously noted. The ketogenic diet is well maintained with stable ketone levels. No medication changes were made at this visit; follow-up planned to monitor seizure pattern and medication rationale.
- Source normalized phrase: `Frequency increased by approximately 20% after dose increase`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:3512:1` primary, `frequency_rate`, `recent`, `llm_candidate`: Frequency increased by ~20% after dose increase.

### Row 3532 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: Frequency increased by ~20% after dose increase
- Assessment: The patient currently experiences generalised tonic-clonic seizures predominantly from sleep with occasional brief absence episodes during the day. There has been a recent ~20% increase in frequency after levetiracetam dose increase, likely related to sleep deprivation and shift work.
- Source normalized phrase: `generalised tonic-clonic seizures predominantly from sleep with occasional brief absence episodes during the day`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:3532:1` primary, `frequency_rate`, `current`, `llm_candidate`: typical events remain generalised tonic‑clonic seizures occurring predominantly from sleep, with occasional brief absence episodes during the day
- `llm:3532:2` supporting, `frequency_rate`, `recent`, `llm_candidate`: Frequency increased by ~20% after dose increase

### Row 3534 - `seizure_free_proxy_overreach`

- Gold label: `unknown`
- Gold reference: Better over the past seven months
- Assessment: The patient reports improved seizure control with no seizures requiring rescue medication in the past seven months. No generalised convulsive activity was documented during recent ED visits. She continues levetiracetam with good tolerability and no changes are required. Occasional sleep disruption related to shift work is noted but does not currently impact seizure control.
- Source normalized phrase: `no seizures requiring rescue medication in the past seven months`
- Projection issues: `seizure_free_proxy_evidence_overreach`
- Route families: `seizure_free_proxy_evidence_overreach`

Candidate evidence:

- `det:3534:1` rejected, `frequency_rate`, `unclear`, `deterministic_candidate`: this year for possible auras and one episode
- `det:3534:2` supporting, `unknown_frequency`, `unclear`, `deterministic_candidate`: Better over the past seven months
- `llm:3534:1` supporting, `seizure_free`, `recent`, `llm_candidate`: no changes required. If breakthrough events recur, we will consider serum levels and alternative add‑on therapy; she will contact us sooner via the epilepsy nurse line if this occurs.
- `llm:3534:2` primary, `seizure_free`, `recent`, `llm_candidate`: not required in the past seven months.

### Row 4345 - `frequency_operands_gap`

- Gold label: `4 per month`
- Gold reference: Seizure events on 07-03, 07-07, 07-10, 07-18
- Assessment: The patient experienced 4 brief generalised tonic–clonic seizures in July, likely triggered by sleep deprivation, heat, and a missed medication dose. Prior to July, he was seizure-free since late March. No injuries or emergency attendances occurred. Management focuses on adherence, sleep hygiene, and monitoring before considering medication changes.
- Source normalized phrase: `4 generalised tonic–clonic seizures in July`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:4345:2` supporting, `seizure_free`, `historical`, `llm_candidate`: Prior to July, he had been seizure-free since late March.
- `llm:4345:1` primary, `frequency_rate`, `recent`, `llm_candidate`: Seizure events on 07-03, 07-07, 07-10, 07-18 were documented, each described as brief generalised tonic–clonic episodes lasting under 2 minutes, with post-ictal fatigue for several hours and no tongue biting reported on two of the dates.

### Row 4368 - `frequency_operands_gap`

- Gold label: `5 per 2 month`
- Gold reference: Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24
- Assessment: The patient has had 5 seizure events documented recently in the seizure diary, with some events associated with missed medication doses and intercurrent illness. No family history of seizures is reported. Further investigations with EEG and MRI are planned to characterize the seizure pattern and guide treatment.
- Source normalized phrase: `5 seizure events documented recently`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:4368:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no family history of seizures reported
- `llm:4368:1` primary, `frequency_rate`, `recent`, `llm_candidate`: Regarding recent frequency, the seizure diary documents: Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24.

### Row 4690 - `frequency_operands_gap`

- Gold label: `multiple per day`
- Gold reference: Electrographic seizures frequent on EEG (~ten/h)
- Assessment: The patient has frequent electrographic seizures on EEG (~10 per hour) despite no witnessed convulsions reported since last contact, indicating ongoing cortical hyperexcitability under current treatment.
- Source normalized phrase: `Electrographic seizures frequent on EEG (~ten/h)`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:4690:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no witnessed convulsions since
- `llm:4690:1` primary, `frequency_rate`, `recent`, `llm_candidate`: Electrographic seizures frequent on EEG (~ten/h).

### Row 4694 - `frequency_operands_gap`

- Gold label: `multiple per day`
- Gold reference: Electrographic seizures frequent on EEG (~9/h)
- Assessment: The patient exhibits frequent electrographic seizures on EEG approximately 9 per hour, primarily subclinical with rare brief behavioral arrest. Carer logs do not capture these events consistently. No medication changes were made pending further correlation and review.
- Source normalized phrase: `Electrographic seizures frequent on EEG (~9/h)`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:4694:1` primary, `frequency_rate`, `recent`, `llm_candidate`: Electrographic seizures frequent on EEG (~9/h)

### Row 4700 - `frequency_operands_gap`

- Gold label: `multiple per day`
- Gold reference: Electrographic seizures frequent on EEG (~4/h)
- Assessment: The patient experiences frequent electrographic seizures approximately 4 per hour on EEG, mostly subclinical or with brief behavioral arrest. No clear precipitant identified, though poor sleep and missed meals may trigger clusters. Current antiseizure therapy adherence is maintained with ongoing monitoring and safety advice.
- Source normalized phrase: `Electrographic seizures frequent on EEG (~4/h)`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:4700:1` primary, `frequency_rate`, `recent`, `llm_candidate`: Electrographic seizures frequent on EEG (~4/h)

### Row 4709 - `frequency_operands_gap`

- Gold label: `multiple per day`
- Gold reference: Electrographic seizures frequent on EEG (~6/h)
- Assessment: The patient has frequent electrographic seizures approximately 6 per hour on EEG, indicating a high seizure burden. They report variable days with clusters, particularly in the late afternoon, which provides contextual information but is not additive to the primary frequency assessment. The seizures are drug-resistant focal epilepsy with photosensitivity and triggers including flickering lights and sleep deprivation.
- Source normalized phrase: `Electrographic seizures frequent on EEG (~6/h)`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:4709:1` primary, `frequency_rate`, `recent`, `llm_candidate`: Electrographic seizures frequent on EEG (~6/h).
- `llm:4709:2` supporting, `unknown_frequency`, `recent`, `llm_candidate`: Since the last review, they report variable days with clusters, particularly late afternoon.

### Row 4842 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Seizure freedom achieved
- Assessment: Patient reports no seizures since last visit with no rescue medication or emergency presentations; current anti-seizure therapy unchanged and adherence good. Anxiety and low mood persist but are improving. Neurological exam unremarkable. Safety advice reinforced.
- Source normalized phrase: `no seizures reported since last appointment`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:4842:1` primary, `seizure_free`, `recent`, `llm_candidate`: she has not experienced any seizures

### Row 4951 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Seizure remission
- Assessment: The patient reports a settled period with no seizures for many months, with no events recorded since February 2025 and feeling largely episode-free since late winter. This indicates sustained seizure freedom under current management.
- Source normalized phrase: `no events for many months`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:4951:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no events for many months; she feels she has been largely episode-free since
- `llm:4951:3` supporting, `seizure_free`, `recent`, `llm_candidate`: no entries for events since February 2025
- `llm:4951:1` primary, `seizure_free`, `recent`, `llm_candidate`: The patient describes a settled period with no events for many months
- `llm:4951:2` supporting, `seizure_free`, `recent`, `llm_candidate`: she feels she has been largely episode-free since late winter

### Row 4992 - `seizure_free_duration_gap`

- Gold label: `seizure free for 11 month`
- Gold reference: Seizure-free interval since 12-Sep-2018
- Assessment: The patient has been seizure-free since 12-Sep-2018 following VNS optimization and medication adherence. Prior seizure frequency was every 8 days on average, now no seizures reported. No rescue medication needed and no adverse effects noted. Continued current management planned.
- Source normalized phrase: `Seizure-free interval since 12-Sep-2018`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:4992:2` primary, `seizure_free`, `recent`, `llm_candidate`: In contrast, there has been a Seizure-free interval since 12-Sep-2018, which they attribute to the combination of the adjusted VNS parameters and consistent adherence to the existing medication regimen.
- `llm:4992:1` supporting, `frequency_rate`, `historical`, `llm_candidate`: Prior to that optimisation, seizures were occurring every 8 days on average.

### Row 4994 - `seizure_free_duration_gap`

- Gold label: `seizure free for 6 month`
- Gold reference: Seizure-free interval since 25/06/2021
- Assessment: Patient reports excellent stability with no seizures since 25 June 2021, no myoclonic jerks, absences, or nocturnal events. Medication is stable with valproate. No injuries or emergency visits. Safety measures and workplace accommodations in place.
- Source normalized phrase: `seizure-free interval since 25/06/2021`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:4994:1` primary, `seizure_free`, `current`, `llm_candidate`: She reports excellent stability with a seizure-free interval since 25/06/2021.

### Row 5040 - `seizure_free_duration_gap`

- Gold label: `seizure free for 6 months`
- Gold reference: Event-free
- Assessment: The patient reports no seizures since last review on 10 March 2025, indicating ongoing seizure freedom on current medication regimen.
- Source normalized phrase: `no further episodes suggestive of seizures`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:5040:1` primary, `seizure_free`, `recent`, `llm_candidate`: Since I last saw him on 10 March 2025, he reports no further episodes suggestive of seizures.

### Row 5082 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No breakthrough seizures
- Assessment: The patient reports a sustained period without any recurrence of typical seizures, indicating stable seizure control. Historical seizures from 2017 are noted but not current. No antiepileptic drugs are in use, and no recent seizures have been reported.
- Source normalized phrase: `a sustained period without any recurrence of her typical events`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:5082:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no similar episodes reported
- `llm:5082:1` primary, `seizure_free`, `current`, `llm_candidate`: she reports a sustained period without any recurrence of her typical events
- `llm:5082:2` rejected, `last_event_only`, `historical`, `llm_candidate`: prior to this improvement she experienced her first seizure in February 2017
- `llm:5082:3` rejected, `last_event_only`, `historical`, `llm_candidate`: A second event occurred in June 2017 at home in France during sleep, lasting approximately three minutes with the same clinical features
- `llm:5082:4` supporting, `frequency_rate`, `recent`, `llm_candidate`: There have been no similar episodes reported in recent months

### Row 5092 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No clinical seizures observed
- Assessment: The patient has no evidence of epilepsy and no clinical seizures observed since initial referral, consistent with a seizure-free state.
- Source normalized phrase: `No clinical seizures observed since the initial referral`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:5092:1` primary, `seizure_free`, `historical`, `llm_candidate`: No clinical seizures observed since the initial referral.
- `llm:5092:2` supporting, `seizure_free`, `historical`, `llm_candidate`: No clinical seizures observed.

### Row 5110 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No clinical seizures observed
- Assessment: The patient has maintained a detailed seizure diary from July to September 2025 with no witnessed or self-reported clinical seizures, indicating seizure freedom during this period. He reports occasional brief lapses of uncertain significance but no definite seizures. No medication changes are planned given this stability.
- Source normalized phrase: `no witnessed convulsive episodes recorded by him or observers, nor any events he felt were likely to represent clinical seizures`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:5110:1` primary, `seizure_free`, `recent`, `llm_candidate`: Review of his paper diary from 01 July 2025 to 30 September 2025 shows regular entries without gaps. Across this interval, there have been no witnessed convulsive episodes recorded by him or observers, nor any events he felt were likely to

### Row 5121 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No clinical seizures observed
- Assessment: Patient reports no events suggestive of seizures or auras since last review; she and her partner have not witnessed any episodes. She feels well and denies blackouts, convulsions, brief lapses, or nocturnal events. No antiseizure medication is currently prescribed. Plan is continued watchful monitoring with routine follow-up in 6-9 months.
- Source normalized phrase: `denies blackouts, convulsions, brief lapses, or nocturnal events`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:5121:1` supporting, `seizure_free`, `recent`, `llm_candidate`: Patient reports no events suggestive of seizures, warnings, or auras since last review; she and her partner have not witnessed any episodes.
- `llm:5121:2` primary, `seizure_free`, `current`, `llm_candidate`: She feels well and denies blackouts, convulsions, brief lapses, or nocturnal events.

### Row 5136 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No recurrence
- Assessment: The patient has had no seizure recurrence during the interval, corroborated by smartwatch data and diary entries.
- Source normalized phrase: `No recurrence`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:5136:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: No recurrence
- `llm:5136:2` supporting, `seizure_free`, `recent`, `llm_candidate`: No recurrence is therefore recorded during this interval

### Row 5141 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No recurrence
- Assessment: Patient reports no seizures since early August following improved sleep with night-time childcare support; no auras or warnings since then, indicating stable seizure freedom.
- Source normalized phrase: `no further events suggestive of seizures since early August`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:5141:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no auras or warnings since
- `llm:5141:1` primary, `seizure_free`, `recent`, `llm_candidate`: Since night-time childcare support began in mid-August and sleep has become more regular, there have been no further events suggestive of seizures; she describes the last episode as occurring in early August.

### Row 5197 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: remains seizure-free
- Assessment: The patient reports excellent day-to-day functioning and remains seizure-free since the last consultation, with no new neurological symptoms or medication side effects. Safety advice and medication adherence were confirmed.
- Source normalized phrase: `remain seizure-free since the last consultation`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:5197:1` primary, `seizure_free`, `current`, `llm_candidate`: remain seizure-free since the last consultation

### Row 5210 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Seizure freedom continues
- Assessment: The patient with generalised epilepsy and photosensitivity reports continued seizure freedom attributed to adherence and trigger avoidance, with no recent seizures or events reported. No medication changes are planned given sustained remission and tolerability.
- Source normalized phrase: `Seizure freedom continues`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:5210:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: Seizure freedom continues

### Row 5221 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Seizure freedom continues
- Assessment: The patient reports no seizures or auras since early 2024, indicating sustained seizure freedom. Lamotrigine therapy is ongoing with good adherence and no adverse effects.
- Source normalized phrase: `no auras, warnings, or witnessed events for an extended period; she cannot recall any episodes since early 2024`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:5221:1` primary, `seizure_free`, `historical`, `llm_candidate`: The patient reports no auras, warnings, or witnessed events for an extended period; she cannot recall any episodes since early 2024.

### Row 5248 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple year`
- Gold reference: Complete seizure control
- Assessment: The patient reports complete seizure control since starting Levetiracetam in March 2023, with no breakthrough seizures, nocturnal episodes, or auras. Safety advice and medication adherence are reinforced. Mood symptoms are managed separately and do not impact seizure burden assessment.
- Source normalized phrase: `complete seizure control without breakthrough events, nocturnal episodes, or auras`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:5248:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: complete seizure control
- `llm:5248:1` primary, `seizure_free`, `current`, `llm_candidate`: Since starting Levetiracetam in March 2023, he reports complete seizure control without breakthrough events, nocturnal episodes, or auras.

### Row 5345 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Stable without seizures
- Assessment: The patient has been consistently free of seizures for several months, with no witnessed episodes or post-event confusion, indicating good seizure control on current medication.
- Source normalized phrase: `he has been free of events for several months`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:5345:1` primary, `seizure_free`, `recent`, `llm_candidate`: he has been free of events for several months

### Row 5476 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: Sporadic epileptic spasms this year
- Assessment: The patient experiences sporadic epileptic spasms typically on waking from fragmented sleep. Clobazam is used as rescue approximately once monthly for short clusters. Environmental stressors and sleep disruption may contribute to seizure occurrence. Levetiracetam titration planned to improve control.
- Source normalized phrase: `sporadic epileptic spasms this year`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:5476:1` primary, `frequency_rate`, `current`, `llm_candidate`: The patient reports sporadic epileptic spasms this year, typically occurring on waking from fragmented sleep.
- `llm:5476:2` supporting, `cluster_frequency`, `current`, `llm_candidate`: Clobazam 5 mg at night as needed for clusters (patient-led use approximately once monthly)

### Row 5534 - `frequency_operands_gap`

- Gold label: `1 per multiple month`
- Gold reference: Rare brief seizure recently
- Assessment: Patient with generalised epilepsy reports a single brief seizure-like event two weeks ago, with no generalised tonic-clonic seizures since last year. Overall seizure control is stable and treatment unchanged.
- Source normalized phrase: `a very infrequent, short event a fortnight ago`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:5534:2` supporting, `seizure_free`, `historical`, `llm_candidate`: No myoclonic jerks were observed or reported in the mornings, and there have been no generalised tonic–clonic seizures since last year.
- `llm:5534:1` primary, `last_event_only`, `recent`, `llm_candidate`: She reports a very infrequent, short event a fortnight ago, described as a sudden pause with eyelid fluttering and brief unresponsiveness lasting under 10 seconds, with immediate recovery and no injury.

### Row 5551 - `additive_mixed_window_or_vague`

- Gold label: `multiple per day`
- Gold reference: Several episodes per day
- Assessment: The patient currently experiences daily focal impaired-awareness seizures occurring in clusters and occasional generalised tonic-clonic seizures approximately once weekly. Recent generalised seizures occurred two weeks ago after a missed dose. Clobazam is used intermittently for clusters. The clinical picture is of combined generalised and focal epilepsy with ongoing seizure burden despite treatment.
- Source normalized phrase: `several episodes per day, predominantly focal events, with occasional generalised breakthroughs approximately once weekly`
- Projection issues: `vague_count, frequency_rate_operands_unparsed, additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `llm:5551:2` primary, `frequency_rate`, `current`, `llm_candidate`: Frequency currently reported as several episodes per day, predominantly focal events, with occasional generalised breakthroughs (approximately once weekly).
- `llm:5551:1` primary, `unknown_frequency`, `current`, `llm_candidate`: Frequency currently reported as several episodes per day, predominantly focal events, with occasional generalised breakthroughs (approximately once weekly).
- `llm:5551:3` supporting, `unknown_frequency`, `current`, `llm_candidate`: They report improved sleep since starting levetiracetam but ongoing daytime clusters of focal impaired-awareness spells, described as “zoning out” with lip-smacking and right-hand fumbling, occurring in short flurries, several episodes per
- `llm:5551:4` supporting, `last_event_only`, `recent`, `llm_candidate`: There is a history of rare generalised tonic–clonic seizures, most recently two weeks ago, occurring in the early morning after a missed evening dose.

### Row 5791 - `additive_mixed_window_or_vague`

- Gold label: `1 per month`
- Gold reference: Nocturnal predominance of seizures
- Assessment: The patient reports two brief myoclonic jerks on awakening and one generalised tonic–clonic seizure over the past three months, indicating a low frequency of seizures currently. Events tend to cluster during sleep and early morning, with no prolonged post-ictal confusion or injury. Medication adherence is confirmed with partial control on valproate and levetiracetam.
- Source normalized phrase: `two brief myoclonic jerks on awakening and one generalised tonic–clonic event over the past three months`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_unparsed, additive_frequency_count_unparsed, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `llm:5791:3` primary, `frequency_rate`, `recent`, `llm_candidate`: Over the past three months they report two brief myoclonic jerks on awakening and one generalised tonic–clonic event at approximately 03:00 in early September, with full recovery by late morning and no injury.
- `llm:5791:2` primary, `frequency_rate`, `recent`, `llm_candidate`: Over the past three months they report two brief myoclonic jerks on awakening and one generalised tonic–clonic event at approximately 03:00 in early September, with full recovery by late morning and no injury.

### Row 5974 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: Seizures with missed ASM doses
- Assessment: Patient experiences seizures only in the context of missed levetiracetam doses, typically within 24–48 hours of a missed evening dose; no convulsive seizures reported in the past year, indicating good seizure control with adherence.
- Source normalized phrase: `Seizures with missed ASM doses, typically occurring within 24–48 hours of a missed levetiracetam dose`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:5974:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: No convulsive events reported
- `llm:5974:1` primary, `frequency_rate`, `current`, `llm_candidate`: Seizures with missed ASM doses, typically occurring within 24–48 hours of a missed levetiracetam dose

### Row 5996 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: Seizures with missed ASM doses
- Assessment: The patient experiences breakthrough seizures mainly associated with lapses in medication adherence, supported by pill diary and peer group observations. No consistent sleep deprivation or alcohol triggers noted. Safety precautions and medication adjustments are planned to improve control.
- Source normalized phrase: `Recent breakthrough events predominantly following lapses in prescribed antiseizure medication`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:5996:1` primary, `frequency_rate`, `recent`, `llm_candidate`: Recent breakthrough events predominantly following lapses in prescribed antiseizure medication, corroborated by entries in the patient’s pill diary and feedback from their peer support group facilitator.

### Row 6029 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: Seizures during intercurrent illness
- Assessment: Patient experiences ongoing focal aware and impaired-awareness seizures with a clustering pattern triggered by minor infections or feeling run down. Last generalized tonic-clonic seizure was 14 months ago. Clusters coincide with colds and disturbed sleep, with less frequent events between clusters.
- Source normalized phrase: `Ongoing focal seizures less frequent between clusters but not absent`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:6029:2` primary, `frequency_rate`, `recent`, `llm_candidate`: Between these periods, events are less frequent but not absent
- `llm:6029:3` supporting, `last_event_only`, `historical`, `llm_candidate`: Last generalised tonic-clonic seizure was 14 months ago after a night shift

### Row 6077 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: Seizures after alcohol intake
- Assessment: The patient experienced one breakthrough seizure on 12/09/2025 during a flight, linked to situational stress and sleep loss. There have been no seizures in the preceding eight months, indicating a generally low frequency outside travel-related triggers. Historical pattern shows seizures tend to occur with disrupted sleep and stress around travel rather than other triggers.
- Source normalized phrase: `one breakthrough seizure on 12/09/2025`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:6077:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no episodes in the preceding eight months
- `llm:6077:1` primary, `last_event_only`, `recent`, `llm_candidate`: one breakthrough episode on 12/09/2025 while on a late-evening flight from London to Lisbon (ï¿½row 18C)
- `llm:6077:2` supporting, `unknown_frequency`, `historical`, `llm_candidate`: a pattern over the past two years where seizures tend to occur in the context of disrupted sleep and heightened stress around travel rather than after alcohol ingestion (Ã©"stress-and-sleep-linked events")

### Row 6131 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: Photosensitive seizure episodes with flicker exposure
- Assessment: Patient has infrequent visually triggered generalised seizures with the last event in May 2025; no unprovoked seizures for over 12 months and no myoclonic jerks on waking for six months. Seizure control is stable on levetiracetam.
- Source normalized phrase: `infrequent generalised seizures provoked by patterned or flickering visual stimuli`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:6131:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: No myoclonic jerks on waking for the past six months
- `llm:6131:1` primary, `frequency_rate`, `current`, `llm_candidate`: She reports infrequent generalised seizures provoked by patterned or flickering visual stimuli (e.g. rapid screen refresh or strobe-like lighting), with the last event occurring in May 2025 at a concert; no unprovoked episodes for over 12 m
- `llm:6131:2` supporting, `last_event_only`, `recent`, `llm_candidate`: She reports infrequent generalised seizures provoked by patterned or flickering visual stimuli (e.g. rapid screen refresh or strobe-like lighting), with the last event occurring in May 2025 at a concert; no unprovoked episodes for over 12 m
- `llm:6131:3` supporting, `seizure_free`, `recent`, `llm_candidate`: She reports infrequent generalised seizures provoked by patterned or flickering visual stimuli (e.g. rapid screen refresh or strobe-like lighting), with the last event occurring in May 2025 at a concert; no unprovoked episodes for over 12 m

### Row 6180 - `frequency_operands_gap`

- Gold label: `multiple per week`
- Gold reference: Seizures after prolonged screen time
- Assessment: The patient has a recent clinically significant decline in seizure control with brief staring spells occurring several times weekly and two recent convulsive seizures in the past six weeks. The increase in frequency is associated with travel-related missed medication doses and prolonged device use. Ongoing monitoring and adherence interventions are planned.
- Source normalized phrase: `brief staring spells with loss of awareness on several occasions each week`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:6180:1` primary, `unknown_frequency`, `current`, `llm_candidate`: brief staring spells with loss of awareness on several occasions each week
- `llm:6180:3` supporting, `frequency_rate`, `recent`, `llm_candidate`: two recent collapses with limb-jerking in the past six weeks

### Row 6209 - `additive_mixed_window_or_vague`

- Gold label: `multiple per day`
- Gold reference: Startle-induced seizures
- Assessment: The patient experiences daily brief seizure-like events and approximately 2–3 longer seizures per month. These events are often preceded by abrupt noises and include brief loss of awareness with occasional right-hand fumbling. No consistent nocturnal pattern or sustained aura is reported. The patient is not currently driving and is under consideration for medication adjustment.
- Source normalized phrase: `daily brief events and 2–3 longer episodes per month`
- Projection issues: `additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `det:6209:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: 2–3 longer episodes per month
- `det:6209:2` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: daily brief events
- `llm:6209:1` primary, `frequency_rate`, `current`, `llm_candidate`: They described daily brief events
- `llm:6209:2` primary, `frequency_rate`, `current`, `llm_candidate`: approximately 2–3 longer episodes per month

### Row 6358 - `seizure_free_duration_gap`

- Gold label: `seizure free for 15 to 16 months`
- Gold reference: Caffeine-associated seizure events
- Assessment: Patient reports no seizures since June 2024 after lifestyle modifications including reduced caffeine and improved sleep. Historical seizures noted in 2017 and May 2024. Rare episodes previously linked to triggers are now absent.
- Source normalized phrase: `no events since June 2024 after moderating caffeine and improving sleep`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:6358:3` primary, `seizure_free`, `recent`, `llm_candidate`: Patient-reported rare episodes temporally linked with high-caffeine intake (e.g., strong coffee/energy drinks) and sleep restriction; no events since June 2024 after moderating caffeine and improving sleep.
- `llm:6358:1` rejected, `frequency_rate`, `historical`, `llm_candidate`: Two unprovoked convulsive episodes (2017, May 2024).
- `llm:6358:2` supporting, `unknown_frequency`, `recent`, `llm_candidate`: Patient-reported rare episodes temporally linked with high-caffeine intake (e.g., strong coffee/energy drinks) and sleep restriction; no events since June 2024 after moderating caffeine and improving sleep.

### Row 6501 - `cluster_axis_gap`

- Gold label: `unknown`
- Gold reference: Periods of clustering followed by quiescence
- Assessment: Patient experiences brief seizure clusters lasting 2–3 days during consecutive evening shifts, followed by several weeks without events. Clustering is associated with work-related stress and dehydration. No consistent auras or nocturnal events reported.
- Source normalized phrase: `brief episodes occurring over 2–3 days`
- Projection issues: `cluster_frequency_operands_unparsed, cluster_cadence_operands_incomplete`
- Route families: `cluster_axis_ambiguity`

Candidate evidence:

- `det:6501:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: No consistent auras reported
- `det:6501:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: No nocturnal events reported
- `llm:6501:1` primary, `cluster_frequency`, `current`, `llm_candidate`: Clusters are described as brief episodes occurring over 2–3 days, often during consecutive evening shifts near the grill station, followed by several weeks without events.
- `llm:6501:2` supporting, `unknown_frequency`, `current`, `llm_candidate`: Patient reports "Periods of clustering followed by quiescence" in the context of work-related stress and dehydration in a commercial kitchen line setting.

### Row 6571 - `seizure_free_duration_gap`

- Gold label: `unknown`
- Gold reference: Typical seizure event duration twenty seconds
- Assessment: Patient has had no further seizure events reported since mid-June 2025 following improved medication supply coordination. Historical clusters occurred during periods of missed or delayed doses but no recent events have been noted.
- Source normalized phrase: `no further events reported`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:6571:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: no further events reported
- `llm:6571:1` supporting, `cluster_frequency`, `historical`, `llm_candidate`: occurring in clusters during periods of missed or delayed doses in the past
- `llm:6571:2` supporting, `last_event_only`, `historical`, `llm_candidate`: Last cluster was in early June 2025 during a documented delay in dispensing (ï¿½ two days without evening tablets)

### Row 6889 - `additive_mixed_window_or_vague`

- Gold label: `multiple per week`
- Gold reference: Interictal discharges on EEG; no ictal correlate
- Assessment: The patient experiences multiple seizure types including brief morning myoclonic jerks several times per week, three generalised tonic–clonic seizures in the past six months, and focal seizures occurring roughly once every 2–3 weeks. These frequencies are additive to represent the overall current seizure burden.
- Source normalized phrase: `brief morning myoclonic jerks several times per week; three generalised tonic–clonic seizures in the past six months; once every 2–3 weeks`
- Projection issues: `vague_count, additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `det:6889:5` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: brief morning myoclonic jerks several times per week
- `llm:6889:3` primary, `frequency_rate`, `current`, `llm_candidate`: occurring roughly once every 2–3 weeks
- `det:6889:3` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: three generalised tonic–clonic seizures in the past six months

### Row 6952 - `frequency_operands_gap`

- Gold label: `2 per week`
- Gold reference: Home video suggests seizure activity
- Assessment: The patient currently experiences brief generalized seizures approximately twice weekly, consistent with family-recorded events over the last eight weeks. Medication adherence has improved with supportive reminders, and the clinical pattern is stable without recent rescue medication use. No injuries or adverse effects reported.
- Source normalized phrase: `approximately twice weekly`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:6952:1` primary, `frequency_rate`, `recent`, `llm_candidate`: clips recorded on the family phone over the last eight weeks indicate brief generalised episodes occurring approximately twice weekly

### Row 7126 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: Peri-ovulatory increase in seizure events
- Assessment: Patient experiences a clear pattern of increased seizure events mid-cycle approximately 10–14 days after menses onset, with infrequent events outside this window. Clobazam is used as needed for clusters up to 10 days per month, which is contextual but not additive to the primary frequency assessment.
- Source normalized phrase: `recurring mid-cycle surge in episodes approximately 10–14 days after menses onset`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:7126:1` supporting, `cluster_frequency`, `recent`, `llm_candidate`: Clobazam 5 mg at night as needed for clusters (maximum 10 days per month)
- `llm:7126:2` primary, `frequency_rate`, `recent`, `llm_candidate`: Over the past four months she has noticed a recurring mid-cycle surge in episodes, with a clear pattern of increased events approximately 10–14 days after menses onset.
- `llm:7126:3` supporting, `unknown_frequency`, `recent`, `llm_candidate`: Outside this window, events are infrequent.

### Row 7168 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: Late luteal phase seizure exacerbations noted
- Assessment: The patient experiences intermittent morning myoclonic jerks daily, especially after poor sleep, representing the current seizure burden. There have been two brief generalized tonic–clonic seizures over the past year occurring shortly before menstruation, which are noted as historical context. The pattern of premenstrual clustering is recognized but not additive to the current day-to-day frequency assessment. Medication adherence is good, and management plans include monitoring and potential perimenstrual dose adjustments.
- Source normalized phrase: `intermittent morning myoclonic jerks day-to-day`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:7168:1` supporting, `frequency_rate`, `recent`, `llm_candidate`: Over the past year there have been two brief generalised tonic–clonic seizures, both occurring shortly before menstruation, with preserved recovery and no injuries.
- `llm:7168:2` primary, `frequency_rate`, `current`, `llm_candidate`: Day-to-day, there are intermittent morning myoclonic jerks, especially after poor sleep.

### Row 7409 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: Tolerability-limited dosing with ongoing seizure events
- Assessment: Patient experiences focal aware seizures most weeks with occasional progression to focal impaired awareness despite aura recognition strategies and lamotrigine at dose ceiling. Clobazam is used PRN for clusters 2-3 times per month. No convulsions for over a year, indicating no recent generalized tonic-clonic seizures.
- Source normalized phrase: `focal aware seizures most weeks, occasionally progressing to focal impaired awareness`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:7409:2` primary, `frequency_rate`, `recent`, `llm_candidate`: She reports that over the past six months she experiences focal aware seizures most weeks, occasionally progressing to focal impaired awareness
- `llm:7409:3` supporting, `frequency_rate`, `current`, `llm_candidate`: Clobazam 5–10 mg PRN for clusters (no more than 2–3 times per month)
- `llm:7409:4` supporting, `seizure_free`, `historical`, `llm_candidate`: No convulsions for over a year

### Row 7738 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No seizure recurrence noted
- Assessment: The patient reports no seizures since the last notification period, indicating seizure freedom. No further attacks were reported at the last appointment six months ago, supporting ongoing seizure control. The candidate indicating unknown frequency was rejected due to redundancy with seizure-free facts.
- Source normalized phrase: `no events since last notification period`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:7738:1` primary, `seizure_free`, `recent`, `llm_candidate`: patient reports no events since last notification period
- `det:7738:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no further attacks reported
- `llm:7738:2` rejected, `unknown_frequency`, `recent`, `llm_candidate`: Since the last appointment six months ago, there have been no further attacks reported

### Row 7818 - `seizure_free_duration_gap`

- Gold label: `seizure free for 2 years`
- Gold reference: Patient remains without seizures
- Assessment: Patient reports no seizures since levetiracetam titration in August 2023, indicating sustained seizure freedom with good medication adherence and no adverse effects.
- Source normalized phrase: `no further events suggestive of seizures`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:7818:1` primary, `seizure_free`, `recent`, `llm_candidate`: He reports that since titration to levetiracetam 1000 mg twice daily in August 2023, there have been no further events suggestive of seizures.

### Row 7834 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No further seizure episodes
- Assessment: Patient reports no further seizure episodes with improved day-to-day functioning, better sleep, reduced anxiety, and ongoing psychological support. Medication is well tolerated with no adverse effects. Family notes improved confidence and fewer avoidance behaviors. Continued monitoring and support planned.
- Source normalized phrase: `No further seizure episodes.`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:7834:1` primary, `seizure_free`, `recent`, `llm_candidate`: No further seizure episodes.

### Row 7859 - `seizure_free_duration_gap`

- Gold label: `unknown`
- Gold reference: No further seizure episodes
- Assessment: The patient reports a recent period with essentially no breakthrough seizures and no events noted for several weeks, indicating a seizure-free state currently. Events have been sparse, with only prodromal sensations and no progression to seizures. Continued monitoring and adherence to current medication and workplace safety measures are advised.
- Source normalized phrase: `recent period with essentially no breakthrough events`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:7859:1` primary, `seizure_free`, `recent`, `llm_candidate`: Continue brivaracetam 50 mg twice daily for now, given the recent period with essentially no breakthrough events.
- `llm:7859:2` supporting, `last_event_only`, `recent`, `llm_candidate`: Since our last contact in May, he reports that events have been sparse; specifically, he has not noted any further turns for several weeks, including during recent late shifts.
- `llm:7859:3` supporting, `unknown_frequency`, `recent`, `llm_candidate`: Since our last contact in May, he reports that events have been sparse; specifically, he has not noted any further turns for several weeks, including during recent late shifts.

### Row 7872 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Complete control of seizures
- Assessment: The patient reports complete seizure control since last review with no breakthrough events, no emergency interventions, and stable medication adherence. Neurological examination and investigations are unremarkable, supporting seizure freedom in the current period.
- Source normalized phrase: `complete control of seizures since his last review`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:7872:1` primary, `seizure_free`, `recent`, `llm_candidate`: complete control of seizures since his last review

### Row 7911 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Seizures under sustained control
- Assessment: Patient reports no auras, warnings, blackouts, or witnessed seizures since last contact, indicating sustained seizure control and stable clinical status.
- Source normalized phrase: `Seizures under sustained control`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:7911:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: No auras, warnings, blackouts, or witnessed episodes since
- `llm:7911:1` primary, `seizure_free`, `current`, `llm_candidate`: Seizures under sustained control.

### Row 7961 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple year`
- Gold reference: Well-controlled epilepsy
- Assessment: The patient reports a sustained period of seizure stability with no impairment of daily activities, with the last confirmed seizure over two years ago and no recent events suggestive of seizures. Historical childhood febrile seizures and prior intermittent blackouts are noted but not current. No red flags or breakthrough events identified. Daily seizures candidate rejected as inconsistent with current clinical picture.
- Source normalized phrase: `a sustained period of seizure stability with no impairment of daily activities`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:7961:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no episodes since
- `det:7961:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no recent events suggestive of seizures
- `det:7961:3` rejected, `frequency_rate`, `unclear`, `deterministic_candidate`: daily Seizures
- `llm:7961:1` primary, `seizure_free`, `current`, `llm_candidate`: she describes a sustained period of seizure stability with no impairment of daily activities
- `llm:7961:2` supporting, `last_event_only`, `historical`, `llm_candidate`: the last confirmed episode occurring over two years ago

### Row 8006 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Stable seizure control maintained
- Assessment: The patient has maintained seizure freedom for six months with no breakthrough events, corroborated by patient report and colleague observations. Ongoing medication and workplace precautions support continued stability.
- Source normalized phrase: `No seizures or breakthrough events over the past six months`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:8006:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: Seizures remain settled without recent breakthrough events
- `llm:8006:2` primary, `seizure_free`, `recent`, `llm_candidate`: The patient reports no blackouts or focal impaired-awareness episodes over the past six months
- `llm:8006:3` supporting, `seizure_free`, `recent`, `llm_candidate`: Colleagues in the stage lighting team have not witnessed any events during rehearsals or live shows

### Row 8089 - `seizure_free_duration_gap`

- Gold label: `seizure free for 16 month`
- Gold reference: Sustained remission since 29-May-2023
- Assessment: The patient has had sustained seizure remission since 29-May-2023 with no breakthrough events, indicating excellent seizure control on current medication. Previous frequency and medication history provide context but do not alter the current seizure-free status.
- Source normalized phrase: `Sustained remission since 29-May-2023`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8089:1` primary, `seizure_free`, `recent`, `llm_candidate`: Sustained remission since 29-May-2023.
- `det:8089:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: sustained remission since 29-May-2023
- `det:8089:3` rejected, `frequency_rate`, `unclear`, `deterministic_candidate`: every 6–12 months

### Row 8144 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Ongoing seizure-free interval
- Assessment: The patient reports a sustained spell without clinical seizures, indicating good control of focal epilepsy on lamotrigine. No nocturnal events were reported. Occasional brief déjà vu sensations occur but are less frequent and do not impair function.
- Source normalized phrase: `a sustained spell without clinical events`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:8144:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: No nocturnal events reported
- `llm:8144:1` primary, `seizure_free`, `recent`, `llm_candidate`: she describes a sustained spell without clinical events
- `llm:8144:2` supporting, `unknown_frequency`, `recent`, `llm_candidate`: She notes occasional brief déjà vu sensations without progression, typically lasting seconds and not followed by confusion; these have become less frequent over the past three months and do not impair function.

### Row 8145 - `seizure_free_duration_gap`

- Gold label: `seizure free for 6 month`
- Gold reference: Ongoing seizure-free interval
- Assessment: The patient reports no seizures since the late third trimester and none at all since delivery, indicating a sustained seizure-free period despite fragmented sleep.
- Source normalized phrase: `a continued period without events`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8145:1` supporting, `seizure_free`, `recent`, `llm_candidate`: They report no seizures since the late third trimester, and none at all since delivery.
- `llm:8145:2` primary, `seizure_free`, `current`, `llm_candidate`: She describes the current phase as a continued period without events, despite sleep fragmentation.

### Row 8160 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Ongoing seizure-free interval
- Assessment: The patient is currently in a stable spell without witnessed convulsions, consistent with seizure freedom. Occasional brief moments of lost thread without clear seizures are reported but are uncertain in nature and not considered definite seizures. Last witnessed seizure was prior to June 2025.
- Source normalized phrase: `stable spell without witnessed convulsions`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:8160:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: steady run without clear seizures at present
- `det:8160:2` rejected, `frequency_rate`, `unclear`, `deterministic_candidate`: once every few weeks
- `llm:8160:1` rejected, `last_event_only`, `recent`, `llm_candidate`: I last saw him on 11th June 2025
- `llm:8160:2` primary, `seizure_free`, `current`, `llm_candidate`: Since that time he reports no witnessed convulsions and has continued with a stable spell without events that his partner has noticed.
- `llm:8160:3` supporting, `unknown_frequency`, `current`, `llm_candidate`: He describes occasional brief moments of lost thread during conversation, occurring perhaps once every few weeks

### Row 8180 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No seizures reported since last evaluation
- Assessment: The patient reports no seizures or seizure-like events since the last review in April, indicating stable seizure freedom. Medication adherence is good, and no changes to antiepileptic therapy were made. The patient maintains usual activity and sleep patterns, with no new neurological symptoms.
- Source normalized phrase: `he has not described any further events suggestive of seizures`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8180:1` primary, `seizure_free`, `recent`, `llm_candidate`: Since our last review in April, he has not described any further events suggestive of seizures.

### Row 8188 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No seizures reported since last evaluation
- Assessment: Patient reports no seizures since last clinic assessment; continues current antiseizure therapy with stable condition.
- Source normalized phrase: `no episodes since`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:8188:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: no episodes since
- `llm:8188:1` supporting, `last_event_only`, `recent`, `llm_candidate`: From a seizure perspective, he reports that there have been no episodes since his last clinic assessment.

### Row 8203 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No seizures reported since last evaluation
- Assessment: The patient reports no witnessed typical seizure events since the last review, with no daytime or nocturnal episodes noted. He continues to keep a diary with no recorded events. Historical medication intolerances are noted but do not affect current seizure freedom status.
- Source normalized phrase: `He described remaining free of his usual attacks over this interval`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8203:1` primary, `seizure_free`, `recent`, `llm_candidate`: He described remaining free of his usual attacks over this interval
- `det:8203:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no daytime episodes reported

### Row 8224 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No seizures documented during follow-up
- Assessment: Patient reports no witnessed convulsive or absence seizures since last appointment three months ago; no interval events recorded. Seizure control is stable with only brief, non-specific moments of inattention not resembling prior seizures. Medication adherence and lifestyle stable. No new neurological symptoms.
- Source normalized phrase: `no witnessed convulsive events or absence episodes`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:8224:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no interval events recorded
- `llm:8224:1` primary, `seizure_free`, `recent`, `llm_candidate`: no witnessed convulsive events or absence episodes

### Row 8235 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No seizures documented during follow-up
- Assessment: The patient previously experienced seizures up to twice daily, particularly around menstruation, but currently has sustained seizure freedom with no events recorded or witnessed over the current follow-up period.
- Source normalized phrase: `no events recorded or witnessed over the current follow-up period`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8235:2` primary, `seizure_free`, `current`, `llm_candidate`: Since adhering to the current regimen and cycle-tracking strategies, there have been no events recorded or witnessed over the current follow-up period.
- `llm:8235:1` supporting, `frequency_rate`, `historical`, `llm_candidate`: Prior to improvement, she described events occurring up to twice daily at worst, particularly around menstruation.

### Row 8264 - `seizure_free_duration_gap`

- Gold label: `seizure free for 4 month`
- Gold reference: Seizure-free throughout monitoring period
- Assessment: The patient has maintained seizure freedom during the monitored period with no recorded focal or generalized seizures, consistent medication adherence, and stable clinical status.
- Source normalized phrase: `no recorded events, either focal or generalised, during the period monitored`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8264:1` primary, `seizure_free`, `recent`, `llm_candidate`: her seizure diary indicates that there have been no recorded events, either focal or generalised, during the period monitored.

### Row 8265 - `seizure_free_duration_gap`

- Gold label: `seizure free for 6 month`
- Gold reference: Seizure-free throughout monitoring period
- Assessment: The patient has remained seizure-free over the current follow-up interval with no absence episodes reported. The last generalised tonic–clonic seizure was in January 2024 during a period of missed doses and illness. Medication adherence has been confirmed since March 2024.
- Source normalized phrase: `she has remained without seizures over this interval`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:8265:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no absence episodes reported
- `llm:8265:1` primary, `seizure_free`, `recent`, `llm_candidate`: she has remained without seizures over this interval
- `llm:8265:2` supporting, `last_event_only`, `historical`, `llm_candidate`: her last generalised tonic–clonic seizure was in January 2024

### Row 8400 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Durable seizure control
- Assessment: The patient reports durable seizure control over several months with no convulsive seizures, only occasional brief warning episodes that do not progress. Current management is stable with no medication changes and adherence confirmed. Aura recognition and diary keeping continue as supportive strategies.
- Source normalized phrase: `durable seizure control over the past several months, with no convulsive events`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8400:1` primary, `seizure_free`, `recent`, `llm_candidate`: durable seizure control over the past several months, with no convulsive events

### Row 8474 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No events suggestive of seizures
- Assessment: Patient reports no events suggestive of seizures during the interval, with no witnessed episodes or post-event confusion. Anxiety and mood symptoms are present but do not indicate seizure activity. The phrase 'on two to three nights per week' refers to early morning awakenings related to sleep, not seizures, and is thus supporting context only.
- Source normalized phrase: `No events suggestive of seizures`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:8474:1` supporting, `cluster_frequency`, `unclear`, `deterministic_candidate`: on two to three nights per week
- `det:8474:2` primary, `seizure_free`, `unclear`, `deterministic_candidate`: No events suggestive of seizures

### Row 8512 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Interval history negative for seizures
- Assessment: The patient reports no seizures over the interval history period, supported by smartwatch data and personal diary, indicating stable seizure freedom.
- Source normalized phrase: `Interval history negative for seizures`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:8512:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: Interval history negative for seizures

### Row 8577 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No seizure-like episodes
- Assessment: The patient has been seizure-free with no reported events or auras since 09 March 2024, supported by consistent seizure diary app records and clinical stability on current medication.
- Source normalized phrase: `no entries for events or auras since 09 March 2024`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8577:1` primary, `seizure_free`, `recent`, `llm_candidate`: app export reviewed today shows no entries for events or auras since 09 March 2024.

### Row 8581 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No seizure-like episodes
- Assessment: The patient has maintained an absence of clinically concerning seizure episodes over the recent period, with no recorded spells suggestive of seizure activity and the last atypical sensation noted in June 2025 which has not recurred. Medication adherence and monitoring continue as planned.
- Source normalized phrase: `absence of clinically concerning episodes over this period`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:8581:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no recorded spells suggestive of seizure activity
- `llm:8581:1` primary, `seizure_free`, `recent`, `llm_candidate`: Overall pattern indicates an absence of clinically concerning episodes over this period.
- `llm:8581:2` supporting, `last_event_only`, `historical`, `llm_candidate`: The last app notation of an atypical sensation was 12th June 2025, described as “brief lightheadedness without other features,” which has not recurred.

### Row 8674 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Seizure-free on current antiseizure regimen
- Assessment: Patient has been free of episodes for several months with no antiseizure medication; prior event frequency was every other week but events are now considered non-epileptic sleep-related phenomena.
- Source normalized phrase: `episode-free on her current routine`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:8674:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: episode-free on her current routine
- `llm:8674:1` rejected, `frequency_rate`, `historical`, `llm_candidate`: Prior to this change, the reported event frequency was qod (every other week).
- `llm:8674:2` supporting, `seizure_free`, `recent`, `llm_candidate`: Over the last several months she describes a complete absence of further episodes

### Row 8724 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Seizure-free on last ASM
- Assessment: The patient has been seizure-free since titration to the current levetiracetam dose three months ago, with no breakthrough events or suggestive episodes. Prior brief, rare spells of transient unresponsiveness after consecutive night shifts occurred before dose stabilization and have not recurred. Sleep disruption due to rotating shifts is noted but managed with sleep hygiene measures. Continue current medication and monitoring plan.
- Source normalized phrase: `No episodes suggestive of seizures since titration to current antiepileptic dose`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8724:1` supporting, `seizure_free`, `recent`, `llm_candidate`: No breakthrough events reported since commencing this dose three months ago.
- `llm:8724:2` primary, `seizure_free`, `recent`, `llm_candidate`: Since titration to her current antiepileptic dose, she describes no episodes suggestive of seizures, including no nocturnal events, auras, or witnessed spells.
- `llm:8724:3` supporting, `last_event_only`, `historical`, `llm_candidate`: Prior to dose stabilisation she had brief, rare spells of transient unresponsiveness after consecutive night shifts; these have not recurred.

### Row 8730 - `seizure_free_duration_gap`

- Gold label: `seizure free for 6 month`
- Gold reference: Seizure-free on last ASM
- Assessment: The patient reports no further seizures or witnessed attacks since the last review, corroborated by diary and clinical examination, indicating seizure freedom at this time.
- Source normalized phrase: `no further episodes and there have been no witnessed attacks`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:8730:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no events since
- `llm:8730:1` primary, `seizure_free`, `recent`, `llm_candidate`: Since that review, he reports no further episodes and there have been no witnessed attacks.
- `llm:8730:2` supporting, `seizure_free`, `recent`, `llm_candidate`: In short, there have been no seizures in this interval.

### Row 8794 - `seizure_free_duration_gap`

- Gold label: `seizure free for 6 month`
- Gold reference: Seizure burden 0% on device metrics
- Assessment: The patient has had no detected seizures over the last 6 months as confirmed by device monitoring and diary entries, indicating excellent seizure control and seizure freedom during this period.
- Source normalized phrase: `no detected seizures over the last 6 months`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:8794:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: recorded seizure rate at zero on the monitoring platform during this period
- `llm:8794:1` primary, `seizure_free`, `recent`, `llm_candidate`: Over the last 6 months, the device reports no detected events and her synced diary entries corroborate this.

### Row 8802 - `seizure_free_duration_gap`

- Gold label: `seizure free for 12 month`
- Gold reference: Seizure burden 0% on device metrics
- Assessment: Patient reports no seizures since last review, confirmed by wearable diary data over 12 months showing no detected events. Neurological exam and medication stable with no new risk factors. Continued seizure freedom supported by clinical and device data.
- Source normalized phrase: `no episodes suggestive of seizures since last review with no witnessed events, nocturnal disturbances, or post-event confusion`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8802:1` primary, `seizure_free`, `recent`, `llm_candidate`: He reports no episodes suggestive of seizures since his last review and confirms there have been no witnessed events, nocturnal disturbances, or post‑event confusion.

### Row 8805 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Seizure burden 0% on device metrics
- Assessment: The patient has been seizure-free from convulsive seizures for the past six months as confirmed by device analytics and personal logs. The last brief episode of confusion without collapse was in late March and is considered historical. Current anti-seizure medications are continued with stable clinical status.
- Source normalized phrase: `no convulsive seizures detected over the past six months`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8805:1` primary, `seizure_free`, `recent`, `llm_candidate`: Over the past six months, the device analytics have not detected any convulsive activity, and his personal event log corroborates this, with no recorded events requiring rescue measures.
- `llm:8805:2` supporting, `last_event_only`, `historical`, `llm_candidate`: He last recalls a brief episode of confusion without collapse in late March, without injury.

### Row 8808 - `seizure_free_duration_gap`

- Gold label: `seizure free for 10 month`
- Gold reference: Seizure burden 0% on device metrics
- Assessment: Patient has been seizure-free since levetiracetam dose titration in November 2024, with corroborating wearable device data showing zero events logged over the past 10 months. Classification remains unresolved; safety advice and monitoring continue.
- Source normalized phrase: `no definite seizures and no witnessed collapses`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8808:1` primary, `seizure_free`, `recent`, `llm_candidate`: Since titrating levetiracetam to the present dose in November 2024, he reports no definite seizures and no witnessed collapses.
- `llm:8808:2` supporting, `seizure_free`, `recent`, `llm_candidate`: His wearable device and home seizure-detection app record no abnormal episodes; the dashboard indicates event detection at baseline only, i.e. device-tracked seizure activity remains effectively absent (                                     

### Row 8820 - `seizure_free_duration_gap`

- Gold label: `seizure free for 7 month`
- Gold reference: Wearable/device logs show no seizures since 29-12-2023
- Assessment: The patient has had no seizures since 29-12-2023, indicating sustained remission corroborated by device logs and clinical history. Historical clustering is noted but is now resolved with lifestyle and dietetic optimization.
- Source normalized phrase: `no seizures since 29-12-2023`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8820:2` primary, `seizure_free`, `recent`, `llm_candidate`: no seizures since 29-12-2023
- `llm:8820:1` supporting, `cluster_frequency`, `historical`, `llm_candidate`: a day of clustering, with multiple events

### Row 8835 - `seizure_free_duration_gap`

- Gold label: `seizure free for 10 month`
- Gold reference: Wearable/device logs show no seizures since 12 June 2020
- Assessment: The patient has been seizure-free since 12 June 2020 as confirmed by wearable/device logs and clinical history, indicating sustained seizure freedom and clinical improvement.
- Source normalized phrase: `no seizures since 12 June 2020`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8835:1` primary, `seizure_free`, `recent`, `llm_candidate`: Wearable/device logs show no seizures since 12 June 2020.

### Row 8854 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Seizure cessation following initiation of last ASM
- Assessment: The patient has achieved seizure cessation following initiation of levetiracetam, with no seizures recorded since starting treatment. The last seizure event predates the start of the current ASM.
- Source normalized phrase: `Seizure cessation following initiation of last ASM`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8854:1` primary, `seizure_free`, `recent`, `llm_candidate`: Seizure cessation following initiation of last ASM.
- `llm:8854:2` supporting, `last_event_only`, `historical`, `llm_candidate`: Entries confirm Seizure cessation following initiation of last ASM, with the last marked event predating the start of levetiracetam.

### Row 8893 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Seizure-free after dose escalation of ASM
- Assessment: Patient with longstanding focal epilepsy is currently seizure-free following recent dose escalation of anti-seizure medication. No dissociative or nocturnal events reported. Well tolerated treatment with no breakthrough seizures. Attending for pre-conception counselling.
- Source normalized phrase: `Seizure-free after dose escalation of ASM`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:8893:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no dissociative or nocturnal events reported
- `llm:8893:1` primary, `seizure_free`, `current`, `llm_candidate`: he is now Seizure-free after dose escalation of ASM

### Row 8922 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Seizure-free after dose escalation of ASM
- Assessment: The patient reports being seizure-free following antiseizure medication dose optimization, with no seizures, absences, or myoclonic jerks reported by family or school staff.
- Source normalized phrase: `being without further seizures since the most recent dose increase`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8922:1` primary, `seizure_free`, `current`, `llm_candidate`: She describes being without further seizures since the most recent dose increase, with no interim absences or myoclonic jerks reported by family or school staff.

### Row 8924 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Seizure-free after dose escalation of ASM
- Assessment: The patient has been seizure-free since the increase in antiseizure medication dose in May, with no recorded events corroborated by diary and partner observations. Historical brief nocturnal episodes prior to dose increase are noted but not current.
- Source normalized phrase: `no recorded events since dose titration`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8924:1` primary, `seizure_free`, `recent`, `llm_candidate`: since titration to the current dose she has had no recorded events
- `llm:8924:2` supporting, `frequency_rate`, `historical`, `llm_candidate`: brief nocturnal episodes with confusion and lip-smacking prior to the dose increase in May

### Row 8938 - `seizure_free_duration_gap`

- Gold label: `seizure free for 10 month`
- Gold reference: Seizure-free off ASMs since 25 Jun 2015
- Assessment: The patient has been seizure-free off antiseizure medications since 25 June 2015 with no reported events or red flags. No routine follow-up is planned, but patient advised to contact clinic if seizures recur or circumstances change.
- Source normalized phrase: `Seizure-free off ASMs since 25 Jun 2015`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8938:1` primary, `seizure_free`, `historical`, `llm_candidate`: Seizure-free off ASMs since 25 Jun 2015
- `det:8938:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no events. Specifically, they confirm they have been Seizure-free off ASMs since

### Row 8949 - `seizure_free_duration_gap`

- Gold label: `seizure free for 6 month`
- Gold reference: Drug-free remission since 20-Jun-2021
- Assessment: The patient has been in sustained drug-free remission since June 20, 2021, with no seizures reported since medication discontinuation. This reflects a stable seizure-free state off antiseizure medication.
- Source normalized phrase: `Drug-free remission since 20-Jun-2021 following a gradual discontinuation of levetiracetam earlier in 2021 due to persistent GI upset and mood symptoms`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:8949:1` primary, `seizure_free`, `recent`, `llm_candidate`: Drug-free remission since 20-Jun-2021 following a gradual discontinuation of levetiracetam earlier in 2021 due to persistent GI upset and mood symptoms.

### Row 8969 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Sustained postoperative seizure freedom
- Assessment: The patient has sustained postoperative seizure freedom with no current epileptic seizures. Historical weekly clusters of 6 events are resolved. No antiepileptic therapy is required, and the patient is stable with no evidence of epilepsy.
- Source normalized phrase: `Sustained postoperative seizure freedom`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:8969:1` supporting, `cluster_frequency`, `unclear`, `deterministic_candidate`: weekly clusters, usually 6 events
- `det:8969:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: seizure freedom and absence of epilepsy. - Routine follow-up in 6–12 months
- `det:8969:3` primary, `seizure_free`, `unclear`, `deterministic_candidate`: Sustained postoperative seizure freedom
- `det:8969:4` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: sustained postoperative seizure freedom
- `llm:8969:1` supporting, `cluster_frequency`, `historical`, `llm_candidate`: weekly clusters, usually 6 events within ~2 h

### Row 9063 - `seizure_free_duration_gap`

- Gold label: `seizure free for 8 month`
- Gold reference: No focal clonic since 19-Mar-2017
- Assessment: Patient reports sustained stability with no focal clonic seizures since 19-Mar-2017, no convulsive activity, no injuries, and no post-event confusion. Medication adherence is good with no recent changes. Remote monitoring continues with seizure diary and telephone reviews planned.
- Source normalized phrase: `No focal clonic seizures since 19-Mar-2017`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:9063:1` primary, `seizure_free`, `recent`, `llm_candidate`: No focal clonic since 19-Mar-2017.

### Row 9103 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: No nocturnal seizures reported
- Assessment: The patient has infrequent generalised tonic–clonic seizures over the past year, with the last seizure approximately four months ago precipitated by missed medication and sleep deprivation. Typical absence episodes are present but frequency is unknown. No nocturnal seizures reported recently. Overall seizure control is stable with good adherence and no recent injuries.
- Source normalized phrase: `infrequent generalised tonic–clonic seizures over the past year`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:9103:1` primary, `frequency_rate`, `recent`, `llm_candidate`: The generalised tonic–clonic seizures have been infrequent over the past year
- `llm:9103:2` supporting, `last_event_only`, `recent`, `llm_candidate`: He reports that the last generalised tonic–clonic seizure occurred approximately four months ago
- `llm:9103:3` rejected, `frequency_rate`, `historical`, `llm_candidate`: Prior to that, episodes were spaced several months apart
- `llm:9103:4` supporting, `unknown_frequency`, `current`, `llm_candidate`: He has generalised epilepsy with typical absence episodes
- `llm:9103:5` supporting, `unknown_frequency`, `recent`, `llm_candidate`: he has not had episodes on waking. He denies any spells overnight; his partner also confirms that she has not observed any nocturnal events or unusual movements during the night

### Row 9163 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Seizure-free by patient report
- Assessment: Patient reports being seizure-free over the recent period with no nocturnal events or injuries, corroborated by partner's observations and no missed doses; medication adherence improved with consistent supply.
- Source normalized phrase: `he is Seizure-free by patient report`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:9163:1` primary, `seizure_free`, `recent`, `llm_candidate`: he is Seizure-free by patient report

### Row 9190 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: Seizure-free by patient report
- Assessment: The patient reports no clinical seizures or auras since early April 2025, with no witnessed focal impaired-awareness seizures or convulsions since late February 2025, corroborated by colleague observations and self-kept diary. Neurological examination is unremarkable, and current antiepileptic treatment is stable. Safety measures and monitoring continue with follow-up planned in six months.
- Source normalized phrase: `no witnessed focal impaired-awareness events or convulsions since late February 2025`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:9190:2` supporting, `seizure_free`, `recent`, `llm_candidate`: he reports no auras since early April 2025
- `llm:9190:4` supporting, `seizure_free`, `recent`, `llm_candidate`: There have been no episodes of unresponsiveness or automatisms reported by supervisors since February
- `llm:9190:1` primary, `seizure_free`, `recent`, `llm_candidate`: there have been no witnessed focal impaired-awareness events or convulsions since late February 2025
- `llm:9190:3` supporting, `seizure_free`, `recent`, `llm_candidate`: effectively no clinical seizures reported in the intervening months

### Row 9215 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No witnessed or reported seizures
- Assessment: The patient reports no recognized seizures since early summer, supported by a simple calendar record and no events noted by carers or bystanders. This indicates a current seizure-free state.
- Source normalized phrase: `no recognized seizures since early summer`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:9215:1` primary, `seizure_free`, `recent`, `llm_candidate`: He keeps a simple calendar record and says there have been no episodes brought to attention by carers or bystanders, nor any events he has recognised as seizures, since early summer.

### Row 9238 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No definite seizures
- Assessment: The patient reports no definite seizures since last assessment, with good medication adherence and lifestyle measures. Continued observation and current antiseizure medication maintained.
- Source normalized phrase: `No definite seizures during this period`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:9238:1` primary, `seizure_free`, `recent`, `llm_candidate`: No definite seizures during this period.

### Row 9250 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: No definite seizures
- Assessment: The patient reports good overall control with no definite recent seizures. Brief clusters of warning symptoms occur only with marked sleep deprivation and do not progress to seizures. Antiepileptic regimen remains unchanged with stable tolerability.
- Source normalized phrase: `no clear-cut events to suggest recent seizures`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:9250:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: no clear-cut events to suggest recent seizures

### Row 9259 - `seizure_free_duration_gap`

- Gold label: `seizure free for 1 year`
- Gold reference: No definite seizures
- Assessment: The patient currently reports a clear period without events consistent with guidance, with no epilepsy diagnosis and no antiseizure medication. Historical episodes were non-epileptic and the patient has had no definite seizures over the past year.
- Source normalized phrase: `clear period without events`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:9259:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: without events for an extended period
- `det:9259:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no events of concern
- `llm:9259:1` primary, `seizure_free`, `current`, `llm_candidate`: the patient currently reports a clear period without events consistent with guidance
- `llm:9259:2` supporting, `unknown_frequency`, `recent`, `llm_candidate`: Over the past year there have been essentially no events of concern; they describe an absence of definite seizures.

### Row 9299 - `frequency_operands_gap`

- Gold label: `5 per week`
- Gold reference: five focal automatisms per week
- Assessment: The patient reports an average of five focal automatisms per week over the past two months, often clustering in the evening. No recent injuries or emergency attendances. Safety advice and remote monitoring plan in place.
- Source normalized phrase: `five focal automatisms per week`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:9299:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: records five focal automatisms per week
- `llm:9299:1` primary, `frequency_rate`, `current`, `llm_candidate`: They have kept a diary over the past two months, which records five focal automatisms per week on average, often clustering in the evening.

### Row 9588 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple month`
- Gold reference: focal epileptic spasms freedom achieved
- Assessment: The patient has achieved freedom from focal epileptic spasms since February 2025, with no recent seizures reported. Current medication adherence is good, and no breakthrough events have occurred. Continued monitoring and follow-up are planned.
- Source normalized phrase: `focal epileptic spasms freedom achieved, with the last brief event described in February 2025`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:9588:1` primary, `seizure_free`, `recent`, `llm_candidate`: Since their last review, focal epileptic spasms freedom achieved, with the last brief event described in February 2025.

### Row 9815 - `frequency_operands_gap`

- Gold label: `multiple per day`
- Gold reference: Electrographic focal clonic frequent on EEG (~9/h)
- Assessment: The patient has combined generalised and focal epilepsy with rare generalised tonic–clonic seizures; last generalised seizure was three months ago. Frequent focal clonic jerks occur but are not quantified as frequency rate here. No injuries reported; patient uses structured medication reminders and has stable seizure control.
- Source normalized phrase: `generalised tonic–clonic seizures occurring rarely`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:9815:2` primary, `frequency_rate`, `current`, `llm_candidate`: generalised tonic–clonic seizures occurring rarely
- `llm:9815:3` supporting, `last_event_only`, `recent`, `llm_candidate`: last reported three months ago

### Row 9879 - `cluster_axis_gap`

- Gold label: `unknown`
- Gold reference: focal tonic with missed ASM doses
- Assessment: Patient reports brief clusters of focal tonic seizures over the past three months, typically lasting under a minute with rapid recovery, linked to missed medication doses. No generalization or postictal deficits noted. Adherence strategies and monitoring planned.
- Source normalized phrase: `brief clusters of events over the past three months`
- Projection issues: `cluster_frequency_operands_unparsed, cluster_cadence_operands_incomplete`
- Route families: `cluster_axis_ambiguity`

Candidate evidence:

- `llm:9879:1` primary, `cluster_frequency`, `recent`, `llm_candidate`: over the past three months she has had brief clusters of events described as “jaw tightness then body goes stiff on the right, and I can’t get words out”, typically lasting under a minute with rapid recovery

### Row 9888 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: Sporadic complex partial seizures this year
- Assessment: The patient reports sporadic complex partial seizures this year with no generalised tonic-clonic seizures since late last year. VNS is functioning well and no recent injuries or post-ictal confusion noted. Sleep irregularity may correlate with focal events. Continued current medication and monitoring advised.
- Source normalized phrase: `sporadic complex partial seizures this year`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:9888:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no generalised tonic-clonic seizures since
- `llm:9888:1` primary, `frequency_rate`, `recent`, `llm_candidate`: This year they report Sporadic complex partial seizures this year, typically brief episodes of impaired awareness with automatisms lasting under two minutes, recovering without post-ictal confusion.
- `llm:9888:2` rejected, `last_event_only`, `historical`, `llm_candidate`: There have been no generalised tonic-clonic seizures since late last year, and no injuries.

### Row 9912 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: Sporadic simple partial seizures this year
- Assessment: The patient currently experiences sporadic simple partial seizures this year without loss of awareness, with no generalized seizures reported this year. Seizure frequency and daily functioning are stable compared to last year.
- Source normalized phrase: `sporadic simple partial seizures this year`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:9912:1` primary, `frequency_rate`, `current`, `llm_candidate`: Sporadic simple partial seizures this year
- `llm:9912:2` supporting, `last_event_only`, `current`, `llm_candidate`: none reported this year

### Row 9937 - `cluster_axis_gap`

- Gold label: `1 cluster per month, multiple per cluster`
- Gold reference: Monthly clusters; within-cluster count unclear
- Assessment: The patient reports improved seizure control with periodic bursts roughly every few weeks and extended seizure-free stretches outside these periods. No injuries or missed medications noted; current pattern suggests improvement with lifestyle changes.
- Source normalized phrase: `periodic bursts roughly every few weeks`
- Projection issues: `cluster_frequency_operands_unparsed, cluster_cadence_operands_incomplete`
- Route families: `cluster_axis_ambiguity`

Candidate evidence:

- `det:9937:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: every few weeks
- `llm:9937:1` primary, `cluster_frequency`, `recent`, `llm_candidate`: The current pattern is best described as periodic bursts roughly every few weeks with an imprecise number of events per burst; outside these periods he has extended stretches without symptoms.

### Row 10371 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple year`
- Gold reference: Prior cluster pattern resolved since 11 Aug 2023
- Assessment: The patient has been seizure-free since 11 August 2023 with no events witnessed during high-heat service periods and no emergency assistance or time off required. Medication adherence is confirmed, and the prior cluster pattern has resolved.
- Source normalized phrase: `Prior cluster pattern resolved since 11 Aug 2023`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:10371:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: Prior cluster pattern resolved since 11 Aug 2023
- `llm:10371:1` rejected, `cluster_frequency`, `historical`, `llm_candidate`: Prior cluster pattern resolved since 11 Aug 2023.
- `llm:10371:2` supporting, `unknown_frequency`, `current`, `llm_candidate`: No events witnessed by colleagues during high-heat service periods, including double shifts and bank holiday brunch service.
- `llm:10371:3` supporting, `unknown_frequency`, `recent`, `llm_candidate`: She denies missed doses over the last 3 months.
- `llm:10371:4` supporting, `unknown_frequency`, `recent`, `llm_candidate`: She has not required any emergency assistance or time off due to events since the above date.

### Row 10434 - `cluster_axis_gap`

- Gold label: `multiple cluster per week, 2 to 3 per cluster`
- Gold reference: More frequent morning clusters despite adherence
- Assessment: The patient experiences brief focal aware seizure clusters on several mornings each week despite medication adherence. These episodes are short, with no loss of awareness or injuries. The patient is monitoring potential triggers including arc-light exposure and sleep patterns. No medication changes have been made yet; safety measures at work are in place.
- Source normalized phrase: `on several mornings each week`
- Projection issues: `vague_count, vague_count, cluster_cadence_operands_incomplete`
- Route families: `cluster_axis_ambiguity`

Candidate evidence:

- `det:10434:1` primary, `cluster_frequency`, `unclear`, `deterministic_candidate`: on several mornings each week
- `llm:10434:1` supporting, `unknown_frequency`, `recent`, `llm_candidate`: brief episodes are tending to bunch together after he wakes, occurring on several mornings each week

### Row 10509 - `cyclic_window_without_count`

- Gold label: `unknown`
- Gold reference: New nocturnal clustering with early-morning spillover
- Assessment: The patient reports a recent change in seizure pattern over the past three months with clusters occurring after nights of curtailed sleep, typically in the latter half of the night and sometimes continuing into early morning. These clusters are linked to late-night screen exposure and irregular sleep. No convulsive injuries reported; episodes involve brief impaired awareness and lip-smacking with recovery in minutes followed by fatigue. Prior EEGs and MRI were non-diagnostic. Management includes sleep hygiene education and initiation of topiramate.
- Source normalized phrase: `clusters arising after nights of curtailed sleep`
- Projection issues: `cluster_frequency_operands_unparsed, cluster_cadence_operands_incomplete, cyclic_window_without_event_count`
- Route families: `cyclic_window_without_event_count`

Candidate evidence:

- `llm:10509:1` primary, `cluster_frequency`, `recent`, `llm_candidate`: She reports a recent shift in her seizure pattern over the past three months, characterised by clusters arising after nights of curtailed sleep, most often grouped during the latter half of the night with occasional continuation into the ea

### Row 10542 - `cluster_axis_gap`

- Gold label: `unknown, 2 to 4 per cluster`
- Gold reference: When clusters occur, typically two to four absences over ~1 h; frequency not tracked
- Assessment: Patient experiences clusters of two to four brief absence seizures over about one hour, typically triggered by poor sleep or stress. No generalized tonic-clonic seizures or injuries reported. Current antiseizure medication unchanged with good adherence. Continued monitoring with seizure diary app recommended.
- Source normalized phrase: `two to four absences per cluster over approximately 1 hour`
- Projection issues: `cluster_frequency_operands_unparsed, cluster_cadence_operands_incomplete`
- Route families: `cluster_axis_ambiguity`

Candidate evidence:

- `llm:10542:1` primary, `cluster_frequency`, `recent`, `llm_candidate`: When clusters occur, typically two to four absences over ~1 h; frequency not tracked.

### Row 10578 - `cluster_axis_gap`

- Gold label: `unknown, 3 to 4 per cluster`
- Gold reference: Clusters characterized by three - four focal impaired-awareness seizures; frequency unclear
- Assessment: Patient reports clusters of three to four focal impaired-awareness seizures with unclear frequency; no formal diary kept. Triggers include sleep disruption, stress, and missed doses. EEG and MRI planned for further classification.
- Source normalized phrase: `three to four focal impaired-awareness seizures per cluster`
- Projection issues: `cluster_frequency_operands_unparsed, cluster_cadence_operands_incomplete`
- Route families: `cluster_axis_ambiguity`

Candidate evidence:

- `det:10578:1` supporting, `unknown_frequency`, `unclear`, `deterministic_candidate`: clusters characterized by three - four focal impaired-awareness seizures; frequency unclear
- `llm:10578:1` primary, `cluster_frequency`, `current`, `llm_candidate`: he describes clusters characterized by three - four focal impaired-awareness seizures

### Row 10630 - `cluster_axis_gap`

- Gold label: `multiple cluster per 2 week, 5 per cluster`
- Gold reference: Per-cluster load around 5 brief events; timing tends to be evenings
- Assessment: The patient experiences seizure clusters several evenings per fortnight, each cluster involving roughly five brief seizures. Clustering tends to occur later in the day after evening meals, with increased prominence during periods of fasting and routine disruption. No injuries or prolonged post-event confusion reported. Medication regimen is stable with no new adverse effects.
- Source normalized phrase: `several evenings per fortnight with roughly five short-lived spells per cluster`
- Projection issues: `vague_count, cluster_cadence_operands_incomplete`
- Route families: `cluster_axis_ambiguity`

Candidate evidence:

- `llm:10630:1` primary, `cluster_frequency`, `current`, `llm_candidate`: On average, each cluster involves roughly five short-lived spells with brief recovery between them, and these clusters arise on several evenings per fortnight.
- `llm:10630:2` supporting, `unknown_frequency`, `current`, `llm_candidate`: He describes that his episodes tend to occur in small clusters, most often later in the day, typically after his evening meal.

### Row 11216 - `seizure_free_duration_gap`

- Gold label: `unknown`
- Gold reference: Last seizure on 25 December 2023
- Assessment: The patient has been seizure free since 25 December 2023 with no subsequent events reported and no absences noted by colleagues or family, indicating good seizure control under current treatment.
- Source normalized phrase: `seizure freedom since 25 December 2023`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:11216:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: Last seizure on 25 December 2023
- `det:11216:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no absences noted by colleagues or family. Sleep has been more regular since
- `llm:11216:2` primary, `seizure_free`, `recent`, `llm_candidate`: seizure freedom since 25 December 2023
- `det:11216:4` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: No subsequent events reported
- `det:11216:5` rejected, `unknown_frequency`, `unclear`, `deterministic_candidate`: Last seizure
- `llm:11216:1` supporting, `last_event_only`, `recent`, `llm_candidate`: Last seizure on 25 December 2023.

### Row 11254 - `seizure_free_duration_gap`

- Gold label: `unknown`
- Gold reference: Last seizure on 31-May
- Assessment: The patient had a single focal aware seizure on 31-May with no further seizures recorded since then, indicating a current seizure-free state. No generalised tonic–clonic seizures have been reported in the past year. Stability is supported by medication adherence and lifestyle improvements.
- Source normalized phrase: `no further seizures recorded since last event on 31-May`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:11254:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no generalised tonic–clonic seizures reported
- `det:11254:2` rejected, `unknown_frequency`, `unclear`, `deterministic_candidate`: Last seizure
- `llm:11254:1` supporting, `last_event_only`, `recent`, `llm_candidate`: Last seizure on 31-May, described as a brief focal aware event lasting approximately 20–30 seconds without loss of awareness, occurring in the late afternoon after a disrupted sleep routine.
- `llm:11254:2` primary, `unknown_frequency`, `recent`, `llm_candidate`: Since then, no further events have been recorded by the patient or noted by the key worker.

### Row 11272 - `seizure_free_duration_gap`

- Gold label: `unknown`
- Gold reference: Last seizure on 20/Dec
- Assessment: The patient has been seizure-free since the last seizure on 20 December 2016, with no seizures reported since then. She remains on stable medication with good adherence and no recent adverse events.
- Source normalized phrase: `no seizures since last seizure on 20/Dec`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:11272:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: no seizures since
- `det:11272:2` supporting, `unknown_frequency`, `unclear`, `deterministic_candidate`: last seizure
- `llm:11272:1` supporting, `last_event_only`, `recent`, `llm_candidate`: She confirms that her last seizure on 20/Dec occurred in the early morning with a brief generalised convulsion lasting approximately 90 seconds, followed by typical post-ictal confusion for 15 60 minutes. There have been no seizures since t

### Row 11337 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: patient reported having a seizure on 06-Nov
- Assessment: Patient had one breakthrough generalized tonic-clonic seizure on 06-Nov following two missed evening doses and significant sleep deprivation; no absence seizures reported in past eight weeks; otherwise stable on valproate with improved concentration after stopping topiramate.
- Source normalized phrase: `one seizure on 06-Nov after missed doses and sleep deprivation`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:11337:1` primary, `last_event_only`, `recent`, `llm_candidate`: patient reported having a seizure on 06-Nov following two missed evening doses and significant sleep deprivation.

### Row 11389 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: The patient gave a history of seizure on 21 December
- Assessment: Patient reports a single recent focal seizure on 21 December with otherwise stable control and no secondary generalization.
- Source normalized phrase: `one focal seizure on 21 December`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:11389:1` primary, `last_event_only`, `recent`, `llm_candidate`: The patient gave a history of seizure on 21 December

### Row 12127 - `additive_mixed_window_or_vague`

- Gold label: `multiple per week`
- Gold reference: focal non-motor occur several times each week, particularly in the evenings. Generalised convulsions seizures are rare, typically two events per year
- Assessment: The patient experiences several focal non-motor seizures weekly, particularly in the evenings, with rare generalised convulsions approximately twice per year. The last generalised convulsion occurred three months ago during air travel, linked to poor sleep and anxiety. Medication adherence is good, and no new neurological symptoms are reported.
- Source normalized phrase: `several focal non-motor seizures per week and two generalised convulsions per year`
- Projection issues: `vague_count, additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `llm:12127:2` primary, `frequency_rate`, `current`, `llm_candidate`: Generalised convulsions seizures are rare, typically two events per year.
- `det:12127:3` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: focal non-motor occur several times each week
- `llm:12127:1` supporting, `unknown_frequency`, `current`, `llm_candidate`: The patient reports focal non-motor occur several times each week, particularly in the evenings.
- `llm:12127:3` supporting, `last_event_only`, `recent`, `llm_candidate`: The last generalised convulsion occurred mid-flight returning from holiday three months ago

### Row 12192 - `additive_mixed_window_or_vague`

- Gold label: `1 per day`
- Gold reference: Her seizure control is variable but the family feels it is acceptable, she continues to experience drop attack on a daily basis, myoclonic jerks in morning clusters, and occasional generalised tonic-clonic seizures, this pattern has remained unchanged for several years
- Assessment: The patient experiences daily drop attacks, focal aware seizures approximately twice weekly, and occasional generalised tonic-clonic seizures. The focal aware episodes are brief and do not generalise. Seizure control is variable but stable over several years. No recent injuries or hospital admissions. Ongoing reduction in alcohol use is noted with no apparent change in seizure burden.
- Source normalized phrase: `drop attack on a daily basis, twice weekly focal aware episodes, occasional generalised tonic-clonic seizures`
- Projection issues: `frequency_rate_operands_unparsed, additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `llm:12192:1` primary, `frequency_rate`, `current`, `llm_candidate`: she continues to experience drop attack on a daily basis
- `det:12192:2` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: occurring approximately twice weekly
- `llm:12192:3` primary, `frequency_rate`, `current`, `llm_candidate`: occasional generalised tonic-clonic seizures
- `llm:12192:4` supporting, `frequency_rate`, `current`, `llm_candidate`: brief focal aware episodes with speech arrest and right-hand automatisms occurring approximately twice weekly

### Row 12236 - `additive_mixed_window_or_vague`

- Gold label: `1 per day`
- Gold reference: Her seizure control is variable but the family feels it is acceptable, she continues to experience absence seizures on a daily basis, myoclonic jerks in morning clusters, and occasional generalised tonic-clonic seizures, this pattern has remained unchanged for several years
- Assessment: The patient experiences daily absence seizures and occasional generalized tonic-clonic seizures, with myoclonic jerks occurring in morning clusters. The seizure pattern has remained stable for several years and is considered acceptable by the patient and family.
- Source normalized phrase: `daily absence seizures and occasional generalised tonic-clonic seizures`
- Projection issues: `frequency_rate_operands_unparsed, additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `llm:12236:1` primary, `frequency_rate`, `current`, `llm_candidate`: she continues to experience absence seizures on a daily basis
- `llm:12236:2` supporting, `cluster_frequency`, `current`, `llm_candidate`: myoclonic jerks in morning clusters
- `llm:12236:3` primary, `frequency_rate`, `current`, `llm_candidate`: occasional generalised tonic-clonic seizures

### Row 12314 - `frequency_operands_gap`

- Gold label: `3 per week`
- Gold reference: Although his seizures fluctuate, his parents consider him reasonably well controlled, he still has generalised tonic-clonic seizures three nights per week, drop attacks occurring in batches, and tonic seizures during both day and night, this long-standing pattern has persisted without major change
- Assessment: The patient experiences generalised tonic-clonic seizures approximately three nights per week, with additional drop attacks and tonic seizures occurring in clusters. The overall seizure pattern is stable without major change. Sleep hygiene and stimulant use are being addressed as potential triggers.
- Source normalized phrase: `generalised tonic-clonic seizures three nights per week`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:12314:1` primary, `frequency_rate`, `current`, `llm_candidate`: he still has generalised tonic-clonic seizures three nights per week

### Row 12366 - `additive_mixed_window_or_vague`

- Gold label: `4 per day`
- Gold reference: He still has simple partial seizures 4 times per day, drop attacks occurring in batches, and tonic-clonic seizures 2 times per month, this long-standing pattern has persisted without major change
- Assessment: The patient has a stable baseline seizure frequency with simple partial seizures occurring 4 times daily and tonic-clonic seizures 2 times monthly. There is reported increased clustering of drop attacks and postictal fatigue after recent travel, but these are contextual and not additive to the primary frequency burden.
- Source normalized phrase: `simple partial seizures 4 times per day and tonic-clonic seizures 2 times per month`
- Projection issues: `additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `llm:12366:1` primary, `frequency_rate`, `current`, `llm_candidate`: He still has simple partial seizures 4 times per day
- `llm:12366:3` primary, `frequency_rate`, `current`, `llm_candidate`: tonic-clonic seizures 2 times per month

### Row 12378 - `additive_mixed_window_or_vague`

- Gold label: `4 per day`
- Gold reference: He still has focal clonic 4 times per day, drop attacks occurring in batches, and tonic-clonic seizures 2 times per month, this long-standing pattern has persisted without major change
- Assessment: The patient experiences a stable pattern of focal clonic seizures occurring 4 times daily and tonic-clonic seizures 2 times monthly, with clusters occurring closer together after sleep disruption but no increase in overall frequency.
- Source normalized phrase: `focal clonic 4 times per day and tonic-clonic seizures 2 times per month`
- Projection issues: `additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `llm:12378:1` primary, `frequency_rate`, `recent`, `llm_candidate`: He still has focal clonic 4 times per day
- `llm:12378:3` primary, `frequency_rate`, `recent`, `llm_candidate`: tonic-clonic seizures 2 times per month

### Row 12383 - `unresolved_multiple`

- Gold label: `4 per day`
- Gold reference: He still has focal onset seizures four times per day, drop attacks occurring in batches, and tonic-clonic seizures 2 times per month, this long-standing pattern has persisted without major change
- Assessment: The patient experiences multiple seizure types with distinct frequencies: frequent focal onset seizures daily, drop attacks in clusters, and less frequent tonic-clonic seizures monthly. These represent separate axes of seizure burden and are additive in the overall assessment.
- Source normalized phrase: `focal onset seizures four times per day, drop attacks occurring in batches, tonic-clonic seizures 2 times per month`
- Projection issues: `unresolved_multiple_not_renderable`
- Route families: ``

Candidate evidence:

- `llm:12383:1` primary, `frequency_rate`, `current`, `llm_candidate`: he still has focal onset seizures four times per day
- `llm:12383:3` primary, `frequency_rate`, `current`, `llm_candidate`: tonic-clonic seizures 2 times per month
- `llm:12383:2` primary, `cluster_frequency`, `current`, `llm_candidate`: drop attacks occurring in batches

### Row 12403 - `additive_mixed_window_or_vague`

- Gold label: `2 to 3 per day`
- Gold reference: He still has focal aware seizures 2 to 3 times per day, drop attacks occurring in batches, and tonic-clonic seizures 2 times per month, this long-standing pattern has persisted without major change
- Assessment: The patient experiences frequent focal aware seizures daily and tonic-clonic seizures twice monthly. Drop attacks occur in clusters once or twice a month, typically triggered by sleep irregularity after moving between households. No recent injuries or prolonged events reported. Adherence is good with coordinated medication management across two households. Safety measures are in place including non-slip mats and seizure supervision at night. The plan includes continued monitoring with seizure diaries and pharmacy records to guide future management.
- Source normalized phrase: `focal aware seizures 2 to 3 times per day and tonic-clonic seizures 2 times per month`
- Projection issues: `additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `llm:12403:1` primary, `frequency_rate`, `current`, `llm_candidate`: He still has focal aware seizures 2 to 3 times per day
- `llm:12403:3` primary, `frequency_rate`, `current`, `llm_candidate`: and tonic-clonic seizures 2 times per month
- `det:12403:3` rejected, `frequency_rate`, `unclear`, `deterministic_candidate`: twice a month
- `llm:12403:2` supporting, `cluster_frequency`, `current`, `llm_candidate`: The drop attacks tend to occur in flurries over 24–48 hours once or twice a month

### Row 12422 - `additive_mixed_window_or_vague`

- Gold label: `1 per day`
- Gold reference: Seizure control is inconsistent and while the caregiver perceives stability, she continues to have nightly generalised convulsions seizures and intermittent tonic seizures four times per year, this has been her enduring seizure profile for many years
- Assessment: The patient experiences nightly generalized convulsions and intermittent tonic seizures approximately four times per year, consistent with a stable seizure profile over many years. No recent changes in medication or rescue treatment use were reported, and no new triggers identified. Post-ictal recovery is slow but predictable with fatigue and transient confusion. No status epilepticus or hospital admissions recently.
- Source normalized phrase: `nightly generalised convulsions seizures and intermittent tonic seizures four times per year`
- Projection issues: `additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `llm:12422:2` primary, `frequency_rate`, `current`, `llm_candidate`: intermittent tonic seizures four times per year
- `llm:12422:1` primary, `frequency_rate`, `current`, `llm_candidate`: she continues to have nightly generalised convulsions seizures

### Row 12456 - `additive_mixed_window_or_vague`

- Gold label: `1 per day`
- Gold reference: Seizure control is inconsistent and while the caregiver perceives stability, she continues to have nightly generalised tonic-clonic seizures and intermittent tonic seizures three times per year, this has been her enduring seizure profile for many years
- Assessment: The patient experiences nightly generalized tonic-clonic seizures and intermittent tonic seizures approximately three times per year, representing a persistent and enduring seizure burden over many years.
- Source normalized phrase: `nightly generalised tonic-clonic seizures plus intermittent tonic seizures three times per year`
- Projection issues: `additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `llm:12456:2` primary, `frequency_rate`, `current`, `llm_candidate`: intermittent tonic seizures three times per year
- `llm:12456:1` primary, `frequency_rate`, `current`, `llm_candidate`: she continues to have nightly generalised tonic-clonic seizures

### Row 12460 - `additive_mixed_window_or_vague`

- Gold label: `1 per day`
- Gold reference: Seizure control is inconsistent and while the caregiver perceives stability, she continues to have nightly generalised convulsions seizures and intermittent tonic seizures two times per year, this has been her enduring seizure profile for many years
- Assessment: The patient experiences nightly generalized convulsions and intermittent tonic seizures approximately twice per year, consistent with a long-standing seizure profile. Caregiver diary supports stability; no recent emergency presentations or injuries reported.
- Source normalized phrase: `nightly generalised convulsions seizures and intermittent tonic seizures two times per year`
- Projection issues: `additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `llm:12460:2` primary, `frequency_rate`, `current`, `llm_candidate`: intermittent tonic seizures two times per year
- `llm:12460:1` primary, `frequency_rate`, `current`, `llm_candidate`: she continues to have nightly generalised convulsions seizures

### Row 12484 - `additive_mixed_window_or_vague`

- Gold label: `3 to 4 per day`
- Gold reference: There has been little alteration in seizure frequency over the past year; she experiences one to two generalised tonic-clonic seizures yearly with the longest seizure-free period being three weeks. She has three - four absences per day. In addition, she suffers clusters of myoclonic jerks and occasional tonic seizures, these occur roughly once a month. No seizures have been recorded since her last appointment
- Assessment: The patient experiences one to two generalized tonic-clonic seizures yearly and three to four absences daily. She also has clusters of myoclonic jerks and occasional tonic seizures roughly once a month, which are noted as context but not additive to the primary frequency burden. No seizures have been recorded since the last appointment, with the longest seizure-free period historically being three weeks. Recent perceived worsening after travel is noted but not reflected in objective seizure frequency.
- Source normalized phrase: `one to two generalised tonic-clonic seizures yearly; three to four absences per day`
- Projection issues: `additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `det:12484:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: No seizures have been recorded since
- `det:12484:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no events have been documented since
- `det:12484:3` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: three - four absences per day
- `det:12484:4` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: once a month
- `llm:12484:1` primary, `frequency_rate`, `current`, `llm_candidate`: she experiences one to two generalised tonic-clonic seizures yearly
- `llm:12484:2` primary, `frequency_rate`, `current`, `llm_candidate`: She has three - four absences per day
- `llm:12484:3` supporting, `cluster_frequency`, `current`, `llm_candidate`: In addition, she suffers clusters of myoclonic jerks and occasional tonic seizures, these occur roughly once a month
- `llm:12484:4` supporting, `seizure_free`, `historical`, `llm_candidate`: with the longest seizure-free period being three weeks
- `llm:12484:5` supporting, `last_event_only`, `recent`, `llm_candidate`: No seizures have been recorded since her last appointment

### Row 12506 - `additive_mixed_window_or_vague`

- Gold label: `4 per day`
- Gold reference: There has been little alteration in seizure frequency over the past year; she experiences one to two generalised tonic-clonic seizures monthly with the longest seizure-free period being three weeks. She has 4 absences per day. In addition, she suffers clusters of myoclonic jerks and occasional tonic seizures, these occur roughly once a month. No seizures have been recorded since her last appointment
- Assessment: The patient currently experiences one to two generalized tonic-clonic seizures monthly and 4 absences per day. Clusters of myoclonic jerks and occasional tonic seizures occur roughly once a month and are noted as context. No seizures have been recorded since the last appointment, indicating some seizure-free intervals. The phrase 'once a month' without specification was rejected due to ambiguity. The overall seizure burden is stable with multiple seizure types contributing to the frequency.
- Source normalized phrase: `one to two generalised tonic-clonic seizures monthly plus 4 absences per day`
- Projection issues: `additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `llm:12506:4` supporting, `seizure_free`, `recent`, `llm_candidate`: No seizures have been recorded since her last appointment
- `llm:12506:2` primary, `frequency_rate`, `current`, `llm_candidate`: She has 4 absences per day
- `det:12506:3` rejected, `frequency_rate`, `unclear`, `deterministic_candidate`: once a month
- `llm:12506:1` primary, `frequency_rate`, `current`, `llm_candidate`: she experiences one to two generalised tonic-clonic seizures monthly
- `llm:12506:3` supporting, `cluster_frequency`, `current`, `llm_candidate`: clusters of myoclonic jerks and occasional tonic seizures, these occur roughly once a month

### Row 12537 - `additive_mixed_window_or_vague`

- Gold label: `1 per day`
- Gold reference: Seizure frequency remains unchanged over the last six months; he continues to have up to three generalised tonic-clonic seizures per week, rarely achieving more than ten consecutive seizure-free days. He also has daily drop attacks. Furthermore, focal impaired-awareness seizures with disorientation are reported every four to six weeks. No events have occurred since his most recent review
- Assessment: The patient experiences up to three generalised tonic-clonic seizures weekly, daily drop attacks, and focal impaired-awareness seizures every four to six weeks. Seizure frequency has remained stable over the past six months with rare seizure-free intervals exceeding ten days. No events have occurred since the most recent review. This burden is despite polytherapy and partial benefit from current treatment.
- Source normalized phrase: `up to three generalised tonic-clonic seizures per week, daily drop attacks, and focal impaired-awareness seizures every four to six weeks`
- Projection issues: `additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `det:12537:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: No events have occurred since
- `llm:12537:1` primary, `frequency_rate`, `recent`, `llm_candidate`: Seizure frequency remains unchanged over the last six months; he continues to have up to three generalised tonic-clonic seizures per week, rarely achieving more than ten consecutive seizure-free days.
- `llm:12537:3` primary, `frequency_rate`, `recent`, `llm_candidate`: focal impaired-awareness seizures with disorientation are reported every four to six weeks.
- `det:12537:4` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: daily drop attacks
- `llm:12537:2` primary, `frequency_rate`, `recent`, `llm_candidate`: He also has daily drop attacks.
- `llm:12537:4` supporting, `seizure_free`, `recent`, `llm_candidate`: Seizure frequency remains unchanged over the last six months; he continues to have up to three generalised tonic-clonic seizures per week, rarely achieving more than ten consecutive seizure-free days.
- `llm:12537:5` supporting, `last_event_only`, `recent`, `llm_candidate`: No events have occurred since his most recent review.

### Row 12551 - `additive_mixed_window_or_vague`

- Gold label: `1 per day`
- Gold reference: Seizure frequency remains unchanged over the last six months; he continues to have up to 2 generalised tonic-clonic seizures per year, rarely achieving more than ten consecutive seizure-free days. He also has daily drop attacks. Furthermore, focal impaired-awareness seizures with disorientation are reported every four to six weeks. No events have occurred since his most recent review
- Assessment: Patient experiences up to 2 generalized tonic-clonic seizures per year, focal impaired-awareness seizures every 4 to 6 weeks, and daily drop attacks. Rarely achieves more than ten consecutive seizure-free days. No events have occurred since the most recent review. Drop attacks may be precipitated by interrupted sleep due to childcare. Protective measures and adherence to medication are maintained.
- Source normalized phrase: `up to 2 generalised tonic-clonic seizures per year; focal impaired-awareness seizures every 4 to 6 weeks; daily drop attacks`
- Projection issues: `additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `det:12551:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: No events have occurred since
- `llm:12551:1` primary, `frequency_rate`, `recent`, `llm_candidate`: he continues to have up to 2 generalised tonic-clonic seizures per year
- `llm:12551:3` primary, `frequency_rate`, `recent`, `llm_candidate`: focal impaired-awareness seizures with disorientation are reported every four to six weeks
- `det:12551:4` rejected, `frequency_rate`, `unclear`, `deterministic_candidate`: daily drop attacks
- `llm:12551:2` primary, `frequency_rate`, `recent`, `llm_candidate`: He also has daily drop attacks.
- `llm:12551:4` supporting, `seizure_free`, `recent`, `llm_candidate`: rarely achieving more than ten consecutive seizure-free days
- `llm:12551:5` supporting, `last_event_only`, `recent`, `llm_candidate`: No events have occurred since his most recent review

### Row 12556 - `additive_mixed_window_or_vague`

- Gold label: `1 per day`
- Gold reference: Seizure frequency remains unchanged over the last six months; he continues to have up to 2 - 3 generalised tonic-clonic seizures per week, rarely achieving more than ten consecutive seizure-free days. He also has daily drop attacks. Furthermore, focal impaired-awareness seizures with disorientation are reported every four to six weeks. No events have occurred since his most recent review
- Assessment: The patient experiences up to 2-3 generalized tonic-clonic seizures weekly, daily drop attacks, and focal impaired-awareness seizures every 4-6 weeks. No seizures have occurred since the most recent review. Cluster patterns are reported following sleep deprivation and illness but are not additive to the primary frequency assessment. The patient rarely achieves more than ten consecutive seizure-free days.
- Source normalized phrase: `2-3 generalized tonic-clonic seizures per week, daily drop attacks, and focal impaired-awareness seizures every 4-6 weeks`
- Projection issues: `additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `det:12556:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: No events have occurred since
- `det:12556:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no events since
- `llm:12556:1` primary, `frequency_rate`, `recent`, `llm_candidate`: he continues to have up to 2 - 3 generalised tonic-clonic seizures per week
- `llm:12556:3` primary, `frequency_rate`, `recent`, `llm_candidate`: focal impaired-awareness seizures with disorientation are reported every four to six weeks
- `llm:12556:2` primary, `frequency_rate`, `recent`, `llm_candidate`: He also has daily drop attacks
- `llm:12556:4` supporting, `last_event_only`, `recent`, `llm_candidate`: No events have occurred since his most recent review

### Row 12562 - `additive_mixed_window_or_vague`

- Gold label: `1 per day`
- Gold reference: Seizure frequency remains unchanged over the last six months; he continues to have up to 3 or 4 generalised tonic-clonic seizures per week, rarely achieving more than ten consecutive seizure-free days. He also has daily drop attacks. Furthermore, focal impaired-awareness seizures with disorientation are reported every four to six weeks. No events have occurred since his most recent review
- Assessment: The patient continues to have up to 3 to 4 generalized tonic-clonic seizures weekly, daily drop attacks, and focal impaired-awareness seizures every 4 to 6 weeks. Rarely achieves more than ten consecutive seizure-free days. No events have occurred since the most recent review, which is a recent quiet period likely related to adherence to routines. The family is maintaining a seizure diary to monitor patterns and triggers.
- Source normalized phrase: `3 to 4 generalized tonic-clonic seizures per week, daily drop attacks, and focal impaired-awareness seizures every 4 to 6 weeks`
- Projection issues: `additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `det:12562:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: No events have occurred since
- `llm:12562:1` primary, `frequency_rate`, `current`, `llm_candidate`: he continues to have up to 3 or 4 generalised tonic-clonic seizures per week
- `llm:12562:3` primary, `frequency_rate`, `current`, `llm_candidate`: focal impaired-awareness seizures with disorientation are reported every four to six weeks
- `llm:12562:2` primary, `frequency_rate`, `current`, `llm_candidate`: He also has daily drop attacks
- `llm:12562:4` supporting, `seizure_free`, `current`, `llm_candidate`: rarely achieving more than ten consecutive seizure-free days
- `llm:12562:5` supporting, `last_event_only`, `recent`, `llm_candidate`: No events have occurred since his most recent review

### Row 12573 - `additive_mixed_window_or_vague`

- Gold label: `1 per day`
- Gold reference: Seizure frequency remains unchanged over the last six months; he continues to have up to two generalised tonic-clonic seizures per month, rarely achieving more than ten consecutive seizure-free days. He also has daily drop attacks. Furthermore, focal impaired-awareness seizures with disorientation are reported every four to six weeks. No events have occurred since his most recent review
- Assessment: The patient experiences up to two generalized tonic-clonic seizures per month, daily drop attacks, and focal impaired-awareness seizures every four to six weeks. Seizure frequency has remained stable over the last six months with rare seizure-free intervals of more than ten days. No events have occurred since the most recent review. Functional impact is worsening due to workplace triggers and injuries.
- Source normalized phrase: `up to two generalised tonic-clonic seizures per month, daily drop attacks, focal impaired-awareness seizures every four to six weeks`
- Projection issues: `additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `det:12573:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: No events have occurred since
- `llm:12573:1` primary, `frequency_rate`, `recent`, `llm_candidate`: Seizure frequency remains unchanged over the last six months; he continues to have up to two generalised tonic-clonic seizures per month, rarely achieving more than ten consecutive seizure-free days.
- `llm:12573:4` primary, `frequency_rate`, `recent`, `llm_candidate`: Furthermore, focal impaired-awareness seizures with disorientation are reported every four to six weeks.
- `det:12573:4` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: daily drop attacks
- `llm:12573:2` supporting, `seizure_free`, `recent`, `llm_candidate`: Seizure frequency remains unchanged over the last six months; he continues to have up to two generalised tonic-clonic seizures per month, rarely achieving more than ten consecutive seizure-free days.
- `llm:12573:3` supporting, `frequency_rate`, `recent`, `llm_candidate`: He also has daily drop attacks.
- `llm:12573:5` supporting, `last_event_only`, `recent`, `llm_candidate`: No events have occurred since his most recent review.

### Row 12584 - `additive_mixed_window_or_vague`

- Gold label: `1 per week`
- Gold reference: Over the past six months seizure control has been stable; she suffers one generalised tonic-clonic seizure every 3 months, with a maximum seizure-free period of four weeks. Weekly absences persist. She also experiences atonic seizures and focal seizures with impaired awareness, each arising once every few months. Since the last visit, she has not had any reported episodes
- Assessment: The patient has a stable seizure frequency with one generalised tonic-clonic seizure every 3 months, persistent weekly absence seizures, and atonic plus focal impaired awareness seizures each occurring every few months. Maximum seizure-free period is four weeks. Despite stable counts, there is qualitative deterioration in aura characteristics and post-ictal symptoms. No seizures reported since last visit.
- Source normalized phrase: `one generalised tonic-clonic seizure every 3 months; weekly absences; atonic and focal impaired awareness seizures each every few months`
- Projection issues: `vague_count, additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `llm:12584:1` primary, `frequency_rate`, `recent`, `llm_candidate`: she suffers one generalised tonic-clonic seizure every 3 months
- `llm:12584:5` primary, `frequency_rate`, `recent`, `llm_candidate`: She also experiences atonic seizures and focal seizures with impaired awareness, each arising once every few months
- `llm:12584:3` primary, `frequency_rate`, `current`, `llm_candidate`: Weekly absences persist
- `det:12584:6` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: Over the past six months seizure control has been stable; she suffers one generalised tonic-clonic seizure
- `llm:12584:2` supporting, `seizure_free`, `recent`, `llm_candidate`: with a maximum seizure-free period of four weeks
- `llm:12584:6` supporting, `last_event_only`, `recent`, `llm_candidate`: Since the last visit, she has not had any reported episodes

### Row 12641 - `additive_mixed_window_or_vague`

- Gold label: `1 per day`
- Gold reference: Seizure frequency has not altered significantly over the past six months; he continues to suffer one to two generalised tonic-clonic seizures per week, with a longest seizure-free interval of around three weeks. He has daily absences. In addition, he experiences focal sensory with disorientation every three to four weeks, together with drop attacks. Since the last clinic visit, no further seizures have been reported
- Assessment: The patient experiences a combined burden of one to two generalised tonic-clonic seizures per week, daily absence seizures, and focal sensory seizures every three to four weeks. The longest seizure-free interval is around three weeks. Triggers include sleep deprivation and missed meals. No recent hospital admissions or new neurological deficits reported.
- Source normalized phrase: `one to two generalised tonic-clonic seizures per week; daily absences; focal sensory seizures every three to four weeks`
- Projection issues: `additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `llm:12641:1` primary, `frequency_rate`, `recent`, `llm_candidate`: he continues to suffer one to two generalised tonic-clonic seizures per week
- `llm:12641:3` primary, `frequency_rate`, `recent`, `llm_candidate`: he experiences focal sensory with disorientation every three to four weeks
- `det:12641:3` rejected, `frequency_rate`, `unclear`, `deterministic_candidate`: daily absences
- `llm:12641:2` primary, `frequency_rate`, `recent`, `llm_candidate`: He has daily absences
- `llm:12641:4` supporting, `seizure_free`, `recent`, `llm_candidate`: with a longest seizure-free interval of around three weeks

### Row 12676 - `additive_mixed_window_or_vague`

- Gold label: `1 per day`
- Gold reference: Seizure frequency has not altered significantly over the past six months; he continues to suffer one to two generalised tonic-clonic seizures per year, with a longest seizure-free interval of around three weeks. He has daily absences. In addition, he experiences focal myoclonic with disorientation every three to four weeks, together with drop attacks. Since the last clinic visit, no further seizures have been reported
- Assessment: The patient currently experiences one to two generalized tonic-clonic seizures per year, daily absence seizures, and focal myoclonic seizures with disorientation every three to four weeks. The longest seizure-free interval is around three weeks. No seizures have been reported since the last clinic visit. Drop attacks are noted but frequency is unclear. This assessment integrates multiple seizure types contributing to the overall burden.
- Source normalized phrase: `one to two generalised tonic-clonic seizures per year; daily absences; focal myoclonic with disorientation every three to four weeks`
- Projection issues: `additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `llm:12676:1` primary, `frequency_rate`, `current`, `llm_candidate`: he continues to suffer one to two generalised tonic-clonic seizures per year
- `llm:12676:3` primary, `frequency_rate`, `current`, `llm_candidate`: he experiences focal myoclonic with disorientation every three to four weeks
- `det:12676:3` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: daily Seizure
- `det:12676:4` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: daily absences
- `llm:12676:2` primary, `frequency_rate`, `current`, `llm_candidate`: He has daily absences
- `llm:12676:4` supporting, `unknown_frequency`, `current`, `llm_candidate`: together with drop attacks
- `llm:12676:5` supporting, `seizure_free`, `current`, `llm_candidate`: with a longest seizure-free interval of around three weeks
- `llm:12676:6` supporting, `last_event_only`, `recent`, `llm_candidate`: Since the last clinic visit, no further seizures have been reported

### Row 12823 - `additive_mixed_window_or_vague`

- Gold label: `9 per month`
- Gold reference: Following introduction of lamotrigine, there has been a clear improvement in control, with just nine generalised tonic-clonic seizures documented this year to date
- Assessment: The patient has combined generalised tonic-clonic seizures with nine events documented this year and focal impaired-awareness seizures occurring roughly once every three to four weeks. Seizure control has improved on lamotrigine. No status epilepticus or prolonged post-ictal confusion reported. Clustering of focal seizures occurs after stress or disrupted sleep but is not quantified separately in burden.
- Source normalized phrase: `nine generalised tonic-clonic seizures this year and focal impaired-awareness seizures every three to four weeks`
- Projection issues: `additive_frequency_period_mismatch, frequency_rate_operands_incomplete`
- Route families: `mixed_window_or_vague_addition`

Candidate evidence:

- `llm:12823:1` primary, `frequency_rate`, `recent`, `llm_candidate`: just nine generalised tonic-clonic seizures documented this year to date
- `llm:12823:2` primary, `frequency_rate`, `current`, `llm_candidate`: now occurring roughly once every three to four weeks

### Row 12963 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: The family feel seizure frequency has decreased markedly since starting medication, with only seven seizures so far this year
- Assessment: The patient has experienced a substantial reduction in seizure frequency this year, with only a small handful of seizures recorded so far. Longer seizure-free intervals over the last 10 weeks are corroborated by the seizure diary, indicating improving control likely due to optimized medication and sleep hygiene.
- Source normalized phrase: `episodes have become noticeably fewer`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:12963:1` primary, `frequency_rate`, `recent`, `llm_candidate`: Since optimising Brivaracetam and reinforcing sleep routines, the family report that episodes have become noticeably fewer; to characterise it in their words, they feel the seizures have tailed off substantially this year, with only a small
- `llm:12963:2` rejected, `unknown_frequency`, `recent`, `llm_candidate`: Since optimising Brivaracetam and reinforcing sleep routines, the family report that episodes have become noticeably fewer; to characterise it in their words, they feel the seizures have tailed off substantially this year, with only a small
- `llm:12963:3` supporting, `seizure_free`, `recent`, `llm_candidate`: He is keeping a seizure diary which corroborates this trend and shows longer seizure-free intervals, particularly over the last 10 weeks.

### Row 13051 - `frequency_operands_gap`

- Gold label: `2 per 8 month`
- Gold reference: He remained seizure-free for 8 months after starting Levetiracetam 500 mg twice daily, before experiencing a generalised tonic-clonic seizure 3 Tuesdays ago, preceded by a cluster of absences
- Assessment: Patient had been seizure-free for 8 months on Levetiracetam before a recent generalised tonic-clonic seizure 3 weeks ago, preceded by a cluster of absences. The recent events occurred in the context of sleep deprivation and high study load. No further seizures reported since. Continued medication adherence noted.
- Source normalized phrase: `one generalised tonic-clonic seizure 3 weeks ago after 8 months seizure-free on Levetiracetam`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:13051:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: seizure-free for 8 months after starting Levetiracetam 500 mg twice daily, before experiencing a generalised tonic-clonic seizure 3 Tuesdays ago, preceded by a cluster of absences
- `llm:13051:1` supporting, `seizure_free`, `historical`, `llm_candidate`: He remained seizure-free for 8 months after starting Levetiracetam 500 mg twice daily
- `llm:13051:2` supporting, `cluster_frequency`, `recent`, `llm_candidate`: preceded by a cluster of absences
- `llm:13051:3` supporting, `last_event_only`, `recent`, `llm_candidate`: a generalised tonic-clonic seizure 3 Tuesdays ago

### Row 13114 - `frequency_operands_gap`

- Gold label: `1 per year`
- Gold reference: She had no seizures for nearly a year following initiation of Valproate, then developed myoclonic jerks leading to a tonic seizure two Saturdays ago
- Assessment: Patient had no seizures for nearly a year after starting Valproate, then experienced brief myoclonic jerks for two days followed by a tonic seizure two weeks ago. Current regimen adjusted with adjunct Levetiracetam to manage breakthrough seizures. Safety and lifestyle advice reinforced.
- Source normalized phrase: `one tonic seizure two weeks ago with preceding brief myoclonic jerks`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:13114:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: no seizures for nearly a year following initiation of Valproate, then developed myoclonic jerks leading to a tonic seizure two Saturdays ago
- `llm:13114:1` supporting, `seizure_free`, `historical`, `llm_candidate`: She had no seizures for nearly a year following initiation of Valproate
- `llm:13114:2` supporting, `last_event_only`, `recent`, `llm_candidate`: a tonic seizure two Saturdays ago
- `llm:13114:3` supporting, `unknown_frequency`, `recent`, `llm_candidate`: brief morning myoclonic jerks on the preceding two days

### Row 13190 - `frequency_operands_gap`

- Gold label: `1 per 5 month`
- Gold reference: On Carbamazepine monotherapy he was seizure-free for 5 months, until a focal impaired-awareness seizure occurred three Thursdays ago
- Assessment: Patient was seizure-free for 5 months on Carbamazepine monotherapy until a single focal impaired-awareness seizure occurred three weeks ago, attributed to sleep disruption and stress. No medication adherence issues reported. No changes made to treatment; plan to continue observation and follow-up in 3 months.
- Source normalized phrase: `seizure-free for 5 months, then 1 focal impaired-awareness seizure`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:13190:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: seizure-free for 5 months, until a focal impaired-awareness seizure occurred three Thursdays ago
- `llm:13190:1` rejected, `seizure_free`, `historical`, `llm_candidate`: On Carbamazepine monotherapy he was seizure-free for 5 months
- `llm:13190:2` supporting, `last_event_only`, `recent`, `llm_candidate`: a focal impaired-awareness seizure occurred three Thursdays ago

### Row 13209 - `frequency_operands_gap`

- Gold label: `1 per 8 month`
- Gold reference: On Carbamazepine monotherapy he was seizure-free for 8 months, until a focal impaired-awareness seizure occurred 2 Thursdays ago
- Assessment: Patient had a focal impaired-awareness seizure 2 weeks ago after 8 months seizure-free on Carbamazepine monotherapy. Seizures appear to cluster roughly every 4–5 weeks, possibly related to catamenial pattern. Increased stress and shorter sleep noted as potential triggers. Current burden is one seizure approximately every 4–5 weeks with recent breakthrough event.
- Source normalized phrase: `focal impaired-awareness seizure 2 weeks ago after 8 months seizure-free`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:13209:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: seizure-free for 8 months, until a focal impaired-awareness seizure occurred 2 Thursdays ago
- `det:13209:2` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: every 4–5 weeks
- `llm:13209:1` rejected, `seizure_free`, `historical`, `llm_candidate`: On Carbamazepine monotherapy he was seizure-free for 8 months
- `llm:13209:2` supporting, `last_event_only`, `recent`, `llm_candidate`: a focal impaired-awareness seizure occurred 2 Thursdays ago
- `llm:13209:3` supporting, `cluster_frequency`, `current`, `llm_candidate`: clusters of auras and brief blanks roughly every 4–5 weeks

### Row 13267 - `frequency_operands_gap`

- Gold label: `2 per 5 month`
- Gold reference: After commencing Clobazam 10 mg nocte, she had a five month remission, then sustained a drop attack 3 Mondays ago, preceded by myoclonic jerks
- Assessment: Patient had a five month seizure remission after starting Clobazam, followed by a recent single drop attack preceded by myoclonic jerks clustered around the late luteal phase as tracked by menstrual app. No other recent seizures reported. Clustering pattern and triggers noted but not additive to frequency burden.
- Source normalized phrase: `one drop attack 3 weeks ago after 5 month remission`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:13267:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: five month remission, then sustained a drop attack 3 Mondays ago, preceded by myoclonic jerks
- `llm:13267:1` rejected, `seizure_free`, `historical`, `llm_candidate`: After commencing Clobazam 10 mg nocte, she had a five month remission
- `llm:13267:2` supporting, `last_event_only`, `recent`, `llm_candidate`: After commencing Clobazam 10 mg nocte, she had a five month remission, then sustained a drop attack 3 Mondays ago
- `llm:13267:4` supporting, `last_event_only`, `recent`, `llm_candidate`: She tracked her cycles using a menstrual app and shared that the single recent drop attack occurred three days before onset of her period; she had noted a run of brief myoclonic jerks over the preceding weekend.

### Row 13290 - `frequency_operands_gap`

- Gold label: `4 per 6 month`
- Gold reference: He did not have seizures for over 6 months, but then reported two generalised tonic-clonic seizures two Fridays ago, each preceded by myoclonic jerks
- Assessment: The patient was seizure-free for over 6 months but recently experienced two generalised tonic-clonic seizures two weeks ago, each preceded by clusters of myoclonic jerks occurring shortly after waking. Medication adherence is good, and no injuries occurred. Sleep disruption and stress may be contributing factors. Continued monitoring and planned EEG are in place.
- Source normalized phrase: `two generalised tonic-clonic seizures two Fridays ago, each preceded by myoclonic jerks`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:13290:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: did not have seizures for over 6 months, but then reported two generalised tonic-clonic seizures two Fridays ago, each preceded by myoclonic jerks
- `llm:13290:1` supporting, `seizure_free`, `historical`, `llm_candidate`: He did not have seizures for over 6 months
- `llm:13290:2` supporting, `last_event_only`, `recent`, `llm_candidate`: two generalised tonic-clonic seizures two Fridays ago

### Row 13327 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple year`
- Gold reference: With a history of Lennox–Gastaut syndrome, previously experiencing convulsions, atonic drop attacks and atypical absences, she has now been seizure free for several years
- Assessment: The patient has been seizure free for several years following VNS optimisation, with marked clinical improvement and no recent seizures or emergency presentations.
- Source normalized phrase: `seizure free for several years`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:13327:1` primary, `seizure_free`, `historical`, `llm_candidate`: she has now been seizure free for several years

### Row 13485 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple year`
- Gold reference: With structural focal epilepsy presenting as focal onset seizures and secondarily generalised convulsions, he has been seizure free for a long duration and has not reported seizures for over several years
- Assessment: Patient has been seizure free for a long duration with no reported seizures for several years. Previous events were reclassified as non-epileptic and are historical. No antiseizure medication is currently indicated.
- Source normalized phrase: `seizure free for a long duration with no reported seizures for several years`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:13485:1` primary, `seizure_free`, `historical`, `llm_candidate`: he has been seizure free for a long duration and has not reported seizures for over several years
- `det:13485:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: free of events since
- `llm:13485:2` rejected, `unknown_frequency`, `historical`, `llm_candidate`: Previous events recorded several years ago were reclassified as non-epileptic (likely stress-related episodes without electrographic correlate)

### Row 13487 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple year`
- Gold reference: With structural focal epilepsy presenting as simple partial seizures and secondarily generalised convulsions, he has been seizure free for a long duration and has not reported seizures for over several years
- Assessment: The patient has been in stable long-term remission with no reported seizures for several years, indicating excellent seizure control on current treatment.
- Source normalized phrase: `seizure free for a long duration and has not reported seizures for over several years`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:13487:1` primary, `seizure_free`, `historical`, `llm_candidate`: he has been seizure free for a long duration and has not reported seizures for over several years

### Row 13574 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple year`
- Gold reference: He previously suffered from frequent clusters of myoclonic jerks, absence seizures and occasional convulsive events 1 or 2 times per year, but is currently in long-term remission, having been seizure free for years
- Assessment: Patient is currently in long-term remission with no seizures for years; previous frequency was 1 to 2 seizures per year. No recent events or relapse reported.
- Source normalized phrase: `currently in long-term remission, having been seizure free for years`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:13574:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: currently in long-term remission, having been seizure free for years
- `det:13574:2` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: 1 or 2 times per year

### Row 13595 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple year`
- Gold reference: He previously suffered from frequent clusters of myoclonic jerks, absence seizures and occasional convulsive events 2 - 3 times per year, but is currently in long-term remission, having been seizure free for years
- Assessment: The patient is currently in long-term remission and seizure free for years, with no recent seizures logged in his diary. Historical seizure frequency was 2-3 times per year with frequent clusters, but this is now resolved. Medication adherence is excellent and no recent neurological issues reported. Continued seizure freedom is the dominant clinical status.
- Source normalized phrase: `currently in long-term remission, having been seizure free for years`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:13595:2` primary, `seizure_free`, `current`, `llm_candidate`: He previously suffered from frequent clusters of myoclonic jerks, absence seizures and occasional convulsive events 2 - 3 times per year, but is currently in long-term remission, having been seizure free for years
- `det:13595:2` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: 2 - 3 times per year
- `llm:13595:1` supporting, `cluster_frequency`, `historical`, `llm_candidate`: He previously suffered from frequent clusters of myoclonic jerks, absence seizures and occasional convulsive events 2 - 3 times per year

### Row 13598 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple year`
- Gold reference: He previously suffered from frequent clusters of myoclonic jerks, absence seizures and occasional convulsive events three times per year, but is currently in long-term remission, having been seizure free for years
- Assessment: Patient is currently in long-term remission with no seizures for years. Historical frequency of three times per year in clusters is noted but not current burden. No antiseizure medication or rescue therapy needed.
- Source normalized phrase: `currently in long-term remission, having been seizure free for years`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:13598:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: currently in long-term remission, having been seizure free for years
- `det:13598:2` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: three times per year
- `llm:13598:1` supporting, `cluster_frequency`, `historical`, `llm_candidate`: He previously suffered from frequent clusters of myoclonic jerks, absence seizures and occasional convulsive events three times per year

### Row 13608 - `seizure_free_duration_gap`

- Gold label: `seizure free for multiple year`
- Gold reference: He previously suffered from frequent clusters of myoclonic jerks, absence seizures and occasional convulsive events 2 times per year, but is currently in long-term remission, having been seizure free for years
- Assessment: The patient is currently in long-term remission with no seizures for years. Historical seizure clusters occurred about 2 times per year but have resolved. The patient self-discontinued antiseizure medication over three years ago with no recurrence. Continued monitoring and dietetic management are advised.
- Source normalized phrase: `currently in long-term remission, having been seizure free for years`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:13608:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: currently in long-term remission, having been seizure free for years
- `det:13608:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no recurrence
- `det:13608:3` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: 2 times per year
- `llm:13608:1` supporting, `cluster_frequency`, `historical`, `llm_candidate`: He previously suffered from frequent clusters of myoclonic jerks, absence seizures and occasional convulsive events 2 times per year

### Row 13627 - `frequency_operands_gap`

- Gold label: `64 per 12 month`
- Gold reference: Seizures in 2014-2015: May: 5 days with more severe seizures June: 5 days with seizures July: 12 days August: 3 days, most of them at sleep time, September: 12 days, October: 3 days with seizures November: 7 days with seizures, December: 5 days with more severe seizures January: 4 days, most of them at sleep time February: 2 days with seizures March: 5 days with more severe seizures, April: 1 days with seizures
- Assessment: The patient experiences recurrent seizures with variable frequency ranging from 1 to 12 days per month over the past year, showing intermittent clustering and a tendency for nocturnal events. No injuries or hospital admissions reported. Rescue medication not required. Ongoing management includes medication continuation and planned investigations to clarify seizure characteristics.
- Source normalized phrase: `Seizures occurred on multiple days per month with intermittent clustering and nocturnal tendency.`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:13627:1` primary, `frequency_rate`, `recent`, `llm_candidate`: Seizures in 2014-2015: May: 5 days with more severe seizures June: 5 days with seizures July: 12 days August: 3 days, most of them at sleep time, September: 12 days, October: 3 days with seizures November: 7 days with seizures, December: 5

### Row 13721 - `frequency_operands_gap`

- Gold label: `77 per 12 month`
- Gold reference: Seizures in 2024-2025: September: 7 days October: 3 days with seizures, November: 4 days, most of them at sleep time December: 7 days with seizures, January: 7 days with seizures February: 1 days with seizures March: 9 days with more severe seizures April: 10 days with seizures, May: 3 days with more severe seizures June: 6 days with more severe seizures July: 10 days, August: 10 days with seizures
- Assessment: The patient experiences seizures on multiple days each month over the past year, with some months having up to 10 seizure days, often at sleep time and with more severe seizures in some months. No clusters requiring emergency care have occurred since April 2025. Triggers include photosensitivity, sleep deprivation, and missed meals. Medication adherence has improved with no recent changes to regimen.
- Source normalized phrase: `Seizures on multiple days each month from September 2024 to August 2025, with some months having up to 10 seizure days`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:13721:1` primary, `frequency_rate`, `recent`, `llm_candidate`: Seizures in 2024-2025: September: 7 days October: 3 days with seizures, November: 4 days, most of them at sleep time December: 7 days with seizures, January: 7 days with seizures February: 1 days with seizures March: 9 days with more severe
- `llm:13721:2` supporting, `cluster_frequency`, `recent`, `llm_candidate`: No clusters requiring emergency care since April 2025.

### Row 13732 - `frequency_operands_gap`

- Gold label: `52 per 8 month`
- Gold reference: Seizures in 2024-2025: Aug: 6 days, most of them at sleep time, Sep: 11 days with seizures, Oct: 1 days, Nov: 7 days, most of them at sleep time, Dec: 8 days with seizures Jan: 9 days, Feb: 8 days with seizures Mar: 2 days
- Assessment: Patient reports variable seizure frequency month to month with several nocturnal events; history limited by intermittent device charging issues and lack of contemporaneous records. Further classification pending investigations. No recent hospital admissions or injuries reported. Plan includes obtaining prior EEG/MRI, providing paper diary, and monitoring medication adherence during power outages.
- Source normalized phrase: `Seizures occurred on 1 to 11 days per month from August 2024 to March 2025, mostly nocturnal in some months.`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:13732:1` primary, `frequency_rate`, `recent`, `llm_candidate`: Seizures in 2024-2025: Aug: 6 days, most of them at sleep time, Sep: 11 days with seizures, Oct: 1 days, Nov: 7 days, most of them at sleep time, Dec: 8 days with seizures Jan: 9 days, Feb: 8 days with seizures Mar: 2 days.

### Row 13922 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: She reported that since her medication was increased she has had two seizures, the most recent occurring on 9 Aug
- Assessment: Patient reports two recent focal impaired-awareness seizures since medication increase, with no secondary generalization or rescue medication use. Seizure frequency is satisfactory and stable for current management.
- Source normalized phrase: `she has had two seizures`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:13922:1` primary, `frequency_rate`, `recent`, `llm_candidate`: she has had two seizures

### Row 14092 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: She told me that since her last clinic appointment she has had 5 myoclonic jerks, the last reported on 7 April
- Assessment: Patient reports 5 myoclonic jerks since last clinic appointment, all brief and without loss of awareness or falls; no tonic-clonic seizures or emergency interventions. Events occurred mostly in early morning and were associated with sleep deprivation or missed meals. Medication adherence improved with digital supports. No new triggers or safety concerns noted. Plan to continue current medication and monitoring.
- Source normalized phrase: `5 myoclonic jerks since last clinic appointment, last on 7 April`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:14092:1` primary, `last_event_only`, `recent`, `llm_candidate`: She told me that since her last clinic appointment she has had 5 myoclonic jerks, the last reported on 7 April.

### Row 14096 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: She told me that since her last clinic appointment she has had five myoclonic jerks, the last reported on 08-Aug
- Assessment: Patient reports five myoclonic jerks since last appointment, last on 08-Aug, with no loss of awareness or other seizure types. No emergency attendances. Planning pregnancy with medication and safety review ongoing.
- Source normalized phrase: `five myoclonic jerks`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:14096:1` primary, `frequency_rate`, `recent`, `llm_candidate`: she has had five myoclonic jerks

### Row 14137 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: He noted that since beginning Clobazam he has had 3 - 4 generalised tonic-clonic seizures, the most recent on 23 December
- Assessment: Patient reports a clear deterioration with 3-4 generalised tonic-clonic seizures since starting Clobazam, most recent on 23 December. Previously, seizures were infrequent and brief. Nocturnal occurrences with tongue biting and myalgia noted. Historical infrequent events are rejected as primary burden.
- Source normalized phrase: `3 - 4 generalised tonic-clonic seizures`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:14137:1` primary, `frequency_rate`, `recent`, `llm_candidate`: he has had 3 - 4 generalised tonic-clonic seizures
- `llm:14137:2` supporting, `last_event_only`, `recent`, `llm_candidate`: the most recent on 23 December
- `llm:14137:3` rejected, `unknown_frequency`, `historical`, `llm_candidate`: events were infrequent
- `llm:14137:4` supporting, `unknown_frequency`, `recent`, `llm_candidate`: nocturnal occurrences

### Row 14146 - `frequency_operands_gap`

- Gold label: `unknown`
- Gold reference: He noted that since beginning Clobazam he has had 3 generalised tonic-clonic seizures, the most recent on 13 October
- Assessment: Patient has had 3 generalised tonic-clonic seizures since starting Clobazam, with the most recent on 13 October. One seizure was attributed to missed doses during a pharmacy supply delay. No myoclonic jerks or focal aware events reported. Family confirms typical post-ictal confusion lasting 30–40 minutes. Medication and supply continuity measures are in place, and follow-up is planned in 4 months or sooner if seizures increase.
- Source normalized phrase: `3 generalised tonic-clonic seizures since starting Clobazam, most recent on 13 October`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:14146:1` primary, `last_event_only`, `recent`, `llm_candidate`: He noted that since beginning Clobazam he has had 3 generalised tonic-clonic seizures, the most recent on 13 October.

### Row 14187 - `seizure_free_duration_gap`

- Gold label: `2 to 3 per month`
- Gold reference: She discontinued Valproate on 10 Jul. Shortly afterwards, she experienced 2 to 3 seizures, one triggered by missed medication. She has remained seizure-free since then
- Assessment: The patient experienced 2 to 3 seizures shortly after discontinuing valproate on 10 Jul, including one triggered by missed medication. Since then, she has remained seizure-free, attributing improvement to better adherence, sleep, and reduced caffeine. No recent myoclonic jerks or absence seizures reported. Safety precautions and follow-up monitoring are planned.
- Source normalized phrase: `She has remained seizure-free since then.`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:14187:2` primary, `seizure_free`, `recent`, `llm_candidate`: She has remained seizure-free since then.
- `det:14187:2` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: Shortly afterwards, she experienced 2 to 3 seizures
- `llm:14187:1` supporting, `last_event_only`, `recent`, `llm_candidate`: She discontinued Valproate on 10 Jul. Shortly afterwards, she experienced 2 to 3 seizures, one triggered by missed medication.

### Row 14214 - `seizure_free_duration_gap`

- Gold label: `2 to 4 per month`
- Gold reference: She discontinued Valproate on 27/Nov. Shortly afterwards, she experienced two to four seizures, one triggered by missed medication. She has remained seizure-free since then
- Assessment: The patient experienced two to four seizures shortly after discontinuing Valproate, including one triggered by missed medication, but has remained seizure-free since early December with improved medication adherence and sleep hygiene.
- Source normalized phrase: `She has remained seizure-free since then.`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:14214:2` primary, `seizure_free`, `recent`, `llm_candidate`: She has remained seizure-free since then.
- `det:14214:2` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: Shortly afterwards, she experienced two to four seizures
- `llm:14214:1` supporting, `last_event_only`, `historical`, `llm_candidate`: She discontinued Valproate on 27/Nov. Shortly afterwards, she experienced two to four seizures, one triggered by missed medication.

### Row 14250 - `seizure_free_duration_gap`

- Gold label: `2 per month`
- Gold reference: He came off Levetiracetam on 03-Mar. In the following week, he had 2 seizures, one associated with sleep deprivation. No further seizures have occurred since
- Assessment: The patient had 2 seizures in the week following discontinuation of Levetiracetam, one associated with sleep deprivation, but no further seizures have occurred since then, indicating improved seizure control and stability under the current regimen and dietetic supervision.
- Source normalized phrase: `No further seizures have occurred since`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:14250:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: No further seizures have occurred since
- `det:14250:3` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: In the following week, he had 2 seizures
- `llm:14250:1` supporting, `last_event_only`, `recent`, `llm_candidate`: No further seizures have occurred since.
- `llm:14250:2` supporting, `frequency_rate`, `recent`, `llm_candidate`: he had 2 seizures, one associated with sleep deprivation

### Row 14282 - `seizure_free_duration_gap`

- Gold label: `multiple per month`
- Gold reference: He came off Levetiracetam on 10 December. In the following week, he had several seizures, one associated with sleep deprivation. No further seizures have occurred since
- Assessment: The patient experienced several seizures in the week following Levetiracetam withdrawal but has had no further seizures since, indicating a recent seizure-free interval. The note describes a deterioration in stability over six weeks with several recent events, but these are contextual and not additive to the current seizure burden assessment.
- Source normalized phrase: `No further seizures have occurred since`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:14282:2` primary, `seizure_free`, `recent`, `llm_candidate`: No further seizures have occurred since.
- `llm:14282:1` supporting, `frequency_rate`, `recent`, `llm_candidate`: In the following week, he had several seizures, one associated with sleep deprivation.
- `det:14282:3` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: Over the past six weeks there has been a notable deterioration in his overall stability, with several recent events

### Row 14284 - `seizure_free_duration_gap`

- Gold label: `2 to 3 per month`
- Gold reference: He came off Levetiracetam on 21-Feb. In the following week, he had two to three seizures, one associated with sleep deprivation. No further seizures have occurred since
- Assessment: The patient had two to three seizures in the week following Levetiracetam discontinuation but has had no further seizures since then. He reports occasional historical cluster patterns triggered by sleep deprivation but currently maintains a strict sleep routine. The current seizure burden is seizure-free with context of recent seizures and historical clusters.
- Source normalized phrase: `No further seizures have occurred since`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:14284:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: No further seizures have occurred since
- `det:14284:2` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: In the following week, he had two to three seizures
- `llm:14284:1` supporting, `last_event_only`, `recent`, `llm_candidate`: No further seizures have occurred since.
- `llm:14284:3` supporting, `unknown_frequency`, `historical`, `llm_candidate`: He reports occasional cluster patterns historically when sleep is curtailed

### Row 14317 - `seizure_free_duration_gap`

- Gold label: `4 per 2 month`
- Gold reference: Lamotrigine was stopped on 4 Apr. Around that period, she had 4 seizures, one following alcohol intake. She has not had any further events since
- Assessment: Patient had 4 seizures around the time of Lamotrigine withdrawal in early April, including one triggered by alcohol intake, but has maintained seizure freedom since early April with improved sleep and stability.
- Source normalized phrase: `has maintained seizure freedom since early April`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:14317:2` primary, `seizure_free`, `recent`, `llm_candidate`: She remains off Lamotrigine following planned withdrawal and has maintained seizure freedom since early April.
- `llm:14317:1` supporting, `frequency_rate`, `historical`, `llm_candidate`: Around that period, she had 4 seizures, one following alcohol intake.

### Row 14332 - `seizure_free_duration_gap`

- Gold label: `5 per 2 month`
- Gold reference: Lamotrigine was stopped on 01-Oct. Around that period, she had five seizures, one following alcohol intake. She has not had any further events since
- Assessment: The patient had a cluster of five seizures around early October, including one after alcohol intake, but has had no further seizures since then. Lamotrigine was stopped on 01-Oct due to side effects. She is currently seizure-free and not on regular anti-seizure medication, with ongoing monitoring and safety precautions in place.
- Source normalized phrase: `She has not had any further events since.`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:14332:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: Around that period, she had five seizures
- `llm:14332:1` supporting, `cluster_frequency`, `recent`, `llm_candidate`: Around that period, she had five seizures, one following alcohol intake.
- `llm:14332:2` primary, `seizure_free`, `recent`, `llm_candidate`: She has not had any further events since.

### Row 14335 - `frequency_operands_gap`

- Gold label: `3 to 4 per 2 month`
- Gold reference: Lamotrigine was stopped on 10 Oct. Around that period, she had three - four seizures, one following alcohol intake. She has not had any further events since
- Assessment: The patient had three to four seizures around the time of lamotrigine discontinuation in October, including one following alcohol intake. Since then, she has been seizure-free for approximately eight weeks on levetiracetam monotherapy, with no witnessed events during scrims. Triggers included sleep loss and alcohol. Current seizure burden is low and stable.
- Source normalized phrase: `three to four seizures around October`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:14335:3` primary, `frequency_rate`, `recent`, `llm_candidate`: Around that period, she had three - four seizures, one following alcohol intake.
- `llm:14335:2` supporting, `last_event_only`, `recent`, `llm_candidate`: Since discontinuation of lamotrigine on 10 Oct and continuation of levetiracetam monotherapy, she remains event-free for approximately eight weeks.

### Row 14383 - `seizure_free_duration_gap`

- Gold label: `3 to 4 per 3 month`
- Gold reference: He withdrew from Clobazam on 13-Jan. At that time, he had 3 - 4 seizures, one precipitated by illness. He has remained stable without seizures since
- Assessment: The patient had 3-4 seizures around the time of Clobazam withdrawal on 13-Jan but has remained stable without seizures since then, indicating a current seizure-free state.
- Source normalized phrase: `seizure-free status since mid-January`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:14383:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: seizure-free status since
- `llm:14383:1` supporting, `frequency_rate`, `historical`, `llm_candidate`: He withdrew from Clobazam on 13-Jan. At that time, he had 3 - 4 seizures, one precipitated by illness.

### Row 14454 - `seizure_free_duration_gap`

- Gold label: `2 per 2 month`
- Gold reference: Topiramate was discontinued on 11 Feb. Soon afterwards, she reported two seizures, one after a stressful day. She has had no seizures since then
- Assessment: The patient experienced two seizures soon after stopping topiramate in February but has had no seizures since then, attributed to improved sleep hygiene and avoiding missed meals. No auras or warning symptoms have been reported since the last events. Safety advice and seizure diary maintenance were discussed.
- Source normalized phrase: `no seizures since`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:14454:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no seizures since
- `det:14454:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no auras or brief warning symptoms reported since
- `det:14454:3` rejected, `frequency_rate`, `unclear`, `deterministic_candidate`: Soon afterwards, she reported two seizures
- `llm:14454:1` primary, `last_event_only`, `recent`, `llm_candidate`: She has had no seizures since then.

### Row 14530 - `frequency_operands_gap`

- Gold label: `2 per 2 month`
- Gold reference: His initial event was in March 2019 in Germany, arising from sleep. He awoke with jerking of the left arm and facial twitching. A second event occurred in Italy the following May 2019, once more during the night, lasting four minutes with similar semiology
- Assessment: The patient has had two nocturnal seizures in March and May 2019 with no further daytime episodes since. He is currently on Levetiracetam and has not required rescue medication. Sleep hygiene and workplace adjustments are in place.
- Source normalized phrase: `Two seizures occurred in March and May 2019, both nocturnal`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:14530:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: His initial event was in March 2019 in Germany, arising from sleep. He awoke with jerking of the left arm and facial twitching. A second event occurred in Italy the following May 2019
- `llm:14530:1` rejected, `last_event_only`, `historical`, `llm_candidate`: His initial event was in March 2019 in Germany, arising from sleep. He awoke with jerking of the left arm and facial twitching. A second event occurred in Italy the following May 2019, once more during the night, lasting four minutes with s
- `llm:14530:2` supporting, `last_event_only`, `recent`, `llm_candidate`: There have been no further daytime episodes

### Row 14540 - `seizure_free_duration_gap`

- Gold label: `2 per 8 month`
- Gold reference: His first seizure occurred in December 2017 in Ireland, at night while asleep. He woke with rhythmic twitching of the right arm and a sense of déjà vu. The second event was in August 2018 in Scotland, also during sleep, lasting five minutes with a similar pattern of symptoms
- Assessment: The patient had two discrete nocturnal seizures in December 2017 and August 2018 but has had no further events since starting Levetiracetam with improved medication adherence.
- Source normalized phrase: `No seizures since starting Levetiracetam`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:14540:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: His first seizure occurred in December 2017 in Ireland, at night while asleep. He woke with rhythmic twitching of the right arm and a sense of déjà vu. The second event was in August 2018
- `llm:14540:1` rejected, `last_event_only`, `historical`, `llm_candidate`: His first seizure occurred in December 2017 in Ireland, at night while asleep.
- `llm:14540:2` supporting, `last_event_only`, `recent`, `llm_candidate`: The second event was in August 2018 in Scotland, also during sleep, lasting five minutes with a similar pattern of symptoms.
- `llm:14540:3` primary, `seizure_free`, `current`, `llm_candidate`: Since commencing Levetiracetam he has not had further events.

### Row 14562 - `seizure_free_duration_gap`

- Gold label: `3 per 6 month`
- Gold reference: She experienced her first seizure in January 2021 while on holiday in Spain. It occurred in the early morning hours. She described sudden stiffness in both legs. Her second and third seizure was in July 2021 back home in France, again during sleep, lasting around three minutes with the same clinical features
- Assessment: The patient experienced three focal seizures between January and July 2021, all nocturnal, with no further seizures reported since July 2021. Current seizure burden is best characterized as seizure-free since last event. Management plan includes monitoring and deferred medication initiation.
- Source normalized phrase: `no further events reported`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:14562:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: no further events reported
- `det:14562:2` rejected, `frequency_rate`, `unclear`, `deterministic_candidate`: her first seizure in January 2021 while on holiday in Spain. It occurred in the early morning hours. She described sudden stiffness in both legs. Her second and third seizure was in July 2021
- `llm:14562:1` supporting, `last_event_only`, `recent`, `llm_candidate`: Since July there have been no further events reported.
- `llm:14562:2` rejected, `frequency_rate`, `historical`, `llm_candidate`: She experienced her first seizure in January 2021 while on holiday in Spain.
- `llm:14562:3` rejected, `frequency_rate`, `historical`, `llm_candidate`: Her second and third seizure was in July 2021 back home in France, again during sleep, lasting around three minutes with the same clinical features.

### Row 14567 - `frequency_operands_gap`

- Gold label: `3 per 3 month`
- Gold reference: She experienced her first seizure in October 2017 while on holiday in Spain. It occurred in the early morning hours. She described sudden stiffness in both legs. Her second and third seizure was in January 2018 back home in France, again during sleep, lasting around three minutes with the same clinical features
- Assessment: The patient has had three seizures from October 2017 to January 2018, with the last two seizures occurring in January 2018. She has not driven since January 2018 due to seizure risk. The seizures occurred during sleep or early morning hours, with no clear triggers identified. Anxiety related to travel is noted as a contextual factor.
- Source normalized phrase: `three seizures over approximately three months`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:14567:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: her first seizure in October 2017 while on holiday in Spain. It occurred in the early morning hours. She described sudden stiffness in both legs. Her second and third seizure was in January 2018
- `llm:14567:1` rejected, `frequency_rate`, `historical`, `llm_candidate`: She experienced her first seizure in October 2017 while on holiday in Spain.
- `llm:14567:2` supporting, `frequency_rate`, `recent`, `llm_candidate`: Her second and third seizure was in January 2018 back home in France, again during sleep, lasting around three minutes with the same clinical features.
- `llm:14567:3` supporting, `last_event_only`, `recent`, `llm_candidate`: She has not driven since January 2018.

### Row 14581 - `seizure_free_duration_gap`

- Gold label: `2 per 3 month`
- Gold reference: His initial event was in July 2014 in Germany, arising from sleep. He awoke with jerking of the left arm and facial twitching. A second event occurred in Italy the following October 2014, once more during the night, lasting four minutes with similar semiology
- Assessment: The patient has had no further seizures since surgical intervention and initiation of Levetiracetam, indicating seizure freedom. Historical events and initial seizures are noted but are not current. No recurrence of nocturnal motor events and steady functional recovery observed.
- Source normalized phrase: `No further seizures since surgery and initiation of Levetiracetam.`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:14581:3` primary, `seizure_free`, `recent`, `llm_candidate`: He has had no further events since surgical intervention and initiation of Levetiracetam.
- `det:14581:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no recurrence
- `det:14581:3` rejected, `frequency_rate`, `unclear`, `deterministic_candidate`: His initial event was in July 2014 in Germany, arising from sleep. He awoke with jerking of the left arm and facial twitching. A second event occurred in Italy the following October 2014
- `llm:14581:1` rejected, `last_event_only`, `historical`, `llm_candidate`: His initial event was in July 2014 in Germany, arising from sleep.
- `llm:14581:2` rejected, `last_event_only`, `historical`, `llm_candidate`: A second event occurred in Italy the following October 2014, once more during the night, lasting four minutes with similar semiology.

### Row 14587 - `frequency_operands_gap`

- Gold label: `2 per 3 month`
- Gold reference: She experienced her first seizure in April 2018 while on holiday in Spain. It occurred in the early morning hours. She described sudden stiffness in both legs. Her second seizure was in July 2018 back home in France, again during sleep, lasting around three minutes with the same clinical features
- Assessment: The patient experienced two nocturnal seizures within three months characterized by bilateral leg stiffness and brief post-event fatigue. Classification remains uncertain pending EEG and MRI results. No convulsive features or prolonged postictal confusion reported. Diabetes is managed separately in primary care.
- Source normalized phrase: `Two nocturnal seizures within three months`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:14587:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: her first seizure in April 2018 while on holiday in Spain. It occurred in the early morning hours. She described sudden stiffness in both legs. Her second seizure was in July 2018
- `llm:14587:1` primary, `frequency_rate`, `recent`, `llm_candidate`: Two nocturnal events within three months featuring bilateral leg stiffness and brief post-event fatigue; classification remains uncertain pending EEG/MRI.

### Row 14592 - `frequency_operands_gap`

- Gold label: `3 per 5 month`
- Gold reference: His first seizure occurred in January 2024 in Ireland, at night while asleep. He woke with rhythmic twitching of the right arm and a sense of déjà vu. The second and third event was in June 2024 in Scotland, also during sleep, lasting five minutes with a similar pattern of symptoms
- Assessment: The patient has had two seizures in June 2024 during sleep, with a first seizure in January 2024; historical myoclonic jerks and a probable adolescent tonic-clonic seizure are noted but not current. The patient is not yet on anti-seizure medication and is planning treatment and safety measures. Triggers include sleep deprivation and alcohol.
- Source normalized phrase: `Two seizures in June 2024 during sleep`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:14592:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: His first seizure occurred in January 2024 in Ireland, at night while asleep. He woke with rhythmic twitching of the right arm and a sense of déjà vu. The second and third event was in June 2024
- `llm:14592:2` primary, `frequency_rate`, `recent`, `llm_candidate`: The second and third event was in June 2024 in Scotland, also during sleep, lasting five minutes with a similar pattern of symptoms.
- `llm:14592:3` rejected, `frequency_rate`, `historical`, `llm_candidate`: He also reports two lifetime episodes (both in 2023) of brief generalised myoclonic jerks on awakening after sleep deprivation, without loss of awareness, and one episode of probable generalised tonic–clonic seizure in adolescence after hea
- `llm:14592:4` rejected, `last_event_only`, `historical`, `llm_candidate`: He also reports two lifetime episodes (both in 2023) of brief generalised myoclonic jerks on awakening after sleep deprivation, without loss of awareness, and one episode of probable generalised tonic–clonic seizure in adolescence after hea

### Row 14611 - `seizure_free_duration_gap`

- Gold label: `2 per 4 month`
- Gold reference: His initial event was in January 2020 in Germany, arising from sleep. He awoke with jerking of the left arm and facial twitching. A second event occurred in Italy the following May 2020, once more during the night, lasting four minutes with similar semiology
- Assessment: The patient experienced two nocturnal seizures in January and May 2020 with no recurrence since May 2020. No daytime events or auras reported. Current seizure burden is seizure-free state with no antiseizure medication started. Ongoing monitoring and investigations planned.
- Source normalized phrase: `no further episodes since May 2020`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:14611:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: no further episodes since
- `det:14611:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no episodes of aura, twitching, or nocturnal confusion since
- `det:14611:3` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no recurrence
- `det:14611:4` rejected, `frequency_rate`, `unclear`, `deterministic_candidate`: His initial event was in January 2020 in Germany, arising from sleep. He awoke with jerking of the left arm and facial twitching. A second event occurred in Italy the following May 2020
- `llm:14611:1` supporting, `last_event_only`, `recent`, `llm_candidate`: There have been no further episodes since the second event.
- `llm:14611:2` rejected, `frequency_rate`, `historical`, `llm_candidate`: His initial event was in January 2020 in Germany, arising from sleep. A second event occurred in Italy the following May 2020, once more during the night, lasting four minutes with similar semiology.

### Row 14635 - `seizure_free_duration_gap`

- Gold label: `5 per 4 month`
- Gold reference: She first experienced a seizure in July 2016 while living in Australia. It occurred during sleep, with sudden jerks of the left leg. Her next 4 seizure came in November 2016 the same year in New Zealand, once more from sleep, lasting three minutes and showing the same semiology
- Assessment: Patient with generalised epilepsy has had no seizures since starting sodium valproate and clobazam at the end of November, showing marked clinical improvement compared to prior events in July and November 2016.
- Source normalized phrase: `no further seizures since starting current regimen at end of November`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:14635:3` primary, `seizure_free`, `recent`, `llm_candidate`: Since commencing the current regimen at the end of November, there have been no further events reported by the patient or her partner
- `det:14635:2` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: She first experienced a seizure in July 2016 while living in Australia. It occurred during sleep, with sudden jerks of the left leg. Her next 4 seizure came in November 2016
- `llm:14635:1` supporting, `last_event_only`, `historical`, `llm_candidate`: She first experienced a seizure in July 2016 while living in Australia.
- `llm:14635:2` supporting, `last_event_only`, `historical`, `llm_candidate`: Her next 4 seizure came in November 2016 the same year in New Zealand, once more from sleep, lasting three minutes and showing the same semiology.

### Row 14645 - `seizure_free_duration_gap`

- Gold label: `2 per 6 month`
- Gold reference: His first seizure occurred in May 2018 in Ireland, at night while asleep. He woke with rhythmic twitching of the right arm and a sense of déjà vu. The second event was in November 2018 in Scotland, also during sleep, lasting five minutes with a similar pattern of symptoms
- Assessment: The patient had two seizures in 2018 but reports no further seizures since November 2018 with good medication adherence and improved lifestyle. This indicates a current seizure-free state.
- Source normalized phrase: `no further events recorded to date`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:14645:3` primary, `seizure_free`, `current`, `llm_candidate`: no further events recorded to date
- `det:14645:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no additional seizures since
- `det:14645:3` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: His first seizure occurred in May 2018 in Ireland, at night while asleep. He woke with rhythmic twitching of the right arm and a sense of déjà vu. The second event was in November 2018
- `llm:14645:1` rejected, `last_event_only`, `historical`, `llm_candidate`: His first seizure occurred in May 2018 in Ireland, at night while asleep.
- `llm:14645:2` rejected, `last_event_only`, `historical`, `llm_candidate`: The second event was in November 2018 in Scotland, also during sleep, lasting five minutes with a similar pattern of symptoms.

### Row 14672 - `seizure_free_duration_gap`

- Gold label: `3 per 8 month`
- Gold reference: The first seizure was reported in March 2017 while visiting relatives in Canada. It happened during an afternoon nap, with an unusual tingling spreading from the right hand to the shoulder. The second and third event took place in November 2017 in the USA, again from sleep, lasting approximately five minutes, with comparable symptoms
- Assessment: The patient has had no seizures since starting her current medication regimen, indicating a marked improvement and seizure freedom currently. Historical seizures in 2017 are noted but are not part of the current burden assessment.
- Source normalized phrase: `There have been no further episodes since starting her current regimen`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:14672:3` primary, `seizure_free`, `recent`, `llm_candidate`: There have been no further episodes since starting her current regimen
- `det:14672:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no recent seizures reported
- `det:14672:3` rejected, `frequency_rate`, `unclear`, `deterministic_candidate`: The first seizure was reported in March 2017 while visiting relatives in Canada. It happened during an afternoon nap, with an unusual tingling spreading from the right hand to the shoulder. The second and third event took place in November
- `llm:14672:1` rejected, `last_event_only`, `historical`, `llm_candidate`: The first seizure was reported in March 2017 while visiting relatives in Canada.
- `llm:14672:2` rejected, `last_event_only`, `historical`, `llm_candidate`: The second and third event took place in November 2017 in the USA, again from sleep, lasting approximately five minutes, with comparable symptoms.

### Row 14765 - `frequency_operands_gap`

- Gold label: `1 per month`
- Gold reference: He experienced several brief dizzy spells followed by headaches, but these settled with treatment. On 25/Jan his absences improved after medication adjustment. His last event was on 30/Jan and he has remained well since. Given that there have been no further episodes in the past month and his epilepsy is otherwise stable, I do not think additional intervention is required at present
- Assessment: The patient has had no seizures in the past month, with the last event on 30/Jan. Previous brief dizzy spells and headaches have settled with treatment. Overall, the epilepsy is stable with improved symptom control and no additional intervention required at present.
- Source normalized phrase: `no seizures in the past month`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:14765:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: His last event was on 30/Jan
- `llm:14765:1` supporting, `unknown_frequency`, `historical`, `llm_candidate`: He experienced several brief dizzy spells followed by headaches, but these settled with treatment.
- `llm:14765:2` supporting, `last_event_only`, `recent`, `llm_candidate`: His last event was on 30/Jan and he has remained well since.
- `llm:14765:3` primary, `frequency_rate`, `recent`, `llm_candidate`: Given that there have been no further episodes in the past month and his epilepsy is otherwise stable, I do not think additional intervention is required at present.

### Row 14806 - `seizure_free_duration_gap`

- Gold label: `1 per 2 month`
- Gold reference: He experienced several brief dizzy spells followed by headaches, but these settled with treatment. On 28/Apr his absences improved after medication adjustment. His last event was on 03/May and he has remained well since. Given that there have been no further episodes in the past month and his epilepsy is otherwise stable, I do not think additional intervention is required at present
- Assessment: The patient has remained seizure-free for the past month since the last event on 03/May, with recent brief aura-like events resolved and improved absences after medication adjustment. No additional intervention is currently required.
- Source normalized phrase: `no further episodes in the past month`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:14806:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: His last event was on 03/May
- `llm:14806:2` rejected, `frequency_rate`, `recent`, `llm_candidate`: several brief dizzy spells followed by headaches
- `llm:14806:3` rejected, `frequency_rate`, `recent`, `llm_candidate`: On 28/Apr his absences improved after medication adjustment
- `llm:14806:4` supporting, `last_event_only`, `recent`, `llm_candidate`: His last event was on 03/May
- `llm:14806:5` supporting, `seizure_free`, `recent`, `llm_candidate`: he has remained well since
- `llm:14806:6` primary, `seizure_free`, `recent`, `llm_candidate`: no further episodes in the past month

### Row 14810 - `seizure_free_duration_gap`

- Gold label: `1 per month`
- Gold reference: She had recurrent headaches following her seizures earlier this month, but these have now settled. On 12 May the absence episodes reduced significantly after she restarted Lamotrigine. Her last reported event was on 19 May and she has been seizure-free since. As she has now been stable for over 4 weeks, I am reassured and see no need for urgent changes
- Assessment: The patient has been seizure-free since 19 May, maintaining good medication adherence and stability for over 4 weeks. Previous absence episodes earlier this month have settled after restarting Lamotrigine. No urgent changes are needed at this time.
- Source normalized phrase: `seizure-free for over 4 weeks`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:14810:1` primary, `seizure_free`, `recent`, `llm_candidate`: she has been seizure-free since
- `det:14810:2` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: this month, but these have now settled. On 12 May the absence episodes

### Row 14821 - `seizure_free_duration_gap`

- Gold label: `1 per month`
- Gold reference: She had recurrent headaches following her seizures earlier this month, but these have now settled. On 17 Jul the absence episodes reduced significantly after she restarted Lamotrigine. Her last reported event was on 24 Jul and she has been seizure-free since. As she has now been stable for over 3 weeks, I am reassured and see no need for urgent changes
- Assessment: Patient has been seizure-free since 24 July following Lamotrigine restart, with resolution of postictal headaches. No urgent changes needed; routine follow-up planned in 3 months.
- Source normalized phrase: `seizure-free since 24 Jul`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:14821:1` primary, `seizure_free`, `recent`, `llm_candidate`: she has been seizure-free since
- `det:14821:2` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: seizure freedom since
- `det:14821:3` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: this month, but these have now settled. On 17 Jul the absence episodes

### Row 14872 - `seizure_free_duration_gap`

- Gold label: `1 per month`
- Gold reference: Following two episodes of dizziness and subsequent headaches, his symptoms improved with supportive care. On 09/May the absences diminished after dose escalation. His last episode was recorded on 17/May and he has remained well since. Considering that he has now been free of seizures for two weeks and his overall condition is stable, no immediate action is necessary
- Assessment: The patient has been seizure-free for two weeks following dose escalation on 09/May. His last seizure was recorded on 17/May. He remains stable with no new neurological findings. Workplace adjustments and medication adherence are maintained. Routine follow-up planned in three months.
- Source normalized phrase: `free of seizures for two weeks`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:14872:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: His last episode was recorded on 17/May
- `llm:14872:1` primary, `seizure_free`, `recent`, `llm_candidate`: Considering that he has now been free of seizures for two weeks and his overall condition is stable, no immediate action is necessary.
- `llm:14872:2` supporting, `last_event_only`, `recent`, `llm_candidate`: His last episode was recorded on 17/May and he has remained well since.

### Row 14943 - `seizure_free_duration_gap`

- Gold label: `1 per 3 month`
- Gold reference: She presented with dizziness and headaches on consecutive days, but these resolved spontaneously. On 15 Feb, following the use of her prescribed medication, the absences became less frequent. The last such episode occurred on 21 Feb and she has been stable since. Given her stability now, I do not propose further intervention for now
- Assessment: The patient experienced intermittent brief behavioural arrests over the past two months, which became less frequent after 15 Feb following medication adjustment. The last episode occurred on 21 Feb, and she has been stable since then with no further seizures reported. Current management includes continuation of medication and monitoring. No new interventions are proposed at this time.
- Source normalized phrase: `stable since 21 Feb with no recent seizures`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:14943:1` supporting, `frequency_rate`, `recent`, `llm_candidate`: The carer reports that over the past two months there have been intermittent brief behavioural arrests noted mainly in the late afternoon, occasionally with loss of thread of conversation and a short pause in activity.
- `llm:14943:2` supporting, `frequency_rate`, `recent`, `llm_candidate`: On 15 Feb, following the use of her prescribed medication, the absences became less frequent.
- `llm:14943:3` supporting, `last_event_only`, `recent`, `llm_candidate`: The last such episode occurred on 21 Feb and she has been stable since.
- `llm:14943:4` primary, `seizure_free`, `recent`, `llm_candidate`: The last such episode occurred on 21 Feb and she has been stable since.

### Row 14965 - `frequency_operands_gap`

- Gold label: `1 per 3 month`
- Gold reference: She presented with dizziness and headaches on consecutive days, but these resolved spontaneously. On 14/May, following the use of her prescribed medication, the absences became less frequent. The last such episode occurred on 20/May and she has been stable since. Given her stability now, I do not propose further intervention for now
- Assessment: The patient has been stable with no seizures since the last focal aware episode on 20 May. Current seizure burden is minimal with no loss of awareness events reported recently. Occupational exposure to strobe lights is managed with workplace measures.
- Source normalized phrase: `last seizure episode on 20 May, stable since`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:14965:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: last such episode occurred on 20/May
- `llm:14965:1` primary, `last_event_only`, `recent`, `llm_candidate`: The last such episode occurred on 20/May and she has been stable since.

### Row 14973 - `seizure_free_duration_gap`

- Gold label: `1 per month`
- Gold reference: She presented with dizziness and headaches on consecutive days, but these resolved spontaneously. On 31 January, following the use of her prescribed medication, the absences became less frequent. The last such episode occurred on 06 February and she has been stable since. Given her stability now, I do not propose further intervention for now
- Assessment: The patient has been stable with no further absences since early February following medication adjustment and workplace safety measures. No nocturnal or convulsive events reported. Ongoing monitoring and safety precautions are in place.
- Source normalized phrase: `no further absences since early February`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:14973:1` primary, `seizure_free`, `unclear`, `deterministic_candidate`: no further absences since
- `det:14973:2` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: last such episode occurred on 06 February
- `llm:14973:1` supporting, `frequency_rate`, `recent`, `llm_candidate`: On 31 January, following the use of her prescribed medication, the absences became less frequent.
- `llm:14973:2` supporting, `last_event_only`, `recent`, `llm_candidate`: The last such episode occurred on 06 February and she has been stable since.
- `llm:14973:3` supporting, `seizure_free`, `recent`, `llm_candidate`: The last such episode occurred on 06 February and she has been stable since.

### Row 15004 - `seizure_free_duration_gap`

- Gold label: `1 per 3 month`
- Gold reference: After experiencing dizziness and headache on two occasions, his symptoms improved without complications. On 15 October his absences settled with treatment. The most recent episode was on 23 October, and since then he has been well. With no recurrence for the past months and overall stable epilepsy, no additional management is indicated at this stage
- Assessment: The patient has had no seizure recurrence for the past months since the last episode on 23 October, indicating stable epilepsy and no current seizures. Continued adherence to medication and lifestyle measures is maintained.
- Source normalized phrase: `no recurrence for the past months`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:15004:2` primary, `seizure_free`, `recent`, `llm_candidate`: no recurrence for the past months
- `det:15004:2` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: The most recent episode was on 23 October
- `llm:15004:1` supporting, `last_event_only`, `recent`, `llm_candidate`: The most recent episode was on 23 October

### Row 15012 - `seizure_free_duration_gap`

- Gold label: `1 per 2 month`
- Gold reference: After experiencing dizziness and headache on two occasions, his symptoms improved without complications. On 23-May his absences settled with treatment. The most recent episode was on 31-May, and since then he has been well. With no recurrence for the past months and overall stable epilepsy, no additional management is indicated at this stage
- Assessment: The patient has been seizure-free since the most recent episode on 31-May, with no recurrence and stable epilepsy. Current management is unchanged with good adherence and no recent events.
- Source normalized phrase: `no recurrence of seizures since 31-May`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:15012:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: seizure‑free requirements are met. - Routine follow‑up in 6 months
- `det:15012:2` primary, `seizure_free`, `unclear`, `deterministic_candidate`: no recurrence
- `det:15012:3` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: The most recent episode was on 31-May
- `llm:15012:1` supporting, `last_event_only`, `recent`, `llm_candidate`: The most recent episode was on 31-May

### Row 15029 - `seizure_free_duration_gap`

- Gold label: `1 per 3 month`
- Gold reference: After experiencing dizziness and headache on two occasions, his symptoms improved without complications. On 07-Mar his absences settled with treatment. The most recent episode was on 15-Mar, and since then he has been well. With no recurrence for the past months and overall stable epilepsy, no additional management is indicated at this stage
- Assessment: The patient has been seizure-free for the past months with overall stable epilepsy. The most recent seizure was on 15-Mar, and since then he has been well. No additional management is indicated at this stage. Continued use of seizure diary app and routine follow-up planned.
- Source normalized phrase: `no recurrence for the past months and overall stable epilepsy`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:15029:1` primary, `seizure_free`, `recent`, `llm_candidate`: With no recurrence for the past months and overall stable epilepsy, no additional management is indicated at this stage.
- `det:15029:2` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: The most recent episode was on 15-Mar
- `llm:15029:2` supporting, `last_event_only`, `recent`, `llm_candidate`: The most recent episode was on 15-Mar, and since then he has been well.

### Row 15094 - `frequency_operands_gap`

- Gold label: `4 per 13 month`
- Gold reference: Last tonic-clonic seizure was in Apr/2022, with 3 morning jerks since then
- Assessment: Patient has had no tonic-clonic seizures since April 2022 and reports 3 brief morning myoclonus jerks without loss of awareness or injury. No absences reported. Psychological support and sleep hygiene improvements have contributed to better control and coping. No medication changes indicated at this time.
- Source normalized phrase: `3 morning jerks since last tonic-clonic seizure in Apr 2022`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:15094:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no absences reported
- `det:15094:2` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: Last tonic-clonic seizure was in Apr/2022, with 3 morning jerks since then
- `llm:15094:1` rejected, `last_event_only`, `historical`, `llm_candidate`: Last tonic-clonic seizure was in Apr/2022
- `llm:15094:2` supporting, `frequency_rate`, `recent`, `llm_candidate`: Last tonic-clonic seizure was in Apr/2022, with 3 morning jerks since then.

### Row 15108 - `frequency_operands_gap`

- Gold label: `3 to 4 per 15 month`
- Gold reference: Last tonic-clonic seizure was in 1 - 2024, with 2 to 3 morning jerks since then
- Assessment: The patient has been seizure-free from convulsive seizures for over 12 months, with 2 to 3 brief morning jerks since the last tonic-clonic seizure in January 2024. The jerks are brief, occur on waking, and have not progressed to loss of awareness or injury. Historical last tonic-clonic seizure in January 2024 is noted but not primary for current burden. The current regimen is stable with no recent convulsive seizures.
- Source normalized phrase: `2 to 3 morning jerks since last tonic-clonic seizure in January 2024`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:15108:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: Last tonic-clonic seizure was in 1 - 2024, with 2 to 3 morning jerks since then
- `llm:15108:1` rejected, `last_event_only`, `historical`, `llm_candidate`: Last tonic-clonic seizure was in 1 - 2024
- `llm:15108:2` supporting, `frequency_rate`, `recent`, `llm_candidate`: Last tonic-clonic seizure was in 1 - 2024, with 2 to 3 morning jerks since then.
- `llm:15108:3` supporting, `last_event_only`, `historical`, `llm_candidate`: No driving issues were raised today, and there has been no convulsive seizure for over 12 months

### Row 15127 - `frequency_operands_gap`

- Gold label: `5 per 13 month`
- Gold reference: Last tonic-clonic seizure was in 2 - 2020, with 4 morning jerks since then
- Assessment: Last tonic-clonic seizure was in February 2020. Since then, the patient has had 4 brief morning jerks without loss of awareness or injury, occurring shortly after waking. Medication adherence is good, and no recent emergency presentations or adverse effects reported. Collateral history pending to further clarify seizure pattern.
- Source normalized phrase: `4 morning jerks since last tonic-clonic seizure in Feb 2020`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:15127:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: Last tonic-clonic seizure was in 2 - 2020, with 4 morning jerks since then
- `llm:15127:1` supporting, `last_event_only`, `historical`, `llm_candidate`: Last tonic-clonic seizure was in 2 - 2020
- `llm:15127:2` supporting, `frequency_rate`, `recent`, `llm_candidate`: 4 morning jerks since then

### Row 15129 - `frequency_operands_gap`

- Gold label: `4 per 15 month`
- Gold reference: Last tonic-clonic seizure was in 3/2015, with four morning jerks since then
- Assessment: The patient reports no generalised tonic-clonic seizures since March 2015, with only four brief morning jerks since then as per diary. No recent loss of awareness or injury. This indicates a low current seizure frequency burden with improved control compared to prior events.
- Source normalized phrase: `four brief morning jerks since 3/2015`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:15129:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: last clearly witnessed tonic–clonic seizure was in 3/2015, with four morning jerks since then
- `llm:15129:1` supporting, `last_event_only`, `historical`, `llm_candidate`: the last clearly witnessed tonic–clonic seizure was in 3/2015
- `llm:15129:2` primary, `frequency_rate`, `recent`, `llm_candidate`: only four brief morning jerks since 3/2015 as per diary

### Row 15193 - `seizure_free_duration_gap`

- Gold label: `multiple per 13 month`
- Gold reference: He has had no generalised seizures since 9 - 2022, though continues to experience brief absence from time to time
- Assessment: The patient has been free of generalised seizures since September 2022, with only occasional brief absence episodes that do not meet criteria for generalised seizures. This indicates good seizure control and improvement over the past year.
- Source normalized phrase: `no generalised seizures since 9 - 2022`
- Projection issues: `vague_count, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `llm:15193:1` primary, `seizure_free`, `recent`, `llm_candidate`: He has had no generalised seizures since 9 - 2022
- `llm:15193:2` supporting, `unknown_frequency`, `current`, `llm_candidate`: though continues to experience brief absence from time to time

### Row 15242 - `cluster_axis_gap`

- Gold label: `multiple cluster per 15 month, multiple per cluster`
- Gold reference: Her last convulsive seizure was recorded in 03/2022, with occasional clusters of myoclonic jerks persisting
- Assessment: The patient currently experiences occasional clusters of myoclonic jerks as the primary seizure burden. The last convulsive seizure was in March 2022 and is considered historical. Intermittent brief morning jerks and transient lapses in awareness are also reported but are less specific. No recent convulsive seizures or emergency attendances have occurred.
- Source normalized phrase: `occasional clusters of myoclonic jerks persisting`
- Projection issues: `cluster_frequency_operands_unparsed, cluster_cadence_operands_incomplete`
- Route families: `cluster_axis_ambiguity`

Candidate evidence:

- `det:15242:1` supporting, `cluster_frequency`, `unclear`, `deterministic_candidate`: Her last convulsive seizure was recorded in 03/2022, with occasional clusters of myoclonic jerks persisting
- `llm:15242:1` supporting, `last_event_only`, `historical`, `llm_candidate`: Her last convulsive seizure was recorded in 03/2022
- `llm:15242:2` primary, `cluster_frequency`, `current`, `llm_candidate`: occasional clusters of myoclonic jerks persisting
- `llm:15242:3` supporting, `unknown_frequency`, `current`, `llm_candidate`: She describes intermittent brief morning jerks and occasional transient lapses in awareness

### Row 15262 - `cluster_axis_gap`

- Gold label: `multiple cluster per 13 month, multiple per cluster`
- Gold reference: Her last convulsive seizure was recorded in June 2018, with occasional clusters of myoclonic jerks persisting
- Assessment: The patient has not had convulsive seizures since June 2018 but continues to experience occasional clusters of myoclonic jerks. There is a noted deterioration in event threshold and speed of onset in visually and acoustically stimulating environments, with longer post-event disorientation. Monitoring and environmental adjustments are planned.
- Source normalized phrase: `occasional clusters of myoclonic jerks persisting`
- Projection issues: `cluster_frequency_operands_unparsed, cluster_cadence_operands_incomplete`
- Route families: `cluster_axis_ambiguity`

Candidate evidence:

- `det:15262:1` primary, `cluster_frequency`, `unclear`, `deterministic_candidate`: Her last convulsive seizure was recorded in June 2018, with occasional clusters of myoclonic jerks persisting
- `llm:15262:1` supporting, `last_event_only`, `historical`, `llm_candidate`: Her last convulsive seizure was recorded in June 2018

### Row 15267 - `seizure_free_duration_gap`

- Gold label: `3 per 14 month`
- Gold reference: No further tonic-clonic seizures have occurred since 06/2017, although three single jerks remain
- Assessment: The patient has been free of tonic-clonic seizures since June 2017, indicating a stable and improving seizure disorder. Three brief myoclonic jerks remain without loss of awareness or other seizure features, occurring during sleep restriction earlier in the year. No injuries or other seizure-related complications reported. Sleep consolidation and night-time support have contributed to improved stability.
- Source normalized phrase: `No further tonic-clonic seizures have occurred since 06/2017`
- Projection issues: `seizure_free_duration_unparsed, seizure_free_duration_required`
- Route families: ``

Candidate evidence:

- `det:15267:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no qualifying events since
- `det:15267:2` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: No further tonic-clonic seizures have occurred since 06/2017, although three single jerks remain
- `llm:15267:1` primary, `seizure_free`, `recent`, `llm_candidate`: No further tonic-clonic seizures have occurred since 06/2017

### Row 15317 - `frequency_operands_gap`

- Gold label: `2 to 3 per 15 month`
- Gold reference: No further tonic-clonic seizures have occurred since Jan-2015, although 2 to 3 single jerks remain
- Assessment: The patient has been free of tonic-clonic seizures since January 2015, with 2 to 3 infrequent myoclonic jerks remaining. No absences have been reported since late 2015. Overall, seizure control is improved with good medication adherence and reduced stress.
- Source normalized phrase: `2 to 3 single jerks remain`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:15317:3` supporting, `seizure_free`, `recent`, `llm_candidate`: There have been no absences reported by the patient or observed by family since late 2015
- `det:15317:3` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: No further tonic-clonic seizures have occurred since Jan-2015, although 2 to 3 single jerks remain
- `llm:15317:1` supporting, `seizure_free`, `recent`, `llm_candidate`: No further tonic-clonic seizures have occurred since Jan-2015
- `llm:15317:2` supporting, `unknown_frequency`, `current`, `llm_candidate`: 2 to 3 single jerks remain

### Row 15964 - `frequency_operands_gap`

- Gold label: `11 per 3 month`
- Gold reference: In March he had 3 in sleep and 2 while awake. In May he had 3 in sleep and 3 while awake
- Assessment: The patient experienced 6 seizures in May, with 3 occurring during sleep and 3 while awake. No significant clustering pattern was identified beyond nocturnal events. The frequency is consistent with the recent diary entries. No changes to antiseizure medication were made. Continued monitoring and safety precautions advised.
- Source normalized phrase: `3 seizures in sleep and 3 while awake in May`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:15964:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: In March he had 3 in sleep and 2 while awake. In May he had 3 in sleep and 3 while awake
- `llm:15964:2` primary, `frequency_rate`, `recent`, `llm_candidate`: In May he had 3 in sleep and 3 while awake.

### Row 15966 - `frequency_operands_gap`

- Gold label: `5 per 3 month`
- Gold reference: In October he had two seizures during sleep and none while awake. In December he had three in sleep and no while awake
- Assessment: The patient had a total of five seizures during sleep over the past two months (October and December) with no seizures while awake. The patient reports improvement with light and screen management strategies and better daytime functioning. No injuries or prolonged post-ictal states were noted. Current medication remains unchanged.
- Source normalized phrase: `5 seizures during sleep over 2 months`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:15966:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: In October he had two seizures during sleep and none while awake. In December he had three in sleep and no while awake
- `llm:15966:2` supporting, `frequency_rate`, `recent`, `llm_candidate`: In December he had three in sleep and no while awake.

### Row 15982 - `frequency_operands_gap`

- Gold label: `9 per 2 month`
- Gold reference: In Jun he had a nocturnal seizure but no daytime events. In July he had three nocturnal seizures and 5 while awake
- Assessment: The patient had 8 seizures in July, including 3 nocturnal and 5 while awake. In June, there was 1 nocturnal seizure but no daytime events. Frequent shift changes and sleep disruption are noted as triggers. No rescue medication used and no injuries reported. Continued monitoring and sleep hygiene plan in place.
- Source normalized phrase: `8 seizures in July, including 3 nocturnal and 5 while awake`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:15982:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: In Jun he had a nocturnal seizure but no daytime events. In July he had three nocturnal seizures and 5 while awake
- `llm:15982:1` supporting, `last_event_only`, `recent`, `llm_candidate`: In Jun he had a nocturnal seizure but no daytime events.
- `llm:15982:2` rejected, `frequency_rate`, `recent`, `llm_candidate`: In July he had three nocturnal seizures and 5 while awake.
- `llm:15982:3` supporting, `unknown_frequency`, `recent`, `llm_candidate`: He works rotating shifts, including nights, and both he and his partner report that his circadian rhythm has been disrupted for several months due to frequent changes in start times.

### Row 15986 - `frequency_operands_gap`

- Gold label: `11 per 3 month`
- Gold reference: In Mar she had five seizures during sleep and 5 while awake. In May she had no in sleep and one while awake
- Assessment: The patient experienced a post-partum deterioration with increased seizures in March (five nocturnal and five awake), but May shows improvement with only one awake seizure and no nocturnal seizures. The current burden is best represented by the May frequency. Lamotrigine dose is being increased to address breakthrough seizures, with mood and sleep factors also considered.
- Source normalized phrase: `In May she had no seizures during sleep and one while awake`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:15986:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: In Mar she had five seizures during sleep and 5 while awake. In May she had no in sleep and one while awake
- `det:15986:2` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: every 5–7 days
- `llm:15986:2` primary, `frequency_rate`, `recent`, `llm_candidate`: In May she had no in sleep and one while awake.

### Row 15992 - `frequency_operands_gap`

- Gold label: `7 per 2 month`
- Gold reference: In Dec he had no nocturnal seizures but four daytime events. In Jan he had no nocturnal seizures and 3 while awake
- Assessment: Patient reports 3 to 4 daytime seizures per month with no nocturnal seizures, typically brief episodes of behavioral arrest with impaired awareness. Sleep fragmentation may contribute to seizure threshold; medication adherence emphasized. No emergency presentations or rescue medication use.
- Source normalized phrase: `3 to 4 daytime seizures per month, no nocturnal seizures`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:15992:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: In Dec he had no nocturnal seizures but four daytime events. In Jan he had no nocturnal seizures and 3 while awake

### Row 15997 - `frequency_operands_gap`

- Gold label: `10 per 3 month`
- Gold reference: In Nov he had 3 seizures during sleep and 1 while awake. In Jan he had five in sleep and one while awake
- Assessment: The patient had six seizures in January, including five nocturnal and one daytime event. Seizures tend to cluster after multiple consecutive nights of less than 4 hours of continuous sleep, which is a contextual factor but not additive to the primary frequency assessment.
- Source normalized phrase: `Six seizures in January, including five nocturnal and one daytime`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:15997:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: In Nov he had 3 seizures during sleep and 1 while awake. In Jan he had five in sleep and one while awake
- `llm:15997:2` primary, `frequency_rate`, `recent`, `llm_candidate`: In Jan he had five in sleep and one while awake.
- `llm:15997:3` supporting, `cluster_frequency`, `recent`, `llm_candidate`: She notices events cluster after multiple consecutive nights of <4 hours’ continuous sleep.

### Row 16021 - `frequency_operands_gap`

- Gold label: `9 per 3 month`
- Gold reference: In Feb he had 3 in sleep and one while awake. In Apr he had five in sleep and no while awake
- Assessment: The patient had five seizures during sleep and none while awake in April, consistent across patient diary and assisted-living incident forms. No injuries or prolonged confusion reported. The seizure pattern is variable month-to-month with nocturnal predominance. Lamotrigine dose is stable with no missed doses. Monitoring and structured logging will continue.
- Source normalized phrase: `five seizures in sleep in April, none while awake`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:16021:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: In Feb he had 3 in sleep and one while awake. In Apr he had five in sleep and no while awake
- `llm:16021:2` primary, `frequency_rate`, `recent`, `llm_candidate`: In Apr he had five in sleep and no while awake.

### Row 16084 - `frequency_operands_gap`

- Gold label: `8 per 4 month`
- Gold reference: She has had no seizures so far this month, four in August, one in July and 3 in June, with events reported from both daytime and nocturnal periods
- Assessment: The patient has had no seizures so far this month, with prior months showing 4 seizures in August, 1 in July, and 3 in June. Seizures occur during both daytime and nocturnal periods. The current seizure burden is best represented by the seizure-free status this month, indicating improvement. The candidate indicating no seizures recorded is historical and less specific, thus rejected.
- Source normalized phrase: `no seizures so far this month`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:16084:1` rejected, `seizure_free`, `unclear`, `deterministic_candidate`: no seizures recorded
- `det:16084:2` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: She has had no seizures so far this month, four in August, one in July and 3 in June
- `llm:16084:5` supporting, `unknown_frequency`, `recent`, `llm_candidate`: events reported from both daytime and nocturnal periods

### Row 16133 - `frequency_operands_gap`

- Gold label: `18 per 4 month`
- Gold reference: He reports 6 seizure events in September, 6 in August and four in July, and 2 in June, from both daytime and nocturnal periods
- Assessment: Patient reports 6 seizures in September from both daytime and nocturnal periods, with clustering noted around sleep deprivation and stress but no changes in VNS settings or medication. No emergency attendances since May and no new injuries reported.
- Source normalized phrase: `6 seizure events in September`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:16133:1` primary, `frequency_rate`, `recent`, `llm_candidate`: He reports 6 seizure events in September, 6 in August and four in July, and 2 in June, from both daytime and nocturnal periods.

### Row 16195 - `frequency_operands_gap`

- Gold label: `16 per 4 month`
- Gold reference: She has had 6 seizures so far this month, 2 in August, five in July and 3 in June, with events reported from both daytime and nocturnal periods
- Assessment: The patient has had 6 seizures this month, indicating a recent increase in seizure frequency compared to previous months. No injuries reported and adherence to medication is good. Safety advice and monitoring continue.
- Source normalized phrase: `6 seizures so far this month`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `llm:16195:4` primary, `frequency_rate`, `recent`, `llm_candidate`: She has had 6 seizures so far this month, 2 in August, five in July and 3 in June

### Row 16220 - `frequency_operands_gap`

- Gold label: `11 per 4 month`
- Gold reference: This month so far she has no seizures; earlier 4 in February, 0 in January and 7 in December, over waking hours and sleep
- Assessment: Patient has focal epilepsy with no seizures reported this month so far, with prior counts of 4 in February, 0 in January, and 7 in December. No recent generalized convulsions reported. Seizure control has improved on current medications.
- Source normalized phrase: `no seizures this month so far`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:16220:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no recent generalised convulsions reported
- `det:16220:2` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: This month so far she has no seizures; earlier 4 in February, 0 in January and 7 in December

### Row 16450 - `frequency_operands_gap`

- Gold label: `1 per multiple day`
- Gold reference: Seizure pattern appears largely unchanged, with events approximately every several days. Occasionally, frequency escalates to daily, and he required midazolam rescue in July and September
- Assessment: The patient experiences generalized seizures approximately every several days, with occasional escalation to daily frequency during clusters. No definite light-triggered events are reported. Clusters are associated with sleep disruption and missed medication doses. Rescue midazolam was required in July and September. Overall seizure pattern is stable outside brief clusters.
- Source normalized phrase: `events approximately every several days`
- Projection issues: `vague_count, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:16450:1` supporting, `seizure_free`, `unclear`, `deterministic_candidate`: no definite light-triggered events
- `llm:16450:1` primary, `frequency_rate`, `current`, `llm_candidate`: Seizure pattern appears largely unchanged, with events approximately every several days.
- `llm:16450:2` supporting, `unknown_frequency`, `current`, `llm_candidate`: Occasionally, frequency escalates to daily,

### Row 16574 - `frequency_operands_gap`

- Gold label: `1 per 4 day`
- Gold reference: His seizures typically occur in clusters, generally spaced four days apart, though brief periods of daily seizures have been reported. VNS is used more frequently, and Buccolam was administered once each month over the past 4 months
- Assessment: The patient experiences seizure clusters approximately once per month, corroborated by monthly Buccolam use. Clusters typically occur spaced about four days apart, with occasional brief periods of daily seizures. VNS and rescue medication use reflect cluster management. No injuries reported; postictal recovery under an hour.
- Source normalized phrase: `approximately one seizure cluster per month`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:16574:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: seizures typically occur in clusters, generally spaced four days apart
- `llm:16574:3` primary, `frequency_rate`, `recent`, `llm_candidate`: Buccolam was administered once each month over the past 4 months
- `llm:16574:2` supporting, `frequency_rate`, `current`, `llm_candidate`: brief periods of daily seizures have been reported

### Row 16674 - `frequency_operands_gap`

- Gold label: `7 per 6 month`
- Gold reference: In Apr she experienced four short absences in a cluster (self-limited). In Jul there was 2 further brief absences, and in Sep another at school (not witnessed by family)
- Assessment: The patient has shown steady improvement with fewer and shorter focal seizures overall. Recent seizure frequency is low with brief absences occurring sporadically over several months. The last menstrual cycle was seizure-free, indicating reduced perimenstrual clustering. No convulsions or injuries reported, and recovery is rapid after each event. Current control is better compared to earlier in the year.
- Source normalized phrase: `four short absences in a cluster in April, two brief absences in July, and one in September`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:16674:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: In Apr she experienced four short absences in a cluster (self-limited). In Jul there was 2 further brief absences, and in Sep another at school (not witnessed by family
- `llm:16674:1` supporting, `cluster_frequency`, `historical`, `llm_candidate`: In Apr she experienced four short absences in a cluster (self-limited).
- `llm:16674:3` supporting, `frequency_rate`, `historical`, `llm_candidate`: in Sep another at school (not witnessed by family)
- `llm:16674:4` supporting, `seizure_free`, `recent`, `llm_candidate`: the last cycle passed without events

### Row 16697 - `frequency_operands_gap`

- Gold label: `3 per 6 month`
- Gold reference: In September a prolonged focal seizure (~10 minutes) settled spontaneously. In November a tonic seizure were recorded, and in February another during physiotherapy
- Assessment: The patient experienced three seizures over the past six months, including a prolonged focal seizure in September, a tonic seizure in November, and another seizure during physiotherapy in February. No rescue medication has been required. Previous seizure during air travel is historical and not included in current burden. The events are spaced over months without clear clustering. The patient has travel-related anxiety due to prior seizure during air travel.
- Source normalized phrase: `Three seizures recorded over six months: September, November, and February`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:16697:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: In September a prolonged focal seizure (~10 minutes) settled spontaneously. In November a tonic seizure were recorded, and in February another
- `llm:16697:1` rejected, `last_event_only`, `historical`, `llm_candidate`: a previous seizure occurred during air travel
- `llm:16697:2` supporting, `last_event_only`, `recent`, `llm_candidate`: In September a prolonged focal seizure (~10 minutes) settled spontaneously
- `llm:16697:3` supporting, `last_event_only`, `recent`, `llm_candidate`: In November a tonic seizure were recorded
- `llm:16697:4` supporting, `last_event_only`, `recent`, `llm_candidate`: in February another during physiotherapy

### Row 16704 - `frequency_operands_gap`

- Gold label: `9 per 6 month`
- Gold reference: A prolonged event occurred in Apr (approximately 12 minutes, alternating between focal and generalised features, settled spontaneously). In Jul she had a drop attack, and in Sep seven myoclonic jerks were documented at college (not observed directly by parents)
- Assessment: The patient experienced a prolonged event in April, a drop attack in July, and seven myoclonic jerks in September, indicating ongoing seizure activity over the past three months. She reports improved stability with current medication. Safety and monitoring plans are in place.
- Source normalized phrase: `seven myoclonic jerks documented in September over three months`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:16704:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: A prolonged event occurred in Apr (approximately 12 minutes, alternating between focal and generalised features, settled spontaneously). In Jul she had a drop attack, and in Sep seven myoclonic jerks were documented at college (not observed
- `llm:16704:1` supporting, `last_event_only`, `historical`, `llm_candidate`: A prolonged event occurred in Apr (approximately 12 minutes, alternating between focal and generalised features, settled spontaneously)

### Row 16719 - `frequency_operands_gap`

- Gold label: `7 per 6 month`
- Gold reference: A prolonged event occurred in December (approximately 12 minutes, alternating between focal and generalised features, settled spontaneously). In March she had a drop attack, and in May five myoclonic jerks were documented at college (not observed directly by parents)
- Assessment: The patient reports early morning myoclonus about once weekly as the primary current seizure frequency. Additional recent events include a prolonged seizure in December, a drop attack in March, and five myoclonic jerks in May, with occasional brief absences reported but not all witnessed. These provide context but are not additive to the primary frequency assessment.
- Source normalized phrase: `early morning myoclonus about once weekly`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:16719:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: A prolonged event occurred in December (approximately 12 minutes, alternating between focal and generalised features, settled spontaneously). In March she had a drop attack, and in May five myoclonic jerks were documented at college (not ob
- `llm:16719:1` supporting, `last_event_only`, `recent`, `llm_candidate`: A prolonged event occurred in December (approximately 12 minutes, alternating between focal and generalised features, settled spontaneously).
- `llm:16719:2` supporting, `last_event_only`, `recent`, `llm_candidate`: In March she had a drop attack,
- `llm:16719:3` supporting, `last_event_only`, `recent`, `llm_candidate`: in May five myoclonic jerks were documented at college (not observed directly by parents).
- `llm:16719:4` primary, `frequency_rate`, `current`, `llm_candidate`: She reports early morning myoclonus about once weekly otherwise,
- `llm:16719:5` supporting, `unknown_frequency`, `current`, `llm_candidate`: and occasional brief absences per her description (brief staring with rapid recovery), though not all have been witnessed.

### Row 16758 - `frequency_operands_gap`

- Gold label: `9 per 5 month`
- Gold reference: In Dec 3 brief absences were reported. In Mar 5 drop attacks occurred, and in Apr another tonic seizure was recorded
- Assessment: The patient experienced a total of 9 seizure-like events over the past 4 months, including brief absences, drop attacks, and a tonic seizure. Medication adherence is good, and no new neurological symptoms were reported. Safety advice and further investigations are planned.
- Source normalized phrase: `3 brief absences in Dec, 5 drop attacks in Mar, and 1 tonic seizure in Apr`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:16758:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: In Dec 3 brief absences were reported. In Mar 5 drop attacks occurred, and in Apr another tonic seizure was recorded
- `llm:16758:1` supporting, `frequency_rate`, `recent`, `llm_candidate`: In Dec 3 brief absences were reported.
- `llm:16758:2` supporting, `frequency_rate`, `recent`, `llm_candidate`: In Mar 5 drop attacks occurred.
- `llm:16758:3` supporting, `last_event_only`, `recent`, `llm_candidate`: in Apr another tonic seizure was recorded.

### Row 16833 - `frequency_operands_gap`

- Gold label: `8 per 6 month`
- Gold reference: A prolonged event occurred in Jul (approximately 12 minutes, alternating between focal and generalised features, settled spontaneously). In Oct she had 5 drop attacks, and in Dec two myoclonic jerks were documented at college (not observed directly by parents)
- Assessment: The patient experienced a prolonged event in July, followed by 5 drop attacks in October and 2 myoclonic jerks in December. Events cluster around periods of sleep disruption but no consistent focal neurological signs are present. Further objective data are pending to clarify diagnosis and event characterization.
- Source normalized phrase: `5 drop attacks in October, 2 myoclonic jerks in December, and a prolonged event in July`
- Projection issues: `frequency_rate_operands_unparsed, frequency_rate_operands_incomplete`
- Route families: ``

Candidate evidence:

- `det:16833:1` primary, `frequency_rate`, `unclear`, `deterministic_candidate`: A prolonged event occurred in Jul (approximately 12 minutes, alternating between focal and generalised features, settled spontaneously). In Oct she had 5 drop attacks, and in Dec two myoclonic jerks were documented at college (not observed
- `llm:16833:1` supporting, `frequency_rate`, `recent`, `llm_candidate`: In Oct she had 5 drop attacks

### Row 16839 - `cluster_axis_gap`

- Gold label: `9 per 4 month`
- Gold reference: In December he had a run of 4 seizures within half an hour (not full generalised tonic-clonic, fluctuating in intensity, resolved without medication). In February there was 4 further seizures at night, and in March another during physiotherapy (unwitnessed by mother)
- Assessment: The patient experienced clusters of 4 seizures in December and February, with an additional single seizure in March during physiotherapy. Seizures are generalised with probable photosensitivity. No emergency attendances or significant injury reported. Clobazam is reserved for cluster rescue. Ongoing monitoring and medication adjustments planned.
- Source normalized phrase: `Clusters of 4 seizures in December and February`
- Projection issues: `cluster_frequency_operands_unparsed, cluster_cadence_operands_incomplete`
- Route families: `cluster_axis_ambiguity`

Candidate evidence:

- `det:16839:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: In December he had a run of 4 seizures within half an hour (not full generalised tonic-clonic, fluctuating in intensity, resolved without medication). In February there was 4 further seizures at night, and in March another
- `llm:16839:1` primary, `cluster_frequency`, `recent`, `llm_candidate`: In December he had a run of 4 seizures within half an hour (not full generalised tonic-clonic, fluctuating in intensity, resolved without medication).
- `llm:16839:2` primary, `cluster_frequency`, `recent`, `llm_candidate`: In February there was 4 further seizures at night
- `llm:16839:3` supporting, `last_event_only`, `recent`, `llm_candidate`: in March another during physiotherapy (unwitnessed by mother)

### Row 16907 - `cluster_axis_gap`

- Gold label: `9 per 6 month`
- Gold reference: In March he had a run of six seizures within half an hour (not full generalised tonic-clonic, fluctuating in intensity, resolved without medication). In June there was two further seizures at night, and in August another during physiotherapy (unwitnessed by mother)
- Assessment: The patient experienced a cluster of six seizures within half an hour in March, with additional isolated seizures in June and August. The overall pattern is improving with lifestyle changes and medication, with shorter, less disruptive seizures and no injuries reported.
- Source normalized phrase: `run of six seizures within half an hour`
- Projection issues: `cluster_frequency_operands_unparsed, cluster_cadence_operands_incomplete`
- Route families: `cluster_axis_ambiguity`

Candidate evidence:

- `det:16907:1` supporting, `frequency_rate`, `unclear`, `deterministic_candidate`: In March he had a run of six seizures within half an hour (not full generalised tonic-clonic, fluctuating in intensity, resolved without medication). In June there was two further seizures at night, and in August another
- `llm:16907:1` primary, `cluster_frequency`, `recent`, `llm_candidate`: In March he had a run of six seizures within half an hour (not full generalised tonic-clonic, fluctuating in intensity, resolved without medication)
- `llm:16907:3` supporting, `frequency_rate`, `recent`, `llm_candidate`: in August another during physiotherapy (unwitnessed by mother)
