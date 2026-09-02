# Protocol: Gan rules-only Phase E2 (remaining find/encode families)

Date: 2026-08-30
Status: complete
Owner: this file
Report: [Phase E2 result](gan_rules_only_three_stage_phase_e2_2026-08-30.md)
Parent: [Phase E](gan_rules_only_three_stage_phase_e_protocol_2026-08-30.md)
Guardrail: `gan2026-scoring-guardrail`
Split: `dev750` only; `test450` sealed. Zero model calls.

## Primary question

Can cluster, diary, and gan-shorthand builders emit the same slot-level
`FindFact` as the rate family, so encode is the only writer of their
codebook strings, without changing the submitted select label?

## Stage-stop policy

Unchanged from Phase E. Find is the pre-codebook tag of the
document-order pick. Encode is codebook render of that pick. Select is
the submitted label. Cited five-cell stops stay **292 / 292 / 325**.

Cluster find tags use `cluster:{count}/{period}:{size}` from raw slots.
Unknown-with-size find tags stay `unknown`; encode writes
`unknown, N per cluster`. Diary and gan-shorthand use the rate slot tag
(`{count}/{unit}`). Adjective and compact units (`daily`, `mo`) stay raw
at find; encode maps them.

Date-window and diary-aggregation arithmetic stay in find. Encode only
renders already-chosen slots.

## Gates

- **E1:** default select identical to `run_record` on `dev750` (669/750).
  Promoted select remains 691/750.
- **E5:** cluster, diary, and gan-shorthand RuleSpec examples still emit
  their recorded `expected_label`, and those candidates have
  `find_fact.custom_label is None`.
- **E6:** fixtures exist where cluster / diary / shorthand find_tag ≠
  encode codebook form on the same pick.

No new Select keep. No holdout replay. No `_gan_grid` rewire.
