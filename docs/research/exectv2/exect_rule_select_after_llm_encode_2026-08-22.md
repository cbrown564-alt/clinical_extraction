# ExECT rule-select-after-LLM-encode

Date: 2026-08-22
Status: promoted into the cited ExECT five-cell table
Owner: [protocol](exect_rule_select_after_llm_encode_protocol_2026-08-22.md)
Artifact: `experiments/exectv2_rule_select_after_llm_encode_20260822/{split}/comparison.json`

## Paper table

ExECT uses the same five role rows as Gan. Each of extract, encode,
and select is rules, LLM, or both. The cited score is the select
stop. This study is **cell 4** (LLM / LLM / rules): saved
`exect_llm_only`, later-stage `exect_llm_encode`, then accepted
Select. It is the peak Gemini inventory row (holdout **0.82**). It
is **not** the six-model row—that is cell 3 (`exect_llm_only`, rule
encode, rule select). Later-stage encode and select stay Gemini only.
`exect_llm_with_rules` is the live alias of `exect_llm_pre_post`
(both extract); it is not a second headline method. A living producer
raw F1 is not LLM extract.

## Answer

ExECT cell 4 exists. On the saved Gemini later-stage encode ledger,
accepted Select rules raise exact clinical-fact F1 from **0.8176 to
0.8288** on `dev140` and from **0.8059 to 0.8173** on locked `test60`.
That holdout select stop is above later-stage LLM select (**0.7954**)
and 0.0012 above living rungs cell 3 select (**0.8161**). The
retired encode/select-split replay of that cell 3 stop was
**0.7869**.

No new model calls. Holdout rows were not inspected.

## Protocol

Gemini 3.7 Flash. Extract is saved `exect_llm_only`. Encode is saved
`exect_llm_encode`. Select is `ACCEPTED_SELECT_RULE_IDS` on those
encoded mentions, using extract mentions as the source ledger.

## Component result

Exact `clinical_headline_unit_keys`.

| Split | Encode stop | Cell 4 select | Select actions |
| --- | ---: | ---: | ---: |
| `dev140` | 0.8176 | **0.8288** | 18 |
| `test60` | 0.8059 | **0.8173** | 11 |

Locked `test60` family F1, encode → select: Diagnosis 0.73 → 0.76;
Investigations 0.94 → 0.94; Prescription 0.92 → 0.92; SeizureFrequency
0.71 → 0.71.

## Claim boundary

Holdout evidence for this frozen replay. Aggregate only. Promoted as
cell 4 in the cited five role rows (select stop **0.82**). Not the
six-model roster row (cell 3). Not a six-model result. Do not inspect
`test60` rows. Do not retune Select rules from this total.

## Next

Done: `claims.md`, `README.md`, and
`paper_experiments/exect/five_cell_grid/gemini37flash/test60/comparison.json`
cite this stop.
