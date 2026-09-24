"""Record selected diary totals where R9 instructions and the reference diverge."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.benchmarks import score_compact_findings_v03 as base

ROOT = Path("runs/one_shot_frequency_v2_measurements_r9/dev750")
OWNER = Path(
    "runs/seizure_finding_annotation_compact_v0_1/dev750/"
    "candidate_v0_3_owner_adjudicated.json"
)
OUTPUT = ROOT / "concepts_v03_policy_candidate/diary_arithmetic_review.jsonl"
CASES = {
    ("4402", "f1"): "same-unit diary months",
    ("4410", "f1"): "same-unit diary months",
    ("5995", "f12"): "two convulsions plus three cluster constituents",
    ("6065", "f2"): "same-subtype diary months; progressions are subsets",
    ("15965", "f2"): "sleep and awake counts across two months",
    ("15982", "f3"): "sleep and awake counts across two months",
    ("15992", "f1"): "awake counts across two months",
    ("16041", "f6"): "sleep and awake counts across two reported months",
}


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    references, _ = base.load_reference()
    refs = {str(row["source_id"]): row for row in references}
    owner = json.loads(OWNER.read_text())
    owners = {str(row["source_id"]): row for row in owner["rows"]}
    predictions = {
        row["source_row_index"]: row
        for row in (json.loads(line) for line in (ROOT / "parsed_predictions.jsonl").open())
    }
    rows = []
    for (source_id, legacy_id), arithmetic in CASES.items():
        ref = refs[source_id]
        index = ref["origin_ids"].index(legacy_id)
        finding = ref["findings"][index]
        claim = next(
            claim for claim in owners[source_id]["claims"] if claim["legacy_id"] == legacy_id
        )
        prediction = predictions[ref["source_row_index"]]
        if prediction["source_sha256"] != ref["source_sha256"]:
            raise ValueError(f"Source mismatch: {source_id}")
        if not all(fragment in ref["note"] for fragment in finding["evidence"]):
            raise ValueError(f"Evidence mismatch: {source_id}")
        rows.append(
            {
                "source_id": source_id,
                "source_row_index": ref["source_row_index"],
                "source_sha256": ref["source_sha256"],
                "origin_id": legacy_id,
                "reference_claim_index": index,
                "arithmetic": arithmetic,
                "reference_event": finding["event"],
                "reference_measurement": finding["measurement"],
                "reference_time": finding["time"],
                "reference_evidence": finding["evidence"],
                "owner_edit_reason": claim.get("edit_reason"),
                "r9_findings": prediction.get("response", {}).get("findings", []),
                "attribution": "prompt_reference_policy_mismatch",
            }
        )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))
    print(f"Wrote {len(rows)} selected source-checked cases to {OUTPUT}")


if __name__ == "__main__":
    main()
