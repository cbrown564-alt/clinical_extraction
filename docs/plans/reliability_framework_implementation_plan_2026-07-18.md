# Shared reliability framework implementation plan

Date: 2026-07-18  
Status: implemented and verified on 2026-07-18  
Work mode: promote a paper-facing evidence framework  
Roadmap owner: [ACTIVE_ROADMAP.md](ACTIVE_ROADMAP.md)

## Objective

Replace the attempted one-to-one replication of the Gan reliability scorecard
with one shared reliability framework for Gan 2026 and ExECTv2.

The framework will use the same eight clinical and operational questions for
both tasks while allowing task-appropriate measures, denominators, score
stages, and evidence limits. It will produce task scorecards and a cross-task
synthesis without pooling incompatible metrics or assigning a composite
reliability score.

The implementation is complete when:

1. all eight criteria have stable definitions and canonical owners;
2. both tasks have one explicit result state for every criterion: measured,
   not measured, not applicable, or not measurable from the current data;
3. every measured result records its model scope, split, denominator, scorer,
   output stage, repair policy, row-inspection rule, evidence state, and claim
   boundary;
4. the machine-readable scorecard reproduces the human report;
5. the manuscript and claim canon use the framework without strengthening any
   unsupported claim; and
6. repository-wide tests, Ruff, mypy, retained-evidence validation, and paper
   source synchronization pass.

## Fixed decisions

### The eight criteria

The following set is final for this implementation. Changing the set or
merging/splitting a criterion requires an amendment to the planned decision
record, not an incidental report edit.

| # | Criterion | Shared question |
| --- | --- | --- |
| 1 | Clinical correctness and generalization | Does the final system recover the intended clinical result, and what changes outside development? |
| 2 | Clinical selection and unsupported inference | Does the system select a warranted current fact rather than an unsupported, historical, planned, or ambiguous one? |
| 3 | Evidence support and faithfulness | Is cited text present, and does it semantically support the selected conclusion? |
| 4 | Uncertainty and selective action | Do uncertainty signals identify failures, and can they support abstention or review at acceptable burden? |
| 5 | Robustness and stability | Does the decision persist across relevant data, sampling, wording, prompt, parser, or runtime changes? |
| 6 | Component attribution and correction safety | Which component changes the answer, and does deterministic correction help without damaging correct model output? |
| 7 | Coverage and clinical-slice behavior | Which clinical families and hard cases are covered, missing, or materially weaker? |
| 8 | Operational reliability | Does the named runtime complete predictably, with failures, repairs, retries, latency, and usage reported at their measured scope? |

### Assurance gates

The following are required metadata and governance gates, not scored criteria:

- dataset, split manifest, row policy, and inspection permission;
- exact model, route, runtime, temperature, token limit, and cache/replay mode;
- prompt/program, scorer, score stage, and repair policy;
- source identifiers, artifact hashes, and reproducibility command;
- split barriers, locked-row controls, canaries, and failure handling;
- independent clinical-review status; and
- claim boundary.

A criterion cannot be called complete when one of its required gates is
missing. Gates are never averaged into a numerical reliability result.

### Evidence state and comparability

Evidence state and inspection scope must remain separate.

Allowed evidence states:

- `not_measured`;
- `diagnostic`;
- `development_answer`;
- `aggregate_holdout_evidence`; and
- `externally_validated`.

Allowed row scopes:

- `synthetic_fixture`;
- `development_rows_permitted`;
- `aggregate_only_rows_sealed`; and
- `independent_review_rows`.

Allowed cross-task comparability states:

- `direct`: the measurement object, transform, and unit are the same;
- `construct_only`: both measures answer the same criterion but their values
  must not be compared numerically; and
- `not_comparable`: the measures answer different questions or one task lacks
  a valid denominator.

These labels describe evidence; they are not a five-point quality scale.

### No composite score

The framework will not calculate an overall reliability number, average
criterion coverage, or rank models by a weighted reliability index. A missing
or diagnostic criterion must remain visible rather than being diluted by
stronger unrelated results.

## Criterion specification

### 1. Clinical correctness and generalization

**Gan implementation**

- Purist accuracy is primary; Pragmatic accuracy is secondary.
- Report validation and locked test separately.
- Report the matched six-model `test450` panel without row-level test analysis.

**ExECT implementation**

- `clinical_headline` F1 overall and by the four fixed families.
- Report `dev140` and aggregate-only `test60` separately.
- Keep published phrase, CUI, and full-attribute views separate from the
  internal clinical score.

**Model scope:** all six conditions for the fixed comparison.  
**Comparability:** `construct_only`.  
**Required completion:** score, denominator, split, model, stage, and
development-to-holdout change where available.

### 2. Clinical selection and unsupported inference

**Gan implementation**

- Unknown-gold active-rate over-read.
- Current-versus-historical event selection and faithful-but-wrong counts.

**ExECT implementation**

- Do not reuse empty-gold rows as unknown.
- Retain the completed six-model SF study as a diagnostic result: the
  predeclared unknown-only denominator is zero.
- A future unsupported-selection rate requires an exhaustively reviewed
  development substrate that separates unsupported predictions from annotation
  omission, multiplicity, and accepted representation differences.

**Model scope:** all compared models only when a valid reviewed substrate
exists.  
**Comparability:** currently `not_comparable`.  
**Required completion:** preserve the zero-denominator result and state the
unblock condition; do not commission model calls to repair an annotation
denominator.

### 3. Evidence support and faithfulness

Both tasks must report two separate levels:

1. **Textual grounding:** exact or safely repaired source presence.
2. **Semantic support:** the evidence is sufficient and decisive for the
   selected clinical conclusion.

Exact-evidence rate must never be presented as semantic or clinical
faithfulness.

**Gan implementation:** retain the existing grounding packages and label the
measurement stage for every method.  
**ExECT implementation:** report six-model final exact evidence and build an
independent-review sampling substrate for semantic support.  
**Model scope:** all six for textual grounding; stratified representative
sampling for semantic review unless a six-model comparative claim is required.
**Comparability:** `construct_only` until both tasks measure semantic support at
the same decision stage.

### 4. Uncertainty and selective action

This criterion combines calibration and abstention because the operational
question is whether uncertainty supports a safe action.

Report, when defined:

- confidence coverage and missingness;
- Brier score and ECE for probabilistic signals;
- failure AUROC;
- risk-coverage behavior; and
- catch rate and review burden for predeclared review rules.

**Gan implementation:** retain the external-confidence calibration,
risk-coverage, and self-confidence degeneracy results.  
**ExECT implementation:** retain the internal scoring-rule result and the
historical three-model negative routing result. Do not describe either as a
final six-model or deployment-calibration result.  
**Model scope:** one selected operational system is sufficient for a review
policy; all six are required only for a comparative uncertainty claim.  
**Comparability:** `construct_only`.

### 5. Robustness and stability

Keep the following subdimensions separate:

- development-to-holdout change;
- repeated-sampling consistency;
- prompt or formatting perturbation;
- clinically equivalent wording;
- parser and schema variation; and
- runtime or provider variation.

**Gan implementation:** retain the prompt-version robustness index and the
one-model repeated-temperature study with their original scope.  
**ExECT implementation:** report six-model dev-to-test aggregate changes and
existing parser/runtime behavior. Do not call these perturbation robustness or
self-consistency.  
**Model scope:** all six only if the paper makes a comparative robustness
claim; otherwise a predeclared canonical subject is sufficient.  
**Comparability:** `construct_only`.

No new repeated-temperature or perturbation calls are part of the required
implementation. They require a separate protocol and an explicit manuscript
claim that would change if the result were positive or negative.

### 6. Component attribution and correction safety

Required outputs:

- raw, evidence-valid, normalized/projected, and final score stages where
  available;
- wrong-to-correct, correct-to-wrong, changed-still-wrong, and unchanged
  counts;
- first prediction-changing and first unrecoverable-failure owner;
- rule-added and rule-removed facts;
- exact evidence on changed rows; and
- deterministic rule category when the change affects clinical meaning.

**Gan implementation:** preserve raw selection, format repair,
selected-evidence repair, clinical repair, final label, and scoring as separate
stages.  
**ExECT implementation:** use the decision-0040 family boundary and existing
finding provenance; include the six-model SF state result and known
deterministic regressions.  
**Model scope:** every condition used in an attribution claim.  
**Comparability:** `construct_only`; transition counts remain task-specific.

### 7. Coverage and clinical-slice behavior

Do not label entity-family or seizure-band variation as demographic fairness.

**Gan implementation:** seizure bands, seizure-free duration, unknown, cluster
or diary language, and named hard families.  
**ExECT implementation:** four main entity families plus temporal selection,
seizure state, medication regimen, investigation completion, annotation-
sensitive cases, and parse/schema status.  
**Model scope:** all six when reporting model differences; otherwise report the
selected system and state the scope.  
**Comparability:** `construct_only`.

Demographic fairness is `not_measured` unless suitable attributes, sample
sizes, and a clinically meaningful fairness question are established.

### 8. Operational reliability

Report only directly observed or reproducibly reconstructed values:

- attempted and completed calls;
- call, parse, schema, label, and render failures;
- retries, repairs, fallbacks, and missing outputs;
- route, runtime, temperature, context/output limit, cache state, and local
  hardware where applicable; and
- latency, tokens, and cost only under a matched measurement protocol.

**Gan implementation:** retain the existing repair and failure counts and the
bounded offline cost estimate; keep matched latency and retry comparison
unavailable.  
**ExECT implementation:** report six-model call and parse/schema behavior,
including Gemma's recorded events and hosted/local differences.  
**Model scope:** all six.  
**Comparability:** `construct_only`; local and hosted conditions cannot support
a matched efficiency ranking.

## Machine-readable contract

The scorecard artifact will contain one record per task, criterion, model
scope, split, and measurement. The minimum record is:

```json
{
  "task": "gan2026 | exectv2",
  "criterion_id": "clinical_correctness_generalization",
  "measurement_id": "task-owned stable name",
  "model_scope": ["exact runtime identifiers"],
  "dataset": "named dataset",
  "split": "named split",
  "split_manifest": "repository path",
  "row_scope": "development_rows_permitted",
  "denominator": 0,
  "score_stage": "raw | evidence_valid | projected | final",
  "scorer": "named scorer or transform",
  "repair_policy": "named policy",
  "value": null,
  "evidence_state": "diagnostic",
  "comparability": "construct_only",
  "source_artifacts": ["repository paths"],
  "claim_boundary": "bounded statement",
  "not_measured_reason": null
}
```

Rules:

- `value` may be null only when `evidence_state` is `not_measured` or the
  denominator is invalid or zero.
- A zero denominator must be recorded as zero, not omitted.
- Pooled values require a declared pooling unit and cannot duplicate the same
  letter across models without saying so.
- A `direct` cross-task comparison requires an identical measurement ID,
  transform, stage, and unit.
- No artifact may contain a composite reliability field.

## Deliverables and owners

| Deliverable | Planned owner | Purpose |
| --- | --- | --- |
| Shared framework design | `docs/design/reliability_evaluation_framework.md` | Canonical criterion definitions, evidence states, assurance gates, and comparability rules |
| Durable decision | `docs/decisions/0044-shared-reliability-criteria-use-task-specific-measures.md` | Why identical Gan metrics and a composite score were rejected |
| Machine scorecard | `experiments/shared_reliability_scorecard_20260718.json` | Reproducible task, criterion, model, split, and measurement records |
| Human scorecard | `docs/research/shared_reliability_scorecard_2026-07-18.md` | Main substantive reliability result |
| Builder | `scripts/build_shared_reliability_scorecard.py` | Validate sources and generate the scorecard and report |
| Focused tests | `tests/test_shared_reliability_scorecard.py` | Pin schema, source values, split rules, comparability, and report synchronization |
| Paper claim owner | `docs/canon/10_paper_provenance.md` | Permitted claim strength |
| Cross-task summary | `docs/canon/09_cross_task_reliability.md` | Short maintained conclusion, not detailed tables |
| Evidence selection | `docs/experiments/retained_evidence_manifest.json` and `.md` | Exact selected files, hashes, and replay requirements |
| Current status | `PROJECT_STATUS.md` | Outcome, strongest evidence, remaining boundary, and next action only |

This plan owns the work breakdown only. It does not replace the active roadmap,
claim canon, status, or retained evidence index.

## Implementation sequence

### Phase 0 — Record the decision

1. Create decision 0044.
2. Create the canonical framework design document from the fixed definitions in
   this plan.
3. Add one link from `ACTIVE_ROADMAP.md`; do not duplicate the phase details
   there.

**Gate:** the design document names all eight criteria, assurance gates,
evidence states, row scopes, comparability states, and the no-composite rule.

### Phase 1 — Inventory and map retained evidence

Build a source inventory before writing a scorecard builder. For each existing
result, record:

- criterion and task;
- exact source artifact;
- model and runtime scope;
- split, denominator, row policy, and inspection permission;
- scorer, stage, prompt/program, and repair policy;
- current evidence state and claim boundary; and
- whether the measurement is direct, construct-only, or not comparable across
  tasks.

Start with the retained evidence manifest, then resolve each selected report or
machine artifact. Do not infer a missing value from narrative prose when a
machine source is required.

**Gate:** all 16 task-by-criterion cells have either mapped evidence or an
explicit reason and unblock condition.

### Phase 2 — Prove two representative slices with TDD

Implement the smallest builder that supports two criteria:

1. **Clinical correctness and generalization** to prove a straightforward
   six-model, two-task synthesis.
2. **Component attribution and correction safety** to prove that different
   task measurements can share a criterion without being pooled.

Write failing tests first for:

- required metadata;
- model roster and split identity;
- zero-denominator preservation;
- no locked-row material;
- no cross-task numeric pooling when comparability is `construct_only`;
- no composite score;
- report values matching JSON; and
- correct source hashes or retained paths.

Keep the representative implementation local to the builder until these two
slices demonstrate a reusable pattern. Extract shared helpers only after the
second criterion passes.

**Gate:** the two criteria regenerate identically from retained sources and all
focused tests pass.

### Phase 3 — Implement the remaining no-call criteria

Add, in order:

1. evidence support and faithfulness;
2. operational reliability;
3. coverage and clinical-slice behavior;
4. uncertainty and selective action;
5. robustness and stability; and
6. clinical selection and unsupported inference.

The order prioritizes well-instrumented retained evidence before incomplete or
diagnostic criteria. Every addition must include a focused regression test and
must preserve its original measurement stage.

**Gate:** all eight criteria render for both tasks, with missing or invalid
denominators visible rather than backfilled.

### Phase 4 — Decide evidence gaps without broad reruns

Classify each remaining gap as one of:

- closed negative or diagnostic result;
- documentation/instrumentation gap resolvable by no-call replay;
- independent clinical-review dependency;
- optional new experiment tied to a named paper claim; or
- outside the project boundary.

Required decisions:

- Keep ExECT unknown-versus-rate as diagnostic until an independently governed
  reviewed substrate exists.
- Prepare, but do not self-certify, a stratified ExECT semantic-support review
  substrate.
- Keep the historical ExECT uncertainty result bounded unless a six-model
  review-routing claim is explicitly adopted.
- Do not run six-model temperature or perturbation studies merely to fill the
  framework.
- Do not recreate unmatched cost or latency telemetry.

Any new model call requires its own dated protocol under the clinical research
loop. No locked holdout call or row inspection is authorized by this plan.

**Gate:** every gap has a decision, owner, unblock condition, and claim effect.

### Phase 5 — Generate the final scorecards and reconcile claims

Generate:

- one Gan task table;
- one ExECT task table;
- one cross-task criterion matrix;
- one evidence-state and comparability matrix; and
- a concise list of unresolved dependencies.

Then update, in order:

1. the detailed reliability report;
2. the retained evidence manifest;
3. `docs/canon/09_cross_task_reliability.md`;
4. `docs/canon/10_paper_provenance.md`;
5. the Markdown and IEEE paper sources;
6. `PROJECT_STATUS.md`; and
7. `ACTIVE_ROADMAP.md` with completion only.

Do not place detailed tables or chronology in the status file.

**Gate:** no manuscript statement exceeds the evidence state or claim boundary
recorded in the machine scorecard and claim canon.

### Phase 6 — Verify and hand off

Run through the repository `.venv` on Windows:

```powershell
.venv\Scripts\python.exe scripts/build_shared_reliability_scorecard.py --check
.venv\Scripts\python.exe scripts/check_retained_evidence_manifest.py
.venv\Scripts\python.exe scripts/verify_reference_evidence.py
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m mypy src
```

Rebuild the IEEE PDF, render every page, and inspect tables, wrapping,
references, page count, and claim wording. Run the paper-source synchronization
tests after the final render.

**Gate:** automated checks pass, the PDF has no clipping or unreadable tables,
the retained hashes validate, and the scorecard can be regenerated without
model calls or locked-row inspection.

## Required tests

At minimum, tests must prove:

- exactly eight criterion IDs exist;
- both tasks have one state for every criterion;
- every measured result has the required assurance metadata;
- an invalid or zero denominator cannot produce a rate;
- empty-gold ExECT rows cannot be relabelled as unknown by the builder;
- textual grounding and semantic support use different measurement IDs;
- calibration and routing results retain their original model scope;
- the same letter repeated across models cannot be presented as independent
  pooled rows;
- `construct_only` and `not_comparable` cells cannot generate a cross-task
  numerical delta;
- no composite reliability value is present;
- locked artifacts contribute aggregates only;
- report tables reproduce the JSON values; and
- claim-language snapshots retain the published-score, clinical-validation,
  runtime-route, and cross-task-transfer limits.

## Decision ledger from the document grill

| Question | Decision | Evidence | Consequence | Owner |
| --- | --- | --- | --- | --- |
| Must both tasks use identical metrics? | No; share constructs and use task-specific measures | Gan is exhaustive single-label; ExECT is multi-mention and has no unknown-only denominator | Cross-task values are usually `construct_only` | Decision 0044 and framework design |
| Should the Gan ten-row scorecard remain the template? | No; replace it with eight shared criteria | Several Gan rows combine task-specific transforms and one-model studies | Historical Gan scorecard remains evidence, not the shared schema | Framework design |
| Is fairness a core shared criterion? | No; use coverage and clinical-slice behavior | Neither selected dataset supports a defensible demographic fairness comparison | Do not relabel entity-family or band variation as fairness | Framework design and report |
| Are calibration and abstention separate criteria? | No; combine them as uncertainty and selective action | Both answer whether uncertainty supports a safe operational action | Preserve individual metrics as submeasures | Framework design |
| Are consistency and robustness separate criteria? | No; combine them while keeping subdimensions separate | Existing evidence has different sampling, prompt, split, and runtime scopes | No broad robustness claim from one subdimension | Framework design |
| Is safety/compliance a scored criterion? | No; safety, data governance, and reproducibility are assurance gates | Split protection and hash integrity are invariants, not model-quality scores | A failed gate blocks a claim rather than lowering an average | Framework design and tests |
| Should the framework produce an overall score? | Never | Averaging would hide missing denominators and incompatible constructs | Report criterion results and evidence states only | Decision 0044 |
| Can ExECT empty-gold rows substitute for Gan unknown? | Never without independent adjudication | Annotation synthesis documents omission and representation effects | Preserve the zero-denominator diagnostic result | Claim canon |
| Are broad new six-model calls required? | No | Current claims can be represented from retained evidence; symmetry is not a research question | New calls require a separate claim-changing protocol | Active roadmap |
| What is the main external dependency? | Independent clinical review for semantic support and clinical-validity language | Internal and LLM-assisted review is not external validation | Prepare a review substrate but do not claim validation | Project status and claim canon |

## Risks and controls

| Risk | Control |
| --- | --- |
| New framework silently changes an existing scorer | Treat scorer changes as separate studies; the builder reads retained results and does not rescore by default |
| Cross-task table implies direct comparability | Require a comparability field and suppress numerical deltas unless it is `direct` |
| Missing evidence is hidden by prose | Require one machine record for every task-by-criterion cell |
| Aggregate holdout results are treated as row evidence | Encode row scope and test that sealed splits cannot emit row fields |
| Exact evidence is called semantic faithfulness | Separate measurement IDs and report columns |
| Six-model pooled counts exaggerate sample size | Record unique letters and model-letter rows separately |
| Framework grows into a generic reporting platform | Prove two slices first; implement only the retained two-task report |
| Independent review is simulated internally | Use `not_measured` or `diagnostic` until external reviewer provenance exists |
| Paper and scorecard drift | Generate tables from the machine artifact and keep source-sync tests |

## Work explicitly excluded

- changing prompts, pipelines, scorers, gold labels, or deterministic clinical
  rules;
- inspecting ExECT `test60` or Gan `test450` rows;
- rerunning locked panels for symmetry;
- creating a demographic fairness claim without suitable data;
- inventing matched cost, latency, token, energy, or retry measurements;
- adopting a deployment review policy from the historical confidence study;
- creating a generic dashboard, frontend, registry platform, or observability
  service; and
- claiming independent clinical validation without independent reviewers.

## Final handoff statement

At completion, the project should be able to say:

> Gan 2026 and ExECTv2 are assessed with the same eight reliability questions.
> Each task uses measures appropriate to its annotation and output structure,
> and every result states its model, split, stage, evidence strength, and claim
> limit. Incompatible values are not pooled, missing denominators remain
> visible, and component corrections are reported with their benefits and
> regressions.

It must not say that the tasks share one reliability metric, that all criteria
are equally evidenced, or that the framework establishes clinical validity.
