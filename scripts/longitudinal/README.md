# Longitudinal scripts

Run commands from the repository root inside `.venv`, with the `dev` extra installed.

- `check_annotations.py`: canonical schema, evidence, bounds and relationship checks.
- `verify_patient_case.py <case_dir>`: full authored-case integrity, fixed schedule,
  exact filtered inputs and reference checks; reuses the annotation checker.
- `build_patient_case.py <case_dir>`: rebuild filtered inputs and README tables from
  reviewed case files. Letters, annotations and references are canonical authored
  data. The obsolete duplicated Python authoring script has been removed.
- `run_pilot_scoring_dry_run.py`: verify all cases and write the v0.2 reference
  summary and constant-status baselines, with input/program hashes. Agreement,
  effort and field sensitivity remain unavailable until actually measured.

These checks do not establish clinical entailment, annotation completeness or
independent agreement. See the canonical pilot review for remaining work.


`run_agy_annotation_pass.py` captures isolated agy jobs under the predeclared
protocol. It resumes saved attempts, checks input hashes, stops scheduling after
failure and never sends references to the model. The high-effort diagnostic and
medium-effort pass are separate. `analyze_agy_annotation_pass.py` replays saved
outputs: status agreement, exact evidence validity and a deliberately limited
literal-content assertion/link comparison. A partial pass has no full-pass score.
These scripts do not authorize paid API calls or repair clinical output.

`audit_temporal_relationships.py` reads saved successful independent outputs and
separates time wording/null encodings from bounds/kind/anchor differences on
uniquely matched content. It writes the temporal/link review artifact; it does
not adjudicate all clinical differences or calculate unrestricted link accuracy.

`evaluate_q5_slice.py` runs the patient-001 Q5 positive-witness prototype and
replays correction-link, decision-time and time-wording removals. It writes
`results/longitudinal/pilot_v0.5/q5_field_ablation.json`. It does not infer complete
negative revision history, implement all five queries, or call a model.

The current Q5 replay writes `pilot_v0.6/q5_field_ablation.json` and additionally
supports explicit patient-wide first-reinterpretation evidence for the bounded
negative case. The earlier v0.5 replay remains a historical artifact.

## Current pilot review extension

`evaluate_query_witnesses.py` writes v0.8, evaluating all 240 requests under nine
field variants. It is a conservative, incomplete Q1–Q4 witness evaluator with
the existing Q5 implementation. Expected answers are compared after prediction.
`review_pilot_alignment.py` and `summarize_pilot_review.py` belong to the historical
v0.7 review and still target that directory; do not use them to overwrite frozen
v0.7 evidence with later annotations.

`run_timed_annotation_probe.py` executes the declared 18-call agy study serially,
with no retries or paid fallback. The manifest records the user's confirmation of
zero per-call charge. Capture stops after a CLI, tool, timeout or parse failure;
schema, grounding and offset checks are separate offline diagnostics. Re-running
the capture command resumes saved attempts; it does not repair failed outputs.

`summarize_timed_annotation_probe.py` replays the saved outputs and reports wall
time by the four families and two focused temporal/relationship activities.
Literal and evidence-constrained alignment remain limited representation
comparisons. `verify_phase2_pilot.py` checks the case pack, preservation hashes,
review coverage, query/timing replay parity and generation-configuration pins.
Neither command makes model calls. See the
[v0.8 evidence entry](../../results/longitudinal/pilot_v0.8/README.md) and the
[generation protocol](../../docs/longitudinal/generation_protocol.md).

## Seed-free generation and review

`generate_seed_free_batch.py` captures saved same-assistant authoring outputs,
renders exact quotes and filtered inputs, and runs case/QC checks. Its `capture`,
`review` and `replay` commands enforce immutable attempts, version/hash matching,
explicit retry of failed or interrupted captures, disabled providers and recorded
internal review before stage expansion. Semantic review is recorded per assertion,
relationship, answer and diagnostic mismatch; automated checks cannot supply it.
Changed successful inputs require a new run revision.

`summarize_generation_batch.py` recomputes reviewed QC, style/scenario counts,
query diagnostics, normalized duplicate/shingle candidates and lineage records.
It copies only the ten explicitly allowed final case files per patient and refuses
to overwrite differing reviewed results. Hidden histories and raw attempts stay
under ignored `runs/`; they never enter filtered task inputs.

The completed 1 → 5 → 12 run, rejected drafts, claim limits and replay commands
are in the [Phase 3 record](../../results/longitudinal/generation_v0.1/README.md).
The [execution configuration](../../configs/longitudinal/generation_v0.1.json)
pins the program and document versions. The governing provenance/recovery tests
are `tests/test_longitudinal_generation.py`; the existing annotation tests continue
to own evidence shape and cutoff validation.

## Phase 4 prototype

`run_prototype.py` replays the independent saved extractions, infers links from
permitted facts, assembles both histories and evaluates all five queries. It
writes the frontend inputs and component comparison under
`results/longitudinal/prototype_v0.1/`. `verify_prototype.py` checks the resulting
hashes, exact evidence, cutoffs and failure denominators. Neither makes model calls.
The new implementation lives in `src/clinical_extraction/longitudinal/`; frozen
pilot diagnostics remain unchanged. See the [prototype record](../../results/longitudinal/prototype_v0.1/README.md)
for commands, known limitations and browser verification.
