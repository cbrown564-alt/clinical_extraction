# Paper experiments

Tracked machine results for the paper comparison. Everyday dumps stay
in gitignored `experiments/`.

Headline tables are Gemini five-cell grids (rules, LLM, or both at
extract / encode / select). The cited score is the select stop. The
six-model comparison uses cell 3 only (LLM extract, rules encode, rules
select) on both Gan and ExECT. Gan cell-3 extract is
`gan_llm_extract`; ExECT cell-3 extract is
`exect_llm_only`. ExECT cell 4 (LLM encode then rules select) is the
Gemini-only peak, not the roster row.

Claim wording: [`docs/paper/claims.md`](../docs/paper/claims.md).
Methods: [`docs/paper/methods.md`](../docs/paper/methods.md).
Roster: [`roster.json`](roster.json). Inventory: [`inventory.json`](inventory.json).

## Cited cells

| Path | Role |
| --- | --- |
| `gan/five_cell_grid/` | Gemini Gan five-cell holdout grid |
| `exect/five_cell_grid/` | Gemini ExECT five-cell holdout grid |
| `exect/exect_llm_only/` | ExECT cell-3 extract raw; rungs 2–4 replay this raw for stage ablations |
| `exect/exect_llm_encode/` | ExECT cell-4 LLM encode. Gemini only, `dev140` and aggregate-only `test60` |
| `exect/exect_rules/` | ExECT rules baseline (cell 1) |
| `gan/rungs/` | Gan extract / encode / select replay from cell-3 and source-near raws |
| `exect/rungs/` | ExECT extract / encode / select replay from `exect_llm_only` raw |

## Historical / on disk (not headline)

| Path | What it is |
| --- | --- |
| `gan/gan_llm_only/` | Gan LLM-only baseline. Not a results column |
| `gan/gan_llm_extract_raw/` | Source-near Gan ablation (source wording vs form alignment) |
| `gan/gan_llm_pre_post/` | No-forms both-extract ablation. Not a headline column |
| `exect/exect_llm_pre_post/` | Historical two-method hybrid. `exect_llm_with_rules` is a live alias only |
| `gan/gan_llm_encode/` | Gan later-stage LLM encode. Gemini only |
| `gan/gan_llm_select/` | Gan later-stage LLM select. Gemini only |
| `exect/exect_llm_select/` | ExECT later-stage LLM select. Gemini only |
| `current_stack/` | Historical Full-ledger / enveloped-Gan fills |
| `gan/dev750_panel.json` | Frontend cell-3 development index (rules / extract / encode / select). Not `gan_llm_only` or `gan_llm_extract_raw` |
| `exect/dev140_panel.json` | Frontend cell-3 development index (rules / extract / encode / select on `exect_llm_only`). Not `exect_llm_pre_post` |

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
python -m clinical_extraction.paper promote-exect --method exect_llm_only --model grok46 --split test60
```

`/exectv2/runs` is the July explorer payload (Sol + Qwen 3.6). Not
the cited comparison.

Present for cell-3 roster: Grok, Luna, Gemini on both tasks (partial
holdout). Pending: Qwen, Gemma, remaining DeepSeek holdout fills.
See [`inventory.json`](inventory.json).
