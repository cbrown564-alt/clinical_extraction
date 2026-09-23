"""V3 fictional classification/verification experiment, separate from native Gan scoring."""

from __future__ import annotations

import argparse
import copy
import json
import re
from collections import defaultdict
from pathlib import Path

from scripts.benchmarks import jev_pilot as transport

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "results/letter-benchmarks/gan/jev_fictional_v3"
RUN = ROOT / "runs/jev_fictional_v3"
CASES = ROOT / "examples/jev_comparison/v3/cases.json"
VERSION = "jev_classification_verification_v3"
GUIDE = """Classify frequency findings anchored in each candidate, using the entire letter
for event identity, temporal scope and contradictions. Context-only sentences, medication,
other people's events, confirmed non-epileptic attacks, and duration of an individual event
are other/none. Inherit event identity across sentences when explicit. Treat an observed
total within a window as count, not rate. Grouped seizure days or episodes are clusters.
Seizure-free gaps between recurring clusters do not imply global seizure freedom.
role is current, historical, future (hypothetical frequency), uncertain (epileptic status
unresolved), conflicting (incompatible accounts of the same events and same period without
resolution), or other. Conflicting overrides current; uncertain overrides current.
kind is rate, count, cluster, seizure_free, qualitative, none, or unresolved.
Seizure_free covers event-specific absence over an interval or anchor, including between
cluster episodes. Qualitative is frequency without a numerical measurement. Unresolved is
used only when a frequency finding cannot be assigned one supported kind. Other has kind none.
Outer quantity applies to rates, observed counts and cluster recurrence, even if historical,
future, uncertain or conflicting. Inner quantity applies only to grouped seizure episodes,
even if their size is unstated. Applicability is semantic, not whether a number is present.
Do not estimate numerical values. Return source-based judgments without repairing a record."""
OPTIONS = {
    "role": {
        "current": "Present or ongoing frequency finding.",
        "historical": "Superseded/past finding.",
        "future": "Hypothetical/prospective frequency finding.",
        "uncertain": "Epileptic status of the measured event is unresolved.",
        "conflicting": "Incompatible unresolved accounts of the same events and period.",
        "other": "Not a patient seizure-frequency finding, or context without a measurement.",
    },
    "kind": {
        "rate": "Recurring individual events per time.",
        "count": "Observed total in a window.",
        "cluster": "Grouped events with group recurrence distinct from individual seizures.",
        "seizure_free": "Event-specific absence over an interval or anchor.",
        "qualitative": "Non-numerical frequency.",
        "none": "No in-scope frequency measurement.",
        "unresolved": "A frequency measurement exists but its kind cannot be determined.",
    },
    "outer_applicable": {
        "yes": "An outer quantity field applies: rate, count or group recurrence.",
        "no": "No outer quantity field applies.",
    },
    "inner_applicable": {
        "yes": "An inner quantity field applies to grouped seizures.",
        "no": "No inner quantity field applies: the finding is not grouped.",
    },
}
FIELDS = tuple(OPTIONS)


def setup():
    transport.RUN = RUN
    transport.BUDGET = 2.0


def write(path, value):
    transport.write(path, value)


def read(path):
    return transport.read(path)


def candidates(case, include_omitted=False):
    return [
        {"id": f"s{i}", "text": m[0], "start": m.start(), "end": m.end()}
        for i, m in enumerate(re.finditer(r"[^\n]+", case["text"]))
        if include_omitted or f"s{i}" not in case["omitted"]
    ]


def request(case):
    questions = {}
    for c in candidates(case):
        for field, options in OPTIONS.items():
            questions[c["id"] + "." + field] = {
                "type": "choice",
                "instructions": GUIDE
                + f"\nFor candidate {c['id']}: {c['text']}\n"
                + f"Classify {field}. This question stands alone; do not assume another answer.",
                "criteria": options,
            }
    questions["coverage"] = {
        "type": "choice",
        "instructions": GUIDE
        + "\nConsidering all current confirmed frequency findings in the letter, do these "
        "candidates cover every such finding? Candidates: " + json.dumps(candidates(case)),
        "criteria": {
            "complete": "At least one unconflicted current confirmed finding exists and "
            "all are represented.",
            "missing": "An unconflicted current confirmed finding lacks a candidate.",
            "none": "No unconflicted current confirmed finding can be established.",
        },
    }
    return {"model": "jev-1.13.0", "state": case["text"], "questions": questions}


def llm_request(case):
    common = {k: v for k, v in request(case).items() if k != "model"}
    return transport.llm_body(
        [
            {
                "role": "system",
                "content": "Return one JSON object mapping question IDs to allowed Choice keys. "
                "Apply the supplied definitions to each question independently; do"
                " not add explanations.",
            },
            {"role": "user", "content": json.dumps(common)},
        ]
    )


def coverage_gold(case):
    current = [k for k, v in case["gold"].items() if v["role"] == "current"]
    if not current:
        return "none"
    return "missing" if any(k in case["omitted"] for k in current) else "complete"


def expected(case):
    result = {"coverage": coverage_gold(case)}
    for c in candidates(case):
        result.update({c["id"] + "." + k: v for k, v in case["gold"][c["id"]].items()})
    return result


def choices(record, provider):
    payload, error = transport.decode(record, provider)
    if error:
        return {}, error
    if provider == "jev":
        answers = payload.get("answers", {})
        if not isinstance(answers, dict):
            return {}, "invalid_answers"
        return {k: v.get("choice") for k, v in answers.items() if isinstance(v, dict)}, None
    return payload, None


def extracted(case, answers):
    # Pure structural assembly: no conditional masking or semantic correction.
    return [
        {
            "id": c["id"],
            "evidence": c["text"],
            "fields": {f: answers.get(c["id"] + "." + f) for f in FIELDS},
        }
        for c in candidates(case)
    ]


def verify_request(case, claims):
    questions = {}
    for i, claim in enumerate(claims):
        questions[f"claim_{i}"] = {
            "type": "choice",
            "instructions": GUIDE
            + "\nVerify every field and the evidence of this proposed classification against "
            "the entire source. Accept only if all fields are supported under the definitions. "
            "Reject any incorrect, incompatible, invented or omitted required field. "
            "Choose uncertain if the source cannot settle the proposal. Proposal: "
            + json.dumps(claim),
            "criteria": {
                "accept": "Every proposed field and evidence is supported.",
                "reject": "At least one field or the evidence is incorrect or missing.",
                "uncertain": "The source cannot establish whether this proposal is correct.",
            },
        }
    return {"model": "jev-1.13.0", "state": case["text"], "questions": questions}


def challenges(case):
    # Keys are used only to construct a separately labelled verifier challenge set.
    # They are never used to prepare either classification condition.
    c = next(c for c in candidates(case) if case["gold"][c["id"]]["kind"] != "none")
    correct = {"id": c["id"], "evidence": c["text"], "fields": copy.deepcopy(case["gold"][c["id"]])}
    items = [{"claim": correct, "correct": True, "mutation": "none"}]
    for field, value in [
        ("role", "future" if correct["fields"]["role"] != "future" else "current"),
        ("kind", "rate" if correct["fields"]["kind"] != "rate" else "cluster"),
        ("inner_applicable", "no" if correct["fields"]["inner_applicable"] == "yes" else "yes"),
    ]:
        claim = copy.deepcopy(correct)
        claim["fields"][field] = value
        items.append({"claim": claim, "correct": False, "mutation": field})
    # Do not reveal correct/mutation labels or stable answer-position patterns to the model.
    return sorted(items, key=lambda x: transport.sha(x["claim"]))


def call(provider, rid, body):
    setup()
    record = transport.attempt(provider, rid, body)
    if record.get("http_status") in (400, 401, 402, 403, 404, 422):
        raise ValueError("Provider rejected request; no automatic retry")
    return record


def review():
    payload = [
        {"id": c["id"], "text": c["text"], "candidates": candidates(c, True)} for c in read(CASES)
    ]
    body = transport.llm_body(
        [
            {
                "role": "system",
                "content": GUIDE + "\nIndependently annotate these fictional sources. "
                'No proposed keys or predictions are supplied. Return JSON {"cases": {case_id: '
                "{candidate_id: {role,kind,outer_applicable,inner_applicable}}}, "
                '"notes": [ambiguities]}. '
                "All applicability answers are strings yes/no. Include context-only sentences.",
            },
            {"role": "user", "content": json.dumps(payload)},
        ],
        review=True,
    )
    call("review", "source_only", body)


def freeze():
    setup()
    cases = read(CASES)
    reviewed, error = transport.decode(read(RUN / "review/source_only.json"), "review")
    if error:
        raise ValueError(error)
    differences = []
    for c in cases:
        if reviewed["cases"][c["id"]] != c["gold"]:
            differences.append(
                {"id": c["id"], "author": c["gold"], "review": reviewed["cases"][c["id"]]}
            )
    comparison = {
        "differences": differences,
        "notes": reviewed.get("notes"),
        "review_hash": transport.file_sha(RUN / "review/source_only.json"),
    }
    adjudication = read(ART / "adjudication.json")
    unresolved = []
    for difference in differences:
        for cid, fields in difference["author"].items():
            for field, value in fields.items():
                reviewed_value = difference["review"].get(cid, {}).get(field)
                if reviewed_value == value:
                    continue
                decision = adjudication.get(difference["id"] + "." + cid + "." + field, {})
                if decision.get("accepted") != value or decision.get("reviewer") != reviewed_value:
                    unresolved.append((difference["id"], cid, field))
    comparison["adjudication"] = adjudication
    if unresolved:
        raise ValueError("Unresolved reference differences: " + str(unresolved))
    write(ART / "review.json", comparison)
    jobs = []
    for c in cases:
        jobs.extend(
            [
                {"provider": "jev", "id": "classify_" + c["id"], "body": request(c)},
                {"provider": "deepseek", "id": "classify_" + c["id"], "body": llm_request(c)},
                {
                    "provider": "jev",
                    "id": "challenge_" + c["id"],
                    "body": verify_request(c, [x["claim"] for x in challenges(c)]),
                },
            ]
        )
    reserve = sum(transport.reservation(j["provider"], j["body"]) for j in jobs)
    # Hybrid proposals contain only enumerated keys + exact candidate evidence.
    # Reserve an additional full 64k input context for each Jev verification call.
    reserve += len(cases) * 64000 * 0.042 / 1_000_000
    reserve += read(RUN / "review/source_only.started.json")["reservation_usd"]
    assert reserve < 2
    write(ART / "requests.json", jobs)
    write(ART / "cases.json", cases)
    numeric = {
        c["id"]: [
            {"text": m[0], "start": m.start(), "end": m.end()}
            for m in re.finditer(r"\b\d+(?:[-–]\d+)?\b", c["text"])
        ]
        for c in cases
    }
    write(ART / "literal_candidates.json", numeric)
    paths = [
        Path(__file__),
        Path(transport.__file__),
        Path(transport.v1.__file__),
        CASES,
        ART / "cases.json",
        ART / "requests.json",
        ART / "review.json",
        ART / "adjudication.json",
        ART / "split_lock.json",
    ]
    write(
        ART / "freeze.json",
        {
            "version": VERSION,
            "created_at": transport.now(),
            "split": "8 development + 8 reserved fictional cases; not clinical holdout",
            "row_policy": "all fixed candidates including missing/invalid answers",
            "model": "jev-1.13.0 versus deepseek-flash; source review deepseek-v4-pro",
            "runtime": "600s timeout, sequential per provider; DeepSeek thinking low, "
            "24000 output cap",
            "budget_usd": 2,
            "reservation_usd": reserve,
            "repair": "none",
            "hybrid_policy": "Accept releases unchanged candidate; reject/uncertain/missing "
            "defers to review. No correction.",
            "hybrid_numerical_policy": (
                "No numerical extraction performance claim; literal candidates parsed separately."
            ),
            "decision": "No dev750 run unless reserved cases avoid recurring "
            "role/applicability failures and "
            "verification rejects all seeded wrong claims without losing correct inventory; "
            "even then reviewed native mapping and candidate coverage are prerequisites.",
            "files": {str(p.resolve().relative_to(ROOT)): transport.file_sha(p) for p in paths},
        },
    )
    print(json.dumps(read(ART / "freeze.json"), indent=2))


def check_freeze():
    f = read(ART / "freeze.json")
    for path, h in f["files"].items():
        assert transport.file_sha(ROOT / path) == h, path
    return f


def run(split, provider):
    check_freeze()
    cases = [c for c in read(ART / "cases.json") if c["split"] == split]
    jobs = read(ART / "requests.json")
    for c in cases:
        rid = "classify_" + c["id"]
        job = next(j for j in jobs if j["id"] == rid and j["provider"] == provider)
        record = call(provider, rid, job["body"])
        if provider == "jev":
            challenge = next(j for j in jobs if j["id"] == "challenge_" + c["id"])
            call("jev", challenge["id"], challenge["body"])
        else:
            answers, error = choices(record, "deepseek")
            if error:
                continue  # Fixed-denominator report treats absent verification as deferral.
            # Only transport structurally valid enumerated tuples; invalids are not silently
            # repaired.
            claims = extracted(c, answers)
            if any(claim["fields"][f] not in OPTIONS[f] for claim in claims for f in FIELDS):
                continue
            call("jev", "verify_" + c["id"], verify_request(c, claims))


def load(provider, rid):
    path = RUN / provider / (rid + ".json")
    return read(path) if path.exists() else {"error": "not_run"}


def report():
    freeze = check_freeze()
    result = {"freeze": freeze, "splits": {}, "rows": []}
    for split in ["development", "reserved"]:
        buckets = {k: defaultdict(int) for k in ["jev", "deepseek", "hybrid", "challenge"]}
        for c in [x for x in read(ART / "cases.json") if x["split"] == split]:
            gold = expected(c)
            predicted = {}
            for provider in ["jev", "deepseek"]:
                record = load(provider, "classify_" + c["id"])
                answers, error = choices(record, provider)
                predicted[provider] = answers
                b = buckets[provider]
                b["cases"] += 1
                b["decisions"] += len(gold)
                b["correct"] += sum(answers.get(k) == v for k, v in gold.items())
                b["complete_cases"] += all(answers.get(k) == v for k, v in gold.items())
                b["coverage_correct"] += answers.get("coverage") == gold["coverage"]
                wanted = {k for k, v in c["gold"].items() if v["role"] == "current"}
                emitted = {
                    x["id"] for x in candidates(c) if answers.get(x["id"] + ".role") == "current"
                }
                b["current_tp"] += len(wanted & emitted)
                b["current_fp"] += len(emitted - wanted)
                b["current_fn"] += len(wanted - emitted)
                result["rows"].append(
                    {
                        "id": c["id"],
                        "split": split,
                        "provider": provider,
                        "error": error,
                        "wrong": {
                            k: {"expected": v, "actual": answers.get(k)}
                            for k, v in gold.items()
                            if answers.get(k) != v
                        },
                    }
                )
            ver, _ = choices(load("jev", "verify_" + c["id"]), "jev")
            b = buckets["hybrid"]
            exact = True
            released = set()
            for i, candidate in enumerate(candidates(c)):
                cid = candidate["id"]
                fields = {f: predicted["deepseek"].get(cid + "." + f) for f in FIELDS}
                correct = fields == c["gold"][cid]
                accept = ver.get(f"claim_{i}") == "accept"
                b["proposals"] += 1
                b["correct_proposals"] += correct
                b["incorrect_proposals"] += not correct
                b["accepted_correct"] += correct and accept
                b["false_accepts"] += not correct and accept
                b["correct_deferred"] += correct and not accept
                b["deferred"] += not accept
                exact = exact and correct and accept
                if accept and fields["role"] == "current":
                    released.add(cid)
            wanted = {k for k, v in c["gold"].items() if v["role"] == "current"}
            b["current_tp"] += len(wanted & released)
            b["current_fp"] += len(released - wanted)
            b["current_fn"] += len(wanted - released)
            b["cases"] += 1
            b["all_candidates_correct_and_released"] += exact
            challenge, _ = choices(load("jev", "challenge_" + c["id"]), "jev")
            b = buckets["challenge"]
            for i, item in enumerate(challenges(c)):
                accept = challenge.get(f"claim_{i}") == "accept"
                b["correct_claims" if item["correct"] else "wrong_claims"] += 1
                if item["correct"]:
                    b["correct_accepted"] += accept
                    b["correct_deferred"] += not accept
                else:
                    b["false_accepts"] += accept
                    b["wrong_deferred"] += not accept
                b["missing_or_invalid_verdicts"] += challenge.get(f"claim_{i}") not in [
                    "accept",
                    "reject",
                    "uncertain",
                ]
        result["splits"][split] = {k: dict(v) for k, v in buckets.items()}
    records = [read(p) for p in RUN.glob("*/*.json") if not p.name.endswith(".started.json")]
    result["cost_peak_upper_usd"] = sum(r["peak_charge_upper_usd"] for r in records)
    result["calls"] = len(records)
    result["timing"] = {}
    for stage in ["classify_jev", "classify_deepseek", "verify", "challenge", "review"]:
        matched = [
            r
            for r in records
            if (stage == "review" and r["provider"] == "review")
            or (
                stage == "classify_jev"
                and r["provider"] == "jev"
                and r["id"].startswith("classify_")
            )
            or (stage == "classify_deepseek" and r["provider"] == "deepseek")
            or (stage in ["verify", "challenge"] and r["id"].startswith(stage + "_"))
        ]
        result["timing"][stage] = {
            "calls": len(matched),
            "seconds": sum(r["elapsed_seconds"] for r in matched),
            "peak_upper_usd": sum(r["peak_charge_upper_usd"] for r in matched),
        }
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["review", "freeze", "run", "report"])
    p.add_argument("--split", choices=["development", "reserved"])
    p.add_argument("--provider", choices=["jev", "deepseek"])
    a = p.parse_args()
    if a.command == "review":
        review()
    elif a.command == "freeze":
        freeze()
    elif a.command == "run":
        if not a.split or not a.provider:
            p.error("--split and --provider required")
        run(a.split, a.provider)
    else:
        print(json.dumps(report(), indent=2))


if __name__ == "__main__":
    main()
