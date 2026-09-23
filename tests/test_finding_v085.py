from __future__ import annotations

import copy
import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_v084,
    finding_v085,
)
from scripts.benchmarks.revise_findings_v085 import SPAN_PERIODS, revise

BUNDLE = Path("runs/seizure_finding_annotation_v0_8_4/dev750_r8_saved/review_bundle.json")
REFERENCE = Path("runs/seizure_finding_annotation_v0_8_4/dev750_r8_saved/reference.jsonl")


def examples(*ids: int) -> dict[int, tuple[dict, str]]:
    wanted = set(ids)
    rows = {
        r["source_row_index"]: r["note"]
        for r in json.loads(BUNDLE.read_text())["rows"]
        if r["source_row_index"] in wanted
    }
    refs = {
        r["source_row_index"]: r
        for r in (json.loads(line) for line in REFERENCE.read_text().splitlines())
        if r["source_row_index"] in wanted
    }
    return {i: (refs[i], rows[i]) for i in ids}


def test_cluster_span_is_evidence_context_even_if_prediction_emits_period() -> None:
    ref, note = examples(15442)[15442]
    old = next(f for f in ref["findings"] if f["measurement"]["type"] == "cluster")
    revised, _ = revise(ref, note)
    gold = next(f for f in revised["findings"] if f["id"] == old["id"])
    assert "a day" in gold["evidence"]
    assert "period" not in gold
    assert not finding_v084.compatible(old, gold, note)
    assert finding_v085.compatible(old, gold, note)
    wrong_size = copy.deepcopy(old)
    wrong_size["measurement"]["seizures_per_cluster"]["value"] = 3
    assert not finding_v085.compatible(wrong_size, gold, note)


def test_observation_window_and_cluster_cadence_still_score() -> None:
    ref, note = examples(11131)[11131]
    gold = next(f for f in ref["findings"] if f["measurement"]["type"] == "cluster")
    no_period = copy.deepcopy(gold)
    no_period.pop("period")
    assert not finding_v085.compatible(no_period, gold, note)
    assert finding_v085.compatible(gold, gold, note)

    ref, note = examples(8969)[8969]
    gold = next(f for f in ref["findings"] if f["measurement"]["type"] == "cluster")
    wrong_cadence = copy.deepcopy(gold)
    wrong_cadence["measurement"]["rate"]["per"]["unit"] = "month"
    assert not finding_v085.compatible(wrong_cadence, gold, note)

    ref, note = examples(15697)[15697]
    gold = next(f for f in ref["findings"] if f["measurement"]["type"] == "cluster")
    tautological_size = copy.deepcopy(gold)
    tautological_size["measurement"]["seizures_per_cluster"] = {
        "type": "qualitative",
        "quantity": "multiple",
    }
    assert finding_v085.compatible(tautological_size, gold, note)
    invented_size = copy.deepcopy(gold)
    invented_size["measurement"]["seizures_per_cluster"] = {
        "type": "number",
        "value": 3,
    }
    assert not finding_v085.compatible(invented_size, gold, note)


def test_only_source_checked_within_cluster_spans_move_out_of_period() -> None:
    rows = examples(*SPAN_PERIODS, 11131, 10618)
    assert len(SPAN_PERIODS) == 18
    for index, ident in SPAN_PERIODS.items():
        ref, note = rows[index]
        revised, edits = revise(ref, note)
        before = next(f for f in ref["findings"] if f["id"] == ident)
        after = next(f for f in revised["findings"] if f["id"] == ident)
        assert before["period"]["time"] in after["evidence"]
        assert "period" not in after
        assert len(edits) == 1
    for index in (11131, 10618):
        ref, note = rows[index]
        revised, edits = revise(ref, note)
        assert revised["findings"] == ref["findings"]
        assert not edits
