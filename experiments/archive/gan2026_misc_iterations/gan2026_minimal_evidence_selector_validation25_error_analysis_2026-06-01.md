# Gan 2026 Minimal Evidence Selector Validation25 Error Analysis

Date: 2026-06-01

This note compares the GPT-4.1 mini `llm_only_minimal_evidence_selector_v0`
validation25 run with LLM-only claim-table selector runs on the same validation
prefix. It is development error analysis only, not holdout evidence.

## Compared Artifacts

- Minimal evidence selector:
  `experiments/gan2026_llm_only_minimal_evidence_selector_validation25_v0_2026-06-01.jsonl`
- Section claim-table v4:
  `experiments/gan2026_section_claim_table_validation25_gpt41mini_v4_2026-06-01.jsonl`
- Claim-table selector v5:
  `experiments/gan2026_llm_only_claim_table_selector_validation25_gpt41mini_v5_2026-06-01.jsonl`
- Structured-events v0.5 strict-format replay:
  `experiments/gan2026_llm_structured_validation25_gpt41mini_v05_strict_format_smoke_2026-06-01.jsonl`

## Score Contrast On The Same 25 Rows

| Pipeline | Raw scorable | Raw Purist | Strict Purist | Clean Purist | Main failure mode |
| --- | ---: | ---: | ---: | ---: | --- |
| Minimal evidence selector v0 | 2 / 25 | 2 / 25 | 15 / 25 | 16 / 25 | Source-near answer text remains scorer-unparsable |
| Section claim-table v4 | 25 / 25 | 25 / 25 | 25 / 25 | 25 / 25 | One non-selected claim evidence issue only |
| Claim-table selector v5 | 22 / 25 | 22 / 25 | 22 / 25 | 22 / 25 | Two schema failures plus one scorer-format miss |
| Structured-events v0.5 strict-format replay | 0 / 25 in score_layers; report score 17 / 25 | n/a | n/a | 17 / 25 report score | Narrow strict repair leaves several source-near labels unscorable |

The minimal selector is not worse because GPT-4.1 mini failed to find the
relevant seizure-frequency text. It is worse because the simplified contract
made the source-near answer itself prediction-bearing, while the better
claim-table runs made a separate parser-ready `final_label` prediction-bearing.

## Row-Level Failure Families

The minimal run has 9 clean Purist failures. All 9 are unscorable after clean
repair:

| Family | Rows | What happened |
| --- | --- | --- |
| Inequality retained | 40, 103 | The model kept `<=` plus prose/range wording; repair converted words but did not remove the upper-bound operator in these forms. |
| Prose around every-interval retained | 182, 212, 243 | Repair changed `every` to `1 per`, but left leading prose such as `are occurring`, `ongoing occurring`, or `occur`. |
| Cluster cadence expressed as prose cluster label | 187, 190 | The model correctly found the cadence but marked it as `cluster_frequency`; scorer expected either ordinary cadence `1 per ...` or a full cluster dual-axis label. |
| Vague quantity phrase retained | 278, 338 | The model kept source wording like `multiple times in past week` and `many convulsions in past month`; claim-table prompts convert these to accepted category labels. |

There were no minimal JSON/schema failures and no alias repairs. Evidence was
mostly exact: answer evidence 24 / 25 and supporting-fact evidence 49 / 50. The
single exactness miss was row 243, where the output used a non-exact casing or
substring variant for the selected evidence.

## Why The Contracts Behave Differently

The minimal prompt explicitly asks for `answer.answer_text` to be
source-near. It even gives examples such as `<= four per day`, `no seizures for
six months`, and `unknown`. That improves portability and local-model contract
simplicity, but it removes the strongest instruction from claim-table v4/v5:
produce a Gan-compatible parser-ready `final_label`.

Claim-table v4/v5 separate three things that the minimal contract collapses:

1. `raw_frequency`: source-near text copied from the note.
2. `final_label`: scorer-facing normalized answer.
3. `conversion_note` / selector fields: the model's explanation of how it moved
   from source wording to Gan-compatible label.

The minimal contract has only `answer_text` plus deterministic downstream
repair. That downstream repair is intentionally conservative and frozen. It can
handle some simple surfaces, such as `seizures every 6 days` -> `1 per 6 day`,
but it is not a semantic converter for every source-near phrase. The result is
a clean output contract but a weak scorer-facing contract.

The minimal prompt also tells the model not to emit `cluster_axis`,
`boundary_state`, `selector_decision`, `temporality`, `assertion_status`,
`section`, or `semiology`. That is useful for minimizing the schema, but it
means the sidecar has to infer these fields after the fact from text. For
scoring, the bigger loss is cluster-axis ownership: claim-table v5 can say a
cluster statement is `cadence_only` and still emit `1 per 7 to 9 day`; minimal
can only say `state=cluster_frequency` with prose in `answer_text`.

Max tokens is unlikely to be the primary cause. The minimal output is much
shorter than claim-table output and was contract-complete in 25 / 25 rows. The
observed failures are format/normalization failures, not truncation failures.

## Detailed Example: Row 187

Gold: `1 per 7 to 9 day`.

Minimal output:

```json
{
  "answer": {
    "state": "cluster_frequency",
    "answer_text": "events tend to cluster every seven to nine days",
    "evidence": "Since the last review, Ms Aisha Rahman reports that events tend to cluster every seven to nine days",
    "confidence": "high"
  },
  "supporting_facts": [
    {
      "fact_id": "f1",
      "role": "selected",
      "state": "cluster_frequency",
      "fact_text": "Since the last review, Ms Aisha Rahman reports that events tend to cluster every seven to nine days",
      "evidence": "Since the last review, Ms Aisha Rahman reports that events tend to cluster every seven to nine days"
    },
    {
      "fact_id": "f2",
      "role": "context",
      "state": "frequency",
      "fact_text": "Over the same interval, there have been two nocturnal generalised tonic-clonic seizures, each under two minutes",
      "evidence": "Over the same interval, there have been two nocturnal generalised tonic-clonic seizures, each under two minutes"
    }
  ]
}
```

Minimal score path:

- Raw label: `events tend to cluster every seven to nine days`
- Strict/clean label: `tend to cluster every 7 to 9 day`
- Error: `Unparsable cluster label`

The clinical selection is basically right: the model selected the ongoing
cluster cadence over the lower-burden recent nocturnal seizure count. The
failure is the representation boundary. Because the answer state is
`cluster_frequency`, the scorer treats the repaired label as a cluster label,
but it is only a cadence. It lacks a full cluster burden such as
`1 cluster per month, 6 to 7 per cluster`, and it is not normalized into the
ordinary cadence form `1 per 7 to 9 day`.

Claim-table v4 on the same row:

- Claim c1: `claim_type=cluster_frequency`, `raw_frequency=every seven to nine days`
- Final query: `final_label=1 per 7 to 9 day`
- Conversion note: selected cluster cadence as the primary current seizure
  frequency and preserved it as `1 per 7 to 9 day`
- Clean Purist: correct

Claim-table v5 improves the ownership further:

- Claim c1: `claim_type=frequency`, `cluster_axis=cadence_only`,
  `boundary_state=ordinary_frequency`
- Final query: `final_label=1 per 7 to 9 day`, `selector_decision=preserve_cluster_axis`
- Clean Purist: correct

So row 187 is not evidence that the minimal model cannot reason about the note.
It is evidence that the minimal schema removed the field where the model was
previously doing the needed conversion.

## Detailed Example: Row 40

Gold: `4 per week`.

Minimal output selected the right evidence and answer family:

- `answer_text`: `<= four seizures per week`
- evidence: `overall a frequency of <= four seizures per week`
- raw score: unscorable
- strict/clean label: `<= 4 per week`
- clean score: still unscorable

Claim-table v4/v5 both output the same source-near value in the claim table but
then convert the final answer:

- `raw_frequency`: `<= four seizures per week`
- `final_label`: `4 per week`
- conversion note: use the maximum current frequency
- clean score: correct

This is the simplest form of the difference. The minimal run preserves the
clinically cautious upper-bound wording; the benchmark scorer expects the
Gan-compatible maximum label. Because clean scorer-facing repair is frozen and
conservative, it does not silently decide that every `<= X per unit` should be
scored as `X per unit`.

## Likely Causes Ranked

1. Missing parser-ready final-label field. This is the dominant cause on this
   slice. The minimal answer is source-near by design; the better claim-table
   pipelines ask the model to emit both source-near and Gan-facing forms.
2. Prompt instruction conflict. The minimal prompt says the prediction-bearing
   answer should be source-near, while scoring expects normalized Gan labels.
   That pushes work into deterministic repair that the experiment intentionally
   kept narrow.
3. Cluster-axis information moved out of the model boundary. The minimal schema
   derives `cluster_axis` after the fact and cannot ask the model to distinguish
   cadence-only clusters from true cluster burden in the final selector.
4. Reduced selector scratch space. Supporting facts are useful for evidence,
   but they do not carry temporality, assertion, section, semiology, uncertainty,
   conversion notes, or selected-claim rationale. On this slice selection mostly
   survived, but this design gives the model less structure for hard conflicts.
5. Conservative frozen repair. This is desirable for attribution, but it means
   many natural expressions remain unscorable: `<= 4 per week`,
   `multiple times in past week`, `many convulsions in past month`, and prose
   around `every` intervals.

## Interpretation

The minimal evidence selector succeeded as an output-contract and evidence
smoke: strict JSON, shallow schema, exact evidence, and complete derived review
projection were mostly achieved. It failed as a scorer-facing baseline because
the simplified contract omitted the parser-ready label conversion that made
claim-table v4/v5 strong on this prefix.

For Qwen transfer, this is still useful: the first question is whether Qwen can
emit strict JSON with correct answer state and exact evidence under the minimal
schema. But its Purist/Pragmatic score should be interpreted as a mixed measure
of answer selection plus downstream normalization weakness, not as a clean
measure of clinical reasoning.

The next design fork is explicit:

- Keep the minimal contract as-is for local-model schema-transfer diagnostics,
  and report low raw/clean score as expected scorer-facing incompleteness.
- Or add one small field, `answer.final_label`, with a strict Gan-compatible
  parser-ready instruction. That would test whether a still-small schema can
  recover the v4/v5 scoring benefit without reintroducing the full claim table.
