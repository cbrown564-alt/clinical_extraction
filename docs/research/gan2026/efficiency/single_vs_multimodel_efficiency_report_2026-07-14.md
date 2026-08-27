# Gan single-pass versus multi-model efficiency result

Date: 2026-07-14

## Answer

The retained evidence supports a quality-versus-call-structure conclusion, not
a matched token, cost, or latency conclusion.

On the locked `test450` aggregate, V12 scored `379/450` Purist and the
single-pass event extractor scored `364/450`. The gain is 15 rows, or 3.33
percentage points. A cold single-pass execution requires one model pass per
note. The saved V12 test condition requires GPT and Qwen extraction passes plus
one reasoner pass, or three model passes per note. DeepSeek input was unavailable
on all 450 rows.

The saved V12 holdout audit was not a cold matched run: it made 450 live
reasoner calls while replaying two previously saved upstream traces. The
single-pass aggregate came from an earlier live run. Comparing their recorded
wall time or spend would therefore mix execution dates, models, hosted and
local runtimes, and cache conditions.

## Evidence table

| Dimension | Single pass | V12 | Evidence status |
| --- | --- | --- | --- |
| Purist quality | 364/450 (0.809) | 379/450 (0.842) | Observed aggregate holdout result |
| Cold model passes per note | 1 | 3 | Registry plus aggregate input-availability audit |
| Calls in the retained V12 audit | Earlier live pass; per-call telemetry absent | 450 new reasoner calls plus two replayed upstream traces | Partly observed, not matched |
| Prompt/completion tokens | Not retained | Not retained | Unavailable |
| Dollar or energy cost | Not retained | Not retained | Unavailable |
| Wall-clock latency | Not retained | Not retained | Unavailable |
| Hardware | Hosted provider hardware undisclosed | Mixed hosted/local; local Qwen hardware unretained | Partial, not matched |
| Cache use | Originating cache telemetry unretained | Two upstream traces replayed | Partial, conditions differ |

`Purist correct / cold model pass` is `0.8089` for the single pass and `0.2807`
for V12. This is an architecture ratio, not a token, price, or latency measure.

## Component and regression evidence

The V12 run registry records 26 wrong-to-correct changes and 13
correct-to-wrong changes relative to the single-pass answer. The selected
aggregate report records changed-label precision `0.3171` and 423 exact
evidence substrings overall. Neither source records
exact-evidence coverage for every changed row, clinical-subproblem ownership, or
first-failure ownership.

The saved final score difference is 15 rows, while the saved changed-row counts
net to 13. Reconciling the two would require prohibited row-level holdout
inspection. The test result therefore supports only system-level attribution.
Validation evidence in the selected architecture report assigns the improvement
to the full corroboration-and-reasoner system rather than to the near-inert
guard layer, but that mechanism is not promoted as row-level holdout evidence.

## Decision

Retain the single-pass system as the operational Gan method. V12's 3.33-point
quality gain does not justify restoring a removed three-pass research pipeline
when no matched token, cost, latency, or hardware evidence survives.

Close the retrospective efficiency phase with two explicit limits:

- the paper may compare saved quality and required model passes;
- the paper must not claim measured token, dollar, energy, hardware, or latency
  efficiency.

No new model calls were made, no locked row was inspected, and no pipeline,
prompt, scorer, split, or repair policy changed.

## Reproduction

The machine-readable result is
`experiments/gan2026_single_vs_multimodel_efficiency_2026-07-14.json`.
Validate its aggregate facts with:

```powershell
.venv\Scripts\python.exe scripts\check_gan2026_efficiency_comparison.py
```
