# ExECTv2 Luna single-call `dev140` residual map protocol

Date: 2026-07-31  
Status: complete; no-call development analysis  
Report: [residual map](exectv2_luna_single_call_dev140_residual_map_2026-07-31.md)  
Follow-on: [Luna prompt-variant A/B/C protocol](exectv2_luna_prompt_variants_dev140_protocol_2026-07-31.md)

## Primary question

On ExECTv2 `dev140`, under the fixed one-call architecture and saved GPT-5.6
Luna outputs, which family-local residuals remain after deterministic assembly,
and which of those are prompt-addressable clinical-selection errors versus
rule-owned or annotation-bound failures?

## Why this study

Gan Luna prompt variants moved a modest band of rows only after residual themes
were named from saved traces. ExECT already has a frozen Luna single-call
`dev140` panel and a selected joint bounded policy. Before paying for Luna
prompt A/B/C calls, this no-call map must:

1. separate model-owned wrongs from final wrongs by family;
2. mark exact-evidence status and first deterministic owner on changed rows;
3. compare default Diagnosis/Prescription policy with the selected joint
   bounded (`combined` / `combined`) reassembly;
4. seed prompt variants B/C from development exemplars without inspecting
   sealed `test60`.

## Fixed conditions

- Dataset / split: ExECTv2 `dev140`; row inspection permitted.
- Locked split: `test60` remains sealed and uninspected.
- Model: GPT-5.6 Luna (`openai/gpt-5.6-luna`) only.
- Architecture: decision 0040 model-led family ownership + decision 0041
  single-call comparison.
- Prompt identity of the saved producers:
  `exectv2_hybrid_key_family_event_ledger_v0.9.24`.
- Call mode: zero fresh model calls; local saved producers only.
- Scorer: family-local `clinical_headline_unit_keys` equality against
  family-local gold; overall `clinical_headline` F1 is secondary.
- Source producers:
  - Diagnosis / Prescription / Investigations:
    `experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715_structured.jsonl`
  - Seizure Frequency model-owned:
    `..._sf_structured_direct.jsonl`
  - Seizure Frequency final producer used by assembly:
    `..._sf_unknown_suppression.jsonl`
- Assembly config:
  `configs/exectv2/six_model_comparison/gpt56luna_dev140.json`
- Policy columns:
  - `default`: retained panel Diagnosis/Prescription policy
  - `joint`: `diagnosis_policy_variant=combined` and
    `prescription_policy_variant=combined`

## Method

1. Load the 140 manifest development letters.
2. Assemble twice from the same saved producers under `default` and `joint`.
3. For every letter × family, compare model-owned keys, default-final keys, and
   joint-final keys to family-local gold.
4. On key-changing rows, attach selected evidence grades, deterministic
   actions, mechanism groups, and first prediction-changing owner using the
   same classification helpers as the 2026-07-15 model-led regression study.
5. Theme final-wrong rows with coarse analyst labels for prompt seeding
   (`sf_rate_construction`, `sf_state_boundary`, `dx_specificity`,
   `rx_current_regimen`, `annotation_or_empty_gold`, `other`).
6. Emit machine panel, summary counts, and stratified exemplars.

## Required artifacts

Root: `experiments/exectv2_luna_single_call_dev140_residual_map_20260731/`

| File | Role |
| --- | --- |
| `residual_summary.json` | Counts, family ladders, policy deltas, theme buckets |
| `residual_panel.jsonl` | One row per letter × family |
| `residual_exemplars.json` | Stratified development seeds for prompt B/C |
| Narrative report under `docs/experiments/exectv2/reliability/` | Mechanism answer |

Schema identity: `exectv2.luna_single_call_dev140_residual_map.v1`

## Stop rule

- **Answer:** name dominant Luna residual mechanisms by family and mark which
  are prompt-addressable under frozen joint policy.
- **Negative:** saved producers cannot support matched model-owned versus final
  comparison.
- **Reject:** any sealed `test60` inspection, scorer change, or live model call.
- **Hand off:** if SF/Dx clinical-selection residuals dominate with exact
  evidence, draft the Luna A/B/C prompt protocol; if residuals are almost
  entirely known joint-policy or empty-gold annotation issues, stop without
  prompt calls.

## Claim boundary

ExECTv2 `dev140` development mechanism evidence for GPT-5.6 Luna under the
named saved producers and assembly policies. Theme labels are analyst
heuristics, not a new gold taxonomy. This does not establish holdout transfer,
clinical validity, published-benchmark improvement, or promotion of a new
prompt or ruleset.
