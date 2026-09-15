"""Offline structural/source checks; clinical review still requires A02–A09.

Run with Python 3.11+ and jsonschema 4.x; no network or model calls.
Writes JSON to stdout and exits nonzero on any error. Inputs are never edited.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def check(sources_path: Path, annotations_path: Path, schema_path: Path, expected: int) -> dict:
    errors: list[dict] = []

    def error(code: str, source_id: str | None, detail: str) -> None:
        errors.append({"check": code, "source_id": source_id, "detail": detail})

    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON number: {value}")

    def read(path: Path) -> list[dict]:
        rows = []
        for line_number, line in enumerate(path.read_text().splitlines(), 1):
            try:
                row = json.loads(line, parse_constant=reject_constant)
                if not isinstance(row, dict):
                    raise ValueError("record is not an object")
                rows.append(row)
            except (ValueError, TypeError) as exc:
                error("A01", None, f"{path.name}:{line_number}: {exc}")
        return rows

    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    sources = read(sources_path)
    annotations = read(annotations_path)
    index: dict[str, dict] = {}
    indices = set()
    for source in sources:
        sid = source.get("source_id")
        if not isinstance(sid, str) or not sid:
            error("A01", None, "source_id must be a nonempty string")
            continue
        row_index = source.get("source_row_index")
        if type(row_index) is not int or row_index < 0:
            error("A01", sid, "invalid source_row_index")
        elif row_index in indices:
            error("C01", sid, "duplicate source_row_index")
        else:
            indices.add(row_index)
        if sid in index:
            error("C01", sid, "duplicate source_id")
        index[sid] = source
        note = source.get("note_text")
        if not isinstance(note, str) or not note.strip():
            error("A01", sid, "missing/empty source text")
        elif digest(note) != source.get("source_sha256"):
            error("A01", sid, "source text SHA-256 mismatch")
        if type(source.get("row_ok")) is not bool:
            error("A01", sid, "row_ok must be supplied as a boolean; false is included")
    if len(index) != expected:
        error("C01", None, f"expected {expected} source IDs; found {len(index)}")
    seen = set()
    unresolved = []
    for record in annotations:
        sid = record.get("source_id")
        problems = sorted(validator.iter_errors(record), key=lambda e: str(e.json_path))
        for problem in problems:
            error(
                "A01",
                sid if isinstance(sid, str) else None,
                f"{problem.json_path}: {problem.message}",
            )
        if not isinstance(sid, str):
            continue
        if sid in seen:
            error("C01", sid, "duplicate annotation")
        seen.add(sid)
        if sid not in index:
            error("C01", sid, "annotation has no supplied source")
            continue
        if problems:
            continue
        source = index[sid]
        for key in ("source_row_index", "source_sha256"):
            if source.get(key) != record[key]:
                error("A01", sid, f"{key} differs from source")
        note = source.get("note_text")
        if not isinstance(note, str):
            continue
        findings = record["findings"]
        ids = [f["id"] for f in findings]
        issues = record["issues"]
        issue_ids = [i["id"] for i in issues]
        contexts = record["finding_context"]
        context_ids = [c["finding_id"] for c in contexts]
        if len(ids) != len(set(ids)) or len(issue_ids) != len(set(issue_ids)):
            error("A01", sid, "duplicate finding or issue IDs")
        if len(context_ids) != len(set(context_ids)) or set(context_ids) != set(ids):
            error("A01", sid, "exactly one finding_context is required per finding")

        def quote(text: str, note: str = note, sid: str = sid) -> None:
            if not text.strip() or text not in note:
                error("A07", sid, f"non-exact/empty quotation: {text!r}")

        def refs(values: list[str], allowed: list[str], kind: str, sid: str = sid) -> None:
            if len(values) != len(set(values)) or not set(values) <= set(allowed):
                error("A01", sid, f"invalid/duplicate {kind} references: {values}")

        for item in findings + record["document_dates"] + issues + record["source_checks"]:
            quote(item["evidence"])

        def quantities(value: object, sid: str = sid) -> None:
            if isinstance(value, list):
                for child in value:
                    quantities(child)
            elif isinstance(value, dict):
                if value.get("type") == "range":
                    lo, hi = value["lower"], value["upper"]
                    if lo > hi or (
                        lo == hi
                        and not (
                            value.get("lower_inclusive", True)
                            and value.get("upper_inclusive", True)
                        )
                    ):
                        error("A05", sid, "reversed or empty range")
                if value.get("type") == "bound" and "unit" in value:
                    bound = value["value"]
                    minimum = bound["lower"] if isinstance(bound, dict) else bound
                    if minimum <= 0:
                        error("A05", sid, "duration bound must be positive")
                for child in value.values():
                    quantities(child)

        quantities(findings)
        for finding in findings:
            measurement = finding["measurement"]
            if measurement["type"] == "cluster" and measurement.get("count") is not None:
                if not finding.get("period") and not measurement.get("occurred_at"):
                    error("A04", sid, f"{finding['id']}: cluster count needs a time anchor")
        by_id = {f["id"]: f for f in findings}
        for context in contexts:
            for mention in context["mentions"]:
                quote(mention)
            if context["finding_id"] in by_id:
                if by_id[context["finding_id"]]["evidence"] not in context["mentions"]:
                    error("A07", sid, "principal evidence missing from mentions")
            for relation in context["relations"]:
                refs([relation["target_id"]], ids, "relation")
                if relation["target_id"] == context["finding_id"]:
                    error("A08", sid, "self relation")
        for issue in issues:
            refs(issue["finding_ids"], ids, "issue finding")
        covered_findings, covered_issues = set(), set()
        for candidate in record["source_checks"]:
            refs(candidate["finding_ids"], ids, "candidate finding")
            refs(candidate["issue_ids"], issue_ids, "candidate issue")
            covered_findings.update(candidate["finding_ids"])
            covered_issues.update(candidate["issue_ids"])
            state = candidate["disposition"]
            if state in ("included", "repeat") and not candidate["finding_ids"]:
                error("A02", sid, "included/repeated candidate has no finding")
            if state == "unresolved" and not candidate["issue_ids"]:
                error("A09", sid, "unresolved candidate has no issue")
            if state == "excluded" and (
                not candidate["reason"].strip()
                or candidate["finding_ids"]
                or candidate["issue_ids"]
            ):
                error("A02", sid, "excluded candidate needs reason and empty links")
        if covered_findings != set(ids) or covered_issues != set(issue_ids):
            error("A02", sid, "every finding/issue must be linked from source_checks")
        if bool(issues) != (record["annotation_state"] == "needs_review"):
            error("A09", sid, "needs_review must correspond to open issues")
        if record["annotation_state"] != "complete":
            unresolved.append(sid)
        if record["annotation_state"] == "source_unavailable" and note.strip():
            error("A09", sid, "source_unavailable although supplied source is readable")
    for sid in sorted(set(index) - seen):
        error("C01", sid, "missing annotation")
    return {
        "status": "fail" if errors else "pass",
        "scope": "mechanical checks only; not source completeness or clinical support",
        "expected_sources": expected,
        "source_records": len(sources),
        "annotation_records": len(annotations),
        "unresolved_source_ids": unresolved,
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument(
        "--schema", type=Path, default=Path(__file__).with_name("annotation.schema.json")
    )
    parser.add_argument(
        "--expected",
        type=int,
        default=750,
        help="750 for the complete run; actual manifest size for pilot/fixtures",
    )
    args = parser.parse_args()
    if args.expected <= 0:
        parser.error("--expected must be positive")
    try:
        result = check(args.sources, args.annotations, args.schema, args.expected)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Input/setup error: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(result["status"] != "pass")


if __name__ == "__main__":
    main()
