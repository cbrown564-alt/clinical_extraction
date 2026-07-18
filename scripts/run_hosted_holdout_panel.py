"""Run one frozen hosted holdout panel from the dated orchestration config."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--panel", choices=("exectv2", "gan2026"), required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    panel = config[args.panel]
    protocol = Path(panel["protocol"])
    if not protocol.is_file():
        raise SystemExit(f"missing frozen protocol: {protocol}")
    allowed_slugs = set(panel.get("model_slugs", []))
    models = [
        model
        for model in config["models"]
        if not allowed_slugs or model["slug"] in allowed_slugs
    ]
    for model in models:
        if args.panel == "exectv2":
            command = _prepare_exect_command(model, panel)
        else:
            command = _prepare_gan_command(model, panel)
        subprocess.run(command, check=True)


def _prepare_exect_command(model: dict[str, Any], panel: dict[str, Any]) -> list[str]:
    base_path = Path(model["exect_base_config"])
    payload = json.loads(base_path.read_text(encoding="utf-8"))
    slug = str(model["slug"])
    root = Path(panel["scratch_root"]) / slug
    root.mkdir(parents=True, exist_ok=True)
    payload["candidate_id"] = f"exectv2_decision_0041_{slug}_test60_v1"
    payload["architecture_core_id"] = "exectv2_decision_0041_single_call_test60_v1"
    payload["claim_boundary"] = "Frozen ExECTv2 test60 aggregate-only holdout evidence."
    payload["run_command"] = "generated from frozen hosted holdout configuration"
    assembly = payload["assembly"]
    assembly["candidate_id"] = payload["candidate_id"]
    assembly["pipeline_family"] = "exectv2_decision_0041_single_call_test60"
    assembly["split"] = "test60"
    assembly["row_count"] = int(panel["row_count"])
    assembly["claim_boundary"] = payload["claim_boundary"]
    assembly["promotion_decision"] = "frozen-test60-aggregate-readout"
    for producer_id, producer in assembly["producers"].items():
        suffix = (
            "structured.jsonl"
            if producer_id == "structured_key_family_event_ledger"
            else "sf_unknown_suppression.jsonl"
        )
        producer["artifact"] = (root / f"{slug}_{suffix}").as_posix()
    payload["outputs"] = {
        "json": (root / f"{slug}_aggregate.json").as_posix(),
        "jsonl": (root / f"{slug}_sealed_rows.jsonl").as_posix(),
        "markdown": (root / f"{slug}_aggregate.md").as_posix(),
    }
    runtime_config = root / f"{slug}_test60_config.json"
    runtime_config.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return [
        sys.executable,
        str(panel["runner"]),
        "--config",
        str(runtime_config),
        "--allow-non-dev140",
        "--no-dspy-cache",
        "--progress-every",
        "1",
        "--allow-row-failures",
    ]


def _prepare_gan_command(model: dict[str, Any], panel: dict[str, Any]) -> list[str]:
    slug = str(model["slug"])
    root = Path(panel["scratch_root"]) / slug
    root.mkdir(parents=True, exist_ok=True)
    return [
        sys.executable,
        str(panel["runner"]),
        "--pipeline",
        str(panel["pipeline"]),
        "--prompt-version",
        str(panel["prompt_version"]),
        "--split",
        str(panel["split"]),
        "--frozen-test-protocol",
        str(panel["protocol"]),
        "--model",
        str(model["model"]),
        "--temperature",
        str(model.get("gan_temperature", 0)),
        "--max-tokens",
        str(model.get("gan_max_tokens", panel["max_tokens"])),
        "--disable-dspy-cache",
        "--progress-every",
        "1",
        "--resume-existing",
        "--jsonl",
        str(root / f"{slug}_sealed_rows.jsonl"),
        "--markdown",
        str(root / f"{slug}_aggregate.md"),
    ]


if __name__ == "__main__":
    main()
