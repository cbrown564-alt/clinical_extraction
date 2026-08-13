"""Build the retained ExECTv2 annotation-evidence taxonomy.

This is a no-call synthesis over permitted development artifacts. It does not
read test60, edit gold, or change a scorer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

GENERATED_ON = "2026-07-15"
PROTOCOL_PATH = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_annotation_evidence_synthesis_protocol_2026-07-15.md"
)
MANIFEST_PATH = Path("docs/experiments/retained_evidence_manifest.json")
OUTPUT_PATH = Path("experiments/exectv2_annotation_evidence_synthesis_20260715.json")

LEDGER_PATHS = {
    "Diagnosis": Path("experiments/gold_case_ledger_diagnosis.jsonl"),
    "Investigations": Path("experiments/gold_case_ledger_investigations.jsonl"),
    "Prescription": Path("experiments/gold_case_ledger_prescription.jsonl"),
    "SeizureFrequency": Path("experiments/gold_case_ledger_seizurefrequency.jsonl"),
}
GOLD_ISSUES_PATH = Path("experiments/gold_data_issues.jsonl")
SF_ANALYSIS_PATH = Path(
    "docs/experiments/exectv2/seizure_frequency/"
    "exectv2_sf_canonical_metric_row_analysis_2026-06-29.md"
)
DX_LEGACY_ANALYSIS_PATH = Path(
    "docs/experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md"
)
BLIND_REVIEW_PATH = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_gold_quality_adjudication_blind_replication_2026-07-01.md"
)
GUIDELINES_PATH = Path("docs/research/exectv2/annotation_guidelines_v9_extracted.md")
DX_RESOLUTION_LEDGER_PATH = Path(
    "experiments/exectv2_diagnosis_resolution_ledger_dev140_20260714.jsonl"
)
DX_SENSITIVITY_PATH = Path("experiments/exectv2_diagnosis_sensitivity_dev140_20260714.json")
DX_REVIEW_OVERLAY_PATH = Path("experiments/exectv2_diagnosis_review_completed_dev140_20260714.json")
DX_COMPONENT_PATH = Path("experiments/exectv2_diagnosis_component_comparison_dev140_20260714.json")

SOURCE_PATHS = (
    *LEDGER_PATHS.values(),
    GOLD_ISSUES_PATH,
    SF_ANALYSIS_PATH,
    DX_LEGACY_ANALYSIS_PATH,
    BLIND_REVIEW_PATH,
    GUIDELINES_PATH,
    DX_RESOLUTION_LEDGER_PATH,
    DX_SENSITIVITY_PATH,
    DX_REVIEW_OVERLAY_PATH,
    DX_COMPONENT_PATH,
)
NARRATIVE_CASE_PATHS = (SF_ANALYSIS_PATH, DX_LEGACY_ANALYSIS_PATH, BLIND_REVIEW_PATH)

LEGACY_MECHANISM_CLASSES = {
    "gold_under_annotation": "probable_annotation_defect",
    "gold_orthographic_typo": "mechanical_annotation_defect",
    "gold_multiplicity_consolidation": "multiplicity_or_representation_convention",
    "iaa_ambiguity": "annotation_ambiguity",
    "scorer_mechanics_artifact": "scoring_artifact",
    "genuine_model_error": "model_error_control",
}
DX_MECHANISM_CLASSES = {
    "clinical_granularity": "representation_convention",
    "reviewed_equivalence": "representation_convention",
    "same_cui_representation": "scoring_representation",
    "likely_gold_omission": "probable_annotation_defect",
    "manual_representation": "representation_or_convention",
    "unresolved_clinical_ambiguity": "annotation_ambiguity",
    "manual_extraction_error": "model_error_control",
    "missed_named_diagnosis": "model_error_control",
    "non_target_diagnosis": "model_error_control",
    "unsupported_spurious_diagnosis": "model_error_control",
    "context_scope_error": "model_error_control",
}
CONSERVATIVE_DX_MECHANISMS = {
    "clinical_granularity",
    "reviewed_equivalence",
    "same_cui_representation",
}
WIDEST_ONLY_DX_MECHANISMS = {"likely_gold_omission", "manual_representation"}
TEXT_SUFFIXES = {".json", ".jsonl", ".md", ".py", ".txt", ".toml", ".yaml", ".yml"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    payload = build_synthesis(root)
    output = args.output if args.output.is_absolute() else root / args.output
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "pass",
                "entries": payload["summary"]["taxonomy_entry_count"],
                "cited_letters": payload["summary"]["cited_letter_count"],
                "unmapped_cited_letters": payload["summary"]["unmapped_cited_letter_count"],
                "output": output.relative_to(root).as_posix(),
            },
            sort_keys=True,
        )
    )


def build_synthesis(root: Path) -> dict[str, Any]:
    """Return the complete annotation-evidence synthesis payload."""

    protocol = root / PROTOCOL_PATH
    if not protocol.is_file():
        raise ValueError(f"predeclared protocol is missing: {PROTOCOL_PATH.as_posix()}")

    manifest = _read_json(root / MANIFEST_PATH)
    expected_fingerprints = _manifest_fingerprints(manifest)
    sources = [_source_record(root, path, expected_fingerprints) for path in SOURCE_PATHS]

    entries: list[dict[str, Any]] = []
    for family, path in LEDGER_PATHS.items():
        entries.extend(_legacy_ledger_entries(root, family, path))
    entries.extend(_gold_issue_entries(root))
    entries.extend(_current_diagnosis_entries(root))

    cited_letters = _cited_letter_coverage(root, entries)
    entries.extend(_citation_only_entries(cited_letters))
    entries.sort(key=lambda row: row["entry_id"])
    _validate_entries(entries)

    statements = _evidence_statements(root, entries)
    summary = _summary(entries, cited_letters)
    return {
        "schema_version": "exectv2_annotation_evidence_synthesis_v1",
        "generated_on": GENERATED_ON,
        "protocol": PROTOCOL_PATH.as_posix(),
        "source_commit": _source_commit(root),
        "dirty_tree_at_generation": _dirty_tree(root),
        "dataset": "ExECTv2 2025 broad epilepsy phenotyping corpus",
        "split": "dev140 retained permitted-development records",
        "row_policy": "dev140_rows_permitted_test60_forbidden",
        "call_mode": "no_model_calls_retained_artifact_synthesis",
        "gold_changed": False,
        "scorer_changed": False,
        "sources": sources,
        "taxonomy_entries": entries,
        "evidence_statements": statements,
        "citation_coverage": cited_letters,
        "summary": summary,
        "limitations": [
            (
                "The historical Diagnosis narrative reports 209 concept disagreements, while "
                "the selected generated Diagnosis family ledger contains 199 rows. All 57 "
                "letter IDs explicitly cited across the three narrative reports are mapped, "
                "but ten historical Diagnosis concept rows cannot be reconstructed from the "
                "retained files and remain aggregate-only evidence."
            ),
            (
                "The 584 taxonomy entries overlap across historical family ledgers, direct "
                "defect records, and the current Diagnosis review. They are evidence records, "
                "not unique letters and not a prevalence denominator."
            ),
            (
                "The blind re-review was performed by LLM sub-agents on small samples; its "
                "narrative report is retained, but it is not independent clinical review."
            ),
        ],
        "claim_boundary": (
            "This artifact combines internal project review, pattern-assisted review, "
            "mechanically identified defects, scorer effects, and blind LLM re-review on "
            "permitted development records. It does not correct gold, replace an original "
            "score, inspect test60, establish prevalence outside the retained records, or "
            "provide independent clinical validation. Clinical-validity claims require "
            "independent clinical review."
        ),
    }


def _legacy_ledger_entries(root: Path, family: str, path: Path) -> list[dict[str, Any]]:
    entries = []
    for row in _read_jsonl(root / path):
        mechanism = str(row["mechanism"])
        verdict = str(row["verdict"])
        if mechanism not in LEGACY_MECHANISM_CLASSES:
            raise ValueError(f"unmapped legacy mechanism: {mechanism}")
        if verdict == "gold_right":
            sensitivity = "not_forgiven_model_error_control"
            handling = "Keep the original gold and score; treat as a method error candidate."
        else:
            sensitivity = "historical_internal_adjustment_only"
            handling = (
                "Keep the original gold and score; use only in a separately labelled "
                "historical sensitivity or annotation analysis."
            )
        history_status = (
            "superseded_for_current_diagnosis_magnitude"
            if family == "Diagnosis"
            else "retained_historical_internal_evidence"
        )
        entries.append(
            {
                "entry_id": f"legacy-ledger:{row['row_id']}",
                "record_type": "retained_family_ledger_case",
                "source_path": path.as_posix(),
                "source_row_id": row["row_id"],
                "family": family,
                "letter_id": row["letter_id"],
                "review_key": None,
                "issue_class": LEGACY_MECHANISM_CLASSES[mechanism],
                "mechanism": mechanism,
                "verdict": verdict,
                "disagreement_direction": row["disagreement_type"],
                "original_score_treatment": (
                    "Counts as an original-scorer disagreement; the source gold and scorer "
                    "remain unchanged."
                ),
                "handling": handling,
                "sensitivity_treatment": sensitivity,
                "review_method": row["provenance"]["adjudicated_by"],
                "review_status": "internal_project_adjudication",
                "structured_clinical_fields_status": "not_available_in_legacy_ledger",
                "clinical_review_state": "not_independently_clinically_reviewed",
                "history_status": history_status,
                "source_statement": row["provenance"]["reason"],
            }
        )
    return entries


def _gold_issue_entries(root: Path) -> list[dict[str, Any]]:
    entries = []
    for row in _read_jsonl(root / GOLD_ISSUES_PATH):
        status = str(row["resolution_status"])
        issue_class = (
            "closed_vocab_format_defect" if status == "fixed" else "mechanical_annotation_defect"
        )
        entries.append(
            {
                "entry_id": (
                    f"gold-issue:{row['letter_id']}:{row['entity']}:"
                    f"{str(row['field']).replace(' ', '_')}"
                ),
                "record_type": "direct_gold_issue",
                "source_path": GOLD_ISSUES_PATH.as_posix(),
                "source_row_id": f"{row['letter_id']}|{row['entity']}|{row['field']}",
                "family": row["entity"],
                "letter_id": row["letter_id"],
                "review_key": None,
                "issue_class": issue_class,
                "mechanism": "field_value_conflicts_with_span_schema_or_companion_fields",
                "verdict": "mechanically_confirmed_issue",
                "disagreement_direction": None,
                "original_score_treatment": row["notes"],
                "handling": (
                    "Frozen gold unchanged; canonical score normalization handles the format quirk."
                    if status == "fixed"
                    else "Frozen gold unchanged; retain as an open score-bearing defect."
                ),
                "sensitivity_treatment": "not_folded_into_any_headline_score",
                "review_method": "mechanical corpus and field-consistency audit",
                "review_status": status,
                "structured_clinical_fields_status": "mechanical_field_conflict_recorded",
                "clinical_review_state": (
                    "mechanical inconsistency does not validate broader clinical equivalence"
                ),
                "history_status": "current_direct_defect_record",
                "source_statement": row["conflicting_evidence"],
            }
        )
    return entries


def _current_diagnosis_entries(root: Path) -> list[dict[str, Any]]:
    rows = _read_jsonl(root / DX_RESOLUTION_LEDGER_PATH)
    overlay = _read_json(root / DX_REVIEW_OVERLAY_PATH)
    decisions = overlay["decisions"]
    if len(rows) != 246 or len(decisions) != 246:
        raise ValueError("completed Diagnosis review must contain 246 rows and decisions")

    entries = []
    for row in rows:
        decision = row["review_decision"]
        review_key = str(row["review_key"])
        if review_key not in decisions:
            raise ValueError(f"Diagnosis review key missing from completed overlay: {review_key}")
        if decisions[review_key]["triage"] != decision["triage"]:
            raise ValueError(f"Diagnosis triage drift for {review_key}")
        mechanism = str(decision["mechanism"])
        if mechanism not in DX_MECHANISM_CLASSES:
            raise ValueError(f"unmapped Diagnosis mechanism: {mechanism}")
        if mechanism in CONSERVATIVE_DX_MECHANISMS:
            sensitivity = "forgiven_in_conservative_and_reviewed_interpretation_views"
        elif mechanism in WIDEST_ONLY_DX_MECHANISMS:
            sensitivity = "forgiven_only_in_widest_reviewed_interpretation_view"
        else:
            sensitivity = "not_forgiven_in_diagnosis_sensitivity_views"
        provenance = str(decision["provenance"])
        review_status = (
            "pattern_assisted_project_hypothesis"
            if provenance == "pattern_assisted"
            else "manual_project_triage"
        )
        if decision["triage"] == "uncertain":
            review_status = "unresolved_project_triage"
        entries.append(
            {
                "entry_id": f"diagnosis-review:{review_key}",
                "record_type": "completed_diagnosis_review_case",
                "source_path": DX_RESOLUTION_LEDGER_PATH.as_posix(),
                "source_row_id": review_key,
                "family": "Diagnosis",
                "letter_id": row["letter_id"],
                "review_key": review_key,
                "issue_class": DX_MECHANISM_CLASSES[mechanism],
                "mechanism": mechanism,
                "verdict": decision["triage"],
                "disagreement_direction": row["direction"],
                "original_score_treatment": (
                    "The row remains a false-negative or false-positive contribution under "
                    "the fixed Diagnosis concept scorer."
                ),
                "handling": (
                    "Gold and the fixed scorer remain unchanged; report only in the named "
                    "sensitivity view or as a development mechanism record."
                    if decision["triage"] == "representation"
                    else "Gold and the fixed scorer remain unchanged; retain as an extraction "
                    "error or unresolved control."
                ),
                "sensitivity_treatment": sensitivity,
                "review_method": provenance,
                "review_status": review_status,
                "structured_clinical_fields_status": row["adjudication"]["status"],
                "clinical_review_state": "not_independently_clinically_reviewed",
                "history_status": "current_2026_07_14_diagnosis_review",
                "source_statement": (
                    decision["note"]
                    or "Manual project triage; inspect the source ledger for note and "
                    "method records."
                ),
            }
        )
    return entries


def _evidence_statements(root: Path, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sf_text = _normalized_text(root / SF_ANALYSIS_PATH)
    dx_text = _normalized_text(root / DX_LEGACY_ANALYSIS_PATH)
    blind_text = _normalized_text(root / BLIND_REVIEW_PATH)
    guideline_text = _normalized_text(root / GUIDELINES_PATH)
    sensitivity = _read_json(root / DX_SENSITIVITY_PATH)
    component = _read_json(root / DX_COMPONENT_PATH)

    _require_text(sf_text, "53 metric disagreements")
    _require_text(sf_text, "22 (42%) to annotation mismatch or redundant annotation")
    _require_text(dx_text, "92 missed + 117 spurious = 209 individual concept-level disagreements")
    _require_text(blind_text, "Pooled | 40 | 60.0% | 0.397 | 0.362 | 0.331")
    _require_text(
        guideline_text,
        "A phrase may be assigned to more than one concept, depending on the context provided.",
    )
    _require_text(
        guideline_text, "If multiple time periods are used, as in Example 5; annotate both."
    )
    _require_text(guideline_text, "well controlled = infrequent")

    triage = Counter(
        row["verdict"] for row in entries if row["record_type"] == "completed_diagnosis_review_case"
    )
    review_status = Counter(
        row["review_status"]
        for row in entries
        if row["record_type"] == "completed_diagnosis_review_case"
    )
    review_method = Counter(
        row["review_method"]
        for row in entries
        if row["record_type"] == "completed_diagnosis_review_case"
    )
    views = sensitivity["views"]
    baselines = component["baselines"]
    return [
        {
            "statement_id": "guideline:multi_concept_and_context",
            "subject": "annotation_convention",
            "source_path": GUIDELINES_PATH.as_posix(),
            "finding": (
                "The source guideline allows one phrase to carry more than one concept when "
                "contexts differ; multiplicity can therefore be a prescribed representation, "
                "not automatically duplicate gold."
            ),
            "handling": (
                "Keep multiplicity visible and test a separate multiplicity-insensitive view."
            ),
            "claim_strength": "primary annotation guideline",
        },
        {
            "statement_id": "guideline:sf_time_and_word_conventions",
            "subject": "annotation_convention",
            "source_path": GUIDELINES_PATH.as_posix(),
            "finding": (
                "The guideline instructs annotators to retain multiple time periods and maps "
                "'well controlled' to infrequent; these conventions can differ from a model's "
                "single consolidated state."
            ),
            "handling": "Treat convention differences separately from mechanical gold defects.",
            "claim_strength": "primary annotation guideline",
        },
        {
            "statement_id": "legacy:seizure_frequency_internal_review",
            "subject": "ambiguity_multiplicity_and_scoring",
            "source_path": SF_ANALYSIS_PATH.as_posix(),
            "finding": (
                "The internal review assigned 15/53 disagreements to model error, 22/53 to "
                "annotation mismatch or redundancy, and 16/53 to ambiguity or temporal "
                "convention. Exact per-letter agreement was 62.1%; the internally defensible "
                "view was 89.3%."
            ),
            "handling": (
                "Keep state_profile primary and the internally defensible percentage as a "
                "separate historical sensitivity result."
            ),
            "claim_strength": "historical internal dev140 adjudication; not clinical validation",
        },
        {
            "statement_id": "legacy:diagnosis_internal_review",
            "subject": "multiplicity_and_representation",
            "source_path": DX_LEGACY_ANALYSIS_PATH.as_posix(),
            "finding": (
                "The historical review classified 31/209 disagreements as model errors, "
                "167/209 as model-defensible annotation mismatch, and 11/209 as ambiguous."
            ),
            "handling": (
                "Retain as historical mechanism evidence only. Its 0.6617-to-0.9501 adjustment "
                "belongs to a different run and scorer and is superseded for current magnitude."
            ),
            "claim_strength": "historical internal dev140 adjudication",
        },
        {
            "statement_id": "review:blind_rereview_limit",
            "subject": "review_reproducibility",
            "source_path": BLIND_REVIEW_PATH.as_posix(),
            "finding": (
                "A 40-case blind LLM re-review had 60.0% raw agreement and pooled unweighted "
                "kappa 0.397. The aggregate reweighted Diagnosis estimate shifted more than "
                "Seizure Frequency, so individual clinical-equivalence judgments remain soft."
            ),
            "handling": (
                "Report the negative reproducibility result and do not treat the re-review "
                "as external validation."
            ),
            "claim_strength": "internal LLM blind re-review with small samples",
        },
        {
            "statement_id": "current:diagnosis_review",
            "subject": "current_review_status",
            "source_path": DX_RESOLUTION_LEDGER_PATH.as_posix(),
            "finding": (
                f"The current 246-row review contains {triage['representation']} representation "
                f"decisions, {triage['extraction_error']} extraction errors, and "
                f"{triage['uncertain']} uncertain row. Review provenance is "
                f"{review_method['pattern_assisted']} pattern-assisted and "
                f"{review_method['manual']} manual; "
                f"{review_status['unresolved_project_triage']} manual row remains unresolved."
            ),
            "handling": (
                "Gold and the fixed scorer remain unchanged; pattern-assisted rows stay "
                "project hypotheses."
            ),
            "claim_strength": (
                "completed project triage on dev140; not independent clinical adjudication"
            ),
        },
        {
            "statement_id": "current:diagnosis_sensitivity",
            "subject": "sensitivity_scoring",
            "source_path": DX_SENSITIVITY_PATH.as_posix(),
            "finding": {
                method: {
                    "fixed_f1": baselines[method]["fixed_primary"]["f1"],
                    "conservative_f1": views["multiplicity_and_clinical_granularity"]["methods"][
                        method
                    ]["scores"]["f1"],
                    "widest_reviewed_f1": views["reviewed_interpretation"]["methods"][method][
                        "scores"
                    ]["f1"],
                }
                for method in ("rules_only", "llm_only", "llm_with_rules")
            },
            "handling": (
                "Treat both sensitivity views as diagnostic reinterpretations of fixed outputs, "
                "not replacement scores or corrected clinical accuracy."
            ),
            "claim_strength": "reproducible dev140 arithmetic with unchanged gold and scorer",
        },
        {
            "statement_id": "current:diagnosis_candidate_handling",
            "subject": "handling",
            "source_path": DX_COMPONENT_PATH.as_posix(),
            "finding": (
                "Rules and hybrid fixes remain development candidates; the LLM-only prompt "
                "candidate was rejected after regression. No candidate was promoted."
            ),
            "handling": "Do not mix candidate score changes with sensitivity reinterpretation.",
            "claim_strength": "dev140 component result",
        },
        {
            "statement_id": "boundary:independent_clinical_review",
            "subject": "clinical_validity",
            "source_path": PROTOCOL_PATH.as_posix(),
            "finding": (
                "Mechanical defects, annotation conventions, internal judgments, score effects, "
                "and sensitivity results are now traceable, but no source supplies independent "
                "clinical validation."
            ),
            "handling": (
                "Require independent clinical review before making clinical-validity claims."
            ),
            "claim_strength": "explicit unresolved evidence boundary",
        },
    ]


def _cited_letter_coverage(root: Path, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mapped = {str(row["letter_id"]) for row in entries if row.get("letter_id")}
    coverage = []
    for path in NARRATIVE_CASE_PATHS:
        text = (root / path).read_text(encoding="utf-8")
        cited = sorted(set(re.findall(r"\bEA\d{4}\b", text)))
        coverage.append(
            {
                "source_path": path.as_posix(),
                "cited_letter_ids": cited,
                "mapped_letter_ids": sorted(set(cited) & mapped),
                "unmapped_letter_ids": sorted(set(cited) - mapped),
            }
        )
    return coverage


def _citation_only_entries(coverage: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entries = []
    for source in coverage:
        for letter_id in source["unmapped_letter_ids"]:
            entries.append(
                {
                    "entry_id": f"narrative-citation:{source['source_path']}:{letter_id}",
                    "record_type": "narrative_case_reference",
                    "source_path": source["source_path"],
                    "source_row_id": letter_id,
                    "family": "NarrativeSource",
                    "letter_id": letter_id,
                    "review_key": None,
                    "issue_class": "narrative_case_not_present_in_retained_row_ledger",
                    "mechanism": "not_inferred",
                    "verdict": "source_only_reference",
                    "disagreement_direction": None,
                    "original_score_treatment": (
                        "See the named source; no score treatment is inferred."
                    ),
                    "handling": (
                        "Retain as an explicit source-only citation rather than inventing "
                        "row fields."
                    ),
                    "sensitivity_treatment": "not_inferred",
                    "review_method": "source narrative",
                    "review_status": "source_only_reference",
                    "structured_clinical_fields_status": "not_available",
                    "clinical_review_state": "not_independently_clinically_reviewed",
                    "history_status": "citation_coverage_record",
                    "source_statement": (
                        "Letter identifier is explicitly cited in the source narrative."
                    ),
                }
            )
    return entries


def _summary(
    entries: list[dict[str, Any]], citation_coverage: list[dict[str, Any]]
) -> dict[str, Any]:
    by_type = Counter(str(row["record_type"]) for row in entries)
    by_family = Counter(str(row["family"]) for row in entries)
    by_issue = Counter(str(row["issue_class"]) for row in entries)
    current_dx = [row for row in entries if row["record_type"] == "completed_diagnosis_review_case"]
    legacy_dx_count = sum(
        1
        for row in entries
        if row["record_type"] == "retained_family_ledger_case"
        and row["family"] == "Diagnosis"
    )
    cited = {item for source in citation_coverage for item in source["cited_letter_ids"]}
    unmapped = {item for source in citation_coverage for item in source["unmapped_letter_ids"]}
    return {
        "taxonomy_entry_count": len(entries),
        "entries_by_record_type": dict(sorted(by_type.items())),
        "entries_by_family": dict(sorted(by_family.items())),
        "entries_by_issue_class": dict(sorted(by_issue.items())),
        "legacy_ledger_row_count": sum(
            1 for row in entries if row["record_type"] == "retained_family_ledger_case"
        ),
        "legacy_diagnosis_reported_disagreement_count": 209,
        "legacy_diagnosis_ledger_row_count": legacy_dx_count,
        "legacy_diagnosis_unmaterialized_row_count": 209 - legacy_dx_count,
        "current_diagnosis_review_row_count": len(current_dx),
        "current_diagnosis_triage": dict(
            sorted(Counter(str(row["verdict"]) for row in current_dx).items())
        ),
        "current_diagnosis_review_method": dict(
            sorted(Counter(str(row["review_method"]) for row in current_dx).items())
        ),
        "current_diagnosis_review_status": dict(
            sorted(Counter(str(row["review_status"]) for row in current_dx).items())
        ),
        "current_diagnosis_sensitivity_treatment": dict(
            sorted(Counter(str(row["sensitivity_treatment"]) for row in current_dx).items())
        ),
        "direct_gold_issue_status": dict(
            sorted(
                Counter(
                    str(row["review_status"])
                    for row in entries
                    if row["record_type"] == "direct_gold_issue"
                ).items()
            )
        ),
        "cited_letter_count": len(cited),
        "unmapped_cited_letter_count": len(unmapped),
        "citation_only_entry_count": by_type.get("narrative_case_reference", 0),
    }


def _validate_entries(entries: list[dict[str, Any]]) -> None:
    ids = [str(row["entry_id"]) for row in entries]
    if len(ids) != len(set(ids)):
        raise ValueError("taxonomy entry IDs must be unique")
    required = {
        "entry_id",
        "record_type",
        "source_path",
        "source_row_id",
        "family",
        "letter_id",
        "issue_class",
        "mechanism",
        "original_score_treatment",
        "handling",
        "sensitivity_treatment",
        "review_method",
        "review_status",
        "clinical_review_state",
        "history_status",
        "source_statement",
    }
    for row in entries:
        missing = required - row.keys()
        if missing:
            raise ValueError(f"taxonomy entry {row.get('entry_id')} is missing {sorted(missing)}")


def _source_record(
    root: Path,
    path: Path,
    expected_fingerprints: dict[str, tuple[str, int]],
) -> dict[str, Any]:
    relative = path.as_posix()
    expected = expected_fingerprints.get(relative)
    if expected is None:
        raise ValueError(f"source is not retained in the manifest: {relative}")
    observed = _fingerprint(root / path)
    if observed != expected:
        raise ValueError(f"retained source hash or size drift: {relative}")
    return {
        "path": relative,
        "recorded_sha256": expected[0],
        "observed_sha256": observed[0],
        "recorded_bytes": expected[1],
        "observed_bytes": observed[1],
        "hash_status": "matched_manifest",
    }


def _manifest_fingerprints(manifest: dict[str, Any]) -> dict[str, tuple[str, int]]:
    result: dict[str, tuple[str, int]] = {}
    for section in ("reference_cells", "evidence_packages"):
        for record in manifest[section]:
            for artifact in record["artifacts"]:
                result[str(artifact["path"])] = (
                    str(artifact["sha256"]),
                    int(artifact["bytes"]),
                )
    return result


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"expected JSON object row: {path}")
            rows.append(value)
    return rows


def _fingerprint(path: Path) -> tuple[str, int]:
    content = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        content = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest(), len(content)


def _normalized_text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _require_text(text: str, expected: str) -> None:
    normalized = " ".join(expected.split())
    if normalized not in text:
        raise ValueError(f"expected retained statement is missing: {normalized}")


def _source_commit(root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _dirty_tree(root: Path) -> bool:
    return bool(
        subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )


if __name__ == "__main__":
    main()
