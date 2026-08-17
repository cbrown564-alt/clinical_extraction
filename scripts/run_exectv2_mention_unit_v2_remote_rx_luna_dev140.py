"""Closed-study remasure of the former remote+rx stack.

Living encoder identities are landed and leftover_form. This script
names historical identities and will not re-run on the living head.
"""

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
from scripts.run_exectv2_mention_unit_v2_febrile_widen_luna_dev140 import _slice
from scripts.run_exectv2_mention_unit_v2_leftover_form_v3_luna_dev140 import (
    _form_census,
    _score_method,
)
from scripts.run_exectv2_mention_unit_v2_luna import DEV20_IDS
from scripts.run_exectv2_mention_unit_v2_remote_history_luna_dev140 import (
    _mention_with_cue,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/exectv2/mention_unit_v2_remote_rx_luna_dev140_protocol_2026-08-17.md"
)
REPORT = ROOT / (
    "docs/research/exectv2/mention_unit_v2_remote_rx_luna_dev140_2026-08-17.md"
)
SOURCE_ROWS = ROOT / "experiments/exectv2_mention_unit_v2_luna_dev140_20260816" / "rows.jsonl"
STUDY_DIR = ROOT / "experiments/exectv2_mention_unit_v2_remote_rx_luna_dev140_20260817"
PARENT: MentionUnitEncoder = "leftover_form_span_fold_febrile_v14"
REMOTE: MentionUnitEncoder = "leftover_form_span_fold_remote_v15"
RX: MentionUnitEncoder = "leftover_form_span_fold_rx_dose_v21"
CANDIDATE: MentionUnitEncoder = "leftover_form_span_fold_remote_rx_v22"
ENCODERS: tuple[MentionUnitEncoder, ...] = (PARENT, REMOTE, RX, CANDIDATE)
DEV20 = frozenset(DEV20_IDS)
V14_EMPTY_GOLD_SF = 54
V14_REST120_EMPTY_GOLD_SF = 51
EA0010_CUE = (
    "His last seizures were in his teenage years where he probably "
    "had around 3 or 4 focal to bilateral convulsive seizures."
)
EA0011_CUE = (
    "he did have around 3 febrile seizures between the age of 1 year "
    "and 30 months."
)
EA0158_CUE = (
    "Jennifer’s seizures started at the age of 2 years and have continued every since."
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
    predictions: dict[str, list[PredictedLetter]] = {name: [] for name in ENCODERS}
    with SOURCE_ROWS.open(encoding="utf-8") as handle:
        for line in handle:
            saved = json.loads(line)
            letter = by_id[str(saved["letter_id"])]
            gold_in_order.append(letter)
            row = _rematerialize_row(letter, saved)
            rows.append(row)
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
    named = _named_leftovers(rows)
    decision = _decision(scored, named)
    artifact = {
        "schema_version": "exectv2.mention_unit_v2_remote_rx.dev140.v1",
        "status": "complete",
        "protocol": PROTOCOL,
        "split": "dev140",
        "row_count": len(rows),
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "control": PARENT,
        "siblings": [REMOTE, RX],
        "candidate": CANDIDATE,
        "named_leftovers": named,
        "decision": decision,
        "slices": {
            name: {
                "letter_count": len(letter_ids),
                "methods": scored[name]["methods"],
                "form_census": scored[name]["form_census"],
            }
            for name, letter_ids in slices.items()
        },
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "claim_boundary": (
            "GPT-5.6 Luna ExECT leftover-form remote+rx stack remasure on frozen "
            "mention-unit v2 dev140 hybrid raws. Not holdout, not a Decision 0050 "
            "change, and not selected-stack parity."
        ),
    }
    (STUDY_DIR / "comparison.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT.write_text(_render_report(artifact), encoding="utf-8")
    print(json.dumps({"model_calls": 0, "decision": decision, "named_leftovers": named}, indent=2))


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


def _named_leftovers(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {row["letter_id"]: row for row in rows}
    return {
        "ea0010_dropped": _mention_with_cue(by_id["EA0010"], CANDIDATE, EA0010_CUE) is None,
        "ea0011_dropped": _mention_with_cue(by_id["EA0011"], CANDIDATE, EA0011_CUE) is None,
        "ea0158_kept": _mention_with_cue(by_id["EA0158"], CANDIDATE, EA0158_CUE) is not None,
        "v15_ea0010_dropped": _mention_with_cue(by_id["EA0010"], REMOTE, EA0010_CUE) is None,
        "v21_ea0010_kept": _mention_with_cue(by_id["EA0010"], RX, EA0010_CUE) is not None,
    }


def _decision(scored: dict[str, dict[str, Any]], named: dict[str, Any]) -> dict[str, Any]:
    all140 = scored["all140"]["methods"]
    rest = scored["rest120"]["methods"]
    parent = all140[PARENT]
    remote = all140[REMOTE]
    rx = all140[RX]
    candidate = all140[CANDIDATE]
    extras = candidate["empty_gold_sf_extras"]["mention_count"]
    rest_extras = rest[CANDIDATE]["empty_gold_sf_extras"]["mention_count"]
    sibling_extras = [
        remote["empty_gold_sf_extras"]["mention_count"],
        rx["empty_gold_sf_extras"]["mention_count"],
        rest[REMOTE]["empty_gold_sf_extras"]["mention_count"],
        rest[RX]["empty_gold_sf_extras"]["mention_count"],
    ]
    extras_rose = extras > V14_EMPTY_GOLD_SF or rest_extras > V14_REST120_EMPTY_GOLD_SF
    extras_rose_vs_sibling = extras > min(sibling_extras[:2]) or rest_extras > min(
        sibling_extras[2:]
    )
    remote_gain = (
        named["ea0010_dropped"]
        and named["ea0011_dropped"]
        and named["ea0158_kept"]
        and candidate["clinical_headline_family_f1"]["SeizureFrequency"]
        == remote["clinical_headline_family_f1"]["SeizureFrequency"]
    )
    rx_gain = (
        candidate["clinical_headline_family_f1"]["Prescription"]
        == rx["clinical_headline_family_f1"]["Prescription"]
    )
    headline = candidate["clinical_headline_f1"]
    parent_headline = parent["clinical_headline_f1"]
    better_sibling = max(remote["clinical_headline_f1"], rx["clinical_headline_f1"])
    if extras_rose or extras_rose_vs_sibling or not named["ea0158_kept"]:
        status = "revise"
        mechanism = "stack_damaged_keep_or_extras"
    elif not remote_gain or not rx_gain:
        status = "revise" if named["ea0010_dropped"] or rx_gain else "reject"
        mechanism = "sibling_gain_lost"
    elif headline > parent_headline and headline > better_sibling:
        status = "answer"
        mechanism = "both_sibling_gates_additive"
    elif headline > parent_headline:
        status = "negative_result"
        mechanism = "both_sibling_gates_no_headline_over_better_sibling"
    else:
        status = "negative_result"
        mechanism = "both_sibling_gates_headline_unchanged"
    return {
        "status": status,
        "mechanism": mechanism,
        "headline_140": headline,
        "parent_headline_140": parent_headline,
        "remote_headline_140": remote["clinical_headline_f1"],
        "rx_headline_140": rx["clinical_headline_f1"],
        "sf_140": candidate["clinical_headline_family_f1"]["SeizureFrequency"],
        "remote_sf_140": remote["clinical_headline_family_f1"]["SeizureFrequency"],
        "rx_140": candidate["clinical_headline_family_f1"]["Prescription"],
        "rx_sibling_140": rx["clinical_headline_family_f1"]["Prescription"],
        "empty_gold_sf_extras": extras,
        "rest120_empty_gold_sf_extras": rest_extras,
        "extras_rose": extras_rose,
        "extras_rose_vs_sibling": extras_rose_vs_sibling,
        "remote_gain": remote_gain,
        "rx_gain": rx_gain,
        "ea0010_dropped": named["ea0010_dropped"],
        "ea0011_dropped": named["ea0011_dropped"],
        "ea0158_kept": named["ea0158_kept"],
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
        "# ExECT leftover-form remote+rx stack, mention-unit v2 `dev140`\n\n"
        f"Date: 2026-08-17  \n"
        f"Status: complete; **{decision['status']}**  \n"
        f"Protocol: [remote+rx `dev140`]({Path(PROTOCOL).name})  \n"
        "Parent: [encoder composition]"
        "(mention_unit_leftover_form_encoder_refactor_2026-08-17.md)\n\n"
        "`model_calls`: 0. Draft rendered by the remasure script. "
        "Replace with the inspected report.\n"
    )


if __name__ == "__main__":
    main()
