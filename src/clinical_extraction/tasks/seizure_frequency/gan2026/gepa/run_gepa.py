"""Single-experiment GEPA driver for Gan 2026 (resumable, registry-aware).

Compiles a from-scratch GEPA program against the frozen ``train`` split, then
evaluates the optimized program on a development split (never ``test``), writing
the evolved instruction, per-row eval, a JSON/Markdown summary, and a registry
entry. The optimizer log dir lets a crashed run resume; the orchestrator skips
experiments whose summary JSON already exists.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import dspy

from clinical_extraction.core.registry import (
    RunRegistryEntry,
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026 import data as gan_data
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    write_run_registry_markdown,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.gepa import data as gepa_data
from clinical_extraction.tasks.seizure_frequency.gan2026.gepa.metric import (
    LengthPenaltyConfig,
    approx_tokens,
    build_metric,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.gepa.program import (
    OUTPUT_SCHEMA_JSON,
    GepaStructuredExtractor,
    build_from_scratch_program,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    boundary_band,
    map_pragmatic,
    map_purist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredRepairConfig,
    parse_structured_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

ROOT = Path(__file__).resolve().parents[6]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"
GEPA_LOG_ROOT = EXPERIMENTS / "gepa_overnight"


@dataclass(frozen=True)
class GepaExperimentConfig:
    """One GEPA experiment: task model, optimizer budget, eval surface, penalty."""

    run_id: str
    task_model: str
    reflection_model: str = "deepseek/deepseek-reasoner"
    api_base: str | None = None
    task_temperature: float = 0.0
    task_max_tokens: int = 12000
    reflection_temperature: float = 1.0
    reflection_max_tokens: int = 12000
    auto: str | None = "medium"
    max_metric_calls: int | None = None
    valset_size: int | None = 200
    trainset_size: int | None = None
    final_eval_split: str = "validation"
    final_eval_limit: int | None = None
    num_threads: int = 12
    reflection_minibatch_size: int = 3
    length_penalty: LengthPenaltyConfig = field(default_factory=LengthPenaltyConfig)
    date: str = "2026-06-27"
    seed: int = 0
    notes: str = ""


def _build_reflection_lm(config: GepaExperimentConfig) -> dspy.LM:
    return build_dspy_lm(
        config.reflection_model,
        temperature=config.reflection_temperature,
        max_tokens=config.reflection_max_tokens,
        cache=False,
        api_base=None,
    )


def _configure_task_lm(config: GepaExperimentConfig) -> dspy.LM:
    lm = build_dspy_lm(
        config.task_model,
        temperature=config.task_temperature,
        max_tokens=config.task_max_tokens,
        cache=True,
        api_base=config.api_base,
    )
    dspy.configure(lm=lm)
    return lm


def _evaluate_program(
    program: GepaStructuredExtractor,
    records: list[gan_data.GanFrequencyRecord],
    *,
    num_threads: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the optimized program over records and score purist/pragmatic per row."""

    examples = [
        dspy.Example(note_text=r.note_text, output_schema=OUTPUT_SCHEMA_JSON).with_inputs(
            "note_text", "output_schema"
        )
        for r in records
    ]
    evaluator = dspy.Parallel(num_threads=num_threads, provide_traceback=True)
    exec_pairs = [
        (program, {"note_text": ex.note_text, "output_schema": ex.output_schema}) for ex in examples
    ]
    predictions = evaluator(exec_pairs)

    rows: list[dict[str, Any]] = []
    purist = pragmatic = scorable = 0
    for record, prediction in zip(records, predictions, strict=True):
        raw_output = str(getattr(prediction, "structured_json", "") or "") if prediction else ""
        extraction, _normalized, errors = (
            parse_structured_json(
                raw_output, note_text=record.note_text, repair_config=StructuredRepairConfig()
            )
            if raw_output
            else (None, [], ["empty_output"])
        )
        gold_purist = str(map_purist(record.gold_monthly_frequency))
        gold_pragmatic = str(map_pragmatic(record.gold_monthly_frequency))
        predicted_label = extraction.selection.final_label if extraction else None
        predicted_purist = predicted_pragmatic = None
        row_scorable = False
        if predicted_label:
            try:
                predicted_record = label_to_frequency_record(predicted_label)
                predicted_purist = str(map_purist(predicted_record.monthly_frequency))
                predicted_pragmatic = str(map_pragmatic(predicted_record.monthly_frequency))
                row_scorable = True
            except ValueError as exc:
                errors = [*errors, f"unscorable_final_label: {exc}"]
        purist_correct = bool(row_scorable and predicted_purist == gold_purist)
        pragmatic_correct = bool(row_scorable and predicted_pragmatic == gold_pragmatic)
        purist += int(purist_correct)
        pragmatic += int(pragmatic_correct)
        scorable += int(row_scorable)
        rows.append(
            {
                "source_row_index": record.source_row_index,
                "gold_label": record.gold_label,
                "gold_purist_category": gold_purist,
                "gold_band": boundary_band(record.gold_monthly_frequency),
                "predicted_label": predicted_label,
                "predicted_purist_category": predicted_purist,
                "purist_correct": purist_correct,
                "pragmatic_correct": pragmatic_correct,
                "scorable": row_scorable,
                "errors": errors,
                "raw_output_tokens": approx_tokens(raw_output),
            }
        )
    n = len(rows) or 1
    summary = {
        "rows": len(rows),
        "scorable": scorable,
        "purist_correct": purist,
        "purist_accuracy": round(purist / n, 4),
        "pragmatic_correct": pragmatic,
        "pragmatic_accuracy": round(pragmatic / n, 4),
    }
    return rows, summary


def _final_instruction(program: GepaStructuredExtractor) -> str:
    return str(program.extract.signature.instructions)


def _markdown(payload: dict[str, Any], instruction: str) -> str:
    s = payload["final_eval"]
    lp = payload["length_penalty"]
    lines = [
        f"# GEPA from-scratch — {payload['run_id']}",
        "",
        f"Date: {payload['date']}",
        "",
        (
            "DSPy-native GEPA run. The optimizable surface is the signature "
            "instruction; the deterministic schema-repair/normalize/purist stack is "
            "reused unchanged. Trained on the frozen `train` split (optimizer-only); "
            f"evaluated on `{payload['final_eval_split']}` (development surface, NOT test450)."
        ),
        "",
        "## Models",
        "",
        f"- Task model: `{payload['task_model']}` (temp {payload['task_temperature']}, "
        f"max_tokens {payload['task_max_tokens']})",
        f"- Reflection (teacher) model: `{payload['reflection_model']}`",
        f"- GEPA budget: auto={payload['auto']} max_metric_calls={payload['max_metric_calls']} "
        f"(trainset {payload['trainset_size']}, valset {payload['valset_size']})",
        "",
        "## Length penalty (prompt-bloat control)",
        "",
        f"- enabled: {lp['enabled']}",
        f"- instruction budget: {lp['instruction_token_budget']} tok "
        f"(beta {lp['beta_instruction']})",
        f"- demo budget: {lp['demo_token_budget']} tok (beta {lp['beta_demo']})",
        f"- output budget: {lp['output_token_budget']} tok (alpha {lp['alpha_output']})",
        f"- **final instruction length: {payload['final_instruction_tokens']} tokens** "
        f"(seed was {payload['seed_instruction_tokens']} tokens)",
        "",
        "## Final evaluation",
        "",
        f"- Purist: {s['purist_correct']} / {s['rows']} = **{s['purist_accuracy']:.3f}**",
        f"- Pragmatic: {s['pragmatic_correct']} / {s['rows']} = {s['pragmatic_accuracy']:.3f}",
        f"- Scorable rows: {s['scorable']} / {s['rows']}",
        "",
        "## Evolved instruction",
        "",
        "```text",
        instruction,
        "```",
        "",
        "## Provenance",
        "",
        (
            "`train` split is optimizer-only per `gan2026_split_v1` intended_use. "
            "Development-split result; necessary, NOT sufficient, for any test450 "
            "authorization. Length penalty is part of the GEPA selection metric, so a "
            "shorter evolved instruction is a recorded optimization outcome, not a "
            "post-hoc trim."
        ),
    ]
    return "\n".join(lines)


def _register(payload: dict[str, Any], artifact_names: list[str]) -> None:
    try:
        existing = load_run_registry(REGISTRY_PATH)
    except ValueError as exc:
        # A pre-existing malformed record blocks loading (and therefore registering).
        # The experiment artifacts are already written; do not crash the run over a
        # registry record we did not create. Surface it for manual repair instead.
        print(
            f"[gepa] WARNING: registry load failed, skipping registration of "
            f"{payload['run_id']}: {exc}",
            flush=True,
        )
        return
    entries = [e for e in existing if e.run_id != payload["run_id"]]
    s = payload["final_eval"]
    entries.append(
        RunRegistryEntry(
            run_id=payload["run_id"],
            artifact_paths=tuple(f"experiments/{name}" for name in artifact_names),
            date=payload["date"],
            pipeline_family="gepa_from_scratch",
            split=payload["final_eval_split"],
            row_count=s["rows"],
            model=payload["task_model"],
            model_role=(
                f"GEPA from-scratch student ({payload['task_model']}), reflection LM "
                f"{payload['reflection_model']}; length-penalized purist metric; "
                "trained on optimizer-only train split."
            ),
            mode="live",
            replay_status="live",
            decision="inform_architecture_loop",
            primary_metrics={
                "purist_correct": s["purist_correct"],
                "purist_accuracy": s["purist_accuracy"],
                "pragmatic_accuracy": s["pragmatic_accuracy"],
                "final_instruction_tokens": payload["final_instruction_tokens"],
                "seed_instruction_tokens": payload["seed_instruction_tokens"],
            },
            repair_mode="hybrid_full_stack",
            cache_reuse_source=f"experiments/{payload['run_id']}.jsonl",
            evidence_validity=(
                f"Development split ({payload['final_eval_split']}, gan2026_split_v1), "
                "NOT test450. GEPA trained on optimizer-only train split. Length penalty "
                "is part of the selection metric. Live task model; "
                f"reflection {payload['reflection_model']}."
            ),
            supersedes=(),
            claim_language_notes=(
                "DSPy-native GEPA from-scratch; instruction evolved under an explicit "
                "prompt-length penalty. Development-surface number only."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


def run_experiment(config: GepaExperimentConfig, *, register: bool = True) -> dict[str, Any]:
    """Compile, evaluate, persist, and (optionally) register one GEPA experiment."""

    GEPA_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    log_dir = GEPA_LOG_ROOT / config.run_id
    log_dir.mkdir(parents=True, exist_ok=True)

    _configure_task_lm(config)
    reflection_lm = _build_reflection_lm(config)

    trainset = gepa_data.load_trainset(limit=config.trainset_size)
    valset = gepa_data.load_valset(limit=config.valset_size)
    metric = build_metric(config.length_penalty)

    seed_program = build_from_scratch_program()
    seed_instruction_tokens = approx_tokens(_final_instruction(seed_program))

    gepa_kwargs: dict[str, Any] = {
        "metric": metric,
        "reflection_lm": reflection_lm,
        "reflection_minibatch_size": config.reflection_minibatch_size,
        "num_threads": config.num_threads,
        "track_stats": True,
        "track_best_outputs": True,
        "log_dir": str(log_dir),
        "seed": config.seed,
        "add_format_failure_as_feedback": True,
        # Dynamically-built DSPy signatures are not standard-pickleable; cloudpickle
        # serializes them so GEPA can checkpoint candidate state to log_dir (resume).
        "gepa_kwargs": {"use_cloudpickle": True},
    }
    if config.max_metric_calls is not None:
        gepa_kwargs["max_metric_calls"] = config.max_metric_calls
    else:
        gepa_kwargs["auto"] = config.auto

    optimizer = dspy.GEPA(**gepa_kwargs)

    started = time.time()
    optimized = optimizer.compile(seed_program, trainset=trainset, valset=valset)
    elapsed = time.time() - started

    final_instruction = _final_instruction(optimized)
    final_instruction_tokens = approx_tokens(final_instruction)

    eval_records = [r for r in gan_data.load_records_for_split(config.final_eval_split) if r.row_ok]
    if config.final_eval_limit is not None:
        eval_records = eval_records[: config.final_eval_limit]
    eval_rows, eval_summary = _evaluate_program(
        optimized, eval_records, num_threads=config.num_threads
    )

    payload: dict[str, Any] = {
        "run_id": config.run_id,
        "date": config.date,
        "task_model": config.task_model,
        "reflection_model": config.reflection_model,
        "task_temperature": config.task_temperature,
        "task_max_tokens": config.task_max_tokens,
        "auto": config.auto,
        "max_metric_calls": config.max_metric_calls,
        "trainset_size": len(trainset),
        "valset_size": len(valset),
        "final_eval_split": config.final_eval_split,
        "seed_instruction_tokens": seed_instruction_tokens,
        "final_instruction_tokens": final_instruction_tokens,
        "elapsed_seconds": round(elapsed, 1),
        "length_penalty": {
            "enabled": config.length_penalty.enabled,
            "instruction_token_budget": config.length_penalty.instruction_token_budget,
            "demo_token_budget": config.length_penalty.demo_token_budget,
            "output_token_budget": config.length_penalty.output_token_budget,
            "beta_instruction": config.length_penalty.beta_instruction,
            "beta_demo": config.length_penalty.beta_demo,
            "alpha_output": config.length_penalty.alpha_output,
        },
        "final_eval": eval_summary,
        "notes": config.notes,
    }

    jsonl_name = f"{config.run_id}.jsonl"
    json_name = f"{config.run_id}.json"
    md_name = f"{config.run_id}.md"
    instruction_name = f"{config.run_id}.instruction.txt"
    write_jsonl_rows(eval_rows, EXPERIMENTS / jsonl_name)
    (EXPERIMENTS / instruction_name).write_text(final_instruction + "\n", encoding="utf-8")
    (EXPERIMENTS / json_name).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (EXPERIMENTS / md_name).write_text(_markdown(payload, final_instruction), encoding="utf-8")
    if register:
        _register(payload, [json_name, md_name, jsonl_name, instruction_name])

    return payload
