# 06 — Gan 2026 retained evidence

Last updated: 2026-07-14

Gan 2026 asks for one current seizure-frequency label per letter.

## Split policy

- validation750 is the development and replay surface;
- test450 is locked and aggregate-only;
- a new holdout run requires a fresh frozen protocol and explicit authority;
- row-level test450 analysis and post-test tuning are prohibited.

## Retained comparison

| Family | Split | Purist result | Role |
| --- | --- | ---: | --- |
| Rules only | validation750 | 697/750 | Deterministic comparator |
| LLM only | validation750 | 581/750 | Single-pass comparator |
| Hybrid | validation750 | 661/748 rendered | Single-pass structured-event comparator |

The exact artifacts and closures are in the
[retained evidence manifest](../experiments/retained_evidence_manifest.md).

## Frozen holdout evidence

| Subject | Purist result | Boundary |
| --- | ---: | --- |
| Operational structured-event pass | 364/450 | Frozen aggregate |
| V12 multi-trace ceiling | 379/450 | Saved aggregate comparator only |

The V12 source candidate was removed. Its aggregate report remains because it
supports the quality-versus-complexity question. Calls, tokens, cost, latency,
hardware, and cache policy still need a matched comparison.

## Label semantics

Purist and Pragmatic mapping, cluster handling, seizure-free handling, and
normalization are owned by current code, tests, and
[the normalization note](../design/gan2026_normalization_semantics.md).

