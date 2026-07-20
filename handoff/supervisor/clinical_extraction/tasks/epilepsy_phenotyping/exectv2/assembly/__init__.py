"""Manifest-driven clinical finding assembly for ExECTv2."""

from __future__ import annotations

from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.clinical_finding import (
    ClinicalFinding,
    FindingSource,
    ProvenanceEvent,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.finding_store import (
    ClinicalFindingStore,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.manifests import (
    FindingAssemblyManifest,
    LensManifest,
    ProducerManifest,
    load_finding_assembly_manifest,
)

__all__ = [
    "AssemblyRun",
    "ClinicalFinding",
    "ClinicalFindingStore",
    "FindingAssemblyManifest",
    "FindingSource",
    "LensManifest",
    "ProducerManifest",
    "ProvenanceEvent",
    "build_finding_assembly",
    "load_finding_assembly_manifest",
    "render_finding_assembly_markdown",
]


def __getattr__(name: str) -> Any:
    """Load report-building assembly code only when its public API is requested."""

    if name in {
        "AssemblyRun",
        "build_finding_assembly",
        "render_finding_assembly_markdown",
    }:
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly import pipeline

        return getattr(pipeline, name)
    raise AttributeError(name)
