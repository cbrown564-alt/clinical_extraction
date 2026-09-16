"""Render R8, check its fictional fixtures and export the v0.7 annotation package.

No dataset or provider access. Writes the no-call artifacts for R8 and the portable
guide v0.7 package (wrapper JSON Schema generated from the same Finding model).
"""

from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    one_shot_measurements_r7_quarter as r7,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r8 as r8

ROOT = Path("results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r8_no_call")
PACKAGE = Path("results/letter-benchmarks/gan/seizure_finding_annotation_v0_7")
GUIDE = Path("docs/research/gan2026/seizure_finding_annotation_guide.md")
REVIEW = Path("docs/research/gan2026/seizure_finding_annotation_review.md")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    cases = r8.fictional_cases()
    checks = []
    for case in cases:
        record = r8.Rich.model_validate(case["output"])
        quotes = [f.evidence for f in record.findings] + [d.evidence for d in record.document_dates]
        if record.answer.evidence is not None:
            quotes.append(record.answer.evidence)
        assert all(quote in case["note_text"] for quote in quotes), case["name"]
        for finding in record.findings:
            assert finding.event.scope == r8.derive_scope(finding.event.type), case["name"]
        checks.append({"name": case["name"], "valid": True, "findings": len(record.findings)})
    payload = r8.prompt_payload("<NOTE_TEXT>")
    baseline = r7.prompt_payload("<NOTE_TEXT>")
    for key in ("task", "instructions", "label_forms", "cases"):
        assert payload[key] == baseline[key], key
    messages = r8.messages("<NOTE_TEXT>")
    rendered = json.JSONDecoder().raw_decode(
        messages[1]["content"].split("[[ ## prompt_input_json ## ]]")[1].lstrip()
    )[0]
    assert rendered == payload
    for name, value in {
        "rich.messages": messages,
        "rich.schema": r8.Rich.model_json_schema(),
        "fictional_fixtures": cases,
    }.items():
        (ROOT / (name + ".json")).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    old = json.dumps(baseline, indent=2).splitlines(True)
    new = json.dumps(payload, indent=2).splitlines(True)
    (ROOT / "r7_r8.diff").write_text(
        "".join(difflib.unified_diff(old, new, fromfile="r7_quarter", tofile="r8"))
    )
    components = [Path(r8.__file__), Path(r8.r5.__file__), Path(r8.r4.__file__), Path(__file__)]
    verification = {
        "version": r8.VERSION,
        "revision": r8.REVISION,
        "guide_version": r8.GUIDE_VERSION,
        "fixtures": checks,
        "shared_with_r7": ["task", "instructions", "label_forms", "cases"],
        "components": {str(p): sha(p) for p in components},
        "artifacts": {
            p.name: sha(p) for p in sorted(ROOT.glob("*")) if p.name != "verification.json"
        },
        "model_calls": 0,
    }
    (ROOT / "verification.json").write_text(json.dumps(verification, indent=2) + "\n")

    PACKAGE.mkdir(parents=True, exist_ok=True)
    schema = r8.Annotation.model_json_schema()
    schema["description"] = (
        "Seizure-finding annotation v0.7 wrapper generated from the R8 Finding model. "
        "Structural validation only; use scripts/benchmarks/check_annotations_v07.py."
    )
    (PACKAGE / "annotation.schema.json").write_text(json.dumps(schema, indent=2) + "\n")
    manifest = {
        "guide_version": r8.GUIDE_VERSION,
        "canonical_owners": [str(GUIDE), str(REVIEW)],
        "owner_sha256": {str(GUIDE): sha(GUIDE), str(REVIEW): sha(REVIEW)},
        "r8_source_sha256": sha(Path(r8.__file__)),
        "checker": "scripts/benchmarks/check_annotations_v07.py",
        "files": {
            p.name: sha(p) for p in sorted(PACKAGE.glob("*")) if p.name != "handoff_manifest.json"
        },
    }
    (PACKAGE / "handoff_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"fixtures": len(checks), "artifacts": sorted(verification["artifacts"])}))


if __name__ == "__main__":
    main()
