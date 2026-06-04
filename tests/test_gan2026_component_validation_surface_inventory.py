from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    validation_surface_inventory,
)


def test_validation_surface_inventory_marks_existing_full_validation_surfaces() -> None:
    reasoner_rows = [
        {
            "source_row_index": index,
            "component_status": {
                "selected_evidence_exactness": "ok",
                "source_id_trace": "ok",
            },
        }
        for index in range(1, 751)
    ]
    safety_rows = [
        {
            "source_row_index": index,
            "selected_evidence_exact": True,
            "selected_source_ids_exist": True,
        }
        for index in range(1, 751)
    ]
    router_rows = [
        {
            "source_row_index": index,
            "selective_action": "predict" if index <= 716 else "abstain",
        }
        for index in range(1, 751)
    ]

    inventory = validation_surface_inventory.build_validation_surface_inventory(
        reasoner_rows=reasoner_rows,
        safety_floor_rows=safety_rows,
        router_rows=router_rows,
        safety_floor_summary={
            "slice_summary": {
                "validation750": {
                    "variant_summary": {
                        "combined_selective_gate_v0": {
                            "changed_rows": 21,
                            "wrong_to_correct": 11,
                            "correct_to_wrong": 0,
                        }
                    }
                }
            }
        },
        router_summary={"metrics": {"covered_rows": 716}},
    )

    assert inventory["full_validation_components"] == [
        "hybrid_reasoner_replay",
        "selective_safety_floor_gate_v0",
        "rq9_selective_action_router_v3",
    ]
    assert inventory["component_row_counts"]["rq9_selective_action_router_v3"] == 750
    assert inventory["available_components"][1]["selected_evidence_exact_rows"] == 750
    assert inventory["available_components"][1]["combined_gate_summary"][
        "wrong_to_correct"
    ] == 11
    assert inventory["available_components"][2]["action_counts"] == {
        "abstain": 34,
        "predict": 716,
    }
    assert "promoted_binary_selective_verifier" in {
        component["component_name"]
        for component in inventory["missing_component_inputs"]
    }


def test_validation_surface_inventory_writes_report(tmp_path) -> None:
    inventory = validation_surface_inventory.build_validation_surface_inventory(
        reasoner_rows=[],
        safety_floor_rows=[],
        router_rows=[],
    )
    json_path = tmp_path / "inventory.json"
    report_path = tmp_path / "inventory.md"

    validation_surface_inventory.write_summary_json(inventory, json_path)
    validation_surface_inventory.write_report(
        inventory,
        report_path,
        json_path=json_path,
    )

    assert json_path.exists()
    report = report_path.read_text()
    assert "Available Components" in report
    assert "promoted_binary_selective_verifier" in report
