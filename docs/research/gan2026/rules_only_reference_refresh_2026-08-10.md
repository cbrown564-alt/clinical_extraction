# Gan 2026 Rules-Only Reference Refresh and Architecture Re-Freeze

Date: 2026-08-10
Status: executed
Trigger: [Gate A failure](rules_only_validation750_gate_a_2026-08-10.md)
Decision: user, 2026-08-10 — adopt the current portable ruleset and re-freeze
Model calls: zero

## What changed

The Gan rules-only reference cell pointed at a 2026-06-07 run whose extraction
depended on benchmark-specific shorthand (word numbers such as `TC nine/mo`,
separator prefixes such as `sz X7/mo`). Those variants were deliberately
retired on 2026-06-09 as overfitted to the Gan corpus. The comparator therefore
described extraction behaviour no longer present in the codebase.

The reference is now a fresh no-call run of the current portable ruleset.

| | Superseded (06-07) | Current (08-10) |
| --- | ---: | ---: |
| Run ID | `…deterministic_canonical_pipeline_gpt41mini_2026-06-07` | `gan2026_rules_only_canonical_validation750_20260810` |
| Purist of rendered | 688 / 741 | **673 / 741** |
| Pragmatic of rendered | 695 / 741 | **681 / 741** |
| Purist, all rows | 697 / 750 | **682 / 750** |
| Null rows (`unknown`) | 9 | 9 |
| Evidence-valid | 750 / 750 | 750 / 750 |

`rendered` in the rules lane means `final_label != "unknown"`. The LLM lanes use
a different convention (row produced a parseable `comparison` block), so Gan
figures must always name their denominator. Both of the previously recorded
figures were correct; they were not in conflict.

## Files changed

- `docs/experiments/retained_evidence_manifest.json` — `gan2026_rules_reference`
  repointed: new `run_id`, `result_summary`, `verification` block, artifacts,
  `prompt_program_version`, `claim_boundary`, and a `supersedes` entry.
- `docs/experiments/retained_evidence_manifest.md` — reference table row and
  freeze description.
- `experiments/registry.jsonl` — new run row; the 06-07 row marked
  `decision: superseded` with `superseded_by` set and a claim-language warning.
- `experiments/gan2026_rules_only_canonical_validation750_20260810.jsonl` — the
  new replay artifact (750 rows, validation split, row inspection permitted).
- `experiments/gan2026_rules_only_validation750_parity_20260810.json` — Gate A
  parity evidence.

## Re-freeze

`retained_comparison_architecture_20260720` →
**`retained_comparison_architecture_20260810`**, source commit
`c275151331cdf9f9fe482ab87a38c3301fef227c`.

The `mutation_policy` gained `deterministic extraction-ruleset` to its list of
changes requiring a new freeze ID. That was the gap the old freeze had: the
rules-only extraction modules are not covered by any `policy_files` role, so the
2026-06-09 rule rewrite mutated a frozen lane without tripping the freeze.

`policy_files` roles are a closed set (`dependency`, `model`, `prompt`,
`quality`, `repair`, `scorer`, `split`, `split_runbook`) and none honestly
describes an extraction rule module, so the ruleset is pinned indirectly by the
hash of the reference cell's replay artifact. `scripts/verify_reference_evidence.py`
now fails if the rules lane changes behaviour on validation750. This is weaker
than a direct file pin and is recorded as a known limitation.

## Verification

- `scripts/check_retained_evidence_manifest.py` — valid.
- `scripts/verify_reference_evidence.py` — all six reference cells replay; Gan
  rules-only returns `purist_correct: 682`, `pragmatic_correct: 690`, 750 rows.

## Not changed

- `test450` remains unconsumed. A fresh Gate A against the newly frozen
  ruleset was the precondition for any holdout run; it has since
  [passed](rules_only_validation750_gate_a_2026-08-10.md)
  (2026-08-11, 0 label diffs across 750 rows). Gate B (holdout execution) has
  not been entered.
- `docs/canon/10_paper_provenance.md` has no Gan rules-only headline row, so no
  cited figure moved. Any future citation must use `673/741` or `682/750`, never
  the retired `688/741`.
