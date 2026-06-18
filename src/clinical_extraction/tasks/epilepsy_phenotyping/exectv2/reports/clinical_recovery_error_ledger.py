"""Clinical-recovery error ledger for ExECTv2 key-entity runs.

The projection-gap ledger explains benchmark mention/key failures. This ledger
works one level higher: it records the clinical-recovery keys used by the
objective-aligned headline scores for Prescription, Diagnosis, SeizureFrequency,
and Investigations. It is intended for prompt/error-analysis loops over existing
prediction artifacts, not for changing scoring policy.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Hashable, Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
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
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    ClinicalRecoveryPRF1,
    normalize_phrase,
    score_concept_identity,
    score_frequency_state,
    score_investigations_components,
    score_prescription_components,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    _concept_keys as concept_keys,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    _frequency_state_keys as frequency_state_keys,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    _investigation_component_keys as investigation_component_keys,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    _prescription_component_key as prescription_component_key,
)

KEY_ENTITIES: tuple[str, ...] = (
    PRESCRIPTION.name,
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY.name,
    INVESTIGATIONS.name,
)
DEFAULT_REGISTRY_PATH = Path("experiments/registry.jsonl")


@dataclass(frozen=True)
class ClinicalRecoveryErrorRecord:
    letter_id: str
    entity: str
    side: Literal["gold", "predicted"]
    key: str
    count: int
    example_text: str
    example_attributes: dict[str, str]
    evidence: str
    note_excerpt: str


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def build_combined_predictions_from_rows(
    gold_letters: Sequence[ExectLetter],
    structured_rows: Sequence[Mapping[str, Any]],
    *,
    diagnosis_rows: Sequence[Mapping[str, Any]] | None = None,
    sf_rows: Sequence[Mapping[str, Any]] | None = None,
    investigations_rows: Sequence[Mapping[str, Any]] | None = None,
) -> list[PredictedLetter]:
    """Combine best current family outputs into one prediction object per letter."""

    structured_by_id = _rows_by_id(structured_rows)
    diagnosis_by_id = _rows_by_id(diagnosis_rows or ())
    sf_by_id = _rows_by_id(sf_rows or ())
    investigations_by_id = _rows_by_id(investigations_rows or ())
    predictions: list[PredictedLetter] = []

    for letter in gold_letters:
        structured = structured_by_id.get(letter.letter_id, {})
        diagnosis = diagnosis_by_id.get(letter.letter_id, structured)
        sf = sf_by_id.get(letter.letter_id, structured)
        investigations = investigations_by_id.get(letter.letter_id, structured)
        mentions = [
            *_mentions_from_row(
                structured,
                allowed_entities={PRESCRIPTION.name},
            ),
            *_mentions_from_row(investigations, allowed_entities={INVESTIGATIONS.name}),
            *_mentions_from_row(diagnosis, allowed_entities={DIAGNOSIS.name}),
            *_mentions_from_row(sf, allowed_entities={SEIZURE_FREQUENCY.name}),
        ]
        predictions.append(
            PredictedLetter(
                letter_id=letter.letter_id,
                mentions=tuple(mentions),
                diagnostics={
                    "structured_source": str(structured.get("pipeline_family", "")),
                    "diagnosis_source": str(diagnosis.get("pipeline_family", "")),
                    "sf_source": str(sf.get("pipeline_family", "")),
                    "investigations_source": str(
                        investigations.get("pipeline_family", "")
                    ),
                },
            )
        )
    return predictions


def build_error_ledger(
    gold_letters: Sequence[ExectLetter],
    predictions: Sequence[PredictedLetter],
    *,
    entities: Sequence[str] = KEY_ENTITIES,
) -> dict[str, Any]:
    pred_letters = [
        to_exect_letter(prediction, note_text=gold.note_text)
        for prediction, gold in zip(predictions, gold_letters, strict=True)
    ]
    records: list[ClinicalRecoveryErrorRecord] = []
    summary: dict[str, Any] = {}
    for entity in entities:
        entity_records = _entity_error_records(gold_letters, pred_letters, entity)
        records.extend(entity_records)
        summary[entity] = {
            "headline": _score_to_dict(_headline_score(gold_letters, pred_letters, entity)),
            "top_gold_misses": _top_records(entity_records, "gold"),
            "top_predicted_over_emissions": _top_records(entity_records, "predicted"),
        }
    return {
        "row_count": len(gold_letters),
        "entities": list(entities),
        "summary": {"per_entity": summary},
        "records": [asdict(record) for record in records],
    }


def write_error_ledger_artifacts(
    *,
    structured_jsonl: Path,
    out_json: Path,
    out_md: Path,
    diagnosis_jsonl: Path | None = None,
    sf_jsonl: Path | None = None,
    investigations_jsonl: Path | None = None,
    split: str = "dev",
    generated_on: str | None = None,
) -> tuple[Path, Path]:
    generated_on = generated_on or date.today().isoformat()
    structured_rows = read_jsonl(structured_jsonl)
    ids = [str(row["letter_id"]) for row in structured_rows]
    gold_by_id = {letter.letter_id: letter for letter in load_letters_for_split(split)}
    gold_letters = [gold_by_id[letter_id] for letter_id in ids]
    predictions = build_combined_predictions_from_rows(
        gold_letters,
        structured_rows,
        diagnosis_rows=read_jsonl(diagnosis_jsonl) if diagnosis_jsonl else None,
        sf_rows=read_jsonl(sf_jsonl) if sf_jsonl else None,
        investigations_rows=(
            read_jsonl(investigations_jsonl) if investigations_jsonl else None
        ),
    )
    ledger = build_error_ledger(gold_letters, predictions)
    ledger.update(
        {
            "generated_on": generated_on,
            "split": split,
            "structured_jsonl": str(structured_jsonl),
            "diagnosis_jsonl": str(diagnosis_jsonl) if diagnosis_jsonl else None,
            "sf_jsonl": str(sf_jsonl) if sf_jsonl else None,
            "investigations_jsonl": (
                str(investigations_jsonl) if investigations_jsonl else None
            ),
        }
    )

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(_render_markdown(ledger, json_path=out_json), encoding="utf-8")
    return out_json, out_md


def _rows_by_id(rows: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    return {str(row["letter_id"]): row for row in rows}


def _mentions_from_row(
    row: Mapping[str, Any],
    *,
    allowed_entities: set[str],
) -> list[PredictedMention]:
    mentions: list[PredictedMention] = []
    for raw in row.get("predicted_mentions", []):
        entity = str(raw.get("entity", ""))
        if entity not in allowed_entities:
            continue
        mentions.append(
            PredictedMention(
                entity=entity,
                text=str(raw.get("text", "")),
                attributes={
                    str(k): str(v)
                    for k, v in dict(raw.get("attributes") or {}).items()
                    if v is not None
                },
                evidence=str(raw.get("evidence", "")),
                confidence=_confidence(raw.get("confidence")),
                rationale=str(raw.get("rationale", "")),
                component_owner=str(raw.get("component_owner", "")),
            )
        )
    return mentions


def _confidence(value: Any) -> Literal["low", "medium", "high"] | None:
    return value if value in {"low", "medium", "high"} else None


def _headline_score(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    entity: str,
) -> Any:
    if entity == PRESCRIPTION.name:
        return score_prescription_components(gold_letters, pred_letters).clinical_headline
    if entity == INVESTIGATIONS.name:
        return score_investigations_components(gold_letters, pred_letters).clinical_headline
    if entity == SEIZURE_FREQUENCY.name:
        return score_frequency_state(gold_letters, pred_letters).clinical_headline
    if entity == DIAGNOSIS.name:
        return score_concept_identity(gold_letters, pred_letters, entity).concept_assertion
    raise ValueError(f"Unsupported clinical-recovery entity {entity!r}")


def _entity_error_records(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    entity: str,
) -> list[ClinicalRecoveryErrorRecord]:
    pred_by_id = {letter.letter_id: letter for letter in pred_letters}
    records: list[ClinicalRecoveryErrorRecord] = []
    for gold_letter in gold_letters:
        pred_letter = pred_by_id[gold_letter.letter_id]
        gold_items = _clinical_key_items(gold_letter, gold_letter, entity, side="gold")
        pred_precision_items = _clinical_key_items(
            pred_letter,
            gold_letter,
            entity,
            side="predicted",
            home_only=True,
        )
        pred_recall_items = _clinical_key_items(
            pred_letter,
            gold_letter,
            entity,
            side="predicted",
            home_only=False,
        )

        gold_counter = Counter(item[0] for item in gold_items)
        pred_precision_counter = Counter(item[0] for item in pred_precision_items)
        pred_recall_counter = Counter(item[0] for item in pred_recall_items)

        for key, count in (gold_counter - (gold_counter & pred_recall_counter)).items():
            records.append(
                _record_from_item(
                    gold_letter.letter_id,
                    entity,
                    "gold",
                    key,
                    count,
                    _first_item(gold_items, key),
                    gold_letter.note_text,
                )
            )
        for key, count in (
            pred_precision_counter - (gold_counter & pred_precision_counter)
        ).items():
            records.append(
                _record_from_item(
                    gold_letter.letter_id,
                    entity,
                    "predicted",
                    key,
                    count,
                    _first_item(pred_precision_items, key),
                    gold_letter.note_text,
                )
            )
    return records


ClinicalKeyItem = tuple[Hashable, ExectAnnotation]


def _clinical_key_items(
    letter: ExectLetter,
    source_letter: ExectLetter,
    entity: str,
    *,
    side: Literal["gold", "predicted"],
    home_only: bool = True,
) -> list[ClinicalKeyItem]:
    if entity == PRESCRIPTION.name:
        return [
            (key, ann)
            for ann in letter.entities(PRESCRIPTION.name)
            if (
                key := prescription_component_key(
                    ann,
                    "clinical_headline",
                    source_letter.note_text,
                )
            )
            is not None
        ]
    if entity == INVESTIGATIONS.name:
        return [
            (key, ann)
            for ann in letter.entities(INVESTIGATIONS.name)
            for key in investigation_component_keys((ann,), "clinical_headline")
        ]
    if entity == SEIZURE_FREQUENCY.name:
        return [
            (key, ann)
            for ann in letter.entities(SEIZURE_FREQUENCY.name)
            for key in frequency_state_keys((ann,), "clinical_headline")
        ]
    if entity == DIAGNOSIS.name:
        annotations: Iterable[ExectAnnotation]
        annotations = letter.entities(DIAGNOSIS.name) if home_only else letter.annotations
        if side == "gold":
            annotations = letter.entities(DIAGNOSIS.name)
        return [
            (key, ann)
            for ann in annotations
            for key in concept_keys((ann,), DIAGNOSIS.name, "assertion")
        ]
    raise ValueError(f"Unsupported clinical-recovery entity {entity!r}")


def _first_item(items: Sequence[ClinicalKeyItem], key: Hashable) -> ClinicalKeyItem:
    for item in items:
        if item[0] == key:
            return item
    raise ValueError(f"Missing example item for key {key!r}")


def _record_from_item(
    letter_id: str,
    entity: str,
    side: Literal["gold", "predicted"],
    key: Hashable,
    count: int,
    item: ClinicalKeyItem,
    note_text: str,
) -> ClinicalRecoveryErrorRecord:
    _, annotation = item
    evidence = annotation.raw_text or annotation.text
    return ClinicalRecoveryErrorRecord(
        letter_id=letter_id,
        entity=entity,
        side=side,
        key=_key_to_string(key),
        count=count,
        example_text=annotation.text,
        example_attributes=dict(annotation.attributes),
        evidence=evidence,
        note_excerpt=_excerpt(note_text, evidence or annotation.text),
    )


def _key_to_string(key: Hashable) -> str:
    return json.dumps(_jsonable_key(key), sort_keys=True, ensure_ascii=False)


def _jsonable_key(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable_key(item) for item in value]
    if isinstance(value, list):
        return [_jsonable_key(item) for item in value]
    if isinstance(value, dict):
        return {str(k): _jsonable_key(v) for k, v in value.items()}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _excerpt(note_text: str, evidence: str, *, radius: int = 140) -> str:
    if not note_text or not evidence:
        return ""
    index = note_text.lower().find(evidence.lower())
    if index == -1:
        phrase = normalize_phrase(evidence)
        normalized_note = normalize_phrase(note_text)
        index = normalized_note.find(phrase)
        if index == -1:
            return ""
    start = max(0, index - radius)
    end = min(len(note_text), index + len(evidence) + radius)
    return " ".join(note_text[start:end].split())


def _top_records(
    records: Sequence[ClinicalRecoveryErrorRecord],
    side: Literal["gold", "predicted"],
    *,
    limit: int = 15,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[ClinicalRecoveryErrorRecord]] = defaultdict(list)
    for record in records:
        if record.side == side:
            grouped[record.key].append(record)
    rows: list[dict[str, Any]] = []
    for key, bucket in grouped.items():
        total = sum(record.count for record in bucket)
        example = bucket[0]
        rows.append(
            {
                "key": key,
                "count": total,
                "letters": sorted({record.letter_id for record in bucket}),
                "example_text": example.example_text,
                "example_attributes": example.example_attributes,
                "example_evidence": example.evidence,
                "example_excerpt": example.note_excerpt,
            }
        )
    return sorted(rows, key=lambda row: (-int(row["count"]), str(row["key"])))[:limit]


def _score_to_dict(score: Any) -> dict[str, Any]:
    if isinstance(score, ClinicalRecoveryPRF1):
        return {
            "precision": round(score.precision, 4),
            "recall": round(score.recall, 4),
            "f1": round(score.f1, 4),
            "tp": score.tp,
            "precision_tp": score.precision_tp,
            "recall_tp": score.recall_tp,
            "fp": score.fp,
            "fn": score.fn,
            "pred_count": score.pred_count,
            "gold_count": score.gold_count,
        }
    return {
        "precision": round(score.precision, 4),
        "recall": round(score.recall, 4),
        "f1": round(score.f1, 4),
        "tp": score.tp,
        "fp": score.fp,
        "fn": score.fn,
        "pred_count": score.tp + score.fp,
        "gold_count": score.tp + score.fn,
    }


def _render_markdown(ledger: Mapping[str, Any], *, json_path: Path) -> str:
    lines = [
        "# ExECTv2 Clinical-Recovery Error Ledger",
        "",
        f"- Generated: `{ledger['generated_on']}`",
        f"- JSON: `{json_path}`",
        f"- Split: `{ledger['split']}`",
        f"- Letters: {ledger['row_count']}",
        f"- Structured JSONL: `{ledger['structured_jsonl']}`",
        f"- Diagnosis JSONL: `{ledger.get('diagnosis_jsonl')}`",
        f"- SeizureFrequency JSONL: `{ledger.get('sf_jsonl')}`",
        f"- Investigations JSONL: `{ledger.get('investigations_jsonl')}`",
        "",
        "## Headline Scores",
        "",
        "| Entity | F1 | P | R | TP | FP | FN |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for entity in ledger["entities"]:
        score = ledger["summary"]["per_entity"][entity]["headline"]
        lines.append(
            f"| {entity} | {score['f1']:.3f} | {score['precision']:.3f} "
            f"| {score['recall']:.3f} | {score['tp']} | {score['fp']} | {score['fn']} |"
        )

    for entity in ledger["entities"]:
        entry = ledger["summary"]["per_entity"][entity]
        lines.extend(["", f"## {entity}", "", "### Top Gold Misses", ""])
        lines.extend(_top_table(entry["top_gold_misses"]))
        lines.extend(["", "### Top Predicted Over-Emissions", ""])
        lines.extend(_top_table(entry["top_predicted_over_emissions"]))
    lines.append("")
    return "\n".join(lines)


def _top_table(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    lines = [
        "| Count | Key | Example | Letters |",
        "| ---: | --- | --- | --- |",
    ]
    if not rows:
        lines.append("| 0 |  |  |  |")
        return lines
    for row in rows:
        example = str(row["example_text"]).replace("|", "\\|")
        key = str(row["key"]).replace("|", "\\|")
        letters = ", ".join(str(letter) for letter in row["letters"][:8])
        if len(row["letters"]) > 8:
            letters += ", ..."
        lines.append(f"| {row['count']} | `{key}` | {example} | {letters} |")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write an ExECTv2 clinical-recovery error ledger for key entities",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--split", default="dev")
    parser.add_argument("--structured-jsonl", type=Path, required=True)
    parser.add_argument("--diagnosis-jsonl", type=Path, default=None)
    parser.add_argument("--sf-jsonl", type=Path, default=None)
    parser.add_argument("--investigations-jsonl", type=Path, default=None)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("experiments/exectv2_key_entities_clinical_error_ledger.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("experiments/exectv2_key_entities_clinical_error_ledger.md"),
    )
    args = parser.parse_args()
    json_path, md_path = write_error_ledger_artifacts(
        structured_jsonl=args.structured_jsonl,
        diagnosis_jsonl=args.diagnosis_jsonl,
        sf_jsonl=args.sf_jsonl,
        investigations_jsonl=args.investigations_jsonl,
        out_json=args.out_json,
        out_md=args.out_md,
        split=args.split,
    )
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
