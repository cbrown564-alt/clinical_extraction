"""Conservative agentic patches over structured-event Gan outputs.

This module is intentionally smaller than a live agent runner. It defines the
typed patch surface that tools or specialist agents must satisfy before they can
change a `hybrid_structured_events` final selection.
"""

from __future__ import annotations

import copy
import json
from collections.abc import Mapping, Sequence
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist

PatchAction = Literal["keep", "abstain", "select_existing_event"]
PatchFamily = Literal[
    "raise_current_burden",
    "restore_cluster_burden",
    "restore_recent_unresolved_burden",
    "block_boundary_demotion",
    "other",
]
PatchPolicy = Literal["recent_unresolved_burden_v0"]

_BOUNDARY_KINDS = {"seizure_free", "unknown", "no_reference"}
_FREQUENCY_KINDS = {"frequency", "unresolved_multiple"}


class StructuredEventPatch(BaseModel):
    """Agent/tool proposal to patch a structured-events selection.

    Patches name event ids already present in the structured-events artifact.
    Event addition is deliberately left for a later protocol because it needs a
    separate evidence-normalization contract.
    """

    model_config = ConfigDict(extra="forbid")

    action: PatchAction
    patch_family: PatchFamily = "other"
    selected_event_ids: tuple[str, ...] = Field(default_factory=tuple)
    confidence: Literal["low", "medium", "high"] = "low"
    evidence: str | None = None
    rationale: str


def apply_selection_patch(
    row: Mapping[str, Any],
    patch: StructuredEventPatch,
) -> dict[str, Any]:
    """Apply one conservative selection patch to a structured-events row."""

    patched = copy.deepcopy(dict(row))
    baseline_label = _baseline_label(row)
    baseline_ids = _baseline_selected_event_ids(row)
    final_label = baseline_label
    selected_ids = baseline_ids
    accepted = False
    reason = f"fallback_action:{patch.action}"

    if patch.action == "select_existing_event":
        accepted, reason, final_label, selected_ids = _evaluate_selection_patch(
            row,
            patch,
            baseline_label=baseline_label,
            baseline_ids=baseline_ids,
        )

    patched_comparison = _comparison_for_label(final_label, row)
    patched["agentic_patch"] = {
        "proposal": patch.model_dump(mode="json"),
        "accepted": accepted,
        "reason": reason,
        "baseline_final_label": baseline_label,
        "baseline_selected_event_ids": list(baseline_ids),
    }
    patched["patched_final_label"] = final_label
    patched["patched_selected_event_ids"] = list(selected_ids)
    patched["patched_comparison"] = patched_comparison
    patched["patch_transition"] = _transition(
        baseline_comparison=dict(row.get("comparison") or {}),
        patched_comparison=patched_comparison,
        baseline_label=baseline_label,
        patched_label=final_label,
        accepted=accepted,
    )
    return patched


def summarize_patch_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize accepted patch precision over saved structured-event rows."""

    accepted = 0
    changed = 0
    wrong_to_correct = 0
    correct_to_wrong = 0
    correct_to_correct = 0
    wrong_to_wrong = 0
    reasons: dict[str, int] = {}

    for row in rows:
        patch_info = dict(row.get("agentic_patch") or {})
        transition = dict(row.get("patch_transition") or {})
        reason = str(patch_info.get("reason") or "missing_patch_info")
        reasons[reason] = reasons.get(reason, 0) + 1
        if not patch_info.get("accepted"):
            continue
        accepted += 1
        if transition.get("label_changed"):
            changed += 1
        if transition.get("purist_transition") == "wrong_to_correct":
            wrong_to_correct += 1
        elif transition.get("purist_transition") == "correct_to_wrong":
            correct_to_wrong += 1
        elif transition.get("purist_transition") == "correct_to_correct":
            correct_to_correct += 1
        elif transition.get("purist_transition") == "wrong_to_wrong":
            wrong_to_wrong += 1

    return {
        "rows": len(rows),
        "accepted_patches": accepted,
        "changed_labels": changed,
        "wrong_to_correct": wrong_to_correct,
        "correct_to_wrong": correct_to_wrong,
        "correct_to_correct": correct_to_correct,
        "wrong_to_wrong": wrong_to_wrong,
        "net_purist_gain": wrong_to_correct - correct_to_wrong,
        "changed_label_precision": (wrong_to_correct / changed) if changed else 0.0,
        "reasons": reasons,
    }


def propose_selection_patch(
    row: Mapping[str, Any],
    *,
    policy: PatchPolicy = "recent_unresolved_burden_v0",
) -> StructuredEventPatch:
    """Propose one conservative patch from inference-available event fields."""

    if policy == "recent_unresolved_burden_v0":
        return _propose_recent_unresolved_burden_patch(row)
    return _keep_patch(f"Unsupported patch policy: {policy}")


def propose_selection_patches(
    rows: Sequence[Mapping[str, Any]],
    *,
    policy: PatchPolicy = "recent_unresolved_burden_v0",
) -> dict[int | str, StructuredEventPatch]:
    """Return non-keep patch proposals keyed by source row index."""

    proposals: dict[int | str, StructuredEventPatch] = {}
    for row in rows:
        source_row_index = row.get("source_row_index")
        if source_row_index is None:
            continue
        patch = propose_selection_patch(row, policy=policy)
        if patch.action == "select_existing_event":
            proposals[source_row_index] = patch
    return proposals


def run_patch_replay(
    rows: Sequence[Mapping[str, Any]],
    patch_proposals: Mapping[int | str, StructuredEventPatch | Mapping[str, Any]],
    *,
    split: str,
    split_manifest: str,
    source_artifact: str,
    condition: str = "structured_event_selection_patch_v0",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Replay typed patch proposals over saved structured-events rows."""

    patched_rows: list[dict[str, Any]] = []
    for row in rows:
        source_row_index = row.get("source_row_index")
        patch = _patch_for_source_index(patch_proposals, source_row_index)
        if patch is None:
            patch = StructuredEventPatch(
                action="keep",
                confidence="high",
                rationale="No patch proposal supplied; keep baseline structured selection.",
            )
        patched_rows.append(apply_selection_patch(row, patch))

    metadata = {
        "artifact_kind": "gan2026_agentic_structured_event_patch_replay",
        "pipeline_family": "agentic_structured_event_patch",
        "condition": condition,
        "split": split,
        "split_manifest": split_manifest,
        "source_artifact": source_artifact,
        "mode": "no_call_replay",
        "claim_boundary": (
            "validation-development replay over saved structured-event artifacts; "
            "patch acceptance uses inference-available event and normalization "
            "fields only, while gold labels are used only for post-hoc scoring"
        ),
        "summary": summarize_replay_rows(patched_rows),
    }
    return patched_rows, metadata


def summarize_replay_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize baseline and patched accuracy plus patch transitions."""

    patch_summary = summarize_patch_rows(rows)
    baseline_purist = 0
    baseline_pragmatic = 0
    patched_purist = 0
    patched_pragmatic = 0
    scored_patched = 0
    for row in rows:
        baseline_comparison = row.get("comparison") or {}
        patched_comparison = row.get("patched_comparison") or {}
        if isinstance(baseline_comparison, Mapping):
            baseline_purist += int(baseline_comparison.get("purist_correct") is True)
            baseline_pragmatic += int(baseline_comparison.get("pragmatic_correct") is True)
        if isinstance(patched_comparison, Mapping) and patched_comparison:
            scored_patched += 1
            patched_purist += int(patched_comparison.get("purist_correct") is True)
            patched_pragmatic += int(patched_comparison.get("pragmatic_correct") is True)
    rows_count = len(rows)
    return {
        **patch_summary,
        "baseline_purist_correct": baseline_purist,
        "baseline_pragmatic_correct": baseline_pragmatic,
        "patched_purist_correct": patched_purist,
        "patched_pragmatic_correct": patched_pragmatic,
        "baseline_purist_accuracy": (baseline_purist / rows_count) if rows_count else 0.0,
        "baseline_pragmatic_accuracy": (baseline_pragmatic / rows_count) if rows_count else 0.0,
        "patched_purist_accuracy": (patched_purist / rows_count) if rows_count else 0.0,
        "patched_pragmatic_accuracy": (patched_pragmatic / rows_count) if rows_count else 0.0,
        "patched_scored_rows": scored_patched,
    }


def _evaluate_selection_patch(
    row: Mapping[str, Any],
    patch: StructuredEventPatch,
    *,
    baseline_label: str | None,
    baseline_ids: tuple[str, ...],
) -> tuple[bool, str, str | None, tuple[str, ...]]:
    if patch.confidence != "high":
        return False, "low_confidence_patch", baseline_label, baseline_ids
    if len(patch.selected_event_ids) != 1:
        return False, "unsupported_multi_event_selection_v0", baseline_label, baseline_ids

    event_id = patch.selected_event_ids[0]
    event_by_id = _events_by_id(row)
    normalized_by_id = _normalized_by_id(row)
    event = event_by_id.get(event_id)
    normalized = normalized_by_id.get(event_id)
    if event is None or normalized is None:
        return False, "unknown_event_id", baseline_label, baseline_ids
    if normalized.get("validation_errors"):
        return False, "candidate_normalization_invalid", baseline_label, baseline_ids

    candidate_label = _as_optional_str(normalized.get("normalized_label"))
    if candidate_label is None:
        return False, "candidate_label_missing", baseline_label, baseline_ids
    if patch.evidence and not _patch_evidence_is_valid(row, patch.evidence):
        return False, "evidence_not_exact_substring", baseline_label, baseline_ids

    baseline_kind = _baseline_kind(row)
    candidate_kind = _as_optional_str(
        normalized.get("semantic_kind")
    ) or _event_selection_kind(event)
    if baseline_kind in _FREQUENCY_KINDS and candidate_kind in _BOUNDARY_KINDS:
        return False, "unsupported_boundary_demotion", baseline_label, baseline_ids
    if candidate_label == baseline_label and tuple(patch.selected_event_ids) == baseline_ids:
        return False, "no_selection_change", baseline_label, baseline_ids

    if patch.patch_family == "raise_current_burden":
        if not _is_higher_burden(row, normalized):
            return False, "candidate_not_higher_burden", baseline_label, baseline_ids
    elif patch.patch_family == "restore_cluster_burden":
        if not _is_cluster_restore(event, candidate_label):
            return False, "candidate_not_cluster_restore", baseline_label, baseline_ids
    elif patch.patch_family == "restore_recent_unresolved_burden":
        if not _is_recent_unresolved_frequency_event(event, normalized):
            return (
                False,
                "candidate_not_recent_unresolved_frequency",
                baseline_label,
                baseline_ids,
            )
    else:
        return False, "unsupported_patch_family", baseline_label, baseline_ids

    return (
        True,
        f"accepted_{patch.patch_family}",
        candidate_label,
        tuple(patch.selected_event_ids),
    )


def _patch_for_source_index(
    patch_proposals: Mapping[int | str, StructuredEventPatch | Mapping[str, Any]],
    source_row_index: Any,
) -> StructuredEventPatch | None:
    if source_row_index is None:
        return None
    patch = patch_proposals.get(source_row_index)
    if patch is None:
        patch = patch_proposals.get(str(source_row_index))
    if patch is None:
        try:
            patch = patch_proposals.get(int(source_row_index))
        except (TypeError, ValueError):
            patch = None
    if patch is None:
        return None
    if isinstance(patch, StructuredEventPatch):
        return patch
    return StructuredEventPatch.model_validate(patch)


def _propose_recent_unresolved_burden_patch(
    row: Mapping[str, Any],
) -> StructuredEventPatch:
    baseline_ids = set(_baseline_selected_event_ids(row))
    event_by_id = _events_by_id(row)
    normalized_by_id = _normalized_by_id(row)
    candidates: list[tuple[int, str, Mapping[str, Any]]] = []
    for event_id, event in event_by_id.items():
        if event_id in baseline_ids:
            continue
        normalized = normalized_by_id.get(event_id)
        if normalized is None:
            continue
        if not _is_recent_unresolved_frequency_event(event, normalized):
            continue
        evidence = _as_optional_str(event.get("evidence"))
        if evidence is None:
            continue
        candidates.append((_temporality_rank(event), event_id, event))

    if not candidates:
        return _keep_patch("No recent asserted unresolved-frequency event available.")

    _, event_id, event = sorted(candidates, key=lambda item: (item[0], item[1]))[0]
    return StructuredEventPatch(
        action="select_existing_event",
        patch_family="restore_recent_unresolved_burden",
        selected_event_ids=(event_id,),
        confidence="high",
        evidence=_as_optional_str(event.get("evidence")),
        rationale=(
            "A recent asserted unresolved frequency event was extracted "
            "but not selected; preserve the source-near vague burden instead "
            "of an over-specific or boundary selection."
        ),
    )


def _keep_patch(rationale: str) -> StructuredEventPatch:
    return StructuredEventPatch(
        action="keep",
        confidence="high",
        rationale=rationale,
    )


def _transition(
    *,
    baseline_comparison: Mapping[str, Any],
    patched_comparison: Mapping[str, Any],
    baseline_label: str | None,
    patched_label: str | None,
    accepted: bool,
) -> dict[str, Any]:
    baseline_correct = baseline_comparison.get("purist_correct")
    patched_correct = patched_comparison.get("purist_correct")
    if baseline_correct is True and patched_correct is True:
        purist_transition = "correct_to_correct"
    elif baseline_correct is True and patched_correct is False:
        purist_transition = "correct_to_wrong"
    elif baseline_correct is False and patched_correct is True:
        purist_transition = "wrong_to_correct"
    elif baseline_correct is False and patched_correct is False:
        purist_transition = "wrong_to_wrong"
    else:
        purist_transition = "unscored"
    return {
        "accepted": accepted,
        "label_changed": baseline_label != patched_label,
        "purist_transition": purist_transition,
    }


def _comparison_for_label(label: str | None, row: Mapping[str, Any]) -> dict[str, Any]:
    if label is None:
        return {}
    gold_monthly = _gold_monthly_frequency(row)
    if gold_monthly is None:
        return {}
    try:
        predicted = label_to_frequency_record(label)
    except ValueError:
        return {}
    predicted_purist = str(map_purist(predicted.monthly_frequency))
    gold_purist = str(map_purist(gold_monthly))
    predicted_pragmatic = str(map_pragmatic(predicted.monthly_frequency))
    gold_pragmatic = str(map_pragmatic(gold_monthly))
    return {
        "predicted_monthly_frequency": predicted.monthly_frequency,
        "gold_monthly_frequency": gold_monthly,
        "predicted_purist_category": predicted_purist,
        "gold_purist_category": gold_purist,
        "purist_correct": predicted_purist == gold_purist,
        "predicted_pragmatic_category": predicted_pragmatic,
        "gold_pragmatic_category": gold_pragmatic,
        "pragmatic_correct": predicted_pragmatic == gold_pragmatic,
    }


def _baseline_label(row: Mapping[str, Any]) -> str | None:
    selection = _selection(row)
    return _as_optional_str(selection.get("final_label"))


def _baseline_kind(row: Mapping[str, Any]) -> str | None:
    selection = _selection(row)
    return _as_optional_str(selection.get("final_kind"))


def _baseline_selected_event_ids(row: Mapping[str, Any]) -> tuple[str, ...]:
    selection = _selection(row)
    return tuple(str(event_id) for event_id in selection.get("selected_event_ids") or ())


def _selection(row: Mapping[str, Any]) -> Mapping[str, Any]:
    structured = row.get("structured_record") or {}
    if isinstance(structured, Mapping):
        selection = structured.get("selection") or {}
        if isinstance(selection, Mapping):
            return selection
    return {}


def _events_by_id(row: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    structured = row.get("structured_record") or {}
    events = structured.get("events") if isinstance(structured, Mapping) else []
    return {
        str(event.get("event_id")): event
        for event in events or []
        if isinstance(event, Mapping) and event.get("event_id") is not None
    }


def _normalized_by_id(row: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(event.get("event_id")): event
        for event in row.get("normalized_events") or []
        if isinstance(event, Mapping) and event.get("event_id") is not None
    }


def _patch_evidence_is_valid(row: Mapping[str, Any], evidence: str) -> bool:
    note_text = _note_text(row)
    if note_text is None:
        event_evidence = {
            str(event.get("evidence"))
            for event in _events_by_id(row).values()
            if event.get("evidence") is not None
        }
        return evidence in event_evidence
    return evidence_is_substring(note_text, evidence)


def _note_text(row: Mapping[str, Any]) -> str | None:
    prompt_input_json = row.get("prompt_input_json")
    if not isinstance(prompt_input_json, str):
        return None
    try:
        payload = json.loads(prompt_input_json)
    except json.JSONDecodeError:
        return None
    note_text = payload.get("note_text")
    return note_text if isinstance(note_text, str) else None


def _event_selection_kind(event: Mapping[str, Any]) -> str | None:
    event_kind = _as_optional_str(event.get("kind"))
    if event_kind in {"frequency_rate", "cluster_frequency"}:
        return "frequency"
    if event_kind == "unknown_frequency":
        return "unknown"
    return event_kind


def _is_higher_burden(row: Mapping[str, Any], candidate: Mapping[str, Any]) -> bool:
    candidate_monthly = _as_float(candidate.get("monthly_frequency"))
    baseline_monthly = _baseline_monthly_frequency(row)
    if candidate_monthly is None or baseline_monthly is None:
        return False
    return candidate_monthly > baseline_monthly


def _baseline_monthly_frequency(row: Mapping[str, Any]) -> float | None:
    selected_ids = _baseline_selected_event_ids(row)
    normalized_by_id = _normalized_by_id(row)
    selected_monthlies = [
        _as_float(normalized_by_id[event_id].get("monthly_frequency"))
        for event_id in selected_ids
        if event_id in normalized_by_id
    ]
    selected_monthlies = [value for value in selected_monthlies if value is not None]
    if selected_monthlies:
        return max(selected_monthlies)
    label = _baseline_label(row)
    if label is None:
        return None
    try:
        return float(label_to_frequency_record(label).monthly_frequency)
    except ValueError:
        return None


def _is_cluster_restore(event: Mapping[str, Any], candidate_label: str) -> bool:
    return event.get("kind") == "cluster_frequency" or "cluster" in candidate_label


def _is_recent_unresolved_frequency_event(
    event: Mapping[str, Any],
    normalized: Mapping[str, Any],
) -> bool:
    if normalized.get("validation_errors"):
        return False
    candidate_label = _as_optional_str(normalized.get("normalized_label"))
    if candidate_label is None or "multiple" not in candidate_label:
        return False
    return (
        event.get("kind") == "frequency_rate"
        and event.get("assertion_status") == "asserted"
        and event.get("temporality") == "recent"
        and normalized.get("semantic_kind") == "unresolved_multiple"
    )


def _temporality_rank(event: Mapping[str, Any]) -> int:
    temporality = event.get("temporality")
    if temporality == "current":
        return 0
    if temporality == "recent":
        return 1
    return 2


def _gold_monthly_frequency(row: Mapping[str, Any]) -> float | None:
    reference = row.get("reference") or {}
    if isinstance(reference, Mapping):
        value = _as_float(reference.get("gold_monthly_frequency"))
        if value is not None:
            return value
    comparison = row.get("comparison") or {}
    if isinstance(comparison, Mapping):
        return _as_float(comparison.get("gold_monthly_frequency"))
    return None


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
