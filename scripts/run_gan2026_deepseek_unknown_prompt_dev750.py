"""Run the DeepSeek hosted unknown prompt-variant A/U development comparison."""

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
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import hybrid_structured_events
from clinical_extraction.tasks.seizure_frequency.gan2026.reports import (
    llm_structured_events_report,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = (
    REPO_ROOT / "configs/gan2026/deepseek_unknown_prompt_dev750_20260731.json"
)
ESCALATION_REASON = (
    "Predeclared DeepSeek hosted unknown prompt A/U development comparison on "
    "validation750 under docs/experiments/gan2026/"
    "gan2026_deepseek_unknown_prompt_dev750_protocol_2026-07-31.md"
)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="DeepSeek A/U config JSON",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Run or resume one variant")
    run_parser.add_argument(
        "--variant",
        required=True,
        choices=("A_v05_control", "U_deepseek_unknown"),
    )
    run_parser.add_argument("--limit", type=int, default=None)
    run_parser.add_argument(
        "--row-ids-file",
        type=Path,
        default=None,
        help=(
            "Optional JSON file with a source_row_index list (or {source_row_indices: [...]}). "
            "Restricts the run to those validation rows; resume into the same artifact "
            "remains valid when later scaling to the full split."
        ),
    )
    run_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing complete artifact for this variant",
    )

    status_parser = sub.add_parser("status", help="Print per-variant row counts")
    status_parser.add_argument("--variant", default=None)

    finalize_parser = sub.add_parser(
        "finalize",
        help="Build the comparison panel when all variants are complete",
    )
    finalize_parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Write a partial panel from whatever variants exist",
    )

    args = parser.parse_args(argv)
    config = _load_config(args.config)
    if args.command == "run":
        result = run_variant(
            config,
            variant_slug=args.variant,
            limit=args.limit,
            row_ids_file=args.row_ids_file,
            overwrite=args.overwrite,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
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
    if config.get("split") != "validation":
        raise ValueError("config split must be validation")
    if config.get("split_manifest") != "gan2026_split_v1":
        raise ValueError("config split_manifest drifted")
    if config.get("repair_mode") != "hybrid_full_stack":
        raise ValueError("config repair_mode must be hybrid_full_stack")
    if config.get("dspy_cache") is not False:
        raise ValueError("config must disable DSPy cache")
    if config.get("model") != "deepseek/deepseek-v4-flash":
        raise ValueError("config model must be deepseek/deepseek-v4-flash")
    variants = config.get("variants")
    if not isinstance(variants, list) or len(variants) != 2:
        raise ValueError("config must declare exactly two variants")
    return config


def _variant(config: Mapping[str, Any], slug: str) -> dict[str, Any]:
    for item in config["variants"]:
        if item["slug"] == slug:
            return item
    raise ValueError(f"unknown variant: {slug}")


def _variant_dir(config: Mapping[str, Any], slug: str) -> Path:
    return REPO_ROOT / str(config["artifact_root"]) / slug


def _rows_path(config: Mapping[str, Any], slug: str) -> Path:
    return _variant_dir(config, slug) / "validation750.rows.jsonl"


def _report_path(config: Mapping[str, Any], slug: str) -> Path:
    return _variant_dir(config, slug) / "validation750.report.md"


def _provenance_path(config: Mapping[str, Any], slug: str) -> Path:
    return _variant_dir(config, slug) / "validation750.provenance.json"


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
        path = _rows_path(config, slug)
        if not path.exists():
            out["variants"][slug] = {"exists": False, "rows": 0}
            continue
        rows = load_jsonl_rows(path)
        out["variants"][slug] = {
            "exists": True,
            "rows": len(rows),
            "unique_source_rows": len({int(row["source_row_index"]) for row in rows}),
            "path": path.relative_to(REPO_ROOT).as_posix(),
            "sha256": _sha256(path),
        }
    return out


def _load_row_ids(path: Path) -> list[int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        raw = payload
    elif isinstance(payload, dict) and "source_row_indices" in payload:
        raw = payload["source_row_indices"]
    else:
        raise ValueError(
            f"{path}: expected a JSON list or an object with source_row_indices"
        )
    ids = [int(item) for item in raw]
    if not ids:
        raise ValueError(f"{path}: empty source_row_indices")
    if len(ids) != len(set(ids)):
        raise ValueError(f"{path}: duplicate source_row_indices")
    return ids


def run_variant(
    config: Mapping[str, Any],
    *,
    variant_slug: str,
    limit: int | None = None,
    row_ids_file: Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    variant = _variant(config, variant_slug)
    prompt_version = str(variant["prompt_version"])
    snapshot = REPO_ROOT / str(variant["prompt_snapshot"])
    if not snapshot.is_file():
        raise FileNotFoundError(snapshot)
    hybrid_structured_events.set_active_prompt_version(prompt_version)

    records = load_records_for_split("validation")
    row_ids_filter: list[int] | None = None
    if row_ids_file is not None:
        row_ids_filter = _load_row_ids(
            row_ids_file if row_ids_file.is_absolute() else REPO_ROOT / row_ids_file
        )
        wanted = set(row_ids_filter)
        records = [record for record in records if int(record.source_row_index) in wanted]
        missing = wanted - {int(record.source_row_index) for record in records}
        if missing:
            raise ValueError(
                f"{row_ids_file}: {len(missing)} ids not in validation750; "
                f"first={sorted(missing)[:5]}"
            )
        # Keep slice order stable and aligned with the ids file.
        by_index = {int(record.source_row_index): record for record in records}
        records = [by_index[index] for index in row_ids_filter]
    if limit is not None:
        records = records[:limit]
    expected_count = len(records)
    rows_path = _rows_path(config, variant_slug)
    report_path = _report_path(config, variant_slug)
    provenance_path = _provenance_path(config, variant_slug)
    rows_path.parent.mkdir(parents=True, exist_ok=True)

    existing_rows: list[dict[str, Any]] = []
    if rows_path.exists() and not overwrite:
        existing_rows = load_jsonl_rows(rows_path)
        existing_indices = {int(row["source_row_index"]) for row in existing_rows}
        if len(existing_rows) >= expected_count and len(existing_indices) >= expected_count:
            return {
                "variant": variant_slug,
                "state": "already_complete",
                "rows": len(existing_rows),
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
                f"{variant_slug} missing reused raw outputs for "
                f"{len(missing)} rows; first={missing[:5]}"
            )

    started = datetime.now(UTC)
    started_mono = time.perf_counter()
    manifest = load_split_manifest()
    checkpoint_jsonl = rows_path.with_suffix(".resume-part.jsonl")
    checkpoint_report = report_path.with_suffix(".resume-part.md")
    fresh_rows, metadata = (
        hybrid_structured_events.run_split(
            records,
            split="validation",
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
    if limit is None and len(combined) != int(config["row_count"]):
        # Partial resume is allowed; finalize enforces completeness.
        pass

    metadata = dict(metadata)
    metadata["summary"] = hybrid_structured_events.summarize_records(combined)
    metadata["deepseek_unknown_prompt_variant"] = {
        "slug": variant_slug,
        "prompt_version": prompt_version,
        "prompt_snapshot": variant["prompt_snapshot"],
        "prompt_snapshot_sha256": _sha256(snapshot),
        "call_mode": variant["call_mode"],
        "reuse_source": reuse_source,
        "row_ids_file": (
            None
            if row_ids_file is None
            else (
                (REPO_ROOT / row_ids_file).resolve().relative_to(REPO_ROOT).as_posix()
                if not row_ids_file.is_absolute()
                else (
                    row_ids_file.resolve().relative_to(REPO_ROOT).as_posix()
                    if REPO_ROOT in row_ids_file.resolve().parents
                    else str(row_ids_file)
                )
            )
        ),
        "row_ids_filter_n": len(row_ids_filter) if row_ids_filter is not None else None,
        "existing_rows_resumed": len(existing_rows) if not overwrite else 0,
        "fresh_rows": len(fresh_rows),
        "combined_rows": len(combined),
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
    provenance = {
        "schema_version": "gan2026.deepseek_unknown_prompt_variants_dev750_run.v1",
        "variant": variant_slug,
        "model": config["model"],
        "prompt_version": prompt_version,
        "prompt_snapshot_sha256": _sha256(snapshot),
        "repair_mode": "hybrid_full_stack",
        "call_mode": variant["call_mode"],
        "reuse_source": reuse_source,
        "rows": len(combined),
        "unique_source_rows": len({int(row["source_row_index"]) for row in combined}),
        "artifact": rows_path.relative_to(REPO_ROOT).as_posix(),
        "artifact_sha256": _sha256(rows_path),
        "summary": metadata["summary"],
        "elapsed_seconds": metadata["elapsed_seconds"],
        "claim_boundary": (
            "Development DeepSeek hosted A/U unknown-prompt comparison on validation750; "
            "not a six-model panel rewrite and not holdout evidence."
        ),
    }
    provenance_path.write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    checkpoint_jsonl.unlink(missing_ok=True)
    checkpoint_report.unlink(missing_ok=True)
    # Restore default prompt version for subsequent imports in the same process.
    hybrid_structured_events.set_active_prompt_version(
        hybrid_structured_events.PROMPT_VERSION_V0_5
    )
    return provenance


def finalize(
    config: Mapping[str, Any],
    *,
    allow_incomplete: bool = False,
) -> dict[str, Any]:
    expected = int(config["row_count"])
    conditions: list[dict[str, Any]] = []
    for variant in config["variants"]:
        slug = str(variant["slug"])
        path = _rows_path(config, slug)
        if not path.exists():
            if allow_incomplete:
                continue
            raise FileNotFoundError(f"missing variant artifact: {path}")
        rows = load_jsonl_rows(path)
        unique = {int(row["source_row_index"]) for row in rows}
        if not allow_incomplete and (
            len(rows) != expected or len(unique) != expected
        ):
            raise ValueError(
                f"{slug} incomplete: rows={len(rows)} unique={len(unique)} "
                f"expected={expected}"
            )
        summary = hybrid_structured_events.summarize_records(rows)
        # Dual readout: model boundary vs final.
        model_boundary_correct = 0
        final_correct = int(summary.get("purist_correct", 0))
        for row in rows:
            raw = (
                ((row.get("row_trace") or {}).get("model_prediction") or {}).get(
                    "record"
                )
                or {}
            )
            selection = raw.get("selection") if isinstance(raw, Mapping) else None
            raw_label = (
                selection.get("final_label") if isinstance(selection, Mapping) else None
            )
            gold = float((row.get("reference") or {}).get("gold_monthly_frequency"))
            if raw_label:
                try:
                    from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import (
                        convert_to_categories,
                    )
                    from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
                        label_to_frequency_record,
                    )

                    predicted = float(
                        label_to_frequency_record(str(raw_label)).monthly_frequency
                    )
                    if (
                        convert_to_categories([predicted], method="purist")[0]
                        == convert_to_categories([gold], method="purist")[0]
                    ):
                        model_boundary_correct += 1
                except (TypeError, ValueError):
                    pass
        conditions.append(
            {
                "variant": slug,
                "prompt_version": variant["prompt_version"],
                "call_mode": variant["call_mode"],
                "rows": len(rows),
                "unique_source_rows": len(unique),
                "llm_only_purist_correct": model_boundary_correct,
                "llm_with_rules_purist_correct": final_correct,
                "llm_with_rules_pragmatic_correct": int(
                    summary.get("pragmatic_correct", 0)
                ),
                "artifact": path.relative_to(REPO_ROOT).as_posix(),
                "artifact_sha256": _sha256(path),
                "summary": summary,
            }
        )

    panel = {
        "schema_version": "gan2026.deepseek_unknown_prompt_variants_dev750_panel.v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "protocol": config["protocol"],
        "configuration": DEFAULT_CONFIG.relative_to(REPO_ROOT).as_posix(),
        "dataset": config["dataset"],
        "split": "validation750",
        "split_manifest": config["split_manifest"],
        "row_policy": config["row_policy"],
        "model": config["model"],
        "repair_mode": config["repair_mode"],
        "complete": len(conditions) == 3
        and all(item["rows"] == expected for item in conditions),
        "conditions": conditions,
        "claim_boundary": (
            "Development DeepSeek hosted A/U unknown-prompt comparison on validation750; "
            "not a six-model ranking, clinical validation, or holdout result."
        ),
    }
    out_dir = REPO_ROOT / "experiments" / "gan2026_deepseek_unknown_prompt_variants_dev750_20260730"
    out_dir.mkdir(parents=True, exist_ok=True)
    panel_path = out_dir / "panel.json"
    panel_path.write_text(
        json.dumps(panel, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    report_lines = [
        "# DeepSeek unknown prompt-variant A/U panel",
        "",
        f"Generated: {panel['generated_at_utc']}",
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
        ]
    )
    report_path = (
        REPO_ROOT
        / "docs/experiments/gan2026/gan2026_deepseek_unknown_prompt_variants_dev750_2026-07-30.md"
    )
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    return {
        "panel": panel_path.relative_to(REPO_ROOT).as_posix(),
        "report": report_path.relative_to(REPO_ROOT).as_posix(),
        "complete": panel["complete"],
        "conditions": len(conditions),
    }


if __name__ == "__main__":
    main()
