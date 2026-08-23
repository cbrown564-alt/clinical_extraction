#!/usr/bin/env python3
"""Audit new ExECT same-fact encode rules on the saved Gemini dev140 ledger."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from collections.abc import Hashable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.exect import letters_for_split
from clinical_extraction.paper.exect_cell_replay import FAMILIES, _family_keys
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.format_stack import (  # noqa: E501
    DEFAULT_FORMAT_RULES,
    DIAGNOSIS_STANDARD_NAME_RULE,
    INVESTIGATION_LOCAL_RESULT_RULE,
    PRESCRIPTION_FORMULATION_NAME_RULE,
    PRESCRIPTION_LOCAL_SLOTS_RULE,
    PRESCRIPTION_STANDARD_NAME_RULE,
    SEIZURE_FREQUENCY_LOCAL_EVIDENCE_RULE,
    SEIZURE_FREQUENCY_STANDARD_NAME_RULE,
    apply_format_stack,
    assign_flatten_mention_ids,
    mention_row,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    clinical_headline_unit_keys,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

ROOT = discover_repo_root(start=Path(__file__))
OUT_DIR = ROOT / "experiments/exectv2_encode_rule_development_20260821"
SOURCE_ROWS = ROOT / "experiments/paper/exect_llm_encode/gemini37flash/dev140/rows.jsonl"
PROTOCOL = "docs/research/exectv2/exect_encode_rule_development_protocol_2026-08-21.md"
RULES = (
    DIAGNOSIS_STANDARD_NAME_RULE,
    INVESTIGATION_LOCAL_RESULT_RULE,
    PRESCRIPTION_FORMULATION_NAME_RULE,
    PRESCRIPTION_LOCAL_SLOTS_RULE,
    PRESCRIPTION_STANDARD_NAME_RULE,
    SEIZURE_FREQUENCY_LOCAL_EVIDENCE_RULE,
    SEIZURE_FREQUENCY_STANDARD_NAME_RULE,
)
_WHITESPACE = re.compile(r"\s+")


def _gold_rows(letter: ExectLetter) -> list[dict[str, Any]]:
    return [
        {
            "entity": annotation.entity,
            "text": annotation.text,
            "attributes": dict(annotation.attributes),
        }
        for annotation in letter.annotations
    ]


def _gold_keys(letter: ExectLetter) -> dict[str, Counter[Hashable]]:
    return {
        family: Counter(
            clinical_headline_unit_keys(
                family,
                [annotation for annotation in letter.annotations if annotation.entity == family],
                letter.note_text,
            )
        )
        for family in FAMILIES
    }


def _render(
    letter: ExectLetter,
    extract_mentions: Sequence[Mapping[str, Any]],
    enabled_rules: frozenset[str],
) -> list[dict[str, Any]]:
    mentions, _warnings = apply_format_stack(
        extract_mentions,
        letter.note_text,
        letter_id=letter.letter_id,
        enabled_rules=enabled_rules,
    )
    return assign_flatten_mention_ids([mention_row(mention) for mention in mentions])


def _key_rows(keys: Counter[Hashable]) -> list[dict[str, Any]]:
    return [
        {"key": repr(key), "count": count}
        for key, count in sorted(keys.items(), key=lambda item: repr(item[0]))
    ]


def _counts(gold: Counter[Hashable], prediction: Counter[Hashable]) -> dict[str, int | bool]:
    tp = sum((gold & prediction).values())
    fp = sum((prediction - gold).values())
    fn = sum((gold - prediction).values())
    return {"tp": tp, "fp": fp, "fn": fn, "exact": fp == 0 and fn == 0}


def _prf(counts: Mapping[str, int]) -> dict[str, float | int]:
    tp = int(counts.get("tp", 0))
    fp = int(counts.get("fp", 0))
    fn = int(counts.get("fn", 0))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def _exact_surface_score(
    letters: Mapping[str, ExectLetter],
    predictions: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, Any]:
    total: Counter[str] = Counter()
    family_scores: dict[str, dict[str, float | int]] = {}
    family_exact: Counter[str] = Counter()
    for family in FAMILIES:
        counts: Counter[str] = Counter()
        for letter_id, letter in letters.items():
            gold = _gold_keys(letter)[family]
            pred = _family_keys(letter, predictions[letter_id])[family]
            row_counts = _counts(gold, pred)
            counts.update(
                {
                    "tp": int(row_counts["tp"]),
                    "fp": int(row_counts["fp"]),
                    "fn": int(row_counts["fn"]),
                }
            )
            if row_counts["exact"]:
                family_exact[family] += 1
        family_scores[family] = _prf(counts)
        total.update(counts)
    return {
        "clinical_fact": _prf(total),
        "family": family_scores,
        "family_exact_letters": dict(family_exact),
        "scorer": "clinical_headline_unit_keys exact multiset per letter/family",
    }


def _evidence_status(evidence: str, note_text: str) -> str:
    if not evidence:
        return "missing"
    if evidence in note_text:
        return "exact"
    if _WHITESPACE.sub(" ", evidence).strip() in _WHITESPACE.sub(" ", note_text):
        return "whitespace_repaired"
    return "invalid"


def _git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main() -> None:
    letters = {letter.letter_id: letter for letter in letters_for_split("dev140")}
    rows = {str(row["letter_id"]): row for row in load_jsonl_rows(SOURCE_ROWS)}
    if set(rows) != set(letters) or len(rows) != 140:
        raise RuntimeError("saved encode rows do not match the 140 development letters")

    arms: dict[str, dict[str, list[dict[str, Any]]]] = {
        "rule_encode_baseline": {},
        "rule_encode_candidate": {},
        "gemini_encode_saved": {},
    }
    isolated: dict[str, dict[str, list[dict[str, Any]]]] = {rule: {} for rule in RULES}
    for letter_id, letter in letters.items():
        extract = list(rows[letter_id]["extract_mentions"])
        arms["rule_encode_baseline"][letter_id] = _render(letter, extract, frozenset())
        arms["rule_encode_candidate"][letter_id] = _render(
            letter, extract, DEFAULT_FORMAT_RULES
        )
        arms["gemini_encode_saved"][letter_id] = list(rows[letter_id]["encoded_mentions"])
        for rule in RULES:
            isolated[rule][letter_id] = _render(letter, extract, frozenset({rule}))

    exact_scores = {
        name: _exact_surface_score(letters, predictions) for name, predictions in arms.items()
    }
    isolated_scores = {
        rule: _exact_surface_score(letters, predictions) for rule, predictions in isolated.items()
    }

    mention_changes: list[dict[str, Any]] = []
    family_changes: list[dict[str, Any]] = []
    llm_family_changes: list[dict[str, Any]] = []
    residual_family_errors: list[dict[str, Any]] = []
    evidence_counts: Counter[str] = Counter()
    rule_change_counts: Counter[str] = Counter()
    changed_family_pairs: set[tuple[str, str]] = set()
    comparator_correct_regressions: list[dict[str, str]] = []
    family_exact_rescues: list[dict[str, str]] = []
    llm_exact_rescues: list[dict[str, str]] = []
    llm_correct_regressions: list[dict[str, str]] = []
    candidate_error_directions: Counter[str] = Counter()
    residual_error_units: Counter[str] = Counter()

    for letter_id, letter in letters.items():
        row = rows[letter_id]
        extract = list(row["extract_mentions"])
        baseline = arms["rule_encode_baseline"][letter_id]
        candidate = arms["rule_encode_candidate"][letter_id]
        gemini = arms["gemini_encode_saved"][letter_id]
        gold_keys = _gold_keys(letter)
        extract_keys = _family_keys(letter, extract)
        baseline_keys = _family_keys(letter, baseline)
        candidate_keys = _family_keys(letter, candidate)
        gemini_keys = _family_keys(letter, gemini)

        isolated_by_id = {
            rule: {str(mention.get("mention_id")): mention for mention in isolated[rule][letter_id]}
            for rule in RULES
        }
        baseline_by_id = {str(mention.get("mention_id")): mention for mention in baseline}
        candidate_by_id = {str(mention.get("mention_id")): mention for mention in candidate}
        extract_by_id = {str(mention.get("mention_id")): mention for mention in extract}

        for mention_id, before in baseline_by_id.items():
            after = candidate_by_id[mention_id]
            if before == after:
                continue
            fired = [rule for rule in RULES if isolated_by_id[rule][mention_id] != before]
            evidence = str(after.get("evidence") or "")
            status = _evidence_status(evidence, letter.note_text)
            evidence_counts[status] += 1
            for rule in fired:
                rule_change_counts[rule] += 1
            family = str(after.get("entity") or "")
            mention_changes.append(
                {
                    "schema_version": "exectv2.encode_rule_mention_change.dev140.v1",
                    "dataset": "ExECTv2",
                    "split": "dev140",
                    "row_policy": "development_review_permitted",
                    "letter_id": letter_id,
                    "family": family,
                    "mention_id": mention_id,
                    "rule_ids": fired,
                    "evidence": evidence,
                    "evidence_status": status,
                    "required_operands_present_in_extract_row": True,
                    "extract_mention": extract_by_id[mention_id],
                    "comparator_mention": before,
                    "candidate_mention": after,
                    "gold_family_keys": _key_rows(gold_keys[family]),
                    "extract_family_keys": _key_rows(extract_keys[family]),
                    "comparator_family_keys": _key_rows(baseline_keys[family]),
                    "candidate_family_keys": _key_rows(candidate_keys[family]),
                    "gemini_encode_family_keys": _key_rows(gemini_keys[family]),
                    "component_owner": "deterministic_adapter",
                    "model": "gemini/gemini-3.7-flash",
                    "prompt_version": "exect_llm_encode",
                    "replay_state": "saved_llm_output_and_no_call_rule_replay",
                }
            )

        for family in FAMILIES:
            gold = gold_keys[family]
            base = baseline_keys[family]
            cand = candidate_keys[family]
            llm = gemini_keys[family]
            if base != cand:
                changed_family_pairs.add((letter_id, family))
            base_counts = _counts(gold, base)
            cand_counts = _counts(gold, cand)
            llm_counts = _counts(gold, llm)

            if not cand_counts["exact"]:
                missing = gold - cand
                excess = cand - gold
                family_extract_mentions = [
                    mention for mention in extract if mention.get("entity") == family
                ]
                family_candidate_mentions = [
                    mention for mention in candidate if mention.get("entity") == family
                ]
                evidence_statuses = Counter(
                    _evidence_status(
                        str(mention.get("evidence") or ""), letter.note_text
                    )
                    for mention in family_candidate_mentions
                )
                residual_error_units[f"{family}:fp"] += sum(excess.values())
                residual_error_units[f"{family}:fn"] += sum(missing.values())
                if extract_keys[family] == gold:
                    residual_owner = "deterministic_adapter_remaining"
                elif llm_counts["exact"]:
                    residual_owner = "deterministic_adapter_remaining"
                else:
                    residual_owner = "extract_or_selection_unresolved"
                residual_family_errors.append(
                    {
                        "schema_version": (
                            "exectv2.encode_residual_family_error.dev140.v1"
                        ),
                        "dataset": "ExECTv2",
                        "split": "dev140",
                        "row_policy": "development_review_permitted",
                        "letter_id": letter_id,
                        "family": family,
                        "gold_keys": _key_rows(gold),
                        "extract_keys": _key_rows(extract_keys[family]),
                        "comparator_keys": _key_rows(base),
                        "candidate_keys": _key_rows(cand),
                        "gemini_encode_keys": _key_rows(llm),
                        "missing_keys": _key_rows(missing),
                        "excess_keys": _key_rows(excess),
                        "candidate_counts": cand_counts,
                        "extract_mentions": family_extract_mentions,
                        "candidate_mentions": family_candidate_mentions,
                        "gemini_encode_mentions": [
                            mention
                            for mention in gemini
                            if mention.get("entity") == family
                        ],
                        "candidate_evidence_status": dict(evidence_statuses),
                        "initial_first_failure_owner": residual_owner,
                        "manual_classification": "unresolved",
                    }
                )
            wrong_to_correct = bool(not base_counts["exact"] and cand_counts["exact"])
            correct_to_wrong = bool(base_counts["exact"] and not cand_counts["exact"])
            if wrong_to_correct:
                family_exact_rescues.append({"letter_id": letter_id, "family": family})
            if correct_to_wrong:
                comparator_correct_regressions.append({"letter_id": letter_id, "family": family})
            if cand_counts["exact"]:
                first_failure_owner = "none"
            elif base_counts["exact"] and not cand_counts["exact"]:
                first_failure_owner = "deterministic_adapter"
            elif llm_counts["exact"] and not cand_counts["exact"]:
                first_failure_owner = "deterministic_adapter_remaining"
            elif extract_keys[family] == gold:
                first_failure_owner = "deterministic_adapter_remaining"
            else:
                first_failure_owner = "extract_or_selection_unresolved"
            if base != cand:
                base_error = int(base_counts["fp"]) + int(base_counts["fn"])
                candidate_error = int(cand_counts["fp"]) + int(cand_counts["fn"])
                candidate_error_delta = candidate_error - base_error
                direction = (
                    "better"
                    if candidate_error_delta < 0
                    else "worse"
                    if candidate_error_delta > 0
                    else "same"
                )
                candidate_error_directions[f"{family}:{direction}"] += 1
                family_changes.append(
                    {
                        "schema_version": "exectv2.encode_rule_family_change.dev140.v1",
                        "dataset": "ExECTv2",
                        "split": "dev140",
                        "letter_id": letter_id,
                        "family": family,
                        "gold_keys": _key_rows(gold),
                        "extract_keys": _key_rows(extract_keys[family]),
                        "comparator_keys": _key_rows(base),
                        "candidate_keys": _key_rows(cand),
                        "gemini_encode_keys": _key_rows(llm),
                        "comparator_counts": base_counts,
                        "candidate_counts": cand_counts,
                        "gemini_encode_counts": llm_counts,
                        "tp_delta": int(cand_counts["tp"]) - int(base_counts["tp"]),
                        "fp_delta": int(cand_counts["fp"]) - int(base_counts["fp"]),
                        "fn_delta": int(cand_counts["fn"]) - int(base_counts["fn"]),
                        "error_delta": candidate_error_delta,
                        "wrong_to_correct": wrong_to_correct,
                        "correct_to_wrong": correct_to_wrong,
                        "first_failure_owner": first_failure_owner,
                    }
                )

            if base != llm:
                llm_wrong_to_correct = bool(not base_counts["exact"] and llm_counts["exact"])
                llm_correct_to_wrong = bool(base_counts["exact"] and not llm_counts["exact"])
                if llm_wrong_to_correct:
                    llm_exact_rescues.append({"letter_id": letter_id, "family": family})
                if llm_correct_to_wrong:
                    llm_correct_regressions.append({"letter_id": letter_id, "family": family})
                base_error = int(base_counts["fp"]) + int(base_counts["fn"])
                llm_error = int(llm_counts["fp"]) + int(llm_counts["fn"])
                llm_family_changes.append(
                    {
                        "schema_version": "exectv2.llm_encode_family_change.dev140.v1",
                        "dataset": "ExECTv2",
                        "split": "dev140",
                        "letter_id": letter_id,
                        "family": family,
                        "gold_keys": _key_rows(gold),
                        "comparator_keys": _key_rows(base),
                        "gemini_encode_keys": _key_rows(llm),
                        "candidate_keys": _key_rows(cand),
                        "comparator_counts": base_counts,
                        "gemini_encode_counts": llm_counts,
                        "candidate_counts": cand_counts,
                        "tp_delta": int(llm_counts["tp"]) - int(base_counts["tp"]),
                        "fp_delta": int(llm_counts["fp"]) - int(base_counts["fp"]),
                        "fn_delta": int(llm_counts["fn"]) - int(base_counts["fn"]),
                        "error_delta": llm_error - base_error,
                        "wrong_to_correct": llm_wrong_to_correct,
                        "correct_to_wrong": llm_correct_to_wrong,
                        "candidate_matches_or_betters_llm_error": (
                            int(cand_counts["fp"]) + int(cand_counts["fn"]) <= llm_error
                        ),
                    }
                )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl_rows(mention_changes, OUT_DIR / "mention_changes.jsonl")
    write_jsonl_rows(family_changes, OUT_DIR / "family_changes.jsonl")
    write_jsonl_rows(llm_family_changes, OUT_DIR / "llm_family_changes.jsonl")
    write_jsonl_rows(
        residual_family_errors, OUT_DIR / "residual_family_errors.jsonl"
    )

    generated = datetime.now(UTC).isoformat()
    summary = {
        "schema_version": "exectv2.encode_rule_development.dev140.v1",
        "generated_utc": generated,
        "protocol": PROTOCOL,
        "dataset": "ExECTv2",
        "split": "dev140",
        "row_count": len(letters),
        "row_policy": "development_review_permitted",
        "holdout_policy": "test60_not_loaded_or_inspected",
        "source_extract": SOURCE_ROWS.relative_to(ROOT).as_posix(),
        "source_llm_encode": SOURCE_ROWS.relative_to(ROOT).as_posix(),
        "scorer": "clinical_headline_unit_keys exact multiset per letter/family",
        "model": "gemini/gemini-3.7-flash",
        "prompt_version": "exect_llm_encode",
        "program_schema": "paper.exect_llm_encode.v1",
        "model_calls": 0,
        "replay_state": "saved_llm_output_and_no_call_rule_replay",
        "repair_policy": "same_fact_encode_only; no add/drop/split/merge/reselect",
        "git_head": _git_output("rev-parse", "HEAD"),
        "dirty_tree": bool(_git_output("status", "--short")),
        "exact_surface_scores": exact_scores,
        "isolated_rule_scores": isolated_scores,
        "cumulative_rule_ids": sorted(DEFAULT_FORMAT_RULES),
        "changed_mentions": len(mention_changes),
        "changed_letter_family_pairs": len(changed_family_pairs),
        "evidence_status": dict(evidence_counts),
        "rule_changed_mentions": dict(rule_change_counts),
        "family_exact_rescue_count": len(family_exact_rescues),
        "family_exact_rescues": family_exact_rescues,
        "deterministic_correct_regression_count": len(comparator_correct_regressions),
        "deterministic_correct_regressions": comparator_correct_regressions,
        "changed_family_error_directions": dict(candidate_error_directions),
        "residual_nonexact_letter_family_pairs": len(residual_family_errors),
        "residual_error_units": dict(residual_error_units),
        "llm_changed_letter_family_pairs": len(llm_family_changes),
        "llm_family_exact_rescue_count": len(llm_exact_rescues),
        "llm_family_exact_rescues": llm_exact_rescues,
        "llm_deterministic_correct_regression_count": len(llm_correct_regressions),
        "llm_deterministic_correct_regressions": llm_correct_regressions,
        "claim_boundary": (
            "Development answer on the frozen Gemini exect_llm_only dev140 "
            "mention distribution. Not holdout evidence or clinical validation."
        ),
        "artifacts": {
            "mention_changes": "mention_changes.jsonl",
            "family_changes": "family_changes.jsonl",
            "llm_family_changes": "llm_family_changes.jsonl",
            "residual_family_errors": "residual_family_errors.jsonl",
        },
    }
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
