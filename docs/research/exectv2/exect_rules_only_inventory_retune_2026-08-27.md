# ExECT rules-only inventory retune

Date: 2026-08-27
Status: accepted on development; cited holdout cell unchanged
Protocol: [inventory retune protocol](exect_rules_only_inventory_retune_protocol_2026-08-27.md)
Artifact: [`experiments/exect_rules_only_inventory_retune_20260827/summary.json`](../../../experiments/exect_rules_only_inventory_retune_20260827/summary.json)

## Answer

A recall-first extract plus Diagnosis encode and a Diagnosis-only
inventory Select stack raises standalone rules on `dev140` from
**0.8824 to 0.8949** inventory F1 (P 0.899 / R 0.891). Eight Diagnosis
letter/family sets improve. None worsen. Rate-less SF anchors are
rejected. The cited `test60` **0.7725** cell is unchanged.

## What was accepted

1. **Investigations are per-occurrence.** Same-result collapse left
   extract. Distinct MRI/EEG/CT spans survive mention identity.
   Investigations F1 **0.962 → 0.985** (FN 10 → 4, precision 1.0).
   `selection.investigation_same_result_dedupe` exists as a switch and
   is **off** in the accepted rules-only set.

2. **Diagnosis recognise then encode/Select.** Heading aliases
   (`focal onset epilepsy`, localisation-related, symptomatic
   structural, `epilepsy – probable focal`) are recognised. `run_letter`
   then applies `encoding.diagnosis_standard_name` and inventory
   `keep_source` / local-specificity / heading-phenotype Select.
   Diagnosis F1 **0.803 → 0.826** (FN 70 → 59).

3. **Rate-less SF anchors are rejected.** Emitting them then dropping
   them at Select falls to **0.7909** (precision 0.71). Default extract
   still requires a nearby rate.

Prescription and SeizureFrequency scores are unchanged versus the
pre-Select extract. Applying the full inventory Select plus SF/Rx
encode caused four exact-family regressions; those rules stay off for
rules-only.

## Bound

Development mechanism only. Gemini cell 3 select-stop on `dev140` is
0.8877; this rules stack is now slightly higher there. That does not
move the locked five-cell rules row. A later aggregate-only `test60`
replay would need its own protocol.

This patch is not the three-stage reconstruction. Follow-up:
[reconstruct rules-only for recognise / encode / select](exect_rules_only_three_stage_reconstruction_brief_2026-08-27.md).
