"""Run one frozen ExECTv2 2-call same-core model-swap config.

This script executes the two live model-owned components in a model-swap config
and rebuilds the deterministic SF, Prescription, and finding-assembly surfaces.
It is intended for dev140 runs only unless a separate aggregate-only full-200
predeclaration exists.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_state_projection as sf_projection,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_unknown_suppression as sf_suppression,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_diagnosis_decomposer as dx_decomposer,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_union_arbitration as sf_union,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import model_swap
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.simplification_frontier import (
    _write_sf_structured_direct_artifact,
)
from scripts.run_exectv2_v08_full200_gpt41mini_audit import (
    _run_prescription_deterministic,
)


def main() -> None:
    args = _parse_args()
    config = model_swap.load_model_swap_config(args.config)
    if config.assembly.row_count > 140 and not args.allow_non_dev140:
        raise SystemExit(
            "Refusing non-dev140 model-swap run without --allow-non-dev140. "
            "Full-200 needs a fresh aggregate-only predeclaration."
        )

    letters = load_letters()[args.offset : args.offset + config.assembly.row_count]
    producer_paths = {
        producer_id: producer.artifact
        for producer_id, producer in config.assembly.producers.items()
    }
    structured_jsonl = producer_paths["structured_key_family_event_ledger"]
    diagnosis_jsonl = producer_paths["diagnosis_decomposer"]
    sf_union_jsonl = producer_paths["sf_structured_union"]
    prescription_jsonl = producer_paths["prescription_deterministic_repair"]

    structured_rows = _run_structured(config, letters, structured_jsonl, args)
    _run_diagnosis(config, letters, structured_rows, diagnosis_jsonl, args)
    _run_sf_chain(
        structured_jsonl=structured_jsonl,
        sf_union_jsonl=sf_union_jsonl,
        letters=letters,
        split=config.assembly.split,
    )
    _run_prescription_deterministic(letters, prescription_jsonl)
    run = model_swap.write_model_swap_candidate_artifacts(
        config,
        generated_on=args.generated_on,
        gold_loader=lambda _split: letters,
    )
    headline = run.report["score_ladder"]["headline_target"]["overall"]
    print(
        json.dumps(
            {
                "candidate_id": config.candidate_id,
                "model": config.model,
                "json": config.output_json.as_posix(),
                "jsonl": config.output_jsonl.as_posix(),
                "markdown": config.output_markdown.as_posix(),
                "overall_clinical_headline_f1": headline["f1"],
            },
            indent=2,
            sort_keys=True,
        )
    )


def _run_structured(
    config: model_swap.ModelSwapConfig,
    letters: list,
    jsonl_path: Path,
    args: argparse.Namespace,
) -> list[dict]:
    if jsonl_path.exists() and args.resume:
        print(f"Reusing structured artifact: {jsonl_path.as_posix()}")
    rows, meta = structured.run_split(
        letters,
        split=config.assembly.split,
        model=config.model,
        temperature=config.temperature,
        max_tokens=int(config.max_tokens.get("structured_key_family_event_ledger", 6000)),
        mode="live",
        dspy_cache=not args.no_dspy_cache,
        api_base=args.api_base,
        progress_every=args.progress_every,
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=jsonl_path.with_suffix(".md"),
        resume=args.resume,
        prompt_profile=config.prompt_profile,  # type: ignore[arg-type]
    )
    write_jsonl(rows, jsonl_path)
    structured.write_report(rows, meta, jsonl_path.with_suffix(".md"), jsonl_path=jsonl_path)
    return rows


def _run_diagnosis(
    config: model_swap.ModelSwapConfig,
    letters: list,
    structured_rows: list[dict],
    jsonl_path: Path,
    args: argparse.Namespace,
) -> None:
    if jsonl_path.exists() and args.resume:
        print(f"Reusing Diagnosis decomposer artifact: {jsonl_path.as_posix()}")
    rows, meta = dx_decomposer.run_split(
        letters,
        draft_rows=structured_rows,
        split=config.assembly.split,
        model=config.model,
        temperature=config.temperature,
        max_tokens=int(config.max_tokens.get("diagnosis_decomposer", 2600)),
        mode="live",
        dspy_cache=not args.no_dspy_cache,
        api_base=args.api_base,
        progress_every=args.progress_every,
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=jsonl_path.with_suffix(".md"),
        resume=args.resume,
        prompt_profile=config.prompt_profile,  # type: ignore[arg-type]
    )
    write_jsonl(rows, jsonl_path)
    dx_decomposer.write_report(rows, meta, jsonl_path.with_suffix(".md"), jsonl_path=jsonl_path)


def _run_sf_chain(
    *,
    structured_jsonl: Path,
    sf_union_jsonl: Path,
    letters: list,
    split: str,
) -> None:
    sf_direct_jsonl = sf_union_jsonl.with_name(
        sf_union_jsonl.name.replace("_sf_union_arbitration", "_sf_structured_direct")
    )
    _write_sf_structured_direct_artifact(
        source=structured_jsonl,
        output=sf_direct_jsonl,
        letters=letters,
    )
    sf_projection_jsonl = sf_union_jsonl.with_name(
        sf_union_jsonl.name.replace("_sf_union_arbitration", "_sf_state_projection_combined")
    )
    sf_projection.write_rows_and_report(
        sf_projection.read_rows(sf_direct_jsonl),
        ablation="combined",
        jsonl_path=sf_projection_jsonl,
        report_path=sf_projection_jsonl.with_suffix(".md"),
    )
    sf_suppression_jsonl = sf_union_jsonl.with_name(
        sf_union_jsonl.name.replace("_sf_union_arbitration", "_sf_unknown_suppression")
    )
    sf_suppression.write_rows_and_report(
        sf_suppression.read_rows(sf_projection_jsonl),
        jsonl_path=sf_suppression_jsonl,
        report_path=sf_suppression_jsonl.with_suffix(".md"),
    )
    sf_union.write_rows_and_report(
        sf_union.read_rows(sf_suppression_jsonl),
        sf_union.deterministic_rows_from_letters(letters, split=split),
        jsonl_path=sf_union_jsonl,
        report_path=sf_union_jsonl.with_suffix(".md"),
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--generated-on", default=model_swap.DEFAULT_GENERATED_ON)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--progress-every", type=int, default=10)
    parser.add_argument("--api-base")
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--no-dspy-cache", action="store_true")
    parser.add_argument("--allow-non-dev140", action="store_true")
    args = parser.parse_args()
    args.resume = not args.no_resume
    return args


if __name__ == "__main__":
    main()
