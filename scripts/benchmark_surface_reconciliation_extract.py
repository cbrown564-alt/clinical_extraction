"""Aggregate-only extract: headline vs clinical-recovery via benchmark_format category."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
DEFS = (
    REPO
    / "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/reports"
    / "component_ablation/definitions.yaml"
)


def load_benchmark_format_ids() -> tuple[str, ...]:
    catalog = yaml.safe_load(DEFS.read_text(encoding="utf-8"))
    return tuple(
        c["component_id"]
        for c in catalog["component_off"]
        if c["component_portability_category"] == "benchmark_format"
    )


def extract_table(replay_json: Path) -> dict[str, dict[str, float]]:
    data = json.loads(replay_json.read_text(encoding="utf-8"))
    by_run: dict[str, dict[str, float]] = defaultdict(dict)
    for ab in data["ablations"]:
        if ab["component_portability_category"] != "benchmark_format":
            continue
        rid = ab["baseline_run_id"]
        cid = ab["component_id"]
        if cid == "headline_projection":
            by_run[rid]["headline_f1"] = float(ab["baseline_aggregate_score"]["overall"]["f1"])
        if cid == "residual_semantic_lens":
            by_run[rid]["clinical_recovery_f1"] = float(
                ab["component_off_aggregate_score"]["overall"]["f1"]
            )
            by_run[rid]["clinical_recovery_surface"] = ab["component_off_surface"]
    return dict(by_run)


def main() -> None:
    bf_ids = load_benchmark_format_ids()
    print("benchmark_format component_ids from definitions.yaml:", bf_ids)
    print()

    for label, path in (
        ("dev140", REPO / "experiments/exectv2_component_off_replay_dev140_20260626.json"),
        ("full200", REPO / "experiments/exectv2_component_off_replay_full200_20260626.json"),
    ):
        table = extract_table(path)
        print(f"=== {label} (benchmark_format category only) ===")
        for rid, scores in sorted(table.items()):
            h = scores["headline_f1"]
            c = scores["clinical_recovery_f1"]
            print(
                f"{rid}: headline={h:.4f} clinical_recovery={c:.4f} "
                f"delta={h - c:.4f} surface={scores['clinical_recovery_surface']}"
            )
        print()


if __name__ == "__main__":
    main()
