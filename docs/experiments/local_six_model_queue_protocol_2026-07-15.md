# Local six-model queue protocol

Date: 2026-07-15

## Question and order

Complete the two local-model conditions without overlapping Ollama workloads.
Run Qwen 3.6:35B through ExECTv2 first, then Gemma 4 26B through ExECTv2,
then run the two Gan 2026 conditions. The fixed order is:

1. Qwen ExECT dev pilots (1, 5, 25), dev140, aggregate-only test60.
2. Gemma ExECT dev5, dev140, aggregate-only test60.
3. Qwen Gan validation5 gate, then test450 if the gate passes.
4. Gemma Gan validation5 gate, then test450 if the gate passes.

## Frozen conditions

- ExECT uses decisions 0040 and 0041, prompt
  `exectv2_hybrid_key_family_event_ledger_v0.9.24`, the manifest-defined splits,
  one structured call per letter, disabled DSPy cache, and the current fixed
  downstream lenses and scorer.
- Gan uses prompt `gan2026_hybrid_structured_events_v0.7`, pipeline
  `llm_with_rules`, temperature 0, one call per note, disabled DSPy cache, and
  the current fixed repair and Purist/Pragmatic scorers.
- Qwen route: `ollama_chat/qwen3.6:35b`, `think=false`, Q4_K_M.
- Gemma route: `ollama_chat/gemma4:26b`, `think=false`, Q4_K_M.
- Ollama endpoint: `http://localhost:11434`.

## Gates and row policy

An ExECT pilot must complete all requested rows without call or blocking parse
failure before the next stage starts. A Gan validation5 pilot must complete
5/5 calls and structured records with zero blocking parse/schema/label failure
and exact evidence for all five rows. A failed command stops the queue and no
later holdout command runs.

ExECT dev rows and Gan validation rows may be inspected for operational
diagnosis. ExECT test60 and Gan test450 are aggregate-only: do not print,
inspect, compare, or tune from row-level material. Sealed rows remain under
ignored `scratch/local_queue/`; only aggregate summaries may be promoted.

## Claim boundary

Successful runs are matched local-model evidence for the named fixed pipelines.
They are not clinical validation, a published ExECT reproduction, or a general
open-versus-closed model ranking. Provider, transport, hardware, and partial
offload differences remain visible.
