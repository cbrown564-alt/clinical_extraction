"""No-call arbitration for the ExECTv2 Investigations verifier lane.

This replay layer keeps the GPT-4.1-mini Investigations verifier as the source
of completed-test result mentions, then removes verifier residuals where the
mention itself says a test is pending, requested, arranged, or awaited. The
rules are prediction-bearing clinical-epilepsy rules, so each drop is logged.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    INVESTIGATIONS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_investigations_verifier as verifier_base,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)

ARBITRATION_VERSION = "exectv2_llm_investigations_arbitration_v02"
PIPELINE_FAMILY = "exectv2_llm_investigations_arbitration"
COMPONENT_OWNER = "deterministic_investigations_arbitration"

_PENDING_TEST_RE = re.compile(
    r"\b(?:will|arrang(?:e|ed|ing)|request(?:ed|ing)?|await(?:ing)?|"
    r"appointment|suggest|recommend|should update|today agreed to chase|"
    r"up to date|not yet (?:performed|received)|planned)\b",
    re.IGNORECASE,
)


def read_rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def arbitrate_rows(
    rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    arbitrated = [arbitrate_row(row) for row in rows]
    metadata = {
        "arbitration_version": ARBITRATION_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "source_pipeline_family": _first_value(rows, "pipeline_family"),
        "source_prompt_version": _first_value(rows, "prompt_version"),
        "split": _first_value(rows, "split") or "dev",
        "n_letters": len(arbitrated),
        "summary": verifier_base.summarize_rows(arbitrated),
        "arbitration_action_counts": _action_counts(arbitrated),
    }
    return arbitrated, metadata


def arbitrate_row(row: Mapping[str, Any]) -> dict[str, Any]:
    mentions, actions = arbitrate_investigations_mentions(
        [
            mention
            for mention in row.get("predicted_mentions", [])
            if str(mention.get("entity", INVESTIGATIONS.name)) == INVESTIGATIONS.name
        ]
    )
    out = dict(row)
    out["source_pipeline_family"] = row.get("pipeline_family")
    out["source_prompt_version"] = row.get("prompt_version")
    out["arbitration_version"] = ARBITRATION_VERSION
    out["pipeline_family"] = PIPELINE_FAMILY
    out["prompt_version"] = ARBITRATION_VERSION
    out["model"] = str(row.get("model") or "openai/gpt-4.1-mini")
    out["mode"] = "no-call replay"
    out["component_owner"] = COMPONENT_OWNER
    out["arbitration_actions"] = actions
    out["predicted_mentions"] = mentions
    out["n_mentions_raw"] = len(mentions)
    out["n_mentions_scored"] = len(mentions)
    out["n_evidence_invalid"] = 0
    out["raw_output"] = json.dumps(
        {"mentions": [_raw_mention(mention) for mention in mentions]},
        sort_keys=True,
    )
    return out


def arbitrate_investigations_mentions(
    mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    kept: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    for mention in mentions:
        normalized = _mention_to_row(mention)
        action = _drop_action(normalized)
        if action is not None:
            actions.append(action)
            continue
        kept.append(normalized)
    return kept, actions


def write_rows_and_report(
    rows: Sequence[Mapping[str, Any]],
    *,
    jsonl_path: Path,
    report_path: Path,
) -> dict[str, Any]:
    arbitrated, metadata = arbitrate_rows(rows)
    write_jsonl(arbitrated, jsonl_path)
    verifier_base.write_report(arbitrated, metadata, report_path, jsonl_path=jsonl_path)
    return metadata


def _drop_action(mention: Mapping[str, Any]) -> dict[str, Any] | None:
    attrs = dict(mention.get("attributes") or {})
    evidence = str(mention.get("evidence", ""))
    rationale = str(mention.get("rationale", ""))
    context = f"{evidence} {rationale}"
    if _has_performed_no(attrs) and _PENDING_TEST_RE.search(context):
        return _action(
            rule_id="drop_pending_or_planned_investigation",
            mention=mention,
        )
    if _has_unknown_result(attrs) and _PENDING_TEST_RE.search(context):
        return _action(
            rule_id="drop_requested_unknown_investigation",
            mention=mention,
        )
    return None


def _has_performed_no(attrs: Mapping[str, Any]) -> bool:
    return any(attrs.get(f"{mod}_Performed") == "No" for mod in ("MRI", "CT", "EEG"))


def _has_unknown_result(attrs: Mapping[str, Any]) -> bool:
    return any(attrs.get(f"{mod}_Results") == "Unknown" for mod in ("MRI", "CT", "EEG"))


def _action(*, rule_id: str, mention: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "category": "clinical_epilepsy",
        "text": str(mention.get("text", "")),
        "evidence": str(mention.get("evidence", "")),
        "attributes": dict(mention.get("attributes") or {}),
    }


def _mention_to_row(mention: Mapping[str, Any]) -> dict[str, Any]:
    out = {
        "entity": INVESTIGATIONS.name,
        "text": str(mention.get("text", "")),
        "attributes": dict(mention.get("attributes") or {}),
        "evidence": str(mention.get("evidence", "")),
        "confidence": str(mention.get("confidence") or "medium"),
        "rationale": str(mention.get("rationale", "")),
    }
    if "component_owner" in mention:
        out["component_owner"] = str(mention.get("component_owner"))
    return out


def _raw_mention(mention: Mapping[str, Any]) -> dict[str, Any]:
    raw = dict(mention)
    raw.pop("entity", None)
    return raw


def _action_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        for action in row.get("arbitration_actions", []):
            counts[str(action.get("rule_id", "unknown"))] += 1
    return dict(sorted(counts.items()))


def _first_value(rows: Sequence[Mapping[str, Any]], key: str) -> str:
    for row in rows:
        value = row.get(key)
        if value:
            return str(value)
    return ""
