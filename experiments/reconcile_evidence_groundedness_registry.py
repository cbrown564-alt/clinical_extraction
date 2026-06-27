"""Phase 3 replay recompute + registry annotation for evidence groundedness.

Usage:
    uv run python experiments/reconcile_evidence_groundedness_registry.py
"""

from __future__ import annotations

from clinical_extraction.core.evidence_validity_audit import write_reconciliation


def main() -> None:
    md_path, json_path, updated = write_reconciliation()
    print(f"Evidence validity audit JSON: {json_path}")
    print(f"Phase 3 reconciliation report: {md_path}")
    print(f"Registry rows annotated: {updated}")


if __name__ == "__main__":
    main()
