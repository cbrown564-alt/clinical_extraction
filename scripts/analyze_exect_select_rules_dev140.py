#!/usr/bin/env python3
"""Audit deterministic ExECT Select rules on the frozen Gemini dev140 ledger."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from collections.abc import Hashable, Mapping, Sequence
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.exect import letters_for_split
from clinical_extraction.paper.exect_cell_replay import FAMILIES, _family_keys
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.select_rules import (
    ACCEPTED_SELECT_RULE_IDS,
    CANDIDATE_SELECT_RULE_IDS,
    DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE,
    DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY,
    PRESCRIPTION_ACTIVE_TITRATION,
    PRESCRIPTION_EXACT_REGIMEN_DEDUPE,
    PRESCRIPTION_LOCAL_REGIMEN_SCOPE,
    SF_NAMED_TYPE_IDENTITY,
    SF_RECENT_EVENT_OVER_HISTORICAL_FREE,
    SF_TO_DIAGNOSIS_EXPLICIT_TYPE,
    apply_select_rules,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.format_stack import (  # noqa: E501
    DEFAULT_FORMAT_RULES,
    apply_format_stack,
    as_predicted_mentions,
    mention_row,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
    StructuredMethodConfig,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.letter_assembly import (  # noqa: E501
    assemble_structured_rows,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    clinical_headline_unit_keys,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

ROOT = discover_repo_root(start=Path(__file__))
OUT_DIR = ROOT / "experiments/exectv2_select_rule_development_20260822"
SOURCE_ROWS = ROOT / "experiments/paper/exect_llm_select/gemini37flash/dev140/rows.jsonl"
PROTOCOL = "docs/research/exectv2/exect_select_rule_development_protocol_2026-08-22.md"
STUDY_CONTEXT: dict[str, Any] = {
    "dataset": "ExECTv2",
    "split": "dev140",
    "row_policy": "development_review_permitted",
    "scorer": "clinical_headline_unit_keys exact multiset per letter/family",
    "model": "gemini/gemini-3.7-flash",
    "programs": ["exect_llm_encode", "exect_llm_select"],
    "replay_state": "saved_llm_output_and_no_call_rule_replay",
    "repair_policy": (
        "ledger-only Select add/drop/rewrite; no unused-note scan or gold-conditioned operand"
    ),
    "call_state": "no_call",
    "fallback_state": "none",
}

# Predeclared candidates are all measured. Promotion is narrower: only rules
# with a positive exact-score contribution and no comparator-exact regression
# on the frozen primary development ledger enter the accepted arm.
REJECTED_SELECT_RULE_IDS: tuple[str, ...] = (SF_RECENT_EVENT_OVER_HISTORICAL_FREE,)
RULE_DECISIONS: dict[str, dict[str, str]] = {
    DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY: {
        "decision": "accept",
        "reason": "repairs three overbroad rewrites without a changed-family regression",
    },
    PRESCRIPTION_LOCAL_REGIMEN_SCOPE: {
        "decision": "accept",
        "reason": "keeps rescue cadence local to the named rescue medicine",
    },
    PRESCRIPTION_ACTIVE_TITRATION: {
        "decision": "accept",
        "reason": "retains the explicit current regimen before a future titration",
    },
    PRESCRIPTION_EXACT_REGIMEN_DEDUPE: {
        "decision": "accept",
        "reason": "drops one exact duplicate and never merges unequal doses",
    },
    SF_NAMED_TYPE_IDENTITY: {
        "decision": "accept",
        "reason": "blocks sibling seizure-type reassignment but permits named refinements",
    },
    SF_TO_DIAGNOSIS_EXPLICIT_TYPE: {
        "decision": "accept",
        "reason": "projects selected named SF facts into Diagnosis without note scanning",
    },
    DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE: {
        "decision": "accept",
        "reason": "restores an explicit heading phenotype outside JME syndrome rows",
    },
    SF_RECENT_EVENT_OVER_HISTORICAL_FREE: {
        "decision": "reject",
        "reason": "clinically plausible change was neutral under the exact scorer",
    },
}


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
    tp, fp, fn = (int(counts.get(key, 0)) for key in ("tp", "fp", "fn"))
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


def _score(
    letters: Mapping[str, ExectLetter],
    predictions: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, Any]:
    total: Counter[str] = Counter()
    family_scores: dict[str, dict[str, float | int]] = {}
    exact_letters: Counter[str] = Counter()
    for family in FAMILIES:
        counts: Counter[str] = Counter()
        for letter_id, letter in letters.items():
            gold = _gold_keys(letter)[family]
            pred = _family_keys(letter, predictions[letter_id])[family]
            row = _counts(gold, pred)
            counts.update(tp=int(row["tp"]), fp=int(row["fp"]), fn=int(row["fn"]))
            if row["exact"]:
                exact_letters[family] += 1
        family_scores[family] = _prf(counts)
        total.update(counts)
    return {
        "clinical_fact": _prf(total),
        "family": family_scores,
        "family_exact_letters": dict(exact_letters),
        "scorer": "clinical_headline_unit_keys exact multiset per letter/family",
    }


def _gate_mentions(
    letter: ExectLetter, mentions: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    gated, _warnings = structured.to_predicted_letter(
        letter.letter_id,
        as_predicted_mentions(mentions),
        note_text=letter.note_text,
    )
    return [mention_row(mention) for mention in gated.mentions]


def _rule_encode(
    letter: ExectLetter, extract_mentions: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    formatted, _warnings = apply_format_stack(
        extract_mentions,
        letter.note_text,
        letter_id=letter.letter_id,
        enabled_rules=DEFAULT_FORMAT_RULES,
    )
    gated, _gate_warnings = structured.to_predicted_letter(
        letter.letter_id,
        formatted,
        note_text=letter.note_text,
    )
    return [mention_row(mention) for mention in gated.mentions]


def _current_select(
    letter: ExectLetter, source_mentions: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    row = {
        "letter_id": letter.letter_id,
        "split": "dev",
        "model": "gemini/gemini-3.7-flash",
        "mode": "saved-output no-call replay",
        "pipeline_family": "exectv2_rule_encode",
        "prompt_version": "exect_llm_encode_plus_accepted_format_rules",
        "predicted_mentions": list(source_mentions),
        "raw_output": "",
        "gold_mentions": [],
    }
    assembled = assemble_structured_rows(
        [letter],
        [row],
        config=StructuredMethodConfig(
            archived_replay=True,
            select_rule_ids=frozenset(),
        ),
    )[letter.letter_id]
    return list(assembled["predicted_mentions"])


def _apply_arm(
    letters: Mapping[str, ExectLetter],
    comparator: Mapping[str, Sequence[Mapping[str, Any]]],
    source: Mapping[str, Sequence[Mapping[str, Any]]],
    enabled: frozenset[str],
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    predictions: dict[str, list[dict[str, Any]]] = {}
    action_rows: list[dict[str, Any]] = []
    for letter_id, letter in letters.items():
        predictions[letter_id], actions = apply_select_rules(
            comparator[letter_id],
            source_mentions=source[letter_id],
            note_text=letter.note_text,
            enabled_rule_ids=enabled,
        )
        for action in actions:
            action_rows.append(
                {
                    "schema_version": "exectv2.select_rule_action.dev140.v1",
                    **STUDY_CONTEXT,
                    "letter_id": letter_id,
                    "evidence_status": (
                        "exact"
                        if str(action.get("evidence") or "") in letter.note_text
                        else "missing_or_invalid"
                    ),
                    **action,
                }
            )
    return predictions, action_rows


def _family_changes(
    *,
    arm_name: str,
    letters: Mapping[str, ExectLetter],
    comparator: Mapping[str, Sequence[Mapping[str, Any]]],
    candidate: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for letter_id, letter in letters.items():
        gold = _gold_keys(letter)
        before = _family_keys(letter, comparator[letter_id])
        after = _family_keys(letter, candidate[letter_id])
        for family in FAMILIES:
            if before[family] == after[family]:
                continue
            before_counts = _counts(gold[family], before[family])
            after_counts = _counts(gold[family], after[family])
            before_error = int(before_counts["fp"]) + int(before_counts["fn"])
            after_error = int(after_counts["fp"]) + int(after_counts["fn"])
            changes.append(
                {
                    "schema_version": "exectv2.select_rule_family_change.dev140.v1",
                    **STUDY_CONTEXT,
                    "arm": arm_name,
                    "letter_id": letter_id,
                    "family": family,
                    "rule_ids": (
                        [arm_name] if arm_name in CANDIDATE_SELECT_RULE_IDS else []
                    ),
                    "first_changing_component": "deterministic_select_rule_stack",
                    "required_operand_status": "emitted_ledger_only",
                    "direction": (
                        "better"
                        if after_error < before_error
                        else "worse"
                        if after_error > before_error
                        else "same"
                    ),
                    "error_delta": after_error - before_error,
                    "wrong_to_correct": bool(not before_counts["exact"] and after_counts["exact"]),
                    "correct_to_wrong": bool(before_counts["exact"] and not after_counts["exact"]),
                    "gold_keys": _key_rows(gold[family]),
                    "comparator_keys": _key_rows(before[family]),
                    "candidate_keys": _key_rows(after[family]),
                    "comparator_counts": before_counts,
                    "candidate_counts": after_counts,
                    "source_mentions": [
                        mention
                        for mention in comparator[letter_id]
                        if mention.get("entity") == family
                    ],
                    "candidate_mentions": [
                        mention
                        for mention in candidate[letter_id]
                        if mention.get("entity") == family
                    ],
                    "evidence_status": (
                        "exact"
                        if all(
                            str(mention.get("evidence") or "") in letter.note_text
                            for mention in candidate[letter_id]
                            if mention.get("entity") == family
                        )
                        else "missing_or_invalid"
                    ),
                }
            )
    return changes


def _change_summary(changes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    directions = Counter(str(row["direction"]) for row in changes)
    rescues = [
        {"letter_id": row["letter_id"], "family": row["family"]}
        for row in changes
        if row.get("wrong_to_correct")
    ]
    regressions = [
        {"letter_id": row["letter_id"], "family": row["family"]}
        for row in changes
        if row.get("correct_to_wrong")
    ]
    return {
        "changed_letter_family_pairs": len(changes),
        "directions": dict(directions),
        "family_exact_rescues": rescues,
        "comparator_exact_regressions": regressions,
    }


def _residual_rows(
    letters: Mapping[str, ExectLetter],
    predictions: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    rule_encode: Mapping[str, Sequence[Mapping[str, Any]]],
    current_select: Mapping[str, Sequence[Mapping[str, Any]]],
    saved_gemini_select: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    residuals: list[dict[str, Any]] = []
    for letter_id, letter in letters.items():
        gold = _gold_keys(letter)
        candidate = _family_keys(letter, predictions[letter_id])
        encoded = _family_keys(letter, rule_encode[letter_id])
        current = _family_keys(letter, current_select[letter_id])
        gemini = _family_keys(letter, saved_gemini_select[letter_id])
        for family in FAMILIES:
            counts = _counts(gold[family], candidate[family])
            if counts["exact"]:
                continue
            missing = gold[family] - candidate[family]
            excess = candidate[family] - gold[family]
            missing_owners = _missing_unit_owners(
                missing,
                encoded=encoded[family],
                candidate=candidate[family],
            )
            excess_owners = _excess_unit_owners(
                excess,
                encoded=encoded[family],
                candidate=candidate[family],
            )
            owner_set = {str(row["owner"]) for row in (*missing_owners, *excess_owners)}
            first_failure_owner = (
                "upstream_extract_or_encode"
                if owner_set and all(owner.startswith("upstream_") for owner in owner_set)
                else "deterministic_select"
                if owner_set
                and all(owner.startswith("deterministic_select_") for owner in owner_set)
                else "mixed_upstream_and_select"
            )
            residuals.append(
                {
                    "schema_version": "exectv2.select_residual_family_error.dev140.v1",
                    **STUDY_CONTEXT,
                    "letter_id": letter_id,
                    "family": family,
                    "accepted_rule_ids": list(ACCEPTED_SELECT_RULE_IDS),
                    "gold_keys": _key_rows(gold[family]),
                    "candidate_keys": _key_rows(candidate[family]),
                    "rule_encode_keys": _key_rows(encoded[family]),
                    "current_select_keys": _key_rows(current[family]),
                    "saved_gemini_select_keys": _key_rows(gemini[family]),
                    "missing_keys": _key_rows(missing),
                    "excess_keys": _key_rows(excess),
                    "missing_unit_owners": missing_owners,
                    "excess_unit_owners": excess_owners,
                    "first_failure_owner": first_failure_owner,
                    "candidate_counts": counts,
                    "candidate_mentions": [
                        mention
                        for mention in predictions[letter_id]
                        if mention.get("entity") == family
                    ],
                    "evidence_status": (
                        "exact"
                        if all(
                            str(mention.get("evidence") or "") in letter.note_text
                            for mention in predictions[letter_id]
                            if mention.get("entity") == family
                        )
                        else "missing_or_invalid"
                    ),
                    "classification": ("exact_key_provenance_against_frozen_rule_encode_surface"),
                }
            )
    return residuals


def _missing_unit_owners(
    missing: Counter[Hashable],
    *,
    encoded: Counter[Hashable],
    candidate: Counter[Hashable],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, count in missing.items():
        select_owned = min(count, max(0, encoded[key] - candidate[key]))
        if select_owned:
            rows.append(
                {
                    "key": repr(key),
                    "count": select_owned,
                    "owner": "deterministic_select_removed_or_rewrote",
                }
            )
        if count > select_owned:
            rows.append(
                {
                    "key": repr(key),
                    "count": count - select_owned,
                    "owner": "upstream_absent_at_encode",
                }
            )
    return rows


def _excess_unit_owners(
    excess: Counter[Hashable],
    *,
    encoded: Counter[Hashable],
    candidate: Counter[Hashable],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, count in excess.items():
        select_owned = min(count, max(0, candidate[key] - encoded[key]))
        if select_owned:
            rows.append(
                {
                    "key": repr(key),
                    "count": select_owned,
                    "owner": "deterministic_select_added_or_rewrote",
                }
            )
        if count > select_owned:
            rows.append(
                {
                    "key": repr(key),
                    "count": count - select_owned,
                    "owner": "upstream_excess_preserved",
                }
            )
    return rows


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
    saved = {str(row["letter_id"]): row for row in load_jsonl_rows(SOURCE_ROWS)}
    if set(saved) != set(letters) or len(saved) != 140:
        raise RuntimeError("saved Gemini Select rows do not match the 140 development letters")

    rule_encode: dict[str, list[dict[str, Any]]] = {}
    current_select: dict[str, list[dict[str, Any]]] = {}
    saved_gemini_encode: dict[str, list[dict[str, Any]]] = {}
    saved_gemini_select: dict[str, list[dict[str, Any]]] = {}
    current_select_on_gemini: dict[str, list[dict[str, Any]]] = {}
    gemini_sources: dict[str, list[dict[str, Any]]] = {}
    for letter_id, letter in letters.items():
        row = saved[letter_id]
        rule_encode[letter_id] = _rule_encode(letter, row["extract_mentions"])
        current_select[letter_id] = _current_select(letter, rule_encode[letter_id])
        saved_gemini_encode[letter_id] = list(row["encoded_mentions"])
        saved_gemini_select[letter_id] = list(row["selected_mentions"])
        gemini_sources[letter_id] = _gate_mentions(letter, row["encoded_mentions"])
        current_select_on_gemini[letter_id] = _current_select(letter, gemini_sources[letter_id])

    isolated_predictions: dict[str, dict[str, list[dict[str, Any]]]] = {}
    all_actions: list[dict[str, Any]] = []
    all_family_changes: list[dict[str, Any]] = []
    arm_summaries: dict[str, Any] = {}
    for rule_id in CANDIDATE_SELECT_RULE_IDS:
        arm, actions = _apply_arm(
            letters,
            current_select,
            rule_encode,
            frozenset({rule_id}),
        )
        isolated_predictions[rule_id] = arm
        changes = _family_changes(
            arm_name=rule_id,
            letters=letters,
            comparator=current_select,
            candidate=arm,
        )
        all_actions.extend(actions)
        all_family_changes.extend(changes)
        arm_summaries[rule_id] = {
            **RULE_DECISIONS[rule_id],
            "score": _score(letters, arm),
            "action_count": len(actions),
            **_change_summary(changes),
        }

    accepted, accepted_actions = _apply_arm(
        letters,
        current_select,
        rule_encode,
        frozenset(ACCEPTED_SELECT_RULE_IDS),
    )
    accepted_changes = _family_changes(
        arm_name="accepted_combined",
        letters=letters,
        comparator=current_select,
        candidate=accepted,
    )
    accepted_rules_by_pair: dict[tuple[str, str], set[str]] = {}
    for action in accepted_actions:
        pair = (str(action["letter_id"]), str(action["entity"]))
        accepted_rules_by_pair.setdefault(pair, set()).add(str(action["rule_id"]))
    accepted_changes = [
        {
            **row,
            "rule_ids": sorted(
                accepted_rules_by_pair.get((str(row["letter_id"]), str(row["family"])), set())
            ),
        }
        for row in accepted_changes
    ]
    all_actions.extend([{**row, "arm": "accepted_combined"} for row in accepted_actions])
    all_family_changes.extend(accepted_changes)

    candidate_on_gemini, _candidate_gemini_actions = _apply_arm(
        letters,
        current_select_on_gemini,
        gemini_sources,
        frozenset(ACCEPTED_SELECT_RULE_IDS),
    )

    cumulative: dict[str, Any] = {}
    enabled: set[str] = set()
    for rule_id in ACCEPTED_SELECT_RULE_IDS:
        enabled.add(rule_id)
        arm, _actions = _apply_arm(
            letters,
            current_select,
            rule_encode,
            frozenset(enabled),
        )
        cumulative[rule_id] = {
            "enabled_rule_ids": sorted(enabled),
            "score": _score(letters, arm),
        }

    leave_one_out: dict[str, Any] = {}
    for rule_id in ACCEPTED_SELECT_RULE_IDS:
        enabled = frozenset(set(ACCEPTED_SELECT_RULE_IDS) - {rule_id})
        arm, _actions = _apply_arm(letters, current_select, rule_encode, enabled)
        changes = _family_changes(
            arm_name=f"leave_one_out:{rule_id}",
            letters=letters,
            comparator=accepted,
            candidate=arm,
        )
        leave_one_out[rule_id] = {
            "enabled_rule_ids": sorted(enabled),
            "score": _score(letters, arm),
            **_change_summary(changes),
        }

    accepted_summary = {
        "score": _score(letters, accepted),
        "action_count": len(accepted_actions),
        **_change_summary(accepted_changes),
    }
    residuals = _residual_rows(
        letters,
        accepted,
        rule_encode=rule_encode,
        current_select=current_select,
        saved_gemini_select=saved_gemini_select,
    )
    evidence_status = Counter(str(row["evidence_status"]) for row in accepted_actions)
    action_counts = Counter(str(row["rule_id"]) for row in accepted_actions)
    residual_owner_counts = Counter(str(row["first_failure_owner"]) for row in residuals)
    residual_unit_owner_counts = Counter(
        str(unit["owner"])
        for row in residuals
        for unit in (*row["missing_unit_owners"], *row["excess_unit_owners"])
        for _ in range(int(unit["count"]))
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl_rows(all_actions, OUT_DIR / "rule_actions.jsonl")
    write_jsonl_rows(all_family_changes, OUT_DIR / "family_changes.jsonl")
    write_jsonl_rows(residuals, OUT_DIR / "residual_family_errors.jsonl")
    write_jsonl_rows(
        [
            {
                "schema_version": "exectv2.select_rule_ablation.dev140.v1",
                "rule_id": rule_id,
                **summary,
            }
            for rule_id, summary in arm_summaries.items()
        ],
        OUT_DIR / "rule_ablations.jsonl",
    )

    summary = {
        "schema_version": "exectv2.select_rule_development.dev140.v1",
        "generated_utc": datetime.now(UTC).isoformat(),
        "protocol": PROTOCOL,
        "dataset": "ExECTv2",
        "split": "dev140",
        "row_count": len(letters),
        "row_policy": "development_review_permitted",
        "holdout_policy": "test60_not_loaded_or_inspected",
        "source_extract": SOURCE_ROWS.relative_to(ROOT).as_posix(),
        "source_llm_encode": SOURCE_ROWS.relative_to(ROOT).as_posix(),
        "source_llm_select": SOURCE_ROWS.relative_to(ROOT).as_posix(),
        "source_input_counts": {
            "rows": len(saved),
            "extract_mentions": sum(
                len(row.get("extract_mentions", [])) for row in saved.values()
            ),
            "encoded_mentions": sum(
                len(row.get("encoded_mentions", [])) for row in saved.values()
            ),
            "selected_mentions": sum(
                len(row.get("selected_mentions", [])) for row in saved.values()
            ),
        },
        "dependency_versions": {
            "python": sys.version.split()[0],
            "pydantic": version("pydantic"),
        },
        "model": "gemini/gemini-3.7-flash",
        "prompt_versions": ["exect_llm_encode", "exect_llm_select"],
        "model_calls": 0,
        "replay_state": "saved_llm_output_and_no_call_rule_replay",
        "repair_policy": (
            "Select may add, drop, or rewrite only emitted ledger facts; "
            "no unused-note scan and no gold-conditioned rule operand"
        ),
        "scorer": "clinical_headline_unit_keys exact multiset per letter/family",
        "git_head": _git_output("rev-parse", "HEAD"),
        "dirty_tree": bool(_git_output("status", "--short")),
        "candidate_rule_ids": list(CANDIDATE_SELECT_RULE_IDS),
        "accepted_rule_ids": list(ACCEPTED_SELECT_RULE_IDS),
        "rejected_rule_ids": list(REJECTED_SELECT_RULE_IDS),
        "score_ladder": {
            "deterministic_rule_encode": _score(letters, rule_encode),
            "deterministic_current_select": _score(letters, current_select),
            "deterministic_candidate_select": _score(letters, accepted),
            "saved_gemini_encode": _score(letters, saved_gemini_encode),
            "saved_gemini_select": _score(letters, saved_gemini_select),
            "current_select_on_saved_gemini_encode": _score(letters, current_select_on_gemini),
            "candidate_select_on_saved_gemini_encode": _score(letters, candidate_on_gemini),
        },
        "isolated_rule_ablations": arm_summaries,
        "cumulative_accepted_rules": cumulative,
        "leave_one_out_accepted_rules": leave_one_out,
        "accepted_combined": accepted_summary,
        "accepted_action_counts": dict(action_counts),
        "accepted_evidence_status": dict(evidence_status),
        "residual_nonexact_letter_family_pairs": len(residuals),
        "residual_first_failure_owner_counts": dict(residual_owner_counts),
        "residual_unit_owner_counts": dict(residual_unit_owner_counts),
        "claim_boundary": (
            "Development answer on frozen Gemini dev140 saved outputs. "
            "Not holdout evidence or clinical validation."
        ),
        "artifacts": {
            "rule_actions": "rule_actions.jsonl",
            "family_changes": "family_changes.jsonl",
            "rule_ablations": "rule_ablations.jsonl",
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
