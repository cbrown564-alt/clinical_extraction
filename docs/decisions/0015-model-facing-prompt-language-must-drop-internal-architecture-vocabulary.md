# 0015: Model-Facing Prompt Language Must Drop This Project's Internal Architecture Vocabulary

Date: 2026-06-07

## Status

Accepted.

## Decision

Any text that an LLM will actually read as part of a prompt — `dspy.Signature`
docstrings, `InputField`/`OutputField` `desc` strings, and the keys, values,
and instruction strings inside JSON prompt payloads such as
`build_prompt_input()` — must be written as a **plain, task-oriented brief to
someone with no other context about this project**. It must not assume the
reader already knows this project's internal pipeline-architecture vocabulary,
naming conventions, or pipeline mechanics.

Concretely, model-facing prompt text must not use terms like *extraction,
selection, normalization, projection, rendering, deterministic/hybrid/Gan 2026
pipelines, stage-owned, ablatable rules, rule taxonomy, benchmark, scored,
scorer-facing, downstream*, or similarly internal architecture/process
vocabulary (see `CONTEXT.md`'s defined-term list for the canonical inventory of
internal terms). Where such a term names a real constraint the model needs to
honor, restate the constraint itself in plain language instead of naming the
internal concept.

This decision governs prompt-authoring for all `llm_only_*` configurations and
any future model-facing surface — it is not specific to
`llm_only_canonical_pipeline`, though that module's authoring is what
surfaced the issue.

## Context

While implementing `llm_only_canonical_pipeline`
([[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]]
Phase 0), the first drafts of its `Signature` docstring and JSON prompt payload
described the task using this project's own internal vocabulary, for example:

- *"Collapse extraction, selection, normalization, projection, and rendering
  into one pass."*
- A JSON payload key named `embedded_clinical_reasoning_rule_taxonomy`, with a
  `purpose` string reading *"These are the same named clinical-reasoning
  principles the deterministic and hybrid Gan 2026 pipelines encode as
  stage-owned, ablatable rules."*
- An output-field description telling the model to *"write it exactly as you
  want it scored, since nothing downstream will adjust it."*

Each of these reads naturally to someone who already has this project's mental
model — but the model receiving the prompt has none of that context. It does
not know what "the deterministic and hybrid Gan 2026 pipelines" are, what a
"stage-owned, ablatable rule" is, what "scored" or "downstream" refer to in
this project's machinery, or why any of that would matter to the clinical
judgment it is being asked to make. Phrases like these add noise rather than
guidance, and risk being parroted back into the model's own output (the
`rationale`/`applied_rule_families` fields) in ways that misrepresent what the
model actually reasoned about.

## Why

The whole point of the prompt is to brief an outside reasoner on a clinical
task it can complete on its own. A brief that leans on internal naming
conventions fails at that job in two ways:

1. **It doesn't communicate anything useful.** The model cannot act on
   "collapse extract→select→normalize→project→render into one pass" — it has
   no concept of those stages as separate things to collapse. What it *can*
   act on is the actual constraint underneath: *"give one complete, final
   answer yourself; nothing will revise it afterward."*
2. **It actively risks distortion.** Internal-architecture phrasing invites the
   model to reflect that phrasing back (e.g., echoing "stage-owned, ablatable
   rules" in a `rationale` string), producing outputs that look like they
   understand our pipeline taxonomy when they are really just pattern-matching
   our prompt's own words back to us. That undermines the value of
   self-reported diagnostic fields like `applied_rule_families` and
   `rationale`.

The fix in each case was to ask: *what is the underlying constraint or fact the
model actually needs, stripped of the internal name we use for it?* —

- "Collapse extract→select→normalize→project→render into one pass" became
  *"Provide a complete answer that adheres to the instructions below... Return
  exactly one JSON object with these keys: ..."* — the model is told what to
  produce and that nothing downstream will revise it, without being told about
  stages it has no model of.
- `embedded_clinical_reasoning_rule_taxonomy` (with its "stage-owned, ablatable
  rules" framing) became `guidance_for_tricky_cases`, framed entirely from the
  reader's vantage point: *"Clinical notes describe seizure frequency in many
  different ways, and some are easy to misread. The notes below each name a
  situation that commonly trips people up and say what to do about it... you
  are the only one who will look at this note, so any misreading here will
  reach the final answer unchanged."*
- "write it exactly as you want it scored, since nothing downstream will
  adjust it" was dropped — the format examples in the field description already
  communicate what a complete answer looks like, and no claim about "scoring"
  or "downstream" stages is needed at all.

## Consequences

- `tests/test_gan2026_llm_prompt_hygiene.py` (`INTERNAL_MODEL_FACING_PHRASES`)
  is the enforcement mechanism for this decision: any new `llm_only_*` prompt
  builder added to its parametrized suite is checked against a deny-list of
  internal-vocabulary phrases. Extend that list (rather than special-casing
  individual prompt builders) when a new internal term is found leaking into
  model-facing text.
- When adding or revising any model-facing prompt text, the authoring question
  is not "is this accurate?" (internal-architecture phrasing usually *is*
  accurate) but "would this mean anything to a capable reasoner who has never
  seen this codebase?" If the answer is no, restate the underlying constraint
  in plain language instead.
- This does **not** apply to human/team-facing text — module docstrings,
  `CONTEXT.md` entries, experiment reports (e.g. `write_report`'s generated
  markdown), commit messages, or ADRs like this one. Those audiences *do* share
  this project's internal vocabulary, and using it precisely there remains the
  right call (see [[0014-evidence-trace-check-not-verify-for-deterministic-canonical-pipeline]]
  for an example of getting *internal* naming right). The distinction this ADR
  draws is strictly about which strings the model itself will read.

## Related Artifacts

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_only_canonical_pipeline.py`
  — the `Gan2026CanonicalLlmExtractorSignature` docstring/field descriptions and
  `build_prompt_input()`'s `guidance_for_tricky_cases` block are the worked
  example this ADR documents.
- `tests/test_gan2026_llm_prompt_hygiene.py` — `INTERNAL_MODEL_FACING_PHRASES`,
  the automated guard for this decision.
- [[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]]
- [[0014-evidence-trace-check-not-verify-for-deterministic-canonical-pipeline]]
  — the contrasting case: get *internal* naming precise for human-facing
  surfaces, while this ADR asks for the opposite treatment of model-facing ones.
