# Outputs

Each JSONL row has `id`, overall `status`, `package_version`, `model`,
`workflows`, and `warnings`. A workflow block has `status` and either `result`
or a stable, privacy-safe `error`.

The `seizure_frequency` result contains `value`, `kind`, exact `evidence`, an
`evidence_exact` check, `rationale`, `first_prediction_owner`, and named
`deterministic_changes`. Unknown frequency, no reference, seizure-free, ranges,
clusters, and vague frequency remain distinct where the selected workflow does.

The `clinical_findings` result has `diagnoses`, `seizure_frequencies`,
`prescriptions`, and `investigations`. Each finding contains family, value,
attributes, exact evidence state, model origin, deterministic actions, and
warnings. These seizure-frequency findings are not the Gan-derived single
current answer.

Overall status is `ok`, `partial`, or `error`. Error codes include
`configuration_error`, `input_validation_error`, `endpoint_error`,
`schema_validation_failure`, `resume_mismatch`, and `unexpected_error`.

An optional trace row contains the prompt payload, actual schema, raw model
response, parsing notes, intermediate events or findings, evidence gates, and
component attribution. It is private clinical data.

