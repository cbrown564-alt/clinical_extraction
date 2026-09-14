"""Dev750 comparison: r4 simple, r5 rich and r6 original. Thinking is the default."""

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

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_measurements_dev as previous,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation.gan_cell_replay import (
    score_label,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation.one_shot_analysis import (
    summarize,
    wilson,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r5 as r5
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_original_r6 as r6

old = previous.old
r4 = previous.v2
ROOT = Path("runs/one_shot_thinking_r4_r5_r6/dev750")
CONDITIONS = ("r4_simple", "r5_rich", "r6_original")
THINKING = "enabled"
REASONING_EFFORT = "low"
MAX_TOKENS = 24000
CONCURRENCY = 12
BUDGET = 20.0
TIMEOUT = 300


def body(record: GanFrequencyRecord, condition: str) -> dict[str, Any]:
    if condition == "r4_simple":
        messages = r4.messages(record.note_text, "simple")
    elif condition == "r5_rich":
        messages = r5.messages(record.note_text)
    elif condition == "r6_original":
        messages = r6.messages(record)
    else:
        raise ValueError("Unknown condition")
    return {
        "model": old.MODEL,
        "messages": messages,
        "temperature": 0,
        "max_tokens": MAX_TOKENS,
        "thinking": {"type": THINKING},
        "reasoning_effort": REASONING_EFFORT,
    }


def inspect(
    content: str | None, finish: str | None, record: GanFrequencyRecord, condition: str
) -> dict[str, Any]:
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
    match = previous.ENVELOPE.fullmatch(content or "")
    if not match or "[[ ##" in match[1]:
        failure = "invalid_envelope" if content else "no_response"
        result.update(failure=failure, answer_failure=failure)
        return result
    raw = match[1]
    result["structured_json"] = raw
    if condition == "r6_original":
        try:
            extraction = r6.parse(raw, record)
        except (ValueError, TypeError, KeyError):
            extraction = None
        if extraction is None:
            result.update(
                failure="historical_parse_failure", answer_failure="historical_parse_failure"
            )
            return result
        label = extraction.selection.final_label
        scored = score_label(record, label)
        result.update(
            label=label,
            record_valid=True,
            answer_valid=scored["scorable"],
            answer_failure=None if scored["scorable"] else "unscorable_label",
            failure=None if scored["scorable"] else "unscorable_label",
        )
        result.update({m + "_correct": scored[m + "_correct"] for m in ("purist", "pragmatic")})
        return result
    try:
        payload = json.loads(raw, object_pairs_hook=r4.v1._unique_object)
    except (ValueError, TypeError):
        result.update(failure="invalid_syntax", answer_failure="invalid_syntax")
        return result
    answer = payload.get("answer") if isinstance(payload, dict) else None
    checked = r4.v1.inspect_output(json.dumps({"answer": answer}), record.note_text, "simple")
    result.update(
        answer_failure=checked["failure"],
        answer_valid=checked["failure"] is None,
        label=checked["label"],
    )
    for method in ("purist", "pragmatic"):
        gold = old.gold_categories(record.raw)[method]
        result[method + "_correct"] = (
            result["answer_valid"] and checked["categories"][method] == gold
        )
    try:
        (r5.Rich if condition == "r5_rich" else r4.v1.Simple).model_validate(payload)
        result["record_valid"] = True
    except ValidationError:
        result["failure"] = "invalid_schema"
    if result["failure"] is None:
        result["failure"] = checked["failure"]
    return result


def records() -> list[GanFrequencyRecord]:
    permitted = previous.rows()
    loaded = load_records_for_split("validation")
    assert len(loaded) == 750 and {r.source_row_index for r in loaded} == {
        r["source_row_index"] for r in permitted
    }
    return sorted(loaded, key=lambda r: r.source_row_index)


def jobs(selected: list[GanFrequencyRecord]) -> list[dict[str, Any]]:
    tasks = []
    for i, record in enumerate(selected):
        order = CONDITIONS[i % 3 :] + CONDITIONS[: i % 3]
        for condition in order:
            request = body(record, condition)
            rid = old.digest(
                old.encoded(
                    {"id": record.source_row_index, "condition": condition, "body": request}
                )
            )
            tasks.append(
                {"record": record, "condition": condition, "body": request, "request_id": rid}
            )
    return tasks


def identity() -> dict[str, Any]:
    prior = sum(
        old.charged(old.read_lines(p))
        for p in (old.ROOT / "attempts.jsonl", previous.ROOT / "attempts.jsonl")
    )
    source_root = Path("src/clinical_extraction")
    return {
        "version": "thinking_comparison_v1",
        "conditions": CONDITIONS,
        "dataset": "Gan 2026 synthetic",
        "split": "dev750",
        "row_policy": "all development rows including row_ok=False; failures retained",
        "dataset_sha256": old.digest(old.DEFAULT_DATA_PATH.read_bytes()),
        "manifest_sha256": old.digest(old.DEFAULT_SPLIT_MANIFEST_PATH.read_bytes()),
        "model": old.MODEL,
        "provider_documented_version": "DeepSeek-V4.1-Flash",
        "thinking": THINKING,
        "reasoning_effort": REASONING_EFFORT,
        "temperature_submitted": 0,
        "temperature_effective": "ignored by provider in thinking mode",
        "max_tokens": MAX_TOKENS,
        "timeout_seconds": TIMEOUT,
        "concurrency": CONCURRENCY,
        "cache": "no local response cache",
        "budget_usd": BUDGET,
        "prior_charge_upper_usd": prior,
        "pricing": {"input_per_million": 0.30, "output_per_million": 1.20, "checked": "2026-09-14"},
        "retry_policy": "none; saved first response; no automatic JSONAdapter fallback",
        "repair_policy": {
            "r4_simple": "none",
            "r5_rich": "none",
            "r6_original": "historical raw_model parser",
        },
        "scoring": (
            "native Purist/Pragmatic; r4/r5 independent declared answer + whole-record "
            "strict; r6 historical selection"
        ),
        "source_sha256": {
            str(p): old.digest(p.read_bytes()) for p in sorted(source_root.rglob("*.py"))
        },
    }


def analyze(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    responses = {r["request_id"]: r for r in old.read_lines(ROOT / "responses.jsonl")}
    checked = {}
    diagnostics = []
    models: Counter[str] = Counter()
    for job in tasks:
        saved = responses.get(job["request_id"], {})
        content, finish = old.response_content(saved.get("response"))
        value = inspect(content, finish, job["record"], job["condition"])
        checked[(job["record"].source_row_index, job["condition"])] = value
        diagnostics.append(
            {
                "source_row_index": job["record"].source_row_index,
                "condition": job["condition"],
                **value,
            }
        )
        if saved.get("response"):
            models[str(saved["response"].get("model"))] += 1
    report: dict[str, Any] = {
        "identity": old.read_json(ROOT / "plan.json"),
        "conditions": {},
        "paired": {},
        "calls_finished": len(responses),
        "response_models": dict(models),
    }
    for condition in CONDITIONS:
        values = [v for (_, c), v in checked.items() if c == condition]
        n = len(values)
        summary = {
            "n": n,
            "record_valid": sum(v["record_valid"] for v in values),
            "answer_valid": sum(v["answer_valid"] for v in values),
            "failures": dict(Counter(v["failure"] for v in values if v["failure"])),
            "answer_failures": dict(
                Counter(v["answer_failure"] for v in values if v["answer_failure"])
            ),
        }
        for mode in ("answer", "strict"):
            summary[mode] = {}
            for method in ("purist", "pragmatic"):
                count = sum(
                    bool(v.get(method + "_correct")) and (mode == "answer" or v["failure"] is None)
                    for v in values
                )
                summary[mode][method] = {
                    "correct": count,
                    "n": n,
                    "agreement": count / n,
                    "ci95": wilson(count, n),
                }
        report["conditions"][condition] = summary
    ids = sorted({i for i, _ in checked})
    # Reuse the existing paired bootstrap without changing the historical scorer.
    for left, right in (
        ("r5_rich", "r4_simple"),
        ("r6_original", "r4_simple"),
        ("r5_rich", "r6_original"),
    ):
        for mode in ("answer", "strict"):
            pairs = []
            for i in ids:
                pair = {}
                for alias, condition in (("rich", left), ("simple", right)):
                    value = checked[(i, condition)]
                    stub = r4.v1.inspect_output(None, "", "simple")
                    for method in ("purist", "pragmatic"):
                        stub[method + "_correct"] = bool(value.get(method + "_correct")) and (
                            mode == "answer" or value["failure"] is None
                        )
                    pair[alias] = stub
                pairs.append(pair)
            report["paired"][left + " minus " + right + " " + mode] = summarize(pairs)["paired"]
    attempts = old.read_lines(ROOT / "attempts.jsonl")
    report["charge_upper_usd"] = old.charged(attempts)
    report["total_study_charge_upper_usd"] = (
        report["charge_upper_usd"] + report["identity"]["prior_charge_upper_usd"]
    )
    old.write_json(ROOT / "diagnostics.json", diagnostics)
    old.write_json(ROOT / "aggregate.json", report)
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "calls_finished",
                    "conditions",
                    "charge_upper_usd",
                    "total_study_charge_upper_usd",
                )
            }
        ),
        flush=True,
    )
    return report


async def run(tasks: list[dict[str, Any]]) -> None:
    from dotenv import dotenv_values

    key = os.getenv("DEEPSEEK_API_KEY") or dotenv_values(".env").get("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError("API key unavailable")
    ledger = old.read_lines(ROOT / "attempts.jsonl")
    started = {x["request_id"] for x in ledger}
    pending = [j for j in tasks if j["request_id"] not in started]
    spent = old.read_json(ROOT / "plan.json")["prior_charge_upper_usd"] + old.charged(ledger)
    stopped = False
    completed = 0
    semaphore = asyncio.Semaphore(CONCURRENCY)
    async with httpx.AsyncClient(
        timeout=TIMEOUT, headers={"Authorization": f"Bearer {key}"}
    ) as client:

        async def call(job: dict[str, Any]) -> None:
            nonlocal spent, stopped, completed
            async with semaphore:
                request = job["body"]
                rid = job["request_id"]
                reserve = (
                    len(old.encoded(request["messages"])) + 1024
                ) * old.INPUT_PEAK + MAX_TOKENS * old.OUTPUT_PEAK
                if stopped:
                    return
                if spent + reserve > BUDGET:
                    stopped = True
                    print("Budget stop; no retries.", flush=True)
                    return
                spent += reserve
                start = time.time()
                event = {
                    "request_id": rid,
                    "condition": job["condition"],
                    "state": "started",
                    "charged_upper_usd": reserve,
                }
                old.append(
                    ROOT / "requests.jsonl",
                    {
                        "request_id": rid,
                        "condition": job["condition"],
                        "source_row_index": job["record"].source_row_index,
                        "body": request,
                    },
                )
                old.append(ROOT / "attempts.jsonl", event)
                response = None
                error = None
                try:
                    returned = await client.post(old.API + "/chat/completions", json=request)
                    if returned.status_code == 200:
                        response = returned.json()
                    else:
                        error = f"http_{returned.status_code}"
                        if returned.status_code in (400, 401, 402, 403, 404, 422):
                            stopped = True
                except (httpx.HTTPError, ValueError) as exc:
                    error = type(exc).__name__
                usage = (response or {}).get("usage") or {}
                charge = reserve
                if "prompt_tokens" in usage and "completion_tokens" in usage:
                    charge = (
                        usage["prompt_tokens"] * old.INPUT_PEAK
                        + usage["completion_tokens"] * old.OUTPUT_PEAK
                    )
                spent += charge - reserve
                old.append(
                    ROOT / "responses.jsonl",
                    {"request_id": rid, "response": response, "error": error},
                )
                old.append(
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
                if completed % 30 == 0:
                    print(
                        f"{completed}/{len(pending)} complete; "
                        f"total including active reserves ${spent:.4f}",
                        flush=True,
                    )

        await asyncio.gather(*(call(j) for j in pending))
    analyze(tasks)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "run", "replay"])
    args = parser.parse_args()
    tasks = jobs(records())
    plan = identity()
    # Round-trip normalizes tuples for comparison to persisted JSON.
    plan = json.loads(json.dumps(plan))
    ROOT.mkdir(parents=True, exist_ok=True)
    target = ROOT / "plan.json"
    if args.command == "prepare":
        if target.exists() and old.read_json(target) != plan:
            raise ValueError("Existing identity changed")
        old.write_json(target, plan)
        print(
            f"Prepared {len(tasks)} calls; thinking enabled/low, "
            f"prior cost ${plan['prior_charge_upper_usd']:.4f}"
        )
    else:
        if old.read_json(target) != plan:
            raise ValueError("Prepared identity changed")
        if args.command == "run":
            asyncio.run(run(tasks))
        else:
            analyze(tasks)


if __name__ == "__main__":
    main()
