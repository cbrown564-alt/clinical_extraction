> **Superseded for navigation —** canonical summary: [`VALIDATION750_CANON.md`](../VALIDATION750_CANON.md). Full detail retained below.

# Gan 2026 Validation750 GPT-4.1-mini Verifier Read

Date: 2026-06-06

This is a mechanics read over validation750 using the existing
CandidateSet v3 nested-dedupe artifact and GPT-4.1-mini clinical-assessment
probe. It is not a locked-test run and does not make a benchmark-comparable
promotion claim.

## Source Artifacts

- Candidate set:
  `experiments/gan2026_validation750_candidate_set_v3_nested_dedupe_2026-06-06.jsonl`
- Clinical assessment:
  `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation750_gpt41mini_v3nested_v3_2026-06-06.jsonl`
- Projection/render:
  `experiments/gan2026_clinical_assessment_projection_render_validation750_gpt41mini_v0_2026-06-06.jsonl`
- Score-policy audit:
  `experiments/gan2026_clinical_assessment_projection_score_validation750_gpt41mini_v0_2026-06-06.jsonl`
- Verification route:
  `experiments/gan2026_validation750_verification_route_gpt41mini_v0_2026-06-06.jsonl`
- VerificationDecision V0:
  `experiments/gan2026_validation750_verification_decision_gpt41mini_v0_2026-06-06.jsonl`

## Clinical-Assessment Read

- Rows: 750
- Valid clinical assessments: 732
- Call failures: 0
- Parse/validation failures: 18
- Missing candidate-set rows: 0

The 18 invalid assessment rows are role-id hygiene failures, not API failures:

- duplicate ids within a role: 13
- primary/supporting overlap: 3
- supporting/rejected overlap: 2

This suggests the next quick implementation iteration should either strengthen
the prompt around mutually exclusive candidate roles or add a deterministic
role-id dedupe/precedence repair before strict `ClinicalAssessment` assembly.

## Projection/Render Read

- Projection rows: 732
- Rendered-label rows: 498
- Null-rendered rows: 234
- Row-issue rows: 18

Projection kinds:

- `frequency_rate`: 412
- `seizure_free`: 141
- `cluster_frequency`: 82
- `unknown_frequency`: 71
- `no_reference`: 25
- `unresolved_multiple`: 1

Largest non-id issue families:

- `projection_semantics_missing`: 234
- `vague_count`: 127
- `seizure_free_duration_required`: 114
- `frequency_rate_operands_incomplete`: 101
- `frequency_rate_operands_unparsed`: 81
- `seizure_free_duration_unparsed`: 35
- `additive_frequency_period_mismatch`: 23

## Score-Policy Audit

The score artifact is audit-only over rendered rows.

- Scored rows: 498
- Non-scored rows: 252
- Purist correct on scored rows: 427 / 498 = 0.8574
- Pragmatic correct on scored rows: 456 / 498 = 0.9157
- Exact normalized-label matches on scored rows: 372 / 498 = 0.747
- Non-scored issue: `rendered_label_null` on 252 rows

## Automated Verifier Baseline

Verification route V0 routed 42 / 750 rows. All routed rows came from the
null-rendered surface.

Route-family counts:

- `mixed_window_or_vague_addition`: 24
- `cluster_axis_ambiguity`: 12
- `cyclic_window_without_event_count`: 5
- `seizure_free_proxy_evidence_overreach`: 1

VerificationDecision V0 emitted:

- `abstain`: 42
- `human_review`: 0
- `affirm`: 0
- `reject`: 0

Action basis:

- `route_family_policy`: 42

## Interpretation Before LLM Verifier Work

The automated verifier currently behaves as a conservative unresolved-risk
surface. On this GPT-4.1-mini validation750 pass, it does not affirm or reject
any routed row; it only abstains over null-rendered route families. That makes
the first LLM-verifier comparison clean: evaluate whether an LLM verifier can
produce evidence-grounded `affirm`, `reject`, `abstain`, or `human_review`
actions over these 42 routed rows without inventing replacement scorer-facing
labels.

The main pre-verifier implementation opportunity is upstream schema hygiene:
18 rows failed strict assessment assembly because candidate ids were duplicated
or assigned to overlapping roles. Fixing that should increase the projection
surface without changing verifier/action policy.
