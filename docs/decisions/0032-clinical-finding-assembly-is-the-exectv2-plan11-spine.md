# ADR 0032: Clinical Finding Assembly Is The ExECTv2 Plan 11 Spine

Date: 2026-06-21

## Status

Accepted. The retained control is v08.

## Context

The best current Plan 11 component-evidence result combines frozen v0.42
Prescription and Investigations controls with focused Diagnosis and
SeizureFrequency lanes. The result is attribution-clean, but the implementation
previously made the report module own source selection, lane assembly, scoring
views, and gate rendering.

That made the architecture read like an artifact-specific report rather than a
clinical extraction system.

## Decision

ExECTv2 Plan 11 assembly is now expressed as:

1. saved candidate producers that emit evidence-backed `ClinicalFinding`
   objects into a per-letter `ClinicalFindingStore`;
2. entity-specific lenses that reconcile producer findings into final clinical
   findings;
3. first-class scoring views rendered from those final findings;
4. an attribution sidecar through `FindingSource` and `ProvenanceEvent`.

The assembly is implemented by the retained v08 control. Historical v01-v07
artifacts documented the path to that control but are no longer active evidence.

## Consequences

- The holistic v08 candidate is the retained ExECT hybrid control.
- Source provenance and deterministic ownership stay row-level and
  prediction-bearing. Semantic lens behavior must be represented as provenance,
  not hidden as normalization.
- This ADR does not authorize a benchmark, full-200, or locked-test claim.

## Verification

The implementation is covered by:

- `tests/test_exectv2_clinical_finding_assembly.py`

The selected report, saved inputs, hashes, and no-call replay command live in
`docs/experiments/retained_evidence_manifest.json`.
