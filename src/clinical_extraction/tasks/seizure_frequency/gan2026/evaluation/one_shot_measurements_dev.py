"""Paired v2 development execution; no test or patient split execution path."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any

import httpx

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import one_shot_study as old
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation.one_shot_analysis import (
    summarize,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements as v2

ROOT = Path("runs") / v2.VERSION / "dev750"
MAX_TOKENS = 4096
CONCURRENCY = 6
ENVELOPE = re.compile(
    r"\s*\[\[ ## structured_json ## \]\]\s*(.*?)\s*(?:\[\[ ## completed ## \]\]\s*)?", re.S
)


def rows() -> list[dict[str, Any]]:
    manifest = old.read_json(old.DEFAULT_SPLIT_MANIFEST_PATH)
    if old.digest(old.DEFAULT_DATA_PATH.read_bytes()) != manifest["dataset_sha256"]:
        raise ValueError("Dataset hash mismatch")
    ids = manifest["splits"]["validation"]["source_row_indices"]
    if len(ids) != 750 or len(set(ids)) != 750:
        raise ValueError("Expected exactly 750 development IDs")
    if set(ids) & set(manifest["splits"]["test"]["source_row_indices"]):
        raise ValueError("Development/test overlap")
    allowed = set(ids)
    selected = [r for r in old.read_json(old.DEFAULT_DATA_PATH) if r["source_row_index"] in allowed]
    if len(selected) != 750 or {r["source_row_index"] for r in selected} != allowed:
        raise ValueError("Missing or duplicate development rows")
    return sorted(selected, key=lambda r: r["source_row_index"])


def body(note: str, condition: v2.v1.Condition) -> dict[str, Any]:
    return {
        "model": old.MODEL,
        "messages": v2.messages(note, condition),
        "max_tokens": MAX_TOKENS,
        "temperature": 0,
        "thinking": {"type": "disabled"},
    }


def inspect(
    content: str | None, note: str, condition: v2.v1.Condition, finish: str | None = "stop"
) -> dict[str, Any]:
    result = v2.v1.inspect_output(None, note, condition)
    result["received"] = content is not None
    result["envelope_valid"] = False
    result["structured_json"] = None
    if finish == "length":
        result["failure"] = "truncation"
        return result
    if not content:
        return result
    match = ENVELOPE.fullmatch(content)
    if not match or "[[ ##" in match[1]:
        result["failure"] = "invalid_envelope"
        return result
    raw = match[1]
    checked = v2.inspect_output(raw, note, condition)
    result.update(checked)
    result.update(envelope_valid=True, structured_json=raw, received=True)
    if condition == "rich":
        output = checked.get("output")
        result["schema_valid"] = output is not None or checked["failure"] == "invalid_target_label"
        if output is not None:
            findings = output["findings"]
            result.update(
                label=output["answer"]["label"],
                finding_count=len(findings),
                finding_types=[f["measurement"]["kind"] for f in findings],
                finding_certainties=[f["event"]["seizure_interpretation"] for f in findings],
                finding_temporalities=[f["temporal_status"] for f in findings],
                no_evidence_state=output["answer"]["label"] == "no seizure frequency reference",
            )
        result["all_quotes_exact"] = (
            bool(result["quote_slots"]) and result["quote_slots"] == result["exact_quotes"]
        )
    return result


def plan(selected: list[dict[str, Any]]) -> dict[str, Any]:
    previous = old.charged(old.read_lines(old.ROOT / "attempts.jsonl"))
    paths = [
        Path(__file__),
        Path(v2.__file__),
        Path(v2.v1.__file__),
        Path(v2.v1.historical.__file__),
        Path(old.__file__),
        Path(old.one_shot_analysis.__file__),
        Path("src/clinical_extraction/tasks/shared/epilepsy/normalization.py"),
        Path("src/clinical_extraction/tasks/seizure_frequency/gan2026/labels.py"),
    ]
    return {
        "version": v2.VERSION,
        "split": "dev750",
        "source_row_indices": [r["source_row_index"] for r in selected],
        "dataset_sha256": old.digest(old.DEFAULT_DATA_PATH.read_bytes()),
        "manifest_sha256": old.digest(old.DEFAULT_SPLIT_MANIFEST_PATH.read_bytes()),
        "components": {str(p): old.digest(p.read_bytes()) for p in paths},
        "empty_requests": {c: body("", c) for c in v2.v1.CONDITIONS},
        "model": old.MODEL,
        "provider_documented_version": "DeepSeek-V4.1-Flash",
        "base_url": old.API,
        "max_tokens": MAX_TOKENS,
        "concurrency": CONCURRENCY,
        "timeout_seconds": old.TIMEOUT,
        "retry_policy": "none",
        "repair_policy": "none",
        "envelope_policy": (
            "one structured_json ChatAdapter section; optional completed marker; strict JSON inside"
        ),
        "response_format": "text, matching the ChatAdapter envelope",
        "row_policy": "all 750 development rows including row_ok=False; failures count as wrong",
        "scorer": "native purist/pragmatic via label_to_frequency_record; one_shot_analysis_v1",
        "prior_exposure": "development corpus used in previous studies and targeted wording audit",
        "budget_total_usd": 10,
        "prior_v1_charge_upper_usd": previous,
        "input_per_million_usd": 0.30,
        "output_per_million_usd": 1.20,
        "pricing_checked": "2026-09-14",
        "pricing_url": "https://api-docs.deepseek.com/quick_start/pricing/",
        "budget_policy": (
            "reserve UTF-8 input-byte bound plus full output limit before each call; "
            "release to peak-price usage after response"
        ),
    }


def jobs(
    selected: list[dict[str, Any]],
) -> list[tuple[dict[str, Any], v2.v1.Condition, dict[str, Any], str]]:
    result = []
    for i, row in enumerate(selected):
        for c in v2.v1.CONDITIONS if i % 2 == 0 else tuple(reversed(v2.v1.CONDITIONS)):
            request = body(old.note_text(row), c)
            rid = old.digest(
                old.encoded({"source_row_index": row["source_row_index"], "body": request})
            )
            result.append((row, c, request, rid))
    return result


def analyze(selected: list[dict[str, Any]], identity: dict[str, Any]) -> dict[str, Any]:
    responses = {r["request_id"]: r for r in old.read_lines(ROOT / "responses.jsonl")}
    paired: dict[int, dict[str, Any]] = {}
    diagnostics = []
    models: Counter[str] = Counter()
    for row, condition, _, rid in jobs(selected):
        saved = responses.get(rid, {})
        response = saved.get("response")
        content, finish = old.response_content(response)
        checked = inspect(content, old.note_text(row), condition, finish)
        for method, gold in old.gold_categories(row).items():
            checked[method + "_correct"] = (
                checked["failure"] is None and checked["categories"][method] == gold
            )
        paired.setdefault(row["source_row_index"], {})[condition] = checked
        diagnostics.append(
            {
                "source_row_index": row["source_row_index"],
                "condition": condition,
                "request_id": rid,
                **checked,
            }
        )
        if response:
            models[str(response.get("model"))] += 1
    report = summarize(list(paired.values()))
    attempts = old.read_lines(ROOT / "attempts.jsonl")
    report.update(
        execution_identity=identity,
        response_models=dict(models),
        calls_finished=len(responses),
        peak_charge_upper_usd=old.charged(attempts),
        total_study_charge_upper_usd=identity["prior_v1_charge_upper_usd"] + old.charged(attempts),
        scope="synthetic development; not held-out generalization",
        replay_mode="saved first responses",
        row_ok_false_included=sum(not r["row_ok"] for r in selected),
    )
    old.write_json(ROOT / "development_diagnostics.json", diagnostics)
    old.write_json(ROOT / "aggregate.json", report)
    print(
        json.dumps(
            {
                k: report[k]
                for k in ("calls_finished", "peak_charge_upper_usd", "conditions", "paired")
            }
        ),
        flush=True,
    )
    return report


async def run(selected: list[dict[str, Any]], identity: dict[str, Any]) -> None:
    from dotenv import dotenv_values

    key = os.getenv("DEEPSEEK_API_KEY") or dotenv_values(".env").get("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError("API key unavailable")
    attempts = old.read_lines(ROOT / "attempts.jsonl")
    started = {a["request_id"] for a in attempts}
    pending = [j for j in jobs(selected) if j[3] not in started]
    spent = identity["prior_v1_charge_upper_usd"] + old.charged(attempts)
    semaphore = asyncio.Semaphore(CONCURRENCY)
    stopped = False
    completed = 0
    async with httpx.AsyncClient(
        timeout=old.TIMEOUT, headers={"Authorization": f"Bearer {key}"}
    ) as client:

        async def call(job: tuple[dict[str, Any], v2.v1.Condition, dict[str, Any], str]) -> None:
            nonlocal spent, stopped, completed
            row, condition, request, rid = job
            async with semaphore:
                reserve = old.upper_cost(request)
                if stopped:
                    return
                if spent + reserve > 10:
                    stopped = True
                    print("Budget stop: retained all first attempts.", flush=True)
                    return
                spent += reserve
                start = time.time()
                event = {
                    "request_id": rid,
                    "condition": condition,
                    "state": "started",
                    "charged_upper_usd": reserve,
                }
                old.append(
                    ROOT / "requests.jsonl",
                    {
                        "request_id": rid,
                        "source_row_index": row["source_row_index"],
                        "source_sha256": old.digest(str(row["clinic_date"]).encode()),
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
                if completed % 25 == 0:
                    print(
                        f"{completed}/{len(pending)} new calls finished; "
                        f"study cost including active reserves ${spent:.4f}",
                        flush=True,
                    )

        await asyncio.gather(*(call(j) for j in pending))
    analyze(selected, identity)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "run", "replay"])
    args = parser.parse_args()
    selected = rows()
    identity = plan(selected)
    ROOT.mkdir(parents=True, exist_ok=True)
    target = ROOT / "plan.json"
    if args.command == "prepare":
        if target.exists() and old.read_json(target) != identity:
            raise ValueError("Existing plan changed; do not overwrite")
        old.write_json(target, identity)
        print(
            f"Prepared {len(selected)} paired development rows; "
            f"prior charge ${identity['prior_v1_charge_upper_usd']:.4f}"
        )
        return
    if old.read_json(target) != identity:
        raise ValueError("Prepared identity changed")
    if args.command == "run":
        asyncio.run(run(selected, identity))
    else:
        analyze(selected, identity)


if __name__ == "__main__":
    main()
