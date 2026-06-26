#!/usr/bin/env python3
"""Build rate_builders.py and EXTRACT_IMPLS from live rate.py RuleSpecs."""

from __future__ import annotations

import ast
import inspect
import re
import textwrap
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules import rate as rate_mod

REPO_ROOT = Path(__file__).resolve().parent.parent
RATE_PATH = (
    REPO_ROOT
    / "src"
    / "clinical_extraction"
    / "tasks"
    / "epilepsy_phenotyping"
    / "exectv2"
    / "deterministic"
    / "rules"
    / "rate.py"
)
BUILDERS_PATH = RATE_PATH.with_name("rate_builders.py")

_RULE_SPEC_RE = re.compile(
    r"^[A-Z][A-Z0-9_]*_RULE\s*=\s*RuleSpec\(",
    re.MULTILINE,
)
_RATE_RULES_RE = re.compile(
    r"\n# -+\n# Ordered rule list.*\nRATE_RULES:.*\Z",
    re.DOTALL,
)


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
    body = _RATE_RULES_RE.sub("", body)
    return body.rstrip() + "\n"


from extract_migration_utils import impl_registry_lines


def _impl_registry_block() -> str:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.rate import (
        RATE_RULES,
    )

    return "\n".join(impl_registry_lines(dict_name="RATE_EXTRACT_IMPLS", specs=RATE_RULES))


def main() -> None:
    source = RATE_PATH.read_text(encoding="utf-8")
    header = textwrap.dedent(
        '''\
        """Rate-expression builders and patterns for ExECTv2 (Stack A).

        RuleSpec metadata lives in ``sf_surface_registry/catalog/extract.yaml``.
        ``adapters/extraction.py`` assembles ``RATE_RULES`` from catalog + this module.
        """
        '''
    )
    body = _strip_rule_specs(source)
    body = body.replace(
        '"""Seizure-frequency rate extraction rules for ExECTv2 (Stack A).\n\nCovers:',
        '"""PLACEHOLDER',
        1,
    )
    # Remove old module docstring (first triple-quoted block)
    body = re.sub(r'^""".*?"""\n', "", body, count=1, flags=re.DOTALL)
    body = body.replace(
        "from ..rule_metadata import (\n    ExtractionContext,\n    Portability,\n    RuleExample,\n    RuleGroup,\n    RuleSpec,\n)",
        "from ..rule_metadata import (\n    ExtractionContext,\n    Portability,\n    RuleGroup,\n)",
        1,
    )
    out = header + body + _impl_registry_block()
    BUILDERS_PATH.write_text(out, encoding="utf-8")
    print(f"wrote {BUILDERS_PATH} ({len(out.splitlines())} lines)")


if __name__ == "__main__":
    main()
