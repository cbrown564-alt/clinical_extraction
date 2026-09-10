"""Check authored annotation structure and references, without clinical adjudication."""

import argparse
import hashlib
import json
import re
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]


def fold_evidence(text: str) -> str:
    """Gan-style light surface normalization; no clinical or synonym repair."""
    text = unicodedata.normalize("NFKC", text).casefold()
    text = text.replace("≤", "<=").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", text).strip()


def grounded_span(span: dict, documents: dict) -> bool:
    try:
        quote = fold_evidence(span["text"])
        return bool(quote) and quote in fold_evidence(documents[span["letter_id"]]["text"])
    except (KeyError, TypeError, AttributeError):
        return False


def evidence_overlap(left: dict, right: dict) -> bool:
    if left.get("letter_id") != right.get("letter_id"):
        return False
    a, b = fold_evidence(left["text"]), fold_evidence(right["text"])
    if min(len(a), len(b)) < 5:
        return bool(a) and a == b
    return a in b or b in a


def load_example(path: Path) -> tuple[dict, dict, dict]:
    manifest = json.loads((path / "manifest.json").read_text())
    documents = {}
    for document in manifest["documents"]:
        raw = (path / document["path"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != document["sha256"]:
            raise ValueError("Source hash mismatch")
        if document["letter_id"] in documents:
            raise ValueError("Duplicate letter ID")
        documents[document["letter_id"]] = {**document, "text": raw.decode("utf-8")}
    return (
        json.loads((path / "annotations.json").read_text()),
        documents,
        json.loads((ROOT / "docs/longitudinal/annotation.schema.json").read_text()),
    )


def check_annotations(
    annotations: dict,
    documents: dict,
    schema: dict,
    *,
    cutoff: str | None = None,
    require_offsets: bool = True,
) -> None:
    """Reject malformed structure, invalid references and unavailable evidence."""
    Draft202012Validator.check_schema(schema)
    errors = list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(annotations)
    )
    if errors:
        raise ValueError(f"Schema: {errors[0].json_path}: {errors[0].message}")
    if cutoff is not None:
        date.fromisoformat(cutoff)

    def document(letter_id: str) -> dict:
        if letter_id not in documents:
            raise ValueError(f"Unknown letter: {letter_id}")
        source = documents[letter_id]
        date.fromisoformat(source["available_date"])
        if cutoff is not None and source["available_date"] > cutoff:
            raise ValueError(f"Letter after cutoff: {letter_id}")
        return source

    def spans(evidence: list, owner: str | None = None) -> None:
        for span in evidence:
            source = document(span["letter_id"])
            if owner is not None and span["letter_id"] != owner:
                raise ValueError("Assertion span belongs to another letter")
            if not require_offsets:
                if not grounded_span(span, documents):
                    raise ValueError("Evidence span is not grounded in source")
                continue
            start, end = span["start"], span["end"]
            if not 0 <= start < end <= len(source["text"]):
                raise ValueError("Invalid span bounds")
            if source["text"][start:end] != span["text"]:
                raise ValueError("Evidence span does not match source")

    def time(value: dict | None) -> None:
        if value is None:
            return
        if value["anchor_letter_id"] is not None:
            document(value["anchor_letter_id"])
        for endpoint in (value["start"], value["end"]):
            if endpoint and endpoint["earliest"] and endpoint["latest"]:
                if endpoint["earliest"] > endpoint["latest"]:
                    raise ValueError("Reversed date bounds")
        start, end = value["start"], value["end"]
        if start and end and start["earliest"] and end["latest"]:
            if start["earliest"] > end["latest"]:
                raise ValueError("Impossible interval bounds")

    def quantities(value: Any) -> None:
        if isinstance(value, dict):
            if "lower" in value and "upper" in value:
                lower, upper = value["lower"], value["upper"]
                if lower is not None and upper is not None:
                    if lower > upper or (
                        lower == upper
                        and (
                            not value.get("lower_inclusive", True)
                            or not value.get("upper_inclusive", True)
                        )
                    ):
                        raise ValueError("Invalid quantity bounds")
            for child in value.values():
                quantities(child)
        elif isinstance(value, list):
            for child in value:
                quantities(child)

    ids = set()
    for assertion in annotations["assertions"]:
        identifier = assertion["assertion_id"]
        if identifier in ids:
            raise ValueError("Duplicate assertion ID")
        ids.add(identifier)
        document(assertion["letter_id"])
        spans(assertion["evidence"], assertion["letter_id"])
        time(assertion["time"])
        quantities(assertion["content"])
    link_ids = set()
    for link in annotations["links"]:
        if link["link_id"] in link_ids:
            raise ValueError("Duplicate link ID")
        link_ids.add(link["link_id"])
        earlier, later = link["earlier_assertion"], link["later_assertion"]
        if earlier not in ids or later not in ids or earlier == later:
            raise ValueError("Invalid link endpoint")
        spans(link["evidence"])
        spans(link.get("first_reinterpretation_evidence", []))
        time(link["decision_time"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "example", nargs="?", type=Path, default=ROOT / "examples/longitudinal/authored_patient_001"
    )
    args = parser.parse_args()
    annotations, documents, schema = load_example(args.example)
    check_annotations(annotations, documents, schema)
    print(
        f"Checked {len(annotations['assertions'])} assertions and "
        f"{len(annotations['links'])} links; clinical meaning requires review."
    )


if __name__ == "__main__":
    main()
