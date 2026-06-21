# ADR 0032: Clinical Finding Assembly Is The ExECTv2 Plan 11 Spine

Date: 2026-06-21

## Status

Accepted for the dev140 Plan 11 structural replay.

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

The v01 implementation is behavior-preserving. Lenses are thin saved-artifact
adapters, and no clinical logic was rewritten. The manifest
`configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v01_dev140.yaml`
selects the same frozen source artifacts as the focused-lane replay.

## Consequences

- The focused-lane report remains available as a compatibility wrapper.
- The holistic candidate
  `exectv2_holistic_finding_assembly_v01_dev140` reproduces the focused-lane
  dev140 score ladder while explaining the system as findings, lenses, and
  views.
- Source provenance and deterministic ownership stay row-level and
  prediction-bearing. Semantic lens behavior must be represented as provenance,
  not hidden as normalization.
- This ADR does not authorize a benchmark, full-200, or locked-test claim.

## Verification

The implementation is covered by:

- `tests/test_exectv2_clinical_finding_assembly.py`
- `tests/test_exectv2_focused_lane_component_evidence.py`

The generated replay artifact is:

`docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v01_dev140_20260621.md`
