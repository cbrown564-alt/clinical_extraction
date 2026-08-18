# Paper experiments

Tracked machine results for the paper comparison. Everyday dumps stay
in gitignored `experiments/`.

Claim wording: [`docs/paper/claims.md`](../docs/paper/claims.md).
Methods: [`docs/paper/methods.md`](../docs/paper/methods.md).
Roster: [`roster.json`](roster.json). Inventory: [`inventory.json`](inventory.json).

| Path | What it is |
| --- | --- |
| `exect/exect_llm_with_rules/` | Cited ExECT hybrid (Compact). Same call is ExECT LLM-only (raw). |
| `exect/exect_rules/` | E5 rules-only headlines |
| `comparators/exect_full_ledger/` | Full-ledger control raws |
| `gan/gan_llm_only/` | Cited Gan LLM-only |
| `current_stack/` | Historical Full-ledger / enveloped-Gan fills. Not the cited Gan hybrid. |

Holdout raws keep only replay keys. Do not inspect `test450` or
`test60` rows.

Still missing:

- Grok 4.6 Compact (`exect_llm_with_rules`) `dev140` and `test60`
- Qwen 3.8 Compact (`exect_llm_with_rules`) `dev140` and `test60`
- Cleaned Gan hybrid (`gan_llm_with_rules`) six-model panel
- Grok 4.6 and Qwen 3.8 Gan LLM-only
