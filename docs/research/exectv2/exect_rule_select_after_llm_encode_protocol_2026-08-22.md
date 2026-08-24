# ExECT rule-select-after-LLM-encode protocol

Date: 2026-08-22
Revised: 2026-08-23 (cited cells now use the inventory extract)
Status: superseded for cited numbers by
[Gemini inventory cells 3–5](exect_gemini_inventory_cells_3_5_protocol_2026-08-23.md)
Owner: this file

## Primary question

What is the exact clinical-fact F1 of accepted deterministic Select
rules applied to the saved Gemini later-stage encode ledger?

This is ExECT cell 4: LLM extract, LLM encode, rules select. Cell 3
inventory Select is the cited Gemini peak, not this replay (six-model
roster comparison uses rule encode/select on filtered extract). Gan
can fold extract and encode into one codebook call. ExECT cannot;
encode is a second letter-out call. The missing stop is rule select
after that call, not later-stage LLM select (cell 5). Gemini only.

## Why it matters

The cited ExECT five role rows need a Gan cell-4 analog (LLM / LLM /
rules with accepted Select on the encode ledger). Cited holdout select
stops on the living extract are in
[Gemini inventory cells 3–5](exect_gemini_inventory_cells_3_5_protocol_2026-08-23.md).
This protocol's original replay used the filtered extract and headline
scorer below; those figures are not the paper's 4-family micro F1 grid.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Model | Gemini 3.7 Flash |
| Extract | saved `exect_llm_extract_filtered` flatten (protocol-time `exect_llm_only`) |
| Encode | saved `exect_llm_encode` joined mentions |
| Select | accepted deterministic Select rule ids |
| Development | `dev140`, review permitted |
| Holdout | `test60`, aggregate only. Do not inspect rows. |
| Calls | none |
| Scorer | exact `clinical_headline_unit_keys` (development replay only; not the cited 4-family micro F1 scorer) |

## Candidate and comparator

- Comparator: later-stage encode stop (no select).
- Candidate: the same encoded mentions, then `ACCEPTED_SELECT_RULE_IDS`.
- Fixed: later-stage LLM select remains cell 5, not this study.

## Required analysis

- Overall and four-family F1 versus the encode stop.
- Action counts by rule id.
- On `dev140` only: whether any encode-exact letter/family pair
  becomes non-exact.
- Holdout: aggregates only.

## Artifact

`experiments/exectv2_rule_select_after_llm_encode_20260822/{split}/comparison.json`

Holdout writes comparison only. No scored row file.

## Stop rule

Answer with the two-split aggregates. Do not retune Select rules.
Do not overwrite the cited ExECT five-cell table in this cut. Cited
`test60` select stops on the living extract are in
[Gemini inventory cells 3–5](exect_gemini_inventory_cells_3_5_protocol_2026-08-23.md)
and cell 2 in
[both-extract on inventory](exect_both_extract_on_inventory_protocol_2026-08-23.md).

## Claim boundary

ExECT cell 4 exists as a frozen no-call replay, promoted into the
cited five role rows (4-family micro F1 select stop). Not the
six-model roster row (cell 3). Not a six-model result.
`exect_llm_pre_post` is both-extract on the living extract; the
retired Compact filtered extract is `exect_llm_extract_filtered`.
A living producer raw F1 is not LLM extract.
