"""Paired minimal/expanded one-call runs on Gan synthetic dev750; one attempt, no repair.

    .venv/bin/python -m scripts.benchmarks.one_call render    # no-call prompt artifacts
    .venv/bin/python -m scripts.benchmarks.one_call prepare   # freeze plan and requests
    .venv/bin/python -m scripts.benchmarks.one_call run       # DeepSeek calls (authorised only)
    .venv/bin/python -m scripts.benchmarks.one_call score     # offline replay of saved responses

Only dev750 is available here. test450 needs its re-annotated reference and a
recorded freeze before any runner may touch it.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

import httpx
from dotenv import dotenv_values

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_DATA_PATH,
    DEFAULT_SPLIT_MANIFEST_PATH,
    SEIZURE_FREQUENCY_KEY,
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.one_call import (
    analysis,
    findings_score,
    parse,
    prompts,
)
from clinical_extraction.tasks.shared.epilepsy.normalization import label_to_frequency_record

ROOT = Path("runs/seizure_frequency/one_call/dev750")
REFERENCE = Path("runs/seizure_frequency/reference/dev750.jsonl")
RESULTS = Path("results/letter-benchmarks/gan/one_call")
MODEL = "deepseek-flash"
API = "https://api.deepseek.com"
MAX_TOKENS = 24000
TIMEOUT = 600
CONCURRENCY = 12


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def encoded(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def read_lines(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def append(path: Path, value: Any) -> None:
    with path.open("a") as stream:
        stream.write(encoded(value).decode() + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def records() -> list[GanFrequencyRecord]:
    loaded = load_records_for_split("validation")
    if len(loaded) != 750:
        raise ValueError("Expected 750 dev750 rows")
    return sorted(loaded, key=lambda r: r.source_row_index)


def gold_categories(record: GanFrequencyRecord) -> dict[str, str]:
    label = record.raw[SEIZURE_FREQUENCY_KEY]["seizure_frequency_number"]
    value = label_to_frequency_record(str(label[0] if isinstance(label, list) else label))
    return {
        "purist": str(map_purist(value.monthly_frequency)),
        "pragmatic": str(map_pragmatic(value.monthly_frequency)),
    }


def body(note: str, condition: prompts.Condition) -> dict[str, Any]:
    return {
        "model": MODEL,
        "messages": prompts.messages(note, condition),
        "temperature": 0,
        "max_tokens": MAX_TOKENS,
        "thinking": {"type": "enabled"},
        "reasoning_effort": "low",
    }


def jobs(conditions: tuple[prompts.Condition, ...]) -> list[dict[str, Any]]:
    """Condition order alternates between letters."""
    output = []
    for i, record in enumerate(records()):
        for condition in conditions if i % 2 == 0 else conditions[::-1]:
            request = body(record.note_text, condition)
            request_id = digest(
                encoded(
                    {
                        "source_row_index": record.source_row_index,
                        "condition": condition,
                        "body": request,
                    }
                )
            )
            output.append(
                {
                    "record": record,
                    "condition": condition,
                    "body": request,
                    "request_id": request_id,
                }
            )
    return output


def identity(conditions: tuple[prompts.Condition, ...]) -> dict[str, Any]:
    return {
        "dataset": "Gan 2026 synthetic",
        "split": "dev750",
        "row_policy": "all 750 split rows including row_ok=False",
        "dataset_sha256": digest(DEFAULT_DATA_PATH.read_bytes()),
        "manifest_sha256": digest(DEFAULT_SPLIT_MANIFEST_PATH.read_bytes()),
        "conditions": list(conditions),
        "prompt_sha256": {
            c: digest(encoded(prompts.messages("<NOTE_TEXT>", c))) for c in conditions
        },
        "schema_sha256": digest(prompts.SCHEMA_PATH.read_bytes()),
        "model": MODEL,
        "provider_documented_version": "DeepSeek-V4.1-Flash",
        "thinking": "enabled",
        "reasoning_effort": "low",
        "temperature_submitted": 0,
        "max_tokens": MAX_TOKENS,
        "timeout_seconds": TIMEOUT,
        "concurrency": CONCURRENCY,
        "retry_policy": "none; first response only",
        "repair_policy": "none",
    }


async def run(selected: list[dict[str, Any]]) -> None:
    key = os.getenv("DEEPSEEK_API_KEY") or dotenv_values(".env").get("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError("API key unavailable")
    ledger = read_lines(ROOT / "attempts.jsonl")
    started = {row["request_id"] for row in ledger}
    pending = [job for job in selected if job["request_id"] not in started]
    print(f"Starting {len(pending)} calls", flush=True)
    semaphore = asyncio.Semaphore(CONCURRENCY)
    stopped = False
    completed = 0
    async with httpx.AsyncClient(
        timeout=TIMEOUT, headers={"Authorization": f"Bearer {key}"}
    ) as client:

        async def call(job: dict[str, Any]) -> None:
            nonlocal stopped, completed
            async with semaphore:
                if stopped:
                    return
                rid, request = job["request_id"], job["body"]
                start = time.time()
                append(
                    ROOT / "requests.jsonl",
                    {
                        "request_id": rid,
                        "source_row_index": job["record"].source_row_index,
                        "condition": job["condition"],
                        "body": request,
                    },
                )
                append(
                    ROOT / "attempts.jsonl",
                    {"request_id": rid, "state": "started"},
                )
                response, error = None, None
                try:
                    returned = await client.post(API + "/chat/completions", json=request)
                    if returned.status_code == 200:
                        response = returned.json()
                    else:
                        error = f"http_{returned.status_code}"
                        stopped = returned.status_code in (400, 401, 402, 403, 404, 422)
                except (httpx.HTTPError, ValueError) as exc:
                    error = type(exc).__name__
                usage = (response or {}).get("usage") or {}
                append(
                    ROOT / "responses.jsonl",
                    {"request_id": rid, "response": response, "error": error},
                )
                append(
                    ROOT / "attempts.jsonl",
                    {
                        "request_id": rid,
                        "state": "finished",
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


def content(response: dict[str, Any] | None) -> tuple[str | None, str | None]:
    choices = (response or {}).get("choices") or []
    if not choices:
        return None, None
    return choices[0].get("message", {}).get("content"), choices[0].get("finish_reason")


def usage_summary(
    selected: list[dict[str, Any]], conditions: tuple[prompts.Condition, ...]
) -> dict[str, Any]:
    """Provider-reported tokens and request latency per condition; no cost estimate."""
    condition_of = {job["request_id"]: job["condition"] for job in selected}
    finished = [
        a
        for a in read_lines(ROOT / "attempts.jsonl")
        if a["state"] == "finished" and a["request_id"] in condition_of
    ]
    summary = {}
    for c in conditions:
        rows = [a for a in finished if condition_of[a["request_id"]] == c]
        seconds = sorted(a["elapsed_seconds"] for a in rows)
        summary[c] = {
            "finished": len(rows),
            "prompt_tokens": sum(a["usage"].get("prompt_tokens", 0) for a in rows),
            "completion_tokens": sum(a["usage"].get("completion_tokens", 0) for a in rows),
            "median_seconds": seconds[len(seconds) // 2] if seconds else None,
        }
    return summary


def score(selected: list[dict[str, Any]], conditions: tuple[prompts.Condition, ...]) -> None:
    saved = {row["request_id"]: row for row in read_lines(ROOT / "responses.jsonl")}
    reference = {row["source_row_index"]: row for row in read_lines(REFERENCE)}
    correct: dict[str, dict[str, list[bool]]] = {
        c: {view: [] for view in ("purist", "pragmatic", "answer_purist", "answer_pragmatic")}
        for c in conditions
    }
    failures: dict[str, dict[str, int]] = {c: {} for c in conditions}
    quotes = {c: [0, 0] for c in conditions}
    letters, per_letter = [], []
    for job in selected:
        record, condition = job["record"], job["condition"]
        raw = saved.get(job["request_id"])
        text, finish = content(raw.get("response") if raw else None)
        checked = parse.inspect(text, finish, record.note_text, condition)
        gold = gold_categories(record)
        for method in ("purist", "pragmatic"):
            match = (
                checked["categories"] is not None and checked["categories"][method] == gold[method]
            )
            correct[condition][method].append(checked["failure"] is None and match)
            correct[condition]["answer_" + method].append(
                checked["answer_failure"] is None and match
            )
        if checked["failure"]:
            failures[condition][checked["failure"]] = (
                failures[condition].get(checked["failure"], 0) + 1
            )
        quotes[condition][0] += checked["exact_quotes"]
        quotes[condition][1] += checked["quote_slots"]
        per_letter.append(
            {
                "source_row_index": record.source_row_index,
                "condition": condition,
                "failure": checked["failure"],
                "label": checked["label"],
                "gold": gold,
            }
        )
        if condition == "expanded" and REFERENCE.exists():
            ref = reference[record.source_row_index]
            if ref["source_sha256"] != digest(record.note_text.encode()):
                raise ValueError(f"Reference source hash differs for {record.source_row_index}")
            letters.append(
                {
                    "source_row_index": record.source_row_index,
                    "note": record.note_text,
                    "reference": ref["findings"],
                    "predicted": checked["findings"] if checked["failure"] is None else None,
                }
            )
    summary: dict[str, Any] = {
        "identity": identity(conditions),
        "responses_saved": sum(job["request_id"] in saved for job in selected),
        "scheduled": len(selected),
        "usage": usage_summary(selected, conditions),
        "conditions": {
            c: {
                "primary_whole_response": {
                    m: analysis.agreement(correct[c][m]) for m in analysis.METHODS
                },
                "declared_answer_only": {
                    m: analysis.agreement(correct[c]["answer_" + m]) for m in analysis.METHODS
                },
                "failures": failures[c],
                "exact_quotes": {"exact": quotes[c][0], "slots": quotes[c][1]},
            }
            for c in conditions
        },
    }
    if set(conditions) == set(prompts.CONDITIONS):
        summary["paired"] = {
            m: analysis.paired(correct["expanded"][m], correct["minimal"][m])
            for m in analysis.METHODS
        }
    local: dict[str, Any] = {"per_letter": per_letter}
    if letters:
        summary["findings"], local["findings"] = findings_score.score(letters)
        summary["reference_sha256"] = digest(REFERENCE.read_bytes())
    write_json(RESULTS / "dev750" / "score.json", summary)
    write_json(ROOT / "per_letter.json", local)
    print(json.dumps({k: v for k, v in summary.items() if k != "identity"}, indent=2))


def render() -> None:
    target = RESULTS / "rendered"
    for condition in prompts.CONDITIONS:
        write_json(
            target / f"{condition}.messages.json", prompts.messages("<NOTE_TEXT>", condition)
        )
    write_json(target / "expanded.schema.json", prompts.EXPANDED_SCHEMA)
    print(f"Rendered prompts to {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("render", "prepare", "run", "score"))
    parser.add_argument(
        "--conditions", nargs="+", choices=prompts.CONDITIONS, default=list(prompts.CONDITIONS)
    )
    args = parser.parse_args()
    if args.command == "render":
        render()
        return
    conditions = tuple(args.conditions)
    selected, plan = jobs(conditions), identity(conditions)
    target = ROOT / "plan.json"
    if args.command == "prepare":
        if target.exists() and json.loads(target.read_text()) != plan:
            raise ValueError("Existing plan changed")
        write_json(target, plan)
        print(f"Prepared {len(selected)} calls")
        return
    if json.loads(target.read_text()) != plan:
        raise ValueError("Prepared plan changed")
    if args.command == "run":
        asyncio.run(run(selected))
    else:
        score(selected, conditions)


if __name__ == "__main__":
    main()
