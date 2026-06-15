# Gan 2026 Unknown-Frequency Policy Audit

Date: 2026-06-15

## Purpose

Yujian clarified that Gan seizure-frequency labels should avoid over-interpreting
ambiguous seizure counts or ambiguous time windows. This audit records the
validation-only policy implications for the current `fresh_evidence_reasoner`
line. It does not inspect or tune from `test450` row-level failures.

## Policy Rule

Portability category: `seizure_frequency`, with Gan label-scheme-specific
projection consequences.

Rule:

- If either the number of seizures or the relevant time period is unclear,
  prefer `unknown` over an inferred frequency.
- A most-recent seizure date alone is not a count over a defined window.
- A statement like "since starting/beginning medication or diet" is not enough
  unless the start date or elapsed period is explicit enough to define the
  denominator.
- An explicit seizure count plus a usable follow-up period can support a
  frequency label when the note timeline defines the period.

This is prompt policy, not scorer policy. The Gan Purist mapper still maps
`unknown`, `no seizure frequency reference`, and `multiple per ...` labels into
the unknown Purist category when their monthly frequency is `1000.0`.

## Supervisor Examples

All six supervisor-discussed examples are in `gan2026_split_v1` validation.

| Source row | Gold | Policy reading | V12 v0.4 raw/final decision | Purist result |
| ---: | --- | --- | --- | --- |
| 11272 | `unknown` | Last seizure date and no-seizures-since text should not become a defined frequency or seizure-free label. | `seizure free for 3 month` | Wrong |
| 14454 | `2 per 2 month` | Two seizures are explicit and the surrounding post-topiramate follow-up period is usable. | `2 per 2 month` | Correct |
| 14029 | `unknown` | Several drop attacks since ketogenic diet, but diet start/window is unclear. | `multiple per month` | Purist-correct unknown bucket, semantically over-specific |
| 13267 | `2 per 5 month` | Five-month period and post-remission activity are explicit enough under the current scheme. | `unknown` | Wrong |
| 14137 | `unknown` | Avoid deriving a frequency from open-ended "since beginning Clobazam" plus most-recent event framing. | `3 to 4 per month` | Wrong |
| 11337 | `unknown` | One provoked breakthrough seizure is ambiguous unless the relevant period is clearly defined from the note context. | `1 per 8 week` | Wrong |

## Validation Slice Signal

Artifact audited:

- `experiments/gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl`

Gold-normalized `unknown` rows on validation:

- Rows: `92`
- V0 Purist-correct: `79/92`
- V12 v0.4 raw model Purist-correct: `75/92`
- V12 v0.4 format-only Purist-correct: `75/92`
- V12 v0.4 final Purist-correct: `76/92`
- V12 v0.4 actions: `69` keep original, `23` replace
- V12 v0.4 raw unknown replacements: `6`

Interpretation: the v0.4 prompt underperforms the V0 comparator on the
validation unknown slice and sometimes over-infers exact rates from last-event
or open-ended "since" evidence. The issue is not simply failure to output the
literal word `unknown`; some `multiple per ...` outputs are counted as unknown
by Purist scoring while still being clinically over-specific.

## Implemented Change

`fresh_evidence_reasoner` prompt version `gan2026_fresh_evidence_reasoner_v0_6`
adds explicit unknown-frequency boundary instructions:

- prefer unknown when count or period is unclear;
- treat last-event-only evidence as unknown;
- treat open-ended "since starting/beginning medication or diet" as unknown
  unless both count and window are explicit;
- reject last-seizure-date plus no-seizures-since evidence as a seizure-free
  duration unless the duration is independently stated as the current frequency
  state;
- reject single provoked breakthrough events as rates unless the observation
  period for that event count is defined;
- preserve explicit count plus usable follow-up period as frequency evidence.

The safety gate is now `gan2026_fresh_evidence_safety_gate_v0_9`. It keeps the
nonselective `unknown` replacement block, but allows selective last-event-only
unknown demotions from seizure-free originals and blocks open-ended
treatment-start denominators when the original answer is already a boundary
state. It also blocks seizure-free replacements of original frequency labels
when the model rationale points to historical frequency rather than a current
absence state. The v0.8 replay added two regression guards: do not exactify vague
`multiple per ...` originals from terms such as "a few", "a couple", and
"several"; and do not downgrade a same-day seizure cluster original merely
because the model says the daily rate is not recurring. This is deterministic
rule coverage in the `seizure_frequency` category, not scorer or label-mapping
drift.

Safety v0.9 adds one scorer-neutral semantic repair: when a safety fallback
would preserve `no seizure frequency reference` but the model's own evidence
shows seizure activity with unclear count/window, render `unknown` instead.
This matches Yujian's guidance that unclear seizure-frequency evidence is
usually `unknown`, not no-reference.

## Validation Hard-Slice Results

| Run | Surface | V0 Purist | Raw Purist | Final Purist | W->C | C->W | Interpretation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| v0.5 prompt, safety v0.4 | supervisor6 | 4/6 | 2/6 | 2/6 | 0 | 2 | Rejected: wording was not strong enough. |
| v0.6 prompt, safety v0.5 | supervisor6 | 4/6 | 4/6 | 4/6 | 1 | 1 | Prompt fixed last-event unknowns, but treatment-start denominator still regressed. |
| v0.6 prompt, safety v0.6 | supervisor6 | 4/6 | 4/6 | 5/6 | 1 | 0 | Promising small-slice result. |
| v0.6 prompt, safety v0.6 | trigger25 | 21/25 | 21/25 | 22/25 | 1 | 0 | Positive validation hard-slice result; still too small for holdout promotion. |
| v0.6 prompt, safety v0.6 | trigger_full | 105/123 | 98/123 | 108/123 | 4 | 1 | Useful targeted lift, but one regression remained. |
| v0.6 prompt, safety v0.7 | trigger_full | 105/123 | 98/123 | 109/123 | 4 | 0 | Positive hard-slice result after blocking historical-frequency-to-seizure-free regression. |
| v0.6 prompt, safety v0.7 | validation250 | 236/250 | 232/250 | 238/250 | 4 | 2 | Beats V0 by two rows, but trails the earlier v0.4 validation250 result (`242/250`); diagnostic/revise, not promotion. |
| v0.6 prompt, safety v0.9 no-call replay | trigger_full | 105/123 | 98/123 | 109/123 | 4 | 0 | Maintains the targeted unknown-boundary gain; 4 scorer-neutral no-reference-to-unknown repairs. |
| v0.6 prompt, safety v0.9 no-call replay | validation250 | 236/250 | 232/250 | 240/250 | 4 | 0 | Removes both safety-v0.7 validation250 regressions; 5 scorer-neutral no-reference-to-unknown repairs; still trails v0.4 `242/250`; diagnostic/revise, not promotion. |

Artifacts:

- `experiments/gan2026_fresh_evidence_reasoner_unknown_policy_supervisor6_validation_live_gpt41_v0_5_2026-06-15.md`
- `experiments/gan2026_fresh_evidence_reasoner_unknown_policy_supervisor6_validation_live_gpt41_v0_6_2026-06-15.md`
- `experiments/gan2026_fresh_evidence_reasoner_unknown_policy_supervisor6_validation_live_gpt41_v0_6_safety_v0_5_2026-06-15.md`
- `experiments/gan2026_fresh_evidence_reasoner_unknown_policy_supervisor6_validation_live_gpt41_v0_6_safety_v0_6_2026-06-15.md`
- `experiments/gan2026_fresh_evidence_reasoner_unknown_policy_trigger25_validation_live_gpt41_v0_6_safety_v0_6_2026-06-15.md`
- `experiments/gan2026_fresh_evidence_reasoner_unknown_policy_trigger_full_validation_live_gpt41_v0_6_safety_v0_6_2026-06-15.md`
- `experiments/gan2026_fresh_evidence_reasoner_unknown_policy_trigger_full_validation_live_gpt41_v0_6_safety_v0_7_2026-06-15.md`
- `experiments/gan2026_fresh_evidence_reasoner_validation250_live_gpt41_v0_6_safety_v0_7_2026-06-15.md`
- `experiments/gan2026_fresh_evidence_reasoner_unknown_policy_trigger_full_validation_nocall_replay_v0_6_safety_v0_9_2026-06-15.md`
- `experiments/gan2026_fresh_evidence_reasoner_validation250_nocall_replay_v0_6_safety_v0_9_2026-06-15.md`

## Decision

The v0.6 prompt/safety-v0.9 line is not promoted to a holdout-facing run. It
captures Yujian's unknown-frequency rule, improves the predeclared
unknown-boundary trigger panel (`109/123` versus V0 `105/123`) with no final
correct-to-wrong regressions on that panel, and improves the v0.7 validation250
replay from `238/250` to `240/250`. It also converts 4 trigger-panel and 5
validation250 no-reference fallbacks to `unknown` without changing Purist
counts. The broader validation250 check is still weaker than the earlier v0.4
comparator (`242/250`).

Next validation-only design work should preserve the specific safety lessons
while either reverting to the stronger v0.4 base prompt or moving the
unknown-frequency logic into a narrower selector/router. Promotion still
requires improving the unknown hard slice without regressing explicit
count-plus-window cases such as rows `14454` and `13267`, and without losing the
broader validation250/validation750 margin.

## 2026-06-15 Addendum: Ambiguity Classification

The follow-up selector residual audit showed that many remaining errors are not
selector errors: no available deterministic, consensus, or V12 fresh-evidence
component is correct. A deterministic last-event-to-unknown repair probe was
then rejected because broad profile-string rewrites damage true seizure-free
rows.

The next component-generation contract is therefore model-owned. The
`fresh_evidence_reasoner` schema now accepts an optional
`ambiguity_classification` field before final-label rendering, and the safety
gate can permit selective `unknown` replacements when the model marks
`unknown_count_or_window`, `last_event_only_unknown`, or
`cluster_axis_incomplete`.

The registered supervisor-seeded ambiguity panel passes `6/6` across the six
examples in this audit:

- `11272`: `last_event_only_unknown` -> `unknown`
- `14454`: `explicit_count_window` -> `2 per 2 month`
- `14029`: `unknown_count_or_window` -> `unknown`
- `13267`: `explicit_count_window` -> `2 per 5 month`
- `14137`: `unknown_count_or_window` -> `unknown`
- `11337`: `unknown_count_or_window` -> `unknown`

Artifact:

- `experiments/gan2026_unknown_frequency_ambiguity_panel_2026-06-15.md`

This is validation infrastructure only. Because the reasoner and its tests have
changed from the frozen hashes, the old V12 v0.6/safety-v0.9 preflight is now
expected to fail until a new validation-backed freeze packet is written.
