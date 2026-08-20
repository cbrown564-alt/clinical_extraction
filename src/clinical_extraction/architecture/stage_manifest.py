"""Authoritative stage manifests for the six selected task-method pairs.

A manifest is the single machine-readable statement of how a record moves
through one selected method. Diagrams, method cards, and teaching traces are
generated from or checked against it, so no hand-authored explanation can
disagree with runtime ownership.

The manifest describes the *selected* path only. Historical variants, rejected
candidates, and operational wrappers are named in ``related_paths`` so a reader
can see they exist without mistaking them for the selected method.
"""

from __future__ import annotations

import importlib
import json
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

MANIFEST_DIR = Path(__file__).resolve().parent / "manifests"
# Gitignored local research trees. A public clone has none of these; existence
# checks against paths inside them are skipped when the tree is absent.
LOCAL_RESEARCH_TREES = frozenset({"data", "docs", "experiments"})


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


# Every stage declares exactly one effect class. This is the taxonomy the
# 2026-07-30 understandability review asked for: a reader must be able to tell,
# without opening the code, whether a stage can move a clinical answer.
EFFECT_CLASSES: Mapping[str, str] = {
    "transport_or_schema": (
        "Changes transport or schema shape only. Cannot change which clinical "
        "answer is expressed."
    ),
    "representation": (
        "Changes how a clinical fact is written down (units, casing, state "
        "fields) without changing which clinical fact it is."
    ),
    "clinical_meaning": (
        "May change clinical selection or meaning: a different label, a "
        "different event, an added or removed finding."
    ),
    "benchmark_projection": (
        "Projects a settled clinical answer into a scorer-facing view. Changes "
        "the measured number, not the clinical answer."
    ),
    # Extension to the four classes proposed by the 2026-07-30 review. A gate
    # rewrites nothing, so calling it 'transport_or_schema' would be false, but
    # it can drop a row out of scoring, so calling it inert would also be false.
    "validation_gate": (
        "Accepts or rejects. Cannot rewrite a clinical answer, but can fail a "
        "row or finding out of the scored set."
    ),
}

OWNERS = frozenset({"model", "deterministic", "scorer"})

# From AGENTS.md: deterministic rules carry one of these categories whenever the
# distinction affects claims or ablations.
RULE_CATEGORIES = frozenset(
    {
        "general",
        "clinical_epilepsy",
        "seizure_frequency",
        "gan2026_specific",
        "benchmark_format",
    }
)

METHOD_IDS: tuple[str, ...] = (
    "gan2026_rules_only",
    "gan2026_llm_only",
    "gan2026_llm_with_rules",
    "exectv2_rules_only",
    "exectv2_llm_only",
    "exectv2_llm_pre_post",
)

LEGACY_METHOD_ID_ALIASES: dict[str, str] = {
    "exectv2_llm_with_rules": "exectv2_llm_pre_post",
}

_REQUIRED_STAGE_FIELDS = (
    "stage_id",
    "name",
    "operation",
    "owner",
    "effect_class",
    "input_type",
    "input_example",
    "output_type",
    "output_example",
    "implementation",
    "governing_test",
    "trace_fields",
    "paper_wording",
)


@dataclass(frozen=True)
class Implementation:
    """Where a stage actually runs."""

    path: str
    symbol: str

    @property
    def module(self) -> str:
        return self.symbol.split(":", 1)[0]

    @property
    def attribute(self) -> str | None:
        _, _, attr = self.symbol.partition(":")
        return attr or None

    def resolve(self) -> Any:
        module = importlib.import_module(self.module)
        attr = self.attribute
        if attr is None:
            return module
        target: Any = module
        for part in attr.split("."):
            target = getattr(target, part)
        return target


@dataclass(frozen=True)
class Stage:
    """One explainable step in a selected method."""

    stage_id: str
    name: str
    operation: str
    owner: str
    effect_class: str
    input_type: str
    input_example: str
    output_type: str
    output_example: str
    implementation: Implementation
    governing_test: str
    trace_fields: tuple[str, ...]
    paper_wording: str
    rule_category: str | None = None
    notes: str | None = None
    runtime_action: str | None = None

    @property
    def may_change_clinical_meaning(self) -> bool:
        return self.effect_class == "clinical_meaning"

    @property
    def short_label(self) -> str:
        return self.name

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "stage_id": self.stage_id,
            "name": self.name,
            "operation": self.operation,
            "owner": self.owner,
            "effect_class": self.effect_class,
            "may_change_clinical_meaning": self.may_change_clinical_meaning,
            "input_type": self.input_type,
            "input_example": self.input_example,
            "output_type": self.output_type,
            "output_example": self.output_example,
            "implementation": {
                "path": self.implementation.path,
                "symbol": self.implementation.symbol,
            },
            "governing_test": self.governing_test,
            "trace_fields": list(self.trace_fields),
            "paper_wording": self.paper_wording,
        }
        if self.rule_category:
            payload["rule_category"] = self.rule_category
        if self.notes:
            payload["notes"] = self.notes
        if self.runtime_action:
            payload["runtime_action"] = self.runtime_action
        return payload


@dataclass(frozen=True)
class RelatedPath:
    """A path that is *not* the selected method, named so it cannot be confused."""

    name: str
    role: str
    path: str
    note: str


@dataclass(frozen=True)
class MethodManifest:
    """One selected task-method pair."""

    method_id: str
    task: str
    task_label: str
    method: str
    method_label: str
    role: str
    entry_point: Implementation
    one_sentence: str
    sixty_second: str
    prediction_owner: str
    scored_representation: str
    stages: tuple[Stage, ...]
    related_paths: tuple[RelatedPath, ...]
    evidence_owners: tuple[str, ...]

    def stage(self, stage_id: str) -> Stage:
        for candidate in self.stages:
            if candidate.stage_id == stage_id:
                return candidate
        raise KeyError(f"{self.method_id}: no stage {stage_id!r}")

    @property
    def clinical_meaning_stages(self) -> tuple[Stage, ...]:
        return tuple(stage for stage in self.stages if stage.may_change_clinical_meaning)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method_id": self.method_id,
            "task": self.task,
            "task_label": self.task_label,
            "method": self.method,
            "method_label": self.method_label,
            "role": self.role,
            "entry_point": {
                "path": self.entry_point.path,
                "symbol": self.entry_point.symbol,
            },
            "one_sentence": self.one_sentence,
            "sixty_second": self.sixty_second,
            "prediction_owner": self.prediction_owner,
            "scored_representation": self.scored_representation,
            "stages": [stage.to_dict() for stage in self.stages],
            "related_paths": [
                {
                    "name": related.name,
                    "role": related.role,
                    "path": related.path,
                    "note": related.note,
                }
                for related in self.related_paths
            ],
            "evidence_owners": list(self.evidence_owners),
        }


def _implementation(payload: Mapping[str, Any]) -> Implementation:
    return Implementation(path=str(payload["path"]), symbol=str(payload["symbol"]))


def _stage(payload: Mapping[str, Any]) -> Stage:
    missing = [field for field in _REQUIRED_STAGE_FIELDS if field not in payload]
    if missing:
        raise ValueError(
            f"stage {payload.get('stage_id', '<unknown>')!r} missing fields: "
            f"{', '.join(missing)}"
        )
    return Stage(
        stage_id=str(payload["stage_id"]),
        name=str(payload["name"]),
        operation=str(payload["operation"]),
        owner=str(payload["owner"]),
        effect_class=str(payload["effect_class"]),
        input_type=str(payload["input_type"]),
        input_example=str(payload["input_example"]),
        output_type=str(payload["output_type"]),
        output_example=str(payload["output_example"]),
        implementation=_implementation(payload["implementation"]),
        governing_test=str(payload["governing_test"]),
        trace_fields=tuple(str(field) for field in payload["trace_fields"]),
        paper_wording=str(payload["paper_wording"]),
        rule_category=(
            str(payload["rule_category"]) if payload.get("rule_category") else None
        ),
        notes=str(payload["notes"]) if payload.get("notes") else None,
        runtime_action=(
            str(payload["runtime_action"]) if payload.get("runtime_action") else None
        ),
    )


def _manifest(payload: Mapping[str, Any]) -> MethodManifest:
    return MethodManifest(
        method_id=str(payload["method_id"]),
        task=str(payload["task"]),
        task_label=str(payload["task_label"]),
        method=str(payload["method"]),
        method_label=str(payload["method_label"]),
        role=str(payload["role"]),
        entry_point=_implementation(payload["entry_point"]),
        one_sentence=str(payload["one_sentence"]),
        sixty_second=str(payload["sixty_second"]),
        prediction_owner=str(payload["prediction_owner"]),
        scored_representation=str(payload["scored_representation"]),
        stages=tuple(_stage(stage) for stage in payload["stages"]),
        related_paths=tuple(
            RelatedPath(
                name=str(related["name"]),
                role=str(related["role"]),
                path=str(related["path"]),
                note=str(related["note"]),
            )
            for related in payload.get("related_paths", ())
        ),
        evidence_owners=tuple(str(owner) for owner in payload.get("evidence_owners", ())),
    )


def manifest_path(method_id: str) -> Path:
    return MANIFEST_DIR / f"{method_id}.json"


@cache
def load_manifest(method_id: str) -> MethodManifest:
    resolved = LEGACY_METHOD_ID_ALIASES.get(method_id, method_id)
    path = manifest_path(resolved)
    if not path.is_file():
        raise FileNotFoundError(f"no stage manifest for {method_id!r} at {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    manifest = _manifest(payload)
    if manifest.method_id != resolved:
        raise ValueError(
            f"{path.name} declares method_id {manifest.method_id!r}"
        )
    return manifest


def load_manifests() -> tuple[MethodManifest, ...]:
    return tuple(load_manifest(method_id) for method_id in METHOD_IDS)


def iter_stages() -> Iterator[tuple[MethodManifest, Stage]]:
    for manifest in load_manifests():
        for stage in manifest.stages:
            yield manifest, stage


def validate_manifest(manifest: MethodManifest, *, root: Path | None = None) -> list[str]:
    """Return every way this manifest disagrees with the repository."""

    root = root or repo_root()
    problems: list[str] = []
    prefix = manifest.method_id

    if manifest.method_id not in METHOD_IDS:
        problems.append(f"{prefix}: unknown method_id")

    seen: set[str] = set()
    for stage in manifest.stages:
        tag = f"{prefix}/{stage.stage_id}"
        if stage.stage_id in seen:
            problems.append(f"{tag}: duplicate stage_id")
        seen.add(stage.stage_id)

        if stage.owner not in OWNERS:
            problems.append(f"{tag}: owner {stage.owner!r} not in {sorted(OWNERS)}")
        if stage.effect_class not in EFFECT_CLASSES:
            problems.append(
                f"{tag}: effect_class {stage.effect_class!r} not in "
                f"{sorted(EFFECT_CLASSES)}"
            )
        if stage.owner == "deterministic" and stage.rule_category is None:
            problems.append(f"{tag}: deterministic stage must declare a rule_category")
        if stage.rule_category and stage.rule_category not in RULE_CATEGORIES:
            problems.append(
                f"{tag}: rule_category {stage.rule_category!r} not in "
                f"{sorted(RULE_CATEGORIES)}"
            )
        if stage.owner == "model" and stage.effect_class != "clinical_meaning":
            problems.append(
                f"{tag}: a model-owned stage proposes clinical content and must "
                "declare effect_class 'clinical_meaning'"
            )
        if not stage.trace_fields:
            problems.append(f"{tag}: no trace_fields; execution cannot be proven")

        problems.extend(_check_implementation(tag, stage.implementation, root))
        problems.extend(_check_governing_test(tag, stage.governing_test, root))

    problems.extend(
        _check_implementation(f"{prefix}/entry_point", manifest.entry_point, root)
    )
    for related in manifest.related_paths:
        if _local_research_path_absent(root, related.path):
            continue
        if not (root / related.path).exists():
            problems.append(
                f"{prefix}: related path {related.path} does not exist"
            )
    for owner in manifest.evidence_owners:
        if _local_research_path_absent(root, owner):
            continue
        if not (root / owner).exists():
            problems.append(f"{prefix}: evidence owner {owner} does not exist")

    if not manifest.clinical_meaning_stages:
        problems.append(f"{prefix}: no stage owns the clinical answer")
    return problems


def _local_research_path_absent(root: Path, relative: str) -> bool:
    """True when ``relative`` lives under a missing gitignored research tree."""

    parts = Path(relative).parts
    return bool(parts) and parts[0] in LOCAL_RESEARCH_TREES and not (root / parts[0]).exists()


def _check_implementation(tag: str, impl: Implementation, root: Path) -> list[str]:
    problems: list[str] = []
    if not (root / impl.path).is_file():
        problems.append(f"{tag}: implementation path {impl.path} does not exist")
    try:
        impl.resolve()
    except (ImportError, AttributeError) as exc:
        problems.append(f"{tag}: cannot resolve {impl.symbol!r} ({exc})")
    return problems


def _check_governing_test(tag: str, governing_test: str, root: Path) -> list[str]:
    file_part, _, test_name = governing_test.partition("::")
    path = root / file_part
    if not path.is_file():
        return [f"{tag}: governing test file {file_part} does not exist"]
    if test_name and f"def {test_name}(" not in path.read_text(encoding="utf-8"):
        return [f"{tag}: governing test {test_name} not found in {file_part}"]
    return []


def validate_all(*, root: Path | None = None) -> list[str]:
    problems: list[str] = []
    for method_id in METHOD_IDS:
        try:
            manifest = load_manifest(method_id)
        except (FileNotFoundError, ValueError) as exc:
            problems.append(f"{method_id}: {exc}")
            continue
        problems.extend(validate_manifest(manifest, root=root))
    return problems


def ownership_matrix() -> list[dict[str, Any]]:
    """One row per selected method: who owns each effect class."""

    rows: list[dict[str, Any]] = []
    for manifest in load_manifests():
        counts = {effect: 0 for effect in EFFECT_CLASSES}
        for stage in manifest.stages:
            counts[stage.effect_class] += 1
        rows.append(
            {
                "method_id": manifest.method_id,
                "task_label": manifest.task_label,
                "method_label": manifest.method_label,
                "prediction_owner": manifest.prediction_owner,
                "stage_count": len(manifest.stages),
                "clinical_meaning_stages": [
                    stage.stage_id for stage in manifest.clinical_meaning_stages
                ],
                **counts,
            }
        )
    return rows


def stage_index() -> list[dict[str, Any]]:
    """Flat index of every stage, for cross-method search."""

    return [
        {"method_id": manifest.method_id, **stage.to_dict()}
        for manifest, stage in iter_stages()
    ]


def format_problems(problems: Sequence[str]) -> str:
    if not problems:
        return "stage manifests agree with the repository"
    lines = [f"{len(problems)} stage-manifest problem(s):"]
    lines.extend(f"  - {problem}" for problem in problems)
    return "\n".join(lines)
