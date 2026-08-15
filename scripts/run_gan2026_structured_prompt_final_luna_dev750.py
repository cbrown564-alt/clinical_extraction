"""Luna-only Gan final-prompt study on all 750 Gan development rows."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    map_pragmatic,
    map_purist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import hybrid_structured_events

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = (
    REPO_ROOT / "scratch/validation/gan2026_structured_prompt_final_luna_dev750_20260815"
)
PANEL_PATH = REPO_ROOT / "experiments/gan2026_structured_prompt_final_luna_dev750_20260815.json"
REPORT_PATH = (
    REPO_ROOT / "docs/research/gan2026/structured_prompt_final_luna_dev750_2026-08-15.md"
)
PROTOCOL = "docs/research/gan2026/structured_prompt_final_luna_dev750_protocol_2026-08-15.md"
MODEL = "openai/gpt-5.6-luna"
EXPECTED_FINAL_CONTRACT_SHA256 = (
    "171d15bc6d3c2fb178e5ba0d713e75d008d31aceabe25d0163e0c8457a9ebb1d"
)
LARGE_DROP_HYBRID_PURIST = -15
TRANSPORT_ERROR_MARKERS = (
    "Connection error",
    "InternalServerError",
    "APIConnectionError",
    "Timeout",
    "RateLimitError",
    "ServiceUnavailable",
)
DEV20_V05 = (
    REPO_ROOT
    / "experiments/gan2026_structured_prompt_final_luna_dev20_20260815"
    / "v05_control"
    / "validation20.rows.jsonl"
)
DEV20_FINAL = (
    REPO_ROOT
    / "experiments/gan2026_structured_prompt_final_luna_dev20_20260815"
    / "final_live"
    / "validation20.rows.jsonl"
)
CONTROL_CANDIDATES = (
    REPO_ROOT
    / "scratch/validation/gan2026_luna_prompt_variants_dev750_20260730"
    / "A_v05_control"
    / "validation750.rows.jsonl",
    REPO_ROOT
    / "scratch/validation/gan2026_matched_v05_dev750_20260727"
    / "gpt56luna"
    / "validation750.rows.jsonl",
    DEV20_V05,
)
ESCALATION_REASON = (
    "Predeclared Luna-only Gan final-prompt envelope study on all 750 "
    "dev750 rows under docs/research/gan2026/"
    "structured_prompt_final_luna_dev750_protocol_2026-08-15.md"
)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--progress-every", type=int, default=5)
    parser.add_argument("--api-base")
    parser.add_argument(
        "--arm",
        choices=("v05_control", "final_live", "both"),
        default="both",
    )
    parser.add_argument(
        "--finalize-only",
        action="store_true",
        help="Score existing row files and write the panel/report only.",
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_study(
                overwrite=args.overwrite,
                progress_every=args.progress_every,
                api_base=args.api_base,
                arm=args.arm,
                finalize_only=args.finalize_only,
            ),
            indent=2,
            sort_keys=True,
        )
    )


def run_study(
    *,
    overwrite: bool,
    progress_every: int,
    api_base: str | None,
    arm: str = "both",
    finalize_only: bool = False,
) -> dict[str, Any]:
    records = list(load_records_for_split("validation"))
    if len(records) != 750:
        raise ValueError(f"expected 750 validation rows, found {len(records)}")
    records.sort(key=lambda record: int(record.source_row_index))
    wanted = [int(record.source_row_index) for record in records]
    if len(set(wanted)) != 750:
        raise RuntimeError("validation split must have 750 unique source_row_index values")

    contract = _final_contract_hash()
    if contract != EXPECTED_FINAL_CONTRACT_SHA256:
        raise RuntimeError(
            "final instruction/schema/task contract drifted: "
            f"got {contract}, expected {EXPECTED_FINAL_CONTRACT_SHA256}"
        )
    _assert_final_payload(records[0])
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()

    control: dict[str, Any] | None = None
    candidate: dict[str, Any] | None = None
    if arm in {"v05_control", "both"}:
        control = _run_arm(
            slug="v05_control",
            prompt_version=hybrid_structured_events.PROMPT_VERSION_V0_5,
            records=records,
            overwrite=overwrite,
            progress_every=progress_every,
            api_base=api_base,
            reuse_raws=_control_raws(wanted),
            finalize_only=finalize_only,
        )
    if arm in {"final_live", "both"}:
        candidate = _run_arm(
            slug="final_live",
            prompt_version=hybrid_structured_events.PROMPT_VERSION_FINAL,
            records=records,
            overwrite=overwrite,
            progress_every=progress_every,
            api_base=api_base,
            reuse_raws=_final_reuse_raws(wanted),
            finalize_only=finalize_only,
        )

    if control is None or candidate is None:
        return {
            "state": "partial",
            "arm": arm,
            "control_rows": None if control is None else control["summary"]["rows"],
            "candidate_rows": None if candidate is None else candidate["summary"]["rows"],
        }

    if control["summary"]["rows"] != 750 or candidate["summary"]["rows"] != 750:
        return {
            "state": "incomplete",
            "control_rows": control["summary"]["rows"],
            "candidate_rows": candidate["summary"]["rows"],
            "control_path": control["path"],
            "candidate_path": candidate["path"],
        }

    comparison = _compare_arms(control, candidate, records)
    artifact = {
        "schema_version": "gan2026.structured_prompt_final_luna_dev750.v1",
        "generated_on": "2026-08-15",
        "protocol": PROTOCOL,
        "decision": "docs/decisions/0053-gan-structured-events-final-prompt.md",
        "model": MODEL,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "row_count": 750,
        "repair_mode": "hybrid_full_stack",
        "temperature": 1,
        "max_tokens": 10000,
        "dspy_cache": False,
        "replay_mode": {
            "v05_control": control["call_mode"],
            "final_live": candidate["call_mode"],
        },
        "control_source": control.get("reuse_source"),
        "final_reuse_source": candidate.get("reuse_source"),
        "reused_vs_live": {
            "v05_control": {
                "reused": control["reused"],
                "live": control["live"],
            },
            "final_live": {
                "reused": candidate["reused"],
                "live": candidate["live"],
            },
        },
        "final_contract_sha256": contract,
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "arms": {
            "v05_control": control["summary"],
            "final_live": candidate["summary"],
        },
        "hybrid_purist_by_gold_kind": comparison["hybrid_purist_by_gold_kind"],
        "comparison": {
            key: value
            for key, value in comparison.items()
            if key != "hybrid_purist_by_gold_kind"
        },
        "claim_boundary": (
            "Gan Luna 750-row development comparison of the final envelope "
            "against v0.5. Envelope hygiene only. Not holdout, not a selected "
            "prompt, and not a six-model ranking."
        ),
    }
    PANEL_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(_render_report(artifact), encoding="utf-8")
    return {
        "state": "complete",
        "artifact": PANEL_PATH.relative_to(REPO_ROOT).as_posix(),
        "report": REPORT_PATH.relative_to(REPO_ROOT).as_posix(),
        "control_mode": control["call_mode"],
        "candidate_mode": candidate["call_mode"],
        "hybrid_purist_delta": comparison["hybrid_purist_delta"],
        "large_drop": comparison["large_drop"],
    }


def _assert_final_payload(record: GanFrequencyRecord) -> None:
    raw = hybrid_structured_events.build_prompt_input(
        record,
        prompt_version=hybrid_structured_events.PROMPT_VERSION_FINAL,
    )
    payload = json.loads(raw)
    blob = json.dumps(payload)
    if "prompt_version" in payload or "source_row_index" in payload:
        raise RuntimeError("final payload still contains envelope identity")
    if "Gan 2026" in blob or "LLM-only" in blob or "gan2026_hybrid_structured_events" in blob:
        raise RuntimeError("final payload still contains internal language")
    baseline = json.loads(
        hybrid_structured_events.build_prompt_input(
            record,
            prompt_version=hybrid_structured_events.PROMPT_VERSION_V0_5,
        )
    )
    if payload["instructions"] != baseline["instructions"]:
        raise RuntimeError("final instructions drifted from v0.5")


def _final_contract_hash() -> str:
    record = load_records_for_split("validation")[0]
    payload = json.loads(
        hybrid_structured_events.build_prompt_input(
            record,
            prompt_version=hybrid_structured_events.PROMPT_VERSION_FINAL,
        )
    )
    subset = {
        key: payload[key]
        for key in ("task", "instructions", "event_schema", "selection_schema")
    }
    return hashlib.sha256(
        json.dumps(subset, ensure_ascii=False, sort_keys=True).encode()
    ).hexdigest()


def _raws_from_path(
    path: Path, wanted: Sequence[int], prompt_version: str
) -> dict[int, str] | None:
    if not path.is_file():
        return None
    rows = load_jsonl_rows(path)
    versions = {str(row.get("prompt_version")) for row in rows}
    if versions != {prompt_version}:
        return None
    raws = {
        int(row["source_row_index"]): str(row["raw_output"])
        for row in rows
        if str(row.get("raw_output") or "").strip()
        and int(row["source_row_index"]) in set(wanted)
    }
    return raws or None


def _control_raws(wanted: Sequence[int]) -> tuple[dict[int, str], str] | None:
    needed = set(wanted)
    for path in CONTROL_CANDIDATES:
        raws = _raws_from_path(path, wanted, hybrid_structured_events.PROMPT_VERSION_V0_5)
        if raws is None:
            continue
        source = path.relative_to(REPO_ROOT).as_posix()
        if needed <= set(raws):
            return raws, source
        if path == DEV20_V05 and raws:
            return raws, source
    return None


def _final_reuse_raws(wanted: Sequence[int]) -> tuple[dict[int, str], str] | None:
    raws = _raws_from_path(
        DEV20_FINAL, wanted, hybrid_structured_events.PROMPT_VERSION_FINAL
    )
    if raws is None:
        return None
    return raws, DEV20_FINAL.relative_to(REPO_ROOT).as_posix()


def _gold_bucket(record: GanFrequencyRecord) -> str:
    label = record.gold_label.lower()
    if "cluster" in label:
        return "cluster"
    return str(record.gold_label_kind)


def _run_arm(
    *,
    slug: str,
    prompt_version: str,
    records: Sequence[GanFrequencyRecord],
    overwrite: bool,
    progress_every: int,
    api_base: str | None,
    reuse_raws: tuple[dict[int, str], str] | None,
    finalize_only: bool,
) -> dict[str, Any]:
    out_dir = OUTPUT_ROOT / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    rows_path = out_dir / "validation750.rows.jsonl"
    wanted = [int(record.source_row_index) for record in records]
    reuse_raw_outputs: dict[int, str] = {}
    reuse_source: str | None = None
    if reuse_raws is not None:
        reuse_raw_outputs, reuse_source = reuse_raws

    existing_rows: list[dict[str, Any]] = []
    if rows_path.exists() and not overwrite:
        existing_rows = [
            row
            for row in load_jsonl_rows(rows_path)
            if not _is_transport_error(row.get("call_error"))
        ]
        existing_idx = {int(row["source_row_index"]) for row in existing_rows}
        if existing_idx == set(wanted) and len(existing_rows) == 750:
            return _arm_result(
                slug=slug,
                prompt_version=prompt_version,
                rows=existing_rows,
                reuse_source=reuse_source,
                path=rows_path,
            )
        remaining = [
            record
            for record in records
            if int(record.source_row_index) not in existing_idx
        ]
    else:
        remaining = list(records)

    if finalize_only:
        return _arm_result(
            slug=slug,
            prompt_version=prompt_version,
            rows=existing_rows,
            reuse_source=reuse_source,
            path=rows_path,
        )

    remaining_reuse = {
        index: raw
        for index, raw in reuse_raw_outputs.items()
        if index in {int(record.source_row_index) for record in remaining}
    }
    live_needed = [
        record
        for record in remaining
        if int(record.source_row_index) not in remaining_reuse
    ]
    mode: str = "prompt-only" if not live_needed else "live"

    original = hybrid_structured_events.PROMPT_VERSION
    try:
        hybrid_structured_events.set_active_prompt_version(prompt_version)
        if mode == "live":
            print(f"ESCALATION_REASON={ESCALATION_REASON}", flush=True)
            print(
                f"{slug}: remaining={len(remaining)} reused={len(remaining_reuse)} "
                f"live={len(live_needed)}",
                flush=True,
            )
        checkpoint_jsonl = rows_path.with_suffix(".resume-part.jsonl")
        checkpoint_report = rows_path.with_suffix(".resume-part.md")
        fresh_rows, _metadata = (
            hybrid_structured_events.run_split(
                remaining,
                split="validation",
                split_manifest="gan2026_split_v1",
                model=MODEL,
                temperature=1.0,
                max_tokens=10000,
                mode=mode,  # type: ignore[arg-type]
                dspy_cache=False,
                api_base=api_base,
                reuse_raw_outputs=remaining_reuse or None,
                reuse_source=reuse_source,
                escalation_reason=ESCALATION_REASON,
                progress_every=progress_every,
                checkpoint_jsonl_path=checkpoint_jsonl,
                checkpoint_report_path=checkpoint_report,
                repair_config=hybrid_structured_events.StructuredRepairConfig.for_mode(
                    "hybrid_full_stack"
                ),
            )
            if remaining
            else ([], {})
        )
        by_index = {int(row["source_row_index"]): row for row in existing_rows}
        for row in fresh_rows:
            by_index[int(row["source_row_index"])] = row
        transport_retries = 0
        while transport_retries < 3:
            retry_records = [
                record
                for record in records
                if _is_transport_error(
                    (by_index.get(int(record.source_row_index)) or {}).get("call_error")
                )
                or int(record.source_row_index) not in by_index
            ]
            retry_records = [
                record
                for record in retry_records
                if int(record.source_row_index)
                not in remaining_reuse
            ]
            if not retry_records:
                break
            transport_retries += 1
            print(
                f"{slug}: retry transport failures pass={transport_retries} "
                f"n={len(retry_records)}",
                flush=True,
            )
            retry_rows, _ = hybrid_structured_events.run_split(
                retry_records,
                split="validation",
                split_manifest="gan2026_split_v1",
                model=MODEL,
                temperature=1.0,
                max_tokens=10000,
                mode="live",
                dspy_cache=False,
                api_base=api_base,
                reuse_raw_outputs=None,
                reuse_source=reuse_source,
                escalation_reason=ESCALATION_REASON,
                progress_every=progress_every,
                checkpoint_jsonl_path=checkpoint_jsonl,
                checkpoint_report_path=checkpoint_report,
                repair_config=hybrid_structured_events.StructuredRepairConfig.for_mode(
                    "hybrid_full_stack"
                ),
            )
            for row in retry_rows:
                if not _is_transport_error(row.get("call_error")):
                    by_index[int(row["source_row_index"])] = row
        rows = [by_index[index] for index in wanted if index in by_index]
        write_jsonl_rows(rows, rows_path)
        checkpoint_jsonl.unlink(missing_ok=True)
        checkpoint_report.unlink(missing_ok=True)
    finally:
        hybrid_structured_events.set_active_prompt_version(original)
    return _arm_result(
        slug=slug,
        prompt_version=prompt_version,
        rows=rows,
        reuse_source=reuse_source,
        path=rows_path,
    )


def _is_transport_error(call_error: object) -> bool:
    text = str(call_error or "")
    return bool(text) and any(marker in text for marker in TRANSPORT_ERROR_MARKERS)


def _score_label(gold_monthly: float, label: str | None) -> dict[str, bool]:
    if not label:
        return {"purist": False, "pragmatic": False}
    try:
        predicted = label_to_frequency_record(label)
    except ValueError:
        return {"purist": False, "pragmatic": False}
    return {
        "purist": map_purist(predicted.monthly_frequency) == map_purist(gold_monthly),
        "pragmatic": map_pragmatic(predicted.monthly_frequency)
        == map_pragmatic(gold_monthly),
    }


def _row_scores(row: Mapping[str, Any]) -> dict[str, Any]:
    comparison = row.get("comparison") or {}
    gold_monthly = float((row.get("reference") or {})["gold_monthly_frequency"])
    structured = row.get("structured_record") or {}
    selection = structured.get("selection") or {}
    raw = _score_label(gold_monthly, selection.get("final_label"))
    return {
        "source_row_index": int(row["source_row_index"]),
        "gold_kind": (row.get("reference") or {}).get("gold_label_kind"),
        "call_error": bool(row.get("call_error")),
        "parse_failed": row.get("structured_record") is None,
        "reused_raw_output": bool(row.get("reused_raw_output")),
        "raw_purist": raw["purist"],
        "raw_pragmatic": raw["pragmatic"],
        "hybrid_purist": bool(comparison.get("purist_correct")),
        "hybrid_pragmatic": bool(comparison.get("pragmatic_correct")),
    }


def _arm_result(
    *,
    slug: str,
    prompt_version: str,
    rows: Sequence[Mapping[str, Any]],
    reuse_source: str | None,
    path: Path,
) -> dict[str, Any]:
    scored = [_row_scores(row) for row in rows]
    reused = sum(1 for row in scored if row["reused_raw_output"])
    live = len(scored) - reused
    if reused == len(scored) and scored:
        call_mode = "saved_raw_output_no_call"
    elif reused:
        call_mode = "mixed_reuse_and_live"
    else:
        call_mode = "live"
    return {
        "slug": slug,
        "prompt_version": prompt_version,
        "call_mode": call_mode,
        "reuse_source": reuse_source,
        "path": path.relative_to(REPO_ROOT).as_posix(),
        "reused": reused,
        "live": live,
        "rows": scored,
        "summary": {
            "rows": len(scored),
            "unique_source_rows": len({row["source_row_index"] for row in scored}),
            "call_failures": sum(1 for row in scored if row["call_error"]),
            "parse_failures": sum(1 for row in scored if row["parse_failed"]),
            "reused": reused,
            "live": live,
            "raw_purist": sum(1 for row in scored if row["raw_purist"]),
            "raw_pragmatic": sum(1 for row in scored if row["raw_pragmatic"]),
            "hybrid_purist": sum(1 for row in scored if row["hybrid_purist"]),
            "hybrid_pragmatic": sum(1 for row in scored if row["hybrid_pragmatic"]),
        },
    }


def _compare_arms(
    control: Mapping[str, Any],
    candidate: Mapping[str, Any],
    records: Sequence[GanFrequencyRecord],
) -> dict[str, Any]:
    control_by = {row["source_row_index"]: row for row in control["rows"]}
    candidate_by = {row["source_row_index"]: row for row in candidate["rows"]}
    flips = []
    kind_totals: Counter[str] = Counter()
    kind_control: Counter[str] = Counter()
    kind_candidate: Counter[str] = Counter()
    for record in records:
        index = int(record.source_row_index)
        left = control_by[index]
        right = candidate_by[index]
        bucket = _gold_bucket(record)
        kind_totals[bucket] += 1
        if left["hybrid_purist"]:
            kind_control[bucket] += 1
        if right["hybrid_purist"]:
            kind_candidate[bucket] += 1
        if left["hybrid_purist"] != right["hybrid_purist"]:
            flips.append(
                {
                    "source_row_index": index,
                    "gold_kind": bucket,
                    "v05_hybrid_purist": left["hybrid_purist"],
                    "final_hybrid_purist": right["hybrid_purist"],
                }
            )
    hybrid_delta = (
        int(candidate["summary"]["hybrid_purist"])
        - int(control["summary"]["hybrid_purist"])
    )
    by_kind = {
        kind: {
            "n": kind_totals[kind],
            "v05_hybrid_purist": kind_control[kind],
            "final_hybrid_purist": kind_candidate[kind],
            "delta": kind_candidate[kind] - kind_control[kind],
        }
        for kind in sorted(kind_totals)
    }
    lost = [
        item
        for item in flips
        if item["v05_hybrid_purist"] and not item["final_hybrid_purist"]
    ]
    gained = [
        item
        for item in flips
        if item["final_hybrid_purist"] and not item["v05_hybrid_purist"]
    ]
    return {
        "raw_purist_delta": int(candidate["summary"]["raw_purist"])
        - int(control["summary"]["raw_purist"]),
        "raw_pragmatic_delta": int(candidate["summary"]["raw_pragmatic"])
        - int(control["summary"]["raw_pragmatic"]),
        "hybrid_purist_delta": hybrid_delta,
        "hybrid_pragmatic_delta": int(candidate["summary"]["hybrid_pragmatic"])
        - int(control["summary"]["hybrid_pragmatic"]),
        "hybrid_purist_flips": flips,
        "hybrid_purist_lost": lost,
        "hybrid_purist_gained": gained,
        "large_drop": hybrid_delta <= LARGE_DROP_HYBRID_PURIST,
        "kind_counts": dict(kind_totals),
        "hybrid_purist_by_gold_kind": by_kind,
    }


def _render_report(artifact: Mapping[str, Any]) -> str:
    arms = artifact["arms"]
    comparison = artifact["comparison"]
    control = arms["v05_control"]
    candidate = arms["final_live"]
    reuse = artifact["reused_vs_live"]
    if comparison["large_drop"]:
        verdict = (
            "**large drop.** Stop. Inspect the `final` payload. Do not add "
            "clinical rules. Do not write a holdout protocol."
        )
    else:
        verdict = (
            "**not a large drop.** Report written. Decision 0043 / 0050 fills "
            "and `operational/gan.py` stay on `v0.5`. `test450` and the other "
            "five models stay closed."
        )
    flip_lines = "none"
    flips = comparison["hybrid_purist_flips"]
    if flips:
        flip_lines = "\n".join(
            f"- `{item['source_row_index']}` ({item['gold_kind']}): "
            f"v0.5 {item['v05_hybrid_purist']} → final {item['final_hybrid_purist']}"
            for item in flips
        )
    kind = artifact["hybrid_purist_by_gold_kind"]
    kind_rows = "\n".join(
        f"| {name} | {stats['n']} | {stats['v05_hybrid_purist']} | "
        f"{stats['final_hybrid_purist']} | {stats['delta']:+d} |"
        for name, stats in kind.items()
    )
    counts = [
        (
            "raw Purist",
            control["raw_purist"],
            candidate["raw_purist"],
            comparison["raw_purist_delta"],
        ),
        (
            "raw Pragmatic",
            control["raw_pragmatic"],
            candidate["raw_pragmatic"],
            comparison["raw_pragmatic_delta"],
        ),
        (
            "hybrid Purist",
            control["hybrid_purist"],
            candidate["hybrid_purist"],
            comparison["hybrid_purist_delta"],
        ),
        (
            "hybrid Pragmatic",
            control["hybrid_pragmatic"],
            candidate["hybrid_pragmatic"],
            comparison["hybrid_pragmatic_delta"],
        ),
    ]
    count_rows = "\n".join(
        f"| {name} | {left}/750 | {right}/750 | {delta:+d} |"
        for name, left, right, delta in counts
    )
    return "\n".join(
        [
            "# Luna `dev750` test of the Gan `final` prompt",
            "",
            "Date: 2026-08-15",
            "Status: complete",
            "Protocol: [final Luna `dev750` protocol]"
            "(structured_prompt_final_luna_dev750_protocol_2026-08-15.md)",
            "Decision: [0053](../../decisions/0053-gan-structured-events-final-prompt.md)",
            f"Model: `{artifact['model']}`",
            "Sample: all 750 Gan `dev750` rows; `test450` not touched",
            "",
            "## Verdict",
            "",
            verdict,
            "",
            "This is not a promotion and not a selected-fill rewrite.",
            "",
            "## Conditions",
            "",
            "| Item | Value |",
            "| :--- | :--- |",
            f"| Control | `{artifact['replay_mode']['v05_control']}` "
            f"`{hybrid_structured_events.PROMPT_VERSION_V0_5}` |",
            f"| Control source | `{artifact['control_source'] or 'live v0.5'}` |",
            f"| Control reused / live | {reuse['v05_control']['reused']} / "
            f"{reuse['v05_control']['live']} |",
            f"| Candidate | `{artifact['replay_mode']['final_live']}` "
            f"`{hybrid_structured_events.PROMPT_VERSION_FINAL}` |",
            f"| Candidate reuse source | `{artifact['final_reuse_source'] or 'none'}` |",
            f"| Candidate reused / live | {reuse['final_live']['reused']} / "
            f"{reuse['final_live']['live']} |",
            "| Repair | `hybrid_full_stack` |",
            "| Scorer | Gan Purist primary; Pragmatic secondary |",
            "| Gold at prompt-build time | forbidden |",
            "| Holdout | not touched |",
            f"| `final` contract SHA-256 | `{artifact['final_contract_sha256']}` |",
            "",
            "## Counts on the 750-row pool",
            "",
            "| Surface | v0.5 | final | delta |",
            "| :--- | ---: | ---: | ---: |",
            count_rows,
            "",
            f"Call failures: v0.5 {control['call_failures']}, "
            f"final {candidate['call_failures']}.",
            f"Parse failures: v0.5 {control['parse_failures']}, "
            f"final {candidate['parse_failures']}.",
            "",
            "## Hybrid Purist by gold-kind pool",
            "",
            "| Kind | n | v0.5 | final | delta |",
            "| :--- | ---: | ---: | ---: | ---: |",
            kind_rows,
            "",
            "## Hybrid Purist flips",
            "",
            flip_lines,
            "",
            "## Boundary",
            "",
            "Development only. Luna versus Luna. Envelope hygiene, not a "
            "prompt-policy study. Not a six-model ranking. Not holdout "
            "evidence. Not a selected-fill rewrite. Decision 0043 / 0050 "
            "fills stay on `v0.5`.",
            "",
        ]
    )


if __name__ == "__main__":
    main()
