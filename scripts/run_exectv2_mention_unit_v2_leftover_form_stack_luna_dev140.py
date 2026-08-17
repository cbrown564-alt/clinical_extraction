"""No-call transfer remasure of stacked leftover-form on saved dev140 raws."""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit import (
    HYBRID_METHOD,
    LLM_METHOD,
    MENTION_UNIT_PROMPT_VERSION,
    MentionUnitEncoder,
    materialize_mention_unit,
    parse_mention_unit_json,
)
from scripts.run_exectv2_mention_unit_v2_leftover_form_v3_luna_dev140 import (
    _catalog,
    _form_census,
    _score_method,
)
from scripts.run_exectv2_mention_unit_v2_luna import DEV20_IDS

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/exectv2/"
    "mention_unit_v2_leftover_form_stack_luna_dev140_protocol_2026-08-17.md"
)
REPORT = ROOT / (
    "docs/research/exectv2/"
    "mention_unit_v2_leftover_form_stack_luna_dev140_2026-08-17.md"
)
SOURCE_ROWS = ROOT / "experiments/exectv2_mention_unit_v2_luna_dev140_20260816" / "rows.jsonl"
STUDY_DIR = (
    ROOT / "experiments/exectv2_mention_unit_v2_leftover_form_stack_luna_dev140_20260817"
)
CONTROL: MentionUnitEncoder = "landed"
FORM: MentionUnitEncoder = "leftover_form_intervening_v3"
CANDIDATE: MentionUnitEncoder = "leftover_form_span_fold_fortnight_v10"
ENCODERS: tuple[MentionUnitEncoder, ...] = (CONTROL, FORM, CANDIDATE)
INTENDED_REWRITES = frozenset(
    {"cluster of seizures", "focal seizures with altered awareness"}
)
DEV20 = frozenset(DEV20_IDS)


def main() -> None:
    if not SOURCE_ROWS.exists():
        raise SystemExit(f"missing saved raws: {SOURCE_ROWS}")
    letters = list(load_letters_for_split("dev"))
    if len(letters) != 140:
        raise SystemExit(f"expected 140 development letters, found {len(letters)}")
    by_id = {letter.letter_id: letter for letter in letters}
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()

    rows: list[dict[str, Any]] = []
    gold_in_order = []
    predictions: dict[str, list[PredictedLetter]] = {
        name: [] for name in ("llm", *ENCODERS)
    }
    with SOURCE_ROWS.open(encoding="utf-8") as handle:
        for line in handle:
            saved = json.loads(line)
            letter_id = str(saved["letter_id"])
            letter = by_id[letter_id]
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
    if len(gold_in_order) != 140:
        raise SystemExit(f"expected 140 saved rows, found {len(gold_in_order)}")

    slices = {
        "all140": [letter.letter_id for letter in gold_in_order],
        "dev20": [letter.letter_id for letter in gold_in_order if letter.letter_id in DEV20],
        "rest120": [
            letter.letter_id for letter in gold_in_order if letter.letter_id not in DEV20
        ],
    }
    scored: dict[str, dict[str, Any]] = {}
    for slice_name, letter_ids in slices.items():
        gold, preds = _slice(gold_in_order, predictions, letter_ids)
        scored[slice_name] = {
            "methods": {name: _score_method(gold, preds[name]) for name in preds},
            "form_census": {name: _form_census(preds[name]) for name in preds},
        }
    catalogs = {encoder: _catalog(rows, encoder=encoder) for encoder in ENCODERS}
    named = _named_outcomes(catalogs)
    decision = _decision(scored, catalogs, named)
    artifact = {
        "schema_version": "exectv2.mention_unit_v2_leftover_form_stack.dev140.v1",
        "status": "complete",
        "protocol": PROTOCOL,
        "split": "dev140",
        "row_count": len(rows),
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "control": CONTROL,
        "form_context": FORM,
        "candidate": CANDIDATE,
        "slices": {
            name: {
                "letter_count": len(letter_ids),
                "methods": scored[name]["methods"],
                "form_census": scored[name]["form_census"],
            }
            for name, letter_ids in slices.items()
        },
        "catalog_summary": {
            encoder: catalog["class_counts"] for encoder, catalog in catalogs.items()
        },
        "name_rewritten": {
            encoder: catalogs[encoder]["name_rewritten"] for encoder in ENCODERS
        },
        "named_outcomes": named,
        "decision": decision,
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "claim_boundary": (
            "GPT-5.6 Luna ExECT leftover-form stacked-encoder transfer on "
            "frozen mention-unit v2 dev140 hybrid raws. Not holdout, not a "
            "Decision 0050 change, and not selected-stack parity."
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
                "named_outcomes": {
                    "other_rewrites": named["other_rewrites"],
                    "intended_rewrites": named["intended_rewrites"],
                },
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
        "split": "dev140",
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "raw_output": raw,
        "parse_errors": parsed.errors,
        "hybrid": hybrid,
        "llm_prediction": saved["methods"][LLM_METHOD]["prediction"],
    }


def _slice(
    gold: list[Any],
    predictions: dict[str, list[PredictedLetter]],
    letter_ids: list[str],
) -> tuple[list[Any], dict[str, list[PredictedLetter]]]:
    wanted = set(letter_ids)
    keep = [index for index, letter in enumerate(gold) if letter.letter_id in wanted]
    return (
        [gold[index] for index in keep],
        {name: [rows[index] for index in keep] for name, rows in predictions.items()},
    )


def _named_outcomes(catalogs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    form_other = [
        item
        for item in catalogs[FORM]["items"]
        if item["class"] == "name_rewritten"
    ]
    intended = [
        item
        for item in catalogs[CANDIDATE]["items"]
        if item["class"] == "name_rewritten"
        and item.get("scorer_text") in INTENDED_REWRITES
    ]
    other = [
        item
        for item in catalogs[CANDIDATE]["items"]
        if item["class"] == "name_rewritten"
        and item.get("scorer_text") not in INTENDED_REWRITES
    ]
    form_keys = {
        (item["letter_id"], item.get("clinical_name"), item.get("scorer_text"))
        for item in form_other
    }
    extra_other = [
        item
        for item in other
        if (item["letter_id"], item.get("clinical_name"), item.get("scorer_text"))
        not in form_keys
    ]
    return {
        "intended_rewrites": intended,
        "other_rewrites": other,
        "form_other_rewrites": form_other,
        "extra_other_rewrites": extra_other,
    }


def _decision(
    scored: dict[str, dict[str, Any]],
    catalogs: dict[str, dict[str, Any]],
    named: dict[str, Any],
) -> dict[str, Any]:
    all140 = scored["all140"]["methods"]
    rest = scored["rest120"]["methods"]
    extras = all140[CANDIDATE]["empty_gold_sf_extras"]["mention_count"]
    landed_extras = all140[CONTROL]["empty_gold_sf_extras"]["mention_count"]
    form_extras = all140[FORM]["empty_gold_sf_extras"]["mention_count"]
    rest_extras = rest[CANDIDATE]["empty_gold_sf_extras"]["mention_count"]
    rest_landed_extras = rest[CONTROL]["empty_gold_sf_extras"]["mention_count"]
    headline = all140[CANDIDATE]["clinical_headline_f1"]
    landed_headline = all140[CONTROL]["clinical_headline_f1"]
    rest_headline = rest[CANDIDATE]["clinical_headline_f1"]
    rest_landed_headline = rest[CONTROL]["clinical_headline_f1"]
    sf = all140[CANDIDATE]["clinical_headline_family_f1"]["SeizureFrequency"]
    landed_sf = all140[CONTROL]["clinical_headline_family_f1"]["SeizureFrequency"]
    extras_rose = extras > landed_extras or extras > form_extras
    rest_extras_rose = rest_extras > rest_landed_extras
    ecg = bool(all140[CANDIDATE]["nontarget_mentions"])
    rose_140 = headline > landed_headline or sf > landed_sf
    rose_rest = rest_headline > rest_landed_headline
    extra_rewrites = bool(named["extra_other_rewrites"])
    if extras_rose or rest_extras_rose or ecg or extra_rewrites:
        status = "revise"
    elif rose_140 and rose_rest:
        status = "promote"
    elif rose_140 and not rose_rest:
        status = "hold"
    else:
        status = "negative_result"
    return {
        "status": status,
        "headline_rose_140": headline > landed_headline,
        "sf_rose_140": sf > landed_sf,
        "headline_rose_rest120": rose_rest,
        "control_headline_140": landed_headline,
        "candidate_headline_140": headline,
        "form_headline_140": all140[FORM]["clinical_headline_f1"],
        "control_sf_140": landed_sf,
        "candidate_sf_140": sf,
        "control_headline_rest120": rest_landed_headline,
        "candidate_headline_rest120": rest_headline,
        "empty_gold_sf_extras": extras,
        "control_empty_gold_sf_extras": landed_extras,
        "form_empty_gold_sf_extras": form_extras,
        "rest120_empty_gold_sf_extras": rest_extras,
        "rest120_control_empty_gold_sf_extras": rest_landed_extras,
        "extras_rose": extras_rose,
        "rest_extras_rose": rest_extras_rose,
        "ecg": ecg,
        "extra_other_rewrites": extra_rewrites,
        "sf_with_count": scored["all140"]["form_census"][CANDIDATE]["sf_with_count"],
        "control_sf_with_count": scored["all140"]["form_census"][CONTROL]["sf_with_count"],
        "form_sf_with_count": scored["all140"]["form_census"][FORM]["sf_with_count"],
        "name_rewritten": catalogs[CANDIDATE]["name_rewritten"],
    }


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
        "# ExECT leftover-form stacked encoder transfer on mention-unit v2 `dev140`",
        "",
        "Date: 2026-08-17  ",
        f"Status: complete; **{decision['status']}**  ",
        f"Protocol: [{Path(PROTOCOL).name}]({Path(PROTOCOL).name})  ",
        "Parent: [fortnight `dev20`](mention_unit_v2_fortnight_luna_dev20_2026-08-17.md)",
        "",
        "`model_calls`: 0. Saved mention-unit v2 hybrid raws only.",
        "",
        "## Headlines",
        "",
        "| Slice | Arm | Headline | SF | extras |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for slice_name in ("all140", "dev20", "rest120"):
        slice_payload = artifact["slices"][slice_name]
        for name in ("llm", *ENCODERS):
            method = slice_payload["methods"][name]
            family = method["clinical_headline_family_f1"]
            extras = method["empty_gold_sf_extras"]["mention_count"]
            lines.append(
                f"| `{slice_name}` | `{name}` | "
                f"{method['clinical_headline_f1']:.4f} | "
                f"{family['SeizureFrequency']:.4f} | {extras} |"
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
