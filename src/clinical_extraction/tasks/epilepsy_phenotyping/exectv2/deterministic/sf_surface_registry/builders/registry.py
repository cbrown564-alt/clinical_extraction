"""Builder registry and catalog-driven adapter loops."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from ..catalog import rules_for_phase
from ..types import SurfacePhase, SurfaceRule
from .context import ConventionContext, ResidualCandidate, RewriteResult

NoiseSignal = bool | None  # True=noise, False=definite not-noise, None=continue
NoiseBuilder = Callable[[ConventionContext], NoiseSignal]
RewriteBuilder = Callable[[ConventionContext], RewriteResult | None]
ResidualBuilder = Callable[[str], list[ResidualCandidate]]
OperandBuilder = Callable[[ConventionContext], RewriteResult | None]

_BUILDER_REGISTRY: dict[str, RewriteBuilder | NoiseBuilder | ResidualBuilder | OperandBuilder] = {}


def register_builder(name: str):
    def decorator(fn: object) -> object:
        _BUILDER_REGISTRY[name] = fn  # type: ignore[assignment]
        return fn

    return decorator


def get_builder(name: str) -> object:
    return _BUILDER_REGISTRY[name]


def _builder_name(rule: SurfaceRule) -> str:
    return rule.builder or rule.rule_id


def apply_operand_format(ctx: ConventionContext) -> RewriteResult | None:
    fn = _BUILDER_REGISTRY.get("operand_format_rewrite")
    if fn is None:
        return None
    return fn(ctx)  # type: ignore[return-value]


def apply_rewrite_builders(ctx: ConventionContext) -> RewriteResult | None:
    operand = apply_operand_format(ctx)
    if operand is not None:
        return operand
    for rule in rules_for_phase(SurfacePhase.REWRITE):
        builder = _BUILDER_REGISTRY.get(_builder_name(rule))
        if builder is None:
            continue
        result = builder(ctx)  # type: ignore[operator]
        if result is not None:
            return result
    return None


def apply_noise_builders(ctx: ConventionContext) -> bool:
    for rule in rules_for_phase(SurfacePhase.NOISE):
        builder = _BUILDER_REGISTRY.get(_builder_name(rule))
        if builder is None:
            continue
        signal = builder(ctx)  # type: ignore[operator]
        if signal is True:
            return True
        if signal is False:
            return False
    return False


def collect_residual_candidates(note_text: str) -> list[ResidualCandidate]:
    additions: list[ResidualCandidate] = []
    for rule in rules_for_phase(SurfacePhase.RESIDUAL_ADD):
        builder = _BUILDER_REGISTRY.get(_builder_name(rule))
        if builder is None:
            continue
        additions.extend(builder(note_text))  # type: ignore[operator]
    return additions


def apply_rewrite(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> RewriteResult | None:
    return apply_rewrite_builders(ConventionContext(text, evidence, attributes))


def apply_noise(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> bool:
    return apply_noise_builders(ConventionContext(text, evidence, attributes))


def residual_candidates(note_text: str) -> list[ResidualCandidate]:
    return collect_residual_candidates(note_text)


def _load_builders() -> None:
    from . import rewrite_builders as _rewrite_builders  # noqa: F401
    from . import noise_builders as _noise_builders  # noqa: F401
    from . import residual_builders as _residual_builders  # noqa: F401


_load_builders()
