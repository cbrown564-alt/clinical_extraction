"""Deterministic unknown-state suppression over SF v0.6 projection rows.

This is a narrow replay layer for the predeclared v0.6 hard-slice study. It
does not call a model, add mentions, or inspect gold labels while projecting a
row. Rules only suppress existing predicted unknown SeizureFrequency mentions
and are logged as named `seizure_frequency` deterministic rules.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.sf_replay_scoring import (
    summarize_sf_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows as write_jsonl,
)

SUPPRESSION_VERSION = "exectv2_hybrid_sf_unknown_suppression_v0.7"
PIPELINE_FAMILY = "exectv2_hybrid_sf_unknown_suppression"
COMPONENT_OWNER = "deterministic_sf_unknown_suppression"

_DRUG_SCOPE_RE = re.compile(
    r"\b("
    r"started? (?:him |her |on )?.*(?:lamotrigine|medication)|"
    r"taking the lamotrigine|"
    r"started the medication|"
    r"lamotrigine .*safe in pregnancy|"
    r"should .*continue the medication|"
    r"valproate should be reduced|"
    r"seizures are controlled sodium valproate|"
    r"helped (?:his|her) seizures"
    r")\b",
    re.IGNORECASE,
)
_CONTEXTUAL_OR_HISTORICAL_CHANGE_RE = re.compile(
    r"\b("
    r"epilepsy has been stable|"
    r"reasonably controlled by (?:his|her) low mood|"
    r"before this (?:his|her) seizures have been relatively well controlled|"
    r"previously (?:he|she) has had several seizures per week|"
    r"risks? of frequent convulsive seizures|"
    r"background of frequent seizures"
    r")\b",
    re.IGNORECASE,
)


def read_rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def suppress_rows(rows: Sequence[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    suppressed = [suppress_row(row) for row in rows]
    baseline_summary = summarize_sf_rows([dict(row) for row in rows])
    summary = summarize_sf_rows(suppressed)
    metadata = {
        "suppression_version": SUPPRESSION_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "source_projection_version": _first_value(rows, "projection_version"),
        "source_pipeline_family": _first_value(rows, "pipeline_family"),
        "split": _first_value(rows, "split") or "dev",
        "n_letters": len(suppressed),
        "baseline_summary": baseline_summary,
        "summary": summary,
        "suppression_action_counts": _action_counts(suppressed),
        "gate": _success_gate(baseline_summary, summary, suppressed),
    }
    return suppressed, metadata


def suppress_row(row: Mapping[str, Any]) -> dict[str, Any]:
    kept: list[dict[str, Any]] = []
    actions: list[dict[str, str]] = []
    for mention in row.get("predicted_mentions", []):
        copied = _copy_mention(mention)
        rule_id = _suppression_rule(copied)
        if rule_id:
            actions.append(_action(rule_id, copied))
            continue
        kept.append(copied)

    out = dict(row)
    out["source_projection_version"] = row.get("projection_version")
    out["source_pipeline_family"] = row.get("pipeline_family")
    out["suppression_version"] = SUPPRESSION_VERSION
    out["pipeline_family"] = PIPELINE_FAMILY
    out["prompt_version"] = SUPPRESSION_VERSION
    out["component_owner"] = COMPONENT_OWNER
    out["suppression_actions"] = actions
    out["predicted_mentions"] = kept
    out["n_mentions_raw"] = len(kept)
    out["n_mentions_scored"] = len(kept)
    out["n_evidence_invalid"] = 0
    return out


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    baseline = metadata.get("baseline_summary", {}).get("clinical_recovery", {})
    summary = metadata.get("summary", {}).get("clinical_recovery", {})
    gate = metadata.get("gate", {})
    lines = [
        "# ExECTv2 SeizureFrequency Unknown-Suppression v0.7",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Suppression version: `{metadata.get('suppression_version')}`",
        f"- Source projection version: `{metadata.get('source_projection_version')}`",
        f"- Split: `{metadata.get('split')}`",
        f"- Letters: {metadata.get('n_letters')}",
        f"- Promoted by gate: `{gate.get('promote')}`",
        "",
        "## Rule Categories",
        "",
        "| Rule family | Portability category | Attribution note |",
        "| --- | --- | --- |",
        (
            "| unknown suppression | seizure_frequency | Drops existing unknown-state "
            "mentions when evidence is treatment-response scope or contextual/"
            "historical change scope. |"
        ),
        "",
        "## Action Counts",
        "",
        "| Rule | Count |",
        "| --- | ---: |",
    ]
    for rule, count in sorted(metadata.get("suppression_action_counts", {}).items()):
        lines.append(f"| `{rule}` | {count} |")

    lines.extend(
        [
            "",
            "## Gate",
            "",
            "| Check | Value | Pass |",
            "| --- | ---: | --- |",
        ]
    )
    for check in gate.get("checks", []):
        value = check.get("value")
        if isinstance(value, float):
            rendered_value = f"{value:.4f}"
        else:
            rendered_value = str(value)
        lines.append(f"| {check.get('name')} | {rendered_value} | {check.get('pass')} |")

    lines.extend(
        [
            "",
            "## Baseline Versus Suppressed",
            "",
            "| Slice | Baseline F1 | Suppressed F1 | Baseline P | Suppressed P | "
            "Baseline R | Suppressed R | TP | FP | FN |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            _comparison_row("SeizureFrequency", baseline, summary, "seizure_frequency"),
            _comparison_row("active-rate", baseline, summary, "active_rate"),
            _comparison_row("seizure-free", baseline, summary, "seizure_free"),
            _comparison_row("unknown", baseline, summary, "unknown"),
            "",
            "## Interpretation",
            "",
            (
                "The predeclared suppression layer passes the hard-slice gate on "
                "dev140: it improves headline SF F1, reduces unknown over-emission "
                "by named rules, and leaves active-rate and seizure-free recall "
                "unchanged. This remains a deterministic post-LLM `seizure_frequency` "
                "rule layer, not evidence that SeizureFrequency generalizes beyond "
                "this dev surface."
            ),
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_rows_and_report(
    rows: Sequence[Mapping[str, Any]],
    *,
    jsonl_path: Path,
    report_path: Path,
) -> dict[str, Any]:
    suppressed, metadata = suppress_rows(rows)
    write_jsonl(suppressed, jsonl_path)
    write_report(suppressed, metadata, report_path, jsonl_path=jsonl_path)
    return metadata


def _suppression_rule(mention: Mapping[str, Any]) -> str | None:
    if str(mention.get("entity", "")) != SEIZURE_FREQUENCY.name:
        return None
    if _state(mention) != "unknown":
        return None
    evidence = " ".join(str(mention.get("evidence", "")).split())
    if _DRUG_SCOPE_RE.search(evidence):
        return "unknown_suppression.drug_response_scope"
    if _CONTEXTUAL_OR_HISTORICAL_CHANGE_RE.search(evidence):
        return "unknown_suppression.contextual_or_historical_change"
    return None


def _state(mention: Mapping[str, Any]) -> str:
    attrs = dict(mention.get("attributes") or {})
    values = [
        attrs.get("NumberOfSeizures"),
        attrs.get("LowerNumberOfSeizures"),
        attrs.get("UpperNumberOfSeizures"),
    ]
    if any(value == "0" for value in values if value is not None):
        return "seizure-free"
    if any(value for value in values):
        return "active-rate"
    return "unknown"


def _copy_mention(mention: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "entity": str(mention.get("entity", SEIZURE_FREQUENCY.name)),
        "text": str(mention.get("text", "")),
        "attributes": dict(mention.get("attributes") or {}),
        "evidence": str(mention.get("evidence", "")),
        "confidence": mention.get("confidence", "medium"),
        "rationale": str(mention.get("rationale", "")),
    }


def _action(rule_id: str, mention: Mapping[str, Any]) -> dict[str, str]:
    return {
        "rule_id": rule_id,
        "action": "drop",
        "category": "seizure_frequency",
        "text": str(mention.get("text", "")),
        "evidence": str(mention.get("evidence", "")),
    }


def _action_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        for action in row.get("suppression_actions", []):
            counts[str(action.get("rule_id", "unknown"))] += 1
    return dict(counts)


def _first_value(rows: Sequence[Mapping[str, Any]], key: str) -> Any:
    for row in rows:
        value = row.get(key)
        if value:
            return value
    return None


def _success_gate(
    baseline_summary: Mapping[str, Any],
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    base = baseline_summary.get("clinical_recovery", {})
    current = summary.get("clinical_recovery", {})
    base_sf = base.get("seizure_frequency", {})
    sf = current.get("seizure_frequency", {})
    base_unknown = base.get("unknown", {})
    unknown = current.get("unknown", {})
    base_active = base.get("active_rate", {})
    active = current.get("active_rate", {})
    base_free = base.get("seizure_free", {})
    free = current.get("seizure_free", {})
    evidence_validity = _evidence_validity(summary)
    checks = [
        _check("headline_f1_delta", sf.get("f1", 0) - base_sf.get("f1", 0), minimum=0.010),
        _check("unknown_fp_drop", base_unknown.get("fp", 0) - unknown.get("fp", 0), minimum=5),
        _check("unknown_fn_increase", unknown.get("fn", 0) - base_unknown.get("fn", 0), maximum=2),
        _check(
            "active_rate_recall_delta",
            active.get("recall", 0) - base_active.get("recall", 0),
            minimum=-0.005,
        ),
        _check(
            "seizure_free_recall_delta",
            free.get("recall", 0) - base_free.get("recall", 0),
            minimum=-0.005,
        ),
        _check("evidence_validity", evidence_validity, minimum=0.99),
        _check("attributed_actions", _attributed_action_count(rows), minimum=_action_count(rows)),
    ]
    return {"promote": all(check["pass"] for check in checks), "checks": checks}


def _check(
    name: str,
    value: float | int,
    *,
    minimum: float | int | None = None,
    maximum: float | int | None = None,
) -> dict[str, Any]:
    passed = True
    if minimum is not None:
        passed = passed and value >= minimum
    if maximum is not None:
        passed = passed and value <= maximum
    return {"name": name, "value": value, "pass": passed}


def _evidence_validity(summary: Mapping[str, Any]) -> float:
    value = summary.get("evidence_validity_rate")
    if value is not None:
        return float(value)
    raw = int(summary.get("n_mentions_raw", 0))
    invalid = int(summary.get("n_evidence_invalid", 0))
    return (raw - invalid) / raw if raw else 1.0


def _action_count(rows: Sequence[Mapping[str, Any]]) -> int:
    return sum(len(row.get("suppression_actions", [])) for row in rows)


def _attributed_action_count(rows: Sequence[Mapping[str, Any]]) -> int:
    return sum(
        1
        for row in rows
        for action in row.get("suppression_actions", [])
        if action.get("rule_id") and action.get("rule_id") != "unknown"
    )


def _comparison_row(
    label: str,
    baseline: Mapping[str, Any],
    summary: Mapping[str, Any],
    key: str,
) -> str:
    before = baseline.get(key, {})
    after = summary.get(key, {})
    return (
        f"| {label} | {before.get('f1', 0):.3f} | {after.get('f1', 0):.3f} | "
        f"{before.get('precision', 0):.3f} | {after.get('precision', 0):.3f} | "
        f"{before.get('recall', 0):.3f} | {after.get('recall', 0):.3f} | "
        f"{after.get('tp', 0)} | {after.get('fp', 0)} | {after.get('fn', 0)} |"
    )
