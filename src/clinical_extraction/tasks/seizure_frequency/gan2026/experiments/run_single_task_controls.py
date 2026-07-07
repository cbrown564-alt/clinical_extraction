"""Runner to execute Gan 2026 RQ1/RQ2 component-control rows."""

import argparse
import json
from pathlib import Path

import dspy
from tqdm import tqdm

from clinical_extraction.tasks.seizure_frequency.gan2026.contract import label_parser
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments import (
    single_task_control_prompts as prompt_builders,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import Gan2026PipelineV1

# Load configuration and panel rows
PANEL_JSONL_PATH = Path("experiments/gan2026_rq1_rq2_single_task_control_panels_2026-06-04.jsonl")
MATRIX_JSONL_PATH = Path("experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.jsonl")
MATRIX_REPORT_PATH = Path("experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.md")
SOURCE_ID = "note"


class Gan2026SingleTaskControlSignature(dspy.Signature):
    """Run a single clinical extraction subtask control prompt."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON input containing task instructions, source text, and output schema."
    )
    control_output_json: str = dspy.OutputField(
        desc="JSON output object matching the requested schema."
    )


class DspySingleTaskControl(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026SingleTaskControlSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def map_candidate_to_schema(candidate_event, normalized_event) -> dict:
    label = normalized_event["normalized_label"]
    components = {}
    try:
        rec = label_parser.label_to_frequency_record(label)
        if rec.kind.name == "FREQUENCY":
            components["count"] = rec.raw_phrase or "1"
            components["rate_time_basis"] = "month"
        elif rec.kind.name == "SEIZURE_FREE":
            components["seizure_free_duration"] = label
    except Exception:
        pass

    kind_mapping = {
        "frequency_rate": "frequency_rate",
        "cluster_frequency": "cluster_frequency",
        "seizure_free": "seizure_free",
        "last_event_only": "last_event_only",
        "unknown_frequency": "unknown_frequency",
        "no_reference": "no_reference",
    }
    cand_kind = kind_mapping.get(normalized_event["semantic_kind"], "frequency_rate")

    return {
        "candidate_id": candidate_event["event_id"],
        "source_id": "note",
        "evidence": candidate_event["evidence"],
        "candidate_kind": cand_kind,
        "temporality": "current",
        "assertion_status": "asserted",
        "applies_to": candidate_event.get("applies_to"),
        "components": {
            "count": components.get("count"),
            "timeframe": components.get("timeframe"),
            "unit": components.get("unit"),
            "rate_time_basis": components.get("rate_time_basis"),
            "cluster_cadence": components.get("cluster_cadence"),
            "per_cluster_burden": components.get("per_cluster_burden"),
            "seizure_free_duration": components.get("seizure_free_duration"),
        },
        "ambiguity_reasons": [],
        "normalization_note": None,
        "confidence": "high",
        "rationale": "deterministic rule",
    }


def map_evidence_to_schema(final_selection, candidate_event, normalized_event) -> dict:
    cand = map_candidate_to_schema(candidate_event, normalized_event)
    return {
        "evidence_id": "e1",
        "source_id": "note",
        "evidence": final_selection["evidence"],
        "role": "decisive",
        "support_status": "supports_candidate",
        "applies_to": cand.get("applies_to"),
        "extracted_components": cand["components"],
        "missing_components": [],
        "conflict_notes": [],
        "ambiguity_reasons": [],
        "confidence": "high",
        "rationale": "deterministic selection",
    }


def selected_candidate_and_normalized_event(diag: dict) -> tuple[dict, dict]:
    final_sel = diag["final_selection"]
    cand_event = next(
        (
            candidate
            for candidate in diag["candidate_events"]
            if candidate["event_id"] == final_sel.get("event_id")
        ),
        diag["candidate_events"][0],
    )
    norm_event = next(
        (
            normalized
            for normalized in diag["normalized_events"]
            if normalized["event_id"] == cand_event["event_id"]
        ),
        diag["normalized_events"][0],
    )
    return cand_event, norm_event


def main():
    args = parse_args()
    model = args.model
    temperature = args.temperature
    max_tokens = args.max_tokens

    # Configure DSPy
    lm = build_dspy_lm(model, temperature=temperature, max_tokens=max_tokens, cache=True)
    dspy.configure(lm=lm)

    # Load all validation records to fetch raw text
    validation_records = {r.source_row_index: r for r in load_records_for_split("validation")}

    # Load the component control matrix rows to preserve structure
    matrix_rows = load_jsonl_rows(MATRIX_JSONL_PATH)

    target_panels = set(args.panels)
    target_conditions = set(args.conditions)

    runner = DspySingleTaskControl()

    pipeline = Gan2026PipelineV1()

    updated_rows = []

    print(
        "Running RQ1/RQ2 component controls for panels "
        f"{sorted(target_panels)} and conditions {sorted(target_conditions)}..."
    )
    for row in tqdm(matrix_rows):
        if row["row_panel_id"] not in target_panels or row["condition_id"] not in target_conditions:
            updated_rows.append(row)
            continue
        if row.get("component_output") and not args.force:
            updated_rows.append(row)
            continue

        source_idx = row["source_row_index"]
        record = validation_records.get(source_idx)
        if not record:
            updated_rows.append(row)
            continue

        condition_id = row["condition_id"]

        # Run deterministic pipeline for context if needed
        res = pipeline.run(record)
        diag = res.diagnostics

        prompt_input = ""
        if condition_id == "candidate_only":
            prompt_input = prompt_builders.build_candidate_only_prompt_input(record)
        elif condition_id == "gold_query_evidence_only":
            prompt_input = prompt_builders.build_gold_query_evidence_only_prompt_input(record)
        elif condition_id == "candidate_conditioned_evidence_only":
            # Condition on the deterministic selected candidate
            cand_event, norm_event = selected_candidate_and_normalized_event(diag)
            cand_schema = map_candidate_to_schema(cand_event, norm_event)
            prompt_input = prompt_builders.build_candidate_conditioned_evidence_only_prompt_input(
                record, cand_schema
            )
        elif condition_id == "projection_only":
            final_sel = diag["final_selection"]
            cand_event, norm_event = selected_candidate_and_normalized_event(diag)
            cand_schema = map_candidate_to_schema(cand_event, norm_event)
            ev_schema = map_evidence_to_schema(final_sel, cand_event, norm_event)
            prompt_input = prompt_builders.build_projection_only_prompt_input(
                record, [cand_schema], [ev_schema], input_source="deterministic"
            )
        elif condition_id == "projection_only_instruction_heavy":
            final_sel = diag["final_selection"]
            cand_event, norm_event = selected_candidate_and_normalized_event(diag)
            cand_schema = map_candidate_to_schema(cand_event, norm_event)
            ev_schema = map_evidence_to_schema(final_sel, cand_event, norm_event)
            prompt_input = prompt_builders.build_projection_only_instruction_heavy_prompt_input(
                record,
                [cand_schema],
                [ev_schema],
                input_source="deterministic",
            )
        elif condition_id == "candidate_plus_evidence":
            prompt_input = prompt_builders.build_candidate_plus_evidence_prompt_input(record)
        elif condition_id == "evidence_plus_projection":
            cand_event, norm_event = selected_candidate_and_normalized_event(diag)
            cand_schema = map_candidate_to_schema(cand_event, norm_event)
            prompt_input = prompt_builders.build_evidence_plus_projection_prompt_input(
                record, cand_schema
            )
        elif condition_id == "candidate_plus_evidence_plus_projection":
            prompt_input = (
                prompt_builders.build_candidate_plus_evidence_plus_projection_prompt_input(record)
            )

        # Call prediction
        raw_output = ""
        try:
            pred = runner(prompt_input_json=prompt_input)
            raw_output = str(pred.control_output_json)
        except Exception as e:
            raw_output = json.dumps({"error": str(e)})

        # Try to parse and update output fields
        parsed_out = {}
        try:
            # Strip JSON markdown fences if present
            clean_out = raw_output.strip()
            if clean_out.startswith("```"):
                clean_out = clean_out.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            parsed_out = json.loads(clean_out)
        except Exception:
            parsed_out = {"raw_output": raw_output}

        # Update control matrix row
        row["model_id"] = model
        row["prompt_version"] = prompt_builders.PROMPT_VERSIONS.get(condition_id, "v0")
        row["component_output"] = parsed_out
        row["claim_boundary"] = "validation_development_isolated_control_run"

        exact_ev = exact_evidence_status(parsed_out, record.note_text)
        row["exact_evidence_status"] = exact_ev
        row["source_id_status"] = source_id_status(parsed_out)

        # Populate basic metrics
        row["component_metrics"] = {
            "parsed_successfully": "error" not in parsed_out,
            "exact_evidence": exact_ev == "exact",
        }

        updated_rows.append(row)

    # Write matrix updates
    write_jsonl_rows(updated_rows, MATRIX_JSONL_PATH)
    print("Done running RQ1/RQ2 component controls.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=3000)
    parser.add_argument(
        "--panels",
        nargs="+",
        default=["balanced_validation50", "hidden_family_hard_panel"],
    )
    parser.add_argument(
        "--conditions",
        nargs="+",
        default=[
            "candidate_only",
            "gold_query_evidence_only",
            "candidate_conditioned_evidence_only",
            "projection_only",
            "candidate_plus_evidence",
            "evidence_plus_projection",
            "candidate_plus_evidence_plus_projection",
        ],
    )
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def exact_evidence_status(parsed_out: dict, note_text: str) -> str:
    evidence_values = list(iter_evidence_values(parsed_out))
    if not evidence_values:
        return "not_checked"
    return "exact" if all(value in note_text for value in evidence_values) else "not_exact"


def source_id_status(parsed_out: dict) -> str:
    source_ids = list(iter_source_ids(parsed_out))
    if not source_ids:
        return "not_instrumented"
    return "valid" if all(source_id == SOURCE_ID for source_id in source_ids) else "invalid"


def iter_evidence_values(value):
    if isinstance(value, dict):
        if isinstance(value.get("evidence"), str):
            yield value["evidence"]
        for child in value.values():
            yield from iter_evidence_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_evidence_values(child)


def iter_source_ids(value):
    if isinstance(value, dict):
        if isinstance(value.get("source_id"), str):
            yield value["source_id"]
        for child in value.values():
            yield from iter_source_ids(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_source_ids(child)


if __name__ == "__main__":
    main()
