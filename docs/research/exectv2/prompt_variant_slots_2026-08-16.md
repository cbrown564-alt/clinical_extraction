# ExECT prompt variants (current hybrid)

Date: 2026-08-16  
Status: **assigned**  
Ledger: [REGENERATION.md](../../REGENERATION.md)  
Taxonomy: [hierarchical matrix](../maintenance/retention_slice_hierarchical_retention_matrix_2026-08-16.md)  
Table: [retention candidate table](../maintenance/retention_candidate_table_2026-08-16.md)

The current one-call ExECT hybrid keeps three prompt variants. That is
the [REGENERATION.md](../../REGENERATION.md) three-slot cap for prompt
variants inside the selected hybrid, not a fourth architecture and not
a Decision 0050 change.

`load_bearing` on a prune stop bar is a reason not to replace the live
default. It is not a reason to drop a named cheap variant.

## The three variants

| Slot | Role | Identity | Status |
| --- | --- | --- | --- |
| 1 | Full selected prompt | `exectv2_hybrid_key_family_event_ledger_v0.9.24` | Selected live default. Six-model and replay identity. |
| 2 | Cheap stack | `exectv2_hybrid_key_family_event_ledger_v0.9.44_cheap_stack_further_prunes` | Retained cheap variant. Not selected. User-reassigned 2026-08-17. |
| 3 | Mention-unit encoder | `exectv2_mention_unit_v2` | Retained representation alternative. Not selected. Encoder pairing still open. |

Live default stays `v0.9.24`. Decision 0050 is unchanged. Do not
inspect `test60`. Slot 2 is now the stacked further prune. The
three-model `dev140` remasure is in progress. Owner:
[slot-2 `dev140` protocol](v0924_cheap_slot2_dev140_protocol_2026-08-17.md).

## Slot 1 — full `v0.9.24`

The selected current-stack prompt. Scaffold, encoding, scope, and all
49 examples stay in the live payload.

- Prompt identity: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- EA0133 live payload: 58,382 characters
- Owners: [Decision 0050](../../decisions/0050-current-stack-hybrid-primary-fills.md);
  [Decision 0046](../../decisions/0046-exect-primary-method-comparison-boundary.md);
  current-stack sidecars
- Prune lineage: [THREAD_MAP door](../../THREAD_MAP.md#exect-v0924-leave-one-out-prune)

This slot is the paper/current method. Later cheap or mention-unit
work is compared to it. It is not replaced by a cheaper or more
natural representation until a new selected-stack decision says so.

## Slot 2 — cheap stack

The half-size cut of the same hybrid prompt. It drops the 16 non-SF
encoding rules and all 49 examples. It keeps the 13 SF encoding
rules, all scope rules, and the remaining scaffold in ordinary
language.

- Prompt identity: `exectv2_hybrid_key_family_event_ledger_v0.9.44_cheap_stack_further_prunes`
  (user-reassigned 2026-08-17). Predecessor:
  `exectv2_hybrid_key_family_event_ledger_v0.9.40_drop_encoding_non_sf_all_examples`
- EA0133 payload after the language pass: 25,249 characters (−33,133,
  **−57%**)
- Structural-cut Luna `dev20` versus `v0.9.24`: headline −0.0168;
  SeizureFrequency **−0.0929**; exact 10/20 → 9/20
- Cleaned-wording remasure on the same pool: headline −0.0255;
  SeizureFrequency still **−0.0929** (0.8302); exact 9/20. Versus the
  pre-cleanup cheap raws, SF F1 is unchanged.
- Prune verdict on that pool: **load_bearing** (family bar). That
  verdict blocks promotion. It does not block retention.
- Authorized Luna `dev140` transfer versus saved `v0.9.24`: headline
  −0.0118; SeizureFrequency −0.0465; exact 55/140 → 49/140 (net −6).
  Verdict: **load_bearing** (exact bar). Owner:
  [cheap-stack `dev140`](v0924_cheap_stack_luna_dev140_2026-08-16.md)
- One-at-a-time further prunes on Luna `dev20` versus the cleaned
  cheap stack: investigation-pending, scaffold-reprint, and refuse
  chorus are each **low_value**. Stacking those three cuts stays
  **low_value** (headline +0.0047; exact 11/20) and does not keep the
  scaffold-only SF bump. The user then assigned the stacked identity
  as slot 2. The three-model `dev140` remasure is in progress. Owners:
  [further prune](v0924_cheap_further_prune_luna_dev20_2026-08-16.md);
  [stacked](v0924_cheap_further_prune_stacked_luna_dev20_2026-08-17.md);
  [slot-2 `dev140`](v0924_cheap_slot2_dev140_protocol_2026-08-17.md)
- Owners: [cheap-stack report](v0924_cheap_stack_luna_dev20_2026-08-16.md);
  [plain remasure](v0924_cheap_stack_plain_luna_dev20_2026-08-16.md);
  [further prune](v0924_cheap_further_prune_luna_dev20_2026-08-16.md);
  [protocol](v0924_cheap_stack_luna_dev20_protocol_2026-08-16.md);
  artifacts
  `experiments/exectv2_v0924_cheap_stack_luna_dev20_20260816/comparison.json`
  and
  `experiments/exectv2_v0924_cheap_stack_plain_luna_dev20_20260816/comparison.json`

This slot exists so the project can keep a cheap instruction stack
next to the full selected prompt. It is not a new selected stack, not
holdout evidence, and not a licence to retune from the SF drop.

## Slot 3 — mention-unit encoder

The Fork A representation alternative: ordinary-language mention
units, then a named hybrid encoder. The prompt identity is
`exectv2_mention_unit_v2`. The encoder pairing is part of this slot,
not a fourth prompt.

Current pairing:

- Prompt: `exectv2_mention_unit_v2` (language frozen)
- Default encoder: `landed`
- Measured form-recovery encoder: `leftover_form`
  (`exectv2_mention_unit_leftover_form_v1`)

Neither encoder is selected. `landed` stays the default. Do not start
mention-unit v3 or Fork B from this assignment.

Owners:
[campaign](../../plans/exect_llm_representation_and_hybrid_revaluation_2026-08-16.md);
[prompt fundamentals](../../plans/exect_prompt_fundamentals_2026-08-16.md);
[v2 `dev20`](mention_unit_v2_fork_a_luna_dev20_2026-08-16.md);
[v2 `dev140`](mention_unit_v2_fork_a_luna_dev140_2026-08-16.md);
[hybrid encoder](mention_unit_v2_hybrid_encoder_damage_luna_dev140_2026-08-16.md);
[leftover-form](mention_unit_v2_leftover_form_encoder_luna_dev140_2026-08-16.md);
[Decision 0055](../../decisions/0055-exect-semantic-inventory-and-method-contracts.md).

What this slot may claim today: gold SeizureFrequency wording can
appear as `clinical_name` on frozen Luna `dev20`; the `dev140`
transfer is a revise; the landed encoder keeps names and loses form;
leftover-form recovers some of that form on saved raws. What it may
not claim: selected-stack parity, holdout generalization, or a
finished encoder.

## What these slots are not

- Not a change to the live default.
- Not a Decision 0050 or Decision 0046 rewrite.
- Not permission to inspect `test60`.
- Not a licence to replace `v0.9.24`. Slot 2 is now the stacked
  further prune; the three-model `dev140` remasure is the transfer
  measurement, not a selected-stack change.
- Not a live prompt zoo. Intermediate structured-prompt drafts
  (v10–v27), abandoned semantic-inventory / mention-unit v1 lanes, and
  intermediate prune experiment dumps are removed from the working
  tree; Markdown prune answers for `v0.9.24` remain. Recover drafts
  from Git history if needed.
- Not a fourth current-hybrid prompt.

## Where `v08` sits

`v08` holistic finding assembly stays the ExECT hybrid **reference
cell** and the Decision 0040 / 0046 historical control. It is a
different assembly architecture, not a fourth prompt inside the
current one-call hybrid. Keep the reference-cell bundle. Do not put
it back in this three-slot list.

## Evidence closure

Each slot already has a protocol, a result, and a machine artifact:

| Slot | Protocol | Result | Artifact |
| --- | --- | --- | --- |
| 1 | Decisions 0046 / 0050; current-stack runbook | Living fills | `experiments/current_stack/latest/fills.json` |
| 2 | [cheap-stack protocol](v0924_cheap_stack_luna_dev20_protocol_2026-08-16.md); [plain remasure](v0924_cheap_stack_plain_luna_dev20_protocol_2026-08-16.md); [`dev140` protocol](v0924_cheap_stack_luna_dev140_protocol_2026-08-16.md); [further prune](v0924_cheap_further_prune_luna_dev20_protocol_2026-08-16.md); [stacked](v0924_cheap_further_prune_stacked_luna_dev20_protocol_2026-08-17.md) | [cheap-stack report](v0924_cheap_stack_luna_dev20_2026-08-16.md); [plain remasure](v0924_cheap_stack_plain_luna_dev20_2026-08-16.md); [`dev140`](v0924_cheap_stack_luna_dev140_2026-08-16.md); [further prune](v0924_cheap_further_prune_luna_dev20_2026-08-16.md); [stacked](v0924_cheap_further_prune_stacked_luna_dev20_2026-08-17.md) | structural cut `experiments/exectv2_v0924_cheap_stack_luna_dev20_20260816/comparison.json`; live wording `experiments/exectv2_v0924_cheap_stack_plain_luna_dev20_20260816/comparison.json`; transfer `experiments/exectv2_v0924_cheap_stack_luna_dev140_20260816/comparison.json`; further prune `experiments/exectv2_v0924_cheap_further_prune_luna_dev20_20260816/comparison.json`; stacked `experiments/exectv2_v0924_cheap_further_prune_stacked_luna_dev20_20260817/comparison.json` |
| 3 | [v2 `dev20` protocol](mention_unit_v2_fork_a_luna_dev20_protocol_2026-08-16.md) | [v2 `dev20`](mention_unit_v2_fork_a_luna_dev20_2026-08-16.md); later catalogs on the [Fork A door](../../THREAD_MAP.md#exect-llm-representation-fork-a) | `experiments/exectv2_mention_unit_v2_luna_dev20_20260816/comparison.json` |

Slot 3 may later name one encoder pairing as its retained closure
without opening a new prompt slot.

## Claim boundary

This note assigns retention slots. It does not select a new prompt,
change scored hybrid fills, or treat Luna `dev20` cheap-stack or
mention-unit numbers as holdout or paper primary results.
