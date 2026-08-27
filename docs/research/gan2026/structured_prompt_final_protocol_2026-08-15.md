# Protocol: Gan `final` prompt development re-run

Date: 2026-08-15
Status: complete; no large drop. Live `v0.5` control (sidecar absent).
Evidence: [run](structured_prompt_final_luna_dev20_2026-08-15.md)
Parent: [decision 0053](../../decisions/0053-gan-structured-events-final-prompt.md)
Prompt: `gan2026_hybrid_structured_events_final`

## Primary question

On a frozen development sample, does the envelope-hygiene prompt
(`final`) change Gan Purist relative to the frozen `v0.5` sidecar
under one named model?

The clinical instructions are the same. This study only removes
`task` / `prompt_version` / `source_row_index` identity from the
model-facing JSON.

## Why this study

Decision 0053 authorizes `final` but does not replace Decision 0043
fills. Before any `dev750` scale-up or holdout call, measure whether
dropping the envelope moves Luna on a mixed `dev20`.

## Scope and fixed conditions

| Item | Value |
| :--- | :--- |
| Dataset | Gan 2026 `dev750` (`validation` in `gan2026_split_v1`) only |
| Sample | 20 rows, frozen before the first `final` call |
| Model | `openai/gpt-5.6-luna` |
| Current arm | no-call reuse of Luna `v0.5` from [`experiments/gan2026_luna_prompt_variants_dev750_20260730/`](../../../experiments/gan2026_luna_prompt_variants_dev750_20260730/) variant A |
| Candidate arm | live Luna calls with `gan2026_hybrid_structured_events_final` |
| Repair | current `hybrid_full_stack` |
| Scorer | Gan Purist and Pragmatic |
| Gold at prompt-build time | **forbidden** |
| Holdout | **not touched** |
| Other five models | **not called** |

Do not change the operational default prompt. Do not rewrite Decision
0043 / 0050 fills. Do not inspect `test450`.

## Sample freeze

Before the first `final` call, write twenty `source_row_index` values
from `dev750` that exist on the Luna `v0.5` sidecar. Mix gold kinds
from the development labels only (frequency, seizure-free, unknown,
no-reference, cluster). Do not choose rows by `v0.5` error. Record
the indices in the run artifact.

## Payload identity

`build_prompt_input(..., prompt_version=gan2026_hybrid_structured_events_final)`
must omit `prompt_version` and `source_row_index`, must not contain
`Gan 2026`, `LLM-only`, or `gan2026_hybrid_structured_events`, and
must keep the `v0.5` instruction list and schemas.

Row artifacts still store `prompt_version` beside `prompt_input_json`.

## Readout

- Purist and Pragmatic correct counts on the same 20 rows
- Parse / schema / call failures
- Contract hash of the `final` instruction/schema/task object

A large drop on this 20 is a reason to stop and inspect the `final`
payload, not a reason to add clinical rules. A small or zero drop
authorizes the completed Luna `dev750` remasure:
[structured_prompt_final_luna_dev750_2026-08-15.md](structured_prompt_final_luna_dev750_2026-08-15.md).
It does not authorize `test450` or the other five models.

## Claim boundary

Development only. Envelope hygiene, not a prompt-policy study. Not a
six-model ranking. Not holdout evidence.
