"""Check returned seizure-frequency annotations against their source batch.

Standalone: copied into annotation packages. Needs Python 3.10+ and ``jsonschema``.

    python validate_annotations.py ANNOTATIONS.jsonl SOURCES.jsonl [SOURCES.jsonl ...]

Checks one record per source letter, matching identity, the finding schema and
that every evidence quotation is an exact substring of its letter. It never
changes an annotation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

SCHEMA = Path(__file__).with_name("annotation.schema.json")
IDENTITY = ("source_row_index", "source_id", "source_sha256")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise SystemExit(f"{path}:{number}: invalid JSON: {error}") from error
    return rows


def validate(annotations: list[dict[str, Any]], sources: list[dict[str, Any]]) -> list[str]:
    try:
        from jsonschema import Draft202012Validator
    except ImportError as error:
        raise SystemExit("Install jsonschema first: python -m pip install jsonschema") from error
    validator = Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    by_index = {s["source_row_index"]: s for s in sources}
    errors: list[str] = []
    seen: set[int] = set()
    for record in annotations:
        index = record.get("source_row_index")
        label = f"letter {index}"
        for problem in validator.iter_errors(record):
            path = "/".join(str(p) for p in problem.absolute_path) or "record"
            errors.append(f"{label}: {path}: {problem.message}")
        if index not in by_index:
            errors.append(f"{label}: not in the supplied source batches")
            continue
        if index in seen:
            errors.append(f"{label}: annotated more than once")
        seen.add(index)
        source = by_index[index]
        for key in IDENTITY:
            if record.get(key) != source[key]:
                errors.append(f"{label}: {key} does not match the source")
        for number, finding in enumerate(record.get("findings") or []):
            for quote in finding.get("evidence") or [] if isinstance(finding, dict) else []:
                if isinstance(quote, str) and quote not in source["note"]:
                    errors.append(f"{label}: finding {number}: quotation not found: {quote!r}")
    for index in sorted(set(by_index) - seen):
        errors.append(f"letter {index}: missing annotation")
    return errors


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    annotations = read_jsonl(Path(sys.argv[1]))
    sources = [row for path in sys.argv[2:] for row in read_jsonl(Path(path))]
    errors = validate(annotations, sources)
    findings = sum(len(r.get("findings") or []) for r in annotations)
    print(f"{len(annotations)} records, {findings} findings, {len(sources)} source letters")
    for error in errors:
        print(error)
    print("OK" if not errors else f"{len(errors)} problems")
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
