"""Apply 24 September owner decisions to the versioned dev750 compact candidate.

The source-bearing v0.2 candidate is immutable. This overlay preserves every
legacy claim and its original record; it changes only attributed review choices.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path("runs/seizure_finding_annotation_compact_v0_1/dev750")
BASE = ROOT / "candidate_v0_2_zero_primary_audit_reviewed.json"
OUTPUT = ROOT / "candidate_v0_3_owner_adjudicated.json"
EXPECTED_BASE_SHA256 = "c9cf6790cbe7ffd7979589101f6448e34b396af7ceb862ac80fba6c9ec7985ca"

REVIEW_IDS = {
    "891",
    "959",
    "960",
    "1597",
    "1640",
    "1706",
    "1707",
    "1880",
    "1979",
    "1980",
    "2459",
    "2678",
    "2759",
    "2932",
    "3082",
    "3242",
    "3262",
    "3281",
    "4496",
    "5567",
    "6077",
    "6094",
    "8577",
    "9002",
    "12484",
    "12502",
    "12506",
    "12537",
    "12548",
    "12551",
    "12556",
    "12562",
    "12573",
    "12584",
    "12641",
    "12665",
    "12667",
    "12676",
    "12679",
    "12749",
    "12751",
    "12882",
    "13149",
    "13209",
    "14025",
    "14076",
    "14187",
    "14282",
    "14540",
    "14645",
    "14765",
    "14810",
    "14821",
    "15168",
    "15193",
    "15267",
    "15429",
    "15497",
    "15519",
    "15672",
    "15771",
    "15965",
    "16097",
    "16674",
}

CONTRADICTION_IDS = {
    "12502",
    "12506",
    "12537",
    "12548",
    "12551",
    "12556",
    "12562",
    "12573",
    "12584",
    "12641",
    "12665",
    "12667",
    "12676",
    "12679",
    "12749",
    "12751",
}
LITERAL_TIME_IDS = {
    "1880",
    "2459",
    "2759",
    "2932",
    "3082",
    "5567",
    "6077",
    "9002",
    "13209",
    "14025",
    "14076",
    "14540",
    "14645",
    "14765",
    "14810",
    "14821",
    "16674",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one_sentence(note: str, phrase: str) -> str:
    for sentence in re.split(r"(?<=[.!?])\s+", note):
        if phrase in sentence:
            return sentence.strip()
    raise ValueError(f"Source phrase absent: {phrase}")


def audit(row: dict[str, Any], decision: str, reason: str) -> None:
    row.setdefault("owner_adjudications", []).append(
        {"decision": decision, "reason": reason, "date": "2026-09-24"}
    )


def claim(row: dict[str, Any], legacy_id: str) -> dict[str, Any]:
    return next(c for c in row["claims"] if c["legacy_id"] == legacy_id)


def add(row: dict[str, Any], key: str, candidate: dict[str, Any], reason: str) -> None:
    if any(c.get("id") == key for c in row.get("added_claims", [])):
        raise ValueError(f"Duplicate owner addition: {row['source_id']}/{key}")
    row.setdefault("added_claims", []).append(
        {
            "id": key,
            "disposition": "primary",
            "candidate": candidate,
            "source": "owner_adjudication_2026_09_24",
            "proposal_sha256": EXPECTED_BASE_SHA256,
            "decision_index": 1000 + int(row["source_id"]),
            "quotation": candidate["evidence"][0],
            "decision_evidence": candidate["evidence"],
            "decision_reason": reason,
            "overlap_legacy_ids": [],
        }
    )
    audit(row, key, reason)


def monthly(row: dict[str, Any], tonic_id: str, cluster_id: str) -> None:
    sentence = one_sentence(row["note"], "these occur roughly once a month")
    tonic = claim(row, tonic_id)
    tonic["candidate"]["measurement"] = {
        "kind": "rate",
        "quantity": {"kind": "verbatim", "text": "roughly once"},
        "per": {"kind": "number", "value": 1, "unit": "month"},
    }
    tonic["edit_reason"] = (
        "Owner: the monthly phrase applies separately to tonic seizures and "
        "myoclonic clusters; preserve their distinct counted units."
    )
    clusters = claim(row, cluster_id)
    clusters["disposition"] = "primary"
    clusters["candidate"] = {
        "event": {"scope": "named", "label": "clusters of myoclonic jerks"},
        "counted_unit": "cluster",
        "status": "stated",
        "measurement": {
            "kind": "cluster",
            "cadence": {
                "kind": "rate",
                "quantity": {"kind": "verbatim", "text": "roughly once"},
                "per": {"kind": "number", "value": 1, "unit": "month"},
            },
        },
        "time": {"phase": "ongoing"},
        "evidence": [sentence],
    }
    clusters["edit_reason"] = "Owner: monthly cadence also measures myoclonic clusters."
    audit(row, "monthly_both", "Apply monthly cadence to both named populations separately.")


def maximum_gap(row: dict[str, Any], weeks: int, phrase: str) -> None:
    sentence = one_sentence(row["note"], phrase)
    if any(
        c.get("candidate", {}).get("measurement", {}).get("kind") == "seizure_free"
        and c.get("candidate", {}).get("restriction", "").startswith(("longest", "maximum"))
        for c in row.get("added_claims", [])
    ):
        raise ValueError(f"Duplicate maximum gap: {row['source_id']}")
    add(
        row,
        f"owner_max_gap_{row['source_id']}",
        {
            "event": {"scope": "unspecified", "label": "seizures"},
            "counted_unit": "not_applicable",
            "status": "stated",
            "measurement": {
                "kind": "seizure_free",
                "duration": {"kind": "number", "value": weeks, "unit": "week"},
            },
            "time": {"phase": "past_or_unclear", "source": phrase},
            "evidence": [sentence],
            "restriction": phrase,
        },
        "Owner-approved literal maximum gap; subtype and timing are not inferred.",
    )


def apply(result: dict[str, Any]) -> None:
    rows = {row["source_id"]: row for row in result["rows"]}
    if len(REVIEW_IDS) != 64:
        raise ValueError("Owner review source coverage changed")
    if REVIEW_IDS != {
        row["source_id"] for row in result["rows"] if row["annotation_state"] == "needs_review"
    }:
        raise ValueError("Owner review does not match unresolved base rows")

    # Exact source meanings resolved directly in the owner conversation.
    for sid in ("959", "960"):
        c = claim(rows[sid], "f1")
        c["candidate"] = copy.deepcopy(c["original_record"]["candidate"])
        c["candidate"]["time"]["phase"] = "ongoing"
        c["edit_reason"] = "Owner: bimonthly means once every two months."
        audit(rows[sid], "bimonthly", "Once every two months; no reciprocal guess remains.")

    for sid in ("1597", "1640"):
        audit(
            rows[sid],
            "separate_named_counts",
            "Keep absence and petit-mal counts separately; do not sum or deduplicate.",
        )

    r = rows["1706"]
    add(
        r,
        "owner_cluster_1706",
        {
            "event": {"scope": "unspecified", "label": "cluster of short events"},
            "counted_unit": "cluster",
            "status": "stated",
            "measurement": {"kind": "cluster", "count": {"kind": "number", "value": 1}},
            "time": {"phase": "ongoing", "source": "over the past month"},
            "evidence": [
                one_sentence(r["note"], "Over the past month, the patient reports a cluster")
            ],
            "restriction": "on multiple days",
        },
        "Owner: Present Seizure Frequency heading links this cluster to seizure activity.",
    )

    r = rows["1707"]
    add(
        r,
        "owner_cluster_1707",
        {
            "event": {"scope": "unspecified", "label": "cluster of reduced-awareness events"},
            "counted_unit": "cluster",
            "status": "uncertain",
            "measurement": {"kind": "cluster", "count": {"kind": "number", "value": 1}},
            "time": {"phase": "ongoing", "source": "within the past week"},
            "evidence": [
                one_sentence(
                    r["note"], "Since the last review, the patient describes a brief cluster"
                )
            ],
            "restriction": "on multiple days",
        },
        "Owner: include as a possible-seizure cluster, retaining uncertain status.",
    )

    r = rows["8577"]
    add(
        r,
        "owner_diary_absence_8577",
        {
            "event": {"scope": "named", "label": "possible seizure events or auras"},
            "counted_unit": "not_applicable",
            "status": "uncertain",
            "measurement": {"kind": "seizure_free", "since": "09 March 2024"},
            "time": {"phase": "ongoing", "source": "since 09 March 2024"},
            "evidence": [one_sentence(r["note"], "app export reviewed today shows no entries")],
            "restriction": "seizure diary app entries",
        },
        "Owner: count anchored possible-event or aura entries, not global clinical freedom.",
    )

    r = rows["10873"]
    c = claim(r, "f1")
    c["disposition"] = "primary"
    c["candidate"] = {
        "event": {"scope": "unspecified", "label": "clusters of possible seizures"},
        "counted_unit": "cluster",
        "status": "uncertain",
        "measurement": {
            "kind": "cluster",
            "cadence": {
                "kind": "rate",
                "quantity": {"kind": "number", "value": 1},
                "per": {"kind": "number", "value": 1, "unit": "week"},
            },
            "seizures_per_cluster": {"kind": "bound", "relation": "at_least", "value": 6},
        },
        "time": {"phase": "ongoing"},
        "evidence": [one_sentence(r["note"], "Weekly clusters, usually 6 or more events")],
    }
    c["edit_reason"] = "Owner: weekly clusters of possible seizures with at least six events each."
    audit(r, "possible_weekly_clusters", c["edit_reason"])

    claim(rows["1979"], "f2")["disposition"] = "context"
    claim(rows["1979"], "f2")["edit_reason"] = (
        "Owner: focal automatisms remain context; independent seizure identity is unclear."
    )
    audit(
        rows["1979"],
        "automatisms_context",
        "Three automatisms are not an independent scored seizure count.",
    )

    claim(rows["1980"], "f1")["disposition"] = "context"
    claim(rows["1980"], "f1")["edit_reason"] = (
        "Owner: intermittent auras are a less precise account of the counted focal seizures."
    )
    r = rows["1980"]
    c = claim(r, "f4")
    c["candidate"] = {
        "event": {"scope": "named", "label": "focal epileptic spasms"},
        "counted_unit": "individual_seizure",
        "status": "stated",
        "measurement": {"kind": "observed_count", "quantity": {"kind": "number", "value": 3}},
        "time": {"phase": "ongoing", "source": "the past three months"},
        "evidence": [
            one_sentence(
                r["note"],
                "he has recorded three focal onset seizures and three focal epileptic spasms",
            )
        ],
    }
    c["edit_reason"] = "Owner: three individual focal epileptic spasms, not three clusters."
    audit(r, "spasms_unit", c["edit_reason"])

    for sid in ("12484", "12502", "12506"):
        monthly(
            rows[sid],
            "f6" if sid == "12484" else "f4",
            {"12484": "f9", "12502": "f7", "12506": "f6"}[sid],
        )
    for sid, legacy_id in (("12484", "f7"), ("12506", "f5")):
        r = rows[sid]
        c = claim(r, legacy_id)
        c["disposition"] = "primary"
        c["candidate"] = copy.deepcopy(claim(rows["12502"], "f5")["candidate"])
        c["candidate"]["evidence"] = ["No seizures have been recorded since her last appointment."]
        c["edit_reason"] = "Owner: retain separate, recording-scoped since-appointment absence."
        audit(r, "recorded_absence", c["edit_reason"])

    for sid in ("3242", "3262"):
        c = claim(rows[sid], "f1")
        c["candidate"]["time"]["source"] = "this month"
        c["edit_reason"] = (
            "Owner: this month is the observation window; preserve the counted absence label."
        )
        audit(rows[sid], "calendar_month_window", c["edit_reason"])
    claim(rows["3281"], "f2")["candidate"]["time"]["source"] = "this month"
    audit(
        rows["3281"],
        "calendar_month_window",
        "Use literal this month despite the date inconsistency.",
    )
    audit(rows["4496"], "literal_count_label", "Use absence seizures from the counted sentence.")
    audit(
        rows["2678"],
        "precise_cadence",
        "Every night is primary; most nights is corroborating context.",
    )

    r = rows["6094"]
    sentence = one_sentence(r["note"], "She reports clusters of brief nocturnal warning sensations")
    for legacy_id, amount, window in (("f1", 3, "September"), ("f2", 2, "early October")):
        c = claim(r, legacy_id)
        c["candidate"] = {
            "event": {"scope": "unspecified", "label": "brief nocturnal events"},
            "counted_unit": "individual_seizure",
            "status": "uncertain",
            "measurement": {
                "kind": "observed_count",
                "quantity": {"kind": "number", "value": amount},
            },
            "time": {"phase": "ongoing", "source": window},
            "evidence": [sentence],
        }
        c["edit_reason"] = "Owner: count brief nocturnal events; warning clusters remain context."
    audit(
        r, "nocturnal_event_counts", "Three September and two early-October brief nocturnal events."
    )

    audit(
        rows["15193"],
        "literal_scope",
        "Keep generalised-seizure absence separate from intermittent absences.",
    )
    audit(
        rows["15168"],
        "literal_scope",
        "Keep generalised-seizure absence separate from jerks and auras.",
    )
    audit(
        rows["15771"],
        "prior_unit_context",
        "Earlier once-per-couple-of-weeks phrase has no stated counted unit.",
    )
    audit(
        rows["15965"],
        "generic_total",
        "Keep the 13-seizure calendar total without subtype allocation.",
    )
    audit(rows["16097"], "generic_total", "Keep the 17-seizure sum without subtype allocation.")
    claim(rows["13209"], "f3")["candidate"]["time"]["phase"] = "past_or_unclear"
    claim(rows["13209"], "f3")["edit_reason"] = (
        "Owner: retain the diary cluster pattern without assigning an ongoing phase "
        "when its observation window is unstated."
    )
    audit(rows["13209"], "unclear_cluster_phase", "The diary does not date the cluster pattern.")

    claim(rows["15497"], "f4")["disposition"] = "context"
    claim(rows["15497"], "f4")["edit_reason"] = (
        "Owner: air-travel episode is detail of the same most recent flight cluster."
    )
    audit(rows["15497"], "last_cluster_deduplication", "No second primary last event.")
    claim(rows["15519"], "f3")["disposition"] = "primary"
    claim(rows["15519"], "f3")["edit_reason"] = (
        "Owner: occasional early-morning generalised seizures are a separate restricted claim."
    )
    audit(
        rows["15519"],
        "distinct_early_morning",
        "Preserve early-morning restricted level separately.",
    )
    audit(
        rows["15672"],
        "unanchored_possible_absences_context",
        "Two observed pauses have no clear count window.",
    )

    r = rows["15267"]
    c = claim(r, "f2")
    c["candidate"] = {
        "event": {"scope": "named", "label": "possible myoclonic jerks"},
        "counted_unit": "individual_seizure",
        "status": "uncertain",
        "measurement": {"kind": "observed_count", "quantity": {"kind": "number", "value": 3}},
        "time": {"phase": "past_or_unclear", "source": "earlier in the year"},
        "evidence": [
            one_sentence(r["note"], "No further tonic-clonic seizures have occurred since 06/2017")
        ],
    }
    c["edit_reason"] = "Owner-approved possible myoclonic event count; preserve earlier-year phase."
    audit(r, "possible_myoclonic_count", c["edit_reason"])

    # Source-stated maximum gaps >= two weeks remain separate even beside rates.
    for sid, weeks, phrase in (
        ("12484", 3, "longest seizure-free period"),
        ("12502", 3, "longest seizure-free period"),
        ("12584", 4, "maximum seizure-free period"),
        ("12641", 3, "longest seizure-free interval"),
        ("12665", 3, "longest seizure-free interval"),
        ("12667", 3, "longest seizure-free interval"),
        ("12676", 3, "longest seizure-free interval"),
        ("12679", 3, "longest seizure-free interval"),
        ("12749", 5, "maximum seizure-free span"),
        ("12751", 5, "maximum seizure-free span"),
    ):
        maximum_gap(rows[sid], weeks, phrase)
    audit(
        rows["12506"],
        "existing_maximum_gap",
        "The three-week literal maximum gap is already primary.",
    )

    r = rows["12665"]
    add(
        r,
        "owner_occasional_clusters_12665",
        {
            "event": {"scope": "unspecified", "label": "seizure clusters"},
            "counted_unit": "cluster",
            "status": "stated",
            "measurement": {"kind": "qualitative", "level": "occasional"},
            "time": {"phase": "ongoing"},
            "evidence": [
                one_sentence(r["note"], "He and his sister note occasional cluster patterns")
            ],
            "restriction": "linked to sleep loss",
        },
        "Owner: keep occasional clusters separately from the since-visit statement.",
    )

    for sid in CONTRADICTION_IDS:
        audit(
            rows[sid],
            "separate_source_assertions",
            "Do not resolve concurrent rates against a since-visit absence.",
        )
    for sid in LITERAL_TIME_IDS:
        audit(
            rows[sid],
            "literal_time",
            "Preserve source time and distinct claims without repairing chronology.",
        )

    for sid in ("891", "13149", "14187", "15429"):
        audit(
            rows[sid],
            "no_unsupported_absence",
            "Unanchored or threshold-ambiguous absence remains context.",
        )
    audit(
        rows["12751"], "literal_maximum_gap", "Five-week maximum gap has unspecified seizure scope."
    )
    audit(
        rows["12882"],
        "distinct_progression",
        "Occasional impaired-awareness progression is distinct from monthly aura rate.",
    )
    audit(rows["14282"], "falls_context", "Unwitnessed falls are not additional seizure counts.")
    audit(
        rows["1880"],
        "unwindowed_mornings_context",
        "Affected mornings lack an independent observation window.",
    )

    # Complete the approved review only after every primary has a valid record.
    for sid in REVIEW_IDS:
        r = rows[sid]
        if any(c["disposition"] == "primary" and c["candidate"] is None for c in r["claims"]):
            raise ValueError(f"{sid}: null primary after owner review")
        if not r.get("owner_adjudications"):
            audit(
                r, "approved_batch", "Approved source-literal disposition from owner review batch."
            )
        if r.get("review_reason"):
            r["prior_review_reason"] = r["review_reason"]
        r["review_reason"] = None
        for item in r.pop("unresolved_omission_suggestions", []):
            r.setdefault("adjudicated_omission_suggestions", []).append(
                {
                    **item,
                    "owner_resolution": "Owner-approved batch; see owner_adjudications.",
                }
            )
        r["annotation_state"] = "complete"


def main() -> None:
    if sha256(BASE) != EXPECTED_BASE_SHA256:
        raise ValueError("Base candidate hash mismatch")
    result = copy.deepcopy(json.loads(BASE.read_text()))
    apply(result)
    result["policy"] = "compact_primary_finding_candidate_v0_3"
    result["status"] = "owner_adjudicated_development_candidate_pending_independent_agreement"
    result["owner_review"] = {
        "date": "2026-09-24",
        "base_candidate": str(BASE),
        "base_sha256": EXPECTED_BASE_SHA256,
        "source": "User answers and approval of six-rule remaining-row batch in Codex task",
        "reviewed_source_ids": sorted(REVIEW_IDS, key=int),
        "method": "Versioned source-literal overlay; no source or frozen v0.8.5 edit",
    }
    counts = Counter(row["annotation_state"] for row in result["rows"])
    dispositions = Counter(c["disposition"] for row in result["rows"] for c in row["claims"])
    result["summary"]["annotation_states"] = dict(counts)
    result["summary"]["dispositions"] = dict(dispositions)
    result["summary"]["null_primary_claims"] = sum(
        c["disposition"] == "primary" and c["candidate"] is None
        for row in result["rows"]
        for c in row["claims"]
    )
    result["summary"]["added_primary_claims"] = sum(
        len(row.get("added_claims", [])) for row in result["rows"]
    )
    result["summary"]["unresolved_omission_suggestions"] = sum(
        len(row.get("unresolved_omission_suggestions", [])) for row in result["rows"]
    )
    result["summary"]["scored_partition"] = (
        "all source rows structurally complete; independent annotation agreement pending"
    )
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(
        json.dumps(
            {
                "candidate": str(OUTPUT),
                "sha256": sha256(OUTPUT),
                "annotation_states": dict(counts),
                "legacy_dispositions": dict(dispositions),
                "added_primary_claims": result["summary"]["added_primary_claims"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
