# Gan 2026 LLM-Structured V0.5 Repair Audit

Date: 2026-06-01

Audited artifact:

- Markdown report: `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion_2026-06-01.md`
- JSONL artifact: `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion_2026-06-01.jsonl`
- Split: `validation`, `gan2026_split_v1`
- Model: `openai/gpt-4.1-mini`
- Prompt/program: `gan2026_llm_structured_event_selector_v0.5`

This is a validation development audit. It is not a final holdout result and
should not be described as a benchmark result.

## Executive Summary

The v0.5 structured pipeline should not currently be described as a clean
LLM-first extractor whose score mainly reflects model selection quality. The
prompt does omit gold labels and deterministic candidate diagnostics, and there
is no evidence in this audit that gold labels are passed to the model or used
directly at inference time. However, the post-LLM repair layer has grown into a
substantial deterministic clinical and benchmark-shaping rule stack.

The reported validation score is therefore best interpreted as:

```text
GPT-4.1 mini structured event extraction plus a large Gan-specific
post-processing rule stack reaches 0.8938 Purist on 650 validation rows.
The contribution of the LLM selection versus deterministic benchmark repair is
not yet isolated.
```

The main concern is not hard leakage. The main concern is attribution and
generalization. Many repairs are benign label-format canonicalizations, but many
others replace the selected LLM label with a different clinical interpretation
derived from selected evidence, unselected events, note text, clinic dates,
monthly diaries, and Gan-specific conventions. Some of these repairs look like
rules built around recurring synthetic validation-row families.

## Headline Metrics

From the audited JSONL:

```text
Rows: 650
Structured records: 650 / 650
Call failures: 0
Parse/schema/label issues: 0
Rows with deterministic repair notes: 397
Repair notes total: 430
Exact selection evidence substrings: 619 / 650
Reported Purist validation accuracy/micro F1 proxy: 0.8938 (581 / 650)
Reported Pragmatic validation accuracy/micro F1 proxy: 0.9108 (592 / 650)
```

Approximate contribution of the full repair stack, comparing raw LLM
`selection.final_label` after basic label parsing against the final post-repair
label:

```text
raw correct -> final correct:   455
raw wrong   -> final correct:   126
raw wrong   -> final wrong:      63
raw correct -> final wrong:       6
```

This means the repair stack accounts for a large share of the reported Purist
result. It fixes roughly 126 rows that the raw selected label would not have
scored correctly, while introducing roughly 6 category regressions.

## Pipeline Mechanics

### Prompted LLM Stage

The prompt is built in `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_structured.py`.
It includes only:

- the source note text
- a slim event schema
- selection instructions
- output-format constraints

It explicitly says deterministic rule candidates are not provided. Gold labels
are not included in the prompt payload.

The model returns:

```text
events[]:
  event_id
  kind
  raw_value
  applies_to
  time_window
  temporality
  assertion_status
  evidence
  notes

selection:
  selected_event_ids
  final_kind
  final_label
  evidence
  confidence
  rationale
```

### Post-LLM Stage

`parse_structured_json(...)` then applies a chain of deterministic operations:

1. JSON extraction and schema repair.
2. Pydantic validation.
3. Per-event Gan normalization.
4. Resolve the selected final label.
5. Repair the final label using selected evidence.
6. Override with monthly diary aggregation when detected.
7. Override with "usual interval" when detected.
8. Override unknown/no-reference with breakthrough count after seizure-free interval.
9. Override unknown/no-reference for current non-epileptic events.
10. Override using residual jerk/date-anchor logic.
11. Override seizure-free or high-frequency labels using post-change burst logic.
12. Override using dated sequence logic.
13. Override seizure-free labels using elapsed-since-anchor logic.
14. Parse the final repaired label for scoring.

Steps 5 through 13 are the core audit concern. They go well beyond benchmark
format repair in many rows.

## Repair Taxonomy

The audit bucketed the 430 repair notes as follows. These buckets are heuristic
and intended for triage, not as final labels.

```text
format/unit canonicalization:        86
frequency -> different frequency:   105
frequency -> sentinel/unknown:       83
seizure-free -> frequency:           29
sentinel -> frequency:               15
other repair:                       112
```

### Low Concern: Format Canonicalization

These repairs keep the clinical meaning stable while making the label acceptable
to the Gan parser.

Examples:

```text
1 per 6 days -> 1 per 6 day
seizure free for 9 months -> seizure free for 9 month
12 to 30 per quarter -> 12 to 30 per 3 month
2 to 3 per fortnight -> 2 to 3 per 2 week
```

These should remain allowed as benchmark-format repairs, provided they are
audited separately from semantic overrides.

### Medium Concern: Source-Evidence Arithmetic

These repairs compute a more benchmark-shaped label from explicitly selected
source evidence.

Examples:

```text
multiple per month -> 64 per 12 month
9 per year -> 9 per month
less than 1 per month -> 5 to 7 per 10 month
```

Some of these are clinically defensible, especially diary summations. They
should still be separated from pure LLM performance because deterministic code
is doing meaningful extraction work.

### High Concern: Semantic Overrides

These repairs replace the model's selected semantic state with another state.

Examples:

```text
unknown -> seizure free for multiple year
no seizure frequency reference -> 1 per 6 month
seizure free for 6 month -> 2 per 6 month
seizure free for multiple year -> 10 per 6 week
multiple per hour -> no seizure frequency reference
most weekdays -> no seizure frequency reference
```

These should not be counted as mere repair. They should either be promoted to
explicit candidate rules with their own ablation, or removed from the LLM-first
claim path.

## End-to-End Example Classes

### 1. Benign Grammar Repair

Row 156:

```text
Gold:       1 per 6 day
LLM raw:    1 per 6 days
Final:      1 per 6 day
Repair:     1 per 6 days -> 1 per 6 day
Evidence:   Patient reports seizures every 6 days...
Assessment: Acceptable benchmark grammar repair.
```

### 2. Inequality Or Approximation Normalization

Row 103:

```text
Gold:       2 to 4 per year
LLM raw:    2 to 4 per year
Final:      2 to 4 per year
Evidence:   current pattern is <= two or four per year
Assessment: Reasonable conversion from source phrase to Gan-compatible range.
```

Rows 10, 40, and 79 show similar repairs from "up to" or "<=" into a bounded
numeric label. These often improve score, but the evidence still contains the
count and unit.

### 3. Cluster Reconstruction

Row 3224:

```text
Gold:       1 cluster per month, 6 to 7 per cluster
LLM raw:    6 to 7 per month
Final:      1 cluster per month, 6 to 7 per cluster
Repair:     6 to 7 per month -> 1 cluster per month, 6 to 7 per cluster
Evidence:   Monthly clusters, typically 6 to 7 seizures over 24 h.
Assessment: Clinically plausible, but not just formatting. The repair layer
            reconstructs a cluster label from the evidence.
```

Cluster reconstruction is especially score-active because raw labels like
`1 cluster per week` are often unparsable or scored as unknown before repair.

### 4. Monthly Diary Arithmetic

Row 13627:

```text
Gold:       64 per 12 month
LLM raw:    multiple per month
Final:      64 per 12 month
Repair:     multiple per month -> 64 per 12 month
Evidence:   May: 5, June: 5, July: 12, August: 3, September: 12,
            October: 3, November: 7, December: 5, January: 4,
            February: 2, March: 5, April: 1
Assessment: The deterministic layer sums the diary and constructs the label.
            This is useful, but it is not LLM-only selection.
```

This family should probably become an explicit deterministic arithmetic module,
with separate reporting.

### 5. Year-To-Date / Elapsed-Window Conversion

Row 12823:

```text
Gold:       9 per month
LLM raw:    9 per year
Final:      9 per month
Repair:     9 per year -> 9 per month
Evidence:   just nine generalised tonic-clonic seizures documented this year to date
Assessment: Potentially benchmark-compatible, but clinically fragile. It relies
            on clinic-date context and Gan-specific interpretation of "this year
            to date". This should be isolated in ablation.
```

This family is high-risk for validation overfitting because the denominator can
change categories dramatically.

### 6. Last-Event Converted To Frequency

Row 13149:

```text
Gold:       3 per year
LLM raw:    3 seizures 2 weeks ago
Final:      3 per 1 year
Repair:     3 seizures 2 weeks ago -> no seizure frequency reference
            no seizure frequency reference -> 3 per 1 year
Evidence:   no seizures for nearly a year ... then developed ... 3 tonic seizure
Assessment: The final answer is benchmark-compatible, but the repair converts a
            last-event statement plus prior seizure-free interval into a rate.
            This is a semantic benchmark inference, not format repair.
```

This is one of the clearest examples where the repair layer acts as a candidate
extractor.

### 7. Seizure-Free Reversed Into Frequency

Row 14645:

```text
Gold:       2 per 6 month
LLM raw:    seizure free for 6 month
Final:      2 per 6 month
Repair:     seizure free for 6 month -> 2 per 6 month
Evidence:   first seizure occurred in May 2018 ... second event was in November 2018 ...
Assessment: Very high concern. The selected LLM answer is seizure-free, but the
            repair layer uses historical dated events to construct the gold-like
            rate. This should not be presented as selected-label repair.
```

### 8. Repair-Induced Regression

Row 14282:

```text
Gold:       multiple per month
LLM raw:    seizure free for 6 weeks
Final:      10 per 6 week
Repair:     seizure free for 6 weeks -> seizure free for multiple year
            seizure free for multiple year -> 10 per 6 week
Evidence:   In the following week, he had several seizures ... No further seizures...
Assessment: The repair family is brittle. It can over-convert seizure-free
            follow-up phrasing into a recent burst frequency and produce a wrong
            category.
```

### 9. Scoring Collapse Hides Semantic Error

Row 744:

```text
Gold:       multiple per week
LLM raw:    most weekdays
Final:      no seizure frequency reference
Repair:     most weekdays -> no seizure frequency reference
Purist:     reported yes
Assessment: Clinically wrong final label, but Purist category still passes
            because scoring collapses some unknown/no-reference/multiple states.
```

Row 4690:

```text
Gold:       multiple per day
LLM raw:    multiple per hour
Final:      no seizure frequency reference
Repair:     multiple per hour -> no seizure frequency reference
Evidence:   Electrographic seizures frequent on EEG (~ten/h)
Purist:     reported yes
Assessment: Clinically unacceptable as a final extraction label, despite category
            credit.
```

These examples show why exact-label, semantic-state, and evidence-support audits
must accompany Purist/Pragmatic category metrics.

### 10. Non-Epileptic / Sentinel Overrides

Rows such as 5406 show:

```text
unknown -> seizure free for multiple year
```

This can be appropriate when current events are clearly non-epileptic, but it is
a clinical semantic decision. It should be counted as a deterministic candidate
rule and ablated independently.

## Main Risks

### 1. Misattributed Performance

The run summary says deterministic code only repairs labels selected by the LLM.
That is not accurate enough. The repair layer frequently overrides the selected
answer using information outside the final selected label.

### 2. Validation-Set Rule Accretion

Many rules appear to target recurring Gan synthetic idioms:

- seizure-free interval followed by breakthrough count
- "this year to date"
- monthly diary tables
- first/second/third dated event sequences
- cluster days with per-cluster counts
- non-epileptic current event phrasing
- "no further events since" after a burst

These may be legitimate benchmark policies, but they should be documented as
Gan-specific rules and evaluated with ablations.

### 3. Semantic State Collapse

Purist and Pragmatic categories can hide important differences among:

- `unknown`
- `no seizure frequency reference`
- `multiple per week`
- `multiple per day`
- exact numeric frequency
- seizure-free state

The table's `Purist: yes` column should not be read as exact or clinically
faithful label agreement.

### 4. Evidence Validity Is Not Enough

Exact evidence substring validity checks whether the selected evidence appears
in the note. It does not prove that the final repaired label is entailed by that
evidence. Several repaired labels use unselected events or broader note context.

### 5. Generalization Risk

Rules that construct denominators from clinic dates, infer rates from last-event
statements, or flip seizure-free to frequency may fit Gan synthetic conventions
but fail on real clinical letters or future benchmarks.

## Recommended Claim Language

Avoid:

```text
The LLM-structured pipeline reaches 0.8938 Purist F1.
```

Prefer:

```text
On 650 validation rows, GPT-4.1 mini structured extraction plus the current
Gan-specific post-processing stack reaches a 0.8938 Purist category accuracy
proxy. This is a validation development result, and the LLM-only contribution is
not yet isolated.
```

For internal shorthand:

```text
v0.5 is a hybrid LLM + deterministic repair candidate, not a clean LLM-first
selection result.
```

## Ablation Plan

The next step should be a no-new-calls replay ablation over the saved raw model
outputs. The goal is to measure which repair families drive the score and which
families create regressions.

### Proposed Ablation Ladder

Run each condition on the same 650 JSONL rows:

```text
A. raw LLM final_label only
B. raw + basic Gan label format repair only
C. + selected-evidence repair
D. + monthly diary arithmetic
E. + usual interval override
F. + breakthrough-after-seizure-free override
G. + non-epileptic override
H. + residual jerk/date-anchor override
I. + post-change burst override
J. + dated sequence override
K. + elapsed-since-anchor override
L. full current stack
```

### Required Outputs

For each ablation condition, report:

- Purist category accuracy
- Pragmatic category accuracy
- exact normalized-label match rate
- semantic-kind match rate
- evidence exact-substring rate
- row count improved versus previous condition
- row count regressed versus previous condition
- top 20 changed rows with raw label, previous label, new label, gold label, and notes

### Minimum Row-Level Slices

Track performance and changes for:

- seizure-free gold rows
- unknown/no-reference gold rows
- cluster gold rows
- monthly diary rows
- year-to-date/current-year rows
- dated sequence rows
- `row_ok=False` rows
- rows where Purist is correct but exact label is wrong

### Decision Criteria

Promote a repair family only if:

- it improves category accuracy without large semantic regressions
- it has a clear clinical or benchmark-policy justification
- it does not depend on validation-specific row wording
- it can be described as normalization/arithmetic rather than hidden clinical
  selection, or is explicitly reclassified as a deterministic rule module

Demote or remove a repair family if:

- it converts seizure-free to frequency without a clear selected-event basis
- it converts unknown/no-reference to numeric frequency from weak anchors
- it turns unsupported or out-of-schema expressions into no-reference while
  receiving category credit
- it mainly helps because of Purist category collapse

## Follow-Up Implementation Notes

The current `parse_structured_json(...)` path should be made configurable by
repair family. A small dataclass or enum set would allow replaying saved raw
outputs without model calls.

Suggested controls:

```text
basic_label_repair
selected_evidence_repair
monthly_diary_repair
usual_interval_repair
breakthrough_repair
non_epileptic_repair
residual_jerk_repair
post_change_burst_repair
dated_sequence_repair
elapsed_anchor_repair
```

The ablation should not change scorer policy, split policy, labels, or prompts.
It should only reparse the existing raw outputs under different deterministic
repair configurations.

