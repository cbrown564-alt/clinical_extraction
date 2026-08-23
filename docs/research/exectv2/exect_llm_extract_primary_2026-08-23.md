# ExECT inventory extract becomes the primary cell-3 method

Date: 2026-08-23
Status: Gemini cells 3–5 promoted 2026-08-23; roster fills continue
Owner: this file
Track: [inventory](exect_llm_inventory_track.md)

## Primary question

Can ExECT cell 3 use the recall-first inventory extract and inventory
F1 as the cited method and scorer, leaving filtering and de-duplication
to select, with the older Compact extract kept only as a Gemini
ablation?

## Why this matters

The inventory prompt lists stated diagnoses, heading types, and
frequency or control statements without most-specific collapse or
scoring-time de-duplication. Select then filters. That matches the
paper's extract / encode / select split more cleanly than asking the
extract call to pre-filter. The older Compact extract
(`exect_llm_only`) becomes `exect_llm_extract_filtered`, the same
secondary role as `gan_llm_extract_raw` beside `gan_llm_extract`.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Splits | `dev140` (review permitted); `test60` aggregate-only |
| Candidate | `exect_llm_extract` (was `exect_llm_inventory`) |
| Comparator / ablation | Gemini `exect_llm_extract_filtered` (was `exect_llm_only`) |
| Scorer | `clinical_inventory_unit_keys` |
| Cell 3 roster this machine | Luna, Grok, DeepSeek on both splits |
| Cell 3 roster other device | Qwen, Gemma |
| Cells 4–5 | Gemini only, on the new extract. Encode prompt unchanged. Select prompt adjusted for the larger extract. |

Do not inspect `test60` rows. Do not retune from holdout.

## Minimal change

Rename the live method ids. Keep old prompt strings as read aliases.
Reuse the finished Gemini inventory extracts. Do not re-run Luna,
Grok, or DeepSeek on the filtered extract.

## Stop rule

Answer when the new method id is the living cell-3 extract, inventory
F1 is the cited scorer, the filtered Gemini cell is an ablation only,
and the named live cells have started or finished under those names.

## Claim boundary

Development scores may be inspected. Holdout is aggregate-only. Do
not treat unfinished roster fills as cited five-cell numbers.
