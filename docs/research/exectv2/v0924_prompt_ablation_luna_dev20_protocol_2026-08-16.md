# Protocol: ExECT `v0.9.24` leave-one-out prompt prune on Luna `dev20`

Date: 2026-08-16  
Status: **complete; four-arm answer. Scope is load-bearing; the other three slices are low_value.**  
Parent: [Decision 0054](../../decisions/0054-model-request-order-and-metadata-are-explicit.md); [prompt variant slots](prompt_variant_slots_2026-08-16.md)  
Catalog: Phase 1/2 convention catalog pruned; living owner
[prompt variant slots](prompt_variant_slots_2026-08-16.md)

This is not a from-scratch rebuild. Each candidate is `v0.9.24` with one
named slice removed. The selected stack stays
`exectv2_hybrid_key_family_event_ledger_v0.9.24`. `test60` is sealed.

`v0.9.25` is already used by two additive Luna variants. This series
starts at `v0.9.26`.

## Primary question

On the frozen 20-letter Luna pool, which named slice of the oversized
`v0.9.24` prompt moves four-family hybrid headline F1 when it is
removed and everything else is left in place?

v10 dropped the whole manual at once and SeizureFrequency collapsed.
That does not say which slice was load-bearing. This series measures
one slice at a time.

## Why leave-one-out, not a cumulative strip

A cumulative prune (`v0.9.26` drops examples, `v0.9.27` drops
examples plus encoding) confounds the second delta. Leave-one-out
answers “how much score does this slice buy in the winning prompt.”
A later cumulative prune is allowed only after these four deltas
exist.

## Arms

| Arm | Prompt | Drop | Calls |
| --- | --- | --- | ---: |
| `v0924_head` | saved `v0.9.24` through HEAD | none | 0 |
| `drop_scaffold` | `v0.9.26_drop_scaffold` | architecture, decision procedure, candidate ledger, lane guide, and the four junk ledger-operator rules | 20 |
| `drop_examples` | `v0.9.27_drop_examples` | the 49 worked examples | 20 |
| `drop_encoding` | `v0.9.28_drop_encoding_rules` | the 29 catalog `encoding` clinical rules | 20 |
| `drop_scope` | `v0.9.29_drop_scope_rules` | the 25 catalog `scope` clinical rules | 20 |

Rule classes come from the 2026-08-15 catalog. The live `v0.9.24`
payload now has 83 clinical rules: the catalog's CUI-invention rule
was removed earlier and is not part of this series. Hygiene rules and
the three `already_code` rules stay in every arm. Schema, family
guidance, and attribute vocabulary stay. Hybrid projection stays on
HEAD.

`drop_scaffold` rewrites the task sentence so it does not mention the
removed ledger. That is not a new job.

## Data and scoring

- Dataset: ExECTv2 (2025), split manifest
  `data/ExECTv2 (2025)/splits/exectv2_split_v2.json`.
- Same frozen `dev20` as v10–v19 and mention-unit v1: EA0002, EA0004,
  EA0005, EA0006, EA0007, EA0008, EA0009, EA0010, EA0011, EA0012,
  EA0015, EA0016, EA0047, EA0074, EA0093, EA0120, EA0131, EA0133,
  EA0154, EA0158.
- Development rows may be inspected. `test60` remains aggregate-only.
- Model: `openai/gpt-5.6-luna`. Temperature 1.0. Cache off. One call
  per letter per arm.
- Primary: four-family `clinical_headline` F1 through unchanged HEAD
  assembly, versus saved `v0.9.24` on the same letters.
- Secondary: family F1, four-family letter exact, parse/schema
  failures, and changed-row direction. EA0004 and EA0010 are
  contamination letters (examples 09 and 20). Report them separately;
  do not retune the prompt from those two letters.

## Order and stop rule

Run the arms in the table order. Score each arm before starting the
next. Do not start `dev140`. Do not change the default prompt.

After each arm:

- **low_value** if hybrid headline drop < 0.05, no family drop ≥ 0.08,
  and net four-family exact losses < 3. That slice is a later prune
  candidate.
- **load_bearing** if any of those bars fail. Keep that slice in the
  winning prompt. Do not put it back as a new metaphor.
- **revise** if parse/schema failures appear or the payload contract
  drifted.

A low-value scaffold does not authorize dropping examples. Each arm
answers one slice.

## Claim boundary

GPT-5.6 Luna ExECT development result on the named `dev20` sample. It
is not clinical validation, not holdout evidence, and not a Decision
0050 change. A small drop on this pool is not proof the slice is
worthless on `dev140`.
