#!/usr/bin/env python3
"""No-call dev140 SF generic dated-cluster next to seizure-free drop study.

Protocol: docs/research/exectv2/sf_dated_cluster_next_to_free_protocol_2026-08-14.md
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import sf_dated_cluster
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    annotation_from_mapping,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    _frequency_state,
    _frequency_type_key,
    score_frequency_state,
)

apply_dated_cluster_next_to_free_drop = sf_dated_cluster.apply_dated_cluster_next_to_free_drop

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/exectv2/sf_dated_cluster_next_to_free_protocol_2026-08-14.md"
OUT_JSON = REPO_ROOT / "experiments/exectv2_sf_dated_cluster_next_to_free_dev140_20260814.json"
ARM = "drop_generic_dated_cluster_next_to_free"
ROSTER = (
    ("gpt41mini", "GPT-4.1-mini"),
    ("gpt56luna", "GPT-5.6 Luna"),
    ("gpt56sol", "GPT-5.6 Sol"),
    ("deepseek_v4_flash", "DeepSeek V4 Flash"),
    ("qwen36_35b", "Qwen 3.6:35B"),
    ("gemma4_26b", "Gemma 4 26B"),
)
FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")
SOL_BASELINE_SF = 0.8447

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


def _structured_path(slug: str) -> Path:
    rel = _inventory()["cells"]["exect_dev140"]["sources"][slug]["structured"]
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
    letters = {letter.letter_id: letter for letter in load_letters_for_split("dev")}
    if len(letters) != 140:
        raise ValueError(f"expected 140 dev letters, got {len(letters)}")

    models: dict[str, Any] = {}
    for slug, label in ROSTER:
        path = _structured_path(slug)
        print(f"replaying {slug} from {path.relative_to(REPO_ROOT)}", flush=True)
        structured_rows = _read_jsonl(path)
        gold_letters: list[ExectLetter] = []
        baseline_pred: list[ExectLetter] = []
        arm_pred: list[ExectLetter] = []
        action_counts: Counter[str] = Counter()
        effects: Counter[str] = Counter()
        fires: list[dict[str, Any]] = []
        replayable = 0
        empty = 0

        for structured_row in structured_rows:
            letter_id = str(structured_row["letter_id"])
            letter = letters[letter_id]
            gold = _gold_mentions(letter)
            mentions = _replay_mentions(structured_row, letter, gold)
            if not (structured_row.get("structured_events") or []):
                empty += 1
            else:
                replayable += 1
            gold_letters.append(_sf_letters(letter_id, gold))
            baseline_pred.append(_sf_letters(letter_id, mentions))
            after, actions = apply_dated_cluster_next_to_free_drop(mentions)
            arm_pred.append(_sf_letters(letter_id, after))
            for action in actions:
                action_counts[action["action"]] += 1
            gold_keys = _sf_keys(gold)
            before_keys = _sf_keys(mentions)
            after_keys = _sf_keys(after)
            effect = _cell_effect(before_keys == gold_keys, after_keys == gold_keys)
            effects[effect] += 1
            if actions:
                fires.append(
                    {
                        "letter_id": letter_id,
                        "effect": effect,
                        "actions": actions,
                        "gold_keys": [str(key) for key in gold_keys],
                        "before_keys": [str(key) for key in before_keys],
                        "after_keys": [str(key) for key in after_keys],
                    }
                )

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
            "source_artifact": path.relative_to(REPO_ROOT).as_posix(),
            "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "letters": len(structured_rows),
            "empty_structured_events": empty,
            "replayable": replayable,
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
                    "fires": fires,
                }
            },
        }

    selection = _selection(models)
    return {
        "schema_version": "exectv2.sf_dated_cluster_next_to_free.dev140.v1",
        "date": "2026-08-14",
        "protocol": PROTOCOL,
        "git": _git_note(),
        "split": "dev140",
        "method": "llm_with_rules",
        "claim_boundary": (
            "Development no-call generic dated-cluster next to seizure-free "
            "drop. Gold unused at apply time. Not holdout evidence and not a "
            "production rewrite."
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
        "development_selection": selection,
    }


def _selection(models: dict[str, Any]) -> dict[str, Any]:
    base_tp = base_fp = base_fn = 0
    after_tp = after_fp = after_fn = 0
    prof_base_tp = prof_base_fp = prof_base_fn = 0
    prof_after_tp = prof_after_fp = prof_after_fn = 0
    rescue = 0
    harm = 0
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
    fire_letters = sorted(
        {
            fire["letter_id"]
            for rec in models.values()
            for fire in rec["arms"][ARM]["fires"]
        }
    )
    met = (
        headline_delta >= 0
        and profile_delta >= 0
        and harm == 0
        and rescue >= 1
        and not negative_models
    )
    return {
        "arm": ARM,
        "pooled_headline_f1_delta": headline_delta,
        "pooled_state_profile_f1_delta": profile_delta,
        "rescue_letters": rescue,
        "harm_letters": harm,
        "models_headline_delta_below_0": negative_models,
        "fire_letter_ids": fire_letters,
        "met": met,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    payload = build()
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(REPO_ROOT)}", flush=True)
    print(json.dumps(payload["development_selection"], indent=2))


if __name__ == "__main__":
    main()
