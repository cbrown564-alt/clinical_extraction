"""Run the declared 18-call, zero-incremental-charge annotation probe through agy."""

from __future__ import annotations

import json
from threading import Event

import run_agy_annotation_pass as capture


def main() -> None:
    pack = capture.ROOT / "results/longitudinal/pilot_v0.8/timed_pass"
    manifest_path = pack / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("incremental_charge_gbp") != 0 or not manifest.get("cost_basis"):
        raise ValueError("The declared zero-charge access must be confirmed")
    if len(manifest["jobs"]) != 18 or manifest["retry_budget"] != 0:
        raise ValueError("Probe must retain its declared call and retry limits")
    capture.PACK, capture.OUTPUT = pack, pack / "outputs"
    capture.MODEL = manifest["model"]
    capture.OUTPUT.mkdir(parents=True, exist_ok=True)
    stop, results = Event(), []
    manifest["status"] = "running"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    for job in manifest["jobs"]:
        result = capture.run_job(job, stop)
        result.update(activity=job["activity"], case=job["case"])
        results.append(result)
        (capture.OUTPUT / "capture_summary.json").write_text(json.dumps(results, indent=2) + "\n")
        print(job["id"], result["status"], result.get("wall_seconds"), flush=True)
    manifest["status"] = "failed" if stop.is_set() else "captured"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
