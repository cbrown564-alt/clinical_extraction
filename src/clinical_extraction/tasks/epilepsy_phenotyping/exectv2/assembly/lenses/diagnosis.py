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
    diagnosis_added_finding,
    diagnosis_finding_with_text,
    rewrite_counts,
    text_counts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
)

from .base import DiagnosisLens, ThinArtifactLens

_DIAGNOSIS_POLICY_VARIANTS = frozenset(
    {
        "default",
        "residual_subsumption_only",
        "absence_preservation_only",
        "combined",
    }
)


class DiagnosisHeadingRecoveryLens(ThinArtifactLens):
    """Legacy lens identity retained as a behavior-preserving thin adapter."""

    pass


class DiagnosisDictionaryLens(ThinArtifactLens):
    """Standard-dictionary Diagnosis repair over saved model findings.

    The former heading-recovery and generic-companion additions are retained
    only in historical artifacts; the selected v10 lens keeps the active
    dictionary rewrites, noise filtering, attribute repair, and residual
    additions.
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
        preserve_absence = variant in {"absence_preservation_only", "combined"}
        suppress_subsumed_residual = variant in {
            "residual_subsumption_only",
            "combined",
        }
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
            preserve_absence_phenotype = (
                (policy.model_preserving_policy_candidate or preserve_absence)
                and _is_model_owned_absence_phenotype(current, recovered.findings)
            )
            if sd.is_diagnosis_convention_noise(
                current.text,
                evidence=current.evidence or current.text,
                diag_category=current.attributes.get("DiagCategory"),
            ) and not preserve_absence_phenotype:
                dropped.append(current)
                continue
            kept.append(current)

        kept = list(sd.drop_syndrome_covered_phenotypes(kept))

        added: list[ClinicalFinding] = []
        addition_rule_categories: list[str] = []
        for text, evidence in sd.diagnosis_residual_additions(
            store.note_text,
            include_resolution_candidate=policy.diagnosis_resolution_candidate,
        ):
            if _has_diagnosis_concept(
                [*kept, *added],
                text=text,
                include_resolution_candidate=policy.diagnosis_resolution_candidate,
            ):
                continue
            selected_texts = [finding.text for finding in [*kept, *added]]
            if sd.is_redundant_diagnosis_residual_addition(
                text,
                evidence=evidence,
                selected_texts=selected_texts,
                include_resolution_candidate=policy.diagnosis_resolution_candidate,
                model_preserving_policy_candidate=(
                    policy.model_preserving_policy_candidate
                    or suppress_subsumed_residual
                ),
            ):
                continue
            new_finding = diagnosis_added_finding(
                store,
                text=text,
                evidence=evidence,
                selected=[*kept, *added],
                policy=policy,
                lens_id=self.lens_id,
                rule_category=sd.diagnosis_residual_addition_category(text, evidence),
            )
            if new_finding is not None:
                added.append(new_finding)
                addition_rule_categories.append(
                    sd.diagnosis_residual_addition_category(text, evidence)
                )

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


def _is_model_owned_absence_phenotype(
    finding: ClinicalFinding,
    recovered: tuple[ClinicalFinding, ...],
) -> bool:
    if canonicalize_diagnosis_concept(finding.text) != "absence seizures":
        return False
    if finding.source.fact_origin != "target_model_generated":
        return False
    if finding.attributes.get("Negation") != "Affirmed":
        return False
    return any(
        other.finding_id != finding.finding_id
        and other.source.fact_origin == "target_model_generated"
        and other.attributes.get("Negation") == "Affirmed"
        and "absence epilepsy" in canonicalize_diagnosis_concept(other.text)
        for other in recovered
    )


def _has_diagnosis_concept(
    findings: list[ClinicalFinding],
    *,
    text: str,
    include_resolution_candidate: bool = False,
) -> bool:
    target = canonicalize_diagnosis_concept(text)
    for finding in findings:
        concept = canonicalize_diagnosis_concept(finding.text)
        if concept == target:
            return True
        fragments = {"drug", "focal", "generalised", "occipital", "secondary", "symptomatic"}
        if include_resolution_candidate:
            fragments.remove("symptomatic")
        if target in fragments:
            if target in concept.split():
                return True
    return False


__all__ = [
    "DiagnosisDictionaryLens",
    "DiagnosisHeadingRecoveryLens",
    "DiagnosisLens",
]
