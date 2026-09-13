# ExECTv2 fixed six-model comparison protocol

Date: 2026-07-15  
Status: redeclared for decision 0041 before the clean rerun

## Question

How do the six decision-0039 model conditions compare on ExECTv2 dev140 when
the prompt, decision-0040 model-led family graph, deterministic transforms, and
scorer are fixed?

The comparison matters because the retained three-model table used a
deterministic-only Prescription lane and an independent Seizure Frequency
extractor union. This study measures the named models after removing those
substitutions and preserving every prediction-changing deterministic action.

## Data and row policy

- Dataset: ExECTv2.
- Split: manifest-defined `dev140`, loaded through the repository split
  definition. Positional `load_letters()[:140]` selection is forbidden.
- Inspection: row-level inspection is permitted only for dev140.
- Excluded: test60 and full200 row-level predictions, annotations, errors, and
  differences. This study makes no test60 calls and does not inspect test60.
- Calls: one structured four-family event-ledger call per letter. Diagnosis is
  read from that structured response; there is no Diagnosis decomposer call.
- Resume: only from the same condition's decision-0041 checkpoint after the
  runner verifies that every saved ID belongs to manifest dev140.

The first attempted panel used positional first-140 selection. Only 94 IDs
overlapped manifest dev140. The GPT-4.1-mini output and partial Luna, Sol, and
DeepSeek outputs from that attempt are contaminated, excluded from evidence,
and must not be resumed. The active processes were stopped.

## Frozen conditions

| Display name | Runtime identifier | Route | Thinking | Prompt |
| --- | --- | --- | --- | --- |
| GPT-4.1-mini | `openai/gpt-4.1-mini` | OpenAI hosted | Provider default | `full` |
| GPT-5.6 Luna | `openai/gpt-5.6-luna` | OpenAI Chat Completions | Provider default | `full` |
| GPT-5.6 Sol | `openai/gpt-5.6-sol` | OpenAI Responses | Provider default | `full` |
| DeepSeek V4 Flash | `deepseek/deepseek-v4-flash` | Official DeepSeek hosted | Enabled by API default | `full` |
| Qwen 3.6:35B | `ollama_chat/qwen3.6:35b` | Local Ollama native chat | Disabled with `think=false` | `full` |
| Gemma 4 26B | `ollama_chat/gemma4:26b` | Local Ollama native chat | Disabled with `think=false` | `full` |

On 2026-07-15 the configured OpenAI account listed all three hosted OpenAI
  identifiers. Luna completed a Chat Completions probe. Sol was listed but
  returned 401 from Chat Completions and completed through the Responses API;
  DSPy's `model_type="responses"` is therefore a declared transport adapter
  for Sol. The official DeepSeek account listed `deepseek-v4-flash` and
`deepseek-v4-pro`. A 14-token route probe that omitted an explicit runtime override
returned both `reasoning_content` and final content from `deepseek-v4-flash`,
confirming the documented default. `deepseek-chat` is not this condition: it
is the legacy non-thinking compatibility alias.

Local runtime identities are frozen to Ollama 0.30.10 at
`http://localhost:11434`:

- Qwen: digest
  `07d35212591fc27746f0a317c975a6d68754fb38e9053d82e25f06057af28522`,
  Q4_K_M, reported parameter size 36.0B.
- Gemma: digest
  `5571076f3d70050487b26b341705799e0ab29b808164f90d20d4cf84f699d251`,
  Q4_K_M, reported parameter size 25.8B.
- Hardware: NVIDIA GeForce RTX 4070 Laptop GPU, 8188 MiB VRAM. Record system
  RAM, loaded context, `size_vram`, and observed partial offload in the final
  artifact rather than inferring them from latency.

## Fixed pipeline and comparator

- Candidate: each named model's decision-0040 output.
- Fixed historical comparator: the corrected GPT-4.1-mini dev140 condition,
  used only as a named within-panel baseline; no historical score is copied
  into the result.
- Required model inputs: the named model's Diagnosis, Seizure Frequency,
  Prescription, and Investigations facts and exact evidence.
- Diagnosis: the named model's structured event-ledger Diagnosis output plus
  the selected attributable heading, boundary, normalization, and residual
  recovery. The dedicated decomposer is removed under decision 0041.
- Seizure Frequency: model structured output, direct adapter, state
  projection, and unsupported-state suppression. No independent extractor
  union.
- Prescription: model structured output plus shared normalization, supported
  regimen splitting, unsupported-fact removal, and bounded repair. No
  deterministic producer substitution.
- Investigations: model structured output plus evidence validation,
  normalization, and deduplication.
- Semantic prompts: the same committed `full` prompt profile for all six
  models. Transport or output-shape repair may vary only when it preserves the
  selected clinical facts. A semantic prompt change would be a separate
  condition and does not count toward this panel.
- Temperature and output limit: `0` with a 10,000-token structured-call limit
  for GPT-4.1-mini. The first Qwen and Gemma clinical smokes completed Diagnosis
  but their structured calls exceeded the inconsistent 10,000-output/8,192-
  context setup and produced parse failures. Before any panel run, both local
  conditions were revised to a 32,768 context and a 16,000-token structured
  limit. The earlier DeepSeek Diagnosis-sidecar smoke is not part of the
  selected architecture. DSPy requires GPT-5-family reasoning
  routes to use temperature `1` and at least 16,000 output tokens, so Luna and
  Sol use temperature `1` and a 16,000-token structured limit. DeepSeek
  thinking mode documents that temperature is ignored. These runtime
  asymmetries are reported as conditions rather than described as identical
  sampling.
- Cache: DSPy cache disabled for the final calls; same-condition checkpoint
  resume is allowed after interruption.

## Scores and component evidence

- Primary overall score: de-duplicated `clinical_headline` F1 across the four
  main families.
- Required family scores: Diagnosis concept/assertion, Prescription regimen,
  Investigations result, Seizure Frequency compatibility headline, and the
  decision-0037 Seizure Frequency `state_profile` score.
- Secondary scores: normalized phrase, CUI/semantic, full attributes,
  exact-evidence rate, call failures, schema/parse failures, and final fact
  counts.
- Attribution: final model-origin facts, rule-added and rule-removed facts,
  deterministic action counts, first prediction-changing owner, and
  correct-to-wrong versus wrong-to-correct counts on dev140.
- Hard slices: family, parse/schema status, evidence status, deterministic
  action type, and the existing clinical-subproblem taxonomy where the saved
  trace supports it.

One machine-readable row represents one model, letter, family, processing
step, and scored output. It retains source identifier, selected evidence,
evidence status, model-owned clinical keys, final clinical keys, gold keys,
deterministic actions, first prediction-changing owner, correctness direction,
parse/schema/call state, and scorer identity. The aggregate artifact also
records source revision or dirty-tree note, dependency versions, exact model
route, endpoint, prompt versions, cache policy, token limits, local model
digests, hardware, latency when available, and output hashes.

## Preflight and scale-up

Before any clinical-row call:

1. pass the retained-evidence, prompt-snapshot, split-barrier, focused runner,
   Ruff, mypy, and full pytest checks;
2. validate all six configurations against decision 0040 and confirm identical
   component signatures;
3. smoke-test one short non-clinical prompt per exact route;
4. run one dev140 row per condition and require a final structured response;
5. run five rows per local condition before the full dev140 run.

Stop a condition at the first layer that fails. Do not silently substitute a
model, tag, quantization, endpoint, prompt profile, component graph, or scorer.

## Decision and stop rules

The panel is complete only when all six exact conditions finish dev140 with
reproducible configurations and the aggregate component report can be rebuilt
from the retained row artifacts. A condition with call or parse failures may
remain in the panel if those failures are retained as model behavior rather
than repaired by changing clinical meaning.

Stop with one of: complete panel; negative result for a named condition;
revise only a transport/output-shape adapter in a separately recorded version;
or blocked by an unavailable exact model/runtime. Do not rank closed versus
open models, sizes, or reasoning modes from a partial panel.

## Claim boundary

This is a development comparison on ExECTv2 dev140. It can support a bounded
statement about the six exact runtime conditions under the fixed pipeline and
scorer. It is not an independent holdout, published ExECT benchmark
reproduction, clinical validation, cross-task transfer result, deployment
study, or general claim about open- versus closed-weight models.
