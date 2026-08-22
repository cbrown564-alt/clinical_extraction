# Method × stage grid: methods against extract / encode / select

Date: 2026-08-20
Revised: 2026-08-22 (wording ablation labeled; five role rows)
Status: paper source; development illustrations only
Owners: [methods](../../paper/methods.md), [claims](../../paper/claims.md),
this file for the worked reading

The cited Gan table is five role rows. Each of **extract**,
**encode**, and **select** is **rules**, **LLM**, or **both**. The
cited score is the select stop. ExECT uses the same five role rows.
Locked Gan totals:
[five-cell grid](../gan2026/gan_five_cell_grid_2026-08-22.md).
Locked ExECT cell 4:
[rule-select-after-LLM-encode](../exectv2/exect_rule_select_after_llm_encode_2026-08-22.md).
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

Both tasks name who runs each stage (rules, LLM, or both):

- **rules / rules / rules** — no model.
- **both / rules / rules** — `gan_llm_pre_post_label_forms` /
  `exect_llm_pre_post`, then rule encode and select.
- **LLM / rules / rules** — codebook extract / `exect_llm_only`,
  then rule encode and select.
- **LLM / LLM / rules** — Gan: codebook extract, then select only.
  ExECT: later-stage encode, then accepted Select rules.
- **LLM / LLM / LLM** — Gan `gan_llm_select_from_extract`. ExECT
  later-stage `exect_llm_select`.

The two public golds are evaluation forms, not the task. Gan asks for
one current seizure-frequency label. ExECT asks for a complete
four-family inventory. The cells use the same names on both tasks.
The scores do not move between tasks.

A later cell is not automatically better. A recorded hop is not a
clinically correct step. The score is how the submitted answer is
judged. Do not recode the stack; this is a refile of the claim.

## The Gan grid

| Extract | Encode | Select | What runs |
| --- | --- | --- | --- |
| rules | rules | rules | `gan_rules` |
| both | rules | rules | `gan_llm_pre_post_label_forms`, then rule encode and select |
| LLM | rules | rules | `gan_llm_extract_label_forms`, then codebook encode and rule select |
| LLM | LLM | rules | Same extract; select families only |
| LLM | LLM | LLM | Same extract; `gan_llm_select_from_extract` |

ExECT LLM encode is a second letter-out call. LLM / LLM / rules is
accepted Select on that encode ledger.

Three hop effects on one raw support the reading (the paper table need
not list every revise subtype):

- **Dialect** — same-fact writing (`mgs`→`mg`, brand→generic, word numbers).
- **Encode** — codebook / designed form / Gan selected-evidence renderer.
- **Select** — gate, drop, rewrite, reselect, invent.

On Gan the cited extract is the codebook request, not
`gan_llm_with_rules`. LLM encode in the headline table is that
extract, not a later-stage encode call. Tables cite Gemini 3.7 Flash.

On ExECT, cells 2–4 replay one `exect_llm_only` raw. **both / rules /
rules** is a different request (`exect_llm_pre_post`). `exect_llm_with_rules`
is the live alias of that request, not the cited extract.

The paper records every submitted-answer version as a hop log. A
**score projection** converts the submitted answer to the unit the
benchmark scores. It can discard distinctions that remain in the
object.

## Gan worked example: a bound becomes a gold label

**Letter:** Gan development source row `10`. **Model:** Grok 4.6.
**Wording ablation raw:** `gan_llm_with_rules` (not the cited
codebook extract). **Score:** Purist.
**Artifacts:** `paper_experiments/gan/rungs/grok46/dev750/` and
`paper_experiments/gan/gan_llm_with_rules/grok46/dev750/`.

The letter states a current rate as an upper bound:

> the observed frequency is noted as ≤ four per day, with variable clustering

Gold is `4 per day`. That is a Gan gold-dialect convention. The bound
stays in the quoted span. It is not in the submitted label.

| Role row | Extract | Encode | Select |
| --- | --- | --- | --- |
| **rules / rules / rules** | `4 per day` (correct) | same | same |
| **Wording ablation** (`gan_llm_with_rules`) | `≤ 4 per day` (incorrect) | `4 per day` (correct) | `4 per day` (correct) |
| **both / rules / rules** | `4 per day` (correct) | — | `4 per day` (correct) |

The wording-ablation extract and rule encode / select share one Grok
`gan_llm_with_rules` output. The model already selected the
accommodation-log event. Source-near extract keeps the inequality, so
Purist misses. Rule encode **encodes** that already chosen event into the
evaluation form and does not change `selected_event_ids`. Rule
select does not switch the event on this letter.

This is why encode exists as its own stop. The clinical fact is the
same rate the model chose. The designed form is a different string.
Turning selected-evidence repair off disables that whole renderer, not
only bound flattening. The same raw can be replayed with the renderer
off. **both / rules / rules** is a different request
(`gan_llm_pre_post_label_forms`), not a replay of this letter's
wording-ablation raw.

**Contrast, still development:** source row `15431`. Gold is the
two-part cluster label `1 cluster per 4 month, 5 per cluster`. Rules
submit that label and are Purist-correct. Wording-ablation extract
writes a long cluster-after-quiet phrase and misses. Rule encode and
rule select on that raw both submit `seizure free for multiple month`
and miss. Select
does not recover a two-part cluster once the model has collapsed the
reading. Visibility is the point: the hops name the collapse.

## ExECT worked example: a hedge becomes a diagnosis concept

**Letter:** ExECT development `EA0007`. **Model:** Grok 4.6.
**Shared raw for cells 2–4:** `exect_llm_only`. **Cell 2 (both /
rules / rules):** `exect_llm_pre_post`. **Score:** four-family clinical fact F1.
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
**both / rules / rules** on the same letter has select F1 1.0 and
four-family letter-exact true. The unrepaired `exect_llm_pre_post` body
on that request is the extract stop (cell 2), not the select stop.
Cell 3 (`exect_llm_only` plus rule encode and select) is the
six-model row and a separate saved call.

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
   change what the model is asked to collect. That is why ExECT cell 2
   is `exect_llm_pre_post`, and why an unrepaired pre-post body is not
   LLM extract.

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
