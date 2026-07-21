"""Package, prompt, schema, and rule identifiers written to every run."""

from __future__ import annotations

import hashlib
from pathlib import Path

PACKAGE_VERSION = "0.1.0"
FINDINGS_PROMPT_VERSION = "exectv2_hybrid_key_family_event_ledger_v0.9.24"
FINDINGS_RULE_SET_VERSION = "decision_0040_joint_bounded_dev140_v1"
FREQUENCY_PROMPT_VERSION = "gan2026_hybrid_structured_events_v0.5"
FREQUENCY_RULE_SET_VERSION = "gan2026_v05_selected_repair_default"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def version_record() -> dict[str, object]:
    package_root = Path(__file__).resolve().parent
    assets = {
        "seizure_frequency_prompt": package_root / "seizure_frequency" / "prompt.md",
        "seizure_frequency_schema": package_root / "seizure_frequency" / "schema.json",
        "clinical_findings_prompt": package_root / "clinical_findings" / "prompt.md",
        "clinical_findings_schema": package_root / "clinical_findings" / "schema.json",
    }
    return {
        "package_version": PACKAGE_VERSION,
        "prompt_versions": {
            "seizure_frequency": FREQUENCY_PROMPT_VERSION,
            "clinical_findings": FINDINGS_PROMPT_VERSION,
        },
        "rule_set_versions": {
            "seizure_frequency": FREQUENCY_RULE_SET_VERSION,
            "clinical_findings": FINDINGS_RULE_SET_VERSION,
        },
        "asset_sha256": {name: _sha256(path) for name, path in assets.items()},
    }
