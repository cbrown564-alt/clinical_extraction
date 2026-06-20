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
    assert PROJECTION_RULE_REGISTRY[
        "projected_diagnosis_context_to_frequent_myoclonic_jerks"
    ].portability is ProjectionPortability.GAN2026_SPECIFIC
    assert PROJECTION_RULE_REGISTRY["projected_christmas_point_to_month_date"].as_dict() == {
        "rule_id": "projected_christmas_point_to_month_date",
        "entity": "SeizureFrequency",
        "portability_category": "benchmark_format",
        "enabled_by_default": False,
        "switch_name": (
            "target_projection_family_switches."
            "projected_christmas_point_to_month_date"
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
                "Diagnosis: normalized_diagnosis_text: 'focal epilepsy' -> "
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
                    "text": "focal epilepsy",
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
