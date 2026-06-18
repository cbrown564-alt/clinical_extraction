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
- v0.4 is now the best single-prompt dev25 candidate:
  `experiments/exectv2_llm_only_key_entities_structured_v04_dev25_gpt41mini_20260618.md`.
  It recovered SeizureFrequency to `0.644` clinical headline F1 while preserving
  medication (`0.900`) and Investigations (`0.837`) above target. Diagnosis only
  moved to `0.460`, making concept/assertion recovery the primary bottleneck.
  See `docs/research/exectv2_key_entities_structured_v04_pilot_report_2026-06-18.md`.
- v0.5 is the best single-prompt dev25 candidate so far:
  `experiments/exectv2_llm_only_key_entities_structured_v05_dev25_gpt41mini_20260618.md`.
  Diagnosis improved to `0.569` clinical headline F1 while medication (`0.897`)
  and Investigations (`0.837`) stayed above target and SF stayed at `0.633`.
  This supports moving to a specialist Diagnosis prompt comparison on the same
  dev25 surface before dev140. See
  `docs/research/exectv2_key_entities_structured_v05_pilot_report_2026-06-18.md`.
- The existing per-entity Diagnosis specialist prompt is not competitive with
  v0.5: clinical headline F1 `0.282` vs v0.5 single structured `0.569`, despite
  a clean gate and source-near recall lift versus the old all-9 baseline. See
  `docs/research/exectv2_diagnosis_specialist_prompt_comparison_2026-06-18.md`.
- Diagnosis verifier v0.1 is the first multi-prompt variant to beat v0.5 on the
  objective-aligned Diagnosis headline: `0.592` vs `0.569`, with a clean gate and
  evidence validity `1.0000`. It improves precision but loses recall, so v0.2
  should target recall without reintroducing symptom/non-epileptic FPs. See
  `docs/research/exectv2_diagnosis_verifier_v01_pilot_report_2026-06-18.md`.
- Diagnosis verifier v0.2 is now the best Diagnosis-specific candidate:
  clinical headline F1 `0.619` with precision `0.682`, recall `0.566`, and
  evidence validity `1.0000`. It improves over v0.1 by allowing model-owned
  normalized concept text while keeping exact evidence. See
  `docs/research/exectv2_diagnosis_verifier_v02_pilot_report_2026-06-18.md`.
- Diagnosis verifier v0.3 is now the best Diagnosis-specific candidate:
  clinical headline F1 `0.701` with precision `0.773`, recall `0.641`, and
  evidence validity `1.0000`. It targeted v0.2 residual misses around repeated
  tonic-clonic assertions, epilepsy-with-generalised-tonic-clonic-seizures-alone
  syndrome rendering, uncertain temporal/focal seizure-type diagnoses, and
  non-named symptom suppression. It is still revise-only because Diagnosis
  remains below `0.8`. See
  `docs/research/exectv2_diagnosis_verifier_v03_pilot_report_2026-06-18.md`.
- Diagnosis verifier v0.4 is now the best Diagnosis-specific candidate:
  clinical headline F1 `0.768` with precision `0.826`, recall `0.717`, and
  evidence validity `1.0000`. It targeted only v0.3 residual families
  (singular one-off seizure text, duplicated independently supported seizure
  assertions, uncertain focal-onset lines, probable-cause wording, intractable
  epilepsy, epileptic-event normalization, febrile-history suppression, and
  generic reviewed-with-epilepsy recovery). It remains revise-only but is close
  enough to justify one residual-error v0.5 loop before dev140. See
  `docs/research/exectv2_diagnosis_verifier_v04_pilot_report_2026-06-18.md`.
- Diagnosis verifier v0.5 is the first Diagnosis-specific candidate to clear the
  dev25 target: clinical headline F1 `0.837` with precision `0.911`, recall
  `0.774`, and evidence validity `1.0000`. This is a development-surface
  success only and needs dev140 confirmation before any generalization claim.
  The remaining below-target key family on dev25 is now SeizureFrequency
  (`0.633` best single structured headline). See
  `docs/research/exectv2_diagnosis_verifier_v05_pilot_report_2026-06-18.md`.
- SeizureFrequency verifier v0.1 is a clean diagnostic improvement over the
  v0.5 single structured draft, but not a promoted candidate: clinical headline
  F1 `0.667` vs `0.633`, precision `0.629`, recall `0.710`, evidence validity
  `1.0000`. It confirms the verifier path can add recall, but v0.2 must recover
  precision and still clear `0.8` before any dev140 run. See
  `docs/research/exectv2_sf_verifier_v01_pilot_report_2026-06-18.md`.
- SeizureFrequency verifier v0.3 is the first SF-specific candidate to clear the
  dev25 target: clinical headline F1 `0.831` with precision `0.794`, recall
  `0.871`, and evidence validity `1.0000`. Together with medication (`0.897`),
  Diagnosis verifier v0.5 (`0.837`), and Investigations (`0.837`), all four key
  families now clear `0.8` on dev25. This is still development-surface evidence
  only; next step is a predeclared dev140 readout. See
  `docs/research/exectv2_sf_verifier_v03_pilot_report_2026-06-18.md`.
- The dev140 transfer readout did not confirm the dev25 result. Single
  structured v0.5 dev140 is clean but below target for medication (`0.777`) and
  Investigations (`0.786`); Diagnosis verifier v0.5 transfers to only `0.616`;
  SeizureFrequency verifier v0.3 transfers to only `0.602`. Treat the dev25
  success as local development evidence and restart from dev140 residual slices.
  See
  `docs/research/exectv2_key_entities_dev140_transfer_readout_2026-06-18.md`.
- The dev140 clinical-recovery error ledger is now built:
  `experiments/exectv2_key_entities_clinical_error_ledger_dev140_20260618.md`.
  It confirms the next loop should use the single structured draft as substrate
  but add family-specific verification: medication over-emits lamotrigine
  titration/future doses, Investigations over-emits modality-only tests and
  misses normal/abnormal result attributes, Diagnosis needs hierarchy/assertion
  normalization, and SF needs generic-vs-specific state classification. See
  `docs/research/exectv2_key_entities_dev140_clinical_error_ledger_readout_2026-06-18.md`.
- Prescription/Investigations verifier v0.1 is a split decision on dev140:
  Prescription clears target (`0.817`, precision `0.773`, recall `0.865`) and
  should replace the single structured medication output for now, but
  Investigations regresses badly (`0.496`) and should stay on the single
  structured v0.5 baseline (`0.786`) until a dedicated verifier exists. See
  `docs/research/exectv2_med_inv_verifier_v01_dev140_report_2026-06-18.md`.

## Active Priorities

1. Build dev140 clinical-recovery error ledgers for Prescription,
   Investigations, Diagnosis, and SeizureFrequency; use them to separate source
   coverage, concept normalization, attribute/state rendering, and over-emission.
2. Require benchmark-beating dev evidence before any new full-200 audit:
   overall `0.87` per-item / `0.90` per-letter, plus per-entity tables,
   evidence/schema reliability, semantic-vs-CUI gaps, and ablations.

## Work Board

### Now

- Build a dedicated Investigations verifier from the dev140 ledger. Keep
  Prescription verifier v0.1 as the current medication candidate.

### Next

- Draft a dev140-led v0.6/v0.4 architecture plan after residual ledgers identify
  which families need prompt-only fixes versus new verifier decomposition.
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
  (`0.421`). v0.4 recovered SF to `0.644` while preserving medication and
  Investigations above target; v0.5 then lifted Diagnosis to `0.569` while
  preserving the other family wins. Runs are registered in
  `experiments/RUN_INDEX.md`. The first specialist Diagnosis comparison rejected
  the old per-entity frame (`0.282` clinical F1 vs v0.5 `0.569`); the v0.1
  Diagnosis verifier improved to `0.592`, v0.2 improved to `0.619`, v0.3
  improved to `0.701`, v0.4 improved to `0.768`, and v0.5 cleared the dev25
  Diagnosis target at `0.837`. The SeizureFrequency verifier then moved SF from
  `0.633` to `0.667` (v0.1), `0.788` (v0.2), and finally `0.831` (v0.3) with
  clean gates, clearing all four key families on dev25. Latest
  report:
  `docs/research/exectv2_sf_verifier_v03_pilot_report_2026-06-18.md`.
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
