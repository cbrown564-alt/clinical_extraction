"""Phase 2: same-raw ablation of the quarantined v0.42 projection families.

No model calls. Re-projects the GENUINE live LLM raw output (the v0.39 live
artifact) through the current v0.42 deterministic projection under several
quarantine-switch configurations, then scores every configuration on the same
25 dev letters:

  * baseline   = default quarantine (all named families OFF)
  * audit_all  = audit_only_projection_replay (all named families ON)
  * <family>   = exactly one quarantined family ON, all others OFF

For each configuration we read four surfaces from architecture_report:

  headline   = cui_projected_headline_scores  (lenient redefined key)
  benchmark  = cui_audit benchmark_f1_after_cui_projection (paper-comparable)
  Dx fidelity = Diagnosis.concept_negation companion (forgives Negation)
  SF fidelity = SeizureFrequency.active_rate_fidelity companion (forgives rate)

The marginal effect of each family is its config minus the baseline. A family
that moves benchmark and/or fidelity in the right direction is a KEEP candidate;
one that only moves the lenient headline, or hurts a fidelity companion, is a
CUT; one with no same-raw effect is INSUFFICIENT EVIDENCE on the source rows.

Why v0.39 live and not the v0.42 reproject artifact: the v0.40-v0.42 reproject
artifacts re-serialize an already-projected output into ``raw_output``, so they
are post-projection and cannot exercise the quarantine switches faithfully. The
v0.39 live ``raw_output`` is the untouched model output.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_target_indicators_single_call import (  # noqa: E501
    QUARANTINED_TARGET_PROJECTION_FAMILIES,
    _parse_target_extraction_json,
    audit_only_projection_replay_switches,
    to_predicted_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first_essential_evaluation import (  # noqa: E501
    architecture_report,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (  # noqa: E501
    TARGET_INDICATORS,
)

SOURCE = Path(
    "experiments/"
    "exectv2_target_indicators_single_call_v039_live_dev25_"
    "qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl"
)
OUT_JSON = Path("experiments/exectv2_phase2_family_ablation_dev25_20260620.json")
OUT_MD = Path(
    "docs/experiments/exectv2/key_entities/"
    "exectv2_phase2_family_ablation_same_raw_dev25_20260620.md"
)
OWNERSHIP = "llm_first_with_deterministic_normalization_projection"
DEFAULT_SOURCE_NOTE = (
    "v0.39 live raw_output is the genuine untouched model output; the "
    "v0.40-v0.42 reproject artifacts store post-projection raw and are "
    "unsuitable as the same-raw source."
)


def _load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _gold_letter(row: dict[str, Any], note: str) -> ExectLetter:
    return ExectLetter(
        letter_id=str(row["letter_id"]),
        note_text=note,
        annotations=tuple(
            ExectAnnotation(
                entity=str(m["entity"]),
                text=str(m.get("text", "")),
                attributes={str(k): str(v) for k, v in dict(m.get("attributes", {})).items()},
            )
            for m in row.get("gold_mentions", [])
            if str(m.get("entity")) in TARGET_INDICATORS
        ),
    )


def _score_config(
    rows: list[dict[str, Any]],
    note_by_id: dict[str, str],
    switches: dict[str, bool] | None,
) -> dict[str, Any]:
    """Re-project every row's live raw under one switch config and score it."""

    gold_letters: list[ExectLetter] = []
    pred_letters = []
    family_fires: Counter[str] = Counter()
    for row in rows:
        lid = str(row["letter_id"])
        note = note_by_id.get(lid, "")
        gold_letters.append(_gold_letter(row, note))
        extraction, _ = _parse_target_extraction_json(str(row.get("raw_output", "")))
        mentions = list(extraction.mentions) if extraction is not None else []
        predicted, warnings = to_predicted_letter(
            lid,
            mentions,
            note_text=note,
            projection_family_switches=switches,
        )
        pred_letters.append(predicted)
        for warning in warnings:
            for family in QUARANTINED_TARGET_PROJECTION_FAMILIES:
                if (
                    family in warning
                    and not warning.startswith("SeizureFrequency: quarantined_projection_family")
                    and "quarantined_projection_family" not in warning
                ):
                    family_fires[family] += 1

    report = architecture_report(
        name="phase2_family_ablation",
        ownership=OWNERSHIP,
        gold_letters=gold_letters,
        pred_letters=pred_letters,
        entities=TARGET_INDICATORS,
    )
    cr = report["clinical_recovery"]
    cui_audit = report["cui_audit"]
    fid = cr.get("fidelity_companions", {})
    return {
        "headline_overall": float(cr["cui_projected_overall"]["f1"]),
        "benchmark_overall": float(cui_audit["overall"]["benchmark_f1_after_cui_projection"]),
        "headline_by_indicator": {
            ind: float(cr["cui_projected_headline_scores"][ind]["f1"]) for ind in TARGET_INDICATORS
        },
        "benchmark_by_indicator": {
            ind: float(cui_audit["per_entity"][ind]["benchmark_f1"]) for ind in TARGET_INDICATORS
        },
        "dx_concept_negation_f1": (
            float(fid["Diagnosis"]["companion_f1"]) if "Diagnosis" in fid else None
        ),
        "sf_active_rate_fidelity_f1": (
            float(fid["SeizureFrequency"]["companion_f1"]) if "SeizureFrequency" in fid else None
        ),
        "family_fires": dict(family_fires),
    }


def _verdict(family: str, base: dict[str, Any], cfg: dict[str, Any]) -> tuple[str, str]:
    fires = cfg["family_fires"].get(family, 0)
    d_bench = cfg["benchmark_overall"] - base["benchmark_overall"]
    d_head = cfg["headline_overall"] - base["headline_overall"]

    def _d(key: str) -> float | None:
        if cfg[key] is None or base[key] is None:
            return None
        return cfg[key] - base[key]

    d_dx = _d("dx_concept_negation_f1")
    d_sf = _d("sf_active_rate_fidelity_f1")
    hurts_fidelity = (d_dx is not None and d_dx < -1e-9) or (d_sf is not None and d_sf < -1e-9)
    if fires == 0 and abs(d_bench) < 1e-9 and abs(d_head) < 1e-9:
        return "INSUFFICIENT EVIDENCE", "no same-raw fire or score change on source rows"
    if hurts_fidelity:
        return "CUT", "degrades a clinical-fidelity companion"
    if d_bench > 1e-9:
        return "KEEP CANDIDATE", "improves the paper-comparable benchmark key"
    if d_bench < -1e-9:
        return "CUT", "lowers the paper-comparable benchmark key"
    if d_head > 1e-9:
        return "CUT", "moves only the lenient headline, not benchmark"
    return "INSUFFICIENT EVIDENCE", "fires but no net score movement on source rows"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--date", default="2026-06-20")
    parser.add_argument("--source-note", default=None)
    args = parser.parse_args()

    source = args.source
    out_json = args.out_json or OUT_JSON
    out_md = args.out_md or OUT_MD
    rows = _load_rows(source)
    split = str(rows[0].get("split", "dev"))
    note_by_id = {letter.letter_id: letter.note_text for letter in load_letters_for_split(split)}

    families = sorted(QUARANTINED_TARGET_PROJECTION_FAMILIES)
    configs: dict[str, dict[str, bool] | None] = {"baseline": None}
    configs["audit_all"] = audit_only_projection_replay_switches()
    for family in families:
        configs[family] = {family: True}

    results = {name: _score_config(rows, note_by_id, sw) for name, sw in configs.items()}
    base = results["baseline"]

    verdicts: dict[str, dict[str, str]] = {}
    for family in families:
        verdict, reason = _verdict(family, base, results[family])
        verdicts[family] = {"verdict": verdict, "reason": reason}

    payload = {
        "date": args.date,
        "source_artifact": source.name,
        "source_path": str(source),
        "source_note": args.source_note or DEFAULT_SOURCE_NOTE,
        "split": split,
        "row_count": len(rows),
        "surfaces": {
            "headline": "cui_projected_headline_scores (lenient redefined key)",
            "benchmark": "cui_audit benchmark_f1_after_cui_projection (paper-comparable)",
            "dx_fidelity": "Diagnosis.concept_negation companion",
            "sf_fidelity": "SeizureFrequency.active_rate_fidelity companion",
        },
        "configs": results,
        "verdicts": verdicts,
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(_render_markdown(payload), encoding="utf-8")

    _print_console(payload)
    print(f"\nWrote {out_json}")
    print(f"Wrote {out_md}")


def _fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.4f}"


def _delta(cfg: float | None, base: float | None) -> str:
    if cfg is None or base is None:
        return "n/a"
    return f"{cfg - base:+.4f}"


def _print_console(payload: dict[str, Any]) -> None:
    base = payload["configs"]["baseline"]
    print(f"Same-raw family ablation  source={payload['source_artifact']}")
    print(f"Letters: {payload['row_count']}  Split: {payload['split']}")
    print()
    print(
        "{:<52}{:>10}{:>10}{:>9}{:>9}{:>7}".format(
            "Config", "headline", "bench", "DxFid", "SFFid", "fires"
        )
    )
    for name, cfg in payload["configs"].items():
        family_fire = (
            cfg["family_fires"].get(name, sum(cfg["family_fires"].values()))
            if name not in {"baseline", "audit_all"}
            else sum(cfg["family_fires"].values())
        )
        print(
            "{:<52}{:>10.4f}{:>10.4f}{:>9}{:>9}{:>7}".format(
                name[:52],
                cfg["headline_overall"],
                cfg["benchmark_overall"],
                _fmt(cfg["dx_concept_negation_f1"]),
                _fmt(cfg["sf_active_rate_fidelity_f1"]),
                family_fire,
            )
        )
    print()
    print("Per-family verdicts (marginal vs baseline):")
    for family, v in payload["verdicts"].items():
        cfg = payload["configs"][family]
        print(
            f"  {family}\n"
            f"    d_bench={_delta(cfg['benchmark_overall'], base['benchmark_overall'])} "
            f"d_head={_delta(cfg['headline_overall'], base['headline_overall'])} "
            f"-> {v['verdict']}: {v['reason']}"
        )


def _render_markdown(payload: dict[str, Any]) -> str:
    base = payload["configs"]["baseline"]
    lines: list[str] = []
    lines.append("# ExECTv2 Phase 2 Same-Raw Projection-Family Ablation")
    lines.append("")
    lines.append(f"Date: {payload['date']}")
    lines.append("")
    lines.append(
        "No model calls. Re-projects the source live LLM `raw_output` through "
        "current v0.42 deterministic projection under each quarantine switch "
        "configuration, then scores the same source letters."
    )
    lines.append("")
    lines.append(f"- Source artifact: `{payload['source_artifact']}`")
    lines.append(f"- Rows: {payload['row_count']} ({payload['split']} split)")
    lines.append(f"- Note: {payload['source_note']}")
    lines.append("")
    lines.append("## Surfaces")
    lines.append("")
    for key, desc in payload["surfaces"].items():
        lines.append(f"- `{key}`: {desc}")
    lines.append("")
    lines.append("## Configuration Scores")
    lines.append("")
    lines.append("| Config | Headline | Benchmark | Dx concept_negation |")
    lines[-1] += " SF active_rate_fidelity | Family fires |"
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for name, cfg in payload["configs"].items():
        family_fire = (
            cfg["family_fires"].get(name, 0)
            if name not in {"baseline", "audit_all"}
            else sum(cfg["family_fires"].values())
        )
        lines.append(
            f"| `{name}` | {cfg['headline_overall']:.4f} | "
            f"{cfg['benchmark_overall']:.4f} | "
            f"{_fmt(cfg['dx_concept_negation_f1'])} | "
            f"{_fmt(cfg['sf_active_rate_fidelity_f1'])} | {family_fire} |"
        )
    lines.append("")
    lines.append("## Per-Family Keep/Cut Verdicts")
    lines.append("")
    lines.append(
        "Marginal effect of enabling exactly one quarantined family versus the "
        "all-quarantined baseline."
    )
    lines.append("")
    lines.append(
        "| Family | d Headline | d Benchmark | d DxFid | d SFFid | Fires | Verdict | Reason |"
    )
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |")
    for family, v in payload["verdicts"].items():
        cfg = payload["configs"][family]
        lines.append(
            f"| `{family}` | "
            f"{_delta(cfg['headline_overall'], base['headline_overall'])} | "
            f"{_delta(cfg['benchmark_overall'], base['benchmark_overall'])} | "
            f"{_delta(cfg['dx_concept_negation_f1'], base['dx_concept_negation_f1'])} | "
            f"{_delta(cfg['sf_active_rate_fidelity_f1'], base['sf_active_rate_fidelity_f1'])} | "
            f"{cfg['family_fires'].get(family, 0)} | {v['verdict']} | {v['reason']} |"
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "Keep candidates are families that move the paper-comparable benchmark "
        "key without degrading a clinical-fidelity companion. Families that move "
        "only the lenient headline, lower the benchmark, or hurt fidelity are "
        "cut. Families with no same-raw effect stay quarantined as "
        "insufficient-evidence until a broader surface exists."
    )
    lines.append("")
    lines.append(
        "**Single-letter caveat.** Every keep-candidate family fires on exactly "
        "one source letter, so each benchmark gain rests on a single letter. "
        "This is the overfit risk the projection-family overfit audit named: a "
        "one-letter benchmark nudge cannot distinguish a clinically general "
        "projection from a benchmark-letter patch. 'Keep candidate' here means "
        "'promote to a broader check', not 'restore to the default pipeline'."
    )
    lines.append("")
    base_head = base["headline_overall"]
    base_bench = base["benchmark_overall"]
    if "v039_live_dev25" in str(payload["source_artifact"]):
        lines.append(
            "**Reproducibility note.** This same-raw baseline (default quarantine) "
            f"scores headline {base_head:.4f} / benchmark {base_bench:.4f} when the "
            "genuine v0.39 live raw is re-projected through v0.42 code. The published "
            "Phase 0 v0.42 artifact reads headline 0.9487 / benchmark-after-CUI "
            "0.3816. The two differ because the v0.40-v0.42 reproject chain stored "
            "already-projected output back into `raw_output` and re-projected it at "
            "each hop. The genuine-raw re-projection is the defensible same-raw "
            "surface for this ablation; the chained artifact is double-projected."
        )
    else:
        lines.append(
            "**Reproducibility note.** This same-raw baseline (default quarantine) "
            f"scores headline {base_head:.4f} / benchmark {base_bench:.4f}. "
            "All marginal family effects above are within-source replays of the "
            "same saved live raw output; they should not be compared as separate "
            "live model conditions."
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
