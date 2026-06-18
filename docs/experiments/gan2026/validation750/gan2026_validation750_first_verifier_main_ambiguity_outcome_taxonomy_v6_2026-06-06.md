# Gan 2026 Validation750 First Verifier Main-Ambiguity Outcome Taxonomy V6

Date: 2026-06-06

Scope: taxonomize the `29` rows in the first verifier main ambiguity score
table from
``.

This is a validation-development failure-mode read only. It does not authorize
replacement labels, locked-test inspection, or benchmark-comparable claims.

## Purpose

The main ambiguity table is the first real verifier target surface. The goal of
this note is to convert the row-by-row action outputs into a durable failure
taxonomy that can guide the next verifier prompt/policy iteration.

## Top-Line Action Split

| Action | Rows |
| --- | ---: |
| `affirm` | `1` |
| `reject` | `5` |
| `human_review` | `15` |
| `abstain` | `8` |

## Primary Taxonomy

### 1. `affirm`: single dominant explicit burden despite route noise

Rows: `5791`

Interpretation:

- The note contains a direct, recent, clinically coherent burden statement.
- Route noise remains visible, but the evidence still supports a clear
  action-bearing read.
- This is the only row where the action-only verifier judged the ambiguity
  surface affirmable without human escalation.

Operational lesson:

- `affirm` should stay rare and should require a clearly dominant primary fact
  rather than merely a highest-frequency candidate.

### 2. `reject`: contradiction between active burden and seizure-free/no-event state

Rows: `12537, 12548, 12556, 12573, 12749`

Subfamilies:

| Subfamily | Rows | Why `reject` fits |
| --- | ---: | --- |
| `active_burden_vs_recent_no_events_conflict` | `12537, 12548, 12556, 12573` | Ongoing daily/weekly burden conflicts with a competing no-events or seizure-free state strongly enough that the proposed interpretation should not be affirmed. |
| `direct_competing_current_facts` | `12749` | A no-seizures statement and a precise high-frequency current burden co-exist as direct rivals, creating a contradiction too strong for abstain-only handling. |

Interpretation:

- `reject` is not just "messy multi-semiology." It appears when the packet
  contains evidence that actively undermines the proposed interpretation.
- The decisive pattern is contradiction, not merely incompleteness.

Operational lesson:

- Reserve `reject` for rows where a proposed frequency interpretation is
  positively contradicted by competing current evidence, especially recent
  seizure-free or no-event claims.

### 3. `human_review`: real ambiguity after a clinically plausible read exists

Rows:
`5551, 6889, 12192, 12366, 12456, 12484, 12502, 12506, 12551, 12562, 12584, 12641, 12676, 12679, 12751`

Subfamilies:

| Subfamily | Rows | Why `human_review` fits |
| --- | ---: | --- |
| `mixed_window_multi_semiology_without_clean_contradiction` | `5551, 6889, 12192, 12366, 12456, 12502, 12506, 12641, 12676, 12679, 12751` | Multiple current burdens exist, but they span different windows or seizure types and do not collapse into one clean action automatically. |
| `mixed_burden_plus_boundary_context` | `12484, 12551, 12562, 12584` | Mixed burdens coexist with seizure-free or no-events context that complicates interpretation but does not cleanly invalidate the proposed state. |

Interpretation:

- `human_review` is the dominant action because the main ambiguity surface is
  mostly not about parser failure. It is about clinically plausible but
  unresolved burden competition.
- The repeated pattern is additive or competing current evidence across
  different time windows, semiologies, or contextual boundary statements.

Operational lesson:

- The next verifier iteration should sharpen when competing burdens are strong
  enough for `reject` versus when they remain true review debt.
- If the row contains several valid current burdens but no decisive
  contradiction, `human_review` is the stable default.

### 4. `abstain`: known unresolved policy/aggregation surface with no safe action move

Rows: `6209, 12127, 12236, 12378, 12403, 12422, 12460, 12823`

Interpretation:

- These rows look structurally ambiguous in a way the verifier can recognize
  but not safely resolve.
- The dominant patterns are mixed-window additive burden, incomplete
  normalization, and exact-trace weakness without a clear contradiction.
- Unlike the `human_review` rows, these tend to lack a verifier-justified move
  toward either contradiction-driven `reject` or a plausible-but-escalated
  clinical selection.

Operational lesson:

- `abstain` remains appropriate for policy-known unresolved mixed-window cases
  where the verifier can explain the ambiguity but should not choose among
  competing burdens.

## What Separates The Actions

| Action | Practical rule emerging from this run |
| --- | --- |
| `affirm` | One dominant explicit burden survives the route noise. |
| `reject` | Competing evidence actively contradicts the proposed interpretation. |
| `human_review` | Several clinically plausible current burdens remain, but contradiction is not decisive. |
| `abstain` | The verifier recognizes unresolved policy/aggregation debt and should not act beyond naming it. |

## Comparison To Forced Choice

The forced-choice verifier agreed with the action-only run on only `5 / 29`
main-table rows:

- `5791`
- `6889`
- `12366`
- `12679`
- `12749`

The main disagreement pattern is informative:

- forced choice collapses many `abstain` and `human_review` rows into
  frequency-dominance `affirm`
- action-only preserves the distinction between
  contradiction,
  clinically plausible review debt,
  and policy-known unresolved aggregation

This is evidence that the action-only protocol better matches the reset goal of
making verifier behavior explicit and conservative on the true ambiguity
surface.

## Recommended Next Prompt/Policy Tightening

1. State explicitly that "highest current frequency" is not enough for
   `affirm` when mixed windows or competing current burdens remain unresolved.
2. State explicitly that `reject` requires contradiction, not just multiplicity.
3. Bias mixed-window additive burden toward `human_review` or `abstain`
   depending on whether a clinically plausible but non-decisive read exists.
4. Keep the `29`-row ambiguity table as the only primary tuning surface for the
   next verifier iteration.

## Decision Summary

The `29`-row main ambiguity table is not one failure family. It contains four
distinct action regimes:

1. a tiny `affirm` surface with one dominant explicit burden
2. a contradiction-driven `reject` surface
3. a large clinically plausible but unresolved `human_review` surface
4. a policy-known unresolved `abstain` surface

That taxonomy should govern the next verifier prompt/policy revision.
