# DeepSeek unknown prompt candidate draft notes

Date: 2026-07-31  
Status: implemented; UNK-slice pilot complete; **stopped (negative)** — do not scale to 750  
Parent: [unknown-competence protocol](gan2026_deepseek_unknown_competence_protocol_2026-07-31.md)  
Phase 2 run protocol: [gan2026_deepseek_unknown_prompt_dev750_protocol_2026-07-31.md](gan2026_deepseek_unknown_prompt_dev750_protocol_2026-07-31.md)  
Pilot compare: [experiments/gan2026_deepseek_unknown_heavy_slice_u_vs_a_20260731.json](../../../experiments/gan2026_deepseek_unknown_heavy_slice_u_vs_a_20260731.json)

## What changed

The candidate keeps the frozen v0.5 event and selection schemas. Only
model-facing instructions were added before the final "return one JSON object"
line.

| ID | Prompt identity | Added instructions | Role |
| --- | --- | ---: | --- |
| A | `gan2026_hybrid_structured_events_v0.5` | 0 | Hosted DeepSeek Phase 0 control (reuse retained raws) |
| U | `gan2026_hybrid_structured_events_v0.8_deepseek_unknown` | 6 | Hosted DeepSeek unknown-selection candidate |

Default `PROMPT_VERSION` remains v0.5. Candidate U is selectable only by
explicit prompt version and must not replace the frozen six-model panel.

## Why the extra text is allowed

Controlled prompt-shape experiment for the DeepSeek unknown-competence thread.
Phase 0 hosted LLM-only misses collaboration gates (UNK acc 0.765; 11 false
seizure-free and 29 gold-UNK misses at the model boundary; many non-UNK rows
collapse clear counts to vague `multiple …` labels that score as the UNK
sentinel). The added lines target those mechanisms only.

## U targets from Phase 0 DeepSeek LLM-only residuals

- Quiet spell / “since date” without clear current seizure-free → `unknown`,
  not `seizure_free`.
- Possible or single questionable events → `unknown`.
- Do not invent numeric rates from vague or incomplete frequency language.
- Keep clear countable rates; do not replace them with `multiple per …`.
- Incomplete cluster (per-cluster count without spacing) → `unknown` / unknown
  with per-cluster side, not a smooth invented rate.
- Dated countable windows stay frequency evidence (not `no_reference`).

## Plain-language audit

| Check | Result |
| --- | --- |
| Rendered prompt inspected | Yes (`build_prompt_input` for U) |
| Model-facing text is plain language | Yes; ordinary verbs and clinical terms |
| Internal metadata separated | Research ids stay in code/docs; instructions omit gold, gates, and residual taxonomy |
| Non-obvious schema fields described | Unchanged from v0.5 |
| Jargon removed or defined | No new `source-near`, `scorer`, `gate`, or experiment jargon in the added lines |
| Prompt length matches purpose | Intentionally longer than v0.5 for this controlled study |
| Controlled-experiment deviation justified | Yes, above |

Inherited v0.5 wording such as `source-near` remains in the shared base lines
because the schema and baseline instruction set are frozen for A/U
comparability.

## Snapshot

Pinned by `tests/snapshots/prompt_contracts/gan2026__hybrid_structured_events_v0.8_deepseek_unknown.txt`
via `tests/test_prompt_contract_snapshots.py`.

## Next action

None for U. Pilot was insufficient (+2 Purist on UNK slice; LLM-only UNK
accuracy worse). Full-750 aborted. See thread for the next-component decision.
