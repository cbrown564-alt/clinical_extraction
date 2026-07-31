# ExECTv2 Luna single-call `dev140` residual map

Date: 2026-07-31  
Status: development mechanism answer  
Protocol: [residual map protocol](exectv2_luna_single_call_dev140_residual_map_protocol_2026-07-31.md)

## Answer

GPT-5.6 Luna’s remaining ExECT errors are dominated by **model-owned clinical
selection with exact evidence**, not by missing quotes. Under the selected
joint Diagnosis/Prescription policy, Seizure Frequency stays at family F1
`0.7892` with **52** family-local wrong letters; deterministic SF projection
barely moves the letter-correctness census (**54 → 52**). Diagnosis and
Prescription still benefit from joint rules (`0.8910 → 0.9086` and
`0.9250 → 0.9679`), so Rx/Dx residual-addition tuning is the wrong next lever.
The prompt-addressable mass is SF state construction plus remaining Dx
specificity misses.

Machine artifacts:
`experiments/exectv2_luna_single_call_dev140_residual_map_20260731/`.

## Protocol and boundary

- Dataset: ExECTv2 `dev140` (140 letters); row inspection permitted.
- Model: GPT-5.6 Luna saved single-call producers only; **zero new model calls**.
- Prompt of the saved producers: `exectv2_hybrid_key_family_event_ledger_v0.9.24`.
- Scorer: family-local `clinical_headline_unit_keys`; headline F1 secondary.
- Policies compared: retained `default` assembly versus joint
  (`diagnosis=combined`, `prescription=combined`).
- `test60` was not inspected.

## Score ladder

| Stage | Overall | Diagnosis | SF | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| Model-owned (letter wrongs) | — | 80 wrong | 54 wrong | 13 wrong | 15 wrong |
| Default final F1 | 0.8832 | 0.8910 | 0.7892 | 0.9250 | 0.9202 |
| Joint final F1 | 0.9006 | 0.9086 | 0.7892 | 0.9679 | 0.9202 |
| Default final letter wrongs | 140 | 49 | 52 | 24 | 15 |
| Joint final letter wrongs | 116 | 39 | 52 | 10 | 15 |

Default deterministic changes across families: **45** wrong→correct, **23**
correct→wrong, **30** changed-still-wrong. Joint versus default on the same
raws: **26** wrong→correct, **2** correct→wrong, **6** changed-still-wrong.
Exact evidence remains high among wrongs (typically ≥90% of wrong letters).

## Mechanism by family

### Seizure Frequency — prompt primary

SF is Luna’s weakest family and almost entirely model-owned. Of **40**
joint-final wrong letters with non-empty gold:

- gold often mixes `active-rate` with `unknown`, or expects `seizure-free`
  alone;
- predictions commonly emit competing `active-rate` + `seizure-free`, drop
  required `unknown`, or attach the wrong concept/CUI to a stated rate;
- **0** of those 40 are model-owned correct and then ruined by rules.

Theme labels on default-final SF wrongs: **35** `sf_state_boundary`, **5**
`sf_rate_construction`, plus **12** empty-gold diagnostics that must not drive
prompt success criteria.

### Diagnosis — prompt secondary / measured

Joint policy already rescues many default Dx residuals (**49 → 39** letter
wrongs). The remaining **39** joint wrongs are still mostly model-owned
(**38**) with exact evidence: missing syndrome labels, over-broad `epilepsy`,
or extra phenotype mentions. Prompt guidance can try specificity, but Dx/Rx
**rule** residual addition remains closed.

### Prescription — rules, not prompt

Default assembly **regresses** Luna Rx letter correctness (**13 → 24** wrong).
Joint recovers to **10** wrong. Treat Rx as a fixed-policy column in the prompt
study, not a B/C success slice.

### Investigations — thin

**15** wrong letters; unchanged by joint. Not a prompt driver.

## Prompt-seed estimate

Among default-final wrongs, analyst themes mark **89** letters in
`sf_rate_construction`, `sf_state_boundary`, or `dx_specificity`. Under joint
(the intended fixed repair), the non-empty-gold seed mass is about **40 SF +
39 Dx**. Empty-gold wrongs (**15** default / **13** joint-ish SF empty band)
stay diagnostic only.

## Decision

Proceed to a Luna-only prompt A/B/C study on `dev140` with:

1. frozen schema `v0.9.24`;
2. fixed joint bounded repair;
3. variant B targeting SF competing-state / rate construction;
4. variant C targeting SF seizure-free/unknown boundaries plus light Dx
   specificity;
5. no sealed `test60` tuning and no reopen of rejected Dx/Rx residual-addition
   rule candidates.

## Claim boundary

ExECTv2 `dev140` development mechanism evidence for GPT-5.6 Luna under the
named saved producers. Theme labels are analyst heuristics. Not holdout
evidence, clinical validation, published-benchmark improvement, or prompt
promotion into the frozen six-model panel.
