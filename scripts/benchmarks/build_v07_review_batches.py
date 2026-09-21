"""Build and assemble guide v0.7 review batches for isolated independent rereads.

``build`` splits a migrated candidate into fixed-size batch folders, each with the
matching source subset. ``assemble`` merges the reviewers' ``reviewed.jsonl`` files
into one snapshot plus a separate review log, and reports coverage. Local files only.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def build(candidate: Path, sources: Path, out: Path, size: int) -> None:
    records = read_jsonl(candidate)
    texts = {str(s["source_id"]): s for s in read_jsonl(sources)}
    records.sort(key=lambda r: r["source_row_index"])
    manifest = []
    for index in range(0, len(records), size):
        chunk = records[index : index + size]
        number = index // size + 1
        folder = out / f"batch_{number:03d}"
        write_jsonl(folder / "candidate.jsonl", chunk)
        write_jsonl(folder / "sources.jsonl", [texts[str(r["source_id"])] for r in chunk])
        manifest.append(
            {
                "batch": folder.name,
                "size": len(chunk),
                "source_ids": [str(r["source_id"]) for r in chunk],
            }
        )
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"{len(manifest)} batches of up to {size} letters under {out}")


def assemble(out: Path, snapshot: Path, log: Path) -> None:
    manifest = json.loads((out / "manifest.json").read_text())
    rows: list[dict[str, Any]] = []
    reviews: list[dict[str, Any]] = []
    missing: list[str] = []
    verdicts: Counter[str] = Counter()
    for entry in manifest:
        path = out / entry["batch"] / "reviewed.jsonl"
        if not path.exists():
            missing.append(entry["batch"])
            continue
        reviewed = read_jsonl(path)
        ids = [str(r["source_id"]) for r in reviewed]
        if sorted(ids) != sorted(entry["source_ids"]):
            missing.append(entry["batch"] + " (coverage mismatch)")
            continue
        for row in reviewed:
            review = row.pop("review", None) or {"verdict": "unknown", "changes": []}
            verdicts[review["verdict"]] += 1
            reviews.append({"source_id": str(row["source_id"]), "batch": entry["batch"], **review})
            rows.append(row)
    rows.sort(key=lambda r: r["source_row_index"])
    summary = {
        "batches": len(manifest),
        "reviewed_batches": len(manifest) - len(missing),
        "missing": missing,
        "records": len(rows),
        "verdicts": dict(verdicts),
        "semantic_changes_during_assembly": 0,
    }
    print(json.dumps(summary, indent=2))
    if missing:
        sys.exit(1)
    write_jsonl(snapshot, rows)
    write_jsonl(log, reviews)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build")
    b.add_argument("--candidate", type=Path, required=True)
    b.add_argument("--sources", type=Path, required=True)
    b.add_argument("--out", type=Path, required=True)
    b.add_argument("--size", type=int, default=10)
    a = sub.add_parser("assemble")
    a.add_argument("--out", type=Path, required=True)
    a.add_argument("--snapshot", type=Path, required=True)
    a.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "build":
        build(args.candidate, args.sources, args.out, args.size)
    else:
        assemble(args.out, args.snapshot, args.log)


if __name__ == "__main__":
    main()
