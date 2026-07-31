"""Run Luna-only ExECTv2 prompt-variant A/B/C on locked test60 (aggregate-only)."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
    build_finding_assembly,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.views import (
    predictions_from_rows,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    has_blocking_parse_issue,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import model_swap
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    clinical_headline_unit_keys,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows as write_jsonl,
)
from scripts import run_exectv2_2call_model_swap as swap_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = (
    REPO_ROOT / "configs/exectv2/luna_prompt_variants_test60_20260731.json"
)
FAMILIES = (
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY.name,
    PRESCRIPTION.name,
    INVESTIGATIONS.name,
)
GENERATED_ON = "2026-07-31"
ESCALATION_REASON = (
    "Predeclared Luna-only ExECT prompt-variant A/B/C aggregate-only test60 "
    "transfer check under docs/experiments/exectv2/reliability/"
    "exectv2_luna_prompt_variants_test60_protocol_2026-07-31.md"
)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Run or resume one variant")
    run_parser.add_argument(
        "--variant",
        required=True,
        choices=("A_v0924_control", "B_luna_sf_state", "C_luna_sf_boundary_dx"),
    )
    run_parser.add_argument("--overwrite", action="store_true")
    run_parser.add_argument("--progress-every", type=int, default=5)
    run_parser.add_argument("--api-base")

    status_parser = sub.add_parser("status", help="Print aggregate status only")
    status_parser.add_argument("--variant", default=None)

    finalize_parser = sub.add_parser(
        "finalize",
        help="Write aggregate-only panel when all variants are complete",
    )
    finalize_parser.add_argument("--allow-incomplete", action="store_true")

    args = parser.parse_args(argv)
    config = _load_config(args.config)
    if args.command == "run":
        print(
            json.dumps(
                run_variant(
                    config,
                    variant_slug=args.variant,
                    overwrite=args.overwrite,
                    progress_every=args.progress_every,
                    api_base=args.api_base,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.command == "status":
        print(json.dumps(status(config, variant_slug=args.variant), indent=2))
        return
    if args.command == "finalize":
        print(
            json.dumps(
                finalize(config, allow_incomplete=args.allow_incomplete),
                indent=2,
                sort_keys=True,
            )
        )
        return
    raise ValueError(f"unknown command: {args.command}")


def _load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("split") != "test60":
        raise ValueError("config split must be test60")
    if config.get("row_policy") != "aggregate_only":
        raise ValueError("config row_policy must be aggregate_only")
    if config.get("row_count") != 59:
        raise ValueError("config row_count must be 59")
    if config.get("dspy_cache") is not False:
        raise ValueError("config must disable DSPy cache")
    if config.get("model") != "openai/gpt-5.6-luna":
        raise ValueError("config model must be openai/gpt-5.6-luna")
    if not str(config.get("artifact_root", "")).startswith("scratch/holdout/"):
        raise ValueError("test60 artifacts must stay under scratch/holdout/")
    repair = config.get("repair_policy") or {}
    if repair.get("diagnosis_policy_variant") != "default":
        raise ValueError(
            "active Luna variants require diagnosis_policy_variant=default "
            "(decision 0045); joint/combined is archived"
        )
    if repair.get("prescription_policy_variant") != "default":
        raise ValueError(
            "active Luna variants require prescription_policy_variant=default "
            "(decision 0045); joint/combined is archived"
        )
    variants = config.get("variants")
    if not isinstance(variants, list) or len(variants) != 3:
        raise ValueError("config must declare exactly three variants")
    return config


def _variant(config: Mapping[str, Any], slug: str) -> dict[str, Any]:
    for item in config["variants"]:
        if item["slug"] == slug:
            return item
    raise ValueError(f"unknown variant: {slug}")


def _variant_dir(config: Mapping[str, Any], slug: str) -> Path:
    return REPO_ROOT / str(config["artifact_root"]) / slug


def _structured_path(config: Mapping[str, Any], slug: str) -> Path:
    return _variant_dir(config, slug) / "structured.jsonl"


def _sf_final_path(config: Mapping[str, Any], slug: str) -> Path:
    return _variant_dir(config, slug) / "variant_sf_unknown_suppression.jsonl"


def _sf_direct_path(config: Mapping[str, Any], slug: str) -> Path:
    return _variant_dir(config, slug) / "variant_sf_structured_direct.jsonl"


def _assembly_jsonl_path(config: Mapping[str, Any], slug: str) -> Path:
    return _variant_dir(config, slug) / "assembly.jsonl"


def _aggregate_path(config: Mapping[str, Any], slug: str) -> Path:
    return _variant_dir(config, slug) / "aggregate.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def status(
    config: Mapping[str, Any],
    *,
    variant_slug: str | None = None,
) -> dict[str, Any]:
    slugs = (
        [variant_slug]
        if variant_slug
        else [str(item["slug"]) for item in config["variants"]]
    )
    out: dict[str, Any] = {"row_policy": "aggregate_only", "variants": {}}
    for slug in slugs:
        agg_path = _aggregate_path(config, slug)
        structured_path = _structured_path(config, slug)
        rows = _count_jsonl(structured_path) if structured_path.exists() else 0
        out["variants"][slug] = {
            "structured_rows": rows,
            "aggregate_exists": agg_path.exists(),
            "complete": rows >= int(config["row_count"]) and agg_path.exists(),
        }
        if agg_path.exists():
            aggregate = json.loads(agg_path.read_text(encoding="utf-8"))
            out["variants"][slug]["joint_headline_f1"] = aggregate.get(
                "joint_headline_f1"
            )
            out["variants"][slug]["sf_model_owned_correct"] = aggregate.get(
                "model_owned_letter_correct", {}
            ).get(SEIZURE_FREQUENCY.name)
            out["variants"][slug]["sf_joint_correct"] = aggregate.get(
                "joint_letter_correct", {}
            ).get(SEIZURE_FREQUENCY.name)
    return out


def run_variant(
    config: Mapping[str, Any],
    *,
    variant_slug: str,
    overwrite: bool = False,
    progress_every: int = 5,
    api_base: str | None = None,
) -> dict[str, Any]:
    variant = _variant(config, variant_slug)
    prompt_version = str(variant["prompt_version"])
    snapshot = REPO_ROOT / str(variant["prompt_snapshot"])
    if not snapshot.is_file():
        raise FileNotFoundError(snapshot)

    letters = load_letters_for_split("test")
    if len(letters) != int(config["row_count"]):
        raise ValueError(
            f"expected {config['row_count']} test letters, found {len(letters)}"
        )
    expected_count = len(letters)

    out_dir = _variant_dir(config, variant_slug)
    out_dir.mkdir(parents=True, exist_ok=True)
    structured_path = _structured_path(config, variant_slug)
    sf_final_path = _sf_final_path(config, variant_slug)
    assembly_jsonl = _assembly_jsonl_path(config, variant_slug)
    aggregate_path = _aggregate_path(config, variant_slug)

    if (
        not overwrite
        and aggregate_path.exists()
        and structured_path.exists()
        and _count_jsonl(structured_path) >= expected_count
    ):
        aggregate = json.loads(aggregate_path.read_text(encoding="utf-8"))
        return {
            "variant": variant_slug,
            "state": "already_complete",
            "row_policy": "aggregate_only",
            "rows": aggregate.get("rows"),
            "joint_headline_f1": aggregate.get("joint_headline_f1"),
        }

    original_prompt = structured.PROMPT_VERSION
    started = datetime.now(UTC).isoformat()
    try:
        structured.set_active_prompt_version(prompt_version)
        if variant["call_mode"] == "saved_structured_no_call":
            source = REPO_ROOT / str(variant["reuse_structured"])
            if not source.is_file():
                raise FileNotFoundError(source)
            _copy_structured_subset(source, structured_path, letters)
            call_mode = "saved_structured_no_call"
            new_model_calls = 0
        elif variant["call_mode"] == "live":
            print(f"ESCALATION_REASON={ESCALATION_REASON}")
            rows, meta = structured.run_split(
                letters,
                split="test60",
                model=str(config["model"]),
                temperature=float(config["temperature"]),
                max_tokens=int(
                    config["max_tokens"]["structured_key_family_event_ledger"]
                ),
                mode="live",
                dspy_cache=False,
                api_base=api_base,
                progress_every=progress_every,
                checkpoint_jsonl_path=structured_path,
                checkpoint_report_path=structured_path.with_suffix(".md"),
                resume=not overwrite,
                prompt_profile=str(config["prompt_profile"]),
            )
            write_jsonl(rows, structured_path)
            structured.write_report(
                rows,
                meta,
                structured_path.with_suffix(".md"),
                jsonl_path=structured_path,
            )
            call_mode = "live"
            new_model_calls = sum(
                1 for row in rows if not row.get("call_error") and row.get("raw_output")
            )
        else:
            raise ValueError(f"unsupported call_mode: {variant['call_mode']}")

        rows = _read_jsonl(structured_path)
        _require_clean_complete_rows(rows, expected_count=expected_count)
        swap_runner._run_model_led_sf_chain(
            structured_jsonl=structured_path,
            sf_output_jsonl=sf_final_path,
            letters=letters,
        )
        assembly = _variant_assembly(config, variant_slug, structured_path, sf_final_path)
        run = build_finding_assembly(
            assembly,
            generated_on=GENERATED_ON,
            gold_loader=lambda _split: letters,
            diagnosis_resolution_candidate=True,
            diagnosis_policy_variant=str(
                config["repair_policy"]["diagnosis_policy_variant"]
            ),
            prescription_policy_variant=str(
                config["repair_policy"]["prescription_policy_variant"]
            ),
        )
        write_jsonl(run.rows, assembly_jsonl)
        counts = _aggregate_letter_counts(
            gold=letters,
            structured_path=structured_path,
            sf_direct_path=_sf_direct_path(config, variant_slug),
            assembly_jsonl=assembly_jsonl,
        )
        headline = run.report["score_ladder"]["headline_target"]
        aggregate = {
            "schema_version": "exectv2.luna_prompt_variants_test60_aggregate.v1",
            "variant": variant_slug,
            "model": config["model"],
            "split": "test60",
            "row_policy": "aggregate_only",
            "prompt_version": prompt_version,
            "prompt_snapshot": variant["prompt_snapshot"],
            "prompt_snapshot_sha256": _sha256(snapshot),
            "repair_policy": config["repair_policy"],
            "call_mode": call_mode,
            "new_model_calls": new_model_calls,
            "rows": expected_count,
            "call_failures": sum(bool(row.get("call_error")) for row in rows),
            "parse_failures": sum(
                has_blocking_parse_issue(row.get("parse_errors")) for row in rows
            ),
            "joint_headline_f1": float(headline["overall"]["f1"]),
            "joint_family_f1": {
                family: float(headline["by_indicator"][family]["f1"])
                for family in FAMILIES
            },
            "model_owned_letter_correct": counts["model_owned_letter_correct"],
            "joint_letter_correct": counts["joint_letter_correct"],
            "structured_sha256": _sha256(structured_path),
            "sf_final_sha256": _sha256(sf_final_path),
            "assembly_sha256": _sha256(assembly_jsonl),
            "started_utc": started,
            "finished_utc": datetime.now(UTC).isoformat(),
            "claim_boundary": (
                "Aggregate-only Luna-versus-Luna test60 transfer evidence; "
                "not row-level analysis, clinical validation, or a six-model "
                "panel rewrite."
            ),
        }
        aggregate_path.write_text(
            json.dumps(aggregate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    finally:
        structured.set_active_prompt_version(original_prompt)

    return {
        "variant": variant_slug,
        "state": "complete",
        "row_policy": "aggregate_only",
        "rows": expected_count,
        "call_mode": call_mode,
        "new_model_calls": new_model_calls,
        "joint_headline_f1": aggregate["joint_headline_f1"],
        "joint_family_f1": aggregate["joint_family_f1"],
        "model_owned_letter_correct": aggregate["model_owned_letter_correct"],
        "joint_letter_correct": aggregate["joint_letter_correct"],
        "artifact_sha256": aggregate["structured_sha256"],
    }


def finalize(
    config: Mapping[str, Any],
    *,
    allow_incomplete: bool = False,
) -> dict[str, Any]:
    expected = int(config["row_count"])
    conditions: list[dict[str, Any]] = []
    for variant in config["variants"]:
        slug = str(variant["slug"])
        agg_path = _aggregate_path(config, slug)
        if not agg_path.exists():
            if allow_incomplete:
                continue
            raise FileNotFoundError(f"missing variant aggregate: {agg_path}")
        aggregate = json.loads(agg_path.read_text(encoding="utf-8"))
        if not allow_incomplete and int(aggregate.get("rows", 0)) != expected:
            raise ValueError(
                f"{slug} incomplete: rows={aggregate.get('rows')} expected={expected}"
            )
        conditions.append(
            {
                "variant": slug,
                "prompt_version": variant["prompt_version"],
                "call_mode": variant["call_mode"],
                "rows": aggregate["rows"],
                "call_failures": aggregate["call_failures"],
                "parse_failures": aggregate["parse_failures"],
                "joint_headline_f1": aggregate["joint_headline_f1"],
                "joint_family_f1": aggregate["joint_family_f1"],
                "model_owned_letter_correct": aggregate["model_owned_letter_correct"],
                "joint_letter_correct": aggregate["joint_letter_correct"],
                "structured_sha256": aggregate["structured_sha256"],
            }
        )

    by_slug = {item["variant"]: item for item in conditions}
    comparison: dict[str, Any] = {}
    if "A_v0924_control" in by_slug:
        base = by_slug["A_v0924_control"]
        for slug, item in by_slug.items():
            if slug == "A_v0924_control":
                continue
            comparison[slug] = {
                "delta_joint_headline_f1": round(
                    item["joint_headline_f1"] - base["joint_headline_f1"], 4
                ),
                "delta_sf_model_owned_correct": (
                    item["model_owned_letter_correct"][SEIZURE_FREQUENCY.name]
                    - base["model_owned_letter_correct"][SEIZURE_FREQUENCY.name]
                ),
                "delta_sf_joint_correct": (
                    item["joint_letter_correct"][SEIZURE_FREQUENCY.name]
                    - base["joint_letter_correct"][SEIZURE_FREQUENCY.name]
                ),
                "delta_sf_joint_f1": round(
                    item["joint_family_f1"][SEIZURE_FREQUENCY.name]
                    - base["joint_family_f1"][SEIZURE_FREQUENCY.name],
                    4,
                ),
                "delta_dx_joint_correct": (
                    item["joint_letter_correct"][DIAGNOSIS.name]
                    - base["joint_letter_correct"][DIAGNOSIS.name]
                ),
            }

    panel = {
        "schema_version": "exectv2.luna_prompt_variants_test60_panel.v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "protocol": config["protocol"],
        "configuration": DEFAULT_CONFIG.relative_to(REPO_ROOT).as_posix(),
        "dataset": config["dataset"],
        "split": "test60",
        "row_policy": "aggregate_only",
        "model": config["model"],
        "repair_policy": config["repair_policy"],
        "complete": len(conditions) == 3
        and all(item["rows"] == expected for item in conditions),
        "conditions": conditions,
        "comparison_vs_A": comparison,
        "claim_boundary": (
            "Aggregate-only Luna-versus-Luna test60 transfer evidence for the named "
            "prompts under default Diagnosis/Prescription repair (decision 0045); "
            "not clinical validation, row-level analysis, or a rewrite of the "
            "frozen six-model v0.9.24 panel."
        ),
    }
    out_dir = REPO_ROOT / "experiments" / "exectv2_luna_prompt_variants_test60_20260731"
    out_dir.mkdir(parents=True, exist_ok=True)
    panel_path = out_dir / "panel.json"
    panel_path.write_text(
        json.dumps(panel, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report_path = (
        REPO_ROOT
        / "docs/experiments/exectv2/reliability/"
        / "exectv2_luna_prompt_variants_test60_2026-07-31.md"
    )
    report_path.write_text(_render_report(panel), encoding="utf-8")
    return {
        "panel": panel_path.relative_to(REPO_ROOT).as_posix(),
        "report": report_path.relative_to(REPO_ROOT).as_posix(),
        "complete": panel["complete"],
        "conditions": len(conditions),
        "row_policy": "aggregate_only",
        "comparison_vs_A": comparison,
    }


def _render_report(panel: Mapping[str, Any]) -> str:
    lines = [
        "# Luna ExECT prompt-variant A/B/C test60 panel",
        "",
        f"Generated: {panel['generated_at_utc']}",
        "Readout: aggregate-only",
        f"Protocol: [{Path(str(panel['protocol'])).name}]({Path(str(panel['protocol'])).name})",
        "",
        "## Results",
        "",
        (
            "| Variant | Overall F1 (default repair) | SF F1 | "
            "SF model-owned correct | SF final correct | Dx final correct |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in panel["conditions"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    item["variant"],
                    f"{item['joint_headline_f1']:.4f}",
                    f"{item['joint_family_f1'][SEIZURE_FREQUENCY.name]:.4f}",
                    f"{item['model_owned_letter_correct'][SEIZURE_FREQUENCY.name]}/{item['rows']}",
                    f"{item['joint_letter_correct'][SEIZURE_FREQUENCY.name]}/{item['rows']}",
                    f"{item['joint_letter_correct'][DIAGNOSIS.name]}/{item['rows']}",
                ]
            )
            + " |"
        )
    if panel.get("comparison_vs_A"):
        lines.extend(
            [
                "",
                "## Deltas versus A",
                "",
                (
                    "| Variant | Δ joint F1 | Δ SF joint F1 | Δ SF model-owned | "
                    "Δ SF joint | Δ Dx joint |"
                ),
                "| --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for slug, item in panel["comparison_vs_A"].items():
            lines.append(
                "| "
                + " | ".join(
                    [
                        slug,
                        f"{item['delta_joint_headline_f1']:+.4f}",
                        f"{item['delta_sf_joint_f1']:+.4f}",
                        f"{item['delta_sf_model_owned_correct']:+d}",
                        f"{item['delta_sf_joint_correct']:+d}",
                        f"{item['delta_dx_joint_correct']:+d}",
                    ]
                )
                + " |"
            )
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            str(panel["claim_boundary"]),
            "",
            "No test-row identifiers, notes, predictions, or failure cases are "
            "reported.",
            "",
        ]
    )
    return "\n".join(lines)


def _copy_structured_subset(
    source: Path,
    destination: Path,
    letters: Sequence[Any],
) -> None:
    wanted = {letter.letter_id for letter in letters}
    rows = [
        row for row in _read_jsonl(source) if str(row.get("letter_id")) in wanted
    ]
    if len(rows) != len(wanted):
        raise ValueError(
            f"reuse structured artifact incomplete: found {len(rows)} of {len(wanted)}"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(rows, destination)


def _variant_assembly(
    config: Mapping[str, Any],
    slug: str,
    structured_path: Path,
    sf_final_path: Path,
) -> Any:
    base = model_swap.load_model_swap_config(
        REPO_ROOT / "configs/exectv2/six_model_comparison/gpt56luna_dev140.json"
    ).assembly
    producers = {
        "structured_key_family_event_ledger": replace(
            base.producers["structured_key_family_event_ledger"],
            artifact=structured_path,
        ),
        "sf_model_projection_suppression": replace(
            base.producers["sf_model_projection_suppression"],
            artifact=sf_final_path,
        ),
    }
    return replace(
        base,
        candidate_id=f"exectv2_luna_prompt_variants_test60_{slug}",
        split="test",
        row_count=int(config["row_count"]),
        producers=producers,
        claim_boundary=(
            "ExECTv2 Luna prompt-variant aggregate-only test60 transfer check."
        ),
    )


def _require_clean_complete_rows(rows: list[dict[str, Any]], *, expected_count: int) -> None:
    if len(rows) != expected_count:
        raise RuntimeError(
            f"Refusing model artifact with {len(rows)} rows; expected {expected_count}."
        )
    call_failures = sum(bool(row.get("call_error")) for row in rows)
    parse_failures = sum(
        has_blocking_parse_issue(row.get("parse_errors")) for row in rows
    )
    if call_failures or parse_failures:
        raise RuntimeError(
            "Refusing model artifact before scoring: "
            f"{call_failures} call failure(s), {parse_failures} parse/schema failure(s)."
        )


def _aggregate_letter_counts(
    *,
    gold: Sequence[Any],
    structured_path: Path,
    sf_direct_path: Path,
    assembly_jsonl: Path,
) -> dict[str, dict[str, int]]:
    structured_rows = {
        str(row["letter_id"]): row for row in _read_jsonl(structured_path)
    }
    sf_rows = {str(row["letter_id"]): row for row in _read_jsonl(sf_direct_path)}
    assembly_rows = {
        str(row["letter_id"]): row for row in _read_jsonl(assembly_jsonl)
    }
    model_owned = {
        DIAGNOSIS.name: _letters_from_producer(structured_rows, DIAGNOSIS.name),
        PRESCRIPTION.name: _letters_from_producer(structured_rows, PRESCRIPTION.name),
        INVESTIGATIONS.name: _letters_from_producer(
            structured_rows, INVESTIGATIONS.name
        ),
        SEIZURE_FREQUENCY.name: _letters_from_producer(
            sf_rows, SEIZURE_FREQUENCY.name
        ),
    }
    joint_final = {
        prediction.letter_id: to_exect_letter(prediction)
        for prediction in predictions_from_rows(
            list(assembly_rows.values()),
            "predicted_mentions",
        )
    }
    model_counts = {family: 0 for family in FAMILIES}
    joint_counts = {family: 0 for family in FAMILIES}
    for letter in gold:
        final_letter = joint_final[letter.letter_id]
        for family in FAMILIES:
            source_mentions = [
                mention
                for mention in model_owned[family][letter.letter_id].annotations
                if mention.entity == family
            ]
            final_mentions = [
                mention
                for mention in final_letter.annotations
                if mention.entity == family
            ]
            gold_mentions = [
                annotation
                for annotation in letter.annotations
                if annotation.entity == family
            ]
            source_keys = Counter(
                clinical_headline_unit_keys(family, source_mentions, letter.note_text)
            )
            final_keys = Counter(
                clinical_headline_unit_keys(family, final_mentions, letter.note_text)
            )
            gold_keys = Counter(
                clinical_headline_unit_keys(family, gold_mentions, letter.note_text)
            )
            if source_keys == gold_keys:
                model_counts[family] += 1
            if final_keys == gold_keys:
                joint_counts[family] += 1
    return {
        "model_owned_letter_correct": model_counts,
        "joint_letter_correct": joint_counts,
    }


def _letters_from_producer(
    rows_by_id: Mapping[str, dict[str, Any]],
    family: str,
) -> dict[str, Any]:
    predictions = predictions_from_rows(list(rows_by_id.values()), "predicted_mentions")
    return {
        prediction.letter_id: to_exect_letter(prediction) for prediction in predictions
    }


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


if __name__ == "__main__":
    main()
