"""Manifest objects for ExECTv2 clinical finding assembly."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProducerManifest:
    producer_id: str
    kind: str
    artifact: Path
    ownership_label: str
    source_lane: str = ""
    label: str = ""


@dataclass(frozen=True)
class LensManifest:
    entity: str
    producer: str
    lens: str
    source_lane: str = ""
    ownership_label: str = ""
    portability: str | None = None


@dataclass(frozen=True)
class FindingAssemblyManifest:
    candidate_id: str
    split: str
    row_count: int
    claim_boundary: str
    producers: Mapping[str, ProducerManifest]
    lenses: Mapping[str, LensManifest]
    views: tuple[str, ...]
    pipeline_family: str = "exectv2_holistic_finding_assembly"
    ownership: str = "component_attributed_holistic_finding_replay"
    baseline_producer: str = ""
    focused_comparator_artifact: Path | None = None
    promotion_decision: str = "promote-dev-holistic-finding-assembly"

    @property
    def stage(self) -> str:
        return f"{self.split}{self.row_count}"


def load_finding_assembly_manifest(path: Path) -> FindingAssemblyManifest:
    """Load a JSON/YAML finding assembly manifest."""

    payload = _load_payload(path)
    return manifest_from_mapping(payload)


def manifest_from_mapping(payload: Mapping[str, Any]) -> FindingAssemblyManifest:
    producers = {
        str(producer_id): ProducerManifest(
            producer_id=str(producer_id),
            kind=str(config.get("kind", "saved_jsonl")),
            artifact=Path(str(config["artifact"])),
            ownership_label=str(config.get("ownership_label", "")),
            source_lane=str(config.get("source_lane", "")),
            label=str(config.get("label", "")),
        )
        for producer_id, config in _required_mapping(payload, "producers").items()
    }
    lenses = {
        str(entity): LensManifest(
            entity=str(entity),
            producer=str(config["producer"]),
            lens=str(config["lens"]),
            source_lane=str(config.get("source_lane", "")),
            ownership_label=str(
                config.get(
                    "ownership_label",
                    producers[str(config["producer"])].ownership_label,
                )
            ),
            portability=(
                str(config["portability"]) if config.get("portability") is not None else None
            ),
        )
        for entity, config in _required_mapping(payload, "lenses").items()
    }
    comparator = payload.get("focused_comparator_artifact")
    return FindingAssemblyManifest(
        candidate_id=str(payload["candidate_id"]),
        pipeline_family=str(payload.get("pipeline_family", "exectv2_holistic_finding_assembly")),
        ownership=str(payload.get("ownership", "component_attributed_holistic_finding_replay")),
        split=str(payload.get("split", "dev")),
        row_count=int(payload["row_count"]),
        claim_boundary=str(payload.get("claim_boundary", "")),
        producers=producers,
        lenses=lenses,
        views=tuple(str(view) for view in _required_sequence(payload, "views")),
        baseline_producer=str(payload.get("baseline_producer", "")),
        focused_comparator_artifact=Path(str(comparator)) if comparator else None,
        promotion_decision=str(
            payload.get("promotion_decision", "promote-dev-holistic-finding-assembly")
        ),
    )


def _load_payload(path: Path) -> Mapping[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError as exc:  # pragma: no cover - local env has PyYAML via lock
            raise ValueError(
                f"{path} is not JSON and PyYAML is unavailable for YAML parsing"
            ) from exc
        payload = yaml.safe_load(text)
    if not isinstance(payload, Mapping):
        raise ValueError(f"{path} did not contain a mapping manifest")
    return payload


def _required_mapping(payload: Mapping[str, Any], key: str) -> Mapping[str, Mapping[str, Any]]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"manifest field {key!r} must be a mapping")
    return value  # type: ignore[return-value]


def _required_sequence(payload: Mapping[str, Any], key: str) -> Sequence[Any]:
    value = payload.get(key)
    if not isinstance(value, Sequence) or isinstance(value, str):
        raise ValueError(f"manifest field {key!r} must be a sequence")
    return value
