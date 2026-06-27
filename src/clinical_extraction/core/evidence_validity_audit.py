"""Replay-only evidence validity audit (Phase 0 — taxonomy, no metric call-site changes).

Classifies cited evidence strings against note text using the existing repair
cascade in ``core.evidence``. Read-only over saved artifacts + dataset note text.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.core.evidence import (
    clean_semantically_neutral_text_artifacts,
    evidence_is_substring,
    repair_case_only_evidence_copy,
    repair_ellipsis_span_evidence_copy,
    repair_section_header_list_item_evidence_copy,
    repair_whitespace_evidence_copy,
)
from clinical_extraction.core.registry import RunRegistryEntry, load_run_registry
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.loader import (
    load_active_llm_only_runs,
    load_rich_schema_runs,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_surfacing import (
    SURFACED_REPLAY_RUNS,
)

ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / "experiments" / "registry.jsonl"
OUT_JSON = ROOT / "experiments" / "evidence_validity_audit_2026-06-27.json"
OUT_MD = ROOT / "docs" / "experiments" / "reliability" / "evidence_validity_audit_2026-06-27.md"

TaskKind = Literal["gan2026", "exectv2"]
GanPipelineKind = Literal["hybrid", "llm_only", "agentic", "unknown"]


class EvidenceGrade(StrEnum):
    EXACT = "EXACT"
    REPAIRED_ARTIFACT = "REPAIRED_ARTIFACT"
    REPAIRED_CASE = "REPAIRED_CASE"
    REPAIRED_WHITESPACE = "REPAIRED_WHITESPACE"
    REPAIRED_ELLIPSIS = "REPAIRED_ELLIPSIS"
    REPAIRED_SECTION = "REPAIRED_SECTION"
    ABSENT = "ABSENT"
    EMPTY = "EMPTY"


GROUNDED_GRADES: frozenset[EvidenceGrade] = frozenset(
    grade
    for grade in EvidenceGrade
    if grade.name.startswith("EXACT") or grade.name.startswith("REPAIRED_")
)

ALL_GRADES: tuple[EvidenceGrade, ...] = tuple(EvidenceGrade)


@dataclass(frozen=True)
class AuditTarget:
    run_id: str
    task: TaskKind
    rows_path: Path
    model_label: str
    pipeline_family: str
    split: str
    source: str


def grade_evidence_string(note_text: str, evidence: str) -> EvidenceGrade:
    """Classify one evidence string using the existing repair cascade priority."""

    if not str(evidence or "").strip():
        return EvidenceGrade.EMPTY
    if evidence_is_substring(note_text, evidence):
        return EvidenceGrade.EXACT

    repaired = clean_semantically_neutral_text_artifacts(evidence)
    if repaired and repaired != evidence and evidence_is_substring(note_text, repaired):
        return EvidenceGrade.REPAIRED_ARTIFACT

    case_repaired = repair_case_only_evidence_copy(repaired, note_text)
    if case_repaired != repaired and evidence_is_substring(note_text, case_repaired):
        return EvidenceGrade.REPAIRED_CASE

    whitespace_repaired = repair_whitespace_evidence_copy(repaired, note_text)
    if whitespace_repaired != repaired and evidence_is_substring(note_text, whitespace_repaired):
        return EvidenceGrade.REPAIRED_WHITESPACE

    ellipsis_repaired = repair_ellipsis_span_evidence_copy(repaired, note_text)
    if ellipsis_repaired != repaired and evidence_is_substring(note_text, ellipsis_repaired):
        return EvidenceGrade.REPAIRED_ELLIPSIS

    section_repaired = repair_section_header_list_item_evidence_copy(repaired, note_text)
    if section_repaired != repaired and evidence_is_substring(note_text, section_repaired):
        return EvidenceGrade.REPAIRED_SECTION

    return EvidenceGrade.ABSENT


def is_grounded(grade: EvidenceGrade) -> bool:
    return grade in GROUNDED_GRADES


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if isinstance(obj, dict) and set(obj.keys()) == {"_metadata"}:
                continue
            rows.append(obj)
    return rows


def _gan_note_text_by_index() -> dict[int, str]:
    return {record.source_row_index: record.note_text for record in load_records()}


def _exect_note_text_by_letter() -> dict[str, str]:
    return {letter.letter_id: letter.note_text for letter in load_letters()}


def _infer_gan_pipeline(run_id: str, pipeline_family: str) -> GanPipelineKind:
    if "llm_only" in pipeline_family or "llm_only" in run_id:
        return "llm_only"
    if "hybrid_structured" in pipeline_family or "hybrid_structured" in run_id:
        return "hybrid"
    if any(token in run_id for token in ("fresh_evidence", "agentic", "consensus", "boundary")):
        return "agentic"
    return "unknown"


def _append_evidence(value: object, out: list[str]) -> None:
    if isinstance(value, list):
        for item in value:
            if item is not None and str(item).strip():
                out.append(str(item))
        return
    if value is not None and str(value).strip():
        out.append(str(value))


def extract_gan2026_evidence(row: Mapping[str, Any], pipeline: GanPipelineKind) -> list[str]:
    strings: list[str] = []
    if pipeline == "hybrid":
        structured = row.get("structured_record") or {}
        for event in structured.get("events") or []:
            _append_evidence((event or {}).get("evidence"), strings)
        _append_evidence((structured.get("selection") or {}).get("evidence"), strings)
        for event in row.get("normalized_events") or []:
            _append_evidence((event or {}).get("evidence"), strings)
    elif pipeline == "llm_only":
        _append_evidence((row.get("decision_record") or {}).get("evidence"), strings)
    elif pipeline == "agentic":
        for key in (
            "fresh_evidence_decision_record",
            "decision_record",
            "format_only_decision_record",
            "raw_decision_record",
        ):
            decision = row.get(key) or {}
            _append_evidence(decision.get("evidence"), strings)
        structured = row.get("structured_record") or {}
        for event in structured.get("events") or []:
            _append_evidence((event or {}).get("evidence"), strings)
        _append_evidence((structured.get("selection") or {}).get("evidence"), strings)
    else:
        structured = row.get("structured_record") or {}
        for event in structured.get("events") or []:
            _append_evidence((event or {}).get("evidence"), strings)
        _append_evidence((structured.get("selection") or {}).get("evidence"), strings)
        _append_evidence((row.get("decision_record") or {}).get("evidence"), strings)
    return strings


def extract_exectv2_evidence(row: Mapping[str, Any]) -> list[str]:
    strings: list[str] = []
    for mention in row.get("predicted_mentions") or []:
        _append_evidence((mention or {}).get("evidence"), strings)
    for mentions in (row.get("prediction_surfaces") or {}).values():
        for mention in mentions or []:
            _append_evidence((mention or {}).get("evidence"), strings)
    for mention in row.get("raw_lane_mentions") or []:
        _append_evidence((mention or {}).get("evidence"), strings)
    return strings


def _current_row_exact_valid(row: Mapping[str, Any], pipeline: GanPipelineKind) -> bool | None:
    if pipeline == "llm_only":
        if "evidence_text_contained" in row:
            return bool(row["evidence_text_contained"])
        return None
    if "evidence_valid" in row:
        return bool(row["evidence_valid"])
    return None


def _dedupe_preserve(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _pick_primary_jsonl(entry: RunRegistryEntry) -> Path | None:
    candidates = [
        Path(path)
        for path in entry.artifact_paths
        if path.endswith(".jsonl") and path.strip()
    ]
    if not candidates:
        return None
    preferred = [
        path
        for path in candidates
        if "phase1_report" not in path.name and not path.name.endswith("_graphs.jsonl")
    ]
    chosen = preferred[0] if preferred else candidates[0]
    return chosen if chosen.exists() else None


def build_registry_targets(entries: Sequence[RunRegistryEntry]) -> list[AuditTarget]:
    by_run_id = {entry.run_id: entry for entry in entries}
    targets: list[AuditTarget] = []

    for curation in SURFACED_REPLAY_RUNS:
        entry = by_run_id.get(curation.run_id)
        rows_path = (
            Path(curation.source_jsonl)
            if curation.source_jsonl
            else _pick_primary_jsonl(entry)
            if entry
            else None
        )
        if rows_path is None or not rows_path.exists():
            continue
        targets.append(
            AuditTarget(
                run_id=curation.run_id,
                task="gan2026",
                rows_path=rows_path,
                model_label=curation.model_display,
                pipeline_family=curation.pipeline_family,
                split="validation",
                source="registry_surface_as_architecture",
            )
        )

    for entry in entries:
        if entry.decision != "promote":
            continue
        rows_path = _pick_primary_jsonl(entry)
        if rows_path is None or not rows_path.exists():
            continue
        if any(target.run_id == entry.run_id for target in targets):
            continue
        targets.append(
            AuditTarget(
                run_id=entry.run_id,
                task="gan2026",
                rows_path=rows_path,
                model_label=entry.model,
                pipeline_family=entry.pipeline_family,
                split=entry.split,
                source="registry_promote",
            )
        )
    return targets


def build_exectv2_catalog_targets() -> list[AuditTarget]:
    targets: list[AuditTarget] = []
    for run in (*load_rich_schema_runs(), *load_active_llm_only_runs()):
        rows_path = run.rows_path
        if not rows_path.exists():
            continue
        split = "dev140" if "dev140" in rows_path.name else "unknown"
        targets.append(
            AuditTarget(
                run_id=run.candidate,
                task="exectv2",
                rows_path=rows_path,
                model_label=run.model_label,
                pipeline_family=run.surface_id or "rich_schema",
                split=split,
                source="exectv2_reliability_catalog",
            )
        )
    return targets


def audit_target(
    target: AuditTarget,
    *,
    gan_notes: Mapping[int, str],
    exect_notes: Mapping[str, str],
    sample_limit: int = 5,
) -> dict[str, Any]:
    rows = _load_jsonl(target.rows_path)
    pipeline = _infer_gan_pipeline(target.run_id, target.pipeline_family)

    grade_counts: Counter[str] = Counter()
    exact_invalid_counts: Counter[str] = Counter()
    samples: dict[str, list[str]] = defaultdict(list)
    row_total = 0
    row_current_exact_valid = 0
    row_current_exact_invalid = 0
    row_missing_current_flag = 0
    row_grounded_after_repair = 0
    row_all_strings_grounded = 0
    mention_total = 0
    mention_current_exact_valid = 0

    for row in rows:
        if target.task == "gan2026":
            source_index = row.get("source_row_index")
            if source_index is None:
                continue
            note_text = gan_notes.get(int(source_index), "")
            if not note_text:
                continue
            evidence_strings = _dedupe_preserve(extract_gan2026_evidence(row, pipeline))
            current_valid = _current_row_exact_valid(row, pipeline)
            row_total += 1
            if current_valid is None:
                row_missing_current_flag += 1
            elif current_valid:
                row_current_exact_valid += 1
            else:
                row_current_exact_invalid += 1
        else:
            letter_id = str(row.get("letter_id") or "")
            note_text = exect_notes.get(letter_id, "")
            if not letter_id or not note_text:
                continue
            evidence_strings = _dedupe_preserve(extract_exectv2_evidence(row))
            row_total += 1
            predicted = row.get("predicted_mentions") or []
            for mention in predicted:
                mention_total += 1
                if mention.get("evidence_valid") is True:
                    mention_current_exact_valid += 1

        if not evidence_strings:
            grade_counts[EvidenceGrade.EMPTY] += 1
            if len(samples[EvidenceGrade.EMPTY]) < sample_limit:
                samples[EvidenceGrade.EMPTY].append("<no evidence strings extracted>")
            continue

        row_strings_grounded = True
        for evidence in evidence_strings:
            grade = grade_evidence_string(note_text, evidence)
            grade_counts[grade.value] += 1
            if grade != EvidenceGrade.EXACT:
                exact_invalid_counts[grade.value] += 1
            if not is_grounded(grade):
                row_strings_grounded = False
            if len(samples[grade.value]) < sample_limit:
                samples[grade.value].append(_truncate(evidence))

        if row_strings_grounded:
            row_all_strings_grounded += 1

        if all(
            is_grounded(grade_evidence_string(note_text, evidence))
            for evidence in evidence_strings
        ):
            row_grounded_after_repair += 1

    total_strings = sum(grade_counts.values())
    exact_strings = grade_counts[EvidenceGrade.EXACT]
    grounded_strings = sum(grade_counts[grade.value] for grade in GROUNDED_GRADES)
    exact_invalid_total = total_strings - exact_strings
    recoverable_invalid = sum(
        grade_counts[grade.value]
        for grade in GROUNDED_GRADES
        if grade != EvidenceGrade.EXACT
    )
    genuine_invalid = grade_counts[EvidenceGrade.ABSENT] + grade_counts[EvidenceGrade.EMPTY]

    return {
        "run_id": target.run_id,
        "task": target.task,
        "model_label": target.model_label,
        "pipeline_family": target.pipeline_family,
        "split": target.split,
        "source": target.source,
        "rows_path": target.rows_path.as_posix(),
        "gan_pipeline": pipeline if target.task == "gan2026" else None,
        "row_count": row_total,
        "evidence_string_count": total_strings,
        "grade_counts": dict(sorted(grade_counts.items())),
        "exact_rate": _rate(exact_strings, total_strings),
        "grounded_rate": _rate(grounded_strings, total_strings),
        "row_exact_valid_rate": _rate(row_current_exact_valid, row_total)
        if target.task == "gan2026"
        else _rate(mention_current_exact_valid, mention_total),
        "row_grounded_rate": _rate(row_all_strings_grounded, row_total),
        "row_grounded_after_repair_rate": _rate(row_grounded_after_repair, row_total),
        "current_invalid_rows": row_current_exact_invalid if target.task == "gan2026" else None,
        "current_invalid_mentions": mention_total - mention_current_exact_valid
        if target.task == "exectv2"
        else None,
        "exact_invalid_split": {
            "total_exact_invalid_strings": exact_invalid_total,
            "recoverable_repaired": recoverable_invalid,
            "genuine_absent_or_empty": genuine_invalid,
            "recoverable_share_of_exact_invalid": _rate(recoverable_invalid, exact_invalid_total),
            "by_grade": {
                grade.value: exact_invalid_counts[grade.value]
                for grade in ALL_GRADES
                if grade != EvidenceGrade.EXACT and exact_invalid_counts[grade.value]
            },
        },
        "samples_by_grade": {grade: samples[grade.value] for grade in ALL_GRADES if samples[grade.value]},
        "row_missing_current_flag": row_missing_current_flag,
    }


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 4)


def _truncate(text: str, limit: int = 120) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1] + "…"


def run_audit(*, sample_limit: int = 5) -> dict[str, Any]:
    entries = load_run_registry(REGISTRY_PATH)
    targets = build_registry_targets(entries) + build_exectv2_catalog_targets()
    gan_notes = _gan_note_text_by_index()
    exect_notes = _exect_note_text_by_letter()

    run_results = [
        audit_target(
            target,
            gan_notes=gan_notes,
            exect_notes=exect_notes,
            sample_limit=sample_limit,
        )
        for target in targets
    ]

    gan_results = [result for result in run_results if result["task"] == "gan2026"]
    exect_results = [result for result in run_results if result["task"] == "exectv2"]
    qwen_gan = [
        result
        for result in gan_results
        if "qwen" in result["run_id"].lower() or "qwen" in result["model_label"].lower()
    ]

    return {
        "date": "2026-06-27",
        "phase": "Phase 0 — read-only taxonomy audit",
        "model_calls": 0,
        "targets_audited": len(run_results),
        "gan2026_runs": gan_results,
        "exectv2_runs": exect_results,
        "headline": _headline(qwen_gan, gan_results, exect_results),
    }


def _headline(
    qwen_gan: Sequence[Mapping[str, Any]],
    gan_results: Sequence[Mapping[str, Any]],
    exect_results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    qwen_hybrid = next(
        (
            row
            for row in qwen_gan
            if row.get("gan_pipeline") == "hybrid" and "three_way" in row["run_id"]
        ),
        None,
    )
    qwen_llm = next(
        (
            row
            for row in qwen_gan
            if row.get("gan_pipeline") == "llm_only" and "three_way" in row["run_id"]
        ),
        None,
    )
    return {
        "qwen_hybrid_row_exact_valid_rate": qwen_hybrid.get("row_exact_valid_rate") if qwen_hybrid else None,
        "qwen_hybrid_grounded_rate": qwen_hybrid.get("grounded_rate") if qwen_hybrid else None,
        "qwen_hybrid_recoverable_share_of_exact_invalid": (
            (qwen_hybrid.get("exact_invalid_split") or {}).get("recoverable_share_of_exact_invalid")
            if qwen_hybrid
            else None
        ),
        "qwen_llm_row_exact_valid_rate": qwen_llm.get("row_exact_valid_rate") if qwen_llm else None,
        "qwen_llm_grounded_rate": qwen_llm.get("grounded_rate") if qwen_llm else None,
        "qwen_llm_recoverable_share_of_exact_invalid": (
            (qwen_llm.get("exact_invalid_split") or {}).get("recoverable_share_of_exact_invalid")
            if qwen_llm
            else None
        ),
        "gan_run_count": len(gan_results),
        "exect_run_count": len(exect_results),
    }


def render_markdown(payload: Mapping[str, Any]) -> str:
    lines: list[str] = [
        "# Evidence Validity Audit — Phase 0 Before Picture",
        "",
        f"Date: {payload['date']}  ·  Model calls: {payload['model_calls']} (replay-only)",
        "",
        "Read-only taxonomy audit over saved artifacts. Current validity uses the "
        "existing raw substring metric (`evidence_valid` / `evidence_text_contained` "
        "at row level for gan2026; mention-level `evidence_valid` for ExECTv2). "
        "Grounded rate applies the existing repair cascade from `core/evidence.py` "
        "without changing any call site.",
        "",
        "## Headline",
        "",
    ]
    headline = payload["headline"]
    lines.extend(
        [
            _headline_line(
                "Qwen hybrid (validation750 surfaced row)",
                headline.get("qwen_hybrid_row_exact_valid_rate"),
                headline.get("qwen_hybrid_grounded_rate"),
                headline.get("qwen_hybrid_recoverable_share_of_exact_invalid"),
            ),
            _headline_line(
                "Qwen LLM-only (validation750 surfaced row)",
                headline.get("qwen_llm_row_exact_valid_rate"),
                headline.get("qwen_llm_grounded_rate"),
                headline.get("qwen_llm_recoverable_share_of_exact_invalid"),
            ),
            "",
            "The Qwen gap is overwhelmingly recoverable formatting (`REPAIRED_*`, "
            "especially artifact normalisation for `≤` copy quirks), not absent "
            "evidence — the current metric penalises grounded copy fidelity.",
            "",
        ]
    )

    lines.append("## gan2026")
    lines.extend(_render_task_section(payload["gan2026_runs"], granularity="row"))
    lines.append("## ExECTv2")
    lines.extend(_render_task_section(payload["exectv2_runs"], granularity="mention"))

    lines.extend(
        [
            "",
            "---",
            "",
            "Generated by `experiments/build_evidence_validity_audit.py` (Phase 0). "
            "Phase 1 will promote `grade_evidence` into `core/evidence.py`; Phases 2–4 "
            "replace call sites and replay the unified metric.",
            "",
        ]
    )
    return "\n".join(lines)


def _headline_line(
    label: str,
    exact_rate: float | None,
    grounded_rate: float | None,
    recoverable_share: float | None,
) -> str:
    exact_pct = _fmt_pct(exact_rate)
    grounded_pct = _fmt_pct(grounded_rate)
    recoverable_pct = _fmt_pct(recoverable_share)
    return (
        f"- **{label}:** exact {exact_pct} → grounded {grounded_pct}; "
        f"{recoverable_pct} of exact-invalid strings are recoverable `REPAIRED_*`."
    )


def _render_task_section(
    runs: Sequence[Mapping[str, Any]],
    *,
    granularity: Literal["row", "mention"],
) -> list[str]:
    lines: list[str] = [""]
    for run in runs:
        split = run["exact_invalid_split"]
        lines.extend(
            [
                f"### `{run['run_id']}`",
                "",
                f"- Model: {run['model_label']}",
                f"- Pipeline: `{run['pipeline_family']}` · split `{run['split']}` · source `{run['source']}`",
                f"- Artifact: `{run['rows_path']}`",
                f"- Audited {run['row_count']} rows · {run['evidence_string_count']} evidence strings",
                f"- Current exact-valid rate ({granularity}): {_fmt_pct(run['row_exact_valid_rate'])}",
                f"- Grounded rate (all extracted strings): {_fmt_pct(run['grounded_rate'])}",
                f"- Exact-only string rate: {_fmt_pct(run['exact_rate'])}",
                "",
                "| Grade | Count |",
                "|---|---:|",
            ]
        )
        for grade in ALL_GRADES:
            count = (run.get("grade_counts") or {}).get(grade.value, 0)
            if count:
                lines.append(f"| `{grade.value}` | {count} |")
        lines.extend(
            [
                "",
                "**Exact-invalid split** (strings failing raw substring today):",
                "",
                f"- Exact-invalid strings: {split['total_exact_invalid_strings']}",
                f"- Recoverable `REPAIRED_*`: {split['recoverable_repaired']} "
                f"({_fmt_pct(split['recoverable_share_of_exact_invalid'])} of exact-invalid)",
                f"- Genuine `ABSENT`/`EMPTY`: {split['genuine_absent_or_empty']}",
                "",
                "**Samples (up to 5 per grade)**",
                "",
            ]
        )
        samples = run.get("samples_by_grade") or {}
        for grade in ALL_GRADES:
            grade_samples = samples.get(grade.value) or []
            if not grade_samples:
                continue
            lines.append(f"- `{grade.value}`:")
            for sample in grade_samples:
                lines.append(f"  - \"{sample}\"")
        lines.append("")
    return lines


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def write_report(*, sample_limit: int = 5) -> tuple[Path, Path]:
    payload = run_audit(sample_limit=sample_limit)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    return OUT_JSON, OUT_MD
