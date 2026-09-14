# One-call extraction evaluation protocol

Execution decisions in progress, 2026-09-14. Owner: Conor Brown.
Aligned with the [paper outline](../../../publications/jamia-one-shot/README.md)
and [roadmap](../../plans/ACTIVE_ROADMAP.md). Conor authorised synthetic DeepSeek API work on 2026-09-13 within a total
US$10 ceiling, subject to the preparation and freeze requirements below. Real-data
permission remains pending. Longitudinal work is postponed.

## Current plan: timeout reruns and expanded annotation (2026-09-14)

Conor approved the following priorities after the r5 dev750 review. This amendment
supersedes the earlier decision to require no assertion-level annotation. It records
planned work, not completed reruns, annotations or clinical validation.

### Timeout reruns

Rerun each timed-out request from r4 simple (14) and r5 rich (40), using a
600-second limit: 54 condition-specific requests, not only the seven letters where
both timed out. Preserve the original prompt, schema, model settings, scorer and
row policy; no representation correction is included in these reruns. Save new
attempts separately with links to the originals. Keep the original first-attempt
aggregate unchanged. Report a separately named timeout-completed view that uses
the new attempt only for each originally timed-out request, with all 750 letters
in each condition and residual failures retained. This is a mixed-attempt view,
not a fresh first-pass experiment at 600 seconds. Do not rerun returned wrong,
schema-invalid or envelope-invalid outputs under this permission.

Measure time per letter, distinguishing original and rerun duration and cumulative
work for repeated requests. Include all costs in the existing US$100 study ceiling,
including the separately authorised r6 test450 run; reconcile current spending and
outstanding reservations before calls. Completion reliability is not a separate
research priority. Conor expects approximately 0.88 Purist performance for both
conditions; test that expectation using the existing native agreement measure,
without relabelling it as a new F1 metric or tuning to the expected value.

### Completed timeout reruns (2026-09-14)

All 54 authorised requests returned at the 600-second limit: 14 r4 simple and
40 r5 rich, with no remaining transport failures. Frozen request bodies, model,
thinking enabled/low, 24,000-token limit, native scorer and no-repair policy were
unchanged. Original artifacts were hash-verified and preserved. This is a
mixed-attempt dev750 view, not a fresh all-row run at 600 seconds.

| Condition | Purist answer | Pragmatic answer | Strict Purist | Strict Pragmatic |
| --- | --- | --- | --- | --- |
| r4 simple | 658/750 (87.73%) | 673/750 (89.73%) | 658/750 (87.73%) | 673/750 (89.73%) |
| r5 rich | 658/750 (87.73%) | 678/750 (90.40%) | 656/750 (87.47%) | 676/750 (90.13%) |

Rich-minus-simple Purist answer difference: 0.00 percentage points
(paired 95% interval −1.73 to +1.60); Pragmatic: +0.67 points (−0.80 to +2.27).
Original non-timeout failures remain: each condition has two invalid envelopes
and one invalid target label; rich also has two schema failures. R6 development
results remain original first attempts, including 29 timeouts; their presence
in the replay aggregate does not make them a matched timeout-completed comparison.
No locked rows were inspected or executed for this rerun work.

Mean rerun request time was 11.96 seconds for simple and 32.07 seconds for rich.
Across all 750 letters, mean cumulative original-plus-rerun request time was
41.01 and 121.29 seconds respectively. These sum request durations, not concurrent
batch wall time. Per-request original, rerun and cumulative durations are retained.
Conservative rerun charge: US$0.5514081; cumulative study charges including the
completed r6 test450 run: US$29.1822888 of US$100. No attempts were outstanding
at reconciliation.

Runner: `scripts/benchmarks/rerun_thinking_timeouts.py` (`prepare`, `run`, `replay`).
Raw attempts and original-request links: `runs/one_shot_thinking_r4_r5_r6/dev750/timeout600/`.
The [aggregate and timing artifacts](../../../results/letter-benchmarks/gan/one_shot_thinking_r4_r5_r6/dev750_timeout600/)
retain all-row denominators and residual failures. Offline replay was byte-identical.
Verification: 831 always-on tests, Ruff and mypy (418 source files).

### Minimal correction, then disagreement review

Create a separate candidate for demonstrated source-representation gaps: cluster
counts within observation intervals and compound bounds/ranges. Preserve source
wording, counting units and native answer-selection rules. Handle enum spelling
separately from semantic changes. Use representative fictional checks before
spreading changes. Then review permitted rich/simple development disagreements,
distinguishing source extraction, representation, answer selection and benchmark
convention. No correction modifies the frozen requests used for timeout reruns.

### Main next research step: full seizure-finding annotation

The target is all dev750 letters, including row_ok=False, with a complete inventory
of task-relevant seizure findings read from each full source letter. Annotators must
not limit their inventory to r5 outputs or to the existing selected answer. The
existing Gan answer reference remains separate and retains its scoring semantics.

Codex will author the guidelines here in this protocol, with worked annotation
examples in the existing study artifact area. The guide must define:

- Included event types and measurement scope; current, historical and recent facts;
  explicit absence, uncertainty, conditions and legitimate no-reference states.
- Finding identity and repeated mentions; counting units; counts versus rates;
  cluster components; bounds, approximation and vague quantities; observation
  periods, unresolved anchors and time precision; exact source evidence and context.
- Source statements versus derived benchmark interpretations, without silently
  converting a source count or last-event time into a recurring rate.
- Annotation output format, ambiguous cases, review and adjudication records,
  and whole-finding matching with attribute-level error diagnostics.
- Finding correctness and completeness denominators, one-to-one matching,
  duplicate handling, empty inventories and unusable outputs. Report answer
  agreement independently and keep source support separate from quotation occurrence.

Conor will obtain annotations from Gemini. Codex will review them against the full
letters, first piloting a representative set to refine the guide, then reviewing
the full development set. Retain Gemini's originals, corrections, unresolved
judgements and model/prompt/reference versions. Agree pilot acceptance criteria
before scaling. Gemini output and Codex agreement alone do not establish clinical
expert validation; unresolved clinical interpretations need Conor/domain review.
These annotations are development references, not untouched holdout evidence.
No new model calls or paid Gemini execution are implied by defining the guidelines.

### Prove seizure annotation, then extend all four families

If the seizure annotation approach works well, extend the same process to the
four categories: seizure findings, medications (the existing Prescription family),
diagnoses and investigations. Define family-specific scope and matching rather
than reusing seizure quantity rules. Compare seizure-only rich extraction against
all-four-family extraction on the same permitted letters, holding the model,
runtime, original frequency-label rules and shared clinical content fixed. Retain
the original frequency answer as the common endpoint to test whether expanded
task scope harms that task. Score additional findings only against the reviewed
family references; freeze the concrete comparison and analysis before execution.

Conor plans to provide the reviewed dataset and guidelines to Yujian Gan and ask
whether the King's College London Hospital annotators are willing to use the full
annotation approach on real patient letters, ideally across all four categories.
This is planned collaborator outreach by Conor, not confirmed participation or
permission to send data. Real annotation and evaluation need an agreed scope,
source-use/sharing permissions, exposure history and clinical review procedure.
Existing aggregate-only holdout safeguards remain in force; any additional clinical
annotation access must be explicitly arranged with the custodian, never inferred
as permission to inspect sealed prediction failures for development.

## R6 live test450 comparison (2026-09-14)

Conor authorised a fresh r6 test450 run, compared side by side with the saved
20260910 aggregate, and an increased timeout. The new request timeout is 600
seconds, up from 300 seconds in the completed dev750 comparison. The historical
DeepSeek model spec defaulted to 600 seconds and the saved command had no override;
the old aggregate did not record timeout, so this value is reconstructed from the
pre-migration code and protocol, rather than confirmed by a per-run timeout log.

`scripts/benchmarks/run_r6_test450.py` verifies the frozen development source and
data identities. It retains the r6 prompt, original schema/raw_model parser,
current strict envelope handling, thinking enabled/low, 24,000-token limit and
submitted temperature 0. It uses concurrency 12 and no retries or automatic adapter
fallback. The historical command used synchronous transport; this new runner uses
concurrent HTTP requests. These execution differences remain explicit.

All 450 locked notes are included. Tools/runners may read them to execute the
frozen requests and score outputs, but no identifiers, notes, predictions or
failures are exposed for inspection. Only aggregate results are reported. Replay
rows contain only source_row_index, prompt_version and raw_output; provider
responses remain local. There is no holdout row-diagnostic report. Historical
scores are 369/450 Purist and 385/450 Pragmatic. This is a reused-holdout replication
comparison, not fresh generalization evidence, and cannot authorize tuning on rows.

The US$100 cumulative ceiling includes US$24.255057 in prior conservative study
charges. Before calls, the runner reserves the worst-case cost of all remaining
requests. Requests and analysis remain frozen for replay. Run artifacts are under
`runs/one_shot_original_r6/test450_timeout600/`; the comparison aggregate is written
to `results/letter-benchmarks/gan/one_shot_original_r6/test450_timeout600/`.

## Thinking-enabled r4/r5/r6 development comparison (2026-09-14)

Budget amendment: after 1,782 attempts (594 per condition), the initial US$20
safeguard stopped execution at a conservative US$19.7474916 cumulative bound.
Conor raised the ceiling to US$100 and authorised resuming the remaining 468
unstarted calls. The frozen plan and all completed attempts, including 78 timeouts,
are preserved. `scripts/benchmarks/resume_one_shot_thinking.py --budget 100`
verifies the original source/request identity before applying the budget-only
override. The active authorization and its history are saved alongside the run.
No completed attempt was retried in that original run. The later authorised
r4/r5 timeout reruns above are separate attempts. The US$20 values below describe
the initial cap.


Conor authorised r4 simple, r5 rich and r6 original on dev750 and raised the total
DeepSeek study budget to US$20. Thinking enabled, reasoning effort low and a
24,000-token response limit are now the defaults for new one-shot study runs.
Frozen earlier runners and request identities are unchanged. Temperature 0 is
submitted to match the original configuration; DeepSeek documents that temperature
is ignored in thinking mode. Model alias: `deepseek-flash`, provider-documented
DeepSeek-V4.1-Flash. All three use identical provider settings, no local response
cache, concurrency 12, 300-second timeout and no retries or automatic adapter
fallback calls. Condition order rotates between letters. The native API receives
the rendered ChatAdapter messages directly, with text output.

| Condition | Prompt/output | Scoring |
| --- | --- | --- |
| r4 simple | Unchanged r4 answer-only request. | Independent declared answer and whole-output strict agreement. |
| r5 rich | Original task/cases, revised measurement schema and schema-population instructions. | Independent declared answer, complete-record validity, and strict end-to-end agreement. |
| r6 original | Original `gan_llm_extract_encode_select` prompt and original schema verbatim. | Original `raw_model` parser and native selected-label scorer; legacy parser semantics remain explicit. |

R5 has one observation_period field for all findings; recurring-rate denominators
remain separate. It allows unquantified clusters, qualitative numeric quantities,
and week/hour/minute/second time precision. Durations must remain positive and
unknown answers must link to findings. A schema-population example explains unknown
answer links. These changes do not modify the historical task or selection cases.
Sixteen fictional r5 outputs cover the changes, and the test explicitly proves
that invalid additional findings do not invalidate an independently valid answer.
A missing answer is never inferred from findings. R4 and r5 answer checks both use
the same required label/evidence contract; quotation exactness is not added as a
new label-scoring condition. The original r6 parser does not implement this newer
answer-only contract, so its validity counts have different semantics.

The runner is `evaluation/one_shot_thinking.py` (prepare/run/replay). It includes all
750 development rows, including row_ok=False, with 2,250 scheduled first attempts.
Plan, all source hashes, requests, responses, usage and development diagnostics
are local under `runs/one_shot_thinking_r4_r5_r6/dev750/`. Rendered empty-note
requests and fixtures are under `results/letter-benchmarks/gan/one_shot_thinking_r4_r5_r6/`.
Cost accounting reserves each input-byte bound and full 24,000-token output before
starting it, then uses returned token usage at peak cache-miss prices. Prior study
spending is US$4.4273178; the runner cannot exceed the US$20 cumulative ceiling.
No prompt or scorer changes are permitted during this comparison. Prior synthetic
development exposure remains disclosed; dev750 scores are not holdout replication.

Historical replication evidence: the located 20260910 aggregate reports 369/450
Purist and 385/450 Pragmatic, thinking enabled, low effort and 24,000 tokens. The
current original-prompt source is byte-identical to its pre-migration snapshot.
Aggregate-only replay of the saved outputs through the current original parser and
scorer reproduced both counts exactly, with zero parse failures. See
[replay aggregate](../../../results/letter-benchmarks/gan/one_shot_original_r6/replay.aggregate.json).
The removed protocol remains recoverable in the pre-migration snapshot; this
protocol owns its current interpretation. No holdout identifiers, notes or failures
were inspected. This establishes replay compatibility, not fresh-call determinism.
Thinking alone has not yet been isolated as the cause of prior score differences:
output budget, schema, parser and evaluation population also differed.

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

### Paired simple correction (r4)

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

### Paired dev750 execution (2026-09-14)

Conor authorised running both r4 prompts on all dev750 rows. The separate
`evaluation/one_shot_measurements_dev.py` runner supports development only; it
cannot execute a test or patient partition. The prepared identity is saved under
`runs/one_shot_frequency_v2_measurements_r4/dev750/plan.json`. All 750 development
IDs are included regardless of `row_ok`, with one first attempt per condition
(1,500 calls), alternating condition order between letters. The model is
`deepseek-flash` (provider-documented DeepSeek-V4.1-Flash), temperature 0, thinking
disabled, maximum 4,096 output tokens for each condition, concurrency 6 and a
180-second timeout. The provider response model is saved for every call.

The ChatAdapter envelope uses text output, rather than v1's API JSON-object mode.
Exactly one `structured_json` section is extracted, with an optional `completed`
marker; bare JSON, duplicate sections and truncated responses fail. Its JSON is
then checked by the unchanged r4 validators. No retries, fallback calls, syntax
repair, semantic repair or answer inference are allowed. Raw responses and
extracted JSON remain separate. This transport setting follows the restored
prompt and is shared between conditions; it differs from frozen v1.

The existing native purist/pragmatic scorer and paired analysis are reused.
Every scheduled row remains in the denominator; failed outputs count as wrong.
Exact quotation diagnostics are reported separately from label agreement.
These are previously exposed synthetic development data, not held-out evidence
or validation of the richer measurements. No test-row failures are inspected.
The total US$10 study budget includes v1's US$1.1732 conservative charge. Each
new call reserves its input-byte upper bound plus maximum output charge; returned
usage releases that reservation to peak cache-miss prices (US$0.30/1M input and
US$1.20/1M output, checked 2026-09-14). Execution stops before exceeding the budget.
Interrupted requests are never silently resent. Replay uses saved first responses
without model access.

Completed: all 1,500 requests returned, with no transport, envelope or truncation
failures. Rich purist agreement was 521/750 (69.47%) and simple 570/750 (76.00%);
pragmatic was 564/750 (75.20%) and 620/750 (82.67%). Rich had 72 schema failures
and six invalid labels; simple had ten invalid labels. Failures count as wrong.
The paired purist difference was −6.53 points (95% CI −8.80 to −4.40), pragmatic
−7.47 points (−9.73 to −5.33). These are synthetic development results only.
Offline replay was byte-identical. Conservative run cost was US$3.2541282,
US$4.4273178 including v1. Detailed results and metadata are owned by the
[dev750 result artifact](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r4/dev750/README.md).
The prompt and validators were not changed in response to these outputs.

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

## Confirmed execution decisions (2026-09-13)

- Main synthetic evaluations use the DeepSeek API from Conor's current computer.
  The total API budget is US$10 across development and evaluation, including failed
  attempts and any retries. Reserve the frozen comparison cost before development;
  stop before the cap rather than silently reducing the evaluation denominator.
  Exact model identifier, current pricing, decoding and call limits remain to be
  pinned before calls.
- Supplementary local runs use Conor's Dell XPS 15. Hardware, model and runtime
  feasibility remain to be recorded; these are distinct execution conditions.
- Conor's collaborator owns the cluster and local DeepSeek execution on real patient
  data. No cluster budget is required from this task. Written custodian permission
  and the exposure/reference metadata remain pending with Conor.
- Two real-data runs are planned: one-call single-label seizure-frequency extraction
  and a separate extension across several clinical families. The extension's exact
  families, fields, reference availability and analysis must be specified and frozen
  before either real run; no adaptation from the first run's sealed errors is allowed.
  Gan's existing single-frequency reference cannot score the additional families.
  This original decision did not authorise additional annotation; the current
  dev750 annotation amendment above now supersedes that restriction for development.
- Develop on dev750, then run one frozen evaluation on test450 with aggregate-only
  reporting. Conor confirmed this policy; record prior exposure and retain all
  eligible rows, including row_ok=False. train300 remains outside this permission.
- Report agreement and paired rich-minus-simple differences with 95% intervals.
  Do not pursue a clinical adequacy threshold, equivalence or non-inferiority claim.
  The exact interval implementation and development selection rule still need to
  be specified before the evaluation freeze.

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

## Question and scope

Can a locally deployable model preserve the established seizure-frequency answer
while returning a richer, inspectable evidence record in one clinical inference
call? The primary outcome uses the existing expert-selected current-frequency
label. The richer record is a model-produced inventory, not private reasoning and
not a newly gold-annotated clinical-fact benchmark.

The core study comprises the primary real-letter frequency result, controlled
synthetic rich/simple contrast, contract reliability, actual runtime and one compact
configuration example. The separately planned multi-family patient extension needs
its own prespecified fields and reference limits within this protocol. Hybrid/rule-heavy comparators, longitudinal evaluation,
optimizer search, authoring-effort and participant usability studies are out of
scope. Historical results remain context, not results of this method.

## Data and reference

| Source | Reference and intended role | Use conditions |
| --- | --- | --- |
| Real Gan 300 | Existing expert-selected current-frequency label; primary clinical-task evaluation, native Purist and Pragmatic companion. | Confirm authority, reference version, prior development/evaluation exposure and eligibility before access. Real(300) remains sealed. Do not substitute the synthetic split permissions. |
| Synthetic Gan | Existing single-label reference; controlled prompt/model comparison. Historical study union is 1,200 letters, dev750 + test450, including row_ok=False. | Develop on permitted dev750 only. Freeze reuse/evaluation policy before any test450 run; train300 is not implicitly available. Disclose prior use of every evaluated partition. |
| ExECT | Expert-annotated synthetic four-family inventory; one small descriptive configuration example. | Select from permitted dev140; retain native units and scoring. No new test60 run or model leaderboard is needed. |

The [dataset description](../shared/dataset_description_2026-08-26.md) owns the
historical corpus counts; counts for this study must come from its authorised
manifest. The [holdout policy](../../benchmarks/holdout-is-aggregate-only.md)
continues to apply. Never inspect sealed identifiers, notes, quotes, predictions
or errors during development. A custodian/execution process may produce permitted
aggregates under a separately approved frozen run procedure.

Use all eligible real letters, targeting the existing 300 rather than selecting
easy or successful cases. Record any exclusions with prespecified, prediction-free
reasons and the resulting denominator. Patient linkage and prior exposure require
metadata confirmation; if independence cannot be established, disclose it and do
not claim patient-level generalisation or unsupported precision. The existing
reference does not support full inventory recall, precision or completeness.

## Conditions and output

| Condition | One response contains | Interpretation |
| --- | --- | --- |
| Rich, primary | Zero or more scoped seizure-frequency findings with type/value, relevant seizure type, temporality, uncertainty/negation and exact quotations; one native task answer linked to relevant findings where applicable. | Tests the richer extraction contract. Any brief stated selection basis is visible output, not evidence of internal reasoning. |
| Simple, controlled | One native task answer and supporting quotation; no emitted finding inventory. | Primary paired comparator for the cost and task effect of the richer contract. |
| Holgate, contingent | Original supplied task and output form, parsed under its documented constraints. | External whole-prompt comparator; not an isolated feature ablation. |

Freeze the concrete schema and scope before calls. A valid zero-finding response
is allowed when appropriate; it is not permission to omit a required answer or
fabricate evidence for a no-reference state. Define required fields and the legal
representation of absent evidence for each sentinel in the no-call fixtures.

Match rich/simple note text, model and revision, decoding, runtime, label and
selection definitions, uncertainty convention, evidence obligation and examples'
clinical content. Record exact paired edits to scope instructions and schema-shaped
example outputs. Use the same development-chosen output cap and timeout, generous
enough for rich output; report truncation and realised costs. Keep the constrained
decoding policy fixed while recording each condition's schema. This contrast
changes scope and output together; any selection-basis field must be recorded as
part of that intervention. Additional component ablations are not required.

Conor's supervisor is obtaining Holgate's full Llama 2 prompt. Record supplied
version, provenance, message roles, examples, output requirements and original
runtime/adaptation assumptions. Confirm use and quotation permissions. Do not
reconstruct or substitute it. Compare supplied and own prompts on the same chosen
model and notes where feasible; a Holgate/Llama 2 versus newer-model comparison
alone confounds prompt and model. Any adapted external prompt is separately named.
Missing comparator evidence fields remain unavailable, never manufactured.

## One-call and failure accounting

One-call means one clinical inference request per note, not zero demonstrations.
The model supplies both findings and final answer. Deterministic handling may
parse, check types, validate quotation locations and serialise values without
changing their meaning. It must not choose a different event, resolve ambiguity,
normalise a clinical value semantically or invent an answer. Audit the actual
prompt/parser/adapter path before adopting an existing runner.

The primary condition uses first-attempt output with no repair call. Preserve raw
responses and failure categories: no response/timeout, truncation, invalid syntax,
invalid schema, invalid target label and absent required evidence. Apply a fixed
precedence for mutually exclusive unusable-response counts; diagnostic flags may
overlap. Schema-invalid or otherwise unusable responses count as incorrect in the
all-note task denominator, even if a plausible label can be salvaged from text.
A correct native unknown/no-reference label is not a system refusal; preserve those
states in scoring and coverage. Exact quotation checks are separately reported; they do not adjudicate entailment.

Any deterministic format-only recovery is a separately reported secondary view,
with original validity, recovered count and remaining failures. An extra model
repair request is outside the primary one-call condition and must show total calls
and cost. Operational retries cannot replace failed first attempts invisibly.
Clinical repair or deterministic clinical selection constitutes another method,
not a format fix in this study.

## Outcomes and analysis

| Outcome | Denominator and report | Outline exhibit |
| --- | --- | --- |
| Primary real-letter task agreement | Native Purist correct / all eligible scheduled real notes, unusable output incorrect. Pragmatic companion; no pooled cross-corpus score. | Table 2 |
| Usable-answer coverage | Usable responses / all eligible scheduled notes. Conditional agreement is secondary and never replaces all-note agreement. | Table 2 |
| Controlled task difference | Rich minus simple all-note Purist on the same authorised synthetic notes; Pragmatic companion, paired wins/losses/ties and uncertainty. | Table 3 |
| First-pass contract validity | Schema-valid responses / all scheduled notes; distinguish responses received from absent responses. | Table 4 |
| Exact-source quotations | Exact matches / all schema-required quotation slots in received outputs, counting missing required quotes as failures; also notes with every required quote exact / all scheduled notes. Report no-evidence states separately, never as vacuous successes. | Table 4 |
| Rich record description | Finding counts and declared types/qualifiers among schema-valid outputs, with usable counts and exclusions. | Table 4 |
| Execution | Failure categories, truncation, any secondary recovery, call counts, latency and tokens; actual model revision, quantisation, engine, hardware and concurrency. | Table 4 |

A matching quote proves location only. The current annotation plan above adds a
source-first dev750 inventory reference and review of emitted findings so that
finding correctness and completeness can be measured separately. Until that
reference and its matching rules are reviewed, schema validity, quotation occurrence
and finding counts remain technical/descriptive measures, not clinical finding
precision or recall. Real finding measures depend on the clinical annotations
actually obtained. Sealed failure reporting remains mechanical and aggregate-only;
the development annotation plan does not permit inspection of sealed failures.

The primary real endpoint and primary controlled contrast above are fixed. Report
absolute scores and paired differences with 95% intervals under a prespecified
analysis implementation. Use patient clusters where known; otherwise use the
established sampling unit with the independence limitation explicit. Respect known
synthetic source families. Freeze the interval method, random seed if resampling,
and handling of small strata before evaluation. Do not choose an analysis after
seeing which makes a difference persuasive. Other slices are descriptive.

The real cohort target is 300 eligible existing letters, subject to authority and
eligibility; it is not a newly powered sample-size claim. Report attainable
precision rather than inventing a larger recruitment target. Absence of a
statistically clear rich/simple difference does not establish equivalence or
non-inferiority. Such a claim requires a justified margin and analysis agreed
before runs. Conor selected descriptive performance reporting without numerical adequacy
thresholds or a non-inferiority claim. Report measured performance, not that the
system is clinically good enough. This preserves the roadmap's capability question without requiring a new
clinical validation study for the planned descriptive paper.

## Prespecified synthetic execution and analysis

The initial main condition is `deepseek-flash`, provider-documented DeepSeek-V4.1-Flash,
via `https://api.deepseek.com/chat/completions`. The provider offers a mutable alias,
not an immutable weight revision: record the documented version and every returned
model identifier without claiming exact weight reproducibility. Both prompts use
thinking disabled, temperature 0, JSON-object output (schema supplied in the prompt),
4,096 output tokens, 180-second timeout and concurrency six. No hidden SDK retries,
format recovery, semantic repair or second clinical request is permitted.

Pricing checked 2026-09-13 against [DeepSeek's official table](https://api-docs.deepseek.com/quick_start/pricing/):
reserve US$0.30/million input and US$1.20/million output tokens, the peak cache-miss
rates. This deliberately overestimates off-peak/cache-hit charges. Preflight bounds
input tokens by rendered UTF-8 bytes plus framing allowance and output by its cap;
all pending requests must fit before a phase starts. Missing usage or interrupted
requests keep their full reservation. Development is capped at US$1, retaining at
least US$9 for the comparison within the US$10 total.

Develop on 20 dev750 notes chosen without predictions by ascending
SHA-256 of `20260913:<source_row_index>`. Include row_ok=False if selected. Run both
conditions once on each note. This is a technical development comparison, not a
representative clinical-performance estimate. One model/runtime is prespecified;
freeze it unchanged if first-pass technical checks pass. Any development correction
requires a recorded new version and new checks, never an invisible replacement of
first attempts. Select the rich frequency condition for later real evaluation
before viewing synthetic test results; the real runtime still needs its own freeze.

The test phase schedules both conditions for every test450 note, including
row_ok=False. Freeze dataset/manifest, prompt, parser, native scoring, analysis and
runtime hashes before execution. Save full local requests/responses and separate
attempt records; the holdout replay file retains only source ID, prompt version and
raw output. Publish aggregate results only. No new test failure inspection or tuning
is permitted. Earlier studies used both partitions; describe this as reused-holdout
evaluation, not a fresh untouched test cohort.

Use Wilson 95% intervals for absolute all-note agreement. Use 10,000 paired
letter-level percentile bootstrap replicates, seed 20260913, for rich-minus-simple
agreement (sorted draws 250 and 9750, one-based). Report wins, losses and ties.
Patient and synthetic source-family linkage fields are absent from the supplied
row schema, so these intervals assume independent letters; they do not establish
patient/family-level precision. Do not infer clusters from clinical note text.
No inferential subgroup analyses are planned; degenerate bootstrap intervals are
explicitly flagged. Unusable responses count as incorrect even for unknown gold.
Failure precedence is truncation, no response, invalid syntax, invalid schema,
invalid target label, absent required evidence; transport error types are also
reported. Required quotation slots are countable in parseable object outputs;
report unparseable/absent output separately and count it as failure in the all-note
quotation measure. Empty no-evidence states never count as exact-quote successes.

## Model panel and execution order

1. Complete no-call rich/simple rendering, schema and native-adapter fixtures,
   including numeric, uncertain/no-reference, multiple-statement and unusable cases.
   Inspect exact prompts; do not reopen sealed notes.
2. Confirm feasible local runtime candidates and budget, then prespecify a compact
   panel with the same contract. An older model may provide capability context if
   it is feasible and matched; no historical model list is mandatory. Pin revision,
   quantisation, engine, context and decoding. Do not infer hospital deployment.
3. Use permitted synthetic development to settle prompts and output limits. Record
   selection and all attempts; development comparisons are not held-out results.
4. Freeze conditions, scorer/adapter, row policy, panel and analysis before the
   authorised synthetic evaluation. Report runtime changes as distinct conditions.
5. Freeze the selected real-evaluation condition before any authorised real run.
   Do not revise it from sealed errors. Report prior exposure and permitted
   aggregate outcomes, whether favourable or not.
6. Complete one compact ExECT specification-to-component change on development
   examples with the same model/decoding. Show edited fields, scope, evidence rules
   and examples, native descriptive checks and visible regressions. It demonstrates
   configurability, not clinician usability, reduced expertise or generalisation.

## Completed synthetic comparison (2026-09-13)

The fixed development comparison made 40 calls, all usable, with exact quotations
in every required slot. Development Purist agreement was 12/20 rich and 10/20 simple.
The condition was frozen unchanged before the 900-call test450 comparison. No
repair calls, operational retries, transport failures or truncations occurred.
The frozen rich frequency condition was selected before test evaluation; the
collaborator's real-data runtime and permission remain pending.

| Test450 measure | Rich | Simple |
| --- | --- | --- |
| Purist agreement, all 450 notes | 342/450 (76.0%; 95% CI 71.8–79.7%) | 334/450 (74.2%; 95% CI 70.0–78.0%) |
| Pragmatic agreement, all 450 notes | 368/450 (81.8%) | 360/450 (80.0%) |
| Usable responses | 446/450 | 447/450 |
| Schema-valid responses | 448/450 | 450/450 |
| Exact required quotations | 1,547/1,558 | 423/429 |
| Notes with every required quote exact / all notes | 420/450 | 423/450 |
| No-evidence states, separately reported | 20 | 21 |
| Median request latency | 1.75 seconds | 0.97 seconds |
| Completion tokens | 160,864 | 22,024 |

Rich won 16 paired Purist comparisons, lost eight and tied 426: +1.78 percentage
points, paired 95% CI −0.44 to +4.00 points. This does not establish superiority,
equivalence or non-inferiority. Rich had two invalid-schema and two invalid-label
responses; simple had three invalid-label responses. All remained in the denominator
as incorrect. Twenty row_ok=False notes were included. No sealed failures were
inspected. Quote exactness establishes source location only.

The peak-price charge estimate is US$0.0506 development plus US$1.1226 evaluation,
US$1.1732 total, below the approved US$10 ceiling. These are conservative token-based
estimates, not a provider invoice; cache/off-peak billing can be lower.

The [artifact directory](../../../results/letter-benchmarks/gan/one_shot_frequency_v1/)
contains fictional rendered requests/schemas, the matched diff, development aggregate,
pre-test freeze, [test aggregate](../../../results/letter-benchmarks/gan/one_shot_frequency_v1/test450.aggregate.json)
and verification record. Private requests/responses and attempt logs remain in
`runs/one_shot_frequency_v1/`. Offline replay reproduced the aggregate exactly and
left the attempt ledger unchanged. The new checks and full always-on suite passed
(828 tests), as did Ruff, mypy and document hygiene. No deep tests were needed for
these new first-attempt/split safeguards; the local client was checked with a
fictional loopback stub, not an actual Dell model.

## Supplementary local preparation

`runs/one_shot_frequency_v1/local_preparation/` contains the same 20-note synthetic
development bundle and an explicit runtime metadata template. The no-install
`scripts/benchmarks/run_one_shot_local.py` client accepts that bundle and a completed
runtime file. It preserves requests/responses, performs no retries or repair and
uses the same strict parser and all-note scoring. A loopback stub check passed with
two fictional responses; this verifies client wiring only, not local model behavior.

From the repository root in the Dell's `.venv`, after supplying its actual server,
model revision, quantisation, hardware, engine/version and non-thinking parameters:

```sh
python scripts/benchmarks/run_one_shot_local.py \
  --bundle runs/one_shot_frequency_v1/local_preparation/synthetic_development_bundle.json \
  --runtime runs/one_shot_frequency_v1/local_preparation/runtime.template.json \
  --output runs/one_shot_frequency_v1/dell_development
```

The template intentionally has unfilled runtime fields; no Dell server or model has
been assumed. Report its results as a separate supplementary development condition.
The historical `run.py` route includes different clinical handling and does not
substitute for this paper-specific client.

## Proposed multi-family patient extension (not frozen)

After proving the expanded seizure annotation on dev750, extend annotation and
extraction to the four families below. This staged development plan replaces the
earlier descriptive-only extension proposal. Reuse the existing ExECT family names. Conor/collaborator still need to confirm the scope and
available reference metadata without inspecting sealed rows.

| Family | Proposed returned fields | Reference boundary |
| --- | --- | --- |
| Diagnosis | Named diagnosis, certainty, negation, timeframe and exact quotation | Score only against an authorised diagnosis reference if available. |
| Seizure frequency | Measurement-specific findings with event scope, timeframe, bounds/approximation and quotations; one declared current-frequency answer | Existing Gan single-label scoring applies only to the declared answer. |
| Prescription | Medication name, dose/unit, schedule, current/planned/stopped status and quotation | Do not infer administration or adherence from a prescription. |
| Investigations | Named investigation, performed/planned status, reported result, timeframe and quotation | Do not infer a normal result from missing documentation. |

Absent findings are empty family lists, not assertions that the patient has no
condition. Preserve uncertainty and family-specific meaning: diagnosis negation
may be relevant to that separate family; the frequency record has no generic negation
field. Distinguish these clinical states from execution failure. Do not derive additional-family accuracy, inventory recall or clinical
completeness from the Gan frequency label. Until additional references are confirmed,
report schema, quote and output counts descriptively; do not invent family
accuracy. Development annotation is now planned under the amendment above.
Patient annotation and data sharing still require explicit arrangements. Freeze exact
schemas, examples, scope, runtime and analysis before either patient run; neither
run may be tuned from the other's sealed outputs.

## Readiness and reproducibility

| Decision still required | Owner | Evidence needed before dependent execution |
| --- | --- | --- |
| Real-set authority, prior use, reference version, linkage and eligibility | Conor with custodian | Recorded metadata/access decision; no sealed-row inspection to resolve it. |
| Rich/simple contract and synthetic analysis | Implemented and verified | Rendered artifacts, four new safeguard tests, frozen configuration and completed aggregates linked above. |
| Supplementary local runtime | Conor with implementation contributor | API configuration and comparison complete; Dell access/runtime details pending. Collaborator owns real-data cluster runtime. |
| Real aggregate-only procedure | Conor with evaluation owner | Synthetic manifest/freeze and prior-exposure disclosure recorded; written real-data authority and execution metadata remain pending. |
| Interval implementation and selection rule | Implemented and verified | Prespecified Wilson/paired bootstrap analysis complete; rich frequency condition selected before test results. No adequacy or non-inferiority claim. |
| Seizure-finding annotation | Codex guidelines/review; Conor obtains Gemini annotations | Reviewed source-first dev750 inventories, matching rules, guide versions and unresolved judgements. |
| Four-family extension and clinical annotation | Conor with Yujian Gan/custodian and implementation contributor | Successful seizure annotation pilot, reviewed development references, agreed clinical annotation participation/permissions, and frozen comparison before real runs. |
| Holgate prompt and permitted use | Conor's supervisor | Original supplied material and conditions; blocks this comparator only. |

Every run records dataset/version, split, source hashes, selection and row policy,
reference and scorer versions, model/runtime, rendered request and component hashes,
raw attempts, first-pass failures, repair policy, replay mode, exclusions,
denominators and costs. Keep extraction, format handling and scoring separable.
The outline's Figure 1 shows that path; Table 1 shows data/reference roles; Figure 2
shows the configuration change. Fill tables only from reviewed run artifacts.
