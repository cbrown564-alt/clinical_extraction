# ExECTv2 v0.42 Dev140 Local-Qwen Run Decision

Date: 2026-06-19
Decision: no-go / defer exact dev140 local-Qwen single-call spend

## Question

Should we spend a full dev140 local-Qwen CPU run on the exact
`exectv2_target_indicators_single_call_v0.42` single-call condition now?

## Decision

Do not run the exact v0.42 dev140 local-Qwen single-call experiment yet.

The run would answer one useful narrow question: whether the exact local-Qwen
v0.42 single-call prompt plus current deterministic projection reproduces the
dev25 headline on the 140-letter development surface. It would not yet answer
the more important attribution question: whether any gain is owned by the LLM,
by general clinical projection, or by one-letter dev25 projection families.

Because the current blocker is attribution rather than lack of another aggregate
headline, a full CPU dev140 spend is deferred until same-raw-output projection
attribution is available.

## Evidence Read

Existing exact v0.42 evidence is dev25 only:

- Artifact:
  `experiments/exectv2_target_indicators_single_call_v042_reproject_v041live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.42`
- Model/source: local `ollama_chat/qwen3.6:35b`, saved v0.41 live raw output,
  v0.42 no-call projection replay
- Rows: 25
- Headline overall: `0.9487`
- Benchmark key: `0.3675` raw / `0.3816` after CUI projection

Existing dev140 target comparators already provide the held-out development
warning signal:

| Candidate | Ownership | Headline overall | Benchmark raw | Benchmark after CUI | Semantic |
| --- | --- | ---: | ---: | ---: | ---: |
| `deterministic_all9` | `rules_only` | 0.7301 | 0.3586 | 0.3540 | 0.3706 |
| `llm_only_all_entities` | `llm_first` | 0.4313 | 0.0000 | 0.1110 | 0.1151 |
| `hybrid_all_entities` | `hybrid` | 0.5684 | 0.1810 | 0.1917 | 0.2195 |
| `family_routed_llm_first` | `llm_first_with_hybrid_sf_route` | 0.5592 | 0.0593 | 0.1789 | 0.1833 |
| `family_routed_with_focused_diagnosis_route` | `llm_first_with_hybrid_diagnosis_and_sf_routes` | 0.7081 | 0.1486 | 0.2316 | 0.2941 |

Best existing dev140 headline by target indicator:

| Indicator | Best candidate | Headline F1 |
| --- | --- | ---: |
| Diagnosis | `deterministic_all9` | 0.7302 |
| SeizureFrequency | `deterministic_all9` | 0.7277 |
| Prescription | `deterministic_all9` | 0.9072 |
| Investigations | `llm_only_all_entities` | 0.7475 |

Only Prescription currently clears the `>0.900` dev140 headline threshold among
existing target artifacts.

## Attribution Blocker

The Phase 2 projection-family audit found v0.42-added or v0.42-relevant
prediction-bearing families that fire on one dev25 letter each and are not yet
ablated:

| Projection family | Saved v0.42 fires | Letter(s) | Current disposition |
| --- | ---: | --- | --- |
| `projected_diagnosis_context_to_remote_last_seizures_state` | 1 | `EA0010` | quarantine until generalized/ablated |
| `projected_infrequent_context_state` | 1 | `EA0011` | quarantine/cut |
| `projected_diagnosis_context_to_controlled_sf_state` | 1 | `EA0022` | keep only behind a named general family and hard-slice tests |
| `projected_diagnosis_context_to_frequent_myoclonic_jerks` | 1 | `EA0025` | quarantine/cut |
| `dropped_inconsistent_zero_state_with_active_rate` | 1 | `EA0025` | likely general guard, but still needs tests/attribution |
| `projected_four_since_last_clinic` | 1 | `EA0002` | quarantine/cut or replace with general parser |

These families are not merely format-preserving CUI or JSON repairs. They can
change selected clinical states, diagnosis/SF ownership, or active-rate versus
seizure-free interpretation. Under the research protocol, they are deterministic
semantic rules until proven otherwise.

## Why The Run Is Not Worth The Spend Yet

An exact dev140 run would be useful if the missing evidence were only aggregate
generalization. It is not. The current missing evidence is component ownership.

Running dev140 now would create a mixed prompt/model/raw-output/projection
condition:

- live local-Qwen raw output on dev140;
- frozen v0.42 prompt;
- deterministic normalization/projection with known one-letter dev25 families;
- headline, benchmark, `concept_negation`, and `active_rate_fidelity` readouts.

Even a strong result could not support promotion because we could not separate
LLM selection from deterministic semantic repair. A weak result would be easier
to interpret, but existing dev140 comparators already make the dev25 headline
claim unsafe. The expected information gain does not justify a full CPU run
before attribution instrumentation.

## Next Trigger

Reconsider the exact dev140 local-Qwen run only after a same-raw-output
projection attribution path exists for v0.42. Minimum trigger:

- rule-family switches or an audit-only replay path for the suspicious v0.42
  Diagnosis and SeizureFrequency projection families;
- per-family attribution sidecar with rule id, entity, portability category,
  changed rows, wrong-to-correct and correct-to-wrong counts, and effects on
  `concept_negation` / `active_rate_fidelity`;
- quarantine or explicit retention decision for one-letter projection families;
- a predeclaration that states the run purpose as attribution-qualified
  generalization, not promotion by headline F1.

If that trigger is met, the authorized runtime condition should remain:

```powershell
$env:OPENAI_API_KEY = "ollama"
$env:CLINICAL_EXTRACTION_OLLAMA_NUM_GPU = "0"
$env:CLINICAL_EXTRACTION_OLLAMA_NUM_CTX = "16384"

.\.venv\Scripts\python.exe -m clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_target_indicators_single_call `
  --split dev `
  --pilot 140 `
  --mode live `
  --model ollama_chat/qwen3.6:35b `
  --api-base http://localhost:11434 `
  --temperature 0 `
  --max-tokens 6000 `
  --no-dspy-cache `
  --progress-every 10 `
  --out-jsonl experiments\exectv2_target_indicators_single_call_v042_live_dev140_qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl `
  --out-report experiments\exectv2_target_indicators_single_call_v042_live_dev140_qwen36_35b_ollama_cpu_ctx16384_20260619.md
```

No live LLM calls were run for this decision.
