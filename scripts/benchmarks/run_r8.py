"""R8 rich versus paired r4 simple on synthetic Gan dev750 or test450.

Thinking enabled/low, 24,000-token limit, 600-second timeout, no retries or repairs.
Answer agreement uses native Purist/Pragmatic scoring; finding correctness and
completeness use the frozen guide v0.7 reference and finding_matching_v07. The test450
run writes aggregates only: no row-level diagnostics are produced for the holdout.
Frozen r4–r7 requests and runners are unchanged.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import random
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
    finding_matching_v07 as fm,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation.one_shot_analysis import wilson
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r8 as r8

CONDITIONS = ("r8_rich", "r4_simple")
TIMEOUT = 600
BUDGET = 100.0
MAX_TOKENS = 24000
SEED = 20260913
BOOTSTRAPS = 10000
PRIOR_LEDGERS = (
    Path("runs/one_shot_frequency_v1/attempts.jsonl"),
    Path("runs/one_shot_frequency_v2_measurements_r4/dev750/attempts.jsonl"),
    Path("runs/one_shot_thinking_r4_r5_r6/dev750/attempts.jsonl"),
    Path("runs/one_shot_thinking_r4_r5_r6/dev750/timeout600/attempts.jsonl"),
    Path("runs/one_shot_original_r6/test450_timeout600/attempts.jsonl"),
    Path("runs/one_shot_frequency_v2_measurements_r7/dev750/attempts.jsonl"),
    Path("runs/one_shot_frequency_v2_measurements_r7/dev750/timeout600/attempts.jsonl"),
    Path("runs/one_shot_frequency_v2_measurements_r8/dev750/attempts.jsonl"),
    Path("runs/one_shot_frequency_v2_measurements_r8/test450/attempts.jsonl"),
)
SPLITS = {"dev750": ("validation", 750), "test450": ("test", 450)}


def root(split: str, *, rich_only: bool = False) -> Path:
    name = "dev750_rich_only" if rich_only else split
    return Path("runs/one_shot_frequency_v2_measurements_r8") / name


def results(split: str, *, rich_only: bool = False) -> Path:
    name = "dev750_rich_only" if rich_only else split
    return Path("results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r8") / name


def body(record: GanFrequencyRecord, condition: str) -> dict[str, Any]:
    if condition == "r8_rich":
        messages = r8.messages(record.note_text)
    else:
        messages = study.r4.messages(record.note_text, "simple")
    return {
        "model": study.old.MODEL,
        "messages": messages,
        "temperature": 0,
        "max_tokens": MAX_TOKENS,
        "thinking": {"type": "enabled"},
        "reasoning_effort": "low",
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
        "findings": None,
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
        if condition == "r8_rich":
            rich = r8.Rich.model_validate(payload)
            result["findings"] = [f.model_dump(exclude_none=True) for f in rich.findings]
        else:
            study.r4.v1.Simple.model_validate(payload)
        result["record_valid"] = True
    except ValidationError:
        result["failure"] = "invalid_schema"
    if result["failure"] is None:
        result["failure"] = checked["failure"]
    return result


def prior_charge(split: str, *, rich_only: bool = False) -> float:
    own = root(split, rich_only=rich_only) / "attempts.jsonl"
    return sum(study.old.charged(study.old.read_lines(p)) for p in PRIOR_LEDGERS if p != own)


def records(split: str) -> list[GanFrequencyRecord]:
    name, expected = SPLITS[split]
    loaded = load_records_for_split(name)
    if len(loaded) != expected:
        raise ValueError(f"Expected {expected} {split} rows")
    return sorted(loaded, key=lambda r: r.source_row_index)


def tasks(split: str, *, rich_only: bool = False) -> list[dict[str, Any]]:
    jobs = []
    active = ("r8_rich",) if rich_only else CONDITIONS
    for i, record in enumerate(records(split)):
        order = active if i % 2 == 0 else active[::-1]
        for condition in order:
            request = body(record, condition)
            rid = study.old.digest(
                study.old.encoded(
                    {
                        "source_row_index": record.source_row_index,
                        "version": r8.VERSION,
                        "revision": r8.REVISION,
                        "condition": condition,
                        "body": request,
                    }
                )
            )
            jobs.append(
                {"record": record, "condition": condition, "body": request, "request_id": rid}
            )
    return jobs


def identity(split: str, reference: Path, *, rich_only: bool = False) -> dict[str, Any]:
    paths = [
        Path(__file__),
        Path(r8.__file__),
        Path(fm.__file__),
        Path(r8.r5.__file__),
        Path(r8.r4.__file__),
    ]
    active = ("r8_rich",) if rich_only else CONDITIONS
    return {
        "version": "r8_rich_only_timeout600_v1" if rich_only else "r8_paired_timeout600_v1",
        "conditions": active,
        "prompt_version": r8.VERSION,
        "revision": r8.REVISION,
        "guide_version": r8.GUIDE_VERSION,
        "dataset": "Gan 2026 synthetic",
        "split": split,
        "row_policy": "all split rows including row_ok=False; failures retained",
        "dataset_sha256": study.old.digest(study.old.DEFAULT_DATA_PATH.read_bytes()),
        "manifest_sha256": study.old.digest(study.old.DEFAULT_SPLIT_MANIFEST_PATH.read_bytes()),
        "reference_path": str(reference),
        "reference_sha256": study.old.digest(reference.read_bytes()),
        "components": {str(p): study.old.digest(p.read_bytes()) for p in paths},
        "matching_version": fm.MATCHING_VERSION,
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
        "prior_charge_upper_usd": prior_charge(split, rich_only=rich_only),
        "retry_policy": "none; saved first response; no automatic JSONAdapter fallback",
        "repair_policy": "none",
        "scoring": (
            "native Purist/Pragmatic answer agreement; "
            "finding precision/recall/F1 on complete v0.7 reference letters with "
            "finding_matching_v07. Rich-only runs do not repeat r4 simple."
            if rich_only
            else (
                "native Purist/Pragmatic answer agreement per condition with paired bootstrap; "
                "finding precision/recall/F1 on adjudicable v0.7 reference letters (r8_rich only)"
            )
        ),
        "row_level_outputs": "dev750 only; test450 aggregate-only",
        "scope": "synthetic development"
        if split == "dev750"
        else "synthetic reused holdout; aggregate-only",
    }


def reserve(request: dict[str, Any]) -> float:
    return (
        len(study.old.encoded(request["messages"])) + 1024
    ) * study.old.INPUT_PEAK + MAX_TOKENS * study.old.OUTPUT_PEAK


def load_reference(path: Path, selected: list[GanFrequencyRecord]) -> dict[int, dict[str, Any]]:
    by_index = {}
    for row in study.old.read_lines(path):
        by_index[int(row["source_row_index"])] = row
    for record in selected:
        ref = by_index.get(record.source_row_index)
        if ref is None:
            raise ValueError(f"Reference missing row {record.source_row_index}")
        if hashlib.sha256(record.note_text.encode("utf-8")).hexdigest() != ref["source_sha256"]:
            raise ValueError(f"Reference hash mismatch for row {record.source_row_index}")
    return by_index


def paired_bootstrap(rich: list[bool], simple: list[bool]) -> dict[str, Any]:
    n = len(rich)
    rng = random.Random(SEED)
    diffs = []
    for _ in range(BOOTSTRAPS):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append((sum(rich[i] for i in idx) - sum(simple[i] for i in idx)) / n)
    diffs.sort()
    return {
        "difference_points": 100 * (sum(rich) - sum(simple)) / n,
        "ci95_points": [
            100 * diffs[int(0.025 * BOOTSTRAPS)],
            100 * diffs[int(0.975 * BOOTSTRAPS) - 1],
        ],
        "seed": SEED,
        "replicates": BOOTSTRAPS,
    }


def analyze(
    split: str,
    jobs: list[dict[str, Any]],
    plan: dict[str, Any],
    reference: Path,
    *,
    rich_only: bool = False,
) -> dict[str, Any]:
    active = tuple(plan["conditions"])
    out = root(split, rich_only=rich_only)
    responses = {row["request_id"]: row for row in study.old.read_lines(out / "responses.jsonl")}
    selected = records(split)
    refs = load_reference(reference, selected)
    per_condition: dict[str, dict[int, dict[str, Any]]] = {c: {} for c in active}
    models: Counter[str] = Counter()
    for job in jobs:
        saved = responses.get(job["request_id"], {})
        content, finish = study.old.response_content(saved.get("response"))
        value = inspect(content, finish, job["record"], job["condition"])
        per_condition[job["condition"]][job["record"].source_row_index] = value
        if saved.get("response"):
            models[str(saved["response"].get("model"))] += 1
    n = len(selected)
    summary: dict[str, Any] = {}
    for condition in active:
        rows = [per_condition[condition][r.source_row_index] for r in selected]
        block: dict[str, Any] = {
            "n": n,
            "record_valid": sum(row["record_valid"] for row in rows),
            "answer_valid": sum(row["answer_valid"] for row in rows),
            "failures": dict(Counter(row["failure"] for row in rows if row["failure"])),
        }
        for mode in ("answer", "strict"):
            block[mode] = {}
            for method in ("purist", "pragmatic"):
                count = sum(
                    bool(row.get(method + "_correct"))
                    and (mode == "answer" or row["failure"] is None)
                    for row in rows
                )
                block[mode][method] = {
                    "correct": count,
                    "n": n,
                    "agreement": count / n,
                    "ci95": wilson(count, n),
                }
        summary[condition] = block
    paired = None
    if "r4_simple" in active:
        paired = {}
        for method in ("purist", "pragmatic"):
            rich = [
                bool(per_condition["r8_rich"][r.source_row_index].get(method + "_correct"))
                for r in selected
            ]
            simple = [
                bool(per_condition["r4_simple"][r.source_row_index].get(method + "_correct"))
                for r in selected
            ]
            paired[method] = paired_bootstrap(rich, simple)

    letters = []
    diagnostics = []
    excluded = 0
    by_timing: dict[str, Counter[str]] = {"current": Counter(), "historical": Counter()}
    for record in selected:
        ref = refs[record.source_row_index]
        if ref["annotation_state"] != "complete":
            excluded += 1
            continue
        value = per_condition["r8_rich"][record.source_row_index]
        predictions = value["findings"] if value["record_valid"] else None
        scored = fm.score_letter(record.note_text, ref["findings"], predictions)
        letters.append(scored)
        if predictions is not None:
            matched_ref = {pair[1] for pair in scored["pairs"]}
            for finding in ref["findings"]:
                by_timing[finding.get("timing", "current")][
                    "matched" if finding["id"] in matched_ref else "missed"
                ] += 1
        diagnostics.append(
            {
                "source_row_index": record.source_row_index,
                "answers": {
                    c: per_condition[c][record.source_row_index]["label"] for c in active
                },
                "answer_correct": {
                    c: {
                        m: per_condition[c][record.source_row_index].get(m + "_correct")
                        for m in ("purist", "pragmatic")
                    }
                    for c in active
                },
                "findings": scored,
            }
        )
    finding_summary = fm.aggregate(letters) if letters else {"letters": 0}
    finding_summary["excluded_needs_review_letters"] = excluded
    finding_summary["reference_recall_by_timing"] = {k: dict(v) for k, v in by_timing.items()}
    events = study.old.read_lines(out / "attempts.jsonl")
    report = {
        "identity": plan,
        "answer": summary,
        "paired_rich_minus_simple": paired,
        "findings_r8_rich": finding_summary,
        "calls_finished": len(responses),
        "calls_expected": len(jobs),
        "response_models": dict(models),
        "transport_failures": dict(
            Counter(row["error"] for row in responses.values() if row.get("error"))
        ),
        "charge_upper_usd": study.old.charged(events),
        "total_study_charge_upper_usd": plan["prior_charge_upper_usd"] + study.old.charged(events),
        "complete": len(responses) == len(jobs),
        "replay_mode": "saved first responses",
    }
    study.old.write_json(out / "aggregate.json", report)
    if split == "dev750":
        study.old.write_json(out / "diagnostics.json", diagnostics)
    results(split, rich_only=rich_only).mkdir(parents=True, exist_ok=True)
    study.old.write_json(results(split, rich_only=rich_only) / "aggregate.json", report)
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "answer",
                    "paired_rich_minus_simple",
                    "findings_r8_rich",
                    "calls_finished",
                    "charge_upper_usd",
                    "total_study_charge_upper_usd",
                    "complete",
                )
            },
            indent=1,
        ),
        flush=True,
    )
    return report


async def run(
    split: str,
    jobs: list[dict[str, Any]],
    plan: dict[str, Any],
    reference: Path,
    *,
    rich_only: bool = False,
) -> None:
    from dotenv import dotenv_values

    key = os.getenv("DEEPSEEK_API_KEY") or dotenv_values(".env").get("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError("API key unavailable")
    out = root(split, rich_only=rich_only)
    ledger = study.old.read_lines(out / "attempts.jsonl")
    started = {event["request_id"] for event in ledger}
    pending = [job for job in jobs if job["request_id"] not in started]
    upper = (
        plan["prior_charge_upper_usd"]
        + study.old.charged(ledger)
        + sum(reserve(job["body"]) for job in pending)
    )
    if upper > BUDGET:
        raise ValueError(
            f"Full remaining-request reservation ${upper:.2f} exceeds authorized budget"
        )
    print(
        f"Starting {len(pending)} r8 calls on {split}; timeout {TIMEOUT}s; "
        f"worst-case bound ${upper:.2f}",
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
                    "condition": job["condition"],
                    "state": "started",
                    "charged_upper_usd": charge,
                }
                study.old.append(
                    out / "requests.jsonl",
                    {
                        "request_id": rid,
                        "condition": job["condition"],
                        "source_row_index": job["record"].source_row_index,
                        "body": request,
                    },
                )
                study.old.append(out / "attempts.jsonl", event)
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
                    out / "responses.jsonl",
                    {"request_id": rid, "response": response, "error": error},
                )
                study.old.append(
                    out / "attempts.jsonl",
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
                if completed % 50 == 0:
                    print(
                        f"{completed}/{len(pending)} complete; "
                        f"study cost including active reserves ${spent:.4f}",
                        flush=True,
                    )

        await asyncio.gather(*(call(job) for job in pending))
    analyze(split, jobs, plan, reference, rich_only=rich_only)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "run", "replay"])
    parser.add_argument("--split", choices=sorted(SPLITS), required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument(
        "--rich-only",
        action="store_true",
        help="Dev750 R8 rich only. Does not repeat r4 simple and refuses test450.",
    )
    args = parser.parse_args()
    if args.rich_only and args.split != "dev750":
        raise ValueError("Rich-only R8 is dev750 only")
    jobs = tasks(args.split, rich_only=args.rich_only)
    plan = json.loads(
        json.dumps(identity(args.split, args.reference, rich_only=args.rich_only))
    )
    out = root(args.split, rich_only=args.rich_only)
    out.mkdir(parents=True, exist_ok=True)
    target = out / "plan.json"
    if args.command == "prepare":
        if target.exists() and study.old.read_json(target) != plan:
            raise ValueError("Existing identity changed")
        study.old.write_json(target, plan)
        print(
            f"Prepared {len(jobs)} r8 calls on {args.split}; "
            f"prior cost ${plan['prior_charge_upper_usd']:.4f}"
        )
        return
    if study.old.read_json(target) != plan:
        raise ValueError("Prepared identity changed")
    if args.command == "run":
        asyncio.run(
            run(args.split, jobs, plan, args.reference, rich_only=args.rich_only)
        )
    else:
        analyze(args.split, jobs, plan, args.reference, rich_only=args.rich_only)


if __name__ == "__main__":
    main()
