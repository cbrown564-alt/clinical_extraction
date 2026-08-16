"""DSPy signature, request adapter, and module for structured-event extraction."""

from __future__ import annotations

import dspy
from dspy.adapters.chat_adapter import ChatAdapter

from .constants import (
    PROMPT_VERSION_V17,
    PROMPT_VERSION_V18,
    PROMPT_VERSION_V19,
    PROMPT_VERSION_V20,
    PROMPT_VERSION_V21,
    PROMPT_VERSION_V22,
    PROMPT_VERSION_V23,
    PROMPT_VERSION_V24,
    PROMPT_VERSION_V25,
    PROMPT_VERSION_V26,
    PROMPT_VERSION_V27,
    prompt_version_for,
)

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


class ExECTv2KeyEntitiesStructuredSignatureV26(dspy.Signature):
    """Read one clinical letter and produce structured clinical events.

    Return exactly one JSON object with a 'clinical_events' list. No markdown.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and task instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            'One JSON object: {"clinical_events": [{"clinical_family": ..., '
            '"event": ..., "evidence": ..., "attributes": {...}}, ...]}.'
        )
    )


_MINIMAL_SYSTEM_PROMPT_VERSIONS = frozenset(
    {
        PROMPT_VERSION_V17,
        PROMPT_VERSION_V18,
        PROMPT_VERSION_V19,
        PROMPT_VERSION_V20,
        PROMPT_VERSION_V21,
        PROMPT_VERSION_V22,
        PROMPT_VERSION_V23,
        PROMPT_VERSION_V24,
        PROMPT_VERSION_V25,
        PROMPT_VERSION_V26,
        PROMPT_VERSION_V27,
    }
)


class DspyKeyEntitiesStructuredExtractor(dspy.Module):
    def __init__(self, *, prompt_version: str | None = None) -> None:
        super().__init__()
        selected_prompt_version = prompt_version or prompt_version_for()
        self._signature: type[dspy.Signature] = (
            ExECTv2KeyEntitiesStructuredSignatureV26
            if selected_prompt_version in {PROMPT_VERSION_V26, PROMPT_VERSION_V27}
            else ExECTv2KeyEntitiesStructuredSignature
        )
        self._adapter = (
            MinimalSystemChatAdapter()
            if selected_prompt_version in _MINIMAL_SYSTEM_PROMPT_VERSIONS
            else None
        )
        self.predict = dspy.Predict(self._signature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        if self._adapter is not None:
            with dspy.context(adapter=self._adapter):
                return self.predict(prompt_input_json=prompt_input_json)
        return self.predict(prompt_input_json=prompt_input_json)

    def render_messages(self, *, prompt_input_json: str) -> list[dict[str, object]]:
        """Render the initial model request without making a model call."""

        adapter = self._adapter or ChatAdapter()
        return adapter.format(
            self._signature,
            demos=[],
            inputs={"prompt_input_json": prompt_input_json},
        )
