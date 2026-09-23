"""Build a local-only R8 dev750 review bundle from saved responses and frozen scores.

No model calls, repairs, or locked-test reads. The bundle is intentionally written
under ignored runs/ and must never be copied to frontend/public.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.benchmarks.run_r8 import load_reference, records
from scripts.benchmarks.score_finding_purist import R8_OUT, REFERENCE, r8_predictions

OUT = Path("runs/one_shot_frequency_v2_measurements_r8/dev750_rich_only/review_bundle.json")


def main() -> None:
    selected = records("dev750")
    refs = load_reference(REFERENCE, selected)
    predictions = r8_predictions(selected)
    score = json.loads(R8_OUT.read_text())
    score_rows = {r["source_row_index"]: r for r in score["letters"]}
    if len(selected) != 750 or len(score_rows) != 750:
        raise ValueError("Expected 750 score rows")
    diagnostics = {
        r["source_row_index"]: r for r in json.loads((OUT.parent / "diagnostics.json").read_text())
    }
    rows = []
    for record in selected:
        index = record.source_row_index
        ref = refs[index]
        pred = predictions[index]
        scored = score_rows[index]
        pairs = scored["purist_pairs"]
        matched_pred = {p for p, _ in pairs}
        matched_ref = {r for _, r in pairs}
        predicted_findings = pred or []
        reference_findings = ref["findings"]
        if scored["purist_tp"] != len(pairs) or scored["reference"] != len(reference_findings):
            raise ValueError(f"Score mismatch on {index}")
        if pred is not None and scored["predicted"] != len(pred):
            raise ValueError(f"Prediction mismatch on {index}")
        rows.append(
            {
                "source_row_index": index,
                "source_id": ref["source_id"],
                "gold_answer": record.gold_label,
                "predicted_answer": diagnostics[index]["answers"]["r8_rich"],
                "answer_correct": diagnostics[index]["answer_correct"]["r8_rich"]["purist"],
                "note": record.note_text,
                "usable": scored["usable"],
                "exact_tp": scored["exact_tp"],
                "purist_tp": scored["purist_tp"],
                "purist_fp": scored["purist_fp"],
                "purist_fn": scored["purist_fn"],
                "collapsed_tp": scored["collapsed_tp"],
                "pairs": pairs,
                "reference": reference_findings,
                "predicted": predicted_findings,
                "unmatched_reference_ids": [
                    f["id"] for f in reference_findings if f["id"] not in matched_ref
                ],
                "unmatched_prediction_ids": [
                    f["id"] for f in predicted_findings if f["id"] not in matched_pred
                ],
            }
        )
    bundle = {
        "scope": (
            "Gan synthetic dev750; reviewed v0.7 reference; saved R8 rich responses; "
            "no model call or repair; not clinical validation or holdout performance"
        ),
        "matcher": score["finding_purist"]["matching_version"],
        "reference_sha256": score["reference_sha256"],
        "aggregate": score["finding_purist"],
        "exact": score["exact"],
        "pair_classes": score["purist_pair_classes"],
        "rows": rows,
    }
    OUT.write_text(json.dumps(bundle, ensure_ascii=False, separators=(",", ":")))
    print(f"Wrote {OUT}: {len(rows)} letters")


if __name__ == "__main__":
    main()
