# Project status

Last updated: 2026-07-15

## Current outcome

The repository cleanup, engineering repair, selected-evidence replay, paper
build, Gan efficiency audit, ExECT published-metric development, and ExECT
component-policy studies are complete. The active work is the fixed ExECTv2
six-model comparison on the permitted `dev140` split.

[Decision 0040](docs/decisions/0040-final-exect-llm-with-rules-family-ownership.md)
owns the final model-led family boundary and selected joint bounded policy.
[Decision 0041](docs/decisions/0041-single-call-exect-model-comparison.md)
owns the single structured call per letter. This is an accepted quality and
resource-policy tradeoff, not measured cost or latency evidence.

The clean decision-0041 hosted ExECT panel is complete on dev140 and frozen
aggregate-only test60 for GPT-4.1-mini, GPT-5.6 Luna, GPT-5.6 Sol, and
thinking-enabled DeepSeek V4 Flash. All four test60 conditions completed 59/59
letters with zero call or blocking parse failures. Qwen 3.6:35B and Gemma 4
26B have not started. The missing Gan test450 Luna and Sol conditions are also
complete. The final Gan comparison will retain those two runs and add four
fresh conditions under prompt v0.7 and the same current pipeline.

## Fresh evidence

- The four completed hosted ExECT runs use prompt
  `exectv2_hybrid_key_family_event_ledger_v0.9.24`, split `dev140`, one live
  structured call per letter, and the same downstream family lenses and scorer.
- Their `clinical_headline` F1 scores are `0.8202` for GPT-4.1-mini, `0.8832`
  for GPT-5.6 Luna, and `0.8920` for GPT-5.6 Sol. Exact evidence rate is `1.0`
  after assembly for every family in all three final readouts.
- The completed DeepSeek condition uses `deepseek/deepseek-v4-flash` with
  thinking enabled and has a clean 140/140 final artifact.
- On frozen ExECT test60, `clinical_headline` F1 is `0.7572` for GPT-4.1-mini,
  `0.7950` for Luna, `0.8047` for Sol, and `0.7881` for thinking DeepSeek. These
  are aggregate-only internal-scorer results, not published benchmark scores.
- On locked Gan test450 under current prompt v0.7, Luna scored `352/450`
  Purist and `365/450` Pragmatic with three parse/schema/label issues; Sol
  scored `358/450` Purist and `376/450` Pragmatic with zero call or parse
  failures. The source artifact for the retained GPT-4.1-mini `364/450` Purist
  result identifies prompt v0.5, not v0.6 as previously recorded. Thinking
  DeepSeek scored `346/450` on v0.7, but that run used the older
  `deepseek-reasoner` route and pre-refactor pipeline.
- A no-call GPT-4.1-mini ablation found that the one-call Diagnosis architecture
  reduced final Diagnosis F1 from `0.8727` to `0.8542`, with 3 rescues and 11
  regressions. Decision 0041 accepts that loss to avoid a second model pass.
- The selected joint bounded policy produced 172 rescues, 3 regressions, and
  retained 153/160 current-policy rescues on saved dev140 outputs. EA0117 and
  EA0141 remain known development failures. Its component studies and replay
  are owned by the linked reports in [documentation navigation](docs/NAVIGATION.md).

## Verification state

- Last clean broad verification before the current policy and runner changes:
  1,227 tests, Ruff, mypy, the retained-evidence check, all six no-call reference
  replays, and a two-pass IEEE build passed on 2026-07-15. All three PDF pages
  were rendered and visually checked.
- The joint-policy change subsequently passed 21 focused tests, Ruff, its
  no-call replay, and the retained-evidence check.
- The single-call Diagnosis and split-control change passed 18 focused tests,
  Ruff, mypy across 288 source files, and its no-call replay.
- The hosted-run timeout and clean-completion safeguards passed 23 focused
  tests after the Sol transport diagnosis.
- The later 1,246-test run had 1,240 passes and six evidence-bookkeeping
  failures: three contaminated checkpoint documents were outside the allowlist,
  and the retained-evidence freeze still named pre-correction runner hashes.
  That run is not a clean broad pass for the current working tree.
- Current model runs and many associated artifacts are uncommitted. Earlier
  verification does not cover later changes or the final six-model panel.

## Data and claim boundaries

- **Gan 2026 `test450`:** locked holdout. During the 2026-07-15 documentation
  consolidation, a command unintentionally printed part of a sealed aggregate
  Markdown row table. No row was analyzed or used to change the model, prompt,
  repair policy, or scorer, but the stronger claim that no test row was ever
  exposed is no longer available. Only aggregate results may be cited.
- **ExECTv2 `dev140`:** row review is permitted for development.
- **ExECTv2 `test60`:** held out; do not inspect rows during development.
  `full200` mixes development and held-out rows and is not an independent
  holdout.
- **Scores:** Gan uses Purist and Pragmatic label accuracy. ExECT's primary
  internal score is de-duplicated clinical fact recovery (`clinical_headline`).
  It is not the published ExECT benchmark; phrase, CUI, evidence-valid, and
  full-attribute views remain separate.
- Independent clinical review remains required before making clinical-validity
  claims from the internal annotation review.

## Selected established results

- Gan locked test450: the single-pass event extractor scored `364/450` Purist;
  the saved three-pass comparator scored `379/450`. The 15-row gain is a
  quality-versus-model-pass result. Matched token, cost, latency, hardware, and
  cache telemetry was not retained.
- ExECT rules-only no-call dev140: macro item F1 is `0.5687` for normalized
  phrase, `0.7144` for CUI, and `0.6020` for all features across nine entity
  types. This is development evidence, not reproduction of the original ExECT
  system or its reported validation scores.
- Historical ExECT full200 model rows do not meet the final family boundary:
  Prescription was deterministic-only and Seizure Frequency included an
  independent extractor union. They remain audit evidence, not final model
  comparison results.
- Frozen aggregate-only test60 replay found model-reported confidence
  uninformative for review routing across the three historical outputs; no
  confidence-based review policy was adopted.

Exact selected files, hashes, versions, and replay requirements are in the
[retained evidence index](docs/experiments/retained_evidence_manifest.md).
[Paper claim status](docs/canon/10_paper_provenance.md) owns what the manuscript
may say.

## Active work

1. Freeze the completed hosted ExECT and Gan panels in the retained-evidence
   index without inspecting held-out rows.
2. Predeclare one matched Gan test450 protocol that pins prompt
   `gan2026_hybrid_structured_events_v0.7`, its rendered snapshot hash, the
   current pipeline and repair/scoring hashes, one call per note, disabled
   cache, aggregate-only readout, model routes, token limits, and permitted
   format-only adapters. Make prompt selection explicit in the runner before
   any call.
3. Retain the completed Luna and Sol v0.7 runs. Run fresh v0.7 conditions for
   GPT-4.1-mini and thinking-enabled DeepSeek V4 Flash on the final hosted
   routes and current pipeline after model-specific validation pilots pass.
4. Run Qwen 3.6:35B and Gemma 4 26B on the same Gan v0.7 condition, alongside
   their ExECTv2 work, sequentially through native Ollama. Record exact tag
   digests, Q4_K_M quantization, context, thinking policy, endpoint, hardware
   and observed partial-offload state. Qwen uses `think=false`; Gemma's adapter
   policy must be confirmed before its frozen pilot.
5. Freeze and verify the six-model Gan panel before making a matched comparison
   claim. Keep provider-required temperature and transport differences visible.

The [active roadmap](docs/plans/ACTIVE_ROADMAP.md) owns the detailed work order.

## Blocked or unvalidated

- The six-model development comparison remains incomplete until DeepSeek, Qwen,
  and Gemma have final artifacts and the common-panel checks pass. This blocks
  a complete six-model comparison, not the already frozen hosted test60 and Gan
  test450 runs.
- Hosted ExECT test60 and Gan Luna/Sol test450 calls are complete. The long
  local ExECT Qwen and Gemma conditions remain unstarted.
- The matched Gan panel remains incomplete until fresh GPT-4.1-mini, DeepSeek,
  Qwen and Gemma v0.7 conditions complete under the current pipeline. The
  protocol decision is made, but the dated predeclaration and runner freeze
  must exist before new holdout calls.
- The retained-evidence freeze and clean broad verification remain stale until
  the completed hosted artifacts are indexed and contaminated artifacts are
  excluded.

## Known defects and risks

- Existing Gan reports describe test450 output as a validation development
  result. Correct the report wording and regenerate aggregate summaries without
  exposing rows; this reporting defect does not require repeating Luna or Sol.
- Gan prompt v0.7 was developed from DeepSeek-reasoner validation failures. A
  matched v0.7 panel removes prompt and pipeline mismatch but is not a
  model-neutral capability ranking. Test450 has also supported sequential
  aggregate evaluations, and part of one row report was accidentally exposed;
  report the result as a matched aggregate-only panel, not a pristine one-shot
  holdout comparison.
- The rejected first six-model attempt used the first 140 sorted letters; only
  94 were manifest dev IDs. Its outputs are contaminated development artifacts:
  never resume, score as panel evidence, or add them to the retained-evidence
  index. Replacement `single_call` paths and resume validation prevent reuse.
- The working tree contains active source, configuration, document, and
  experiment changes. Do not describe these changes as committed, released, or
  covered by the earlier clean-checkout verification.
- The selected joint policy retains three deterministic regressions, and the
  one-call Diagnosis decision accepts a measured development-quality loss.
  Keep both limitations visible in comparisons and paper claims.
- Gan test450 row text was unintentionally exposed while reading a generated
  aggregate Markdown report during documentation consolidation. Treat the
  hosted results as frozen aggregate evidence only; do not perform follow-up
  row analysis or tuning from the exposure.

Use *implemented*, *verified*, *validated*, and *promoted* precisely.
