# Rules and models across extract, encode, and select (Gan 2026)

Date: 2026-08-21
Revised: 2026-08-21 (ledger-only hybrid select; Gemini replay)
Status: paper source; Gan only; Gemini 3.7 Flash
Owners: [methods](../../paper/methods.md), [claims](../../paper/claims.md),
[method × stage](five_rungs_of_rule_help_2026-08-20.md)

This report reads the locked Gemini four-method grid on Gan 2026. It asks
what rules do well, what the model does well, why **Rules then LLM** is
the strongest overall method on this gold, and why **LLM then rules**
beats a model-only encode or select. Worked letters are development
only. Holdout is aggregate-only. Do not inspect `test450` rows. ExECT
is a separate report.

Replayable cells:
`paper_experiments/gan/rungs/gemini37flash/`,
`paper_experiments/gan/gan_llm_pre_post/gemini37flash/`,
`paper_experiments/gan/gan_llm_encode/gemini37flash/`,
`paper_experiments/gan/gan_llm_select/gemini37flash/`.

## The question

Gan asks for one current seizure-frequency label. A letter can hold a
usual rate, a dated count, a cluster, a quiet interval, and older
history. Several of those statements can be true. The gold keeps one.

The four methods are different ways of dividing that work between
written rules and Gemini:

| Method | What happens |
| --- | --- |
| **Rules** | Standalone deterministic pipeline. No model. One answer, shown in every stage column. That rule set is not the encode/select stack on a model ledger. |
| **LLM** | Gemini only. Extract is the parsed `gan_llm_with_rules` ledger. Encode and select are later-stage Gemini calls on that ledger. They do not re-read the letter. |
| **LLM then rules** | The same `gan_llm_with_rules` raw, stopped at extract, then rule encode, then rule select. |
| **Rules then LLM** | A different request (`gan_llm_pre_post`): rules first suggest candidate quotes, Gemini collects and picks, then the same rule encode and select stack runs. |

`gan_llm_only` is a third prompt. It is not a results column.

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

Named Gemini `test450` totals. **LLM then rules** is the three stops on
the `gan_llm_with_rules` raw. **Rules then LLM** is the three stops on
the `gan_llm_pre_post` raw. **LLM** encode and select are later-stage
Gemini cells. LLM extract is the `gan_llm_with_rules` extract stop.

| | Extract | Encode | Select |
| --- | ---: | ---: | ---: |
| **Rules** | 329/450 (0.73) | 329/450 (0.73) | 329/450 (0.73) |
| **LLM** | 246/450 (0.55), 297 scorable | 291/450 (0.65) | 320/450 (0.71) |
| **LLM then rules** | 246/450 (0.55), 297 scorable | 335/450 (0.74) | 357/450 (0.79) |
| **Rules then LLM** | 265/450 (0.59), 316 scorable | 345/450 (0.77) | 358/450 (0.80) |

Select on both hybrid rows is ledger-only: drop, regroup, or relabel
events already collected. `elapsed_anchor` and `residual_jerk` are
off. The living Gemini `gan_llm_with_rules` cell is now the same
357/450 as the select stop. The living Gemini `gan_llm_pre_post`
cell is the same 358/450 as that select stop. The paper may not say
which holdout letters moved. These totals replace the earlier
letter-clock select readings (368 and 372).

Three patterns sit in that table.

1. **Extract is where standalone rules dominate.** 329 correct labels
   with no model. Gemini without suggested candidates is 246. Giving
   the model those candidates raises extract only to 265. The model is
   not a better first writer of Gan labels than the rule book.
2. **Encode is where a model ledger plus rules first beats rules.**
   Rule encode on a Gemini ledger is 335 or 345. That is already above
   standalone rules (329) and well above later-stage Gemini encode
   (291).
3. **Select is where both hybrids still clear later-stage Gemini, and
   almost meet each other.** 357 and 358 sit above rules (329) and
   above later-stage Gemini select (320). Once both hybrids use the
   same ledger bound as the LLM select cell, the last-mile gap is one
   letter.

Those are locked totals. They compare methods. They do not attribute a
holdout letter to one named rule.

## The development grid (mechanism, not holdout)

Named Gemini `dev750`. Same identities. Letters on this split may be
read.

| | Extract | Encode | Select |
| --- | ---: | ---: | ---: |
| **Rules** | 669/750 (0.89) | 669/750 (0.89) | 669/750 (0.89) |
| **LLM** | 444/750 (0.59), 532 scorable | 506/750 (0.67) | 568/750 (0.76) |
| **LLM then rules** | 444/750 (0.59), 532 scorable | 608/750 (0.81) | 660/750 (0.88) |
| **Rules then LLM** | 502/750 (0.67), 582 scorable | 632/750 (0.84) | 664/750 (0.89) |

On this Gemini `gan_llm_with_rules` raw, selected-evidence render never
changed `selected_event_ids` (219 kind changes; 167 Purist rescues;
three harms). That is why encode is encode. The living Gemini hybrid
cells now match their select stops (660 and 664).

The development table repeats the locked shape at extract and encode.
At select the two hybrids are four letters apart (664 vs 660). “Rules
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
a simple rate. Later-stage select and living hybrid select now share
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

## Why Rules then LLM is stronger overall

On the locked set the method that is submitted is the select column.
Rules then LLM is 358/450. That is 29 letters above standalone rules
and 1 above LLM then rules.

The cause is visible earlier than select.

**The extract gap is the large one.** Standalone rules already have
329 correct labels. Gemini without candidates has 246. Candidates add
19 locked letters at extract (265) and 19 more scorable rows (316
versus 297). Pre-suggestion does not make extract as strong as
standalone rules. It makes the *model ledger* less empty and less
wrong before anyone encodes it.

**Encode then spends a better ledger.** Rule encode on the
pre-suggestion raw is 345. On the free-extract raw it is 335. Same
renderer, different events. The eight-letter encode gap is already
most of the four-letter select gap.

**Select does the last current-state work on both hybrids.** The
post stack is the same ledger-only families. On development Rules then
LLM is four letters ahead (664 vs 660). On the locked set it is one
letter ahead. That is a method comparison of two requests, not proof
that pre-suggestion is necessary on any named holdout letter. The
old four-letter locked gap (372 vs 368) included clinic-date select
that later-stage Gemini cannot do.

The short account: **rules are better first readers of this gold’s
surface forms; the model is a better collector of leftover paraphrase
once those forms are on the page; recorded rules are a better last
writer than asking Gemini to finish the form without the letter.**
Rules then LLM is the only method that uses that order.

## Why LLM then rules beats LLM on encode and select

These two rows share one extract (246 / 444). The difference is who
finishes the ledger.

### Encode: 291 → 335 locked; 506 → 608 development

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

### Select: 320 → 357 locked; 568 → 660 development

Later-stage Gemini select sees the labelled events plus the extract
pick as a hint. It may keep that pick or write a new label from the
same form list. Living hybrid select now uses the same licence: usual
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

| | Extract | Encode | Select |
| --- | --- | --- | --- |
| **Rules** | `4 per day` | same | same |
| **LLM** | `up to 4 per day` (miss; unscorable) | `4 per day` | `4 per day` |
| **LLM then rules** | `up to 4 per day` (same raw) | `4 per day` (`gan.render.selected_evidence`) | `4 per day` (no event switch) |
| **Rules then LLM** | living cell `4 per day` | — | living cell `4 per day` |

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

| | Extract | Encode | Select |
| --- | --- | --- | --- |
| **Rules** | `1 per 7 to 9 day` | same | same |
| **LLM** | `1 cluster every 7 to 9 days` (miss) | `unknown` | `unknown` |
| **LLM then rules** | same extract | `1 per 7 to 9 day` | `1 per 7 to 9 day` |
| **Rules then LLM** | living cell `1 per 7 to 9 day` | — | living cell `1 per 7 to 9 day` |

This is why rule encode beats later-stage Gemini encode on the same
ledger. The model collected the span. The renderer maps cluster-worded
cadence onto the gold rate. Gemini encode, without the letter, writes
`unknown` and select cannot recover. LLM then rules is 44 locked
letters ahead of LLM at encode because this class of mapping is
stable, replayable, and not a new extract.

Row `190` is the same shape with the opposite temptation: extract
writes `1 cluster per 4 weeks`, rule encode writes gold `1 per 4
week`, later-stage Gemini encode keeps a cluster template
(`1 cluster per 4 week, multiple per cluster`).

### 3. A two-part cluster the free extract flattened (row `15431`)

Gold is `1 cluster per 4 month, 5 per cluster`. Rules submit that
label. Gemini `gan_llm_with_rules` extract writes `5 per day` from

> experience clusters of 5 seizures in a single day

and rule encode and rule select keep `5 per day`. The two-part reading
is already gone.

| | Extract | Encode | Select |
| --- | --- | --- | --- |
| **Rules** | `1 cluster per 4 month, 5 per cluster` | same | same |
| **LLM** | `5 per day` | `unknown, 5 per cluster` | `1 cluster per 4 month, 5 per cluster` |
| **LLM then rules** | `5 per day` | `5 per day` | `5 per day` |
| **Rules then LLM** | living cell `1 cluster per 4 month, 5 per cluster` | — | living cell `1 cluster per 4 month, 5 per cluster` |

Three readings sit together.

- Standalone rules know the cluster pattern.
- Rule encode cannot restore a second quantity once extract has
  collapsed it. Select on that raw does not recover either.
- Later-stage Gemini select, looking at a quiet-interval event and a
  cluster-burden event, composes the gold label. That is a real model
  strength at select.
- Rules then LLM also lands on gold, because the suggested candidates
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
Pragmatic hits. Standalone rules and the living Rules then LLM cell
write the gold order. Later-stage Gemini encode and select also write
`1 per 1 to 2 week` on this letter.

The object makes the disagreement inspectable. The score’s strictness
is a gold-dialect fact, not lost evidence. Rules then LLM can inherit
the rule book’s order because those candidates were on the page
before the call.

### 5. A quiet-interval extract that ledger-only select cannot rewrite (row `14214`)

Gemini extract writes `seizure free` from

> She has remained seizure-free since then.

Rule encode lengthens that to `seizure free for multiple year`.
Ledger-only rule select no longer runs `elapsed_anchor`, so the hop
stays on that encoded label and still misses. Gold is `2 to 4 per
month`. Later-stage Gemini select stays on `seizure free`. Standalone
rules and the living Rules then LLM cell are Purist-correct
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
   before the call are the only method that changes extract. That is
   why Rules then LLM still leads on the locked grid, by one letter at
   select, after the two hybrids share a ledger-only post stack.
4. **Putting rules after a free extract is still worth a large
   locked lift** (246 → 335 → 357) because most of the work is
   rendering and named ledger policy, not a second reading of the
   letter. That is why LLM then rules still beats later-stage Gemini
   encode and select after the comparison is equalised.
5. **The recorded object is the claim.** The span, the named hop, and
   the submitted label can be replayed. The score can discard a bound
   or an interval order. A reader can disagree with the mapping
   without losing the quote.
6. **The remaining hard cases are current-state choice.** Clusters
   with two quantities, quiet intervals versus dated bursts, and
   unknowns that a select rule should have left unknown. Those are
   not syntax problems.

## Claim boundary

This report may say the locked Gemini totals above, that Rules then
LLM is the strongest overall method on this grid, and that LLM then
rules beats later-stage Gemini encode and select on the same extract.
It may use the development letters as mechanism. It may not treat a
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
