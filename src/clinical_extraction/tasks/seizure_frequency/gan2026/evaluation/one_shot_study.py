"""Bounded synthetic paper experiment. Real-data execution is deliberately unavailable.

python -m clinical_extraction.tasks.seizure_frequency.gan2026.evaluation.one_shot_study
    render|dev|freeze|evaluate|replay
"""

from __future__ import annotations

import argparse
import asyncio
import difflib
import hashlib
import json
import os
import time
from collections import Counter
from pathlib import Path
from typing import Any, cast

import httpx

from clinical_extraction.core.evidence import clean_semantically_neutral_text_artifacts
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_DATA_PATH,
    DEFAULT_SPLIT_MANIFEST_PATH,
    SEIZURE_FREQUENCY_KEY,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import one_shot_analysis
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_contract as contract
from clinical_extraction.tasks.shared.epilepsy.normalization import label_to_frequency_record

ROOT = Path("runs/one_shot_frequency_v1")
BUDGET = 10.0
DEV_LIMIT = 1.0
MODEL = "deepseek-flash"
API = "https://api.deepseek.com"
MAX_TOKENS = 4096
TIMEOUT = 180
CONCURRENCY = 6
INPUT_PEAK = 0.30 / 1_000_000
OUTPUT_PEAK = 1.20 / 1_000_000
SEED = "20260913"


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def encoded(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


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


def request_body(note: str, condition: contract.Condition) -> dict[str, Any]:
    return {
        "model": MODEL,
        "messages": contract.messages(note, condition),
        "max_tokens": MAX_TOKENS,
        "temperature": 0,
        "thinking": {"type": "disabled"},
        "response_format": {"type": "json_object"},
    }


def upper_cost(body: dict[str, Any]) -> float:
    # UTF-8 bytes bound text token count; extra allowance covers role/framing tokens.
    input_bound = len(encoded(body["messages"])) + 1024
    return input_bound * INPUT_PEAK + MAX_TOKENS * OUTPUT_PEAK


def charged(attempts: list[dict[str, Any]]) -> float:
    amounts: dict[str, float] = {}
    for event in attempts:
        amounts[event["request_id"]] = event["charged_upper_usd"]
    return sum(amounts.values())


def identity() -> dict[str, Any]:
    base = Path("src/clinical_extraction")
    paths = [
        Path(__file__),
        Path(contract.__file__),
        Path(contract.historical.__file__),
        Path(one_shot_analysis.__file__),
        base / "tasks/shared/epilepsy/normalization.py",
        base / "tasks/seizure_frequency/gan2026/labels.py",
        base / "core/evidence.py",
    ]
    return {
        "contract_version": contract.VERSION,
        "model": MODEL,
        "provider_documented_version": "DeepSeek-V4.1-Flash",
        "provider_revision_limit": "mutable API alias; response model retained for every call",
        "base_url": API,
        "max_tokens": MAX_TOKENS,
        "thinking": "disabled",
        "temperature": 0,
        "timeout_seconds": TIMEOUT,
        "concurrency": CONCURRENCY,
        "retry_policy": "none",
        "repair_policy": "none; strict first attempt",
        "json_policy": "json_object; schema in prompt",
        "budget_usd": BUDGET,
        "development_limit_usd": DEV_LIMIT,
        "pricing_checked": "2026-09-13",
        "pricing_url": "https://api-docs.deepseek.com/quick_start/pricing/",
        "cost_accounting": "peak cache-miss input plus peak output; unknown usage fully reserved",
        "input_peak_per_million": 0.30,
        "output_peak_per_million": 1.20,
        "components": {
            str(p.relative_to(Path.cwd()) if p.is_absolute() else p): digest(p.read_bytes())
            for p in paths
        },
        "dataset_sha256": digest(DEFAULT_DATA_PATH.read_bytes()),
        "split_manifest_sha256": digest(DEFAULT_SPLIT_MANIFEST_PATH.read_bytes()),
        "rendered_empty_requests": {
            c: digest(encoded(request_body("", c))) for c in contract.CONDITIONS
        },
        "row_policy": "all split rows including row_ok=False; no prediction-based exclusions",
        "development_selection": "20 dev750 IDs sorted by sha256(20260913:ID)",
        "selection_rule": "one model/runtime; freeze unchanged after technical development checks",
        "analysis": {
            "version": one_shot_analysis.ANALYSIS_VERSION,
            "absolute": "Wilson 95%",
            "paired": "paired letter percentile bootstrap",
            "replicates": 10000,
            "seed": 20260913,
            "linkage": "patient/source-family identifiers not supplied in dataset",
            "small_strata": "no inferential subgroup analyses",
            "claim": "descriptive; no adequacy, equivalence or non-inferiority",
        },
        "prior_exposure": "dev750 and test450 used in earlier prompt/model studies; "
        "new test450 result is a reused-holdout comparison, not fresh holdout",
    }


def selected_rows(phase: str) -> list[dict[str, Any]]:
    manifest = read_json(DEFAULT_SPLIT_MANIFEST_PATH)
    if digest(DEFAULT_DATA_PATH.read_bytes()) != manifest["dataset_sha256"]:
        raise ValueError("Dataset hash differs from split manifest")
    if phase not in {"dev", "evaluate"}:
        raise ValueError("Only authorised synthetic partitions are supported")
    if phase == "evaluate":
        frozen = read_json(ROOT / "freeze.json")
        if frozen["identity"] != identity():
            raise ValueError("Frozen experiment identity changed")
    ids = manifest["splits"]["validation" if phase == "dev" else "test"]["source_row_indices"]
    if phase == "dev":
        ids = sorted(ids, key=lambda i: digest(f"{SEED}:{i}".encode()))[:20]
    allowed = set(ids)
    # Filter before cleaning, normalising, or reporting; never render excluded rows.
    by_id = {
        r["source_row_index"]: r
        for r in read_json(DEFAULT_DATA_PATH)
        if r["source_row_index"] in allowed
    }
    if set(by_id) != allowed or len(ids) != len(allowed):
        raise ValueError("Missing or duplicate split IDs")
    return [by_id[i] for i in ids]


def note_text(row: dict[str, Any]) -> str:
    return clean_semantically_neutral_text_artifacts(str(row["clinic_date"]))


def gold_categories(row: dict[str, Any]) -> dict[str, str]:
    label = row[SEIZURE_FREQUENCY_KEY]["seizure_frequency_number"]
    value = label_to_frequency_record(str(label[0] if isinstance(label, list) else label))
    return {
        "purist": str(map_purist(value.monthly_frequency)),
        "pragmatic": str(map_pragmatic(value.monthly_frequency)),
    }


def render() -> None:
    if (ROOT / "freeze.json").exists():
        raise ValueError("Do not change preparation after evaluation freeze")
    target = ROOT / "no_call"
    target.mkdir(parents=True, exist_ok=True)
    for condition in contract.CONDITIONS:
        write_json(
            target / f"{condition}.messages.json",
            contract.messages(contract.fictional_cases()[4]["note_text"], condition),
        )
        write_json(
            target / f"{condition}.schema.json", contract.MODELS[condition].model_json_schema()
        )
    rendered = {
        c: json.dumps(contract.messages("<NOTE_TEXT>", c), indent=2).splitlines(True)
        for c in contract.CONDITIONS
    }
    (target / "rich_simple.diff").write_text(
        "".join(
            difflib.unified_diff(
                rendered["simple"], rendered["rich"], fromfile="simple", tofile="rich"
            )
        )
    )
    checks = []
    for case in contract.fictional_cases():
        for condition in contract.CONDITIONS:
            output = case["output"] if condition == "rich" else {"answer": case["output"]["answer"]}
            result = contract.inspect_output(json.dumps(output), case["note_text"], condition)
            if result["failure"]:
                raise ValueError("Fictional fixture failed")
            checks.append({"case": case["name"], "condition": condition, "result": result})
    write_json(target / "fictional_fixtures.json", contract.fictional_cases())
    write_json(target / "checks.json", checks)
    write_json(ROOT / "development_plan.json", identity())
    print("No-call artifacts rendered; 12 fictional condition checks passed.")


async def run(phase: str) -> None:
    if read_json(ROOT / "development_plan.json") != identity():
        raise ValueError("Preparation identity changed; review and render before development")
    rows = selected_rows(phase)
    output = ROOT / phase
    output.mkdir(exist_ok=True)
    attempts_path = ROOT / "attempts.jsonl"
    attempts = read_lines(attempts_path)
    started = {a["request_id"] for a in attempts}
    tasks = []
    for row in rows:
        for condition in contract.CONDITIONS:
            body = request_body(note_text(row), condition)
            request_id = digest(
                encoded({"phase": phase, "id": row["source_row_index"], "body": body})
            )
            if request_id not in started:
                tasks.append((row, condition, body, request_id))
    maximum = sum(upper_cost(body) for _, _, body, _ in tasks)
    spent = charged(attempts)
    if spent + maximum > (DEV_LIMIT if phase == "dev" else BUDGET):
        raise ValueError(f"Preflight exceeds budget: spent {spent:.4f}, reserved {maximum:.4f}")
    print(
        json.dumps(
            {
                "phase": phase,
                "pending_calls": len(tasks),
                "peak_cost_upper_usd": maximum,
                "previous_charge_upper_usd": spent,
            }
        ),
        flush=True,
    )
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        # Do not print or persist credentials. dotenv is provided by the existing runtime.
        from dotenv import dotenv_values

        key = dotenv_values(".env").get("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError("DEEPSEEK_API_KEY is unavailable")
    semaphore = asyncio.Semaphore(CONCURRENCY)
    completed = 0
    async with httpx.AsyncClient(
        timeout=TIMEOUT, headers={"Authorization": f"Bearer {key}"}
    ) as client:

        async def call(row: dict[str, Any], condition: str, body: dict[str, Any], rid: str) -> None:
            nonlocal completed
            async with semaphore:
                reserve = upper_cost(body)
                started_at = time.time()
                event = {
                    "request_id": rid,
                    "phase": phase,
                    "condition": condition,
                    "started_at": started_at,
                    "charged_upper_usd": reserve,
                    "state": "started",
                }
                append(
                    output / "requests.jsonl",
                    {
                        "request_id": rid,
                        "body": body,
                        "source_row_index": row["source_row_index"],
                        "source_sha256": digest(str(row["clinic_date"]).encode()),
                        "text_view_sha256": digest(note_text(row).encode()),
                    },
                )
                append(attempts_path, event)
                raw_response: dict[str, Any] | None = None
                error = None
                status = None
                try:
                    response = await client.post(API + "/chat/completions", json=body)
                    status = response.status_code
                    if status == 200:
                        raw_response = response.json()
                    else:
                        error = f"http_{status}"
                except (httpx.HTTPError, ValueError) as exc:
                    error = type(exc).__name__  # No exception text containing notes or credentials.
                usage = (raw_response or {}).get("usage") or {}
                charge = reserve
                if "prompt_tokens" in usage and "completion_tokens" in usage:
                    charge = (
                        usage["prompt_tokens"] * INPUT_PEAK
                        + usage["completion_tokens"] * OUTPUT_PEAK
                    )
                append(
                    output / "responses.jsonl",
                    {
                        "request_id": rid,
                        "response": raw_response,
                        "error": error,
                        "http_status": status,
                    },
                )
                append(
                    attempts_path,
                    {
                        **event,
                        "state": "finished",
                        "charged_upper_usd": charge,
                        "elapsed_seconds": time.time() - started_at,
                        "usage": usage,
                        "error": error,
                    },
                )
                if phase == "evaluate":
                    content, _ = response_content(raw_response)
                    append(
                        output / "replay.jsonl",
                        {
                            "source_row_index": row["source_row_index"],
                            "prompt_version": contract.VERSION + ":" + condition,
                            "raw_output": content,
                        },
                    )
                completed += 1
                if completed % 10 == 0:
                    print(f"{phase}: {completed}/{len(tasks)} new calls finished", flush=True)

        await asyncio.gather(*(call(*task) for task in tasks))
    analyze(phase)


def response_content(response: dict[str, Any] | None) -> tuple[str | None, str | None]:
    choices = (response or {}).get("choices") or []
    if not choices:
        return None, None
    return choices[0].get("message", {}).get("content"), choices[0].get("finish_reason")


def analyze(phase: str) -> dict[str, Any]:
    rows = selected_rows(phase)
    output = ROOT / phase
    responses = {r["request_id"]: r for r in read_lines(output / "responses.jsonl")}
    paired = []
    response_models: Counter[str] = Counter()
    for row in rows:
        item: dict[str, Any] = {}
        for condition in contract.CONDITIONS:
            rid = digest(
                encoded(
                    {
                        "phase": phase,
                        "id": row["source_row_index"],
                        "body": request_body(note_text(row), condition),
                    }
                )
            )
            response = responses.get(rid, {}).get("response")
            content, finish = response_content(response)
            result = contract.inspect_output(
                content, note_text(row), condition, finish_reason=finish
            )
            if response:
                response_models[str(response.get("model"))] += 1
            gold = gold_categories(row)
            for method in ("purist", "pragmatic"):
                result[method + "_correct"] = result["failure"] is None and (
                    result["categories"][method] == gold[method]
                )
            item[condition] = result
        paired.append(item)
    report = one_shot_analysis.summarize(paired)
    events = read_lines(ROOT / "attempts.jsonl")
    finished = [e for e in events if e["phase"] == phase and e["state"] == "finished"]
    phase_events = [e for e in events if e["phase"] == phase]
    report.update(
        {
            "split": "dev750_fixed20" if phase == "dev" else "test450",
            "row_ok_false_included": sum(not row["row_ok"] for row in rows),
            "calls_started": sum(e["state"] == "started" for e in phase_events),
            "calls_finished": len(finished),
            "response_models": dict(response_models),
            "peak_charge_upper_usd": charged(phase_events),
            "total_study_charge_upper_usd": charged(events),
            "transport_failures": dict(Counter(e["error"] for e in finished if e["error"])),
            "execution_identity": identity(),
            "scope": "development" if phase == "dev" else "reused holdout; aggregate only",
        }
    )
    for condition in contract.CONDITIONS:
        condition_events = [e for e in finished if e["condition"] == condition]
        latencies = sorted(e["elapsed_seconds"] for e in condition_events)
        report["conditions"][condition]["execution"] = {
            "calls_finished": len(condition_events),
            "latency_median_seconds": latencies[len(latencies) // 2] if latencies else None,
            "prompt_tokens": sum(e["usage"].get("prompt_tokens", 0) for e in condition_events),
            "completion_tokens": sum(
                e["usage"].get("completion_tokens", 0) for e in condition_events
            ),
            "missing_usage": sum(not e["usage"] for e in condition_events),
        }
    write_json(output / "aggregate.json", report)
    if phase == "dev":
        write_json(output / "development_diagnostics.json", paired)
    print(
        json.dumps(
            {
                "split": report["split"],
                "calls_finished": len(finished),
                "charge_upper_usd": report["peak_charge_upper_usd"],
                "conditions": {
                    c: {
                        "purist": report["conditions"][c]["purist"],
                        "failures": report["conditions"][c]["failures"],
                    }
                    for c in contract.CONDITIONS
                },
            }
        ),
        flush=True,
    )
    return report


def freeze() -> None:
    if (ROOT / "freeze.json").exists():
        if read_json(ROOT / "freeze.json")["identity"] != identity():
            raise ValueError("Cannot overwrite a frozen experiment")
        print("Existing freeze unchanged")
        return
    development = read_json(ROOT / "dev/aggregate.json")
    if development["calls_finished"] != 40:
        raise ValueError("Complete the fixed development comparison first")
    if development["execution_identity"] != identity():
        raise ValueError("Development identity no longer matches")
    if any(development["conditions"][c]["failures"] for c in contract.CONDITIONS):
        raise ValueError("Review development technical failures before selecting condition")
    write_json(
        ROOT / "freeze.json",
        {
            "identity": identity(),
            "frozen_at": time.time(),
            "development_aggregate_sha256": digest((ROOT / "dev/aggregate.json").read_bytes()),
            "selected_frequency_condition": "rich",
            "patient_run_authorised": False,
            "selection_reason": "single prespecified API condition; first-pass checks passed; "
            "no selection from test results",
        },
    )
    print("Synthetic evaluation frozen; real-data permission remains pending.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["render", "dev", "freeze", "evaluate", "replay"])
    args = parser.parse_args()
    ROOT.mkdir(parents=True, exist_ok=True)
    lock = ROOT / "execution.lock"
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(descriptor)
    try:
        if args.phase == "render":
            render()
        elif args.phase == "freeze":
            freeze()
        elif args.phase == "replay":
            analyze("evaluate" if (ROOT / "freeze.json").exists() else "dev")
        else:
            asyncio.run(run(cast(str, args.phase)))
    finally:
        lock.unlink()


if __name__ == "__main__":
    main()
