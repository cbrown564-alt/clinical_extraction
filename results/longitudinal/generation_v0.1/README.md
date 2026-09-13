# Phase 3: seed-free generation and review

Completed 2026-09-11 (Europe/London; run timestamps are UTC) for synthetic development use. The staged 1 → 5 → 12
authoring/QC run produced **12 accepted patient records, 36 letters, 114 assertions,
39 relationships and 240 query references**. All accepted case files and QC
regenerated exactly from saved authoring outputs. This is internal same-assistant
review, not independent annotation, clinical validation or a dataset release.

The [generation protocol v0.3](../../../docs/longitudinal/generation_protocol.md)
owns the procedure. The [execution configuration](../../../configs/longitudinal/generation_v0.1.json)
pins the program, schema/guide v0.3, query definition v0.2 and authoring instructions.
The [summary](summary.json), [internal review](internal_review.json),
[duplicate audit](duplicate_audit.json) and [replay hashes](replay.json) own the
machine-readable evidence. The roadmap remains the phase-status owner.

## What was generated and checked

Four scenario types are crossed with concise, detailed and shorthand writing.
Each style has exactly the same reference-status distribution: 18 eligible,
13 ineligible and 49 indeterminate. In total there are **54 eligible, 39 ineligible
and 147 indeterminate** answers; 24/120 paired views differ. Thirty-nine answers
cite more than one letter. These are authored-reference counts, not model scores.

| Scenario | Concise | Detailed | Shorthand | Distinction preserved |
| --- | --- | --- | --- | --- |
| Ordinary follow-up | [001](cases/generated-001/manifest.json) | [005](cases/generated-005/manifest.json) | [009](cases/generated-009/manifest.json) | Single recurring pattern, copied diagnosis and administrative follow-up |
| Concurrent patterns and a treatment plan | [002](cases/generated-002/manifest.json) | [006](cases/generated-006/manifest.json) | [010](cases/generated-010/manifest.json) | Ranges, clusters, two distinct patterns, non-use and a later confirmed start |
| Reporter disagreement | [003](cases/generated-003/manifest.json) | [007](cases/generated-007/manifest.json) | [011](cases/generated-011/manifest.json) | Patient denial, caregiver report and clinician uncertainty remain separate |
| Delayed correction and result documentation | [004](cases/generated-004/manifest.json) | [008](cases/generated-008/manifest.json) | [012](cases/generated-012/manifest.json) | Event, decision, result and letter-availability dates remain distinct |

Each case directory contains the final letters, provisional annotations, reference
answers, manifest and four physically filtered inputs. Query answers and authoring
history never appear in those inputs. The ten-file case allowlist excludes raw
histories, failed drafts and review notes from task inputs and this reviewed export.

All 426 assertion, relationship, answer and diagnostic-review items have a recorded
disposition tied to exact case and QC hashes. Automated checks cover IDs, hashes,
schema, spans, dates, quantity bounds, links, fixed query schedules, cutoff inputs
and definitive-answer evidence. Review additionally checked interpretation,
exhaustive negative scope, contradiction provenance and each query reason. No
unresolved internal defect remains; this does not prove clinical correctness.

The duplicate audit compared all 36 new letters with one another and with the
36 Phase 2 authored letters. It removes the generated metadata header before
casefolded word-token matching and five-token-shingle Jaccard comparison at 0.8.
No exact normalized or threshold-level candidate pairs were found. The four
scenario histories and common authoring template still provide known shared
ancestry: **all twelve records stay in one conservative development family**.
Low text similarity does not establish independence. No ExECT/Gan source records
were loaded or licensed for this run; seeded generation remains disabled.

## Revisions and retained failures

The local directory `runs/longitudinal/generation_v0.1/` retains 35 capture records
across five run revisions, representing 22 distinct raw outputs. Captures are
immutable; a changed successful capture starts a new run revision. Stage reviews
and explicit amendments retain superseded acceptances. These counts include
unchanged captures carried into a new run, not 35 independent generations.

- The first draft paraphrased frequency text and omitted stated time wording.
  The revision retains exact source wording and the copied diagnosis's anchor.
- Five-case review found shared query reasons mentioning information from another
  cutoff. Revised reasons use only the relevant permitted evidence. Further review
  removed two remaining anticipatory explanations from the delayed-correction case.
- The full date audit found a one-day gap in the delayed-correction scenario's
  EEG-request inventory. The second lookback starts on **2 February**, while the
  letter excludes requests only from **3 February**. The final letters were kept
  unchanged and three Q4 references changed from ineligible to indeterminate.
  Hidden intended absence did not fill the missing day. A separate query reason's
  printed lookback date was corrected at the same time.

Every planned patient remains in the final denominator. No patient was removed
because an extractor disagreed, and all 36 final letter bytes match the first
complete twelve-patient capture. The failed/resumed-capture tests separately
exercise malformed JSON, process interruption, source changes and stale review.
No model-call failures occurred because no separate model provider was called.

## Diagnostic and claim limits

The unchanged development query diagnostic matches **207/240** references. Its
33 mismatches remain in `summary.json` with case/request IDs and review reasons:
12 ordinary-case single-pattern negatives and 21 delayed-correction cases involving
diagnosis withdrawal, corrected event identity, absence and complete reassessment
history. Three of these are harmful eligible answers after explicit diagnosis
withdrawal; the other 30 abstain. Agreement was never an acceptance condition.
Phase 4 should use these examples alongside the eleven Phase 2 mechanism cases.

Draft annotations were authored alongside letters, followed by final-text review
and revisions. There was no blinded annotation pass. Patient-reported burden and
an explicitly attributed clinician interpretation sometimes share one assertion;
separating them is a recorded acceptable alternative. Negative reinterpretation
history remains partly in query evidence because schema v0.3 has no general field
for its exhaustive inventory. Expert review and annotation effort remain unmeasured.

[Prompt audit](prompt_audit.json): the rendered example was inspected; language is
plain, research metadata is separate, non-obvious fields have descriptions, jargon
is removed or defined, and length matches the task. There are no controlled-prompt
deviations. The [rendering](rendered_annotation_example.json) is an inspection-only
recipe, not a claimed external provider request. Model family is recorded as
supplied by this Codex session; the exact hosted snapshot and sampling parameters
were unavailable. Fresh stochastic authoring is not claimed to reproduce bytes.

[Workload](workload.json) records about 80.2 minutes of elapsed task time through
package creation, including protocol, code, authoring, review, debugging and
verification. Stage capture/review timestamps are in the summary. This is neither
active human labor nor isolated annotation time. Additional provider calls and
API charges were zero; assistant account cost is unknown. No paid fallback,
outreach, corpus freeze or release occurred.

## Reproduce and verify

From the repository root, activate `.venv`. Raw authoring outputs remain local;
replay needs the retained capture directory. Use a new destination for each replay:

```sh
source .venv/bin/activate
python scripts/longitudinal/generate_seed_free_batch.py replay \
  --run runs/longitudinal/generation_v0.1/capture-r5 \
  --destination scratch/generation-v0.1-replay
python scripts/longitudinal/summarize_generation_batch.py \
  --run runs/longitudinal/generation_v0.1/capture-r5 \
  --output results/longitudinal/generation_v0.1
python -m pytest tests/test_longitudinal_generation.py tests/test_longitudinal_annotations.py
```

The summary command recomputes QC and refuses to replace differing reviewed output.
On a checkout without local raw captures, `verify_patient_case.py` can still check
each bundled case. The local regenerated working batch is
`data/longitudinal/generation_v0.1/`. Changed code/configuration must use a new run
revision; never bypass a failed hash check to overwrite evidence.

Verification on the final code: **26 focused tests passed**. The full always-on
suite reported **806 passed and two pre-existing failures**:
`test_published_documents_match_the_pipeline` and
`test_inventory_covers_present_and_missing_cells`. Ruff passed for `src`, `tests`
and longitudinal scripts; mypy passed for all 399 source files; documentation
hygiene passed. Phase 2 verification still reproduces its query/timing evidence
and all 48 source-letter/reference preservation hashes. No frontend files changed,
so frontend/browser checks were not needed; deep tests and model calls were not run.

Phase 3 is complete for the declared seed-free development scope. The next work is
the Phase 4 extraction/history/query loop, not larger-scale generation or a claim
of clinical validation.
