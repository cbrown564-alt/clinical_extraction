"""Explanatory architecture layer.

This package holds the authoritative stage manifests for the six selected
task-method pairs, plus the generators that turn those manifests into
diagrams and teaching traces.

It owns *explanation*, never prediction. Nothing here may be imported by a
prediction-bearing pipeline, and nothing here changes a score.
"""

from clinical_extraction.architecture.stage_manifest import (
    EFFECT_CLASSES,
    METHOD_IDS,
    OWNERS,
    MethodManifest,
    Stage,
    load_manifest,
    load_manifests,
    validate_all,
    validate_manifest,
)

__all__ = [
    "EFFECT_CLASSES",
    "METHOD_IDS",
    "OWNERS",
    "MethodManifest",
    "Stage",
    "load_manifest",
    "load_manifests",
    "validate_manifest",
    "validate_all",
]
