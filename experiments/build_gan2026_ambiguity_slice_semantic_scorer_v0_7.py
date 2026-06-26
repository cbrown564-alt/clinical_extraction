"""Semantic / over-specificity scorer for the ambiguity slice.

Instrumentation step 3.2 of the unknown-frequency agentic pathways doc. Purist
scoring is partially blind on exactly the axis the ambiguity work targets
(Insight 5): `multiple per month`, `multiple per year`, `unknown`, and
`no seizure frequency reference` all normalize to `monthly=1000.0` /
`seizure_freq_unknown`. So an over-specific concrete-frequency output can score
Purist-*correct* on a gold-`unknown` row purely by re-bucketing, and a future
live run's "gains" could be illusory.

This scorer re-reads the saved live ambiguity slice and scores each row on the
*clinical decision* (unknown vs seizure-free vs concrete frequency), not just the
Purist bucket. It flags two failure modes Purist cannot see:

1. Over-specific re-bucketing: gold is an unknown-bucket decision, the prediction
   is Purist-correct, but the predicted label asserts a concrete frequency that
   merely lands in the unknown bucket. Purist credits it; clinically it is wrong.
2. Class/label incoherence (Insight 4): the emitted `ambiguity_classification`
   disagrees with the rendered `final_label` (e.g. `explicit_count_window` on a
   row rendered `unknown`). When this happens the contract is being satisfied by
   the gate and the label logic, not by a trustworthy class signal, so the class
   cannot yet be used as a selector feature.

Validation-only. Reads the saved live slice; makes no model calls, reads no
locked test rows, and changes no scorer policy. The semantic verdict here is a
*diagnostic overlay* on Purist, not a replacement for the frozen scorer.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.core.registry import (
    RunRegistryEntry,
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    write_run_registry_markdown,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"

SLICE_JSONL = (
    EXPERIMENTS
    / "gan2026_fresh_evidence_reasoner_residual_slice_live_gpt41_v0_7_safety_v0_9_"
    "2026-06-15.jsonl"
)

RUN_ID = "gan2026_ambiguity_slice_semantic_scorer_v0_7_2026-06-15"
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"

# Clinical decision types. These are coarser than the Gan label space on
# purpose: the question this scorer answers is "did the model make the right
# *kind* of call", not "did it land the exact rate". A label's decision kind is
# taken from its Purist bucket, not its surface form: `1 per multiple month`,
# `multiple per month`, and `unknown` all sit in the unknown bucket and are all
# the same clinical call (non-quantified), so they share DECISION_UNKNOWN.
DECISION_UNKNOWN = "unknown_decision"
DECISION_SEIZURE_FREE = "seizure_free_decision"
DECISION_FREQUENCY = "frequency_decision"
DECISION_UNPARSEABLE = "unparseable"

# Surface specificity within a decision kind. Over-specification is predicting a
# *more* specific surface than gold while staying in the unknown bucket (the
# Insight-5 illusion: `multiple per month` for a gold `unknown`). Predicting a
# *less* specific surface (plain `unknown` for gold `1 per multiple month`) is
# the safe call the supervisor policy prefers, not an error.
SPECIFICITY_BARE_UNKNOWN = 0  # "unknown" / "no seizure frequency reference"
SPECIFICITY_QUANTIFIED_UNKNOWN = 1  # unknown-bucket but quantified surface
SPECIFICITY_CONCRETE = 2  # concrete rate or seizure-free duration

# Which ambiguity classes are coherent with which clinical decision. A class is
# coherent if the rendered decision is in its allowed set; not_applicable and a
# missing class are never counted as incoherent.
CLASS_COHERENT_DECISIONS = {
    "explicit_count_window": {DECISION_FREQUENCY},
    "explicit_seizure_free_duration": {DECISION_SEIZURE_FREE},
    "last_event_only_unknown": {DECISION_UNKNOWN},
    "unknown_count_or_window": {DECISION_UNKNOWN},
    "no_seizure_frequency_reference": {DECISION_UNKNOWN},
    "cluster_axis_incomplete": {DECISION_UNKNOWN},
    "cluster_axis_complete": {DECISION_FREQUENCY},
}


def main() -> None:
    rows = _load_slice_rows(SLICE_JSONL)
    scored = [_score_row(row) for row in rows]
    summary = _summarize(scored)
    payload = {
        "run_id": RUN_ID,
        "date": "2026-06-15",
        "purpose": (
            "Validation-only semantic / over-specificity overlay on the live "
            "ambiguity slice. Scores each row on the clinical decision (unknown "
            "vs seizure-free vs frequency), flags over-specific re-bucketing that "
            "Purist credits (Insight 5), and flags class/label incoherence "
            "(Insight 4)."
        ),
        "source_artifact": str(SLICE_JSONL),
        "summary": summary,
        "rows": sorted(scored, key=lambda r: r["source_row_index"]),
    }
    JSON_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(_markdown(payload), encoding="utf-8")
    _register(summary)
    print(json.dumps(summary["headline"], indent=2, sort_keys=True))


def _load_slice_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _purist_bucket(label: str | None) -> str | None:
    if not label:
        return None
    try:
        record = label_to_frequency_record(str(label))
    except Exception:
        return None
    return str(map_purist(record.monthly_frequency))


def _clinical_decision(label: str | None) -> str:
    """Decision kind taken from the Purist bucket, not the surface form."""
    if not label:
        return DECISION_UNPARSEABLE
    lowered = str(label).strip().lower()
    if lowered.startswith("seizure free"):
        return DECISION_SEIZURE_FREE
    bucket = _purist_bucket(label)
    if bucket is None:
        return DECISION_UNPARSEABLE
    if bucket == "seizure_freq_unknown":
        return DECISION_UNKNOWN
    if bucket == "currently_no_seizure":
        return DECISION_SEIZURE_FREE
    return DECISION_FREQUENCY


def _specificity_level(label: str | None) -> int | None:
    """Surface specificity used only to detect over-specification within the
    unknown bucket. None when the label does not parse."""
    if not label:
        return None
    lowered = str(label).strip().lower()
    if lowered in {"unknown", "no seizure frequency reference"}:
        return SPECIFICITY_BARE_UNKNOWN
    bucket = _purist_bucket(label)
    if bucket is None:
        return None
    if bucket == "seizure_freq_unknown":
        return SPECIFICITY_QUANTIFIED_UNKNOWN
    return SPECIFICITY_CONCRETE


def _score_row(row: dict[str, Any]) -> dict[str, Any]:
    comparison = row["score_layers"]["final"]["comparison"]
    decision_record = row.get("fresh_evidence_decision_record") or {}
    predicted_label = comparison.get("final_label")
    gold_label = row["reference"]["gold_label"]
    purist_correct = bool(comparison.get("purist_correct"))

    predicted_decision = _clinical_decision(predicted_label)
    gold_decision = _clinical_decision(gold_label)

    # Over-specific re-bucketing: Purist says correct (both in the unknown
    # bucket), gold's clinical call is unknown, but the prediction asserts a
    # *more specific* surface than gold (e.g. `multiple per month` for a gold
    # `unknown`). Predicting a less specific surface than gold is the safe call
    # the supervisor policy prefers, not an error, so the comparison is strict.
    gold_specificity = _specificity_level(gold_label)
    predicted_specificity = _specificity_level(predicted_label)
    over_specific_rebucket = bool(
        purist_correct
        and gold_decision == DECISION_UNKNOWN
        and gold_specificity is not None
        and predicted_specificity is not None
        and predicted_specificity > gold_specificity
    )

    # Semantic-correct: Purist-correct AND the clinical decision kind agrees.
    # Seizure-free and unknown both sit in non-frequency territory but are
    # clinically distinct, so they are only "semantically correct" when the kind
    # matches gold's kind.
    semantic_correct = bool(
        purist_correct
        and not over_specific_rebucket
        and predicted_decision == gold_decision
    )

    ambiguity_class = decision_record.get("ambiguity_classification")
    coherent_decisions = CLASS_COHERENT_DECISIONS.get(str(ambiguity_class))
    class_label_incoherent = bool(
        coherent_decisions is not None
        and predicted_decision not in coherent_decisions
    )

    return {
        "source_row_index": row["source_row_index"],
        "gold_label": gold_label,
        "predicted_label": predicted_label,
        "gold_decision": gold_decision,
        "predicted_decision": predicted_decision,
        "purist_correct": purist_correct,
        "semantic_correct": semantic_correct,
        "over_specific_rebucket": over_specific_rebucket,
        "ambiguity_classification": ambiguity_class,
        "class_label_incoherent": class_label_incoherent,
    }


def _summarize(scored: list[dict[str, Any]]) -> dict[str, Any]:
    purist = sum(1 for row in scored if row["purist_correct"])
    semantic = sum(1 for row in scored if row["semantic_correct"])
    over_specific = [
        row["source_row_index"] for row in scored if row["over_specific_rebucket"]
    ]
    purist_only = [
        row["source_row_index"]
        for row in scored
        if row["purist_correct"] and not row["semantic_correct"]
    ]
    incoherent = [
        row["source_row_index"] for row in scored if row["class_label_incoherent"]
    ]
    decision_confusion = Counter(
        (row["gold_decision"], row["predicted_decision"]) for row in scored
    )
    return {
        "headline": {
            "rows": len(scored),
            "purist_correct": purist,
            "semantic_correct": semantic,
            "purist_minus_semantic": purist - semantic,
            "over_specific_rebucket_rows": over_specific,
            "class_label_incoherent_rows": incoherent,
        },
        "purist_correct_but_not_semantic_rows": sorted(purist_only),
        "decision_confusion": {
            f"{gold}->{pred}": count
            for (gold, pred), count in sorted(decision_confusion.items())
        },
    }


def _yn(value: bool) -> str:
    return "yes" if value else "no"


def _markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    head = summary["headline"]
    lines = [
        "# Gan 2026 Ambiguity Slice Semantic / Over-Specificity Scorer",
        "",
        "Date: 2026-06-15",
        "",
        "Validation-only instrumentation (step 3.2 of the unknown-frequency "
        "agentic pathways doc). It re-reads the saved live ambiguity slice and "
        "scores each row on the *clinical decision* alongside Purist, to catch "
        "the two failure modes Purist is blind to. No model calls, no locked "
        "test rows, no scorer change — this is a diagnostic overlay, not a "
        "replacement for the frozen scorer.",
        "",
        "## Why Purist is not enough here",
        "",
        "`multiple per month`, `multiple per year`, `unknown`, and "
        "`no seizure frequency reference` all normalize to `monthly=1000.0` / "
        "`seizure_freq_unknown`. So on a gold-`unknown` row an over-specific "
        "concrete frequency scores Purist-correct purely by re-bucketing "
        "(Insight 5). Optimizing the ambiguity slice on Purist alone would credit "
        "re-bucketing as reasoning.",
        "",
        "## Headline",
        "",
        f"- Rows scored: `{head['rows']}`",
        f"- Purist-correct: `{head['purist_correct']}/{head['rows']}`",
        f"- Semantic-correct (clinical decision agrees, no re-bucketing credit): "
        f"`{head['semantic_correct']}/{head['rows']}`",
        f"- Purist credit not backed by semantics: "
        f"`{head['purist_minus_semantic']}`",
        f"- Over-specific re-bucketing rows (Purist-correct, clinically wrong): "
        f"`{head['over_specific_rebucket_rows'] or 'none'}`",
        f"- Class/label incoherent rows (Insight 4): "
        f"`{head['class_label_incoherent_rows'] or 'none'}`",
        "",
        "## Per-row",
        "",
        "| Row | Gold | Pred | Gold decision | Pred decision | Purist | Semantic | Over-spec | Class | Class incoherent |",
        "| ---: | --- | --- | --- | --- | :---: | :---: | :---: | --- | :---: |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| {row['source_row_index']} "
            f"| `{row['gold_label']}` "
            f"| `{row['predicted_label']}` "
            f"| {row['gold_decision']} "
            f"| {row['predicted_decision']} "
            f"| {_yn(row['purist_correct'])} "
            f"| {_yn(row['semantic_correct'])} "
            f"| {_yn(row['over_specific_rebucket'])} "
            f"| `{row['ambiguity_classification']}` "
            f"| {_yn(row['class_label_incoherent'])} |"
        )
    lines.extend(
        [
            "",
            "## Gold -> predicted clinical decision confusion",
            "",
            "| Gold decision -> predicted decision | Rows |",
            "| --- | ---: |",
        ]
    )
    for key, count in summary["decision_confusion"].items():
        lines.append(f"| {key} | {count} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            _interpretation(summary),
            "",
        ]
    )
    return "\n".join(lines)


def _interpretation(summary: dict[str, Any]) -> str:
    head = summary["headline"]
    gap = head["purist_minus_semantic"]
    over_specific = head["over_specific_rebucket_rows"]
    incoherent = head["class_label_incoherent_rows"]
    parts = []
    if over_specific:
        parts.append(
            f"Purist over-credits {len(over_specific)} row(s) "
            f"({over_specific}): the prediction lands in the unknown bucket via an "
            "over-specific concrete frequency rather than a genuine unknown call. "
            "Any future live gain on these rows would be re-bucketing, not "
            "reasoning, and must not be counted as a fix."
        )
    else:
        parts.append(
            "No over-specific re-bucketing fires on this slice: the Purist-correct "
            "rows are genuine unknown / seizure-free / frequency calls, so the "
            f"Purist-semantic gap is driven by clinical-kind mismatches "
            f"({gap} row(s)) rather than the Insight-5 illusion. The scorer is in "
            "place for the live run, where regeneration is far more likely to "
            "trip it."
        )
    if incoherent:
        parts.append(
            f"Class/label incoherence (Insight 4) fires on {len(incoherent)} "
            f"row(s) ({incoherent}): the emitted ambiguity class contradicts the "
            "rendered decision, so the correct label is coming from the gate and "
            "label logic, not from a trustworthy class signal. The class field "
            "must not be used as a selector feature until this is driven to zero "
            "on the supervisor and source-near panels."
        )
    else:
        parts.append(
            "No class/label incoherence on this slice: the emitted ambiguity class "
            "agrees with every rendered decision."
        )
    return " ".join(parts)


def _register(summary: dict[str, Any]) -> None:
    head = summary["headline"]
    entries = [
        entry for entry in load_run_registry(REGISTRY_PATH) if entry.run_id != RUN_ID
    ]
    entries.append(
        RunRegistryEntry(
            run_id=RUN_ID,
            artifact_paths=(
                f"experiments/{JSON_PATH.name}",
                f"experiments/{MD_PATH.name}",
                f"experiments/{SLICE_JSONL.name}",
            ),
            date="2026-06-15",
            pipeline_family="fresh_evidence_reasoner_ambiguity_semantic_scorer",
            split="validation",
            row_count=head["rows"],
            model="none",
            model_role=(
                "Deterministic semantic / over-specificity overlay on the saved "
                "live ambiguity slice; scores clinical decision kind alongside "
                "Purist and flags re-bucketing and class/label incoherence."
            ),
            mode="analysis-only",
            replay_status="analysis_only",
            repair_mode="none",
            cache_reuse_source=str(SLICE_JSONL),
            primary_metrics={
                "rows": head["rows"],
                "purist_correct": head["purist_correct"],
                "semantic_correct": head["semantic_correct"],
                "purist_minus_semantic": head["purist_minus_semantic"],
                "over_specific_rebucket_count": len(
                    head["over_specific_rebucket_rows"]
                ),
                "class_label_incoherent_count": len(
                    head["class_label_incoherent_rows"]
                ),
            },
            evidence_validity=(
                "Validation-only diagnostic overlay on saved live outputs. No "
                "model calls, no scorer policy change, no locked test rows read. "
                "The frozen Purist scorer is unchanged; this is an additional "
                "view used to keep the live run honest about re-bucketing."
            ),
            decision="revise",
            supersedes=(),
            claim_language_notes=(
                "Adds a semantic / over-specificity view so the live ambiguity "
                "run cannot be credited for Purist re-bucketing. Diagnostic "
                "instrumentation, not a holdout-facing candidate or a scorer "
                "replacement."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
