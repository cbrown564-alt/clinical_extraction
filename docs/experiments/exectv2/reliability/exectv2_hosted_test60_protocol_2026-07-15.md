# ExECTv2 hosted test60 protocol

Date: 2026-07-15  
Status: complete; six-model aggregate-only results retained
Authorization: the user explicitly authorized this run on 2026-07-15.

## Question

How do the six decision-0039 models perform on ExECTv2 test60 under
the fixed decision-0041 one-call architecture and decision-0040 component
policy selected on dev140?

## Frozen data and row policy

- Dataset and split: ExECTv2 manifest-defined `test60`, 59 loadable letters.
- Test60 note text is read only by the frozen runner to make model calls.
- No test60 identifier, text, prediction, evidence, error, changed row, or
  model-specific failure may be inspected or copied into a report.
- Raw call and checkpoint artifacts are operationally necessary but sealed
  under ignored `scratch/holdout/exectv2_test60/`. They are not evidence that
  may be reviewed row by row.
- Only aggregate counts, scores, failure totals, timing, and provider usage may
  leave the sealed directory.

## Frozen conditions

The conditions are GPT-4.1-mini (`openai/gpt-4.1-mini`), GPT-5.6 Luna
(`openai/gpt-5.6-luna`), GPT-5.6 Sol (`openai/gpt-5.6-sol`, Responses
transport), and DeepSeek V4 Flash
(`deepseek/deepseek-v4-flash`). Temperature is zero, DSPy cache is disabled,
and the structured-event maximum is 10,000 tokens.

Candidate: `exectv2_decision_0041_six_model_single_call_test60_v1`. Each model
makes one `exectv2_hybrid_key_family_event_ledger_v0.9.24` structured call per
letter. Diagnosis, Seizure Frequency, Prescription, and Investigations use the
same selected deterministic lenses, joint bounded policy, evidence validation,
assembly, and scorer as the completed clean dev140 runs. No prompt, scorer,
projection, repair, threshold, or fallback may change after calls begin.

## Readouts and failures

Primary: aggregate `clinical_headline` F1 overall and by the four families.
Secondary: aggregate evidence-valid, CUI, source-near, schema/parse, call,
evidence-invalid, timing, and usage totals. Purported row examples and
post-hoc test60 slices are prohibited.

A call or parse failure remains a failure in the frozen aggregate. It may be
retried only by the runner's predeclared provider retry policy; it may not be
repaired semantically after observing test60. Resume is allowed only from the
same model, prompt, split, candidate, and clean output path after ID-set
validation by code. A defect is recorded and starts a future dev140 candidate;
it does not license test60 tuning.

## Stop rule and claim boundary

Run all four hosted conditions once. The separately authorized local queue uses
the same frozen decision-0041 architecture and contributes Qwen and Gemma
aggregate-only readouts. Report each completed aggregate and any operational
failure. Do not choose or tune a model from test60 for another
test60 attempt. A clean result is frozen ExECTv2 test60 holdout evidence for
these exact models and this internal scorer, not the published ExECT benchmark,
clinical validation.

Configuration: [hosted holdout runs](../../../../configs/holdout/hosted_holdout_runs_20260715.json).

## Pre-call amendment

The first launch attempt stopped before any model call because the frozen
configuration assumed 60 rows while the repository's manifest loader returned
59. The row count was corrected to the loader's aggregate count without
printing or inspecting identifiers, notes, annotations, or predictions. No
other field changed.

## Launch record

Launched at 2026-07-15 12:59 Europe/London. The controller runs the four
hosted conditions in frozen order. Operational logs are
`scratch/holdout/exectv2_test60_panel.stdout.log` and
`scratch/holdout/exectv2_test60_panel.stderr.log`; sealed condition artifacts
remain beneath `scratch/holdout/exectv2_test60/`.

## Sol provider-credit restart

The first Sol test60 attempt encountered provider-credit exhaustion after its
clean dev140 and Gan dev5 transport checks. Its mixed success/failure artifact
is rejected as an operational failure and must not be resumed or reported as a
model result. After the user restored credits, Sol was restarted from the clean
root `scratch/holdout/exectv2_test60_sol_credit_v2/` with the same frozen model,
prompt, transport, pipeline, scorer, and row policy.

## Aggregate result

All four hosted conditions completed 59/59 letters with zero call failures and
zero blocking parse/schema failures. No held-out row was inspected.

| Model | Clinical-headline F1 | Precision | Recall |
| --- | ---: | ---: | ---: |
| GPT-4.1-mini | 0.7572 | 0.7742 | 0.7409 |
| GPT-5.6 Luna | 0.7950 | 0.8272 | 0.7652 |
| GPT-5.6 Sol | 0.8047 | 0.8237 | 0.7866 |
| DeepSeek V4 Flash | 0.7881 | 0.8158 | 0.7622 |
| Qwen 3.6:35B | 0.7872 | 0.7848 | 0.7896 |
| Gemma 4 26B | 0.7169 | 0.7299 | 0.7043 |

The Qwen and Gemma local conditions each cover 59/59 letters with zero call
failures. Qwen has zero aggregate parse/schema failures; Gemma records six.
All six results have the same retained status for the internal
`clinical_headline` scorer and named decision-0041 pipeline. Hosted-versus-local
runtime and parse differences remain explicit caveats. These are not published
ExECT benchmark scores or clinical validation.
