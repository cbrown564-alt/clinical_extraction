"""Export focused source checks for the remaining compact policy choices."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.benchmarks import score_compact_findings_v03 as base

ROOT = Path("runs/one_shot_frequency_v2_measurements_r9/dev750")
OUTPUT = ROOT / "concepts_v03_policy_candidate/source_review_cases.jsonl"
CASES = [
    (
        "2023",
        2,
        "context",
        "Workday/meal association is non-exclusive; the occasional cluster level is general.",
    ),
    (
        "4592",
        2,
        "context",
        "Restricted sleep offshore is an association, not an exclusive denominator.",
    ),
    ("6321", 0, "scored_condition", "Uncommon spells is expressly conditional on regular meals."),
    ("10996", 1, "scored_condition", "Convulsion is conditional on a prolonged cluster."),
    (
        "7168",
        2,
        "scored_condition",
        "The qualitative claim is the recurring premenstrual cluster pattern.",
    ),
    (
        "5092",
        0,
        "scored_observation",
        "The owner-retained absence is of observed clinical seizures.",
    ),
    (
        "6077",
        2,
        "owner_provisional",
        "The owner retained literal day-to-day absence, unresolved against the flight event.",
    ),
    (
        "17146",
        2,
        "literal_combined",
        "The model marked a source-combined population as named; preserve scope.",
    ),
    (
        "17189",
        2,
        "literal_combined",
        "The one model combined output repeats the source's mixed label.",
    ),
]


def load_rows(path: Path) -> dict[int, dict]:
    rows = (json.loads(line) for line in path.read_text().splitlines())
    return {row["source_row_index"]: row for row in rows}


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    references, _ = base.load_reference()
    by_id = {str(row["source_id"]): row for row in references}
    predictions = load_rows(ROOT / "parsed_predictions.jsonl")
    scores = load_rows(ROOT / "concepts_v03_policy_candidate/per_letter.jsonl")
    owner_rows = json.loads(
        Path(
            "runs/seizure_finding_annotation_compact_v0_1/dev750/"
            "candidate_v0_3_owner_adjudicated.json"
        ).read_text()
    )
    owner_by_id = {str(row["source_id"]): row for row in owner_rows["rows"]}
    output = []
    for source_id, index, decision, reason in CASES:
        ref = by_id[source_id]
        finding = ref["findings"][index]
        row_index = ref["source_row_index"]
        if predictions[row_index]["source_sha256"] != ref["source_sha256"]:
            raise ValueError(f"Source mismatch: {source_id}")
        if not all(fragment in ref["note"] for fragment in finding["evidence"]):
            raise ValueError(f"Evidence mismatch: {source_id}#{index}")
        score = scores[row_index]["score"]
        pair = next(
            (x for x in score["source_aligned_pairs"] if x["reference_index"] == index),
            None,
        )
        prediction = (
            predictions[row_index]["response"]["findings"][pair["prediction_index"]]
            if pair is not None
            else None
        )
        origin = ref["origin_ids"][index]
        owner_claim = next(
            (x for x in owner_by_id[source_id]["claims"] if x["legacy_id"] == origin),
            None,
        )
        output.append(
            {
                "source_id": source_id,
                "source_row_index": row_index,
                "source_sha256": ref["source_sha256"],
                "origin_id": origin,
                "reference_claim_index": index,
                "decision": decision,
                "reason": reason,
                "reference": finding,
                "owner_edit_reason": owner_claim.get("edit_reason") if owner_claim else None,
                "owner_source_adjudication": (
                    owner_claim.get("source_adjudication") if owner_claim else None
                ),
                "source_aligned_prediction": prediction,
                "v03_component_agreement": pair["components"] if pair else None,
                "v03_whole_claim_matched": any(j == index for _, j in score["pairs"]),
            }
        )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in output))
    print(f"Wrote {len(output)} source checks to {OUTPUT}")


if __name__ == "__main__":
    main()
