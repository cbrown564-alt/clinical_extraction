"""Tests for the ExECTv2 GPT-first reliability scorecard (satellite 09, Phase E)."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid import (
    all_entity_assessment as hybrid,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability_scorecard import (
    bootstrap_f1_ci,
    build_scorecard,
    render_markdown,
)


def test_bootstrap_ci_brackets_point() -> None:
    counts = [(2, 0, 0), (1, 1, 1), (0, 0, 2), (3, 1, 0)] * 10
    ci = bootstrap_f1_ci(counts, reps=200, seed=1)
    assert ci.lower <= ci.point <= ci.upper
    assert 0.0 <= ci.lower <= 1.0
    assert 0.0 <= ci.upper <= 1.0


def test_bootstrap_ci_perfect_is_one() -> None:
    ci = bootstrap_f1_ci([(5, 0, 0), (3, 0, 0)], reps=100, seed=2)
    assert ci.point == 1.0
    assert ci.lower == 1.0
    assert ci.upper == 1.0


def _rows(predicted: list[dict], gold: list[dict]) -> list[dict]:
    return [
        {
            "letter_id": "EA1",
            "augment_rules": False,
            "n_candidates": len(predicted),
            "n_mentions_scored": len(predicted),
            "n_routed": 0,
            "routed_taxonomy": {},
            "routed_taxonomy_by_entity": {},
            "predicted_mentions": predicted,
            "gold_mentions": gold,
        }
    ]


def test_gate_not_met_on_empty_prediction() -> None:
    rows = _rows([], [{"entity": "Diagnosis", "text": "epilepsy", "attributes": {"CUI": "C1"}}])
    summary = hybrid.summarize_rows(rows)
    sc = build_scorecard(rows, summary, model="m", split="dev", augment_rules=False,
                         bootstrap_reps=50)
    assert sc["promotion_gate"]["gate_met"] is False
    assert sc["promotion_gate"]["full_200_audit_authorized"] is False


def test_gate_met_on_perfect_prediction() -> None:
    mention = {
        "entity": "Diagnosis",
        "text": "epilepsy",
        "attributes": {"DiagCategory": "Epilepsy", "CUI": "C0014544"},
    }
    rows = _rows([dict(mention)], [dict(mention)])
    summary = hybrid.summarize_rows(rows)
    sc = build_scorecard(rows, summary, model="m", split="dev", augment_rules=False,
                         bootstrap_reps=50)
    assert sc["promotion_gate"]["gate_met"] is True
    assert sc["promotion_gate"]["full_200_audit_authorized"] is True


def test_render_markdown_states_gate() -> None:
    rows = _rows([], [{"entity": "Diagnosis", "text": "epilepsy", "attributes": {"CUI": "C1"}}])
    summary = hybrid.summarize_rows(rows)
    sc = build_scorecard(rows, summary, model="m", split="dev", augment_rules=False,
                         bootstrap_reps=50)
    md = render_markdown(sc)
    assert "Gate met: False" in md
    assert "NOT authorized" in md
