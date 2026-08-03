# Project status

Last updated: 2026-08-03 after pre-gate ExECT evidence + open mechanism questions

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
replay identities remain. The Decision 0048 label-leftover blockers landed in
`d8f39378`; residual plain group-label and Gan ablation display polish landed
2026-08-03. Host/unaided review remains before the status flip.

Retention waves through 2026-08-02 removed unserved mocks, orphan docs, and
large scoring-lane orphans; retained-evidence checks remain the gate. The
standalone handoff tree and ZIP are rebuilt; supervisor-host verification and
unaided README review remain open. Owner:
[handoff plan](docs/plans/supervisor_local_extraction_handoff_plan.md).

Documentation corpus triage advanced 2026-08-03: thinned active index and
live-view status; six orphan docs deleted; Decision 0046/0047 evidence rebound;
five peer satellites deleted after living-cited rebinds. README currency pass
complete: glance layer shows Gan and ExECT primary results as peers. Owners:
[corpus slice](docs/research/maintenance/retention_slice_documentation_corpus_2026-08-03.md),
[peer-satellite slice](docs/research/maintenance/retention_slice_peer_satellites_2026-08-03.md),
[REGENERATION.md](docs/REGENERATION.md), [README](README.md).

## Current outcome

The selected six-model × three-method × two-task system is operational for
live generation, saved/fixture demonstration, frontend development workflows,
and exact no-call replay of the six retained reference cells. Decision 0047
canonical orchestrators own the six selected task-method paths. Gan and ExECT
results are equally primary; scores are not interchangeable across tasks.

**Gan 2026 (Purist):** selected `llm_with_rules` final holdout results give Sol
`0.85` on `test450`; DeepSeek `0.82`. On `dev750`, mini `0.90` and Sol/Luna
`0.88`. Development method peers on `dev750` (GPT-4.1-mini three-way
reference): rules `0.93`, llm `0.77`. Owners:
[final panel](experiments/six_model_final_panel_20260803/panel_aggregate.json),
[comparison report](docs/research/six_model_comparison_report_2026-07-18.md),
[paper claim status C16](docs/canon/10_paper_provenance.md),
retained three-way reference cells in
[retained evidence index](docs/experiments/retained_evidence_manifest.md).

**ExECTv2 (clinical fact F1):** Decision 0046 locks the paper's primary
three-method comparison on Sol-matched four-family scores. Primary fills:
rules `0.8160` (`dev140`) / `0.7154` (`test60`); Sol llm `0.8097` / `0.7771`;
Sol llm_with_rules `0.8920` / `0.8047`. Owners:
[decision 0046](docs/decisions/0046-exect-primary-method-comparison-boundary.md),
[stage panel](experiments/exectv2_six_model_test60_stage_panel_20260801/panel_aggregate.json),
[rules-only dev140](experiments/exectv2_rules_only_four_family_clinical_headline_dev140_20260801.json),
[rules-only test60](experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260801.json).

## Fresh evidence

- **Selected matrix owners:** [final panel](experiments/six_model_final_panel_20260803/panel_aggregate.json)
  (`six_model.final_panel.v4`: LLM-only development cells plus ExECT
  `dev140` pre-gate exact-evidence / repair / hard-drop), finding-led
  [comparison report](docs/research/six_model_comparison_report_2026-07-18.md)
  with open mechanism questions A–C, [retained evidence index](docs/experiments/retained_evidence_manifest.md),
  [paper claim status](docs/canon/10_paper_provenance.md). Key report reading:
  ExECT large holdout drops under LLM with rules are mostly rules lift that
  does not transfer; post-rules exact-evidence ~`1.00` is a filter, not model
  quality (pre-gate rates diverge, Qwen ~0.86); Gan “better models, smaller
  gap” is mainly LLM-with-rules.
- **Decision 0048/0049:** method migrations and pytest firewall are verified on
  the stated dates above; README glance currency pass complete with Gan and
  ExECT as equal primary strips; host/unaided handoff checks and the 0048
  status flip remain open.
- **Decision 0046 primary fills:** A→B→C protocol complete; numbers above.
  Manuscript primary ExECT three-method rows aligned 2026-08-03
  ([working manuscript](docs/research/paper_manuscript_2026-06-26.md)); GEPA
  and `v08` remain secondary controls only.
- **DeepSeek V4-Flash-0731:** folded into the
  [final six-model panel](experiments/six_model_final_panel_20260803/panel_aggregate.json)
  (ExECT `test60` `0.81`; Gan Purist `0.82`). Provider-update study remains at
  [0731 report](docs/research/deepseek_v4_flash_0731_matched_comparison_report_2026-08-03.md).
  Decision 0046 Sol method-row fills are unchanged. Gan llm_only `test450` =
  `0.74`; matched llm_only `dev750` re-run is **in progress**.
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
- **Handoff packaging:** source-to-shipped closure current after rebuild that
  ships prepared `demo.ipynb` (synthetic fixtures + optional live cells);
  supervisor-host and unaided README review not done.
- Older full-suite and frontend green checks from the ExECT method-migration
  merges remain in Git history; they are not re-listed here as live archaeology.

## In progress

- Decision 0048 host/unaided supervisor checks before status flip.

## Next

1. Verify the rebuilt supervisor handoff on the intended host/endpoint
   (including prepared `demo.ipynb` Run All, then optional live cells) and
   perform unaided README review against the decluttered glance layer.
2. Run the strict Decision 0048 completion gate only after host/unaided checks
   pass.
3. Keep research and validation dependencies intact: do not resume DeepSeek U
   to 750; defer local-route DeepSeek parity until its runtime exists; retain
   independent clinical review as unvalidated; never tune from sealed
   `test450`, Real(300), or ExECT `test60`.
4. Optional: if the standalone handoff package should point supervisors at the
   repository glance layer, add a short link from `handoff/source/README.md`
   (operational package README remains distinct from the research front door).

## Blocked or unvalidated

- Independent clinical review remains required before any clinical-validity
  claim.
- Exact evidence is measured; semantic support remains unmeasured until the
  48-item ExECT substrate is reviewed.
- Supervisor endpoint/host setup and unaided README use remain open.
- ExECT joint/`combined` assembly stays archived under
  [decision 0045](docs/decisions/0045-exect-default-policy-not-joint-combined.md);
  it is not an active comparison.

## Data and claim boundaries

- **Gan `test450`:** locked and aggregate-only. Do not perform failure analysis
  or prompt, repair, or scorer changes from test rows.
- **ExECT `dev140`:** development review is permitted.
- **ExECT `test60`:** locked and aggregate-only; sealed row artifacts must not
  be inspected or shared.
- **Scores:** Gan reports Purist and Pragmatic label accuracy. ExECT clinical
  fact recovery is an internal research metric, not the published benchmark
  (code and saved scores still use `clinical_headline`).

## Canonical owners

- Exact retained files, hashes, and replay:
  [retained evidence index](docs/experiments/retained_evidence_manifest.md)
- Paper claim strength: [paper claim status](docs/canon/10_paper_provenance.md)
- Work order: [active roadmap](docs/plans/ACTIVE_ROADMAP.md)
- Regeneration and retention triage: [REGENERATION.md](docs/REGENERATION.md)
- Handoff refactor: [Decision 0048](docs/decisions/0048-comprehension-and-handoff-refactor.md)
- Cross-task six-model final results:
  [final panel](experiments/six_model_final_panel_20260803/panel_aggregate.json),
  [comparison report](docs/research/six_model_comparison_report_2026-07-18.md)
- DeepSeek V4-Flash-0731 matched comparison:
  [report](docs/research/deepseek_v4_flash_0731_matched_comparison_report_2026-08-03.md)
- DeepSeek unknown-competence (open):
  [thread](docs/research/gan2026_deepseek_unknown_competence_thread_2026-07-31.md)
- Active documentation index: [NAVIGATION.md](docs/NAVIGATION.md) and
  [THREAD_MAP.md](docs/THREAD_MAP.md)

Use *implemented*, *verified*, *validated*, and *promoted* precisely.
