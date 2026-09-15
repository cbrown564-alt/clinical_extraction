"""Refresh the guide export and handoff file hashes from the canonical annotation owners.

Run from any directory using the repository's Python. Does not read dataset files.
The pinned JSON Schema is not regenerated: schema changes require explicit review.
"""

import hashlib
import json
from pathlib import Path

folder = Path(__file__).resolve().parent
root = folder.parents[3]
owners = [
    root / "docs/research/gan2026/seizure_finding_annotation_guide.md",
    root / "docs/research/gan2026/seizure_finding_annotation_review.md",
]
original = "\n\n".join(path.read_text().strip() for path in owners)
section = original.replace(
    "../../../results/letter-benchmarks/gan/seizure_finding_annotation_v0_1/worked_examples.md",
    "worked_examples.md",
).replace(
    "[final R7 decision](one_shot_schema_decisions.md#final-r7-schema-decision-2026-09-14)",
    "supplied annotation.schema.json (R7 finding fields)",
)
# The portable artifact joins both owners; internal references remain local.
section = section.replace("seizure_finding_annotation_guide.md", "annotation_guide.md")
section = section.replace("seizure_finding_annotation_review.md", "annotation_guide.md")
section = section.replace(
    "one_shot_paper_protocol.md", "../../../../docs/research/gan2026/one_shot_paper_protocol.md"
)
section = section.replace(
    "one_shot_execution_record.md",
    "../../../../docs/research/gan2026/one_shot_execution_record.md",
)
header = (
    "<!-- Generated from annotation guide/review owners; "
    "edit those documents and regenerate. -->\n\n"
)
(folder / "annotation_guide.md").write_text(header + section + "\n")
manifest = {
    "guide_version": "seizure_finding_annotation_v0.6",
    "status": "instruction package; no dev750 sources or annotation run included",
    "canonical_owners": [str(path.relative_to(root)) for path in owners],
    "canonical_section_sha256": hashlib.sha256(original.encode()).hexdigest(),
    "r7_source_sha256": hashlib.sha256(
        (
            root / "src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/"
            "one_shot_measurements_r7_quarter.py"
        ).read_bytes()
    ).hexdigest(),
    "files": {
        name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
        for name in [
            "annotation_guide.md",
            "annotation.schema.json",
            "worked_examples.md",
            "check_annotations.py",
            "export_guide.py",
            "verify_handoff.py",
            "build_review_groups.py",
            "verify_review_groups.py",
            "review_searches.json",
            "expand_group_review.py",
            "verify_group_decisions.py",
        ]
    },
}
(folder / "handoff_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print("Guide export and handoff hashes refreshed; no source data read.")
