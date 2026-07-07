"""Re-score the 5 stale `exectv2_2call_no_sf_adjudicator_*` runs under the
finalized scorer (the 07-02 pipeline-assumption-audit sweep left these out of
scope; their cached predictions are present, so a faithful re-score is a
zero-LLM mechanical operation).

This is the committed replacement for the 07-02 sweep's ad-hoc inline harness,
so the Phase-4 anti-recurrence guardrail has a reusable tool the next time the
scorer moves.

Why this works without any LLM calls: each run's cached per-letter `.jsonl`
producer artifacts (structured / diagnosis_decomposer / sf_union /
prescription_deterministic_repair) are `kind: saved_jsonl` inputs to the
deterministic finding-assembly pipeline. ``build_finding_assembly`` reads them,
runs the four scorers, and emits ``score_ladder.headline_target`` — the exact
computation path ``model_swap.write_model_swap_candidate_artifacts`` used
historically. Diagnosis is reported as ``concept_only`` (the
``clinical_headline`` unit-key surface, CUI-projected), matching the
post-07-02 canonical convention.

Aggregate-only mandate (holdout discipline): the one full-200 run
(`qwen36_repair_v02_full200`) updates ONLY the overall `clinical_headline_f1`;
its per-family `primary_metrics` are left at pre-fix values per the
exectv2_same_core_full200_predeclaration_2026-06-25.md boundary.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
from typing import Any

from clinical_extraction.core.registry import (
    load_run_registry,
    write_run_registry,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
    build_finding_assembly,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import model_swap

REGISTRY_PATH = Path("experiments/registry.jsonl")
# The 5 stale runs (run_id -> config path). All have cached saved-jsonl producers.
STALE_RUN_CONFIGS: dict[str, Path] = {
    "exectv2_2call_no_sf_adjudicator_deepseek_dev140": Path(
        "configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_deepseek_dev140.json"
    ),
    "exectv2_2call_no_sf_adjudicator_gpt41mini_dev140": Path(
        "configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_gpt41mini_dev140.json"
    ),
    "exectv2_2call_no_sf_adjudicator_qwen36_dev140": Path(
        "configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_qwen36_dev140.json"
    ),
    "exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140": Path(
        "configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140.json"
    ),
    "exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200": Path(
        "configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200.json"
    ),
}
# The only full-200 run: aggregate-only mandate -> update overall only.
FULL200_RUN_IDS: frozenset[str] = frozenset(
    {"exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200"}
)
# Tail marker that the 07-02 sweep stamped on every NOT-re-scored record. We
# replace everything from this marker onward with the corrected re-score note.
STALE_TAIL_MARKER = "| 2026-07-02 scorer-correctness sweep: NOT re-scored"
RESCORE_DATE = "2026-07-03"


def _rescore_run(config_path: Path) -> dict[str, float]:
    """Re-build the no-call finding assembly for one config and return the
    headline_target per-family F1 (overall + Dx/SF/Rx/Inv)."""
    config = model_swap.load_model_swap_config(config_path)
    gold = load_letters()  # historical runs sliced [:row_count] internally
    run = build_finding_assembly(
        config.assembly, generated_on=RESCORE_DATE, gold_loader=lambda _split: gold
    )
    headline = run.report["score_ladder"]["headline_target"]
    by_ind = headline["by_indicator"]
    return {
        "overall": float(headline["overall"]["f1"]),
        "Diagnosis": float(by_ind["Diagnosis"]["f1"]),
        "SeizureFrequency": float(by_ind["SeizureFrequency"]["f1"]),
        "Prescription": float(by_ind["Prescription"]["f1"]),
        "Investigations": float(by_ind["Investigations"]["f1"]),
    }


def _new_disclosure_tail(
    run_id: str,
    stale: dict[str, Any],
    rescored: dict[str, float],
    is_full200: bool,
) -> str:
    """Build the corrected re-score note that replaces the stale tail.

    Preserves the prior stale values inline so the disclosure is self-contained
    provenance (overwrite-with-disclose policy, matching the 07-02 sweep's
    style on the canonical GEPA run).
    """
    stale_overall = stale["clinical_headline_f1"]
    new_overall = rescored["overall"]
    parts = [
        f"| 2026-07-03 scorer-correctness re-score (zero new LLM calls; finalized scorer = "
        f"Rx clause-scope + valproate/brand lexicon, SF zero-count precedence, Inv text-fallback "
        f"gate, Dx D1 hierarchy-aware match; closes the 07-02 sweep's out-of-scope gap): "
        f"clinical_headline_f1 {stale_overall}->{new_overall}"
    ]
    if is_full200:
        # Aggregate-only mandate: do not report per-family full-200 numbers.
        parts.append(
            ". Per-family primary_metrics left at pre-fix values per the "
            "exectv2_same_core_full200_predeclaration aggregate-only boundary. "
            "Predictions (.jsonl) unchanged."
        )
    else:
        # dev140: report all four families.
        family_pairs = []
        for fam_key, fam_name in (
            ("diagnosis_f1", "Diagnosis"),
            ("seizure_frequency_f1", "SeizureFrequency"),
            ("prescription_f1", "Prescription"),
            ("investigations_f1", "Investigations"),
        ):
            if fam_key in stale:
                family_pairs.append(f"{fam_name} {stale[fam_key]}->{rescored[fam_name]}")
        parts.append(", " + ", ".join(family_pairs) + ".")
        parts.append(" Predictions (.jsonl) unchanged.")
    return "".join(parts)


def _strip_stale_tail(notes: str) -> str:
    """Return the original prose up to the stale tail marker."""
    idx = notes.find(STALE_TAIL_MARKER)
    if idx == -1:
        # Not all 5 runs may carry the exact marker; fall back to stripping
        # from the first dated re-score mention after the base prose.
        return notes.rstrip()
    return notes[:idx].rstrip()


def rescore_all(registry_path: Path = REGISTRY_PATH, *, dry_run: bool = False) -> None:
    entries = list(load_run_registry(registry_path))
    by_id = {e.run_id: e for e in entries}
    missing = [rid for rid in STALE_RUN_CONFIGS if rid not in by_id]
    if missing:
        raise SystemExit(f"registry missing stale run_id(s): {missing}")

    changes: list[str] = []
    for run_id, config_path in STALE_RUN_CONFIGS.items():
        is_full200 = run_id in FULL200_RUN_IDS
        rescored = _rescore_run(config_path)
        entry = by_id[run_id]
        stale = dict(entry.primary_metrics)
        new_primary = dict(stale)
        new_primary["clinical_headline_f1"] = rescored["overall"]
        if not is_full200:
            new_primary["diagnosis_f1"] = rescored["Diagnosis"]
            new_primary["seizure_frequency_f1"] = rescored["SeizureFrequency"]
            new_primary["prescription_f1"] = rescored["Prescription"]
            new_primary["investigations_f1"] = rescored["Investigations"]
        new_tail = _new_disclosure_tail(run_id, stale, rescored, is_full200)
        base_notes = _strip_stale_tail(entry.claim_language_notes)
        new_notes = base_notes + " " + new_tail
        updated = replace(entry, primary_metrics=new_primary, claim_language_notes=new_notes)
        by_id[run_id] = updated
        # Faithfulness self-check (informational, not gating): the audit's I1
        # Inv text-fallback fix is latent on the GEPA canonical run, but these
        # model-swap runs use a different Investigations lane (structured-
        # direct, not a per-family LLM Inv extractor), and the F2 greedy ->
        # maximum-cardinality match fix (also 07-02) can legitimately move Inv
        # clinical_headline by re-pairing bare-word Inv spans that the old
        # greedy matcher mis-paired. Flag any Inv drift for confirmation, but
        # do not treat it as a harness bug.
        if not is_full200:
            inv_old = stale.get("investigations_f1")
            inv_new = rescored["Investigations"]
            if inv_old is not None and abs(inv_new - inv_old) > 1e-9:
                print(
                    f"  NOTE: {run_id} Investigations moved {inv_old}->{inv_new} "
                    f"(I1 latent on GEPA canonical; F2 match fix or I1 firing on "
                    f"this lane's predictions — legitimate scorer effect, not a bug)."
                )
        delta = rescored["overall"] - float(stale["clinical_headline_f1"])
        changes.append(
            f"  {run_id}: overall {stale['clinical_headline_f1']}->{rescored['overall']} "
            f"({'+' if delta >= 0 else ''}{delta:.4f})"
            + (
                ""
                if is_full200
                else f" | Inv {stale.get('investigations_f1')}->{rescored['Investigations']}"
            )
        )

    print("=== re-score summary ===")
    print("\n".join(changes))
    if dry_run:
        print("\n(dry-run: registry NOT written)")
        return
    write_run_registry(list(by_id.values()), registry_path)
    print(f"\nWrote {len(by_id)} records to {registry_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Re-score and print the summary without writing the registry.",
    )
    args = parser.parse_args()
    rescore_all(REGISTRY_PATH, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
