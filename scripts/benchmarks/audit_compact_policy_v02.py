"""Export selected source-first R9 compact policy decisions with exact evidence.

The listed decisions are a deliberately selected mechanism audit, not an
exhaustive adjudication of the flagged development reference claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.benchmarks import score_compact_findings_v03 as base

OUTPUT = Path(
    "runs/one_shot_frequency_v2_measurements_r9/dev750/"
    "concepts_v02_source_audit/source_review_comparison.jsonl"
)
PREDICTIONS = Path("runs/one_shot_frequency_v2_measurements_r9/dev750/parsed_predictions.jsonl")
V1_PAIRS = Path(
    "runs/one_shot_frequency_v2_measurements_r9/dev750/"
    "concepts_v01_final_candidate/per_letter.jsonl"
)
V2_PAIRS = Path(
    "runs/one_shot_frequency_v2_measurements_r9/dev750/"
    "concepts_v02_source_audit/per_letter.jsonl"
)

# source ID, zero-based reference claim, decision, source-backed reason.
CASES = [
    ("2374", 2, "duplicate", "Morning already names the myoclonic population."),
    ("2513", 1, "distinct_event", "Jerks and staring spells are separately measured."),
    ("2513", 2, "distinct_event", "Staring spells are not the same population as jerks."),
    ("3356", 0, "material_condition", "No events only when sleep has been adequate."),
    ("3371", 0, "material_condition", "No events outside nights with curtailed rest."),
    ("3468", 0, "material_condition", "Seizures are stated to occur only perimenstrually."),
    ("3469", 0, "material_condition", "The zero applies outside a named cycle window."),
    ("3482", 0, "material_condition", "The zero applies outside a named cycle window."),
    ("3846", 0, "material_condition", "The two-per-day rate is measured on the hot line."),
    ("3846", 2, "event_context", "Two convulsions occurred there; the place is not a denominator."),
    ("4026", 2, "optional_descriptor", "Brief does not change the absence population."),
    ("4116", 1, "material_condition", "The recurring rate is stated for workdays."),
    ("4597", 2, "material_condition", "No jerks is stated only for mornings."),
    ("467", 0, "model_type_error", "R9 drops preserved-to-impaired focal progression."),
    ("5092", 0, "open", "Observed clinical absence may be broader than the source warrants."),
    ("5210", 1, "material_condition", "No events is limited to specified light exposures."),
    ("6029", 0, "event_context", "Night shift describes the last event's trigger."),
    ("6094", 0, "model_scope_error", "R9 turns unclassified nocturnal events into all seizures."),
    ("6077", 2, "open", "Day-to-day zero coexists with a recent flight event."),
    ("6319", 0, "model_scope_error", "R9 turns unclassified events into all seizures."),
    ("6131", 2, "material_condition", "Unprovoked absence does not include provoked seizures."),
    ("6131", 3, "material_condition", "No myoclonic jerks is limited to waking."),
    ("6180", 1, "explicit_alias", "The note calls the limb-jerking collapses convulsive events."),
    ("6321", 0, "material_condition", "Uncommon spells are stated when meals are regular."),
    ("7859", 0, "duplicate", "Turns already exclude the separately described prodrome."),
    ("8805", 0, "material_observation", "Device absence is corroborated by a personal log."),
    ("8938", 0, "event_context", "Off ASM describes treatment state, not event count."),
    ("8949", 0, "event_context", "Drug-free describes treatment state, not event count."),
    ("9103", 1, "duplicate", "During sleep already names the counted population."),
    ("9215", 0, "material_observation", "Zero is limited to reported or recognised events."),
    ("9250", 0, "material_condition", "Clear-cut events exclude ongoing warning features."),
    ("9815", 1, "duplicate", "Electrographic already names the EEG-observed population."),
    ("12403", 2, "optional_descriptor", "The cluster measurement supplies the counted unit."),
    ("13721", 1, "material_condition", "No clusters is limited to those needing emergency care."),
    ("14187", 2, "material_condition", "No jerks is limited to waking; R9 omitted that limit."),
    ("15992", 0, "model_aggregation_error", "R9 emits four and three, not the stated seven total."),
    ("16408", 1, "material_condition", "Daily rate occurs only during occasional escalation."),
    ("16574", 1, "material_condition", "Daily rate is reported only for brief periods."),
    ("17110", 0, "optional_descriptor", "Both word orders name absence clusters."),
]


def main() -> None:
    references, _ = base.load_reference()
    by_source = {str(row["source_id"]): row for row in references}
    if len(by_source) != len(references):
        raise ValueError("Duplicate source ID")
    predictions = {
        row["source_row_index"]: row
        for row in (json.loads(line) for line in PREDICTIONS.read_text().splitlines())
    }
    v1 = {
        row["source_row_index"]: row["score"]
        for row in (json.loads(line) for line in V1_PAIRS.read_text().splitlines())
    }
    v2 = {
        row["source_row_index"]: row["score"]
        for row in (json.loads(line) for line in V2_PAIRS.read_text().splitlines())
    }
    rows = []
    for source_id, index, decision, reason in CASES:
        ref = by_source[source_id]
        finding = ref["findings"][index]
        if not all(fragment in ref["note"] for fragment in finding["evidence"]):
            raise ValueError(f"Evidence mismatch for {source_id}#{index}")
        row_index = ref["source_row_index"]
        if predictions[row_index]["source_sha256"] != ref["source_sha256"]:
            raise ValueError(f"Prediction source mismatch for {source_id}")
        aligned = next(
            (
                pair for pair in v2[row_index]["source_aligned_pairs"]
                if pair["reference_index"] == index
            ),
            None,
        )
        predicted = (
            predictions[row_index]["response"]["findings"][aligned["prediction_index"]]
            if aligned is not None
            else None
        )
        rows.append(
            {
                "source_id": source_id,
                "source_row_index": ref["source_row_index"],
                "source_sha256": ref["source_sha256"],
                "reference_claim_index": index,
                "origin_id": ref["origin_ids"][index],
                "decision": decision,
                "reason": reason,
                "reference_event": finding["event"],
                "reference_measurement": finding["measurement"],
                "reference_restriction": finding.get("restriction"),
                "exact_evidence": finding["evidence"],
                "source_aligned_prediction_index_v2": (
                    aligned["prediction_index"] if aligned is not None else None
                ),
                "prediction": predicted,
                "v1_whole_claim_matched": any(pair[1] == index for pair in v1[row_index]["pairs"]),
                "v2_whole_claim_matched": any(pair[1] == index for pair in v2[row_index]["pairs"]),
                "v2_component_agreement": aligned["components"] if aligned is not None else None,
            }
        )
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))
    print(f"Wrote {len(rows)} source-reviewed cases to {OUTPUT}")


if __name__ == "__main__":
    main()
