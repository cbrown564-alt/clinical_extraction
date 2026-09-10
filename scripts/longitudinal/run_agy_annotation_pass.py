"""Capture fresh agy annotations; never repair or tune against reference answers."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from threading import Event

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "results/longitudinal/pilot_v0.3/independent_pass"
OUTPUT = ROOT / "results/longitudinal/pilot_v0.3/agy_pass_medium"
PREFIX = (
    "Use only the supplied task. Do not call tools, read other files, load skills, "
    "or use prior conversations. Return only the requested JSON object.\n\n"
)
MODEL = "gemini-3.8-flash-medium"


def decode_trace(events: list[dict]) -> tuple[dict, dict]:
    for event in events:
        if event.get("event") == "step_update":
            kind = event["step_update"].get("step_type")
            if kind not in {"user_input", "agent_response", "error_message"}:
                raise ValueError(f"Unexpected tool or other step: {kind}")
    final = next((e["result"] for e in reversed(events) if e.get("event") == "result"), None)
    if final is None or final.get("status") != "SUCCESS":
        raise ValueError(
            "No successful result: "
            + json.dumps({k: v for k, v in (final or {}).items() if k != "response"})
        )
    response = final["response"].strip()
    if response.startswith("```json\n") and response.endswith("```"):
        response = response[8:-3].strip()
    elif response.startswith("```\n") and response.endswith("```"):
        response = response[4:-3].strip()
    payload = json.loads(response)
    if not isinstance(payload, dict):
        raise ValueError("Response is not an object")
    return payload, {k: v for k, v in final.items() if k != "response"}


def read_events(path: Path) -> list[dict]:
    events = []
    for line in path.read_text().splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            # A live writer may not yet have finished its last line. Finished
            # traces still require a successful result before use.
            continue
    return events


def inspect_attempt(out: Path) -> dict:
    metadata = json.loads((out / "attempt.json").read_text())
    events = read_events(out / "stdout.jsonl")
    try:
        if metadata["exit_code"] != 0:
            raise ValueError(f"CLI exit: {metadata['exit_code']}")
        payload, telemetry = decode_trace(events)
        (out / "parsed.json").write_text(json.dumps(payload, indent=2) + "\n")
        metadata.update(status="parsed", telemetry=telemetry, observed_tool_steps=0)
    except (ValueError, KeyError, TypeError) as error:
        metadata.update(status="failed", error=str(error))
    metadata["tool_catalog_present"] = bool(events and events[0].get("init", {}).get("tools"))
    metadata["isolation_limit"] = (
        "fresh temporary project; no observed tool steps required; "
        "tool catalog remains present and plan mode is ignored by CLI with slash expansion disabled"
    )
    (out / "attempt.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return metadata


def run_job(job: dict, stop: Event) -> dict:
    source = PACK / job["input"]
    relative = source.relative_to(PACK / "inputs").with_suffix("")
    out = OUTPUT / "attempts" / relative
    if (out / "attempt.json").exists():
        previous = inspect_attempt(out)
        if previous["input_sha256"] != job["sha256"]:
            stop.set()
            raise ValueError("Saved attempt does not match current input")
        if previous["status"] != "parsed":
            stop.set()
        return {"job": str(relative), **previous}
    if stop.is_set():
        return {"job": str(relative), "status": "not_started_after_failure"}
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != job["sha256"]:
        stop.set()
        raise ValueError(f"Input hash mismatch: {relative}")
    out.mkdir(parents=True, exist_ok=False)
    prompt = PREFIX + raw.decode()
    executable = shutil.which("agy")
    if executable is None:
        raise ValueError("agy is not available")
    started = datetime.now(UTC).isoformat()
    timer = time.monotonic()
    metadata = {
        "status": "running",
        "input_sha256": job["sha256"],
        "rendered_prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "model_requested": MODEL,
        "effort": "medium",
        "interface": "agy",
        "executable_sha256": hashlib.sha256(Path(executable).read_bytes()).hexdigest(),
        "fresh_project": True,
        "sandbox": True,
        "tools_requested": False,
        "started_at": started,
        "semantic_repair": False,
        "provider_cost": None,
        "human_annotation_minutes": None,
    }
    with tempfile.TemporaryDirectory(prefix="independent-pilot-agy-") as temporary:
        command = [
            executable,
            "--new-project",
            "--model",
            MODEL,
            "--effort",
            "medium",
            "--mode",
            "plan",
            "--sandbox",
            "--disable-slash-commands",
            "--output-format",
            "stream-json",
            "--print-timeout",
            "4m",
            "--print",
            prompt,
        ]
        with (out / "stdout.jsonl").open("w") as stdout, (out / "stderr.txt").open("w") as stderr:
            process = subprocess.Popen(
                command, cwd=temporary, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr
            )
            interrupted = None
            while process.poll() is None:
                events = read_events(out / "stdout.jsonl")
                unexpected = any(
                    e.get("event") == "step_update"
                    and e["step_update"].get("step_type")
                    not in {"user_input", "agent_response", "error_message"}
                    for e in events
                )
                if unexpected or time.monotonic() - timer > 260:
                    interrupted = "unexpected_tool_step" if unexpected else "timeout"
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    break
                time.sleep(0.5)
            metadata["exit_code"] = interrupted or process.returncode
    metadata.update(ended_at=datetime.now(UTC).isoformat(), wall_seconds=time.monotonic() - timer)
    (out / "attempt.json").write_text(json.dumps(metadata, indent=2) + "\n")
    result = inspect_attempt(out)
    if result["status"] != "parsed":
        stop.set()
    return {"job": str(relative), **result}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=3, choices=(1, 2, 3))
    args = parser.parse_args()
    jobs = json.loads((PACK / "manifest.json").read_text())["jobs"]
    stop = Event()
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_job, job, stop) for job in jobs]
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            (OUTPUT / "capture_summary.json").write_text(json.dumps(results, indent=2) + "\n")
            print(result["job"], result["status"], result.get("error", ""), flush=True)
