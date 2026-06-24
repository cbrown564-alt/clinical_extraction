"""GPT-4.1-mini ExECTv2 simplification frontier artifacts.

This module assembles aggregate-only full-200 simplification candidates from
saved producer artifacts. It intentionally does not inspect full-200 row-level
failures; row JSONL outputs preserve provenance, while the frontier decision is
made from aggregate clinical-recovery metrics.
"""

from __future__ import annotations

import json
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.frontend_review import REPO_ROOT
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_state_projection as sf_projection,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_union_arbitration as sf_union,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_unknown_suppression as sf_suppression,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (
    TARGET_INDICATORS,
)

DEFAULT_GENERATED_ON = "2026-06-24"
DEFAULT_CONFIG_DIR = Path("configs/exectv2/simplification_frontier")
DEFAULT_FRONTIER_JSON = Path("experiments/exectv2_gpt41mini_simplification_frontier_20260624.json")
DEFAULT_FRONTIER_MD = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_gpt41mini_simplification_frontier_2026-06-24.md"
)

ACCEPTABILITY_FLOORS = {
    "overall": 0.8400,
    DIAGNOSIS.name: 0.8300,
    SEIZURE_FREQUENCY.name: 0.7700,
    PRESCRIPTION.name: 0.8800,
    INVESTIGATIONS.name: 0.8400,
}


@dataclass(frozen=True)
class SimplificationConfig:
    """One simplification candidate plus its output contract."""

    path: Path
    candidate_id: str
    stage: str
    label: str
    calls_per_letter: float
    live_call_components: tuple[str, ...]
    replayed_components: tuple[str, ...]
    removed_components: tuple[str, ...]
    role: str
    assembly: FindingAssemblyManifest
    derived_artifacts: tuple[Mapping[str, Any], ...]
    output_json: Path
    output_jsonl: Path
    output_markdown: Path

    @property
    def full_200_calls(self) -> float:
        return self.calls_per_letter * self.assembly.row_count


GoldLoader = Callable[[str], list[ExectLetter]]


def default_config_paths(config_dir: Path = DEFAULT_CONFIG_DIR) -> list[Path]:
    """Return simplification candidate configs in declared stage order."""

    return sorted(config_dir.glob("*.json"))


def load_simplification_config(path: Path) -> SimplificationConfig:
    """Load one simplification candidate JSON config."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    assembly = manifest_from_mapping(payload["assembly"])
    output = payload["outputs"]
    return SimplificationConfig(
        path=path,
        candidate_id=str(payload["candidate_id"]),
        stage=str(payload["stage"]),
        label=str(payload.get("label", payload["candidate_id"])),
        calls_per_letter=float(payload["calls_per_letter"]),
        live_call_components=tuple(str(v) for v in payload.get("live_call_components", [])),
        replayed_components=tuple(str(v) for v in payload.get("replayed_components", [])),
        removed_components=tuple(str(v) for v in payload.get("removed_components", [])),
        role=str(payload.get("role", "candidate")),
        assembly=assembly,
        derived_artifacts=tuple(payload.get("derived_artifacts", [])),
        output_json=Path(str(output["json"])),
        output_jsonl=Path(str(output["jsonl"])),
        output_markdown=Path(str(output["markdown"])),
    )


def write_simplification_candidate_artifacts(
    config_path: Path,
    *,
    generated_on: str = DEFAULT_GENERATED_ON,
    gold_loader: GoldLoader | None = None,
    force_derived: bool = False,
) -> dict[str, Path]:
    """Materialize one candidate assembly JSON, JSONL, and Markdown report."""

    config = load_simplification_config(config_path)
    letters = (gold_loader or (lambda _split: load_letters()))(config.assembly.split)[
        : config.assembly.row_count
    ]
    materialize_derived_artifacts(
        config,
        letters=letters,
        force=force_derived,
    )
    run = build_simplification_candidate(
        config,
        letters=letters,
        generated_on=generated_on,
    )

    config.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    config.output_json.parent.mkdir(parents=True, exist_ok=True)
    config.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(run.rows, config.output_jsonl)
    config.output_json.write_text(
        json.dumps(run.report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    config.output_markdown.write_text(
        render_simplification_candidate_markdown(
            run.report,
            json_path=config.output_json,
            jsonl_path=config.output_jsonl,
        ),
        encoding="utf-8",
    )
    return {
        "json": config.output_json,
        "jsonl": config.output_jsonl,
        "markdown": config.output_markdown,
    }


def build_simplification_candidate(
    config: SimplificationConfig,
    *,
    letters: Sequence[ExectLetter],
    generated_on: str,
) -> AssemblyRun:
    """Build and annotate one simplification assembly run."""

    run = build_finding_assembly(
        config.assembly,
        generated_on=generated_on,
        gold_loader=lambda _split: list(letters),
    )
    report = dict(run.report)
    report["simplification_frontier"] = _candidate_metadata(config, report)
    return AssemblyRun(
        manifest=run.manifest,
        rows=run.rows,
        report=report,
        stores=run.stores,
        views=run.views,
    )


def materialize_derived_artifacts(
    config: SimplificationConfig,
    *,
    letters: Sequence[ExectLetter],
    force: bool = False,
) -> None:
    """Build no-call derivative producer artifacts requested by a config."""

    for spec in config.derived_artifacts:
        kind = str(spec["kind"])
        output = Path(str(spec["output"]))
        if output.exists() and not force:
            continue
        if kind == "sf_structured_direct":
            _write_sf_structured_direct_artifact(
                source=Path(str(spec["source"])),
                output=output,
                letters=letters,
            )
            continue
        if kind == "sf_projection":
            sf_projection.write_rows_and_report(
                sf_projection.read_rows(Path(str(spec["source"]))),
                ablation=str(spec.get("ablation", "combined")),  # type: ignore[arg-type]
                jsonl_path=output,
                report_path=Path(str(spec.get("report", output.with_suffix(".md")))),
            )
            continue
        if kind == "sf_suppression":
            sf_suppression.write_rows_and_report(
                sf_suppression.read_rows(Path(str(spec["source"]))),
                jsonl_path=output,
                report_path=Path(str(spec.get("report", output.with_suffix(".md")))),
            )
            continue
        if kind == "sf_union":
            sf_union.write_rows_and_report(
                sf_union.read_rows(Path(str(spec["source"]))),
                sf_union.deterministic_rows_from_letters(
                    letters,
                    split=str(spec.get("split", "full_200_authorized_simplification")),
                ),
                jsonl_path=output,
                report_path=Path(str(spec.get("report", output.with_suffix(".md")))),
            )
            continue
        raise ValueError(f"unsupported derived artifact kind {kind!r}")


def write_simplification_frontier_artifacts(
    *,
    config_paths: Sequence[Path] | None = None,
    generated_on: str = DEFAULT_GENERATED_ON,
    json_path: Path = DEFAULT_FRONTIER_JSON,
    markdown_path: Path = DEFAULT_FRONTIER_MD,
    force_derived: bool = False,
) -> dict[str, Path]:
    """Run configured candidates and write the aggregate frontier report."""

    paths = list(config_paths or default_config_paths())
    candidate_paths: list[dict[str, Path]] = []
    reports: list[dict[str, Any]] = []
    for config_path in paths:
        written = write_simplification_candidate_artifacts(
            config_path,
            generated_on=generated_on,
            force_derived=force_derived,
        )
        candidate_paths.append(written)
        reports.append(json.loads(written["json"].read_text(encoding="utf-8")))

    payload = build_frontier_payload(reports, generated_on=generated_on)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(
        render_frontier_markdown(payload, json_path=json_path),
        encoding="utf-8",
    )
    return {
        "json": json_path,
        "markdown": markdown_path,
        "candidate_json": [p["json"] for p in candidate_paths],  # type: ignore[dict-item]
        "candidate_jsonl": [p["jsonl"] for p in candidate_paths],  # type: ignore[dict-item]
        "candidate_markdown": [p["markdown"] for p in candidate_paths],  # type: ignore[dict-item]
    }


def build_frontier_payload(
    reports: Sequence[Mapping[str, Any]],
    *,
    generated_on: str,
) -> dict[str, Any]:
    """Build the machine-readable frontier summary from candidate reports."""

    candidates = [_candidate_summary(report) for report in reports]
    recommended = _recommended_candidate(candidates)
    return {
        "artifact_kind": "exectv2_gpt41mini_simplification_frontier",
        "generated_on": generated_on,
        "row_inspection_policy": "aggregate_only_no_full200_failure_ledgers",
        "allow_model_calls": False,
        "claim_boundary": (
            "Authorized full-200 aggregate-only current-code GPT-4.1-mini "
            "simplification frontier. Candidate rows preserve provenance, but "
            "promotion decisions use aggregate metrics only."
        ),
        "acceptability_rule": {
            "primary": {"overall_clinical_headline_f1": ACCEPTABILITY_FLOORS["overall"]},
            "family_guardrails": {
                entity: ACCEPTABILITY_FLOORS[entity] for entity in TARGET_INDICATORS
            },
        },
        "candidates": candidates,
        "recommended_candidate": recommended,
    }


def render_simplification_candidate_markdown(
    report: Mapping[str, Any],
    *,
    json_path: Path,
    jsonl_path: Path,
) -> str:
    """Render a candidate report with simplification cost metadata."""

    base = render_finding_assembly_markdown(
        report,
        json_path=json_path,
        jsonl_path=jsonl_path,
    )
    meta = report["simplification_frontier"]
    checks = meta["acceptability"]["checks"]
    lines = [
        "",
        "## Simplification Contract",
        "",
        f"- Stage: `{meta['stage']}`",
        f"- Role: `{meta['role']}`",
        f"- Calls per letter: `{meta['calls_per_letter']}`",
        f"- Full-200 calls: `{meta['full_200_calls']}`",
        f"- Live call components: `{', '.join(meta['live_call_components']) or 'none'}`",
        f"- Replayed/no-call components: `{', '.join(meta['replayed_components']) or 'none'}`",
        f"- Removed components: `{', '.join(meta['removed_components']) or 'none'}`",
        f"- Acceptability: **{meta['acceptability']['decision']}**",
        "",
        "| Guardrail | Value | Floor | Status |",
        "| --- | ---: | ---: | --- |",
    ]
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(
            f"| {check['name']} | {check['value']:.4f} | "
            f"{check['floor']:.4f} | {status} |"
        )
    return base + "\n" + "\n".join(lines) + "\n"


def render_frontier_markdown(payload: Mapping[str, Any], *, json_path: Path) -> str:
    """Render the aggregate simplification frontier markdown."""

    recommended = payload.get("recommended_candidate") or {}
    lines = [
        "# ExECTv2 GPT-4.1-mini Simplification Frontier",
        "",
        f"- Generated: `{payload['generated_on']}`",
        f"- JSON: `{json_path.as_posix()}`",
        f"- Row inspection policy: `{payload['row_inspection_policy']}`",
        f"- Model calls during this frontier build: `{payload['allow_model_calls']}`",
        f"- Claim boundary: {payload['claim_boundary']}",
        "",
        "## Recommendation",
        "",
    ]
    if recommended:
        lines.extend(
            [
                f"- Recommended lean architecture: `{recommended['candidate_id']}`",
                f"- Calls per letter: `{recommended['calls_per_letter']}`",
                f"- Rationale: {recommended['rationale']}",
            ]
        )
    else:
        lines.append("- No candidate passed the predeclared acceptability rule.")

    lines.extend(
        [
            "",
            "## Frontier Table",
            "",
            (
                "| Candidate | Calls / letter | Full-200 calls | Overall | Dx | SF | "
                "Presc | Inv | Pass/fail | Recommended? |"
            ),
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    recommended_id = str(recommended.get("candidate_id", ""))
    for candidate in payload["candidates"]:
        metrics = candidate["metrics"]
        families = metrics["by_indicator"]
        lines.append(
            f"| `{candidate['candidate_id']}` | {candidate['calls_per_letter']:.0f} | "
            f"{candidate['full_200_calls']:.0f} | {metrics['overall']['f1']:.4f} | "
            f"{families[DIAGNOSIS.name]['f1']:.4f} | "
            f"{families[SEIZURE_FREQUENCY.name]['f1']:.4f} | "
            f"{families[PRESCRIPTION.name]['f1']:.4f} | "
            f"{families[INVESTIGATIONS.name]['f1']:.4f} | "
            f"{candidate['acceptability']['decision']} | "
            f"{'yes' if candidate['candidate_id'] == recommended_id else 'no'} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "The frontier treats `clinical_headline` de-duplicated clinical "
                "recovery as the primary surface. Strict benchmark/CUI scores stay "
                "diagnostic and are not used for the recommendation."
            ),
            "",
            (
                "No full-200 row-level failure ledger was generated or inspected. "
                "The assembly JSONL files are provenance-preserving candidate outputs, "
                "not development error-analysis ledgers."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def evaluate_acceptability(report: Mapping[str, Any]) -> dict[str, Any]:
    """Apply the predeclared simplification floors to one report."""

    headline = report["score_ladder"]["headline_target"]
    checks = [
        _check("overall", headline["overall"]["f1"], ACCEPTABILITY_FLOORS["overall"])
    ]
    checks.extend(
        _check(entity, headline["by_indicator"][entity]["f1"], ACCEPTABILITY_FLOORS[entity])
        for entity in TARGET_INDICATORS
    )
    return {
        "decision": "pass" if all(check["passed"] for check in checks) else "fail",
        "checks": checks,
    }


def _candidate_metadata(
    config: SimplificationConfig,
    report: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "stage": config.stage,
        "label": config.label,
        "role": config.role,
        "config_path": config.path.as_posix(),
        "calls_per_letter": config.calls_per_letter,
        "full_200_calls": config.full_200_calls,
        "live_call_components": list(config.live_call_components),
        "replayed_components": list(config.replayed_components),
        "removed_components": list(config.removed_components),
        "output_json": config.output_json.as_posix(),
        "output_jsonl": config.output_jsonl.as_posix(),
        "output_markdown": config.output_markdown.as_posix(),
        "acceptability": evaluate_acceptability(report),
    }


def _candidate_summary(report: Mapping[str, Any]) -> dict[str, Any]:
    meta = report["simplification_frontier"]
    headline = report["score_ladder"]["headline_target"]
    lane_diagnostics = report.get("lane_diagnostics", {})
    return {
        "candidate_id": report["candidate_name"],
        "stage": meta["stage"],
        "label": meta["label"],
        "role": meta["role"],
        "calls_per_letter": float(meta["calls_per_letter"]),
        "full_200_calls": float(meta["full_200_calls"]),
        "live_call_components": list(meta["live_call_components"]),
        "replayed_components": list(meta["replayed_components"]),
        "removed_components": list(meta["removed_components"]),
        "acceptability": dict(meta["acceptability"]),
        "metrics": {
            "overall": dict(headline["overall"]),
            "by_indicator": {
                entity: dict(headline["by_indicator"][entity])
                for entity in TARGET_INDICATORS
            },
        },
        "diagnostics": {
            "call_failures": sum(
                int(value.get("call_failures", 0))
                for value in lane_diagnostics.values()
                if isinstance(value, Mapping)
            ),
            "parse_schema_failures": sum(
                int(value.get("parse_schema_failures", 0))
                for value in lane_diagnostics.values()
                if isinstance(value, Mapping)
            ),
            "evidence_invalid_dropped": sum(
                int(value.get("evidence_invalid_dropped", 0))
                for value in lane_diagnostics.values()
                if isinstance(value, Mapping)
            ),
            "exact_evidence_rate": min(
                [
                    float(value.get("exact_evidence_rate", 0.0))
                    for value in lane_diagnostics.values()
                    if isinstance(value, Mapping)
                ]
                or [1.0]
            ),
        },
        "paths": {
            "json": meta.get("output_json", ""),
            "jsonl": meta.get("output_jsonl", ""),
            "markdown": meta.get("output_markdown", ""),
            "config": meta["config_path"],
        },
    }


def _recommended_candidate(candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any] | None:
    passing = [
        candidate
        for candidate in candidates
        if candidate["acceptability"]["decision"] == "pass"
    ]
    if not passing:
        return None
    best = sorted(
        passing,
        key=lambda candidate: (
            float(candidate["calls_per_letter"]),
            -float(candidate["metrics"]["overall"]["f1"]),  # type: ignore[index]
        ),
    )[0]
    return {
        "candidate_id": best["candidate_id"],
        "calls_per_letter": best["calls_per_letter"],
        "full_200_calls": best["full_200_calls"],
        "rationale": (
            "lowest-call candidate that satisfies the overall clinical-headline "
            "floor and all family guardrails"
        ),
    }


def _check(name: str, value: float, floor: float) -> dict[str, Any]:
    return {
        "name": name,
        "value": round(float(value), 4),
        "floor": floor,
        "passed": float(value) >= floor,
    }


def _write_sf_structured_direct_artifact(
    *,
    source: Path,
    output: Path,
    letters: Sequence[ExectLetter],
) -> None:
    """Filter the structured all-family artifact down to direct SF mentions."""

    letter_by_id = {letter.letter_id: letter for letter in letters}
    rows = []
    for row in _read_jsonl(source):
        letter_id = str(row["letter_id"])
        mentions = [
            _sf_mention(mention)
            for mention in row.get("predicted_mentions", [])
            if str(mention.get("entity")) == SEIZURE_FREQUENCY.name
        ]
        rows.append(
            {
                "letter_id": letter_id,
                "split": row.get("split", "full_200_authorized_simplification"),
                "prompt_version": "structured_direct_no_sf_adjudicator_v01",
                "pipeline_family": "exectv2_structured_direct_no_sf_adjudicator",
                "model": row.get("model", "openai/gpt-4.1-mini"),
                "mode": "no-call projection from structured extractor",
                "source_pipeline_family": row.get("pipeline_family", ""),
                "source_prompt_version": row.get("prompt_version", ""),
                "component_owner": "single_gpt_structured_no_sf_adjudicator",
                "call_error": None,
                "parse_errors": [],
                "gate_warnings": [],
                "predicted_mentions": mentions,
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(mentions),
                "n_evidence_invalid": 0,
                "raw_output": json.dumps(
                    {"mentions": [_raw_mention(mention) for mention in mentions]},
                    sort_keys=True,
                ),
                "gold_mentions": [
                    {
                        "entity": annotation.entity,
                        "text": annotation.text,
                        "attributes": dict(annotation.attributes),
                    }
                    for annotation in letter_by_id[letter_id].annotations
                    if annotation.entity == SEIZURE_FREQUENCY.name
                ],
            }
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(rows, output)
    output.with_suffix(".md").write_text(
        "\n".join(
            [
                "# ExECTv2 Structured-Direct SeizureFrequency Adapter",
                "",
                f"- JSONL: `{output.as_posix()}`",
                f"- Source JSONL: `{source.as_posix()}`",
                "- Mode: `no-call projection from structured extractor`",
                f"- Letters: {len(rows)}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _sf_mention(mention: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "entity": SEIZURE_FREQUENCY.name,
        "text": str(mention.get("text", "")),
        "attributes": dict(mention.get("attributes") or {}),
        "evidence": str(mention.get("evidence", "")),
        "confidence": str(mention.get("confidence") or "medium"),
        "rationale": str(mention.get("rationale", "")),
        "component_owner": "single_gpt_structured_no_sf_adjudicator",
    }


def _raw_mention(mention: Mapping[str, Any]) -> dict[str, Any]:
    row = dict(mention)
    row.pop("entity", None)
    return row


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    resolved = path if path.is_absolute() else REPO_ROOT / path
    return [
        json.loads(line)
        for line in resolved.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
