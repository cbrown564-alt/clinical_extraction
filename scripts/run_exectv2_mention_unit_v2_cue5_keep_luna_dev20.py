"""Score one cue-5 keep sentence on frozen mention-unit v2 Luna dev20."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dspy
from dotenv import load_dotenv

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit import (
    CUE5_ARM_VERSIONS,
    HYBRID_METHOD,
    LLM_METHOD,
    MENTION_UNIT_MODEL,
    MENTION_UNIT_PROMPT_VERSION,
    SYSTEM_MESSAGE,
    MentionUnitCue5Arm,
    MentionUnitExtractor,
    build_mention_unit_prompt,
    materialize_mention_unit,
    mention_unit_prompt_version,
    parse_mention_unit_json,
    selection_cues_for,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from scripts.run_exectv2_mention_unit_v2_luna import (
    FAMILIES,
    _empty_materialization,
    _hybrid_growth,
    _load_controls,
    _load_dev20,
    _nontarget_mentions,
    _norm_span,
    _provenance,
    _replay_current_controls,
    _score_method,
    _span_matches,
    _verify_prompt_contracts,
)
from scripts.run_exectv2_mention_unit_v2_luna import (
    STUDY_DIR as V2_STUDY_DIR,
)
from scripts.run_exectv2_v0924_cheap_stack_luna_dev140 import _require_api_key

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/exectv2/mention_unit_v2_cue5_keep_luna_dev20_protocol_2026-08-17.md"
REPORT = ROOT / "docs/research/exectv2/mention_unit_v2_cue5_keep_luna_dev20_2026-08-17.md"
STUDY_DIR = ROOT / "experiments/exectv2_mention_unit_v2_cue5_keep_luna_dev20_20260817"
V2_ROWS = V2_STUDY_DIR / "rows.jsonl"
ARM_ORDER: tuple[MentionUnitCue5Arm, ...] = ("heading", "bare_frame", "one_row", "no_join")
HEADING_LETTERS = ("EA0008", "EA0011")
BARE_FRAME_LETTERS = ("EA0016", "EA0074")
NO_JOIN_LETTER = "EA0047"
_BANNED = (
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


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=ARM_ORDER, required=True)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--api-base")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--progress-every", type=int, default=5)
    args = parser.parse_args(argv)
    if args.live:
        print(json.dumps(run_study(args), indent=2, sort_keys=True))
        return
    print(json.dumps(verify_payload(args.arm), indent=2, sort_keys=True))


def verify_payload(arm: MentionUnitCue5Arm) -> dict[str, Any]:
    letter = ExectLetter(letter_id="EA0002", note_text="She takes lamotrigine 100 mg daily.")
    _verify_prompt_contracts(letter)
    frozen = json.loads(build_mention_unit_prompt(letter, method=LLM_METHOD))
    if frozen["selection_cues"][4] != selection_cues_for()[4]:
        raise RuntimeError("frozen v2 cue 5 drifted")
    if mention_unit_prompt_version() != MENTION_UNIT_PROMPT_VERSION:
        raise RuntimeError("default prompt identity drifted")
    for method in (LLM_METHOD, HYBRID_METHOD):
        payload = json.loads(build_mention_unit_prompt(letter, method=method, cue5_arm=arm))
        cues = payload["selection_cues"]
        if len(cues) != 7:
            raise RuntimeError(f"{arm} no longer has seven cues")
        if cues[4] == frozen["selection_cues"][4]:
            raise RuntimeError(f"{arm} did not change cue 5")
        if not cues[4].startswith(frozen["selection_cues"][4] + " "):
            raise RuntimeError(f"{arm} rewrote frozen cue 5 instead of appending")
        if cues[:4] != frozen["selection_cues"][:4] or cues[5:] != frozen["selection_cues"][5:]:
            raise RuntimeError(f"{arm} changed a cue other than cue 5")
        serialized = json.dumps(
            {key: value for key, value in payload.items() if key != "letter_text"}
        ).lower()
        for term in _BANNED:
            if term in serialized:
                raise RuntimeError(f"{arm} leaked {term!r}")
        messages = MentionUnitExtractor(method=method).render_messages(
            prompt_input_json=build_mention_unit_prompt(letter, method=method, cue5_arm=arm)
        )
        if messages[0] != {"role": "system", "content": SYSTEM_MESSAGE}:
            raise RuntimeError("system message drifted")
    return {
        "ok": True,
        "arm": arm,
        "prompt_version": CUE5_ARM_VERSIONS[arm],
        "default_prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "protocol": PROTOCOL,
        "model_calls": 0,
    }


def run_study(args: argparse.Namespace) -> dict[str, Any]:
    arm: MentionUnitCue5Arm = args.arm
    verify_payload(arm)
    load_dotenv(ROOT / ".env", override=False)
    _require_api_key()
    if not V2_ROWS.exists():
        raise RuntimeError(f"missing saved mention-unit v2 rows: {V2_ROWS}")

    letters = _load_dev20()
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    arm_dir = STUDY_DIR / arm
    rows_path = arm_dir / "rows.jsonl"
    if rows_path.exists() and not args.overwrite:
        raise SystemExit(f"arm exists; pass --overwrite: {arm_dir}")

    started = datetime.now(UTC).isoformat()
    v2_rows = _load_v2_rows()
    controls = _load_controls()
    v2_predictions = _rematerialize_saved(letters, v2_rows)
    control_predictions = {
        LLM_METHOD: [],
        HYBRID_METHOD: [],
    }
    for letter in letters:
        control_llm, control_hybrid = _replay_current_controls(letter, controls[letter.letter_id])
        control_predictions[LLM_METHOD].append(control_llm)
        control_predictions[HYBRID_METHOD].append(control_hybrid)

    candidate_predictions, rows, operational = _run_live(
        letters,
        arm,
        api_base=args.api_base,
        timeout=args.timeout,
        progress_every=args.progress_every,
    )
    summaries = {
        "control_llm": _score_method(letters, control_predictions[LLM_METHOD]),
        "control_llm_with_rules": _score_method(letters, control_predictions[HYBRID_METHOD]),
        "mention_unit_v2_llm": _score_method(letters, v2_predictions[LLM_METHOD]),
        "mention_unit_v2_llm_with_rules": _score_method(letters, v2_predictions[HYBRID_METHOD]),
        LLM_METHOD: _score_method(letters, candidate_predictions[LLM_METHOD]),
        HYBRID_METHOD: _score_method(letters, candidate_predictions[HYBRID_METHOD]),
    }
    emission = _emission_versus_v2(letters, rows, v2_rows)
    leftover = _leftover_signals(arm, letters, rows, v2_rows, v2_predictions)
    stop = _stop_checks(letters, rows, summaries, leftover)
    arm_dir.mkdir(parents=True, exist_ok=True)
    _write_rows(rows_path, rows)
    previous = _load_artifact()
    arms = dict(previous.get("arms") or {})
    arms[arm] = {
        "prompt_version": CUE5_ARM_VERSIONS[arm],
        "methods": summaries,
        "operational": operational,
        "stop_checks": stop,
        "leftover_signals": leftover,
        "gold_wording_emission": emission["families"],
        "model_calls": len(letters) * 2,
    }
    requested = list(previous.get("requested_arms") or [])
    if arm not in requested:
        requested.append(arm)
    artifact = {
        "schema_version": "exectv2.mention_unit_v2_cue5_keep.dev20.v1",
        "status": "complete" if set(requested) == set(ARM_ORDER) else "in_progress",
        "protocol": PROTOCOL,
        "split": "dev20",
        "row_count": len(letters),
        "model": MENTION_UNIT_MODEL,
        "temperature": 1.0,
        "max_tokens": 2400,
        "cache": False,
        "default_prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "requested_arms": requested,
        "model_calls": sum(int(item["model_calls"]) for item in arms.values()),
        "arms": arms,
        "started_utc": previous.get("started_utc") or started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "row_policy": "development rows permitted; test60 sealed",
        "claim_boundary": (
            "GPT-5.6 Luna ExECT development result on frozen dev20. "
            "Study-only cue-5 suffixes. Mention-unit v2 stays frozen. "
            "test60 was not inspected. Decision 0050 is unchanged."
        ),
    }
    (STUDY_DIR / "comparison.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT.write_text(_render_report(artifact), encoding="utf-8")
    return {
        "status": artifact["status"],
        "arm": arm,
        "verdict": stop["verdict"],
        "model_calls": artifact["model_calls"],
        "stop_checks": stop,
        "leftover_signals": leftover,
        "claim_boundary": artifact["claim_boundary"],
    }


def _load_v2_rows() -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    with V2_ROWS.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            rows[str(row["letter_id"])] = row
    return rows


def _rematerialize_saved(
    letters: list[ExectLetter],
    saved_rows: dict[str, dict[str, Any]],
) -> dict[str, list[PredictedLetter]]:
    predictions: dict[str, list[PredictedLetter]] = {LLM_METHOD: [], HYBRID_METHOD: []}
    for letter in letters:
        saved = saved_rows[letter.letter_id]
        for method in (LLM_METHOD, HYBRID_METHOD):
            raw = str(saved["methods"][method].get("raw_output") or "")
            parsed = parse_mention_unit_json(raw, method=method)
            if parsed.record is None:
                materialized = _empty_materialization(letter, parsed.errors)
            else:
                materialized = materialize_mention_unit(letter, parsed.record, method=method)
            predictions[method].append(materialized.prediction)
    return predictions


def _run_live(
    letters: list[ExectLetter],
    arm: MentionUnitCue5Arm,
    *,
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
            "prompt_version": CUE5_ARM_VERSIONS[arm],
            "cue5_arm": arm,
            "methods": {},
        }
        for method in (LLM_METHOD, HYBRID_METHOD):
            prompt = build_mention_unit_prompt(letter, method=method, cue5_arm=arm)
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
            else:
                materialized = materialize_mention_unit(letter, parsed.record, method=method)
            candidate[method].append(materialized.prediction)
            stats["evidence_invalid"] += materialized.evidence_invalid
            row["methods"][method] = {
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
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
            print(f"{arm}: completed {index}/{len(letters)} rows", flush=True)
    return candidate, rows, operational


def _emission_versus_v2(
    letters: list[ExectLetter],
    rows: list[dict[str, Any]],
    v2_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    totals = {
        family: {
            "gold_units": 0,
            "candidate_llm_exact": 0,
            "candidate_hybrid_exact": 0,
            "v2_llm_exact": 0,
            "v2_hybrid_exact": 0,
        }
        for family in FAMILIES
    }
    for letter, row in zip(letters, rows, strict=True):
        v2 = v2_rows[letter.letter_id]
        for family in FAMILIES:
            gold_units = [
                {"text": annotation.text, "raw_text": annotation.raw_text or annotation.text}
                for annotation in letter.entities(family)
            ]
            matched = {
                "candidate_llm": _span_matches(gold_units, _names(row["methods"][LLM_METHOD])),
                "candidate_hybrid": _span_matches(
                    gold_units, _names(row["methods"][HYBRID_METHOD])
                ),
                "v2_llm": _span_matches(gold_units, _names(v2["methods"][LLM_METHOD])),
                "v2_hybrid": _span_matches(gold_units, _names(v2["methods"][HYBRID_METHOD])),
            }
            totals[family]["gold_units"] += len(gold_units)
            for key, value in matched.items():
                totals[family][f"{key}_exact"] += value["exact"]
    return {"families": totals}


def _names(method_row: dict[str, Any]) -> list[str]:
    texts: list[str] = []
    for fact in method_row.get("semantic_facts", []):
        value = fact.get("clinical_name") or fact.get("text")
        if value:
            texts.append(str(value))
    if texts:
        return texts
    prediction = PredictedLetter.model_validate(method_row["prediction"])
    return [mention.text for mention in prediction.mentions]


def _stop_checks(
    letters: list[ExectLetter],
    rows: list[dict[str, Any]],
    summaries: dict[str, Any],
    leftover: dict[str, Any],
) -> dict[str, Any]:
    candidate_empty = {
        method: summaries[method]["empty_gold_extras"] for method in (LLM_METHOD, HYBRID_METHOD)
    }
    v2_empty = {
        LLM_METHOD: summaries["mention_unit_v2_llm"]["empty_gold_extras"],
        HYBRID_METHOD: summaries["mention_unit_v2_llm_with_rules"]["empty_gold_extras"],
    }
    extras_rose = any(
        candidate_empty[method]["mention_counts"]["SeizureFrequency"]
        > v2_empty[method]["mention_counts"]["SeizureFrequency"]
        for method in (LLM_METHOD, HYBRID_METHOD)
    )
    exact_fell = any(
        leftover["sf_exact"][method]["candidate"] < leftover["sf_exact"][method]["v2"]
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
    leftover_moved = bool(leftover.get("moved"))
    if revise:
        verdict = "revise"
    elif leftover_moved:
        verdict = "answer"
    else:
        verdict = "negative_result"
    return {
        "empty_gold_sf_extras_rose": extras_rose,
        "gold_sf_exact_fell": exact_fell,
        "nontarget_mentions": nontargets,
        "hybrid_growth_from_unused_letter": growth,
        "parse_or_schema_failure": parse_fail,
        "leftover_moved": leftover_moved,
        "verdict": verdict,
    }


def _leftover_signals(
    arm: MentionUnitCue5Arm,
    letters: list[ExectLetter],
    rows: list[dict[str, Any]],
    v2_rows: dict[str, dict[str, Any]],
    v2_predictions: dict[str, list[PredictedLetter]],
) -> dict[str, Any]:
    by_id = {letter.letter_id: letter for letter in letters}
    row_by_id = {row["letter_id"]: row for row in rows}
    sf_exact = {}
    for method in (LLM_METHOD, HYBRID_METHOD):
        candidate_exact = 0
        v2_exact = 0
        for letter in letters:
            gold_units = [
                {"text": annotation.text, "raw_text": annotation.raw_text or annotation.text}
                for annotation in letter.entities("SeizureFrequency")
            ]
            candidate_exact += _span_matches(
                gold_units, _names(row_by_id[letter.letter_id]["methods"][method])
            )["exact"]
            v2_names = _names(v2_rows[letter.letter_id]["methods"][method])
            v2_exact += _span_matches(gold_units, v2_names)["exact"]
        sf_exact[method] = {"candidate": candidate_exact, "v2": v2_exact}

    if arm == "heading":
        detail = {
            letter_id: {
                "v2_llm": _names(v2_rows[letter_id]["methods"][LLM_METHOD]),
                "candidate_llm": _names(row_by_id[letter_id]["methods"][LLM_METHOD]),
            }
            for letter_id in HEADING_LETTERS
        }
        moved = any(
            set(map(_norm_span, item["candidate_llm"])) - set(map(_norm_span, item["v2_llm"]))
            for item in detail.values()
        )
        return {"arm": arm, "letters": detail, "moved": moved, "sf_exact": sf_exact}
    if arm == "bare_frame":
        detail = {}
        for letter_id in BARE_FRAME_LETTERS:
            v2_pred = next(
                pred for pred in v2_predictions[LLM_METHOD] if pred.letter_id == letter_id
            )
            cand = PredictedLetter.model_validate(
                row_by_id[letter_id]["methods"][LLM_METHOD]["prediction"]
            )
            detail[letter_id] = {
                "v2_extras": [
                    mention.text
                    for mention in v2_pred.mentions
                    if mention.entity == "SeizureFrequency"
                ],
                "candidate_extras": [
                    mention.text
                    for mention in cand.mentions
                    if mention.entity == "SeizureFrequency"
                ],
            }
        moved = any(
            len(item["candidate_extras"]) < len(item["v2_extras"]) for item in detail.values()
        )
        return {"arm": arm, "letters": detail, "moved": moved, "sf_exact": sf_exact}
    if arm == "one_row":
        over = []
        moved = False
        for letter in letters:
            gold_n = len(letter.entities("SeizureFrequency"))
            if gold_n == 0:
                continue
            v2_n = len(_sf_mentions(v2_rows[letter.letter_id]["methods"][LLM_METHOD]))
            cand_n = len(_sf_mentions(row_by_id[letter.letter_id]["methods"][LLM_METHOD]))
            if v2_n > gold_n:
                over.append(
                    {
                        "letter_id": letter.letter_id,
                        "gold": gold_n,
                        "v2": v2_n,
                        "candidate": cand_n,
                    }
                )
                if cand_n < v2_n:
                    moved = True
        return {"arm": arm, "over_emit_letters": over, "moved": moved, "sf_exact": sf_exact}
    names = _names(row_by_id[NO_JOIN_LETTER]["methods"][LLM_METHOD])
    v2_names = _names(v2_rows[NO_JOIN_LETTER]["methods"][LLM_METHOD])
    bundled = any(" and " in _norm_span(name) for name in names)
    v2_bundled = any(" and " in _norm_span(name) for name in v2_names)
    letter = by_id[NO_JOIN_LETTER]
    gold_units = [
        {"text": annotation.text, "raw_text": annotation.raw_text or annotation.text}
        for annotation in letter.entities("SeizureFrequency")
    ]
    exact = _span_matches(gold_units, names)
    moved = (not bundled and v2_bundled) or (
        exact["exact"] > _span_matches(gold_units, v2_names)["exact"]
    )
    return {
        "arm": arm,
        "letter_id": NO_JOIN_LETTER,
        "v2_llm": v2_names,
        "candidate_llm": names,
        "bundled": bundled,
        "moved": moved,
        "sf_exact": sf_exact,
    }


def _sf_mentions(method_row: dict[str, Any]) -> list[str]:
    prediction = PredictedLetter.model_validate(method_row["prediction"])
    return [mention.text for mention in prediction.mentions if mention.entity == "SeizureFrequency"]


def _load_artifact() -> dict[str, Any]:
    path = STUDY_DIR / "comparison.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _render_report(artifact: dict[str, Any]) -> str:
    lines = [
        "# ExECT mention-unit cue-5 keep sentences — GPT-5.6 Luna `dev20`",
        "",
        "Date: 2026-08-17  ",
        f"Status: {artifact['status']}  ",
        f"Protocol: [{Path(PROTOCOL).name}]({Path(PROTOCOL).name})  ",
        "Parent: [mention-unit v2 `dev20`](mention_unit_v2_fork_a_luna_dev20_2026-08-16.md)",
        "",
        "Mention-unit v2 stays frozen. These four IDs are study-only.",
        "Do not promote. Do not inspect `test60`.",
        "",
        "## Arms",
        "",
        "| Arm | Verdict | SF exact llm | Empty-gold SF extras llm | Leftover moved |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for arm in ARM_ORDER:
        item = artifact.get("arms", {}).get(arm)
        if item is None:
            lines.append(f"| `{arm}` | pending | — | — | — |")
            continue
        stop = item["stop_checks"]
        leftover = item["leftover_signals"]
        v2_exact = leftover["sf_exact"][LLM_METHOD]["v2"]
        cand_exact = leftover["sf_exact"][LLM_METHOD]["candidate"]
        v2_extras = item["methods"]["mention_unit_v2_llm"]["empty_gold_extras"]["mention_counts"][
            "SeizureFrequency"
        ]
        cand_extras = item["methods"][LLM_METHOD]["empty_gold_extras"]["mention_counts"][
            "SeizureFrequency"
        ]
        lines.append(
            f"| `{arm}` | **{stop['verdict']}** | {v2_exact} → {cand_exact} | "
            f"{v2_extras} → {cand_extras} | {leftover['moved']} |"
        )
    lines += [
        "",
        "## Claim boundary",
        "",
        artifact["claim_boundary"],
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
