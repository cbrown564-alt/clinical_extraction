"""Resume unstarted requests with a separately recorded budget authorization."""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import UTC, datetime

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget", type=float, required=True)
    args = parser.parse_args()
    original = study.old.read_json(study.ROOT / "plan.json")
    if json.loads(json.dumps(study.identity())) != original:
        raise ValueError("Frozen study identity changed; budget authorization cannot bypass this")
    events = study.old.read_lines(study.ROOT / "attempts.jsonl")
    started = {e["request_id"] for e in events if e["state"] == "started"}
    finished = {e["request_id"] for e in events if e["state"] == "finished"}
    if started != finished:
        raise ValueError("Outstanding attempts exist; do not start another runner")
    spent = original["prior_charge_upper_usd"] + study.old.charged(events)
    if args.budget < spent:
        raise ValueError("Budget is below the existing charge bound")
    tasks = study.jobs(study.records())
    pending = sum(j["request_id"] not in started for j in tasks)
    authorization = {
        "authorized_utc": datetime.now(UTC).isoformat(),
        "budget_usd": args.budget,
        "original_plan_budget_usd": original["budget_usd"],
        "prior_charge_upper_usd": spent,
        "unstarted_calls": pending,
        "scope": "budget-only amendment; frozen requests, runtime, parser and scorer unchanged",
        "retry_policy": "none; completed and timed-out attempts are not repeated",
    }
    study.old.append(study.ROOT / "budget_authorizations.jsonl", authorization)
    study.old.write_json(study.ROOT / "active_budget.json", authorization)
    study.BUDGET = args.budget
    print(
        f"Resuming {pending} unstarted calls with cumulative budget ${args.budget:.2f}", flush=True
    )
    asyncio.run(study.run(tasks))
    report = study.old.read_json(study.ROOT / "aggregate.json")
    report["budget_authorization"] = authorization
    study.old.write_json(study.ROOT / "aggregate.json", report)


if __name__ == "__main__":
    main()
