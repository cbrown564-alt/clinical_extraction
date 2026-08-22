"""Ablatable deterministic Select rules over an emitted ExECT fact ledger.

The rules in this module may revise selection or create a cross-family view of
an already-selected fact. They never scan unused note text for new concepts.
Each rule is independently switchable so development replays can report its
own changed rows and leave-one-out contribution.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence, Set
from copy import deepcopy
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    attach_benchmark_concept,
    diagnosis_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
    diagnosis_category_for_concept,
    is_diagnosis_descendant,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.projection_tables import (
    ABSENCE_FAMILY_CUIS,
    DIRECT_SF_DIAGNOSIS_TEXT_BY_CUI,
    EMBEDDED_DIAGNOSIS_ALIASES_BY_CUI,
    HEADING_ONLY_SF_DIAGNOSIS_TEXT_BY_CUI,
    HEADING_PHENOTYPE_NAMES,
    NAMED_ABSENCE_SURFACES,
    SF_TYPE_PARENT_CUI,
)

DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY = "selection.diagnosis_source_local_specificity"
DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE = "selection.diagnosis_explicit_heading_phenotype"
PRESCRIPTION_LOCAL_REGIMEN_SCOPE = "selection.prescription_local_regimen_scope"
PRESCRIPTION_ACTIVE_TITRATION = "selection.prescription_active_titration"
PRESCRIPTION_EXACT_REGIMEN_DEDUPE = "selection.prescription_exact_regimen_dedupe"
SF_NAMED_TYPE_IDENTITY = "selection.sf_named_type_identity"
SF_RECENT_EVENT_OVER_HISTORICAL_FREE = "selection.sf_recent_event_over_historical_free"
SF_TO_DIAGNOSIS_EXPLICIT_TYPE = "selection.sf_to_diagnosis_explicit_type"

CANDIDATE_SELECT_RULE_IDS: tuple[str, ...] = (
    DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY,
    DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE,
    PRESCRIPTION_LOCAL_REGIMEN_SCOPE,
    PRESCRIPTION_ACTIVE_TITRATION,
    PRESCRIPTION_EXACT_REGIMEN_DEDUPE,
    SF_NAMED_TYPE_IDENTITY,
    SF_RECENT_EVENT_OVER_HISTORICAL_FREE,
    SF_TO_DIAGNOSIS_EXPLICIT_TYPE,
)
ACCEPTED_SELECT_RULE_IDS: tuple[str, ...] = (
    DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY,
    DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE,
    PRESCRIPTION_LOCAL_REGIMEN_SCOPE,
    PRESCRIPTION_ACTIVE_TITRATION,
    PRESCRIPTION_EXACT_REGIMEN_DEDUPE,
    SF_NAMED_TYPE_IDENTITY,
    SF_TO_DIAGNOSIS_EXPLICIT_TYPE,
)
_RULE_PORTABILITY_BY_ID = {
    DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY: "clinical_epilepsy",
    DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE: "benchmark_format",
    PRESCRIPTION_LOCAL_REGIMEN_SCOPE: "clinical_epilepsy",
    PRESCRIPTION_ACTIVE_TITRATION: "clinical_epilepsy",
    PRESCRIPTION_EXACT_REGIMEN_DEDUPE: "benchmark_format",
    SF_NAMED_TYPE_IDENTITY: "seizure_frequency",
    SF_RECENT_EVENT_OVER_HISTORICAL_FREE: "seizure_frequency",
    SF_TO_DIAGNOSIS_EXPLICIT_TYPE: "benchmark_format",
}

EMITTED_ACTIONS_BY_RULE_ID: dict[str, frozenset[str]] = {
    DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY: frozenset({"rewrite"}),
    DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE: frozenset({"add"}),
    PRESCRIPTION_LOCAL_REGIMEN_SCOPE: frozenset({"rewrite"}),
    PRESCRIPTION_ACTIVE_TITRATION: frozenset({"add"}),
    PRESCRIPTION_EXACT_REGIMEN_DEDUPE: frozenset({"drop"}),
    SF_NAMED_TYPE_IDENTITY: frozenset({"rewrite"}),
    SF_RECENT_EVENT_OVER_HISTORICAL_FREE: frozenset({"add", "drop"}),
    SF_TO_DIAGNOSIS_EXPLICIT_TYPE: frozenset({"add"}),
}

_DIAGNOSIS_HEADING_RE = re.compile(
    r"^\s*(?:medical\s+)?diagnosis\s*:",
    re.IGNORECASE,
)
_TITRATION_RE = re.compile(
    r"\b(?:increas(?:e|es|ed|ing)|titra(?:te|tes|ted|ting|tion))\b",
    re.IGNORECASE,
)
_FUTURE_START_RE = re.compile(
    r"\b(?:plan(?:ned)?\s+to\s+|will\s+|to\s+)?(?:prescribe|start|commence|initiate)\b",
    re.IGNORECASE,
)
_DOSE_RE = re.compile(
    r"\b(?P<dose>\d+(?:\.\d+)?)\s*(?P<unit>mg|mgs|g|mcg|micrograms?)\b",
    re.IGNORECASE,
)
_HISTORICAL_INITIATION_RE = re.compile(
    r"\b(?:once|after|when)\s+(?:commenced|started|initiated)\b|"
    r"\bwas\s+(?:commenced|started)\b",
    re.IGNORECASE,
)
_CURRENT_REGIMEN_ASSERTION_RE = re.compile(
    r"\b(?:continue|current(?:ly)?|at\s+present|is\s+taking|takes)\b",
    re.IGNORECASE,
)
_RECENT_EVENT_RE = re.compile(
    r"\b(?:recent|recently|today|yesterday|last\s+(?:night|week|month))\b",
    re.IGNORECASE,
)
_HISTORICAL_FREE_BEFORE_EVENT_RE = re.compile(
    r"\bbefore\s+(?:this|the|that)\s+seizure\b.*\bseizure[- ]free\b",
    re.IGNORECASE,
)

_GENERIC_SF_CUIS = frozenset({"", "C0036572"})
_TYPE_HEADING_RE = re.compile(
    r"^\s*(?:diagnosis|seizure\s+type(?:\s+and\s+frequency)?)\s*:",
    re.IGNORECASE,
)


def apply_select_rules(
    selected_mentions: Sequence[Mapping[str, Any]],
    *,
    source_mentions: Sequence[Mapping[str, Any]],
    note_text: str,
    enabled_rule_ids: Set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Apply only ``enabled_rule_ids`` and return mentions plus action records."""

    unknown_rule_ids = set(enabled_rule_ids) - set(CANDIDATE_SELECT_RULE_IDS)
    if unknown_rule_ids:
        raise ValueError(f"unknown deterministic Select rule id(s): {sorted(unknown_rule_ids)}")
    del note_text  # Exact evidence validation remains the assembly owner's job.
    working = [_copy_mention(row) for row in selected_mentions]
    source = [_copy_mention(row) for row in source_mentions]
    actions: list[dict[str, Any]] = []

    if DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY in enabled_rule_ids:
        working, records = _restore_source_local_diagnoses(working, source)
        actions.extend(records)
    if DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE in enabled_rule_ids:
        working, records = _restore_explicit_heading_phenotypes(working, source)
        actions.extend(records)
    if PRESCRIPTION_LOCAL_REGIMEN_SCOPE in enabled_rule_ids:
        working, records = _restore_local_regimen_frequency(working, source)
        actions.extend(records)
    if PRESCRIPTION_ACTIVE_TITRATION in enabled_rule_ids:
        working, records = _restore_active_titrations(working, source)
        actions.extend(records)
    if PRESCRIPTION_EXACT_REGIMEN_DEDUPE in enabled_rule_ids:
        working, records = _dedupe_exact_prescription_regimens(working)
        actions.extend(records)
    if SF_NAMED_TYPE_IDENTITY in enabled_rule_ids:
        working, records = _restore_named_sf_identity(working, source)
        actions.extend(records)
    if SF_RECENT_EVENT_OVER_HISTORICAL_FREE in enabled_rule_ids:
        working, records = _prefer_recent_event_over_historical_free(working, source)
        actions.extend(records)
    if SF_TO_DIAGNOSIS_EXPLICIT_TYPE in enabled_rule_ids:
        working, records = _project_named_sf_to_diagnosis(working)
        actions.extend(records)

    return working, actions


def _restore_source_local_diagnoses(
    selected: list[dict[str, Any]], source: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    actions: list[dict[str, Any]] = []
    out: list[dict[str, Any]] = []
    source_dx = [row for row in source if _entity(row) == "Diagnosis"]
    for mention in selected:
        if _entity(mention) != "Diagnosis":
            out.append(mention)
            continue
        candidates = [
            row
            for row in source_dx
            if _evidence_key(row) == _evidence_key(mention)
            and normalize_phrase(str(row.get("text") or ""))
            != normalize_phrase(str(mention.get("text") or ""))
        ]
        restored = next(
            (row for row in candidates if _should_restore_diagnosis(row, mention)),
            None,
        )
        if restored is None:
            out.append(mention)
            continue
        replacement = _copy_mention(restored)
        replacement = _with_action_provenance(
            replacement,
            rule_id=DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY,
            action="rewrite",
            before=mention,
        )
        out.append(replacement)
        actions.append(
            _action(
                DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY,
                "rewrite",
                before=mention,
                after=replacement,
            )
        )
    return out, actions


def _should_restore_diagnosis(source: Mapping[str, Any], selected: Mapping[str, Any]) -> bool:
    source_text = str(source.get("text") or "")
    selected_text = str(selected.get("text") or "")
    source_concept = canonicalize_diagnosis_concept(source_text)
    selected_concept = canonicalize_diagnosis_concept(selected_text)
    if source_concept == selected_concept:
        return False
    if is_diagnosis_descendant(source_concept, selected_concept):
        return True
    if source_concept in {
        "temporal lobe epilepsy",
        "frontal lobe epilepsy",
        "parietal lobe epilepsy",
        "occipital lobe epilepsy",
    } and selected_concept in {
        "localisation related epilepsy",
        "localization related epilepsy",
        "symptomatic focal epilepsy",
        "symptomatic structural focal epilepsy",
    }:
        return True
    if not is_diagnosis_descendant(selected_concept, source_concept):
        return False
    authorized = sd.diagnosis_select_specificity_target(
        source_text, str(source.get("evidence") or "")
    )
    return canonicalize_diagnosis_concept(authorized or "") != selected_concept


def _restore_explicit_heading_phenotypes(
    selected: list[dict[str, Any]], source: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    diagnosis_rows = [
        mention for mention in (*selected, *source) if _entity(mention) == "Diagnosis"
    ]
    owned = sd.owned_heading_phenotypes(
        {
            canonicalize_diagnosis_concept(str(mention.get("text") or ""))
            for mention in diagnosis_rows
        }
    )
    out = list(selected)
    actions: list[dict[str, Any]] = []
    for mention in source:
        if _entity(mention) != "Diagnosis":
            continue
        phenotype = canonicalize_diagnosis_concept(str(mention.get("text") or ""))
        if (
            phenotype not in HEADING_PHENOTYPE_NAMES
            and normalize_phrase(str(mention.get("text") or "")) not in HEADING_PHENOTYPE_NAMES
        ):
            continue
        if phenotype in owned:
            continue
        if _DIAGNOSIS_HEADING_RE.search(str(mention.get("evidence") or "")) is None:
            continue
        if _has_equivalent_diagnosis(out, mention):
            continue
        addition = _with_action_provenance(
            _diagnosis_normalized_copy(mention),
            rule_id=DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE,
            action="add",
        )
        out.append(addition)
        actions.append(
            _action(
                DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE,
                "add",
                after=addition,
            )
        )
    return out, actions


def _restore_local_regimen_frequency(
    selected: list[dict[str, Any]], source: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    out: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    source_rx = [row for row in source if _entity(row) == "Prescription"]
    for mention in selected:
        if _entity(mention) != "Prescription":
            out.append(mention)
            continue
        attrs = _attrs(mention)
        if attrs.get("Frequency") != "As_Required":
            out.append(mention)
            continue
        match = next(
            (
                row
                for row in source_rx
                if _prescription_source_key(row) == _prescription_source_key(mention)
                and _attrs(row).get("Frequency") not in {None, "", "As_Required"}
            ),
            None,
        )
        if match is None:
            out.append(mention)
            continue
        repaired = _copy_mention(mention)
        repaired_attrs = _attrs(repaired)
        repaired_attrs["Frequency"] = str(_attrs(match)["Frequency"])
        repaired["attributes"] = repaired_attrs
        repaired = _with_action_provenance(
            repaired,
            rule_id=PRESCRIPTION_LOCAL_REGIMEN_SCOPE,
            action="rewrite",
            before=mention,
        )
        out.append(repaired)
        actions.append(
            _action(
                PRESCRIPTION_LOCAL_REGIMEN_SCOPE,
                "rewrite",
                before=mention,
                after=repaired,
            )
        )
    return out, actions


def _restore_active_titrations(
    selected: list[dict[str, Any]], source: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    out = list(selected)
    actions: list[dict[str, Any]] = []
    existing = {_prescription_source_key(row) for row in out if _entity(row) == "Prescription"}
    for mention in source:
        if _entity(mention) != "Prescription":
            continue
        evidence = str(mention.get("evidence") or "")
        if _TITRATION_RE.search(evidence) is None or _FUTURE_START_RE.search(evidence):
            continue
        attrs = _attrs(mention)
        if not all(attrs.get(key) for key in ("DrugName", "DrugDose", "DoseUnit", "Frequency")):
            continue
        if not _is_initial_titration_regimen(mention):
            continue
        key = _prescription_source_key(mention)
        if key in existing:
            continue
        addition = _with_action_provenance(
            _copy_mention(mention),
            rule_id=PRESCRIPTION_ACTIVE_TITRATION,
            action="add",
        )
        out.append(addition)
        existing.add(key)
        actions.append(_action(PRESCRIPTION_ACTIVE_TITRATION, "add", after=addition))
    return out, actions


def _is_initial_titration_regimen(mention: Mapping[str, Any]) -> bool:
    evidence = str(mention.get("evidence") or "")
    dose_match = _DOSE_RE.search(evidence)
    titration = _TITRATION_RE.search(evidence)
    if dose_match is None or titration is None or dose_match.start() >= titration.start():
        return False
    attrs = _attrs(mention)
    if sd.normalize_dose_value(str(attrs.get("DrugDose") or "")) != sd.normalize_dose_value(
        dose_match.group("dose")
    ):
        return False
    if sd.normalize_dose_unit(str(attrs.get("DoseUnit") or "")) != sd.normalize_dose_unit(
        dose_match.group("unit")
    ):
        return False
    initial_frequency = sd.frequency_code(evidence[: titration.start()])
    return initial_frequency is None or str(attrs.get("Frequency") or "") == initial_frequency


def _dedupe_exact_prescription_regimens(
    selected: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    grouped: dict[tuple[str, ...], list[int]] = {}
    for index, mention in enumerate(selected):
        if _entity(mention) == "Prescription" and _has_complete_regimen(mention):
            grouped.setdefault(_prescription_regimen_key(mention), []).append(index)

    drop_indices: set[int] = set()
    for indices in grouped.values():
        if len(indices) < 2:
            continue
        historical = [
            index
            for index in indices
            if _HISTORICAL_INITIATION_RE.search(str(selected[index].get("evidence") or ""))
        ]
        current = [
            index
            for index in indices
            if _CURRENT_REGIMEN_ASSERTION_RE.search(str(selected[index].get("evidence") or ""))
        ]
        if historical and current:
            drop_indices.update(historical)

    out: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    for index, mention in enumerate(selected):
        if index not in drop_indices:
            out.append(mention)
            continue
        actions.append(_action(PRESCRIPTION_EXACT_REGIMEN_DEDUPE, "drop", before=mention))
    return out, actions


def _restore_named_sf_identity(
    selected: list[dict[str, Any]], source: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    out = list(selected)
    actions: list[dict[str, Any]] = []
    source_groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    selected_groups: dict[tuple[Any, ...], list[int]] = {}
    for mention in source:
        if _entity(mention) != "SeizureFrequency" or _sf_cui(mention) in _GENERIC_SF_CUIS:
            continue
        source_groups.setdefault(_sf_identity_group_key(mention), []).append(mention)
    for index, mention in enumerate(selected):
        if _entity(mention) == "SeizureFrequency":
            selected_groups.setdefault(_sf_identity_group_key(mention), []).append(index)

    for group_key, indices in selected_groups.items():
        remaining_source = list(source_groups.get(group_key, []))
        if not remaining_source:
            continue
        unmatched_indices: list[int] = []
        for index in indices:
            mention = out[index]
            matched_index = next(
                (
                    candidate_index
                    for candidate_index, candidate in enumerate(remaining_source)
                    if _sf_cui(candidate) == _sf_cui(mention)
                    or _is_allowed_named_refinement(candidate, mention)
                ),
                None,
            )
            if matched_index is None:
                unmatched_indices.append(index)
            else:
                remaining_source.pop(matched_index)

        for index, match in zip(unmatched_indices, remaining_source, strict=False):
            mention = out[index]
            repaired = _copy_mention(mention)
            repaired["text"] = str(match.get("text") or "")
            if match.get("standard_name"):
                repaired["standard_name"] = str(match["standard_name"])
            elif "standard_name" in repaired:
                repaired["standard_name"] = repaired["text"]
            repaired_attrs = _attrs(repaired)
            source_attrs = _attrs(match)
            for key in ("CUI", "CUIPhrase"):
                if source_attrs.get(key):
                    repaired_attrs[key] = str(source_attrs[key])
                else:
                    repaired_attrs.pop(key, None)
            repaired["attributes"] = repaired_attrs
            repaired = _with_action_provenance(
                repaired,
                rule_id=SF_NAMED_TYPE_IDENTITY,
                action="rewrite",
                before=mention,
            )
            out[index] = repaired
            actions.append(
                _action(
                    SF_NAMED_TYPE_IDENTITY,
                    "rewrite",
                    before=mention,
                    after=repaired,
                )
            )
    return out, actions


def _is_sf_type_descendant(child_cui: str, parent_cui: str) -> bool:
    current = child_cui
    seen: set[str] = set()
    while current in SF_TYPE_PARENT_CUI and current not in seen:
        seen.add(current)
        current = SF_TYPE_PARENT_CUI[current]
        if current == parent_cui:
            return True
    return False


def _is_allowed_named_refinement(source: Mapping[str, Any], selected: Mapping[str, Any]) -> bool:
    return _is_sf_type_descendant(_sf_cui(selected), _sf_cui(source))


def _prefer_recent_event_over_historical_free(
    selected: list[dict[str, Any]], source: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    recent = [
        row
        for row in source
        if _entity(row) == "SeizureFrequency"
        and _is_nonzero_sf(row)
        and _RECENT_EVENT_RE.search(str(row.get("evidence") or ""))
    ]
    historical_keys = {
        _evidence_key(row)
        for row in source
        if _entity(row) == "SeizureFrequency"
        and _is_zero_sf(row)
        and _HISTORICAL_FREE_BEFORE_EVENT_RE.search(str(row.get("evidence") or ""))
    }
    if not recent or not historical_keys:
        return selected, []

    out: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    for mention in selected:
        if (
            _entity(mention) == "SeizureFrequency"
            and _evidence_key(mention) in historical_keys
            and _is_zero_sf(mention)
        ):
            actions.append(
                _action(
                    SF_RECENT_EVENT_OVER_HISTORICAL_FREE,
                    "drop",
                    before=mention,
                )
            )
            continue
        out.append(mention)

    existing = {_sf_full_key(row) for row in out if _entity(row) == "SeizureFrequency"}
    for mention in recent:
        if _sf_full_key(mention) in existing:
            continue
        addition = _with_action_provenance(
            _copy_mention(mention),
            rule_id=SF_RECENT_EVENT_OVER_HISTORICAL_FREE,
            action="add",
        )
        out.append(addition)
        existing.add(_sf_full_key(addition))
        actions.append(
            _action(
                SF_RECENT_EVENT_OVER_HISTORICAL_FREE,
                "add",
                after=addition,
            )
        )
    return out, actions


def _project_named_sf_to_diagnosis(
    selected: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    out = list(selected)
    actions: list[dict[str, Any]] = []
    existing_dx_cuis = {
        str(_attrs(row).get("CUI") or "") for row in out if _entity(row) == "Diagnosis"
    }
    for mention in list(selected):
        if _entity(mention) != "SeizureFrequency":
            continue
        text = _sf_diagnosis_projection_text(mention)
        if text is None:
            continue
        concept = diagnosis_concept(text)
        if (
            concept is None
            or concept.cui in existing_dx_cuis
            or _has_embedded_diagnosis_alias(out, concept.cui)
        ):
            continue
        addition = _diagnosis_from_sf(mention, text)
        addition = _with_action_provenance(
            addition,
            rule_id=SF_TO_DIAGNOSIS_EXPLICIT_TYPE,
            action="add",
        )
        out.append(addition)
        existing_dx_cuis.add(concept.cui)
        actions.append(_action(SF_TO_DIAGNOSIS_EXPLICIT_TYPE, "add", after=addition))
    return out, actions


def _sf_diagnosis_projection_text(mention: Mapping[str, Any]) -> str | None:
    """Return the Diagnosis view of a selected named SF fact, or None.

    Always-project CUIs are the same clinical fact in both families. Heading-only
    CUIs are a gold-view alias kept only under an explicit type heading. Generic
    ``absences`` stay in SeizureFrequency; a named absence refinement may
    project as ``absence seizures``.
    """

    cui = _sf_cui(mention)
    surface = normalize_phrase(str(mention.get("text") or ""))
    if cui in DIRECT_SF_DIAGNOSIS_TEXT_BY_CUI:
        return DIRECT_SF_DIAGNOSIS_TEXT_BY_CUI[cui]
    if cui in ABSENCE_FAMILY_CUIS and surface in NAMED_ABSENCE_SURFACES:
        return "absence seizures"
    heading_text = HEADING_ONLY_SF_DIAGNOSIS_TEXT_BY_CUI.get(cui)
    if heading_text is None:
        return None
    if _TYPE_HEADING_RE.search(str(mention.get("evidence") or "")) is None:
        return None
    return heading_text


def _has_embedded_diagnosis_alias(mentions: Sequence[Mapping[str, Any]], target_cui: str) -> bool:
    aliases = EMBEDDED_DIAGNOSIS_ALIASES_BY_CUI.get(target_cui, ())
    if not aliases:
        return False
    for mention in mentions:
        if _entity(mention) != "Diagnosis":
            continue
        text = normalize_phrase(str(mention.get("text") or ""))
        if any(alias in text for alias in aliases):
            return True
    return False


def _diagnosis_from_sf(mention: Mapping[str, Any], text: str) -> dict[str, Any]:
    concept = diagnosis_concept(text)
    if concept is None:
        raise ValueError(f"missing Diagnosis benchmark concept for {text!r}")
    attributes = attach_benchmark_concept(
        {
            "DiagCategory": diagnosis_category_for_concept(text),
            "Certainty": "5",
            "Negation": "Affirmed",
        },
        concept,
    )
    addition = _copy_mention(mention)
    addition["entity"] = "Diagnosis"
    addition["text"] = text
    addition["standard_name"] = text
    addition["attributes"] = attributes
    addition["normalized_concept"] = text
    addition["assertion"] = "5"
    addition["fact_origin"] = "post_model_cross_family_projection"
    return addition


def _diagnosis_normalized_copy(mention: Mapping[str, Any]) -> dict[str, Any]:
    copied = _copy_mention(mention)
    text = str(copied.get("text") or "")
    concept = diagnosis_concept(text)
    if concept is not None:
        attrs = attach_benchmark_concept(_attrs(copied), concept)
        attrs.setdefault("DiagCategory", diagnosis_category_for_concept(text))
        copied["attributes"] = attrs
    return copied


def _has_equivalent_diagnosis(
    mentions: Sequence[Mapping[str, Any]], candidate: Mapping[str, Any]
) -> bool:
    normalized = _diagnosis_normalized_copy(candidate)
    target_cui = str(_attrs(normalized).get("CUI") or "")
    target_text = canonicalize_diagnosis_concept(str(normalized.get("text") or ""))
    for mention in mentions:
        if _entity(mention) != "Diagnosis":
            continue
        cui = str(_attrs(mention).get("CUI") or "")
        if target_cui and cui == target_cui:
            return True
        if canonicalize_diagnosis_concept(str(mention.get("text") or "")) == target_text:
            return True
    return False


def _prescription_source_key(mention: Mapping[str, Any]) -> tuple[str, ...]:
    attrs = _attrs(mention)
    drug = sd.normalize_drug_name(str(attrs.get("DrugName") or "")) or normalize_phrase(
        str(attrs.get("DrugName") or mention.get("text") or "")
    )
    return (
        _evidence_key(mention),
        normalize_phrase(drug),
        sd.normalize_dose_value(str(attrs.get("DrugDose") or "")),
        sd.normalize_dose_unit(str(attrs.get("DoseUnit") or "")),
    )


def _prescription_regimen_key(mention: Mapping[str, Any]) -> tuple[str, ...]:
    attrs = _attrs(mention)
    drug = sd.normalize_drug_name(str(attrs.get("DrugName") or "")) or normalize_phrase(
        str(attrs.get("DrugName") or mention.get("text") or "")
    )
    return (
        normalize_phrase(drug),
        sd.normalize_dose_value(str(attrs.get("DrugDose") or "")),
        sd.normalize_dose_unit(str(attrs.get("DoseUnit") or "")),
        normalize_phrase(str(attrs.get("Frequency") or "")),
        normalize_phrase(str(attrs.get("Route") or "")),
    )


def _has_complete_regimen(mention: Mapping[str, Any]) -> bool:
    attrs = _attrs(mention)
    return all(attrs.get(key) for key in ("DrugName", "DrugDose", "DoseUnit", "Frequency"))


def _sf_state_attribute_key(mention: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    return tuple(
        sorted(
            (str(key), str(value))
            for key, value in _attrs(mention).items()
            if key not in {"CUI", "CUIPhrase", "Certainty", "Negation"}
        )
    )


def _sf_identity_group_key(mention: Mapping[str, Any]) -> tuple[Any, ...]:
    return (_evidence_key(mention), _sf_state_attribute_key(mention))


def _sf_full_key(mention: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        _evidence_key(mention),
        normalize_phrase(str(mention.get("text") or "")),
        _sf_state_attribute_key(mention),
    )


def _is_zero_sf(mention: Mapping[str, Any]) -> bool:
    return str(_attrs(mention).get("NumberOfSeizures") or "") == "0"


def _is_nonzero_sf(mention: Mapping[str, Any]) -> bool:
    attrs = _attrs(mention)
    return any(
        str(attrs.get(key) or "") not in {"", "0"}
        for key in ("NumberOfSeizures", "LowerNumberOfSeizures", "UpperNumberOfSeizures")
    )


def _entity(mention: Mapping[str, Any]) -> str:
    return str(mention.get("entity") or "")


def _attrs(mention: Mapping[str, Any]) -> dict[str, str]:
    return {
        str(key): str(value)
        for key, value in dict(mention.get("attributes") or {}).items()
        if value is not None
    }


def _sf_cui(mention: Mapping[str, Any]) -> str:
    return str(_attrs(mention).get("CUI") or "")


def _evidence_key(mention: Mapping[str, Any]) -> str:
    return normalize_phrase(str(mention.get("evidence") or ""))


def _copy_mention(mention: Mapping[str, Any]) -> dict[str, Any]:
    return deepcopy(dict(mention))


def _validate_emitted_action(rule_id: str, action: str) -> None:
    allowed = EMITTED_ACTIONS_BY_RULE_ID.get(rule_id)
    if allowed is None or action not in allowed:
        declared = sorted(allowed or ())
        raise ValueError(
            f"Select rule {rule_id!r} emitted action {action!r}; "
            f"declared kinds are {declared}"
        )


def _with_action_provenance(
    mention: dict[str, Any],
    *,
    rule_id: str,
    action: str,
    before: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    _validate_emitted_action(rule_id, action)
    out = _copy_mention(mention)
    provenance = list(out.get("provenance") or [])
    provenance.append(
        {
            "stage": "select_rule_stack",
            "action": action,
            "owner": rule_id,
            "portability": _RULE_PORTABILITY_BY_ID[rule_id],
            "detail": {
                "rule_id": rule_id,
                "source_text": str((before or {}).get("text") or ""),
                "target_text": str(out.get("text") or ""),
            },
        }
    )
    out["provenance"] = provenance
    out["component_owner"] = f"{out.get('component_owner') or 'fact_ledger'}+{rule_id}"
    return out


def _action(
    rule_id: str,
    action: str,
    *,
    before: Mapping[str, Any] | None = None,
    after: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    _validate_emitted_action(rule_id, action)
    carrier = after or before or {}
    return {
        "rule_id": rule_id,
        "action": action,
        "portability": _RULE_PORTABILITY_BY_ID[rule_id],
        "entity": _entity(carrier),
        "evidence": str(carrier.get("evidence") or ""),
        "before_text": str((before or {}).get("text") or ""),
        "after_text": str((after or {}).get("text") or ""),
        "before_attributes": _attrs(before or {}),
        "after_attributes": _attrs(after or {}),
    }


__all__ = [
    "ACCEPTED_SELECT_RULE_IDS",
    "CANDIDATE_SELECT_RULE_IDS",
    "DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE",
    "DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY",
    "EMITTED_ACTIONS_BY_RULE_ID",
    "PRESCRIPTION_ACTIVE_TITRATION",
    "PRESCRIPTION_EXACT_REGIMEN_DEDUPE",
    "PRESCRIPTION_LOCAL_REGIMEN_SCOPE",
    "SF_NAMED_TYPE_IDENTITY",
    "SF_RECENT_EVENT_OVER_HISTORICAL_FREE",
    "SF_TO_DIAGNOSIS_EXPLICIT_TYPE",
    "apply_select_rules",
]
