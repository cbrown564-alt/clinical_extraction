# Two reviewable evidence-to-output cases

Date: 2026-08-19
Revised: 2026-08-22 (wording ablation labeled; five role rows)
Status: paper source; paired case collection; Grok 4.6 development traces

## Purpose and boundary

These two existing development cases answer one question: how does the
proposed method keep the selected letter span, name the rule that changed
it, and still submit a designed structured form?

The examples are reproduced from saved Grok 4.6 development cells by
replaying saved `raw_output` (no new model calls). They illustrate the
recorded object under task-specific golds. They do not establish absolute
clinical truth, clinical safety, or holdout performance.

## Gan 2026: a bounded rate becomes one current label

**Case:** validation source row `10`, Grok 4.6, **wording ablation**
`gan_llm_extract_raw` (not the cited codebook recognise), Purist scoring.
Cell:
`paper_experiments/gan/gan_llm_extract_raw/grok46/dev750/`.

**Task question:** what single current seizure-frequency label should this
letter receive?

**Selected evidence:**

> the observed frequency is noted as ≤ four per day, with variable clustering

**Important decision:** Grok selected that accommodation-log event
(`raw_value` `≤ four per day`). Rule encode on that wording-ablation raw
recorded `final_label_repaired: '≤ 4 per day' -> '4 per day'`. Final
Purist output is `4 per day`, matching gold.

| Step | Recorded value |
| --- | --- |
| Selected event raw value | `≤ four per day` |
| Label repair | `≤ 4 per day` → `4 per day` |
| Final output after rule encode | `4 per day` |
| Gan gold label | `4 per day` |
| Score projection | Monthly Purist band match |
| Recorded effect | Gold-dialect match; bound kept in the span, not in the label |

**Why it is reviewable:** the object keeps the exact span, the named repair,
and the submitted label. The same model output can be replayed with that
repair off.

**Limit:** this is a Gan gold convention, not lost evidence. Turning
selected-evidence repair off disables the whole renderer, not only
bound-flattening. This gold still scores `4 per day`. Do not treat this
wording-ablation path as the cited recognise or as preserving clinical
reasoning.

## ExECTv2: a quoted hedge becomes a diagnosis concept

**Case:** development letter `EA0007`, Grok 4.6, cell 2
(`exect_llm_pre_post` / live alias `exect_llm_with_rules`), Diagnosis
family. Cell:
`paper_experiments/exect/exect_llm_with_rules/grok46/dev140/`.

**Task question:** which diagnosis concepts should the structured phenotype
contain?

**Selected evidence:**

> Diagnosis: epilepsy – unclassified

and

> Seizure type and frequency: seizures every 3 to 4 weeks, possibly focal onset

**Important decision:** Grok quoted both spans. Select Diagnosis mentions
are `epilepsy – unclassified` plus `focal epilepsy`. The second mention
records `rewrote_diagnosis_convention_from_dictionary` from the quoted
hedge *“possibly focal onset”*. Diagnosis family letter-exact is
true; four-family letter-exact is true; select F1 is 1.0. Cell 3
(`exect_llm_only` plus rule encode and select) on the same letter is a
separate saved call.

This is **not** the retired Sol unquoted-letter add. Grok put the hedge
on the seizure-frequency (and diagnosis) evidence span.

| Step | Recorded value |
| --- | --- |
| Heading diagnosis | `epilepsy – unclassified` |
| Quoted hedge | `possibly focal onset` |
| Dictionary rewrite | `focal onset` → `focal epilepsy` |
| Submitted diagnosis set | Includes `focal epilepsy` |
| Diagnosis letter-exact | true |
| Select F1 | 1.0 |

**Why it is reviewable:** a reviewer can see both source phrases, the
hedge, the dictionary owner, the submitted concept, and the family score.

**Limit:** “possibly focal onset” is uncertain language. The example shows
an inspectable task-policy decision, not an unqualified clinical
diagnosis.

## Evidence lanes

- **Dataset evidence** supplies each task question and gold label.
- **Project evidence** supplies the selected spans, repair notes, and
  replayable cell paths.

Claim strength remains governed by
[paper claims](../../paper/claims.md).
