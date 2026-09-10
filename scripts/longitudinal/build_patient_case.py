"""Rebuild derived inputs and README tables from reviewed pilot case files.

Letters, annotations and reference answers are canonical authored data. This
command does not generate clinical content or infer reference statuses.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))  # Allow direct execution from the repository checkout.

from scripts.longitudinal.check_annotations import load_example  # noqa: E402
from scripts.longitudinal.verify_patient_case import (  # noqa: E402
    input_payload,
    verify_patient_case,
)


def build_case(case_dir: Path) -> None:
    manifest = json.loads((case_dir / "manifest.json").read_text())
    annotations, documents, _ = load_example(case_dir)
    for req in manifest["requests"]:
        payload = input_payload(manifest["case_id"], documents, req["information_cutoff"])
        (case_dir / req["input_path"]).write_text(json.dumps(payload, indent=2) + "\n")
    verify_patient_case(case_dir)
    # Patient 001 retains its hand-written explanatory walkthrough.
    if manifest["case_id"] == "authored-001":
        return
    reference = json.loads((case_dir / "reference.json").read_text())
    answers = {a["request_id"]: a for a in reference["answers"]}
    intro = (case_dir / "README.md").read_text().split("## Requests and Allowed Inputs")[0]
    intro = intro.replace("version 0.1", f"version {manifest['version']}").replace(
        "version 0.2", f"version {manifest['version']}"
    )
    rows = [
        "## Requests and Allowed Inputs",
        "",
        "Indices are fixed 180 days apart; each retrospective cutoff is T + 180 days.",
        "",
        "| Index/view | Index date | Information cutoff | Included letters |",
        "| --- | --- | --- | --- |",
    ]
    for r in manifest["requests"]:
        if r["query_id"] != "Q1":
            continue
        included = ", ".join(
            d["letter_id"]
            for d in documents.values()
            if d["available_date"] <= r["information_cutoff"]
        )
        rows.append(
            f"| {r['request_id'].removesuffix('_Q1')} | {r['index_date']} | "
            f"{r['information_cutoff']} | {included or 'none'} |"
        )
    rows += [
        "",
        "## Expected Answers (20 Queries)",
        "",
        "| Query | T1 visit | T1 retrospective | T2 visit | T2 retrospective |",
        "| --- | --- | --- | --- | --- |",
    ]
    for q in range(1, 6):
        values = [
            answers[f"T{i}_{v}_Q{q}"]["status"] for i in (1, 2) for v in ("visit", "retrospective")
        ]
        rows.append(f"| Q{q} | " + " | ".join(values) + " |")
    rows += [
        "",
        "## Annotation coverage and limits",
        "",
        f"[annotations.json](annotations.json) contains {len(annotations['assertions'])} "
        f"assertions and {len(annotations['links'])} relationships. "
        "Empty clinical letters are explicitly recorded in the manifest.",
        "[reference.json](reference.json) records the evidence and reason for every answer.",
        "",
        "The case manifest records whether this version preserves or revises authored letters.",
        "Versioned changes cover the query schedule, unsupported negatives and treatment plans.",
        "Source paragraphs retain context; they are not minimal evidence spans.",
        "This is an authoring-assistant review, not an independent annotation pass.",
        "Uncertain dates, identity and missing outcomes remain unresolved. No expert",
        "validation, annotation-time measurement or schema-utility experiment is claimed.",
        "",
    ]
    (case_dir / "README.md").write_text(intro + "\n".join(rows))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir", type=Path)
    build_case(parser.parse_args().case_dir)
