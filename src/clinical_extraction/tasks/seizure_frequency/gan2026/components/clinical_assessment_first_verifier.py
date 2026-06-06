"""Action-only first verifier contract for Gan 2026 clinical-assessment packets."""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, Field, ValidationError

POLICY_ID = "gan2026_clinical_assessment_first_verifier_v0"
SCHEMA_VERSION = "gan2026_clinical_assessment_first_verifier_output_v0"
COMPONENT_OWNER = "llm_verifier"
ALLOWED_ACTIONS = {"affirm", "reject", "abstain", "human_review"}


class FirstVerifierOutput(BaseModel):
    source_row_index: int
    component_owner: str
    schema_version: str
    verifier_policy_id: str
    baseline_action: str
    action: str
    action_basis: str = ""
    cited_candidate_ids: list[str] = Field(default_factory=list)
    cited_source_ids: list[str] = Field(default_factory=list)
    issue_flags: list[str] = Field(default_factory=list)
    rationale: str = ""
    proposed_rendered_label: str | None = None
    final_rendered_label: str | None = None
    replacement_rendered_label: str | None = None


def parse_output(raw_output: str) -> tuple[FirstVerifierOutput | None, list[str]]:
    """Parse a first-verifier JSON response."""

    try:
        payload = json.loads(_extract_json_object(raw_output))
        parsed = FirstVerifierOutput.model_validate(_normalize_payload(payload))
    except (json.JSONDecodeError, ValidationError, ValueError) as exc:
        return None, [f"{type(exc).__name__}: {exc}"]
    errors = []
    if parsed.action not in ALLOWED_ACTIONS:
        errors.append(f"unsupported_action:{parsed.action}")
    if parsed.baseline_action not in ALLOWED_ACTIONS:
        errors.append(f"unsupported_baseline_action:{parsed.baseline_action}")
    return (None, errors) if errors else (parsed, [])


def verifier_decision(
    parsed: FirstVerifierOutput | None,
    row: Mapping[str, Any],
    *,
    parse_errors: Sequence[str],
) -> dict[str, Any]:
    """Validate parsed output against the row-local first-verifier contract."""

    baseline_action = _baseline_action(row)
    proposed_rendered_label = _proposed_rendered_label(row)
    if parsed is None or parse_errors:
        return _decision(
            action="parse_error",
            baseline_action=baseline_action,
            action_valid=False,
            baseline_matches=False,
            citations_valid=False,
            first_experiment_label_policy_ok=False,
            component_owner_ok=False,
            source_row_index_ok=False,
            verifier_policy_ok=False,
            proposed_rendered_label_ok=False,
            cited_candidate_ids=[],
            cited_source_ids=[],
            issue_flags=[],
            rationale="",
            proposed_rendered_label=proposed_rendered_label,
            final_rendered_label=None,
            replacement_rendered_label=None,
        )
    component_owner_ok = parsed.component_owner == COMPONENT_OWNER
    source_row_index_ok = parsed.source_row_index == int(row["source_row_index"])
    verifier_policy_ok = bool(parsed.verifier_policy_id)
    baseline_matches = parsed.baseline_action == baseline_action
    action_valid = parsed.action in ALLOWED_ACTIONS
    citations_valid = _citations_valid(parsed, row)
    first_experiment_label_policy_ok = (
        parsed.final_rendered_label is None and parsed.replacement_rendered_label is None
    )
    proposed_rendered_label_ok = parsed.proposed_rendered_label == proposed_rendered_label
    return _decision(
        action=parsed.action if action_valid else "unsupported",
        baseline_action=baseline_action,
        action_valid=action_valid,
        baseline_matches=baseline_matches,
        citations_valid=citations_valid,
        first_experiment_label_policy_ok=first_experiment_label_policy_ok,
        component_owner_ok=component_owner_ok,
        source_row_index_ok=source_row_index_ok,
        verifier_policy_ok=verifier_policy_ok,
        proposed_rendered_label_ok=proposed_rendered_label_ok,
        cited_candidate_ids=list(parsed.cited_candidate_ids),
        cited_source_ids=list(parsed.cited_source_ids),
        issue_flags=list(parsed.issue_flags),
        rationale=parsed.rationale,
        proposed_rendered_label=parsed.proposed_rendered_label,
        final_rendered_label=parsed.final_rendered_label,
        replacement_rendered_label=parsed.replacement_rendered_label,
    )


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize a first-verifier run."""

    actions = Counter(str(row["verifier_decision"]["action"]) for row in rows)
    sections = Counter(str(row["report_section"]) for row in rows)
    changed = sum(bool(row["verifier_vs_baseline"]["action_changed"]) for row in rows)
    contract_ok = sum(bool(row["verifier_decision"]["contract_ok"]) for row in rows)
    citations_ok = sum(bool(row["verifier_decision"]["citations_valid"]) for row in rows)
    return {
        "policy_id": POLICY_ID,
        "row_count": len(rows),
        "action_counts": dict(sorted(actions.items())),
        "report_section_counts": dict(sorted(sections.items())),
        "changed_action_rows": changed,
        "contract_ok_rows": contract_ok,
        "contract_error_rows": len(rows) - contract_ok,
        "citations_valid_rows": citations_ok,
        "decision": _decision_label(actions, contract_ok, len(rows)),
    }


def _decision(
    *,
    action: str,
    baseline_action: str,
    action_valid: bool,
    baseline_matches: bool,
    citations_valid: bool,
    first_experiment_label_policy_ok: bool,
    component_owner_ok: bool,
    source_row_index_ok: bool,
    verifier_policy_ok: bool,
    proposed_rendered_label_ok: bool,
    cited_candidate_ids: list[str],
    cited_source_ids: list[str],
    issue_flags: list[str],
    rationale: str,
    proposed_rendered_label: str | None,
    final_rendered_label: str | None,
    replacement_rendered_label: str | None,
) -> dict[str, Any]:
    contract_ok = all(
        [
            action_valid,
            baseline_matches,
            citations_valid,
            first_experiment_label_policy_ok,
            component_owner_ok,
            source_row_index_ok,
            verifier_policy_ok,
            proposed_rendered_label_ok,
        ]
    )
    return {
        "action": action,
        "baseline_action": baseline_action,
        "contract_ok": contract_ok,
        "action_valid": action_valid,
        "baseline_matches": baseline_matches,
        "citations_valid": citations_valid,
        "first_experiment_label_policy_ok": first_experiment_label_policy_ok,
        "component_owner_ok": component_owner_ok,
        "source_row_index_ok": source_row_index_ok,
        "verifier_policy_ok": verifier_policy_ok,
        "proposed_rendered_label_ok": proposed_rendered_label_ok,
        "cited_candidate_ids": cited_candidate_ids,
        "cited_source_ids": cited_source_ids,
        "issue_flags": issue_flags,
        "rationale": rationale,
        "proposed_rendered_label": proposed_rendered_label,
        "final_rendered_label": final_rendered_label,
        "replacement_rendered_label": replacement_rendered_label,
    }


def _baseline_action(row: Mapping[str, Any]) -> str:
    return str(
        (((row.get("verifier_model_input") or {}).get("verification_case") or {}).get(
            "baseline_verification_decision_v0"
        ) or {}).get("action")
        or ""
    )


def _proposed_rendered_label(row: Mapping[str, Any]) -> str | None:
    return (
        (((row.get("verifier_model_input") or {}).get("verification_case") or {}).get(
            "baseline_verification_decision_v0"
        ) or {}).get("proposed_rendered_label")
    )


def _citations_valid(parsed: FirstVerifierOutput, row: Mapping[str, Any]) -> bool:
    model_input = dict(row.get("verifier_model_input") or {})
    verification_case = dict(model_input.get("verification_case") or {})
    candidate_packets = list(verification_case.get("candidate_evidence_packets") or [])
    allowed_candidate_ids = {
        str(packet.get("candidate_id"))
        for packet in candidate_packets
        if packet.get("candidate_id") is not None
    }
    allowed_source_ids = {
        str(source_id)
        for packet in candidate_packets
        for source_id in packet.get("source_ids") or []
        if source_id is not None
    }
    return (
        all(candidate_id in allowed_candidate_ids for candidate_id in parsed.cited_candidate_ids)
        and all(source_id in allowed_source_ids for source_id in parsed.cited_source_ids)
    )


def _decision_label(actions: Counter[str], contract_ok: int, row_count: int) -> str:
    if contract_ok != row_count:
        return "contract_failures_present"
    if actions["affirm"] or actions["reject"] or actions["human_review"]:
        return "action_surface_materialized"
    return "abstain_only_surface"


def _normalize_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    normalized = dict(payload)
    for key in [
        "action",
        "baseline_action",
        "component_owner",
        "schema_version",
        "verifier_policy_id",
        "action_basis",
        "rationale",
        "proposed_rendered_label",
        "final_rendered_label",
        "replacement_rendered_label",
    ]:
        value = normalized.get(key)
        if isinstance(value, list) and len(value) == 1:
            normalized[key] = value[0]
    for key in ["cited_candidate_ids", "cited_source_ids", "issue_flags"]:
        value = normalized.get(key)
        if isinstance(value, str):
            normalized[key] = [value]
    return normalized


def _extract_json_object(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, flags=re.DOTALL)
    if match:
        return match.group(1)
    first = stripped.find("{")
    last = stripped.rfind("}")
    if first >= 0 and last > first:
        return stripped[first : last + 1]
    raise ValueError("no JSON object found")
