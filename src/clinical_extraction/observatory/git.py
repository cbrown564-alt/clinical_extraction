"""Git metadata helpers for Observatory routes."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def git_metadata(repo_root: Path) -> dict[str, Any]:
    def _run(cmd: list[str]) -> str:
        try:
            result = subprocess.run(
                cmd,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            return ""

    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    commit = _run(["git", "rev-parse", "HEAD"])
    dirty = _run(["git", "status", "--porcelain"]) != ""
    remote = _run(["git", "remote", "get-url", "origin"])

    return {
        "branch": branch or None,
        "commit": commit or None,
        "dirty": dirty,
        "remote_url": remote or None,
    }
