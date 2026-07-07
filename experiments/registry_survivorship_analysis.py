"""Registry survivorship-bias analysis (Item 2 of
docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md).

Zero-LLM, read-only. `docs/research/paper_manuscript_2026-06-26.md` does not cite
run_ids directly (one exception, `exectv2_2call_no_sf_adjudicator`, itself a
pipeline_family prefix rather than a literal run_id). It cites ~16 companion docs
instead. This script traces the run_ids those companion docs cite -- a two-hop
extraction, manuscript -> doc -> run_id -- back through the run registry's
`supersedes` chains and reports:

1. Which cited references resolve to a registry entry (direct `run_id` match,
   an `artifact_paths` basename match, or -- for two cases where a doc used an
   informal label that matches no registry `run_id` but whose cited numbers
   matched a differently-named combined registry entry's `primary_metrics`
   exactly -- a metrics-verified match), and which resolve to *nothing*: real
   on-disk artifacts backing manuscript claims that were never written to
   `experiments/registry.jsonl` at all.
2. Chain-length-to-publication per resolved cited run_id: the count of
   distinct ancestor run_ids reachable by recursively walking `supersedes`.
3. A `superseded_by` forward sanity check -- is each cited run_id itself the
   terminal (non-superseded) node, or does the manuscript cite something a
   later run superseded?
4. Registry-wide accounting: of the registry's 244 rows, how many are (a)
   directly cited, (b) silently absorbed as an ancestor of a citation via
   `supersedes`, or (c) untouched by the citation graph entirely -- broken out
   by `decision`, in particular the 146 `revise` / 34 `reject` rows.

Extraction method (documented here, not re-derived mechanically at run time --
see docs/research/exectv2_registry_survivorship_bias_2026-07-01.md "Extraction
method" section for the full per-doc audit trail): each of the 16
manuscript-cited companion docs was read for backtick-quoted run_id-shaped
tokens and "Runs / Artifacts / Sources" citation blocks. Every candidate token
was checked against the registry three ways, in this order: (1) exact
`run_id` match; (2) exact `artifact_paths` basename match; (3) for two
specific cases (Table 6 of exectv2_results_section_draft_2026-06-26.md) where
a doc's own ad hoc row label matched no registry `run_id` but its cited
numbers matched a differently-named combined entry's `primary_metrics`
exactly, resolved to that entry. Tokens that matched none of the three are
reported below as NOT_REGISTERED_CITATIONS -- confirmed present as real
artifacts on disk, absent from the registry.

Usage:
    uv run python experiments/registry_survivorship_analysis.py
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from pathlib import Path

from clinical_extraction.core.registry import RunRegistryEntry, load_run_registry

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "experiments" / "registry.jsonl"

# The 16 manuscript-cited companion docs (paper_manuscript_2026-06-26.md's full
# non-run_id citation list, verified present on disk 2026-07-01).
COMPANION_DOCS: tuple[str, ...] = (
    "docs/design/reliability_thesis.md",
    "docs/experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md",
    "docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md",
    "docs/research/closing_stage_research_critique_2026-06-27.md",
    "docs/research/consensus_fresh_selector_fate_2026-06-27.md",
    "docs/research/decomposition_research_impact_review_2026-06-27.md",
    "docs/research/exectv2_results_section_draft_2026-06-26.md",
    "docs/research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md",
    "docs/research/gan2026/syntheses/gan2026_closeoff_report_2026-06-12.md",
    "docs/research/paper_drafts/benchmark_surface_reconciliation_subsection_2026-06-27.md",
    "docs/research/paper_drafts/capability_first_discussion_contributions_2026-06-27.md",
    "docs/research/paper_drafts/capability_first_manuscript_outline_2026-06-27.md",
    "docs/research/paper_drafts/capability_first_results_section_2026-06-27.md",
    "docs/research/paper_drafts/wall_transfer_cross_dataset_2026-06-27.md",
    "experiments/exectv2_hybrid_benchmark_overall_bestof_dev_20260618.json",
    "experiments/gan2026_reliability_p2_1_semantic_entropy_preflight150_2026-06-17.md",
)


@dataclass(frozen=True)
class CitedRun:
    """A run_id the manuscript's citation graph rests on, resolved to a registry row."""

    run_id: str
    source_docs: tuple[str, ...]
    resolution: str  # "direct" | "artifact_path" | "metrics_verified"
    note: str = ""


@dataclass(frozen=True)
class UnregisteredCitation:
    """A run-shaped reference in a companion doc with no registry row at all."""

    label: str
    source_docs: tuple[str, ...]
    note: str = ""


# The registered run_ids the manuscript's companion docs actually cite. See the
# module docstring and the companion write-up doc for the per-doc extraction.
CITED_RUNS: tuple[CitedRun, ...] = (
    CitedRun(
        "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628",
        ("docs/experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md",),
        "direct",
        "Canonical Diagnosis row-adjudication run (dev140 0.7313 multi-family GEPA).",
    ),
    CitedRun(
        "gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate1_hard_slice_audit_2026-06-26",
        ("docs/research/consensus_fresh_selector_fate_2026-06-27.md",),
        "direct",
        "Frozen-gate hard-slice audit for the consensus/fresh selector v0.9.",
    ),
    CitedRun(
        "gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate2_robustness_stress_2026-06-26",
        ("docs/research/consensus_fresh_selector_fate_2026-06-27.md",),
        "direct",
        "Frozen-gate robustness stress for the same selector.",
    ),
    CitedRun(
        "gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_constrained_aggregate_audit_2026-06-26",
        ("docs/research/consensus_fresh_selector_fate_2026-06-27.md",),
        "direct",
        "Constrained-variant frozen aggregate audit (348/450, P4 fail case).",
    ),
    CitedRun(
        "gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_exact_aggregate_audit_2026-06-26",
        ("docs/research/consensus_fresh_selector_fate_2026-06-27.md",),
        "direct",
        "Exact-variant frozen aggregate audit (359/450, the P1/P2 kill-criterion row).",
    ),
    CitedRun(
        "gan2026_consensus_fresh_agreement_selector_v0_9_frozen_protocol_2026-06-26",
        ("docs/research/consensus_fresh_selector_fate_2026-06-27.md",),
        "direct",
        "Frozen-test protocol declaration for the selector v0.9.",
    ),
    CitedRun(
        "gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15",
        ("docs/research/consensus_fresh_selector_fate_2026-06-27.md",),
        "direct",
        "Validation750 no-call replay supporting the P3 precision-with-margin check.",
    ),
    CitedRun(
        "exectv2_2call_no_sf_adjudicator_deepseek_dev140",
        ("docs/research/exectv2_results_section_draft_2026-06-26.md",),
        "direct",
        "Table 5: same-core model-swap dev140, DeepSeek row.",
    ),
    CitedRun(
        "exectv2_2call_no_sf_adjudicator_gpt41mini_dev140",
        ("docs/research/exectv2_results_section_draft_2026-06-26.md",),
        "direct",
        "Table 5: same-core model-swap dev140, GPT-4.1-mini row.",
    ),
    CitedRun(
        "exectv2_2call_no_sf_adjudicator_qwen36_dev140",
        ("docs/research/exectv2_results_section_draft_2026-06-26.md",),
        "direct",
        "Table 5: same-core model-swap dev140, Qwen (unrepaired) row.",
    ),
    CitedRun(
        "exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140",
        ("docs/research/exectv2_results_section_draft_2026-06-26.md",),
        "direct",
        "Table 5: same-core model-swap dev140, Qwen repair v02 row.",
    ),
    CitedRun(
        "exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200",
        ("docs/research/exectv2_results_section_draft_2026-06-26.md",),
        "direct",
        "Table 6: same-core model-swap full200, Qwen repair v02 row.",
    ),
    CitedRun(
        "exectv2_same_core_model_swap_full200_20260625",
        (
            "docs/research/exectv2_results_section_draft_2026-06-26.md",
            "docs/research/paper_drafts/capability_first_manuscript_outline_2026-06-27.md",
            "docs/research/paper_drafts/capability_first_results_section_2026-06-27.md",
        ),
        "metrics_verified",
        "Table 6 of exectv2_results_section_draft_2026-06-26.md labels two rows "
        "`exectv2_2call_no_sf_adjudicator_deepseek_full200` / "
        "`..._gpt41mini_full200`; neither string is a registry run_id. Both "
        "resolve to this single combined entry -- its primary_metrics carry "
        "deepseek_clinical_headline_f1=0.8566 and gpt41mini_clinical_headline_f1"
        "=0.8356, an exact match to the doc's cited numbers. The other two docs "
        "cite this entry by its real filename, exectv2_same_core_model_swap_"
        "full200_2026-06-25.md.",
    ),
    CitedRun(
        "gan2026_closeoff_report_2026-06-12",
        ("docs/research/gan2026/syntheses/gan2026_closeoff_report_2026-06-12.md",),
        "direct",
        "The companion doc is itself the registered analysis-only entry (matched "
        "by run_id == doc-filename-slug convention). Note: its own "
        '`artifact_paths` field is `[""]` -- a placeholder, not a real path '
        "back to this doc -- a minor registry-hygiene gap distinct from the "
        "chain-length question this script answers.",
    ),
    CitedRun(
        "exectv2_hybrid_benchmark_overall_dev_20260618",
        ("experiments/exectv2_hybrid_benchmark_overall_bestof_dev_20260618.json",),
        "artifact_path",
        "The companion artifact is itself listed in this entry's artifact_paths.",
    ),
    CitedRun(
        "gan2026_reliability_p2_1_semantic_entropy_2026-06-17",
        ("experiments/gan2026_reliability_p2_1_semantic_entropy_preflight150_2026-06-17.md",),
        "artifact_path",
        "The companion artifact is itself listed in this entry's artifact_paths. "
        "Also cited by name (`RUN_INDEX §gan2026_reliability_p2_1_semantic_"
        "entropy`) from capability_first_manuscript_outline_2026-06-27.md.",
    ),
)

# Run-shaped references found in the same 16 companion docs that resolve to
# NO registry row -- neither a direct run_id nor an artifact_paths basename
# match -- despite real, dated artifacts existing on disk. Reported per the
# plan's explicit instruction not to silently drop these.
NOT_REGISTERED_CITATIONS: tuple[UnregisteredCitation, ...] = (
    UnregisteredCitation(
        "exectv2_gepa_sf_verify_gpt41mini_20260628",
        (
            "docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md",
        ),
        "The canonical P2 two-stage GEPA run the SF plateau finding (state_profile "
        "0.710 stage1 / 0.772 stage2) rests on. Artifacts exist on disk "
        "(experiments/exectv2_gepa_sf_verify_gpt41mini_20260628.{json,jsonl,"
        "instruction.txt}), confirmed present 2026-07-01, but no registry row. "
        "The entire Phase-5 sibling family (exectv2_gepa_sf_verify_p5_reasoner_"
        "*_20260629, exectv2_gepa_sf_verify_v2_deepseekchat_20260629) is equally "
        "unregistered. Same silent-registration-failure pattern the "
        "implementation plan already flagged for exectv2_gepa_multistage_dedup_"
        "gpt41mini_20260628 (Phase 2 step 0) -- this makes at least two confirmed "
        "instances.",
    ),
    UnregisteredCitation(
        "exectv2_gpt41mini_simplification_2call_no_sf_adjudicator",
        ("docs/research/exectv2_results_section_draft_2026-06-26.md",),
        "The lean 2-call cost-performance frontier row (full-200 0.8356 overall, 400 calls).",
    ),
    UnregisteredCitation(
        "gan2026_research_closeout_synthesis_2026-06-17 (the companion doc itself)",
        ("docs/research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md",),
        "One of the 16 manuscript-cited companion docs; no registry row of its "
        "own. Its own 'Core Artifacts' section (lines 330-343) lists mostly "
        "empty backtick placeholders (``), a curation gap in the source doc "
        "itself, independent of registry coverage.",
    ),
    UnregisteredCitation(
        "gan2026_simplest_arch_decomposition_v1_validation750_2026-06-16",
        ("docs/research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md",),
        "One of only two non-empty 'Core Artifacts' entries in that doc.",
    ),
    UnregisteredCitation(
        "gan2026_single_model_anchor_v0reference_test450_aggregate_readout_2026-06-16",
        ("docs/research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md",),
        "The other non-empty 'Core Artifacts' entry.",
    ),
    UnregisteredCitation(
        "exectv2_sf_wall_transfer_probe_2026-06-27",
        (
            "docs/research/paper_drafts/capability_first_discussion_contributions_2026-06-27.md",
            "docs/research/paper_drafts/capability_first_manuscript_outline_2026-06-27.md",
        ),
        "The probe underlying the wall-transfer verdict "
        "(docs/research/paper_drafts/wall_transfer_cross_dataset_2026-06-27.md, "
        "one of the 16 companion docs itself) -- band_unknown entropy 0.000, "
        "H0_confident_over_reading not refuted. No registry row.",
    ),
    UnregisteredCitation(
        "exectv2_component_off_replay_dev140_20260626",
        (
            "docs/research/paper_drafts/capability_first_discussion_contributions_2026-06-27.md",
            "docs/research/paper_drafts/capability_first_manuscript_outline_2026-06-27.md",
        ),
        "Dev140 one-component-off replay (16 rows), Table 8 source.",
    ),
    UnregisteredCitation(
        "exectv2_component_off_replay_full200_20260626",
        ("docs/research/paper_drafts/capability_first_results_section_2026-06-27.md",),
        "Full-200 one-component-off replay (9 rows), Table R2/R8 source; also the "
        "source the implementation plan's own Item 3 cites directly "
        "(experiments/exectv2_component_off_replay_full200_20260626.md:35-37).",
    ),
    UnregisteredCitation(
        "exectv2_all_entities_scoring_mechanics_deep_dive_2026-06-12",
        ("docs/research/paper_drafts/capability_first_manuscript_outline_2026-06-27.md",),
        "Cited as evidence that the two architectures exist in code.",
    ),
    UnregisteredCitation(
        "cross_task_shared_component_ablation_2026-06-27",
        ("docs/research/paper_drafts/capability_first_manuscript_outline_2026-06-27.md",),
        "The N=2 cross-task component-transfer table (evidence_validation "
        "Delta=0.0000 both tasks; standard_dictionary +0.0389 exectv2 / +0.0293 "
        "Gan2026) -- the sole evidentiary basis for the manuscript's one "
        "cross-task component-transfer claim. No registry row.",
    ),
    UnregisteredCitation(
        "gan2026_component_stage_ladder_validation_20260624",
        ("docs/research/paper_drafts/capability_first_manuscript_outline_2026-06-27.md",),
        "Gan2026 stage-ladder validation source for the cross-task read-out.",
    ),
)


@dataclass
class ChainResult:
    run_id: str
    chain_length: int
    ancestors: list[str]
    unregistered_ancestors: list[str]
    is_terminal: bool
    superseded_by_chain: list[str] = field(default_factory=list)


def _load_entries() -> dict[str, RunRegistryEntry]:
    entries = load_run_registry(REGISTRY_PATH)
    by_id = {entry.run_id: entry for entry in entries}
    if len(by_id) != len(entries):
        raise ValueError("duplicate run_id in registry.jsonl")
    return by_id


def _walk_supersedes(run_id: str, by_id: dict[str, RunRegistryEntry]) -> ChainResult:
    """Recursively walk `supersedes` from run_id, collecting distinct ancestors."""

    seen: set[str] = set()
    unregistered: list[str] = []
    queue: list[str] = [run_id]
    frontier_seen = {run_id}
    while queue:
        current = queue.pop()
        entry = by_id.get(current)
        if entry is None:
            if current != run_id:
                unregistered.append(current)
            continue
        for prior in entry.supersedes:
            if prior in frontier_seen:
                continue  # cycle guard
            frontier_seen.add(prior)
            seen.add(prior)
            queue.append(prior)

    entry = by_id[run_id]
    superseded_by_chain: list[str] = []
    cursor = entry.superseded_by
    visited_forward = {run_id}
    while cursor:
        if cursor in visited_forward:
            break  # cycle guard
        superseded_by_chain.append(cursor)
        visited_forward.add(cursor)
        next_entry = by_id.get(cursor)
        cursor = next_entry.superseded_by if next_entry else None

    return ChainResult(
        run_id=run_id,
        chain_length=len(seen),
        ancestors=sorted(seen),
        unregistered_ancestors=sorted(set(unregistered)),
        is_terminal=entry.superseded_by is None,
        superseded_by_chain=superseded_by_chain,
    )


def main() -> None:
    by_id = _load_entries()
    total_rows = len(by_id)
    decisions = {}
    for entry in by_id.values():
        decisions.setdefault(entry.decision, []).append(entry.run_id)

    print("=" * 78)
    print("REGISTRY SURVIVORSHIP-BIAS ANALYSIS")
    print("=" * 78)
    print(f"Registry: {REGISTRY_PATH} ({total_rows} rows)")
    print(f"Companion docs scanned: {len(COMPANION_DOCS)}")
    print(f"Cited, registry-resolved run_ids: {len(CITED_RUNS)}")
    print(
        f"Cited, NOT registered (real artifacts, no registry row): {len(NOT_REGISTERED_CITATIONS)}"
    )
    print()

    print("-" * 78)
    print("PER-CITATION CHAIN LENGTH")
    print("-" * 78)
    results: list[ChainResult] = []
    absorbed: set[str] = set()
    for cited in CITED_RUNS:
        result = _walk_supersedes(cited.run_id, by_id)
        results.append(result)
        absorbed.update(result.ancestors)
        stale_flag = (
            ""
            if result.is_terminal
            else "  *** STALE: superseded_by chain -> " + " -> ".join(result.superseded_by_chain)
        )
        print(f"- {cited.run_id}")
        print(f"    resolution: {cited.resolution}; source docs: {', '.join(cited.source_docs)}")
        print(f"    chain_length_to_publication: {result.chain_length}")
        if result.ancestors:
            print(f"    ancestors: {', '.join(result.ancestors)}")
        if result.unregistered_ancestors:
            print(
                f"    unregistered ancestors named in supersedes: {', '.join(result.unregistered_ancestors)}"
            )
        print(f"    terminal (not itself superseded): {result.is_terminal}{stale_flag}")
    print()

    chain_lengths = [r.chain_length for r in results]
    print("-" * 78)
    print("SUMMARY STATISTICS ACROSS THE CITED SET")
    print("-" * 78)
    print(f"n cited run_ids (registry-resolved): {len(chain_lengths)}")
    print(f"mean chain length: {statistics.mean(chain_lengths):.2f}")
    print(f"median chain length: {statistics.median(chain_lengths):.2f}")
    print(f"min / max chain length: {min(chain_lengths)} / {max(chain_lengths)}")
    non_terminal = [r.run_id for r in results if not r.is_terminal]
    print(f"cited run_ids that are themselves superseded (stale citations): {len(non_terminal)}")
    if non_terminal:
        print(f"  -> {', '.join(non_terminal)}")
    print()

    print("-" * 78)
    print("REGISTRY-WIDE ACCOUNTING")
    print("-" * 78)
    cited_ids = {c.run_id for c in CITED_RUNS}
    absorbed_only = absorbed - cited_ids
    accounted = cited_ids | absorbed_only
    untouched = set(by_id) - accounted
    print(f"total registry rows: {total_rows}")
    print(
        f"  directly cited by the manuscript's citation graph: {len(cited_ids)} ({len(cited_ids) / total_rows:.1%})"
    )
    print(
        f"  silently absorbed as an ancestor via supersedes: {len(absorbed_only)} "
        f"({len(absorbed_only) / total_rows:.1%})"
    )
    print(
        f"  accounted for (cited + absorbed): {len(accounted)} ({len(accounted) / total_rows:.1%})"
    )
    print(
        f"  untouched by the citation graph entirely: {len(untouched)} "
        f"({len(untouched) / total_rows:.1%})"
    )
    print()

    print("By decision:")
    for decision, run_ids in sorted(decisions.items(), key=lambda kv: -len(kv[1])):
        run_id_set = set(run_ids)
        n = len(run_id_set)
        n_cited = len(run_id_set & cited_ids)
        n_absorbed = len(run_id_set & absorbed_only)
        n_untouched = len(run_id_set & untouched)
        print(
            f"  {decision:<38} n={n:>4}  cited={n_cited:>3}  absorbed={n_absorbed:>3}  "
            f"untouched={n_untouched:>3}"
        )
    print()

    print("-" * 78)
    print("NOT REGISTERED (real artifacts, cited by companion docs, no registry row)")
    print("-" * 78)
    for missing in NOT_REGISTERED_CITATIONS:
        print(f"- {missing.label}")
        print(f"    cited from: {', '.join(missing.source_docs)}")
        print(f"    {missing.note}")
    print()
    print(
        f"Distinct references traced from the 16 companion docs: "
        f"{len(CITED_RUNS)} registered + {len(NOT_REGISTERED_CITATIONS)} not registered = "
        f"{len(CITED_RUNS) + len(NOT_REGISTERED_CITATIONS)} total; "
        f"{len(NOT_REGISTERED_CITATIONS) / (len(CITED_RUNS) + len(NOT_REGISTERED_CITATIONS)):.1%} "
        f"of the manuscript's own citation graph is invisible to registry.jsonl."
    )


if __name__ == "__main__":
    main()
