"""LLM-only claim-table selector for Gan 2026 seizure-frequency extraction."""

from __future__ import annotations

import json
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.replay_io import (
    load_raw_outputs_by_source_index,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.repair_modes import (
    repair_mode_layers,
    repair_mode_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.claim_table_parser import (
    SectionClaimTableExtractionRecord,
    parse_llm_only_claim_table_selector_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label_clean_scorer_facing,
    repair_prediction_label_format_preserving,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.claim_table_report import (
    write_report,
)

PROMPT_VERSION = "gan2026_llm_only_claim_table_selector_v5"
PROMPT_POLICY_TAXONOMY: list[dict[str, str]] = [
    {
        "policy_id": "sct_v5.schema.scalar_enum_output",
        "controlled_variable": "prompt_schema_enum_scalar_policy",
        "portability": "general",
        "status": "active",
        "description": (
            "Prompt requires enum fields to be single schema values rather than lists or "
            "free-text mixtures."
        ),
    },
    {
        "policy_id": "sct_v5.schema.strict_json_object",
        "controlled_variable": "prompt_strict_json_object_policy",
        "portability": "general",
        "status": "active",
        "description": "Prompt requires exactly one JSON object with no markdown wrapper.",
    },
    {
        "policy_id": "sct_v5.evidence.exact_substring",
        "controlled_variable": "prompt_exact_evidence_substring_policy",
        "portability": "seizure_frequency",
        "status": "active",
        "description": (
            "Prompt requires claim and final-query evidence to be copied as source substrings."
        ),
    },
    {
        "policy_id": "sct_v5.gan_label.parser_ready_surface",
        "controlled_variable": "prompt_gan_parser_ready_label_policy",
        "portability": "benchmark_format",
        "status": "active",
        "description": (
            "Prompt bans prose and symbols in final_label and asks for Gan-parser-compatible "
            "label syntax."
        ),
    },
    {
        "policy_id": "sct_v5.gan_label.interval_preservation",
        "controlled_variable": "prompt_explicit_interval_preservation_policy",
        "portability": "gan2026_specific",
        "status": "active",
        "description": (
            "Prompt preserves explicit interval and range wording instead of rounding or "
            "softening it."
        ),
    },
    {
        "policy_id": "sct_v5.gan_label.cluster_dual_axis",
        "controlled_variable": "prompt_cluster_cadence_and_burden_policy",
        "portability": "gan2026_specific",
        "status": "active",
        "description": (
            "Prompt preserves both cluster cadence and per-cluster burden when both are stated."
        ),
    },
    {
        "policy_id": "sct_v5.schema.cluster_axis_state",
        "controlled_variable": "prompt_cluster_axis_state_policy",
        "portability": "seizure_frequency",
        "status": "active",
        "description": (
            "Prompt requires each claim and final selector decision to expose whether cluster "
            "cadence, per-cluster burden, both axes, or only vague clustering is present."
        ),
    },
    {
        "policy_id": "sct_v5.selection.current_burden_precedence",
        "controlled_variable": "prompt_current_burden_selection_policy",
        "portability": "seizure_frequency",
        "status": "active",
        "description": (
            "Prompt selects the highest current or recent seizure burden unless an overall "
            "count is given."
        ),
    },
    {
        "policy_id": "sct_v5.selection.add_same_window_counts",
        "controlled_variable": "prompt_same_window_count_addition_policy",
        "portability": "gan2026_specific",
        "status": "active",
        "description": (
            "Prompt adds exact counts across active semiologies in the same current window."
        ),
    },
    {
        "policy_id": "sct_v5.boundary.unknown_no_reference_seizure_free",
        "controlled_variable": "prompt_boundary_answer_policy",
        "portability": "seizure_frequency",
        "status": "active",
        "description": (
            "Prompt separates unknown, no seizure frequency reference, and seizure-free answers."
        ),
    },
    {
        "policy_id": "sct_v5.schema.boundary_state",
        "controlled_variable": "prompt_boundary_state_policy",
        "portability": "seizure_frequency",
        "status": "active",
        "description": (
            "Prompt requires explicit boundary-state fields so unknown, no-reference, "
            "seizure-free, proxy, last-event-only, and conditional/window-limited cases "
            "remain inspectable before scoring."
        ),
    },
    {
        "policy_id": "sct_v5.exclusion.proxy_or_conditional_frequency",
        "controlled_variable": "prompt_proxy_conditional_exclusion_policy",
        "portability": "seizure_frequency",
        "status": "active",
        "description": (
            "Prompt excludes proxy, conditional, rescue-medication, and non-epileptic counts "
            "unless they explicitly state current epileptic seizure burden."
        ),
    },
    {
        "policy_id": "sct_v5.gan_label.compact_interval_notation",
        "controlled_variable": "prompt_compact_interval_notation_policy",
        "portability": "gan2026_specific",
        "status": "active",
        "description": "Prompt maps compact interval notation such as q2-3wk to 1 per 2 to 3 week.",
    },
    {
        "policy_id": "sct_v5.gan_label.maximum_burden",
        "controlled_variable": "prompt_maximum_current_burden_policy",
        "portability": "gan2026_specific",
        "status": "active",
        "description": (
            "Prompt preserves explicit maximum current burden instead of converting it to multiple."
        ),
    },
    {
        "policy_id": "sct_v5.selection.constrained_selector",
        "controlled_variable": "prompt_constrained_selector_policy",
        "portability": "seizure_frequency",
        "status": "active",
        "description": (
            "Prompt separates source-near claim extraction from a constrained final selector "
            "decision over selected claims."
        ),
    },
]
REQUIRED_ABLATIONS_BEFORE_LADDER: list[str] = [
    "raw_model_claim_table",
    "strict_schema_repair",
    "constrained_selector_state",
    "clean_scorer_facing_policy",
]
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_llm_only_claim_table_selector_validation25_gpt41mini_v5_2026-06-01.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_llm_only_claim_table_selector_validation25_gpt41mini_v5_2026-06-01.md"
)


class Gan2026LlmOnlyClaimTableSelectorSignature(dspy.Signature):
    """Extract section-local seizure-frequency claims, then answer from the table."""

    prompt_input_json: str = dspy.InputField(
        desc=(
            "JSON containing one clinical note and task instructions. It intentionally omits "
            "gold labels and deterministic candidate diagnostics."
        )
    )
    llm_only_claim_table_selector_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object with claims and final_query. Claims are source-near "
            "section-local facts; final_query selects the Gan-facing answer from them."
        )
    )


class DspyLlmOnlyClaimTableSelector(dspy.Module):
    """DSPy claim-table selector with no deterministic candidate inputs."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026LlmOnlyClaimTableSelectorSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def build_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the claim-table prompt payload, excluding gold labels."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": ("Gan 2026 LLM-only claim-table selector diagnostic extraction"),
        "source_row_index": record.source_row_index,
        "prompt_policy_taxonomy": PROMPT_POLICY_TAXONOMY,
        "required_ablations_before_ladder_runs": REQUIRED_ABLATIONS_BEFORE_LADDER,
        "instructions": [
            "Read the full clinical note and make a flat table of seizure-frequency claims.",
            "Do not use deterministic rule candidates; this input contains only the note.",
            (
                "Each claim should stay source-near: preserve its local section or text zone, "
                "evidence substring, temporality, assertion status, semiology, and uncertainty."
            ),
            (
                "For claim_type, temporality, assertion_status, uncertainty, answer_kind, "
                "and confidence, return one scalar string from the schema enum, not a list. "
                "If two enum values seem plausible, choose the best primary value and explain "
                "the ambiguity in rationale."
            ),
            (
                "Do not use historical as claim_type. Historical is represented only by "
                "temporality or assertion_status; choose the source-near clinical claim type "
                "from the schema enum instead."
            ),
            (
                "Keep current/recent, historical, negated, no-reference, seizure-free, "
                "last-event-only, and unclear-frequency statements as separate claim rows."
            ),
            (
                "After producing claim rows, run a constrained final selector over the table. "
                "Choose selector_decision from the enum, copy selected_claim_ids, preserve "
                "cluster_axis and boundary_state in final_query, then produce the Gan-facing "
                "answer. Do not let final_label hide whether the answer came from cluster-axis "
                "preservation or a boundary-state decision."
            ),
            (
                "Keep raw_selected_frequency source-near, but make final_label a parser-ready "
                "Gan-compatible label such as 1 per day, 2 to 3 per month, "
                "multiple per week, 1 per 2 day, 1 per 7 to 10 day, "
                "2 per 2 week, 1 per 2 month, seizure free for 6 month, unknown, "
                "or no seizure frequency reference."
            ),
            (
                "Do not put inequality symbols, prose such as daily/yearly/bimonthly, "
                "or phrases like every other week in final_label. Convert them to the "
                "closest Gan label while preserving the selected clinical fact."
            ),
            (
                "Preserve explicit intervals in final_label instead of rounding them: "
                "every 3 to 4 weeks -> 1 per 3 to 4 week; twice every two weeks -> "
                "2 per 2 week; once every seven to ten days -> 1 per 7 to 10 day."
            ),
            (
                "Preserve explicit counted ranges even when wording uses alternatives: "
                "5 or 7 focal onset seizures in three weeks -> 5 to 7 per 3 week. "
                "Do not soften a counted range to multiple."
            ),
            (
                "Convert twice per ordinary calendar unit directly: twice a month -> "
                "2 per month; twice a week -> 2 per week. Do not turn twice a month "
                "into every two months."
            ),
            (
                "In these Gan synthetic letters, bimonthly means every two months "
                "unless the text explicitly says twice per month; use 1 per 2 month."
            ),
            (
                "Do not emit a cluster final_label unless the selected claim truly states "
                "cluster frequency with both cluster cadence and event burden. Vague "
                "clustering around an ordinary rate should stay an ordinary frequency. Mark "
                "claim.cluster_axis and final_query.cluster_axis so the axis decision is "
                "reviewable before scoring."
            ),
            (
                "When the selected current claim states both cluster cadence and per-cluster "
                "burden, preserve both parts in final_label: one cluster each month with six "
                "to seven seizures in a cluster -> 1 cluster per month, 6 to 7 per cluster. "
                "Do not flatten this to 6 to 7 per day, multiple per month, or 1 per day."
            ),
            (
                "Cluster cadence can be the ordinary Gan-facing frequency when a cluster "
                "statement gives only timing, such as every seven to nine days -> "
                "1 per 7 to 9 day. Use unknown only when the current cadence cannot be "
                "converted."
            ),
            (
                "An explicit current cluster cadence normally outranks an isolated lower-burden "
                "recent subtype count with an assumed denominator. For example, if events tend "
                "to cluster every seven to nine days and the note separately mentions two "
                "recent nocturnal tonic-clonic seizures, choose 1 per 7 to 9 day unless the "
                "note says the cadence is non-epileptic, historical, or not the Gan target."
            ),
            (
                "When a recent quantified event burden is followed by a short seizure-free "
                "span, prefer the quantified recent burden for Gan-facing final_label unless "
                "the note explicitly frames the patient as currently seizure-free overall."
            ),
            (
                "For Gan-style labels, a short subsequent seizure-free span does not by itself "
                "erase a counted recent event range in the same current clinical interval. "
                "Keep the counted range, such as 5 or 7 focal onset seizures in three weeks -> "
                "5 to 7 per 3 week, unless the whole letter clearly makes seizure freedom the "
                "overall current answer."
            ),
            (
                "For vague but recurring monthly burden, use accepted category wording in "
                "final_label: several events across most months -> multiple per month. Keep "
                "phrases like several per month in raw_selected_frequency, not final_label."
            ),
            (
                "If multiple current seizure semiologies are active, select the highest "
                "current or recent seizure burden unless the note gives an overall count."
            ),
            (
                "If multiple active seizure semiologies have exact counts in the same current "
                "window, add the counts and preserve the shared denominator in final_label: "
                "six drop attacks plus two absence seizures over two months -> 8 per 2 month. "
                "Do not omit a semiology or soften an exact total to multiple."
            ),
            (
                "Do not convert window-limited hormonal, perimenstrual, rescue-medication, "
                "conditional, or last-event-only statements into ordinary rates unless an "
                "event count and denominator are explicitly stated for current seizure burden. "
                "Use unknown when the note discusses seizures but the current frequency cannot "
                "be converted."
            ),
            (
                "Separate boundary answers carefully: no seizure frequency reference means no "
                "usable seizure-frequency evidence; seizure_free means definite epileptic "
                "seizures are negated for a stated current interval; unknown means seizure "
                "evidence exists but the frequency is vague, conditional, proxy-only, or not "
                "convertible. Mark claim.boundary_state and final_query.boundary_state with "
                "the reason rather than relying only on final_label."
            ),
            (
                "Rescue medication use frequency, caregiver concern, falls, collapses, and "
                "non-epileptic-like episodes are not seizure-frequency counts unless the note "
                "explicitly ties them to definite epileptic seizures."
            ),
            (
                "Preserve compact every-interval notation correctly: q2-3wk, qtwo-threewk, "
                "or every two to three weeks means 1 per 2 to 3 week, not 2 to 3 per week."
            ),
            (
                "When the source gives an explicit maximum current burden such as up to once "
                "daily or as many as seven in a week, preserve the maximum as 7 per week "
                "instead of softening it to multiple per week."
            ),
            (
                "Use unknown when seizures or seizure-like events are discussed but current "
                "frequency cannot be converted to a Gan-compatible rate."
            ),
            (
                "Use no seizure frequency reference only when the note contains no usable "
                "seizure-frequency evidence."
            ),
            "Every evidence value must be an exact substring from the note when possible.",
            (
                "The final_query evidence must also be an exact substring from the note. "
                "Copy the evidence field verbatim from one selected claim row instead of "
                "paraphrasing it."
            ),
            "Return exactly one JSON object with no markdown.",
        ],
        "claim_schema": {
            "claim_id": "stable string such as c1",
            "section": "source section or local zone, or null",
            "claim_type": [
                "frequency",
                "cluster_frequency",
                "seizure_free",
                "last_event_only",
                "unknown_frequency",
                "no_reference",
                "non_seizure_event",
            ],
            "evidence": "exact note substring supporting this claim",
            "anchor_text": "short local anchor text, or null",
            "raw_frequency": "source-near frequency expression, or null",
            "cluster_axis": [
                "none",
                "cadence_only",
                "burden_only",
                "cadence_and_burden",
                "vague_cluster",
            ],
            "boundary_state": [
                "ordinary_frequency",
                "seizure_free_interval",
                "unknown_frequency",
                "no_frequency_reference",
                "non_epileptic_or_proxy",
                "last_event_only",
                "conditional_or_window_limited",
            ],
            "temporality": ["current", "recent", "historical", "future", "unclear"],
            "assertion_status": [
                "asserted",
                "negated",
                "historical",
                "hypothetical",
                "unknown",
            ],
            "semiology": "seizure type or clinical target, or null",
            "uncertainty": ["low", "medium", "high"],
        },
        "final_query_schema": {
            "selected_claim_ids": "claim IDs used to select the answer",
            "selector_decision": [
                "select_single_claim",
                "combine_same_window_claims",
                "preserve_cluster_axis",
                "boundary_unknown",
                "boundary_no_reference",
                "boundary_seizure_free",
                "unresolved_conflict",
            ],
            "answer_kind": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "cluster_axis": [
                "none",
                "cadence_only",
                "burden_only",
                "cadence_and_burden",
                "vague_cluster",
            ],
            "boundary_state": [
                "ordinary_frequency",
                "seizure_free_interval",
                "unknown_frequency",
                "no_frequency_reference",
                "non_epileptic_or_proxy",
                "last_event_only",
                "conditional_or_window_limited",
            ],
            "raw_selected_frequency": (
                "source-near selected frequency text before Gan label conversion, or null"
            ),
            "final_label": (
                "Gan-compatible label, or null if answer_kind implies unknown/no_reference"
            ),
            "conversion_note": (
                "brief explanation of any source-near to Gan-compatible label conversion"
            ),
            "evidence": "exact note substring supporting the final answer",
            "confidence": ["low", "medium", "high"],
            "rationale": "brief reason for choosing these claim rows",
        },
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def run_split(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    reuse_raw_outputs: Mapping[int, str] | None = None,
    reuse_source: str | None = None,
    escalation_reason: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    reuse_raw_outputs = reuse_raw_outputs or {}
    metadata = _run_metadata(
        records,
        split=split,
        split_manifest=split_manifest,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        api_base=api_base,
    )
    metadata["dspy_cache"] = dspy_cache
    metadata["reuse_source"] = reuse_source
    metadata["escalation_reason"] = escalation_reason
    metadata["repair_mode_layers"] = repair_mode_layers(
        ("raw_model", "strict_format", "clean_scorer_facing")
    )
    program = DspyLlmOnlyClaimTableSelector()
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

    rows: list[dict[str, Any]] = []
    for record in records:
        prompt_input_json = build_prompt_input(record)
        raw_output = reuse_raw_outputs.get(record.source_row_index, "")
        call_error: str | None = None
        reused_raw_output = raw_output != ""
        if mode == "live" and not reused_raw_output:
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.llm_only_claim_table_selector_json)
            except Exception as exc:  # pragma: no cover - exercised only with live APIs.
                call_error = f"{type(exc).__name__}: {exc}"

        extraction, parse_errors = (
            parse_llm_only_claim_table_selector_json(raw_output, note_text=record.note_text)
            if raw_output
            else (None, ["not_run"])
        )
        evidence_summary = (
            _evidence_summary(record.note_text, extraction)
            if extraction
            else _empty_evidence_summary()
        )
        score_layers = _score_layers(record, extraction)
        repair_changes = _repair_changes(score_layers)
        component_status = _component_status(
            extraction=extraction,
            parse_errors=parse_errors,
            evidence_summary=evidence_summary,
            score_layers=score_layers,
            call_error=call_error,
        )
        rows.append(
            {
                "source_row_index": record.source_row_index,
                "split": split,
                "split_manifest": split_manifest,
                "pipeline_name": PROMPT_VERSION,
                "prompt_version": PROMPT_VERSION,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "reused_raw_output": reused_raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "structured_record": extraction.model_dump() if extraction else None,
                "component_status": component_status,
                "evidence_summary": evidence_summary,
                "score_layers": score_layers,
                "repair_changes": repair_changes,
                "repair_mode_layers": repair_mode_layers(
                    ("raw_model", "strict_format", "clean_scorer_facing")
                ),
                "reference": {
                    "gold_label": record.gold_label,
                    "gold_normalized_label": record.gold_normalized_label,
                    "gold_label_kind": str(record.gold_label_kind),
                    "gold_monthly_frequency": record.gold_monthly_frequency,
                    "row_ok": record.row_ok,
                },
            }
        )
        if progress_every and len(rows) % progress_every == 0:
            _emit_progress_checkpoint(
                rows,
                metadata,
                total=len(records),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
            )

    metadata["summary"] = summarize_records(rows)
    return rows, metadata


def summarize_records(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    count = len(rows)
    claim_evidence_valid = sum(
        int((row.get("evidence_summary") or {}).get("claim_evidence_valid", 0)) for row in rows
    )
    claim_evidence_total = sum(
        int((row.get("evidence_summary") or {}).get("claim_evidence_total", 0)) for row in rows
    )
    selected_evidence_valid = sum(
        int(bool((row.get("evidence_summary") or {}).get("selected_evidence_valid")))
        for row in rows
    )
    raw = _layer_summary(rows, "raw")
    strict = _layer_summary(rows, "strict_format")
    clean = _layer_summary(rows, "clean_scorer_facing")
    component_failures = Counter(
        component
        for row in rows
        for component, status in (row.get("component_status") or {}).items()
        if status != "ok"
    )
    return {
        "examples": count,
        "structured_records": sum(bool(row.get("structured_record")) for row in rows),
        "call_failures": sum(bool(row.get("call_error")) for row in rows),
        "reused_raw_outputs": sum(bool(row.get("reused_raw_output")) for row in rows),
        "parse_or_validation_failures": sum(
            _has_blocking_parse_issue(row.get("parse_errors")) for row in rows
        ),
        "claim_evidence_valid": claim_evidence_valid,
        "claim_evidence_total": claim_evidence_total,
        "selected_evidence_valid": selected_evidence_valid,
        "raw_scorable": raw["scorable"],
        "raw_purist_correct": raw["purist_correct"],
        "raw_purist_accuracy": raw["purist_accuracy"],
        "raw_pragmatic_correct": raw["pragmatic_correct"],
        "raw_pragmatic_accuracy": raw["pragmatic_accuracy"],
        "strict_format_scorable": strict["scorable"],
        "strict_format_purist_correct": strict["purist_correct"],
        "strict_format_purist_accuracy": strict["purist_accuracy"],
        "strict_format_pragmatic_correct": strict["pragmatic_correct"],
        "strict_format_pragmatic_accuracy": strict["pragmatic_accuracy"],
        "clean_scorer_facing_scorable": clean["scorable"],
        "clean_scorer_facing_purist_correct": clean["purist_correct"],
        "clean_scorer_facing_purist_accuracy": clean["purist_accuracy"],
        "clean_scorer_facing_pragmatic_correct": clean["pragmatic_correct"],
        "clean_scorer_facing_pragmatic_accuracy": clean["pragmatic_accuracy"],
        "component_failures": dict(sorted(component_failures.items())),
        "repair_changed_rows": sum(bool(row.get("repair_changes")) for row in rows),
    }


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def load_reusable_raw_outputs(path: Path) -> dict[int, str]:
    return load_raw_outputs_by_source_index(path)


def _score_layers(
    record: GanFrequencyRecord,
    extraction: SectionClaimTableExtractionRecord | None,
) -> dict[str, dict[str, Any]]:
    raw_label = _raw_final_label(extraction)
    strict_label = repair_prediction_label_format_preserving(raw_label) if raw_label else None
    clean_label = repair_prediction_label_clean_scorer_facing(raw_label) if raw_label else None
    return {
        "raw": _score_label(record, raw_label, repair_mode="raw_model"),
        "strict_format": _score_label(record, strict_label, repair_mode="strict_format"),
        "clean_scorer_facing": _score_label(
            record,
            clean_label,
            repair_mode="clean_scorer_facing",
        ),
    }


def _raw_final_label(extraction: SectionClaimTableExtractionRecord | None) -> str | None:
    if extraction is None:
        return None
    if extraction.final_query.final_label:
        return extraction.final_query.final_label
    if extraction.final_query.answer_kind == "unknown":
        return "unknown"
    if extraction.final_query.answer_kind == "no_reference":
        return "no seizure frequency reference"
    return None


def _score_label(
    record: GanFrequencyRecord,
    label: str | None,
    *,
    repair_mode: str,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "final_label": label,
        "scorable": False,
        "repair_mode_metadata": repair_mode_metadata(repair_mode),
    }
    if not label:
        result["error"] = "missing_final_label"
        return result
    try:
        predicted_record = label_to_frequency_record(label)
    except ValueError as exc:
        result["error"] = str(exc)
        return result
    gold_purist = str(map_purist(record.gold_monthly_frequency))
    predicted_purist = str(map_purist(predicted_record.monthly_frequency))
    gold_pragmatic = str(map_pragmatic(record.gold_monthly_frequency))
    predicted_pragmatic = str(map_pragmatic(predicted_record.monthly_frequency))
    result.update(
        {
            "scorable": True,
            "predicted_monthly_frequency": predicted_record.monthly_frequency,
            "gold_monthly_frequency": record.gold_monthly_frequency,
            "predicted_purist_category": predicted_purist,
            "gold_purist_category": gold_purist,
            "purist_correct": predicted_purist == gold_purist,
            "predicted_pragmatic_category": predicted_pragmatic,
            "gold_pragmatic_category": gold_pragmatic,
            "pragmatic_correct": predicted_pragmatic == gold_pragmatic,
        }
    )
    return result


def _repair_changes(score_layers: Mapping[str, Mapping[str, Any]]) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    previous_layer = "raw"
    previous = score_layers["raw"].get("final_label")
    for layer in ["strict_format", "clean_scorer_facing"]:
        current = score_layers[layer].get("final_label")
        if isinstance(previous, str) and isinstance(current, str) and current != previous:
            changes.append({"layer": layer, "before": previous, "after": current})
        previous_layer = layer
        previous = score_layers[previous_layer].get("final_label")
    return changes


def _evidence_summary(
    note_text: str,
    extraction: SectionClaimTableExtractionRecord | None,
) -> dict[str, Any]:
    if extraction is None:
        return _empty_evidence_summary()
    claim_validity = []
    invalid_claim_evidence = []
    for claim in extraction.claims:
        valid = evidence_is_substring(note_text, claim.evidence)
        claim_validity.append(valid)
        if not valid:
            invalid_claim_evidence.append(
                {
                    "claim_id": claim.claim_id,
                    "evidence": claim.evidence,
                }
            )
    selected_valid = evidence_is_substring(note_text, extraction.final_query.evidence)
    summary: dict[str, Any] = {
        "claim_evidence_valid": sum(claim_validity),
        "claim_evidence_total": len(claim_validity),
        "claim_evidence_invalid": invalid_claim_evidence,
        "selected_evidence_valid": selected_valid,
        "selected_evidence": extraction.final_query.evidence,
    }
    return summary


def _empty_evidence_summary() -> dict[str, Any]:
    return {
        "claim_evidence_valid": 0,
        "claim_evidence_total": 0,
        "claim_evidence_invalid": [],
        "selected_evidence_valid": False,
        "selected_evidence": None,
    }


def _component_status(
    *,
    extraction: SectionClaimTableExtractionRecord | None,
    parse_errors: Sequence[str],
    evidence_summary: Mapping[str, Any],
    score_layers: Mapping[str, Mapping[str, Any]],
    call_error: str | None,
) -> dict[str, str]:
    status = {
        "segmentation_sectioning": "ok",
        "claim_extraction": "ok",
        "temporality_conflict": "ok",
        "final_query": "ok",
        "parse_schema": "ok",
        "scorer_format": "ok",
    }
    if call_error or _has_blocking_parse_issue(parse_errors):
        status["parse_schema"] = "fail"
    if extraction is None:
        status["claim_extraction"] = "fail"
        status["final_query"] = "fail"
        status["scorer_format"] = "fail"
        return status
    if not extraction.claims or any(
        error.startswith("claim_extraction:") for error in parse_errors
    ):
        status["claim_extraction"] = "fail"
    if not any(claim.section for claim in extraction.claims):
        status["segmentation_sectioning"] = "fail"
    if any(error.startswith("final_query:") for error in parse_errors):
        status["final_query"] = "fail"
    selected_ids = set(extraction.final_query.selected_claim_ids)
    selected_claims = [claim for claim in extraction.claims if claim.claim_id in selected_ids]
    if selected_claims and all(
        claim.temporality in {"historical", "future"} for claim in selected_claims
    ):
        status["temporality_conflict"] = "fail"
    if evidence_summary.get("claim_evidence_valid") != evidence_summary.get("claim_evidence_total"):
        status["claim_extraction"] = "fail"
    if not evidence_summary.get("selected_evidence_valid"):
        status["final_query"] = "fail"
    if not score_layers["raw"].get("scorable"):
        status["scorer_format"] = "fail"
    return status


def _layer_summary(rows: Sequence[Mapping[str, Any]], layer: str) -> dict[str, Any]:
    count = len(rows)
    layer_rows = [(row.get("score_layers") or {}).get(layer) or {} for row in rows]
    scorable = sum(bool(row.get("scorable")) for row in layer_rows)
    purist = sum(bool(row.get("purist_correct")) for row in layer_rows)
    pragmatic = sum(bool(row.get("pragmatic_correct")) for row in layer_rows)
    return {
        "scorable": scorable,
        "purist_correct": purist,
        "purist_accuracy": round(purist / count, 4) if count else 0.0,
        "pragmatic_correct": pragmatic,
        "pragmatic_accuracy": round(pragmatic / count, 4) if count else 0.0,
    }


def _has_blocking_parse_issue(errors: Any) -> bool:
    return any(
        str(error).startswith(
            (
                "invalid_json:",
                "schema_validation_error:",
                "not_run",
            )
        )
        for error in errors or []
    )


def _emit_progress_checkpoint(
    rows: Sequence[Mapping[str, Any]],
    metadata: dict[str, Any],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
) -> None:
    metadata["summary"] = summarize_records(rows)
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None and jsonl_path is not None:
        write_report(rows, metadata, report_path, jsonl_path=jsonl_path)
    progress = {
        "processed": len(rows),
        "total": total,
        "call_failures": metadata["summary"]["call_failures"],
        "clean_purist_accuracy_so_far": metadata["summary"]["clean_scorer_facing_purist_accuracy"],
        "raw_scorable": metadata["summary"]["raw_scorable"],
        "reused_raw_outputs": metadata["summary"]["reused_raw_outputs"],
    }
    print(json.dumps(progress, sort_keys=True), file=sys.stderr, flush=True)


def _run_metadata(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: str,
    api_base: str | None = None,
) -> dict[str, Any]:
    return build_run_metadata(
        mode=mode,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        prompt_version=PROMPT_VERSION,
        dspy_version=getattr(dspy, "__version__", "unknown"),
        split=split,
        split_manifest=split_manifest,
        api_base=api_base,
        row_count=len(records),
        extra={
            "pipeline_name": PROMPT_VERSION,
            "prompt_policy_ids": [policy["policy_id"] for policy in PROMPT_POLICY_TAXONOMY],
            "required_ablations_before_ladder_runs": REQUIRED_ABLATIONS_BEFORE_LADDER,
        },
    )
