"""Entity-specific finding lenses for the first ExECTv2 assembly pass."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

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
    finding_with_text_attributes,
    first_source_finding,
    has_diagnosis_text_with_evidence,
    rewrite_counts,
    source_for_residual,
    text_counts,
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
    diagnosis_category_for_concept,
    normalize_phrase,
)

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


class DiagnosisHeadingRecoveryLens(_ThinArtifactLens):
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
            target = sd.diagnosis_convention_target(
                finding.text, finding.evidence or finding.text
            )
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


class SeizureFrequencyDictionaryLens(_ThinArtifactLens):
    """v09 SeizureFrequency: thin standard-dictionary benchmark rewrites only.

    Type/state precision is owned by the v0.9 prompt; this lens only applies the
    small set of benchmark CUIPhrase rewrites from ``standard_dictionary``.
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
        out: list[ClinicalFinding] = []
        rewritten = 0
        dropped: list[ClinicalFinding] = []
        seen_exact: set[tuple[str, tuple[tuple[str, str], ...], str]] = set()
        for finding in selected:
            rewrite = sd.sf_convention_rewrite(
                finding.text,
                evidence=finding.evidence or finding.text,
                attributes=finding.attributes,
            )
            if rewrite is not None:
                new_text, new_attrs, rule_id = rewrite
                finding = finding_with_text_attributes(
                    finding,
                    text=new_text,
                    attributes=new_attrs,
                    owner_suffix="standard_dictionary_sf_convention",
                    provenance=ProvenanceEvent(
                        stage="entity_lens",
                        action="rewrote_sf_convention_from_dictionary",
                        owner="standard_dictionary",
                        portability="benchmark_format",
                        detail={"lens_id": self.lens_id, "rule_id": rule_id},
                    ),
                )
                rewritten += 1
            if sd.is_sf_convention_noise(
                finding.text,
                evidence=finding.evidence or finding.text,
                attributes=finding.attributes,
            ):
                dropped.append(finding)
                continue
            exact_key = (
                normalize_phrase(finding.text),
                tuple(sorted((str(k), str(v)) for k, v in finding.attributes.items())),
                finding.evidence,
            )
            if exact_key in seen_exact:
                dropped.append(finding)
                continue
            seen_exact.add(exact_key)
            out.append(finding)

        added: list[ClinicalFinding] = []
        existing_keys = {_sf_recovery_key(finding) for finding in out}
        for text, evidence, attrs in sd.sf_residual_additions(store.note_text):
            if sd.is_sf_convention_noise(text, evidence=evidence, attributes=attrs):
                continue
            key = _sf_recovery_key_from_parts(text, attrs)
            if key in existing_keys:
                continue
            finding = _sf_added_finding(
                store,
                text=text,
                evidence=evidence,
                attributes=attrs,
                selected=selected,
                policy=policy,
                lens_id=self.lens_id,
            )
            if finding is None:
                continue
            existing_keys.add(key)
            added.append(finding)

        event = ProvenanceEvent(
            stage="entity_lens",
            action="applied_standard_dictionary_sf_repair",
            owner="standard_dictionary",
            portability=policy.portability,
            detail={
                "lens_id": self.lens_id,
                "producer_id": policy.producer_id,
                "source_lane": policy.source_lane,
                "rewritten_count": rewritten,
                "added_count": len(added),
                "added_text_counts": text_counts(added),
                "dropped_count": len(dropped),
                "dropped_text_counts": text_counts(dropped),
            },
        )
        final_findings = tuple(
            [finding.with_provenance(event) for finding in out]
            + [finding.with_provenance(event) for finding in added]
        )
        return LensResult(
            entity=self.entity,
            lens_id=self.lens_id,
            findings=final_findings,
            diagnostics={
                "lens_id": self.lens_id,
                "rewritten_dictionary_findings": rewritten,
                "added_dictionary_findings": len(added),
                "dropped_dictionary_findings": len(dropped),
                "selected_findings": len(final_findings),
            },
        )


class PrescriptionDictionaryLens(_ThinArtifactLens):
    """v09 Prescription: standard-dictionary drug-name / dose-unit normalization.

    The v0.9 prompt owns regimen selection and future-plan suppression; this
    lens only canonicalizes the surfaces the dictionary owns (generic drug name,
    canonical dose unit).
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
        out: list[ClinicalFinding] = []
        normalized = 0
        split_regimens = 0
        dropped: list[ClinicalFinding] = []
        for finding in selected:
            attrs = dict(finding.attributes)
            changed = False
            repaired_attrs = sd.prescription_convention_attribute_repairs(
                finding.text,
                evidence=finding.evidence,
                attributes=attrs,
            )
            if repaired_attrs != attrs:
                attrs = repaired_attrs
                changed = True
            drug = attrs.get("DrugName")
            if drug:
                generic = sd.normalize_drug_name(drug)
                if generic is not None and generic != drug:
                    attrs["DrugName"] = generic
                    changed = True
            unit = attrs.get("DoseUnit")
            if unit:
                canonical = sd.normalize_dose_unit(unit)
                if canonical != unit:
                    attrs["DoseUnit"] = canonical
                    changed = True
            dose = attrs.get("DrugDose")
            if dose:
                normalized_dose = sd.normalize_dose_value(dose)
                if normalized_dose != dose:
                    attrs["DrugDose"] = normalized_dose
                    changed = True
            if sd.is_prescription_convention_noise(
                finding.text,
                evidence=finding.evidence,
                attributes=attrs,
            ):
                dropped.append(finding)
                continue
            split_rows = sd.split_daily_dose_regimen(
                finding.text,
                evidence=finding.evidence,
                attributes=attrs,
            )
            if split_rows:
                for index, (text, split_attrs, rule) in enumerate(split_rows):
                    out.append(
                        finding_with_text_attributes(
                            finding,
                            text=text,
                            attributes=split_attrs,
                            owner_suffix=f"standard_dictionary_prescription_split_{index}",
                            provenance=ProvenanceEvent(
                                stage="entity_lens",
                                action="split_prescription_regimen_from_dictionary",
                                owner="standard_dictionary",
                                portability="clinical_epilepsy",
                                detail={"lens_id": self.lens_id, "rule": rule},
                            ),
                        )
                    )
                split_regimens += 1
                continue
            if changed:
                finding = finding_with_text_attributes(
                    finding,
                    text=finding.text,
                    attributes=attrs,
                    owner_suffix="standard_dictionary_prescription",
                    provenance=ProvenanceEvent(
                        stage="entity_lens",
                        action="normalized_prescription_from_dictionary",
                        owner="standard_dictionary",
                        portability="clinical_epilepsy",
                        detail={"lens_id": self.lens_id},
                    ),
                )
                normalized += 1
            out.append(finding)

        added: list[ClinicalFinding] = []
        existing_keys = {_prescription_recovery_key(finding) for finding in out}
        for text, evidence, attrs in sd.prescription_residual_additions(store.note_text):
            key = _prescription_recovery_key_from_parts(attrs)
            if key in existing_keys:
                continue
            finding = _prescription_added_finding(
                store,
                text=text,
                evidence=evidence,
                attributes=attrs,
                selected=selected,
                policy=policy,
                lens_id=self.lens_id,
            )
            if finding is None:
                continue
            existing_keys.add(key)
            added.append(finding)

        event = ProvenanceEvent(
            stage="entity_lens",
            action="applied_standard_dictionary_prescription_repair",
            owner="standard_dictionary",
            portability=policy.portability,
            detail={
                "lens_id": self.lens_id,
                "producer_id": policy.producer_id,
                "source_lane": policy.source_lane,
                "normalized_count": normalized,
                "split_regimen_count": split_regimens,
                "added_count": len(added),
                "added_text_counts": text_counts(added),
                "dropped_count": len(dropped),
                "dropped_text_counts": text_counts(dropped),
            },
        )
        final_findings = tuple(
            [finding.with_provenance(event) for finding in out]
            + [finding.with_provenance(event) for finding in added]
        )
        return LensResult(
            entity=self.entity,
            lens_id=self.lens_id,
            findings=final_findings,
            diagnostics={
                "lens_id": self.lens_id,
                "normalized_dictionary_findings": normalized,
                "split_regimen_dictionary_findings": split_regimens,
                "added_dictionary_findings": len(added),
                "dropped_dictionary_findings": len(dropped),
                "selected_findings": len(final_findings),
            },
        )


class SeizureFrequencyLens(_ThinArtifactLens):
    pass


class PrescriptionLens(_ThinArtifactLens):
    pass


class InvestigationsDictionaryLens(_ThinArtifactLens):
    """v09 Investigations: standard-dictionary cleanup for Qwen convention drift.

    The prompt owns whether a test is clinically selected. This lens removes
    unsupported cross-modality ``No`` defaults and drops planned/resultless
    investigation renderings that the headline scorer treats as false positives.
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
        out: list[ClinicalFinding] = []
        normalized = 0
        dropped: list[ClinicalFinding] = []
        seen_exact: set[tuple[str, tuple[tuple[str, str], ...], str]] = set()
        for finding in selected:
            attrs = dict(finding.attributes)
            repaired_attrs = sd.investigation_convention_attribute_repairs(
                finding.text,
                evidence=finding.evidence,
                attributes=attrs,
            )
            if sd.is_investigation_convention_noise(
                finding.text,
                evidence=finding.evidence,
                attributes=repaired_attrs,
            ):
                dropped.append(finding)
                continue
            exact_key = (
                normalize_phrase(finding.text),
                tuple(sorted((str(k), str(v)) for k, v in repaired_attrs.items())),
                finding.evidence,
            )
            if exact_key in seen_exact:
                dropped.append(finding)
                continue
            seen_exact.add(exact_key)
            if repaired_attrs != attrs:
                finding = finding_with_text_attributes(
                    finding,
                    text=finding.text,
                    attributes=repaired_attrs,
                    owner_suffix="standard_dictionary_investigations",
                    provenance=ProvenanceEvent(
                        stage="entity_lens",
                        action="normalized_investigations_from_dictionary",
                        owner="standard_dictionary",
                        portability="clinical_epilepsy",
                        detail={"lens_id": self.lens_id},
                    ),
                )
                normalized += 1
            out.append(finding)

        added: list[ClinicalFinding] = []
        existing_keys = {_investigation_recovery_key(finding) for finding in out}
        for text, evidence, attrs in sd.investigation_residual_additions(store.note_text):
            key = _investigation_recovery_key_from_parts(attrs)
            if key in existing_keys:
                continue
            finding = _investigation_added_finding(
                store,
                text=text,
                evidence=evidence,
                attributes=attrs,
                selected=selected,
                policy=policy,
                lens_id=self.lens_id,
            )
            if finding is None:
                continue
            existing_keys.add(key)
            added.append(finding)

        event = ProvenanceEvent(
            stage="entity_lens",
            action="applied_standard_dictionary_investigations_repair",
            owner="standard_dictionary",
            portability=policy.portability,
            detail={
                "lens_id": self.lens_id,
                "producer_id": policy.producer_id,
                "source_lane": policy.source_lane,
                "normalized_count": normalized,
                "added_count": len(added),
                "added_text_counts": text_counts(added),
                "dropped_count": len(dropped),
                "dropped_text_counts": text_counts(dropped),
            },
        )
        final_findings = tuple(
            [finding.with_provenance(event) for finding in out]
            + [finding.with_provenance(event) for finding in added]
        )
        return LensResult(
            entity=self.entity,
            lens_id=self.lens_id,
            findings=final_findings,
            diagnostics={
                "lens_id": self.lens_id,
                "normalized_dictionary_findings": normalized,
                "added_dictionary_findings": len(added),
                "dropped_dictionary_findings": len(dropped),
                "selected_findings": len(final_findings),
            },
        )


class InvestigationsLens(_ThinArtifactLens):
    pass


def lens_from_manifest(config: LensManifest) -> EntityLens:
    dictionary_lens_by_manifest: dict[tuple[str, str], type[_ThinArtifactLens]] = {
        (DIAGNOSIS.name, "diagnosis_convention_dictionary_v09"): DiagnosisDictionaryLens,
        (SEIZURE_FREQUENCY.name, "sf_convention_dictionary_v09"): SeizureFrequencyDictionaryLens,
        (PRESCRIPTION.name, "prescription_dictionary_v09"): PrescriptionDictionaryLens,
        (
            INVESTIGATIONS.name,
            "investigations_convention_dictionary_v09",
        ): InvestigationsDictionaryLens,
    }
    legacy_diagnosis_dictionary_lens_ids = frozenset({
        "diagnosis_heading_recovery_residual_benchmark_v05",
        "diagnosis_heading_recovery_convention_alias_v04",
        "diagnosis_heading_recovery_convention_cleanup_v03",
    })
    key = (config.entity, config.lens)
    if key in dictionary_lens_by_manifest:
        return dictionary_lens_by_manifest[key](lens_id=config.lens, entity=config.entity)
    if config.entity == DIAGNOSIS.name and config.lens in legacy_diagnosis_dictionary_lens_ids:
        return DiagnosisDictionaryLens(lens_id=config.lens, entity=config.entity)
    if config.entity == DIAGNOSIS.name and config.lens == "diagnosis_heading_recovery_v02":
        return DiagnosisHeadingRecoveryLens(lens_id=config.lens, entity=config.entity)
    lens_type = {
        DIAGNOSIS.name: DiagnosisLens,
        SEIZURE_FREQUENCY.name: SeizureFrequencyLens,
        PRESCRIPTION.name: PrescriptionLens,
        INVESTIGATIONS.name: InvestigationsLens,
    }.get(config.entity, _ThinArtifactLens)
    return lens_type(lens_id=config.lens, entity=config.entity)


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
        evidence_valid=evidence in store.note_text,
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


def _sf_recovery_key(finding: ClinicalFinding) -> tuple[str, ...]:
    return _sf_recovery_key_from_parts(finding.text, finding.attributes)


_PRESCRIPTION_NAME_ALIASES = {
    "brivetiracetam": "brivaracetam",
    "brivitiracetam": "brivaracetam",
    "epilim": "sodium-valproate",
    "epilim-chrono": "sodium-valproate",
    "eplim": "sodium-valproate",
    "episenta": "sodium-valproate",
    "sodiumvalproate": "sodium-valproate",
    "tegretol-retard": "carbamazepine",
}


def _prescription_recovery_key(finding: ClinicalFinding) -> tuple[str, ...]:
    return _prescription_recovery_key_from_parts(finding.attributes)


def _prescription_recovery_key_from_parts(
    attributes: Mapping[str, Any],
) -> tuple[str, ...]:
    attrs = {str(key): str(value) for key, value in attributes.items()}
    drug = _prescription_drug_key(attrs.get("DrugName", ""))
    frequency = attrs.get("Frequency", "").lower()
    if not drug or not frequency:
        return ()
    if frequency == "as_required":
        return "rescue", drug, frequency
    dose = sd.normalize_dose_value(attrs.get("DrugDose", ""))
    unit = sd.normalize_dose_unit(attrs.get("DoseUnit", "")) if attrs.get("DoseUnit") else ""
    if not dose or not unit:
        return ()
    return "ordinary", drug, dose, unit, frequency


def _prescription_drug_key(value: str) -> str:
    generic = sd.normalize_drug_name(value) or value
    key = normalize_phrase(generic).replace(" ", "-")
    return _PRESCRIPTION_NAME_ALIASES.get(key, key)


def _prescription_added_finding(
    store: ClinicalFindingStore,
    *,
    text: str,
    evidence: str,
    attributes: dict[str, str],
    selected: list[ClinicalFinding],
    policy: LensPolicy,
    lens_id: str,
) -> ClinicalFinding | None:
    source = source_for_residual(
        store,
        entity=PRESCRIPTION.name,
        selected=selected,
        policy=policy,
        ownership_suffix="standard_dictionary_prescription_residual",
    )
    if source is None:
        return None
    dose = attributes.get("DrugDose", "")
    frequency = attributes.get("Frequency", "")
    return ClinicalFinding(
        finding_id=(
            f"{store.letter_id}:{policy.producer_id}:Prescription:lens:{lens_id}:"
            f"{normalize_phrase(text).replace(' ', '_')}:{dose}:{frequency}"
        ),
        letter_id=store.letter_id,
        entity=PRESCRIPTION.name,
        text=text,
        attributes={str(key): str(value) for key, value in attributes.items()},
        evidence=evidence,
        normalized_concept=attributes.get("DrugName") or text,
        assertion=None,
        confidence="high",
        source=source,
        provenance=(
            ProvenanceEvent(
                stage="entity_lens",
                action="added_prescription_residual_from_dictionary",
                owner="standard_dictionary",
                portability="clinical_epilepsy",
                detail={
                    "lens_id": lens_id,
                    "producer_id": policy.producer_id,
                    "source_lane": policy.source_lane,
                    "rule_category": "prescription_current_regimen",
                    "target_text": text,
                    "evidence": evidence,
                },
            ),
        ),
        rationale="The source phrase matches a bounded dev residual current-regimen pattern.",
        evidence_valid=evidence in store.note_text,
        raw_surface=False,
    )


def _sf_recovery_key_from_parts(
    text: str,
    attributes: dict[str, str] | dict[str, object],
) -> tuple[str, ...]:
    attrs = {str(key): str(value) for key, value in attributes.items()}
    concept = attrs.get("CUI") or normalize_phrase(text)
    if attrs.get("NumberOfSeizures") == "0":
        state = "seizure-free"
    elif any(
        key in attrs
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
        )
    ) and any(
        key in attrs
        for key in (
            "TimePeriod",
            "YearDate",
            "MonthDate",
            "DayDate",
            "PointInTime",
        )
    ):
        state = "active-rate"
    elif attrs.get("FrequencyChange"):
        state = "unknown"
    else:
        state = "unknown"
    if state == "active-rate":
        fingerprint_keys = (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
            "NumberOfTimePeriods",
            "LowerNumberOfTimePeriods",
            "UpperNumberOfTimePeriods",
            "TimePeriod",
            "YearDate",
            "MonthDate",
            "DayDate",
            "PointInTime",
            "TimeSince_or_TimeOfEvent",
        )
        fingerprint = "|".join(
            f"{key}={attrs[key]}" for key in fingerprint_keys if key in attrs
        )
        if fingerprint:
            return concept, state, fingerprint
    return concept, state


def _sf_added_finding(
    store: ClinicalFindingStore,
    *,
    text: str,
    evidence: str,
    attributes: dict[str, str],
    selected: list[ClinicalFinding],
    policy: LensPolicy,
    lens_id: str,
) -> ClinicalFinding | None:
    source = source_for_residual(
        store,
        entity=SEIZURE_FREQUENCY.name,
        selected=selected,
        policy=policy,
        ownership_suffix="standard_dictionary_sf_residual",
    )
    if source is None:
        return None
    return ClinicalFinding(
        finding_id=(
            f"{store.letter_id}:{policy.producer_id}:SeizureFrequency:lens:{lens_id}:"
            f"{normalize_phrase(text).replace(' ', '_')}"
        ),
        letter_id=store.letter_id,
        entity=SEIZURE_FREQUENCY.name,
        text=text,
        attributes={str(key): str(value) for key, value in attributes.items()},
        evidence=evidence,
        normalized_concept=attributes.get("CUI") or text,
        assertion=None,
        confidence="high",
        source=source,
        provenance=(
            ProvenanceEvent(
                stage="entity_lens",
                action="added_sf_residual_convention_from_dictionary",
                owner="standard_dictionary",
                portability="seizure_frequency",
                detail={
                    "lens_id": lens_id,
                    "producer_id": policy.producer_id,
                    "source_lane": policy.source_lane,
                    "rule_category": "seizure_frequency",
                    "target_text": text,
                    "evidence": evidence,
                },
            ),
        ),
        rationale="The source phrase matches a bounded dev residual seizure-frequency pattern.",
        evidence_valid=evidence in store.note_text,
        raw_surface=False,
    )


def _investigation_recovery_key(finding: ClinicalFinding) -> tuple[str, str | None]:
    return _investigation_recovery_key_from_parts(finding.attributes)


def _investigation_recovery_key_from_parts(
    attributes: Mapping[str, Any],
) -> tuple[str, str | None]:
    attrs = {str(key): str(value) for key, value in attributes.items()}
    for modality in ("EEG", "MRI", "CT"):
        if attrs.get(f"{modality}_Performed") == "Yes":
            return modality, attrs.get(f"{modality}_Results")
    return "", None


def _investigation_added_finding(
    store: ClinicalFindingStore,
    *,
    text: str,
    evidence: str,
    attributes: dict[str, str],
    selected: list[ClinicalFinding],
    policy: LensPolicy,
    lens_id: str,
) -> ClinicalFinding | None:
    source = source_for_residual(
        store,
        entity=INVESTIGATIONS.name,
        selected=selected,
        policy=policy,
        ownership_suffix="standard_dictionary_investigation_residual",
    )
    if source is None:
        return None
    return ClinicalFinding(
        finding_id=(
            f"{store.letter_id}:{policy.producer_id}:Investigations:lens:{lens_id}:"
            f"{normalize_phrase(text).replace(' ', '_')}"
        ),
        letter_id=store.letter_id,
        entity=INVESTIGATIONS.name,
        text=text,
        attributes={str(key): str(value) for key, value in attributes.items()},
        evidence=evidence,
        normalized_concept=text,
        assertion=None,
        confidence="high",
        source=source,
        provenance=(
            ProvenanceEvent(
                stage="entity_lens",
                action="added_investigation_residual_from_dictionary",
                owner="standard_dictionary",
                portability="clinical_epilepsy",
                detail={
                    "lens_id": lens_id,
                    "producer_id": policy.producer_id,
                    "source_lane": policy.source_lane,
                    "rule_category": "clinical_epilepsy",
                    "target_text": text,
                    "evidence": evidence,
                },
            ),
        ),
        rationale=(
            "The source phrase matches a bounded dev residual completed-investigation "
            "pattern."
        ),
        evidence_valid=evidence in store.note_text,
        raw_surface=False,
    )
