# Six-model final panel

Final ExECT and Gan results for the six selected models, including LLM only and
LLM with rules on development and locked holdout.

- Machine panel: [`panel_aggregate.json`](panel_aggregate.json)
- Report: [`docs/research/six_model_comparison_report_2026-07-18.md`](../../docs/research/six_model_comparison_report_2026-07-18.md)
- Rebuild: `python scripts/build_six_model_final_panel.py`

Holdout splits (`test60`, `test450`) are aggregate-only. Development splits
permit row review. Report primary scores to two decimal places. Do not treat
ExECT clinical fact F1 and Gan Purist as interchangeable.

Gan `llm_only` uses the matched v0.8 prompt on `dev750` and `test450`. Do not
mix historical `llm_with_rules` v0.7 validation with current-floors v0.5
`test450`. DeepSeek Gan `llm_only` `dev750` is still pre-0731 while `test450`
is 0731; that gap is provisional.
