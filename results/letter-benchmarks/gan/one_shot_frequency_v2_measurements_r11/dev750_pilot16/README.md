# R11 fixed development pilot

This is a selected 16-letter **Gan 2026 synthetic dev750** prompt check, not a
representative performance estimate. The fixed source IDs, including eight
owner-approved diary totals, were chosen before the R10 and R11 calls. R9,
R10 and R11 use the same DeepSeek V4.1 Flash model, one first response per
letter, temperature zero, no retries and no repair. The source and compact
v0.3 reference are unchanged. No test450 rows were inspected.

R10 added a finite common-type vocabulary and the bounded diary-sum rule. R11
clarified `time.source` as a concise window and distinguished an unspecified
population from an explicitly overall one. Seven fictional schema examples
passed before each run. The [comparison JSON](calendar_window_v04_comparison.json)
replays all three saved responses with `finding_compact_concepts_v04`, which
normalizes written month abbreviations and range punctuation while keeping
separate listed months distinct from a continuous range. R9's full dev750
score is unchanged by this scorer revision.

| Saved first responses, same 16 letters | Matches | Extras | Misses | F1 |
| --- | ---: | ---: | ---: | ---: |
| R9 | 6 | 45 | 27 | 14.29% |
| R10 | 9 | 18 | 24 | 30.00% |
| R11 | 14 | 11 | 19 | 48.28% |

R11 returned the owner-approved derived count in all eight selected diary
cases. Some whole claims still miss because of population scope, subtype
coverage or other fields. The pilot supports running R11 on the full dev750;
its selected F1 must not be reported as broad performance. R10 cost
US$0.1761174 and R11 cost US$0.172701 under the conservative usage calculation.
Raw requests, responses, attempts, parsed predictions and per-letter scores
are retained under `runs/one_shot_frequency_v2_measurements_r10/dev750_pilot16/`
and `runs/one_shot_frequency_v2_measurements_r11/dev750_pilot16/`. The
[rendered R11 prompt](../../one_shot_frequency_r11_compact_v01_no_call/rich.messages.json)
and its checks are versioned separately.

The native answer was unchanged in this selection: R9, R10 and R11 each
matched 14/16 Purist and 15/16 Pragmatic labels. This small selection does not
establish native-answer equivalence on dev750.
