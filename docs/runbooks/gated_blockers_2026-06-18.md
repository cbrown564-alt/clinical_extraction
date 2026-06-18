# Gated Blockers Resume Note

Date: 2026-06-18

This note makes the current blocked states actionable without authorizing any
blocked evaluation. It does not permit Gan `test450` row-level inspection,
post-test tuning, or new ExECTv2 full-200 audits.

## Required Authorization Artifacts

### Gan Holdout-Facing Work

Blocked work:

- Gan holdout-facing reruns;
- locked-test row-level error analysis;
- any prompt, rule, threshold, model, scorer, or repair change based on
  locked-test output.

To unblock an aggregate holdout-facing run, create a dated frozen protocol that
names:

- explicit user authorization for the specific run;
- split manifest (`gan2026_split_v1`) and distribution (`test450`);
- candidate code, prompt/schema versions, model/version, scorer, gates, repair
  policy, output paths, and artifact hashes where practical;
- allowed readouts: aggregate Purist/Pragmatic plus any predeclared aggregate
  slice summaries;
- inspection policy: no row-level locked-test failures during development; any
  row-level review must be post-hoc final-evaluation analysis and cannot drive
  tuning;
- stop rule and claim language.

Authority docs:

- `docs/design/gan2026_split_protocol.md`
- `docs/design/gan2026_saturated_validation_protocol.md`
- current frozen-test examples under `docs/experiments/gan2026/frozen_test/`

### ExECTv2 Full-200 Audits

Blocked work:

- new ExECTv2 full-200/test audits;
- full-200 row-level error analysis before a frozen audit;
- post-test schema/prompt/projection tuning.

To unblock, the next cycle needs all of:

- benchmark-beating GPT-first dev evidence on a predeclared headline, with
  ownership-clean attribution and exact evidence/schema readouts;
- explicit user authorization for the specific full-200/test audit;
- a predeclared aggregate readout that names the headline, companion tables,
  slice summaries, stop rule, and claim language before execution;
- a separate frozen full-200 protocol that pins architecture, prompt/schema
  versions, projection adapters, scorer policy, model/version, artifact paths,
  allowed aggregate-only tables, failure handling, and no row-level tuning.

Existing predeclarations are not enough by themselves:

- `docs/experiments/exectv2/predeclarations/exectv2_phase_e_full200_audit_predeclaration_2026-06-17.md`
  explicitly records that the gate was not met and the audit was not run.
- `docs/experiments/exectv2/predeclarations/exectv2_family_routed_llm_first_comparison_predeclaration_2026-06-18.md`
  authorizes only the dev ladder and says any full-200 audit needs a separate
  protocol.

### EpilepsyCause

Current decision: keep `EpilepsyCause` diagnostic.

Authority doc:

- `docs/decisions/0029-epilepsy-cause-remains-a-low-frequency-diagnostic-family.md`

Do not promote EpilepsyCause to a targeted route unless a predeclared dev-only
boundary-control study first shows it is a material architecture bottleneck
after concept projection. The ADR already identifies the likely issue as
cause-boundary/projection control and over-emission, not a missing standalone
extractor. A future study would need:

- dev-only rows and a dev-only boundary taxonomy;
- no Gan holdout/test-row artifacts;
- no ExECTv2 full-200 row-level inspection;
- ownership-clean comparison against existing diagnostic-family treatment,
  focused per-entity probes, and deterministic projection layers;
- a promotion rule showing concept-identity precision/recall gain without
  increased causal-context over-emission.

No new boundary-control protocol is needed now unless that bottleneck evidence
is first assembled from allowed dev artifacts.

## Next Permitted Action

The next permitted action is dev-only ExECTv2 analysis: review the dev140 SF
route residuals and CUI/projection gaps named in `PROJECT_STATUS.md`, preserving
the current ownership label `llm_first_with_hybrid_sf_route`. This may use
predeclared dev artifacts and dev row/error ledgers only. It does not authorize
Gan `test450`, ExECTv2 full-200/test, holdout row-level review, repeated
holdout calls, or post-hoc tuning.

## Current Verification Reproduction

Use the repo-managed environment:

```powershell
uv run --extra dev python -m pytest -q
```

Observed on 2026-06-18 in the guardrail worktree:

```text
1700 passed, 4 failed in 40.56s
```

Current unrelated failures:

- `tests/test_exectv2_deterministic_all9.py::test_deterministic_all9_scores_tiny_active_entity_gold`
  now scores per-item `0.9655172413793104` (`tp=14`, `fp=1`, `fn=0`) instead of
  the expected `1.0`.
- `tests/test_exectv2_projection_gap_ledger.py::test_build_ledger_on_dev_split_is_consistent_and_has_rx_families`
  expects Diagnosis regime `recall_bound`, but the ledger reports
  `representation_bound`; this is the projection-gap total/regime drift.
- `tests/test_gan2026_validation_test_gap_protocol.py::test_gap_protocol_blocks_locked_test_row_level_tuning`
  has `PROTOCOL_PATH = ROOT / ""`, so it reads the repo directory and fails with
  `PermissionError`.
- `tests/test_gan2026_validation_test_gap_protocol.py::test_gap_artifact_inventory_declares_provenance_and_safe_inspection`
  compares the inventory protocol path to `.` because of the same
  `PROTOCOL_PATH` issue.

The plain `python -m pytest -q` command is not a valid reproduction in a fresh
worktree unless the package is already installed; it fails during collection
with `ModuleNotFoundError`.
