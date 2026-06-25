"""Self-consistency analysis for ExECTv2 saved assembly repeats.

The analysis is intentionally no-call. It scores family-cell clinical-headline
units across saved assembly JSONL artifacts and reports aggregate stability,
entropy, and correctness curves without emitting row-level failure ledgers.
"""

from __future__ import annotations

import itertools
import json
import math
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    clinical_headline_unit_keys,
)

TARGET_FAMILIES: tuple[str, ...] = (
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY.name,
    PRESCRIPTION.name,
    INVESTIGATIONS.name,
)


def build_self_consistency_report(
    *,
    assembly_jsonl_paths: Sequence[Path],
    producer_jsonl_paths: Mapping[str, Sequence[Path]] | None = None,
    panel_id: str,
    candidate_id: str = "exectv2_gpt41mini_simplification_2call_no_sf_adjudicator",
    model: str = "openai/gpt-4.1-mini",
    temperatures: Sequence[float] = (),
    generated_on: str,
    letters: Sequence[ExectLetter] | None = None,
    claim_boundary: str = "",
) -> dict[str, Any]:
    """Build aggregate self-consistency metrics from saved repeat artifacts."""

    if len(assembly_jsonl_paths) < 2:
        raise ValueError("at least two assembly artifacts are required")

    letters = list(letters or load_letters())
    letter_by_id = {letter.letter_id: letter for letter in letters}
    repeats = [_load_repeat(path, letter_by_id) for path in assembly_jsonl_paths]
    common_ids = sorted(set.intersection(*(set(repeat["cells"]) for repeat in repeats)))
    families = TARGET_FAMILIES
    cells = [(letter_id, family) for letter_id in common_ids for family in families]
    pairwise = _pairwise_metrics(repeats, cells)
    entropy = _entropy_metrics(repeats, cells)
    majority = _majority_correctness(repeats, cells, letter_by_id)
    run_health = [_run_health(repeat) for repeat in repeats]
    producer_variation = _producer_variation(producer_jsonl_paths or {})
    score_summary = [_score_summary(path) for path in assembly_jsonl_paths]

    return {
        "artifact_kind": "exectv2_self_consistency",
        "generated_on": generated_on,
        "panel_id": panel_id,
        "candidate_id": candidate_id,
        "model": model,
        "temperatures": [float(t) for t in temperatures],
        "repeat_count": len(repeats),
        "rows": len(common_ids),
        "family_cell_count": len(cells),
        "families": list(families),
        "claim_boundary": claim_boundary
        or (
            "Aggregate-only self-consistency readout for saved live repeats of "
            "the selected GPT-4.1-mini 2-call no-SF-adjudicator ExECTv2 candidate."
        ),
        "row_inspection_policy": "aggregate_only_no_failure_ledger",
        "assembly_artifacts": [path.as_posix() for path in assembly_jsonl_paths],
        "producer_artifacts": {
            key: [path.as_posix() for path in paths]
            for key, paths in (producer_jsonl_paths or {}).items()
        },
        "run_health": run_health,
        "score_summary": score_summary,
        "pairwise_agreement": pairwise,
        "semantic_entropy": entropy,
        "majority_correctness": majority,
        "producer_raw_output_variation": producer_variation,
        "interpretation": _interpretation(pairwise, entropy, majority, producer_variation),
    }


def write_self_consistency_artifacts(
    payload: Mapping[str, Any],
    *,
    json_path: Path,
    markdown_path: Path,
) -> dict[str, Path]:
    """Write JSON and Markdown self-consistency readouts."""

    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_self_consistency_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}


def render_self_consistency_markdown(payload: Mapping[str, Any]) -> str:
    """Render a compact paper-facing self-consistency report."""

    pairwise = payload["pairwise_agreement"]
    entropy = payload["semantic_entropy"]
    majority = payload["majority_correctness"]
    temperature_note = _temperature_note(payload.get("temperatures", ()))
    lines = [
        "# ExECTv2 2-Call GPT-4.1-Mini Self-Consistency",
        "",
        f"- Generated: `{payload['generated_on']}`",
        f"- Panel: `{payload['panel_id']}`",
        f"- Candidate: `{payload['candidate_id']}`",
        f"- Model: `{payload['model']}`",
        f"- Temperatures: `{', '.join(str(t) for t in payload['temperatures'])}`",
        f"- Repeats: `{payload['repeat_count']}`",
        f"- Rows: `{payload['rows']}`",
        f"- Family cells: `{payload['family_cell_count']}`",
        f"- Row inspection policy: `{payload['row_inspection_policy']}`",
        f"- Claim boundary: {payload['claim_boundary']}",
        "",
        temperature_note,
        "",
        "## Agreement And Entropy",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Pairwise comparisons | {pairwise['pairwise_comparisons']} |",
        f"| Exact family-cell agreement | {pairwise['exact_family_cell_agreement_rate']:.4f} |",
        f"| Mean pairwise Jaccard | {pairwise['mean_pairwise_jaccard']:.4f} |",
        f"| Mean semantic entropy | {entropy['mean_entropy']:.4f} |",
        f"| Non-zero entropy cells | {entropy['nonzero_entropy_cells']} |",
        "",
        "## Per-Family Stability",
        "",
        "| Family | Exact agreement | Mean Jaccard | Mean entropy | Non-zero entropy cells |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    entropy_by_family = {
        row["family"]: row for row in entropy["by_family"]
    }
    for row in pairwise["by_family"]:
        family_entropy = entropy_by_family[row["family"]]
        lines.append(
            f"| {row['family']} | {row['exact_family_cell_agreement_rate']:.4f} | "
            f"{row['mean_pairwise_jaccard']:.4f} | "
            f"{family_entropy['mean_entropy']:.4f} | "
            f"{family_entropy['nonzero_entropy_cells']} |"
        )

    lines.extend(
        [
            "",
            "## Majority Agreement Correctness",
            "",
            "| Majority top/k | Cells | Exact-correct majority | Accuracy |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for row in majority["agreement_accuracy_curve"]:
        lines.append(
            f"| {row['majority_top_k']} | {row['cells']} | "
            f"{row['correct_majority_cells']} | {row['accuracy']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Run Health",
            "",
            "| Artifact | Rows | Call failures | Parse/schema failures | Evidence validity |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in payload["run_health"]:
        lines.append(
            f"| `{row['artifact']}` | {row['rows']} | {row['call_failures']} | "
            f"{row['parse_schema_failures']} | {row['evidence_validity_rate']:.4f} |"
        )

    if payload.get("producer_raw_output_variation"):
        lines.extend(
            [
                "",
                "## Producer Raw-Output Variation",
                "",
                "| Producer | Rows compared | Mean unique raw outputs / row | Rows with variation |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for row in payload["producer_raw_output_variation"].values():
            lines.append(
                f"| {row['producer']} | {row['rows_compared']} | "
                f"{row['mean_unique_raw_outputs_per_row']:.4f} | "
                f"{row['rows_with_raw_output_variation']} |"
            )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            payload["interpretation"],
            "",
            "## Artifacts",
            "",
        ]
    )
    for artifact in payload["assembly_artifacts"]:
        lines.append(f"- Assembly JSONL: `{artifact}`")
    for producer, artifacts in payload.get("producer_artifacts", {}).items():
        for artifact in artifacts:
            lines.append(f"- {producer}: `{artifact}`")
    return "\n".join(lines) + "\n"


def _temperature_note(temperatures: Sequence[Any]) -> str:
    unique_temperatures = {float(t) for t in temperatures}
    if len(unique_temperatures) == 1:
        temperature = next(iter(unique_temperatures))
        return (
            f"> **Temperature caveat.** All repeats use temperature `{temperature:g}`, so this "
            "panel measures reproducibility/decision stability under repeated live calls, not "
            "varying-temperature semantic self-consistency. The varying-temperature entropy panel "
            "is the direct ExECTv2 analogue of Gan P2.1."
        )
    return (
        "> **Temperature panel.** Repeats use varying temperatures, so entropy and agreement "
        "measure semantic stability under sampled live calls rather than temp-0 reproducibility."
    )


def _load_repeat(path: Path, letter_by_id: Mapping[str, ExectLetter]) -> dict[str, Any]:
    rows = _read_jsonl(path)
    cells: dict[str, dict[str, tuple[str, ...]]] = {}
    for row in rows:
        letter_id = str(row["letter_id"])
        note_text = letter_by_id.get(letter_id, ExectLetter(letter_id, "", ())).note_text
        mentions = [_annotation(m) for m in row.get("predicted_mentions", [])]
        by_family: dict[str, list[ExectAnnotation]] = {family: [] for family in TARGET_FAMILIES}
        for mention in mentions:
            if mention.entity in by_family:
                by_family[mention.entity].append(mention)
        cells[letter_id] = {
            family: _keyset(family, by_family[family], note_text)
            for family in TARGET_FAMILIES
        }
    return {"path": path, "rows": rows, "cells": cells}


def _pairwise_metrics(
    repeats: Sequence[Mapping[str, Any]],
    cells: Sequence[tuple[str, str]],
) -> dict[str, Any]:
    family_counts: dict[str, Counter[str]] = defaultdict(Counter)
    jaccards: list[float] = []
    exact = total = pairwise = 0
    for left, right in itertools.combinations(repeats, 2):
        pairwise += 1
        for letter_id, family in cells:
            left_keys = set(left["cells"][letter_id][family])
            right_keys = set(right["cells"][letter_id][family])
            total += 1
            family_counts[family]["cells"] += 1
            value = _jaccard(left_keys, right_keys)
            jaccards.append(value)
            family_counts[family]["jaccard_sum"] += value
            if left_keys == right_keys:
                exact += 1
                family_counts[family]["exact"] += 1
    return {
        "pairwise_comparisons": pairwise,
        "cell_count": total,
        "exact_family_cell_agreement_rate": _rate(exact, total),
        "mean_pairwise_jaccard": round(sum(jaccards) / len(jaccards), 4) if jaccards else 0.0,
        "by_family": [
            {
                "family": family,
                "cell_count": int(family_counts[family]["cells"]),
                "exact_family_cell_agreement_rate": _rate(
                    int(family_counts[family]["exact"]),
                    int(family_counts[family]["cells"]),
                ),
                "mean_pairwise_jaccard": round(
                    float(family_counts[family]["jaccard_sum"])
                    / int(family_counts[family]["cells"]),
                    4,
                )
                if family_counts[family]["cells"]
                else 0.0,
            }
            for family in TARGET_FAMILIES
        ],
    }


def _entropy_metrics(
    repeats: Sequence[Mapping[str, Any]],
    cells: Sequence[tuple[str, str]],
) -> dict[str, Any]:
    by_family: dict[str, list[float]] = defaultdict(list)
    values: list[float] = []
    for letter_id, family in cells:
        counts = Counter(repeat["cells"][letter_id][family] for repeat in repeats)
        entropy = _entropy(counts.values())
        values.append(entropy)
        by_family[family].append(entropy)
    return {
        "mean_entropy": round(sum(values) / len(values), 4) if values else 0.0,
        "nonzero_entropy_cells": sum(value > 0 for value in values),
        "by_family": [
            {
                "family": family,
                "cell_count": len(by_family[family]),
                "mean_entropy": round(
                    sum(by_family[family]) / len(by_family[family]), 4
                )
                if by_family[family]
                else 0.0,
                "nonzero_entropy_cells": sum(value > 0 for value in by_family[family]),
            }
            for family in TARGET_FAMILIES
        ],
    }


def _majority_correctness(
    repeats: Sequence[Mapping[str, Any]],
    cells: Sequence[tuple[str, str]],
    letter_by_id: Mapping[str, ExectLetter],
) -> dict[str, Any]:
    buckets: dict[str, Counter[str]] = defaultdict(Counter)
    for letter_id, family in cells:
        counts = Counter(repeat["cells"][letter_id][family] for repeat in repeats)
        majority_keys, top_count = counts.most_common(1)[0]
        gold = _gold_keyset(letter_by_id[letter_id], family)
        bucket = f"{top_count}/{len(repeats)}"
        buckets[bucket]["cells"] += 1
        if tuple(majority_keys) == gold:
            buckets[bucket]["correct"] += 1
    rows = []
    for bucket in sorted(buckets, key=lambda item: (-int(item.split("/")[0]), item)):
        cells_n = int(buckets[bucket]["cells"])
        correct = int(buckets[bucket]["correct"])
        rows.append(
            {
                "majority_top_k": bucket,
                "cells": cells_n,
                "correct_majority_cells": correct,
                "accuracy": _rate(correct, cells_n),
            }
        )
    return {"agreement_accuracy_curve": rows}


def _run_health(repeat: Mapping[str, Any]) -> dict[str, Any]:
    rows = repeat["rows"]
    lane_diagnostics = _load_summary_for_jsonl(repeat["path"]).get("lane_diagnostics", {})
    if lane_diagnostics:
        call_failures = sum(int(v.get("call_failures", 0)) for v in lane_diagnostics.values())
        parse_failures = sum(
            int(v.get("parse_schema_failures", 0)) for v in lane_diagnostics.values()
        )
        raw = sum(int(v.get("raw_mentions", 0)) for v in lane_diagnostics.values())
        invalid = sum(int(v.get("evidence_invalid_dropped", 0)) for v in lane_diagnostics.values())
    else:
        call_failures = sum(bool(row.get("call_error")) for row in rows)
        parse_failures = sum(bool(row.get("parse_errors")) for row in rows)
        raw = sum(len(row.get("raw_lane_mentions", [])) for row in rows)
        invalid = 0
    return {
        "artifact": repeat["path"].as_posix(),
        "rows": len(rows),
        "call_failures": call_failures,
        "parse_schema_failures": parse_failures,
        "raw_mentions": raw,
        "evidence_invalid_mentions": invalid,
        "evidence_validity_rate": _rate(raw - invalid, raw) if raw else 1.0,
    }


def _score_summary(path: Path) -> dict[str, Any]:
    report = _load_summary_for_jsonl(path)
    headline = report.get("score_ladder", {}).get("headline_target", {})
    return {
        "artifact": path.as_posix(),
        "overall": dict(headline.get("overall", {})),
        "by_indicator": dict(headline.get("by_indicator", {})),
    }


def _producer_variation(
    producer_jsonl_paths: Mapping[str, Sequence[Path]],
) -> dict[str, dict[str, Any]]:
    result = {}
    for producer, paths in producer_jsonl_paths.items():
        if len(paths) < 2:
            continue
        rows_by_path = [_read_jsonl(path) for path in paths]
        common_ids = sorted(
            set.intersection(*({str(row["letter_id"]) for row in rows} for rows in rows_by_path))
        )
        unique_counts = []
        varied = 0
        for letter_id in common_ids:
            outputs = {
                str(next(row for row in rows if str(row["letter_id"]) == letter_id).get("raw_output", ""))
                for rows in rows_by_path
            }
            unique_counts.append(len(outputs))
            if len(outputs) > 1:
                varied += 1
        result[producer] = {
            "producer": producer,
            "rows_compared": len(common_ids),
            "mean_unique_raw_outputs_per_row": round(
                sum(unique_counts) / len(unique_counts), 4
            )
            if unique_counts
            else 0.0,
            "rows_with_raw_output_variation": varied,
        }
    return result


def _interpretation(
    pairwise: Mapping[str, Any],
    entropy: Mapping[str, Any],
    majority: Mapping[str, Any],
    producer_variation: Mapping[str, Any],
) -> str:
    exact = float(pairwise["exact_family_cell_agreement_rate"])
    mean_entropy = float(entropy["mean_entropy"])
    curve = majority["agreement_accuracy_curve"]
    top = curve[0] if curve else {"majority_top_k": "n/a", "accuracy": 0.0}
    raw_varied = any(
        int(row.get("rows_with_raw_output_variation", 0)) > 0
        for row in producer_variation.values()
    )
    raw_clause = (
        "Raw producer outputs vary across repeats, so stable clinical-headline cells "
        "should be read as decision stability rather than cache reuse."
        if raw_varied
        else "Raw-output variation was not demonstrated in the supplied producer artifacts."
    )
    return (
        f"Exact family-cell agreement is {exact:.4f} with mean semantic entropy "
        f"{mean_entropy:.4f}. The strongest agreement bucket is "
        f"{top['majority_top_k']} with correctness {top['accuracy']:.4f}. "
        f"{raw_clause} Interpret high agreement as reliability only where the "
        "majority-correctness curve also stays high; unanimous-but-wrong cells are "
        "the ExECTv2 analogue of Gan's confident residual."
    )


def _gold_keyset(letter: ExectLetter, family: str) -> tuple[str, ...]:
    return _keyset(family, letter.entities(family), letter.note_text)


def _keyset(
    family: str,
    annotations: Sequence[ExectAnnotation],
    note_text: str,
) -> tuple[str, ...]:
    keys = clinical_headline_unit_keys(family, annotations, note_text)
    return tuple(sorted(_stable_key(key) for key in keys))


def _stable_key(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=True)
    except TypeError:
        return repr(value)


def _annotation(payload: Mapping[str, Any]) -> ExectAnnotation:
    return ExectAnnotation(
        entity=str(payload.get("entity", "")),
        text=str(payload.get("text", "")),
        attributes={
            str(key): str(value)
            for key, value in (payload.get("attributes") or {}).items()
            if value is not None
        },
    )


def _load_summary_for_jsonl(path: Path) -> dict[str, Any]:
    json_path = path.with_suffix(".json")
    if json_path.exists():
        return json.loads(json_path.read_text(encoding="utf-8"))
    return {}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    return len(left & right) / len(left | right)


def _entropy(counts: Sequence[int]) -> float:
    total = sum(counts)
    if total <= 0:
        return 0.0
    value = 0.0
    for count in counts:
        p = count / total
        value -= p * math.log2(p)
    return value


def _rate(num: int | float, den: int | float) -> float:
    return round(float(num) / float(den), 4) if den else 0.0
