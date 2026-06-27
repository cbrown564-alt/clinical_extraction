"""Stage 1: clinical-findings extraction (LLM signature + module)."""

from __future__ import annotations

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.clinical_findings.prompt_builders import (
    build_prompt_input,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.clinical_findings.parsing import (
    parse_clinical_findings_json,
)

__all__ = [
    "DspyClinicalFindingsSFExtractor",
    "ExECTv2ClinicalFindingsSFSignature",
    "build_prompt_input",
    "parse_clinical_findings_json",
]


class ExECTv2ClinicalFindingsSFSignature(dspy.Signature):
    """Read one clinical letter and return seizure frequency findings as JSON.

    Return a strict JSON object with key 'findings'. No markdown wrapper.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and task instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"event_frames\": [{\"event_id\": ..., "
            "\"evidence\": ..., \"seizure_phrase\": ..., \"target_status\": ..., "
            "\"statement_family\": ...}], \"findings\": [{\"text\": ..., "
            "\"evidence\": ..., \"clinical_kind\": ..., "
            "\"frequency_statement_type\": ..., \"source_role\": ..., "
            "\"count\": ..., \"period_unit\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )


class DspyClinicalFindingsSFExtractor(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2ClinicalFindingsSFSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)
