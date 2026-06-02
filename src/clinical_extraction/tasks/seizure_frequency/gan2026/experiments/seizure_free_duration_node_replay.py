"""Compatibility wrapper for Gan 2026 duration-node artifact replay."""

from ..artifact_analysis.seizure_free_duration_node_replay import *  # noqa: F403
from ..artifact_analysis.seizure_free_duration_node_replay import main

if __name__ == "__main__":
    main()
