"""Dry-run registry-to-MLflow sync script.

This wrapper intentionally delegates to the package entry point so the behavior
is testable without requiring MLflow to be installed.
"""

from clinical_extraction.core.mlflow_sync_cli import main

if __name__ == "__main__":
    main()
