"""Shadow diff runner: legacy Stack B vs registry convention adapter."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from ..adapters.convention import apply_rewrite


@dataclass(frozen=True)
class RewriteCase:
    name: str
    text: str
    evidence: str
    attributes: Mapping[str, Any]
    expected_rule: str | None = None
    expected_rule_contains: str | None = None


@dataclass(frozen=True)
class ShadowDiff:
    case_name: str
    legacy: tuple[str, dict[str, Any], str] | None
    registry: tuple[str, dict[str, Any], str] | None

    @property
    def matches(self) -> bool:
        return self.legacy == self.registry


def compare_rewrite_outputs(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> ShadowDiff:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.standard_dictionary import (
        sf_convention_rewrite as legacy_sf_convention_rewrite,
    )

    legacy_result = legacy_sf_convention_rewrite(
        text, evidence=evidence, attributes=attributes
    )
    registry_result = apply_rewrite(text, evidence=evidence, attributes=attributes)
    return ShadowDiff(
        case_name="inline",
        legacy=legacy_result,
        registry=registry_result,
    )


def run_shadow_diff(cases: Sequence[RewriteCase]) -> list[ShadowDiff]:
    diffs: list[ShadowDiff] = []
    for case in cases:
        diff = compare_rewrite_outputs(
            case.text,
            evidence=case.evidence,
            attributes=case.attributes,
        )
        diffs.append(
            ShadowDiff(
                case_name=case.name,
                legacy=diff.legacy,
                registry=diff.registry,
            )
        )
    return diffs


def format_diff_ledger(diffs: Sequence[ShadowDiff]) -> str:
    mismatches = [diff for diff in diffs if not diff.matches]
    if not mismatches:
        return f"shadow diff: OK ({len(diffs)} cases)"
    lines = [f"shadow diff: {len(mismatches)} mismatch(es)"]
    for diff in mismatches:
        lines.append(f"- {diff.case_name}: legacy={diff.legacy!r} registry={diff.registry!r}")
    return "\n".join(lines)
