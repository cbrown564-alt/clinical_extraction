"""Offline structural checker for guide v0.7 seizure-finding annotations.

Checks source identity and hashes, the R8 ``Annotation`` schema, coverage, duplicate
IDs, exact quotation occurrence and state consistency. It reads local files only and
exits nonzero on any error. It does not judge clinical support.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r8 as r8


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def check(
    sources: list[dict[str, Any]], annotations: list[dict[str, Any]], expected: int
) -> dict[str, Any]:
    by_id = {str(s["source_id"]): s for s in sources}
    errors: list[dict[str, Any]] = []
    seen: Counter[str] = Counter()
    states: Counter[str] = Counter()
    measurements: Counter[str] = Counter()
    findings = 0
    for row in annotations:
        sid = str(row.get("source_id"))
        seen[sid] += 1
        review = row.get("review")
        if review is not None and not (
            isinstance(review, dict)
            and review.get("verdict") in {"agree", "corrected"}
            and isinstance(review.get("changes"), list)
        ):
            errors.append(
                {
                    "source_id": sid,
                    "check": "review",
                    "detail": "review needs verdict agree|corrected and changes list",
                }
            )
        try:
            record = r8.Annotation.model_validate({k: v for k, v in row.items() if k != "review"})
        except ValidationError as exc:
            errors.append(
                {"source_id": sid, "check": "schema", "detail": str(exc).splitlines()[:6]}
            )
            continue
        source = by_id.get(sid)
        if source is None:
            errors.append({"source_id": sid, "check": "identity", "detail": "unknown source_id"})
            continue
        text = source["note_text"]
        if source["source_row_index"] != record.source_row_index:
            errors.append({"source_id": sid, "check": "identity", "detail": "row index mismatch"})
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != record.source_sha256:
            errors.append({"source_id": sid, "check": "identity", "detail": "source hash mismatch"})
        for finding in record.findings:
            findings += 1
            measurements[finding.measurement.type] += 1
            if finding.evidence not in text:
                errors.append(
                    {
                        "source_id": sid,
                        "check": "evidence",
                        "detail": f"{finding.id} quote not in source",
                    }
                )
            if r8.derive_scope(finding.event.type) != finding.event.scope:
                errors.append(
                    {
                        "source_id": sid,
                        "check": "scope",
                        "detail": (
                            f"{finding.id} scope {finding.event.scope} != derived "
                            f"{r8.derive_scope(finding.event.type)}"
                        ),
                    }
                )
        for date in record.document_dates:
            if date.evidence not in text:
                errors.append(
                    {
                        "source_id": sid,
                        "check": "evidence",
                        "detail": "document date quote not in source",
                    }
                )
        states[record.annotation_state] += 1
    duplicates = sorted(sid for sid, n in seen.items() if n > 1)
    missing = sorted(set(by_id) - set(seen))
    for sid in duplicates:
        errors.append({"source_id": sid, "check": "coverage", "detail": "duplicate record"})
    if len(seen) != expected or missing:
        errors.append(
            {
                "source_id": None,
                "check": "coverage",
                "detail": f"{len(seen)} records, expected {expected}; missing {len(missing)}",
            }
        )
    return {
        "records": len(annotations),
        "distinct_sources": len(seen),
        "expected": expected,
        "states": dict(states),
        "findings": findings,
        "measurements": dict(measurements),
        "errors": errors,
        "error_count": len(errors),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--expected", type=int, default=750)
    args = parser.parse_args()
    report = check(read_jsonl(args.sources), read_jsonl(args.annotations), args.expected)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(1 if report["error_count"] else 0)


if __name__ == "__main__":
    main()
