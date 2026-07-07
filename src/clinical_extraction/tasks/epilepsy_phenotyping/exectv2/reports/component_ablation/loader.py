"""Load and validate component-ablation replay specs from catalog.yaml."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.schema import (
    ComponentOffDefinitionRecord,
    DefinitionsCatalog,
    LayerDefinitionRecord,
    ReplayCatalog,
    ReplaySpecRecord,
)

if TYPE_CHECKING:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.types import (
        ComponentImpactReplaySpec,
        ComponentOffDefinition,
        LayerDefinition,
    )

DEFAULT_CATALOG_PATH = Path(__file__).with_name("catalog.yaml")
DEFAULT_DEFINITIONS_PATH = Path(__file__).with_name("definitions.yaml")


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


@lru_cache(maxsize=4)
def _load_definitions_catalog(
    definitions_path: Path = DEFAULT_DEFINITIONS_PATH,
) -> DefinitionsCatalog:
    resolved = definitions_path.resolve()
    payload = _load_yaml_mapping(resolved)
    return DefinitionsCatalog.model_validate(payload)


def load_replay_specs(
    catalog_path: Path | None = None,
) -> tuple[ComponentImpactReplaySpec, ...]:
    """Load dev140 replay specs from the catalog."""

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.types import (
        ComponentImpactReplaySpec,
    )

    path = catalog_path or DEFAULT_CATALOG_PATH
    catalog = _load_catalog(path)
    return tuple(_record_to_spec(record, ComponentImpactReplaySpec) for record in catalog.dev140)


def load_full200_specs(
    catalog_path: Path | None = None,
) -> tuple[ComponentImpactReplaySpec, ...]:
    """Load full200 replay specs from the catalog."""

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.types import (
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


def _record_to_layer(record: LayerDefinitionRecord) -> LayerDefinition:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.types import (
        LayerDefinition,
    )

    return LayerDefinition(
        layer_id=record.layer_id,
        label=record.label,
        component_type=record.component_type,
        score_source=record.score_source,
        surface_key=record.surface_key,
        interpretation=record.interpretation,
        inert=record.inert,
    )


def _record_to_component_off(record: ComponentOffDefinitionRecord) -> ComponentOffDefinition:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.types import (
        ComponentOffDefinition,
    )

    return ComponentOffDefinition(
        component_id=record.component_id,
        component_boundary=record.component_boundary,
        component_type=record.component_type,
        component_portability_category=record.component_portability_category,
        prediction_bearing_status=record.prediction_bearing_status,
        baseline_surface=record.baseline_surface,
        component_off_surface=record.component_off_surface,
        scorer_view=record.scorer_view,
        scorer_version=record.scorer_version,
    )


def load_layer_definitions(
    definitions_path: Path | None = None,
) -> tuple[LayerDefinition, ...]:
    """Load the component-impact layer ladder from definitions.yaml."""

    path = definitions_path or DEFAULT_DEFINITIONS_PATH
    catalog = _load_definitions_catalog(path)
    return tuple(_record_to_layer(record) for record in catalog.layers)


def load_component_off_definitions(
    definitions_path: Path | None = None,
) -> tuple[ComponentOffDefinition, ...]:
    """Load one-component-off definitions from definitions.yaml."""

    path = definitions_path or DEFAULT_DEFINITIONS_PATH
    catalog = _load_definitions_catalog(path)
    return tuple(_record_to_component_off(record) for record in catalog.component_off)


def load_full200_component_off_definitions(
    definitions_path: Path | None = None,
) -> tuple[ComponentOffDefinition, ...]:
    """Load the full200 subset of one-component-off definitions."""

    path = definitions_path or DEFAULT_DEFINITIONS_PATH
    catalog = _load_definitions_catalog(path)
    allowed = frozenset(catalog.full200_component_ids)
    return tuple(
        _record_to_component_off(record)
        for record in catalog.component_off
        if record.component_id in allowed
    )
