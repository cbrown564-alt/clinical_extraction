"""Versioned saved-extraction adapter and patient-history execution."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]

from . import PROGRAM_VERSION
from .evidence import Record, digest, normalize_evidence
from .history import assemble_history, link_assertions
from .queries import evaluate_query

REPLAY = Path("results/longitudinal/pilot_v0.3")


def saved_extraction(
    root: Path, patient: str, frame: str, documents: Record, patient_id: str
) -> Record:
    """Replay actual saved model facts, rejecting changed inputs and capture failures."""
    attempt_dir = root / REPLAY / "agy_pass_medium/attempts" / patient / frame
    input_path = root / REPLAY / "independent_pass/inputs" / patient / f"{frame}.json"
    attempt_path = attempt_dir / "attempt.json"
    provenance = {
        "mode": "saved_model_extraction",
        "new_model_calls": 0,
        "query_context_visible_during_extraction": True,
        "semantic_repair": False,
    }
    try:
        attempt = json.loads(attempt_path.read_text())
        provenance.update(
            attempt=attempt, input_sha256=digest(input_path), attempt_sha256=digest(attempt_path)
        )
        if digest(input_path) != attempt["input_sha256"]:
            raise ValueError("Saved input hash mismatch")
        payload = json.loads(input_path.read_text())
        expected = [
            {k: d[k] for k in ("letter_id", "visit_date", "available_date", "text")}
            for d in documents.values()
        ]
        if payload["patient_id"] != patient_id or payload["documents"] != expected:
            raise ValueError("Saved extraction does not match the supplied patient letters/cutoff")
        if attempt["status"] != "parsed":
            raise ValueError("Original model capture failed; no facts are available for this view")
        parsed = attempt_dir / "parsed.json"
        provenance["raw_parsed_sha256"] = digest(parsed)
        provenance["raw_stdout_sha256"] = digest(attempt_dir / "stdout.jsonl")
        # Discard saved answers and links. The new linker sees predicted facts only.
        raw = json.loads(parsed.read_text())["annotations"]
        raw_facts = {"assertions": raw["assertions"], "links": []}
        normalized, repairs = normalize_evidence(raw_facts, documents)
        schema = json.loads((root / "docs/longitudinal/annotation.schema.json").read_text())
        errors = list(
            Draft202012Validator(
                schema, format_checker=Draft202012Validator.FORMAT_CHECKER
            ).iter_errors(normalized)
        )
        if errors:
            raise ValueError("Malformed extraction: " + errors[0].message)
        return {
            "status": "ready",
            "raw": raw_facts,
            "annotations": normalized,
            "offset_repairs": repairs,
            "provenance": provenance,
        }
    except (OSError, ValueError, KeyError, TypeError) as error:
        return {"status": "failed", "error": str(error), "provenance": provenance}


def run_frame(
    documents: Record,
    annotations: Record,
    requests: list[Record],
    provenance: Record,
    use_reference_links: bool = False,
    without_links: bool = False,
) -> Record:
    """Physically filter before linking, so changing views cannot mutate prior history."""
    cutoff = requests[0]["information_cutoff"]
    if any(r["information_cutoff"] != cutoff for r in requests):
        raise ValueError("A frame must have one information cutoff")
    permitted = {k: d for k, d in documents.items() if d["available_date"] <= cutoff}
    facts = [a for a in annotations["assertions"] if a["letter_id"] in permitted]
    ids = {a["assertion_id"] for a in facts}
    links = (
        [
            edge
            for edge in annotations["links"]
            if all(edge[k] in ids for k in ("earlier_assertion", "later_assertion"))
        ]
        if use_reference_links
        else link_assertions(facts, permitted)
    )
    if without_links:
        links = []
    selected = {"assertions": facts, "links": links}
    return {
        "program_version": PROGRAM_VERSION,
        "status": "ready",
        "provenance": provenance,
        "documents": list(permitted.values()),
        "annotations": selected,
        "history": assemble_history(facts, links),
        "requests": requests,
        "answers": [
            {
                "request_id": r["request_id"],
                "query_id": r["query_id"],
                **evaluate_query(selected, permitted, r),
            }
            for r in requests
        ],
    }
