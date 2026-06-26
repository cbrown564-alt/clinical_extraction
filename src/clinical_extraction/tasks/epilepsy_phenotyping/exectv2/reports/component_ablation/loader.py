"""Load and validate component-ablation replay specs from catalog.yaml."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.schema import (
    ReplayCatalog,
    ReplaySpecRecord,
)

if TYPE_CHECKING:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation_replay import (
        ComponentImpactReplaySpec,
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
def _load_catalog(catalog_path: Path = DEFAULT_CATALOG_PATH) -> ReplayCatalog:
    resolved = catalog_path.resolve()
    payload = _load_yaml_mapping(resolved)
    return ReplayCatalog.model_validate(payload)


def load_replay_specs(
    catalog_path: Path | None = None,
) -> tuple[ComponentImpactReplaySpec, ...]:
    """Load dev140 replay specs from the catalog."""

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation_replay import (
        ComponentImpactReplaySpec,
    )

    path = catalog_path or DEFAULT_CATALOG_PATH
    catalog = _load_catalog(path)
    return tuple(_record_to_spec(record, ComponentImpactReplaySpec) for record in catalog.dev140)


def load_full200_specs(
    catalog_path: Path | None = None,
) -> tuple[ComponentImpactReplaySpec, ...]:
    """Load full200 replay specs from the catalog."""

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation_replay import (
        ComponentImpactReplaySpec,
    )

    path = catalog_path or DEFAULT_CATALOG_PATH
    catalog = _load_catalog(path)
    return tuple(_record_to_spec(record, ComponentImpactReplaySpec) for record in catalog.full200)


def _record_to_spec(
    record: ReplaySpecRecord,
    spec_cls: type[ComponentImpactReplaySpec],
) -> ComponentImpactReplaySpec:
    return spec_cls(
        run_id=record.run_id,
        label=record.label,
        source_summary_path=Path(record.source_summary_path),
        source_jsonl_path=Path(record.source_jsonl_path),
        model=record.model,
        decision=record.decision,
        architecture_family=record.architecture_family,
        split=record.split,
        row_count=record.row_count,
    )
