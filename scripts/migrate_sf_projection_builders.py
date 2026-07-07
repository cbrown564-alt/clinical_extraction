#!/usr/bin/env python3
"""Move Stack C SF projection implementations into sf_surface_registry/builders/."""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TP = (
    REPO
    / "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/target_projection"
)
BUILDERS = (
    REPO
    / "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/sf_surface_registry/builders"
)
_PREFIX = "clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.target_projection"

_MOVES: dict[str, str] = {
    "sf_state.py": "projection_sf_state.py",
    "evidence_repair.py": "projection_evidence_repair.py",
    "cross_entity.py": "projection_cross_entity.py",
}

_RELATIVE_IMPORTS = {
    ".constants": f"{_PREFIX}.constants",
    ".policy": f"{_PREFIX}.policy",
    ".shared": f"{_PREFIX}.shared",
    ".types": f"{_PREFIX}.types",
}


def _rewrite_imports(source: str) -> str:
    for relative, absolute in _RELATIVE_IMPORTS.items():
        source = source.replace(f"from {relative} import", f"from {absolute} import")
    return source


def _facade(module: str, builder_module: str, names: list[str]) -> str:
    imports = ",\n    ".join(names)
    return f'''"""Stack C facade — implementation in ``sf_surface_registry/builders/{builder_module}``."""
from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.builders.{builder_module} import (
    {imports},
)

__all__ = [
    {", ".join(repr(name) for name in names)},
]
'''


def _public_names(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    names: list[str] = []
    for match in re.finditer(r"^def ([a-z_][a-z0-9_]*)", source, re.MULTILINE):
        names.append(match.group(1))
    if (path.name == "cross_entity.py") and "remote_last_seizures_evidence" not in names:
        names.extend(
            [
                "controlled_focal_seizures_evidence",
                "frequent_myoclonic_jerks_evidence",
                "remote_last_seizures_evidence",
            ]
        )
    return sorted(set(names))


def main() -> None:
    BUILDERS.mkdir(parents=True, exist_ok=True)
    for src_name, dst_name in _MOVES.items():
        src = TP / src_name
        dst = BUILDERS / dst_name
        body = _rewrite_imports(src.read_text(encoding="utf-8"))
        header = f'"""SF projection builders migrated from ``target_projection/{src_name}``."""\n'
        if not body.lstrip().startswith('"""'):
            body = header + body
        else:
            body = re.sub(r'^"""[\s\S]*?"""', header.rstrip(), body, count=1)
        dst.write_text(body, encoding="utf-8")
        names = _public_names(src)
        (TP / src_name).write_text(
            _facade(src_name.replace(".py", ""), dst_name.replace(".py", ""), names),
            encoding="utf-8",
        )
        print(f"migrated {src_name} -> builders/{dst_name} ({len(names)} exports)")


if __name__ == "__main__":
    main()
