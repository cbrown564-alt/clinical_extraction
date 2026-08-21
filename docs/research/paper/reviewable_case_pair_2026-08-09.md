# Two reviewable evidence-to-output cases

Date: 2026-08-19  
Status: paper source; paired case collection; Grok 4.6 cited traces

## Purpose and boundary

These two existing development cases answer one question: how does the
proposed method keep the selected letter span, name the rule that changed
it, and still submit a designed structured form?

The examples are reproduced from living Grok 4.6 paper cells by replaying
saved `raw_output` (no new model calls). They illustrate the recorded
object under task-specific golds. They do not establish absolute clinical
truth, clinical safety, or holdout performance.

## Gan 2026: a bounded rate becomes one current label

**Case:** validation source row `10`, Grok 4.6, `gan_llm_with_rules`, Purist
scoring. Cell:
`paper_experiments/gan/gan_llm_with_rules/grok46/dev750/`.

**Task question:** what single current seizure-frequency label should this
letter receive?

**Selected evidence:**

> the observed frequency is noted as ≤ four per day, with variable clustering

**Important decision:** Grok selected that accommodation-log event
(`raw_value` `≤ four per day`). The living stack recorded
`final_label_repaired: '≤ 4 per day' -> '4 per day'`. Final Purist output
is `4 per day`, matching gold. Grok LLM-only on the same row is also
`4 per day` Purist-correct; the bound collapse is visible on the hybrid
trace.

| Step | Recorded value |
| --- | --- |
| Selected event raw value | `≤ four per day` |
| Label repair | `≤ 4 per day` → `4 per day` |
| Final hybrid output | `4 per day` |
| Gan gold label | `4 per day` |
| Score projection | Monthly Purist band match |
| Recorded effect | Gold-dialect match; bound kept in the span, not in the label |

**Why it is reviewable:** the object keeps the exact span, the named repair,
and the submitted label. The same model output can be replayed with that
repair off.

**Limit:** this is a Gan gold convention, not lost evidence. Turning
selected-evidence repair off disables the whole renderer, not only
bound-flattening. This gold still scores `4 per day`.

## ExECTv2: a quoted hedge becomes a diagnosis concept

**Case:** development letter `EA0007`, Grok 4.6, `exect_llm_with_rules`,
Diagnosis family. Cell:
`paper_experiments/exect/exect_llm_with_rules/grok46/dev140/`.

**Task question:** which diagnosis concepts should the structured phenotype
contain?

**Selected evidence:**

> Diagnosis: epilepsy – unclassified

and

> Seizure type and frequency: seizures every 3 to 4 weeks, possibly focal onset

**Important decision:** Grok quoted both spans. Hybrid Diagnosis mentions
are `epilepsy – unclassified` plus `focal epilepsy`. The second mention
records `rewrote_diagnosis_convention_from_dictionary` from the quoted
hedge *“possibly focal onset”*. Hybrid Diagnosis family letter-exact is
true; four-family letter-exact is true; hybrid headline F1 is 1.0. Grok
LLM-only on its own request has raw F1 0.8333 and is not four-family
exact.

This is **not** the retired Sol unquoted-letter add. Grok put the hedge
on the seizure-frequency (and diagnosis) evidence span.

| Step | Recorded value |
| --- | --- |
| Heading diagnosis | `epilepsy – unclassified` |
| Quoted hedge | `possibly focal onset` |
| Dictionary rewrite | `focal onset` → `focal epilepsy` |
| Submitted diagnosis set | Includes `focal epilepsy` |
| Hybrid Diagnosis letter-exact | true |
| Hybrid headline F1 | 1.0 |

**Why it is reviewable:** a reviewer can see both source phrases, the
hedge, the dictionary owner, the submitted concept, and the family score.

**Limit:** “possibly focal onset” is uncertain language. The example shows
an inspectable task-policy decision, not an unqualified clinical
diagnosis.

## Evidence lanes

- **Dataset evidence** supplies each task question and gold label.
- **Project evidence** supplies the selected spans, repair notes, and
  living paper-cell paths.

Claim strength remains governed by
[paper claims](../../paper/claims.md).
