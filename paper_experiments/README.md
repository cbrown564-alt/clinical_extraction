# Paper experiments

Tracked machine results for the paper comparison. Everyday dumps stay
in gitignored `experiments/`.

Headline tables are Gemini five-cell grids (rules, LLM, or both at
recognise / encode / select). The cited score is the select stop. The
six-model comparison uses cell 3 only (LLM recognise, rules encode, rules
select) on both Gan and ExECT. Gan cell-3 recognise is
`gan_llm_extract`; ExECT cell-3 recognise is
`exect_llm_extract`. ExECT cell 3 is the roster row and the Gemini
peak. Cell 4 (LLM encode then rule select) stays
Gemini-only. All five ExECT rows use 4-family micro F1.

Claim wording: [`docs/paper/claims.md`](../docs/paper/claims.md).
Methods: [`docs/paper/methods.md`](../docs/paper/methods.md).
Roster: [`roster.json`](roster.json). Inventory: [`inventory.json`](inventory.json).

## Cited cells

| Path | Role |
| --- | --- |
| `gan/five_cell_grid/` | Gemini Gan five-cell holdout grid |
| `exect/five_cell_grid/` | Gemini ExECT five-cell holdout grid (4-family micro F1; cell 3 peak). Owner: [both-recognise on inventory](../docs/research/exectv2/exect_both_extract_on_inventory_protocol_2026-08-23.md) |
| `exect/exect_llm_extract/` | ExECT cell-3 inventory recognise raw; cells 3–5 replay this raw |
| `exect/exect_llm_encode/` | ExECT cell-4 LLM encode. Gemini only, `dev140` and aggregate-only `test60` |
| `exect/exect_llm_select/` | ExECT cell-5 LLM select. Gemini only, `dev140` and aggregate-only `test60` |
| `exect/exect_rule_select_after_llm_encode/` | ExECT cell-4 inventory Select on the encode ledger |
| `exect/exect_llm_pre_post/` | ExECT cell-2 both-recognise. Gemini is living recognise plus suggested candidates |
| `exect/exect_rules/` | ExECT rules baseline (cell 1) |
| `gan/rungs/` | Gan recognise / encode / select replay from cell-3 and source-near raws |
| `exect/rungs/` | Historical ExECT recognise / encode / select replay |

## Historical / on disk (not headline)

| Path | What it is |
| --- | --- |
| `gan/gan_llm_only/` | Gan LLM-only baseline. Not a results column |
| `gan/gan_llm_extract_raw/` | Source-near Gan ablation (source wording vs form alignment) |
| `gan/gan_llm_pre_post/` | No-forms both-recognise ablation. Not a headline column |
| `exect/exect_llm_pre_post/` (non-Gemini) | Historical Compact both-recognise. `exect_llm_with_rules` is a live alias only |
| `gan/gan_llm_encode/` | Gan later-stage LLM encode. Gemini only |
| `gan/gan_llm_select/` | Gan later-stage LLM select. Gemini only |
| `current_stack/` | Historical Full-ledger / enveloped-Gan fills |
| `gan/dev750_panel.json` | Frontend cell-3 development index (rules / recognise / encode / select). Not `gan_llm_only` or `gan_llm_extract_raw` |
| `exect/dev140_panel.json` | Frontend cell-3 development index. Still the previous Compact recognise until the panel is rebuilt from the promoted inventory recognise. Not `exect_llm_pre_post` |

Holdout raws keep only replay keys. Do not inspect `test450` or
`test60` rows.

Gemini thinking low / medium / high ablations on cell 3 only stay
under `experiments/paper/` and are not this panel.

Frontend pull:

- Gan notes: `GET /datasets/gan2026/letters`
- Gan panel: `GET /paper/gan/dev750`
- ExECT notes: `GET /datasets/exectv2/letters`
- ExECT panel: `GET /paper/exect/dev140`

Promote a finished replay file with:

```bash
python -m clinical_extraction.paper promote-gan --method gan_llm_extract --model gemini37flash --split test450
python -m clinical_extraction.paper promote-exect --method exect_llm_extract --model grok46 --split test60
```

`/exectv2/runs` is the July explorer payload (Sol + Qwen 3.6). Not
the cited comparison.

Present for cell-3 recognise: Gemini on both tasks; Qwen and Gemma
inventory and codebook recognises on both splits. Pending: Grok, Luna,
and DeepSeek `exect_llm_extract`; remaining DeepSeek Gan fills; encode
and select replay for the new local recognise raws. See
[`inventory.json`](inventory.json).
