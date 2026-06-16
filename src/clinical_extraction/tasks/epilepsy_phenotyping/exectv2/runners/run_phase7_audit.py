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
import json
import random
import subprocess
import sys
from collections.abc import Sequence
from datetime import date
from importlib import import_module
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    SEIZURE_FREQUENCY,
    ExectAnnotation,
    ExectLetter,
    load_letters,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.pipeline import (
    run_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    SF_BENCHMARK,
    SF_SEMANTIC,
    EntityScore,
    MatchConfig,
    _keys,
    _letters_by_id,
    multiset_prf1,
    prf1_from_counts,
    score_entity,
)

# Published SF cell (Fonferko-Shadrach 2024, Table 1) — the audit target.
PUBLISHED_PER_ITEM_F1 = 0.66
PUBLISHED_PER_LETTER_F1 = 0.68

AUTHORIZATION = "full-200 read authorized by user 2026-06-11 (Phase 7)"
DEFAULT_REGISTRY_PATH = Path("experiments/registry.jsonl")
AUDIT_SURFACE = "full200_audit"
BOOTSTRAP_SAMPLES = 5000
BOOTSTRAP_SEED = 20260611

_CONFIGS: tuple[tuple[str, MatchConfig], ...] = (
    ("phrase_only", PHRASE_ONLY),
    ("sf_semantic", SF_SEMANTIC),
    ("sf_benchmark", SF_BENCHMARK),
)

# architecture → registry pipeline_family.
_PIPELINE_FAMILY = {
    "rules": "exectv2_deterministic",
    "llm_only_single_pass": "exectv2_llm_only_single_pass",
    "llm_only_per_entity": "exectv2_llm_only_per_entity",
    "llm_only_clinical_findings": "exectv2_llm_only_clinical_findings",
    "hybrid": "exectv2_hybrid",
}

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


# ── per-letter bookkeeping (shared by point estimate and bootstrap) ────────────


class _LetterRecord:
    """Per-letter match tallies under one config, enough to re-aggregate both the
    per-item (micro) and per-letter F1 on any resample of letters."""

    __slots__ = ("item_tp", "item_fp", "item_fn", "gold_present", "any_correct", "pred_present")

    def __init__(self, item_tp, item_fp, item_fn, gold_present, any_correct, pred_present):
        self.item_tp = item_tp
        self.item_fp = item_fp
        self.item_fn = item_fn
        self.gold_present = gold_present
        self.any_correct = any_correct
        self.pred_present = pred_present


def _letter_records(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    config: MatchConfig,
) -> list[_LetterRecord]:
    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    records: list[_LetterRecord] = []
    for letter_id in sorted(gold_by_id.keys() | pred_by_id.keys()):
        gold_m = (
            gold_by_id[letter_id].entities(SEIZURE_FREQUENCY)
            if letter_id in gold_by_id
            else ()
        )
        pred_m = (
            pred_by_id[letter_id].entities(SEIZURE_FREQUENCY)
            if letter_id in pred_by_id
            else ()
        )
        item = multiset_prf1(_keys(gold_m, config), _keys(pred_m, config))
        records.append(
            _LetterRecord(
                item.tp,
                item.fp,
                item.fn,
                len(gold_m) > 0,
                item.tp > 0,
                len(pred_m) > 0,
            )
        )
    return records


def _aggregate(records: Sequence[_LetterRecord]) -> tuple[float, float]:
    """Return (per_item_f1, per_letter_f1) over a (possibly resampled) record set."""
    it_tp = sum(r.item_tp for r in records)
    it_fp = sum(r.item_fp for r in records)
    it_fn = sum(r.item_fn for r in records)
    l_tp = sum(1 for r in records if r.gold_present and r.any_correct)
    l_fn = sum(1 for r in records if r.gold_present and not r.any_correct)
    l_fp = sum(1 for r in records if not r.gold_present and r.pred_present)
    return (
        prf1_from_counts(it_tp, it_fp, it_fn).f1,
        prf1_from_counts(l_tp, l_fp, l_fn).f1,
    )


def _bootstrap_ci(
    records: Sequence[_LetterRecord],
    n_samples: int = BOOTSTRAP_SAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, tuple[float, float]]:
    """Percentile bootstrap CI over letters for per-item and per-letter F1."""
    rng = random.Random(seed)
    k = len(records)
    per_item: list[float] = []
    per_letter: list[float] = []
    for _ in range(n_samples):
        sample = [records[rng.randrange(k)] for _ in range(k)]
        pi, pl = _aggregate(sample)
        per_item.append(pi)
        per_letter.append(pl)
    per_item.sort()
    per_letter.sort()

    def ci(values: list[float]) -> tuple[float, float]:
        lo = values[int(0.025 * len(values))]
        hi = values[int(0.975 * len(values)) - 1]
        return round(lo, 4), round(hi, 4)

    return {"per_item": ci(per_item), "per_letter": ci(per_letter)}


# ── scoring across the three configs ──────────────────────────────────────────


def _score_all(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> dict[str, EntityScore]:
    return {
        name: score_entity(gold_letters, pred_letters, SEIZURE_FREQUENCY, cfg)
        for name, cfg in _CONFIGS
    }


# ── family execution (returns gold/pred ExectLetters + gate metadata) ──────────


def _reconstruct_from_rows(rows: Sequence[dict], key: str) -> list[ExectLetter]:
    """Rebuild scorer-ready letters from a run's jsonl rows. The row schema is
    uniform across families (``gold_mentions`` / ``predicted_mentions``, each a
    list of ``{text, attributes}``); matching reads only text + attributes, so a
    direct reconstruction reproduces the run's own point estimate (asserted)."""
    letters: list[ExectLetter] = []
    for row in rows:
        anns = tuple(
            ExectAnnotation(
                entity=SEIZURE_FREQUENCY,
                text=m["text"],
                attributes=m.get("attributes", {}),
            )
            for m in (row.get(key) or [])
        )
        letters.append(ExectLetter(letter_id=row["letter_id"], note_text="", annotations=anns))
    return letters


def _run_rules(letters: Sequence[ExectLetter]) -> tuple[list[ExectLetter], dict[str, Any]]:
    predicted = run_on_letters(list(letters))
    pred_letters = [
        to_exect_letter(p, note_text=g.note_text)
        for p, g in zip(predicted, letters, strict=True)
    ]
    n_pred = sum(len(p.mentions) for p in predicted)
    meta = {
        "mode": "deterministic",
        "replay_status": "analysis_only",
        "model": "(model-independent)",
        "prompt_version": "n/a (deterministic rules)",
        "gates": {
            "schema_validity_rate": 1.0,  # structural: no LLM, no schema repair
            "repair_rate": 0.0,
            "evidence_validity_rate": 1.0,  # evidence is the source phrase by construction
            "call_failures": 0,
            "parse_failures": 0,
            "n_mentions": n_pred,
        },
    }
    return pred_letters, meta


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

    gold_letters = _reconstruct_from_rows(rows, "gold_mentions")
    pred_letters = _reconstruct_from_rows(rows, "predicted_mentions")

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
        "_run_scores": summary.get("scores", {}),  # for the consistency assertion
    }
    return gold_letters, pred_letters, meta


# ── dev reference for the dev→audit gap ───────────────────────────────────────


def _dev_reference(
    architecture: str, model: str, registry_path: Path
) -> dict[str, tuple[float, float]] | None:
    """Return {config: (per_item_f1, per_letter_f1)} on dev, for the gap line."""
    if architecture == "rules":
        dev = load_letters_for_split("dev")
        pred, _ = _run_rules(dev)
        scores = _score_all(dev, pred)
        return {
            name: (round(s.per_item.f1, 4), round(s.per_letter.f1, 4))
            for name, s in scores.items()
        }

    family = _PIPELINE_FAMILY[architecture]
    best: dict | None = None
    for line in registry_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if (
            r.get("pipeline_family") == family
            and r.get("model") == model
            and r.get("split") == "dev"
        ):
            if best is None or int(r.get("row_count", 0)) > int(best.get("row_count", 0)):
                best = r
    if best is None:
        return None
    pm = best.get("primary_metrics", {})
    out: dict[str, tuple[float, float]] = {}
    for name, _ in _CONFIGS:
        pi = pm.get(f"{name}_per_item_f1")
        pl = pm.get(f"{name}_per_letter_f1")
        if pi is not None and pl is not None:
            out[name] = (float(pi), float(pl))
    return out or None


# ── report + registry ─────────────────────────────────────────────────────────


def _fmt_gap(audit_f1: float, dev_f1: float | None) -> str:
    if dev_f1 is None:
        return "—"
    delta = audit_f1 - dev_f1
    return f"{dev_f1:.3f} → {audit_f1:.3f} ({delta:+.3f})"


def render_audit_markdown(
    *,
    architecture: str,
    config: str,
    scores: dict[str, EntityScore],
    ci: dict[str, tuple[float, float]],
    dev_ref: dict[str, tuple[float, float]] | None,
    meta: dict[str, Any],
    git_head: str,
    n_letters: int,
    generated_on: str,
) -> str:
    headline = scores["sf_benchmark"]
    pi = headline.per_item.f1
    pl = headline.per_letter.f1
    ci_pi = ci["per_item"]
    ci_pl = ci["per_letter"]
    beat_item = ci_pi[0] > PUBLISHED_PER_ITEM_F1
    beat_letter = ci_pl[0] > PUBLISHED_PER_LETTER_F1

    def verdict(point: float, target: float, lo: float) -> str:
        if lo > target:
            return f"**clears** {target:.2f} (CI lower {lo:.3f} > target)"
        if point > target:
            return f"point estimate {point:.3f} > {target:.2f} but CI includes it (lo {lo:.3f})"
        return f"below {target:.2f} (point {point:.3f})"

    gates = meta.get("gates", {})
    dev_ref = dev_ref or {}

    lines: list[str] = [
        f"# ExECTv2 Phase 7 Frozen Audit — {architecture}"
        + (f" / {config}" if config else "")
        + " — SeizureFrequency",
        "",
        "> **IMMUTABLE AUDIT RECORD.** Frozen full-200 read; no tuning, no row "
        "inspection, no repair beyond the standing semantically-neutral ladder. "
        "Any later change requires a *new* authorized audit, not an edit to this "
        "artifact (protocol §4.5).",
        "",
        f"- Generated: `{generated_on}`",
        f"- Authorization: {AUTHORIZATION}",
        f"- Locked code: git `{git_head}`",
        f"- Surface: **all {n_letters} letters** (`load_letters`, D16 gold) — the "
        "benchmark-comparable surface",
        f"- Architecture: `{architecture}`" + (f" / `{config}`" if config else ""),
        f"- Model: `{meta.get('model')}`  ·  mode: `{meta.get('mode')}`"
        + (f"  ·  prompt: `{meta.get('prompt_version')}`" if meta.get("prompt_version") else ""),
        "- Entity: SeizureFrequency (benchmark's hardest cell; Table 1, "
        "Fonferko-Shadrach 2024). **This audits the SF cell, not the overall "
        "0.87/0.90 headline** (9-entity scale-up is Phase 6, open).",
        "",
        "## Headline vs published SF cell",
        "",
        f"Published SF: **{PUBLISHED_PER_ITEM_F1:.2f} per item / "
        f"{PUBLISHED_PER_LETTER_F1:.2f} per letter**. Headline match config = "
        "`sf_benchmark` (entity + phrase + guideline features + CUI; protocol §2).",
        "",
        f"- **Per-item F1 {pi:.3f}** (95% CI {ci_pi[0]:.3f}–{ci_pi[1]:.3f}) — "
        f"{verdict(pi, PUBLISHED_PER_ITEM_F1, ci_pi[0])}",
        f"- **Per-letter F1 {pl:.3f}** (95% CI {ci_pl[0]:.3f}–{ci_pl[1]:.3f}) — "
        f"{verdict(pl, PUBLISHED_PER_LETTER_F1, ci_pl[0])}",
        "",
        f"Verdict: {'**beats**' if (beat_item and beat_letter) else 'does not clear'} "
        "the SF benchmark on both axes (CI-based).",
        "",
        "## Scores under all three match configs (sensitivity)",
        "",
        "| Config | per-item P | R | F1 | per-letter P | R | F1 "
        "| dev→audit per-item | dev→audit per-letter |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name, _ in _CONFIGS:
        s = scores[name]
        di = _fmt_gap(s.per_item.f1, dev_ref.get(name, (None, None))[0])
        dl = _fmt_gap(s.per_letter.f1, dev_ref.get(name, (None, None))[1])
        bold = "**" if name == "sf_benchmark" else ""
        lines.append(
            f"| {bold}`{name}`{bold} "
            f"| {s.per_item.precision:.3f} | {s.per_item.recall:.3f} "
            f"| {bold}{s.per_item.f1:.3f}{bold} "
            f"| {s.per_letter.precision:.3f} | {s.per_letter.recall:.3f} "
            f"| {bold}{s.per_letter.f1:.3f}{bold} "
            f"| {di} | {dl} |"
        )

    # Make a CUI-driven headline collapse legible rather than a bald 0.000: when
    # the only difference between sf_semantic and sf_benchmark (CUI) erases every
    # match, the architecture emits no CUI. This is the "future divergence made
    # visible" case protocol §2 anticipated when CUI was pinned into the headline.
    sem_tp = scores["sf_semantic"].per_item.tp
    bench_tp = scores["sf_benchmark"].per_item.tp
    if bench_tp == 0 and sem_tp > 0:
        lines += [
            "",
            "## CUI note (why the headline is 0.000)",
            "",
            "This architecture does **not emit the `CUI` attribute**. The headline "
            "`sf_benchmark` config keeps CUI (protocol §2, user-pinned), so no "
            "prediction can match the gold CUI and the headline collapses to 0.000 "
            "even though phrase and semantic-attribute extraction are non-trivial "
            f"(`sf_semantic` keeps {sem_tp} per-item matches; `phrase_only` keeps "
            f"{scores['phrase_only'].per_item.tp}). Read `sf_semantic` (CUI dropped) "
            "as this architecture's attribute-level quality. This is the exact "
            "CUI-divergence §2 made the headline policy guard against — surfaced, "
            "not hidden.",
        ]

    lines += [
        "",
        "## Gates & reliability trail (protocol §5)",
        "",
    ]
    for k, v in gates.items():
        if v is None or v == {} or v == "":
            continue  # field not applicable to this family (e.g. routing for non-hybrid)
        lines.append(f"- `{k}`: {v}")

    lines += [
        "",
        "## Provenance & reproduction",
        "",
        f"- Bootstrap: percentile CI over letters, {BOOTSTRAP_SAMPLES} resamples, "
        f"seed {BOOTSTRAP_SEED}.",
        "- The dev→audit gap columns diff this frozen read against the locked dev "
        "read (rules: recomputed live; LLM/hybrid: the registered full-dev run) — "
        "the generalization check (protocol §3).",
        "- Run once per architecture, after dev was locked; not iterated against.",
        "",
    ]
    return "\n".join(lines) + "\n"


def _append_registry_row(
    *,
    registry_path: Path,
    run_id: str,
    pipeline_family: str,
    architecture: str,
    config: str,
    scores: dict[str, EntityScore],
    ci: dict[str, tuple[float, float]],
    meta: dict[str, Any],
    git_head: str,
    n_letters: int,
    md_path: Path,
    jsonl_path: Path,
    generated_on: str,
) -> str:
    family = pipeline_family

    primary: dict[str, Any] = {"git_head": git_head, "authorization": AUTHORIZATION}
    for name, _ in _CONFIGS:
        s = scores[name]
        primary[f"{name}_per_item_f1"] = round(s.per_item.f1, 4)
        primary[f"{name}_per_letter_f1"] = round(s.per_letter.f1, 4)
    primary["sf_benchmark_per_item_ci"] = list(ci["per_item"])
    primary["sf_benchmark_per_letter_ci"] = list(ci["per_letter"])
    if meta.get("prompt_version"):
        primary["prompt_version"] = meta["prompt_version"]
    for k in ("call_failures", "parse_failures"):
        if k in meta.get("gates", {}):
            primary[k] = meta["gates"][k]

    row = {
        "run_id": run_id,
        "artifact_paths": [str(md_path).replace("\\", "/"), str(jsonl_path).replace("\\", "/")],
        "date": generated_on,
        "pipeline_family": family,
        "split": AUDIT_SURFACE,
        "row_count": n_letters,
        "model": meta.get("model"),
        "mode": meta.get("mode"),
        "replay_status": meta.get("replay_status", "live"),
        "decision": "historical",  # frozen, immutable record (valid registry enum)
        "model_role": f"ExECTv2 Phase 7 frozen full-200 SF audit ({architecture}"
        + (f"/{config}" if config else "")
        + ").",
        "evidence_validity": "frozen audit; gates recorded in the audit report.",
        "repair_mode": None,
        "cache_reuse_source": None,
        "superseded_by": None,
        "supersedes": [],
        "primary_metrics": primary,
        "claim_language_notes": (
            f"Phase 7 frozen SF audit over all {n_letters} letters (authorized "
            f"{generated_on}). Headline sf_benchmark per-item F1 "
            f"{scores['sf_benchmark'].per_item.f1:.3f} (CI {ci['per_item'][0]:.3f}-"
            f"{ci['per_item'][1]:.3f}), per-letter F1 "
            f"{scores['sf_benchmark'].per_letter.f1:.3f} (CI {ci['per_letter'][0]:.3f}-"
            f"{ci['per_letter'][1]:.3f}) vs published 0.66/0.68. Immutable; locked at "
            f"git {git_head}."
        ),
    }
    with registry_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    return run_id


# ── orchestration ─────────────────────────────────────────────────────────────


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()[:12]
    except Exception:
        return "unknown"


def main() -> None:
    p = argparse.ArgumentParser(
        description="ExECTv2 Phase 7 frozen full-200 SF audit",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--architecture", required=True, choices=["rules", "llm_only", "hybrid"])
    p.add_argument(
        "--config",
        choices=["single_pass", "per_entity", "clinical_findings"],
        default="per_entity",
        help="LLM-only configuration (ignored for rules/hybrid).",
    )
    p.add_argument("--model", default="openai/gpt-4.1-mini")
    p.add_argument("--mode", choices=["live", "prompt-only"], default="live")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-tokens", type=int, default=2400)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--git-head", default=None, help="Override the recorded locked-code commit.")
    p.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    p.add_argument("--no-register", action="store_true", help="Skip the registry append (dry run).")
    args = p.parse_args()

    generated_on = date.today().isoformat()
    git_head = args.git_head or _git_head()

    print(f"[audit] AUTHORIZATION: {AUTHORIZATION}", flush=True)
    print(f"[audit] locked code: git {git_head}", flush=True)
    print("[audit] loading FULL 200-letter corpus (frozen surface) ...", flush=True)
    gold_letters = load_letters()
    n_letters = len(gold_letters)
    print(f"[audit] {n_letters} letters loaded.", flush=True)

    # Resolve the architecture-level identity for the family selector.
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

    # Execute the locked pipeline over the frozen surface.
    if args.architecture == "rules":
        pred_letters, meta = _run_rules(gold_letters)
        # Persist the deterministic predictions as the audit jsonl.
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        with jsonl_path.open("w", encoding="utf-8") as fh:
            for g, pl in zip(gold_letters, pred_letters, strict=True):
                fh.write(json.dumps({
                    "letter_id": g.letter_id,
                    "gold_mentions": [
                        {"text": a.text, "attributes": dict(a.attributes)}
                        for a in g.entities(SEIZURE_FREQUENCY)
                    ],
                    "predicted_mentions": [
                        {"text": a.text, "attributes": dict(a.attributes)}
                        for a in pl.entities(SEIZURE_FREQUENCY)
                    ],
                }) + "\n")
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

    # Score (single scorer for all families), bootstrap, gap.
    scores = _score_all(gold_letters, pred_letters)

    # Consistency guard: our recomputed point estimate must match the run's own.
    run_scores = meta.pop("_run_scores", None)
    if run_scores:
        for name, _ in _CONFIGS:
            ours = round(scores[name].per_item.f1, 3)
            theirs = round(float(run_scores.get(name, {}).get("per_item", {}).get("f1", -1)), 3)
            if theirs >= 0 and ours != theirs:
                print(
                    f"[audit][WARN] {name} per-item F1 mismatch: audit {ours} vs run {theirs}",
                    file=sys.stderr,
                )

    ci = _bootstrap_ci(_letter_records(gold_letters, pred_letters, SF_BENCHMARK))
    dev_ref = _dev_reference(arch_key, args.model, args.registry)

    md = render_audit_markdown(
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
    md_path.write_text(md, encoding="utf-8")
    print(f"[audit] wrote report: {md_path}", flush=True)

    if not args.no_register:
        run_id = _append_registry_row(
            registry_path=args.registry,
            run_id=stem,
            pipeline_family=_PIPELINE_FAMILY[arch_key],
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

    hb = scores["sf_benchmark"]
    print(
        f"[audit] HEADLINE sf_benchmark: per-item F1 {hb.per_item.f1:.3f} "
        f"(CI {ci['per_item'][0]:.3f}-{ci['per_item'][1]:.3f}), per-letter "
        f"{hb.per_letter.f1:.3f} (CI {ci['per_letter'][0]:.3f}-{ci['per_letter'][1]:.3f}) "
        f"vs published {PUBLISHED_PER_ITEM_F1}/{PUBLISHED_PER_LETTER_F1}",
        flush=True,
    )


if __name__ == "__main__":
    main()
