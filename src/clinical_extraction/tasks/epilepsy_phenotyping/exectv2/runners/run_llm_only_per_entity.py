"""CLI runner for the ExECTv2 focused per-entity candidate-source probe.

Loops the target entities (all nine after Phase B; the four regime probes in
Phase A), runs one focused call per (entity, letter), and writes a
per-entity JSONL + report for each, then a combined per-entity table that puts
the focused per-entity scores next to (a) the all-9 single-pass dev baseline and
(b) the published per-entity cells. The LLM is the candidate source for every
entity; the decision read is the source-near overlap recall, which says whether
the focused frame lifts LLM candidate recall over the attention-diluted all-9
pass. The regime column (read on the deterministic ledger) sizes how much
deterministic projection must follow the LLM candidate — it never routes an
entity away from GPT candidate generation.

Usage::

    # Smoke test: prompt-only over the pilot 25 letters (no LLM calls)
    uv run python -m \\
        clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_llm_only_per_entity \\
        --mode prompt-only --pilot 25

    # Live pilot 25 on gpt-4.1-mini
    uv run python -m \\
        clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_llm_only_per_entity \\
        --mode live --model openai/gpt-4.1-mini --temperature 0.0 --pilot 25

    # Full dev140, live, resumable
    uv run python -m \\
        clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_llm_only_per_entity \\
        --mode live --model openai/gpt-4.1-mini --temperature 0.0 --resume
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_per_entity as per_entity,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    score_entity,
    semantic_config_for,
    source_near_diagnostic,
)

# Documented projection-gap-ledger regime per entity (dev), measured on the
# DETERMINISTIC all-9 baseline. It sizes how much deterministic projection must
# follow the LLM candidate (heavy for representation-bound, light for recall-bound)
# — it is not a ceiling on LLM recall. The LLM is the candidate source for every
# entity; representation-bound just means raw LLM recall needs projection to land
# on the benchmark key.
LEDGER_REGIME: dict[str, str] = {
    "Diagnosis": "recall_bound",
    "Investigations": "recall_bound",
    "PatientHistory": "recall_bound",
    "Onset": "mixed",
    "SeizureFrequency": "mixed",
    "EpilepsyCause": "representation_bound",
    "BirthHistory": "representation_bound",
    "Prescription": "representation_bound",
    "WhenDiagnosed": "representation_bound",
}

# The focused per-entity frame is judged to lift LLM candidate recall when it beats
# the all-9 baseline on source-near overlap recall by at least this margin (and to
# regress when it falls short by it). This is a recall-quality read, not a routing
# decision — the LLM stays the candidate source regardless.
SOURCE_NEAR_RECALL_MARGIN = 0.05

DEFAULT_BASELINE_JSONL = Path(
    "experiments/exectv2_llm_only_all_entities_dev140_gpt41mini_20260612.jsonl"
)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="ExECTv2 focused per-entity candidate-source runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--split", default="dev", help="Data split (dev only for development).")
    p.add_argument("--model", default="openai/gpt-4.1-mini", help="DSPy model string.")
    p.add_argument(
        "--mode",
        choices=["live", "prompt-only"],
        default="prompt-only",
        help="'live' makes real LLM calls; 'prompt-only' emits prompts only.",
    )
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-tokens", type=int, default=2400)
    p.add_argument("--no-dspy-cache", action="store_true", help="Disable DSPy response caching.")
    p.add_argument("--api-base", default=None, help="Optional OpenAI-compatible API base URL.")
    p.add_argument("--pilot", type=int, default=None, help="Restrict to the first N letters.")
    p.add_argument(
        "--entities",
        nargs="+",
        default=list(per_entity.TARGET_ENTITIES),
        help="Entity names to probe.",
    )
    p.add_argument(
        "--resume",
        action="store_true",
        help="Resume each entity from its existing per-entity JSONL checkpoint.",
    )
    p.add_argument("--progress-every", type=int, default=25, help="Checkpoint every N letters.")
    p.add_argument(
        "--baseline-jsonl",
        type=Path,
        default=DEFAULT_BASELINE_JSONL,
        help="All-9 single-pass JSONL for the baseline column (per-entity, same split).",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments"),
        help="Directory for per-entity and combined artifacts.",
    )
    p.add_argument(
        "--out-prefix",
        default=None,
        help="Filename prefix for artifacts. Auto-generated if omitted.",
    )
    return p


def _auto_prefix(split: str, model: str, n: int) -> str:
    model_slug = model.split("/")[-1].replace("-", "").replace(".", "")
    today = date.today().isoformat().replace("-", "")
    n_str = str(n) if n else "all"
    return f"exectv2_llm_only_per_entity_{split}{n_str}_{model_slug}_{today}"


def _entity_slug(entity: str) -> str:
    return entity.lower()


# ── Baseline (all-9 single pass) per-entity scores ────────────────────────────


def _str_attrs(mention: dict[str, Any]) -> dict[str, str]:
    return {str(k): str(v) for k, v in (mention.get("attributes") or {}).items()}


def _baseline_letters(
    baseline_path: Path, entity: str, requested_ids: set[str]
) -> tuple[list[ExectLetter], list[ExectLetter]] | None:
    """Reconstruct (gold, pred) ExectLetters for one entity from an all-9 JSONL.

    Returns None when the baseline artifact is missing. Only letters in
    ``requested_ids`` are kept so the baseline column matches the probe scale.
    """
    if not baseline_path.exists():
        return None

    gold_letters: list[ExectLetter] = []
    pred_letters: list[ExectLetter] = []
    with baseline_path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            letter_id = row.get("letter_id")
            if letter_id not in requested_ids:
                continue
            gold_letters.append(
                ExectLetter(
                    letter_id=letter_id,
                    note_text="",
                    annotations=tuple(
                        ExectAnnotation(
                            entity=entity,
                            text=str(m["text"]),
                            attributes=_str_attrs(m),
                        )
                        for m in (row.get("gold_mentions") or [])
                        if m.get("entity") == entity
                    ),
                )
            )
            pred = PredictedLetter(
                letter_id=letter_id,
                mentions=tuple(
                    PredictedMention(
                        entity=entity,
                        text=str(m["text"]),
                        attributes=_str_attrs(m),
                        evidence="",
                    )
                    for m in (row.get("predicted_mentions") or [])
                    if m.get("entity") == entity
                ),
            )
            pred_letters.append(to_exect_letter(pred))
    return gold_letters, pred_letters


def _baseline_entity_scores(
    baseline_path: Path, entity: str, requested_ids: set[str]
) -> dict[str, float] | None:
    pair = _baseline_letters(baseline_path, entity, requested_ids)
    if pair is None:
        return None
    gold_letters, pred_letters = pair
    semantic = score_entity(gold_letters, pred_letters, entity, semantic_config_for(entity))
    sn = source_near_diagnostic(
        gold_letters, pred_letters, [entity], semantic_config_for
    ).per_entity[entity]
    return {
        "semantic_item_f1": round(semantic.per_item.f1, 4),
        "semantic_letter_f1": round(semantic.per_letter.f1, 4),
        "source_near_recall": round(sn.overlap.recall, 4),
        "source_near_f1": round(sn.overlap.f1, 4),
        "over_emission": sn.overlap.fp,
    }


# ── Combined table ────────────────────────────────────────────────────────────


def _verdict(delta_recall: float | None) -> str:
    """Recall-quality read of the focused frame vs the all-9 baseline.

    This judges the focused LLM frame's candidate recall, not which component
    generates candidates: the LLM is the candidate source for every entity.
    """
    if delta_recall is None:
        return "no baseline"
    if delta_recall >= SOURCE_NEAR_RECALL_MARGIN:
        return "focused frame lifts LLM recall"
    if delta_recall <= -SOURCE_NEAR_RECALL_MARGIN:
        return "focused frame regresses vs all-9"
    return "recall on par with all-9"


def _build_combined(
    per_entity_summaries: dict[str, dict[str, Any]],
    baselines: dict[str, dict[str, float] | None],
    *,
    split: str,
    model: str,
    mode: str,
    n_letters: int,
) -> dict[str, Any]:
    table: list[dict[str, Any]] = []
    for entity, summary in per_entity_summaries.items():
        scores = summary.get("scores", {})
        semantic = scores.get("semantic", {})
        sem_item = semantic.get("per_item", {})
        sem_letter = semantic.get("per_letter", {})
        sn = summary.get("source_near", {}).get("overlap", {})
        baseline = baselines.get(entity)
        base_recall = baseline.get("source_near_recall") if baseline else None
        probe_recall = sn.get("recall", 0.0)
        delta_recall = round(probe_recall - base_recall, 4) if base_recall is not None else None
        regime = LEDGER_REGIME.get(entity, "unknown")
        table.append(
            {
                "entity": entity,
                "regime": regime,
                "published_item_f1": per_entity.PUBLISHED_PER_ENTITY_ITEM_F1.get(entity),
                "baseline_semantic_item_f1": baseline.get("semantic_item_f1") if baseline else None,
                "probe_semantic_item_f1": sem_item.get("f1"),
                "probe_semantic_letter_f1": sem_letter.get("f1"),
                "baseline_source_near_recall": base_recall,
                "probe_source_near_recall": probe_recall,
                "delta_source_near_recall": delta_recall,
                "probe_source_near_f1": sn.get("f1"),
                "over_emission": summary.get("over_emission"),
                "baseline_over_emission": baseline.get("over_emission") if baseline else None,
                "evidence_validity_rate": summary.get("evidence_validity_rate"),
                "call_failures": summary.get("call_failures"),
                "parse_failures": summary.get("parse_failures"),
                "verdict": _verdict(delta_recall),
            }
        )
    return {
        "split": split,
        "model": model,
        "mode": mode,
        "n_letters": n_letters,
        "prompt_version": per_entity.PROMPT_VERSION,
        "source_near_recall_margin": SOURCE_NEAR_RECALL_MARGIN,
        "generated_on": date.today().isoformat(),
        "per_entity": table,
    }


def _render_combined_md(combined: dict[str, Any], *, json_path: Path) -> str:
    lines = [
        "# ExECTv2 Per-Entity Candidate-Source Probe — Combined",
        "",
        f"- Generated: `{combined['generated_on']}`",
        f"- JSON: `{json_path}`",
        f"- Split: `{combined['split']}`  Letters: {combined['n_letters']}",
        f"- Model: `{combined['model']}`  Mode: `{combined['mode']}`",
        f"- Prompt version: `{combined['prompt_version']}`",
        (
            f"- Verdict rule: focused frame lifts LLM candidate recall when source-near "
            f"overlap recall beats the all-9 baseline by >= "
            f"{combined['source_near_recall_margin']:.2f}"
        ),
        "",
        (
            "The LLM is the candidate source for every entity. Source-near overlap "
            "recall is the format-blind candidate read; semantic F1 is the CUI-dropped "
            "headline; the all-9 baseline is the documented negative comparator "
            "(attention-diluted single pass). The regime column sizes the deterministic "
            "projection that must follow the LLM candidate — it does not route an entity "
            "away from GPT candidate generation."
        ),
        "",
        "## Per-Entity Table",
        "",
        (
            "| Entity | Regime | Pub item F1 | Base sem item | Probe sem item | "
            "Probe sem letter | Base SN recall | Probe SN recall | Δ SN recall | "
            "Over-emit (probe/base) | Verdict |"
        ),
        (
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"
        ),
    ]
    for r in combined["per_entity"]:
        lines.append(
            f"| {r['entity']} | {r['regime']} | {_f(r['published_item_f1'])} "
            f"| {_f(r['baseline_semantic_item_f1'])} | {_f(r['probe_semantic_item_f1'])} "
            f"| {_f(r['probe_semantic_letter_f1'])} | {_f(r['baseline_source_near_recall'])} "
            f"| {_f(r['probe_source_near_recall'])} | {_signed(r['delta_source_near_recall'])} "
            f"| {_i(r['over_emission'])}/{_i(r['baseline_over_emission'])} | {r['verdict']} |"
        )
    lines.extend([
        "",
        "## Reading",
        "",
        (
            "The LLM generates candidates for every entity. A positive Δ source-near "
            "recall means the focused frame recovers more real candidates than the "
            "attention-diluted all-9 pass; flat/negative Δ means the focused frame did "
            "not help recall there. High LLM source-near recall on a representation-bound "
            "entity (e.g. Prescription) is expected — its low semantic F1 is a projection "
            "gap, not a recall gap, and is closed by deterministic projection (Phase D), "
            "not by routing candidate generation away from the LLM. Read the over-emission "
            "columns for the first hybrid target."
        ),
        "",
    ])
    return "\n".join(lines)


def _f(value: Any) -> str:
    return "—" if value is None else f"{float(value):.3f}"


def _signed(value: Any) -> str:
    return "—" if value is None else f"{float(value):+.3f}"


def _i(value: Any) -> str:
    return "—" if value is None else str(int(value))


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    args = _build_parser().parse_args()

    if args.split == "test":
        print(
            "ERROR: test split is a locked holdout — only dev is permitted for "
            "development runs. Use --split dev.",
            file=sys.stderr,
        )
        sys.exit(1)

    letters = load_letters_for_split(args.split)
    if args.pilot:
        letters = letters[: args.pilot]
    n = len(letters)
    requested_ids = {letter.letter_id for letter in letters}
    print(f"Loaded {n} letters from split '{args.split}'.", flush=True)

    prefix = args.out_prefix or _auto_prefix(args.split, args.model, n)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    per_entity_summaries: dict[str, dict[str, Any]] = {}
    baselines: dict[str, dict[str, float] | None] = {}

    for entity in args.entities:
        if entity not in per_entity.ENTITY_REGISTRY:
            print(f"Skipping unknown entity {entity!r}.", file=sys.stderr)
            continue
        jsonl_path = args.out_dir / f"{prefix}_{_entity_slug(entity)}.jsonl"
        report_path = args.out_dir / f"{prefix}_{_entity_slug(entity)}.md"

        print(
            f"\n=== {entity}: {args.mode} / {args.model} over {n} letters ===",
            flush=True,
        )
        rows, metadata = per_entity.run_split(
            letters,
            entity_name=entity,
            split=args.split,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            mode=args.mode,
            dspy_cache=not args.no_dspy_cache,
            api_base=args.api_base,
            progress_every=args.progress_every,
            checkpoint_jsonl_path=jsonl_path,
            checkpoint_report_path=report_path,
            resume=args.resume,
        )
        per_entity.write_jsonl(rows, jsonl_path)
        per_entity.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

        summary = metadata.get("summary", {})
        per_entity_summaries[entity] = summary
        baselines[entity] = _baseline_entity_scores(args.baseline_jsonl, entity, requested_ids)

        sn = summary.get("source_near", {}).get("overlap", {})
        sem = summary.get("scores", {}).get("semantic", {}).get("per_item", {})
        print(
            f"  call_fail={summary.get('call_failures', 0)} "
            f"parse_fail={summary.get('parse_failures', 0)} "
            f"evidence_valid={summary.get('evidence_validity_rate', 0):.3f}",
            flush=True,
        )
        print(
            f"  semantic item F1={sem.get('f1', 0):.3f}  "
            f"source-near recall={sn.get('recall', 0):.3f}  "
            f"over-emit={summary.get('over_emission', 0)}",
            flush=True,
        )

    combined = _build_combined(
        per_entity_summaries,
        baselines,
        split=args.split,
        model=args.model,
        mode=args.mode,
        n_letters=n,
    )
    combined_json = args.out_dir / f"{prefix}_combined.json"
    combined_md = args.out_dir / f"{prefix}_combined.md"
    combined_json.write_text(
        json.dumps(combined, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    combined_md.write_text(_render_combined_md(combined, json_path=combined_json), encoding="utf-8")

    print(f"\nWrote combined table: {combined_md}", flush=True)
    for r in combined["per_entity"]:
        print(
            f"  {r['entity']:<16} regime={r['regime']:<20} "
            f"Δsource-near-recall={_signed(r['delta_source_near_recall'])} "
            f"-> {r['verdict']}",
            flush=True,
        )


if __name__ == "__main__":
    main()
