"""Score Compact versus Full ledger comparison for the paper runner."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.views import (
    predictions_from_rows,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    has_blocking_parse_issue,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    clinical_headline_unit_keys,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")
HEADLINE_DROP_LIMIT = 0.05
FAMILY_DROP_LIMIT = 0.08
NET_LOSS_LIMIT = 3


def _letters() -> list[ExectLetter]:
    letters = list(load_letters_for_split("dev"))
    letters.sort(key=lambda item: item.letter_id)
    if len(letters) != 140:
        raise RuntimeError(f"expected 140 loadable development letters, found {len(letters)}")
    return letters


def _existing_complete_rows(path: Path, prompt_version: str) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in load_jsonl_rows(path):
        letter_id = str(row.get("letter_id") or "")
        if not letter_id or letter_id in seen:
            continue
        if row.get("prompt_version") != prompt_version:
            raise RuntimeError(
                f"{path} has {letter_id} with {row.get('prompt_version')}"
            )
        if row.get("call_error") or not row.get("raw_output"):
            continue
        seen.add(letter_id)
        rows.append(row)
    return rows


def _assembly_row(row: Mapping[str, Any], prompt_version: str, call_mode: str) -> dict[str, Any]:
    return {
        "letter_id": row["letter_id"],
        "prompt_version": prompt_version,
        "call_mode": call_mode,
        "predicted_mentions": list(row.get("predicted_mentions") or []),
        "policy": row.get("policy") or {},
    }


def _score_arm(
    *,
    slug: str,
    prompt_version: str,
    call_mode: str,
    new_model_calls: int,
    letters: Sequence[ExectLetter],
    structured_path: Path,
    assembly_path: Path,
    model: str,
) -> dict[str, Any]:
    structured_rows = load_jsonl_rows(structured_path)
    if len(structured_rows) != len(letters):
        raise RuntimeError(
            f"{slug} structured file has {len(structured_rows)} rows, expected {len(letters)}"
        )
    letter_rows = _letter_family_rows(
        gold=letters,
        structured_path=structured_path,
        assembly_path=assembly_path,
        prompt_version=prompt_version,
        arm=slug,
        call_mode=call_mode,
        model=model,
    )
    write_jsonl_rows(letter_rows, structured_path.parent / "letter_family.jsonl")
    metrics = _letter_metrics(
        letters, letter_rows, structured_rows, slug, prompt_version, call_mode
    )
    write_jsonl_rows(metrics, structured_path.parent / "letter_metrics.jsonl")
    raw_prf = _surface_prf(letter_rows, "raw_keys")
    hybrid_prf = _surface_prf(letter_rows, "hybrid_keys")
    quality = _quality_counts(structured_rows)
    summary = {
        "prompt_version": prompt_version,
        "call_mode": call_mode,
        "new_model_calls": new_model_calls,
        "assembly_headline_f1": hybrid_prf["overall"]["f1"],
        "assembly_family_f1": {
            family: hybrid_prf["by_family"][family]["f1"] for family in FAMILIES
        },
        "raw_headline_f1": raw_prf["overall"]["f1"],
        "raw_family_f1": {family: raw_prf["by_family"][family]["f1"] for family in FAMILIES},
        "hybrid_headline_f1": hybrid_prf["overall"]["f1"],
        "hybrid_family_f1": {
            family: hybrid_prf["by_family"][family]["f1"] for family in FAMILIES
        },
        "raw_headline_prf": raw_prf["overall"],
        "raw_family_prf": raw_prf["by_family"],
        "hybrid_headline_prf": hybrid_prf["overall"],
        "hybrid_family_prf": hybrid_prf["by_family"],
        "raw_four_family_letter_exact": _four_family_exact(letter_rows, "raw_letter_exact"),
        "hybrid_four_family_letter_exact": _four_family_exact(
            letter_rows, "hybrid_letter_exact"
        ),
        "raw_family_letter_exact": _family_exact(letter_rows, "raw_letter_exact"),
        "hybrid_family_letter_exact": _family_exact(letter_rows, "hybrid_letter_exact"),
        "hybrid_rewrite_letters": sorted(
            {row["letter_id"] for row in letter_rows if row["hybrid_rewrote"]}
        ),
        "quality": quality,
        "raw_mention_count": sum(int(row.get("n_mentions_raw") or 0) for row in structured_rows),
        "scored_mention_count": sum(
            int(row.get("n_mentions_scored") or 0) for row in structured_rows
        ),
        "gate_event_count": sum(len(row.get("gate_warnings") or []) for row in structured_rows),
    }
    return {"summary": summary, "letter_rows": letter_rows, "metrics": metrics}


def _letter_family_rows(
    *,
    gold: Sequence[ExectLetter],
    structured_path: Path,
    assembly_path: Path,
    prompt_version: str,
    arm: str,
    call_mode: str,
    model: str,
) -> list[dict[str, Any]]:
    structured_rows = {
        str(row["letter_id"]): row for row in load_jsonl_rows(structured_path)
    }
    assembly_rows = {str(row["letter_id"]): row for row in load_jsonl_rows(assembly_path)}
    raw_letters = {
        prediction.letter_id: to_exect_letter(prediction)
        for prediction in predictions_from_rows(
            list(structured_rows.values()), "predicted_mentions"
        )
    }
    hybrid_letters = {
        prediction.letter_id: to_exect_letter(prediction)
        for prediction in predictions_from_rows(
            list(assembly_rows.values()), "predicted_mentions"
        )
    }
    out: list[dict[str, Any]] = []
    for letter in gold:
        for family in FAMILIES:
            raw_mentions = [
                mention
                for mention in raw_letters[letter.letter_id].annotations
                if mention.entity == family
            ]
            hybrid_mentions = [
                mention
                for mention in hybrid_letters[letter.letter_id].annotations
                if mention.entity == family
            ]
            gold_mentions = [
                annotation
                for annotation in letter.annotations
                if annotation.entity == family
            ]
            raw_keys = Counter(
                clinical_headline_unit_keys(family, raw_mentions, letter.note_text)
            )
            hybrid_keys = Counter(
                clinical_headline_unit_keys(family, hybrid_mentions, letter.note_text)
            )
            gold_keys = Counter(
                clinical_headline_unit_keys(family, gold_mentions, letter.note_text)
            )
            out.append(
                {
                    "arm": arm,
                    "prompt_version": prompt_version,
                    "letter_id": letter.letter_id,
                    "family": family,
                    "raw_mention_count": len(raw_mentions),
                    "hybrid_mention_count": len(hybrid_mentions),
                    "gold_mention_count": len(gold_mentions),
                    "raw_letter_exact": raw_keys == gold_keys,
                    "hybrid_letter_exact": hybrid_keys == gold_keys,
                    "hybrid_rewrote": raw_keys != hybrid_keys,
                    "empty_gold": len(gold_keys) == 0,
                    "raw_keys": _counter_rows(raw_keys),
                    "hybrid_keys": _counter_rows(hybrid_keys),
                    "gold_keys": _counter_rows(gold_keys),
                    "model": model,
                    "repair_policy": "default/default",
                    "replay_mode": call_mode,
                }
            )
    return out


def _letter_metrics(
    letters: Sequence[ExectLetter],
    letter_rows: Sequence[Mapping[str, Any]],
    structured_rows: Sequence[Mapping[str, Any]],
    slug: str,
    prompt_version: str,
    call_mode: str,
) -> list[dict[str, Any]]:
    by_letter: dict[str, list[Mapping[str, Any]]] = {}
    for row in letter_rows:
        by_letter.setdefault(str(row["letter_id"]), []).append(row)
    structured_by_id = {str(row["letter_id"]): row for row in structured_rows}
    out: list[dict[str, Any]] = []
    for letter in letters:
        family_rows = by_letter[letter.letter_id]
        structured_row = structured_by_id[letter.letter_id]
        raw = _prf_from_family_rows(family_rows, "raw_keys")
        hybrid = _prf_from_family_rows(family_rows, "hybrid_keys")
        out.append(
            {
                "arm": slug,
                "prompt_version": prompt_version,
                "replay_mode": call_mode,
                "letter_id": letter.letter_id,
                "raw_headline_prf": raw,
                "hybrid_headline_prf": hybrid,
                "raw_four_family_letter_exact": all(
                    bool(row["raw_letter_exact"]) for row in family_rows
                ),
                "hybrid_four_family_letter_exact": all(
                    bool(row["hybrid_letter_exact"]) for row in family_rows
                ),
                "family_letter_exact": {
                    str(row["family"]): {
                        "raw": bool(row["raw_letter_exact"]),
                        "hybrid": bool(row["hybrid_letter_exact"]),
                    }
                    for row in family_rows
                },
                "quality": _quality_counts([structured_row]),
            }
        )
    return out


def _compare_pair(
    control: Mapping[str, Any],
    candidate: Mapping[str, Any],
    letters: Sequence[ExectLetter],
) -> dict[str, Any]:
    ctrl = control["summary"]
    cand = candidate["summary"]
    control_rows = {(row["letter_id"], row["family"]): row for row in control["letter_rows"]}
    candidate_rows = {
        (row["letter_id"], row["family"]): row for row in candidate["letter_rows"]
    }
    surfaces: dict[str, Any] = {}
    triggers: list[str] = []
    for surface, f1_field, exact_field, family_f1_field in (
        ("raw", "raw_headline_f1", "raw_letter_exact", "raw_family_f1"),
        ("hybrid", "hybrid_headline_f1", "hybrid_letter_exact", "hybrid_family_f1"),
    ):
        delta_f1 = round(cand[f1_field] - ctrl[f1_field], 4)
        family_delta = {
            family: round(cand[family_f1_field][family] - ctrl[family_f1_field][family], 4)
            for family in FAMILIES
        }
        wins = 0
        losses = 0
        per_family_flip: dict[str, dict[str, int]] = {}
        for letter in letters:
            control_all = True
            candidate_all = True
            for family in FAMILIES:
                c_ok = bool(control_rows[(letter.letter_id, family)][exact_field])
                n_ok = bool(candidate_rows[(letter.letter_id, family)][exact_field])
                control_all = control_all and c_ok
                candidate_all = candidate_all and n_ok
                flips = per_family_flip.setdefault(family, {"wins": 0, "losses": 0})
                if n_ok and not c_ok:
                    flips["wins"] += 1
                elif c_ok and not n_ok:
                    flips["losses"] += 1
            if candidate_all and not control_all:
                wins += 1
            elif control_all and not candidate_all:
                losses += 1
        net = wins - losses
        if delta_f1 <= -HEADLINE_DROP_LIMIT:
            triggers.append(f"{surface} four-family F1 drop {delta_f1}")
        for family, delta in family_delta.items():
            if delta <= -FAMILY_DROP_LIMIT:
                triggers.append(f"{surface} {family} F1 drop {delta}")
        if losses - wins >= NET_LOSS_LIMIT:
            triggers.append(f"{surface} net four-family letter-exact losses {losses - wins}")
        surfaces[surface] = {
            "headline_f1_delta": delta_f1,
            "family_f1_delta": family_delta,
            "four_family_letter_exact_wins": wins,
            "four_family_letter_exact_losses": losses,
            "four_family_letter_exact_net": net,
            "per_family_letter_exact_flips": per_family_flip,
        }
    return {
        "surfaces": surfaces,
        "significant_regression": bool(triggers),
        "regression_triggers": triggers,
    }


def _changed_rows(
    control: Mapping[str, Any],
    candidate: Mapping[str, Any],
    letters: Sequence[ExectLetter],
) -> list[dict[str, Any]]:
    control_rows = {(row["letter_id"], row["family"]): row for row in control["letter_rows"]}
    candidate_rows = {
        (row["letter_id"], row["family"]): row for row in candidate["letter_rows"]
    }
    out: list[dict[str, Any]] = []
    for letter in letters:
        control_all = True
        candidate_all = True
        family_direction: dict[str, str] = {}
        for family in FAMILIES:
            c_ok = bool(control_rows[(letter.letter_id, family)]["hybrid_letter_exact"])
            n_ok = bool(candidate_rows[(letter.letter_id, family)]["hybrid_letter_exact"])
            control_all = control_all and c_ok
            candidate_all = candidate_all and n_ok
            if n_ok and not c_ok:
                family_direction[family] = "win"
            elif c_ok and not n_ok:
                family_direction[family] = "loss"
            else:
                family_direction[family] = "same"
        if candidate_all and not control_all:
            direction = "win"
        elif control_all and not candidate_all:
            direction = "loss"
        else:
            direction = "same"
        if direction == "same" and all(value == "same" for value in family_direction.values()):
            continue
        out.append(
            {
                "letter_id": letter.letter_id,
                "four_family_exact_direction": direction,
                "family_exact_direction": family_direction,
            }
        )
    return out


def _quality_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    schema = 0
    parse = 0
    illegal_enum = 0
    inexact = 0
    for row in rows:
        errors = [str(item) for item in (row.get("parse_errors") or [])]
        initial = [str(item) for item in (row.get("initial_parse_errors") or [])]
        warnings = [str(item) for item in (row.get("gate_warnings") or [])]
        if any(item.startswith("schema_validation_error:") for item in [*errors, *initial]):
            schema += 1
        if any(item.startswith("invalid_json:") for item in [*errors, *initial]):
            parse += 1
        if has_blocking_parse_issue(errors) and not (
            any(item.startswith("schema_validation_error:") for item in errors)
            or any(item.startswith("invalid_json:") for item in errors)
        ):
            schema += 1
        illegal_enum += sum(1 for item in warnings if "dropped_illegal_value:" in item)
        inexact += int(row.get("n_evidence_invalid") or 0)
        if not row.get("n_evidence_invalid"):
            inexact += sum(
                1
                for item in warnings
                if item.startswith("dropped_evidence_not_substring:")
                or item.startswith("dropped_empty_evidence:")
            )
    return {
        "schema": schema,
        "parse": parse,
        "illegal_enum": illegal_enum,
        "inexact_evidence": inexact,
    }


def _surface_prf(letter_rows: Sequence[Mapping[str, Any]], key_field: str) -> dict[str, Any]:
    by_family: dict[str, dict[str, float]] = {}
    overall: Counter[str] = Counter()
    for family in FAMILIES:
        counts: Counter[str] = Counter()
        for row in letter_rows:
            if row["family"] != family:
                continue
            gold = _counter_from_rows(row["gold_keys"])
            pred = _counter_from_rows(row[key_field])
            counts += _prf_counts(gold, pred)
        overall += counts
        by_family[family] = _prf(counts)
    return {"overall": _prf(overall), "by_family": by_family}


def _prf_from_family_rows(
    family_rows: Sequence[Mapping[str, Any]], key_field: str
) -> dict[str, float]:
    counts: Counter[str] = Counter()
    for row in family_rows:
        gold = _counter_from_rows(row["gold_keys"])
        pred = _counter_from_rows(row[key_field])
        counts += _prf_counts(gold, pred)
    return _prf(counts)


def _prf_counts(gold: Counter[Any], pred: Counter[Any]) -> Counter[str]:
    return Counter(
        {
            "tp": sum((gold & pred).values()),
            "fp": sum((pred - gold).values()),
            "fn": sum((gold - pred).values()),
        }
    )


def _prf(counts: Mapping[str, int]) -> dict[str, float]:
    tp = int(counts.get("tp", 0))
    fp = int(counts.get("fp", 0))
    fn = int(counts.get("fn", 0))
    precision = 0.0 if tp + fp == 0 else round(tp / (tp + fp), 4)
    recall = 0.0 if tp + fn == 0 else round(tp / (tp + fn), 4)
    denom = 2 * tp + fp + fn
    f1 = 0.0 if denom == 0 else round(2 * tp / denom, 4)
    return {"precision": precision, "recall": recall, "f1": f1}


def _four_family_exact(letter_rows: Sequence[Mapping[str, Any]], field: str) -> int:
    by_letter: dict[str, list[bool]] = {}
    for row in letter_rows:
        by_letter.setdefault(str(row["letter_id"]), []).append(bool(row[field]))
    return sum(1 for flags in by_letter.values() if all(flags))


def _family_exact(letter_rows: Sequence[Mapping[str, Any]], field: str) -> dict[str, int]:
    return {
        family: sum(1 for row in letter_rows if row["family"] == family and row[field])
        for family in FAMILIES
    }


def _counter_rows(counter: Counter[Any]) -> list[dict[str, Any]]:
    rows = [{"key": _jsonable(key), "count": count} for key, count in counter.items()]
    return sorted(rows, key=lambda row: json.dumps(row["key"], sort_keys=True))


def _counter_from_rows(rows: Sequence[Mapping[str, Any]]) -> Counter[Any]:
    counter: Counter[Any] = Counter()
    for row in rows:
        key = row["key"]
        if isinstance(key, list):
            key = tuple(tuple(item) if isinstance(item, list) else item for item in key)
        counter[key] += int(row["count"])
    return counter


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


assembly_row = _assembly_row
changed_rows = _changed_rows
compare_pair = _compare_pair
existing_complete_rows = _existing_complete_rows
letters_dev140 = _letters
score_arm = _score_arm


if __name__ == "__main__":
    raise SystemExit("use python -m clinical_extraction.paper")
