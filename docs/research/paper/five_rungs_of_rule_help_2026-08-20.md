# Five rungs of rule help

Date: 2026-08-20
Status: paper source; development illustrations only
Owners: [methods](../../paper/methods.md), [claims](../../paper/claims.md),
this file for the worked reading

The headline table is five rungs of rule help, not three methods. This
page is the plain-language owner for what those rungs are, how they
run on one Gan letter and one ExECT letter, and what the full design
is worth. Replayable numbers stay in
[`paper_experiments/`](../../../paper_experiments/README.md). What a
sentence may say stays in [claims](../../paper/claims.md).

These examples are development letters. They explain a mechanism. They
are not holdout component estimates. Do not inspect `test450` or
`test60` rows.

## What the design is

The proposed method translates a clinic letter into structured clinical
facts in a designed form, with quoted source text. A model collects a
ledger. Recorded rules then shape that ledger. The same saved model
output can be replayed through those rules without a new call.

The two public golds are evaluation forms, not the task. Gan asks for
one current seizure-frequency label. ExECT asks for a complete
four-family inventory. The rungs use the same names on both tasks.
The scores do not move between tasks.

Rule help is a depth axis. It is not an on/off hybrid switch. A later
rung is not automatically better. A recorded hop is not a clinically
correct step. The score is how the submitted answer is judged.

## The five rungs

Each rung is a depth of rule help around one letter.

| Rung | Plain name | What happens | What must not be confused with it |
| --- | --- | --- | --- |
| 1 | Rules only | Deterministic code reads the letter and submits the designed form. No model. | The later post stack that repairs a model ledger. Those are different rule sets. |
| 2 | Schema only | One model call, no candidate list in the prompt. Score the parsed model object as written. | `gan_llm_only`, which asks for a finished Gan label. That prompt is not a results column. |
| 3 | Format render | Same saved model output as rung 2. Change spelling, units, or serialization. Do not pick a different fact. | Dictionary rewrite, event switching, or family transforms. Those are semantic. |
| 4 | Clinical post | Same saved output plus the full clinical rule stack. Rules may change meaning. | An unrepaired hybrid answer, or a new model call. |
| 5 | Pre-suggest + post | Deterministic candidates go into the prompt. Then the same post stack. This is a different request from rungs 2–4. | Scoring the raw body of that hybrid call as if it were rung 2. |

On Gan, rungs 2–4 replay one `gan_llm_with_rules` `raw_output`. Rung 5
is `gan_llm_pre_post`, a new request. Luna is the development
iterator for that request. It is not automatically the cited model.

On ExECT, rungs 2–4 replay one `exect_llm_only` `raw_output`. Rung 5 is
living `exect_llm_pre_post`. `exect_llm_with_rules` is the live alias
for that request.

The paper records every submitted-answer version as a hop log. A
**format** change keeps the represented fact. A **semantic** change
alters the selected event, concept, attribute, multiplicity, evidence
acceptance, or unknown status. A **score projection** converts the
submitted answer to the unit the benchmark scores. It can discard
distinctions that remain in the object.

## Gan worked example: a bound becomes a gold label

**Letter:** Gan development source row `10`. **Model:** Grok 4.6.
**Shared raw:** `gan_llm_with_rules`. **Score:** Purist.
**Artifacts:** `paper_experiments/gan/rungs/grok46/dev750/` and
`paper_experiments/gan/gan_llm_with_rules/grok46/dev750/`.

The letter states a current rate as an upper bound:

> the observed frequency is noted as ≤ four per day, with variable clustering

Gold is `4 per day`. That is a Gan gold-dialect convention. The bound
stays in the quoted span. It is not in the submitted label.

| Rung | Submitted label | Purist |
| --- | --- | --- |
| 1 rules only | `4 per day` | correct |
| 2 schema only | `≤ 4 per day` | incorrect |
| 3 format render | `4 per day` | correct |
| 4 clinical post | `4 per day` | correct |

Rungs 2–4 share one Grok output. The model already selected the
accommodation-log event. Schema keeps the inequality in the label, so
Purist misses. Selected-evidence render (rung 3) writes the gold
dialect and does not change `selected_event_ids`. Clinical post does
not switch the event on this letter.

This is why rung 3 exists. The clinical fact is the same rate the
model chose. The designed form is a different string. Turning
selected-evidence repair off disables that whole renderer, not only
bound flattening. The same raw can be replayed with the renderer off.
Rung 5 is not shown here: Grok `gan_llm_pre_post` is not a cited cell
in this cut.

**Contrast, still development:** source row `15431`. Gold is the
two-part cluster label `1 cluster per 4 month, 5 per cluster`. Rules
only submits that label and is Purist-correct. Schema writes a long
cluster-after-quiet phrase and misses. Format and post both submit
`seizure free for multiple month` and miss. The full post stack does
not recover a two-part cluster once the model has collapsed the
reading. Visibility is the point: the hops name the collapse.

## ExECT worked example: a hedge becomes a diagnosis concept

**Letter:** ExECT development `EA0007`. **Model:** Grok 4.6.
**Shared raw for rungs 2–4:** `exect_llm_only`. **Rung 5:** living
`exect_llm_pre_post`. **Score:** four-family clinical fact F1.
**Artifacts:** `paper_experiments/exect/rungs/grok46/dev140/` and
`paper_experiments/exect/exect_llm_pre_post/grok46/dev140/`.

The letter quotes a hedge on onset:

> Diagnosis: epilepsy – unclassified

and

> Seizure type and frequency: seizures every 3 to 4 weeks, possibly focal onset

Grok put that hedge on the collected evidence. Rung 2 keeps Diagnosis
as the written `epilepsy` mention. Rung 3 may attach a CUI or respell
closed-vocab fields; it does not rewrite the concept. Rung 4 runs the
diagnosis dictionary and records `focal epilepsy`. That is a semantic
change, not a format change.

ExECT format is same-fact writing: attribute canonicalize, codebook
ids, prescription name/unit/dose, seizure-frequency encoding, and
investigation attribute strip. Evidence reject, SF state projection,
unknown suppression, and family lenses are clinical post and land on
rung 4.

Living rung 5 on the same letter has hybrid headline F1 1.0 and
four-family letter-exact true. The unrepaired hybrid raw on that
request is not rung 2. Rung 2 is the separate `exect_llm_only` call.

The rewrite is a task-format commitment. It is not an unqualified
clinical diagnosis. The object keeps the quoted hedge, the named
dictionary rule, and the submitted concept. A reader can disagree with
the mapping without losing the span.

## What the full design is worth

The value is the recorded object and the ability to stop the stack,
not a promise that the last rung always wins.

1. **The same names on two questions.** Gan selects one current state.
   ExECT inventories four families. Readers can compare depth of rule
   help without pretending the scores are interchangeable.
2. **Replay without a new call.** Rungs 2–4 are readings of one saved
   `raw_output`. A format-only stop and a full post can be shown on
   the same model text.
3. **Format and meaning stay separable.** Gan row 10 is a dialect
   render of an already chosen event. ExECT `EA0007` is a concept
   rewrite at post. Calling both “repair” would hide which class of
   change occurred.
4. **The score can throw distinctions away.** Purist accepts `4 per
   day` and rejects `≤ 4 per day` on the same span. Clinical fact F1
   can match gold after a dictionary rewrite. The object still holds
   the bound and the hedge.
5. **Rules only is a baseline, not the post stack.** On row `15431`
   standalone rules get the cluster gold and the model-led rungs do
   not. On the locked Gan set, rung 4 beats that baseline in the
   aggregate. Those facts can both be true because they compare
   different objects.
6. **Pre-suggestion is a different request.** Candidates in the prompt
   change what the model is asked to collect. That is why ExECT rung 5
   is living `exect_llm_pre_post`, and why an unrepaired hybrid answer
   is not ExECT rung 2.

The files do not support a claim that every deterministic step is
safe, that a visible hop is clinically correct, that development hop
shares are holdout effects, or that one extraction already serves a
second use case.

## Where to read next

| Need | File |
| --- | --- |
| Locked wording | [claims](../../paper/claims.md) |
| Identities, splits, scorers | [methods](../../paper/methods.md) |
| Why a model plus recorded rules | [hybrid architecture](why_hybrid_architecture_2026-08-09.md) |
| The two golds | [what the two golds already decided](what_the_two_golds_already_decided_2026-08-17.md) |
| Earlier pair of reviewable traces | [reviewable case pair](reviewable_case_pair_2026-08-09.md) |
| Replayable cells | [`paper_experiments/`](../../../paper_experiments/README.md) |
