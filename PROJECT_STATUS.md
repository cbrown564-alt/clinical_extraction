# Project status

Last updated: 2026-07-18

## Current outcome

The repository cleanup, engineering repair, selected-evidence replay, paper
build, Gan efficiency audit, ExECT published-metric development, and ExECT
component-policy studies are complete. The six-model ExECTv2 `dev140` artifacts
and six-model Gan `test450` aggregate artifacts are now present. The ExECT
`test60` aggregate panel remains the four hosted conditions. The maintained
status, retained-evidence index, and per-run summaries still need reconciliation
before these newer panels are promoted as canonical report evidence.

[Decision 0040](docs/decisions/0040-final-exect-llm-with-rules-family-ownership.md)
owns the final model-led family boundary and selected joint bounded policy.
[Decision 0041](docs/decisions/0041-single-call-exect-model-comparison.md)
owns the single structured call per letter. This is an accepted quality and
resource-policy tradeoff, not measured cost or latency evidence.
[Decision 0043](docs/decisions/0043-gan-hosted-comparison-uses-v05-prompt.md)
selects prompt v0.5 as the shared default for the next four-model hosted Gan
comparison. The dated protocol, v0.5 fingerprint, reconciliation, pilots, and
execution amendment are owned by
`docs/experiments/gan2026/gan2026_matched_v05_test450_protocol_2026-07-16.md`.

The clean decision-0041 ExECT panel is complete on `dev140` for GPT-4.1-mini,
GPT-5.6 Luna, GPT-5.6 Sol, thinking-enabled DeepSeek V4 Flash, Qwen 3.6:35B,
and Gemma 4 26B. The frozen aggregate-only `test60` panel contains the four
hosted conditions, each completing 59/59 letters with zero call or blocking
parse failures. The Gan `test450` v0.7 panel now has six aggregate conditions:
the four hosted models plus Qwen 3.6:35B and Gemma 4 26B.

## Fresh evidence

- A two-row Gemma 4 26B ExECTv2 dev140 context probe isolated one
  context-sensitive Ollama early stop. EA0135 reproduced truncated JSON at
  32,768 context after only 303 completion tokens and 14,141 total tokens, but
  both residual rows parsed cleanly at 65,536 context. Gemma ExECT now declares
  65,536 context with sequential single-call execution; the diagnostic does not
  replace or rescore the completed full-run artifact. The
  [protocol and result](docs/experiments/exectv2/reliability/exectv2_gemma4_context_probe_dev140_protocol_2026-07-17.md)
  owns the interpretation and links to the machine-readable telemetry.
- The six current ExECT `dev140` single-call artifacts range from `0.8016` to
  `0.8920` `clinical_headline` F1. Exact evidence is `1.0` after assembly for
  every model; Gemma has six recorded parse/schema events and the other five
  have none. These are development comparison artifacts and their maintained
  summaries are not yet reconciled.
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
- On the matched locked Gan test450 panel under current prompt v0.7, Sol scored
  `358/450` Purist and `376/450` Pragmatic, GPT-4.1-mini `353/450` and
  `371/450`, Luna `352/450` and `365/450`, and thinking DeepSeek `342/450` and
  `362/450`. All had zero call failures; parse/schema/label issues were 0, 2,
  3, and 4 respectively. This is aggregate-only same-prompt evidence with
  provider-route caveats, not a pristine one-shot or model-neutral ranking.
- The local Gan `test450` aggregates add Qwen at `367/450` Purist and `380/450`
  Pragmatic, and Gemma at `343/450` and `367/450`, under the same v0.7 prompt,
  `hybrid_full_stack` repair policy, and scorer. Their exact-evidence counts are
  `363/450` and `437/450`; the aggregate files record no final parse/schema/
  label issues after deterministic repair. The six-model report remains an
  aggregate-only result and needs retained-evidence reconciliation.
- The restored v0.5 snapshot is 3,716 bytes with SHA-256
  `77a5575244423f989b247ff1e89930c081c0e91a3b19e0ad74687bf40eb90993`.
  The retained GPT-4.1-mini artifact's 450/450 prompt payloads match it, but
  current non-prompt replay changes 15 final labels and shifts the no-call
  aggregate from 364/381 to 366/383; GPT therefore required a fresh run.
- All four v0.5 five-record operational pilots passed: 5/5 calls, structured
  records, zero blocking parse/schema/label failures, and exact evidence.
  Fresh v0.5 GPT-4.1-mini scored `361/450` Purist and `379/450` Pragmatic;
  Luna scored `362/450` and `375/450`. Both had zero call failures. The
  aggregate artifact and sealed fingerprints are in
  `experiments/gan2026_matched_v05_test450_aggregate_20260716.json`.
- Sol and DeepSeek v0.5 holdout artifacts stopped at 350/450 and 150/450 after
  the one-hour controller timeout. They are rejected operational diagnostics,
  not scores, and were not resumed.
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
- The v0.5 prompt and transport changes passed 26 focused prompt/contract tests,
  the v0.5 runner tests, Ruff, and targeted mypy. No clean broad verification
  covers the final working tree or the incomplete v0.5 panel.
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

1. Reconcile and freeze the completed six-model ExECT `dev140` and Gan `test450`
   artifacts in the retained-evidence index without inspecting held-out rows.
2. Preserve the four hosted ExECT `test60` aggregate-only panel as the current
   holdout comparison; no local test60 conditions are currently recorded.
3. Build the requested 3–4 page six-model comparison report. Scale the existing
   six-dimension reliability scorecard across the additional models added since
   the original reports were built, then decide whether ExECT needs ten-dimension
   scorecard infrastructure and a corresponding report. Both are targets, not
   completed scorecard work.

The [active roadmap](docs/plans/ACTIVE_ROADMAP.md) owns the detailed work order.

## Blocked or unvalidated

- The six-model ExECT `dev140` and Gan `test450` artifacts are present, but the
  retained-evidence index, common-panel checks, and canonical summaries have
  not yet been updated for them.
- ExECT `test60` remains a four-hosted-model aggregate-only panel. Gan `test450`
  is aggregate-only and must not be used for row-level tuning or failure review.
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
- The retained GPT-4.1-mini `364/450` artifact uses prompt v0.5 but predates the
  current matched runner and failed the required non-prompt reconciliation. Do
  not combine it with the fresh v0.5 results.
- Sol's v0.5 transport pilot initially sent an unsupported temperature field
  because the runner patched `llm_config` after the pipeline imported the
  builder. The wrapper now patches the pipeline module directly; the corrected
  pilot passed. The final Sol condition still timed out operationally.
- The combined v0.5 controller timed out after one hour with Sol and DeepSeek
  incomplete. Their partial artifacts must not be resumed, scored, or added to
  retained evidence without a new protocol.
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
