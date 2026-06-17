# P0.6 — Safety-Property Table (fail-closed + research integrity)

Date: 2026-06-17  ·  Model calls: 0

| Property | Status | Layer | Evidence |
|---|---|---|---|
| No-regression safety floor (selective gated action) | code-enforced + documented | [comparator: hybrid-adjudicator] RQ6/rq9 selective intervention | RQ6 selective gated action: validation750 21 changed, 11 W->C, 0 C->W (precision 1.000); frozen test450 14 changed, 8 W->C, 0 C->W. The selective layer never converts a correct row to wrong. |
| Unconstrained replace mechanism DOES regress (why the floor matters) | recomputed | [comparator: V12-full-gpt4.1] reasoner final vs v0_reference | validation750: 147 changed, 42 W->C, 22 C->W; test450: 82 changed, 26 W->C, 13 C->W. The full replace path trades regressions for coverage, so the production go-forward is the un-replaced single-SE subject (the floor itself). |
| Abstain-to-unknown policy | code-enforced | subject + selective | SAFETY_GATE_VERSION = 'gan2026_fresh_evidence_safety_gate_v0_9' (fresh_evidence_reasoner.py:70); the gate withholds to unknown rather than emit an unsupported rate. |
| Contamination canaries + hash/version pinning | code-enforced | governance | frozen_test_preflight.py pins EXPECTED_SPLIT_MANIFEST='gan2026_split_v1', EXPECTED_TEST_ROW_COUNT=450, and verifies SHA-256 protocol hashes (_check_protocol_hashes) before any holdout run is permitted. |
| Aggregate-only readout guard (no row-level test inspection) | code-enforced | governance | frozen_test_readout.py refuses any report containing forbidden markers (source_row_index, transition_vs_v0, score_layers) and requires the aggregate-only marker + a 450-row count check. |
| Operational fail-closed integrity | recomputed elsewhere (P0.7) | subject | 0 parse failures / 0 evidence loss / source ids 1.000 across 2,295 rows. |

## Out of scope (stated finding)

**PHI-leakage and demographic-bias evals are N/A on this benchmark.** The Gan rows are synthetic templated letters with no real PHI and no reliable demographic signal, so jailbreak/PII/subgroup-demographic safety cannot be measured here. Clinical-family parity (P0.5) is the available fairness axis. Real-letter validation would be required before any deployment-grade PHI or demographic-fairness claim.

---

**Reading.** Safety here is fail-closed extraction + research integrity, and it is code-enforced rather than aspirational: the selective layer holds a 0 C→W floor while the unconstrained replace path measurably regresses, which is exactly why the simpler subject is the go-forward. The contamination canaries, hash pinning, and aggregate-only readout guard are what make every holdout number in this scorecard trustworthy.
