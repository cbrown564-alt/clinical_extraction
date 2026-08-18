#!/usr/bin/env python3
"""Generate (or check) the explanatory architecture documents.

The documents under ``docs/architecture/`` are derived from the stage
manifests and from teaching cases that execute the real pipelines. This script
is the only supported way to write them.

    python scripts/build_architecture_docs.py            # write
    python scripts/build_architecture_docs.py --check    # fail on drift

``--check`` is the drift gate: if the code moves and the manifests or teaching
cases produce different output, the committed explanation no longer matches the
pipeline and CI fails. No model calls are made and no locked rows are read.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from clinical_extraction.architecture.render import all_documents
from clinical_extraction.architecture.stage_manifest import (
    format_problems,
    repo_root,
    validate_all,
)
from clinical_extraction.architecture.teaching_case import build_teaching_letters

DOCS_DIR = Path("docs/architecture")


def build(root: Path) -> dict[Path, str]:
    cases = build_teaching_letters()
    return {
        root / DOCS_DIR / relative: content
        for relative, content in all_documents(cases).items()
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write; exit non-zero if any document is missing or stale.",
    )
    args = parser.parse_args(argv)
    root = repo_root()

    problems = validate_all(root=root)
    if problems:
        print(format_problems(problems), file=sys.stderr)
        return 1

    documents = build(root)

    if args.check:
        stale: list[str] = []
        for path, content in documents.items():
            relative = path.relative_to(root)
            if not path.is_file():
                stale.append(f"missing: {relative}")
            elif path.read_text(encoding="utf-8") != content:
                stale.append(f"stale: {relative}")
        if stale:
            print(
                f"{len(stale)} architecture document(s) out of date:",
                file=sys.stderr,
            )
            for entry in stale:
                print(f"  - {entry}", file=sys.stderr)
            print(
                "Run: python scripts/build_architecture_docs.py",
                file=sys.stderr,
            )
            return 1
        print(f"{len(documents)} architecture document(s) match the pipeline")
        return 0

    for path, content in documents.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"wrote {len(documents)} architecture document(s) under {DOCS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
