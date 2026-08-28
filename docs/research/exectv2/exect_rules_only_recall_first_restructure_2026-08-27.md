# Results: ExECT rules-only recall-first restructure (Phases A–C)

Date: 2026-08-27
Protocol: [restructure protocol](exect_rules_only_recall_first_restructure_protocol_2026-08-27.md)
Artifacts: `experiments/exect_rules_only_recall_first_20260827/` (per-arm JSON)
Split: `dev140` only; `test60` sealed throughout Phases A–C.
Scorer: `clinical_inventory_unit_keys`, zero model calls.
Comparator: `run_letter` = `run_letter_three_stage(ACCEPTED_THREE_STAGE_CONFIG)`, dev140 select stop 0.9167.

## Phase A — taxonomy and plumbing (gates met)

- [Rule taxonomy audit](exect_rules_only_rule_taxonomy_audit_2026-08-27.md) classifies
  every deterministic rule by actual role (recognise / encode / select) and family.
- `ThreeStageConfig` gained per-family encoder and select-sequence plans
  (`family_encoders`, `family_select`, validated by
  `flatten_family_select_plan`) plus tagged recall-first `direct_classes`.
  Gate A1: default and accepted configs mention-identical to `run_letter`
  on 140/140 letters (`accepted.json`).
- Score-neutral relocations (Gate A2, each select-stop mention-identical
  on 140/140): SF rate-gate (`sf_rateless_relocation`), Diagnosis
  non-diagnostic context (`dx_context_relocation`), Diagnosis nested
  ancestors (`dx_ancestor_relocation`), deferred SF classes
  (`sf_deferred_relocation`), Investigations result requirement
  (`inv_resultless_relocation`), and all combined
  (`recall_first_all_relocations`).

## Phase B — recall-first recognise (targets met)

Arm `phase_b_dx_recall` (all recall-first classes emitted as tagged
direct; select stop still mention-identical to comparator, 140/140):

| Family | Baseline recognise R | Target | Achieved recognise R |
| --- | ---: | ---: | ---: |
| Diagnosis | 0.8298 | >= 0.90 | **0.9666** |
| SeizureFrequency | 0.8667 | >= 0.90 | **0.9212** |
| Prescription | 0.9709 | no dev regression | **0.9854** |
| Investigations | 0.9706 | >= 0.99 | **1.0000** |

Recognise-stop precision fell as designed (overall recognise P 0.5315,
F1 0.6862); the select stop stayed identical to the comparator.

New recognise producers (all emit tagged direct candidates; the Select
gate `selection.recall_first_unsupported_drop` owns keep/drop):

- Diagnosis: heading decomposition (qualified epilepsy headings name two
  concepts), hierarchy-free nested surfaces, expansion-lexicon surfaces
  plus alias decompositions (`diagnosis_expansion_surface`), unrestricted
  benchmark surfaces plus seizure-type→syndrome inference
  (`diagnosis_unrestricted_surface`), hierarchy ancestors, component
  tokens.
- SF: state variants (typo'd GTC anchor, plural "seizures free",
  "last seizure was", "cluster of seizures") on top of the relocated
  named-type / heading-state / seizure-free / rate-less classes.
- Prescription: external ASM generics and UK brand aliases
  (`EXTERNAL_ASM_GENERICS`, `EXTERNAL_ASM_BRAND_ALIASES`), edit-distance-1
  typo matching (words >= 7 chars), relaxed line-scoped dose/frequency
  parse (dotted abbreviations, bullet-item default frequency, rescue
  `As_Required`).
- Investigations: result variants for result-less mentions (inherit the
  letter-level bound result of the modality, else `Unknown`).

## Phase C — Select precision recovery (gates met)

Isolated keep arms on the Phase B ledger (select-stop deltas vs
comparator; regressions = comparator-exact letter/family pairs broken):

| Keep (candidate class) | Select F1 | Regressions | Improved | Verdict |
| --- | ---: | ---: | ---: | --- |
| heading decomposition | 0.9195 | 0 | 4 | **kept** (unconditional) |
| SF state variant (conditional) | 0.9199 | 0 | 5 | **kept** |
| Rx recall expansion (conditional) | 0.9186 | 0 | 3 | **kept** |
| Inv result variant (conditional) | 0.9186 | 0 | 3 | **kept** |
| expansion surface | 0.9133 | 10 | 9 | rejected (gold unit-key inconsistencies; no explainable condition) |
| unrestricted surface | — | — | — | rejected (+19 TP / +153 FP) |
| hierarchy ancestor | — | — | — | rejected (+2 TP / +49 FP) |
| component token | — | — | — | rejected (+11 TP / +158 FP) |
| nested surface | — | — | — | rejected (+2 TP / +70 FP) |
| non-diagnostic context | — | — | — | rejected (0 TP / +20 FP) |
| SF named-type / heading-state / seizure-free | 0.9167 | 0 | 0 | neutral, left unkept |

Keep conditions (in `RECALL_FIRST_KEEP_CONDITIONS`, plain-language
rationale in `select_rules.py`):

- Inv result variant: evidence must assert the test event itself
  ("had a CT head", "underwent an MRI", "recent EEG results") and name
  the modality exactly once (a second in-sentence mention means the
  result-less token belongs to the same test event).
- Rx recall expansion: evidence must describe the current regimen —
  conditional requests ("if you could prescribe"), queries/refusals
  ("asked about whether", "wouldn't recommend"), and transitional doses
  inside an upward titration ("increasing to") stay dropped.
- SF state variant: the cluster surface counts as an active event only
  when reported as having happened ("had a cluster of seizures"); the
  plural "seizures free" surface only fills a gap when the well-formed
  singular surface is absent from the letter.

SF R1/R3 gated rewrite components (per the
[gated SF rewrite protocol](exect_rules_only_sf_gated_rewrite_protocol_2026-08-27.md))
were measured score-neutral on dev140 in
`experiments/exect_rules_only_sf_gated_rewrite_20260827/summary.json`;
`selection.sf_named_type_identity` (R1) is already in the accepted
stack, and no additional R2/R3 rules earned acceptance. The recall-first
SF gains came from the state-variant keep instead.

Accepted candidate (`phase_c_candidate` = frozen
`RECALL_FIRST_THREE_STAGE_CONFIG`):

| Stop | F1 | P | R |
| --- | ---: | ---: | ---: |
| recognise | 0.6862 | 0.5315 | 0.9677 |
| encode | 0.6885 | 0.5343 | 0.9677 |
| select | **0.9266** | 0.9249 | 0.9282 |

Per family at the select stop (comparator → candidate F1): Diagnosis
0.8765 → 0.8841, SeizureFrequency 0.8640 → 0.8810, Prescription
0.9780 → 0.9854, Investigations 0.9851 → 0.9963.

Gate C: candidate F1 0.9266 >= 0.9167; **zero** comparator-exact
regressions (15 letter/family pairs improved, 0 worsened); every kept
class isolated-positive and leave-one-out-negative
(`phase_c_loo_*`: 0.9238 / 0.9234 / 0.9246 / 0.9246, all < 0.9266);
Phase B recognise recall targets maintained.

## Claim boundary

Development mechanism evidence on dev140 only. The cited rows
(dev 0.9167, test60 0.8018) do not move until the Phase D
aggregate-only replay completes and an owner promotes the result.
