# Paper experiments

Tracked machine results for the paper comparison. Everyday dumps stay in
gitignored `experiments/`.

This is not a second evidence register. Claim wording stays in
`docs/canon/10_paper_provenance.md`. Living hybrid numbers are Decision 0050.
Rules-only peers are the E5 remasure. Replay procedure:
`docs/runbooks/current_stack_six_model_replay.md`.

| Path | What it is |
| --- | --- |
| `local_raws.json` | Inventory of Gemma 4 / Qwen 3.8 replayable raws |
| `current_stack/latest/fills.json` | Selected six-model hybrid fills |
| `current_stack/SOURCES.json` | Inventory for those fills |
| `current_stack/latest/panel_aggregate.json` | Panel companion |
| `exectv2_rules_only_campaign_e5_remeasure_20260815.json` | ExECT rules-only E5 headline |
| `exectv2_rules_only_four_family_clinical_headline_test60_20260815.json` | E5 test60 companion |
| `exectv2_compact_ledger/gemma4_26b/` | Gemma Compact remasure, both splits, raw and hybrid |
| `gan2026_hybrid_structured_events_v0.5/` | Gemma and Qwen 3.8 Gan hybrid v0.5 raws |
| `gan2026_llm_only_canonical_pipeline_v0.8/` | Gemma Gan LLM-only v0.8 raws |

Holdout raws are stripped to replay keys only (`source_row_index` or
`letter_id`, `prompt_version`, `raw_output`). Do not inspect `test450`
or `test60` rows.

Still missing, still to run:

- Qwen 3.8 Compact (`dev140`, then aggregate-only `test60`)
- Qwen 3.8 Gan `gan2026_llm_only_canonical_pipeline_v0.8` (`dev750` and `test450`)
