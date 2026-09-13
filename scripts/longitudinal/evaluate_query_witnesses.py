"""Conservative development witnesses for Q1-Q5; no text inference or reference lookup.

This deliberately incomplete evaluator measures structured-field dependencies.
Unimplemented negatives, qualitative time inclusion and graph traversal abstain.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.longitudinal.check_annotations import (  # noqa: E402
    evidence_overlap,
    grounded_span,
    load_example,
)
from scripts.longitudinal.evaluate_q5_slice import evaluate_q5, within_window  # noqa: E402


def covers(value: dict | None, first: str, last: str) -> bool:
    """Only an explicitly bounded active interval proves whole-period coverage."""
    if not value or value["kind"] != "active_interval":
        return False
    start, end = value.get("start") or {}, value.get("end") or {}
    return bool(
        start.get("latest")
        and end.get("earliest")
        and start["latest"] <= first <= last <= end["earliest"]
    )


def before(value: dict | None, last: str) -> bool:
    if not value:
        return False
    return bool((value.get("end") or {}).get("latest") and value["end"]["latest"] <= last)


def evaluate_query(annotations: dict, documents: dict, request: dict) -> dict:
    q, index, cutoff = request["query_id"], request["index_date"], request["information_cutoff"]
    for days in (90, 180):
        first = (date.fromisoformat(index) - timedelta(days=days - 1)).isoformat()
        if request[f"lookback_{days}_start"] != first:
            raise ValueError("Invalid fixed lookback")
    if cutoff < index:
        raise ValueError("Invalid cutoff")
    if q == "Q5":
        return evaluate_q5(annotations, documents, request)
    permitted = {
        k: d
        for k, d in documents.items()
        if d.get("available_date") and d["available_date"] <= cutoff
    }
    assertions = {
        a["assertion_id"]: a
        for a in annotations["assertions"]
        if a["letter_id"] in permitted
        and a["evidence"]
        and all(grounded_span(e, permitted) for e in a["evidence"])
        and (
            not a["time"]
            or not a["time"].get("anchor_letter_id")
            or a["time"]["anchor_letter_id"] in permitted
        )
    }
    links = [
        link
        for link in annotations["links"]
        if all(link[k] in assertions for k in ("earlier_assertion", "later_assertion"))
        and link["evidence"]
        and all(grounded_span(e, permitted) for e in link["evidence"])
    ]
    conflicted = {
        link[k]
        for link in links
        if link["relation"] == "contradicts"
        for k in ("earlier_assertion", "later_assertion")
    }
    # Split pattern/occurrence assertions can describe the same disputed account.
    # Block that same-letter, same-name, overlapping-evidence account too. This
    # conservative exclusion does not infer identity across letters or dates.
    conflict_scopes = [
        assertions[k] for k in conflicted if assertions[k]["content"]["family"] == "seizure"
    ]
    conflicted.update(
        a["assertion_id"]
        for a in assertions.values()
        if a["content"]["family"] == "seizure"
        and any(
            a["letter_id"] == b["letter_id"]
            and a["content"]["names"] == b["content"]["names"]
            and any(evidence_overlap(x, y) for x in a["evidence"] for y in b["evidence"])
            for b in conflict_scopes
        )
    )
    usable = {
        k: a
        for k, a in assertions.items()
        if k not in conflicted and a["certainty"] == "asserted" and a["polarity"] == "affirmed"
    }
    links = [
        link
        for link in links
        if link["certainty"] == "asserted"
        and all(link[k] in usable for k in ("earlier_assertion", "later_assertion"))
    ]
    positive, negative = [], []

    def add(
        target: list,
        items: list[dict],
        link: dict | None = None,
        extra_evidence: list[dict] | None = None,
    ) -> None:
        target.append(
            {
                "assertion_ids": [a["assertion_id"] for a in items],
                "link_ids": [link["link_id"]] if link else [],
                "evidence": [e for a in items for e in a["evidence"]]
                + (link["evidence"] if link else [])
                + (extra_evidence or []),
            }
        )

    a90, a180 = request["lookback_90_start"], request["lookback_180_start"]
    seizures = [a for a in usable.values() if a["content"]["family"] == "seizure"]
    # A reviewed correction excludes its earlier assertion. Other same-name mentions
    # are not silently propagated; complete identity traversal is outside this slice.
    corrected = {
        link["earlier_assertion"] for link in links if link["relation"] == "corrects_interpretation"
    }
    epileptic = [
        a
        for a in seizures
        if a["content"]["interpretation"] == "epileptic" and a["assertion_id"] not in corrected
    ]
    whole_absence = [
        a
        for a in epileptic
        if a["content"]["kind"] == "absence"
        and a["content"]["scope"] == "all_epileptic"
        and a["coverage"] == "complete"
        and covers(a["time"], a90, index)
    ]
    if q == "Q1":
        diagnoses = [
            a
            for a in usable.values()
            if a["content"]["family"] == "diagnosis"
            and a["content"]["phase"] == "current"
            and "epilepsy" in a["content"]["name"].casefold()
            and before(a["time"], index)
        ]
        events = [
            a
            for a in epileptic
            if a["content"]["kind"] in ("occurrence", "pattern")
            and within_window(a["time"], a90, index)
        ]
        if diagnoses:
            for event in events:
                add(positive, [diagnoses[-1], event])
        for absence in whole_absence:
            add(negative, [absence])
    elif q == "Q2":
        for link in links:
            if link["relation"] != "overlaps_active":
                continue
            pair = [usable[link[k]] for k in ("earlier_assertion", "later_assertion")]
            if all(a in epileptic and within_window(a["time"], a90, index) for a in pair):
                # The explicit overlap link supplies concurrency/identity evidence;
                # overlapping uncertainty envelopes alone would not suffice.
                add(positive, pair, link)
        for a in seizures:
            if (
                a["content"]["kind"] == "inventory"
                and a["content"]["scope"] == "all_epileptic"
                and a["content"]["interpretation"] == "epileptic"
                and a["coverage"] == "complete"
                and covers(a["time"], a90, index)
                and len(a["content"]["names"]) <= 1
            ):
                add(negative, [a])
        for absence in whole_absence:
            add(negative, [absence])
    elif q == "Q3":
        drug = request["parameters"]["medication"].casefold()
        for a in usable.values():
            c = a["content"]
            if c["family"] != "medication" or c["name"].casefold() != drug:
                continue
            if c["status"] == "started" and within_window(a["time"], a180, index):
                add(positive, [a])
            if c["status"] == "not_started" and a["coverage"] == "complete":
                prior = a.get("all_prior_history_evidence", [])
                entire_prior = bool(
                    prior
                    and all(grounded_span(e, permitted) for e in prior)
                    and a["time"]
                    and a["time"]["kind"] == "active_interval"
                    and (a["time"].get("end") or {}).get("earliest")
                    and a["time"]["end"]["earliest"] >= index
                )
                if entire_prior:
                    add(negative, [a], extra_evidence=prior)
                elif covers(a["time"], a180, index):
                    add(negative, [a])
                # An unknown start remains unknown without explicit prior-history evidence.
    elif q == "Q4":
        modality = request["parameters"]["modality"]
        for link in links:
            if link["relation"] != "request_has_result":
                continue
            a, b = [usable[link[k]] for k in ("earlier_assertion", "later_assertion")]
            if (
                a["content"]["family"] == b["content"]["family"] == "investigation"
                and a["content"]["modality"] == b["content"]["modality"] == modality
                and a["content"]["status"] == "requested"
                and b["content"]["status"] == "result"
                and within_window(a["time"], a180, index)
                and b["time"]
                and b["time"]["kind"] == "result_available"
                and before(b["time"], index)
            ):
                add(positive, [a, b], link)
    else:
        raise ValueError("Unknown query")
    status = (
        "indeterminate"
        if positive and negative
        else "eligible"
        if positive
        else "ineligible"
        if negative
        else "indeterminate"
    )
    return {
        "status": status,
        "witnesses": positive,
        "negative_witnesses": negative,
        "reason": "Conflicting witnesses"
        if positive and negative
        else "Structured witness"
        if positive or negative
        else "No implemented decisive witness; missing evidence or unsupported mechanism",
    }


def replay() -> dict:
    rows, hashes = [], {}
    variants = (
        "full",
        "without_links",
        "without_assertion_time",
        "without_decision_time",
        "without_first_reinterpretation_evidence",
        "without_evidence",
        "without_time_wording",
        "without_burden",
        "without_prior_history_evidence",
    )
    for case in sorted((ROOT / "examples/longitudinal").glob("authored_patient_*")):
        annotations, documents, _ = load_example(case)
        manifest = json.loads((case / "manifest.json").read_text())
        reference = {
            a["request_id"]: a["status"]
            for a in json.loads((case / "reference.json").read_text())["answers"]
        }
        for file in [
            case / n for n in ("annotations.json", "manifest.json", "reference.json")
        ] + list((case / "letters").glob("*.txt")):
            hashes[str(file.relative_to(ROOT))] = hashlib.sha256(file.read_bytes()).hexdigest()
        for variant in variants:
            changed = deepcopy(annotations)
            if variant == "without_links":
                changed["links"] = []
            for a in changed["assertions"]:
                if variant == "without_prior_history_evidence":
                    a.pop("all_prior_history_evidence", None)
                if variant == "without_assertion_time":
                    a["time"] = None
                if variant == "without_evidence":
                    a["evidence"] = []
                if variant == "without_time_wording" and a["time"]:
                    a["time"]["text"] = None
                if variant == "without_burden" and a["content"]["family"] == "seizure":
                    a["content"]["burden"] = None
            for link in changed["links"]:
                if variant == "without_decision_time":
                    link["decision_time"] = None
                if variant == "without_first_reinterpretation_evidence":
                    link.pop("first_reinterpretation_evidence", None)
                if variant == "without_time_wording" and link.get("decision_time"):
                    link["decision_time"]["text"] = None
            for request in manifest["requests"]:
                rows.append(
                    {
                        "case": case.name,
                        "request_id": request["request_id"],
                        "query": request["query_id"],
                        "view": request["view"],
                        "variant": variant,
                        "reference_status": reference[request["request_id"]],
                        **evaluate_query(changed, documents, request),
                    }
                )
    full = {(r["case"], r["request_id"]): r for r in rows if r["variant"] == "full"}
    summary = {}
    for variant in variants:
        summary[variant] = {}
        for q in ("Q1", "Q2", "Q3", "Q4", "Q5"):
            selected = [r for r in rows if r["variant"] == variant and r["query"] == q]
            summary[variant][q] = {
                "requests": len(selected),
                "reference_matches": sum(r["status"] == r["reference_status"] for r in selected),
                "changed_from_full": sum(
                    r["status"] != full[r["case"], r["request_id"]]["status"] for r in selected
                ),
                "status_counts": dict(Counter(r["status"] for r in selected)),
            }
    return {
        "dataset": "12 authored development patients; current versioned annotations",
        "split": "development_only",
        "model": None,
        "model_calls": 0,
        "repair_policy": "none",
        "scorer": "exact three-state match; 20 fixed requests per patient",
        "claim": "incomplete structured-witness development diagnostic; not model accuracy",
        "program_sha256": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (
                Path(__file__),
                ROOT / "scripts/longitudinal/evaluate_q5_slice.py",
                ROOT / "scripts/longitudinal/check_annotations.py",
            )
        },
        "input_sha256": hashes,
        "summary": summary,
        "rows": rows,
    }


if __name__ == "__main__":
    result = replay()
    path = ROOT / "results/longitudinal/pilot_v0.8/query_field_ablation.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["summary"], indent=2))
