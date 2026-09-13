"""Audit a reviewed seed-free batch and copy only allowlisted fictional cases.

No source histories, raw drafts or private corpus records are exported. Exact
replay is provided by generate_seed_free_batch.py; this command recomputes the
reviewed batch summary, duplicate candidates and source evidence inventory.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.longitudinal.generate_seed_free_batch import (  # noqa: E402
    case_hashes,
    checked_review,
    digest,
    qc_case,
    read,
    save,
    stage_record,
    validate_config,
)

CASE_FILES = (
    ["manifest.json", "annotations.json", "reference.json"]
    + [f"letters/L{i}.txt" for i in (1, 2, 3)]
    + [f"inputs/T{i}_{view}.json" for i in (1, 2) for view in ("visit", "retrospective")]
)


def tokens(text: str) -> list[str]:
    # Remove only the known generated metadata header. Patient IDs must not
    # manufacture apparent uniqueness. Phase 2 source letters remain intact.
    if text.startswith("Fictional outpatient letter |"):
        text = text.split("\n\n", 1)[1]
    return re.findall(r"\w+", text.casefold())


def duplicate_audit(cases: list[Path]) -> dict:
    records = []
    paths = [p for case in cases for p in (case / "letters").glob("*.txt")]
    paths += sorted((ROOT / "examples/longitudinal").glob("authored_patient_*/letters/*.txt"))
    for path in paths:
        words = tokens(path.read_text())
        records.append(
            {
                "id": f"{path.parent.parent.name}/{path.name}",
                "generated": path in paths[: len(cases) * 3],
                "sha256": digest(path.read_bytes()),
                "normalized": " ".join(words),
                "shingles": set(tuple(words[i : i + 5]) for i in range(max(0, len(words) - 4))),
            }
        )
    pairs = []
    for a, b in combinations(records, 2):
        if not a["generated"] and not b["generated"]:
            continue
        exact = bool(a["normalized"]) and a["normalized"] == b["normalized"]
        union = a["shingles"] | b["shingles"]
        score = len(a["shingles"] & b["shingles"]) / len(union) if union else 0.0
        if exact or score >= 0.8:
            pairs.append(
                {
                    "left": a["id"],
                    "right": b["id"],
                    "exact": exact,
                    "jaccard": score,
                    "disposition": "retain in development",
                    "reason": "Known shared authoring context; no independence or split claim",
                }
            )
    return {
        "threshold": 0.8,
        "shingle_tokens": 5,
        "normalization": "casefolded word tokens; strip known generated metadata header",
        "generated_letters": len(cases) * 3,
        "phase2_context_letters": len(records) - len(cases) * 3,
        "pairs": pairs,
        "source_hashes": {r["id"]: r["sha256"] for r in records},
        "lineage_disposition": (
            "All 12 records share one conservative authoring-template family. "
            "Phase 2 is declared development-only authoring context. No train/test assignment."
        ),
        "limitation": "Low similarity does not establish independent histories or source ancestry",
    }


def summarize(run: Path) -> tuple[dict, dict, dict]:
    config = read(run / "config.json")
    validate_config(config)
    count = config["stage_patient_counts"][-1]
    capture, review = stage_record(run, count), checked_review(run, count)
    accepted = {p["patient_id"] for p in review["patients"] if p["disposition"] == "accepted"}
    if len(accepted) != count:
        raise ValueError("This completion package requires every planned patient to be accepted")
    statuses: Counter = Counter()
    families: Counter = Counter()
    by_style: dict[str, Counter] = defaultdict(Counter)
    by_query: dict[str, Counter] = defaultdict(Counter)
    style_scenario: dict[str, Counter] = defaultdict(Counter)
    review_rows = {p["patient_id"]: p for p in review["patients"]}
    cases, rows, diagnostics = [], [], []
    assertions = links = cross_letter = different_views = 0
    for p in capture["patients"]:
        case = run / p["attempt_path"] / "case"
        qc = qc_case(case)
        if qc != read(case.parent / "qc.json"):
            raise ValueError("QC changed")
        if set(case_hashes(case)) != set(CASE_FILES):
            raise ValueError("Case contains files outside the reviewed allowlist")
        manifest, annotation, reference = (read(case / f) for f in CASE_FILES[:3])
        cases.append(case)
        assertions += len(annotation["assertions"])
        links += len(annotation["links"])
        style_scenario[manifest["style"]][manifest["scenario"]] += 1
        for a in annotation["assertions"]:
            families[a["content"]["family"]] += 1
            quote = " ".join(e["text"] for e in a["evidence"])
            for field in (a["time"], a["content"].get("burden")):
                if field and field.get("text") and field["text"] not in quote:
                    raise ValueError("Source time/burden wording is not preserved")
        for link in annotation["links"]:
            if link["decision_time"] and link["decision_time"].get("text"):
                if not any(link["decision_time"]["text"] in e["text"] for e in link["evidence"]):
                    raise ValueError("Decision time wording is not preserved")
        evidence = {e["evidence_id"]: e for e in reference["evidence"]}
        answers = {a["request_id"]: a for a in reference["answers"]}
        for answer in answers.values():
            statuses[answer["status"]] += 1
            by_style[manifest["style"]][answer["status"]] += 1
            by_query[answer["request_id"].split("_")[-1]][answer["status"]] += 1
            cross_letter += len({evidence[e]["letter_id"] for e in answer["evidence_ids"]}) > 1
        for index in (1, 2):
            for query in range(1, 6):
                different_views += (
                    answers[f"T{index}_visit_Q{query}"]["status"]
                    != answers[f"T{index}_retrospective_Q{query}"]["status"]
                )
        items = {r["item_id"]: r for r in review_rows[p["patient_id"]]["items"]}
        for diagnostic in qc["query_diagnostic"]:
            if not diagnostic["matches"]:
                diagnostics.append(
                    {
                        "patient_id": p["patient_id"],
                        **diagnostic,
                        "review": items[f"diagnostic:{diagnostic['request_id']}"],
                    }
                )
        rows.append(
            {
                "patient_id": p["patient_id"],
                "style": manifest["style"],
                "scenario": manifest["scenario"],
                "revision": manifest["version"],
                "assertions": len(annotation["assertions"]),
                "links": len(annotation["links"]),
                "letter_words": [
                    len(tokens(f.read_text())) for f in sorted((case / "letters").glob("*.txt"))
                ],
                "files": case_hashes(case),
                "source_sha256": p["source_sha256"],
                "case_sha256": p["case_sha256"],
                "qc_sha256": p["qc_sha256"],
            }
        )
    stages = []
    for n in config["stage_patient_counts"]:
        cap, rev = stage_record(run, n), checked_review(run, n)
        stages.append(
            {
                "count": n,
                "capture_started_at": cap["started_at"],
                "capture_wall_seconds": cap["capture_wall_seconds"],
                "review_recorded_at": rev["review_recorded_at"],
                "capture_to_review_elapsed_seconds": (
                    datetime.fromisoformat(rev["review_recorded_at"])
                    - datetime.fromisoformat(cap["started_at"])
                ).total_seconds(),
                "dispositions": dict(Counter(p["disposition"] for p in rev["patients"])),
            }
        )
    history = []
    for path in sorted(run.parent.glob("capture*/patients/*/attempt-*/record.json")):
        record = read(path)
        history.append(
            {
                "path": str(path.resolve().relative_to(ROOT)),
                "patient_id": record["patient_id"],
                "status": record["status"],
                "source_sha256": record["source_sha256"],
            }
        )
    summary = {
        "dataset": "generation_v0.1",
        "split": "development_only",
        "row_policy": "12 configured patients, each with 20 fixed requests; no exclusions",
        "mode": "seed-free same-assistant authoring; saved-output regeneration",
        "author": config["author"],
        "annotation_version": "0.3",
        "query_definition_version": "0.2",
        "provider_calls": 0,
        "additional_api_cost_gbp": 0,
        "assistant_account_cost": None,
        "human_effort_minutes": None,
        "accepted_patients": count,
        "letters": count * 3,
        "assertions": assertions,
        "assertions_by_family": dict(families),
        "links": links,
        "requests": sum(statuses.values()),
        "reference_status_counts": dict(statuses),
        "by_query": dict(by_query),
        "by_style": dict(by_style),
        "style_scenario_counts": dict(style_scenario),
        "different_view_pairs": different_views,
        "view_pairs": count * 10,
        "cross_letter_answer_references": cross_letter,
        "diagnostic_matches": count * 20 - len(diagnostics),
        "diagnostic_mismatches": len(diagnostics),
        "diagnostic_program": "scripts/longitudinal/evaluate_query_witnesses.py",
        "diagnostic_limit": "Incomplete evaluator; agreement was not an acceptance criterion",
        "semantic_review": (
            "All assertions, links and answers have same-assistant internal dispositions. "
            "No independent clinical adjudication."
        ),
        "unresolved_internal_review_defects": 0,
        "expert_validation": False,
        "common_ancestor": config["common_ancestor"],
        "independent_history_count_claimed": False,
        "stage_records": stages,
        "cases": rows,
        "diagnostic_rows": diagnostics,
        "retained_capture_records": history,
        "provenance": read(run / "provenance.json"),
        "summary_program_sha256": digest(Path(__file__).read_bytes()),
    }
    return summary, duplicate_audit(cases), review


def persist(path: Path, value: dict) -> None:
    if path.exists():
        if read(path) != value:
            raise ValueError(f"Existing reviewed output differs: {path}")
    else:
        save(path, value)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary, duplicates, review = summarize(args.run)
    for p in stage_record(args.run, summary["accepted_patients"])["patients"]:
        source = args.run / p["attempt_path"] / "case"
        for name in CASE_FILES:
            target = args.output / "cases" / p["patient_id"] / name
            raw = (source / name).read_bytes()
            if target.exists():
                if target.read_bytes() != raw:
                    raise ValueError(f"Export differs: {target}")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as stream:
                    stream.write(raw)
    persist(args.output / "summary.json", summary)
    persist(args.output / "duplicate_audit.json", duplicates)
    persist(args.output / "internal_review.json", review)
    print(
        json.dumps(
            {
                k: summary[k]
                for k in (
                    "accepted_patients",
                    "letters",
                    "assertions",
                    "links",
                    "requests",
                    "reference_status_counts",
                    "diagnostic_matches",
                    "diagnostic_mismatches",
                )
            },
            indent=2,
        )
    )
    print(f"Duplicate candidates: {len(duplicates['pairs'])}")


if __name__ == "__main__":
    main()
