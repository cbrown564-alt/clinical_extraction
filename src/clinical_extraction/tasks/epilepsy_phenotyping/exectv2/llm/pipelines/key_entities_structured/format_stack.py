"""Same-fact format render for ExECT mentions.

Schema is parse and flatten only. Format respells attributes and attaches
codebook ids without dropping, adding, or remapping a finding. Clinical
gates and family lenses stay out of this stack.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.drug_lexicon import (
    resolve_drug_surface,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    ENTITY_REGISTRY,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.repair import (
    repair_attributes,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_attribute_encoding,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
    canonical_seizure_type_name,
)

from .constants import (
    COMPONENT_OWNER,
    KEY_ENTITY_NAMES,
    PIPELINE_FAMILY,
    PROMPT_VERSION,
)
from .projection import (
    _repair_evidence_from_mention_text,
    _strip_model_supplied_projection_attrs,
)

DIAGNOSIS_STANDARD_NAME_RULE = "encoding.diagnosis_standard_name"
PRESCRIPTION_LOCAL_SLOTS_RULE = "encoding.prescription_local_slots"
PRESCRIPTION_STANDARD_NAME_RULE = "encoding.prescription_standard_name"
PRESCRIPTION_FORMULATION_NAME_RULE = "encoding.prescription_formulation_name"
INVESTIGATION_LOCAL_RESULT_RULE = "encoding.investigation_local_result"
SEIZURE_FREQUENCY_STANDARD_NAME_RULE = "encoding.sf_standard_name"
SEIZURE_FREQUENCY_LOCAL_EVIDENCE_RULE = "encoding.sf_local_evidence"
DEFAULT_FORMAT_RULES = frozenset(
    {
        DIAGNOSIS_STANDARD_NAME_RULE,
        INVESTIGATION_LOCAL_RESULT_RULE,
        PRESCRIPTION_FORMULATION_NAME_RULE,
        PRESCRIPTION_LOCAL_SLOTS_RULE,
        PRESCRIPTION_STANDARD_NAME_RULE,
        SEIZURE_FREQUENCY_LOCAL_EVIDENCE_RULE,
        SEIZURE_FREQUENCY_STANDARD_NAME_RULE,
    }
)


def as_predicted_mentions(mentions: Sequence[Any]) -> list[PredictedMention]:
    """Rehydrate producer mention views into PredictedMention rows."""

    out: list[PredictedMention] = []
    for mention in mentions:
        if isinstance(mention, PredictedMention):
            out.append(mention)
            continue
        payload = mention.model_dump() if hasattr(mention, "model_dump") else dict(mention)
        attributes = payload.get("attributes") or {}
        if not isinstance(attributes, Mapping):
            attributes = {}
        out.append(
            PredictedMention(
                entity=str(payload.get("entity") or ""),
                text=str(payload.get("text") or ""),
                attributes={str(key): str(value) for key, value in attributes.items()},
                evidence=str(payload.get("evidence") or ""),
                confidence=payload.get("confidence") or "medium",
                rationale=str(payload.get("rationale") or ""),
                component_owner=str(payload.get("component_owner") or ""),
            )
        )
    return out


def schema_mentions(mentions: Sequence[Any]) -> list[PredictedMention]:
    """Keep four-family events as written. Drop only out-of-scope names."""

    return [
        mention
        for mention in as_predicted_mentions(mentions)
        if mention.entity in KEY_ENTITY_NAMES
    ]


def apply_format_stack(
    mentions: Sequence[Any],
    note_text: str,
    *,
    letter_id: str = "format",
    enabled_rules: frozenset[str] = DEFAULT_FORMAT_RULES,
) -> tuple[list[PredictedMention], list[str]]:
    """Apply shared and family format rules. Do not gate or rewrite concepts."""

    warnings: list[str] = []
    prepared: list[PredictedMention] = []
    for mention in schema_mentions(mentions):
        repaired = _repair_evidence_from_mention_text(mention, note_text, warnings)
        attrs, projection_warnings = _strip_model_supplied_projection_attrs(
            dict(repaired.attributes)
        )
        warnings.extend(f"{repaired.entity}: {warning}" for warning in projection_warnings)
        prepared.append(repaired.model_copy(update={"attributes": attrs}))

    family_formatted = [
        _apply_family_format(
            mention,
            enabled_rules=enabled_rules,
        )
        for mention in prepared
    ]
    formatted: list[PredictedMention] = []
    for mention in family_formatted:
        repaired_attrs, attr_warnings = repair_attributes(
            dict(mention.attributes), spec=ENTITY_REGISTRY[mention.entity]
        )
        warnings.extend(f"{mention.entity}: {warning}" for warning in attr_warnings)
        formatted.append(mention.model_copy(update={"attributes": repaired_attrs}))
    projected = project_cuis(
        PredictedLetter(
            letter_id=letter_id,
            mentions=tuple(formatted),
            diagnostics={
                "prompt_version": PROMPT_VERSION,
                "pipeline_family": PIPELINE_FAMILY,
                "format_stack": "same_fact",
            },
        )
    )
    return list(projected.mentions), warnings


def mention_row(mention: PredictedMention) -> dict[str, object]:
    """JSON-shaped mention used by rung replay."""

    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "confidence": mention.confidence,
        "rationale": mention.rationale,
        "component_owner": mention.component_owner or COMPONENT_OWNER,
    }


def assign_flatten_mention_ids(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, object]]:
    """Give flatten rows a stable mention_id when extract did not emit one."""

    assigned: list[dict[str, object]] = []
    for index, row in enumerate(rows, start=1):
        next_row = dict(row)
        current = str(next_row.get("mention_id") or next_row.get("finding_id") or "")
        next_row["mention_id"] = current or f"m{index}"
        assigned.append(next_row)
    return assigned


def _apply_family_format(
    mention: PredictedMention,
    *,
    enabled_rules: frozenset[str],
) -> PredictedMention:
    if (
        mention.entity == DIAGNOSIS.name
        and DIAGNOSIS_STANDARD_NAME_RULE in enabled_rules
    ):
        return _format_diagnosis(mention)
    if mention.entity == PRESCRIPTION.name:
        return _format_prescription(
            mention,
            enabled_rules=enabled_rules,
        )
    if mention.entity == INVESTIGATIONS.name:
        return _format_investigation(mention, enabled_rules=enabled_rules)
    if mention.entity == SEIZURE_FREQUENCY.name:
        return _format_seizure_frequency(mention, enabled_rules=enabled_rules)
    return mention


def _format_diagnosis(mention: PredictedMention) -> PredictedMention:
    target = sd.diagnosis_format_target(
        mention.text,
        evidence=mention.evidence or mention.text,
        diag_category=mention.attributes.get("DiagCategory"),
    )
    if not target or target == mention.text:
        return mention
    return mention.model_copy(update={"text": target})


def _format_prescription(
    mention: PredictedMention,
    *,
    enabled_rules: frozenset[str],
) -> PredictedMention:
    if PRESCRIPTION_LOCAL_SLOTS_RULE in enabled_rules:
        attrs = sd.prescription_format_attribute_repairs(
            mention.text,
            evidence=mention.evidence or mention.text,
            attributes=mention.attributes,
        )
    else:
        attrs = sd.prescription_convention_attribute_repairs(
            mention.text,
            evidence=mention.evidence or mention.text,
            attributes=mention.attributes,
        )
    drug = attrs.get("DrugName")
    if drug and PRESCRIPTION_FORMULATION_NAME_RULE in enabled_rules:
        drug = sd.prescription_base_drug_name(drug) or drug
        attrs["DrugName"] = drug
    if drug:
        resolved = resolve_drug_surface(drug)
        generic = sd.normalize_drug_name(resolved) or resolved
        if generic != drug:
            attrs["DrugName"] = generic
    unit = attrs.get("DoseUnit")
    if unit:
        attrs["DoseUnit"] = sd.normalize_dose_unit(unit)
    dose = attrs.get("DrugDose")
    if dose:
        attrs["DrugDose"] = sd.normalize_dose_value(dose)
    preserve_contextual_text = (
        attrs.get("Frequency") == "As_Required"
        or sd.is_planned_start_prescription(
            mention.text,
            evidence=mention.evidence or mention.text,
            attributes=attrs,
        )
        or bool(re.search(r"\b\d+(?:\.\d+)?\s*(?:mg|g)\s*/?\s*kg\b", mention.text, re.I))
    )
    return mention.model_copy(
        update={
            "text": (
                attrs.get("DrugName") or mention.text
                if PRESCRIPTION_STANDARD_NAME_RULE in enabled_rules
                and not preserve_contextual_text
                else mention.text
            ),
            "attributes": attrs,
        }
    )


def _format_investigation(
    mention: PredictedMention,
    *,
    enabled_rules: frozenset[str],
) -> PredictedMention:
    attrs = sd.investigation_convention_attribute_repairs(
        mention.text,
        evidence=mention.evidence or mention.text,
        attributes=mention.attributes,
    )
    if INVESTIGATION_LOCAL_RESULT_RULE in enabled_rules:
        attrs = sd.investigation_local_result_repairs(
            mention.text,
            evidence=mention.evidence or mention.text,
            attributes=attrs,
        )
    return mention.model_copy(update={"attributes": attrs})


def _format_seizure_frequency(
    mention: PredictedMention,
    *,
    enabled_rules: frozenset[str],
) -> PredictedMention:
    encoded, _actions = sf_attribute_encoding.apply_sf_attribute_encoding(
        [mention_row(mention)]
    )
    if not encoded:
        return mention
    row = encoded[0]
    text = str(row.get("text") or mention.text)
    if SEIZURE_FREQUENCY_LOCAL_EVIDENCE_RULE in enabled_rules:
        attrs = dict(row.get("attributes") or mention.attributes)
        evidence = str(row.get("evidence") or mention.evidence)
        if (
            attrs.get("NumberOfSeizures") == "0"
            and re.search(r"\bseizure[- ]free\b", evidence, re.IGNORECASE)
            and not re.search(r"\blast\s+seizure\b", evidence, re.IGNORECASE)
        ):
            text = "seizure free"
    if SEIZURE_FREQUENCY_STANDARD_NAME_RULE in enabled_rules:
        text = canonical_seizure_type_name(text)
    return mention.model_copy(
        update={
            "text": text,
            "attributes": dict(row.get("attributes") or mention.attributes),
            "evidence": str(row.get("evidence") or mention.evidence),
        }
    )
