# One-call responses with cell-3 rules

Date: 2026-09-10
Status: completed; protocol fixed before replay

## Question and fixed comparison

What happens when the existing Gan cell-3 codebook encoder and rule selector
process the saved `gan_llm_extract_encode_select` responses? Compare the same
responses under `raw_model`, the previously reported `llm_encode` repair,
`gan_rules_encode`, and `llm_select_after_codebook`. The last mode includes
codebook encoding and rule selection; it is not an additional model call.

Use all six local models from remote commit
`9a2ce3ffda69059f6575008d53796d724cc1cc23` and the three hosted models in local
`20260905` run directories (Gemini, Luna, DeepSeek). Exclude the older Gemini
run rather than selecting between runs by score. No Grok response set is available.

## Frozen procedure and boundaries

- Dataset: Gan 2026, `gan2026_split_v1`, locked `test450`, all 450 records.
- Row policy: aggregate only. The script may read sealed responses and records
  internally; do not display or save identifiers, predictions, examples or failures.
- Code: current checkout at protocol creation; record commit and source hashes.
  No prompt, parser, semantic rule, scorer or split changes are permitted.
- Primary metric: Purist accuracy; secondary: Pragmatic accuracy, parse failures,
  exact selected-evidence counts, and aggregate correct/wrong transitions.
- Preserve saved outputs. Assert exact split coverage and reproduce the saved
  raw-model Purist total before accepting each result.
- No independent deterministic extractor or safety floor is added. Any changed
  answer belongs to the deterministic post-processing comparison.
- Stop after one fixed aggregate replay and verification. Do not tune from it.

This is a requested diagnostic on an already evaluated holdout, not a fresh
independent confirmation, clinical validation, or replacement for the cited
cell-3 prompt. Subproblem attribution and failure examples remain unavailable
under aggregate-only inspection. There are no paid calls.

Runner: `scripts/benchmarks/replay_one_call_cell3.py`.
Output: `results/letter-benchmarks/gan/one_call_cell3_replay/2026-09-10/comparison.json`.

## Results

All totals below are Purist-correct out of 450. Codebook encode is
`gan_rules_encode`, not the earlier `llm_encode` diagnostic.

| Model | One-call answer | Codebook encode | Encode + rule select | Rescues / harms versus one-call |
| --- | ---: | ---: | ---: | ---: |
| Gemini 3.7 Flash | 384 | 387 | 392 | 14 / 6 |
| DeepSeek V4 Flash | 353 | 375 | 373 | 25 / 5 |
| GPT-5.6 Luna | 344 | 369 | 372 | 33 / 5 |
| Qwen 3.8 27B | 333 | 343 | 356 | 25 / 2 |
| Qwen 3.6 35B | 297 | 310 | 322 | 29 / 4 |
| Gemma 4 26B | 286 | 310 | 330 | 46 / 2 |
| Qwen 3.5 9B | 237 | 256 | 265 | 30 / 2 |
| Qwen 2.5 14B | 231 | 233 | 250 | 19 / 0 |
| Llama 3.1 8B | 139 | 144 | 151 | 15 / 3 |

The complete stack improves net accuracy over the one-call answer for each
model. Selection after codebook encoding adds correct answers on balance for
eight models, but loses two for DeepSeek. The older `llm_encode` repair remains
better than the cell-3 stack for Qwen 3.5 (286 versus 265) and Llama (174 versus
151). These are different deterministic policies, not successive stops.

Parsing failures and exact selected-evidence substring counts are unchanged
across modes for each model. Substring presence does not establish clinical
support for a changed answer. No clinical-subproblem, hidden-family or row-level
mechanism claim is made, and no further rule adjustment follows this result.

Verification: all nine saved raw-model and prior `llm_encode` Purist totals
reproduce exactly; each source covers the exact 450-record split once. The
focused codebook/replay tests pass (18 tests). The runner passes Ruff. Production
code is unchanged; broad pytest/mypy were not rerun for this bounded replay.
