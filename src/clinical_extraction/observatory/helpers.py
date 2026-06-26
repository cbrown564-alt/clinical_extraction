"""Shared helper functions for Observatory routers."""

from __future__ import annotations

import importlib
import inspect
import json
import os
import subprocess
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel

from clinical_extraction.observatory.models import (
    EXECUTABLE_PIPELINES,
    ObservatorySettings,
    RunNoteRequest,
    TEMPORAL_SELECTION_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord, load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.cluster import (
    CLUSTER_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.diary import (
    DIARY_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.gan_shorthand import (
    GAN_SHORTHAND_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.rate import (
    PORTABLE_RATE_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.seizure_free import (
    SEIZURE_FREE_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import RuleSpec
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.core.registry import (
    load_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_surfacing import (
    load_surfaced_runs_from_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import BENCHMARK_REPAIR_RULES


def discover_repo_root() -> Path:
    for candidate in (Path.cwd(), *Path.cwd().parents, Path(__file__).resolve().parents[5:6]):
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    return Path.cwd()


def resolve_under_root(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def safe_repo_path(repo_root: Path, relative_path: str) -> Path:
    path = Path(relative_path)
    if path.is_absolute() or ".." in path.parts:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid repository-relative path: {relative_path}",
        )
    resolved = (repo_root / path).resolve()
    if repo_root not in (resolved, *resolved.parents):
        raise HTTPException(status_code=400, detail=f"Path escapes repository: {relative_path}")
    return resolved


def relative_to_root(settings: ObservatorySettings, path: Path) -> str:
    try:
        return str(path.relative_to(settings.repo_root))
    except ValueError:
        return str(path)


def request_record(request: RunNoteRequest) -> GanRecord:
    gold_label = request.gold_label.strip() or "unknown"
    try:
        gold_record = label_to_frequency_record(gold_label)
    except ValueError:
        gold_record = label_to_frequency_record("unknown")
    return GanRecord(
        source_row_index=request.source_row_index,
        note_text=request.note_text,
        gold_label=gold_record.normalized_label,
        gold_reference=request.gold_reference,
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={"source": "observatory_run_note"},
    )


def require_supported_pipeline(pipeline: str) -> None:
    if pipeline not in EXECUTABLE_PIPELINES:
        raise HTTPException(
            status_code=400,
            detail=f"Pipeline {pipeline!r} is not yet executable via the Observatory API. "
            f"Supported: {sorted(EXECUTABLE_PIPELINES)}.",
        )


def load_split_records(settings: ObservatorySettings, split: str) -> Sequence[Any]:
    try:
        return load_records_for_split(
            split,
            data_path=settings.data_path,
            manifest_path=settings.split_manifest_path,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def registry_entry(settings: ObservatorySettings, run_id: str) -> Any:
    for entry in load_run_registry(settings.registry_path):
        if entry.run_id == run_id:
            return entry
    raise HTTPException(status_code=404, detail=f"Unknown run_id: {run_id}")


def select_artifact_paths(
    repo_root: Path,
    paths: Sequence[str],
    split: str | None,
    requested: str | None,
) -> list[str]:
    if requested is not None:
        if requested not in paths:
            raise HTTPException(
                status_code=404,
                detail=f"Run does not reference artifact: {requested}",
            )
        return [requested]

    jsonl_paths = [p for p in paths if Path(p).suffix == ".jsonl"]
    if not jsonl_paths:
        return []

    if split and "+" in split and "test" in split:
        return jsonl_paths

    def _file_size(path: str) -> int:
        try:
            return os.path.getsize(safe_repo_path(repo_root, path))
        except Exception:
            return 0

    largest = max(jsonl_paths, key=_file_size)
    return [largest]


def load_artifact_content(path: Path, *, limit: int | None) -> Any:
    if path.suffix == ".jsonl":
        rows = load_jsonl_rows(path)
        return rows[:limit] if limit is not None else rows
    if path.suffix == ".json":
        content = json.loads(path.read_text(encoding="utf-8"))
        if limit is not None and isinstance(content, list):
            return content[:limit]
        return content
    return {"text": path.read_text(encoding="utf-8")}


def all_rule_specs() -> tuple[RuleSpec, ...]:
    return (
        *PORTABLE_RATE_RULES,
        *CLUSTER_RULES,
        *DIARY_RULES,
        *SEIZURE_FREE_RULES,
        *GAN_SHORTHAND_RULES,
        *TEMPORAL_SELECTION_RULES,
        *BENCHMARK_REPAIR_RULES,
    )


def rule_payload(spec: RuleSpec) -> dict[str, Any]:
    return {
        "rule_id": spec.rule_id,
        "group": spec.group.value,
        "portability": spec.portability.value,
        "description": spec.description,
        "regex_preview": spec.pattern.pattern,
        "provenance": spec.provenance,
        "examples": [rule_example_payload(example) for example in spec.examples],
        "has_exclusions": bool(spec.exclude),
    }


def rule_example_payload(example: Any) -> dict[str, Any]:
    return {
        "text": example.text,
        "expected_label": example.expected_label,
        "expected_evidence": example.expected_evidence,
        "anti_example": example.anti_example,
        "note": example.note,
    }


def prompt_payload(module_name: str) -> dict[str, Any]:
    module = importlib.import_module(module_name)
    prompt_version = getattr(module, "PROMPT_VERSION", module_name.rsplit(".", maxsplit=1)[-1])
    taxonomy = getattr(module, "PROMPT_POLICY_TAXONOMY", [])
    return {
        "module": module_name,
        "prompt_version": prompt_version,
        "policy_taxonomy": jsonable_mapping_sequence(taxonomy),
        "policy_ids": [
            str(policy["policy_id"])
            for policy in taxonomy
            if isinstance(policy, Mapping) and "policy_id" in policy
        ],
    }


def build_pipeline_families(settings: ObservatorySettings) -> list[dict[str, Any]]:
    return load_surfaced_runs_from_registry(settings.registry_path)


def jsonable_mapping_sequence(items: Iterable[Any]) -> list[dict[str, Any]]:
    payload = []
    for item in items:
        if isinstance(item, Mapping):
            payload.append({str(key): value for key, value in item.items()})
    return payload


_CATEGORY_MAGNITUDE: dict[str, int] = {
    "currently_no_seizure": 0,
    "seizure_freq_unknown": 0,
    "seizure_freq_1_per_yr": 1,
    "seizure_freq_1_per_6mon": 2,
    "seizure_freq_more1per6mon_less1mon": 3,
    "seizure_freq_1_per_mon": 4,
    "seizure_freq_more1mon_less1week": 5,
    "seizure_freq_1_per_week": 6,
    "seizure_freq_more1week_less1day": 7,
    "seizure_freq_1ormore_daily": 8,
    "seizure_infrequent": 1,
    "seizure_frequent": 8,
}


def category_magnitude(cat: str) -> int:
    return _CATEGORY_MAGNITUDE.get(cat, 0)


def classify_error(
    gold_category: str,
    predicted_category: str,
    purist_correct: bool,
) -> dict[str, Any]:
    if purist_correct:
        return {"error_type": "correct", "severity": 0, "severity_level": "none"}

    gold_mag = category_magnitude(gold_category)
    pred_mag = category_magnitude(predicted_category)
    severity = abs(pred_mag - gold_mag)

    if gold_mag > 0 and pred_mag == 0:
        error_type = "false_negative"
    elif gold_mag == 0 and pred_mag > 0:
        error_type = "false_positive"
    elif pred_mag > gold_mag:
        error_type = "near_miss" if pred_mag - gold_mag == 1 else "over_estimate"
    elif pred_mag < gold_mag:
        error_type = "near_miss" if gold_mag - pred_mag == 1 else "under_estimate"
    else:
        error_type = "near_miss"

    if severity == 0:
        severity_level = "none"
    elif severity == 1:
        severity_level = "near"
    elif severity <= 3:
        severity_level = "moderate"
    elif severity <= 5:
        severity_level = "significant"
    else:
        severity_level = "severe"

    return {"error_type": error_type, "severity": severity, "severity_level": severity_level}


def prompt_template_payload(module_name: str) -> dict[str, Any]:
    module = importlib.import_module(module_name)
    prompt_version = getattr(module, "PROMPT_VERSION", module_name.rsplit(".", maxsplit=1)[-1])
    taxonomy = getattr(module, "PROMPT_POLICY_TAXONOMY", [])

    system_hint: str | None = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and hasattr(attr, "__mro__"):
            if any(hasattr(base, "fields") for base in attr.__mro__ if base is not object):
                doc = inspect.getdoc(attr)
                if doc and len(doc) > 20:
                    system_hint = doc
                    break

    user_hint: str | None = None
    build_fn = getattr(module, "build_prompt_input", None)
    if build_fn is not None:
        user_hint = inspect.getdoc(build_fn)

    output_schema_hint: str | None = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and issubclass(attr, BaseModel) and "Record" in attr_name:
            doc = inspect.getdoc(attr)
            if doc and len(doc) > 10:
                output_schema_hint = doc
                break

    build_sig: str | None = None
    if build_fn is not None:
        try:
            build_sig = str(inspect.signature(build_fn))
        except Exception:
            build_sig = None

    return {
        "module": module_name,
        "prompt_version": prompt_version,
        "system_hint": system_hint,
        "user_hint": user_hint,
        "output_schema_hint": output_schema_hint,
        "build_prompt_signature": build_sig,
        "policy_taxonomy": jsonable_mapping_sequence(taxonomy),
    }


def git_metadata(repo_root: Path) -> dict[str, Any]:
    def _run(cmd: list[str]) -> str:
        try:
            result = subprocess.run(
                cmd,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            return ""

    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    commit = _run(["git", "rev-parse", "HEAD"])
    dirty = _run(["git", "status", "--porcelain"]) != ""
    remote = _run(["git", "remote", "get-url", "origin"])

    return {
        "branch": branch or None,
        "commit": commit or None,
        "dirty": dirty,
        "remote_url": remote or None,
    }
