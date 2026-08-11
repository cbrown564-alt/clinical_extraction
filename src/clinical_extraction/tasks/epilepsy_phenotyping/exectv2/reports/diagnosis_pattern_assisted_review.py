"""Apply conservative, observable patterns to a Diagnosis review overlay."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.artifact_io import (
    sha256_file,
)

OVERLAY_SCHEMA = "exectv2_diagnosis_review_overlay_v1"
SUMMARY_SCHEMA = "exectv2_diagnosis_pattern_assisted_review_v1"

_NON_TARGET_CONCEPTS = frozenset(
    {
        "anxiety",
        "avm",
        "depression",
        "diabetes",
        "episodic migraine",
        "excess alcohol consumption",
        "hydrocephalus",
        "hypertension",
        "ischaemic heart disease",
        "mild head injury",
        "myoclonic jerks",
        "myoclonus",
        "nonepileptic events",
        "seizures",
        "stroke",
        "syncope",
        "tuberous sclerosis",
        "unwitnessed blackouts",
    }
)

_REVIEW_EQUIVALENCE_FAMILIES: tuple[frozenset[str], ...] = (
    frozenset(
        {
            "epilepsy",
            "epileptic attack",
            "intractable epilepsy",
            "drug resistant epilepsy",
            "drug refractory epilepsy",
            "drug refractory epilepsies",
            "refractory epilepsies",
        }
    ),
    frozenset(
        {
            "focal",
            "focal seizure",
            "focal seizures",
            "epileptic",
            "epileptic seizure",
            "epileptic seizures",
            "temporal lobe onset seizure",
            "temporal lobe seizure",
            "temporal lobe seizures",
        }
    ),
    frozenset(
        {
            "complex partial seizure",
            "complex partial seizures",
            "dyscognitive seizures",
            "focal dyscognitive seizures",
            "focal seizures with altered awareness",
        }
    ),
    frozenset(
        {
            "focal to bilateral convulsive seizure",
            "focal to bilateral convulsive seizures",
            "focal to bilateral seizures",
            "focal to bilateral tonic clonic seizures",
            "secondary generalisation",
            "secondary generalised seizures",
            "secondary generalised tonic clonic seizures",
            "secondarily generalised seizures",
        }
    ),
    frozenset(
        {
            "absence seizures",
            "typical absences",
        }
    ),
    frozenset(
        {
            "generalised",
            "generalised seizures",
            "generalised tonic seizures",
            "grand mal",
            "tonic clonic convulsion",
            "tonic clonic seizures",
        }
    ),
)

_NEGATED_FOCAL = re.compile(r"\b(?:no|not|never)\b[^.\n]{0,100}\bfocal seizures?\b", re.I)
_NEGATED_ABSENCE = re.compile(r"\b(?:no|not|never)\b[^.\n]{0,100}\babsences?\b", re.I)
_ABSENCE_LIKE = re.compile(r"\babsence[- ]like\b", re.I)
_AMBIGUITY_CUE = re.compile(
    r"\b(?:possible|possibly|probable|probably|suggestive|suspected|query|may|might|"
    r"difficult to be sure|not very clear|unclear|possibility|no|not|never|mother|father|"
    r"family history)\b",
    re.I,
)
_NON_WORD = re.compile(r"[^a-z0-9]+")
_RELATION_STOPWORDS = frozenset(
    {
        "alone",
        "epilepsy",
        "epileptic",
        "lobe",
        "multiple",
        "onset",
        "seizure",
        "seizures",
        "single",
        "structural",
        "symptomatic",
        "with",
    }
)


def build_pattern_assisted_review(
    *,
    audit_jsonl: Path,
    manual_overlay_json: Path,
    out_overlay_json: Path | None = None,
    out_summary_json: Path | None = None,
    timestamp: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Preserve manual decisions and add non-conflicting automatic labels."""

    rows = [
        json.loads(line)
        for line in audit_jsonl.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    row_by_key = {str(row["review_key"]): row for row in rows}
    if len(row_by_key) != len(rows):
        raise ValueError("audit contains duplicate review keys")

    manual_overlay = json.loads(manual_overlay_json.read_text(encoding="utf-8"))
    manual_decisions = dict(manual_overlay.get("decisions", {}))
    unknown_manual = set(manual_decisions) - set(row_by_key)
    if unknown_manual:
        raise ValueError(f"manual overlay contains unknown review keys: {sorted(unknown_manual)}")
    expected_rows = manual_overlay.get("source_review_row_count")
    if expected_rows is not None and expected_rows != len(rows):
        raise ValueError(
            f"manual overlay row count mismatch: overlay={expected_rows}, audit={len(rows)}"
        )

    now = timestamp or datetime.now(UTC).isoformat().replace("+00:00", "Z")
    row_groups = _rows_by_letter_and_method(rows)
    decisions = dict(manual_decisions)
    automatic_rules: Counter[str] = Counter()
    automatic_triage: Counter[str] = Counter()
    automatic_methods: Counter[str] = Counter()
    conflicts: dict[str, list[str]] = {}

    for key, row in row_by_key.items():
        if key in manual_decisions:
            continue
        matches = _matching_rules(row, row_groups)
        triages = {triage for triage, _rule in matches}
        if len(triages) != 1:
            if len(triages) > 1:
                conflicts[key] = sorted(f"{triage}:{rule}" for triage, rule in matches)
            continue
        triage = next(iter(triages))
        rules = sorted(rule for _triage, rule in matches)
        decisions[key] = {
            "triage": triage,
            "note": f"[auto:{','.join(rules)}] Pattern-assisted hypothesis; confirm if needed.",
            "updated_at": now,
        }
        automatic_triage[triage] += 1
        automatic_rules.update(rules)
        automatic_methods.update(row.get("methods", []))

    manual_after = {key: decisions[key] for key in manual_decisions}
    if manual_after != manual_decisions:
        raise AssertionError("pattern pass changed a manual decision")

    overlay = {
        "schema_version": OVERLAY_SCHEMA,
        "exported_at": now,
        "source_gold_sha256": manual_overlay.get("source_gold_sha256"),
        "source_audit_schema": manual_overlay.get("source_audit_schema"),
        "source_review_row_count": len(rows),
        "triaged_count": len(decisions),
        "decisions": decisions,
    }
    automatic_count = len(decisions) - len(manual_decisions)
    remaining_keys = sorted(set(row_by_key) - set(decisions))
    calibration = _calibration_summary(row_by_key, manual_decisions, row_groups)
    summary = {
        "schema_version": SUMMARY_SCHEMA,
        "generated_at": now,
        "audit_jsonl": str(audit_jsonl),
        "audit_sha256": sha256_file(audit_jsonl),
        "manual_overlay_json": str(manual_overlay_json),
        "manual_overlay_sha256": sha256_file(manual_overlay_json),
        "audit_row_count": len(rows),
        "manual_decision_count": len(manual_decisions),
        "automatic_decision_count": automatic_count,
        "remaining_manual_review_count": len(remaining_keys),
        "remaining_manual_review_keys": remaining_keys,
        "conflict_count": len(conflicts),
        "automatic_triage_counts": dict(sorted(automatic_triage.items())),
        "automatic_rule_counts": dict(sorted(automatic_rules.items())),
        "automatic_method_memberships": dict(sorted(automatic_methods.items())),
        "conflicts": conflicts,
        "manual_calibration": calibration,
        "claim_boundary": (
            "Diagnostic dev140 review aid; automatic labels are hypotheses, not independent "
            "clinical adjudication, corrected gold, or scorer changes."
        ),
    }
    if len(decisions) + len(remaining_keys) != len(rows):
        raise AssertionError("review counts do not reconcile")

    _write_json(out_overlay_json, overlay)
    _write_json(out_summary_json, summary)
    return overlay, summary


def _matching_rules(
    row: Mapping[str, Any],
    row_groups: Mapping[tuple[str, str], list[Mapping[str, Any]]],
) -> set[tuple[str, str]]:
    matches: set[tuple[str, str]] = set()
    concept = str(row["normalized_concept"]).lower()
    note = str(row.get("note_text", ""))

    if row["direction"] == "spurious" and concept == "myoclonic seizures":
        return matches

    if row["direction"] == "spurious" and concept in _NON_TARGET_CONCEPTS:
        matches.add(("extraction_error", "non_target_diagnosis_scope"))
    if (
        row["direction"] == "spurious"
        and concept == "focal seizures"
        and _NEGATED_FOCAL.search(note)
    ):
        matches.add(("extraction_error", "reviewed_negated_focal_pattern"))
    if row["direction"] == "spurious" and concept == "absence seizures":
        if _ABSENCE_LIKE.search(note):
            matches.add(("uncertain", "reviewed_absence_like_pattern"))
        elif _NEGATED_ABSENCE.search(note):
            matches.add(("extraction_error", "reviewed_negated_absence_pattern"))
    if (
        row["direction"] == "spurious"
        and concept == "epilepsy"
        and re.search(r"\bdiscussion about epilepsy in general\b", note, re.I)
    ):
        matches.add(("extraction_error", "reviewed_generic_discussion_pattern"))
    if row["direction"] == "spurious" and concept == "generalised epilepsy":
        for method in row.get("methods", []):
            method_concepts = _method_concepts(row, str(method))
            if "genetic generalised epilepsy" in method_concepts:
                matches.add(("extraction_error", "redundant_generic_parent"))

    if matches:
        return matches

    for method in row.get("methods", []):
        peers = row_groups.get((str(row["letter_id"]), str(method)), [])
        for peer in peers:
            if peer["direction"] == row["direction"]:
                continue
            if _target_cuis(row, str(method)) & _target_cuis(peer, str(method)):
                matches.add(("representation", "opposite_direction_same_cui"))
            if _same_review_equivalence_family(
                str(row["normalized_concept"]), str(peer["normalized_concept"])
            ):
                matches.add(("representation", "reviewed_equivalence_pair"))
    if matches:
        return matches

    if row["direction"] == "missed":
        if any(
            _concepts_related(concept, candidate)
            for method in row.get("methods", [])
            for candidate in _method_concepts(row, str(method))
        ):
            matches.add(("representation", "related_prediction_representation"))
        else:
            matches.add(("extraction_error", "unsupported_gold_concept_miss"))
        return matches

    gold_concepts = _gold_concepts(row)
    if any(_concepts_related(concept, gold) for gold in gold_concepts):
        matches.add(("representation", "related_gold_representation"))
        return matches

    contexts = _target_contexts(row)
    if contexts and all(_AMBIGUITY_CUE.search(context) for context in contexts):
        return matches
    if contexts:
        matches.add(("representation", "supported_gold_omission"))
    elif concept != "epilepsy":
        matches.add(("extraction_error", "unsupported_spurious_concept"))
    return matches


def _rows_by_letter_and_method(
    rows: Iterable[Mapping[str, Any]],
) -> dict[tuple[str, str], list[Mapping[str, Any]]]:
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        for method in row.get("methods", []):
            grouped[(str(row["letter_id"]), str(method))].append(row)
    return dict(grouped)


def _target_cuis(row: Mapping[str, Any], method: str) -> set[str]:
    if row["direction"] == "missed":
        mentions = row.get("gold_diagnosis_mentions", [])
    else:
        mentions = row.get("method_records", {}).get(method, {}).get(
            "diagnosis_candidate_mentions", []
        )
    concept = str(row["normalized_concept"])
    cuis: set[str] = set()
    for mention in mentions:
        if mention.get("entity") != "Diagnosis":
            continue
        if concept not in mention.get("normalized_diagnosis_concepts", []):
            continue
        cui = mention.get("attributes", {}).get("CUI")
        if cui:
            cuis.add(str(cui))
    return cuis


def _same_review_equivalence_family(first: str, second: str) -> bool:
    first = first.lower()
    second = second.lower()
    if first == second:
        return False
    return any(first in family and second in family for family in _REVIEW_EQUIVALENCE_FAMILIES)


def _concepts_related(first: str, second: str) -> bool:
    first = _normalize_text(first)
    second = _normalize_text(second)
    if first == second or _same_review_equivalence_family(first, second):
        return True
    if "status epilepticus" in {first, second}:
        return False
    if {first, second} <= {"absence seizures", "juvenile myoclonic epilepsy"}:
        return True
    if {first, second} <= {"myoclonic seizures", "juvenile myoclonic epilepsy"}:
        return True
    if (
        "epilep" in first
        and "epilep" in second
        and "non epilep" not in first
        and "non epilep" not in second
        and "dissociative" not in first
        and "dissociative" not in second
    ):
        return True
    first_tokens = set(first.split()) - _RELATION_STOPWORDS
    second_tokens = set(second.split()) - _RELATION_STOPWORDS
    if first_tokens and second_tokens and (
        first_tokens <= second_tokens
        or second_tokens <= first_tokens
        or len(first_tokens & second_tokens) >= 2
    ):
        return True
    if first == "focal epilepsy" and (
        "focal" in second or "bilateral convulsive" in second
    ):
        return True
    if second == "focal epilepsy" and (
        "focal" in first or "bilateral convulsive" in first
    ):
        return True
    return False


def _gold_concepts(row: Mapping[str, Any]) -> set[str]:
    return {
        _normalize_text(concept)
        for mention in row.get("gold_diagnosis_mentions", [])
        for concept in mention.get("normalized_diagnosis_concepts", [])
    }


def _method_concepts(row: Mapping[str, Any], method: str) -> set[str]:
    return {
        _normalize_text(concept)
        for mention in row.get("method_records", {}).get(method, {}).get(
            "diagnosis_candidate_mentions", []
        )
        if mention.get("entity") == "Diagnosis"
        for concept in mention.get("normalized_diagnosis_concepts", [])
    }


def _target_contexts(row: Mapping[str, Any]) -> list[str]:
    note = str(row.get("note_text", ""))
    contexts: list[str] = []
    if row["direction"] == "missed":
        for mention in row.get("gold_diagnosis_mentions", []):
            if row["normalized_concept"] not in mention.get(
                "normalized_diagnosis_concepts", []
            ):
                continue
            start = max(0, int(mention.get("start_index", 0)) - 90)
            end = min(len(note), int(mention.get("end_index", 0)) + 50)
            contexts.append(note[start:end])
        return contexts

    needles: set[str] = set()
    for method in row.get("methods", []):
        for mention in row.get("method_records", {}).get(method, {}).get(
            "diagnosis_candidate_mentions", []
        ):
            if row["normalized_concept"] not in mention.get(
                "normalized_diagnosis_concepts", []
            ):
                continue
            for field in ("evidence", "text"):
                value = str(mention.get(field, "")).strip()
                if value:
                    needles.add(value)
    for needle in needles:
        contexts.extend(_find_contexts(note, needle))
    if not contexts:
        contexts.extend(_find_contexts(note, str(row["normalized_concept"])))
    if not contexts and row["normalized_concept"] == "absence seizures":
        contexts.extend(_find_contexts(note, "absences"))
        contexts.extend(_find_contexts(note, "absence events"))
    return contexts


def _find_contexts(note: str, needle: str) -> list[str]:
    tokens = _normalize_text(needle).split()
    if not tokens:
        return []
    pattern = re.compile(r"\b" + r"[^A-Za-z0-9]+".join(map(re.escape, tokens)) + r"\b", re.I)
    return [
        note[max(0, match.start() - 90) : min(len(note), match.end() + 50)]
        for match in pattern.finditer(note)
    ]


def _normalize_text(value: str) -> str:
    return _NON_WORD.sub(" ", value.lower()).strip()


def _calibration_summary(
    row_by_key: Mapping[str, Mapping[str, Any]],
    manual_decisions: Mapping[str, Mapping[str, Any]],
    row_groups: Mapping[tuple[str, str], list[Mapping[str, Any]]],
) -> dict[str, Any]:
    matched = 0
    contradicted: dict[str, dict[str, Any]] = {}
    unclassified: list[str] = []
    for key, decision in manual_decisions.items():
        matches = _matching_rules(row_by_key[key], row_groups)
        triages = {triage for triage, _rule in matches}
        expected = str(decision.get("triage", ""))
        if triages == {expected}:
            matched += 1
        elif not triages:
            unclassified.append(key)
        else:
            contradicted[key] = {
                "manual": expected,
                "automatic": sorted(triages),
                "rules": sorted(rule for _triage, rule in matches),
            }
    return {
        "manual_count": len(manual_decisions),
        "matched_count": matched,
        "unclassified_count": len(unclassified),
        "unclassified_keys": sorted(unclassified),
        "contradicted_count": len(contradicted),
        "contradictions": contradicted,
    }



def _write_json(path: Path | None, payload: Mapping[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
