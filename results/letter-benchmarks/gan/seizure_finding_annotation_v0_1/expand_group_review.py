"""Expand explicit reviewer decisions; validate membership, never infer judgements."""

import argparse
import hashlib
import json
from pathlib import Path


def expand(groups, report):
    allowed = {g["group_id"]: g for g in groups}
    if len(allowed) != len(groups):
        raise ValueError("Duplicate input groups")
    decisions = report["group_reviews"]
    got = [d["group_id"] for d in decisions]
    if len(got) != len(set(got)) or set(got) != set(allowed):
        raise ValueError("Missing, duplicate or unknown review groups")
    result = []
    for d in decisions:
        g = allowed[d["group_id"]]
        mids = [m["member_id"] for m in g["members"]]
        if len(mids) != len(set(mids)):
            raise ValueError("Duplicate input members")
        if d.get("apply_to_all_members") is not True:
            raise ValueError("Explicit whole-group declaration required")
        overrides = {}
        for e in d.get("exceptions", []):
            for mid in e["member_ids"]:
                if mid not in mids or mid in overrides:
                    raise ValueError("Unknown or duplicate exception member")
                overrides[mid] = e
        comparisons = []
        for mid in mids or [None]:
            decision = overrides.get(mid, d)
            if decision["outcome"] not in {
                "consistent",
                "justified_difference",
                "error",
                "unresolved",
            }:
                raise ValueError("Unknown outcome")
            if not decision.get("reason") or not decision.get("rule_ids"):
                raise ValueError("Missing reason or rule reference")
            comparisons.append(
                {
                    "member_ids": [] if mid is None else [mid],
                    **{k: decision[k] for k in ("outcome", "rule_ids", "reason")},
                    "change_ids": decision.get("change_ids", []),
                    "issue_ids": decision.get("issue_ids", []),
                }
            )
        result.append({**g, "comparisons": comparisons, "review_state": "reviewed"})
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--groups", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    groups = [json.loads(line) for line in args.groups.read_text().splitlines()]
    report = json.loads(args.report.read_text())
    expanded = expand(groups, report)
    args.out.mkdir(exist_ok=False)
    (args.out / "groups.jsonl").write_text(
        "".join(json.dumps(g, ensure_ascii=False) + "\n" for g in expanded)
    )
    states = [c["outcome"] for g in expanded for c in g["comparisons"]]
    summary = {
        "groups": len(expanded),
        "memberships": sum(len(g["members"]) for g in expanded),
        "membership_coverage": "pass",
        "errors": states.count("error"),
        "unresolved": states.count("unresolved"),
        "source_actions": report.get("source_actions", []),
        "input_hashes": {
            k: hashlib.sha256(v.read_bytes()).hexdigest()
            for k, v in {"groups": args.groups, "report": args.report}.items()
        },
        "scope": "Supplied membership only; semantic decisions copied from reviewer.",
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
