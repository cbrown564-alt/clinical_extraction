"""Frozen r6 test450 replication. Output is aggregate-only; no row diagnostics."""

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

from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation.one_shot_analysis import wilson

ROOT = Path("runs/one_shot_original_r6/test450_timeout600")
ORIGINAL = Path(
    "scratch/holdout/paper/gan_llm_extract_encode_select/deepseek_v41_flash/20260910/comparison.json"
)
TIMEOUT = 600
BUDGET = 100.0


def prepare() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    frozen = study.old.read_json(study.ROOT / "plan.json")
    current = study.identity()
    if current["source_sha256"] != frozen["source_sha256"]:
        raise ValueError("Development source identity changed; do not open a new holdout candidate")
    for key in ("dataset_sha256", "manifest_sha256"):
        if current[key] != frozen[key]:
            raise ValueError("Dataset/split identity changed")
    prior = frozen["prior_charge_upper_usd"] + study.old.charged(
        study.old.read_lines(study.ROOT / "attempts.jsonl")
    )
    records = load_records_for_split("test")
    manifest = study.old.read_json(study.old.DEFAULT_SPLIT_MANIFEST_PATH)
    allowed = set(manifest["splits"]["test"]["source_row_indices"])
    if len(records) != 450 or {r.source_row_index for r in records} != allowed:
        raise ValueError("Holdout coverage mismatch; no row details exposed")
    tasks = []
    for record in records:
        request = study.body(record, "r6_original")
        rid = study.old.digest(
            study.old.encoded({"source_row_index": record.source_row_index, "body": request})
        )
        tasks.append({"record": record, "body": request, "request_id": rid})
    identity = {
        "version": "r6_test450_timeout600_v1",
        "prompt_version": study.r6.VERSION,
        "dataset": "Gan 2026 synthetic",
        "split": "test450",
        "row_policy": "all 450; aggregate-only",
        "source_sha256": current["source_sha256"],
        "runner_sha256": study.old.digest(Path(__file__).read_bytes()),
        "dataset_sha256": current["dataset_sha256"],
        "manifest_sha256": current["manifest_sha256"],
        "original_comparison_sha256": study.old.digest(ORIGINAL.read_bytes()),
        "model": "deepseek-flash",
        "thinking": "enabled",
        "reasoning_effort": "low",
        "max_tokens": 24000,
        "temperature_submitted": 0,
        "temperature_effective": "ignored in thinking mode",
        "timeout_seconds": TIMEOUT,
        "historical_default_timeout_seconds": 600,
        "concurrency": study.CONCURRENCY,
        "budget_usd": BUDGET,
        "prior_charge_upper_usd": prior,
        "retry_policy": "none; no automatic adapter fallback",
        "parser": "same r6 strict envelope and historical raw_model parser used on dev750",
        "scorer": "native Purist/Pragmatic; failures count as wrong",
        "pricing": (
            "peak cache-miss input .30 and output 1.20 per million; unknown usage fully reserved"
        ),
        "prior_exposure": (
            "reused holdout; compare to 20260910 aggregate, not fresh holdout evidence"
        ),
    }
    return tasks, identity


def analyze(tasks: list[dict[str, Any]], identity: dict[str, Any]) -> None:
    responses = {r["request_id"]: r for r in study.old.read_lines(ROOT / "responses.jsonl")}
    totals = {
        "scheduled": 450,
        "attempts_finished": len(responses),
        "record_valid": 0,
        "answer_valid": 0,
        "purist_correct": 0,
        "pragmatic_correct": 0,
    }
    failures: Counter[str] = Counter()
    models: Counter[str] = Counter()
    for task in tasks:
        response = responses.get(task["request_id"], {}).get("response")
        content, finish = study.old.response_content(response)
        try:
            value = study.inspect(content, finish, task["record"], "r6_original")
        except Exception:
            raise RuntimeError(
                "Holdout analysis exception; use development fixtures to investigate"
            ) from None
        for field in ("record_valid", "answer_valid", "purist_correct", "pragmatic_correct"):
            totals[field] += int(bool(value.get(field)))
        if value["failure"]:
            failures[value["failure"]] += 1
        if response:
            models[str(response.get("model"))] += 1
    original = study.old.read_json(ORIGINAL)
    events = study.old.read_lines(ROOT / "attempts.jsonl")
    cost = study.old.charged(events)
    report = {
        "identity": identity,
        "live": totals,
        "failures": dict(failures),
        "response_models": dict(models),
        "original": original,
        "score_comparison": {},
        "charge_upper_usd": cost,
        "total_study_charge_upper_usd": identity["prior_charge_upper_usd"] + cost,
        "transport_failures": dict(
            Counter(r["error"] for r in responses.values() if r.get("error"))
        ),
        "complete": len(responses) == 450,
        "replay_mode": "saved first responses, no new model calls in analysis",
    }
    for method in ("purist", "pragmatic"):
        count = totals[method + "_correct"]
        before = original["summary"][method + "_correct"]
        report["score_comparison"][method] = {
            "original_correct": before,
            "new_correct": count,
            "n": 450,
            "original_agreement": before / 450,
            "new_agreement": count / 450,
            "new_ci95": wilson(count, 450),
            "difference_points": 100 * (count - before) / 450,
        }
    study.old.write_json(ROOT / "aggregate.json", report)
    out = Path("results/letter-benchmarks/gan/one_shot_original_r6/test450_timeout600")
    study.old.write_json(out / "comparison.json", report)
    print(
        json.dumps(
            {
                k: report[k]
                for k in ("live", "failures", "score_comparison", "total_study_charge_upper_usd")
            }
        ),
        flush=True,
    )


async def run(tasks: list[dict[str, Any]], identity: dict[str, Any]) -> None:
    from dotenv import dotenv_values

    key = os.getenv("DEEPSEEK_API_KEY") or dotenv_values(".env").get("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError("API key unavailable")
    events = study.old.read_lines(ROOT / "attempts.jsonl")
    started = {e["request_id"] for e in events}
    pending = [t for t in tasks if t["request_id"] not in started]

    def reserve(body: dict[str, Any]) -> float:
        return (
            len(study.old.encoded(body["messages"])) + 1024
        ) * study.old.INPUT_PEAK + 24000 * study.old.OUTPUT_PEAK

    upper = (
        identity["prior_charge_upper_usd"]
        + study.old.charged(events)
        + sum(reserve(t["body"]) for t in pending)
    )
    if upper > BUDGET:
        raise ValueError("Full remaining-request reservation exceeds authorized budget")
    print(
        f"Starting {len(pending)} r6 test450 calls; timeout 600s; "
        f"cumulative worst-case bound ${upper:.2f}",
        flush=True,
    )
    stopped = False
    completed = 0
    semaphore = asyncio.Semaphore(study.CONCURRENCY)
    async with httpx.AsyncClient(
        timeout=TIMEOUT, headers={"Authorization": f"Bearer {key}"}
    ) as client:

        async def call(task: dict[str, Any]) -> None:
            nonlocal stopped, completed
            async with semaphore:
                if stopped:
                    return
                body = task["body"]
                rid = task["request_id"]
                charge = reserve(body)
                begin = time.time()
                event = {"request_id": rid, "state": "started", "charged_upper_usd": charge}
                study.old.append(ROOT / "attempts.jsonl", event)
                response = None
                error = None
                try:
                    returned = await client.post(study.old.API + "/chat/completions", json=body)
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
                    charge = (
                        usage["prompt_tokens"] * study.old.INPUT_PEAK
                        + usage["completion_tokens"] * study.old.OUTPUT_PEAK
                    )
                study.old.append(
                    ROOT / "responses.jsonl",
                    {"request_id": rid, "response": response, "error": error},
                )
                content, _ = study.old.response_content(response)
                match = study.previous.ENVELOPE.fullmatch(content or "")
                study.old.append(
                    ROOT / "rows.jsonl",
                    {
                        "source_row_index": task["record"].source_row_index,
                        "prompt_version": "gan_llm_extract_encode_select",
                        "raw_output": match[1] if match else (content or ""),
                    },
                )
                study.old.append(
                    ROOT / "attempts.jsonl",
                    {
                        **event,
                        "state": "finished",
                        "charged_upper_usd": charge,
                        "usage": usage,
                        "error": error,
                        "elapsed_seconds": time.time() - begin,
                    },
                )
                completed += 1
                if completed % 25 == 0:
                    print(f"{completed}/{len(pending)} test450 calls finished", flush=True)

        await asyncio.gather(*(call(t) for t in pending))
    analyze(tasks, identity)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "run", "replay"])
    args = parser.parse_args()
    tasks, identity = prepare()
    ROOT.mkdir(parents=True, exist_ok=True)
    target = ROOT / "plan.json"
    if args.command == "prepare":
        if target.exists() and study.old.read_json(target) != identity:
            raise ValueError("Frozen identity changed")
        study.old.write_json(target, identity)
        print("Prepared frozen r6 test450 identity; no model calls.", flush=True)
    else:
        if study.old.read_json(target) != identity:
            raise ValueError("Frozen identity changed")
        if args.command == "run":
            asyncio.run(run(tasks, identity))
        else:
            analyze(tasks, identity)


if __name__ == "__main__":
    main()
