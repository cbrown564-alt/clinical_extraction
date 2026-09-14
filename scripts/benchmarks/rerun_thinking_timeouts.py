"""Rerun only frozen r4/r5 dev750 timeouts and replay a separate mixed-attempt view."""

from __future__ import annotations

import argparse
import asyncio
import json
from collections import Counter
from pathlib import Path
from statistics import mean, median

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)

ORIGINAL = study.ROOT
ROOT = ORIGINAL / "timeout600"
VIEW = ROOT / "timeout_completed"
RESULTS = Path("results/letter-benchmarks/gan/one_shot_thinking_r4_r5_r6/dev750_timeout600")
HOLDOUT = Path("runs/one_shot_original_r6/test450_timeout600")


def prepare():
    old = study.old
    frozen = old.read_json(ORIGINAL / "plan.json")
    if json.loads(json.dumps(study.identity())) != frozen:
        raise ValueError("Frozen development identity changed")
    originals = old.read_lines(ORIGINAL / "requests.jsonl")
    responses = {r["request_id"]: r for r in old.read_lines(ORIGINAL / "responses.jsonl")}
    tasks = study.jobs(study.records())
    saved = {r["request_id"]: r for r in originals}
    if len(saved) != 2250 or len(responses) != 2250:
        raise ValueError("Original coverage mismatch")
    for task in tasks:
        if task["body"] != saved[task["request_id"]]["body"]:
            raise ValueError("Saved request changed")
    selected = [
        t
        for t in tasks
        if t["condition"] in ("r4_simple", "r5_rich")
        and responses[t["request_id"]]["error"] == "ReadTimeout"
        and responses[t["request_id"]]["response"] is None
    ]
    if Counter(t["condition"] for t in selected) != {"r4_simple": 14, "r5_rich": 40}:
        raise ValueError("Timeout selection mismatch")
    prior = frozen["prior_charge_upper_usd"]
    for root, expected in ((ORIGINAL, 2250), (HOLDOUT, 450)):
        events = old.read_lines(root / "attempts.jsonl")
        started = {e["request_id"] for e in events if e["state"] == "started"}
        finished = {e["request_id"] for e in events if e["state"] == "finished"}
        if started != finished or len(finished) != expected:
            raise ValueError("Other study work is unfinished; reconcile reservations first")
        prior += old.charged(events)
    plan = {
        **frozen,
        "version": "r4_r5_timeout600_v1",
        "timeout_seconds": 600,
        "budget_usd": 100.0,
        "prior_charge_upper_usd": prior,
        "retry_policy": "one separate attempt per originally timed-out r4/r5 request only",
        "original_root": str(ORIGINAL),
        "original_sha256": {
            name: old.digest((ORIGINAL / name).read_bytes())
            for name in (
                "plan.json",
                "requests.jsonl",
                "responses.jsonl",
                "attempts.jsonl",
                "aggregate.json",
            )
        },
        "rerun_request_ids": [t["request_id"] for t in selected],
        "attempt_link": "request_id identifies the identical request in original_root",
        "runner_sha256": old.digest(Path(__file__).read_bytes()),
    }
    if (ROOT / "plan.json").exists() and old.read_json(ROOT / "plan.json") != plan:
        raise ValueError("Rerun freeze changed")
    events = old.read_lines(ROOT / "attempts.jsonl")
    started = {e["request_id"] for e in events if e["state"] == "started"}
    finished = {e["request_id"] for e in events if e["state"] == "finished"}
    if started != finished or not started.issubset(set(plan["rerun_request_ids"])):
        raise ValueError("Outstanding or unauthorized rerun attempts")
    reserve = sum(
        (len(old.encoded(t["body"]["messages"])) + 1024) * old.INPUT_PEAK
        + study.MAX_TOKENS * old.OUTPUT_PEAK
        for t in selected
        if t["request_id"] not in started
    )
    upper = prior + old.charged(events) + reserve
    if upper > 100:
        raise ValueError("Remaining-request reservation exceeds study ceiling")
    old.write_json(ROOT / "plan.json", plan)
    print(f"Selected 54 timeouts; cumulative worst-case bound ${upper:.6f}", flush=True)
    return tasks, selected, plan


def analyze(tasks, selected, plan):
    old = study.old
    reruns = old.read_lines(ROOT / "responses.jsonl")
    replacements = {r["request_id"]: r for r in reruns}
    if len(reruns) != 54 or set(replacements) != {t["request_id"] for t in selected}:
        raise ValueError("All 54 reruns must finish before mixed-attempt analysis")
    for name, digest in plan["original_sha256"].items():
        if old.digest((ORIGINAL / name).read_bytes()) != digest:
            raise ValueError("Original artifact changed")
    VIEW.mkdir(parents=True, exist_ok=True)
    merged = [
        replacements.get(r["request_id"], r) for r in old.read_lines(ORIGINAL / "responses.jsonl")
    ]
    (VIEW / "responses.jsonl").write_text("".join(json.dumps(r) + "\n" for r in merged))
    old.write_json(
        VIEW / "plan.json",
        {**plan, "view": "mixed attempts; original non-timeouts plus single timeout reruns"},
    )
    study.ROOT = VIEW
    report = study.analyze(tasks)
    events = old.read_lines(ROOT / "attempts.jsonl")
    originals = old.read_lines(ORIGINAL / "attempts.jsonl")
    timing = []
    finished = {e["request_id"]: e for e in events if e["state"] == "finished"}
    for event in originals:
        if event["state"] != "finished" or event["condition"] not in ("r4_simple", "r5_rich"):
            continue
        rerun = finished.get(event["request_id"])
        original_seconds = event["elapsed_seconds"]
        rerun_seconds = rerun["elapsed_seconds"] if rerun else 0
        timing.append(
            {
                "request_id": event["request_id"],
                "condition": event["condition"],
                "original_seconds": original_seconds,
                "rerun_seconds": rerun_seconds,
                "cumulative_seconds": original_seconds + rerun_seconds,
                "rerun": bool(rerun),
            }
        )
    report["timing"] = {}
    for condition in ("r4_simple", "r5_rich"):
        values = [v for v in timing if v["condition"] == condition]
        report["timing"][condition] = {
            key: {"n": len(times), "sum": sum(times), "mean": mean(times), "median": median(times)}
            for key in ("original_seconds", "rerun_seconds", "cumulative_seconds")
            if (times := [v[key] for v in values if key != "rerun_seconds" or v["rerun"]])
        }
    report["charge_upper_usd"] = old.charged(events)
    report["total_study_charge_upper_usd"] = plan["prior_charge_upper_usd"] + old.charged(events)
    report["rerun_transport_errors"] = dict(Counter(r["error"] for r in reruns if r.get("error")))
    report["reruns_finished"] = len(reruns)
    report["replay_mode"] = (
        "saved responses only; no repair; original first-attempt aggregate unchanged"
    )
    old.write_json(VIEW / "aggregate.json", report)
    old.write_json(RESULTS / "aggregate.json", report)
    old.write_json(RESULTS / "time_per_request.json", timing)
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "reruns_finished",
                    "rerun_transport_errors",
                    "total_study_charge_upper_usd",
                    "timing",
                )
            }
        ),
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run", "replay"))
    args = parser.parse_args()
    tasks, selected, plan = prepare()
    if args.command == "prepare":
        return
    if args.command == "run":
        study.ROOT, study.TIMEOUT, study.BUDGET = ROOT, 600, 100.0
        original_analyze = study.analyze
        study.analyze = lambda _: {}  # Analysis requires all 750 original rows, assembled below.
        try:
            asyncio.run(study.run(selected))
        finally:
            study.analyze = original_analyze
    analyze(tasks, selected, plan)


if __name__ == "__main__":
    main()
