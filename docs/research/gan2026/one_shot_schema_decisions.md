# One-call prompt and schema decisions

Canonical owner of representation versions, prompt audits and their rationale.
Reorganised 2026-09-14 from the [study protocol](one_shot_paper_protocol.md).
R8 is the latest development representation below. Earlier dated sections describe
their named versions; their uses of “current” refer to that decision date.
They do not override the [source annotation guide](seizure_finding_annotation_guide.md).
Execution results and authorisations belong to the [execution record](one_shot_execution_record.md).

## Prospective R9 two-week absence rule (2026-09-23)

R9 revision `guide_v083_two_week_absence_candidate` now tells the model to
exclude known seizure-free intervals shorter than two weeks and ordinary gaps
between recurring clusters. The owner chose the two-week threshold after review
of source 15442 (four-day intercluster gap), 14872 (two-week current absence)
and 12506 (explicit three-week longest absence). An explicit anchor with an
unknown duration remains representable; the model must not invent elapsed time.
This is a prompt-only candidate, not a new model result. The v0.8.3 reference
still includes a ten-day `none since` finding in source 15513 and therefore
needs a versioned correction before comparison against this prompt.

The later R9 revision `guide_v084_cluster_units_and_seizure_link_candidate`
also instructs one structured finding for a single dated cluster or for
cluster days with a stated size. The date is unscored context. It requires an
explicit seizure link for uncertain spells; clinician concern about reduced
awareness alone does not meet that boundary. This remains a no-call candidate.
The v0.8.4 development reference and scorer now implement those annotation
decisions against saved R8 responses; the [result README](../../../results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_4/dev750_r8_saved/README.md)
owns the changed target and score.

R9 revision `guide_v085_unscored_cluster_span_candidate` tells the model to
keep a cluster's within-cluster span in the exact evidence quotation, omit it
from `period`, and never default clusters to a day. `period` continues to hold
the observation window for a cluster count. The v0.8.5 reference and scorer
apply this owner decision to the saved development comparison; no R9 model
run has occurred. The [v0.8.5 result](../../../results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_5/dev750_r8_saved/README.md)
owns the replay and score.

## R8 bimonthly default (2026-09-22)

Conor selected one per two months as the default interpretation of "bimonthly",
consistent with the original development gold labels. Exact evidence retains the
word for possible later reinterpretation. An explicit source definition takes
precedence. R8 revision `guide_v07_v4_bimonthly_default` makes this semantic default
explicit in finding instructions; the JSON schema and native answer scorer are
unchanged. A fictional fixture covers the default and an explicit twice-monthly
definition. Saved predictions and earlier references are preserved; no output
repair or benchmark rerun is introduced. The annotation guide owns this convention;
the execution record owns the source checks and adjudication results.

## R8 verbatim recurrence intervals (2026-09-21, preceding revision)

Conor approved preserving vague rate denominators after reviewing the six remaining
representation flags. R8 revision `guide_v07_v3_verbatim_rates` uses the same source
duration structure for `rate.per`, `cluster.rate.per` and `seizure_free.duration`.
"Once every few weeks" retains count 1 with
`per: {"type": "qualitative", "quantity": "few weeks"}`. "Several months apart"
retains count 1 per `"several months"`. Neither creates a numeric interval or a
monthly conversion. Observation `period.duration` remains numeric.

The existing finding matcher already compares these duration strings and requires
the measurement type and counting unit to match. Its implementation is unchanged;
the existing test now checks ordinary and cluster rates against invented numbers,
ranges and different units. Fictional fixtures cover both forms. Six development
letters are reissued in an attributed adjudication snapshot; prior reference and
batch files remain preserved. No model run or test-derived decision is authorised
by this schema change. The execution record owns the updated reference counts.

## R8 vague seizure-free duration (2026-09-21, preceding revision)

Conor approved retaining vague absence durations verbatim instead of excluding
otherwise anchored seizure freedom. R8 revision `guide_v07_v2_vague_absence`
extends only `seizure_free.duration` with
`{"type": "qualitative", "quantity": "several months"}`. The string retains the
complete duration phrase, including its unit. Named intervals such as "In October"
use the same representation; do not infer a full numeric month, a date, or a
`since` anchor. At that revision, rate denominators remained numeric, range or bound
durations; the later approved recurrence extension is described above.

The existing qualitative-value comparison supports this string form. The matching
check now verifies that it cannot match an invented numeric duration or a phrase
with a different unit. The shared annotation schema is generated from the R8
model. [No-call artifacts](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r8_no_call/)
and the [portable annotation package](../../../results/letter-benchmarks/gan/seizure_finding_annotation_v0_7/)
record the revised schema, rendered instructions and source hashes. R7 requests,
scorers and saved outputs remain frozen. This preparation does not authorise an
R8 benchmark run; the execution record owns the development annotation review.

## Minimal correction, then disagreement review

Create a separate candidate for demonstrated source-representation gaps: cluster
counts within observation intervals and compound bounds/ranges. Preserve source
wording, counting units and native answer-selection rules. Handle enum spelling
separately from semantic changes. Use representative fictional checks before
spreading changes. Then review permitted rich/simple development disagreements,
distinguishing source extraction, representation, answer selection and benchmark
convention. No correction modifies the frozen requests used for timeout reruns.

Reviewed on 2026-09-22 from the saved R7 rich mixed view and the earlier r4
simple timeout-completed view. The [execution record](one_shot_execution_record.md#r7-development-failure-and-disagreement-classification-2026-09-22)
owns the counts. Schema failures are serialization against slots the schema
already has. No frozen request was modified, and this review does not authorise
an R8 run.

## Native quarter R7 candidate (2026-09-15)

Conor requested native `quarter` support and numeric reclassification of source
531. The isolated candidate `one_shot_frequency_v2_measurements_r7_quarter`,
revision `native_quarter_v1`, adds `quarter` to number, range and bound durations.
It supports rate denominators, cluster rates, observation periods and seizure-free
durations. Preserve the source unit without converting quarters to months or days.
An observed count within a quarter remains a count; cadence without an explicit
count remains qualitative. This is an explicit semantic representation decision.

The implementation is `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/one_shot_measurements_r7_quarter.py`.
Original R7, frozen requests, scorers and saved model outputs remain unchanged.
Task wording, selection examples and label forms are preserved. Annotation guide
v0.6 and its portable schema add the same unit; earlier frozen guide versions
remain available for existing batches. Reviewed migrations use separate snapshots.

[No-call artifacts](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r7_quarter_no_call/)
contain 26 fictional fixtures, rendered messages and verification. Reproduce with
`.venv/bin/python scripts/benchmarks/prepare_one_shot_r7_quarter.py`.
Verification: 26 fixtures, 32 annotation-package checks, 832 tests, Ruff and mypy
passed. Original R7 rejects the new unit, and removing quarter from the candidate's
three duration enums restores its schema. No model calls or benchmark evaluation
were performed. The execution record owns source reclassification and concurrency.

## Final R7 schema decision (2026-09-14)

R7 (`one_shot_frequency_v2_measurements_r7`, revision `simplified_dates_v1`) is
finalised as a separate no-call development candidate. It incorporates Conor's
approved simplifications and modest date collection, while preserving cluster
interval counts and compound bounds. The source is
`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/one_shot_measurements_r7.py`.
R5 and the frozen r4/r5/r6 requests and runners remain unchanged. Finalising this
schema does not freeze or authorise a new benchmark run.

| Concern | R7 decision |
| --- | --- |
| Measurement types | `rate`, `count`, `cluster`, `seizure_free`, `last_seizure`, `qualitative`; all discriminators use `type`. |
| Events | `event.type` retains the source event name, without inferring a diagnosis. `scope` is `specific`, `combined` or `unspecified`; combined requires explicit source support for events measured together. `seizure_status` is `stated`, `uncertain`, `non_seizure` or `unspecified`. |
| Finding metadata | `id`, `timing`, `period`, `condition`, `evidence`; answer links are `selected_ids`. Timing is `current`, `historical`, `future` or `unclear`. Recent findings describing the present situation are current; dates and periods retain finer timing. |
| Quantities | `number`, `range`, `bound`, `qualitative`. Qualitative quantities retain source text in `quantity`; qualitative frequencies use `frequency`. |
| Bounds | Keep `relation` values `at_least`, `more_than`, `at_most`, `less_than`. A bound may apply to a number or a range. Merge `bounded_range` into `range`, with lower/upper inclusivity defaulting to true. Preserve explicit exclusive endpoints and reject empty or reversed intervals. |
| Durations | Flatten the numeric quantity and `unit` into one object. Rate denominators are `per`. Keep positive-duration validation. |
| Clusters | `rate` contains count and per without a redundant nested type. `count` counts observed clusters; `seizures_per_cluster` counts seizures within each cluster. A cluster count needs `period` or `occurred_at`; unquantified clusters can omit both count and rate. |
| Approximation | One optional `approximate` flag on each measurement, default false. It covers any approximate numeric component, including an associated period duration. No nested approximation flags. The exact quotation retains which component was approximate; the structured flag no longer does. |
| Time points | `time` retains the source expression; `form` remains calendar or relative. Remove `precision`. Do not infer missing years, resolve relative references, compute calendar dates or derive source durations from dates. |
| Document dates | Optional `document_dates` entries contain role (`clinic`, `letter`, `unspecified`), time, form and evidence. Keep clinic and letter dates distinct. Birth dates and seizure dates are not document dates. Document dates alone do not change the no-reference answer. |
| Dated events | Optional `occurred_at` on count and cluster; last-seizure `when` becomes required `occurred_at`. Keep `since` for seizure freedom. Separate dated counts only with source support; never distribute a combined total across dates by inference. |
| Periods | Use `period.time` for the source window and optional start, end and flattened duration. Keep observation windows separate from recurring rate denominators. |
| Omission | Omit absent optional fields, false approximation and true inclusivity flags. Omission means no value extracted, not proof of source absence. The parser applies declared defaults and accepts explicit null for optional objects; compact output omits it. The existing no-reference answer still requires explicit null evidence, empty findings and empty selected_ids. |

The instructions are rendered through the existing ChatAdapter JSON envelope,
which does not require every schema property to be emitted. No provider-side
strict response-format mode was added or tested. Required IDs, evidence, answer
and links remain strict; old field spellings are not accepted as aliases. Native
task instructions, selection cases and label forms are identical to r5. Only the
output schema and its population instructions change; no semantic output repair
or automatic conversion of saved model responses is introduced.

[No-call artifacts](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r7_no_call/)
contain the rendered rich messages, schema, r5-to-r7 prompt diff, source/artifact
hashes and 23 fictional fixtures. Reproduce with
`.venv/bin/python scripts/benchmarks/prepare_one_shot_r7.py`.
The [complete fictional example](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r7_no_call/complete_example.md)
shows the agreed date and cluster structures. Additional representation fixtures
use explicitly marked placeholder unknown answers; they do not establish native
answer conversion or benchmark performance.

Remaining limits: a dated event can overlap an interval total without an explicit
relationship link; findings are not automatically additive. Relative references
such as “that date” rely on their quoted antecedents. Approximation no longer
identifies its numeric component, and removed time precision is not recovered in
this candidate. These are deliberate representation tradeoffs, not resolved
annotation or date-normalisation problems. Disagreement classification and any
candidate evaluation remain pending.

## Original one-shot to v1 to v2 prompt audit (2026-09-14)

Conor requested that v2 preserve the original one-shot prompt except for its schema
and instructions for populating that schema. R3 therefore derives its authored
request directly from `prompt_llm_extract_encode_select.py`, rather than from
`one_shot_contract.messages`. The original and frozen v1 sources remain unchanged.
This is a source comparison, not a performance attribution experiment. The reported
approximately 0.82 historical score was subsequently tied to its saved run and
reproduced by aggregate-only replay (see the thinking comparison above); the completed v1 aggregate below is 76.0% purist agreement.
These numbers alone do not establish which prompt change caused a difference.

| Component | Original one-shot | New v1 / inherited v2 r2 change | V2 r3 correction |
| --- | --- | --- | --- |
| Task | Extract every frequency fact, then select current frequency. | Replaced with a current-frequency task title and new common instructions. | Restore original task verbatim. |
| Full-note extraction | Read full note; retain all frequency facts. | Generic current-pattern instruction and new rich scope. | Restore full-note extraction instruction. |
| Per-fact fields | Require raw wording and a normalized label; omit a fact if either cannot be written. | Removed per-fact normalized labels; different generic attributes. | Adapt only field-population instruction: measurement-specific values/evidence, retain unquantifiable findings, normalize the declared answer. |
| Fact kinds | Six old kinds, including no-reference. | Changed inventory and no-reference encoding. | Use agreed measurement union; no-reference uses empty findings/links and null answer evidence. |
| Unknown/no-reference | No-reference only without usable frequency evidence; unclear frequency with seizures is unknown. | Reworded to no frequency information; mandatory answer. | Restore original usable-evidence distinction, expressed in new output fields; keep mandatory answer. |
| Seizure-free versus last-event facts | Separate these states; retain dated last seizure even when selecting seizure-free. | Specific extraction reminders removed. | Restore both original instructions verbatim. |
| Residual counts | Retain jerk count and date since last tonic-clonic seizure. | Specific reminder removed. | Restore verbatim. |
| Evidence / JSON | Exact substring when possible; one JSON object, no markdown. | New mandatory exact answer quotation and null convention. | Restore original instructions; schema instructions specify mandatory evidence and null handling. |
| Selection bridge | Follow matching cases; create new label only if no single fact is the answer. | Removed bridge. | Restore verbatim. |
| Label rules/forms | Seven rules and sixteen forms with examples. | Content retained, reorganized into separate keys. | Restore complete original label_forms block and layout. |
| Selection cases | Ten titles, instructions and worked fact/answer examples. | Only instruction strings retained; titles and worked examples dropped. | Restore all ten cases verbatim, in original order. Explain their intermediate field names in schema instructions. |
| Extra selection rules | No additional common block. | Added highest-frequency/cluster, uncertainty, wellbeing and unresolved-conflict rules. | Remove v1 COMMON entirely; original cases decide final selection. |
| Additional few-shot notes | No separate full-note examples. | Six new v1 examples; twelve different v2 r2 examples. | Remove these from model-facing prompts; retain twelve as offline schema fixtures. |
| Measurement instructions | Old fact schema. | Rich source-preservation instructions included unscoped bans on arithmetic/time inference. | Keep new measurement semantics, explicitly limit these restrictions to source measurements; original cases still govern answer arithmetic/time conversion. |
| Request envelope | DSPy ChatAdapter; self-contained JSON including note in user input. | Task in system JSON and note in separate user JSON. | Restore ChatAdapter and original input/output field names; adapt only output-schema wording. |

The ten restored cases are Usual gap; Usual rate, not a year total; Recent seizures
after a quiet spell; Not epileptic seizures; Month counts; Dated seizures; Burst
after a change; Short quiet spell after a last seizure; Overall count; and Do not
choose seizure-free while seizures continue. Their original numeric examples,
quotations and selections are preserved, including their original assumptions.
They are intermediate decision examples, not valid v2 response objects; an explicit
field mapping prevents presenting the old fields as the requested output schema.

Simple and rich use the same restored task, extraction instructions, label forms,
and complete cases. Only output schema and schema-population instructions differ.
The simple condition omits the returned inventory. Mandatory final answers, richer
measurements and omission of rationale are intentional schema differences from the
historical method. Historical parser/fallback behavior is not restored: strict
first-pass validation remains separate from prompt content and from scoring.
No historical performance-equivalence or recovered-score claim follows from this
prompt restoration. No model calls, locked-row inspection or scoring changes were
needed. Rendered requests and `original_v2.diff` live with the existing v2 no-call
artifacts; the preparation script reproduces them.

## Paired simple correction (r4)

The r3 shared instructions still requested source measurement fields, finding IDs
and empty finding lists from simple even though its schema forbids those fields.
R4 moves those field-population requirements into the rich-only instructions.
Both conditions now share the task, schema-neutral extraction instructions,
complete ten worked cases, label forms, answer-label/evidence requirements, note
and ChatAdapter envelope. Only `output_schema` and the condition-specific portion
of `schema_instructions` differ. Simple returns exactly `answer.label` and
`answer.evidence`; rich additionally returns measurements and finding links.
The worked cases remain intermediate decision examples in both conditions.

The existing parity test checks that all other payload components and the system
message are identical, and that simple's instructions contain no rich-only field
requirements. `paired_examples.json` displays the same twelve fictional notes
with matched rich/simple answers and quotations; these remain offline examples.
All 24 fictional output checks pass. No model calls or dataset inspection occurred;
prompt parity does not establish equal model performance. Frozen v1 is unchanged.

## Agreed v2 measurement design (2026-09-14)

Conor approved replacing the generic rich attributes with measurement-specific
structures. This is the active development candidate, `one_shot_frequency_v2_measurements_r4`.
The completed v1 comparison and its selected condition retain their original
meaning; they provide no performance evidence for v2. V2 r4 now has the paired
dev750 results above, but no clinical validation evidence and is not frozen for
patient evaluation.

The record must identify the event/group, represent its stated measurement and
time, preserve relevant uncertainty/conditions, and retain exact source evidence.

| Component | Agreed representation |
| --- | --- |
| Event scope | Source description; one type, explicitly combined group or unspecified seizures; explicit uncertainty/non-seizure interpretation separate from numeric uncertainty. |
| Recurring rate | Count/range/bound and a denominator quantity/unit. |
| Observed count | Count/range/bound and the stated observation interval; never silently turn it into a recurring finding. |
| Cluster pattern | Cluster cadence and seizures per cluster separately; either can be unknown. Entirely unquantified patterns retain qualitative wording. |
| Seizure-free interval | Stated duration and/or starting point, including unknown duration, scoped to the named event type. |
| Last seizure | Source date/relative wording with stated precision; no inferred dates or missing years. |
| Qualitative frequency | Original qualitative expression, without an invented numeric conversion. |
| Measurement uncertainty | Exact value, range or one-sided bound, with approximation attached. Preserve strict/inclusive bounds (more than versus at least, less than versus at most). |
| Temporal context | Current/recent/historical/future/unclear; observation period separate from rate denominator. Observed-count periods live only in the count's interval. |
| Conditions | Explicit source restriction, such as only when medication is missed, or null. |
| Answer and evidence | Mandatory native answer with quotation, linked to finding IDs; exact quotation per finding. No-reference retains empty findings/links and null answer evidence. |

Remove universal `raw_value`, generic `certainty`, `negated` and
`measurement_assertion`. No general negation/denial flag is required for frequency.
Preserve negative wording through its actual content: an upper bound, qualitative
pattern, missing value or event-scoped seizure-free interval. Do not add model
confidence, explanations of reasoning, inferred calendar dates or automatic summation
across types. Numeric conversion for the benchmark answer must not overwrite a
finding's source measurement. Native label rules and complete selection cases now come from the original one-shot
prompt, rather than the rewritten v1 common instructions; the model still declares the answer in the same response.

Implementation owner: `llm/one_shot_measurements.py`. Its separate development
runner has completed dev750; it has not replaced the frozen v1 experiment runner. Both candidate prompts share task rules,
complete original decision cases; only output schema and schema-population
instructions differ. The twelve fictional fixtures are offline checks, not prompt examples. Strict validation rejects incompatible measurement fields,
reversed ranges, zero denominators, duplicate/missing finding links and absent
answers without repair or inference. Exact quotations locate text; these checks do
not establish clinical correctness or completeness.

Reproduce preparation with `.venv/bin/python scripts/benchmarks/prepare_one_shot_measurements.py`.
The [v2 no-call artifacts](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_no_call/)
contain schemas, paired rendered prompts/diff, twelve fictional examples and 24
condition checks. They cover all six measurement kinds, approximate ranges,
one-sided bounds, nonclustered/reduced-but-not-absent patterns, event-scoped seizure
freedom, explicit conditions and no-reference outputs.
`tests/test_one_shot_measurements.py` owns the new semantic-preservation safeguards.
Verification: 830 always-on tests, Ruff, mypy (414 source files), document hygiene
and links passed. Frozen v1 component hashes remain unchanged.
The paired development assessment is complete. Review its failures before deciding
on a new candidate or whether to replace v1.
No locked-test rerun, real-data access or new model spending follows from adopting
this design; all future runs must retain the existing permission and budget rules.

## Dev750 review of the negation field (2026-09-14)

Conor challenged the generic denied-rate field and the contrived fictional example.
A lexical screen of all 750 permitted development letters, including 32 row_ok=False
letters, retrieved 5,945 absence/negation/change-marker sentence fragments. Forward
and backward proximity searches for frequency terms yielded 259 candidate contexts
(192 forward, 67 additional backward), which were reviewed. No explicitly denied
numeric seizure rate was identified that justified a generic schema field.

Negative wording is present beyond seizure-free periods, but existing structures
can preserve its meaning without a separate negation flag:

| Dev source ID | Exact excerpt | Representation |
| --- | --- | --- |
| 16961 | no more than twice weekly | Upper bound: at most two per week. |
| 1772 | These were not clustered | Qualitative pattern retaining the wording. |
| 6029 | less frequent but not absent | Qualitative frequency; do not infer seizure freedom. |
| 9496 | No generalised tonic-clonic seizures since March 2018 | Seizure-free interval scoped to this event type. |
| 763 | no change in the weekly occurrence of events | Stated weekly frequency with qualitative unchanged-pattern wording if retained. |
| 10003 | number per cluster not documented | Missing cluster count; do not interpret as zero. |

Decision: remove `measurement_assertion` and the artificial denied-numeric-rate
fixture. Revise v2 to r2, adding fixtures for observed wording patterns instead.
Preserve source quotations. No keyword rule changes model outputs or native scoring.
This is a targeted development wording review, not exhaustive linguistic annotation,
a prevalence estimate or clinical validation. The 259 are retrieval candidates, not
259 instances requiring negation. No locked/test or real-patient letters were inspected.

The [audit artifact](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_no_call/dev750_negation_audit.json)
records source/manifest hashes, split/row policy, queries, counts, exact examples and
limitations. Reproduce the screen with
`.venv/bin/python scripts/benchmarks/audit_dev750_frequency_negation.py`.
The full local candidate contexts are saved under
`runs/one_shot_frequency_v2_measurements/negation_audit/`; no model, scorer or gold
labels were used for this review. Verification passed: 24 fictional condition
checks, Ruff/mypy and 830 tests on the full rerun. The first full run encountered
an unrelated flaky API test comparing a numeric letter ID against a random request
ID; the endpoint returned 403. The verification artifact records both runs.

## V1 no-call implementation audit

The retained `prompt_llm_extract_encode_select` is a candidate source of task
instructions, not an already-proved implementation of this study. Its examples
can provide selected fact IDs without an explicit final label; its fact schema
also lacks explicit uncertainty/negation fields. The shared
`parse_structured_json_with_trace` applies payload repair before schema validation,
and `_resolve_final_label` can derive an absent answer from selected events or a
sentinel kind. That path does not by itself establish strict first-pass validity
or an unchanged model-declared answer. Preserve historical behavior and prove the
new strict rich/simple path with fictional fixtures before adopting a runner.
The new `llm/one_shot_contract.py` path requires a model-declared answer and never
calls that historical parser. Six fictional examples are rendered under both
conditions. Scope, schema and example output shape differ; task instructions,
selection guidance, label forms and example note content are shared. Rich findings
retain uncertainty and negation without requiring every finding to normalize.
Unknown requires a quotation; no-reference requires null answer evidence and an
empty inventory. Missing answers, duplicate JSON keys, extra fields, invalid IDs
and malformed labels fail without salvage. Quote mismatch is separately reported;
absent required evidence makes the response unusable.

The native adapter projects the untouched answer through existing Gan normalization
and Purist/Pragmatic mapping only for scoring. It preserves the original output.
Unknown/no-reference remain distinct outputs but share the native unknown score;
cluster scoring uses cadence, and native range/multiple/time conversions remain
unchanged. The existing weekly cutoff behavior is covered by a fixture.
No native scorer or historical parser was changed.

No-call artifacts: `runs/one_shot_frequency_v1/no_call/` contains rendered messages,
schemas, their diff, fictional fixtures and checks. This local artifact directory
also owns the development plan, frozen configuration, requests, responses, attempts
and aggregates. Tests in `tests/test_one_shot_paper.py` cover the new first-attempt,
split, budget and all-note scoring obligations.
