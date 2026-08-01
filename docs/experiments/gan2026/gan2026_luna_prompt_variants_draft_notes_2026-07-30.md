# Luna Gan prompt variants B and C draft notes

Date: 2026-07-30  
Status: drafts implemented and snapshotted; no Luna A/B/C runs yet  
Protocol: [gan2026_luna_prompt_variants_dev750_protocol_2026-07-30.md](gan2026_luna_prompt_variants_dev750_protocol_2026-07-30.md)

## What changed

Both candidates keep the frozen v0.5 event and selection schemas. Only
model-facing instructions were added before the final "return one JSON object"
line.

| Variant | Prompt identity | Added instructions | Snapshot |
| --- | --- | ---: | --- |
| A | `gan2026_hybrid_structured_events_v0.5` | 0 (control) | existing |
| B | `gan2026_hybrid_structured_events_v0.8_luna_rate` | 6 | `tests/snapshots/prompt_contracts/gan2026__hybrid_structured_events_v0.8_luna_rate.txt` |
| C | `gan2026_hybrid_structured_events_v0.8_luna_current` | 7 | `tests/snapshots/prompt_contracts/gan2026__hybrid_structured_events_v0.8_luna_current.txt` |

Default `PROMPT_VERSION` remains v0.5. These candidates are selectable only by
explicit prompt version and must not replace the frozen six-model panel.

## Why the extra text is allowed

This is a controlled prompt-shape experiment. The question is whether
plain-language clinical guidance still moves Luna LLM-only answers after the
mini-tuned short prompt plateaued. The extra instructions are justified by
retained Luna residual mass on `validation750`, not by locked-test inspection.

## B targets from exemplars

- Keep count ranges as ranges (`1 to 3`), not one endpoint or
  `unresolved_multiple`.
- Prefer countable period totals over vague `multiple` / `several times` rates.
- Prefer overall count over subtype-only selection.
- Keep cluster cadence and events per cluster together.
- Do not let a short post-burst quiet spell erase the recent countable burden.
- Prefer clinic or diary totals over device hints or one-type guesses.

## C targets from exemplars

- Short quiet intervals of days or weeks → `unknown` when current frequency is
  unclear, not `seizure_free`.
- Long quiet stretches do not erase a stated current or yearly rate.
- Possible or single questionable events → `unknown`.
- Dated counts remain frequency evidence; do not demote them to `no_reference`.
- Recurrent cluster-day patterns stay `cluster_frequency`.
- Vague "every few weeks" estimates do not override clearer definite-seizure
  freedom without a usable count.
- Non-progressing occasional sensations without a rate do not invent a
  frequency answer.

## Plain-language audit

| Check | Result |
| --- | --- |
| Rendered prompt inspected | Yes, both variants |
| Model-facing text is plain language | Yes; ordinary verbs and clinical terms |
| Internal metadata separated | Research ids stay in code/docs; instructions omit gold, slices, and residual taxonomy |
| Non-obvious schema fields described | Unchanged from v0.5 |
| Jargon removed or defined | No new `source-near`, `denominator`, `scorer`, or experiment jargon in the added lines |
| Prompt length matches purpose | Intentionally longer than v0.5 for this controlled study |
| Controlled-experiment deviation justified | Yes, above |

Inherited v0.5 wording such as `source-near` remains in the shared base lines
because the schema and baseline instruction set are frozen for A/B/C
comparability.

## Next action

Run Luna-only A/B/C on `validation750` with dual LLM-only and LLM-with-rules
readouts under the protocol stop rules. Do not inspect `test450`.
