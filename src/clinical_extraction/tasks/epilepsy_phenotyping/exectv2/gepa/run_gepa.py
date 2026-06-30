"""Single-experiment GEPA driver for ExECTv2 de-dup clinical facts (resumable).

Compiles a from-scratch GEPA program against a seeded sub-split of the frozen
``dev`` surface, then evaluates the optimized program on the full ``dev`` split
(never ``test``), writing the evolved instruction, per-letter eval, a JSON/Markdown
summary, and a registry entry. The optimizer log dir lets a crashed run resume;
the orchestrator skips experiments whose summary JSON already exists.

Primary reported surface is the canonical ``clinical_headline`` overall
(Diagnosis=concept_negation), with the strict benchmark and CUI-dropped semantic
F1 reported beside it per plan 13's claim-language discipline.
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.metric import (
    KEY_FAMILIES,
    LengthPenaltyConfig,
    _counts,
    _f1_from,
    build_metric,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program import (
    OUTPUT_SCHEMA_JSON,
    GepaDedupFactsExtractor,
    approx_tokens,
    build_from_scratch_program,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.parsing import (
    parse_dedup_clinical_facts_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.projection import (
    to_predicted_letter_from_dedup_facts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    benchmark_config_for,
    score_concept_identity,
    score_frequency_state,
    score_investigations_components,
    score_overall,
    score_prescription_components,
    semantic_config_for,
    source_near_diagnostic,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    write_run_registry_markdown,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

ROOT = Path(__file__).resolve().parents[6]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"
GEPA_LOG_ROOT = EXPERIMENTS / "gepa_overnight_exectv2"

KEY_ENTITY_NAMES: tuple[str, ...] = ("Prescription", "Diagnosis", "SeizureFrequency", "Investigations")
#: The hand-tuned single-prompt de-dup plateau (plan 13) and the v08 hybrid control,
#: recorded so every report frames the GEPA number against what it must beat.
DEV140_HAND_TUNED_HEADLINE = {"gpt-4.1-mini": 0.710, "deepseek-chat": 0.745, "qwen3.6-35b": 0.694}
DEV140_V08_HYBRID_HEADLINE = 0.9155


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
    trainset_size: int = gepa_data.DEFAULT_TRAINSET_SIZE
    valset_size: int | None = None
    final_eval_limit: int | None = None
    num_threads: int = 12
    reflection_minibatch_size: int = 3
    length_penalty: LengthPenaltyConfig = field(default_factory=LengthPenaltyConfig)
    #: F-beta weight for the optimization objective. 1.0 = F1; >1 favours recall.
    recall_beta: float = 1.0
    #: Per-family F-beta weights (family -> beta) as pairs; macro per-family objective.
    #: Overrides recall_beta when non-empty. e.g. (("Diagnosis", 2.0),).
    family_recall_beta: tuple[tuple[str, float], ...] = ()
    #: Optional override of GEPA's reflective-mutation component selector (default:
    #: dspy's "round_robin", which cycles through every named predictor). Pass a
    #: callable matching gepa's ReflectionComponentSelector protocol to restrict
    #: which predictor(s) GEPA is allowed to mutate, e.g. a single-family lane run.
    component_selector: Any | None = None
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


def _canonical_headline(
    gold_letters: list[ExectLetter], pred_letters: list[ExectLetter]
) -> dict[str, Any]:
    """The dedup runner's canonical clinical_headline overall, micro-averaged."""

    scores = {
        "Prescription": score_prescription_components(gold_letters, pred_letters).clinical_headline,
        "Diagnosis": score_concept_identity(gold_letters, pred_letters, "Diagnosis").concept_negation,
        "SeizureFrequency": score_frequency_state(gold_letters, pred_letters).clinical_headline,
        "Investigations": score_investigations_components(gold_letters, pred_letters).clinical_headline,
    }
    precision_tp = recall_tp = pred_count = gold_count = 0
    per_family: dict[str, float] = {}
    for family in KEY_FAMILIES:
        ptp, rtp, pc, gc = _counts(scores[family])
        precision_tp += ptp
        recall_tp += rtp
        pred_count += pc
        gold_count += gc
        per_family[family] = round(float(getattr(scores[family], "f1", 0.0)), 4)
    return {
        "overall_f1": round(_f1_from(precision_tp, recall_tp, pred_count, gold_count), 4),
        "precision": round(precision_tp / pred_count, 4) if pred_count else 0.0,
        "recall": round(recall_tp / gold_count, 4) if gold_count else 0.0,
        "per_family": per_family,
        "diagnosis_component": "concept_negation",
    }


def _evidence_recall(
    gold_letters: list[ExectLetter], pred_letters: list[ExectLetter]
) -> dict[str, Any]:
    """Producer evidence-presence recall (source_near same-entity text-overlap).

    The fraction of gold facts for which the program retrieved ANY overlapping-text
    prediction, representation aside — the north-star for "did the producers retrieve
    more?", independent of keying. GEPA per-family baseline 0.694; v08 hybrid 0.883.
    """

    diag = source_near_diagnostic(gold_letters, pred_letters, KEY_ENTITY_NAMES, benchmark_config_for)
    return {
        "overall_recall": round(diag.overall.overlap.recall, 4),
        "per_family": {
            entity: round(diag.per_entity[entity].overlap.recall, 4) for entity in KEY_ENTITY_NAMES
        },
        "comparators": {"gepa_per_family_baseline": 0.694, "v08_hybrid": 0.883},
    }


def _evaluate_program(
    program: GepaDedupFactsExtractor,
    letters: list[ExectLetter],
    *,
    num_threads: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the optimized program over letters and score the clinical_headline surface."""

    evaluator = dspy.Parallel(num_threads=num_threads, provide_traceback=True)
    exec_pairs = [
        (program, {"letter_text": letter.note_text, "output_schema": OUTPUT_SCHEMA_JSON})
        for letter in letters
    ]
    predictions = evaluator(exec_pairs)

    gold_letters: list[ExectLetter] = []
    pred_letters: list[ExectLetter] = []
    rows: list[dict[str, Any]] = []
    n_facts_total = n_scored_total = n_unscorable = 0
    for letter, prediction in zip(letters, predictions, strict=True):
        raw_output = str(getattr(prediction, "clinical_facts_json", "") or "") if prediction else ""
        record, errors = (
            parse_dedup_clinical_facts_json(raw_output) if raw_output else (None, ["empty_output"])
        )
        if record is None:
            predicted = PredictedLetter(letter_id=letter.letter_id, mentions=())
            n_facts = n_scored = 0
            n_unscorable += 1
        else:
            predicted, _gate, _prov, _notes = to_predicted_letter_from_dedup_facts(letter, record)
            n_facts = len(record.clinical_facts)
            n_scored = len(predicted.mentions)
        pred_exect = to_exect_letter(predicted)
        gold_letters.append(letter)
        pred_letters.append(pred_exect)
        n_facts_total += n_facts
        n_scored_total += n_scored
        rows.append(
            {
                "letter_id": letter.letter_id,
                "n_facts": n_facts,
                "n_scored": n_scored,
                "errors": errors,
                "raw_output_tokens": approx_tokens(raw_output),
                "predicted_mentions": [
                    {"entity": m.entity, "text": m.text, "attributes": dict(m.attributes)}
                    for m in predicted.mentions
                ],
            }
        )

    headline = _canonical_headline(gold_letters, pred_letters)
    strict = score_overall(gold_letters, pred_letters, KEY_ENTITY_NAMES, benchmark_config_for).per_item
    semantic = score_overall(gold_letters, pred_letters, KEY_ENTITY_NAMES, semantic_config_for).per_item
    evidence_recall = _evidence_recall(gold_letters, pred_letters)
    summary = {
        "letters": len(rows),
        "unscorable_letters": n_unscorable,
        "n_facts_total": n_facts_total,
        "n_scored_total": n_scored_total,
        "clinical_headline": headline,
        "evidence_recall": evidence_recall,
        "strict_benchmark_per_item_f1": round(strict.f1, 4),
        "semantic_per_item_f1": round(semantic.f1, 4),
        "comparators": {
            "dev140_hand_tuned_single_prompt_headline": DEV140_HAND_TUNED_HEADLINE,
            "dev140_v08_hybrid_headline": DEV140_V08_HYBRID_HEADLINE,
        },
    }
    return rows, summary


def _final_instruction(program: GepaDedupFactsExtractor) -> str:
    return str(program.extract.signature.instructions)


def _write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _markdown(payload: dict[str, Any], instruction: str) -> str:
    s = payload["final_eval"]
    h = s["clinical_headline"]
    lp = payload["length_penalty"]
    pf = h["per_family"]
    lines = [
        f"# GEPA from-scratch (ExECTv2 de-dup facts) — {payload['run_id']}",
        "",
        f"Date: {payload['date']}",
        "",
        (
            "DSPy-native GEPA run. The optimizable surface is the signature "
            "instruction; the existing de-dup parse/evidence-gate/adapter and the "
            "canonical clinical_headline scorers are reused unchanged. Trained on a "
            "seeded sub-split of `dev` (optimizer-only); evaluated on the full `dev` "
            "split (development surface, NOT test). Attribution-clean LLM-only: the "
            "adapter performs representation mapping only, it adds no facts."
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
        f"- instruction budget: {lp['instruction_token_budget']} tok (beta {lp['beta_instruction']})",
        f"- demo budget: {lp['demo_token_budget']} tok (beta {lp['beta_demo']})",
        f"- output budget: {lp['output_token_budget']} tok (alpha {lp['alpha_output']})",
        f"- **final instruction length: {payload['final_instruction_tokens']} tokens** "
        f"(seed was {payload['seed_instruction_tokens']} tokens)",
        "",
        "## Final evaluation (dev, clinical-recovery surface)",
        "",
        f"- **Canonical clinical_headline overall F1: {h['overall_f1']:.3f}** "
        f"(P={h['precision']:.3f} R={h['recall']:.3f}, Diagnosis={h['diagnosis_component']})",
        f"  - Diagnosis={pf['Diagnosis']:.3f}  SeizureFrequency={pf['SeizureFrequency']:.3f}  "
        f"Prescription={pf['Prescription']:.3f}  Investigations={pf['Investigations']:.3f}",
        (
            f"- **Producer evidence-recall (source_near): {s['evidence_recall']['overall_recall']:.3f}** "
            f"(GEPA per-family baseline 0.694, v08 hybrid 0.883) — Dx="
            f"{s['evidence_recall']['per_family']['Diagnosis']:.3f} "
            f"SF={s['evidence_recall']['per_family']['SeizureFrequency']:.3f} "
            f"Rx={s['evidence_recall']['per_family']['Prescription']:.3f} "
            f"Inv={s['evidence_recall']['per_family']['Investigations']:.3f}"
        ),
        f"- Strict benchmark per-item F1 (diagnostic, NOT paper-cleared): "
        f"{s['strict_benchmark_per_item_f1']:.3f}",
        f"- Semantic (CUI-dropped) per-item F1: {s['semantic_per_item_f1']:.3f}",
        f"- Letters: {s['letters']} (unscorable: {s['unscorable_letters']}); "
        f"facts emitted {s['n_facts_total']}, scored {s['n_scored_total']}",
        "",
        "## Comparators (dev140, from plan 13)",
        "",
        "- Hand-tuned single-prompt de-dup plateau: GPT-4.1-mini 0.710, DeepSeek 0.745, Qwen 0.694",
        f"- v08 hybrid (multi-component) control: {DEV140_V08_HYBRID_HEADLINE}",
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
            "`dev` is sub-split deterministically (seed "
            f"{gepa_data.DEV_SUBSPLIT_SEED}) into an optimizer-only trainset and a "
            "selection valset; `test` is never touched. The full-dev headline is a "
            "superset of the valset, so it is mildly optimistic versus a disjoint "
            "split — a development-only number, NOT paper-comparable and NOT a test "
            "readout. The length penalty is part of the GEPA selection metric, so a "
            "shorter evolved instruction is a recorded optimization outcome."
        ),
    ]
    return "\n".join(lines)


def _register(payload: dict[str, Any], artifact_names: list[str]) -> None:
    try:
        existing = load_run_registry(REGISTRY_PATH)
    except ValueError as exc:
        print(
            f"[gepa] WARNING: registry load failed, skipping registration of "
            f"{payload['run_id']}: {exc}",
            flush=True,
        )
        return
    entries = [e for e in existing if e.run_id != payload["run_id"]]
    s = payload["final_eval"]
    h = s["clinical_headline"]
    entries.append(
        RunRegistryEntry(
            run_id=payload["run_id"],
            artifact_paths=tuple(f"experiments/{name}" for name in artifact_names),
            date=payload["date"],
            pipeline_family="gepa_from_scratch",
            split="dev",
            row_count=s["letters"],
            model=payload["task_model"],
            model_role=(
                f"GEPA from-scratch student ({payload['task_model']}), reflection LM "
                f"{payload['reflection_model']}; length-penalized clinical_headline metric; "
                "trained on optimizer-only dev sub-split, attribution-clean de-dup adapter."
            ),
            mode="live",
            replay_status="live",
            decision="inform_architecture_loop",
            primary_metrics={
                "clinical_headline_overall_f1": h["overall_f1"],
                "clinical_headline_diagnosis_f1": h["per_family"]["Diagnosis"],
                "clinical_headline_seizure_frequency_f1": h["per_family"]["SeizureFrequency"],
                "clinical_headline_prescription_f1": h["per_family"]["Prescription"],
                "clinical_headline_investigations_f1": h["per_family"]["Investigations"],
                "strict_benchmark_per_item_f1": s["strict_benchmark_per_item_f1"],
                "semantic_per_item_f1": s["semantic_per_item_f1"],
                "final_instruction_tokens": payload["final_instruction_tokens"],
                "seed_instruction_tokens": payload["seed_instruction_tokens"],
            },
            repair_mode="dedup_clinical_facts_adapter",
            cache_reuse_source=f"experiments/{payload['run_id']}.jsonl",
            evidence_validity=(
                "Development split (dev, exectv2_split_v1), NOT test. GEPA trained on an "
                "optimizer-only dev sub-split. clinical_headline is the clinical-recovery "
                "surface (decision 0027), NOT paper-comparable; strict benchmark reported "
                "beside it. Live task model; reflection deepseek-reasoner."
            ),
            supersedes=(),
            claim_language_notes=(
                "DSPy-native GEPA from-scratch on the de-dup clinical_headline surface; "
                "instruction evolved under a prompt-length penalty. Clinical-recovery "
                "number only, development-surface only; not benchmark-cleared."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


def run_experiment(
    config: GepaExperimentConfig,
    *,
    register: bool = True,
    seed_program: dspy.Module | None = None,
    final_instruction_fn=None,
) -> dict[str, Any]:
    """Compile, evaluate, persist, and (optionally) register one GEPA experiment.

    By default optimizes the single-instruction monolith. Pass ``seed_program`` (and
    ``final_instruction_fn``, which extracts the optimizable instruction text from a
    program) to optimize a different program shape, e.g. the per-family
    multi-signature program — everything else (eval, artifacts, registry) is shared.
    """

    GEPA_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    log_dir = GEPA_LOG_ROOT / config.run_id
    log_dir.mkdir(parents=True, exist_ok=True)

    _configure_task_lm(config)
    reflection_lm = _build_reflection_lm(config)

    trainset = gepa_data.load_trainset(trainset_size=config.trainset_size)
    valset = gepa_data.load_valset(trainset_size=config.trainset_size, limit=config.valset_size)
    metric = build_metric(
        config.length_penalty,
        recall_beta=config.recall_beta,
        family_beta=dict(config.family_recall_beta) or None,
    )

    program = seed_program if seed_program is not None else build_from_scratch_program()
    instruction_of = final_instruction_fn or _final_instruction
    seed_instruction_tokens = approx_tokens(instruction_of(program))

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
        "gepa_kwargs": {"use_cloudpickle": True},
    }
    if config.component_selector is not None:
        gepa_kwargs["component_selector"] = config.component_selector
    if config.max_metric_calls is not None:
        gepa_kwargs["max_metric_calls"] = config.max_metric_calls
    else:
        gepa_kwargs["auto"] = config.auto

    optimizer = dspy.GEPA(**gepa_kwargs)

    started = time.time()
    optimized = optimizer.compile(program, trainset=trainset, valset=valset)
    elapsed = time.time() - started

    final_instruction = instruction_of(optimized)
    final_instruction_tokens = approx_tokens(final_instruction)

    eval_letters = gepa_data.load_dev_letters()
    if config.final_eval_limit is not None:
        eval_letters = eval_letters[: config.final_eval_limit]
    eval_rows, eval_summary = _evaluate_program(
        optimized, eval_letters, num_threads=config.num_threads
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
        "recall_beta": config.recall_beta,
        "family_recall_beta": dict(config.family_recall_beta),
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
    _write_jsonl(eval_rows, EXPERIMENTS / jsonl_name)
    (EXPERIMENTS / instruction_name).write_text(final_instruction + "\n", encoding="utf-8")
    (EXPERIMENTS / json_name).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (EXPERIMENTS / md_name).write_text(_markdown(payload, final_instruction), encoding="utf-8")
    if register:
        _register(payload, [json_name, md_name, jsonl_name, instruction_name])

    return payload
