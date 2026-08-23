# ExECT diagnostic inventory track

Date: 2026-08-23
Status: current
Owner: this file

`exect_llm_inventory` is a live extract method for prompt clarity.
It copies Compact LLM-only wording and drops the extra restriction
that withholds a generic epilepsy diagnosis beside a specific type.
It is scored on unique Diagnosis concepts without most-specific
collapse. It is not a paper cell and is not in `CELL_ORDER`.

The model-facing prompt stays in the Compact LLM-only voice. Scorer
names stay in code and this note only.
