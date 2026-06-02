"""Compatibility wrapper for Gan 2026 boundary-state graph artifact replay."""

from ..artifact_analysis.boundary_state_graph_replay import *  # noqa: F403
from ..artifact_analysis.boundary_state_graph_replay import main

if __name__ == "__main__":
    main()
