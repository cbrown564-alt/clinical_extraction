# 0048: Refocus the repository for comprehension, live use, and external validation

Date: 2026-08-02
Status: accepted; implementation in progress and currently paused

## Decision

Refactor the repository over the next working week into a clean research system
that is immediately useful to a supervisor and remains ready for new runs and
external validation. The goal is not a retrospective evidence archive and not
an expansion into a clinical deployment system. It is a working codebase,
frontend, evidence set, and explanation package with one clear path from the
system story to live execution, exact replay, and stated limits.

The retained operational system must support:

- the six selected models across the three selected methods and two tasks;
- live runs and saved/fixture demonstrations;
- full permitted development-split workflows in the frontend;
- exact no-call replay of selected results from saved raw outputs;
- the prompt, component, negative, and safety evidence needed to explain the
  selected methods, including the essential DeepSeek and Luna studies; and
- a focused, restricted research-validation workflow for future real-patient
  data, without presenting it as clinical deployment.

Everything else is a deletion or simplification candidate. Historical material
must be reviewed for value and regeneration status before removal. A retained
item must serve at least one of these purposes:

1. explain the system;
2. demonstrate a selected method;
3. support a named evidence claim;
4. reproduce a selected result; or
5. state a limitation, decision, or historical reason needed to prevent
   misunderstanding.

## Supervisor-facing completion standard

The final repository must let a supervisor, without agent assistance:

- understand the system from the README and concise supervisor path;
- open the frontend and run the selected development workflows;
- inspect one teaching letter through all six task-method paths;
- see one deliberate failure and its recovery or containment;
- find the canonical results report, evidence/limits table, and reproduction
  commands; and
- distinguish engineering verification, research evidence, clinical review,
  and clinical validation.

The frontend is the primary interactive demonstration. The teaching case is its
explanatory companion. Both saved/fixture mode and clearly marked live one-row
mode remain available.

## Reproduction standard

Selected results use protocol reproduction plus exact replay. A new run must
record the same task, model, method, prompt/program version, route, split,
repair policy, scorer, and run metadata. The original raw output must be
retained so the reported result can be replayed exactly without another model
call. Exact live model text is not promised for nondeterministic providers.

## Cleanup rules

- Active source, tests, frontend routes, configuration keys, and documentation
  may receive breaking renames when every retained caller and workflow is
  migrated and verified.
- Remove obsolete compatibility facades, historical paths, duplicate reports,
  and unused infrastructure after dependency and evidence review.
- Keep one canonical owner for each durable concern; other documents link to it.
- The main story covers the selected six methods. Historical candidates belong
  in focused decision evidence or a replay-only area.
- The cleanup is behavior-preserving by default. Clinical meaning, scoring,
  splits, prompts, model routing, and evidence policy require a separate
  predeclared study and verification if changed.
- External-validation runs require a readiness record naming the data owner,
  permitted dataset, split policy, technical run owner, independent clinical
  reviewer, review process, and claim boundary.

## Required owner documents and outputs

- `README.md` is the front door.
- `PROJECT_STATUS.md` owns current evidence and checks.
- `docs/canon/10_paper_provenance.md` owns claim strength and limits.
- `docs/REGENERATION.md` owns regeneration and historical-artifact triage.
- Source manifests and generated architecture documents own current stage
  definitions.
- One canonical results report owns the six-model, three-method, two-task
  results matrix. Focused reports own prompt, component, negative, safety, and
  validation evidence.

## ExECT `llm_with_rules` vertical-slice gate

This is the next execution phase after the verified `rules` and `llm` slices.
It is a behavior-preserving migration of the selected Decision 0046 Sol
hybrid, not a new model, prompt, scorer, repair policy, or experiment.

### Entry gate

Work may start only from merged `main` with the ExECT `llm` slice green. The
implementation must pin the governed baseline commit and the full permitted
`dev140` comparison fingerprint. It must use the Decision 0041 structured
one-call producer and Decision 0040 family ownership with
`diagnosis_policy_variant="default"` and
`prescription_policy_variant="default"`. No model call or locked-row access is
part of the migration gate.

### Required implementation invariants

- The active public identity is `llm_with_rules`. Saved frontend run IDs,
  retained-evidence IDs, manifest IDs, filenames, prompt/program versions, and
  artifact hashes remain immutable and occupy separate provenance fields.
  Resolution accepts a unique exact active, saved, retained, or supported
  legacy alias and rejects collisions across those fields in both backend and
  frontend.
- `run_llm_with_rules_letter` consumes the same immutable
  `produce_structured_letter` result used by `run_llm_only_letter`.
  `run_primary_pair` makes exactly one producer call per letter; batch callers
  reuse one configured program and preserve route, cache, mode, retry, and raw
  output provenance. The hybrid must not make a second model call or invoke an
  independent family extractor.
- Only the selected `default/default` assembly is active. The archived
  `combined` policy, `v08`, GEPA, and rejected candidate switches must be
  unavailable through the selected runner. Historical replay, where retained,
  requires an explicitly named opt-in path.
- The trace keeps raw model clinical selection separate from deterministic
  format, representation, family-transform, evidence, and final-view stages.
  Stage order, IDs, actions, component owners, first owner/failure, mention
  order, attributes, evidence, fact origin, and scorer-facing raw and final
  projections must remain attributable.
- Public runner, API, CLI, operational, split/checkpoint/resume, teaching, and
  frontend paths delegate to the canonical orchestrator. LLM split access is
  row-level `dev`/`dev140` only and requires an explicit `live`,
  `prompt-only`, or `replay` mode. Every forbidden split or mode must reject
  before consuming input, reading checkpoints, or configuring a provider.
  Live mode rejects supplied raw outputs; replay preflights an exact complete
  ID set; prompt-only makes no call; resume preserves completed-ID call counts.

### Evidence and negative gate

An independent full-value replay over all 140 governed Sol development rows
must compare the pre-migration selected hybrid with the canonical path. The
fingerprint must cover the producer row, raw candidate, final prediction,
mentions and their order/attributes/evidence, parse and format-retry layers,
model/prompt/profile/route/mode fields, every stage action and owner, first
owner/failure, deterministic actions, and scorer raw/final projections. Only
the declared outward active identity transition may be excluded. A paired spy
test must additionally prove that `llm` and `llm_with_rules` receive the same
producer object and require one call per letter.

Negative probes must cover malformed and schema-blocking output, empty and
partial families, evidence-invalid findings, duplicate/order behavior, SF
projection and unknown suppression, mismatched producer/letter IDs, archived
policy rejection, every forbidden split and mode, incomplete replay maps,
checkpoint resume, fresh-provenance absence, alias collisions against the
hydrated six-run payload, legacy delegation, and absence of any second
producer or independent extractor call.

### Exit and stop gate

Before integration, generated architecture and teaching claims must describe
the selected one-call four-family hybrid and regenerate check-clean. Hydrated
Git LFS evidence, retained-manifest verification, all six no-call reference
replays, locked-artifact safety, the full backend suite, Ruff, mypy, frontend
unit tests, type checking, lint, and production build must pass. A Sol strict
post-change review must report no actionable finding.

Stop and open a separate decision or predeclared study for any prompt, model,
route, scorer, split, clinical meaning, assembly policy, evidence policy, or
call-count change; any locked-row exposure; any unexplained parity difference;
or any route from the selected API into an archived policy.

## Completion gate

Completion requires no unexplained obsolete active labels, broken internal
links, duplicate durable owners, stale claims outside the canonical results
report, unexplained retained artifacts, or unverified selected live and replay
paths. Generated architecture and frontend outputs must be rebuilt and checked.

This decision does not establish clinical validity. Independent clinical review
and external validation remain open work.
