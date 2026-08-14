#!/usr/bin/env python3
"""Aggregate-only test60 readout of SF single last-event duration.

Protocol:
docs/research/exectv2/sf_single_last_event_duration_test59_confirmation_protocol_2026-08-14.md
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_last_event_duration,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    annotation_from_mapping,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    _frequency_state,
    _frequency_type_key,
    score_frequency_state,
)

apply_single_last_event = sf_last_event_duration.apply_single_last_event

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/exectv2/sf_single_last_event_duration_test59_confirmation_protocol_2026-08-14.md"
)
OUT_JSON = REPO_ROOT / "experiments/exectv2_sf_single_last_event_duration_test60_20260814.json"
ARM = "complete_single_last_event"
ROSTER = (
    ("gpt41mini", "GPT-4.1-mini", "gpt41mini"),
    ("gpt56luna", "GPT-5.6 Luna", "gpt56luna"),
    ("gpt56sol", "GPT-5.6 Sol", "gpt56sol"),
    ("deepseek_v4_flash", "DeepSeek V4 Flash", "deepseek_v4_flash_0731"),
    ("qwen36_35b", "Qwen 3.6:35B", "qwen36_35b"),
    ("gemma4_26b", "Gemma 4 26B", "gemma4_26b"),
)
FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")
SOL_BASELINE_SF = 0.6567

_STAGE_PATH = REPO_ROOT / "scripts/build_exectv2_hybrid_stage_ablation.py"
_SPEC = importlib.util.spec_from_file_location("exect_hybrid_stage_ablation", _STAGE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Cannot import replay helpers from {_STAGE_PATH}")
stage = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(stage)


def _round(value: float) -> float:
    return round(float(value), 4)


def _git_note() -> dict[str, Any]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty_tree": None}
    return {"commit": commit, "dirty_tree": dirty}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _inventory() -> dict[str, Any]:
    return json.loads(
        (REPO_ROOT / "experiments/current_stack/SOURCES.json").read_text(encoding="utf-8")
    )


def _structured_path(source_slug: str) -> Path:
    rel = _inventory()["cells"]["exect_test60"]["sources"][source_slug]["structured"]
    path = Path(rel)
    return path if path.is_absolute() else REPO_ROOT / path


def _gold_mentions(letter: ExectLetter) -> list[dict[str, Any]]:
    return [
        {
            "entity": annotation.entity,
            "text": annotation.text,
            "attributes": dict(annotation.attributes),
        }
        for annotation in letter.annotations
        if annotation.entity in FAMILIES
    ]


def _sf_letters(letter_id: str, mentions: list[dict[str, Any]]) -> ExectLetter:
    return ExectLetter(
        letter_id=letter_id,
        note_text="",
        annotations=tuple(
            annotation_from_mapping(mention)
            for mention in mentions
            if mention.get("entity") == "SeizureFrequency"
        ),
    )


def _sf_keys(mentions: list[dict[str, Any]]) -> list[tuple[Any, str]]:
    keys: list[tuple[Any, str]] = []
    for mention in mentions:
        if mention.get("entity") != "SeizureFrequency":
            continue
        annotation = annotation_from_mapping(mention)
        keys.append((_frequency_type_key(annotation), _frequency_state(annotation.attributes)))
    return list(dict.fromkeys(keys))


def _prf(score: Any) -> dict[str, Any]:
    return {
        "precision": _round(score.precision),
        "recall": _round(score.recall),
        "f1": _round(score.f1),
        "tp": int(score.tp),
        "fp": int(score.fp),
        "fn": int(score.fn),
    }


def _score_pair(gold: list[ExectLetter], pred: list[ExectLetter]) -> dict[str, Any]:
    states = score_frequency_state(gold, pred)
    return {
        "clinical_headline": _prf(states.clinical_headline),
        "state_profile": _prf(states.state_profile),
    }


def _replay_mentions(
    structured_row: dict[str, Any], letter: ExectLetter, gold: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    events = structured_row.get("structured_events") or []
    if not events:
        return []
    replay = stage.replay_letter(structured_row, letter, gold_mentions=gold)
    if not replay.get("replayable"):
        return []
    return [
        mention
        for mention in (replay.get("final_mentions") or [])
        if mention.get("entity") in FAMILIES
    ]


def _cell_effect(before_exact: bool, after_exact: bool) -> str:
    if (not before_exact) and after_exact:
        return "rescue"
    if before_exact and (not after_exact):
        return "harm"
    return "unchanged"


def _f1(tp: int, fp: int, fn: int) -> float:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return _round(
        (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    )


def build() -> dict[str, Any]:
    letters = {letter.letter_id: letter for letter in load_letters_for_split("test")}
    if len(letters) != 59:
        raise ValueError(f"expected 59 test letters, got {len(letters)}")

    models: dict[str, Any] = {}
    for slug, label, source_slug in ROSTER:
        path = _structured_path(source_slug)
        print(f"replaying {slug}", flush=True)
        structured_rows = _read_jsonl(path)
        by_id = {str(row["letter_id"]): row for row in structured_rows}
        gold_letters: list[ExectLetter] = []
        baseline_pred: list[ExectLetter] = []
        arm_pred: list[ExectLetter] = []
        action_counts: Counter[str] = Counter()
        effects: Counter[str] = Counter()
        fire_count = 0
        replayable = 0
        empty = 0
        missing = 0

        for ordinal, letter_id in enumerate(sorted(letters)):
            letter = letters[letter_id]
            gold = _gold_mentions(letter)
            structured_row = by_id.get(letter_id)
            if structured_row is None:
                missing += 1
                mentions: list[dict[str, Any]] = []
            else:
                mentions = _replay_mentions(structured_row, letter, gold)
                if not (structured_row.get("structured_events") or []):
                    empty += 1
                else:
                    replayable += 1
            cell_id = f"cell-{ordinal:03d}"
            gold_letters.append(_sf_letters(cell_id, gold))
            baseline_pred.append(_sf_letters(cell_id, mentions))
            after, actions = apply_single_last_event(mentions)
            arm_pred.append(_sf_letters(cell_id, after))
            for action in actions:
                action_counts[action["action"]] += 1
            if actions:
                fire_count += 1
            effects[
                _cell_effect(
                    _sf_keys(mentions) == _sf_keys(gold),
                    _sf_keys(after) == _sf_keys(gold),
                )
            ] += 1

        baseline_scores = _score_pair(gold_letters, baseline_pred)
        if slug == "gpt56sol":
            actual = baseline_scores["clinical_headline"]["f1"]
            if abs(actual - SOL_BASELINE_SF) > 0.0001:
                raise RuntimeError(
                    f"Sol baseline SF F1 {actual} != {SOL_BASELINE_SF}"
                )
        after_scores = _score_pair(gold_letters, arm_pred)
        models[slug] = {
            "label": label,
            "source_slug": source_slug,
            "source_artifact": path.relative_to(REPO_ROOT).as_posix(),
            "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "letters": len(letters),
            "sidecar_rows": len(structured_rows),
            "empty_structured_events": empty,
            "replayable": replayable,
            "missing_sidecar": missing,
            "baseline": baseline_scores,
            "arms": {
                ARM: {
                    "scores": after_scores,
                    "delta_headline_f1": _round(
                        after_scores["clinical_headline"]["f1"]
                        - baseline_scores["clinical_headline"]["f1"]
                    ),
                    "delta_state_profile_f1": _round(
                        after_scores["state_profile"]["f1"]
                        - baseline_scores["state_profile"]["f1"]
                    ),
                    "effects": dict(effects),
                    "actions": dict(action_counts),
                    "fire_count": fire_count,
                }
            },
        }

    confirmation = _confirmation(models)
    return {
        "schema_version": "exectv2.sf_single_last_event_duration.test60.v1",
        "date": "2026-08-14",
        "protocol": PROTOCOL,
        "git": _git_note(),
        "split": "test60",
        "split_machine": "test",
        "row_policy": "aggregate_only",
        "method": "llm_with_rules",
        "claim_boundary": (
            "Aggregate-only holdout readout of the promoted single "
            "last-event duration pass. No letter identifiers. Not a "
            "Decision 0046 / 0050 rewrite."
        ),
        "models": models,
        "pooled_effects": {
            ARM: dict(
                sum(
                    (Counter(rec["arms"][ARM]["effects"]) for rec in models.values()),
                    Counter(),
                )
            )
        },
        "confirmation": confirmation,
    }


def _confirmation(models: dict[str, Any]) -> dict[str, Any]:
    base_tp = base_fp = base_fn = 0
    after_tp = after_fp = after_fn = 0
    prof_base_tp = prof_base_fp = prof_base_fn = 0
    prof_after_tp = prof_after_fp = prof_after_fn = 0
    rescue = 0
    harm = 0
    fires = 0
    for rec in models.values():
        b = rec["baseline"]["clinical_headline"]
        a = rec["arms"][ARM]["scores"]["clinical_headline"]
        base_tp += b["tp"]
        base_fp += b["fp"]
        base_fn += b["fn"]
        after_tp += a["tp"]
        after_fp += a["fp"]
        after_fn += a["fn"]
        pb = rec["baseline"]["state_profile"]
        pa = rec["arms"][ARM]["scores"]["state_profile"]
        prof_base_tp += pb["tp"]
        prof_base_fp += pb["fp"]
        prof_base_fn += pb["fn"]
        prof_after_tp += pa["tp"]
        prof_after_fp += pa["fp"]
        prof_after_fn += pa["fn"]
        rescue += int(rec["arms"][ARM]["effects"].get("rescue", 0))
        harm += int(rec["arms"][ARM]["effects"].get("harm", 0))
        fires += int(rec["arms"][ARM]["fire_count"])

    headline_delta = _round(
        _f1(after_tp, after_fp, after_fn) - _f1(base_tp, base_fp, base_fn)
    )
    profile_delta = _round(
        _f1(prof_after_tp, prof_after_fp, prof_after_fn)
        - _f1(prof_base_tp, prof_base_fp, prof_base_fn)
    )
    negative_models = [
        slug
        for slug, rec in models.items()
        if rec["arms"][ARM]["delta_headline_f1"] < 0
    ]
    met = (
        headline_delta >= 0
        and profile_delta >= 0
        and harm == 0
        and not negative_models
    )
    return {
        "arm": ARM,
        "pooled_headline_f1_delta": headline_delta,
        "pooled_state_profile_f1_delta": profile_delta,
        "rescue_letters": rescue,
        "harm_letters": harm,
        "fire_count": fires,
        "models_headline_delta_below_0": negative_models,
        "verdict": "CONFIRMED" if met else "KILLED",
        "met": met,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    payload = build()
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(REPO_ROOT)}", flush=True)
    print(json.dumps(payload["confirmation"], indent=2))


if __name__ == "__main__":
    main()
