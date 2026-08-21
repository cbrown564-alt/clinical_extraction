# What the evidence supports

Date: 2026-08-20
Revised: 2026-08-21 (headline is a 3×3: rules / llm / hybrid × extract / encode / select)
Status: current
Owner: this file

This page is the paper's reading of the living comparison. Method names
and splits are on [methods](methods.md). The headline table is a 3×3;
it is not five depths of one hybrid switch. Replayable
numbers live in
[`paper_experiments/`](../../paper_experiments/README.md). Writing
sources that unpack the same evidence are the
[Gan story](../research/paper/gan_story_2026-08-10.md) and the
[ExECT story](../research/paper/exect_story_2026-08-12.md).

A stronger sentence than this page is not a paper sentence. The job of
the page is the supported reading, not a list of things to avoid.

## How strong a sentence may be

| Strength | Means |
| --- | --- |
| **Locked total** | Saved overall score on a held-out split. Letters were not read. |
| **Development mechanism** | Replay on letters that may be read. Explains *how* a change happened. Not a holdout component estimate. |
| **Engineering** | Tests, hashes, split locks, replay. Not clinical validation. |
| **Unsupported** | The files do not bear the sentence. |

Gemini 3.7 Flash is the cited model, so the story stays on the
method. Grok, Luna, DeepSeek, Qwen, and Gemma are companion rows.
Later-stage LLM encode and LLM select calls are Gemini only. Scores
do not move between tasks.

## Central claim

The proposed method translates clinic letters into structured clinical
facts in a designed form, with quoted source text. A model collects the
facts and evidence. Recorded rules then shape those facts into the
required form. Those mappings can be replayed on the same model output
without a new call. The two public golds are the evaluation forms used
in this paper, not the definition of the method.

The strongest cross-task formulation currently supported is:

> The proposed method keeps a source span and a change log while
> translating letters into a designed structured form. On two public
> evaluation golds it beats a model alone and beats or slightly beats
> standalone rules. Gemini is the cited model; Grok repeats the pattern
> where both cells exist.

This is a claim about the recorded object and the locked totals. It is
not a claim that the system exposes a model's internal reasoning, that
every rule is a free switch, that one extraction already serves
multiple use cases, or that a visible step is clinically correct.

## The comparison

Clinic letters hold epilepsy facts that tables omit. The proposed
system asks two different questions of those letters.

**Current seizure frequency** (Gan 2026) asks for one current label per
letter. Several statements in the letter can be true; only one is the
scored current state. The primary score is the share of letters whose
fine frequency band is correct.

**Clinical inventory** (ExECT) asks for the supported set of diagnoses,
frequency facts, medicines, and investigations. Missing a fact, merging
two facts, or adding an unsupported rate is an error. The primary score
is how completely those four kinds of fact were recovered. It is a
research measure. It is not the published 2019 ExECT benchmark.

The headline comparison is a 3×3: rules / llm / hybrid against
extract / encode / select. Rules repeat one score in every stage
column. LLM has extract only until Gemini later-stage encode and
select runs exist. Hybrid extract is the `*_pre_post` request (was
cell 5). Hybrid encode and hybrid select replay the
`gan_llm_with_rules` / `exect_llm_only` raw (were cells 3 and 4).
The worked reading is
[five rungs of rule help](../research/paper/five_rungs_of_rule_help_2026-08-20.md).
`gan_llm_only` is a different prompt and is not a results column.
An unrepaired hybrid body is not llm extract.
A recorded rule may change clinical meaning; deterministic does not
mean neutral or safe. A recorded hop is not a clinically correct
step. A later cell is not automatically better. Development hop shares
are not holdout component estimates.

## Current seizure frequency

### What the locked totals show

On 450 held-out letters, written rules labelled 329 correctly
(73.1%). That score fills every rules column. Gemini hybrid extract
(`gan_llm_pre_post`) labelled 372 (82.7%). Gemini hybrid select
labelled 373 (82.9%). Grok hybrid extract labelled 370 (82.2%).
Grok hybrid select labelled 375 (83.3%). Those extract and select
cells are different requests. The paper may say those locked totals.
It may not treat `gan_llm_only` as a results column.
That request is a different prompt (one finished label). Its Grok
holdout cell is 327/450 (72.7%); it is not extract or encode.

The paper may say that, with Gemini as the cited model, hybrid select
clears the rules baseline on this locked set, and that Grok repeats the
pattern. It may say the gain is an overall count. It may not say
which letters moved.

The rule baseline is a standalone deterministic pipeline. It is not the
same rule set that later repairs model events. The gap from rules to
Gemini-plus-select is therefore a method comparison, not a
measurement of those later repair stages in isolation.

### What development replay shows about the lift

On development letters, most first corrections after the model are
recorded rules, not a new reading of the letter. In a six-model
development provenance study, 1,437 of 1,539 first rescues (93%)
rendered a span the model had already selected. Eighty-nine composed a
label from events the model had already extracted. Thirteen promoted
another extracted event. None invented a rate from text the model never
quoted.

Named Gemini `dev750` 3×3, from standalone rules, one saved
`gan_llm_with_rules` raw, and (blank) later-stage LLM calls:

| | Extract | Encode | Select |
| --- | ---: | ---: | ---: |
| **Rules** | 669/750 | 669/750 | 669/750 |
| **LLM** | 444/750 (0.5920), 532 scorable | — | — |
| **Hybrid** | 675/750 (0.9000) living `gan_llm_pre_post` | 608/750 (0.8107) | 677/750 (0.9027) |

Companion Grok on the shared `gan_llm_with_rules` raw: llm extract
371/750, hybrid encode 603/750, hybrid select 671/750.

On the Gemini raw, selected-evidence render never changed
`selected_event_ids`, so it is encode. It changed predicted kind 219
times and rescued 167 Purist letters (three harms). Those scores
explain the *kind* of work recorded encode does. They are not holdout
component shares. The paper may say the lift is stepwise (extract →
encode → select → pre-suggestion) when the rung-5 cell exists. It may
not treat a development hop share as a holdout component estimate.

The paper may say the mass first change is label rendering of a span
the model already chose, and that later select rules can still switch
the reading (diary, dated count, usual rate, breakthrough). It may not
say that recorded repair is causally necessary on held-out letters, or
that it never harms an answer. Luna is the Gan pre-post development
iterator. It is not the cited model. Later-stage LLM encode and LLM
select calls are Gemini only, on both tasks.

### What remains hard

The remaining problem is no longer malformed rate syntax. It is
choosing among clinically plausible readings.

Cluster descriptions need two linked quantities: how often clusters
occur, and how many seizures occur in one cluster. Models often flatten
that into a smooth rate or an unknown. On unknown-gold development
letters, some clinical rules turn a justified unknown into a false
active rate or a false seizure-free answer. Removing the breakthrough
rule rescues some of those unknowns and harms the wider ledger, so the
files do not support switching it off.

Gold agreement is a measured proxy. Development row 10 is a gold-dialect
rule, not lost evidence. Grok quoted “≤ four per day.” Recorded repair
rendered `4 per day`, which is the Gan gold form. The span stays in the
object. The bound is not in the submitted label. That mapping can be
inspected, and the same model output can be replayed with
selected-evidence repair off. Turning that family off disables the
whole renderer, not only bound-flattening. A different convention would
need its own gold; this gold still scores `4 per day`.

## Clinical inventory

### What the locked totals show

On 60 held-out letters, written rules recovered 79.4% of clinical
facts and living Gemini hybrid extract (`exect_llm_pre_post`) recovered
81.3%. Grok hybrid extract recovered 80.5%. Grok `exect_llm_only` raw
F1 is 77.3% on that locked set; it is not llm extract flatten. On 140
development letters the Grok 3×3 is:

| | Extract | Encode | Select |
| --- | ---: | ---: | ---: |
| **Rules** | 0.9042 | 0.9042 | 0.9042 |
| **LLM** | 0.6485 (flatten only) | — | — |
| **Hybrid** | 0.8998 (`exect_llm_pre_post`) | 0.8197 | 0.9040 |

Rungs 2–4 share one `exect_llm_only` output. Rung 5 is a different
request. Dictionary rewrite is revise, not encode. Live
`exect_llm_only` Grok `dev140` raw F1 remains 0.8212; that gated
producer view is not llm extract. SeizureFrequency schema F1 is 0.0
because the clinical-fact key needs the codebook id that format
attaches. The paper may not say the inventory format stop is empty.
It may not park a semantic SF projection on the format rung.

Gemini after repair recovered 81.3% of facts on the 60 held-out
letters (89.5% on development). Luna after repair recovered 78.3%
(88.8% on development). DeepSeek and Gemma have repair totals on both
inventory splits (DeepSeek held-out 81.2%; Gemma held-out 69.3%).
Their model-alone inventory cells are not yet on disk. Qwen is
missing both inventory model methods.

The paper may say that, with Gemini as the cited model, hybrid extract
sits above the model-alone request and slightly above written rules on
the locked inventory, and that Grok's total is in the same band. It
may say the inventory gain is smaller than the frequency-label gain. It
may not rank providers, and it may not treat those percentages as the
2019 benchmark.

### What development replay shows about the lift

The model proposes all four kinds of fact in one structured call.
Recorded rules then do different jobs by kind of fact, on development
letters:

- **Diagnosis** rewrites many concept substitutions and omissions
  (exactness 0.39 → 0.58 on the recorded diagnosis transform; 212
  rescues and 49 harms). Most first rescues reuse a model quote that
  was not scored as that diagnosis, or drop extras. A small class adds
  a diagnosis from letter text the model did not quote.
- **Seizure frequency** drops unsupported states at the producer check
  (305 rescues and no recorded harms at that stage). Almost all first
  rescues re-render a model state. Missed and mixed inventories remain.
- **Medicines** are strong overall, but not every rule helps. An
  earlier transform recorded 44 rescues and 60 harms. Removing two
  development-fitted rules produced a simpler transform, confirmed on
  an aggregate held-out check. The surviving first rescues rewrite a
  drug the model already named.
- **Investigations** do not change the scored answer in the selected
  repair configuration. Standalone rules now bind investigation
  findings themselves; that is why rules are no longer the
  investigations floor.

The paper may say recorded repair is family-specific, that the mass
frequency rescue is a re-render of a model state, and that two harmful
medicine rules were deleted after a measured harm. It may not say every
deterministic correction is safe, or that those family lifts are
holdout component estimates.

### What remains hard

The remaining problem is keeping a complete, unmerged, evidence-
supported set. Frequency facts are again the hardest part of the
inventory, as they were for the original ExECT rules. Named windows,
missed states, and mixed inventories persist after the producer check.
Single-seizure diagnosis remains a shared difficulty for the model
alone. Gold agreement is still a proxy: in development letter EA0007,
Grok quoted a hedged onset, the diagnosis dictionary rewrote it to
`focal epilepsy`, and the letter matched gold. The trace is
inspectable. The rewrite is a task-format commitment, not an
unqualified clinical diagnosis.

## What both tasks support together

The files support this account of the proposed method, cited on Grok:

1. The method translates letters into structured facts in a designed
   form, with quoted source text. Recorded rules shape the collected
   facts. This paper evaluates two forms: Gan's one current state, and
   ExECT's four-family inventory. The public golds are those evaluation
   forms, not the task.
2. The output that matters is the full object: the source span, the
   named rule changes, and the submitted answer. The score is how that
   answer is judged.
3. Development replay names the first recorded rule change and whether
   it rescued, harmed, or did nothing. Most first Gan changes re-render
   a span the model already chose. Some later rules switch the reading,
   add a diagnosis, cause harm, or do nothing. The same model output can
   be replayed without a new call. A named family is not always a free
   switch: removing breakthrough helps some unknowns and harms the
   wider ledger.
4. On locked frequency letters rung 4 raises the correct-label count
   by 46 against standalone rules. `gan_llm_only` is not in that
   comparison. On the locked inventory the rise from the model-alone
   request to living hybrid is smaller, and slightly above standalone
   rules. These totals compare rungs or requests; they do not
   attribute holdout effects to individual rules. One extraction is
   not a second use case.
5. The remaining disagreements are current-state choice and incomplete
   inventories: which evidence is decisive, which reading is current,
   whether a cluster has two quantities, whether an unknown should stay
   unknown, whether an inventory is complete, and what the score throws
   away. The same record makes those disagreements visible.

They do not support a claim that the architecture is state of the art,
that the two tasks share a reliability transfer, that every rule is
safe, that the system is clinically validated, or that this record is
ready for clinical use.

A matching score establishes agreement with the gold, not clinical
truth. An exact source span establishes textual presence, not that the
span is relevant, decisive, sufficient, or complete. The score cannot by
itself identify which upstream decision produced an error.

Normalization improves both tasks on named development replays. The
exact-evidence check is score-neutral on those replays: it does not
raise the score when the selected predictions already quote the
letter, and a zero delta is not evidence that the check is unused.
Split locks, replay hashes, and the always-on tests are engineering
verification.

Some inventory disagreements on development letters concern
annotation multiplicity, representation, convention, or ambiguity.
That is an internal reading of specific cases. It is not a prevalence
estimate and not an independent clinical review.

## What is on disk

Frequency development cells exist for Grok, Luna, and Gemini, both
model methods. Frequency locked totals exist for Grok and Gemini, both
model methods, and for rules. Inventory repair cells exist for Grok,
Luna, Gemini, DeepSeek, and Gemma on both splits. Inventory model-
alone cells exist for Grok, Luna, and Gemini on both splits. Inventory
rules exist for Grok. Qwen is pending on both tasks. DeepSeek and
Gemma model-alone inventory, and the remaining frequency locked
totals, are not yet present.

A missing cell is a missing cell. The paper reports the panel that
exists.

## Identities that would change the reading

These are the only mix-ups that falsify the comparison above. They
belong here because they are different experiments, not because the
paper is a list of bans.

| If the text uses | It is citing |
| --- | --- |
| Sol 381/450, or any Gan hybrid that still sent lab labels to the model | The enveloped request, not the cleaned frequency method |
| Compact-dump scores as model-plus-repair | A different inventory request shape |
| Full-ledger headlines as a sixth rung | The long control book, not a peer of the five-rung table |
| `gan_llm_only` as extract or encode | A different prompt, not the shared hybrid raw |
| Later-stage LLM encode / select on Grok, Luna, DeepSeek, Qwen, or Gemma | A run the paper did not authorise; those calls are Gemini only |
| GEPA, historical `v08`, full200, or all-nine paper-derived metrics as the inventory comparison | A different evaluation object |
| A three-pass multi-model frequency score | A different architecture |
| The 60-plus-140 inventory letters as one independent test | A development-inclusive audit, not a locked test |

Grok has no Full-ledger cell. Clinical fact recovery is not the 2019
published score. Held-out letters are not read and not cited by row.
