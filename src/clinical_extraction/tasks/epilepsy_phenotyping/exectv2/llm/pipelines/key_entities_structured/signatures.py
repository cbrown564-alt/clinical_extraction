"""DSPy signature and module for the structured-event extractor.

Pure relocation from ``llm_only_key_entities_structured``. No logic changes.
"""

from __future__ import annotations

import dspy
from dspy.adapters.chat_adapter import ChatAdapter

from .constants import PROMPT_VERSION_V17, prompt_version_for

MINIMAL_SYSTEM_MESSAGE = (
    "Extract structured clinical events from the supplied clinical letter. "
    "Return the requested output fields exactly."
)


class MinimalSystemChatAdapter(ChatAdapter):
    """Keep DSPy's field parsing while replacing its generated system preamble."""

    def format(
        self,
        signature: type[dspy.Signature],
        demos: list[dict[str, object]],
        inputs: dict[str, object],
    ) -> list[dict[str, object]]:
        messages = super().format(signature, demos, inputs)
        messages[0] = {"role": "system", "content": MINIMAL_SYSTEM_MESSAGE}
        return messages


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
        selected_prompt_version = prompt_version or prompt_version_for()
        self._adapter = (
            MinimalSystemChatAdapter()
            if selected_prompt_version == PROMPT_VERSION_V17
            else None
        )
        self.predict = dspy.Predict(ExECTv2KeyEntitiesStructuredSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        if self._adapter is not None:
            with dspy.context(adapter=self._adapter):
                return self.predict(prompt_input_json=prompt_input_json)
        return self.predict(prompt_input_json=prompt_input_json)

    def render_messages(self, *, prompt_input_json: str) -> list[dict[str, object]]:
        """Render the initial model request without making a model call."""

        adapter = self._adapter or ChatAdapter()
        return adapter.format(
            ExECTv2KeyEntitiesStructuredSignature,
            demos=[],
            inputs={"prompt_input_json": prompt_input_json},
        )
