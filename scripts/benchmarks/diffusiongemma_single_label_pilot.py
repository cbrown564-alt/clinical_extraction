"""Small fictional Purist-category pilot for vLLM DiffusionGemma structured reads.

The default command prints the frozen requests without making model calls. A live
run requires an explicit endpoint and writes the unmodified responses separately
from the scored projection. No benchmark corpus or locked holdout is read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from clinical_extraction.tasks.seizure_frequency.gan2026.llm.one_shot_contract import (
    fictional_cases,
    native_categories,
)

VERSION = "diffusiongemma_single_label_fictional_v1"
CRITERIA = {
    "currently_no_seizure": (
        "The current state is seizure-free or no current seizures are reported."
    ),
    "seizure_freq_unknown": (
        "Current seizure frequency cannot be established, or no seizure-frequency "
        "reference is present."
    ),
    "seizure_freq_1_per_yr": "Positive current frequency up to about one seizure per year.",
    "seizure_freq_1_per_6mon": "Positive current frequency about one seizure per six months.",
    "seizure_freq_more1per6mon_less1mon": (
        "Positive current frequency between one per six months and one per month."
    ),
    "seizure_freq_1_per_mon": "Positive current frequency about one seizure per month.",
    "seizure_freq_more1mon_less1week": "Positive current frequency above monthly but below weekly.",
    "seizure_freq_1_per_week": "Positive current frequency about one seizure per week.",
    "seizure_freq_more1week_less1day": "Positive current frequency above weekly but below daily.",
    "seizure_freq_1ormore_daily": "Positive current frequency at least daily.",
}


def request_for(note: str, model: str) -> dict[str, Any]:
    return {
        "model": model,
        "state": {"clinical_note": note},
        "instructions": (
            "Classify the patient's current overall epileptic seizure burden. "
            "Use the note's current, asserted observations; do not select an old rate, "
            "future condition, medication schedule or an interval between clusters "
            "as the overall rate. Count seizures within clusters when an overall "
            "frequency is given. Choose exactly one category."
        ),
        "samples": 4,
        "steps": 1,
        "think": 0,
        "questions": {
            "purist_category": {
                "type": "choice",
                "instructions": "Which category best represents current seizure frequency?",
                "criteria": CRITERIA,
            }
        },
    }


def score_response(raw: Any, gold: str) -> dict[str, Any]:
    answer = raw.get("answers", {}).get("purist_category") if isinstance(raw, dict) else None
    choice = answer.get("choice") if isinstance(answer, dict) else None
    probabilities = answer.get("probabilities") if isinstance(answer, dict) else None
    valid = (
        isinstance(choice, str)
        and choice in CRITERIA
        and isinstance(probabilities, dict)
        and set(probabilities) == set(CRITERIA)
        and all(isinstance(p, (int, float)) and 0 <= p <= 1 for p in probabilities.values())
    )
    return {
        "valid": valid,
        "predicted": choice if valid else None,
        "gold": gold,
        "correct": valid and choice == gold,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="dgemma")
    parser.add_argument("--endpoint", help="Base URL of the structured_server.py proxy")
    parser.add_argument("--output", type=Path, help="New JSON result file for a live run")
    parser.add_argument("--api-key-env", help="Environment variable containing proxy bearer token")
    args = parser.parse_args()
    if bool(args.endpoint) != bool(args.output):
        parser.error("--endpoint and --output must be supplied together for a live run")

    cases = [
        {
            "id": case["name"],
            "gold_label": case["output"]["answer"]["label"],
            "gold_purist": native_categories(case["output"]["answer"]["label"])["purist"],
            "request": request_for(case["note_text"], args.model),
        }
        for case in fictional_cases()
    ]
    if not args.endpoint:
        print(json.dumps({"version": VERSION, "cases": cases}, indent=2))
        return

    import os

    if args.api_key_env and not os.environ.get(args.api_key_env):
        parser.error(f"{args.api_key_env} is not set")
    headers = (
        {"Authorization": f"Bearer {os.environ[args.api_key_env]}"} if args.api_key_env else {}
    )
    output = args.output
    assert output is not None
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        parser.error(f"Refusing to replace existing result: {output}")
    attempts_path = output.with_suffix(output.suffix + ".attempts.jsonl")
    records = []
    with (
        attempts_path.open("x") as attempts,
        httpx.Client(timeout=600, follow_redirects=False, headers=headers) as client,
    ):
        for case in cases:
            response = client.post(
                args.endpoint.rstrip("/") + "/v1/systemone", json=case["request"]
            )
            try:
                raw = response.json()
            except ValueError:
                raw = None
            score = score_response(raw, case["gold_purist"])
            record = {
                **case,
                "http_status": response.status_code,
                "raw_text": response.text,
                "score": score,
            }
            attempts.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
            attempts.flush()
            records.append(record)
    result = {
        "version": VERSION,
        "created_at": datetime.now(UTC).isoformat(),
        "dataset": "authored fictional cases from one_shot_contract.fictional_cases",
        "scorer": "native_categories Purist projection; invalid responses count incorrect",
        "model": args.model,
        "endpoint": args.endpoint,
        "requests_sha256": hashlib.sha256(
            json.dumps([c["request"] for c in cases], sort_keys=True).encode()
        ).hexdigest(),
        "records": records,
        "summary": {
            "correct": sum(r["score"]["correct"] for r in records),
            "valid": sum(r["score"]["valid"] for r in records),
            "total": len(records),
        },
    }
    with output.open("x") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps(result["summary"]))


if __name__ == "__main__":
    main()
