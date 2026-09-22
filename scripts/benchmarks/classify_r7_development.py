"""Classify saved R7 dev750 failures and rich/simple disagreements.

Reads the frozen mixed-attempt diagnostics and the earlier r4 simple
timeout-completed diagnostics. No model call, repair, or test450 access.

    .venv/bin/python scripts/benchmarks/classify_r7_development.py
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r7 as r7
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.one_shot_contract import (
    native_categories,
)

R7_VIEW = Path(
    "runs/one_shot_frequency_v2_measurements_r7/dev750/timeout600/timeout_completed"
)
PAIR_DIAG = Path(
    "runs/one_shot_thinking_r4_r5_r6/dev750/timeout600/timeout_completed/diagnostics.json"
)
OUT = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r7/"
    "dev750_timeout600/classification.json"
)

# Reviewed readings of the schema-valid Purist misses that are neither an unknown
# gold label nor a year-to-date denominator. The rule in `valid_wrong_cause`
# assigns the other misses. These sets must partition the remainder.
ANSWER_SELECTION = frozenset(
    {
        187, 869, 1357, 1695, 1706, 4116, 5141, 6065, 6251, 6509,
        7834, 7911, 8160, 9250, 9937, 10245, 10434, 12823, 13051, 13058,
        13893, 14540, 14581, 14635, 14806, 14872, 15306, 15317, 15529, 17110,
    }
)
SOURCE_EXTRACTION = frozenset({743, 1880, 4709, 5827, 8144, 8400})
BENCHMARK_REMAINDER = frozenset({10237, 10481, 12979, 15168, 15193, 15242, 15262})
YEAR_TO_DATE = frozenset({12788, 12810, 12827, 12835, 12877, 12901, 12949, 13008})


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def loc_template(loc: tuple[Any, ...]) -> str:
    return ".".join("*" if isinstance(part, int) else str(part) for part in loc)


def norm(text: str | None) -> str:
    return " ".join((text or "").split()).casefold()


def overlaps(left: str | None, right: str | None) -> bool:
    """Location test only. Short strings are not treated as the same passage."""
    a, b = norm(left), norm(right)
    if len(a) < 12 or len(b) < 12:
        return False
    return a in b or b in a


def surface(label: str) -> str:
    text = label
    for plural, singular in (
        ("months", "month"),
        ("weeks", "week"),
        ("years", "year"),
        ("days", "day"),
    ):
        text = text.replace(plural, singular)
    return re.sub(r"\bper 1 (month|week|year|day)\b", r"per \1", text)


def categories(label: str | None) -> dict[str, str] | None:
    if not label:
        return None
    try:
        return native_categories(label)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None


def schema_kind(errors: list[dict[str, Any]]) -> str:
    for error in errors:
        loc = loc_template(error["loc"])
        if error["type"] == "extra_forbidden" and loc.endswith(".period"):
            return "period_nested_in_measurement"
        if "number_duration" in error["msg"]:
            return "legacy_duration_tag"
        if error["type"] == "value_error":
            return "cluster_count_without_time"
        value = error.get("input")
        if (
            "bound.value" in loc
            and isinstance(value, dict)
            and value.get("type") == "number"
        ):
            return "quantity_object_inside_bound"
    return "other"


def answer_evidence(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    return str((payload.get("answer") or {}).get("evidence") or "")


def valid_wrong_cause(row: dict[str, Any], gold: str, evidence: str) -> str:
    """One cause for a schema-valid Purist miss.

    Unknown gold is the benchmark's unknown convention. A year-to-date count
    labeled per year is the benchmark's elapsed-window convention. The
    remaining rows were read from the saved quotations.
    """
    if gold == "unknown":
        return "benchmark_convention"
    text = evidence.casefold()
    label = row.get("label") or ""
    if "per year" in label and re.search(r"so far|this year|documented in 20", text):
        return "benchmark_convention"
    index = row["source_row_index"]
    if index in ANSWER_SELECTION:
        return "answer_selection"
    if index in SOURCE_EXTRACTION:
        return "source_extraction"
    if index in BENCHMARK_REMAINDER:
        return "benchmark_convention"
    raise ValueError(f"Unreviewed schema-valid miss {index}")


def disagreement_cause(item: dict[str, Any]) -> str:
    if item["relation"] == "one_unusable":
        failures = {item["r7_failure"], item["simple_failure"]}
        if "no_response" in failures:
            return "no_response"
        return "representation"
    if item["relation"] == "surface":
        return "representation"
    if item["relation"] in {"seizure_free_duration", "sentinel"}:
        return "benchmark_convention"
    if item["same_evidence"]:
        return "answer_selection"
    return "source_extraction"


def response_gap(saved: dict[str, Any]) -> str:
    if saved.get("error"):
        return str(saved["error"])
    response = saved.get("response") or {}
    if not response.get("choices"):
        return "provider_error_payload"
    return "empty_content"


def main() -> None:
    records = {row.source_row_index: row for row in study.records()}
    r7_rows = load_json(R7_VIEW / "diagnostics.json")
    responses = {
        row["request_id"]: row
        for row in study.old.read_lines(R7_VIEW / "responses.jsonl")
    }
    simple = {
        row["source_row_index"]: row
        for row in load_json(PAIR_DIAG)
        if row["condition"] == "r4_simple"
    }
    if len(r7_rows) != 750 or len(simple) != 750:
        raise ValueError("Development coverage is not 750")

    schema_rows = []
    invalid_labels = []
    valid_wrong = []
    disagreements = []
    paired: Counter[str] = Counter()
    year_to_date: set[int] = set()

    for row in r7_rows:
        record = records[row["source_row_index"]]
        other = simple[row["source_row_index"]]
        payload = json.loads(row["structured_json"]) if row.get("structured_json") else {}
        other_payload = (
            json.loads(other["structured_json"]) if other.get("structured_json") else {}
        )
        rich_right = bool(row.get("purist_correct"))
        simple_right = bool(other.get("purist_correct"))
        if rich_right and simple_right:
            paired["both_correct"] += 1
        elif rich_right:
            paired["rich_only"] += 1
        elif simple_right:
            paired["simple_only"] += 1
        else:
            paired["both_wrong"] += 1

        if row["failure"] == "invalid_schema":
            try:
                r7.Rich.model_validate(payload)
            except ValidationError as exc:
                errors = list(exc.errors())
            else:
                raise ValueError("Schema-invalid row validated")
            schema_rows.append(
                {
                    "source_row_index": row["source_row_index"],
                    "kind": schema_kind(errors),
                    "label": row.get("label"),
                    "purist_correct": rich_right,
                    "gold_label": record.gold_label,
                }
            )
        if row.get("answer_failure") == "invalid_target_label":
            invalid_labels.append(
                {
                    "source_row_index": row["source_row_index"],
                    "label": (payload.get("answer") or {}).get("label")
                    if isinstance(payload, dict)
                    else None,
                    "gold_label": record.gold_label,
                }
            )
        if row["failure"] is None and not rich_right:
            evidence = answer_evidence(payload) + " " + record.gold_reference
            cause = valid_wrong_cause(row, record.gold_label, evidence)
            if cause == "benchmark_convention" and row["source_row_index"] in YEAR_TO_DATE:
                year_to_date.add(row["source_row_index"])
            elif (
                record.gold_label != "unknown"
                and "per year" in (row.get("label") or "")
                and re.search(
                    r"so far|this year|documented in 20", evidence.casefold()
                )
            ):
                year_to_date.add(row["source_row_index"])
            valid_wrong.append(
                {
                    "source_row_index": row["source_row_index"],
                    "cause": cause,
                    "gold_label": record.gold_label,
                    "label": row.get("label"),
                    "simple_label": other.get("label"),
                    "simple_purist_correct": simple_right,
                }
            )

        rich_ok = bool(row.get("answer_valid"))
        simple_ok = bool(other.get("answer_valid"))
        labels_differ = rich_ok and simple_ok and row.get("label") != other.get("label")
        if not (labels_differ or rich_ok != simple_ok):
            continue
        rich_label = row.get("label")
        simple_label = other.get("label")
        rich_cat = categories(rich_label)
        simple_cat = categories(simple_label)
        if not rich_ok or not simple_ok:
            relation = "one_unusable"
        elif surface(rich_label) == surface(simple_label):
            relation = "surface"
        elif (
            rich_cat is not None
            and simple_cat is not None
            and rich_cat["purist"] == simple_cat["purist"]
            and str(rich_label).startswith("seizure free")
            and str(simple_label).startswith("seizure free")
        ):
            relation = "seizure_free_duration"
        elif (
            rich_cat is not None
            and simple_cat is not None
            and rich_cat["purist"] == simple_cat["purist"]
            and (
                str(rich_label).startswith("unknown")
                or str(rich_label) == "no seizure frequency reference"
            )
            and (
                str(simple_label).startswith("unknown")
                or str(simple_label) == "no seizure frequency reference"
            )
        ):
            relation = "sentinel"
        elif (
            rich_cat is not None
            and simple_cat is not None
            and rich_cat["purist"] == simple_cat["purist"]
        ):
            relation = "same_purist_bin"
        else:
            relation = "different_purist_bin"
        item = {
            "source_row_index": row["source_row_index"],
            "relation": relation,
            "gold_label": record.gold_label,
            "r7_label": rich_label,
            "r7_failure": row.get("failure"),
            "r7_purist_correct": rich_right,
            "simple_label": simple_label,
            "simple_failure": other.get("failure"),
            "simple_purist_correct": simple_right,
            "same_evidence": overlaps(
                answer_evidence(payload), answer_evidence(other_payload)
            ),
        }
        item["cause"] = disagreement_cause(item)
        disagreements.append(item)

    if year_to_date != YEAR_TO_DATE:
        raise ValueError(f"Year-to-date rows changed: {sorted(year_to_date)}")
    assigned = {row["source_row_index"] for row in valid_wrong}
    reviewed = ANSWER_SELECTION | SOURCE_EXTRACTION | BENCHMARK_REMAINDER
    unknown_or_ytd = assigned - reviewed
    if reviewed - assigned:
        raise ValueError(f"Reviewed rows were not misses: {sorted(reviewed - assigned)}")
    if any(
        row["source_row_index"] in reviewed and row["cause"] == "benchmark_convention"
        and row["gold_label"] == "unknown"
        for row in valid_wrong
    ):
        raise ValueError("A reviewed remainder row was swallowed by the unknown rule")
    causes = Counter(row["cause"] for row in valid_wrong)
    if sum(causes.values()) != 83 or len(schema_rows) != 36 or len(invalid_labels) != 7:
        raise ValueError("Failure totals drifted from the frozen mixed view")
    schema_kinds = Counter(row["kind"] for row in schema_rows)
    if schema_kinds["other"]:
        raise ValueError("Unclassified schema failure")
    gaps = Counter(
        response_gap(responses[row["request_id"]])
        for row in r7_rows
        if row["failure"] == "no_response"
    )
    if sum(gaps.values()) != 5:
        raise ValueError("No-response count drifted")

    purist = sum(bool(row.get("purist_correct")) for row in r7_rows)
    strict = sum(
        bool(row.get("purist_correct")) and row["failure"] is None for row in r7_rows
    )
    report = {
        "version": "r7_dev750_failure_classification_v1",
        "dataset": "Gan 2026 synthetic",
        "split": "dev750",
        "row_policy": "all development rows; failures retained",
        "n": 750,
        "model": "deepseek-flash",
        "provider_documented_version": "DeepSeek-V4.1-Flash",
        "repair_policy": "none",
        "scope": (
            "Synthetic development review of saved outputs. Not a holdout result, "
            "not a simultaneous paired rerun, and not clinical validation."
        ),
        "rich": {
            "prompt_version": r7.VERSION,
            "revision": r7.REVISION,
            "view": "mixed attempts; original usable responses plus single no-response reruns",
            "purist_correct": purist,
            "strict_purist_correct": strict,
        },
        "simple": {
            "condition": "r4_simple",
            "view": "thinking timeout-completed mixed attempts",
            "purist_correct": sum(bool(row.get("purist_correct")) for row in simple.values()),
            "note": (
                "R7 was not run as a paired simple condition. r4 simple is the "
                "earlier controlled comparator. R7 kept r5 task wording and changed "
                "the rich schema and its population instructions."
            ),
        },
        "paired_purist": dict(paired),
        "development_failures": {
            "purist_misses": 750 - purist,
            "recorded_failure": dict(Counter(row["failure"] for row in r7_rows if row["failure"])),
            "no_response": dict(gaps),
            "schema": {
                "n": len(schema_rows),
                "kinds": dict(schema_kinds),
                "purist_correct_despite_schema": sum(row["purist_correct"] for row in schema_rows),
                "rows": schema_rows,
            },
            "invalid_target_label": invalid_labels,
            "schema_valid_purist_miss": {
                "n": len(valid_wrong),
                "causes": dict(causes),
                "simple_also_wrong": sum(
                    not row["simple_purist_correct"] for row in valid_wrong
                ),
                "by_cause_simple_also_wrong": {
                    cause: sum(
                        not row["simple_purist_correct"]
                        for row in valid_wrong
                        if row["cause"] == cause
                    )
                    for cause in sorted(causes)
                },
                "year_to_date": sorted(YEAR_TO_DATE),
                "rows": valid_wrong,
            },
        },
        "disagreements": {
            "definition": (
                "Declared labels differ, or exactly one side has a usable answer. "
                "Surface differences are plural units and 'per 1 unit' versus 'per unit'."
            ),
            "n": len(disagreements),
            "relations": dict(Counter(row["relation"] for row in disagreements)),
            "causes": dict(Counter(row["cause"] for row in disagreements)),
            "rows": disagreements,
        },
        "method": {
            "schema": (
                "Every invalid_schema payload was revalidated. Kinds come from the "
                "rejected input, not from the union-member noise around it."
            ),
            "schema_valid_miss": (
                "Gold unknown is benchmark convention. A per-year label whose "
                "quotation says so far, this year, or documented in 20xx is the "
                "year-to-date convention. Remaining rows were assigned by reading "
                "the gold reference and the declared answer quotation."
            ),
            "disagreement": (
                "Same-bin and surface classes use the native Purist projection. "
                "Quotation overlap is a substring test of at least 12 characters, "
                "not an entailment judgment."
            ),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    summary = {
        "purist": purist,
        "strict": strict,
        "paired": dict(paired),
        "schema_kinds": dict(schema_kinds),
        "valid_wrong": dict(causes),
        "valid_wrong_shared": report["development_failures"]["schema_valid_purist_miss"][
            "by_cause_simple_also_wrong"
        ],
        "no_response": dict(gaps),
        "invalid_labels": [
            (row["source_row_index"], row["label"]) for row in invalid_labels
        ],
        "disagreement_relations": report["disagreements"]["relations"],
        "disagreement_causes": report["disagreements"]["causes"],
        "unknown_or_ytd_n": len(unknown_or_ytd),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
