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
_MAX_TARGET_PROJECTION_SF_LOC = 800
_TARGET_PROJECTION_SF_MODULES = (
    "policy.py",
    "constants.py",
    "shared.py",
    "types.py",
    "__init__.py",
)

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


def test_target_projection_sf_modules_line_count_gate() -> None:
    tp_root = _REGISTRY_ROOT.parent / "target_projection"
    total = sum(_count_lines(tp_root / name) for name in _TARGET_PROJECTION_SF_MODULES)
    assert total <= _MAX_TARGET_PROJECTION_SF_LOC, (
        f"target_projection SF modules LOC {total} exceeds {_MAX_TARGET_PROJECTION_SF_LOC}"
    )


def test_p1_v09_dev140_sf_scores_match_frozen_baseline() -> None:
    """Live no-call replay: SF headline + active_rate_fidelity unchanged vs frozen v09."""

    repo = _REPO_ROOT
    frozen_path = (
        repo
        / "experiments/_archive/exectv2_richschema_iterations"
        / "exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140_20260621.json"
    )
    structured_archive = (
        repo
        / "experiments/_archive/exectv2_richschema_iterations"
        / "exectv2_llm_only_key_entities_structured_v09_dev140_gpt41mini_20260621.jsonl"
    )
    if not frozen_path.exists() or not structured_archive.exists():
        pytest.skip("archived v09 dev140 artifacts not available")

    import json

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.manifests import (
        ProducerManifest,
        load_finding_assembly_manifest,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
        build_finding_assembly,
    )

    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))["score_ladder"]
    manifest = load_finding_assembly_manifest(
        repo
        / "configs/exectv2/finding_assembly"
        / "exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140.yaml"
    )
    structured = manifest.producers["key_entities_structured_v09"]
    if not structured.artifact.exists():
        structured = ProducerManifest(**{**structured.__dict__, "artifact": structured_archive})
        manifest = type(manifest)(
            **{
                **manifest.__dict__,
                "producers": {**manifest.producers, "key_entities_structured_v09": structured},
            }
        )
    run = build_finding_assembly(manifest, generated_on="2026-06-26")
    ladder = run.report["score_ladder"]
    sf_headline = ladder["headline_target"]["by_indicator"]["SeizureFrequency"]["f1"]
    sf_fidelity = ladder["fidelity_companions"]["SeizureFrequency"]["active_rate_fidelity"]["f1"]
    assert sf_headline == frozen["headline_target"]["by_indicator"]["SeizureFrequency"]["f1"]
    # active_rate_fidelity is NOT compared against the frozen archive: the SF
    # point/range shape-equivalence fix (bare count/cadence vs. an equal-bounds
    # Lower/Upper range now collapse to the same scorer key, see
    # scoring/normalize.py:resolve_point_range) legitimately moves this
    # companion metric, and the frozen v09 JSON predates the fix (0.5907 ->
    # 0.6919 on live replay). Headline is unaffected because clinical_headline
    # keys on count presence, not shape, so it stays frozen-archive-comparable.
    assert sf_fidelity == 0.6919


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
