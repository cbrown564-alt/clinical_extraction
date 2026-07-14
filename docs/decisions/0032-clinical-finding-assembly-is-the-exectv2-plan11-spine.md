# 0032: Combine ExECT findings before scoring

Date: 2026-06-21
Status: accepted; selected development reference is `v08`

ExECT extractors emit evidence-backed `ClinicalFinding` objects. Entity-specific
transforms reconcile them into final findings, score-specific views format the
results, and row records preserve source and deterministic changes.

This replaces report code that previously selected sources, combined results,
scored them, and formatted evidence in one place. Version `v08` remains the
selected LLM-with-rules development result. Earlier versions document history
but are not current evidence. This decision does not authorize a benchmark,
full200, or holdout claim.
