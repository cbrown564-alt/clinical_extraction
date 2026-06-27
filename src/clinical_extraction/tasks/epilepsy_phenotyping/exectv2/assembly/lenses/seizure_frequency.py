"""SeizureFrequency entity lenses for ExECTv2 assembly."""

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
    source_for_residual,
    text_counts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)

from .base import SeizureFrequencyLens, ThinArtifactLens


class SeizureFrequencyDictionaryLens(ThinArtifactLens):
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


def _sf_recovery_key(finding: ClinicalFinding) -> tuple[str, ...]:
    return _sf_recovery_key_from_parts(finding.text, finding.attributes)


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


__all__ = [
    "SeizureFrequencyDictionaryLens",
    "SeizureFrequencyLens",
]
