"""Separate representation differences from unresolved temporal/link meaning."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASS = ROOT / "results/longitudinal/pilot_v0.3/agy_pass_medium"


def normalized_time(value: dict | None) -> dict | None:
    if value is None:
        return None
    result = {k: v for k, v in value.items() if k != "text"}
    for field in ("start", "end"):
        if result.get(field) == {"earliest": None, "latest": None}:
            result[field] = None
    return result


def compare_time(reference: dict | None, observed: dict | None) -> str:
    if reference == observed:
        return "exact"
    left, right = normalized_time(reference), normalized_time(observed)
    if left == right:
        return "representation_only"
    if left is None or right is None:
        return "missing_time"
    if any(left.get(k) != right.get(k) for k in ("kind", "anchor_letter_id")):
        return "kind_or_anchor_difference"
    return "bounds_difference"


def audit() -> dict:
    saved = json.loads((PASS / "analysis_evidence_v2.json").read_text())
    rows, links = [], []
    for job in saved["job_audits"]:
        if not job["comparison"]:
            continue
        case, stem = job["job"].split("/")
        reference = json.loads(
            (ROOT / "examples/longitudinal" / case / "annotations.json").read_text()
        )
        observed = json.loads((PASS / "attempts" / case / stem / "parsed.json").read_text())[
            "annotations"
        ]
        ref = {a["assertion_id"]: a for a in reference["assertions"]}
        pred = {a["assertion_id"]: a for a in observed["assertions"]}
        matches = job["comparison"]["matched_details"]
        mapping = {m["observed_id"]: m["reference_id"] for m in matches}
        for match in matches:
            a, b = ref[match["reference_id"]], pred[match["observed_id"]]
            rows.append(
                {
                    "job": job["job"],
                    **match,
                    "classification": compare_time(a["time"], b["time"]),
                    "reference_time": a["time"],
                    "observed_time": b["time"],
                    "reference_evidence": a["evidence"],
                    "observed_evidence": b["evidence"],
                }
            )
        input_path = (
            ROOT / "results/longitudinal/pilot_v0.3/independent_pass/inputs" / case / f"{stem}.json"
        )
        permitted = {d["letter_id"] for d in json.loads(input_path.read_text())["documents"]}
        mapped = set(mapping.values())
        for origin, items in [("reference", reference["links"]), ("observed", observed["links"])]:
            for link in items:
                ids = (link["earlier_assertion"], link["later_assertion"])
                if origin == "reference" and any(x not in ref for x in ids):
                    continue
                # Full reference can contain future letters; only report permitted endpoints.
                if origin == "reference" and any(ref[x]["letter_id"] not in permitted for x in ids):
                    continue
                links.append(
                    {
                        "job": job["job"],
                        "origin": origin,
                        "both_endpoints_literal_matched": all(
                            x in (mapped if origin == "reference" else mapping) for x in ids
                        ),
                        "link": link,
                    }
                )
    return {
        "scope": "44 successful synthetic development jobs; unique literal content matches only",
        "normalization": "ignore time.text; equate null bound and two-null bound; no date repair",
        "claim": "difference triage, not semantic accuracy or adjudication of every row",
        "time_counts": dict(Counter(r["classification"] for r in rows)),
        "by_family": {
            f: dict(Counter(r["classification"] for r in rows if r["family"] == f))
            for f in sorted({r["family"] for r in rows})
        },
        "link_counts": dict(
            Counter(
                f"{r['origin']}/{'aligned' if r['both_endpoints_literal_matched'] else 'unaligned'}"
                for r in links
            )
        ),
        "rows": rows,
        "links": links,
    }


if __name__ == "__main__":
    result = audit()
    destination = ROOT / "results/longitudinal/pilot_v0.5/temporal_relationship_audit.json"
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("rows", "links")}))
