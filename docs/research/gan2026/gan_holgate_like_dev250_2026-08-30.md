# Holgate-like dialect on `dev250`

Date: 2026-08-30
Status: development answer; holdout aggregate confirmation
Owner: this file
Protocol: [dev250 protocol](gan_holgate_like_dev250_protocol_2026-08-30.md)
Artifact: [aggregates](gan_holgate_like_dev250_2026-08-30.json)
Projection: `holgate_dialect_v1` in
`src/clinical_extraction/paper/holgate_dialect.py`

## Question

Which Holgate-like labels fail the living parser because the model
did what the Holgate prompt asked, not because it missed the
clinical state?

## Sample

`gan_holgate_like_dev250_v1`: 250 letters from `dev750`, seed
20260830. Gemini 3.7 Flash Holgate-like find. 0 parse failures, 0
call failures. Letters may be read. `test450` was not used to invent
aliases.

## Living find on the 250 letters

Scorable **69**/250. Purist **66**. The common unscorable strings
were empty `final_label` with kind `unknown` (20) or `no_reference`
(3), `I do not know.` (19), hyphenated `seizure-free` / `seizure_free`
(21+), and `N seizures per month` / `N/month` rates.

`I do not know.` is the Holgate abstention the prompt required.
Living parse accepts `unknown` and `no seizure frequency reference`,
which already share the Purist unknown band.

## Frozen projection

`holgate_dialect_v1` is an ablation scorer. It does not change the
living codebook parser. It maps:

- `I do not know` / `I don't know` → `unknown`
- empty label + kind `unknown` / `no_reference` → the matching sentinel
- `seizure-free` / `seizure_free` → `seizure free` (already parseable)
- `0 seizures` → `seizure free`
- `N seizures per unit` and `N/unit`, including a flattened `≤`

Narrative multi-type strings stay unscorable.

## After projection

| Surface | Living find | Dialect find | Dialect encode | Dialect select |
| --- | ---: | ---: | ---: | ---: |
| `dev250` | 0.264 (66) | 0.636 (159) | 0.664 (166) | 0.700 (175) |
| Locked `test450` | 0.333 (150) | 0.616 (277) | 0.640 (288) | 0.649 (292) |

On `dev250`, 124 letters become scorable. Rescue families:
hyphenated seizure-free 41, `N seizures per` 25, empty+unknown 20,
`I do not know` 19, slash rates 13, empty+no_reference 3, zero
seizures 2. Holdout confirmation is aggregate-only (161 format
rescues). No holdout row inspection.

Cited codebook find / select on the same `test450` remain **355** /
**387**. Dialect Holgate find **277**, encode **288**, and select
**292** are the fairer comparison and still below the codebook.

## Claim boundary

Development answer plus holdout aggregate confirmation. These
dialect scores are not the living scorer and not Table 1. Fair:
“the Holgate ask was being punished for writing `I do not know`
and nearby Holgate phrasing; after a named format projection it
remains weaker than codebook find.”
