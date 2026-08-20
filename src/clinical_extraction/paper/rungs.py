"""Five paper rungs of rule help.

These names replace the three-method results table. ``gan_llm_only`` remains
a live runner identity for existing cells. It is not a results column.
"""

from __future__ import annotations

from typing import Literal

RungId = Literal[
    "rules_only",
    "llm_schema",
    "llm_format",
    "llm_post",
    "llm_pre_post",
]
TaskName = Literal["gan2026", "exectv2"]

RUNG_IDS: tuple[RungId, ...] = (
    "rules_only",
    "llm_schema",
    "llm_format",
    "llm_post",
    "llm_pre_post",
)
RESULT_COLUMNS: tuple[RungId, ...] = RUNG_IDS

GAN_METHOD_FOR_RUNG: dict[RungId, str] = {
    "rules_only": "gan_rules",
    "llm_schema": "gan_llm_schema",
    "llm_format": "gan_llm_format",
    "llm_post": "gan_llm_with_rules",
    "llm_pre_post": "gan_llm_pre_post",
}
EXECT_METHOD_FOR_RUNG: dict[RungId, str] = {
    "rules_only": "exect_rules",
    "llm_schema": "exect_llm_schema",
    "llm_format": "exect_llm_format",
    "llm_post": "exect_llm_post",
    "llm_pre_post": "exect_llm_with_rules",
}
GAN_REPAIR_MODE_FOR_RUNG: dict[str, str] = {
    "llm_schema": "raw_model",
    "llm_format": "selected_evidence_derivation",
    "llm_post": "hybrid_full_stack",
    "llm_pre_post": "hybrid_full_stack",
}
GAN_RUNG_SOURCE: dict[RungId, str] = {
    "rules_only": "standalone_rules",
    "llm_schema": "replay_gan_llm_with_rules",
    "llm_format": "replay_gan_llm_with_rules",
    "llm_post": "replay_gan_llm_with_rules",
    "llm_pre_post": "new_request",
}
EXECT_RUNG_SOURCE: dict[RungId, str] = {
    "rules_only": "standalone_rules",
    "llm_schema": "replay_exect_llm_only",
    "llm_format": "replay_exect_llm_only",
    "llm_post": "replay_exect_llm_only",
    "llm_pre_post": "living_exect_llm_with_rules",
}
RUNG_DEPTH: dict[RungId, int] = {
    "rules_only": 1,
    "llm_schema": 2,
    "llm_format": 3,
    "llm_post": 4,
    "llm_pre_post": 5,
}
EXECT_HOP_EFFECT_CLASS: dict[str, str] = {
    "exect.schema.parse": "schema",
    "exect.format.stop": "format",
    "exect.validation.evidence": "validation",
    "exect.select.dictionary": "semantic",
    "exect.select.residual": "semantic",
    "exect.projection.clinical_fact": "projection",
}
EXECT_STAGE_EFFECT_CLASS: dict[str, str] = {
    "transport_or_schema": "schema",
    "representation": "format",
    "clinical_meaning": "semantic",
    "validation_gate": "validation",
    "benchmark_projection": "projection",
}


def gan_method_for_rung(rung: RungId) -> str:
    """Return the Gan paper identity for one rung."""

    return GAN_METHOD_FOR_RUNG[rung]


def exect_method_for_rung(rung: RungId) -> str:
    """Return the ExECT paper identity for one rung."""

    return EXECT_METHOD_FOR_RUNG[rung]


def repair_mode_for_gan_rung(rung: str) -> str:
    """Return the StructuredRepairConfig mode that implements a Gan replay rung."""

    try:
        return GAN_REPAIR_MODE_FOR_RUNG[rung]
    except KeyError as exc:
        raise ValueError(f"Gan rung {rung!r} has no replay repair mode") from exc
