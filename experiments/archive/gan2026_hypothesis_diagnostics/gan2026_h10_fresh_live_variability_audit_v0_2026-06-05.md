# H10 Fresh Live Variability Audit

Decision: `h10_supported_for_raw_runtime_variance_but_not_final_policy_variance_on_prefix`.

Validation-development variability audit only. No locked-test rows or failures were inspected. Run B was interrupted after 20 completed rows because the final block hung.

## Run Contract

- Run A rows: 25.
- Run B rows: 20.
- Matched rows compared: 20.
- DSPy/LiteLLM cache: disabled via `--disable-dspy-cache`.
- Reused outputs A: candidate 0, adjudicator 0.
- Reused outputs B: candidate 0, adjudicator 0.
- Call failures A/B: 0 / 0.

## Raw Output Identity

| Field | Identical rows | Different rows | Identity rate |
| --- | ---: | ---: | ---: |
| `llm_candidate_raw_output` | 1 | 19 | 0.0500 |
| `adjudicator_raw_output` | 1 | 19 | 0.0500 |
| `raw_output` | 1 | 19 | 0.0500 |

## Score-Layer Drift

| Score layer | Final-label changed | Purist changed | Run A accuracy | Run B accuracy |
| --- | ---: | ---: | ---: | ---: |
| `adapter_only_sidecar_from_adjudicator_selection` | 0 | 0 | 1.0000 | 1.0000 |
| `deterministic_top_candidate` | 0 | 0 | 1.0000 | 1.0000 |
| `hybrid_adjudicator_raw` | 1 | 1 | 0.9500 | 0.9000 |
| `hybrid_adjudicator_with_adapters` | 0 | 0 | 1.0000 | 1.0000 |
| `llm_candidate_selector_raw` | 3 | 0 | 1.0000 | 1.0000 |
| `state_graph_projection` | 0 | 0 | 0.9500 | 0.9500 |

## Interpretation

Fresh uncached validation calls show substantial raw-output variability: 19/20 paired rows differ at the LLM-candidate and adjudicator raw-output levels. On this completed 20-row prefix, deterministic adapters and final hybrid-with-adapters labels were stable, while raw adjudicator scoring changed one row. This means the prior cached replay audit was only a provenance check; a broader fresh-call audit with explicit request timeouts is needed before estimating whether runtime variance contributes materially to the full validation-test gap.
