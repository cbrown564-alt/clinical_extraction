# Codebase Thermonuclear Review

Date: 2026-06-01

## Scope

Repo-wide review of the young `clinical-extraction` codebase, focused on flaws,
reliable improvements, and thorny research problems. This is broader than a
diff review: it covers architecture, data/scoring contract, deterministic
rules, LLM experiment harnesses, repair attribution, tests, static checks,
artifacts, and project-control documents.

Locked test row-level failures were not inspected. Existing aggregate locked
test context is used only where it is already recorded in project documents.

## Method

Inputs reviewed:

- `PROJECT_STATUS.md`
- `docs/design/architecture.md`
- `docs/design/data_contract.md`
- `docs/design/gan2026_split_protocol.md`
- `docs/design/gan2026_normalization_semantics.md`
- `docs/research/gan2026_current_pipeline_results_report_2026-06-01.md`
- `docs/research/gan2026_deterministic_rule_review_2026-05-31.md`
- `docs/research/gan2026_research_drift_audit_2026-06-01.md`
- source under `src/clinical_extraction/`
- tests under `tests/`
- artifact inventory under `experiments/`

Checks run with macOS/Linux shell activation:

```shell
source .venv/bin/activate
python -m ruff check .
python -m pytest -q
python -m mypy src
```

On Windows PowerShell, activate with `.\.venv\Scripts\Activate.ps1` before the
same `python -m ...` commands.

Results:

- Ruff: passed.
- Pytest: 578 passed, 4 failed.
- Mypy: 31 errors across 11 source files.

## Executive Verdict

The repo has unusually strong research instincts for its age: split discipline,
status tracking, conservative claim language, evidence validity checks, rule
metadata, ablations, and explicit repair attribution all exist. The current risk
is not that the project is careless. The risk is that the code is moving faster
than the architecture can absorb.

Three themes dominate:

1. The docs describe clean boundaries, but several source files still combine
   too many concepts.
2. The strongest metrics depend heavily on deterministic repair and selected
   evidence derivation, so claim language must remain strict.
3. The current test suite is broad, but it mostly preserves accumulated behavior
   rather than forcing simpler, more general abstractions.

The project is very salvageable. The right next phase is not a rewrite. It is a
deliberate consolidation phase: fix the current failing tests, make repair modes
first-class, split the largest behavior files by ownership, and turn the
artifact pile into an indexed run record.

## Findings

### P0: Shared Schema Repair Currently Breaks The Test Suite

Files:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/schema_repair.py`
- `tests/test_gan2026_schema_repair.py`

`repair_decision_payload()` is advertised as repairing common model schema
aliases without changing clinical content. It currently adds default `"unknown"`
values for `seizure_or_event_target`, `window`, `normalized_rate`, and
`rationale`, and inserts `uncertainty="high"` when absent.

That causes four failing tests:

- `test_repair_decision_payload_handles_common_schema_aliases`
- `test_repair_decision_payload_handles_llm_answer_kind_variants`
- `test_repair_structured_extraction_payload_handles_cluster_final_kind_alias`
- `test_repair_structured_extraction_payload_handles_last_event_final_kind_alias`

Why this matters:

This is a concrete behavior bug and a research-validity smell. A shared repair
function should not silently alter output shape unless the caller has explicitly
asked for that pipeline's required-field defaults. If shared repair mutates
payloads before pipeline-specific validation, parse-failure rates and schema
robustness summaries become harder to trust.

Concrete fix:

- Make `repair_decision_payload()` alias-only by default.
- Move required-field defaulting to the specific parser that owns those fields.
- Add tests that prove shared repair does not add fields, and parser-level repair
  does add only the fields required by that parser.

### P1: The Largest Behavior Files Have Become Concept Warehouses

Files:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/normalize.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/pipeline_v1.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_only_structured_events.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_only_claim_table_selector.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/hybrid_rules_candidates_llm_adjudicator.py`

Current size signals:

| File | Lines | Main issue |
| --- | ---: | --- |
| `normalize.py` | 2,332 | label parser, benchmark repair, gold policy, selected-evidence derivation, diary parsing, cluster parsing |
| `pipeline_v1.py` | 2,119 | deterministic orchestration, schemas, rate extraction, cluster extraction, selection, temporal helpers |
| `llm_only_structured_events.py` | 2,070 | prompt, DSPy module, schema parsing, repair stack, temporal derivation, scoring, reporting |
| `llm_only_claim_table_selector.py` | 1,241 | prompt, parser, scoring layers, component status, reporting |
| `hybrid_rules_candidates_llm_adjudicator.py` | 1,141 | prompt, parser, deterministic candidate packaging, scoring, reporting, CLI |

Why this matters:

Large files are not automatically wrong, but these files combine research
concepts that need independent attribution. When label repair, gold policy,
semantic derivation, parser repair, scoring, and report writing share a file,
future changes become harder to review. More importantly, it becomes easier to
accidentally describe a repair-heavy result as a model result.

Concrete fix:

Split by stable concept, not by superficial helper type:

- `label_parser.py`: Gan label grammar, yearly/monthly conversion, sentinels.
- `benchmark_repair.py`: prediction-label format repair and trace objects.
- `gold_policy.py`: clean scorer-facing gold-normalization policy.
- `selected_evidence_derivation.py`: deriving Gan labels from model-selected
  evidence.
- `temporal_windows.py`: clinic dates, elapsed months, dated event windows.
- `deterministic_extractor.py`: candidate extraction orchestration.
- `deterministic_selector.py`: final selection scoring and rationale.
- `llm_records.py`: shared row/run record structures for LLM artifacts.
- `reports.py`: markdown and JSON summary writers.

Do this incrementally. Each split should preserve behavior first, then simplify.

### P1: Deterministic V1 Shows Validation Overfit And Should Stay Frozen

Files:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/pipeline_v1.py`
- `tests/test_gan2026_pipeline_v1.py`
- `docs/research/gan2026_deterministic_rule_review_2026-05-31.md`
- `docs/research/gan2026_current_pipeline_results_report_2026-06-01.md`

Existing project reports already record the decisive signal:

- deterministic V1 validation Purist: 0.9293
- deterministic V1 locked test Purist: 0.7600

Why this matters:

That gap is too large to treat as ordinary split noise. It suggests late
deterministic rule additions learned validation phrasing families rather than
stable clinical extraction principles. The current code still contains the
shape of that history: a very large deterministic extractor and a very large
example-literal regression suite.

Concrete fix:

- Do not add new behavior to deterministic V1 except bug fixes that preserve its
  frozen comparator role.
- Put any new deterministic idea into a named candidate pipeline.
- Require ablation metadata and paraphrase/adversarial tests for new
  deterministic behavior.
- Keep locked test aggregate as historical context; do not inspect locked test
  row-level failures for development.

### P1: Repair Modes Are Configurable But Not Yet First-Class Enough

Files:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_only_structured_events.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_only_structured_events_repair_ablation.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/normalize.py`
- `docs/research/gan2026_current_pipeline_results_report_2026-06-01.md`

`StructuredRepairConfig` exposes useful repair-family switches:

- basic label repair
- clean scorer-facing gold policy
- selected-evidence repair
- monthly diary repair
- usual interval repair
- breakthrough repair
- non-epileptic repair
- residual jerk repair
- post-change burst repair
- dated sequence repair
- elapsed anchor repair

The problem is not that these switches exist. The problem is that the default
config enables a broad hybrid repair stack. That default is convenient for
development, but dangerous for claim language.

Why this matters:

The current reports correctly say that high structured-LLM scores are
repair-heavy hybrid diagnostics. Future code should make it mechanically hard
to forget that boundary.

Concrete fix:

- Replace free-floating booleans with named modes:
  - `raw_model`
  - `strict_format`
  - `clean_scorer_facing`
  - `selected_evidence_derivation`
  - `hybrid_full_stack`
- Make the report title, metadata, and summary table display the repair mode
  prominently.
- Require mode in artifact filenames or run registry entries.
- Treat `hybrid_full_stack` as hybrid by construction, not as an LLM-only result
  with extra options.

### P1: Validation Ladder Policy Is Documented But Not Enforced In The Main CLI

File:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_pipeline_cli.py`

The split protocol says LLM/hybrid work should escalate 25 -> 50 -> 250, and
full 750-row validation runs should be rare and justified. The main CLI records
`--escalation-reason`, but it does not enforce or warn on broad validation
runs.

Why this matters:

This is a small missing guardrail with a large research-process payoff. Without
it, a tired future run can accidentally normalize full-validation iteration as
ordinary development.

Concrete fix:

- Warn or fail when `--split validation` and `--limit` is absent or greater than
  250 unless `--escalation-reason` is provided.
- Keep `test` unavailable from routine LLM CLI commands.
- Add a separate frozen-evaluation command later if/when holdout evaluation is
  allowed.

### P2: `core/` Is Not Fully Task-Neutral

Files:

- `src/clinical_extraction/core/schemas.py`
- `docs/design/architecture.md`

`core/schemas.py` defines `SeizureEvent`, while the architecture doc says
`core/` should contain task-neutral primitives.

Why this matters:

This is small now, but it is exactly the kind of early boundary leak that later
makes a supposedly reusable package feel Gan/seizure-specific. The package is
young enough to correct this cheaply.

Concrete fix:

- Move `SeizureEvent` into the seizure-frequency task package.
- Keep `core/` limited to generic evidence spans, pipeline containers,
  validation issues, and task-neutral base models.

### P2: Static Typing Is Present But Not Yet A Useful Refactor Guardrail

Files:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/evaluate.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/normalize.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/pipeline_v1.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_only_structured_events.py`
- `src/clinical_extraction/core/pipeline.py`

`python -m mypy src` reports 31 errors. Some are configuration noise around
untyped DSPy imports, but several are real internal type-shape problems:

- metrics dictionaries mix string labels and float values in ways mypy cannot
  verify;
- optional regex groups are passed to `float`;
- date/month helpers return optional pieces that callers treat as definite;
- generic pipeline type variables have the wrong variance.

Why this matters:

The next work phase requires moving code without changing behavior. Mypy does
not need to be perfect, but it should catch accidental type-shape regressions in
the modules being split.

Concrete fix:

- Add a pragmatic mypy config for untyped third-party packages.
- Fix internal type errors in small batches.
- Start with `core/pipeline.py`, `evaluate.py`, and the date helper errors
  before splitting temporal logic.

### P2: Tests Are Broad But Too Example-Literal

Files:

- `tests/test_gan2026_pipeline_v1.py`
- `tests/test_gan2026_normalize.py`
- `tests/test_gan2026_llm_only_structured_events.py`

The suite has 582 collected tests, which is excellent for a young repo. The
problem is shape, not quantity. The largest tests encode many specific snippets
and expected labels. That is useful regression coverage, but it also makes the
next natural fix "add one more pattern for this exact phrase."

Why this matters:

Example-literal tests preserve known behavior but do not force generality. The
repo needs more invariant tests that protect the research contract.

Concrete fix:

Add focused invariant tests for:

- repair modes do not cross attribution boundaries;
- alias repair does not add clinical content;
- evidence validity remains exact or explicitly invalid;
- no-reference, unknown, seizure-free, and unresolved-multiple remain distinct
  before scoring collapse;
- disabling a rule group removes only that group's behavior;
- temporal-window helpers choose documented month-span semantics;
- broad validation requires escalation metadata;
- artifact rows preserve `source_row_index`, split, split manifest, model,
  prompt version, repair mode, and reuse/cache status.

### P2: Experiment Artifacts Need A Registry

Directory:

- `experiments/`

The repo currently has 226 top-level experiment files, including 95 JSONL files.
This is good for traceability, but the naming history is now dense enough that
filenames alone are no longer a reliable project-control surface.

Why this matters:

When artifacts accumulate quickly, "latest" becomes ambiguous. A future reader
needs to know whether an artifact is live, replay, schema replay, rejected,
superseded, promotion candidate, or historical context.

Concrete fix:

Create a lightweight run registry, probably `experiments/registry.jsonl` or
`experiments/RUN_INDEX.md`, with:

- run id
- artifact paths
- date
- pipeline family
- split and row count
- model and role
- mode/replay status
- repair config or named repair mode
- cache/reuse source
- primary metrics
- evidence validity
- decision: promote, revise, reject, superseded, historical
- supersedes/superseded-by
- claim language notes

This does not replace raw artifacts. It makes them navigable.

### P3: Generated And External Reference Files Are Tracked Too Loosely

Paths:

- `data/Gan (2026)/previous implementation/`
- `experiments/*.jsonl`
- `experiments/*.json`

The repo tracks prior implementation scripts and many large-ish experiment
artifacts. That may be intentional for research reproducibility, but the policy
is not explicit enough.

Why this matters:

Research repos often need to version artifacts. But if everything is tracked
equally, source code, canonical reports, raw outputs, and scratch replays become
hard to distinguish.

Concrete fix:

- Decide which artifact classes are canonical and which are scratch.
- Document artifact retention policy in `experiments/README.md`.
- Keep historical scripts only if they are referenced as provenance; otherwise
  move them under a clearly named provenance folder.
- Consider storing bulky raw JSONL outside normal review flow once the run
  registry points to them.

## Reliable Improvements

These are high-confidence changes that should improve the project without
changing the research thesis.

### 1. Fix Schema Repair First

This is the only current red test surface and should be fixed before broad
refactoring.

Desired outcome:

- `pytest -q` passes.
- Shared repair remains alias-only.
- Parser-specific defaults are explicit and tested.

### 2. Add CLI Validation-Ladder Guard

This is small and aligns with existing `PROJECT_STATUS.md`.

Desired outcome:

- broad validation runs require an escalation reason;
- routine CLI remains train/validation only;
- reports keep recording escalation reason.

### 3. Introduce Named Repair Modes

This reduces attribution drift immediately.

Desired outcome:

- every LLM artifact says whether it is raw, strict, clean, selected-evidence
  derivation, or full hybrid;
- "LLM-only" claims cannot accidentally include hybrid repair.

### 4. Move `SeizureEvent` Out Of `core`

This is low-risk and protects the architecture boundary early.

Desired outcome:

- `core/` is genuinely task-neutral;
- seizure-frequency schemas live under the seizure-frequency task.

### 5. Make Mypy Pragmatically Useful

This should happen before large file splitting.

Desired outcome:

- untyped DSPy imports are configured intentionally;
- internal type errors are burned down;
- future module splits have a lightweight static safety net.

### 6. Split Report Writing Out Of Pipeline Modules

This is usually a safer first split than changing core behavior.

Desired outcome:

- behavior-preserving extraction of markdown/JSON reporting;
- pipeline modules become easier to scan;
- future report changes do not touch parsing/extraction code.

### 7. Create Experiment Run Registry

This improves research continuity without changing pipeline behavior.

Desired outcome:

- one durable index says which run is latest, rejected, promoted, or superseded;
- project status can link to registry entries instead of ambiguous filename
  families.

## Thorny Problems

### Attribution Is The Central Research Problem

The strongest current scientific question is not "rules or LLMs?" It is:

What semantic work is performed by the model, what semantic work is performed by
deterministic code, and what work is merely benchmark-format normalization?

This repo is unusually close to answering that, because it already records raw,
strict, clean, and hybrid repair ladders. The danger is that default configs and
informal wording can blur those boundaries.

Long-term answer:

- prediction-bearing ownership must be explicit in pipeline names;
- repair modes must be named, ablated, and reported;
- metric tables must separate raw model selection from deterministic derivation.

### Temporal Semantics Are The Task, Not A Helper Detail

The hard rows revolve around:

- last event versus current frequency;
- seizure-free since a date versus recent breakthrough;
- current/recent/historical windows;
- diary months and partial elapsed windows;
- clusters with cadence and within-cluster burden;
- brief seizure-free spans after recent counted events.

These are not just label formatting problems. They are the clinical reasoning
problem. They need typed intermediate state and explicit temporal policies,
otherwise regex and repair functions will keep absorbing semantic decisions.

Long-term answer:

- define a task-level temporal window model;
- store anchor date, window start/end, count, cadence, and uncertainty where
  possible;
- make final selection reason over those structures rather than over strings
  alone.

### Benchmark Compatibility And Clinical Generality Pull In Different Directions

Gan labels require very specific output strings. Clinical extraction wants
source-near, semantically rich state. The project already knows this, but the
implementation still sometimes routes both through the same functions.

Long-term answer:

- keep clinical state rich until the final scorer-facing boundary;
- make benchmark-format repair explicitly non-clinical;
- make gold-normalization policy a separate layer with direct citation and
  frozen scope.

### The Test Suite Needs To Stop Incentivizing One More Regex

The current tests are valuable. They also preserve the path that produced
validation overfit: find a missed phrase, add a pattern, add a snippet test.

Long-term answer:

- keep regression snippets, but surround them with invariants;
- add adversarial/paraphrase tests for portable rules;
- require every new deterministic behavior to name its portability and ablation
  impact.

## Proposed Fix Sequence

### Phase 1: Restore Green And Guard The Protocol

1. Fix shared schema repair defaults.
2. Run full pytest.
3. Add validation-ladder guard to `gan2026-llm-experiment`.
4. Add focused CLI tests for broad-validation escalation.

### Phase 2: Make Attribution Mechanical

1. Add named repair modes.
2. Update structured-events report metadata and titles.
3. Update repair ablation tooling to use named modes.
4. Add tests that "LLM-only clean" mode cannot use hybrid semantic repair.

### Phase 3: Protect Architecture Boundaries

1. Move `SeizureEvent` out of `core/`.
2. Add or fix mypy config.
3. Burn down internal mypy errors in `core`, `evaluate.py`, date helpers, and
   the CLI spec protocol.

### Phase 4: Split Low-Risk Presentation Code

1. Extract report writers from LLM pipeline modules.
2. Extract run metadata helpers into a shared module.
3. Add snapshot-ish tests for report sections that matter for claim language.

### Phase 5: Split High-Risk Behavior Code

1. Extract Gan label parser from `normalize.py`.
2. Extract benchmark repair and gold policy from `normalize.py`.
3. Extract selected-evidence derivation from `normalize.py`.
4. Extract temporal/date helpers into one owned module.
5. Extract deterministic final selection from `pipeline_v1.py`.

Every step in this phase should be behavior-preserving first.

### Phase 6: Create The Run Registry

1. Define registry schema.
2. Backfill only canonical/high-signal runs first.
3. Update `PROJECT_STATUS.md` to reference registry entries.
4. Stop relying on "latest filename" as project memory.

## Suggested First Work Item

Start with the schema repair failure.

Reason:

- It is concrete and currently red.
- It exercises the exact boundary discipline the repo needs: shared repair
  versus pipeline-specific defaults.
- It is small enough to fix and verify before the broader refactor begins.

Expected patch shape:

- update `schema_repair.py`;
- add or adjust tests in `test_gan2026_schema_repair.py`;
- run `python -m pytest tests/test_gan2026_schema_repair.py -q`;
- run full `python -m pytest -q`.

## Closing Assessment

The codebase is not rotten. It is alive in the slightly dangerous way a young
research repo gets alive: the experiments are teaching the architecture faster
than the architecture is being cleaned up.

The thesis is still intact. In fact, the strongest result so far is the
decomposition itself: Gan 2026 seizure-frequency extraction needs explicit
temporal reasoning, semantic-state handling, benchmark normalization, evidence
validation, and repair attribution. The next step is to make the code embody
that decomposition as clearly as the reports already describe it.
