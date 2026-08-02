#!/usr/bin/env python3
"""Run the no-call characterization/parity harness for decision 0047.

The harness uses the synthetic architecture fixtures and replay strings only.
It does not load benchmark rows, gold annotations, or configure a provider.
The resulting JSON is a machine-readable implementation-parity artifact, not
clinical validation evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from clinical_extraction.architecture.stage_manifest import load_manifest
from clinical_extraction.architecture.teaching_case import (
    EXECT_HYBRID_RAW_OUTPUT,
    EXECT_LETTER_ID,
    EXECT_NOTE_TEXT,
    GAN_HYBRID_RAW_OUTPUT,
    GAN_LLM_ONLY_RAW_OUTPUT,
    GAN_NOTE_TEXT,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
    rules as exect_rules,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
    structured_one_call,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
    StructuredMethodConfig,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration import (
    llm as gan_llm,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration import (
    llm_with_rules as gan_hybrid,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration import (
    rules as gan_rules,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "experiments" / "canonical_orchestrator_parity_0047.json"
IMPLEMENTATION_ROOTS = (
    ROOT
    / "src"
    / "clinical_extraction"
    / "tasks"
    / "seizure_frequency"
    / "gan2026"
    / "orchestration",
    ROOT
    / "src"
    / "clinical_extraction"
    / "tasks"
    / "epilepsy_phenotyping"
    / "exectv2"
    / "orchestration",
    ROOT / "src" / "clinical_extraction" / "architecture" / "manifests",
)
IMPLEMENTATION_FILES = (
    Path(__file__).resolve(),
    ROOT / "src" / "clinical_extraction" / "operational" / "exect.py",
    ROOT
    / "src"
    / "clinical_extraction"
    / "tasks"
    / "epilepsy_phenotyping"
    / "exectv2"
    / "assembly"
    / "pipeline.py",
    ROOT
    / "src"
    / "clinical_extraction"
    / "tasks"
    / "epilepsy_phenotyping"
    / "exectv2"
    / "llm"
    / "pipelines"
    / "key_entities_structured"
    / "runner.py",
    ROOT
    / "src"
    / "clinical_extraction"
    / "tasks"
    / "epilepsy_phenotyping"
    / "exectv2"
    / "llm"
    / "shared"
    / "mention_pipeline.py",
    ROOT / "scripts" / "verify_reference_evidence.py",
    ROOT / "scripts" / "build_architecture_docs.py",
    ROOT / "scripts" / "check_canonical_orchestrator_development_parity.py",
    ROOT / "scripts" / "check_locked_aggregate_safety.py",
    ROOT / "experiments" / "canonical_orchestrator_development_parity_0047.json",
    ROOT / "docs" / "experiments" / "retained_evidence_manifest.json",
)


def _jsonable(value: Any) -> Any:
    if isinstance(value, PredictedLetter):
        return value.model_dump(mode="json")
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _fixture_gan_record() -> GanFrequencyRecord:
    """Build the typed input shape without exposing it in the report."""

    frequency = label_to_frequency_record("1 per month")
    return GanFrequencyRecord(
        source_row_index=1,
        note_text=GAN_NOTE_TEXT,
        gold_label="1 per month",
        gold_reference="synthetic fixture reference",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=frequency.normalized_label,
        gold_label_kind=frequency.kind,
        gold_yearly_bounds=frequency.yearly_bounds,
        gold_monthly_frequency=frequency.monthly_frequency,
    )


def _fixture_config(**kwargs: Any) -> PipelineConfiguration:
    return PipelineConfiguration(
        architecture="llm_only_canonical_pipeline",
        model="fixture",
        **kwargs,
    )


def _method_record(method_id: str, result: Any) -> dict[str, Any]:
    manifest = load_manifest(method_id)
    return {
        "method_id": method_id,
        "entry_point": manifest.entry_point.symbol,
        "stage_ids": [event.stage_id for event in result.stage_events],
        "declared_stage_ids": [stage.stage_id for stage in manifest.stages],
        "output": _jsonable(result.output),
        "scorer_projection": _jsonable(getattr(result, "scorer_projection", {})),
        "first_prediction_changing_owner": getattr(
            result, "first_prediction_changing_owner", None
        ),
        "first_failure": getattr(result, "first_failure", None),
    }


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    content = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py", ".toml", ".lock"}:
        content = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    digest.update(content)
    return digest.hexdigest()


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):  # pragma: no cover - packaging fallback
        return "unknown"


def _implementation_hashes() -> dict[str, str]:
    paths = {
        path
        for root in IMPLEMENTATION_ROOTS
        for path in root.rglob("*")
        if path.is_file() and path.suffix in {".json", ".py"}
    }
    paths.update(IMPLEMENTATION_FILES)
    return {path.relative_to(ROOT).as_posix(): _hash_file(path) for path in paths}


def _verification_gates() -> dict[str, dict[str, Any]]:
    """Run the no-call external checks claimed by this retained artifact."""

    retained_command = [sys.executable, "scripts/verify_reference_evidence.py"]
    retained = subprocess.run(
        retained_command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    retained_cells: dict[str, Any] = {}
    if retained.returncode == 0:
        try:
            retained_cells = json.loads(retained.stdout)
        except json.JSONDecodeError:
            retained = subprocess.CompletedProcess(
                retained.args,
                1,
                retained.stdout,
                "reference verifier returned invalid JSON",
            )

    architecture_command = [sys.executable, "scripts/build_architecture_docs.py", "--check"]
    architecture = subprocess.run(
        architecture_command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    development = subprocess.run(
        [
            sys.executable,
            "scripts/check_canonical_orchestrator_development_parity.py",
            "--check",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    locked = subprocess.run(
        [sys.executable, "scripts/check_locked_aggregate_safety.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "retained_historical_reference": {
            "passed": retained.returncode == 0,
            "command": ".venv\\Scripts\\python.exe scripts\\verify_reference_evidence.py",
            "cells": retained_cells,
        },
        "architecture_drift": {
            "passed": architecture.returncode == 0,
            "command": (
                ".venv\\Scripts\\python.exe scripts\\build_architecture_docs.py --check"
            ),
        },
        "selected_method_development_parity": {
            "passed": development.returncode == 0,
            "command": (
                ".venv\\Scripts\\python.exe "
                "scripts\\check_canonical_orchestrator_development_parity.py --check"
            ),
        },
        "locked_aggregate_safety": {
            "passed": locked.returncode == 0,
            "command": (
                ".venv\\Scripts\\python.exe scripts\\check_locked_aggregate_safety.py"
            ),
        },
    }


def _legacy_parity(
    gan_record: GanFrequencyRecord, exect_letter: ExectLetter
) -> dict[str, bool]:
    """Compare canonical adapters with the preserved pre-refactor batch paths."""

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines import (
        key_entities_structured,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        hybrid_structured_events as legacy_gan_hybrid,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        llm_only_canonical_pipeline as legacy_gan_llm,
    )

    legacy_exect = importlib.import_module(f"{key_entities_structured.__name__}.runner")
    legacy_llm_rows, _ = legacy_gan_llm._legacy_run_split(
        [gan_record],
        split="synthetic_fixture",
        split_manifest="decision_0047_synthetic",
        model="fixture",
        temperature=0.0,
        max_tokens=1,
        mode="prompt-only",
        reuse_raw_outputs={gan_record.source_row_index: GAN_LLM_ONLY_RAW_OUTPUT},
    )
    canonical_llm_rows, _ = gan_llm.run_split(
        [gan_record],
        split="synthetic_fixture",
        split_manifest="decision_0047_synthetic",
        model="fixture",
        temperature=0.0,
        max_tokens=1,
        mode="prompt-only",
        reuse_raw_outputs={gan_record.source_row_index: GAN_LLM_ONLY_RAW_OUTPUT},
    )
    legacy_hybrid_rows, _ = legacy_gan_hybrid._legacy_run_split(
        [gan_record],
        split="synthetic_fixture",
        split_manifest="decision_0047_synthetic",
        model="fixture",
        temperature=0.0,
        max_tokens=1,
        mode="prompt-only",
        reuse_raw_outputs={gan_record.source_row_index: GAN_HYBRID_RAW_OUTPUT},
    )
    canonical_hybrid_rows, _ = gan_hybrid.run_split(
        [gan_record],
        split="synthetic_fixture",
        split_manifest="decision_0047_synthetic",
        model="fixture",
        temperature=0.0,
        max_tokens=1,
        mode="prompt-only",
        reuse_raw_outputs={gan_record.source_row_index: GAN_HYBRID_RAW_OUTPUT},
    )

    legacy_exect_rows, _ = legacy_exect._legacy_run_split(
        [exect_letter],
        split="synthetic_fixture",
        model="fixture",
        temperature=0.0,
        max_tokens=1,
        mode="prompt-only",
    )
    canonical_exect_rows, _ = structured_one_call.run_split(
        [exect_letter],
        split="synthetic_fixture",
        model="fixture",
        temperature=0.0,
        max_tokens=1,
        mode="prompt-only",
    )
    return {
        "exect_structured_prompt_only_rows": legacy_exect_rows
        == canonical_exect_rows,
        "gan_hybrid_saved_output_rows": _compatibility_rows_match(
            legacy_hybrid_rows, canonical_hybrid_rows
        ),
        "gan_llm_only_saved_output_rows": legacy_llm_rows == canonical_llm_rows,
    }


def _compatibility_row(row: dict[str, Any]) -> dict[str, Any]:
    """Project a row to fields whose equality proves legacy compatibility.

    The canonical hybrid entry point intentionally publishes its current
    outward identity as ``llm_with_rules``.  The preserved legacy batch path
    predates that identity field, so only this top-level metadata field is
    excluded.  Nested traces and all other row fields remain part of the
    comparison; semantic or provenance drift must still fail parity.
    """

    projected = dict(row)
    projected.pop("pipeline_family", None)
    return projected


def _compatibility_rows_match(
    legacy_rows: list[dict[str, Any]], canonical_rows: list[dict[str, Any]]
) -> bool:
    return [_compatibility_row(row) for row in legacy_rows] == [
        _compatibility_row(row) for row in canonical_rows
    ]


def reports_match(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    """Compare artifacts while excluding only the commit containing the artifact."""

    expected = dict(expected)
    actual = dict(actual)
    expected.pop("source_commit", None)
    actual.pop("source_commit", None)
    return expected == actual


def build_parity_report() -> dict[str, Any]:
    gan_record = _fixture_gan_record()
    gan_config = _fixture_config()
    exect_letter = ExectLetter(letter_id=EXECT_LETTER_ID, note_text=EXECT_NOTE_TEXT)
    exect_config = StructuredMethodConfig.selected()

    gan_rules_result = gan_rules.run_record(gan_record, gan_config)
    gan_llm_result = gan_llm.run_record(
        gan_record,
        gan_config,
        mode="prompt-only",
        raw_output=GAN_LLM_ONLY_RAW_OUTPUT,
    )
    gan_hybrid_result = gan_hybrid.run_record(
        gan_record,
        gan_config,
        mode="prompt-only",
        raw_output=GAN_HYBRID_RAW_OUTPUT,
    )
    exect_rules_result = exect_rules.run_letter(exect_letter)
    producer = structured_one_call.produce_structured_letter(
        exect_letter,
        mode="prompt-only",
        raw_output=EXECT_HYBRID_RAW_OUTPUT,
        config=exect_config,
    )
    exect_llm_result, exect_hybrid_result = structured_one_call.run_primary_pair(
        exect_letter,
        producer=producer,
        config=exect_config,
    )

    methods = {
        "gan2026_rules_only": _method_record("gan2026_rules_only", gan_rules_result),
        "gan2026_llm_only": _method_record("gan2026_llm_only", gan_llm_result),
        "gan2026_llm_with_rules": _method_record(
            "gan2026_llm_with_rules", gan_hybrid_result
        ),
        "exectv2_rules_only": _method_record("exectv2_rules_only", exect_rules_result),
        "exectv2_llm_only": _method_record("exectv2_llm_only", exect_llm_result),
        "exectv2_llm_with_rules": _method_record(
            "exectv2_llm_with_rules", exect_hybrid_result
        ),
    }
    stage_mismatches = {
        method_id: {
            "missing": sorted(
                set(payload["declared_stage_ids"]) - set(payload["stage_ids"])
            ),
            "unexpected": sorted(
                set(payload["stage_ids"]) - set(payload["declared_stage_ids"])
            ),
        }
        for method_id, payload in methods.items()
        if payload["stage_ids"] != payload["declared_stage_ids"]
    }

    # These are compatibility/delegation comparisons, not scorer comparisons.
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
        orchestrator as legacy_exect_rules,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners import (
        deterministic_canonical as legacy_gan_rules,
    )

    legacy_gan = legacy_gan_rules.run_item(gan_record, gan_config)
    legacy_exect = legacy_exect_rules.run_all9_on_letters([exect_letter])[0]
    compatibility = {
        "gan_rules_adapter_matches": _jsonable(legacy_gan)
        == _jsonable(gan_rules_result.to_pipeline_result()),
        "exect_rules_adapter_matches": _jsonable(legacy_exect)
        == _jsonable(exect_rules_result.prediction),
        "exect_pair_uses_one_producer": (
            exect_llm_result.producer is producer
            and exect_hybrid_result.producer is producer
        ),
    }
    legacy_parity = _legacy_parity(gan_record, exect_letter)
    verification_gates = _verification_gates()

    return {
        "schema_version": "decision_0047_parity_v4",
        "decision": "0047-full-canonical-pipeline-orchestrator-refactor",
        "claim_boundary": (
            "No-call implementation characterization and compatibility parity; "
            "not clinical validation, holdout evidence, or model performance."
        ),
        "source_commit": _git_head(),
        "implementation_hashes": _implementation_hashes(),
        "environment_lock": {
            "pyproject.toml": _hash_file(ROOT / "pyproject.toml"),
            "uv.lock": _hash_file(ROOT / "uv.lock"),
        },
        "selected_configurations": {
            "gan": {
                "architecture": gan_config.architecture,
                "mode": "prompt-only",
                "prompt_version": gan_config.prompt_version,
            },
            "exect": {
                "prompt_profile": exect_config.prompt_profile,
                "diagnosis_policy_variant": exect_config.diagnosis_policy_variant,
                "prescription_policy_variant": exect_config.prescription_policy_variant,
                "sf_projection_ablation": exect_config.sf_projection_ablation,
            },
        },
        "input_fixtures": {
            "gan": {
                "source_id": "TEACH-GAN-01",
                "note_hash": hashlib.sha256(GAN_NOTE_TEXT.encode()).hexdigest(),
            },
            "exect": {
                "source_id": EXECT_LETTER_ID,
                "note_hash": hashlib.sha256(EXECT_NOTE_TEXT.encode()).hexdigest(),
            },
        },
        "comparison_fields": [
            "entry_point",
            "stage_ids",
            "output",
            "scorer_projection",
            "first_prediction_changing_owner",
            "first_failure",
        ],
        "allowed_metadata_exclusions": [
            "fixture source text from serialized outputs",
            "source_commit during artifact check; implementation_hashes detect code drift",
        ],
        "commands": [
            ".venv\\Scripts\\python.exe scripts\\check_canonical_orchestrator_parity.py",
            ".venv\\Scripts\\python.exe -m pytest "
            "tests\\test_*canonical_orchestrators.py "
            "tests\\test_architecture_teaching_cases.py -q",
        ],
        "methods": methods,
        "stage_mismatches": stage_mismatches,
        "compatibility": compatibility,
        "legacy_parity": legacy_parity,
        "verification_gates": verification_gates,
        "verification_state": "verified",
        "unverified_gates": [],
        "result": (
            "pass"
            if not stage_mismatches
            and all(compatibility.values())
            and all(legacy_parity.values())
            and all(gate["passed"] for gate in verification_gates.values())
            else "fail"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check the committed artifact.")
    parser.add_argument("--output", type=Path, default=ARTIFACT)
    args = parser.parse_args()
    report = build_parity_report()
    path = args.output if args.output.is_absolute() else ROOT / args.output
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not path.is_file():
            print(f"parity artifact is missing: {path}")
            return 1
        existing = json.loads(path.read_text(encoding="utf-8"))
        if not reports_match(report, existing):
            print(f"parity artifact is stale: {path}")
            return 1
        print(f"parity artifact matches: {path}")
        return 0 if report["result"] == "pass" else 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")
    print(f"wrote {path}")
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
