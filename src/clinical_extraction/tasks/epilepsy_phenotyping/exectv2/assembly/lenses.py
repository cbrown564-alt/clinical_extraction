"""Entity-specific finding lenses for the first ExECTv2 assembly pass."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.clinical_finding import (
    ClinicalFinding,
    ProvenanceEvent,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.finding_store import (
    ClinicalFindingStore,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.manifests import (
    LensManifest,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)


@dataclass(frozen=True)
class LensPolicy:
    producer_id: str
    source_lane: str
    ownership_label: str
    portability: str | None


@dataclass(frozen=True)
class LensResult:
    entity: str
    lens_id: str
    findings: tuple[ClinicalFinding, ...]
    diagnostics: dict[str, object]


class EntityLens(Protocol):
    lens_id: str
    entity: str

    def reconcile(
        self,
        store: ClinicalFindingStore,
        *,
        policy: LensPolicy,
    ) -> LensResult:
        ...


@dataclass(frozen=True)
class _ThinArtifactLens:
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


class DiagnosisLens(_ThinArtifactLens):
    pass


class SeizureFrequencyLens(_ThinArtifactLens):
    pass


class PrescriptionLens(_ThinArtifactLens):
    pass


class InvestigationsLens(_ThinArtifactLens):
    pass


def lens_from_manifest(config: LensManifest) -> EntityLens:
    lens_type = {
        DIAGNOSIS.name: DiagnosisLens,
        SEIZURE_FREQUENCY.name: SeizureFrequencyLens,
        PRESCRIPTION.name: PrescriptionLens,
        INVESTIGATIONS.name: InvestigationsLens,
    }.get(config.entity, _ThinArtifactLens)
    return lens_type(lens_id=config.lens, entity=config.entity)
