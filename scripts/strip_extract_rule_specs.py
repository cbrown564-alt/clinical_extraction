#!/usr/bin/env python3
"""Strip RuleSpec metadata from rule modules; add EXTRACT_IMPLS registries."""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = (
    REPO_ROOT
    / "src"
    / "clinical_extraction"
    / "tasks"
    / "epilepsy_phenotyping"
    / "exectv2"
    / "deterministic"
    / "rules"
)

_RULE_SPEC_RE = re.compile(
    r"^[A-Z][A-Z0-9_]*_RULE\s*=\s*RuleSpec\(",
    re.MULTILINE,
)
_LIST_RE = re.compile(
    r"\n# -+\n# Ordered rule list.*\n[A-Z_]+_RULES:.*\Z",
    re.DOTALL,
)

_MODULES = {
    "anchor.py": ("ANCHOR_EXTRACT_IMPLS", "ANCHOR_RULES"),
    "change.py": ("CHANGE_EXTRACT_IMPLS", "CHANGE_RULES"),
    "seizure_free.py": ("SEIZURE_FREE_EXTRACT_IMPLS", "SEIZURE_FREE_RULES"),
    "temporal.py": ("TEMPORAL_EXTRACT_IMPLS", "TEMPORAL_RULES"),
}


def _strip_rule_specs(source: str) -> str:
    lines = source.splitlines(keepends=True)
    out: list[str] = []
    skipping = False
    for line in lines:
        if not skipping and _RULE_SPEC_RE.match(line.rstrip("\n")):
            skipping = True
            continue
        if skipping:
            if line.rstrip("\n") == ")":
                skipping = False
            continue
        out.append(line)
    body = "".join(out)
    body = _LIST_RE.sub("", body)
    body = re.sub(
        r"\n[A-Z_]+_RULES: list\[RuleSpec\] = \[[\s\S]*?\]\n",
        "\n",
        body,
        count=1,
    )
    return body.rstrip() + "\n"


from extract_migration_utils import impl_registry_lines


def _impl_block(module_name: str, dict_name: str, list_name: str) -> str:
    import importlib

    mod = importlib.import_module(
        f"clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.{module_name}"
    )
    specs = getattr(mod, list_name)
    return "\n".join(impl_registry_lines(dict_name=dict_name, specs=specs))


def _update_imports(body: str) -> str:
    body = body.replace(
        "from ..rule_metadata import (\n    ExtractionContext,\n    Portability,\n    RuleExample,\n    RuleGroup,\n    RuleSpec,\n)",
        "from ..rule_metadata import (\n    ExtractionContext,\n    Portability,\n    RuleGroup,\n)",
    )
    body = body.replace(
        "from ..rule_metadata import (\n    ExtractionContext,\n    Portability,\n    RuleExample,\n    RuleGroup,\n    RuleSpec,\n)",
        "from ..rule_metadata import (\n    ExtractionContext,\n    Portability,\n    RuleGroup,\n)",
    )
    return body


def main() -> None:
    for filename, (dict_name, list_name) in _MODULES.items():
        path = RULES_DIR / filename
        source = path.read_text(encoding="utf-8")
        body = _strip_rule_specs(source)
        body = _update_imports(body)
        note = textwrap.dedent(
            """
            # RuleSpec metadata: sf_surface_registry/catalog/extract.yaml
            # Assembled via sf_surface_registry/adapters/extraction.py
            """
        )
        out = body.rstrip() + note + _impl_block(Path(filename).stem, dict_name, list_name)
        path.write_text(out, encoding="utf-8")
        print(f"updated {path.name} ({len(out.splitlines())} lines)")


if __name__ == "__main__":
    main()
