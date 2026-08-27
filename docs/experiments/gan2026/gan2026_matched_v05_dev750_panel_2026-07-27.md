# Gan 2026 matched v0.5 six-model dev750 panel

Generated: 2026-07-28T15:33:19.381860+00:00

Development evidence on `validation750`; the prompt, repair policy, scorers, and split are the frozen protocol values.

## Results

| Model | Rows | Purist | Pragmatic | Raw boundary | Exact evidence | Grounded evidence | W→C | C→W | Rules-correct regressions | Calls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| gpt41mini | 750 | 668/750 | 686/750 | 359/750 | 692/750 | 703/750 | 314 | 5 | 69 | 0 |
| gpt56luna | 750 | 646/750 | 671/750 | 411/750 | 744/750 | 745/750 | 240 | 5 | 91 | 0 |
| gpt56sol | 750 | 656/750 | 678/750 | 345/750 | 749/750 | 749/750 | 317 | 6 | 78 | 0 |
| deepseek_v4_flash | 750 | 619/750 | 641/750 | 449/750 | 728/750 | 736/750 | 174 | 4 | 114 | 0 |
| qwen36_35b | 750 | 660/750 | 680/750 | 325/750 | 567/750 | 661/750 | 339 | 4 | 75 | 0 |
| gemma4_26b | 750 | 643/750 | 676/750 | 425/750 | 734/750 | 734/750 | 223 | 5 | 87 | 0 |

## Attribution

The raw model boundary, format repair, deterministic semantic repair, final label, evidence grade, rules-control comparison, first failure, and clinical subproblem are retained per row in the companion artifact.

## Provenance

- `gpt41mini`: `saved_raw_output_no_call`; 0 resumed existing rows and 750 fresh rows in the retained artifact; `ef6651fcd35ae0243a30f5a968097b07b6dfe064a477f5a2b3dee2d18af6505f`.
- `gpt56luna`: `fresh_with_declared_resume_if_applicable`; 0 resumed existing rows and 750 fresh rows in the retained artifact; `4984f81e91c60c4379cf1e878b50cef01ce952b27295129b05ee7813f974a300`.
- `gpt56sol`: `fresh_with_declared_resume_if_applicable`; 0 resumed existing rows and 750 fresh rows in the retained artifact; `6c2f2d1b6357e6ccebc9919255adbedceac594959990475aa315a7ea9bc52be7`.
- `deepseek_v4_flash`: `fresh_resume_across_sessions`; 350 resumed existing rows and 400 fresh rows in the retained artifact; controller event `shell_controller_timeout_child_survived`; `88ebf9b6f59489d23eed5592698f1ed8b7460b8170bfcf2e20ccb8a7694eaaad`.
- `qwen36_35b`: `fresh_resume_across_sessions`; 45 resumed existing rows and 705 fresh rows in the retained artifact; `db7ff4fafdccacbfc53de93098864547234549b0f0643f18b4a01674896ccb4c`.
- `gemma4_26b`: `fresh_resume_across_sessions`; 395 resumed existing rows and 355 fresh rows in the retained artifact; `78b454ce184c7295e3b420789d9e04b57dcedfbf7e490b9319b551bcbabb7336`.

## Claim boundary

Development evidence for the named models, routes, v0.5 prompt, the then-
current `hybrid_full_stack` repair, Gan scorers, and validation750
distribution; not clinical validation, a model-neutral ranking, or new holdout
evidence.

**Note (2026-07-31):** This panel remains the historical row-trace and
attribution owner under the prior repair. The Gan LLM-with-rules ruleset is
now finalized with additional floors/guards; current LLM-with-rules scores are
no-call replays through that final ruleset. See
[six-model comparison](../../research/shared/six_model_comparison_report_2026-07-18.md)
and
[final-ruleset replay](../../../experiments/gan2026_six_model_current_floors_replay_20260731/replay_summary.json).
