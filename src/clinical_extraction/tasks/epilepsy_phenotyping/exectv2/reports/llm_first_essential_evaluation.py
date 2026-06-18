"""LLM-first essential clinical evaluation (plan satellite 11).

Analysis-only. Replays existing ExECTv2 prediction artifacts under the
ownership-aware layer ladder from
``docs/plans/exectv2/11_llm_first_essential_clinical_evaluation_plan.md``:

* **clinical-recovery headline** (``build_scorecard``) — does the architecture
  recover the essential clinical facts once CUI/certainty/format are demoted?
* **certainty projection audit** — how mechanical is ``Certainty``/``Negation``,
  what is the default-projection ceiling, and how much benchmark loss is
  certainty-only (the benchmark key with vs without certainty)?
* **CUI projection audit** — per-concept ``one_to_one`` / ``result_conditioned``
  / ``gold_inconsistent`` / ``missing_mapping`` buckets, deterministic projection
  coverage/correctness, and the CUI-only benchmark loss (benchmark vs semantic).
* **ownership ladder** — ``rules_only`` / ``llm_first`` / ``hybrid`` per
  architecture.

No model calls: predictions are reconstructed from saved JSONL artifacts (or
generated deterministically for the ``rules_only`` baseline). The gold side is
read from the artifact itself (``gold_mentions``), which stores the already
resolved scored phrase, so the replay reproduces the scored gold exactly.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from collections.abc import Hashable, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    EPILEPSY_CAUSE,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.clinical_recovery_scorecard import (  # noqa: E501
    ARTIFACT_LAYER_ENTITIES,
    build_scorecard,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.cui_projection_diagnostic import (  # noqa: E501
    cui_projection_diagnostic,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    MatchConfig,
    _concept_keys,
    _frequency_state_keys,
    _investigation_component_keys,
    _prescription_component_keys,
    benchmark_config_for,
    benchmark_ignore_for,
    match_key,
    normalize_phrase,
    score_overall,
    semantic_config_for,
)

_CERTAINTY = "Certainty"
_NEGATION = "Negation"
_CUI = "CUI"
_CUI_PHRASE = "CUIPhrase"
_CERTAINTY_ATTRS = frozenset({_CERTAINTY, _NEGATION})
_GUIDELINE_CERTAINTY_ENTITIES = frozenset(
    {
        "BirthHistory",
        DIAGNOSIS.name,
        EPILEPSY_CAUSE.name,
        "Onset",
        "PatientHistory",
        "WhenDiagnosed",
    }
)
_GUIDELINE_NEGATION_ENTITIES = _GUIDELINE_CERTAINTY_ENTITIES
_GUIDELINE_CERTAINTY_TRIGGERS: tuple[tuple[str, str], ...] = tuple(
    sorted(
        {
            "ruled out": "1",
            "doubt": "2",
            "improbable": "2",
            "not convincingly": "2",
            "remote": "2",
            "unclear": "2",
            "unsure": "2",
            "??": "2",
            "doubtful": "2",
            "not convinced": "2",
            "not likely": "2",
            "remote possibility": "2",
            "unlikely": "2",
            "unusual": "2",
            "considered": "3",
            "describes himself": "3",
            "?": "3",
            "could be": "3",
            "further clarification": "3",
            "investigate her along the lines": "3",
            "markers": "3",
            "might": "3",
            "possible": "3",
            "possibility": "3",
            "potentially": "3",
            "potential": "3",
            "to be sure": "3",
            "to see if": "3",
            "to see whether": "3",
            "to be confirmed": "3",
            "to know whether": "3",
            "this or that": "3",
            "uncertain": "3",
            "further investigation": "3",
            "not conclusive": "4",
            "suspicious": "4",
            "suspect": "4",
            "suggestive": "4",
            "sound like": "4",
            "supports": "4",
            "suspected": "4",
            "suspicion": "4",
            "i think": "4",
            "is in keeping with": "4",
            "point more towards": "4",
            "probable": "4",
            "probably": "4",
            "compatible with": "4",
            "impression is": "4",
            "likely": "4",
            "point towards": "4",
            "supportive of": "4",
            "treated as": "4",
            "consistent with": "5",
            "is conclusive": "5",
            "are dealing with": "5",
            "certain": "5",
            "definite": "5",
            "in keeping with": "5",
        }.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )
)
_FEBRILE_HISTORY = re.compile(r"\bfebrile\s+(?:seizures?|convulsions?)\b", re.IGNORECASE)
_NEGATED_FEBRILE_HISTORY = re.compile(
    r"\b(?:no|not|never|denies?|denied|without)\b.{0,60}\bfebrile\s+"
    r"(?:seizures?|convulsions?)\b|\bfebrile\s+(?:seizures?|convulsions?)\b"
    r".{0,60}\b(?:absent|denied|negated)\b",
    re.IGNORECASE | re.DOTALL,
)
ESSENTIAL_CLINICAL_ENTITIES: tuple[str, ...] = (
    PRESCRIPTION.name,
    SEIZURE_FREQUENCY.name,
    DIAGNOSIS.name,
    EPILEPSY_CAUSE.name,
    INVESTIGATIONS.name,
)
_ESSENTIAL_ATOMIC_CONCEPT_ONLY = frozenset({DIAGNOSIS.name, EPILEPSY_CAUSE.name})

# Ownership ladder. ``rules_only`` = deterministic all-9; ``llm_first`` = LLM
# owns candidate generation + selection, deterministic only projects; ``hybrid``
# = deterministic candidate set or rule augmentation contributes selections.
OWNERSHIP_RULES_ONLY = "rules_only"
OWNERSHIP_LLM_FIRST = "llm_first"
OWNERSHIP_HYBRID = "hybrid"


# --------------------------------------------------------------------------- #
# Artifact loading
# --------------------------------------------------------------------------- #
def _annotation_from_mention(mention: dict[str, Any]) -> ExectAnnotation:
    return ExectAnnotation(
        entity=str(mention["entity"]),
        text=str(mention.get("text", "")),
        attributes={str(k): str(v) for k, v in dict(mention.get("attributes", {})).items()},
    )


def _predicted_mention(mention: dict[str, Any]) -> PredictedMention:
    return PredictedMention(
        entity=str(mention["entity"]),
        text=str(mention.get("text", "")),
        attributes={str(k): str(v) for k, v in dict(mention.get("attributes", {})).items()},
        evidence=str(mention.get("evidence", "")),
        rationale=str(mention.get("rationale", "")),
        confidence=mention.get("confidence"),
    )


def letters_from_artifact(
    path: Path,
) -> tuple[list[ExectLetter], list[PredictedLetter]]:
    """Reconstruct (gold_letters, predicted_letters) from a saved JSONL artifact.

    The artifact rows carry both ``gold_mentions`` and ``predicted_mentions``
    with an ``entity`` field, so the replay is self-contained and reproduces the
    gold that was scored when the run was produced.
    """

    gold_letters: list[ExectLetter] = []
    pred_letters: list[PredictedLetter] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        letter_id = str(row["letter_id"])
        gold_letters.append(
            ExectLetter(
                letter_id=letter_id,
                note_text="",
                annotations=tuple(
                    _annotation_from_mention(m) for m in row.get("gold_mentions", [])
                ),
            )
        )
        pred_letters.append(
            PredictedLetter(
                letter_id=letter_id,
                mentions=tuple(
                    _predicted_mention(m) for m in row.get("predicted_mentions", [])
                ),
            )
        )
    return gold_letters, pred_letters


def predicted_by_id_from_artifact(path: Path) -> dict[str, PredictedLetter]:
    """Return predicted letters keyed by ``letter_id`` from a JSONL artifact."""

    by_id: dict[str, PredictedLetter] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        letter_id = str(row["letter_id"])
        by_id[letter_id] = PredictedLetter(
            letter_id=letter_id,
            mentions=tuple(_predicted_mention(m) for m in row.get("predicted_mentions", [])),
        )
    return by_id


def align_predictions_to_gold(
    gold_letters: Sequence[ExectLetter],
    predicted_by_id: dict[str, PredictedLetter],
) -> list[PredictedLetter]:
    """Order predictions to match ``gold_letters``; emit empty letters for misses."""

    return [
        predicted_by_id.get(g.letter_id, PredictedLetter(letter_id=g.letter_id, mentions=()))
        for g in gold_letters
    ]


# --------------------------------------------------------------------------- #
# Certainty projection audit (plan report #2)
# --------------------------------------------------------------------------- #
def certainty_dropped_config_for(entity: str) -> MatchConfig:
    """Benchmark config that additionally drops ``Certainty``/``Negation``."""

    return MatchConfig(
        include_attributes=True,
        ignore_attributes=benchmark_ignore_for(entity) | _CERTAINTY_ATTRS,
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
        # If a deterministic rule simply assigned the dominant value to every
        # mention that carries the attribute, this is the fraction it gets right.
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
    """Among source-near overlap pairs, does the prediction carry gold's value?

    Measures whether the certainty/negation answer is recoverable once the
    clinical concept is matched, separately for each attribute.
    """

    pred_by_id = {letter.letter_id: letter for letter in pred_letters}
    stats = {
        attr: {"pairs_gold_has": 0, "agree": 0}
        for attr in (_CERTAINTY, _NEGATION)
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
            for attr in (_CERTAINTY, _NEGATION):
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
    if entity in _GUIDELINE_NEGATION_ENTITIES:
        negated_febrile = (
            entity == "PatientHistory"
            and _FEBRILE_HISTORY.search(normalized_text) is not None
            and _NEGATED_FEBRILE_HISTORY.search(context) is not None
        )
        projected[_NEGATION] = "Negated" if negated_febrile else "Affirmed"
        if negated_febrile:
            projected[_CERTAINTY] = "1"

    if entity in _GUIDELINE_CERTAINTY_ENTITIES and _CERTAINTY not in projected:
        projected[_CERTAINTY] = "5"
        for trigger, level in _GUIDELINE_CERTAINTY_TRIGGERS:
            if _contains_guideline_trigger(normalized_context, trigger):
                projected[_CERTAINTY] = level
                break
    return projected


def _guideline_projection_score(
    gold_letters: Sequence[ExectLetter],
    entity: str,
) -> dict[str, Any]:
    stats = {
        attr: {"gold_has_value": 0, "projected": 0, "agree": 0, "mismatches": Counter()}
        for attr in (_CERTAINTY, _NEGATION)
    }
    rule_hits: Counter[str] = Counter()
    for letter in gold_letters:
        for ann in letter.entities(entity):
            projection = project_guideline_certainty_negation(
                ann.entity,
                ann.text,
                _local_context(letter, ann),
            )
            if projection.get(_NEGATION) == "Negated":
                rule_hits["negated_febrile_history"] += 1
            elif _NEGATION in projection:
                rule_hits["default_affirmed_negation"] += 1
            if projection.get(_CERTAINTY) == "5":
                rule_hits["default_certainty_5"] += 1
            elif _CERTAINTY in projection:
                rule_hits[f"certainty_level_{projection[_CERTAINTY]}_trigger"] += 1

            for attr in (_CERTAINTY, _NEGATION):
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
    """Quantify how mechanical certainty is and the certainty-only benchmark loss.

    The benchmark deltas are measured on CUI-projected predictions (CUI stripped
    then deterministically re-attached), so the residual benchmark-vs-
    certainty-dropped gap is owned by certainty/negation, not by missing CUI.
    """

    pred_exect = [
        to_exect_letter(p) for p in _strip_and_project(_as_predicted(pred_letters))
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
            "certainty": _attr_distribution(gold_letters, entity, _CERTAINTY),
            "negation": _attr_distribution(gold_letters, entity, _NEGATION),
            "guideline_projection": _guideline_projection_score(gold_letters, entity),
            "recovery_on_overlap": _certainty_recovery_on_overlap(
                gold_letters, _as_exect(pred_letters), entity
            ),
            "benchmark_f1": round(bench.f1, 4),
            "certainty_dropped_f1": round(dropped.f1, 4),
            "certainty_only_tp_gain_if_dropped": dropped.tp - bench.tp,
        }
    overall_benchmark = benchmark.per_item
    overall_dropped = certainty_dropped.per_item
    return {
        "status": "guideline_rule_projection_audited",
        "ignored_attributes": sorted(_CERTAINTY_ATTRS),
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


# --------------------------------------------------------------------------- #
# CUI projection audit (plan report #3)
# --------------------------------------------------------------------------- #
def _concept_key(ann: ExectAnnotation) -> str:
    return normalize_phrase(ann.attributes.get(_CUI_PHRASE) or ann.text)


def cui_concept_buckets(
    gold_letters: Sequence[ExectLetter],
    entities: Sequence[str],
) -> dict[str, Any]:
    """Bucket every gold clinical concept by its CUI projection character."""

    # (entity, concept) -> CUIs / result states observed in gold
    concept_cuis: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    concept_results: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for letter in gold_letters:
        for entity in entities:
            for ann in letter.entities(entity):
                cui = ann.attributes.get(_CUI)
                if cui:
                    concept_cuis[(entity, _concept_key(ann))][cui] += 1
                    if entity == INVESTIGATIONS.name:
                        concept_results[(entity, _concept_key(ann))][
                            _investigation_result_key(ann)
                        ] += 1

    bucket_counts: Counter[str] = Counter()
    bucket_concepts: Counter[str] = Counter()
    examples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    per_entity: dict[str, Counter[str]] = defaultdict(Counter)
    for (entity, concept), cuis in concept_cuis.items():
        mentions = sum(cuis.values())
        distinct = len(cuis)
        if distinct == 1:
            bucket = "one_to_one"
        elif entity == INVESTIGATIONS.name and len(concept_results[(entity, concept)]) > 1:
            bucket = "result_conditioned"
        else:
            bucket = "gold_inconsistent"
        bucket_counts[bucket] += mentions
        bucket_concepts[bucket] += 1
        per_entity[entity][bucket] += 1
        if len(examples[bucket]) < 12 and distinct > 1:
            examples[bucket].append(
                {"entity": entity, "concept": concept, "cuis": dict(cuis.most_common())}
            )
    return {
        "concept_count": sum(bucket_concepts.values()),
        "bucket_concepts": dict(bucket_concepts),
        "bucket_mentions": dict(bucket_counts),
        "per_entity_concepts": {e: dict(c) for e, c in per_entity.items()},
        "examples": {k: v for k, v in examples.items()},
    }


def _investigation_result_key(ann: ExectAnnotation) -> str:
    for modality in ("EEG", "MRI", "CT"):
        result = ann.attributes.get(f"{modality}_Results")
        if result:
            return f"{modality}:{result}"
    return "unknown_result"


def cui_projection_coverage(
    gold_letters: Sequence[ExectLetter],
    entities: Sequence[str],
) -> dict[str, Any]:
    """Run the deterministic projection over gold and measure coverage/correctness.

    ``missing_mapping`` = gold mention carries a CUI but the deterministic
    projection table attaches none.
    """

    per_entity: dict[str, dict[str, int]] = {
        e: {"gold_with_cui": 0, "projected": 0, "projected_correct": 0, "missing_mapping": 0}
        for e in entities
    }
    missing_examples: dict[str, list[dict[str, str]]] = defaultdict(list)
    missing_concepts: Counter[tuple[str, str]] = Counter()
    entity_set = set(entities)
    for letter in gold_letters:
        # Keep the original gold CUI for grading, but strip it before projecting
        # so the deterministic table must reconstruct it (not pass it through).
        gold_cuis = [
            ann.attributes.get(_CUI)
            for ann in letter.annotations
            if ann.entity in entity_set
        ]
        stripped = PredictedLetter(
            letter_id=letter.letter_id,
            mentions=tuple(
                PredictedMention(
                    entity=ann.entity,
                    text=ann.text,
                    attributes={
                        k: v
                        for k, v in ann.attributes.items()
                        if k not in (_CUI, _CUI_PHRASE)
                    },
                    evidence="",
                )
                for ann in letter.annotations
                if ann.entity in entity_set
            ),
        )
        try:
            projected = project_cuis(stripped)
        except Exception:  # pragma: no cover - projection is best-effort here
            projected = stripped
        for src_mention, proj, gold_cui in zip(
            stripped.mentions, projected.mentions, gold_cuis, strict=True
        ):
            src = src_mention
            if not gold_cui:
                continue
            stats = per_entity[src.entity]
            stats["gold_with_cui"] += 1
            proj_cui = proj.attributes.get(_CUI)
            if proj_cui:
                stats["projected"] += 1
                if proj_cui == gold_cui:
                    stats["projected_correct"] += 1
            else:
                stats["missing_mapping"] += 1
                concept = _concept_key(
                    ExectAnnotation(
                        src.entity,
                        src.text,
                        src.attributes,
                    )
                )
                missing_concepts[(src.entity, concept)] += 1
                if len(missing_examples[src.entity]) < 8:
                    missing_examples[src.entity].append(
                        {
                            "letter_id": letter.letter_id,
                            "entity": src.entity,
                            "concept": concept,
                            "gold_cui": gold_cui,
                        }
                    )
    out: dict[str, Any] = {}
    totals = {"gold_with_cui": 0, "projected": 0, "projected_correct": 0, "missing_mapping": 0}
    for entity, stats in per_entity.items():
        for k in totals:
            totals[k] += stats[k]
        gold_n = stats["gold_with_cui"]
        proj_n = stats["projected"]
        out[entity] = {
            **stats,
            "coverage": round(proj_n / gold_n, 4) if gold_n else 0.0,
            "correctness": round(stats["projected_correct"] / proj_n, 4) if proj_n else 0.0,
        }
    gold_n = totals["gold_with_cui"]
    proj_n = totals["projected"]
    out["__overall__"] = {
        **totals,
        "coverage": round(proj_n / gold_n, 4) if gold_n else 0.0,
        "correctness": round(totals["projected_correct"] / proj_n, 4) if proj_n else 0.0,
    }
    out["__missing_mapping__"] = {
        "concept_count": len(missing_concepts),
        "mention_count": sum(missing_concepts.values()),
        "examples": {
            entity: examples for entity, examples in sorted(missing_examples.items())
        },
    }
    return out


def cui_projection_audit(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    entities: Sequence[str] = ARTIFACT_LAYER_ENTITIES,
) -> dict[str, Any]:
    """Full CUI audit: buckets, deterministic coverage, and CUI-only benchmark loss."""

    pred_exect = _as_exect(pred_letters)
    projected_exect = [to_exect_letter(p) for p in _strip_and_project(_as_predicted(pred_letters))]
    benchmark = score_overall(gold_letters, pred_exect, entities, benchmark_config_for)
    benchmark_projected = score_overall(
        gold_letters, projected_exect, entities, benchmark_config_for
    )
    semantic = score_overall(gold_letters, pred_exect, entities, semantic_config_for)
    diagnostic = cui_projection_diagnostic(gold_letters, pred_exect, entities)
    per_entity: dict[str, Any] = {}
    for entity in entities:
        bench = benchmark.per_entity[entity].per_item
        sem = semantic.per_entity[entity].per_item
        d = diagnostic.per_entity[entity]
        per_entity[entity] = {
            "benchmark_f1": round(bench.f1, 4),
            "semantic_f1": round(sem.f1, 4),
            "cui_only_f1_gain_if_dropped": round(sem.f1 - bench.f1, 4),
            "prediction_cui_coverage": round(d.coverage, 4),
            "prediction_cui_agreement": round(d.cui_agreement_rate, 4),
            "gold_cui_density": round(d.gold_cui_density, 4),
        }
    return {
        "note": (
            "CUI is benchmark-format projection: the benchmark key keeps CUI, the "
            "semantic key drops it. The benchmark-minus-semantic delta is owned by "
            "deterministic CUI projection, never by LLM clinical reasoning."
        ),
        "overall": {
            "benchmark_f1_raw_llm": round(benchmark.per_item.f1, 4),
            "benchmark_f1_after_cui_projection": round(benchmark_projected.per_item.f1, 4),
            "semantic_f1": round(semantic.per_item.f1, 4),
            "cui_projection_recovers_f1": round(
                benchmark_projected.per_item.f1 - benchmark.per_item.f1, 4
            ),
            "residual_cui_loss_vs_semantic": round(
                semantic.per_item.f1 - benchmark_projected.per_item.f1, 4
            ),
        },
        "concept_buckets": cui_concept_buckets(gold_letters, entities),
        "deterministic_projection": cui_projection_coverage(gold_letters, entities),
        "per_entity": per_entity,
    }


# --------------------------------------------------------------------------- #
# Per-architecture assembly
# --------------------------------------------------------------------------- #
def _strip_and_project(pred_letters: Sequence[PredictedLetter]) -> list[PredictedLetter]:
    """Strip model-supplied CUI/CUIPhrase, then deterministically re-attach CUIs.

    This realizes the plan's ownership rule: the model never owns CUI; the
    deterministic projection attaches it after the clinical fact is selected.
    """

    projected: list[PredictedLetter] = []
    for letter in pred_letters:
        stripped = PredictedLetter(
            letter_id=letter.letter_id,
            mentions=tuple(
                m.model_copy(
                    update={
                        "attributes": {
                            k: v
                            for k, v in m.attributes.items()
                            if k not in (_CUI, _CUI_PHRASE)
                        }
                    }
                )
                for m in letter.mentions
            ),
            diagnostics=letter.diagnostics,
        )
        try:
            projected.append(project_cuis(stripped))
        except Exception:  # pragma: no cover - projection is best-effort here
            projected.append(stripped)
    return projected


def _strip_prediction_cui(pred_letters: Sequence[PredictedLetter]) -> list[PredictedLetter]:
    stripped: list[PredictedLetter] = []
    for letter in pred_letters:
        stripped.append(
            PredictedLetter(
                letter_id=letter.letter_id,
                mentions=tuple(
                    m.model_copy(
                        update={
                            "attributes": {
                                k: v
                                for k, v in m.attributes.items()
                                if k not in (_CUI, _CUI_PHRASE)
                            }
                        }
                    )
                    for m in letter.mentions
                ),
                diagnostics=letter.diagnostics,
            )
        )
    return stripped


def _strip_gold_cui(gold_letters: Sequence[ExectLetter]) -> list[ExectLetter]:
    return [
        ExectLetter(
            letter_id=letter.letter_id,
            note_text=letter.note_text,
            annotations=tuple(
                ExectAnnotation(
                    entity=ann.entity,
                    text=ann.text,
                    attributes={
                        k: v for k, v in ann.attributes.items() if k not in (_CUI, _CUI_PHRASE)
                    },
                    raw_text=ann.raw_text,
                )
                for ann in letter.annotations
            ),
        )
        for letter in gold_letters
    ]


def _as_predicted(pred_letters: Sequence[Any]) -> list[PredictedLetter]:
    out: list[PredictedLetter] = []
    for letter in pred_letters:
        if isinstance(letter, PredictedLetter):
            out.append(letter)
        else:  # already an ExectLetter -> wrap
            out.append(
                PredictedLetter(
                    letter_id=letter.letter_id,
                    mentions=tuple(
                        PredictedMention(
                            entity=a.entity,
                            text=a.text,
                            attributes=dict(a.attributes),
                            evidence="",
                        )
                        for a in letter.annotations
                    ),
                )
            )
    return out


def _as_exect(pred_letters: Sequence[Any]) -> list[ExectLetter]:
    out: list[ExectLetter] = []
    for letter in pred_letters:
        if isinstance(letter, ExectLetter):
            out.append(letter)
        else:
            out.append(to_exect_letter(letter))
    return out


def _score_for_primary(entity: str, scorecard: dict[str, Any]) -> dict[str, Any]:
    score = scorecard["headline_scores"][entity]
    if entity in _ESSENTIAL_ATOMIC_CONCEPT_ONLY:
        return score["concept_only"]
    return score["headline"]


def _aggregate_score_dicts(scores: Sequence[dict[str, Any]]) -> dict[str, Any]:
    precision_tp = recall_tp = pred_count = gold_count = 0
    for score in scores:
        precision_tp += int(score.get("precision_tp", score["tp"]))
        recall_tp += int(score.get("recall_tp", score["tp"]))
        pred_count += int(score["pred_count"])
        gold_count += int(score["gold_count"])
    precision = precision_tp / pred_count if pred_count else 0.0
    recall = recall_tp / gold_count if gold_count else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": recall_tp,
        "precision_tp": precision_tp,
        "recall_tp": recall_tp,
        "fp": max(0, pred_count - precision_tp),
        "fn": max(0, gold_count - recall_tp),
        "pred_count": pred_count,
        "gold_count": gold_count,
    }


def _primary_recovery(
    scorecard: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    scores = {
        entity: _score_for_primary(entity, scorecard)
        for entity in ESSENTIAL_CLINICAL_ENTITIES
    }
    return _aggregate_score_dicts(tuple(scores.values())), scores


def evidence_validation_summary(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[PredictedLetter],
    entities: Sequence[str] = ESSENTIAL_CLINICAL_ENTITIES,
) -> dict[str, Any]:
    """Summarize exact evidence-substring validity for prediction mentions.

    Evidence policy for this analysis-only replay is deliberately narrow:
    evidence is valid only when the prediction carries non-empty evidence text
    and that text appears verbatim in the source letter text. This is a source
    validity gate, not a claim that the evidence proves the extracted concept.
    """

    note_by_id = {letter.letter_id: letter.note_text or "" for letter in gold_letters}
    entity_set = set(entities)
    per_entity: dict[str, dict[str, int]] = {
        e: {"predicted_mentions": 0, "evidence_present": 0, "exact_evidence": 0}
        for e in entities
    }
    for pred in pred_letters:
        note = note_by_id.get(pred.letter_id, "")
        for mention in pred.mentions:
            if mention.entity not in entity_set:
                continue
            stats = per_entity[mention.entity]
            stats["predicted_mentions"] += 1
            evidence = mention.evidence.strip()
            if not evidence:
                continue
            stats["evidence_present"] += 1
            if note and evidence in note:
                stats["exact_evidence"] += 1

    totals = {"predicted_mentions": 0, "evidence_present": 0, "exact_evidence": 0}
    out: dict[str, Any] = {}
    for entity, stats in per_entity.items():
        for key in totals:
            totals[key] += stats[key]
        pred_n = stats["predicted_mentions"]
        invalid = pred_n - stats["exact_evidence"]
        out[entity] = {
            **stats,
            "invalid_evidence": invalid,
            "evidence_present_rate": round(stats["evidence_present"] / pred_n, 4)
            if pred_n
            else 0.0,
            "exact_evidence_rate": round(stats["exact_evidence"] / pred_n, 4)
            if pred_n
            else 0.0,
            "invalid_evidence_rate": round(invalid / pred_n, 4) if pred_n else 0.0,
        }
    pred_n = totals["predicted_mentions"]
    invalid = pred_n - totals["exact_evidence"]
    out["overall"] = {
        **totals,
        "invalid_evidence": invalid,
        "evidence_present_rate": round(totals["evidence_present"] / pred_n, 4)
        if pred_n
        else 0.0,
        "exact_evidence_rate": round(totals["exact_evidence"] / pred_n, 4)
        if pred_n
        else 0.0,
        "invalid_evidence_rate": round(invalid / pred_n, 4) if pred_n else 0.0,
    }
    return out


def error_taxonomy_summary(
    primary_scores: dict[str, dict[str, Any]],
    evidence_summary: dict[str, Any],
) -> dict[str, Any]:
    """Coarse corpus-level error taxonomy for the LLM-first report.

    ``candidate_miss`` is unmatched gold clinical detail (FN);
    ``wrong_detail_selection`` is unmatched emitted detail (FP);
    ``evidence_failure`` is an emitted mention without exact source evidence.
    The categories are diagnostic and can overlap.
    """

    per_entity: dict[str, dict[str, int]] = {}
    totals = {"candidate_miss": 0, "wrong_detail_selection": 0, "evidence_failure": 0}
    for entity in ESSENTIAL_CLINICAL_ENTITIES:
        score = primary_scores[entity]
        evidence = evidence_summary[entity]
        row = {
            "candidate_miss": int(score["fn"]),
            "wrong_detail_selection": int(score["fp"]),
            "evidence_failure": int(
                evidence["predicted_mentions"] - evidence["exact_evidence"]
            ),
        }
        per_entity[entity] = row
        for key in totals:
            totals[key] += row[key]
    return {
        "note": (
            "Coarse diagnostic taxonomy; categories can overlap and do not replace "
            "row-level adjudication."
        ),
        "overall": totals,
        "per_entity": per_entity,
    }


_ERROR_TYPES: tuple[str, ...] = (
    "candidate_miss",
    "wrong_detail_selection",
    "projection_gap",
    "evidence_failure",
)


def _counter_match_counts(
    gold_keys: Sequence[Hashable],
    pred_keys: Sequence[Hashable],
) -> tuple[int, int, int]:
    gold = Counter(gold_keys)
    pred = Counter(pred_keys)
    tp = sum((gold & pred).values())
    return tp, max(0, sum(gold.values()) - tp), max(0, sum(pred.values()) - tp)


def _limited_counter_examples(keys: Sequence[Hashable], limit: int = 4) -> str:
    examples = []
    for key, count in Counter(keys).most_common(limit):
        suffix = f" x{count}" if count > 1 else ""
        examples.append(f"{key!r}{suffix}")
    return "; ".join(examples)


def _entity_letter(
    letter_id: str,
    note_text: str,
    annotations: Sequence[ExectAnnotation],
) -> ExectLetter:
    return ExectLetter(letter_id=letter_id, note_text=note_text, annotations=tuple(annotations))


def _pred_to_exect_with_note(pred: PredictedLetter, note_text: str) -> ExectLetter:
    return ExectLetter(
        letter_id=pred.letter_id,
        note_text=note_text,
        annotations=tuple(
            ExectAnnotation(
                entity=m.entity,
                text=m.text,
                attributes=dict(m.attributes),
            )
            for m in pred.mentions
        ),
    )


def _primary_row_key_sets(
    *,
    family: str,
    gold: ExectLetter,
    pred: ExectLetter,
) -> tuple[list[Hashable], list[Hashable], list[Hashable]]:
    """Return gold, precision-prediction, and recall-prediction keys.

    Diagnosis and EpilepsyCause use the same entity-agnostic recall/home-tagged
    precision contract as ``score_concept_identity``. The other essential
    families use their headline component keys directly.
    """

    if family == PRESCRIPTION.name:
        gold_keys = _prescription_component_keys(
            gold.entities(family),
            "clinical_headline",
            gold.note_text,
        )
        pred_keys = _prescription_component_keys(
            pred.entities(family),
            "clinical_headline",
            pred.note_text,
        )
        return gold_keys, pred_keys, pred_keys
    if family == SEIZURE_FREQUENCY.name:
        gold_keys = _frequency_state_keys(gold.entities(family), "clinical_headline")
        pred_keys = _frequency_state_keys(pred.entities(family), "clinical_headline")
        return gold_keys, pred_keys, pred_keys
    if family == INVESTIGATIONS.name:
        gold_keys = _investigation_component_keys(gold.entities(family), "clinical_headline")
        pred_keys = _investigation_component_keys(pred.entities(family), "clinical_headline")
        return gold_keys, pred_keys, pred_keys
    if family in _ESSENTIAL_ATOMIC_CONCEPT_ONLY:
        return (
            _concept_keys(gold.entities(family), family, "concept"),
            _concept_keys(pred.entities(family), family, "concept"),
            _concept_keys(pred.annotations, family, "concept"),
        )
    raise ValueError(f"Unsupported essential family {family!r}")


def _entity_match_tp(
    gold: ExectLetter,
    pred: ExectLetter,
    family: str,
    config: MatchConfig,
) -> int:
    return _counter_match_counts(
        [match_key(a, config) for a in gold.entities(family)],
        [match_key(a, config) for a in pred.entities(family)],
    )[0]


def _exact_evidence_counts(
    gold: ExectLetter,
    pred: PredictedLetter,
    family: str,
) -> tuple[int, int, int, str]:
    note = gold.note_text or ""
    predicted = 0
    exact = 0
    failures: list[str] = []
    for mention in pred.mentions:
        if mention.entity != family:
            continue
        predicted += 1
        evidence = mention.evidence.strip()
        if evidence and note and evidence in note:
            exact += 1
        else:
            failures.append(evidence or "<missing>")
    return predicted, exact, predicted - exact, "; ".join(failures[:4])


def row_level_error_ledger(
    *,
    architecture: str,
    ownership: str,
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[PredictedLetter],
    families: Sequence[str] = ESSENTIAL_CLINICAL_ENTITIES,
) -> list[dict[str, Any]]:
    """Build a dev-row essential-family error ledger from replayed artifacts.

    Rows are ``letter_id`` + ``family`` + ``error_type``. Counts reconcile with
    the primary CUI-free headline for candidate misses and wrong detail
    selections. Projection gaps are benchmark-layer losses after deterministic
    CUI projection: a CUI-free semantic mention match exists but the projected
    benchmark key still does not match.
    """

    pred_by_id = {letter.letter_id: letter for letter in pred_letters}
    projected_by_id = {
        letter.letter_id: letter for letter in _strip_and_project(_as_predicted(pred_letters))
    }
    rows: list[dict[str, Any]] = []
    for gold in gold_letters:
        pred = pred_by_id.get(
            gold.letter_id,
            PredictedLetter(letter_id=gold.letter_id, mentions=()),
        )
        projected = projected_by_id.get(gold.letter_id, pred)

        gold_cui_free = _strip_gold_cui([gold])[0]
        pred_cui_free = _pred_to_exect_with_note(_strip_prediction_cui([pred])[0], gold.note_text)
        projected_exect = _pred_to_exect_with_note(projected, gold.note_text)
        raw_pred_exect = _pred_to_exect_with_note(pred, gold.note_text)

        for family in families:
            family_gold = _entity_letter(
                gold_cui_free.letter_id,
                gold_cui_free.note_text,
                gold_cui_free.entities(family),
            )
            family_pred = _entity_letter(
                pred_cui_free.letter_id,
                pred_cui_free.note_text,
                pred_cui_free.entities(family),
            )
            gold_keys, home_pred_keys, recall_pred_keys = _primary_row_key_sets(
                family=family,
                gold=gold_cui_free,
                pred=pred_cui_free,
            )
            _, candidate_miss, _ = _counter_match_counts(gold_keys, recall_pred_keys)
            _, _, wrong_detail_selection = _counter_match_counts(
                gold_keys,
                home_pred_keys,
            )
            semantic_tp = _entity_match_tp(
                family_gold,
                family_pred,
                family,
                semantic_config_for(family),
            )
            projected_benchmark_tp = _entity_match_tp(
                gold,
                projected_exect,
                family,
                benchmark_config_for(family),
            )
            projection_gap = max(0, semantic_tp - projected_benchmark_tp)
            evidence_predicted, exact_evidence, evidence_failure, evidence_examples = (
                _exact_evidence_counts(gold, pred, family)
            )
            counts = {
                "candidate_miss": candidate_miss,
                "wrong_detail_selection": wrong_detail_selection,
                "projection_gap": projection_gap,
                "evidence_failure": evidence_failure,
            }
            base = {
                "architecture": architecture,
                "ownership": ownership,
                "letter_id": gold.letter_id,
                "family": family,
                "gold_count": len(gold_keys),
                "pred_count": len(home_pred_keys),
                "primary_tp": _counter_match_counts(gold_keys, recall_pred_keys)[0],
                "candidate_miss": candidate_miss,
                "wrong_detail_selection": wrong_detail_selection,
                "projection_gap": projection_gap,
                "evidence_failure": evidence_failure,
                "semantic_tp": semantic_tp,
                "projected_benchmark_tp": projected_benchmark_tp,
                "raw_benchmark_tp": _entity_match_tp(
                    gold,
                    raw_pred_exect,
                    family,
                    benchmark_config_for(family),
                ),
                "evidence_predicted": evidence_predicted,
                "exact_evidence": exact_evidence,
                "gold_examples": _limited_counter_examples(gold_keys),
                "pred_examples": _limited_counter_examples(home_pred_keys),
                "evidence_examples": evidence_examples,
            }
            for error_type in _ERROR_TYPES:
                count = counts[error_type]
                if count <= 0:
                    continue
                rows.append({**base, "error_type": error_type, "count": count})
    return rows


def architecture_report(
    *,
    name: str,
    ownership: str,
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[PredictedLetter],
    entities: Sequence[str] = ARTIFACT_LAYER_ENTITIES,
    include_row_error_ledger: bool = False,
) -> dict[str, Any]:
    """Build the full layer ladder for one architecture over one artifact."""

    predicted = _as_predicted(pred_letters)
    cui_free_gold = _strip_gold_cui(gold_letters)
    cui_free_predicted = _strip_prediction_cui(predicted)
    cui_free_scorecard = build_scorecard(cui_free_gold, cui_free_predicted)
    primary_overall, primary_scores = _primary_recovery(cui_free_scorecard)

    # Companion diagnostic: attach deterministic CUI before scoring so the
    # legacy SeizureFrequency key that prefers CUI can be compared explicitly.
    projected = _strip_and_project(predicted)
    projected_scorecard = build_scorecard(gold_letters, projected)
    projected_overall, projected_scores = _primary_recovery(projected_scorecard)
    nonessential = {
        entity: cui_free_scorecard["headline_scores"][entity]["headline"]
        for entity in cui_free_scorecard["headline_entities"]
        if entity not in ESSENTIAL_CLINICAL_ENTITIES
    }
    evidence_summary = evidence_validation_summary(
        gold_letters,
        predicted,
        ESSENTIAL_CLINICAL_ENTITIES,
    )
    report = {
        "name": name,
        "ownership": ownership,
        "row_count": len(gold_letters),
        "clinical_recovery_note": (
            "Primary clinical-recovery headline is CUI-free and aggregates only "
            "the five essential families. A CUI-projected companion score is "
            "reported separately because the legacy SeizureFrequency state key "
            "uses CUI as seizure-type identity when present."
        ),
        "clinical_recovery": {
            "primary_entities": list(ESSENTIAL_CLINICAL_ENTITIES),
            "overall": primary_overall,
            "headline_scores": primary_scores,
            "cui_projected_overall": projected_overall,
            "cui_projected_headline_scores": projected_scores,
            "diagnostic_nonessential_scores": nonessential,
            "artifact_projection_scores": projected_scorecard["artifact_projection_scores"],
        },
        "evidence_validation": evidence_summary,
        "error_taxonomy": error_taxonomy_summary(primary_scores, evidence_summary),
        "certainty_audit": certainty_projection_audit(gold_letters, predicted, entities),
        "cui_audit": cui_projection_audit(gold_letters, predicted, entities),
    }
    if include_row_error_ledger:
        report["row_error_ledger"] = row_level_error_ledger(
            architecture=name,
            ownership=ownership,
            gold_letters=gold_letters,
            pred_letters=predicted,
        )
    return report
