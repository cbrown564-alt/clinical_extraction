"""Shared scoring helpers for Compact versus Full ledger remasure.

Living Compact runners import compare/score helpers from here.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dspy
from dotenv import load_dotenv

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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    has_blocking_parse_issue,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
    structured_one_call,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
    StructuredMethodConfig,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    clinical_headline_unit_keys,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/exectv2/v0924_cheap_stack_luna_dev140_protocol_2026-08-16.md"
REPORT_PATH = ROOT / "docs/research/exectv2/v0924_cheap_stack_luna_dev140_2026-08-16.md"
STUDY_DIR = ROOT / "experiments/exectv2_v0924_cheap_stack_luna_dev140_20260816"
CONTROL_STRUCTURED = (
    ROOT / "experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715_structured.jsonl"
)
CHEAP_STACK_DEV20 = (
    ROOT / "experiments/exectv2_v0924_cheap_stack_luna_dev20_20260816" / "comparison.json"
)
MODEL = "openai/gpt-5.6-luna"
CANDIDATE_ARM = "drop_encoding_non_sf_all_examples"
CANDIDATE_VERSION = structured.COMPACT_LEDGER
CONTROL_VERSION = structured.FULL_LEDGER
FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")
FROZEN_DEV20_IDS = (
    "EA0002",
    "EA0004",
    "EA0005",
    "EA0006",
    "EA0007",
    "EA0008",
    "EA0009",
    "EA0010",
    "EA0011",
    "EA0012",
    "EA0015",
    "EA0016",
    "EA0047",
    "EA0074",
    "EA0093",
    "EA0120",
    "EA0131",
    "EA0133",
    "EA0154",
    "EA0158",
)
HEADLINE_DROP_LIMIT = 0.05
FAMILY_DROP_LIMIT = 0.08
NET_LOSS_LIMIT = 3
SCAFFOLD_KEYS = ("decision_procedure", "suggested_evidence", "categories")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--api-base")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--progress-every", type=int, default=1)
    args = parser.parse_args(argv)
    if args.live:
        print(json.dumps(run_study(
            live=True,
            overwrite=args.overwrite,
            api_base=args.api_base,
            timeout=args.timeout,
            progress_every=args.progress_every,
        ), indent=2, sort_keys=True))
        return
    print(json.dumps(verify_payload(), indent=2, sort_keys=True))


def verify_payload() -> dict[str, Any]:
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    before = structured.PROMPT_VERSION
    try:
        control = json.loads(
            structured.build_prompt_input(letter, prompt_version=CONTROL_VERSION)
        )
        if len(control["clinical_rules"]) != 83 or len(control["worked_examples"]) != 49:
            raise RuntimeError("Full ledger control payload drifted")
        payload = json.loads(
            structured.build_prompt_input(letter, prompt_version=CANDIDATE_VERSION)
        )
        if "prompt_version" in payload or "letter_id" in payload:
            raise RuntimeError("Compact still emits research metadata")
        if "cui" in json.dumps(payload).lower():
            raise RuntimeError("Compact leaked CUI")
        n_rules = len(payload["clinical_rules"])
        n_examples = len(payload.get("worked_examples") or [])
        has_scaffold = all(key in payload for key in SCAFFOLD_KEYS)
        if n_rules != 67 or n_examples != 0 or not has_scaffold:
            raise RuntimeError("Compact contract drifted")
    finally:
        structured.set_active_prompt_version(before)
    if structured.PROMPT_VERSION != structured.COMPACT_LEDGER:
        raise RuntimeError("payload check changed the live default")
    return {
        "ok": True,
        "default_prompt_version": structured.PROMPT_VERSION,
        "prompt_version": CANDIDATE_VERSION,
        "n_rules": 67,
        "n_examples": 0,
        "has_scaffold": True,
        "protocol": PROTOCOL,
    }


def topology_failures(hybrid: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    delta = float(hybrid["headline_f1_delta"])
    if delta <= -HEADLINE_DROP_LIMIT:
        failures.append(f"hybrid four-family F1 drop {delta}")
    for family, family_delta in dict(hybrid["family_f1_delta"]).items():
        if float(family_delta) <= -FAMILY_DROP_LIMIT:
            failures.append(f"hybrid {family} F1 drop {family_delta}")
    losses = int(hybrid["four_family_letter_exact_losses"])
    wins = int(hybrid["four_family_letter_exact_wins"])
    net_losses = losses - wins
    if net_losses >= NET_LOSS_LIMIT:
        failures.append(f"hybrid net four-family letter-exact losses {net_losses}")
    return failures


def decide_arm(hybrid: Mapping[str, Any], quality: Mapping[str, Any]) -> str:
    if int(quality.get("parse") or 0) or int(quality.get("schema") or 0):
        return "revise"
    return "load_bearing" if topology_failures(hybrid) else "low_value"


def run_study(
    *,
    live: bool,
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int = 300,
    progress_every: int = 1,
) -> dict[str, Any]:
    verify_payload()
    if not live:
        raise RuntimeError("run_study requires live=True for the authorized transfer")
    load_dotenv(ROOT / ".env", override=False)
    if not os.environ.get("OPENAI_API_KEY", "").strip():
        raise RuntimeError("OPENAI_API_KEY is missing; stopping before any candidate call")
    if not CONTROL_STRUCTURED.exists():
        raise RuntimeError(f"missing saved control sidecar: {CONTROL_STRUCTURED}")

    letters = _letters()
    control_raws = _control_raws(letters)
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    if structured.PROMPT_VERSION != structured.COMPACT_LEDGER:
        raise RuntimeError("live default drifted before the run")

    control = _run_control(letters, control_raws)
    candidate = _run_candidate(
        letters,
        overwrite=overwrite,
        api_base=api_base,
        timeout=timeout,
        progress_every=progress_every,
    )
    if structured.PROMPT_VERSION != structured.COMPACT_LEDGER:
        raise RuntimeError("candidate arm left the live default changed")

    versus = _compare_pair(control, candidate, letters)
    hybrid = versus["surfaces"]["hybrid"]
    quality = candidate["summary"]["quality"]
    verdict = decide_arm(hybrid, quality)
    overlap = _overlap_dev20(control, candidate, letters)
    artifact = {
        "schema_version": "exectv2.v0924_cheap_stack_luna_dev140.v1",
        "generated_on": "2026-08-16",
        "protocol": PROTOCOL,
        "model": MODEL,
        "temperature": 1.0,
        "max_tokens": 16000,
        "cache": False,
        "split": "dev140",
        "row_count": len(letters),
        "letter_ids": [letter.letter_id for letter in letters],
        "repair_policy": {
            "diagnosis_policy_variant": "default",
            "prescription_policy_variant": "default",
        },
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": True,
        "model_calls": candidate["summary"]["new_model_calls"],
        "default_prompt_version": structured.PROMPT_VERSION,
        "requested_arms": [CANDIDATE_ARM],
        "arms": {
            "v0924_head": control["summary"],
            CANDIDATE_ARM: candidate["summary"],
        },
        "comparison": {f"{CANDIDATE_ARM}_minus_v0924_head": versus},
        "decision": {
            CANDIDATE_ARM: {
                "status": "scored",
                "verdict": verdict,
                "failures": topology_failures(hybrid)
                if verdict != "revise"
                else [
                    *topology_failures(hybrid),
                    f"parse={quality['parse']} schema={quality['schema']}",
                ],
                "headline_f1_delta": hybrid["headline_f1_delta"],
                "family_f1_delta": hybrid["family_f1_delta"],
                "four_family_letter_exact_net": hybrid["four_family_letter_exact_net"],
            }
        },
        "frozen_dev20_overlap": overlap,
        "changed_rows": _changed_rows(control, candidate, letters),
        "provenance": _provenance(),
        "claim_boundary": (
            "ExECTv2 Luna 140-letter development cheap-stack transfer of "
            "v0.9.24. Not holdout, not a selected prompt, and not a Decision "
            "0050 change."
        ),
    }
    out = STUDY_DIR / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "artifact": out.relative_to(ROOT).as_posix(),
        "report": REPORT_PATH.relative_to(ROOT).as_posix(),
        "live": True,
        "model_calls": artifact["model_calls"],
        "decision": artifact["decision"],
        "default_prompt_version": structured.PROMPT_VERSION,
    }


def _letters() -> list[ExectLetter]:
    letters = list(load_letters_for_split("dev"))
    letters.sort(key=lambda item: item.letter_id)
    if len(letters) != 140:
        raise RuntimeError(f"expected 140 loadable development letters, found {len(letters)}")
    return letters


def _control_raws(letters: Sequence[ExectLetter]) -> dict[str, str]:
    wanted = {letter.letter_id for letter in letters}
    raws: dict[str, str] = {}
    for row in load_jsonl_rows(CONTROL_STRUCTURED):
        letter_id = str(row.get("letter_id") or "")
        if letter_id not in wanted:
            continue
        raw = str(row.get("raw_output") or "")
        if not raw:
            raise RuntimeError(f"control sidecar missing raw_output for {letter_id}")
        raws[letter_id] = raw
    missing = sorted(wanted - set(raws))
    if missing:
        raise RuntimeError(f"control sidecar missing letters: {missing}")
    return raws


def _run_control(
    letters: Sequence[ExectLetter],
    raws: Mapping[str, str],
) -> dict[str, Any]:
    out_dir = STUDY_DIR / "v0924_head"
    structured_path = out_dir / "structured.jsonl"
    assembly_path = out_dir / "assembly.jsonl"
    producer_rows: list[dict[str, Any]] = []
    assembly_rows: list[dict[str, Any]] = []
    for letter in letters:
        producer = structured_one_call.produce_structured_letter(
            letter,
            model=MODEL,
            mode="replay",
            raw_output=raws[letter.letter_id],
            split="dev140",
            config=StructuredMethodConfig.selected(),
        )
        hybrid = structured_one_call.run_llm_with_rules_letter(letter, producer)
        producer_rows.append(dict(producer.row))
        assembly_rows.append(_assembly_row(hybrid.row, CONTROL_VERSION, "saved_structured_no_call"))
    write_jsonl_rows(producer_rows, structured_path)
    write_jsonl_rows(assembly_rows, assembly_path)
    return _score_arm(
        slug="v0924_head",
        prompt_version=CONTROL_VERSION,
        call_mode="saved_structured_no_call",
        new_model_calls=0,
        letters=letters,
        structured_path=structured_path,
        assembly_path=assembly_path,
    )


def _run_candidate(
    letters: Sequence[ExectLetter],
    *,
    overwrite: bool,
    api_base: str | None,
    timeout: int,
    progress_every: int,
) -> dict[str, Any]:
    out_dir = STUDY_DIR / CANDIDATE_ARM
    structured_path = out_dir / "structured.jsonl"
    assembly_path = out_dir / "assembly.jsonl"
    existing = [] if overwrite else _existing_complete_rows(structured_path, CANDIDATE_VERSION)
    done = {str(row["letter_id"]) for row in existing}
    todo = [letter for letter in letters if letter.letter_id not in done]
    before = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(CANDIDATE_VERSION)
        if todo:
            _require_api_key()
            dspy.configure(
                lm=build_dspy_lm(
                    MODEL,
                    temperature=1.0,
                    max_tokens=16000,
                    cache=False,
                    api_base=api_base,
                    timeout=timeout,
                )
            )
            program = structured_one_call.DspyKeyEntitiesStructuredExtractor()
            rows = list(existing)
            for index, letter in enumerate(todo, start=1):
                producer = structured_one_call.produce_structured_letter(
                    letter,
                    model=MODEL,
                    temperature=1.0,
                    max_tokens=16000,
                    mode="live",
                    dspy_cache=False,
                    api_base=api_base,
                    timeout=timeout,
                    split="dev140",
                    program=program,
                    config=StructuredMethodConfig.selected(),
                )
                row = dict(producer.row)
                if row.get("prompt_version") != CANDIDATE_VERSION:
                    raise RuntimeError(
                        f"{letter.letter_id} used {row.get('prompt_version')}"
                    )
                if producer.call_error:
                    raise RuntimeError(
                        f"{letter.letter_id} call failed: {producer.call_error}"
                    )
                rows.append(row)
                write_jsonl_rows(rows, structured_path)
                if progress_every and index % progress_every == 0:
                    print(
                        f"cheap-stack dev140: {len(rows)}/{len(letters)} structured",
                        flush=True,
                    )
            existing = rows
        assembly_rows = []
        by_id = {str(row["letter_id"]): row for row in existing}
        for letter in letters:
            saved = by_id[letter.letter_id]
            producer = structured_one_call.produce_structured_letter(
                letter,
                model=MODEL,
                mode="replay",
                raw_output=str(saved["raw_output"]),
                split="dev140",
                config=StructuredMethodConfig.selected(),
            )
            hybrid = structured_one_call.run_llm_with_rules_letter(letter, producer)
            assembly_rows.append(
                _assembly_row(hybrid.row, CANDIDATE_VERSION, "live")
            )
        write_jsonl_rows(existing, structured_path)
        write_jsonl_rows(assembly_rows, assembly_path)
    finally:
        structured.set_active_prompt_version(before)
    return _score_arm(
        slug=CANDIDATE_ARM,
        prompt_version=CANDIDATE_VERSION,
        call_mode="live",
        new_model_calls=len(todo),
        letters=letters,
        structured_path=structured_path,
        assembly_path=assembly_path,
    )


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
    model: str | None = None,
) -> dict[str, Any]:
    structured_rows = load_jsonl_rows(structured_path)
    if len(structured_rows) != len(letters):
        raise RuntimeError(
            f"{slug} structured sidecar has {len(structured_rows)} rows, expected {len(letters)}"
        )
    letter_rows = _letter_family_rows(
        gold=letters,
        structured_path=structured_path,
        assembly_path=assembly_path,
        prompt_version=prompt_version,
        arm=slug,
        call_mode=call_mode,
        model=model or MODEL,
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
    model: str | None = None,
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
                    "model": model or MODEL,
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


def _overlap_dev20(
    control: Mapping[str, Any],
    candidate: Mapping[str, Any],
    letters: Sequence[ExectLetter],
) -> dict[str, Any]:
    wanted = set(FROZEN_DEV20_IDS)
    overlap_letters = [letter for letter in letters if letter.letter_id in wanted]
    control_overlap = _subset_arm(control, wanted)
    candidate_overlap = _subset_arm(candidate, wanted)
    versus = _compare_pair(control_overlap, candidate_overlap, overlap_letters)
    saved = {}
    if CHEAP_STACK_DEV20.exists():
        previous = json.loads(CHEAP_STACK_DEV20.read_text(encoding="utf-8"))
        saved = {
            "control_hybrid_headline_f1": previous["arms"]["v0924_head"]["hybrid_headline_f1"],
            "candidate_hybrid_headline_f1": previous["arms"][CANDIDATE_ARM][
                "hybrid_headline_f1"
            ],
            "candidate_sf_f1": previous["arms"][CANDIDATE_ARM]["hybrid_family_f1"][
                "SeizureFrequency"
            ],
            "headline_f1_delta": previous["decision"][CANDIDATE_ARM]["headline_f1_delta"],
            "sf_f1_delta": previous["decision"][CANDIDATE_ARM]["family_f1_delta"][
                "SeizureFrequency"
            ],
        }
    return {
        "letter_ids": [letter.letter_id for letter in overlap_letters],
        "row_count": len(overlap_letters),
        "arms": {
            "v0924_head": control_overlap["summary"],
            CANDIDATE_ARM: candidate_overlap["summary"],
        },
        "comparison": versus,
        "saved_dev20_artifact": saved,
        "note": (
            "Frozen 20-letter overlap only. Do not treat this slice as the "
            "140-letter result."
        ),
    }


def _subset_arm(arm: Mapping[str, Any], wanted: set[str]) -> dict[str, Any]:
    letter_rows = [row for row in arm["letter_rows"] if row["letter_id"] in wanted]
    raw_prf = _surface_prf(letter_rows, "raw_keys")
    hybrid_prf = _surface_prf(letter_rows, "hybrid_keys")
    summary = {
        "raw_headline_f1": raw_prf["overall"]["f1"],
        "raw_family_f1": {family: raw_prf["by_family"][family]["f1"] for family in FAMILIES},
        "hybrid_headline_f1": hybrid_prf["overall"]["f1"],
        "hybrid_family_f1": {
            family: hybrid_prf["by_family"][family]["f1"] for family in FAMILIES
        },
        "raw_four_family_letter_exact": _four_family_exact(letter_rows, "raw_letter_exact"),
        "hybrid_four_family_letter_exact": _four_family_exact(
            letter_rows, "hybrid_letter_exact"
        ),
    }
    return {"summary": summary, "letter_rows": letter_rows}


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


def _provenance() -> dict[str, Any]:
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
    )
    return {"git_commit": commit, "dirty_tree": dirty}


def _require_api_key() -> None:
    if not os.environ.get("OPENAI_API_KEY", "").strip():
        raise RuntimeError("OPENAI_API_KEY is missing; stopping before any candidate call")


if __name__ == "__main__":
    main()
