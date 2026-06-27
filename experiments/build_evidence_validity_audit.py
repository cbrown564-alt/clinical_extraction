"""Build the Phase 0 evidence-validity taxonomy audit (replay-only, no model calls).

Usage:
    uv run python experiments/build_evidence_validity_audit.py
"""

from __future__ import annotations

from clinical_extraction.core.evidence_validity_audit import write_report


def main() -> None:
    json_path, md_path = write_report()
    print(f"Evidence validity audit JSON: {json_path}")
    print(f"Evidence validity audit report: {md_path}")


if __name__ == "__main__":
    main()
