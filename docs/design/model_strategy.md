# LLM model and comparison policy

Last updated: 2026-07-14
Status: frozen for new evidence

The machine-readable freeze is `architecture_freeze` in
`docs/experiments/retained_evidence_manifest.json`. It pins the reduced source
tree at commit `465621341c6af59f2fc028be7bf5f9e325739c50`, the policy files,
the six retained reference cells, and the commands required before a result can
be added to the paper evidence set.

## Retained runtime identifiers

| Identifier | Retained role | Boundary |
| --- | --- | --- |
| `openai/gpt-4.1-mini` | Gan and ExECT development/reference runtime | Development baseline, not a best-model claim |
| `deepseek/deepseek-chat` | ExECT same-core model-transfer runtime | Retained three-model evidence |
| `ollama_chat/qwen3.6:35b` | ExECT local model-transfer runtime | Local transfer evidence; thinking disabled |
| `deepseek/deepseek-reasoner` | GEPA reflection model | Optimizer provenance only |
| `openai/gpt-4.1` | Gan V12 frozen holdout reviewer | Aggregate ceiling evidence only |

The exact Ollama route is part of the identity. Qwen must use the native
`ollama_chat/qwen3.6:35b` route with thinking disabled; the OpenAI-compatible
Ollama endpoint is not an equivalent runtime.

## Frozen ExECT model-comparison core

New same-core model evidence must inherit
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

The earlier GPT, DeepSeek, and Qwen artifacts remain valid retained evidence,
but they are asymmetric: the GPT config used temperature `0.3`, and Qwen used
the compact prompt plus output-schema repair. They support a bounded
same-core transfer statement, not a strict same-prompt six-model conclusion.

## Six-model claim boundary

The retained roster is three of six: GPT-4.1-mini, DeepSeek chat, and Qwen
3.6:35b. The other three runtime identifiers were never predeclared in the
governing evidence and are therefore not invented during cleanup. Before any
new model call, a comparison predeclaration must name all remaining exact
provider/API identifiers, hosted-versus-local route, model revision if exposed,
temperature, token limits, cache mode, hardware/endpoint metadata, and the
handling of model-specific format adapters.

No six-model ordering or size/reasoning conclusion is permitted until all six
conditions run under the frozen core and the asymmetries are either removed or
reported as explicit conditions.

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
