"""Deterministic state/ownership projection over saved SF rows.

This is an attribution-preserving replay layer for the saved v0.5
SeizureFrequency state-adjudicator output. It does not call a model and it does
not inspect gold labels while projecting a row. Rules are deliberately finite
and ablatable because they change prediction-bearing SeizureFrequency state or
ownership conventions.

The row walk is one design with two phases:

1. State and generic-to-named ownership run on the model's mentions and
   candidate spans, before CUI assignment.
2. After CUI assignment, the landed extra-AR ownership passes in
   ``_OWNERSHIP_PASSES`` run in listed order. Single last-event duration
   (v0.10) is a state-pass rewrite that uses
   ``sf_last_event_duration.last_event_duration``, not an ownership pass.
   v0.15 applies List 11 / range / interval / dated-heading encoding on
   emitted mentions before those state repairs. v0.16 adds gold-free
   leftover-scope drops (bare symptom token including episode, febrile
   history, driving without a duration frame). v0.17 adds bare episode.
   v0.18 recodes last-event / none-since mentions whose count is missing,
   ``no``, ``none``, or a year token to ``NumberOfSeizures='0'`` + Since.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, Literal, NamedTuple

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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_attribute_encoding as sf_encoding,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_bare_count_active_rate as bare_count,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_cui_phrase_preserve as cui_phrase_preserve,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_dated_cluster as dated_cluster,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_drugchange_before as drugchange_before,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_last_event_duration as last_event,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_lifetime_oneoff as lifetime_oneoff,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_named_last_week_generic as named_last_week,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_scope_residue as scope_residue,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
    GENERIC_SF_CUIS,
    GENERIC_SF_PHRASES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalizer import (
    MONTH_MAP,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_umbrella_clone import (
    apply_umbrella_clone_drop,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.artifact_io import (
    first_value as _first_value,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.artifact_io import (
    # scripts/run_exectv2_2call_model_swap.py calls this as sf_projection.read_rows.
    read_rows as read_rows,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    frequency_state_faithful,
)

PROJECTION_VERSION = "exectv2_hybrid_sf_state_projection_v0.18"
PIPELINE_FAMILY = "exectv2_hybrid_sf_state_projection"
COMPONENT_OWNER = "deterministic_sf_state_ownership_projection"

ProjectionAblation = Literal["none", "state", "ownership", "combined"]
_OwnershipApply = Callable[
    [Sequence[Mapping[str, Any]]],
    tuple[list[dict[str, Any]], list[dict[str, str]]],
]


class _OwnershipPass(NamedTuple):
    apply: _OwnershipApply
    kind: Literal["drop", "repair"]
    rule_id: str | None = None


def _apply_cui_phrase_bundle(
    mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    return cui_phrase_preserve.apply_cui_phrase_preserve(mentions, arm="bundle")


# Landed extra-AR ownership passes after CUI assignment, oldest first.
_OWNERSHIP_PASSES: tuple[_OwnershipPass, ...] = (
    _OwnershipPass(apply_umbrella_clone_drop, "drop", "ownership.drop_umbrella_clone"),
    _OwnershipPass(_apply_cui_phrase_bundle, "repair"),
    _OwnershipPass(
        bare_count.apply_bare_count_active_rate_drop,
        "drop",
        "ownership.drop_bare_count_active_rate",
    ),
    _OwnershipPass(
        lifetime_oneoff.apply_lifetime_oneoff_active_rate_drop,
        "drop",
        "ownership.drop_lifetime_oneoff_active_rate",
    ),
    _OwnershipPass(
        dated_cluster.apply_dated_cluster_next_to_free_drop,
        "drop",
        "ownership.drop_dated_cluster_next_to_free",
    ),
    _OwnershipPass(
        named_last_week.apply_named_last_week_generic_retarget,
        "repair",
        "ownership.retarget_last_week_named_to_generic",
    ),
    _OwnershipPass(
        drugchange_before.apply_drugchange_before_sibling_drop,
        "drop",
        "ownership.drop_drugchange_before_if_other_active_rate",
    ),
    _OwnershipPass(
        scope_residue.apply_scope_residue_drop,
        "drop",
        "ownership.drop_scope_residue",
    ),
)

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
# Onset framing for Rule 4. The ``since`` alternatives are anchored to the year
# or age token they claim to describe: a bare ``"since 20"`` substring also
# matched doses ("since 20mg"), durations ("since 20 years ago"), and unrelated
# text elsewhere in a long evidence window.
_ONSET_FRAMING_RE = re.compile(
    r"\b(?:"
    r"started\s+in\b"
    r"|since\s+(?:the\s+)?age\s+(?:of\s+)?\d+"
    r"|since\s+(?:19|20)\d{2}"
    r")\b",
    re.IGNORECASE,
)
def project_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    ablation: ProjectionAblation = "combined",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.sf_replay_scoring import (  # noqa: E501
        summarize_sf_rows,
    )

    projected = [project_row(row, ablation=ablation) for row in rows]
    metadata = {
        "projection_version": PROJECTION_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "source_prompt_version": _first_value(rows, "prompt_version"),
        "source_pipeline_family": _first_value(rows, "pipeline_family"),
        "ablation": ablation,
        "split": _first_value(rows, "split") or "dev",
        "n_letters": len(projected),
        "summary": summarize_sf_rows(projected),
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
    if ablation in {"ownership", "combined"}:
        projected_mentions = _apply_landed_ownership_passes(projected_mentions, actions)

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
        "# ExECTv2 SeizureFrequency State/Ownership Projection v0.18",
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


def _apply_landed_ownership_passes(
    mentions: list[dict[str, Any]],
    actions: list[dict[str, str]],
) -> list[dict[str, Any]]:
    working = mentions
    for stage in _OWNERSHIP_PASSES:
        working, records = stage.apply(working)
        for record in records:
            rule_id = stage.rule_id or f"ownership.{record['action']}"
            actions.append(_action(rule_id, stage.kind, record))
    return working


def _apply_state_projection(
    row: Mapping[str, Any],
    mentions: list[dict[str, Any]],
    actions: list[dict[str, str]],
) -> list[dict[str, Any]]:
    mentions, encoding_actions = sf_encoding.apply_sf_attribute_encoding(mentions)
    for record in encoding_actions:
        actions.append(
            _action(
                str(record.get("rule_id") or "encoding.sf_attribute"),
                "repair",
                {"text": record.get("text", ""), "evidence": ""},
            )
        )
    kept: list[dict[str, Any]] = []
    for mention in mentions:
        dated_free = _rewrite_dated_last_event(mention)
        if dated_free is not mention:
            actions.append(_action("state.last_event_date_to_seizure_free", "repair", mention))
            mention = _copy_mention(dated_free)
        drop_rule = _state_drop_rule(mention, mentions)
        if drop_rule:
            actions.append(_action(drop_rule, "drop", mention))
            continue
        repaired = _repair_state_mention(mention)
        if repaired is not mention:
            if _state(mention) == "active-rate" and _state(repaired) == "seizure-free":
                rule_id = "state.last_event_active_to_seizure_free"
            else:
                rule_id = "state.temporal_direction"
            actions.append(_action(rule_id, "repair", mention))
        kept.append(dict(repaired))

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
    lower_evidence = evidence.lower()
    attrs = dict(mention.get("attributes") or {})
    num_sz = attrs.get("NumberOfSeizures")
    tso = attrs.get("TimeSince_or_TimeOfEvent")
    point = attrs.get("PointInTime")
    has_date = any(k in attrs for k in ("YearDate", "MonthDate", "DayDate"))
    has_duration = "TimePeriod" in attrs or "NumberOfTimePeriods" in attrs

    repaired_attrs = dict(attrs)
    changed = False

    # Rule 1: PointInTime anchor missing TimeSince_or_TimeOfEvent -> Add 'Since' (or 'During')
    if point and "TimeSince_or_TimeOfEvent" not in attrs:
        if point in ("Last_Year", "Last_Month", "Last_Week") and num_sz and num_sz != "0":
            repaired_attrs["TimeSince_or_TimeOfEvent"] = "During"
        else:
            repaired_attrs["TimeSince_or_TimeOfEvent"] = "Since"
        changed = True

    # Rule 2: Duration-based mention WITHOUT a specific date/point -> Strip TimeSince_or_TimeOfEvent
    if has_duration and not point and not has_date and "TimeSince_or_TimeOfEvent" in repaired_attrs:
        repaired_attrs.pop("TimeSince_or_TimeOfEvent")
        changed = True

    # Rule 3: Active count (NumberOfSeizures > 0) -> Set 'During' if no 'since'
    if (
        num_sz
        and num_sz != "0"
        and (point or has_date)
        and tso == "Since"
        and "since" not in lower_evidence
    ):
        repaired_attrs["TimeSince_or_TimeOfEvent"] = "During"
        changed = True

    # Rule 4: Active rate mention with historical onset framing -> Strip onset YearDate / Age
    has_onset = bool(_ONSET_FRAMING_RE.search(lower_evidence))
    if num_sz and num_sz != "0" and has_duration and has_onset:
        repaired_attrs.pop("TimeSince_or_TimeOfEvent", None)
        # Date and age attributes are paired: dropping only YearDate/AgeLower
        # would leave a MonthDate with no year, an upper age bound with no
        # lower, or an AgeUnit qualifying an age that is no longer there.
        for onset_key in (
            "YearDate",
            "MonthDate",
            "DayDate",
            "AgeLower",
            "AgeUpper",
            "AgeUnit",
        ):
            repaired_attrs.pop(onset_key, None)
        changed = True

    # Rule 5: Seizure-free mention (NumberOfSeizures == '0') -> TimeSince_or_TimeOfEvent is Since
    if num_sz == "0" and tso == "During":
        repaired_attrs["TimeSince_or_TimeOfEvent"] = "Since"
        changed = True

    # Rule 6: Strip FrequencyChange from concrete numeric count mentions
    has_count = any(
        k in attrs
        for k in ("NumberOfSeizures", "LowerNumberOfSeizures", "UpperNumberOfSeizures")
    )
    if has_count and "FrequencyChange" in repaired_attrs:
        repaired_attrs.pop("FrequencyChange")
        changed = True

    # Rule 7: Strip TimePeriod & NumberOfTimePeriods when PointInTime is present
    if point and "TimePeriod" in repaired_attrs:
        repaired_attrs.pop("TimePeriod", None)
        repaired_attrs.pop("NumberOfTimePeriods", None)
        changed = True

    # Rule 8: Strip TimeSince_or_TimeOfEvent when DayDate anchors a point event.
    # A seizure-free mention anchored with an explicit 'since <day>' keeps its
    # direction: the day is the start of the free period, not the event date.
    seizure_free_since = repaired_attrs.get("NumberOfSeizures") == "0" and (
        "since" in lower_evidence or "seizure free" in lower_evidence
    )
    if (
        "DayDate" in repaired_attrs
        and "TimeSince_or_TimeOfEvent" in repaired_attrs
        and not seizure_free_since
    ):
        repaired_attrs.pop("TimeSince_or_TimeOfEvent", None)
        changed = True

    if changed:
        repaired = _copy_mention(mention)
        repaired["attributes"] = repaired_attrs
        repaired["rationale"] = _append_rationale(
            repaired,
            "Deterministic state projection aligns temporal direction.",
        )
        if _is_single_last_event(repaired, evidence):
            return _rewrite_last_event(repaired, evidence)
        return repaired

    if _state(mention) != "active-rate":
        return mention
    duration = last_event.last_event_duration(evidence)
    if duration is None:
        return mention
    return _rewrite_last_event(mention, evidence)


_COINCIDED_LAST_EVENT_RE = re.compile(
    r"\b(coincided with|previous seizure was a year ago)\b",
    re.IGNORECASE,
)
_TEENAGE_LAST_EVENT_RE = re.compile(
    r"\blast seizures?\b.{0,80}\bteenage years\b",
    re.IGNORECASE,
)
_NONE_SINCE_CUE_RE = re.compile(
    r"\b(has had none since|none since|seizure[- ]free since)\b",
    re.IGNORECASE,
)


def _rewrite_dated_last_event(mention: Mapping[str, Any]) -> dict[str, Any] | Mapping[str, Any]:
    """Map last-event / none-since dates to NumberOfSeizures=0 even without model 1."""

    evidence = str(mention.get("evidence") or "")
    attrs = dict(mention.get("attributes") or {})
    already_free = attrs.get("NumberOfSeizures") == "0" and attrs.get(
        "TimeSince_or_TimeOfEvent"
    ) == "Since"
    if already_free and any(attrs.get(key) for key in ("YearDate", "MonthDate", "AgeLower")):
        return mention

    if _TEENAGE_LAST_EVENT_RE.search(evidence):
        repaired = _copy_mention(mention)
        new_attrs = {
            "NumberOfSeizures": "0",
            "AgeLower": "13",
            "AgeUpper": "19",
            "AgeUnit": "Year",
            "TimeSince_or_TimeOfEvent": "Since",
        }
        for keep in ("CUI", "CUIPhrase", "Certainty", "Negation"):
            if attrs.get(keep):
                new_attrs[keep] = str(attrs[keep])
        repaired["attributes"] = new_attrs
        repaired["rationale"] = _append_rationale(
            repaired,
            "Deterministic state projection treats last seizures in teenage years as seizure-free.",
        )
        return repaired

    date_attrs = _last_event_date_attrs(evidence)
    if not date_attrs and _NONE_SINCE_CUE_RE.search(evidence):
        date_attrs = _calendar_date_attrs(evidence)
    if not date_attrs:
        return mention
    if _COINCIDED_LAST_EVENT_RE.search(evidence) and not re.search(
        r"\blast event\b", evidence, re.IGNORECASE
    ):
        return mention
    if not date_attrs.get("YearDate") and not date_attrs.get("MonthDate"):
        return mention

    repaired = _copy_mention(mention)
    new_attrs = {"NumberOfSeizures": "0", **date_attrs, "TimeSince_or_TimeOfEvent": "Since"}
    for keep in ("CUI", "CUIPhrase", "Certainty", "Negation"):
        if attrs.get(keep):
            new_attrs[keep] = str(attrs[keep])
    repaired["attributes"] = new_attrs
    repaired["rationale"] = _append_rationale(
        repaired,
        "Deterministic state projection treats a dated last-event as seizure-free.",
    )
    return repaired


def _calendar_date_attrs(evidence: str) -> dict[str, str]:
    lower = evidence.lower()
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


def _is_single_last_event(mention: Mapping[str, Any], evidence: str) -> bool:
    if _state(mention) != "active-rate":
        return False
    if last_event.last_event_duration(evidence) is None:
        return False
    attrs = dict(mention.get("attributes") or {})
    if str(attrs.get("NumberOfSeizures") or "") != "1":
        return False
    return bool(re.search(r"\b(single|last)\b", evidence.lower()))


def _rewrite_last_event(mention: Mapping[str, Any], evidence: str) -> dict[str, Any]:
    duration = last_event.last_event_duration(evidence)
    if duration is None:
        return dict(mention)
    number, unit = duration
    repaired = _copy_mention(mention)
    repaired["text"] = (
        "seizure" if "seizure" in normalize_phrase(evidence).split() else "seizures"
    )
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
        attrs["FrequencyChange"] = "Infrequent" if _drug_change_context(lower) else "Same"
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
    duration = last_event.last_event_duration(evidence)
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
        "rationale": f"Deterministic v0.7 projection: {rule_id}.",
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
    """Count-based state, or ``changed``/``unknown`` via the shared faithful
    definition (SF-5, 2026-07-02).

    Previously a local 3-way (seizure-free/active-rate/unknown) reimplementation
    that discarded ``FrequencyChange`` entirely, silently collapsing every
    genuinely reported qualitative change to ``unknown`` for this module's own
    drop-rule/dedup/ownership logic (a separate defect from -- and now
    reconciled with -- :func:`frequency_state_faithful`, the canonical scorer
    definition). See the Phase 4 guardrail doc's SF-5 item.
    """

    return frequency_state_faithful(dict(mention.get("attributes") or {}))


def _is_generic_type(mention: Mapping[str, Any]) -> bool:
    attrs = dict(mention.get("attributes") or {})
    cui = attrs.get("CUI")
    if cui in GENERIC_SF_CUIS:
        return True
    return normalize_phrase(str(mention.get("text", ""))) in GENERIC_SF_PHRASES


def _has_equivalent_state_mention(
    mentions: Sequence[Mapping[str, Any]],
    candidate: Mapping[str, Any],
) -> bool:
    candidate_key = (normalize_phrase(str(candidate["text"])), _state(candidate))
    return any(
        (normalize_phrase(str(m.get("text", ""))), _state(m)) == candidate_key for m in mentions
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
                sorted((str(k), str(v)) for k, v in dict(mention.get("attributes") or {}).items())
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


def _month_number(token: str) -> str:
    return MONTH_MAP[token.lower()]


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
    from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (  # noqa: E501
        write_jsonl_rows as write_jsonl,
    )

    projected, metadata = project_rows(rows, ablation=ablation)
    write_jsonl(projected, jsonl_path)
    write_report(projected, metadata, report_path, jsonl_path=jsonl_path)
    return metadata
