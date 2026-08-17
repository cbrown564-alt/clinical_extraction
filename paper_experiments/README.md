# Paper experiments

Tracked machine results for the paper comparison. Everyday dumps stay in
gitignored `experiments/`.

This is not a second evidence register. Claim wording stays in
[`docs/paper/claims.md`](../docs/paper/claims.md). Compact is the
cited ExECT hybrid. The cleaned request is the cited Gan hybrid.
Full ledger is the ExECT control. Living roster:
[`roster.json`](roster.json). Cell inventory:
[`local_raws.json`](local_raws.json).

| Path | What it is |
| --- | --- |
| `roster.json` | Six living models and historical aliases |
| `local_raws.json` | Present and missing replayable cells |
| `exectv2_compact_ledger/{model}/{split}/` | Paper-cited ExECT hybrid and Compact raw, plus Full-ledger control |
| `current_stack/latest/fills.json` | Decision 0050 Full-ledger hybrid fills (control) |
| `exectv2_rules_only_campaign_e5_remeasure_20260815.json` | ExECT rules-only E5 headline |
| `exectv2_rules_only_four_family_clinical_headline_test60_20260815.json` | E5 test60 companion |
| `gan2026_hybrid_structured_events_v0.5/` | Gan hybrid v0.5 raws |
| `gan2026_llm_only_canonical_pipeline_v0.8/` | Gan LLM-only v0.8 raws |

Holdout raws are stripped to replay keys only (`source_row_index` or
`letter_id`, `prompt_version`, `raw_output`). Do not inspect `test450`
or `test60` rows.

Still missing, still to run:

- Qwen 3.8 Compact (`dev140`, then aggregate-only `test60`)
- Qwen 3.8 Gan `gan2026_llm_only_canonical_pipeline_v0.8` (`dev750` and `test450`)
- Cleaned Gan hybrid (`gan_llm_with_rules`) six-model panel
