from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry import (
    rules_for_phase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.catalog import (
    projection_sf_rule_ids,
    quarantined_projection_families,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.types import (
    SurfacePhase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.projection_rule_attribution import (  # noqa: E501
    PROJECTION_RULE_REGISTRY,
    ProjectionPortability,
    build_projection_rule_sidecar,
    parse_rule_warning,
    render_projection_rule_sidecar_markdown,
)


def test_projection_rule_registry_uses_required_portability_categories() -> None:
    categories = {spec.portability for spec in PROJECTION_RULE_REGISTRY.values()}

    assert categories == set(ProjectionPortability)
    assert (
        PROJECTION_RULE_REGISTRY[
            "projected_diagnosis_context_to_frequent_myoclonic_jerks"
        ].portability
        is ProjectionPortability.GAN2026_SPECIFIC
    )
    assert PROJECTION_RULE_REGISTRY["projected_christmas_point_to_month_date"].as_dict() == {
        "rule_id": "projected_christmas_point_to_month_date",
        "entity": "SeizureFrequency",
        "portability_category": "benchmark_format",
        "enabled_by_default": False,
        "switch_name": (
            "target_projection_family_switches.projected_christmas_point_to_month_date"
        ),
        "switch_status": "adapter_quarantined_default_audit_replay",
    }


def test_projection_warning_parser_normalizes_entity_prefixed_and_bare_warnings() -> None:
    prefixed = parse_rule_warning(
        "Diagnosis: projected_active_rate_seizure_type_to_diagnosis: focal seizures"
    )
    bare = parse_rule_warning("projected_christmas_point_to_month_date")

    assert prefixed.rule_id == "projected_active_rate_seizure_type_to_diagnosis"
    assert prefixed.entity == "Diagnosis"
    assert bare.rule_id == "projected_christmas_point_to_month_date"
    assert bare.entity == "SeizureFrequency"


def test_projection_rule_sidecar_counts_same_raw_corrections_and_fidelity_effects() -> None:
    rows = [
        {
            "letter_id": "EA-DX",
            "gate_warnings": [
                "Diagnosis: normalized_diagnosis_text: 'cardiac syncope' -> "
                "'temporal lobe epilepsy'"
            ],
            "gold_mentions": [
                {
                    "entity": "Diagnosis",
                    "text": "temporal lobe epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                }
            ],
            "raw_mentions": [
                {
                    "entity": "Diagnosis",
                    "text": "cardiac syncope",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                }
            ],
            "predicted_mentions": [
                {
                    "entity": "Diagnosis",
                    "text": "temporal lobe epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                }
            ],
        },
        {
            "letter_id": "EA-SF",
            "gate_warnings": ["SeizureFrequency: projected_four_since_last_clinic"],
            "gold_mentions": [
                {
                    "entity": "SeizureFrequency",
                    "text": "secondary generalised seizures",
                    "attributes": {
                        "NumberOfSeizures": "4",
                        "TimeSince_or_TimeOfEvent": "Since",
                        "PointInTime": "LastClinic",
                    },
                }
            ],
            "raw_mentions": [],
            "predicted_mentions": [
                {
                    "entity": "SeizureFrequency",
                    "text": "secondary generalised seizures",
                    "attributes": {
                        "NumberOfSeizures": "4",
                        "TimeSince_or_TimeOfEvent": "Since",
                        "PointInTime": "LastClinic",
                    },
                }
            ],
        },
    ]

    sidecar = build_projection_rule_sidecar(rows)
    rules = {rule["rule_id"]: rule for rule in sidecar["rules"]}

    diagnosis = rules["normalized_diagnosis_text"]
    assert diagnosis["changed_rows"] == ["EA-DX"]
    assert diagnosis["wrong_to_correct_count"] == 1
    assert diagnosis["correct_to_wrong_count"] == 0
    assert diagnosis["fidelity_effects"][0]["metric"] == "Diagnosis.concept_negation"
    assert diagnosis["fidelity_effects"][0]["before_f1"] == 0.0
    assert diagnosis["fidelity_effects"][0]["after_f1"] == 1.0

    sf = rules["projected_four_since_last_clinic"]
    assert sf["changed_rows"] == ["EA-SF"]
    assert sf["wrong_to_correct_count"] == 1
    assert sf["fidelity_effects"][0]["metric"] == "SeizureFrequency.active_rate_fidelity"
    assert sf["fidelity_effects"][0]["delta_f1"] == 1.0

    markdown = render_projection_rule_sidecar_markdown(sidecar)
    assert "projected_four_since_last_clinic" in markdown
    assert "Wrong-to-correct" in markdown


def test_projection_sf_catalog_registers_all_seizure_frequency_rules() -> None:
    registered = projection_sf_rule_ids()
    catalog_project = {
        rule.rule_id for rule in rules_for_phase(SurfacePhase.PROJECT) if rule.rule_id in registered
    }
    catalog_evidence = {
        rule.rule_id
        for rule in rules_for_phase(SurfacePhase.EVIDENCE_REPAIR)
        if rule.rule_id in registered
    }

    assert registered == catalog_project | catalog_evidence
    assert len(registered) == 31


def test_quarantined_projection_families_match_attribution_registry() -> None:
    attribution_quarantined = {
        rule_id for rule_id, spec in PROJECTION_RULE_REGISTRY.items() if not spec.enabled_by_default
    }
    registry_quarantined = quarantined_projection_families()

    assert registry_quarantined == {
        rule_id for rule_id in attribution_quarantined if rule_id in projection_sf_rule_ids()
    }
    assert registry_quarantined == frozenset(
        {
            "projected_christmas_point_to_month_date",
            "projected_diagnosis_context_to_controlled_sf_state",
            "projected_diagnosis_context_to_frequent_myoclonic_jerks",
            "projected_diagnosis_context_to_remote_last_seizures_state",
            "projected_four_since_last_clinic",
            "projected_infrequent_context_state",
            "projected_several_since_last_clinic",
            "repaired_last_event_evidence",
            "repaired_since_last_clinic_count_evidence",
        }
    )


def test_each_projection_sf_rule_has_catalog_entry() -> None:
    all_catalog_ids = {rule.rule_id for rule in rules_for_phase(SurfacePhase.PROJECT)} | {
        rule.rule_id for rule in rules_for_phase(SurfacePhase.EVIDENCE_REPAIR)
    }
    for rule_id in sorted(projection_sf_rule_ids()):
        assert rule_id in all_catalog_ids
        spec = PROJECTION_RULE_REGISTRY.get(rule_id)
        if spec is not None:
            assert spec.entity == "SeizureFrequency"
