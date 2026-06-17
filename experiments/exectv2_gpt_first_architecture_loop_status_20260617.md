# ExECTv2 GPT-First Architecture Loop Status

- Generated: `2026-06-17`
- Model loop: `openai/gpt-4.1-mini`
- Development split: `dev`
- Strategy: `docs/research/exectv2_gpt_first_full_architecture_strategy_2026-06-17.md`
- Freeze target: benchmark dev overall >= `0.87` per-item and >= `0.90` per-letter, plus all three attribution-clean tracks.
- Architecture freeze readiness: `not ready`

## Freeze Blockers

- rules_only: benchmark F1 0.252/0.520 below 0.87/0.90
- llm_only: shape_gap - Best available run has the right broad scope, but not the strategy's required architecture shape.
- hybrid: scope_gap - Best available run is sf_only, but the required scope is all9.

## Run Matrix

| Track | Required shape | Status | Best run | Scope | Letters | Semantic F1 | Benchmark F1 | Reliability | Next action |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| rules_only | deterministic all-9 baseline with rule families and CUI projection | `satisfied` | `exectv2_deterministic_all9_dev_20260617`<br>`exectv2_deterministic_all9` | all9 | 140 | 0.280/0.542 | 0.252/0.520 | calls=0; parse=0; ev=1.000 | Use the deterministic all-9 scorecard to reduce active-entity over-emission, improve Prescription/Investigations exactness, and add the next entity engines with rule-family/CUI ablations. |
| llm_only | GPT per-entity all-9 structured mention frames | `shape_gap` | `exectv2_llm_only_all_entities_dev140_gpt41mini_20260612`<br>`exectv2_llm_only_all_entities` | all9 | 140 | 0.087/0.236 | 0.000/0.000 | calls=0; parse=0; ev=0.942; dropped=61 | Run GPT per-entity all-9 pilot25 then dev140, beginning with Prescription, Investigations, Diagnosis, and SeizureFrequency. |
| hybrid | GPT all-9 candidate assessment over evidence-grounded candidates | `scope_gap` | `exectv2_hybrid_dev140_gpt41mini_20260611`<br>`exectv2_hybrid` | sf_only | 140 | 0.327/0.578 | 0.327/0.578 | calls=0; parse=0; routed=37 | Extend the live candidate-set and GPT candidate-assessment pattern from SeizureFrequency to all nine entities, with routing and CUI ablations. |

## Reading

Current evidence is useful but not architecture-freeze evidence. The all-entity LLM single-pass baseline is retained as a negative baseline; it does not satisfy the new per-entity structured-frame track. SF-only rules and hybrid runs remain valuable transfer checks, but they do not satisfy all-9 breadth.

Full-200 auditing remains blocked until dev140 has all-9 rules_only, llm_only, and hybrid evidence with reliability scorecards and component/CUI ablations.
