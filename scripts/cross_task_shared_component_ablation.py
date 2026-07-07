"""Build cross-task shared-component ablation table (aggregate-only, no model calls)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from clinical_extraction.core.cross_task_component_ablation import (
    build_cross_task_ablation_payload,
)

REPO = Path(__file__).resolve().parents[1]
DEFAULT_JSON = REPO / "experiments/cross_task_shared_component_ablation_2026-06-27.json"
DEFAULT_MD = (
    REPO / "docs/experiments/reliability/cross_task_shared_component_ablation_2026-06-27.md"
)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Cross-Task Shared-Component Ablation",
        "",
        f"- Generated: `{payload['generated_on']}`",
        "- JSON: `experiments/cross_task_shared_component_ablation_2026-06-27.json`",
        "- Harness: `scripts/cross_task_shared_component_ablation.py`",
        "- Core module: `src/clinical_extraction/core/cross_task_component_ablation.py`",
        f"- Claim boundary: {payload['claim_boundary']}",
        "- Row inspection policy: `aggregate_only`",
        "- No model calls; reads saved dev140 / validation750 replay artifacts only.",
        "",
        "## Bottom Line",
        "",
        "**Primary subject: `evidence_validation`** (from existing `definitions.yaml` "
        "`component_off`; M2 evidence-unification not required for this read). Turning "
        "off the exact-substring evidence gate is **structurally inert on both tasks** "
        "on the representative validation surfaces: contribution Δ = **0.0000** on "
        "ExECTv2 dev140 (v08 control) and Gan2026 validation750 (deterministic "
        "`evidence_trace_check`). Producers already emit verbatim-grounded mentions / "
        "rule outputs already pass the gate — the guard is present but does not move "
        "the declared score on these splits.",
        "",
        "Secondary (SF-normalization structure): `standard_dictionary` / Gan `normalize` "
        "shows **positive** contribution on both tasks (+0.0389 ExECTv2, +0.0293 Gan "
        "hybrid GPT-4.1-mini) — normalization buys score, but the mechanisms differ "
        "(CUI/dictionary vs format-level Gan label normalization).",
        "",
        "**Deferred:** date-arithmetic policy has no clean cross-task ladder rung; "
        "isolating it requires Gan one-family-off replays "
        "(`seizure_free_duration_date_instrumentation`, etc.) outside this harness.",
        "",
        "## Primary Table (`evidence_validation`)",
        "",
        "| Component | Task | Split | Baseline | Component-off | Δ (contribution) | Metric |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    primary_id = "evidence_validation"
    secondary_ids = {row["component_id"] for row in payload["rows"]} - {primary_id}
    for row in payload["rows"]:
        if row["component_id"] != primary_id:
            continue
        lines.append(
            f"| `{row['component_id']}` | {row['task']} | {row['split']} "
            f"| {row['baseline_score']:.4f} | {row['component_off_score']:.4f} "
            f"| {row['contribution_delta']:+.4f} | {row['metric']} |"
        )
    if secondary_ids:
        lines.extend(
            [
                "",
                "## Secondary Table (SF-normalization structure)",
                "",
                "| Component | Task | Split | Baseline | Component-off | Δ (contribution) | Metric |",
                "| --- | --- | --- | ---: | ---: | ---: | --- |",
            ]
        )
        for row in payload["rows"]:
            if row["component_id"] == primary_id:
                continue
            lines.append(
                f"| `{row['component_id']}` | {row['task']} | {row['split']} "
                f"| {row['baseline_score']:.4f} | {row['component_off_score']:.4f} "
                f"| {row['contribution_delta']:+.4f} | {row['metric']} |"
            )
    lines.extend(
        [
            "",
            "Contribution Δ = baseline − component-off (positive means removing the "
            "component lowers the score on this split).",
            "",
            "## Mapping Notes",
            "",
        ]
    )
    seen: set[str] = set()
    for row in payload["rows"]:
        key = row["component_id"]
        if key in seen:
            continue
        seen.add(key)
        exectv2 = next(
            r for r in payload["rows"] if r["component_id"] == key and r["task"] == "exectv2"
        )
        lines.append(f"### `{key}`")
        lines.append("")
        lines.append(
            f"- ExECTv2 ({exectv2['architecture_run_id']}): "
            f"`{exectv2['baseline_surface']}` → `{exectv2['component_off_surface']}`"
        )
        gan = next(
            (r for r in payload["rows"] if r["component_id"] == key and r["task"] == "gan2026"),
            None,
        )
        if gan is not None:
            lines.append(
                f"- Gan2026 ({gan['architecture_run_id']}): "
                f"`{gan['baseline_surface']}` → `{gan['component_off_surface']}`"
            )
            if gan.get("mapping_note"):
                lines.append(f"- Gan mapping note: {gan['mapping_note']}")
        else:
            lines.append("- Gan2026: no clean ladder rung mapped for this component.")
        lines.append("")

    lines.extend(
        [
            "## Source Artifacts",
            "",
            f"- ExECTv2 component-off: `{payload['source_artifacts']['exectv2_component_off']}`",
            f"- Gan2026 stage ladder: `{payload['source_artifacts']['gan2026_stage_ladder']}`",
            f"- Component definitions: `{payload['source_artifacts']['exectv2_definitions']}`",
            "",
            "## Interpretation Boundary",
            "",
            "These rows measure whether turning off one shared component changes the "
            "declared validation-side score on each task's representative architecture. "
            "They do not prove a component is globally unnecessary, and they must not "
            "be blended into reliability-scorecard or holdout claims.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--components",
        default="evidence_validation,standard_dictionary",
        help="Comma-separated component_id list from definitions.yaml",
    )
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()

    component_ids = tuple(part.strip() for part in args.components.split(",") if part.strip())
    payload = build_cross_task_ablation_payload(component_ids=component_ids)

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")

    print(f"Wrote {args.json_out}")
    print(f"Wrote {args.md_out}")
    for row in payload["rows"]:
        print(
            f"{row['component_id']:25} {row['task']:8} "
            f"baseline={row['baseline_score']:.4f} "
            f"off={row['component_off_score']:.4f} "
            f"delta={row['contribution_delta']:+.4f}"
        )


if __name__ == "__main__":
    main()
