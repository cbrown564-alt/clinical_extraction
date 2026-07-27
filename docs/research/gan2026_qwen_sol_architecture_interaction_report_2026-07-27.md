# Why Qwen leads GPT-5.6 Sol in the Gan 2026 LLM-with-rules pipeline

Date: 2026-07-27  
Status: no-call `dev750` development mechanism report

## Answer

The retained evidence does **not** show that the deterministic rule stack is optimized for Qwen. On the same saved event-ledger output, fixed processing rescues 343 Qwen rows and 389 Sol rows, while regressing 7 Qwen rows and 2 Sol rows. The same-output net benefit is therefore larger for Sol, not Qwen.

The apparent reversal comes from comparing two different model tasks. `llm_only` asks for one direct final label. `llm_with_rules` asks for an event ledger plus a selected answer, then applies deterministic processing. Qwen is weaker on the direct-label task but interacts better with the event-ledger representation on particular Gan families. In the final event-ledger pipeline, Qwen is uniquely correct on 44 rows and Sol is uniquely correct on 32 rows: the 12-row net difference exactly explains 667 versus 655.

This is a development answer, not proof that no validation overfitting exists. The deterministic policy was developed on Gan validation data, and the two methods are not a same-prompt or same-raw-output architecture ablation.

## What was compared

| Layer | Qwen | Sol | Interpretation |
| --- | ---: | ---: | --- |
| Direct-label raw model boundary | 405/750 | 468/750 | Scorer-facing raw label before the direct adapter |
| Direct-label final | 565/750 | 590/750 | The report's `llm_only` condition |
| Event-ledger raw model boundary | 331/750 | 268/750 | Model-selected label before fixed processing |
| Event-ledger final | 667/750 | 655/750 | The report's `llm_with_rules` condition |

Raw-boundary accuracy is not a pure clinical-selection measure. Source-near Sol labels are often Purist-unscorable until canonicalized, while some vague labels can map to a scorer sentinel. It is retained here to measure transitions, not to rank the raw models.

## The headline gain is a model-by-method interaction

| Model | Direct-label final | Event-ledger final | Difference | Wrong→correct | Correct→wrong |
| --- | ---: | ---: | ---: | ---: | ---: |
| Qwen 3.6:35B | 565/750 | 667/750 | +102 | 125 | 23 |
| GPT-5.6 Sol | 590/750 | 655/750 | +65 | 96 | 31 |

Because the prompt, requested schema, and division of work all change, the 102-versus-65 difference cannot be attributed to rules alone.

## Same-saved-output effect of fixed processing

| Model and method | Raw correct | Final correct | Wrong→correct | Correct→wrong | Net |
| --- | ---: | ---: | ---: | ---: | ---: |
| Qwen 3.6:35B direct-label | 405/750 | 565/750 | 167 | 7 | +160 |
| Qwen 3.6:35B event-ledger | 331/750 | 667/750 | 343 | 7 | +336 |
| GPT-5.6 Sol direct-label | 468/750 | 590/750 | 123 | 1 | +122 |
| GPT-5.6 Sol event-ledger | 268/750 | 655/750 | 389 | 2 | +387 |

The event-ledger fixed code gives Sol 51 more net scorer rescues than Qwen (+387 versus +336). That directly contradicts the narrow hypothesis that the rule stack succeeds because it was tailored to Qwen's output form.

## Final head-to-head result

| Outcome | Rows |
| --- | ---: |
| Both correct | 623 |
| Qwen only correct | 44 |
| Sol only correct | 32 |
| Both wrong | 51 |

### Where Qwen's 44 unique wins come from

- Gold families: `cluster` 13, `frequency` 24, `seizure_free` 4, `unknown` 3.
- Sol first-failure owners: `llm_clinical_selection` 44.
- Sol clinical subproblems: `cluster_or_diary_aggregation` 21, `competing_event_selection` 6, `rate_denominator` 8, `temporal_selection` 3, `uncertainty_boundary` 6.

### Where Sol's 32 unique wins come from

- Gold families: `cluster` 2, `frequency` 18, `no_reference` 3, `seizure_free` 1, `unknown` 8.
- Qwen first-failure owners: `deterministic_semantic` 1, `evidence_selection` 10, `format_or_schema` 3, `llm_clinical_selection` 18.
- Qwen clinical subproblems: `cluster_or_diary_aggregation` 7, `competing_event_selection` 3, `rate_denominator` 6, `seizure_free_boundary` 9, `temporal_selection` 6, `uncertainty_boundary` 1.

### Shared residual failures

Both models are wrong on 51 rows. Qwen ownership on those rows: `deterministic_semantic` 3, `evidence_selection` 13, `llm_clinical_selection` 35. Sol ownership: `deterministic_semantic` 2, `llm_clinical_selection` 49.

## What is and is not optimized for Qwen

| Hypothesis | Verdict from `dev750` | Evidence |
| --- | --- | --- |
| Fixed rules preferentially rescue Qwen output | Contradicted | Same-output net rescue is +336 for Qwen and +387 for Sol. |
| Fixed rules overwrite Qwen less often | Partly supported, too small to explain the lead | Seven Qwen and two Sol event-ledger raw-correct answers become wrong; the difference is five rows, not twelve, and several are shared policy defects. |
| Event-ledger prompting suits Qwen better than direct-label prompting | Supported on this development distribution | Qwen's between-method gain is +102 versus +65 for Sol, concentrated in cluster/diary and seizure-free cases in the retained comparison. |
| The architecture is optimized for local models | Unmeasured | Local execution is confounded with model identity; only Qwen and Gemma are local and no matched hosted/local route ablation exists. |
| The architecture is optimized for smaller models | Unmeasured | Parameter count is confounded with model family, training, serving route, and output behavior. |
| Sol is under-optimized | Plausible, not demonstrated | Sol had fewer costly iterations, but no Sol-specific prompt or adapter candidate was predeclared and replayed here. |
| Sol should necessarily remain best after rules because it is best LLM-only | Rejected as an assumption | The methods ask the model to solve different representation and selection tasks; rank preservation is not guaranteed. |

## Unique failure modes and first decision owner

The useful optimization target is not “make the rules more Sol-like.” It is the first stage that loses the correct fact:

- `llm_clinical_selection`: the event ledger or selected event is already wrong.
- `evidence_selection`: the selected quotation is missing or not an exact source span.
- `deterministic_semantic`: fixed selection or aggregation changes a usable model answer.
- `format_or_schema`: output cannot be retained without structural repair.

Qwen's distinctive weakness is evidence copying, documented separately. Sol's event-ledger labels are more often source-near and initially Purist-unscorable, so deterministic canonicalization produces more same-output rescues. The final 12-row Qwen lead is produced by the balance of 44 versus 32 unique wins, not by one Qwen-specific rule.

## Deterministic raw-correct regressions

These are every event-ledger row where either model is scorer-correct at the model boundary and wrong after fixed processing. They are the strongest direct evidence of over-rule on permitted development data.

| Row | Gold | Regressed model(s) | Qwen raw → final | Sol raw → final |
| ---: | --- | --- | --- | --- |
| 2459 | `7 to 9 per 2 week` | Qwen 3.6:35B | `7 to 9 per 2 weeks` → `5 per 5 month` | `7 to 9 seizures per 2 weeks` → `5 per 5 month` |
| 2932 | `seizure free for 9 month` | Qwen 3.6:35B, GPT-5.6 Sol | `seizure free since 29/09/2017` → `13 per 2 month` | `seizure free since 29/09/2017` → `13 per 2 month` |
| 6368 | `unknown` | Qwen 3.6:35B | `multiple per week` → `3 per 6 week` | `1 every 1 to 2 weeks` → `1 per 1 to 2 week` |
| 10183 | `unknown` | Qwen 3.6:35B | `unknown` → `2 per 6 week` | `2 episodes in 6 weeks` → `2 per 6 week` |
| 10542 | `unknown, 2 to 4 per cluster` | Qwen 3.6:35B | `unknown` → `2 to 4 per 3 month` | `2 to 4 absences per cluster` → `2 to 4 per 3 month` |
| 12979 | `3 per 4 month` | Qwen 3.6:35B | `3 per year` → `4 per 3 month` | `3 seizures in 2021 year to date` → `3 per 4 month` |
| 16161 | `18 per 3 month` | GPT-5.6 Sol | `multiple per week` → `11 per 3 month` | `7 per month` → `11 per 3 month` |
| 16774 | `19 per 7 month` | Qwen 3.6:35B | `3 per month` → `19 per 4 month` | `19 seizure-like events from November through May` → `19 per 4 month` |

The existing row audit records the clinical interpretation of these cases. Clear shared defects include historical diary counts overriding an explicit current seizure-free statement and incorrect observation-window denominators. These are policy defects, not evidence that Qwen was favored.

## Decision

Do not assume that a Sol-specific tuning pass will make Sol win, and do not promote a model-specific rule branch from this result. The next defensible study is a frozen Sol-focused development candidate that changes one component at a time: event-ledger prompt wording, clinical selection, or deterministic aggregation. It must replay the same `dev750` rows, report Qwen as a fixed regression comparator, and require exact selected evidence on every claimed changed-row win.

## Exhaustive final divergence and failure appendix

The table below contains every row where the final Qwen and Sol `llm_with_rules` correctness differs or both are wrong. Rows where both are correct are omitted because they do not explain the ranking or residual errors.

| Row | Outcome | Gold | Qwen raw → final | Sol raw → final | Qwen owner/subproblem | Sol owner/subproblem |
| ---: | --- | --- | --- | --- | --- | --- |
| 1030 | `both_wrong` | `1 to 3 per month` | `unknown` → `1 per month` | `1 to 3 seizures last month` → `1 per month` | `evidence_selection` / `uncertainty_boundary` | `llm_clinical_selection` / `rate_denominator` |
| 1046 | `qwen_only_correct` | `3 to 5 per month` | `3 to 5 per month` → `3 to 5 per month` | `3 or 5 seizures per month` → `5 per month` | `evidence_selection` / `rate_denominator` | `llm_clinical_selection` / `rate_denominator` |
| 1773 | `qwen_only_correct` | `11 per 3 month` | `11 events in 3 months` → `11 per 3 month` | `1 to 2 per week` → `1 to 2 per week` | `none` / `rate_denominator` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 1880 | `both_wrong` | `8 per 2 month` | `multiple per week` → `multiple per week` | `3 clusters this month, approximately 4 absences per cluster` → `3 cluster per month, 4 per cluster` | `evidence_selection` / `rate_denominator` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 1979 | `qwen_only_correct` | `6 per 2 month` | `6 events in 2 months` → `3 per 2 month` | `2 clusters per week` → `unknown` | `evidence_selection` / `rate_denominator` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 2023 | `qwen_only_correct` | `5 per month` | `5 per month` → `5 per month` | `5 seizures this month` → `no seizure frequency reference` | `none` / `rate_denominator` | `llm_clinical_selection` / `competing_event_selection` |
| 2459 | `both_wrong` | `7 to 9 per 2 week` | `7 to 9 per 2 weeks` → `5 per 5 month` | `7 to 9 seizures per 2 weeks` → `5 per 5 month` | `deterministic_semantic` / `rate_denominator` | `llm_clinical_selection` / `rate_denominator` |
| 2932 | `both_wrong` | `seizure free for 9 month` | `seizure free since 29/09/2017` → `13 per 2 month` | `seizure free since 29/09/2017` → `13 per 2 month` | `evidence_selection` / `seizure_free_boundary` | `deterministic_semantic` / `seizure_free_boundary` |
| 3371 | `sol_only_correct` | `unknown` | `seizure free for 8 weeks` → `seizure free for multiple year` | `unknown` → `unknown` | `llm_clinical_selection` / `seizure_free_boundary` | `none` / `uncertainty_boundary` |
| 3534 | `sol_only_correct` | `unknown` | `seizure free for 7 months` → `seizure free for 7 month` | `unknown` → `unknown` | `llm_clinical_selection` / `seizure_free_boundary` | `none` / `uncertainty_boundary` |
| 4337 | `qwen_only_correct` | `3 per 3 month` | `3 seizures since June 2021` → `3 per 3 month` | `3 events from 3 June to 23 September 2021` → `3 per 1 month` | `evidence_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 4624 | `sol_only_correct` | `1 per 3 to 4 day` | `multiple per week` → `multiple per week` | `1 focal aware seizure every 3 to 4 days` → `1 per 3 to 4 day` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `none` / `cluster_or_diary_aggregation` |
| 4771 | `sol_only_correct` | `unknown` | `2 per 6 weeks` → `2 per 6 week` | `several seizure clusters per month` → `unknown` | `llm_clinical_selection` / `rate_denominator` | `none` / `cluster_or_diary_aggregation` |
| 5491 | `both_wrong` | `unknown` | `increasing sporadic seizures (jerks and brief loss of awareness)` → `2 per 6 week` | `2 in 6 weeks` → `2 per 6 week` | `evidence_selection` / `temporal_selection` | `llm_clinical_selection` / `rate_denominator` |
| 5763 | `both_wrong` | `2 per month` | `6 seizures in 3 months` → `2 per 3 month` | `approximately 6 seizures over 3 months` → `2 per 3 month` | `llm_clinical_selection` / `rate_denominator` | `llm_clinical_selection` / `rate_denominator` |
| 5837 | `both_wrong` | `2 cluster per 3 week, multiple per cluster` | `multiple per week` → `multiple per week` | `2 myoclonic clusters in 3 weeks` → `unknown` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 6065 | `both_wrong` | `5 per month` | `increasing frequency, up to 5 per month` → `multiple per month` | `5 seizures in September 2025` → `no seizure frequency reference` | `llm_clinical_selection` / `rate_denominator` | `llm_clinical_selection` / `competing_event_selection` |
| 6077 | `both_wrong` | `unknown` | `seizure free for 8 month` → `1 per 1 month` | `1 seizure since last review` → `1 per 8 month` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `temporal_selection` |
| 6131 | `both_wrong` | `unknown` | `seizure free for 12 month` → `seizure free for 12 month` | `seizure free since May 2025` → `1 per 5 month` | `llm_clinical_selection` / `seizure_free_boundary` | `llm_clinical_selection` / `seizure_free_boundary` |
| 6244 | `both_wrong` | `unknown` | `2 per week` → `2 per week` | `approximately 2 per week` → `2 per week` | `llm_clinical_selection` / `rate_denominator` | `llm_clinical_selection` / `rate_denominator` |
| 6368 | `both_wrong` | `unknown` | `multiple per week` → `3 per 6 week` | `1 every 1 to 2 weeks` → `1 per 1 to 2 week` | `evidence_selection` / `temporal_selection` | `llm_clinical_selection` / `temporal_selection` |
| 6509 | `qwen_only_correct` | `1 per week` | `2 per 2 weeks` → `2 per 2 week` | `seizure flurries over several days, including 2 tonic-clonic seizures in 2 weeks` → `unknown` | `none` / `rate_denominator` | `llm_clinical_selection` / `uncertainty_boundary` |
| 6571 | `both_wrong` | `unknown` | `seizure free since mid-June 2025` → `seizure free for multiple year` | `seizure free since mid-June 2025` → `seizure free for multiple year` | `llm_clinical_selection` / `seizure_free_boundary` | `llm_clinical_selection` / `seizure_free_boundary` |
| 7167 | `both_wrong` | `1 cluster per 2 weeks, 2 to 4 per cluster` | `3 clusters in 6 weeks (2-4 events per cluster)` → `unknown` | `3 clusters in 6 weeks, 2 to 4 events per cluster` → `unknown` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 7168 | `qwen_only_correct` | `unknown` | `multiple per week (myoclonic jerks), 2 per year (GTC), catamenial clustering` → `unknown` | `2 tonic-clonic seizures per year` → `2 per year` | `evidence_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `rate_denominator` |
| 7195 | `sol_only_correct` | `unknown` | `1 per month` → `1 per month` | `2 events in the weeks surrounding childbirth three months ago` → `no seizure frequency reference` | `llm_clinical_selection` / `temporal_selection` | `none` / `competing_event_selection` |
| 7275 | `qwen_only_correct` | `1 per month` | `3 events in 12 weeks` → `3 per 12 week` | `3 events over 12 weeks` → `5 per 3 month` | `none` / `rate_denominator` | `llm_clinical_selection` / `rate_denominator` |
| 7401 | `both_wrong` | `2 cluster per 6 week, 1 to 2 per cluster` | `2 clusters per 6 weeks (1-2 events per cluster)` → `unknown` | `2 clusters in 6 weeks, with 1–2 events per cluster` → `unknown` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 7615 | `both_wrong` | `3 to 7 per month` | `multiple per week (focal) and 2 per year (GTC)` → `2 per 10 month` | `3–6 brief episodes per menstrual cycle, clustered within a 5-day perimenstrual window` → `no seizure frequency reference` | `evidence_selection` / `rate_denominator` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 7859 | `sol_only_correct` | `unknown` | `seizure free for several weeks` → `seizure free for multiple year` | `2 prodromal events since May` → `no seizure frequency reference` | `evidence_selection` / `seizure_free_boundary` | `none` / `temporal_selection` |
| 8144 | `qwen_only_correct` | `seizure free for multiple month` | `seizure free` → `seizure free for multiple year` | `unknown` → `unknown` | `evidence_selection` / `seizure_free_boundary` | `llm_clinical_selection` / `uncertainty_boundary` |
| 8160 | `both_wrong` | `seizure free for multiple month` | `once every few weeks` → `no seizure frequency reference` | `1 every few weeks` → `no seizure frequency reference` | `llm_clinical_selection` / `competing_event_selection` | `llm_clinical_selection` / `competing_event_selection` |
| 8400 | `qwen_only_correct` | `seizure free for multiple month` | `seizure free for several months` → `seizure free for multiple year` | `unknown` → `unknown` | `none` / `seizure_free_boundary` | `llm_clinical_selection` / `uncertainty_boundary` |
| 8419 | `both_wrong` | `1 to 2 per week` | `multiple per week` → `multiple per week` | `episodes most nights` → `no seizure frequency reference` | `evidence_selection` / `rate_denominator` | `llm_clinical_selection` / `competing_event_selection` |
| 8805 | `qwen_only_correct` | `seizure free for multiple month` | `seizure free for 6 month` → `seizure free for 6 month` | `no convulsive seizures for 6 months` → `no seizure frequency reference` | `none` / `seizure_free_boundary` | `llm_clinical_selection` / `competing_event_selection` |
| 9250 | `qwen_only_correct` | `seizure free for multiple month` | `seizure free since January 2025` → `seizure free for multiple year` | `unknown` → `unknown` | `none` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 9496 | `qwen_only_correct` | `6 per 12 month` | `6 per year` → `6 per 18 month` | `4 focal-aware seizures in Jan-Jul 2020` → `6 per 6 month` | `none` / `rate_denominator` | `llm_clinical_selection` / `rate_denominator` |
| 9937 | `both_wrong` | `1 cluster per month, multiple per cluster` | `multiple per week (cluster frequency)` → `unknown` | `1 cluster every few weeks` → `unknown` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 9943 | `both_wrong` | `1 cluster per 4 to 5 week, multiple per cluster` | `1 cluster per 4-5 weeks` → `1 per 4 to 5 week` | `1 cluster every 4 to 5 weeks` → `1 per 4 to 5 week` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 10097 | `both_wrong` | `3 cluster per month, multiple per cluster` | `3 per month` → `3 per month` | `3 clusters per month` → `unknown` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 10183 | `both_wrong` | `unknown` | `unknown` → `2 per 6 week` | `2 episodes in 6 weeks` → `2 per 6 week` | `deterministic_semantic` / `uncertainty_boundary` | `llm_clinical_selection` / `rate_denominator` |
| 10237 | `both_wrong` | `4 cluster per month, multiple per cluster` | `4 clusters per month` → `unknown` | `approximately 4 clusters per month` → `unknown` | `evidence_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 10245 | `both_wrong` | `3 cluster per month, multiple per cluster` | `3 clusters per month` → `2 per 6 month` | `approximately 3 clusters last month` → `3 per 6 month` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 10434 | `both_wrong` | `multiple cluster per week, 2 to 3 per cluster` | `several per week` → `multiple per week` | `clusters on several mornings per week, 2 to 3 events per cluster` → `unknown` | `llm_clinical_selection` / `rate_denominator` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 10542 | `both_wrong` | `unknown, 2 to 4 per cluster` | `unknown` → `2 to 4 per 3 month` | `2 to 4 absences per cluster` → `2 to 4 per 3 month` | `evidence_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 10630 | `both_wrong` | `multiple cluster per 2 week, 5 per cluster` | `several clusters per fortnight, ~5 events per cluster` → `unknown` | `several clusters per fortnight, roughly 5 spells per cluster` → `unknown` | `evidence_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 10673 | `both_wrong` | `1 cluster per month, multiple per cluster` | `multiple per month (clustered)` → `multiple per month` | `seizure clusters in most months` → `unknown` | `evidence_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 10677 | `both_wrong` | `1 cluster per month, multiple per cluster` | `1 cluster per month` → `unknown` | `approximately 1 cluster per month` → `unknown` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 10829 | `qwen_only_correct` | `2 cluster per month, multiple per cluster` | `2 clusters per month` → `2 cluster per month, multiple per cluster` | `2 cluster days this month` → `2 per 2 year` | `none` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 10965 | `qwen_only_correct` | `2 cluster per month, 4 to 5 per cluster` | `2 to 3 clusters per month, 4-5 events per cluster` → `2 to 3 cluster per month, 4 to 5 per cluster` | `2 nocturnal clusters this month, 4 to 5 events per cluster` → `unknown` | `none` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 10967 | `both_wrong` | `3 cluster per month, 4 to 5 per cluster` | `multiple per week` → `multiple per week` | `3 clusters this month, 4 to 5 events per cluster` → `unknown` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 11035 | `qwen_only_correct` | `1 cluster per 3 month, 1 per cluster` | `1 cluster per quarter with 1 generalized convulsion` → `1 cluster per 3 month, 1 per cluster` | `1 cluster every 3 months with 1 convulsion per cluster` → `unknown` | `none` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 11197 | `qwen_only_correct` | `1 cluster per month, 4 to 6 per cluster` | `1 cluster per month with 4-6 events per cluster` → `1 cluster per month, 4 to 6 per cluster` | `1 cluster this month; approximately 4 to 6 events per cluster` → `unknown` | `none` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 11216 | `both_wrong` | `unknown` | `seizure free for 4 month` → `seizure free for 4 month` | `seizure free since 25 December 2023` → `seizure free for multiple year` | `llm_clinical_selection` / `seizure_free_boundary` | `llm_clinical_selection` / `seizure_free_boundary` |
| 11254 | `both_wrong` | `unknown` | `seizure free since 31-May` → `seizure free for multiple year` | `seizure free for 3 months` → `seizure free for 3 month` | `llm_clinical_selection` / `seizure_free_boundary` | `llm_clinical_selection` / `seizure_free_boundary` |
| 11259 | `qwen_only_correct` | `unknown` | `unknown` → `unknown` | `seizure free since 27 May 2018` → `seizure free for multiple year` | `none` / `uncertainty_boundary` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 11272 | `both_wrong` | `unknown` | `seizure free for 3 month` → `seizure free for 3 month` | `seizure free for 3 months` → `seizure free for 3 month` | `llm_clinical_selection` / `seizure_free_boundary` | `llm_clinical_selection` / `seizure_free_boundary` |
| 11282 | `both_wrong` | `unknown` | `seizure free since 05-Aug` → `seizure free for multiple year` | `seizure free for 3 months` → `1 per 3 month` | `llm_clinical_selection` / `seizure_free_boundary` | `llm_clinical_selection` / `seizure_free_boundary` |
| 11337 | `sol_only_correct` | `unknown` | `1 seizure in recent period (since last review)` → `1 per 8 week` | `1 seizure since last review` → `no seizure frequency reference` | `evidence_selection` / `temporal_selection` | `none` / `temporal_selection` |
| 11389 | `sol_only_correct` | `unknown` | `1 per year (approx)` → `1 per year` | `1 recent seizure` → `no seizure frequency reference` | `llm_clinical_selection` / `temporal_selection` | `none` / `temporal_selection` |
| 11562 | `sol_only_correct` | `no seizure frequency reference` | `` → `` | `no seizure frequency reference` → `no seizure frequency reference` | `format_or_schema` / `competing_event_selection` | `none` / `competing_event_selection` |
| 11737 | `sol_only_correct` | `no seizure frequency reference` | `seizure free` → `seizure free for multiple year` | `unknown` → `unknown` | `llm_clinical_selection` / `seizure_free_boundary` | `none` / `uncertainty_boundary` |
| 11841 | `sol_only_correct` | `no seizure frequency reference` | `` → `` | `no seizure frequency reference` → `no seizure frequency reference` | `format_or_schema` / `competing_event_selection` | `none` / `competing_event_selection` |
| 12484 | `sol_only_correct` | `3 to 4 per day` | `3 to 4 per day (absences), ~1 cluster per month (myoclonic/tonic)` → `1 cluster per month, multiple per cluster` | `3 to 4 absence seizures per day` → `3 to 4 per day` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `none` / `rate_denominator` |
| 12502 | `sol_only_correct` | `4 per day` | `multiple seizure types with high frequency (4/day absence, ~1-2/month GTC, ~1/month cluster)` → `1 cluster per month, multiple per cluster` | `4 per day` → `4 per day` | `evidence_selection` / `cluster_or_diary_aggregation` | `none` / `rate_denominator` |
| 12506 | `sol_only_correct` | `4 per day` | `multiple per day (absences) with monthly GTC and cluster events` → `1 cluster per month, multiple per cluster` | `4 absences per day` → `4 per day` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `none` / `rate_denominator` |
| 12584 | `sol_only_correct` | `1 per week` | `multiple per week` → `1 per 3 month` | `weekly` → `1 per week` | `evidence_selection` / `rate_denominator` | `none` / `rate_denominator` |
| 12963 | `sol_only_correct` | `unknown` | `seizure free for 10 weeks` → `seizure free for multiple year` | `small handful of seizures this year` → `no seizure frequency reference` | `llm_clinical_selection` / `seizure_free_boundary` | `none` / `competing_event_selection` |
| 12979 | `sol_only_correct` | `3 per 4 month` | `3 per year` → `4 per 3 month` | `3 seizures in 2021 year to date` → `3 per 4 month` | `deterministic_semantic` / `rate_denominator` | `none` / `rate_denominator` |
| 13051 | `sol_only_correct` | `2 per 8 month` | `1 GTC and 1 absence cluster in recent past (3 weeks)` → `1 per day` | `1 absence cluster about 3 weeks ago` → `2 per 8 month` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `none` / `cluster_or_diary_aggregation` |
| 13114 | `sol_only_correct` | `1 per year` | `multiple per week (recent burst)` → `multiple per week` | `seizure activity on 3 consecutive days, including 1 tonic seizure` → `1 per 1 year` | `llm_clinical_selection` / `temporal_selection` | `none` / `seizure_free_boundary` |
| 13149 | `sol_only_correct` | `3 per year` | `3 seizures in the last 2 weeks` → `3 per 2 week` | `3 tonic seizures 2 Saturdays ago` → `3 per 1 year` | `evidence_selection` / `temporal_selection` | `none` / `uncertainty_boundary` |
| 13178 | `sol_only_correct` | `1 per 6 month` | `unknown` → `1 per month` | `1 recent seizure` → `1 per 6 month` | `llm_clinical_selection` / `uncertainty_boundary` | `none` / `seizure_free_boundary` |
| 13190 | `sol_only_correct` | `1 per 5 month` | `seizure free for 5 months` → `seizure free for 5 month` | `1 recent seizure` → `1 per 5 month` | `llm_clinical_selection` / `seizure_free_boundary` | `none` / `temporal_selection` |
| 13209 | `both_wrong` | `1 per 8 month` | `1 cluster per month` → `1 per 4 to 5 week` | `1 cluster every 4 to 5 weeks` → `1 per 4 to 5 week` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 13267 | `qwen_only_correct` | `2 per 5 month` | `multiple events in recent week (drop attack and myoclonic cluster)` → `2 per 5 month` | `1 myoclonic cluster over the preceding weekend` → `unknown` | `evidence_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 13290 | `sol_only_correct` | `4 per 6 month` | `2 seizures in the last 2 weeks` → `2 per 2 week` | `2 generalized tonic-clonic seizures in one day two weeks ago` → `2 per 6 month` | `llm_clinical_selection` / `rate_denominator` | `none` / `uncertainty_boundary` |
| 13858 | `sol_only_correct` | `seizure free for multiple month` | `` → `` | `unknown` → `seizure free for multiple year` | `format_or_schema` / `competing_event_selection` | `none` / `seizure_free_boundary` |
| 13893 | `sol_only_correct` | `2 per year` | `seizure free` → `seizure free for multiple year` | `2 per year` → `2 per year` | `llm_clinical_selection` / `seizure_free_boundary` | `none` / `rate_denominator` |
| 14025 | `qwen_only_correct` | `unknown` | `2 in 6 weeks` → `no seizure frequency reference` | `2 drop attacks in 6 weeks` → `2 per 6 week` | `none` / `temporal_selection` | `llm_clinical_selection` / `temporal_selection` |
| 14137 | `both_wrong` | `unknown` | `3 to 4 per 3 months` → `3 to 4 per 3 month` | `3 to 4 seizures in 3 months` → `4 per 3 month` | `llm_clinical_selection` / `temporal_selection` | `llm_clinical_selection` / `temporal_selection` |
| 14187 | `qwen_only_correct` | `2 to 3 per month` | `seizure free` → `2 to 3 per 1 month` | `2 to 3 seizures since 10 Jul` → `no seizure frequency reference` | `none` / `seizure_free_boundary` | `llm_clinical_selection` / `temporal_selection` |
| 14214 | `qwen_only_correct` | `2 to 4 per month` | `seizure free` → `2 to 4 per 1 month` | `2 to 4 seizures shortly after 27 Nov` → `no seizure frequency reference` | `none` / `seizure_free_boundary` | `llm_clinical_selection` / `competing_event_selection` |
| 14250 | `qwen_only_correct` | `2 per month` | `seizure free since 03-Mar` → `2 per 1 month` | `2 seizures in 1 week` → `2 per week` | `none` / `seizure_free_boundary` | `llm_clinical_selection` / `rate_denominator` |
| 14282 | `sol_only_correct` | `multiple per month` | `seizure free` → `seizure free for multiple year` | `several seizures in 1 week` → `no seizure frequency reference` | `llm_clinical_selection` / `seizure_free_boundary` | `none` / `competing_event_selection` |
| 14284 | `qwen_only_correct` | `2 to 3 per month` | `seizure free since 21-Feb-2017` → `2 to 3 per 1 month` | `2 to 3 seizures in one week` → `3 per week` | `evidence_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `rate_denominator` |
| 14317 | `qwen_only_correct` | `4 per 2 month` | `seizure free since early April` → `4 per 2 month` | `4 seizures around 4 April 2017` → `no seizure frequency reference` | `evidence_selection` / `seizure_free_boundary` | `llm_clinical_selection` / `competing_event_selection` |
| 14332 | `qwen_only_correct` | `5 per 2 month` | `seizure free for 2 months` → `5 per 2 month` | `5 seizures around early October 2017` → `no seizure frequency reference` | `evidence_selection` / `seizure_free_boundary` | `llm_clinical_selection` / `competing_event_selection` |
| 14335 | `qwen_only_correct` | `3 to 4 per 2 month` | `seizure free for 8 weeks` → `3 to 4 per 8 week` | `3 to 4 seizures around 10 Oct` → `no seizure frequency reference` | `evidence_selection` / `seizure_free_boundary` | `llm_clinical_selection` / `competing_event_selection` |
| 14454 | `both_wrong` | `2 per 2 month` | `seizure free since 11 Feb` → `seizure free for multiple year` | `2 seizures in February` → `no seizure frequency reference` | `evidence_selection` / `seizure_free_boundary` | `llm_clinical_selection` / `competing_event_selection` |
| 14524 | `both_wrong` | `2 per 6 month` | `occasional clusters` → `unknown` | `occasional seizure clusters` → `unknown` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 14628 | `qwen_only_correct` | `2 per 2 month` | `2 recent events` → `2 per 2 month` | `2 seizure-like events from April to June 2015` → `no seizure frequency reference` | `none` / `temporal_selection` | `llm_clinical_selection` / `temporal_selection` |
| 14635 | `both_wrong` | `5 per 4 month` | `seizure free since late November 2016` → `5 per 5 month` | `4 seizures in November 2016` → `5 per 5 month` | `llm_clinical_selection` / `seizure_free_boundary` | `llm_clinical_selection` / `rate_denominator` |
| 14806 | `qwen_only_correct` | `1 per 2 month` | `seizure free for 1 month` → `1 per 2 month` | `1 recent cluster with several aura-like events` → `unknown` | `none` / `seizure_free_boundary` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 15108 | `both_wrong` | `3 to 4 per 15 month` | `2 to 3 per month` → `2 to 3 per 15 month` | `2 to 3 morning jerks since January 2024` → `2 to 3 per 15 month` | `llm_clinical_selection` / `temporal_selection` | `llm_clinical_selection` / `temporal_selection` |
| 15242 | `qwen_only_correct` | `multiple cluster per 15 month, multiple per cluster` | `occasional clusters of myoclonic jerks and intermittent morning jerks` → `multiple cluster per 15 month, multiple per cluster` | `unknown` → `unknown` | `evidence_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 15317 | `sol_only_correct` | `2 to 3 per 15 month` | `2 to 3 per month` → `2 to 3 per 1 month` | `2 to 3 myoclonic jerks since last review` → `2 to 3 per 15 month` | `llm_clinical_selection` / `temporal_selection` | `none` / `temporal_selection` |
| 15376 | `sol_only_correct` | `1 cluster per 2 week, 4 to 6 per cluster` | `multiple per week (clusters of 4-6 daily)` → `unknown` | `4 to 6 seizures in one day about every 2 weeks` → `1 cluster per 2 week, 4 to 6 per cluster` | `evidence_selection` / `cluster_or_diary_aggregation` | `none` / `cluster_or_diary_aggregation` |
| 15404 | `qwen_only_correct` | `1 cluster per 4 month, 3 to 4 per cluster` | `3 to 4 per day (in clusters)` → `3 to 4 per 4 month` | `3 to 4 seizures per cluster day after up to 4 seizure-free months` → `seizure free for multiple year` | `none` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 15429 | `qwen_only_correct` | `1 cluster per 2 month, 4 per cluster` | `4 per day (in clusters)` → `4 per 2 month` | `1 cluster after up to 2 seizure-free months, with 4 seizures in 1 day` → `seizure free for multiple year` | `none` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 15431 | `sol_only_correct` | `1 cluster per 4 month, 5 per cluster` | `seizure free for 3 month` → `seizure free for 3 month` | `1 cluster of 5 seizures every up to 4 months` → `5 per 4 month` | `evidence_selection` / `seizure_free_boundary` | `none` / `cluster_or_diary_aggregation` |
| 15442 | `qwen_only_correct` | `1 cluster per 4 day, 2 per cluster` | `2 per cluster (on cluster days)` → `1 cluster per 4 day, 2 per cluster` | `1 cluster day after 4 seizure-free days, typically 2 tonic seizures per cluster day` → `seizure free for multiple year` | `none` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 15470 | `qwen_only_correct` | `1 cluster per 5 day, multiple per cluster` | `multiple per week (tonic) and 2 per 3 months (convulsive)` → `1 cluster per 5 day, 2 per cluster` | `several tonic seizures per cluster day` → `unknown` | `evidence_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 15479 | `qwen_only_correct` | `1 cluster per 4 to 5 day, 2 per cluster` | `multiple per week (clustered)` → `1 cluster per 4 to 5 day, 2 per cluster` | `typically 2 tonic seizures per cluster day after 4 to 5 seizure-free days` → `seizure free for multiple year` | `none` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 15497 | `qwen_only_correct` | `1 cluster per 4 to 5 day, 5 per cluster` | `1 cluster per week (approx)` → `1 cluster per 5 day, 5 per cluster` | `1 cluster after 4 to 5 seizure-free days, with 5 seizures within 24 hours` → `seizure free for multiple year` | `none` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 15519 | `qwen_only_correct` | `1 cluster per 4 day, 3 per cluster` | `3 per day (in clusters)` → `1 cluster per 4 day, 3 per cluster` | `approximately 2 clusters per month, typically 3 seizures within 24 hours` → `unknown` | `none` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 15529 | `qwen_only_correct` | `1 cluster per 3 day, 4 per cluster` | `1 cluster per week (approx)` → `1 cluster per 3 day, 4 per cluster` | `4 seizures within 24 hours during clusters` → `unknown` | `none` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 15697 | `sol_only_correct` | `1 per day` | `multiple per day (clusters) and multiple per week` → `multiple per week` | `almost 1 myoclonic cluster per day` → `1 per day` | `evidence_selection` / `cluster_or_diary_aggregation` | `none` / `cluster_or_diary_aggregation` |
| 15745 | `qwen_only_correct` | `2 to 3 per week` | `2 to 3 per week` → `2 to 3 per week` | `2 to 3 days per week with absence seizures` → `unknown` | `none` / `rate_denominator` | `llm_clinical_selection` / `uncertainty_boundary` |
| 15768 | `qwen_only_correct` | `2 to 3 per week` | `2 to 3 per week` → `2 to 3 per week` | `2 to 3 days per week with absence seizures` → `unknown` | `none` / `rate_denominator` | `llm_clinical_selection` / `uncertainty_boundary` |
| 15772 | `qwen_only_correct` | `2 per week` | `2 days per week` → `2 per week` | `2 days per week with absence seizures` → `unknown` | `none` / `rate_denominator` | `llm_clinical_selection` / `uncertainty_boundary` |
| 16091 | `both_wrong` | `3 per 3 month` | `3 seizures in 3 months (current window)` → `1 per 2 month` | `3 seizures from July through September 2011 (2 so far in September)` → `1 per 2 month` | `llm_clinical_selection` / `temporal_selection` | `llm_clinical_selection` / `rate_denominator` |
| 16161 | `both_wrong` | `18 per 3 month` | `multiple per week` → `11 per 3 month` | `7 per month` → `11 per 3 month` | `llm_clinical_selection` / `rate_denominator` | `deterministic_semantic` / `rate_denominator` |
| 16203 | `both_wrong` | `9 per 3 month` | `9 seizures over 3 months (approx. 3 per month)` → `8 per 2 month` | `1 in September, 5 in August, and 3 in July` → `8 per 2 month` | `llm_clinical_selection` / `rate_denominator` | `llm_clinical_selection` / `rate_denominator` |
| 16220 | `both_wrong` | `11 per 4 month` | `seizure free for current month (March 2024)` → `11 per 2 month` | `4 seizures in February` → `11 per 2 month` | `llm_clinical_selection` / `seizure_free_boundary` | `llm_clinical_selection` / `rate_denominator` |
| 16432 | `qwen_only_correct` | `1 per 2 day` | `multiple per day` → `1 per 2 day` | `occasionally 1 per day` → `2 per 2 month` | `none` / `rate_denominator` | `llm_clinical_selection` / `rate_denominator` |
| 16645 | `qwen_only_correct` | `5 per 7 month` | `multiple per month` → `5 per 7 month` | `5 seizures from August through February` → `5 per 4 month` | `evidence_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 16714 | `both_wrong` | `5 per 6 month` | `multiple per month` → `5 per 4 month` | `5 seizures from November through April` → `5 per 4 month` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 16728 | `both_wrong` | `4 per 6 month` | `3 seizures in the last several months (Aug, Oct, Jan)` → `4 per 4 month` | `4 seizures over the last several months` → `4 per 4 month` | `evidence_selection` / `rate_denominator` | `llm_clinical_selection` / `rate_denominator` |
| 16757 | `qwen_only_correct` | `13 per 6 month` | `multiple per month` → `13 per 6 month` | `6 seizures within 30 minutes` → `12 per 3 month` | `evidence_selection` / `rate_denominator` | `llm_clinical_selection` / `rate_denominator` |
| 16772 | `both_wrong` | `9 per 5 month` | `10 seizures over 3 months` → `8 per 2 month` | `9 seizures since last review (November–March)` → `8 per 2 month` | `llm_clinical_selection` / `rate_denominator` | `llm_clinical_selection` / `temporal_selection` |
| 16774 | `both_wrong` | `19 per 7 month` | `3 per month` → `19 per 4 month` | `19 seizure-like events from November through May` → `19 per 4 month` | `deterministic_semantic` / `rate_denominator` | `llm_clinical_selection` / `rate_denominator` |
| 16867 | `both_wrong` | `6 per 7 month` | `6 seizures over the last 7 months (Dec-Mar-Jun)` → `5 per 4 month` | `6 seizures from December through June` → `6 per 4 month` | `llm_clinical_selection` / `rate_denominator` | `llm_clinical_selection` / `rate_denominator` |
| 17110 | `both_wrong` | `4 to 5 cluster per week, multiple per cluster` | `4 to 5 days per week` → `4 to 5 per week` | `absence seizure clusters 4 to 5 days per week` → `unknown` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 17135 | `both_wrong` | `5 cluster per month, multiple per cluster` | `5 days per month with absence seizure clusters` → `1 cluster per month, multiple per cluster` | `absence seizure clusters on 5 days per month` → `1 cluster per month, multiple per cluster` | `llm_clinical_selection` / `cluster_or_diary_aggregation` | `llm_clinical_selection` / `cluster_or_diary_aggregation` |
| 17146 | `sol_only_correct` | `1 per day` | `multiple per day` → `multiple per week` | `daily` → `1 per day` | `evidence_selection` / `rate_denominator` | `none` / `rate_denominator` |
| 17167 | `sol_only_correct` | `1 per week` | `multiple per week` → `multiple per week` | `weekly myoclonic jerks` → `1 per week` | `evidence_selection` / `rate_denominator` | `none` / `rate_denominator` |

## Reproducibility and limits

- Protocol: `docs/experiments/gan2026/gan2026_qwen_sol_architecture_interaction_protocol_2026-07-27.md`
- Machine artifact: `experiments/gan2026_qwen_sol_architecture_interaction_20260727.json`
- Inputs: four retained 750-row JSONL files plus the retained post-panel attribution artifact.
- Calls: none; all results are saved-output replay and analysis.
- Scorer: Gan Purist primary; Pragmatic is not used to define the row sets.
- Split: `dev750`; retained identifiers say `validation750`.
- `test450`: aggregate context only; no test row was opened.
- Exact evidence is textual substring provenance, not clinical semantic validation.
