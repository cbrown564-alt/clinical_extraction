#!/usr/bin/env python3
"""Apply Phase 4 extraction alignment in one atomic pass."""

from __future__ import annotations

import re
import subprocess
import sys
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RULES = REPO / "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/rules"
REGISTRY = REPO / "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/sf_surface_registry"


def _write_support_files() -> None:
    (RULES / "extract_impl_types.py").write_text(
        textwrap.dedent(
            '''\
            """Shared types for Stack A extract rule implementations."""
            from __future__ import annotations

            from dataclasses import dataclass
            from re import Pattern

            from ..rule_metadata import ExclusionPredicate, RuleBuilder


            @dataclass(frozen=True)
            class ExtractRuleImpl:
                pattern: Pattern[str]
                build: RuleBuilder
                exclude: tuple[ExclusionPredicate, ...] = ()
            '''
        ),
        encoding="utf-8",
    )
    (RULES / "extract_reexports.py").write_text(
        Path(__file__).with_name("extract_reexports.py").read_text(encoding="utf-8")
        if Path(__file__).with_name("extract_reexports.py").exists()
        else "",
        encoding="utf-8",
    )
    # embed reexports inline below if missing
    reexports = RULES / "extract_reexports.py"
    if reexports.stat().st_size == 0:
        reexports.write_text(
            textwrap.dedent(
                '''\
                """Lazy re-exports of assembled RuleSpec objects for backward-compatible imports."""
                from __future__ import annotations

                import importlib
                from typing import Any

                _LIST_NAMES = frozenset({
                    "ANCHOR_RULES", "CHANGE_RULES", "RATE_RULES", "SEIZURE_FREE_RULES", "TEMPORAL_RULES",
                })
                _NAMED_RULE_IDS = {
                    "SEIZURE_TYPE_ANCHOR_RULE": "anchor.seizure_type_phrase",
                    "SEIZURE_FREE_ANCHOR_RULE": "anchor.seizure_free_phrase",
                    "ADVERBIAL_RULE": "rate.adverbial",
                    "ARTICLE_SEIZURE_COUNT_RULE": "rate.article_seizure_count",
                    "BETWEEN_RANGE_PER_PERIOD_RULE": "rate.between_range_per_period",
                    "COUNT_IN_LAST_PERIOD_RULE": "rate.count_in_last_period",
                    "COUNT_PER_FORTNIGHT_RULE": "rate.count_per_fortnight",
                    "COUNT_PER_PERIOD_RULE": "rate.count_per_period",
                    "EVERY_N_PERIODS_RULE": "rate.every_n_periods",
                    "EVERY_PERIOD_RULE": "rate.every_period",
                    "HEADER_CONTINUATION_RATE_RULE": "rate.header_continuation_rate",
                    "N_TIMES_PER_PERIOD_RULE": "rate.n_times_per_period",
                    "PERIOD_RANGE_RULE": "rate.period_range",
                    "RANGE_EVERY_PERIOD_RULE": "rate.range_every_period",
                    "RANGE_OF_SEIZURE_TERMS_RULE": "rate.range_of_seizure_terms",
                    "RANGE_OVER_PERIOD_RULE": "rate.range_over_period",
                    "RANGE_PER_PERIOD_RULE": "rate.range_per_period",
                    "SEVERAL_TIMES_PER_PERIOD_RULE": "rate.several_times_per_period",
                    "CONTROL_PHRASE_RULE": "sf.control_phrase",
                    "NO_HAD_DURATION_RULE": "sf.no_had_duration",
                    "SF_BARE_RULE": "sf.bare",
                    "SF_WITH_DURATION_RULE": "sf.duration",
                    "DECREASED_RULE": "change.decreased",
                    "INCREASED_RULE": "change.increased",
                    "SAME_RULE": "change.same",
                    "DATE_MONTH_RULE": "temporal.date_month",
                    "DATE_MY_RULE": "temporal.date_month_year",
                    "LAST_EVENT_DATE_RULE": "temporal.last_event_date",
                    "LAST_SEIZURE_DATE_RULE": "temporal.last_seizure_date",
                    "PIT_SINCE_RULE": "temporal.point_in_time_since",
                    "PIT_STANDALONE_DURING_RULE": "temporal.point_in_time_standalone_during",
                    "SEIZURE_TERM_MONTH_YEAR_RULE": "temporal.seizure_term_month_year",
                    "SEIZURE_TERM_YEAR_RULE": "temporal.seizure_term_year",
                }
                _EXTRACTION_MODULE = (
                    "clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic."
                    "sf_surface_registry.adapters.extraction"
                )


                def extract_reexport(name: str) -> Any:
                    if name.startswith("__") and name.endswith("__"):
                        raise AttributeError(name)
                    if name not in _LIST_NAMES and name not in _NAMED_RULE_IDS:
                        raise AttributeError(name)
                    extraction = importlib.import_module(_EXTRACTION_MODULE)
                    if name in _LIST_NAMES:
                        return getattr(extraction, name)
                    return extraction.rule_by_id(_NAMED_RULE_IDS[name])
                '''
            ),
            encoding="utf-8",
        )

    (REGISTRY / "extract_catalog.py").write_text(
        textwrap.dedent(
            '''\
            """Load extract-phase catalog metadata for Stack A RuleSpec assembly."""
            from __future__ import annotations

            from dataclasses import dataclass
            from functools import lru_cache
            from pathlib import Path

            import yaml

            from ..rule_metadata import Portability, RuleExample, RuleGroup

            _CATALOG_PATH = Path(__file__).resolve().parent / "catalog" / "extract.yaml"


            @dataclass(frozen=True)
            class ExtractCatalogEntry:
                rule_id: str
                rule_set: str
                order: int
                group: RuleGroup
                portability: Portability
                description: str
                builder: str
                source_stack: str
                examples: tuple[RuleExample, ...]
                provenance: str | None = None
                exclude: tuple[str, ...] = ()
                pattern_id: str | None = None


            def _parse_example(entry: dict[str, object]) -> RuleExample:
                attrs = entry.get("expected_attributes")
                return RuleExample(
                    text=str(entry["text"]),
                    expected_evidence=(
                        str(entry["expected_evidence"]) if entry.get("expected_evidence") is not None else None
                    ),
                    expected_attributes=dict(attrs) if isinstance(attrs, dict) else None,
                    anti_example=bool(entry.get("anti_example")),
                    note=str(entry["note"]) if entry.get("note") is not None else None,
                )


            def _parse_entry(entry: dict[str, object]) -> ExtractCatalogEntry:
                exclude_raw = entry.get("exclude") or []
                return ExtractCatalogEntry(
                    rule_id=str(entry["rule_id"]),
                    rule_set=str(entry["rule_set"]),
                    order=int(entry["order"]),
                    group=RuleGroup(str(entry["group"])),
                    portability=Portability(str(entry["portability"])),
                    description=str(entry["description"]),
                    builder=str(entry["builder"]),
                    source_stack=str(entry["source_stack"]),
                    examples=tuple(_parse_example(ex) for ex in entry.get("examples") or []),
                    provenance=str(entry["provenance"]) if entry.get("provenance") is not None else None,
                    exclude=tuple(str(name) for name in exclude_raw),
                    pattern_id=str(entry["pattern_id"]) if entry.get("pattern_id") is not None else None,
                )


            @lru_cache(maxsize=1)
            def load_extract_catalog() -> tuple[ExtractCatalogEntry, ...]:
                payload = yaml.safe_load(_CATALOG_PATH.read_text(encoding="utf-8")) or {}
                entries = [_parse_entry(entry) for entry in payload.get("rules") or []]
                return tuple(sorted(entries, key=lambda e: (e.rule_set, e.order)))


            def extract_rules_for_set(rule_set: str) -> tuple[ExtractCatalogEntry, ...]:
                return tuple(entry for entry in load_extract_catalog() if entry.rule_set == rule_set)
            '''
        ),
        encoding="utf-8",
    )

    (REGISTRY / "adapters/extraction.py").write_text(
        textwrap.dedent(
            '''\
            """Extraction-phase adapter — assembles Stack A RuleSpec lists from catalog + builders."""
            from __future__ import annotations

            from functools import lru_cache

            from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rule_metadata import RuleSpec
            from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.anchor import ANCHOR_EXTRACT_IMPLS
            from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.change import CHANGE_EXTRACT_IMPLS
            from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.extract_impl_types import ExtractRuleImpl
            from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.rate_builders import RATE_EXTRACT_IMPLS
            from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.seizure_free import SEIZURE_FREE_EXTRACT_IMPLS
            from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.temporal import TEMPORAL_EXTRACT_IMPLS

            from ..extract_catalog import ExtractCatalogEntry, extract_rules_for_set, load_extract_catalog
            from ..patterns import PERIOD_UNIT

            _EXTRACT_IMPLS: dict[str, ExtractRuleImpl] = {
                **ANCHOR_EXTRACT_IMPLS,
                **RATE_EXTRACT_IMPLS,
                **SEIZURE_FREE_EXTRACT_IMPLS,
                **CHANGE_EXTRACT_IMPLS,
                **TEMPORAL_EXTRACT_IMPLS,
            }


            def _resolve_exclude(entry: ExtractCatalogEntry, impl: ExtractRuleImpl) -> tuple:
                if entry.exclude:
                    by_name = {fn.__name__: fn for fn in impl.exclude}
                    return tuple(by_name[name] for name in entry.exclude)
                return impl.exclude


            def _build_rule_spec(entry: ExtractCatalogEntry) -> RuleSpec:
                impl = _EXTRACT_IMPLS[entry.rule_id]
                return RuleSpec(
                    rule_id=entry.rule_id,
                    group=entry.group,
                    portability=entry.portability,
                    description=entry.description,
                    pattern=impl.pattern,
                    build=impl.build,
                    exclude=_resolve_exclude(entry, impl),
                    examples=entry.examples,
                    provenance=entry.provenance,
                )


            @lru_cache(maxsize=8)
            def _rule_set(rule_set: str) -> tuple[RuleSpec, ...]:
                return tuple(_build_rule_spec(entry) for entry in extract_rules_for_set(rule_set))


            def rule_by_id(rule_id: str) -> RuleSpec:
                for entry in load_extract_catalog():
                    if entry.rule_id == rule_id:
                        return _build_rule_spec(entry)
                raise KeyError(rule_id)


            ANCHOR_RULES: list[RuleSpec] = list(_rule_set("anchor"))
            RATE_RULES: list[RuleSpec] = list(_rule_set("rate"))
            SEIZURE_FREE_RULES: list[RuleSpec] = list(_rule_set("seizure_free"))
            CHANGE_RULES: list[RuleSpec] = list(_rule_set("change"))
            TEMPORAL_RULES: list[RuleSpec] = list(_rule_set("temporal"))

            SEIZURE_TYPE_ANCHOR_RULE = rule_by_id("anchor.seizure_type_phrase")
            SEIZURE_FREE_ANCHOR_RULE = rule_by_id("anchor.seizure_free_phrase")

            __all__ = [
                "ANCHOR_RULES", "CHANGE_RULES", "PERIOD_UNIT", "RATE_RULES",
                "SEIZURE_FREE_ANCHOR_RULE", "SEIZURE_FREE_RULES", "SEIZURE_TYPE_ANCHOR_RULE",
                "TEMPORAL_RULES", "rule_by_id",
            ]
            '''
        ),
        encoding="utf-8",
    )
    (REGISTRY / "adapters/__init__.py").write_text(
        '"""Phase adapters for the SF surface registry."""\n\n__all__: list[str] = []\n',
        encoding="utf-8",
    )


def _fix_anchor() -> None:
    path = RULES / "anchor.py"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"\nANCHOR_RULES: list\[RuleSpec\] = \[[\s\S]*?\]\n", "\n", text, count=1)
    if "def __getattr__" not in text:
        text = text.rstrip() + (
            "\n\n\ndef __getattr__(name: str):\n"
            "    if name.startswith(\"__\") and name.endswith(\"__\"):\n"
            "        raise AttributeError(name)\n"
            "    from .extract_reexports import extract_reexport\n\n"
            "    return extract_reexport(name)\n"
        )
    path.write_text(text, encoding="utf-8")


def _add_getattr(module: str) -> None:
    path = RULES / module
    text = path.read_text(encoding="utf-8")
    if "def __getattr__" in text:
        return
    text = text.rstrip() + (
        "\n\n\ndef __getattr__(name: str):\n"
        "    if name.startswith(\"__\") and name.endswith(\"__\"):\n"
        "        raise AttributeError(name)\n"
        "    from .extract_reexports import extract_reexport\n\n"
        "    return extract_reexport(name)\n"
    )
    path.write_text(text, encoding="utf-8")


def main() -> int:
    rule_paths = [
        "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/rules/rate.py",
        "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/rules/anchor.py",
        "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/rules/change.py",
        "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/rules/seizure_free.py",
        "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/rules/temporal.py",
    ]
    subprocess.run(["git", "checkout", "--", *rule_paths], cwd=REPO, check=True)
    _write_support_files()
    for cmd in (
        [sys.executable, "scripts/generate_extract_catalog.py"],
        [sys.executable, "scripts/build_rate_builders.py"],
        [sys.executable, "scripts/strip_extract_rule_specs.py"],
    ):
        subprocess.run(cmd, cwd=REPO, check=True)
    _fix_anchor()
    for module in ("change.py", "seizure_free.py", "temporal.py"):
        _add_getattr(module)
    (RULES / "rate.py").write_text(
        textwrap.dedent(
            '''\
            """Seizure-frequency rate extraction rules for ExECTv2 (Stack A).

            RuleSpec metadata lives in ``sf_surface_registry/catalog/extract.yaml``.
            Builders and patterns live in ``rate_builders.py``; ``RATE_RULES`` is assembled
            by ``sf_surface_registry/adapters/extraction.py``.
            """
            from __future__ import annotations

            from typing import Any

            from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.patterns import (
                PERIOD_UNIT,
            )

            __all__ = ["PERIOD_UNIT"]


            def __getattr__(name: str) -> Any:
                from .extract_reexports import extract_reexport

                return extract_reexport(name)
            '''
        ),
        encoding="utf-8",
    )
    loc = len((RULES / "rate.py").read_text(encoding="utf-8").splitlines())
    print(f"rate.py LOC: {loc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
