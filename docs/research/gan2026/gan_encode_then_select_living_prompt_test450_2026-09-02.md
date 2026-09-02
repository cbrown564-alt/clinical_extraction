# Results: Living-prompt encode-then-select on Gan `test450`

Date: 2026-09-02
Protocol: [protocol](gan_encode_then_select_living_prompt_test450_protocol_2026-09-02.md)
Artifact: [aggregates](gan_encode_then_select_living_prompt_test450_2026-09-02.json)
Split: `test450` aggregate-only. No row inspection.

## Answer

Gemini 3.7 Flash, temperature 0, living low thinking. OpenRouter
batch. No hybrid rule post-stack. Purist / Pragmatic micro-F1:

| Cell | Purist F1 | Pragmatic F1 |
| --- | ---: | ---: |
| Codebook encode | **0.68** (304/450) | **0.73** (327/450) |
| Codebook encode → living select | **0.86** (386/450) | **0.88** (394/450) |
| Source-near encode → living select | **0.79** (354/450) | **0.82** (368/450) |
| One-call find + encode + select | **0.87** (392/450) | **0.90** (404/450) |

Call failures **0**. Parse failures **0** on every cell.

Versus the predeclared comparators (Purist):

| Comparator | Stop | Δ vs codebook encode | Δ vs codebook select | Δ vs source-near select | Δ vs one-call |
| --- | ---: | ---: | ---: | ---: | ---: |
| Codebook find | 354 | −50 | +32 | 0 | +38 |
| Source-near find | 246 |  |  | +108 |  |
| Aug 21 source-near encode | 291 |  |  | +63 |  |
| Aug 21 old-prompt select | 320 |  | +66 | +34 | +72 |
| Cited cell 5 | 383 |  | +3 | −29 | +9 |
| Cited cell 3 | 387 |  | −1 | −33 | +5 |

Codebook encode repeats the `dev750` drop (0.78 → 0.69): find
**0.79** falls to encode **0.68**. Living select then recovers
to **0.86**, one Purist below cell 3 and three above cell 5.

Source-near living select is **0.79** (354): above old-prompt
select **0.71** and Aug 21 encode **0.65**, equal to codebook
find **354**, and well below cell 5.

The one-call extract stop is the highest of the four cells
(**0.87**). That is a holdout aggregate, not a Table 1 number.
The matching `dev750` cell is a separate protocol.

## Claim boundary

Holdout aggregate-only ablation. Not promoted. Not Table 1. Not
cell 5. No row-level rescue or harm table. Do not inspect holdout
rows. Do not retune from these stops.
