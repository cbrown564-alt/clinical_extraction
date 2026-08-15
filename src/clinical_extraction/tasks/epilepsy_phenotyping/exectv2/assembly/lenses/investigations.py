"""Investigations lens for ExECTv2 assembly."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.finding_store import (
    ClinicalFindingStore,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lens_ops import (
    LensPolicy,
    LensResult,
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
        for finding in recovered.findings:
            if sd.is_pending_investigation(
                finding.text,
                evidence=finding.evidence or finding.text,
                attributes=finding.attributes,
            ):
                dropped += 1
                continue
            kept.append(finding)
        return LensResult(
            entity=self.entity,
            lens_id=self.lens_id,
            findings=tuple(kept),
            diagnostics={
                **dict(recovered.diagnostics),
                "pending_investigations_dropped": dropped,
            },
        )


__all__ = [
    "InvestigationsDictionaryLens",
    "InvestigationsLens",
]
