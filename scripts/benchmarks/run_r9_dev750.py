"""Run frozen compact R9 once on all Gan synthetic dev750 rows; no retries."""

from __future__ import annotations

import argparse
import asyncio
import os
import time
from pathlib import Path
from typing import Any

import httpx
from dotenv import dotenv_values

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r9 as r9
from scripts.benchmarks import run_r8

ROOT = Path("runs/one_shot_frequency_v2_measurements_r9/dev750")
REFERENCE = Path("runs/seizure_finding_annotation_compact_v0_1/dev750/scorer_v03/reference.jsonl")
BUDGET = 100.0


def jobs() -> list[dict[str, Any]]:
    output = []
    for record in run_r8.records("dev750"):
        body = {
            "model": study.old.MODEL,
            "messages": r9.messages(record.note_text),
            "temperature": 0,
            "max_tokens": run_r8.MAX_TOKENS,
            "thinking": {"type": "enabled"},
            "reasoning_effort": "low",
        }
        request_id = study.old.digest(
            study.old.encoded(
                {
                    "source_row_index": record.source_row_index,
                    "version": r9.VERSION,
                    "revision": r9.REVISION,
                    "body": body,
                }
            )
        )
        output.append({"record": record, "body": body, "request_id": request_id})
    return output


def identity() -> dict[str, Any]:
    return {
        "dataset": "Gan 2026 synthetic",
        "split": "dev750",
        "row_policy": "all 750 split rows including row_ok=False",
        "dataset_sha256": study.old.digest(study.old.DEFAULT_DATA_PATH.read_bytes()),
        "manifest_sha256": study.old.digest(study.old.DEFAULT_SPLIT_MANIFEST_PATH.read_bytes()),
        "reference_sha256": study.old.digest(REFERENCE.read_bytes()),
        "prompt_version": r9.VERSION,
        "prompt_revision": r9.REVISION,
        "guide_version": r9.GUIDE_VERSION,
        "prompt_sha256": study.old.digest(Path(r9.__file__).read_bytes()),
        "schema_sha256": study.old.digest(r9.SCHEMA_PATH.read_bytes()),
        "model": study.old.MODEL,
        "provider_documented_version": "DeepSeek-V4.1-Flash",
        "thinking": "enabled",
        "reasoning_effort": "low",
        "max_tokens": run_r8.MAX_TOKENS,
        "timeout_seconds": run_r8.TIMEOUT,
        "concurrency": study.CONCURRENCY,
        "budget_usd": BUDGET,
        "retry_policy": "none; first response only",
        "repair_policy": "none",
        "replay_mode": "saved first responses",
        "scorer": "finding_compact_v03_v2; native Purist/Pragmatic answer",
    }


def reserve(body: dict[str, Any]) -> float:
    return (
        len(study.old.encoded(body["messages"])) + 1024
    ) * study.old.INPUT_PEAK + run_r8.MAX_TOKENS * study.old.OUTPUT_PEAK


async def run(selected: list[dict[str, Any]], plan: dict[str, Any]) -> None:
    key = os.getenv("DEEPSEEK_API_KEY") or dotenv_values(".env").get("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError("API key unavailable")
    ledger = study.old.read_lines(ROOT / "attempts.jsonl")
    started = {row["request_id"] for row in ledger}
    pending = [job for job in selected if job["request_id"] not in started]
    prior = run_r8.prior_charge("dev750", rich_only=True)
    prior += study.old.charged(
        study.old.read_lines(
            Path("runs/one_shot_frequency_v2_measurements_r8/dev750_rich_only/attempts.jsonl")
        )
    )
    bound = prior + study.old.charged(ledger) + sum(reserve(job["body"]) for job in pending)
    if bound > BUDGET:
        raise ValueError(f"Remaining request reservation ${bound:.2f} exceeds ${BUDGET:.2f} budget")
    print(
        f"Starting {len(pending)} R9 dev750 calls; worst-case study bound ${bound:.2f}", flush=True
    )
    semaphore = asyncio.Semaphore(study.CONCURRENCY)
    stopped = False
    completed = 0
    async with httpx.AsyncClient(
        timeout=run_r8.TIMEOUT, headers={"Authorization": f"Bearer {key}"}
    ) as client:

        async def call(job: dict[str, Any]) -> None:
            nonlocal stopped, completed
            async with semaphore:
                if stopped:
                    return
                rid, body = job["request_id"], job["body"]
                charge = reserve(body)
                start = time.time()
                study.old.append(
                    ROOT / "requests.jsonl",
                    {
                        "request_id": rid,
                        "source_row_index": job["record"].source_row_index,
                        "body": body,
                    },
                )
                study.old.append(
                    ROOT / "attempts.jsonl",
                    {"request_id": rid, "state": "started", "charged_upper_usd": charge},
                )
                response, error = None, None
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
                study.old.append(
                    ROOT / "attempts.jsonl",
                    {
                        "request_id": rid,
                        "state": "finished",
                        "charged_upper_usd": charge,
                        "usage": usage,
                        "error": error,
                        "elapsed_seconds": time.time() - start,
                    },
                )
                completed += 1
                if completed % 50 == 0:
                    print(f"{completed}/{len(pending)} finished", flush=True)

        await asyncio.gather(*(call(job) for job in pending))
    print(f"Finished {completed} calls; stopped={stopped}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run"))
    args = parser.parse_args()
    selected, plan = jobs(), identity()
    ROOT.mkdir(parents=True, exist_ok=True)
    target = ROOT / "plan.json"
    if args.command == "prepare":
        if target.exists() and study.old.read_json(target) != plan:
            raise ValueError("Existing plan changed")
        study.old.write_json(target, plan)
        print(f"Prepared {len(selected)} R9 dev750 calls")
        return
    if study.old.read_json(target) != plan:
        raise ValueError("Prepared plan changed")
    asyncio.run(run(selected, plan))


if __name__ == "__main__":
    main()
