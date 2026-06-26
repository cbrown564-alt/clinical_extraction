"""Registry row selection for MLflow backfill scopes."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import date

from clinical_extraction.core.mlflow_sync_types import BACKFILL_SCOPES, BackfillScope, BackfillScopeName
from clinical_extraction.core.registry import REGISTRY_ROLES, RegistryRole, RunRegistryEntry


def resolve_backfill_filters(
    *,
    backfill_scope: BackfillScopeName | None = None,
    since_date: str | None = None,
    registry_roles: Iterable[RegistryRole] = (),
) -> tuple[BackfillScope | None, str | None, frozenset[RegistryRole] | None]:
    """Resolve operator scope presets into concrete sync filters."""

    scope = BACKFILL_SCOPES[backfill_scope] if backfill_scope is not None else None
    resolved_since_date = since_date if since_date is not None else (
        scope.since_date if scope is not None else None
    )
    role_list = tuple(registry_roles)
    if role_list:
        unknown = sorted(set(role_list) - set(REGISTRY_ROLES))
        if unknown:
            allowed = ", ".join(sorted(REGISTRY_ROLES))
            raise ValueError(
                f"unknown registry role(s): {', '.join(unknown)}; allowed: {allowed}"
            )
        resolved_roles = frozenset(role_list)
    elif scope is not None and scope.registry_roles is not None:
        resolved_roles = scope.registry_roles
    else:
        resolved_roles = None
    return scope, resolved_since_date, resolved_roles


def filter_registry_entries(
    entries: Sequence[RunRegistryEntry],
    *,
    since_date: str | None = None,
    run_ids: Iterable[str] = (),
    registry_roles: frozenset[RegistryRole] | None = None,
) -> list[RunRegistryEntry]:
    """Return registry entries selected by run id, date, and/or registry role."""

    run_id_set = set(run_ids)
    threshold = parse_since_date(since_date)
    selected: list[RunRegistryEntry] = []
    for entry in entries:
        if run_id_set and entry.run_id not in run_id_set:
            continue
        if threshold is not None and date.fromisoformat(entry.date) < threshold:
            continue
        if registry_roles is not None:
            entry_roles = frozenset(entry.registry_roles)
            if not entry_roles.intersection(registry_roles):
                continue
        selected.append(entry)
    return selected


def parse_since_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("--since-date must use YYYY-MM-DD format") from exc
