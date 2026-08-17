# Current-stack hybrid fills

Decision 0050 Full-ledger control for six-model `llm_with_rules`
no-call scores. Compact ledger is the paper-cited ExECT hybrid
([Decision 0058](../../docs/decisions/0058-compact-ledger-is-the-paper-cited-exect-hybrid.md)).
This copy is the tracked paper tree under `paper_experiments/`.

- Inventory: [`SOURCES.json`](SOURCES.json)
- Numbers: [`latest/fills.json`](latest/fills.json)
- Procedure: [`docs/runbooks/current_stack_six_model_replay.md`](../../../docs/runbooks/current_stack_six_model_replay.md)
- Policy: [Decision 0050](../../../docs/decisions/0050-current-stack-hybrid-primary-fills.md)

Holdout raw sidecars stay in local `experiments/current_stack/sidecars/`.
Do not put letter IDs or note text in `latest/`. Dated copies live under `runs/`.
