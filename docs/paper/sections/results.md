# Paper results

Date: 2026-08-24  
Status: structured first draft; final prose and visual values to be completed  
Owner: this file

## A. Experimental environment and evaluation

The experiments were run from two documented environments: hosted model calls
were primarily submitted from the Mac mini development machine, while local
Qwen and Gemma runs used Ollama on a Dell XPS 15 with an 8 GB NVIDIA GPU. The
supporting material records the machine specifications, operating systems,
software versions, model routes, API settings, and local-runtime settings
needed to reproduce each reported condition. **[Complete the Dell hardware and
driver fields from `docs/paper/experiment_environment.md` before submission.]**

Primary performance was evaluated against each task's intended output: Purist
accuracy tested whether the final Gan label represented the required current
seizure-frequency state, while four-family micro F1 measured whether the ExECT
pipeline recovered the complete inventory of supported diagnoses,
seizure-frequency facts, prescriptions, and investigations without adding
unsupported facts.

Because the primary measures capture different error structures—fine-grained
frequency-band and sentinel errors in Gan, versus missed and unsupported facts
in ExECT—Pragmatic accuracy for Gan and precision and recall for ExECT are
reported as complementary measures to show how each configuration's errors are
distributed. Scores are reported separately and are not pooled across tasks.

## B. Model-led recognition with rule-based later stages gave the strongest result

Across both held-out tasks, the five-cell comparison found that Gemini
candidate recognition followed by rule-based encoding and selection was the
best-performing allocation, outperforming both standalone rules and the
end-to-end model configuration (Table 1).

| Candidate recognition | Task encoding | Final selection | Gan `test450` Purist accuracy | ExECT `test60` four-family micro F1 |
| --- | --- | --- | ---: | ---: |
| Rules | Rules | Rules | 0.73 | 0.77 |
| Model and rules | Rules | Rules | 0.82 | 0.86 |
| Model | Rules | Rules | **0.83** | **0.87** |
| Model | Model | Rules | 0.82 | 0.86 |
| Model | Model | Model | 0.79 | 0.85 |

**Table 1.** Locked aggregate-only five-cell comparison using Gemini 3.7
Flash. The cited score is the output after final selection. Gan and ExECT use
different metrics and are displayed side by side rather than combined.

On Gan, replacing rule-based candidate recognition with Gemini raised Purist
accuracy from 0.73 to 0.83 when encoding and selection remained rule based,
while assigning those later stages to the model reduced the final score to
0.79.

On ExECT, the same allocation achieved the highest four-family micro F1 of
0.87, compared with 0.77 for rules throughout and 0.85 for the end-to-end
model configuration; adding a later model encoding step did not improve this
result.

## C. The most difficult errors involve interpretation, not detection

The remaining performance limitation was concentrated in clinically meaningful
subgroups rather than evenly distributed across the task outputs. On the
aggregate-only ExECT holdout, the preferred configuration was strongest on
Prescription and Investigations and weaker on Diagnosis and SeizureFrequency
(family F1 0.95, 0.91, 0.81, and 0.81 respectively). The Gan preferred cell
achieved 373/450 Purist-correct labels. The available historical category-cut
artifacts inform the development cases below, but are not relabelled as a
current-Gemini preferred-cell subgroup result.

Development case review explains the hard categories: Gan failures include
competing temporal readings, cluster structure, and uncertainty that cannot be
reduced safely to a rate; ExECT failures include retaining the correct
diagnosis and linking a seizure-frequency statement to the correct condition.
These examples illustrate mechanisms in the saved traces; they do not estimate
held-out prevalence, clinical safety, or causal necessity.

**Supporting material.** Include the detailed subgroup tables, residual-error
taxonomy, and representative development cases. The main paper should retain
only the subgroup finding needed to explain the headline scores.

## D. Source-faithful recognition incurred a small performance cost *(optional)*

The Gan source-form ablation held the multi-candidate output schema constant
and changed only the form written by the model: the headline request emitted
gold-aligned encoded candidates, whereas the source-near request retained the
wording and uncertainty of the letter. Later rule encoding and selection
recovered much of the source-near deficit, but the bundled recognise-and-encode
request retained the better final score.

This is a choice between task performance and source fidelity, rather than a
comparison of rich versus flattened schemas. For example, a source-near
candidate can retain a bound such as “up to four per day”; later rules may map
it to the permitted `4 per day` label, but not every source-form distinction is
recovered without loss. **[If retained, add the compact four-row Gan ablation
table from `gan_source_near_vs_bundled_encode_2026-08-23.md`; otherwise move
this subsection to supporting material.]**

## E. More reasoning effort did not materially improve the preferred pipeline

Across the tested effort levels, increasing Gemini's reasoning budget produced
little or no improvement in the model-recognise, rule-encode, rule-select
pipeline. On Gan, low effort achieved the best final Purist result (0.831),
compared with 0.813 at medium effort and 0.818 at high effort. The ExECT
thinking comparison is reported as a clearly labelled secondary
Compact/headline analysis rather than substituted for the cited four-family
five-cell result; its final-score spread was 0.007 across low, medium, and
high effort.

Higher-effort settings increased computational cost and latency without a
corresponding improvement in the primary task metrics. The practical finding
is therefore bounded: once the model's role is fixed to candidate recognition,
the study does not support spending additional reasoning budget on this
pipeline.

## F. Rules reduced, but did not remove, differences between models

The six-model cell-3 comparison assesses whether the preferred allocation is
stable when only the candidate-recognition model changes. It should report the
performance pattern across the completed roster without treating Gemini as the
object of the comparison: stronger models are expected to form a close group,
while weaker models provide a more demanding test of the later rule stages.
**[Insert completed Qwen and Gemma rows before finalising.]**

Later rule-based encoding and selection narrowed, but did not remove,
performance differences between models: rules can correct task-form and
selection errors in an existing candidate record, but cannot reconstruct a
clinically relevant distinction omitted or collapsed at recognition. This
provides the deployment trade-off relevant to local open-source models: later
rules may compensate for some weaker extraction, but model capability remains
material.

**Figure 1.** Six-model cell-3 comparison before and after later rule-based
processing. Plot each completed model separately for Gan and ExECT, with the
model-recognise output and final rule-processed output connected. The caption
should state the split, scorer, configuration, and whether the ExECT surface
uses the cited four-family inventory scorer or a clearly labelled secondary
surface.

## Visual and supporting-material plan

The main Results section contains Table 1, the five-cell cross-task comparison,
and Figure 1, the six-model before-and-after-rules comparison. Detailed
subgroup tables, full error taxonomy, representative development traces,
source-form ablation detail, hardware specifications, prompts, API settings,
and replay artifacts belong in supporting material unless the final page budget
permits their inclusion.

## Claim boundary

Held-out results are aggregate-only. Development examples explain mechanisms
and limitations but do not establish prevalence or clinical safety. This study
evaluates agreement with the two task-specific reference standards; it does
not claim clinical validation, deployment readiness, a universal architecture,
or visibility into model-internal reasoning.
