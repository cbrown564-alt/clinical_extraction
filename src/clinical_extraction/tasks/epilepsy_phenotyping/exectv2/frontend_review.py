"""Build the ExECTv2 frontend review payload from the final artifact index.

This module is the single source of truth for the ExECTv2 frontend dataset. Both
the static generator (``scripts/build_exectv2_frontend_mock_data.py``) and the
live observatory API route (``GET /exectv2/runs``) call into it, so the served
data and the committed dev fallback can never drift.

The run set is parsed directly from the canonical
``docs/experiments/final_artifact_index_*.md`` rather than a hardcoded list: each
``### ExECTv2 …`` section under ``## Canonical Artifact Groups`` maps its
``| Field | Value |`` table onto a run spec, which is then rendered into the same
per-letter review payload the frontend consumes. Non-ExECTv2 and non-canonical
sections are ignored.
"""

from __future__ import annotations

import json
import re
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    headline_duplicate_tags,
)


def _find_repo_root() -> Path:
    """Walk up from this module to the directory holding ``pyproject.toml``."""
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    # Fallback: src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/<file>
    return here.parents[5]


REPO_ROOT = _find_repo_root()

FAMILIES = ["Diagnosis", "SeizureFrequency", "Prescription", "Investigations"]

PIPELINE_FAMILY = "exectv2_holistic_finding_assembly"
INDEX_DIR = REPO_ROOT / "docs" / "experiments"
INDEX_GLOB = "final_artifact_index_*.md"

# Canonical letter-text sources per split. The Field/Value tables for the v08 and
# v09 controls do not list a "Source JSONL", and a model-specific source may omit
# ``letter_text``, so these guarantee the renderer can always recover letter text.
FALLBACK_TEXT_SOURCES: dict[str, list[str]] = {
    "dev140": [
        "experiments/exectv2_llm_only_key_entities_structured_v09_dev140_gpt41mini_20260621.jsonl",
    ],
}


# ── Index parsing ─────────────────────────────────────────────────────

_H2 = re.compile(r"^##\s+(.*\S)\s*$")
_H3 = re.compile(r"^###\s+(.*\S)\s*$")
_TABLE_ROW = re.compile(r"^\|(.*)\|\s*$")


def find_index_path() -> Path:
    """Return the newest ``final_artifact_index_*.md`` (ISO date sorts last)."""
    candidates = sorted(INDEX_DIR.glob(INDEX_GLOB))
    if not candidates:
        raise FileNotFoundError(f"No {INDEX_GLOB} found under {INDEX_DIR}")
    return candidates[-1]


def index_date(path: Path) -> str:
    match = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
    return match.group(1) if match else date.today().isoformat()


def _first_backtick(text: str | None) -> str | None:
    match = re.search(r"`([^`]+)`", text or "")
    return match.group(1).strip() if match else None


def _strip_backticks(text: str | None) -> str:
    return (text or "").replace("`", "").strip()


def _parse_field_table(lines: list[str]) -> dict[str, str]:
    """Parse the first ``| Field | Value |`` table in a section's lines.

    Stops at the first non-table line so the trailing ``| Path | SHA-256 |``
    hashes table is never folded into the fields.
    """
    fields: dict[str, str] = {}
    in_table = False
    for line in lines:
        match = _TABLE_ROW.match(line.strip())
        if not match:
            if in_table:
                break
            continue
        cells = [cell.strip() for cell in match.group(1).split("|")]
        if not in_table:
            if len(cells) >= 2 and cells[0].lower() == "field" and cells[1].lower() == "value":
                in_table = True
            continue
        # Skip the markdown separator row (e.g. | --- | --- |).
        if set("".join(cells)) <= set("-: "):
            continue
        if len(cells) >= 2:
            fields[cells[0]] = cells[1]
    return fields


def _decision_from_heading(heading: str) -> str:
    lowered = heading.lower()
    if "diagnostic" in lowered:
        return "diagnostic"
    if "simplification" in lowered:
        return "simplification"
    if "control" in lowered:
        return "control"
    return "diagnostic"


def _model_from_cell(cell: str) -> str:
    backtick = _first_backtick(cell)
    if backtick:
        return backtick
    if "gpt-4.1-mini" in cell.lower():
        return "openai/gpt-4.1-mini"
    return cell.strip()


def _promotion_slug(cell: str) -> str:
    lowered = cell.lower()
    # Check the more specific phrase first: "Simplicity control, not performance
    # control" must resolve to simplicity, not performance.
    if "simplicity control" in lowered:
        return "simplicity-control"
    if "performance control" in lowered:
        return "performance-control"
    if "diagnostic comparator" in lowered:
        return "diagnostic-comparator"
    if "do not promote" in lowered:
        return "do-not-promote"
    words = re.findall(r"[a-z0-9]+", lowered)
    return "-".join(words[:4]) or "unspecified"


def _humanize_boundary(value: str) -> str:
    text = _strip_backticks(value)
    # Diagnostic claim boundaries are kebab slugs; controls are prose.
    if text and " " not in text:
        text = text.replace("-", " ").replace("_", " ")
    return text


def _architecture_family(run_id: str, split: str) -> str:
    core = re.sub(r"^exectv2_holistic_finding_assembly_?", "", run_id)
    core = re.sub(rf"_?{re.escape(split)}$", "", core)
    core = re.sub(r"^v\d+_?", "", core)
    core = core.strip("_")
    return core or "holistic_finding_assembly"


def _split_from_cell(cell: str) -> str:
    backtick = _first_backtick(cell)
    if backtick:
        return backtick
    match = re.search(r"dev\d+", cell or "")
    return match.group(0) if match else ""


def _fields_to_spec(heading: str, fields: dict[str, str]) -> dict[str, Any] | None:
    run_id = _first_backtick(fields.get("Candidate", ""))
    if not run_id:
        # Prose Candidate (e.g. the Gan package) is not a renderable run.
        return None

    split = _split_from_cell(fields.get("Split and row count", ""))
    source_jsonl = _first_backtick(fields.get("Source JSONL", "")) if "Source JSONL" in fields else None
    text_sources: list[str] = []
    if source_jsonl:
        text_sources.append(source_jsonl)
    text_sources.extend(FALLBACK_TEXT_SOURCES.get(split, []))

    return {
        "run_id": run_id,
        "label": re.sub(r"^ExECTv2\s+", "", heading).strip(),
        "model": _model_from_cell(fields.get("Model", "")),
        "architecture_family": _architecture_family(run_id, split),
        "pipeline_family": PIPELINE_FAMILY,
        "split": split,
        "decision": _decision_from_heading(heading),
        "promotion_decision": _promotion_slug(fields.get("Promotion decision", "")),
        "claim_boundary": _humanize_boundary(fields.get("Claim boundary", "")),
        "scorer_view": _first_backtick(fields.get("Scorer/view", "")) or "headline_target",
        "config_path": _first_backtick(fields.get("Config", "")),
        "report_path": _first_backtick(fields.get("Report", "")),
        "summary_path": _first_backtick(fields.get("JSON", "")),
        "assembly_jsonl_path": _first_backtick(fields.get("JSONL", "")),
        "text_source_paths": text_sources,
    }


def parse_canonical_exectv2_runs(md_text: str) -> list[dict[str, Any]]:
    """Extract run specs from every canonical ``### ExECTv2 …`` section."""
    lines = md_text.splitlines()
    current_h2: str | None = None
    runs: list[dict[str, Any]] = []
    i = 0
    while i < len(lines):
        h2 = _H2.match(lines[i])
        if h2:
            current_h2 = h2.group(1)
            i += 1
            continue
        h3 = _H3.match(lines[i])
        if h3:
            heading = h3.group(1)
            j = i + 1
            section: list[str] = []
            while j < len(lines) and not _H2.match(lines[j]) and not _H3.match(lines[j]):
                section.append(lines[j])
                j += 1
            if current_h2 == "Canonical Artifact Groups" and heading.startswith("ExECTv2"):
                spec = _fields_to_spec(heading, _parse_field_table(section))
                if spec:
                    runs.append(spec)
            i = j
            continue
        i += 1
    return runs


def load_run_specs_from_index(index_path: Path) -> list[dict[str, Any]]:
    return parse_canonical_exectv2_runs(index_path.read_text(encoding="utf-8"))


def _spec_artifacts_exist(spec: dict[str, Any]) -> bool:
    for key in ("summary_path", "assembly_jsonl_path"):
        value = spec.get(key)
        if not value or not (REPO_ROOT / value).exists():
            return False
    return True


def validate_specs(specs: list[dict[str, Any]]) -> None:
    """Fail loudly (with the offending run/field) if the index points nowhere."""
    errors: list[str] = []
    for spec in specs:
        for key in ("summary_path", "assembly_jsonl_path"):
            value = spec.get(key)
            if not value:
                errors.append(f"{spec['run_id']}: index is missing {key}")
            elif not (REPO_ROOT / value).exists():
                errors.append(f"{spec['run_id']}: {key} not found on disk: {value}")
    if errors:
        raise SystemExit("Index references missing ExECTv2 artifacts:\n  - " + "\n  - ".join(errors))


# ── Rendering ─────────────────────────────────────────────────────────


def load_json(path: str) -> dict[str, Any]:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def load_jsonl(path: str) -> list[dict[str, Any]]:
    full_path = REPO_ROOT / path
    return [
        json.loads(line)
        for line in full_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def extract_letter_texts(paths: list[str]) -> dict[str, str]:
    texts: dict[str, str] = {}
    for path in paths:
        full_path = REPO_ROOT / path
        if not full_path.exists():
            continue
        for row in load_jsonl(path):
            letter_id = str(row.get("letter_id", ""))
            if not letter_id or letter_id in texts:
                continue
            prompt_input = row.get("prompt_input_json")
            if isinstance(prompt_input, str):
                try:
                    prompt_input = json.loads(prompt_input)
                except json.JSONDecodeError:
                    prompt_input = {}
            if isinstance(prompt_input, dict) and isinstance(prompt_input.get("letter_text"), str):
                texts[letter_id] = prompt_input["letter_text"]
    return texts


def simplify_attributes(attributes: Any) -> dict[str, str]:
    if not isinstance(attributes, dict):
        return {}
    result: dict[str, str] = {}
    for key, value in attributes.items():
        if value is None:
            continue
        if isinstance(value, (str, int, float, bool)):
            result[str(key)] = str(value)
    return result


def simplify_mention(mention: dict[str, Any], fallback_id: str, source: str) -> dict[str, Any]:
    return {
        "id": str(mention.get("finding_id") or mention.get("mention_id") or fallback_id),
        "source": source,
        "entity": str(mention.get("entity") or "Unknown"),
        "text": str(mention.get("text") or ""),
        "evidence": str(mention.get("evidence") or mention.get("text") or ""),
        "evidence_valid": bool(mention.get("evidence_valid", True)),
        "component_owner": str(mention.get("component_owner") or ""),
        "source_lane": str(mention.get("source_lane") or mention.get("lane") or ""),
        "source_model": str(mention.get("source_model") or ""),
        "confidence": str(mention.get("confidence") or ""),
        "assertion": str(mention.get("assertion") or ""),
        "attributes": simplify_attributes(mention.get("attributes")),
        "status": source,
        # Set by apply_headline_status(): "deduplicated" | "distinct_assertion" | "".
        "headline_status": "",
    }


def evidence_spans(letter_text: str, mentions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    seen: set[tuple[int, int, str, str]] = set()
    for mention in mentions:
        evidence = str(mention.get("evidence") or mention.get("text") or "").strip()
        if not evidence:
            continue
        start = letter_text.find(evidence)
        if start < 0:
            start = letter_text.lower().find(evidence.lower())
        if start < 0:
            continue
        end = start + len(evidence)
        key = (start, end, str(mention.get("entity")), str(mention.get("source")))
        if key in seen:
            continue
        seen.add(key)
        spans.append(
            {
                "start": start,
                "end": end,
                "text": letter_text[start:end],
                "entity": mention.get("entity"),
                "kind": "gold" if mention.get("source") == "gold" else "llm",
                "label": f"{mention.get('source')} {mention.get('entity')}",
            }
        )
    return sorted(spans, key=lambda span: (span["start"], span["end"]))


def family_counts(mentions: list[dict[str, Any]]) -> dict[str, int]:
    """Per-family counts against the clinical-recovery headline unit.

    Mentions the headline de-duplicates away (``headline_status ==
    "deduplicated"``) are excluded so the family tabs agree with the headline
    chips instead of the raw mention multiset. Distinct-assertion duplicates are
    still counted — the headline counts them per occurrence.
    """
    counts = {family: 0 for family in FAMILIES}
    for mention in mentions:
        if mention.get("headline_status") == "deduplicated":
            continue
        entity = str(mention.get("entity") or "")
        if entity in counts:
            counts[entity] += 1
    return counts


def _annotation_from_mention(mention: dict[str, Any]) -> ExectAnnotation:
    return ExectAnnotation(
        entity=str(mention.get("entity") or "Unknown"),
        text=str(mention.get("text") or ""),
        attributes={
            str(key): str(value)
            for key, value in dict(mention.get("attributes") or {}).items()
        },
    )


def apply_headline_status(mentions: list[dict[str, Any]], note_text: str) -> None:
    """Tag each simplified mention with how the headline treats its scoring unit.

    Sets ``headline_status`` to ``"deduplicated"`` (a Redundant-Convention
    Duplicate the headline collapses), ``"distinct_assertion"`` (a
    Distinct-Assertion Duplicate the headline counts per occurrence), or ``""``.
    Keying is delegated to ``scoring.headline_duplicate_tags`` so the surface never
    re-implements the per-family headline keys.
    """
    annotations = [_annotation_from_mention(mention) for mention in mentions]
    tags = headline_duplicate_tags(annotations, note_text)
    for mention, tag in zip(mentions, tags):
        mention["headline_status"] = tag or ""


def metrics_from_summary(summary: dict[str, Any]) -> dict[str, Any]:
    headline = summary.get("score_ladder", {}).get("headline_target", {})
    overall = headline.get("overall", {})
    by_indicator = headline.get("by_indicator", {})
    return {
        "overall_f1": overall.get("f1"),
        "precision": overall.get("precision"),
        "recall": overall.get("recall"),
        "families": {
            family: {
                "f1": by_indicator.get(family, {}).get("f1"),
                "precision": by_indicator.get(family, {}).get("precision"),
                "recall": by_indicator.get(family, {}).get("recall"),
                "tp": by_indicator.get(family, {}).get("tp"),
                "fp": by_indicator.get(family, {}).get("fp"),
                "fn": by_indicator.get(family, {}).get("fn"),
            }
            for family in FAMILIES
        },
    }


def operational_from_summary(summary: dict[str, Any]) -> dict[str, Any]:
    diagnostics = summary.get("lane_diagnostics", {})
    exact_rates = [
        float(value.get("exact_evidence_rate", 0.0))
        for value in diagnostics.values()
        if isinstance(value, dict)
    ]
    return {
        "call_failures": max(
            [int(value.get("call_failures", 0)) for value in diagnostics.values() if isinstance(value, dict)]
            or [0]
        ),
        "parse_schema_failures": max(
            [
                int(value.get("parse_schema_failures", 0))
                for value in diagnostics.values()
                if isinstance(value, dict)
            ]
            or [0]
        ),
        "evidence_invalid_dropped": sum(
            int(value.get("evidence_invalid_dropped", 0))
            for value in diagnostics.values()
            if isinstance(value, dict)
        ),
        "exact_evidence_rate": min(exact_rates) if exact_rates else None,
        "by_family": diagnostics,
    }


def build_run(spec: dict[str, Any]) -> dict[str, Any]:
    summary = load_json(spec["summary_path"])
    rows = load_jsonl(spec["assembly_jsonl_path"])
    letter_texts = extract_letter_texts(spec["text_source_paths"])

    letters: list[dict[str, Any]] = []
    for row in rows:
        letter_id = str(row.get("letter_id") or "")
        gold_mentions = [
            simplify_mention(mention, f"{letter_id}:gold:{index}", "gold")
            for index, mention in enumerate(row.get("gold_mentions") or [])
        ]
        predicted_mentions = [
            simplify_mention(mention, f"{letter_id}:predicted:{index}", "predicted")
            for index, mention in enumerate(row.get("predicted_mentions") or [])
        ]
        letter_text = letter_texts.get(letter_id) or "\n\n".join(
            mention["evidence"]
            for mention in predicted_mentions
            if mention.get("evidence")
        )
        apply_headline_status(gold_mentions, letter_text)
        apply_headline_status(predicted_mentions, letter_text)
        all_mentions = gold_mentions + predicted_mentions
        letters.append(
            {
                "letter_id": letter_id,
                "split": row.get("split", "dev"),
                "stage": row.get("stage", spec["split"]),
                "letter_text": letter_text,
                "gold_mentions": gold_mentions,
                "predicted_mentions": predicted_mentions,
                "family_counts": {
                    "gold": family_counts(gold_mentions),
                    "predicted": family_counts(predicted_mentions),
                },
                "evidence_spans": evidence_spans(letter_text, all_mentions),
            }
        )

    return {
        "run_id": spec["run_id"],
        "task": "exectv2",
        "label": spec["label"],
        "model": spec["model"],
        "architecture_family": spec["architecture_family"],
        "pipeline_family": spec["pipeline_family"],
        "split": spec["split"],
        "row_count": summary.get("row_count", len(rows)),
        "date": summary.get("generated_on", "2026-06-22"),
        "decision": spec["decision"],
        "promotion_decision": spec["promotion_decision"],
        "claim_boundary": spec["claim_boundary"],
        "scorer_view": spec["scorer_view"],
        "artifact_paths": [
            path
            for path in [
                spec.get("config_path"),
                spec.get("report_path"),
                spec.get("summary_path"),
                spec.get("assembly_jsonl_path"),
            ]
            if path
        ],
        "source_paths": spec["text_source_paths"],
        "metrics": metrics_from_summary(summary),
        "operational": operational_from_summary(summary),
        "letters": letters,
    }


def build_exectv2_runs(*, strict: bool) -> tuple[Path, list[dict[str, Any]]]:
    """Resolve the index and render every renderable canonical run.

    ``strict`` (used by the static generator) fails loudly via
    :func:`validate_specs` when the index points at missing artifacts. The live
    API uses ``strict=False`` so a partially-synced checkout still serves the
    runs whose artifacts are present rather than erroring the whole surface.
    """
    index_path = find_index_path()
    specs = load_run_specs_from_index(index_path)
    if not specs:
        raise FileNotFoundError(f"No canonical ExECTv2 runs found in {index_path}")
    if strict:
        validate_specs(specs)
        usable = specs
    else:
        usable = [spec for spec in specs if _spec_artifacts_exist(spec)]
    return index_path, [build_run(spec) for spec in usable]


def build_exectv2_runs_payload(*, strict: bool = False) -> dict[str, Any]:
    """The full ``{generated_on, source_index, runs}`` payload the frontend reads."""
    index_path, runs = build_exectv2_runs(strict=strict)
    return {
        "generated_on": index_date(index_path),
        "source_index": index_path.relative_to(REPO_ROOT).as_posix(),
        "runs": runs,
    }


@lru_cache(maxsize=1)
def cached_exectv2_runs_payload() -> dict[str, Any]:
    """Process-cached payload for the live API (read-only; rebuilt on restart)."""
    return build_exectv2_runs_payload(strict=False)


@lru_cache(maxsize=1)
def cached_exectv2_runs_json() -> str:
    """Process-cached serialized payload — the multi-MB body is encoded once."""
    return json.dumps(cached_exectv2_runs_payload(), ensure_ascii=False)


# Re-exports for observatory cached report routes (stable facade surface).
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation_replay import (  # noqa: E402,E501
    cached_component_ablation_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_transition_examples import (  # noqa: E402,E501
    cached_component_transitions_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.final_consolidation import (  # noqa: E402
    cached_reliability_scorecard_json,
)

__all__ = [
    "cached_component_ablation_json",
    "cached_component_transitions_json",
    "cached_exectv2_runs_json",
    "cached_exectv2_runs_payload",
    "cached_reliability_scorecard_json",
]
