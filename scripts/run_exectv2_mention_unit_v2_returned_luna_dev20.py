"""No-call remasure of returned-after-freedom change on negation v9 dev20."""

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
PROTOCOL = "docs/research/exectv2/mention_unit_v2_returned_luna_dev20_protocol_2026-08-17.md"
REPORT = ROOT / "docs/research/exectv2/mention_unit_v2_returned_luna_dev20_2026-08-17.md"
SOURCE_ROWS = ROOT / "experiments/exectv2_mention_unit_v2_luna_dev20_20260816" / "rows.jsonl"
STUDY_DIR = ROOT / "experiments/exectv2_mention_unit_v2_returned_luna_dev20_20260817"
CONTROL: MentionUnitEncoder = "leftover_form_span_fold_negation_v9"
CANDIDATE: MentionUnitEncoder = "leftover_form_span_fold_returned_v11"
ENCODERS: tuple[MentionUnitEncoder, ...] = ("landed", CONTROL, CANDIDATE)
INTENDED_REWRITES = frozenset(
    {"focal seizures with altered awareness", "cluster of seizures"}
)
UNUSED_DROPS: tuple[tuple[str, str], ...] = (
    ("EA0005", "absences"),
    ("EA0005", "myoclonus"),
    ("EA0005", "focal seizures"),
)
KEEP_NAMES: tuple[tuple[str, str], ...] = (
    ("EA0005", "Generalised tonic clonic seizure"),
    ("EA0005", "seizures"),
    ("EA0002", "focal seizures"),
    ("EA0008", "focal seizures with altered awareness"),
    ("EA0009", "cluster of seizures"),
    ("EA0133", "Focal seizures"),
    ("EA0120", "seizures"),
)
FEBRILE_DROPS: tuple[tuple[str, str], ...] = (
    ("EA0009", "febrile seizures"),
    ("EA0010", "Febrile seizures"),
    ("EA0011", "Febrile seizures"),
    ("EA0133", "Febrile seizures"),
)
EA0008_RETURNED = (
    "Unfortunately after the period of seizure freedom the seizures have returned."
)
QUALITATIVE_MARKERS = ("worse", "quite a number", "risk")


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
    named = _named_outcomes(predictions, catalogs)
    leftovers = _sf_first_failures(gold_in_order, predictions)
    decision = _decision(methods, form, catalogs, named)
    artifact = {
        "schema_version": "exectv2.mention_unit_v2_returned.dev20.v1",
        "status": "complete",
        "protocol": PROTOCOL,
        "split": "dev20",
        "row_count": len(rows),
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "control": CONTROL,
        "candidate": CANDIDATE,
        "methods": methods,
        "form_census": form,
        "catalog_summary": {
            encoder: catalog["class_counts"] for encoder, catalog in catalogs.items()
        },
        "name_rewritten": {
            encoder: catalogs[encoder]["name_rewritten"] for encoder in ENCODERS
        },
        "named_outcomes": named,
        "sf_first_failures": leftovers,
        "decision": decision,
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "claim_boundary": (
            "GPT-5.6 Luna ExECT leftover-form returned-after-freedom remasure "
            "on frozen mention-unit v2 dev20 hybrid raws. Not holdout, not a "
            "selected encoder, and not a Decision 0050 change."
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
                "sf": {
                    name: summary["clinical_headline_family_f1"]["SeizureFrequency"]
                    for name, summary in methods.items()
                },
                "named_outcomes": named,
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


def _sf_names(predictions: dict[str, list[PredictedLetter]], encoder: str) -> set[tuple[str, str]]:
    names: set[tuple[str, str]] = set()
    for prediction in predictions[encoder]:
        for mention in prediction.mentions:
            if mention.entity == "SeizureFrequency":
                names.add((prediction.letter_id, mention.text))
    return names


def _named_outcomes(
    predictions: dict[str, list[PredictedLetter]],
    catalogs: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    candidate_names = _sf_names(predictions, CANDIDATE)
    keeps = [
        {"letter_id": letter_id, "clinical_name": name}
        for letter_id, name in KEEP_NAMES
        if (letter_id, name) in candidate_names
    ]
    lost_keeps = [
        {"letter_id": letter_id, "clinical_name": name}
        for letter_id, name in KEEP_NAMES
        if (letter_id, name) not in candidate_names
    ]
    unused_returned = [
        {"letter_id": letter_id, "clinical_name": name}
        for letter_id, name in UNUSED_DROPS
        if (letter_id, name) in candidate_names
    ]
    febrile_returned = [
        {"letter_id": letter_id, "clinical_name": name}
        for letter_id, name in FEBRILE_DROPS
        if (letter_id, name) in candidate_names
    ]
    other_rewrites = [
        item
        for item in catalogs[CANDIDATE]["items"]
        if item["class"] == "name_rewritten"
        and item.get("scorer_text") not in INTENDED_REWRITES
    ]
    returned = None
    last_event_zeros: list[dict[str, Any]] = []
    qualitative_parsed: list[dict[str, Any]] = []
    for prediction in predictions[CANDIDATE]:
        for mention in prediction.mentions:
            if mention.entity != "SeizureFrequency":
                continue
            if mention.evidence == EA0008_RETURNED:
                returned = {
                    "letter_id": prediction.letter_id,
                    "clinical_name": mention.text,
                    "frequency_change": mention.attributes.get("FrequencyChange"),
                    "count": mention.attributes.get("NumberOfSeizures"),
                }
            if mention.attributes.get("NumberOfSeizures") == "0":
                last_event_zeros.append(
                    {
                        "letter_id": prediction.letter_id,
                        "clinical_name": mention.text,
                        "evidence": mention.evidence,
                    }
                )
            evidence_l = mention.evidence.lower()
            if mention.attributes.get("FrequencyChange") and any(
                marker in evidence_l for marker in QUALITATIVE_MARKERS
            ):
                qualitative_parsed.append(
                    {
                        "letter_id": prediction.letter_id,
                        "clinical_name": mention.text,
                        "evidence": mention.evidence,
                        "frequency_change": mention.attributes.get("FrequencyChange"),
                    }
                )
    recovered = (
        returned is not None
        and returned["frequency_change"] == "Increased"
        and returned["count"] is None
        and returned["clinical_name"] == "seizures"
    )
    last_event_kept = any(
        item["letter_id"] == "EA0120" and item["clinical_name"] == "seizures"
        for item in last_event_zeros
    )
    return {
        "returned_recovered": recovered,
        "ea0008_returned": returned,
        "last_event_kept": last_event_kept,
        "qualitative_parsed": qualitative_parsed,
        "keeps": keeps,
        "lost_keeps": lost_keeps,
        "unused_returned": unused_returned,
        "febrile_returned": febrile_returned,
        "other_rewrites": other_rewrites,
    }


def _decision(
    methods: dict[str, dict[str, Any]],
    form: dict[str, dict[str, int]],
    catalogs: dict[str, dict[str, Any]],
    named: dict[str, Any],
) -> dict[str, Any]:
    extras = methods[CANDIDATE]["empty_gold_sf_extras"]["mention_count"]
    control_extras = methods[CONTROL]["empty_gold_sf_extras"]["mention_count"]
    ecg = bool(methods[CANDIDATE]["nontarget_mentions"])
    headline = methods[CANDIDATE]["clinical_headline_f1"]
    control_headline = methods[CONTROL]["clinical_headline_f1"]
    sf = methods[CANDIDATE]["clinical_headline_family_f1"]["SeizureFrequency"]
    control_sf = methods[CONTROL]["clinical_headline_family_f1"]["SeizureFrequency"]
    extras_rose = extras > control_extras
    rose = headline > control_headline or sf > control_sf
    damaged = bool(
        named["lost_keeps"]
        or named["febrile_returned"]
        or named["other_rewrites"]
        or named["unused_returned"]
        or named["qualitative_parsed"]
        or not named["last_event_kept"]
    )
    if extras_rose or ecg or damaged:
        status = "revise"
    elif named["returned_recovered"] and rose:
        status = "answer"
    elif named["returned_recovered"] and not rose:
        status = "negative_result"
    else:
        status = "revise"
    return {
        "status": status,
        "headline_rose": headline > control_headline,
        "sf_rose": sf > control_sf,
        "control_headline": control_headline,
        "candidate_headline": headline,
        "control_sf": control_sf,
        "candidate_sf": sf,
        "extras_rose": extras_rose,
        "ecg": ecg,
        "returned_recovered": named["returned_recovered"],
        "last_event_kept": named["last_event_kept"],
        "empty_gold_sf_extras": extras,
        "control_empty_gold_sf_extras": control_extras,
        "sf_with_count": form[CANDIDATE]["sf_with_count"],
        "control_sf_with_count": form[CONTROL]["sf_with_count"],
        "name_rewritten": catalogs[CANDIDATE]["name_rewritten"],
    }


def _sf_first_failures(
    gold: list[Any],
    predictions: dict[str, list[PredictedLetter]],
) -> dict[str, Any]:
    failures: dict[str, list[dict[str, Any]]] = {CONTROL: [], CANDIDATE: []}
    for name in (CONTROL, CANDIDATE):
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
    return failures


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
        "# ExECT leftover-form returned-after-freedom on mention-unit v2 `dev20`",
        "",
        "Date: 2026-08-17  ",
        f"Status: complete; **{decision['status']}**  ",
        f"Protocol: [{Path(PROTOCOL).name}]({Path(PROTOCOL).name})  ",
        "Parent: [combination](mention_unit_cheap_combo_luna_dev20_2026-08-17.md); "
        "[negation `dev20`](mention_unit_v2_negation_luna_dev20_2026-08-17.md)",
        "",
        "`model_calls`: 0. Saved mention-unit v2 hybrid raws only.",
        "",
        "## Headlines",
        "",
        "| Arm | Headline | SF | Dx | Rx | Ix | SF-with-count | extras |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name in ("llm", *ENCODERS):
        method = artifact["methods"][name]
        family = method["clinical_headline_family_f1"]
        form = artifact["form_census"][name]
        extras = method["empty_gold_sf_extras"]["mention_count"]
        lines.append(
            f"| `{name}` | {method['clinical_headline_f1']:.4f} | "
            f"{family['SeizureFrequency']:.4f} | {family['Diagnosis']:.4f} | "
            f"{family['Prescription']:.4f} | {family['Investigations']:.4f} | "
            f"{form['sf_with_count']} | {extras} |"
        )
    lines += [
        "",
        f"Returned change recovered: {artifact['named_outcomes']['returned_recovered']}.",
        f"Last-event zero kept: {artifact['named_outcomes']['last_event_kept']}.",
        "",
        "## Claim boundary",
        "",
        artifact["claim_boundary"],
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
