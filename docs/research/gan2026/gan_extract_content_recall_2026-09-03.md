# Results: Extract content recall (answer or evidence)

Date: 2026-09-03
Protocol: [protocol](gan_candidate_set_recall_test450_protocol_2026-09-03.md)
Artifact: [aggregates](gan_extract_content_recall_2026-09-03.json)
Module: `clinical_extraction.paper.gan_extract_content_recall`
Replay: `python scripts/measure_gan_extract_content_recall.py`
Tests: `tests/test_gan_extract_content_recall.py`
Model calls: 0. Holdout is aggregate-only.

## Definition

On the living Gemini `gan_llm_extract` record, **all events** count
(not only the selected answer):

- **Answer:** provisional `final_label` or any event after
  `_normalize_event` is Purist-correct vs gold.
- **Evidence:** annotation `gold_reference` overlaps selection evidence
  or any event evidence (folded either-contains).
- **Answer or evidence:** union of the two.

This is the corrected stage-1 measure. A raw string match against
`gold_reference` alone under-counts letters where a candidate already
maps to the right Purist answer under different wording.

## Answer

| Split | Answer | Evidence | **Answer or evidence** | Hybrid decide | LLM-only decide |
| --- | ---: | ---: | ---: | ---: | ---: |
| `test450` | 382/450 (0.849) | 308/450 (0.684) | **433**/450 (**0.962**) | 387/450 | 383/450 |
| `dev750` | 655/750 (0.873) | 541/750 (0.721) | **738**/750 (**0.984**) | 656/750 | — |

Decide-correct with no extract answer-or-evidence hit: Hybrid **1** on
`test450`, **2** on `dev750`; LLM-only **0** on `test450`.

Gates on `test450`: Hybrid 387 and LLM-only 383 reproduced; parse
failures 0.

## Reproduce

```bash
source .venv/bin/activate
python scripts/measure_gan_extract_content_recall.py
python -m pytest tests/test_gan_extract_content_recall.py -q
```

## Claim boundary

Stage-1 extract content recall for the shared Gemini record. Holdout
aggregates only. Not a new Table 1 score. Not permission to inspect
or retune from locked rows.
