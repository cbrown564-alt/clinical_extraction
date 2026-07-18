"""Run one frozen ExECTv2 2-call same-core model-swap config.

This script executes the two live model-owned components in a model-swap config
and rebuilds model-led SF, Prescription, and finding-assembly surfaces.
It is intended for dev140 runs only unless a separate aggregate-only full-200
predeclaration exists.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_state_projection as sf_projection,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_unknown_suppression as sf_suppression,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    diagnosis_decomposer as dx_decomposer,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    has_blocking_parse_issue,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import model_swap
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows as write_jsonl,
)


def main() -> None:
    args = _parse_args()
    config = model_swap.load_model_swap_config(args.config)
    architecture = model_swap.validate_model_led_architecture(config)
    if architecture["status"] != "pass":
        details = "\n- ".join(str(item) for item in architecture["violations"])
        raise SystemExit(
            "Refusing a model-swap run that violates decision 0040:\n- " + details
        )
    letters = _letters_for_config(
        config,
        offset=args.offset,
        allow_non_dev140=args.allow_non_dev140,
    )
    producer_paths = {
        producer_id: producer.artifact
        for producer_id, producer in config.assembly.producers.items()
    }
    structured_jsonl = producer_paths["structured_key_family_event_ledger"]
    diagnosis_jsonl = _diagnosis_artifact_path(config)
    sf_producer = config.assembly.lenses[SEIZURE_FREQUENCY.name].producer
    sf_output_jsonl = producer_paths[sf_producer]

    if args.resume:
        expected_ids = {letter.letter_id for letter in letters}
        _validate_resume_artifact(
            structured_jsonl,
            expected_ids=expected_ids,
            component="structured_key_family_event_ledger",
        )
        if diagnosis_jsonl is not None:
            _validate_resume_artifact(
                diagnosis_jsonl,
                expected_ids=expected_ids,
                component="diagnosis_decomposer",
            )

    structured_rows = _run_structured(config, letters, structured_jsonl, args)
    _require_complete_rows(
        structured_rows,
        expected_count=len(letters),
        allow_row_failures=args.allow_row_failures,
    )
    if diagnosis_jsonl is not None:
        _run_diagnosis(config, letters, structured_rows, diagnosis_jsonl, args)
    _run_model_led_sf_chain(
        structured_jsonl=structured_jsonl,
        sf_output_jsonl=sf_output_jsonl,
        letters=letters,
    )
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


def _diagnosis_artifact_path(config: model_swap.ModelSwapConfig) -> Path | None:
    """Return the sidecar path only when Diagnosis has a separate producer."""

    producer_id = config.assembly.lenses["Diagnosis"].producer
    if producer_id == "structured_key_family_event_ledger":
        return None
    if producer_id == "diagnosis_decomposer":
        return config.assembly.producers[producer_id].artifact
    raise ValueError(f"Unsupported Diagnosis producer: {producer_id}")


def _letters_for_config(
    config: model_swap.ModelSwapConfig,
    *,
    offset: int,
    allow_non_dev140: bool,
) -> list:
    split = config.assembly.split.lower()
    if split in {"dev", "dev140"}:
        source = load_letters_for_split("dev")
    elif not allow_non_dev140:
        raise SystemExit(
            "Refusing non-dev140 model-swap run without --allow-non-dev140. "
            "Full-200 needs a fresh aggregate-only predeclaration."
        )
    elif split in {"test", "test60"}:
        source = load_letters_for_split("test")
    elif split in {"full", "full200"}:
        source = load_letters()
    else:
        raise ValueError(f"unknown ExECTv2 split: {config.assembly.split!r}")
    selected = source[offset : offset + config.assembly.row_count]
    if len(selected) != config.assembly.row_count:
        raise ValueError(
            f"split {config.assembly.split!r} returned {len(selected)} rows; "
            f"expected {config.assembly.row_count}"
        )
    return selected


def _validate_resume_artifact(
    path: Path,
    *,
    expected_ids: set[str],
    component: str,
) -> None:
    if not path.exists():
        return
    rows = _read_jsonl(path)
    ids = [str(row.get("letter_id", "")) for row in rows]
    duplicate_ids = sorted(
        letter_id for letter_id in set(ids) if ids.count(letter_id) > 1
    )
    outside = sorted(set(ids) - expected_ids)
    if outside:
        raise ValueError(
            f"{component} resume artifact contains rows outside the frozen row set: "
            f"{outside}"
        )
    if duplicate_ids:
        raise ValueError(
            f"{component} resume artifact contains duplicate row ids: {duplicate_ids}"
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


def _require_clean_complete_rows(rows: list[dict], *, expected_count: int) -> None:
    """Prevent incomplete or failed model calls from reaching scoring and assembly."""

    if len(rows) != expected_count:
        raise RuntimeError(
            f"Refusing model artifact with {len(rows)} rows; expected {expected_count}."
        )
    call_failures = sum(bool(row.get("call_error")) for row in rows)
    parse_failures = sum(has_blocking_parse_issue(row.get("parse_errors")) for row in rows)
    if call_failures or parse_failures:
        raise RuntimeError(
            "Refusing model artifact before scoring: "
            f"{call_failures} call failure(s), {parse_failures} parse/schema failure(s)."
        )


def _require_complete_rows(
    rows: list[dict], *, expected_count: int, allow_row_failures: bool
) -> None:
    """Require all rows while optionally retaining reported model failures."""

    if not allow_row_failures:
        _require_clean_complete_rows(rows, expected_count=expected_count)
        return
    if len(rows) != expected_count:
        raise RuntimeError(
            f"Refusing incomplete model artifact: expected {expected_count} rows, "
            f"found {len(rows)}."
        )


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


def _run_model_led_sf_chain(
    *,
    structured_jsonl: Path,
    sf_output_jsonl: Path,
    letters: list,
) -> None:
    """Project and suppress model SF facts without an independent extractor union."""

    suffix = "_sf_unknown_suppression.jsonl"
    if not sf_output_jsonl.name.endswith(suffix):
        raise ValueError(
            "model-led Seizure Frequency output must end with "
            f"{suffix!r}: {sf_output_jsonl}"
        )
    prefix = sf_output_jsonl.name[: -len(suffix)]
    sf_direct_jsonl = sf_output_jsonl.with_name(f"{prefix}_sf_structured_direct.jsonl")
    _write_sf_structured_direct_artifact(
        source=structured_jsonl,
        output=sf_direct_jsonl,
        letters=letters,
    )
    sf_projection_jsonl = sf_output_jsonl.with_name(
        f"{prefix}_sf_state_projection_combined.jsonl"
    )
    sf_projection.write_rows_and_report(
        sf_projection.read_rows(sf_direct_jsonl),
        ablation="combined",
        jsonl_path=sf_projection_jsonl,
        report_path=sf_projection_jsonl.with_suffix(".md"),
    )
    sf_suppression.write_rows_and_report(
        sf_suppression.read_rows(sf_projection_jsonl),
        jsonl_path=sf_output_jsonl,
        report_path=sf_output_jsonl.with_suffix(".md"),
    )


def _write_sf_structured_direct_artifact(*, source: Path, output: Path, letters: list) -> None:
    """Project direct SeizureFrequency mentions from the shared model output."""

    letter_by_id = {letter.letter_id: letter for letter in letters}
    rows = []
    for row in _read_jsonl(source):
        letter_id = str(row["letter_id"])
        mentions = [
            _sf_mention(mention)
            for mention in row.get("predicted_mentions", [])
            if str(mention.get("entity")) == SEIZURE_FREQUENCY.name
        ]
        rows.append(
            {
                "letter_id": letter_id,
                "split": row.get("split", "dev"),
                "prompt_version": "structured_direct_no_sf_adjudicator_v01",
                "pipeline_family": "exectv2_structured_direct_no_sf_adjudicator",
                "model": row.get("model", ""),
                "mode": "no-call projection from structured extractor",
                "source_pipeline_family": row.get("pipeline_family", ""),
                "source_prompt_version": row.get("prompt_version", ""),
                "component_owner": "single_gpt_structured_no_sf_adjudicator",
                "call_error": None,
                "parse_errors": [],
                "gate_warnings": [],
                "predicted_mentions": mentions,
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(mentions),
                "n_evidence_invalid": 0,
                "raw_output": json.dumps(
                    {"mentions": [_raw_mention(mention) for mention in mentions]},
                    sort_keys=True,
                ),
                "gold_mentions": [
                    {
                        "entity": annotation.entity,
                        "text": annotation.text,
                        "attributes": dict(annotation.attributes),
                    }
                    for annotation in letter_by_id[letter_id].annotations
                    if annotation.entity == SEIZURE_FREQUENCY.name
                ],
            }
        )
    write_jsonl(rows, output)


def _sf_mention(mention: Mapping[str, object]) -> dict[str, object]:
    attributes = mention.get("attributes")
    return {
        "entity": SEIZURE_FREQUENCY.name,
        "text": str(mention.get("text", "")),
        "attributes": dict(attributes) if isinstance(attributes, Mapping) else {},
        "evidence": str(mention.get("evidence", "")),
        "confidence": str(mention.get("confidence") or "medium"),
        "rationale": str(mention.get("rationale", "")),
        "component_owner": "single_gpt_structured_no_sf_adjudicator",
    }


def _raw_mention(mention: Mapping[str, object]) -> dict[str, object]:
    raw = dict(mention)
    raw.pop("entity", None)
    return raw


def _read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


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
    parser.add_argument(
        "--allow-row-failures",
        action="store_true",
        help="Keep complete runs even when model call or parse failures are reported.",
    )
    args = parser.parse_args()
    args.resume = not args.no_resume
    return args


if __name__ == "__main__":
    main()
