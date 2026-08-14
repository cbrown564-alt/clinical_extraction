#!/usr/bin/env python3
"""One entry point for current-stack six-model hybrid replay.

See docs/runbooks/current_stack_six_model_replay.md.
Stages: check, measure, assemble, exhibits, snapshot, promote-checklist, all.
Zero model calls.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
STACK = REPO_ROOT / "experiments/current_stack"
SOURCES = STACK / "SOURCES.json"
LATEST = STACK / "latest"
RUNS = STACK / "runs"


def _load_sources() -> dict[str, Any]:
    return json.loads(SOURCES.read_text(encoding="utf-8"))


def _python() -> str:
    return sys.executable


def _run(script: str, extra: list[str]) -> None:
    command = [_python(), str(REPO_ROOT / script), *extra]
    print(">", " ".join(command), flush=True)
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def stage_check() -> int:
    sources = _load_sources()
    missing: list[str] = []
    selected: list[str] = []
    for cell_id, cell in sources["cells"].items():
        cell_sources = cell.get("sources") or {}
        for slug, spec in cell_sources.items():
            for key in ("path", "structured", "assembly"):
                rel = spec.get(key)
                if not rel:
                    continue
                path = REPO_ROOT / rel
                label = f"{cell_id}.{slug}.{key}={rel}"
                if spec.get("selected"):
                    selected.append(label)
                if not path.is_file():
                    missing.append(label)
    if missing:
        print("missing selected or inventoried source files:")
        for item in missing:
            print(f"  {item}")
        return 2
    print(f"SOURCES ok: {len(selected)} selected paths present")
    for item in selected:
        print(f"  selected {item}")
    return 0


def stage_measure(*, overwrite: bool) -> int:
    extra = [
        "--cell",
        "all",
        "--out-dir",
        str(LATEST),
        "--scratch-dir",
        str(REPO_ROOT / "scratch/validation/current_stack/latest"),
    ]
    if overwrite:
        extra.append("--overwrite")
    _run("scripts/replay_six_model_current_stack_remaining_cells.py", extra)
    return 0


def _gan_rate(cell: dict[str, Any]) -> dict[str, Any]:
    after = cell["after"]
    n = int(after["rows"])
    return {
        "purist": after["purist"],
        "pragmatic": after["pragmatic"],
        "n": n,
        "purist_rate": round(after["purist"] / n, 4),
        "pragmatic_rate": round(after["pragmatic"] / n, 4),
        "source": cell.get("source_artifact"),
    }


def _exect_rate(cell: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "f1": cell["after_four_family_f1"],
        "by_family": {
            family: float(score["f1"])
            for family, score in cell["after_by_family"].items()
        },
        "source": cell.get("source_artifact"),
    }
    for key in ("call_mode", "thinking", "provider_revision"):
        if cell.get(key):
            payload[key] = cell[key]
    return payload


def _attach_source_meta(
    cell: dict[str, Any], spec: dict[str, Any] | None
) -> dict[str, Any]:
    if not spec:
        return cell
    for key in ("selected", "role", "call_mode", "thinking", "provider_revision"):
        if key in spec and spec[key] not in (None, ""):
            cell[key] = spec[key]
    return cell


def extract_fills(replay: dict[str, Any]) -> dict[str, Any]:
    gan = replay["gan2026_test450"]["models"]
    ex_dev = replay["exectv2_dev140"]["models"]
    ex_test = replay["exectv2_test60"]["models"]
    deepseek = replay["deepseek_v4_flash_0731"]
    gan_selected = {
        slug: _gan_rate(cell)
        for slug, cell in gan.items()
        if slug != "deepseek_v4_flash"
    }
    gan_selected["deepseek_v4_flash"] = _gan_rate(deepseek["gan2026_test450"])
    gan_selected["deepseek_v4_flash"]["provider_revision"] = "DeepSeek-V4-Flash-0731"
    test60 = {
        slug: _exect_rate(cell)
        for slug, cell in ex_test.items()
        if slug != "deepseek_v4_flash"
    }
    test60["deepseek_v4_flash"] = _exect_rate(deepseek["exectv2_test60"])
    test60["deepseek_v4_flash"]["provider_revision"] = "DeepSeek-V4-Flash-0731"
    previous_fills_path = LATEST / "fills.json"
    if previous_fills_path.is_file():
        previous = json.loads(previous_fills_path.read_text(encoding="utf-8"))
        previous_gan = ((previous.get("hybrid") or {}).get("gan_test450") or {})
        if "gemini37flash" in previous_gan and "gemini37flash" not in gan_selected:
            gan_selected["gemini37flash"] = previous_gan["gemini37flash"]
    sol_gan = gan_selected["gpt56sol"]["purist_rate"]
    sol_exect = test60["gpt56sol"]["f1"]
    sources = _load_sources()
    gan_specs = sources["cells"]["gan_test450"]["sources"]
    dev_specs = sources["cells"]["exect_dev140"]["sources"]
    test_specs = sources["cells"]["exect_test60"]["sources"]
    for slug, cell in gan_selected.items():
        spec = gan_specs.get(f"{slug}_0731") or gan_specs.get(slug)
        _attach_source_meta(cell, spec)
    ex_dev_fills = {
        slug: _attach_source_meta(_exect_rate(cell), dev_specs.get(slug))
        for slug, cell in ex_dev.items()
    }
    for slug, cell in test60.items():
        spec = test_specs.get(f"{slug}_0731") or test_specs.get(slug)
        _attach_source_meta(cell, spec)
    return {
        "schema_version": "current_stack.fills.v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "decision": "docs/decisions/0050-current-stack-hybrid-primary-fills.md",
        "six_model_slot_amendment": "docs/decisions/0052-gemini-37-flash-holdout-six-model-slot.md",
        "method_identity_model": "gpt56sol",
        "hybrid": {
            "gan_test450": gan_selected,
            "exect_dev140": ex_dev_fills,
            "exect_test60": test60,
        },
        "glance_2dp": {
            "gan_sol_llm_with_rules": round(sol_gan, 2),
            "exect_sol_llm_with_rules": round(sol_exect, 2),
            "gan_sol_purist": gan_selected["gpt56sol"]["purist"],
            "gan_sol_n": 450,
        },
        "pre0731_not_selected": {
            "gan_test450_deepseek": _gan_rate(gan["deepseek_v4_flash"]),
            "exect_test60_deepseek": _exect_rate(ex_test["deepseek_v4_flash"]),
        },
    }


def _write_checklist(fills: dict[str, Any], sources: dict[str, Any], path: Path) -> None:
    glance = fills["glance_2dp"]
    gan = fills["hybrid"]["gan_test450"]
    ex_test = fills["hybrid"]["exect_test60"]
    ex_dev = fills["hybrid"]["exect_dev140"]
    lines = [
        "# Current-stack promote checklist",
        "",
        "Machine assemble wrote these numbers. Claim owners are not edited",
        "until you do this step on purpose.",
        "",
        "## Sol method-identity fills",
        "",
        f"- Gan test450 Purist: **{glance['gan_sol_purist']}/450** "
        f"({gan['gpt56sol']['purist_rate']}, glance {glance['gan_sol_llm_with_rules']})",
        f"- ExECT test60 F1: **{ex_test['gpt56sol']['f1']}** "
        f"(glance {glance['exect_sol_llm_with_rules']})",
        f"- ExECT dev140 F1: **{ex_dev['gpt56sol']['f1']}**",
        "",
        "## Selected six-model hybrid holdout",
        "",
        "| Model | ExECT test60 | Gan test450 Purist |",
        "| --- | ---: | ---: |",
    ]
    order = [
        "gemini37flash",
        "gpt56sol",
        "deepseek_v4_flash",
        "gpt56luna",
        "qwen36_35b",
        "gemma4_26b",
        "gpt41mini",
    ]
    labels = {row["slug"]: row["label"] for row in sources["models"]}
    for slug in order:
        gan_cell = gan[slug]
        lines.append(
            f"| {labels[slug]} | {ex_test[slug]['f1']} | "
            f"{gan_cell['purist']}/{gan_cell['n']} ({gan_cell['purist_rate']}) |"
        )
    lines.extend(
        [
            "",
            "## Living claim owners to update (or leave unchanged)",
            "",
        ]
    )
    for owner in sources["promote_owners"]:
        lines.append(f"- `{owner}`")
    lines.extend(
        [
            "",
            "Do not edit rules-only or LLM-only fills.",
            "Do not rewrite retained-evidence live-run `result_summary`.",
            "Sol stays the Decision 0046 method-identity row.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def stage_assemble() -> int:
    replay_path = LATEST / "replay_summary.json"
    if not replay_path.is_file():
        print(f"missing {replay_path.relative_to(REPO_ROOT)}; run measure first")
        return 2
    replay = json.loads(replay_path.read_text(encoding="utf-8"))
    if "deepseek_v4_flash_0731" not in replay:
        print("replay_summary has no deepseek_v4_flash_0731 cell; run measure --cell all")
        return 2
    LATEST.mkdir(parents=True, exist_ok=True)
    fills = extract_fills(replay)
    (LATEST / "fills.json").write_text(
        json.dumps(fills, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    _write_checklist(fills, _load_sources(), LATEST / "promote_checklist.md")
    _run(
        "scripts/build_six_model_current_stack_primary_panel.py",
        [
            "--replay",
            str(replay_path),
            "--out",
            str(LATEST / "panel_aggregate.json"),
        ],
    )
    print(f"wrote { (LATEST / 'fills.json').relative_to(REPO_ROOT) }")
    print(f"wrote { (LATEST / 'promote_checklist.md').relative_to(REPO_ROOT) }")
    return 0


def stage_exhibits() -> int:
    panel = LATEST / "panel_aggregate.json"
    if not panel.is_file():
        print("missing latest panel; run assemble first")
        return 2
    _run(
        "scripts/render_six_model_comparison_charts.py",
        ["--panel", str(panel)],
    )
    return 0


def stage_snapshot() -> int:
    if not (LATEST / "fills.json").is_file():
        print("missing latest/fills.json; run assemble first")
        return 2
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    dest = RUNS / stamp
    dest.mkdir(parents=True, exist_ok=True)
    for name in (
        "replay_summary.json",
        "panel_aggregate.json",
        "fills.json",
        "promote_checklist.md",
    ):
        src = LATEST / name
        if src.is_file():
            shutil.copy2(src, dest / name)
    print(f"snapshotted {dest.relative_to(REPO_ROOT)}")
    return 0


def stage_checklist() -> int:
    path = LATEST / "promote_checklist.md"
    if not path.is_file():
        print("missing promote checklist; run assemble first")
        return 2
    print(path.read_text(encoding="utf-8"))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "stage",
        choices=(
            "check",
            "measure",
            "assemble",
            "exhibits",
            "snapshot",
            "promote-checklist",
            "all",
        ),
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.stage == "check":
        return stage_check()
    if args.stage == "measure":
        return stage_measure(overwrite=args.overwrite)
    if args.stage == "assemble":
        return stage_assemble()
    if args.stage == "exhibits":
        return stage_exhibits()
    if args.stage == "snapshot":
        return stage_snapshot()
    if args.stage == "promote-checklist":
        return stage_checklist()
    status = stage_check()
    if status:
        return status
    status = stage_measure(overwrite=args.overwrite)
    if status:
        return status
    status = stage_assemble()
    if status:
        return status
    status = stage_exhibits()
    if status:
        return status
    status = stage_snapshot()
    if status:
        return status
    return stage_checklist()


if __name__ == "__main__":
    raise SystemExit(main())
