# Inventory Select replay on the recall-first extract

Date: 2026-08-23
Status: answered on development data; not a paper cell
Owner: this file
Track: [inventory](exect_llm_inventory_track.md)

## Primary question

On the frozen Gemini inventory extract (`dev140` run 3), which
deterministic Select / lens / suppression pieces still help inventory
F1 after extract started keeping generic diagnoses, heading types, and
companion frequency states?

The Compact Select stack was tuned for headline collapse and a thinner
extract. Inventory now emits about 100 more mentions and scores unique
Diagnosis concepts. Select should filter extracted candidates. It
should not invent from unused letter text.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Split | `dev140` |
| Row policy | Development review permitted |
| Locked split | `test60` sealed; not loaded |
| Extract | `experiments/paper/exect_llm_inventory/gemini37flash/dev140/exect_llm_inventory/structured.jsonl` |
| Model | Gemini 3.7 Flash, effort low |
| Call mode | No new model calls |
| Scorer | `clinical_inventory_unit_keys` |

## Answer

Toggling the Compact Select switches does not unlock the extra extract
volume. Named paper rules still help Prescription. Keeping
syndrome-covered phenotypes and turning off unknown-suppression did
nothing. Turning off `selection.sf_to_diagnosis_explicit_type` gained
0.0009 F1 and broke one exact Diagnosis letter.

The Compact stack was still replacing extract parents with more
specific syndromes (`epilepsy` → `focal epilepsy` → a lobe syndrome).
Inventory gold wants both. A second leftover from the fatter extract
is non-seizure episode wording (`events`, `jerk`, `drops`).

The accepted inventory-only profile keeps the paper Diagnosis and
Prescription Select rules and adds:

- `selection.inventory_keep_source_diagnosis` — restore an extract
  Diagnosis that is an ancestor of a selected concept
- `selection.inventory_weak_episode_drop` — drop event/episode/jerk
  wording that is not a seizure type

Paper `StructuredMethodConfig.selected()` is unchanged. Inventory
Select drops Compact headline SeizureFrequency companion rules
(named-type identity, SF-to-Diagnosis invent, umbrella-clone,
generic-to-named rewrite, dated-cluster-next-to-free,
preceded-by-current-free, and unknown suppression). Those rules stay
on the paper Compact stack.

| Arm | Inventory F1 | Diagnosis | SeizureFrequency | Exact letter/family regressions |
| --- | ---: | ---: | ---: | ---: |
| Extract | 0.8273 | 0.7197 | 0.7967 | — |
| Paper Select | 0.8822 | 0.8228 | 0.8421 | comparator |
| Inventory Select with headline SF rules | 0.8917 | 0.8392 | 0.8571 | 0 vs paper |
| Inventory Select | **0.8877** | **0.8413** | **0.8338** | vs paper: Diagnosis up, SF down |

Current inventory Select is +5 TP and −4 FP versus paper Select.
Removing the headline SF rules costs 2 TP and adds 5 FP versus the
prior inventory stack: Diagnosis inventory F1 rises (no SF-to-Diagnosis
invent) and SeizureFrequency falls (companion mentions stay). Claim is
development-only. Not holdout.
