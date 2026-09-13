# Results: Local one-call find, encode, and select

Date: 2026-09-13
Protocol: [protocol](gan_local_one_call_encode_select_protocol_2026-09-13.md)
Artifact: [aggregates](gan_local_one_call_encode_select_2026-09-13.json)
Row analysis (`dev750` only):
[row tables](gan_local_one_call_encode_select_dev750_row_analysis_2026-09-13.json)
Promoted holdout cells:
`paper_experiments/gan/gan_llm_extract_encode_select/{slug}/test450/`
Development work:
`experiments/paper/gan_llm_extract_encode_select/{slug}/dev750/`

## Answer

The frozen one-call prompt does not travel evenly across local
models. Size helps, but generation and JSON validity matter more
than raw parameter count. Qwen 3.8 27B is the local peak. Qwen 3.6
35B does not beat it. Qwen 3.5 9B beats older Qwen 2.5 14B. Llama
3.1 8B mostly fails the form. Llama 2 13B is out of the set
(4,096-token window; 450/450 holdout parse failures).

Call failures are **0** on every retained cell.

### Purist, one-call extract stop

| Model | `dev750` | `test450` |
| --- | ---: | ---: |
| Llama 3.1 8B | 215/750 (0.287) | 139/450 (0.309) |
| Qwen 3.5 9B | 412/750 (0.549) | 237/450 (0.527) |
| Qwen 2.5 14B | 362/750 (0.483) | 231/450 (0.513) |
| Gemma 4 26B | 482/750 (0.643) | 286/450 (0.636) |
| Qwen 3.8 27B | **546**/750 (**0.728**) | **333**/450 (**0.740**) |
| Qwen 3.6 35B | 476/750 (0.635) | 297/450 (0.660) |
| Gemini 3.7 Flash (hosted, same prompt) | 657/750 (0.876) | 392/450 (0.871) |

Development and holdout ranks match. The local peak is still **111**
Purist below Gemini on `dev750` and **59** below on `test450`.

### Pragmatic sidecar

| Model | `dev750` | `test450` | `dev750` prag−purist |
| --- | ---: | ---: | ---: |
| Llama 3.1 8B | 334/750 (0.445) | 207/450 (0.460) | +119 |
| Qwen 3.5 9B | 462/750 (0.616) | 267/450 (0.593) | +50 |
| Qwen 2.5 14B | 421/750 (0.561) | 257/450 (0.571) | +59 |
| Gemma 4 26B | 535/750 (0.713) | 315/450 (0.700) | +53 |
| Qwen 3.8 27B | 585/750 (0.780) | 352/450 (0.782) | +39 |
| Qwen 3.6 35B | 526/750 (0.701) | 318/450 (0.707) | +50 |

The Llama gap is the tell: many rows are roughly the right clinical
state and still miss the allowed form.

## Versus cell 3 (living locals only)

Cell 3 is codebook extract, then rules encode and rules select.
The four newer locals have no cell 3 cells yet.

| Model | Split | Cell 3 extract | Cell 3 select | One-call | vs extract | vs select |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Qwen 3.8 27B | `dev750` | 505 | **577** | 546 | +41 | −31 |
| Qwen 3.8 27B | `test450` | 315 | **343** | 333 | +18 | −10 |
| Gemma 4 26B | `dev750` | 501 | **567** | 482 | −19 | −85 |
| Gemma 4 26B | `test450` | 299 | **326** | 286 | −13 | −40 |

Qwen's bundled request beats its own codebook extract and still
loses the rules-select lift. Gemma loses to both of its cell 3
stops. One-call is not a substitute for cell 3 on these locals.

## Where they break (`dev750` only)

Parse failure is a miss. The rest of the miss is a parseable label
that is the wrong form or the wrong clinical pick.

| Model | Parse | Structured | Purist among structured | Evidence valid | Written rates | Written unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Llama 3.1 8B | 114 | 636 | 0.338 | 277 | 510 | 12 |
| Qwen 3.5 9B | 93 | 657 | 0.627 | 399 | 367 | 55 |
| Qwen 2.5 14B | **135** | 615 | 0.589 | 468 | 372 | 16 |
| Gemma 4 26B | 8 | 742 | 0.650 | 699 | 382 | 99 |
| Qwen 3.8 27B | 8 | 742 | **0.736** | 693 | 418 | 68 |
| Qwen 3.6 35B | 32 | 718 | 0.663 | 576 | 411 | 41 |

**Llama 3.1 8B.** Format is the first wall (114 parse failures) and
not the only one. Among structured rows it is still 0.34 Purist.
It writes a rate on 510 notes and almost never writes `unknown`
(12). Illegal leftovers (`infrequent`, `ongoing`, `variable`,
`1 every 2 days`) sit in the Pragmatic gap. Evidence validity is
low (277/750). This is a form-and-abstention failure, not a
near-miss at Gemini quality.

**Qwen 2.5 14B.** Worst parse rate in the set (135). Once it
parses, Purist among structured (0.59) is close to Qwen 3.5 and
Gemma. It writes few `unknown` labels (16). The extra size over
Qwen 3.5 does not help.

**Qwen 3.5 9B.** Best of the small models. Parse is still high
(93) but structured accuracy (0.63) matches Gemma's structured
accuracy. Cluster and unknown use look closer to the larger Qwen
cells than Llama or Qwen 2.5.

**Gemma 4 26B.** JSON is mostly fine (8 parse). The remaining gap
to Qwen 3.8 is label choice, not schema. One-call is worse than
its own extract stop, so bundling select into the find call costs
this model.

**Qwen 3.8 27B.** Local ceiling: 8 parse, highest structured
Purist (0.74), smallest prag−purist gap (+39). Still well below
Gemini one-call and below its own cell 3 select.

**Qwen 3.6 35B.** Larger and older than 3.8. More parse (32) and
weaker evidence validity (576) than Gemma or 3.8. Score sits with
Gemma, not above it. Parameter count is not the ranking.

## Row-level analysis (`dev750` only)

Inspection is development-only. `test450` rows were not opened.
`data_text_policy: development_letter_excerpt`. Quotes below are
short source spans or model strings, not holdout text.

Exact evidence means the selected `evidence` string is a
case-sensitive contiguous substring of the note. It is not
clinical validity. Parse/schema means a blocking
`invalid_json`, `schema_validation_error`, or
`unscorable_final_label` (or no structured record). Format
retry on Ollama does not count as a second clinical call;
rejected retries stay misses.

First-failure owner on a Purist miss, in order: schema/parse;
then **find** (gold Purist bucket absent from extracted event
labels); then **select** (bucket present in the inventory, not
in the selected facts); then **encode** (selected fact matches
gold, final label does not); then **form/bucket** (Pragmatic
right, Purist wrong). One owner per row.

| Model | Schema/parse | Find | Select | Encode | Form/bucket | Other | Purist |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Llama 3.1 8B | 114 | 198 | 75 | 63 | 73 | 12 | 215 |
| Qwen 3.5 9B | 93 | 130 | 45 | 28 | 36 | 6 | 412 |
| Qwen 2.5 14B | **135** | 132 | 72 | 9 | 37 | 3 | 362 |
| Gemma 4 26B | 8 | 144 | 50 | 14 | 30 | 22 | 482 |
| Qwen 3.8 27B | 8 | **107** | 41 | 18 | 26 | 4 | **546** |
| Qwen 3.6 35B | 32 | 121 | 47 | 15 | 39 | 20 | 476 |

Schema is the small-model wall. Once JSON is mostly valid,
**find** is the largest leftover owner on every model,
including the local peak. Select and form shrink with generation
more than they shrink with raw size. Qwen 3.6 does not improve
on 3.8 on any owner.

98 / 750 letters are Purist-wrong on all six locals (68 gold
frequency, 23 unknown, 7 unresolved-multiple). 136 letters are
wrong on all three small models and right on at least one large
model; only 21 of those are right on all three large models.

### Why schema failures happen

The request asks for `facts` / `fact_id` / `selected_fact_ids`
and event kinds such as `frequency_rate`. The validator wants
`events` / `event_id` / `selected_event_ids` and selection
`final_kind` in `{frequency, seizure_free, unknown,
no_reference, unresolved_multiple}`. Alias repair maps the
prompt names. It does **not** map `final_kind: frequency_rate`
to `frequency`. Extra top-level keys after filter also fail
(`extra="forbid"`). Missing `event_id` is filled only when
*some* fact already has an id.

| Model | Dominant schema class | Main field | Blocked rows whose raw `final_label` would have been Purist-correct |
| --- | --- | --- | ---: |
| Llama 3.1 8B | missing required (94) | `event_id` (79), then `temporality` (14) | 37 / 114 |
| Qwen 3.5 9B | missing or illegal enum | `temporality` (32), `final_kind` (45) | 42 / 93 |
| Qwen 2.5 14B | illegal enum (134) | `selection.final_kind` | **61 / 135** |
| Gemma 4 26B | residual enum / missing | `final_kind` or event `kind` | 4 / 8 |
| Qwen 3.8 27B | leftover JSON / extra key | unmatched commas; top-level `selected_fact_ids` | **0 / 8** |
| Qwen 3.6 35B | invalid JSON (17) + missing | control characters, truncated objects, `temporality` (12) | 11 / 32 |

**Correct label, dead schema** is a real mode, not a rare
edge. Qwen 2.5 writes the gold string and then names the
selection `frequency_rate` (130 of 135 blocked rows). Row 243:
gold `1 per 4 month`; raw selection is `final_label: "1 per 4
month"`, `final_kind: "frequency_rate"`. Every other local
scores the letter. The 14B model is not worse at the clinical
object than Qwen 3.5 on those rows; it leaks the event-kind
vocabulary into the selection kind. If those 61 blocked
Purist-correct labels had validated, 2.5 would sit at 423/750,
just above 3.5. That is a diagnostic counterfactual, not a
repair proposal.

Llama's schema miss is emptier. Row 212 gold is `1 per 3 to 4
week`. The raw object lists that rate as the first event and
omits `fact_id` / `event_id` on every fact. Repair will not
invent ids when none exist. The same letter is Purist-correct
on Qwen 3.5, 2.5, Gemma, 3.8, and 3.6. Llama also copies
`frequency_rate` into `final_kind` (23 blocked rows) and drops
`temporality` (37).

Qwen 3.5 mixes the 2.5 enum leak (`frequency_rate`, invented
kinds such as `multiple per week` and `unknown cluster count`)
with omitted `temporality`. Qwen 3.6 is the messy-JSON model:
305 rows need dialect repair (trailing commas, control
characters, unmatched closes). Most of those repairs succeed;
the 32 that do not are truncated or still missing
`temporality`. Gemma and 3.8 are down to a handful of leftover
kind strings (`unknown_cluster_count`) and one extra top-level
`selected_fact_ids` next to `selection`.

Format retry does not rescue the wall. Llama's 114 blocked
rows are 114 rejected retries. Qwen 3.5 rejects 83. Qwen 3.8
rejects 4. The retry is asked not to change clinical values;
missing ids and illegal enums are not a dialect typo.

### Why exact evidence failures happen

Selected evidence is scored exact-or-not. A paraphrase that
points at the right sentence still fails the gate. A correct
Purist label can sit on invalid evidence.

| Model | Exact | Exact and Purist-wrong | Inexact and Purist-right | Empty selected evidence | Main inexact class |
| --- | ---: | ---: | ---: | ---: | --- |
| Llama 3.1 8B | 277 | 147 | 85 | 34 | absent / paraphrase (186+108) |
| Qwen 3.5 9B | 399 | 124 | 137 | **116** | empty, then paraphrase |
| Qwen 2.5 14B | 468 | 183 | 77 | 26 | paraphrase / absent |
| Gemma 4 26B | **699** | 229 | 12 | 10 | residual absent |
| Qwen 3.8 27B | 693 | 189 | 42 | 1 | residual absent / ellipsis |
| Qwen 3.6 35B | 576 | 174 | 74 | 7 | **ellipsis join (71)** |

Three different evidence failures, not one:

1. **Invented sentence (Llama).** Row 466 is Purist-correct
   (`21 to 28 per month`) with evidence `The patient reports an
   ongoing pattern of 21 to 28 seizures per month.` That
   sentence is not in the note. The count is. Llama writes a
   caption. 85 Llama rows are inexact and still Purist-right;
   388 are inexact and wrong. Evidence failure here is a
   symptom of not copying, not the only clinical error.

2. **Blank quote (Qwen 3.5).** 116 structured rows have an
   empty selected `evidence` string. 59 of those are still
   Purist-correct. The model often knows the label and skips
   the substring obligation. That is why 3.5's evidence-valid
   count (399) lags its structured count (657) more than Gemma
   or 3.8.

3. **Ellipsis join (Qwen 3.6).** 71 inexact rows glue two
   spans with `...`. Row 187: evidence is `events tend to
   cluster every seven to nine days... Over the same interval,
   there have been two nocturnal generalised tonic–clonic
   seizures`. The grade cascade would repair that to one source
   span (`REPAIRED_ELLIPSIS`); the cell scores exact
   containment only, so it stays invalid. This is the same 3.6
   habit seen on the older hybrid stack (140 ellipsis joins
   there). 3.8 has 13 leftover ellipsis rows, not 71.

Gemma and Qwen 3.8 mostly copy. Their leftover miss is
clinical, not quote-shaped: 229 and 189 rows are exact and
still Purist-wrong. Qwen 3.8 has only 15 inexact-and-wrong
rows. Evidence validity is no longer the ranking among the
large locals; 3.6 is the exception.

Llama misses exact evidence on 424 letters that 3.8 copies.
Qwen 3.6 misses 148 letters that 3.8 copies. That is the
clearest scale/generation split that is not a score.

### Clinical error modes

Gold-kind Purist recall on all 750 (parse misses count as
wrong):

| Gold kind (n) | Llama | Qwen 3.5 | Qwen 2.5 | Gemma | Qwen 3.8 | Qwen 3.6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| frequency (468) | 0.314 | 0.506 | 0.440 | 0.611 | **0.701** | 0.645 |
| seizure_free (112) | 0.491 | 0.902 | **0.982** | 0.955 | 0.964 | 0.946 |
| unknown (100) | 0.060 | 0.380 | 0.130 | **0.660** | 0.530 | 0.280 |
| no_reference (27) | 0.000 | 0.667 | 0.593 | 0.074 | **0.963** | 0.481 |
| unresolved_multiple (43) | 0.163 | 0.419 | 0.395 | 0.488 | **0.721** | 0.628 |

Seizure-free is solved early. Llama is the only model still
bad at it. Frequency recall is the ranking. Unknown and
no-reference are where generation, not size, shows up.

#### Correct facts, wrong pick

On structured Purist misses, the gold Purist bucket is already
in the event list on 150 Llama rows, 79 Qwen 3.5, 84 Qwen 2.5,
86 Gemma, 63 Qwen 3.8, and 82 Qwen 3.6. The inventory was good
enough. Select lost the letter.

The recurring conflicts:

- **Quiet tail over a recent count.** Row 1165, gold `5 to 7
  per 3 week`. The note also says no further episodes for six
  weeks. Qwen 3.5 keeps `5 to 7 per 3 week`. Qwen 2.5, Gemma,
  and Qwen 3.8 all select `seizure free for 6 week`. Llama
  lands `5 per week` (Purist-right, sloppy encode). Qwen 3.6
  writes `1 per 6 week`. Larger/newer models are *more* willing
  to follow the seizure-free span. The living case "do not
  choose seizure-free while seizures continue" and the case
  "recent seizures after a quiet spell" pull in opposite
  directions; locals do not share one policy.

- **Competing current types.** Row 1979, gold `6 per 2 month`
  (focal) versus `2 per week` (nocturnal movement clusters).
  Gemma and Qwen 3.6 take the overall/gold count. Qwen 3.8
  takes the nocturnal rate. The "highest current overall
  count" case is in the prompt. 3.8 does not always apply it.

- **Cluster versus plain rate.** Gold `unknown, multiple per
  cluster` (row 1317) is read as `multiple per day` by 3.5,
  3.8, and 3.6. Gemma writes a cluster form
  (`1 cluster per day, multiple per cluster`) and still misses
  gold unknown. The shared hard set is heavy on this family
  (68/98 all-wrong letters are gold frequency; many are cluster
  or dated-count conventions).

- **Unknown filled with a specific.** Structured unknown/no-
  reference golds scored as a rate or seizure-free: Llama 74,
  Qwen 2.5 63, Qwen 3.8 34, Qwen 3.5 29, Gemma 28, Qwen 3.6 26.
  Llama and 2.5 almost never abstain (12 and 16 written
  `unknown`). Gemma writes 99 `unknown` and is the best unknown
  recall (66/100). That abstention is the same habit that
  destroys no-reference (below).

Row 3371 is the shared convention miss: gold `unknown`, last
event plus "no events have occurred in the past eight weeks."
All six write a seizure-free duration (3.6: eight weeks read as
`seizure free for 2 month`). Exact evidence does not help;
five of six quotes are exact.

#### Correct kind, null label

Gemma's no-reference collapse is not a find miss. On 24 / 27
gold `no_reference` rows it extracts a `no_reference` fact,
sets `final_kind` to `no_reference`, and leaves `final_label`
null (often with empty evidence). The extract-stop scorer
returns no comparison when `final_label` is missing, so the
row is a miss. Qwen 3.8 writes the sentinel string `no seizure
frequency reference` on 26 / 27. Gemma knows the class and
does not emit the codebook token.

Qwen 3.6 has 45 null labels (22 tagged `unknown`, 10
`no_reference`, 10 `unresolved_multiple`). Null label is an
older-generation leftover. Qwen 3.8 is down to 8, mostly
`unresolved_multiple`.

#### Form and illegal leftovers

The Pragmatic−Purist gap is the form wall. It shrinks as
models get newer, not merely bigger: Llama +119, Qwen 2.5 +59,
Qwen 3.5 +50, Gemma +53, Qwen 3.6 +50, Qwen 3.8 +39.

Llama still writes `infrequent`, `ongoing`, `several per week`,
`1 every 6 days`, `1 per night`, `1 per 2d`. Those are the
prompt's forbidden leftovers. Qwen 2.5 still writes `several`,
`per hour`, `per night`, and incomplete cluster strings
(`1 cluster per week` with no per-cluster count). By 3.8 the
leftovers are codebook-edge, not English hedges: `9 per hour`,
`1 cluster per 2 to 3 days`, `5 or 7 per year`. Form/bucket
near-misses on 3.8 are unit or cluster-versus-rate projection
(gold `1 per 7 to 9 day` versus `1 cluster per 7 to 9 days,
multiple per cluster`; gold `1 per month` versus `1 per
multiple months`).

Qwen 2.5 is also eager to overwrite a current rate with a
seizure-free span (45 structured frequency→seizure-free
misses). Gemma and 3.8 still do this (29 and 35) but on a
higher frequency baseline. Qwen 2.5's seizure-free recall
(0.982) is the other side of the same habit.

### How the models differ

**Llama 3.1 8B** fails three gates at once: schema (no
`fact_id`), evidence (captions), and form (illegal words). It
over-extracts (mean 4.37 events versus ~2.3 on the others) and
almost never writes `unknown`. When it is clinically close, the
label is often still illegal. This is not a small version of
3.8.

**Qwen 2.5 14B** is the schema-specialist failure. One missing
alias (`frequency_rate` as `final_kind`) accounts for the
headline parse rank. Among structured rows it is a
high-seizure-free, low-unknown model: it fills unspecified
notes and prefers a quiet tail. Size over 3.5 is spent on a
vocabulary leak, not on better selection.

**Qwen 3.5 9B** is the first model that behaves like the large
set. Structured Purist (0.627) already matches Gemma. It
abstains more than 2.5, uses cluster forms, and keeps some
conflict cases that 3.8 later drops (row 1165). Its distinctive
remainders are parse (missing `temporality` / invented kinds)
and empty evidence. Newer and smaller beats older and larger.

**Gemma 4 26B** has Gemini-like JSON (8 parse, 699 exact
evidence) and a local-model select. Bundling select into the
find call is expensive: one-call 482 versus its own cell 3
extract 501 and select 567. It over-writes `unknown` (best
unknown recall, worst no-reference recall). Exact+wrong (229)
is the residual. Schema is no longer the story.

**Qwen 3.8 27B** is the only local that is simultaneously
good at JSON, exact quotes, no-reference sentinels, and
frequency recall. Remaining miss is find (107) then select
(41) then form (26). Schema-blocked rows are not near-correct
(0 / 8 would have been Purist). It still loses the quiet-tail
versus recent-count argument and some overall-count conflicts.
It is below its own cell 3 select (546 vs 577) and 111 below
Gemini one-call.

**Qwen 3.6 35B** is 3.8's older, larger sibling. More dialect
repair, more parse, more ellipsis evidence, more null labels,
weaker unknown and no-reference. Frequency recall (0.645) sits
with Gemma, not above 3.8. On a few conflict letters it wins
where 3.8 loses (row 1979). That does not change the ranking.

### What changes as models get bigger or newer

What goes away, in order:

1. **Empty or id-less JSON** (Llama). Later models always
   stamp `f1`.
2. **Event-kind leaked into `final_kind`** (Qwen 2.5's 130
   rows). Residual on Gemma/3.8.
3. **English leftover labels** (`infrequent`, `ongoing`,
   `several`). Gone as a mass mode by 26B+.
4. **Caption evidence and blank quotes.** Llama paraphrases;
   3.5 leaves evidence empty; 26B+ mostly copy. 3.6 keeps
   ellipsis.
5. **Seizure-free class error.** Solved from 3.5 upward.
6. **No-reference sentinel omission.** Solved on 3.8, not on
   Gemma or 3.6.

What does not go away, and is the Gemini gap:

1. **Find on hard frequency letters** — dated counts, cluster
   burden, "usual gap versus spell," menstrual clustering
   read as a monthly rate. Even 3.8's largest owner is find
   (107).
2. **Conflict resolution among true facts.** Quiet tail versus
   recent count; one type versus overall; cluster versus rate;
   last-event-plus-well versus gold unknown. Bigger models are
   not uniformly better (1165, 1979, 3371).
3. **Unknown boundary.** Small models fill. Gemma over-
   abstains. 3.8 is in the middle (53/100). 98 letters remain
   wrong on every local; 23 of those are gold unknown.
4. **Form/bucket near-misses** after the illegal-word wall
   falls: hour rates, cluster dialect, `multiple months`
   versus `1 per month`.

Newer beats larger inside the Qwen line (3.5 > 2.5; 3.8 >
3.6). Crossing 26B mostly buys JSON and exact quotes, not
select. That is why Gemma can look "solved" on schema/evidence
and still sit 64 Purist below 3.8, and why one-call is not a
substitute for cell 3 rules-select on the living locals.

### Worked letters

Row **243** (gold `1 per 4 month`). Schema-only miss on Qwen
2.5: the raw label is already gold, `final_kind` is
`frequency_rate`. Llama, 3.5, Gemma, 3.8, 3.6 are Purist-
correct.

Row **212** (gold `1 per 3 to 4 week`). Llama omits every
`fact_id`; blocked. The others score. Gemma's label is `3 to 4
per month` (same Purist bucket, different wording).

Row **1165** (gold `5 to 7 per 3 week`, competing six-week
quiet tail). Qwen 3.5 selects the count (inexact evidence).
Qwen 2.5 / Gemma / 3.8 select seizure-free. Llama is
Purist-right with `5 per week`. This is select policy, not
JSON.

Row **1979** (gold `6 per 2 month` versus nocturnal `2 per
week`). Gemma and 3.6 take gold. 3.8 takes the nocturnal rate.
3.5's `3 per 2 month` still lands the Purist bucket. Same
prompt, three picks.

Row **3371** (gold `unknown`; "no events have occurred in the
past eight weeks"). All six write seizure-free. Shared
convention miss. Not a size effect.

Row **466** (gold `21 to 28 per month`). Llama is Purist-
correct and evidence-invalid: it quotes a sentence it wrote.
Exact evidence and score can diverge.

## Claim boundary

Local-model transfer of the frozen one-call ablation.
Development row review only. `test450` is aggregate-only. Not
Table 1. Not a living roster change. Not a reason to edit the
prompt, the `frequency_rate` alias, or the scorer from this
read. The schema-alias counterfactuals are diagnostic. Cell 3
for Llama 3.1, Qwen 3.5, Qwen 2.5, and Qwen 3.6 is still open.
