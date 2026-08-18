# Paper experiments

Tracked machine results for the paper comparison. Everyday dumps stay
in gitignored `experiments/`.

Claim wording: [`docs/paper/claims.md`](../docs/paper/claims.md).
Methods: [`docs/paper/methods.md`](../docs/paper/methods.md).
Roster: [`roster.json`](roster.json). Inventory: [`inventory.json`](inventory.json).

| Path | What it is |
| --- | --- |
| `exect/exect_llm_with_rules/` | Cited ExECT hybrid (Compact; cite hybrid F1). |
| `exect/exect_llm_only/` | Cited ExECT LLM-only (standalone Compact; cite raw F1). |
| `exect/dev140_panel.json` | Rectangular living six-model ExECT Compact `dev140` index for the frontend |
| `exect/exect_rules/` | E5 rules-only headlines |
| `comparators/exect_full_ledger/` | Full-ledger control raws (named comparator only; not a headline method) |
| `gan/gan_llm_only/` | Cited Gan LLM-only |
| `gan/gan_llm_with_rules/` | Cited Gan hybrid (cleaned request) |
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
- ExECT scores: `GET /paper/exect/dev140/{slug}/scored`

Join Gan on `source_row_index`. Join ExECT on `letter_id`. Promote a
finished living replay file with:

```bash
python -m clinical_extraction.paper promote-gan --method gan_llm_only --model grok46 --split test450
python -m clinical_extraction.paper promote-exect --method exect_llm_with_rules --model qwen38_27b --split test60
python -m clinical_extraction.paper promote-exect --method exect_llm_only --model gpt56luna --split dev140
```

`/exectv2/runs` is the July explorer payload (Sol + Qwen 3.6). The
living Compact panel is `/paper/exect/dev140`.

Present in the living Gan panel now: Grok, Luna, and Gemini, both
methods. Pending: DeepSeek, Qwen, and living Gemma.

Present in the living ExECT panel now: Grok, Luna, Gemini, DeepSeek,
and Gemma. Pending: Qwen 3.8.

Still missing elsewhere:

- Qwen 3.8 Compact hybrid and standalone LLM-only on `dev140` / `test60`
- Cleaned Gan hybrid and living Gan LLM-only for DeepSeek, Qwen, and
  living Gemma; Luna and Gemini Gan `test450` exist in holdout
  scratch and are not yet promoted
