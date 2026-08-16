"""DSPy signature and module for structured-event extraction."""

from __future__ import annotations

import dspy
from dspy.adapters.chat_adapter import ChatAdapter


class ExECTv2KeyEntitiesStructuredSignature(dspy.Signature):
    """Read one clinical letter and produce structured clinical events.

    Return exactly one JSON object with a 'clinical_events' list. No markdown.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and task instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            'One strict JSON object: {"clinical_events": [{"family": ..., '
            '"anchor_text": ..., "evidence": ..., "event_state": {...}, '
            '"mentions": [{"entity": ..., "text": ..., "attributes": {...}}], '
            '"confidence": ..., "rationale": ""}, ...]}. Rationale may be '
            "an empty string; do not include analysis or first-person reasoning."
        )
    )


class DspyKeyEntitiesStructuredExtractor(dspy.Module):
    def __init__(self, *, prompt_version: str | None = None) -> None:
        super().__init__()
        del prompt_version  # Call-site compatibility; only v0.9.24 / v0.9.40 remain.
        self._signature: type[dspy.Signature] = ExECTv2KeyEntitiesStructuredSignature
        self.predict = dspy.Predict(self._signature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)

    def render_messages(self, *, prompt_input_json: str) -> list[dict[str, object]]:
        """Render the initial model request without making a model call."""

        return ChatAdapter().format(
            self._signature,
            demos=[],
            inputs={"prompt_input_json": prompt_input_json},
        )
