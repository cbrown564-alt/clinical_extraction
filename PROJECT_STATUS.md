# Project Status

Last updated: 2026-06-01

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that can reach at least
0.9000 Purist F1 on development surfaces while preserving transparent evidence
trails, component-level ablations, and conservative benchmark language.

## Current Strategy

Use Gan 2026 as the first controlled extraction surface. Keep data loading,
label normalization, scoring, split discipline, and deterministic-rule behavior
explicit before optimizing LLM or DSPy components.

Deterministic V1 is frozen as a controlled comparator, not an expanding solution.
New candidate work should stay LLM-first: model extraction and clinical
selection produce the prediction-bearing interpretation; deterministic code is
limited to schema validation, evidence validation, Gan-compatible normalization,
strict benchmark-format repair, arithmetic repair, and explicitly ablated named
modules.

## Recent Context

- Locked split `gan2026_split_v1`: 300 train, 750 validation, 450 final holdout;
  LLM/DSPy work escalates 25 -> 50 -> 250 validation rows.
- Deterministic V1 is a frozen comparator: 0.9293/0.9387 validation
  Purist/Pragmatic, but 0.7600/0.7867 on its one locked-test evaluation.
- Structured v0.5 reached 675/750 Purist = 0.9000 on full validation, but audit
  classified it as repair-heavy hybrid behavior, not clean LLM-first completion.
- Clean claim language now treats raw LLM final-label selection as the
  attribution baseline. Only strict format-preserving benchmark normalization
  belongs on the clean LLM-first path; selected-evidence repair, diary
  arithmetic, cluster conversion, and clinical-selection overrides are named
  deterministic modules.
- Completed `gan2026_clean_attribution_format50_v0` as a no-call 50-row diagnostic: raw 34/50 Purist (0.6800), strict format-only 41/50 (0.8200), 17 surface repairs, 7 improvements, 0 regressions, 50/50 exact evidence, and 3 strict parse failures (2 cluster-only plus `most weekdays`).
- Gold-normalization policy is now separated from strict format repair and named
  semantic modules. The first tested clean scorer-facing slice covers
  cluster-name stripping, vague weekday cadence, and Gan-specific `bimonthly`;
  broader policy families remain documented but not implemented.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`, `docs/design/data_contract.md`
- Framing/policy: `docs/research/contribution_thesis.md`,
  `docs/research/gan2026_gold_normalization_policy_question_2026-06-01.md`
- Core code: `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_structured.py`;
  observatory: `notebooks/gan2026_living_observatory.ipynb`
- Current artifacts: `experiments/gan2026_clean_attribution_format50_v0_2026-06-01.md`,
  `experiments/gan2026_llm_structured_decision_retrospective_2026-06-01.md`

## Active Priorities

1. Keep deterministic V1 frozen and put new deterministic behavior into named,
   ablated candidates.
2. Enforce the architecture gate before the metric gate; semantic-state-changing
   repair needs separate naming, ablation, and claim language.
3. Use `gan2026_clean_attribution_format50_v0` before promoting semantic repair,
   selector guidance, or a new architecture family.
4. Separate benchmark gold-normalization policy from clinical reasoning:
   preserve source-near traces, but match Gan scoring conventions when they are
   explicit and consistent.
5. Maintain conservative benchmark language; the test split has been touched
   once and must not become a tuning surface.

## Work Board

### Now

- Keep clean scorer-facing normalization separate from named deterministic
  modules in run attribution and claim language.
- Use the new clean scorer-facing policy flag in a no-call replay or small
  validation run before promoting any additional policy families.
- Build direct-citation row tables before implementing any new policy family.

### Next

- Compare v0.2 and v0.4 error families before broader selector guidance.
- If useful, run a focused 25- or 50-row comparison for the selected next
  architecture before any 250-row escalation.

### Blocked

- Final benchmark-comparison language is blocked until the replication surface
  and paper comparability are explicit.
- Further holdout analysis is blocked by locked-test discipline; do not inspect
  test-row failures during candidate development.

### Done Recently

- 2026-06-01: Added staged structured LLM extraction, repair-family attribution
  audit, strict format-only clean replay, and the living observatory notebook.
- 2026-06-01: Settled and implemented the first tested clean scorer-facing
  gold-policy slice while preserving separate structured-run attribution.

## Immediate Next Step

Run a no-call clean-policy replay or focused validation comparison, then only
add more scorer-facing policy families after direct-citation row tables confirm
consistent Gan annotation behavior.
