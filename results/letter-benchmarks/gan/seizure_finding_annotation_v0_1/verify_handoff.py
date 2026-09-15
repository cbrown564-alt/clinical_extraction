"""Run fictional regression checks for the handoff; no dataset/model access."""

import copy
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from check_annotations import check

folder = Path(__file__).resolve().parent
manifest = json.loads((folder / "handoff_manifest.json").read_text())
for name, expected_hash in manifest["files"].items():
    assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == expected_hash, name
blocks = [
    json.loads(block)
    for block in re.findall(
        r"```json\n(.*?)\n```", (folder / "worked_examples.md").read_text(), re.S
    )
]
record = blocks[0]
source = {
    "source_id": record["source_id"],
    "source_row_index": 0,
    "source_sha256": record["source_sha256"],
    "row_ok": False,
    "note_text": (
        "She currently has two focal seizures per week. "
        "She also had three tonic-clonic seizures in the past six weeks."
    ),
}
with tempfile.TemporaryDirectory() as temporary:
    directory = Path(temporary)
    sources = directory / "sources.jsonl"
    annotations = directory / "annotations.jsonl"
    sources.write_text(json.dumps(source) + "\n")

    def run(records: list[dict], expected: int = 1) -> dict:
        annotations.write_text("".join(json.dumps(row) + "\n" for row in records))
        return check(sources, annotations, folder / "annotation.schema.json", expected)

    assert run([record])["status"] == "pass", "valid row_ok=False source"
    variants = []
    item = copy.deepcopy(record)
    item["findings"][0]["evidence"] = "invented quotation"
    variants.append(item)
    item = copy.deepcopy(record)
    item["source_sha256"] = "0" * 64
    variants.append(item)
    item = copy.deepcopy(record)
    item["finding_context"][0]["finding_id"] = "missing"
    variants.append(item)
    item = copy.deepcopy(record)
    item["source_checks"] = []
    variants.append(item)
    item = copy.deepcopy(record)
    item["annotation_state"] = "needs_review"
    variants.append(item)
    item = copy.deepcopy(record)
    item["findings"][0]["measurement"]["count"] = {"type": "range", "lower": 5, "upper": 2}
    variants.append(item)
    item = copy.deepcopy(record)
    item["findings"][0]["measurement"] = {
        "type": "cluster",
        "count": {"type": "number", "value": 3},
    }
    variants.append(item)
    for number, item in enumerate(variants):
        assert run([item])["status"] == "fail", f"invalid fixture {number}"
    assert run([record, record])["status"] == "fail", "duplicate annotation"
    assert run([])["status"] == "fail", "missing annotation"
    assert run([record], 750)["status"] == "fail", "full dataset denominator"
    item = copy.deepcopy(record)
    item.update(findings=[], finding_context=[], annotation_state="needs_review")
    item["issues"] = [
        {
            "id": "i1",
            "finding_ids": [],
            "evidence": source["note_text"],
            "kind": "source_ambiguity",
            "question": "Fictional unresolved test",
            "alternatives": ["A", "B"],
        }
    ]
    item["source_checks"] = [
        {
            "evidence": source["note_text"],
            "disposition": "unresolved",
            "finding_ids": [],
            "issue_ids": ["i1"],
            "rule_id": "D12",
            "reason": "",
        }
    ]
    result = run([item])
    assert result["status"] == "pass" and result["unresolved_source_ids"]
print("Handoff hashes and 12 fictional checks passed; no dataset rows read.")

# Run the separate source-group safeguards on fictional records only.

subprocess.run([sys.executable, str(folder / "verify_review_groups.py")], check=True)

subprocess.run([sys.executable, str(folder / "verify_group_decisions.py")], check=True)
