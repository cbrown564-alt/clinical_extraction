"""Export selected source-backed R9/R11 dev750 mechanism comparisons."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.benchmarks import score_compact_findings_v03 as base

OUTPUT = Path("runs/one_shot_frequency_v2_measurements_r11/dev750/source_review_cases.jsonl")
OWNER = Path(
    "runs/seizure_finding_annotation_compact_v0_1/dev750/candidate_v0_3_owner_adjudicated.json"
)
CASES = {
    "1591": "model_improvement_observed_count_not_rate",
    "5995": "model_improvement_mixed_diary_total",
    "6065": "model_improvement_subtype_diary_total",
    "15992": "model_error_population_and_awake_limit",
    "2023": "model_overaggregation_and_reference_policy_question",
    "12584": "model_error_window_carried_to_unwindowed_claims",
    "12679": "model_omission",
    "13574": "model_omission_of_prior_measurements",
    "9103": "model_error_last_event_phase",
}
ROOT9 = Path("runs/one_shot_frequency_v2_measurements_r9/dev750")
ROOT11 = Path("runs/one_shot_frequency_v2_measurements_r11/dev750")


def by_source(path: Path) -> dict[str, dict]:
    return {str(row["source_id"]): row for row in (json.loads(line) for line in path.open())}


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    references, _ = base.load_reference()
    refs = {str(row["source_id"]): row for row in references}
    owners = {str(row["source_id"]): row for row in json.loads(OWNER.read_text())["rows"]}
    r9 = by_source(ROOT9 / "parsed_predictions.jsonl")
    r11 = by_source(ROOT11 / "parsed_predictions.jsonl")
    s9 = by_source(ROOT9 / "calendar_window_v04/per_letter.jsonl")
    s11 = by_source(ROOT11 / "per_letter.jsonl")
    output = []
    for source_id, mechanism in CASES.items():
        ref = refs[source_id]
        for row in (r9[source_id], r11[source_id], s9[source_id], s11[source_id]):
            if row["source_sha256"] != ref["source_sha256"]:
                raise ValueError(f"Source mismatch: {source_id}")
        if not all(
            fragment in ref["note"]
            for finding in ref["findings"]
            for fragment in finding["evidence"]
        ):
            raise ValueError(f"Evidence mismatch: {source_id}")
        owner_reasons = {
            claim["legacy_id"]: claim.get("edit_reason")
            for claim in owners[source_id]["claims"]
            if claim["legacy_id"] in ref["origin_ids"]
        }
        output.append(
            {
                "source_id": source_id,
                "source_row_index": ref["source_row_index"],
                "source_sha256": ref["source_sha256"],
                "mechanism": mechanism,
                "reference_origin_ids": ref["origin_ids"],
                "reference_findings": ref["findings"],
                "owner_edit_reasons": owner_reasons,
                "r9_findings": (r9[source_id].get("response") or {}).get("findings", []),
                "r11_findings": (r11[source_id].get("response") or {}).get("findings", []),
                "r9_score": s9[source_id]["score"],
                "r11_score": s11[source_id]["score"],
            }
        )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in output))
    print(f"Wrote {len(output)} selected source checks")


if __name__ == "__main__":
    main()
