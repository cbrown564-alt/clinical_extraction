# Project Status

Last updated: 2026-06-18

## Active Objective

ExECTv2 is now the forward workstream. Use the Gan 2026 closeout as the strategy
template for full deterministic, LLM-only, and hybrid runs: source-near state,
exact evidence, component attribution, benchmark-format ablations, and
family-aware promotion gates. Current target is key-entity F1 >0.8 for
Prescription/medication, Diagnosis, SeizureFrequency, and Investigations. Pursue
the single structured schema + single prompt path first; use `gpt-4.1-mini` for
rapid loops and keep Qwen 3.6:35B as a later transfer track.

## Recent Context

- Split discipline remains intact. Gan `test450` remains aggregate-only for
  development; ExECTv2 full-200 audits are blocked until a GPT-first architecture
  has benchmark-beating dev evidence and a predeclared readout. Gan is closed:
  V12 fresh-evidence hybrid ceiling `379/450` Purist (`0.842`); recommended
  simple labeler `364/450` Purist (`0.809`).
- GPT-first ExECTv2 strategy:
  `docs/research/exectv2_gpt_first_full_architecture_strategy_2026-06-17.md`.
  Freeze blockers: rules-only all-9 below target, LLM-only all-9 still a
  negative single-pass baseline, and hybrid evidence still SF-only.
- Deterministic all-9 dev scorecard:
  `experiments/exectv2_deterministic_all9_dev_20260617.md`; benchmark `0.3625`
  item / `0.6747` letter. PatientHistory is conservative at `0.2087` item /
  `0.5475` letter with `157/157` emitted mentions carrying CUI.
- Shared `project_cuis` is now wired into ExECTv2 LLM-only and hybrid
  post-steps, including SeizureFrequency. The source-near/semantic layers remain
  inspectable while benchmark-format CUI projection is counted separately.
- Single-prompt four-family structured events v0.1 is built and piloted on dev25:
  `experiments/exectv2_llm_only_key_entities_structured_dev25_gpt41mini_20260618.md`.
  Gate is clean (`0` call/parse failures, evidence validity `0.9539`) but not
  near target: semantic item F1 `0.206`, benchmark `0.158`, source-near `0.722`.
  This is a viable architecture baseline, not a promoted candidate.
- v0.2 confirms error-analysis-led prompt optimization works but is not enough:
  `experiments/exectv2_llm_only_key_entities_structured_v02_dev25_gpt41mini_20260618.md`
  improved semantic item F1 `0.206`→`0.272` and benchmark `0.158`→`0.220`
  with `0` call/parse failures and evidence validity `0.9760`. The
  objective-aligned clinical-recovery headline now shows the real target state:
  Prescription/medication is above target (`0.846`), Investigations is near
  target (`0.783`), while Diagnosis (`0.414`) and SeizureFrequency (`0.456`)
  are the bottlenecks. See
  `docs/research/exectv2_key_entities_structured_v02_pilot_report_2026-06-18.md`.
- v0.3 is a revise-only prompt iteration:
  `experiments/exectv2_llm_only_key_entities_structured_v03_dev25_gpt41mini_20260618.md`.
  Medication (`0.883`) and Investigations (`0.878`) now clear the clinical
  headline target; Diagnosis improved modestly (`0.455`), but SeizureFrequency
  slipped (`0.421`) and evidence validity fell to `0.9441`. Next work should be
  SF/Diagnosis error-analysis first, not more broad prompt accretion. See
  `docs/research/exectv2_key_entities_structured_v03_pilot_report_2026-06-18.md`.

## Active Priorities

1. Iterate the single-prompt four-family structured-event architecture from the
   dev25 clinical-recovery error slices: protect medication above `0.8`, lift
   Investigations precision, and focus most prompt/error-analysis work on
   Diagnosis and SeizureFrequency.
2. Require benchmark-beating dev evidence before any new full-200 audit:
   overall `0.87` per-item / `0.90` per-letter, plus per-entity tables,
   evidence/schema reliability, semantic-vs-CUI gaps, and ablations.

## Work Board

### Now

- Build v0.4 on the same dev25 surface using clinical-recovery headline F1 as
  the promotion readout: preserve medication/investigation wins, diagnose the
  SF headline-state regression by miss family, and continue Diagnosis certainty
  and specific-syndrome work.

### Next

- If v0.3 improves semantic F1 without entity-level collapse, run dev140 and
  compare against the per-entity prompt family.
- Compare the best single-prompt structured-event variant against the existing
  per-entity prompt family before returning to specialist/verifier variants.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, or post-test tuning remain
  blocked without explicit authorization and a frozen protocol.
- New ExECTv2 full-200 audits are blocked until benchmark-beating GPT-first dev
  evidence and a predeclared aggregate readout.

### Backlog

- Resume ExECTv2 Qwen event-frame dev25/dev140 after GPT choices are clearer.

### Done Recently

- 2026-06-18: Added `llm_only_key_entities_structured`, a single-prompt
  structured clinical-event extractor for Prescription/medication, Diagnosis,
  SeizureFrequency, and Investigations, plus runner/tests and a live dev25 GPT
  pilot. v0.2 then lifted semantic item F1 to `0.272` and benchmark to `0.220`
  with a clean gate. The refreshed objective-aligned headline table shows
  medication already above target (`0.846`), Investigations near target
  (`0.783`), and Diagnosis/SF below target (`0.414`/`0.456`). v0.3 then moved
  medication and Investigations above target (`0.883`/`0.878`) but regressed SF
  (`0.421`). Runs are registered in `experiments/RUN_INDEX.md`; latest report:
  `docs/research/exectv2_key_entities_structured_v03_pilot_report_2026-06-18.md`.
- 2026-06-17: Built the reusable all-entity projection-gap ledger
  (`reports/projection_gap_ledger.py`). Classifies every gold FN / predicted FP
  into a layered `gap_family` (phrase coverage, attribute bundle, CUI
  projection, over-emission) and an orthogonal `miss_kind` (candidate-source vs
  projection by Finding 2's CUI-recovery proxy), with a per-entity regime
  rollup and a Prescription component-family table (source/defaulted frequency,
  rescue, future medication, weight dosing, phrase scope, DrugName CUI). Dev
  artifact reproduces the layered error analysis exactly: 1021 gold misses,
  340/1021 = 0.333 projection share, and the published per-entity regimes. 5
  new tests; full ExECTv2 suite (279) and Ruff on touched files pass.
- 2026-06-17: Extended shared benchmark-format CUI projection to
  SeizureFrequency and wired `project_cuis` into LLM-only SF, LLM-only all-entity,
  clinical-findings, and hybrid post-steps. Preserved explicit
  format/semantic-vs-CUI layers for ablation. Verified `1573` tests pass and
  Ruff on touched files; full-project Ruff remains blocked by pre-existing lint
  in old experiment/test surfaces.
- 2026-06-17: Completed the deterministic all-9 substrate: Prescription,
  Investigations, Diagnosis, Onset, WhenDiagnosed, BirthHistory, EpilepsyCause,
  PatientHistory, SeizureFrequency, and the Prescription clinical headline plus
  benchmark projection ladder. Current all-9 dev benchmark `0.3625` item /
  `0.6747` letter.
- 2026-06-14 to 2026-06-17: Closed the Gan strand and wrote the GPT-first
  ExECTv2 architecture strategy; Qwen moved to an overnight transfer track.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- New Gan holdout-facing runs require explicit frozen-protocol authorization.
- Keep architecture claims attribution-clean across `rules_only`, `llm_only`,
  and `hybrid`.
- Treat Gan-specific rules and benchmark-format repairs as controlled variables,
  not hidden implementation detail.

## Core Artifacts

- `experiments/exectv2_deterministic_all9_dev_20260617.md`
- `experiments/exectv2_projection_gap_ledger_dev.md`
- `docs/research/exectv2_gpt_first_full_architecture_strategy_2026-06-17.md`
- `docs/research/gan2026_research_closeout_synthesis_2026-06-17.md`
- `experiments/RUN_INDEX.md`
