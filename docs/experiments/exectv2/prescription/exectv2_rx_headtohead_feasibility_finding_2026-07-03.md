# Section C feasibility finding — deterministic Prescription producer already wins

Date: 2026-07-03. Owner: ExECTv2 workstream.
Hypotheses: `rx_llm_producer_into_v08_2026-07-03`, `rx_deterministic_rule_harden_2026-07-03`.
Status: **both hypotheses REFUTED by the feasibility probe; C2/C3 cancelled.**

## The finding

The planned Section C head-to-head (LLM producer vs hardened deterministic
producer, then holdout eval of the winner) was predicated on the assumption
that the v08 deterministic Prescription producer *drops* the recall gains the
two confirmed LLM probes recovered (EA0038 carbamazepine doses, EA0021 nocte
split). A free scorer-replay feasibility probe on the cached deterministic
artifact refutes this premise decisively.

**The deterministic producer already emits every fact the probes were
chasing**, and scores higher than every LLM arm:

| Producer (dev140 Rx `clinical_headline`) | F1 | P | R | tp/fp/fn |
| --- | ---: | ---: | ---: | --- |
| **v08 deterministic (P7-fixed, current)** | **0.9615** | 0.9524 | 0.9709 | 200/10/6 |
| LLM probe #2+#3 combined arm | 0.9526 | 0.9795 | 0.9272 | 191/4/15 |
| LLM probe #2 (current-vs-future) | 0.9395 | 0.9372 | 0.9417 | 194/13/12 |
| LLM probe #3 (AED-only) | 0.9350 | 0.9639 | 0.9078 | 187/7/19 |
| GEPA LLM canonical (the probe baseline) | 0.9122 | — | — | — |
| Fresh matched LLM baseline | 0.9073 | 0.9118 | 0.9029 | 186/18/20 |

The deterministic producer's 0.9615 carries through the v08 assembly unchanged
(the Prescription lens is a passthrough): the P7-treatment assembly's Rx
component is also 0.9615 (overall 0.9189).

## Why the probes looked like wins

The two probes compared the LLM *against itself* — a fresh matched LLM
baseline (0.9073) → probe LLM arm (0.9395 / 0.9350 / 0.9526). The gains were
real *relative to that weak LLM baseline*, but the comparison never included
the deterministic producer that v08 actually uses. The LLM's "recall gains"
(EA0038 carbamazepine, EA0021 nocte split) were facts the deterministic
extractor already captures structurally via its AED-only `_MEDICATION_PATTERN`
lexicon + per-clause current-vs-future gating (the same machinery the probes
re-encoded as English instructions).

## Conclusion

- **No LLM Prescription producer should be introduced into v08.** Doing so
  would *lower* the Rx component from 0.9615 to at best 0.9526 (a -0.0089
  regression), at real LLM cost, while adding architectural complexity to the
  manuscript's architecture-of-record.
- **No deterministic rule hardening is needed.** The producer already emits
  the target facts; there is nothing to recover.
- **The head-to-head (C2) and holdout eval (C3) are cancelled** — there is no
  competitor that can beat the deterministic producer, so no comparison to run.
  This saves ~760 planned LLM calls (C2 ~560 + C3 ~200).

## What this confirms about the audit

This reinforces the 07-02 pipeline-assumption-audit's Prescription finding
rather than challenging it. Prescription is the one family where model error
genuinely dominates (72.2% of disagreements under the finalized scorer). The
deterministic producer's 0.9615 is strong *because* it sidesteps the LLM's
failure modes (current-vs-future conflation, non-AED over-extraction)
structurally — which is exactly why the hybrid architecture uses a deterministic
Prescription lane. The probes' value was diagnostic: they confirmed *which*
LLM behaviors were broken, informing the audit's mechanism map, even though
the production path doesn't need them.

## Provenance

- Feasibility probe: `run_all9_on_letters(dev140)` → `score_prescription_components` (this file).
- v08 assembly Rx: `exectv2_holistic_finding_assembly_v08_dev140_p7_treatment_20260702.json`
  (`score_ladder.headline_target.by_indicator.Prescription.f1 = 0.9615`).
- LLM probe numbers: `docs/experiments/exectv2/prescription/exectv2_rx_extraction_probes_2026-07-02.md`.
