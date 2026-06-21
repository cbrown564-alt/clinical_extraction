# Gan 2026 Qwen v0.6 Repairfix Frozen Test450 Aggregate Summary

Date: 2026-06-21

Claim language: frozen aggregate holdout result for a hybrid development artifact. This is not an LLM-first raw-Qwen score; same-raw validation attribution shows substantial deterministic repair contribution.

Inspection policy: aggregate summary only. Test450 row-level failures, rationales, evidence, selected events, transitions, and correctness were not inspected for development.

## Candidate

- Pipeline: `hybrid_structured_events`
- Prompt/program version: `gan2026_hybrid_structured_events_v0.6`
- Model: `ollama_chat/qwen3.6:35b`
- Split manifest: `gan2026_split_v1`
- Split: `test`, 450 rows
- Temperature: `0.0`
- Max tokens: `2400`
- Repair mode: `hybrid_full_stack` with the 2026-06-21 Qwen repairfix code

## Aggregate Result

- Purist micro-F1 proxy / accuracy: `0.8133` (366 / 450)
- Pragmatic micro-F1 proxy / accuracy: `0.8467` (381 / 450)
- Structured records: 449 / 450
- Call failures after technical recovery: 0
- Parse/schema/label issues: 1
- JSON dialect repairs: 449
- Deterministic repair notes: 307
- Exact selection evidence substrings: 367 / 450

## Artifacts

- Test JSONL: `experiments\gan2026_v06_test450_hybrid_structured_events_qwen3635b_repairfix_technical_recovery_2026-06-21.jsonl`
- Test report: `experiments\gan2026_v06_test450_hybrid_structured_events_qwen3635b_repairfix_technical_recovery_2026-06-21.md` (contains row-level output; do not use for development tuning)
- Validation repair replay: `experiments\gan2026_v06_validation750_hybrid_structured_events_qwen3635b_replay_repairfix_2026-06-21.md`
- Validation attribution report: `experiments\gan2026_v06_validation750_qwen3635b_repairfix_attribution_2026-06-21.md`

## Decision

The requested `>0.8` Gan frequency Purist score on locked test450 is achieved: `0.8133` Purist micro-F1 proxy / accuracy. Because the result depends materially on deterministic repair, future claims should call this a hybrid repairfix candidate unless a separate attribution-clean LLM-first run is produced.
