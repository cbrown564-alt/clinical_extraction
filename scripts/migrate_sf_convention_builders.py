#!/usr/bin/env python3
"""Generate rewrite/noise/residual builder modules from legacy cascade."""

from __future__ import annotations

import ast
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUILDERS = (
    REPO
    / "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic"
    / "sf_surface_registry/builders"
)
LEGACY = BUILDERS / "_legacy_impl.py"


def _source_segment(source: str, node: ast.AST) -> str:
    try:
        segment = ast.get_source_segment(source, node)
    except (TypeError, ValueError):
        segment = None
    if segment is None:
        lines = source.splitlines()
        segment = "\n".join(lines[node.lineno - 1 : getattr(node, "end_lineno", node.lineno)])
    return segment or ""


def _rule_id_from_if(source: str, node: ast.If) -> str | None:
    for child in ast.walk(node):
        if isinstance(child, ast.Return) and child.value is not None:
            for const in ast.walk(child.value):
                if isinstance(const, ast.Constant) and isinstance(const.value, str):
                    if const.value.startswith(("rewrite_", "drop_", "collapse_")):
                        return const.value
    return None


def _extract_rewrite_ifs(source: str) -> list[tuple[str, str, str]]:
    tree = ast.parse(source)
    fn = next(
        n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "sf_convention_rewrite"
    )
    blocks: list[tuple[str, str, str]] = []
    for node in fn.body:
        if not isinstance(node, ast.If):
            continue
        rule_id = _rule_id_from_if(source, node)
        if rule_id is None:
            continue
        cond = _source_segment(source, node.test).strip()
        body_parts = [_source_segment(source, stmt).strip() for stmt in node.body]
        body = "\n".join(body_parts)
        blocks.append((rule_id, cond, body))
    return blocks


def _fix_condition(cond: str, rule_id: str) -> tuple[str, list[str]]:
    """Return (condition, setup lines)."""
    setup: list[str] = []
    if rule_id == "rewrite_every_range_phrase_to_generic_seizures":
        setup.append("match = _SF_GENERIC_EVERY_RANGE_RE.search(surface)")
        return "match is not None", setup
    return cond, setup


def _write_rewrite_builders(source: str, blocks: list[tuple[str, str, str]]) -> None:
    lines = [
        '"""Catalog-backed rewrite builders."""',
        "",
        "from __future__ import annotations",
        "",
        "import re",
        "",
        "from .context import ConventionContext, RewriteResult",
        "from . import _legacy_impl as legacy",
        "from .registry import register_builder",
        "",
        "_SF_GENERIC_EVERY_RANGE_RE = legacy._SF_GENERIC_EVERY_RANGE_RE",
        "_SF_RISK_COUNSELLING_RE = legacy._SF_RISK_COUNSELLING_RE",
        "_REWRITE_THESE_SEIZURES_RE = legacy._REWRITE_THESE_SEIZURES_RE",
        "_REWRITE_UP_TO_RANGE_RE = legacy._REWRITE_UP_TO_RANGE_RE",
        "_SF_FTB_GENERIC_LAST_EVENT_RE = legacy._SF_FTB_GENERIC_LAST_EVENT_RE",
        "_SF_FTB_EVENTS_IN_TOTAL_LAST_EVENT_RE = legacy._SF_FTB_EVENTS_IN_TOTAL_LAST_EVENT_RE",
        "_SF_UP_TO_SEIZURE_FREE_RE = legacy._SF_UP_TO_SEIZURE_FREE_RE",
        "_SF_RECENT_LAST_SEIZURE_RE = legacy._SF_RECENT_LAST_SEIZURE_RE",
        "_SF_GTCS_ACTIVE_WITHOUT_COUNT_RE = legacy._SF_GTCS_ACTIVE_WITHOUT_COUNT_RE",
        "_SF_NO_FURTHER_GTC_SINCE_RE = legacy._SF_NO_FURTHER_GTC_SINCE_RE",
        "",
        "",
        '@register_builder("operand_format_rewrite")',
        "def operand_format_rewrite(ctx: ConventionContext) -> RewriteResult | None:",
        "    return legacy._sf_operand_format_rewrite(",
        "        ctx.text, surface=ctx.surface, attributes=ctx.attrs",
        "    )",
        "",
    ]
    for rule_id, cond, body in blocks:
        cond, setup = _fix_condition(cond, rule_id)
        fn_name = f"builder_{rule_id}"
        lines.extend(
            [
                "",
                f"@register_builder({rule_id!r})",
                f"def {fn_name}(ctx: ConventionContext) -> RewriteResult | None:",
            ]
        )
        lines.append("    attrs = dict(ctx.attrs)")
        lines.append("    text = ctx.text")
        lines.append("    evidence = ctx.evidence")
        lines.append("    phrase = ctx.phrase")
        lines.append("    surface = ctx.surface")
        for setup_line in setup:
            lines.append(f"    {setup_line}")
        lines.append(f"    if not ({cond}):")
        lines.append("        return None")
        for body_line in body.splitlines():
            lines.append(f"    {body_line}")
    (BUILDERS / "rewrite_builders.py").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote rewrite_builders.py ({len(blocks)} builders)")


def _extract_noise_ifs(source: str) -> list[tuple[str, str, str]]:
    tree = ast.parse(source)
    fn = next(
        n
        for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "is_sf_convention_noise"
    )
    blocks: list[tuple[str, str, str]] = []
    idx = 0
    for node in fn.body:
        if isinstance(node, ast.If):
            idx += 1
            cond = _source_segment(source, node.test).strip()
            body_parts = [_source_segment(source, stmt).strip() for stmt in node.body]
            body = "\n".join(body_parts)
            rule_id = f"noise_branch_{idx:02d}"
            blocks.append((rule_id, cond, body))
        elif isinstance(node, ast.Return):
            break
    return blocks


def _write_noise_builders(source: str, blocks: list[tuple[str, str, str]]) -> None:
    lines = [
        '"""Catalog-backed noise builders."""',
        "",
        "from __future__ import annotations",
        "",
        "import re",
        "",
        "from .context import ConventionContext",
        "from . import _legacy_impl as legacy",
        "from .registry import register_builder",
        "",
        "_SF_VAGUE_EPISODE_RE = legacy._SF_VAGUE_EPISODE_RE",
        "_SF_RISK_COUNSELLING_RE = legacy._SF_RISK_COUNSELLING_RE",
        "_SF_CONTEXTUAL_RATE_NOISE_RE = legacy._SF_CONTEXTUAL_RATE_NOISE_RE",
        "_SF_CONTEXTUAL_SEIZURE_FREE_RE = legacy._SF_CONTEXTUAL_SEIZURE_FREE_RE",
        "_SF_HISTORICAL_COMPARATOR_RE = legacy._SF_HISTORICAL_COMPARATOR_RE",
        "",
    ]
    for rule_id, cond, body in blocks:
        fn_name = f"builder_{rule_id}"
        lines.extend(
            [
                "",
                f"@register_builder({rule_id!r})",
                f"def {fn_name}(ctx: ConventionContext) -> bool:",
            ]
        )
        lines.append("    phrase = ctx.phrase")
        lines.append("    evidence = ctx.evidence")
        lines.append("    attrs = {str(k): str(v) for k, v in ctx.attrs.items()}")
        lines.append('    cui = attrs.get("CUI")')
        lines.append(f"    if ({cond}):")
        for body_line in body.splitlines():
            lines.append(f"        {body_line}")
        lines.append("    return False")
    (BUILDERS / "noise_builders.py").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote noise_builders.py ({len(blocks)} builders)")


def _residual_loop_names(source: str) -> list[tuple[str, str]]:
    """Heuristic: one builder wrapping each legacy helper loop block."""
    names: list[tuple[str, str]] = []
    for match in re.finditer(r"for match in (_SF_[A-Z0-9_]+)\.finditer", source):
        names.append((f"residual_{match.group(1).lower()}", match.group(1)))
    for match in re.finditer(r"match = (_SF_[A-Z0-9_]+)\.search", source):
        pat = match.group(1)
        if pat not in {n[1] for n in names}:
            names.append((f"residual_{pat.lower()}", pat))
    return names


def _write_residual_builders(source: str) -> None:
    # Residual uses monolithic legacy function registered as single builder for parity.
    lines = [
        '"""Catalog-backed residual-add builders."""',
        "",
        "from __future__ import annotations",
        "",
        "from .context import ResidualCandidate",
        "from . import _legacy_impl as legacy",
        "from .registry import register_builder",
        "",
        "",
        '@register_builder("residual_all_patterns")',
        "def residual_all_patterns(note_text: str) -> list[ResidualCandidate]:",
        "    return legacy.sf_residual_additions(note_text)",
        "",
    ]
    (BUILDERS / "residual_builders.py").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote residual_builders.py (monolithic residual builder)")


def main() -> None:

    source = LEGACY.read_text(encoding="utf-8")
    rewrite_blocks = _extract_rewrite_ifs(source)
    noise_blocks = _extract_noise_ifs(source)
    _write_rewrite_builders(source, rewrite_blocks)
    _write_noise_builders(source, noise_blocks)
    _write_residual_builders(source)


if __name__ == "__main__":
    main()
