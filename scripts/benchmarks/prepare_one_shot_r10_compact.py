"""Render the compact R10 candidate and check source-backed fictional responses.

No provider, dataset or scorer access.
"""

from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    one_shot_measurements_r10 as r10,
)

ROOT = Path("results/letter-benchmarks/gan/one_shot_frequency_r10_compact_v01_no_call")
FIXTURES = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_compact_scope_candidate_no_call/"
    "fictional_fixtures.json"
)
V03_FIXTURES = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_r9_compact_v03_no_call/"
    "v03_fictional_fixtures.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_response(note: str, response: dict[str, Any], schema: dict[str, Any]) -> None:
    Draft202012Validator(schema).validate(response)
    answer = response["answer"]
    findings = response["findings"]
    assert all(i < len(findings) for i in answer["claim_indices"])
    if answer["label"] == "no seizure frequency reference":
        assert answer["evidence"] is None and not answer["claim_indices"] and not findings
    else:
        assert answer["evidence"] and answer["evidence"] in note
    for finding in findings:
        assert all(quote in note for quote in finding["evidence"])


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    payload = r10.prompt_payload("<NOTE_TEXT>")
    schema = payload["output_schema"]
    Draft202012Validator.check_schema(schema)
    cases = json.loads(FIXTURES.read_text()) + json.loads(V03_FIXTURES.read_text())
    for case in cases:
        check_response(case["note"], case["response"], schema)

    messages = r10.messages("<NOTE_TEXT>")
    rendered = json.JSONDecoder().raw_decode(
        messages[1]["content"].split("[[ ## prompt_input_json ## ]]")[1].lstrip()
    )[0]
    assert rendered == payload
    old = json.dumps(r10.r8.prompt_payload("<NOTE_TEXT>"), indent=2).splitlines(True)
    new = json.dumps(payload, indent=2).splitlines(True)
    artifacts = {
        "rich.messages.json": messages,
        "rich.schema.json": schema,
        "fictional_checks.json": [case["case"] for case in cases],
    }
    for name, value in artifacts.items():
        (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    (ROOT / "r8_r10.diff").write_text(
        "".join(difflib.unified_diff(old, new, fromfile="r8", tofile="r10_compact_v01"))
    )
    verification = {
        "version": r10.VERSION,
        "revision": r10.REVISION,
        "guide_version": r10.GUIDE_VERSION,
        "fixture_count": len(cases),
        "model_calls": 0,
        "components": {
            str(path): sha(path)
            for path in (
                Path(r10.__file__), r10.SCHEMA_PATH, FIXTURES, V03_FIXTURES, Path(__file__)
            )
        },
        "artifacts": {
            path.name: sha(path)
            for path in sorted(ROOT.iterdir())
            if path.name != "verification.json"
        },
    }
    (ROOT / "verification.json").write_text(json.dumps(verification, indent=2) + "\n")
    print(json.dumps({"fixtures": len(cases), "artifacts": sorted(verification["artifacts"])}))


if __name__ == "__main__":
    main()
