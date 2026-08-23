"""Inventory-only replay of recorded diagnosis residual adds.

Does not change the selected Compact / cell-3 lens. Applied when rescoring
the diagnostic-inventory track from a saved extract.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

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


def apply_inventory_residuals(
    note_text: str,
    mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Replay recorded ``diagnosis_residual_additions`` onto hybrid mentions."""

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
            if concept.canonical in {"Epilepsy", "MultipleSeizures", "SingleSeizure"}:
                attributes["DiagCategory"] = concept.canonical
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
