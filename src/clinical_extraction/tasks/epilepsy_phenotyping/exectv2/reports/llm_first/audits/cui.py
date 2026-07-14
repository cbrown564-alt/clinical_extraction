"""CUI projection audit (plan report #3)."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Sequence
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.clinical_recovery_scorecard import (
    ARTIFACT_LAYER_ENTITIES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.cui_projection_diagnostic import (
    cui_projection_diagnostic,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.constants import (
    CUI,
    CUI_PHRASE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.projection import (
    as_exect,
    as_predicted,
    strip_and_project,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    benchmark_config_for,
    score_overall,
    semantic_config_for,
)


def _concept_key(ann: ExectAnnotation) -> str:
    return normalize_phrase(ann.attributes.get(CUI_PHRASE) or ann.text)


def _investigation_result_key(ann: ExectAnnotation) -> str:
    for modality in ("EEG", "MRI", "CT"):
        result = ann.attributes.get(f"{modality}_Results")
        if result:
            return f"{modality}:{result}"
    return "unknown_result"


def cui_concept_buckets(
    gold_letters: Sequence[ExectLetter],
    entities: Sequence[str],
) -> dict[str, Any]:
    """Bucket every gold clinical concept by its CUI projection character."""

    concept_cuis: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    concept_results: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for letter in gold_letters:
        for entity in entities:
            for ann in letter.entities(entity):
                cui = ann.attributes.get(CUI)
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


def cui_projection_coverage(
    gold_letters: Sequence[ExectLetter],
    entities: Sequence[str],
) -> dict[str, Any]:
    """Run the deterministic projection over gold and measure coverage/correctness."""

    per_entity: dict[str, dict[str, int]] = {
        e: {"gold_with_cui": 0, "projected": 0, "projected_correct": 0, "missing_mapping": 0}
        for e in entities
    }
    missing_examples: dict[str, list[dict[str, str]]] = defaultdict(list)
    missing_concepts: Counter[tuple[str, str]] = Counter()
    entity_set = set(entities)
    for letter in gold_letters:
        gold_cuis = [
            ann.attributes.get(CUI) for ann in letter.annotations if ann.entity in entity_set
        ]
        stripped = PredictedLetter(
            letter_id=letter.letter_id,
            mentions=tuple(
                PredictedMention(
                    entity=ann.entity,
                    text=ann.text,
                    attributes={
                        k: v for k, v in ann.attributes.items() if k not in (CUI, CUI_PHRASE)
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
            proj_cui = proj.attributes.get(CUI)
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
        "examples": {entity: examples for entity, examples in sorted(missing_examples.items())},
    }
    return out


def cui_projection_audit(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[Any],
    entities: Sequence[str] = ARTIFACT_LAYER_ENTITIES,
) -> dict[str, Any]:
    """Full CUI audit: buckets, deterministic coverage, and CUI-only benchmark loss."""

    pred_exect = as_exect(pred_letters)
    projected_exect = [to_exect_letter(p) for p in strip_and_project(as_predicted(pred_letters))]
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
