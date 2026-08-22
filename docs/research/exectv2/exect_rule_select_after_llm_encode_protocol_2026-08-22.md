# ExECT rule-select-after-LLM-encode protocol

Date: 2026-08-22
Status: completed 2026-08-22; promoted
Owner: this file

## Primary question

What is the exact clinical-fact F1 of accepted deterministic Select
rules applied to the saved Gemini later-stage encode ledger?

This is ExECT cell 4: LLM extract, LLM encode, rules select. It is
the peak Gemini inventory row, not the six-model roster row (cell 3:
`exect_llm_only`, rule encode, rule select). Gan can fold extract and
encode into one codebook call. ExECT cannot; encode is a second
letter-out call. The missing stop is rule select after that call, not
later-stage LLM select (cell 5). Gemini only.

## Why it matters

The cited ExECT five role rows have later-stage encode (0.81 holdout)
and later-stage select (0.80). They do not yet name the Gan cell-4
analog (LLM / LLM / rules with accepted Select on the encode ledger).
Without this replay the two-task tables do not name the same method.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Model | Gemini 3.7 Flash |
| Extract | saved `exect_llm_only` flatten |
| Encode | saved `exect_llm_encode` joined mentions |
| Select | accepted deterministic Select rule ids |
| Development | `dev140`, review permitted |
| Holdout | `test60`, aggregate only. Do not inspect rows. |
| Calls | none |
| Scorer | exact `clinical_headline_unit_keys` |

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
Do not overwrite the cited ExECT five-cell table in this cut.

## Claim boundary

ExECT cell 4 exists as a frozen no-call replay, promoted into the
cited five role rows (select stop). Not the six-model roster row
(cell 3). Not a six-model result. `exect_llm_with_rules` is the live
alias of `exect_llm_pre_post`; it is not a second headline method. A
living producer raw F1 is not LLM extract.
