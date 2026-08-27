# Gemini 3.7 Flash ExECT LLM-only raw-lane confirmation

Date: 2026-08-14
Status: **complete — already on disk; no new calls**
Protocol: recovered from git history; this report is the answer.
Artifact: [`experiments/exectv2_gemini37flash_llm_only_raw_lane_20260814.json`](../../experiments/exectv2_gemini37flash_llm_only_raw_lane_20260814.json)

## Plain answer

Gemini LLM-only was not missing a live run. Gan already has successor
`llm` cells. ExECT has no second call: Decision 0046 LLM-only is the
`raw_lane_score` of the existing one-call packages.

| Cell | Gemini LLM-only | Source |
| --- | ---: | --- |
| Gan `dev750` Purist | **578/750 (0.7707)** | live 13 Aug v0.8 |
| Gan `test450` Purist | **319/450 (0.7089)** | live 13 Aug, aggregate-only |
| ExECT `dev140` raw lane | **0.8444** | one-call assembly |
| ExECT `test60` raw lane | **0.82** | holdout aggregate |

Sol remains the paper LLM-only row: Gan `test450` **335/450**, ExECT
`dev140` **0.8097**, `test60` **0.7771**. Hybrid fills stay Decision
0050 / 0052.

## What was run today

No model calls. Confirmed the Gan summary and the two ExECT raw-lane
owners. A HEAD reconstruction of sidecar `structured_events` scored
0.8566 / 0.8263 and is **not selected**. Frozen generation-time
identities stay, the same way Sol's 0.8097 / 0.7771 stay.

No holdout rows inspected.

## Claim boundary

Successor-roster `llm` evidence. Not a rewrite of Decision 0046 Sol
identity, Decision 0050 / 0052 hybrid fills, or GPT-4.1-mini scores.
