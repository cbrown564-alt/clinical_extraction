"""No-call remasure of leftover-form answers on frozen mention-unit v2 dev20."""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit import (
    HYBRID_METHOD,
    LLM_METHOD,
    MENTION_UNIT_PROMPT_VERSION,
    MentionUnitEncoder,
    materialize_mention_unit,
    parse_mention_unit_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    score_frequency_state,
)
from scripts.run_exectv2_mention_unit_v2_leftover_form_v3_luna_dev140 import (
    _catalog,
    _form_census,
    _score_method,
)
from scripts.run_exectv2_mention_unit_v2_luna import DEV20_IDS, _load_dev20

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/exectv2/mention_unit_v2_leftover_form_luna_dev20_protocol_2026-08-17.md"
REPORT = ROOT / "docs/research/exectv2/mention_unit_v2_leftover_form_luna_dev20_2026-08-17.md"
SOURCE_ROWS = ROOT / "experiments/exectv2_mention_unit_v2_luna_dev20_20260816" / "rows.jsonl"
STUDY_DIR = ROOT / "experiments/exectv2_mention_unit_v2_leftover_form_luna_dev20_20260817"
ENCODERS: tuple[MentionUnitEncoder, ...] = (
    "landed",
    "leftover_form",
    "leftover_form_intervening_v3",
    "leftover_form_episodes_v4",
    "leftover_form_implicit_v4",
)
HEADLINE_TARGET = 0.8


def main() -> None:
    if not SOURCE_ROWS.exists():
        raise SystemExit(f"missing saved raws: {SOURCE_ROWS}")
    letters = {letter.letter_id: letter for letter in _load_dev20()}
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()

    rows: list[dict[str, Any]] = []
    gold_in_order = []
    predictions: dict[str, list[PredictedLetter]] = {name: [] for name in ("llm", *ENCODERS)}
    with SOURCE_ROWS.open(encoding="utf-8") as handle:
        for line in handle:
            saved = json.loads(line)
            letter_id = str(saved["letter_id"])
            if letter_id not in DEV20_IDS:
                continue
            letter = letters[letter_id]
            gold_in_order.append(letter)
            row = _rematerialize_row(letter, saved)
            rows.append(row)
            predictions["llm"].append(
                PredictedLetter.model_validate(saved["methods"][LLM_METHOD]["prediction"])
            )
            for encoder in ENCODERS:
                predictions[encoder].append(
                    PredictedLetter.model_validate(row["hybrid"][encoder]["prediction"])
                )
    if [letter.letter_id for letter in gold_in_order] != sorted(DEV20_IDS):
        raise SystemExit("frozen dev20 rows are missing or reordered")

    methods = {name: _score_method(gold_in_order, predictions[name]) for name in predictions}
    form = {name: _form_census(predictions[name]) for name in predictions}
    catalogs = {encoder: _catalog(rows, encoder=encoder) for encoder in ENCODERS}
    leftovers = _sf_first_failures(gold_in_order, predictions)
    decision = _decision(methods, form, catalogs)
    artifact = {
        "schema_version": "exectv2.mention_unit_v2_leftover_form.dev20.v1",
        "status": "complete",
        "protocol": PROTOCOL,
        "split": "dev20",
        "row_count": len(rows),
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "headline_target": HEADLINE_TARGET,
        "methods": methods,
        "form_census": form,
        "catalog_summary": {
            encoder: catalog["class_counts"] for encoder, catalog in catalogs.items()
        },
        "name_rewritten": {
            encoder: catalogs[encoder]["name_rewritten"] for encoder in ENCODERS
        },
        "sf_first_failures": leftovers,
        "decision": decision,
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "claim_boundary": (
            "GPT-5.6 Luna ExECT leftover-form remasure on frozen mention-unit "
            "v2 dev20 hybrid raws. Not holdout, not a selected encoder, and "
            "not a Decision 0050 change."
        ),
    }
    (STUDY_DIR / "comparison.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (STUDY_DIR / "damage_catalog.json").write_text(
        json.dumps(catalogs, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (STUDY_DIR / "rows.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    REPORT.write_text(_render_report(artifact), encoding="utf-8")
    print(
        json.dumps(
            {
                "model_calls": 0,
                "decision": decision,
                "clinical_headline": {
                    name: summary["clinical_headline_f1"]
                    for name, summary in methods.items()
                },
                "form_census": form,
                "catalog_summary": artifact["catalog_summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )


def _rematerialize_row(letter: Any, saved: dict[str, Any]) -> dict[str, Any]:
    raw = str(saved["methods"][HYBRID_METHOD]["raw_output"])
    parsed = parse_mention_unit_json(raw, method=HYBRID_METHOD)
    hybrid: dict[str, Any] = {}
    for encoder in ENCODERS:
        if parsed.record is None:
            prediction = PredictedLetter(letter_id=letter.letter_id, mentions=())
            payload = {
                "semantic_facts": [],
                "rule_trace": [],
                "warnings": [],
                "evidence_invalid": 0,
                "prediction": prediction.model_dump(mode="json"),
            }
        else:
            materialized = materialize_mention_unit(
                letter,
                parsed.record,
                method=HYBRID_METHOD,
                encoder=encoder,
            )
            payload = {
                "semantic_facts": materialized.semantic_facts,
                "rule_trace": materialized.rule_trace,
                "warnings": materialized.warnings,
                "evidence_invalid": materialized.evidence_invalid,
                "prediction": materialized.prediction.model_dump(mode="json"),
            }
        hybrid[encoder] = payload
    return {
        "letter_id": letter.letter_id,
        "split": "dev20",
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "raw_output": raw,
        "parse_errors": parsed.errors,
        "hybrid": hybrid,
        "llm_prediction": saved["methods"][LLM_METHOD]["prediction"],
    }


def _decision(
    methods: dict[str, dict[str, Any]],
    form: dict[str, dict[str, int]],
    catalogs: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    landed_extras = methods["landed"]["empty_gold_sf_extras"]["mention_count"]
    landed_names = catalogs["landed"]["name_rewritten"]
    arms = {}
    reached = []
    for encoder in ENCODERS:
        extras = methods[encoder]["empty_gold_sf_extras"]["mention_count"]
        names = catalogs[encoder]["name_rewritten"]
        ecg = bool(methods[encoder]["nontarget_mentions"])
        headline = methods[encoder]["clinical_headline_f1"]
        extras_rose = extras > landed_extras
        names_rose = names > landed_names
        if extras_rose or names_rose or ecg:
            verdict = "revise"
        elif headline >= HEADLINE_TARGET:
            verdict = "answer"
            reached.append(encoder)
        else:
            verdict = "negative_result"
        arms[encoder] = {
            "verdict": verdict,
            "clinical_headline_f1": headline,
            "sf_with_count": form[encoder]["sf_with_count"],
            "empty_gold_sf_extras": extras,
            "extras_rose": extras_rose,
            "names_rewritten": names,
            "ecg": ecg,
        }
    if reached:
        status = "answer"
    elif any(arm["verdict"] == "revise" for arm in arms.values() if arm is not arms["landed"]):
        status = "revise"
    else:
        status = "negative_result"
    return {
        "status": status,
        "headline_target": HEADLINE_TARGET,
        "reached_target": reached,
        "llm_headline": methods["llm"]["clinical_headline_f1"],
        "landed_headline": methods["landed"]["clinical_headline_f1"],
        "arms": arms,
    }


def _sf_first_failures(
    gold: list[Any],
    predictions: dict[str, list[PredictedLetter]],
) -> dict[str, Any]:
    """Letter-level SF headline misses for llm and the best leftover-form arm."""

    leftover_best = max(
        (name for name in ENCODERS if name != "landed"),
        key=lambda name: _score_method(gold, predictions[name])["clinical_headline_f1"],
    )
    failures: dict[str, list[dict[str, Any]]] = {"llm": [], leftover_best: []}
    for name in ("llm", leftover_best):
        for letter, prediction in zip(gold, predictions[name], strict=True):
            score = score_frequency_state(
                [letter], [to_exect_letter(prediction)]
            ).clinical_headline
            if score.f1 >= 1.0:
                continue
            failures[name].append(
                {
                    "letter_id": letter.letter_id,
                    "f1": round(score.f1, 4),
                    "tp": int(score.tp),
                    "fp": int(score.fp),
                    "fn": int(score.fn),
                    "gold": [annotation.text for annotation in letter.entities("SeizureFrequency")],
                    "pred": [
                        mention.text
                        for mention in prediction.mentions
                        if mention.entity == "SeizureFrequency"
                    ],
                }
            )
    return {"best_leftover_encoder": leftover_best, "letters": failures}


def _provenance() -> dict[str, Any]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    dirty = bool(
        subprocess.run(
            ["git", "status", "--porcelain"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout.strip()
    )
    return {"git_head": commit, "dirty_tree": dirty}


def _render_report(artifact: dict[str, Any]) -> str:
    decision = artifact["decision"]
    lines = [
        "# ExECT leftover-form answers on mention-unit v2 `dev20`",
        "",
        "Date: 2026-08-17  ",
        f"Status: complete; **{decision['status']}**  ",
        f"Protocol: [{Path(PROTOCOL).name}]({Path(PROTOCOL).name})  ",
        "Parent: [mention-unit v2 `dev20`](mention_unit_v2_fork_a_luna_dev20_2026-08-16.md)",
        "",
        "`model_calls`: 0. Saved mention-unit v2 hybrid raws only.",
        "",
        "## Headlines",
        "",
        "| Arm | Headline | SF | Diagnosis | Prescription | Investigations | SF-with-count |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name in ("llm", *ENCODERS):
        method = artifact["methods"][name]
        family = method["clinical_headline_family_f1"]
        form = artifact["form_census"][name]
        lines.append(
            f"| `{name}` | {method['clinical_headline_f1']:.4f} | "
            f"{family['SeizureFrequency']:.4f} | {family['Diagnosis']:.4f} | "
            f"{family['Prescription']:.4f} | {family['Investigations']:.4f} | "
            f"{form['sf_with_count']} |"
        )
    lines += [
        "",
        f"Target: `{HEADLINE_TARGET}`. Reached: {decision['reached_target'] or 'none'}.",
        "",
        "## Claim boundary",
        "",
        artifact["claim_boundary"],
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
