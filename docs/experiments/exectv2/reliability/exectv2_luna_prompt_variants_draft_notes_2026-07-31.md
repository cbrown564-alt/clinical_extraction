# Luna ExECT prompt variants B and C draft notes

Date: 2026-07-31  
Status: drafts implemented; A/B/C `dev140` panel complete  
Protocol: [exectv2_luna_prompt_variants_dev140_protocol_2026-07-31.md](exectv2_luna_prompt_variants_dev140_protocol_2026-07-31.md)  
Report: [panel report](exectv2_luna_prompt_variants_dev140_2026-07-31.md)

## What changed

Both candidates keep the frozen v0.9.24 event schema. Only additive
`extra_clinical_guidance` lines were added. Default `PROMPT_VERSION` remains
`v0.9.24`.

| Variant | Prompt identity | Added guidance lines | Snapshot |
| --- | --- | ---: | --- |
| A | `..._v0.9.24` | 0 (control) | existing `exectv2__structured_key_families.txt` |
| B | `..._v0.9.25_luna_sf_state` | 5 | `exectv2__structured_key_families_v0.9.25_luna_sf_state.txt` |
| C | `..._v0.9.25_luna_sf_boundary_dx` | 5 | `exectv2__structured_key_families_v0.9.25_luna_sf_boundary_dx.txt` |

## Why the extra text is allowed

This is a controlled prompt-shape experiment. The residual map showed SF letter
wrongs under joint repair are almost entirely model-owned clinical state
selection with exact evidence. The question is whether plain-language guidance
still moves Luna model-owned SF answers after the mature `v0.9.24` prompt.

## B targets from exemplars

- Emit only supported current SF states.
- Do not invent seizure-free beside a clear active rate.
- Keep unknown when current frequency is only partly clear.
- Keep multi-type active-rate sets the letter supports.
- Prefer countable period rates over vague control language.

## C targets from exemplars

- Short quiet spells / unclear improvement → unknown, not seizure-free.
- Dated prior events do not invent a current active rate beside seizure-free.
- Keep active-rate + unknown when one type is current and another is unclear.
- Prefer the most specific diagnosis phrase supported by the letter.
- Do not add unstated sibling diagnosis phenotypes.

## Plain-language audit

| Check | Result |
| --- | --- |
| Rendered prompt inspected | Yes, both variants via `build_prompt_input` |
| Model-facing text is plain language | Yes; ordinary verbs and clinical terms |
| Internal metadata separated | Research ids stay in code/docs; guidance omits gold, slices, and residual taxonomy |
| Non-obvious schema fields described | Unchanged from v0.9.24 |
| Jargon removed or defined | No new scorer, denominator, or experiment jargon in the added lines |
| Prompt length matches purpose | Intentionally longer than v0.9.24 for this controlled study |
| Controlled-experiment deviation justified | Yes, above |

Inherited `v0.9.24` wording such as `source-near` remains in the shared base
payload because the schema and baseline instruction set are frozen for A/B/C
comparability.

## Next action

None for drafting. See the panel report for the development answer and any
later aggregate-only `test60` protocol.
