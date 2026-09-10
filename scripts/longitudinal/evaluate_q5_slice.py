"""Development Q5 evaluator with explicit first-reinterpretation evidence."""

from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.longitudinal.check_annotations import grounded_span, load_example  # noqa: E402


def within_window(value: dict | None, first: str, last: str) -> bool:
    """Require a bounded occurrence or a definitely overlapping active interval."""
    if not value or value.get("kind") not in ("occurrence", "active_interval"):
        return False
    start, end = value.get("start") or {}, value.get("end") or {}
    if value["kind"] == "occurrence":
        return bool(
            start.get("earliest")
            and end.get("latest")
            and first <= start["earliest"] <= end["latest"] <= last
        )
    return bool(
        start.get("latest")
        and end.get("earliest")
        and start["latest"] <= end["earliest"]
        and start["latest"] <= last
        and end["earliest"] >= first
    )


def evaluate_q5(annotations: dict, documents: dict, request: dict) -> dict:
    """Evaluate schema-valid development annotations; explicit conflicts abstain."""
    index, cutoff = request["index_date"], request["information_cutoff"]
    first = (date.fromisoformat(index) - timedelta(days=179)).isoformat()
    if request["query_id"] != "Q5" or request["lookback_180_start"] != first:
        raise ValueError("Q5 requires the fixed 180-day window")
    if cutoff < index:
        raise ValueError("Information cutoff precedes index")
    permitted = {k: d for k, d in documents.items() if d["available_date"] <= cutoff}
    assertions = {
        a["assertion_id"]: a for a in annotations["assertions"] if a["letter_id"] in permitted
    }
    # This slice conservatively abstains on explicit unresolved endpoint conflicts;
    # it does not implement conflict-resolution traversal.
    conflicted = {
        endpoint
        for link in annotations["links"]
        if link["relation"] == "contradicts"
        and all(link[k] in assertions for k in ("earlier_assertion", "later_assertion"))
        and link["evidence"]
        and all(grounded_span(e, permitted) for e in link["evidence"])
        for endpoint in (link["earlier_assertion"], link["later_assertion"])
    }
    witnesses = []
    negative_witnesses = []
    for link in annotations["links"]:
        if link["relation"] != "corrects_interpretation" or link["certainty"] != "asserted":
            continue
        earlier = assertions.get(link["earlier_assertion"])
        later = assertions.get(link["later_assertion"])
        if link["earlier_assertion"] in conflicted or link["later_assertion"] in conflicted:
            continue
        if not earlier or not later:
            continue
        if any(
            a["certainty"] != "asserted"
            or a["polarity"] != "affirmed"
            or a["content"]["family"] != "seizure"
            for a in (earlier, later)
        ):
            continue
        if (earlier["content"]["interpretation"], later["content"]["interpretation"]) != (
            "epileptic",
            "non_epileptic",
        ):
            continue
        evidence = earlier["evidence"] + later["evidence"] + link["evidence"]
        if not all(a["evidence"] for a in (earlier, later)) or not link["evidence"]:
            continue
        if not all(grounded_span(e, permitted) for e in evidence):
            continue
        decision = link.get("decision_time") or {}
        start, end = decision.get("start") or {}, decision.get("end") or {}
        if (
            decision.get("kind") != "decision"
            or not start.get("earliest")
            or not end.get("latest")
            or not start["earliest"] <= end["latest"]
        ):
            continue
        first_evidence = link.get("first_reinterpretation_evidence", [])
        if (
            start["earliest"] > index
            and first_evidence
            and all(grounded_span(e, permitted) for e in first_evidence)
        ):
            negative_witnesses.append({"link_id": link["link_id"], "evidence": first_evidence})
        if end["latest"] > index:
            continue
        # The correction can explicitly extend the same pattern's occurrence history.
        if not any(within_window(a["time"], first, index) for a in (earlier, later)):
            continue
        witnesses.append(
            {
                "link_id": link["link_id"],
                "assertion_ids": [earlier["assertion_id"], later["assertion_id"]],
                "evidence": evidence,
            }
        )
    status = (
        "indeterminate"
        if witnesses and negative_witnesses
        else "eligible"
        if witnesses
        else "ineligible"
        if negative_witnesses
        else "indeterminate"
    )
    return {
        "status": status,
        "negative_witnesses": negative_witnesses,
        "witnesses": witnesses,
        "reason": "Conflicting positive and first-reinterpretation evidence"
        if witnesses and negative_witnesses
        else "Supported same-pattern correction with occurrence and decision in scope"
        if witnesses
        else "Explicit first patient reinterpretation is after index"
        if negative_witnesses
        else "No positive witness or supported complete negative history",
    }


def replay() -> dict:
    case = ROOT / "examples/longitudinal/authored_patient_001"
    annotations, documents, _ = load_example(case)
    manifest = json.loads((case / "manifest.json").read_text())
    reference = {
        a["request_id"]: a for a in json.loads((case / "reference.json").read_text())["answers"]
    }
    rows = []
    for variant in (
        "full",
        "without_correction_links",
        "without_decision_time",
        "without_time_wording",
        "without_first_reinterpretation_evidence",
    ):
        changed = deepcopy(annotations)
        if variant == "without_correction_links":
            changed["links"] = [
                x for x in changed["links"] if x["relation"] != "corrects_interpretation"
            ]
        elif variant == "without_decision_time":
            for link in changed["links"]:
                link["decision_time"] = None
        elif variant == "without_first_reinterpretation_evidence":
            for link in changed["links"]:
                link.pop("first_reinterpretation_evidence", None)
        elif variant == "without_time_wording":
            for a in changed["assertions"]:
                if a["time"]:
                    a["time"]["text"] = None
            for link in changed["links"]:
                if link["decision_time"]:
                    link["decision_time"]["text"] = None
        for request in manifest["requests"]:
            if request["query_id"] == "Q5":
                rows.append(
                    {
                        "variant": variant,
                        "request_id": request["request_id"],
                        "reference_status": reference[request["request_id"]]["status"],
                        **evaluate_q5(changed, documents, request),
                    }
                )
    return {
        "scope": "patient 001, four Q5 requests, authored development annotations",
        "evaluator": "positive witness plus explicit first-patient-reinterpretation negative",
        "semantic_rule_family": "longitudinal_epilepsy_Q5",
        "model_calls": 0,
        "raw_output_repair": False,
        "program_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "input_sha256": {
            name: hashlib.sha256((case / name).read_bytes()).hexdigest()
            for name in ("annotations.json", "manifest.json", "reference.json")
        },
        "rows": rows,
    }


if __name__ == "__main__":
    result = replay()
    path = ROOT / "results/longitudinal/pilot_v0.6/q5_field_ablation.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    for row in result["rows"]:
        print(row["variant"], row["request_id"], row["status"], row["reference_status"])
