# Gan 2026 hosted test450 protocol

Date: 2026-07-15  
Status: complete for the two missing hosted conditions  
Authorization: the user explicitly authorized this run on 2026-07-15.

## Question

How do the two missing hosted decision-0039 models, GPT-5.6 Luna and GPT-5.6
Sol, perform on locked Gan test450 with the retained one-call `llm_with_rules`
event extractor and unchanged Gan scorer?

## Frozen data and row policy

- Dataset: Gan 2026; manifest `gan2026_split_v1`; distribution `test450`.
- The runner may read locked notes solely to make the frozen calls.
- No test-row identifier, note, prediction, evidence, error, family membership,
  or model-specific failure may be inspected or reported.
- Raw checkpoints are sealed under ignored `scratch/holdout/gan_test450/`.
  Only aggregate results and operational totals may leave that directory.

## Frozen candidate and conditions

Candidate: retained `hybrid_structured_events`, exposed by CLI name
`llm_with_rules`. It makes one structured event call per note, then applies the
existing format repair, selected-evidence repair, deterministic clinical rules,
and final rendering as separately recorded stages. There is no scorer,
normalization, sentinel, cluster, row-ok, or repair-policy change.

Fresh conditions are GPT-5.6 Luna (`openai/gpt-5.6-luna`) and GPT-5.6 Sol
(`openai/gpt-5.6-sol`, Responses transport). Luna uses its only supported
temperature, the provider default value `1`; Sol omits the unsupported
temperature parameter. DSPy cache is disabled, and the maximum is 10,000
tokens.

No repeat is authorized for the completed GPT-4.1-mini, thinking DeepSeek, or
Qwen 3.6:35B conditions. Their aggregate-only results are retained in current
evidence or recoverable from Git history: GPT-4.1-mini v0.6 scored 364/450
Purist; thinking DeepSeek scored 345/450 on v0.6 and 346/450 on v0.7; Qwen
v0.6 repairfix scored 366/450. These historical prompts remain named rather
than being treated as exact reruns of the current code.

## Readouts, gates, and stop rule

Primary: Purist accuracy and correct count on all 450 rows. Secondary:
Pragmatic accuracy and correct count, aggregate call/parse/schema/fallback
counts, stage attribution totals, timing, and provider usage when exposed.
No post-hoc row slice or failure review is permitted.

Provider retries are limited to the frozen runner policy. Parse or model
failures remain visible in aggregates and are not silently converted into
successful model-selected labels. Resume is allowed only for the same frozen
condition from sealed artifacts whose source indices are validated by code.

Run Luna and Sol once. A defect is recorded; it starts a new
validation candidate and never licenses test450 tuning. A clean result is final
holdout evidence for this exact candidate, split, model route, and scorer. It is
benchmark-comparable only to the extent stated by the existing Gan canon; it is
not a complete six-model result until the local conditions finish.

Configuration: [hosted holdout runs](../../../configs/holdout/hosted_holdout_runs_20260715.json).

## Pre-call amendment

The first controller launch began a redundant GPT-4.1-mini condition before
the existing completed Gan results were checked. The user stopped that repeat;
the controller and child process were terminated, and its partial scratch
artifact is rejected and must not be resumed or reported. The frozen run list
was narrowed to Luna and Sol before either missing condition started.

## Launch record

The corrected Luna-and-Sol panel launched at 2026-07-15 13:02 Europe/London.
Operational logs are `scratch/holdout/gan_test450_missing_panel.stdout.log` and
`scratch/holdout/gan_test450_missing_panel.stderr.log`; sealed artifacts remain
beneath `scratch/holdout/gan_test450/`.

## Luna transport amendment

The first Luna attempt failed before generation because the provider rejects
temperature `0` and supports only its default value `1`. The controller was
stopped after the aggregate failure was detected. A permitted five-record
validation run then used the identical model, prompt, pipeline, schema, repair,
and scorer with temperature `1`: 5/5 calls and structured parses succeeded,
with zero call or parse/schema failures and valid evidence on all five. Luna's
frozen transport setting is therefore amended to `1`; the failed holdout
artifact remains rejected and must not be resumed or reported.

The corrected run uses the clean root
`scratch/holdout/gan_test450_tempfix_v2/`, distinct from every rejected
temperature-0 artifact.

## Sol transport amendment

The first Sol attempt failed before generation because the provider rejects the
temperature parameter entirely. The controller was stopped after the aggregate
failure was detected. A permitted five-record validation run then used the
identical model, prompt, pipeline, schema, repair, and scorer while omitting
temperature: 5/5 calls and structured parses succeeded, with zero call or
parse/schema failures and valid evidence on all five. The frozen Sol Responses
adapter therefore omits temperature. Its corrected test450 run uses the clean
root `scratch/holdout/gan_test450_sol_transport_v3/` and must not resume or
report either rejected Sol artifact.

The first transport-corrected Sol test450 attempt later encountered
provider-credit exhaustion. Its mixed success/failure artifact is also rejected
and must not be resumed or reported as a model result. After the user restored
credits, Sol was restarted from the clean root
`scratch/holdout/gan_test450_sol_credit_v4/` with every frozen candidate field
unchanged.

## Aggregate result

The two predeclared missing hosted conditions completed without call failures.
Luna had three aggregate parse/schema/label failures; Sol had none.

| Model | Prompt | Purist | Pragmatic | Call failures | Parse/schema/label issues |
| --- | --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Luna | v0.7 | 352/450 (0.7822) | 365/450 (0.8111) | 0 | 3 |
| GPT-5.6 Sol | v0.7 | 358/450 (0.7956) | 376/450 (0.8356) | 0 | 0 |

For context, the retained hosted comparators are GPT-4.1-mini at 364/450
Purist on v0.6 and thinking DeepSeek at 346/450 on v0.7. Their prompt and
pipeline histories remain named; this is not an exact four-model matched rerun.

## Documentation-exposure amendment

During result consolidation on 2026-07-15, a command intended to read the
summary section printed part of the generated locked-row table. No exposed row
was analyzed, selected, or used to change the model, prompt, repair policy, or
scorer. The completed runs remain frozen, but the stronger provenance claim
that no test row was ever exposed is withdrawn. Only aggregate results may be
cited, and no follow-up tuning or row analysis is permitted.
