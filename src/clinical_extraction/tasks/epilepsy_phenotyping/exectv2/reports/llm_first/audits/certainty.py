"""Certainty projection audit (plan report #2)."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Sequence
from functools import lru_cache
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.clinical_recovery_scorecard import (
    ARTIFACT_LAYER_ENTITIES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.constants import (
    CERTAINTY,
    CERTAINTY_ATTRS,
    FEBRILE_HISTORY,
    GUIDELINE_CERTAINTY_ENTITIES,
    GUIDELINE_CERTAINTY_TRIGGERS_PATH,
    GUIDELINE_NEGATION_ENTITIES,
    NEGATED_FEBRILE_HISTORY,
    NEGATION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.projection import (
    as_exect,
    as_predicted,
    strip_and_project,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    MatchConfig,
    benchmark_config_for,
    benchmark_ignore_for,
    normalize_phrase,
    score_overall,
)


@lru_cache(maxsize=1)
def _load_guideline_certainty_triggers() -> tuple[tuple[str, str], ...]:
    text = GUIDELINE_CERTAINTY_TRIGGERS_PATH.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:  # pragma: no cover - PyYAML is a repo dependency
        raise ValueError(
            f"{GUIDELINE_CERTAINTY_TRIGGERS_PATH} requires PyYAML but it is unavailable"
        ) from exc
    payload = yaml.safe_load(text)
    if not isinstance(payload, dict):
        raise ValueError(f"{GUIDELINE_CERTAINTY_TRIGGERS_PATH} did not contain a mapping")
    triggers = payload.get("triggers")
    if not isinstance(triggers, dict):
        raise ValueError(
            f"{GUIDELINE_CERTAINTY_TRIGGERS_PATH} missing top-level 'triggers' mapping"
        )
    items = [(str(trigger), str(level)) for trigger, level in triggers.items()]
    return tuple(sorted(items, key=lambda item: len(item[0]), reverse=True))


def certainty_dropped_config_for(entity: str) -> MatchConfig:
    """Benchmark config that additionally drops ``Certainty``/``Negation``."""

    return MatchConfig(
        include_attributes=True,
        ignore_attributes=benchmark_ignore_for(entity) | CERTAINTY_ATTRS,
    )


def _attr_distribution(
    gold_letters: Sequence[ExectLetter],
    entity: str,
    attr: str,
) -> dict[str, Any]:
    values: Counter[str] = Counter()
    total = 0
    for letter in gold_letters:
        for ann in letter.entities(entity):
            total += 1
            value = ann.attributes.get(attr)
            if value is not None and value != "":
                values[value] += 1
    present = sum(values.values())
    modal_share = (values.most_common(1)[0][1] / present) if present else 0.0
    return {
        "gold_mentions": total,
        "present": present,
        "present_rate": round(present / total, 4) if total else 0.0,
        "distinct_values": len(values),
        "distribution": dict(values.most_common()),
        "default_projection_ceiling": round(modal_share, 4),
    }


def _first_overlap_index(
    gold_phrase: str,
    predictions: Sequence[ExectAnnotation],
    used: set[int],
) -> int | None:
    if not gold_phrase:
        return None
    for i, pred in enumerate(predictions):
        if i in used:
            continue
        pred_phrase = normalize_phrase(pred.text)
        if pred_phrase and (gold_phrase in pred_phrase or pred_phrase in gold_phrase):
            return i
    return None


def _certainty_recovery_on_overlap(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    entity: str,
) -> dict[str, Any]:
    pred_by_id = {letter.letter_id: letter for letter in pred_letters}
    stats = {
        attr: {"pairs_gold_has": 0, "agree": 0}
        for attr in (CERTAINTY, NEGATION)
    }
    empty = ExectLetter("", "")
    for gold in gold_letters:
        preds = list(pred_by_id.get(gold.letter_id, empty).entities(entity))
        used: set[int] = set()
        for ann in gold.entities(entity):
            idx = _first_overlap_index(normalize_phrase(ann.text), preds, used)
            if idx is None:
                continue
            used.add(idx)
            for attr in (CERTAINTY, NEGATION):
                gold_val = ann.attributes.get(attr)
                if gold_val in (None, ""):
                    continue
                stats[attr]["pairs_gold_has"] += 1
                if preds[idx].attributes.get(attr) == gold_val:
                    stats[attr]["agree"] += 1
    out: dict[str, Any] = {}
    for attr, s in stats.items():
        pairs = s["pairs_gold_has"]
        out[attr] = {
            "overlap_pairs_gold_has_value": pairs,
            "predicted_value_agrees": s["agree"],
            "recovery_rate": round(s["agree"] / pairs, 4) if pairs else 0.0,
        }
    return out


def _local_context(letter: ExectLetter, ann: ExectAnnotation, window: int = 120) -> str:
    note = letter.note_text or ""
    if note and ann.start_index is not None:
        start = max(0, ann.start_index - window)
        end = min(len(note), (ann.end_index or ann.start_index) + window)
        return note[start:end]

    normalized_note = normalize_phrase(note)
    for phrase in (ann.raw_text or "", ann.text):
        normalized_phrase = normalize_phrase(phrase)
        if not normalized_note or not normalized_phrase:
            continue
        idx = normalized_note.find(normalized_phrase)
        if idx >= 0:
            start = max(0, idx - window)
            end = min(len(normalized_note), idx + len(normalized_phrase) + window)
            return normalized_note[start:end]
    return " ".join(p for p in (ann.raw_text or "", ann.text) if p)


def _contains_guideline_trigger(context: str, trigger: str) -> bool:
    if trigger in {"?", "??"}:
        return trigger in context
    return re.search(rf"(?<!\w){re.escape(trigger)}(?!\w)", context) is not None


def project_guideline_certainty_negation(
    entity: str,
    text: str,
    context: str,
) -> dict[str, str]:
    """Project Certainty/Negation from explicit ExECT v9 guideline rules."""

    projected: dict[str, str] = {}
    normalized_context = normalize_phrase(context)
    normalized_text = normalize_phrase(text)
    if entity in GUIDELINE_NEGATION_ENTITIES:
        negated_febrile = (
            entity == "PatientHistory"
            and FEBRILE_HISTORY.search(normalized_text) is not None
            and NEGATED_FEBRILE_HISTORY.search(context) is not None
        )
        projected[NEGATION] = "Negated" if negated_febrile else "Affirmed"
        if negated_febrile:
            projected[CERTAINTY] = "1"

    if entity in GUIDELINE_CERTAINTY_ENTITIES and CERTAINTY not in projected:
        projected[CERTAINTY] = "5"
        for trigger, level in _load_guideline_certainty_triggers():
            if _contains_guideline_trigger(normalized_context, trigger):
                projected[CERTAINTY] = level
                break
    return projected


def _guideline_projection_score(
    gold_letters: Sequence[ExectLetter],
    entity: str,
) -> dict[str, Any]:
    stats = {
        attr: {"gold_has_value": 0, "projected": 0, "agree": 0, "mismatches": Counter()}
        for attr in (CERTAINTY, NEGATION)
    }
    rule_hits: Counter[str] = Counter()
    for letter in gold_letters:
        for ann in letter.entities(entity):
            projection = project_guideline_certainty_negation(
                ann.entity,
                ann.text,
                _local_context(letter, ann),
            )
            if projection.get(NEGATION) == "Negated":
                rule_hits["negated_febrile_history"] += 1
            elif NEGATION in projection:
                rule_hits["default_affirmed_negation"] += 1
            if projection.get(CERTAINTY) == "5":
                rule_hits["default_certainty_5"] += 1
            elif CERTAINTY in projection:
                rule_hits[f"certainty_level_{projection[CERTAINTY]}_trigger"] += 1

            for attr in (CERTAINTY, NEGATION):
                gold_value = ann.attributes.get(attr)
                if gold_value in (None, ""):
                    continue
                stats[attr]["gold_has_value"] += 1
                projected_value = projection.get(attr)
                if projected_value:
                    stats[attr]["projected"] += 1
                if projected_value == gold_value:
                    stats[attr]["agree"] += 1
                else:
                    stats[attr]["mismatches"][(gold_value, projected_value or "")] += 1

    out: dict[str, Any] = {}
    for attr, s in stats.items():
        gold_n = s["gold_has_value"]
        projected_n = s["projected"]
        out[attr] = {
            "gold_has_value": gold_n,
            "projected": projected_n,
            "agree": s["agree"],
            "coverage": round(projected_n / gold_n, 4) if gold_n else 0.0,
            "accuracy": round(s["agree"] / gold_n, 4) if gold_n else 0.0,
            "mismatches": {
                f"gold={gold}|projected={projected}": count
                for (gold, projected), count in s["mismatches"].most_common(8)
            },
        }
    return {"rule_hits": dict(rule_hits), **out}


def certainty_projection_audit(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    entities: Sequence[str] = ARTIFACT_LAYER_ENTITIES,
) -> dict[str, Any]:
    """Quantify how mechanical certainty is and the certainty-only benchmark loss."""

    pred_exect = [
        to_exect_letter(p) for p in strip_and_project(as_predicted(pred_letters))
    ]
    benchmark = score_overall(gold_letters, pred_exect, entities, benchmark_config_for)
    certainty_dropped = score_overall(
        gold_letters, pred_exect, entities, certainty_dropped_config_for
    )
    per_entity: dict[str, Any] = {}
    for entity in entities:
        bench = benchmark.per_entity[entity].per_item
        dropped = certainty_dropped.per_entity[entity].per_item
        per_entity[entity] = {
            "certainty": _attr_distribution(gold_letters, entity, CERTAINTY),
            "negation": _attr_distribution(gold_letters, entity, NEGATION),
            "guideline_projection": _guideline_projection_score(gold_letters, entity),
            "recovery_on_overlap": _certainty_recovery_on_overlap(
                gold_letters, as_exect(pred_letters), entity
            ),
            "benchmark_f1": round(bench.f1, 4),
            "certainty_dropped_f1": round(dropped.f1, 4),
            "certainty_only_tp_gain_if_dropped": dropped.tp - bench.tp,
        }
    overall_benchmark = benchmark.per_item
    overall_dropped = certainty_dropped.per_item
    return {
        "status": "guideline_rule_projection_audited",
        "ignored_attributes": sorted(CERTAINTY_ATTRS),
        "guideline_rules": {
            "certainty": (
                "Assign certainty to Diagnosis, BirthHistory, EpilepsyCause, "
                "Onset, WhenDiagnosed, and PatientHistory. Use ExECT v9 List 2 "
                "trigger phrases; default uncued assertions to Certainty=5."
            ),
            "negation": (
                "Assign Negation to the same concept families. Default to "
                "Affirmed; project PatientHistory febrile seizure/convulsion "
                "statements with local no/not/denied context as Negated and "
                "Certainty=1."
            ),
            "excluded": (
                "SeizureFrequency, Prescription, and Investigations do not own "
                "Certainty/Negation under the guideline convention."
            ),
        },
        "limitations": (
            "This audit implements explicit guideline-trigger rules and scores "
            "them over gold rows, using source-local context when offsets/text "
            "are available. It estimates projection reliability after the "
            "clinical concept is already selected; it does not license "
            "deterministic concept generation."
        ),
        "note": (
            "SeizureFrequency already ignores Certainty/Negation in its benchmark "
            "key (guideline convention), so it contributes no certainty-only loss."
        ),
        "overall": {
            "benchmark_f1": round(overall_benchmark.f1, 4),
            "certainty_dropped_f1": round(overall_dropped.f1, 4),
            "certainty_only_f1_gain_if_dropped": round(
                overall_dropped.f1 - overall_benchmark.f1, 4
            ),
            "certainty_only_tp_gain_if_dropped": overall_dropped.tp - overall_benchmark.tp,
            "benchmark_tp": overall_benchmark.tp,
        },
        "per_entity": per_entity,
    }
