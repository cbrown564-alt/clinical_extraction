"""Build the SF v0.8 hard-slice residual diagnostic panel.

This is a dev140-only offline analysis of the v0.7 SeizureFrequency residual
ledger. It does not alter predictions. The panel separates state, ownership,
benchmark-format, context-span, and true candidate-gap residuals before any
prediction-bearing SF v0.8 rule is proposed.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

DEFAULT_LEDGER_JSON = Path(
    "experiments/exectv2_key_entities_clinical_error_ledger_v07sf_dev140_20260618.json"
)
DEFAULT_SOURCE_JSONL = Path(
    "experiments/exectv2_hybrid_sf_unknown_suppression_v07_dev140_20260618.jsonl"
)
OUT_JSON = Path("experiments/exectv2_sf_v08_hard_slice_panel_dev140_20260618.json")
OUT_MD = Path("experiments/exectv2_sf_v08_hard_slice_panel_dev140_20260618.md")

SF_ENTITY = "SeizureFrequency"
SF_STATES = {"active-rate", "seizure-free", "unknown"}
GENERIC_CUIS = {"C0036572"}
SEIZURE_FREE_CUIS = {"C1299590"}
GENERIC_PHRASES = {"seizure", "seizures"}
SEIZURE_FREE_PHRASES = {"seizure free", "seizure-free"}

CONTEXT_RE = re.compile(
    r"\b("
    r"diagnosis|syndrome|semiology|family history|no history of|risk of|"
    r"driving|advice|if\s+\w+|should\s+there|medication|drug|dose|"
    r"lamotrigine|carbamazepine|valproate|levetiracetam|stable|"
    r"well controlled|previously|in the past|photosensitive|photosensitivity"
    r")\b",
    re.IGNORECASE,
)


def read_ledger(path: Path = DEFAULT_LEDGER_JSON) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_rows(path: Path = DEFAULT_SOURCE_JSONL) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def build_panel(
    ledger: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    *,
    ledger_json: Path = DEFAULT_LEDGER_JSON,
    source_jsonl: Path = DEFAULT_SOURCE_JSONL,
) -> dict[str, Any]:
    row_by_id = {str(row["letter_id"]): row for row in rows}
    residual_records = [
        record for record in ledger.get("records", []) if str(record.get("entity", "")) == SF_ENTITY
    ]
    by_letter = _records_by_letter(residual_records)
    panel = [
        _panel_entry(record, by_letter[str(record["letter_id"])], row_by_id)
        for record in residual_records
    ]

    return {
        "generated": "2026-06-18",
        "split": str(ledger.get("split", "dev")),
        "scope": "dev140 SF v0.7 residual hard-slice diagnostic only",
        "claim_language": {
            "supported": (
                "The v0.8 work completed a pre-change dev140 residual panel "
                "that separates clinical SF state/ownership failures from "
                "benchmark-format convention and context-span residuals."
            ),
            "not_supported": (
                "The panel does not show that v0.8 improves SeizureFrequency "
                "and does not authorize a prediction-bearing SF rule."
            ),
        },
        "source_ledger_json": str(ledger_json),
        "source_jsonl": str(source_jsonl),
        "row_count": len(rows),
        "residual_record_count": len(panel),
        "residual_unit_count": sum(int(item["count"]) for item in panel),
        "bucket_counts_by_side_state": _bucket_counts_by_side_state(panel),
        "bucket_counts_by_type_family": _bucket_counts_by_type_family(panel),
        "top_letter_pair_patterns": _top_letter_pair_patterns(panel),
        "possible_fix_counts_by_action_class": _possible_fix_counts(panel),
        "candidate_lane_counts_by_bucket": _candidate_lane_counts(panel),
        "panel": panel,
    }


def write_artifacts(
    diagnostic: Mapping[str, Any],
    *,
    out_json: Path = OUT_JSON,
    out_md: Path = OUT_MD,
) -> tuple[Path, Path]:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(diagnostic, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(_render_markdown(diagnostic, json_path=out_json), encoding="utf-8")
    return out_json, out_md


def _panel_entry(
    record: Mapping[str, Any],
    letter_records: Sequence[Mapping[str, Any]],
    row_by_id: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    letter_id = str(record["letter_id"])
    side = _side(record)
    key_type, state = _parse_sf_key(str(record["key"]))
    opposite = [item for item in letter_records if _side(item) != side]
    row = row_by_id.get(letter_id, {})
    candidates = _matching_candidates(row.get("candidate_spans", []), key_type, state, record)
    bucket = _bucket(record, key_type, state, opposite, candidates)

    return {
        "letter_id": letter_id,
        "side": side,
        "count": int(record.get("count", 1)),
        "state": state,
        "type_key": key_type,
        "type_family": _type_family(key_type),
        "bucket": bucket,
        "possible_action_class": _action_class(bucket, side, candidates),
        "portability_category": _portability_category(bucket),
        "candidate_span_available": bool(candidates),
        "candidate_lanes": sorted({str(item.get("decision_lane", "")) for item in candidates}),
        "candidate_types": sorted({str(item.get("candidate_type", "")) for item in candidates}),
        "evidence": str(record.get("evidence", "")),
        "text": str(record.get("example_text", "")),
        "attributes": {
            str(k): str(v) for k, v in dict(record.get("example_attributes") or {}).items()
        },
        "opposite_summary": _opposite_summary(opposite),
        "pair_pattern": _pair_pattern(letter_records),
        "secondary_tags": _secondary_tags(record, key_type, state, opposite, candidates),
    }


def _records_by_letter(
    records: Iterable[Mapping[str, Any]],
) -> dict[str, list[Mapping[str, Any]]]:
    out: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for record in records:
        out[str(record["letter_id"])].append(record)
    return out


def _side(record: Mapping[str, Any]) -> str:
    side = str(record.get("side", ""))
    if side not in {"gold", "predicted"}:
        raise ValueError(f"Unsupported residual side: {side!r}")
    return side


def _parse_sf_key(key: str) -> tuple[Any, str]:
    value = json.loads(key)
    if not isinstance(value, list) or len(value) != 2 or str(value[1]) not in SF_STATES:
        raise ValueError(f"Unsupported SeizureFrequency key: {key!r}")
    return value[0], str(value[1])


def _bucket(
    record: Mapping[str, Any],
    key_type: Any,
    state: str,
    opposite: Sequence[Mapping[str, Any]],
    candidates: Sequence[Mapping[str, Any]],
) -> str:
    if _has_seizure_free_convention_pair(key_type, state, opposite):
        return "seizure_free_cui_convention"
    if _has_state_swap(key_type, state, opposite):
        return "state_swap"
    if _is_context_span(record):
        return "diagnosis_context_span"
    if _has_generic_named_pair(key_type, state, opposite):
        return "generic_named_ownership"
    if _side(record) == "gold" and not opposite and not candidates:
        return "true_candidate_gap"
    if _side(record) == "gold" and not _has_actionable_candidate(candidates):
        return "true_candidate_gap"
    return "other_or_ambiguous"


def _has_seizure_free_convention_pair(
    key_type: Any,
    state: str,
    opposite: Sequence[Mapping[str, Any]],
) -> bool:
    if state != "seizure-free" or not _is_seizure_free_convention_type(key_type):
        return False
    for item in opposite:
        other_type, other_state = _parse_sf_key(str(item["key"]))
        if other_state == "seizure-free" and _is_seizure_free_convention_type(other_type):
            return True
    return False


def _has_state_swap(
    key_type: Any,
    state: str,
    opposite: Sequence[Mapping[str, Any]],
) -> bool:
    for item in opposite:
        other_type, other_state = _parse_sf_key(str(item["key"]))
        if other_state == state:
            continue
        if _same_type(key_type, other_type) or _same_anchor_family(key_type, other_type):
            return True
    return False


def _has_generic_named_pair(
    key_type: Any,
    state: str,
    opposite: Sequence[Mapping[str, Any]],
) -> bool:
    for item in opposite:
        other_type, other_state = _parse_sf_key(str(item["key"]))
        if other_state == state and _generic_named_disagreement(key_type, other_type):
            return True
    return False


def _is_context_span(record: Mapping[str, Any]) -> bool:
    text = " ".join(
        str(record.get(field, "")) for field in ("evidence", "example_text", "note_excerpt")
    )
    return bool(CONTEXT_RE.search(text))


def _matching_candidates(
    candidates: Iterable[Mapping[str, Any]],
    key_type: Any,
    state: str,
    record: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    out = []
    evidence = _norm(str(record.get("evidence", "")))
    text = _norm(str(record.get("example_text", "")))
    want_generic = _is_generic_type(key_type)
    want_seizure_free = _is_seizure_free_type(key_type)
    for candidate in candidates:
        state_hint = str(candidate.get("state_hint", ""))
        lane = str(candidate.get("decision_lane", ""))
        hint = _norm(str(candidate.get("text_hint", "")))
        candidate_evidence = _norm(str(candidate.get("evidence", "")))
        state_match = state_hint == state or _lane_matches_state(lane, state)
        evidence_match = bool(
            evidence
            and candidate_evidence
            and (evidence in candidate_evidence or candidate_evidence in evidence)
        )
        text_match = bool(text and hint and (text in hint or hint in text))
        type_match = _generic_phrase(hint) == want_generic or (
            _seizure_free_phrase(hint) and want_seizure_free
        )
        if state_match and (evidence_match or text_match or type_match):
            out.append(candidate)
    return out


def _lane_matches_state(lane: str, state: str) -> bool:
    return (lane, state) in {
        ("active_rate", "active-rate"),
        ("seizure_free", "seizure-free"),
        ("qualitative_change", "unknown"),
    }


def _has_actionable_candidate(candidates: Sequence[Mapping[str, Any]]) -> bool:
    return any(str(candidate.get("decision_lane", "")) != "reject" for candidate in candidates)


def _type_family(key_type: Any) -> str:
    if _is_generic_type(key_type):
        return "generic_seizure"
    if _is_seizure_free_type(key_type):
        return "seizure_free_concept"
    if isinstance(key_type, list) and key_type and key_type[0] == "cui":
        return "named_cui"
    if isinstance(key_type, list) and key_type and key_type[0] == "phrase":
        return "phrase"
    return "other"


def _is_seizure_free_convention_type(key_type: Any) -> bool:
    return _is_generic_type(key_type) or _is_seizure_free_type(key_type)


def _is_generic_type(key_type: Any) -> bool:
    if not isinstance(key_type, list) or len(key_type) != 2:
        return False
    kind = str(key_type[0])
    raw_value = str(key_type[1])
    value = _norm(raw_value)
    return (
        (kind == "cui" and value in GENERIC_CUIS)
        or (kind == "cui" and raw_value.upper() in GENERIC_CUIS)
        or (kind == "phrase" and value in GENERIC_PHRASES)
    )


def _is_seizure_free_type(key_type: Any) -> bool:
    if not isinstance(key_type, list) or len(key_type) != 2:
        return False
    kind = str(key_type[0])
    raw_value = str(key_type[1])
    value = _norm(raw_value)
    return (
        (kind == "cui" and value in SEIZURE_FREE_CUIS)
        or (kind == "cui" and raw_value.upper() in SEIZURE_FREE_CUIS)
        or (kind == "phrase" and value in SEIZURE_FREE_PHRASES)
    )


def _same_type(left: Any, right: Any) -> bool:
    return _json_key(left) == _json_key(right)


def _same_anchor_family(left: Any, right: Any) -> bool:
    if _same_type(left, right):
        return True
    if _is_seizure_free_convention_type(left) and _is_seizure_free_convention_type(right):
        return True
    return _type_family(left) == _type_family(right) == "named_cui"


def _generic_named_disagreement(left: Any, right: Any) -> bool:
    return _is_generic_type(left) != _is_generic_type(right)


def _json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def _generic_phrase(value: str) -> bool:
    return _norm(value) in GENERIC_PHRASES


def _seizure_free_phrase(value: str) -> bool:
    return _norm(value) in SEIZURE_FREE_PHRASES


def _norm(value: str) -> str:
    return " ".join(value.lower().replace("-", " ").split())


def _action_class(
    bucket: str,
    side: str,
    candidates: Sequence[Mapping[str, Any]],
) -> str:
    if bucket == "generic_named_ownership":
        return "repair_ownership"
    if bucket == "state_swap":
        return "repair_state"
    if bucket == "seizure_free_cui_convention":
        return "repair_benchmark_format"
    if bucket == "diagnosis_context_span" and side == "predicted":
        return "drop"
    if bucket == "other_or_ambiguous" and side == "gold" and _has_actionable_candidate(candidates):
        return "add"
    return "no_action"


def _portability_category(bucket: str) -> str:
    return {
        "generic_named_ownership": "seizure_frequency",
        "state_swap": "seizure_frequency",
        "seizure_free_cui_convention": "benchmark_format",
        "diagnosis_context_span": "seizure_frequency",
        "true_candidate_gap": "no_action",
        "other_or_ambiguous": "no_action",
    }[bucket]


def _secondary_tags(
    record: Mapping[str, Any],
    key_type: Any,
    state: str,
    opposite: Sequence[Mapping[str, Any]],
    candidates: Sequence[Mapping[str, Any]],
) -> list[str]:
    tags = []
    if _is_context_span(record):
        tags.append("context_cue_present")
    if _has_state_swap(key_type, state, opposite):
        tags.append("state_swap_candidate")
    if _has_generic_named_pair(key_type, state, opposite):
        tags.append("ownership_pair_present")
    if candidates:
        tags.append("candidate_span_available")
    return tags


def _opposite_summary(opposite: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    out = []
    for item in opposite[:6]:
        key_type, state = _parse_sf_key(str(item["key"]))
        out.append(
            {
                "side": _side(item),
                "state": state,
                "type_family": _type_family(key_type),
                "key": str(item["key"]),
                "evidence": str(item.get("evidence", "")),
            }
        )
    return out


def _pair_pattern(records: Sequence[Mapping[str, Any]]) -> str:
    by_side: dict[str, Counter[str]] = {"gold": Counter(), "predicted": Counter()}
    for record in records:
        _key_type, state = _parse_sf_key(str(record["key"]))
        by_side[_side(record)][state] += int(record.get("count", 1))
    parts = []
    for side in ("gold", "predicted"):
        if by_side[side]:
            states = "+".join(state for state, _count in sorted(by_side[side].items()))
            parts.append(f"{side}:{states}")
    return " -> ".join(parts) if parts else "unpaired"


def _bucket_counts_by_side_state(
    panel: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, int]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for item in panel:
        counts[str(item["bucket"])][f"{item['side']}/{item['state']}"] += int(item["count"])
    return {bucket: dict(values) for bucket, values in sorted(counts.items())}


def _bucket_counts_by_type_family(
    panel: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, int]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for item in panel:
        counts[str(item["bucket"])][str(item["type_family"])] += int(item["count"])
    return {bucket: dict(values) for bucket, values in sorted(counts.items())}


def _top_letter_pair_patterns(panel: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    letters: dict[str, set[str]] = defaultdict(set)
    for item in panel:
        pattern = str(item["pair_pattern"])
        counts[pattern] += int(item["count"])
        letters[pattern].add(str(item["letter_id"]))
    return [
        {
            "pattern": pattern,
            "count": count,
            "letters": sorted(letters[pattern])[:12],
        }
        for pattern, count in counts.most_common(20)
    ]


def _possible_fix_counts(panel: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts = Counter()
    for item in panel:
        counts[str(item["possible_action_class"])] += int(item["count"])
    return dict(sorted(counts.items()))


def _candidate_lane_counts(panel: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for item in panel:
        lanes = item.get("candidate_lanes") or ["none"]
        for lane in lanes:
            counts[str(item["bucket"])][str(lane or "none")] += int(item["count"])
    return {bucket: dict(values) for bucket, values in sorted(counts.items())}


def _render_markdown(diagnostic: Mapping[str, Any], *, json_path: Path) -> str:
    lines = [
        "# ExECTv2 SF v0.8 Hard-Slice Panel",
        "",
        f"- Generated: `{diagnostic['generated']}`",
        f"- Split: `{diagnostic['split']}`",
        f"- Scope: {diagnostic['scope']}",
        f"- JSON: `{json_path}`",
        f"- Source ledger: `{diagnostic['source_ledger_json']}`",
        f"- Source JSONL: `{diagnostic['source_jsonl']}`",
        f"- Rows: {diagnostic['row_count']}",
        f"- Residual records: {diagnostic['residual_record_count']}",
        f"- Residual units: {diagnostic['residual_unit_count']}",
        "",
        "## Bucket Counts By Side And State",
        "",
        "| Bucket | Side/State | Count |",
        "| --- | --- | ---: |",
    ]
    for bucket, values in diagnostic["bucket_counts_by_side_state"].items():
        for side_state, count in sorted(values.items()):
            lines.append(f"| `{bucket}` | {side_state} | {count} |")

    lines.extend(["", "## Bucket Counts By Type Family", ""])
    lines.extend(_nested_count_table(diagnostic["bucket_counts_by_type_family"], "Type family"))
    lines.extend(["", "## Possible Fix Counts", ""])
    lines.extend(_flat_count_table(diagnostic["possible_fix_counts_by_action_class"], "Action"))
    lines.extend(["", "## Candidate Lanes By Bucket", ""])
    lines.extend(_nested_count_table(diagnostic["candidate_lane_counts_by_bucket"], "Lane"))
    lines.extend(["", "## Top Letter Pair Patterns", ""])
    lines.extend(
        [
            "| Pattern | Count | Letters |",
            "| --- | ---: | --- |",
        ]
    )
    for item in diagnostic["top_letter_pair_patterns"]:
        lines.append(
            f"| `{_cell(str(item['pattern']))}` | {item['count']} | "
            f"{_cell(', '.join(item['letters']))} |"
        )

    lines.extend(["", "## Read", ""])
    lines.append(diagnostic["claim_language"]["supported"])
    lines.extend(["", "Not supported:"])
    lines.append(diagnostic["claim_language"]["not_supported"])
    lines.extend(["", "## Examples By Bucket", ""])
    for bucket, examples in _examples_by_bucket(diagnostic["panel"]).items():
        lines.extend([f"### `{bucket}`", ""])
        lines.extend(_example_table(examples))
        lines.append("")
    return "\n".join(lines)


def _nested_count_table(values: Mapping[str, Mapping[str, int]], label: str) -> list[str]:
    lines = ["| Bucket | " + label + " | Count |", "| --- | --- | ---: |"]
    for bucket, bucket_values in values.items():
        for key, count in sorted(bucket_values.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"| `{bucket}` | {key} | {count} |")
    return lines


def _flat_count_table(values: Mapping[str, int], label: str) -> list[str]:
    lines = [f"| {label} | Count |", "| --- | ---: |"]
    for key, count in sorted(values.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{key}` | {count} |")
    return lines


def _examples_by_bucket(panel: Sequence[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    out: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for item in panel:
        bucket = str(item["bucket"])
        if len(out[bucket]) < 5:
            out[bucket].append(item)
    return dict(sorted(out.items()))


def _example_table(examples: Sequence[Mapping[str, Any]]) -> list[str]:
    lines = [
        "| Letter | Side | State | Type family | Action | Evidence | Opposite |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in examples:
        opposite = "; ".join(
            f"{opp['side']}/{opp['state']}/{opp['type_family']}"
            for opp in item.get("opposite_summary", [])
        )
        lines.append(
            "| "
            + " | ".join(
                _cell(str(value))
                for value in (
                    item["letter_id"],
                    item["side"],
                    item["state"],
                    item["type_family"],
                    item["possible_action_class"],
                    item["evidence"],
                    opposite,
                )
            )
            + " |"
        )
    return lines


def _cell(value: str) -> str:
    return " ".join(value.split()).replace("|", "\\|")


def main() -> None:
    diagnostic = build_panel(read_ledger(), read_rows())
    out_json, out_md = write_artifacts(diagnostic)
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
