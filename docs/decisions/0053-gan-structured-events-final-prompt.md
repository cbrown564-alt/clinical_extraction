# 0053: Strip internal envelope language from the Gan structured-events prompt

Date: 2026-08-15
Status: accepted; payload implemented; Luna `dev20` and `dev750`
complete (no large drop); selected fills unchanged
Amends: [decision 0015](0015-model-facing-prompt-language-must-drop-internal-architecture-vocabulary.md)
        (envelope identity is also model-facing);
        [decision 0043](0043-gan-hosted-comparison-uses-v05-prompt.md)
        (adds a hygiene successor; does not replace v0.5 panels)
Does not change: Decision 0043 / 0050 / 0052 selected scores; clinical
instructions; event or selection schema; repair; scorer

## Decision

The next clean Gan `llm_with_rules` structured-events run uses
`gan2026_hybrid_structured_events_final`.

`final` is Decision 0043's `v0.5` clinical contract with three
model-facing identity fields removed:

| `v0.5` field | `final` |
| :--- | :--- |
| `task`: “Gan 2026 LLM-only structured-events extraction and clinical selection” | “Read the clinical note. Extract seizure-frequency facts as slim events, then select the current burden.” |
| `prompt_version`: `gan2026_hybrid_structured_events_v0.5` | omitted from the payload |
| `source_row_index` | omitted from the payload |

The thirteen instructions, `event_schema`, and `selection_schema` are
unchanged. Run artifacts still record
`prompt_version=gan2026_hybrid_structured_events_final` outside the
model-facing JSON.

`v0.5` remains the selected historical comparison identity until a
matched `final` panel exists. Existing Decision 0043 / 0050 / 0052
fills are not rewritten by this decision. `v0.6` / `v0.7` / `v0.8_*`
stay diagnostic.

## Reason

[Decision 0015](0015-model-facing-prompt-language-must-drop-internal-architecture-vocabulary.md)
requires model-facing text to brief a capable clinical reader who has
never seen this repository. The 3 June hygiene pass removed
“deterministic rule candidates,” “benchmark,” and “Gan-compatible”
from the instructions. The 15 August
[lineage review](../research/gan2026/structured_prompt_lineage_2026-08-15.md)
found no ExECT-style architecture block, but the payload envelope
still names the dataset, the method (`LLM-only`, which is the wrong
method for this path), the software version string, and the split row
index.

Those three strings do not instruct extraction. They are project
identity. A clean re-run should not carry them.

This is not a `v10` cut of the clinical rules. It is not authorization
to land `v0.6` / `v0.7` policy, and it is not a fill rewrite.

## Comparison boundary for the clean re-run

- Prompt: exact `gan2026_hybrid_structured_events_final` payload.
- Clinical instructions and schemas: byte-identical to current `v0.5`.
- Pipeline, repair, scorer, split manifest, and row policy: current
  stack, frozen before the first `final` call.
- First measurement: Luna `dev20`, complete
  ([run](../research/gan2026/structured_prompt_final_luna_dev20_2026-08-15.md)).
- Next measurement: Luna `dev750`, complete
  ([run](../research/gan2026/structured_prompt_final_luna_dev750_2026-08-15.md);
  hybrid Purist 660/750 vs 663/750, not a large drop).
- `test450` stays sealed. No holdout calls under this decision.
- Gold must not enter prompt construction.
- Cache disabled. One structured-events call per note.
- `final` outputs cannot be compared to `v0.5` as the same prompt.
  A no-call `v0.5` sidecar may be the control arm only when its
  non-prompt stack is reconciled.

## Consequences

- Do not describe a `final` score as a `v0.5` score.
- Do not promote `final` into Decision 0043 / 0050 tables from this
  decision alone.
- Do not change the live operational default
  (`gan2026_hybrid_structured_events_v0.5` in `operational/gan.py`)
  until a later decision says the `final` panel is the selected
  identity.
- A later holdout protocol is required before any `test450` `final`
  call.

## Owners

- Payload:
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py`
  (`PROMPT_VERSION_FINAL`, `build_prompt_input`)
- Contract:
  `tests/test_gan2026_hybrid_structured_events_contract.py`
- Lineage:
  [Gan structured-prompt lineage](../research/gan2026/structured_prompt_lineage_2026-08-15.md)
- `dev20` protocol / run:
  [protocol](../research/gan2026/structured_prompt_final_protocol_2026-08-15.md);
  [run](../research/gan2026/structured_prompt_final_luna_dev20_2026-08-15.md)
- `dev750` run:
  [run](../research/gan2026/structured_prompt_final_luna_dev750_2026-08-15.md)
