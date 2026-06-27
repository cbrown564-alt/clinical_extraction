"""Phase 7 frozen benchmark audit for ExECTv2 SeizureFrequency.

This is the **only holdout-facing runner**. It executes a locked architecture
over the **full 200-letter corpus** (``load_letters``) — the surface the
published benchmark scored on, and therefore the only directly comparable
number — and emits an immutable audit artifact plus a registry row. It performs
**no tuning, no row inspection, no repair** beyond the standing
semantically-neutral text ladder already baked into the loaders.

Procedure (docs/plans/exectv2/06_evaluation_and_benchmark_protocol.md §4):

1. Lock the architecture (configs/prompts/code). Recorded here as the git HEAD
   the audit ran against — pass ``--git-head`` or let it read HEAD.
2. Obtain explicit user authorization for the full-200 read (granted 2026-06-11).
3. Run the locked pipeline over the frozen surface. One pass, no re-tuning.
4. Produce the aggregate report: per-item / per-letter F1 under the three pinned
   match configs (§2), the headline ``sf_benchmark`` vs the published 0.66/0.68
   with a bootstrap CI and margin, the gates, and the dev→audit gap.
5. Register the audit run as an immutable record.

Scope note: only SeizureFrequency is built across the three families (Phase 6,
the 9-entity scale-up, is open), so this audits the benchmark's **SF cell**, not
the overall 0.87/0.90 headline. The SF cell (0.66 per item / 0.68 per letter,
Fonferko-Shadrach 2024 Table 1) is the benchmark's hardest entity and the one the
SF-first strategy was built to clear.

Usage::

    # rules — instant, model-independent
    uv run python -m \\
        clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_phase7_audit \\
        --architecture rules

    # llm_only (per_entity) — live, long; use the detached Start-Process pattern
    uv run python -m \\
        clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_phase7_audit \\
        --architecture llm_only --config per_entity --model openai/gpt-4.1-mini \\
        --mode live --resume

    # hybrid — live, long
    uv run python -m \\
        clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_phase7_audit \\
        --architecture hybrid --model openai/gpt-4.1-mini --mode live --resume
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from datetime import date
from importlib import import_module
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.phase7_sf_audit import (
    AUDIT_SURFACE,
    AUTHORIZATION,
    BOOTSTRAP_SAMPLES,
    BOOTSTRAP_SEED,
    CONFIGS,
    PIPELINE_FAMILY,
    PUBLISHED_PER_ITEM_F1,
    PUBLISHED_PER_LETTER_F1,
    aggregate,
    append_registry_row,
    build_rules_jsonl,
    dev_reference,
    letter_records,
    reconstruct_from_rows,
    render_audit_markdown,
    run_rules_predictions,
    score_all,
    write_audit_artifacts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import SF_BENCHMARK
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.bootstrap import (
    bootstrap_cluster_metrics_ci,
)

DEFAULT_REGISTRY_PATH = Path("experiments/registry.jsonl")

_LLM_RUNNER_MODULES = {
    "single_pass": (
        "clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm."
        "llm_only_single_pass"
    ),
    "per_entity": (
        "clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm."
        "llm_only_per_entity"
    ),
    "clinical_findings": (
        "clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm."
        "llm_only_clinical_findings"
    ),
}

_HYBRID_RUNNER_MODULE = (
    "clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid."
    "clinical_assessment"
)


def _run_llm_family(
    architecture: str,
    config: str,
    letters: Sequence[ExectLetter],
    *,
    model: str,
    mode: str,
    temperature: float,
    max_tokens: int,
    resume: bool,
    jsonl_path: Path,
    report_path: Path,
) -> tuple[list[ExectLetter], list[ExectLetter], dict[str, Any]]:
    if architecture == "hybrid":
        runner_module = import_module(_HYBRID_RUNNER_MODULE)
    else:
        runner_module = import_module(_LLM_RUNNER_MODULES[config])
    run_split = runner_module.run_split
    write_jsonl = runner_module.write_jsonl
    write_report = runner_module.write_report

    rows, metadata = run_split(
        list(letters),
        split=AUDIT_SURFACE,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        dspy_cache=True,
        api_base=None,
        progress_every=25,
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        resume=resume,
    )
    write_jsonl(rows, jsonl_path)
    write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    gold_letters = reconstruct_from_rows(rows, "gold_mentions")
    pred_letters = reconstruct_from_rows(rows, "predicted_mentions")

    summary = metadata.get("summary", {})
    meta = {
        "mode": mode,
        "replay_status": "live",
        "model": model,
        "prompt_version": metadata.get("prompt_version", ""),
        "n_resumed": metadata.get("n_resumed", 0),
        "gates": {
            "call_failures": summary.get("call_failures", 0),
            "parse_failures": summary.get("parse_failures", 0),
            "n_candidates": summary.get("n_candidates"),
            "n_mentions_raw": summary.get("n_mentions_raw"),
            "n_mentions_scored": summary.get("n_mentions_scored"),
            "n_routed": summary.get("n_routed"),
            "routed_taxonomy": summary.get("routed_taxonomy", {}),
        },
        "_run_scores": summary.get("scores", {}),
    }
    return gold_letters, pred_letters, meta


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()[:12]
    except Exception:
        return "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ExECTv2 Phase 7 frozen full-200 SF audit",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--architecture", required=True, choices=["rules", "llm_only", "hybrid"])
    parser.add_argument(
        "--config",
        choices=["single_pass", "per_entity", "clinical_findings"],
        default="per_entity",
        help="LLM-only configuration (ignored for rules/hybrid).",
    )
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--mode", choices=["live", "prompt-only"], default="live")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=2400)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--git-head", default=None, help="Override the recorded locked-code commit.")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--no-register", action="store_true", help="Skip the registry append (dry run).")
    args = parser.parse_args()

    generated_on = date.today().isoformat()
    git_head = args.git_head or _git_head()

    print(f"[audit] AUTHORIZATION: {AUTHORIZATION}", flush=True)
    print(f"[audit] locked code: git {git_head}", flush=True)
    print("[audit] loading FULL 200-letter corpus (frozen surface) ...", flush=True)
    gold_letters = load_letters()
    n_letters = len(gold_letters)
    print(f"[audit] {n_letters} letters loaded.", flush=True)

    if args.architecture == "rules":
        arch_key, config_label = "rules", ""
    elif args.architecture == "llm_only":
        arch_key, config_label = f"llm_only_{args.config}", args.config
    else:
        arch_key, config_label = "hybrid", ""

    model_slug = args.model.split("/")[-1].replace("-", "").replace(".", "")
    stem = (
        f"exectv2_audit_{args.architecture}"
        + (f"_{config_label}" if config_label else "")
        + f"_full200_{model_slug if args.architecture != 'rules' else 'modelindependent'}"
        + f"_{generated_on.replace('-', '')}"
    )
    jsonl_path = Path("experiments") / f"{stem}.jsonl"
    md_path = Path("experiments") / f"{stem}.md"
    rules_jsonl: str | None = None

    if args.architecture == "rules":
        pred_letters, meta = run_rules_predictions(gold_letters)
        rules_jsonl = build_rules_jsonl(gold_letters, pred_letters)
    else:
        gold_letters, pred_letters, meta = _run_llm_family(
            args.architecture,
            args.config,
            gold_letters,
            model=args.model,
            mode=args.mode,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            resume=args.resume,
            jsonl_path=jsonl_path,
            report_path=md_path,
        )

    scores = score_all(gold_letters, pred_letters)

    run_scores = meta.pop("_run_scores", None)
    if run_scores:
        for name, _ in CONFIGS:
            ours = round(scores[name].per_item.f1, 3)
            theirs = round(float(run_scores.get(name, {}).get("per_item", {}).get("f1", -1)), 3)
            if theirs >= 0 and ours != theirs:
                print(
                    f"[audit][WARN] {name} per-item F1 mismatch: audit {ours} vs run {theirs}",
                    file=sys.stderr,
                )

    ci = bootstrap_cluster_metrics_ci(
        letter_records(gold_letters, pred_letters, SF_BENCHMARK),
        {
            "per_item": lambda sample: aggregate(sample)[0],
            "per_letter": lambda sample: aggregate(sample)[1],
        },
        reps=BOOTSTRAP_SAMPLES,
        seed=BOOTSTRAP_SEED,
    )
    dev_ref = dev_reference(arch_key, args.model, args.registry)

    markdown = render_audit_markdown(
        architecture=args.architecture,
        config=config_label,
        scores=scores,
        ci=ci,
        dev_ref=dev_ref,
        meta=meta,
        git_head=git_head,
        n_letters=n_letters,
        generated_on=generated_on,
    )
    write_audit_artifacts(
        jsonl_path=jsonl_path,
        md_path=md_path,
        jsonl_content=rules_jsonl,
        markdown=markdown,
    )
    print(f"[audit] wrote report: {md_path}", flush=True)

    if not args.no_register:
        run_id = append_registry_row(
            registry_path=args.registry,
            run_id=stem,
            pipeline_family=PIPELINE_FAMILY[arch_key],
            architecture=arch_key,
            config=config_label,
            scores=scores,
            ci=ci,
            meta=meta,
            git_head=git_head,
            n_letters=n_letters,
            md_path=md_path,
            jsonl_path=jsonl_path,
            generated_on=generated_on,
        )
        print(f"[audit] registered immutable run: {run_id}", flush=True)

    headline = scores["sf_benchmark"]
    print(
        f"[audit] HEADLINE sf_benchmark: per-item F1 {headline.per_item.f1:.3f} "
        f"(CI {ci['per_item'][0]:.3f}-{ci['per_item'][1]:.3f}), per-letter "
        f"{headline.per_letter.f1:.3f} (CI {ci['per_letter'][0]:.3f}-{ci['per_letter'][1]:.3f}) "
        f"vs published {PUBLISHED_PER_ITEM_F1}/{PUBLISHED_PER_LETTER_F1}",
        flush=True,
    )


if __name__ == "__main__":
    main()
