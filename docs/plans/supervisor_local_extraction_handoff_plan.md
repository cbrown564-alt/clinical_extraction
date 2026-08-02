# Supervisor local clinical extraction handoff plan

Date: 2026-07-20  
Status: source-to-shipped closure current after 2026-08-02 rebuild; supervisor-host and unaided README checks pending
Work mode: build one complete operational handoff, then verify it on the
supervisor's endpoint  
Owner: this document

## Source-to-shipped closure (implemented)

The standalone `handoff/supervisor/` tree and
`handoff/clinical_extraction_supervisor_handoff.zip` were rebuilt from active
source on 2026-08-02. The gate
`tests/test_supervisor_source_handoff.py::test_shipped_package_matches_current_source_closure`
and the non-mutating command
`python scripts/build_supervisor_source_handoff.py --check-source-closure`
both pass. The checker requires every file discovered by the traced runtime
closure, reports content and path drift, and never rewrites the standalone
tree or ZIP.

The former rebuild blocker was an eager import in
`tasks/seizure_frequency/gan2026/llm/__init__.py` that pulled
`reports/base.py` into the hybrid runtime closure. That package init is now
empty, and the builder exercises the lazy ExECT `_assemble` path so
`letter_assembly` enters the shipped closure. Research `reports/` paths remain
forbidden.

Remaining before calling the handoff usability-validated:

- run setup and the synthetic examples on the supervisor's intended host and
  Python 3.11 installation;
- run `check` against the exact approved endpoint/model route; and
- have the supervisor follow the README unaided and record any correction.

No archive rebuild or new model call is authorized merely by documentation
updates. Rebuild again only after active source identities that enter the
traced runtime change.

## Historical implementation snapshot (2026-07-21)

This section records a past engineering snapshot. It does **not** override the
current closure status in **Source-to-shipped closure (implemented)** above.

The source-first handoff was built under `handoff/supervisor/` and in
`handoff/clinical_extraction_supervisor_handoff.zip` at this snapshot. Its
active public source is `src/clinical_extraction_local/`; `handoff/source/`
owns the README, setup, examples, and operational documentation. The builder
copies the selected internal runtime through an explicit path allowlist and
writes every shipped file and SHA-256 hash to `SOURCE_MANIFEST.json`.

**Historical status only (superseded 2026-08-02):** at this snapshot the shipped
tree and ZIP had drifted from active source and the source-to-shipped closure
test would have failed until rebuild. The 2026-08-02 rebuild restored closure.
The claims below describe this snapshot's behavior and checks at the time; they
do not certify today's shipped package.

Historical behavior at that snapshot:

- `show-config`, `validate-input`, real-schema `check`, `seizure-frequency`,
  `clinical-findings`, and independent two-call `all` commands;
- direct OpenAI-compatible `VLLMClient` with explicit generation, thinking,
  JSON-schema, timeout, retry, and non-secret route settings;
- strict full-file JSONL validation before model construction, concise default
  results, optional private traces, privacy-safe errors, atomic output, synced
  partial rows, exact resume identity, and selective failed-row retry;
- the selected Gan v0.5 and one-call ExECT processing paths, exact evidence,
  format-only retry validation, and prediction-changing component attribution;
- readable prompts, schemas, source map, Windows and shell setup, synthetic
  examples, locked dependencies, tests, and a clean extraction archive with no
  `.pyz`, benchmark-result files, private configuration, or research reports.

Historical local evidence for that snapshot:

- 26 focused handoff, privacy, recovery, source-manifest, and five-fixture
  parity tests pass in the repository environment;
- the builder extracts the archive into a clean Windows directory, runs
  `validate-input`, and runs the shipped package tests from that directory;
- scoped Ruff and package mypy pass. Repository-wide mypy passes across 335
  source files;
- the latest broad pytest run passed 1,376 of 1,381 tests. Four failures are
  retained-evidence hash drift in unrelated changed reports, and one is a
  pre-existing artifact-root assertion affected by the workspace-local pytest
  temp location. The handoff-focused suite is green.

Still required before calling the handoff usability-validated:

- run setup and the synthetic examples on the supervisor's intended host and
  Python 3.11 installation;
- run `check` against the exact approved endpoint/model route and inspect JSON
  mode, thinking, token-limit, retry, and returned-model behavior; and
- have the supervisor follow the README unaided and record any correction.

No private note, locked row, or paid model call was used during implementation.
This was operational implementation and local engineering evidence, not
clinical validation or endpoint compatibility evidence. Source-to-shipped
closure is now current; host and unaided checks remain open.

## Objective

Create a small, readable source package that lets the supervisor run the
project's selected DeepSeek-compatible extraction workflows against private
clinical notes through an approved OpenAI-compatible endpoint.

The package will include both established workflows:

1. `seizure-frequency` produces the Gan-derived current seizure-frequency
   answer, evidence, rationale, and component trace.
2. `clinical-findings` makes the selected one-call ExECT extraction and returns
   Diagnosis, Seizure Frequency, Prescription, and Investigations findings.

An `all` command may run both workflows for each note. It is orchestration over
two existing workflows, not a new shared prompt. It will normally make two
model calls per note and report that fact before execution.

The first-run instructions will lead with `seizure-frequency`. The four-family
workflow will be installed and documented from the beginning so the handoff
does not need to be replaced when the supervisor expands its use.

## Why the current handoff must change

The current handoff is small on disk but opaque to a reader. Its executable
archive contains 132 Python files behind `clinical_extraction.pyz`. The setup
and commands are visible, but the prompt, schema, deterministic changes, and
output construction are not easy to find.

The supervisor-provided utility sample establishes a different working style:

- ordinary Python modules that can be opened and edited;
- direct use of the OpenAI client for OpenAI-compatible endpoints;
- environment variables for endpoint and API-key configuration;
- a model object with an explicit request method;
- visible temperature, token, JSON-output, and thinking settings; and
- local files for logs and optional response caching.

The new handoff will preserve the familiar direct-Python experience without
copying the supervisor's 1,035-line multi-provider utility. It will also avoid
that utility's unsafe defaults for private notes: it writes full prompts and
responses to a readable log, and its optional pickle cache stores complete
prompt and response content.

## Fixed product decisions

### Two workflows remain distinct

The handoff will not merge the Gan-derived current-frequency prompt with the
ExECT four-family prompt.

| Command | Model calls per note | Output |
| --- | ---: | --- |
| `seizure-frequency` | 1 normally | One selected current seizure-frequency answer |
| `clinical-findings` | 1 normally | Diagnosis, Seizure Frequency, Prescription, and Investigations findings |
| `all` | 2 normally | Both results, with independent status and trace summaries |

The ExECT Seizure Frequency family and the Gan-derived current-frequency
answer are related but not interchangeable. They use different task contracts,
selection behavior, and output representations. The combined result must keep
them under different field names.

### Use the selected architectures

- The current-frequency workflow uses the Gan v0.5 structured-event prompt and
  its selected deterministic repair path.
- The clinical-findings workflow uses one structured four-family call per note,
  as selected by [decision 0041](../decisions/0041-single-call-exect-model-comparison.md).
- Model ownership and deterministic changes for the four families follow
  [decision 0040](../decisions/0040-final-exect-llm-with-rules-family-ownership.md).
- Format-only structured-output repair follows
  [decision 0042](../decisions/0042-shared-local-model-structured-output-repair.md).
- No independent rules-only producer may silently replace a model-led family.
- A deterministic step that adds, removes, selects, or changes a clinical fact
  remains visible as a prediction-changing component.

### Keep the endpoint boundary familiar

The public endpoint client will use the OpenAI Python client and an
OpenAI-compatible `/chat/completions` endpoint. The documented configuration
will use the supervisor's familiar names:

```dotenv
VLLM_BASE_URL=http://127.0.0.1:8000/v1
VLLM_API_KEY=EMPTY
VLLM_MODEL=deepseek-v4-flash
VLLM_THINKING=false
```

For a transition period, the implementation may also accept the current
`CLINICAL_LLM_*` names as aliases. If both are set, the command must reject the
ambiguous configuration unless their values agree. It must never silently pick
one credential or endpoint over another.

The exact request settings will be explicit and recorded:

- endpoint base URL, with credentials removed;
- requested and response model names;
- thinking mode and reasoning setting, when supported;
- temperature and seed, when supported;
- maximum completion tokens;
- timeout and retry count;
- JSON response mode;
- cache state; and
- prompt, schema, rule-set, and package versions.

Endpoint-specific fields such as vLLM `chat_template_kwargs` will live in the
endpoint adapter. Clinical prompt code must not contain transport branching.

### Source is the primary deliverable

The handoff will ship readable `.py`, prompt, schema, example, and test files.
It will not require the supervisor to inspect a `.pyz`, wheel, generated
single-file executable, or container image.

A zip file may remain the transfer format, but extracting it must produce the
same readable directory tree. A container may be added later as an optional
runtime convenience; it will not replace the source package.

## Intended user experience

### First successful run

The README will begin with the current-frequency workflow and a synthetic
example. It will not begin with architecture history or benchmark results.

On Windows PowerShell:

```powershell
.\setup.ps1
Copy-Item .env.example .env
.\.venv\Scripts\python.exe run.py check
.\.venv\Scripts\python.exe run.py seizure-frequency `
  --input examples\seizure_frequency\notes.jsonl `
  --output results.jsonl
```

On macOS or Linux:

```sh
./setup.sh
cp .env.example .env
./.venv/bin/python run.py check
./.venv/bin/python run.py seizure-frequency \
  --input examples/seizure_frequency/notes.jsonl \
  --output results.jsonl
```

The example notes must be synthetic and visibly labelled as such.

### Broader extraction

The next README section will introduce the four-family workflow:

```sh
./.venv/bin/python run.py clinical-findings \
  --input notes.jsonl \
  --output findings.jsonl
```

The combined command will be documented after both individual commands:

```sh
./.venv/bin/python run.py all \
  --input notes.jsonl \
  --output results.jsonl
```

Before `all` starts, the command will print a privacy-safe summary such as:

```text
Notes: 25
Workflows: seizure-frequency, clinical-findings
Expected normal model calls: 50
Endpoint: http://127.0.0.1:8000/v1
Model: deepseek-v4-flash
Thinking: disabled
Cache: disabled
```

No note text or API key may appear in this summary.

### Inspection commands

The package will provide:

- `check`: connect to the endpoint, verify JSON mode, and run a real extraction
  against a bundled synthetic note;
- `validate-input`: check JSONL structure, unique IDs, and non-empty note text
  without making a model call;
- `show-config`: print resolved non-secret configuration and the source of each
  value;
- `seizure-frequency`: run the current-frequency workflow;
- `clinical-findings`: run the four-family workflow; and
- `all`: run both workflows independently.

`check` must exercise the actual prompt and response schema. A generic
`{"ok": true}` response is insufficient evidence that the endpoint can run the
workflow.

## Python interface

The command-line script will be a thin wrapper over a documented Python API:

```python
from clinical_extraction_local import ClinicalExtractor, VLLMClient

model = VLLMClient.from_env()
extractor = ClinicalExtractor(model)

frequency = extractor.seizure_frequency(note_id="note-001", text=note)
findings = extractor.clinical_findings(note_id="note-001", text=note)
```

The public model interface will be small enough to adapt to the supervisor's
existing client when required:

```python
class ModelClient(Protocol):
    def complete_json(
        self,
        *,
        messages: list[dict[str, str]],
        schema: dict[str, object],
        settings: GenerationSettings,
    ) -> ModelResponse: ...
```

The default `VLLMClient` will implement this protocol directly with the OpenAI
client. A compatibility adapter for an existing `request(...)` object may be
provided, but it must not inherit full-content logging or caching without an
explicit private-data configuration.

DSPy may remain an internal dependency only where removing it would change the
selected program or prompt. The README and public API must not require the
supervisor to understand DSPy. Any later removal of DSPy requires prompt and
result parity checks rather than a claim that transport refactoring is
semantically neutral.

## Proposed directory structure

```text
clinical_extraction_handoff/
  README.md
  run.py
  setup.ps1
  setup.sh
  requirements.txt
  requirements.lock
  .env.example
  LICENSE-or-usage-notice.md

  clinical_extraction_local/
    __init__.py
    cli.py
    config.py
    client.py
    input.py
    output.py
    errors.py
    versions.py

    seizure_frequency/
      __init__.py
      pipeline.py
      prompt.md
      schema.json
      parsing.py
      selection.py
      rules/

    clinical_findings/
      __init__.py
      pipeline.py
      prompt.md
      schema.json
      parsing.py
      assembly.py
      diagnosis.py
      seizure_frequency.py
      prescription.py
      investigations.py

  examples/
    seizure_frequency/
      notes.jsonl
      expected_shape.jsonl
    clinical_findings/
      notes.jsonl
      expected_shape.jsonl

  docs/
    HOW_IT_WORKS.md
    OUTPUTS.md
    PRIVATE_DATA.md
    TROUBLESHOOTING.md

  tests/
    test_cli.py
    test_client.py
    test_seizure_frequency.py
    test_clinical_findings.py
    test_private_data_controls.py
    test_source_manifest.py
```

This is a target organization, not a requirement to split every function into
its own file. Prefer a short reading path over an artificial file-count limit.

The source package will be built from an explicit allowlist manifest. Runtime
import tracing may check the manifest, but it must not be the only mechanism
that decides which files are shipped. Conditional error, retry, and repair
paths must be included deliberately.

## Short reading path

The README will give the supervisor this order:

1. `run.py` for the complete command invocation.
2. `clinical_extraction_local/client.py` for the endpoint call.
3. The selected workflow's `pipeline.py` for processing order.
4. `prompt.md` and `schema.json` for the model contract.
5. Named rule or family files for deterministic changes.
6. `docs/OUTPUTS.md` for result and trace interpretation.

Research dataset loaders, scorers, experiment reports, holdout artifacts, and
paper machinery will not be included merely because a runtime import once
loaded them.

## Input contract

Input is UTF-8 JSONL with one object per note:

```json
{"id":"note-001","text":"Synthetic example note text."}
```

Rules:

- `id` is required, non-empty, and unique within the file;
- `text` is required and non-empty;
- blank lines are ignored;
- malformed JSON stops before any model call;
- duplicate IDs stop before any model call;
- input order is preserved in the final output;
- unknown fields are rejected by default so accidental private columns are not
  silently copied into outputs; and
- note IDs are treated as private data even when they are not patient names.

If metadata passthrough becomes necessary, it requires an explicit allowlist
of field names and a documented output destination.

## Output contract

### Common row envelope

Every output row will contain:

```json
{
  "id": "note-001",
  "status": "ok",
  "package_version": "...",
  "model": "deepseek-v4-flash",
  "workflows": {},
  "warnings": []
}
```

The default result contains final clinical values, exact supporting evidence,
and concise provenance. It does not contain the full prompt, raw model
response, or every intermediate finding.

### Current seizure-frequency result

```json
{
  "current_seizure_frequency": {
    "value": "2 per month",
    "kind": "frequency",
    "evidence": "two seizures each month",
    "rationale": "The statement describes the current recurring rate.",
    "first_prediction_owner": "model",
    "deterministic_changes": []
  }
}
```

The exact field vocabulary will be derived from the selected Gan output
contract. `unknown`, no reference, seizure-free state, ranges, clusters, and
vague frequency must remain distinct wherever the selected pipeline keeps them
distinct. Benchmark formatting must not erase the richer operational value.

### Four-family clinical finding result

```json
{
  "clinical_findings": {
    "diagnoses": [],
    "seizure_frequencies": [],
    "prescriptions": [],
    "investigations": []
  }
}
```

Each finding will include:

- family and normalized clinical value;
- relevant attributes;
- exact evidence text;
- assertion or temporality when the task defines it;
- model origin;
- named prediction-changing deterministic actions; and
- warnings or repair notes that affect interpretation.

The final output must not imply that ExECT Seizure Frequency is identical to
the Gan-derived `current_seizure_frequency` field.

### Trace output

`--trace-output PATH` will write a separate JSONL file containing the raw model
response, parse attempts, format repairs, intermediate values, deterministic
actions, and component attribution needed to explain the result.

The trace file is private clinical data. The command must display that warning
before creating it. Full traces are off by default.

### Errors and partial success

One workflow failing must not erase a successful result from the other
workflow. Under `all`, each workflow receives its own status:

```json
{
  "id": "note-001",
  "status": "partial",
  "workflows": {
    "seizure_frequency": {"status": "ok", "result": {}},
    "clinical_findings": {
      "status": "error",
      "error": {"code": "schema_validation_failure"}
    }
  }
}
```

Default errors contain a stable code and safe summary. Raw provider exceptions
belong only in an explicitly requested private trace after likely credentials,
headers, and request bodies are removed.

## Privacy and storage requirements

The package processes private data and will therefore default to minimal local
retention.

Required defaults:

- no prompt or response logging;
- no response cache;
- no telemetry or error reporting to another service;
- no note text in console progress;
- no note text in exception summaries;
- no credential values in configuration output;
- no temporary files outside the selected output directory;
- atomic final output replacement; and
- restrictive file permissions where the host supports them.

The README and `docs/PRIVATE_DATA.md` will state that notes leave the process
through the configured endpoint. Calling the tool "local" is accurate only
when that endpoint and its logs, storage, and operators are inside the approved
boundary.

Optional caching or tracing requires:

1. an explicit command flag;
2. an explicit destination;
3. a warning that the file contains note text and model output;
4. a recorded cache or trace state in run metadata; and
5. documented deletion and retention responsibility.

The handoff must not include private notes, API keys, row-level holdout data,
sealed artifacts, or support logs captured from a real note.

## Endpoint behavior and structured output

The endpoint adapter will support the request pattern already familiar to the
supervisor while detecting capability differences rather than assuming them.

`check` will report:

- whether the endpoint is reachable;
- the requested and returned model identifiers;
- whether JSON response mode is accepted;
- whether the real task schema is satisfied;
- whether thinking or reasoning content is present despite the configured
  setting;
- whether final content is empty or truncated; and
- which structured-output handling mode was used.

The adapter will preserve the original response in memory long enough to parse
and diagnose it. It will apply only the format repairs allowed by decision
0042. A bounded format-only retry may occur after a parseable schema defect;
the run must count the initial failure, retry, and final result separately.

Clinical values, evidence, selected events, temporality, and categories must
not be changed by transport repair. Those changes belong to named clinical
rules and component attribution.

## Progress, recovery, and reruns

The current operational wrapper collects a full run before writing the final
file. The handoff will preserve completed work during a long private-data run.

Planned behavior:

- write each completed row to a private partial JSONL file in the output
  directory;
- flush and sync each completed record;
- on `--resume`, verify the input identity, workflow versions, endpoint route,
  model, prompt, schema, rule set, and settings before reuse;
- refuse a partial file containing unknown or duplicate IDs;
- never reuse a row produced under different semantic settings;
- keep failed rows eligible for an explicit retry without repeating successful
  rows; and
- atomically produce the final ordered output when all requested work ends.

The run summary will report requested notes, successful rows, partial rows,
failures, model calls, retries, parse repairs, elapsed time, and usage only when
the provider supplies it. It will not invent cost estimates.

## Documentation included in the handoff

### README.md

- two-minute seizure-frequency quick start;
- endpoint configuration;
- real-schema `check` command;
- first synthetic run;
- four-family and `all` commands;
- where private data is written;
- common errors; and
- link to the deeper documents.

### HOW_IT_WORKS.md

- the two separate workflows;
- model call, parsing, clinical rules, and final output order;
- why `all` makes two calls;
- component ownership; and
- exact prompt, schema, and rule version locations.

### OUTPUTS.md

- field-by-field default result definitions;
- distinction between the two seizure-frequency representations;
- evidence and attribution interpretation;
- error codes;
- trace schema; and
- one synthetic success, partial success, and failure.

### PRIVATE_DATA.md

- endpoint boundary;
- files containing note content;
- default logging and cache behavior;
- trace and resume-file sensitivity;
- credential handling;
- deletion responsibility; and
- support procedure that never requests a real note or key.

### TROUBLESHOOTING.md

- endpoint and certificate errors;
- model-name mismatch;
- unsupported JSON mode;
- thinking-only or empty final content;
- truncation;
- schema validation failure;
- retry behavior;
- safe diagnostic information to share; and
- resume mismatch.

Aggregate research results do not belong in the first-run directory. If they
are retained for context, place sanitized summaries under an optional
`evidence/` directory, remove internal `scratch/...` paths, and state their
dataset, split, scorer, model route, and claim limits. They are not evidence of
performance on the supervisor's private data.

## Implementation sequence

### 1. Prove the endpoint and current-frequency experience

- Replace the executable-only entry with readable source.
- Implement configuration, the OpenAI-compatible client, safe progress output,
  strict JSONL input, and concise output.
- Wire the selected Gan v0.5 prompt and deterministic path without changing its
  clinical behavior.
- Implement `show-config`, `validate-input`, and the real-schema `check`.
- Run one synthetic note, then five permitted fixtures.
- Compare the new source package with the current operational wrapper at the
  raw structured response, selected event, final value, evidence, and repair
  stages.

This is the representative slice. Do not spread the packaging pattern to the
four-family workflow until this complete loop, including one failure and
resume, works.

### 2. Extract the reusable package pattern

- Freeze the public `ModelClient`, input, result, error, trace, and run-metadata
  contracts.
- Add the explicit source allowlist and provenance manifest.
- Separate endpoint-format repair from clinical deterministic changes.
- Complete Windows and macOS/Linux setup instructions.
- Confirm that no default log, cache, exception, or temporary file contains
  note text outside the requested result location.

### 3. Add the one-call four-family workflow

- Include the selected structured prompt and schema as readable assets.
- Add the model-led Diagnosis, Seizure Frequency, Prescription, and
  Investigations paths.
- Preserve family-specific model origin and deterministic actions.
- Produce the concise four-family result and optional full trace.
- Compare permitted fixtures against the selected main-repository operational
  assembly at raw, parsed, evidence-valid, deterministic-change, and final
  finding stages.

### 4. Add orchestration and recovery

- Implement `all` as two independent workflow calls.
- Report expected normal call count before execution.
- Preserve successful workflow output when the other workflow fails.
- Implement partial files, strict resume validation, selective retry, ordered
  finalization, and safe summaries.

### 5. Build and inspect the transfer archive

- Generate the readable directory from an explicit manifest.
- Exclude Git metadata, `.env`, caches, logs, real outputs, `__pycache__`, macOS
  archive metadata, research data, and sealed artifacts.
- List every shipped file and its SHA-256 hash in `SOURCE_MANIFEST.json`.
- Extract the archive into a clean directory and run the documented commands
  only from its contents.
- Inspect the extracted source tree manually using the README reading path.

### 6. Verify on the supervisor's runtime

- Confirm the intended operating system and Python 3.11 availability.
- Run `check` against the exact endpoint software and model route.
- Run the synthetic examples without real private data.
- Confirm thinking, JSON mode, token limit, and retry behavior.
- Have the supervisor follow the README without repository knowledge.
- Record usability corrections before private-data use.

This is verification of the handoff and endpoint compatibility. It is not
clinical validation on the supervisor's data.

## Verification plan

### Automated checks

- input validation and duplicate-ID rejection;
- environment precedence and conflicting-alias rejection;
- API-key redaction in representations, console output, and exceptions;
- request construction for thinking on and off;
- actual schema supplied to the endpoint;
- format-only repair and bounded retry records;
- no clinical-value change from format repair;
- prompt, schema, and rule version hashes;
- current-frequency stage parity on permitted fixtures;
- four-family stage parity on permitted fixtures;
- exact-evidence checks;
- component attribution for prediction-changing rules;
- output and trace schema validation;
- independent failure status under `all`;
- partial-file recovery and configuration-mismatch refusal;
- no full note text in default logs or temporary paths;
- explicit source manifest completeness;
- archive exclusions; and
- commands run from a clean extracted copy.

### Host checks

- repository `.venv` focused tests during implementation;
- repository-wide pytest, Ruff, and mypy before a broad completion claim;
- clean Windows PowerShell setup and synthetic run;
- clean macOS or Linux shell setup and synthetic run;
- exact supervisor endpoint `check`; and
- manual inspection of default output, trace output, failure, retry, resume,
  and overwrite refusal.

### Review checks

The supervisor should be able to answer from the shipped files:

1. Which endpoint and model will receive the notes?
2. How many model calls will each command make?
3. Where is each prompt and response schema?
4. Which code changes a model-produced clinical fact?
5. Which output files contain private text?
6. How can a failed run resume without repeating successful notes?
7. What evidence supports the selected architecture, and what does it not
   establish about the supervisor's data?

If those answers require access to the main research repository, the handoff
is not complete.

## Acceptance criteria

The handoff is implemented when:

1. the transfer archive contains readable source and no `.pyz` as its required
   runtime;
2. the README's first successful path is seizure frequency on a synthetic note;
3. the four-family and `all` workflows are present from the first release;
4. `all` clearly reports two normal calls per note and preserves separate task
   results;
5. prompts, schemas, deterministic clinical changes, and output definitions
   have a short documented reading path;
6. private note logging, caching, and telemetry are off by default;
7. input validation occurs before the first model call;
8. `check` exercises the real extraction schema against the configured route;
9. default results are concise and full traces are optional and visibly
   sensitive;
10. permitted-fixture parity checks pass for both selected workflows;
11. failure, retry, partial success, resume, and overwrite behavior are tested;
12. a clean extracted copy works on Windows and the supervisor's host;
13. the exact supervisor endpoint passes the synthetic check; and
14. the supervisor can follow the README without help from the main repository.

The handoff is verified only after the automated and direct host checks pass.
It is validated for usability only after the supervisor completes the
synthetic workflow successfully. Neither result is clinical validation on
private data.

## Work explicitly excluded

- merging both workflows into one new model prompt;
- changing clinical prompts or deterministic rules merely to reduce file count;
- claiming that Gan and ExECT seizure-frequency outputs are interchangeable;
- including research loaders, scorers, datasets, notebooks, dashboards, paper
  sources, or sealed row artifacts in the operational package;
- inspecting locked Gan `test450` or ExECT `test60` rows;
- tuning from the supervisor's private data without a separate permitted
  protocol;
- enabling full-content logs, traces, or caches by default;
- sending telemetry or diagnostics outside the configured endpoint;
- presenting retained aggregate benchmark results as validation on private
  data;
- supporting every provider class found in the supervisor's general LLM
  utility; and
- making a container the only supported way to inspect or run the code.

## Risks and controls

| Risk | Control |
| --- | --- |
| A small archive remains conceptually opaque | Ship readable source, prompts, schemas, examples, and a short reading path |
| Rewriting transport changes prompt behavior | Retain prompt snapshots and compare raw and parsed stages on permitted fixtures |
| Import tracing omits a conditional path | Build from an explicit allowlist and test failures, retries, and repairs |
| The familiar LLM utility logs private notes | Use a small client with logging and caching off by default; test for note leakage |
| `all` appears to be one call or one task | Report two calls and keep independent result fields and statuses |
| The two frequency representations are confused | Use distinct field names and define their task contracts in `OUTPUTS.md` |
| Endpoint JSON behavior differs | Run the actual schema in `check` and retain bounded repair and retry diagnostics |
| Thinking consumes the completion budget | Make thinking explicit, detect reasoning-only responses, and test the exact route |
| A long run loses completed work | Write synced partial rows and validate resume identity before reuse |
| Error handling exposes note text or credentials | Stable safe error codes by default and redaction tests for optional diagnostics |
| Research results imply private-data performance | Separate optional sanitized evidence and repeat the claim boundary |
| Source extraction drifts from the main package | Version and hash prompt, schema, rule set, and source manifest; run parity checks |
| Cross-platform instructions drift | Test clean Windows and macOS/Linux setup from the transfer archive |

## Decision ledger

| Question | Decision or assumption | Evidence | Consequence | Owner |
| --- | --- | --- | --- | --- |
| What should the supervisor encounter first? | Current seizure frequency on one synthetic note | The immediate need is seizure frequency | README and examples lead with `seizure-frequency` | This plan |
| Should the later families wait? | No; include the four-family workflow in the first complete handoff | The supervisor is expected to need all four | Package and tests cover both workflows now | This plan |
| Is `all` a new prompt? | No; it runs the two selected workflows independently | Their task and output contracts differ | Two normal calls per note and separate result fields | Decisions 0040, 0041, and this plan |
| What interface should feel familiar? | Visible Python using an OpenAI-compatible client and `VLLM_*` settings | Supervisor-provided utilities use this pattern | Small public client and Python API; no executable-only entry | This plan |
| Should the supervisor's LLM utility be bundled? | No; preserve its useful calling pattern, not its unrelated providers and unsafe logging defaults | The utility has many providers and logs full conversations | Provide a small compatible client and optional adapter | This plan |
| May the handoff hide source in a `.pyz`? | No | The current archive is difficult to inspect despite its size | Readable source is the primary runtime | This plan |
| How is private data handled? | Minimal retention, no default full-content logs or cache | Notes, evidence, traces, and IDs may be sensitive | Explicit destinations and privacy tests | This plan |
| How is endpoint compatibility established? | Run the real extraction schema on synthetic text | A generic connectivity probe does not cover structured extraction | `check` validates the configured route before private-data use | This plan and decision 0042 |
| Can the handoff claim private-data performance? | No | Retained results use different datasets and claim limits | Operational and usability verification remain separate from clinical validation | Project canon and this plan |

## Durable document ownership

- This plan owns the handoff scope, user experience, privacy defaults,
  implementation order, and acceptance criteria until supervisor-host and
  unaided README verification are complete.
- [Software design](../design/architecture.md) continues to own main-package
  component boundaries.
- [Decision 0040](../decisions/0040-final-exect-llm-with-rules-family-ownership.md)
  owns ExECT model and deterministic family ownership.
- [Decision 0041](../decisions/0041-single-call-exect-model-comparison.md) owns
  the one-call four-family architecture.
- [Decision 0042](../decisions/0042-shared-local-model-structured-output-repair.md)
  owns allowed format-only repairs and retry accounting.
- [Project status](../../PROJECT_STATUS.md) will change only after the evidence
  or implementation owner is updated and the stated checks pass.

If implementation requires a lasting technical choice that contradicts this
plan or the accepted decisions, record that choice in a new decision document
instead of silently editing generated handoff files.
