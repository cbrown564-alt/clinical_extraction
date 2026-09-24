"""Parse and score saved R11 first responses for the pilot or full dev750."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    compact_scored_terms_v03 as terms,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_compact_v08 as scorer,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    one_shot_measurements_r11 as r11,
)
from scripts.benchmarks import run_r11_dev750 as runner
from scripts.benchmarks import score_compact_findings_v03 as compact


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    root = runner.PILOT_ROOT if args.pilot else runner.ROOT
    result = Path("results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r11") / (
        "dev750_pilot16" if args.pilot else "dev750"
    )
    if (root / "parsed_predictions.jsonl").exists() or result.exists():
        raise FileExistsError("Saved R11 replay exists")
    jobs = runner.jobs()
    references, manifest = compact.load_reference()
    by_index = {row["source_row_index"]: row for row in references}
    if args.pilot:
        source_ids = set(runner.PILOT_IDS)
        jobs = [
            job
            for job in jobs
            if str(by_index[job["record"].source_row_index]["source_id"]) in source_ids
        ]
    saved = {row["request_id"]: row for row in study.old.read_lines(root / "responses.jsonl")}
    if len(saved) != len(jobs):
        raise ValueError(f"Only {len(saved)}/{len(jobs)} saved responses")
    validator = Draft202012Validator(json.loads(r11.SCHEMA_PATH.read_text()))
    predictions: list[dict[str, Any]] = []
    scores = []
    per_letter = []
    failures: Counter[str] = Counter()
    native: dict[str, Counter[str]] = {method: Counter() for method in ("purist", "pragmatic")}
    for job in jobs:
        record = job["record"]
        ref = by_index[record.source_row_index]
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
        prediction = {
            "source_id": ref["source_id"],
            "source_row_index": ref["source_row_index"],
            "source_sha256": ref["source_sha256"],
            "response": parsed,
        }
        predictions.append(prediction)
        findings, invalid = compact.validate_response(parsed, ref["note"], validator)
        if invalid:
            failures[invalid] += 1
        score = scorer.score_letter(ref["note"], ref["findings"], findings)
        scores.append(score)
        per_letter.append(
            {
                "source_id": ref["source_id"],
                "source_row_index": ref["source_row_index"],
                "source_sha256": ref["source_sha256"],
                "score": score,
                "invalid_reason": invalid,
            }
        )
    root.mkdir(parents=True, exist_ok=True)
    result.mkdir(parents=True, exist_ok=True)
    compact.write_jsonl(root / "parsed_predictions.jsonl", predictions)
    compact.write_jsonl(root / "per_letter.jsonl", per_letter)
    metadata = {
        **runner.identity(args.pilot),
        "invalid_reasons": dict(failures),
        "native_answers": {k: dict(v) for k, v in native.items()},
        "charge_upper_usd": study.old.charged(study.old.read_lines(root / "attempts.jsonl")),
    }
    compact.write_json(root / "run_metadata.json", metadata)
    aggregate = scorer.aggregate(scores)
    aggregate.update(manifest)
    aggregate.update(
        {
            "scorer": scorer.VERSION,
            "scorer_source_sha256": compact.sha(Path(scorer.__file__)),
            "term_dictionary": terms.VERSION,
            "term_dictionary_sha256": compact.sha(Path(terms.__file__)),
            "prompt_version": r11.VERSION,
            "prompt_revision": r11.REVISION,
            "prompt_source_sha256": compact.sha(Path(r11.__file__)),
            "run_metadata": metadata,
            "prediction_sha256": compact.sha(root / "parsed_predictions.jsonl"),
            "reference_sha256": compact.sha(compact.REFERENCE),
            "requests_sha256": compact.sha(root / "requests.jsonl"),
            "responses_sha256": compact.sha(root / "responses.jsonl"),
            "attempts_sha256": compact.sha(root / "attempts.jsonl"),
            "per_letter_sha256": compact.sha(root / "per_letter.jsonl"),
            "run_metadata_sha256": compact.sha(root / "run_metadata.json"),
            "selected_source_ids": list(runner.PILOT_IDS) if args.pilot else None,
            "invalid_reasons": dict(failures),
        }
    )
    compact.write_json(result / "score.json", aggregate)
    print(
        json.dumps(
            {
                "rows": len(jobs),
                "tp": aggregate["tp"],
                "fp": aggregate["fp"],
                "fn": aggregate["fn"],
                "f1": aggregate["f1"],
                "native": metadata["native_answers"],
                "invalid_reasons": dict(failures),
                "charge_upper_usd": metadata["charge_upper_usd"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
