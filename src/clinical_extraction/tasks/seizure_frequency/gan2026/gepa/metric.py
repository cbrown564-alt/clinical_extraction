"""Length-penalized feedback metric for GEPA optimization of Gan 2026.

This is the mechanism the operator asked for: a scoring function that rewards
purist correctness *and* actively penalizes prompt bloat, so GEPA cannot win by
growing an ever-longer instruction (the failure mode of the hand-tuned prompts).

The metric returns ``dspy.Prediction(score=..., feedback=...)``:

* ``score``    graded quality minus a length penalty, clamped to ``[0, 1]``.
* ``feedback`` natural-language reflection signal. It states the clinical failure
  mode (encoding the failure taxonomy accumulated over the research) *and* the
  current instruction/demo token counts versus budget, so GEPA's reflective
  mutation is told, in words, to keep the prompt short.

The length penalty enters the aggregate validation score, so the Pareto/candidate
selection deselects bloated programs even when they are occasionally correct.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import dspy

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.gepa.program import approx_tokens
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    boundary_band,
    map_pragmatic,
    map_purist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredRepairConfig,
    parse_structured_json,
)


@dataclass(frozen=True)
class LengthPenaltyConfig:
    """Token budgets and weights for the prompt-bloat penalty.

    Budgets are soft: the penalty is proportional to overflow *beyond* the budget,
    so a lean prompt pays nothing. ``enabled=False`` recovers a pure-quality metric
    (kept for a potential length-penalty ablation arm).
    """

    enabled: bool = True
    instruction_token_budget: int = 600
    demo_token_budget: int = 800
    output_token_budget: int = 1200
    beta_instruction: float = 0.25
    beta_demo: float = 0.25
    alpha_output: float = 0.10
    max_penalty: float = 0.6


# Graded quality tiers. Purist is the headline metric; the lower tiers give GEPA a
# denser gradient than a bare 0/1 without rewarding verbosity.
QUALITY_PURIST = 1.0
QUALITY_PRAGMATIC = 0.4
QUALITY_SCORABLE = 0.1
QUALITY_UNSCORABLE = 0.0


def _demo_tokens(demos: Any) -> int:
    total = 0
    for demo in demos or []:
        try:
            total += approx_tokens(str(dict(demo)))
        except Exception:  # pragma: no cover - demos are plain mappings in practice
            total += approx_tokens(str(demo))
    return total


def _predictor_lengths(pred_trace: Any) -> tuple[int, int]:
    """Instruction and demo token counts of the predictor under optimization.

    ``pred_trace`` entries are ``(predictor, inputs, outputs)``; the predictor's
    ``signature.instructions`` is the *evolved* instruction GEPA is scoring. When
    GEPA does not pass a predictor trace (e.g. plain eval), returns ``(0, 0)`` so
    no instruction penalty is applied.
    """

    if not pred_trace:
        return 0, 0
    try:
        predictor = pred_trace[-1][0]
    except (IndexError, TypeError):
        return 0, 0
    signature = getattr(predictor, "signature", None)
    instruction = getattr(signature, "instructions", "") if signature is not None else ""
    return approx_tokens(instruction), _demo_tokens(getattr(predictor, "demos", None))


def _structured_json_of(pred: Any) -> str:
    value = getattr(pred, "structured_json", None)
    if value is None and isinstance(pred, dict):
        value = pred.get("structured_json")
    return str(value) if value is not None else ""


def _prompt_lengths(pred: Any, pred_trace: Any) -> tuple[int, int]:
    """Instruction and demo token counts for the candidate under evaluation.

    Prefers the values the program stamped onto the prediction (available in every
    GEPA call path, including plain valset scoring), and falls back to reading the
    predictor out of ``pred_trace`` for callers that do not stamp.
    """

    instr = getattr(pred, "instruction_tokens", None)
    demo = getattr(pred, "demo_tokens", None)
    if instr is not None:
        return int(instr), int(demo or 0)
    return _predictor_lengths(pred_trace)


def _score_prediction(
    raw_output: str,
    note_text: str,
    gold_monthly_frequency: float,
) -> dict[str, Any]:
    """Run the deterministic stack on the model output and grade it."""

    extraction, _normalized, errors = (
        parse_structured_json(
            raw_output,
            note_text=note_text,
            repair_config=StructuredRepairConfig(),
        )
        if raw_output
        else (None, [], ["empty_output"])
    )
    gold_purist = str(map_purist(gold_monthly_frequency))
    gold_pragmatic = str(map_pragmatic(gold_monthly_frequency))
    if extraction is None or not extraction.selection.final_label:
        return {
            "scorable": False,
            "errors": errors,
            "predicted_label": None,
            "predicted_purist": None,
            "gold_purist": gold_purist,
            "purist_correct": False,
            "pragmatic_correct": False,
            "rationale": None,
        }
    predicted_label = extraction.selection.final_label
    try:
        predicted_record = label_to_frequency_record(predicted_label)
    except ValueError as exc:
        return {
            "scorable": False,
            "errors": [*errors, f"unscorable_final_label: {exc}"],
            "predicted_label": predicted_label,
            "predicted_purist": None,
            "gold_purist": gold_purist,
            "purist_correct": False,
            "pragmatic_correct": False,
            "rationale": extraction.selection.rationale,
        }
    predicted_purist = str(map_purist(predicted_record.monthly_frequency))
    predicted_pragmatic = str(map_pragmatic(predicted_record.monthly_frequency))
    return {
        "scorable": True,
        "errors": errors,
        "predicted_label": predicted_label,
        "predicted_purist": predicted_purist,
        "gold_purist": gold_purist,
        "purist_correct": predicted_purist == gold_purist,
        "pragmatic_correct": predicted_pragmatic == gold_pragmatic,
        "rationale": extraction.selection.rationale,
    }


def _quality(graded: dict[str, Any]) -> float:
    if not graded["scorable"]:
        return QUALITY_UNSCORABLE
    if graded["purist_correct"]:
        return QUALITY_PURIST
    if graded["pragmatic_correct"]:
        return QUALITY_PRAGMATIC
    return QUALITY_SCORABLE


def _length_penalty(
    instr_tokens: int,
    demo_tokens: int,
    out_tokens: int,
    config: LengthPenaltyConfig,
) -> float:
    if not config.enabled:
        return 0.0

    def overflow(tokens: int, budget: int) -> float:
        return max(0, tokens - budget) / budget if budget > 0 else 0.0

    penalty = (
        config.beta_instruction * overflow(instr_tokens, config.instruction_token_budget)
        + config.beta_demo * overflow(demo_tokens, config.demo_token_budget)
        + config.alpha_output * overflow(out_tokens, config.output_token_budget)
    )
    return min(penalty, config.max_penalty)


def _clinical_hint(note_text: str, gold_label: str, predicted_label: str | None) -> str:
    text = " ".join([note_text, gold_label or "", predicted_label or ""]).lower()
    hints: list[str] = []
    pred = (predicted_label or "").lower()
    gold = (gold_label or "").lower()
    non_countable = {"unknown", "no seizure frequency reference"}
    demoted = pred in non_countable
    gold_countable = gold not in non_countable and not gold.startswith("seizure free")
    if demoted and gold_countable:
        hints.append(
            "Do not demote countable evidence (explicit counts, ranges, "
            "days-with-seizures, cluster cadence, or dated sequences in a recent "
            "window) to unknown/no_reference."
        )
    if "cluster" in text:
        hints.append(
            "For clusters, keep cluster cadence separate from events-per-cluster; "
            "select cluster_frequency when both are supported."
        )
    sf_gold = gold.startswith("seizure free") or "no seizures" in text or "seizure-free" in text
    if sf_gold and pred and not pred.startswith("seizure free"):
        hints.append(
            "A clear sustained current absence interval is seizure_free; but do not "
            "pick seizure_free when an active countable seizure-like event remains "
            "in the same or a later window."
        )
    if (not sf_gold) and pred.startswith("seizure free"):
        hints.append(
            "Do not let a generic 'no seizures since review' erase an active aura, "
            "jerk, absence, or counted event; select the active frequency instead."
        )
    return " ".join(hints)


def _feedback(
    graded: dict[str, Any],
    gold: Any,
    instr_tokens: int,
    demo_tokens: int,
    out_tokens: int,
    config: LengthPenaltyConfig,
) -> str:
    gold_label = str(getattr(gold, "gold_label", "") or "")
    gold_month = float(getattr(gold, "gold_monthly_frequency", 0.0) or 0.0)
    band = boundary_band(gold_month)
    parts: list[str]
    if not graded["scorable"]:
        first_error = (graded["errors"] or ["unknown error"])[0]
        parts = [
            f"OUTPUT NOT SCORABLE ({first_error}). Return exactly one JSON object "
            "matching output_schema with an 'events' list and a 'selection' object; "
            "no markdown; every evidence value an exact note substring; provide a "
            "non-null selection.final_label for the chosen burden."
        ]
    elif graded["purist_correct"]:
        parts = [f"CORRECT. Purist category {graded['predicted_purist']} (gold band {band})."]
    else:
        parts = [
            f"WRONG. Predicted '{graded['predicted_label']}' -> {graded['predicted_purist']}; "
            f"gold '{gold_label}' -> {graded['gold_purist']} (gold band {band})."
        ]
        hint = _clinical_hint(
            str(getattr(gold, "note_text", "") or ""),
            gold_label,
            graded["predicted_label"],
        )
        if hint:
            parts.append(hint)
        if band == "band_weekly":
            parts.append(
                "Weekly-band rates (e.g. 'most weekdays', 'several per week') are the "
                "hardest boundary; map multi-per-week language carefully."
            )
    if config.enabled:
        budget_note = (
            f"Instruction is {instr_tokens} tokens (budget {config.instruction_token_budget})"
        )
        if demo_tokens:
            budget_note += f", demos {demo_tokens} tokens (budget {config.demo_token_budget})"
        budget_note += (
            ". Keep the instruction concise: prefer a few general clinical principles "
            "over many overlapping special-case rules; merge or drop redundant rules."
        )
        if instr_tokens > config.instruction_token_budget:
            budget_note = "TOO LONG. " + budget_note
        parts.append(budget_note)
    if graded["scorable"] and out_tokens > config.output_token_budget:
        parts.append(
            f"Output is verbose ({out_tokens} tokens); keep selection.rationale to one "
            "concise clinical sentence and avoid step-by-step reasoning in the JSON."
        )
    return " ".join(parts)


def build_metric(config: LengthPenaltyConfig | None = None):
    """Return a GEPA feedback metric closed over a length-penalty config.

    The returned callable also works as a plain DSPy metric (trailing GEPA-only
    arguments default to ``None``), so the same scoring is reused for final
    evaluation of the optimized program.
    """

    cfg = config or LengthPenaltyConfig()

    def metric(
        gold: Any,
        pred: Any,
        trace: Any = None,
        pred_name: str | None = None,
        pred_trace: Any = None,
    ) -> dspy.Prediction:
        note_text = str(getattr(gold, "note_text", "") or "")
        gold_month = float(getattr(gold, "gold_monthly_frequency", 0.0) or 0.0)
        raw_output = _structured_json_of(pred)
        graded = _score_prediction(raw_output, note_text, gold_month)

        instr_tokens, demo_tokens = _prompt_lengths(pred, pred_trace)
        out_tokens = approx_tokens(raw_output)

        quality = _quality(graded)
        penalty = _length_penalty(instr_tokens, demo_tokens, out_tokens, cfg)
        score = max(0.0, quality - penalty)
        feedback = _feedback(graded, gold, instr_tokens, demo_tokens, out_tokens, cfg)
        return dspy.Prediction(score=score, feedback=feedback)

    return metric
