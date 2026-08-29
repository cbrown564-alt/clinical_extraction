# Gan five-cell prefix grid

Date: 2026-08-22
Revised: 2026-08-28 (living primary is Purist micro-F1; class report + Qwen COT compare)
Status: cited
Owner: [protocol](gan_five_cell_grid_protocol_2026-08-22.md)
Paper artifact: `paper_experiments/gan/five_cell_grid/gemini37flash/test450/comparison.json`

Cell 3 (LLM / rules / rules) is the six-model row: `gan_llm_extract`,
`gan_rules_encode`, rule select (**0.83** holdout). The source-near
ablation `gan_llm_extract_raw` stays on disk; it is not the paper
primary.

## Answer

The cited Gemini table is five role combinations. Each of find,
encode, and select is **rules**, **LLM**, or **both**. The headline
score is the select stop (the submitted label). Find and encode
stops are prior-stage ablations. `gan_llm_only` is not a results column.

On locked `test450`, LLM find plus codebook rule encode plus rule
select is the strongest row (**0.83**). Rule select without that
encode is **0.82**, matching both-then-rules. LLM select is **0.79**.
Standalone rules are **0.71** (321/450; living gold). The historical selected-evidence
encoder on the same extract is an ablation (encode 0.77, select 0.80).

## Locked `test450` headline (select stop, aggregate only)

| Find | Encode | Select | Purist micro-F1 |
| --- | --- | --- | ---: |
| rules | rules | rules | 0.71 |
| both | rules | rules | 0.82 |
| LLM | rules | rules | **0.83** |
| LLM | LLM | rules | 0.82 |
| LLM | LLM | LLM | 0.79 |

`both` find is `gan_llm_and_rules_extract`. LLM find is
`gan_llm_extract`. LLM encode means the find already
wrote the codebook form (no rule encode). LLM select is
`gan_llm_select_from_extract`. The LLM-then-rules encode is
`gan_rules_encode`.

## Prior-stage ablation (same rows)

| Find | Encode | Select | Find stop | Encode stop |
| --- | --- | --- | ---: | ---: |
| rules | rules | rules | 0.71 | 0.71 |
| both | rules | rules | 0.82 | 0.80 |
| LLM | rules | rules | 0.79 | 0.80 |
| LLM | LLM | rules | 0.79 | 0.79 |
| LLM | LLM | LLM | 0.79 | 0.79 |

## `dev750` select (`gan_rules_encode` on the LLM-then-rules row)

| Find | Encode | Select | Purist micro-F1 |
| --- | --- | --- | ---: |
| rules | rules | rules | 0.89 |
| both | rules | rules | 0.89 |
| LLM | rules | rules | 0.86 |
| LLM | LLM | rules | 0.85 |
| LLM | LLM | LLM | 0.79 |

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
select is 373/450 (0.83).

## Claim boundary

Frozen-prompt holdout aggregates. Cited in `claims.md` and
`README.md`. Headline is the select stop.
Class report: [gan_test450_classification_report_2026-08-28.md](gan_test450_classification_report_2026-08-28.md).
Equivalent Qwen COT synthetic compare:
[gan_gemini_vs_qwen25_14b_cot_synthetic_2026-08-28.md](gan_gemini_vs_qwen25_14b_cot_synthetic_2026-08-28.md). Do not retune
`label_forms`. Do not inspect holdout rows.
