# Gan 2026 CandidateSet Clinical Assessment Probe: Qwen 3.6 35B Validation250 Repaired Recovery

Date: 2026-06-06

## Executive Summary

The repaired and recovered Qwen 3.6 35B CandidateSet clinical-assessment probe is a strong schema-fit and internal-consistency result, but it is not yet a final answer-quality result.

After deterministic assembly repairs and a targeted cached recovery of six previously missing rows, the validation250 artifact reaches complete structural coverage:

- clinical assessment rows: 250/250;
- call failures: 0;
- parse/validation failures: 0;
- missing CandidateSet rows: 0;
- diagnostic flags: 0;
- invalid candidate references: 0;
- role overlap rows: 0.

This is a major improvement over the original lenient draft artifact, which had 244/250 clinical assessments and 20 diagnostic-flag rows, including 6 missing assessments. It is also a decisive improvement over the non-lenient v3 artifact, which only produced 26/250 clinical assessments.

However, the clean diagnostic result should not be read as a clean clinical result. The current diagnostics check role validity, coarse policy consistency, context leakage, and reference integrity. They do not fully verify normalized operand correctness, duplicate/additive semantics, summary quality, or clinical truth against a gold answer. The remaining risk is concentrated in normalization and synthesis polish:

- 61/250 rows have at least one `normalization_issues` entry.
- 46/250 rows have a non-repair parsing or normalization issue.
- 11 frequency-rate rows have unrenderable or incomplete normalized frequency burdens.
- 12 seizure-free rows lack parsed seizure-free duration operands.
- 13 rows have empty summaries.
- 13 rows have summary text that leaks management, safety, medication, driving, investigation, or care-plan context.
- Several additive rows remain clinically risky, especially where the primary facts are duplicates, totals plus components, or different frequency windows.

The run is therefore best characterized as follows:

> Qwen 3.6 35B, with CandidateSet input and deterministic assembly repair, is viable for producing a complete clinical-assessment object over validation250. It is not yet sufficient evidence that the downstream rendered seizure-frequency answer will be correct without further projection/rendering checks and stronger normalization diagnostics.

## Artifacts Reviewed

Primary recovered artifact:

- `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_lenientdraft_repaired_recovered_2026-06-06.jsonl`
- `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_lenientdraft_repaired_recovered_2026-06-06.md`

Diagnostics:

- `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_lenientdraft_repaired_recovered_diagnostics_2026-06-06.jsonl`
- `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_lenientdraft_repaired_recovered_diagnostics_2026-06-06.json`
- `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_lenientdraft_repaired_recovered_diagnostics_2026-06-06.md`

Targeted recovery artifact:

- `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_lenientdraft_missing6_recovery_2026-06-06.jsonl`
- `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_lenientdraft_missing6_recovery_2026-06-06.md`

CandidateSet source:

- `experiments/gan2026_validation250_candidate_set_qwen36_35b_v3_nested_dedupe_2026-06-06.jsonl`

Code changes supporting the recovered run:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_clinical_assessment_probe.py`
- `tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py`

## Claim Boundary

This report evaluates clinical-assessment schema fit, role/policy consistency, normalization health, and qualitative failure modes. It does not compute benchmark accuracy. It does not compare rendered answers to gold labels. It should not be cited as a final clinical-frequency performance estimate.

The useful claim is narrower: the repaired assembly layer can now turn Qwen-generated assessment drafts into structurally valid clinical-assessment records for all 250 validation rows, while preserving repair evidence in `normalization_issues`.

## Method

The evaluation used four passes:

1. Read the recovered artifact-level summary.
2. Read the clinical-assessment diagnostics summary.
3. Compute additional row-level statistics from the JSONL:
   - normalization issue counts;
   - repair issue counts;
   - kind/policy combinations;
   - primary candidate count distributions;
   - empty and verbose summaries;
   - context leakage terms in summaries;
   - unrenderable burden heuristics.
4. Manually inspected high-risk rows, especially additive, multi-primary, recovered, and parser-issue rows.

The recovery of the six missing rows was performed as a targeted cached live run over:

- 531;
- 1695;
- 2932;
- 2938;
- 5082;
- 5210.

All six recovered successfully with no call failures or parse failures.

## Aggregate Results

### Schema Fit

| Metric | Result |
|---|---:|
| Rows | 250 |
| Clinical assessments | 250 |
| Call failures | 0 |
| Parse/validation failure rows | 0 |
| Missing CandidateSet rows | 0 |
| Invalid candidate-reference rows | 0 |
| Role-overlap rows | 0 |
| Diagnostic-flag rows | 0 |

This is excellent for the component's structural contract. It shows that the combination of lenient model-facing draft parsing plus deterministic assembly repair has effectively removed the major schema failure mode for this run.

### Assessment Kind Distribution

| Assessment kind | Count |
|---|---:|
| `frequency_rate` | 158 |
| `seizure_free` | 43 |
| `unknown_frequency` | 41 |
| `cluster_frequency` | 8 |

The distribution is plausible for a validation set dominated by explicit frequency references, with a meaningful minority of seizure-free and uncertain-frequency cases.

### Aggregation Policy Distribution

| Aggregation policy | Count |
|---|---:|
| `single_fact` | 126 |
| `primary_with_context` | 56 |
| `seizure_free_state` | 27 |
| `unknown_due_to_ambiguity` | 19 |
| `unknown_due_to_absence` | 14 |
| `additive_same_window` | 7 |
| `cluster_axis` | 1 |

The most important structural shift after repairs is that `additive_same_window` falls to 7. Earlier repair logic briefly allowed one cluster assessment into additive policy; that was corrected so additive repair only applies to `frequency_rate` assessments.

### Primary Candidate Count Distribution

| Primary count | Rows |
|---|---:|
| 0 | 8 |
| 1 | 228 |
| 2 | 11 |
| 3 | 2 |
| 4 | 1 |

The 0-primary rows are all compatible with unknown/no-reference style assessments. Most rows converge to one primary candidate, which is desirable for this component because the assessment is supposed to identify the dominant current burden rather than indiscriminately aggregate all candidate facts.

## Deterministic Repair Analysis

The deterministic repair layer is doing useful work. It converted brittle model-output choices into coherent assessment records while preserving evidence in `normalization_issues`.

Repair issue counts:

| Repair issue | Count |
|---|---:|
| `single_primary_additive_same_window_to_single_fact` | 7 |
| `multi_primary_nonadditive_demoted_to_supporting` | 6 |
| `single_primary_cluster_axis_to_single_fact` | 4 |
| `cluster_axis_without_cluster_primary_to_primary_with_context` | 2 |
| `aggregation_policy_defaulted:seizure_free_state` | 2 |
| `historical_primary_replaced_with_current:llm:2762:2` | 1 |
| `multi_primary_nonadditive_to_additive_same_window` | 1 |

There are 21 unique rows with at least one repair issue. That is 8.4 percent of the run. This is acceptable for a repaired LLM component, provided downstream reports expose these issues rather than silently treating all rows as equally clean.

The most valuable repairs are:

- missing `aggregation_policy` recovery for seizure-free rows;
- demotion of extra primaries in `primary_with_context`;
- converting single-primary additive policies back to `single_fact`;
- replacing a historical primary with a current candidate when available.

The least settled repair is `multi_primary_nonadditive_to_additive_same_window`, observed in row 2822. In that row the two primary candidates both express "myoclonic jerk daily" from deterministic and LLM sources, so additive normalization produces 2/day despite the summary saying one daily jerk. This is a likely overcount and should be handled as duplicate/co-reference, not additive burden.

## Residual Error Analysis

### 1. Normalization Issues Remain Material

Although the schema and diagnostics are clean, 61/250 rows have at least one `normalization_issues` entry. Of these, 46 rows have a non-repair parsing or normalization issue.

Normalization issue counts:

| Issue | Count |
|---|---:|
| `vague_count` | 23 |
| `seizure_free_duration_unparsed` | 12 |
| `frequency_rate_operands_unparsed` | 9 |
| `additive_frequency_period_mismatch` | 4 |
| `normalization_source_phrase_missing` | 1 |

This is the main reason not to treat the artifact as render-ready. Some issues are benign, especially `vague_count` where uncertainty is expected. Others are blockers for numeric rendering.

High-risk parser issue rows:

- Frequency-rate rows with incomplete or unrenderable normalized burden: 763, 899, 1790, 2023, 2609, 2622, 2762, 3846, 3995, 4116, 4700.
- Additive rows with period mismatch or unparsed burden: 2622, 3846, 3995, 4116.
- Seizure-free rows without parsed duration: 854, 1695, 2965, 3015, 3371, 3468, 4951, 4992, 4994, 5082, 5136, 5406.

Interpretation:

- The clinical-assessment object is valid, but the deterministic normalization layer cannot always produce the operands that a renderer or scorer would need.
- A downstream projection step must either abstain, carry uncertainty, or repair these burdens before producing a numeric answer.

### 2. Additive Policy Is Still the Highest-Risk Area

Only 7 rows use `additive_same_window`, but several deserve review.

#### Row 1413

The model selects:

- `det:1413:1`: "four focal sensory and five focal non-motors in last month";
- `det:1413:2`: "nine events per month".

The summary says the total is nine seizures in the last month. The normalized burden is 18/month.

This is a probable duplicate/total-plus-components error. `det:1413:1` already sums to 9, and `det:1413:2` restates the same total. This should be `single_fact` or primary plus supporting duplicate, not additive.

#### Row 1914

The model selects two LLM candidates that both say the same thing:

- two drop attacks and five tonic-clonic seizures in the past three months.

The summary says seven seizures, but the normalized burden is 14 over three months. This is another duplicate overcount.

#### Row 2622

The model combines:

- nightly seizures;
- three secondary generalizations this month.

This has both unparsed operands and period mismatch. Clinically, the secondary generalizations may be a subtype or escalation of the nightly seizures, not necessarily additive. The artifact correctly notes parsing trouble, but the aggregation policy remains too assertive.

#### Row 2822

The model combines a deterministic and LLM expression of the same "myoclonic jerk daily" fact. The normalized burden becomes 2/day while the summary says daily. This is a duplicate/co-reference overcount.

#### Row 3846

The selected facts mix "sz X2/d" and "on two occasions this escalated to generalized tonic-clonic activity." The summary says 2/month, but the deterministic candidate phrase suggests 2/day. The burden is unrenderable due to unparsed operands and period mismatch. This row likely needs source-text review.

#### Row 3995

The model combines "3 per day" and "abs monthly." These are different periods and likely different axes/subtypes. It should probably use the clinically dominant current burden as primary and keep the monthly absence reference as context.

#### Row 4116

The model combines "three witnessed convulsions in the past 10 days" with "one to two events on workdays." This is not a same-window additive pair. It should be primary-with-context or unknown/ambiguous depending on whether event overlap can be resolved.

Recommendation:

The diagnostics should add a stricter additive audit:

- reject additive if deterministic parsing returns period mismatch;
- reject additive if one candidate is a total/restatement of another;
- reject additive if phrases have high lexical overlap or shared source spans;
- reject additive when one fact is a subtype/escalation of the other unless the note explicitly says non-overlapping events;
- downgrade failed additive to `primary_with_context` or `single_fact` with repair evidence.

### 3. Cluster Assessment Is Structurally Sparse

Only 8 rows are `cluster_frequency`, and only one uses `cluster_axis`.

The cluster-axis repair removed earlier bad patterns, especially cases where the model selected frequency-rate candidates while declaring cluster-axis policy. That was useful. But the final distribution suggests the cluster axis is underused or fragile.

Examples:

- Rows 187 and 190 were repaired from cluster-axis-style outputs into `primary_with_context`.
- Row 1694 remains the cleanest true `cluster_axis` case, with cluster cadence and events-per-cluster represented.

Interpretation:

The model can identify clusters, but CandidateSet candidate kinds and source phrases do not always provide clean separate axes. Deterministic cluster parsing still needs better support for cases where frequency-like phrases carry cluster semantics, such as "clusters every 4 weeks."

### 4. Seizure-Free Rows Are Structurally Good But Duration Parsing Is Weak

The recovered rows are mostly seizure-free rows, and the recovery itself worked well:

| Row | Kind | Policy | Notes |
|---|---|---|---|
| 1695 | `seizure_free` | `seizure_free_state` | Policy defaulted; duration phrase "current month to date" not parsed. |
| 2932 | `seizure_free` | `seizure_free_state` | Policy defaulted; date-based seizure-free phrase preserved but duration not fully parsed. |
| 2938 | `seizure_free` | `seizure_free_state` | Date-based phrase preserved; duration unit present but low/high missing. |
| 5082 | `seizure_free` | `seizure_free_state` | Correct current no-event synthesis; no duration parsed. |
| 5210 | `seizure_free` | `seizure_free_state` | Correct seizure freedom; summary leaks driving context. |

The main issue is date and open-ended interval parsing. Phrases such as "seizure-free since 29/09/2017," "since 13-Nov-2015," "current month to date," and "recent months" are clinically useful but not converted into stable duration operands.

Recommendation:

Add deterministic date-aware seizure-free normalization:

- parse "since DD/MM/YYYY" and "since DD-Mon-YYYY";
- use clinic date from note context where available;
- preserve exact source phrase;
- add explicit issue when duration cannot be computed because the reference date is missing.

### 5. Summary Quality Is Inconsistent

The assessment summaries are often clinically useful, but the component does not reliably keep them compact and burden-focused.

Observed summary issues:

- 13 rows have empty summaries.
- 26 rows have summaries longer than 250 characters.
- 13 rows include non-burden context such as safety, SUDEP, follow-up, medication, plan, EEG, sleep hygiene, or driving.

Examples:

- Row 40 includes safety, SUDEP, and follow-up plan despite a simple four-per-week frequency.
- Row 2149 discusses seizure action plan, sleep hygiene, and follow-up while ultimately saying no specific frequency can be quantified.
- Row 5210 correctly identifies seizure freedom but adds driving/DVLA context.
- Row 4771 is a reasonable clinical synthesis but too long for a source-near burden assessment.
- Row 3753 contains speculative interpretation about whether daily events and "only two seizures" refer to different subtypes.

Interpretation:

The model often writes like a clinician summarizing a note rather than a component producing a compact burden assessment. This is understandable but risky for downstream rendering because summaries may sound more authoritative than the normalized burden supports.

Recommendation:

Add a deterministic summary sanitizer or diagnostic:

- flag empty summary;
- flag summaries over a length threshold;
- flag management-context terms;
- require that summary mention the primary burden phrase or the source-normalized phrase;
- optionally generate a deterministic fallback summary from `assessment_kind`, `aggregation_policy`, and `source_normalized_phrase`.

### 6. Unknown-Frequency Handling Is Mostly Sensible But Needs Clearer Boundaries

There are 41 unknown-frequency assessments:

- 19 `unknown_due_to_ambiguity`;
- 14 `unknown_due_to_absence`;
- 5 `primary_with_context`;
- 3 `single_fact`.

This is broadly reasonable. The model usually avoids forcing vague patterns into exact numeric burdens.

However, rows such as 3988 show that unknown-frequency can coexist with deterministic frequency-rate candidates such as "several times per week." That may be acceptable if the model treats "several" as vague, but it should be made explicit: unknown frequency due to vague count, not absence.

Recommendation:

Split unknown-frequency policy more explicitly:

- `unknown_due_to_vague_quantifier`;
- `unknown_due_to_conflicting_current_facts`;
- `unknown_due_to_absence`;
- `unknown_due_to_nonclinical_or_nonseizure_reference`.

This would make diagnostics and downstream abstention decisions cleaner.

## What Performs Well

1. Candidate ID discipline is excellent.

There are no invalid candidate references and no role overlaps. This is a major strength compared with unconstrained extraction workflows.

2. The primary/supporting/rejected role model is useful.

The component separates dominant burden from context in many difficult rows. Rows with triggers, history, seizure-free outside a pattern window, and subtype references often land in reasonable role structures.

3. Deterministic assembly repair is the right strategy.

The repair layer turns recoverable LLM schema slips into valid records without hiding the intervention. This is better than hard rejection because the rejected rows were often clinically understandable.

4. Recovery through cache worked.

The six missing rows were recovered successfully without broad rerun. The final artifact preserves a clean run summary.

5. Context leak diagnostics pass.

The normalized burden generally does not contain cluster or seizure-free context in inappropriate fields. The remaining leakage is more in the free-text summary than in the structured burden object.

## What Performs Poorly

1. Additive semantics are not safe enough.

The model and current deterministic repairs still allow additive overcounting for duplicate facts, total-plus-component facts, and different-window facts.

2. Normalized burden renderability is incomplete.

Some rows are valid assessments but cannot safely produce a numeric rendered answer because operands are missing or period windows mismatch.

3. Date-based seizure-free duration parsing is weak.

The component preserves the source phrase but often cannot turn it into duration fields.

4. Summary generation is too free-form.

It sometimes includes plan/safety/medication context, speculation, or empty strings. This needs either prompt tightening or deterministic summary fallback.

5. Diagnostics are now too permissive relative to projection needs.

Zero diagnostic flags is structurally true but could be misleading. The diagnostic suite should incorporate normalized-burden and additive-risk checks so "0 flags" better tracks render readiness.

## Recommended Next Work

### Immediate

1. Add additive safety diagnostics and repairs.

Priority rows: 1413, 1914, 2622, 2822, 3846, 3995, 4116.

2. Add a renderability diagnostic.

Flag `frequency_rate` rows without count/vague count plus period fields, and flag additive rows with period mismatch.

3. Add summary diagnostics.

Flag empty summaries, long summaries, and management-context leakage.

4. Add date-aware seizure-free duration parsing.

Start with `since <date>` and clinic-date anchored phrases.

### Medium Term

1. Run projection/render on the recovered artifact.

This will expose whether structurally valid clinical assessments can become usable final answers.

2. Compare rendered outputs to validation gold labels.

Only after projection/render should this be evaluated as an answer-quality system.

3. Add selector comparison rows for this artifact.

The current diagnostics report has no minimal/rich selector comparisons available. Adding those comparisons would make role-selection differences easier to interpret.

4. Add row-level repair summary to reports.

The markdown report should include counts of repair issues and parser issues, not just parse failures.

## Bottom Line

This run is a successful component-architecture result. The CandidateSet clinical-assessment layer can now produce complete, reference-valid structured assessments over validation250 with Qwen 3.6 35B, and deterministic repairs are both effective and auditable.

It is not yet a final performance result. The most important remaining errors are not schema errors; they are semantic normalization errors, especially additive overcounting, unrenderable frequency burdens, weak seizure-free duration parsing, and summary drift.

The next milestone should be "render-ready clinical assessments," not another schema-fit run. The proposed diagnostics and repairs above are enough to move the component from structurally complete to projection-safe.

## Projection/Render Check

After this report was drafted, the existing projection/render mechanics were run against the repaired recovered clinical-assessment artifact.

Projection/render artifact:

- `experiments/gan2026_clinical_assessment_projection_render_validation250_qwen36_35b_repaired_recovered_v0_2026-06-06.jsonl`
- `experiments/gan2026_clinical_assessment_projection_render_validation250_qwen36_35b_repaired_recovered_v0_2026-06-06.json`
- `experiments/gan2026_clinical_assessment_projection_render_validation250_qwen36_35b_repaired_recovered_v0_2026-06-06.md`

Projection score artifact:

- `experiments/gan2026_clinical_assessment_projection_score_validation250_qwen36_35b_repaired_recovered_v0_2026-06-06.jsonl`
- `experiments/gan2026_clinical_assessment_projection_score_validation250_qwen36_35b_repaired_recovered_v0_2026-06-06.json`
- `experiments/gan2026_clinical_assessment_projection_score_validation250_qwen36_35b_repaired_recovered_v0_2026-06-06.md`

### Projection/Render Results

| Metric | Result |
|---|---:|
| Rows | 250 |
| Projection rows | 250 |
| Rendered-label rows | 209 |
| Null rendered-label rows | 41 |
| Row issue rows | 0 |

Projection owner distribution:

| Owner | Count |
|---|---:|
| `rate_projection_policy` | 158 |
| `boundary_projection_policy` | 43 |
| `benchmark_renderer` | 41 |
| `cluster_projection_policy` | 8 |

Projection rules:

| Rule | Count |
|---|---:|
| `frequency_rate_operands_v0` | 158 |
| `unknown_frequency_sentinel_render_v0` | 41 |
| `seizure_free_duration_required_v0` | 29 |
| `seizure_free_duration_projection_v0` | 14 |
| `cluster_cadence_with_events_per_cluster_v0` | 5 |
| `cluster_cadence_as_event_rate_when_size_absent_v0` | 2 |
| `cluster_cadence_operands_required_v0` | 1 |

Render bases:

| Render basis | Count |
|---|---:|
| `frequency_rate` | 158 |
| `unknown_frequency_internal_state` | 41 |
| `seizure_free_duration` | 43 |
| `cluster_cadence_with_events_per_cluster` | 5 |
| `cluster_cadence_without_size` | 2 |
| `cluster_frequency` | 1 |

The renderer is behaving like a safety gate. It projects all 250 rows but renders only 209. The 41 null rendered rows are not random; they are concentrated in unknown internal states, seizure-free duration requirements, incomplete frequency operands, and one incomplete cluster-cadence case.

Null rendered-label rows:

- 763, 854, 899, 1695, 1706, 1790, 2023, 2609, 2622, 2762, 2907, 2932, 2938, 2965, 2992, 3015, 3118, 3137, 3371, 3468, 3846, 3995, 4116, 4700, 4842, 4951, 4992, 4994, 5040, 5082, 5092, 5110, 5121, 5136, 5141, 5197, 5210, 5221, 5248, 5345, 5406.

Null render causes:

- 29 seizure-free rows require duration but lack renderable duration operands.
- 11 frequency-rate rows have incomplete operands.
- 1 cluster-frequency row has incomplete cluster-cadence operands.

This validates part of the earlier concern: many normalized-burden problems do not leak into rendered labels. The renderer abstains instead.

### Mechanics Scoring Results

The existing projection scorer was then run over the rendered-label artifact. This is still a mechanics score over saved rows, not a benchmark promotion claim.

| Metric | Result |
|---|---:|
| Rows | 250 |
| Scored rows | 209 |
| Non-scored rows | 41 |
| Exact normalized-label matches on scored rows | 159/209 = 0.7608 |
| Purist correct on scored rows | 188/209 = 0.8995 |
| Pragmatic correct on scored rows | 196/209 = 0.9378 |

If null rendered labels are counted as misses over the full 250-row denominator:

| Metric | Full-denominator result |
|---|---:|
| Exact normalized-label match | 159/250 = 0.636 |
| Purist correct | 188/250 = 0.752 |
| Pragmatic correct | 196/250 = 0.784 |

The scored-only result is strong, especially pragmatic accuracy. The full-denominator result shows that abstention coverage remains a material limitation, mostly due to duration and operand parsing rather than LLM schema failure.

### Error Breakdown on Scored Rows

There are 21 purist errors among the 209 scored rows:

- 14 frequency-rate render errors;
- 6 unknown-frequency sentinel errors;
- 1 seizure-free render error.

There are 13 pragmatic errors among the 209 scored rows:

- 6 frequency-rate render errors;
- 6 unknown-frequency sentinel errors;
- 1 seizure-free render error.

Purist error rows:

- 849, 1030, 1363, 1486, 1773, 1866, 1914, 2427, 2554, 2748, 2759, 3469, 3482, 3623, 3643, 4022, 4026, 4243, 4402, 4624, 5528.

Pragmatic error rows:

- 849, 1030, 2427, 2554, 2759, 3469, 3482, 3623, 3643, 4022, 4026, 4402, 5528.

### What Projection/Render Catches

The renderer catches most rows where the structured burden is not safe to render:

- Row 2622 remains an additive period-mismatch case and is null rendered.
- Row 3846 remains a frequency/additive mismatch case and is null rendered.
- Row 3995 remains a different-window additive case and is null rendered.
- Row 4116 remains a different-window additive case and is null rendered.
- Many seizure-free rows with date/open-ended phrases are null rendered rather than converted into invented durations.

This is good behavior. It means the assessment layer can be structurally permissive while the render layer remains conservative.

### What Projection/Render Does Not Catch

The renderer does not catch all semantic overcount or primary-selection errors when operands are parseable.

Important examples:

#### Row 1413

Earlier manual inspection suggested a likely duplicate/total-plus-components risk. It did not appear in the scored-error list, which means either the gold label aligns with the rendered result or the scorer category is too coarse to expose the exact duplicate issue. This row still deserves manual review because the assessment selected both "four focal sensory and five focal non-motors" and "nine events per month."

#### Row 1914

Rendered label: 14 per 3 month.

Gold label: 7 per 3 month.

The model selected two LLM candidates that express the same "two drop attacks and five tonic-clonic in the past three months" fact. Projection then rendered the duplicate sum. This is a clear additive/co-reference overcount.

#### Row 1486

Rendered label: 5 per month.

Gold label: 3 per month.

The summary says "3 seizures in the last month," but the rendered label is 5/month. This points to a deterministic normalization/parser problem for compound phrases such as "two focal epileptic spasms and one focal non-motor in last month." The clinical assessment chose the right conceptual fact, but projection produced the wrong numeric label.

#### Rows 1773 and 1866

Both show doubling:

- Row 1773 rendered 22 per 3 month vs gold 11 per 3 month.
- Row 1866 rendered 16 per 2 month vs gold 8 per 2 month.

These are likely parser or source-phrase duplication errors where component counts and totals are both being counted.

#### Row 4022

Rendered label: 1 per month.

Gold label: 8 per month.

The assessment summary says current burden is 8 absence seizures per month, but the primary candidate/rendered output resolves to 1/month. This is a primary-candidate or deterministic parsing failure that projection does not detect.

#### Row 4026

Rendered label: 6 to 7 per month.

Gold label: 1 per month.

The summary notes a reduction and says only a single brief spell occurred over the past eight weeks, but the selected burden remains the broader 6 to 7/month history. This is a current-versus-historical/trajectory selection error.

#### Row 4624

Rendered label: 2 per month.

Gold label: 1 per 3 to 4 day.

The summary includes intervals of three to four days but the assessment primary chooses two per month. This is a dominant-burden selection error.

### Unknown-Frequency Sentinel Errors

Unknown sentinel rendering is conservative but sometimes too conservative.

Examples:

- Row 849 renders unknown, but gold is 1/year. The summary itself says current pattern is yearly seizures.
- Row 1030 renders unknown, but gold is 1 to 3/month. The model treated "one or three seizures in the last month" as ambiguous rather than a range.
- Row 2427 renders unknown, but gold is 3 to 5/month.
- Row 2554 renders unknown, but gold is 1 to 10 per 2 months.
- Row 5528 renders unknown, but gold is 1/month.

These are not schema failures. They are boundary-policy choices: the model and projection pipeline prefer abstention/unknown when a range or vague phrasing could be rendered.

This may be desirable for a high-precision system, but it hurts recall and pragmatic score.

### Seizure-Free Error

Row 3469 renders seizure-free for 6 months, while gold is unknown. The assessment chooses seizure-free status for "last six months" even though the note may describe seizures as occurring only during perimenstrual windows rather than a global seizure-free state. This is a clinical boundary error: no events outside a risk window should not automatically become global seizure freedom.

### Updated Interpretation

The projection/render check improves confidence in the architecture, but it sharpens the target for fixes.

The system now has three distinct layers:

1. Clinical-assessment schema layer: strong, complete, reference-valid.
2. Projection/render safety layer: mostly conservative; catches 41 unsafe/non-renderable rows.
3. Scored rendered output layer: strong on rows it renders, but still vulnerable to duplicate additive overcounting, parser double-counting, current-vs-historical selection errors, and over-conservative unknown classification.

The earlier conclusion should be revised:

> The next milestone is no longer merely "render-ready clinical assessments." Projection/render is already present and provides useful abstention. The next milestone is "rendered-label semantic safety": additive/co-reference guards, compound-count parser fixes, date-aware seizure-free duration rendering, and stricter current-burden selection before rendering.

### Priority Fixes After Projection/Render

1. Add co-reference duplicate guards before additive projection.

Rows 1914, 1773, 1866, and probably 1413 show that duplicate or total-plus-component facts can become doubled rendered labels.

2. Fix compound-count parsing.

Row 1486 should render 3/month, not 5/month. Similar double-count patterns should be mined from purist errors.

3. Add current-burden dominance checks.

Rows 4026, 4624, 3643, and 1363 show recent/current selection problems where a contextual or historical pattern competes with the current burden.

4. Revisit unknown rendering policy for explicit ranges.

Rows 1030, 2427, and 2554 are range-like facts that could be rendered instead of becoming unknown.

5. Extend seizure-free duration parsing.

This would reduce the 29 seizure-free null renders. It should be done cautiously and anchored to clinic dates.

6. Preserve abstention for genuinely unsafe rows.

The 41 null renders are not just failures; many are appropriate abstentions. Any recall improvement should distinguish "can parse safely" from "should render."
