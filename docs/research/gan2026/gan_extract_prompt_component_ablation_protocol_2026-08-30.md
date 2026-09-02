# Protocol: Gan find prompt-component ablations

Date: 2026-08-30
Status: `test450` finds and cell-3 replay complete
Owner: this file
Report: [aggregates](gan_extract_prompt_component_ablation_2026-08-30.md)
Related: [source-near vs bundled encode](../paper/gan_source_near_vs_bundled_encode_2026-08-23.md),
[extract label-forms](gan_extract_label_forms_protocol_2026-08-22.md),
[results §D](../../paper/sections/results.md)

## Primary question

On Gemini cell 3, how much of the cited codebook find
(`gan_llm_extract`) depends on example strings, and how much of the
whole codebook package (clinical instructions + allowed forms +
examples) is doing work relative to a Holgate-style three-step ask?

This is not `gan_llm_extract` versus `gan_llm_extract_raw`. That older
contrast bundles labels with examples. These two variants keep the
cited extract as the base and change one package at a time.

## Why it matters

The paper already treats form-at-find as an optional ablation. The
next useful claim is narrower: examples, given the codebook; and the
codebook package versus a short literature-style query. The study
cannot attribute “instructions alone” without a later third cell that
keeps the current instructions and drops `label_forms`.

## What is held constant

- Dataset Gan 2026, scorer living Purist (primary) and Pragmatic.
- Model Gemini 3.7 Flash (`gemini37flash`), temperature 0, living
  thinking/low setting.
- Event schema and selection schema from `gan_llm_extract`.
- Later cell-3 stages: `gan_rules_encode` then
  `llm_select_after_codebook`, including living
  `last_event_well_since`. No new encode/select calls.
- Output object: one JSON events-plus-selection record. Holgate’s
  free-text answer is not replicated.

Schema field descriptions stay those of the cited extract, including
`final_label: normalized label, or null if not directly countable`.
That is a held-constant leak of form language, not a second codebook.

## Candidates

Base (already cited; do not rerun unless a raw is missing):

- `gan_llm_extract`: full instructions + form names/descriptions/rules
  + example strings.

Variant 1 — examples off:

- `gan_llm_extract_no_examples`
- Same instructions and allowed forms.
- Drop every `examples` array.
- Rewrite “Copy an example and change the numbers if needed” to
  “Change the numbers if needed.”
- Bound-flattening and night-as-day rules stay. Those are form-writing
  rules, not the examples list.

Variant 2 — Holgate-like floor:

- `gan_llm_extract_holgate_like`
- No `label_forms`. No few-shots. No persona.
- Clinical ask follows Holgate et al. 2024 Figure 2 three steps:
  is there frequency information; if not, answer “I do not know”;
  if yes, state a rate per year, month, week, or day.
- One extra instruction only so the same parser can run: return the
  event/selection JSON, keep note wording in `raw_value`, quote
  evidence as a substring.

Holgate’s published method also used 11 few-shots and a
neuroscientist persona. This variant copies the short query, not that
full method.

Frozen requests without `note_text`:

- [no-examples template](gan_llm_extract_no_examples_prompt_template.json)
- [Holgate-like template](gan_llm_extract_holgate_like_prompt_template.json)

Cited codebook template remains
`paper/supporting materials/gan_llm_extract_prompt_template.json`.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Primary split | locked `test450` (`gan2026_split_v1` test) |
| Row policy | Aggregate only. Do not inspect holdout rows, labels, or notes. |
| Secondary split | `dev750` only if a mechanism reading is needed after aggregates; not for prompt retune |
| Model | Gemini 3.7 Flash |
| Scorer | Purist micro-F1; Pragmatic companion |
| Repair | Live find is `raw_model`. Cell 3 encode/select is no-call replay. |
| New calls | Required. Saved `gan_llm_extract` raws cannot be reused. |

Do not retune wording, forms, or rules from `test450`. A parse-failure
spike may stop the study or start a new protocol. It does not permit
holdout repair.

## Comparator

Living Gemini cell 3 on the same `test450` letters, from
`paper_experiments/gan/rungs/gemini37flash/test450/comparison.json`
and the five-cell living replay:

| Stop | Purist |
| --- | ---: |
| Find (`raw_model`) | 0.789 (355) |
| Encode (`gan_rules_encode`) | 0.800 (360) |
| Select (`llm_select_after_codebook`) | 0.860 (387) |

Extract-cell `comparison.json` summaries are find stops. Do not treat
those files’ `summary.purist_correct` as cell 3 select.

## Required tables

For base and both variants, report find / encode / select Purist
(and Pragmatic) on `test450`. Primary contrasts:

1. Base versus no-examples: examples, given instructions + forms.
2. Base versus Holgate-like: the codebook package.
3. No-examples versus Holgate-like: forms and policy together, not
   instructions alone.

Also record parse/schema failures, scorable count, and call failures.
Changed-row direction is allowed on `dev750` only.

## Artifact

Live work cells (holdout under scratch):

- `scratch/holdout/paper/gan_llm_extract_no_examples/gemini37flash/test450/`
- `scratch/holdout/paper/gan_llm_extract_holgate_like/gemini37flash/test450/`

Do not promote into `paper_experiments/gan/rungs/` or the five-cell
grid. After both extracts exist, replay saved raws through living
cell 3 and write a dated report plus machine-readable aggregates
beside this protocol. No letter text and no `test450` row ids.

## Commands (after verify; not yet run)

```bash
source .venv/bin/activate
python -m clinical_extraction.paper verify --method gan_llm_extract_no_examples --model gemini37flash --split test450
python -m clinical_extraction.paper verify --method gan_llm_extract_holgate_like --model gemini37flash --split test450
python -m clinical_extraction.paper run --method gan_llm_extract_no_examples --model gemini37flash --split test450 --live
python -m clinical_extraction.paper run --method gan_llm_extract_holgate_like --model gemini37flash --split test450 --live
```

## Stop rule

Answer when both `test450` extracts are complete and the no-call
cell-3 replay is written. Negative result is allowed. Do not add a
third variant in this study. Do not change Table 1.

## Claim boundary

Holdout evidence is aggregate-only. Ablation, not a results column.
Fair sentences after a complete run:

- “Removing examples, with the codebook otherwise intact, changed
  find/select by …”
- “Replacing the codebook package with a Holgate-style three-step
  ask changed find/select by …”

Not allowed from these two cells: “we measured the separate
importance of instructions, labels, and examples.”

## Decision

Protocol accepted 2026-08-30. Both Gemini `test450` finds ran
(450/450, 0 call failures, 0 parse failures). Cell-3 replay is
written. Table 1 unchanged.
