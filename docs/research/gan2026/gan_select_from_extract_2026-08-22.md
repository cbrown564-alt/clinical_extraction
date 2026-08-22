# Gan select-from-extract result

Date: 2026-08-22
Status: development answer
Owner: [protocol](gan_select_from_extract_protocol_2026-08-22.md)
Work cell: `experiments/paper/gan_llm_select_from_extract/gemini37flash/gan_llm_extract_label_forms/dev750/`
Encode mechanism: [encode on codebook extract](gan_encode_on_codebook_extract_2026-08-22.md)

## Answer

Gemini select can read the codebook extract directly. On `dev750`
that cell is **0.79**. Extract is 0.78. Select after later-stage
encode is 0.79. Skipping encode costs two letters at select and
avoids the 0.69 encode column.

## Protocol

Gemini 3.7 Flash, Gan `dev750`, Purist. Same select prompt. Event
labels from extract (`final_label` on the pick, `raw_value` on the
rest). No encode cell. No hybrid post-stack. `test450` was not
loaded. Existing `gan_llm_select` was not overwritten.

## Component result

| Cell | Purist |
| --- | ---: |
| Codebook extract | 0.78 |
| Later-stage encode (same ledger) | 0.69 |
| Select after that encode | 0.79 |
| **Select from extract** | **0.79** |
| Rule encode / select on that raw | 0.80 / 0.86 |

Select-from-extract vs extract: 7 rescues, 2 harms, 10 pick changes.
Vs select-after-encode: 3 letters only the skip-encode cell hits, 5
only the encode-then-select cell hits.

## Attribution

Later-stage encode does not feed select a better ledger. It discards
extract `final_label` and rewrites from `raw_value` without the
letter, which is why encode is 517. Rule encode keeps that
`final_label` and still adds 17 letters.

## Claim boundary

Development candidate. Not holdout. Not promoted. Do not retune
`label_forms`.
