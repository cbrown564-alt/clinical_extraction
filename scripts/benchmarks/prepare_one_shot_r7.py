"""Render final R7 and check fictional examples only; no dataset or provider access."""

from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r5 as r5
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r7 as r7

ROOT = Path("results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r7_no_call")


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    cases = r7.fictional_cases()
    checks = []
    for case in cases:
        record = r7.Rich.model_validate(case["output"])
        assert record.output() == case["output"]
        quotes = [f.evidence for f in record.findings]
        quotes += [d.evidence for d in record.document_dates]
        if record.answer.evidence is not None:
            quotes.append(record.answer.evidence)
        assert all(quote in case["note_text"] for quote in quotes)
        checks.append({"name": case["name"], "valid": True, "exact_quotes": len(quotes)})
    payload = r7.prompt_payload("<NOTE_TEXT>")
    for key in ("task", "instructions", "label_forms", "cases"):
        assert payload[key] == r5.prompt_payload("<NOTE_TEXT>")[key]
    messages = r7.messages("<NOTE_TEXT>")
    # Inspect the actual model input rather than only the payload builder.
    rendered = json.JSONDecoder().raw_decode(
        messages[1]["content"].split("[[ ## prompt_input_json ## ]]")[1].lstrip()
    )[0]
    assert rendered == payload
    example = r7.complete_example()
    for name, value in {
        "rich.messages": messages,
        "rich.schema": r7.Rich.model_json_schema(),
        "fictional_fixtures": cases,
        "complete_example": example,
    }.items():
        (ROOT / (name + ".json")).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    old = json.dumps(r5.prompt_payload("<NOTE_TEXT>"), indent=2).splitlines(True)
    new = json.dumps(payload, indent=2).splitlines(True)
    (ROOT / "r5_r7.diff").write_text(
        "".join(difflib.unified_diff(old, new, fromfile="r5", tofile="r7"))
    )
    # The display matches the approved design example: omit placeholder answer/links.
    display = {k: v for k, v in example["output"].items() if k not in ("answer", "selected_ids")}
    (ROOT / "complete_example.md").write_text(
        "# R7 fictional design example\n\n"
        "This example illustrates representation, not benchmark performance. The full JSON "
        "fixture includes a placeholder unknown answer and selected_ids solely for schema "
        "checks; they are omitted from this design view.\n\n"
        + "\n\n".join("> " + line for line in example["note_text"].splitlines() if line)
        + "\n\n```json\n"
        + json.dumps(display, ensure_ascii=False, indent=2)
        + "\n```\n\n"
        "The dated cluster is part of the period total, not an additional cluster. "
        "The schema does not encode that overlap as a link. Relative references such as "
        "that date remain unresolved, with their antecedent preserved in evidence. "
        "Missing years are not filled in. Approximate defaults to false, range endpoints "
        "default to inclusive, and absent optional fields are omitted.\n"
    )
    paths = [Path(r7.__file__), Path(r5.__file__), Path(r7.r4.__file__), Path(__file__)]
    artifacts = [
        ROOT / name
        for name in (
            "rich.messages.json",
            "rich.schema.json",
            "fictional_fixtures.json",
            "complete_example.json",
            "complete_example.md",
            "r5_r7.diff",
        )
    ]
    verification = {
        "version": r7.VERSION,
        "revision": r7.REVISION,
        "scope": "fictional no-call representation checks only; not an evaluation freeze",
        "model_calls": 0,
        "dataset_rows_loaded": 0,
        "repair": "none",
        "scorer": "none; native task instructions/cases/label forms unchanged",
        "checks": checks,
        "rendered_payload_identical": True,
        "sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths + artifacts},
    }
    (ROOT / "verification.json").write_text(json.dumps(verification, indent=2) + "\n")
    print(f"{len(checks)} fictional cases verified; model-facing input inspected; {ROOT}")


if __name__ == "__main__":
    main()
