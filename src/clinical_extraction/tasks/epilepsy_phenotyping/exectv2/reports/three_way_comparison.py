"""Three-way architecture comparison report for ExECTv2 SeizureFrequency.

Renders one shared table — rules / llm_only / hybrid — over the universally
meaningful score axes (``phrase_only``, ``sf_semantic``, ``sf_benchmark``;
per-item and per-letter F1), with a model-parameterized title, against the
published SF benchmark cell (0.66 per item / 0.68 per letter; Fonferko-Shadrach
2024 Table 1 — the benchmark's hardest entity).

Provenance is deliberately mixed, and the report says so rather than hiding it
(the Gan 2026 asymmetry-handling lesson, satellite 05 §1):

- The **llm_only** and **hybrid** rows are read from the run registry — the
  durable index where every live run is recorded (satellite 05 §3).
- The **rules** row is computed **live**. The deterministic SF pipeline runs the
  full dev split in a sub-second pass with no per-record cost and is deliberately
  not registered (satellite 05 §5a), so the report recomputes it on demand and it
  is always current with the rule set in the tree.

Partial runs (fewer letters than the full dev split) are excluded from the
comparison body — a 50-letter prefix is not comparable to a 140-letter run — and
listed separately under a coverage note.

The structure is entity-agnostic: Phase 6 extends it to all nine entities by
parameterizing ``entity`` and the per-entity match configs; only SF is wired
today.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.pipeline import (
    run_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    SF_BENCHMARK,
    SF_SEMANTIC,
    score_entity,
)

DEFAULT_REGISTRY_PATH = Path("experiments/registry.jsonl")

# pipeline_family → architecture family, for correct grouping in the report
# (satellite 05 §1). The rules family is computed live and never appears in the
# registry; the rest are read from it.
ARCHITECTURE_FAMILY: Mapping[str, str] = {
    "exectv2_deterministic": "rules",
    "exectv2_llm_only_single_pass": "llm_only",
    "exectv2_llm_only_per_entity": "llm_only",
    "exectv2_llm_only_clinical_findings": "llm_only",
    "exectv2_hybrid": "hybrid",
}
FAMILY_ORDER: tuple[str, ...] = ("rules", "llm_only", "hybrid")

# Short config label per pipeline_family, for the second table column.
_CONFIG_LABEL: Mapping[str, str] = {
    "exectv2_deterministic": "deterministic_sf",
    "exectv2_llm_only_single_pass": "single_pass",
    "exectv2_llm_only_per_entity": "per_entity",
    "exectv2_llm_only_clinical_findings": "clinical_findings",
    "exectv2_hybrid": "candidate_assessment",
}

# Published SF cell (Fonferko-Shadrach 2024, Table 1).
SF_BENCHMARK_PER_ITEM_F1 = 0.66
SF_BENCHMARK_PER_LETTER_F1 = 0.68

# The six universally-meaningful score axes shared by every family's run record.
_METRIC_KEYS: tuple[str, ...] = (
    "phrase_only_per_item_f1",
    "phrase_only_per_letter_f1",
    "sf_semantic_per_item_f1",
    "sf_semantic_per_letter_f1",
    "sf_benchmark_per_item_f1",
    "sf_benchmark_per_letter_f1",
)


@dataclass(frozen=True)
class ComparisonRow:
    """One architecture's dev-split read on the shared SF score axes."""

    family: str
    config: str
    model: str
    n_letters: int
    metrics: Mapping[str, float] = field(default_factory=dict)
    provenance: str = ""
    partial: bool = False


def compute_rules_row(split: str = "dev") -> ComparisonRow:
    """Score the deterministic SF pipeline on ``split`` live (sub-second pass)."""

    gold_letters = load_letters_for_split(split)
    predicted = run_on_letters(gold_letters)
    pred_letters = [
        to_exect_letter(p, note_text=g.note_text)
        for p, g in zip(predicted, gold_letters, strict=True)
    ]

    def f1(config: object) -> tuple[float, float]:
        score = score_entity(
            gold_letters,
            pred_letters,
            SEIZURE_FREQUENCY.name,
            config,  # type: ignore[arg-type]
        )
        return round(score.per_item.f1, 3), round(score.per_letter.f1, 3)

    po_i, po_l = f1(PHRASE_ONLY)
    ss_i, ss_l = f1(SF_SEMANTIC)
    sb_i, sb_l = f1(SF_BENCHMARK)
    metrics = {
        "phrase_only_per_item_f1": po_i,
        "phrase_only_per_letter_f1": po_l,
        "sf_semantic_per_item_f1": ss_i,
        "sf_semantic_per_letter_f1": ss_l,
        "sf_benchmark_per_item_f1": sb_i,
        "sf_benchmark_per_letter_f1": sb_l,
    }
    return ComparisonRow(
        family="rules",
        config=_CONFIG_LABEL["exectv2_deterministic"],
        model="(model-independent)",
        n_letters=len(gold_letters),
        metrics=metrics,
        provenance="live (deterministic pipeline)",
    )


def _load_exectv2_rows(registry_path: Path) -> list[dict]:
    """Read ExECTv2 architecture rows from the registry as plain records.

    The registry is read as raw JSON lines rather than through the Gan 2026
    ``RunRegistryEntry`` parser: ExECTv2 rows use task-specific ``decision`` /
    ``replay_status`` vocabulary that the Gan schema's enums reject.
    """

    rows: list[dict] = []
    for line in registry_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        if ARCHITECTURE_FAMILY.get(str(record.get("pipeline_family", ""))) is not None:
            rows.append(record)
    return rows


def build_comparison_rows(
    model: str,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    split: str = "dev",
) -> list[ComparisonRow]:
    """Build the ordered comparison rows for ``model`` on ``split``.

    The rules row (model-independent) is always first, computed live. The
    llm_only and hybrid rows are the registry runs for this exact model and
    split, grouped by family. Partial runs are flagged, not dropped — the caller
    decides how to surface them.
    """

    rules_row = compute_rules_row(split)
    full_dev_size = rules_row.n_letters
    rows: list[ComparisonRow] = [rules_row]

    for record in _load_exectv2_rows(registry_path):
        if record.get("model") != model or record.get("split") != split:
            continue
        family = record["pipeline_family"]
        if family == "exectv2_deterministic":
            continue  # rules is the live row, never the registry
        metrics_src = record.get("primary_metrics", {})
        metrics = {
            key: float(metrics_src[key]) for key in _METRIC_KEYS if metrics_src.get(key) is not None
        }
        n_letters = int(record.get("row_count", 0))
        rows.append(
            ComparisonRow(
                family=ARCHITECTURE_FAMILY[family],
                config=_CONFIG_LABEL.get(family, family),
                model=model,
                n_letters=n_letters,
                metrics=metrics,
                provenance=f"registry:{record.get('run_id', '')}",
                partial=n_letters < full_dev_size,
            )
        )

    rows.sort(key=lambda r: (FAMILY_ORDER.index(r.family), r.config))
    return rows


def _fmt(row: ComparisonRow, key: str) -> str:
    value = row.metrics.get(key)
    return f"{value:.3f}" if value is not None else "—"


_HEADER = (
    "| Family | Config | Letters | phrase per-item | phrase per-letter "
    "| semantic per-item | semantic per-letter | benchmark per-item "
    "| benchmark per-letter |"
)
_DIVIDER = "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"


def render_comparison_markdown(
    model: str,
    rows: Sequence[ComparisonRow],
    split: str = "dev",
    *,
    generated_on: str | None = None,
) -> str:
    """Render the three-way comparison as a Markdown report string."""

    generated_on = generated_on or date.today().isoformat()
    body_rows = [r for r in rows if not r.partial]
    partial_rows = [r for r in rows if r.partial]
    families_present = {r.family for r in body_rows}
    missing = [f for f in FAMILY_ORDER if f not in families_present]

    lines: list[str] = [
        f"# ExECTv2 Three-Way Architecture Comparison — SeizureFrequency ({model}, {split})",
        "",
        f"- Generated: `{generated_on}`",
        f"- Model: `{model}` (rules family is model-independent)",
        f"- Split: `{split}`",
        "- Entity: SeizureFrequency (the benchmark's hardest cell; Table 1, "
        "Fonferko-Shadrach 2024)",
        "- Match axes: `phrase_only` (phrase recall), `sf_semantic` "
        "(guideline-aligned attributes), `sf_benchmark` (keeps CUI)",
        "",
        "## Scores (F1)",
        "",
        _HEADER,
        _DIVIDER,
    ]

    for row in body_rows:
        lines.append(
            f"| {row.family} | `{row.config}` | {row.n_letters} "
            f"| {_fmt(row, 'phrase_only_per_item_f1')} "
            f"| {_fmt(row, 'phrase_only_per_letter_f1')} "
            f"| {_fmt(row, 'sf_semantic_per_item_f1')} "
            f"| {_fmt(row, 'sf_semantic_per_letter_f1')} "
            f"| {_fmt(row, 'sf_benchmark_per_item_f1')} "
            f"| {_fmt(row, 'sf_benchmark_per_letter_f1')} |"
        )

    lines.append(
        f"| **benchmark target** | published SF | 200 | — | — | — | — "
        f"| **{SF_BENCHMARK_PER_ITEM_F1:.3f}** | **{SF_BENCHMARK_PER_LETTER_F1:.3f}** |"
    )

    lines.extend(
        [
            "",
            "## Provenance",
            "",
            "- The **rules** row is computed live from the deterministic pipeline "
            "in the tree (sub-second dev pass, no per-record cost; deliberately "
            "unregistered per satellite 05 §5a).",
            "- The **llm_only** and **hybrid** rows are the registered live runs "
            "for this model and split.",
        ]
    )
    for row in body_rows:
        if row.provenance.startswith("registry:"):
            lines.append(f"  - `{row.config}` ← `{row.provenance.split(':', 1)[1]}`")

    if missing:
        lines.extend(
            [
                "",
                "## Coverage gaps",
                "",
                f"No full-`{split}` run for this model in: "
                + ", ".join(f"**{f}**" for f in missing)
                + ". Generate and register one to complete the comparison.",
            ]
        )

    if partial_rows:
        lines.extend(["", "## Excluded partial runs", ""])
        for row in partial_rows:
            lines.append(
                f"- {row.family} `{row.config}` — {row.n_letters} letters "
                f"(< full dev {body_rows[0].n_letters if body_rows else '?'}); "
                f"`{row.provenance}`. Not comparison-grade."
            )

    return "\n".join(lines) + "\n"


def write_comparison_report(
    model: str,
    out_path: Path,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    split: str = "dev",
    *,
    generated_on: str | None = None,
) -> Path:
    """Build and write the three-way comparison report for ``model``."""

    rows = build_comparison_rows(model, registry_path, split)
    markdown = render_comparison_markdown(model, rows, split, generated_on=generated_on)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(markdown, encoding="utf-8")
    return out_path
