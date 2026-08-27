# Luna `dev750` test of the Gan `final` prompt

Date: 2026-08-15
Status: complete
Protocol: recovered from git history; living owner is [Decision 0053](../../decisions/0053-gan-structured-events-final-prompt.md).
Decision: [0053](../../decisions/0053-gan-structured-events-final-prompt.md)
Model: `openai/gpt-5.6-luna`
Sample: all 750 Gan `dev750` rows; `test450` not touched

## Verdict

**not a large drop.** Hybrid Purist **660/750 vs 663/750 (−3)**. The
predeclared stop bar was −15/750. Treat this as temperature-1 noise.
Decision 0043 / 0050 fills and `operational/gan.py` stay on `v0.5`.
`test450` and the other five models stay closed.

This is not a promotion and not a selected-fill rewrite.

## Conditions

| Item | Value |
| :--- | :--- |
| Control | `mixed_reuse_and_live` `gan2026_hybrid_structured_events_v0.5` |
| Control source | `experiments/gan2026_structured_prompt_final_luna_dev20_20260815/v05_control/validation20.rows.jsonl` |
| Control reused / live | 20 / 730 |
| Candidate | `mixed_reuse_and_live` `gan2026_hybrid_structured_events_final` |
| Candidate reuse source | `experiments/gan2026_structured_prompt_final_luna_dev20_20260815/final_live/validation20.rows.jsonl` |
| Candidate reused / live | 20 / 730 |
| Repair | `hybrid_full_stack` |
| Scorer | Gan Purist primary; Pragmatic secondary |
| Gold at prompt-build time | forbidden |
| Holdout | not touched |
| `final` contract SHA-256 | `171d15bc6d3c2fb178e5ba0d713e75d008d31aceabe25d0163e0c8457a9ebb1d` |

## Counts on the 750-row pool

| Surface | v0.5 | final | delta |
| :--- | ---: | ---: | ---: |
| raw Purist | 663/750 | 660/750 | -3 |
| raw Pragmatic | 684/750 | 679/750 | -5 |
| hybrid Purist | 663/750 | 660/750 | -3 |
| hybrid Pragmatic | 684/750 | 679/750 | -5 |

Call failures: v0.5 0, final 0.
Parse failures: v0.5 0, final 7.

## Hybrid Purist by gold-kind pool

| Kind | n | v0.5 | final | delta |
| :--- | ---: | ---: | ---: | ---: |
| cluster | 72 | 57 | 55 | -2 |
| frequency | 404 | 355 | 351 | -4 |
| no_reference | 27 | 27 | 27 | +0 |
| seizure_free | 112 | 105 | 106 | +1 |
| unknown | 92 | 79 | 80 | +1 |
| unresolved_multiple | 43 | 40 | 41 | +1 |

## Hybrid Purist flips

- `180` (frequency): v0.5 True → final False
- `763` (frequency): v0.5 True → final False
- `2023` (frequency): v0.5 True → final False
- `2548` (frequency): v0.5 True → final False
- `2907` (seizure_free): v0.5 False → final True
- `3015` (seizure_free): v0.5 True → final False
- `4337` (frequency): v0.5 False → final True
- `4631` (frequency): v0.5 False → final True
- `5406` (seizure_free): v0.5 False → final True
- `5827` (unresolved_multiple): v0.5 False → final True
- `8805` (seizure_free): v0.5 True → final False
- `9002` (frequency): v0.5 True → final False
- `9250` (seizure_free): v0.5 True → final False
- `10003` (cluster): v0.5 True → final False
- `10386` (cluster): v0.5 True → final False
- `10517` (cluster): v0.5 False → final True
- `10942` (cluster): v0.5 False → final True
- `10996` (cluster): v0.5 True → final False
- `12751` (frequency): v0.5 True → final False
- `13627` (frequency): v0.5 False → final True
- `13711` (frequency): v0.5 True → final False
- `13843` (seizure_free): v0.5 False → final True
- `13858` (seizure_free): v0.5 False → final True
- `13922` (unknown): v0.5 False → final True
- `14383` (frequency): v0.5 True → final False
- `14645` (frequency): v0.5 False → final True
- `14765` (frequency): v0.5 False → final True
- `15012` (frequency): v0.5 False → final True
- `15127` (frequency): v0.5 False → final True
- `15267` (frequency): v0.5 True → final False
- `15317` (frequency): v0.5 True → final False
- `15376` (cluster): v0.5 True → final False
- `15404` (cluster): v0.5 True → final False
- `15479` (cluster): v0.5 False → final True
- `15519` (cluster): v0.5 True → final False
- `15593` (cluster): v0.5 False → final True
- `15745` (frequency): v0.5 True → final False
- `15768` (frequency): v0.5 True → final False
- `15771` (frequency): v0.5 True → final False
- `15772` (frequency): v0.5 True → final False
- `16618` (frequency): v0.5 False → final True
- `16645` (frequency): v0.5 False → final True
- `16697` (frequency): v0.5 False → final True
- `16704` (frequency): v0.5 True → final False
- `16717` (frequency): v0.5 False → final True
- `16772` (frequency): v0.5 True → final False
- `16867` (frequency): v0.5 False → final True

## Boundary

Development only. Luna versus Luna. Envelope hygiene, not a prompt-policy study. Not a six-model ranking. Not holdout evidence. Not a selected-fill rewrite. Decision 0043 / 0050 fills stay on `v0.5`.
