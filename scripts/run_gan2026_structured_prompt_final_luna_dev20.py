"""Luna-only Gan final-prompt study on a frozen 20-row dev750 sample."""

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
STUDY_DIR = REPO_ROOT / "experiments/gan2026_structured_prompt_final_luna_dev20_20260815"
SAMPLE_PATH = STUDY_DIR / "sample.json"
PROTOCOL = "docs/research/gan2026/structured_prompt_final_protocol_2026-08-15.md"
MODEL = "openai/gpt-5.6-luna"
CONTROL_CANDIDATES = (
    REPO_ROOT
    / "scratch/validation/gan2026_luna_prompt_variants_dev750_20260730"
    / "A_v05_control"
    / "validation750.rows.jsonl",
    REPO_ROOT
    / "scratch/validation/gan2026_matched_v05_dev750_20260727"
    / "gpt56luna"
    / "validation750.rows.jsonl",
)
KIND_TARGETS = {
    "frequency": 8,
    "cluster": 4,
    "seizure_free": 4,
    "unknown": 2,
    "no_reference": 2,
}
ESCALATION_REASON = (
    "Predeclared Luna-only Gan final-prompt envelope study on a frozen "
    "20-row dev750 sample under docs/research/gan2026/"
    "structured_prompt_final_protocol_2026-08-15.md"
)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("freeze-sample", help="Freeze the 20-row draw before any final call")
    run_parser = sub.add_parser("run", help="Score the control arm and run final live")
    run_parser.add_argument("--overwrite", action="store_true")
    run_parser.add_argument("--progress-every", type=int, default=1)
    run_parser.add_argument("--api-base")
    args = parser.parse_args(argv)
    if args.command == "freeze-sample":
        print(json.dumps(freeze_sample(), indent=2, sort_keys=True))
        return
    print(
        json.dumps(
            run_study(
                overwrite=args.overwrite,
                progress_every=args.progress_every,
                api_base=args.api_base,
            ),
            indent=2,
            sort_keys=True,
        )
    )


def freeze_sample() -> dict[str, Any]:
    sample = _draw_sample()
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    if SAMPLE_PATH.exists():
        existing = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
        if existing["source_row_indices"] != sample["source_row_indices"]:
            raise RuntimeError("sample.json already frozen with a different index list")
        return existing
    SAMPLE_PATH.write_text(
        json.dumps(sample, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return sample


def _gold_bucket(record: GanFrequencyRecord) -> str:
    label = record.gold_label.lower()
    if "cluster" in label:
        return "cluster"
    return str(record.gold_label_kind)


def _draw_sample() -> dict[str, Any]:
    records = load_records_for_split("validation")
    if len(records) != 750:
        raise ValueError(f"expected 750 validation rows, found {len(records)}")
    pools: dict[str, list[int]] = {kind: [] for kind in KIND_TARGETS}
    for record in records:
        bucket = _gold_bucket(record)
        if bucket in pools:
            pools[bucket].append(int(record.source_row_index))
    chosen: dict[str, list[int]] = {}
    for kind, target in KIND_TARGETS.items():
        pool = sorted(pools[kind])
        if len(pool) < target:
            raise RuntimeError(f"not enough {kind} rows: {len(pool)} < {target}")
        chosen[kind] = pool[:target]
    indices = sorted(index for group in chosen.values() for index in group)
    if len(indices) != 20 or len(set(indices)) != 20:
        raise RuntimeError(f"sample must be 20 unique rows, got {indices}")
    by_index = {int(record.source_row_index): record for record in records}
    return {
        "schema_version": "gan2026.structured_prompt_final_luna_dev20_sample.v1",
        "protocol": PROTOCOL,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "selection_rule": (
            "Lowest source_row_index in each gold-kind pool. "
            "Not selected by v0.5 error."
        ),
        "kind_targets": KIND_TARGETS,
        "by_kind": chosen,
        "source_row_indices": indices,
        "gold_kinds": {
            str(index): _gold_bucket(by_index[index]) for index in indices
        },
    }


def run_study(
    *,
    overwrite: bool,
    progress_every: int,
    api_base: str | None,
) -> dict[str, Any]:
    if not SAMPLE_PATH.exists():
        raise FileNotFoundError("freeze the sample before run: freeze-sample")
    sample = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    wanted = [int(index) for index in sample["source_row_indices"]]
    records = [
        record
        for record in load_records_for_split("validation")
        if int(record.source_row_index) in set(wanted)
    ]
    records.sort(key=lambda record: int(record.source_row_index))
    if [int(record.source_row_index) for record in records] != wanted:
        raise RuntimeError("loaded records do not match frozen sample")

    _assert_final_payload(records[0])
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    control = _run_arm(
        slug="v05_control",
        prompt_version=hybrid_structured_events.PROMPT_VERSION_V0_5,
        records=records,
        overwrite=overwrite,
        progress_every=progress_every,
        api_base=api_base,
        prefer_reuse=True,
    )
    candidate = _run_arm(
        slug="final_live",
        prompt_version=hybrid_structured_events.PROMPT_VERSION_FINAL,
        records=records,
        overwrite=overwrite,
        progress_every=progress_every,
        api_base=api_base,
        prefer_reuse=False,
    )
    comparison = _compare_arms(control, candidate, records)
    artifact = {
        "schema_version": "gan2026.structured_prompt_final_luna_dev20.v1",
        "generated_on": "2026-08-15",
        "protocol": PROTOCOL,
        "decision": "docs/decisions/0053-gan-structured-events-final-prompt.md",
        "model": MODEL,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "row_count": 20,
        "sample": sample,
        "repair_mode": "hybrid_full_stack",
        "replay_mode": {
            "v05_control": control["call_mode"],
            "final_live": "live",
        },
        "control_source": control.get("reuse_source"),
        "final_contract_sha256": _final_contract_hash(),
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "arms": {
            "v05_control": control["summary"],
            "final_live": candidate["summary"],
        },
        "comparison": comparison,
        "claim_boundary": (
            "Gan Luna 20-row development comparison of the final envelope "
            "against v0.5. Not holdout, not a selected prompt, and not a "
            "six-model ranking."
        ),
    }
    artifact_path = STUDY_DIR / "comparison.json"
    artifact_path.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report_path = (
        REPO_ROOT / "docs/research/gan2026/structured_prompt_final_luna_dev20_2026-08-15.md"
    )
    report_path.write_text(_render_report(artifact), encoding="utf-8")
    return {
        "artifact": artifact_path.relative_to(REPO_ROOT).as_posix(),
        "report": report_path.relative_to(REPO_ROOT).as_posix(),
        "control_mode": control["call_mode"],
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


def _control_raws(wanted: Sequence[int]) -> tuple[dict[int, str], str] | None:
    needed = set(wanted)
    for path in CONTROL_CANDIDATES:
        if not path.is_file():
            continue
        rows = load_jsonl_rows(path)
        versions = {str(row.get("prompt_version")) for row in rows}
        if versions != {hybrid_structured_events.PROMPT_VERSION_V0_5}:
            continue
        raws = {
            int(row["source_row_index"]): str(row["raw_output"])
            for row in rows
            if str(row.get("raw_output") or "").strip()
        }
        if needed <= set(raws):
            return raws, path.relative_to(REPO_ROOT).as_posix()
    return None


def _run_arm(
    *,
    slug: str,
    prompt_version: str,
    records: Sequence[GanFrequencyRecord],
    overwrite: bool,
    progress_every: int,
    api_base: str | None,
    prefer_reuse: bool,
) -> dict[str, Any]:
    out_dir = STUDY_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    rows_path = out_dir / "validation20.rows.jsonl"
    wanted = [int(record.source_row_index) for record in records]
    reuse_raw_outputs: dict[int, str] = {}
    reuse_source: str | None = None
    call_mode = "live"
    mode: str = "live"
    if prefer_reuse:
        found = _control_raws(wanted)
        if found is not None:
            reuse_raw_outputs, reuse_source = found
            call_mode = "saved_raw_output_no_call"
            mode = "prompt-only"
    if rows_path.exists() and not overwrite:
        existing = load_jsonl_rows(rows_path)
        existing_idx = [int(row["source_row_index"]) for row in existing]
        if existing_idx == wanted:
            return _arm_result(
                slug=slug,
                prompt_version=prompt_version,
                rows=existing,
                call_mode=call_mode if reuse_source else "resumed",
                reuse_source=reuse_source,
                path=rows_path,
            )

    original = hybrid_structured_events.PROMPT_VERSION
    try:
        hybrid_structured_events.set_active_prompt_version(prompt_version)
        if call_mode == "live":
            print(f"ESCALATION_REASON={ESCALATION_REASON}", flush=True)
        rows, _metadata = hybrid_structured_events.run_split(
            records,
            split="validation",
            split_manifest="gan2026_split_v1",
            model=MODEL,
            temperature=1.0,
            max_tokens=10000,
            mode=mode,  # type: ignore[arg-type]
            dspy_cache=False,
            api_base=api_base,
            reuse_raw_outputs=reuse_raw_outputs or None,
            reuse_source=reuse_source,
            escalation_reason=ESCALATION_REASON,
            progress_every=progress_every,
            checkpoint_jsonl_path=rows_path,
            checkpoint_report_path=rows_path.with_suffix(".md"),
            repair_config=hybrid_structured_events.StructuredRepairConfig.for_mode(
                "hybrid_full_stack"
            ),
        )
        write_jsonl_rows(rows, rows_path)
    finally:
        hybrid_structured_events.set_active_prompt_version(original)
    return _arm_result(
        slug=slug,
        prompt_version=prompt_version,
        rows=rows,
        call_mode=call_mode,
        reuse_source=reuse_source,
        path=rows_path,
    )


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
    call_mode: str,
    reuse_source: str | None,
    path: Path,
) -> dict[str, Any]:
    scored = [_row_scores(row) for row in rows]
    return {
        "slug": slug,
        "prompt_version": prompt_version,
        "call_mode": call_mode,
        "reuse_source": reuse_source,
        "path": path.relative_to(REPO_ROOT).as_posix(),
        "rows": scored,
        "summary": {
            "rows": len(scored),
            "call_failures": sum(1 for row in scored if row["call_error"]),
            "parse_failures": sum(1 for row in scored if row["parse_failed"]),
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
    for record in records:
        index = int(record.source_row_index)
        left = control_by[index]
        right = candidate_by[index]
        if left["hybrid_purist"] != right["hybrid_purist"]:
            flips.append(
                {
                    "source_row_index": index,
                    "gold_kind": _gold_bucket(record),
                    "v05_hybrid_purist": left["hybrid_purist"],
                    "final_hybrid_purist": right["hybrid_purist"],
                }
            )
    hybrid_delta = (
        int(candidate["summary"]["hybrid_purist"])
        - int(control["summary"]["hybrid_purist"])
    )
    return {
        "raw_purist_delta": int(candidate["summary"]["raw_purist"])
        - int(control["summary"]["raw_purist"]),
        "raw_pragmatic_delta": int(candidate["summary"]["raw_pragmatic"])
        - int(control["summary"]["raw_pragmatic"]),
        "hybrid_purist_delta": hybrid_delta,
        "hybrid_pragmatic_delta": int(candidate["summary"]["hybrid_pragmatic"])
        - int(control["summary"]["hybrid_pragmatic"]),
        "hybrid_purist_flips": flips,
        "large_drop": hybrid_delta <= -3,
        "kind_counts": dict(Counter(_gold_bucket(record) for record in records)),
    }


def _render_report(artifact: Mapping[str, Any]) -> str:
    sample = artifact["sample"]
    arms = artifact["arms"]
    comparison = artifact["comparison"]
    control = arms["v05_control"]
    candidate = arms["final_live"]
    if comparison["large_drop"]:
        verdict = (
            "**large drop.** Stop. Inspect the `final` payload. Do not add "
            "clinical rules. Do not scale to `dev750`."
        )
    elif comparison["hybrid_purist_delta"] < 0:
        verdict = (
            "**small drop.** Envelope change moved a few rows. A Luna "
            "`dev750` protocol is allowed only after reviewing the flips. "
            "Not `test450`."
        )
    else:
        verdict = (
            "**no large drop.** A predeclared Luna `dev750` protocol is "
            "allowed. This does not authorize `test450` or the other five "
            "models."
        )
    kinds = sample["by_kind"]
    kind_lines = "\n".join(
        f"- **{kind}:** {', '.join(str(index) for index in indices)}"
        for kind, indices in kinds.items()
    )
    flip_lines = "none"
    flips = comparison["hybrid_purist_flips"]
    if flips:
        flip_lines = "\n".join(
            f"- `{item['source_row_index']}` ({item['gold_kind']}): "
            f"v0.5 {item['v05_hybrid_purist']} → final {item['final_hybrid_purist']}"
            for item in flips
        )
    control_prompt = hybrid_structured_events.PROMPT_VERSION_V0_5
    final_prompt = hybrid_structured_events.PROMPT_VERSION_FINAL
    control_source = artifact["control_source"] or "live v0.5 (sidecar absent)"
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
        f"| {name} | {left}/20 | {right}/20 | {delta:+d} |"
        for name, left, right, delta in counts
    )
    return "\n".join(
        [
            "# Luna `dev20` test of the Gan `final` prompt",
            "",
            "Date: 2026-08-15",
            "Status: complete",
            "Protocol: [final Luna `dev20` protocol]"
            "(structured_prompt_final_protocol_2026-08-15.md)",
            "Decision: [0053](../../decisions/0053-gan-structured-events-final-prompt.md)",
            f"Model: `{artifact['model']}`",
            "Sample: frozen 20 rows from Gan `dev750`; `test450` not touched",
            "",
            "## Verdict",
            "",
            verdict,
            "",
            "This is not a promotion and not a selected-fill rewrite.",
            "",
            "## Frozen sample",
            "",
            "Lowest `source_row_index` in each gold-kind pool. "
            "Not chosen by `v0.5` error.",
            "",
            kind_lines,
            "",
            "Indices: "
            + ", ".join(str(index) for index in sample["source_row_indices"]),
            "",
            "## Conditions",
            "",
            "| Item | Value |",
            "| :--- | :--- |",
            f"| Control | `{artifact['replay_mode']['v05_control']}` `{control_prompt}` |",
            f"| Control source | `{control_source}` |",
            f"| Candidate | live Luna, `{final_prompt}` |",
            "| Repair | `hybrid_full_stack` |",
            "| Scorer | Gan Purist primary; Pragmatic secondary |",
            "| Gold at prompt-build time | forbidden |",
            "| Holdout | not touched |",
            f"| `final` contract SHA-256 | `{artifact['final_contract_sha256']}` |",
            "",
            "## Counts on the 20-row pool",
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
            "## Hybrid Purist flips",
            "",
            flip_lines,
            "",
            "## Boundary",
            "",
            "Not `test450`. Not a selected prompt. Decision 0043 / 0050 fills "
            "stay on `v0.5`. Only the model-facing envelope changed on the "
            "`final` arm.",
            "",
        ]
    )


if __name__ == "__main__":
    main()