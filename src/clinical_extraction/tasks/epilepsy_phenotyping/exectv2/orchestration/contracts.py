"""Typed boundaries for ExECTv2 canonical orchestration."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)


@dataclass(frozen=True)
class StructuredMethodConfig:
    """Immutable selected policy for the one-call ExECT method pair."""

    prompt_profile: Literal["full", "qwen_compact"] = "full"
    diagnosis_policy_variant: str = "default"
    prescription_policy_variant: str = "default"
    sf_projection_ablation: Literal["none", "state", "ownership", "combined"] = "combined"
    archived_replay: bool = False
    diagnosis_resolution_candidate: bool = False
    model_preserving_policy_candidate: bool = False
    prescription_rescue_scope_candidate: bool = False

    def __post_init__(self) -> None:
        if self.diagnosis_policy_variant not in {"default", "combined"}:
            raise ValueError(
                "diagnosis_policy_variant must be 'default' or 'combined'"
            )
        if self.prescription_policy_variant not in {"default", "combined"}:
            raise ValueError(
                "prescription_policy_variant must be 'default' or 'combined'"
            )
        if self.has_archived_policy and not self.archived_replay:
            raise ValueError(
                "non-selected policy requires archived_replay=True"
            )

    @property
    def has_archived_policy(self) -> bool:
        """Return whether any setting changes the selected method policy."""

        return (
            self.diagnosis_policy_variant != "default"
            or self.prescription_policy_variant != "default"
            or self.sf_projection_ablation != "combined"
            or self.diagnosis_resolution_candidate
            or self.model_preserving_policy_candidate
            or self.prescription_rescue_scope_candidate
        )

    @property
    def is_selected(self) -> bool:
        """Return whether this is an immutable selected-method configuration."""

        return not self.archived_replay and not self.has_archived_policy

    def require_selected(self) -> None:
        """Reject archived or candidate behavior at a selected entry point."""

        if not self.is_selected:
            raise ValueError(
                "selected ExECT method requires default/default policy, combined SF "
                "projection, and no archived or candidate switches"
            )

    @classmethod
    def selected(
        cls, *, prompt_profile: Literal["full", "qwen_compact"] = "full"
    ) -> StructuredMethodConfig:
        return cls(prompt_profile=prompt_profile)

    @classmethod
    def archived_combined(
        cls, *, prompt_profile: Literal["full", "qwen_compact"] = "full"
    ) -> StructuredMethodConfig:
        return cls(
            prompt_profile=prompt_profile,
            diagnosis_policy_variant="combined",
            prescription_policy_variant="combined",
            archived_replay=True,
        )


@dataclass(frozen=True)
class ExectStageEvent:
    stage_id: str
    owner: str
    effect_class: str
    input_value: Any = None
    output_value: Any = None
    changed: bool = False
    action: str = ""
    rule_category: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "owner": self.owner,
            "effect_class": self.effect_class,
            "input_value": self.input_value,
            "output_value": self.output_value,
            "changed": self.changed,
            "action": self.action,
            "rule_category": self.rule_category,
        }


@dataclass(frozen=True)
class StructuredProducerResult:
    """Immutable output of the one structured model/replay boundary."""

    letter_id: str
    prompt_input_json: str
    raw_output: str
    parsed_record: Any
    flattened_mentions: tuple[Any, ...]
    projected_letter: PredictedLetter
    gate_warnings: tuple[str, ...]
    initial_parse_errors: tuple[str, ...] = ()
    parse_errors: tuple[str, ...] = ()
    format_retry_output: str = ""
    format_retry_notes: tuple[str, ...] = ()
    call_error: str | None = None
    model: str = ""
    mode: str = ""
    row: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExectRecordResult:
    """Final method projection plus the producer and stage trace it used."""

    prediction: PredictedLetter
    row: Mapping[str, Any]
    stage_events: tuple[ExectStageEvent, ...]
    producer: StructuredProducerResult
    scorer_projection: Mapping[str, Any] = field(default_factory=dict)
    first_prediction_changing_owner: str | None = None
    first_failure: str | None = None

    @property
    def output(self) -> PredictedLetter:
        return self.prediction
