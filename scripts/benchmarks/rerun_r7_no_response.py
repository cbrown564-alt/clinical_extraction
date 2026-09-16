"""Rerun only the r7 dev750 requests that returned no usable response, then replay a mixed view.

Run from the repository root:

    python -m scripts.benchmarks.rerun_r7_no_response {prepare,run,replay}

Selection is the original first attempt's ``no_response`` category where no model output
was returned: client transport errors and provider error payloads without choices. Returned
outputs, including two empty-content completions, wrong, schema-invalid or label-invalid
outputs, are not rerun. Frozen r7 request bodies, model settings, the
600-second limit, native scorer and no-repair policy are unchanged. The original
first-attempt artifacts and aggregate are preserved and hash-checked.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from collections import Counter
from pathlib import Path
from statistics import mean, median
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from scripts.benchmarks import run_r7_dev750 as r7run

ORIGINAL = r7run.ROOT
ROOT = ORIGINAL / "timeout600"
VIEW = ROOT / "timeout_completed"
RESULTS = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r7/dev750_timeout600"
)
ORIGINAL_ARTIFACTS = (
    "plan.json",
    "requests.jsonl",
    "responses.jsonl",
    "attempts.jsonl",
    "aggregate.json",
    "diagnostics.json",
)
EXPECTED_RERUNS = 149


def ledger_state(root: Path) -> tuple[set[str], set[str], list[dict[str, Any]]]:
    events = study.old.read_lines(root / "attempts.jsonl")
    started = {e["request_id"] for e in events if e["state"] == "started"}
    finished = {e["request_id"] for e in events if e["state"] == "finished"}
    return started, finished, events


def original_error(saved: dict[str, Any]) -> str:
    if saved.get("error"):
        return str(saved["error"])
    if not (saved.get("response") or {}).get("choices"):
        return "provider_error_payload"
    return "empty_content"


def prepare() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    old = study.old
    frozen = old.read_json(ORIGINAL / "plan.json")
    if json.loads(json.dumps(r7run.identity())) != frozen:
        raise ValueError("Frozen r7 development identity changed")
    jobs = r7run.tasks()
    saved = {r["request_id"]: r for r in old.read_lines(ORIGINAL / "requests.jsonl")}
    responses = {r["request_id"]: r for r in old.read_lines(ORIGINAL / "responses.jsonl")}
    if len(saved) != 750 or len(responses) != 750:
        raise ValueError("Original coverage mismatch")
    for job in jobs:
        if job["body"] != saved[job["request_id"]]["body"]:
            raise ValueError("Saved request changed")
    selected = []
    for job in jobs:
        saved = responses[job["request_id"]]
        content, finish = old.response_content(saved.get("response"))
        if r7run.inspect(content, finish, job["record"])["failure"] != "no_response":
            continue
        if original_error(saved) == "empty_content":
            continue  # An empty completion is a returned output, not a transport failure.
        selected.append(job)
    if len(selected) != EXPECTED_RERUNS:
        raise ValueError(f"No-response selection mismatch: {len(selected)}")
    started, finished, events = ledger_state(ORIGINAL)
    if started != finished or len(finished) != 750:
        raise ValueError("Original r7 attempts are unreconciled")
    prior = frozen["prior_charge_upper_usd"] + old.charged(events)
    plan = {
        **frozen,
        "version": "r7_dev750_no_response_rerun_timeout600_v1",
        "timeout_seconds": r7run.TIMEOUT,
        "prior_charge_upper_usd": prior,
        "retry_policy": (
            "one separate attempt per original r7 request without a usable response only"
        ),
        "selection": (
            "original first attempts in the no_response category without any returned model "
            "output: client transport errors and provider error payloads without choices; "
            "two empty-content completions are retained as returned failures"
        ),
        "original_root": str(ORIGINAL),
        "original_sha256": {
            name: old.digest((ORIGINAL / name).read_bytes()) for name in ORIGINAL_ARTIFACTS
        },
        "rerun_request_ids": [job["request_id"] for job in selected],
        "original_errors": dict(
            Counter(original_error(responses[job["request_id"]]) for job in selected)
        ),
        "attempt_link": "request_id identifies the identical request in original_root",
        "runner_sha256": old.digest(Path(__file__).read_bytes()),
    }
    if (ROOT / "plan.json").exists() and old.read_json(ROOT / "plan.json") != plan:
        raise ValueError("Rerun freeze changed")
    rerun_started, rerun_finished, rerun_events = ledger_state(ROOT)
    if rerun_started != rerun_finished or not rerun_started.issubset(
        set(plan["rerun_request_ids"])
    ):
        raise ValueError("Outstanding or unauthorized rerun attempts")
    reserve = sum(
        r7run.reserve(job["body"]) for job in selected if job["request_id"] not in rerun_started
    )
    upper = prior + old.charged(rerun_events) + reserve
    if upper > r7run.BUDGET:
        raise ValueError("Remaining-request reservation exceeds study ceiling")
    old.write_json(ROOT / "plan.json", plan)
    print(
        f"Selected {len(selected)} no-response requests; cumulative worst-case bound ${upper:.6f}",
        flush=True,
    )
    return jobs, selected, plan


def analyze(
    jobs: list[dict[str, Any]], selected: list[dict[str, Any]], plan: dict[str, Any]
) -> None:
    old = study.old
    reruns = old.read_lines(ROOT / "responses.jsonl")
    replacements = {r["request_id"]: r for r in reruns}
    if len(reruns) != EXPECTED_RERUNS or set(replacements) != {
        job["request_id"] for job in selected
    }:
        raise ValueError("All reruns must finish before mixed-attempt analysis")
    for name, digest in plan["original_sha256"].items():
        if old.digest((ORIGINAL / name).read_bytes()) != digest:
            raise ValueError("Original artifact changed")
    VIEW.mkdir(parents=True, exist_ok=True)
    merged = [
        replacements.get(r["request_id"], r) for r in old.read_lines(ORIGINAL / "responses.jsonl")
    ]
    (VIEW / "responses.jsonl").write_text("".join(json.dumps(r) + "\n" for r in merged))
    events = old.read_lines(ROOT / "attempts.jsonl")
    (VIEW / "attempts.jsonl").write_text((ROOT / "attempts.jsonl").read_text())
    view_plan = {
        **plan,
        "view": "mixed attempts; original usable responses plus single no-response reruns",
    }
    old.write_json(VIEW / "plan.json", view_plan)
    r7run.ROOT, r7run.RESULTS = VIEW, RESULTS
    report = r7run.analyze(jobs, view_plan)
    finished = {e["request_id"]: e for e in events if e["state"] == "finished"}
    timing = []
    for event in old.read_lines(ORIGINAL / "attempts.jsonl"):
        if event["state"] != "finished":
            continue
        rerun = finished.get(event["request_id"])
        original_seconds = event["elapsed_seconds"]
        rerun_seconds = rerun["elapsed_seconds"] if rerun else 0
        timing.append(
            {
                "request_id": event["request_id"],
                "original_seconds": original_seconds,
                "rerun_seconds": rerun_seconds,
                "cumulative_seconds": original_seconds + rerun_seconds,
                "rerun": bool(rerun),
            }
        )
    report["timing"] = {
        key: {"n": len(times), "sum": sum(times), "mean": mean(times), "median": median(times)}
        for key in ("original_seconds", "rerun_seconds", "cumulative_seconds")
        if (times := [v[key] for v in timing if key != "rerun_seconds" or v["rerun"]])
    }
    report["rerun_transport_errors"] = dict(Counter(r["error"] for r in reruns if r.get("error")))
    report["rerun_provider_error_payloads"] = sum(
        1 for r in reruns if r.get("response") and not r["response"].get("choices")
    )
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
                    "rerun_provider_error_payloads",
                    "total_study_charge_upper_usd",
                    "timing",
                )
            }
        ),
        flush=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run", "replay"))
    args = parser.parse_args()
    jobs, selected, plan = prepare()
    if args.command == "prepare":
        return
    if args.command == "run":
        r7run.ROOT = ROOT
        original_analyze = r7run.analyze
        r7run.analyze = lambda *_: {}  # Analysis needs all 750 original rows, assembled below.
        try:
            asyncio.run(r7run.run(selected, plan))
        finally:
            r7run.analyze = original_analyze
            r7run.ROOT = ORIGINAL
    analyze(jobs, selected, plan)


if __name__ == "__main__":
    main()
