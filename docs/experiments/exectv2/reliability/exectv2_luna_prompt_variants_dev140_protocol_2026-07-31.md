# ExECTv2 Luna prompt-variant A/B/C protocol

Date: 2026-07-31  
Status: complete; A/B/C `dev140` panel finalized 2026-07-31  
Report: [panel report](exectv2_luna_prompt_variants_dev140_2026-07-31.md)  
Parent evidence: [Luna residual map](exectv2_luna_single_call_dev140_residual_map_2026-07-31.md)  
Exemplar pack: [exemplar pack](exectv2_luna_prompt_variants_exemplar_pack_2026-07-31.md)  
Draft notes: [draft notes](exectv2_luna_prompt_variants_draft_notes_2026-07-31.md)

## Primary question

For GPT-5.6 Luna alone on ExECTv2 `dev140`, how much can plain-language prompt
change move **model-owned** and **joint LLM-with-rules** Seizure Frequency
(and secondary Diagnosis) letter correctness when the event schema, joint
bounded repair, scorers, and split stay frozen?

This is a Luna-versus-Luna development candidate. It is not a six-model
comparison and must not rewrite the frozen single-call panel in place.

## Why this study

The no-call residual map shows:

| Boundary | Overall F1 | SF F1 | SF letter wrongs | Dx letter wrongs |
| --- | ---: | ---: | ---: | ---: |
| Saved model-owned | — | — | 54 | 80 |
| Default final | 0.8832 | 0.7892 | 52 | 49 |
| Joint final | 0.9006 | 0.7892 | 52 | 39 |

SF barely moves under deterministic projection. Joint policy already fixes most
default Rx regressions and many Dx residuals. The remaining SF mass is
model-owned clinical state construction with exact evidence. That makes Luna a
cheap surface for testing whether prompt tuning still matters inside the fixed
one-call ExECT stack.

## Fixed conditions

- Dataset / split: ExECTv2 `dev140`; row-level analysis permitted.
- Locked split: `test60` remains aggregate-only and sealed. No row inspection,
  failure analysis, or prompt change from test60.
- Model: `openai/gpt-5.6-luna` only.
- Route and sampling: match the frozen Luna single-call condition (OpenAI chat,
  temperature `1`, structured max tokens `16000`, cache disabled) unless a
  provider constraint forces an explicit recorded change.
- Architecture: decision 0040 model-led families + decision 0041 single call.
- Schema: keep the `v0.9.24` key-family event ledger JSON contract unchanged.
- Repair: Diagnosis/Prescription `default` / `default` (decision 0045; joint/combined archived)
  (`diagnosis_policy_variant=combined`,
  `prescription_policy_variant=combined`) for the LLM-with-rules readout.
- Scorer: family-local `clinical_headline_unit_keys` primary for SF and Dx
  letter correctness; overall `clinical_headline` F1 secondary.
- Output root:
  `scratch/validation/exectv2_luna_prompt_variants_dev140_20260731/`.

## Three prompt variants

| ID | Prompt identity | Strategy | Residual target |
| --- | --- | --- | --- |
| A | `exectv2_hybrid_key_family_event_ledger_v0.9.24` | Frozen control | None; baseline |
| B | `exectv2_hybrid_key_family_event_ledger_v0.9.25_luna_sf_state` | SF competing-state and rate-set guidance | `sf_state_boundary`, `sf_rate_construction` |
| C | `exectv2_hybrid_key_family_event_ledger_v0.9.25_luna_sf_boundary_dx` | SF seizure-free/unknown boundaries plus light Dx specificity | `sf_state_boundary`, `dx_specificity` |

Variant A reuses the retained Luna single-call raw/structured outputs and
reassembles them under joint policy (no new calls). Variants B and C require
selectable prompt versions, prompt-contract snapshots, and live Luna calls.

Rules for B and C:

- Change model-facing instructions only.
- Do not change enum names, required fields, joint repair semantics,
  normalization, or scorers.
- Do not mix B and C into a kitchen-sink prompt until one variant wins its
  target slices without harming complementary slices.
- Do not retarget the frozen six-model panel prompt in place.
- Do not reopen rejected Diagnosis/Prescription residual-addition rule
  candidates as part of this study.

## Predeclared hard slices

Slices come from the Luna residual map. No fresh hard-slice generation run is
required to open drafting.

| Bundle | Themes / family | Approx. joint-final wrong letters (non-empty gold) |
| --- | --- | ---: |
| B target | `sf_state_boundary`, `sf_rate_construction` | ~40 SF |
| C target | `sf_state_boundary`, `dx_specificity` | ~40 SF + ~39 Dx |
| Explicit non-target | `rx_current_regimen`, `annotation_or_empty_gold` | scored for safety only |

Empty-gold SF letters remain diagnostic and are excluded from B/C win criteria.

## Drafting aid

- [exemplar pack](exectv2_luna_prompt_variants_exemplar_pack_2026-07-31.md)
- Machine exemplars:
  `experiments/exectv2_luna_single_call_dev140_residual_map_20260731/residual_exemplars.json`

After B and C are drafted, run `$plain-language-prompt-auditor` on the rendered
model-facing text before any Luna calls.

## Required readouts

For each variant, retain matched:

1. **Model-owned** family-local letter correctness and family F1 before joint
   repair.
2. **Joint LLM-with-rules** family-local letter correctness and family F1.
3. Exact selected-evidence rates.
4. Wrong-to-correct and correct-to-wrong transitions versus the model boundary.
5. Slice tables for B-target, C-target, Rx non-target, and empty-gold diagnostic
   bands.
6. Prompt snapshot hash and rendered payload identity.

Primary decision metrics:

- Model-owned SF letter correctness on full `dev140` (non-empty-gold SF subset
  as the hard slice).
- Model-owned SF letter correctness on the B-target theme bundle.
- Joint SF letter correctness and overall headline F1 as secondary safety
  readouts.
- For C only: joint Dx letter correctness as an additional secondary metric.

A variant is interesting only if the model-owned SF boundary improves on its
target bundle without a material off-target loss on complementary families.
Aggregate joint gain alone is not enough if the raw SF boundary does not move.

## Execution order

1. Keep A as the frozen Luna `v0.9.24` no-call joint reassembly baseline.
2. Implement selectable prompt identities for B and C with contract snapshots;
   default `PROMPT_VERSION` remains `v0.9.24`.
3. Draft B from the SF competing-state / rate exemplars; plain-language audit.
4. Draft C from the SF boundary and Dx specificity exemplars; plain-language
   audit.
5. Optional cheap pilot: stratified hard subset before full 140, only if the
   pilot rows and stop rule are recorded first.
6. Run B and C on full `dev140` with cache disabled.
7. Build the machine comparison artifact before the narrative report.
8. Only if development wins on the primary SF metric, consider aggregate-only
   `test60` under a separate holdout protocol. Do not inspect sealed rows.

## Stop rule

- **Answer:** B or C improves Luna model-owned SF letter correctness on its
  target bundle and does not worsen complementary slices enough to cancel the
  gain; report the matched joint effect.
- **Negative:** neither B nor C moves model-owned SF beyond noise on its target
  bundle.
- **Revise once:** if a draft fails only from clear instruction ambiguity found
  in permitted development rows, allow one redraft per variant.
- **Reject:** any change that alters schema enums, joint repair semantics,
  scorers, or inspects `test60`.
- Do not promote a Luna-tuned prompt into the frozen six-model panel from this
  study alone.
- Do not open a new Dx/Rx residual-addition rule study from a negative prompt
  result without a separate predeclaration.

## Required artifact

Retain a machine comparison with:

- schema version `exectv2.luna_prompt_variants_dev140.v1`;
- one row per letter per variant;
- prompt version and snapshot hash;
- model-owned and joint-final family keys for all four families;
- family-local correctness flags;
- evidence grade;
- theme / slice membership;
- claim boundary string.

Narrative report path:

`docs/experiments/exectv2/reliability/exectv2_luna_prompt_variants_dev140_2026-07-31.md`

## Claim boundary

Development evidence for Luna prompt sensitivity under a frozen ExECT schema
and joint bounded repair stack. It may support a bounded claim that prompt
tuning still moves model-owned and/or joint answers for this model and
distribution. It does not establish general model ranking, clinical validation,
holdout generalization, published-benchmark improvement, or replacement of the
frozen six-model panel.

## Next action

Panel complete. Aggregate-only `test60` transfer is complete under
[test60 protocol](exectv2_luna_prompt_variants_test60_protocol_2026-07-31.md).
Do not retarget the frozen six-model panel without a separate promotion study.
