"""Agent-callable tool contracts for the ExECTv2 SeizureFrequency agentic
redo. See docs/experiments/exectv2/seizure_frequency/exectv2_sf_agentic_redo_predeclaration_2026-07-01.md.

A concept/CUI-lookup tool (the natural ExECTv2 analogue of nothing tested
in the Gan 2026 study) was considered and rejected: `deterministic/
concept_normalizer.py`'s InSampleConceptNormalizer is explicitly built from
gold annotations (a leaky dev-only stub per its own docstring), and
UmlsConceptNormalizer is unimplemented (raises NotImplementedError). Both
tools here are confirmed gold-free.
"""
from __future__ import annotations

from typing import Any

from clinical_extraction.core.evidence import evidence_is_substring, grade_evidence
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_sf_state_adjudicator import (
    _clinical_rules,
    _generic_seizure_policy,
    _seizure_free_anchor_guide,
    _state_decision_guide,
    _typed_candidate_guide,
    _unknown_change_recovery_lane,
)

# Re-exposes the existing v08 hybrid SF stage's clinical-decision prose
# (already reviewed, already in production) as named, queryable guides --
# adaptation of already-written clinical content, not new clinical
# judgment authored for this redo.
_GUIDES: dict[str, Any] = {
    "clinical_rules": _clinical_rules,
    "generic_seizure_policy": _generic_seizure_policy,
    "seizure_free_anchor_guide": _seizure_free_anchor_guide,
    "typed_candidate_guide": _typed_candidate_guide,
    "unknown_change_recovery_lane": _unknown_change_recovery_lane,
    "state_decision_guide": _state_decision_guide,
}

_GUIDE_ALIASES = {
    "rules": "clinical_rules",
    "general rules": "clinical_rules",
    "keep reject policy": "generic_seizure_policy",
    "active rate vs seizure free vs unknown": "generic_seizure_policy",
    "seizure free": "seizure_free_anchor_guide",
    "seizure free duration": "seizure_free_anchor_guide",
    "candidate types": "typed_candidate_guide",
    "candidate kinds": "typed_candidate_guide",
    "unknown": "unknown_change_recovery_lane",
    "changed": "unknown_change_recovery_lane",
    "frequency change": "unknown_change_recovery_lane",
    "state decision": "state_decision_guide",
    "final state": "state_decision_guide",
}


def _normalize_key(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", " ").replace("-", " ").split())


def read_sf_boundary_guide(query: str) -> dict[str, Any]:
    """Look up SeizureFrequency clinical boundary guidance by ID or a
    trigger phrase (e.g. "seizure free", "frequency change", "candidate
    kinds", "keep reject policy"). Raises if the query does not match a
    known guide; retry with a different query or a guide ID from the error
    message."""
    normalized = _normalize_key(query)
    guide_id = normalized if normalized in _GUIDES else _GUIDE_ALIASES.get(normalized)
    if guide_id is None:
        guide_id = next(
            (gid for gid in _GUIDES if normalized in gid.replace("_", " ")), None
        )
    if guide_id is None:
        available = ", ".join(sorted(_GUIDES))
        raise KeyError(f"Unknown SF boundary guide: {query!r}. Available guides: {available}")
    content = _GUIDES[guide_id]()
    return {
        "tool_name": "read_sf_boundary_guide",
        "guide_id": guide_id,
        "content": content,
    }


def bound_evidence_check_tool(note_text: str):
    """Build an evidence-verification tool bound to one letter's text.

    Returns a callable taking a candidate evidence string and reporting
    whether/how it is grounded in this letter -- gold-free (uses only the
    letter text and the candidate string, never touches annotations)."""

    def check_evidence_in_letter(evidence_text: str) -> dict[str, Any]:
        """Check whether a candidate evidence quote is actually present in
        the current letter, and how exactly (exact match, or a specific
        repaired-artifact/case/whitespace/ellipsis/section variant)."""
        grade = grade_evidence(note_text, evidence_text)
        return {
            "tool_name": "check_evidence_in_letter",
            "evidence_text": evidence_text,
            "grade": str(grade),
            "is_exact": evidence_is_substring(note_text, evidence_text),
        }

    return check_evidence_in_letter
