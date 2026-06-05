# Gan 2026 H10 Raw Identity Sidecar v1

H10 provenance sidecar only. It makes no model calls, changes no predictions, writes no row-level output artifact, and uses no locked-test row-level failures.

## Decision

raw_identity_sidecar_ready

## Artifact Summaries

| Artifact | Rows | SHA-256 | Raw fields present |
| --- | ---: | --- | ---: |
| `experiments/gan2026_llm_replacement_postprocessing_ablation_validation250_v0_2026-06-02.jsonl` | 1000 | `915edbf34f236af779c795630054839dfcfaaaa4e45ab811e4ac233b4a42b909` | 0 |
| `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_conservative_live_2026-06-03.jsonl` | 750 | `91c4021e4ae0fd1727c38647b72e43e6adca7a6b0210446705753b2bc7c1dc68` | 750 |
| `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl` | 750 | `bcc883ba959543ec1350e6076380c7179b2bbe2484bd5d31d20d8ee9d16a99c4` | 750 |

## Paired Identity

Left: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_conservative_live_2026-06-03.jsonl`

Right: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl`

Matched rows: 750.

| Field | Present pairs | Identical pairs | Identity rate |
| --- | ---: | ---: | ---: |
| `raw_output` | 750 | 750 | 1.0000 |
| `llm_candidate_raw_output` | 750 | 750 | 1.0000 |
| `adjudicator_raw_output` | 750 | 750 | 1.0000 |

## Next Step

Use this sidecar as the H10 provenance prerequisite before boundary_event_contract_v1 and any later live/replay comparison.
