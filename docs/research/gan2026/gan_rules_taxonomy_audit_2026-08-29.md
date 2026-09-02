# Gan rules-only rule taxonomy audit (Phase B prerequisite)

Date: 2026-08-29
Protocol: [three-stage protocol](gan_rules_only_three_stage_protocol_2026-08-29.md)
Phase A: [instrumentation result](gan_rules_only_three_stage_phase_a_2026-08-29.md)
Artifact: `experiments/gan2026_rules_only_three_stage_20260829/rule_inventory.json`
(generated per-rule table: rule_id, module, group, portability, exclude,
example count, description)
Split basis: ledger-share numbers measured on `dev750` wide ledgers;
no holdout loaded.

## Inventory

| Producer class | Count | Stage role (locked taxonomy) | Attributable? |
| --- | ---: | --- | --- |
| `RuleSpec` producers — cluster | 27 | find + encode fused (builders emit codebook labels) | yes (rule_id, ablatable) |
| `RuleSpec` producers — rate | 30 | find + encode fused | yes |
| `RuleSpec` producers — diary | 11 | find + encode fused | yes |
| `RuleSpec` producers — seizure_free | 9 | find + encode fused | yes |
| `RuleSpec` producers — gan_shorthand | 4 | find + encode fused | yes |
| `RuleSpec` producers — unknown (in `deterministic_extraction`) | 1 | find | yes |
| Inline regex producers in `extract_rate_candidates` | 32 | find + encode fused | **no** (`rule_id="unknown"`) |
| Inline regex producers in `_extract_unknown_candidates` | 3 | find | **no** |
| `RuleSpec.exclude` predicates (9 rules) | 9 | select interleaved in find | recorded since Phase A (span-level) |
| Inline distractor call in `extract_rate_candidates` | 1 | select interleaved in find | no |
| Dedupe / fragment / historical pruning | 3 mechanisms | select | relocated to tagged drops in Phase A |
| Priority ladder + evidence cues | 7 reasons | select | ablatable (`temporal_selection`) |
| `repair_prediction_label` + parse fallback | n/a | encode | measured no-op on Phase A doc-order picks |

Total: **82 named `RuleSpec`s**, 9 with exclusion predicates, plus
**35 anonymous inline producers**.

## Findings

1. **A quarter of the find ledger is anonymous.** On `dev750`,
   366 of 1,419 wide-ledger candidates (**25.8%**) carry
   `rule_id="unknown"` — 347 frequency-rate and 19 unknown-frequency
   candidates from the inline regexes. These cannot be ablated,
   attributed, or gated per class. Any Phase B/C work that needs
   per-class keep/drop decisions on rate candidates must either name
   these producers first or treat them as one opaque class.
2. **Every builder encodes.** All 82 `RuleSpec` builders and all
   inline producers emit final codebook-form labels at match time
   (Phase A measured the encode stop contributing exactly zero).
   A true encode stage for rules would have to move label arithmetic
   (rate rendering, seizure-free date math, cluster arithmetic) out of
   the builders — a Phase C+ decision, not required for Phase B
   recall work because provisional producers can carry provisional
   labels of the same designed form.
3. **Select-in-find is now bounded.** The nine `exclude`
   predicates (71 suppressions on `dev750`, dominated by
   `seizure_free.generic_duration_or_since` with 31) are recorded
   spans since Phase A. The single inline distractor call remains
   unrecorded; it guards one inline rate pattern.
4. **Ledger concentration.** The top named producers are
   `seizure_free.current_control_phrase` (175),
   `rate.direct_count_per_period` (152),
   `seizure_free.generic_duration_or_since` (117) — the seizure-free
   family produces heavily, which matches the Phase A finding that 13
   gold-`unknown` rows are answered seizure-free with no `unknown`
   candidate even present.

## Consequence for Phase B

New recall-first producers must be **named `RuleSpec`s with a
provisional tag** from the start (no new inline regexes), so the
Select gate can own their keep/drop per class. The protected benchmark
shorthand rows stay unfixed. The anonymous inline producers are left
as-is for Phase B (renaming them is score-neutral refactoring work
that should not be mixed into a recall candidate).
