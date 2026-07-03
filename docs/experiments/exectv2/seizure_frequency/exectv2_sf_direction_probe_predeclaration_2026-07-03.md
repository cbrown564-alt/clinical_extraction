# Predeclaration — SF direction-aware two-stage probe (B2, dev140 + full-200)

Date: 2026-07-03. Owner: ExECTv2 workstream.
Hypothesis: `sf_direction_extraction_probe_2026-07-03` (PENDING).
Driver: `scripts/run_exectv2_sf_direction_probe.py b2 {dev140,full200} --cache`.
B1 results: this doc, §"Phase B1 result".

## Reframed purpose (post pre-work finding)

The free pre-work replay established that the v08 hybrid SF union-arbitration
producer is NOT direction-blind — it scores **0.8897** on `state_profile_directional`
on dev140 by sourcing directions from `deterministic/rules/change.py`. The
direction-blindness finding (state_profile_directional 0.6552) is a property of
the RAW two-stage SF-verify LLM program, which the production pipeline does not
use alone.

So this probe does NOT test "is the deterministic side blind" (known). It tests:

  Can an LLM-only direction-aware program MATCH the hybrid's deterministic
  direction arbitration on state_profile_directional?

This is evidence for/against the paper's "deterministic lanes are not strictly
necessary" thread. The canonical SF analysis (`exectv2_sf_changed_class_row_analysis_2026-06-29.md`
§10) is skeptical — it argues the LLM-only route will not out-learn the
deterministic `rules/change.py` regex patterns.

## Phase B1 result (cheap capacity test, ~28 calls, dev140 post-hoc)

| Run | `state_profile_directional` F1 | `state_profile` F1 | Direction recovered |
| --- | ---: | ---: | --- |
| Raw SF-verify (direction-blind) | 0.6552 (tp=95 fp=55 fn=45) | 0.7483 | 0/12 (baseline) |
| **Post-hoc adjudicated** (28 calls) | **0.7254** (tp=107 fp=48 fn=33) | 0.7483 | **+12 tp** |
| v08 hybrid production (reference) | 0.8897 | 0.9338 | (sourced from rules/change.py) |

B1 isolated MODEL CAPACITY from SCHEMA DEFECT: when explicitly asked to judge
direction, the model recovered 12 of the 30 gold-directional changed facts
(adjudicated directions: 12 Increased, 10 Decreased, 7 Frequent, 2
Infrequent — a sensible distribution, not noise). `state_profile` was
byte-identical (0.7483 — the direction field is additive, regression check
passes).

**Kill criterion PASSED** (>2 recovered). The schema defect (the raw program
never asked for direction) was the bottleneck for 12/30 facts; the model can
judge direction when asked.

## Phase B2 design (full two-stage direction-aware extraction)

Modify the SF-verify two-stage program:
1. **Schema**: add `change_direction` to `EVENT_SCHEMA` (the evolved instruction
   already asks for it — the instruction text contains "change_direction only
   when kind = changed" — but the schema didn't list it and `events_to_sf_facts`
   ignored it; this wires it through).
2. **Adapter**: `events_to_sf_facts_directional` maps `change_direction` →
   `FrequencyChange` instead of the adapter defaulting to "Same".
3. **Instruction**: append a DIRECTION DISCIPLINE delta to the evolved verify
   seed (assert a direction for every changed event; never default to
   null/same out of uncertainty).
4. Run generate→verify with the same evolved generate instruction, score
   `state_profile_directional` (primary), `state_profile` + `clinical_headline`
   (regression check).

## Predeclared outcomes

The target metric is `state_profile_directional`. The reference is the v08
hybrid production number (0.8897 dev140 / 0.8483 full-200 from the free-replay
baseline).

| Outcome | Verdict | Action |
| --- | --- | --- |
| Direction-aware `state_profile_directional` >= hybrid reference on dev140 AND full-200, with no `state_profile` regression | **LLM matches hybrid** — evidence deterministic lane not strictly necessary for direction | Report as a paper-relevant finding (the LLM can match the deterministic arbitration) |
| Direction-aware beats raw baseline (0.6552) but trails hybrid (0.8897) | **PARTIAL** — schema fix helps but LLM cannot match deterministic arbitration | The canonical analysis's skepticism confirmed; the deterministic rules/change.py is genuinely better at direction |
| `state_profile` regresses (direction wiring harms the direction-blind metric) | **REFUTED** — the additive assumption fails | Document; the direction field is not free |

## Cost

- dev140: ~280 calls (two-stage: 140 generate + 140 verify), gpt-4.1-mini temp 0, cached.
- full-200: ~400 calls (200 generate + 200 verify), aggregate-only.
- Same-day direction-aware vs non-directional baseline isolation (both arms run
  in the same invocation through the same scorer).
