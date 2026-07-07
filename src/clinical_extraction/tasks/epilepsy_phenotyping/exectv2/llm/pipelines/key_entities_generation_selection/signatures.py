"""DSPy signatures and program wrappers for the generation-selection route."""

from __future__ import annotations

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)


class QwenGenerationSelectionExtractor:
    """Two-call DSPy wrapper: model generation followed by model finalization."""

    def __init__(self) -> None:
        self.predict = dspy.Predict(structured.ExECTv2KeyEntitiesStructuredSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)

    __call__ = forward


class ExECTv2KeyEntitiesInventorySelectionSignature(dspy.Signature):
    """Read one clinical letter and emit generated events plus final selected events.

    Return exactly one JSON object with generated_events and final_events. No markdown.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and task instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            'One strict JSON object: {"generated_events": [...], '
            '"final_events": [...], "selection_summary": [...]}. Each event '
            "uses family, anchor_text, evidence, event_state, mentions, confidence, "
            "and rationale. Do not include analysis or first-person reasoning."
        )
    )


class QwenSingleCallInventoryExtractor:
    """Single-call wrapper: Qwen emits generated inventory and final selection."""

    def __init__(self) -> None:
        self.predict = dspy.Predict(ExECTv2KeyEntitiesInventorySelectionSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)

    __call__ = forward


class ExECTv2KeyEntitiesMentionSelectionSignature(dspy.Signature):
    """Read one clinical letter and emit generated mentions plus final mentions.

    Return exactly one JSON object with generated_mentions and final_mentions.
    No markdown.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and task instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            'One strict JSON object: {"generated_mentions": [...], '
            '"final_mentions": [...], "selection_summary": [...]}. Each mention '
            "uses entity, text, attributes, evidence, confidence, and rationale. "
            "Do not include analysis or first-person reasoning."
        )
    )


class QwenSingleCallMentionExtractor:
    """Single-call wrapper: Qwen emits generated and final rendered mentions."""

    def __init__(self) -> None:
        self.predict = dspy.Predict(ExECTv2KeyEntitiesMentionSelectionSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)

    __call__ = forward


class ExECTv2KeyEntitiesMentionIdSelectionSignature(dspy.Signature):
    """Read one clinical letter and emit generated mentions plus selected IDs.

    Return exactly one JSON object with generated_mentions and final_mention_ids.
    No markdown.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and task instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            'One strict JSON object: {"generated_mentions": [...], '
            '"final_mention_ids": [...], "selection_summary": [...]}. Each '
            "generated mention uses mention_id, entity, text, attributes, evidence, "
            "confidence, and rationale. Do not include analysis or first-person "
            "reasoning."
        )
    )


class QwenSingleCallMentionIdExtractor:
    """Single-call wrapper: Qwen emits mentions once and selects by ID."""

    def __init__(self) -> None:
        self.predict = dspy.Predict(ExECTv2KeyEntitiesMentionIdSelectionSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)

    __call__ = forward


class ExECTv2DedupClinicalFactsSignature(dspy.Signature):
    """Read one clinical letter and emit de-duplicated clinical facts.

    Return exactly one JSON object with clinical_facts. No markdown.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and de-duplicated fact instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            'One strict JSON object: {"clinical_facts": [...]}. Each fact uses '
            "family-specific simplified fields plus exact evidence. Do not include "
            "analysis or first-person reasoning."
        )
    )


class QwenSingleCallDedupFactsExtractor:
    """Single-call wrapper: model emits de-duplicated clinical facts directly."""

    def __init__(self) -> None:
        self.predict = dspy.Predict(ExECTv2DedupClinicalFactsSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)

    __call__ = forward


class ExECTv2KeyEntitiesPoolAdjudicationSignature(dspy.Signature):
    """Read one letter and select final IDs from Qwen-generated mention tables.

    Return exactly one JSON object with final_mention_ids. No markdown.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter, model-generated mentions, and task instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            'One strict JSON object: {"final_mention_ids": [...], '
            '"selection_summary": [...]}. Select only mention_id values that '
            "appear in model_generated_mentions. Do not include analysis or "
            "first-person reasoning."
        )
    )


class QwenPoolAdjudicationExtractor:
    """Replay wrapper: Qwen selects among prior Qwen-generated mention IDs."""

    def __init__(self) -> None:
        self.predict = dspy.Predict(ExECTv2KeyEntitiesPoolAdjudicationSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)

    __call__ = forward
