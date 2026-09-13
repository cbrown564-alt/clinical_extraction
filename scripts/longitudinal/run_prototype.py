"""Rebuild the Phase 4 comparison and browser inputs without model calls.

Run from the repository root with its .venv. Sources are synthetic development
records and saved independent-pass captures; no benchmark data is opened.
"""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.longitudinal import PROGRAM_VERSION
from clinical_extraction.longitudinal.evaluation import link_comparison, summarize
from clinical_extraction.longitudinal.evidence import digest, load_case
from clinical_extraction.longitudinal.pipeline import run_frame, saved_extraction

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/longitudinal/prototype_v0.1"


def write(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    rows, comparisons, patients, failures = [], [], [], []
    source_hashes = {}
    for dataset, directory in (
        ("authored", ROOT / "examples/longitudinal"),
        ("generated", ROOT / "results/longitudinal/generation_v0.1/cases"),
    ):
        for case in sorted(directory.iterdir()):
            if not (case / "manifest.json").is_file():
                continue
            manifest, documents, annotations = load_case(case)
            for name in ("manifest.json", "annotations.json", "reference.json"):
                source_hashes[str((case / name).relative_to(ROOT))] = digest(case / name)
            refs = {r["request_id"]: r for r in json.loads((case / "reference.json").read_text())["answers"]}
            if dataset == "authored":
                patients.append({"id": case.name, "case_id": manifest["case_id"],
                                 "label": f"Patient {case.name[-3:]}",
                                 "origin": manifest["origin"]})
            for frame in ("T1_visit", "T1_retrospective", "T2_visit", "T2_retrospective"):
                requests = [r for r in manifest["requests"] if r["request_id"].startswith(frame + "_")]
                cutoff = requests[0]["information_cutoff"]
                permitted = {k: d for k, d in documents.items() if d["available_date"] <= cutoff}
                frames = {}
                for variant in ("reference_links", "inferred_links", "no_links"):
                    frames[variant] = run_frame(
                        permitted, annotations, requests,
                        {"mode": "provisional_reference_facts", "expert_review": False},
                        use_reference_links=variant == "reference_links", without_links=variant == "no_links",
                    )
                comparisons.append({"patient": case.name, "frame": frame, "variant": "reference_facts",
                    **link_comparison(frames["inferred_links"]["annotations"],
                                      frames["reference_links"]["annotations"], use_ids=True)})
                if dataset == "authored":
                    extraction = saved_extraction(ROOT, case.name, frame, permitted, manifest["case_id"])
                    if extraction["status"] == "ready":
                        predicted = run_frame(permitted, extraction["annotations"], requests,
                                              extraction["provenance"])
                        predicted["offset_repairs"] = extraction["offset_repairs"]
                        predicted["raw_extraction"] = extraction["raw"]
                        comparisons.append({"patient": case.name, "frame": frame, "variant": "predicted_facts",
                            **link_comparison(predicted["annotations"], frames["reference_links"]["annotations"])})
                    else:
                        predicted = {**extraction, "program_version": PROGRAM_VERSION,
                                     "documents": list(permitted.values()), "requests": requests,
                                     "answers": [{"request_id": r["request_id"], "query_id": r["query_id"],
                                                  "status": "failed", "error": extraction["error"],
                                                  "evidence": [], "rule_ids": []} for r in requests]}
                        failures.append({"patient": case.name, "frame": frame, **extraction})
                    frames["predicted_facts"] = predicted
                    for mode, result in (("reference", frames["inferred_links"]), ("predicted", predicted)):
                        write(OUT / "frames" / case.name / f"{frame}.{mode}.json", result)
                for variant, result in frames.items():
                    for answer in result["answers"]:
                        rid = answer["request_id"]
                        expected = refs[rid]["status"]
                        link_answer = next(a for a in frames["inferred_links"]["answers"] if a["request_id"] == rid)
                        first_failure = (None if answer["status"] == expected else
                            "extraction_or_format" if answer["status"] == "failed" else
                            "predicted_input_or_linking" if variant == "predicted_facts" and link_answer["status"] == expected
                            else "linking" if variant in ("inferred_links", "predicted_facts", "no_links")
                            else "query_policy")
                        rows.append({"patient": case.name, "dataset": dataset, "variant": variant,
                                     "view": requests[0]["view"], "frame": frame,
                                     "reference_status": expected, "first_failing_condition": first_failure,
                                     **answer})
    source_hashes.update({str(p.relative_to(ROOT)): digest(p) for p in (
        *sorted((ROOT / "src/clinical_extraction/longitudinal").glob("*.py")),
        Path(__file__), ROOT / "docs/longitudinal/evaluation_protocol.md",
        ROOT / "docs/longitudinal/annotation.schema.json")})
    write(OUT / "patients.json", {"program_version": PROGRAM_VERSION, "patients": patients})
    write(OUT / "comparison.json", rows)
    write(OUT / "link_alignment.json", comparisons)
    write(OUT / "failures.json", failures)
    summary = {"program_version": PROGRAM_VERSION, "scope": "synthetic development; provisional references",
               "model_calls": 0, "scorer": "exact three-state status agreement; failed capture counts wrong",
               "row_policy": "all fixed requests; no exclusions", "repair_policy": "unique exact quote offsets only",
               "source_sha256": source_hashes, "query_comparison": summarize(rows),
               "link_comparison": {variant: {
                   key: sum(c[key] for c in comparisons if c["variant"] == variant)
                   for key in ("matched_edges", "reference_supported_edges", "reference_recalled_edges", "reference_edges", "aligned_predicted_edges", "predicted_edges",
                               "unaligned_predicted_edges", "aligned_assertions", "predicted_assertions",
                               "reference_assertions")}
                   for variant in ("reference_facts", "predicted_facts")}}
    rule_ids = sorted({rule for row in rows for rule in row["rule_ids"]})
    write(OUT / "rule_catalog.json", {
        "format_normalization": {"rule": "exact-offset", "owner": "evidence.py",
            "meaning": "Unique exact-quotation offset repair; clinical fields unchanged"},
        "evidence_selection": {"owner": "evidence.py", "meaning": "Grounded source paragraph for explicit link context"},
        "semantic_linking": {"owner": "history.py", "meaning": "Identity, correction, conflict, study and medication links"},
        "semantic_query_policy": {"owner": "queries.py and temporal.py", "rule_ids": rule_ids,
            "meaning": "Clinical selection, scope, date inclusion and negative coverage; no treatment causality"},
        "semantic_extraction_repair": False,
    })
    write(OUT / "summary.json", summary)
    print(json.dumps({"queries": summary["query_comparison"]["variant"],
                      "links": summary["link_comparison"]}, indent=2))


if __name__ == "__main__":
    main()
