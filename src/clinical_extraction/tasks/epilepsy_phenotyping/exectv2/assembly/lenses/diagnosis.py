"""Diagnosis entity lenses for ExECTv2 assembly."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.clinical_finding import (
    ClinicalFinding,
    ProvenanceEvent,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.finding_store import (
    ClinicalFindingStore,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lens_ops import (
    LensPolicy,
    LensResult,
    diagnosis_finding_with_text,
    rewrite_counts,
    text_counts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)

from .base import DiagnosisLens, ThinArtifactLens

_DIAGNOSIS_POLICY_VARIANTS = frozenset({"default"})


class DiagnosisHeadingRecoveryLens(ThinArtifactLens):
    """Legacy lens identity retained as a behavior-preserving thin adapter."""

    pass


class DiagnosisDictionaryLens(ThinArtifactLens):
    """Standard-dictionary Diagnosis repair over saved model findings.

    The former heading-recovery, generic-companion, and residual
    additions are retained only in historical artifacts. The selected
    lens keeps dictionary rewrites, noise filtering, and attribute
    repair.
    """

    def reconcile(
        self,
        store: ClinicalFindingStore,
        *,
        policy: LensPolicy,
    ) -> LensResult:
        variant = policy.diagnosis_policy_variant
        if variant not in _DIAGNOSIS_POLICY_VARIANTS:
            raise ValueError(f"unknown Diagnosis policy variant: {variant}")
        recovered = super().reconcile(store, policy=policy)
        kept: list[ClinicalFinding] = []
        rewritten: list[ClinicalFinding] = []
        dropped: list[ClinicalFinding] = []
        for finding in recovered.findings:
            current = finding
            target = sd.diagnosis_convention_target(finding.text, finding.evidence or finding.text)
            if target is not None:
                current = diagnosis_finding_with_text(
                    finding,
                    target,
                    owner_suffix="standard_dictionary_diagnosis_convention",
                    provenance=ProvenanceEvent(
                        stage="entity_lens",
                        action="rewrote_diagnosis_convention_from_dictionary",
                        owner="standard_dictionary",
                        portability="benchmark_format",
                        detail={
                            "lens_id": self.lens_id,
                            "rule_category": "benchmark_format",
                            "source_text": finding.text,
                            "target_text": target,
                        },
                    ),
                )
                rewritten.append(current)
            if sd.is_diagnosis_convention_noise(
                current.text,
                evidence=current.evidence or current.text,
                diag_category=current.attributes.get("DiagCategory"),
            ):
                dropped.append(current)
                continue
            kept.append(current)

        kept = list(sd.drop_syndrome_covered_phenotypes(kept))

        added: list[ClinicalFinding] = []
        addition_rule_categories: list[str] = []

        event = ProvenanceEvent(
            stage="entity_lens",
            action="applied_standard_dictionary_diagnosis_repair",
            owner="standard_dictionary",
            portability=(
                "clinical_epilepsy"
                if "clinical_epilepsy" in addition_rule_categories
                else "benchmark_format"
            ),
            detail={
                "lens_id": self.lens_id,
                "producer_id": policy.producer_id,
                "source_lane": policy.source_lane,
                "rule_categories": sorted(
                    {"benchmark_format", *addition_rule_categories}
                ),
                "rewritten_count": len(rewritten),
                "rewritten_text_counts": rewrite_counts(rewritten),
                "added_count": len(added),
                "added_text_counts": text_counts(list(added)),
                "dropped_count": len(dropped),
                "dropped_text_counts": text_counts(dropped),
                "diagnosis_policy_variant": variant,
            },
        )
        final_findings = tuple(
            [finding.with_provenance(event) for finding in kept]
            + [finding.with_provenance(event) for finding in added]
        )
        diagnostics = dict(recovered.diagnostics)
        diagnostics.update(
            {
                "lens_id": self.lens_id,
                "rewritten_dictionary_findings": len(rewritten),
                "added_dictionary_findings": len(added),
                "dropped_dictionary_findings": len(dropped),
                "selected_findings": len(final_findings),
                "diagnosis_policy_variant": variant,
            }
        )
        return LensResult(
            entity=self.entity,
            lens_id=self.lens_id,
            findings=final_findings,
            diagnostics=diagnostics,
        )


__all__ = [
    "DiagnosisDictionaryLens",
    "DiagnosisHeadingRecoveryLens",
    "DiagnosisLens",
]
