# Gan 2026 RQ3 Rich Selected-State Five-Letter Answer

Date: 2026-06-04

Status: focused validation-development answer for the five-letter RQ3 smoke
surface. This is not a hard-panel, holdout, or F1 claim.

Protocol:
``

Artifact:
`experiments/gan2026_rich_selected_state_five_letter_2026-06-04.jsonl`

Report:
`experiments/gan2026_rich_selected_state_five_letter_2026-06-04.md`

## Answer

The rich selected-state schema is worth carrying forward to a hard-panel RQ3
run, with one important caveat:

```text
The model reliably filled the boundary fields needed for deterministic
projection on the five focused rows, but it did not always put the broad
state_kind in the category a human would choose.
```

That is acceptable for the next experiment because the core hypothesis was not
"can the model render the label?" It was "can the model carry the clinical facts
needed for deterministic projection?"

On the five focused rows:

- structured records: 5/5;
- exact selected evidence: 5/5;
- parse/boundary errors: 0/5;
- deterministic projected labels after renderer replay: 5/5 parseable;
- focused mechanism targets rendered as intended:
  - row 10 -> `4 per day`;
  - row 280 -> `multiple per day`;
  - row 3356 -> `unknown`;
  - row 10618 -> `unknown, 4 to 6 per cluster`;
  - row 2748 -> `1 per month`.

## What Worked

The model selected exact, clinically relevant evidence on all five rows.

More importantly, it filled the fields that the earlier RQ1/RQ2 controls were
missing:

- row 3356 carried the conditionality note: seizures occur only after curtailed
  sleep, with no events when sleep is adequate;
- row 10618 carried both cluster burden and unknown cluster cadence: 4 to 6
  short spells grouped on days when they occur, with no stable cluster rate;
- row 280 preserved multiple-event wording instead of inventing an exact count;
- row 2748 selected the current monthly summary rather than the derived
  year-to-date count;
- row 10 preserved the upper-bound rate and variable cluster context.

This is the bridge RQ3 needed: exact evidence plus typed boundary fields, not
direct label rendering.

## What Failed Or Remains Risky

The model overused `state_kind="frequency"`.

Rows 3356 and 10618 should be semantically closer to `unknown` or
`unresolved_multiple` at the selected-state category level, but the model used
`frequency` while placing the corrective information in `conditionality_note`
and `cluster`. The deterministic renderer could recover because those fields
were populated.

This means the next hard-panel run must judge:

- whether boundary fields remain reliable beyond five rows;
- whether overuse of `frequency` is harmless when boundary fields are present;
- whether additional validation should flag inconsistent combinations, such as
  `state_kind=frequency` plus conditionality that forces `unknown`.

## Renderer Revision

The first live pass exposed renderer gaps, not prompt/schema parse failures.
Using the same saved raw model outputs, the deterministic renderer was tightened
before any broader run:

- upper-bound rate with only `count_high` now renders from the upper count;
- `1 per 1 month` collapses to `1 per month`;
- cluster burden without known cadence takes precedence over accidental
  daily-rate interpretation;
- conditional selected states render to `unknown`.

This is a development-control revision on the five-row surface. It is not a
hard-panel-tuned or holdout-facing policy.

## Decision

Proceed to a hard-panel RQ3 run only after freezing:

- prompt version: `gan2026_llm_only_rich_selected_state_reasoner_v0`;
- schema version: `rich_selected_state_v0`;
- deterministic renderer behavior tested in
  `tests/test_gan2026_llm_only_rich_selected_state_reasoner.py`.

Primary hard-panel metrics should remain component metrics:

- schema-valid selected states;
- exact selected evidence;
- boundary field completeness;
- boundary inconsistency count;
- deterministic projected parseability;
- rows where deterministic projection intentionally maps a model-selected
  `frequency` state to `unknown`.

Do not interpret hard-panel final labels as an F1 result. The research question
is whether the rich selected state carries enough information for safe
deterministic projection.

## Next Action

Run the rich selected-state reasoner on `hidden_family_hard_panel` rows from the
RQ1/RQ2 control matrix, then analyze boundary-field reliability by hidden family.
