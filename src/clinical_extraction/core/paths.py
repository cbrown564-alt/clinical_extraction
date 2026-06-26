"""Repository path discovery and resolution utilities."""

from __future__ import annotations

from pathlib import Path


def discover_repo_root(
    *,
    start: Path | None = None,
    require_src: bool = False,
    include_cwd: bool = True,
) -> Path:
    """Locate the repository root by walking upward from anchor paths."""
    candidates: list[Path] = []
    if include_cwd:
        candidates.extend([Path.cwd(), *Path.cwd().parents])
    anchor = (start or Path(__file__)).resolve()
    candidates.extend([anchor, *anchor.parents])

    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if not (resolved / "pyproject.toml").exists():
            continue
        if require_src and not (resolved / "src").exists():
            continue
        return resolved
    raise RuntimeError("Could not locate repository root")


def discover_repo_root_or_cwd(
    *,
    start: Path | None = None,
    require_src: bool = False,
    include_cwd: bool = True,
) -> Path:
    """Like discover_repo_root, but fall back to cwd when no root is found."""
    try:
        return discover_repo_root(
            start=start,
            require_src=require_src,
            include_cwd=include_cwd,
        )
    except RuntimeError:
        return Path.cwd()


def resolve_under_root(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path
