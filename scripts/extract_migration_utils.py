#!/usr/bin/env python3
"""Helpers for Phase 4 extract-rule migration scripts."""

from __future__ import annotations

import re
from re import Pattern


def pattern_source(pattern: Pattern[str]) -> str:
    flag_names: list[str] = []
    for bit, name in (
        (re.IGNORECASE, "re.IGNORECASE"),
        (re.MULTILINE, "re.MULTILINE"),
        (re.DOTALL, "re.DOTALL"),
    ):
        if pattern.flags & bit:
            flag_names.append(name)
    if flag_names:
        flags = " | ".join(flag_names)
        return f"re.compile({pattern.pattern!r}, {flags})"
    return f"re.compile({pattern.pattern!r})"


def impl_registry_lines(*, dict_name: str, specs) -> list[str]:
    lines = [
        "",
        "from .extract_impl_types import ExtractRuleImpl",
        "",
        f"{dict_name}: dict[str, ExtractRuleImpl] = {{",
    ]
    for spec in specs:
        exclude = ", ".join(f.__name__ for f in spec.exclude)
        exclude_part = f", exclude=({exclude},)" if exclude else ""
        pat = pattern_source(spec.pattern)
        lines.append(
            f"    {spec.rule_id!r}: ExtractRuleImpl("
            f"{pat}, {spec.build.__name__}{exclude_part}),"
        )
    lines.append("}")
    lines.append("")
    return lines
