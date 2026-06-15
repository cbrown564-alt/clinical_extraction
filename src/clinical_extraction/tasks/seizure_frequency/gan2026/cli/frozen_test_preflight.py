"""Preflight checks for the frozen Gan 2026 V12 test audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    fresh_evidence_reasoner,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.cli.llm_pipeline_cli import (
    FROZEN_TEST_PIPELINE_LAUNCH_SPECS,
    pipeline_specs,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

DEFAULT_PROTOCOL_PATH = Path(
    "docs/research/gan2026_fresh_evidence_reasoner_frozen_test450_protocol_2026-06-13.md"
)
DEFAULT_TEST_JSONL_PATH = Path(
    "experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_2026-06-15.jsonl"
)
DEFAULT_TEST_REPORT_PATH = Path(
    "experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_2026-06-15.md"
)
EXPECTED_PIPELINE = "fresh_evidence_reasoner"
EXPECTED_MODEL = "openai/gpt-4.1"
EXPECTED_MAX_TOKENS = 2800
EXPECTED_PROMPT_VERSION = "gan2026_fresh_evidence_reasoner_v0_6"
EXPECTED_SAFETY_GATE_VERSION = "gan2026_fresh_evidence_safety_gate_v0_9"
EXPECTED_SPLIT_MANIFEST = "gan2026_split_v1"
EXPECTED_TEST_ROW_COUNT = 450
EXPECTED_TARGET_PURIST = "383/450"
SYNTHETIC_HOLDOUT_ROW_ID = 9902001
SYNTHETIC_HOLDOUT_PROFILE = "synthetic_holdout_profile_should_be_omitted"
SYNTHETIC_HOLDOUT_LABEL = "2 per week"
SYNTHETIC_PROMPT_ROW_ID = 9902002
SYNTHETIC_PROMPT_GOLD_LABEL = "synthetic_gold_label_should_not_leak"
SYNTHETIC_PROMPT_RAW_SECRET = "synthetic_raw_secret_should_not_leak"
SYNTHETIC_PROMPT_NOTE_EVIDENCE = "current seizures are twice per week"
EXPECTED_TEST_SOURCE_ARTIFACTS = (
    ("gpt", fresh_evidence_reasoner.TEST_GPT_STRUCTURED_EVENT_JSONL_PATH),
    ("qwen", fresh_evidence_reasoner.TEST_QWEN_STRUCTURED_EVENT_JSONL_PATH),
    ("deepseek", fresh_evidence_reasoner.TEST_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH),
)

HASH_LINE_RE = re.compile(r"^([0-9a-f]{64})\s+(.+?)\s*$", re.MULTILINE)
POWERSHELL_BLOCK_RE = re.compile(r"```powershell\s+(.*?)```", re.DOTALL)


@dataclass(frozen=True)
class PreflightConfig:
    """Inputs for a frozen-test preflight check."""

    protocol_path: Path = DEFAULT_PROTOCOL_PATH
    test_jsonl_path: Path = DEFAULT_TEST_JSONL_PATH
    test_report_path: Path = DEFAULT_TEST_REPORT_PATH
    check_test_source_artifacts: bool = True
    required_hash_paths: tuple[str, ...] = (
        "src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/fresh_evidence_reasoner.py",
        "src/clinical_extraction/tasks/seizure_frequency/gan2026/runner.py",
        "src/clinical_extraction/tasks/seizure_frequency/gan2026/cli/llm_pipeline_cli.py",
        "src/clinical_extraction/tasks/seizure_frequency/gan2026/cli/frozen_test_preflight.py",
        "src/clinical_extraction/tasks/seizure_frequency/gan2026/cli/frozen_test_readout.py",
        "tests/test_gan2026_fresh_evidence_reasoner.py",
        "tests/test_gan2026_llm_pipeline_cli.py",
        "tests/test_gan2026_frozen_test_preflight.py",
        "tests/test_gan2026_frozen_test_readout.py",
        "experiments/gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl",
        "experiments/gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.md",
        "experiments/gan2026_fresh_evidence_reasoner_safety_v0_4_validation750_no_call_replay_2026-06-15.md",
        "experiments/gan2026_fresh_evidence_reasoner_validation250_nocall_replay_v0_6_safety_v0_9_2026-06-15.md",
        "experiments/gan2026_fresh_evidence_reasoner_unknown_policy_trigger_full_validation_nocall_replay_v0_6_safety_v0_9_2026-06-15.md",
        "experiments/gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_2026-06-09.jsonl",
        "experiments/gan2026_agentic_structured_event_patch_recent_unresolved_burden_test450_qwen3635b_2026-06-13.jsonl",
        "experiments/gan2026_v06_test450_hybrid_structured_events_deepseek_2026-06-14.jsonl",
        "data/Gan (2026)/splits/gan2026_split_v1.json",
    )


@dataclass(frozen=True)
class PreflightReport:
    """Machine-readable summary of frozen-test readiness."""

    ok: bool
    checks: tuple[str, ...]
    failures: tuple[str, ...]

    def to_json_record(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "checks": list(self.checks),
            "failures": list(self.failures),
        }


def run_preflight(config: PreflightConfig | None = None) -> PreflightReport:
    """Return a report for the frozen V12 test audit launch conditions."""

    if config is None:
        config = PreflightConfig()
    checks: list[str] = []
    failures: list[str] = []
    protocol_text = _read_protocol(config.protocol_path, checks, failures)
    _check_protocol_text(protocol_text, checks, failures)
    _check_protocol_hashes(protocol_text, config.required_hash_paths, checks, failures)
    _check_v12_constants(checks, failures)
    _check_cli_spec(checks, failures)
    _check_split_manifest(checks, failures)
    _check_v12_test_source_artifacts(config, checks, failures)
    _check_v12_prompt_input_contract(checks, failures)
    _check_v12_aggregate_only_output_contract(checks, failures)
    _check_absent_test_outputs(config, checks, failures)
    return PreflightReport(ok=not failures, checks=tuple(checks), failures=tuple(failures))


def _read_protocol(path: Path, checks: list[str], failures: list[str]) -> str:
    if not path.exists():
        failures.append(f"missing protocol artifact: {path}")
        return ""
    checks.append(f"protocol artifact exists: {path}")
    return path.read_text(encoding="utf-8")


def _check_protocol_text(
    protocol_text: str,
    checks: list[str],
    failures: list[str],
) -> None:
    if not protocol_text:
        return
    required_text = {
        "pipeline name": EXPECTED_PIPELINE,
        "model": EXPECTED_MODEL,
        "prompt version": EXPECTED_PROMPT_VERSION,
        "safety gate": EXPECTED_SAFETY_GATE_VERSION,
        "target": EXPECTED_TARGET_PURIST,
        "confirm flag": "--confirm-test-audit",
        "test split": "--split test",
        "aggregate policy": "aggregate-only",
        "no deterministic fallback": "No deterministic final-label fallback",
        "aggregate readout helper": "frozen_test_readout",
        "GPT test source artifact": (
            fresh_evidence_reasoner.TEST_GPT_STRUCTURED_EVENT_JSONL_PATH.as_posix()
        ),
        "Qwen test source artifact": (
            fresh_evidence_reasoner.TEST_QWEN_STRUCTURED_EVENT_JSONL_PATH.as_posix()
        ),
        "DeepSeek test source artifact": (
            fresh_evidence_reasoner.TEST_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH.as_posix()
        ),
    }
    for label, text in required_text.items():
        if text not in protocol_text:
            failures.append(f"protocol missing {label}: {text}")
        else:
            checks.append(f"protocol includes {label}")
    command = _extract_powershell_command(protocol_text)
    if command is None:
        failures.append("protocol missing powershell command block")
        return
    checks.append("protocol includes powershell command block")
    _check_authorized_command(command, checks, failures)


def _check_authorized_command(
    command: str,
    checks: list[str],
    failures: list[str],
) -> None:
    normalized_command = _normalize_command_text(command)
    required_command_text = {
        "pipeline": f"--pipeline {EXPECTED_PIPELINE}",
        "test split": "--split test",
        "live mode": "--mode live",
        "model": f"--model {EXPECTED_MODEL}",
        "max tokens": f"--max-tokens {EXPECTED_MAX_TOKENS}",
        "confirm flag": "--confirm-test-audit",
        "JSONL path": f"--jsonl {DEFAULT_TEST_JSONL_PATH}",
        "Markdown path": f"--markdown {DEFAULT_TEST_REPORT_PATH}",
        "disabled progress checkpoints": "--progress-every 0",
        "escalation reason": "--escalation-reason",
    }
    for label, text in required_command_text.items():
        if _normalize_command_text(text) not in normalized_command:
            failures.append(f"authorized command missing {label}: {text}")
        else:
            checks.append(f"authorized command includes {label}")
    singleton_command_options = (
        "--pipeline",
        "--split",
        "--mode",
        "--model",
        "--max-tokens",
        "--jsonl",
        "--markdown",
        "--progress-every",
        "--escalation-reason",
    )
    for option in singleton_command_options:
        count = _count_cli_option(normalized_command, option)
        if count != 1:
            failures.append(
                f"authorized command must include {option} exactly once; found {count}"
            )
        else:
            checks.append(f"authorized command includes {option} exactly once")
    forbidden_command_options = (
        "--limit",
        "--source-row-indices",
        "--source-row-index-file",
        "--resume-existing",
        "--overwrite-existing",
        "--candidate-set-jsonl",
        "--structured-event-jsonl",
        "--temperature",
        "--mode prompt-only",
        "--api-base",
        "--disable-dspy-cache",
    )
    for option in forbidden_command_options:
        if option in normalized_command:
            failures.append(f"authorized command must not include {option}")
        else:
            checks.append(f"authorized command omits {option}")


def _count_cli_option(normalized_command: str, option: str) -> int:
    return len(re.findall(rf"(?<!\S){re.escape(option)}(?:\s|=|$)", normalized_command))


def _extract_powershell_command(protocol_text: str) -> str | None:
    matches = POWERSHELL_BLOCK_RE.findall(protocol_text)
    for command in matches:
        if "llm_pipeline_cli" in command and f"--pipeline {EXPECTED_PIPELINE}" in command:
            return command
    return None


def _normalize_command_text(command_text: str) -> str:
    return " ".join(command_text.replace("`", " ").replace("\\", "/").split())


def _check_protocol_hashes(
    protocol_text: str,
    required_paths: Sequence[str],
    checks: list[str],
    failures: list[str],
) -> None:
    if not protocol_text:
        return
    protocol_hashes = _parse_protocol_hashes(protocol_text)
    for path_text in required_paths:
        expected_hash = protocol_hashes.get(path_text)
        if expected_hash is None:
            failures.append(f"protocol missing hash for {path_text}")
            continue
        path = Path(path_text)
        if not path.exists():
            failures.append(f"hashed artifact missing on disk: {path_text}")
            continue
        actual_hash = _sha256(path)
        if actual_hash != expected_hash:
            failures.append(
                f"hash mismatch for {path_text}: expected {expected_hash}, got {actual_hash}"
            )
        else:
            checks.append(f"hash matches: {path_text}")


def _parse_protocol_hashes(protocol_text: str) -> dict[str, str]:
    return {path_text: digest for digest, path_text in HASH_LINE_RE.findall(protocol_text)}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check_v12_constants(checks: list[str], failures: list[str]) -> None:
    expected_values = {
        "PROMPT_VERSION": (
            fresh_evidence_reasoner.PROMPT_VERSION,
            EXPECTED_PROMPT_VERSION,
        ),
        "SAFETY_GATE_VERSION": (
            fresh_evidence_reasoner.SAFETY_GATE_VERSION,
            EXPECTED_SAFETY_GATE_VERSION,
        ),
        "PIPELINE_FAMILY": (fresh_evidence_reasoner.PIPELINE_FAMILY, EXPECTED_PIPELINE),
    }
    for label, (actual, expected) in expected_values.items():
        if actual != expected:
            failures.append(f"V12 {label} drifted: expected {expected}, got {actual}")
        else:
            checks.append(f"V12 {label} matches {expected}")


def _check_cli_spec(checks: list[str], failures: list[str]) -> None:
    specs = pipeline_specs()
    spec = specs.get(EXPECTED_PIPELINE)
    if spec is None:
        failures.append(f"CLI registry missing {EXPECTED_PIPELINE}")
        return
    checks.append(f"CLI registry exposes {EXPECTED_PIPELINE}")
    if spec.default_max_tokens != EXPECTED_MAX_TOKENS:
        failures.append(
            f"{EXPECTED_PIPELINE} max tokens drifted: "
            f"expected {EXPECTED_MAX_TOKENS}, got {spec.default_max_tokens}"
        )
    else:
        checks.append(f"{EXPECTED_PIPELINE} max tokens match {EXPECTED_MAX_TOKENS}")
    launch_spec = FROZEN_TEST_PIPELINE_LAUNCH_SPECS.get(EXPECTED_PIPELINE)
    if launch_spec is None:
        failures.append(f"CLI frozen launch spec missing {EXPECTED_PIPELINE}")
        return
    expected_launch_values = {
        "frozen model": (launch_spec.model, EXPECTED_MODEL),
        "frozen max tokens": (launch_spec.max_tokens, EXPECTED_MAX_TOKENS),
        "frozen JSONL path": (launch_spec.jsonl_path, DEFAULT_TEST_JSONL_PATH),
        "frozen Markdown path": (launch_spec.report_path, DEFAULT_TEST_REPORT_PATH),
    }
    for label, (actual, expected) in expected_launch_values.items():
        if actual != expected:
            failures.append(
                f"{EXPECTED_PIPELINE} {label} drifted: expected {expected}, got {actual}"
            )
        else:
            checks.append(f"{EXPECTED_PIPELINE} {label} matches {expected}")


def _check_split_manifest(checks: list[str], failures: list[str]) -> None:
    manifest = load_split_manifest()
    manifest_name = str(manifest.get("manifest_version") or manifest.get("name") or "")
    if manifest_name != EXPECTED_SPLIT_MANIFEST:
        failures.append(
            f"split manifest drifted: expected {EXPECTED_SPLIT_MANIFEST}, got {manifest_name}"
        )
    else:
        checks.append(f"split manifest matches {EXPECTED_SPLIT_MANIFEST}")
    test_count = _manifest_split_count(manifest, "test")
    if test_count != EXPECTED_TEST_ROW_COUNT:
        failures.append(
            f"test split row count drifted: expected {EXPECTED_TEST_ROW_COUNT}, got {test_count}"
        )
    else:
        checks.append(f"test split count matches {EXPECTED_TEST_ROW_COUNT}")


def _check_v12_test_source_artifacts(
    config: PreflightConfig,
    checks: list[str],
    failures: list[str],
) -> None:
    if not config.check_test_source_artifacts:
        checks.append("test source artifact coverage check disabled by config")
        return
    manifest = load_split_manifest()
    test_source_indices = _manifest_split_source_indices(manifest, "test")
    if test_source_indices is None:
        failures.append("test split manifest is missing source_row_indices")
        return
    gpt_source_path = fresh_evidence_reasoner._gpt_structured_event_source_path(
        "test",
        fresh_evidence_reasoner.DEFAULT_STRUCTURED_EVENT_JSONL_PATH,
    )
    source_paths = fresh_evidence_reasoner._structured_event_source_paths_for_split(
        "test",
        gpt_source_path,
    )
    if source_paths.get("gpt") != fresh_evidence_reasoner.TEST_GPT_STRUCTURED_EVENT_JSONL_PATH:
        failures.append(
            "V12 test GPT structured-event source drifted: "
            f"got {source_paths.get('gpt')}"
        )
    else:
        checks.append("V12 test GPT source uses frozen test450 artifact")
    if (
        source_paths.get("qwen")
        != fresh_evidence_reasoner.TEST_QWEN_STRUCTURED_EVENT_JSONL_PATH
    ):
        failures.append(
            "V12 test Qwen structured-event source drifted: "
            f"got {source_paths.get('qwen')}"
        )
    else:
        checks.append("V12 test Qwen source uses frozen test450 artifact")
    deepseek_path = source_paths.get("deepseek")
    if deepseek_path != fresh_evidence_reasoner.TEST_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH:
        failures.append(
            "V12 test DeepSeek structured-event source drifted: "
            f"got {deepseek_path}"
        )
    else:
        checks.append("V12 test DeepSeek source uses frozen test450 artifact")

    for agent_id, expected_path in EXPECTED_TEST_SOURCE_ARTIFACTS:
        _check_test_source_artifact_coverage(
            agent_id,
            expected_path,
            test_source_indices,
            checks,
            failures,
        )


def _check_test_source_artifact_coverage(
    agent_id: str,
    path: Path,
    expected_source_indices: set[int],
    checks: list[str],
    failures: list[str],
) -> None:
    if not path.exists():
        failures.append(f"{agent_id} test source artifact missing: {path}")
        return
    checks.append(f"{agent_id} test source artifact exists: {path}")
    try:
        rows = load_jsonl_rows(path)
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"{agent_id} test source artifact is not valid JSONL: {exc}")
        return
    rows_with_id = [
        row
        for row in rows
        if isinstance(row, Mapping) and row.get("source_row_index") is not None
    ]
    source_indices = {int(row["source_row_index"]) for row in rows_with_id}
    if len(source_indices) != len(rows_with_id):
        failures.append(f"{agent_id} test source artifact has duplicate row ids")
    else:
        checks.append(f"{agent_id} test source artifact has unique row ids")
    if source_indices != expected_source_indices:
        failures.append(
            f"{agent_id} test source coverage drifted: "
            f"expected {len(expected_source_indices)}, got {len(source_indices)}, "
            f"missing {len(expected_source_indices - source_indices)}, "
            f"extra {len(source_indices - expected_source_indices)}"
        )
    else:
        checks.append(
            f"{agent_id} test source covers {len(expected_source_indices)} locked row ids"
        )
    split_counts: dict[str, int] = {}
    for row in rows_with_id:
        split = row.get("split")
        if split is not None:
            split_text = str(split)
            split_counts[split_text] = split_counts.get(split_text, 0) + 1
    if split_counts and set(split_counts) != {"test"}:
        failures.append(
            f"{agent_id} test source split labels drifted: {dict(sorted(split_counts.items()))}"
        )
    elif split_counts:
        checks.append(f"{agent_id} test source rows are labeled test")


def _check_v12_aggregate_only_output_contract(
    checks: list[str],
    failures: list[str],
) -> None:
    row = _synthetic_output_contract_row()
    test_summary = fresh_evidence_reasoner.summarize_rows([row], split="test")
    if "fresh_evidence_profiles" in test_summary:
        failures.append("V12 test summary exposes fresh_evidence_profiles")
    else:
        checks.append("V12 test summary omits fresh_evidence_profiles")
    if "final_labels" in test_summary:
        failures.append("V12 test summary exposes final_labels")
    else:
        checks.append("V12 test summary omits final_labels")
    omitted_fields = test_summary.get("aggregate_only_omitted_fields")
    expected_omitted = ["final_labels", "fresh_evidence_profiles"]
    if omitted_fields != expected_omitted:
        failures.append(
            "V12 test summary omitted-fields marker drifted: "
            f"expected {expected_omitted}, got {omitted_fields}"
        )
    else:
        checks.append("V12 test summary records omitted aggregate-only fields")

    validation_summary = fresh_evidence_reasoner.summarize_rows([row], split="validation")
    if SYNTHETIC_HOLDOUT_PROFILE not in validation_summary.get(
        "fresh_evidence_profiles", {}
    ):
        failures.append("V12 validation summary no longer preserves profile diagnostics")
    else:
        checks.append("V12 validation summary preserves profile diagnostics")

    with tempfile.TemporaryDirectory(prefix="gan2026_v12_preflight_") as tmp_dir:
        report_path = Path(tmp_dir) / "synthetic_test_report.md"
        fresh_evidence_reasoner.write_report(
            [row],
            _synthetic_output_contract_metadata(
                _synthetic_readout_summary(test_summary)
            ),
            report_path,
            jsonl_path=DEFAULT_TEST_JSONL_PATH,
        )
        report_text = report_path.read_text(encoding="utf-8")
        from clinical_extraction.tasks.seizure_frequency.gan2026.cli import (
            frozen_test_readout,
        )

        readout = frozen_test_readout.read_aggregate_report(report_path)
        if not readout.ok:
            failures.extend(
                f"V12 test report is not parseable by aggregate readout helper: {failure}"
                for failure in readout.failures
            )
        elif readout.metrics.get("target_reached") is not True:
            failures.append("V12 synthetic aggregate readout does not reach target")
        else:
            checks.append("V12 test report is parseable by aggregate readout helper")
    forbidden_report_text = {
        "row table heading": "## Rows",
        "synthetic row id": str(SYNTHETIC_HOLDOUT_ROW_ID),
        "synthetic profile": SYNTHETIC_HOLDOUT_PROFILE,
    }
    for label, text in forbidden_report_text.items():
        if text in report_text:
            failures.append(f"V12 test report exposes {label}")
        else:
            checks.append(f"V12 test report omits {label}")
    if "## Aggregate-Only Holdout Readout" not in report_text:
        failures.append("V12 test report missing aggregate-only holdout section")
    else:
        checks.append("V12 test report includes aggregate-only holdout section")


def _check_v12_prompt_input_contract(
    checks: list[str],
    failures: list[str],
) -> None:
    prompt_input = fresh_evidence_reasoner.build_prompt_input(
        _synthetic_prompt_hygiene_record(),
        {
            "gpt": _synthetic_prompt_hygiene_agent_row(),
            "qwen": None,
            "deepseek": None,
        },
    )
    forbidden_prompt_text = {
        "source row index": str(SYNTHETIC_PROMPT_ROW_ID),
        "source_row_index field": "source_row_index",
        "gold label value": SYNTHETIC_PROMPT_GOLD_LABEL,
        "gold_label field": "gold_label",
        "split manifest": EXPECTED_SPLIT_MANIFEST,
        "deterministic top token": "deterministic_top",
        "raw secret": SYNTHETIC_PROMPT_RAW_SECRET,
        "row_ok field": "row_ok",
    }
    for label, text in forbidden_prompt_text.items():
        if text in prompt_input:
            failures.append(f"V12 prompt input exposes {label}")
        else:
            checks.append(f"V12 prompt input omits {label}")
    required_prompt_text = {
        "raw note evidence": SYNTHETIC_PROMPT_NOTE_EVIDENCE,
        "saved structured-event final": "1 per month",
        "fresh-evidence variant": "V12_fresh_evidence_reasoner",
    }
    for label, text in required_prompt_text.items():
        if text not in prompt_input:
            failures.append(f"V12 prompt input missing {label}: {text}")
        else:
            checks.append(f"V12 prompt input includes {label}")


def _synthetic_prompt_hygiene_record() -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=SYNTHETIC_PROMPT_ROW_ID,
        note_text=(
            "Synthetic preflight note. Older history was one per month, but "
            f"{SYNTHETIC_PROMPT_NOTE_EVIDENCE}."
        ),
        gold_label=SYNTHETIC_PROMPT_GOLD_LABEL,
        gold_reference="synthetic gold evidence should not leak",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={"hidden": SYNTHETIC_PROMPT_RAW_SECRET},
        gold_normalized_label=SYNTHETIC_PROMPT_GOLD_LABEL,
        gold_label_kind=FrequencyLabelKind.UNKNOWN,
        gold_yearly_bounds=None,
        gold_monthly_frequency=123.456,
    )


def _synthetic_prompt_hygiene_agent_row() -> dict[str, Any]:
    return {
        "source_row_index": SYNTHETIC_PROMPT_ROW_ID,
        "prompt_version": "synthetic_agent_trace_should_not_expose_row_id",
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "1 per month",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": "Older history was one per month",
                    "time_window": "historical",
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "1 per month",
                "evidence": "Older history was one per month",
                "confidence": "high",
                "rationale": "Synthetic structured-event final.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": "1 per month",
                "semantic_kind": "frequency",
                "monthly_frequency": 1.0138888888888888,
                "validation_errors": [],
            }
        ],
        "comparison": {"purist_correct": False, "pragmatic_correct": False},
        "evidence_valid": True,
    }


def _synthetic_output_contract_row() -> dict[str, Any]:
    return {
        "source_row_index": SYNTHETIC_HOLDOUT_ROW_ID,
        "fresh_evidence_decision_record": {
            "action": "replace_with_fresh_evidence_final",
            "boundary_profile": [SYNTHETIC_HOLDOUT_PROFILE],
        },
        "score_layers": {
            "raw_model": {
                "final_label": SYNTHETIC_HOLDOUT_LABEL,
                "comparison": {"purist_correct": True, "pragmatic_correct": True},
            },
            "format_only": {
                "final_label": SYNTHETIC_HOLDOUT_LABEL,
                "comparison": {"purist_correct": True, "pragmatic_correct": True},
            },
            "final": {
                "final_label": SYNTHETIC_HOLDOUT_LABEL,
                "comparison": {"purist_correct": True, "pragmatic_correct": True},
            },
        },
        "v0_reference": {
            "final_label": "1 per month",
            "comparison": {"purist_correct": False, "pragmatic_correct": False},
        },
        "transition_vs_v0": {
            "label_changed": True,
            "purist_transition": "wrong_to_correct",
        },
        "model_call_attempted": True,
        "call_error": None,
        "evidence_valid": True,
        "parse_errors": [],
        "format_repair_events": [],
        "action_render_events": [],
    }


def _synthetic_output_contract_metadata(summary: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "date": "2026-06-13",
        "split": "test",
        "split_manifest": EXPECTED_SPLIT_MANIFEST,
        "mode": "live",
        "model": EXPECTED_MODEL,
        "prompt_version": EXPECTED_PROMPT_VERSION,
        "claim_boundary": fresh_evidence_reasoner._claim_boundary_for_split("test"),
        "summary": dict(summary),
        "gate": {"status": "preflight", "interpretation": "synthetic contract check"},
    }


def _synthetic_readout_summary(summary: Mapping[str, Any]) -> dict[str, Any]:
    readout_summary = dict(summary)
    readout_summary.update(
        {
            "rows": EXPECTED_TEST_ROW_COUNT,
            "prediction_bearing_rows": EXPECTED_TEST_ROW_COUNT,
            "model_calls_attempted": EXPECTED_TEST_ROW_COUNT,
            "v0_purist_correct": 364,
            "v0_pragmatic_correct": 381,
            "raw_model_purist_correct": 383,
            "raw_model_pragmatic_correct": 386,
            "format_only_purist_correct": 383,
            "format_only_pragmatic_correct": 386,
            "final_purist_correct": 383,
            "final_pragmatic_correct": 386,
            "evidence_exact_substrings": 430,
            "net_purist_gain_vs_v0": 19,
        }
    )
    return readout_summary


def _manifest_split_count(manifest: Mapping[str, Any], split: str) -> int | None:
    split_record = manifest.get("splits", {}).get(split)
    if not isinstance(split_record, Mapping):
        return None
    count = split_record.get("count")
    if isinstance(count, int):
        return count
    source_row_indices = split_record.get("source_row_indices")
    if isinstance(source_row_indices, Sequence):
        return len(source_row_indices)
    return None


def _manifest_split_source_indices(
    manifest: Mapping[str, Any],
    split: str,
) -> set[int] | None:
    split_record = manifest.get("splits", {}).get(split)
    if not isinstance(split_record, Mapping):
        return None
    source_row_indices = split_record.get("source_row_indices")
    if not isinstance(source_row_indices, Sequence) or isinstance(
        source_row_indices,
        (str, bytes),
    ):
        return None
    return {int(source_row_index) for source_row_index in source_row_indices}


def _check_absent_test_outputs(
    config: PreflightConfig,
    checks: list[str],
    failures: list[str],
) -> None:
    for path in (
        config.test_jsonl_path,
        config.test_report_path,
        _resume_part_path(config.test_jsonl_path),
        _resume_part_path(config.test_report_path),
    ):
        if path.exists():
            failures.append(f"test output already exists before authorized launch: {path}")
        else:
            checks.append(f"test output absent: {path}")


def _resume_part_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}.resume-part{path.suffix}")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Verify frozen V12 Gan 2026 test-audit launch conditions."
    )
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL_PATH)
    parser.add_argument("--json", action="store_true", help="Emit a JSON preflight report.")
    args = parser.parse_args(argv)

    report = run_preflight(PreflightConfig(protocol_path=args.protocol))
    if args.json:
        print(json.dumps(report.to_json_record(), indent=2, sort_keys=True))
    else:
        for check in report.checks:
            print(f"OK: {check}")
        for failure in report.failures:
            print(f"FAIL: {failure}")
    raise SystemExit(0 if report.ok else 1)


if __name__ == "__main__":
    main()
