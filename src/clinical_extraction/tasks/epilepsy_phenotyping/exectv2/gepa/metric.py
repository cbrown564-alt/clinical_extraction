"""Length-penalized feedback metric for GEPA optimization of ExECTv2 de-dup facts.

This is the mechanism that made the Gan run work, ported to ExECTv2: a scoring
function that rewards clinical-recovery (``clinical_headline``) correctness *and*
actively penalizes prompt bloat, so GEPA cannot win by growing an ever-longer
instruction (the failure mode of the hand-tuned de-dup prompts in plan 13).

The metric returns ``dspy.Prediction(score=..., feedback=...)``:

* ``score``    per-letter clinical_headline F1 minus a length penalty, clamped to ``[0, 1]``.
* ``feedback`` natural-language reflection signal: per-family P/R/F1, targeted hints
  for the two gap families (Diagnosis enumeration, SeizureFrequency state), de-dup /
  over-emission and evidence-exactness guidance, plus the live instruction token
  count versus budget so reflection is told, in words, to keep the prompt short.

Quality reuses the existing de-dup route end-to-end (parser -> evidence-gated,
attribution-clean adapter -> the four canonical clinical_headline scorers), so the
GEPA number is computed exactly as the dedup runner's canonical headline overall,
just per-letter for a dense per-example gradient.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program import approx_tokens
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.parsing import (
    parse_dedup_clinical_facts_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.projection import (
    to_predicted_letter_from_dedup_facts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    concept_keys,
    frequency_state_keys,
    investigation_component_keys,
    prescription_component_keys,
    score_concept_identity,
    score_frequency_state,
    score_investigations_components,
    score_prescription_components,
)

#: Canonical clinical_headline families and their per-letter F1 (Diagnosis uses
#: concept_negation, matching the dedup runner's canonical headline overall).
KEY_FAMILIES: tuple[str, ...] = (
    "Diagnosis",
    "SeizureFrequency",
    "Prescription",
    "Investigations",
)


@dataclass(frozen=True)
class LengthPenaltyConfig:
    """Token budgets and weights for the prompt-bloat penalty.

    Budgets are soft: the penalty is proportional to overflow *beyond* the budget,
    so a lean prompt pays nothing. ``enabled=False`` recovers a pure-quality metric
    (the length-penalty ablation arm). The output budget is generous with a small
    weight because ExECTv2 output length is data-driven (number of facts), not a
    prompt-engineering bloat surface like Gan's free-text rationale.
    """

    enabled: bool = True
    instruction_token_budget: int = 600
    demo_token_budget: int = 800
    output_token_budget: int = 2000
    beta_instruction: float = 0.25
    beta_demo: float = 0.25
    alpha_output: float = 0.05
    max_penalty: float = 0.6


def _counts(score: Any) -> tuple[int, int, int, int]:
    """(precision_tp, recall_tp, pred_count, gold_count) for any headline score."""

    tp = int(getattr(score, "tp", 0))
    fp = int(getattr(score, "fp", 0))
    fn = int(getattr(score, "fn", 0))
    precision_tp = int(getattr(score, "precision_tp", tp))
    recall_tp = int(getattr(score, "recall_tp", tp))
    pred_count = int(getattr(score, "pred_count", tp + fp))
    gold_count = int(getattr(score, "gold_count", tp + fn))
    return precision_tp, recall_tp, pred_count, gold_count


def _f1_from(precision_tp: int, recall_tp: int, pred_count: int, gold_count: int) -> float:
    if pred_count == 0 and gold_count == 0:
        return 1.0  # correctly emitted nothing for the key families
    precision = precision_tp / pred_count if pred_count else 0.0
    recall = recall_tp / gold_count if gold_count else 0.0
    if precision + recall == 0.0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _family_scores(gold_letter: ExectLetter, pred_letter: ExectLetter) -> dict[str, Any]:
    g = [gold_letter]
    p = [pred_letter]
    return {
        "Prescription": score_prescription_components(g, p).clinical_headline,
        "Diagnosis": score_concept_identity(g, p, "Diagnosis").concept_negation,
        "SeizureFrequency": score_frequency_state(g, p).clinical_headline,
        "Investigations": score_investigations_components(g, p).clinical_headline,
    }


def _family_unit_keys(family: str, annotations: list, note_text: str) -> list:
    """The canonical clinical_headline unit keys the scorer uses for one family."""

    if family == "Diagnosis":
        return concept_keys(annotations, "Diagnosis", "negation")
    if family == "SeizureFrequency":
        return frequency_state_keys(annotations, "clinical_headline")
    if family == "Prescription":
        return prescription_component_keys(annotations, "clinical_headline", note_text)
    if family == "Investigations":
        return investigation_component_keys(annotations, "clinical_headline")
    return []


def _label(family: str, ann: Any) -> str:
    """Compact human-readable rendering of a mention for reflection feedback."""

    text = str(getattr(ann, "text", "") or "")
    attrs = dict(getattr(ann, "attributes", {}) or {})
    if family == "Diagnosis":
        negated = str(attrs.get("Negation", "")).lower().startswith("negat")
        return f"{text} (negated)" if negated else text
    if family == "SeizureFrequency":
        bits = [
            f"{k}={attrs[k]}"
            for k in ("NumberOfSeizures", "LowerNumberOfSeizures", "UpperNumberOfSeizures",
                      "FrequencyChange")
            if attrs.get(k)
        ]
        return f"{text} [{', '.join(bits)}]" if bits else text
    if family == "Prescription":
        bits = [str(attrs.get("DrugName") or text)]
        if attrs.get("DrugDose"):
            bits.append(f"{attrs['DrugDose']}{attrs.get('DoseUnit', '')}")
        if attrs.get("Frequency"):
            bits.append(f"x{attrs['Frequency']}")
        return " ".join(bits)
    if family == "Investigations":
        result = next((str(v) for k, v in attrs.items() if k.endswith("_Results") and v), "")
        return f"{text} ({result})" if result else text
    return text


def _labels_for_keys(family: str, annotations: list, target_keys: set, note_text: str) -> list[str]:
    labels: list[str] = []
    seen: set = set()
    for ann in annotations:
        for key in _family_unit_keys(family, [ann], note_text):
            if key in target_keys and key not in seen:
                seen.add(key)
                labels.append(_label(family, ann))
    return labels


def _family_diffs(gold_letter: ExectLetter, pred_letter: ExectLetter) -> dict[str, dict[str, list[str]]]:
    """Per-family missed-gold and spurious-predicted headline units, as readable labels.

    This is the actionable signal GEPA's reflective mutation needs: it shows the
    reflection LM exactly which gold facts were not recovered (with their canonical
    text/granularity) and which predicted facts were not in gold — so the evolved
    instruction can learn the target convention, not just receive a scalar score.
    """

    note = gold_letter.note_text
    diffs: dict[str, dict[str, list[str]]] = {}
    for family in KEY_FAMILIES:
        gold_anns = list(gold_letter.entities(family))
        pred_anns = list(pred_letter.entities(family))
        gold_keys = set(_family_unit_keys(family, gold_anns, note))
        pred_keys = set(_family_unit_keys(family, pred_anns, note))
        diffs[family] = {
            "missed": _labels_for_keys(family, gold_anns, gold_keys - pred_keys, note),
            "spurious": _labels_for_keys(family, pred_anns, pred_keys - gold_keys, note),
        }
    return diffs


def _score_prediction(raw_output: str, gold_letter: ExectLetter) -> dict[str, Any]:
    """Run the de-dup parse/adapter/scorer stack on the model output and grade it."""

    record, errors = (
        parse_dedup_clinical_facts_json(raw_output) if raw_output else (None, ["empty_output"])
    )
    if record is None:
        return {
            "scorable": False,
            "errors": errors,
            "headline_f1": 0.0,
            "family_f1": {family: 0.0 for family in KEY_FAMILIES},
            "aggregate": (0, 0, 0, 0),
            "n_facts": 0,
            "n_scored": 0,
            "diffs": {},
        }

    predicted, _gate_warnings, _provenance, _adapter_notes = to_predicted_letter_from_dedup_facts(
        gold_letter, record
    )
    pred_exect = to_exect_letter(predicted)
    scores = _family_scores(gold_letter, pred_exect)

    precision_tp = recall_tp = pred_count = gold_count = 0
    family_f1: dict[str, float] = {}
    for family in KEY_FAMILIES:
        ptp, rtp, pc, gc = _counts(scores[family])
        precision_tp += ptp
        recall_tp += rtp
        pred_count += pc
        gold_count += gc
        family_f1[family] = round(float(getattr(scores[family], "f1", 0.0)), 4)

    return {
        "scorable": True,
        "errors": errors,
        "headline_f1": _f1_from(precision_tp, recall_tp, pred_count, gold_count),
        "family_f1": family_f1,
        "aggregate": (precision_tp, recall_tp, pred_count, gold_count),
        "n_facts": len(record.clinical_facts),
        "n_scored": len(predicted.mentions),
        "diffs": _family_diffs(gold_letter, pred_exect),
    }


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


_MAX_DIFF_ITEMS = 4


def _diff_lines(graded: dict[str, Any]) -> str:
    """Concrete per-family gold-vs-pred diff — the actionable signal for reflection.

    Shows the reflection LM the exact gold facts it missed (with their canonical
    text/granularity) and the spurious facts it emitted, so the evolved instruction
    can learn the target convention rather than chase a scalar score.
    """

    diffs = graded.get("diffs") or {}
    lines: list[str] = []
    for family in KEY_FAMILIES:
        entry = diffs.get(family) or {}
        missed = entry.get("missed") or []
        spurious = entry.get("spurious") or []
        if not missed and not spurious:
            continue
        parts = [f"{family}:"]
        if missed:
            shown = "; ".join(missed[:_MAX_DIFF_ITEMS])
            extra = f" (+{len(missed) - _MAX_DIFF_ITEMS} more)" if len(missed) > _MAX_DIFF_ITEMS else ""
            parts.append(f"MISSED gold you should emit [{shown}{extra}]")
        if spurious:
            shown = "; ".join(spurious[:_MAX_DIFF_ITEMS])
            extra = (
                f" (+{len(spurious) - _MAX_DIFF_ITEMS} more)"
                if len(spurious) > _MAX_DIFF_ITEMS
                else ""
            )
            parts.append(f"WRONG you emitted (not in gold) [{shown}{extra}]")
        lines.append(" ".join(parts))
    return " | ".join(lines)


def _clinical_hint(graded: dict[str, Any]) -> str:
    """Lead with the concrete gold-vs-pred diff; add a compact convention reminder.

    The diff is the high-signal part: it lets reflection match the gold's canonical
    granularity (e.g. 'focal epilepsy' not 'focal epilepsy - probable temporal'),
    de-duplicate, and stop inventing facts. Generic guidance is secondary.
    """

    diff = _diff_lines(graded)
    hints: list[str] = []
    if diff:
        hints.append("DIFF — " + diff + ".")
        hints.append(
            "Learn from the diff: emit the missed gold facts at the SAME concise "
            "canonical granularity shown (short concept, not a long qualified phrase), "
            "de-duplicate, and stop emitting the WRONG facts."
        )

    if graded["scorable"] and graded["n_scored"] < graded["n_facts"]:
        hints.append(
            "Some emitted facts were dropped before scoring: every 'evidence' must be "
            "copied verbatim as an exact substring of the letter, investigation "
            "modality must be MRI/CT/EEG/telemetry, and every SeizureFrequency fact "
            "needs a concrete state (a seizure count/rate, 'seizure-free', or a "
            "frequency change) — a bare 'unknown' state carries no attributes and is "
            "dropped."
        )
    return " ".join(hints)


def _feedback(
    graded: dict[str, Any],
    instr_tokens: int,
    demo_tokens: int,
    out_tokens: int,
    config: LengthPenaltyConfig,
) -> str:
    parts: list[str]
    if not graded["scorable"]:
        first_error = (graded["errors"] or ["unknown error"])[0]
        parts = [
            f"OUTPUT NOT SCORABLE ({first_error}). Return exactly one JSON object with "
            "a 'clinical_facts' list per output_schema; no markdown; every 'evidence' an "
            "exact substring of the letter."
        ]
    else:
        family_f1 = graded["family_f1"]
        family_str = ", ".join(f"{family}={family_f1[family]:.2f}" for family in KEY_FAMILIES)
        verdict = "CORRECT" if graded["headline_f1"] >= 0.999 else "PARTIAL"
        parts = [
            f"{verdict}. clinical_headline F1={graded['headline_f1']:.3f} "
            f"({family_str}). Emitted {graded['n_facts']} facts, "
            f"{graded['n_scored']} scored."
        ]
        hint = _clinical_hint(graded)
        if hint:
            parts.append(hint)

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
            f"Output is verbose ({out_tokens} tokens); emit only the de-duplicated facts, "
            "no extra keys or commentary."
        )
    return " ".join(parts)


def _clinical_facts_json_of(pred: Any) -> str:
    value = getattr(pred, "clinical_facts_json", None)
    if value is None and isinstance(pred, dict):
        value = pred.get("clinical_facts_json")
    return str(value) if value is not None else ""


def _predictor_lengths(pred_trace: Any) -> tuple[int, int]:
    if not pred_trace:
        return 0, 0
    try:
        predictor = pred_trace[-1][0]
    except (IndexError, TypeError):
        return 0, 0
    signature = getattr(predictor, "signature", None)
    instruction = getattr(signature, "instructions", "") if signature is not None else ""
    demo_tokens = sum(
        approx_tokens(str(dict(demo))) for demo in (getattr(predictor, "demos", None) or [])
    )
    return approx_tokens(instruction), demo_tokens


def _prompt_lengths(pred: Any, pred_trace: Any) -> tuple[int, int]:
    instr = getattr(pred, "instruction_tokens", None)
    demo = getattr(pred, "demo_tokens", None)
    if instr is not None:
        return int(instr), int(demo or 0)
    return _predictor_lengths(pred_trace)


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
        gold_letter = getattr(gold, "letter", None)
        if gold_letter is None:
            raise ValueError("GEPA example is missing the gold ExectLetter ('letter').")
        raw_output = _clinical_facts_json_of(pred)
        graded = _score_prediction(raw_output, gold_letter)

        instr_tokens, demo_tokens = _prompt_lengths(pred, pred_trace)
        out_tokens = approx_tokens(raw_output)

        quality = graded["headline_f1"] if graded["scorable"] else 0.0
        penalty = _length_penalty(instr_tokens, demo_tokens, out_tokens, cfg)
        score = max(0.0, quality - penalty)
        feedback = _feedback(graded, instr_tokens, demo_tokens, out_tokens, cfg)
        return dspy.Prediction(score=score, feedback=feedback)

    return metric
