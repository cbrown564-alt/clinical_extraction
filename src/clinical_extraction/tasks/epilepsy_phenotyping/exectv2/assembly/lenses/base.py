"""Shared lens scaffolding for ExECTv2 assembly."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.clinical_finding import (
    ProvenanceEvent,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.finding_store import (
    ClinicalFindingStore,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lens_ops import (
    LensPolicy,
    LensResult,
)


class EntityLens(Protocol):
    lens_id: str
    entity: str

    def reconcile(
        self,
        store: ClinicalFindingStore,
        *,
        policy: LensPolicy,
    ) -> LensResult: ...


@dataclass(frozen=True)
class ThinArtifactLens:
    lens_id: str
    entity: str

    def reconcile(
        self,
        store: ClinicalFindingStore,
        *,
        policy: LensPolicy,
    ) -> LensResult:
        selected = store.findings(
            entity=self.entity,
            producer_id=policy.producer_id,
            raw_surface=False,
        )
        event = ProvenanceEvent(
            stage="entity_lens",
            action="selected_saved_artifact_mentions",
            owner=policy.ownership_label,
            portability=policy.portability,
            detail={
                "lens_id": self.lens_id,
                "producer_id": policy.producer_id,
                "source_lane": policy.source_lane,
                "behavior": "thin_behavior_preserving_adapter",
            },
        )
        final_findings = tuple(finding.with_provenance(event) for finding in selected)
        return LensResult(
            entity=self.entity,
            lens_id=self.lens_id,
            findings=final_findings,
            diagnostics={
                "selected_findings": len(final_findings),
                "producer_id": policy.producer_id,
                "source_lane": policy.source_lane,
            },
        )


class DiagnosisLens(ThinArtifactLens):
    pass


class SeizureFrequencyLens(ThinArtifactLens):
    pass


class PrescriptionLens(ThinArtifactLens):
    pass


class InvestigationsLens(ThinArtifactLens):
    pass
