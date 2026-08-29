# Paper results

Date: 2026-08-24
Revised: 2026-08-29 (`last_event_well_since` promoted on living cell-3
select; six-model rungs and Table 1 refreshed)
Status: structured first draft; ExECT columns removed from the dissertation
Owner: this file
Scope: [Gan is the dissertation paper](../decisions/gan-is-the-dissertation-paper.md)
Feasibility: [100-letter descriptive study](../../research/gan2026/gan_inventory_feasibility_dev750_n100_2026-08-28.md)

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

## B. Model-led find with rule-based later stages gave the strongest result

On locked `test450`, the five-cell comparison found that Gemini
codebook find, then a second rule encode, then rule selection
was the strongest allocation, outperforming both standalone rules and
the end-to-end model configuration (Table 1).

| Find | Encode | Select | Purist | Pragmatic |
| --- | --- | --- | ---: | ---: |
| Rules | Rules | Rules | 0.72 (325) | 0.77 (345) |
| Model and rules | Rules | Rules | 0.82 (368) | 0.84 (380) |
| Model | Model + Rules | Rules | **0.86** (387) | **0.88** (396) |
| Model | Model | Rules | 0.85 (382) | 0.87 (391) |
| Model | Model | Model | 0.79 (357) | 0.82 (369) |

**Table 1.** Locked aggregate-only Gan five-cell comparison using
Gemini 3.7 Flash. The cited score is the select stop. Source:
`paper_experiments/gan/five_cell_grid/gemini37flash/test450/comparison.json`
and
[the `test450` class report](../../research/gan2026/gan_test450_classification_report_2026-08-28.md).
Cell 3 find is `gan_llm_extract`, which already writes the
codebook form. Encode then runs `gan_rules_encode` on that ledger, so
both the model and the rules encode. That is not cell 2 (both at
find) and not cell 4 (same extract, no rule encode). Table 1 cell 3
is the living no-call replay of that extract through
`llm_select_after_codebook`, including `last_event_well_since`
(387/450 Purist, 396/450 Pragmatic). Cell 4 is the same extract
through `llm_select_only` (382/450 Purist).

Replacing rule-based find with Gemini raised Purist
micro-F1 from 0.72 to 0.86 when the model already wrote the codebook
form and rules then encoded and selected. Dropping the second rule
encode (cell 4) or assigning selection to the model (cell 5) reduced
the final score. Rules Purist 325/450 and Pragmatic 345/450 are the
promoted three-stage select stops.

Paired exact McNemar tests use that same cell-3 vector
(**387**/450). On those letters cell 3 beats standalone rules
(325; 99 vs 37 discordant; Δ+0.138, 95% CI 0.089 to 0.187;
*p* = 1.0×10⁻⁷) and beats cell 5 (357; 40 vs 10; Δ+0.067,
95% CI 0.037 to 0.097; *p* = 2.4×10⁻⁵). Owner:
[paired `test450` tests](../../research/gan2026/gan_paired_significance_test450_2026-08-29.md).

## C. The most difficult errors involve interpretation, not detection

The preferred cell submitted 387/450 cited Purist-correct labels.
Residual errors were not spread evenly across frequency bands. Tables
2a–2c are the living per-class reading for cells 1 (rules throughout),
3 (model codebook find, model-then-rule encode, rule select),
and 5 (model throughout).
Gold and predicted ε only; no letter text and no row ids. Source:
[the `test450` class report](../../research/gan2026/gan_test450_classification_report_2026-08-28.md).
Cell 3 class scores use the same 387/450 living replay as Table 1.

The harder bins are Unknown, Seizure free, and
sparse rare rates (less than once every 6 months, once every 6
months, and to a lesser extent once a month). Mid-to-high countable
rates are stronger. Cell 3 raises Daily and Unknown F1 relative to
standalone rules, and keeps more-than-weekly F1 high. The all-model
cell keeps Daily F1 but loses mid-band recall. Seizure free is the
`currently_no_seizure` band (monthly frequency 0). It is not gold-kind
`no seizure frequency reference`, which scores as Unknown.

Development case review explains the hard categories: competing
temporal readings, cluster structure, and uncertainty that cannot be
reduced safely to a rate. These examples illustrate mechanisms in
saved development traces. They do not estimate held-out prevalence,
clinical safety, or causal necessity.

**Table 2a.** Cell 1 — rules / rules / rules. Pre-promotion living
`gan_rules` class reading at **321/450**; the cited select stop is now
**325/450** and has no new class report. n=450; dropped=0. Classes
follow the draft Purist labels, most frequent to least frequent.
Unknown support 76/450.

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

**Table 2b.** Cell 3 — Gemini codebook find (`gan_llm_extract`
already encodes), then `gan_rules_encode` and rule select. Replay
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

**Table 2c.** Cell 5 — Gemini find, encode, and select. Purist
357/450; two later-stage rows with no scorable select label count as
incorrect. Same class order as Table 2a.

| Class | P | R | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| Daily | 0.90 | 0.93 | 0.92 | 41 |
| More than weekly, less than daily | 0.94 | 0.85 | 0.89 | 123 |
| Once a week | 1.00 | 0.60 | 0.75 | 5 |
| More than monthly, less than weekly | 0.89 | 0.69 | 0.78 | 58 |
| Once a month | 0.64 | 0.50 | 0.56 | 18 |
| More than 6 months, less than monthly | 0.94 | 0.62 | 0.75 | 55 |
| Once every 6 months | 0.00 | 0.00 | 0.00 | 1 |
| Less than once every 6 months | 1.00 | 0.67 | 0.80 | 6 |
| Unknown | 0.61 | 0.91 | 0.73 | 76 |
| Seizure free | 0.69 | 0.84 | 0.76 | 67 |
| micro-F1 | 0.79 | 0.79 | 0.79 | 450 |

Pragmatic companion: Frequent 0.92, Infrequent 0.71, Unknown 0.73,
Seizure free 0.76; micro-F1 0.82.

**Supporting material.** Keep the four-decimal class report, residual
taxonomy, and representative development cases. The main paper needs
the hard-bin finding and the three-cell class tables.

## D. Source-faithful find incurred a small performance cost *(optional)*

The Gan source-form ablation held the multi-candidate output schema
constant and changed only the form written by the model: the headline
request emitted gold-aligned encoded candidates, whereas the
source-near request retained the wording and uncertainty of the
letter. Later rule encoding and selection recovered much of the
source-near deficit, but the bundled find-and-encode request
retained the better final score.

This is a choice between task performance and source fidelity, rather
than a comparison of rich versus flattened schemas. For example, a
source-near candidate can retain a bound such as “up to four per day”;
later rules may map it to the permitted `4 per day` label, but not
every source-form distinction is recovered without loss. **[If
retained, add the compact four-row Gan ablation table from
`gan_source_near_vs_bundled_encode_2026-08-23.md`; otherwise move this
subsection to supporting material.]**

## D2. A second LLM encode call on the codebook extract made the score worse *(optional)*

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
Holdout is aggregate-only. Cited cell 5 on `test450` remains
**0.79** (357). Do not retune Table 1 from these cells.

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

The six-model comparison holds the same cell-3 stack and changes only
the find-stage model: `gan_llm_extract` (model already
encodes), then `gan_rules_encode` and `llm_select_after_codebook`.
The promoted roster on locked `test450` is:

| Model | Find | Encode | Select |
| --- | ---: | ---: | ---: |
| Gemini 3.7 Flash | 0.789 (355) | 0.800 (360) | **0.860** (387) |
| Grok 4.6 | 0.789 (355) | 0.811 (365) | 0.853 (384) |
| GPT-5.6 Luna | 0.693 (312) | 0.738 (332) | 0.789 (355) |
| DeepSeek V4 Flash | 0.742 (334) | 0.758 (341) | 0.820 (369) |
| Qwen 3.8 27B | 0.700 (315) | 0.731 (329) | 0.762 (343) |
| Gemma 4 26B | 0.664 (299) | 0.682 (307) | 0.724 (326) |

**Table 4.** Locked aggregate-only Gan cell-3 roster from
`paper_experiments/gan/rungs/{slug}/test450/` on promoted
`gan_llm_extract`. Encode is `gan_rules_encode`; select is
`llm_select_after_codebook`. Grok living temperature is 0. Gemini
select here is the living codebook replay (387/450), the same
total as Table 1. Historical selected-evidence encode (346 / 362
on Gemini) remains the five-cell encode ablation, not this table.

Later rules raised every model over its find stop and helped
Luna most (+43 letters), but did not bring Luna or the local
models level with Gemini or Grok.
Rules can correct task-form and selection errors in an existing
candidate record. They cannot reconstruct a clinically relevant
distinction omitted at find.

**Figure 1.** Hosted cell-3 comparison before and after later
rule-based processing on Gan `test450`. The caption should state the
split, Purist micro-F1, and configuration.

## G. The same letters support a broader clinical inventory, descriptively

The Gan gold is one current seizure-frequency state. The same
synthetic letters also mention diagnoses, medicines, investigations,
and multiple seizure-frequency statements. A frozen ExECT-style
four-family inventory program (`run_letter` /
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

The main Results section contains Table 1 (Gan five-cell), Tables
2a–2c (Purist class reports for cells 1, 3, and 5), Table 3
(Gemini temperature ablation), Table 3a (optional later-stage LLM
encode-then-select), Table 4 (six-model cell-3 roster), Table 5
(descriptive inventory), and Figure 1 (before-and-after-rules).
The paired tests sit in supporting material with a one-line
reading after Tables 1 and 3. Full
four-decimal class tables, residual taxonomy, representative
development traces, source-form ablation detail, later-stage LLM
encode mechanism, hardware
specifications, prompts, API settings, and replay artifacts belong in
supporting material unless the final page budget permits more of
them. ExECT locked totals are later-paper evidence. They are not
dissertation tables.

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
