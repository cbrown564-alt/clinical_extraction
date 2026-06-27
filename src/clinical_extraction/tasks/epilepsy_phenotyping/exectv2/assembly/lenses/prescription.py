"""Prescription entity lenses for ExECTv2 assembly."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

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
    finding_with_text_attributes,
    source_for_residual,
    text_counts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    PRESCRIPTION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)

from .base import PrescriptionLens, ThinArtifactLens

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


class PrescriptionDictionaryLens(ThinArtifactLens):
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


__all__ = [
    "PrescriptionDictionaryLens",
    "PrescriptionLens",
]
