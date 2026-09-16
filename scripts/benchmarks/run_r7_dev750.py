"""R7 rich development evaluation on synthetic Gan dev750.

Thinking enabled/low, 24,000-token limit, 600-second timeout, no retries or repairs.
Does not change frozen r4/r5/r6 requests or runners.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
from collections import Counter
from pathlib import Path
from typing import Any

import httpx
from pydantic import ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation.one_shot_analysis import wilson
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r7 as r7

ROOT = Path("runs/one_shot_frequency_v2_measurements_r7/dev750")
RESULTS = Path("results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r7/dev750")
TIMEOUT = 600
BUDGET = 100.0
MAX_TOKENS = 24000
PRIOR_LEDGERS = (
    Path("runs/one_shot_frequency_v1/attempts.jsonl"),
    Path("runs/one_shot_frequency_v2_measurements_r4/dev750/attempts.jsonl"),
    Path("runs/one_shot_thinking_r4_r5_r6/dev750/attempts.jsonl"),
    Path("runs/one_shot_thinking_r4_r5_r6/dev750/timeout600/attempts.jsonl"),
    Path("runs/one_shot_original_r6/test450_timeout600/attempts.jsonl"),
)


def body(record: Any) -> dict[str, Any]:
    return {
        "model": study.old.MODEL,
        "messages": r7.messages(record.note_text),
        "temperature": 0,
        "max_tokens": MAX_TOKENS,
        "thinking": {"type": "enabled"},
        "reasoning_effort": "low",
    }


def inspect(content: str | None, finish: str | None, record: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "failure": None,
        "answer_failure": None,
        "label": None,
        "record_valid": False,
        "answer_valid": False,
        "structured_json": None,
    }
    if finish == "length":
        result.update(failure="truncation", answer_failure="truncation")
        return result
    match = study.previous.ENVELOPE.fullmatch(content or "")
    if not match or "[[ ##" in match[1]:
        failure = "invalid_envelope" if content else "no_response"
        result.update(failure=failure, answer_failure=failure)
        return result
    raw = match[1]
    result["structured_json"] = raw
    try:
        payload = json.loads(raw, object_pairs_hook=study.r4.v1._unique_object)
    except (ValueError, TypeError):
        result.update(failure="invalid_syntax", answer_failure="invalid_syntax")
        return result
    answer = payload.get("answer") if isinstance(payload, dict) else None
    checked = study.r4.v1.inspect_output(json.dumps({"answer": answer}), record.note_text, "simple")
    result.update(
        answer_failure=checked["failure"],
        answer_valid=checked["failure"] is None,
        label=checked["label"],
    )
    for method in ("purist", "pragmatic"):
        gold = study.old.gold_categories(record.raw)[method]
        result[method + "_correct"] = (
            result["answer_valid"] and checked["categories"][method] == gold
        )
    try:
        r7.Rich.model_validate(payload)
        result["record_valid"] = True
    except ValidationError:
        result["failure"] = "invalid_schema"
    if result["failure"] is None:
        result["failure"] = checked["failure"]
    return result


def prior_charge() -> float:
    return sum(study.old.charged(study.old.read_lines(path)) for path in PRIOR_LEDGERS)


def tasks() -> list[dict[str, Any]]:
    selected = study.records()
    jobs = []
    for record in selected:
        request = body(record)
        rid = study.old.digest(
            study.old.encoded(
                {
                    "source_row_index": record.source_row_index,
                    "version": r7.VERSION,
                    "revision": r7.REVISION,
                    "body": request,
                }
            )
        )
        jobs.append(
            {"record": record, "condition": r7.VERSION, "body": request, "request_id": rid}
        )
    return jobs


def identity() -> dict[str, Any]:
    paths = [
        Path(__file__),
        Path(r7.__file__),
        Path(r7.r5.__file__),
        Path(r7.r4.__file__),
        Path(r7.r4.v1.__file__),
    ]
    return {
        "version": "r7_dev750_timeout600_v1",
        "prompt_version": r7.VERSION,
        "revision": r7.REVISION,
        "dataset": "Gan 2026 synthetic",
        "split": "dev750",
        "row_policy": "all development rows including row_ok=False; failures retained",
        "dataset_sha256": study.old.digest(study.old.DEFAULT_DATA_PATH.read_bytes()),
        "manifest_sha256": study.old.digest(study.old.DEFAULT_SPLIT_MANIFEST_PATH.read_bytes()),
        "components": {str(path): study.old.digest(path.read_bytes()) for path in paths},
        "model": study.old.MODEL,
        "provider_documented_version": "DeepSeek-V4.1-Flash",
        "thinking": "enabled",
        "reasoning_effort": "low",
        "temperature_submitted": 0,
        "temperature_effective": "ignored by provider in thinking mode",
        "max_tokens": MAX_TOKENS,
        "timeout_seconds": TIMEOUT,
        "concurrency": study.CONCURRENCY,
        "budget_usd": BUDGET,
        "prior_charge_upper_usd": prior_charge(),
        "retry_policy": "none; saved first response; no automatic JSONAdapter fallback",
        "repair_policy": "none",
        "scoring": "native Purist/Pragmatic; independent declared answer plus whole-record strict",
        "scope": "synthetic development; not held-out generalization",
    }


def reserve(request: dict[str, Any]) -> float:
    return (
        len(study.old.encoded(request["messages"])) + 1024
    ) * study.old.INPUT_PEAK + MAX_TOKENS * study.old.OUTPUT_PEAK


def analyze(jobs: list[dict[str, Any]], plan: dict[str, Any]) -> dict[str, Any]:
    responses = {row["request_id"]: row for row in study.old.read_lines(ROOT / "responses.jsonl")}
    diagnostics = []
    models: Counter[str] = Counter()
    for job in jobs:
        saved = responses.get(job["request_id"], {})
        content, finish = study.old.response_content(saved.get("response"))
        value = inspect(content, finish, job["record"])
        diagnostics.append(
            {
                "source_row_index": job["record"].source_row_index,
                "condition": r7.VERSION,
                "request_id": job["request_id"],
                **value,
            }
        )
        if saved.get("response"):
            models[str(saved["response"].get("model"))] += 1
    n = len(diagnostics)
    summary: dict[str, Any] = {
        "n": n,
        "record_valid": sum(row["record_valid"] for row in diagnostics),
        "answer_valid": sum(row["answer_valid"] for row in diagnostics),
        "failures": dict(Counter(row["failure"] for row in diagnostics if row["failure"])),
        "answer_failures": dict(
            Counter(row["answer_failure"] for row in diagnostics if row["answer_failure"])
        ),
    }
    for mode in ("answer", "strict"):
        summary[mode] = {}
        for method in ("purist", "pragmatic"):
            count = sum(
                bool(row.get(method + "_correct")) and (mode == "answer" or row["failure"] is None)
                for row in diagnostics
            )
            summary[mode][method] = {
                "correct": count,
                "n": n,
                "agreement": count / n if n else 0.0,
                "ci95": wilson(count, n) if n else None,
            }
    events = study.old.read_lines(ROOT / "attempts.jsonl")
    report = {
        "identity": plan,
        "condition": summary,
        "calls_finished": len(responses),
        "response_models": dict(models),
        "transport_failures": dict(
            Counter(row["error"] for row in responses.values() if row.get("error"))
        ),
        "charge_upper_usd": study.old.charged(events),
        "total_study_charge_upper_usd": plan["prior_charge_upper_usd"] + study.old.charged(events),
        "complete": len(responses) == 750,
        "replay_mode": "saved first responses",
        "scope": "synthetic development; not held-out generalization",
    }
    study.old.write_json(ROOT / "diagnostics.json", diagnostics)
    study.old.write_json(ROOT / "aggregate.json", report)
    RESULTS.mkdir(parents=True, exist_ok=True)
    study.old.write_json(RESULTS / "aggregate.json", report)
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "calls_finished",
                    "condition",
                    "charge_upper_usd",
                    "total_study_charge_upper_usd",
                    "complete",
                )
            }
        ),
        flush=True,
    )
    return report


async def run(jobs: list[dict[str, Any]], plan: dict[str, Any]) -> None:
    from dotenv import dotenv_values

    key = os.getenv("DEEPSEEK_API_KEY") or dotenv_values(".env").get("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError("API key unavailable")
    ledger = study.old.read_lines(ROOT / "attempts.jsonl")
    started = {event["request_id"] for event in ledger}
    pending = [job for job in jobs if job["request_id"] not in started]
    upper = plan["prior_charge_upper_usd"] + study.old.charged(ledger) + sum(
        reserve(job["body"]) for job in pending
    )
    if upper > BUDGET:
        raise ValueError("Full remaining-request reservation exceeds authorized budget")
    print(
        f"Starting {len(pending)} r7 rich calls; timeout {TIMEOUT}s; "
        f"cumulative worst-case bound ${upper:.2f}",
        flush=True,
    )
    spent = plan["prior_charge_upper_usd"] + study.old.charged(ledger)
    stopped = False
    completed = 0
    semaphore = asyncio.Semaphore(study.CONCURRENCY)
    async with httpx.AsyncClient(
        timeout=TIMEOUT, headers={"Authorization": f"Bearer {key}"}
    ) as client:

        async def call(job: dict[str, Any]) -> None:
            nonlocal spent, stopped, completed
            async with semaphore:
                request = job["body"]
                rid = job["request_id"]
                charge = reserve(request)
                if stopped:
                    return
                spent += charge
                start = time.time()
                event = {
                    "request_id": rid,
                    "condition": r7.VERSION,
                    "state": "started",
                    "charged_upper_usd": charge,
                }
                study.old.append(
                    ROOT / "requests.jsonl",
                    {
                        "request_id": rid,
                        "condition": r7.VERSION,
                        "source_row_index": job["record"].source_row_index,
                        "body": request,
                    },
                )
                study.old.append(ROOT / "attempts.jsonl", event)
                response = None
                error = None
                try:
                    returned = await client.post(study.old.API + "/chat/completions", json=request)
                    if returned.status_code == 200:
                        response = returned.json()
                    else:
                        error = f"http_{returned.status_code}"
                        if returned.status_code in (400, 401, 402, 403, 404, 422):
                            stopped = True
                except (httpx.HTTPError, ValueError) as exc:
                    error = type(exc).__name__
                usage = (response or {}).get("usage") or {}
                if "prompt_tokens" in usage and "completion_tokens" in usage:
                    actual = (
                        usage["prompt_tokens"] * study.old.INPUT_PEAK
                        + usage["completion_tokens"] * study.old.OUTPUT_PEAK
                    )
                    spent += actual - charge
                    charge = actual
                study.old.append(
                    ROOT / "responses.jsonl",
                    {"request_id": rid, "response": response, "error": error},
                )
                study.old.append(
                    ROOT / "attempts.jsonl",
                    {
                        **event,
                        "state": "finished",
                        "charged_upper_usd": charge,
                        "usage": usage,
                        "error": error,
                        "elapsed_seconds": time.time() - start,
                    },
                )
                completed += 1
                if completed % 25 == 0:
                    print(
                        f"{completed}/{len(pending)} complete; "
                        f"study cost including active reserves ${spent:.4f}",
                        flush=True,
                    )

        await asyncio.gather(*(call(job) for job in pending))
    analyze(jobs, plan)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "run", "replay"])
    args = parser.parse_args()
    jobs = tasks()
    plan = json.loads(json.dumps(identity()))
    ROOT.mkdir(parents=True, exist_ok=True)
    target = ROOT / "plan.json"
    if args.command == "prepare":
        if target.exists() and study.old.read_json(target) != plan:
            raise ValueError("Existing identity changed")
        study.old.write_json(target, plan)
        print(
            f"Prepared {len(jobs)} r7 rich calls; prior cost ${plan['prior_charge_upper_usd']:.4f}"
        )
        return
    if study.old.read_json(target) != plan:
        raise ValueError("Prepared identity changed")
    if args.command == "run":
        asyncio.run(run(jobs, plan))
    else:
        analyze(jobs, plan)


if __name__ == "__main__":
    main()
