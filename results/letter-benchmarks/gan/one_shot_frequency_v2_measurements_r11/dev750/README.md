# R11 compact dev750 first-response comparison

This is a **Gan 2026 synthetic dev750** development result, not a locked-test
or clinical validation result. R11 used one DeepSeek V4.1 Flash call per note,
temperature zero, thinking enabled at low effort, 12-call concurrency, no
retry and no format or semantic repair. All 750 rows, including `row_ok=False`,
are scored against the unchanged compact v0.3 reference of 1,219 claims.
There were 750 first responses; nine were unusable for compact scoring. The
conservative usage charge was US$7.6709676. No test450 rows were inspected.

The [run score](score.json) and [paired comparison](r9_r11_paired_comparison.json)
record identities, hashes, model/prompt/scorer versions, row policy, replay
and repair policy. Raw requests, responses, attempts, parsed outputs and
per-letter scores are under `runs/one_shot_frequency_v2_measurements_r11/dev750/`.
The R9 row scores were replayed under the same
`finding_compact_concepts_v04` scorer; its result is
[versioned separately](../../one_shot_frequency_v2_measurements_r9/dev750/calendar_window_v04/score.json).
The v04 month spelling and range-punctuation aliases do not change R9's full
score. Both prompts use the same finite scored-term dictionary; source labels
and evidence remain literal in saved responses.

| Same dev750 reference and v04 scorer | R9 | R11 |
| --- | ---: | ---: |
| Whole-claim matches | 445 | 428 |
| Extra claims | 864 | 718 |
| Missed claims | 774 | 791 |
| Precision | 34.00% | 37.35% |
| Recall | 36.51% | 35.11% |
| F1 | 35.21% | 36.19% |
| Source-aligned pairs | 1,062 | 1,032 |
| Native Purist correct | 652/750 | 651/750 |
| Native Pragmatic correct | 676/750 | 667/750 |

R11 emits 1,146 usable claims versus R9's 1,309. Its F1 gain of 0.99
percentage points comes from fewer extras despite 17 fewer exact matches.
A paired 5,000-resample bootstrap over source rows (seed 20260924) gives a
95% percentile interval of **−2.00 to +3.95 percentage points** for R11 minus
R9 whole-claim F1. This development comparison does not establish a reliable
improvement. Native paired changes were 25 R11 wins versus 26 R9 wins for
Purist, and 17 versus 26 for Pragmatic.

The source-aligned event component improves from 755 to 807 correct, while
the window component falls from 781 to 697. This fits the source checks:
R11 recovers a five-seizure mixed diary total in 5995 and a 12-event focal
motor total in 6065, but it also carries a six-month window onto claims that
the source did not window separately (12584), omits all compact findings in
12679, and changes an explicit last-event phase in 9103. In 15992 it computes
the approved seven-event total but wrongly calls awake events unrestricted
overall seizures. These are model output errors under the current reference.

Source 2023 exposes a separate annotation question. The note lists four
absence seizures and one myoclonic event this month. R11 merges them into one
combined five-event claim, losing the two named subtype findings. The owner
v0.8.3 rule also calls for one overall count when disjoint mixed-diary
components can be added; the current v0.3 reference contains only the named
counts. Its missing overall count needs a source-first owner decision in a
versioned successor reference. It does not make R11's combined claim an exact
match to the current named findings. The
[selected source checks](../../../../../runs/one_shot_frequency_v2_measurements_r11/dev750/source_review_cases.jsonl)
retain exact quotations, owner edit reasons, saved R9/R11 findings and paired
scores. They illustrate mechanisms, not their prevalence.

R11 remains a development candidate. Its narrower output and diary arithmetic
are useful, but the full run does not justify replacing R9 for a locked-test
comparison. Any next prompt should retain named subtype measurements and avoid
copying a broad context window into every finding. Resolve the 2023 reference
question before interpreting that row as model-only error.
