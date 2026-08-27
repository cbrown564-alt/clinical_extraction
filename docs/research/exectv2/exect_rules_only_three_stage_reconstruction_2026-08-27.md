# ExECT rules-only three-stage reconstruction

Date: 2026-08-27
Status: accepted development candidate; holdout replay complete
Protocol: [three-stage reconstruction protocol](exect_rules_only_three_stage_reconstruction_protocol_2026-08-27.md)
Holdout: [test60 aggregate replay](exect_rules_only_three_stage_test60_aggregate_2026-08-27.md)
Brief: [reconstruction brief](exect_rules_only_three_stage_reconstruction_brief_2026-08-27.md)
Artifact: [`experiments/exect_rules_only_three_stage_reconstruction_20260827/summary.json`](../../../experiments/exect_rules_only_three_stage_reconstruction_20260827/summary.json)
Runner: `scripts/measure_exect_rules_only_three_stage_dev140.py`

## Answer

Re-specifying standalone rules as recognise / encode / select — a typed
recognise ledger, per-family encode switches, and an ordered switchable
Select sequence — raises `dev140` exact 4-family inventory micro F1
from **0.8949 to 0.9167** (P 0.926 / R 0.908). Thirty-six letter/family
pairs improve; none worsen; no comparator-exact pair regresses. The
frozen candidate is `ACCEPTED_THREE_STAGE_CONFIG` in
`orchestration/rules.py`. The comparator `run_letter` and the cited
five-cell rules row **0.7725** in promoted artifacts are unchanged.
Aggregate-only holdout replay of the candidate scores **0.8018**
inventory F1 (+0.0126 vs same-run `run_letter` **0.7892**).

Gemini cell 3 select-stop on the same split is 0.8877. The
reconstructed rules program is above it on development. That is a
development statement only.

## The structural change

`run_letter_three_stage` runs three independently stoppable programs:

1. **Recognise ledger** (`deterministic/recognise_ledger.py`). Every
   extractor mention becomes a `direct` candidate. Deferred classes
   carry what extract used to discard: Diagnosis nested ancestors,
   non-diagnostic Diagnosis contexts, SF named-type / heading-state /
   seizure-free candidates. Deferred candidates are never emitted
   directly; Select reads them as `source_mentions`.
2. **Encode registry.** Same-fact encode per family
   (`encode_families`; Diagnosis on, as in the comparator).
3. **Select sequence.** `select_rule_ids` in recorded order on the
   encoded direct rows with the full ledger visible.

With the default config the runner is mention-identical to
`run_letter` on all 140 development letters (M1 gate).

## Accepted components (each isolated-positive, each leave-one-out-negative)

| Component | Isolated F1 | Leave-one-out F1 | Mechanism |
| --- | ---: | ---: | --- |
| D1 service-context exclusion | 0.9078 | 0.9038 | `epilepsy` immediately followed by nurse / service / helpline / clinic / team / colleagues, or inside `family history of`, is not a patient diagnosis. Possessive prefix (`his epilepsy started…`) overrides the onset-statement exclusion. 23 pairs improve. |
| D2 secondary-to retention | 0.9008 | 0.9107 | `_is_diagnosis_phrase_inside_cause_statement` was deleting the left-side diagnosis in `focal epilepsy secondary to X`. Retained; the cause side stays excluded. 9 pairs improve. |
| D3 focal-onset alias | 0.8962 | 0.9154 | `Diagnosis: Epilepsy - focal onset` and `possibly focal onset` now emit the focal-epilepsy concept. 2 pairs improve. |
| S2 SF seizure-free positive-count drop | 0.8954 | 0.9161 | A `seizure free` surface carrying `NumberOfSeizures > 0` is a mis-anchored rate (`selection.sf_seizure_free_positive_count_drop`). |
| W1 inventory weak-episode drop | 0.8960 | 0.9156 | Existing `selection.inventory_weak_episode_drop`, now on for rules-only; drops bare `jerk`-class anchors. |

Candidate family cut versus comparator: Diagnosis **0.8257 → 0.8765**
(FN 59 → 45, FP 55 → 35), SeizureFrequency **0.8563 → 0.8640**
(FP 26 → 23), Prescription and Investigations unchanged. Family
error deltas: Diagnosis −34, SeizureFrequency −3, others 0.

## Rejected components (recorded negative results)

- **S1 generic-duplicate SF drop** (`selection.sf_generic_duplicate_of_named_type_drop`):
  isolated 0.8932 with 4 comparator-exact regressions. Gold keeps the
  generic and named unit side by side in EA0050, EA0123, EA0161,
  EA0186. The rule stays in the catalogue, off everywhere.
- **Nested-ancestor promotion** (M2): ungated
  `inventory_keep_source_diagnosis` over the nested-ancestor class
  promotes 22 ancestors for ≤ 2 real FNs and falls to 0.8804. The
  class stays in the ledger; no Select rule promotes it.
- **SF named-type promotion** (M3, `selection.sf_supported_state_promotion`
  over `sf_named_type`): 7 promotions, mostly wrong `(type, unknown)`
  units; SF F1 0.856 → 0.845. Producer and rule retained, off.
- **SF heading-state / seizure-free producers** emit zero candidates
  on `dev140` after support filtering; score-neutral, not enabled.

## Row-level mechanism (development, permitted)

The dominant Diagnosis error was one confusion: 35 letters predicted a
generic `epilepsy` unit that gold omits because every occurrence was
administrative (`the epilepsy nurse`, `The Epilepsy service`,
`epilepsy helpline`, `no family history of epilepsy`), while gold
keeps the generic when any occurrence is a patient assertion
(`this lady with epilepsy`, `Diagnosis: epilepsy – unclassified`).
Two D1 implementation defects were found and fixed during gating: the
collocation test matched anywhere in a 64-character window (killing
`epilepsy in clinic today` letters), and the onset-statement exclusion
deleted `his epilepsy started at the age of 14`, which gold annotates.

The SF picture is different: the biggest remaining SF errors are
named-type identity and gold dated-event conventions, not missing
anchors. Ledger coverage confirms recall is not the binding
constraint on development: direct-vs-ledger gold-unit recall is
0.796 → 0.799 (Diagnosis) and 0.867 → 0.879 (SeizureFrequency).

## Claim boundary

Development and aggregate holdout evidence on the frozen candidate.
The cited five-cell rules row **0.7725** remains in promoted paper
artifacts until an owner promotes **0.8018**. Sealed holdout rows were
not inspected. SeizureFrequency remains the binding holdout weakness
(F1 **0.6131** vs cell 3 **0.8082**). See
[test60 aggregate replay](exect_rules_only_three_stage_test60_aggregate_2026-08-27.md).

## Next executable step

Further development, if wanted: remaining Diagnosis residuals are
specific-concept recognise gaps; remaining SF residuals need a gated
rewrite design (not promotion). Holdout promotion is an owner decision,
not automatic from this replay.
