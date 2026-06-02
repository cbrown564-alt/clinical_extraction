from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord

from .graph import build_state_graph


class OracleCoverageSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    row_count: int
    representable_count: int
    representable_rate: float
    by_gold_kind: dict[str, dict[str, int | float]]
    missing_source_row_indices: tuple[int, ...]


def oracle_coverage_summary(records: Sequence[GanFrequencyRecord]) -> OracleCoverageSummary:
    row_count = len(records)
    representable = 0
    by_kind_total: Counter[str] = Counter()
    by_kind_representable: Counter[str] = Counter()
    missing_indices: list[int] = []

    for record in records:
        gold_kind = record.gold_label_kind.value
        by_kind_total[gold_kind] += 1
        graph = build_state_graph(
            record.note_text,
            source_row_index=record.source_row_index,
            include_no_reference_fallback=True,
        )
        if _gold_is_representable(record, graph_node_labels(graph)):
            representable += 1
            by_kind_representable[gold_kind] += 1
        else:
            missing_indices.append(record.source_row_index)

    return OracleCoverageSummary(
        row_count=row_count,
        representable_count=representable,
        representable_rate=_rounded_rate(representable, row_count),
        by_gold_kind={
            kind: {
                "total": by_kind_total[kind],
                "representable": by_kind_representable[kind],
                "representable_rate": _rounded_rate(
                    by_kind_representable[kind],
                    by_kind_total[kind],
                ),
            }
            for kind in sorted(by_kind_total)
        },
        missing_source_row_indices=tuple(missing_indices),
    )


def graph_node_labels(graph) -> tuple[tuple[FrequencyLabelKind, str | None], ...]:
    return tuple((node.semantic_kind, node.normalized_label) for node in graph.nodes)


def _gold_is_representable(
    record: GanFrequencyRecord,
    node_labels: Sequence[tuple[FrequencyLabelKind, str | None]],
) -> bool:
    if record.gold_label_kind in {
        FrequencyLabelKind.UNKNOWN,
        FrequencyLabelKind.NO_REFERENCE,
        FrequencyLabelKind.SEIZURE_FREE,
    }:
        return any(kind is record.gold_label_kind for kind, _label in node_labels)
    return any(label == record.gold_normalized_label for _kind, label in node_labels)


def _rounded_rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0
