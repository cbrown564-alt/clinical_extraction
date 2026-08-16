"""Gate B: Gan 2026 rules-only aggregate on the locked test450 holdout split.

Protocol:
docs/research/gan2026/rules_only_test450_aggregate_protocol_2026-08-10.md

Precondition (Gate A) passed 2026-08-11:
docs/research/gan2026/rules_only_validation750_gate_a_2026-08-10.md

Deterministic rules-only pipeline, zero model calls. Row-level output
(`source_row_index`, `diagnostics`, `final_label`, `reference.gold_label`) is
forbidden in the public artifact under
`scripts/check_locked_aggregate_safety.py`. Row-level predictions are written
to `scratch/holdout/` (git-ignored, sealed) and referenced from the public
artifact by path, sha256, and byte count only. The public artifact carries
aggregates only.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.split import run_split

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/gan2026/rules_only_test450_aggregate_protocol_2026-08-10.md"
GATE_A = "docs/research/gan2026/rules_only_validation750_gate_a_2026-08-10.md"
SEALED_ROOT = REPO_ROOT / "scratch/holdout/gan2026_rules_only_test450_20260810"
SEALED_PATH = SEALED_ROOT / "rows.jsonl"
OUT_JSON = REPO_ROOT / "experiments/gan2026_rules_only_test450_20260810.json"
OUT_MD = REPO_ROOT / "docs/research/gan2026/rules_only_test450_aggregate_2026-08-10.md"
EXPECTED_ROW_COUNT = 450


def main() -> None:
    records = load_records_for_split("test")
    if len(records) != EXPECTED_ROW_COUNT:
        raise ValueError(f"expected {EXPECTED_ROW_COUNT} test450 records, got {len(records)}")

    rows, _metadata = run_split(
        records,
        architecture="deterministic_canonical_pipeline",
        split="test",
        split_manifest="gan2026_split_v1",
        model="none",
        temperature=0.0,
        max_tokens=0,
        mode="prompt-only",
        dspy_cache=False,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )
    if len(rows) != EXPECTED_ROW_COUNT:
        raise ValueError(f"expected {EXPECTED_ROW_COUNT} scored rows, got {len(rows)}")

    rendered = [r for r in rows if r["final_label"] != "unknown"]
    null_rows = len(rows) - len(rendered)
    purist_of_rendered = sum(1 for r in rendered if r["comparison"]["purist_correct"])
    pragmatic_of_rendered = sum(1 for r in rendered if r["comparison"]["pragmatic_correct"])
    purist_all = sum(1 for r in rows if r["comparison"]["purist_correct"])
    pragmatic_all = sum(1 for r in rows if r["comparison"]["pragmatic_correct"])
    evidence_valid = sum(1 for r in rows if r.get("evidence_valid"))

    sealed_path = _write_sealed_predictions(rows)
    sealed_digest = _sha256(sealed_path)

    payload: dict[str, Any] = {
        "schema_version": "gan2026.rules_only.test450.v1",
        "protocol": PROTOCOL,
        "gate_a": GATE_A,
        "generated_on": date.today().isoformat(),
        "split": "test450",
        "split_loader": "test",
        "row_count": len(rows),
        "row_policy": "aggregate_only",
        "method": {
            "pipeline": "deterministic_canonical_pipeline",
            "ablation_config": "default (all rule groups and portability classes enabled)",
            "model": "none (deterministic rules pipeline; no LLM calls)",
        },
        "purist": {
            "correct_of_rendered": purist_of_rendered,
            "rendered_denominator": len(rendered),
            "correct_of_all_rows": purist_all,
            "all_rows_denominator": len(rows),
            "rate_of_rendered": round(purist_of_rendered / len(rendered), 4) if rendered else 0.0,
            "rate_of_all_rows": round(purist_all / len(rows), 4),
        },
        "pragmatic": {
            "correct_of_rendered": pragmatic_of_rendered,
            "rendered_denominator": len(rendered),
            "correct_of_all_rows": pragmatic_all,
            "all_rows_denominator": len(rows),
            "rate_of_rendered": round(pragmatic_of_rendered / len(rendered), 4)
            if rendered
            else 0.0,
            "rate_of_all_rows": round(pragmatic_all / len(rows), 4),
        },
        "rendered_rows": len(rendered),
        "null_rows": null_rows,
        "evidence_valid_rows": evidence_valid,
        "rendered_definition": (
            "rules lane: final_label != 'unknown'; the LLM lanes instead use "
            "'row produced a parseable comparison block'"
        ),
        "sealed_predictions": {
            "local_path": str(sealed_path.relative_to(REPO_ROOT)).replace("\\", "/"),
            "sha256": sealed_digest,
            "bytes": sealed_path.stat().st_size,
            "note": (
                "Sealed under scratch/holdout; not committed, not for row "
                "inspection or public copy."
            ),
        },
        "claim_boundary": (
            "Standalone Gan rules-only test450 holdout figure (deterministic "
            "pipeline, zero model calls). Not ruleset-matched to the "
            "llm_with_rules test450 row (that row replays the 2026-07-31 "
            "ruleset through LLM-produced structured events; rules-only has "
            "no such repair stages and never did). Not a stage-contribution "
            "or leave-one-stage-out measurement. Aggregate-only; no row text, "
            "row index, label, diagnostic, or failure case from test450 is "
            "included in this artifact."
        ),
    }
    _assert_aggregate_only(payload)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(_render_markdown(payload), encoding="utf-8")

    print(f"wrote {OUT_JSON.relative_to(REPO_ROOT)}")
    print(f"wrote {OUT_MD.relative_to(REPO_ROOT)}")
    print(f"sealed {sealed_path.relative_to(REPO_ROOT)}")
    print(
        f"purist {purist_of_rendered}/{len(rendered)} rendered, "
        f"{purist_all}/{len(rows)} all rows"
    )


def _write_sealed_predictions(rows: list[dict[str, Any]]) -> Path:
    SEALED_ROOT.mkdir(parents=True, exist_ok=True)
    with SEALED_PATH.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return SEALED_PATH


def _assert_aggregate_only(payload: dict[str, Any]) -> None:
    forbidden = {
        "rows",
        "letters",
        "predictions",
        "traces",
        "source_row_index",
        "source_row_indices",
        "diagnostics",
        "final_label",
        "reference",
    }
    leaked = sorted(forbidden.intersection(payload))
    if leaked:
        raise ValueError(f"public payload contains forbidden keys: {leaked}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _render_markdown(payload: dict[str, Any]) -> str:
    purist = payload["purist"]
    pragmatic = payload["pragmatic"]
    lines = [
        "# Gan 2026 Rules-Only test450 Aggregate (Gate B)",
        "",
        f"Date: {payload['generated_on']}",
        "Status: complete; Gate B of the test450 aggregate protocol",
        "Row policy: aggregate-only",
        "Model calls: zero",
        "",
        f"Protocol: [{PROTOCOL}]({Path(PROTOCOL).name})",
        f"Gate A: [{GATE_A}]({Path(GATE_A).name})",
        "",
        "Machine artifact: "
        "[JSON](../../experiments/gan2026_rules_only_test450_20260810.json)",
        "",
        "## Question",
        "",
        "What is the Purist accuracy of the Gan rules-only pipeline (no model "
        "calls) on the locked `test450` split?",
        "",
        "## Result",
        "",
        "Aggregate-only. No row text, row index, label, diagnostic, or "
        "failure case is reported. Sealed row-level predictions remain under "
        "ignored `scratch/holdout/`.",
        "",
        "| Measure | Of rendered | Of all 450 rows |",
        "| --- | ---: | ---: |",
        (
            f"| Purist correct | {purist['correct_of_rendered']}/"
            f"{purist['rendered_denominator']} ({purist['rate_of_rendered']:.4f}) | "
            f"{purist['correct_of_all_rows']}/{purist['all_rows_denominator']} "
            f"({purist['rate_of_all_rows']:.4f}) |"
        ),
        (
            f"| Pragmatic correct | {pragmatic['correct_of_rendered']}/"
            f"{pragmatic['rendered_denominator']} ({pragmatic['rate_of_rendered']:.4f}) | "
            f"{pragmatic['correct_of_all_rows']}/{pragmatic['all_rows_denominator']} "
            f"({pragmatic['rate_of_all_rows']:.4f}) |"
        ),
        "",
        f"Rendered rows (`final_label != \"unknown\"`): {payload['rendered_rows']}",
        f"Null rows (`unknown`): {payload['null_rows']}",
        f"Evidence-valid rows: {payload['evidence_valid_rows']}",
        "",
        "`rendered` uses the rules lane's own convention "
        "(`final_label != \"unknown\"`); the LLM lanes use a different "
        "convention (non-null `comparison` block). See "
        "`rules_only_reference_refresh_2026-08-10.md`.",
        "",
        "## Method",
        "",
        "- Pipeline: `deterministic_canonical_pipeline` "
        "(`runners/split.py:run_split` -> `_run_deterministic_split`).",
        "- Ablation config: default — all rule groups and portability classes "
        "enabled, `disabled_rule_ids` empty.",
        "- Split: `test450` (locked), `gan2026_split_v1` manifest.",
        "- Models: none. Zero LLM calls.",
        "",
        "## Claim boundary",
        "",
        str(payload["claim_boundary"]),
        "",
        "## Predeclared reporting",
        "",
        "Per the protocol, this number is reported as-is with no threshold "
        "and no pass/fail criterion.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
