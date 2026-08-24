# ExECT diagnostic inventory track

Date: 2026-08-23
Status: current
Owner: this file

`exect_llm_extract` (was `exect_llm_inventory`) is the living ExECT
cell-3 extract. The model-facing prompt is authored in
`prompt_inventory.py`. It asks for generic and specific diagnoses,
heading types, and frequency or control statements, including events
with no count. It is scored on unique Diagnosis concepts without
most-specific collapse (`clinical_inventory_unit_keys`). The older
Compact extract is `exect_llm_extract_filtered`, a Gemini ablation.

Select for this track is `StructuredMethodConfig.inventory()`, not the
paper Compact stack. Headline-tuned SeizureFrequency companion
collapses stay off: named-type identity, SF-to-Diagnosis invent,
umbrella-clone drop, generic-to-named rewrite, dated-cluster-next-to-free,
preceded-by-current-free, and unknown suppression. Two inventory-only
rules keep extract parent diagnoses and drop leftover event/episode/jerk
wording. Residual dictionary letter-scan adds remain an ablation only.

Cited primary metric: 4-family micro F1
(`clinical_inventory_unit_keys`). Retired Compact/headline collapse
(`clinical_headline_unit_keys`) is a Gemini ablation only.

Latest Gemini 3.7 Flash 4-family micro F1. Cited `test60` select stops:
rules **0.7725**; both-extract **0.8592**; inventory Select
**0.8674** (peak); inventory Select after encode **0.8636**;
later-stage LLM select **0.853**. `dev140`: extract **0.8273**,
inventory Select **0.8877**; both-extract **0.8884**; later-stage
encode **0.8598**; inventory Select after encode **0.8585**;
later-stage LLM select **0.8527**. Aggregate-only `test60` extract
**0.8491**; later-stage encode **0.8649**. Owners: cell 1–2
[cells 1–2](exect_four_family_micro_f1_cells_1_2_protocol_2026-08-23.md),
[both-extract](exect_both_extract_on_inventory_protocol_2026-08-23.md);
cells 3–5
[cells 3–5](exect_gemini_inventory_cells_3_5_protocol_2026-08-23.md),
[cell 4 result](exect_rule_select_after_llm_encode_2026-08-22.md).
Select replay:
[inventory Select replay](exect_inventory_select_replay_protocol_2026-08-23.md).
