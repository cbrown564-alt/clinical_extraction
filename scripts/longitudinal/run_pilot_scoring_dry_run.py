"""Summarize verified authored references and score constant-status baselines.

This does not run an independent annotation pass or measure annotation effort.
No agreement, timing or field-utility result is inferred from authored references.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))  # Allow direct execution from the repository checkout.

from scripts.longitudinal.verify_patient_case import verify_patient_case  # noqa: E402

STATUSES = ("eligible", "ineligible", "indeterminate")


def summarize_pilot(examples_dir: Path) -> dict:
    case_dirs = sorted(examples_dir.glob("authored_patient_*"))
    if len(case_dirs) != 12:
        raise ValueError("Expected exactly 12 pilot cases")
    counts: Counter = Counter()
    breakdown: dict[str, Counter] = defaultdict(Counter)
    pairs = []
    cases = []
    hashes = {}
    baseline_scores: dict[str, list] = {status: [] for status in STATUSES}
    for path in case_dirs:
        verified = verify_patient_case(path)
        reference = json.loads((path / "reference.json").read_text())
        manifest = json.loads((path / "manifest.json").read_text())
        answers = {a["request_id"]: a["status"] for a in reference["answers"]}
        case_counts = Counter(answers.values())
        counts.update(case_counts)
        for req in manifest["requests"]:
            breakdown[req["query_id"]][answers[req["request_id"]]] += 1
        for index in (1, 2):
            for query in range(1, 6):
                visit = answers[f"T{index}_visit_Q{query}"]
                retro = answers[f"T{index}_retrospective_Q{query}"]
                pairs.append(
                    {
                        "case_id": manifest["case_id"],
                        "index": index,
                        "query_id": f"Q{query}",
                        "visit": visit,
                        "retrospective": retro,
                        "differs": visit != retro,
                    }
                )
        for status in STATUSES:
            baseline_scores[status].append(case_counts[status] / len(answers))
        cases.append(
            {
                "case_id": manifest["case_id"],
                **{k: v for k, v in verified.items() if k != "case_dir"},
            }
        )
        for file in sorted(path.rglob("*")):
            if file.is_file() and file.suffix in {".json", ".txt"}:
                hashes[str(file.relative_to(examples_dir))] = hashlib.sha256(
                    file.read_bytes()
                ).hexdigest()
    return {
        "pilot_version": "0.5",
        "task_definition_version": "0.2",
        "dataset": "authored longitudinal pilot",
        "split": "development_only",
        "row_policy": "12 patients; all 20 requests per patient; no exclusions",
        "reference_provenance": "AI-authored references corrected by the authoring assistant",
        "scorer": "exact status match, mean within patient then across patients",
        "model": None,
        "prompt_version": None,
        "replay_mode": "local saved references only",
        "repair_policy": "none during scoring; authored corrections are versioned in case files",
        "program_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "input_sha256": hashes,
        "cases_count": len(cases),
        "total_letters": sum(c["documents"] for c in cases),
        "total_requests": sum(counts.values()),
        "total_evidence_spans": sum(c["evidence_spans"] for c in cases),
        "total_assertions": sum(c["assertions"] for c in cases),
        "total_links": sum(c["links"] for c in cases),
        "overall_status_distribution": {status: counts[status] for status in STATUSES},
        "query_breakdown": {q: {s: v[s] for s in STATUSES} for q, v in sorted(breakdown.items())},
        "dual_perspective_divergence": {
            "total_matched_pairs": len(pairs),
            "divergent_pairs": sum(p["differs"] for p in pairs),
            "pairs": pairs,
        },
        "constant_baselines": {
            status: {
                "patient_averaged_accuracy": sum(scores) / len(scores),
                "patient_scores": scores,
                "interpretation": (
                    "arithmetic baseline on authored development references; "
                    "not extractor performance"
                ),
            }
            for status, scores in baseline_scores.items()
        },
        "independent_pass_status": "not_performed",
        "inter_annotator_agreement": None,
        "effort_analysis": None,
        "field_cost_utility": None,
        "cases": cases,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results/longitudinal/pilot_v0.5/pilot_dry_run_report.json",
    )
    args = parser.parse_args()
    report = summarize_pilot(ROOT / "examples/longitudinal")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Wrote reference summary: {args.output}; independent pass not performed.")
