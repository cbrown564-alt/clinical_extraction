# Project status

Last updated: 2026-08-03 during the documentation corpus triage pass

## Current handoff objective

[Decision 0048](docs/decisions/0048-comprehension-and-handoff-refactor.md)
sets the active priority: turn the verified research system into a clean,
immediately useful handoff package without removing the live-run capability
needed for new experiments and external validation.

[Decision 0049](docs/decisions/0049-pytest-research-validity-firewall.md)
is complete through Wave 4: plain `pytest` is the always-on research-validity
firewall and collects **243** tests (**verified 2026-08-02**, all passed,
~40s). Architecture manifests name short governing owners; the deep allowlist
is empty. Supervisor handoff still traces
`tests/test_clinical_extraction_local_parity.py`.

The retained operational boundary is the selected six-model × three-method ×
two-task system, its frontend development workflows, saved/fixture and live
demonstrations, exact no-call replay, essential decision evidence, and a
restricted research-validation workflow. Cleanup is behavior-preserving by
default; clinical, scoring, split, prompt, routing, or evidence-policy changes
require a separate predeclared study.

Completion requires a supervisor to navigate from the README to the frontend,
the six-path teaching case, the canonical results report, evidence and limits,
and reproduction commands without agent assistance. Engineering verification,
research evidence, independent clinical review, and clinical validation remain
separate claims.

## Decision 0048 current point

Active method names are `rules`, `llm`, and `llm_with_rules` across runtime,
API/frontend, teaching material, and generated architecture. Historical
replay identities remain. Label-leftover blockers (`comparison_mode` removal,
stage-ID rename to active-method namespaces, ExECT component-ablation removal
from the supervisor path, Gan ablation retag) are implemented in the working
tree and still need to land before the 0048 status flip.

Retention waves through 2026-08-02 removed unserved mocks, orphan docs, and
large scoring-lane orphans; retained-evidence checks remain the gate. The
standalone handoff tree and ZIP are rebuilt; supervisor-host verification and
unaided README review remain open. Owner:
[handoff plan](docs/plans/supervisor_local_extraction_handoff_plan.md).

Documentation corpus triage advanced 2026-08-03: thinned active index and
live-view status; six orphan docs deleted; Decision 0046/0047 evidence rebound;
five peer satellites deleted after living-cited rebinds. README currency
remains deferred. Owners:
[corpus slice](docs/research/maintenance/retention_slice_documentation_corpus_2026-08-03.md),
[peer-satellite slice](docs/research/maintenance/retention_slice_peer_satellites_2026-08-03.md),
[REGENERATION.md](docs/REGENERATION.md).

## Current outcome

The selected six-model × three-method × two-task system is operational for
live generation, saved/fixture demonstration, frontend development workflows,
and exact no-call replay of the six retained reference cells. Decision 0047
canonical orchestrators own the six selected task-method paths.

Decision 0046 locks the paper's primary ExECT three-method comparison on
Sol-matched four-family `clinical_headline`. Primary fills: rules-only
`0.8160` (`dev140`) / `0.7154` (`test60`); Sol LLM-only `0.8097` / `0.7771`;
Sol hybrid `0.8920` / `0.8047`. Owners:
[decision 0046](docs/decisions/0046-exect-primary-method-comparison-boundary.md),
[stage panel](experiments/exectv2_six_model_test60_stage_panel_20260801/panel_aggregate.json),
[rules-only dev140](experiments/exectv2_rules_only_four_family_clinical_headline_dev140_20260801.json),
[rules-only test60](experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260801.json).

## Fresh evidence

- **Selected matrix owners:** [comparison report](docs/research/six_model_comparison_report_2026-07-18.md),
  [retained evidence index](docs/experiments/retained_evidence_manifest.md),
  [paper claim status](docs/canon/10_paper_provenance.md).
- **Decision 0048/0049:** method migrations and pytest firewall are verified on
  the stated dates above; host/unaided handoff checks and the 0048 status flip
  remain open.
- **Decision 0046 primary fills:** A→B→C protocol complete; numbers above.
  A consistency glance may still find residual manuscript wording drift; that
  is a separate Next item, not part of index triage.
- **Open DeepSeek unknown thread:** U stopped after UNK-slice pilot; do not
  resume U to full-750. Owners:
  [thread](docs/research/gan2026_deepseek_unknown_competence_thread_2026-07-31.md),
  [pilot compare](experiments/gan2026_deepseek_unknown_heavy_slice_u_vs_a_20260731.json).
- **Open semantic-support review:** 48-item ExECT substrate unreviewed.
  Owner: [protocol](docs/experiments/exectv2/reliability/exectv2_semantic_support_review_substrate_protocol_2026-07-18.md).

## Verification state

- **Always-on pytest (2026-08-02):** 243 collected/passing; deep allowlist empty.
- **Retained evidence:** manifest check and six no-call reference replays remain
  the selected reproduction gate (`scripts/check_retained_evidence_manifest.py`,
  `scripts/verify_reference_evidence.py`).
- **Handoff packaging:** source-to-shipped closure current; supervisor-host and
  unaided README review not done.
- Older full-suite and frontend green checks from the ExECT method-migration
  merges remain in Git history; they are not re-listed here as live archaeology.

## In progress

- Decision 0048 label-leftover blockers in the working tree, awaiting commit
  and the remaining host/unaided checks before status flip.
## Next

1. Verify the rebuilt supervisor handoff on the intended host/endpoint and
   perform unaided README review.
2. Land remaining Decision 0048 label-leftover working-tree changes; run the
   strict completion gate only after host/unaided checks pass.
3. Keep research and validation dependencies intact: do not resume DeepSeek U
   to 750; defer local-route DeepSeek parity until its runtime exists; retain
   independent clinical review as unvalidated; never tune from sealed
   `test450`, Real(300), or ExECT `test60`.
4. README currency pass (deferred from documentation corpus triage).
5. If manuscript wording still contradicts Decision 0046 primary rows, open a
   separate provenance edit.

## Blocked or unvalidated

- Independent clinical review remains required before any clinical-validity
  claim.
- Exact evidence is measured; semantic support remains unmeasured until the
  48-item ExECT substrate is reviewed.
- Supervisor endpoint/host setup and unaided README use remain open.
- ExECT joint/`combined` assembly stays archived under
  [decision 0045](docs/decisions/0045-exect-default-policy-not-joint-combined.md);
  it is not an active comparison surface.

## Data and claim boundaries

- **Gan `test450`:** locked and aggregate-only. Do not perform failure analysis
  or prompt, repair, or scorer changes from test rows.
- **ExECT `dev140`:** development review is permitted.
- **ExECT `test60`:** locked and aggregate-only; sealed row artifacts must not
  be inspected or shared.
- **Scores:** Gan reports Purist and Pragmatic label accuracy. ExECT
  `clinical_headline` is an internal research metric, not the published
  benchmark.

## Canonical owners

- Exact retained files, hashes, and replay:
  [retained evidence index](docs/experiments/retained_evidence_manifest.md)
- Paper claim strength: [paper claim status](docs/canon/10_paper_provenance.md)
- Work order: [active roadmap](docs/plans/ACTIVE_ROADMAP.md)
- Regeneration and retention triage: [REGENERATION.md](docs/REGENERATION.md)
- Handoff refactor: [Decision 0048](docs/decisions/0048-comprehension-and-handoff-refactor.md)
- Cross-task six-model synthesis:
  [comparison report](docs/research/six_model_comparison_report_2026-07-18.md)
- DeepSeek unknown-competence (open):
  [thread](docs/research/gan2026_deepseek_unknown_competence_thread_2026-07-31.md)
- Active documentation index: [NAVIGATION.md](docs/NAVIGATION.md) and
  [THREAD_MAP.md](docs/THREAD_MAP.md)

Use *implemented*, *verified*, *validated*, and *promoted* precisely.
