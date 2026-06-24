from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.final_consolidation import (
    REPO_ROOT,
)


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_phase4_reliability_is_a_distinct_cross_dataset_surface() -> None:
    meta = _read("frontend/components/surface/meta.tsx")
    navbar = _read("frontend/components/Navbar.tsx")
    reliability_page = REPO_ROOT / "frontend/app/reliability-scorecard/page.tsx"

    assert reliability_page.exists()
    assert 'label: "Reliability Scorecard"' in meta
    assert 'href: "/reliability-scorecard"' in meta
    assert '"laboratory",\n  "reliability",' in meta
    assert "SURFACE_ORDER.map" in navbar


def test_phase4_exectv2_component_ablation_contract_is_documented() -> None:
    contract = _read("docs/design/exectv2_component_ablation_contract_2026-06-24.md")

    for boundary in (
        "LLM producers",
        "Deterministic dictionaries",
        "Semantic lenses",
        "Evidence validation",
        "Assembly / arbitration",
        "Deterministic projection",
    ):
        assert boundary in contract

    for required_field in (
        "baseline_run_id",
        "ablated_run_id",
        "component_boundary",
        "overall_f1_delta",
        "family_deltas",
        "provenance_policy",
    ):
        assert required_field in contract

    assert "No full-200 or holdout-facing row-level inspection" in contract


def test_phase4_exectv2_frontend_keeps_projection_separate_from_prediction_bearing_lanes() -> None:
    descriptor = _read("frontend/lib/datasets/exectv2.ts")
    adapter = _read("frontend/lib/datasets/adapters/exectv2Components.ts")
    surface = _read("frontend/components/exectv2/Exectv2ComponentImpact.tsx")

    assert 'id: "deterministic_projection"' in descriptor
    assert '| "deterministic_projection"' in adapter
    assert 'return "deterministic_projection";' in adapter
    assert "True one-component-off deltas remain gated" in surface
