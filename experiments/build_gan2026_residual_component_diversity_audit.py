"""Component diversity audit: are the three components *independently* wrong, or
identically wrong, on the v0.9 residual?

Instrumentation step 3.1 of the unknown-frequency agentic pathways doc. The
selector-only oracle is capped at 739/750 because 11 selected-wrong rows have no
Purist-correct deterministic, consensus, or fresh-v0.4 component (Insight 1).
Insight 2 claims those failures are *correlated*: the three nominally
independent sources share one over-reading prior and collapse on exactly the
rows that matter. This script quantifies that claim.

For each selected-wrong row it normalizes the deterministic, consensus, and
fresh-v0.4 labels to their Purist buckets and measures how many *distinct*
buckets the three produce. On the no-correct rows, "all three in one bucket"
means identically wrong (fully correlated); "two or three distinct buckets"
means at least one source broke ranks and a smarter selector or a second
generation pass could in principle help.

The practical payoff: a second generation pass only buys headroom where the
sources already disagree or where a *new* correct bucket can be reached. If the
no-correct residual is dominated by single-bucket correlated failure, a second
model that shares the over-reading prior buys nothing, and the lever must be
changing the evidence the model reads, not adding another voter.

Validation-only. Reads the saved v0.9 residual component-generation audit; makes
no model calls, reads no locked test rows, and changes no scorer policy.
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

RESIDUAL_AUDIT_JSON = (
    EXPERIMENTS
    / "gan2026_consensus_fresh_agreement_selector_v0_9_"
    "residual_component_generation_audit_2026-06-15.json"
)

RUN_ID = "gan2026_residual_component_diversity_audit_2026-06-15"
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"

COMPONENTS = ("deterministic", "consensus", "fresh_evidence")
COMPONENT_LABEL_KEY = {
    "deterministic": "deterministic_label",
    "consensus": "consensus_label",
    "fresh_evidence": "fresh_evidence_label",
}


def main() -> None:
    records = _load_residual_records(RESIDUAL_AUDIT_JSON)
    summary = _audit(records)
    payload = {
        "run_id": RUN_ID,
        "date": "2026-06-15",
        "purpose": (
            "Validation-only component diversity audit: on the v0.9 residual, "
            "how often are the deterministic/consensus/fresh-v0.4 components "
            "identically wrong (one Purist bucket) versus split across buckets? "
            "Quantifies the correlated-failure claim (Insight 2) that caps the "
            "selector oracle at 739/750."
        ),
        "source_artifact": str(RESIDUAL_AUDIT_JSON),
        "summary": summary,
    }
    JSON_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(_markdown(payload), encoding="utf-8")
    _register(summary)
    print(json.dumps(summary["headline"], indent=2, sort_keys=True))


def _load_residual_records(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return list(payload["summary"]["selected_wrong_records"])


def _purist_bucket(label: str | None) -> str | None:
    if not label:
        return None
    try:
        record = label_to_frequency_record(str(label))
    except Exception:
        return None
    return str(map_purist(record.monthly_frequency))


def _row_diversity(record: dict[str, Any]) -> dict[str, Any]:
    gold_bucket = _purist_bucket(record["gold_label"])
    component_buckets = {
        component: _purist_bucket(record[COMPONENT_LABEL_KEY[component]])
        for component in COMPONENTS
    }
    # Unparseable components count as their own distinct outcome so a parse
    # failure is never silently merged with a real bucket.
    distinct_outcomes = {
        component_buckets[component] or f"<unparseable:{component}>"
        for component in COMPONENTS
    }
    distinct_count = len(distinct_outcomes)
    if distinct_count == 1:
        agreement = "all_three_one_bucket"
    elif distinct_count == 2:
        agreement = "two_buckets"
    else:
        agreement = "three_buckets"
    any_correct = bool(record["correct_components"])
    return {
        "source_row_index": record["source_row_index"],
        "gold_band": record["gold_band"],
        "gold_label": record["gold_label"],
        "gold_bucket": gold_bucket,
        "component_labels": {
            component: record[COMPONENT_LABEL_KEY[component]]
            for component in COMPONENTS
        },
        "component_buckets": component_buckets,
        "distinct_bucket_count": distinct_count,
        "agreement": agreement,
        "correct_components": list(record["correct_components"]),
        "has_correct_component": any_correct,
        "audit_categories": list(record["audit_categories"]),
    }


def _audit(records: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [_row_diversity(record) for record in records]
    no_correct = [row for row in rows if not row["has_correct_component"]]
    recoverable = [row for row in rows if row["has_correct_component"]]

    def _agreement_counts(subset: list[dict[str, Any]]) -> dict[str, int]:
        return dict(sorted(Counter(row["agreement"] for row in subset).items()))

    no_correct_correlated = [
        row["source_row_index"]
        for row in no_correct
        if row["agreement"] == "all_three_one_bucket"
    ]
    no_correct_split = [
        row["source_row_index"]
        for row in no_correct
        if row["agreement"] != "all_three_one_bucket"
    ]
    category_counts = Counter()
    for row in no_correct:
        for category in row["audit_categories"]:
            category_counts[category] += 1

    return {
        "headline": {
            "selected_wrong_rows": len(rows),
            "no_correct_rows": len(no_correct),
            "recoverable_rows": len(recoverable),
            "no_correct_correlated_one_bucket": len(no_correct_correlated),
            "no_correct_split_across_buckets": len(no_correct_split),
            "correlated_failure_fraction": (
                round(len(no_correct_correlated) / len(no_correct), 4)
                if no_correct
                else None
            ),
        },
        "no_correct_correlated_rows": sorted(no_correct_correlated),
        "no_correct_split_rows": sorted(no_correct_split),
        "no_correct_audit_category_counts": dict(sorted(category_counts.items())),
        "agreement_counts": {
            "all_selected_wrong": _agreement_counts(rows),
            "no_correct": _agreement_counts(no_correct),
            "recoverable": _agreement_counts(recoverable),
        },
        "no_correct_rows": sorted(no_correct, key=lambda r: r["source_row_index"]),
        "recoverable_rows": sorted(
            recoverable, key=lambda r: r["source_row_index"]
        ),
    }


def _markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    head = summary["headline"]
    lines = [
        "# Gan 2026 Residual Component Diversity Audit",
        "",
        "Date: 2026-06-15",
        "",
        "Validation-only instrumentation (step 3.1 of the unknown-frequency "
        "agentic pathways doc). It reads the saved v0.9 residual "
        "component-generation audit, normalizes each component's label to its "
        "Purist bucket, and measures whether the deterministic, consensus, and "
        "fresh-v0.4 components fail in *correlated* (one bucket) or *independent* "
        "(split bucket) ways. No model calls, no locked test rows, no scorer "
        "change.",
        "",
        "## Why this matters",
        "",
        "The selector-only oracle is capped at `739/750` because "
        f"`{head['no_correct_rows']}` selected-wrong rows have no Purist-correct "
        "component at all (Insight 1). Insight 2 claims those failures are "
        "*correlated* — the three nominally independent sources share one "
        "over-reading prior. If true, a second generation pass that shares that "
        "prior buys nothing; only changing the evidence the model reads can move "
        "the ceiling. This audit tests the claim directly.",
        "",
        "## Headline",
        "",
        f"- Selected-wrong rows audited: `{head['selected_wrong_rows']}` "
        f"(`{head['no_correct_rows']}` no-correct, "
        f"`{head['recoverable_rows']}` recoverable)",
        f"- No-correct rows where all three components land in **one** Purist "
        f"bucket (identically wrong): "
        f"**`{head['no_correct_correlated_one_bucket']}/"
        f"{head['no_correct_rows']}`** "
        f"(fraction `{head['correlated_failure_fraction']}`)",
        f"- No-correct rows where at least one component breaks ranks: "
        f"`{head['no_correct_split_across_buckets']}/{head['no_correct_rows']}`",
        "",
        f"Correlated (one-bucket) no-correct rows: "
        f"`{summary['no_correct_correlated_rows']}`",
        "",
        f"Split (multi-bucket) no-correct rows: "
        f"`{summary['no_correct_split_rows']}`",
        "",
        "## Agreement structure",
        "",
        "| Subset | all_three_one_bucket | two_buckets | three_buckets |",
        "| --- | ---: | ---: | ---: |",
    ]
    for name in ("all_selected_wrong", "no_correct", "recoverable"):
        counts = summary["agreement_counts"][name]
        lines.append(
            f"| {name} | {counts.get('all_three_one_bucket', 0)} "
            f"| {counts.get('two_buckets', 0)} "
            f"| {counts.get('three_buckets', 0)} |"
        )
    lines.extend(
        [
            "",
            "## No-correct rows (the rows that gate the ceiling)",
            "",
            "| Row | Band | Gold | Det bucket | Consensus bucket | Fresh-v0.4 bucket | Distinct | Agreement |",
            "| ---: | --- | --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for row in summary["no_correct_rows"]:
        buckets = row["component_buckets"]
        lines.append(
            f"| {row['source_row_index']} "
            f"| `{row['gold_band']}` "
            f"| `{row['gold_label']}` "
            f"| `{buckets['deterministic']}` "
            f"| `{buckets['consensus']}` "
            f"| `{buckets['fresh_evidence']}` "
            f"| {row['distinct_bucket_count']} "
            f"| {row['agreement']} |"
        )
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
    correlated = head["no_correct_correlated_one_bucket"]
    total = head["no_correct_rows"]
    fraction = head["correlated_failure_fraction"]
    parts = [
        (
            f"Of the {total} no-correct residual rows, {correlated} have all three "
            f"components collapsed into a single Purist bucket "
            f"(fraction {fraction}). On those rows the deterministic rules, exact "
            "consensus, and V12 fresh evidence are not just wrong but "
            "*identically* wrong — independence has collapsed exactly where it "
            "would have to hold for selection or voting to help."
        )
    ]
    if fraction is not None and fraction >= 0.5:
        parts.append(
            "This confirms Insight 2 quantitatively: the dominant residual mode is "
            "correlated, single-bucket over-reading, not a selection miss among "
            "diverse candidates. A second generation pass only helps if it does "
            "not share the over-reading prior — i.e. if it changes the evidence "
            "the model conditions on, not merely the decision contract layered on "
            "top. Adding another same-prior voter is expected to buy nothing on "
            "these rows."
        )
    else:
        parts.append(
            "The residual is more split across buckets than Insight 2 assumed, "
            "which means at least one source already breaks ranks on many "
            "no-correct rows. That leaves room for a sharper selector or a "
            "diversity-seeking second pass, and the correlated subset should be "
            "separated from the genuinely-split subset before the next generation "
            "bet."
        )
    parts.append(
        "The split rows are the more tractable target for a second pass; the "
        "correlated rows need different evidence, not another vote."
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
            ),
            date="2026-06-15",
            pipeline_family="consensus_fresh_agreement_selector_component_diversity",
            split="validation",
            row_count=head["selected_wrong_rows"],
            model="none",
            model_role=(
                "Deterministic re-analysis of saved v0.9 residual component "
                "labels; normalizes each component to its Purist bucket to "
                "measure correlated versus independent failure."
            ),
            mode="analysis-only",
            replay_status="analysis_only",
            repair_mode="none",
            cache_reuse_source=str(RESIDUAL_AUDIT_JSON),
            primary_metrics={
                "no_correct_rows": head["no_correct_rows"],
                "no_correct_correlated_one_bucket": (
                    head["no_correct_correlated_one_bucket"]
                ),
                "no_correct_split_across_buckets": (
                    head["no_correct_split_across_buckets"]
                ),
                "correlated_failure_fraction": head["correlated_failure_fraction"],
            },
            evidence_validity=(
                "Validation-only re-analysis of saved component labels. No model "
                "calls, no scorer changes, no locked test rows read."
            ),
            decision="revise",
            supersedes=(),
            claim_language_notes=(
                "Quantifies whether the no-correct residual is correlated "
                "(single-bucket) or independent (split) failure. Diagnostic "
                "instrumentation for the component-generation bet, not a "
                "holdout-facing candidate."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
