# Jev and LLM fictional comparison

V1 is an offline prototype with invented sources and provisional author-written keys.
V2 is the separately frozen live pilot described below. Neither is clinical validation.
The [evaluation protocol](../../docs/research/gan2026/one_shot_paper_protocol.md#jev-fictional-comparison)
owns scope and future execution requirements.

## Prepare and inspect

From the repository root, use the repository Python environment:

```sh
.venv/bin/python scripts/benchmarks/prepare_jev_comparison.py prepare --output /tmp/jev-review
```

The output directory must not already exist. Seven saved packs contain:

- `jev`: a request body with model, whole-letter state and Choice questions;
- `llm.messages`: the identical state and questions with a JSON-output instruction;
- source candidates and exact offsets, source/request hashes and explicit policies.

Review the full `jev.state`, `jev.questions` and `llm.messages` before any live use.
The model sees the request body only, never `gold.json`, scoring output or metadata.
The script has no network operation and reads no benchmark corpus. Changing gold
cannot change a request: request construction only accepts a source and model.
The built-in verification runs on preparation, including missing and malformed
outputs, a wrong allowed numeric option, omitted evidence and deterministic rebuild.

A prepared snapshot and verification are under
[results](../../results/letter-benchmarks/gan/jev_fictional_v1/).
Do not count oracle-key self-checks as model performance.

## Score saved responses

Save one provider's responses as a JSON object keyed by fixture ID. Each value can
be a raw Jev response with `answers`, or an LLM JSON object mapping question IDs
to option keys. Decode LLM JSON without changing semantic values. For a failed or
unparseable completion, preserve its raw text separately and omit its fixture entry;
all expected answers then count as wrong. Preserve raw provider responses and
model/runtime/timing/usage metadata separately. Do not mix providers or attempts.

```sh
.venv/bin/python scripts/benchmarks/prepare_jev_comparison.py score \
  --prepared results/letter-benchmarks/gan/jev_fictional_v1 \
  --responses /path/to/saved-responses.json \
  --output /tmp/jev-score.json
```

The score output must not already exist. The scorer refuses prepared requests that
differ from the current builder/model; replay with the frozen code and model flag.
It records request, response and reference hashes. Each report retains all seven
conditions and all 48 scored decisions, including missing/invalid responses.
`final_selection_and_attributes_correct` requires the correct primary selection
and all four scored attributes of that candidate. Diagnostic role judgments are
reported separately; other candidates' attributes are unscored.

## What this can establish

This tests candidate selection and semantic classification. Candidates are complete
newline-delimited sentences, with digit-based quantities extracted from each source
candidate. These are source values, not hand-authored answer suggestions. All source
sentences become candidates, including medication and historical distractors.
Fields name their candidate explicitly; independent questions cannot silently rely
on another answer selecting the same finding. One extra condition removes the
correct candidate but preserves the whole letter, requiring `unsupported`.

This does not implement arbitrary finding discovery, word-number parsing,
cross-sentence evidence binding, a complete R7/R8 output, native Gan normalization,
calibration or clinical validation. Range syntax is recognised by the candidate
builder but not evaluated by the initial keys. The final result is a selected
candidate plus field choices, not an assembled native frequency label. Do not
interpret a duration as a rate or multiply cluster quantities into an observed total.

The paired LLM model and runtime, live-call budget and independent review of the
keys remain to be fixed before an actual comparison. This pack does not modify the
one-call study, existing annotations or locked-test permissions.

## Frozen live pilot v2

The [v2 freeze](../../results/letter-benchmarks/gan/jev_fictional_v2/freeze.json)
records 22 conditions, 157 scored decisions, independent source-only model review,
provider settings and the US$2 budget ceiling. V1 commands and artifacts above
remain unchanged. The live runner is `scripts/benchmarks/jev_pilot.py`.

```sh
.venv/bin/python -m scripts.benchmarks.jev_pilot run --provider jev
.venv/bin/python -m scripts.benchmarks.jev_pilot run --provider deepseek
.venv/bin/python -m scripts.benchmarks.jev_pilot report
```

`run` resumes only never-started cases and skips completed attempts; an incomplete
started attempt blocks replaying that request. It verifies all frozen file hashes
and refuses changed inputs. Calls use `TYPESAFE_API_KEY` (or `JEV_API_KEY`) and
`DEEPSEEK_API_KEY` from the environment or repository `.env`; never place keys in
request artifacts. Outputs live under `runs/jev_fictional_v2/`. `report` is offline
and includes missing rows as wrong. Run commands are paid operations; `report`
never calls a provider. Both runs are complete. See the [v2 results and decision](../../results/letter-benchmarks/gan/jev_fictional_v2/README.md).
The execution record owns current completion status.

## Frozen v3 classification / verification pilot

[V3 inputs and freeze](../../results/letter-benchmarks/gan/jev_fictional_v3/freeze.json)
cover eight development and eight reserved fictional letters. This narrower task
classifies candidate findings and field applicability; it does not extract numerical
values. The hybrid adds a Jev verification call to DeepSeek and defers unsupported
tuples without repair. Seeded incorrect proposals separately test verification.

Run only one command at a time; budget-accounting writes are serial:

```sh
.venv/bin/python -m scripts.benchmarks.jev_verifier_pilot run --split development --provider deepseek
.venv/bin/python -m scripts.benchmarks.jev_verifier_pilot run --split development --provider jev
.venv/bin/python -m scripts.benchmarks.jev_verifier_pilot run --split reserved --provider deepseek
.venv/bin/python -m scripts.benchmarks.jev_verifier_pilot run --split reserved --provider jev
.venv/bin/python -m scripts.benchmarks.jev_verifier_pilot report
```

The run commands are paid; report is offline. Credentials follow v2. Completed
attempts are reused without new calls. `runs/jev_fictional_v3/` preserves local raw
requests, responses, usage and timings. The execution record owns completion and
the decision about any larger development evaluation.

V3 is complete. The [results and stop decision](../../results/letter-benchmarks/gan/jev_fictional_v3/README.md)
record why this candidate is not being extended to dev750. Preserve the frozen
inputs and outputs; do not rerun with revised questions under the same version.
