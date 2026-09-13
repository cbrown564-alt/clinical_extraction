"""Aggregate-only fixed replay of one-call responses through cell-3 rules."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation.gan_cell_replay import (
    score_label,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredRepairConfig,
    parse_structured_json_with_trace,
)

ROOT = Path(__file__).resolve().parents[2]
REMOTE = "9a2ce3ffda69059f6575008d53796d724cc1cc23"
METHOD = "gan_llm_extract_encode_select"
MODES = ("raw_model", "llm_encode", "gan_rules_encode", "llm_select_after_codebook")
LOCAL = ("qwen38_27b", "qwen36_35b", "gemma4_26b", "qwen35_9b", "qwen25_14b", "llama31_8b")
HOSTED = ("gemini37flash", "deepseek_v4_flash", "gpt56luna")


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def source(slug: str, name: str) -> tuple[bytes, str]:
    if slug in LOCAL:
        path = f"paper_experiments/gan/{METHOD}/{slug}/test450/{name}"
        return git("show", f"{REMOTE}:{path}"), f"git:{REMOTE}:{path}"
    path = f"scratch/holdout/paper/{METHOD}/{slug}/20260905/{name}"
    return (ROOT / path).read_bytes(), path


def main() -> None:
    records = {r.source_row_index: r for r in load_records_for_split("test")}
    assert len(records) == 450, "unexpected split count"
    output = {
        "schema_version": "one_call_cell3_replay.v1",
        "generated_utc": datetime.now(UTC).isoformat(),
        "commit": git("rev-parse", "HEAD").decode().strip(),
        "working_tree_status": git("status", "--short").decode(),
        "dataset": "Gan 2026",
        "split": "test450",
        "split_manifest": "gan2026_split_v1",
        "row_policy": "aggregate_only",
        "prompt_version": METHOD,
        "replay_mode": "saved_outputs_no_calls",
        "model_calls": 0,
        "primary_scorer": "purist",
        "secondary_scorer": "pragmatic",
        "claim_boundary": (
            "Diagnostic fixed-rule replay on previously evaluated holdout; "
            "no tuning or clinical validation."
        ),
        "source_hashes": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / "src/clinical_extraction").rglob("*.py"))
        },
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "split_manifest_sha256": hashlib.sha256(
            (ROOT / "data/Gan (2026)/splits/gan2026_split_v1.json").read_bytes()
        ).hexdigest(),
        "models": [],
    }
    for slug in (*HOSTED, *LOCAL):
        raw_bytes, raw_source = source(slug, "rows.jsonl")
        meta_bytes, meta_source = source(slug, "comparison.json")
        meta = json.loads(meta_bytes)
        rows = [json.loads(line) for line in raw_bytes.splitlines() if line.strip()]
        ids = [int(row["source_row_index"]) for row in rows]
        assert len(ids) == 450 and set(ids) == set(records), f"{slug}: split coverage mismatch"
        assert meta["prompt_version"] == METHOD and meta["split"] == "test450"
        assert all(row["prompt_version"] == METHOD for row in rows), f"{slug}: prompt mismatch"
        scores = {mode: [] for mode in MODES}
        totals = {
            mode: {
                "n": 450,
                "purist_correct": 0,
                "pragmatic_correct": 0,
                "parse_failures": 0,
                "selected_evidence_exact": 0,
            }
            for mode in MODES
        }
        for row in rows:
            record = records[int(row["source_row_index"])]
            for mode in MODES:
                extraction, _, _, _ = parse_structured_json_with_trace(
                    str(row["raw_output"]),
                    note_text=record.note_text,
                    repair_config=StructuredRepairConfig.for_mode(mode),
                )
                label = extraction.selection.final_label if extraction else None
                scored = score_label(record, label)
                correct = bool(scored["purist_correct"])
                scores[mode].append(correct)
                total = totals[mode]
                total["purist_correct"] += int(correct)
                total["pragmatic_correct"] += int(scored["pragmatic_correct"])
                total["parse_failures"] += int(extraction is None)
                evidence = extraction.selection.evidence if extraction else None
                total["selected_evidence_exact"] += int(
                    bool(evidence) and evidence in record.note_text
                )
        assert totals["raw_model"]["purist_correct"] == meta["score"]["purist_correct"], (
            f"{slug}: baseline mismatch"
        )
        assert (
            totals["llm_encode"]["purist_correct"] == meta["stages"]["encode"]["purist_correct"]
        ), f"{slug}: prior encode mismatch"
        for total in totals.values():
            total["purist_accuracy"] = total["purist_correct"] / 450
            total["pragmatic_accuracy"] = total["pragmatic_correct"] / 450
        transitions = {}
        for before, after in (
            ("raw_model", "gan_rules_encode"),
            ("gan_rules_encode", "llm_select_after_codebook"),
            ("raw_model", "llm_select_after_codebook"),
        ):
            pairs = list(zip(scores[before], scores[after], strict=True))
            transitions[f"{before}_to_{after}"] = {
                "wrong_to_correct": sum(not a and b for a, b in pairs),
                "correct_to_wrong": sum(a and not b for a, b in pairs),
            }
        result = {
            "model_slug": slug,
            "model": meta["model"],
            "model_label": meta["model_label"],
            "raw_source": raw_source,
            "raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "comparison_source": meta_source,
            "comparison_sha256": hashlib.sha256(meta_bytes).hexdigest(),
            "source_configuration": {
                k: meta.get(k)
                for k in (
                    "temperature",
                    "reasoning_effort",
                    "thinking_type",
                    "max_tokens",
                    "started_utc",
                    "finished_utc",
                )
            },
            "modes": totals,
            "purist_transitions": transitions,
        }
        output["models"].append(result)
        print(json.dumps({"model": slug, "modes": totals, "transitions": transitions}), flush=True)
    out = ROOT / "results/letter-benchmarks/gan/one_call_cell3_replay/2026-09-10/comparison.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(f"Saved aggregate artifact: {out}")


if __name__ == "__main__":
    main()
