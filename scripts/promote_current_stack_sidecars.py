#!/usr/bin/env python3
"""Copy selected holdout replay inputs out of scratch/ as stripped replay JSONL.

Keeps only the fields current-stack rerun needs. Drops note text, gold,
prompt payloads, and sealed rows. Scratch trees stay as the operational dump.

See docs/runbooks/current_stack_six_model_replay.md.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCES = REPO_ROOT / "paper_experiments/current_stack/SOURCES.json"
OUT = REPO_ROOT / "experiments/current_stack/sidecars"


def _gan_sidecar(row: dict[str, Any]) -> dict[str, Any]:
    comparison = row.get("comparison")
    slim_comparison = None
    if comparison is not None:
        slim_comparison = {
            "purist_correct": bool(comparison.get("purist_correct")),
            "pragmatic_correct": bool(comparison.get("pragmatic_correct")),
        }
    return {
        "source_row_index": row["source_row_index"],
        "prompt_version": row.get("prompt_version"),
        "raw_output": row.get("raw_output") or "",
        "comparison": slim_comparison,
    }


def _exect_sidecar(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "letter_id": row["letter_id"],
        "prompt_version": row.get("prompt_version"),
        "structured_events": row.get("structured_events") or [],
    }


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def main() -> None:
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))
    mapping: dict[str, str] = {}
    for cell_id, cell in sources["cells"].items():
        kind = "gan" if cell.get("task") == "gan2026" else "exect"
        for slug, spec in (cell.get("sources") or {}).items():
            src_rel = spec.get("path") or spec.get("structured")
            if not src_rel or not str(src_rel).startswith("scratch/"):
                continue
            src = REPO_ROOT / src_rel
            if not src.is_file():
                raise FileNotFoundError(src)
            rows = [
                json.loads(line)
                for line in src.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            kept = [_gan_sidecar(row) if kind == "gan" else _exect_sidecar(row) for row in rows]
            dest_rel = f"experiments/current_stack/sidecars/{cell_id}/{slug}.jsonl"
            dest = REPO_ROOT / dest_rel
            _write_jsonl(dest, kept)
            mapping[src_rel] = dest_rel
            print(f"{src_rel} -> {dest_rel} ({len(kept)} rows, {dest.stat().st_size} bytes)")

    (OUT / "promotion_map.json").write_text(
        json.dumps(mapping, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"wrote { (OUT / 'promotion_map.json').relative_to(REPO_ROOT) }")


if __name__ == "__main__":
    main()
