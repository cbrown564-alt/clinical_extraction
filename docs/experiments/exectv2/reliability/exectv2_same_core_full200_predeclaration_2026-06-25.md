# ExECTv2 Same-Core Full-200 Aggregate Predeclaration

- Date: `2026-06-25`
- Status: frozen predeclaration before any new same-core full-200 execution
- Code hash at drafting: `0f01ae6`
- Worktree at drafting: clean
- Architecture core: `exectv2_2call_no_sf_adjudicator_model_swap`
- Primary surface: `clinical_headline`
- Split/scope: full-200 aggregate-only validation
- Row-inspection boundary: `aggregate_only_no_full200_or_holdout_row_level_inspection`

## Purpose

This predeclaration freezes the same-core full-200 model-swap comparison before
any new full-200 execution. The comparison question is whether GPT-4.1-mini and
DeepSeek chat preserve the frozen two-call no-SF-adjudicator architecture on the
benchmark-facing 200-letter surface. Qwen is not an operational candidate in
this protocol because the same-core dev140 row failed operational stability and
repair v01 failed its predeclared dev140 gate.

This artifact authorizes only aggregate reporting. It does not authorize
full-200 or holdout row-level failure analysis.

## Candidate Set

| Role | Candidate id | Model/runtime | Dev140 source | Full-200 status |
| --- | --- | --- | --- | --- |
| operational reference | `exectv2_2call_no_sf_adjudicator_gpt41mini_full200` | `openai/gpt-4.1-mini` / `openai_chat` | `exectv2_2call_no_sf_adjudicator_gpt41mini_dev140` | May be materialized by aggregate replay from the accepted GPT-4.1-mini full-200 two-call no-SF-adjudicator artifacts if the config signature matches; otherwise rerun once from the frozen full-200 config. |
| operational candidate | `exectv2_2call_no_sf_adjudicator_deepseek_full200` | `deepseek/deepseek-chat` / `deepseek_chat` | `exectv2_2call_no_sf_adjudicator_deepseek_dev140` | Run once from the frozen full-200 config after this predeclaration. |
| diagnostic only, excluded from operational candidate set | `exectv2_2call_no_sf_adjudicator_qwen36_dev140` | `ollama_chat/qwen3.6:35b` / `ollama_chat_think_false` | `exectv2_2call_no_sf_adjudicator_qwen36_dev140` plus failed repair v01 | Not eligible for this full-200 protocol. Any Qwen revisit requires a separate v02 repair predeclaration and a passing dev140 rerun before full-200 inclusion. |

The GPT reference full-200 result is already known from the simplification
frontier. It is a fixed anchor for this comparison, not a tuning surface for
DeepSeek prompts, thresholds, or repairs.

## Frozen Architecture Contract

Both operational candidates must keep the frozen component graph:

| Component | Owner | Policy |
| --- | --- | --- |
| `structured_key_family_event_ledger` | model | live or matched saved model output; same schema contract |
| `diagnosis_decomposer` | model | live or matched saved model output; same schema contract |
| `sf_structured_direct_adapter` | deterministic | unchanged from same-core dev140 |
| `sf_state_projection` | deterministic | unchanged from same-core dev140 |
| `sf_unknown_suppression` | deterministic | unchanged from same-core dev140 |
| `sf_union_arbitration` | deterministic | unchanged from same-core dev140 |
| `prescription_deterministic_repair` | deterministic | unchanged deterministic Prescription repair v0.3 |
| `finding_assembly` | deterministic assembly | unchanged lenses, views, and scorer |

Required views are `raw_candidate`, `evidence_valid`, `clinical_headline`,
`fidelity_companion`, and `benchmark_cui`. The primary reporting view is
`clinical_headline` de-duplicated clinical recovery. `benchmark_cui` and strict
benchmark results may be reported only as diagnostic/comparability surfaces.

Allowed model-specific differences are runtime model identifier, endpoint,
temperature, token/context budgets, prompt wording needed to satisfy the same
output contract, format-preserving JSON/schema repair, and runtime telemetry.
Semantic repair, changed entity lenses, changed SF projection, changed
Prescription repair, candidate-backed selection, or scorer/view changes are not
same-core eligible.

## Full-200 Config Freeze

Before execution, create or verify full-200 configs that mirror the dev140
configs except for split, row count, candidate id, output namespace, and source
artifact paths:

```text
configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_gpt41mini_full200.json
configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_deepseek_full200.json
```

Required config fields:

- `architecture_core_id`: `exectv2_2call_no_sf_adjudicator_model_swap`
- `split`: `full200`
- `row_count`: `200`
- `calls_per_letter`: `2`
- `live_call_components`: `structured_key_family_event_ledger`, `diagnosis_decomposer`
- `replayed_components`: deterministic SF chain, deterministic Prescription repair, finding assembly
- identical lenses and views to the dev140 same-core configs
- aggregate-only claim boundary

Expected report namespaces:

```text
experiments/exectv2_2call_no_sf_adjudicator_gpt41mini_full200_20260625.json
experiments/exectv2_2call_no_sf_adjudicator_gpt41mini_full200_20260625.jsonl
docs/experiments/exectv2/reliability/exectv2_2call_no_sf_adjudicator_gpt41mini_full200_2026-06-25.md

experiments/exectv2_2call_no_sf_adjudicator_deepseek_full200_20260625.json
experiments/exectv2_2call_no_sf_adjudicator_deepseek_full200_20260625.jsonl
docs/experiments/exectv2/reliability/exectv2_2call_no_sf_adjudicator_deepseek_full200_2026-06-25.md
```

The JSONL artifacts may persist per-letter predictions for reproducibility, but
the aggregate report must not emit row-level examples, row identifiers tied to
errors, note text, evidence text, rationales, or residual failure ledgers.

## Execution Rule

Run each operational candidate once after the full-200 config signatures are
frozen. If an infrastructure failure occurs before metrics are read, such as a
missing artifact, corrupted checkpoint, provider outage, or runner crash, a
rerun is allowed only after the reason is recorded in the final report.

If a candidate fails any promotion gate after metrics are read, stop and report
the null result. Any prompt, threshold, parser, adapter, deterministic-rule, or
scorer change starts a new dev140-only development cycle and a fresh
predeclaration.

## Allowed Aggregate Outputs

The full-200 report may include:

- overall and per-family `clinical_headline` precision, recall, F1, TP, FP, and FN
- diagnostic `benchmark_cui` aggregate precision, recall, and F1
- call-failure and parse/schema-failure counts by producer and model
- schema-validity and exact-evidence aggregate rates
- aggregate deterministic-action counts for SF projection/suppression/union and Prescription repair
- aggregate runtime telemetry, including call counts and token/cost totals when available
- cross-model aggregate deltas between GPT-4.1-mini and DeepSeek
- promotion-gate status and claim-boundary language

The report must not include:

- full-200 row-level failure tables
- note text, gold labels, prediction text, evidence spans, or rationales tied to
  full-200 row identifiers
- threshold/prompt edits after seeing full-200 metrics
- Qwen as an operational full-200 row

## Promotion Gates

| Gate | Requirement |
| --- | --- |
| architecture parity | Both operational candidates use the frozen same-core graph, same lenses, same views, and same `clinical_headline` scorer. |
| attribution clarity | Model-generated structured and Diagnosis facts are separated from deterministic SF projection and Prescription repair in the aggregate report. |
| operational stability | Call failures and blocking parse/schema failures are reported by producer. A promoted operational row should have `0` call failures and no unresolved output-contract failure cluster; otherwise it is diagnostic/null evidence. |
| evidence validity | Exact evidence rate is reported overall and by family; any family below `0.99` exact evidence needs an explicit caveat. |
| clinical interpretability | Overall `clinical_headline` F1 is at least `0.8000`, no scored family is hidden, and no family with eligible cells falls below `0.7000` without demoting the row to diagnostic evidence. |
| comparison value | DeepSeek may be promoted as same-core full-200 evidence if it is within `0.0300` overall F1 of the fixed GPT anchor or shows a named family advantage without failing operational/evidence gates. |
| claim boundary | The report labels the result as full-200 aggregate validation only, not holdout, deployment, or strict benchmark superiority. |

## Qwen Boundary

Qwen remains outside this protocol because:

- baseline same-core dev140 had `1` call failure and `12` parse/schema failures;
- the output-contract audit classified failures as Qwen/runtime-adapter contract
  instability rather than harmless aggregate noise;
- repair v01 was early-stopped at `50/140` structured rows with `2` blocking
  parse/schema failures and checkpoint evidence validity `0.9639`.

Qwen can re-enter the operational path only through a separate v02
predeclaration that defines whether invalid-family dropping or valid-object
extraction is format-only schema repair or semantic adapter behavior, then
passes dev140 before any full-200 use.

## Reporting Contract

The final same-core full-200 report must include:

- this predeclaration path;
- full-200 config paths and config-signature summary;
- code hash and worktree state at execution;
- candidate ids, model ids, runtime settings, and artifact paths;
- row-inspection boundary statement;
- stop-rule outcome;
- promotion-gate table;
- aggregate metrics and operational telemetry;
- explicit statement that strict benchmark/CUI results are diagnostic only.

If the audit is not executed, this predeclaration remains the frozen next-step
artifact and does not by itself promote any new full-200 same-core evidence.
