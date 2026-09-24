"""Parse saved first R9 responses and score compact claims plus native answers."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r9 as r9
from scripts.benchmarks import run_r9_dev750 as runner
from scripts.benchmarks import score_compact_findings_v03 as compact


def main() -> None:
    selected = runner.jobs()
    saved = {
        row["request_id"]: row for row in study.old.read_lines(runner.ROOT / "responses.jsonl")
    }
    if len(saved) != len(selected):
        raise ValueError(f"Only {len(saved)}/{len(selected)} saved responses; wait for run")
    reference, _ = compact.load_reference()
    by_index = {row["source_row_index"]: row for row in reference}
    predictions: list[dict[str, Any]] = []
    native: dict[str, Counter[str]] = {method: Counter() for method in ("purist", "pragmatic")}
    failures: Counter[str] = Counter()
    for job in selected:
        record = job["record"]
        raw = saved[job["request_id"]]
        content, finish = study.old.response_content(raw.get("response"))
        parsed = None
        reason = raw.get("error")
        if not reason:
            if finish == "length":
                reason = "truncation"
            else:
                match = study.previous.ENVELOPE.fullmatch(content or "")
                if not match or "[[ ##" in match[1]:
                    reason = "invalid_envelope" if content else "no_response"
                else:
                    try:
                        parsed = json.loads(match[1], object_pairs_hook=study.r4.v1._unique_object)
                    except (ValueError, TypeError):
                        reason = "invalid_syntax"
        if reason:
            failures[reason] += 1
        answer = parsed.get("answer") if isinstance(parsed, dict) else None
        projected = (
            {"label": answer.get("label"), "evidence": answer.get("evidence")}
            if isinstance(answer, dict)
            else None
        )
        checked = study.r4.v1.inspect_output(
            json.dumps({"answer": projected}) if projected else None,
            record.note_text,
            "simple",
        )
        for method in native:
            native[method]["n"] += 1
            gold = study.old.gold_categories(record.raw)[method]
            if checked["failure"] is None and checked["categories"][method] == gold:
                native[method]["answer_correct"] += 1
        ref = by_index[record.source_row_index]
        predictions.append(
            {
                "source_id": ref["source_id"],
                "source_row_index": ref["source_row_index"],
                "source_sha256": ref["source_sha256"],
                "response": parsed,
            }
        )
    out = runner.ROOT
    compact.write_jsonl(out / "parsed_predictions.jsonl", predictions)
    compact.write_json(
        out / "run_metadata.json",
        {
            "model": study.old.MODEL,
            "prompt_version": r9.VERSION,
            "prompt_revision": r9.REVISION,
            "replay_mode": "saved first responses",
            "repair_policy": "none",
            "transport_failures": dict(failures),
            "native_answers": {method: dict(counts) for method, counts in native.items()},
            "charge_upper_usd": study.old.charged(study.old.read_lines(out / "attempts.jsonl")),
        },
    )
    score_dir = Path("results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r9/dev750")
    schema = json.loads(r9.SCHEMA_PATH.read_text())
    summary, local = compact.score_saved(reference, out / "parsed_predictions.jsonl", schema)
    score_dir.mkdir(parents=True, exist_ok=True)
    compact.write_json(score_dir / "score.json", summary)
    compact.write_jsonl(out / "per_letter.jsonl", local)
    compact.write_json(
        score_dir / "run_metadata.json", json.loads((out / "run_metadata.json").read_text())
    )
    print(
        json.dumps(
            {
                "native": {k: dict(v) for k, v in native.items()},
                "transport_failures": dict(failures),
                "compact": summary,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
