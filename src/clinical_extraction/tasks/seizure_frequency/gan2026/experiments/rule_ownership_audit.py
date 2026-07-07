"""Rule-ownership audit matrix for Gan 2026 deterministic components."""

from __future__ import annotations

import csv
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.gold_policy import (
    CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    RuleGroup,
    RuleSpec,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules import (
    temporal_selection,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.cluster import (
    CLUSTER_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.diary import (
    DIARY_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.gan_shorthand import (
    GAN_SHORTHAND_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.rate import (
    PORTABLE_RATE_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.seizure_free import (
    SEIZURE_FREE_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    BENCHMARK_REPAIR_RULES,
)

DEFAULT_CSV_PATH = Path("experiments/gan2026_rule_ownership_matrix_2026-06-02.csv")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_rule_ownership_audit_2026-06-02.md")


@dataclass(frozen=True)
class OwnershipRow:
    rule_id: str
    group: str
    portability: str
    current_module: str
    current_prediction_effect: str
    proposed_owner: str
    prompt_instruction_status: str
    deterministic_adapter_status: str
    ablation_switch: str
    target_failure_rows: str
    claim_language_constraint: str
    notes: str


@dataclass(frozen=True)
class Registry:
    specs: tuple[RuleSpec, ...]
    module: str


REGISTRIES: tuple[Registry, ...] = (
    Registry(PORTABLE_RATE_RULES, "deterministic.rules.rate"),
    Registry(CLUSTER_RULES, "deterministic.rules.cluster"),
    Registry(DIARY_RULES, "deterministic.rules.diary"),
    Registry(SEIZURE_FREE_RULES, "deterministic.rules.seizure_free"),
    Registry(GAN_SHORTHAND_RULES, "deterministic.rules.gan_shorthand"),
    Registry(
        temporal_selection.TEMPORAL_SELECTION_RULES,
        "deterministic.rules.temporal_selection",
    ),
    Registry(BENCHMARK_REPAIR_RULES, "contract.benchmark_prediction_repair"),
    Registry(CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES, "contract.gold_policy"),
)


POSTPROCESSING_ADAPTER_ROWS: tuple[OwnershipRow, ...] = (
    OwnershipRow(
        rule_id="adapter.label_parser",
        group="label_parser",
        portability="benchmark_format",
        current_module="contract.label_parser",
        current_prediction_effect="Parses scorer-facing labels into semantic kind and rates.",
        proposed_owner="deterministic_extraction_or_adapter",
        prompt_instruction_status=(
            "Do not prompt-train parser grammar except in explicit LLM-owned-rendering smokes."
        ),
        deterministic_adapter_status="Keep as scorer contract and format validator.",
        ablation_switch="repair_mode/raw vs strict parser layers",
        target_failure_rows=(
            "parser-incompatible raw labels across LLM-heavy and typed-adapter smokes"
        ),
        claim_language_constraint="Parser success is format compatibility, not clinical reasoning.",
        notes="Stable benchmark contract; changing it is a scoring/data-contract change.",
    ),
    OwnershipRow(
        rule_id="adapter.schema_repair_aliases",
        group="schema_repair",
        portability="benchmark_format",
        current_module="contract.schema_repair",
        current_prediction_effect="Repairs aliases and schema-compatible field variants.",
        proposed_owner="deterministic_extraction_or_adapter",
        prompt_instruction_status=(
            "Model should be asked for typed fields, but alias repair remains "
            "allowed format repair."
        ),
        deterministic_adapter_status="Keep as format-only repair.",
        ablation_switch="strict/raw/schema-replay score layers",
        target_failure_rows="schema enum drift and alias-only failures",
        claim_language_constraint=(
            "Allowed only when it does not change selected clinical fact or semantic kind."
        ),
        notes="Semantic repair must stay outside this bucket.",
    ),
    OwnershipRow(
        rule_id="adapter.selected_evidence_derivation",
        group="selected_evidence_arithmetic",
        portability="seizure_frequency",
        current_module="selected_evidence.selected_evidence_derivation",
        current_prediction_effect="Derives a Gan-compatible label from selected evidence text.",
        proposed_owner="deterministic_extraction_or_adapter",
        prompt_instruction_status=(
            "Model owns evidence/fact selection; prompt for exact evidence and "
            "operands rather than parser-ready Gan syntax."
        ),
        deterministic_adapter_status=(
            "Allowed in primary LLM-heavy score layer when it computes from "
            "model-selected evidence."
        ),
        ablation_switch="raw vs selected-evidence-arithmetic repair modes",
        target_failure_rows="LLM-heavy v1/v2 selected-evidence arithmetic gaps",
        claim_language_constraint=(
            "Still LLM-heavy when deterministic code only renders or computes from "
            "model-selected facts; hybrid if it selects a different clinical fact."
        ),
        notes="Preferred way to reduce model load while preserving clinical-selection attribution.",
    ),
    OwnershipRow(
        rule_id="adapter.selected_evidence_cluster",
        group="cluster_arithmetic",
        portability="seizure_frequency",
        current_module="selected_evidence.selected_evidence_cluster",
        current_prediction_effect=(
            "Converts selected cluster evidence into cluster cadence and per-cluster labels."
        ),
        proposed_owner="deterministic_extraction_or_adapter",
        prompt_instruction_status=(
            "Model owns ambiguous cluster evidence selection; deterministic code "
            "may render selected operands."
        ),
        deterministic_adapter_status=(
            "Allowed as benchmark/arithmetic adapter when cluster operands are model-selected."
        ),
        ablation_switch="selected-evidence-arithmetic component ablation",
        target_failure_rows="row 187 and cluster-cadence/flattening failures",
        claim_language_constraint=(
            "LLM-heavy if the model selected the cluster fact/operands; hybrid if "
            "deterministic code chose cadence, size, or competing burden."
        ),
        notes="Cluster syntax and clinical burden are often separable decisions.",
    ),
    OwnershipRow(
        rule_id="adapter.selected_evidence_monthly_diary",
        group="diary_log_aggregation",
        portability="gan2026_specific",
        current_module="selected_evidence.selected_evidence_monthly_diary",
        current_prediction_effect=(
            "Aggregates selected month-log evidence into a total-window label."
        ),
        proposed_owner="research_comparison",
        prompt_instruction_status="Use only as a targeted instruction or operand-trace test.",
        deterministic_adapter_status=(
            "Keep as side-car; do not silently replace primary LLM labels."
        ),
        ablation_switch="selected-evidence-arithmetic component ablation",
        target_failure_rows=(
            "monthly diary/log rows from replacement ablation and claim-table failures"
        ),
        claim_language_constraint=(
            "Treat gains as dataset-pattern or side-car gains until cross-template evidence exists."
        ),
        notes="High validation utility but likely local-template sensitive.",
    ),
    OwnershipRow(
        rule_id="adapter.selected_evidence_window_counts",
        group="date_duration_utilities",
        portability="seizure_frequency",
        current_module="selected_evidence.selected_evidence_window",
        current_prediction_effect="Sums or formats selected counts over explicit windows.",
        proposed_owner="deterministic_extraction_or_adapter",
        prompt_instruction_status="Model should emit selected operands and arithmetic trace.",
        deterministic_adapter_status=(
            "Allowed in primary LLM-heavy score layer when operands are model-selected."
        ),
        ablation_switch="selected-evidence-arithmetic component ablation",
        target_failure_rows="single-total-window and compact interval rendering failures",
        claim_language_constraint=(
            "Deterministic arithmetic does not break LLM-heavy attribution if "
            "clinical selection is model-owned."
        ),
        notes=(
            "Mechanical when evidence selection is already correct; semantic when "
            "it chooses the window."
        ),
    ),
    OwnershipRow(
        rule_id="adapter.state_graph_projection_v0",
        group="temporal_selection",
        portability="seizure_frequency",
        current_module="state_graph.projection",
        current_prediction_effect="Projects graph nodes to one Gan-compatible final label.",
        proposed_owner="hybrid_side_car",
        prompt_instruction_status=(
            "Clinical selection policy should be explicit in model instructions "
            "or adjudicator prompts."
        ),
        deterministic_adapter_status=(
            "Allowed for named hybrid runs; diagnostic only for LLM-heavy primary score layers."
        ),
        ablation_switch="projection policy variant and graph projection ablations",
        target_failure_rows="projection/arbitration miss-only rows and competing-state hard slices",
        claim_language_constraint=(
            "Deterministic projection is hybrid clinical selection in LLM-heavy "
            "contexts, not formatting."
        ),
        notes="Useful diagnostic substrate; not production policy by default.",
    ),
    OwnershipRow(
        rule_id="adapter.month_bucket_duration_selection_graph_gated_v2",
        group="seizure_free_no_event_assertions",
        portability="gan2026_specific",
        current_module="artifact_analysis.month_bucket_duration_selection_ablation",
        current_prediction_effect=(
            "Selects enriched seizure-free duration labels when graph metadata allows it."
        ),
        proposed_owner="research_comparison",
        prompt_instruction_status=(
            "Use findings to design model duration-selection instructions, not "
            "as silent replacement."
        ),
        deterministic_adapter_status="Diagnostic only; do not promote without a written decision.",
        ablation_switch="month-bucket duration-selection v0/v1/graph-gated-v2",
        target_failure_rows="18 enriched duration target rows and 232 broad-regression rows",
        claim_language_constraint="Validation-only diagnostic; not benchmark or production policy.",
        notes="Strong target correction with graph gate, but deliberately not a final policy.",
    ),
)


def build_ownership_rows() -> list[OwnershipRow]:
    rows: list[OwnershipRow] = []
    for registry in REGISTRIES:
        for spec in registry.specs:
            rows.append(_row_from_spec(spec, registry.module))
    rows.extend(POSTPROCESSING_ADAPTER_ROWS)
    return sorted(rows, key=lambda row: (row.group, row.rule_id))


def write_ownership_csv(rows: Iterable[OwnershipRow], path: Path = DEFAULT_CSV_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = tuple(OwnershipRow.__dataclass_fields__)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def write_ownership_report(
    rows: list[OwnershipRow],
    path: Path = DEFAULT_REPORT_PATH,
    *,
    csv_path: Path = DEFAULT_CSV_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    group_counts = Counter(row.group for row in rows)
    owner_counts = Counter(row.proposed_owner for row in rows)
    lines = [
        "# Gan 2026 Deterministic Rule Ownership Audit",
        "",
        "Date: 2026-06-02",
        "",
        "This is Workstream B from the hybrid LLM/deterministic boundary report. "
        "It inventories deterministic rules and post-processing adapters and assigns "
        "component ownership for future LLM-heavy and hybrid experiments. It is a "
        "validation-development governance artifact, not a benchmark claim.",
        "",
        f"- Durable matrix: `{csv_path}`",
        f"- Matrix rows: {len(rows)}",
        "- Split policy: no new data run; no test inspection; uses registry and saved "
        "experiment evidence only.",
        "- Governing decision: "
        "`docs/decisions/0007-llm-heavy-clinical-selection-deterministic-adapters.md`",
        "",
        "## Ownership Counts",
        "",
        "| Proposed owner | Rows |",
        "| --- | ---: |",
    ]
    for owner, count in sorted(owner_counts.items()):
        lines.append(f"| `{owner}` | {count} |")
    lines.extend(["", "## Rule Group Coverage", "", "| Group | Rows |", "| --- | ---: |"])
    for group, count in sorted(group_counts.items()):
        lines.append(f"| `{group}` | {count} |")
    lines.extend(
        [
            "",
            "## Decisions",
            "",
            "1. LLM-heavy runs do not need the raw model output to contain a "
            "parser-ready Gan label. The model owns clinical selection: the relevant "
            "fact, evidence, temporal state, competing-event choice, and operands.",
            "2. Deterministic code should intentionally own mechanical work that frees "
            "model capacity: parser-ready formatting, unit grammar, arithmetic from "
            "model-selected operands, seizure-free duration calculation, cluster "
            "syntax rendering, and stable Gan benchmark conventions.",
            "3. Semantic arithmetic is allowed in the primary LLM-heavy score layer "
            "when it computes from model-selected evidence or operands. If "
            "deterministic code selects a different clinical fact, the run becomes "
            "hybrid.",
            "4. Deterministic projection or temporal selection among multiple clinical "
            "facts is hybrid behavior. It is allowed in named hybrid implementations "
            "but is not an LLM-heavy primary answer.",
            "5. Synthetic diary/log aggregation remains research-only until "
            "portability is shown outside Gan-style notes, even when it is useful on "
            "validation rows.",
            "6. Benchmark repair and clean gold-normalization policy stay deterministic "
            "adapters. `bimonthly`/`biweekly`-style Gan conventions should be applied "
            "automatically once the model selects the relevant evidence.",
            "",
            "## Hard Follow-Up Decisions",
            "",
            "- Cluster rendering: deterministic cluster syntax/rendering is acceptable "
            "when operands are model-selected; require explicit hybrid claim language "
            "when deterministic code selects burden, cadence, or which cluster fact "
            "wins.",
            "- `adapter.month_bucket_duration_selection_graph_gated_v2`: retain as a "
            "diagnostic research comparison. Promotion would require a separate "
            "decision note because it appears to select among graph-derived states, "
            "not merely compute duration from model-selected evidence.",
            "- Synthetic diary templates: use as hard-slice or ablation rows, not as "
            "general clinical extraction evidence until evaluated outside Gan-style "
            "letter templates.",
            "",
            "## Claim-Language Rules",
            "",
            "- `LLM-heavy`: the model selected the clinical fact/evidence/operands; "
            "deterministic code may render the final Gan-compatible label.",
            "- `LLM-owned clinical selection`: the raw model output identifies the "
            "selected clinical fact, evidence, temporal state, and operands used by "
            "the deterministic adapter.",
            "- `Hybrid`: deterministic and model components both contribute semantic "
            "selection, candidate choice, graph projection, or competing-fact "
            "arbitration.",
            "- `Benchmark adapter`: deterministic code maps an already selected fact to "
            "Gan-compatible syntax or an arbitrary gold-label convention.",
            "- `Research-only comparison`: deterministic logic is useful on Gan-style "
            "patterns but lacks enough portability evidence for default LLM-heavy "
            "scoring.",
            "",
            "## Matrix Preview",
            "",
            "| Rule ID | Group | Owner | Module |",
            "| --- | --- | --- | --- |",
        ]
    )
    preview_rows = rows[:20]
    for row in preview_rows:
        lines.append(
            f"| `{row.rule_id}` | `{row.group}` | `{row.proposed_owner}` | `{row.current_module}` |"
        )
    lines.append("")
    lines.append(
        f"The CSV contains all {len(rows)} rows, including extraction rules, benchmark "
        "repair steps, clean gold-policy rules, selected-evidence adapters, and graph "
        "projection diagnostics."
    )
    path.write_text("\n".join(lines) + "\n")


def _row_from_spec(spec: RuleSpec, module: str) -> OwnershipRow:
    policy = _policy_for_spec(spec)
    return OwnershipRow(
        rule_id=spec.rule_id,
        group=str(spec.group),
        portability=str(spec.portability),
        current_module=module,
        current_prediction_effect=spec.description,
        proposed_owner=policy["proposed_owner"],
        prompt_instruction_status=policy["prompt_instruction_status"],
        deterministic_adapter_status=policy["deterministic_adapter_status"],
        ablation_switch=_ablation_switch(spec),
        target_failure_rows=policy["target_failure_rows"],
        claim_language_constraint=policy["claim_language_constraint"],
        notes=policy["notes"],
    )


def _policy_for_spec(spec: RuleSpec) -> Mapping[str, str]:
    if spec.group is RuleGroup.PORTABLE_RATE_EXPRESSIONS:
        return _policy(
            owner="deterministic_extraction_or_adapter",
            prompt="Teach as a source-reading principle in LLM-owned extraction prompts.",
            adapter=(
                "Keep deterministic extraction for rules-only and as format/arithmetic adapter."
            ),
            target="direct rates, intervals, compact intervals, vague quantities",
            claim="Deterministic rate replacement makes the scored layer hybrid or adapter-owned.",
            notes="Portable seizure-frequency expression; high value as comparator.",
        )
    if spec.group is RuleGroup.CLUSTER_ARITHMETIC:
        return _policy(
            owner="hybrid_side_car",
            prompt="Teach clinical cluster interpretation and operand exposure.",
            adapter="Keep deterministic cluster arithmetic as side-car unless explicitly promoted.",
            target="cluster syntax, cadence flattening, events-per-cluster rows",
            claim=(
                "Cluster corrections are not LLM-owned unless raw output selects and renders them."
            ),
            notes="Clinical burden and Gan syntax must remain separately attributed.",
        )
    if spec.group is RuleGroup.DIARY_LOG_AGGREGATION:
        owner = (
            "research_comparison"
            if spec.rule_id.startswith("diary.monthly_summary.")
            else "hybrid_side_car"
        )
        notes = (
            "Synthetic monthly-summary template; keep as research-only until generalized."
            if owner == "research_comparison"
            else "Diary arithmetic side-car when evidence selection is already fixed."
        )
        return _policy(
            owner=owner,
            prompt="Ask model for exact diary evidence and operands before aggregation.",
            adapter="Use deterministic aggregation as named side-car or ablation condition.",
            target="monthly diary/log aggregation and sparse date-list failures",
            claim="Aggregation gains are side-car or research-only unless raw model owns totals.",
            notes=notes,
        )
    if spec.group is RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS:
        owner = (
            "deterministic_extraction_or_adapter"
            if spec.rule_id
            in {
                "seizure_free.since_date",
                "seizure_free.absence_for_duration",
                "seizure_free.no_events_for_duration",
                "seizure_free.duration_status",
                "seizure_free.one_and_half_years",
                "seizure_free.last_epileptic_event",
            }
            else "model_instruction"
        )
        return _policy(
            owner=owner,
            prompt="Teach current/no-event assertion, temporality, and duration selection.",
            adapter=(
                "Use deterministic date/duration arithmetic once the model selects "
                "the seizure-free or last-event evidence."
            ),
            target="seizure-free duration, no-current-event, and no-reference boundary rows",
            claim=(
                "Date/duration conversion is adapter-owned; deterministic no-event "
                "clinical selection is hybrid if it chooses the final fact."
            ),
            notes="Boundary between mechanical duration and clinical currentness is the key risk.",
        )
    if spec.group is RuleGroup.TEMPORAL_SELECTION:
        return _policy(
            owner="model_instruction",
            prompt=(
                "Put clinical currentness and conflict-resolution principles in "
                "prompts/adjudicators."
            ),
            adapter="Keep deterministic selection as comparator/projection policy only.",
            target="current-vs-historical, competing frequency, trigger-conditioned rows",
            claim="Deterministic final selection owns semantic behavior and must be called hybrid.",
            notes="Selection rules are clinical policy, not formatting.",
        )
    if spec.group is RuleGroup.GAN_SHORTHAND:
        return _policy(
            owner="research_comparison",
            prompt=(
                "Use only in targeted shorthand smokes if the model is expected to own shorthand."
            ),
            adapter="Keep deterministic shorthand expansion as Gan-specific ablation condition.",
            target="TC/sz/abs compact shorthand and q-interval rows",
            claim="Gan shorthand gains are dataset-specific until externalized.",
            notes="Useful for Gan rows but weak portability by design.",
        )
    if spec.group is RuleGroup.BENCHMARK_REPAIR:
        return _policy(
            owner="deterministic_extraction_or_adapter",
            prompt=(
                "Do not spend model capacity on parser grammar except in explicit "
                "comparator smokes."
            ),
            adapter="Keep as explicit benchmark-format repair layer.",
            target="parser grammar, slash/per, units, cluster syntax, seizure-free label format",
            claim="Benchmark repair is format compatibility, not clinical extraction.",
            notes="Report raw/strict/repaired layers separately.",
        )
    if spec.group is RuleGroup.GOLD_NORMALIZATION_POLICY:
        return _policy(
            owner="deterministic_extraction_or_adapter",
            prompt="Do not prompt-train arbitrary Gan conventions by default.",
            adapter=(
                "Apply stable Gan conventions automatically once the model selects "
                "the relevant evidence."
            ),
            target="bimonthly, vague weekday cadence, cluster-name stripping, single total windows",
            claim="Gold-policy conversion is benchmark convention, not model clinical reasoning.",
            notes="Keep documented, ablatable, and separated from clinical selection.",
        )
    raise ValueError(f"Unhandled rule group: {spec.group}")


def _policy(
    *,
    owner: str,
    prompt: str,
    adapter: str,
    target: str,
    claim: str,
    notes: str,
) -> Mapping[str, str]:
    return {
        "proposed_owner": owner,
        "prompt_instruction_status": prompt,
        "deterministic_adapter_status": adapter,
        "target_failure_rows": target,
        "claim_language_constraint": claim,
        "notes": notes,
    }


def _ablation_switch(spec: RuleSpec) -> str:
    if spec.group is RuleGroup.BENCHMARK_REPAIR:
        return "repair_mode raw/strict/clean/benchmark-aligned"
    if spec.group is RuleGroup.GOLD_NORMALIZATION_POLICY:
        return f"gold policy rule_id {spec.rule_id}"
    return f"AblationConfig enabled_groups={spec.group}; disabled_rule_ids={spec.rule_id}"


def main() -> None:
    rows = build_ownership_rows()
    write_ownership_csv(rows)
    write_ownership_report(rows)


if __name__ == "__main__":
    main()
