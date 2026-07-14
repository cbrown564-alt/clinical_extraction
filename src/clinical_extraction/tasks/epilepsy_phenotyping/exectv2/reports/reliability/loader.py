"""Load and validate cross-model reliability runs from catalog.yaml."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.schema import (
    ReliabilityCatalog,
    ReliabilityRunRecord,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.types import (
    ReliabilityRun,
)

DEFAULT_CATALOG_PATH = Path(__file__).with_name("catalog.yaml")


def _load_yaml_mapping(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:  # pragma: no cover - PyYAML is a repo dependency
        raise ValueError(
            f"{path} requires PyYAML for catalog parsing but PyYAML is unavailable"
        ) from exc
    payload = yaml.safe_load(text)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} did not contain a mapping catalog")
    return payload


@lru_cache(maxsize=4)
def _load_catalog(catalog_path: Path = DEFAULT_CATALOG_PATH) -> ReliabilityCatalog:
    resolved = catalog_path.resolve()
    payload = _load_yaml_mapping(resolved)
    return ReliabilityCatalog.model_validate(payload)


def _record_to_run(record: ReliabilityRunRecord) -> ReliabilityRun:
    return ReliabilityRun(
        candidate=record.candidate,
        model_label=record.model_label,
        rows_path=Path(record.rows_path),
        summary_path=Path(record.summary_path) if record.summary_path else None,
        surface_id=record.surface_id,
        role=record.role,
        claim_boundary=record.claim_boundary,
    )


def load_rich_schema_runs(
    catalog_path: Path | None = None,
) -> tuple[ReliabilityRun, ...]:
    """Load rich-schema holistic assembly runs from the catalog."""

    path = catalog_path or DEFAULT_CATALOG_PATH
    catalog = _load_catalog(path)
    return tuple(_record_to_run(record) for record in catalog.rich_schema_runs)
