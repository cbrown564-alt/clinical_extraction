"""Artifact I/O helpers for cross-model reliability analysis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.types import ReliabilityRun

def find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[6]


REPO_ROOT = find_repo_root()


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def run_ref(run: ReliabilityRun) -> dict[str, str]:
    out = {
        "candidate": run.candidate,
        "model_label": run.model_label,
        "rows_path": run.rows_path.as_posix(),
        "role": run.role,
        "claim_boundary": run.claim_boundary,
    }
    if run.summary_path is not None:
        out["summary_path"] = run.summary_path.as_posix()
    return out
