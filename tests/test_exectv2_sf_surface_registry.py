"""CI gates for the SF surface registry (P1-1 Phase 0)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    all_entities as _all_entities,  # noqa: F401 — prime normalization before dictionary import
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.parity.shadow_diff import (
    RewriteCase,
    format_diff_ledger,
    run_shadow_diff,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_REGISTRY_ROOT = (
    _REPO_ROOT
    / "src"
    / "clinical_extraction"
    / "tasks"
    / "epilepsy_phenotyping"
    / "exectv2"
    / "deterministic"
    / "sf_surface_registry"
)
_RULE_INDEX_PATH = _REPO_ROOT / "docs" / "plans" / "sf_surface_rule_index.yaml"
_PHASE2_MAX_PYTHON_LINES = 850
_PHASE2_MAX_YAML_LINES = 1500
_MAX_CATALOG_FILE_LINES = 250

STANDARD_DICTIONARY_SF_REWRITE_CASES: tuple[RewriteCase, ...] = (
    RewriteCase(
        name="cluster_of_3",
        text="cluster of 3",
        evidence="a cluster of 3 in March",
        attributes={},
        expected_rule="rewrite_cluster_of_3_to_seizure_cluster",
    ),
    RewriteCase(
        name="absences_requires_evidence",
        text="absences",
        evidence="frequent typical absences",
        attributes={},
        expected_rule="rewrite_absences_to_typical_absences",
    ),
    RewriteCase(
        name="absence_like_dated_occurrence",
        text="absence like seizures",
        evidence="Around the same time he would also have absence-like episodes.",
        attributes={
            "NumberOfSeizures": "1",
            "TimeSince_or_TimeOfEvent": "During",
            "YearDate": "2014",
        },
        expected_rule="rewrite_absence_like_dated_occurrence_to_cui",
    ),
    RewriteCase(
        name="drop_per_month_month_date_operand_noise",
        text="seizures",
        evidence="Currently she get around 2-4 seizures per month.",
        attributes={
            "LowerNumberOfSeizures": "2",
            "UpperNumberOfSeizures": "4",
            "NumberOfTimePeriods": "1",
            "TimePeriod": "Month",
            "MonthDate": "1",
        },
        expected_rule_contains="drop_per_month_spurious_month_date",
    ),
    RewriteCase(
        name="exact_count_over_months_operands",
        text="seizures",
        evidence="approximately 15 seizures over 4 months",
        attributes={
            "LowerNumberOfSeizures": "15",
            "UpperNumberOfSeizures": "15",
            "TimePeriod": "Month",
        },
        expected_rule_contains="rewrite_exact_count_over_months_operand_format",
    ),
    RewriteCase(
        name="exact_every_weeks_not_range",
        text="focal seizures with altered awareness",
        evidence="focal seizures with altered awareness every 3 weeks",
        attributes={
            "NumberOfSeizures": "1",
            "LowerNumberOfTimePeriods": "3",
            "UpperNumberOfTimePeriods": "4",
            "TimePeriod": "Week",
        },
        expected_rule="rewrite_exact_every_weeks_operand_format",
    ),
    RewriteCase(
        name="collapse_lower_zero_to_exact_zero",
        text="absences",
        evidence="There have been no absences since November 2016.",
        attributes={
            "CUI": "C0563606",
            "CUIPhrase": "absences",
            "LowerNumberOfSeizures": "0",
            "MonthDate": "11",
            "TimeSince_or_TimeOfEvent": "Since",
        },
        expected_rule_contains="collapse_lower_zero_to_exact_zero_count",
    ),
    RewriteCase(
        name="selected_no_further_gtc_state",
        text="seizures",
        evidence=(
            "I was pleased to hear that she has not had any further generalised "
            "tonic clonic seizures since August 2016."
        ),
        attributes={
            "CUI": "C0036572",
            "CUIPhrase": "seizures",
            "LowerNumberOfSeizures": "0",
            "MonthDate": "8",
            "TimeSince_or_TimeOfEvent": "Since",
        },
        expected_rule="rewrite_selected_no_further_gtc_to_named_seizure_free",
    ),
)


def _count_lines(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def _registry_python_line_count() -> int:
    total = 0
    for path in sorted(_REGISTRY_ROOT.rglob("*.py")):
        if path.name == "builders.py" or "builders" in path.parts or "__pycache__" in path.parts:
            continue
        total += _count_lines(path)
    return total


def _registry_yaml_line_count() -> int:
    return sum(_count_lines(path) for path in sorted(_REGISTRY_ROOT.rglob("*.yaml")))


def test_catalog_rule_ids_are_unique() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry import (
        validate_unique_rule_ids,
    )

    validate_unique_rule_ids()


def test_rule_index_has_disjoint_stack_namespaces() -> None:
    index = yaml.safe_load(_RULE_INDEX_PATH.read_text(encoding="utf-8"))
    stacks = index["stacks"]
    extract = set(stacks["extract"]["rule_ids"])
    convention = set(stacks["convention_rewrite"]["rule_ids"])
    projection = set(stacks["projection"]["rule_ids"])
    assert extract.isdisjoint(convention)
    assert extract.isdisjoint(projection)
    assert convention.isdisjoint(projection)


def test_registry_package_line_count_gate() -> None:
    python_lines = _registry_python_line_count()
    yaml_lines = _registry_yaml_line_count()
    assert python_lines <= _PHASE2_MAX_PYTHON_LINES, (
        f"sf_surface_registry Python LOC {python_lines} exceeds {_PHASE2_MAX_PYTHON_LINES}"
    )
    assert yaml_lines <= _PHASE2_MAX_YAML_LINES, (
        f"sf_surface_registry YAML LOC {yaml_lines} exceeds {_PHASE2_MAX_YAML_LINES}"
    )
    for path in sorted((_REGISTRY_ROOT / "catalog").glob("*.yaml")):
        if path.name == "extract.yaml":
            continue
        file_lines = _count_lines(path)
        assert file_lines <= _MAX_CATALOG_FILE_LINES, (
            f"{path.name} has {file_lines} lines; catalog files must stay ≤{_MAX_CATALOG_FILE_LINES}"
        )


@pytest.mark.parametrize("case", STANDARD_DICTIONARY_SF_REWRITE_CASES, ids=lambda c: c.name)
def test_shadow_diff_matches_legacy_on_standard_dictionary_case(case: RewriteCase) -> None:
    diff = run_shadow_diff([case])[0]
    assert diff.matches, format_diff_ledger([diff])
    if case.expected_rule is not None:
        assert diff.legacy is not None
        assert diff.legacy[2] == case.expected_rule
    if case.expected_rule_contains is not None:
        assert diff.legacy is not None
        assert case.expected_rule_contains in diff.legacy[2]


def test_shadow_diff_zero_mismatches_on_all_standard_dictionary_cases() -> None:
    diffs = run_shadow_diff(STANDARD_DICTIONARY_SF_REWRITE_CASES)
    mismatches = [diff for diff in diffs if not diff.matches]
    assert not mismatches, format_diff_ledger(mismatches)


def test_shared_patterns_match_standard_dictionary_fixtures() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.patterns import (
        CONTEXTUAL_RATE_NOISE,
        EVERY_N_TO_M_PERIODS,
        NO_FURTHER_SINCE,
        SEIZURES_EVERY_RANGE_WEEKS,
    )

    assert SEIZURES_EVERY_RANGE_WEEKS.search("seizures every 3 to 4 weeks")
    assert EVERY_N_TO_M_PERIODS.search("every 3 to 4 weeks")
    assert NO_FURTHER_SINCE.search("no further seizures since August 2016")
    assert not CONTEXTUAL_RATE_NOISE.search(
        "I was pleased to hear that he remains seizure free and is now driving."
    )
    assert CONTEXTUAL_RATE_NOISE.search(
        "referred previously before the seizure and remains well controlled"
    )


def test_extract_adapter_rule_count_matches_catalog() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.adapters.extraction import (
        ANCHOR_RULES,
        CHANGE_RULES,
        RATE_RULES,
        SEIZURE_FREE_RULES,
        TEMPORAL_RULES,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.extract_catalog import (
        load_extract_catalog,
    )

    assembled = ANCHOR_RULES + RATE_RULES + SEIZURE_FREE_RULES + CHANGE_RULES + TEMPORAL_RULES
    catalog = load_extract_catalog()
    assert len(assembled) == len(catalog)
    assert {spec.rule_id for spec in assembled} == {entry.rule_id for entry in catalog}


def test_extract_adapter_examples_match_catalog_metadata() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.adapters.extraction import (
        RATE_RULES,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.extract_catalog import (
        load_extract_catalog,
    )

    by_id = {entry.rule_id: entry for entry in load_extract_catalog()}
    for spec in RATE_RULES:
        entry = by_id[spec.rule_id]
        assert spec.description == entry.description
        assert spec.provenance == entry.provenance
        assert len(spec.examples) == len(entry.examples)


def test_pattern_registry_exports_phase1_keys() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.patterns import (
        pattern_names,
    )

    assert {
        "CONTEXTUAL_RATE_NOISE",
        "EVERY_N_TO_M_PERIODS",
        "NO_FURTHER_SINCE",
        "SEIZURES_EVERY_RANGE_WEEKS",
        "NO_FURTHER_GTC_SINCE",
    }.issubset(set(pattern_names()))
