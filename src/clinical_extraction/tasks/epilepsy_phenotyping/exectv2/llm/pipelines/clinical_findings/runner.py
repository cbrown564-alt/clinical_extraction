"""Run-split orchestration and reporting for clinical findings."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

import dspy

from clinical_extraction.core.run_resume import (
    merge_rows,
    pending_items,
    read_completed,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.clinical_findings.constants import (
    _OUTPUT_LAYERS,
    ENTITY_NAME,
    PIPELINE_FAMILY,
    PLAN11_EVENT_STATE_LAYER_LADDER,
    PLAN11_EVENT_STATE_ROUTE_VERSION,
    PROMPT_VERSION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.clinical_findings.extract import (
    DspyClinicalFindingsSFExtractor,
    build_prompt_input,
    parse_clinical_findings_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.clinical_findings.projection import (
    build_plan11_event_state_route,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.clinical_findings.types import (
    ClinicalFindingRecord,
    ClinicalFindingsRecord,
    FindingFamilyChecklist,
    VerificationDecisionList,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.clinical_findings.verify import (
    DspyClinicalFindingsSFVerifier,
    apply_verification_decisions,
    build_verification_prompt_input,
    parse_verification_decisions_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.dspy_runner import (
    emit_run_checkpoint,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    SF_BENCHMARK,
    SF_SEMANTIC,
    EntityScore,
    score_entity,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm


def run_split(
    letters: Sequence[ExectLetter],
    *,
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the clinical-findings extractor over a split."""

    program = DspyClinicalFindingsSFExtractor()
    verifier = DspyClinicalFindingsSFVerifier()
    if mode == "live":
        dspy.configure(
            lm=build_dspy_lm(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=dspy_cache,
                api_base=api_base,
            )
        )

    order = [letter.letter_id for letter in letters]
    requested = set(order)
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None, key="letter_id"
    )
    rows: list[dict[str, Any]] = [r for r in existing_rows if r.get("letter_id") in requested]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    for letter in todo:
        prompt_input_json = build_prompt_input(letter)
        raw_output = ""
        call_error: str | None = None

        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"

        extraction, parse_errors = (
            parse_clinical_findings_json(raw_output) if raw_output else (None, ["not_run"])
        )
        findings = extraction.findings if extraction else []
        event_frames = extraction.event_frames if extraction else []

        verification_prompt_input_json = ""
        verification_raw_output = ""
        verification_call_error: str | None = None
        verification_parse_errors: list[str] = []
        verified_findings: list[ClinicalFindingRecord] = []
        verification_decisions: VerificationDecisionList | None = None
        verification_warnings: list[str] = []
        final_findings = findings

        if mode == "live" and findings:
            verification_prompt_input_json = build_verification_prompt_input(
                letter,
                findings,
                event_frames,
            )
            try:
                verification_prediction = verifier(prompt_input_json=verification_prompt_input_json)
                verification_raw_output = str(verification_prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                verification_call_error = f"{type(exc).__name__}: {exc}"

            verification_decisions, verification_parse_errors = (
                parse_verification_decisions_json(verification_raw_output)
                if verification_raw_output
                else (None, ["not_run"])
            )
            if verification_decisions is not None:
                verified_findings, verification_warnings = apply_verification_decisions(
                    findings,
                    verification_decisions,
                )
                final_findings = verified_findings
        elif mode == "prompt-only":
            verification_parse_errors = ["not_run"]

        final_record = ClinicalFindingsRecord(
            family_checklist=(
                extraction.family_checklist if extraction is not None else FindingFamilyChecklist()
            ),
            event_frames=event_frames,
            findings=final_findings,
        )
        layers, route_diagnostics, projection_warnings = build_plan11_event_state_route(
            letter.letter_id, final_record, note_text=letter.note_text
        )

        gold_sf = letter.entities(ENTITY_NAME)
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "pipeline_family": PIPELINE_FAMILY,
                "prompt_version": PROMPT_VERSION,
                "model": model,
                "mode": mode,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "verification_prompt_input_json": verification_prompt_input_json,
                "verification_raw_output": verification_raw_output,
                "verification_call_error": verification_call_error,
                "verification_parse_errors": verification_parse_errors,
                "verification_warnings": verification_warnings,
                "projection_warnings": projection_warnings,
                "plan11_event_state_route": route_diagnostics,
                "event_frames": [frame.model_dump(mode="json") for frame in event_frames],
                "raw_extraction_findings": [
                    finding.model_dump(mode="json") for finding in findings
                ],
                "verified_model_findings": [
                    finding.model_dump(mode="json") for finding in verified_findings
                ],
                "verification_decisions": (
                    verification_decisions.model_dump(mode="json")
                    if verification_decisions is not None
                    else None
                ),
                "raw_model_findings": [
                    finding.model_dump(mode="json") for finding in final_findings
                ],
                "n_event_frames": len(event_frames),
                "n_extraction_findings": len(findings),
                "n_verified_findings": len(verified_findings),
                "n_mentions_raw": len(final_findings),
                "n_mentions_scored": len(layers["cui_projected"].mentions),
                "n_format_projected_mentions": len(layers["format_projected"].mentions),
                "n_cui_projected_mentions": len(layers["cui_projected"].mentions),
                "n_evidence_invalid": (
                    len(final_findings) - len(layers["format_projected"].mentions)
                ),
                "format_projected_mentions": _letter_mentions_to_rows(layers["format_projected"]),
                "cui_projected_mentions": _letter_mentions_to_rows(layers["cui_projected"]),
                "predicted_mentions": _letter_mentions_to_rows(layers["cui_projected"]),
                "gold_mentions": [
                    {"text": a.text, "attributes": dict(a.attributes)} for a in gold_sf
                ],
            }
        )

        if progress_every and (len(rows) - n_resumed) % progress_every == 0:
            _emit_checkpoint(
                rows,
                total=len(letters),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
                split=split,
                model=model,
                mode=mode,
            )

    rows = merge_rows(rows, order, key="letter_id")
    metadata = {
        "pipeline_family": PIPELINE_FAMILY,
        "prompt_version": PROMPT_VERSION,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": mode,
        "split": split,
        "n_letters": len(letters),
        "n_resumed": n_resumed,
        "dspy_version": getattr(dspy, "__version__", "unknown"),
    }
    metadata["summary"] = summarize_rows(rows)
    return rows, metadata


def _letter_mentions_to_rows(letter: PredictedLetter) -> list[dict[str, Any]]:
    return [
        {
            "text": m.text,
            "attributes": dict(m.attributes),
            "evidence": m.evidence,
            "confidence": m.confidence,
            "rationale": m.rationale,
        }
        for m in letter.mentions
    ]


def summarize_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate statistics and F1 scores across all rows and layers."""

    n = len(rows)
    if n == 0:
        return {"examples": 0}

    call_failures = sum(bool(r.get("call_error")) for r in rows)
    verification_call_failures = sum(bool(r.get("verification_call_error")) for r in rows)
    parse_failures = sum(_has_blocking_parse_issue(r.get("parse_errors")) for r in rows)
    verification_parse_failures = sum(
        _has_blocking_parse_issue(r.get("verification_parse_errors")) for r in rows
    )
    n_event_frames = sum(int(r.get("n_event_frames", 0)) for r in rows)
    n_mentions_raw = sum(int(r.get("n_mentions_raw", 0)) for r in rows)
    n_extraction_findings = sum(int(r.get("n_extraction_findings", 0)) for r in rows)
    n_verified_findings = sum(int(r.get("n_verified_findings", 0)) for r in rows)
    n_evidence_invalid = sum(int(r.get("n_evidence_invalid", 0)) for r in rows)

    layer_summaries = {
        layer: _score_layer(rows, mention_field=f"{layer}_mentions") for layer in _OUTPUT_LAYERS
    }
    primary = layer_summaries["cui_projected"]
    route_summary = _plan11_route_summary(rows)

    return {
        "examples": n,
        "call_failures": call_failures,
        "verification_call_failures": verification_call_failures,
        "parse_failures": parse_failures,
        "verification_parse_failures": verification_parse_failures,
        "n_event_frames": n_event_frames,
        "n_extraction_findings": n_extraction_findings,
        "n_verified_findings": n_verified_findings,
        "n_mentions_raw": n_mentions_raw,
        "n_mentions_scored": primary["n_mentions_scored"],
        "n_format_projected_mentions": layer_summaries["format_projected"]["n_mentions_scored"],
        "n_cui_projected_mentions": primary["n_mentions_scored"],
        "n_evidence_invalid": n_evidence_invalid,
        "evidence_validity_rate": (
            round((n_mentions_raw - n_evidence_invalid) / n_mentions_raw, 4)
            if n_mentions_raw
            else 1.0
        ),
        "scores": primary["scores"],
        "attribution_layers": layer_summaries,
        "plan11_event_state_route": route_summary,
    }


def _plan11_route_summary(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    layer_counts = {layer["layer"]: 0 for layer in PLAN11_EVENT_STATE_LAYER_LADDER}
    policy_counts: dict[str, int] = {}
    deterministic_selection_rows = 0
    ownerships: set[str] = set()
    for row in rows:
        route = row.get("plan11_event_state_route") or {}
        ownership = route.get("aggregate_ownership")
        if ownership:
            ownerships.add(str(ownership))
        if route.get("deterministic_clinical_selection"):
            deterministic_selection_rows += 1
        for layer in route.get("layers") or []:
            name = str(layer.get("layer", ""))
            if name in layer_counts:
                layer_counts[name] += int(layer.get("count", 0))
        for key, count in (route.get("post_llm_state_policy_counts") or {}).items():
            policy_counts[str(key)] = policy_counts.get(str(key), 0) + int(count)

    if deterministic_selection_rows:
        aggregate = "hybrid_or_diagnostic_required"
    elif policy_counts:
        aggregate = "llm_first_with_declared_post_llm_state_policy"
    else:
        aggregate = "llm_first"
    return {
        "route_version": PLAN11_EVENT_STATE_ROUTE_VERSION,
        "aggregate_ownership": aggregate,
        "row_ownerships": sorted(ownerships),
        "deterministic_clinical_selection_rows": deterministic_selection_rows,
        "post_llm_state_policy_counts": policy_counts,
        "layer_counts": layer_counts,
        "layer_ladder": list(PLAN11_EVENT_STATE_LAYER_LADDER),
    }


def _score_layer(rows: Sequence[dict[str, Any]], *, mention_field: str) -> dict[str, Any]:
    gold_letters = _reconstruct_gold_letters(rows)
    pred_letters = _reconstruct_pred_letters(rows, mention_field=mention_field)
    scores: dict[str, Any] = {}
    for config_name, config in [
        ("phrase_only", PHRASE_ONLY),
        ("sf_semantic", SF_SEMANTIC),
        ("sf_benchmark", SF_BENCHMARK),
    ]:
        entity_score: EntityScore = score_entity(gold_letters, pred_letters, ENTITY_NAME, config)
        scores[config_name] = {
            "per_item": {
                "precision": round(entity_score.per_item.precision, 4),
                "recall": round(entity_score.per_item.recall, 4),
                "f1": round(entity_score.per_item.f1, 4),
                "tp": entity_score.per_item.tp,
                "fp": entity_score.per_item.fp,
                "fn": entity_score.per_item.fn,
            },
            "per_letter": {
                "precision": round(entity_score.per_letter.precision, 4),
                "recall": round(entity_score.per_letter.recall, 4),
                "f1": round(entity_score.per_letter.f1, 4),
                "tp": entity_score.per_letter.tp,
                "fp": entity_score.per_letter.fp,
                "fn": entity_score.per_letter.fn,
            },
        }
    return {
        "n_mentions_scored": sum(len(r.get(mention_field) or []) for r in rows),
        "scores": scores,
    }


def _reconstruct_gold_letters(rows: Sequence[dict[str, Any]]) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        annotations = tuple(
            ExectAnnotation(
                entity=ENTITY_NAME,
                text=m["text"],
                attributes=m["attributes"],
            )
            for m in (row.get("gold_mentions") or [])
        )
        letters.append(
            ExectLetter(
                letter_id=row["letter_id"],
                note_text="",
                annotations=annotations,
            )
        )
    return letters


def _reconstruct_pred_letters(
    rows: Sequence[dict[str, Any]], *, mention_field: str
) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        pred_letter = PredictedLetter(
            letter_id=row["letter_id"],
            mentions=tuple(
                PredictedMention(
                    entity=ENTITY_NAME,
                    text=m["text"],
                    attributes=m["attributes"],
                    evidence=m.get("evidence", ""),
                    confidence=m.get("confidence", "medium"),
                    rationale=m.get("rationale", ""),
                )
                for m in (row.get(mention_field) or [])
            ),
        )
        letters.append(to_exect_letter(pred_letter))
    return letters


def write_jsonl(rows: Sequence[dict[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: dict[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    """Write a concise Markdown run report."""

    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary") or summarize_rows(rows)
    lines = [
        "# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Pipeline family: `{metadata.get('pipeline_family', PIPELINE_FAMILY)}`",
        f"- Prompt version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- Split: `{metadata.get('split')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Letters: {summary.get('examples', 0)}",
        "",
        "## Gate Summary",
        "",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Verification call failures: {summary.get('verification_call_failures', 0)}",
        f"- Parse/schema failures: {summary.get('parse_failures', 0)}",
        f"- Verification parse/schema failures: {summary.get('verification_parse_failures', 0)}",
        f"- Event frames: {summary.get('n_event_frames', 0)}",
        f"- First-pass findings: {summary.get('n_extraction_findings', 0)}",
        f"- Verified findings: {summary.get('n_verified_findings', 0)}",
        f"- Final model findings: {summary.get('n_mentions_raw', 0)}",
        f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
        f"- Format-projected mentions: {summary.get('n_format_projected_mentions', 0)}",
        f"- CUI-projected mentions: {summary.get('n_cui_projected_mentions', 0)}",
        (f"- Evidence validity rate: {summary.get('evidence_validity_rate', 0.0):.4f}"),
        "",
        "## Plan 11 Event/State Route",
        "",
    ]
    route = summary.get("plan11_event_state_route", {})
    lines.extend(
        [
            f"- Route version: `{route.get('route_version', PLAN11_EVENT_STATE_ROUTE_VERSION)}`",
            f"- Aggregate ownership: `{route.get('aggregate_ownership', 'llm_first')}`",
            (
                "- Deterministic clinical-selection rows: "
                f"{route.get('deterministic_clinical_selection_rows', 0)}"
            ),
            (f"- Post-LLM state policy actions: {route.get('post_llm_state_policy_counts', {})}"),
            "",
            "| Layer | Owner | Count | Claim role |",
            "| --- | --- | ---: | --- |",
        ]
    )
    layer_counts = route.get("layer_counts", {})
    for layer in route.get("layer_ladder", PLAN11_EVENT_STATE_LAYER_LADDER):
        name = layer["layer"]
        lines.append(
            f"| `{name}` | `{layer['owner']}` | {layer_counts.get(name, 0)} "
            f"| {layer['claim_role']} |"
        )
    lines.extend(
        [
            "",
            "## Attribution Layers",
            "",
        ]
    )
    layers = summary.get("attribution_layers", {})
    for layer in _OUTPUT_LAYERS:
        layer_summary = layers.get(layer, {})
        scores = layer_summary.get("scores", {})
        lines.extend([f"### {layer}", ""])
        for config_name in ("phrase_only", "sf_semantic", "sf_benchmark"):
            s = scores.get(config_name, {})
            pi = s.get("per_item", {})
            pl = s.get("per_letter", {})
            lines.append(
                f"- {config_name} per-item F1={pi.get('f1', 0):.3f} "
                f"(P={pi.get('precision', 0):.3f} R={pi.get('recall', 0):.3f}); "
                f"per-letter F1={pl.get('f1', 0):.3f}"
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _has_blocking_parse_issue(errors: Any) -> bool:
    return any(
        str(e).startswith(("invalid_json:", "schema_validation_error:", "not_run"))
        for e in (errors or [])
    )


def _emit_checkpoint(
    rows: Sequence[dict[str, Any]],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
    split: str,
    model: str,
    mode: str,
) -> None:
    emit_run_checkpoint(
        rows,
        total=total,
        jsonl_path=jsonl_path,
        report_path=report_path,
        metadata={
            "pipeline_family": PIPELINE_FAMILY,
            "prompt_version": PROMPT_VERSION,
            "split": split,
            "model": model,
            "mode": mode,
        },
        summarize_rows=summarize_rows,
        write_jsonl=write_jsonl,
        write_report=write_report,
    )
