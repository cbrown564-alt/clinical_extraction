# Gan 2026 Research Drift Audit

Date: 2026-06-01

## Scope

Repo-wide research-drift audit across the project thesis, architecture/data
contracts, Gan 2026 implementation, tests, status document, and recent
validation artifacts. Locked test row-level failures were not inspected.

## Verdict

Mostly aligned with important watches.

The repo still supports the intended paper contribution: a modular, auditable
hybrid clinical extraction system where deterministic rules, LLM reasoning,
evidence validity, split discipline, and claim language are visible. The main
risk is not a single invalid result. The risk is that prompt-level Gan-specific
fixes and post-LLM repair modules grow faster than their taxonomy, ablation, and
status language.

## Research Contract

The intended contract from `docs/research/contribution_thesis.md`,
`docs/design/architecture.md`, `docs/design/data_contract.md`,
`docs/design/gan2026_normalization_semantics.md`, and
`docs/design/gan2026_split_protocol.md` is:

- Gan 2026 is the first controlled task, not the package identity.
- `core/` contains task-neutral primitives; Gan-specific schemas, label policy,
  scoring, repair, prompts, and error analysis remain under `tasks/`.
- Deterministic rules are controlled variables, not hidden implementation
  detail.
- `unknown`, `no seizure frequency reference`, unresolved cluster states, and
  scorer sentinel values remain semantically distinct before Gan scoring.
- Validation is the development surface; locked test is final holdout only.
- LLM-backed reports record model, prompt/program, split, cache/reuse status,
  repair policy, evidence validity, and caveats.
- Aggregate F1 is insufficient without attribution, evidence, and ablation
  context.

## Findings

### P1 Watch: Prompt Policy Is Becoming An Unmeasured Rule Surface

`src/clinical_extraction/tasks/seizure_frequency/gan2026/section_claim_table.py`
now encodes many section-claim-table v4 fixes directly in prompt prose:
bimonthly interpretation, cluster-cadence preservation, additive counted-window
arithmetic, rescue-medication boundaries, compact `q2-3wk` notation,
upper-bound preservation, and no-reference/seizure-free/unknown distinctions.

This is acceptable for a diagnostic candidate because the v3 250-row family
review recommended a narrow v4 attempt. The drift risk is that prompt prose
starts functioning like a deterministic rule stack without being categorized,
ablated, or described as a controlled variable.

Narrow corrective action: add a prompt-change taxonomy for v4 and future
section-claim-table candidates, then report which prompt policy families changed
between versions.

Fix belongs in: experiment protocol and docs/status; later tests or prompt
snapshot checks if the prompt continues to be a controlled artifact.

### P1 Watch: Semantic Repair Is Well Labeled In Reports But Dangerous By Default

`StructuredRepairConfig` in `llm_structured.py` defaults to multiple post-LLM
semantic repair families. The combined 650-row repair ladder correctly separates
raw model selection, strict format repair, frozen clean scorer-facing policy,
and hybrid semantic repair modules. It also states that the jump from clean
policy to full stack is deterministic semantic-repair contribution.

This is currently aligned because the artifact language is conservative. The
watch is that future summaries must not describe repair-heavy results as clean
LLM-first results.

Narrow corrective action: keep default repair-heavy runs labeled as hybrid; make
clean attribution configs the default for any "LLM-first" claim or comparison.

Fix belongs in: experiment protocol, CLI defaults or named configs, and claim
language.

### P2 Drift: Seizure-Specific Schema Lives In `core/`

`src/clinical_extraction/core/schemas.py` defines `SeizureEvent`, while the
architecture contract says `core/` should contain task-neutral primitives only.
Gan and seizure-frequency schemas belong under
`tasks/seizure_frequency/gan2026/` until cross-task reuse is proven.

This is small and currently low blast radius, but it violates the package
boundary that protects the long-term modular clinical extraction thesis.

Narrow corrective action: move or remove `core.schemas.SeizureEvent` before more
code depends on it.

Fix belongs in: code and tests.

### P2 Watch: CLI Records But Does Not Enforce The Validation Ladder

`llm_pipeline_cli.py` records `--escalation-reason`, split, limit, cache, and
reuse metadata, but it allows arbitrary validation limits. The split protocol
requires the 25 -> 50 -> 250 ladder and written reasons for rare full validation
runs.

Current reports are disciplined, so this is not yet drift. A small CLI guard or
warning would make the protocol harder to bypass accidentally.

Narrow corrective action: warn or fail when validation runs exceed the expected
ladder without `--escalation-reason`; continue disallowing test in LLM CLIs.

Fix belongs in: code and tests.

### P2 Watch: Status Should Name The Current V4 Schema Blocker

`PROJECT_STATUS.md` says the immediate next step is to implement v4 and run the
25-row gate. A current v4 artifact exists, but it is only a 10-row live smoke
attempt and all 10 rows failed schema parsing with "Extra inputs are not
permitted." That makes v4 implementation incomplete from the perspective of the
validation gate.

Narrow corrective action: update status to say v4 has a schema-output blocker
before the 25-row gate.

Fix belongs in: docs/status and then code/tests for schema repair or prompt
shape.

## Aligned Signals

- Split discipline and claim language are conservative in status and experiment
  artifacts.
- The deterministic V1 locked-test result is framed as a final holdout result,
  not tuning fuel.
- Unknown/no-reference and scorer sentinel semantics are preserved in
  normalization code and tests.
- Rule metadata provides group and portability labels, plus ablation controls.
- Section-claim-table reports preserve raw, strict-format, and clean
  scorer-facing score layers separately.
- Repair-attribution artifacts explicitly distinguish clean attribution layers
  from hybrid deterministic post-processing modules.

## Metric Risk Versus Research Risk

The largest metric opportunity remains deterministic semantic repair. The
largest research risk is exactly the same surface: repair and prompt policy can
raise Purist F1 while weakening attribution, generalisation, and transparency if
they are not named and ablated.

This means metric improvement is acceptable only when accompanied by component
labels, repair-rate reporting, evidence validity, split metadata, and
appropriately hybrid claim language.

## Restoration Plan

1. Record the v4 schema-output blocker in `PROJECT_STATUS.md`; do not call v4
   ready for the 25-row gate until structured claim-table records parse.
2. Add a section-claim-table prompt taxonomy for v4 policy families and require
   future prompt changes to name the family they target.
3. Move or remove `core.schemas.SeizureEvent` so the core package remains
   task-neutral.
4. Add a validation-ladder guard or warning to `llm_pipeline_cli.py`, with tests.
5. Keep repair-heavy structured runs labeled as hybrid and reserve "LLM-first"
   language for raw/strict/clean attribution layers.

## Residual Risk

This audit judged artifacts, source code, and tests available in the workspace.
It did not inspect locked test row-level failures, did not rerun expensive LLM
experiments, and did not adjudicate whether the latest v4 raw outputs should be
schema-repaired or reprompted. That decision should be made on validation only,
using the existing 25/50 ladder.
