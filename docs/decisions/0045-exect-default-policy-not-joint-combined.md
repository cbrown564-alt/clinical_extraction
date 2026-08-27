# 0045: ExECT comparison uses default Diagnosis/Prescription policy

Date: 2026-07-31  
Status: accepted  
Supersedes: the disclosed-fallback selection of
`decision_0040_joint_bounded_dev140_v1` in
[decision 0040](0040-final-exect-llm-with-rules-family-ownership.md)  
Amends: [decision 0041](0041-single-call-exect-model-comparison.md) assembly-policy wording

## Decision

The active ExECTv2 comparison and prompt-variant studies use Diagnosis and
Prescription policy variants **`default` / `default`**.

The joint bounded policy (`combined` / `combined`, identifier
`decision_0040_joint_bounded_dev140_v1`) is **demoted to archived development
evidence**. It must not be the default assembly setting for new runs, Luna
prompt comparisons, six-model tables, or paper-facing ExECT cells.

## Why

A matched six-model no-call reassembly (2026-07-31) showed that joint raises
overall `clinical_headline` F1 for every model on `dev140` and aggregate-only
`test60` (roughly `+0.01` to `+0.02` overall) without changing rank order.
Seizure Frequency and Investigations are unchanged. The retained six-model
panel hashes were already assembled under `default` / `default`.

The user rejects carrying joint as the active comparison policy: the score
gain is marginal relative to the extra Diagnosis/Prescription guard complexity
and the risk of documenting one policy while scoring another. This matches the
resource-tradeoff pattern already accepted in decision 0041 (small F1 change
does not justify a second model call).

## What remains true from 0040 / 0041

- Model-led family ownership (decision 0040) is unchanged.
- One structured call per letter (decision 0041) is unchanged.
- Joint bounded replay results remain valid **historical** development
  evidence: findable under the archive index, reproducible with an explicit
  opt-in, not deleted.

## Consequences

- Active ExECT configs, Luna A/B/C comparisons, and canon score tables cite
  `default` / `default` and the retained default-panel numbers.
- Runners for active studies must reject `combined` unless an archived-replay
  flag or archived config is used.
- Navigation and status documents must not present joint as the selected live
  comparison policy.
- Do not retune joint guards to chase the marginal F1 lift.
- The research runner, operational wrapper, and local clinical-findings wrapper
  all use the same selected `default` / `default` policy. The pre-2026-08-01
  operational path that unconditionally enabled
  `diagnosis_resolution_candidate=True` is historical policy drift, not selected
  behavior that the canonical-orchestrator refactor must preserve.
- Any comparison with that older operational path is a development-only policy
  delta. It must be reported separately from structural parity and may be
  replayed only through an explicitly archived entry point.

## Evidence owners

- [Default-panel six-model comparison](../research/shared/six_model_comparison_report_2026-07-18.md)
- Historical joint-policy archive and selection records: recover from
  Git history. This decision is the living owner.
