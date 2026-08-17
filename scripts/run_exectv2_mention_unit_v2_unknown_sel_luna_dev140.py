"""No-call catalog of remaining unknown-state extras on febrile v14."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit import (
    HYBRID_METHOD,
    LLM_METHOD,
    MENTION_UNIT_PROMPT_VERSION,
    materialize_mention_unit,
    parse_mention_unit_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    frequency_state_faithful,
    frequency_state_keys,
)
from scripts.run_exectv2_mention_unit_v2_leftover_form_stack_error_analysis_luna_dev140 import (
    _AGE_RE,
    _DURATION_RE,
    _HISTORY_RE,
    _IMPLICIT_PERIOD_RE,
    _LAST_EVENT_RE,
    _NEGATION_RE,
    _QUALITATIVE_RE,
    _RISK_RE,
    _fold_span,
    _gold_letter_extra_class,
)
from scripts.run_exectv2_mention_unit_v2_luna import DEV20_IDS

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/exectv2/"
    "mention_unit_v2_unknown_sel_luna_dev140_protocol_2026-08-17.md"
)
REPORT = ROOT / (
    "docs/research/exectv2/mention_unit_v2_unknown_sel_luna_dev140_2026-08-17.md"
)
SOURCE_ROWS = ROOT / "experiments/exectv2_mention_unit_v2_luna_dev140_20260816" / "rows.jsonl"
V10_ERROR = (
    ROOT
    / "experiments/exectv2_mention_unit_v2_leftover_form_stack_luna_dev140_20260817"
    / "error_analysis.json"
)
STUDY_DIR = ROOT / "experiments/exectv2_mention_unit_v2_unknown_sel_luna_dev140_20260817"
CONTROL = "leftover_form_span_fold_febrile_v14"
DEV20 = frozenset(DEV20_IDS)
V14_EMPTY_GOLD_EXTRAS = 54
V14_REST120_EMPTY_GOLD_EXTRAS = 51

_QUITE_A_NUMBER_RE = re.compile(r"\bquite a number\b", re.I)
_WEEKEND_RE = re.compile(r"\bweekend\b", re.I)
_CALENDAR_DAY_RE = re.compile(
    r"\b(?:sunday|monday|tuesday|wednesday|thursday|friday|saturday|"
    r"january|february|march|april|may|june|july|august|september|"
    r"october|november|december)\b",
    re.I,
)
_IMPROVEMENT_RE = re.compile(
    r"\b(?:significant improvement|improved|better|well[- ]managed)\b", re.I
)
_FREQUENTLY_RE = re.compile(r"\bfrequently\b", re.I)
_CLUSTER_RE = re.compile(r"\bclusters?\b", re.I)


def _subclass(text: str, evidence: str, attributes: dict[str, str] | None) -> str:
    haystack = f"{text} {evidence}"
    if _QUITE_A_NUMBER_RE.search(haystack):
        return "quite_a_number"
    if _RISK_RE.search(haystack):
        return "risk_sentence"
    if _LAST_EVENT_RE.search(haystack) or (
        _DURATION_RE.search(haystack)
        and re.search(r"\b(?:last|haven.?t|ago)\b", haystack, re.I)
    ):
        return "last_event_or_zero"
    if _AGE_RE.search(haystack):
        return "age_onset"
    if _HISTORY_RE.search(haystack):
        return "remote_history"
    if _IMPLICIT_PERIOD_RE.search(haystack):
        return "implicit_period_unfilled"
    if _WEEKEND_RE.search(haystack) or _CLUSTER_RE.search(haystack):
        return "cluster_or_weekend"
    if _CALENDAR_DAY_RE.search(haystack):
        return "calendar_or_named_day"
    if _IMPROVEMENT_RE.search(haystack):
        return "qualitative_change"
    if _FREQUENTLY_RE.search(haystack) or _QUALITATIVE_RE.search(haystack):
        return "qualitative_or_vague"
    if _NEGATION_RE.search(haystack):
        return "negated_or_unused_type"
    if frequency_state_faithful(attributes or {}) == "unknown":
        return "unknown_no_rate_language"
    return "other"


def _item_key(item: dict[str, Any]) -> tuple[str, str, str]:
    return (
        item["letter_id"],
        _fold_span(str(item.get("clinical_name") or "")),
        _fold_span(str(item.get("evidence") or ""))[:80],
    )


def _mention_key(letter_id: str, mention: Any) -> tuple[Any, ...]:
    keys = frequency_state_keys(
        to_exect_letter(
            PredictedLetter(letter_id=letter_id, mentions=(mention,))
        ).entities("SeizureFrequency"),
        "clinical_headline",
    )
    return keys[0] if keys else ()


def _extras_for(
    rows: list[dict[str, Any]], letters: dict[str, Any]
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in rows:
        prediction = PredictedLetter.model_validate(row["hybrid"][CONTROL]["prediction"])
        letter = letters[row["letter_id"]]
        gold = letter.entities("SeizureFrequency")
        if not gold:
            continue
        gold_keys = Counter(frequency_state_keys(gold, "clinical_headline"))
        pred_mentions = [
            mention for mention in prediction.mentions if mention.entity == "SeizureFrequency"
        ]
        pred_letter = to_exect_letter(prediction)
        pred_keys = Counter(
            frequency_state_keys(pred_letter.entities("SeizureFrequency"), "clinical_headline")
        )
        extra_keys = pred_keys - gold_keys
        if not extra_keys:
            continue
        for mention in pred_mentions:
            key = _mention_key(letter.letter_id, mention)
            if not key or key not in extra_keys:
                continue
            attrs = mention.attributes or {}
            extra_class = _gold_letter_extra_class(mention.text, mention.evidence, attrs)
            items.append(
                {
                    "letter_id": row["letter_id"],
                    "clinical_name": mention.text,
                    "evidence": mention.evidence,
                    "state": frequency_state_faithful(attrs),
                    "count": attrs.get("NumberOfSeizures"),
                    "period": attrs.get("TimePeriod"),
                    "extra_class": extra_class,
                    "subclass": _subclass(mention.text, mention.evidence, attrs),
                    "slice": "dev20" if row["letter_id"] in DEV20 else "rest120",
                }
            )
    return items


def _gold_matching_unknown_named(
    rows: list[dict[str, Any]], letters: dict[str, Any]
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in rows:
        prediction = PredictedLetter.model_validate(row["hybrid"][CONTROL]["prediction"])
        letter = letters[row["letter_id"]]
        gold = letter.entities("SeizureFrequency")
        if not gold:
            continue
        gold_keys = Counter(frequency_state_keys(gold, "clinical_headline"))
        for mention in prediction.mentions:
            if mention.entity != "SeizureFrequency":
                continue
            attrs = mention.attributes or {}
            extra_class = _gold_letter_extra_class(mention.text, mention.evidence, attrs)
            if extra_class != "unknown_state_name":
                continue
            key = _mention_key(letter.letter_id, mention)
            if not key or key not in gold_keys:
                continue
            items.append(
                {
                    "letter_id": row["letter_id"],
                    "clinical_name": mention.text,
                    "evidence": mention.evidence,
                    "state": frequency_state_faithful(attrs),
                    "slice": "dev20" if row["letter_id"] in DEV20 else "rest120",
                }
            )
    return items


def main() -> None:
    if not SOURCE_ROWS.exists():
        raise SystemExit(f"missing saved raws: {SOURCE_ROWS}")
    letters = {letter.letter_id: letter for letter in load_letters_for_split("dev")}
    if len(letters) != 140:
        raise SystemExit(f"expected 140 development letters, found {len(letters)}")
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    rows: list[dict[str, Any]] = []
    with SOURCE_ROWS.open(encoding="utf-8") as handle:
        for line in handle:
            saved = json.loads(line)
            letter = letters[str(saved["letter_id"])]
            raw = str(saved["methods"][HYBRID_METHOD]["raw_output"])
            parsed = parse_mention_unit_json(raw, method=HYBRID_METHOD)
            if parsed.record is None:
                prediction = PredictedLetter(letter_id=letter.letter_id, mentions=())
                payload = {"prediction": prediction.model_dump(mode="json")}
            else:
                materialized = materialize_mention_unit(
                    letter,
                    parsed.record,
                    method=HYBRID_METHOD,
                    encoder=CONTROL,
                )
                payload = {"prediction": materialized.prediction.model_dump(mode="json")}
            rows.append(
                {
                    "letter_id": letter.letter_id,
                    "split": "dev140",
                    "model_calls": 0,
                    "prompt_version": MENTION_UNIT_PROMPT_VERSION,
                    "raw_output": raw,
                    "parse_errors": parsed.errors,
                    "hybrid": {CONTROL: payload},
                    "llm_prediction": saved["methods"][LLM_METHOD]["prediction"],
                }
            )
    v14 = _extras_for(rows, letters)
    v14_unknown = [item for item in v14 if item["extra_class"] == "unknown_state_name"]
    v10_unknown: list[dict[str, Any]] = []
    if V10_ERROR.exists():
        catalog = json.loads(V10_ERROR.read_text(encoding="utf-8"))
        v10_unknown = [
            item
            for item in catalog["leftover_buckets"]["gold_letter_sf_extras"]["items"]
            if item["extra_class"] == "unknown_state_name"
        ]
    v14_keys = {_item_key(item) for item in v14_unknown}
    filled = []
    for item in v10_unknown:
        if _item_key(item) in v14_keys:
            continue
        matches = [
            row
            for row in v14
            if row["letter_id"] == item["letter_id"]
            and _fold_span(row["clinical_name"]) == _fold_span(item["clinical_name"])
        ]
        filled.append(
            {
                "letter_id": item["letter_id"],
                "clinical_name": item["clinical_name"],
                "v10_evidence": item.get("evidence"),
                "v14_matches": [
                    {
                        "extra_class": row["extra_class"],
                        "state": row["state"],
                        "count": row["count"],
                        "period": row["period"],
                    }
                    for row in matches
                ],
            }
        )
    gold_matching = _gold_matching_unknown_named(rows, letters)
    new_unknown = [
        item
        for item in v14_unknown
        if _item_key(item) not in {_item_key(row) for row in v10_unknown}
    ]
    decision = _decision(v14_unknown, filled, gold_matching)
    artifact = {
        "schema_version": "exectv2.mention_unit_v2_unknown_sel.dev140.v1",
        "status": "complete",
        "protocol": PROTOCOL,
        "split": "dev140",
        "row_count": len(rows),
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "control": CONTROL,
        "candidate_identity_not_implemented": "leftover_form_span_fold_unknown_sel_v17",
        "v10_unknown_count": len(v10_unknown),
        "v14_unknown_count": len(v14_unknown),
        "v14_extra_class_counts": dict(Counter(item["extra_class"] for item in v14)),
        "v14_unknown_subclass_counts": dict(
            Counter(item["subclass"] for item in v14_unknown)
        ),
        "implicit_period_filled": filled,
        "new_unknown_after_v10": new_unknown,
        "remaining": v14_unknown,
        "gold_matching_unknown_named": gold_matching,
        "gold_matching_unknown_named_count": len(gold_matching),
        "empty_gold_sf_extras_control": {
            "all140": V14_EMPTY_GOLD_EXTRAS,
            "rest120": V14_REST120_EMPTY_GOLD_EXTRAS,
        },
        "decision": decision,
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "claim_boundary": (
            "GPT-5.6 Luna ExECT leftover-form unknown-state selection catalog "
            "on frozen mention-unit v2 dev140 hybrid raws. Not holdout, not a "
            "Decision 0050 change, and not selected-stack parity."
        ),
    }
    (STUDY_DIR / "catalog.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (STUDY_DIR / "rows.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    if not REPORT.exists():
        REPORT.write_text(_render_report(artifact), encoding="utf-8")
    print(json.dumps({"model_calls": 0, "decision": decision}, indent=2))


def _decision(
    remaining: list[dict[str, Any]],
    filled: list[dict[str, Any]],
    gold_matching: list[dict[str, Any]],
) -> dict[str, Any]:
    implementable = {"implicit_period_unfilled"}
    leftover_classes = {item["subclass"] for item in remaining}
    banned_or_qualitative = leftover_classes - implementable
    if gold_matching or banned_or_qualitative:
        status = "reject"
        mechanism = "remaining_unknown_is_last_event_qualitative_or_intended"
    else:
        status = "hold"
        mechanism = "unknown_sel_predicate_unjustified"
    return {
        "status": status,
        "mechanism": mechanism,
        "v14_unknown_count": len(remaining),
        "implicit_period_filled_count": len(filled),
        "gold_matching_unknown_named_count": len(gold_matching),
        "implemented_candidate": False,
        "empty_gold_sf_extras": V14_EMPTY_GOLD_EXTRAS,
        "rest120_empty_gold_sf_extras": V14_REST120_EMPTY_GOLD_EXTRAS,
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
        "# ExECT leftover-form unknown-state selection, mention-unit v2 `dev140`\n\n"
        f"Date: 2026-08-17  \n"
        f"Status: complete; **{decision['status']}**  \n"
        f"Protocol: [unknown-state selection `dev140`]({Path(PROTOCOL).name})  \n"
        "Parent: [error analysis `dev140`]"
        "(mention_unit_v2_leftover_form_stack_error_analysis_luna_dev140_2026-08-17.md)\n\n"
        "`model_calls`: 0. Draft rendered by the catalog script. "
        "Replace with the inspected report.\n"
    )


if __name__ == "__main__":
    main()
