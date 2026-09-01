# Gan five-cell prefix grid

Date: 2026-08-22
Revised: 2026-08-31 (cited LLM select 383/450; living source-near rules find 190/450; encode 284; select 325)
Status: cited
Owner: [protocol](gan_five_cell_grid_protocol_2026-08-22.md)
Paper artifact: `paper_experiments/gan/five_cell_grid/gemini37flash/test450/comparison.json`

Cell 3 (LLM / rules / rules) is the six-model row: `gan_llm_extract`,
`gan_rules_encode`, rule select (**0.86** holdout). The source-near
ablation `gan_llm_extract_raw` stays on disk; it is not the paper
primary.

## Answer

The cited Gemini table is five role combinations. Each of find,
encode, and select is **rules**, **LLM**, or **both**. The headline
score is the select stop (the submitted label). Find and encode
stops are prior-stage ablations. `gan_llm_only` is not a results column.

On locked `test450`, LLM find plus codebook rule encode plus rule
select is the strongest row (**0.86**). Rule select without that
encode is **0.85**. Both-then-rules is **0.82**. LLM select is **0.85**.
Standalone rules are **0.72** (325/450; promoted three-stage
program). Living rules find is source-near **190/450**; encode of
that pick is **284/450**. Phase D **292 / 292** is fused codebook
instrumentation.
The historical selected-evidence
encoder on the same extract is an ablation (encode 0.77, select 0.80).

## Locked `test450` headline (select stop, aggregate only)

| Find | Encode | Select | Purist micro-F1 |
| --- | --- | --- | ---: |
| rules | rules | rules | 0.72 |
| both | rules | rules | 0.82 |
| LLM | rules | rules | **0.86** |
| LLM | LLM | rules | 0.85 |
| LLM | LLM | LLM | 0.85 |

`both` find is `gan_llm_and_rules_extract`. Cited LLM extract is
`gan_llm_extract` (bundled find-and-encode). Living rules find is
source-near. LLM encode in the table means that extract already
wrote the codebook form (no second rule encode). LLM select is
`gan_llm_select_from_extract` with the living policy-example
prompt. The LLM-then-rules encode is
`gan_rules_encode`.

## Prior-stage ablation (same rows)

Rules find is living source-near (**190/450 = 0.42**). Encode is
**284/450 = 0.63**. Phase D 0.65 / 0.65 was fused codebook.

| Find | Encode | Select | Find stop | Encode stop |
| --- | --- | --- | ---: | ---: |
| rules | rules | rules | 0.42 | 0.63 |
| both | rules | rules | 0.82 | 0.80 |
| LLM | rules | rules | 0.79 | 0.80 |
| LLM | LLM | rules | 0.79 | 0.79 |
| LLM | LLM | LLM | 0.79 | 0.79 |

## `dev750` select (`gan_rules_encode` on the LLM-then-rules row)

| Find | Encode | Select | Purist micro-F1 |
| --- | --- | --- | ---: |
| rules | rules | rules | 0.92 |
| both | rules | rules | 0.89 |
| LLM | rules | rules | 0.87 |
| LLM | LLM | rules | 0.85 |
| LLM | LLM | LLM | 0.85 |

Holdout rows were not inspected. The old `gan_llm_extract_raw` grid
is the source-near ablation.

## Post-grid development diagnosis

The historical renderer re-derives an answer from evidence after the
LLM has already attempted a codebook label. That is why it is an
ablation, not the cited encode column. The codebook-preserving
candidate raises development Purist from 0.8027 to 0.8093, changes 27
rows with 22 Purist rescues and no observed Purist or exact-label
harms, and keeps semantic select separate. See the
[protocol](gan_codebook_encode_rule_development_protocol_2026-08-22.md)
and
[development result](gan_codebook_encode_rule_development_2026-08-22.md).

The frozen holdout of that candidate is the cited LLM-then-rules row:
[codebook-encode holdout](gan_codebook_encode_holdout_2026-08-22.md).
On `test450` codebook encode is 359/450 (0.80) and codebook then
select was 373/450 (0.83). Living cited select is now 387/450
(0.86) after the `last_event_well_since` promotion.

## Claim boundary

Frozen-prompt holdout aggregates. Cited in `claims.md` and
`README.md`. Headline is the select stop.
Class report: [gan_test450_classification_report_2026-08-28.md](gan_test450_classification_report_2026-08-28.md).
Equivalent Qwen COT synthetic compare:
[gan_gemini_vs_qwen25_14b_cot_synthetic_2026-08-28.md](gan_gemini_vs_qwen25_14b_cot_synthetic_2026-08-28.md). Do not retune
`label_forms`. Do not inspect holdout rows.
