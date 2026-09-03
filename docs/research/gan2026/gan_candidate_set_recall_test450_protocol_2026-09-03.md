# Protocol: Candidate-set recall for Gemini cells 3 and 5 on Gan `test450`

Date: 2026-09-03
Status: complete (superseded metric owner below)
Owner: this file
Report: [extract content recall](gan_extract_content_recall_2026-09-03.md)
Artifact: [aggregates](gan_extract_content_recall_2026-09-03.json)
Replay: `python scripts/measure_gan_extract_content_recall.py`
Related development measurement: prior session on `dev750` (same
definition; not an owner file).
Paper context:
[paper story simplification archive](../paper/paper_story_simplification_2026-09-02.md);
[paper-story simplification](../../paper/decisions/paper-story-simplification.md)
Guardrail: `gan2026-scoring-guardrail`;
[holdout is aggregate-only](../../paper/decisions/holdout-is-aggregate-only.md)

## Primary question

On sealed Gan `test450`, under Purist mapping, how often is the gold
answer present in the shared Gemini extract record (candidate-set
recall), and how does that ceiling relate to cited cell 3 (Hybrid
decide) and cited cell 5 (LLM-only decide)?

## Why this matters

The paper needs a stage-1 metric for extract: whether gold is among
the extracted candidates. Rules-only already has a pool oracle on
development. Cells 3 and 5 share `gan_llm_extract`; both need the
same aggregate recall, plus residual headroom versus each decide stop.

## Frozen inputs (zero model calls)

- Extract ledger: living Gemini `gan_llm_extract` rows on `test450`
  (`paper_experiments/gan/gan_llm_extract/gemini37flash/test450/rows.jsonl`)
- Cell 3 decide stop: replay extract through
  `llm_select_after_codebook` (cited Hybrid select **387**/450)
- Cell 5 decide stop: stored Purist flags from the promoted select
  work cell
  (`scratch/holdout/paper/gan_llm_select_from_extract/gemini37flash/gan_llm_extract/test450/rows.jsonl`;
  cited **383**/450)
- No new extract or select calls. No prompt or repair-mode change.

## Metric definition (predeclared)

Purist via existing `score_label` / `map_purist`.

1. **Extract events-only:** parse extract with `raw_model`; for each
   event run `_normalize_event`; hit if any normalized label is
   Purist-correct.
2. **Extract record pool (primary):** events-only **or** provisional
   `selection.final_label` Purist-correct. This is the stage-1
   candidate-set recall for both cells.
3. **Encode pool (cell 3 diagnostic):** parse with `gan_rules_encode`;
   hit if any normalized event label or encode `final_label` is
   Purist-correct.
4. **Decide stops:** cell 3 and cell 5 Purist correct counts must
   reproduce the cited aggregates (387 and 383) before residuals are
   reported.
5. **Residuals (aggregate counts only):** on decide-wrong letters,
   `headroom` = extract-record pool hit; `recall_gap` = pool miss.
   Same split for the encode pool versus cell 3.

## Fixed comparators

| Cell | Cited Purist select |
| --- | ---: |
| Cell 3 Hybrid (`llm_select_after_codebook`) | **387**/450 |
| Cell 5 LLM-only (`gan_llm_select_from_extract`) | **383**/450 |
| Extract provisional (rungs `llm_extract`) | 355/450 |
| Encode provisional (rungs `llm_encode`) | 360/450 |

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Split | `test450` |
| Row policy | `aggregate_only` |
| Scorer | Purist; secondary Pragmatic on the same pools |
| Model calls | 0 |
| Public output | aggregate counts and rates only |

Do not inspect, quote, or tune on holdout identifiers, notes,
predictions, evidence, errors, or changed rows. The public artifact
must not contain those keys. Runners may read locked notes only to
rescore saved outputs. A holdout defect starts a new development
candidate; it does not permit holdout repair.

## Required analysis

- Primary extract-record candidate-set recall (Purist).
- Events-only and provisional-alone as diagnostics.
- Encode-pool diagnostic for Hybrid.
- Residual headroom / recall-gap aggregates versus cell 3 and cell 5.
- Gate: recomputed cell 3 and cell 5 select totals match 387 and 383.

Do not write row-level rescue tables. Do not retune Table 1.

## Artifact schema

Public JSON only:

- `schema_version`, `date`, `protocol`, `split`, `row_policy`,
  `model_slug`, `model_calls`
- pool counts / rates (events_only, extract_record, provisional,
  encode_pool) for Purist and Pragmatic
- decide_stop counts for cell 3 and cell 5
- residual aggregate counts
- claim_boundary string

No `source_row_index`, notes, labels, or evidence in the public file.

## Stop rule

Stop after gates pass and the public aggregate JSON plus short report
are written. Do not load `dev750` in this protocol’s public claim.
Do not overwrite living extract or cited select cells.

## Claim boundary

Holdout aggregate-only stage-1 measurement for the shared Gemini
extract record and its relation to cited cells 3 and 5. Not a new
Table 1 score. Not permission to inspect holdout rows.
