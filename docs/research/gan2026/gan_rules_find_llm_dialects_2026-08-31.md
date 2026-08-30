# Results: Rules find dialects for LLM extract comparison

Date: 2026-08-31
Protocol: [dialect protocol](gan_rules_find_llm_dialects_protocol_2026-08-31.md)
Artifact: `experiments/gan2026_rules_find_llm_dialects_20260831/dev750_summary.json`
Split: `dev750` only; `test450` never loaded. Zero model calls.
Scorer: Purist via `score_label` on the document-order find pick.

## Decision

The best representation for a meaningful Purist comparison to LLM find
is the **codebook `final_label`**. That is what `gan_llm_extract`
writes and what `living_gan_stages` scores after a `raw_model` parse.
Atomic slot tags (`four/day`) and source-near phrases (`four per day`)
fail `label_to_frequency_record` the same way letter wording fails it.

Atomic `FindFact` stays the source of truth. Two named projections
remap those slots:

| Dialect | Maps to | Rules render |
| --- | --- | --- |
| `gan_llm_extract` | cited codebook find | `encode_find_fact` |
| `gan_llm_extract_raw` | source-near find | found tokens as a phrase (`four per day`, `5 per mo`, `daily`) |

`project_find_event` fills the slim extract fields: `kind`,
`raw_value` (evidence when present), and dialect `final_label`.

## Gates (all met)

- **D1 / D2:** fixtures pin codebook = `encode_find_fact` and
  source-near ≠ codebook on word-number, compact, and adjective rates.
- **D3:** default select **669/750**, identical to `run_record`.
  Promoted select **691/750**.
- **D4:** codebook-dialect find equals encode on the same pick
  (label disagree **0**; Purist **577** default / **599** promoted).

Cited five-cell stops stay **292 / 292 / 325**.

## Stage stops on the same pick

| Arm | Atomic find | Source-near (`gan_llm_extract_raw`) | Codebook (`gan_llm_extract`) | Encode | Select |
| --- | ---: | ---: | ---: | ---: | ---: |
| Default | 109 | 386 | **577** | 577 | 669 |
| Promoted Phase C | 128 | 408 | **599** | 599 | 691 |

Source-near Purist is the dialect tax: the same fact, scored before
codebook token mapping. Use the codebook column next to
`gan_llm_extract` find. Use the source-near column next to
`gan_llm_extract_raw` find when the question is form, not clinical
pick.

Gemini `gan_llm_extract` find on `dev750` is scored on codebook
`final_label` (extract summary 585 is the living select stop, not
this pick policy). Do not treat 577 as a five-cell extract cell.
Rules find here is document-order first wide-ledger candidate,
including Select-dropped rows.

## Claim boundary

Development instrumentation. Not a cited-row change. Not holdout
evidence. The codebook dialect is the comparison form; atomic tags
remain diagnostic.
