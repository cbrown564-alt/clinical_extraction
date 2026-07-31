"""Run the Luna-only ExECTv2 prompt-variant A/B/C development comparison."""

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
    render_finding_assembly_markdown,
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
    REPO_ROOT / "configs/exectv2/luna_prompt_variants_dev140_20260731.json"
)
FAMILIES = (
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY.name,
    PRESCRIPTION.name,
    INVESTIGATIONS.name,
)
GENERATED_ON = "2026-07-31"
ESCALATION_REASON = (
    "Predeclared Luna-only ExECT prompt-variant A/B/C development comparison on "
    "dev140 under docs/experiments/exectv2/reliability/"
    "exectv2_luna_prompt_variants_dev140_protocol_2026-07-31.md"
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
    run_parser.add_argument("--limit", type=int, default=None)
    run_parser.add_argument("--overwrite", action="store_true")
    run_parser.add_argument("--progress-every", type=int, default=5)
    run_parser.add_argument("--api-base")

    status_parser = sub.add_parser("status", help="Print per-variant completeness")
    status_parser.add_argument("--variant", default=None)

    finalize_parser = sub.add_parser(
        "finalize",
        help="Build the comparison panel when all variants are complete",
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
                    limit=args.limit,
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
    if config.get("split") != "dev140":
        raise ValueError("config split must be dev140")
    if config.get("row_count") != 140:
        raise ValueError("config row_count must be 140")
    if config.get("dspy_cache") is not False:
        raise ValueError("config must disable DSPy cache")
    if config.get("model") != "openai/gpt-5.6-luna":
        raise ValueError("config model must be openai/gpt-5.6-luna")
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
    # Must end with `_sf_unknown_suppression.jsonl` so the retained SF chain
    # can derive the structured-direct and projection companion paths.
    return _variant_dir(config, slug) / "variant_sf_unknown_suppression.jsonl"


def _sf_direct_path(config: Mapping[str, Any], slug: str) -> Path:
    return _variant_dir(config, slug) / "variant_sf_structured_direct.jsonl"


def _assembly_json_path(config: Mapping[str, Any], slug: str) -> Path:
    return _variant_dir(config, slug) / "assembly.json"


def _assembly_jsonl_path(config: Mapping[str, Any], slug: str) -> Path:
    return _variant_dir(config, slug) / "assembly.jsonl"


def _provenance_path(config: Mapping[str, Any], slug: str) -> Path:
    return _variant_dir(config, slug) / "provenance.json"


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
    out: dict[str, Any] = {"variants": {}}
    for slug in slugs:
        structured_path = _structured_path(config, slug)
        assembly_path = _assembly_json_path(config, slug)
        structured_rows = (
            _read_jsonl(structured_path) if structured_path.exists() else []
        )
        out["variants"][slug] = {
            "structured_exists": structured_path.exists(),
            "structured_rows": len(structured_rows),
            "assembly_exists": assembly_path.exists(),
            "complete": (
                len(structured_rows) >= int(config["row_count"])
                and assembly_path.exists()
            ),
            "structured_path": structured_path.relative_to(REPO_ROOT).as_posix()
            if structured_path.exists()
            else None,
            "assembly_path": assembly_path.relative_to(REPO_ROOT).as_posix()
            if assembly_path.exists()
            else None,
        }
    return out


def run_variant(
    config: Mapping[str, Any],
    *,
    variant_slug: str,
    limit: int | None = None,
    overwrite: bool = False,
    progress_every: int = 5,
    api_base: str | None = None,
) -> dict[str, Any]:
    variant = _variant(config, variant_slug)
    prompt_version = str(variant["prompt_version"])
    snapshot = REPO_ROOT / str(variant["prompt_snapshot"])
    if not snapshot.is_file():
        raise FileNotFoundError(snapshot)

    letters = load_letters_for_split("dev")
    if len(letters) != 140:
        raise ValueError(f"expected 140 dev letters, found {len(letters)}")
    if limit is not None:
        letters = letters[:limit]
    expected_count = len(letters)

    out_dir = _variant_dir(config, variant_slug)
    out_dir.mkdir(parents=True, exist_ok=True)
    structured_path = _structured_path(config, variant_slug)
    sf_final_path = _sf_final_path(config, variant_slug)
    assembly_json = _assembly_json_path(config, variant_slug)
    assembly_jsonl = _assembly_jsonl_path(config, variant_slug)
    provenance_path = _provenance_path(config, variant_slug)

    if (
        not overwrite
        and structured_path.exists()
        and assembly_json.exists()
        and len(_read_jsonl(structured_path)) >= expected_count
    ):
        return {
            "variant": variant_slug,
            "state": "already_complete",
            "rows": len(_read_jsonl(structured_path)),
            "assembly": assembly_json.relative_to(REPO_ROOT).as_posix(),
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
            rows, _meta = structured.run_split(
                letters,
                split="dev140",
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
                _meta,
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
        report = dict(run.report)
        report["prompt_version"] = prompt_version
        report["variant_slug"] = variant_slug
        report["repair_policy"] = config["repair_policy"]
        report["claim_boundary"] = (
            "ExECTv2 Luna prompt-variant development comparison on dev140 only."
        )
        write_jsonl(run.rows, assembly_jsonl)
        assembly_json.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        assembly_json.with_suffix(".md").write_text(
            render_finding_assembly_markdown(
                report,
                json_path=assembly_json,
                jsonl_path=assembly_jsonl,
            ),
            encoding="utf-8",
        )
        provenance = {
            "variant": variant_slug,
            "prompt_version": prompt_version,
            "prompt_snapshot": variant["prompt_snapshot"],
            "prompt_snapshot_sha256": _sha256(snapshot),
            "call_mode": call_mode,
            "new_model_calls": new_model_calls,
            "started_utc": started,
            "finished_utc": datetime.now(UTC).isoformat(),
            "structured_sha256": _sha256(structured_path),
            "sf_final_sha256": _sha256(sf_final_path),
            "assembly_sha256": _sha256(assembly_json),
            "escalation_reason": ESCALATION_REASON,
            "row_count": expected_count,
            "limit": limit,
        }
        provenance_path.write_text(
            json.dumps(provenance, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    finally:
        structured.set_active_prompt_version(original_prompt)

    headline = report["score_ladder"]["headline_target"]
    return {
        "variant": variant_slug,
        "state": "complete",
        "rows": expected_count,
        "call_mode": call_mode,
        "new_model_calls": new_model_calls,
        "overall_clinical_headline_f1": headline["overall"]["f1"],
        "family_f1": {
            family: headline["by_indicator"][family]["f1"] for family in FAMILIES
        },
        "assembly": assembly_json.relative_to(REPO_ROOT).as_posix(),
        "provenance": provenance_path.relative_to(REPO_ROOT).as_posix(),
    }


def _copy_structured_subset(
    source: Path,
    destination: Path,
    letters: Sequence[Any],
) -> None:
    wanted = {letter.letter_id for letter in letters}
    rows = [
        row
        for row in _read_jsonl(source)
        if str(row.get("letter_id")) in wanted
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
        candidate_id=f"exectv2_luna_prompt_variants_{slug}",
        split="dev",
        row_count=int(config["row_count"]),
        producers=producers,
        claim_boundary=(
            "ExECTv2 Luna prompt-variant development comparison on dev140 only."
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


def finalize(
    config: Mapping[str, Any],
    *,
    allow_incomplete: bool = False,
) -> dict[str, Any]:
    completeness = status(config)
    incomplete = [
        slug
        for slug, info in completeness["variants"].items()
        if not info["complete"]
    ]
    if incomplete and not allow_incomplete:
        raise RuntimeError(f"incomplete variants: {incomplete}")

    gold = load_letters_for_split("dev")
    slice_membership = _slice_membership(config)
    panel_rows: list[dict[str, Any]] = []
    variant_summaries: dict[str, Any] = {}

    for variant in config["variants"]:
        slug = str(variant["slug"])
        if not completeness["variants"][slug]["complete"]:
            continue
        structured_path = _structured_path(config, slug)
        sf_direct_path = _sf_direct_path(config, slug)
        if not sf_direct_path.exists():
            raise FileNotFoundError(sf_direct_path)

        assembly_report = json.loads(
            _assembly_json_path(config, slug).read_text(encoding="utf-8")
        )
        letter_rows = _letter_family_rows(
            gold=gold,
            structured_path=structured_path,
            sf_direct_path=sf_direct_path,
            assembly_jsonl=_assembly_jsonl_path(config, slug),
            variant=variant,
            slice_membership=slice_membership,
        )
        panel_rows.extend(letter_rows)
        variant_summaries[slug] = _variant_summary(
            slug=slug,
            variant=variant,
            assembly_report=assembly_report,
            letter_rows=letter_rows,
            provenance=_read_json(_provenance_path(config, slug)),
        )

    out_dir = REPO_ROOT / "experiments" / "exectv2_luna_prompt_variants_dev140_20260731"
    out_dir.mkdir(parents=True, exist_ok=True)
    panel_path = out_dir / "panel.jsonl"
    summary_path = out_dir / "panel_summary.json"
    with panel_path.open("w", encoding="utf-8") as handle:
        for row in panel_rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    summary = {
        "schema_version": "exectv2.luna_prompt_variants_dev140.v1",
        "generated_on": GENERATED_ON,
        "protocol": config["protocol"],
        "model": config["model"],
        "repair_policy": config["repair_policy"],
        "variants": variant_summaries,
        "comparison_vs_A": _comparison_vs_a(variant_summaries),
        "panel_path": panel_path.relative_to(REPO_ROOT).as_posix(),
        "claim_boundary": (
            "ExECTv2 Luna-versus-Luna development evidence on dev140 under frozen "
            "schema and default Diagnosis/Prescription repair (decision 0045). "
            "Not test60, clinical validation, or panel promotion."
        ),
    }
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report_path = (
        REPO_ROOT
        / "docs/experiments/exectv2/reliability/"
        / "exectv2_luna_prompt_variants_dev140_2026-07-31.md"
    )
    report_path.write_text(_render_report(summary), encoding="utf-8")
    return {
        "status": "pass",
        "panel": panel_path.relative_to(REPO_ROOT).as_posix(),
        "summary": summary_path.relative_to(REPO_ROOT).as_posix(),
        "report": report_path.relative_to(REPO_ROOT).as_posix(),
        "variants": {
            slug: {
                "overall_f1": item["joint_headline_f1"],
                "sf_model_owned_correct": item["model_owned_letter_correct"][
                    SEIZURE_FREQUENCY.name
                ],
                "sf_joint_correct": item["joint_letter_correct"][SEIZURE_FREQUENCY.name],
            }
            for slug, item in variant_summaries.items()
        },
    }


def _slice_membership(config: Mapping[str, Any]) -> dict[str, set[str]]:
    path = REPO_ROOT / str(config["residual_panel"])
    rows = _read_jsonl(path)
    membership: dict[str, set[str]] = {
        "b_target": set(),
        "c_target": set(),
        "rx_nontarget": set(),
        "empty_gold_diagnostic": set(),
    }
    for row in rows:
        letter_id = str(row["letter_id"])
        theme = str(row.get("theme", ""))
        if theme in {"sf_state_boundary", "sf_rate_construction"}:
            membership["b_target"].add(letter_id)
        if theme in {"sf_state_boundary", "dx_specificity"}:
            membership["c_target"].add(letter_id)
        if theme == "rx_current_regimen":
            membership["rx_nontarget"].add(letter_id)
        if theme == "annotation_or_empty_gold" or row.get("empty_gold"):
            membership["empty_gold_diagnostic"].add(letter_id)
    return membership


def _letter_family_rows(
    *,
    gold: Sequence[Any],
    structured_path: Path,
    sf_direct_path: Path,
    assembly_jsonl: Path,
    variant: Mapping[str, Any],
    slice_membership: Mapping[str, set[str]],
) -> list[dict[str, Any]]:
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
    # Assembly rows already contain final mentions; rebuild via lanes if needed.
    if not joint_final:
        raise ValueError("assembly jsonl produced no predictions")

    # Prefer lane-assembled clinical_headline surface by converting assembly
    # predicted_mentions (already joint final).
    out: list[dict[str, Any]] = []
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
            out.append(
                {
                    "schema_version": "exectv2.luna_prompt_variants_dev140.v1",
                    "variant": variant["slug"],
                    "prompt_version": variant["prompt_version"],
                    "letter_id": letter.letter_id,
                    "family": family,
                    "model_owned_correct": source_keys == gold_keys,
                    "joint_final_correct": final_keys == gold_keys,
                    "empty_gold": len(gold_keys) == 0,
                    "model_owned_keys": _counter_rows(source_keys),
                    "joint_final_keys": _counter_rows(final_keys),
                    "family_local_gold_keys": _counter_rows(gold_keys),
                    "b_target": letter.letter_id in slice_membership["b_target"],
                    "c_target": letter.letter_id in slice_membership["c_target"],
                    "rx_nontarget": letter.letter_id in slice_membership["rx_nontarget"],
                    "empty_gold_diagnostic": letter.letter_id
                    in slice_membership["empty_gold_diagnostic"],
                }
            )
    return out


def _letters_from_producer(
    rows_by_id: Mapping[str, dict[str, Any]],
    family: str,
) -> dict[str, Any]:
    predictions = predictions_from_rows(list(rows_by_id.values()), "predicted_mentions")
    return {
        prediction.letter_id: to_exect_letter(prediction) for prediction in predictions
    }


def _counter_rows(counter: Counter[Any]) -> list[dict[str, Any]]:
    rows = [{"key": _jsonable(key), "count": count} for key, count in counter.items()]
    return sorted(rows, key=lambda row: json.dumps(row["key"], sort_keys=True))


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _variant_summary(
    *,
    slug: str,
    variant: Mapping[str, Any],
    assembly_report: Mapping[str, Any],
    letter_rows: Sequence[Mapping[str, Any]],
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    headline = assembly_report["score_ladder"]["headline_target"]

    def _correct_counts(field: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for family in FAMILIES:
            rows = [row for row in letter_rows if row["family"] == family]
            out[family] = sum(1 for row in rows if row[field])
        return out

    sf_rows = [
        row for row in letter_rows if row["family"] == SEIZURE_FREQUENCY.name
    ]
    nonempty_sf = [row for row in sf_rows if not row["empty_gold"]]
    b_sf = [
        row
        for row in sf_rows
        if row["b_target"] and not row["empty_gold"]
    ]
    return {
        "slug": slug,
        "prompt_version": variant["prompt_version"],
        "call_mode": provenance.get("call_mode"),
        "joint_headline_f1": float(headline["overall"]["f1"]),
        "joint_family_f1": {
            family: float(headline["by_indicator"][family]["f1"]) for family in FAMILIES
        },
        "model_owned_letter_correct": _correct_counts("model_owned_correct"),
        "joint_letter_correct": _correct_counts("joint_final_correct"),
        "sf_nonempty_model_owned_correct": sum(
            1 for row in nonempty_sf if row["model_owned_correct"]
        ),
        "sf_nonempty_total": len(nonempty_sf),
        "b_target_sf_model_owned_correct": sum(
            1 for row in b_sf if row["model_owned_correct"]
        ),
        "b_target_sf_total": len(b_sf),
        "provenance": provenance,
    }


def _comparison_vs_a(summaries: Mapping[str, Any]) -> dict[str, Any]:
    if "A_v0924_control" not in summaries:
        return {}
    base = summaries["A_v0924_control"]
    out: dict[str, Any] = {}
    for slug, item in summaries.items():
        if slug == "A_v0924_control":
            continue
        out[slug] = {
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
            "delta_sf_nonempty_model_owned_correct": (
                item["sf_nonempty_model_owned_correct"]
                - base["sf_nonempty_model_owned_correct"]
            ),
            "delta_b_target_sf_model_owned_correct": (
                item["b_target_sf_model_owned_correct"]
                - base["b_target_sf_model_owned_correct"]
            ),
            "delta_dx_joint_correct": (
                item["joint_letter_correct"][DIAGNOSIS.name]
                - base["joint_letter_correct"][DIAGNOSIS.name]
            ),
        }
    return out


def _render_report(summary: Mapping[str, Any]) -> str:
    lines = [
        "# ExECTv2 Luna prompt variants on `dev140`",
        "",
        f"Date: {summary['generated_on']}",
        "Status: development panel",
        f"Protocol: [{Path(str(summary['protocol'])).name}]({Path(str(summary['protocol'])).name})",
        "",
        "## Results",
        "",
        "| Variant | Overall F1 (default repair) | SF model-owned correct | SF final correct | SF nonempty model-owned | B-target SF model-owned |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for slug, item in summary["variants"].items():
        lines.append(
            "| "
            + " | ".join(
                [
                    slug,
                    f"{item['joint_headline_f1']:.4f}",
                    str(item["model_owned_letter_correct"][SEIZURE_FREQUENCY.name]),
                    str(item["joint_letter_correct"][SEIZURE_FREQUENCY.name]),
                    f"{item['sf_nonempty_model_owned_correct']}/{item['sf_nonempty_total']}",
                    f"{item['b_target_sf_model_owned_correct']}/{item['b_target_sf_total']}",
                ]
            )
            + " |"
        )
    if summary.get("comparison_vs_A"):
        lines.extend(
            [
                "",
                "## Deltas versus A",
                "",
                "| Variant | Δ joint F1 | Δ SF model-owned | Δ SF joint | Δ SF nonempty model-owned | Δ B-target SF | Δ Dx joint |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for slug, item in summary["comparison_vs_A"].items():
            lines.append(
                "| "
                + " | ".join(
                    [
                        slug,
                        f"{item['delta_joint_headline_f1']:+.4f}",
                        f"{item['delta_sf_model_owned_correct']:+d}",
                        f"{item['delta_sf_joint_correct']:+d}",
                        f"{item['delta_sf_nonempty_model_owned_correct']:+d}",
                        f"{item['delta_b_target_sf_model_owned_correct']:+d}",
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
            str(summary["claim_boundary"]),
            "",
        ]
    )
    return "\n".join(lines)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
