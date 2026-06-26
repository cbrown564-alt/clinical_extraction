"""Merged hybrid -> benchmark-overall runner for ExECTv2.

The synthesis key-family architecture is scored per family on the *clinical
recovery* surface (concept identity / frequency state / components). That surface
is more lenient than, and not comparable to, the published ExECTv2 benchmark
headline (exact normalized phrase + all attributes + CUI). This runner produces
the missing like-for-like number: it overlays the current best per-family hybrid
verifier predictions (Prescription, Investigations, Diagnosis, SeizureFrequency)
onto the deterministic all-9 substrate for the remaining five families, then
scores the merged all-9 prediction through ``score_overall`` under the same
benchmark / semantic / phrase-only configs the deterministic all-9 scorecard and
the Phase-7 audit use.

No LLM calls: the four key-family verifier predictions are read from their saved
JSONL run artifacts. The output is directly comparable to the paper's overall
F1 0.87 per item / 0.90 per letter and to the deterministic all-9 baseline.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ALL_ENTITIES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    run_all9_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.registry_sync import (
    DEFAULT_RUN_INDEX_PATH,
    register_run,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.scorecard_core import (
    prf1_to_dict,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    benchmark_config_for,
    score_overall,
    semantic_config_for,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry import (
    RunRegistryEntry,
)

PIPELINE_FAMILY = "exectv2_hybrid_benchmark_overall"
MODEL = "gpt-4.1-mini (key families) + deterministic"
DEFAULT_REGISTRY_PATH = Path("experiments/registry.jsonl")
ALL_ENTITY_NAMES: tuple[str, ...] = tuple(spec.name for spec in ALL_ENTITIES)
EXPERIMENTS_DIR = Path("experiments")

# Key families served by hybrid verifier artifacts; everything else falls back to
# the deterministic all-9 substrate. Each entry is (default artifact, entity to
# pull from that artifact's ``predicted_mentions``).
KEY_FAMILY_DEFAULTS: dict[str, tuple[Path, str]] = {
    "Prescription": (
        EXPERIMENTS_DIR / "exectv2_llm_med_inv_verifier_v01_dev140_gpt41mini_20260618.jsonl",
        "Prescription",
    ),
    "Investigations": (
        EXPERIMENTS_DIR / "exectv2_llm_investigations_verifier_v01_dev140_gpt41mini_20260618.jsonl",
        "Investigations",
    ),
    "Diagnosis": (
        EXPERIMENTS_DIR / "exectv2_hybrid_diagnosis_reconciler_v02_dev140_gpt41mini_20260618.jsonl",
        "Diagnosis",
    ),
    "SeizureFrequency": (
        EXPERIMENTS_DIR / "exectv2_hybrid_sf_unknown_suppression_v07_dev140_20260618.jsonl",
        "SeizureFrequency",
    ),
}
KEY_FAMILIES: tuple[str, ...] = tuple(KEY_FAMILY_DEFAULTS)

# Published ExECTv2 (Fonferko-Shadrach 2024) per-item F1 cells and overall.
PAPER_PER_ITEM_F1: dict[str, float] = {
    "BirthHistory": 0.97,
    "Diagnosis": 0.85,
    "EpilepsyCause": 0.90,
    "Investigations": 0.95,
    "Onset": 0.96,
    "PatientHistory": 0.78,
    "Prescription": 0.87,
    "SeizureFrequency": 0.66,
    "WhenDiagnosed": 0.91,
}
PAPER_OVERALL_PER_ITEM = 0.87
PAPER_OVERALL_PER_LETTER = 0.90

_VALID_CONFIDENCE = {"low", "medium", "high"}


def _mention_from_row(item: Mapping[str, Any], default_entity: str) -> PredictedMention:
    """Build a PredictedMention from a saved verifier ``predicted_mentions`` row."""

    confidence = item.get("confidence")
    if confidence not in _VALID_CONFIDENCE:
        confidence = None
    return PredictedMention(
        entity=str(item.get("entity") or default_entity),
        text=str(item.get("text", "")),
        attributes={str(k): str(v) for k, v in dict(item.get("attributes", {})).items()},
        evidence=str(item.get("evidence", "")),
        rationale=str(item.get("rationale", "")),
        confidence=confidence,
    )


def load_family_mentions(
    path: Path,
    entity_filter: str,
) -> dict[str, list[PredictedMention]]:
    """Read one verifier JSONL, returning {letter_id: [mentions of entity_filter]}."""

    by_letter: dict[str, list[PredictedMention]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            letter_id = str(row["letter_id"])
            mentions = by_letter.setdefault(letter_id, [])
            for item in row.get("predicted_mentions", []):
                if str(item.get("entity") or entity_filter) != entity_filter:
                    continue
                mentions.append(_mention_from_row(item, entity_filter))
    return by_letter


def build_merged_predictions(
    gold_letters: Sequence[ExectLetter],
    family_sources: Mapping[str, tuple[Path, str]],
) -> tuple[list[PredictedLetter], dict[str, Any]]:
    """Overlay hybrid key-family mentions onto the deterministic substrate.

    Any entity absent from ``family_sources`` is served by the deterministic
    all-9 substrate, so callers can choose, per family, hybrid verifier vs rules.
    """

    deterministic_families = tuple(
        name for name in ALL_ENTITY_NAMES if name not in family_sources
    )
    deterministic = {pred.letter_id: pred for pred in run_all9_on_letters(gold_letters)}
    family_mentions: dict[str, dict[str, list[PredictedMention]]] = {}
    provenance: dict[str, Any] = {}
    for entity, (path, entity_filter) in family_sources.items():
        family_mentions[entity] = load_family_mentions(path, entity_filter)
        provenance[entity] = {
            "source": "hybrid_verifier",
            "artifact": str(path),
            "entity_filter": entity_filter,
        }
    for entity in deterministic_families:
        provenance[entity] = {"source": "deterministic_all9"}

    merged: list[PredictedLetter] = []
    mention_counts: dict[str, int] = {name: 0 for name in ALL_ENTITY_NAMES}
    for gold in gold_letters:
        letter_id = gold.letter_id
        det = deterministic[letter_id]
        mentions: list[PredictedMention] = [
            m for m in det.mentions if m.entity in deterministic_families
        ]
        for entity in family_sources:
            mentions.extend(family_mentions[entity].get(letter_id, []))
        for m in mentions:
            if m.entity in mention_counts:
                mention_counts[m.entity] += 1
        merged.append(
            PredictedLetter(
                letter_id=letter_id,
                mentions=tuple(mentions),
                diagnostics={"architecture_track": "hybrid_key_family_plus_deterministic"},
            )
        )
    metadata = {"provenance": provenance, "mention_counts": mention_counts}
    return merged, metadata


def build_scorecard(
    gold_letters: Sequence[ExectLetter],
    predictions: Sequence[PredictedLetter],
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    pred_letters = [
        to_exect_letter(pred, note_text=gold.note_text)
        for pred, gold in zip(predictions, gold_letters, strict=True)
    ]
    configs = {
        "phrase_only": lambda _entity: PHRASE_ONLY,
        "semantic": semantic_config_for,
        "benchmark": benchmark_config_for,
    }
    scores = {
        name: score_overall(gold_letters, pred_letters, ALL_ENTITY_NAMES, config_for)
        for name, config_for in configs.items()
    }
    benchmark = scores["benchmark"]
    per_entity_benchmark = {
        entity: {
            "per_item": prf1_to_dict(score.per_item),
            "per_letter": prf1_to_dict(score.per_letter),
            "paper_per_item_f1": PAPER_PER_ITEM_F1.get(entity),
            "delta_vs_paper_item": round(score.per_item.f1 - PAPER_PER_ITEM_F1[entity], 4)
            if entity in PAPER_PER_ITEM_F1
            else None,
            "source": metadata["provenance"][entity]["source"],
        }
        for entity, score in benchmark.per_entity.items()
    }
    provenance = metadata["provenance"]
    key_families = [
        name for name in ALL_ENTITY_NAMES if provenance[name]["source"] == "hybrid_verifier"
    ]
    fallback_families = [
        name for name in ALL_ENTITY_NAMES if provenance[name]["source"] == "deterministic_all9"
    ]
    return {
        "pipeline_family": PIPELINE_FAMILY,
        "model": MODEL,
        "row_count": len(gold_letters),
        "key_families": key_families,
        "deterministic_fallback_families": fallback_families,
        "provenance": provenance,
        "mention_counts": metadata["mention_counts"],
        "scores": {
            name: {
                "per_item": prf1_to_dict(score.per_item),
                "per_letter": prf1_to_dict(score.per_letter),
            }
            for name, score in scores.items()
        },
        "per_entity_benchmark": per_entity_benchmark,
        "paper_overall_per_item_f1": PAPER_OVERALL_PER_ITEM,
        "paper_overall_per_letter_f1": PAPER_OVERALL_PER_LETTER,
        "benchmark_overall_delta_vs_paper": {
            "per_item": round(benchmark.per_item.f1 - PAPER_OVERALL_PER_ITEM, 4),
            "per_letter": round(benchmark.per_letter.f1 - PAPER_OVERALL_PER_LETTER, 4),
        },
    }


def _render_markdown(scorecard: Mapping[str, Any], *, json_path: Path) -> str:
    lines: list[str] = []
    lines.append("# ExECTv2 Hybrid Merged Benchmark-Overall Scorecard")
    lines.append("")
    lines.append(f"- Generated: `{scorecard['generated_on']}`")
    lines.append(f"- Split: `{scorecard['split']}`")
    lines.append(f"- JSON: `{json_path}`")
    lines.append(f"- Pipeline family: `{scorecard['pipeline_family']}`")
    lines.append(f"- Row count: {scorecard['row_count']}")
    lines.append(
        "- Key families (hybrid verifier): " + ", ".join(scorecard["key_families"])
    )
    lines.append(
        "- Deterministic fallback families: "
        + ", ".join(scorecard["deterministic_fallback_families"])
    )
    lines.append("")
    lines.append("## Overall Scores (vs paper 0.87 item / 0.90 letter)")
    lines.append("")
    lines.append("| Layer | Per-item F1 | Per-letter F1 | TP | FP | FN |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for layer, score in scorecard["scores"].items():
        item = score["per_item"]
        letter = score["per_letter"]
        lines.append(
            f"| {layer} | {item['f1']:.4f} | {letter['f1']:.4f} | "
            f"{item['tp']} | {item['fp']} | {item['fn']} |"
        )
    delta = scorecard["benchmark_overall_delta_vs_paper"]
    lines.append("")
    lines.append(
        f"- Benchmark overall vs paper: per-item {delta['per_item']:+.4f}, "
        f"per-letter {delta['per_letter']:+.4f}"
    )
    lines.append("")
    lines.append("## Per-Entity Benchmark F1 vs Paper")
    lines.append("")
    lines.append("| Entity | Source | Item F1 | Paper item F1 | Δ vs paper | Letter F1 | TP | FP | FN |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for entity in ALL_ENTITY_NAMES:
        cell = scorecard["per_entity_benchmark"][entity]
        item = cell["per_item"]
        letter = cell["per_letter"]
        paper = cell["paper_per_item_f1"]
        delta_e = cell["delta_vs_paper_item"]
        src = "hybrid" if cell["source"] == "hybrid_verifier" else "rules"
        lines.append(
            f"| {entity} | {src} | {item['f1']:.4f} | "
            f"{paper:.2f} | {delta_e:+.4f} | {letter['f1']:.4f} | "
            f"{item['tp']} | {item['fp']} | {item['fn']} |"
        )
    lines.append("")
    lines.append("## Mention Counts")
    lines.append("")
    lines.append("| Entity | Merged predicted mentions |")
    lines.append("| --- | ---: |")
    for entity in ALL_ENTITY_NAMES:
        lines.append(f"| {entity} | {scorecard['mention_counts'][entity]} |")
    lines.append("")
    lines.append("## Provenance")
    lines.append("")
    for entity in ALL_ENTITY_NAMES:
        prov = scorecard["provenance"][entity]
        if prov["source"] == "hybrid_verifier":
            lines.append(f"- {entity}: hybrid verifier `{prov['artifact']}`")
        else:
            lines.append(f"- {entity}: deterministic all-9 substrate")
    lines.append("")
    lines.append("## Reading")
    lines.append("")
    lines.append(
        "The benchmark layer is the only surface comparable to the published "
        "0.87/0.90 headline (exact normalized phrase + all attributes + CUI). The "
        "phrase_only and semantic layers expose how much of the gap is "
        "phrase/attribute/CUI projection versus concept recall."
    )
    lines.append("")
    return "\n".join(lines)


def _registry_entry(
    scorecard: Mapping[str, Any], *, json_path: Path, md_path: Path
) -> RunRegistryEntry:
    benchmark = scorecard["scores"]["benchmark"]
    return RunRegistryEntry(
        run_id=f"exectv2_hybrid_benchmark_overall_{scorecard['split']}_"
        f"{scorecard['generated_on'].replace('-', '')}",
        date=scorecard["generated_on"],
        pipeline_family=PIPELINE_FAMILY,
        model=MODEL,
        split=scorecard["split"],
        row_count=scorecard["row_count"],
        decision="inform_architecture_loop",
        mode="analysis_only",
        replay_status="analysis_only",
        model_role="Merged hybrid key-family + deterministic all-9, benchmark surface.",
        primary_metrics={
            "benchmark_per_item_f1": benchmark["per_item"]["f1"],
            "benchmark_per_letter_f1": benchmark["per_letter"]["f1"],
            "semantic_per_item_f1": scorecard["scores"]["semantic"]["per_item"]["f1"],
            "phrase_only_per_item_f1": scorecard["scores"]["phrase_only"]["per_item"]["f1"],
            "paper_overall_per_item_f1": PAPER_OVERALL_PER_ITEM,
            "paper_overall_per_letter_f1": PAPER_OVERALL_PER_LETTER,
        },
        claim_language_notes=(
            "Like-for-like benchmark-surface overall for the synthesis hybrid "
            "key-family architecture. Dev140, analysis-only, no full-200 audit."
        ),
        artifact_paths=[str(json_path), str(md_path)],
    )


def write_artifacts(
    *,
    out_json: Path,
    out_md: Path,
    split: str,
    family_sources: Mapping[str, tuple[Path, str]],
    generated_on: str | None,
    registry_path: Path | None,
    run_index_path: Path,
) -> dict[str, Any]:
    generated_on = generated_on or date.today().isoformat()
    gold_letters = load_letters_for_split(split)
    predictions, metadata = build_merged_predictions(gold_letters, family_sources)
    scorecard = build_scorecard(gold_letters, predictions, metadata)
    scorecard.update({"split": split, "generated_on": generated_on})

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(_render_markdown(scorecard, json_path=out_json), encoding="utf-8")

    if registry_path is not None:
        register_run(
            _registry_entry(scorecard, json_path=out_json, md_path=out_md),
            registry_path=registry_path,
            run_index_path=run_index_path,
        )
    return scorecard


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Merged hybrid key-family + deterministic all-9 benchmark-overall scorer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--split", default="dev", help="Data split; test is locked.")
    parser.add_argument("--prescription-jsonl", type=Path, default=None)
    parser.add_argument("--investigations-jsonl", type=Path, default=None)
    parser.add_argument("--diagnosis-jsonl", type=Path, default=None)
    parser.add_argument("--seizure-frequency-jsonl", type=Path, default=None)
    parser.add_argument(
        "--deterministic-for",
        nargs="*",
        default=(),
        choices=KEY_FAMILIES,
        help="Key families to leave on the deterministic substrate instead of the hybrid verifier.",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--register", action="store_true", help="Register the run (default off).")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--run-index", type=Path, default=DEFAULT_RUN_INDEX_PATH)
    return parser


def _resolve_sources(args: argparse.Namespace) -> dict[str, tuple[Path, str]]:
    overrides = {
        "Prescription": args.prescription_jsonl,
        "Investigations": args.investigations_jsonl,
        "Diagnosis": args.diagnosis_jsonl,
        "SeizureFrequency": args.seizure_frequency_jsonl,
    }
    deterministic_for = set(args.deterministic_for)
    sources: dict[str, tuple[Path, str]] = {}
    for entity, (default_path, entity_filter) in KEY_FAMILY_DEFAULTS.items():
        if entity in deterministic_for:
            continue
        path = overrides[entity] or default_path
        sources[entity] = (path, entity_filter)
    return sources


def main() -> None:
    args = _build_parser().parse_args()
    if args.split == "test":
        raise SystemExit("ERROR: test split is locked; only dev is permitted.")
    family_sources = _resolve_sources(args)
    for entity, (path, _filter) in family_sources.items():
        if not path.exists():
            raise SystemExit(f"ERROR: missing {entity} artifact: {path}")

    today = date.today().isoformat().replace("-", "")
    base = f"exectv2_hybrid_benchmark_overall_{args.split}_{today}"
    out_json = args.out_json or EXPERIMENTS_DIR / f"{base}.json"
    out_md = args.out_md or EXPERIMENTS_DIR / f"{base}.md"

    scorecard = write_artifacts(
        out_json=out_json,
        out_md=out_md,
        split=args.split,
        family_sources=family_sources,
        generated_on=None,
        registry_path=args.registry if args.register else None,
        run_index_path=args.run_index,
    )

    benchmark = scorecard["scores"]["benchmark"]
    delta = scorecard["benchmark_overall_delta_vs_paper"]
    print(f"\nDone. JSON: {out_json}  MD: {out_md}", flush=True)
    print(
        f"Benchmark overall: per-item F1 {benchmark['per_item']['f1']:.4f} "
        f"(paper {PAPER_OVERALL_PER_ITEM}, {delta['per_item']:+.4f}) | "
        f"per-letter F1 {benchmark['per_letter']['f1']:.4f} "
        f"(paper {PAPER_OVERALL_PER_LETTER}, {delta['per_letter']:+.4f})",
        flush=True,
    )
    print(
        f"Semantic overall per-item F1 {scorecard['scores']['semantic']['per_item']['f1']:.4f} | "
        f"phrase-only per-item F1 {scorecard['scores']['phrase_only']['per_item']['f1']:.4f}",
        flush=True,
    )


if __name__ == "__main__":
    main()
