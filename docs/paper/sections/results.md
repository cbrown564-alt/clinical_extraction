# Paper results

Date: 2026-08-24
Revised: 2026-09-02 (two decision executors on one shared extract;
Rules-only and five-cell rows move to secondary; section D keeps three
codebook prompt ablations; inventory panel moves to supporting material)
Status: structured draft matching `paper/draft/FES.tex`
Owner: this file
Scope: [Gan is the dissertation paper](../decisions/gan-is-the-dissertation-paper.md),
[paper-story simplification](../decisions/paper-story-simplification.md)
Feasibility: [100-letter descriptive study](../../research/gan2026/gan_inventory_feasibility_dev750_n100_2026-08-28.md)

Paper stage names are **extract** (one LLM call; implementation
`find` with the codebook prompt, which already writes the gold form,
so `encode` is bundled) and **decide** (implementation `select`). The
extraction call's own pick is the **provisional answer**. Implementation
names appear below only where they identify an existing artifact.

## A. Experimental environment and evaluation

The experiments were run from two documented environments: hosted model
calls were primarily submitted from the Mac mini development machine, while
local Qwen and Gemma runs used Ollama on a Dell XPS 16 9640 with an NVIDIA
GeForce RTX 4070 Laptop GPU (8 GB VRAM). The supporting material records
the machine specifications, operating systems, software versions, model
routes, API settings, and local-runtime settings needed to reproduce each
reported condition.

Primary performance was evaluated on Gan 2026: whether the submitted
label was the required current seizure-frequency state. The living
primary is Purist micro-F1 on locked `test450` (aggregate-only).
Pragmatic micro-F1 is the companion grouping. Micro-F1 equals accuracy
here because each letter has one gold bin and one predicted bin.
Accuracy is not printed as a second headline.

A separate descriptive study asks whether a frozen ExECT-style
clinical-inventory schema can emit diagnoses, medicines,
investigations, and seizure-frequency statements from the same
synthetic letters. That study reports output volume and structure
only. It has no inventory reference labels and is not scored.

## B. Two decision executors on one shared extraction record

The paper's core comparison holds the extraction call fixed and
changes only who performs decide. Both executors replay the same
saved Gemini 3.7 Flash extraction record on locked `test450`, so the
difference between them is attributable to the decision stage alone
(Table 1).

| Decision executor | Provisional answer (after extract) | Final answer (after decide) | Pragmatic final |
| --- | ---: | ---: | ---: |
| Hybrid: rules | 0.79 (355) | **0.86** (387) | **0.88** (396) |
| LLM-only: second LLM call | 0.79 (355) | 0.85 (383) | 0.87 (391) |

**Table 1.** Locked aggregate-only Gan comparison, Purist micro-F1
with correct letters of 450. The extraction call is `gan_llm_extract`
(codebook prompt; already writes the gold form). Hybrid is the living
no-call replay of that extract through `gan_rules_encode` and
`llm_select_after_codebook`, including `last_event_well_since`
(387/450 Purist, 396/450 Pragmatic). LLM-only is
`gan_llm_select_from_extract` with the living policy-example decide
prompt on the same record (383/450 Purist, 391/450 Pragmatic).
Sources:
`paper_experiments/gan/rungs/gemini37flash/test450/comparison.json`,
`paper_experiments/gan/five_cell_grid/gemini37flash/test450/comparison.json`,
[the `test450` class report](../../research/gan2026/gan_test450_classification_report_2026-08-28.md).

The provisional answer is the extraction call's own pick and is what
a one-prompt system would submit. Rules add +0.07 (32 letters) and the
second call adds +0.06 (28 letters) on the same record. The two
executors differ on 28 letters (rules correct on 16, the second call
on 12). Paired exact McNemar on that pair: Δ+0.009, 95% CI −0.014 to
0.032, *p* = 0.57, compatible with no difference. Owner:
[paired `test450` tests](../../research/gan2026/gan_paired_significance_test450_2026-08-29.md).

The comparison with the previously reported fine-tuned benchmark
(Gan et al. Synthetic 1,166: Purist 0.81, Pragmatic 0.85) is bounded:
identical metric definitions and corpus, different held-out samples.
It is not a paired comparison and not a state-of-the-art claim. An
approximate two-proportion contrast is indicative only: Hybrid
+0.05 (95% CI +0.01 to +0.09, *p* = 0.01); LLM-only +0.04 (95% CI
0.00 to +0.08, *p* = 0.04).

**Secondary configuration rows (not paper rows).** The Gemini
five-cell grid remains repository evidence. Rules throughout is
0.72 (325) Purist / 0.77 (345) Pragmatic (promoted three-stage
program; living rules find is source-near 190/450, encode 284/450;
Phase D 292 / 292 is fused codebook instrumentation). Model-and-rules
find with rule encode and select is 0.82 (368). The same extract
without the second rule encode (`llm_select_only`) is 0.85 (382),
five below Hybrid. Cell 3 versus rules throughout: 99 vs 37
discordant, Δ+0.138, 95% CI 0.089 to 0.187, *p* = 1.0×10⁻⁷. Owner:
[five-cell grid](../../research/gan2026/gan_five_cell_grid_2026-08-22.md).
Per
[paper-story simplification](../decisions/paper-story-simplification.md),
Rules-only leaves the dissertation and supporting materials; the
rows stay valid as research history.

## C. The most difficult errors involve interpretation, not detection

Hybrid submitted 387/450 cited Purist-correct labels. Residual errors
were not spread evenly across frequency bands. Table 2 is the living
per-class reading for Hybrid; the LLM-only companion is Table 2c.
Gold and predicted ε only; no letter text and no row ids. Source:
[the `test450` class report](../../research/gan2026/gan_test450_classification_report_2026-08-28.md).
Hybrid class scores use the same 387/450 living replay as Table 1.

The harder bins are Unknown, Seizure free, and
sparse rare rates (less than once every 6 months, once every 6
months, and to a lesser extent once a month). Mid-to-high countable
rates are stronger. Daily (0.92) and more-than-weekly (0.91) are
among the best categories, well above Unknown (0.74). The LLM-only
executor tracks the mid-band rates closely; Seizure free and the
sparse six-month bins remain weaker than Hybrid. Seizure free is the
`currently_no_seizure` band (monthly frequency 0). It is not gold-kind
`no seizure frequency reference`, which scores as Unknown.

On Hybrid, 37 of 54 errors are incorrect `unknown` answers
(infrequent → unknown 16, frequent → unknown 13, seizure free →
unknown 8). The paper keeps one confusion figure (Pragmatic) and this
compact reading; the detailed residual taxonomy stays in supporting
material. Owner:
[gold → unknown](../../research/gan2026/gan_pragmatic_unknown_error_mode_2026-08-29.md),
[rate → unknown](../../research/gan2026/gan_pragmatic_infrequent_error_mode_2026-08-29.md).

Development case review explains the hard categories: competing
temporal readings, cluster structure, and uncertainty that cannot be
reduced safely to a rate. These examples illustrate mechanisms in
saved development traces. They do not estimate held-out prevalence,
clinical safety, or causal necessity.

**Table 2a (secondary; not a paper table).** Rules throughout.
Pre-promotion living `gan_rules` class reading at **321/450**; the
cited select stop is now **325/450** and has no new class report.
n=450; dropped=0. Classes follow the draft Purist labels, most
frequent to least frequent. Unknown support 76/450. Retained as
repository evidence only.

| Class | P | R | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| Daily | 0.63 | 0.63 | 0.63 | 41 |
| More than weekly, less than daily | 0.93 | 0.72 | 0.81 | 123 |
| Once a week | 0.83 | 1.00 | 0.91 | 5 |
| More than monthly, less than weekly | 0.80 | 0.81 | 0.80 | 58 |
| Once a month | 0.54 | 0.39 | 0.45 | 18 |
| More than 6 months, less than monthly | 0.80 | 0.80 | 0.80 | 55 |
| Once every 6 months | 0.50 | 1.00 | 0.67 | 1 |
| Less than once every 6 months | 1.00 | 0.67 | 0.80 | 6 |
| Unknown | 0.50 | 0.79 | 0.62 | 76 |
| Seizure free | 0.69 | 0.57 | 0.62 | 67 |
| micro-F1 | 0.71 | 0.71 | 0.71 | 450 |

Pragmatic companion: Frequent 0.86, Infrequent 0.75, Unknown 0.62,
Seizure free 0.62; micro-F1 0.76.

**Table 2b (paper Table 2).** Hybrid — Gemini codebook extract
(`gan_llm_extract`), then `gan_rules_encode` and rule decide. Replay
387/450 Purist. Same class order as Table 2a.

| Class | P | R | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| Daily | 0.90 | 0.93 | 0.92 | 41 |
| More than weekly, less than daily | 0.96 | 0.87 | 0.91 | 123 |
| Once a week | 1.00 | 0.80 | 0.89 | 5 |
| More than monthly, less than weekly | 0.88 | 0.91 | 0.90 | 58 |
| Once a month | 0.94 | 0.94 | 0.94 | 18 |
| More than 6 months, less than monthly | 0.89 | 0.75 | 0.81 | 55 |
| Once every 6 months | 0.00 | 0.00 | 0.00 | 1 |
| Less than once every 6 months | 0.75 | 0.50 | 0.60 | 6 |
| Unknown | 0.64 | 0.88 | 0.74 | 76 |
| Seizure free | 0.95 | 0.85 | 0.90 | 67 |
| micro-F1 | 0.86 | 0.86 | 0.86 | 450 |

Pragmatic companion: Frequent 0.95, Infrequent 0.82, Unknown 0.74,
Seizure free 0.90; micro-F1 0.88.

**Table 2c (companion; supporting material).** LLM-only — the same
Gemini extraction record with the living policy-example decide prompt
as the second call. Purist 383/450; two later-stage rows with no
scorable decide label count as incorrect. Same class order as Table 2a.

| Class | P | R | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| Daily | 0.93 | 0.93 | 0.93 | 41 |
| More than weekly, less than daily | 0.96 | 0.87 | 0.91 | 123 |
| Once a week | 1.00 | 1.00 | 1.00 | 5 |
| More than monthly, less than weekly | 0.91 | 0.88 | 0.89 | 58 |
| Once a month | 0.94 | 0.83 | 0.88 | 18 |
| More than 6 months, less than monthly | 0.93 | 0.71 | 0.80 | 55 |
| Once every 6 months | 0.00 | 0.00 | 0.00 | 1 |
| Less than once every 6 months | 1.00 | 0.67 | 0.80 | 6 |
| Unknown | 0.64 | 0.87 | 0.74 | 76 |
| Seizure free | 0.84 | 0.87 | 0.85 | 67 |
| micro-F1 | 0.85 | 0.85 | 0.85 | 450 |

Pragmatic companion: Frequent 0.94, Infrequent 0.83, Unknown 0.74,
Seizure free 0.85; micro-F1 0.87.

**Supporting material.** Keep the four-decimal class report, residual
taxonomy, and representative development cases. The main paper needs
the hard-bin finding, the Hybrid class table, and one confusion
figure. Rules-only class rows are repository history only.

## D. Secondary prompt and architecture experiments *(optional)*

The experiments in this section remain accessible for later reference but
are not part of the revised paper's prompt-mechanism evidence. They are tied
to the retired three-stage repair narrative, use a different scorer or
request, or test an architecture no longer presented. They must not extend
the main prompt-ablation claims.

### D1. Source-faithful find incurred a small select-stop cost

The source-form request (`gan_llm_extract_raw`) keeps the same event
schema and the same clinical policy as the cited codebook find. It
drops the closed allowed-label list and asks for letter wording or a
near-source phrase. Source-near encode is the selected-evidence renderer, not living
`gan_rules_encode`. That later stack recovers most of the form
(find 246 → encode 335 → select 357). Living codebook encode does
not rewrite letter wording and is not this row. The scores sit in
Table 3c. Do not retune Table 1.

### D2. A second LLM encode call on the codebook extract made the score worse

Cell 5 is not three Gemini calls. Find already writes the
codebook form. Cited select is `gan_llm_select_from_extract` on that
ledger. A separate later-stage stack was run anyway: the same
`gan_llm_extract` raw, then `gan_llm_encode`, then `gan_llm_select`.
That encode does not re-read the letter and does not see extract
`final_label`. It rewrites each event from `raw_value` and a quote.
The stack is an ablation. It is not cell 5 and not Table 1.

| Split | Extract | LLM encode | LLM select after encode |
| --- | ---: | ---: | ---: |
| Locked `test450` | 0.79 (354) | **0.65** (291) | 0.71 (320) |
| `dev750` | 0.78 (585) | **0.67** (506) | 0.76 (568) |

**Table 3a.** Gemini 3.7 Flash Purist micro-F1 for the later-stage
LLM encode-then-select ablation. Sources:
`paper_experiments/gan/gan_llm_extract/gemini37flash/{split}/comparison.json`,
`paper_experiments/gan/gan_llm_encode/gemini37flash/{split}/`,
`paper_experiments/gan/gan_llm_select/gemini37flash/{split}/`.
Holdout is aggregate-only. Cited cell 5 on `test450` is
**0.85** (383). Do not retune Table 1 from these cells.

Encode is the drop. Select recovers some of the lost letters but
stays below the extract stop on both sealed cells, and below cited
cell 5 on holdout. The development mechanism study on the same
codebook ledger scored encode **0.78 → 0.69** (89 harm, 21 rescue;
748 parsed letters) and both select paths at **0.79** (select after
encode 592; select from extract 590). That study is why the LLM row
skips the extra encode call. Owners:
[later-stage encode/select decision](../decisions/gan-later-stage-encode-select-prompts.md),
[encode on codebook extract](../../research/gan2026/gan_encode_on_codebook_extract_2026-08-22.md),
[select-from-extract](../../research/gan2026/gan_select_from_extract_2026-08-22.md).

This is not the five-cell historical selected-evidence encoder
(Gemini encode 346 / select 362). That remains a different ablation.
`gan_llm_encode` on `gan_llm_extract_raw` is also a different
question: it helps source-near wording and still does not beat the
bundled codebook find.

### D3. Retained extraction-prompt mechanism evidence

The revised paper retains exactly three focused ablations against the full
codebook extraction prompt. Each uses the shared extraction record and the
same cell-3 rule replay: find is the provisional-answer F1 and select is the
final-answer F1. The evidence variant removes the evidence fields and
exact-quote instruction as one bundled **evidence-obligation package**; it is
not a quote-only ablation. These comparisons do not claim that effects are
additive.

The table holds Gemini 3.7 Flash and temperature 0. It changes the
find request. The four codebook rows below stay living cell 3
(`gan_rules_encode`, then `llm_select_after_codebook`). The source-near and
Holgate rows are secondary and are reported separately below.

| Find request | Schema | Instructions | Labels | Examples | Evidence | Scorer |
| --- | --- | --- | --- | --- | --- | --- |
| Cited codebook | Events + selection | Full policy | Yes | Yes | Yes | Living parser |
| No examples | Same | Same | Yes | No | Yes | Living parser |
| Examples only | Same | Same | No | Yes | Yes | Living parser |
| No evidence | Same, no `evidence` keys | Same, no quote rule | Yes | Yes | No | Living parser |
| Source-near | Same | Same + informal form hint | No | No | Yes | Living parser |
| Holgate-like | Same | Holgate three-step | No | No | Yes | `holgate_dialect_v1` |
| Holgate one-label | No | Holgate three-step | No | No | No | `holgate_dialect_v1` |

What those rows isolate:

- **examples**, holding forms fixed (codebook vs no examples);
- **forms**, holding examples fixed (codebook vs examples only);
- **the evidence-obligation package**, holding the rest of the codebook fixed
  (codebook vs no evidence fields and exact-quote instruction);
- **written form** (codebook vs source-near);
- **schema plus evidence**, holding the Holgate ask fixed
  (Holgate-like vs Holgate one-label).

They do not isolate the instruction rewrite alone. That missing cell
would be the Holgate three-step ask plus the living `label_forms`
list. Source-near still leaks a few informal labels such as
`1 per day`.

Removing examples cost 10 letters at find and 17 at select. Dropping
the closed form list, while keeping the example strings, cost 8 at
find and 23 at select (387 → 364). Dropping the quote obligation
cost 10 at find and 17 at select (387 → 370), the same select total
as no-examples. Source-near find is 246; selected-evidence encode
raises that to 335, and rule select to 357. A Holgate-style
three-step ask with the event schema scores 277 / 288 / 292 on
`holgate_dialect_v1`. The same ask with one answer field, and no
schema or quote rule, scores 198 at find on that dialect map.
There is no ledger to encode or select. Owner:
[prompt-component ablation](../../research/gan2026/gan_extract_prompt_component_ablation_2026-08-30.md),
[round 2](../../research/gan2026/gan_extract_prompt_component_ablation_round2_2026-08-30.md),
[source-near vs bundled encode](../../research/paper/gan_source_near_vs_bundled_encode_2026-08-23.md).

| Find request | Provisional / find | Encode | Final / select |
| --- | ---: | ---: | ---: |
| Cited codebook (`gan_llm_extract`) | 0.789 (355) | 0.800 (360) | **0.860** (387) |
| Allowed forms, no examples | 0.767 (345) | 0.776 (349) | 0.822 (370) |
| Examples only, no forms | 0.771 (347) | 0.776 (349) | 0.809 (364) |
| Codebook, no evidence keys | 0.767 (345) | 0.771 (347) | 0.822 (370) |

**Table 3b.** Main-paper prompt mechanism comparison. The full codebook
prompt is compared with exactly three focused variants: no examples, no
closed allowed-label forms, and the bundled evidence-obligation package
ablation. The encode column exposes the shared replay; it is not a fourth
prompt ablation.

The following rows preserve secondary prompt experiments and their existing
evidence. Source-near uses a different written-form request and repair
stack. Holgate rows use `holgate_dialect_v1`, a different scorer and
request. They are not comparable to the main prompt mechanism table.

| Secondary find request | Provisional / find | Later encode | Final / select |
| --- | ---: | ---: | ---: |
| Source-near (`gan_llm_extract_raw`) | 0.547 (246) | 0.744 (335) | 0.793 (357) |
| Holgate-like three-step ask | 0.616 (277) | 0.640 (288) | 0.649 (292) |
| Holgate one-label | 0.440 (198) | — | — |

**Table 3c.** Secondary locked aggregate-only Gemini 3.7 Flash Purist
micro-F1 rows, n=450. Source-near encode/select are the promoted
`gan_llm_extract_raw` stages (selected-evidence encode, then `llm_select`).
Holgate rows use `holgate_dialect_v1`; the one-label row is find only.
These scorers and requests are not the same as the main prompt-mechanism
comparison. Do not retune Table 1 from these cells.

## E. Extra thinking budget did not beat the living Gemini setting

The inferential thinking contrast is living **low versus high** at
the cell-3 select stop, the same cited outcome as Table 1. High is
the predeclared extra-budget setting (the same 2× output cap as
medium). Medium stays a point estimate. Thinking changes only the
find call; encode and select stay recorded rules. The test is
whether extra reasoning beat the living select score, not whether
find moved.

On Gan `test450`, low remains the best select stop: 0.860 (387),
against 0.844 (380) at high. Paired
McNemar on low versus high is 21 vs 14 discordant letters
(Δ+0.016, 95% CI −0.010 to 0.041; *p* = 0.31). Extra budget did
not beat the living setting. The interval is also compatible with a
small loss or a small gain, so this is not a formal equivalence
claim. Medium thinking stays a point estimate on the prior stack.

Higher-effort settings increased computational cost and latency.
Once the model's role is fixed to find, the study does not
support spending additional reasoning budget on this pipeline.

## E2. Gemini temperature 0 versus 1 is smaller than stage ownership

Gemini living cell 3 uses temperature 0. Temperature 1 is an
unpromoted ablation on the same find, then codebook rule encode and
rule select.

| Split | Stop | Temp. 0 | Temp. 1 | Letters (1 − 0) |
| --- | --- | ---: | ---: | ---: |
| `test450` | Select | 0.860 (387) | 0.842 (379) | −8 |
| `dev750` | Select | 0.875 (656) | 0.875 (656) | 0 |

**Table 3.** Gemini 3.7 Flash Purist temperature ablation on the
living cell-3 stack. Temperature 0 select is the living codebook
replay (387/450), the same total as Table 1. Source:
[Gemini temperature 1](../../research/gan2026/gan_gemini37flash_temperature_1_2026-08-28.md)
and the living paired-test replay.

Holdout select was 0.860 at temperature 0 against 0.842 at
temperature 1 (Δ+0.018, 95% CI −0.006 to 0.042; *p* = 0.20).
Development select was 0.875 against 0.875 (Δ0.000, 95% CI −0.013
to 0.013; *p* = 1.00). Neither split distinguishes the two
temperatures. The five-cell stage allocation on the same holdout is
0.72 rules versus 0.86 cell 3. Temperature is relatively
inconsequential beside that pipeline. Temperature 0 remains the
living default.

## F. Rules reduced, but did not remove, differences between models

The six-model comparison holds the Hybrid stack fixed and changes
only the model making the extraction call: `gan_llm_extract` (model
already writes the gold form), then `gan_rules_encode` and
`llm_select_after_codebook`. The promoted roster on locked `test450`
is Table 4 (Purist stops; provisional answer, encode replay, final
answer) and Table 4b (the same final stop with the contract-adherence
metrics the paper reports as a compact table):

| Model | Provisional (find) | Encode | Final (select) |
| --- | ---: | ---: | ---: |
| Gemini 3.7 Flash | 0.789 (355) | 0.800 (360) | **0.860** (387) |
| Grok 4.6 | 0.789 (355) | 0.811 (365) | 0.853 (384) |
| GPT-5.6 Luna | 0.693 (312) | 0.738 (332) | 0.789 (355) |
| DeepSeek V4 Flash | 0.742 (334) | 0.758 (341) | 0.820 (369) |
| Qwen 3.8 27B | 0.700 (315) | 0.731 (329) | 0.762 (343) |
| Gemma 4 26B | 0.664 (299) | 0.682 (307) | 0.724 (326) |

**Table 4.** Locked aggregate-only Gan cell-3 roster, Purist
micro-F1, from `paper_experiments/gan/rungs/{slug}/test450/` on
promoted `gan_llm_extract`. Encode is `gan_rules_encode`; select is
`llm_select_after_codebook`. Grok living temperature is 0. Gemini
select here is the living codebook replay (387/450), the same
total as Table 1. Historical selected-evidence encode (346 / 362
on Gemini) remains the five-cell encode ablation, not this table.

| Model | Purist | Pragmatic | Exact evidence | Schema repair | Unparsed | Retry rejected | Events |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Gemini 3.7 Flash | **0.860** (387) | 0.880 (396) | 99.8% (449) | 0% (0) | 1 | 0 | 985 |
| Grok 4.6 | 0.853 (384) | **0.889** (400) | 100% (450) | 0% (0) | 0 | 0 | 1063 |
| GPT-5.6 Luna | 0.789 (355) | 0.820 (369) | 98.9% (445) | 0% (0) | 1 | 0 | 1102 |
| DeepSeek V4 Flash | 0.820 (369) | 0.849 (382) | 99.6% (448) | 0.4% (2) | 0 | 0 | 1267 |
| Qwen 3.8 27B | 0.762 (343) | 0.807 (363) | 96.7% (435) | 0.7% (3) | 2 | 0 | 1004 |
| Gemma 4 26B | 0.724 (326) | 0.773 (348) | 92.9% (418) | 3.3% (15) | 8 | 7 | 1068 |

**Table 4b.** Same locked cell-3 select stop as Table 4. Purist
and Pragmatic are `llm_select` in the rung files. Exact evidence
is `evidence_valid`: the saved find-stage selected quote is an
exact letter substring (count and percent of 450). Schema repair is
`json_dialect_repairs` (non-semantic JSON dialect; count and
percent of 450). Unparsed is
`parse_or_validation_failures` after that repair. Retry rejected
is `format_retries_rejected`. Events is
`predicted_candidate_count` on the select ledger. Call failures,
applied format retries, and other `repair_notes` are 0 on all
six. Gemini Purist 387 and Pragmatic 396 match Table 1 cell 3.
Sources: `paper_experiments/gan/rungs/{slug}/test450/comparison.json`
and
`paper_experiments/gan/gan_llm_extract/{slug}/test450/comparison.json`.

Rule decide raised every model over its provisional answer and
helped Luna most (+43 Purist; +33 Pragmatic), but did not bring Luna
or the local models level with Gemini or Grok. On Purist, Gemini
final is highest (387). On Pragmatic, Grok is four letters above
Gemini (400 vs 396). Exact evidence and parse form track the
same split: Grok is exact on all 450 quotes; Gemma leaves the
most unparsed letters and the weakest exact-evidence count
(92.9%, 418). A valid span is not semantic support. Rules can
correct task-form and selection errors in an existing candidate
record. They cannot reconstruct a clinically relevant distinction
omitted at extract.

Paper claim boundary for the two local models (Qwen, Gemma): the
result shows that the design can execute
on a single laptop GPU under the same synthetic task conditions, not
real-letter performance, clinical
validity, workflow fit, privacy compliance, or deployment readiness
([paper-story simplification](../decisions/paper-story-simplification.md),
Decision 6).

**Figure 1.** Six-model Hybrid comparison, provisional answer and
final answer, on Gan `test450`. The caption states the split, Purist
micro-F1, and configuration.

## G. The same letters support a broader clinical inventory, descriptively (supporting material)

Per
[paper-story simplification](../decisions/paper-story-simplification.md),
this panel is descriptive only and sits in the supporting materials,
not the main paper. The Gan gold is one current seizure-frequency
state. The same synthetic letters also mention diagnoses, medicines,
investigations, and multiple seizure-frequency statements. A frozen
ExECT-style four-family inventory program (`run_letter` /
`ACCEPTED_THREE_STAGE_CONFIG`) was applied to a prespecified sample of
100 `dev750` letters. The pipeline was not tuned after the sample was
drawn. No inventory gold exists on Gan, so the study reports only
what the schema emitted.

| Family | Letters with ≥1 fact | Total facts | Median (range) per letter | Common subtypes |
| --- | ---: | ---: | --- | --- |
| Diagnosis | 76 | 130 | 1 (0–4) | Epilepsy (130) |
| Prescription | 81 | 204 | 2 (0–9) | levetiracetam, lamotrigine, sodium-valproate, clobazam, topiramate |
| Investigations | 40 | 68 | 0 (0–3) | MRI:Normal, EEG:Abnormal, EEG:Normal, MRI:Abnormal |
| SeizureFrequency | 50 | 81 | 0.5 (0–4) | seizures, seizure, Increased, Infrequent, Frequent |
| Any family | 97 | 483 | 5 (0–11) | — |

**Table 5.** Descriptive inventory output on 100 Gan `dev750`
synthetic letters. Source:
`experiments/gan_inventory_feasibility_dev750_n100_20260828/summary.json`.
Diagnosis subtypes use the schema’s `DiagCategory`, which is almost
always `Epilepsy` on this program.

Three synthetic examples were chosen by a predeclared rule (most
families, then fact count, then lowest source-row index), not by
post-hoc clinical interest.

**2748.** Focal epilepsy with impaired-awareness seizures; MRI
unremarkable; left-temporal EEG sharp waves; levetiracetam and
lacosamide. Extracted inventory: focal epilepsy and focal seizure;
levetiracetam and lacosamide (each repeated from a later mention of
the same regimen); MRI:Normal and EEG:Abnormal; Decreased, one focal
seizure per month, and Increased.

**5551.** Combined generalised and focal epilepsy; levetiracetam and
clobazam rescue; normal MRI; EEG with generalised and focal
discharges. Extracted inventory: epilepsy, focal epilepsy, focal
seizures, and generalised seizures; levetiracetam and clobazam (each
repeated); MRI:Normal and EEG:Abnormal; Infrequent clonic seizures.

**2759.** Recurrent seizures of uncertain classification; historical
normal imaging and EEG; lamotrigine split dosing. Extracted
inventory: secondary generalisation; four lamotrigine mentions from
one split-dose sentence; EEG:Normal, MRI:Normal, and EEG:Normal; one
simple partial seizure per month and a daily `seizures` mention.

The examples show multi-fact inventories and also repeated or coarse
mentions. That is part of the descriptive result. These counts are
not precision, recall, accuracy, or clinical validity. They show that
the letters contain a broader structured record than the evaluated
frequency label, and they motivate later expert annotation on real
correspondence.

## Visual and supporting-material plan

The main Results section (`paper/draft/FES.tex`) contains: the
bounded previous-benchmark comparison (Table IV in the draft), the
Hybrid Purist and Pragmatic class table (Table V; this file's Table
2b), the two-executor provisional/final table (Table VI; this file's
Table 1), the three extraction-prompt ablations (Table VII; this
file's Table 3b), the six-model figure plus the compact
scores-and-adherence table (Table VIII; this file's Table 4b), the
temperature and thinking result (section E / E2), a compact error
analysis with one Pragmatic confusion figure, and a short
experimental-environment table. The paired executor test is one
sentence after Table VI.

Supporting material holds: the interface contract and full prompts
and schemas, the event categories and label forms, the secondary
prompt rows (Table 3c), the secondary LLM decompositions (Table 3a,
the one-call ablation, verification and section-splitting development
findings, the July sampling study), the Hybrid stack variants (cells
2 and 4), the six-model adherence table with retry and event counts
(Table 4b), the development-vs-test figure for the two executors,
the LLM-only class table (Table 2c), the descriptive inventory panel
(section G), the residual taxonomy, hardware and API settings, and
the directional evidence protocol summary. The cited extraction
request is
[`gan_llm_extract_prompt_template.json`](../../../paper/supporting%20materials/gan_llm_extract_prompt_template.json).
Rules-only rows (Table 2a and the five-cell rules row) are
repository history only. ExECT locked totals are later-paper
evidence, not dissertation tables.

## Claim boundary

Held-out Gan results are aggregate-only. The paired tests
report discordant counts only. Gemini temperature also uses
`dev750` select flags. Development examples explain
mechanisms and limitations but do not establish prevalence or
clinical safety. The later-stage LLM encode-then-select stack is an
optional ablation, not a Table 1 row. The classification study evaluates agreement with
the Gan seizure-frequency reference standard. The inventory panel is
descriptive output on `dev750` only. This draft does not claim
clinical validation, deployment readiness, a universal architecture,
visibility into model-internal reasoning, or ExECT benchmark
performance.
