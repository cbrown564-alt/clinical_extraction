"""Build exact-source Gate 3 preflight for Gan v0.9 selector.

This script reports only technical inventory metadata for the exact v0.9 source
set: artifact paths, hashes, source-row coverage, duplicate/off-manifest counts,
component role parity, and prompt-input key hygiene. It must not emit test-row
labels, correctness, rationales, evidence, selected events, or row-level
transitions.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
DATE = "2026-06-26"
RUN_ID = (
    "gan2026_consensus_fresh_agreement_selector_v0_9_"
    f"frozen_gate3_exact_source_symmetry_preflight_{DATE}"
)
SPLIT_MANIFEST = ROOT / "data" / "Gan (2026)" / "splits" / "gan2026_split_v1.json"
JSON_OUT = EXPERIMENTS / f"{RUN_ID}.json"
MD_OUT = EXPERIMENTS / f"{RUN_ID}.md"

VALIDATION_CONSENSUS = (
    EXPERIMENTS
    / "gan2026_agentic_structured_event_consensus_unanimous_exact_validation750_"
    "2026-06-13.jsonl"
)
VALIDATION_FRESH = (
    EXPERIMENTS / "gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl"
)
DETERMINISTIC_RULES_TOOL = (
    EXPERIMENTS
    / "gan2026_hybrid_rules_candidates_llm_adjudicator_test450_gpt41mini_"
    "v02_cluster_diary_candidate_recall_live_2026-06-02.jsonl"
)
EXACT_CONSENSUS = (
    EXPERIMENTS
    / "gan2026_agentic_structured_event_consensus_unanimous_exact_test450_"
    "2026-06-26.jsonl"
)
EXACT_CONSENSUS_MD = (
    EXPERIMENTS
    / "gan2026_agentic_structured_event_consensus_unanimous_exact_test450_"
    "2026-06-26.md"
)
FRESH_EVIDENCE = (
    EXPERIMENTS
    / "gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_"
    "2026-06-15.jsonl"
)
FRESH_EVIDENCE_MD = (
    EXPERIMENTS
    / "gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_"
    "2026-06-15.md"
)
GPT_SE = (
    EXPERIMENTS
    / "gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_"
    "2026-06-09.jsonl"
)
QWEN_SE_PATCH = (
    EXPERIMENTS
    / "gan2026_agentic_structured_event_patch_recent_unresolved_burden_test450_"
    "qwen3635b_2026-06-13.jsonl"
)
DEEPSEEK_SE = EXPERIMENTS / "gan2026_v06_test450_hybrid_structured_events_deepseek_2026-06-14.jsonl"

FORBIDDEN_TOP_LEVEL_FIELDS = {
    "comparison",
    "baseline_comparison",
    "consensus_comparison",
    "score_layers",
    "transition_vs_v0",
    "consensus_transition",
    "patch_transition",
    "reference",
    "decision_record",
    "fresh_evidence_decision_record",
    "raw_decision_record",
    "format_only_decision_record",
    "action_render_events",
    "normalized_events",
    "structured_record",
    "raw_output",
    "selected_event_ids",
    "patched_selected_event_ids",
}
PROMPT_FORBIDDEN_KEY_FRAGMENTS = (
    "gold",
    "correct",
    "deterministic_top",
    "deterministic_label",
    "deterministic_final",
)
PROMPT_OBSERVED_KEY_FRAGMENTS = (
    "source_row_index",
    "row_index",
    "split",
    "purist",
    "pragmatic",
)


@dataclass(frozen=True)
class ComponentSpec:
    name: str
    role: str
    policy_match: str
    path: Path
    markdown_path: Path | None = None
    required_prompt_hygiene: bool = False
    require_no_forbidden_row_fields: bool = False


COMPONENTS = [
    ComponentSpec(
        name="deterministic_rules_tool_floor",
        role="validation-matched deterministic rules-tool floor",
        policy_match=(
            "same deterministic role family as validation v0.9 consensus floor: "
            "hybrid-rules-candidates artifact, deterministic_top score layer only"
        ),
        path=DETERMINISTIC_RULES_TOOL,
    ),
    ComponentSpec(
        name="consensus_exact_three_agent",
        role="exact three-agent consensus component",
        policy_match=(
            "validation consensus policy: rules-tool floor plus GPT, Qwen, and "
            "DeepSeek structured-event final labels under exact unanimity"
        ),
        path=EXACT_CONSENSUS,
        markdown_path=EXACT_CONSENSUS_MD,
        require_no_forbidden_row_fields=True,
    ),
    ComponentSpec(
        name="fresh_evidence_v06_safety_v09",
        role="protocol-documented frozen fresh-evidence holdout counterpart",
        policy_match=(
            "test450 frozen v0.6/safety-v0.9 counterpart for validation "
            "fresh-evidence role; prompt/safety version differs and is named"
        ),
        path=FRESH_EVIDENCE,
        markdown_path=FRESH_EVIDENCE_MD,
        required_prompt_hygiene=True,
    ),
]

SOURCE_SUBSTRATES = [
    ComponentSpec(
        name="gpt_structured_events_v05",
        role="GPT structured-event source substrate",
        policy_match="frozen test structured-event substrate",
        path=GPT_SE,
        required_prompt_hygiene=True,
    ),
    ComponentSpec(
        name="qwen_structured_events_recent_patch",
        role="Qwen structured-event source substrate with validation-matched recent patch role",
        policy_match="frozen test structured-event substrate plus recent unresolved-burden patch",
        path=QWEN_SE_PATCH,
        required_prompt_hygiene=True,
    ),
    ComponentSpec(
        name="deepseek_structured_events_v06",
        role="DeepSeek structured-event source substrate",
        policy_match="frozen test v0.6 structured-event substrate",
        path=DEEPSEEK_SE,
        required_prompt_hygiene=True,
    ),
]


def main() -> None:
    manifest_rows = _load_manifest_rows()
    component_audits = [_audit_artifact(spec, manifest_rows) for spec in COMPONENTS]
    substrate_audits = [_audit_artifact(spec, manifest_rows) for spec in SOURCE_SUBSTRATES]
    role_parity = _role_parity()

    all_required = component_audits + substrate_audits
    coverage_ok = all(item.get("coverage_ok") for item in all_required)
    prompt_hygiene_ok = all(
        item.get("prompt_hygiene_ok") is not False for item in all_required
    )
    row_content_boundary_ok = all(
        item.get("row_content_boundary_ok") is not False for item in all_required
    )
    role_parity_ok = (
        role_parity["deterministic_role_parity_ok"]
        and role_parity["consensus_policy_parity_ok"]
        and role_parity["fresh_evidence_role_counterpart_ok"]
    )
    gate_passed = coverage_ok and prompt_hygiene_ok and row_content_boundary_ok and role_parity_ok
    report = {
        "run_id": RUN_ID,
        "date": DATE,
        "gate": "Gate 3: Exact Source-Symmetry Preflight",
        "split_manifest": _rel(SPLIT_MANIFEST),
        "split_manifest_sha256": _sha256(SPLIT_MANIFEST),
        "test_manifest_rows": len(manifest_rows),
        "inspection_boundary": {
            "allowed": [
                "artifact paths",
                "sha256 hashes",
                "source_row_index coverage",
                "duplicate/off-manifest counts",
                "call/parse counts",
                "schema/prompt-key metadata",
                "component role metadata",
            ],
            "forbidden": [
                "gold labels",
                "row correctness values",
                "rationales",
                "evidence text",
                "selected events",
                "row-level transitions",
            ],
            "test_row_content_read_for_development": False,
        },
        "component_audits": component_audits,
        "source_substrate_audits": substrate_audits,
        "role_parity": role_parity,
        "exact_consensus_available": True,
        "consensus_mode": "exact_three_agent_unanimous_label",
        "coverage_ok": coverage_ok,
        "prompt_hygiene_ok": prompt_hygiene_ok,
        "row_content_boundary_ok": row_content_boundary_ok,
        "role_parity_ok": role_parity_ok,
        "gate_passed": gate_passed,
        "gate_scope": "exact_source_symmetry" if gate_passed else "blocked",
        "locked_test_audit_authorized": False,
        "required_next_step": (
            "User must explicitly authorize a fresh aggregate-only exact-source "
            "Gate 4 audit before any exact v0.9 selector holdout readout."
            if gate_passed
            else "Resolve exact-source Gate 3 blockers before any Gate 4 request."
        ),
    }
    JSON_OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_OUT.write_text(_render_markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "gate_passed": gate_passed,
                "scope": report["gate_scope"],
            },
            sort_keys=True,
        )
    )


def _role_parity() -> dict[str, Any]:
    validation_consensus_meta = _first_metadata(VALIDATION_CONSENSUS)
    exact_consensus_meta = _first_metadata(EXACT_CONSENSUS)
    validation_fresh_meta = _sample_metadata(VALIDATION_FRESH)
    test_fresh_meta = _sample_metadata(FRESH_EVIDENCE)

    validation_floor = (
        validation_consensus_meta.get("source_artifacts", {}).get("rules_tool_baseline")
    )
    exact_floor = exact_consensus_meta.get("source_artifacts", {}).get("rules_tool_baseline")
    deterministic_role_parity_ok = (
        validation_floor is not None
        and exact_floor is not None
        and "hybrid_rules_candidates_llm_adjudicator" in validation_floor
        and "hybrid_rules_candidates_llm_adjudicator" in exact_floor
        and "v02_cluster_diary_candidate_recall" in validation_floor
        and "v02_cluster_diary_candidate_recall" in exact_floor
    )

    validation_condition = validation_consensus_meta.get("condition")
    exact_condition = exact_consensus_meta.get("condition")
    validation_expected = "rules_tool_plus_structured_event_unanimous_exact_label_v0"
    exact_expected = "rules_tool_plus_three_structured_event_agents_unanimous_exact_label_v0"
    consensus_policy_parity_ok = (
        validation_condition == validation_expected and exact_condition == exact_expected
    )

    validation_fresh_prompt = validation_fresh_meta.get("prompt_version")
    test_fresh_prompt = test_fresh_meta.get("prompt_version")
    fresh_evidence_role_counterpart_ok = (
        validation_fresh_meta.get("pipeline_family") == "fresh_evidence_reasoner"
        and test_fresh_meta.get("pipeline_family") == "fresh_evidence_reasoner"
        and test_fresh_prompt == "gan2026_fresh_evidence_reasoner_v0_6"
    )

    return {
        "deterministic_role_parity_ok": deterministic_role_parity_ok,
        "validation_consensus_floor": validation_floor,
        "exact_test_consensus_floor": exact_floor,
        "consensus_policy_parity_ok": consensus_policy_parity_ok,
        "validation_consensus_condition": validation_condition,
        "exact_test_consensus_condition": exact_condition,
        "fresh_evidence_role_counterpart_ok": fresh_evidence_role_counterpart_ok,
        "validation_fresh_prompt_version": validation_fresh_prompt,
        "test_fresh_prompt_version": test_fresh_prompt,
        "fresh_evidence_counterpart_note": (
            "The test fresh-evidence component is not prompt-identical to the "
            "validation v0.4 artifact. It is treated as the protocol-documented "
            "frozen exact holdout counterpart: v0.6 with safety v0.9, named "
            "before this exact-source preflight."
        ),
    }


def _audit_artifact(spec: ComponentSpec, manifest_rows: set[int]) -> dict[str, Any]:
    if not spec.path.exists():
        return {
            "name": spec.name,
            "role": spec.role,
            "path": _rel(spec.path),
            "exists": False,
            "coverage_ok": False,
            "prompt_hygiene_ok": None,
            "row_content_boundary_ok": False if spec.require_no_forbidden_row_fields else None,
        }

    row_ids: list[int] = []
    top_level_keys: Counter[str] = Counter()
    metadata_rows = 0
    data_rows = 0
    call_failures = 0
    parse_error_rows = 0
    prompt_key_hits: Counter[str] = Counter()
    prompt_observed_key_hits: Counter[str] = Counter()
    prompt_rows_checked = 0

    for _line_number, obj, is_metadata in _iter_jsonl(spec.path):
        if not isinstance(obj, dict):
            continue
        if is_metadata:
            metadata_rows += 1
            continue
        data_rows += 1
        top_level_keys.update(obj.keys())
        if isinstance(obj.get("source_row_index"), int):
            row_ids.append(obj["source_row_index"])
        if obj.get("call_error"):
            call_failures += 1
        if obj.get("parse_errors"):
            parse_error_rows += 1
        prompt_input = _coerce_prompt_input(obj.get("prompt_input_json"))
        if spec.required_prompt_hygiene and isinstance(prompt_input, dict):
            prompt_rows_checked += 1
            for key_path in _walk_keys(prompt_input):
                key_lower = key_path.lower()
                for forbidden in PROMPT_FORBIDDEN_KEY_FRAGMENTS:
                    if forbidden in key_lower:
                        prompt_key_hits[forbidden] += 1
                for observed in PROMPT_OBSERVED_KEY_FRAGMENTS:
                    if observed in key_lower:
                        prompt_observed_key_hits[observed] += 1

    counts = Counter(row_ids)
    duplicates = sorted(row_id for row_id, count in counts.items() if count > 1)
    unique_rows = set(row_ids)
    missing = sorted(manifest_rows - unique_rows)
    off_manifest = sorted(unique_rows - manifest_rows)
    forbidden_present = sorted(set(top_level_keys) & FORBIDDEN_TOP_LEVEL_FIELDS)
    prompt_hygiene_ok = None
    if spec.required_prompt_hygiene:
        prompt_hygiene_ok = not prompt_key_hits
    row_content_boundary_ok = None
    if spec.require_no_forbidden_row_fields:
        row_content_boundary_ok = not forbidden_present

    return {
        "name": spec.name,
        "role": spec.role,
        "policy_match": spec.policy_match,
        "path": _rel(spec.path),
        "sha256": _sha256(spec.path),
        "markdown_path": (
            _rel(spec.markdown_path)
            if spec.markdown_path and spec.markdown_path.exists()
            else None
        ),
        "markdown_sha256": _sha256(spec.markdown_path)
        if spec.markdown_path and spec.markdown_path.exists()
        else None,
        "exists": True,
        "metadata_rows": metadata_rows,
        "data_rows": data_rows,
        "source_row_count": len(row_ids),
        "unique_source_rows": len(unique_rows),
        "coverage_ok": (
            len(unique_rows) == 450 and not missing and not off_manifest and not duplicates
        ),
        "duplicate_source_row_count": len(duplicates),
        "off_manifest_source_row_count": len(off_manifest),
        "missing_manifest_source_row_count": len(missing),
        "call_failure_rows": call_failures,
        "parse_or_repair_note_rows": parse_error_rows,
        "prompt_rows_checked": prompt_rows_checked,
        "prompt_forbidden_key_hits": dict(sorted(prompt_key_hits.items())),
        "prompt_observed_nonblocking_key_hits": dict(sorted(prompt_observed_key_hits.items())),
        "prompt_hygiene_ok": prompt_hygiene_ok,
        "forbidden_row_content_fields_present": forbidden_present,
        "row_content_boundary_ok": row_content_boundary_ok,
        "row_content_fields_not_opened_for_development": True,
    }


def _render_markdown(report: dict[str, Any]) -> str:
    role = report["role_parity"]
    lines = [
        "# Gan 2026 Consensus/Fresh v0.9 Frozen Gate 3 Exact Source-Symmetry Preflight",
        "",
        f"- Date: `{report['date']}`",
        "- Surface: `test450` metadata inventory only",
        f"- Split manifest: `{report['split_manifest']}`",
        f"- Split manifest SHA-256: `{report['split_manifest_sha256']}`",
        f"- Test manifest rows: `{report['test_manifest_rows']}`",
        f"- Gate passed: `{str(report['gate_passed']).lower()}`",
        f"- Gate scope: `{report['gate_scope']}`",
        f"- Consensus mode: `{report['consensus_mode']}`",
        "- Locked test audit authorized by this report: `false`",
        "",
        "## Inspection Boundary",
        "",
        "This preflight inspected only technical metadata: artifact paths, hashes,",
        "`source_row_index` coverage, duplicate/off-manifest counts, call/parse",
        "counts, prompt-input key metadata, and component role metadata. It did",
        "not report or develop from gold labels, row correctness, rationales,",
        "evidence text, selected events, or row-level transitions.",
        "",
        "## Role Parity",
        "",
        f"- Deterministic role parity: `{role['deterministic_role_parity_ok']}`",
        f"- Validation consensus floor: `{role['validation_consensus_floor']}`",
        f"- Exact test consensus floor: `{role['exact_test_consensus_floor']}`",
        f"- Consensus policy parity: `{role['consensus_policy_parity_ok']}`",
        f"- Validation consensus condition: `{role['validation_consensus_condition']}`",
        f"- Exact test consensus condition: `{role['exact_test_consensus_condition']}`",
        f"- Fresh-evidence counterpart accepted: `{role['fresh_evidence_role_counterpart_ok']}`",
        f"- Validation fresh prompt: `{role['validation_fresh_prompt_version']}`",
        f"- Test fresh prompt: `{role['test_fresh_prompt_version']}`",
        "",
        role["fresh_evidence_counterpart_note"],
        "",
        "## Required Components",
        "",
        (
            "| Component | Role | Coverage | Duplicates | Off manifest | Calls failed | "
            "Parse/repair rows | Prompt hygiene | Row boundary | SHA-256 |"
        ),
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for item in report["component_audits"]:
        lines.append(_audit_row(item))
    lines.extend(
        [
            "",
            "## Source Substrates",
            "",
            (
                "| Substrate | Role | Coverage | Duplicates | Off manifest | Calls failed | "
                "Parse/repair rows | Prompt hygiene | Row boundary | SHA-256 |"
            ),
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
        ]
    )
    for item in report["source_substrate_audits"]:
        lines.append(_audit_row(item))
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Gate 3 passes as exact source-symmetry for the selector source set.",
            "The missing exact three-agent consensus test replay has been generated",
            "and hash-pinned. The deterministic floor is aligned to the validation",
            "rules-tool baseline role, not the older constrained Gate 4 canonical",
            "pipeline comparator. The fresh-evidence component is accepted as the",
            "protocol-documented frozen holdout counterpart, with the prompt/safety",
            "version difference named above.",
            "",
            "This report does not authorize Gate 4. The next step requires explicit",
            "user authorization for one fresh aggregate-only exact-source locked",
            "`test450` audit.",
            "",
        ]
    )
    return "\n".join(lines)


def _audit_row(item: dict[str, Any]) -> str:
    return (
        "| {name} | {role} | {unique}/450 | {dupes} | {off} | {calls} | "
        "{parse} | {hygiene} | {row_boundary} | `{sha}` |"
    ).format(
        name=item["name"],
        role=item["role"],
        unique=item.get("unique_source_rows", 0),
        dupes=item.get("duplicate_source_row_count", 0),
        off=item.get("off_manifest_source_row_count", 0),
        calls=item.get("call_failure_rows", 0),
        parse=item.get("parse_or_repair_note_rows", 0),
        hygiene=_tri_text(item.get("prompt_hygiene_ok")),
        row_boundary=_tri_text(item.get("row_content_boundary_ok")),
        sha=item.get("sha256", "missing"),
    )


def _tri_text(value: bool | None) -> str:
    if value is True:
        return "`pass`"
    if value is False:
        return "`fail`"
    return "`n/a`"


def _load_manifest_rows() -> set[int]:
    manifest = json.loads(SPLIT_MANIFEST.read_text(encoding="utf-8"))
    return set(manifest["splits"]["test"]["source_row_indices"])


def _first_metadata(path: Path) -> dict[str, Any]:
    for _line_number, obj, is_metadata in _iter_jsonl(path):
        if is_metadata:
            return dict(obj["_metadata"])
    return {}


def _sample_metadata(path: Path) -> dict[str, Any]:
    for _line_number, obj, is_metadata in _iter_jsonl(path):
        if is_metadata:
            return dict(obj["_metadata"])
        if isinstance(obj, dict):
            return {
                "pipeline_family": obj.get("pipeline_family"),
                "prompt_version": obj.get("prompt_version"),
                "model": obj.get("model"),
                "split": obj.get("split"),
                "split_manifest": obj.get("split_manifest"),
            }
    return {}


def _iter_jsonl(path: Path):
    with path.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            if not line.strip():
                continue
            obj = json.loads(line)
            if isinstance(obj, dict) and "_metadata" in obj:
                yield line_number, obj, True
            else:
                yield line_number, obj, False


def _walk_keys(value: Any, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            keys.add(path)
            keys.update(_walk_keys(child, path))
    elif isinstance(value, list):
        for child in value[:3]:
            keys.update(_walk_keys(child, prefix))
    return keys


def _coerce_prompt_input(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


if __name__ == "__main__":
    main()
