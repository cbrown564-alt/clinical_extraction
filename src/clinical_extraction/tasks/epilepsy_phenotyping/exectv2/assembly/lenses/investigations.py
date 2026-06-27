"""Investigations entity lenses for ExECTv2 assembly."""

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
    INVESTIGATIONS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)

from .base import InvestigationsLens, ThinArtifactLens


class InvestigationsDictionaryLens(ThinArtifactLens):
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


__all__ = [
    "InvestigationsDictionaryLens",
    "InvestigationsLens",
]
