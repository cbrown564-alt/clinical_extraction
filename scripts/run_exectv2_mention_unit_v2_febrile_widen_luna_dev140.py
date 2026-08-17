"""No-call remasure of childhood-febrile predicate widen on the leftover-form stack."""

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
    "mention_unit_v2_febrile_widen_luna_dev140_protocol_2026-08-17.md"
)
REPORT = ROOT / (
    "docs/research/exectv2/mention_unit_v2_febrile_widen_luna_dev140_2026-08-17.md"
)
SOURCE_ROWS = ROOT / "experiments/exectv2_mention_unit_v2_luna_dev140_20260816" / "rows.jsonl"
STUDY_DIR = (
    ROOT / "experiments/exectv2_mention_unit_v2_febrile_widen_luna_dev140_20260817"
)
CONTROL: MentionUnitEncoder = "leftover_form_span_fold_absences_v13"
FORM: MentionUnitEncoder = "leftover_form_intervening_v3"
CANDIDATE: MentionUnitEncoder = "leftover_form_span_fold_febrile_v14"
ENCODERS: tuple[MentionUnitEncoder, ...] = ("landed", FORM, CONTROL, CANDIDATE)
DEV20 = frozenset(DEV20_IDS)
INTENDED_REWRITES = frozenset(
    {"cluster of seizures", "focal seizures with altered awareness"}
)
NAMED_DROPS: tuple[tuple[str, str], ...] = (
    ("EA0125", "She did have a febrile seizure the age of four years"),
    ("EA0190", "3 febrile seizures between the ages of 3 and 5"),
)
STILL_DROPPED: tuple[tuple[str, str], ...] = (
    ("EA0009", "2 febrile seizures at the age of 2 months and 34 months"),
    ("EA0010", "4 febrile seizures at the age of 3, 4 and then around five"),
    ("EA0061", "He had a febrile seizure at the age of 3."),
    ("EA0133", "2 febrile seizures at the age of 8 months and 18 months"),
    ("EA0141", "between the age of 1 and 3"),
    ("EA0164", "He had one febrile seizure at the age of 2."),
    ("EA0179", "two febrile convulsions at the age of around 3"),
)
ABSENCE_KEEPS: tuple[tuple[str, str], ...] = (
    ("EA0161", "The absences continue to happen maybe every week"),
    ("EA0049", "Occasional absences."),
    ("EA0050", "Occasional absences."),
    ("EA0096", "frequent drops and absences throughout the day"),
    ("EA0184", "more of his typical absences since the last clinic appointment"),
)
HISTORY_DROP = ("EA0128", "There's no history of absences.")
DROP_ATTACKS = ("EA0126", "drop attacks")
IMPLICIT_KEEPS: tuple[tuple[str, str, str, str], ...] = (
    ("EA0049", "Myoclonic jerks daily", "1", "Day"),
    ("EA0050", "Myoclonic jerks weekly", "1", "Week"),
    ("EA0056", "every month", "1", "Month"),
    ("EA0056", "every year", "1", "Year"),
    ("EA0057", "every month", "1", "Month"),
    ("EA0111", "on a weekly basis", "1", "Week"),
    ("EA0117", "on a weekly basis", "1", "Week"),
    ("EA0132", "happening weekly", "1", "Week"),
    ("EA0043", "every year", "1", "Year"),
)


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
            letter = by_id[str(saved["letter_id"])]
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
    named = _named_outcomes(rows, catalogs)
    decision = _decision(scored, named)
    artifact = {
        "schema_version": "exectv2.mention_unit_v2_febrile_widen.dev140.v1",
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
        "named_outcomes": named,
        "decision": decision,
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "claim_boundary": (
            "GPT-5.6 Luna ExECT leftover-form childhood-febrile widen remasure "
            "on frozen mention-unit v2 dev140 hybrid raws. Not holdout, not a "
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
    print(json.dumps({"model_calls": 0, "decision": decision, "named_outcomes": named}, indent=2))


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


def _named_outcomes(
    rows: list[dict[str, Any]], catalogs: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    by_id = {row["letter_id"]: row for row in rows}
    dropped: list[dict[str, Any]] = []
    missed: list[dict[str, Any]] = []
    for letter_id, cue in NAMED_DROPS:
        control = _mention_with_cue(by_id[letter_id], CONTROL, cue)
        candidate = _mention_with_cue(by_id[letter_id], CANDIDATE, cue)
        item = {
            "letter_id": letter_id,
            "cue": cue,
            "control_present": control is not None,
            "candidate_present": candidate is not None,
            "dropped": control is not None and candidate is None,
        }
        (dropped if item["dropped"] else missed).append(item)
    still_dropped = []
    still_kept = []
    for letter_id, cue in STILL_DROPPED:
        present = _mention_with_cue(by_id[letter_id], CANDIDATE, cue) is not None
        item = {"letter_id": letter_id, "cue": cue, "present": present}
        (still_kept if present else still_dropped).append(item)
    absence_kept = []
    absence_lost = []
    for letter_id, cue in ABSENCE_KEEPS:
        mention = _mention_with_cue(by_id[letter_id], CANDIDATE, cue, name="absences")
        item = {"letter_id": letter_id, "cue": cue, "kept": mention is not None}
        (absence_kept if mention is not None else absence_lost).append(item)
    implicit_kept = []
    implicit_missed = []
    for letter_id, cue, count, period in IMPLICIT_KEEPS:
        mention = _mention_with_cue(by_id[letter_id], CANDIDATE, cue)
        landed = bool(
            mention
            and mention.attributes.get("NumberOfSeizures") == count
            and mention.attributes.get("TimePeriod") == period
        )
        (implicit_kept if landed else implicit_missed).append(
            {"letter_id": letter_id, "cue": cue, "landed": landed}
        )
    other = [
        item
        for item in catalogs[CANDIDATE]["items"]
        if item["class"] == "name_rewritten"
        and item.get("scorer_text") not in INTENDED_REWRITES
    ]
    control_other = [
        item
        for item in catalogs[CONTROL]["items"]
        if item["class"] == "name_rewritten"
        and item.get("scorer_text") not in INTENDED_REWRITES
    ]
    return {
        "dropped": dropped,
        "missed": missed,
        "still_dropped": still_dropped,
        "still_kept": still_kept,
        "absence_kept": absence_kept,
        "absence_lost": absence_lost,
        "history_dropped": _mention_with_cue(
            by_id[HISTORY_DROP[0]], CANDIDATE, HISTORY_DROP[1], name="absences"
        )
        is None,
        "drop_attacks_dropped": _mention_with_name(
            by_id[DROP_ATTACKS[0]], CANDIDATE, DROP_ATTACKS[1]
        )
        is None,
        "implicit_kept": implicit_kept,
        "implicit_missed": implicit_missed,
        "other_rewrites": other,
        "control_other_rewrites": control_other,
        "extra_other_rewrites": [
            item
            for item in other
            if (item["letter_id"], item.get("clinical_name"), item.get("scorer_text"))
            not in {
                (row["letter_id"], row.get("clinical_name"), row.get("scorer_text"))
                for row in control_other
            }
        ],
    }


def _mention_with_cue(
    row: dict[str, Any],
    encoder: str,
    cue: str,
    *,
    name: str | None = None,
) -> Any | None:
    prediction = PredictedLetter.model_validate(row["hybrid"][encoder]["prediction"])
    matches = [
        mention
        for mention in prediction.mentions
        if mention.entity == "SeizureFrequency"
        and cue.casefold() in mention.evidence.casefold()
        and (name is None or mention.text.casefold() == name)
    ]
    return matches[0] if matches else None


def _mention_with_name(row: dict[str, Any], encoder: str, name: str) -> Any | None:
    prediction = PredictedLetter.model_validate(row["hybrid"][encoder]["prediction"])
    matches = [
        mention
        for mention in prediction.mentions
        if mention.entity == "SeizureFrequency" and mention.text.casefold() == name
    ]
    return matches[0] if matches else None


def _decision(
    scored: dict[str, dict[str, Any]],
    named: dict[str, Any],
) -> dict[str, Any]:
    all140 = scored["all140"]["methods"]
    rest = scored["rest120"]["methods"]
    extras = all140[CANDIDATE]["empty_gold_sf_extras"]["mention_count"]
    control_extras = all140[CONTROL]["empty_gold_sf_extras"]["mention_count"]
    rest_extras = rest[CANDIDATE]["empty_gold_sf_extras"]["mention_count"]
    rest_control_extras = rest[CONTROL]["empty_gold_sf_extras"]["mention_count"]
    extras_rose = extras > control_extras or rest_extras > rest_control_extras
    dropped = len(named["dropped"])
    missed = len(named["missed"])
    headline = all140[CANDIDATE]["clinical_headline_f1"]
    control_headline = all140[CONTROL]["clinical_headline_f1"]
    sf = all140[CANDIDATE]["clinical_headline_family_f1"]["SeizureFrequency"]
    control_sf = all140[CONTROL]["clinical_headline_family_f1"]["SeizureFrequency"]
    ecg = bool(all140[CANDIDATE]["nontarget_mentions"])
    extra_rewrites = bool(named["extra_other_rewrites"])
    guards = (
        bool(named["still_kept"])
        or bool(named["absence_lost"])
        or bool(named["implicit_missed"])
        or not named["history_dropped"]
        or not named["drop_attacks_dropped"]
    )
    if extras_rose or extra_rewrites or ecg or guards:
        status = "revise"
        mechanism = "febrile_v14_guard_or_extras"
    elif missed:
        status = "reject"
        mechanism = "febrile_v14_named_drop_unmoved"
    elif headline > control_headline or sf > control_sf:
        status = "answer"
        mechanism = "childhood_febrile_predicate_widened"
    else:
        status = "negative_result"
        mechanism = "childhood_febrile_widened_headline_unchanged"
    return {
        "status": status,
        "mechanism": mechanism,
        "dropped": dropped,
        "missed": missed,
        "still_kept": len(named["still_kept"]),
        "absence_lost": len(named["absence_lost"]),
        "implicit_missed": len(named["implicit_missed"]),
        "history_dropped": named["history_dropped"],
        "drop_attacks_dropped": named["drop_attacks_dropped"],
        "extras_rose": extras_rose,
        "empty_gold_sf_extras": extras,
        "control_empty_gold_sf_extras": control_extras,
        "rest120_empty_gold_sf_extras": rest_extras,
        "rest120_control_empty_gold_sf_extras": rest_control_extras,
        "candidate_headline_140": headline,
        "control_headline_140": control_headline,
        "candidate_sf_140": sf,
        "control_sf_140": control_sf,
        "sf_with_count": scored["all140"]["form_census"][CANDIDATE]["sf_with_count"],
        "control_sf_with_count": scored["all140"]["form_census"][CONTROL]["sf_with_count"],
        "ecg": ecg,
        "extra_other_rewrites": extra_rewrites,
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
    return (
        "# ExECT leftover-form childhood-febrile predicate widen, "
        "mention-unit v2 `dev140`\n\n"
        f"Date: 2026-08-17  \n"
        f"Status: complete; **{decision['status']}**  \n"
        f"Protocol: [febrile widen `dev140`]({Path(PROTOCOL).name})  \n"
        "Parent: [error analysis `dev140`]"
        "(mention_unit_v2_leftover_form_stack_error_analysis_luna_dev140_2026-08-17.md)\n\n"
        "`model_calls`: 0. Draft rendered by the remasure script. "
        "Replace with the inspected report.\n"
    )


if __name__ == "__main__":
    main()
