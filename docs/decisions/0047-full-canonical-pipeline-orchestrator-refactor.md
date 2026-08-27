# 0047: Consolidate selected pipelines behind canonical orchestrators

Date: 2026-08-01  
Status: accepted; implementation authorized

## Decision

Proceed with the full Phase 5 refactor proposed by the pipeline
understandability review. Each selected task-method pipeline will have one
authoritative prediction-bearing orchestrator. Research runners, split
runners, operational wrappers, saved-output replay paths, and trace
projections will delegate to that orchestrator instead of independently
restating prediction-bearing processing order.

The refactor may reorganize and rename existing implementation boundaries,
introduce typed stage inputs and outputs, and remove duplicated execution
ownership. It must preserve the selected method definitions and the current
research decisions, including:

- Gan hybrid model-owned initial event selection followed by attributable
  deterministic correction;
- ExECT decision-0040 family ownership;
- ExECT decision-0041 one structured model call per letter;
- ExECT decision-0045 `default` / `default` assembly policy; and
- ExECT decision-0046 primary comparison method identities.

## Required invariants

The refactor must not silently change:

- final predictions or score representations;
- selected or supporting evidence;
- model origin, deterministic actions, or first prediction-changing owner;
- stage ordering where ordering affects clinical meaning;
- schema, format-repair, retry, fallback, unknown-suppression, or
  evidence-validation policy;
- split selection, locked-data restrictions, or retained evidence identity;
- trace meaning or operation ownership.

If a semantic output changes, the change must be treated as a new recorded
pipeline version with an explicit decision and replay evidence. A cleaner
module layout alone is not evidence of equivalence.

## Implementation sequence

The refactor will be delivered in the phases below. Each phase has an exit gate;
the next phase must not begin for a method whose gate is red. Work may proceed
method by method, but a partial migration must remain explicit in the stage
manifests and must not be described as completion of this decision.

### Phase 0: correct the selected-method inventory

Before freezing behavior, reconcile the architecture layer with decisions
0045 and 0046.

1. Change the selected ExECT LLM-only manifest and teaching case from the
   historical GEPA program to the Sol-matched `raw_candidate` / `raw_lane_score`
   view produced by the current one-call structured pipeline. Keep GEPA as a
   named historical or negative comparator.
2. Make the selected ExECT rules-only manifest show both truths: the rules-only
   pipeline may extract all nine entity types, while the primary comparison
   projects only Diagnosis, Seizure Frequency, Prescription, and
   Investigations into clinical fact recovery (`clinical_headline`).
3. Confirm that the selected ExECT hybrid configuration is one structured call
   with `default` / `default` Diagnosis and Prescription policy. The archived
   `combined` / `combined` policy must require an explicit historical-replay
   entry point.
4. Inventory every current caller of the six selected paths and classify it as
   a research runner, split/checkpoint runner, operational wrapper, no-call
   replay, trace or teaching projection, scorer, or historical path. Record the
   inventory in the stage manifests rather than creating a second architecture
   register.
5. Resolve the existing operational-policy drift before using operational
   output as a parity baseline. In particular,
   `src/clinical_extraction/operational/exect.py` still names the
   joint bounded rule set, and `src/clinical_extraction/operational/exect.py`
   enables a Diagnosis candidate directly. If those paths change clinical
   output when brought into line with decision 0045, make that correction in a
   separate commit and recorded operational version. Do not hide it inside an
   otherwise output-preserving refactor.

**Exit gate:** the six manifests describe the methods selected by decisions
0040, 0041, 0045, and 0046; historical controls are visibly separate; every
active caller has one recorded migration destination; and any pre-existing
policy drift has an explicit disposition.

### Phase 1: build the parity harness before moving code

Add a no-call parity checker, tentatively
`scripts/check_canonical_orchestrator_parity.py`, and focused tests under
`tests/`. The checker compares a frozen pre-refactor baseline with the new
orchestrator result after normalizing only an explicit allowlist of
non-semantic run metadata such as generated timestamps and output paths.

The baseline must cover two different sets:

1. **Current selected-method baseline.** Exercise the six task-method pairs as
   they are defined after Phase 0, using permitted development rows and saved
   raw model outputs. This is the behavior the new orchestrators must preserve.
2. **Retained historical reference baseline.** Run
   `scripts/verify_reference_evidence.py` and the existing retained replay
   checks. Three retained ExECT reference cells are historical or negative
   comparators, so this check protects reproducibility but is not a substitute
   for the selected-method baseline.

Freeze small no-call characterization fixtures for the following cases:

| Method | Required fixture coverage |
| --- | --- |
| Gan rules only | Ordinary extraction; no scorable extraction; competing current versus year-to-date rates; exact-evidence boundary; selection tie or ordering case. |
| Gan LLM only | Valid structured answer; JSON-dialect repair; selected-evidence label repair; unscorable label; evidence not contained; blocking malformed output. |
| Gan LLM with rules | Valid no-repair answer; one fixture for every selected repair family; multiple eligible repairs to lock order; format-only retry accept and reject; missing selection; unscorable label; invalid evidence. |
| ExECT rules only | Ordinary all-nine extraction; duplicate mentions; negation or absence; heading/context recovery; exact evidence; four-family comparison projection. |
| ExECT LLM only | The current one-call structured raw lane; all four families; malformed output; evidence-invalid finding removal; empty family; ordering and deduplication. GEPA fixtures remain historical tests only. |
| ExECT LLM with rules | All four family transforms; SF projection and unknown suppression; exact-evidence failure; `default` / `default`; archived-policy rejection; one-call producer reuse; empty and partial model output. |

Fixtures must contain synthetic notes or permitted development rows only. Raw
model output must be stored separately from deterministic output so replay can
enter exactly at the model boundary.

**Exit gate:** the old path passes the new parity harness; every
prediction-changing stage has at least one governing unit test; selected repair
order is characterized; and no live model call or locked-row inspection was
used.

### Phase 2: introduce narrow typed contracts and prove one slice

Create task-local orchestration packages rather than a cross-task workflow
framework:

```text
src/clinical_extraction/tasks/seizure_frequency/gan2026/orchestration/
  contracts.py
  rules.py
  llm.py
  llm_with_rules.py

src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/
  contracts.py
  rules.py
  structured_one_call.py
```

These paths are the intended shape, not permission to move stable clinical
logic merely for symmetry. Existing stage functions should remain in place
until a move has a concrete ownership or readability benefit.

The per-record or per-letter orchestrator contract must:

- accept a typed task record and an immutable selected-method configuration;
- accept a model-output source that can be live, fixture-backed, or saved-output
  replay without changing downstream processing;
- return the final prediction, selected and supporting evidence, stage events,
  component actions, ownership, validation result, failure state, and any
  scorer-ready projection;
- keep raw model output, parsed model output, deterministic intermediate state,
  and final output separately accessible;
- use stable stage IDs from the architecture manifests; and
- avoid file I/O, split selection, checkpointing, progress reporting, provider
  configuration, and aggregate reporting.

Scoring may remain a separate pure adapter because operational inference has no
gold answer. It must consume the settled orchestrator output and must never
rewrite it. A research runner may call the orchestrator and then the scorer,
but it may not repeat a prediction-bearing stage.

Prove the pattern first with Gan rules only. Its existing explicit stage
functions and `run_item` provide the lowest-risk slice. Route one research
entry point through the new typed result while keeping the old public return
shape through a compatibility adapter.

**Exit gate:** Gan rules-only old and new paths are identical under the parity
harness; its split runner delegates; its method manifest points to the new
entry point; and the compatibility adapter contains no clinical rule or stage
ordering.

### Phase 3: migrate the remaining Gan methods

Extract one-record orchestration from the large `run_split` loops for Gan
LLM-only and Gan LLM-with-rules. Keep batch concerns in their current runners
until per-record parity passes.

For Gan LLM-only, the orchestrator must visibly order:

```text
prompt input -> model/replay output -> JSON repair -> schema validation
-> selected-evidence semantic repair -> scorable-label check
-> exact-evidence check -> scorer projection
```

For Gan LLM-with-rules, the orchestrator must visibly order:

```text
prompt input -> model/replay output -> JSON/schema repair
-> optional format-only retry -> schema validation -> event normalization
-> retain and resolve the model selection -> selected-evidence repair
-> the named repair families in their frozen order -> scorable-label check
-> exact-evidence check -> scorer projection
```

Pass prompt version and repair mode explicitly. Remove selected-path reliance
on process-global prompt mutation only after replay callers have explicit
configuration. Preserve all current retry decisions, error strings, trace
events, and checkpoint row shapes through adapters.

Migrate in this order:

1. the primary research runner;
2. no-call raw-output replay;
3. split/checkpoint/resume runner;
4. teaching-case and trace projections; and
5. operational or local wrappers.

**Exit gate:** every active Gan caller delegates to one of the three
orchestrators; every selected repair family remains attributable; saved-output
replays are equal; and no active wrapper imports a prediction-changing stage
function directly.

### Phase 4: migrate ExECT rules only

Wrap `extract_deterministic_all9` as the prediction-bearing core rather than
rewriting its extractors. Add an explicit, pure four-family comparison
projection for decision 0046. Keep the all-nine output available for the
published-metric secondary view.

The contract must make entity filtering a scorer-facing projection, not an
implicit change to deterministic extraction. Dedupe order, evidence, negation,
attributes, CUI normalization, and mention identity must remain exact.

**Exit gate:** all-nine output is identical; the four-family dev140 and
aggregate-only test60 artifacts reproduce; and the manifest distinguishes the
prediction from the primary comparison projection.

### Phase 5: migrate the ExECT one-call pair

The ExECT LLM-only and LLM-with-rules primary rows share the same structured
model producer. Implement that fact directly:

- `produce_structured_letter` owns prompt construction, one model or replay
  read, format-only retry, schema parsing, event flattening, and the first
  model-origin trace;
- `run_llm_only_letter` projects the saved producer result to the decision-0046
  `raw_candidate` method output and evidence gate;
- `run_llm_with_rules_letter` applies SF projection/suppression, finding-store
  registration, the four selected family transforms, exact-evidence
  enforcement, and final view materialization; and
- `run_primary_pair` obtains one producer result and passes the same immutable
  object to both method projections. A test must assert one producer call per
  letter.

The selected hybrid entry point must hard-code or validate
`diagnosis_policy_variant="default"` and
`prescription_policy_variant="default"`. Archived `combined` replay must use a
separate, clearly named opt-in entry point. Do not carry experiment candidate
booleans into the selected orchestrator API.

Refactor `src/clinical_extraction/operational/exect.py` and
`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/assembly/pipeline.py`
to share the same typed letter assembly function. The operational wrapper may
own endpoint credentials, provider timeout, privacy, error serialization, and
response formatting; the saved-output replay may own artifact loading and
aggregate reporting. Neither may own a second assembly order.

Migrate the primary research runner first, then the selected no-call assembly,
the operational wrapper, the local clinical-findings wrapper, the teaching
case, and trace/report projections.

**Exit gate:** the current six-model dev140 raw and final stage outputs replay
identically; aggregate-only test60 stage panels remain identical; exact
evidence, fact origin, deterministic actions, and first prediction-changing
owner are unchanged; one-call count is enforced; and operational and replay
assembly call the same function.

### Phase 6: cut over every entry point and quarantine duplicates

For each inventory item from Phase 0, add a delegation test that replaces the
orchestrator with a spy and proves that the wrapper calls it with the expected
configuration. Add a structural test that fails when an active wrapper imports
selected prediction-changing stage functions directly.

Only after its method-level and full replay gates pass:

1. remove duplicated loops and assembly code;
2. retain compatibility imports only where a supported command or artifact
   depends on them;
3. move historical `v08`, GEPA, joint/combined, and rejected candidates out of
   the selected reading path without deleting replay support; and
4. label any remaining legacy path with its role, supported artifact, and
   removal condition.

Do not delete a compatibility shim in the same change that first routes a
caller through it. Use a later cleanup change so rollback remains simple.

**Exit gate:** every active caller delegates; duplicate prediction-bearing
ownership is zero by the structural test; historical replays still run; and
removing the old loop cannot change a selected result because no active caller
reaches it.

### Phase 7: regenerate explanations and close the decision

Update the manifest schema if needed to distinguish canonical orchestrators,
delegated entry points, historical paths, and scorer adapters. Regenerate the
method cards, diagrams, teaching cases, and code maps. Update runbooks and
`PROJECT_STATUS.md` only after the parity artifact is final.

The final human-readable result belongs under `docs/experiments/` and should
link to one machine-readable summary under `experiments/`; it must not become a
second status board or evidence register. Record the source commit, environment
lock, selected configurations, input artifact hashes, comparison field set,
allowed metadata exclusions, commands, and results.

**Exit gate:** all verification gates below pass from a clean checkout with the
documented repository environment; generated architecture docs are current;
the primary code-reading path is reachable from each method card within two
links; and `PROJECT_STATUS.md` records the refactor as implemented and verified,
not clinically validated.

## Intended orchestrator map

| Selected method | Canonical entry point | First migration target | Highest-risk invariant |
| --- | --- | --- | --- |
| Gan rules only | `gan2026.orchestration.rules:run_record` | `runners/deterministic_canonical.py` | Candidate order, current-event selection, rendered evidence, and ablation configuration. |
| Gan LLM only | `gan2026.orchestration.llm:run_record` | `llm/llm_only_canonical_pipeline.py:run_split` | Selected-evidence repair remains deterministic-owned and no retry/failure behavior changes. |
| Gan LLM with rules | `gan2026.orchestration.llm_with_rules:run_record` | `llm/hybrid_structured_events.py:run_split` | Model-owned initial selection, frozen repair order, repair attribution, and explicit prompt/repair configuration. |
| ExECT rules only | `exectv2.orchestration.rules:run_letter` | `deterministic/all_entities/orchestrator.py` | All-nine predictions stay intact while the primary comparison uses an explicit four-family view. |
| ExECT LLM only | `exectv2.orchestration.structured_one_call:run_llm_only_letter` | `key_entities_structured/runner.py` raw lane | Decision-0046 raw lane replaces GEPA as selected; the producer output is shared, not recalled. |
| ExECT LLM with rules | `exectv2.orchestration.structured_one_call:run_llm_with_rules_letter` | `assembly/pipeline.py` and `operational/exect.py` | One call, decision-0040 ownership, `default` / `default`, exact evidence, and one assembly order. |

Public names may change during implementation if the resulting path is
clearer. The method manifest must point to the final callable, and the six
selected callables must remain separately discoverable even where they share a
producer.

## Contract guardrails

- **No cross-task workflow engine.** Share small evidence, trace, or result
  types only when both tasks already have the same meaning. Gan labels and
  ExECT findings must not be forced into one generic clinical result.
- **No hidden clinical work in adapters.** Compatibility adapters may rename
  fields or serialize typed results. Any add, remove, select, suppress, repair,
  or meaning-changing normalization remains a named stage with an owner.
- **No mutable selected policy.** Selected method configurations are immutable.
  Ablations and archived policies use separate explicit configurations and
  cannot become defaults through a missing argument.
- **No split loading in the orchestrator.** Split manifests, locked-data rules,
  resume validation, and row ordering remain runner concerns and are tested at
  the runner boundary.
- **No live dependency in replay.** A replay source must satisfy the same typed
  model-output boundary without importing or configuring a live provider.
- **No model SDK objects after the provider boundary.** Convert provider
  responses into repository-owned typed records before deterministic work.
- **No gold in prediction stages.** Gold labels may enter only the scorer or a
  parity comparator. The orchestrator cannot branch on correctness.
- **No silent trace rewrite.** Stage ID, owner, effect class, before/after value,
  evidence, action, and first-failure meaning are part of the behavior freeze.
- **No reordered collections by convenience.** Mention, event, warning, repair,
  and provenance order must remain stable unless an explicit semantic decision
  permits a new version.
- **No deletion before delegation.** Preserve old code until the active callers
  delegate and both parity suites pass.
- **No claim upgrade.** Equivalent output proves implementation parity and
  clearer ownership. It does not prove better extraction, transfer, clinical
  validity, or production readiness.

## Evidence requirements

### Field-level parity

The machine parity artifact must compare, as applicable:

- source ID, split identity, prompt/program version, model route, repair mode,
  and selected policy;
- raw and retried model output identity;
- parsed model record and schema/parse failure codes;
- normalized events or findings, including order;
- final label or mention set and every scorer-facing view;
- selected and supporting evidence plus exact-substring validity;
- deterministic actions, rule family, fact origin, component owner, first
  prediction-changing owner, and first failure;
- warning, retry, fallback, unknown-suppression, and unscorable behavior;
- row-level score projections on permitted development data; and
- aggregate scores, denominators, failure counts, evidence counts, rescue and
  regression counts, and artifact hashes where the existing format fixes them.

Exact serialized equality is the default. A normalized comparison is allowed
only for a documented field such as a generated timestamp, absolute output
path, elapsed duration, or source commit that necessarily changes. The
allowlist is stored in the artifact; adding to it requires review.

### Required verification layers

| Gate | Evidence | Pass condition |
| --- | --- | --- |
| Contract | Unit tests for every stage and typed result | Every manifest stage executes, emits its trace event, and enforces its input/output invariant. |
| Characterization | Frozen no-call fixtures listed in Phase 1 | Old and new output match exactly after the fixed metadata allowlist. |
| Delegation | Spy tests for research, split, replay, operational, local, teaching, and trace callers | Every active caller invokes the canonical method entry point and owns no clinical stage order. |
| Selected-method replay | Permitted full development replay from saved outputs | Zero field-level differences for all six selected task-method pairs. |
| Locked aggregate safety | Existing aggregate-only test60/test450 checks and hashes | Aggregates and permitted fingerprints match; no locked row is printed, stored in a new artifact, or inspected. |
| Retained evidence | `scripts/verify_reference_evidence.py` and supporting replay checks | Every historical reference cell still reproduces, including the ExECT controls that are no longer selected methods. |
| Component attribution | Before/after action and first-owner summaries | Counts and row identities match on permitted data; every changed output has the same first owner and action sequence. |
| Architecture drift | `scripts/build_architecture_docs.py --check` and architecture tests | Manifests resolve to the canonical callables and all generated docs are current. |
| Repository quality | Full pytest, Ruff, and mypy through `.venv` | All pass with no new exclusions covering orchestrator code. |
| Clean-checkout replay | Documented no-call verification in a fresh checkout with retained LFS objects | Hashes, selected replays, generated docs, and repository checks reproduce. |

### Completion evidence

The refactor is **implemented** when all selected callers use the canonical
entry points and duplicate active ownership is removed or explicitly
quarantined. It is **verified** when every gate above passes and the evidence
artifact is retained. It is not **validated** unless separate clinical or
research evidence evaluates the unchanged outputs, and it is not **promoted**
until the repository's publication or operational release boundary is crossed.

## Known gotchas and required handling

1. **The current ExECT LLM-only manifest is stale.** It still describes GEPA,
   while decision 0046 selects the Sol raw lane. Correct the identity before
   freezing the selected-method baseline.
2. **The retained six-cell verifier protects history, not the whole selected
   architecture.** Its ExECT LLM-only and hybrid rows are GEPA and `v08`.
   Always run both parity suites.
3. **Operational ExECT policy has drifted.** Joint-bounded version labels and a
   directly enabled Diagnosis candidate conflict with decision 0045. Separate
   any semantic correction and version it before testing refactor parity.
4. **One ExECT model call feeds two paper rows.** Independent LLM-only and
   hybrid wrappers can accidentally double call or parse the same response
   differently. Share one immutable producer result and test the call count.
5. **ExECT has two assembly implementations.** Saved-output
   `assembly/pipeline.py` and live `operational/exect.py` currently restate the
   finding-store/lens order. Their inputs differ, but their per-letter assembly
   must converge on one function.
6. **Gan prompt choice is process-global in one path.** A refactor that runs
   conditions concurrently can leak prompt versions. Pass the version in the
   immutable request before parallel use.
7. **Retry is not merely an exception handler.** Adapter field recovery,
   format-only retry eligibility, retry validation, terminal provider errors,
   and placeholder-row behavior are retained semantics even when they do not
   change a successful prediction.
8. **Evidence validity can change row inclusion without rewriting a fact.** It
   must be compared separately from semantic output and must keep its
   validation-gate ownership.
9. **Order can be observable.** First-owner attribution, deduplication, repair
   precedence, JSONL hashes, and resume merging can all change when events or
   mentions are sorted differently.
10. **IDs have different representations.** Gan saved output uses integer
    `source_row_index`; ExECT uses string `letter_id`. Typed contracts must not
    coerce either into a shared generic ID that changes serialization.
11. **Rules-only ExECT has two legitimate views.** All-nine extraction and the
    decision-0046 four-family comparison must coexist. Do not simplify one away
    to make the orchestrators look symmetric.
12. **Archived policies must remain replayable but unreachable by default.** A
    compatibility argument with a permissive default is insufficient.
13. **A score match can hide mechanism drift.** Equality of aggregate F1 does
    not replace prediction, evidence, action, owner, and row-level parity.
14. **Locked aggregate checks are not row-review permission.** Any discrepancy
    on test60 or test450 blocks release and must be investigated using permitted
    development or synthetic cases, not by opening the locked row.

## Stop, rollback, and version rules

- Stop a method migration at the first unexplained difference in prediction,
  evidence, component action, attribution, failure state, or score.
- Keep the old path callable until the discrepancy is explained. Revert the
  caller to the old path rather than weakening the comparator.
- If the difference is a refactor defect, repair the new path and rerun the
  method-level gates.
- If the old path contradicts an accepted decision, repair that contradiction
  in a separate versioned change with its own evidence, then re-freeze the
  baseline.
- If a desired design intentionally changes clinical meaning, stop work under
  decision 0047 and create a new decision, pipeline version, predeclared replay,
  and claim boundary.
- Do not add a differing field to the normalization allowlist unless it is
  demonstrably non-semantic and recorded in the final parity report.

## Planning decisions

| Question | Decision or assumption | Evidence | Consequence | Owner |
| --- | --- | --- | --- | --- |
| Which ExECT LLM-only method is selected? | The decision-0046 Sol one-call raw lane, not GEPA. | Decision 0046 and the retained six-model stage panel. | Correct the manifest and teaching case in Phase 0; retain GEPA as historical. | Decision 0046 and the ExECT LLM-only manifest. |
| What is the orchestration unit? | One record or letter; splits, checkpoints, and reports stay outside. | The current duplication occurs inside per-row loops and assembly functions. | The core stays testable with synthetic and saved outputs and cannot bypass split policy. | Decision 0047 and task-local contracts. |
| How are ExECT raw and hybrid methods kept comparable? | One typed structured producer result feeds two named method projections. | Decisions 0041 and 0046 require one call and matched Sol peers. | Add `run_primary_pair` and a one-call-count test. | ExECT structured one-call orchestrator. |
| Is the retained six-cell replay sufficient? | No. It protects historical reproducibility; a second current selected-method parity suite is required. | The retained ExECT cells include GEPA and historical `v08`. | Completion requires both suites. | Final 0047 parity artifact. |
| What happens to operational drift from decision 0045? | Correct and version it separately before refactor parity if output changes. | Current local and operational constants enable older policy behavior. | A policy repair cannot be passed off as structural equivalence. | Decision 0045 plus the operational runbook/version owner. |
| What proves effective implementation? | Behavioral parity, one active owner per stage order, complete delegation, reproducible evidence, and an accurate two-link reading path. | Review findings 1-6 and the current stage-manifest layer. | File consolidation or aggregate score equality alone cannot close the decision. | Decision 0047, architecture manifests, final parity report, and `PROJECT_STATUS.md`. |

Operational-drift disposition (2026-08-01): `default` / `default` is the sole
active ExECT research and operational policy. The earlier operational
`diagnosis_resolution_candidate=True` behavior is an archived historical
variant. Its permitted-development delta is disclosed separately and is not an
invariant of this structural refactor.

## Verification gate

Before the refactor is considered complete, no-call replay must demonstrate
identical final predictions, evidence, component actions, attribution, and
scores for both the current selected-method baseline and the six retained
historical reference cells. Focused tests must cover each canonical stage and
each delegated entry point; the repository's full pytest, Ruff, and mypy checks
must pass.

Model calls and locked-row inspection are not authorized by this decision.

## Parity evidence

- Machine artifact:
  [`experiments/canonical_orchestrator_parity_0047.json`](../../experiments/canonical_orchestrator_parity_0047.json)
- Checker: `scripts/check_canonical_orchestrator_parity.py`

## Consequences

- The canonical orchestrators become the primary code-reading path for the
  selected methods.
- Operational wrappers own endpoint, runtime, provider-transport retry, resume,
  and privacy concerns but not independent clinical processing order.
  Prediction-bearing format/schema retry remains a canonical stage.
- Saved-output replay enters and exits through explicit stage boundaries,
  making component attribution and no-call verification easier to audit.
- Temporary migration complexity and compatibility shims are expected.
- Any observed prediction, evidence, attribution, or score difference is a
  release-blocking discrepancy until explained and either repaired or
  versioned deliberately.
- This decision authorizes implementation of the refactor; it does not
  promote any new clinical policy or establish clinical validity.

## Owners

- Generated architecture layer:
  [architecture README](../architecture/README.md)
- Current evidence and verification state:
  [PROJECT_STATUS.md](../../PROJECT_STATUS.md)
- Active sequencing:
  [ACTIVE_ROADMAP.md](../plans/ACTIVE_ROADMAP.md)
