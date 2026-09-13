from __future__ import annotations

from enum import StrEnum


class RowPolicy(StrEnum):
    ILLUSTRATIVE = "illustrative"
    DEVELOPMENT_ROW_LEVEL = "development_row_level"
    AGGREGATE_ONLY = "aggregate_only"
    DENIED = "denied"

    @property
    def permits_records(self) -> bool:
        return self in {self.ILLUSTRATIVE, self.DEVELOPMENT_ROW_LEVEL}


def _key(value: str) -> str:
    return "".join(character for character in value.casefold() if character.isalnum())


def _ids_are_permitted(
    source_ids: tuple[str, ...],
    permitted_development_ids: frozenset[str] | None,
) -> bool:
    if permitted_development_ids is None:
        return True
    return bool(source_ids) and set(source_ids).issubset(permitted_development_ids)


def derive_row_policy(
    *,
    dataset: str,
    split: str,
    source_ids: tuple[str, ...] = (),
    permitted_development_ids: frozenset[str] | None = None,
) -> RowPolicy:
    """Derive row access from canonical identifiers and fail closed on mixed IDs."""

    dataset_key = _key(dataset)
    split_key = _key(split)

    if dataset_key in {"synthetic", "illustrative"}:
        if split_key == "syn014" and source_ids and set(source_ids) == {"SYN-014"}:
            return RowPolicy.ILLUSTRATIVE
        return RowPolicy.DENIED

    if dataset_key == "exectv2":
        if split_key == "dev140":
            return (
                RowPolicy.DEVELOPMENT_ROW_LEVEL
                if _ids_are_permitted(source_ids, permitted_development_ids)
                else RowPolicy.DENIED
            )
        if split_key == "full200":
            if permitted_development_ids is not None and _ids_are_permitted(
                source_ids, permitted_development_ids
            ):
                return RowPolicy.DEVELOPMENT_ROW_LEVEL
            return RowPolicy.AGGREGATE_ONLY
        if split_key == "test60":
            return RowPolicy.AGGREGATE_ONLY
        return RowPolicy.DENIED

    if dataset_key in {"gan2026", "gan"}:
        if split_key in {"validation", "validation750", "development", "development750"}:
            return (
                RowPolicy.DEVELOPMENT_ROW_LEVEL
                if _ids_are_permitted(source_ids, permitted_development_ids)
                else RowPolicy.DENIED
            )
        if split_key in {"test", "test450"}:
            return RowPolicy.AGGREGATE_ONLY
        return RowPolicy.DENIED

    return RowPolicy.DENIED
