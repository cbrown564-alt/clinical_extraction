"""Decoupled confidence reviewer (variant D) — failure-mode-primed calibration.

A post-selection, **label-blind-to-rationale** confidence estimator. Given a clinic
note and an already-chosen seizure-frequency answer, it returns a calibrated
probability that the answer is correct, in a SEPARATE model call that does not see
the model's own events/rationale (the decoupling) and that explicitly names the
dominant unknown↔rate over-reading failure (the priming).

Why this exists (validated 2026-06-17; see
```` and
``experiments/gan2026_reliability_confidence_elicitation_pilot160_2026-06-17.md``):
on a 160-row residual-enriched validation pilot, this decoupled + failure-primed
elicitation produced a failure-prediction AUROC of **0.755** (near the external
cross-model-agreement signal, 0.781), versus **0.503** (chance) for the in-pass
*joint* self-confidence fields it sits beside (``StructuredSelectionRecord.confidence``,
``FreshEvidenceDecision.uncertainty``).

**One-call vs two-call paired test (2026-06-17 — see**
````**).**
Tested whether the priming alone (folded into the extraction call) replaces this
decoupled call. Validation750 could not separate them (joint 0.609 vs decoupled 0.641,
paired diff +0.032, 95% CI [-0.032, +0.098] — includes 0), which suggested the call was
removable. **The frozen test450 holdout overturned that:** decoupled 0.669 vs joint
0.601, paired diff **+0.068, 95% CI [+0.014, +0.132] — excludes 0**; and folding the
priming into extraction *degraded* Purist accuracy (0.767 vs SE 0.809). Direction
(decoupled ≥ joint) was consistent on both splits. **Conclusion: keep this decoupled
stage** — the separate rationale-blind call earns its cost on the holdout. (The
degenerate in-pass ``selection.confidence`` (0.497) is still degenerate because it is
unprimed/categorical, but a primed in-pass field does not match this decoupled call on
test.) Both self-signals remain modest (< external corroboration 0.781) and gate nothing.

**SHADOW STAGE.** This estimator never changes the label. It only stamps a continuous
``calibrated_confidence`` (+ ``risk = 1 - calibrated_confidence``) alongside the
existing intrinsic confidence fields. It gates nothing until the 0.755 is confirmed at
validation750 scale and passes a robustness battery. Caveat: the pilot rested on 12
failures (wide CI), and even variant D still hides roughly half its failures at
confidence ≥ 0.9, so it complements — does not replace — external corroboration.

Single-shot elicitation at temperature 0 is correct here: this is a point calibration
probe, not a sampling/consistency probe (the varying-temperature rule scopes to
self-consistency / semantic entropy only).

Migrated to :mod:`stage_protocol` (prompt builder + decision schema + postprocess policy).
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.stage_protocol import (
    AgenticStage,
    DspyCallSpec,
    ParsedStageResponse,
    build_isolated_dspy_lm,
    extract_json_object,
    make_dspy_predictor,
    run_dspy_json_call,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair import (
    parse_json_payload_with_schema_repair,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord

CONFIDENCE_REVIEWER_VERSION = "variant_D_decoupled_v1"
DEFAULT_MODEL = "openai/gpt-4.1-mini"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOKENS = 300

# Variant D prompt — the failure-mode-primed elicitation that the pilot validated.
# Kept identical in spirit to the predeclared experiment; this module is now the
# production owner of the wording.
VARIANT_D_INSTRUCTIONS: tuple[str, ...] = (
    "The clinic letter below has already been assigned the seizure-frequency answer shown.",
    "Estimate the probability (an integer 0-100) that this stated answer is the CORRECT "
    "purist seizure-frequency category.",
    "Weigh explicitly the most common way such answers are wrong: a NON-QUANTIFIABLE "
    "description — a single last-event date, an event 'since' some anchor, a provoked or "
    "transient event, or one isolated seizure — is mistakenly read as an ongoing habitual "
    "RATE when the correct answer is 'unknown'; or, conversely, a genuine current rate is "
    "wrongly called 'unknown'.",
    "Decide how exposed THIS specific answer is to that error, then report the probability "
    "that the stated answer is correct.",
    "Return exactly one JSON object: "
    '{"probability": <int 0-100>, "reason": "<one short sentence>"}.',
)


class ConfidenceReviewSignature(dspy.Signature):
    """Estimate a calibrated probability for a pre-existing seizure-frequency answer.

    Return exactly one strict JSON object:
    {"probability": <integer 0-100>, "reason": "<one short sentence>"}.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON with one clinical note, the stated answer, and the elicitation question."
    )
    elicitation_json: str = dspy.OutputField(
        desc='One strict JSON object: integer "probability" (0-100) and a short "reason".'
    )


class ConfidenceReviewDecision(BaseModel):
    """Strict schema for variant-D confidence elicitation."""

    model_config = ConfigDict(extra="forbid")

    probability: int = Field(ge=0, le=100)
    reason: str | None = None


@dataclass(frozen=True)
class ConfidenceReview:
    """The reviewer's verdict for one row. ``calibrated_confidence`` is P(correct)."""

    calibrated_confidence: float | None
    risk: float | None
    probability_0_100: int | None
    reason: str | None
    error: str | None
    source: str = CONFIDENCE_REVIEWER_VERSION

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


_DSPY_SPEC = DspyCallSpec(
    ConfidenceReviewSignature,
    input_field="prompt_input_json",
    output_field="elicitation_json",
)


class ConfidenceReviewStage(AgenticStage[ConfidenceReviewDecision]):
    """Shadow-stage scaffold: prompt + schema + parse policy (no split runner)."""

    @property
    def prompt_version(self) -> str:
        return CONFIDENCE_REVIEWER_VERSION

    def build_prompt_input(
        self,
        record: GanFrequencyRecord,
        *,
        final_label: str | None,
        final_kind: str | None,
        **_: object,
    ) -> str:
        return build_review_payload(record.note_text, final_label, final_kind)

    def parse_response(
        self, raw_output: str, **_: object
    ) -> ParsedStageResponse[ConfidenceReviewDecision]:
        return _parse_confidence_response(raw_output)


STAGE = ConfidenceReviewStage()


def build_review_payload(note_text: str, final_label: str | None, final_kind: str | None) -> str:
    """Build the elicitation payload. Deliberately carries ONLY the note and the stated
    answer — never the model's own events/rationale — to preserve the decoupling."""
    payload = {
        "task": "Gan 2026 seizure-frequency confidence elicitation",
        "variant": "D",
        "confidence_reviewer_version": CONFIDENCE_REVIEWER_VERSION,
        "instructions": list(VARIANT_D_INSTRUCTIONS),
        "stated_answer": {"final_label": final_label, "answer_kind": final_kind},
        "allowed_output_fields": ["probability", "reason"],
        "note_text": note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_probability(raw: str) -> tuple[int | None, str | None, str | None]:
    """Return (probability_0_100, reason, error) from the raw model output."""
    parsed = _parse_confidence_response(raw)
    if parsed.decision is not None:
        error = None
        for note in parsed.parse_errors:
            if note == "regex_int_fallback":
                error = note
                break
        return parsed.decision.probability, parsed.decision.reason, error
    error = next(
        (err for err in parsed.parse_errors if not err.startswith("json_dialect_repaired:")),
        parsed.parse_errors[0] if parsed.parse_errors else "parse_failed",
    )
    reason = None
    if raw and "reason" in raw:
        try:
            obj, _ = parse_json_payload_with_schema_repair(extract_json_object(raw))
            if isinstance(obj, dict):
                reason = obj.get("reason")
        except json.JSONDecodeError:
            pass
    return None, reason, error


def review_from_raw(raw: str) -> ConfidenceReview:
    """Build a ConfidenceReview from a raw elicitation string (pure, no model call)."""
    prob, reason, err = parse_probability(raw)
    if prob is None:
        return ConfidenceReview(None, None, None, reason, err or "no_probability_field")
    p = prob / 100.0
    return ConfidenceReview(
        calibrated_confidence=p, risk=1.0 - p, probability_0_100=prob, reason=reason, error=None
    )


class ConfidenceReviewer:
    """Decoupled variant-D confidence estimator. Holds its own LM so its temperature
    and cache settings never disturb the host pass's LM configuration."""

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        api_base: str | None = None,
        lm: dspy.LM | None = None,
        stage: ConfidenceReviewStage | None = None,
    ) -> None:
        self._stage = stage or STAGE
        self._lm = lm or build_isolated_dspy_lm(
            model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_base=api_base,
        )
        self._predict = make_dspy_predictor(_DSPY_SPEC)

    def review(
        self, *, note_text: str, final_label: str | None, final_kind: str | None
    ) -> ConfidenceReview:
        payload = build_review_payload(note_text, final_label, final_kind)
        try:
            raw = run_dspy_json_call(
                self._predict,
                lm=self._lm,
                input_field=_DSPY_SPEC.input_field,
                output_field=_DSPY_SPEC.output_field,
                prompt_input_json=payload,
            )
        except Exception as exc:  # pragma: no cover - live API only
            return ConfidenceReview(None, None, None, None, f"{type(exc).__name__}: {exc}")
        return review_from_raw(raw)


def _parse_confidence_response(raw: str) -> ParsedStageResponse[ConfidenceReviewDecision]:
    if not raw or not raw.strip():
        return ParsedStageResponse(None, parse_errors=["empty_output"])
    try:
        raw_payload, dialect_notes = parse_json_payload_with_schema_repair(extract_json_object(raw))
    except json.JSONDecodeError:
        digits = re.search(r"\b(\d{1,3})\b", raw)
        if digits:
            prob = _clamp(int(digits.group(1)))
            return ParsedStageResponse(
                ConfidenceReviewDecision(probability=prob, reason=None),
                parse_errors=["regex_int_fallback"],
            )
        return ParsedStageResponse(None, parse_errors=["parse_failed"])

    parse_errors = list(dialect_notes)
    if not isinstance(raw_payload, dict):
        return ParsedStageResponse(None, parse_errors=[*parse_errors, "no_probability_field"])
    prob_raw = raw_payload.get("probability")
    try:
        probability = _clamp(int(round(float(prob_raw))))
    except (TypeError, ValueError):
        return ParsedStageResponse(
            None,
            parse_errors=[*parse_errors, "no_probability_field"],
        )
    reason = raw_payload.get("reason")
    try:
        decision = ConfidenceReviewDecision(
            probability=probability,
            reason=str(reason) if reason is not None else None,
        )
    except ValidationError as exc:
        return ParsedStageResponse(
            None,
            parse_errors=[*parse_errors, f"schema_validation_error: {exc.errors()[0]['msg']}"],
        )
    return ParsedStageResponse(decision, parse_errors=parse_errors)


def _clamp(value: int) -> int:
    return max(0, min(100, value))
