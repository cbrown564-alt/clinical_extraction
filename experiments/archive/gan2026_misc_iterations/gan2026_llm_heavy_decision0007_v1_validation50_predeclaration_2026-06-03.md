# Gan 2026 LLM-Heavy Decision 0007 v1 Validation50 Predeclaration

- Date: 2026-06-03
- Candidate: `llm_heavy_evidence_selection_with_deterministic_adapters`
- Prompt/program version: `gan2026_llm_heavy_evidence_selection_deterministic_adapters_v1`
- Split: `validation` / `gan2026_split_v1`
- Surface: first 50 validation rows
- Model: `openai/gpt-4.1-mini`
- Mode: live
- Claim language: validation development escalation, not a benchmark result.

## Rationale

The repaired matched validation25 smoke reached 25/25 raw parser-label Purist
and 25/25 mechanical-adapter Purist after narrow no-call repair of a malformed
selected-evidence `≤` copy. The next useful question is whether the LLM-owned
clinical selection and typed operand contract remains stable beyond the
saturated 25-row prefix.

## Stop Rule

Treat validation50 as promotable to a validation250 predeclaration only if:

- structured typed outputs are 50/50;
- call failures are 0/50;
- adapter parse failures are no more than 1/50;
- selected evidence exactness is at least 48/50 after source-checked
  nonsemantic evidence-copy repair;
- selected fact trace mismatches are 0/50;
- selected operand completeness is at least 48/50;
- raw parser-label Purist remains at least 47/50;
- mechanical adapter raw-correct to wrong is 0/50;
- mechanical adapter Purist remains at least 47/50.

## Inspection Policy

Inspect all rows with selected-evidence defects, raw parser-label misses,
mechanical adapter regressions, schema failures, or operand incompleteness.
Keep no-call repair replays separate from live evidence and name any new repair
family before using it to justify broader escalation.
