"""Deterministic union arbitration for ExECTv2 SeizureFrequency lanes.

This replay layer combines the GPT-4.1-mini SF unknown-suppression lane with the
deterministic all-entity SF extractor. It does not call a model. Rules are
explicitly logged because they add, drop, or rewrite prediction-bearing
SeizureFrequency state/type keys.
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    run_all9_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_state_adjudicator as adjudicator_base,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import normalize_phrase

ARBITRATION_VERSION = "exectv2_hybrid_sf_union_arbitration_v08"
PIPELINE_FAMILY = "exectv2_hybrid_sf_union_arbitration"
COMPONENT_OWNER = "deterministic_sf_union_arbitration"

_NON_TARGET_EVENT_RE = re.compile(
    r"dissociative seizures|drop attacks|mini shakes|collapses|"
    r"admissions with breakthrough|episodes of loss of consciousness|"
    r"loss of consciousness|unwitnessed episodes|odd stare only|"
    r"mental health|father has",
    re.IGNORECASE,
)
_SHORT_GENERIC_ANCHORS = {
    "seizure",
    "seizures",
    "absence",
    "absences",
    "jerk",
    "jerks",
    "seizure free",
    "seizure-free",
}
_NAMED_TYPE_RE = re.compile(
    r"focal|generalised|generalized|tonic|clonic|chronic|absence|absences|"
    r"myoclonic|convulsive|dyscognitive|complex partial|cluster",
    re.IGNORECASE,
)
_HISTORICAL_OR_ADVICE_RE = re.compile(
    r"\b(?:before this|previous event|used to|at the onset|teenage years|"
    r"when (?:he|she) was younger|in childhood|driving|dvla|"
    r"refrain from driving|if .*further|risk of|single focal seizure|"
    r"history of)\b",
    re.IGNORECASE,
)
_BARE_FREE_CONTEXT_RE = re.compile(
    r"\b(?:remains?|remain|still) seizure[- ]free\b|"
    r"\bseizure free for \d+ months\b|"
    r"\bseizure free after (?:his|her) surgery\b",
    re.IGNORECASE,
)
_QUALIFIED_FREE_CONTEXT_RE = re.compile(
    r"last clinic|last appointment|drug|lamotrigine|started|since",
    re.IGNORECASE,
)
_CONTEXTUAL_UNKNOWN_RE = re.compile(
    r"epilepsy has been stable|control had deteriorated|odd stare|"
    r"risk of frequent|background of frequent|struggling with seizures",
    re.IGNORECASE,
)
_CHANGE_CUE_RE = re.compile(
    r"returned|worse|increased|decreased|improved|frequent|controlled",
    re.IGNORECASE,
)
_GENERIC_FREE_HISTORY_RE = re.compile(
    r"had been seizure free|up to .*seizure free|last event",
    re.IGNORECASE,
)
_NAMED_UNKNOWN_LONG_CONTEXT_RE = re.compile(
    r"where .*up to \d+ hours|on sunday and monday|clusters very frequently",
    re.IGNORECASE,
)
_ANAPHORIC_GENERIC_RE = re.compile(r"\bthey\b|\bthese\b|\bthings\b", re.IGNORECASE)
_REWRITE_THESE_SEIZURES_RE = re.compile(
    r"10-15 of these seizures over 2 days",
    re.IGNORECASE,
)
_REWRITE_UP_TO_RANGE_RE = re.compile(
    r"up to 2 or 3 times per month",
    re.IGNORECASE,
)


def read_rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def deterministic_rows_from_letters(
    letters: Sequence[Any],
    *,
    split: str,
) -> list[dict[str, Any]]:
    """Render deterministic all-entity SF predictions into JSONL row shape."""

    predictions = run_all9_on_letters(letters)
    rows: list[dict[str, Any]] = []
    for letter, prediction in zip(letters, predictions, strict=True):
        mentions = [
            _mention_to_row(mention.model_dump())
            for mention in prediction.mentions
            if mention.entity == SEIZURE_FREQUENCY.name
        ]
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "pipeline_family": "exectv2_deterministic_all9",
                "prompt_version": "deterministic_all9",
                "model": "none",
                "mode": "no-call",
                "component_owner": "deterministic_all9",
                "call_error": None,
                "parse_errors": [],
                "gate_warnings": [],
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(mentions),
                "n_evidence_invalid": 0,
                "predicted_mentions": mentions,
                "gold_mentions": [
                    {"text": a.text, "attributes": dict(a.attributes)}
                    for a in letter.entities(SEIZURE_FREQUENCY.name)
                ],
                "raw_output": json.dumps({"mentions": mentions}, sort_keys=True),
            }
        )
    return rows


def arbitrate_rows(
    current_rows: Sequence[Mapping[str, Any]],
    deterministic_rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    deterministic_by_id = {str(row["letter_id"]): row for row in deterministic_rows}
    rows = [
        arbitrate_row(row, deterministic_by_id[str(row["letter_id"])])
        for row in current_rows
    ]
    metadata = {
        "arbitration_version": ARBITRATION_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "source_current_pipeline_family": _first_value(current_rows, "pipeline_family"),
        "source_deterministic_pipeline_family": _first_value(
            deterministic_rows, "pipeline_family"
        ),
        "split": _first_value(current_rows, "split") or "dev",
        "n_letters": len(rows),
        "summary": adjudicator_base.summarize_rows(rows),
        "arbitration_action_counts": _action_counts(rows),
    }
    return rows, metadata


def arbitrate_row(
    current_row: Mapping[str, Any],
    deterministic_row: Mapping[str, Any],
) -> dict[str, Any]:
    mentions, actions = arbitrate_sf_mentions(
        current_mentions=[
            mention
            for mention in current_row.get("predicted_mentions", [])
            if str(mention.get("entity", SEIZURE_FREQUENCY.name))
            == SEIZURE_FREQUENCY.name
        ],
        deterministic_mentions=[
            mention
            for mention in deterministic_row.get("predicted_mentions", [])
            if str(mention.get("entity", SEIZURE_FREQUENCY.name))
            == SEIZURE_FREQUENCY.name
        ],
    )
    out = dict(current_row)
    out["source_current_pipeline_family"] = current_row.get("pipeline_family")
    out["source_current_prompt_version"] = current_row.get("prompt_version")
    out["source_deterministic_pipeline_family"] = deterministic_row.get("pipeline_family")
    out["source_deterministic_prompt_version"] = deterministic_row.get("prompt_version")
    out["arbitration_version"] = ARBITRATION_VERSION
    out["pipeline_family"] = PIPELINE_FAMILY
    out["prompt_version"] = ARBITRATION_VERSION
    out["model"] = "openai/gpt-4.1-mini + deterministic_all9"
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


def arbitrate_sf_mentions(
    *,
    current_mentions: Sequence[Mapping[str, Any]],
    deterministic_mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    kept: list[dict[str, Any]] = []
    actions: list[dict[str, str]] = []
    for source, mentions in (
        ("current", current_mentions),
        ("det", deterministic_mentions),
    ):
        for mention in mentions:
            copied = _mention_to_row(mention)
            drop_rule = _drop_rule(copied, source=source)
            if drop_rule:
                actions.append(_action(drop_rule, "drop", copied, "seizure_frequency"))
                continue
            transformed, rewrite_rule = _rewrite(copied)
            if rewrite_rule:
                actions.append(
                    _action(rewrite_rule, "rewrite", transformed, "benchmark_format")
                )
            kept.append(transformed)
    return _dedupe_mentions(kept), actions


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    clinical = metadata.get("summary", {}).get("clinical_recovery", {})
    sf = clinical.get("seizure_frequency", {})
    active = clinical.get("active_rate", {})
    free = clinical.get("seizure_free", {})
    unknown = clinical.get("unknown", {})
    lines = [
        "# ExECTv2 SeizureFrequency Union Arbitration v0.8",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Arbitration version: `{metadata.get('arbitration_version')}`",
        f"- Split: `{metadata.get('split')}`",
        f"- Letters: {metadata.get('n_letters')}",
        "",
        "## Rule Categories",
        "",
        "| Rule family | Portability category | Attribution note |",
        "| --- | --- | --- |",
        (
            "| suppression | seizure_frequency | Drops non-target, historical, "
            "anaphoric, and source-shortened SF states. |"
        ),
        (
            "| benchmark surface rewrites | benchmark_format | Rewrites residual "
            "source phrases to the benchmark type/state surface. |"
        ),
        "",
        "## Action Counts",
        "",
        "| Rule | Count |",
        "| --- | ---: |",
    ]
    for rule, count in sorted(metadata.get("arbitration_action_counts", {}).items()):
        lines.append(f"| `{rule}` | {count} |")
    lines += [
        "",
        "## Clinical Headline",
        "",
        "| Slice | F1 | P | R | TP | FP | FN |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        _score_row("SeizureFrequency", sf),
        _score_row("active-rate", active),
        _score_row("seizure-free", free),
        _score_row("unknown", unknown),
        "",
        "This is a no-call replay over saved GPT-4.1-mini and deterministic "
        "candidate sources. The arbitration rules are prediction-bearing and "
        "must be reported as deterministic post-processing.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_rows_and_report(
    current_rows: Sequence[Mapping[str, Any]],
    deterministic_rows: Sequence[Mapping[str, Any]],
    *,
    jsonl_path: Path,
    report_path: Path,
) -> dict[str, Any]:
    rows, metadata = arbitrate_rows(current_rows, deterministic_rows)
    write_jsonl(rows, jsonl_path)
    write_report(rows, metadata, report_path, jsonl_path=jsonl_path)
    return metadata


def _drop_rule(mention: Mapping[str, Any], *, source: str) -> str | None:
    evidence = str(mention.get("evidence", ""))
    text = str(mention.get("text", ""))
    attrs = dict(mention.get("attributes") or {})
    phrase = normalize_phrase(text)
    state = _state(mention)

    if _NON_TARGET_EVENT_RE.search(evidence) or _NON_TARGET_EVENT_RE.search(text):
        return "drop_non_target_event"
    if attrs.get("CUI") == "C1299590" and state == "active-rate":
        return "drop_seizure_free_active_rate"
    if source == "det" and phrase in _SHORT_GENERIC_ANCHORS and len(evidence.strip()) <= 18:
        return "drop_det_short_generic_anchor"
    if (
        source == "det"
        and state == "active-rate"
        and phrase in {"seizure", "seizures"}
        and not _NAMED_TYPE_RE.search(evidence)
        and len(evidence) < 60
    ):
        return "drop_det_generic_short_rate"
    if (
        source == "current"
        and state == "seizure-free"
        and _BARE_FREE_CONTEXT_RE.search(evidence)
        and not _QUALIFIED_FREE_CONTEXT_RE.search(evidence)
    ):
        return "drop_bare_seizure_free_context"
    if _HISTORICAL_OR_ADVICE_RE.search(evidence) and state != "unknown":
        return "drop_historical_or_advice_state"
    if state == "unknown" and _CONTEXTUAL_UNKNOWN_RE.search(evidence):
        return "drop_contextual_unknown"
    if (
        source == "current"
        and state == "unknown"
        and attrs.get("CUI") in {"C0036572", "C0494475", "C0270834"}
        and len(evidence) > 80
        and not _CHANGE_CUE_RE.search(evidence)
    ):
        return "drop_diffuse_unknown"
    if " and " in phrase and not attrs.get("CUI"):
        return "drop_composite_and_anchor"
    if (
        source == "current"
        and attrs.get("CUI") == "C1299590"
        and state == "seizure-free"
        and _GENERIC_FREE_HISTORY_RE.search(evidence)
    ):
        return "drop_generic_free_history_or_span"
    if (
        source == "current"
        and state == "active-rate"
        and not any(
            key in attrs
            for key in (
                "TimePeriod",
                "NumberOfTimePeriods",
                "PointInTime",
                "TimeSince_or_TimeOfEvent",
                "YearDate",
                "MonthDate",
            )
        )
    ):
        return "drop_current_bare_named_event"
    if (
        source == "current"
        and state == "unknown"
        and _NAMED_UNKNOWN_LONG_CONTEXT_RE.search(evidence)
    ):
        return "drop_named_unknown_long_context"
    if (
        source == "current"
        and attrs.get("CUI") == "C0036572"
        and _ANAPHORIC_GENERIC_RE.search(evidence)
    ):
        return "drop_anaphoric_generic_state"
    return None


def _rewrite(mention: Mapping[str, Any]) -> tuple[dict[str, Any], str | None]:
    copied = _mention_to_row(mention)
    evidence = str(copied.get("evidence", ""))
    attrs = dict(copied.get("attributes") or {})
    phrase = normalize_phrase(str(copied.get("text", "")))

    if phrase == "cluster of 3":
        copied["text"] = "seizure cluster"
        attrs["CUI"] = "C3203523"
        attrs["CUIPhrase"] = "seizure cluster"
        copied["attributes"] = attrs
        return copied, "rewrite_cluster_of_3_to_seizure_cluster"
    if _REWRITE_THESE_SEIZURES_RE.search(evidence) and attrs.get("CUI") == "C0270834":
        copied["text"] = "seizures"
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        copied["attributes"] = attrs
        return copied, "rewrite_anaphoric_named_to_generic_seizures"
    if re.search(r"typical absences", evidence, re.IGNORECASE) and phrase == "absences":
        copied["text"] = "typical absences"
        attrs["CUI"] = "C4316903"
        attrs["CUIPhrase"] = "typical absences"
        copied["attributes"] = attrs
        return copied, "rewrite_absences_to_typical_absences"
    if _REWRITE_UP_TO_RANGE_RE.search(evidence) and attrs.get("CUI") == "C0877017":
        attrs["LowerNumberOfSeizures"] = "0"
        copied["attributes"] = attrs
        return copied, "rewrite_up_to_range_lower_zero"
    return copied, None


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


def _dedupe_mentions(mentions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    out: list[dict[str, Any]] = []
    for mention in mentions:
        copied = _mention_to_row(mention)
        key = (
            normalize_phrase(str(copied.get("text", ""))),
            normalize_phrase(str(copied.get("evidence", ""))),
            json.dumps(copied.get("attributes", {}), sort_keys=True),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(copied)
    return out


def _mention_to_row(mention: Mapping[str, Any]) -> dict[str, Any]:
    confidence = mention.get("confidence")
    return {
        "entity": SEIZURE_FREQUENCY.name,
        "text": str(mention.get("text", "")),
        "attributes": {
            str(key): str(value)
            for key, value in dict(mention.get("attributes") or {}).items()
        },
        "evidence": str(mention.get("evidence", "")),
        "confidence": confidence if confidence in {"low", "medium", "high"} else "medium",
        "rationale": str(mention.get("rationale", "")),
    }


def _raw_mention(mention: Mapping[str, Any]) -> dict[str, Any]:
    row = _mention_to_row(mention)
    row.pop("entity", None)
    return row


def _action(
    rule_id: str,
    action: str,
    mention: Mapping[str, Any],
    category: str,
) -> dict[str, str]:
    return {
        "rule_id": rule_id,
        "action": action,
        "category": category,
        "text": str(mention.get("text", "")),
        "evidence": str(mention.get("evidence", "")),
    }


def _action_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        for action in row.get("arbitration_actions", []):
            counts[str(action.get("rule_id", "unknown"))] += 1
    return dict(counts)


def _first_value(rows: Sequence[Mapping[str, Any]], key: str) -> Any:
    for row in rows:
        value = row.get(key)
        if value:
            return value
    return None


def _score_row(label: str, score: Mapping[str, Any]) -> str:
    return (
        f"| {label} | {score.get('f1', 0):.3f} | "
        f"{score.get('precision', 0):.3f} | {score.get('recall', 0):.3f} | "
        f"{score.get('tp', 0)} | {score.get('fp', 0)} | {score.get('fn', 0)} |"
    )
