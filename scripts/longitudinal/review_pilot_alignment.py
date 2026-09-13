"""Evidence-constrained endpoint alignment for saved pilot outputs; never repairs them."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.longitudinal.check_annotations import evidence_overlap, grounded_span  # noqa: E402

PASS = ROOT / "results/longitudinal/pilot_v0.3/agy_pass_medium"


def compatible(a: dict, b: dict) -> bool:
    if a["letter_id"] != b["letter_id"]:
        return False
    left, right = a["content"], b["content"]
    if left["family"] != right["family"]:
        return False
    fields = {
        "diagnosis": ("phase",),
        "seizure": ("kind", "interpretation", "scope"),
        "medication": ("name", "status"),
        "investigation": ("modality", "status"),
    }
    return all(
        str(left.get(k)).casefold() == str(right.get(k)).casefold() for k in fields[left["family"]]
    ) and all(a[k] == b[k] for k in ("reporter", "certainty", "polarity"))


def align_assertions(
    reference: list[dict], observed: list[dict], documents: dict
) -> tuple[dict, dict]:
    """Mutual uniqueness only; preserve candidate sets for split/merged assertions."""
    candidates = {}
    for b in observed:
        candidates[b["assertion_id"]] = [
            a["assertion_id"]
            for a in reference
            if compatible(a, b)
            and a["evidence"]
            and b["evidence"]
            and all(grounded_span(e, documents) for e in a["evidence"] + b["evidence"])
            and any(evidence_overlap(x, y) for x in a["evidence"] for y in b["evidence"])
        ]
    counts = Counter(x for values in candidates.values() for x in values)
    mapping = {
        k: values[0]
        for k, values in candidates.items()
        if len(values) == 1 and counts[values[0]] == 1
    }
    return mapping, candidates


def audit() -> dict:
    saved = json.loads((PASS / "analysis_evidence_v2.json").read_text())
    rows, hashes = [], {}
    for job in saved["job_audits"]:
        if not job["comparison"]:
            continue
        case, stem = job["job"].split("/")
        paths = [
            ROOT / "examples/longitudinal" / case / "annotations.json",
            PASS / "attempts" / case / stem / "parsed.json",
            ROOT
            / "results/longitudinal/pilot_v0.3/independent_pass/inputs"
            / case
            / f"{stem}.json",
        ]
        reference, parsed, inputs = [json.loads(p.read_text()) for p in paths]
        hashes.update(
            {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        )
        documents = {d["letter_id"]: d for d in inputs["documents"]}
        ref = [a for a in reference["assertions"] if a["letter_id"] in documents]
        observed = parsed["annotations"]
        mapping, candidates = align_assertions(ref, observed["assertions"], documents)
        ref_ids = {a["assertion_id"] for a in ref}
        expected = [
            link
            for link in reference["links"]
            if all(link[k] in ref_ids for k in ("earlier_assertion", "later_assertion"))
            and link["evidence"]
            and all(grounded_span(e, documents) for e in link["evidence"])
        ]
        link_rows = []
        for origin, links in [("reference", expected), ("observed", observed["links"])]:
            for link in links:
                endpoints = [link[k] for k in ("earlier_assertion", "later_assertion")]
                mapped = endpoints if origin == "reference" else [mapping.get(x) for x in endpoints]
                aligned = (
                    all(x in mapping.values() for x in endpoints)
                    if origin == "reference"
                    else all(mapped)
                )
                link_rows.append(
                    {
                        "origin": origin,
                        "link": link,
                        "mapped_endpoints": mapped,
                        "aligned": bool(aligned),
                        "evidence_grounded": bool(link["evidence"])
                        and all(grounded_span(e, documents) for e in link["evidence"]),
                    }
                )

        def key(row: dict) -> tuple:
            ends = row["mapped_endpoints"]
            if row["link"]["relation"] in ("same_pattern", "overlaps_active", "contradicts"):
                ends = sorted(ends)
            return (*ends, row["link"]["relation"], row["link"]["certainty"])

        counters = {
            origin: Counter(
                key(r)
                for r in link_rows
                if r["origin"] == origin and r["aligned"] and r["evidence_grounded"]
            )
            for origin in ("reference", "observed")
        }
        rows.append(
            {
                "job": job["job"],
                "reference_assertions": len(ref),
                "observed_assertions": len(observed["assertions"]),
                "mapping": mapping,
                "candidates": candidates,
                "links": link_rows,
                "relation_matches_on_aligned_endpoints": sum(
                    (counters["reference"] & counters["observed"]).values()
                ),
            }
        )
    return {
        "claim": "evidence-constrained alignment diagnostic, not clinical relationship accuracy",
        "matching": (
            "same letter, family, semantic status, reporter/certainty/polarity; "
            "grounded overlapping evidence; mutual uniqueness"
        ),
        "model_calls": 0,
        "repair_policy": "none",
        "input_sha256": hashes,
        "program_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "summary": {
            "jobs": len(rows),
            "aligned_assertions": sum(len(r["mapping"]) for r in rows),
            "relation_matches_on_aligned_endpoints": sum(
                r["relation_matches_on_aligned_endpoints"] for r in rows
            ),
            "link_counts": dict(
                Counter(
                    f"{link['origin']}/{'aligned' if link['aligned'] else 'unaligned'}"
                    for row in rows
                    for link in row["links"]
                )
            ),
        },
        "jobs": rows,
    }


if __name__ == "__main__":
    result = audit()
    target = ROOT / "results/longitudinal/pilot_v0.7/link_alignment.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["summary"], indent=2))
