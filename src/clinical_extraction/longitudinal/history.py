"""Deterministic, evidence-cued linking with immutable source assertions."""

from __future__ import annotations

import re
from datetime import datetime
from itertools import combinations

from .evidence import Record, overlap, source_paragraphs, unique_evidence, wording
from .temporal import bounds, interval

MONTHS = "January February March April May June July August September October November December"
DATE = re.compile(r"\b(\d{1,2}) (" + "|".join(MONTHS.lower().split()) + r")(?: (20\d{2}))?\b")


def decision_time(a: Record, documents: Record) -> Record | None:
    text = wording(a)
    visit = documents[a["letter_id"]]["visit_date"]
    # Match the dated review/decision clause; never use an occurrence date merely
    # because it appears in the correction paragraph.
    match = re.search(
        r"(?:at the review on|the review of|decided on|reinterpreted on|"
        r"reclassified on|on review today,) "
        r"(\d{1,2} [a-z]+(?: 20\d{2})?)",
        text,
    )
    found = DATE.search(match.group(1)) if match else None
    value = None
    if found:
        day, month, year = found.groups()
        try:
            value = (
                datetime.strptime(f"{day} {month} {year or visit[:4]}", "%d %B %Y")
                .date()
                .isoformat()
            )
        except ValueError:
            return None
    elif short := re.search(r"(\d{1,2} [a-z]{3} 20\d{2}) review:", text):
        try:
            value = datetime.strptime(short.group(1), "%d %b %Y").date().isoformat()
        except ValueError:
            return None
    elif re.search(
        r"(?:today.*(?:reclassif|reinterpret|decid|diagnose)|(?:reclassif|reinterpret).*today)",
        text,
    ):
        value = visit
    if value is None:
        return None
    return {
        "kind": "decision",
        "start": {"earliest": value, "latest": value},
        "end": {"earliest": value, "latest": value},
        "text": match.group(0) if match else "today",
        "anchor_letter_id": a["letter_id"],
    }


def link_assertions(assertions: list[Record], documents: Record) -> list[Record]:
    """Infer from permitted facts only; no annotation links or reference answers.

    Equal names nominate candidates. An explicit continuity/correction cue is also
    required. Ambiguous investigations and uncertain source accounts abstain.
    """
    ordered = sorted(
        assertions,
        key=lambda a: (
            documents[a["letter_id"]]["available_date"],
            a["letter_id"],
            a["evidence"][0]["start"],
            a["assertion_id"],
        ),
    )
    links: list[Record] = []

    def add(
        a: Record,
        b: Record,
        relation: str,
        evidence: list | None = None,
        decision: Record | None = None,
    ) -> None:
        key = f"{a['assertion_id']}__{b['assertion_id']}__{relation}"
        if any(edge["link_id"] == key for edge in links):
            return
        link = {
            "link_id": key,
            "earlier_assertion": a["assertion_id"],
            "later_assertion": b["assertion_id"],
            "relation": relation,
            "certainty": "asserted",
            "evidence": unique_evidence(evidence or (a["evidence"] + b["evidence"])),
            "decision_time": decision,
            "rule_id": "link-" + relation.replace("_", "-"),
        }
        if (
            relation == "corrects_interpretation"
            and re.search(r"first.*(?:change|reinterpretation|reclassif)", wording(b))
            and re.search(r"(?:record|history|anywhere|patient)", wording(b))
        ):
            link["first_reinterpretation_evidence"] = b["evidence"]
        if relation == "corrects_interpretation":
            # Adjacent first-ever statements must be in the correction's own
            # source paragraph, and become explicit additional link evidence.
            for span in source_paragraphs(b, documents):
                if re.search(
                    r"first (?:reclassification of any|change.*history|"
                    r".*reinterpretation.*history)",
                    span["text"].casefold(),
                ):
                    link["first_reinterpretation_evidence"] = [span]
                    link["evidence"] = unique_evidence(link["evidence"] + [span])
        links.append(link)

    for i, b in enumerate(ordered):
        cb, text = b["content"], wording(b)
        if b["certainty"] != "asserted":
            continue
        earlier = [a for a in ordered[:i] if a["certainty"] == "asserted"]
        if cb["family"] == "seizure" and cb["kind"] in ("pattern", "occurrence"):
            candidates = [
                a
                for a in earlier
                if a["content"]["family"] == "seizure"
                and a["content"]["kind"] in ("pattern", "occurrence")
                and a["content"]["names"] == cb["names"]
            ]
            for a in candidates:
                ca = a["content"]
                shared = any(overlap(x, y) for x in a["evidence"] for y in b["evidence"])
                if a["letter_id"] == b["letter_id"] and shared:
                    add(a, b, "same_pattern")
                elif (
                    a["letter_id"] != b["letter_id"]
                    and ca["interpretation"] == "epileptic"
                    and cb["interpretation"] == "non_epileptic"
                    and re.search(r"(?:same|those|previous|including|reclassif|reinterpret)", text)
                    and re.search(
                        r"(?:reclassif|reinterpret|corrects|no longer|non-epileptic)", text
                    )
                ):
                    add(a, b, "corrects_interpretation", decision=decision_time(b, documents))
                elif a["letter_id"] != b["letter_id"] and (
                    "copied" in text or "carried forward" in text or "carried-forward" in text
                ):
                    add(a, b, "repeats")
                elif a["letter_id"] != b["letter_id"] and re.search(
                    r"\b(?:same|continues?|remain\w*|further|another|unchanged|recurr\w*)\b", text
                ):
                    add(a, b, "same_pattern")
            # Different reporters' directly overlapping accounts remain disputed.
            for a in earlier:
                if (
                    a["content"]["family"] == "seizure"
                    and a["content"].get("names") == cb["names"]
                    and a["reporter"] != b["reporter"]
                    and (
                        a["polarity"] != b["polarity"]
                        or a["content"].get("kind") == "absence" != cb["kind"]
                    )
                    and bounds(a["time"]) == bounds(b["time"])
                ):
                    add(a, b, "contradicts")
        elif cb["family"] == "diagnosis":
            candidates = [
                a
                for a in earlier
                if a["content"]["family"] == "diagnosis"
                and a["content"]["name"] == cb["name"]
                and a["letter_id"] != b["letter_id"]
            ]
            if candidates and re.search(r"withdrawn|corrects|revised|remains|unchanged", text):
                add(candidates[-1], b, "updates")
        elif cb["family"] == "investigation" and cb["status"] in ("performed", "result"):
            requests = [
                a
                for a in earlier
                if a["content"]["family"] == "investigation"
                and a["content"]["modality"] == cb["modality"]
                and a["content"]["status"] == "requested"
            ]
            explicit = []
            for a in requests:
                start, end = bounds(a["time"])
                if start and start == end:
                    dt = datetime.fromisoformat(start)
                    literal = f"{dt.day} {dt.strftime('%B').lower()}"
                    if re.search(r"requested on " + re.escape(literal) + r"\b", text):
                        explicit.append(a)
            candidates = explicit or requests
            if len(candidates) == 1 and re.search(r"requested|same eeg|its report|that.*eeg", text):
                add(
                    candidates[0],
                    b,
                    "request_has_result" if cb["status"] == "result" else "request_performed",
                )
        elif cb["family"] == "medication":
            candidates = [
                a
                for a in earlier
                if a["content"]["family"] == "medication" and a["content"]["name"] == cb["name"]
            ]
            if candidates:
                if cb["status"] == "not_started" and re.search(r"never|did not|not started", text):
                    plans = [
                        a
                        for a in candidates
                        if a["content"]["status"] in ("proposed", "conditional", "prescribed")
                    ]
                    if plans:
                        add(plans[-1], b, "plan_not_enacted")
                elif re.search(r"continues?|remains|started|initiated|stopped", text):
                    add(candidates[-1], b, "updates")
    # A whole-patient denial can conflict with a named event; equal names are
    # not required when the source explicitly identifies the disputed account.
    for a, b in combinations(ordered, 2):
        if not (
            a["letter_id"] == b["letter_id"]
            and a["reporter"] != b["reporter"]
            and a["content"]["family"] == b["content"]["family"] == "seizure"
            and "absence" in (a["content"]["kind"], b["content"]["kind"])
        ):
            continue
        contexts = [
            span
            for span in source_paragraphs(a, documents)
            if any(overlap(span, other) for other in b["evidence"])
        ]
        text = wording(a) + wording(b) + " ".join(e["text"].casefold() for e in contexts)
        if any(
            term in text
            for term in (
                "discordance",
                "disput",
                "specifically denies",
                "discrepancy",
                "denies caregiver",
            )
        ):
            add(a, b, "contradicts", a["evidence"] + b["evidence"] + contexts)
    patterns = [
        a
        for a in ordered
        if a["content"]["family"] == "seizure"
        and a["content"]["kind"] in ("pattern", "occurrence")
        and a["certainty"] == "asserted"
        and a["polarity"] == "affirmed"
    ]
    for a, b in combinations(patterns, 2):
        if a["letter_id"] != b["letter_id"] or a["content"]["names"] == b["content"]["names"]:
            continue
        ia = interval(a["time"]) or (
            bounds(a["time"]) if a["time"]["kind"] == "occurrence" else None
        )
        ib = interval(b["time"]) or (
            bounds(b["time"]) if b["time"]["kind"] == "occurrence" else None
        )
        if not ia or not ib or not all((*ia, *ib)):
            continue
        a_start, a_end, b_start, b_end = ia[0], ia[1], ib[0], ib[1]
        if a_start is None or a_end is None or b_start is None or b_end is None:
            continue
        if max(a_start, b_start) > min(a_end, b_end):
            continue
        # Separate names and active intervals need explicit distinct/concurrent
        # wording; overlapping uncertainty envelopes alone are insufficient.
        paragraph = wording(a) + " " + wording(b)
        if re.search(r"both|distinct|separate|two patterns", paragraph):
            add(a, b, "overlaps_active")
    return links


def assemble_history(assertions: list[Record], links: list[Record]) -> list[Record]:
    """Group supported identity links; retain all source accounts and disagreements."""
    groups = [{a["assertion_id"]} for a in assertions]
    for link in links:
        if link["relation"] not in (
            "same_pattern",
            "repeats",
            "corrects_interpretation",
            "updates",
            "request_performed",
            "request_has_result",
            "plan_not_enacted",
        ):
            continue
        ends = {link["earlier_assertion"], link["later_assertion"]}
        joined = set().union(*(g for g in groups if g & ends))
        groups = [g for g in groups if not g & ends] + [joined]
    by_id = {a["assertion_id"]: a for a in assertions}
    return [
        {
            "assertion_ids": sorted(g),
            "accounts": [by_id[k] for k in sorted(g)],
            "links": [
                edge
                for edge in links
                if edge["earlier_assertion"] in g or edge["later_assertion"] in g
            ],
        }
        for g in groups
    ]
