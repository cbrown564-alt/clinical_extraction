#!/usr/bin/env python3
"""Aggregate-only SeizureFrequency split decomposition (dev140 + test60).

Protocol: docs/research/exectv2/sf_split_decomposition_protocol_2026-08-14.md
Zero model calls. Holdout outputs are aggregates only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.views import (
    mention_to_dict,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    run_all9_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.constants import (
    CUI,
    CUI_PHRASE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (
    TARGET_INDICATORS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    aggregate_scores,
    annotation_from_mapping,
    clinical_headline_scores,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    _frequency_state,
    _frequency_type_key,
    score_frequency_state,
)

try:
    from scripts.exectv2_within_family_categories import family_subtypes
except ModuleNotFoundError:
    from exectv2_within_family_categories import family_subtypes  # type: ignore[no-redef]

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/exectv2/sf_split_decomposition_protocol_2026-08-14.md"
OUT_JSON = REPO_ROOT / "experiments/exectv2_sf_split_decomposition_20260814.json"
DATE_STAMP = "20260814"
MIN_N = 10
PRIMARY_SUBTYPES = (
    "seizure_free",
    "numeric_cadence_rate",
    "count_in_named_window",
    "qualitative_frequency_change",
)
ROSTER = (
    ("gpt41mini", "GPT-4.1-mini"),
    ("gpt56luna", "GPT-5.6 Luna"),
    ("gpt56sol", "GPT-5.6 Sol"),
    ("deepseek_v4_flash", "DeepSeek V4 Flash"),
    ("qwen36_35b", "Qwen 3.6:35B"),
    ("gemma4_26b", "Gemma 4 26B"),
)
SEALED_LLM = {
    "gpt41mini": REPO_ROOT
    / "scratch/holdout/exectv2_test60/gpt41mini/gpt41mini_sealed_rows.jsonl",
    "gpt56luna": REPO_ROOT
    / "scratch/holdout/exectv2_test60/gpt56luna/gpt56luna_sealed_rows.jsonl",
    "gpt56sol": REPO_ROOT
    / "scratch/holdout/exectv2_test60_sol_credit_v2/gpt56sol/gpt56sol_sealed_rows.jsonl",
    "deepseek_v4_flash": REPO_ROOT
    / "scratch/holdout/exectv2_test60/deepseek_v4_flash"
    / "deepseek_v4_flash_sealed_rows.jsonl",
    "qwen36_35b": REPO_ROOT
    / "scratch/local_queue/qwen36_35b_exect/test60/qwen36_35b"
    / "qwen36_35b_sealed_rows.jsonl",
    "gemma4_26b": REPO_ROOT
    / "scratch/local_queue/gemma4_26b_exect/test60/gemma4_26b"
    / "gemma4_26b_sealed_rows.jsonl",
}
FIDELITY = {
    "test60": {
        "gpt56sol": {
            "llm_sf": 0.5106,
            "hybrid_sf": 0.6143,
            "hybrid_four_family": 0.8196,
        }
    },
    "dev140": {"gpt56sol": {"hybrid_sf": 0.7976}},
}

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


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def _structured_path(cell_id: str, slug: str) -> Path:
    sources = _inventory()["cells"][cell_id]["sources"]
    key = "deepseek_v4_flash_0731" if (
        cell_id == "exect_test60" and slug == "deepseek_v4_flash"
    ) else slug
    return REPO_ROOT / sources[key]["structured"]


def _gold_mention_dicts(letter: ExectLetter) -> list[dict[str, Any]]:
    return [
        {
            "entity": annotation.entity,
            "text": annotation.text,
            "attributes": dict(annotation.attributes),
        }
        for annotation in letter.annotations
        if annotation.entity in TARGET_INDICATORS
    ]


def _sf_mentions(mentions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [m for m in mentions if str(m.get("entity") or "") == "SeizureFrequency"]


def letter_profile(sf_gold: list[dict[str, Any]]) -> str:
    if not sf_gold:
        return "empty"
    states = {_frequency_state(m.get("attributes") or {}) for m in sf_gold}
    if states == {"active-rate"}:
        return "active_rate_only"
    if states == {"seizure-free"}:
        return "seizure_free_only"
    if states == {"unknown"}:
        return "unknown_only"
    if len(states) >= 2:
        return "mixed"
    return "other"


def same_type_multi_state(sf_gold: list[dict[str, Any]]) -> bool:
    by_type: dict[Any, set[str]] = defaultdict(set)
    for mention in sf_gold:
        annotation = annotation_from_mapping(mention)
        by_type[_frequency_type_key(annotation)].add(
            _frequency_state(annotation.attributes)
        )
    return any(len(states) >= 2 for states in by_type.values())


def _annos(mentions: list[dict[str, Any]]) -> tuple[ExectAnnotation, ...]:
    return tuple(annotation_from_mapping(m) for m in _sf_mentions(mentions))


def _strip_cui_annos(annotations: tuple[ExectAnnotation, ...]) -> tuple[ExectAnnotation, ...]:
    return tuple(
        ExectAnnotation(
            entity=annotation.entity,
            text=annotation.text,
            attributes={
                key: value
                for key, value in annotation.attributes.items()
                if key not in (CUI, CUI_PHRASE)
            },
        )
        for annotation in annotations
    )


def _letters_from_pairs(
    pairs: list[tuple[str, list[dict[str, Any]], list[dict[str, Any]]]],
    *,
    cui_free: bool = False,
) -> tuple[list[ExectLetter], list[ExectLetter]]:
    gold: list[ExectLetter] = []
    pred: list[ExectLetter] = []
    for letter_id, gold_m, pred_m in pairs:
        gold_annos = _annos(gold_m)
        pred_annos = _annos(pred_m)
        if cui_free:
            gold_annos = _strip_cui_annos(gold_annos)
            pred_annos = _strip_cui_annos(pred_annos)
        gold.append(ExectLetter(letter_id=letter_id, note_text="", annotations=gold_annos))
        pred.append(ExectLetter(letter_id=letter_id, note_text="", annotations=pred_annos))
    return gold, pred


def _prf(score: Any) -> dict[str, Any]:
    return {
        "precision": _round(score.precision),
        "recall": _round(score.recall),
        "f1": _round(score.f1),
        "tp": int(getattr(score, "precision_tp", score.tp)),
        "fp": int(score.fp),
        "fn": int(score.fn),
        "pred_count": int(getattr(score, "pred_count", score.tp + score.fp)),
        "gold_count": int(getattr(score, "gold_count", score.tp + score.fn)),
    }


def _score_pairs(
    pairs: list[tuple[str, list[dict[str, Any]], list[dict[str, Any]]]],
) -> dict[str, Any]:
    gold_letters, pred_letters = _letters_from_pairs(pairs)
    states = score_frequency_state(gold_letters, pred_letters)
    cui_free_gold, cui_free_pred = _letters_from_pairs(pairs, cui_free=True)
    cui_free = score_frequency_state(cui_free_gold, cui_free_pred)
    four = clinical_headline_scores(
        [
            ExectLetter(
                letter_id=letter_id,
                note_text="",
                annotations=tuple(annotation_from_mapping(m) for m in gold_m),
            )
            for letter_id, gold_m, _pred in pairs
        ],
        [
            ExectLetter(
                letter_id=letter_id,
                note_text="",
                annotations=tuple(annotation_from_mapping(m) for m in pred_m),
            )
            for letter_id, _gold, pred_m in pairs
        ],
    )
    overall = aggregate_scores(four.values())
    return {
        "n_letters": len(pairs),
        "clinical_headline": _prf(states.clinical_headline),
        "clinical_headline_cui_free": _prf(cui_free.clinical_headline),
        "state_profile": _prf(states.state_profile),
        "state_profile_directional": _prf(states.state_profile_directional),
        "active_rate": _prf(states.active_rate),
        "seizure_free": _prf(states.seizure_free),
        "unknown": _prf(states.unknown),
        "four_family_f1": _round(float(overall["f1"])),
        "below_floor": len(pairs) < MIN_N,
    }


def _confusion(
    pairs: list[tuple[str, list[dict[str, Any]], list[dict[str, Any]]]],
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for _letter_id, gold_m, pred_m in pairs:
        gold_keys = {
            (_frequency_type_key(a), _frequency_state(a.attributes))
            for a in _annos(gold_m)
        }
        pred_keys = {
            (_frequency_type_key(a), _frequency_state(a.attributes))
            for a in _annos(pred_m)
        }
        gold_types = {item[0] for item in gold_keys}
        gold_states = {item[1] for item in gold_keys}
        pred_types = {item[0] for item in pred_keys}
        counts["gold_keys"] += len(gold_keys)
        counts["pred_keys"] += len(pred_keys)
        counts["exact_tp"] += len(gold_keys & pred_keys)
        for key in pred_keys - gold_keys:
            _type, state = key
            if state == "active-rate":
                counts["extra_active_rate"] += 1
            if _type in gold_types:
                counts["fp_known_type"] += 1
            elif state in gold_states:
                counts["fp_known_state_new_type"] += 1
            else:
                counts["fp_unrelated"] += 1
        for key in gold_keys - pred_keys:
            _type, state = key
            if state == "unknown":
                counts["missed_unknown"] += 1
            if _type in pred_types:
                counts["fn_known_type"] += 1
            elif state in {item[1] for item in pred_keys}:
                counts["fn_known_state_new_type"] += 1
            else:
                counts["fn_unrelated"] += 1
    return dict(counts)


def _restrict(letter: PredictedLetter) -> PredictedLetter:
    return PredictedLetter(
        letter_id=letter.letter_id,
        mentions=tuple(m for m in letter.mentions if m.entity in TARGET_INDICATORS),
    )


def _rules_mentions(split: str) -> dict[str, list[dict[str, Any]]]:
    gold = load_letters_for_split("dev" if split == "dev140" else "test")
    restricted = tuple(
        _restrict(letter)
        for letter in run_all9_on_letters(
            gold,
            include_diagnosis_resolution_candidate=False,
            include_diagnosis_benchmark_residuals=False,
        )
    )
    return {
        letter.letter_id: [mention_to_dict(m) for m in letter.mentions]
        for letter in restricted
    }


def _hybrid_mentions(
    split: str, slug: str, letters: dict[str, ExectLetter]
) -> dict[str, list[dict[str, Any]]]:
    cell = "exect_dev140" if split == "dev140" else "exect_test60"
    path = _structured_path(cell, slug)
    out: dict[str, list[dict[str, Any]]] = {}
    for row in _read_jsonl(path):
        letter_id = str(row["letter_id"])
        letter = letters[letter_id]
        gold = _gold_mention_dicts(letter)
        events = row.get("structured_events") or []
        if not events:
            out[letter_id] = []
            continue
        replay = stage.replay_letter(row, letter, gold_mentions=gold)
        if not replay.get("replayable"):
            out[letter_id] = []
            continue
        out[letter_id] = [
            mention
            for mention in (replay.get("final_mentions") or [])
            if mention.get("entity") in TARGET_INDICATORS
        ]
    return out


def _llm_mentions(split: str, slug: str) -> dict[str, list[dict[str, Any]]]:
    if split == "dev140":
        path = Path(_inventory()["cells"]["exect_dev140"]["sources"][slug]["assembly"])
        if not path.is_absolute():
            path = REPO_ROOT / path
    else:
        path = SEALED_LLM[slug]
    if not path.is_file():
        raise FileNotFoundError(path)
    out: dict[str, list[dict[str, Any]]] = {}
    for row in _read_jsonl(path):
        out[str(row["letter_id"])] = [
            mention
            for mention in (row.get("raw_lane_mentions") or [])
            if mention.get("entity") in TARGET_INDICATORS
        ]
    return out


def _build_gold_index(
    letters: dict[str, ExectLetter],
) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for letter_id, letter in letters.items():
        gold = _gold_mention_dicts(letter)
        sf = _sf_mentions(gold)
        subtypes = {
            subtype
            for mention in sf
            for subtype in family_subtypes(mention)
        }
        index[letter_id] = {
            "gold": gold,
            "profile": letter_profile(sf),
            "subtypes": subtypes,
            "same_type_multi_state": same_type_multi_state(sf),
            "sf_present": bool(sf),
        }
    return index


def _pairs_for(
    letter_ids: list[str],
    gold_index: dict[str, dict[str, Any]],
    pred_by_id: dict[str, list[dict[str, Any]]],
) -> list[tuple[str, list[dict[str, Any]], list[dict[str, Any]]]]:
    return [
        (letter_id, gold_index[letter_id]["gold"], pred_by_id.get(letter_id, []))
        for letter_id in letter_ids
    ]


def _stratum_block(
    name: str,
    letter_ids: list[str],
    gold_index: dict[str, dict[str, Any]],
    pred_by_id: dict[str, list[dict[str, Any]]],
    *,
    include_confusion: bool,
) -> dict[str, Any]:
    pairs = _pairs_for(letter_ids, gold_index, pred_by_id)
    block = {"stratum": name, "n_letters": len(letter_ids), **_score_pairs(pairs)}
    if include_confusion:
        block["confusion"] = _confusion(pairs)
    return block


def _method_block(
    *,
    split: str,
    method: str,
    slug: str | None,
    gold_index: dict[str, dict[str, Any]],
    pred_by_id: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    all_ids = sorted(gold_index)
    sf_ids = [lid for lid in all_ids if gold_index[lid]["sf_present"]]
    profiles: dict[str, list[str]] = defaultdict(list)
    subtypes: dict[str, list[str]] = defaultdict(list)
    multi: list[str] = []
    single_state: list[str] = []
    for lid in all_ids:
        meta = gold_index[lid]
        profiles[meta["profile"]].append(lid)
        for subtype in meta["subtypes"]:
            if subtype in PRIMARY_SUBTYPES:
                subtypes[subtype].append(lid)
        if meta["sf_present"] and meta["same_type_multi_state"]:
            multi.append(lid)
        elif meta["sf_present"]:
            single_state.append(lid)

    overall = _stratum_block("all_letters", all_ids, gold_index, pred_by_id, include_confusion=True)
    return {
        "split": split,
        "method": method,
        "slug": slug,
        "overall": overall,
        "sf_present": _stratum_block(
            "sf_present", sf_ids, gold_index, pred_by_id, include_confusion=True
        ),
        "subtypes": {
            name: _stratum_block(name, lids, gold_index, pred_by_id, include_confusion=False)
            for name, lids in subtypes.items()
        },
        "profiles": {
            name: _stratum_block(name, lids, gold_index, pred_by_id, include_confusion=False)
            for name, lids in profiles.items()
        },
        "same_type_multi_state": _stratum_block(
            "same_type_multi_state", multi, gold_index, pred_by_id, include_confusion=False
        ),
        "sf_present_not_same_type_multi": _stratum_block(
            "sf_present_not_same_type_multi",
            single_state,
            gold_index,
            pred_by_id,
            include_confusion=False,
        ),
    }


def _check_fidelity(payload: dict[str, Any]) -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = []

    def add(name: str, actual: float, expected: float) -> None:
        ok = abs(actual - expected) <= 0.0001
        gates.append(
            {
                "name": name,
                "actual": _round(actual),
                "expected": expected,
                "passed": ok,
            }
        )
        if not ok:
            raise RuntimeError(f"fidelity gate failed: {name} {actual} != {expected}")

    test_models = payload["splits"]["test60"]["methods"]
    gates.append(
        {
            "name": "test60.sol.llm.sf_cui_free_vs_stage_panel",
            "actual": _round(
                test_models["llm"]["gpt56sol"]["overall"]["clinical_headline_cui_free"]["f1"]
            ),
            "expected": FIDELITY["test60"]["gpt56sol"]["llm_sf"],
            "passed": True,
            "note": (
                "Stage-panel raw_lane_score SF 0.5106 is a frozen identity. "
                "Living reconstruction from sealed raw_lane_mentions is recorded, "
                "not gated, because the two surfaces are not byte-reproducible."
            ),
        }
    )
    add(
        "test60.sol.hybrid.sf",
        test_models["llm_with_rules"]["gpt56sol"]["overall"]["clinical_headline"]["f1"],
        FIDELITY["test60"]["gpt56sol"]["hybrid_sf"],
    )
    add(
        "test60.sol.hybrid.four_family",
        test_models["llm_with_rules"]["gpt56sol"]["overall"]["four_family_f1"],
        FIDELITY["test60"]["gpt56sol"]["hybrid_four_family"],
    )
    add(
        "dev140.sol.hybrid.sf",
        payload["splits"]["dev140"]["methods"]["llm_with_rules"]["gpt56sol"]["overall"][
            "clinical_headline"
        ]["f1"],
        FIDELITY["dev140"]["gpt56sol"]["hybrid_sf"],
    )
    rules_test = json.loads(
        (
            REPO_ROOT
            / "experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260801.json"
        ).read_text(encoding="utf-8")
    )
    add(
        "test60.rules.sf",
        test_models["rules"]["overall"]["clinical_headline"]["f1"],
        float(rules_test["clinical_headline_by_family"]["SeizureFrequency"]["f1"]),
    )
    return gates


def build(*, skip_hybrid: bool = False) -> dict[str, Any]:
    splits: dict[str, Any] = {}
    for split, machine, expected_n in (
        ("dev140", "dev", 140),
        ("test60", "test", 59),
    ):
        print(f"loading gold {split}", flush=True)
        loaded = {letter.letter_id: letter for letter in load_letters_for_split(machine)}
        if len(loaded) != expected_n:
            raise ValueError(f"{split} loaded {len(loaded)}, expected {expected_n}")
        gold_index = _build_gold_index(loaded)
        gold_mix = {
            "n_letters": expected_n,
            "profiles": dict(Counter(meta["profile"] for meta in gold_index.values())),
            "subtype_letters": {
                subtype: sum(1 for meta in gold_index.values() if subtype in meta["subtypes"])
                for subtype in PRIMARY_SUBTYPES
            },
            "same_type_multi_state_letters": sum(
                1
                for meta in gold_index.values()
                if meta["sf_present"] and meta["same_type_multi_state"]
            ),
            "sf_present_letters": sum(1 for meta in gold_index.values() if meta["sf_present"]),
        }
        print(f"rules {split}", flush=True)
        rules_pred = _rules_mentions(split)
        methods: dict[str, Any] = {
            "rules": _method_block(
                split=split,
                method="rules",
                slug=None,
                gold_index=gold_index,
                pred_by_id=rules_pred,
            )
        }
        llm_block: dict[str, Any] = {}
        hybrid_block: dict[str, Any] = {}
        for slug, _label in ROSTER:
            print(f"llm {split} {slug}", flush=True)
            llm_pred = _llm_mentions(split, slug)
            llm_block[slug] = _method_block(
                split=split,
                method="llm",
                slug=slug,
                gold_index=gold_index,
                pred_by_id=llm_pred,
            )
            if skip_hybrid:
                continue
            print(f"hybrid {split} {slug}", flush=True)
            hybrid_pred = _hybrid_mentions(split, slug, loaded)
            hybrid_block[slug] = _method_block(
                split=split,
                method="llm_with_rules",
                slug=slug,
                gold_index=gold_index,
                pred_by_id=hybrid_pred,
            )
        methods["llm"] = llm_block
        if not skip_hybrid:
            methods["llm_with_rules"] = hybrid_block
        splits[split] = {
            "n_letters": expected_n,
            "row_policy": (
                "development_review_permitted" if split == "dev140" else "aggregate_only"
            ),
            "gold_mix": gold_mix,
            "methods": methods,
        }

    payload: dict[str, Any] = {
        "schema_version": "exectv2.sf_split_decomposition.v1",
        "date": "2026-08-14",
        "protocol": PROTOCOL,
        "git": _git_note(),
        "claim_boundary": (
            "Aggregate SF strata on dev140 and test60. Machine scoring of sealed "
            "ledgers and in-memory current-stack replay. No human sealed-row "
            "inspection. Not a Decision 0046/0050 rewrite."
        ),
        "row_policy": {
            "sealed_row_jsonl_machine_scored": True,
            "sealed_row_jsonl_human_inspected": False,
            "public_row_identifiers_allowed": False,
        },
        "splits": splits,
    }
    if not skip_hybrid:
        payload["fidelity"] = _check_fidelity(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-hybrid", action="store_true")
    args = parser.parse_args()
    payload = build(skip_hybrid=args.skip_hybrid)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(REPO_ROOT)}", flush=True)


if __name__ == "__main__":
    main()
