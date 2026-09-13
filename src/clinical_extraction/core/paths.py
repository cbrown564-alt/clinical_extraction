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


def resolve_letter_benchmarks_root(*, root: Path | None = None) -> Path:
    """Return the canonical results location for current readers and writers.

    Historical artifact paths remain readable through resolve_saved_artifact_path.
    Never select a different write destination based on directory existence.
    """
    repo = root or discover_repo_root_or_cwd()
    return repo / "results/letter-benchmarks"


def resolve_saved_artifact_path(root: Path, recorded_path: str | Path) -> Path:
    """Resolve an old result path without rewriting immutable saved provenance.

    Only the exact historical root component is remapped. This is a reader
    adapter; current writers always use resolve_letter_benchmarks_root.
    """
    path = Path(recorded_path)
    if path.is_absolute():
        try:
            relative = path.relative_to(root)
        except ValueError:
            return path
    else:
        relative = path
    if relative.parts and relative.parts[0] == "paper_experiments":
        return root / "results" / "letter-benchmarks" / Path(*relative.parts[1:])
    return root / relative
