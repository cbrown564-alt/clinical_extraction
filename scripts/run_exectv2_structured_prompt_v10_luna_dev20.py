"""Luna-only ExECT v10 contract study on a frozen 20-letter dev140 sample."""

# ruff: noqa: E501

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
    build_finding_assembly,
    render_finding_assembly_markdown,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.views import (
    predictions_from_rows,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    has_blocking_parse_issue,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import model_swap
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    clinical_headline_unit_keys,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows as write_jsonl,
)
from scripts import run_exectv2_2call_model_swap as swap_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
STUDY_DIR = REPO_ROOT / "experiments/exectv2_structured_prompt_v10_luna_dev20_20260815"
SAMPLE_PATH = STUDY_DIR / "sample.json"
CONTROL_STRUCTURED = (
    REPO_ROOT
    / "experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715_structured.jsonl"
)
RESIDUAL_PANEL = (
    REPO_ROOT
    / "experiments/exectv2_luna_single_call_dev140_residual_map_20260731/residual_panel.jsonl"
)
MODEL = "openai/gpt-5.6-luna"
FAMILIES = (
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY.name,
    PRESCRIPTION.name,
    INVESTIGATIONS.name,
)
BAND_TARGETS = {"easy": 7, "medium": 7, "hard": 6}
FORCE_HARD = "EA0133"
ESCALATION_REASON = (
    "Predeclared Luna-only ExECT v10 contract study on a frozen 20-letter "
    "dev140 sample under docs/research/exectv2/"
    "structured_prompt_v10_luna_dev20_protocol_2026-08-15.md"
)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("freeze-sample", help="Freeze the 20-letter draw before any v10 call")
    run_parser = sub.add_parser("run", help="Score the control arm and run v10 live")
    run_parser.add_argument("--overwrite", action="store_true")
    run_parser.add_argument("--progress-every", type=int, default=1)
    run_parser.add_argument("--api-base")
    args = parser.parse_args(argv)
    if args.command == "freeze-sample":
        print(json.dumps(freeze_sample(), indent=2, sort_keys=True))
        return
    print(
        json.dumps(
            run_study(
                overwrite=args.overwrite,
                progress_every=args.progress_every,
                api_base=args.api_base,
            ),
            indent=2,
            sort_keys=True,
        )
    )


def freeze_sample() -> dict[str, Any]:
    sample = _draw_sample()
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    if SAMPLE_PATH.exists():
        existing = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
        if existing["letter_ids"] != sample["letter_ids"]:
            raise RuntimeError("sample.json already frozen with a different ID list")
        return existing
    SAMPLE_PATH.write_text(
        json.dumps(sample, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return sample


def _draw_sample() -> dict[str, Any]:
    letters = {letter.letter_id: letter for letter in load_letters_for_split("dev")}
    if len(letters) != 140:
        raise ValueError(f"expected 140 dev letters, found {len(letters)}")
    rows = _read_jsonl(RESIDUAL_PANEL)
    by_letter: dict[str, dict[str, bool]] = {}
    residual_sf_dx: set[str] = set()
    for row in rows:
        letter_id = str(row["letter_id"])
        family = str(row["family"])
        correct = bool(row["default_final_correct"])
        by_letter.setdefault(letter_id, {})[family] = correct
        if family in {DIAGNOSIS.name, SEIZURE_FREQUENCY.name} and not correct:
            residual_sf_dx.add(letter_id)

    bands: dict[str, list[str]] = {"easy": [], "medium": [], "hard": []}
    for letter_id in sorted(letters):
        exact = by_letter.get(letter_id, {})
        n_wrong = sum(1 for family in FAMILIES if not exact.get(family, True))
        if (
            letter_id == FORCE_HARD
            or n_wrong >= 2
            or letter_id in residual_sf_dx
        ):
            bands["hard"].append(letter_id)
        elif n_wrong == 1:
            bands["medium"].append(letter_id)
        else:
            bands["easy"].append(letter_id)

    chosen: dict[str, list[str]] = {}
    for band, target in BAND_TARGETS.items():
        pool = list(bands[band])
        if band == "hard" and FORCE_HARD in pool:
            pool = [FORCE_HARD] + [item for item in pool if item != FORCE_HARD]
        if len(pool) < target:
            raise RuntimeError(
                f"band {band} has only {len(pool)} eligible letters; need {target}"
            )
        chosen[band] = pool[:target]

    letter_ids = sorted({item for items in chosen.values() for item in items})
    if len(letter_ids) != 20:
        raise RuntimeError(f"expected 20 unique letters, got {len(letter_ids)}")
    return {
        "schema_version": "exectv2.structured_prompt_v10_luna_dev20.v1",
        "frozen_before_v10_calls": True,
        "split": "dev140",
        "model": MODEL,
        "control_prompt_version": structured.PROMPT_VERSION_V0_9_24,
        "candidate_prompt_version": structured.PROMPT_VERSION_V10,
        "band_targets": BAND_TARGETS,
        "force_hard": FORCE_HARD,
        "bands": chosen,
        "letter_ids": letter_ids,
        "band_pool_sizes": {band: len(ids) for band, ids in bands.items()},
        "sampling_source": RESIDUAL_PANEL.relative_to(REPO_ROOT).as_posix(),
        "control_structured": CONTROL_STRUCTURED.relative_to(REPO_ROOT).as_posix(),
        "claim_boundary": (
            "ExECTv2 Luna development sample only. Not test60, not a selected "
            "prompt, and not benchmark performance."
        ),
    }


def run_study(
    *,
    overwrite: bool = False,
    progress_every: int = 1,
    api_base: str | None = None,
) -> dict[str, Any]:
    if not SAMPLE_PATH.exists():
        raise FileNotFoundError(
            "freeze the sample with freeze-sample before any v10 call"
        )
    sample = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    wanted = set(sample["letter_ids"])
    letters = [
        letter
        for letter in load_letters_for_split("dev")
        if letter.letter_id in wanted
    ]
    letters.sort(key=lambda letter: letter.letter_id)
    if len(letters) != 20:
        raise RuntimeError(f"expected 20 letters, found {len(letters)}")

    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    control = _run_arm(
        slug="v0924_control",
        prompt_version=structured.PROMPT_VERSION_V0_9_24,
        letters=letters,
        call_mode="saved_structured_no_call",
        overwrite=overwrite,
        progress_every=progress_every,
        api_base=api_base,
    )
    candidate = _run_arm(
        slug="v10_live",
        prompt_version=structured.PROMPT_VERSION_V10,
        letters=letters,
        call_mode="live",
        overwrite=overwrite,
        progress_every=progress_every,
        api_base=api_base,
    )
    comparison = _compare_arms(control, candidate, letters)
    artifact = {
        "schema_version": "exectv2.structured_prompt_v10_luna_dev20.v1",
        "generated_on": "2026-08-15",
        "protocol": (
            "docs/research/exectv2/structured_prompt_v10_luna_dev20_protocol_2026-08-15.md"
        ),
        "model": MODEL,
        "split": "dev140",
        "row_count": 20,
        "sample": sample,
        "repair_policy": {
            "diagnosis_policy_variant": "default",
            "prescription_policy_variant": "default",
        },
        "replay_mode": {
            "v0924_control": "saved_structured_no_call",
            "v10_live": "live",
        },
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "arms": {
            "v0924_control": control["summary"],
            "v10_live": candidate["summary"],
        },
        "comparison": comparison,
        "claim_boundary": (
            "ExECTv2 Luna 20-letter development comparison of the v10 contract "
            "against frozen v0.9.24. Not holdout, not a selected prompt, and "
            "not benchmark performance."
        ),
    }
    artifact_path = STUDY_DIR / "comparison.json"
    artifact_path.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report_path = (
        REPO_ROOT / "docs/research/exectv2/structured_prompt_v10_luna_dev20_2026-08-15.md"
    )
    report_path.write_text(_render_report(artifact), encoding="utf-8")
    return {
        "artifact": artifact_path.relative_to(REPO_ROOT).as_posix(),
        "report": report_path.relative_to(REPO_ROOT).as_posix(),
        "significant_regression": comparison["significant_regression"],
        "regression_triggers": comparison["regression_triggers"],
    }


def _run_arm(
    *,
    slug: str,
    prompt_version: str,
    letters: Sequence[Any],
    call_mode: str,
    overwrite: bool,
    progress_every: int,
    api_base: str | None,
) -> dict[str, Any]:
    out_dir = STUDY_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    structured_path = out_dir / "structured.jsonl"
    sf_final_path = out_dir / "arm_sf_unknown_suppression.jsonl"
    assembly_json = out_dir / "assembly.json"
    assembly_jsonl = out_dir / "assembly.jsonl"
    original = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(prompt_version)
        if call_mode == "saved_structured_no_call":
            _copy_structured_subset(CONTROL_STRUCTURED, structured_path, letters)
            new_model_calls = 0
        elif call_mode == "live":
            print(f"ESCALATION_REASON={ESCALATION_REASON}")
            rows, _meta = structured.run_split(
                letters,
                split="dev140",
                model=MODEL,
                temperature=1.0,
                max_tokens=16000,
                mode="live",
                dspy_cache=False,
                api_base=api_base,
                progress_every=progress_every,
                checkpoint_jsonl_path=structured_path,
                checkpoint_report_path=structured_path.with_suffix(".md"),
                resume=not overwrite,
                prompt_profile="full",
            )
            write_jsonl(rows, structured_path)
            new_model_calls = sum(
                1 for row in rows if not row.get("call_error") and row.get("raw_output")
            )
        else:
            raise ValueError(call_mode)
        rows = _read_jsonl(structured_path)
        _require_clean_complete_rows(rows, expected_count=len(letters))
        swap_runner._run_model_led_sf_chain(
            structured_jsonl=structured_path,
            sf_output_jsonl=sf_final_path,
            letters=letters,
        )
        assembly_cfg = _arm_assembly(slug, structured_path, sf_final_path)
        run = build_finding_assembly(
            assembly_cfg,
            generated_on="2026-08-15",
            gold_loader=lambda _split: list(letters),
            diagnosis_resolution_candidate=True,
            diagnosis_policy_variant="default",
            prescription_policy_variant="default",
        )
        report = dict(run.report)
        report["prompt_version"] = prompt_version
        report["arm"] = slug
        write_jsonl(run.rows, assembly_jsonl)
        assembly_json.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        assembly_json.with_suffix(".md").write_text(
            render_finding_assembly_markdown(
                report,
                json_path=assembly_json,
                jsonl_path=assembly_jsonl,
            ),
            encoding="utf-8",
        )
    finally:
        structured.set_active_prompt_version(original)

    letter_rows = _letter_family_rows(
        gold=letters,
        structured_path=structured_path,
        assembly_jsonl=assembly_jsonl,
        prompt_version=prompt_version,
        arm=slug,
    )
    write_jsonl(letter_rows, out_dir / "letter_family.jsonl")
    summary = _arm_summary(report, letter_rows, prompt_version, call_mode, new_model_calls)
    return {"summary": summary, "letter_rows": letter_rows, "report": report}


def _arm_assembly(slug: str, structured_path: Path, sf_final_path: Path) -> Any:
    base = model_swap.load_model_swap_config(
        REPO_ROOT / "configs/exectv2/six_model_comparison/gpt56luna_dev140.json"
    ).assembly
    producers = {
        "structured_key_family_event_ledger": replace(
            base.producers["structured_key_family_event_ledger"],
            artifact=structured_path,
        ),
        "sf_model_projection_suppression": replace(
            base.producers["sf_model_projection_suppression"],
            artifact=sf_final_path,
        ),
    }
    return replace(
        base,
        candidate_id=f"exectv2_structured_prompt_v10_luna_dev20_{slug}",
        split="dev",
        row_count=20,
        producers=producers,
        claim_boundary=(
            "ExECTv2 Luna v10 contract study on a frozen 20-letter dev140 sample."
        ),
    )


def _copy_structured_subset(
    source: Path, destination: Path, letters: Sequence[Any]
) -> None:
    wanted = {letter.letter_id for letter in letters}
    rows = [row for row in _read_jsonl(source) if str(row.get("letter_id")) in wanted]
    if len(rows) != len(wanted):
        raise ValueError(
            f"reuse structured artifact incomplete: found {len(rows)} of {len(wanted)}"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(rows, destination)


def _require_clean_complete_rows(rows: list[dict[str, Any]], *, expected_count: int) -> None:
    if len(rows) != expected_count:
        raise RuntimeError(
            f"Refusing model artifact with {len(rows)} rows; expected {expected_count}."
        )
    call_failures = sum(bool(row.get("call_error")) for row in rows)
    parse_failures = sum(
        has_blocking_parse_issue(row.get("parse_errors")) for row in rows
    )
    if call_failures or parse_failures:
        raise RuntimeError(
            "Refusing model artifact before scoring: "
            f"{call_failures} call failure(s), {parse_failures} parse/schema failure(s)."
        )


def _letter_family_rows(
    *,
    gold: Sequence[Any],
    structured_path: Path,
    assembly_jsonl: Path,
    prompt_version: str,
    arm: str,
) -> list[dict[str, Any]]:
    structured_rows = {
        str(row["letter_id"]): row for row in _read_jsonl(structured_path)
    }
    assembly_rows = {
        str(row["letter_id"]): row for row in _read_jsonl(assembly_jsonl)
    }
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
                    "model": MODEL,
                    "repair_policy": "default/default",
                    "replay_mode": (
                        "saved_structured_no_call"
                        if arm == "v0924_control"
                        else "live"
                    ),
                }
            )
    return out


def _arm_summary(
    report: Mapping[str, Any],
    letter_rows: Sequence[Mapping[str, Any]],
    prompt_version: str,
    call_mode: str,
    new_model_calls: int,
) -> dict[str, Any]:
    headline = report["score_ladder"]["headline_target"]
    raw_f1 = _surface_f1(letter_rows, "raw_keys")
    hybrid_f1 = _surface_f1(letter_rows, "hybrid_keys")
    return {
        "prompt_version": prompt_version,
        "call_mode": call_mode,
        "new_model_calls": new_model_calls,
        "assembly_headline_f1": float(headline["overall"]["f1"]),
        "assembly_family_f1": {
            family: float(headline["by_indicator"][family]["f1"]) for family in FAMILIES
        },
        "raw_headline_f1": raw_f1["overall"],
        "raw_family_f1": raw_f1["by_family"],
        "hybrid_headline_f1": hybrid_f1["overall"],
        "hybrid_family_f1": hybrid_f1["by_family"],
        "raw_four_family_letter_exact": _four_family_exact(letter_rows, "raw_letter_exact"),
        "hybrid_four_family_letter_exact": _four_family_exact(
            letter_rows, "hybrid_letter_exact"
        ),
        "raw_family_letter_exact": _family_exact(letter_rows, "raw_letter_exact"),
        "hybrid_family_letter_exact": _family_exact(letter_rows, "hybrid_letter_exact"),
        "hybrid_rewrite_letters": sorted(
            {
                row["letter_id"]
                for row in letter_rows
                if row["hybrid_rewrote"]
            }
        ),
    }


def _surface_f1(
    letter_rows: Sequence[Mapping[str, Any]], key_field: str
) -> dict[str, Any]:
    by_family: dict[str, float] = {}
    overall = Counter()
    for family in FAMILIES:
        counts = Counter()
        for row in letter_rows:
            if row["family"] != family:
                continue
            gold = _counter_from_rows(row["gold_keys"])
            pred = _counter_from_rows(row[key_field])
            counts += _prf_counts(gold, pred)
        overall += counts
        by_family[family] = _f1(counts)
    return {"overall": _f1(overall), "by_family": by_family}


def _prf_counts(gold: Counter[Any], pred: Counter[Any]) -> Counter[str]:
    tp = sum((gold & pred).values())
    fp = sum((pred - gold).values())
    fn = sum((gold - pred).values())
    return Counter({"tp": tp, "fp": fp, "fn": fn})


def _f1(counts: Mapping[str, int]) -> float:
    tp = counts["tp"]
    denom = 2 * tp + counts["fp"] + counts["fn"]
    return 0.0 if denom == 0 else round(2 * tp / denom, 4)


def _four_family_exact(letter_rows: Sequence[Mapping[str, Any]], field: str) -> int:
    by_letter: dict[str, list[bool]] = {}
    for row in letter_rows:
        by_letter.setdefault(str(row["letter_id"]), []).append(bool(row[field]))
    return sum(1 for flags in by_letter.values() if all(flags))


def _family_exact(letter_rows: Sequence[Mapping[str, Any]], field: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for family in FAMILIES:
        out[family] = sum(
            1 for row in letter_rows if row["family"] == family and row[field]
        )
    return out


def _compare_arms(
    control: Mapping[str, Any],
    candidate: Mapping[str, Any],
    letters: Sequence[Any],
) -> dict[str, Any]:
    ctrl = control["summary"]
    cand = candidate["summary"]
    control_rows = { (row["letter_id"], row["family"]): row for row in control["letter_rows"] }
    candidate_rows = {
        (row["letter_id"], row["family"]): row for row in candidate["letter_rows"]
    }
    surfaces = {}
    triggers: list[str] = []
    for surface, f1_field, exact_field, family_f1_field in (
        (
            "raw",
            "raw_headline_f1",
            "raw_letter_exact",
            "raw_family_f1",
        ),
        (
            "hybrid",
            "hybrid_headline_f1",
            "hybrid_letter_exact",
            "hybrid_family_f1",
        ),
    ):
        delta_f1 = round(cand[f1_field] - ctrl[f1_field], 4)
        family_delta = {
            family: round(
                cand[family_f1_field][family] - ctrl[family_f1_field][family], 4
            )
            for family in FAMILIES
        }
        wins = 0
        losses = 0
        per_family_flip: dict[str, dict[str, int]] = {}
        four_family_control: dict[str, bool] = {}
        four_family_candidate: dict[str, bool] = {}
        for letter in letters:
            letter_id = letter.letter_id
            control_all = True
            candidate_all = True
            for family in FAMILIES:
                c_ok = bool(control_rows[(letter_id, family)][exact_field])
                n_ok = bool(candidate_rows[(letter_id, family)][exact_field])
                control_all = control_all and c_ok
                candidate_all = candidate_all and n_ok
                flips = per_family_flip.setdefault(family, {"wins": 0, "losses": 0})
                if n_ok and not c_ok:
                    flips["wins"] += 1
                elif c_ok and not n_ok:
                    flips["losses"] += 1
            four_family_control[letter_id] = control_all
            four_family_candidate[letter_id] = candidate_all
            if candidate_all and not control_all:
                wins += 1
            elif control_all and not candidate_all:
                losses += 1
        net = wins - losses
        if delta_f1 <= -0.05:
            triggers.append(f"{surface} four-family F1 drop {delta_f1}")
        for family, delta in family_delta.items():
            if delta <= -0.08:
                triggers.append(f"{surface} {family} F1 drop {delta}")
        if losses - wins >= 3:
            triggers.append(
                f"{surface} net four-family letter-exact losses {losses - wins}"
            )
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


def _counter_rows(counter: Counter[Any]) -> list[dict[str, Any]]:
    rows = [{"key": _jsonable(key), "count": count} for key, count in counter.items()]
    return sorted(rows, key=lambda row: json.dumps(row["key"], sort_keys=True))


def _counter_from_rows(rows: Sequence[Mapping[str, Any]]) -> Counter[Any]:
    counter: Counter[Any] = Counter()
    for row in rows:
        key = row["key"]
        if isinstance(key, list):
            key = tuple(
                tuple(item) if isinstance(item, list) else item for item in key
            )
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


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _render_report(artifact: Mapping[str, Any]) -> str:
    sample = artifact["sample"]
    comparison = artifact["comparison"]
    raw = comparison["surfaces"]["raw"]
    hybrid = comparison["surfaces"]["hybrid"]
    ctrl = artifact["arms"]["v0924_control"]
    cand = artifact["arms"]["v10_live"]
    verdict = (
        "significant regression"
        if comparison["significant_regression"]
        else "no significant regression"
    )
    triggers = comparison["regression_triggers"] or ["none"]
    bands = "\n".join(
        f"- **{band}:** {', '.join(ids)}" for band, ids in sample["bands"].items()
    )
    return f"""# Luna `dev20` test of the ExECT v0.1 contract

Date: 2026-08-15
Status: complete; {verdict}
Protocol: [structured_prompt_v10_luna_dev20_protocol_2026-08-15.md](structured_prompt_v10_luna_dev20_protocol_2026-08-15.md)
Model: `{artifact["model"]}`
Sample: frozen 20 letters from ExECT `dev140`; `test60` not touched

## Verdict

**{verdict}.** This is not a promotion and not a benchmark score.

Regression triggers: {", ".join(triggers)}.

If this is a significant regression, the next step is the named add-back
ladder on the same 20 letters. If it is not, the next step is a
predeclared Luna `dev140` protocol.

## Frozen sample

Drawn from the Luna `v0.9.24` residual panel before any v10 call. Lowest
`letter_id` within each band. `EA0133` forced into hard.

{bands}

Letter IDs: {", ".join(sample["letter_ids"])}

## Conditions

| Item | Value |
| :--- | :--- |
| Control | no-call reuse of the 15 Jul Luna `v0.9.24` structured sidecar |
| Candidate | live Luna, `exectv2_hybrid_key_family_event_ledger_v10` |
| Profile | `full` |
| Repair | default / default |
| Scorer | four-family `clinical_headline` unit keys; family-local letter exactness |
| Gold at prompt-build time | forbidden |
| Holdout | not touched |

## Headline F1 on the 20-letter pool

| Surface | v0.9.24 | v10 | delta |
| :--- | ---: | ---: | ---: |
| raw | {ctrl["raw_headline_f1"]:.4f} | {cand["raw_headline_f1"]:.4f} | {raw["headline_f1_delta"]:+.4f} |
| hybrid | {ctrl["hybrid_headline_f1"]:.4f} | {cand["hybrid_headline_f1"]:.4f} | {hybrid["headline_f1_delta"]:+.4f} |

## Family F1 delta (v10 − v0.9.24)

| Family | raw | hybrid |
| :--- | ---: | ---: |
| Diagnosis | {raw["family_f1_delta"]["Diagnosis"]:+.4f} | {hybrid["family_f1_delta"]["Diagnosis"]:+.4f} |
| SeizureFrequency | {raw["family_f1_delta"]["SeizureFrequency"]:+.4f} | {hybrid["family_f1_delta"]["SeizureFrequency"]:+.4f} |
| Prescription | {raw["family_f1_delta"]["Prescription"]:+.4f} | {hybrid["family_f1_delta"]["Prescription"]:+.4f} |
| Investigations | {raw["family_f1_delta"]["Investigations"]:+.4f} | {hybrid["family_f1_delta"]["Investigations"]:+.4f} |

## Four-family letter-exact wins / losses

| Surface | wins | losses | net |
| :--- | ---: | ---: | ---: |
| raw | {raw["four_family_letter_exact_wins"]} | {raw["four_family_letter_exact_losses"]} | {raw["four_family_letter_exact_net"]} |
| hybrid | {hybrid["four_family_letter_exact_wins"]} | {hybrid["four_family_letter_exact_losses"]} | {hybrid["four_family_letter_exact_net"]} |

Control four-family exact: raw {ctrl["raw_four_family_letter_exact"]}/20, hybrid {ctrl["hybrid_four_family_letter_exact"]}/20.
Candidate four-family exact: raw {cand["raw_four_family_letter_exact"]}/20, hybrid {cand["hybrid_four_family_letter_exact"]}/20.

## Boundary

Not `test60`. Not a selected prompt. Not a six-model claim. Parser, evidence
gate, attribute gate, and hybrid dictionary stayed at HEAD; only the
model-facing JSON changed on the v10 arm.
"""


if __name__ == "__main__":
    main()
