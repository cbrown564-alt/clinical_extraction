"""Diagnosis entity lenses for ExECTv2 assembly."""

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.clinical_finding import (
    ClinicalFinding,
    FindingSource,
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
    evidence_is_grounded,
    first_source_finding,
    has_diagnosis_text_with_evidence,
    rewrite_counts,
    text_counts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import DIAGNOSIS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
    diagnosis_category_for_concept,
)

from .base import DiagnosisLens, ThinArtifactLens

_DIAGNOSIS_HEADING = re.compile(
    r"\bDiagnosis\s*:\s*(?P<section>.{0,220})",
    re.IGNORECASE | re.DOTALL,
)
_DIAGNOSIS_HEADING_STOP = re.compile(
    r"\b(?:Current\s+(?:anti[- ]?epileptic\s+)?medication|"
    r"Previous\s+(?:anti[- ]?epileptic\s+)?medication|Investigations|"
    r"Seizure\s+type\s+and\s+frequency|I reviewed|Thank you|Yours|Plan:)\b",
    re.IGNORECASE,
)
_FOCAL_EPILEPSY = re.compile(r"(?<![A-Za-z])focal[-\s]+epilepsy(?![A-Za-z])", re.IGNORECASE)
_CERTAINTY_4_CUE = re.compile(
    r"\b(?:probable|likely|suggestive|suspected|possible|possibly|query|\?)\b",
    re.IGNORECASE,
)


class DiagnosisHeadingRecoveryLens(ThinArtifactLens):
    """Recover explicit focal-epilepsy Diagnosis-heading concepts.

    This is a deliberately narrow, dev140-derived clinical-epilepsy rule group:
    it only adds a Diagnosis mention when the `Diagnosis:` heading itself names
    focal epilepsy. Broader heading/seizure-type recovery was ablated and hurt
    precision, so it stays out of this lens.
    """

    def reconcile(
        self,
        store: ClinicalFindingStore,
        *,
        policy: LensPolicy,
    ) -> LensResult:
        selected = list(
            store.findings(
                entity=self.entity,
                producer_id=policy.producer_id,
                raw_surface=False,
            )
        )
        added = _focal_epilepsy_heading_findings(
            store,
            selected=selected,
            policy=policy,
            lens_id=self.lens_id,
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
                "behavior": "saved_artifact_plus_focal_epilepsy_heading_recovery",
            },
        )
        final_findings = tuple(
            [finding.with_provenance(event) for finding in selected] + list(added)
        )
        return LensResult(
            entity=self.entity,
            lens_id=self.lens_id,
            findings=final_findings,
            diagnostics={
                "selected_findings": len(selected),
                "added_heading_recovery_findings": len(added),
                "producer_id": policy.producer_id,
                "source_lane": policy.source_lane,
            },
        )


class DiagnosisDictionaryLens(DiagnosisHeadingRecoveryLens):
    """v09 Diagnosis: focal-epilepsy heading recovery plus standard-dictionary
    benchmark/convention repair sourced from ``standard_dictionary``.

    This is the single-GPT-engine replacement for the v03-v05 lens chain: the
    convention rewrites, noise drops, and dev residual additions all come from
    the shared dictionary rather than being inlined here.
    """

    def reconcile(
        self,
        store: ClinicalFindingStore,
        *,
        policy: LensPolicy,
    ) -> LensResult:
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
            repaired_attributes = sd.diagnosis_convention_attribute_repairs(
                current.text,
                evidence=current.evidence or current.text,
                attributes=current.attributes,
            )
            if repaired_attributes != dict(current.attributes):
                current = diagnosis_finding_with_text(
                    current,
                    current.text,
                    owner_suffix="standard_dictionary_diagnosis_attributes",
                    provenance=ProvenanceEvent(
                        stage="entity_lens",
                        action="repaired_diagnosis_attributes_from_dictionary",
                        owner="standard_dictionary",
                        portability="benchmark_format",
                        detail={
                            "lens_id": self.lens_id,
                            "rule_category": "benchmark_format",
                            "target_text": current.text,
                        },
                    ),
                )
                rewritten.append(current)
            kept.append(current)

        added: list[ClinicalFinding] = []
        for text, evidence in sd.diagnosis_residual_additions(store.note_text):
            if _has_diagnosis_concept([*kept, *added], text=text):
                continue
            selected_texts = [finding.text for finding in [*kept, *added]]
            if sd.is_redundant_diagnosis_residual_addition(
                text,
                evidence=evidence,
                selected_texts=selected_texts,
            ):
                continue
            finding = diagnosis_added_finding(
                store,
                text=text,
                evidence=evidence,
                selected=[*kept, *added],
                policy=policy,
                lens_id=self.lens_id,
            )
            if finding is not None:
                added.append(finding)

        companion_added: list[ClinicalFinding] = []
        for finding in [*kept, *added]:
            if not sd.should_add_generic_epilepsy_companion(
                finding.text,
                evidence=finding.evidence or finding.text,
                attributes=finding.attributes,
            ):
                continue
            if has_diagnosis_text_with_evidence(
                [*kept, *added, *companion_added],
                text="epilepsy",
                evidence=finding.evidence or finding.text,
                attributes=finding.attributes,
            ):
                continue
            companion_added.append(
                diagnosis_finding_with_text(
                    finding,
                    "epilepsy",
                    owner_suffix="standard_dictionary_generic_epilepsy_companion",
                    provenance=ProvenanceEvent(
                        stage="entity_lens",
                        action="added_generic_epilepsy_companion_from_dictionary",
                        owner="standard_dictionary",
                        portability="benchmark_format",
                        detail={
                            "lens_id": self.lens_id,
                            "rule_category": "benchmark_format",
                            "source_text": finding.text,
                            "target_text": "epilepsy",
                        },
                    ),
                )
            )

        event = ProvenanceEvent(
            stage="entity_lens",
            action="applied_standard_dictionary_diagnosis_repair",
            owner="standard_dictionary",
            portability="benchmark_format",
            detail={
                "lens_id": self.lens_id,
                "producer_id": policy.producer_id,
                "source_lane": policy.source_lane,
                "rule_category": "benchmark_format",
                "rewritten_count": len(rewritten),
                "rewritten_text_counts": rewrite_counts(rewritten),
                "added_count": len(added),
                "added_text_counts": text_counts(list(added)),
                "companion_added_count": len(companion_added),
                "companion_added_text_counts": text_counts(list(companion_added)),
                "dropped_count": len(dropped),
                "dropped_text_counts": text_counts(dropped),
            },
        )
        final_findings = tuple(
            [finding.with_provenance(event) for finding in kept]
            + [finding.with_provenance(event) for finding in added]
            + [finding.with_provenance(event) for finding in companion_added]
        )
        diagnostics = dict(recovered.diagnostics)
        diagnostics.update(
            {
                "lens_id": self.lens_id,
                "rewritten_dictionary_findings": len(rewritten),
                "added_dictionary_findings": len(added),
                "companion_dictionary_findings": len(companion_added),
                "dropped_dictionary_findings": len(dropped),
                "selected_findings": len(final_findings),
            }
        )
        return LensResult(
            entity=self.entity,
            lens_id=self.lens_id,
            findings=final_findings,
            diagnostics=diagnostics,
        )


def _focal_epilepsy_heading_findings(
    store: ClinicalFindingStore,
    *,
    selected: list[ClinicalFinding],
    policy: LensPolicy,
    lens_id: str,
) -> tuple[ClinicalFinding, ...]:
    section_match = _DIAGNOSIS_HEADING.search(store.note_text)
    if section_match is None:
        return ()
    section = section_match.group("section")
    stop = _DIAGNOSIS_HEADING_STOP.search(section)
    if stop is not None:
        section = section[: stop.start()]
    focal_match = _FOCAL_EPILEPSY.search(section)
    if focal_match is None:
        return ()

    evidence = focal_match.group(0)
    attributes = {
        "DiagCategory": diagnosis_category_for_concept("focal epilepsy"),
        "Certainty": "4" if _CERTAINTY_4_CUE.search(section[: focal_match.end()]) else "5",
        "Negation": "Affirmed",
    }
    if _has_diagnosis_concept(selected, text="focal epilepsy"):
        return ()
    if _has_diagnosis_key(
        selected, text="focal epilepsy", attributes=attributes
    ) or _has_diagnosis_concept(selected, text="focal epilepsy"):
        return ()

    source_seed = selected[0] if selected else first_source_finding(store, policy)
    if source_seed is None:
        return ()
    source = FindingSource(
        producer_id=source_seed.source.producer_id,
        artifact_path=source_seed.source.artifact_path,
        pipeline_family=source_seed.source.pipeline_family,
        model=source_seed.source.model,
        prompt_version=source_seed.source.prompt_version,
        mode=source_seed.source.mode,
        ownership_label=f"{policy.ownership_label}+deterministic_heading_recovery",
        source_lane=policy.source_lane,
        fact_origin="post_model_rescue",
    )
    finding = ClinicalFinding(
        finding_id=f"{store.letter_id}:{policy.producer_id}:Diagnosis:lens:{lens_id}:focal_epilepsy",
        letter_id=store.letter_id,
        entity=DIAGNOSIS.name,
        text="focal epilepsy",
        attributes=attributes,
        evidence=evidence,
        normalized_concept="focal epilepsy",
        assertion=attributes["Certainty"],
        confidence="high",
        source=source,
        provenance=(
            ProvenanceEvent(
                stage="entity_lens",
                action="added_focal_epilepsy_from_diagnosis_heading",
                owner="deterministic_heading_recovery",
                portability=policy.portability or "clinical_epilepsy",
                detail={
                    "lens_id": lens_id,
                    "producer_id": policy.producer_id,
                    "source_lane": policy.source_lane,
                    "rule_category": "clinical_epilepsy",
                    "evidence": evidence,
                },
            ),
        ),
        rationale="The Diagnosis heading explicitly names focal epilepsy.",
        evidence_valid=evidence_is_grounded(store.note_text, evidence),
        raw_surface=False,
    )
    return (finding,)


def _has_diagnosis_key(
    findings: list[ClinicalFinding],
    *,
    text: str,
    attributes: dict[str, str],
) -> bool:
    target_attrs = tuple(sorted(attributes.items()))
    for finding in findings:
        attrs = {
            key: value
            for key, value in dict(finding.attributes).items()
            if key not in {"CUI", "CUIPhrase"}
        }
        if finding.text == text and tuple(sorted(attrs.items())) == target_attrs:
            return True
    return False


def _has_diagnosis_concept(findings: list[ClinicalFinding], *, text: str) -> bool:
    target = canonicalize_diagnosis_concept(text)
    for finding in findings:
        concept = canonicalize_diagnosis_concept(finding.text)
        if concept == target:
            return True
        if target in {"drug", "focal", "generalised", "occipital", "secondary", "symptomatic"}:
            if target in concept.split():
                return True
    return False


__all__ = [
    "DiagnosisDictionaryLens",
    "DiagnosisHeadingRecoveryLens",
    "DiagnosisLens",
]
