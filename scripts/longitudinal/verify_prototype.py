"""Verify the saved Phase 4 artifact's provenance, evidence and cutoff boundaries."""
from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.longitudinal.evidence import digest, grounded

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/longitudinal/prototype_v0.1"


def main() -> None:
    summary = json.loads((OUT / "summary.json").read_text())
    for name, expected in summary["source_sha256"].items():
        assert digest(ROOT / name) == expected, f"Changed source: {name}"
    rows = json.loads((OUT / "comparison.json").read_text())
    assert len(rows) == 1680
    checked = 0
    failures = 0
    for path in sorted((OUT / "frames").glob("*/*.json")):
        frame = json.loads(path.read_text())
        cutoff = frame["requests"][0]["information_cutoff"]
        docs = {d["letter_id"]: d for d in frame["documents"]}
        assert all(d["available_date"] <= cutoff for d in docs.values()), path
        assert len(frame["answers"]) == 5
        if frame["status"] == "failed":
            failures += 1
            assert all(a["status"] == "failed" for a in frame["answers"])
        for a in frame["answers"]:
            assert all(grounded(e, docs) for e in a["evidence"]), path
        for a in frame.get("annotations", {}).get("assertions", []):
            assert all(grounded(e, docs) for e in a["evidence"]), path
        for link in frame.get("annotations", {}).get("links", []):
            assert all(grounded(e, docs) for e in link["evidence"]), path
        checked += 1
    assert checked == 96 and failures == 4
    counts = summary["query_comparison"]["variant"]
    assert all(counts[k]["total"] == 480 for k in ("reference_links", "inferred_links", "no_links"))
    assert counts["predicted_facts"]["total"] == 240 and counts["predicted_facts"]["failures"] == 20
    print(f"Verified {checked} view/source frames, 1680 comparison rows, four retained capture failures.")


if __name__ == "__main__":
    main()
