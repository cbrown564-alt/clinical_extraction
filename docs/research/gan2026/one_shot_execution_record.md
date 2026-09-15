# One-call study execution record

## Simplified workflow and completed pilot secondary review (2026-09-15)

At the user's request, Codex retired the unfinished automatic annotation runner
and simplified continuation to five-letter assignments, immutable initial records
and the existing offline checker. The failed runner/tests remain local historical
provenance; they are not part of the continuation path. No new model calls were
made during this simplification and final secondary review.

Codex reread all 24 complete pilot sources and completed 216 per-letter checks plus
38 comparison groups covering 1,476 pilot memberships. The final pilot contains
77 findings; 20 letters are adjudicable and four retain explicit source-specific
issues owned by Conor/domain reviewer. Corrections preserve qualified conditions,
source antecedents and the shared observation window. The complete change chain
and original initial annotations are retained. No new general clinical rule was added.

Gemini has saved per-letter self-review outputs for all 24, and its earlier
cross-sample report covers 23 sources/1,319 memberships. Codex checked the extra
letter and later corrections across the pilot; this is not described as Gemini
independently cross-reviewing the final 24-source snapshot. Both full750 review
passes remain required before the development reference is complete.

The pilot is accepted for staged continuation, starting with five letters. All 726
remaining sources are assigned once across 146 batches; none has a bulk initial.
Execution is paused for the next phase. Named searches cover all750 source texts,
but semantic review of non-pilot matches remains pending. The pilot is a reviewed
synthetic development artifact, not independent clinical validation.

The active local manifest is
`runs/seizure_finding_annotation_v0_2/agy_gemini38_high/manifest.json`.
Its `reviews/codex/REVIEW.md` explains the decision; `TERMINAL_HANDOFF.md` is the
short continuation procedure. Integrity checks verified both pilot snapshots,
review hashes/coverage, original-record preservation, the full change chain and
exactly 726 remaining sources. The portable package's 32 fictional checks, Ruff,
and documentation hygiene passed. Production extraction code and benchmark outputs
were unchanged; the full extraction pytest/mypy suite was not rerun for this scope.

## Earlier terminal handoff (2026-09-15)

The user requested continuation in their own AGY terminal. The local handoff is
`runs/seizure_finding_annotation_v0_2/agy_gemini38_high/TERMINAL_HANDOFF.md`.
There are24 saved pilot initials and no bulk initials. Gemini self-review outputs
exist for all24; later corrections have not yet been assembled or accepted as a
final24-source reference. The23-source comparison report reconciled39 groups and
1,319 supplied memberships, before the latest corrections and extra letter.
Four source-specific issues remain open. Pilot acceptance is pending.

The latest runner-edit attempt ended with provider503/no capacity. A fresh mocked
runner check ran11 tests with3 recovery failures; it is not ready for bulk use.
The portable annotation package passed32 fictional checks and Ruff. These are
structural/tooling checks, not clinical validation. The handoff specifies runner
repair,24-source reconciliation, pilot review,726 remaining annotations, Gemini's
full review and the subsequent Codex secondary review. Earlier dated pilot counts
below describe their respective snapshots.

Canonical owner of dated run authorisations, settings and completed comparison summaries.
Reorganised 2026-09-14 from the [study protocol](one_shot_paper_protocol.md).
Preserve the original meaning of every named run and linked artifact. Earlier
budgets and runtime settings apply to their named runs; subsequent amendments do
not rewrite earlier attempts. “Pending” in a dated record is not current status;
[PROJECT_STATUS.md](../../../PROJECT_STATUS.md) owns current work.

Annotation runs use the separate [annotation review procedure](seizure_finding_annotation_review.md).
Representation decisions belong to [schema decisions](one_shot_schema_decisions.md).

## Annotation instructions and pilot (2026-09-15)

The protocol was split into separate study, annotation, review, schema-decision and
execution documents. The portable annotation package contains the guide, JSON
Schema, fictional examples and a read-only checker. Its file hashes and 12 fictional
checks pass; documentation hygiene and Ruff checks pass. These checks do not
establish annotation completeness or clinical validity.

Codex exported all 750 permitted development letters, including 32 `row_ok=False`
rows, with exact source hashes and without benchmark labels or predictions. The
source-only JSONL SHA-256 is
`f4a5e9b01c31b526e93347dc3ab61d2f6d07db7eae449ff8eecadfc95084d9b2`.
The local run is `runs/seizure_finding_annotation_v0_2/agy_gemini38_high/`;
the directory name records its creation version. Its `guide_versions/v0.3/`
directory pins the revised instructions.

Gemini ran through AGY as `gemini-3.8-flash-high`, with `--effort high`. All 20
initial pilot records, Gemini self-reviews, corrections and Codex source-first
review notes are retained. Earlier AGY attempts encountered network/stream errors;
complete recovered drafts are distinguished from provider successes. The four
latest five-letter correction requests each returned provider success and all 20
records pass the offline source/schema checks. Codex also corrected one partial
calendar date's form, with before/after hashes. Three source-specific issues remain
explicit: disjunctive numeric wording, a bare resolved historical diagnosis and a
seizure-day counting unit. These letters are not yet adjudicable for finding scoring.

Cross-sample review detected omitted subtype mentions, lost condition qualifiers,
duplicate freedom claims and insufficient quotation context. Exact-source group
membership is now generated separately from reviewer judgements; a model-written
comparison report with shortened, non-exact quotations is retained as a defective
draft. Final pilot group rechecking and batch-runner review remain in progress.
No full dev750 annotation reference or finding-performance result exists yet.
AGY attempts retain available usage and batch timing; provider dollar cost and
individual-letter latency are unavailable and must not be inferred from batch time.

## Current plan: timeout reruns and expanded annotation (2026-09-14)

Conor approved the following priorities after the r5 dev750 review. This amendment
supersedes the earlier decision to require no assertion-level annotation. It records
planned work, not completed reruns, annotations or clinical validation.

## Timeout reruns

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

## Completed timeout reruns (2026-09-14)

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

## Paired dev750 execution (2026-09-14)

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

## Pilot domain adjudication (2026-09-15)

CB returned four selected decisions. Codex applied them under annotation guide v0.5:
faithful qualitative preservation of ambiguous quantities and affected-period
recurrence, and exclusion of bare resolved historical diagnoses. All 24 pilot
letters are complete with 77 unchanged findings and no open issues. The original
export and pre-adjudication review remain preserved. Supporting rationales are
attributed to Codex because the export contained one UI-test placeholder and three
blank rationales. The source-bearing evidence owner is local-only
`runs/seizure_finding_annotation_v0_2/agy_gemini38_high/reviews/adjudication/REVIEW.md`.

The v0.5 structural/source checker passed all 24 records. Codex checked all four
decision changes and the other pilot wording-search candidates. The new snapshot
is `annotations/adjudicated.jsonl`; earlier per-source/group reports remain tied
to their original snapshot. The propagation search contains 133 candidates in 114
dev750 letters, not a completed full-set semantic review. The remaining 726 letters
and both full-set reviews are pending; execution remains paused. No model calls,
locked rows or real-patient data were used.
