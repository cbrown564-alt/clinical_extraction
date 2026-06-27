"""Per-architecture Gan 2026 pipeline runner modules.

Pure relocation of ``runner.py`` into cohesive submodules. The legacy module
path remains a thin facade re-exporting this API.
"""

from clinical_extraction.tasks.seizure_frequency.gan2026.runners import (
    deterministic,
    deterministic_canonical,
    hybrid,
    hybrid_structured_events,
    llm_only_canonical,
    llm_only_direct_labeler,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.artifact import (
    build_unified_pipeline_artifact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.cli_specs import (
    get_cli_specs,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    ARCHITECTURE_FAMILY,
    PipelineArchitecture,
    PipelineConfiguration,
    PipelineOutputArtifact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.reports import (
    write_deterministic_report,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.split import run_split

__all__ = [
    "ARCHITECTURE_FAMILY",
    "PipelineArchitecture",
    "PipelineConfiguration",
    "PipelineOutputArtifact",
    "build_unified_pipeline_artifact",
    "deterministic",
    "deterministic_canonical",
    "get_cli_specs",
    "hybrid",
    "hybrid_structured_events",
    "llm_only_canonical",
    "llm_only_direct_labeler",
    "run_split",
    "write_deterministic_report",
]
