#!/usr/bin/env python3
"""P1-1 gate: replay dev140 v09 assembly and compare to frozen baseline scores."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = (
    REPO
    / "configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140.yaml"
)
FROZEN_SUMMARY = (
    REPO
    / "experiments/_archive/exectv2_richschema_iterations"
    / "exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140_20260621.json"
)
STRUCTURED_V09_ARCHIVE = (
    REPO
    / "experiments/_archive/exectv2_richschema_iterations"
    / "exectv2_llm_only_key_entities_structured_v09_dev140_gpt41mini_20260621.jsonl"
)

FROZEN_BASELINE = {
    "seizure_frequency_headline_f1": 0.9053,
    "seizure_frequency_active_rate_fidelity_f1": 0.5969,
}
_TOLERANCE = 1e-4


def _load_frozen() -> dict[str, float]:
    summary = json.loads(FROZEN_SUMMARY.read_text(encoding="utf-8"))
    ladder = summary["score_ladder"]
    return {
        "seizure_frequency_headline_f1": ladder["headline_target"]["by_indicator"][
            "SeizureFrequency"
        ]["f1"],
        "seizure_frequency_active_rate_fidelity_f1": ladder["fidelity_companions"][
            "SeizureFrequency"
        ]["active_rate_fidelity"]["f1"],
    }


def _replay_current() -> dict[str, float]:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.manifests import (
        load_finding_assembly_manifest,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
        build_finding_assembly,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
        all_entities as _all_entities,  # noqa: F401 — prime imports
    )

    manifest = load_finding_assembly_manifest(MANIFEST)
    structured = manifest.producers["key_entities_structured_v09"]
    if not structured.artifact.exists() and STRUCTURED_V09_ARCHIVE.exists():
        structured = structured.__class__(
            **{**structured.__dict__, "artifact": STRUCTURED_V09_ARCHIVE.relative_to(REPO)}
        )
        manifest = manifest.__class__(
            **{
                **manifest.__dict__,
                "producers": {
                    **manifest.producers,
                    "key_entities_structured_v09": structured,
                },
            }
        )
    run = build_finding_assembly(manifest, generated_on="2026-06-26")
    ladder = run.report["score_ladder"]
    return {
        "seizure_frequency_headline_f1": ladder["headline_target"]["by_indicator"][
            "SeizureFrequency"
        ]["f1"],
        "seizure_frequency_active_rate_fidelity_f1": ladder["fidelity_companions"][
            "SeizureFrequency"
        ]["active_rate_fidelity"]["f1"],
    }


def main() -> int:
    if not FROZEN_SUMMARY.exists():
        print(f"missing frozen summary: {FROZEN_SUMMARY}", file=sys.stderr)
        return 1
    frozen = _load_frozen()
    for key, expected in FROZEN_BASELINE.items():
        if abs(frozen[key] - expected) > _TOLERANCE:
            print(f"frozen summary drift: {key}={frozen[key]} expected {expected}", file=sys.stderr)
            return 1
    current = _replay_current()
    failed = False
    for key, expected in FROZEN_BASELINE.items():
        actual = current[key]
        delta = actual - expected
        status = "OK" if abs(delta) <= _TOLERANCE else "FAIL"
        print(f"{status} {key}: {actual:.4f} (delta {delta:+.4f})")
        if status == "FAIL":
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
