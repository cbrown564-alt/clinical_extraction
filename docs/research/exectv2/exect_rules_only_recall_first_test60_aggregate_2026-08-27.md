# Results: ExECT rules-only recall-first `test60` aggregate stage-rung replay

Date: 2026-08-27
Protocol: [predeclared replay protocol](exect_rules_only_recall_first_test60_aggregate_protocol_2026-08-27.md)
Artifact: `experiments/exect_rules_only_recall_first_test60_aggregate_20260827.json`
(aggregate-only; sealed rows under `scratch/holdout/`, safety check passed)
Candidate: frozen `RECALL_FIRST_THREE_STAGE_CONFIG` (dev140 select F1 0.9266)
Comparator: `run_letter` (`ACCEPTED_THREE_STAGE_CONFIG`), cited `test60` row **0.8018**
One holdout consumption; Gate A (dev parity) passed before execution.

## Verdict (per the predeclared framing rules)

Candidate select F1 **0.8012** vs comparator **0.8018**
(ΔF1 **−0.0006**; ΔP −0.0186, ΔR +0.0143). Overall ΔF1 < 0, so the
recall-first restructure is reported as **development-only mechanism
evidence**: the cited row stays **0.8018**, `run_letter` stays on
`ACCEPTED_THREE_STAGE_CONFIG`, the fingerprint fixture does not roll,
and no holdout retune starts from this replay.

## Family results (select stop, candidate vs comparator)

| Family | Comparator F1 | Candidate F1 | ΔF1 | ΔP | ΔR | Predeclared band | Read |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Diagnosis | 0.8478 | 0.8357 | −0.0121 | −0.0257 | 0.0000 | [0, +0.03] | **Below band.** The heading-decomposition keep added holdout FPs without recall gain. |
| SeizureFrequency | 0.6131 | 0.6232 | +0.0100 | +0.0052 | +0.0135 | [0, +0.04] | In band; stays below 0.70, standing limitation. |
| Prescription | 0.8395 | 0.8521 | +0.0126 | −0.0260 | **+0.0471** | [−0.01, +0.05], ΔR ≥ −0.01 | In band. ΔR ≥ +0.03: the holdout Rx recall gap is **at least partly lexical** — the blind external dictionary / typo / parse expansion transferred. |
| Investigations | 0.8837 | 0.8736 | −0.0102 | −0.0244 | 0.0000 | [−0.01, +0.03] | Marginally below band. Result variants duplicated units on holdout at flat recall. |

## Stage rungs (candidate, aggregate-only)

| Stop | F1 | P | R |
| --- | ---: | ---: | ---: |
| recognise | 0.6162 | 0.4948 | **0.8166** |
| encode | 0.6167 | 0.4965 | 0.8138 |
| select | 0.8012 | 0.8308 | 0.7736 |

Recognise-stop overall recall **0.8166** fell below the predeclared
[0.88, 0.97] band (dev was 0.9677). Per family: Diagnosis 0.8741,
SF 0.6757, Prescription 0.8471, Investigations 0.8085. The recall-first
recognisers are therefore substantially dev-fitted: the dev140 recall
targets did not transfer. Investigations is fully distributional —
recognise recall (0.8085) already equals select recall, so the missing
holdout units are never recognised, not filtered away.

## What this supports

- The Select keep/drop gate architecture transfers structurally: the
  candidate held holdout F1 within 0.001 of the comparator while
  carrying a much wider recognise ledger (recognise P 0.49).
- The Prescription external-lexicon mechanism transfers
  (+0.0471 holdout recall, built blind to holdout).
- The dev-measured Diagnosis/SF recall gains and the Diagnosis/Inv
  keep precision are development evidence only.

## What this does not support

- No change to any cited number: the rules row remains **0.8018**
  (`test60`), 0.9167 (`dev140`).
- No claim that recall-first recognise reaches 0.90+ recall beyond
  dev140.
- No holdout row inspection or retune from this result. A future
  candidate starts as a new development candidate under a new
  predeclared protocol.
