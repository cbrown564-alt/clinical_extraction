"""Generate the 4 family ceiling dossiers straight from the ledger. Never hand-edit the output.

Deterministic, zero-LLM, idempotent (run twice -> byte-identical output). Reads
``experiments/gold_case_ledger_{family}.jsonl`` (one per ``KEY_FAMILIES`` entry),
``experiments/hypothesis_registry.jsonl``, and ``experiments/registry.jsonl``
(for F1 citations), and writes
``docs/canon/workstreams/{FAMILY}_CANONICAL_LEDGER_CANON.md``. Re-run any time
new adjudication lands -- the whole point of this script existing is that the
dossier can never silently drift from the ledger it's generated from, unlike a
hand-authored canon summary.

Usage: uv run python experiments/exectv2_ledger/render_dossier.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

_EXPERIMENTS_DIR = Path(__file__).resolve().parents[1]
if str(_EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_EXPERIMENTS_DIR))

from exectv2_ledger.hypothesis_registry import load_hypothesis_registry  # noqa: E402
from exectv2_ledger.mechanism import Mechanism, Verdict  # noqa: E402
from exectv2_ledger.schema import GoldCaseRow, load_gold_case_ledger  # noqa: E402

ROOT = _EXPERIMENTS_DIR.parent
OUT_DIR = ROOT / "docs" / "canon" / "workstreams"
HYPOTHESIS_REGISTRY = _EXPERIMENTS_DIR / "hypothesis_registry.jsonl"
RUN_REGISTRY = _EXPERIMENTS_DIR / "registry.jsonl"

#: (family, ledger filename, substrate dir relative to docs/research/error_analysis/, or None
#: if that family's substrate is ephemeral local scratch (not durably tracked).
FAMILIES: list[tuple[str, str, str | None]] = [
    ("Diagnosis", "gold_case_ledger_diagnosis.jsonl", None),
    ("SeizureFrequency", "gold_case_ledger_seizurefrequency.jsonl", None),
    ("Prescription", "gold_case_ledger_prescription.jsonl", "rx_canonical"),
    ("Investigations", "gold_case_ledger_investigations.jsonl", "inv_canonical"),
]

_MECHANISM_LABEL = {
    Mechanism.GENUINE_MODEL_ERROR.value: "Genuine model error",
    Mechanism.GOLD_MULTIPLICITY_CONSOLIDATION.value: "Gold multiplicity / consolidation",
    Mechanism.GOLD_ORTHOGRAPHIC_TYPO.value: "Gold/letter orthographic typo",
    Mechanism.GOLD_UNDER_ANNOTATION.value: "Gold under-annotation",
    Mechanism.SCORER_MECHANICS_ARTIFACT.value: "Scorer mechanics artifact",
    Mechanism.IAA_AMBIGUITY.value: "IAA ambiguity",
    Mechanism.UNADJUDICATED.value: "Unadjudicated",
}
# Fixed report order: genuine error first, then gold-side mechanisms, then
# measurement/ambiguity, then the honesty-instrument bucket last.
_MECHANISM_ORDER = [
    Mechanism.GENUINE_MODEL_ERROR.value,
    Mechanism.GOLD_MULTIPLICITY_CONSOLIDATION.value,
    Mechanism.GOLD_ORTHOGRAPHIC_TYPO.value,
    Mechanism.GOLD_UNDER_ANNOTATION.value,
    Mechanism.SCORER_MECHANICS_ARTIFACT.value,
    Mechanism.IAA_AMBIGUITY.value,
    Mechanism.UNADJUDICATED.value,
]


def _load_registry_metrics(run_id: str) -> dict[str, float | int | str | None] | None:
    if not RUN_REGISTRY.exists():
        return None
    for line in RUN_REGISTRY.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("run_id") == run_id:
            return rec.get("primary_metrics", {})
    return None


def _f1_ladder_section(family: str, run_ids: set[str]) -> list[str]:
    lines = ["## F1 ladder (live-queried from `experiments/registry.jsonl`)", ""]
    if not run_ids:
        lines.append("No run_id recorded on any ledger row.")
        return lines
    lines.append("| run_id | key | value |")
    lines.append("| --- | --- | --- |")
    for run_id in sorted(run_ids):
        metrics = _load_registry_metrics(run_id)
        if metrics is None:
            lines.append(f"| `{run_id}` | (not found in registry) | - |")
            continue
        family_key = f"clinical_headline_{_snake(family)}_f1"
        candidates = [family_key, "clinical_headline_f1", "state_profile_f1"]
        shown = False
        for key in candidates:
            if key in metrics:
                lines.append(f"| `{run_id}` | `{key}` | {metrics[key]} |")
                shown = True
        if not shown:
            lines.append(f"| `{run_id}` | (no clinical_headline/state_profile key) | - |")
    if len(run_ids) > 1:
        lines.append("")
        lines.append(
            "**Note:** this family's ledger rows come from more than one run_id -- the "
            "canonical row analyses were not all run against the same underlying prediction "
            "set. Reported here plainly rather than silently picking one."
        )
    return lines


def _snake(family: str) -> str:
    out = []
    for i, ch in enumerate(family):
        if ch.isupper() and i > 0:
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


def _mechanism_table(rows: list[GoldCaseRow]) -> list[str]:
    counts = Counter(row.mechanism for row in rows)
    n = len(rows)
    lines = ["## Mechanism breakdown (every adjudicated disagreement, this family)", ""]
    lines.append("| Mechanism | n | % of disagreements |")
    lines.append("| --- | ---: | ---: |")
    for mechanism in _MECHANISM_ORDER:
        count = counts.get(mechanism, 0)
        if count == 0 and mechanism == Mechanism.UNADJUDICATED.value:
            # Always show the honesty-instrument row, even at zero.
            pass
        elif count == 0:
            continue
        pct = f"{count / n:.1%}" if n else "-"
        lines.append(f"| {_MECHANISM_LABEL[mechanism]} | {count} | {pct} |")
    genuine = counts.get(Mechanism.GENUINE_MODEL_ERROR.value, 0)
    unadjudicated = counts.get(Mechanism.UNADJUDICATED.value, 0)
    lines += [
        "",
        f"**{genuine}/{n} = {genuine/n:.1%} of disagreements are genuine model error "
        f"(the rest are gold-quality or scorer-mechanics artifacts).**" if n else
        "No disagreements recorded.",
        "",
        f"**Unadjudicated: {unadjudicated}/{n}** -- this must be driven toward zero over "
        f"time; a nonzero count here means part of this family's F1 gap is still unexplained, "
        f"not that it's been checked and found genuine." if n else "",
    ]
    return lines


def _worst_offenders(rows: list[GoldCaseRow], substrate_dir: str | None, limit: int = 8) -> list[str]:
    genuine = [r for r in rows if r.mechanism == Mechanism.GENUINE_MODEL_ERROR.value]
    genuine_sorted = sorted(genuine, key=lambda r: r.row_id)[:limit]
    lines = [f"## Worked genuine-model-error examples (up to {limit})", ""]
    if not genuine_sorted:
        lines.append("None recorded.")
        return lines
    for row in genuine_sorted:
        key_desc = row.match_key
        if substrate_dir:
            link = f"`docs/research/error_analysis/{substrate_dir}/{row.letter_id}.md`"
        else:
            link = "(substrate not durably persisted -- local scratch; re-run the canonical row analysis script to regenerate)"
        reason = row.provenance.get("reason", "")
        lines.append(f"- **{row.letter_id}** ({row.disagreement_type}, key=`{key_desc}`): {link}")
        if reason:
            lines.append(f"  > {reason}")
    return lines


def _hypothesis_table(family: str) -> list[str]:
    entries = load_hypothesis_registry(HYPOTHESIS_REGISTRY)
    relevant = [e for e in entries if e.family in (family, "cross_family")]
    relevant.sort(key=lambda e: (e.date, e.hypothesis_id))
    lines = ["## Hypothesis history (from `experiments/hypothesis_registry.jsonl`)", ""]
    if not relevant:
        lines.append("None recorded for this family yet.")
        return lines
    lines.append("| Date | Hypothesis | Verdict | Doc |")
    lines.append("| --- | --- | --- | --- |")
    for entry in relevant:
        lines.append(f"| {entry.date} | {entry.statement} | **{entry.verdict}** | `{entry.predeclaration_doc}` |")
    return lines


def render_family(family: str, ledger_filename: str, substrate_dir: str | None) -> None:
    ledger_path = _EXPERIMENTS_DIR / ledger_filename
    rows = load_gold_case_ledger(ledger_path)
    run_ids = {row.run_id for row in rows}

    verdict_counts = Counter(row.verdict for row in rows)

    lines = [
        f"# {family} -- canonical gold case ledger",
        "",
        f"Generated by `experiments/exectv2_ledger/render_dossier.py` from "
        f"`experiments/{ledger_filename}` -- **do not hand-edit; re-run the script instead.**",
        "",
        f"{len(rows)} adjudicated `clinical_headline` disagreements "
        f"({verdict_counts.get(Verdict.GOLD_RIGHT.value, 0)} gold-right, "
        f"{verdict_counts.get(Verdict.MODEL_DEFENSIBLE.value, 0)} model-defensible, "
        f"{verdict_counts.get(Verdict.BOTH_DEFENSIBLE.value, 0)} both-defensible).",
        "",
    ]
    lines += _f1_ladder_section(family, run_ids)
    lines += [""]
    lines += _mechanism_table(rows)
    lines += [""]
    lines += _worst_offenders(rows, substrate_dir)
    lines += [""]
    lines += _hypothesis_table(family)
    lines += [
        "",
        "## Related reading",
        "",
        "- [`docs/canon/README.md`](../README.md) -- canon index",
        "- [`docs/canon/04_scoring.md`](../04_scoring.md) -- scoring surfaces & gold principles",
        "- [`docs/canon/05_ceilings_wall.md`](../05_ceilings_wall.md) -- the two ceiling mechanisms",
        "",
    ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{family.upper() if family.isupper() else _to_screaming_snake(family)}_CANONICAL_LEDGER_CANON.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{family}: {len(rows)} rows -> {out_path.relative_to(ROOT)}")


def _to_screaming_snake(family: str) -> str:
    return _snake(family).upper()


def main() -> None:
    for family, ledger_filename, substrate_dir in FAMILIES:
        render_family(family, ledger_filename, substrate_dir)


if __name__ == "__main__":
    main()
