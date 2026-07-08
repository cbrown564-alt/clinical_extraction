"""Tests for the SeizureFrequency inspection payload builder.

Codifies the faithfulness guarantee (the scorecard reproduces the published
anchors, so the served payload can never drift from the scorer) and the payload
shape the frontend ``/exectv2-sf-inspection`` route renders.
"""

from __future__ import annotations

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.sf_inspection import (
    COMPONENT_ORDER,
    EXPECTED_F1,
    SfInspectionFaithfulnessError,
    build_sf_inspection_payload,
)


@pytest.fixture(scope="module")
def payload() -> dict:
    return build_sf_inspection_payload()


# ── Faithfulness gate ──


class TestFaithfulnessGate:
    """The scorecard the payload serves must reproduce the scorer's F1s.

    These anchors are the published dev140 numbers for the magnitude-complement
    run. If they drift, the builder raises -- these tests pin that guarantee so a
    regression surfaces in CI rather than as a silently-wrong inspection page.
    """

    def test_state_profile_f1_matches_anchor(self, payload: dict) -> None:
        assert payload["scorecard"]["state_profile"]["f1"] == pytest.approx(
            EXPECTED_F1["state_profile"], abs=1e-4
        )

    def test_directional_f1_matches_anchor(self, payload: dict) -> None:
        assert payload["scorecard"]["state_profile_directional"]["f1"] == pytest.approx(
            EXPECTED_F1["state_profile_directional"], abs=1e-4
        )

    def test_magnitude_f1_matches_anchor(self, payload: dict) -> None:
        assert payload["scorecard"]["state_profile_magnitude"]["f1"] == pytest.approx(
            EXPECTED_F1["state_profile_magnitude"], abs=1e-4
        )

    def test_gate_raises_on_drift(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """If the scorer stops matching the anchor, the builder must fail loudly."""

        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2 import sf_inspection

        # Force a tolerance violation by expecting an unreachable F1.
        monkeypatch.setitem(sf_inspection.EXPECTED_F1, "state_profile", 0.9999)
        # Clear the cache so the next call re-runs the gate.
        sf_inspection.cached_sf_inspection_json.cache_clear()
        with pytest.raises(SfInspectionFaithfulnessError):
            sf_inspection.build_sf_inspection_payload()


# ── Payload shape ──


class TestPayloadShape:
    def test_top_level_fields(self, payload: dict) -> None:
        assert payload["split"] == "dev"
        assert payload["n_letters"] == 140
        assert isinstance(payload["generated_on"], str)
        assert "magnitude_complement" in payload["artifact"]
        assert 0 <= payload["n_with_errors"] <= payload["n_letters"]

    def test_scorecard_has_all_components(self, payload: dict) -> None:
        scorecard = payload["scorecard"]
        assert list(scorecard.keys()) == COMPONENT_ORDER
        for name in COMPONENT_ORDER:
            cell = scorecard[name]
            assert {"f1", "precision", "recall", "tp", "fp", "fn"} <= set(cell.keys())
            assert 0.0 <= cell["f1"] <= 1.0

    def test_components_meta_matches_order(self, payload: dict) -> None:
        names = [c["name"] for c in payload["components"]]
        assert names == COMPONENT_ORDER
        for c in payload["components"]:
            assert c["info"]

    def test_letter_count_matches(self, payload: dict) -> None:
        assert len(payload["letters"]) == payload["n_letters"]

    def test_letter_has_activity_and_layers(self, payload: dict) -> None:
        active = [lt for lt in payload["letters"] if lt["has_activity"]]
        empty = [lt for lt in payload["letters"] if not lt["has_activity"]]
        assert active, "expected at least one letter with SF activity"
        assert empty, "expected at least one empty letter"

        for letter in active:
            assert {
                "letter_id",
                "gold_count",
                "pred_count",
                "total_errors",
                "direction_errors",
                "magnitude_errors",
                "layer_a",
                "layer_b",
                "lineage",
            } <= set(letter.keys())
            assert {"fp", "fn"} <= set(letter["direction_errors"].keys())
            assert {"fp", "fn"} <= set(letter["magnitude_errors"].keys())

            # Layer B always reports all 11 components, even on clean letters.
            comps = letter["layer_b"]["components"]
            assert [c["name"] for c in comps] == COMPONENT_ORDER
            for comp in comps:
                assert {"name", "info", "has_error", "verdict", "tp", "fp", "fn", "rows"} <= set(
                    comp.keys()
                )
                assert comp["verdict"] in {"clean", "err"}
                assert comp["has_error"] == (comp["verdict"] == "err")

    def test_letter_error_sum_is_consistent(self, payload: dict) -> None:
        """A letter's total_errors equals the sum of its components' FP+FN."""

        for letter in payload["letters"]:
            if not letter["has_activity"]:
                assert letter["total_errors"] == 0
                continue
            summed = sum(c["fp"] + c["fn"] for c in letter["layer_b"]["components"])
            assert letter["total_errors"] == summed

    def test_layer_a_pairs_have_attribute_rows(self, payload: dict) -> None:
        active = next(lt for lt in payload["letters"] if lt["gold_count"] and lt["pred_count"])
        pair = active["layer_a"]["pairs"][0]
        assert {
            "label",
            "side",
            "gold_phrase",
            "gold_normalized",
            "pred_phrase",
            "pred_normalized",
            "phrase_match",
            "attributes",
        } <= set(pair.keys())
        # Every pair carries the full SF attribute order.
        keys = [a["key"] for a in pair["attributes"]]
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.sf_inspection import (
            SF_ATTR_ORDER,
        )

        assert keys == SF_ATTR_ORDER
        for attr in pair["attributes"]:
            assert attr["match"] in {"ok", "bad", "absent"}
            assert attr["validity"] in {"ok", "absent", "illegal_value", "illegal_attr", "noise"}

    def test_at_least_one_letter_has_errors(self, payload: dict) -> None:
        with_errors = [lt for lt in payload["letters"] if lt["total_errors"] > 0]
        assert len(with_errors) == payload["n_with_errors"]
        assert with_errors, "expected at least one letter with component errors"

    def test_lineage_override_shape_when_present(self, payload: dict) -> None:
        with_override = [
            lt
            for lt in payload["letters"]
            if lt["lineage"]["override"] and lt["lineage"]["override"].get("applied")
        ]
        if with_override:
            ov = with_override[0]["lineage"]["override"]
            assert ov["applied"] is True
            assert isinstance(ov["items"], list) and ov["items"]
            item = ov["items"][0]
            assert {
                "applies_to",
                "prior_frequency_change",
                "assembled_magnitude",
                "selection_mode",
                "selected_candidate_id",
            } <= set(item.keys())
