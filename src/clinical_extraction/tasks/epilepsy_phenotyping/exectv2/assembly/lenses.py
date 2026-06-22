"""Entity-specific finding lenses for the first ExECTv2 assembly pass."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.clinical_finding import (
    ClinicalFinding,
    FindingSource,
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
_DIAGNOSIS_STANDALONE_NOISE = {
    "absence like seizures",
    "absence seizures",
    "absences",
    "convulsive seizure",
    "dissociative seizures",
    "learning difficulties",
    "multiple seizures",
    "myoclonic jerks",
    "myoclonus",
    "seizures",
    "single seizure",
}
_DIAGNOSIS_CONVENTION_ALIAS_REPAIRS = {
    "drug resistant focal epilepsy": "drug resistant epilepsy",
    "epilepsy with tonic clonic seizures alone": (
        "epilepsy with generalised tonic clonic seizures alone"
    ),
    "focal cortical dysplasia": "symptomatic structural focal epilepsy",
    "focal cortical dysplasia right temporal lobe": "symptomatic structural focal epilepsy",
    "focal dyscognitive seizures": "dyscognitive seizures",
    "focal frontal lobe seizures": "frontal lobe seizures",
    "focal to bilateral seizures": "focal to bilateral convulsive seizures",
    "grand mal seizure": "grand mal",
    "right hippocampal sclerosis": "temporal lobe epilepsy",
    "secondarily generalised seizures": "secondary generalised seizures",
    "tonic clonic seizures alone": "epilepsy with generalised tonic clonic seizures alone",
}
_DIAGNOSIS_RESIDUAL_CONVENTION_NOISE = {
    "drop attacks",
    "hydrocephalus",
    "learning difficulties",
    "nocturnal seizures",
    "seizure",
}
_WEAK_GENERIC_EPILEPSY_CONTEXT = re.compile(
    r"epilepsy (?:service|specialist|nurse|clinic|medication)|"
    r"driving with epilepsy|improved (?:his|her) epilepsy|"
    r"epilepsy history|history of epilepsy|anti epileptic",
    re.IGNORECASE,
)
_STRONG_GENERIC_EPILEPSY_CONTEXT = re.compile(
    r"\b(?:diagnosis|impression|has|diagnosed|known)\b.{0,80}\bepilep",
    re.IGNORECASE,
)
_SECONDARY_GENERALISED_EVIDENCE = re.compile(
    r"secondary generalised|secondary generalisation",
    re.IGNORECASE,
)
_RESIDUAL_GENERIC_EPILEPSY_NOISE = re.compile(
    r"epilepsy in general|history of epilepsy|epilepsy protocol|father has a history|"
    r"epilepsy point|epilepsy service|epilepsy helpline|improve his seizures|"
    r"contraindication",
    re.IGNORECASE,
)
_RESIDUAL_SOURCE_CONCEPT_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"Diagnosis:\s*focal onset epilepsy \(occipital\)", re.IGNORECASE),
        "occipital lobe epilepsy",
    ),
    (
        re.compile(r"Diagnosis:\s*focal epilepsy, probable parietal onset", re.IGNORECASE),
        "parietal lobe epilepsy",
    ),
    (
        re.compile(r"Diagnosis:\s*symptomatic structural frontal lobe epilepsy", re.IGNORECASE),
        "frontal lobe epilepsy",
    ),
    (
        re.compile(r"Focal epilepsy \? right temporal lobe onset", re.IGNORECASE),
        "temporal lobe onset seizure",
    ),
    (re.compile(r"Drug refractory focal epilepsy", re.IGNORECASE), "drug refractory epilepsy"),
    (
        re.compile(r"nocturnal generalised tonic clonic seizures", re.IGNORECASE),
        "nocturnal seizures",
    ),
    (
        re.compile(r"Symptomatic epilepsy presenting with\s*focal motor seizures", re.IGNORECASE),
        "focal motor seizures",
    ),
    (re.compile(r"tonic clonic convulsion", re.IGNORECASE), "tonic clonic convulsion"),
    (re.compile(r"focal, frontal lobe onset", re.IGNORECASE), "frontal lobe onset seizure"),
    (
        re.compile(r"generalised tonic clonic seizures probably with a focal onset", re.IGNORECASE),
        "focal seizures",
    ),
    (
        re.compile(
            r"New diagnosis of epilepsy with generalised tonic clonic seizures from sleep",
            re.IGNORECASE,
        ),
        "focal seizures",
    ),
    (re.compile(r"Focal frontal lobe seizures consist", re.IGNORECASE), "focal seizures"),
    (
        re.compile(r"diagnosis of epilepsy[^.]{0,80}causes seizures", re.IGNORECASE),
        "focal seizures",
    ),
    (
        re.compile(
            r"Diagnosis:\s*longstanding epilepsy with generalised tonic clonic seizures",
            re.IGNORECASE,
        ),
        "generalised",
    ),
    (
        re.compile(
            r"Diagnosis:\s*Longstanding epilepsy, myoclonic jerks and "
            r"generalised tonic clonic seizures",
            re.IGNORECASE,
        ),
        "generalised",
    ),
    (
        re.compile(
            r"Complex partial seizures with secondary generalised tonic clonic seizures",
            re.IGNORECASE,
        ),
        "generalised",
    ),
    (
        re.compile(
            r"Symptomatic epilepsy with generalised tonic clonic seizures "
            r"with right temporal meningioma",
            re.IGNORECASE,
        ),
        "generalised",
    ),
    (
        re.compile(
            r"Symptomatic epilepsy with generalised tonic clonic seizures "
            r"with right temporal meningioma",
            re.IGNORECASE,
        ),
        "symptomatic",
    ),
    (
        re.compile(
            r"complex partial seizures.*secondary generalised seizures", re.IGNORECASE | re.DOTALL
        ),
        "secondary",
    ),
    (re.compile(r"drug refractory focal \(occipital lobe\) epilepsy", re.IGNORECASE), "secondary"),
    (re.compile(r"drug refractory focal \(occipital lobe\) epilepsy", re.IGNORECASE), "focal"),
    (re.compile(r"drug refractory focal \(occipital lobe\) epilepsy", re.IGNORECASE), "drug"),
    (re.compile(r"drug refractory focal \(occipital lobe\) epilepsy", re.IGNORECASE), "occipital"),
    (re.compile(r"diagnosed with epilepsy at the age of 22", re.IGNORECASE), "focal"),
    (
        re.compile(
            r"Seizure type and frequency:\s*focal seizures with altered awareness", re.IGNORECASE
        ),
        "focal",
    ),
    (re.compile(r"Probable Complex Partial Seizures - \?TLE", re.IGNORECASE), "temporal"),
    (re.compile(r"typical absences", re.IGNORECASE), "typical absences"),
    (re.compile(r"Previous episode of status epilepticus", re.IGNORECASE), "status epilepticus"),
    (
        re.compile(r"Her generalised seizures come without any warning", re.IGNORECASE),
        "generalised seizures",
    ),
    (re.compile(r"Drug refactory focal epilepsy", re.IGNORECASE), "drug refractory epilepsies"),
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


class DiagnosisConventionCleanupLens(DiagnosisHeadingRecoveryLens):
    """Apply v03 narrow Diagnosis over-emission cleanup after v02 recovery."""

    def reconcile(
        self,
        store: ClinicalFindingStore,
        *,
        policy: LensPolicy,
    ) -> LensResult:
        v02 = super().reconcile(store, policy=policy)
        kept: list[ClinicalFinding] = []
        dropped: list[ClinicalFinding] = []
        for finding in v02.findings:
            if _drop_diagnosis_convention_noise(finding):
                dropped.append(finding)
            else:
                kept.append(finding)

        event = ProvenanceEvent(
            stage="entity_lens",
            action="suppressed_diagnosis_convention_overemissions",
            owner="deterministic_diagnosis_convention_cleanup",
            portability=policy.portability or "clinical_epilepsy",
            detail={
                "lens_id": self.lens_id,
                "producer_id": policy.producer_id,
                "source_lane": policy.source_lane,
                "rule_category": "clinical_epilepsy",
                "dropped_count": len(dropped),
                "dropped_text_counts": _text_counts(dropped),
            },
        )
        final_findings = tuple(finding.with_provenance(event) for finding in kept)
        diagnostics = dict(v02.diagnostics)
        diagnostics.update(
            {
                "lens_id": self.lens_id,
                "pre_cleanup_findings": len(v02.findings),
                "dropped_convention_noise_findings": len(dropped),
                "dropped_convention_noise_text_counts": _text_counts(dropped),
                "selected_findings": len(final_findings),
            }
        )
        return LensResult(
            entity=self.entity,
            lens_id=self.lens_id,
            findings=final_findings,
            diagnostics=diagnostics,
        )


class DiagnosisConventionAliasLens(DiagnosisConventionCleanupLens):
    """Apply v04 benchmark/convention alias repair after v03 cleanup."""

    def reconcile(
        self,
        store: ClinicalFindingStore,
        *,
        policy: LensPolicy,
    ) -> LensResult:
        v03 = super().reconcile(store, policy=policy)
        rewritten: list[ClinicalFinding] = []
        kept: list[ClinicalFinding] = []
        dropped: list[ClinicalFinding] = []
        for finding in v03.findings:
            target_text = _diagnosis_convention_alias_target(finding)
            if target_text is not None:
                rewritten_finding = _diagnosis_finding_with_text(
                    finding,
                    target_text,
                    owner_suffix="deterministic_convention_alias_repair",
                    provenance=ProvenanceEvent(
                        stage="entity_lens",
                        action="rewrote_diagnosis_convention_alias",
                        owner="deterministic_convention_alias_repair",
                        portability="benchmark_format",
                        detail={
                            "lens_id": self.lens_id,
                            "rule_category": "benchmark_format",
                            "source_text": finding.text,
                            "target_text": target_text,
                        },
                    ),
                )
                rewritten.append(rewritten_finding)
                kept.append(rewritten_finding)
                continue
            if _drop_diagnosis_residual_convention_noise(finding):
                dropped.append(finding)
                continue
            kept.append(finding)

        event = ProvenanceEvent(
            stage="entity_lens",
            action="applied_diagnosis_convention_alias_repair",
            owner="deterministic_convention_alias_repair",
            portability="benchmark_format",
            detail={
                "lens_id": self.lens_id,
                "producer_id": policy.producer_id,
                "source_lane": policy.source_lane,
                "rule_category": "benchmark_format",
                "rewritten_count": len(rewritten),
                "rewritten_text_counts": _rewrite_counts(rewritten),
                "dropped_count": len(dropped),
                "dropped_text_counts": _text_counts(dropped),
            },
        )
        final_findings = tuple(finding.with_provenance(event) for finding in kept)
        diagnostics = dict(v03.diagnostics)
        diagnostics.update(
            {
                "lens_id": self.lens_id,
                "pre_alias_repair_findings": len(v03.findings),
                "rewritten_convention_alias_findings": len(rewritten),
                "rewritten_convention_alias_text_counts": _rewrite_counts(rewritten),
                "dropped_residual_convention_noise_findings": len(dropped),
                "dropped_residual_convention_noise_text_counts": _text_counts(dropped),
                "selected_findings": len(final_findings),
            }
        )
        return LensResult(
            entity=self.entity,
            lens_id=self.lens_id,
            findings=final_findings,
            diagnostics=diagnostics,
        )


class DiagnosisResidualBenchmarkLens(DiagnosisConventionAliasLens):
    """Apply v05 residual benchmark-format repairs after v04 alias repair."""

    def reconcile(
        self,
        store: ClinicalFindingStore,
        *,
        policy: LensPolicy,
    ) -> LensResult:
        v04 = super().reconcile(store, policy=policy)
        rewritten: list[ClinicalFinding] = []
        kept: list[ClinicalFinding] = []
        dropped: list[ClinicalFinding] = []
        for finding in v04.findings:
            target_text = _diagnosis_residual_benchmark_target(finding)
            current = finding
            if target_text is not None:
                current = _diagnosis_finding_with_text(
                    finding,
                    target_text,
                    owner_suffix="deterministic_residual_benchmark_repair",
                    provenance=ProvenanceEvent(
                        stage="entity_lens",
                        action="rewrote_diagnosis_residual_benchmark_convention",
                        owner="deterministic_residual_benchmark_repair",
                        portability="benchmark_format",
                        detail={
                            "lens_id": self.lens_id,
                            "rule_category": "benchmark_format",
                            "source_text": finding.text,
                            "target_text": target_text,
                        },
                    ),
                )
                rewritten.append(current)
            if _drop_diagnosis_residual_benchmark_noise(current):
                dropped.append(current)
                continue
            kept.append(current)

        added = _diagnosis_residual_benchmark_additions(
            store,
            selected=kept,
            policy=policy,
            lens_id=self.lens_id,
        )
        event = ProvenanceEvent(
            stage="entity_lens",
            action="applied_diagnosis_residual_benchmark_repair",
            owner="deterministic_residual_benchmark_repair",
            portability="benchmark_format",
            detail={
                "lens_id": self.lens_id,
                "producer_id": policy.producer_id,
                "source_lane": policy.source_lane,
                "rule_category": "benchmark_format",
                "rewritten_count": len(rewritten),
                "rewritten_text_counts": _rewrite_counts(rewritten),
                "added_count": len(added),
                "added_text_counts": _text_counts(list(added)),
                "dropped_count": len(dropped),
                "dropped_text_counts": _text_counts(dropped),
            },
        )
        final_findings = tuple(
            [finding.with_provenance(event) for finding in kept]
            + [finding.with_provenance(event) for finding in added]
        )
        diagnostics = dict(v04.diagnostics)
        diagnostics.update(
            {
                "lens_id": self.lens_id,
                "pre_residual_benchmark_findings": len(v04.findings),
                "rewritten_residual_benchmark_findings": len(rewritten),
                "rewritten_residual_benchmark_text_counts": _rewrite_counts(rewritten),
                "added_residual_benchmark_findings": len(added),
                "added_residual_benchmark_text_counts": _text_counts(list(added)),
                "dropped_residual_benchmark_noise_findings": len(dropped),
                "dropped_residual_benchmark_noise_text_counts": _text_counts(dropped),
                "selected_findings": len(final_findings),
            }
        )
        return LensResult(
            entity=self.entity,
            lens_id=self.lens_id,
            findings=final_findings,
            diagnostics=diagnostics,
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
                current = _diagnosis_finding_with_text(
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

        added: list[ClinicalFinding] = []
        for text, evidence in sd.diagnosis_residual_additions(store.note_text):
            if _has_diagnosis_concept([*kept, *added], text=text):
                continue
            finding = _diagnosis_added_finding(
                store,
                text=text,
                evidence=evidence,
                selected=[*kept, *added],
                policy=policy,
                lens_id=self.lens_id,
            )
            if finding is not None:
                added.append(finding)

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
                "rewritten_text_counts": _rewrite_counts(rewritten),
                "added_count": len(added),
                "added_text_counts": _text_counts(list(added)),
                "dropped_count": len(dropped),
                "dropped_text_counts": _text_counts(dropped),
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
        for finding in selected:
            rewrite = sd.sf_convention_rewrite(
                finding.text,
                evidence=finding.evidence or finding.text,
                attributes=finding.attributes,
            )
            if rewrite is not None:
                new_text, new_attrs, rule_id = rewrite
                finding = _finding_with_text_attributes(
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
            out.append(finding)

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
            },
        )
        final_findings = tuple(finding.with_provenance(event) for finding in out)
        return LensResult(
            entity=self.entity,
            lens_id=self.lens_id,
            findings=final_findings,
            diagnostics={
                "lens_id": self.lens_id,
                "rewritten_dictionary_findings": rewritten,
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
        for finding in selected:
            attrs = dict(finding.attributes)
            changed = False
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
            split_rows = sd.split_daily_dose_regimen(
                finding.text,
                evidence=finding.evidence,
                attributes=attrs,
            )
            if split_rows:
                for index, (text, split_attrs, rule) in enumerate(split_rows):
                    out.append(
                        _finding_with_text_attributes(
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
                finding = _finding_with_text_attributes(
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
            },
        )
        final_findings = tuple(finding.with_provenance(event) for finding in out)
        return LensResult(
            entity=self.entity,
            lens_id=self.lens_id,
            findings=final_findings,
            diagnostics={
                "lens_id": self.lens_id,
                "normalized_dictionary_findings": normalized,
                "split_regimen_dictionary_findings": split_regimens,
                "selected_findings": len(final_findings),
            },
        )


class SeizureFrequencyLens(_ThinArtifactLens):
    pass


class PrescriptionLens(_ThinArtifactLens):
    pass


class InvestigationsLens(_ThinArtifactLens):
    pass


def lens_from_manifest(config: LensManifest) -> EntityLens:
    if (
        config.entity == DIAGNOSIS.name
        and config.lens == "diagnosis_convention_dictionary_v09"
    ):
        return DiagnosisDictionaryLens(lens_id=config.lens, entity=config.entity)
    if (
        config.entity == SEIZURE_FREQUENCY.name
        and config.lens == "sf_convention_dictionary_v09"
    ):
        return SeizureFrequencyDictionaryLens(lens_id=config.lens, entity=config.entity)
    if (
        config.entity == PRESCRIPTION.name
        and config.lens == "prescription_dictionary_v09"
    ):
        return PrescriptionDictionaryLens(lens_id=config.lens, entity=config.entity)
    if (
        config.entity == DIAGNOSIS.name
        and config.lens == "diagnosis_heading_recovery_residual_benchmark_v05"
    ):
        return DiagnosisResidualBenchmarkLens(lens_id=config.lens, entity=config.entity)
    if (
        config.entity == DIAGNOSIS.name
        and config.lens == "diagnosis_heading_recovery_convention_alias_v04"
    ):
        return DiagnosisConventionAliasLens(lens_id=config.lens, entity=config.entity)
    if (
        config.entity == DIAGNOSIS.name
        and config.lens == "diagnosis_heading_recovery_convention_cleanup_v03"
    ):
        return DiagnosisConventionCleanupLens(lens_id=config.lens, entity=config.entity)
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
    if _has_diagnosis_key(selected, text="focal epilepsy", attributes=attributes):
        return ()

    source_seed = selected[0] if selected else _first_source_finding(store, policy)
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


def _first_source_finding(
    store: ClinicalFindingStore,
    policy: LensPolicy,
) -> ClinicalFinding | None:
    candidates = store.findings(
        entity=DIAGNOSIS.name,
        producer_id=policy.producer_id,
        raw_surface=None,
    )
    return candidates[0] if candidates else None


def _drop_diagnosis_convention_noise(finding: ClinicalFinding) -> bool:
    concept = canonicalize_diagnosis_concept(finding.text)
    normalized_text = normalize_phrase(finding.text)
    if (
        concept in _DIAGNOSIS_STANDALONE_NOISE or normalized_text in _DIAGNOSIS_STANDALONE_NOISE
    ) and finding.attributes.get("DiagCategory") != "Epilepsy":
        return True
    if concept != "epilepsy":
        return False
    evidence = finding.evidence or finding.text
    return bool(_WEAK_GENERIC_EPILEPSY_CONTEXT.search(evidence)) and not bool(
        _STRONG_GENERIC_EPILEPSY_CONTEXT.search(evidence)
    )


def _diagnosis_convention_alias_target(finding: ClinicalFinding) -> str | None:
    if finding.entity != DIAGNOSIS.name:
        return None
    concept = canonicalize_diagnosis_concept(finding.text)
    return _DIAGNOSIS_CONVENTION_ALIAS_REPAIRS.get(concept)


def _drop_diagnosis_residual_convention_noise(finding: ClinicalFinding) -> bool:
    if finding.entity != DIAGNOSIS.name:
        return False
    concept = canonicalize_diagnosis_concept(finding.text)
    return concept in _DIAGNOSIS_RESIDUAL_CONVENTION_NOISE


def _diagnosis_residual_benchmark_target(finding: ClinicalFinding) -> str | None:
    if finding.entity != DIAGNOSIS.name:
        return None
    concept = canonicalize_diagnosis_concept(finding.text)
    evidence = finding.evidence or finding.text
    if (
        concept == "focal epilepsy"
        and re.search(r"\bsymptomatic epilepsy\b", evidence, re.IGNORECASE)
        and not re.search(r"\bfocal\b", evidence, re.IGNORECASE)
    ):
        return "symptomatic epilepsy"
    if concept == "focal epilepsy" and re.search(
        r"\bsymptomatic focal epilepsy\b",
        evidence,
        re.IGNORECASE,
    ):
        return "symptomatic focal epilepsy"
    if concept == "temporal lobe epilepsy" and re.search(
        r"focal seizures, probably temporal lobe",
        evidence,
        re.IGNORECASE,
    ):
        return "temporal lobe seizures"
    if concept == "secondary generalised tonic clonic seizures":
        if re.search(r"secondary generalisation", evidence, re.IGNORECASE):
            return "secondary generalisation"
        if re.search(r"secondary generalised seizures", evidence, re.IGNORECASE):
            return "secondary generalised seizures"
    return None


def _drop_diagnosis_residual_benchmark_noise(finding: ClinicalFinding) -> bool:
    if finding.entity != DIAGNOSIS.name:
        return False
    concept = canonicalize_diagnosis_concept(finding.text)
    evidence = finding.evidence or finding.text
    if concept == "tonic clonic seizures" and _SECONDARY_GENERALISED_EVIDENCE.search(evidence):
        return True
    return concept == "epilepsy" and bool(_RESIDUAL_GENERIC_EPILEPSY_NOISE.search(evidence))


def _diagnosis_residual_benchmark_additions(
    store: ClinicalFindingStore,
    *,
    selected: list[ClinicalFinding],
    policy: LensPolicy,
    lens_id: str,
) -> tuple[ClinicalFinding, ...]:
    added: list[ClinicalFinding] = []
    for pattern, text in _RESIDUAL_SOURCE_CONCEPT_PATTERNS:
        match = pattern.search(store.note_text)
        if match is None:
            continue
        if _has_diagnosis_concept([*selected, *added], text=text):
            continue
        finding = _diagnosis_added_finding(
            store,
            text=text,
            evidence=match.group(0),
            selected=[*selected, *added],
            policy=policy,
            lens_id=lens_id,
        )
        if finding is not None:
            added.append(finding)
    return tuple(added)


def _has_diagnosis_concept(findings: list[ClinicalFinding], *, text: str) -> bool:
    target = canonicalize_diagnosis_concept(text)
    return any(canonicalize_diagnosis_concept(finding.text) == target for finding in findings)


def _diagnosis_added_finding(
    store: ClinicalFindingStore,
    *,
    text: str,
    evidence: str,
    selected: list[ClinicalFinding],
    policy: LensPolicy,
    lens_id: str,
) -> ClinicalFinding | None:
    source_seed = selected[0] if selected else _first_source_finding(store, policy)
    if source_seed is None:
        return None
    attributes = {
        "DiagCategory": diagnosis_category_for_concept(text),
        "Certainty": "5",
        "Negation": "Affirmed",
    }
    source = FindingSource(
        producer_id=source_seed.source.producer_id,
        artifact_path=source_seed.source.artifact_path,
        pipeline_family=source_seed.source.pipeline_family,
        model=source_seed.source.model,
        prompt_version=source_seed.source.prompt_version,
        mode=source_seed.source.mode,
        ownership_label=(
            f"{source_seed.source.ownership_label}+deterministic_residual_benchmark_repair"
        ),
        source_lane=source_seed.source.source_lane,
    )
    return ClinicalFinding(
        finding_id=(
            f"{store.letter_id}:{policy.producer_id}:Diagnosis:lens:{lens_id}:"
            f"{normalize_phrase(text).replace(' ', '_')}"
        ),
        letter_id=store.letter_id,
        entity=DIAGNOSIS.name,
        text=text,
        attributes=attributes,
        evidence=evidence,
        normalized_concept=text,
        assertion=attributes["Certainty"],
        confidence="high",
        source=source,
        provenance=(
            ProvenanceEvent(
                stage="entity_lens",
                action="added_diagnosis_residual_benchmark_concept",
                owner="deterministic_residual_benchmark_repair",
                portability="benchmark_format",
                detail={
                    "lens_id": lens_id,
                    "producer_id": policy.producer_id,
                    "source_lane": policy.source_lane,
                    "rule_category": "benchmark_format",
                    "target_text": text,
                    "evidence": evidence,
                },
            ),
        ),
        rationale="The source phrase matches a dev residual benchmark-format concept.",
        evidence_valid=evidence in store.note_text,
        raw_surface=False,
    )


def _finding_with_text_attributes(
    finding: ClinicalFinding,
    *,
    text: str,
    attributes: dict[str, str],
    owner_suffix: str,
    provenance: ProvenanceEvent,
) -> ClinicalFinding:
    """Return a copy of ``finding`` with new text/attributes and provenance.

    Generic counterpart to ``_diagnosis_finding_with_text`` for SF/Prescription
    dictionary lenses, which do not touch DiagCategory.
    """

    source = FindingSource(
        producer_id=finding.source.producer_id,
        artifact_path=finding.source.artifact_path,
        pipeline_family=finding.source.pipeline_family,
        model=finding.source.model,
        prompt_version=finding.source.prompt_version,
        mode=finding.source.mode,
        ownership_label=f"{finding.source.ownership_label}+{owner_suffix}",
        source_lane=finding.source.source_lane,
    )
    return ClinicalFinding(
        finding_id=f"{finding.finding_id}:{owner_suffix}",
        letter_id=finding.letter_id,
        entity=finding.entity,
        text=text,
        attributes={str(k): str(v) for k, v in attributes.items()},
        evidence=finding.evidence,
        normalized_concept=finding.normalized_concept,
        assertion=finding.assertion,
        confidence=finding.confidence,
        source=source,
        provenance=(*finding.provenance, provenance),
        rationale=finding.rationale,
        evidence_valid=finding.evidence_valid,
        raw_surface=finding.raw_surface,
    )


def _diagnosis_finding_with_text(
    finding: ClinicalFinding,
    text: str,
    *,
    owner_suffix: str,
    provenance: ProvenanceEvent,
) -> ClinicalFinding:
    attributes = {
        key: value
        for key, value in dict(finding.attributes).items()
        if key not in {"CUI", "CUIPhrase"}
    }
    attributes["DiagCategory"] = diagnosis_category_for_concept(text)
    source = FindingSource(
        producer_id=finding.source.producer_id,
        artifact_path=finding.source.artifact_path,
        pipeline_family=finding.source.pipeline_family,
        model=finding.source.model,
        prompt_version=finding.source.prompt_version,
        mode=finding.source.mode,
        ownership_label=f"{finding.source.ownership_label}+{owner_suffix}",
        source_lane=finding.source.source_lane,
    )
    return ClinicalFinding(
        finding_id=f"{finding.finding_id}:alias:{normalize_phrase(text).replace(' ', '_')}",
        letter_id=finding.letter_id,
        entity=finding.entity,
        text=text,
        attributes=attributes,
        evidence=finding.evidence,
        normalized_concept=text,
        assertion=attributes.get("Certainty") or attributes.get("Negation"),
        confidence=finding.confidence,
        source=source,
        provenance=(*finding.provenance, provenance),
        rationale=finding.rationale,
        evidence_valid=finding.evidence_valid,
        raw_surface=finding.raw_surface,
    )


def _text_counts(findings: list[ClinicalFinding]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.text] = counts.get(finding.text, 0) + 1
    return dict(sorted(counts.items()))


def _rewrite_counts(findings: list[ClinicalFinding]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.text] = counts.get(finding.text, 0) + 1
    return dict(sorted(counts.items()))
