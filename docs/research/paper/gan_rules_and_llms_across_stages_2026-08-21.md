# Rules and models across extract, encode, and select (Gan 2026)

Date: 2026-08-21
Revised: 2026-08-22 (five-cell headline; select stop; wording ablation)
Status: paper source; Gan only; Gemini 3.7 Flash
Owners: [methods](../../paper/methods.md), [claims](../../paper/claims.md),
[method × stage](five_rungs_of_rule_help_2026-08-20.md)

This report reads the locked Gemini Gan grid. The cited table is
five role rows; the headline score is the select stop. See
[five-cell grid](../gan2026/gan_five_cell_grid_2026-08-22.md).
Worked letters below are development illustrations, some still on
the source-near `gan_llm_with_rules` ledger. Holdout is
aggregate-only. Do not inspect `test450` rows. ExECT is a separate
report.

Replayable cells:
`paper_experiments/gan/rungs/gemini37flash/`,
`paper_experiments/gan/gan_llm_pre_post/gemini37flash/`,
`paper_experiments/gan/gan_llm_encode/gemini37flash/`,
`paper_experiments/gan/gan_llm_select/gemini37flash/`.

## The question

Gan asks for one current seizure-frequency label. A letter can hold a
usual rate, a dated count, a cluster, a quiet interval, and older
history. Several of those statements can be true. The gold keeps one.

The headline table is five role rows. Each of **extract**, **encode**,
and **select** is **rules**, **LLM**, or **both**. The cited score is
the select stop:

| Extract | Encode | Select | What runs |
| --- | --- | --- | --- |
| rules | rules | rules | `gan_rules` — standalone deterministic pipeline; not the encode/select stack on a model ledger |
| both | rules | rules | `gan_llm_pre_post_label_forms`, then rule encode and select |
| LLM | rules | rules | `gan_llm_extract_label_forms` (codebook), then codebook encode and rule select — **six-model row** |
| LLM | LLM | rules | Same codebook extract; select families only |
| LLM | LLM | LLM | Same extract; `gan_llm_select_from_extract` |

`gan_llm_with_rules` is the source-near **wording ablation**, not the
cited extract. `gan_llm_only` is a third prompt. It is not a results
column.

Extract, encode, and select are different jobs:

- **Extract** collects events and a first pick. Parse is code. A blank
  Gan label stays unscorable.
- **Encode** writes the same facts in the designed form. It does not
  pick a different event. On Gan this is mainly the selected-evidence
  renderer (bounds, units, cluster-versus-rate dialect).
- **Select** may change which fact is current: gate, drop, rewrite,
  reselect, or invent under recorded policy.

The score then projects the submitted label onto a monthly Purist band.
That projection can throw a distinction away without changing the
object.

## The locked Gemini grid

Named Gemini `test450` select stops. Extract and encode stops are
ablations in the five-cell owner.

| Extract | Encode | Select | Purist |
| --- | --- | --- | ---: |
| rules | rules | rules | 0.73 |
| both | rules | rules | 0.82 |
| LLM | rules | rules | 0.83 |
| LLM | LLM | rules | 0.82 |
| LLM | LLM | LLM | 0.79 |

The source-near `gan_llm_with_rules` grid (LLM extract 0.55,
later-stage select 0.71, hybrid select 0.79) is an ablation.

Select on both hybrid rows is ledger-only: drop, regroup, or relabel
events already collected. `elapsed_anchor` and `residual_jerk` are
off. The source-near wording ablation (`gan_llm_with_rules`) reaches
0.79 at select. **both** / rules / rules is 0.82. The paper may not
say which holdout letters moved. It may not say the softer extract
preserves clinical reasoning.

Three patterns sit in that table.

1. **The headline is the submitted (select) label.** LLM extract plus
   codebook encode plus rule select is 0.83. Rule select without
   encode, and both-then-rules, are 0.82. LLM select is 0.79.
   Standalone rules are 0.73.
2. **Codebook extract already writes the form.** The LLM encode
   column is that extract, not a later-stage encode call. Later-stage
   Gemini encode on this ledger is an ablation (it drops the extract
   stop).
3. **The historical selected-evidence encoder is also an ablation.**
   It dropped the locked extract stop (0.79 → 0.77). The cited encode
   on the LLM / rules / rules row is codebook encode (0.80), then
   select 0.83.

Those are locked totals. They compare methods. They do not attribute a
holdout letter to one named rule.

## The development grid (mechanism, not holdout)

Named Gemini `dev750`. Same identities. Letters on this split may be
read.

| Extract | Encode | Select | Purist |
| --- | --- | --- | ---: |
| rules | rules | rules | 0.89 |
| both | rules | rules | 0.89 |
| LLM | rules | rules | 0.86 |
| LLM | LLM | rules | 0.85 |
| LLM | LLM | LLM | 0.79 |

The source-near `gan_llm_with_rules` development grid (extract 0.59,
later-stage 0.67 / 0.76, hybrid select 0.88) stays an ablation. On that
older raw, selected-evidence render never changed
`selected_event_ids` (219 kind changes; 167 Purist rescues; three
harms).

The development table repeats the locked shape at extract and encode.
At select the two hybrids are four letters apart (0.89 vs 0.88). “Rules
then LLM is stronger overall” is a small locked-select edge on top of
a larger extract/encode gap, not a claim that every development
letter prefers pre-suggestion.

## What each actor is good at

### Rules

**Strengths.** Rules already know the evaluation dialect. They flatten
bounds (`≤ four per day` → `4 per day`), keep two-part cluster labels
when the pattern is in the book, and write interval order the gold
expects (`1 per 1 to 2 week` rather than `1 to 2 per week`). They do
this without a call, and they do it the same way on every replay.

**Weaknesses.** They miss paraphrase and unusual current-state
packaging. They cannot invent a richer event list than their own
extractors found. The standalone rule score is one pipeline, not a
measurement of the later encode/select stack. A recorded select rule
can also harm: it can turn a justified unknown into a false rate.

### The model

**Strengths.** Gemini reads varied wording and can keep several events
in one ledger. On a frozen ledger it can still compose a two-part
cluster that the post stack never recovered (development row `15431`
below). Later-stage select rescued 22 development letters that rule
select missed.

**Weaknesses.** The written label often is not the Gan form. Extract
leaves 153 of 450 locked letters unscorable. Later-stage encode, with
no letter, writes `unknown` or a cluster template where the gold wants
a simple rate. Later-stage select and rule select on the wording
ablation now share
the same ledger bound: they may regroup or relabel collected events,
and they may not convert a clinic date or mine leftover dates from
the letter. The remaining select gap is therefore policy on the same
object, not access to the note.

### The combination

The useful split is not “rules versus models.” It is **who first sees
the letter**, **who writes the designed form**, and **who is allowed
to change the current fact**.

Rules first (candidates) raise the chance that the model’s ledger
contains the decisive quote. The model then keeps, rejects, splits, or
merges those rows and still scans the rest of the letter. Rules after
the call write the dialect and apply the named current-state
policies. The same saved output can be stopped at extract, encode, or
select without a new call.

## Why pre-suggestion still matters (both / rules / rules)

On the locked set the cited score is the select stop. The headline row
is **LLM / rules / rules** at 0.83. **both / rules / rules** is 0.82 —
one letter below the headline, nine above standalone rules (0.73).

The cause is still visible earlier than select, but the numbers below
are on the **wording ablation** (`gan_llm_with_rules`), not the cited
codebook extract.

**The extract gap is the large one on that ablation.** Standalone rules
already have 0.73. Gemini codebook extract without candidates scores
0.55 on the source-near raw. Candidates add 19 locked letters at
extract (0.59) and 19 more scorable rows (316 versus 297).
Pre-suggestion does not make extract as strong as standalone rules. It
makes the *model ledger* less empty and less wrong before anyone
encodes it.

**Encode then spends a better ledger.** Rule encode on the
pre-suggestion raw is 0.77 on the ablation stack. On the free-extract
source-near raw it is 0.74. Same renderer, different events.

**Select on the locked codebook grid.** On development, **both** /
rules / rules is 0.89 versus LLM / rules / rules 0.86 — four letters
apart. On the locked set the headline is LLM / rules / rules (0.83).
That is a method comparison of two extract requests, not proof that
pre-suggestion is necessary on any named holdout letter.

The short account: **rules are better first readers of this gold’s
surface forms; the model is a better collector of leftover paraphrase
once those forms are on the page; recorded rules are a better last
writer than asking Gemini to finish the form without the letter.**
**both / rules / rules** is the only row that uses candidate quotes
before the call.

## Why rule encode and select lift the wording ablation

These comparisons are on the source-near **wording ablation**
(`gan_llm_with_rules`), not the cited codebook extract. They explain
why rule stops after a softer extract still recover score.

### Encode: 0.65 → 0.74 locked; 0.67 → 0.81 development

Later-stage Gemini encode sees `event_id`, stated value, and quote. It
writes one label per event from the shared form list. The extract pick
is then projected through those labels. It does not re-read the
letter.

Rule encode on the same extract is the selected-evidence renderer. On
this Gemini raw it never switched events. It changed predicted kind
219 times on development and rescued 167 Purist letters.

The model already chose the right span more often than it wrote the
right string. Asking Gemini to re-encode those spans without the
letter loses 131 development letters that rule encode gets right.
The locked lift (44 letters) is the same kind of work: dialect, not a
new reading.

### Select: 0.71 → 0.79 locked; 0.76 → 0.88 development

Later-stage Gemini select sees the labelled events plus the extract
pick as a hint. It may keep that pick or write a new label from the
same form list. Rule select on the wording ablation uses the same
licence: usual
interval, typical-over-year-to-date, breakthrough, non-epileptic,
on-event diary, on-event dated sequence, and post-change burst.
Elapsed-window and residual-jerk conversion are off on both sides
because they need the letter clinic date.

The remaining locked lift (37 letters) is therefore recorded policy
on the same ledger, not extra access to the note. On development,
rule select still rescues 114 letters that later-stage Gemini select
misses, and later-stage select still rescues 22 that rule select
misses. The aggregate belongs to the recorded stack. A later cell is
not automatically better on every letter.

## Worked development letters

These letters explain a mechanism. They are not holdout component
shares. Model: Gemini 3.7 Flash.

### 1. A bound is the same fact in the wrong form (row `10`)

The letter states a current rate as an upper bound:

> observed frequency is noted as ≤ four per day

Gold is `4 per day`. That is a Gan gold-dialect convention. The bound
stays in the quoted span.

| Role row | Extract | Encode | Select |
| --- | --- | --- | --- |
| **rules / rules / rules** | `4 per day` | same | same |
| **Wording ablation** (`gan_llm_with_rules`) | `up to 4 per day` (miss; unscorable) | `4 per day` | `4 per day` |
| **both / rules / rules** | `4 per day` | — | `4 per day` |

Gemini already selected event `e2` and quoted the bound. Extract keeps
the inequality, so Purist misses. Rule encode writes the gold form and
does not change `selected_event_ids`. Later-stage Gemini encode also
writes `4 per day` on this letter. Encode exists because the clinical
fact can be right while the string is wrong. Turning selected-evidence
repair off disables that whole renderer, not only bound flattening.

### 2. “Cluster” language that gold scores as a simple rate (row `187`)

Evidence:

> events tend to cluster every seven to nine days

Gold is `1 per 7 to 9 day`.

| Role row | Extract | Encode | Select |
| --- | --- | --- | --- |
| **rules / rules / rules** | `1 per 7 to 9 day` | same | same |
| **Wording ablation** | `1 cluster every 7 to 9 days` (miss) | `1 per 7 to 9 day` | `1 per 7 to 9 day` |
| **both / rules / rules** | `1 per 7 to 9 day` | — | `1 per 7 to 9 day` |

This is why rule encode beats later-stage Gemini encode on the same
ledger. The model collected the span. The renderer maps cluster-worded
cadence onto the gold rate. Gemini encode, without the letter, writes
`unknown` and select cannot recover. Rule encode on the wording
ablation is 44 locked
letters ahead of LLM at encode because this class of mapping is
stable, replayable, and not a new extract.

Row `190` is the same shape with the opposite temptation: extract
writes `1 cluster per 4 weeks`, rule encode writes gold `1 per 4
week`, later-stage Gemini encode keeps a cluster template
(`1 cluster per 4 week, multiple per cluster`).

### 3. A two-part cluster the free extract flattened (row `15431`)

Gold is `1 cluster per 4 month, 5 per cluster`. Rules submit that
label. The wording ablation (`gan_llm_with_rules`) extract writes `5 per day` from

> experience clusters of 5 seizures in a single day

and rule encode and rule select keep `5 per day`. The two-part reading
is already gone.

| Role row | Extract | Encode | Select |
| --- | --- | --- | --- |
| **rules / rules / rules** | `1 cluster per 4 month, 5 per cluster` | same | same |
| **Wording ablation** | `5 per day` | `5 per day` | `5 per day` |
| **LLM / LLM / LLM** | `5 per day` | `unknown, 5 per cluster` | `1 cluster per 4 month, 5 per cluster` |
| **both / rules / rules** | `1 cluster per 4 month, 5 per cluster` | — | `1 cluster per 4 month, 5 per cluster` |

Three readings sit together.

- Standalone rules know the cluster pattern.
- Rule encode cannot restore a second quantity once extract has
  collapsed it. Select on that raw does not recover either.
- Later-stage Gemini select, looking at a quiet-interval event and a
  cluster-burden event, composes the gold label. That is a real model
  strength at select.
- **both / rules / rules** also lands on gold, because the suggested candidates
  put both pieces in the extract.

This letter is why the paper should not say the last cell always
wins, or that rule select is always kinder than model select. It is
also why pre-suggestion matters: the cheap way to keep a two-part
cluster is to have both quotes on the extract ledger.

### 4. Interval order the gold treats as a different label (row `5767`)

Evidence:

> spells now occurring every one to two weeks

Gold is `1 per 1 to 2 week`. Gemini extract writes `1 to 2 per week`.
Rule encode and rule select leave that string. Purist misses;
Pragmatic hits. Standalone rules and **both / rules / rules**
write the gold order. Later-stage Gemini encode and select also write
`1 per 1 to 2 week` on this letter.

The object makes the disagreement inspectable. The score’s strictness
is a gold-dialect fact, not lost evidence. **both / rules / rules** can inherit
the rule book’s order because those candidates were on the page
before the call.

### 5. A quiet-interval extract that ledger-only select cannot rewrite (row `14214`)

Gemini extract writes `seizure free` from

> She has remained seizure-free since then.

Rule encode lengthens that to `seizure free for multiple year`.
Ledger-only rule select no longer runs `elapsed_anchor`, so the hop
stays on that encoded label and still misses. Gold is `2 to 4 per
month`. Later-stage Gemini select stays on `seizure free`. Standalone
rules and **both / rules / rules** are Purist-correct
(`2 to 4 per month` / `2 to 4 per 1 month`).

The earlier letter-clock select on this raw rewrote the quiet
interval to `1 per 2 month` and still missed. Turning that family off
makes the comparison with later-stage select fair: neither side may
invent a rate from the clinic date. Pre-suggestion recovers the
letter because the extract already holds the current-rate quote.

## What this tells us

1. **Gan is a form-plus-selection problem, not a span-finding
   problem.** The model often quotes the decisive text at extract and
   still loses Purist. The first mass correction is encode of a span
   already chosen.
2. **Rules and models fail at different stages.** Rules are the better
   extract of this gold’s closed dialect and the better last writer of
   that dialect. The model is the better collector of leftover
   wording and, sometimes, the better composer of a two-part cluster
   from a ledger. Neither role is “intelligence” in the abstract.
3. **Order matters because extract is the bottleneck.** Encode and
   select cannot restore facts the ledger never held. Candidates
   before the call are the only row that changes extract. That is
   why **both / rules / rules** still leads on development select
   (0.89 vs 0.86), even though the locked headline is LLM / rules /
   rules (0.83).
4. **Putting rules after a softer extract is still worth a large
   locked lift on the wording ablation** (0.55 → 0.74 → 0.79)
   because most of the work is rendering and named ledger policy, not
   a second reading of the letter. The paper may say wording can be
   kept and later mapped into the gold form. It may not say the softer
   extract preserves clinical reasoning.
5. **The recorded object is the claim.** The span, the named hop, and
   the submitted label can be replayed. The score can discard a bound
   or an interval order. A reader can disagree with the mapping
   without losing the quote.
6. **The remaining hard cases are current-state choice.** Clusters
   with two quantities, quiet intervals versus dated bursts, and
   unknowns that a select rule should have left unknown. Those are
   not syntax problems.

## Claim boundary

This report may say the locked Gemini totals above, that LLM / rules /
rules is the headline row on this grid, that **both / rules / rules**
beats standalone rules, and that rule encode and select lift the
wording ablation on the same source-near raw. It may use the
development letters as mechanism. It may not treat a
development hop share as a holdout component estimate, inspect
`test450` rows, cite `gan_llm_only` as extract, treat Luna as the
cited model, or move these scores onto ExECT.

It does not support a claim that every rule is safe, that a visible
hop is clinically correct, that later-stage Gemini select is hybrid
select, that pre-suggestion is necessary on holdout letters, or that
the system is ready for clinical use.

## Where to read next

| Need | File |
| --- | --- |
| Locked wording | [claims](../../paper/claims.md) |
| Cell identities | [methods](../../paper/methods.md) |
| Plain-language grid and one letter per task | [method × stage](five_rungs_of_rule_help_2026-08-20.md) |
| Why a model plus recorded rules | [hybrid architecture](why_hybrid_architecture_2026-08-09.md) |
| Gan later-stage prompt contract | [decision](../../paper/decisions/gan-later-stage-encode-select-prompts.md) |
| Earlier Gan story (Grok-centred) | [Gan story](gan_story_2026-08-10.md) |
