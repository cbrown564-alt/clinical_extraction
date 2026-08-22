# Method × stage grid: methods against extract / encode / select

Date: 2026-08-20
Revised: 2026-08-22 (Gan cited grid is five methods)
Status: paper source; development illustrations only
Owners: [methods](../../paper/methods.md), [claims](../../paper/claims.md),
this file for the worked reading

The cited Gan table is five methods — **Rules**, **Rules then LLM**,
**LLM then rules**, **LLM then select rules**, **LLM** — against
stages **extract**, **encode**, and **select**. ExECT keeps four
methods. Locked Gan totals:
[five-cell grid](../gan2026/gan_five_cell_grid_2026-08-22.md).
This page is the plain-language owner for what those cells are, how
they run on one Gan letter and one ExECT letter, and what the full
design is worth. Replayable numbers stay in
[`paper_experiments/`](../../../paper_experiments/README.md). What a
sentence may say stays in [claims](../../paper/claims.md).

These examples are development letters. They explain a mechanism. They
are not holdout component estimates. The locked Gemini `test450`
grid is in [README](../../../README.md) and
[claims](../../paper/claims.md). Do not inspect `test450` or
`test60` rows.

## What the design is

The proposed method translates a clinic letter into structured clinical
facts in a designed form, with quoted source text. A model collects a
ledger. Recorded rules then shape that ledger. The same saved model
output can be replayed through those rules without a new call.

The framing is **four methods × three stages**:

- **Rules** — no model. One submitted answer, shown in all three
  stage columns. That rule set is not the encode/select stack on a
  model ledger.
- **LLM** — model only. Extract is the parsed `gan_llm_with_rules` /
  `exect_llm_only` ledger. Encode and select are later-stage model
  calls on that ledger.
- **LLM then rules** — `gan_llm_with_rules` / `exect_llm_only`.
  Extract, encode, and select are the three stops on that raw.
- **Rules then LLM** — `gan_llm_pre_post` / `exect_llm_pre_post`.
  Extract, encode, and select are the three stops on that raw.

The two public golds are evaluation forms, not the task. Gan asks for
one current seizure-frequency label. ExECT asks for a complete
four-family inventory. The cells use the same names on both tasks.
The scores do not move between tasks.

A later cell is not automatically better. A recorded hop is not a
clinically correct step. The score is how the submitted answer is
judged. Do not recode the stack; this is a refile of the claim.

## The grid

| | Extract | Encode | Select |
| --- | --- | --- | --- |
| **Rules** | `gan_rules` / `exect_rules`. Same score in every stage column. | same | same |
| **LLM** | Parsed model ledger. Blank Gan `final_label` stays unscorable. Not `gan_llm_only`. | Gemini `gan_llm_encode` / `exect_llm_encode`. | Gemini `gan_llm_select` / `exect_llm_select`. |
| **LLM then rules** | `gan_llm_with_rules` / `exect_llm_only` extract stop. | Encode stop on that raw. | Select stop on that raw. |
| **Rules then LLM** | `*_pre_post` extract stop. | Encode stop on that raw. | Select stop on that raw. |

Three hop effects on one raw support the reading (the paper table need
not list every revise subtype):

- **Dialect** — same-fact writing (`mgs`→`mg`, brand→generic, word numbers).
- **Encode** — codebook / designed form / Gan selected-evidence renderer.
- **Select** — gate, drop, rewrite, reselect, invent.

On Gan, LLM then rules is the three stops on one
`gan_llm_with_rules` raw. Rules then LLM is the three stops on one
`gan_llm_pre_post` raw. LLM encode and select are later-stage
Gemini calls. Tables cite Gemini 3.7 Flash. Luna is the development
iterator for the Rules then LLM request.

On ExECT, LLM then rules is the three stops on one `exect_llm_only`
raw. Rules then LLM is the three stops on living
`exect_llm_pre_post`. `exect_llm_with_rules` is the live alias.

The paper records every submitted-answer version as a hop log. A
**score projection** converts the submitted answer to the unit the
benchmark scores. It can discard distinctions that remain in the
object.

## Gan worked example: a bound becomes a gold label

**Letter:** Gan development source row `10`. **Model:** Grok 4.6.
**Shared raw:** `gan_llm_with_rules`. **Score:** Purist.
**Artifacts:** `paper_experiments/gan/rungs/grok46/dev750/` and
`paper_experiments/gan/gan_llm_with_rules/grok46/dev750/`.

The letter states a current rate as an upper bound:

> the observed frequency is noted as ≤ four per day, with variable clustering

Gold is `4 per day`. That is a Gan gold-dialect convention. The bound
stays in the quoted span. It is not in the submitted label.

| | Extract | Encode | Select |
| --- | --- | --- | --- |
| **Rules** | `4 per day` (correct) | same | same |
| **LLM** | `≤ 4 per day` (incorrect) | — | — |
| **Hybrid** | — (other request) | `4 per day` (correct) | `4 per day` (correct) |

LLM extract and hybrid encode / select share one Grok
`gan_llm_with_rules` output. The model already selected the
accommodation-log event. LLM extract keeps the inequality, so Purist
misses. Hybrid encode **encodes** that already chosen event into the
evaluation form and does not change `selected_event_ids`. Hybrid
select does not switch the event on this letter.

This is why encode exists as its own stop. The clinical fact is the
same rate the model chose. The designed form is a different string.
Turning selected-evidence repair off disables that whole renderer, not
only bound flattening. The same raw can be replayed with the renderer
off. Hybrid extract is a different request (`gan_llm_pre_post`),
not a replay of this letter's `gan_llm_with_rules` raw.

**Contrast, still development:** source row `15431`. Gold is the
two-part cluster label `1 cluster per 4 month, 5 per cluster`. Rules
submit that label and are Purist-correct. LLM extract writes a long
cluster-after-quiet phrase and misses. Hybrid encode and hybrid
select both submit `seizure free for multiple month` and miss. Select
does not recover a two-part cluster once the model has collapsed the
reading. Visibility is the point: the hops name the collapse.

## ExECT worked example: a hedge becomes a diagnosis concept

**Letter:** ExECT development `EA0007`. **Model:** Grok 4.6.
**Shared raw for cells 2–4:** `exect_llm_only`. **Cell 5:** living
`exect_llm_pre_post`. **Score:** four-family clinical fact F1.
**Artifacts:** `paper_experiments/exect/rungs/grok46/dev140/` and
`paper_experiments/exect/exect_llm_pre_post/grok46/dev140/`.

The letter quotes a hedge on onset:

> Diagnosis: epilepsy – unclassified

and

> Seizure type and frequency: seizures every 3 to 4 weeks, possibly focal onset

Grok put that hedge on the collected evidence. LLM extract keeps Diagnosis
as the written `epilepsy` mention. Cell 3 (encode-replay) may attach a
CUI or respell closed-vocab fields; that is **encode**, not a concept
rewrite. ExECT encode-replay includes CUI attach, so the encode cell is
not “spelling only.” Cell 4 runs the diagnosis dictionary and records
`focal epilepsy`. That is **select** of the concept, not encode.

ExECT encode is codebook attach, attribute canonicalize,
prescription name/unit/dose, seizure-frequency encoding, and
investigation attribute strip. Evidence reject, SF state projection,
unknown suppression, and family lenses are clinical revise and
land on cell 4.

Living cell 5 on the same letter has hybrid headline F1 1.0 and
four-family letter-exact true. The unrepaired hybrid raw on that
request is not schema (cell 2). Cell 2 is the separate `exect_llm_only`
call.

The rewrite is a task-format commitment. It is not an unqualified
clinical diagnosis. The object keeps the quoted hedge, the named
dictionary rule, and the submitted concept. A reader can disagree with
the mapping without losing the span.

## What the full design is worth

The value is the recorded object and the ability to stop the stack,
not a promise that the last cell always wins.

1. **The same names on two questions.** Gan selects one current state.
   ExECT inventories four families. Readers can compare the reported
   cells without pretending the scores are interchangeable.
2. **Replay without a new call.** Cells 2–4 are readings of one saved
   `raw_output`. An encode-only stop and a full revise can be shown on
   the same model text.
3. **Encode and revise stay separable.** Gan row 10 is encode of an
   already chosen event into the evaluation form. ExECT `EA0007` is
   revise of the concept at the revise stop. Calling both “repair” would hide
   which class of change occurred. ExECT’s encode cell already includes
   CUI attach on encode-replay.
4. **The score can throw distinctions away.** Purist accepts `4 per
   day` and rejects `≤ 4 per day` on the same span. Clinical fact F1
   can match gold after a dictionary rewrite. The object still holds
   the bound and the hedge.
5. **Rules only is a baseline, not the post stack.** On row `15431`
   standalone rules get the cluster gold and the model-led cells do
   not. On the locked Gan set, cell 4 beats that baseline in the
   aggregate. Those facts can both be true because they compare
   different objects.
6. **Pre-suggestion is a different request.** Candidates in the prompt
   change what the model is asked to collect. That is why ExECT cell 5
   is living `exect_llm_pre_post`, and why an unrepaired hybrid answer
   is not ExECT schema.

The files do not support a claim that every deterministic step is
safe, that a visible hop is clinically correct, that development hop
shares are holdout effects, or that one extraction already serves a
second use case.

## Where to read next

| Need | File |
| --- | --- |
| Gan Gemini reading of this grid | [rules and models across stages](gan_rules_and_llms_across_stages_2026-08-21.md) |
| Locked wording | [claims](../../paper/claims.md) |
| Identities, splits, scorers | [methods](../../paper/methods.md) |
| Named schema / format / post rules | [rule catalogue](rule_catalogue_schema_format_post_2026-08-21.md) |
| Why a model plus recorded rules | [hybrid architecture](why_hybrid_architecture_2026-08-09.md) |
| The two golds | [what the two golds already decided](what_the_two_golds_already_decided_2026-08-17.md) |
| Earlier pair of reviewable traces | [reviewable case pair](reviewable_case_pair_2026-08-09.md) |
| Replayable cells | [`paper_experiments/`](../../../paper_experiments/README.md) |
