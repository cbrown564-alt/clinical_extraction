"""Convert section-claim-table rows into normalized atomic-claim node dicts.

Stage B of the KG-grounded component-generation design note (2026-06-15) feeds the
LLM atomic-claim graph to the ontology dual-validation + ``resolve_label`` query.
For the C2 over-inference guard to be *exercised*, the atomic claims must commit a
quantified state wherever the source-near evidence warrants one - i.e. each
claim's ``raw_frequency`` must be normalized into a Gan-compatible label rather
than dropped. (The 2026-06-02 conversion dropped ``raw_frequency`` and minted
every node as ``unknown``, leaving the guard with nothing to police.)

This module does exactly that normalization, using the project's existing
scorer-facing label grammar via ``repair_prediction_label`` - the allowed
"source-near to Gan-compatible label conversion" of design-note section 4. It does
*not* perform diary/window arithmetic reconstruction (the disallowed step): plain
``repair_prediction_label`` is used, never the evidence-window variant, so a node's
state comes only from its own ``raw_frequency`` expression and its claim type.
"""

from __future__ import annotations

from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label,
)

# rule_id stamped on nodes minted from a normalized v3 claim, so attribution
# audits can tell a raw_frequency-normalized mint apart from the older label-less
# ``llm.atomic_claim`` conversion.
NORMALIZED_CLAIM_RULE_ID = "llm.atomic_claim.v3_raw_frequency_normalized"


def atomic_claim_from_table_claim(claim: dict[str, Any]) -> dict[str, Any]:
    """Map one section-claim-table claim to a normalized atomic-claim dict.

    The returned dict is the input shape expected by
    ``build_state_graph_from_atomic_claims``: its ``normalized_label`` is the
    Gan-grammar repair of the claim's ``raw_frequency`` (or ``None`` when the claim
    carries no frequency expression, leaving the builder's kind-based fallback to
    decide ``unknown`` / ``no_reference``). The node *kind* still comes from the
    claim type, so an evidence shape such as ``last_event_only`` is preserved for
    the ontology guard even when the raw frequency parses to a rate.
    """

    raw_frequency = claim.get("raw_frequency")
    raw_frequency = str(raw_frequency).strip() if raw_frequency else ""
    normalized_label = repair_prediction_label(raw_frequency) if raw_frequency else None
    return {
        "kind": claim.get("claim_type"),
        "evidence": claim.get("evidence") or "",
        "assertion_status": claim.get("assertion_status") or "unknown",
        "temporality": claim.get("temporality") or "unclear",
        "applies_to": claim.get("semiology"),
        "normalized_label": normalized_label,
        "rule_id": NORMALIZED_CLAIM_RULE_ID,
        "raw_frequency": raw_frequency or None,
    }


def atomic_claims_from_structured_record(
    structured_record: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Normalize every claim in a claim-table row's ``structured_record``."""

    claims = (structured_record or {}).get("claims") or []
    return [atomic_claim_from_table_claim(claim) for claim in claims]
