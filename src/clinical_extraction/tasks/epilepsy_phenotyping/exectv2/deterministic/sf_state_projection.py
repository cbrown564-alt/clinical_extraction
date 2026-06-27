"""Deterministic state/ownership projection over SF state-adjudicator rows.

This is an attribution-preserving replay layer for the saved v0.5
SeizureFrequency state-adjudicator output. It does not call a model and it does
not inspect gold labels while projecting a row. Rules are deliberately finite
and ablatable because they change prediction-bearing SeizureFrequency state or
ownership conventions.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_state_adjudicator as adjudicator_base,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
PROJECTION_VERSION = "exectv2_hybrid_sf_state_projection_v0.6"
PIPELINE_FAMILY = "exectv2_hybrid_sf_state_projection"
COMPONENT_OWNER = "deterministic_sf_state_ownership_projection"

ProjectionAblation = Literal["none", "state", "ownership", "combined"]

_GENERIC_CUIS = {"C0036572", "C1299590"}
_UNLABELLED_EVENT_RE = re.compile(
    r"\b(attacks?|episodes?|events?|turns?|stares?|blackouts?|loss of consciousness)\b",
    re.IGNORECASE,
)
_SEIZURE_WORD_RE = re.compile(
    r"\b(seizures?|seizure[- ]free|absence|absences|myoclonic|tonic[- ]clonic|"
    r"tonic[- ]chronic|focal|convulsive|dyscognitive|complex partial)\b",
    re.IGNORECASE,
)
_NAMED_TYPE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"\bfocal\s+to\s+bilateral\s+convulsive\s+seizures?\b", re.I),
        "focal to bilateral convulsive seizures",
    ),
    (
        re.compile(r"\bgeneralised\s+tonic[- ](?:clonic|chronic)\s+seizures?\b", re.I),
        "generalised tonic clonic seizures",
    ),
    (
        re.compile(r"\bgeneralized\s+tonic[- ](?:clonic|chronic)\s+seizures?\b", re.I),
        "generalised tonic clonic seizures",
    ),
    (re.compile(r"\btonic[- ](?:clonic|chronic)\s+seizures?\b", re.I), "tonic clonic seizures"),
    (
        re.compile(r"\bfocal\s+seizures?\s+with\s+altered\s+awareness\b", re.I),
        "focal seizures with altered awareness",
    ),
    (re.compile(r"\bfocal\s+motor\s+seizures?\b", re.I), "focal motor seizures"),
    (re.compile(r"\bfocal\s+seizures?\b", re.I), "focal seizures"),
    (re.compile(r"\bmyoclonic\s+jerks\b", re.I), "myoclonic jerks"),
    (re.compile(r"\babsences?\b", re.I), "absences"),
    (re.compile(r"\bdyscognitive\s+seizures?\b", re.I), "dyscognitive seizures"),
    (re.compile(r"\bconvulsive\s+seizures?\b", re.I), "convulsive seizures"),
)
_WORD_NUMBER: dict[str, str] = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
}


def read_rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def project_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    ablation: ProjectionAblation = "combined",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    projected = [project_row(row, ablation=ablation) for row in rows]
    metadata = {
        "projection_version": PROJECTION_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "source_prompt_version": _first_value(rows, "prompt_version"),
        "source_pipeline_family": _first_value(rows, "pipeline_family"),
        "ablation": ablation,
        "split": _first_value(rows, "split") or "dev",
        "n_letters": len(projected),
        "summary": adjudicator_base.summarize_rows(projected),
        "projection_action_counts": _action_counts(projected),
    }
    return projected, metadata


def project_row(row: Mapping[str, Any], *, ablation: ProjectionAblation) -> dict[str, Any]:
    mentions = [_copy_mention(m) for m in row.get("predicted_mentions", [])]
    actions: list[dict[str, str]] = []

    if ablation in {"state", "combined"}:
        mentions = _apply_state_projection(row, mentions, actions)
    if ablation in {"ownership", "combined"}:
        mentions = _apply_ownership_projection(row, mentions, actions)

    mentions = _dedupe_exact_mentions(mentions)
    predicted = _project_mentions(str(row["letter_id"]), mentions)
    projected_mentions = [_mention_to_row(m) for m in predicted.mentions]

    out = dict(row)
    out["source_prompt_version"] = row.get("prompt_version")
    out["source_pipeline_family"] = row.get("pipeline_family")
    out["projection_version"] = PROJECTION_VERSION
    out["pipeline_family"] = PIPELINE_FAMILY
    out["prompt_version"] = PROJECTION_VERSION
    out["projection_ablation"] = ablation
    out["component_owner"] = COMPONENT_OWNER
    out["projection_actions"] = actions
    out["predicted_mentions"] = projected_mentions
    out["n_mentions_raw"] = len(projected_mentions)
    out["n_mentions_scored"] = len(projected_mentions)
    out["n_evidence_invalid"] = 0
    return out


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = metadata.get("summary", {})
    clinical = summary.get("clinical_recovery", {}).get("seizure_frequency", {})
    active = summary.get("clinical_recovery", {}).get("active_rate", {})
    free = summary.get("clinical_recovery", {}).get("seizure_free", {})
    unknown = summary.get("clinical_recovery", {}).get("unknown", {})
    action_counts = metadata.get("projection_action_counts", {})
    lines = [
        "# ExECTv2 SeizureFrequency State/Ownership Projection v0.6",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Projection version: `{metadata.get('projection_version')}`",
        f"- Source prompt version: `{metadata.get('source_prompt_version')}`",
        f"- Ablation: `{metadata.get('ablation')}`",
        f"- Split: `{metadata.get('split')}`",
        f"- Letters: {metadata.get('n_letters')}",
        "",
        "## Rule Categories",
        "",
        "| Rule family | Portability category | Attribution note |",
        "| --- | --- | --- |",
        (
            "| state projection | seizure_frequency | Changes active-rate / "
            "seizure-free / unknown state from explicit evidence spans. |"
        ),
        (
            "| ownership projection | seizure_frequency | Changes generic-vs-named "
            "seizure ownership from named seizure evidence. |"
        ),
        "",
        "## Action Counts",
        "",
        "| Rule | Count |",
        "| --- | ---: |",
    ]
    for rule, count in sorted(action_counts.items()):
        lines.append(f"| `{rule}` | {count} |")
    lines.extend(
        [
            "",
            "## SeizureFrequency Clinical-Recovery Headline",
            "",
            "| Target F1 | F1 | P | R | TP | FP | FN |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            (
                f"| 0.80 | {clinical.get('f1', 0):.3f} | "
                f"{clinical.get('precision', 0):.3f} | {clinical.get('recall', 0):.3f} | "
                f"{clinical.get('tp', 0)} | {clinical.get('fp', 0)} | "
                f"{clinical.get('fn', 0)} |"
            ),
            "",
            "## State Slices",
            "",
            "| State | F1 | P | R | TP | FP | FN |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            _slice_row("active-rate", active),
            _slice_row("seizure-free", free),
            _slice_row("unknown", unknown),
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _apply_state_projection(
    row: Mapping[str, Any],
    mentions: list[dict[str, Any]],
    actions: list[dict[str, str]],
) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    for mention in mentions:
        drop_rule = _state_drop_rule(mention, mentions)
        if drop_rule:
            actions.append(_action(drop_rule, "drop", mention))
            continue
        repaired = _repair_state_mention(mention)
        if repaired is not mention:
            actions.append(_action("state.last_event_active_to_seizure_free", "repair", mention))
        kept.append(repaired)

    for candidate in row.get("candidate_spans", []):
        for new_mention, rule_id in _mentions_from_candidate(candidate):
            if _has_equivalent_state_mention(kept, new_mention):
                continue
            if _same_evidence_state_present(kept, new_mention):
                continue
            if _point_anchor_already_present(kept, new_mention):
                continue
            kept.append(new_mention)
            actions.append(_action(rule_id, "add", new_mention))

    return kept


def _apply_ownership_projection(
    row: Mapping[str, Any],
    mentions: list[dict[str, Any]],
    actions: list[dict[str, str]],
) -> list[dict[str, Any]]:
    projected: list[dict[str, Any]] = []
    for mention in mentions:
        named_type = _owned_named_type(mention.get("evidence", ""))
        if named_type and _is_generic_type(mention) and _state(mention) == "active-rate":
            converted = _copy_mention(mention)
            converted["text"] = named_type
            attrs = dict(converted.get("attributes") or {})
            attrs.pop("CUI", None)
            attrs.pop("CUIPhrase", None)
            converted["attributes"] = attrs
            converted["rationale"] = _append_rationale(
                converted,
                "Deterministic ownership projection assigns the rate to the named seizure type.",
            )
            actions.append(_action("ownership.generic_active_to_named", "repair", converted))
            projected.append(converted)
        else:
            projected.append(mention)
    return projected


def _state_drop_rule(
    mention: Mapping[str, Any],
    all_mentions: Sequence[Mapping[str, Any]],
) -> str | None:
    evidence = str(mention.get("evidence", ""))
    lower = evidence.lower()
    state = _state(mention)
    if state == "active-rate" and not _SEIZURE_WORD_RE.search(evidence):
        if _UNLABELLED_EVENT_RE.search(evidence):
            return "state.drop_unlabelled_active_rate"
    historical_rate = re.search(
        r"\b(at the onset|when (?:he|she) was younger)\b",
        lower,
    )
    if state == "active-rate" and historical_rate:
        return "state.drop_historical_active_rate"
    if (
        state == "active-rate"
        and re.search(r"\b(up until|until)\b", lower)
        and any(_state(other) == "seizure-free" for other in all_mentions)
    ):
        return "state.drop_preceded_by_current_seizure_free"
    if state == "seizure-free" and re.search(
        r"\b(best period|longest period|dvla|refrain from driving)\b",
        lower,
    ):
        return "state.drop_historical_or_advice_seizure_free"
    return None


def _repair_state_mention(mention: Mapping[str, Any]) -> dict[str, Any] | Mapping[str, Any]:
    evidence = str(mention.get("evidence", ""))
    if _state(mention) != "active-rate":
        return mention
    duration = _last_event_duration(evidence)
    if duration is None:
        return mention
    number, unit = duration
    repaired = _copy_mention(mention)
    repaired["text"] = "seizure" if "seizure" in normalize_phrase(evidence).split() else "seizures"
    repaired["attributes"] = {
        "NumberOfSeizures": "0",
        "NumberOfTimePeriods": number,
        "TimePeriod": unit,
    }
    repaired["rationale"] = _append_rationale(
        repaired,
        "Deterministic state projection treats a last-event duration as seizure-free.",
    )
    return repaired


def _mentions_from_candidate(
    candidate: Mapping[str, Any],
) -> list[tuple[dict[str, Any], str]]:
    ctype = str(candidate.get("candidate_type", ""))
    evidence = str(candidate.get("evidence", "")).strip()
    if not evidence:
        return []
    out: list[tuple[dict[str, Any], str]] = []
    if ctype in {"generic_qualitative_change", "named_qualitative_change"}:
        attrs = _change_attrs(evidence)
        if (
            attrs
            and _SEIZURE_WORD_RE.search(evidence)
            and not _change_reject(evidence)
            and not _controlled_named_change(candidate, attrs)
        ):
            text = _text_from_candidate(candidate)
            out.append(
                (
                    _new_mention(text, attrs, evidence, "state.change_recovery"),
                    "state.change_recovery",
                )
            )
    if ctype in {"generic_seizure_free_anchor", "named_seizure_free_anchor"}:
        if _seizure_free_reject(evidence):
            return out
        for attrs, rule_id in _seizure_free_attrs(evidence):
            text = _text_from_candidate(candidate)
            if text in {"seizure-free", "seizure free"}:
                text = "seizures"
            out.append((_new_mention(text, attrs, evidence, rule_id), rule_id))
    return out


def _change_attrs(evidence: str) -> dict[str, str] | None:
    lower = evidence.lower()
    attrs: dict[str, str] = {}
    if re.search(r"\b(returned|worse|increas(?:ed|ing)|more frequent)\b", lower):
        attrs["FrequencyChange"] = "Increased"
    elif re.search(r"\b(decreas(?:ed|ing)|reduced|less frequent)\b", lower):
        attrs["FrequencyChange"] = "Decreased"
    elif re.search(r"\b(infrequent|improved|improvement|helped)\b", lower):
        attrs["FrequencyChange"] = "Infrequent"
    elif re.search(r"\b(fairly frequent|very frequent|frequent)\b", lower):
        attrs["FrequencyChange"] = "Frequent"
    elif re.search(r"\b(well controlled|under control|controlled)\b", lower):
        attrs["FrequencyChange"] = (
            "Infrequent" if _drug_change_context(lower) else "Same"
        )
    else:
        return None
    point = _point_in_time(lower)
    if point:
        attrs["PointInTime"] = point
    return attrs


def _seizure_free_attrs(evidence: str) -> list[tuple[dict[str, str], str]]:
    lower = evidence.lower()
    out: list[tuple[dict[str, str], str]] = []
    point = _point_in_time(lower)
    current_free = re.search(
        r"\b(no further|no more|not had any (?:more|further)|stopped|"
        r"remain(?:s)? seizure[- ]free)\b",
        lower,
    )
    if current_free:
        attrs = {"NumberOfSeizures": "0"}
        if point:
            attrs["PointInTime"] = point
            attrs["TimeSince_or_TimeOfEvent"] = "Since"
        out.append((attrs, "state.seizure_free_point_anchor"))
    duration = _last_event_duration(evidence)
    if duration is not None:
        number, unit = duration
        out.append(
            (
                {
                    "NumberOfSeizures": "0",
                    "NumberOfTimePeriods": number,
                    "TimePeriod": unit,
                },
                "state.seizure_free_last_event_duration",
            )
        )
    date_attrs = _last_event_date_attrs(evidence)
    if date_attrs:
        attrs = {"NumberOfSeizures": "0", **date_attrs}
        if "YearDate" in attrs or "MonthDate" in attrs:
            attrs["TimeSince_or_TimeOfEvent"] = "Since"
        out.append((attrs, "state.seizure_free_last_event_date"))
    return out


def _last_event_duration(evidence: str) -> tuple[str, str] | None:
    lower = evidence.lower()
    if not re.search(r"\b(last|single|about|ago)\b", lower):
        return None
    match = re.search(
        r"\b(?P<num>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
        r"(?P<unit>weeks?|months?|years?)\s+ago\b",
        lower,
    )
    if not match:
        return None
    return (_number_token(match.group("num")), _unit_token(match.group("unit")))


def _last_event_date_attrs(evidence: str) -> dict[str, str]:
    lower = evidence.lower()
    if not re.search(r"\b(last seizure|last seizures|last event)\b", lower):
        return {}
    attrs: dict[str, str] = {}
    month_match = re.search(
        r"\b(january|february|march|april|may|june|july|august|"
        r"september|october|november|novemebr|december|devember|christmas)\b",
        lower,
    )
    if month_match:
        attrs["MonthDate"] = _month_number(month_match.group(1))
    year_match = re.search(r"\b(20\d{2}|19\d{2})\b", lower)
    if year_match:
        attrs["YearDate"] = year_match.group(1)
    return attrs


def _owned_named_type(evidence: str) -> str | None:
    lower = evidence.lower()
    rate_token = re.search(
        r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|per|every)\b",
        lower,
    )
    if not rate_token:
        return None
    for pattern, text in _NAMED_TYPE_PATTERNS:
        if pattern.search(evidence):
            return text
    return None


def _text_from_candidate(candidate: Mapping[str, Any]) -> str:
    hint = str(candidate.get("text_hint", "")).strip()
    evidence = str(candidate.get("evidence", ""))
    ctype = str(candidate.get("candidate_type", ""))
    if ctype.startswith("generic"):
        if re.search(r"\blast seizure\b", evidence, re.I):
            return "seizure"
        return "seizures"
    return hint or _owned_named_type(evidence) or "seizures"


def _new_mention(
    text: str,
    attrs: Mapping[str, str],
    evidence: str,
    rule_id: str,
) -> dict[str, Any]:
    return {
        "entity": SEIZURE_FREQUENCY.name,
        "text": text,
        "attributes": dict(attrs),
        "evidence": evidence,
        "confidence": "medium",
        "rationale": f"Deterministic v0.6 projection: {rule_id}.",
    }


def _project_mentions(letter_id: str, mentions: Sequence[Mapping[str, Any]]) -> PredictedLetter:
    prediction = PredictedLetter(
        letter_id=letter_id,
        mentions=tuple(
            PredictedMention(
                entity=SEIZURE_FREQUENCY.name,
                text=str(m.get("text", "")),
                attributes={str(k): str(v) for k, v in dict(m.get("attributes") or {}).items()},
                evidence=str(m.get("evidence", "")),
                confidence=(
                    m.get("confidence")
                    if m.get("confidence") in {"low", "medium", "high"}
                    else None
                ),
                rationale=str(m.get("rationale", "")),
                component_owner=COMPONENT_OWNER,
            )
            for m in mentions
        ),
        diagnostics={"projection_version": PROJECTION_VERSION},
    )
    return project_cuis(prediction)


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


def _is_generic_type(mention: Mapping[str, Any]) -> bool:
    attrs = dict(mention.get("attributes") or {})
    cui = attrs.get("CUI")
    if cui in _GENERIC_CUIS:
        return True
    return normalize_phrase(str(mention.get("text", ""))) in {
        "seizure",
        "seizures",
        "seizure free",
        "seizure-free",
    }


def _has_equivalent_state_mention(
    mentions: Sequence[Mapping[str, Any]],
    candidate: Mapping[str, Any],
) -> bool:
    candidate_key = (normalize_phrase(str(candidate["text"])), _state(candidate))
    return any(
        (normalize_phrase(str(m.get("text", ""))), _state(m)) == candidate_key
        for m in mentions
    )


def _same_evidence_state_present(
    mentions: Sequence[Mapping[str, Any]],
    candidate: Mapping[str, Any],
) -> bool:
    candidate_evidence = normalize_phrase(str(candidate.get("evidence", "")))
    candidate_state = _state(candidate)
    return any(
        normalize_phrase(str(m.get("evidence", ""))) == candidate_evidence
        and _state(m) == candidate_state
        for m in mentions
    )


def _point_anchor_already_present(
    mentions: Sequence[Mapping[str, Any]],
    candidate: Mapping[str, Any],
) -> bool:
    attrs = dict(candidate.get("attributes") or {})
    if attrs.get("NumberOfSeizures") != "0" or not attrs.get("PointInTime"):
        return False
    return any(
        _state(m) == "seizure-free"
        and dict(m.get("attributes") or {}).get("PointInTime") == attrs["PointInTime"]
        for m in mentions
    )


def _dedupe_exact_mentions(mentions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, ...]] = set()
    out: list[dict[str, Any]] = []
    for mention in mentions:
        key = (
            normalize_phrase(str(mention.get("text", ""))),
            tuple(
                sorted(
                    (str(k), str(v))
                    for k, v in dict(mention.get("attributes") or {}).items()
                )
            ),
            normalize_phrase(str(mention.get("evidence", ""))),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(_copy_mention(mention))
    return out


def _change_reject(evidence: str) -> bool:
    lower = evidence.lower()
    return bool(
        re.search(
            r"\b(epilepsy (?:is|has been) stable|family history|no history of|"
            r"risk of increased seizures|should there be|if .*further seizures|"
            r"previously|in the past|were well controlled)\b",
            lower,
        )
    )


def _controlled_named_change(candidate: Mapping[str, Any], attrs: Mapping[str, str]) -> bool:
    if not str(candidate.get("candidate_type", "")).startswith("named"):
        return False
    evidence = str(candidate.get("evidence", "")).lower()
    return attrs.get("FrequencyChange") in {"Same", "Infrequent"} and bool(
        re.search(r"\b(well controlled|under control|controlled)\b", evidence)
    )


def _seizure_free_reject(evidence: str) -> bool:
    lower = evidence.lower()
    return bool(
        re.search(
            r"\b(best period|longest period|before the recent seizure|"
            r"driv(?:e|ing)|dvla|refrain from driving)\b",
            lower,
        )
    )


def _drug_change_context(lower: str) -> bool:
    return bool(
        re.search(
            r"\b(lamotrigine|tegretol|carbamazepine|valproate|eplim|keppra|"
            r"dose|drug|medication|commenc|start|increas)\b",
            lower,
        )
    )


def _point_in_time(lower: str) -> str | None:
    if re.search(r"\b(last clinic|last appointment|last review)\b", lower):
        return "LastClinic"
    if re.search(r"\b(surgery|operation)\b", lower):
        return "Surgery"
    if _drug_change_context(lower):
        return "DrugChange"
    if re.search(r"\blast week\b", lower):
        return "Last_Week"
    if re.search(r"\blast month\b", lower):
        return "Last_Month"
    if re.search(r"\blast year\b", lower):
        return "Last_Year"
    return None


def _number_token(token: str) -> str:
    return _WORD_NUMBER.get(token.lower(), token)


def _unit_token(token: str) -> str:
    lower = token.lower()
    if lower.startswith("week"):
        return "Week"
    if lower.startswith("month"):
        return "Month"
    return "Year"


def _month_number(token: str) -> str:
    months = {
        "january": "1",
        "february": "2",
        "march": "3",
        "april": "4",
        "may": "5",
        "june": "6",
        "july": "7",
        "august": "8",
        "september": "9",
        "october": "10",
        "november": "11",
        "novemebr": "11",
        "december": "12",
        "devember": "12",
        "christmas": "12",
    }
    return months[token.lower()]


def _copy_mention(mention: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "entity": str(mention.get("entity", SEIZURE_FREQUENCY.name)),
        "text": str(mention.get("text", "")),
        "attributes": dict(mention.get("attributes") or {}),
        "evidence": str(mention.get("evidence", "")),
        "confidence": mention.get("confidence", "medium"),
        "rationale": str(mention.get("rationale", "")),
    }


def _mention_to_row(mention: PredictedMention) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "confidence": mention.confidence,
        "rationale": mention.rationale,
    }


def _append_rationale(mention: Mapping[str, Any], addition: str) -> str:
    existing = str(mention.get("rationale", "")).strip()
    return f"{existing} {addition}".strip()


def _action(rule_id: str, action: str, mention: Mapping[str, Any]) -> dict[str, str]:
    return {
        "rule_id": rule_id,
        "action": action,
        "category": "seizure_frequency",
        "text": str(mention.get("text", "")),
        "evidence": str(mention.get("evidence", "")),
    }


def _action_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        for action in row.get("projection_actions", []):
            counts[str(action.get("rule_id", "unknown"))] += 1
    return dict(counts)


def _first_value(rows: Sequence[Mapping[str, Any]], key: str) -> Any:
    for row in rows:
        value = row.get(key)
        if value:
            return value
    return None


def _slice_row(label: str, score: Mapping[str, Any]) -> str:
    return (
        f"| {label} | {score.get('f1', 0):.3f} | {score.get('precision', 0):.3f} | "
        f"{score.get('recall', 0):.3f} | {score.get('tp', 0)} | "
        f"{score.get('fp', 0)} | {score.get('fn', 0)} |"
    )


def write_rows_and_report(
    rows: Sequence[Mapping[str, Any]],
    *,
    ablation: ProjectionAblation,
    jsonl_path: Path,
    report_path: Path,
) -> dict[str, Any]:
    projected, metadata = project_rows(rows, ablation=ablation)
    write_jsonl(projected, jsonl_path)
    write_report(projected, metadata, report_path, jsonl_path=jsonl_path)
    return metadata
