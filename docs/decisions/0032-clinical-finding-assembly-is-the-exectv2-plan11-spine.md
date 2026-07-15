# 0032: Combine ExECT findings before scoring

Date: 2026-06-21
Status: accepted; `v08` is the retained historical development control

ExECT extractors emit evidence-backed `ClinicalFinding` objects. Entity-specific
transforms reconcile them into final findings, score-specific views format the
results, and row records preserve source and deterministic changes.

This replaces report code that previously selected sources, combined results,
scored them, and formatted evidence in one place. Version `v08` remains the
selected historical LLM-with-rules development result. Earlier versions
document history but are not current evidence. This decision does not authorize
a benchmark, full200, or holdout claim.

Amendment, 2026-07-15: `v08` uses a deterministic Prescription producer and a
Seizure Frequency extractor union. It remains reproducible evidence but does
not meet the final model-led family ownership contract in
[decision 0040](0040-final-exect-llm-with-rules-family-ownership.md).
