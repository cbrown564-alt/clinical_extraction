"""Versioned one-year timing adjudication over the saved v0.8 development reference.

The v0.8 reference and saved R8 responses are inputs and are never overwritten.
This manifest records every changed development finding after a full timing audit.
No model or locked-test data is accessed.
"""

from __future__ import annotations

import calendar
import copy
import json
import re
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Any

from dateutil.parser import ParserError, parse
from dateutil.relativedelta import relativedelta
from jsonschema import Draft202012Validator

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_v08 as scorer,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from scripts.benchmarks.score_findings_v08 import aggregate, write_json, write_jsonl

BASE_RUN = Path("runs/seizure_finding_annotation_v0_8/dev750_r8_saved")
BASE_RESULT = Path(
    "results/letter-benchmarks/gan/seizure_finding_annotation_v0_8/dev750_r8_saved/score.json"
)
BASE_SCHEMA = Path(
    "results/letter-benchmarks/gan/seizure_finding_annotation_v0_8/annotation.schema.json"
)
RUN = Path("runs/seizure_finding_annotation_v0_8_1/dev750_r8_saved")
RESULT_DIR = Path("results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_1/dev750_r8_saved")
SCHEMA = RESULT_DIR.parent / "annotation.schema.json"
GUIDE_VERSION = "seizure_finding_annotation_v0.8.1"
POLICY_VERSION = "v0.8.1_one_year_timing_dev750_v1"

# Dates within one year of the letter. The structured occurrence date is explicit.
DATED_RECENT: dict[int, tuple[str, ...]] = {
    6251: ("f3",),
    14524: ("f1",),
    14530: ("f1", "f2"),
    14540: ("f1", "f2"),
    14562: ("f1", "f2"),
    14567: ("f1",),
    14581: ("f1", "f2"),
    14587: ("f1",),
    14592: ("f1",),
    14611: ("f1", "f2"),
    14628: ("f1",),
    14635: ("f1", "f2"),
    14645: ("f1", "f2"),
    14662: ("f1",),
    14672: ("f1", "f2"),
    14706: ("f2",),
}

# Dates or elapsed intervals more than one year before the letter.
DATED_OLD: dict[int, tuple[str, ...]] = {
    816: ("f3",),
    2965: ("f4",),
    3015: ("f2",),
    3113: ("f2",),
    4919: ("f2",),
    6029: ("f2",),
    7961: ("f1",),
    8265: ("f4",),
    15094: ("f2",),
    15108: ("f1",),
    15127: ("f1",),
    15129: ("f1",),
    15141: ("f1",),
    15242: ("f3",),
    15262: ("f1",),
}

# A stated month, bounded recent interval, or recent dated event elsewhere in
# the same letter locates the claim within the one-year window. An old baseline
# described only as "previously" is deliberately absent from this manifest.
RECENT_CONTEXT: dict[int, tuple[str, ...]] = {
    446: ("f1",),
    1880: ("f1",),
    2459: ("f1",),
    2541: ("f3",),
    2759: ("f1", "f2"),
    2932: ("f2",),
    3082: ("f1",),
    4337: ("f4",),
    4345: ("f2",),
    5827: ("f4",),
    6065: ("f7",),
    6701: ("f3",),
    7195: ("f2",),
    7581: ("f2",),
    10618: ("f3",),
    13051: ("f1",),
    13058: ("f2",),
    13114: ("f1",),
    13122: ("f1",),
    13149: ("f1",),
    13178: ("f1",),
    13190: ("f1",),
    13209: ("f1",),
    13267: ("f1",),
    13290: ("f2",),
    14187: ("f1", "f3"),
    14214: ("f1", "f3"),
    14250: ("f1", "f2"),
    14282: ("f2", "f3"),
    14284: ("f1", "f2"),
    14317: ("f1", "f2"),
    14332: ("f1", "f2"),
    14335: ("f1", "f2"),
    14383: ("f1", "f2"),
    14454: ("f1", "f2"),
    15267: ("f2",),
    15965: ("f7", "f8"),
    16107: ("f5",),
    16750: ("f1", "f2", "f3"),
}

# These quotations state a present, unchanged pattern despite an old
# "historical" label inherited from a larger surrounding comparison.
PRESENT_PATTERN: dict[int, tuple[str, ...]] = {
    4563: ("f4",),
    11002: ("f2",),
}


def overrides() -> dict[tuple[int, str], tuple[str, str]]:
    result: dict[tuple[int, str], tuple[str, str]] = {}
    for basis, timing, rows in (
        ("dated_within_one_year", "current", DATED_RECENT),
        ("dated_over_one_year", "historical", DATED_OLD),
        ("recent_context_within_one_year", "current", RECENT_CONTEXT),
        ("present_pattern", "current", PRESENT_PATTERN),
    ):
        for row_index, ids in rows.items():
            for ident in ids:
                key = row_index, ident
                if key in result:
                    raise ValueError(f"Duplicate timing adjudication: {key}")
                result[key] = timing, basis
    return result


def document_date(row: dict[str, Any]) -> str:
    dates = row["document_dates"]
    for role in ("clinic", "letter", "unspecified"):
        for item in dates:
            if item["role"] == role and item["form"] == "calendar":
                return str(item["time"])
    raise ValueError(f"No usable letter date on {row['source_row_index']}")


def one_year_classification(occurrence: str, document: str) -> str | None:
    """Classify a bounded occurrence date; None means the cutoff is unresolved."""
    clinic = parse(document, fuzzy=True).date()
    cutoff = clinic - relativedelta(years=1)
    phrase = occurrence.strip().lower()
    elapsed = re.search(
        r"\b(?:over |more than |approximately |about )?"
        r"(\d+|fourteen|two|three|four|five|six)\s+(months?|years?)\s+ago\b",
        phrase,
    )
    if elapsed:
        words = {
            "fourteen": 14,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
        }
        number = words.get(elapsed[1], int(elapsed[1]) if elapsed[1].isdigit() else 0)
        if "year" in elapsed[2]:
            return "historical" if number > 1 or "over " in phrase else "current"
        return "historical" if number > 12 or (number == 12 and "over " in phrase) else "current"
    year_only = re.fullmatch(r"((?:19|20)\d{2})", phrase)
    month_year = re.fullmatch(r"(\d{1,2})\s*[-/]\s*((?:19|20)\d{2})", phrase)
    if year_only:
        year = int(year_only[1])
        earliest, latest = date(year, 1, 1), date(year, 12, 31)
    elif month_year:
        month, year = int(month_year[1]), int(month_year[2])
        if not 1 <= month <= 12:
            return None
        earliest = date(year, month, 1)
        latest = date(year, month, calendar.monthrange(year, month)[1])
    elif re.search(r"(?:19|20)\d{2}", phrase) and "," not in phrase:
        try:
            parsed = parse(occurrence, fuzzy=True, default=datetime(2000, 1, 1)).date()
        except (ParserError, ValueError, OverflowError):
            return None
        if parsed.year == 2000:
            return None
        without_year = re.sub(r"(?:19|20)\d{2}", "", phrase)
        if re.search(r"\b\d{1,2}\b", without_year):
            earliest = latest = parsed
        else:
            earliest = date(parsed.year, parsed.month, 1)
            latest = date(
                parsed.year,
                parsed.month,
                calendar.monthrange(parsed.year, parsed.month)[1],
            )
    else:
        return None
    if latest < cutoff:
        return "historical"
    if earliest >= cutoff:
        return "current"
    return None


def main() -> None:
    references = [
        json.loads(line) for line in (BASE_RUN / "reference.jsonl").read_text().splitlines()
    ]
    bundle = json.loads((BASE_RUN / "review_bundle.json").read_text())
    baseline = json.loads(BASE_RESULT.read_text())
    if len(references) != 750 or len(bundle["rows"]) != 750:
        raise ValueError("Expected the complete saved development reference")
    changes = overrides()
    schema = json.loads(BASE_SCHEMA.read_text())
    schema["properties"]["guide_version"]["const"] = GUIDE_VERSION
    schema["description"] = (
        "Seizure-finding annotation v0.8.1: v0.8 structure with a one-year "
        "current/historical timing boundary."
    )
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    reference_rows: list[dict[str, Any]] = []
    review_rows: list[dict[str, Any]] = []
    scores: list[dict[str, Any]] = []
    audit: list[dict[str, Any]] = []
    applied: set[tuple[int, str]] = set()
    for source, old in zip(references, bundle["rows"], strict=True):
        index = source["source_row_index"]
        if index != old["source_row_index"] or source["source_id"] != old["source_id"]:
            raise ValueError(f"Source order changed at {index}")
        revised = copy.deepcopy(source)
        revised["guide_version"] = GUIDE_VERSION
        clinic_date = document_date(source)
        for finding in revised["findings"]:
            key = index, finding["id"]
            if key not in changes:
                continue
            new_timing, basis = changes[key]
            old_timing = finding.get("timing", "current")
            if new_timing == old_timing:
                raise ValueError(f"Redundant timing adjudication: {key}")
            finding["timing"] = new_timing
            applied.add(key)
            audit.append(
                {
                    "source_row_index": index,
                    "source_id": source["source_id"],
                    "source_sha256": source["source_sha256"],
                    "finding_id": finding["id"],
                    "clinic_or_letter_date": clinic_date,
                    "evidence": finding["evidence"],
                    "occurred_at": finding["measurement"].get("occurred_at"),
                    "period": finding.get("period"),
                    "before": old_timing,
                    "after": new_timing,
                    "basis": basis,
                }
            )
        validator.validate(revised)
        reference_rows.append(revised)
        prediction = old["predicted"]
        scored = scorer.score_letter(
            old["note"], revised["findings"], prediction if old["usable"] else None
        )
        scores.append(scored)
        matched_pred = {pred_id for pred_id, _ in scored["pairs"]}
        matched_gold = {gold_id for _, gold_id in scored["pairs"]}
        review = copy.deepcopy(old)
        review["reference"] = revised["findings"]
        review["pairs"] = scored["pairs"]
        review["unmatched_reference_ids"] = [
            f["id"] for f in revised["findings"] if f["id"] not in matched_gold
        ]
        review["unmatched_prediction_ids"] = [
            f["id"] for f in prediction if f["id"] not in matched_pred
        ]
        for prefix in ("v08", "purist"):
            review[prefix + "_tp"] = scored["tp"]
            review[prefix + "_fp"] = scored["fp"]
            review[prefix + "_fn"] = scored["fn"]
        review_rows.append(review)
    if applied != set(changes):
        raise ValueError(f"Missing adjudications: {sorted(set(changes) - applied)}")
    for row in reference_rows:
        clinic_date = document_date(row)
        for finding in row["findings"]:
            occurred_at = finding["measurement"].get("occurred_at")
            if not occurred_at:
                continue
            expected = one_year_classification(occurred_at["time"], clinic_date)
            if expected is not None and finding.get("timing", "current") != expected:
                raise ValueError(
                    f"One-year timing disagrees on {row['source_row_index']}:{finding['id']}"
                )
    if (
        sum(len(row["findings"]) for row in reference_rows)
        != baseline["finding_v08"]["reference_findings"]
    ):
        raise ValueError("Timing correction changed the finding inventory")
    summary = aggregate(scores)
    if summary["letters"] != 750 or summary["usable_letters"] != 714:
        raise ValueError("Development coverage changed")
    write_json(SCHEMA, schema)
    write_jsonl(RUN / "reference.jsonl", reference_rows)
    write_jsonl(RUN / "timing_adjudications.jsonl", audit)
    write_json(
        RUN / "review_bundle.json",
        {
            "scope": "Gan synthetic dev750; v0.8.1 timing labels versus saved R8 predictions",
            "matcher": scorer.VERSION,
            "aggregate": summary,
            "rows": review_rows,
        },
    )
    write_json(
        RESULT_DIR / "score.json",
        {
            "version": POLICY_VERSION,
            "dataset": "Gan 2026 synthetic",
            "split": "dev750",
            "row_policy": "all 750 development letters; 36 unusable saved R8 responses retained",
            "base_score_path": str(BASE_RESULT),
            "base_score_sha256": study.old.digest(BASE_RESULT.read_bytes()),
            "base_reference_sha256": study.old.digest((BASE_RUN / "reference.jsonl").read_bytes()),
            "reference_path": str(RUN / "reference.jsonl"),
            "reference_sha256": study.old.digest((RUN / "reference.jsonl").read_bytes()),
            "schema_path": str(SCHEMA),
            "schema_sha256": study.old.digest(SCHEMA.read_bytes()),
            "scorer": scorer.VERSION,
            "scorer_sha256": study.old.digest(Path(scorer.__file__).read_bytes()),
            "model": baseline["model"],
            "prompt_version": baseline["prompt_version"],
            "prompt_revision": baseline["prompt_revision"],
            "replay_mode": "saved R8 responses; no model call",
            "repair_policy": "none; predictions unchanged from v0.8 projection",
            "gold_timing_changes": len(audit),
            "gold_changes_by_direction": dict(
                Counter(f"{item['before']}_to_{item['after']}" for item in audit)
            ),
            "finding_v08_1": summary,
            "letters": [
                {"source_row_index": row["source_row_index"], **score}
                for row, score in zip(review_rows, scores, strict=True)
            ],
        },
    )
    print(json.dumps({"timing_changes": len(audit), "score": summary}, indent=2))


if __name__ == "__main__":
    main()
