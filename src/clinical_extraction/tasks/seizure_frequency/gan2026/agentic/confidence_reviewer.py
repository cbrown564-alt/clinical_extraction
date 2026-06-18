"""Decoupled confidence reviewer (variant D) — failure-mode-primed calibration.

A post-selection, **label-blind-to-rationale** confidence estimator. Given a clinic
note and an already-chosen seizure-frequency answer, it returns a calibrated
probability that the answer is correct, in a SEPARATE model call that does not see
the model's own events/rationale (the decoupling) and that explicitly names the
dominant unknown↔rate over-reading failure (the priming).

Why this exists (validated 2026-06-17; see
``docs/research/gan2026_confidence_elicitation_predeclaration_2026-06-17.md`` and
``experiments/gan2026_reliability_confidence_elicitation_pilot160_2026-06-17.md``):
on a 160-row residual-enriched validation pilot, this decoupled + failure-primed
elicitation produced a failure-prediction AUROC of **0.755** (near the external
cross-model-agreement signal, 0.781), versus **0.503** (chance) for the in-pass
*joint* self-confidence fields it sits beside (``StructuredSelectionRecord.confidence``,
``FreshEvidenceDecision.uncertainty``).

**One-call vs two-call paired test (2026-06-17 — see**
``docs/research/gan2026_confidence_one_vs_two_call_test450_predeclaration_2026-06-17.md``**).**
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
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass

import dspy

from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

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
    if not raw or not raw.strip():
        return None, None, "empty_output"
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    text = match.group(0) if match else raw
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        digits = re.search(r"\b(\d{1,3})\b", raw)
        if digits:
            return _clamp(int(digits.group(1))), None, "regex_int_fallback"
        return None, None, "parse_failed"
    prob = obj.get("probability")
    try:
        return _clamp(int(round(float(prob)))), obj.get("reason"), None
    except (TypeError, ValueError):
        return None, obj.get("reason"), "no_probability_field"


def _clamp(value: int) -> int:
    return max(0, min(100, value))


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
    ) -> None:
        self._lm = lm or build_dspy_lm(
            model,
            temperature=temperature,
            max_tokens=max_tokens,
            cache=False,
            api_base=api_base,
            num_retries=2,
            timeout=60,
        )
        self._predict = dspy.Predict(ConfidenceReviewSignature)

    def review(
        self, *, note_text: str, final_label: str | None, final_kind: str | None
    ) -> ConfidenceReview:
        payload = build_review_payload(note_text, final_label, final_kind)
        try:
            with dspy.context(lm=self._lm):
                raw = str(self._predict(prompt_input_json=payload).elicitation_json)
        except Exception as exc:  # pragma: no cover - live API only
            return ConfidenceReview(None, None, None, None, f"{type(exc).__name__}: {exc}")
        return review_from_raw(raw)
