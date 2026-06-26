# ExECTv2 Satellite 13 Phase 1 Active Scoreboard

Date: 2026-06-23

Status: active comparison table for the de-duplicated clinical-fact LLM-only
workstream. Superseded rich-schema iteration artifacts are archived under
`experiments/archive/` (see `experiments/archive/ARCHIVE_INDEX.md`).

## Claim Boundary

- This table is dev140 only.
- The primary optimization target is de-duplicated clinical recovery on
  `clinical_headline`, not strict full-schema benchmark reconstruction.
- Strict benchmark numbers remain diagnostic/comparability numbers and must be
  reported beside the de-duplicated surface.
- No row here is a full-200, holdout, locked-test, or paper-comparable benchmark
  claim.

## Comparison Table

| Candidate | Architecture | Model | Split | strict benchmark | de-dup `clinical_headline` overall | Diagnosis | SeizureFrequency | Prescription | Investigations | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `single_call_clean_render_ids` | LLM-only rich schema, one call, full ExECTv2 schema | GPT-4.1-mini | dev140 | 0.334 | 0.7114 | 0.6527 | 0.5507 | 0.8462 | 0.8627 | LLM-only rich-schema comparator; fixed canonical replay reproduced |
| `single_call_clean_render_ids` | LLM-only rich schema, one call, full ExECTv2 schema | Qwen-3.6 | dev140 | 0.339 | 0.7215 | 0.6726 | 0.5118 | 0.8386 | 0.9189 | LLM-only rich-schema comparator; fixed canonical replay reproduced |
| `holistic_finding_assembly_v08` | Full hybrid rich schema | GPT-4.1-mini-family lanes | dev140 | ~0.374 | 0.9155 | 0.9090 | 0.9053 | 0.9357 | 0.9132 | Hybrid performance control |
| `single_call_dedup_facts` v0.5 | LLM-only de-duplicated clinical facts, single prompt | GPT-4.1-mini | dev140 | 0.126 | 0.710 | 0.672 | 0.558 | 0.814 | 0.832 | Phase 3 single-prompt plateau; Phase 4 per-family fallback next |

## Live Artifact Pointers

- GPT-4.1-mini clean-render comparator:
  `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_clean_render_ids_full_examples_dev140_gpt41mini_live_20260623.{jsonl,md}`
- Qwen clean-render comparator:
  `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_clean_render_ids_full_examples_dev140_qwen36_live_20260623.{jsonl,md}`
- v08 hybrid comparator:
  `experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.{json,jsonl,md}`
- GPT-4.1-mini clean-render no-call adapter replay:
  `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_replay_clean_render_ids_dev140_gpt41mini_20260623.{jsonl,md}`
- Qwen clean-render no-call adapter replay:
  `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_replay_clean_render_ids_dev140_qwen36_20260623.{jsonl,md}`
- GPT-4.1-mini Phase 3 single-prompt plateau:
  `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_phase3_v05_dev140_gpt41mini_20260623.{jsonl,md}`
- Phase 3 readout:
  `docs/experiments/exectv2/key_entities/exectv2_dedup_phase3_single_prompt_plateau_2026-06-23.md`

## Phase 1 Outcome

The active path is now deliberately narrow: one LLM-only rich-schema comparator
with two model instances, one hybrid rich-schema control, and the de-duplicated
LLM-only target route. Phase 3 shows that the single-prompt version plateaus
near the clean-render replay baseline, so Phase 4 should test lean per-family
LLM-only prompts before any model rollout. v09, Qwen compact, DeepSeek, Qwen
pool, and small-sample generation-selection diagnostics are retained as archive
evidence, not live scoreboard rows.
