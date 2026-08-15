"""Investigations lens for ExECTv2 assembly."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.clinical_finding import (
    ProvenanceEvent,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.finding_store import (
    ClinicalFindingStore,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lens_ops import (
    LensPolicy,
    LensResult,
    finding_with_text_attributes,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)

from .base import InvestigationsLens, ThinArtifactLens


class InvestigationsDictionaryLens(ThinArtifactLens):
    """Drop pending-only investigation mentions; keep completed tests.

    Residual providers stay prompt-side. The former full noise/result-binding
    lens rules stay off. This only applies the gold-free pending-cue drop from
    the v0.9.24 codebook (await/request/appointment without a completed result).
    """

    def reconcile(
        self,
        store: ClinicalFindingStore,
        *,
        policy: LensPolicy,
    ) -> LensResult:
        recovered = super().reconcile(store, policy=policy)
        kept = []
        dropped = 0
        stripped = 0
        for finding in recovered.findings:
            repaired_attrs = sd.investigation_convention_attribute_repairs(
                finding.text,
                evidence=finding.evidence or finding.text,
                attributes=finding.attributes,
            )
            current = finding
            if repaired_attrs != {
                str(key): str(value) for key, value in dict(finding.attributes).items()
            }:
                current = finding_with_text_attributes(
                    finding,
                    text=finding.text,
                    attributes=repaired_attrs,
                    owner_suffix="standard_dictionary_investigation_convention",
                    provenance=ProvenanceEvent(
                        stage="entity_lens",
                        action="stripped_cross_modality_not_performed",
                        owner="standard_dictionary",
                        portability="benchmark_format",
                        detail={"lens_id": self.lens_id},
                    ),
                )
                stripped += 1
            if sd.is_pending_investigation(
                current.text,
                evidence=current.evidence or current.text,
                attributes=current.attributes,
            ):
                dropped += 1
                continue
            kept.append(current)
        return LensResult(
            entity=self.entity,
            lens_id=self.lens_id,
            findings=tuple(kept),
            diagnostics={
                **dict(recovered.diagnostics),
                "pending_investigations_dropped": dropped,
                "cross_modality_not_performed_stripped": stripped,
            },
        )


__all__ = [
    "InvestigationsDictionaryLens",
    "InvestigationsLens",
]
