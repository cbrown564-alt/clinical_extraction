"""Build aggregate-only six-model LLM-only test450 panel summary."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs/gan2026/six_model_llm_only_test450_20260801.json"
OUT_DIR = REPO_ROOT / "experiments/gan2026_six_model_llm_only_test450_20260801"


def _parse_aggregate(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if "## Rows" in text:
        raise ValueError(f"holdout aggregate must not contain row tables: {path}")
    purist = re.search(
        r"Purist holdout accuracy/micro F1 proxy: ([0-9.]+) \(([0-9]+) / ([0-9]+)\)",
        text,
    )
    pragmatic = re.search(
        r"Pragmatic holdout accuracy/micro F1 proxy: ([0-9.]+) \(([0-9]+) / ([0-9]+)\)",
        text,
    )
    calls = re.search(r"- Call failures: ([0-9]+)", text)
    parses = re.search(r"- Parse/schema/label issues: ([0-9]+)", text)
    if not purist or not pragmatic:
        raise ValueError(f"missing holdout scores in {path}")
    return {
        "purist_accuracy": float(purist.group(1)),
        "purist_correct": int(purist.group(2)),
        "rows": int(purist.group(3)),
        "pragmatic_accuracy": float(pragmatic.group(1)),
        "pragmatic_correct": int(pragmatic.group(2)),
        "call_failures": int(calls.group(1)) if calls else None,
        "parse_or_validation_failures": int(parses.group(1)) if parses else None,
        "aggregate_path": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
    }


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    panel_root = REPO_ROOT / config["artifact_root"]
    conditions: list[dict[str, object]] = []
    for item in config["conditions"]:
        slug = item["slug"]
        if slug == "deepseek_v4_flash" and item.get("artifact_root"):
            agg = REPO_ROOT / item["artifact_root"] / "aggregate.md"
            # Prefer panel hardlink/copy when present.
            panel_agg = panel_root / slug / "aggregate.md"
            if panel_agg.is_file():
                agg = panel_agg
        else:
            agg = panel_root / slug / "aggregate.md"
        if not agg.is_file():
            raise FileNotFoundError(f"missing aggregate for {slug}: {agg}")
        metrics = _parse_aggregate(agg)
        conditions.append(
            {
                "slug": slug,
                "model": item["model"],
                "execution_group": item["execution_group"],
                "transport": item["transport"],
                **metrics,
            }
        )
    if len(conditions) != 6:
        raise ValueError(f"expected 6 conditions, got {len(conditions)}")
    if any(int(c["rows"]) != 450 for c in conditions):
        raise ValueError("every condition must cover 450 rows")

    ranked = sorted(
        conditions,
        key=lambda c: (-int(c["purist_correct"]), str(c["slug"])),
    )
    for rank, item in enumerate(ranked, start=1):
        item["purist_rank"] = rank

    payload = {
        "schema_version": "gan2026.six_model_llm_only_test450_panel.v1",
        "protocol": config["protocol"],
        "config": str(CONFIG_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "split": "test450",
        "row_count": 450,
        "row_policy": "aggregate_only",
        "method": config["method"],
        "conditions": conditions,
        "claim_boundary": config["claim_boundary"],
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "panel_aggregate.json"
    md_path = OUT_DIR / "panel_aggregate.md"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Gan 2026 six-model LLM-only test450 panel",
        "",
        "Date: 2026-08-01",
        "",
        "Aggregate-only matched LLM-only (`gan2026_llm_only_canonical_pipeline_v0.8`) "
        "panel on locked `test450`. Does not replace the frozen hybrid v0.5 "
        "LLM-with-rules panel. Hosted versus local routes are disclosed. No row "
        "inspection.",
        "",
        "| Rank | Model | Purist | Pragmatic | Call failures | Parse/schema | Route |",
        "| ---: | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in ranked:
        lines.append(
            f"| {item['purist_rank']} | `{item['model']}` | "
            f"{item['purist_correct']}/{item['rows']} ({item['purist_accuracy']:.4f}) | "
            f"{item['pragmatic_correct']}/{item['rows']} ({item['pragmatic_accuracy']:.4f}) | "
            f"{item['call_failures']} | {item['parse_or_validation_failures']} | "
            f"{item['execution_group']} |"
        )
    lines.extend(
        [
            "",
            f"Protocol: `{config['protocol']}`",
            f"Machine artifact: `{json_path.relative_to(REPO_ROOT).as_posix()}`",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"json": str(json_path), "markdown": str(md_path)}, indent=2))


if __name__ == "__main__":
    main()
