"""Typed boundaries for ExECTv2 canonical orchestration."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import BaseModel

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)


class _FrozenDict(dict[str, Any]):
    """JSON-compatible recursively immutable mapping used at producer boundaries."""

    def _immutable(self, *_args: Any, **_kwargs: Any) -> None:
        raise TypeError("producer values are immutable")

    __setitem__ = __delitem__ = __setattr__ = clear = pop = popitem = setdefault = update = (  # type: ignore[assignment]
        _immutable
    )

    def __deepcopy__(self, memo: dict[int, Any]) -> dict[str, Any]:
        copied = {deepcopy(key, memo): deepcopy(value, memo) for key, value in self.items()}
        memo[id(self)] = copied
        return copied


class _FrozenList(list[Any]):
    """JSON-compatible recursively immutable sequence used at producer boundaries."""

    def _immutable(self, *_args: Any, **_kwargs: Any) -> None:
        raise TypeError("producer values are immutable")

    __setitem__ = __delitem__ = __setattr__ = append = clear = extend = insert = pop = remove = (
        reverse
    ) = sort = _immutable

    def __deepcopy__(self, memo: dict[int, Any]) -> list[Any]:
        copied = [deepcopy(value, memo) for value in self]
        memo[id(self)] = copied
        return copied


class _FrozenModelView:
    """Read-only attribute view of a Pydantic producer model."""

    __slots__ = ("_data",)

    def __init__(self, model: BaseModel) -> None:
        object.__setattr__(self, "_data", deep_freeze(model.model_dump(mode="python")))

    def __getattr__(self, name: str) -> Any:
        try:
            return self._data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, _name: str, _value: Any) -> None:
        raise TypeError("producer values are immutable")

    def model_dump(self, *, mode: str = "python", **_kwargs: Any) -> dict[str, Any]:
        del mode
        return deep_thaw(self._data)


def deep_freeze(value: Any) -> Any:
    """Copy nested producer data into JSON-compatible immutable containers."""

    if isinstance(value, BaseModel):
        return _FrozenModelView(value)
    if isinstance(value, Mapping):
        frozen = _FrozenDict()
        dict.update(frozen, {key: deep_freeze(item) for key, item in value.items()})
        return frozen
    if isinstance(value, list):
        return _FrozenList(deep_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(deep_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(deep_freeze(item) for item in value)
    return value


def deep_thaw(value: Any) -> Any:
    """Make a mutable deep copy for a downstream projection that may transform data."""

    if isinstance(value, Mapping):
        return {key: deep_thaw(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [deep_thaw(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return {deep_thaw(item) for item in value}
    return deepcopy(value)


@dataclass(frozen=True)
class StructuredMethodConfig:
    """Immutable selected policy for the one-call ExECT method pair."""

    prompt_profile: Literal["full"] = "full"
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
        cls, *, prompt_profile: Literal["full"] = "full"
    ) -> StructuredMethodConfig:
        return cls(prompt_profile=prompt_profile)

    @classmethod
    def archived_combined(
        cls, *, prompt_profile: Literal["full"] = "full"
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

    def __post_init__(self) -> None:
        object.__setattr__(self, "input_value", deep_freeze(self.input_value))
        object.__setattr__(self, "output_value", deep_freeze(self.output_value))

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
    route: str = ""
    dspy_cache: bool = True
    row: Mapping[str, Any] = field(default_factory=dict)
    stage_events: tuple[ExectStageEvent, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "parsed_record", deep_freeze(self.parsed_record))
        object.__setattr__(self, "flattened_mentions", deep_freeze(self.flattened_mentions))
        object.__setattr__(self, "row", deep_freeze(self.row))
        object.__setattr__(self, "stage_events", tuple(self.stage_events))


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
