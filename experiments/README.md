# Experiments

Store run outputs, metrics, row-level predictions, and experiment notes here.

**Start here:** [`KEY_EXPERIMENTS.md`](KEY_EXPERIMENTS.md) — one-screen summaries of the ~12 runs that matter for paper claims and production decisions. Terminology: [`docs/reference/plain_language_glossary.md`](../docs/reference/plain_language_glossary.md).

## Active surface (start here)

Human scan order for the current paper/results sprint:

| Surface | Path |
| --- | --- |
| **Key experiments (plain language)** | [`KEY_EXPERIMENTS.md`](KEY_EXPERIMENTS.md) |
| Machine registry (all decisions) | [`RUN_INDEX.md`](RUN_INDEX.md) ← generated from [`registry.jsonl`](registry.jsonl) |
| ExECTv2 component-off full-200 aggregate replay | [`exectv2_component_off_replay_full200_20260626.md`](exectv2_component_off_replay_full200_20260626.md) |
| ExECTv2 component-off dev140 | [`exectv2_component_off_replay_dev140_20260626.md`](exectv2_component_off_replay_dev140_20260626.md) |
| ExECTv2 same-core full-200 model swap | [`docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_full200_2026-06-25.md`](../docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_full200_2026-06-25.md) |
| ExECTv2 reliability validations | [`docs/experiments/exectv2/reliability/`](../docs/experiments/exectv2/reliability/) (robustness, calibration, review routing) |
| ExECTv2 active scoreboard | [`docs/experiments/exectv2/key_entities/exectv2_dedup_phase1_active_scoreboard_2026-06-23.md`](../docs/experiments/exectv2/key_entities/exectv2_dedup_phase1_active_scoreboard_2026-06-23.md) |
| Gan reliability master scorecard | [`gan2026_reliability_master_scorecard_2026-06-17.md`](gan2026_reliability_master_scorecard_2026-06-17.md) |
| Gan v0.9 selector — Gate 4 exact holdout audit | [`gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_exact_aggregate_audit_2026-06-26.md`](gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_exact_aggregate_audit_2026-06-26.md) |
| Paper-facing rows | [`docs/research/`](../docs/research/) (`exectv2_results_section_draft_2026-06-26.md`, `paper_manuscript_2026-06-26.md`) |
| Retained evidence manifest | [`docs/experiments/retained_evidence_manifest.md`](../docs/experiments/retained_evidence_manifest.md) |

### Gan holdout promotion ladder (Gates 1–4)

Plain-language summary of the frozen v0.9 selector protocol ([`docs/canon/06_gan_clinical_policy.md`](../docs/canon/06_gan_clinical_policy.md), [`docs/experiments/gan2026/frozen_test/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_protocol_2026-06-26.md`](../docs/experiments/gan2026/frozen_test/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_protocol_2026-06-26.md)):

- **Gate 1 — Validation hard-slice audit:** Confirm selector gains are not hiding brittle behavior in weak families (changed-label rows, boundary bands, residual taxonomy). Failing blocks any holdout-facing selector claim.
- **Gate 2 — Robustness and stress panels:** Test selector gates on source-near and adversarial component states before spending holdout budget. Synthetic/mechanism tests, not benchmark evidence.
- **Gate 3 — Test source-symmetry preflight:** Hash-pin every test450 component so locked-test audit uses the same roles as validation (deterministic floor, consensus agents, fresh-evidence counterpart). Exact vs constrained symmetry determines claim language.
- **Gate 4 — Locked test450 aggregate audit:** User-authorized, aggregate-only holdout readout after Gates 1–3 pass. Promotion bars: ≥+10 Purist rows vs deterministic floor, ≤5 correct-to-wrong, changed-label precision ≥0.60. No row-level failure inspection or tuning from the result.

Superseded iteration notes (checkpoints, pre-v08 lanes, historical Gan lineage)
live under [`archive/`](archive/) with bucket manifests in
[`archive/ARCHIVE_INDEX.md`](archive/ARCHIVE_INDEX.md). JSON/JSONL artifacts
stay in `experiments/` for reproduction even when the human note was archived.

## Registry and layout

Prefer timestamped or named subdirectories. Keep enough metadata to reproduce the run.
Use `experiments/registry.jsonl` as the durable machine-readable index for
canonical and high-signal runs. Regenerate `experiments/RUN_INDEX.md` from that
registry when entries change so humans can scan the same decisions without
hand-reading JSONL. The registry does not replace raw artifacts; it records
which artifact family is live, replayed, rejected, superseded, historical, or a
revise signal. Backfill it selectively when a run affects project decisions.

Use `data/Gan (2026)/splits/gan2026_split_v1.json` for Gan 2026 work. Ordinary
development runs should report validation metrics. Train is reserved for DSPy GEPA
or another optimizer. Test is a locked final holdout and should not be used for
row-level debugging or tuning.

For LLM/DSPy and hybrid architecture work, do not default to all 750 validation
rows. Use the standard validation ladder:

1. 25 validation rows for smoke tests.
2. 50 validation rows for meaningful prompt/schema/model signal.
3. 250 validation rows only after the 50-row run passes a decision gate.

The decision gate for moving from 50 to 250 is: no systemic call failures, no
unresolved schema/parse failure family, evidence behavior good enough for
row-level review, and a written reason that the larger slice will decide whether
to promote, revise, or reject the candidate. Full 750-row validation runs should
be rare and must state why 250 rows are insufficient.

For LLM-backed runs, include the model role, display name, exact provider/API
identifier when available, hosted versus local execution details, prompt/program
version, deterministic-rule configuration, and whether the output came from a
direct program, repaired output, or optimizer-generated program. See
`docs/design/model_strategy.md`.

Registry entries should preserve:

- run id and artifact paths;
- date, pipeline family, split, and row count;
- model, model role, run mode, replay status, and cache/reuse source;
- named repair mode or deterministic rule configuration;
- primary metrics and evidence-validity summary;
- decision status and conservative claim-language notes.
