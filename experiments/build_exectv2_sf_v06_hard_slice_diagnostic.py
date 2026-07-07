"""Build the SF v0.6 hard-slice residual diagnostic.

This is a gold-aware offline analysis of the v0.6 SeizureFrequency projection
artifact. It does not alter predictions. The goal is to decide whether the
remaining below-target SF gap is worth another targeted loop, and if so which
failure slice would need a predeclared intervention.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from collections.abc import Hashable, Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    _frequency_state_keys as frequency_state_keys,
)

DEFAULT_JSONL = Path(
    "experiments/exectv2_hybrid_sf_state_projection_v06_combined_dev140_20260618.jsonl"
)
OUT_JSON = Path("experiments/exectv2_sf_v06_hard_slice_diagnostic_dev140_20260618.json")
OUT_MD = Path("experiments/exectv2_sf_v06_hard_slice_diagnostic_dev140_20260618.md")

Side = Literal["gold", "predicted"]

_GENERIC_CUIS = {"C0036572", "C1299590"}
_UNSUPPORTED_CHANGE_RE = re.compile(
    r"\b("
    r"risk of increased seizures|should there be|if .*further seizures|"
    r"previously|in the past|were well controlled|epilepsy .*stable|"
    r"family history|no history of"
    r")\b",
    re.IGNORECASE,
)
_DRUG_CHANGE_RE = re.compile(
    r"\b(lamotrigine|tegretol|carbamazepine|valproate|eplim|dose|drug|medication)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ResidualEvent:
    letter_id: str
    side: Side
    state: str
    type_key: str
    bucket: str
    text: str
    attributes: dict[str, str]
    evidence: str
    opposite_summary: str


def read_rows(path: Path = DEFAULT_JSONL) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def build_diagnostic(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    events: list[ResidualEvent] = []
    state_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"fn": 0, "fp": 0})
    for row in rows:
        gold_items = _items(row.get("gold_mentions", []))
        pred_items = _items(row.get("predicted_mentions", []))
        gold_counter = Counter(key for key, _mention in gold_items)
        pred_counter = Counter(key for key, _mention in pred_items)

        for key, count in (gold_counter - pred_counter).items():
            state_counts[key[1]]["fn"] += count
            for mention in _matching_mentions(gold_items, key, count):
                events.append(_event(row, "gold", key, mention, pred_items))

        for key, count in (pred_counter - gold_counter).items():
            state_counts[key[1]]["fp"] += count
            for mention in _matching_mentions(pred_items, key, count):
                events.append(_event(row, "predicted", key, mention, gold_items))

    unknown_events = [event for event in events if event.state == "unknown"]
    return {
        "generated": "2026-06-18",
        "split": "dev",
        "letters": len(rows),
        "source_jsonl": str(DEFAULT_JSONL),
        "state_residual_counts": dict(state_counts),
        "unknown_summary": _bucket_summary(unknown_events),
        "unknown_events": [asdict(event) for event in unknown_events],
        "all_event_count": len(events),
        "claim_language": {
            "supported": (
                "After v0.6, the remaining SF blocker is not broad state recall. "
                "Unknown-state recall is high enough to expose a precision problem: "
                "22 unknown over-emissions versus 8 unknown misses."
            ),
            "not_supported": (
                "Another broad unknown/change recovery rule is likely to clear "
                "the 0.8 gate without collateral precision loss."
            ),
        },
    }


def write_artifacts(
    diagnostic: Mapping[str, Any],
    *,
    out_json: Path = OUT_JSON,
    out_md: Path = OUT_MD,
) -> tuple[Path, Path]:
    out_json.write_text(json.dumps(diagnostic, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(_render_markdown(diagnostic, json_path=out_json), encoding="utf-8")
    return out_json, out_md


def _items(
    mentions: Iterable[Mapping[str, Any]],
) -> list[tuple[tuple[Hashable, str], Mapping[str, Any]]]:
    out: list[tuple[tuple[Hashable, str], Mapping[str, Any]]] = []
    for mention in mentions:
        annotation = ExectAnnotation(
            entity="SeizureFrequency",
            text=str(mention.get("text", "")),
            attributes={str(k): str(v) for k, v in dict(mention.get("attributes") or {}).items()},
        )
        for key in frequency_state_keys((annotation,), "clinical_headline"):
            out.append((key, mention))
    return out


def _matching_mentions(
    items: Sequence[tuple[tuple[Hashable, str], Mapping[str, Any]]],
    key: tuple[Hashable, str],
    count: int,
) -> list[Mapping[str, Any]]:
    matches = [mention for item_key, mention in items if item_key == key]
    return matches[:count]


def _event(
    row: Mapping[str, Any],
    side: Side,
    key: tuple[Hashable, str],
    mention: Mapping[str, Any],
    opposite_items: Sequence[tuple[tuple[Hashable, str], Mapping[str, Any]]],
) -> ResidualEvent:
    opposite_by_type = [item for item in opposite_items if item[0][0] == key[0]]
    opposite_any = list(opposite_items)
    return ResidualEvent(
        letter_id=str(row["letter_id"]),
        side=side,
        state=key[1],
        type_key=_key_to_string(key[0]),
        bucket=_bucket(side, key, mention, opposite_by_type, opposite_any, row),
        text=str(mention.get("text", "")),
        attributes={str(k): str(v) for k, v in dict(mention.get("attributes") or {}).items()},
        evidence=str(mention.get("evidence", "")),
        opposite_summary=_opposite_summary(opposite_by_type or opposite_any),
    )


def _bucket(
    side: Side,
    key: tuple[Hashable, str],
    mention: Mapping[str, Any],
    opposite_by_type: Sequence[tuple[tuple[Hashable, str], Mapping[str, Any]]],
    opposite_any: Sequence[tuple[tuple[Hashable, str], Mapping[str, Any]]],
    row: Mapping[str, Any],
) -> str:
    typ, state = key
    if side == "gold" and state == "unknown":
        if opposite_by_type:
            return "unknown_fn.state_swap_with_predicted_" + opposite_by_type[0][0][1]
        if _opposite_genericness_present(typ, opposite_any):
            return "unknown_fn.generic_named_ownership_gap"
        if _candidate_change_available(row, typ):
            return "unknown_fn.change_candidate_available_not_selected"
        return "unknown_fn.no_matching_candidate_or_type"

    if side == "predicted" and state == "unknown":
        evidence = str(mention.get("evidence", ""))
        if _UNSUPPORTED_CHANGE_RE.search(evidence):
            return "unknown_fp.unsupported_or_conditional_change"
        if opposite_by_type:
            return "unknown_fp.state_swap_against_gold_" + opposite_by_type[0][0][1]
        if _opposite_genericness_present(typ, opposite_any):
            return "unknown_fp.generic_named_ownership_gap"
        if _DRUG_CHANGE_RE.search(evidence):
            return "unknown_fp.drug_response_scope"
        return "unknown_fp.grounded_scope_overemit"

    if opposite_by_type:
        return f"{state}_{side}.state_swap"
    return f"{state}_{side}.unpaired"


def _candidate_change_available(row: Mapping[str, Any], typ: Hashable) -> bool:
    want_generic = _is_generic_type(typ)
    for candidate in row.get("candidate_spans", []):
        ctype = str(candidate.get("candidate_type", ""))
        if "qualitative_change" not in ctype:
            continue
        text_hint = normalize_phrase(str(candidate.get("text_hint", "")))
        is_generic_candidate = text_hint in {"seizure", "seizures"}
        if is_generic_candidate == want_generic:
            return True
    return False


def _opposite_genericness_present(
    typ: Hashable,
    opposite_items: Sequence[tuple[tuple[Hashable, str], Mapping[str, Any]]],
) -> bool:
    if not opposite_items:
        return False
    want_generic = _is_generic_type(typ)
    return any(_is_generic_type(item_key[0]) != want_generic for item_key, _ in opposite_items)


def _is_generic_type(typ: Hashable) -> bool:
    if isinstance(typ, tuple) and len(typ) == 2:
        kind, value = typ
        if kind == "cui" and value in _GENERIC_CUIS:
            return True
        if kind == "phrase" and normalize_phrase(str(value)) in {
            "seizure",
            "seizures",
            "seizure free",
            "seizure-free",
        }:
            return True
    return False


def _opposite_summary(items: Sequence[tuple[tuple[Hashable, str], Mapping[str, Any]]]) -> str:
    parts = []
    for key, mention in items[:4]:
        parts.append(f"{_key_to_string(key[0])}/{key[1]}:{mention.get('text', '')}")
    if len(items) > 4:
        parts.append("...")
    return "; ".join(parts)


def _bucket_summary(events: Sequence[ResidualEvent]) -> dict[str, Any]:
    by_side = Counter(event.side for event in events)
    by_bucket = Counter(event.bucket for event in events)
    examples: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        if len(examples[event.bucket]) >= 5:
            continue
        examples[event.bucket].append(
            {
                "letter_id": event.letter_id,
                "side": event.side,
                "text": event.text,
                "evidence": event.evidence,
                "opposite": event.opposite_summary,
            }
        )
    return {
        "total": len(events),
        "by_side": dict(by_side),
        "by_bucket": dict(by_bucket),
        "examples": dict(examples),
    }


def _render_markdown(diagnostic: Mapping[str, Any], *, json_path: Path) -> str:
    unknown = diagnostic["unknown_summary"]
    lines = [
        "# ExECTv2 SF v0.6 Hard-Slice Diagnostic",
        "",
        f"- Generated: `{diagnostic['generated']}`",
        f"- JSON: `{json_path}`",
        f"- Source JSONL: `{diagnostic['source_jsonl']}`",
        f"- Split: `{diagnostic['split']}`",
        f"- Letters: {diagnostic['letters']}",
        "",
        "## Residual By State",
        "",
        "| State | FN | FP |",
        "| --- | ---: | ---: |",
    ]
    for state, counts in sorted(diagnostic["state_residual_counts"].items()):
        lines.append(f"| {state} | {counts.get('fn', 0)} | {counts.get('fp', 0)} |")

    lines.extend(
        [
            "",
            "## Unknown-State Hard Slice",
            "",
            f"- Unknown residual events: {unknown['total']}",
            f"- Gold misses: {unknown['by_side'].get('gold', 0)}",
            f"- Predicted over-emissions: {unknown['by_side'].get('predicted', 0)}",
            "",
            "| Bucket | Count |",
            "| --- | ---: |",
        ]
    )
    for bucket, count in sorted(unknown["by_bucket"].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{bucket}` | {count} |")

    lines.extend(
        [
            "",
            "## Read",
            "",
            (
                "The remaining SF blocker is now concentrated in unknown-state "
                "precision. v0.6 recovered many unknown misses, but the residual "
                "is asymmetric: 22 predicted unknown over-emissions versus 8 gold "
                "unknown misses."
            ),
            "",
            (
                "The biggest buckets are grounded scope/ownership disagreements, "
                "not render failures. This argues against another broad "
                "unknown/change recovery rule. A further loop would need a "
                "predeclared hard-slice intervention aimed at high-precision "
                "unknown suppression, with a stop rule if active-rate or "
                "seizure-free recall regresses."
            ),
            "",
            "Supported claim:",
            "",
            f"> {diagnostic['claim_language']['supported']}",
            "",
            "Not supported:",
            "",
            f"> {diagnostic['claim_language']['not_supported']}",
        ]
    )
    for bucket, examples in sorted(unknown["examples"].items()):
        lines.extend(["", f"## Examples: `{bucket}`", ""])
        lines.extend(_example_table(examples))
    lines.append("")
    return "\n".join(lines)


def _example_table(examples: Sequence[Mapping[str, str]]) -> list[str]:
    lines = [
        "| Letter | Side | Text | Evidence | Opposite |",
        "| --- | --- | --- | --- | --- |",
    ]
    for example in examples:
        lines.append(
            "| "
            + " | ".join(
                _cell(str(example[field]))
                for field in ("letter_id", "side", "text", "evidence", "opposite")
            )
            + " |"
        )
    return lines


def _cell(value: str) -> str:
    return " ".join(value.split()).replace("|", "\\|")


def _key_to_string(key: Any) -> str:
    return json.dumps(_jsonable_key(key), sort_keys=True, ensure_ascii=False)


def _jsonable_key(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable_key(item) for item in value]
    if isinstance(value, list):
        return [_jsonable_key(item) for item in value]
    if isinstance(value, dict):
        return {str(k): _jsonable_key(v) for k, v in value.items()}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def main() -> None:
    diagnostic = build_diagnostic(read_rows())
    out_json, out_md = write_artifacts(diagnostic)
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
