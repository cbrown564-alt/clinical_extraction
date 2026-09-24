"""Build a source-only Gan 2026 annotation package under the locked guide.

    .venv/bin/python -m scripts.benchmarks.prepare_annotation_package test
    .venv/bin/python -m scripts.benchmarks.prepare_annotation_package train

Writes to ignored ``runs/seizure_frequency/annotation/<name>/``: every letter of
the split (including row_ok=False) in batches of 50, self-contained instructions
taken from the annotation guide, the record schema, the validator and a zip.
No native labels, references, predictions or row-quality flags are exported,
and nothing is printed from the notes.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.one_call.prompts import EXPANDED_SCHEMA
from scripts.benchmarks import annotation_validator

GUIDE = Path("docs/research/gan2026/seizure_frequency_annotation_guide.md")
VALIDATOR = Path("scripts/benchmarks/annotation_validator.py")
ANNOTATION_ROOT = Path("runs/seizure_frequency/annotation")
BATCH_SIZE = 50
SPLITS = {"test": ("test450", 450, "a held-out evaluation"), "train": ("train300", 300, "an evaluation")}

RECORD_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Seizure-frequency annotation of one letter",
    "type": "object",
    "additionalProperties": False,
    "required": ["source_row_index", "source_id", "source_sha256", "findings"],
    "properties": {
        "source_row_index": {"type": "integer", "minimum": 0},
        "source_id": {"type": "string", "minLength": 1},
        "source_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
        "findings": {"type": "array", "items": {"$ref": "#/$defs/finding"}},
        "note": {"$ref": "#/$defs/nonblank"},
    },
    "$defs": EXPANDED_SCHEMA["$defs"],
}

EXAMPLE_NOTE = (
    "Previously she had daily seizures. Since starting lamotrigine she has two focal "
    "impaired-awareness seizures per month. No generalised tonic-clonic seizures since "
    "March 2019."
)
EXAMPLE_RECORD: dict[str, Any] = {
    "source_row_index": 0,
    "source_id": "example",
    "source_sha256": hashlib.sha256(EXAMPLE_NOTE.encode()).hexdigest(),
    "findings": [
        {
            "event": {"scope": "unspecified", "label": "seizures"},
            "counted_unit": "individual_seizure",
            "status": "stated",
            "measurement": {
                "kind": "rate",
                "quantity": {"kind": "number", "value": 1},
                "per": {"kind": "number", "value": 1, "unit": "day"},
            },
            "time": {"phase": "superseded", "source": "Previously"},
            "evidence": ["Previously she had daily seizures."],
        },
        {
            "event": {"scope": "named", "label": "focal impaired-awareness seizures"},
            "counted_unit": "individual_seizure",
            "status": "stated",
            "measurement": {
                "kind": "rate",
                "quantity": {"kind": "number", "value": 2},
                "per": {"kind": "number", "value": 1, "unit": "month"},
            },
            "time": {"phase": "ongoing"},
            "evidence": ["two focal impaired-awareness seizures per month"],
        },
        {
            "event": {"scope": "named", "label": "generalised tonic-clonic seizures"},
            "counted_unit": "not_applicable",
            "status": "stated",
            "measurement": {"kind": "seizure_free", "since": "March 2019"},
            "time": {"phase": "ongoing", "source": "since March 2019"},
            "evidence": ["No generalised tonic-clonic seizures since March 2019."],
        },
    ],
}


def guide_rules() -> str:
    """The guide's annotation rules, from the one-sentence rule up to scoring."""
    text = GUIDE.read_text(encoding="utf-8")
    start, end = text.index("## One-sentence rule"), text.index("## Scoring")
    rules = text[start:end].rstrip() + "\n"
    link = rules[rules.index("The machine-readable shape is") :]
    link = link[: link.index(".\n") + 2]
    return rules.replace(
        link, "The machine-readable shape is `annotation.schema.json` in this package.\n"
    )


START_HERE = """# Seizure-frequency annotation: {name}

You are annotating {count} synthetic clinic letters about epilepsy. For every letter,
record each statement about **how often, how many, how long without, or when
last** the patient's seizures occurred, following the rules below. This is the
reference for a research evaluation, so annotate from the letter text only.

## What you receive

- `sources/batch_01.jsonl` … `batch_{last_batch:02d}.jsonl`: 50 letters each, one JSON object per
  line with `source_row_index`, `source_id`, `source_sha256` and `note`.
- `annotation.schema.json`: the exact shape of each returned record.
- `validate_annotations.py`: checks your output (needs `pip install jsonschema`).

## What you return

For each batch, `annotations/batch_NN.jsonl`: exactly one line per source letter,

```json
{{"source_row_index": 123, "source_id": "123", "source_sha256": "<copied>", "findings": [ ... ]}}
```

Copy the three identity fields unchanged. `findings` may be empty when the letter
has no seizure-frequency statement. Add an optional one-sentence `note` only when
two readings give materially different values and no default settles it; record
the more literal reading as the finding.

Check each batch before returning it:

```bash
python validate_annotations.py annotations/batch_01.jsonl sources/batch_01.jsonl
```

## Working rules

- Read the whole letter before annotating it. Annotate letters independently.
- Use only the letter. Do not use model outputs, earlier annotations, labels or
  any other source, and do not try to infer what an evaluation expects.
- Every `evidence` item must be copied exactly from the letter (the validator
  checks this). Prefer the shortest span that supports the finding.
- Do not skip difficult letters; every letter needs a record.
- These are synthetic letters for {purpose}. Do not share them
  outside this annotation task.

## Worked example

Letter:

> {example_note}

Record:

```json
{example_record}
```

{rules}"""


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows),
        encoding="utf-8",
    )


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(split: str) -> None:
    name, count, purpose = SPLITS[split]
    out = ANNOTATION_ROOT / name
    package = out / "package"
    records = sorted(load_records_for_split(split), key=lambda r: r.source_row_index)
    if len(records) != count or len({r.source_row_index for r in records}) != count:
        raise ValueError(f"Expected {count} unique {split} rows")
    sources = [
        {
            "source_row_index": r.source_row_index,
            "source_id": str(r.source_row_index),
            "source_sha256": hashlib.sha256(r.note_text.encode()).hexdigest(),
            "note": r.note_text,
        }
        for r in records
    ]

    if package.exists():
        shutil.rmtree(package)
    batches = [sources[i : i + BATCH_SIZE] for i in range(0, len(sources), BATCH_SIZE)]
    for number, batch in enumerate(batches, start=1):
        write_jsonl(package / "sources" / f"batch_{number:02d}.jsonl", batch)
    (package / "annotations").mkdir()
    (package / "annotation.schema.json").write_text(
        json.dumps(RECORD_SCHEMA, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    shutil.copyfile(VALIDATOR, package / "validate_annotations.py")
    (package / "START_HERE.md").write_text(
        START_HERE.format(
            name=name,
            count=count,
            last_batch=len(batches),
            purpose=purpose,
            example_note=EXAMPLE_NOTE,
            example_record=json.dumps(EXAMPLE_RECORD, indent=2, ensure_ascii=False),
            rules=guide_rules(),
        ),
        encoding="utf-8",
    )

    # Self-checks: the worked example is valid, and empty records for every letter
    # pass identity and coverage checks while a missing letter is reported.
    annotation_validator.SCHEMA = package / "annotation.schema.json"
    example_source = {**EXAMPLE_RECORD, "note": EXAMPLE_NOTE}
    if annotation_validator.validate([EXAMPLE_RECORD], [example_source]):
        raise ValueError("Worked example fails validation")
    empty = [{k: s[k] for k in annotation_validator.IDENTITY} | {"findings": []} for s in sources]
    if annotation_validator.validate(empty, sources):
        raise ValueError("Identity check failed on the package sources")
    if not annotation_validator.validate(empty[1:], sources):
        raise ValueError("Validator did not report a missing letter")

    files = sorted(p for p in package.rglob("*") if p.is_file())
    manifest = {
        "dataset": "Gan 2026 synthetic",
        "split": name,
        "letters": len(sources),
        "row_policy": f"all {count} {split} rows including row_ok=False; flag not exported",
        "excluded": "native labels, references, predictions, row-quality flags",
        "guide": str(GUIDE),
        "guide_sha256": sha(GUIDE),
        "source_sha256_basis": "sha256 of the cleaned note text given to the models",
        "batches": len(batches),
        "files": {str(p.relative_to(package)): sha(p) for p in files},
    }
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    archive = out / f"seizure_frequency_{name}_annotation.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in files:
            bundle.write(
                path, Path(f"seizure_frequency_{name}_annotation") / path.relative_to(package)
            )
        bundle.writestr(f"seizure_frequency_{name}_annotation/annotations/.keep", "")
    print(f"Wrote {len(sources)} letters in {len(batches)} batches; zip {archive}")
    print(f"zip sha256 {sha(archive)}; guide sha256 {manifest['guide_sha256']}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in SPLITS:
        raise SystemExit(__doc__)
    main(sys.argv[1])
