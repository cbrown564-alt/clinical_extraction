"""Capture, check, review and replay seed-free authoring; never call a provider.

The author supplies saved histories, consultation plans, finished letters and
text-supported references. This program renders exact quotes into offsets and
filtered inputs; it never derives a clinical assertion or query answer from a
hidden history. Raw attempts are immutable and semantic review is explicit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.longitudinal.check_annotations import load_example  # noqa: E402
from scripts.longitudinal.evaluate_query_witnesses import evaluate_query  # noqa: E402
from scripts.longitudinal.verify_patient_case import (  # noqa: E402
    expected_requests,
    input_payload,
    verify_patient_case,
)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def save(path: Path, value: dict | list) -> None:
    """Exclusive creation: a successful capture/review is never overwritten."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def case_hashes(path: Path) -> dict[str, str]:
    return {
        str(p.relative_to(path)): digest(p.read_bytes())
        for p in sorted(path.rglob("*"))
        if p.is_file()
    }


def object_hash(value: dict) -> str:
    return digest(json.dumps(value, sort_keys=True, ensure_ascii=False).encode())


def now() -> str:
    return datetime.now(UTC).isoformat()


def validate_config(config: dict) -> None:
    required = {
        "mode": "seed_free_authoring",
        "provider_enabled": False,
        "source_conditioned_generation": False,
        "source_records": [],
        "additional_paid_call_cap_gbp": 0,
        "per_patient_paid_call_cap_gbp": 0,
        "automatic_retries": 0,
        "inspection_policy": "development_only",
    }
    if any(config.get(k) != v for k, v in required.items()):
        raise ValueError(
            "Only development-only seed-free authoring with zero provider calls is enabled"
        )
    patients = config["patients"]
    ids = [p["patient_id"] for p in patients]
    if len(ids) != len(set(ids)) or not all(re.fullmatch(r"[a-z0-9-]+", x) for x in ids):
        raise ValueError("Patient IDs must be unique safe identifiers")
    stages = config["stage_patient_counts"]
    if stages != sorted(set(stages)) or stages[0] != 1 or stages[-1] != len(patients):
        raise ValueError("Invalid cumulative stages")
    for name, expected in config["pinned_sha256"].items():
        if digest((ROOT / name).read_bytes()) != expected:
            raise ValueError(f"Configuration pin changed: {name}")


def expand_spans(value: object, texts: dict[str, str]) -> object:
    """Mechanical offset assignment only; ambiguous quotes require explicit offsets."""
    if isinstance(value, list):
        return [expand_spans(v, texts) for v in value]
    if not isinstance(value, dict):
        return value
    if "letter_id" in value and "text" in value:
        source, quote = texts[value["letter_id"]], value["text"]
        if "start" in value or "end" in value:
            if source[value["start"] : value["end"]] != quote:
                raise ValueError("Explicit evidence offsets do not match final text")
            return value
        if not quote or source.count(quote) != 1:
            raise ValueError("Evidence quote must occur exactly once in its final letter")
        start = source.index(quote)
        return {**value, "start": start, "end": start + len(quote)}
    return {k: expand_spans(v, texts) for k, v in value.items()}


def render_case(source: dict, config: dict, destination: Path) -> None:
    pid = source["patient_id"]
    plan = next(p for p in config["patients"] if p["patient_id"] == pid)
    if (
        source["origin"] != "fictional_seed_free"
        or source["source_records"]
        or source["age_at_first_visit"] < 18
        or not source["history"]
        or not source["lineage"]
        or not source["documentation_plan"]
    ):
        raise ValueError("Missing adult fictional origin, history, documentation plan or lineage")
    if source["documentation_plan"]["style"] != plan["style"]:
        raise ValueError("Style differs from its preassigned configuration")
    if source["revision"] < 1:
        raise ValueError("Invalid revision")
    texts = {d["letter_id"]: d["text"] for d in source["documents"]}
    if len(texts) != 3 or set(texts) != {"L1", "L2", "L3"}:
        raise ValueError("Exactly three unique letters required")
    documents = {}
    for d in source["documents"]:
        path = f"letters/{d['letter_id']}.txt"
        raw = d["text"].encode()
        target = destination / path
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(raw)
        documents[d["letter_id"]] = {
            "letter_id": d["letter_id"],
            "version": source["revision"],
            "visit_date": d["visit_date"],
            "available_date": d["available_date"],
            "path": path,
            "sha256": digest(raw),
        }
    requests = expected_requests(source["first_index"])
    save(
        destination / "manifest.json",
        {
            "case_id": pid,
            "version": str(source["revision"]),
            "task_definition_version": "0.2",
            "annotation_guide_version": "0.3",
            "origin": "AI-authored fictional seed-free development case",
            "inspection_policy": "development_only",
            "expert_review": False,
            "independent_annotation": False,
            "lineage": source["lineage"],
            "scenario": plan["scenario"],
            "style": plan["style"],
            "author": config["author"],
            "documents": list(documents.values()),
            "requests": requests,
            "annotation": {"no_assertion_letters": source.get("no_assertion_letters", {})},
        },
    )
    save(destination / "annotations.json", expand_spans(source["annotations"], texts))
    reference = expand_spans(source["reference"], texts)
    save(
        destination / "reference.json",
        {
            **reference,
            "case_id": pid,
            "version": str(source["revision"]),
            "reference_kind": "provisional same-assistant text review; not expert gold",
        },
    )
    docs = {lid: {**d, "text": texts[lid]} for lid, d in documents.items()}
    for req in requests:
        path = destination / req["input_path"]
        if not path.exists():
            save(path, input_payload(pid, docs, req["information_cutoff"]))


def qc_case(case: Path) -> dict:
    report = verify_patient_case(case)
    report.pop("case_dir")
    annotations, docs, _ = load_example(case)
    manifest, reference = read(case / "manifest.json"), read(case / "reference.json")
    annotated = {a["letter_id"] for a in annotations["assertions"]}
    empty = manifest["annotation"]["no_assertion_letters"]
    if (
        annotated & empty.keys()
        or annotated | empty.keys() != docs.keys()
        or not all(isinstance(v, str) and v.strip() for v in empty.values())
    ):
        raise ValueError("Each letter needs assertions or an explicit no-reference reason")
    evidence = {e["evidence_id"]: e for e in reference["evidence"]}
    links = {link["link_id"]: link for link in reference["links"]}
    answers = {a["request_id"]: a for a in reference["answers"]}
    diagnostics = []
    for req in manifest["requests"]:
        answer = answers[req["request_id"]]
        if answer["status"] != "indeterminate" and not answer["evidence_ids"]:
            raise ValueError("Definitive reference requires evidence")
        for lid in answer.get("link_ids", []):
            link = links[lid]
            ids = [
                link["earlier_evidence"],
                link["later_evidence"],
                *link.get("supporting_evidence", []),
            ]
            if any(
                docs[evidence[e]["letter_id"]]["available_date"] > req["information_cutoff"]
                for e in ids
            ):
                raise ValueError("Answer link uses evidence beyond cutoff")
        prediction = evaluate_query(annotations, docs, req)
        diagnostics.append(
            {
                "request_id": req["request_id"],
                "prediction": prediction,
                "reference_status": answer["status"],
                "matches": prediction["status"] == answer["status"],
            }
        )
    review_items = (
        [f"assertion:{a['assertion_id']}" for a in annotations["assertions"]]
        + [f"link:{link['link_id']}" for link in annotations["links"]]
        + [f"answer:{a['request_id']}" for a in reference["answers"]]
        + [f"diagnostic:{r['request_id']}" for r in diagnostics if not r["matches"]]
    )
    return {
        **report,
        "review_items": review_items,
        "query_diagnostic": diagnostics,
        "reference_status_counts": dict(Counter(a["status"] for a in answers.values())),
        "semantic_support": "requires recorded internal review; checks alone cannot establish it",
    }


def stage_record(run: Path, count: int) -> dict:
    paths = sorted((run / "stages").glob(f"stage-{count:02d}-capture-*.json"))
    if not paths:
        raise ValueError("Missing previous stage capture")
    return read(paths[-1])


def check_capture(run: Path, capture: dict) -> None:
    for p in capture["patients"]:
        attempt = run / p["attempt_path"]
        if digest((attempt / "raw.json").read_bytes()) != p["source_sha256"]:
            raise ValueError("Captured raw hash changed")
        if p["status"] == "checked":
            if (
                object_hash(case_hashes(attempt / "case")) != p["case_sha256"]
                or digest((attempt / "qc.json").read_bytes()) != p["qc_sha256"]
            ):
                raise ValueError("Case or QC hash changed after capture")


def checked_review(run: Path, count: int) -> dict:
    capture = stage_record(run, count)
    check_capture(run, capture)
    path = run / "stages" / f"stage-{count:02d}-review.json"
    if not path.exists():
        raise ValueError("Missing recorded review of previous stage")
    review = read(path)
    if review["capture_sha256"] != object_hash(capture):
        raise ValueError("Review hash is stale")
    if any(p["disposition"] == "needs_revision" for p in review["patients"]):
        raise ValueError("Previous stage review still needs revision")
    return review


def capture_stage(
    config_path: Path, run: Path, sources: Path, count: int, *, retry: set[str] | None = None
) -> dict:
    start, started = time.monotonic(), now()
    config = read(config_path)
    validate_config(config)
    retry = retry or set()
    stages = config["stage_patient_counts"]
    if count not in stages:
        raise ValueError("Count must be a configured stage")
    if stages.index(count):
        checked_review(run, stages[stages.index(count) - 1])
    saved = run / "config.json"
    if saved.exists():
        if read(saved) != config:
            raise ValueError("Configuration changed; use a new run revision")
    else:
        save(saved, config)
        save(
            run / "provenance.json",
            {
                "started_at": started,
                "config_sha256": object_hash(config),
                "program_sha256": digest(Path(__file__).read_bytes()),
                "author": config["author"],
                "provider_calls": 0,
                "additional_api_cost_gbp": 0,
                "repair_policy": "exact quote offsets only; semantic edits need a new revision",
                "replay_mode": "saved authoring output",
                "split": "development_only",
                "account_usage_cost": None,
                "human_effort_minutes": None,
            },
        )
    if read(run / "provenance.json")["program_sha256"] != digest(Path(__file__).read_bytes()):
        raise ValueError("Program changed; use a new run revision")
    if not retry.issubset({p["patient_id"] for p in config["patients"][:count]}):
        raise ValueError("Retry patient is outside the requested stage")
    patients = []
    for plan in config["patients"][:count]:
        pid = plan["patient_id"]
        source_path = sources / f"{pid}.json"
        previous = sorted((run / "patients" / pid).glob("attempt-*"))
        raw = source_path.read_bytes() if source_path.exists() else b""
        if previous:
            attempt = previous[-1]
            if not (attempt / "record.json").exists():
                if pid not in retry:
                    raise ValueError("Interrupted attempt retained; explicitly retry this patient")
                save(
                    attempt / "record.json",
                    {
                        "patient_id": pid,
                        "attempt_path": str(attempt.relative_to(run)),
                        "source_sha256": digest((attempt / "raw.json").read_bytes()),
                        "status": "failed",
                        "reason": "Interrupted before capture record completed",
                    },
                )
            prior = read(attempt / "record.json")
            if prior["status"] == "checked":
                check_capture(run, {"patients": [prior]})
                if digest(raw) != prior["source_sha256"] or pid in retry:
                    raise ValueError("Successful source changed; use a new run revision")
                patients.append(prior)
                continue
            if pid not in retry:
                if digest(raw) != prior["source_sha256"]:
                    raise ValueError("Failed input changed; explicitly retry this patient")
                patients.append(prior)
                continue
            try:
                old_source = read(attempt / "raw.json")
                new_source = json.loads(raw)
            except (ValueError, TypeError):
                pass  # Malformed raw has no usable revision; preserve it regardless.
            else:
                if digest(raw) != prior["source_sha256"] and new_source.get(
                    "revision", 0
                ) <= old_source.get("revision", 0):
                    raise ValueError("Changed failed input requires a new source revision")
        attempt = run / "patients" / pid / f"attempt-{len(previous) + 1:03d}"
        attempt.mkdir(parents=True)
        (attempt / "raw.json").write_bytes(raw)
        item = {
            "patient_id": pid,
            "attempt_path": str(attempt.relative_to(run)),
            "source_sha256": digest(raw),
            "started_at": now(),
        }
        patient_start = time.monotonic()
        try:
            source = json.loads(raw)
            if source["patient_id"] != pid:
                raise ValueError("Source patient ID differs from plan")
            render_case(source, config, attempt / "case")
            qc = qc_case(attempt / "case")
            save(attempt / "qc.json", qc)
            item.update(
                status="checked",
                case_sha256=object_hash(case_hashes(attempt / "case")),
                qc_sha256=digest((attempt / "qc.json").read_bytes()),
                review_items=qc["review_items"],
            )
        except (ValueError, KeyError, TypeError, StopIteration) as exc:
            item.update(status="failed", reason=f"{type(exc).__name__}: {exc}")
        item.update(ended_at=now(), wall_seconds=time.monotonic() - patient_start)
        save(attempt / "record.json", item)
        patients.append(item)
    record = {
        "count": count,
        "started_at": started,
        "ended_at": now(),
        "capture_wall_seconds": time.monotonic() - start,
        "patients": patients,
    }
    existing = sorted((run / "stages").glob(f"stage-{count:02d}-capture-*.json"))
    if existing and read(existing[-1])["patients"] == patients:
        return read(existing[-1])
    save(run / "stages" / f"stage-{count:02d}-capture-{len(existing) + 1:03d}.json", record)
    return record


def review_stage(run: Path, count: int, review: dict) -> dict:
    capture = stage_record(run, count)
    check_capture(run, capture)
    patients = {p["patient_id"]: p for p in capture["patients"]}
    rows = review["patients"]
    if len(rows) != len(patients) or {r["patient_id"] for r in rows} != patients.keys():
        raise ValueError("Review patient coverage is incomplete or duplicated")
    if not review.get("reviewer") or review.get("independent") is not False:
        raise ValueError("This authoring probe requires an identified internal reviewer")
    for row in rows:
        p = patients[row["patient_id"]]
        if (
            row["disposition"] not in {"accepted", "needs_revision", "rejected"}
            or not row["reason"].strip()
        ):
            raise ValueError("Missing case disposition or reason")
        if row["disposition"] == "accepted":
            if p["status"] != "checked" or any(
                row[k] != p[k] for k in ("case_sha256", "qc_sha256")
            ):
                raise ValueError("Accepted review requires matching case and QC hashes")
            items = row["items"]
            if len(items) != len(p["review_items"]) or {x["item_id"] for x in items} != set(
                p["review_items"]
            ):
                raise ValueError("Semantic review item coverage is incomplete or duplicated")
            if not all(
                x["disposition"] in {"supported", "uncertainty_preserved", "diagnostic_limit"}
                and x["reason"].strip()
                for x in items
            ):
                raise ValueError("Accepted review includes an unresolved defect")
    result = {**review, "review_recorded_at": now(), "capture_sha256": object_hash(capture)}
    save(run / "stages" / f"stage-{count:02d}-review.json", result)
    return result


def regenerate(run: Path, destination: Path) -> dict:
    config = read(run / "config.json")
    validate_config(config)
    if read(run / "provenance.json")["program_sha256"] != digest(Path(__file__).read_bytes()):
        raise ValueError("Program hash changed")
    if destination.exists():
        raise ValueError("Replay destination must be new")
    reviewed = [
        n
        for n in config["stage_patient_counts"]
        if (run / "stages" / f"stage-{n:02d}-review.json").exists()
    ]
    if not reviewed:
        raise ValueError("No reviewed stage")
    count = reviewed[-1]
    review = checked_review(run, count)
    capture = stage_record(run, count)
    accepted = {p["patient_id"] for p in review["patients"] if p["disposition"] == "accepted"}
    records = []
    for p in capture["patients"]:
        if p["patient_id"] not in accepted:
            continue
        attempt = run / p["attempt_path"]
        target = destination / p["patient_id"]
        render_case(read(attempt / "raw.json"), config, target)
        qc = qc_case(target)
        if case_hashes(target) != case_hashes(attempt / "case") or qc != read(attempt / "qc.json"):
            raise ValueError("Saved-output regeneration changed case bytes or QC")
        records.append({"patient_id": p["patient_id"], "sha256": case_hashes(target)})
    return {
        "byte_identical": True,
        "accepted_patients": len(records),
        "planned_patients": count,
        "cases": records,
        "mode": "saved-output replay",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    capture = commands.add_parser("capture")
    capture.add_argument("--config", type=Path, required=True)
    capture.add_argument("--run", type=Path, required=True)
    capture.add_argument("--sources", type=Path, required=True)
    capture.add_argument("--count", type=int, required=True)
    capture.add_argument("--retry", action="append", default=[])
    review = commands.add_parser("review")
    review.add_argument("--run", type=Path, required=True)
    review.add_argument("--count", type=int, required=True)
    review.add_argument("--review", type=Path, required=True)
    replay = commands.add_parser("replay")
    replay.add_argument("--run", type=Path, required=True)
    replay.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "capture":
        result = capture_stage(
            args.config, args.run, args.sources, args.count, retry=set(args.retry)
        )
        print(
            json.dumps(
                {
                    "count": result["count"],
                    "patients": [
                        {k: p[k] for k in ("patient_id", "status", "reason") if k in p}
                        for p in result["patients"]
                    ],
                },
                indent=2,
            )
        )
    elif args.command == "review":
        result = review_stage(args.run, args.count, read(args.review))
        print(json.dumps({"reviewed": len(result["patients"])}))
    else:
        result = regenerate(args.run, args.destination)
        save(args.destination / "replay.json", result)
        print(json.dumps({k: v for k, v in result.items() if k != "cases"}, indent=2))


if __name__ == "__main__":
    main()
