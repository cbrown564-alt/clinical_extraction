"""ExECTv2 all-entity hybrid — GPT candidate assessment over all nine entities.

The benchmark-beating route of satellite 09 (Phase C). It realizes the winning
Gan ``hybrid_structured_events`` split of labor across the full phenotyping
contract:

```text
raw letter
  -> GPT per-entity candidate generation for every entity (the recall engine)
     [+ deterministic candidates as optional augmentation, never the primary source]
  -> deterministic projection + ontology normalization from selected facts
  -> evidence + plausibility gate (faithful routing, never editing)
  -> combined all-nine PredictedLetter
```

The **LLM owns candidate generation, clinical reasoning, and candidate
selection** — the focused per-entity frame (``llm.llm_only_per_entity``) is the
one strong assessment pass; one focused call per (entity, letter) already merges
generation + reasoning + selection. Deterministic code owns ontology
normalization, CUI projection, the routing gate, and scoring, and may *augment*
(never replace) candidate generation with the deterministic all-9 rules.

This module assembles the nine focused GPT passes into one combined prediction
and scores it overall + per entity. It is **replay-first**: the per-entity GPT
candidates are read from the ``llm_only_per_entity`` JSONL artifacts, so the
combined headline costs zero extra LLM calls. ``run_live`` regenerates the
per-entity candidates first (resumable per entity) and then assembles.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ALL_ENTITIES,
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    extract_deterministic_all9,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    benchmark_config_for,
    score_overall,
    semantic_config_for,
    source_near_diagnostic,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)

from .all_entity_gate import (
    RoutedMention,
    gate_mentions,
    routed_taxonomy,
    routed_taxonomy_by_entity,
)

PROMPT_VERSION = "exectv2_hybrid_all_entities_v0.1"
COMPONENT_OWNER = "hybrid_all_entities"
ENTITY_NAMES: tuple[str, ...] = tuple(spec.name for spec in ALL_ENTITIES)

PUBLISHED_PER_ENTITY_ITEM_F1: dict[str, float] = {
    "BirthHistory": 0.97,
    "Diagnosis": 0.85,
    "EpilepsyCause": 0.90,
    "Investigations": 0.95,
    "Onset": 0.96,
    "PatientHistory": 0.78,
    "Prescription": 0.87,
    "SeizureFrequency": 0.66,
    "WhenDiagnosed": 0.91,
}
PUBLISHED_OVERALL = {"per_item": 0.87, "per_letter": 0.90}


def entity_slug(entity: str) -> str:
    return entity.lower()


# ── Candidate loading (replay of the focused per-entity GPT passes) ────────────


def _mention_from_row(entity: str, row_mention: dict[str, Any]) -> PredictedMention:
    return PredictedMention(
        entity=entity,
        text=str(row_mention.get("text", "")),
        attributes={str(k): str(v) for k, v in (row_mention.get("attributes") or {}).items()},
        evidence=str(row_mention.get("evidence", "")),
        confidence=row_mention.get("confidence") or "medium",
        rationale=str(row_mention.get("rationale", "")),
        component_owner=COMPONENT_OWNER,
    )


def load_candidates_from_per_entity(
    prefix: str,
    *,
    out_dir: Path,
    entities: Sequence[str] = ENTITY_NAMES,
) -> dict[str, list[PredictedMention]]:
    """Read the focused per-entity GPT candidates from their JSONL artifacts.

    Returns ``{letter_id: [PredictedMention, ...]}`` unioned across entities, in
    a deterministic entity order. Missing per-entity files are skipped (the
    combined run simply has no candidates for that entity).
    """
    by_letter: dict[str, list[PredictedMention]] = {}
    for entity in entities:
        path = out_dir / f"{prefix}_{entity_slug(entity)}.jsonl"
        if not path.exists():
            print(f"WARNING: missing per-entity candidates {path}", file=sys.stderr)
            continue
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                letter_id = row.get("letter_id")
                if letter_id is None:
                    continue
                bucket = by_letter.setdefault(letter_id, [])
                for m in row.get("predicted_mentions") or []:
                    bucket.append(_mention_from_row(entity, m))
    return by_letter


def candidates_from_per_entity_rows(
    rows_by_entity: dict[str, Sequence[dict[str, Any]]],
) -> dict[str, list[PredictedMention]]:
    """Assemble candidates from in-memory per-entity run rows (live path)."""
    by_letter: dict[str, list[PredictedMention]] = {}
    for entity in ENTITY_NAMES:
        for row in rows_by_entity.get(entity, ()):
            letter_id = row.get("letter_id")
            if letter_id is None:
                continue
            bucket = by_letter.setdefault(letter_id, [])
            for m in row.get("predicted_mentions") or []:
                bucket.append(_mention_from_row(entity, m))
    return by_letter


# ── Assembly: gate + projection + combine ──────────────────────────────────────


def _rule_augmentation(letter: ExectLetter) -> list[PredictedMention]:
    """Deterministic all-9 candidates as optional augmentation (never primary)."""
    rule_letter = extract_deterministic_all9(letter)
    return [
        PredictedMention(
            entity=m.entity,
            text=m.text,
            attributes=dict(m.attributes),
            evidence=m.evidence,
            confidence=m.confidence,
            rationale=m.rationale,
            component_owner=f"{COMPONENT_OWNER}_rule_augmentation",
        )
        for m in rule_letter.mentions
        if m.entity in ENTITY_NAMES
    ]


def assemble_letter(
    letter: ExectLetter,
    candidates: Sequence[PredictedMention],
    *,
    augment_rules: bool = False,
) -> tuple[PredictedLetter, list[RoutedMention]]:
    """Gate + project the combined candidate set into one all-nine prediction.

    The LLM candidates lead; deterministic rule candidates (when ``augment_rules``
    is set) are appended after them so the gate's duplicate-collapse keeps the LLM
    copy. CUI projection is re-applied so augmented candidates are projected too.
    """
    combined: list[PredictedMention] = list(candidates)
    if augment_rules:
        combined.extend(_rule_augmentation(letter))

    kept, routed = gate_mentions(combined, note_text=letter.note_text)
    predicted = project_cuis(
        PredictedLetter(
            letter_id=letter.letter_id,
            mentions=tuple(kept),
            diagnostics={
                "prompt_version": PROMPT_VERSION,
                "n_candidates": len(combined),
                "n_routed": len(routed),
                "augment_rules": augment_rules,
                "routed_taxonomy": routed_taxonomy(routed),
                "routed_taxonomy_by_entity": routed_taxonomy_by_entity(routed),
            },
        )
    )
    return predicted, routed


# ── Runner (replay) ────────────────────────────────────────────────────────────


def run_replay(
    letters: Sequence[ExectLetter],
    candidates_by_letter: dict[str, list[PredictedMention]],
    *,
    split: str,
    model: str,
    augment_rules: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Assemble + score the combined hybrid from per-entity GPT candidates."""
    rows: list[dict[str, Any]] = []
    for letter in letters:
        candidates = candidates_by_letter.get(letter.letter_id, [])
        predicted, routed = assemble_letter(
            letter, candidates, augment_rules=augment_rules
        )
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "prompt_version": PROMPT_VERSION,
                "model": model,
                "augment_rules": augment_rules,
                "n_candidates": len(candidates) + (
                    len(_rule_augmentation(letter)) if augment_rules else 0
                ),
                "n_mentions_scored": len(predicted.mentions),
                "n_routed": len(routed),
                "routed_taxonomy": routed_taxonomy(routed),
                "routed_taxonomy_by_entity": routed_taxonomy_by_entity(routed),
                "predicted_mentions": [_mention_to_row(m) for m in predicted.mentions],
                "routed_mentions": [
                    {"entity": r.mention.entity, "text": r.mention.text, "reason": r.reason}
                    for r in routed
                ],
                "gold_mentions": [
                    {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
                    for a in letter.annotations
                    if a.entity in set(ENTITY_NAMES)
                ],
            }
        )
    metadata = {
        "prompt_version": PROMPT_VERSION,
        "model": model,
        "split": split,
        "augment_rules": augment_rules,
        "n_letters": len(letters),
    }
    metadata["summary"] = summarize_rows(rows)
    return rows, metadata


def _mention_to_row(mention: PredictedMention) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "confidence": mention.confidence,
        "rationale": mention.rationale,
        "component_owner": mention.component_owner,
    }


# ── Scoring / summary ──────────────────────────────────────────────────────────


def summarize_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Overall + per-entity scorecard with routing and projection diagnostics."""
    n = len(rows)
    if n == 0:
        return {"examples": 0}

    gold_letters = _reconstruct_letters(rows, key="gold_mentions")
    pred_letters = _reconstruct_letters(rows, key="predicted_mentions")

    phrase = score_overall(gold_letters, pred_letters, ENTITY_NAMES, lambda _e: PHRASE_ONLY)
    semantic = score_overall(gold_letters, pred_letters, ENTITY_NAMES, semantic_config_for)
    benchmark = score_overall(gold_letters, pred_letters, ENTITY_NAMES, benchmark_config_for)
    source_near = source_near_diagnostic(
        gold_letters, pred_letters, ENTITY_NAMES, semantic_config_for
    )

    routed_tax: dict[str, int] = {}
    routed_by_entity: dict[str, dict[str, int]] = {}
    for r in rows:
        for reason, count in (r.get("routed_taxonomy") or {}).items():
            routed_tax[reason] = routed_tax.get(reason, 0) + int(count)
        for entity, reasons in (r.get("routed_taxonomy_by_entity") or {}).items():
            bucket = routed_by_entity.setdefault(entity, {})
            for reason, count in reasons.items():
                bucket[reason] = bucket.get(reason, 0) + int(count)

    return {
        "examples": n,
        "n_candidates": sum(int(r.get("n_candidates", 0)) for r in rows),
        "n_mentions_scored": sum(int(r.get("n_mentions_scored", 0)) for r in rows),
        "n_routed": sum(int(r.get("n_routed", 0)) for r in rows),
        "routed_taxonomy": routed_tax,
        "routed_taxonomy_by_entity": routed_by_entity,
        "scores": {
            "phrase_only": _overall_to_dict(phrase),
            "semantic": _overall_to_dict(semantic),
            "benchmark": _overall_to_dict(benchmark),
        },
        "projection_ablation": _projection_ablation(semantic, benchmark),
        "diagnostic_ladder": {"source_near": _source_near_to_dict(source_near)},
        "published_targets": {
            "overall": PUBLISHED_OVERALL,
            "per_entity_per_item": PUBLISHED_PER_ENTITY_ITEM_F1,
        },
    }


def _projection_ablation(semantic: Any, benchmark: Any) -> dict[str, Any]:
    """Per-entity semantic (CUI-dropped) vs benchmark (with-CUI) item F1 gap.

    This is the Phase D read: how much the deterministic CUI projection moves the
    benchmark-comparable headline above the CUI-dropped clinical layer. A positive
    delta is projection credit; it is never LLM clinical-reasoning credit.
    """
    overall = {
        "semantic_item_f1": round(semantic.per_item.f1, 4),
        "benchmark_item_f1": round(benchmark.per_item.f1, 4),
        "delta_item_f1": round(benchmark.per_item.f1 - semantic.per_item.f1, 4),
    }
    per_entity = {}
    for entity in ENTITY_NAMES:
        sem = semantic.per_entity[entity].per_item
        bench = benchmark.per_entity[entity].per_item
        per_entity[entity] = {
            "semantic_item_f1": round(sem.f1, 4),
            "benchmark_item_f1": round(bench.f1, 4),
            "delta_item_f1": round(bench.f1 - sem.f1, 4),
        }
    return {"overall": overall, "per_entity": per_entity}


def _overall_to_dict(score: Any) -> dict[str, Any]:
    return {
        "per_item": _prf1_to_dict(score.per_item),
        "per_letter": _prf1_to_dict(score.per_letter),
        "per_entity": {
            entity: {
                "per_item": _prf1_to_dict(entity_score.per_item),
                "per_letter": _prf1_to_dict(entity_score.per_letter),
                "published_per_item_target": PUBLISHED_PER_ENTITY_ITEM_F1.get(entity),
            }
            for entity, entity_score in score.per_entity.items()
        },
    }


def _source_near_to_dict(diagnostic: Any) -> dict[str, Any]:
    return {
        "overall": {
            "overlap": _prf1_to_dict(diagnostic.overall.overlap),
            "attribute_agreement_rate": round(diagnostic.overall.attribute_agreement_rate, 4),
        },
        "per_entity": {
            entity: {
                "overlap": _prf1_to_dict(entity_score.overlap),
                "attribute_agreement_rate": round(entity_score.attribute_agreement_rate, 4),
            }
            for entity, entity_score in diagnostic.per_entity.items()
        },
    }


def _prf1_to_dict(score: Any) -> dict[str, Any]:
    return {
        "precision": round(score.precision, 4),
        "recall": round(score.recall, 4),
        "f1": round(score.f1, 4),
        "tp": score.tp,
        "fp": score.fp,
        "fn": score.fn,
    }


def _reconstruct_letters(rows: Sequence[dict[str, Any]], *, key: str) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        annotations = tuple(
            ExectAnnotation(
                entity=str(m["entity"]),
                text=str(m["text"]),
                attributes={str(k): str(v) for k, v in dict(m.get("attributes") or {}).items()},
            )
            for m in (row.get(key) or [])
        )
        if key == "predicted_mentions":
            pred = PredictedLetter(
                letter_id=row["letter_id"],
                mentions=tuple(
                    PredictedMention(
                        entity=a.entity,
                        text=a.text,
                        attributes=dict(a.attributes),
                        evidence="",
                    )
                    for a in annotations
                ),
            )
            letters.append(to_exect_letter(pred))
        else:
            letters.append(
                ExectLetter(letter_id=row["letter_id"], note_text="", annotations=annotations)
            )
    return letters


# ── I/O ────────────────────────────────────────────────────────────────────────


def write_jsonl(rows: Sequence[dict[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: dict[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary") or summarize_rows(rows)
    scores = summary.get("scores", {})
    lines = [
        "# ExECTv2 Hybrid — All Entities (GPT candidates + deterministic projection)",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Prompt version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- Split: `{metadata.get('split')}`",
        f"- Model (candidate source): `{metadata.get('model')}`",
        f"- Rule augmentation: `{metadata.get('augment_rules', False)}`",
        f"- Letters: {summary.get('examples', 0)}",
        "",
        "## Gate & routing",
        "",
        f"- Candidates offered: {summary.get('n_candidates', 0)}",
        f"- Mentions scored (post gate): {summary.get('n_mentions_scored', 0)}",
        f"- Routed (excluded): {summary.get('n_routed', 0)}",
        f"- Routed taxonomy: {summary.get('routed_taxonomy', {})}",
        "",
        "## Overall scores",
        "",
        "| Layer | Item P | Item R | Item F1 | Letter P | Letter R | Letter F1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for config_name in ("phrase_only", "semantic", "benchmark"):
        s = scores.get(config_name, {})
        pi = s.get("per_item", {})
        pl = s.get("per_letter", {})
        lines.append(
            f"| {config_name} | {pi.get('precision', 0):.3f} | {pi.get('recall', 0):.3f} "
            f"| {pi.get('f1', 0):.3f} | {pl.get('precision', 0):.3f} "
            f"| {pl.get('recall', 0):.3f} | {pl.get('f1', 0):.3f} |"
        )
    lines.extend([
        "",
        f"Published targets: overall per-item {PUBLISHED_OVERALL['per_item']:.2f} / "
        f"per-letter {PUBLISHED_OVERALL['per_letter']:.2f}.",
        "",
        "## Per-entity (semantic, CUI-dropped) + projection ablation",
        "",
        "| Entity | Pub item F1 | Semantic item F1 | Benchmark item F1 | "
        "Δ (CUI projection) | SN recall | Routed |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    semantic_entities = scores.get("semantic", {}).get("per_entity", {})
    ablation = summary.get("projection_ablation", {}).get("per_entity", {})
    sn_entities = (
        summary.get("diagnostic_ladder", {}).get("source_near", {}).get("per_entity", {})
    )
    routed_by_entity = summary.get("routed_taxonomy_by_entity", {})
    for entity in ENTITY_NAMES:
        sem = semantic_entities.get(entity, {}).get("per_item", {})
        abl = ablation.get(entity, {})
        sn = sn_entities.get(entity, {}).get("overlap", {})
        routed_n = sum((routed_by_entity.get(entity, {}) or {}).values())
        target = PUBLISHED_PER_ENTITY_ITEM_F1.get(entity, 0.0)
        lines.append(
            f"| {entity} | {target:.2f} | {sem.get('f1', 0):.3f} "
            f"| {abl.get('benchmark_item_f1', 0):.3f} | {abl.get('delta_item_f1', 0):+.3f} "
            f"| {sn.get('recall', 0):.3f} | {routed_n} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
