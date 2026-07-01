> **Superseded for navigation —** canonical summary: [`COMPONENT_MECHANICS_CANON.md`](../COMPONENT_MECHANICS_CANON.md). Full detail retained below.

# Gan 2026 RQ1 Candidate-Discovery Answer

Date: 2026-06-04

Status: final validation-development answer for LLM component mechanics. This is
not a holdout-transfer, production, or benchmark-comparable claim.

## Answer

RQ1 is answered for saved validation-development replay:

```text
The useful LLM candidate-generation role is selective boundary-state proposal,
not broad replacement candidate generation.
```

The broad deterministic candidate set and state-graph nodes remain the fixed
candidate substrate and comparator for later RQs, but they are not the research
answer. The LLM component answer is narrower: `llm_candidate_selector_raw`
preserves uncertainty, seizure-free-boundary, and competing-state hypotheses
that deterministic rules often collapse, while also producing too much burden
and too many unsafe label-changing candidates for broad use.

The follow-up panel keeps this distinction visible. It assigns 78 panel rows to
`candidate_generation` as first-failure owner, with high concentration in
`competing_semiologies` (39 rows), `uncertainty_or_ambiguity` (36),
`seizure_free_duration` (35), `current_vs_historical` (33),
`rate_bucket_or_denominator` (29), and `unknown_boundary` (28). Those counts
identify where candidate generation matters; they do not by themselves prove a
rescue. The predeclared candidate-generation rescue slice is 44 rows, and the
unknown/seizure-free candidate slice is 26 rows.

## Claim Boundary

Supporting artifacts:

- ``
- ``
- `experiments/gan2026_component_projection_followup_panel_2026-06-04.md`
- `experiments/gan2026_rq1_candidate_discovery_matrix_2026-06-03.jsonl`
- `experiments/gan2026_llm_component_mechanics_rows_2026-06-03.jsonl`

All evidence comes from saved validation artifacts under `gan2026_split_v1`.
Locked holdout rows were not used for this answer.

## LLM Component/Generator Trade-Offs

| Generator | Source rows | Candidates | Recalled rows | Recall | Exact evidence | Burden signal |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `deterministic_candidates_all` | 750 | 1,194 | 725 | 0.967 | 0.898 | Fixed comparator/substrate |
| `state_graph_nodes` | 750 | 1,122 | 725 | 0.967 | 0.891 | Representability view |
| `deterministic_top_candidate` | 750 | 750 | 716 | 0.955 | 0.847 | Safety-floor comparator |
| `llm_candidate_selector_raw` | 739 | 2,126 | 642 | 0.869 | 0.985 | High recall intent, high burden |
| `llm_selected_state_or_evidence` | 250 | 250 | 222 | 0.888 | 0.956 | Diagnostic selected-state surface |

The raw LLM generator recalled 11 validation rows not recalled by
`deterministic_candidates_all`, but missed 94 rows recalled by the deterministic
candidate set and produced at least four candidates on 136 source rows. In the
follow-up panel, the same raw selector shows why broad promotion is unsafe:
`llm_candidate_selector_raw` has 7 W->C changes but 49 C->W regressions on the
panel rows selected for component stress.

## Deterministic Baseline Role

Deterministic candidates are retained as:

- fixed broad substrate for RQ2/RQ4/RQ5 experiments;
- safety-floor comparator for changed-row accounting;
- source of miss slices for selective LLM candidate rescue;
- oracle-gap reference for state-graph representability.

They are not credited as the RQ1 research answer. The RQ1 answer concerns where
LLM candidate generation adds candidate states the fixed substrate tends to
collapse or omit.

## Row-Level Mechanism Examples

`source_row_index=3356`, gold `unknown`: the LLM preserved a conditional
unknown state for seizures occurring only after curtailed sleep, while
deterministic candidates favored a seizure-free duration. This is the strongest
candidate-generation mechanism: preserve the uncertainty state before
projection.

`source_row_index=6077`, gold `unknown`: the LLM held both an eight-month
seizure-free phrase and a breakthrough/stress state. That candidate pluralism is
useful only if a later verifier can choose among incompatible states.

`source_row_index=10266`, gold `unknown`: the LLM represented device-log
clusters without counts as uncertainty rather than converting the device cadence
into seizure frequency.

`source_row_index=278`, gold `multiple per week`: the LLM phrase "multiple
times per week" is projection-compatible, so candidate generation should receive
representation credit and projection/rendering should own the Gan syntax
conversion.

Rows such as `744` and `1357` show the negative case: when the LLM loses the
rate signal, denominator, or event-frequency identity, candidate generation
owns the failure rather than projection.

## Hidden-Family Readout

The final RQ1 weak families are:

- `unknown_boundary`: 28 panel rows owned by candidate generation.
- `uncertainty_or_ambiguity`: 36 panel rows owned by candidate generation.
- `seizure_free_duration`: 35 panel rows owned by candidate generation.
- `competing_semiologies`: 39 panel rows owned by candidate generation.
- `rate_bucket_or_denominator`: 29 panel rows owned by candidate generation.

Rate and denominator rows are not all missing-candidate problems; many become
projection or typed-state failures once a plausible state exists. Unknown and
seizure-free boundary rows are the clearest target for future LLM candidate
proposal.

## Transfer Confidence

| Finding | Development confidence | Holdout-transfer confidence | Reason |
| --- | --- | --- | --- |
| Broad LLM candidate generation is unsafe as a replacement. | High | Moderate-to-high | Burden and C->W regressions are systematic across saved validation stress rows. |
| LLM candidate generation has selective value on boundary/uncertainty states. | Moderate | Low-to-moderate | Mechanism is clinically plausible, but slices were discovered on validation. |
| Candidate discovery is not the broad bottleneck for ordinary rates. | High | Moderate | Broad validation recall is high, but this rests on validation-developed rules. |

## Metadata/Instrumentation Gaps

- `union_verified_candidates` is still inferred rather than materialized as a
  gated generator.
- LLM candidate rows often lack enough denominator, currentness, cluster-axis,
  and uncertainty metadata for safe projection.
- Candidate multiplicity has not yet been tested with a fixed downstream
  selector.
- Hidden-family tags are now much better in the follow-up panel, but candidate
  rescue still needs a frozen stress panel before holdout-facing use.

## Decision

RQ1 is answered for validation development:

- Broad LLM candidate generation: rejected as a replacement generator.
- Best LLM component role: selective proposer for unknown, seizure-free,
  conditional, and competing-state candidate rescue.
- Required gate: exact evidence, source trace, max-candidate limit, metadata
  completeness, and deterministic safety floor unless a predeclared rescue
  policy passes changed-row accounting.

## Next Action

Carry fixed deterministic/state-graph candidates into RQ2/RQ4/RQ5. If candidate
generation is revisited, run only a predeclared boundary/uncertainty rescue
experiment with candidate recall, evidence exactness, burden, and metadata
metrics, not aggregate validation F1.
