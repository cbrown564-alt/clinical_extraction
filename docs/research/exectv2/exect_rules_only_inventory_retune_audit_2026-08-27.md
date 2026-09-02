# ExECT rules-only is not a fair cell-3 comparison

Date: 2026-08-27
Status: development diagnosis; not a five-cell replacement
Protocol: [inventory retune audit](exect_rules_only_inventory_retune_audit_protocol_2026-08-27.md)
Artifact: [`experiments/exect_rules_only_inventory_retune_audit_20260827/summary.json`](../../../experiments/exect_rules_only_inventory_retune_audit_20260827/summary.json)

## Answer

The comparison is unfair, but not mainly because leftover Diagnosis
collapse still hides parents. Standalone rules never received the
recognise-then-Select program that made cell 3 work on the inventory
scorer. On `dev140` they already recover most uncollapsed Diagnosis
units. What they do not have is a recall-first ledger that still
contains the dropped candidates, then a precision Select that can add
or drop them.

Replay of the living inventory Select stack on the current rules
ledger is almost a no-op. The useful cell-3 rules have nothing to
read.

`test60` was not loaded.

## What changed in the scorer

Cited ExECT scoring is 4-family micro F1
(`clinical_inventory_unit_keys`). Diagnosis is unique concepts with
**no most-specific collapse**. De-duplication belongs to Select
([score definitions](../paper/score_definitions_2026-08-17.md)).
`clinical_headline_unit_keys` remains the Compact ablation: Diagnosis
405 raw mentions → 289 collapsed units on `dev140`; inventory Diagnosis
is **329**.

Rules-only was built as extract-then-identity-dedupe
(`extract_deterministic_all9` → `dedupe_mentions`). It has no encode
stop and no Select stop. Cell 3 is a different program: inventory
recognise, then recorded encode, then inventory Select
(`INVENTORY_KEEP_SOURCE_DIAGNOSIS`, weak-episode drop, Rx scope,
heading phenotype).

## Fresh `dev140` measurement

No-call `extract_deterministic_all9` on 140 development letters.
Exact family unit keys, not the mixed family F1s in the 15 Aug
`exect_rules/dev140.json` file.

| Arm | Inventory P | Inventory R | Inventory F1 | Headline F1 |
| --- | ---: | ---: | ---: | ---: |
| Current rules | 0.894 | 0.871 | **0.8824** | 0.8778 |
| Diagnosis without overlap occupancy | 0.894 | 0.871 | 0.8824 | 0.8778 |
| Investigations without same-result collapse | 0.895 | **0.878** | **0.8865** | 0.8820 |
| Inventory Select on the current ledger | 0.897 | 0.871 | 0.8835 | 0.8789 |

Gemini cell 3 select-stop on the same split is **0.8877**. Rules-only
is close on development. The locked gap (0.7725 vs 0.8674) is the
unfair headline, not this development total.

Current inventory family cut:

| Family | P | R | F1 | FN | FP |
| --- | ---: | ---: | ---: | ---: | ---: |
| Diagnosis | 0.820 | 0.787 | 0.803 | 70 | 57 |
| SeizureFrequency | 0.846 | 0.867 | 0.856 | 22 | 26 |
| Prescription | 0.985 | 0.971 | 0.978 | 6 | 3 |
| Investigations | 1.000 | 0.926 | 0.962 | 10 | 0 |

Gemini cell 3 select-stop family F1 on `dev140` is Diagnosis **0.841**,
SeizureFrequency 0.834, Prescription 0.960, Investigations 0.959.
Rules win the last three on development and lose Diagnosis.

## a) Rules that assume an older scoring contract

### 1. Diagnosis longest-match recognise (real, but not the residual)

The Diagnosis extractor sorts surfaces longest-first and then skips
overlapping spans. `re.finditer` on that alternation never emits a
nested parent (`epilepsy` inside `focal epilepsy`). Occupancy recovery
found **0** extra mentions.

That is Compact-era “keep the most specific phrase” at recognise.
Inventory Select cannot later `keep_source_ancestor` because the
ancestor was never in the ledger.

It is **not** why 70 Diagnosis facts are missing. Only **2** inventory
FNs are a gold parent while a predicted child is present
(`focal epilepsy` under `frontal lobe epilepsy` on EA0054; `epilepsy`
under `focal epilepsy` on EA0178). Both would have been collapsed by
headline. Rules already recover 35 of the 40 extra inventory Diagnosis
units (headline TP 224 → inventory TP 259).

### 2. Investigations same-result collapse (measured harm)

`_collapse_same_result` keeps one (modality, result) pair. Both
headline and inventory score Investigations **per occurrence**.
Turning the collapse off on `dev140` rescues **6** mentions: FN 10 → 4,
precision stays 1.0, inventory F1 **0.8824 → 0.8865**. This rule is
unsuitable for the current scorer and was already unsuitable for
per-occurrence headline.

### 3. Residual Diagnosis redundancy helpers

`is_redundant_diagnosis_residual_addition` still treats a parent as
covered by a more specific selected concept. Those helpers are off in
the selected baseline (`include_diagnosis_benchmark_residuals=False`),
so they are dormant, not the live score.

### 4. Inventory Select cannot be bolted on

Replay of `INVENTORY_SELECT_RULE_IDS` on the current rules mentions
fired only `selection.inventory_weak_episode_drop` twice. Keep-source
Diagnosis, heading phenotype, Rx titration, and Rx dedupe did not
fire. Source and selected were the same already-filtered list.

## b) The missing recall-then-precision sequence

Cell 3’s gain was: emit a wide inventory, then let Select raise
precision while holding recall (Gemini `test60` recognise P/R 0.836 /
0.863 → select 0.873 / 0.863). Rules-only still decides keep/drop
inside each extractor.

Diagnosis concept errors on `dev140` show the split they never built:

- **20** inventory FNs are `focal epilepsy`; **3** are `temporal lobe
  epilepsy`. Specific concepts are under-recognised.
- **36** inventory FPs are generic `epilepsy`. The generic surface is
  over-recognised.
- Encode/Select on the model ledger already has
  `encoding.diagnosis_standard_name` and
  `selection.diagnosis_source_local_specificity` for that pattern.
  Rules-only does not run them.

SeizureFrequency still drops anchors with no nearby rate at extract
(`pipeline.py`). That is precision-first recognise. Cell 3 keeps
named-type and heading states for later Select
(`sf_named_type_identity`, `sf_to_diagnosis_explicit_type`). Those
rules also never see a rules-only ledger.

Investigations collapse is the same inversion: precision at recognise
instead of a later optional drop.

## What this does and does not support

The files support: the locked five-cell rules row is a **different,
earlier program**; several live rules still collapse or drop at
recognise; Investigations same-result collapse costs measured
development recall; Diagnosis residual error is missed specifics plus
extra generics, which is exactly the job cell 3 gave to encode/Select;
replaying cell 3 Select on the current rules output does not
reproduce that job.

They do not support: that turning off span occupancy closes the
inventory gap; that the holdout 0.10 F1 gap is mainly Diagnosis
collapse (holdout family weakness remains SeizureFrequency); that a
retune would match cell 3; or any `test60` letter mechanism.

## Next executable step

If we retune rules-only, do it as a `dev140` protocol with three
independently switchable moves, scored on inventory units, with
changed-letter/family accounting and no holdout inspection:

1. Move Investigations same-result collapse to Select (or delete it).
2. Emit ancestor Diagnosis surfaces as candidates, then apply
   inventory keep-source / local-specificity / weak-episode Select.
3. Stop dropping rate-less SF anchors at extract; let Select drop
   unsupported states.

Do not change the cited 0.7725 cell until that study finishes and an
aggregate-only holdout replay is predeclared.
