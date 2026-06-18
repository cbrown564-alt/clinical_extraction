# Gan 2026 ACD Projection Policy Predeclaration

Date: 2026-06-04

Purpose: predeclare the production state-graph projection policies derived from
ACD-003 through ACD-010 before any broad validation or holdout-facing claim.
These policies address validation-development rows whose first failure owner was
`projection_policy`; they do not change the split protocol or create a benchmark
claim.

Source decisions:

- ACD-003: vague count adjectives with a denominator project to the matching
  `multiple per <denominator>` bucket; vague count adjectives without a calendar
  denominator project to `unknown`.
- ACD-004: conditional-only trigger statements without cadence project to
  `unknown`.
- ACD-005: relative-only trends without absolute current rate project to
  `unknown`.
- ACD-006: diary date listings project by summing listed events and normalizing
  to the covered calendar span.
- ACD-007: explicit no-definite-seizure events with non-epileptic triage project
  to a seizure-free month bucket.
- ACD-008: explicit current qualitative summary rates override derived
  long-period averages.
- ACD-009: previous-month active burden overrides a short current-month-to-date
  zero count unless a longer seizure-free state is explicitly established.
- ACD-010: recent major-semiology relapse takes priority over lower-severity
  interictal rates.

Implementation scope:

- Production state graph construction may emit named `projection_policy.acd_*`
  nodes only for the predeclared source patterns above.
- Production projection may assign ACD-specific rationale and priority only from
  exact graph nodes and preserved evidence text.
- These rules are categorized as `benchmark_format` projection policy: they
  render source-near clinical facts into Gan-compatible labels and must remain
  ablatable from candidate generation and evidence selection claims.

Test contract:

- `tests/test_gan2026_state_graph.py` contains one focused test per ACD-003
  through ACD-010 policy.
- The tests use small source-near fixtures, not broad validation sweeps.
- Any future broad validation or frozen-test use must cite these gates as
  predeclared development policy and still report deterministic-correct
  regression accounting.
