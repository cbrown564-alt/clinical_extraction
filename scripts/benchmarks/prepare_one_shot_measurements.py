"""Render the v2 candidate using authored fixtures only; no dataset or provider access."""

from __future__ import annotations

import difflib
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements as v2


def main() -> None:
    root = Path("results/letter-benchmarks/gan/one_shot_frequency_v2_no_call")
    root.mkdir(parents=True, exist_ok=True)
    cases = v2.fictional_cases()
    artifacts = {"fictional_fixtures": cases}
    artifacts["paired_examples"] = [
        {
            "name": case["name"],
            "note_text": case["note_text"],
            "rich": case["output"],
            "simple": {"answer": case["output"]["answer"]},
        }
        for case in cases
    ]
    checks = []
    for condition in v2.v1.CONDITIONS:
        artifacts[condition + ".messages"] = v2.messages(cases[0]["note_text"], condition)
        artifacts[condition + ".schema"] = (
            v2.Rich if condition == "rich" else v2.v1.Simple
        ).model_json_schema()
        for case in cases:
            output = case["output"] if condition == "rich" else {"answer": case["output"]["answer"]}
            result = v2.inspect_output(json.dumps(output), case["note_text"], condition)
            assert result["failure"] is None
            assert result["quote_slots"] == result["exact_quotes"]
            checks.append(
                {
                    "case": case["name"],
                    "condition": condition,
                    "failure": None,
                    "quote_slots": result["quote_slots"],
                    "exact_quotes": result["exact_quotes"],
                }
            )
    artifacts["checks"] = {
        "version": v2.VERSION,
        "scope": "fictional no-call preparation only",
        "model_calls": 0,
        "checks": checks,
        "source_sha256": hashlib.sha256(Path(v2.__file__).read_bytes()).hexdigest(),
    }
    for name, value in artifacts.items():
        (root / (name + ".json")).write_text(json.dumps(value, indent=2) + "\n")
    rendered = {
        c: json.dumps(v2.prompt_payload("<NOTE_TEXT>", c), indent=2).splitlines(True)
        for c in v2.v1.CONDITIONS
    }
    (root / "rich_simple.diff").write_text(
        "".join(
            difflib.unified_diff(
                rendered["simple"], rendered["rich"], fromfile="simple-v2", tofile="rich-v2"
            )
        )
    )
    original = v2.v1.historical.llm_extract_encode_select_prompt_template()
    original["note_text"] = "<NOTE_TEXT>"
    (root / "original_v2.diff").write_text(
        "".join(
            difflib.unified_diff(
                json.dumps(original, indent=2).splitlines(True),
                rendered["rich"],
                fromfile="original-one-shot",
                tofile=v2.VERSION,
            )
        )
    )
    print(f"{len(checks)} fictional checks passed; no-call artifacts: {root}")


if __name__ == "__main__":
    main()
