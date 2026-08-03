# LLM model and comparison policy

Last updated: 2026-08-03
Status: retained reference frozen; corrected final-comparison target accepted

The machine-readable freeze is `architecture_freeze` in
`docs/experiments/retained_evidence_manifest.json`. It pins the reduced source
tree at commit `465621341c6af59f2fc028be7bf5f9e325739c50`, the policy files,
the six retained reference cells, and the commands required before a result can
be added to the paper evidence set.

## Retained runtime identifiers

| Identifier | Retained role | Boundary |
| --- | --- | --- |
| `openai/gpt-4.1-mini` | Gan and ExECT development/reference runtime | Development baseline, not a best-model claim |
| `deepseek/deepseek-chat` | DeepSeek V4 Flash API runtime | Retained result has incomplete runtime metadata; not yet eligible as the final reported DeepSeek condition |
| `ollama_chat/qwen3.6:35b` | ExECT local model-transfer runtime | Local transfer evidence; thinking disabled |
| `deepseek/deepseek-reasoner` | GEPA reflection model | Optimizer provenance only |
| `openai/gpt-4.1` | Gan V12 frozen holdout reviewer | Aggregate ceiling evidence only |

The exact Ollama route is part of the identity. Qwen must use the native
`ollama_chat/qwen3.6:35b` route with thinking disabled; the OpenAI-compatible
Ollama endpoint is not an equivalent runtime.

OpenAI-compatible vLLM endpoints use the explicit `vllm/<served-model>`
runtime identifier. The shared model factory sends requests through DSPy's
OpenAI-compatible transport and adds only the vLLM chat-template settings from
`VLLM_THINKING` and optional `VLLM_REASONING_EFFORT`. The route and credential
come from `VLLM_BASE_URL` and optional `VLLM_API_KEY`, or the routine command's
explicit options. Keyless `vllm/<served-model>` routes use the conventional
`EMPTY` placeholder. These runs retain the same development prompts, raw
outputs, row traces, checkpoints, scoring, and reports as other routes. vLLM
is a transport condition, not permission to change the clinical prompt or
rules.

Local structured-output handling is governed by
[decision 0042](../decisions/0042-shared-local-model-structured-output-repair.md).
Qwen and Gemma use the same defect-based schema repairs, failure codes,
value-preserving retry rule, and pre-run native Ollama probe. The normal path is
one extraction call. A parseable schema failure may add one format-only retry;
reports must count it separately.

The 2026-07-16 native probe on Ollama 0.30.10 found different enforcement
modes. `gemma4:26b` uses `native_schema_constraint`. `qwen3.6:35b` uses
`prompt_plus_shared_parser` because its installed `qwen3.5` Ollama parser still
ignores `format` when `think=false`. Qwen clinical prompts explicitly require
JSON, and all drift remains subject to decision 0042 repair and reporting.

## Retained historical ExECT model-comparison core

The retained GPT, DeepSeek, and Qwen artifacts used
`exectv2_2call_no_sf_adjudicator_model_swap`:

- split: ExECT `dev140` for row-inspectable development;
- two live calls per letter: the structured key-family event ledger and the
  Diagnosis decomposer;
- no LLM SeizureFrequency adjudicator;
- deterministic replay stages: SF direct adapter, state projection, unknown
  suppression, union arbitration, Prescription repair, and finding assembly;
- output views: raw candidate, evidence-valid, `clinical_headline`, fidelity
  companion, and benchmark/CUI;
- primary comparison scorer: the current ExECT `clinical_headline` owner, with
  strict phrase/CUI/attribute companions reported separately;
- standard prompt profile: `full`, temperature `0`, with the committed prompt
  snapshots as the required semantic schema;
- model-specific adapters may repair transport, JSON dialect, or output shape
  only. Any semantic prompt change, selected-evidence rewrite, deterministic
  clinical repair, or scorer change creates a new comparison condition.

These artifacts remain reproducible historical evidence, but they are not a
consistent model-led comparison. Their Prescription lane is
deterministic-only, and their Seizure Frequency lane unions model output with
an independent deterministic extractor. They are also asymmetric: the GPT
config used temperature `0.3`, and Qwen used the compact prompt plus
output-schema repair.

## Corrected final-comparison core

All new six-model evidence must implement
[decision 0040](../decisions/0040-final-exect-llm-with-rules-family-ownership.md):

- the named model supplies the candidate facts and evidence for Diagnosis,
  Seizure Frequency, Prescription, and Investigations;
- Diagnosis may use recorded heading, boundary, normalization, and residual
  recovery, with every deterministic addition or selection attributed;
- Seizure Frequency uses the named model's pre-union output plus attributable
  state projection and unsupported-state suppression; it must not union an
  independent deterministic extractor;
- Prescription uses the named model's regimen output plus bounded shared
  normalization and repair; it must not substitute the deterministic
  all-entity or Prescription extractor;
- Investigations remains model output through evidence, normalization, and
  deduplication adapters;
- `clinical_headline` remains the declared overall compatibility scorer;
  Seizure Frequency must additionally report the `state_profile` primary
  family score required by decision 0037; and
- output records preserve model origin, deterministic changes, exact-evidence
  status, rule-added and rule-removed facts, and schema/parse failures.

The corrected saved-output aggregate is a candidate until durable
configurations reproduce it and a new architecture freeze selects it. New
model calls may not use the rejected historical component graph as the final
comparison condition.

## Six-model claim boundary

Decision 0039 fixes the final roster:

| Model condition | Availability class | Route |
| --- | --- | --- |
| GPT-4.1-mini | Closed-weight | Hosted |
| GPT-5.6 Luna | Closed-weight | Hosted |
| GPT-5.6 Sol | Closed-weight | Hosted |
| DeepSeek V4 Flash | Open-weight | Hosted |
| Qwen 3.6:35B | Open-weight | Local |
| Gemma 4 26B | Open-weight | Local |

Before any new model call, the comparison predeclaration must name each exact
provider/API or local runtime identifier, hosted-versus-local route, model
revision if exposed, temperature, token limits, cache mode, hardware/endpoint
metadata, and the handling of model-specific format adapters.

`deepseek/deepseek-chat` is the API identifier for DeepSeek V4 Flash. The final
reported condition is displayed as **DeepSeek V4 Flash**. The retained result
has incomplete runtime metadata, so it cannot satisfy the final condition.

No six-model ordering or size/reasoning conclusion is permitted until all six
conditions run under the corrected final-comparison core and the runtime
asymmetries are either removed or reported as explicit conditions.

Roster owner: [decision 0039](../decisions/0039-final-exect-six-model-roster.md).

## Run metadata and change control

Every LLM-backed run must record the dataset, split, row policy, scorer,
runtime model identifier, role, endpoint, prompt profile, cache/replay mode,
repair policy, and output hashes. New model calls require a predeclared research
question and must pass the manifest, prompt snapshot, split-barrier, Ruff,
mypy, full-test, and six-cell replay checks.

Changing a frozen prompt, scorer, split, repair layer, model route, or component
graph requires a new freeze ID and a complete replay. A no-call re-score may
retain the freeze only when predictions are unchanged and the scorer change is
predeclared and separately attributed.
