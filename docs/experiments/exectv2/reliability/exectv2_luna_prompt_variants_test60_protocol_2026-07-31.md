# ExECTv2 Luna prompt-variant A/B/C test60 protocol

Date: 2026-07-31  
Status: complete; aggregate-only A/B/C test60 panel finalized 2026-07-31  
Readout: aggregate-only  
Report: [test60 panel](exectv2_luna_prompt_variants_test60_2026-07-31.md)  
Parent development panel:
[dev140 A/B/C](exectv2_luna_prompt_variants_dev140_protocol_2026-07-31.md)

## Primary question

For GPT-5.6 Luna alone on ExECTv2 `test60`, how do the frozen `v0.9.24`
control prompt and the two Luna development prompts compare on model-owned and
joint LLM-with-rules Seizure Frequency and overall `clinical_headline` scores
when the schema, joint repair, scorers, and split stay fixed?

This is a Luna-versus-Luna holdout transfer check for prompts studied on
`dev140`. It is not a six-model ranking and does not rewrite the frozen
`v0.9.24` six-model panel.

## Data, split, and row policy

- Dataset: ExECTv2; split `test60`; 59 loadable letters.
- Row policy: **aggregate-only**.
- The runner may read each note only to make the frozen call and score it.
- No test-row identifier, note, prediction, evidence, gold label, model-specific
  failure, or hard slice may be printed, copied, analyzed, or used to change a
  prompt, repair, scorer, or conclusion.
- Raw JSONL checkpoints remain sealed under ignored
  `scratch/holdout/exectv2_luna_prompt_variants_test60_20260731/`.
  Only aggregate metrics and sealed-artifact fingerprints may leave those roots.

## Fixed conditions

- Model: `openai/gpt-5.6-luna`
- Temperature: `1` (match sealed Luna test60 and the `dev140` A/B/C study)
- Max tokens: `16000` for the structured ledger
- Cache: disabled
- Architecture: decision 0040/0041 one-call
- Repair: Diagnosis/Prescription `default` / `default` (decision 0045; joint/combined archived)
  (`diagnosis_policy_variant=combined`,
  `prescription_policy_variant=combined`)
- Schema: frozen `v0.9.24` key-family event ledger contract
- Scores: overall and family `clinical_headline` F1; aggregate family-local
  letter-correct counts at model-owned and joint boundaries
- Output root:
  `scratch/holdout/exectv2_luna_prompt_variants_test60_20260731/`

## Variants

| ID | Prompt | Call mode |
| --- | --- | --- |
| A | `exectv2_hybrid_key_family_event_ledger_v0.9.24` | No-call reuse of sealed Luna test60 structured outputs; joint reassembly |
| B | `..._v0.9.25_luna_sf_state` | Fresh live calls; joint reassembly |
| C | `..._v0.9.25_luna_sf_boundary_dx` | Fresh live calls; joint reassembly |

A reuse source (sealed):

`scratch/holdout/exectv2_test60/gpt56luna/gpt56luna_structured.jsonl`

Note: the frozen six-model Luna test60 aggregate used Diagnosis/Prescription
`default` policy and reports overall F1 `0.7950`. Variant A in this study
reassembles the same saved raws under **joint** policy to match the `dev140`
A/B/C comparator. That joint A score may differ from `0.7950` and must not be
confused with the frozen panel cell.

## Launch gate

The development A/B/C `dev140` panel is complete. No prompt text may change
after this protocol is frozen. Test aggregates must not be used to choose
among B and C or to edit instructions.

## Required aggregate readout

For each variant retain only:

- rows completed;
- call failures and blocking parse/schema failures;
- overall and family joint `clinical_headline` F1;
- aggregate model-owned and joint family-local letter-correct counts;
- artifact path and SHA-256;
- prompt version and snapshot hash.

Do not retain or report row-level traces outside sealed holdout storage.

## Stop rule

- Complete each variant once under this frozen condition.
- Transport or resume defects may be repaired operationally without inspecting
  clinical failures.
- A prompt, schema, clinical-repair, normalization, or scorer change after
  seeing test aggregates rejects this protocol and starts a new candidate.
- Test aggregates must not be used to choose among B and C or to edit
  instructions.
- Do not promote into the frozen six-model panel from this transfer check alone.

## Claim boundary

Aggregate-only Luna-versus-Luna transfer evidence on `test60` for the named
prompts and joint repair stack. It does not establish clinical validation,
published-benchmark improvement, or a rewrite of the frozen six-model panel.
