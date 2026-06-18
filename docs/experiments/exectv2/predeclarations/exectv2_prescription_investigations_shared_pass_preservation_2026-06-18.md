# ExECTv2 Prescription/Investigations Shared-Pass Preservation

Date: 2026-06-18
Status: decision note; no new route authorized

## Decision

Preserve Prescription and Investigations on the shared broad all-entities pass
for the current family-routed LLM-first comparison.

The current routed adapter keeps `Prescription`, `Investigations`, and
`Diagnosis` from
`experiments/exectv2_llm_only_all_entities_dev140_gpt41mini_20260612.jsonl`,
then replaces only `SeizureFrequency` with the routed event/state artifact. The
adapter records `prescription_investigations_route_policy:
shared_broad_pass_only`, and the routed report shows zero P/I movement versus
the single-pass baseline:

| Family | Single-pass F1 | Routed F1 | Delta |
| --- | ---: | ---: | ---: |
| Prescription | `0.7472` | `0.7472` | `+0.0000` |
| Investigations | `0.7475` | `0.7475` | `+0.0000` |

The separate verifier reports remain useful candidates, but they are not a
fresh predeclared replacement of the shared P/I pass inside the family-routed
architecture:

- Combined medication/investigations verifier v0.1 improved Prescription
  `0.777 -> 0.817`, but regressed Investigations `0.786 -> 0.496`.
- Dedicated Investigations verifier v0.1 improved Investigations
  `0.786 -> 0.872`.
- No current predeclaration found in this checkout authorizes swapping either
  verifier into the routed P/I slots and replaying the same routed comparison.

Therefore the routed architecture should not promote the specialist P/I
artifacts by implication. They require a separate, dev-only, no-call ablation
before they can replace the shared broad pass.

## Future Ablation Preflight

Before any future P/I replacement route is introduced, write a new
predeclaration that names the exact artifacts, ownership label, and gate. The
minimum preflight checks should be:

- split is dev-only (`pilot25 -> dev140` allowed); full-200/test and Gan holdout
  surfaces remain blocked;
- replay is no-call: all P/I, Diagnosis, and SF source artifacts already exist
  locally before the runner starts;
- baseline is the current shared-pass family-routed comparison on the same
  four-family surface;
- candidate replacement improves the intended routed aggregate and has no
  family-level F1 regression for Prescription, Investigations, Diagnosis, or
  SeizureFrequency;
- exact-evidence rate is preserved at the predeclared gate, and call/parse
  failures are zero or explicitly counted as gate failures;
- ownership is downgraded or renamed if a verifier/adjudicator contributes
  prediction-bearing clinical selection beyond the shared LLM pass;
- the report keeps specialist-verifier gains separate from deterministic CUI,
  certainty, evidence, and benchmark-format projection gains.

Until those checks are predeclared and passed, the preservation policy remains
`shared_broad_pass_only`.
