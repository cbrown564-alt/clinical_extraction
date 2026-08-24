# ExECT cells 1–2 on 4-family micro F1

Date: 2026-08-23
Status: superseded for cell 2 by
[both-extract on inventory](exect_both_extract_on_inventory_protocol_2026-08-23.md).
Cell 1 rules totals below remain the cited 4-family micro F1.
Owner: this file
Related: [Gemini cells 3–5](exect_gemini_inventory_cells_3_5_protocol_2026-08-23.md)

## Primary question

What are the Gemini cell 1 and cell 2 select stops when the same
4-family micro F1 used for cells 3–5 is applied to standalone rules
and to both-extract?

## Why it matters

The cited ExECT table cannot mix the Compact/headline collapse
(Diagnosis de-duplicated) with micro F1 on the four families. The
headline scorer needed its own name because it collapsed repeats.
This score does not. It is micro-averaged F1 over Diagnosis,
SeizureFrequency, Prescription, and Investigations.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Model | none (cell 1); saved Gemini 3.7 Flash both-extract (cell 2) |
| Cell 1 | `exect_rules` |
| Cell 2 | superseded rescore: saved `exect_llm_pre_post`, Compact encode/select. Cited cell 2: living both-extract plus inventory Select |
| Development | `dev140`, review permitted |
| Holdout | `test60`, aggregate only. Do not inspect rows. |
| Calls | none |
| Scorer | 4-family micro F1 (`clinical_inventory_unit_keys`) |

Do not change cell 2's rule stack. Rescore only.

## Stop rule

Answer when both splits have aggregate 4-family micro F1 for cells
1–2 and the five-cell owners cite one scorer for all five rows.

## Answer

Cell 1 rules: `dev140` **0.8824**, `test60` **0.7725**. Cell 2 was
re-run on the living extract plus suggested candidates; do not
cite the Compact-raw rescore (0.8659 / 0.8031). See
[both-extract on inventory](exect_both_extract_on_inventory_protocol_2026-08-23.md).
