"""No-call Luna remasure of the Phase 3 encoding pack.

Luna ``dev140`` v0.9.24 sidecar first. Optional v10 ``dev20`` mechanism
cut. Zero model calls. ``test60`` not loaded.
"""

from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    headline_keys,
)

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "experiments" / "exectv2_prompt_convention_encoding_luna_dev140_20260815.json"
LUNA_DEV140 = (
    REPO
    / "experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715_structured.jsonl"
)
V10_DEV20 = (
    REPO
    / "experiments/exectv2_structured_prompt_v10_luna_dev20_20260815/v10_live/structured.jsonl"
)
V0924_DEV20 = (
    REPO
    / "experiments/exectv2_structured_prompt_v10_luna_dev20_20260815/v0924_control/structured.jsonl"
)
FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")
BASELINE_LUNA = {
    "f1": 0.9028,
    "by_family": {
        "Diagnosis": 0.8995,
        "SeizureFrequency": 0.8328,
        "Prescription": 0.9507,
        "Investigations": 0.9202,
    },
}

_STAGE_PATH = REPO / "scripts/build_exectv2_hybrid_stage_ablation.py"
_SPEC = importlib.util.spec_from_file_location("exect_hybrid_stage_ablation", _STAGE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Cannot import replay helpers from {_STAGE_PATH}")
stage = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(stage)


def _prf(tp: int, fp: int, fn: int) -> dict[str, float | int]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def _gold_rows(letter: ExectLetter) -> list[dict[str, Any]]:
    return [
        {
            "entity": ann.entity,
            "text": ann.text,
            "attributes": dict(ann.attributes),
            "evidence": ann.raw_text or ann.text,
        }
        for ann in letter.annotations
        if ann.entity in FAMILIES
    ]


def _score_letter(
    gold: list[dict[str, Any]], pred: list[dict[str, Any]]
) -> dict[str, Any]:
    by_family: dict[str, dict[str, Any]] = {}
    exact = True
    for family in FAMILIES:
        gold_keys = headline_keys(
            {"gold_mentions": gold, "predicted_mentions": []},
            family,
            field="gold_mentions",
        )
        pred_keys = headline_keys(
            {"gold_mentions": gold, "predicted_mentions": pred},
            family,
            field="predicted_mentions",
        )
        g = Counter(gold_keys)
        p = Counter(pred_keys)
        tp = sum((g & p).values())
        fp = sum((p - g).values())
        fn = sum((g - p).values())
        by_family[family] = {
            "gold_keys": gold_keys,
            "pred_keys": pred_keys,
            **_prf(tp, fp, fn),
        }
        if fp or fn:
            exact = False
    pooled = Counter()
    for family in FAMILIES:
        pooled["tp"] += int(by_family[family]["tp"])
        pooled["fp"] += int(by_family[family]["fp"])
        pooled["fn"] += int(by_family[family]["fn"])
    return {
        "exact": exact,
        "pooled": _prf(pooled["tp"], pooled["fp"], pooled["fn"]),
        "by_family": {family: _prf(
            int(by_family[family]["tp"]),
            int(by_family[family]["fp"]),
            int(by_family[family]["fn"]),
        ) for family in FAMILIES},
    }


def _replay_cell(path: Path, letters: dict[str, ExectLetter]) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    pooled = Counter()
    family_counts = {family: Counter() for family in FAMILIES}
    n = 0
    replayable = 0
    encoding_actions: Counter[str] = Counter()
    letter_rows: list[dict[str, Any]] = []
    for structured in rows:
        letter_id = str(structured["letter_id"])
        letter = letters[letter_id]
        gold = _gold_rows(letter)
        events = structured.get("structured_events") or []
        if not events:
            pred: list[dict[str, Any]] = []
        else:
            replay = stage.replay_letter(structured, letter, gold_mentions=gold)
            pred = [
                mention
                for mention in (replay.get("final_mentions") or [])
                if mention.get("entity") in FAMILIES
            ]
            replayable += 1
            for action in structured.get("projection_actions") or []:
                encoding_actions[str(action.get("rule_id") or "")] += 1
        scored = _score_letter(gold, pred)
        n += 1
        pooled["tp"] += int(scored["pooled"]["tp"])
        pooled["fp"] += int(scored["pooled"]["fp"])
        pooled["fn"] += int(scored["pooled"]["fn"])
        for family in FAMILIES:
            family_counts[family]["tp"] += int(scored["by_family"][family]["tp"])
            family_counts[family]["fp"] += int(scored["by_family"][family]["fp"])
            family_counts[family]["fn"] += int(scored["by_family"][family]["fn"])
        letter_rows.append(
            {
                "letter_id": letter_id,
                "exact": scored["exact"],
                "pooled": scored["pooled"],
                "by_family": scored["by_family"],
            }
        )
    return {
        "n_letters": n,
        "replayable": replayable,
        "source": str(path.relative_to(REPO)).replace("\\", "/"),
        "pooled": _prf(pooled["tp"], pooled["fp"], pooled["fn"]),
        "by_family": {
            family: _prf(
                family_counts[family]["tp"],
                family_counts[family]["fp"],
                family_counts[family]["fn"],
            )
            for family in FAMILIES
        },
        "letters": letter_rows,
    }


SIX_MODEL = (
    ("gpt56luna", LUNA_DEV140),
    (
        "gpt56sol",
        REPO / "experiments/exectv2_six_model_single_call_gpt56sol_dev140_20260715_structured.jsonl",
    ),
    (
        "deepseek_v4_flash",
        REPO / "experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731_structured.jsonl",
    ),
    (
        "qwen36_35b",
        REPO / "experiments/exectv2_six_model_single_call_qwen36_35b_dev140_20260715_structured.jsonl",
    ),
    (
        "gemma4_26b",
        REPO / "experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715_structured.jsonl",
    ),
    (
        "gemini37flash",
        REPO / "experiments/exectv2_six_model_single_call_gemini37flash_dev140_20260813_structured.jsonl",
    ),
)


def main() -> None:
    letters = {letter.letter_id: letter for letter in load_letters_for_split("dev")}
    if len(letters) != 140:
        raise RuntimeError(f"expected 140 dev letters, got {len(letters)}")
    print(f"remeasuring Luna dev140 from {LUNA_DEV140.name}", flush=True)
    luna = _replay_cell(LUNA_DEV140, letters)
    payload: dict[str, Any] = {
        "schema_version": "exectv2.prompt_convention_encoding.luna.v1",
        "date": "2026-08-15",
        "model_calls": 0,
        "row_policy": "dev140_rows_permitted_test60_forbidden",
        "projection_version": "exectv2_hybrid_sf_state_projection_v0.15",
        "fill_promotion": False,
        "baseline_fill": BASELINE_LUNA,
        "luna_dev140": {
            "pooled": luna["pooled"],
            "by_family": luna["by_family"],
            "n_letters": luna["n_letters"],
            "replayable": luna["replayable"],
            "source": luna["source"],
            "delta_vs_fill": round(float(luna["pooled"]["f1"]) - BASELINE_LUNA["f1"], 4),
            "family_delta_vs_fill": {
                family: round(
                    float(luna["by_family"][family]["f1"]) - BASELINE_LUNA["by_family"][family],
                    4,
                )
                for family in FAMILIES
            },
        },
    }
    if V10_DEV20.exists() and V0924_DEV20.exists():
        print("remeasuring Luna v10 and v0.9.24 dev20 mechanism cut", flush=True)
        v10 = _replay_cell(V10_DEV20, letters)
        control = _replay_cell(V0924_DEV20, letters)
        payload["luna_dev20_mechanism"] = {
            "note": (
                "Frozen 20-letter development cut. Not a benchmark. "
                "v10 raws are the encoding-pack mechanism substrate."
            ),
            "v10_through_v015": {
                "pooled": v10["pooled"],
                "by_family": v10["by_family"],
            },
            "v0924_through_v015": {
                "pooled": control["pooled"],
                "by_family": control["by_family"],
            },
        }
    print(json.dumps(payload["luna_dev140"], indent=2))
    if "luna_dev20_mechanism" in payload:
        print(json.dumps(payload["luna_dev20_mechanism"], indent=2))
    six: dict[str, Any] = {}
    for slug, path in SIX_MODEL:
        if slug == "gpt56luna":
            six[slug] = {
                "pooled": luna["pooled"],
                "by_family": luna["by_family"],
                "source": luna["source"],
            }
            continue
        if not path.exists():
            six[slug] = {"error": f"missing {path}"}
            continue
        print(f"remeasuring {slug}", flush=True)
        cell = _replay_cell(path, letters)
        six[slug] = {
            "pooled": cell["pooled"],
            "by_family": cell["by_family"],
            "source": cell["source"],
        }
    payload["six_model_dev140"] = six
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("six-model", {slug: cell.get("pooled") for slug, cell in six.items()})


if __name__ == "__main__":
    main()
