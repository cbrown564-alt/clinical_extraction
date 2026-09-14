"""Replay the prepared synthetic development requests against a local model server.

No-install entry point. Run from the repository root using the repository .venv.
This is a distinct supplementary runtime; it cannot read a test or patient dataset.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import httpx

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation.one_shot_analysis import (
    summarize,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation.one_shot_study import (
    append,
    digest,
    encoded,
    response_content,
    write_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.one_shot_contract import (
    CONDITIONS,
    inspect_output,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    bundle = json.loads(args.bundle.read_text())
    runtime = json.loads(args.runtime.read_text())
    if bundle["scope"] != "synthetic_dev750_fixed20":
        raise ValueError("Only the prepared synthetic development bundle is supported")
    for key in (
        "base_url",
        "model",
        "revision",
        "quantisation",
        "hardware",
        "engine",
        "engine_version",
        "nonthinking_parameters",
    ):
        if key not in runtime or runtime[key] in (None, "", "TO_BE_SUPPLIED"):
            raise ValueError(f"Supply the actual local runtime field: {key}")
    args.output.mkdir(parents=True, exist_ok=False)
    write_json(args.output / "runtime.json", runtime)
    write_json(
        args.output / "bundle_identity.json",
        {"sha256": digest(args.bundle.read_bytes()), "scope": bundle["scope"]},
    )
    pairs = []
    with httpx.Client(timeout=180) as client:
        for row in bundle["rows"]:
            pair = {}
            for condition in CONDITIONS:
                request = dict(row["requests"][condition])
                request.pop("thinking", None)
                parameters = runtime["nonthinking_parameters"]
                if not isinstance(parameters, dict) or any(
                    k in parameters for k in ("messages", "max_tokens", "model", "response_format")
                ):
                    raise ValueError("Runtime parameters must not alter the clinical request")
                request.update(parameters)
                request["model"] = runtime["model"]
                rid = digest(encoded(request))
                append(args.output / "requests.jsonl", {"request_id": rid, "body": request})
                start = time.time()
                response = None
                error = None
                try:
                    returned = client.post(
                        runtime["base_url"].rstrip("/") + "/chat/completions", json=request
                    )
                    returned.raise_for_status()
                    response = returned.json()
                except (httpx.HTTPError, ValueError) as exc:
                    error = type(exc).__name__
                append(
                    args.output / "responses.jsonl",
                    {
                        "request_id": rid,
                        "response": response,
                        "error": error,
                        "latency_seconds": time.time() - start,
                    },
                )
                content, finish = response_content(response)
                result = inspect_output(content, row["note_text"], condition, finish_reason=finish)
                for method in ("purist", "pragmatic"):
                    result[method + "_correct"] = result["failure"] is None and (
                        result["categories"][method] == row["gold_categories"][method]
                    )
                pair[condition] = result
            pairs.append(pair)
    report = summarize(pairs)
    report.update(
        {
            "scope": bundle["scope"],
            "runtime": runtime,
            "claim_boundary": "supplementary local development; not held-out performance",
        }
    )
    write_json(args.output / "aggregate.json", report)
    print(f"Saved local development artifacts to {args.output}")


if __name__ == "__main__":
    main()
