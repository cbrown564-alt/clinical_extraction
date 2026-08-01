"""Promote sealed/sanitized ExECT test60 stage aggregates into a public panel.

Phase A of docs/experiments/exectv2/reliability/
exectv2_primary_method_comparison_surface_protocol_2026-08-01.md.

Reads aggregate JSON only. Never opens sealed row JSONL.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
HOSTED_PANEL = REPO_ROOT / "experiments/hosted_holdout_panels_20260715.json"
PROTOCOL = (
    "docs/experiments/exectv2/reliability/"
    "exectv2_primary_method_comparison_surface_protocol_2026-08-01.md"
)
OUT_DIR = REPO_ROOT / "experiments/exectv2_six_model_test60_stage_panel_20260801"
NARRATIVE = (
    REPO_ROOT
    / "docs/experiments/exectv2/reliability/"
    / "exectv2_six_model_test60_stage_panel_2026-08-01.md"
)

SLUG_BY_MODEL = {
    "openai/gpt-4.1-mini": "gpt41mini",
    "openai/gpt-5.6-luna": "gpt56luna",
    "openai/gpt-5.6-sol": "gpt56sol",
    "deepseek/deepseek-v4-flash": "deepseek_v4_flash",
    "ollama_chat/qwen3.6:35b": "qwen36_35b",
    "ollama_chat/gemma4:26b": "gemma4_26b",
}

FORBIDDEN_TOP_LEVEL = frozenset(
    {
        "rows",
        "letters",
        "predictions",
        "traces",
        "letter_id",
        "note_text",
        "sealed_rows",
    }
)


def main() -> None:
    hosted = json.loads(HOSTED_PANEL.read_text(encoding="utf-8"))
    panel = hosted["panels"]["exectv2_test60"]
    conditions_out: list[dict[str, Any]] = []

    for condition in panel["conditions"]:
        model = str(condition["model"])
        slug = SLUG_BY_MODEL[model]
        rel = str(condition["aggregate_source"]["local_path"]).replace("\\", "/")
        path = REPO_ROOT / rel
        if not path.is_file():
            raise FileNotFoundError(f"missing aggregate for {slug}: {path}")

        raw_bytes = path.read_bytes()
        digest = hashlib.sha256(raw_bytes).hexdigest()
        expected = str(condition["aggregate_source"]["sha256"])
        expected_bytes = int(condition["aggregate_source"]["bytes"])
        hash_status = "matches_hosted_holdout_panel"
        if digest != expected or len(raw_bytes) != expected_bytes:
            # Local sanitized aggregates may be rewritten without changing the
            # retained final headline. Hosted sealed aggregates must match.
            if slug in {"qwen36_35b", "gemma4_26b"}:
                hash_status = "local_sanitized_aggregate_drifted"
            else:
                raise ValueError(
                    f"SHA-256/bytes mismatch for {slug}: expected "
                    f"{expected}/{expected_bytes}, got {digest}/{len(raw_bytes)}"
                )

        data = json.loads(raw_bytes.decode("utf-8"))
        _reject_row_leakage(data, slug)
        ladder = _score_ladder(data)
        raw = _overall(ladder["raw_lane_score"])
        final = _overall(ladder["headline_target"])
        raw_by = _by_indicator(ladder["raw_lane_score"])
        final_by = _by_indicator(ladder["headline_target"])

        hosted_final = condition["clinical_headline"]
        if round(float(final["f1"]), 4) != round(float(hosted_final["f1"]), 4):
            raise ValueError(
                f"{slug}: final F1 {final['f1']} != hosted panel "
                f"{hosted_final['f1']}"
            )

        entry: dict[str, Any] = {
            "slug": slug,
            "model": model,
            "row_count": int(panel["row_count"]),
            "raw_lane_score": raw,
            "clinical_headline": final,
            "raw_lane_score_by_family": raw_by,
            "clinical_headline_by_family": final_by,
            "call_failures": condition.get("call_failures"),
            "blocking_parse_failures": condition.get("blocking_parse_failures"),
            "parse_schema_failures": condition.get("parse_schema_failures"),
            "aggregate_source": {
                "local_path": rel,
                "sha256": digest,
                "bytes": len(raw_bytes),
                "hosted_holdout_panel_sha256": expected,
                "hosted_holdout_panel_bytes": expected_bytes,
                "hash_status": hash_status,
            },
        }
        if "runtime" in condition:
            entry["runtime"] = condition["runtime"]
        if "thinking" in condition:
            entry["thinking"] = condition["thinking"]
        conditions_out.append(entry)

    if len(conditions_out) != 6:
        raise ValueError(f"expected 6 conditions, got {len(conditions_out)}")

    payload = {
        "schema_version": "exectv2.six_model_test60_stage_panel.v1",
        "protocol": PROTOCOL,
        "decision": "docs/decisions/0046-exect-primary-method-comparison-boundary.md",
        "split": "test60",
        "split_manifest": panel["split_manifest"],
        "row_count": int(panel["row_count"]),
        "row_policy": "aggregate_only",
        "prompt_version": panel["prompt_version"],
        "llm_only_surface": "raw_lane_score",
        "hybrid_surface": "headline_target",
        "scorer": panel["scorer"],
        "source_holdout_panel": str(HOSTED_PANEL.relative_to(REPO_ROOT)).replace(
            "\\", "/"
        ),
        "conditions": conditions_out,
        "claim_boundary": (
            "Aggregate-only ExECT test60 stage panel promoted from sealed or "
            "sanitized aggregate JSON for decision 0046. LLM-only identity is "
            "raw_lane_score; hybrid identity is final clinical_headline / "
            "headline_target. No sealed row JSONL was opened. Not the published "
            "ExECT benchmark or clinical validation. Hosted-versus-local route "
            "differences remain disclosed. Primary method table cites Sol only."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "panel_aggregate.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    NARRATIVE.parent.mkdir(parents=True, exist_ok=True)
    NARRATIVE.write_text(_render_markdown(payload), encoding="utf-8")
    print(f"wrote {json_path.relative_to(REPO_ROOT)}")
    print(f"wrote {NARRATIVE.relative_to(REPO_ROOT)}")
    for item in conditions_out:
        print(
            f"{item['slug']}: raw={item['raw_lane_score']['f1']:.4f} "
            f"final={item['clinical_headline']['f1']:.4f}"
        )


def _reject_row_leakage(data: dict[str, Any], slug: str) -> None:
    leaked = sorted(FORBIDDEN_TOP_LEVEL.intersection(data))
    if leaked:
        raise ValueError(f"{slug}: aggregate contains forbidden keys {leaked}")


def _score_ladder(data: dict[str, Any]) -> dict[str, Any]:
    if isinstance(data.get("scorecard"), dict):
        ladder = data["scorecard"].get("score_ladder")
        if isinstance(ladder, dict):
            return ladder
    if isinstance(data.get("score_ladder"), dict):
        return data["score_ladder"]
    if isinstance(data.get("aggregate_scores"), dict):
        return data["aggregate_scores"]
    raise KeyError("no score_ladder or aggregate_scores in aggregate")


def _overall(block: dict[str, Any]) -> dict[str, float]:
    overall = block.get("overall")
    if not isinstance(overall, dict):
        raise KeyError("missing overall block")
    return {
        "f1": float(overall["f1"]),
        "precision": float(overall["precision"]),
        "recall": float(overall["recall"]),
    }


def _by_indicator(block: dict[str, Any]) -> dict[str, dict[str, float]]:
    by_indicator = block.get("by_indicator")
    if not isinstance(by_indicator, dict):
        return {}
    out: dict[str, dict[str, float]] = {}
    for family, values in by_indicator.items():
        if not isinstance(values, dict) or "f1" not in values:
            continue
        out[str(family)] = {
            "f1": float(values["f1"]),
            "precision": float(values["precision"]),
            "recall": float(values["recall"]),
        }
    return out


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# ExECTv2 six-model test60 stage panel",
        "",
        "Date: 2026-08-01",
        "Status: complete; Phase A of the 0046 evidence protocol",
        "Row policy: aggregate-only",
        "",
        "Protocol: "
        "[primary method-comparison surface protocol]"
        "(exectv2_primary_method_comparison_surface_protocol_2026-08-01.md)",
        "",
        "Decision: [0046](../../../decisions/0046-exect-primary-method-comparison-boundary.md)",
        "",
        "Machine panel: "
        "[panel_aggregate.json](../../../experiments/"
        "exectv2_six_model_test60_stage_panel_20260801/panel_aggregate.json)",
        "",
        "## Question",
        "",
        "What are aggregate `raw_lane_score` (LLM only) and final "
        "`clinical_headline` (LLM with rules) for each of the six retained "
        "ExECT `test60` conditions?",
        "",
        "## Result",
        "",
        "Promoted from sealed or sanitized **aggregate** JSON only. No sealed "
        "row JSONL was opened. Hosted aggregate SHA-256 values match "
        "`experiments/hosted_holdout_panels_20260715.json`. Local Qwen and "
        "Gemma sanitized aggregates may drift in hash/bytes while retaining "
        "the same public final `clinical_headline` F1; both hashes are "
        "recorded in the machine panel.",
        "",
        "| Model | LLM only (`raw_lane_score`) | LLM with rules (final) | Δ |",
        "| --- | ---: | ---: | ---: |",
    ]
    for item in payload["conditions"]:
        raw = float(item["raw_lane_score"]["f1"])
        final = float(item["clinical_headline"]["f1"])
        lines.append(
            f"| `{item['model']}` | {raw:.4f} | {final:.4f} | {final - raw:+.4f} |"
        )
    lines.extend(
        [
            "",
            "Primary method-table fill under decision 0046 remains **GPT-5.6 Sol** "
            f"(raw `{_sol(payload)['raw_lane_score']['f1']:.4f}`, "
            f"final `{_sol(payload)['clinical_headline']['f1']:.4f}`). "
            "The six-model rows are model-comparison evidence.",
            "",
            "## Claim boundary",
            "",
            str(payload["claim_boundary"]),
            "",
            "## Next action",
            "",
            "Phase B of the same protocol: rules-only four-family "
            "`clinical_headline` on `dev140`.",
            "",
        ]
    )
    return "\n".join(lines)


def _sol(payload: dict[str, Any]) -> dict[str, Any]:
    for item in payload["conditions"]:
        if item["slug"] == "gpt56sol":
            return item
    raise KeyError("gpt56sol missing")


if __name__ == "__main__":
    main()
