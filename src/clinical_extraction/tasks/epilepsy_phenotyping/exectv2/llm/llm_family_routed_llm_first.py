"""Predeclared family-routed ExECTv2 LLM-first comparison.

This is an analysis-only replay over existing dev artifacts. It combines the
shared all-entities LLM pass for Prescription, Investigations, and Diagnosis
with the current SeizureFrequency event/state route, then scores the
predeclared four-family clinical-recovery surface.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    run_all9_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.clinical_recovery_scorecard import (  # noqa: E501
    build_scorecard,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.family_routed_preflight import (  # noqa: E501
    build_family_routed_preflight,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first_essential_evaluation import (  # noqa: E501
    OWNERSHIP_HYBRID,
    OWNERSHIP_LLM_FIRST,
    OWNERSHIP_RULES_ONLY,
    _aggregate_score_dicts,
    _score_for_primary,
    _strip_and_project,
    _strip_gold_cui,
    _strip_prediction_cui,
    align_predictions_to_gold,
    architecture_report,
    evidence_validation_summary,
    predicted_by_id_from_artifact,
    row_level_error_ledger,
)

PIPELINE_FAMILY = "exectv2_family_routed_llm_first"
MODEL = "openai/gpt-4.1-mini"
ROUTED_PRIMARY_ENTITIES: tuple[str, ...] = (
    PRESCRIPTION.name,
    INVESTIGATIONS.name,
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY.name,
)
SHARED_PASS_ENTITIES = frozenset({PRESCRIPTION.name, INVESTIGATIONS.name, DIAGNOSIS.name})
SF_ROUTE_ENTITIES = frozenset({SEIZURE_FREQUENCY.name})
DIAGNOSIS_ROUTE_ENTITIES = frozenset({DIAGNOSIS.name})
FOCUSED_DIAGNOSIS_AGGREGATE_OWNERSHIP = "llm_first_with_hybrid_diagnosis_and_sf_routes"

DEFAULT_SHARED_PASS_ARTIFACT = Path(
    "experiments/exectv2_llm_only_all_entities_dev140_gpt41mini_20260612.jsonl"
)
DEFAULT_SF_ROUTE_ARTIFACT = Path(
    "experiments/exectv2_hybrid_sf_unknown_suppression_v07_dev140_20260618.jsonl"
)
DEFAULT_HYBRID_COMPARATOR_ARTIFACT = Path(
    "experiments/exectv2_hybrid_all_entities_dev140_gpt41mini_20260617.jsonl"
)
DEFAULT_DIAGNOSIS_ROUTE_ARTIFACT = Path(
    "experiments/exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618.jsonl"
)
DEFAULT_OUT_JSON = Path(
    "experiments/exectv2_family_routed_llm_first_dev140_gpt41mini_20260618.json"
)
DEFAULT_OUT_JSONL = Path(
    "experiments/exectv2_family_routed_llm_first_dev140_gpt41mini_20260618.jsonl"
)
DEFAULT_OUT_MD = Path(
    "docs/experiments/exectv2/key_entities/"
    "exectv2_family_routed_llm_first_comparison_2026-06-18.md"
)
DEFAULT_PILOT_JSON = Path(
    "experiments/exectv2_family_routed_llm_first_pilot25_gpt41mini_20260618.json"
)
DEFAULT_PILOT_JSONL = Path(
    "experiments/exectv2_family_routed_llm_first_pilot25_gpt41mini_20260618.jsonl"
)


def combine_family_routed_predictions(
    gold_letters: Sequence[ExectLetter],
    shared_pass_by_id: Mapping[str, PredictedLetter],
    sf_route_by_id: Mapping[str, PredictedLetter],
    diagnosis_route_by_id: Mapping[str, PredictedLetter] | None = None,
) -> list[PredictedLetter]:
    """Combine shared-pass P/I/D mentions with routed SF mentions."""

    routed: list[PredictedLetter] = []
    shared_entities = SHARED_PASS_ENTITIES
    aggregate_ownership = "llm_first_with_hybrid_sf_route"
    if diagnosis_route_by_id is not None:
        shared_entities = frozenset({PRESCRIPTION.name, INVESTIGATIONS.name})
        aggregate_ownership = FOCUSED_DIAGNOSIS_AGGREGATE_OWNERSHIP

    for gold in gold_letters:
        shared = shared_pass_by_id.get(
            gold.letter_id,
            PredictedLetter(letter_id=gold.letter_id, mentions=()),
        )
        sf_route = sf_route_by_id.get(
            gold.letter_id,
            PredictedLetter(letter_id=gold.letter_id, mentions=()),
        )
        diagnosis_route = (
            diagnosis_route_by_id.get(
                gold.letter_id,
                PredictedLetter(letter_id=gold.letter_id, mentions=()),
            )
            if diagnosis_route_by_id is not None
            else PredictedLetter(letter_id=gold.letter_id, mentions=())
        )
        mentions = (
            tuple(
                _with_owner(m, OWNERSHIP_LLM_FIRST)
                for m in shared.mentions
                if m.entity in shared_entities
            )
            + tuple(
                _with_owner(m, "hybrid_diagnosis_reconciler")
                for m in diagnosis_route.mentions
                if m.entity in DIAGNOSIS_ROUTE_ENTITIES
            )
            + tuple(
                _with_owner(m, "hybrid_sf_route")
                for m in sf_route.mentions
                if m.entity in SF_ROUTE_ENTITIES
            )
        )
        routed.append(
            PredictedLetter(
                letter_id=gold.letter_id,
                mentions=mentions,
                diagnostics={
                    "pipeline_family": PIPELINE_FAMILY,
                    "shared_pass_entities": sorted(shared_entities),
                    "diagnosis_route_entities": (
                        sorted(DIAGNOSIS_ROUTE_ENTITIES)
                        if diagnosis_route_by_id is not None
                        else []
                    ),
                    "sf_route_entities": sorted(SF_ROUTE_ENTITIES),
                    "prescription_investigations_route_policy": (
                        "shared_broad_pass_only"
                    ),
                    "aggregate_ownership": aggregate_ownership,
                },
            )
        )
    return routed


def build_family_routed_comparison(
    *,
    split: str = "dev",
    pilot_size: int | None = None,
    shared_pass_artifact: Path = DEFAULT_SHARED_PASS_ARTIFACT,
    sf_route_artifact: Path = DEFAULT_SF_ROUTE_ARTIFACT,
    hybrid_comparator_artifact: Path = DEFAULT_HYBRID_COMPARATOR_ARTIFACT,
) -> dict[str, Any]:
    """Build the predeclared routed comparison without model calls."""

    preflight = build_family_routed_preflight(Path("."))
    if not preflight.can_run_dev_ladder:
        blockers = ", ".join(check.name for check in preflight.blockers)
        raise RuntimeError(f"family-routed preflight is blocked: {blockers}")

    gold_letters = load_letters_for_split(split)
    if pilot_size is not None:
        gold_letters = gold_letters[:pilot_size]

    shared_by_id = predicted_by_id_from_artifact(shared_pass_artifact)
    sf_by_id = predicted_by_id_from_artifact(sf_route_artifact)
    hybrid_by_id = predicted_by_id_from_artifact(hybrid_comparator_artifact)

    deterministic = run_all9_on_letters(gold_letters)
    llm_only = align_predictions_to_gold(gold_letters, shared_by_id)
    hybrid = align_predictions_to_gold(gold_letters, hybrid_by_id)
    routed = combine_family_routed_predictions(gold_letters, shared_by_id, sf_by_id)

    candidates = [
        _candidate_report(
            name="deterministic_all9",
            ownership=OWNERSHIP_RULES_ONLY,
            gold_letters=gold_letters,
            pred_letters=deterministic,
        ),
        _candidate_report(
            name="llm_only_all_entities",
            ownership=OWNERSHIP_LLM_FIRST,
            gold_letters=gold_letters,
            pred_letters=llm_only,
        ),
        _candidate_report(
            name="hybrid_all_entities",
            ownership=OWNERSHIP_HYBRID,
            gold_letters=gold_letters,
            pred_letters=hybrid,
        ),
        _candidate_report(
            name="family_routed_llm_first",
            ownership="llm_first_with_hybrid_sf_route",
            gold_letters=gold_letters,
            pred_letters=routed,
        ),
    ]
    route_summary = _route_summary(
        gold_letters=gold_letters,
        shared_rows=_rows_by_id(shared_pass_artifact),
        sf_rows=_rows_by_id(sf_route_artifact),
        routed_predictions=routed,
    )
    return {
        "pipeline_family": PIPELINE_FAMILY,
        "model": MODEL,
        "generated_on": date.today().isoformat(),
        "split": split,
        "stage": f"pilot{pilot_size}" if pilot_size is not None else "dev140",
        "row_count": len(gold_letters),
        "primary_entities": list(ROUTED_PRIMARY_ENTITIES),
        "input_artifacts": {
            "shared_pass": str(shared_pass_artifact).replace("\\", "/"),
            "sf_route": str(sf_route_artifact).replace("\\", "/"),
            "hybrid_comparator": str(hybrid_comparator_artifact).replace("\\", "/"),
        },
        "preflight": {
            "can_run_dev_ladder": preflight.can_run_dev_ladder,
            "planned_dev_ladder": list(preflight.planned_dev_ladder),
        },
        "route_summary": route_summary,
        "candidates": candidates,
        "gate_decision": _gate_decision(candidates, route_summary),
    }


def write_family_routed_outputs(
    *,
    out_json: Path = DEFAULT_OUT_JSON,
    out_jsonl: Path = DEFAULT_OUT_JSONL,
    out_md: Path = DEFAULT_OUT_MD,
    pilot_json: Path = DEFAULT_PILOT_JSON,
    pilot_jsonl: Path = DEFAULT_PILOT_JSONL,
    split: str = "dev",
    pilot_size: int = 25,
) -> dict[str, Path]:
    """Run pilot25 then dev140 replay and write comparison artifacts."""

    pilot_report = build_family_routed_comparison(split=split, pilot_size=pilot_size)
    dev_report = build_family_routed_comparison(split=split)
    shared_rows = _rows_by_id(DEFAULT_SHARED_PASS_ARTIFACT)
    sf_rows = _rows_by_id(DEFAULT_SF_ROUTE_ARTIFACT)

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    pilot_json.parent.mkdir(parents=True, exist_ok=True)
    pilot_jsonl.parent.mkdir(parents=True, exist_ok=True)

    pilot_json.write_text(
        json.dumps(pilot_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    out_json.write_text(
        json.dumps(dev_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_routed_jsonl(
        pilot_jsonl,
        split=split,
        pilot_size=pilot_size,
        shared_rows=shared_rows,
        sf_rows=sf_rows,
    )
    _write_routed_jsonl(
        out_jsonl,
        split=split,
        pilot_size=None,
        shared_rows=shared_rows,
        sf_rows=sf_rows,
    )
    out_md.write_text(
        render_family_routed_markdown(
            dev_report,
            pilot_report=pilot_report,
            json_path=out_json,
            jsonl_path=out_jsonl,
        ),
        encoding="utf-8",
    )
    return {
        "pilot_json": pilot_json,
        "pilot_jsonl": pilot_jsonl,
        "json": out_json,
        "jsonl": out_jsonl,
        "md": out_md,
    }


def render_family_routed_markdown(
    report: Mapping[str, Any],
    *,
    pilot_report: Mapping[str, Any] | None = None,
    json_path: Path | None = None,
    jsonl_path: Path | None = None,
) -> str:
    """Render the human-readable predeclared comparison report."""

    candidates = {c["name"]: c for c in report["candidates"]}
    routed = candidates["family_routed_llm_first"]
    single = candidates["llm_only_all_entities"]
    gate = report["gate_decision"]
    lines = [
        "# ExECTv2 Family-Routed LLM-First Comparison",
        "",
        f"- Generated: `{report['generated_on']}`",
        f"- Split/stage: `{report['split']}` / `{report['stage']}`",
        f"- Rows: `{report['row_count']}`",
        f"- Primary routed families: `{', '.join(report['primary_entities'])}`",
        f"- Gate decision: **{gate['decision']}**",
        f"- Ownership: `{routed['ownership']}`",
    ]
    if json_path is not None:
        lines.append(f"- JSON: `{json_path.as_posix()}`")
    if jsonl_path is not None:
        lines.append(f"- JSONL: `{jsonl_path.as_posix()}`")
    if pilot_report is not None:
        pilot_gate = pilot_report["gate_decision"]["decision"]
        lines.append(f"- Pilot25 replay: `{pilot_gate}` over `{pilot_report['row_count']}` rows")

    lines += [
        "",
        "## Key Insight",
        "",
        (
            "The family-routed candidate improves the four-family CUI-free "
            "clinical-recovery headline from "
            f"`{single['routed_primary_recovery']['overall']['f1']:.4f}` to "
            f"`{routed['routed_primary_recovery']['overall']['f1']:.4f}` by replacing the "
            "collapsed single-pass SeizureFrequency surface with the event/state route. "
            "The result is a qualified architecture win, not a clean LLM-first benchmark "
            "claim, because the SF source uses deterministic candidate/projection and "
            "unknown-suppression policy."
        ),
        "",
        (
            "Prescription and Investigations are deliberately preserved from the shared "
            "broad all-entities pass in this routed candidate. Specialist P/I verifier "
            "artifacts remain separate candidates until a fresh predeclaration and "
            "ablation show that replacing the shared pass improves the intended routed "
            "surface without family regression or ownership ambiguity."
        ),
        "",
        "## Table 1: Architecture Ownership",
        "",
        (
            "| Candidate | Owner | Prediction-bearing component | "
            "Deterministic adapters | Claim allowed |"
        ),
        "| --- | --- | --- | --- | --- |",
    ]
    for candidate in report["candidates"]:
        ownership = candidate["ownership"]
        if candidate["name"] == "family_routed_llm_first":
            component = "shared P/I/D pass + SF event/state route"
            adapters = "evidence/CUI/certainty/rendering + SF suppression/projection"
            claim = "dev architecture evidence, qualified ownership"
        elif candidate["name"] == "llm_only_all_entities":
            component = "single broad LLM pass"
            adapters = "evidence/CUI/certainty/rendering"
            claim = "negative baseline"
        elif candidate["name"] == "hybrid_all_entities":
            component = "candidate set + verifier"
            adapters = "projection/rendering"
            claim = "hybrid comparator"
        else:
            component = "deterministic rules"
            adapters = "projection/scorer"
            claim = "rules baseline"
        lines.append(
            f"| {candidate['name']} | `{ownership}` | {component} | {adapters} | {claim} |"
        )

    lines += [
        "",
        "## Table 2: Aggregate Essential Clinical Recovery",
        "",
        (
            "| Candidate | Families | CUI-free F1 | Precision | Recall | "
            "CUI-projected F1 | Evidence exact |"
        ),
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for candidate in report["candidates"]:
        overall = candidate["routed_primary_recovery"]["overall"]
        projected = candidate["routed_primary_recovery"]["cui_projected_overall"]
        evidence = candidate["routed_primary_evidence"]["overall"]
        lines.append(
            f"| {candidate['name']} | routed four | {overall['f1']:.4f} "
            f"| {overall['precision']:.4f} | {overall['recall']:.4f} "
            f"| {projected['f1']:.4f} | {evidence['exact_evidence_rate']:.4f} |"
        )

    lines += [
        "",
        "## Table 3: Per-Family Recovery",
        "",
        "| Family | Single-pass F1 | Routed F1 | Delta | Evidence exact | Dominant residual |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for family in ROUTED_PRIMARY_ENTITIES:
        single_score = single["routed_primary_recovery"]["headline_scores"][family]
        routed_score = routed["routed_primary_recovery"]["headline_scores"][family]
        delta = routed_score["f1"] - single_score["f1"]
        evidence = routed["routed_primary_evidence"][family]["exact_evidence_rate"]
        residual = _dominant_residual(routed["routed_primary_errors"]["per_entity"][family])
        lines.append(
            f"| {family} | {single_score['f1']:.4f} | {routed_score['f1']:.4f} "
            f"| {delta:+.4f} | {evidence:.4f} | {residual} |"
        )

    route = report["route_summary"]["sf_route"]
    state_dist = ", ".join(
        f"{key}: {value}" for key, value in route["state_distribution"].items()
    )
    lines += [
        "",
        "## Table 4: SF Event/State Diagnostics",
        "",
        "| SF diagnostic | Count or rate | Notes |",
        "| --- | ---: | --- |",
        f"| emitted event/state records | {route['predicted_mentions']} | dev routed SF mentions |",
        (
            f"| exact evidence records | {route['exact_evidence_mentions']} | "
            f"{route['exact_evidence_rate']:.4f} exact-evidence rate |"
        ),
        (
            f"| active/seizure-free/unknown distribution | {state_dist or 'none'} | "
            "derived from rendered attributes |"
        ),
        (
            f"| parse/call failures | {route['call_or_parse_failures']} | "
            "source artifact row-level statuses |"
        ),
        (
            f"| deterministic projection actions | {route['projection_actions']} | "
            "named SF projection layer |"
        ),
        (
            f"| deterministic unknown suppression/defaulting | {route['suppression_actions']} | "
            "named suppression layer |"
        ),
        "",
        "## Gate Notes",
        "",
    ]
    for note in gate["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def _candidate_report(
    *,
    name: str,
    ownership: str,
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[PredictedLetter],
) -> dict[str, Any]:
    report = architecture_report(
        name=name,
        ownership=ownership,
        gold_letters=gold_letters,
        pred_letters=pred_letters,
    )
    report["routed_primary_recovery"] = _routed_primary_recovery(gold_letters, pred_letters)
    report["routed_primary_evidence"] = evidence_validation_summary(
        gold_letters,
        pred_letters,
        ROUTED_PRIMARY_ENTITIES,
    )
    report["routed_primary_errors"] = _routed_error_taxonomy(gold_letters, pred_letters)
    return report


def _routed_primary_recovery(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[PredictedLetter],
) -> dict[str, Any]:
    cui_free = build_scorecard(
        _strip_gold_cui(gold_letters),
        _strip_prediction_cui(pred_letters),
    )
    projected = build_scorecard(gold_letters, _strip_and_project(pred_letters))
    scores = {
        entity: _score_for_primary(entity, cui_free)
        for entity in ROUTED_PRIMARY_ENTITIES
    }
    projected_scores = {
        entity: _score_for_primary(entity, projected)
        for entity in ROUTED_PRIMARY_ENTITIES
    }
    return {
        "primary_entities": list(ROUTED_PRIMARY_ENTITIES),
        "overall": _aggregate_score_dicts(tuple(scores.values())),
        "headline_scores": scores,
        "cui_projected_overall": _aggregate_score_dicts(tuple(projected_scores.values())),
        "cui_projected_headline_scores": projected_scores,
    }


def _routed_error_taxonomy(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[PredictedLetter],
) -> dict[str, Any]:
    rows = row_level_error_ledger(
        architecture=PIPELINE_FAMILY,
        ownership="routed_primary_surface",
        gold_letters=gold_letters,
        pred_letters=pred_letters,
        families=ROUTED_PRIMARY_ENTITIES,
    )
    per_entity = {
        entity: {
            "candidate_miss": 0,
            "wrong_detail_selection": 0,
            "projection_gap": 0,
            "evidence_failure": 0,
        }
        for entity in ROUTED_PRIMARY_ENTITIES
    }
    for row in rows:
        per_entity[row["family"]][row["error_type"]] += int(row["count"])
    totals = {key: 0 for key in next(iter(per_entity.values()))}
    for stats in per_entity.values():
        for key, value in stats.items():
            totals[key] += value
    return {"overall": totals, "per_entity": per_entity}


def _gate_decision(
    candidates: Sequence[Mapping[str, Any]],
    route_summary: Mapping[str, Any],
) -> dict[str, Any]:
    by_name = {c["name"]: c for c in candidates}
    single = by_name["llm_only_all_entities"]
    routed = by_name["family_routed_llm_first"]
    single_overall = single["routed_primary_recovery"]["overall"]["f1"]
    routed_overall = routed["routed_primary_recovery"]["overall"]["f1"]
    sf_score = routed["routed_primary_recovery"]["headline_scores"][SEIZURE_FREQUENCY.name]
    p_delta = (
        routed["routed_primary_recovery"]["headline_scores"][PRESCRIPTION.name]["f1"]
        - single["routed_primary_recovery"]["headline_scores"][PRESCRIPTION.name]["f1"]
    )
    i_delta = (
        routed["routed_primary_recovery"]["headline_scores"][INVESTIGATIONS.name]["f1"]
        - single["routed_primary_recovery"]["headline_scores"][INVESTIGATIONS.name]["f1"]
    )
    evidence_exact = routed["routed_primary_evidence"]["overall"]["exact_evidence_rate"]
    route = route_summary["sf_route"]
    promoted = (
        routed_overall > single_overall
        and sf_score["f1"] >= 0.60
        and p_delta >= -0.03
        and i_delta >= -0.03
        and evidence_exact >= 0.95
        and route["call_or_parse_failures"] == 0
    )
    decision = "dev-gate-passed-qualified" if promoted else "dev-gate-not-passed"
    notes = [
        (
            f"Four-family F1 delta vs single pass: {routed_overall - single_overall:+.4f} "
            f"({single_overall:.4f} -> {routed_overall:.4f})."
        ),
        f"Routed SF F1: {sf_score['f1']:.4f}; threshold was 0.6000.",
        (
            f"Prescription delta {p_delta:+.4f}; Investigations delta {i_delta:+.4f}; "
            "allowed regression floor was -0.0300."
        ),
        f"Routed exact-evidence rate: {evidence_exact:.4f}.",
        (
            "Ownership is downgraded to `llm_first_with_hybrid_sf_route` because the SF "
            "source uses deterministic candidate/projection and unknown-suppression layers."
        ),
    ]
    return {"decision": decision, "notes": notes}


def _route_summary(
    *,
    gold_letters: Sequence[ExectLetter],
    shared_rows: Mapping[str, Mapping[str, Any]],
    sf_rows: Mapping[str, Mapping[str, Any]],
    routed_predictions: Sequence[PredictedLetter],
) -> dict[str, Any]:
    gold_by_id = {letter.letter_id: letter for letter in gold_letters}
    state_counts: Counter[str] = Counter()
    projection_actions = 0
    suppression_actions = 0
    call_or_parse_failures = 0
    exact_evidence = 0
    predicted = 0
    for letter in routed_predictions:
        row = sf_rows.get(letter.letter_id, {})
        projection_actions += len(row.get("projection_actions", []))
        suppression_actions += len(row.get("suppression_actions", []))
        if row.get("call_error") or row.get("parse_errors"):
            call_or_parse_failures += 1
        note = gold_by_id[letter.letter_id].note_text
        for mention in letter.mentions:
            if mention.entity != SEIZURE_FREQUENCY.name:
                continue
            predicted += 1
            state_counts[_sf_state(mention)] += 1
            if mention.evidence and mention.evidence in note:
                exact_evidence += 1
    return {
        "shared_pass": {
            "artifact_rows": len(shared_rows),
            "families_used": sorted(SHARED_PASS_ENTITIES),
        },
        "sf_route": {
            "artifact_rows": len(sf_rows),
            "families_used": sorted(SF_ROUTE_ENTITIES),
            "component_owner": _most_common_field(sf_rows.values(), "component_owner"),
            "predicted_mentions": predicted,
            "exact_evidence_mentions": exact_evidence,
            "exact_evidence_rate": round(exact_evidence / predicted, 4) if predicted else 0.0,
            "state_distribution": dict(state_counts.most_common()),
            "projection_actions": projection_actions,
            "suppression_actions": suppression_actions,
            "call_or_parse_failures": call_or_parse_failures,
        },
    }


def _write_routed_jsonl(
    path: Path,
    *,
    split: str,
    pilot_size: int | None,
    shared_rows: Mapping[str, Mapping[str, Any]],
    sf_rows: Mapping[str, Mapping[str, Any]],
) -> None:
    gold_letters = load_letters_for_split(split)
    if pilot_size is not None:
        gold_letters = gold_letters[:pilot_size]
    shared_by_id = predicted_by_id_from_artifact(DEFAULT_SHARED_PASS_ARTIFACT)
    sf_by_id = predicted_by_id_from_artifact(DEFAULT_SF_ROUTE_ARTIFACT)
    routed_by_id = {
        letter.letter_id: letter
        for letter in combine_family_routed_predictions(gold_letters, shared_by_id, sf_by_id)
    }
    lines = []
    for gold in gold_letters:
        routed = routed_by_id[gold.letter_id]
        shared_row = shared_rows.get(gold.letter_id, {})
        sf_row = sf_rows.get(gold.letter_id, {})
        row = {
            "letter_id": gold.letter_id,
            "split": split,
            "stage": f"pilot{pilot_size}" if pilot_size is not None else "dev140",
            "pipeline_family": PIPELINE_FAMILY,
            "model": MODEL,
            "ownership": "llm_first_with_hybrid_sf_route",
            "sources": {
                "shared_pass": DEFAULT_SHARED_PASS_ARTIFACT.as_posix(),
                "sf_route": DEFAULT_SF_ROUTE_ARTIFACT.as_posix(),
            },
            "gold_mentions": [
                _gold_to_row(a)
                for a in gold.annotations
                if a.entity in ROUTED_PRIMARY_ENTITIES
            ],
            "predicted_mentions": [_mention_to_row(m) for m in routed.mentions],
            "shared_pass_mentions": [
                _mention_to_row(m)
                for m in shared_by_id.get(
                    gold.letter_id,
                    PredictedLetter(letter_id=gold.letter_id, mentions=()),
                ).mentions
                if m.entity in SHARED_PASS_ENTITIES
            ],
            "sf_route_mentions": [
                _mention_to_row(m)
                for m in sf_by_id.get(
                    gold.letter_id,
                    PredictedLetter(letter_id=gold.letter_id, mentions=()),
                ).mentions
                if m.entity in SF_ROUTE_ENTITIES
            ],
            "shared_pass_status": _status_from_row(shared_row),
            "sf_route_status": _status_from_row(sf_row),
            "shared_pass_raw_output": shared_row.get("raw_output", ""),
            "sf_route_raw_output": sf_row.get("raw_output", ""),
            "sf_route_diagnostics": {
                "component_owner": sf_row.get("component_owner", ""),
                "projection_version": sf_row.get("projection_version", ""),
                "suppression_version": sf_row.get("suppression_version", ""),
                "projection_actions": sf_row.get("projection_actions", []),
                "suppression_actions": sf_row.get("suppression_actions", []),
            },
        }
        lines.append(json.dumps(row, sort_keys=True))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _rows_by_id(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows[str(row["letter_id"])] = row
    return rows


def _with_owner(mention: PredictedMention, owner: str) -> PredictedMention:
    return mention.model_copy(update={"component_owner": owner})


def _mention_to_row(mention: PredictedMention) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "rationale": mention.rationale,
        "confidence": mention.confidence,
        "component_owner": mention.component_owner,
        "uncertainty_flags": list(mention.uncertainty_flags),
    }


def _gold_to_row(annotation: ExectAnnotation) -> dict[str, Any]:
    return {
        "entity": annotation.entity,
        "text": annotation.text,
        "attributes": dict(annotation.attributes),
    }


def _status_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "call_error": row.get("call_error"),
        "parse_errors": row.get("parse_errors", []),
        "gate_warnings": row.get("gate_warnings", []),
        "n_evidence_invalid": row.get("n_evidence_invalid", 0),
        "n_mentions_scored": row.get("n_mentions_scored", 0),
    }


def _sf_state(mention: PredictedMention) -> str:
    attrs = dict(mention.attributes)
    if attrs.get("NumberOfSeizures") == "0":
        return "seizure_free"
    if any(
        key in attrs
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
        )
    ):
        return "active_rate"
    if attrs.get("FrequencyChange"):
        return f"change_{attrs['FrequencyChange']}"
    return "unknown"


def _most_common_field(rows: Sequence[Mapping[str, Any]], field: str) -> str:
    values = [str(row.get(field, "")) for row in rows if row.get(field)]
    if not values:
        return ""
    return Counter(values).most_common(1)[0][0]


def _dominant_residual(row: Mapping[str, int]) -> str:
    if not row:
        return "none"
    key, value = max(row.items(), key=lambda item: item[1])
    return "none" if value <= 0 else f"{key} ({value})"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write the predeclared ExECTv2 family-routed comparison artifacts",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--split", default="dev")
    parser.add_argument("--pilot-size", type=int, default=25)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-jsonl", type=Path, default=DEFAULT_OUT_JSONL)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    args = parser.parse_args()

    outputs = write_family_routed_outputs(
        out_json=args.out_json,
        out_jsonl=args.out_jsonl,
        out_md=args.out_md,
        split=args.split,
        pilot_size=args.pilot_size,
    )
    for name, path in outputs.items():
        print(f"Wrote {name}: {path}")


if __name__ == "__main__":
    main()
