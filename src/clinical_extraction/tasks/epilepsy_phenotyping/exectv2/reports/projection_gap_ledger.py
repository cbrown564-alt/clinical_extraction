"""Reusable all-entity projection-gap ledger for ExECTv2.

This is the cross-entity generalization of the PatientHistory error ledger that
already ships in ``deterministic_all9_scorecard``. For every entity it classifies
each unmatched gold mention and each unmatched predicted mention into a layered
gap family, and tags each gold miss as either a *candidate-source* miss (the
clinical concept is genuinely absent from predictions) or a *projection* miss
(the concept was recovered; only the benchmark mention key differs). That
candidate-source-vs-projection axis is Finding 2 of the all-9 layered error
analysis (2026-06-17): ~one third of benchmark false negatives are projection,
not recall, and the right architectural move differs between the two regimes.

The ledger is diagnostic, not an authoritative score. It pairs mentions with a
cascade of the same per-entity match configs the scorer uses
(``benchmark`` -> ``semantic`` -> ``phrase``), so the family counts reconcile with
the three-layer scorecard up to greedy-pairing ties. Promotion gates should read
the scorecard for headline F1 and this ledger for *where* the loss sits.
"""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ALL_ENTITIES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
    to_exect_annotation,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    run_all9_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    benchmark_config_for,
    match_key,
    score_prescription_benchmark_projection,
    score_prescription_components,
    semantic_config_for,
)

ALL_ENTITY_NAMES: tuple[str, ...] = tuple(spec.name for spec in ALL_ENTITIES)

# Gap families, ordered from shallowest (phrase) to deepest (CUI) projection, then
# the over-emission family on the prediction side.
GAP_PHRASE_COVERAGE = "phrase_coverage"
GAP_ATTRIBUTE_BUNDLE = "attribute_bundle"
GAP_CUI_PROJECTION = "cui_projection"
GAP_OVER_EMISSION = "over_emission"
GAP_FAMILIES: tuple[str, ...] = (
    GAP_PHRASE_COVERAGE,
    GAP_ATTRIBUTE_BUNDLE,
    GAP_CUI_PROJECTION,
    GAP_OVER_EMISSION,
)

# Miss kinds. ``candidate_source`` and ``projection`` apply to gold misses;
# ``over_emission`` to predicted false positives.
MISS_CANDIDATE_SOURCE = "candidate_source"
MISS_PROJECTION = "projection"
MISS_OVER_EMISSION = "over_emission"

# Regime thresholds on the projection share of gold misses (Finding 2). These
# diagnostic heuristics keep the original regime bands: representation-bound
# entities ran 67-100% projection, recall-bound 17-29%, and the mixed pair
# (SeizureFrequency, Onset) sat at 55-58% in the historical analysis.
REGIME_REPRESENTATION_BOUND_MIN = 0.60
REGIME_RECALL_BOUND_MAX = 0.40

# Prescription component families requested by the work board (PROJECT_STATUS):
# source/defaulted frequency, future medication, weight-based dosing, and rescue.
PRESCRIPTION_COMPONENT_FAMILIES: tuple[str, ...] = (
    "source_stated_frequency",
    "guideline_defaulted_frequency",
    "rescue_regimen",
    "future_medication",
    "weight_based_dosing",
)


@dataclass(frozen=True)
class ProjectionGapRecord:
    """One classified gap between gold and predicted mentions for a letter+entity.

    Records are emitted only for non-matching outcomes: gold false negatives
    (``side="gold"``) and predicted false positives (``side="predicted"``). A
    ``cui_projection`` or ``attribute_bundle`` record carries *both* the gold and
    the predicted side of the pairing that failed at the deeper layer.
    """

    letter_id: str
    entity: str
    side: Literal["gold", "predicted"]
    gap_family: str
    miss_kind: str
    phrase_match: bool
    semantic_match: bool
    benchmark_match: bool
    concept_cui_present: bool
    gold_phrase: str | None
    predicted_phrase: str | None
    gold_attributes: dict[str, str] | None
    predicted_attributes: dict[str, str] | None
    evidence: str


def _pair_by_config(
    gold: Sequence[ExectAnnotation],
    pred: Sequence[ExectAnnotation],
    gold_used: set[int],
    pred_used: set[int],
    config: Any,
) -> list[tuple[int, int]]:
    """Greedily pair still-unused gold/pred mentions whose match keys agree."""

    pred_by_key: dict[Any, list[int]] = defaultdict(list)
    for pi, mention in enumerate(pred):
        if pi in pred_used:
            continue
        pred_by_key[match_key(mention, config)].append(pi)

    pairs: list[tuple[int, int]] = []
    for gi, mention in enumerate(gold):
        if gi in gold_used:
            continue
        bucket = pred_by_key.get(match_key(mention, config))
        if bucket:
            pi = bucket.pop(0)
            gold_used.add(gi)
            pred_used.add(pi)
            pairs.append((gi, pi))
    return pairs


def _entity_records(
    letter_id: str,
    entity: str,
    gold: Sequence[ExectAnnotation],
    pred_mentions: Sequence[PredictedMention],
) -> list[ProjectionGapRecord]:
    pred_anns = [to_exect_annotation(mention) for mention in pred_mentions]
    benchmark_cfg = benchmark_config_for(entity)
    semantic_cfg = semantic_config_for(entity)

    gold_used: set[int] = set()
    pred_used: set[int] = set()

    # Deepest layer first: a benchmark match implies semantic and phrase match, so
    # consuming it first leaves only genuinely shallower pairings behind.
    _pair_by_config(gold, pred_anns, gold_used, pred_used, benchmark_cfg)
    cui_pairs = _pair_by_config(gold, pred_anns, gold_used, pred_used, semantic_cfg)
    attr_pairs = _pair_by_config(gold, pred_anns, gold_used, pred_used, PHRASE_ONLY)

    pred_cuis = {
        mention.attributes["CUI"] for mention in pred_anns if mention.attributes.get("CUI")
    }

    records: list[ProjectionGapRecord] = []
    for gi, pi in cui_pairs:
        records.append(
            _paired_record(
                letter_id,
                entity,
                gold[gi],
                pred_mentions[pi],
                pred_cuis,
                gap_family=GAP_CUI_PROJECTION,
                phrase_match=True,
                semantic_match=True,
            )
        )
    for gi, pi in attr_pairs:
        records.append(
            _paired_record(
                letter_id,
                entity,
                gold[gi],
                pred_mentions[pi],
                pred_cuis,
                gap_family=GAP_ATTRIBUTE_BUNDLE,
                phrase_match=True,
                semantic_match=False,
            )
        )
    for gi, mention in enumerate(gold):
        if gi in gold_used:
            continue
        cui_present = _gold_cui_present(mention, pred_cuis)
        records.append(
            ProjectionGapRecord(
                letter_id=letter_id,
                entity=entity,
                side="gold",
                gap_family=GAP_PHRASE_COVERAGE,
                miss_kind=MISS_PROJECTION if cui_present else MISS_CANDIDATE_SOURCE,
                phrase_match=False,
                semantic_match=False,
                benchmark_match=False,
                concept_cui_present=cui_present,
                gold_phrase=mention.text,
                predicted_phrase=None,
                gold_attributes=dict(mention.attributes),
                predicted_attributes=None,
                evidence=mention.raw_text or mention.text,
            )
        )
    for pi, mention in enumerate(pred_mentions):
        if pi in pred_used:
            continue
        records.append(
            ProjectionGapRecord(
                letter_id=letter_id,
                entity=entity,
                side="predicted",
                gap_family=GAP_OVER_EMISSION,
                miss_kind=MISS_OVER_EMISSION,
                phrase_match=False,
                semantic_match=False,
                benchmark_match=False,
                concept_cui_present=False,
                gold_phrase=None,
                predicted_phrase=mention.text,
                gold_attributes=None,
                predicted_attributes=dict(mention.attributes),
                evidence=mention.evidence,
            )
        )
    return records


def _gold_cui_present(gold: ExectAnnotation, pred_cuis: set[str]) -> bool:
    """Finding 2's concept-recovery proxy: is the gold mention's CUI among preds?"""

    cui = gold.attributes.get("CUI")
    return bool(cui) and cui in pred_cuis


def _paired_record(
    letter_id: str,
    entity: str,
    gold: ExectAnnotation,
    pred: PredictedMention,
    pred_cuis: set[str],
    *,
    gap_family: str,
    phrase_match: bool,
    semantic_match: bool,
) -> ProjectionGapRecord:
    # ``miss_kind`` tracks concept (CUI) recovery (Finding 2); ``gap_family`` tracks
    # the layer where the benchmark key broke. They are orthogonal: a phrase+attribute
    # match whose result-specific CUI is genuinely absent (e.g. Investigations EEG
    # result) is an attribute_bundle gap but a candidate_source miss.
    cui_present = _gold_cui_present(gold, pred_cuis)
    return ProjectionGapRecord(
        letter_id=letter_id,
        entity=entity,
        side="gold",
        gap_family=gap_family,
        miss_kind=MISS_PROJECTION if cui_present else MISS_CANDIDATE_SOURCE,
        phrase_match=phrase_match,
        semantic_match=semantic_match,
        benchmark_match=False,
        concept_cui_present=cui_present,
        gold_phrase=gold.text,
        predicted_phrase=pred.text,
        gold_attributes=dict(gold.attributes),
        predicted_attributes=dict(pred.attributes),
        evidence=pred.evidence or gold.raw_text or gold.text,
    )


def build_projection_gap_records(
    gold_letters: Sequence[ExectLetter],
    predictions: Sequence[PredictedLetter],
    entities: Sequence[str] = ALL_ENTITY_NAMES,
) -> list[ProjectionGapRecord]:
    """Classify every gold FN and predicted FP across ``entities`` into a gap family."""

    pred_by_id = {prediction.letter_id: prediction for prediction in predictions}
    records: list[ProjectionGapRecord] = []
    for gold_letter in gold_letters:
        prediction = pred_by_id.get(gold_letter.letter_id)
        mentions = prediction.mentions if prediction is not None else ()
        for entity in entities:
            gold = gold_letter.entities(entity)
            pred_mentions = [mention for mention in mentions if mention.entity == entity]
            if not gold and not pred_mentions:
                continue
            records.extend(_entity_records(gold_letter.letter_id, entity, gold, pred_mentions))
    return records


def _regime_for(projection: int, candidate_source: int) -> str:
    total = projection + candidate_source
    if total == 0:
        return "no_misses"
    share = projection / total
    if share >= REGIME_REPRESENTATION_BOUND_MIN:
        return "representation_bound"
    if share < REGIME_RECALL_BOUND_MAX:
        return "recall_bound"
    return "mixed"


def summarize_records(records: Sequence[ProjectionGapRecord]) -> dict[str, Any]:
    """Roll classified records up into per-entity gap-family and regime counts."""

    per_entity: dict[str, dict[str, Any]] = {}
    for entity in ALL_ENTITY_NAMES:
        entity_records = [record for record in records if record.entity == entity]
        family_counts = {family: 0 for family in GAP_FAMILIES}
        for record in entity_records:
            family_counts[record.gap_family] += 1
        projection = sum(1 for r in entity_records if r.miss_kind == MISS_PROJECTION)
        candidate_source = sum(1 for r in entity_records if r.miss_kind == MISS_CANDIDATE_SOURCE)
        over_emission = family_counts[GAP_OVER_EMISSION]
        gold_misses = projection + candidate_source
        per_entity[entity] = {
            "gold_misses": gold_misses,
            "projection_misses": projection,
            "candidate_source_misses": candidate_source,
            "projection_share": round(projection / gold_misses, 4) if gold_misses else 0.0,
            "over_emission": over_emission,
            "regime": _regime_for(projection, candidate_source),
            "gap_families": family_counts,
        }

    totals = {
        "gold_misses": sum(e["gold_misses"] for e in per_entity.values()),
        "projection_misses": sum(e["projection_misses"] for e in per_entity.values()),
        "candidate_source_misses": sum(e["candidate_source_misses"] for e in per_entity.values()),
        "over_emission": sum(e["over_emission"] for e in per_entity.values()),
    }
    totals["projection_share"] = (
        round(totals["projection_misses"] / totals["gold_misses"], 4)
        if totals["gold_misses"]
        else 0.0
    )
    return {"per_entity": per_entity, "totals": totals}


def _prescription_component_families(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> dict[str, Any]:
    components = score_prescription_components(gold_letters, pred_letters)
    projection = score_prescription_benchmark_projection(gold_letters, pred_letters)
    families = {
        family: _prf1_to_dict(getattr(components, family))
        for family in PRESCRIPTION_COMPONENT_FAMILIES
    }
    families["phrase_scope"] = _prf1_to_dict(projection.phrase_scope)
    families["drugname_cui_projection"] = _prf1_to_dict(projection.drugname_cui_projection)
    return families


def _prf1_to_dict(score: Any) -> dict[str, Any]:
    return {
        "f1": round(score.f1, 4),
        "precision": round(score.precision, 4),
        "recall": round(score.recall, 4),
        "tp": score.tp,
        "fp": score.fp,
        "fn": score.fn,
    }


def build_projection_gap_ledger(
    gold_letters: Sequence[ExectLetter],
    predictions: Sequence[PredictedLetter],
    entities: Sequence[str] = ALL_ENTITY_NAMES,
) -> dict[str, Any]:
    """Build the full ledger: classified records, per-entity rollup, Rx families."""

    records = build_projection_gap_records(gold_letters, predictions, entities)
    pred_letters = [
        to_exect_letter(prediction, note_text=gold.note_text)
        for prediction, gold in zip(predictions, gold_letters, strict=True)
    ]
    return {
        "row_count": len(gold_letters),
        "scored_entities": list(entities),
        "summary": summarize_records(records),
        "prescription_component_families": _prescription_component_families(
            gold_letters, pred_letters
        ),
        "records": [asdict(record) for record in records],
    }


def write_projection_gap_ledger_artifacts(
    *,
    out_json: Path,
    out_md: Path,
    split: str = "dev",
    generated_on: str | None = None,
) -> tuple[Path, Path]:
    """Run deterministic all-9 on ``split`` and write JSON + Markdown ledger artifacts."""

    generated_on = generated_on or date.today().isoformat()
    gold_letters = load_letters_for_split(split)
    predictions = run_all9_on_letters(gold_letters)
    ledger = build_projection_gap_ledger(gold_letters, predictions)
    ledger.update({"split": split, "generated_on": generated_on})

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(_render_markdown(ledger, json_path=out_json), encoding="utf-8")
    return out_json, out_md


def _render_markdown(ledger: dict[str, Any], *, json_path: Path) -> str:
    summary = ledger["summary"]
    totals = summary["totals"]
    lines = [
        "# ExECTv2 Projection-Gap Ledger",
        "",
        f"- Generated: `{ledger['generated_on']}`",
        f"- JSON: `{json_path}`",
        f"- Split: `{ledger['split']}`",
        f"- Letters: {ledger['row_count']}",
        f"- Records: {len(ledger['records'])}",
        "",
        (
            "Diagnostic ledger: every gold false negative and predicted false "
            "positive, classified into a layered `gap_family` (which key layer "
            "broke) and tagged `miss_kind` candidate-source vs projection by "
            "Finding 2's concept-recovery proxy (is the gold CUI present among "
            "predictions). The two axes are orthogonal: a phrase+attribute match "
            "whose result-specific CUI is absent is an `attribute_bundle` gap but "
            "a `candidate_source` miss. Read alongside the three-layer scorecard "
            "for headline F1."
        ),
        "",
        "## Totals",
        "",
        f"- Gold misses: {totals['gold_misses']}",
        f"- Projection misses (concept recovered, key differs): {totals['projection_misses']}",
        f"- Candidate-source misses (concept absent): {totals['candidate_source_misses']}",
        f"- Projection share of gold misses: {totals['projection_share']:.4f}",
        f"- Over-emissions (predicted FP): {totals['over_emission']}",
        "",
        "## Per-Entity Regime And Gap Families",
        "",
        (
            "| Entity | Regime | Gold misses | Projection | Candidate-source | "
            "Proj. share | Phrase | Attr bundle | CUI proj | Over-emit |"
        ),
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for entity in ledger["scored_entities"]:
        entry = summary["per_entity"][entity]
        families = entry["gap_families"]
        lines.append(
            f"| {entity} | {entry['regime']} | {entry['gold_misses']} "
            f"| {entry['projection_misses']} | {entry['candidate_source_misses']} "
            f"| {entry['projection_share']:.4f} | {families[GAP_PHRASE_COVERAGE]} "
            f"| {families[GAP_ATTRIBUTE_BUNDLE]} | {families[GAP_CUI_PROJECTION]} "
            f"| {families[GAP_OVER_EMISSION]} |"
        )

    lines.extend(
        [
            "",
            "## Prescription Component Families",
            "",
            (
                "Prescription benchmark F1 is dominated by phrase altitude, so its "
                "row-level gaps above are read with these clinical component "
                "families (diagnostic; gains here are projection-format, not "
                "medication recovery)."
            ),
            "",
            "| Family | Item F1 | Precision | Recall | TP | FP | FN |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    families = ledger["prescription_component_families"]
    for family in (
        *PRESCRIPTION_COMPONENT_FAMILIES,
        "phrase_scope",
        "drugname_cui_projection",
    ):
        entry = families[family]
        lines.append(
            f"| {family} | {entry['f1']:.4f} | {entry['precision']:.4f} "
            f"| {entry['recall']:.4f} | {entry['tp']} | {entry['fp']} | {entry['fn']} |"
        )

    lines.extend(
        [
            "",
            "## Reading",
            "",
            (
                "Representation-bound entities (high projection share) move on "
                "projection fixes — phrase altitude, casing, attribute/CUI "
                "convention — not lexicon breadth. Recall-bound entities (low "
                "projection share) need real candidate generation (GPT-first or "
                "hybrid). Split/merge and current-regimen errors are visible as "
                "Prescription phrase_coverage and over_emission rows plus the "
                "component table; first-class split/merge instrumentation is "
                "future work."
            ),
            "",
        ]
    )
    return "\n".join(lines)
