"""Smoke-test one frozen six-model condition on the first dev140 rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured import (  # noqa: E501
    runner as structured_runner,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import model_swap
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from scripts.run_exectv2_six_model_comparison import (
    build_six_model_lm,
    configure_declared_runtime,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--rows", type=int, default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    config = model_swap.load_model_swap_config(args.config)
    configure_declared_runtime(args.config)
    architecture = model_swap.validate_model_led_architecture(config)
    if architecture["status"] != "pass":
        raise SystemExit(json.dumps(architecture, sort_keys=True))

    structured_runner.build_dspy_lm = build_six_model_lm
    letters = load_letters_for_split("dev")[: args.rows]
    structured_rows, structured_meta = structured.run_split(
        letters,
        split="dev140_smoke",
        model=config.model,
        temperature=config.temperature,
        max_tokens=int(config.max_tokens["structured_key_family_event_ledger"]),
        mode="live",
        dspy_cache=False,
        progress_every=1,
        checkpoint_jsonl_path=args.output,
        checkpoint_report_path=args.output.with_suffix(".md") if args.output else None,
        prompt_profile=config.prompt_profile,  # type: ignore[arg-type]
    )
    output = args.output or Path(
        f"scratch/local_queue/{config.candidate_id}/dev{args.rows}.jsonl"
    )
    write_jsonl_rows(structured_rows, output)
    print(
        json.dumps(
            {
                "candidate_id": config.candidate_id,
                "model": config.model,
                "rows": len(letters),
                "structured": _status(structured_meta),
            },
            sort_keys=True,
        )
    )


def _status(metadata: dict) -> dict[str, int]:
    summary = metadata["summary"]
    return {
        "call_failures": int(summary.get("call_failures", 0)),
        "parse_failures": int(summary.get("parse_failures", 0)),
        "mentions_scored": int(summary.get("n_mentions_scored", 0)),
    }


if __name__ == "__main__":
    main()
