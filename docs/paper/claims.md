# What the evidence supports

Date: 2026-08-20
Revised: 2026-08-23 (all five Gemini ExECT rows use 4-family micro F1)
Status: current
Owner: this file

This page is the paper's reading of the living comparison. Method names
and splits are on [methods](methods.md). The Gan headline table is five role rows. Each of extract, encode,
and select is rules, LLM, or both. The cited score is the select
stop. Extract and encode stops are prior-stage ablations. ExECT
uses the same five role rows. Neither table is five depths of one
hybrid switch. Replayable
numbers live in
[`paper_experiments/`](../../paper_experiments/README.md). Writing
sources that unpack the same evidence are the
[Gan Gemini stage reading](../research/paper/gan_rules_and_llms_across_stages_2026-08-21.md),
the [Gan story](../research/paper/gan_story_2026-08-10.md), and the
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
method. The six-model comparison is cell 3 only (LLM extract, rules
encode, rules select) on both tasks. Thinking low / medium / high
is a Gemini cell-3 extract ablation. The source-near Gan extract
(`gan_llm_extract_raw`) is a wording-versus-form ablation, not a
results column. Later-stage LLM encode and LLM select calls are
Gemini only. Scores do not move between tasks.

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

The Gan headline comparison is five role combinations (rules, LLM,
or both at extract / encode / select). The cited score is the select
stop. On Gan, LLM extract is the codebook extract
(`gan_llm_extract`). **both** extract is
`gan_llm_and_rules_extract`. LLM encode means that extract already
wrote the form. LLM-then-rules encode is `gan_rules_encode`. LLM
select is `gan_llm_select_from_extract`. ExECT uses the same five
role rows. LLM extract is `exect_llm_extract`. The Compact
`exect_llm_extract_filtered` extract is a Gemini ablation. both extract is
`exect_llm_pre_post`. LLM encode is later-stage `exect_llm_encode`.
LLM / LLM / rules is accepted Select on that encode ledger. LLM
select is later-stage `exect_llm_select`. The old `gan_llm_extract_raw` grid is the source-near wording
ablation, not a headline. The six-model row is LLM / rules / rules
on both tasks. The worked reading is
[five cells of rule help](../paper/method_x_stage.md),
the [Gan five-cell grid](../research/gan2026/gan_five_cell_grid_2026-08-22.md),
and
[ExECT cell 4](../research/exectv2/exect_rule_select_after_llm_encode_2026-08-22.md).
`gan_llm_only` is a different prompt and is not a results column.
An unrepaired `*_pre_post` body is not LLM extract.
A recorded rule may change clinical meaning; deterministic does not
mean neutral or safe. A recorded hop is not a clinically correct
step. A later cell is not automatically better. Development hop shares
are not holdout component estimates.

## Current seizure frequency

### What the locked totals show

On 450 held-out letters, written rules scored 0.73. Gemini LLM
extract (`gan_llm_extract`) plus `gan_rules_encode` plus rule select scored 0.83. The paper
may say those locked totals and the Gemini grid below.
It may not treat `gan_llm_only` as a results column.
That request is a different prompt (one finished label). Its Grok
holdout cell is 0.73; it is not extract or encode.

Named Gemini `test450` headline (aggregate-only; select stop). Owner:
[five-cell grid](../research/gan2026/gan_five_cell_grid_2026-08-22.md).

| Extract | Encode | Select | Purist |
| --- | --- | --- | ---: |
| rules | rules | rules | 0.73 |
| both | rules | rules | 0.82 |
| LLM | rules | rules | 0.83 |
| LLM | LLM | rules | 0.82 |
| LLM | LLM | LLM | 0.79 |

Hybrid select is ledger-only (`elapsed_anchor` and `residual_jerk`
off). The paper may say that, with Gemini as the cited model, the
strongest row is LLM extract plus codebook rule encode plus rule
select (0.83). It may say rule select without encode, and both-then-
rules, are 0.82. It may say LLM select is 0.79. It may say extract
and encode stops are prior-stage ablations, not a second headline
table. It may not say which letters moved. The historical
selected-evidence encoder on the codebook extract (encode 0.77,
select 0.80) stays an ablation. The source-near `gan_llm_extract_raw`
grid (LLM extract 0.55, later-stage select 0.71, hybrid select 0.79)
stays an ablation: the softer extract keeps letter wording and
scores 0.55; rule encode and rule select recover to 0.79. The paper
may say that shows wording can be kept and later mapped into the
gold form. It may not say the softer extract preserves clinical
reasoning. Grok living `gan_llm_extract_raw` 0.83 was not re-scored
on the codebook stack. The six-model comparison for this paper is
the codebook cell 3, not that source-near hybrid.

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

Named Gemini `dev750` select stops on the same codebook extract.

| Extract | Encode | Select | Purist |
| --- | --- | --- | ---: |
| rules | rules | rules | 0.89 |
| both | rules | rules | 0.89 |
| LLM | rules | rules | 0.86 |
| LLM | LLM | rules | 0.85 |
| LLM | LLM | LLM | 0.79 |

The source-near `gan_llm_extract_raw` development grid (extract 0.59,
later-stage encode 0.67 / select 0.76, hybrid select 0.88) stays an
ablation. Locked `test450` stage cuts are in the table under locked
totals.

Companion Grok LLM then rules on `gan_llm_extract_raw`: extract
0.49, encode 0.80, select 0.89.

On the Gemini raw, selected-evidence render never changed
`selected_event_ids`, so it is encode. It changed predicted kind 219
times and rescued 167 Purist letters (three harms). Those scores
explain the *kind* of work recorded encode does. They are not holdout
component shares. The paper may say the lift is stepwise (extract →
encode → select) on one raw, and that Rules then LLM is a
different extract request. It may
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

On 59 held-out letters, written rules recovered 0.7725 of clinical
facts. Gemini both-extract (living extract plus suggested
candidates, then rule select) scored 0.8592. Gemini extract plus
rule select scored 0.8674. Later-stage encode plus rule select
scored 0.8636. Later-stage LLM select scored 0.853. The paper may
say those locked totals and the Gemini grid below, and may write
the five select stops as 0.77, 0.86, 0.87, 0.86, and 0.85. It may
not treat a living producer F1 as LLM extract. The retired
Compact/headline cell 2 / cell 3 / cell 4 / cell 5 selects (0.8031
/ 0.8161 / 0.8173 / 0.7954) are not the cited rows.

Named Gemini `test60` (aggregate-only; select stop). All five rows
use 4-family micro F1 (`clinical_inventory_unit_keys`). Owner:
[both-extract on inventory](../research/exectv2/exect_both_extract_on_inventory_protocol_2026-08-23.md)
and
`paper_experiments/exect/five_cell_grid/gemini37flash/test60/comparison.json`.

| Extract | Encode | Select | F1 |
| --- | --- | --- | ---: |
| rules | rules | rules | 0.77 |
| both | rules | rules | 0.86 |
| LLM | rules | rules | 0.87 |
| LLM | LLM | rules | 0.86 |
| LLM | LLM | LLM | 0.85 |

On 140 development letters the Grok grid is:

| | Extract | Encode | Select |
| --- | ---: | ---: | ---: |
| **Rules** | 0.9042 | 0.9042 | 0.9042 |
| **LLM** | 0.6485 (flatten only) | — | — |
| **LLM then rules** | 0.6485 (flatten only) | 0.8197 | 0.9040 |
| **Rules then LLM** | — | — | 0.8998 (`exect_llm_pre_post`) |

Rungs 2–4 share one `exect_llm_only` output. Rung 5 is a different
request. Dictionary rewrite is revise, not encode. Live
`exect_llm_only` Grok `dev140` raw F1 remains 0.8212; that gated
producer view is not llm extract. SeizureFrequency schema F1 is 0.0
because the clinical-fact key needs the codebook id that format
attaches. The paper may not say the inventory format stop is empty.
It may not park a semantic SF projection on the format rung.

On the locked inventory the strongest cited row is LLM extract plus
rule select (0.8674). Both-extract plus rule select is 0.8592.
Later-stage encode plus rule select is 0.8636. Later-stage LLM
select is 0.853. Standalone rules are 0.7725. Those five reads are
0.87, 0.86, 0.86, 0.85, and 0.77 at two decimals. The retired
Compact/headline cell 2–5 stops (0.8031 / 0.8161 / 0.8173 /
0.7954) are not the cited rows. Extract and encode stops are
prior-stage ablations. Luna after repair recovered 78.3%
(88.8% on development) on the prior assembly. DeepSeek and Gemma
have prior-assembly repair totals on both inventory splits (DeepSeek
held-out 81.2%; Gemma held-out 69.3%). Their model-alone inventory
cells are not yet on disk. Qwen is missing both inventory model
methods.

The paper may say that, with Gemini as the cited model, rule select
after the inventory extract is the strongest row, and that
later-stage encode then the same Select does not raise that holdout
stop. It may not rank providers, and it may not treat those
percentages as the 2019 benchmark. It may not say which holdout
letters moved. It may not compare 4-family micro F1 to
Compact/headline F1 as if they shared a denominator.

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
4. On locked frequency letters, Gemini LLM extract plus codebook
   encode plus rule select raises the locked score by 0.10 against
   standalone rules (0.83 vs 0.73). Rule select without encode, and
   both-then-rules, are 0.82. LLM select is 0.79. Grok living
   hybrid 0.83 is a different stack on the source-near request.
   `gan_llm_only` is not in that comparison.
   On the locked inventory, Gemini LLM extract plus rule select is
   0.8674 against standalone rules 0.7725, both on 4-family micro
   F1. Both-extract plus rule select is 0.8592. Later-stage encode
   plus rule select is 0.8636. Later-stage LLM select is 0.853. The
   five select stops read 0.87, 0.86, 0.86, 0.85, and 0.77 at two
   decimals.
   These totals compare methods; they do not attribute holdout
   effects to individual rules. One extraction is not a second use
   case.
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

Grok has no Full-ledger cell. 4-family micro F1 is not the 2019
published score. Held-out letters are not read and not cited by row.
