# Reusable Best Practices From Predecessor Repos

Date: 2026-06-27

Purpose: preserve practices that repeatedly improved interpretability,
reproducibility, or claim safety across predecessor attempts. These are framed
as operating practices for `clinical_extraction/`, not as new results.

## BP1. Start With The Contract, Not The Prompt

Historical source:
`dissertation/docs/clean_repo_handoff/14_lessons_for_clean_rebuild.md`

Evidence record:

The clean-rebuild handoff said the old repo reached the evaluation contract too
late. It recommended defining field families before prompts, defining validity
and correctness before metrics, and defining full versus partial contract before
comparing harnesses.

Why it survived:

Later prompt-design work found the same issue at a more detailed level. The
experiment axes were named, but model-facing prompts still blurred task,
schema, evidence, projection, and scoring concepts. This made component
comparisons hard to interpret.

Practice for `clinical_extraction/`:

For any authorized follow-up, write these before running anything:

- task surface;
- prediction-bearing component;
- allowed deterministic repairs;
- scorer and projection path;
- split and inspection rights;
- output schema and null behavior;
- promotion, rejection, and stop rule.

If those cannot be stated, keep the idea as future work.

## BP2. Preserve Fixed-Slice Discipline

Historical sources:

- `dissertation/docs/clean_repo_handoff/14_lessons_for_clean_rebuild.md`
- `clinical_extraction/docs/design/gan2026_split_protocol.md`

Evidence record:

The clean-rebuild handoff identified matched slices and recorded runs as the old
repo's strongest evidence. It recommended specifying row IDs and data hash for
every comparison and generating tables from run records where possible.

The current Gan split protocol formalizes this:

- smoke tests: 25 validation rows;
- meaningful signal: 50 validation rows;
- decision gate before 250 rows;
- 250-row validation as standard stronger development signal;
- rare full 750-row validation only with a written reason.

Practice for `clinical_extraction/`:

- Use small validation prefixes for contract failures and early signal.
- Escalate only when the previous stage answers the intended question.
- Do not promote from aggregate F1 alone.
- Record why a larger slice changes a decision.

## BP3. Separate Validity, Support, Clinical Correctness, And Benchmark Correctness

Historical sources:

- `dissertation/docs/clean_repo_handoff/13_what_did_not_work.md`
- `dissertation/docs/clean_repo_handoff/14_lessons_for_clean_rebuild.md`
- `dissertation-experiments/docs/prompt_design_gap_report.md`

Evidence record:

The clean-rebuild docs warned that parseable JSON and evidence strings were
initially treated as stronger signals than they were. They recommended scoring
parse validity, proxy support, and clinical correctness separately.

The prompt design report later split evidence policies into cleaner variants:
no evidence instruction, exact quote required, quote plus sentence/offset,
event-first evidence, and separate verifier-only evidence assessment. It also
stated that evidence validity and evidence support should remain separate
scoring views.

Practice for `clinical_extraction/`:

When reviewing a result, ask four separate questions:

1. Did the output parse and satisfy the schema?
2. Does the quoted evidence exist as source text?
3. Does that evidence support the value/status/temporality/normalization?
4. Does the scored projection match the benchmark or clinical surface being
   reported?

Never let success on one layer imply success on the others.

## BP4. Treat Architecture As A Testable Intervention

Historical source:
`dissertation/docs/clean_repo_handoff/14_lessons_for_clean_rebuild.md`

Evidence record:

The clean-rebuild handoff explicitly said multi-agent decomposition is not
inherently better. It should be tested, and reports should distinguish where
role separation helps, where it is parity or worse, and how accuracy,
auditability, and cost trade off.

This principle was validated repeatedly:

- `h010/h011` recovered seizure-frequency behavior but destroyed broad-field
  coverage.
- Recursive multi-agent/event-first attempts found stage error propagation and
  validation-scale reversals.
- Later evidence resolver work showed that auditability could be added after a
  compact extraction stage without forcing the first-pass extractor to carry
  evidence-rich output.

Practice for `clinical_extraction/`:

- Describe each stage by responsibility, not by role name.
- Require per-stage artifacts only when they answer a component question.
- Report cost/latency and per-field tradeoffs alongside aggregate quality.
- Keep compact first-pass extraction plus post-hoc evidence resolution on the
  table when quote-rich extraction harms accuracy.

## BP5. Use Component Placement, Not "Hybrid", As The Scientific Variable

Historical source:
`dspy-extraction/docs/workstreams/hybrid/hybrid_deterministic_placement_research_synthesis_20260521.md`

Evidence record:

The DSPy-era hybrid synthesis framed the real question as where deterministic
clinical knowledge enters the pipeline. It used classes such as deterministic
only, LLM only, post-deterministic, pre-deterministic, tool-during, and
pre-plus-LLM-adjudication. It concluded:

- Gan frequency benefited from deterministic temporal candidates before the LLM
  plus LLM adjudication and light post evidence guarding.
- ExECT S1 benefited from benchmark label policy during extraction and
  deterministic bridges after extraction.
- Generic pre-vocabulary/candidate injection on ExECT slices regressed.
- Tool-during ReAct temporal tools were rejected as the default Gan path.

Practice for `clinical_extraction/`:

Every hybrid claim should state:

- which component created candidate facts;
- which component selected the final clinical interpretation;
- which deterministic steps were format-only or evidence-only;
- which steps were semantic/prediction-bearing;
- which rule category is general, clinical epilepsy, seizure-frequency,
  dataset-specific, or benchmark-formatting.

"Hybrid" alone is not a research description.

## BP6. Report Model-By-Field Patterns, Not One Universal Leaderboard

Historical source:
`dissertation-experiments/docs/schema_ladder_sweep_findings.md`

Evidence record:

The schema-ladder sweep found no single model dominated all fields. Examples:

- Medication-name extraction was high for Qwen35, GPT-4.1, and Gemini, with
  values around `0.90-0.99` depending on step.
- Seizure type F1 was much lower, around `0.24-0.48` in the ladder.
- Normalized seizure frequency was lower still, around `0.29-0.42`.
- Gemini led diagnosis at one step (`0.711`) but the advantage narrowed when
  frequency was added.
- GPT-5.4-mini had a step-1 medication anomaly (`0.771`) caused by schema design:
  without explicit previous/planned slots, real but non-current medications
  leaked into current medication output.
- Adding frequency improved seizure-type extraction for all models, a positive
  cross-field interaction that contradicted a simple "more fields always hurts"
  hypothesis.

Practice for `clinical_extraction/`:

- Use field-family tables rather than a single model leaderboard.
- Treat schema design as an intervention.
- Look for cross-field interactions; a field can discipline or destabilize an
  adjacent field.
- Keep model choice as an experimental variable, not a hidden implementation
  detail.

## BP7. Use Gold-Standard Audits To Bound Claims

Historical source:
`dissertation-recursive/docs/33_gold_audit_synthesis.md`

Evidence record:

The gold audit revised several alarming-looking headline numbers:

- ExECT span mismatch `13.5%` was mainly spelling-correction offset drift.
- `30` tier-1 dose conflicts across `29` documents were split-dose
  prescriptions, a schema limitation rather than content error.
- ExECT `57` stale CSV rows were a real evaluation-pipeline bug.
- Gan reference mismatches mostly reflected a two-pass annotation workflow.
- Gan `31/1500` labels were unparsable by the project parser.
- Gan seizure-free multiple-month/year labels split into: about `51%` correct
  vague usage, `16%` precision opportunity, and `27%` sub-threshold
  seizure-free labels despite the written 6-month rule.

Practice for `clinical_extraction/`:

- Use gold audits to decide what a score means, not just whether it is high.
- Footnote known gold/schema limitations near any strict benchmark number.
- Prefer clinical headline or pragmatic views when strict exact labels are known
  to encode annotation convention rather than clinical truth.
- Do not use gold-quality caveats to dismiss all benchmark evidence; use them to
  choose the right claim surface.

## BP8. Keep Agent/Process Infrastructure Lean

Historical sources:

- `dissertation/docs/clean_repo_handoff/13_what_did_not_work.md`
- `dspy-extraction/docs/workstreams/cursor_sdk/cursor_sdk_final_value_report_20260525.md`

Evidence record:

The old Evidence Notebook and Pipeline Observatory solved oversight problems but
became too heavy for the final repo. The clean-rebuild rule was to build one
compact visibility cockpit from simple artifacts and avoid multiple UI products.

The Cursor SDK final report reached the same conclusion for agent process: SDK
outputs were useful for lead lists and source maps but not authoritative; the
active workstream was retired to avoid dependency and review burden.

Practice for `clinical_extraction/`:

- Prefer one control surface: `PROJECT_STATUS.md` plus frozen evidence and
  registry indexes.
- Archive historical notes rather than keeping every run note active.
- Use agent-generated reviews as checklists, not as new truth.
- Add process infrastructure only if it directly reduces claim risk.

## BP9. Preserve Negative Results As Design Knowledge

Historical sources:

- `dissertation/docs/clean_repo_handoff/13_what_did_not_work.md`
- `dspy-extraction/docs/workstreams/hybrid/hybrid_deterministic_placement_research_synthesis_20260521.md`
- `dspy-extraction/docs/workstreams/optimizer/dspy_optimizer_vs_manual_engineering_audit_20260520.md`

Evidence record:

The predecessor repos repeatedly turned failures into useful constraints:

- Regex expansion improved deterministic floor but did not answer LLM reliability.
- Example-heavy prompts regressed output validity or routine-case performance.
- Model-size swaps did not fix schema compliance.
- Evidence presence gates were null.
- Broad-only decomposition collapsed broad-field coverage.
- Static pre-vocab/pre-candidates regressed ExECT slices.
- Generic verify-repair regressed ExECT S1 cap-25 by `-9.4pp`.
- GEPA and bootstrap variants often regressed or bloated prompts.

Practice for `clinical_extraction/`:

- Keep negative results in docs, not active code paths.
- When proposing a repeat, state what changed: data surface, component, model,
  scorer, split, or failure mode.
- If nothing changed, do not repeat the experiment.

## Compact Checklist For Any Authorized New Work

Before running:

- What claim would this support?
- What split permits this inspection?
- What component is prediction-bearing?
- What deterministic behavior is semantic versus format-only?
- What scorer and projection path will be used?
- What existing predecessor failure does this avoid?
- What stop rule prevents another open-ended loop?

After running:

- Did the output contract hold?
- Are metrics generated from the intended scorer?
- Are evidence validity and evidence support separated?
- Are field-family tradeoffs visible?
- Is the result validation/dev, frozen aggregate, or diagnostic?
- Does the documentation say what is not claimed?
