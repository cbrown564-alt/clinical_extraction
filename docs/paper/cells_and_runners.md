# Cells and runners

Date: 2026-08-23
Status: current
Owner: this file

The headline table is five role rows. Each of find, encode, and
select is rules, LLM, or both. Live runner names are not the table.

| Cell | Find | Encode | Select | Gan runner / identity | ExECT runner / identity |
| --- | --- | --- | --- | --- | --- |
| 1 | rules | rules | rules | `gan_rules` | `exect_rules` |
| 2 | both | rules | rules | `gan_llm_and_rules_extract` | `exect_llm_pre_post` (living find plus suggested candidates; `exect_llm_with_rules` is the live alias) |
| 3 | LLM | rules | rules | `gan_llm_extract` then `gan_rules_encode` and rule select | `exect_llm_extract` then rule encode and select |
| 4 | LLM | LLM | rules | Same codebook find; select families only (find already wrote the form) | Later-stage `exect_llm_encode`, then inventory Select |
| 5 | LLM | LLM | LLM | `gan_llm_select_from_extract` | Later-stage `exect_llm_select` |

`gan_llm_only` is a live runner. It is not a results column.
`gan_llm_extract` already writes the codebook form: it is bundled
find-and-encode. That is why cell 3 is LLM find plus a second rule
encode. `gan_llm_extract_raw` is find only (source-near). Living
rules find uses that same source-near dialect. The source-near LLM
request is a wording ablation, not cell 3.
`exect_llm_extract_filtered` is the Compact find ablation, Gemini
only.
On Gan, LLM encode in the table means the find already wrote the
codebook form. On ExECT, LLM encode is a second call.

Replay cells 3–5 on ExECT share one `exect_llm_extract` raw. Cell 2 is a
different request. Sealed artifact aliases (`llm_schema`, `llm_format`,
`llm_post`, `hybrid_full_stack`) still load. They are not live cell ids.
