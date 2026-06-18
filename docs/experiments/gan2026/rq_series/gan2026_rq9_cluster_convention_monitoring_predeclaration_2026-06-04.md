# Gan 2026 RQ9 Cluster/Convention Monitoring Predeclaration

This is a validation-development predeclaration for monitoring cluster/convention rows left prediction-bearing by the v3 RQ9 selective-action router.

It does not change scorer policy, gold labels, deterministic extraction rules, prompts, projection policy, locked-test behavior, or benchmark-comparable claims.

## Decision

Keep cluster/convention rows prediction-bearing by default. Do not restore wholesale human-review routing. Instead, materialize a monitoring artifact and a high-priority verifier queue for convention-risk subfamilies.

## Eligible Surface

Rows are eligible when they are v3 `predict` rows and their pre-routing ambiguity reasons include `cluster_or_per_cluster_convention`.

## Verifier Priority

Use high-priority verifier monitoring for prediction-bearing cluster/convention rows whose label is not cluster-structured: `no seizure frequency reference`, `unknown`, seizure-free labels, or plain frequency labels where cluster/per-cluster structure may have been flattened. Cluster-structured labels remain routine monitoring.

Verifier priority is not a router action. It is an audit queue for future adjudication, robustness checks, or a separately predeclared verifier experiment.

## Required Accounting

The monitoring artifact must report eligible rows, high-priority verifier rows, routine monitoring rows, development-safe and development-unsafe rows, monitoring groups, and row-level packets with selected evidence.

## Claim Boundary

This predeclaration can support validation-development monitoring. It does not authorize holdout use, scorer changes, gold rewrites, or benchmark-comparable language.
