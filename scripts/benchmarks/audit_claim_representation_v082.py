"""Source-backed triage of every saved R8 development letter.

Flags are candidates for human adjudication, never automatic reference edits.
No model or locked-test data is read.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_matching_v07 as exact,
)
from scripts.benchmarks.score_finding_components_v081 import score_row, subtype_key

ROOT = Path("runs/seizure_finding_annotation_v0_8_1/dev750_r8_saved")
OUT = Path("runs/seizure_finding_annotation_v0_8_2/dev750_r8_saved")
RESULT = Path(
    "results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_2/dev750_r8_saved/claim_representation_audit.json"
)


def flags(row: dict[str, Any]) -> list[dict[str, Any]]:
    gold = row["reference"]
    result: list[dict[str, Any]] = []

    def add(kind: str, ids: list[str], rationale: str) -> None:
        result.append({"kind": kind, "finding_ids": ids, "rationale": rationale})

    free = [f for f in gold if f["measurement"]["type"] == "seizure_free"]
    if len(free) > 1:
        add(
            "multiple_absence_claims",
            [f["id"] for f in free],
            "Check for one continuous interval versus distinct scopes or windows.",
        )
    for f in gold:
        m = f["measurement"]
        evidence = f["evidence"].lower()
        if (
            m["type"] == "last_seizure"
            and re.search(r"\b(last recalls?|last remembers?|possible|uncertain)\b", evidence)
            and "last seizure" not in evidence
        ):
            add("uncertain_last_event", [f["id"]], "Check whether seizure identity is established.")
        if m["type"] == "cluster" and "cluster" not in f["event"]["type"].lower():
            add("cluster_unit_label", [f["id"]], "Check counted unit while preserving subtype.")
        if m["type"] == "qualitative" and any(
            other is not f
            and other["measurement"]["type"] in {"rate", "count", "cluster"}
            and exact.label_key(other["event"]["type"]) == exact.label_key(f["event"]["type"])
            for other in gold
        ):
            add(
                "qualitative_with_numeric",
                [f["id"]],
                "Check for duplicate frequency level in the same scope/window.",
            )
    for f in row["predicted"]:
        if f["event"].get("seizure_status") == "non_seizure":
            add(
                "predicted_non_seizure",
                [f["id"]],
                "Check whether the symptom is in scope for frequency.",
            )
    return result


def main() -> None:
    references = [json.loads(line) for line in (ROOT / "reference.jsonl").read_text().splitlines()]
    review = json.loads((ROOT / "review_bundle.json").read_text())["rows"]
    if len(references) != len(review) or len(review) != 750:
        raise ValueError("Expected all 750 development letters")
    entries: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    examples: dict[str, list[int]] = defaultdict(list)
    for source, row in zip(references, review, strict=True):
        index = source["source_row_index"]
        if (index, source["source_id"]) != (row["source_row_index"], row["source_id"]):
            raise ValueError(f"Source identity changed at {index}")
        if source["findings"] != row["reference"]:
            raise ValueError(f"Reference differs from review bundle at {index}")
        if len({f["id"] for f in source["findings"]}) != len(source["findings"]):
            raise ValueError(f"Duplicate finding ID at {index}")
        for finding in source["findings"]:
            if finding["evidence"] not in row["note"]:
                raise ValueError(
                    f"Gold evidence is not an exact source quote at {index}:{finding['id']}"
                )
        invalid_prediction_quotes = [
            f["id"] for f in row["predicted"] if f["evidence"] not in row["note"]
        ]
        if invalid_prediction_quotes:
            counts["invalid_prediction_quotes"] += len(invalid_prediction_quotes)
            examples["invalid_prediction_quotes"].append(index)
        aligned = score_row(row)
        pairs = []
        for pair in aligned["pairs"]:
            p = next(f for f in row["predicted"] if f["id"] == pair["prediction_id"])
            g = next(f for f in row["reference"] if f["id"] == pair["gold_id"])
            mismatches = [
                name for name in ("measurement", "subtype", "event") if not pair[f"{name}_correct"]
            ]
            if p.get("timing") != g.get("timing"):
                mismatches.append("timing")
            if p["event"].get("seizure_status") != g["event"].get("seizure_status"):
                mismatches.append("seizure_status")
            for name in mismatches:
                counts[f"aligned_{name}_mismatch"] += 1
                examples[f"aligned_{name}_mismatch"].append(index)
            pairs.append(
                {
                    "gold_id": g["id"],
                    "prediction_id": p["id"],
                    "gold_event": g["event"]["type"],
                    "prediction_event": p["event"]["type"],
                    "gold_subtype": subtype_key(g),
                    "prediction_subtype": subtype_key(p),
                    "gold_measurement": g["measurement"],
                    "prediction_measurement": p["measurement"],
                    "gold_evidence": g["evidence"],
                    "prediction_evidence": p["evidence"],
                    "mismatches": mismatches,
                }
            )
        row_flags = flags(row)
        for flag in row_flags:
            counts[flag["kind"]] += 1
            examples[flag["kind"]].append(index)
        counts["letters"] += 1
        counts["gold_findings"] += len(row["reference"])
        counts["predicted_findings"] += len(row["predicted"])
        counts["unpaired_gold"] += len(aligned["unpaired_gold"])
        counts["unpaired_predictions"] += len(aligned["unpaired_predictions"])
        if aligned["unpaired_gold"] and aligned["unpaired_predictions"]:
            counts["letters_with_both_unpaired"] += 1
        entries.append(
            {
                "source_row_index": index,
                "source_id": source["source_id"],
                "source_sha256": source["source_sha256"],
                "usable": row["usable"],
                "whole_finding": {key: row[f"v08_{key}"] for key in ("tp", "fp", "fn")},
                "aligned_pairs": pairs,
                "unpaired_gold": [
                    f for f in row["reference"] if f["id"] in aligned["unpaired_gold"]
                ],
                "unpaired_predictions": [
                    f for f in row["predicted"] if f["id"] in aligned["unpaired_predictions"]
                ],
                "invalid_prediction_quotes": invalid_prediction_quotes,
                "rule_review_flags": row_flags,
            }
        )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "claim_representation_audit.jsonl").write_text(
        "".join(json.dumps(entry, ensure_ascii=False) + "\n" for entry in entries)
    )
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(
            {
                "scope": "Gan 2026 synthetic dev750; saved R8 projection against v0.8.1 gold",
                "method": (
                    "exact source validation and deterministic source-overlap alignment; "
                    "flags require adjudication"
                ),
                "counts": dict(sorted(counts.items())),
                "flagged_source_rows": {
                    key: sorted(set(indices)) for key, indices in sorted(examples.items())
                },
                "per_letter_audit": str(OUT / "claim_representation_audit.jsonl"),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
    print(json.dumps(dict(sorted(counts.items())), indent=2))


if __name__ == "__main__":
    main()
