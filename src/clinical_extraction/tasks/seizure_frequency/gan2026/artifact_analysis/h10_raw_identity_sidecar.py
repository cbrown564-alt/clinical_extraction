"""Reusable H10 raw-output identity sidecar for saved Gan 2026 artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

POLICY_NAME = "gan2026_h10_raw_identity_sidecar_v1"
DEFAULT_ARTIFACT_PATHS = (
    Path("experiments/gan2026_llm_replacement_postprocessing_ablation_validation250_v0_2026-06-02.jsonl"),
    Path(
        "experiments/"
        "gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_"
        "conservative_live_2026-06-03.jsonl"
    ),
    Path(
        "experiments/"
        "gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_"
        "deterministic_safety_floor_v2_replay_2026-06-03.jsonl"
    ),
)
DEFAULT_PAIR_LEFT_PATH = DEFAULT_ARTIFACT_PATHS[1]
DEFAULT_PAIR_RIGHT_PATH = DEFAULT_ARTIFACT_PATHS[2]
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_h10_raw_identity_sidecar_v1_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_h10_raw_identity_sidecar_v1_2026-06-05.md"
)
RAW_FIELDS = (
    "raw_output",
    "llm_candidate_raw_output",
    "adjudicator_raw_output",
)
PROMPT_FIELDS = (
    "prompt_version",
    "pipeline_name",
    "pipeline_family",
    "split",
    "split_manifest",
)


def build_h10_raw_identity_sidecar(
    *,
    artifact_paths: Sequence[Path] = DEFAULT_ARTIFACT_PATHS,
    pair_left_path: Path = DEFAULT_PAIR_LEFT_PATH,
    pair_right_path: Path = DEFAULT_PAIR_RIGHT_PATH,
) -> dict[str, Any]:
    """Build H10 provenance summary over saved artifacts."""

    artifact_summaries = [_artifact_summary(path) for path in artifact_paths]
    pair_identity = _paired_identity_summary(pair_left_path, pair_right_path)
    return {
        "artifact_kind": "gan2026_h10_raw_identity_sidecar_v1",
        "policy_name": POLICY_NAME,
        "date": "2026-06-05",
        "split_manifest": "gan2026_split_v1",
        "artifact_summaries": artifact_summaries,
        "paired_identity": pair_identity,
        "claim_boundary": (
            "H10 provenance sidecar only. It makes no model calls, changes no "
            "predictions, writes no row-level output artifact, and uses no "
            "locked-test row-level failures."
        ),
        "decision": (
            "raw_identity_sidecar_ready"
            if artifact_summaries and pair_identity["matched_rows"] > 0
            else "raw_identity_sidecar_incomplete"
        ),
        "recommended_next_step": (
            "Use this sidecar as the H10 provenance prerequisite before "
            "boundary_event_contract_v1 and any later live/replay comparison."
        ),
    }


def write_outputs(artifact: Mapping[str, Any], json_path: Path, report_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(artifact, report_path)


def write_report(artifact: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 H10 Raw Identity Sidecar v1",
        "",
        str(artifact["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(artifact["decision"]),
        "",
        "## Artifact Summaries",
        "",
        "| Artifact | Rows | SHA-256 | Raw fields present |",
        "| --- | ---: | --- | ---: |",
    ]
    for summary in artifact["artifact_summaries"]:
        lines.append(
            f"| `{summary['path']}` | {summary['row_count']} | "
            f"`{summary['sha256']}` | {summary['raw_fields_present_rows']} |"
        )
    pair = artifact["paired_identity"]
    lines.extend(
        [
            "",
            "## Paired Identity",
            "",
            f"Left: `{pair['left_path']}`",
            "",
            f"Right: `{pair['right_path']}`",
            "",
            f"Matched rows: {pair['matched_rows']}.",
            "",
            "| Field | Present pairs | Identical pairs | Identity rate |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for field, summary in pair["raw_field_identity"].items():
        lines.append(
            f"| `{field}` | {summary['present_pairs']} | "
            f"{summary['identical_pairs']} | {summary['identity_rate']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(artifact["recommended_next_step"]),
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def materialize_h10_raw_identity_sidecar(
    *,
    artifact_paths: Sequence[Path] = DEFAULT_ARTIFACT_PATHS,
    pair_left_path: Path = DEFAULT_PAIR_LEFT_PATH,
    pair_right_path: Path = DEFAULT_PAIR_RIGHT_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    artifact = build_h10_raw_identity_sidecar(
        artifact_paths=artifact_paths,
        pair_left_path=pair_left_path,
        pair_right_path=pair_right_path,
    )
    artifact = {
        **artifact,
        "json_artifact": str(output_json_path),
        "report_artifact": str(output_report_path),
    }
    write_outputs(artifact, output_json_path, output_report_path)
    return artifact


def _artifact_summary(path: Path) -> dict[str, Any]:
    rows = _load_rows(path)
    raw_present = {
        field: sum(field in row and row.get(field) is not None for row in rows)
        for field in RAW_FIELDS
    }
    reuse_counts = Counter()
    for row in rows:
        for key, value in row.items():
            if key.startswith("reused_"):
                reuse_counts[f"{key}={bool(value)}"] += 1
    score_layer_counts = Counter(
        layer for row in rows for layer in (row.get("score_layers") or {})
    )
    return {
        "path": str(path),
        "sha256": _file_sha256(path),
        "row_count": len(rows),
        "source_row_count": len(
            {int(row["source_row_index"]) for row in rows if "source_row_index" in row}
        ),
        "raw_field_present_counts": dict(sorted(raw_present.items())),
        "raw_fields_present_rows": sum(
            any(row.get(field) is not None for field in RAW_FIELDS) for row in rows
        ),
        "reuse_flag_counts": dict(sorted(reuse_counts.items())),
        "prompt_field_counts": {
            field: dict(sorted(Counter(str(row.get(field)) for row in rows).items()))
            for field in PROMPT_FIELDS
            if any(field in row for row in rows)
        },
        "score_layer_counts": dict(sorted(score_layer_counts.items())),
    }


def _paired_identity_summary(left_path: Path, right_path: Path) -> dict[str, Any]:
    left_rows = _rows_by_source_index(_load_rows(left_path))
    right_rows = _rows_by_source_index(_load_rows(right_path))
    matched = sorted(set(left_rows) & set(right_rows))
    raw_identity = {}
    for field in RAW_FIELDS:
        present = sum(
            left_rows[index].get(field) is not None
            and right_rows[index].get(field) is not None
            for index in matched
        )
        identical = sum(
            left_rows[index].get(field) == right_rows[index].get(field)
            for index in matched
            if left_rows[index].get(field) is not None
            and right_rows[index].get(field) is not None
        )
        raw_identity[field] = {
            "present_pairs": present,
            "identical_pairs": identical,
            "identity_rate": identical / present if present else 0.0,
        }
    return {
        "left_path": str(left_path),
        "right_path": str(right_path),
        "left_sha256": _file_sha256(left_path),
        "right_sha256": _file_sha256(right_path),
        "matched_rows": len(matched),
        "left_only_rows": len(set(left_rows) - set(right_rows)),
        "right_only_rows": len(set(right_rows) - set(left_rows)),
        "raw_field_identity": raw_identity,
    }


def _load_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix == ".jsonl":
        return load_jsonl_rows(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict) and isinstance(data.get("rows"), list):
        return [row for row in data["rows"] if isinstance(row, dict)]
    if isinstance(data, dict):
        return [data]
    raise ValueError(f"Unsupported artifact shape for {path}")


def _rows_by_source_index(rows: Sequence[Mapping[str, Any]]) -> dict[int, Mapping[str, Any]]:
    return {int(row["source_row_index"]): row for row in rows if "source_row_index" in row}


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact-path",
        type=Path,
        action="append",
        dest="artifact_paths",
        default=None,
    )
    parser.add_argument("--pair-left-path", type=Path, default=DEFAULT_PAIR_LEFT_PATH)
    parser.add_argument("--pair-right-path", type=Path, default=DEFAULT_PAIR_RIGHT_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    artifact = materialize_h10_raw_identity_sidecar(
        artifact_paths=args.artifact_paths or DEFAULT_ARTIFACT_PATHS,
        pair_left_path=args.pair_left_path,
        pair_right_path=args.pair_right_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {
                "decision": artifact["decision"],
                "matched_rows": artifact["paired_identity"]["matched_rows"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
