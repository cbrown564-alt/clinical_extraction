"""Evidence-traced development rules for five longitudinal cohort questions.

No reference answers, case identifiers or model query answers enter this module.
Every clinical inference is attributed to a named rule in the returned witnesses.
"""

from __future__ import annotations

from datetime import date, timedelta

from .evidence import Record, grounded, overlap, unique_evidence, wording
from .temporal import before, bounds, covers, history_scope, holiday_inside, union_covers, within


def available_facts(annotations: Record, documents: Record, cutoff: str) -> tuple[Record, list]:
    permitted = {k: d for k, d in documents.items() if d["available_date"] <= cutoff}
    assertions = {
        a["assertion_id"]: a
        for a in annotations["assertions"]
        if a["letter_id"] in permitted
        and a["evidence"]
        and all(
            grounded(e, permitted)
            for e in (a["evidence"] + a.get("all_prior_history_evidence", []))
        )
        and ((a.get("time") or {}).get("anchor_letter_id") in (None, *permitted))
    }
    links = [
        link
        for link in annotations["links"]
        if all(link[k] in assertions for k in ("earlier_assertion", "later_assertion"))
        and link["evidence"]
        and all(
            grounded(e, permitted)
            for e in (link["evidence"] + link.get("first_reinterpretation_evidence", []))
        )
        and ((link.get("decision_time") or {}).get("anchor_letter_id") in (None, *permitted))
    ]
    return assertions, links


def related(a: Record, b: Record, links: list[Record]) -> bool:
    """Explicit identity path or co-located descriptions of the same account."""
    if a["assertion_id"] == b["assertion_id"]:
        return True
    if (
        a["letter_id"] == b["letter_id"]
        and a["content"].get("names") == b["content"].get("names")
        and any(overlap(x, y) for x in a["evidence"] for y in b["evidence"])
    ):
        return True
    seen = {a["assertion_id"]}
    while True:
        added = set()
        for link in links:
            if link["relation"] in ("same_pattern", "repeats", "corrects_interpretation"):
                ends = {link["earlier_assertion"], link["later_assertion"]}
                if seen & ends:
                    added |= ends - seen
        if not added:
            return b["assertion_id"] in seen
        seen |= added


def evaluate_query(annotations: Record, documents: Record, request: Record) -> Record:
    q, index = request["query_id"], request["index_date"]
    cutoff = request["information_cutoff"]
    if cutoff < index:
        raise ValueError("Information cutoff precedes index")
    for days in (90, 180):
        if (
            request[f"lookback_{days}_start"]
            != (date.fromisoformat(index) - timedelta(days=days - 1)).isoformat()
        ):
            raise ValueError("Invalid fixed inclusive lookback")
    if request["view"] == "visit" and cutoff != index:
        raise ValueError("Visit view must use the index cutoff")
    documents = {k: d for k, d in documents.items() if d["available_date"] <= cutoff}
    assertions, links = available_facts(annotations, documents, cutoff)
    conflict = {
        link[k]
        for link in links
        if link["relation"] == "contradicts"
        for k in ("earlier_assertion", "later_assertion")
    }
    conflict.update(
        a["assertion_id"]
        for a in assertions.values()
        if a["content"]["family"] == "seizure"
        and any(related(a, assertions[b], []) for b in list(conflict))
    )
    usable = {
        k: a for k, a in assertions.items() if k not in conflict and a["certainty"] == "asserted"
    }
    links = [
        edge
        for edge in links
        if edge["certainty"] == "asserted"
        and all(edge[k] in usable for k in ("earlier_assertion", "later_assertion"))
    ]
    positive: list[Record] = []
    negative: list[Record] = []

    def add(target: list, rule: str, items: list, used_links: list | None = None) -> None:
        used_links = used_links or []
        target.append(
            {
                "rule_id": rule,
                "assertion_ids": [a["assertion_id"] for a in items],
                "link_ids": [edge["link_id"] for edge in used_links],
                "evidence": unique_evidence(
                    [e for a in items for e in a["evidence"]]
                    + [e for edge in used_links for e in edge["evidence"]]
                    + [e for a in items for e in a.get("all_prior_history_evidence", [])]
                    + [
                        e
                        for edge in used_links
                        for e in edge.get("first_reinterpretation_evidence", [])
                    ]
                ),
            }
        )

    affirmed = [a for a in usable.values() if a["polarity"] == "affirmed"]
    seizures = [a for a in affirmed if a["content"]["family"] == "seizure"]
    corrections = [
        edge
        for edge in links
        if edge["relation"] == "corrects_interpretation"
        and usable[edge["earlier_assertion"]]["content"].get("interpretation") == "epileptic"
        and usable[edge["later_assertion"]]["content"].get("interpretation") == "non_epileptic"
    ]
    corrected = {
        a["assertion_id"]
        for a in seizures
        if any(related(a, usable[edge["earlier_assertion"]], links) for edge in corrections)
    }
    epileptic = [
        a
        for a in seizures
        if a["content"]["interpretation"] == "epileptic" and a["assertion_id"] not in corrected
    ]
    first90, first180 = request["lookback_90_start"], request["lookback_180_start"]
    # "No new types" is not absence of existing events. The names/wording check
    # prevents an all_reported schema scope from silently erasing a stable pattern.
    absences = [
        a
        for a in seizures
        if a["content"]["kind"] == "absence"
        and a["coverage"] == "complete"
        and a["content"]["scope"] in ("all_epileptic", "all_reported")
        and "new semiolog" not in wording(a)
        and "no new" not in wording(a)
        and (
            a["content"]["scope"] == "all_epileptic"
            or any(
                s in wording(a)
                for s in ("no events", "no further events", "no seizures", "seizure-free")
            )
        )
    ]

    if q == "Q1":
        diagnoses = [
            a
            for a in usable.values()
            if a["content"]["family"] == "diagnosis"
            and "epilepsy" in a["content"]["name"].casefold()
            and a["content"]["phase"] == "current"
            and before(a["time"], index)
        ]
        superseded = {
            edge["earlier_assertion"]
            for edge in links
            if edge["relation"] == "updates"
            and before(usable[edge["later_assertion"]]["time"], index)
        }
        active = [a for a in diagnoses if a["assertion_id"] not in superseded]
        for d in active:
            if d["polarity"] == "negated":
                add(
                    negative,
                    "Q1-diagnosis-explicitly-withdrawn",
                    [d],
                    [edge for edge in links if edge["later_assertion"] == d["assertion_id"]],
                )
            else:
                for event in epileptic:
                    if event["content"]["kind"] not in ("occurrence", "pattern"):
                        continue
                    bounded = within(event["time"], first90, index)
                    holiday = holiday_inside(event, documents, first90, index)
                    if bounded or holiday:
                        add(
                            positive,
                            "Q1-diagnosis-and-"
                            + ("bounded-event" if bounded else "qualitative-christmas-inclusion"),
                            [d, event],
                        )
        if union_covers(absences, first90, index):
            add(negative, "Q1-complete-event-absence", absences)
    elif q == "Q2":
        for link in links:
            if link["relation"] == "overlaps_active":
                pair = [usable[link[k]] for k in ("earlier_assertion", "later_assertion")]
                if all(a in epileptic and within(a["time"], first90, index) for a in pair):
                    add(positive, "Q2-distinct-overlapping-patterns", pair, [link])
        for inv in seizures:
            c = inv["content"]
            if c["kind"] != "inventory" or inv["coverage"] != "complete":
                continue
            if c["scope"] not in ("all_epileptic", "all_reported"):
                continue
            scope = history_scope(inv, documents, first90, index)
            names = c["names"]
            removed, support = set(), []
            for name in names:
                matching = [
                    a
                    for a in seizures
                    if a["content"]["names"] == [name] and a["content"]["kind"] != "inventory"
                ]
                corrected_mentions = [a for a in matching if a["assertion_id"] in corrected]
                # A known pattern's explicit complete absence covers the full window.
                absent = [
                    a
                    for a in matching
                    if a["content"]["kind"] == "absence"
                    and a["coverage"] == "complete"
                    and covers(a["time"], first90, index)
                ]
                if corrected_mentions or absent:
                    removed.add(name)
                    support += corrected_mentions + absent
            if len(set(names) - removed) <= 1 and scope:
                add(negative, f"Q2-{scope}", [inv, *support], corrections if support else [])
            # A complete elicited inventory at T plus a linked correction and
            # whole-window exclusions accounts for every named alternative.
            elif (
                len(set(names) - removed) <= 1
                and removed
                and corrections
                and before(inv["time"], index)
                and bounds(inv["time"])[1] == index
                and "no other event types" in wording(inv)
            ):
                add(
                    negative,
                    "Q2-complete-inventory-linked-exclusions",
                    [inv, *support],
                    corrections,
                )
        if union_covers(absences, first90, index):
            add(negative, "Q2-complete-event-absence", absences)
    elif q == "Q3":
        drug = request["parameters"]["medication"].casefold()
        meds = [
            a
            for a in affirmed
            if a["content"]["family"] == "medication" and a["content"]["name"].casefold() == drug
        ]
        for a in meds:
            c = a["content"]
            if c["status"] == "started" and within(a["time"], first180, index):
                add(positive, "Q3-confirmed-start", [a])
            if c["status"] == "not_started" and a["coverage"] == "complete":
                prior = a.get("all_prior_history_evidence", [])
                end = ((a.get("time") or {}).get("end") or {}).get("earliest", "")
                if covers(a["time"], first180, index) or (
                    prior and end >= index and all(grounded(e, documents) for e in prior)
                ):
                    add(negative, "Q3-complete-no-initiation-history", [a])
        starts = [
            a
            for a in meds
            if a["content"]["status"] == "started"
            and before(a["time"], first180)
            and bounds(a["time"])[1] != first180
        ]
        for start in starts:
            # Explicit titration, reliable continuation and later adherence must
            # describe the same named course. A generic "unchanged" is insufficient.
            early = [
                a
                for a in meds
                if a["content"]["status"] == "taking"
                and before(a["time"], index)
                and "continues to take reliably" in wording(a)
                and "titrated" in wording(a)
            ]
            later = [
                a
                for a in meds
                if a["content"]["status"] == "taking"
                and bounds(a["time"])[0]
                and bounds(a["time"])[0] >= index
                and "remains compliant" in wording(a)
            ]
            interruptions = [
                a
                for a in meds
                if a["content"]["status"] in ("stopped", "not_started")
                or (a["content"]["status"] == "started" and a is not start)
            ]
            if early and later and not interruptions:
                add(
                    negative,
                    "Q3-explicit-continuous-prewindow-course",
                    [start, early[-1], later[0]],
                )
    elif q == "Q4":
        modality = request["parameters"]["modality"].casefold()
        studies = [
            a
            for a in affirmed
            if a["content"]["family"] == "investigation"
            and a["content"]["modality"].casefold() == modality
        ]
        requests = [
            a
            for a in studies
            if a["content"]["status"] == "requested" and within(a["time"], first180, index)
        ]
        for link in links:
            if link["relation"] != "request_has_result":
                continue
            a, b = [usable[link[k]] for k in ("earlier_assertion", "later_assertion")]
            if (
                a in requests
                and b in studies
                and b["content"]["status"] == "result"
                and (b["time"] or {}).get("kind") == "result_available"
                and before(b["time"], index)
            ):
                add(positive, "Q4-matched-clinically-available-result", [a, b], [link])
        for inv in studies:
            if not (
                inv["content"]["status"] == "request_inventory"
                and inv["coverage"] == "complete"
                and covers(inv["time"], first180, index)
            ):
                continue
            count = inv["content"]["request_count"]
            if count == 0:
                add(negative, "Q4-complete-zero-requests", [inv])
            elif count == len(requests):
                unresolved, evidence, used = 0, [inv], []
                for req in requests:
                    pending = [
                        a
                        for a in studies
                        if a["content"]["status"] in ("pending", "cancelled")
                        and bounds(a["time"])[1] == index
                        and any(overlap(x, y) for x in a["evidence"] for y in req["evidence"])
                    ]
                    late_links = [
                        edge
                        for edge in links
                        if edge["relation"] == "request_has_result"
                        and edge["earlier_assertion"] == req["assertion_id"]
                        and (bounds(usable[edge["later_assertion"]]["time"])[0] or "") > index
                    ]
                    if pending or late_links:
                        unresolved += 1
                        evidence += [
                            req,
                            *pending,
                            *[usable[edge["later_assertion"]] for edge in late_links],
                        ]
                        used += late_links
                if unresolved == count:
                    add(negative, "Q4-complete-requests-without-result-by-index", evidence, used)
    elif q == "Q5":
        for link in corrections:
            decision = link.get("decision_time") or {}
            start, end = bounds(decision)
            if decision.get("kind") != "decision" or not start or not end:
                continue
            pair = [usable[link[k]] for k in ("earlier_assertion", "later_assertion")]
            first_evidence = link.get("first_reinterpretation_evidence", [])
            if (
                start > index
                and first_evidence
                and all(grounded(e, documents) for e in first_evidence)
            ):
                add(negative, "Q5-first-patient-reinterpretation-after-index", pair, [link])
            if end <= index:
                events = [
                    a
                    for a in seizures
                    if a["content"]["kind"] in ("pattern", "occurrence")
                    and any(related(a, b, links) for b in pair)
                    and within(a["time"], first180, index)
                ]
                if events:
                    add(
                        positive,
                        "Q5-linked-event-and-dated-reinterpretation",
                        [*pair, *events],
                        [link],
                    )
        # An event during the window is necessary. Complete all-event absence
        # therefore refutes Q5 without assuming anything about unrecorded reviews.
        all_events = [a for a in absences if a["content"]["scope"] == "all_reported"]
        if union_covers(all_events, first180, index):
            add(negative, "Q5-complete-all-event-absence", all_events)
    else:
        raise ValueError(f"Unknown query {q}")
    status = (
        "indeterminate"
        if positive and negative
        else "eligible"
        if positive
        else "ineligible"
        if negative
        else "indeterminate"
    )
    reason = (
        "Positive and negative evidence conflict; review the source accounts."
        if positive and negative
        else "Evidence supports every required condition."
        if positive
        else "Explicit evidence refutes a required condition."
        if negative
        else "The available evidence does not establish eligibility or a complete exclusion."
    )
    return {
        "status": status,
        "reason": reason,
        "witnesses": positive,
        "negative_witnesses": negative,
        "evidence": unique_evidence([e for w in positive + negative for e in w["evidence"]]),
        "rule_ids": sorted({w["rule_id"] for w in positive + negative}),
        "conflicted_assertion_ids": sorted(conflict),
    }
