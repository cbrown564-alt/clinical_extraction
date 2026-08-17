"""Phase 0 catalog, then study-only mention-unit × cheap-stack grafts."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dspy
from dotenv import load_dotenv

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit import (
    COMBO_ARM_VERSIONS,
    HYBRID_METHOD,
    LLM_METHOD,
    MENTION_UNIT_MODEL,
    MENTION_UNIT_PROMPT_VERSION,
    SYSTEM_MESSAGE,
    MentionUnitExtractor,
    build_mention_unit_prompt,
    materialize_mention_unit,
    mention_unit_prompt_version,
    parse_mention_unit_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    score_concept_identity,
    score_frequency_state,
    score_investigations_components,
    score_prescription_components,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from scripts.run_exectv2_mention_unit_v2_leftover_form_v3_luna_dev140 import (
    _form_census,
)
from scripts.run_exectv2_mention_unit_v2_luna import (
    DEV20_IDS,
    FAMILIES,
    _carrier_texts,
    _empty_materialization,
    _hybrid_growth,
    _load_dev20,
    _nontarget_mentions,
    _score_method,
    _span_matches,
    _verify_prompt_contracts,
)
from scripts.run_exectv2_v0924_cheap_further_prune_luna_dev20 import (
    CHEAP_STRUCTURED,
    CHEAP_VERSION,
    CONTROL_STRUCTURED,
    _changed_rows,
    _compare_pair,
    _letters,
    _raws,
    _replay_arm,
    _run_candidate,
    decide_arm,
    topology_failures,
)
from scripts.run_exectv2_v0924_cheap_stack_luna_dev140 import (
    CONTROL_VERSION,
    _require_api_key,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/exectv2/mention_unit_cheap_combo_luna_dev20_protocol_2026-08-17.md"
REPORT = ROOT / "docs/research/exectv2/mention_unit_cheap_combo_luna_dev20_2026-08-17.md"
SOURCE_ROWS = ROOT / "experiments/exectv2_mention_unit_v2_luna_dev20_20260816" / "rows.jsonl"
CHEAP_DIR = ROOT / "experiments/exectv2_v0924_cheap_stack_plain_luna_dev20_20260816"
STUDY_DIR = ROOT / "experiments/exectv2_mention_unit_cheap_combo_luna_dev20_20260817"
MENTION_ENCODER = "leftover_form_span_fold_negation_v9"
SYSTEMS = ("mention_unit_v9", "cheap_stack", "v0924")
COMBO_VERSION = structured.PROMPT_VERSION_V0_9_40_COMBO_CLINICAL_NAME
NAME_IN_CHEAP_ARMS = {
    "name_in_cheap": {
        "version": COMBO_VERSION,
        "n_rules": 67,
        "drops_prompt_version": False,
        "label": "mention-unit clinical-name sentence on cheap stack",
    }
}
FORM_GUIDE_VERSION = COMBO_ARM_VERSIONS["form_guide"]
FORM_GUIDE_ENCODER = "leftover_form_span_fold_negation_v9"
_FORM_GUIDE_BANNED = (
    "mention",
    "span",
    "coding fields",
    "this method",
    "return only",
    "list 2",
    "list 9",
    "list 11",
    "named type not generic",
    "gold",
    "scorer",
    "prompt_version",
    "letter_id",
    "control",
)
SCAFFOLD_VERSION = COMBO_ARM_VERSIONS["scaffold"]
_SCAFFOLD_BANNED = (
    "gold",
    "scorer",
    "prompt_version",
    "letter_id",
    "control",
    "mention",
    "span",
    "coding fields",
    "this method",
    "return only",
    "candidate_id",
    "lane_hint",
    "anchor_hint",
    "architecture",
)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--arm",
        choices=("catalog", "name_in_cheap", "scaffold", "form_guide"),
        default="catalog",
    )
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--api-base")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--progress-every", type=int, default=1)
    args = parser.parse_args(argv)
    if args.arm == "catalog":
        run_catalog()
        return
    if args.arm in {"scaffold", "form_guide"}:
        if not args.live:
            verifier = (
                verify_form_guide_payload
                if args.arm == "form_guide"
                else verify_scaffold_payload
            )
            print(json.dumps(verifier(), indent=2, sort_keys=True))
            return
        runner = run_form_guide if args.arm == "form_guide" else run_scaffold
        print(
            json.dumps(
                runner(
                    overwrite=args.overwrite,
                    api_base=args.api_base,
                    timeout=args.timeout,
                    progress_every=args.progress_every,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return
    if not args.live:
        raise SystemExit("name_in_cheap requires --live")
    print(
        json.dumps(
            run_name_in_cheap(
                overwrite=args.overwrite,
                api_base=args.api_base,
                timeout=args.timeout,
                progress_every=args.progress_every,
            ),
            indent=2,
            sort_keys=True,
        )
    )


def run_catalog() -> None:
    if not SOURCE_ROWS.exists():
        raise SystemExit(f"missing saved raws: {SOURCE_ROWS}")
    letters = {letter.letter_id: letter for letter in _load_dev20()}
    gold = [letters[letter_id] for letter_id in DEV20_IDS]
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()

    mention_preds = _mention_unit_v9(gold)
    cheap_preds = _assembly_preds(CHEAP_DIR / "plain_cheap" / "assembly.jsonl")
    full_preds = _assembly_preds(CHEAP_DIR / "v0924_head" / "assembly.jsonl")
    predictions = {
        "mention_unit_v9": mention_preds,
        "cheap_stack": cheap_preds,
        "v0924": full_preds,
    }
    letter_rows = _letter_catalog(gold, predictions)
    oracular = _oracular_mix(gold, mention_preds, cheap_preds)
    methods = {
        name: _pool_scores(gold, preds) for name, preds in predictions.items()
    }
    methods["oracular_mention_or_cheap"] = oracular["scores"]
    complementary = _complementary(letter_rows)
    decision = _catalog_decision(methods, complementary)
    artifact = {
        "schema_version": "exectv2.mention_unit_cheap_combo.dev20.v1",
        "status": "phase0_complete",
        "phase": "catalog",
        "protocol": PROTOCOL,
        "split": "dev20",
        "row_count": len(gold),
        "model_calls": 0,
        "mention_encoder": MENTION_ENCODER,
        "methods": methods,
        "complementary": complementary,
        "oracular": {
            "headline": oracular["scores"]["clinical_headline_f1"],
            "family": oracular["scores"]["clinical_headline_family_f1"],
            "router_choices": oracular["choices"],
        },
        "letters": letter_rows,
        "decision": decision,
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "claim_boundary": (
            "GPT-5.6 Luna ExECT mention-unit × cheap-stack catalog on frozen "
            "dev20 saved raws. Not holdout, not a selected prompt, and not a "
            "Decision 0050 change."
        ),
    }
    (STUDY_DIR / "comparison.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (STUDY_DIR / "rows.jsonl").open("w", encoding="utf-8") as handle:
        for row in letter_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    REPORT.write_text(_render_catalog_report(artifact), encoding="utf-8")
    print(
        json.dumps(
            {
                "model_calls": 0,
                "decision": decision,
                "headlines": {
                    name: summary["clinical_headline_f1"]
                    for name, summary in methods.items()
                },
                "sf": {
                    name: summary["clinical_headline_family_f1"]["SeizureFrequency"]
                    for name, summary in methods.items()
                },
                "complementary": complementary,
            },
            indent=2,
            sort_keys=True,
        )
    )


def _mention_unit_v9(gold: list[ExectLetter]) -> list[PredictedLetter]:
    saved_by_id = {}
    with SOURCE_ROWS.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            saved_by_id[str(row["letter_id"])] = row
    predictions: list[PredictedLetter] = []
    for letter in gold:
        saved = saved_by_id[letter.letter_id]
        raw = str(saved["methods"][HYBRID_METHOD]["raw_output"])
        parsed = parse_mention_unit_json(raw, method=HYBRID_METHOD)
        if parsed.record is None:
            predictions.append(PredictedLetter(letter_id=letter.letter_id, mentions=()))
            continue
        materialized = materialize_mention_unit(
            letter,
            parsed.record,
            method=HYBRID_METHOD,
            encoder=MENTION_ENCODER,
        )
        predictions.append(materialized.prediction)
    return predictions


def _assembly_preds(path: Path) -> list[PredictedLetter]:
    by_id: dict[str, PredictedLetter] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            letter_id = str(row["letter_id"])
            mentions = []
            for raw in row.get("predicted_mentions") or []:
                attributes = {
                    str(key): str(value)
                    for key, value in (raw.get("attributes") or {}).items()
                    if value is not None
                }
                mentions.append(
                    PredictedMention(
                        entity=str(raw["entity"]),
                        text=str(raw.get("text") or ""),
                        attributes=attributes,
                        evidence=str(raw.get("evidence") or ""),
                    )
                )
            by_id[letter_id] = PredictedLetter(
                letter_id=letter_id, mentions=tuple(mentions)
            )
    return [by_id[letter_id] for letter_id in DEV20_IDS]


def _letter_scores(gold: ExectLetter, prediction: PredictedLetter) -> dict[str, Any]:
    pred_letter = to_exect_letter(prediction)
    scores = {
        "Diagnosis": score_concept_identity(
            [gold], [pred_letter], "Diagnosis"
        ).concept_only,
        "SeizureFrequency": score_frequency_state(
            [gold], [pred_letter]
        ).clinical_headline,
        "Prescription": score_prescription_components(
            [gold], [pred_letter]
        ).clinical_headline,
        "Investigations": score_investigations_components(
            [gold], [pred_letter]
        ).clinical_headline,
    }
    return {
        family: {
            "f1": round(score.f1, 4),
            "precision": round(score.precision, 4),
            "recall": round(score.recall, 4),
            "tp": int(score.tp),
            "fp": int(score.fp),
            "fn": int(score.fn),
            "exact": score.f1 == 1.0,
        }
        for family, score in scores.items()
    }


def _pool_scores(
    gold: list[ExectLetter], predictions: list[PredictedLetter]
) -> dict[str, Any]:
    pred_letters = [to_exect_letter(prediction) for prediction in predictions]
    headline_scores = {
        "Diagnosis": score_concept_identity(gold, pred_letters, "Diagnosis").concept_only,
        "SeizureFrequency": score_frequency_state(gold, pred_letters).clinical_headline,
        "Prescription": score_prescription_components(gold, pred_letters).clinical_headline,
        "Investigations": score_investigations_components(
            gold, pred_letters
        ).clinical_headline,
    }
    return {
        "clinical_headline_f1": round(_aggregate_f1(headline_scores.values()), 4),
        "clinical_headline_family_f1": {
            family: round(score.f1, 4) for family, score in headline_scores.items()
        },
        "empty_gold_sf_extras": _empty_gold_sf_extras(gold, predictions),
        "four_family_letter_exact": sum(
            all(_letter_scores(letter, prediction)[family]["exact"] for family in FAMILIES)
            for letter, prediction in zip(gold, predictions, strict=True)
        ),
    }


def _letter_catalog(
    gold: list[ExectLetter],
    predictions: dict[str, list[PredictedLetter]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, letter in enumerate(gold):
        family_scores = {
            name: _letter_scores(letter, predictions[name][index]) for name in SYSTEMS
        }
        sf_names = {
            name: sorted(
                {
                    mention.text
                    for mention in predictions[name][index].mentions
                    if mention.entity == "SeizureFrequency"
                }
            )
            for name in SYSTEMS
        }
        rows.append(
            {
                "letter_id": letter.letter_id,
                "empty_gold_sf": not bool(letter.entities("SeizureFrequency")),
                "family_scores": family_scores,
                "sf_names": sf_names,
                "winner": {
                    family: _winner(family_scores, family) for family in FAMILIES
                },
            }
        )
    return rows


def _winner(family_scores: dict[str, dict[str, Any]], family: str) -> str:
    ranked = sorted(
        SYSTEMS,
        key=lambda name: (
            family_scores[name][family]["f1"],
            name == "mention_unit_v9",
        ),
        reverse=True,
    )
    best = ranked[0]
    mention_f1 = family_scores["mention_unit_v9"][family]["f1"]
    cheap_f1 = family_scores["cheap_stack"][family]["f1"]
    if mention_f1 == cheap_f1:
        return "tie" if mention_f1 >= family_scores["v0924"][family]["f1"] else best
    return "mention_unit_v9" if mention_f1 > cheap_f1 else "cheap_stack"


def _complementary(letter_rows: list[dict[str, Any]]) -> dict[str, Any]:
    cheap_only: dict[str, list[str]] = {family: [] for family in FAMILIES}
    mention_only: dict[str, list[str]] = {family: [] for family in FAMILIES}
    for row in letter_rows:
        for family in FAMILIES:
            mention = row["family_scores"]["mention_unit_v9"][family]
            cheap = row["family_scores"]["cheap_stack"][family]
            if cheap["f1"] > mention["f1"]:
                cheap_only[family].append(row["letter_id"])
            elif mention["f1"] > cheap["f1"]:
                mention_only[family].append(row["letter_id"])
    return {
        "cheap_only": cheap_only,
        "mention_only": mention_only,
        "sf_cheap_only": cheap_only["SeizureFrequency"],
        "sf_mention_only": mention_only["SeizureFrequency"],
    }


def _oracular_mix(
    gold: list[ExectLetter],
    mention_preds: list[PredictedLetter],
    cheap_preds: list[PredictedLetter],
) -> dict[str, Any]:
    mixed: list[PredictedLetter] = []
    choices: list[dict[str, str]] = []
    for letter, mention, cheap in zip(gold, mention_preds, cheap_preds, strict=True):
        mention_scores = _letter_scores(letter, mention)
        cheap_scores = _letter_scores(letter, cheap)
        selected: list[PredictedMention] = []
        choice: dict[str, str] = {"letter_id": letter.letter_id}
        for family in FAMILIES:
            source = (
                "mention_unit_v9"
                if mention_scores[family]["f1"] >= cheap_scores[family]["f1"]
                else "cheap_stack"
            )
            choice[family] = source
            source_pred = mention if source == "mention_unit_v9" else cheap
            selected.extend(
                mention_item
                for mention_item in source_pred.mentions
                if mention_item.entity == family
            )
        choices.append(choice)
        mixed.append(PredictedLetter(letter_id=letter.letter_id, mentions=tuple(selected)))
    return {"scores": _pool_scores(gold, mixed), "choices": choices}


def _catalog_decision(
    methods: dict[str, dict[str, Any]], complementary: dict[str, Any]
) -> dict[str, Any]:
    cheap_headline = methods["cheap_stack"]["clinical_headline_f1"]
    oracular_headline = methods["oracular_mention_or_cheap"]["clinical_headline_f1"]
    has_complement = bool(
        complementary["sf_cheap_only"] or complementary["sf_mention_only"]
    )
    beats_cheap = oracular_headline > cheap_headline
    if has_complement and beats_cheap:
        status = "answer"
        next_arm = "name_in_cheap"
    else:
        status = "negative_result"
        next_arm = None
    return {
        "status": status,
        "oracular_beats_cheap": beats_cheap,
        "has_sf_complement": has_complement,
        "cheap_headline": cheap_headline,
        "mention_headline": methods["mention_unit_v9"]["clinical_headline_f1"],
        "oracular_headline": oracular_headline,
        "v0924_headline": methods["v0924"]["clinical_headline_f1"],
        "next_live_arm": next_arm,
    }


def _empty_gold_sf_extras(
    gold: list[ExectLetter], predictions: list[PredictedLetter]
) -> dict[str, Any]:
    letters: list[str] = []
    mention_count = 0
    for letter, prediction in zip(gold, predictions, strict=True):
        if letter.entities("SeizureFrequency"):
            continue
        extras = [
            mention
            for mention in prediction.mentions
            if mention.entity == "SeizureFrequency"
        ]
        if extras:
            letters.append(letter.letter_id)
            mention_count += len(extras)
    return {
        "letter_count": len(letters),
        "mention_count": mention_count,
        "letters": letters,
    }


def _aggregate_f1(scores: Iterable[Any]) -> float:
    tp = fp = fn = 0
    for score in scores:
        tp += int(score.tp)
        fp += int(score.fp)
        fn += int(score.fn)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def _provenance() -> dict[str, str]:
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip()
    return {"commit": commit, "dirty_tree": "true" if dirty else "false"}


def run_name_in_cheap(
    *,
    overwrite: bool,
    api_base: str | None,
    timeout: int,
    progress_every: int,
) -> dict[str, Any]:
    letters = _letters()
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    control = _replay_arm(
        slug="v0924_head",
        prompt_version=CONTROL_VERSION,
        raws=_raws(CONTROL_STRUCTURED, letters),
        letters=letters,
        call_mode="saved_structured_no_call",
        study_dir=STUDY_DIR,
    )
    cheap = _replay_arm(
        slug="plain_cheap",
        prompt_version=CHEAP_VERSION,
        raws=_raws(CHEAP_STRUCTURED, letters),
        letters=letters,
        call_mode="saved_structured_no_call",
        study_dir=STUDY_DIR,
    )
    candidate = _run_candidate(
        "name_in_cheap",
        letters,
        overwrite=overwrite,
        api_base=api_base,
        timeout=timeout,
        progress_every=progress_every,
        study_dir=STUDY_DIR,
        arms=NAME_IN_CHEAP_ARMS,
    )
    versus_cheap = _compare_pair(cheap, candidate, letters)
    versus_control = _compare_pair(control, candidate, letters)
    hybrid = versus_cheap["surfaces"]["hybrid"]
    quality = candidate["summary"]["quality"]
    verdict = decide_arm(hybrid, quality)
    named = _name_in_cheap_named(
        STUDY_DIR / "name_in_cheap" / "assembly.jsonl",
        STUDY_DIR / "plain_cheap" / "assembly.jsonl",
    )
    if quality["parse"] or quality["schema"]:
        status = "revise"
    elif named["cluster_recovered"] and not named["extras_rose"]:
        status = "answer"
    elif not named["cluster_recovered"] and not named["extras_rose"]:
        status = "negative_result"
    else:
        status = "revise"
    previous = {}
    if (STUDY_DIR / "comparison.json").exists():
        previous = json.loads((STUDY_DIR / "comparison.json").read_text(encoding="utf-8"))
    artifact = {
        **previous,
        "status": f"name_in_cheap_{status}",
        "phase": "name_in_cheap",
        "model_calls": candidate["summary"].get("new_model_calls", 20),
        "name_in_cheap": {
            "prompt_version": COMBO_VERSION,
            "verdict": verdict,
            "status": status,
            "versus_cheap": versus_cheap,
            "versus_v0924": versus_control,
            "named_outcomes": named,
            "quality": quality,
            "failures": topology_failures(hybrid),
            "changed_versus_cheap": _changed_rows(cheap, candidate, letters),
        },
        "finished_utc": datetime.now(UTC).isoformat(),
        "name_in_cheap_started_utc": started,
        "provenance": _provenance(),
    }
    (STUDY_DIR / "comparison.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _append_name_in_cheap_report(artifact)
    return {
        "status": status,
        "verdict": verdict,
        "named_outcomes": named,
        "headline_delta": hybrid.get("headline_f1_delta"),
        "sf_delta": (hybrid.get("family_f1_delta") or {}).get("SeizureFrequency"),
        "quality": quality,
    }


def _sf_names_by_letter(path: Path) -> dict[str, list[str]]:
    names: dict[str, list[str]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            names[str(row["letter_id"])] = sorted(
                {
                    str(mention.get("text") or "")
                    for mention in row.get("predicted_mentions") or []
                    if mention.get("entity") == "SeizureFrequency"
                }
            )
    return names


def _name_in_cheap_named(candidate_path: Path, cheap_path: Path) -> dict[str, Any]:
    names = _sf_names_by_letter(candidate_path)
    cheap_names = _sf_names_by_letter(cheap_path)
    cluster = any(
        "cluster" in name.casefold() for name in names.get("EA0009", [])
    )
    empty_gold = ("EA0016", "EA0074")
    extras = {
        letter_id: names.get(letter_id, [])
        for letter_id in empty_gold
        if names.get(letter_id)
    }
    cheap_extras = {
        letter_id: cheap_names.get(letter_id, [])
        for letter_id in empty_gold
        if cheap_names.get(letter_id)
    }
    return {
        "cluster_recovered": cluster,
        "ea0009_names": names.get("EA0009", []),
        "empty_gold_sf_letters": extras,
        "cheap_empty_gold_sf_letters": cheap_extras,
        "extras_rose": sum(len(v) for v in extras.values())
        > sum(len(v) for v in cheap_extras.values()),
    }


def verify_scaffold_payload() -> dict[str, Any]:
    letter = ExectLetter(
        letter_id="EA0002",
        note_text="She takes lamotrigine 100 mg daily. She has two seizures a week.",
    )
    _verify_prompt_contracts(letter)
    if mention_unit_prompt_version() != MENTION_UNIT_PROMPT_VERSION:
        raise RuntimeError("default prompt identity drifted")
    cheap = json.loads(
        structured.build_prompt_input(
            letter,
            prompt_version=structured.PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES,
        )
    )
    for method in (LLM_METHOD, HYBRID_METHOD):
        frozen = json.loads(build_mention_unit_prompt(letter, method=method))
        payload = json.loads(
            build_mention_unit_prompt(letter, method=method, combo_arm="scaffold")
        )
        if payload["task"] != frozen["task"]:
            raise RuntimeError(f"{method} scaffold rewrote the frozen task")
        if payload["selection_cues"] != frozen["selection_cues"]:
            raise RuntimeError(f"{method} scaffold rewrote the frozen cues")
        if payload["output_schema"] != frozen["output_schema"]:
            raise RuntimeError(f"{method} scaffold rewrote the frozen schema")
        if payload.get("suggested_evidence") != cheap["suggested_evidence"]:
            raise RuntimeError(f"{method} scaffold rows drifted from cheap stack")
        serialized = json.dumps(
            {key: value for key, value in payload.items() if key != "letter_text"}
        ).lower()
        for term in _SCAFFOLD_BANNED:
            if term in serialized:
                raise RuntimeError(f"{method} scaffold leaked {term!r}")
        messages = MentionUnitExtractor(method=method).render_messages(
            prompt_input_json=build_mention_unit_prompt(
                letter, method=method, combo_arm="scaffold"
            )
        )
        if messages[0] != {"role": "system", "content": SYSTEM_MESSAGE}:
            raise RuntimeError("system message drifted")
    return {
        "ok": True,
        "arm": "scaffold",
        "prompt_version": SCAFFOLD_VERSION,
        "default_prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "protocol": PROTOCOL,
        "model_calls": 0,
    }


def verify_form_guide_payload() -> dict[str, Any]:
    letter = ExectLetter(
        letter_id="EA0002",
        note_text="She takes lamotrigine 100 mg daily. She has two seizures a week.",
    )
    _verify_prompt_contracts(letter)
    if mention_unit_prompt_version() != MENTION_UNIT_PROMPT_VERSION:
        raise RuntimeError("default prompt identity drifted")
    if mention_unit_prompt_version(combo_arm="form_guide") != FORM_GUIDE_VERSION:
        raise RuntimeError("form_guide identity drifted")
    frozen_llm = json.loads(build_mention_unit_prompt(letter, method=LLM_METHOD))
    frozen_hybrid = json.loads(build_mention_unit_prompt(letter, method=HYBRID_METHOD))
    llm = json.loads(
        build_mention_unit_prompt(letter, method=LLM_METHOD, combo_arm="form_guide")
    )
    hybrid = json.loads(
        build_mention_unit_prompt(letter, method=HYBRID_METHOD, combo_arm="form_guide")
    )
    if "form_table" in frozen_hybrid:
        raise RuntimeError("default hybrid already has the form table")
    if hybrid["form_table"] != frozen_llm["form_table"]:
        raise RuntimeError("form_guide hybrid table drifted from llm")
    if len(hybrid["form_table"]) != 8:
        raise RuntimeError("form_guide hybrid table is not the eight-row llm table")
    if hybrid["output_schema"] != frozen_hybrid["output_schema"]:
        raise RuntimeError("form_guide rewrote the hybrid schema")
    if "count" in json.dumps(hybrid["output_schema"]).lower():
        raise RuntimeError("form_guide added coding fields to the hybrid schema")
    if llm["task"] != frozen_llm["task"] or llm["output_schema"] != frozen_llm["output_schema"]:
        raise RuntimeError("form_guide rewrote the frozen llm payload")
    if "use the form table" not in str(hybrid["task"]).lower():
        raise RuntimeError("form_guide hybrid task does not point at the form table")
    serialized = json.dumps(
        {key: value for key, value in hybrid.items() if key != "letter_text"}
    ).lower()
    for term in _FORM_GUIDE_BANNED:
        if term in serialized:
            raise RuntimeError(f"form_guide leaked {term!r}")
    messages = MentionUnitExtractor(method=HYBRID_METHOD).render_messages(
        prompt_input_json=build_mention_unit_prompt(
            letter, method=HYBRID_METHOD, combo_arm="form_guide"
        )
    )
    if messages[0] != {"role": "system", "content": SYSTEM_MESSAGE}:
        raise RuntimeError("system message drifted")
    return {
        "ok": True,
        "arm": "form_guide",
        "prompt_version": FORM_GUIDE_VERSION,
        "default_prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "protocol": PROTOCOL,
        "model_calls": 0,
    }


def run_scaffold(
    *,
    overwrite: bool,
    api_base: str | None,
    timeout: int,
    progress_every: int,
) -> dict[str, Any]:
    verify_scaffold_payload()
    load_dotenv(ROOT / ".env", override=False)
    _require_api_key()
    if not SOURCE_ROWS.exists():
        raise SystemExit(f"missing saved raws: {SOURCE_ROWS}")
    letters = _load_dev20()
    arm_dir = STUDY_DIR / "scaffold"
    rows_path = arm_dir / "rows.jsonl"
    if rows_path.exists() and not overwrite:
        raise SystemExit(f"arm exists; pass --overwrite: {arm_dir}")
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    saved_rows = _load_saved_mention_rows()
    v9_hybrid = _mention_unit_v9(letters)
    v2_llm = _saved_method_predictions(letters, saved_rows, LLM_METHOD)
    candidate, rows, operational = _run_combo_live(
        letters,
        combo_arm="scaffold",
        api_base=api_base,
        timeout=timeout,
        progress_every=progress_every,
    )
    summaries = {
        "mention_unit_v2_llm": _score_method(letters, v2_llm),
        "mention_unit_v9_hybrid": _pool_scores(letters, v9_hybrid),
        LLM_METHOD: _score_method(letters, candidate[LLM_METHOD]),
        HYBRID_METHOD: _pool_scores(letters, candidate[HYBRID_METHOD]),
    }
    wording = _sf_wording_versus_v2(letters, rows, saved_rows)
    extras = _scaffold_extras(letters, candidate, v2_llm, v9_hybrid)
    leftover = _scaffold_leftover(summaries, letters, candidate, v9_hybrid)
    stop = _scaffold_stop(letters, rows, extras, wording, leftover)
    payload_chars = _scaffold_payload_chars(letters)
    arm_dir.mkdir(parents=True, exist_ok=True)
    with rows_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    previous = {}
    if (STUDY_DIR / "comparison.json").exists():
        previous = json.loads((STUDY_DIR / "comparison.json").read_text(encoding="utf-8"))
    artifact = {
        **previous,
        "status": f"scaffold_{stop['verdict']}",
        "phase": "scaffold",
        "model_calls": operational[LLM_METHOD]["calls"] + operational[HYBRID_METHOD]["calls"],
        "scaffold": {
            "prompt_version": SCAFFOLD_VERSION,
            "encoder": MENTION_ENCODER,
            "status": stop["verdict"],
            "methods": summaries,
            "operational": operational,
            "gold_sf_wording": wording,
            "empty_gold_sf_extras": extras,
            "leftover": leftover,
            "stop_checks": stop,
            "payload_characters": payload_chars,
            "quality": {
                "parse": operational[LLM_METHOD]["rows_with_blocking_parse_failure"]
                + operational[HYBRID_METHOD]["rows_with_blocking_parse_failure"],
                "schema": operational[LLM_METHOD]["rows_with_forbidden_fields"]
                + operational[HYBRID_METHOD]["rows_with_forbidden_fields"],
            },
        },
        "scaffold_started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "claim_boundary": (
            "GPT-5.6 Luna ExECT mention-unit × cheap-stack scaffold graft on "
            "frozen dev20. Study-only. Not holdout, not a selected prompt, "
            "and not a Decision 0050 change."
        ),
    }
    (STUDY_DIR / "comparison.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _append_scaffold_report(artifact)
    hybrid = summaries[HYBRID_METHOD]
    control = summaries["mention_unit_v9_hybrid"]
    return {
        "status": stop["verdict"],
        "headline_delta": round(
            hybrid["clinical_headline_f1"] - control["clinical_headline_f1"], 4
        ),
        "sf_delta": round(
            hybrid["clinical_headline_family_f1"]["SeizureFrequency"]
            - control["clinical_headline_family_f1"]["SeizureFrequency"],
            4,
        ),
        "gold_sf_wording": wording,
        "empty_gold_sf_extras": extras,
        "quality": artifact["scaffold"]["quality"],
        "stop_checks": stop,
    }


def _load_saved_mention_rows() -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    with SOURCE_ROWS.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            rows[str(row["letter_id"])] = row
    return rows


def _saved_method_predictions(
    letters: list[ExectLetter],
    saved_rows: dict[str, dict[str, Any]],
    method: str,
) -> list[PredictedLetter]:
    predictions: list[PredictedLetter] = []
    for letter in letters:
        raw = str(saved_rows[letter.letter_id]["methods"][method]["raw_output"])
        parsed = parse_mention_unit_json(raw, method=method)
        if parsed.record is None:
            predictions.append(PredictedLetter(letter_id=letter.letter_id, mentions=()))
            continue
        materialized = materialize_mention_unit(letter, parsed.record, method=method)
        predictions.append(materialized.prediction)
    return predictions


def _run_combo_live(
    letters: list[ExectLetter],
    *,
    combo_arm: str,
    api_base: str | None,
    timeout: int,
    progress_every: int,
) -> tuple[dict[str, list[PredictedLetter]], list[dict[str, Any]], dict[str, Any]]:
    candidate: dict[str, list[PredictedLetter]] = {LLM_METHOD: [], HYBRID_METHOD: []}
    operational: dict[str, dict[str, int]] = {
        method: {
            "calls": 0,
            "rows_with_blocking_parse_failure": 0,
            "parse_notes": 0,
            "items": 0,
            "evidence_invalid": 0,
            "rows_with_forbidden_fields": 0,
        }
        for method in (LLM_METHOD, HYBRID_METHOD)
    }
    extractors = {
        method: MentionUnitExtractor(method=method) for method in (LLM_METHOD, HYBRID_METHOD)
    }
    for method in (LLM_METHOD, HYBRID_METHOD):
        dspy.configure(
            lm=build_dspy_lm(
                MENTION_UNIT_MODEL,
                temperature=1.0,
                max_tokens=2400,
                cache=False,
                api_base=api_base,
                timeout=timeout,
            )
        )
        extractors[method]._configured = True
    rows: list[dict[str, Any]] = []
    for index, letter in enumerate(letters, start=1):
        row: dict[str, Any] = {
            "letter_id": letter.letter_id,
            "split": "dev20",
            "model": MENTION_UNIT_MODEL,
            "prompt_version": COMBO_ARM_VERSIONS[combo_arm],
            "combo_arm": combo_arm,
            "encoder": MENTION_ENCODER,
            "methods": {},
        }
        for method in (LLM_METHOD, HYBRID_METHOD):
            prompt = build_mention_unit_prompt(
                letter, method=method, combo_arm=combo_arm
            )
            raw_output = ""
            call_error: str | None = None
            try:
                prediction = extractors[method](prompt_input_json=prompt)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover - provider behavior.
                call_error = f"{type(exc).__name__}: {exc}"
            parsed = parse_mention_unit_json(raw_output, method=method)
            stats = operational[method]
            stats["calls"] += 1
            stats["parse_notes"] += len(parsed.errors)
            stats["items"] += len(parsed.record.items) if parsed.record is not None else 0
            stats["rows_with_blocking_parse_failure"] += int(
                parsed.record is None
                or any(
                    str(error).startswith(("invalid_json:", "schema_validation_error:", "not_run"))
                    for error in parsed.errors
                )
            )
            stats["rows_with_forbidden_fields"] += int(bool(parsed.forbidden_fields))
            if parsed.record is None:
                materialized = _empty_materialization(letter, parsed.errors)
            elif method == HYBRID_METHOD:
                materialized = materialize_mention_unit(
                    letter,
                    parsed.record,
                    method=method,
                    encoder=MENTION_ENCODER,
                )
            else:
                materialized = materialize_mention_unit(
                    letter, parsed.record, method=method
                )
            candidate[method].append(materialized.prediction)
            stats["evidence_invalid"] += materialized.evidence_invalid
            row["methods"][method] = {
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "prompt_characters": len(prompt),
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parsed.errors,
                "forbidden_model_fields": parsed.forbidden_fields,
                "semantic_facts": materialized.semantic_facts,
                "rule_trace": materialized.rule_trace,
                "warnings": materialized.warnings,
                "evidence_invalid": materialized.evidence_invalid,
                "prediction": materialized.prediction.model_dump(mode="json"),
            }
        rows.append(row)
        if index % max(progress_every, 1) == 0:
            print(f"{combo_arm}: completed {index}/{len(letters)} rows", flush=True)
    return candidate, rows, operational


def _sf_wording_versus_v2(
    letters: list[ExectLetter],
    rows: list[dict[str, Any]],
    saved_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    by_id = {row["letter_id"]: row for row in rows}
    counts: dict[str, dict[str, int]] = {}
    for method in (LLM_METHOD, HYBRID_METHOD):
        candidate_exact = 0
        v2_exact = 0
        gold_units_n = 0
        for letter in letters:
            gold_units = [
                {
                    "text": annotation.text,
                    "raw_text": annotation.raw_text or annotation.text,
                }
                for annotation in letter.entities("SeizureFrequency")
            ]
            gold_units_n += len(gold_units)
            candidate_exact += _span_matches(
                gold_units,
                _carrier_texts(by_id[letter.letter_id]["methods"][method], "clinical_name"),
            )["exact"]
            v2_exact += _span_matches(
                gold_units,
                _carrier_texts(saved_rows[letter.letter_id]["methods"][method], "clinical_name"),
            )["exact"]
        counts[method] = {
            "gold_units": gold_units_n,
            "candidate": candidate_exact,
            "v2": v2_exact,
        }
    return counts


def _scaffold_extras(
    letters: list[ExectLetter],
    candidate: dict[str, list[PredictedLetter]],
    v2_llm: list[PredictedLetter],
    v9_hybrid: list[PredictedLetter],
) -> dict[str, Any]:
    return {
        LLM_METHOD: {
            "candidate": _empty_gold_sf_extras(letters, candidate[LLM_METHOD]),
            "control": _empty_gold_sf_extras(letters, v2_llm),
        },
        HYBRID_METHOD: {
            "candidate": _empty_gold_sf_extras(letters, candidate[HYBRID_METHOD]),
            "control": _empty_gold_sf_extras(letters, v9_hybrid),
        },
    }


def _scaffold_leftover(
    summaries: dict[str, Any],
    letters: list[ExectLetter],
    candidate: dict[str, list[PredictedLetter]],
    v9_hybrid: list[PredictedLetter],
) -> dict[str, Any]:
    hybrid = summaries[HYBRID_METHOD]
    control = summaries["mention_unit_v9_hybrid"]
    candidate_sf = hybrid["clinical_headline_family_f1"]["SeizureFrequency"]
    control_sf = control["clinical_headline_family_f1"]["SeizureFrequency"]
    cheap_only = ("EA0008", "EA0011", "EA0047", "EA0131")
    letter_moves = []
    for letter, cand, control_pred in zip(
        letters, candidate[HYBRID_METHOD], v9_hybrid, strict=True
    ):
        if letter.letter_id not in cheap_only:
            continue
        cand_f1 = _letter_scores(letter, cand)["SeizureFrequency"]["f1"]
        control_f1 = _letter_scores(letter, control_pred)["SeizureFrequency"]["f1"]
        letter_moves.append(
            {
                "letter_id": letter.letter_id,
                "candidate_f1": cand_f1,
                "control_f1": control_f1,
                "improved": cand_f1 > control_f1,
            }
        )
    return {
        "candidate_sf": candidate_sf,
        "control_sf": control_sf,
        "sf_delta": round(candidate_sf - control_sf, 4),
        "moved_toward_cheap": candidate_sf > control_sf,
        "cheap_only_letters": letter_moves,
    }


def _scaffold_stop(
    letters: list[ExectLetter],
    rows: list[dict[str, Any]],
    extras: dict[str, Any],
    wording: dict[str, Any],
    leftover: dict[str, Any],
) -> dict[str, Any]:
    extras_rose = any(
        extras[method]["candidate"]["mention_count"]
        > extras[method]["control"]["mention_count"]
        for method in (LLM_METHOD, HYBRID_METHOD)
    )
    exact_fell = any(
        wording[method]["candidate"] < wording[method]["v2"]
        for method in (LLM_METHOD, HYBRID_METHOD)
    )
    nontargets = [
        hit
        for row in rows
        for method in (LLM_METHOD, HYBRID_METHOD)
        for hit in _nontarget_mentions(
            [PredictedLetter.model_validate(row["methods"][method]["prediction"])]
        )
    ]
    growth = _hybrid_growth(letters, rows)
    parse_fail = any(
        row["methods"][method]["prediction"]["mentions"] == []
        and any(
            str(error).startswith(("invalid_json:", "schema_validation_error:", "not_run"))
            for error in row["methods"][method]["parse_errors"]
        )
        for row in rows
        for method in (LLM_METHOD, HYBRID_METHOD)
    )
    revise = bool(extras_rose or exact_fell or nontargets or growth or parse_fail)
    if revise:
        verdict = "revise"
    elif leftover["moved_toward_cheap"]:
        verdict = "answer"
    else:
        verdict = "negative_result"
    return {
        "empty_gold_sf_extras_rose": extras_rose,
        "gold_sf_exact_fell": exact_fell,
        "nontarget_mentions": nontargets,
        "hybrid_growth_from_unused_letter": growth,
        "parse_or_schema_failure": parse_fail,
        "leftover_moved": leftover["moved_toward_cheap"],
        "verdict": verdict,
    }


def _scaffold_payload_chars(letters: list[ExectLetter]) -> dict[str, Any]:
    frozen: list[int] = []
    candidate: list[int] = []
    ea0133 = {}
    for letter in letters:
        frozen_n = len(build_mention_unit_prompt(letter, method=HYBRID_METHOD))
        cand_n = len(
            build_mention_unit_prompt(letter, method=HYBRID_METHOD, combo_arm="scaffold")
        )
        frozen.append(frozen_n)
        candidate.append(cand_n)
        if letter.letter_id == "EA0133":
            ea0133 = {"frozen": frozen_n, "scaffold": cand_n, "delta": cand_n - frozen_n}
    return {
        "hybrid_mean_frozen": round(sum(frozen) / len(frozen)),
        "hybrid_mean_scaffold": round(sum(candidate) / len(candidate)),
        "ea0133": ea0133,
    }


def _append_scaffold_report(artifact: dict[str, Any]) -> None:
    block = artifact["scaffold"]
    leftover = block["leftover"]
    wording = block["gold_sf_wording"]
    extras = block["empty_gold_sf_extras"]
    hybrid = block["methods"][HYBRID_METHOD]
    control = block["methods"]["mention_unit_v9_hybrid"]
    lines = [
        "",
        "## Live arm `scaffold`",
        "",
        f"Status: **{block['status']}**.",
        f"Hybrid headline {hybrid['clinical_headline_f1']:.4f} versus leftover-form "
        f"v9 {control['clinical_headline_f1']:.4f}.",
        f"SF {leftover['candidate_sf']:.4f} versus v9 {leftover['control_sf']:.4f} "
        f"(Δ {leftover['sf_delta']:+.4f}).",
        f"Gold SF wording llm {wording[LLM_METHOD]['v2']} → "
        f"{wording[LLM_METHOD]['candidate']}; hybrid "
        f"{wording[HYBRID_METHOD]['v2']} → {wording[HYBRID_METHOD]['candidate']}.",
        f"Empty-gold SF extras llm "
        f"{extras[LLM_METHOD]['control']['mention_count']} → "
        f"{extras[LLM_METHOD]['candidate']['mention_count']}; hybrid "
        f"{extras[HYBRID_METHOD]['control']['mention_count']} → "
        f"{extras[HYBRID_METHOD]['candidate']['mention_count']}.",
        f"parse={block['quality']['parse']} schema={block['quality']['schema']}.",
        "",
    ]
    current = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    REPORT.write_text(
        _replace_report_section(current, "## Live arm `scaffold`", "\n".join(lines)),
        encoding="utf-8",
    )


def _replace_report_section(current: str, heading: str, block: str) -> str:
    if heading not in current:
        return current.rstrip() + "\n" + block
    head, _sep, tail = current.partition(heading)
    next_heading = tail.find("\n## ")
    rest = tail[next_heading:] if next_heading >= 0 else ""
    return head.rstrip() + "\n" + block.rstrip() + "\n" + rest


def run_form_guide(
    *,
    overwrite: bool,
    api_base: str | None,
    timeout: int,
    progress_every: int,
) -> dict[str, Any]:
    verify_form_guide_payload()
    load_dotenv(ROOT / ".env", override=False)
    _require_api_key()
    if not SOURCE_ROWS.exists():
        raise SystemExit(f"missing saved raws: {SOURCE_ROWS}")
    letters = _load_dev20()
    arm_dir = STUDY_DIR / "form_guide"
    rows_path = arm_dir / "rows.jsonl"
    if rows_path.exists() and not overwrite:
        raise SystemExit(f"arm exists; pass --overwrite: {arm_dir}")
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    saved_rows = _load_saved_mention_rows()
    v9_hybrid = _mention_unit_v9(letters)
    v2_llm = _saved_method_predictions(letters, saved_rows, LLM_METHOD)
    candidate, rows, operational = _run_combo_live(
        letters,
        combo_arm="form_guide",
        api_base=api_base,
        timeout=timeout,
        progress_every=progress_every,
    )
    summaries = {
        "mention_unit_v2_llm": _score_method(letters, v2_llm),
        "mention_unit_v9_hybrid": _pool_scores(letters, v9_hybrid),
        LLM_METHOD: _score_method(letters, candidate[LLM_METHOD]),
        HYBRID_METHOD: _pool_scores(letters, candidate[HYBRID_METHOD]),
    }
    wording = _sf_wording_versus_v2(letters, rows, saved_rows)
    extras = _scaffold_extras(letters, candidate, v2_llm, v9_hybrid)
    leftover = _form_guide_leftover(summaries, candidate, v9_hybrid)
    stop = _form_guide_stop(letters, rows, extras, wording, leftover)
    payload_chars = _form_guide_payload_chars(letters)
    arm_dir.mkdir(parents=True, exist_ok=True)
    with rows_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    previous = {}
    if (STUDY_DIR / "comparison.json").exists():
        previous = json.loads((STUDY_DIR / "comparison.json").read_text(encoding="utf-8"))
    artifact = {
        **previous,
        "status": f"form_guide_{stop['verdict']}",
        "phase": "form_guide",
        "model_calls": operational[LLM_METHOD]["calls"] + operational[HYBRID_METHOD]["calls"],
        "form_guide": {
            "prompt_version": FORM_GUIDE_VERSION,
            "encoder": FORM_GUIDE_ENCODER,
            "status": stop["verdict"],
            "methods": summaries,
            "operational": operational,
            "gold_sf_wording": wording,
            "empty_gold_sf_extras": extras,
            "leftover": leftover,
            "stop_checks": stop,
            "payload_characters": payload_chars,
            "quality": {
                "parse": operational[LLM_METHOD]["rows_with_blocking_parse_failure"]
                + operational[HYBRID_METHOD]["rows_with_blocking_parse_failure"],
                "schema": operational[LLM_METHOD]["rows_with_forbidden_fields"]
                + operational[HYBRID_METHOD]["rows_with_forbidden_fields"],
            },
        },
        "form_guide_started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "claim_boundary": (
            "GPT-5.6 Luna ExECT mention-unit × cheap-stack form-guide graft on "
            "frozen dev20. Study-only. Not holdout, not a selected prompt, "
            "and not a Decision 0050 change."
        ),
    }
    (STUDY_DIR / "comparison.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _append_form_guide_report(artifact)
    hybrid = summaries[HYBRID_METHOD]
    control = summaries["mention_unit_v9_hybrid"]
    return {
        "status": stop["verdict"],
        "headline_delta": round(
            hybrid["clinical_headline_f1"] - control["clinical_headline_f1"], 4
        ),
        "sf_delta": round(
            hybrid["clinical_headline_family_f1"]["SeizureFrequency"]
            - control["clinical_headline_family_f1"]["SeizureFrequency"],
            4,
        ),
        "gold_sf_wording": wording,
        "empty_gold_sf_extras": extras,
        "leftover": leftover,
        "quality": artifact["form_guide"]["quality"],
        "stop_checks": stop,
    }


def _form_guide_leftover(
    summaries: dict[str, Any],
    candidate: dict[str, list[PredictedLetter]],
    v9_hybrid: list[PredictedLetter],
) -> dict[str, Any]:
    hybrid = summaries[HYBRID_METHOD]
    control = summaries["mention_unit_v9_hybrid"]
    candidate_form = _form_census(candidate[HYBRID_METHOD])
    control_form = _form_census(v9_hybrid)
    candidate_sf = hybrid["clinical_headline_family_f1"]["SeizureFrequency"]
    control_sf = control["clinical_headline_family_f1"]["SeizureFrequency"]
    headline_up = hybrid["clinical_headline_f1"] > control["clinical_headline_f1"]
    sf_up = candidate_sf > control_sf
    form_up = candidate_form["sf_with_count"] > control_form["sf_with_count"]
    return {
        "candidate_headline": hybrid["clinical_headline_f1"],
        "control_headline": control["clinical_headline_f1"],
        "headline_delta": round(
            hybrid["clinical_headline_f1"] - control["clinical_headline_f1"], 4
        ),
        "candidate_sf": candidate_sf,
        "control_sf": control_sf,
        "sf_delta": round(candidate_sf - control_sf, 4),
        "candidate_form": candidate_form,
        "control_form": control_form,
        "moved": headline_up or sf_up or form_up,
    }


def _form_guide_stop(
    letters: list[ExectLetter],
    rows: list[dict[str, Any]],
    extras: dict[str, Any],
    wording: dict[str, Any],
    leftover: dict[str, Any],
) -> dict[str, Any]:
    extras_rose = any(
        extras[method]["candidate"]["mention_count"]
        > extras[method]["control"]["mention_count"]
        for method in (LLM_METHOD, HYBRID_METHOD)
    )
    exact_fell = any(
        wording[method]["candidate"] < wording[method]["v2"]
        for method in (LLM_METHOD, HYBRID_METHOD)
    )
    nontargets = [
        hit
        for row in rows
        for method in (LLM_METHOD, HYBRID_METHOD)
        for hit in _nontarget_mentions(
            [PredictedLetter.model_validate(row["methods"][method]["prediction"])]
        )
    ]
    growth = _hybrid_growth(letters, rows)
    parse_fail = any(
        row["methods"][method]["prediction"]["mentions"] == []
        and any(
            str(error).startswith(("invalid_json:", "schema_validation_error:", "not_run"))
            for error in row["methods"][method]["parse_errors"]
        )
        for row in rows
        for method in (LLM_METHOD, HYBRID_METHOD)
    )
    revise = bool(extras_rose or exact_fell or nontargets or growth or parse_fail)
    if revise:
        verdict = "revise"
    elif leftover["moved"]:
        verdict = "answer"
    else:
        verdict = "negative_result"
    return {
        "empty_gold_sf_extras_rose": extras_rose,
        "gold_sf_exact_fell": exact_fell,
        "nontarget_mentions": nontargets,
        "hybrid_growth_from_unused_letter": growth,
        "parse_or_schema_failure": parse_fail,
        "leftover_moved": leftover["moved"],
        "verdict": verdict,
    }


def _form_guide_payload_chars(letters: list[ExectLetter]) -> dict[str, Any]:
    frozen: list[int] = []
    candidate: list[int] = []
    ea0133 = {}
    for letter in letters:
        frozen_n = len(build_mention_unit_prompt(letter, method=HYBRID_METHOD))
        cand_n = len(
            build_mention_unit_prompt(letter, method=HYBRID_METHOD, combo_arm="form_guide")
        )
        frozen.append(frozen_n)
        candidate.append(cand_n)
        if letter.letter_id == "EA0133":
            ea0133 = {
                "frozen": frozen_n,
                "form_guide": cand_n,
                "delta": cand_n - frozen_n,
            }
    return {
        "hybrid_mean_frozen": round(sum(frozen) / len(frozen)),
        "hybrid_mean_form_guide": round(sum(candidate) / len(candidate)),
        "ea0133": ea0133,
    }


def _append_form_guide_report(artifact: dict[str, Any]) -> None:
    block = artifact["form_guide"]
    leftover = block["leftover"]
    wording = block["gold_sf_wording"]
    extras = block["empty_gold_sf_extras"]
    hybrid = block["methods"][HYBRID_METHOD]
    control = block["methods"]["mention_unit_v9_hybrid"]
    lines = [
        "",
        "## Live arm `form_guide`",
        "",
        f"Status: **{block['status']}**.",
        f"Hybrid headline {hybrid['clinical_headline_f1']:.4f} versus leftover-form "
        f"v9 {control['clinical_headline_f1']:.4f} "
        f"(Δ {leftover['headline_delta']:+.4f}).",
        f"SF {leftover['candidate_sf']:.4f} versus v9 {leftover['control_sf']:.4f} "
        f"(Δ {leftover['sf_delta']:+.4f}).",
        f"SF-with-count {leftover['candidate_form']['sf_with_count']} versus v9 "
        f"{leftover['control_form']['sf_with_count']}.",
        f"Gold SF wording llm {wording[LLM_METHOD]['v2']} → "
        f"{wording[LLM_METHOD]['candidate']}; hybrid "
        f"{wording[HYBRID_METHOD]['v2']} → {wording[HYBRID_METHOD]['candidate']}.",
        f"Empty-gold SF extras llm "
        f"{extras[LLM_METHOD]['control']['mention_count']} → "
        f"{extras[LLM_METHOD]['candidate']['mention_count']}; hybrid "
        f"{extras[HYBRID_METHOD]['control']['mention_count']} → "
        f"{extras[HYBRID_METHOD]['candidate']['mention_count']}.",
        f"parse={block['quality']['parse']} schema={block['quality']['schema']}.",
        "",
    ]
    current = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    if "## Live arm `form_guide`" in current:
        head, _sep, _tail = current.partition("## Live arm `form_guide`")
        current = head.rstrip() + "\n"
    REPORT.write_text(current + "\n".join(lines), encoding="utf-8")


def _append_name_in_cheap_report(artifact: dict[str, Any]) -> None:
    block = artifact["name_in_cheap"]
    named = block["named_outcomes"]
    hybrid = block["versus_cheap"]["surfaces"]["hybrid"]
    lines = [
        "",
        "## Live arm `name_in_cheap`",
        "",
        f"Status: **{block['status']}**. Cheap-stack further-prune verdict "
        f"`{block['verdict']}`.",
        f"EA0009 names: {', '.join(named['ea0009_names']) or 'none'}.",
        f"Cluster recovered: {named['cluster_recovered']}.",
        f"Empty-gold extras: {named['empty_gold_sf_letters'] or 'none'}.",
        f"Headline Δ versus cheap: {hybrid.get('headline_f1_delta')}.",
        f"SF Δ versus cheap: {(hybrid.get('family_f1_delta') or {}).get('SeizureFrequency')}.",
        "",
    ]
    current = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    if "## Live arm `name_in_cheap`" in current:
        head, _sep, _tail = current.partition("## Live arm `name_in_cheap`")
        current = head.rstrip() + "\n"
    REPORT.write_text(current + "\n".join(lines), encoding="utf-8")


def _render_catalog_report(artifact: dict[str, Any]) -> str:
    methods = artifact["methods"]
    complementary = artifact["complementary"]
    decision = artifact["decision"]
    lines = [
        "# ExECT mention-unit × cheap-stack combination — GPT-5.6 Luna `dev20`",
        "",
        "Date: 2026-08-17",
        f"Status: phase 0 **{decision['status']}**; `scaffold` deferred; "
        + (
            f"first live arm `{decision['next_live_arm']}`"
            if decision["next_live_arm"]
            else "live arms blocked"
        ),
        f"Protocol: [combination]({Path(PROTOCOL).name})",
        "Parents: [mention-unit v2](mention_unit_v2_fork_a_luna_dev20_2026-08-16.md); "
        "[cheap-stack plain](v0924_cheap_stack_plain_luna_dev20_2026-08-16.md); "
        "[negation v9](mention_unit_v2_negation_luna_dev20_2026-08-17.md)",
        "",
        "## Executive result",
        "",
        "No-call catalog on saved mention-unit v2 hybrid raws through leftover-form "
        "negation v9, saved cheap-stack plain, and saved `v0.9.24`.",
        "",
        "| System | Headline | SF | Dx | Rx | Ix | Exact |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    labels = {
        "mention_unit_v9": "mention-unit v9",
        "cheap_stack": "cheap stack",
        "v0924": "`v0.9.24`",
        "oracular_mention_or_cheap": "oracular mix",
    }
    for key, label in labels.items():
        row = methods[key]
        family = row["clinical_headline_family_f1"]
        exact = row.get("four_family_letter_exact", "—")
        lines.append(
            f"| {label} | {row['clinical_headline_f1']:.4f} | "
            f"{family['SeizureFrequency']:.4f} | {family['Diagnosis']:.4f} | "
            f"{family['Prescription']:.4f} | {family['Investigations']:.4f} | "
            f"{exact} |"
        )
    lines.extend(
        [
            "",
            "## Complementary SeizureFrequency letters",
            "",
            f"Cheap only: {', '.join(complementary['sf_cheap_only']) or 'none'}.",
            f"Mention-unit only: {', '.join(complementary['sf_mention_only']) or 'none'}.",
            "",
            "## Decision",
            "",
            f"**{decision['status']}**. Oracular mix "
            f"{decision['oracular_headline']:.4f} versus cheap "
            f"{decision['cheap_headline']:.4f}. Next live arm: "
            f"{decision['next_live_arm'] or 'none'}.",
            "",
            "Do not promote. Default stays `v0.9.24`. Slots 2 and 3 stay. "
            "No `test60`.",
            "",
            "## Claim boundary",
            "",
            artifact["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
