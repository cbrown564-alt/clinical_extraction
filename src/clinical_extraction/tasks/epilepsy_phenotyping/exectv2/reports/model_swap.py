"""Same-core ExECTv2 model-swap readiness artifacts.

This module deliberately separates architecture-freeze bookkeeping from live
model execution. It can materialize rows when the frozen producer artifacts are
already present, and otherwise records pending model rows without substituting
older diagnostic architectures.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.manifests import (
    FindingAssemblyManifest,
    manifest_from_mapping,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
    AssemblyRun,
    build_finding_assembly,
    render_finding_assembly_markdown,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (
    TARGET_INDICATORS,
)

DEFAULT_GENERATED_ON = "2026-06-25"
DEFAULT_CONFIG_DIR = Path("configs/exectv2/model_swap")
DEFAULT_SUMMARY_JSON = Path("experiments/exectv2_same_core_model_swap_dev140_20260625.json")
DEFAULT_SUMMARY_JSONL = Path("experiments/exectv2_same_core_model_swap_dev140_20260625.jsonl")
DEFAULT_SUMMARY_MD = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_same_core_model_swap_dev140_2026-06-25.md"
)
PRIMARY_SURFACE = "clinical_headline"
ROW_INSPECTION_POLICY = "dev140_only_no_full200_or_holdout_row_level_inspection"


@dataclass(frozen=True)
class ModelSwapConfig:
    """One same-core model-swap config and its output contract."""

    path: Path
    candidate_id: str
    model: str
    model_label: str
    architecture_core_id: str
    calls_per_letter: float
    runtime: str
    prompt_profile: str
    temperature: float
    max_tokens: Mapping[str, Any]
    live_call_components: tuple[str, ...]
    replayed_components: tuple[str, ...]
    claim_boundary: str
    run_command: str
    assembly: FindingAssemblyManifest
    output_json: Path
    output_jsonl: Path
    output_markdown: Path


GoldLoader = Callable[[str], list[ExectLetter]]


def default_config_paths(config_dir: Path = DEFAULT_CONFIG_DIR) -> list[Path]:
    """Return model-swap configs in stable candidate order."""

    return sorted(config_dir.glob("*.json"))


def load_model_swap_config(path: Path) -> ModelSwapConfig:
    """Load one model-swap JSON config."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    outputs = payload["outputs"]
    return ModelSwapConfig(
        path=path,
        candidate_id=str(payload["candidate_id"]),
        model=str(payload["model"]),
        model_label=str(payload.get("model_label", payload["model"])),
        architecture_core_id=str(payload["architecture_core_id"]),
        calls_per_letter=float(payload.get("calls_per_letter", 2)),
        runtime=str(payload.get("runtime", "")),
        prompt_profile=str(payload.get("prompt_profile", "full")),
        temperature=float(payload.get("temperature", 0.0)),
        max_tokens=dict(payload.get("max_tokens", {})),
        live_call_components=tuple(str(v) for v in payload["live_call_components"]),
        replayed_components=tuple(str(v) for v in payload["replayed_components"]),
        claim_boundary=str(payload.get("claim_boundary", "")),
        run_command=str(payload.get("run_command", "")),
        assembly=manifest_from_mapping(payload["assembly"]),
        output_json=Path(str(outputs["json"])),
        output_jsonl=Path(str(outputs["jsonl"])),
        output_markdown=Path(str(outputs["markdown"])),
    )


def validate_same_core_configs(
    configs: Sequence[ModelSwapConfig],
) -> dict[str, Any]:
    """Validate that all configs share the same non-adapter architecture."""

    if not configs:
        raise ValueError("at least one model-swap config is required")
    reference = _component_signature(configs[0])
    mismatched = [
        config.candidate_id
        for config in configs
        if _component_signature(config) != reference
    ]
    core_ids = sorted({config.architecture_core_id for config in configs})
    return {
        "architecture_core_id": configs[0].architecture_core_id,
        "core_ids": core_ids,
        "component_graph_identical": not mismatched and len(core_ids) == 1,
        "mismatched_candidates": mismatched,
        "shared_signature": reference,
        "adapter_differences": {
            config.candidate_id: {
                "model": config.model,
                "model_label": config.model_label,
                "prompt_profile": config.prompt_profile,
                "runtime": config.runtime,
            }
            for config in configs
        },
    }


def write_model_swap_artifacts(
    *,
    config_paths: Sequence[Path] | None = None,
    generated_on: str = DEFAULT_GENERATED_ON,
    json_path: Path = DEFAULT_SUMMARY_JSON,
    jsonl_path: Path = DEFAULT_SUMMARY_JSONL,
    markdown_path: Path = DEFAULT_SUMMARY_MD,
    gold_loader: GoldLoader | None = None,
) -> dict[str, Path]:
    """Materialize available same-core rows and write the readiness report."""

    configs = [load_model_swap_config(path) for path in (config_paths or default_config_paths())]
    parity = validate_same_core_configs(configs)
    model_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for config in configs:
        missing = _missing_source_artifacts(config)
        if missing:
            row = _pending_model_row(config, missing)
        else:
            run = write_model_swap_candidate_artifacts(
                config,
                generated_on=generated_on,
                gold_loader=gold_loader,
            )
            row = _completed_model_row(config, run.report)
        model_rows.append(row)
        summary_rows.append(_jsonl_summary_row(row))

    payload = build_model_swap_payload(
        configs=configs,
        model_rows=model_rows,
        parity=parity,
        generated_on=generated_on,
    )
    json_path.parent.mkdir(parents=True, exist_ok=True)
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_jsonl(summary_rows, jsonl_path)
    markdown_path.write_text(render_model_swap_markdown(payload), encoding="utf-8")
    return {"json": json_path, "jsonl": jsonl_path, "markdown": markdown_path}


def write_model_swap_candidate_artifacts(
    config: ModelSwapConfig,
    *,
    generated_on: str,
    gold_loader: GoldLoader | None = None,
) -> AssemblyRun:
    """Build one available same-core model-swap assembly row set."""

    loader = gold_loader or (lambda _split: load_letters()[: config.assembly.row_count])
    run = build_finding_assembly(
        config.assembly,
        generated_on=generated_on,
        gold_loader=loader,
    )
    report = _annotated_candidate_report(config, run.report)
    config.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    config.output_json.parent.mkdir(parents=True, exist_ok=True)
    config.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(run.rows, config.output_jsonl)
    config.output_json.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    config.output_markdown.write_text(
        render_model_swap_candidate_markdown(
            report,
            json_path=config.output_json,
            jsonl_path=config.output_jsonl,
        ),
        encoding="utf-8",
    )
    return AssemblyRun(
        manifest=run.manifest,
        rows=run.rows,
        report=report,
        stores=run.stores,
        views=run.views,
    )


def build_model_swap_payload(
    *,
    configs: Sequence[ModelSwapConfig],
    model_rows: Sequence[Mapping[str, Any]],
    parity: Mapping[str, Any],
    generated_on: str,
) -> dict[str, Any]:
    """Build the aggregate model-swap readiness payload."""

    gates = _readiness_gates(model_rows, parity)
    overall_status = _overall_status(gates, model_rows)
    return {
        "artifact_kind": "exectv2_same_core_model_swap_dev140",
        "generated_on": generated_on,
        "architecture_core_id": parity["architecture_core_id"],
        "primary_surface": PRIMARY_SURFACE,
        "row_inspection_policy": ROW_INSPECTION_POLICY,
        "allow_full200_or_holdout_row_inspection": False,
        "claim_boundary": _claim_boundary(model_rows, gates),
        "overall_status": overall_status,
        "same_core_parity": dict(parity),
        "model_rows": [dict(row) for row in model_rows],
        "readiness_gates": gates,
        "historical_diagnostic_boundary": {
            "not_same_core_rows": [
                "exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140",
                "exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140",
                "exectv2_holistic_finding_assembly_v0924_qwencompact_schemaoperand_dev140",
                "exectv2_holistic_finding_assembly_v05_qwen_relaxed_actions_dev140",
            ],
            "policy": (
                "Retain as historical diagnostics/path evidence only. Do not use "
                "them as final same-core model swaps."
            ),
        },
        "next_actions": _next_actions(model_rows, gates),
        "configs": [config.path.as_posix() for config in configs],
    }


def render_model_swap_candidate_markdown(
    report: Mapping[str, Any],
    *,
    json_path: Path,
    jsonl_path: Path,
) -> str:
    """Render one completed same-core candidate report."""

    base = render_finding_assembly_markdown(
        report,
        json_path=json_path,
        jsonl_path=jsonl_path,
    )
    meta = report["model_swap"]
    lines = [
        "",
        "## Same-Core Model-Swap Contract",
        "",
        f"- Architecture core: `{meta['architecture_core_id']}`",
        f"- Model: `{meta['model_label']}` (`{meta['model']}`)",
        f"- Runtime: `{meta['runtime']}`",
        f"- Prompt profile: `{meta['prompt_profile']}`",
        f"- Calls per letter: `{meta['calls_per_letter']}`",
        f"- Live call components: `{', '.join(meta['live_call_components'])}`",
        f"- Replayed/no-call components: `{', '.join(meta['replayed_components'])}`",
        f"- Row inspection policy: `{ROW_INSPECTION_POLICY}`",
        "",
    ]
    return base + "\n" + "\n".join(lines)


def render_model_swap_markdown(payload: Mapping[str, Any]) -> str:
    """Render the aggregate same-core model-swap readiness report."""

    gates = payload["readiness_gates"]
    lines = [
        "# ExECTv2 Same-Core Model-Swap Dev140 Readiness",
        "",
        f"- Generated: `{payload['generated_on']}`",
        f"- Architecture core: `{payload['architecture_core_id']}`",
        f"- Primary surface: `{payload['primary_surface']}`",
        f"- Row inspection policy: `{payload['row_inspection_policy']}`",
        f"- Overall status: **{payload['overall_status']}**",
        f"- Claim boundary: {payload['claim_boundary']}",
        "",
        "## Model Rows",
        "",
        (
            "| Candidate | Model | Status | Overall | Dx | SF | Presc | Inv | "
            "Call failures | Parse/schema failures | Min evidence rate |"
        ),
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["model_rows"]:
        metrics = row.get("metrics") or {}
        by_indicator = metrics.get("by_indicator") or {}
        overall = (metrics.get("overall") or {}).get("f1")
        diagnostics = row.get("diagnostics") or {}
        lines.append(
            f"| `{row['candidate_id']}` | {row['model_label']} | {row['status']} | "
            f"{_fmt_metric(overall)} | "
            f"{_fmt_metric((by_indicator.get(DIAGNOSIS.name) or {}).get('f1'))} | "
            f"{_fmt_metric((by_indicator.get(SEIZURE_FREQUENCY.name) or {}).get('f1'))} | "
            f"{_fmt_metric((by_indicator.get(PRESCRIPTION.name) or {}).get('f1'))} | "
            f"{_fmt_metric((by_indicator.get(INVESTIGATIONS.name) or {}).get('f1'))} | "
            f"{_fmt_count(diagnostics.get('call_failures'))} | "
            f"{_fmt_count(diagnostics.get('parse_schema_failures'))} | "
            f"{_fmt_metric(diagnostics.get('minimum_exact_evidence_rate'))} |"
        )

    lines.extend(
        [
            "",
            "## Readiness Gates",
            "",
            "| Gate | Status | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for gate_id, gate in gates.items():
        lines.append(f"| {gate_id} | {gate['status']} | {gate['detail']} |")

    lines.extend(
        [
            "",
            "## Historical Diagnostic Boundary",
            "",
            payload["historical_diagnostic_boundary"]["policy"],
            "",
        ]
    )
    for candidate in payload["historical_diagnostic_boundary"]["not_same_core_rows"]:
        lines.append(f"- `{candidate}`")

    lines.extend(["", "## Next Actions", ""])
    for action in payload["next_actions"]:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def _annotated_candidate_report(
    config: ModelSwapConfig,
    report: Mapping[str, Any],
) -> dict[str, Any]:
    meta = {
        "config_path": config.path.as_posix(),
        "candidate_id": config.candidate_id,
        "model": config.model,
        "model_label": config.model_label,
        "architecture_core_id": config.architecture_core_id,
        "calls_per_letter": config.calls_per_letter,
        "runtime": config.runtime,
        "prompt_profile": config.prompt_profile,
        "temperature": config.temperature,
        "max_tokens": dict(config.max_tokens),
        "live_call_components": list(config.live_call_components),
        "replayed_components": list(config.replayed_components),
        "row_inspection_policy": ROW_INSPECTION_POLICY,
    }
    return {
        **dict(report),
        "gate_decision": {
            **dict(report["gate_decision"]),
            "decision": "same-core-model-swap-dev140-readout",
            "basis": (
                "Generic assembly gates remain diagnostic; the model-swap "
                "readiness report governs cross-model promotion."
            ),
        },
        "model_swap": meta,
    }


def _completed_model_row(
    config: ModelSwapConfig,
    report: Mapping[str, Any],
) -> dict[str, Any]:
    headline = report["score_ladder"]["headline_target"]
    return {
        "candidate_id": config.candidate_id,
        "model": config.model,
        "model_label": config.model_label,
        "status": "complete",
        "architecture_core_id": config.architecture_core_id,
        "surface": PRIMARY_SURFACE,
        "split": report["split"],
        "row_count": report["row_count"],
        "metrics": {
            "overall": dict(headline["overall"]),
            "by_indicator": {
                entity: dict(headline["by_indicator"][entity])
                for entity in TARGET_INDICATORS
            },
            "strict_benchmark_cui_f1": report["score_ladder"]["benchmark"][
                "after_cui_projection"
            ],
        },
        "diagnostics": _aggregate_diagnostics(report),
        "producer_ownership": _producer_ownership(report),
        "deterministic_action_counts": _deterministic_action_counts(report),
        "paths": {
            "config": config.path.as_posix(),
            "json": config.output_json.as_posix(),
            "jsonl": config.output_jsonl.as_posix(),
            "markdown": config.output_markdown.as_posix(),
        },
        "claim_boundary": config.claim_boundary,
    }


def _pending_model_row(
    config: ModelSwapConfig,
    missing: Sequence[Path],
) -> dict[str, Any]:
    return {
        "candidate_id": config.candidate_id,
        "model": config.model,
        "model_label": config.model_label,
        "status": "pending_source_artifacts",
        "architecture_core_id": config.architecture_core_id,
        "surface": PRIMARY_SURFACE,
        "split": config.assembly.split,
        "row_count": config.assembly.row_count,
        "missing_artifacts": [path.as_posix() for path in missing],
        "run_command": config.run_command,
        "metrics": None,
        "diagnostics": None,
        "paths": {
            "config": config.path.as_posix(),
            "json": config.output_json.as_posix(),
            "jsonl": config.output_jsonl.as_posix(),
            "markdown": config.output_markdown.as_posix(),
        },
        "claim_boundary": config.claim_boundary,
    }


def _readiness_gates(
    model_rows: Sequence[Mapping[str, Any]],
    parity: Mapping[str, Any],
) -> dict[str, dict[str, str]]:
    pending = [row for row in model_rows if row["status"] != "complete"]
    completed = [row for row in model_rows if row["status"] == "complete"]
    all_complete = not pending and bool(completed)
    parity_ok = bool(parity["component_graph_identical"])
    completed_diagnostics = [
        row["diagnostics"] for row in completed if isinstance(row.get("diagnostics"), Mapping)
    ]
    call_failures = sum(
        int(diagnostics.get("call_failures", 0))
        for diagnostics in completed_diagnostics
    )
    parse_failures = sum(
        int(diagnostics.get("parse_schema_failures", 0))
        for diagnostics in completed_diagnostics
    )
    min_evidence = min(
        [
            float(diagnostics.get("minimum_exact_evidence_rate", 0.0))
            for diagnostics in completed_diagnostics
        ]
        or [1.0]
    )
    return {
        "architecture_parity": {
            "status": "pass" if parity_ok else "fail",
            "detail": (
                "All configs share the frozen component graph."
                if parity_ok
                else "At least one config changes the frozen component graph."
            ),
        },
        "attribution_clarity": {
            "status": "pass" if parity_ok else "fail",
            "detail": (
                "Configs separate model-generated structured/Diagnosis outputs "
                "from deterministic SF projection and Prescription repair."
            ),
        },
        "evidence_validity": {
            "status": "pending" if pending else ("pass" if min_evidence >= 0.99 else "fail"),
            "detail": (
                f"Completed rows minimum exact evidence rate is {min_evidence:.4f}; "
                f"{len(pending)} model row(s) still pending."
            ),
        },
        "operational_stability": {
            "status": (
                "pending"
                if pending
                else ("pass" if call_failures == 0 and parse_failures == 0 else "fail")
            ),
            "detail": (
                f"Completed rows call failures={call_failures}, "
                f"parse/schema failures={parse_failures}; "
                f"{len(pending)} model row(s) still pending."
            ),
        },
        "family_parity": {
            "status": "pass" if all_complete else "pending",
            "detail": (
                "Per-family clinical-headline metrics are available for every model."
                if all_complete
                else "Per-family comparison waits for all same-core model rows."
            ),
        },
        "claim_boundary": {
            "status": "pass",
            "detail": (
                "This artifact is dev140-only and does not inspect full-200 or "
                "holdout row-level failures."
            ),
        },
    }


def _overall_status(
    gates: Mapping[str, Mapping[str, str]],
    model_rows: Sequence[Mapping[str, Any]],
) -> str:
    if any(gate["status"] == "fail" for gate in gates.values()):
        return "blocked_architecture_or_operational_gate"
    if any(row["status"] != "complete" for row in model_rows):
        return "pending_same_core_model_runs"
    return "ready_for_same_core_scorecard_review"


def _claim_boundary(
    model_rows: Sequence[Mapping[str, Any]],
    gates: Mapping[str, Mapping[str, str]],
) -> str:
    pending = [row for row in model_rows if row["status"] != "complete"]
    if pending:
        return (
            "Development same-core model-swap readiness. Final cross-model "
            "scorecard comparison is blocked until GPT-4.1-mini, DeepSeek, "
            "and Qwen all have rows on the frozen core."
        )
    if gates["operational_stability"]["status"] == "fail":
        return (
            "Development same-core model-swap rows are complete on the frozen "
            "core, but operational stability is not promoted because at least "
            "one row has call or parse/schema failures. Use the dev140 scores "
            "with this caveat; do not advance to full-200 without a fresh "
            "aggregate-only predeclaration."
        )
    return (
        "Development same-core model-swap rows are complete on the frozen core "
        "and ready for scorecard review. Any full-200 follow-up still requires "
        "a fresh aggregate-only predeclaration."
    )


def _next_actions(
    model_rows: Sequence[Mapping[str, Any]],
    gates: Mapping[str, Mapping[str, str]],
) -> list[str]:
    pending = [row for row in model_rows if row["status"] != "complete"]
    if not pending:
        if gates["operational_stability"]["status"] == "fail":
            return [
                "Record the completed dev140 same-core comparison with an "
                "operational-stability caveat.",
                "Review Qwen call/parse failures before any full-200 "
                "aggregate-only predeclaration.",
            ]
        return [
            "Run the same-core scorecard-readiness review and decide whether a "
            "frozen aggregate-only full-200 audit is warranted."
        ]
    return [
        f"Run or replay `{row['candidate_id']}` using the frozen config at "
        f"`{row['paths']['config']}`."
        for row in pending
    ]


def _component_signature(config: ModelSwapConfig) -> dict[str, Any]:
    assembly = config.assembly
    producer_ids = sorted(assembly.producers)
    return {
        "architecture_core_id": config.architecture_core_id,
        "calls_per_letter": config.calls_per_letter,
        "live_call_components": list(config.live_call_components),
        "replayed_components": list(config.replayed_components),
        "producer_ids": producer_ids,
        "lenses": {
            entity: {
                "producer": lens.producer,
                "lens": lens.lens,
                "source_lane": lens.source_lane,
                "ownership_label": lens.ownership_label,
                "portability": lens.portability,
            }
            for entity, lens in sorted(assembly.lenses.items())
        },
        "views": list(assembly.views),
        "split": assembly.split,
        "row_count": assembly.row_count,
        "baseline_producer": assembly.baseline_producer,
    }


def _missing_source_artifacts(config: ModelSwapConfig) -> list[Path]:
    missing = []
    for producer in config.assembly.producers.values():
        if not producer.artifact.exists():
            missing.append(producer.artifact)
    return missing


def _aggregate_diagnostics(report: Mapping[str, Any]) -> dict[str, Any]:
    lane_diagnostics = report.get("lane_diagnostics", {})
    values = [v for v in lane_diagnostics.values() if isinstance(v, Mapping)]
    return {
        "call_failures": sum(int(v.get("call_failures", 0)) for v in values),
        "parse_schema_failures": sum(int(v.get("parse_schema_failures", 0)) for v in values),
        "evidence_invalid_dropped": sum(
            int(v.get("evidence_invalid_dropped", 0)) for v in values
        ),
        "minimum_exact_evidence_rate": min(
            [float(v.get("exact_evidence_rate", 0.0)) for v in values] or [1.0]
        ),
        "by_family": {family: dict(stats) for family, stats in lane_diagnostics.items()},
    }


def _producer_ownership(report: Mapping[str, Any]) -> dict[str, str]:
    return {
        entity: str(payload.get("ownership_label", ""))
        for entity, payload in report.get("lane_sources", {}).items()
        if isinstance(payload, Mapping)
    }


def _deterministic_action_counts(report: Mapping[str, Any]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    origin = report.get("fact_origin_accounting", {}).get("by_lane", {})
    if isinstance(origin, Mapping):
        prescription = origin.get(PRESCRIPTION.name, {})
        if isinstance(prescription, Mapping):
            final = prescription.get("residual_benchmark_added", {})
            if isinstance(final, Mapping):
                counts["prescription_deterministic_mentions"] = int(
                    final.get("deterministic_projection", 0)
                    + final.get("deterministic_repair", 0)
                )
    lane_diagnostics = report.get("lane_diagnostics", {})
    sf_stats = lane_diagnostics.get(SEIZURE_FREQUENCY.name, {})
    if isinstance(sf_stats, Mapping):
        counts["sf_evidence_invalid_dropped"] = int(
            sf_stats.get("evidence_invalid_dropped", 0)
        )
    return dict(counts)


def _jsonl_summary_row(row: Mapping[str, Any]) -> dict[str, Any]:
    metrics = row.get("metrics") or {}
    diagnostics = row.get("diagnostics") or {}
    return {
        "candidate_id": row["candidate_id"],
        "model_label": row["model_label"],
        "status": row["status"],
        "overall_clinical_headline_f1": (metrics.get("overall") or {}).get("f1"),
        "call_failures": diagnostics.get("call_failures"),
        "parse_schema_failures": diagnostics.get("parse_schema_failures"),
        "minimum_exact_evidence_rate": diagnostics.get("minimum_exact_evidence_rate"),
    }


def _fmt_metric(value: Any) -> str:
    return "n/a" if value is None else f"{float(value):.4f}"


def _fmt_count(value: Any) -> str:
    return "n/a" if value is None else str(int(value))
