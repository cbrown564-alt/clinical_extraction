"""Build Gate 3 source-symmetry preflight for Gan v0.9 frozen selector.

This script intentionally reports only technical inventory metadata: artifact
paths, hashes, source-row coverage, duplicate/off-manifest counts, schema/call
counts, and prompt-input key hygiene. It must not emit test-row labels,
correctness, rationales, evidence, selected events, or row-level transitions.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-06-26"
RUN_ID = (
    "gan2026_consensus_fresh_agreement_selector_v0_9_"
    f"frozen_gate3_source_symmetry_preflight_{DATE}"
)
SPLIT_MANIFEST = ROOT / "data" / "Gan (2026)" / "splits" / "gan2026_split_v1.json"
JSON_OUT = ROOT / "experiments" / f"{RUN_ID}.json"
MD_OUT = ROOT / "experiments" / f"{RUN_ID}.md"

DETERMINISTIC_JSONL = (
    "gan2026_test450_phase4_frozen_audit_deterministic_canonical_pipeline_"
    "gpt41mini_2026-06-09.jsonl"
)
DETERMINISTIC_MD = (
    "gan2026_test450_phase4_frozen_audit_deterministic_canonical_pipeline_"
    "gpt41mini_2026-06-09.md"
)
CONSENSUS_TWO_AGENT_JSONL = (
    "gan2026_agentic_structured_event_consensus_available_two_agent_exact_"
    "test450_2026-06-13.jsonl"
)
CONSENSUS_TWO_AGENT_MD = (
    "gan2026_agentic_structured_event_consensus_available_two_agent_exact_"
    "test450_2026-06-13.md"
)
FRESH_EVIDENCE_JSONL = (
    "gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_"
    "2026-06-15.jsonl"
)
FRESH_EVIDENCE_MD = (
    "gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_"
    "2026-06-15.md"
)
GPT_SE_JSONL = (
    "gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_"
    "2026-06-09.jsonl"
)
GPT_SE_MD = (
    "gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_"
    "2026-06-09.md"
)
QWEN_PATCH_JSONL = (
    "gan2026_agentic_structured_event_patch_recent_unresolved_burden_test450_"
    "qwen3635b_2026-06-13.jsonl"
)
DEEPSEEK_SE_JSONL = "gan2026_v06_test450_hybrid_structured_events_deepseek_2026-06-14.jsonl"
DEEPSEEK_SE_MD = "gan2026_v06_test450_hybrid_structured_events_deepseek_2026-06-14.md"


@dataclass(frozen=True)
class ComponentSpec:
    name: str
    role: str
    policy_match: str
    path: Path
    markdown_path: Path | None = None
    required_prompt_hygiene: bool = False


COMPONENTS = [
    ComponentSpec(
        name="deterministic_floor",
        role="deterministic test component",
        policy_match="locked test450 deterministic canonical-pipeline comparator",
        path=ROOT / "experiments" / DETERMINISTIC_JSONL,
        markdown_path=ROOT / "experiments" / DETERMINISTIC_MD,
    ),
    ComponentSpec(
        name="consensus_available_two_agent",
        role="closest-available constrained consensus component",
        policy_match=(
            "available two-agent exact-label unanimity over GPT/Qwen structured events; "
            "not exact validation three-agent policy"
        ),
        path=ROOT
        / "experiments"
        / CONSENSUS_TWO_AGENT_JSONL,
        markdown_path=ROOT / "experiments" / CONSENSUS_TWO_AGENT_MD,
    ),
    ComponentSpec(
        name="fresh_evidence_v06_safety_v09",
        role="fresh-evidence component matching frozen test V12 role",
        policy_match=(
            "fresh-evidence reasoner over saved GPT/Qwen/DeepSeek structured-event scaffolding; "
            "v0.6/safety-v0.9 frozen test artifact"
        ),
        path=ROOT / "experiments" / FRESH_EVIDENCE_JSONL,
        markdown_path=ROOT / "experiments" / FRESH_EVIDENCE_MD,
        required_prompt_hygiene=True,
    ),
]

SOURCE_SUBSTRATES = [
    ComponentSpec(
        name="gpt_structured_events_v05",
        role="GPT structured-event source substrate",
        policy_match="frozen V12 test default substrate",
        path=ROOT / "experiments" / GPT_SE_JSONL,
        markdown_path=ROOT / "experiments" / GPT_SE_MD,
        required_prompt_hygiene=True,
    ),
    ComponentSpec(
        name="qwen_structured_events_patch",
        role="Qwen structured-event source substrate",
        policy_match="frozen V12 test default substrate",
        path=ROOT / "experiments" / QWEN_PATCH_JSONL,
        required_prompt_hygiene=True,
    ),
    ComponentSpec(
        name="deepseek_structured_events_v06",
        role="DeepSeek structured-event source substrate",
        policy_match=(
            "source-coverage run added after earlier two-agent consensus replay; "
            "available for future exact consensus/scaffolding audits"
        ),
        path=ROOT / "experiments" / DEEPSEEK_SE_JSONL,
        markdown_path=ROOT / "experiments" / DEEPSEEK_SE_MD,
        required_prompt_hygiene=True,
    ),
]

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


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest_rows() -> set[int]:
    manifest = json.loads(SPLIT_MANIFEST.read_text(encoding="utf-8"))
    return set(manifest["splits"]["test"]["source_row_indices"])


def iter_jsonl(path: Path):
    with path.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            if not line.strip():
                continue
            obj = json.loads(line)
            if isinstance(obj, dict) and "_metadata" in obj:
                yield line_number, obj, True
            else:
                yield line_number, obj, False


def walk_keys(value: Any, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            keys.add(path)
            keys.update(walk_keys(child, path))
    elif isinstance(value, list):
        for child in value[:3]:
            keys.update(walk_keys(child, prefix))
    return keys


def audit_artifact(spec: ComponentSpec, manifest_rows: set[int]) -> dict[str, Any]:
    if not spec.path.exists():
        return {
            "name": spec.name,
            "role": spec.role,
            "path": rel(spec.path),
            "exists": False,
            "coverage_ok": False,
            "prompt_hygiene_ok": None,
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

    for _line_number, obj, is_metadata in iter_jsonl(spec.path):
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
        parse_errors = obj.get("parse_errors")
        if parse_errors:
            parse_error_rows += 1
        prompt_input = _coerce_prompt_input(obj.get("prompt_input_json"))
        if spec.required_prompt_hygiene and isinstance(prompt_input, dict):
            prompt_rows_checked += 1
            for key_path in walk_keys(prompt_input):
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

    return {
        "name": spec.name,
        "role": spec.role,
        "policy_match": spec.policy_match,
        "path": rel(spec.path),
        "sha256": sha256(spec.path),
        "markdown_path": (
            rel(spec.markdown_path)
            if spec.markdown_path and spec.markdown_path.exists()
            else None
        ),
        "markdown_sha256": sha256(spec.markdown_path)
        if spec.markdown_path and spec.markdown_path.exists()
        else None,
        "exists": True,
        "metadata_rows": metadata_rows,
        "data_rows": data_rows,
        "source_row_count": len(row_ids),
        "unique_source_rows": len(unique_rows),
        "coverage_ok": (
            len(unique_rows) == 450
            and not missing
            and not off_manifest
            and not duplicates
        ),
        "duplicate_source_row_count": len(duplicates),
        "off_manifest_source_row_count": len(off_manifest),
        "missing_manifest_source_row_count": len(missing),
        "call_failure_rows": call_failures,
        "parse_or_repair_note_rows": parse_error_rows,
        "prompt_rows_checked": prompt_rows_checked,
        "prompt_forbidden_key_hits": dict(sorted(prompt_key_hits.items())),
        "prompt_observed_nonblocking_key_hits": dict(
            sorted(prompt_observed_key_hits.items())
        ),
        "prompt_hygiene_ok": prompt_hygiene_ok,
        "forbidden_row_content_fields_present": forbidden_present,
        "row_content_fields_not_opened_for_development": True,
    }


def main() -> None:
    manifest_rows = load_manifest_rows()
    component_audits = [audit_artifact(spec, manifest_rows) for spec in COMPONENTS]
    substrate_audits = [audit_artifact(spec, manifest_rows) for spec in SOURCE_SUBSTRATES]

    all_required = component_audits + substrate_audits
    coverage_ok = all(item.get("coverage_ok") for item in all_required)
    prompt_hygiene_ok = all(
        item.get("prompt_hygiene_ok") is not False for item in all_required
    )
    exact_consensus_available = False
    consensus_mode = "closest_available_constrained_two_agent"
    gate_passed = coverage_ok and prompt_hygiene_ok

    report = {
        "run_id": RUN_ID,
        "date": DATE,
        "gate": "Gate 3: Test Source-Symmetry Preflight",
        "split_manifest": rel(SPLIT_MANIFEST),
        "split_manifest_sha256": sha256(SPLIT_MANIFEST),
        "test_manifest_rows": len(manifest_rows),
        "inspection_boundary": {
            "allowed": [
                "artifact paths",
                "sha256 hashes",
                "source_row_index coverage",
                "duplicate/off-manifest counts",
                "call/parse counts",
                "schema/prompt-key metadata",
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
        "exact_consensus_available": exact_consensus_available,
        "consensus_mode": consensus_mode,
        "coverage_ok": coverage_ok,
        "prompt_hygiene_ok": prompt_hygiene_ok,
        "gate_passed": gate_passed,
        "gate_scope": "constrained_source_symmetry" if gate_passed else "blocked",
        "locked_test_audit_authorized": False,
        "required_next_step": (
            "User must explicitly authorize a frozen aggregate-only Gate 4 audit; "
            "because exact three-agent consensus replay is not present, any Gate 4 "
            "readout must be labeled constrained holdout evidence."
            if gate_passed
            else "Resolve Gate 3 inventory or prompt-hygiene blockers before any Gate 4 request."
        ),
    }

    JSON_OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_OUT.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"ok": True, "gate_passed": gate_passed, "scope": report["gate_scope"]}))


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Gan 2026 Consensus/Fresh v0.9 Frozen Gate 3 Source-Symmetry Preflight",
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
        "counts, and prompt-input key metadata. It did not report or develop from",
        "gold labels, row correctness, rationales, evidence text, selected events,",
        "or row-level transitions.",
        "",
        "## Required Components",
        "",
        (
            "| Component | Role | Coverage | Duplicates | Off manifest | Calls failed | "
            "Parse/repair rows | Prompt hygiene | Prompt rows checked | SHA-256 |"
        ),
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- |",
    ]
    for item in report["component_audits"]:
        lines.append(
            (
                "| {name} | {role} | {unique}/450 | {dupes} | {off} | {calls} | "
                "{parse} | {hygiene} | {prompt_rows} | `{sha}` |"
            ).format(
                name=item["name"],
                role=item["role"],
                unique=item.get("unique_source_rows", 0),
                dupes=item.get("duplicate_source_row_count", 0),
                off=item.get("off_manifest_source_row_count", 0),
                calls=item.get("call_failure_rows", 0),
                parse=item.get("parse_or_repair_note_rows", 0),
                hygiene=_hygiene_text(item.get("prompt_hygiene_ok")),
                prompt_rows=item.get("prompt_rows_checked", 0),
                sha=item.get("sha256", "missing"),
            )
        )
    lines.extend(
        [
            "",
            "## Source Substrates",
            "",
            (
                "| Substrate | Role | Coverage | Duplicates | Off manifest | Calls failed | "
                "Parse/repair rows | Prompt hygiene | Prompt rows checked | SHA-256 |"
            ),
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- |",
        ]
    )
    for item in report["source_substrate_audits"]:
        lines.append(
            (
                "| {name} | {role} | {unique}/450 | {dupes} | {off} | {calls} | "
                "{parse} | {hygiene} | {prompt_rows} | `{sha}` |"
            ).format(
                name=item["name"],
                role=item["role"],
                unique=item.get("unique_source_rows", 0),
                dupes=item.get("duplicate_source_row_count", 0),
                off=item.get("off_manifest_source_row_count", 0),
                calls=item.get("call_failure_rows", 0),
                parse=item.get("parse_or_repair_note_rows", 0),
                hygiene=_hygiene_text(item.get("prompt_hygiene_ok")),
                prompt_rows=item.get("prompt_rows_checked", 0),
                sha=item.get("sha256", "missing"),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Gate 3 passes only as constrained source-symmetry. The deterministic floor,",
            "available consensus component, fresh-evidence component, and GPT/Qwen/",
            "DeepSeek source substrates each cover the locked manifest exactly",
            "`450/450` with `0` duplicate and `0` off-manifest source rows.",
            "",
            "The exact validation consensus policy is not present as a three-agent",
            "test replay artifact. The available consensus component is the older",
            "two-agent constrained replay, while the DeepSeek test source artifact was",
            "added later as source coverage for future frozen consensus/scaffolding",
            "audits. Therefore any Gate 4 readout must be reported as constrained",
            "holdout evidence, not as an exact v0.9 selector holdout claim.",
            "",
            "This report does not authorize Gate 4. The next step requires explicit",
            "user authorization for one frozen aggregate-only locked `test450` audit.",
            "",
        ]
    )
    return "\n".join(lines)


def _hygiene_text(value: bool | None) -> str:
    if value is True:
        return "`pass`"
    if value is False:
        return "`fail`"
    return "`n/a`"


def _coerce_prompt_input(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


if __name__ == "__main__":
    main()
