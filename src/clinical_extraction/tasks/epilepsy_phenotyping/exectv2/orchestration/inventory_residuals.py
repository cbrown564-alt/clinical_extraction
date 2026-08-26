"""Optional inventory ablation: invent diagnosis mentions from the letter.

Not the default inventory score. ``comparison.json`` scores extract then
select only. This module writes extras onto a saved extract for
``comparison_residual.json`` (invent-from-letter). Does not change the
selected Compact / cell-3 lens.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, TypedDict

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    attach_benchmark_concept,
    diagnosis_concept,
    diagnosis_fragment_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
    diagnosis_category_for_concept,
)


class InventoryResidualStats(TypedDict):
    diagnosis_residual_adds: int
    sf_heading_splits: list[Any]
    sf_generic_keeps: list[Any]
    sf_adds: int


def apply_inventory_residuals(
    note_text: str,
    mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], InventoryResidualStats]:
    """Invent-from-letter diagnosis adds. Ablation only; not default hybrid/select."""

    out = [dict(mention) for mention in mentions]
    diagnosis_added = _add_diagnosis_residuals(note_text, out)
    out.extend(diagnosis_added)
    return out, {
        "diagnosis_residual_adds": len(diagnosis_added),
        "sf_heading_splits": [],
        "sf_generic_keeps": [],
        "sf_adds": 0,
    }


def _has_diagnosis_concept(mentions: Sequence[Mapping[str, Any]], text: str) -> bool:
    target = canonicalize_diagnosis_concept(text)
    fragments = {"drug", "focal", "generalised", "occipital", "secondary", "symptomatic"}
    for mention in mentions:
        if str(mention.get("entity") or "") != "Diagnosis":
            continue
        concept = canonicalize_diagnosis_concept(str(mention.get("text") or ""))
        if concept == target:
            return True
        if target in fragments and target in concept.split():
            return True
    return False


def _add_diagnosis_residuals(
    note_text: str, mentions: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    added: list[dict[str, Any]] = []
    selected_texts = [
        str(mention.get("text") or "")
        for mention in mentions
        if str(mention.get("entity") or "") == "Diagnosis"
    ]
    for text, evidence in sd.diagnosis_residual_additions(note_text):
        if _has_diagnosis_concept([*mentions, *added], text):
            continue
        if sd.is_redundant_diagnosis_residual_addition(
            text,
            evidence=evidence,
            selected_texts=[*selected_texts, *(row["text"] for row in added)],
        ):
            continue
        if evidence and evidence.lower() not in note_text.lower():
            continue
        attributes = {
            "DiagCategory": diagnosis_category_for_concept(text),
            "Certainty": "5",
            "Negation": "Affirmed",
        }
        concept = diagnosis_concept(text) or diagnosis_fragment_concept(text)
        if concept is not None:
            attributes = attach_benchmark_concept(attributes, concept)
        added.append(
            {
                "entity": "Diagnosis",
                "text": text,
                "attributes": attributes,
                "evidence": evidence,
                "component_owner": "inventory_diagnosis_residual",
            }
        )
        selected_texts.append(text)
    return added
