# ExECT mention-unit v2 — GPT-5.6 Luna `dev20`

Date: 2026-08-16  
Status: complete; **answer**  
Protocol: [mention_unit_v2_fork_a_luna_dev20_protocol_2026-08-16.md](mention_unit_v2_fork_a_luna_dev20_protocol_2026-08-16.md)  
Review: [prompt fundamentals](../../plans/exect_prompt_fundamentals_2026-08-16.md)  
Plan: [ExECT LLM representation and hybrid re-evaluation](../../plans/exect_llm_representation_and_hybrid_revaluation_2026-08-16.md)  
Decision: [0055](../../decisions/0055-exect-semantic-inventory-and-method-contracts.md)  
Prior result: [mention-unit v1 (mention-unit v1 pruned; recover from Git history)

## Executive result

The signed-off clinical-name language put gold SeizureFrequency wording
into `clinical_name`. Exact SF wording rose from 12/32 on mention-unit
v1 `llm` to **24/32**. Hybrid exact rose from 4/32 to **26/32**. Empty-gold
SF extras did not rise (v1 `llm` 6 → v2 `llm` 5). Stop checks are
**mechanically_clean**. The result is an **answer** on this development
pool. Decision 0050 is unchanged. Do not promote. Do not inspect
`test60`. The later `dev140` transfer is a **revise**:
[report](mention_unit_v2_fork_a_luna_dev140_2026-08-16.md).

Headline F1 is context only. Mention-unit v2 `llm` is **0.7667** and
hybrid is **0.6460**, versus v1 **0.6234** / **0.6301** and control
hybrid **0.9251**. The headline move follows the wording copy: leftover
numbers now sit in `llm` fields instead of inside the name.

## Valid evidence

- 20 frozen development letters; `test60` not inspected.
- 40 fresh candidate calls: 20 `llm` and 20 `llm_with_rules`.
- Model `openai/gpt-5.6-luna`, temperature 1.0, 2400 tokens, cache off.
- Prompt `exectv2_mention_unit_v2`. Seven selection cues. Form table on
  `llm` only, including `period_count`. Landed encoder on hybrid
  `clinical_name` + `evidence`. No List 2 / List 9 / List 11. No
  “named type not generic.” No “current” on Diagnosis, SeizureFrequency,
  or Investigations.
- Fixed comparators: saved `v0.9.24` replay; saved mention-unit v1 raws;
  default v4 on the saved fork-A `dev20` raws; `trust_item`
  rematerialization of those same v4 raws.
- 0 blocking parse rows. 0 forbidden hybrid fields. 0 ECG or other
  non-target mentions. 0 hybrid mentions grown from unused letter text.

Artifact: [`comparison.json`](../../../experiments/exectv2_mention_unit_v2_luna_dev20_20260816/comparison.json)  
Rows: [`rows.jsonl`](../../../experiments/exectv2_mention_unit_v2_luna_dev20_20260816/rows.jsonl)  
Emission: [`emission_census.json`](../../../experiments/exectv2_mention_unit_v2_luna_dev20_20260816/emission_census.json)

## Gold wording as clinical name

Primary question: does gold SeizureFrequency wording appear as
`clinical_name`, and do empty-gold extras stay down?

| Family | Gold units | v1 `llm` exact / read | v2 `llm` exact / read | v2 hybrid exact / read |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 58 | 28 / 51 | 40 / 56 | 35 / 56 |
| SeizureFrequency | 32 | 12 / 31 | 24 / 31 | 26 / 31 |
| Prescription | 35 | 13 / 26 | 11 / 15 | 11 / 12 |
| Investigations | 17 | 4 / 16 | 8 / 8 | 7 / 7 |

v1 still wrote the sentence into `text`. v2 writes the name:
`focal seizures with altered awareness`, `seizures`, `absences`. The
“2 to 3” and the “week” go in `llm` fields. Hybrid leftover words stay
in evidence; the landed encoder recovers last-event zero and “every 3
weeks” from that evidence.

The leftover exact SF misses are name-form, not unread letters:

- EA0009 `cluster-of-seizures` is still unread. That leftover was
  deferred. Do not retune this prompt for that one letter.
- EA0154 gold `seizure` versus emitted `seizures`.
- EA0008 gold `seizure` is inside the typed rate row, not a second name.
- EA0011 gold `convulsive-seizure` sits inside `Focal to bilateral
  convulsive seizures`.
- EA0047 gold `absences` was bundled as `absences and jerks` on `llm`.

Prescription and Investigations “unread” counts fall because gold
stores the whole regimen or `MRI-2012-normal`, while `clinical_name` is
the drug or MRI / CT / EEG. That is the job. It is not a new miss of
those units.

## Stop rules

| Check | Result |
| --- | --- |
| Empty-gold SF extras versus v1 / v4 / trust-item | Did not rise. v2 `llm` 5 mentions (v1 6; v4 / trust-item 2). Hybrid stayed at 3. Letters remain EA0016 and EA0074. |
| ECG or other non-targets | None |
| Hybrid growth from unused letter text | None |

EA0016 still has no gold SF units. The model listed a December focal
seizure, one seizure, and historical seizures. Cue 1 plus cue 5 is the
bound: empty-gold extras cannot be prompted away.

The deferred leftovers were left alone: bundled drugs, intervening-word
counts, and the EA0015 EEG Unknown extra.

## Headline context

| Method | Headline | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| Control hybrid | 0.9251 | 0.9041 | 0.9231 | 0.9412 | 0.9412 |
| Control `llm` | 0.8987 | 0.8493 | 0.9434 | 0.8955 | 0.9412 |
| v1 `llm` | 0.6234 | 0.6488 | 0.1613 | 0.8615 | 0.9143 |
| v1 hybrid | 0.6301 | 0.6535 | 0.0357 | 0.9412 | 0.9412 |
| v2 `llm` | 0.7667 | 0.6910 | 0.6061 | 0.9062 | 0.9143 |
| v2 hybrid | 0.6460 | 0.8437 | 0.3934 | 0.8182 | 0.4000 |

`llm` SF headline rises because `period_count` and the other form
fields now have a home. Hybrid SF stays lower: leftover words in
evidence are expected, and this study did not retune the landed
encoder. Hybrid Investigations also drop versus v1 because the encoder
path is item-local and the name is now `EEG`, not a result-bearing
clause.

## Decision

**answer.** The one knob — this language — copies gold SeizureFrequency
wording as `clinical_name` on this pool and does not raise empty-gold
extras versus mention-unit v1. A score that still left the wording
inside a sentence would have been a negative result. That is not what
happened.

This is a development-method answer. It is not transfer evidence, not
clinical validation, and not a Decision 0050 change. Do not promote.
Do not start Fork B from this result. Empty-gold extras and the one
unread EA0009 unit are not, by themselves, a reason to teach Markup.

## Next

The frozen-language `dev140` transfer is a **revise**: wording still
copies; empty-gold extras rose. Do not retune this prompt. Owner:
[dev140 report](mention_unit_v2_fork_a_luna_dev140_2026-08-16.md).

## Claim boundary

GPT-5.6 Luna ExECT development result on the named `dev20` sample. It
is not clinical validation, not holdout evidence, and not a Decision
0050 change.
