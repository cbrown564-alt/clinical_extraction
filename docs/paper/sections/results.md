# Paper results

Date: 2026-08-24
Revised: 2026-08-28 (Gan-only dissertation scope; living class tables; roster counts)
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

## B. Model-led recognition with rule-based later stages gave the strongest result

On locked `test450`, the five-cell comparison found that Gemini
codebook recognition, then a second rule encode, then rule selection
was the strongest allocation, outperforming both standalone rules and
the end-to-end model configuration (Table 1).

| Candidate recognition | Task encoding | Final selection | Purist | Pragmatic |
| --- | --- | --- | ---: | ---: |
| Rules | Rules | Rules | 0.71 (321) | 0.76 (341) |
| Model and rules | Rules | Rules | 0.82 (368) | 0.84 (380) |
| Model | Model + Rules | Rules | **0.83** (373) | **0.85** (382) |
| Model | Model | Rules | 0.82 (368) | 0.84 (377) |
| Model | Model | Model | 0.79 (357) | 0.82 (369) |

**Table 1.** Locked aggregate-only Gan five-cell comparison using
Gemini 3.7 Flash. The cited score is the select stop. Source:
`paper_experiments/gan/five_cell_grid/gemini37flash/test450/comparison.json`
and
[the `test450` class report](../../research/gan2026/gan_test450_classification_report_2026-08-28.md).
Cell 3 recognise is `gan_llm_extract`, which already writes the
codebook form. Encode then runs `gan_rules_encode` on that ledger, so
both the model and the rules encode. That is not cell 2 (both at
recognise) and not cell 4 (same extract, no rule encode). A later
no-call replay of the same cell-3 extract scores 374/450 Purist and
383/450 Pragmatic. The cited five-cell totals remain 373 and 382. Do
not retune from the one-count gap.

Replacing rule-based candidate recognition with Gemini raised Purist
micro-F1 from 0.71 to 0.83 when the model already wrote the codebook
form and rules then encoded and selected. Dropping the second rule
encode (cell 4) or assigning selection to the model (cell 5) reduced
the final score.

## C. The most difficult errors involve interpretation, not detection

The preferred cell submitted 373/450 cited Purist-correct labels.
Residual errors were not spread evenly across frequency bands. Tables
2a–2c are the living per-class reading for cells 1 (rules throughout),
3 (model codebook recognise, model-then-rule encode, rule select),
and 5 (model throughout).
Gold and predicted ε only; no letter text and no row ids. Source:
[the `test450` class report](../../research/gan2026/gan_test450_classification_report_2026-08-28.md).
Cell 3 class scores use the later 374/450 replay. Cite Table 1’s
373/450 for the five-cell total.

The harder bins are Unknown, No seizure frequency reference, and
sparse rare rates (less than once every 6 months, once every 6
months, and to a lesser extent once a month). Mid-to-high countable
rates are stronger. Cell 3 raises Daily and Unknown F1 relative to
standalone rules, and keeps more-than-weekly F1 high. The all-model
cell keeps Daily F1 but loses mid-band recall.

Development case review explains the hard categories: competing
temporal readings, cluster structure, and uncertainty that cannot be
reduced safely to a rate. These examples illustrate mechanisms in
saved development traces. They do not estimate held-out prevalence,
clinical safety, or causal necessity.

**Table 2a.** Cell 1 — rules / rules / rules. Living `gan_rules`;
n=450; dropped=0. Classes follow the draft Purist labels, most
frequent to least frequent. Unknown support 76/450.

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
| No seizure frequency reference | 0.69 | 0.57 | 0.62 | 67 |
| micro-F1 | 0.71 | 0.71 | 0.71 | 450 |

Pragmatic companion: Frequent 0.86, Infrequent 0.75, Unknown 0.62, No
seizure 0.62; micro-F1 0.76.

**Table 2b.** Cell 3 — Gemini codebook recognise (`gan_llm_extract`
already encodes), then `gan_rules_encode` and rule select. Replay
374/450 Purist (cited five-cell 373/450). Same class order as Table
2a.

| Class | P | R | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| Daily | 0.90 | 0.93 | 0.92 | 41 |
| More than weekly, less than daily | 0.96 | 0.87 | 0.91 | 123 |
| Once a week | 1.00 | 0.60 | 0.75 | 5 |
| More than monthly, less than weekly | 0.88 | 0.91 | 0.90 | 58 |
| Once a month | 0.92 | 0.61 | 0.73 | 18 |
| More than 6 months, less than monthly | 0.88 | 0.64 | 0.74 | 55 |
| Once every 6 months | 0.00 | 0.00 | 0.00 | 1 |
| Less than once every 6 months | 0.75 | 0.50 | 0.60 | 6 |
| Unknown | 0.64 | 0.88 | 0.74 | 76 |
| No seizure frequency reference | 0.78 | 0.85 | 0.81 | 67 |
| micro-F1 | 0.83 | 0.83 | 0.83 | 450 |

Pragmatic companion: Frequent 0.95, Infrequent 0.72, Unknown 0.74, No
seizure 0.81; micro-F1 0.85.

**Table 2c.** Cell 5 — Gemini recognise, encode, and select. Purist
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
| No seizure frequency reference | 0.69 | 0.84 | 0.76 | 67 |
| micro-F1 | 0.79 | 0.79 | 0.79 | 450 |

Pragmatic companion: Frequent 0.92, Infrequent 0.71, Unknown 0.73, No
seizure 0.76; micro-F1 0.82.

**Supporting material.** Keep the four-decimal class report, residual
taxonomy, and representative development cases. The main paper needs
the hard-bin finding and the three-cell class tables.

## D. Source-faithful recognition incurred a small performance cost *(optional)*

The Gan source-form ablation held the multi-candidate output schema
constant and changed only the form written by the model: the headline
request emitted gold-aligned encoded candidates, whereas the
source-near request retained the wording and uncertainty of the
letter. Later rule encoding and selection recovered much of the
source-near deficit, but the bundled recognise-and-encode request
retained the better final score.

This is a choice between task performance and source fidelity, rather
than a comparison of rich versus flattened schemas. For example, a
source-near candidate can retain a bound such as “up to four per day”;
later rules may map it to the permitted `4 per day` label, but not
every source-form distinction is recovered without loss. **[If
retained, add the compact four-row Gan ablation table from
`gan_source_near_vs_bundled_encode_2026-08-23.md`; otherwise move this
subsection to supporting material.]**

## E. More reasoning effort did not materially improve the preferred pipeline

Across the tested effort levels, increasing Gemini's reasoning budget
produced little or no improvement in the model-recognise, rule-encode,
rule-select pipeline. On Gan, low effort achieved the best final
Purist result (0.831), compared with 0.813 at medium effort and 0.818
at high effort.

Higher-effort settings increased computational cost and latency
without a corresponding improvement in the primary task metric. Once
the model's role is fixed to candidate recognition, the study does not
support spending additional reasoning budget on this pipeline.

## E2. Temperature 0 versus 1 is mixed and smaller than stage ownership

Gemini and Grok were compared at temperature 0 and 1 on the same
cell-3 recognise, then codebook rule encode and rule select. Gemini
living is 0; temperature 1 is an unpromoted ablation. Grok living is
now 0; temperature 1 is the earlier cited Grok cell. Luna remains at
1 because that provider rejects 0.

| Model | Split | Stop | Temp. 0 | Temp. 1 | Letters (1 − 0) |
| --- | --- | --- | ---: | ---: | ---: |
| Gemini 3.7 Flash | `test450` | Select | 0.831 (374) | 0.824 (371) | −3 |
| Gemini 3.7 Flash | `dev750` | Select | 0.865 (649) | 0.867 (650) | +1 |
| Grok 4.6 | `test450` | Select | 0.838 (377) | 0.842 (379) | +2 |

**Table 3.** Gan Purist temperature ablation on the living cell-3
stack (`gan_llm_extract`, then `gan_rules_encode`, then
`llm_select_after_codebook`). Gemini temperature 0 select is the
living codebook replay (374/450). Table 1 still cites 373/450.
Grok `dev750` temperature 1 is omitted: those codebook extract raws
were overwritten. Sources:
[Grok temperature 0](../../research/gan2026/gan_grok46_temperature_0_2026-08-28.md),
[Gemini temperature 1](../../research/gan2026/gan_gemini37flash_temperature_1_2026-08-28.md).

The signs reverse by model. Holdout select prefers Gemini at 0 and
Grok at 1 by two or three letters. Development is flat for Gemini.
The holdout band is smaller than thinking’s 8. The five-cell stage
allocation on the same Gemini holdout is 0.71 rules versus 0.83
cell 3 (54 letters). Temperature is relatively inconsequential
beside that three-stage pipeline. Temperature 0 is the appropriate
living default for every model that accepts it. Luna was not
measured at 0; the mixed Gemini and Grok results do not predict
that Luna would rise or fall if the same setting were allowed.

## F. Rules reduced, but did not remove, differences between models

The six-model comparison holds the same cell-3 stack and changes only
the candidate-recognition model: `gan_llm_extract` (model already
encodes), then `gan_rules_encode` and `llm_select_after_codebook`.
The promoted roster on locked `test450` is:

| Model | Recognise | Encode | Select |
| --- | ---: | ---: | ---: |
| Gemini 3.7 Flash | 0.789 (355) | 0.800 (360) | 0.831 (374) |
| Grok 4.6 | 0.789 (355) | 0.811 (365) | **0.838** (377) |
| GPT-5.6 Luna | 0.693 (312) | 0.738 (332) | 0.778 (350) |
| DeepSeek V4 Flash | 0.742 (334) | 0.758 (341) | 0.796 (358) |
| Qwen 3.8 27B | 0.700 (315) | 0.731 (329) | 0.753 (339) |
| Gemma 4 26B | 0.664 (299) | 0.682 (307) | 0.718 (323) |

**Table 4.** Locked aggregate-only Gan cell-3 roster from
`paper_experiments/gan/rungs/{slug}/test450/` on promoted
`gan_llm_extract`. Encode is `gan_rules_encode`; select is
`llm_select_after_codebook`. Grok living temperature is 0. Gemini
select here is the living codebook replay (374/450). Table 1 cites
the curated five-cell total **0.83** (373/450); do not retune from
the one-count gap. Historical selected-evidence encode (346 / 362
on Gemini) remains the five-cell encode ablation, not this table.

Later rules raised every model over its recognise stop and helped
Luna most, but did not bring Luna or the local models level with Grok.
Rules can correct task-form and selection errors in an existing
candidate record. They cannot reconstruct a clinically relevant
distinction omitted at recognition.

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
(temperature ablation), Table 4 (six-model cell-3 roster), Table 5
(descriptive inventory), and Figure 1 (before-and-after-rules). Full
four-decimal class tables, residual taxonomy, representative
development traces, source-form ablation detail, hardware
specifications, prompts, API settings, and replay artifacts belong in
supporting material unless the final page budget permits more of
them. ExECT locked totals are later-paper evidence. They are not
dissertation tables.

## Claim boundary

Held-out Gan results are aggregate-only. Development examples explain
mechanisms and limitations but do not establish prevalence or
clinical safety. The classification study evaluates agreement with
the Gan seizure-frequency reference standard. The inventory panel is
descriptive output on `dev750` only. This draft does not claim
clinical validation, deployment readiness, a universal architecture,
visibility into model-internal reasoning, or ExECT benchmark
performance.
