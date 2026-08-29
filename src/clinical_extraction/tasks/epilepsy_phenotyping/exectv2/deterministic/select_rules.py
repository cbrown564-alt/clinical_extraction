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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.find_ledger import (
    DIAGNOSIS_COMPONENT_TOKEN,
    DIAGNOSIS_EXPANSION_SURFACE,
    DIAGNOSIS_HEADING_DECOMPOSITION,
    DIAGNOSIS_HIERARCHY_ANCESTOR,
    DIAGNOSIS_NESTED_ANCESTOR,
    DIAGNOSIS_NESTED_SURFACE,
    DIAGNOSIS_NONDIAGNOSTIC_CONTEXT,
    DIAGNOSIS_UNRESTRICTED_SURFACE,
    INV_RESULT_VARIANT,
    RX_RECALL_EXPANSION,
    SF_HEADING_STATE,
    SF_NAMED_TYPE,
    SF_SEIZURE_FREE,
    SF_STATE_VARIANT,
    recall_first_class_of,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    annotation_from_mapping,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    _frequency_state,
    _frequency_state_keys,
)

DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY = "selection.diagnosis_source_local_specificity"
DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE = "selection.diagnosis_explicit_heading_phenotype"
PRESCRIPTION_LOCAL_REGIMEN_SCOPE = "selection.prescription_local_regimen_scope"
PRESCRIPTION_ACTIVE_TITRATION = "selection.prescription_active_titration"
PRESCRIPTION_EXACT_REGIMEN_DEDUPE = "selection.prescription_exact_regimen_dedupe"
SF_NAMED_TYPE_IDENTITY = "selection.sf_named_type_identity"
SF_RECENT_EVENT_OVER_HISTORICAL_FREE = "selection.sf_recent_event_over_historical_free"
SF_TO_DIAGNOSIS_EXPLICIT_TYPE = "selection.sf_to_diagnosis_explicit_type"
SF_SUPPORTED_STATE_PROMOTION = "selection.sf_supported_state_promotion"
INVENTORY_KEEP_SOURCE_DIAGNOSIS = "selection.inventory_keep_source_diagnosis"
INVENTORY_WEAK_EPISODE_DROP = "selection.inventory_weak_episode_drop"
INVESTIGATION_SAME_RESULT_DEDUPE = "selection.investigation_same_result_dedupe"
SF_RATELESS_ANCHOR_DROP = "selection.sf_rateless_anchor_drop"
SF_GENERIC_DUPLICATE_DROP = "selection.sf_generic_duplicate_of_named_type_drop"
SF_SEIZURE_FREE_POSITIVE_COUNT_DROP = "selection.sf_seizure_free_positive_count_drop"
RECALL_FIRST_UNSUPPORTED_DROP = "selection.recall_first_unsupported_drop"
INVESTIGATION_RESULTLESS_DROP = "selection.investigation_resultless_drop"

# Phase C keep rules (2026-08-27 restructure): each retains one recall-first
# find class at Select. They carry no handler of their own; the
# RECALL_FIRST_UNSUPPORTED_DROP gate consults them (with the per-class
# condition in RECALL_FIRST_KEEP_CONDITIONS, when one is registered).
KEEP_DX_NONDIAGNOSTIC_CONTEXT = "selection.keep_dx_nondiagnostic_context"
KEEP_DX_NESTED_ANCESTOR = "selection.keep_dx_nested_ancestor"
KEEP_DX_NESTED_SURFACE = "selection.keep_dx_nested_surface"
KEEP_DX_HEADING_DECOMPOSITION = "selection.keep_dx_heading_decomposition"
KEEP_DX_UNRESTRICTED_SURFACE = "selection.keep_dx_unrestricted_surface"
KEEP_DX_EXPANSION_SURFACE = "selection.keep_dx_expansion_surface"
KEEP_DX_HIERARCHY_ANCESTOR = "selection.keep_dx_hierarchy_ancestor"
KEEP_DX_COMPONENT_TOKEN = "selection.keep_dx_component_token"
KEEP_SF_NAMED_TYPE = "selection.keep_sf_named_type"
KEEP_SF_HEADING_STATE = "selection.keep_sf_heading_state"
KEEP_SF_SEIZURE_FREE = "selection.keep_sf_seizure_free"
KEEP_SF_STATE_VARIANT = "selection.keep_sf_state_variant"
KEEP_RX_RECALL_EXPANSION = "selection.keep_rx_recall_expansion"
KEEP_INV_RESULT_VARIANT = "selection.keep_inv_result_variant"

_KEEP_RULE_IDS: tuple[str, ...] = (
    KEEP_DX_NONDIAGNOSTIC_CONTEXT,
    KEEP_DX_NESTED_ANCESTOR,
    KEEP_DX_NESTED_SURFACE,
    KEEP_DX_HEADING_DECOMPOSITION,
    KEEP_DX_UNRESTRICTED_SURFACE,
    KEEP_DX_EXPANSION_SURFACE,
    KEEP_DX_HIERARCHY_ANCESTOR,
    KEEP_DX_COMPONENT_TOKEN,
    KEEP_SF_NAMED_TYPE,
    KEEP_SF_HEADING_STATE,
    KEEP_SF_SEIZURE_FREE,
    KEEP_SF_STATE_VARIANT,
    KEEP_RX_RECALL_EXPANSION,
    KEEP_INV_RESULT_VARIANT,
)

CANDIDATE_SELECT_RULE_IDS: tuple[str, ...] = (
    RECALL_FIRST_UNSUPPORTED_DROP,
    *_KEEP_RULE_IDS,
    DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY,
    DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE,
    PRESCRIPTION_LOCAL_REGIMEN_SCOPE,
    PRESCRIPTION_ACTIVE_TITRATION,
    PRESCRIPTION_EXACT_REGIMEN_DEDUPE,
    SF_NAMED_TYPE_IDENTITY,
    SF_RECENT_EVENT_OVER_HISTORICAL_FREE,
    SF_TO_DIAGNOSIS_EXPLICIT_TYPE,
    SF_SUPPORTED_STATE_PROMOTION,
    INVENTORY_KEEP_SOURCE_DIAGNOSIS,
    INVENTORY_WEAK_EPISODE_DROP,
    INVESTIGATION_SAME_RESULT_DEDUPE,
    SF_RATELESS_ANCHOR_DROP,
    SF_GENERIC_DUPLICATE_DROP,
    SF_SEIZURE_FREE_POSITIVE_COUNT_DROP,
    INVESTIGATION_RESULTLESS_DROP,
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
INVENTORY_SELECT_RULE_IDS: tuple[str, ...] = (
    DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY,
    DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE,
    PRESCRIPTION_LOCAL_REGIMEN_SCOPE,
    PRESCRIPTION_ACTIVE_TITRATION,
    PRESCRIPTION_EXACT_REGIMEN_DEDUPE,
    INVENTORY_KEEP_SOURCE_DIAGNOSIS,
    INVENTORY_WEAK_EPISODE_DROP,
)
RULES_ONLY_SELECT_RULE_IDS: tuple[str, ...] = (
    DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY,
    DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE,
    INVENTORY_KEEP_SOURCE_DIAGNOSIS,
)
CROSS_FAMILY = "cross_family"
# Family that owns each Select rule. A rule reading or writing more than
# one family is CROSS_FAMILY. Used by flatten_family_select_plan to
# validate per-family Select sequences in ThreeStageConfig.
RULE_FAMILY_BY_ID: dict[str, str] = {
    KEEP_DX_NONDIAGNOSTIC_CONTEXT: "Diagnosis",
    KEEP_DX_NESTED_ANCESTOR: "Diagnosis",
    KEEP_DX_NESTED_SURFACE: "Diagnosis",
    KEEP_DX_HEADING_DECOMPOSITION: "Diagnosis",
    KEEP_DX_UNRESTRICTED_SURFACE: "Diagnosis",
    KEEP_DX_EXPANSION_SURFACE: "Diagnosis",
    KEEP_DX_HIERARCHY_ANCESTOR: "Diagnosis",
    KEEP_DX_COMPONENT_TOKEN: "Diagnosis",
    KEEP_SF_NAMED_TYPE: "SeizureFrequency",
    KEEP_SF_HEADING_STATE: "SeizureFrequency",
    KEEP_SF_SEIZURE_FREE: "SeizureFrequency",
    KEEP_SF_STATE_VARIANT: "SeizureFrequency",
    KEEP_RX_RECALL_EXPANSION: "Prescription",
    KEEP_INV_RESULT_VARIANT: "Investigations",
    DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY: "Diagnosis",
    DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE: "Diagnosis",
    PRESCRIPTION_LOCAL_REGIMEN_SCOPE: "Prescription",
    PRESCRIPTION_ACTIVE_TITRATION: "Prescription",
    PRESCRIPTION_EXACT_REGIMEN_DEDUPE: "Prescription",
    SF_NAMED_TYPE_IDENTITY: "SeizureFrequency",
    SF_RECENT_EVENT_OVER_HISTORICAL_FREE: "SeizureFrequency",
    SF_TO_DIAGNOSIS_EXPLICIT_TYPE: CROSS_FAMILY,
    SF_SUPPORTED_STATE_PROMOTION: "SeizureFrequency",
    INVENTORY_KEEP_SOURCE_DIAGNOSIS: "Diagnosis",
    INVENTORY_WEAK_EPISODE_DROP: CROSS_FAMILY,
    INVESTIGATION_SAME_RESULT_DEDUPE: "Investigations",
    SF_RATELESS_ANCHOR_DROP: "SeizureFrequency",
    SF_GENERIC_DUPLICATE_DROP: "SeizureFrequency",
    SF_SEIZURE_FREE_POSITIVE_COUNT_DROP: "SeizureFrequency",
    RECALL_FIRST_UNSUPPORTED_DROP: CROSS_FAMILY,
    INVESTIGATION_RESULTLESS_DROP: "Investigations",
}
_SELECT_PLAN_FAMILIES = frozenset(
    {"Diagnosis", "SeizureFrequency", "Prescription", "Investigations", CROSS_FAMILY}
)


def flatten_family_select_plan(
    plan: Mapping[str, Sequence[str]],
) -> tuple[str, ...]:
    """Validate a per-family Select plan and flatten it to execution order.

    Every rule must be listed under the family that owns it. The flattened
    sequence follows the canonical registry order used by
    ``apply_select_rules`` so a family plan is exactly equivalent to
    enabling the same rule set.
    """

    requested: set[str] = set()
    for family, rule_ids in plan.items():
        if family not in _SELECT_PLAN_FAMILIES:
            raise ValueError(f"unknown Select plan family: {family!r}")
        for rule_id in rule_ids:
            owner = RULE_FAMILY_BY_ID.get(rule_id)
            if owner is None:
                raise ValueError(f"unknown deterministic Select rule id: {rule_id!r}")
            if owner != family:
                raise ValueError(
                    f"Select rule {rule_id!r} belongs to family {owner!r}, "
                    f"not {family!r}"
                )
            requested.add(rule_id)
    return tuple(rule_id for rule_id in CANDIDATE_SELECT_RULE_IDS if rule_id in requested)


_RULE_PORTABILITY_BY_ID = {
    **{rule_id: "clinical_epilepsy" for rule_id in _KEEP_RULE_IDS},
    DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY: "clinical_epilepsy",
    DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE: "benchmark_format",
    PRESCRIPTION_LOCAL_REGIMEN_SCOPE: "clinical_epilepsy",
    PRESCRIPTION_ACTIVE_TITRATION: "clinical_epilepsy",
    PRESCRIPTION_EXACT_REGIMEN_DEDUPE: "benchmark_format",
    SF_NAMED_TYPE_IDENTITY: "seizure_frequency",
    SF_RECENT_EVENT_OVER_HISTORICAL_FREE: "seizure_frequency",
    SF_TO_DIAGNOSIS_EXPLICIT_TYPE: "benchmark_format",
    SF_SUPPORTED_STATE_PROMOTION: "seizure_frequency",
    INVENTORY_KEEP_SOURCE_DIAGNOSIS: "clinical_epilepsy",
    INVENTORY_WEAK_EPISODE_DROP: "clinical_epilepsy",
    INVESTIGATION_SAME_RESULT_DEDUPE: "clinical_epilepsy",
    SF_RATELESS_ANCHOR_DROP: "seizure_frequency",
    SF_GENERIC_DUPLICATE_DROP: "seizure_frequency",
    SF_SEIZURE_FREE_POSITIVE_COUNT_DROP: "seizure_frequency",
    RECALL_FIRST_UNSUPPORTED_DROP: "clinical_epilepsy",
    INVESTIGATION_RESULTLESS_DROP: "clinical_epilepsy",
}

EMITTED_ACTIONS_BY_RULE_ID: dict[str, frozenset[str]] = {
    # Keep rules never emit actions; the recall-first gate records drops.
    **{rule_id: frozenset() for rule_id in _KEEP_RULE_IDS},
    DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY: frozenset({"rewrite"}),
    DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE: frozenset({"add"}),
    PRESCRIPTION_LOCAL_REGIMEN_SCOPE: frozenset({"rewrite"}),
    PRESCRIPTION_ACTIVE_TITRATION: frozenset({"add"}),
    PRESCRIPTION_EXACT_REGIMEN_DEDUPE: frozenset({"drop"}),
    SF_NAMED_TYPE_IDENTITY: frozenset({"rewrite"}),
    SF_RECENT_EVENT_OVER_HISTORICAL_FREE: frozenset({"add", "drop"}),
    SF_TO_DIAGNOSIS_EXPLICIT_TYPE: frozenset({"add"}),
    SF_SUPPORTED_STATE_PROMOTION: frozenset({"add"}),
    INVENTORY_KEEP_SOURCE_DIAGNOSIS: frozenset({"add"}),
    INVENTORY_WEAK_EPISODE_DROP: frozenset({"drop"}),
    INVESTIGATION_SAME_RESULT_DEDUPE: frozenset({"drop"}),
    SF_RATELESS_ANCHOR_DROP: frozenset({"drop"}),
    SF_GENERIC_DUPLICATE_DROP: frozenset({"drop"}),
    SF_SEIZURE_FREE_POSITIVE_COUNT_DROP: frozenset({"drop"}),
    RECALL_FIRST_UNSUPPORTED_DROP: frozenset({"drop"}),
    INVESTIGATION_RESULTLESS_DROP: frozenset({"drop"}),
}

# Keep rules that retain a recall-first direct candidate class at Select.
# A class survives the gate only when its keep rule is enabled; a class
# with a condition in RECALL_FIRST_KEEP_CONDITIONS must also satisfy it.
RECALL_FIRST_KEEP_RULE_BY_CLASS: dict[str, str] = {
    DIAGNOSIS_NONDIAGNOSTIC_CONTEXT: KEEP_DX_NONDIAGNOSTIC_CONTEXT,
    DIAGNOSIS_NESTED_ANCESTOR: KEEP_DX_NESTED_ANCESTOR,
    DIAGNOSIS_NESTED_SURFACE: KEEP_DX_NESTED_SURFACE,
    DIAGNOSIS_HEADING_DECOMPOSITION: KEEP_DX_HEADING_DECOMPOSITION,
    DIAGNOSIS_UNRESTRICTED_SURFACE: KEEP_DX_UNRESTRICTED_SURFACE,
    DIAGNOSIS_EXPANSION_SURFACE: KEEP_DX_EXPANSION_SURFACE,
    DIAGNOSIS_HIERARCHY_ANCESTOR: KEEP_DX_HIERARCHY_ANCESTOR,
    DIAGNOSIS_COMPONENT_TOKEN: KEEP_DX_COMPONENT_TOKEN,
    SF_NAMED_TYPE: KEEP_SF_NAMED_TYPE,
    SF_HEADING_STATE: KEEP_SF_HEADING_STATE,
    SF_SEIZURE_FREE: KEEP_SF_SEIZURE_FREE,
    SF_STATE_VARIANT: KEEP_SF_STATE_VARIANT,
    RX_RECALL_EXPANSION: KEEP_RX_RECALL_EXPANSION,
    INV_RESULT_VARIANT: KEEP_INV_RESULT_VARIANT,
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
_EXPLICIT_SEIZURE_FREE_EVIDENCE_RE = re.compile(
    r"\bseizure\s*[-]?\s*free\b|"
    r"\bno\s+(?:further|more)\s+seizures\b|\bremains?\s+seizure\s*[-]?\s*free\b",
    re.IGNORECASE,
)


def _has_explicit_seizure_free_evidence(evidence: str) -> bool:
    return bool(_EXPLICIT_SEIZURE_FREE_EVIDENCE_RE.search(evidence))


_GENERIC_SF_CUIS = frozenset({"", "C0036572"})
_TYPE_HEADING_RE = re.compile(
    r"^\s*(?:diagnosis|seizure\s+type(?:\s+and\s+frequency)?)\s*:",
    re.IGNORECASE,
)
_SF_DEFERRED_PROMOTION_CLASSES = frozenset(
    {SF_NAMED_TYPE, SF_HEADING_STATE, SF_SEIZURE_FREE}
)
_INVENTORY_WEAK_EPISODE_PHRASES = frozenset(
    {
        "attack",
        "attacks",
        "drop",
        "drop attack",
        "drops",
        "episdoes",
        "episode",
        "episodes",
        "event",
        "events",
        "jerk",
        "several",
    }
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
    verbatim_note_text = note_text
    working = [_copy_mention(row) for row in selected_mentions]
    source = [_copy_mention(row) for row in source_mentions]
    actions: list[dict[str, Any]] = []

    if RECALL_FIRST_UNSUPPORTED_DROP in enabled_rule_ids:
        working, source, records = _drop_unsupported_recall_first(
            working, source, enabled_rule_ids, note_text=verbatim_note_text
        )
        actions.extend(records)
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
    if SF_SUPPORTED_STATE_PROMOTION in enabled_rule_ids:
        working, records = _promote_supported_sf_deferred(working, source, verbatim_note_text)
        actions.extend(records)
    if INVENTORY_KEEP_SOURCE_DIAGNOSIS in enabled_rule_ids:
        working, records = _keep_source_ancestor_diagnoses(working, source)
        actions.extend(records)
    if INVENTORY_WEAK_EPISODE_DROP in enabled_rule_ids:
        working, records = _drop_weak_episode_mentions(working)
        actions.extend(records)
    if INVESTIGATION_SAME_RESULT_DEDUPE in enabled_rule_ids:
        working, records = _dedupe_same_investigation_results(working)
        actions.extend(records)
    if SF_RATELESS_ANCHOR_DROP in enabled_rule_ids:
        working, records = _drop_rateless_sf_anchors(working)
        actions.extend(records)
    if SF_GENERIC_DUPLICATE_DROP in enabled_rule_ids:
        working, records = _drop_generic_sf_duplicates_of_named_type(working)
        actions.extend(records)
    if SF_SEIZURE_FREE_POSITIVE_COUNT_DROP in enabled_rule_ids:
        working, records = _drop_seizure_free_positive_count_sf(working)
        actions.extend(records)
    if INVESTIGATION_RESULTLESS_DROP in enabled_rule_ids:
        working, records = _drop_resultless_investigations(working)
        actions.extend(records)

    return working, actions


def _mention_recall_first_class(mention: Mapping[str, Any]) -> str | None:
    return recall_first_class_of(str(mention.get("component_owner") or ""))


# A result variant is kept only when its evidence asserts the test event
# itself ("had a CT head", "underwent an MRI", "recent EEG results") and
# names the modality exactly once. Planned tests and anaphoric references
# to an already-reported result ("the EEG changes", "requesting an MRI")
# stay dropped, as does a sentence that names the modality again with its
# result ("had an EEG ... no EEG changes"): there the result-less token
# belongs to the same test event, not a separate reportable mention.
_INV_TEST_EVENT_RE = re.compile(
    r"\b(?:had|underwent)\s+an?\b(?P<window>[^.\n]{0,30})"
    r"|\brecent\s+(?P<recent>\w+)\s+results?\b",
    re.IGNORECASE,
)


def _inv_result_variant_condition(
    mention: Mapping[str, Any], note_text: str
) -> bool:
    modalities = {
        key[: -len("_Performed")].lower()
        for key in _attrs(mention)
        if key.endswith("_Performed")
    }
    evidence = str(mention.get("evidence") or "")
    evidence_words = [word.lower() for word in re.findall(r"\w+", evidence)]
    if any(evidence_words.count(modality) != 1 for modality in modalities):
        return False
    for match in _INV_TEST_EVENT_RE.finditer(evidence):
        window = match.group("window") or match.group("recent") or ""
        if any(word.lower() in modalities for word in re.findall(r"\w+", window)):
            return True
    return False


# An Rx recall candidate is kept only when its evidence describes the
# current regimen. Conditional requests ("if you could prescribe"),
# queries and refusals ("asked about whether", "wouldn't recommend"),
# and transitional doses inside an upward titration ("400mg od,
# increasing to 800mg od") are proposals, not prescriptions.
_RX_NONCURRENT_RE = re.compile(
    r"\bif\s+you\s+could\s+prescribe\b"
    r"|\basked\s+about\s+whether\b"
    r"|\b(?:would\s+not|wouldn[\u2019']t|not)\s+recommend\b"
    r"|\bincreasing\s+to\b",
    re.IGNORECASE,
)


def _rx_recall_expansion_condition(
    mention: Mapping[str, Any], note_text: str
) -> bool:
    return not _RX_NONCURRENT_RE.search(str(mention.get("evidence") or ""))


# SF state variants: the cluster surface counts as an active event only
# when the letter reports it happened ("had a cluster of seizures");
# hypothetical or descriptive references stay dropped. The plural
# "seizures free" surface only fills a gap when the well-formed singular
# surface is absent from the letter (otherwise the direct path already
# owns that state and the variant would double-count it).
_SF_CLUSTER_EVENT_RE = re.compile(
    r"\bhad\s+a\s+cluster\s+of\s+seizures\b", re.IGNORECASE
)
_SF_SINGULAR_FREE_RE = re.compile(r"\bseizure\s+free\b", re.IGNORECASE)


def _sf_state_variant_condition(mention: Mapping[str, Any], note_text: str) -> bool:
    phrase = str(_attrs(mention).get("CUIPhrase") or "")
    if phrase == "cluster-of-seizures":
        return bool(
            _SF_CLUSTER_EVENT_RE.search(str(mention.get("evidence") or ""))
        )
    if phrase == "seizure-free":
        return not _SF_SINGULAR_FREE_RE.search(note_text)
    return True


# Per-class keep conditions. A class without an entry is kept
# unconditionally when its keep rule is enabled.
RECALL_FIRST_KEEP_CONDITIONS: dict[str, Any] = {
    INV_RESULT_VARIANT: _inv_result_variant_condition,
    RX_RECALL_EXPANSION: _rx_recall_expansion_condition,
    SF_STATE_VARIANT: _sf_state_variant_condition,
}


def _drop_unsupported_recall_first(
    working: list[dict[str, Any]],
    source: list[dict[str, Any]],
    enabled_rule_ids: Set[str],
    *,
    note_text: str = "",
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Gate recall-first direct candidates before any other Select rule runs.

    A tagged candidate survives only when its class has a registered keep
    rule that is enabled (Phase C) and passes that class's keep condition,
    if one is registered; otherwise it is removed from both the working
    set and the source view so downstream rules observe exactly the
    pre-restructure ledger.
    """

    def _keep(mention: Mapping[str, Any]) -> bool:
        candidate_class = _mention_recall_first_class(mention)
        if candidate_class is None:
            return True
        keep_rule = RECALL_FIRST_KEEP_RULE_BY_CLASS.get(candidate_class)
        if keep_rule is None or keep_rule not in enabled_rule_ids:
            return False
        condition = RECALL_FIRST_KEEP_CONDITIONS.get(candidate_class)
        return condition is None or condition(mention, note_text)

    kept_working: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    for mention in working:
        if _keep(mention):
            kept_working.append(mention)
            continue
        actions.append(_action(RECALL_FIRST_UNSUPPORTED_DROP, "drop", before=mention))
    kept_source = [mention for mention in source if _keep(mention)]
    return kept_working, kept_source, actions


def _drop_resultless_investigations(
    selected: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    out: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    for mention in selected:
        if _entity(mention) == "Investigations" and not any(
            key.endswith("_Results") for key in _attrs(mention)
        ):
            actions.append(_action(INVESTIGATION_RESULTLESS_DROP, "drop", before=mention))
            continue
        out.append(mention)
    return out, actions


def _keep_source_ancestor_diagnoses(
    selected: list[dict[str, Any]], source: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected_concepts = {
        canonicalize_diagnosis_concept(str(mention.get("text") or ""))
        for mention in selected
        if _entity(mention) == "Diagnosis"
    }
    out = list(selected)
    actions: list[dict[str, Any]] = []
    for mention in source:
        if _entity(mention) != "Diagnosis":
            continue
        concept = canonicalize_diagnosis_concept(str(mention.get("text") or ""))
        if not concept or concept in _INVENTORY_WEAK_EPISODE_PHRASES:
            continue
        if _has_equivalent_diagnosis(out, mention):
            continue
        if not any(
            is_diagnosis_descendant(selected_concept, concept)
            for selected_concept in selected_concepts
            if selected_concept
        ):
            continue
        addition = _with_action_provenance(
            _diagnosis_normalized_copy(mention),
            rule_id=INVENTORY_KEEP_SOURCE_DIAGNOSIS,
            action="add",
        )
        out.append(addition)
        actions.append(
            _action(
                INVENTORY_KEEP_SOURCE_DIAGNOSIS,
                "add",
                after=addition,
            )
        )
    return out, actions


def _drop_weak_episode_mentions(
    selected: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    out: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    for mention in selected:
        entity = _entity(mention)
        concept = canonicalize_diagnosis_concept(str(mention.get("text") or ""))
        if entity in {"Diagnosis", "SeizureFrequency"} and (
            concept in _INVENTORY_WEAK_EPISODE_PHRASES
            or normalize_phrase(str(mention.get("text") or ""))
            in _INVENTORY_WEAK_EPISODE_PHRASES
        ):
            actions.append(
                _action(
                    INVENTORY_WEAK_EPISODE_DROP,
                    "drop",
                    before=mention,
                )
            )
            continue
        out.append(mention)
    return out, actions


def _investigation_result_key(mention: Mapping[str, Any]) -> tuple[str, str] | None:
    if _entity(mention) != "Investigations":
        return None
    attrs = _attrs(mention)
    modality = next(
        (
            name
            for name in ("EEG", "MRI", "CT")
            if attrs.get(f"{name}_Performed") == "Yes"
        ),
        str(mention.get("text") or ""),
    )
    result = str(attrs.get(f"{modality}_Results") or "")
    if not modality:
        return None
    return (modality, result)


def _dedupe_same_investigation_results(
    selected: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    out: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for mention in selected:
        key = _investigation_result_key(mention)
        if key is None:
            out.append(mention)
            continue
        if key in seen:
            actions.append(_action(INVESTIGATION_SAME_RESULT_DEDUPE, "drop", before=mention))
            continue
        seen.add(key)
        out.append(mention)
    return out, actions


def _has_frequency_attributes(mention: Mapping[str, Any]) -> bool:
    return bool(set(_attrs(mention)) - {"CUI", "CUIPhrase"})


def _drop_rateless_sf_anchors(
    selected: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    out: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    for mention in selected:
        if _entity(mention) == "SeizureFrequency" and not _has_frequency_attributes(mention):
            actions.append(_action(SF_RATELESS_ANCHOR_DROP, "drop", before=mention))
            continue
        out.append(mention)
    return out, actions


_SF_FREQUENCY_STATE_RATE_KEYS: tuple[str, ...] = (
    "NumberOfSeizures",
    "LowerNumberOfSeizures",
    "UpperNumberOfSeizures",
    "TimePeriod",
    "NumberOfTimePeriods",
)
_SEIZURE_FREE_CUI = "C1299590"


def _sf_frequency_state_unit_key(mention: Mapping[str, Any]) -> tuple[Any, ...]:
    attrs = _attrs(mention)
    state = _frequency_state(attrs)
    rate = tuple(
        sorted(
            (key, str(attrs[key]))
            for key in _SF_FREQUENCY_STATE_RATE_KEYS
            if attrs.get(key)
        )
    )
    return (state, rate)


def _is_generic_sf_mention(mention: Mapping[str, Any]) -> bool:
    return _entity(mention) == "SeizureFrequency" and _sf_cui(mention) in _GENERIC_SF_CUIS


def _is_named_sf_mention(mention: Mapping[str, Any]) -> bool:
    return _entity(mention) == "SeizureFrequency" and _sf_cui(mention) not in _GENERIC_SF_CUIS


def _drop_generic_sf_duplicates_of_named_type(
    selected: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    named_units = {
        _sf_frequency_state_unit_key(mention)
        for mention in selected
        if _is_named_sf_mention(mention)
    }
    out: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    for mention in selected:
        if (
            _is_generic_sf_mention(mention)
            and _sf_frequency_state_unit_key(mention) in named_units
        ):
            actions.append(_action(SF_GENERIC_DUPLICATE_DROP, "drop", before=mention))
            continue
        out.append(mention)
    return out, actions


def _is_seizure_free_surface(mention: Mapping[str, Any]) -> bool:
    if _entity(mention) != "SeizureFrequency":
        return False
    attrs = _attrs(mention)
    if attrs.get("CUI") == _SEIZURE_FREE_CUI:
        return True
    phrase = normalize_phrase(str(mention.get("text") or ""))
    cuiphrase = normalize_phrase(str(attrs.get("CUIPhrase") or ""))
    return phrase == "seizure free" or cuiphrase == "seizure free"


def _has_positive_sf_count(mention: Mapping[str, Any]) -> bool:
    attrs = _attrs(mention)
    for key in ("NumberOfSeizures", "LowerNumberOfSeizures", "UpperNumberOfSeizures"):
        value = str(attrs.get(key) or "")
        if not value or value == "0":
            continue
        try:
            if float(value) > 0:
                return True
        except ValueError:
            return True
    return False


def _drop_seizure_free_positive_count_sf(
    selected: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    out: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    for mention in selected:
        if _is_seizure_free_surface(mention) and _has_positive_sf_count(mention):
            actions.append(
                _action(SF_SEIZURE_FREE_POSITIVE_COUNT_DROP, "drop", before=mention)
            )
            continue
        out.append(mention)
    return out, actions


def _sf_inventory_unit_keys(mention: Mapping[str, Any]) -> tuple[Any, ...]:
    annotation = annotation_from_mapping(dict(mention))
    return tuple(_frequency_state_keys([annotation], "clinical_headline"))


def _selected_sf_inventory_unit_keys(selected: Sequence[Mapping[str, Any]]) -> set[Any]:
    keys: set[Any] = set()
    for mention in selected:
        if _entity(mention) == "SeizureFrequency":
            keys.update(_sf_inventory_unit_keys(mention))
    return keys


def _evidence_on_frequency_section_line(evidence: str, note_text: str) -> bool:
    for line in note_text.splitlines():
        if evidence not in line:
            continue
        if "seizure type and frequency" in line.lower():
            return True
    return False


def _sf_deferred_candidate_supported(
    mention: Mapping[str, Any],
    *,
    note_text: str,
) -> bool:
    candidate_class = str(mention.get("candidate_class") or "")
    evidence = str(mention.get("evidence") or "")
    if candidate_class == SF_NAMED_TYPE:
        return _evidence_on_frequency_section_line(evidence, note_text)
    if candidate_class == SF_SEIZURE_FREE:
        return _has_explicit_seizure_free_evidence(evidence)
    if candidate_class == SF_HEADING_STATE:
        return _frequency_state(_attrs(mention)) != "unknown"
    return False


def _should_promote_sf_deferred_candidate(
    mention: Mapping[str, Any],
    *,
    selected_units: set[Any],
) -> bool:
    candidate_class = str(mention.get("candidate_class") or "")
    unit_keys = _sf_inventory_unit_keys(mention)
    if not unit_keys:
        return False
    if any(unit in selected_units for unit in unit_keys):
        return False
    if candidate_class == SF_NAMED_TYPE:
        return True
    state = _frequency_state(_attrs(mention))
    return state != "unknown"


def _promote_supported_sf_deferred(
    selected: list[dict[str, Any]],
    source: list[dict[str, Any]],
    note_text: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected_units = _selected_sf_inventory_unit_keys(selected)
    out = list(selected)
    actions: list[dict[str, Any]] = []
    for mention in source:
        if str(mention.get("candidate_class") or "") not in _SF_DEFERRED_PROMOTION_CLASSES:
            continue
        if _entity(mention) != "SeizureFrequency":
            continue
        evidence = str(mention.get("evidence") or "")
        if not evidence or evidence not in note_text:
            continue
        if not _sf_deferred_candidate_supported(mention, note_text=note_text):
            continue
        if not _should_promote_sf_deferred_candidate(
            mention,
            selected_units=selected_units,
        ):
            continue
        addition = _with_action_provenance(
            _copy_mention(mention),
            rule_id=SF_SUPPORTED_STATE_PROMOTION,
            action="add",
        )
        out.append(addition)
        selected_units.update(_sf_inventory_unit_keys(addition))
        actions.append(
            _action(
                SF_SUPPORTED_STATE_PROMOTION,
                "add",
                after=addition,
            )
        )
    return out, actions


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
    "CROSS_FAMILY",
    "RULE_FAMILY_BY_ID",
    "flatten_family_select_plan",
    "DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE",
    "DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY",
    "EMITTED_ACTIONS_BY_RULE_ID",
    "INVENTORY_KEEP_SOURCE_DIAGNOSIS",
    "INVENTORY_SELECT_RULE_IDS",
    "INVENTORY_WEAK_EPISODE_DROP",
    "INVESTIGATION_SAME_RESULT_DEDUPE",
    "RULES_ONLY_SELECT_RULE_IDS",
    "SF_RATELESS_ANCHOR_DROP",
    "SF_GENERIC_DUPLICATE_DROP",
    "SF_SEIZURE_FREE_POSITIVE_COUNT_DROP",
    "PRESCRIPTION_ACTIVE_TITRATION",
    "PRESCRIPTION_EXACT_REGIMEN_DEDUPE",
    "PRESCRIPTION_LOCAL_REGIMEN_SCOPE",
    "SF_NAMED_TYPE_IDENTITY",
    "SF_RECENT_EVENT_OVER_HISTORICAL_FREE",
    "SF_SUPPORTED_STATE_PROMOTION",
    "SF_TO_DIAGNOSIS_EXPLICIT_TYPE",
    "apply_select_rules",
]
