# ExECT mention-unit v2 — GPT-5.6 Luna `dev140`

Date: 2026-08-16  
Status: complete; **revise**  
Protocol: [mention_unit_v2_fork_a_luna_dev140_protocol_2026-08-16.md](mention_unit_v2_fork_a_luna_dev140_protocol_2026-08-16.md)  
Prior: [mention-unit v2 `dev20`](mention_unit_v2_fork_a_luna_dev20_2026-08-16.md)  
Review: [prompt fundamentals](../../plans/exect_prompt_fundamentals_2026-08-16.md)  
Decision: [0055](../../decisions/0055-exect-semantic-inventory-and-method-contracts.md)

## Executive result

The frozen clinical-name language still copies gold SeizureFrequency
wording as `clinical_name` on the 140 development letters: **131/187**
exact on `llm` versus **0/187** on default v4. The predeclared stop
rule still fired. Empty-gold SF extras rose versus v4 and trust-item
(53 versus 38 / 30 on `llm`). The result is **revise**. Decision 0050
is unchanged. Do not retune the prompt. Do not promote. Do not inspect
`test60`.

Headline F1 is context only. Mention-unit v2 `llm` is **0.7340** and
hybrid is **0.6255**, versus control hybrid **0.9020** and v4 **0.6694**
/ **0.6292**. The overlapping 20 letters did not raise extras versus
saved mention-unit v1.

## Valid evidence

- 140 development letters; `test60` not inspected.
- 280 fresh candidate calls. Prompt `exectv2_mention_unit_v2` unchanged
  from the `dev20` answer. Landed encoder unchanged.
- Model `openai/gpt-5.6-luna`, temperature 1.0, 2400 tokens, cache off.
- Fixed comparators: saved `v0.9.24` replay; saved mention-unit v1 on
  the overlapping 20 only; default v4 and `trust_item` rematerialized
  from the saved v4 `dev140` raws.
- 0 blocking parse rows. 0 forbidden hybrid fields. 0 ECG or other
  non-target mentions.

Artifact: [`comparison.json`](../../../experiments/exectv2_mention_unit_v2_luna_dev140_20260816/comparison.json)  
Rows: [`rows.jsonl`](../../../experiments/exectv2_mention_unit_v2_luna_dev140_20260816/rows.jsonl)  
Emission: [`emission_census.json`](../../../experiments/exectv2_mention_unit_v2_luna_dev140_20260816/emission_census.json)

## Gold wording as clinical name

| Family | Gold units | v4 `llm` exact / read | v2 `llm` exact / read | v2 hybrid exact / read |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 405 | 0 / 360 | 257 / 371 | 256 / 369 |
| SeizureFrequency | 187 | 0 / 168 | 131 / 173 | 115 / 174 |
| Prescription | 206 | 0 / 74 | 60 / 75 | 69 / 72 |
| Investigations | 136 | 0 / 119 | 99 / 99 | 99 / 99 |

The `dev20` mechanism held: the model writes the name, not the
sentence. Fourteen SF gold units stay unread. Two of those are
`cluster-of-seizures` (EA0009, EA0135). Several others are gold
hyphenation leftovers (`seizure-free`, `typical-absen`, `ysrue-free`).
Do not retune for those.

## Stop rules

| Check | Result |
| --- | --- |
| Empty-gold SF extras versus v4 / trust-item on 140 | **Rose.** `llm` 53 mentions (v4 38; trust-item 30). Hybrid 49 (v4 29; trust-item 27). |
| Empty-gold SF extras versus v1 on the overlapping 20 | Did not rise. New `llm` calls 3 versus saved v1 6. |
| ECG or other non-targets | None |
| Hybrid growth from unused letter text | Detector flagged EA0102 `epilim` and EA0152 `carbamazepine`. Both are spelling rewrites of emitted `Eplim` / `Carbamazapine`, not new units from unused letter text. |

The binding stop is the extras rise. Prompt fundamentals already said
empty-gold extras cannot be prompted away. On 140 that leftover is
large enough to block a transfer answer.

## Headline context

| Method | Headline | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| Control hybrid | 0.9020 | 0.8995 | 0.8291 | 0.9505 | 0.9202 |
| v4 `llm` | 0.6694 | 0.6901 | 0.4412 | 0.7826 | 0.7511 |
| trust-item `llm` | 0.7356 | 0.7317 | 0.5134 | 0.7826 | 0.9124 |
| v2 `llm` | 0.7340 | 0.6750 | 0.6225 | 0.8182 | 0.9027 |
| v2 hybrid | 0.6255 | 0.7569 | 0.3167 | 0.8389 | 0.4788 |

`llm` SF headline sits above v4 and trust-item because the name and
the form fields now have a home. Hybrid SF and Investigations stay
lower: leftover words in evidence are expected, and this study did not
retune the encoder.

## Decision

**revise.** The language still names the scored unit on this
distribution. It does not keep empty-gold SeizureFrequency extras down
versus the saved v4 / trust-item baselines. That is a development
transfer leftover, not a reason to invent a new metaphor or dump the
codebook.

Do not start mention-unit v3 from this extras rise. Do not start Fork
B. Do not promote. A later study that wants extras down needs a
different question than “copy the clinical name.”

## Next

The extras catalog is an **answer**. The hybrid encoder catalog is
an **answer**: names stay; counts and investigation results do not.
Owners:
[extras catalog](mention_unit_v2_empty_gold_sf_extras_luna_dev140_2026-08-16.md),
[hybrid encoder](mention_unit_v2_hybrid_encoder_damage_luna_dev140_2026-08-16.md).
Leave this language frozen. Do not retune for EA0009 or empty-gold
extras.

## Claim boundary

GPT-5.6 Luna ExECT development-transfer result on the named `dev140`
sample. It is not clinical validation, not holdout evidence, and not a
Decision 0050 change.
