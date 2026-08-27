# Retention keep-set and leftovers (2026-08-16)

Ledger: [REGENERATION.md](../../REGENERATION.md).
Slot inventory: [candidate table](retention_candidate_table_2026-08-16.md).
Taxonomy: [hierarchical matrix](retention_slice_hierarchical_retention_matrix_2026-08-16.md).
Decision: [0048](../../decisions/0048-comprehension-and-handoff-refactor.md).

This note records what the 2026-08-16 living-stack freeze and the
docs/scripts confident cut kept, why, and what is still uncertain.
It is not a deletion list and not a new status board. Git history is
the restore for everything removed. No model calls. No locked-row
inspection. Hybrid fills are unchanged.

Freeze id: `retained_comparison_architecture_20260816`.

## What we kept, and why

### Living comparison stack

The six reference cells are the current selected comparison, not the
11 Aug museum. Keep these because Decision 0046 / 0050 cite them and
`scripts/verify_reference_evidence.py` replays them with no model
calls.

| Cell | Why it stays |
| --- | --- |
| ExECT rules — E5 **0.9042 / 0.7937** | Decision 0046 four-family floor; living remasure |
| ExECT LLM-only — Sol raw_lane **0.8097 / 0.7771** | Matched LLM-only peer for the same table |
| ExECT hybrid — current-stack Sol **0.9119 / 0.8302** | Decision 0050 selected hybrid |
| Gan rules — 10 Aug portable cell **682/750** | Selected deterministic Gan floor (`gan_saved_comparisons`) |
| Gan LLM-only — current-stack **0.7444** | Matched LLM-only peer |
| Gan hybrid — current-stack Sol **381/450** | Decision 0050 selected hybrid |

Owners: [`SOURCES.json`](../../../experiments/current_stack/SOURCES.json),
[`latest/fills.json`](../../../experiments/current_stack/latest/fills.json),
[retained evidence](../../experiments/retained_evidence_manifest.md).
Replay type `current_stack_primary` owns the living fills / sources /
E5 inputs. Historical sidecar keys (`gpt41mini`, pre-0731
`deepseek_v4_flash`) are gone from `SOURCES.json`.

### Docs that still earn their keep

Keep these because a living decision, slot, paper path, or gated
checker still names them:

- Paper source library, canon, and living decisions 0046–0055
- Architecture index and generated method cards
- Retention candidate table and hierarchical matrix
- E5 / G5 remasures and the 08-15 four-family headlines
- Decision 0046 Phase A protocol and the `test60` stage-panel report
- Three ExECT prompt-slot answers and their living protocols
  (leave-one-out, cheap-stack, cheap-stack plain, cheap-stack
  `dev140`, mention-unit v2 catalogs)
- Prescription bounded-policy and rescue-scope protocol/report pairs
  (`scripts/check_exectv2_prescription_*` still require the protocol
  path)
- Protocols a builder still writes into machine JSON
- Manifest-hashed `docs/experiments/` paths
- Luna ExECT variant bundle under `docs/experiments/exectv2/reliability/`
- `evidence_exploration_brief_2026-08-09.md` and
  `six_model_single_letter_walkthrough_2026-08-15.md`
- Annotation IAA notes and literature PDFs
- `documentation_lifecycle.md`

Closed-campaign **answers** stay after their protocols were dropped.
The report is the public result; the protocol is recoverable from
git history.

### Scripts that still earn their keep

Keep these because a runbook, always-on test, retained-evidence
check, or assigned slot still calls them:

- `run_current_stack.py`, `verify_reference_evidence.py`
- Manifest / architecture / hygiene checkers
- Slot runners (leave-one-out, cheap-stack, mention-unit)
- Paper and E5 builders
- `run_exectv2_2call_model_swap.py` (hashed / pytest helper)
- `check_exectv2_prescription_rescue_scope_candidate.py` and the
  bounded-policy checker
- Remaining-cells replay and current-stack panel builder
- `build_trace_explorer_exectv2_comparison.py` (workbench runbook
  still names this thin wrapper)

## What the confident cuts removed

Git history is the restore. Do not put these back as live slots.

**Experiments.** 2-call / `v08` producers; July 18 v0.7 Gan rows;
13 Aug explorer replay; mini 0039 and pre-0731 ExECT forests;
historical sidecars; diagnosis campaign dumps; post-panel
attribution; per-model markdown forests; cheap-stack runner dumps
except `comparison.json` + `structured.jsonl` + `assembly.jsonl`;
Luna residuals; `current_stack/runs/20260815/`. Workbench Gan
`dev750` cells are `not_retained`.

**Docs.** Dated retention-slice logs (matrix and candidate table
stay); unused six-model PNG twins and three unused SVG pairs;
retired case-map deck; closed plans/reviews; leftover 08-01
headlines; Luna leftover protocols; rejected joint / model-preserving
/ diagnosis-guard cluster; closed-campaign protocols whose reports
remain; v0.9.24 sibling prune protocols.

**Scripts.** SF split decomposition, A–C mechanism builder, six-model
figure generator, SF rule-index generator, SF type-key reconcile,
hosted/Ollama/Qwen queue wrappers.

Closed experiment JSON may still name a deleted protocol. That is a
historical pointer, not a reason to restore the file.

## Uncertain leftovers

These still look useful. They were not cut because a living owner,
gated checker, or paper path might still need them. They are not
selected slots.

### Docs

- Prescription bounded + rescue-scope pairs (checker-gated)
- Luna ExECT variant markdown under `docs/experiments/exectv2/reliability/`
- Protocols that builders still write into machine JSON
- Manifest-hashed `docs/experiments/` paths
- Paper walkthrough / exploration brief
- Annotation IAA notes and literature PDFs
- `documentation_lifecycle.md`
- `ACTIVE_ROADMAP` completed-link thinning (deferred since 2026-08-03)

### Scripts

- `build_exectv2_rules_only_four_family_letter_scores_dev140.py`
- `build_exectv2_six_model_test60_stage_panel.py`
- Hard-slice builders (`build_six_model_hard_slice_error_modes.py`,
  `build_six_model_hard_slice_error_mode_examples.py`)
- `smoke_exectv2_six_model_condition.py`
- `run_gan2026_llm_only_condition.py`
- `build_trace_explorer_exectv2_comparison.py` (optional collapse;
  rebind the workbench runbook first)

### Experiments / optional later collapse

From the [candidate table](retention_candidate_table_2026-08-16.md):

- Optional further `*_sf_state_projection_combined.jsonl` review for
  **closed** SF campaign lanes only
- Protocol docs outside the machine manifest that have no focused
  evidence thread
- `current_stack/runs/20260813/` (not a `latest/` duplicate; still
  present)

Do not delete files the three assigned ExECT prompts still need.
Do not restore pruned forests as live comparison cells.
