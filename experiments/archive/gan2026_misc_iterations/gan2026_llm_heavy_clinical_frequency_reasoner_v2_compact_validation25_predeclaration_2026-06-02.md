# Gan 2026 LLM-Heavy V2 Compact Validation25 Predeclaration

- Pipeline family: `llm_heavy_clinical_frequency_reasoner`
- Prompt version: `gan2026_llm_heavy_clinical_frequency_reasoner_v2_compact`
- Split/surface: first 25 `validation` rows under `gan2026_split_v1`
- Model: `openai/gpt-4.1-mini`
- Mode: live hosted smoke, cache-first through `gan2026-llm-experiment`
- Claim language: validation development smoke only; not a benchmark result

## Hypothesis

The rejected v2 validation25 run was blocked mainly by output-contract
compactness, omitted `final_answer.selected_event_ids`, non-selected
administrative evidence copying, and one cluster-cadence semantic miss. A
smaller v2 contract should improve schema/evidence reliability without adding
deterministic semantic replacement.

## Minimal Revision

- Rename the prompt artifact to
  `gan2026_llm_heavy_clinical_frequency_reasoner_v2_compact`.
- Keep `final_answer.selected_event_ids` mandatory and explicitly require it to
  equal `selection.selected_event_ids`.
- Make non-prediction-bearing final-answer prose fields optional in the parser
  and move them to optional prompt fields.
- Instruct the model to omit administrative, medication, plan, and
  no-reference events unless they are necessary for the final answer and can
  copy exact note evidence.
- Clarify that cluster cadence is not events-per-cluster: evidence such as
  events clustering every N days should render one cluster occurrence per
  interval unless the selected evidence also states per-cluster burden.

## Evaluation

Run only:

```bash
gan2026-llm-experiment --pipeline llm_heavy_clinical_frequency_reasoner --mode live --limit 25 --model openai/gpt-4.1-mini --jsonl experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_compact_2026-06-02.jsonl --markdown experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_compact_2026-06-02.md
```

Report raw model-owned, format-only, selected-evidence-arithmetic,
benchmark-aligned, and oracle-format layers. Deterministic selected-evidence
arithmetic remains a side-car only.

## Stop Rule

Apply decision 0006 unchanged:

- 25/25 structured outputs.
- At least 24/25 raw parser-compatible labels.
- At least 23/25 exact selected-evidence spans.
- 0/25 selected-event trace mismatches.
- Raw model-owned Purist at least 20/25, unless row review shows every raw miss
  is a predeclared benchmark-format convention.
- Deterministic selected-evidence arithmetic improves no more than five rows
  over raw model-owned labels.

Escalation to validation50 is disallowed unless this smoke passes the stop
rules. No train or locked-test rows will be inspected.
