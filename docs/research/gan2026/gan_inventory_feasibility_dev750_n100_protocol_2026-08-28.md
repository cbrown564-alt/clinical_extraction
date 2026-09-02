# Protocol: descriptive clinical-inventory feasibility on Gan `dev750`

Date: 2026-08-28
Status: completed 2026-08-28; one frozen pass; no retune
Result: [feasibility report](gan_inventory_feasibility_dev750_n100_2026-08-28.md)
Decision: [Gan is the dissertation paper](../../paper/decisions/gan-is-the-dissertation-paper.md)
Artifact: `experiments/gan_inventory_feasibility_dev750_n100_20260828/`

## Primary question

Can the frozen ExECT-style four-family clinical-inventory program
produce structured descriptions of diagnoses, medicines,
investigations, and seizure-frequency statements from Gan synthetic
letters?

This is a descriptive feasibility study. It sits beside the evaluated
Gan seizure-frequency classification task. It does not ask whether
those extracted facts are correct.

## Why it matters

The dissertation paper now cites Gan only. The Gan gold is one current
seizure-frequency state. The same synthetic letters may still contain
a broader clinical inventory. A frozen, no-tune extract on a
prespecified development sample shows the range and structure of
information the schema can represent, and motivates later expert
annotation on real correspondence.

## Data, split, inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 synthetic letters |
| Split | Paper name `dev750` only. Machine name `validation` (750 letters). |
| Manifest | `data/Gan (2026)/splits/gan2026_split_v1.json` |
| Data file | `data/Gan (2026)/synthetic_data_subset_1500.json` |
| Row policy | All 750 validation letters are eligible. No `row_ok` filter. Do not include `train` or `test`. |
| Inspection | Development letters may be read. |
| Holdout | `test450` is not loaded, not sampled, not inspected, not summarised. |

## Sample

Prespecified before any letter is read for this study.

| Item | Value |
| --- | --- |
| Sample id | `gan_inventory_feasibility_dev750_n100_v1` |
| Size | 100 letters without replacement |
| Pool | Integer `source_row_index` values from `splits.validation`, sorted ascending |
| Draw | `random.Random(20260828).sample(sorted_pool, 100)` |
| Processing order | The selected indices, sorted ascending |

Do not redraw after seeing output. Do not add or drop letters. Do not
tune the pipeline after the sample is drawn.

## Frozen program

| Item | Value |
| --- | --- |
| Entry | `run_letter` |
| Implementation | `run_letter_three_stage(ACCEPTED_THREE_STAGE_CONFIG)` |
| Owner | `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/rules.py` |
| Schema | Four-family inventory: Diagnosis, Prescription, Investigations, SeizureFrequency |
| Stop used for counts | Select-stop four-family mentions |
| Model | None. No LLM calls. |
| Scorer | None. Do not compute precision, recall, F1, or Purist accuracy. |

Adapter: wrap each Gan note as
`ExectLetter(letter_id="gan:{source_row_index}", note_text=record.note_text, annotations=())`.
Empty gold annotations are required. There is no inventory reference
standard on Gan.

Do not use `RECALL_FIRST_THREE_STAGE_CONFIG`,
`TRANSFERRED_RECALL_FIRST_THREE_STAGE_CONFIG`, or
`run_letter_retune_stack`. Do not change `ACCEPTED_THREE_STAGE_CONFIG`.

## Reported outputs

For each family, from the select-stop mentions on the 100 letters:

| Measure | Definition |
| --- | --- |
| Letters containing at least one extracted fact | Count of sampled letters with ≥1 mention in that family |
| Total extracted facts | Sum of that family's mentions across the sample |
| Median and range of facts per letter | Median, min, and max of that family's mention count over all 100 letters, including zeros |
| Common extracted subtypes | Up to five most frequent subtype labels in that family |

Subtype labels, in order of preference:

- Diagnosis: `DiagCategory`, else `CUIPhrase`, else `text`
- Prescription: `DrugName`, else `text`
- Investigations: `MRI:{MRI_Results}`, `CT:{CT_Results}`, or
  `EEG:{EEG_Results}` when a result attribute is present; else `text`
- SeizureFrequency: `FrequencyChange`, else `CUIPhrase`, else `text`

Also report the number of letters with at least one extracted fact in
any family, and the median and range of total four-family facts per
letter.

## Illustration letters

After extraction, choose up to three letters by this fixed rule, not
by post-hoc clinical interest:

1. Keep letters with at least three of the four families present.
2. Sort by fact count descending, then `source_row_index` ascending.
3. Take the first three.
4. If fewer than three remain, repeat with a two-family floor, then a
   one-family floor.

Each illustration shows a high-level letter excerpt (first 500
characters, whitespace collapsed) and the structured four-family
inventory. These are synthetic development letters.

## Artifact schema

Write `experiments/gan_inventory_feasibility_dev750_n100_20260828/`:

- `summary.json`: protocol id, date, commit or dirty-tree note,
  split, sample id, seed, selected indices, program identity, family
  summaries, illustration `source_row_index` list. No precision,
  recall, F1, or accuracy fields.
- `rows.jsonl`: one object per sampled letter with `source_row_index`
  and select-stop mentions (`entity`, `text`, `subtype`, `attributes`,
  `evidence`). No Gan gold inventory labels. No `test450` keys.

## Stop rule

Stop after one frozen pass over the declared 100-letter sample and
the descriptive report. Answer the feasibility question as
descriptive output volume and structure. Do not revise the program
from these letters. Do not expand the sample. Do not load holdout.

Negative result: the schema yields few or no facts. That is still an
answer. It is not a reason to retune.

## Claim boundary

Development descriptive evidence only.

The study may say that the frozen inventory program produced named
counts and subtypes on 100 Gan `dev750` synthetic letters.

It may not say that those facts are precise, complete, clinically
valid, or transferable to real correspondence. It may not cite ExECT
`test60` scores, and it may not treat this sample as a Gan
classification result.
