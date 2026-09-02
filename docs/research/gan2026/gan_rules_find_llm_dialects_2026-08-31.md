# Results: Rules find dialects for LLM extract comparison

Date: 2026-08-31
Revised: 2026-08-31 (source-near promoted as living rules find)
Protocol: [dialect protocol](gan_rules_find_llm_dialects_protocol_2026-08-31.md)
Artifact: `experiments/gan2026_rules_find_llm_dialects_20260831/dev750_summary.json`
Split: `dev750` only; `test450` never loaded. Zero model calls.
Scorer: Purist via `score_label` on the document-order find pick.

## Decision

Living rules find is the **source-near phrase**
(`gan_llm_extract_raw` dialect). That is find without codebook
writing.

`gan_llm_extract` already writes the allowed codebook form. It is
bundled find-and-encode. Cell 3 is LLM plus rules sharing encode
because that request arrives already encoded; `gan_rules_encode` runs
on the same fact. Comparing rules codebook render to
`gan_llm_extract` `final_label` compares two encode outputs, not two
find outputs.

Atomic `FindFact` stays the source of truth. Named projections:

| Dialect | What it is | Rules render |
| --- | --- | --- |
| `gan_llm_extract_raw` | **Living rules find** | found tokens as a phrase (`four per day`, `5 per mo`, `daily`) |
| `gan_llm_extract` | bundled find-and-encode | `encode_find_fact` |
| atomic | diagnostic slots | `four/day` |

`project_find_event` fills the slim extract fields: `kind`,
`raw_value` (evidence when present), and dialect `final_label`.
`GanStageStops.find_label` is the source-near phrase.

## Gates (all met)

- **D1 / D2:** fixtures pin codebook = `encode_find_fact` and
  source-near ≠ codebook on word-number, compact, and adjective rates.
- **D3:** default select **669/750**, identical to `run_record`.
  Promoted select **691/750**.
- **D4:** codebook projection equals encode on the same pick
  (label disagree **0**; Purist **577** default / **599** promoted).
  That column is encode, not find.

Cited five-cell select stays **325/450**. Living holdout stops are
find **190**, encode **284**, select **325**
([`test450` remasure](gan_rules_source_near_find_test450_2026-08-31.md)).
Phase D **292 / 292** is fused codebook instrumentation.

## Stage stops on the same pick

| Arm | Atomic | **Find** (source-near) | Codebook / encode | Select |
| --- | ---: | ---: | ---: | ---: |
| Default | 109 | **386** | 577 | 669 |
| Promoted Phase C | 128 | **408** | 599 | 691 |

Find 386/408 is the living rules find Purist on `dev750` under the
document-order pick, including Select-dropped rows. Encode is the
same pick after codebook writing. Do not put 577 in a find column
next to `gan_llm_extract`. That number is already encode.

## Claim boundary

Development instrumentation. Not a cited-row change. Not holdout
evidence. Living rules find is source-near everywhere in the
three-stage runner.
