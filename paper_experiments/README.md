# Paper experiments

Tracked machine results for the paper comparison. Everyday dumps stay
in gitignored `experiments/`.

Claim wording: [`docs/paper/claims.md`](../docs/paper/claims.md).
Methods: [`docs/paper/methods.md`](../docs/paper/methods.md).
Roster: [`roster.json`](roster.json). Inventory: [`inventory.json`](inventory.json).

| Path | What it is |
| --- | --- |
| `exect/exect_llm_pre_post/` | ExECT rung 5 (cite hybrid F1). `exect_llm_with_rules` is the live alias. |
| `exect/exect_llm_only/` | ExECT LLM only (cite raw F1). |
| `exect/dev140_panel.json` | Rectangular living six-model ExECT `dev140` index for the frontend |
| `exect/exect_rules/` | ExECT rules headlines |
| `gan/gan_llm_only/` | Existing Gan LLM-only cells. Not a results column |
| `gan/gan_llm_with_rules/` | Gan rung 4 (cleaned request). Living scores predate the omitted-`kind` schema fill; a later six-model no-call reparse is listed in `inventory.json` `deferred`. |
| `gan/gan_llm_pre_post/` | Gan Rules then LLM. Gemini, Grok, and Luna on `dev750` and `test450`. Cite Gemini. Stage scores are extract / encode / select on this raw. |
| `gan/gan_llm_encode/` | Gan later-stage LLM encode. Gemini only, `dev750` and aggregate-only `test450`. |
| `gan/gan_llm_select/` | Gan later-stage LLM select. Gemini only, `dev750` and aggregate-only `test450`. |
| `gan/rungs/` | Extract / encode / select replay of the `gan_llm_with_rules` raw (LLM then rules). Development may keep row files. `test450` writes `comparison.json` aggregates only. |
| `exect/rungs/` | Replay of rungs 1–4 from `exect_llm_only` raw. Development may keep row files. `test60` writes `comparison.json` aggregates only. |
| `gan/dev750_panel.json` | Rectangular living six-model Gan `dev750` index for the frontend |
| `current_stack/` | Historical Full-ledger / enveloped-Gan fills. Not the cited Gan hybrid. |

Holdout raws keep only replay keys. Do not inspect `test450` or
`test60` rows.

Living Gan `dev750` effort is hosted `low` (DeepSeek thinking-on /
provider default; local models have no effort knob). Medium/high and
thinking-off reruns stay under `experiments/paper/` and are not
this panel.

Frontend pull:

- Gan notes: `GET /datasets/gan2026/letters`
- Gan panel: `GET /paper/gan/dev750`
- Gan scores: `GET /paper/gan/dev750/{gan_llm_only|gan_llm_with_rules}/{slug}/scored`
- ExECT notes: `GET /datasets/exectv2/letters`
- ExECT panel: `GET /paper/exect/dev140`
- ExECT scores: `GET /paper/exect/dev140/{exect_llm_only|exect_llm_pre_post|llm_extract|llm_encode|llm_select}/{slug}/scored`

Join Gan on `source_row_index`. Join ExECT on `letter_id`. Promote a
finished living replay file with:

```bash
python -m clinical_extraction.paper promote-gan --method gan_llm_only --model grok46 --split test450
python -m clinical_extraction.paper promote-exect --method exect_llm_pre_post --model qwen38_27b --split test60
python -m clinical_extraction.paper promote-exect --method exect_llm_only --model gpt56luna --split dev140
```

`/exectv2/runs` is the July explorer payload (Sol + Qwen 3.6). The
living ExECT panel is `/paper/exect/dev140`.

Present in the living Gan panel now: Grok, Luna, and Gemini, both
methods. Pending: DeepSeek, Qwen, and living Gemma.

Present in the living ExECT panel now: Grok, Luna, Gemini, DeepSeek,
and Gemma. Pending: Qwen 3.8.

Still missing elsewhere:

- Qwen 3.8 ExECT LLM with rules and ExECT LLM only on `dev140` / `test60`
- ExECT LLM only for DeepSeek and Gemma
- Cleaned Gan hybrid and living Gan LLM-only for DeepSeek, Qwen, and
  living Gemma. Luna Gan hybrid and pre-post `test450` are promoted.
