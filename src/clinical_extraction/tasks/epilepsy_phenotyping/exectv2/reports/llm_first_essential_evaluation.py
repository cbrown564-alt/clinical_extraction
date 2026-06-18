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
from collections import Counter, defaultdict
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    INVESTIGATIONS,
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
    benchmark_config_for,
    benchmark_ignore_for,
    normalize_phrase,
    score_overall,
    semantic_config_for,
)

_CERTAINTY = "Certainty"
_NEGATION = "Negation"
_CUI = "CUI"
_CUI_PHRASE = "CUIPhrase"
_CERTAINTY_ATTRS = frozenset({_CERTAINTY, _NEGATION})

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
        "ignored_attributes": sorted(_CERTAINTY_ATTRS),
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

    # (entity, concept) -> CUIs observed in gold
    concept_cuis: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for letter in gold_letters:
        for entity in entities:
            for ann in letter.entities(entity):
                cui = ann.attributes.get(_CUI)
                if cui:
                    concept_cuis[(entity, _concept_key(ann))][cui] += 1

    bucket_counts: Counter[str] = Counter()
    bucket_concepts: Counter[str] = Counter()
    examples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    per_entity: dict[str, Counter[str]] = defaultdict(Counter)
    for (entity, concept), cuis in concept_cuis.items():
        mentions = sum(cuis.values())
        distinct = len(cuis)
        if distinct == 1:
            bucket = "one_to_one"
        elif entity == INVESTIGATIONS.name:
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


def architecture_report(
    *,
    name: str,
    ownership: str,
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[PredictedLetter],
    entities: Sequence[str] = ARTIFACT_LAYER_ENTITIES,
) -> dict[str, Any]:
    """Build the full layer ladder for one architecture over one artifact."""

    predicted = _as_predicted(pred_letters)
    # The plan's ownership ladder attaches CUI deterministically *before* the key
    # is rendered. The SeizureFrequency state key uses CUI as the seizure-type
    # identity when present (and all gold SF mentions carry one), so scoring raw
    # CUI-free LLM output collapses SF to 0 as a projection artifact. Projecting
    # CUI first is idempotent for rules_only and harmless for the CUI-free concept
    # and prescription/investigation component keys; it only un-gates SF.
    projected = _strip_and_project(predicted)
    scorecard = build_scorecard(gold_letters, projected)
    return {
        "name": name,
        "ownership": ownership,
        "row_count": len(gold_letters),
        "clinical_recovery_note": (
            "Clinical-recovery headline computed on CUI-projected predictions "
            "(deterministic CUI attached before scoring, per the ownership ladder); "
            "the SeizureFrequency state key uses CUI as seizure-type identity."
        ),
        "clinical_recovery": {
            "overall": scorecard["overall_clinical_recovery"],
            "headline_scores": {
                entity: scorecard["headline_scores"][entity]["headline"]
                for entity in scorecard["headline_entities"]
            },
            "artifact_projection_scores": scorecard["artifact_projection_scores"],
        },
        "certainty_audit": certainty_projection_audit(gold_letters, predicted, entities),
        "cui_audit": cui_projection_audit(gold_letters, predicted, entities),
    }
