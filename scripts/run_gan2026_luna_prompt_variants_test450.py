"""Run Luna-only Gan prompt-variant A/B/C on locked test450 (aggregate-only)."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import (
    convert_to_categories,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import hybrid_structured_events
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports import (
    llm_structured_events_report,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = (
    REPO_ROOT / "configs/gan2026/luna_prompt_variants_test450_20260730.json"
)
ESCALATION_REASON = (
    "Predeclared Luna-only Gan prompt-variant A/B/C aggregate-only test450 "
    "transfer check under docs/experiments/gan2026/"
    "gan2026_luna_prompt_variants_test450_protocol_2026-07-30.md"
)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Run or resume one variant")
    run_parser.add_argument(
        "--variant",
        required=True,
        choices=("A_v05_control", "B_luna_rate", "C_luna_current"),
    )
    run_parser.add_argument("--overwrite", action="store_true")

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
    if config.get("split") != "test":
        raise ValueError("config split must be test")
    if config.get("row_policy") != "aggregate_only":
        raise ValueError("config row_policy must be aggregate_only")
    if config.get("split_manifest") != "gan2026_split_v1":
        raise ValueError("config split_manifest drifted")
    if config.get("repair_mode") != "hybrid_full_stack":
        raise ValueError("config repair_mode must be hybrid_full_stack")
    if config.get("dspy_cache") is not False:
        raise ValueError("config must disable DSPy cache")
    if config.get("model") != "openai/gpt-5.6-luna":
        raise ValueError("config model must be openai/gpt-5.6-luna")
    if config.get("row_count") != 450:
        raise ValueError("config row_count must be 450")
    if not str(config.get("artifact_root", "")).startswith("scratch/holdout/"):
        raise ValueError("test450 artifacts must stay under scratch/holdout/")
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


def _rows_path(config: Mapping[str, Any], slug: str) -> Path:
    return _variant_dir(config, slug) / "rows.jsonl"


def _report_path(config: Mapping[str, Any], slug: str) -> Path:
    return _variant_dir(config, slug) / "report.md"


def _aggregate_path(config: Mapping[str, Any], slug: str) -> Path:
    return _variant_dir(config, slug) / "aggregate.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _aggregate_summary(summary: Mapping[str, Any]) -> dict[str, Any]:
    """Keep only aggregate fields safe to leave sealed storage."""

    return {
        "examples": int(summary.get("examples", 0)),
        "structured_records": int(summary.get("structured_records", 0)),
        "call_failures": int(summary.get("call_failures", 0)),
        "parse_or_validation_failures": int(
            summary.get("parse_or_validation_failures", 0)
        ),
        "evidence_valid": int(summary.get("evidence_valid", 0)),
        "purist_correct": int(summary.get("purist_correct", 0)),
        "purist_accuracy": float(summary.get("purist_accuracy", 0.0)),
        "pragmatic_correct": int(summary.get("pragmatic_correct", 0)),
        "pragmatic_accuracy": float(summary.get("pragmatic_accuracy", 0.0)),
        "repair_notes": int(summary.get("repair_notes", 0)),
        "reused_raw_outputs": int(summary.get("reused_raw_outputs", 0)),
    }


def _llm_only_purist_correct(rows: Sequence[Mapping[str, Any]]) -> int:
    correct = 0
    for row in rows:
        raw = (
            ((row.get("row_trace") or {}).get("model_prediction") or {}).get("record")
            or {}
        )
        selection = raw.get("selection") if isinstance(raw, Mapping) else None
        raw_label = (
            selection.get("final_label") if isinstance(selection, Mapping) else None
        )
        gold = (row.get("reference") or {}).get("gold_monthly_frequency")
        if raw_label is None or gold is None:
            continue
        try:
            predicted = float(label_to_frequency_record(str(raw_label)).monthly_frequency)
            if (
                convert_to_categories([predicted], method="purist")[0]
                == convert_to_categories([float(gold)], method="purist")[0]
            ):
                correct += 1
        except (TypeError, ValueError):
            continue
    return correct


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
        path = _rows_path(config, slug)
        agg_path = _aggregate_path(config, slug)
        if not path.exists():
            out["variants"][slug] = {"exists": False, "rows": 0}
            continue
        rows = load_jsonl_rows(path)
        payload: dict[str, Any] = {
            "exists": True,
            "rows": len(rows),
            "unique_source_rows": len({int(row["source_row_index"]) for row in rows}),
            "path": path.relative_to(REPO_ROOT).as_posix(),
            "sha256": _sha256(path),
        }
        if agg_path.exists():
            payload["aggregate"] = json.loads(agg_path.read_text(encoding="utf-8"))
        out["variants"][slug] = payload
    return out


def run_variant(
    config: Mapping[str, Any],
    *,
    variant_slug: str,
    overwrite: bool = False,
) -> dict[str, Any]:
    variant = _variant(config, variant_slug)
    prompt_version = str(variant["prompt_version"])
    snapshot = REPO_ROOT / str(variant["prompt_snapshot"])
    if not snapshot.is_file():
        raise FileNotFoundError(snapshot)
    hybrid_structured_events.set_active_prompt_version(prompt_version)

    records = load_records_for_split("test")
    expected_count = int(config["row_count"])
    if len(records) != expected_count:
        raise ValueError(f"test split has {len(records)} rows; expected {expected_count}")

    rows_path = _rows_path(config, variant_slug)
    report_path = _report_path(config, variant_slug)
    aggregate_path = _aggregate_path(config, variant_slug)
    rows_path.parent.mkdir(parents=True, exist_ok=True)

    existing_rows: list[dict[str, Any]] = []
    if rows_path.exists() and not overwrite:
        existing_rows = load_jsonl_rows(rows_path)
        existing_indices = {int(row["source_row_index"]) for row in existing_rows}
        if len(existing_rows) >= expected_count and len(existing_indices) >= expected_count:
            summary = _aggregate_summary(
                hybrid_structured_events.summarize_records(existing_rows)
            )
            return {
                "variant": variant_slug,
                "state": "already_complete",
                "row_policy": "aggregate_only",
                "rows": len(existing_rows),
                "summary": summary,
                "path": rows_path.relative_to(REPO_ROOT).as_posix(),
            }
        records = [
            record
            for record in records
            if int(record.source_row_index) not in existing_indices
        ]

    reuse_raw_outputs: dict[int, str] = {}
    reuse_source: str | None = None
    mode = "live"
    if variant["call_mode"] == "saved_raw_output_no_call":
        mode = "prompt-only"
        source = REPO_ROOT / str(variant["reuse_source"])
        if not source.is_file():
            raise FileNotFoundError(source)
        expected_sha = str(variant.get("reuse_source_sha256") or "")
        actual_sha = _sha256(source)
        if expected_sha and actual_sha != expected_sha:
            raise ValueError(
                f"reuse source hash mismatch: expected {expected_sha}, got {actual_sha}"
            )
        reuse_source = source.relative_to(REPO_ROOT).as_posix()
        source_rows = load_jsonl_rows(source)
        reuse_raw_outputs = {
            int(row["source_row_index"]): str(row["raw_output"])
            for row in source_rows
            if str(row.get("raw_output") or "").strip()
        }
        missing = [
            int(record.source_row_index)
            for record in records
            if int(record.source_row_index) not in reuse_raw_outputs
        ]
        if missing:
            raise ValueError(
                f"{variant_slug} missing reused raw outputs for {len(missing)} rows"
            )

    started = datetime.now(UTC)
    started_mono = time.perf_counter()
    manifest = load_split_manifest()
    checkpoint_jsonl = rows_path.with_suffix(".resume-part.jsonl")
    checkpoint_report = report_path.with_suffix(".resume-part.md")
    fresh_rows, metadata = (
        hybrid_structured_events.run_split(
            records,
            split="test",
            split_manifest=str(manifest.get("manifest_version", "gan2026_split_v1")),
            model=str(config["model"]),
            temperature=float(config["temperature"]),
            max_tokens=int(config["max_tokens"]),
            mode=mode,  # type: ignore[arg-type]
            dspy_cache=False,
            escalation_reason=ESCALATION_REASON,
            reuse_raw_outputs=reuse_raw_outputs or None,
            reuse_source=reuse_source,
            progress_every=10,
            checkpoint_jsonl_path=checkpoint_jsonl,
            checkpoint_report_path=checkpoint_report,
            repair_config=hybrid_structured_events.StructuredRepairConfig.for_mode(
                "hybrid_full_stack"
            ),
        )
        if records
        else ([], {"summary": {}})
    )

    by_index = {
        int(row["source_row_index"]): row for row in existing_rows if not overwrite
    }
    for row in fresh_rows:
        by_index[int(row["source_row_index"])] = row
    combined = [by_index[index] for index in sorted(by_index)]

    full_summary = hybrid_structured_events.summarize_records(combined)
    aggregate_summary = _aggregate_summary(full_summary)
    llm_only = _llm_only_purist_correct(combined)
    metadata = dict(metadata)
    metadata["summary"] = full_summary
    metadata["luna_prompt_variant"] = {
        "slug": variant_slug,
        "prompt_version": prompt_version,
        "prompt_snapshot_sha256": _sha256(snapshot),
        "call_mode": variant["call_mode"],
        "reuse_source": reuse_source,
        "existing_rows_resumed": len(existing_rows) if not overwrite else 0,
        "fresh_rows": len(fresh_rows),
        "combined_rows": len(combined),
        "row_policy": "aggregate_only",
    }
    metadata["run_started_at_utc"] = started.isoformat()
    metadata["elapsed_seconds"] = time.perf_counter() - started_mono

    hybrid_structured_events.write_jsonl(combined, rows_path)
    llm_structured_events_report.write_report(
        combined,
        metadata,
        report_path,
        jsonl_path=rows_path,
    )
    aggregate = {
        "schema_version": "gan2026.luna_prompt_variants_test450_aggregate.v1",
        "variant": variant_slug,
        "model": config["model"],
        "split": "test450",
        "row_policy": "aggregate_only",
        "prompt_version": prompt_version,
        "prompt_snapshot_sha256": _sha256(snapshot),
        "repair_mode": "hybrid_full_stack",
        "call_mode": variant["call_mode"],
        "reuse_source": reuse_source,
        "rows": len(combined),
        "unique_source_rows": len({int(row["source_row_index"]) for row in combined}),
        "llm_only_purist_correct": llm_only,
        "llm_with_rules_purist_correct": aggregate_summary["purist_correct"],
        "llm_with_rules_pragmatic_correct": aggregate_summary["pragmatic_correct"],
        "summary": aggregate_summary,
        "artifact": rows_path.relative_to(REPO_ROOT).as_posix(),
        "artifact_sha256": _sha256(rows_path),
        "elapsed_seconds": metadata["elapsed_seconds"],
        "claim_boundary": (
            "Aggregate-only Luna-versus-Luna test450 transfer evidence; "
            "not row-level analysis, clinical validation, or a six-model panel rewrite."
        ),
    }
    aggregate_path.write_text(
        json.dumps(aggregate, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    checkpoint_jsonl.unlink(missing_ok=True)
    checkpoint_report.unlink(missing_ok=True)
    hybrid_structured_events.set_active_prompt_version(
        hybrid_structured_events.PROMPT_VERSION_V0_5
    )
    return {
        "variant": variant_slug,
        "state": "complete" if len(combined) == expected_count else "partial",
        "row_policy": "aggregate_only",
        "rows": len(combined),
        "unique_source_rows": aggregate["unique_source_rows"],
        "llm_only_purist_correct": llm_only,
        "llm_with_rules_purist_correct": aggregate_summary["purist_correct"],
        "llm_with_rules_pragmatic_correct": aggregate_summary["pragmatic_correct"],
        "summary": aggregate_summary,
        "artifact_sha256": aggregate["artifact_sha256"],
        "elapsed_seconds": metadata["elapsed_seconds"],
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
        rows_path = _rows_path(config, slug)
        if not agg_path.exists() or not rows_path.exists():
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
                "unique_source_rows": aggregate["unique_source_rows"],
                "llm_only_purist_correct": aggregate["llm_only_purist_correct"],
                "llm_with_rules_purist_correct": aggregate[
                    "llm_with_rules_purist_correct"
                ],
                "llm_with_rules_pragmatic_correct": aggregate[
                    "llm_with_rules_pragmatic_correct"
                ],
                "call_failures": aggregate["summary"]["call_failures"],
                "parse_or_validation_failures": aggregate["summary"][
                    "parse_or_validation_failures"
                ],
                "evidence_valid": aggregate["summary"]["evidence_valid"],
                "artifact": aggregate["artifact"],
                "artifact_sha256": aggregate["artifact_sha256"],
            }
        )

    panel = {
        "schema_version": "gan2026.luna_prompt_variants_test450_panel.v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "protocol": config["protocol"],
        "configuration": DEFAULT_CONFIG.relative_to(REPO_ROOT).as_posix(),
        "dataset": config["dataset"],
        "split": "test450",
        "split_manifest": config["split_manifest"],
        "row_policy": "aggregate_only",
        "model": config["model"],
        "repair_mode": config["repair_mode"],
        "complete": len(conditions) == 3
        and all(item["rows"] == expected for item in conditions),
        "conditions": conditions,
        "claim_boundary": (
            "Aggregate-only Luna-versus-Luna test450 transfer evidence for the named "
            "prompts and repair stack; not clinical validation, row-level analysis, "
            "or a rewrite of the frozen six-model v0.5 panel."
        ),
    }
    out_dir = REPO_ROOT / "experiments" / "gan2026_luna_prompt_variants_test450_20260730"
    out_dir.mkdir(parents=True, exist_ok=True)
    panel_path = out_dir / "panel.json"
    panel_path.write_text(
        json.dumps(panel, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    report_lines = [
        "# Luna Gan prompt-variant A/B/C test450 panel",
        "",
        f"Generated: {panel['generated_at_utc']}",
        "Readout: aggregate-only",
        "",
        "| Variant | Prompt | Rows | LLM-only Purist | LLM+rules Purist | LLM+rules Pragmatic |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for item in conditions:
        report_lines.append(
            f"| {item['variant']} | `{item['prompt_version']}` | {item['rows']} | "
            f"{item['llm_only_purist_correct']}/{item['rows']} | "
            f"{item['llm_with_rules_purist_correct']}/{item['rows']} | "
            f"{item['llm_with_rules_pragmatic_correct']}/{item['rows']} |"
        )
    report_lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            panel["claim_boundary"],
            "",
            "No test-row identifiers, notes, predictions, or failure cases are "
            "reported.",
            "",
        ]
    )
    report_path = (
        REPO_ROOT
        / "docs/experiments/gan2026/"
        "gan2026_luna_prompt_variants_test450_2026-07-30.md"
    )
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    return {
        "panel": panel_path.relative_to(REPO_ROOT).as_posix(),
        "report": report_path.relative_to(REPO_ROOT).as_posix(),
        "complete": panel["complete"],
        "conditions": len(conditions),
        "row_policy": "aggregate_only",
    }


if __name__ == "__main__":
    main()
