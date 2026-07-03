# SF direction-extraction probe — results

Date: 2026-07-03. Owner: ExECTv2 workstream.
Hypothesis: `sf_direction_extraction_probe_2026-07-03` — **REFUTED** (main claim).
Predeclaration: `exectv2_sf_direction_probe_predeclaration_2026-07-03.md`.
Driver: `scripts/run_exectv2_sf_direction_probe.py`.

## Reframed purpose (post pre-work finding)

The pre-work free replay established that the v08 hybrid SF producer is NOT
direction-blind — it scores **0.8897** (dev140) on `state_profile_directional`
by sourcing directions from `deterministic/rules/change.py`. The
direction-blindness finding (state_profile_directional 0.6552 on the raw
SF-verify LLM program) is a property of the raw two-stage program, which the
production pipeline does not use alone.

So this probe tested: **can an LLM-only direction-aware program MATCH the
hybrid's deterministic direction arbitration?** (evidence for/against the
paper's "deterministic lanes are not strictly necessary" thread). The canonical
SF analysis was skeptical that it could.

## Results

### Phase B1 — post-hoc direction adjudication (~28 calls, dev140)

Isolated MODEL CAPACITY from SCHEMA DEFECT: take the raw SF-verify program's 35
changed-state mentions (all FC=Same) across 28 letters, make ONE LLM call per
letter asking it to assign a 5-way direction, re-score.

| Run (dev140) | `state_profile_directional` F1 | `state_profile` F1 |
| --- | ---: | ---: |
| Raw SF-verify (direction-blind) | 0.6552 (tp=95 fp=55 fn=45) | 0.7483 |
| **Post-hoc adjudicated** (28 calls) | **0.7254** (tp=107 fp=48 fn=33) | 0.7483 |

**B1 PASSED its kill criterion.** When explicitly asked to judge direction, the
model recovered **+12 of 30** gold-directional changed facts (adjudicated
directions: 12 Increased, 10 Decreased, 7 Frequent, 2 Infrequent — a sensible
distribution, not noise). `state_profile` was byte-identical (the direction
field is additive). **The model CAN judge direction in isolation; the schema
defect (the raw program never asked) was the bottleneck for 12/30 facts.**

### Phase B2 — full two-stage direction-aware extraction (gated on B1)

Modified the SF-verify program: added `change_direction` to the event schema
(the evolved instruction already asks for it; the schema and `events_to_sf_facts`
ignored it), wired the adapter to pass it through to `FrequencyChange`, and
appended a DIRECTION DISCIPLINE delta to the evolved verify instruction. Ran
both a direction-aware treatment and a non-directional baseline (same-day, same
evolved instructions minus the delta) through the same scorer.

| Run | `state_profile_directional` F1 | `state_profile` F1 | `clinical_headline` F1 |
| --- | ---: | ---: | ---: |
| **dev140** | | | |
| Non-directional baseline (this run) | 0.6667 (tp=98 fp=56 fn=42) | 0.7793 | 0.6439 |
| Direction-aware treatment | 0.5892 (tp=71 fp=30 fn=69) | 0.6245 | 0.4965 |
| Δ (treatment − baseline) | **−0.0775** | **−0.1548** | **−0.1474** |
| v08 hybrid production (reference) | 0.8897 | 0.9338 | — |
| gap (direction-aware LLM − hybrid) | **−0.3005** | — | — |
| **full-200** | | | |
| Non-directional baseline (this run) | 0.6494 (tp=138 fp=82 fn=67) | 0.7648 | 0.5880 |
| Direction-aware treatment | 0.6012 (tp=104 fp=37 fn=101) | 0.6257 | 0.4703 |
| Δ (treatment − baseline) | **−0.0483** | **−0.1391** | **−0.1177** |
| v08 hybrid production (reference) | 0.8483 | 0.8738 | — |
| gap (direction-aware LLM − hybrid) | **−0.2471** | — | — |

**B2 REFUTED the main claim.** The direction-aware two-stage program regressed
on ALL metrics on BOTH splits — including the target `state_profile_directional`.
It trails the v08 hybrid production number by ~0.25–0.30.

## The finding: a capacity-vs-execution gap

The decisive contrast is B1 vs B2:

- **B1 (post-hoc adjudication): +0.07.** When asked to judge direction IN
  ISOLATION (a focused single-purpose call over an existing extraction), the
  model recovers 12/30 gold-directional facts. The schema defect — not model
  capacity — was the bottleneck.
- **B2 (extraction-time emission): −0.08.** When asked to emit direction AS
  PART OF the two-stage extraction task, the model regresses on everything,
  including the directional metric.

**Interpretation: the model can judge direction, but cannot cleanly emit it as
part of the structured extraction task.** Adding a new field to the event schema
increases the extraction's cognitive load and degrades the other fields — the
direction emission competes with (rather than complements) the kind/evidence/
applies_to emissions. This is the same task-overload pattern the Rx probes
exhibited (probe #3's AED-only instruction harmed recall before the
emit-if-unsure fix).

## Implication

The v08 hybrid's deterministic direction arbitration
(`deterministic/rules/change.py`, a regex-based change extractor emitting the
closed FC vocabulary) is **genuinely better** at direction than an LLM-only
direction-aware program — by ~0.25-0.30 on `state_profile_directional`. The
canonical SF analysis's skepticism is confirmed: the LLM-only route does not
out-learn the deterministic rules.

This is **evidence FOR the paper's architecture-of-record**: the v08 hybrid's
deterministic SF components are not removable redundancy. The deterministic
`rules/change.py` does something the LLM demonstrably cannot match on this
metric, even with a schema fix and explicit direction discipline.

A post-hoc adjudication pass (B1) over an LLM extraction is a viable cheap
**supplement** (+0.07) but does not approach the hybrid; and in practice the
hybrid already captures those facts via the deterministic lane, so B1's gain
is hypothetical (it improves a raw-LLM baseline the production pipeline doesn't
use alone).

## Provenance

- B1 artifact: `experiments/exectv2_sf_verify_posthoc_direction_dev140_20260703.jsonl`
- B2 artifacts: `experiments/exectv2_sf_direction_aware_{dev140,full200}_20260703.jsonl`
- Driver: `scripts/run_exectv2_sf_direction_probe.py`
- Call counts: B1 28 (dev140), B2 dev140 ~280 (140 generate + 140 verify), B2 full-200 ~400.
- Free-replay baseline: `docs/experiments/exectv2/seizure_frequency/_sf_directional_baseline_replay_2026-07-03.json`
