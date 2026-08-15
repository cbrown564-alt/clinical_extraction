"""Prescription entity lenses for ExECTv2 assembly."""

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
    finding_with_text_attributes,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)

from .base import PrescriptionLens, ThinArtifactLens

# The `current_guard_only` / `residual_explicit_current_only` variants existed
# only to bound the noise-drop and residual-add rules; both rules are gone, so
# an unknown name now raises rather than silently doing nothing.
_PRESCRIPTION_POLICY_VARIANTS = frozenset({"default", "local_scope_only", "combined"})


class PrescriptionDictionaryLens(ThinArtifactLens):
    """v10 Prescription: standard-dictionary normalization and regimen splitting.

    The v0.9 prompt owns regimen selection and future-plan suppression; this
    lens only canonicalizes the surfaces the dictionary owns (generic drug name,
    canonical dose unit, dose value) and splits an explicitly stated uneven
    once-daily regimen into one fact per dose.

    It deliberately does **not** delete model-selected regimens that read as
    planned/historical, and does **not** add dictionary residual regimens. Both
    rules were measured net-harmful on dev140 across six models: see
    ``docs/research/exectv2/prescription_lens_rule_decomposition_2026-08-10.md``.
    """

    def reconcile(
        self,
        store: ClinicalFindingStore,
        *,
        policy: LensPolicy,
    ) -> LensResult:
        variant = policy.prescription_policy_variant
        if variant not in _PRESCRIPTION_POLICY_VARIANTS:
            raise ValueError(f"unknown Prescription policy variant: {variant}")
        local_frequency_scope = variant in {"local_scope_only", "combined"}
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
        dropped_non_asm = 0
        for finding in selected:
            if sd.is_non_antiepileptic_prescription(
                finding.text,
                evidence=finding.evidence or finding.text,
                attributes=finding.attributes,
            ) or sd.is_planned_start_prescription(
                finding.text,
                evidence=finding.evidence or finding.text,
                attributes=finding.attributes,
            ):
                dropped_non_asm += 1
                continue
            before_attrs = {
                str(key): str(value) for key, value in dict(finding.attributes).items()
            }
            attrs = dict(before_attrs)
            changed = False
            repaired_attrs = sd.prescription_convention_attribute_repairs(
                finding.text,
                evidence=finding.evidence,
                attributes=attrs,
                rescue_scope_candidate=(
                    policy.prescription_rescue_scope_candidate or local_frequency_scope
                ),
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
            split_rows = sd.split_daily_dose_regimen(
                finding.text,
                evidence=finding.evidence,
                attributes=attrs,
            )
            if split_rows:
                for index, (text, split_attrs, rule) in enumerate(split_rows):
                    after_attrs = {
                        str(key): str(value) for key, value in dict(split_attrs).items()
                    }
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
                                detail={
                                    "lens_id": self.lens_id,
                                    "rule": rule,
                                    "source_text": finding.text,
                                    "target_text": text,
                                    "before_attributes": before_attrs,
                                    "after_attributes": after_attrs,
                                    "attribute_changes": _attribute_changes(
                                        before_attrs, after_attrs
                                    ),
                                },
                            ),
                        )
                    )
                split_regimens += 1
                continue
            if changed:
                after_attrs = {str(key): str(value) for key, value in attrs.items()}
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
                        detail={
                            "lens_id": self.lens_id,
                            "source_text": finding.text,
                            "target_text": finding.text,
                            "before_attributes": before_attrs,
                            "after_attributes": after_attrs,
                            "attribute_changes": _attribute_changes(
                                before_attrs, after_attrs
                            ),
                        },
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
                "dropped_non_antiepileptic_count": dropped_non_asm,
                "prescription_policy_variant": variant,
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
                "dropped_non_antiepileptic_findings": dropped_non_asm,
                "selected_findings": len(final_findings),
                "prescription_policy_variant": variant,
            },
        )


def _attribute_changes(
    before: dict[str, str], after: dict[str, str]
) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    for key in sorted(set(before) | set(after)):
        old = before.get(key, "")
        new = after.get(key, "")
        if old != new:
            changes.append({"attribute": key, "before": old, "after": new})
    return changes


__all__ = [
    "PrescriptionDictionaryLens",
    "PrescriptionLens",
]
