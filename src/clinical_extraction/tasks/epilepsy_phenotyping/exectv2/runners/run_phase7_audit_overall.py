"""Phase 7 frozen benchmark audit for ExECTv2 all-entity LLM-only extraction."""

from __future__ import annotations

import argparse
import json
import random
import subprocess
from collections.abc import Callable, Sequence
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.core.scoring import PRF1, multiset_prf1, prf1_from_counts
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ALL_ENTITIES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_all_entities import (
    PROMPT_VERSION,
    PUBLISHED_OVERALL,
    PUBLISHED_PER_ENTITY_ITEM_F1,
    run_split,
    write_jsonl,
    write_report,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    MatchConfig,
    _keys,
    benchmark_config_for,
    score_overall,
    semantic_config_for,
)

AUTHORIZATION = "full-200 overall read authorized by user 2026-06-12 (Phase 6/7)"
AUDIT_SURFACE = "full200_overall_audit"
DEFAULT_REGISTRY_PATH = Path("experiments/registry.jsonl")
BOOTSTRAP_SAMPLES = 5000
BOOTSTRAP_SEED = 20260612
ENTITY_NAMES: tuple[str, ...] = tuple(spec.name for spec in ALL_ENTITIES)
PIPELINE_FAMILY = "exectv2_llm_only_all_entities"


class _LetterRecord:
    __slots__ = ("item_tp", "item_fp", "item_fn", "letter_tp", "letter_fp", "letter_fn")

    def __init__(
        self,
        item_tp: int,
        item_fp: int,
        item_fn: int,
        letter_tp: int,
        letter_fp: int,
        letter_fn: int,
    ) -> None:
        self.item_tp = item_tp
        self.item_fp = item_fp
        self.item_fn = item_fn
        self.letter_tp = letter_tp
        self.letter_fp = letter_fp
        self.letter_fn = letter_fn


def _letters_from_rows(rows: Sequence[dict[str, Any]], *, key: str) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        annotations = tuple(
            ExectAnnotation(
                entity=str(m["entity"]),
                text=str(m["text"]),
                attributes={str(k): str(v) for k, v in dict(m.get("attributes") or {}).items()},
            )
            for m in (row.get(key) or [])
        )
        letters.append(
            ExectLetter(
                letter_id=row["letter_id"],
                note_text="",
                annotations=annotations,
            )
        )
    return letters


def _letter_records(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    config_for: Callable[[str], MatchConfig],
) -> list[_LetterRecord]:
    gold_by_id = {letter.letter_id: letter for letter in gold_letters}
    pred_by_id = {letter.letter_id: letter for letter in pred_letters}
    records: list[_LetterRecord] = []

    for letter_id in sorted(gold_by_id.keys() | pred_by_id.keys()):
        item_tp = item_fp = item_fn = 0
        letter_tp = letter_fp = letter_fn = 0
        gold_letter = gold_by_id.get(letter_id)
        pred_letter = pred_by_id.get(letter_id)
        for entity in ENTITY_NAMES:
            gold_m = gold_letter.entities(entity) if gold_letter else ()
            pred_m = pred_letter.entities(entity) if pred_letter else ()
            item = multiset_prf1(
                _keys(gold_m, config_for(entity)),
                _keys(pred_m, config_for(entity)),
            )
            item_tp += item.tp
            item_fp += item.fp
            item_fn += item.fn

            gold_present = len(gold_m) > 0
            pred_present = len(pred_m) > 0
            if gold_present and item.tp > 0:
                letter_tp += 1
            elif gold_present:
                letter_fn += 1
            elif pred_present:
                letter_fp += 1

        records.append(_LetterRecord(item_tp, item_fp, item_fn, letter_tp, letter_fp, letter_fn))
    return records


def _aggregate(records: Sequence[_LetterRecord]) -> tuple[PRF1, PRF1]:
    return (
        prf1_from_counts(
            sum(r.item_tp for r in records),
            sum(r.item_fp for r in records),
            sum(r.item_fn for r in records),
        ),
        prf1_from_counts(
            sum(r.letter_tp for r in records),
            sum(r.letter_fp for r in records),
            sum(r.letter_fn for r in records),
        ),
    )


def _bootstrap_ci(records: Sequence[_LetterRecord]) -> dict[str, tuple[float, float]]:
    rng = random.Random(BOOTSTRAP_SEED)
    k = len(records)
    per_item: list[float] = []
    per_letter: list[float] = []
    for _ in range(BOOTSTRAP_SAMPLES):
        sample = [records[rng.randrange(k)] for _ in range(k)]
        item, letter = _aggregate(sample)
        per_item.append(item.f1)
        per_letter.append(letter.f1)
    per_item.sort()
    per_letter.sort()

    def ci(values: list[float]) -> tuple[float, float]:
        lo = values[int(0.025 * len(values))]
        hi = values[int(0.975 * len(values)) - 1]
        return round(lo, 4), round(hi, 4)

    return {"per_item": ci(per_item), "per_letter": ci(per_letter)}


def _git_head() -> str:
    try:
        head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()[:12]
        dirty = (
            subprocess.run(
                ["git", "diff", "--quiet"],
                stderr=subprocess.DEVNULL,
                check=False,
            ).returncode
            != 0
        )
        untracked = bool(
            subprocess.check_output(
                ["git", "ls-files", "--others", "--exclude-standard"],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        )
        return f"{head}+dirty" if dirty or untracked else head
    except Exception:
        return "unknown"


def _dev_reference(registry_path: Path, model: str) -> dict[str, tuple[float, float]] | None:
    if not registry_path.exists():
        return None
    best: dict[str, Any] | None = None
    for line in registry_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if (
            row.get("pipeline_family") == PIPELINE_FAMILY
            and row.get("model") == model
            and row.get("split") == "dev"
        ):
            if best is None or int(row.get("row_count", 0)) > int(best.get("row_count", 0)):
                best = row
    if best is None:
        return None
    metrics = best.get("primary_metrics", {})
    return {
        "semantic": (
            float(metrics["semantic_per_item_f1"]),
            float(metrics["semantic_per_letter_f1"]),
        ),
        "benchmark": (
            float(metrics["benchmark_per_item_f1"]),
            float(metrics["benchmark_per_letter_f1"]),
        ),
        "phrase_only": (
            float(metrics["phrase_only_per_item_f1"]),
            float(metrics["phrase_only_per_letter_f1"]),
        ),
    }


def _fmt_gap(audit_f1: float, dev_f1: float | None) -> str:
    if dev_f1 is None:
        return "-"
    return f"{dev_f1:.3f} -> {audit_f1:.3f} ({audit_f1 - dev_f1:+.3f})"


def _score_block(name: str, score: Any, ci: dict[str, tuple[float, float]] | None) -> list[str]:
    item_ci = f" CI {ci['per_item'][0]:.3f}-{ci['per_item'][1]:.3f}" if ci else ""
    letter_ci = f" CI {ci['per_letter'][0]:.3f}-{ci['per_letter'][1]:.3f}" if ci else ""
    return [
        f"### {name}",
        "",
        f"- per-item: P={score.per_item.precision:.3f} R={score.per_item.recall:.3f} "
        f"F1={score.per_item.f1:.3f}{item_ci} "
        f"(TP={score.per_item.tp} FP={score.per_item.fp} FN={score.per_item.fn})",
        f"- per-letter: P={score.per_letter.precision:.3f} R={score.per_letter.recall:.3f} "
        f"F1={score.per_letter.f1:.3f}{letter_ci} "
        f"(TP={score.per_letter.tp} FP={score.per_letter.fp} FN={score.per_letter.fn})",
        "",
    ]


def _render_report(
    *,
    scores: dict[str, Any],
    ci: dict[str, dict[str, tuple[float, float]]],
    dev_ref: dict[str, tuple[float, float]] | None,
    summary: dict[str, Any],
    jsonl_path: Path,
    git_head: str,
    generated_on: str,
    model: str,
    n_letters: int,
) -> str:
    lines = [
        "# ExECTv2 Phase 7 Frozen Overall Audit - LLM-Only All Entities",
        "",
        "> Immutable full-200 overall read. No row-level tuning or post-audit repair.",
        "",
        f"- Generated: `{generated_on}`",
        f"- Authorization: {AUTHORIZATION}",
        f"- Locked code: git `{git_head}`",
        f"- JSONL: `{jsonl_path}`",
        f"- Surface: all {n_letters} letters (`load_letters`)",
        f"- Architecture: `{PIPELINE_FAMILY}`",
        f"- Model: `{model}`",
        f"- Prompt version: `{PROMPT_VERSION}`",
        "",
        "## Gate Summary",
        "",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema failures: {summary.get('parse_failures', 0)}",
        f"- Mentions raw: {summary.get('n_mentions_raw', 0)}",
        f"- Mentions scored: {summary.get('n_mentions_scored', 0)}",
        f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
        f"- Evidence validity rate: {summary.get('evidence_validity_rate', 0.0):.4f}",
        "",
        "## Overall Scores",
        "",
        f"Published overall target: {PUBLISHED_OVERALL['per_item']:.2f} per item / "
        f"{PUBLISHED_OVERALL['per_letter']:.2f} per letter.",
        "",
    ]
    lines.extend(_score_block("semantic (CUI dropped)", scores["semantic"], ci["semantic"]))
    lines.extend(_score_block("benchmark (with CUI)", scores["benchmark"], ci["benchmark"]))
    lines.extend(_score_block("phrase_only", scores["phrase_only"], None))

    dev_ref = dev_ref or {}
    lines.extend(
        [
            "## Dev -> Audit Gap",
            "",
            "| Config | per-item | per-letter |",
            "| --- | --- | --- |",
        ]
    )
    for name in ("semantic", "benchmark", "phrase_only"):
        item_dev, letter_dev = dev_ref.get(name, (None, None))
        lines.append(
            f"| {name} | {_fmt_gap(scores[name].per_item.f1, item_dev)} "
            f"| {_fmt_gap(scores[name].per_letter.f1, letter_dev)} |"
        )

    lines.extend(["", "## Per-Entity Semantic F1", ""])
    lines.append("| Entity | Published item F1 | Item F1 | Letter F1 |")
    lines.append("| --- | ---: | ---: | ---: |")
    for entity in ENTITY_NAMES:
        entity_score = scores["semantic"].per_entity[entity]
        lines.append(
            f"| {entity} | {PUBLISHED_PER_ENTITY_ITEM_F1[entity]:.2f} "
            f"| {entity_score.per_item.f1:.3f} | {entity_score.per_letter.f1:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Reading",
            "",
            "The all-entity single-pass prompt is contract-clean but not competitive: "
            "it over-emits broad surface phrases and misses exact benchmark phrase/"
            "attribute bundles. The with-CUI benchmark score is structurally 0.000 "
            "because the LLM-only slice emits no CUI; semantic is the meaningful "
            "LLM-only quality read for this pass.",
            "",
            f"Bootstrap: percentile CI over letters, {BOOTSTRAP_SAMPLES} samples, "
            f"seed {BOOTSTRAP_SEED}.",
            "",
        ]
    )
    return "\n".join(lines)


def _append_registry_row(
    *,
    registry_path: Path,
    run_id: str,
    md_path: Path,
    jsonl_path: Path,
    model: str,
    generated_on: str,
    git_head: str,
    n_letters: int,
    scores: dict[str, Any],
    ci: dict[str, dict[str, tuple[float, float]]],
    summary: dict[str, Any],
) -> None:
    primary_metrics: dict[str, Any] = {
        "git_head": git_head,
        "authorization": AUTHORIZATION,
        "prompt_version": PROMPT_VERSION,
        "call_failures": summary.get("call_failures", 0),
        "parse_failures": summary.get("parse_failures", 0),
        "evidence_validity_rate": summary.get("evidence_validity_rate", 0.0),
        "mentions_raw": summary.get("n_mentions_raw", 0),
        "mentions_scored": summary.get("n_mentions_scored", 0),
    }
    for name in ("semantic", "benchmark", "phrase_only"):
        primary_metrics[f"{name}_per_item_f1"] = round(scores[name].per_item.f1, 4)
        primary_metrics[f"{name}_per_letter_f1"] = round(scores[name].per_letter.f1, 4)
    primary_metrics["semantic_per_item_ci"] = list(ci["semantic"]["per_item"])
    primary_metrics["semantic_per_letter_ci"] = list(ci["semantic"]["per_letter"])
    primary_metrics["benchmark_per_item_ci"] = list(ci["benchmark"]["per_item"])
    primary_metrics["benchmark_per_letter_ci"] = list(ci["benchmark"]["per_letter"])

    row = {
        "run_id": run_id,
        "artifact_paths": [str(jsonl_path).replace("\\", "/"), str(md_path).replace("\\", "/")],
        "date": generated_on,
        "pipeline_family": PIPELINE_FAMILY,
        "split": AUDIT_SURFACE,
        "row_count": n_letters,
        "model": model,
        "mode": "live",
        "replay_status": "live",
        "decision": "historical",
        "model_role": "ExECTv2 Phase 7 frozen full-200 overall all-entity LLM-only audit.",
        "evidence_validity": "frozen audit; exact substring evidence gate recorded in report.",
        "repair_mode": None,
        "cache_reuse_source": None,
        "superseded_by": None,
        "supersedes": [],
        "primary_metrics": primary_metrics,
        "claim_language_notes": (
            f"Phase 7 frozen overall all-entity audit. Semantic overall F1 "
            f"{scores['semantic'].per_item.f1:.3f}/{scores['semantic'].per_letter.f1:.3f}; "
            f"benchmark with-CUI F1 {scores['benchmark'].per_item.f1:.3f}/"
            f"{scores['benchmark'].per_letter.f1:.3f}; locked at git {git_head}."
        ),
    }
    with registry_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ExECTv2 Phase 7 frozen full-200 overall all-entity audit",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=4000)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--progress-every", type=int, default=10)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--no-register", action="store_true")
    parser.add_argument("--git-head", default=None)
    args = parser.parse_args()

    generated_on = date.today().isoformat()
    date_slug = generated_on.replace("-", "")
    model_slug = args.model.split("/")[-1].replace("-", "").replace(".", "")
    run_id = f"exectv2_audit_llm_only_all_entities_full200_{model_slug}_{date_slug}"
    jsonl_path = Path("experiments") / f"{run_id}.jsonl"
    md_path = Path("experiments") / f"{run_id}.md"
    git_head = args.git_head or _git_head()

    print(f"[audit] AUTHORIZATION: {AUTHORIZATION}", flush=True)
    print(f"[audit] locked code: git {git_head}", flush=True)
    letters = load_letters()
    print(f"[audit] loaded full corpus: {len(letters)} letters", flush=True)

    rows, metadata = run_split(
        letters,
        split=AUDIT_SURFACE,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        mode="live",
        progress_every=args.progress_every,
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=md_path,
        resume=args.resume,
    )
    write_jsonl(rows, jsonl_path)

    gold_letters = _letters_from_rows(rows, key="gold_mentions")
    pred_letters = _letters_from_rows(rows, key="predicted_mentions")
    scores = {
        "semantic": score_overall(gold_letters, pred_letters, ENTITY_NAMES, semantic_config_for),
        "benchmark": score_overall(gold_letters, pred_letters, ENTITY_NAMES, benchmark_config_for),
        "phrase_only": score_overall(
            gold_letters,
            pred_letters,
            ENTITY_NAMES,
            lambda _entity: MatchConfig(include_attributes=False),
        ),
    }
    ci = {
        "semantic": _bootstrap_ci(_letter_records(gold_letters, pred_letters, semantic_config_for)),
        "benchmark": _bootstrap_ci(
            _letter_records(gold_letters, pred_letters, benchmark_config_for)
        ),
    }
    summary = metadata.get("summary", {})
    report = _render_report(
        scores=scores,
        ci=ci,
        dev_ref=_dev_reference(args.registry, args.model),
        summary=summary,
        jsonl_path=jsonl_path,
        git_head=git_head,
        generated_on=generated_on,
        model=args.model,
        n_letters=len(letters),
    )
    md_path.write_text(report, encoding="utf-8")
    write_report(
        rows,
        metadata,
        md_path.with_name(md_path.stem + "_run_summary.md"),
        jsonl_path=jsonl_path,
    )

    if not args.no_register:
        _append_registry_row(
            registry_path=args.registry,
            run_id=run_id,
            md_path=md_path,
            jsonl_path=jsonl_path,
            model=args.model,
            generated_on=generated_on,
            git_head=git_head,
            n_letters=len(letters),
            scores=scores,
            ci=ci,
            summary=summary,
        )

    print(
        "[audit] semantic overall "
        f"{scores['semantic'].per_item.f1:.3f}/{scores['semantic'].per_letter.f1:.3f}; "
        "benchmark "
        f"{scores['benchmark'].per_item.f1:.3f}/{scores['benchmark'].per_letter.f1:.3f}",
        flush=True,
    )
    print(f"[audit] wrote {md_path}", flush=True)


if __name__ == "__main__":
    main()
