# Paper experiments

Tracked machine results for the paper comparison. Everyday dumps stay in
gitignored `experiments/`.

This is not a second evidence register. Claim wording stays in
`docs/canon/10_paper_provenance.md`. Living hybrid numbers are Decision 0050.
Rules-only peers are the E5 remasure. Replay procedure:
`docs/runbooks/current_stack_six_model_replay.md`.

| Path | What it is |
| --- | --- |
| `current_stack/latest/fills.json` | Selected six-model hybrid fills |
| `current_stack/SOURCES.json` | Inventory for those fills |
| `current_stack/latest/panel_aggregate.json` | Panel companion |
| `exectv2_rules_only_campaign_e5_remeasure_20260815.json` | ExECT rules-only E5 headline |
| `exectv2_rules_only_four_family_clinical_headline_test60_20260815.json` | E5 test60 companion |

Holdout raw sidecars are still local. The current-stack copies are Git LFS
pointers, not replayable JSONL, so they are not in this tree. Headline
no-call replay reads the JSON fills above and does not inspect holdout rows.
