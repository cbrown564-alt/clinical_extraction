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
