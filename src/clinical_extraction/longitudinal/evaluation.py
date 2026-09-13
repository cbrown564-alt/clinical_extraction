"""Transparent component comparisons against provisional development references."""

from __future__ import annotations

from collections import Counter

from .evidence import Record, overlap
from .queries import related


def alignment(predicted: Record, reference: Record) -> Record:
    """Unique same-letter content and overlapping evidence, never ID equality."""
    mapping = {}
    for a in predicted["assertions"]:
        candidates = [
            b
            for b in reference["assertions"]
            if a["letter_id"] == b["letter_id"]
            and a["content"] == b["content"]
            and a["polarity"] == b["polarity"]
            and a["certainty"] == b["certainty"]
            and any(overlap(x, y) for x in a["evidence"] for y in b["evidence"])
        ]
        if len(candidates) == 1:
            mapping[a["assertion_id"]] = candidates[0]["assertion_id"]
    counts = Counter(mapping.values())
    mapping = {k: v for k, v in mapping.items() if counts[v] == 1}
    return {
        "mapping": mapping,
        "aligned_assertions": len(mapping),
        "predicted_assertions": len(predicted["assertions"]),
        "reference_assertions": len(reference["assertions"]),
    }


def link_comparison(predicted: Record, reference: Record, use_ids: bool = False) -> Record:
    aligned = alignment(predicted, reference)
    mapping = (
        {a["assertion_id"]: a["assertion_id"] for a in predicted["assertions"]}
        if use_ids
        else aligned["mapping"]
    )

    def key(link: Record, ids: Record) -> tuple | None:
        a, b = [ids.get(link[k]) for k in ("earlier_assertion", "later_assertion")]
        if a is None or b is None:
            return None
        if link["relation"] in ("same_pattern", "overlaps_active", "contradicts"):
            a, b = sorted((a, b))
        return a, b, link["relation"]

    identity = {a["assertion_id"]: a["assertion_id"] for a in reference["assertions"]}
    expected = {item for edge in reference["links"] if (item := key(edge, identity)) is not None}
    observed = {k for edge in predicted["links"] if (k := key(edge, mapping)) is not None}
    matches = len(observed & expected)
    ref_by_id = {a["assertion_id"]: a for a in reference["assertions"]}

    def equivalent(a: str, b: str) -> bool:
        if a == b:
            return True
        left, right = ref_by_id[a], ref_by_id[b]
        return left["content"]["family"] == right["content"]["family"] == "seizure" and related(
            left, right, reference["links"]
        )

    def supports(candidate: tuple, target: tuple) -> bool:
        a, b, relation = candidate
        c, d, target_relation = target
        if relation != target_relation:
            return False
        forward = equivalent(a, c) and equivalent(b, d)
        reverse = (
            relation in ("same_pattern", "overlaps_active", "contradicts")
            and equivalent(a, d)
            and equivalent(b, c)
        )
        return forward or reverse

    reference_supported = sum(
        any(supports(candidate, target) for target in expected)
        or (candidate[2] == "same_pattern" and equivalent(candidate[0], candidate[1]))
        for candidate in observed
    )
    recalled = sum(
        any(supports(candidate, target) for candidate in observed) for target in expected
    )
    return {
        **aligned,
        "matched_edges": matches,
        "reference_supported_edges": reference_supported,
        "reference_recalled_edges": recalled,
        "support_policy": "Same-letter overlapping evidence and reference seizure-identity paths "
        "allow equivalent endpoints. All unaligned predictions stay in precision's "
        "denominator. This measures provisional-reference support, not clinical truth.",
        "reference_edges": len(expected),
        "aligned_predicted_edges": len(observed),
        "predicted_edges": len(predicted["links"]),
        "unaligned_predicted_edges": sum(key(edge, mapping) is None for edge in predicted["links"]),
        "missing_reference_edges": sorted(expected - observed),
        "additional_aligned_edges": sorted(observed - expected),
        "interpretation": "Exact annotated-edge agreement; extra supported edges "
        "may be unannotated."
        " This is not adjudicated clinical link precision.",
    }


def summarize(rows: list[Record]) -> Record:
    groups = {}
    for dimension in ("variant", "dataset", "view", "query_id", "reference_status", "patient"):
        by_group: dict[str, list] = {}
        for row in rows:
            key = (
                str(row[dimension])
                if dimension == "variant"
                else (f"{row['variant']}/{row[dimension]}")
            )
            by_group.setdefault(key, []).append(row)
        groups[dimension] = {
            key: {
                "correct": sum(r["status"] == r["reference_status"] for r in group),
                "total": len(group),
                "failures": sum(r["status"] == "failed" for r in group),
                "unsupported_definitive": sum(
                    r["status"] in ("eligible", "ineligible")
                    and r["status"] != r["reference_status"]
                    for r in group
                ),
                "statuses": dict(Counter(r["status"] for r in group)),
            }
            for key, group in by_group.items()
        }
    return groups
