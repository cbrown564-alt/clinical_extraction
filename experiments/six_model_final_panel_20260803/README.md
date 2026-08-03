# Six-model final panel

Final ExECT and Gan results for the six selected models, including LLM only and
LLM with rules on locked holdout plus LLM-with-rules development side-by-side.

- Machine panel: [`panel_aggregate.json`](panel_aggregate.json)
- Report: [`docs/research/six_model_comparison_report_2026-07-18.md`](../../docs/research/six_model_comparison_report_2026-07-18.md)
- Rebuild: `python scripts/build_six_model_final_panel.py`

Holdout splits (`test60`, `test450`) are aggregate-only. Development splits
permit row review. Report primary scores to two decimal places. Do not treat
ExECT clinical fact F1 and Gan Purist as interchangeable.
