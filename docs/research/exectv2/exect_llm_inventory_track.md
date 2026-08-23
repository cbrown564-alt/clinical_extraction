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

Latest Gemini 3.7 Flash inventory F1. `dev140`: extract **0.8273**,
inventory Select **0.8877**. Aggregate-only `test60`: extract
**0.8491**, inventory Select **0.8674**. Later-stage encode is
**0.8598** / **0.8649**; inventory Select after encode is **0.8585**
/ **0.8636**; later-stage LLM select is **0.8527** / **0.853**.
Cited five-cell owner:
[cell 4](exect_rule_select_after_llm_encode_2026-08-22.md). Protocol:
[inventory Select replay](exect_inventory_select_replay_protocol_2026-08-23.md).
