"""Atomic multi-artifact writers for ExECTv2 runners."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Any


@contextmanager
def atomic_artifact_bundle(*targets: Path) -> Iterator[dict[Path, Path]]:
    """Stage writes beside final paths, then commit with ``os.replace``.

    Yields a mapping from each resolved target path to its staging path. All
    staging writes must succeed before any final path is replaced. On failure,
    staged temp files are removed and existing artifacts are left untouched.
    """

    resolved = [path.resolve() for path in targets]
    staged: list[tuple[Path, str]] = []
    staging: dict[Path, Path] = {}
    try:
        for target in resolved:
            target.parent.mkdir(parents=True, exist_ok=True)
            _fd, tmp_path = tempfile.mkstemp(
                dir=target.parent,
                prefix=f".{target.name}.",
                suffix=".tmp",
            )
            os.close(_fd)
            staged.append((target, tmp_path))
            staging[target] = Path(tmp_path)
        yield staging
        for target, tmp_path in staged:
            os.replace(tmp_path, target)
        staged.clear()
    finally:
        for _, tmp_path in staged:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


def write_artifact_bundle(
    artifacts: Mapping[Path, str | bytes],
    *,
    encoding: str = "utf-8",
) -> dict[Path, Path]:
    """Write multiple text or binary artifacts atomically."""

    if not artifacts:
        return {}

    normalized: dict[Path, str | bytes] = {
        path.resolve(): content for path, content in artifacts.items()
    }
    with atomic_artifact_bundle(*normalized.keys()) as staging:
        for target, content in normalized.items():
            stage_path = staging[target]
            if isinstance(content, bytes):
                stage_path.write_bytes(content)
            else:
                stage_path.write_text(content, encoding=encoding)
    return {target: target for target in normalized}


def commit_artifact_bundle(
    targets: Sequence[Path],
    writer: Callable[[Mapping[Path, Path]], Any],
) -> Any:
    """Run ``writer`` against staging paths, then atomically publish all targets."""

    with atomic_artifact_bundle(*targets) as staging:
        result = writer(staging)
    return result
