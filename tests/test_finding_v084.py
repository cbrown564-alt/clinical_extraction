from __future__ import annotations

import copy
import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import finding_v084
from scripts.benchmarks.revise_findings_v084 import revise

BUNDLE = Path("runs/seizure_finding_annotation_v0_8_3/dev750_r8_saved/review_bundle.json")
REFERENCE = Path("runs/seizure_finding_annotation_v0_8_3/dev750_r8_saved/reference.jsonl")


def examples(*ids: int) -> dict[int, tuple[dict, str]]:
    rows = {r["source_row_index"]: r for r in json.loads(BUNDLE.read_text())["rows"]}
    refs = {
        r["source_row_index"]: r
        for r in (json.loads(line) for line in REFERENCE.read_text().splitlines())
    }
    return {i: (refs[i], rows[i]["note"]) for i in ids}


def test_cluster_occurrence_date_is_context_but_size_is_scored() -> None:
    ref, note = examples(16645)[16645]
    gold = next(f for f in ref["findings"] if f["measurement"]["type"] == "cluster")
    predicted = copy.deepcopy(gold)
    predicted["measurement"]["occurred_at"] = {"time": "another date", "form": "calendar"}
    assert finding_v084.compatible(predicted, gold, note)
    predicted["measurement"]["seizures_per_cluster"]["value"] = 4
    assert not finding_v084.compatible(predicted, gold, note)


def test_cluster_days_and_size_are_one_finding_without_merging_different_windows() -> None:
    for index in (11109, 11118, 11131):
        ref, note = examples(index)[index]
        revised, edits = revise(ref, note)
        clusters = [f for f in revised["findings"] if f["measurement"]["type"] == "cluster"]
        assert len(clusters) == 1
        assert clusters[0]["measurement"]["count"] == {"type": "number", "value": 2}
        assert clusters[0]["measurement"]["seizures_per_cluster"]
        assert not any(f["event"]["type"] == "seizure days" for f in revised["findings"])
        assert any(
            e["reason"] == "combine cluster-day count and seizures per cluster" for e in edits
        )
    ref, note = examples(3827)[3827]
    revised, _ = revise(ref, note)
    assert len(revised["findings"]) == len(ref["findings"])


def test_explicit_seizure_link_and_two_week_boundary() -> None:
    for index in (6738, 15513):
        ref, note = examples(index)[index]
        revised, _ = revise(ref, note)
        assert len(revised["findings"]) == len(ref["findings"]) - 1
    for index in (3528, 8144):
        ref, note = examples(index)[index]
        revised, _ = revise(ref, note)
        assert revised["findings"] == ref["findings"]
