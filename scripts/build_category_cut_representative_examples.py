#!/usr/bin/env python3
# ruff: noqa: E501
"""Build real development-letter companion reports for the category cuts.

No model calls. No locked-test row inspection. See the dated protocol beside
the generated reports.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    headline_keys,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
)

try:
    from scripts.exectv2_within_family_categories import (
        FAMILIES,
        family_subtypes,
        observed_gold_subtypes,
    )
except ModuleNotFoundError:  # Direct ``python scripts/...`` execution.
    from exectv2_within_family_categories import (  # type: ignore[no-redef]
        FAMILIES,
        family_subtypes,
        observed_gold_subtypes,
    )

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "experiments/category_cut_representative_examples_20260808.json"
GAN_REPORT = ROOT / "docs/research/gan2026_category_cut_representative_examples_2026-08-08.md"
EXECT_REPORT = ROOT / "docs/research/exectv2_category_cut_representative_examples_2026-08-08.md"
GAN_RULES = ROOT / "experiments/gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_gpt41mini_2026-06-07.jsonl"
GAN_LLM = ROOT / "experiments/gan2026_six_model_validation_20260718/gpt56sol--llm_only.jsonl"
GAN_HYBRID = ROOT / "experiments/gan2026_matched_v05_dev750_attribution_20260727.json"
EXECT_RULES = ROOT / "experiments/exectv2_rules_only_four_family_letter_scores_dev140_20260806.jsonl"
EXECT_MODEL = ROOT / "experiments/exectv2_six_model_single_call_gpt56sol_dev140_20260715.jsonl"

GAN_BUCKETS = (
    "ordinary_point_rate",
    "cluster_burden",
    "seizure_free",
    "range_rate",
    "unknown_sentinel",
    "no_reference_sentinel",
    "unresolved_multiple",
)
# A deliberately plain ordinary-rate letter: one current monthly statement,
# without a diary reconstruction, cluster grammar, or competing window total.
GAN_PREFERRED_EXAMPLE_ROWS = {
    "ordinary_point_rate": (4026, 4402),
}
_MULTIPLE = re.compile(r"\bmultiple\b", re.I)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def compact(text: Any, limit: int = 180) -> str:
    value = " ".join(str(text or "").split())
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def esc(text: Any) -> str:
    return str(text or "").replace("|", "\\|").replace("\n", " ")


def excerpt(note: str, anchors: list[str], limit: int = 1200) -> str:
    """Return a readable note window covering the first useful anchor."""
    note_one = " ".join(note.split())
    positions = []
    lower = note_one.lower()
    for anchor in anchors:
        a = " ".join(str(anchor or "").split()).strip()
        if not a:
            continue
        pos = lower.find(a.lower())
        if pos >= 0:
            positions.append((pos, len(a)))
    if not positions:
        return compact(note_one, limit)
    start = max(0, min(p for p, _ in positions) - 260)
    end = min(len(note_one), max(p + n for p, n in positions) + 420)
    if end - start > limit:
        end = start + limit
    prefix = "…" if start else ""
    suffix = "…" if end < len(note_one) else ""
    return prefix + note_one[start:end].strip() + suffix


def gan_bucket(record: Any) -> str:
    label = record.gold_label.lower().strip()
    kind = record.gold_label_kind.value
    if kind == "frequency" and "cluster" in label:
        return "cluster_burden"
    if kind == "frequency" and " to " in label:
        return "range_rate"
    if kind == "frequency":
        return "ordinary_point_rate"
    if kind == "seizure_free":
        return "seizure_free"
    if kind == "unknown":
        return "unknown_sentinel"
    if kind == "no_reference":
        return "no_reference_sentinel"
    if kind == "unresolved_multiple" or _MULTIPLE.search(label):
        return "unresolved_multiple"
    raise ValueError(f"Unmapped Gan label: {record.gold_label!r}")


def gan_label(row: dict[str, Any], method: str) -> str:
    if method == "rules":
        return str(row.get("final_label") or "[no answer]")
    if method == "llm":
        return str((row.get("decision_record") or {}).get("final_label") or "[no answer]")
    return str(row.get("final_label") or "[no answer]")


def replay_undoubled_calendar_log(answer: str, evidence: str) -> str:
    """Replace a saved hybrid 2x calendar-log total with the current unique-month parse."""
    from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence.selected_evidence_monthly_diary import (
        monthly_diary_label_from_text,
    )

    replayed = monthly_diary_label_from_text(evidence)
    if not replayed:
        return answer
    saved = re.fullmatch(r"(\d+) per (\d+) month", answer.strip())
    live = re.fullmatch(r"(\d+) per (\d+) month", replayed.strip())
    if (
        saved
        and live
        and int(saved.group(1)) == 2 * int(live.group(1))
        and int(saved.group(2)) == 2 * int(live.group(2))
    ):
        return replayed
    return answer


def gan_evidence(row: dict[str, Any], method: str) -> str:
    if method == "rules":
        return str(((row.get("diagnostics") or {}).get("final_selection") or {}).get("evidence") or "")
    if method == "llm":
        return str((row.get("decision_record") or {}).get("evidence") or "")
    return str(row.get("selected_evidence") or "")


def gan_correct(row: dict[str, Any], method: str) -> bool | None:
    if method == "hybrid":
        value = row.get("final_purist_correct")
    else:
        value = (row.get("comparison") or {}).get("purist_correct")
    return None if value is None else bool(value)


def method_signature(answers: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(answers[k].get("answer", "")) for k in ("rules", "llm", "llm_with_rules"))


def pick(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return sorted(
        candidates,
        key=lambda r: (
            -len(set(method_signature(r["methods"]))),
            -(sum(r["methods"][m].get("correct") is True for m in r["methods"])),
            int(r["row_id"] if str(r["row_id"]).isdigit() else 0),
        ),
    )[0]


def build_gan() -> dict[str, Any]:
    records = {int(r.source_row_index): r for r in load_records_for_split("validation")}
    rules = {int(r["source_row_index"]): r for r in read_jsonl(GAN_RULES)}
    llm = {int(r["source_row_index"]): r for r in read_jsonl(GAN_LLM)}
    hybrid_raw = json.loads(GAN_HYBRID.read_text(encoding="utf-8"))
    hybrid = {int(r["source_row_index"]): r for r in hybrid_raw["rows"] if r.get("model_slug") == "gpt56sol"}
    by_bucket: dict[str, list[dict[str, Any]]] = {b: [] for b in GAN_BUCKETS}
    for idx, record in records.items():
        if idx not in rules or idx not in llm or idx not in hybrid:
            continue
        methods = {
            "rules": {"answer": gan_label(rules[idx], "rules"), "evidence": gan_evidence(rules[idx], "rules"), "correct": gan_correct(rules[idx], "rules")},
            "llm": {"answer": gan_label(llm[idx], "llm"), "evidence": gan_evidence(llm[idx], "llm"), "correct": gan_correct(llm[idx], "llm")},
            "llm_with_rules": {
                "answer": replay_undoubled_calendar_log(
                    gan_label(hybrid[idx], "hybrid"),
                    gan_evidence(hybrid[idx], "hybrid"),
                ),
                "evidence": gan_evidence(hybrid[idx], "hybrid"),
                "correct": gan_correct(hybrid[idx], "hybrid"),
            },
        }
        anchors = [record.gold_reference, *[m["evidence"] for m in methods.values()]]
        item = {"row_id": idx, "category": gan_bucket(record), "gold": record.gold_label, "excerpt": excerpt(record.note_text, anchors), "methods": methods}
        by_bucket[item["category"]].append(item)
    examples: dict[str, list[dict[str, Any]]] = {}
    for bucket, rows in by_bucket.items():
        if not rows:
            continue
        preferred = GAN_PREFERRED_EXAMPLE_ROWS.get(bucket)
        if preferred:
            preferred_rows = [row for row_id in preferred for row in rows if row["row_id"] == row_id]
            examples[bucket] = preferred_rows or [pick(rows)]
        else:
            examples[bucket] = [pick(rows)]
    return {"split": "dev750", "model": "GPT-5.6 Sol", "examples": examples}


def mention_display(mention: dict[str, Any]) -> str:
    attrs = mention.get("attributes") or {}
    keep = (
        "DiagCategory",
        "NumberOfSeizures",
        "LowerNumberOfSeizures",
        "UpperNumberOfSeizures",
        "NumberOfTimePeriods",
        "LowerNumberOfTimePeriods",
        "UpperNumberOfTimePeriods",
        "TimePeriod",
        "PointInTime",
        "TimeSince_or_TimeOfEvent",
        "FrequencyChange",
        "YearDate",
        "MonthDate",
        "DayDate",
        "DrugName",
        "DrugDose",
        "DoseUnit",
        "Frequency",
        "MRI_Performed",
        "MRI_Results",
        "EEG_Performed",
        "EEG_Results",
        "CT_Performed",
        "CT_Results",
    )
    bits = [f"{k}={attrs[k]}" for k in keep if k in attrs]
    return f"{mention.get('text', '')}" + (f" ({', '.join(bits)})" if bits else "")


def exect_methods(row_rules: dict[str, Any], row_model: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for name, field in (("rules", "predicted_mentions"), ("llm", "raw_lane_mentions"), ("llm_with_rules", "predicted_mentions")):
        source = row_rules if name == "rules" else row_model
        mentions = [m for m in source.get(field, []) if m.get("entity") in FAMILIES]
        out[name] = {"answers": {f: [mention_display(m) for m in mentions if m.get("entity") == f] for f in FAMILIES}, "evidence": [str(m.get("evidence") or "") for m in mentions if m.get("evidence")]}
    return out


def exect_status(gold: list[dict[str, Any]], pred: list[dict[str, Any]], family: str) -> str:
    return "match" if headline_keys({"gold_mentions": gold, "predicted_mentions": pred}, family, field="gold_mentions") == headline_keys({"gold_mentions": gold, "predicted_mentions": pred}, family, field="predicted_mentions") else "differs"


def build_exect() -> dict[str, Any]:
    rules = {str(r["letter_id"]): r for r in read_jsonl(EXECT_RULES)}
    model = {str(r["letter_id"]): r for r in read_jsonl(EXECT_MODEL)}
    letters = {str(r.letter_id): r for r in load_letters_for_split("dev")}
    subtype_order = {
        family: observed_gold_subtypes(rules.values(), family) for family in FAMILIES
    }
    by_subtype: dict[str, dict[str, list[dict[str, Any]]]] = {
        family: {subtype: [] for subtype in subtype_order[family]}
        for family in FAMILIES
    }
    for letter_id, letter in letters.items():
        if letter_id not in rules or letter_id not in model:
            continue
        gold = rules[letter_id].get("gold_mentions", [])
        methods = exect_methods(rules[letter_id], model[letter_id])
        for name, field in (("rules", "predicted_mentions"), ("llm", "raw_lane_mentions"), ("llm_with_rules", "predicted_mentions")):
            src = rules[letter_id] if name == "rules" else model[letter_id]
            pred = [m for m in src.get(field, []) if m.get("entity") in FAMILIES]
            methods[name]["status"] = {f: exect_status(gold, pred, f) for f in FAMILIES}
        anchors = [str(m.get("evidence") or "") for m in model[letter_id].get("predicted_mentions", [])] + [str(m.get("evidence") or "") for m in rules[letter_id].get("predicted_mentions", [])]
        for ann in letter.annotations:
            if ann.entity in FAMILIES:
                anchors.append(ann.raw_text)
        for family in FAMILIES:
            gold_family = [m for m in gold if m.get("entity") == family]
            subtypes = {
                subtype for mention in gold_family for subtype in family_subtypes(mention)
            }
            for subtype in subtypes:
                item = {
                    "row_id": letter_id,
                    "family": family,
                    "subtype": subtype,
                    "gold": [mention_display(m) for m in gold_family],
                    "excerpt": excerpt(letter.note_text, anchors),
                    "methods": {
                        name: {
                            "answers": method["answers"][family],
                            "status": method["status"][family],
                        }
                        for name, method in methods.items()
                    },
                }
                by_subtype[family][subtype].append(item)

    def pick_family(rows: list[dict[str, Any]]) -> dict[str, Any]:
        return sorted(
            rows,
            key=lambda row: (
                -len(
                    {
                        tuple(row["methods"][name]["answers"])
                        for name in ("rules", "llm", "llm_with_rules")
                    }
                ),
                -sum(
                    row["methods"][name]["status"] == "match"
                    for name in ("rules", "llm", "llm_with_rules")
                ),
                row["row_id"],
            ),
        )[0]

    return {
        "split": "dev140",
        "model": "GPT-5.6 Sol",
        "category_unit": "gold_defined_within_family_subtype",
        "examples": {
            family: {
                subtype: pick_family(rows)
                for subtype, rows in subtypes.items()
                if rows
            }
            for family, subtypes in by_subtype.items()
        },
    }


def gan_markdown(data: dict[str, Any]) -> str:
    why = {"ordinary_point_rate": "One countable rate; the main Gan mass.", "cluster_burden": "Cluster grammar must preserve both cluster frequency and seizures per cluster.", "seizure_free": "The note supports a quiet interval rather than an active rate.", "range_rate": "Both ends of a rate range matter.", "unknown_sentinel": "The gold answer withholds a rate.", "no_reference_sentinel": "The note has no usable seizure-frequency reference.", "unresolved_multiple": "The note says multiple, without a count that should be invented."}
    lines = [
        "# Gan 2026 category-cut representative examples",
        "",
        "Paper-library role: detailed development examples; use the [row-evidence workbook](artifacts/paper_source_row_evidence_2026-08-10.xlsx) for filtering.",
        "",
        "Real development letters, with two examples for the dominant ordinary-rate bucket and one for each other gold-defined bucket. The examples explain the aggregate category cut; they do not estimate category performance on their own.",
        "",
        f"Split: `{data['split']}` · LLM model: `{data['model']}` · rules baseline: retained deterministic artifact.",
        "",
        "## How to read the cases",
        "",
        "The excerpt is the smallest source window covering the gold or method evidence. `correct` means Purist-correct for Gan; it is not a clinical-validation judgment.",
        "",
    ]
    for bucket, items in data["examples"].items():
        lines += [f"## `{bucket}`", "", why[bucket], ""]
        for number, item in enumerate(items, start=1):
            if len(items) > 1:
                lines += [f"### Example {number}", ""]
            lines += [
                f"**Development row:** `{item['row_id']}`  ",
                f"**Gold:** `{item['gold']}`",
                "",
                "### Source excerpt",
                "",
                f"> {item['excerpt']}",
                "",
                "### Three outputs",
                "",
                "| Method | Answer | Evidence used | Purist |",
                "| --- | --- | --- | --- |",
            ]
            for name, label in (("rules", "Rules"), ("llm", "LLM"), ("llm_with_rules", "LLM with rules")):
                method = item["methods"][name]
                status = "correct" if method["correct"] else "wrong" if method["correct"] is False else "—"
                lines.append(
                    f"| {label} | `{esc(method['answer'])}` | “{esc(compact(method['evidence'], 220))}” | {status} |"
                )
            if bucket == "ordinary_point_rate" and number == 1:
                lesson = (
                    "What this case makes visible: this is the easy, shared-competence "
                    "case—all three methods recover the same ordinary rate from one "
                    "explicit sentence."
                )
            else:
                lesson = (
                    "What this case makes visible: the methods can read the same source "
                    "text and still differ in selection, representation, or canonical "
                    "rendering."
                )
            if item["row_id"] == 4402:
                lines += [
                    "",
                    "Hybrid is a no-call calendar-log replay on the saved span. Older "
                    "hybrid panels still store `14 per 14 month`.",
                ]
            lines += ["", lesson, ""]
    lines += ["## Boundary", "", "These are `dev750` examples only. The reports use real synthetic clinical letters and retained predictions, but they are explanatory slices, not holdout evidence or clinical validation. See the [category-cut performance report](six_model_category_cut_performance_2026-08-06.md) for aggregate results and the [protocol](category_cut_representative_examples_protocol_2026-08-08.md) for provenance.", ""]
    return "\n".join(lines)


def exect_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# ExECTv2 within-family category examples",
        "",
        "Paper-library role: detailed development examples; use the [row-evidence workbook](artifacts/paper_source_row_evidence_2026-08-10.xlsx) for filtering.",
        "",
        "Real development examples for every observed gold-defined subtype inside Diagnosis, SeizureFrequency, Prescription, and Investigations. Whole-letter composition buckets are not the category surface.",
        "",
        f"Split: `{data['split']}` · LLM model: `{data['model']}` · rules baseline: regenerated deterministic four-family artifact.",
        "",
        "## How to read the cases",
        "",
        "Each case shows only the named clinical family. `LLM` is the saved raw model lane; `LLM with rules` is the saved post-family-rules prediction. `match` means the complete family-level headline keys equal gold on that letter; it is not a clinical-validation judgment.",
        "",
    ]
    for family, subtypes in data["examples"].items():
        lines += [f"## {family}", ""]
        for subtype, item in subtypes.items():
            lines += [f"### `{subtype}`", "", f"**Letter:** `{item['row_id']}`", "", "#### Source excerpt", "", f"> {item['excerpt']}", "", f"#### Gold {family} facts", ""]
            lines += ["; ".join(f"`{esc(v)}`" for v in item["gold"]), "", "#### Three outputs", "", "| Method | Family output | Family match |", "| --- | --- | --- |"]
            for name, label in (("rules", "Rules"), ("llm", "LLM"), ("llm_with_rules", "LLM with rules")):
                method = item["methods"][name]
                answers = method["answers"] or ["—"]
                lines.append(
                    f"| {label} | {'<br>'.join(esc(v) for v in answers)} | {method['status']} |"
                )
            lines += [""]
    lines += ["## Boundary", "", "These are `dev140` examples only. The reports use real annotated letters and retained predictions, but they are explanatory slices, not holdout evidence or clinical validation. See the [category-cut performance report](six_model_category_cut_performance_2026-08-06.md) for aggregate results and the [protocol](category_cut_representative_examples_protocol_2026-08-08.md) for provenance.", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write the artifact and reports")
    args = parser.parse_args()
    data = {"schema_version": "category_cut_representative_examples.v2", "date": "2026-08-08", "protocol": "docs/research/category_cut_representative_examples_protocol_2026-08-08.md", "gan2026": build_gan(), "exectv2": build_exect()}
    if not args.write:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    OUT_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    GAN_REPORT.write_text(gan_markdown(data["gan2026"]), encoding="utf-8")
    EXECT_REPORT.write_text(exect_markdown(data["exectv2"]), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {GAN_REPORT}")
    print(f"wrote {EXECT_REPORT}")


if __name__ == "__main__":
    main()
