"""Five reported cells: two producers, one replay stack, optional prompt treatment.

These names replace the three-method results table. ``gan_llm_only`` remains
a live runner identity for existing cells. It is not a results column.

Cell ids are report identities, not a better-later depth axis.
``CELL_ORDER`` is table order only.
"""

from __future__ import annotations

from typing import Literal

RungId = Literal[
    "rules_only",
    "llm_extract",
    "llm_encode",
    "llm_select",
    "llm_pre_post",
]
TaskName = Literal["gan2026", "exectv2"]

RUNG_IDS: tuple[RungId, ...] = (
    "rules_only",
    "llm_extract",
    "llm_encode",
    "llm_select",
    "llm_pre_post",
)
# README / paper table order. Not replay order and not a depth axis.
RESULT_COLUMNS: tuple[RungId, ...] = (
    "rules_only",
    "llm_pre_post",
    "llm_extract",
    "llm_encode",
    "llm_select",
)
CELL_ORDER: dict[RungId, int] = {
    "rules_only": 1,
    "llm_pre_post": 2,
    "llm_extract": 3,
    "llm_encode": 4,
    "llm_select": 5,
}
# Sealed hops used these ints before the table was reordered.
LEGACY_HOP_ORDER: dict[RungId, int] = {
    "rules_only": 1,
    "llm_extract": 2,
    "llm_encode": 3,
    "llm_select": 4,
    "llm_pre_post": 5,
}

CELL_ID_ALIASES: dict[str, RungId] = {
    "llm_schema": "llm_extract",
    "llm_format": "llm_encode",
    "llm_revise": "llm_select",
    "llm_post": "llm_select",
}
METHOD_VIEW_ALIASES: dict[str, str] = {
    "gan_llm_schema": "gan_llm_extract",
    "gan_llm_extract_label_forms": "gan_llm_extract",
    "gan_llm_pre_post_label_forms": "gan_llm_and_rules_extract",
    "gan_llm_with_rules": "gan_llm_extract_raw",
    "gan_llm_format": "gan_llm_encode",
    "gan_llm_revise": "gan_llm_select",
    "exect_llm_schema": "exect_llm_extract",
    "exect_llm_format": "exect_llm_encode",
    "exect_llm_revise": "exect_llm_select",
    "exect_llm_post": "exect_llm_select",
}
# Paper/replay view for Gan select; live source-near extract is gan_llm_extract_raw.
GAN_SELECT_PAPER_VIEW = "gan_llm_select"
GAN_REVISE_PAPER_VIEW = GAN_SELECT_PAPER_VIEW

GAN_METHOD_FOR_RUNG: dict[RungId, str] = {
    "rules_only": "gan_rules",
    "llm_extract": "gan_llm_extract",
    "llm_encode": "gan_llm_encode",
    "llm_select": "gan_llm_extract_raw",
    "llm_pre_post": "gan_llm_and_rules_extract",
}
EXECT_METHOD_FOR_RUNG: dict[RungId, str] = {
    "rules_only": "exect_rules",
    "llm_extract": "exect_llm_extract",
    "llm_encode": "exect_llm_encode",
    "llm_select": "exect_llm_select",
    "llm_pre_post": "exect_llm_pre_post",
}
GAN_REPAIR_MODE_FOR_RUNG: dict[str, str] = {
    "llm_extract": "raw_model",
    "llm_encode": "gan_rules_encode",
    "llm_select": "llm_select_after_codebook",
    "llm_pre_post": "llm_select",
}
GAN_RUNG_SOURCE: dict[RungId, str] = {
    "rules_only": "standalone_rules",
    "llm_extract": "replay_gan_llm_extract_raw",
    "llm_encode": "replay_gan_llm_extract_raw",
    "llm_select": "replay_gan_llm_extract_raw",
    "llm_pre_post": "new_request",
}
EXECT_RUNG_SOURCE: dict[RungId, str] = {
    "rules_only": "standalone_rules",
    "llm_extract": "replay_exect_llm_extract",
    "llm_encode": "replay_exect_llm_extract",
    "llm_select": "replay_exect_llm_extract",
    "llm_pre_post": "living_exect_llm_pre_post",
}
EXECT_HOP_EFFECT_CLASS: dict[str, str] = {
    "exect.schema.parse": "extract",
    "exect.format.stop": "encode",
    "exect.validation.evidence": "validation",
    "exect.select.dictionary": "select",
    "exect.select.residual": "select",
    "exect.projection.clinical_fact": "projection",
}
EXECT_STAGE_EFFECT_CLASS: dict[str, str] = {
    "transport_or_schema": "extract",
    "representation": "encode",
    "clinical_meaning": "select",
    "validation_gate": "validation",
    "benchmark_projection": "projection",
}

REPAIR_MODE_ALIASES: dict[str, str] = {
    "selected_evidence_derivation": "llm_encode",
    "hybrid_full_stack": "llm_select",
    "llm_revise": "llm_select",
    "encode": "llm_encode",
    "revise": "llm_select",
    "select": "llm_select",
    "llm_encode_codebook": "gan_rules_encode",
}
EFFECT_CLASS_ALIASES: dict[str, str] = {
    "schema": "extract",
    "format": "encode",
    "semantic": "select",
    "revise": "select",
}
CELL_ORDER_TO_ID: dict[int, RungId] = {order: cell for cell, order in CELL_ORDER.items()}
LEGACY_HOP_ORDER_TO_ID: dict[int, RungId] = {
    order: cell for cell, order in LEGACY_HOP_ORDER.items()
}


def normalize_cell_id(value: str) -> RungId:
    """Map a cell id, including sealed-artifact aliases, to the live name."""

    mapped = CELL_ID_ALIASES.get(value, value)
    if mapped not in RUNG_IDS:
        raise ValueError(f"unknown cell id {value!r}")
    return mapped  # type: ignore[return-value]


def normalize_method_view(value: str) -> str:
    """Map a paper/replay method view name, including folder aliases."""

    return METHOD_VIEW_ALIASES.get(value, value)


def normalize_repair_mode(value: str) -> str:
    """Map a repair-mode string, including sealed-artifact aliases."""

    return REPAIR_MODE_ALIASES.get(value, value)


def normalize_effect_class(value: str) -> str:
    """Map a hop/stage effect class, including sealed-artifact aliases."""

    return EFFECT_CLASS_ALIASES.get(value, value)


def cell_id_from_legacy_rung(rung: int | str | None) -> RungId | None:
    """Resolve an old hop ``rung`` int (or string id) to a named cell id."""

    if rung is None:
        return None
    if isinstance(rung, int):
        return LEGACY_HOP_ORDER_TO_ID.get(rung)
    if isinstance(rung, str) and rung.isdigit():
        return LEGACY_HOP_ORDER_TO_ID.get(int(rung))
    return normalize_cell_id(str(rung))


def gan_method_for_rung(rung: RungId | str) -> str:
    """Return the Gan paper identity for one cell."""

    return GAN_METHOD_FOR_RUNG[normalize_cell_id(rung)]


def exect_method_for_rung(rung: RungId | str) -> str:
    """Return the ExECT paper identity for one cell."""

    return EXECT_METHOD_FOR_RUNG[normalize_cell_id(rung)]


def repair_mode_for_gan_rung(rung: str) -> str:
    """Return the StructuredRepairConfig mode that implements a Gan replay cell."""

    try:
        return GAN_REPAIR_MODE_FOR_RUNG[normalize_cell_id(rung)]
    except (KeyError, ValueError) as exc:
        raise ValueError(f"Gan cell {rung!r} has no replay repair mode") from exc


def normalize_rungs_payload(rungs: dict[str, object]) -> dict[str, object]:
    """Rewrite sealed comparison ``rungs`` keys to live cell ids."""

    return {normalize_cell_id(key): value for key, value in rungs.items()}
