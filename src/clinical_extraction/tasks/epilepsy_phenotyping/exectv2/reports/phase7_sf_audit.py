"""Phase 7 frozen SeizureFrequency audit report and scoring helpers."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.pipeline import (
    run_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.artifact_io import (
    write_artifact_bundle,
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

PUBLISHED_PER_ITEM_F1 = 0.66
PUBLISHED_PER_LETTER_F1 = 0.68
AUTHORIZATION = "full-200 read authorized by user 2026-06-11 (Phase 7)"
AUDIT_SURFACE = "full200_audit"
BOOTSTRAP_SAMPLES = 5000
BOOTSTRAP_SEED = 20260611

CONFIGS: tuple[tuple[str, MatchConfig], ...] = (
    ("phrase_only", PHRASE_ONLY),
    ("sf_semantic", SF_SEMANTIC),
    ("sf_benchmark", SF_BENCHMARK),
)

PIPELINE_FAMILY = {
    "rules": "exectv2_deterministic",
    "llm_only_single_pass": "exectv2_llm_only_single_pass",
    "llm_only_per_entity": "exectv2_llm_only_per_entity",
    "llm_only_clinical_findings": "exectv2_llm_only_clinical_findings",
    "hybrid": "exectv2_hybrid",
}


class LetterRecord:
    __slots__ = ("item_tp", "item_fp", "item_fn", "gold_present", "any_correct", "pred_present")

    def __init__(self, item_tp, item_fp, item_fn, gold_present, any_correct, pred_present):
        self.item_tp = item_tp
        self.item_fp = item_fp
        self.item_fn = item_fn
        self.gold_present = gold_present
        self.any_correct = any_correct
        self.pred_present = pred_present


def letter_records(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    config: MatchConfig,
) -> list[LetterRecord]:
    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    records: list[LetterRecord] = []
    for letter_id in sorted(gold_by_id.keys() | pred_by_id.keys()):
        gold_m = (
            gold_by_id[letter_id].entities(SEIZURE_FREQUENCY.name)
            if letter_id in gold_by_id
            else ()
        )
        pred_m = (
            pred_by_id[letter_id].entities(SEIZURE_FREQUENCY.name)
            if letter_id in pred_by_id
            else ()
        )
        item = multiset_prf1(_keys(gold_m, config), _keys(pred_m, config))
        records.append(
            LetterRecord(
                item.tp,
                item.fp,
                item.fn,
                len(gold_m) > 0,
                item.tp > 0,
                len(pred_m) > 0,
            )
        )
    return records


def aggregate(records: Sequence[LetterRecord]) -> tuple[float, float]:
    it_tp = sum(record.item_tp for record in records)
    it_fp = sum(record.item_fp for record in records)
    it_fn = sum(record.item_fn for record in records)
    l_tp = sum(1 for record in records if record.gold_present and record.any_correct)
    l_fn = sum(1 for record in records if record.gold_present and not record.any_correct)
    l_fp = sum(1 for record in records if not record.gold_present and record.pred_present)
    return (
        prf1_from_counts(it_tp, it_fp, it_fn).f1,
        prf1_from_counts(l_tp, l_fp, l_fn).f1,
    )


def score_all(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> dict[str, EntityScore]:
    return {
        name: score_entity(gold_letters, pred_letters, SEIZURE_FREQUENCY.name, cfg)
        for name, cfg in CONFIGS
    }


def reconstruct_from_rows(rows: Sequence[dict], key: str) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        anns = tuple(
            ExectAnnotation(
                entity=SEIZURE_FREQUENCY.name,
                text=m["text"],
                attributes=m.get("attributes", {}),
            )
            for m in (row.get(key) or [])
        )
        letters.append(ExectLetter(letter_id=row["letter_id"], note_text="", annotations=anns))
    return letters


def run_rules_predictions(
    letters: Sequence[ExectLetter],
) -> tuple[list[ExectLetter], dict[str, Any]]:
    predicted = run_on_letters(list(letters))
    pred_letters = [
        to_exect_letter(prediction, note_text=gold.note_text)
        for prediction, gold in zip(predicted, letters, strict=True)
    ]
    n_pred = sum(len(prediction.mentions) for prediction in predicted)
    meta = {
        "mode": "deterministic",
        "replay_status": "analysis_only",
        "model": "(model-independent)",
        "prompt_version": "n/a (deterministic rules)",
        "gates": {
            "schema_validity_rate": 1.0,
            "repair_rate": 0.0,
            "evidence_validity_rate": 1.0,
            "call_failures": 0,
            "parse_failures": 0,
            "n_mentions": n_pred,
        },
    }
    return pred_letters, meta


def build_rules_jsonl(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> str:
    lines: list[str] = []
    for gold, pred in zip(gold_letters, pred_letters, strict=True):
        lines.append(
            json.dumps(
                {
                    "letter_id": gold.letter_id,
                    "gold_mentions": [
                        {"text": annotation.text, "attributes": dict(annotation.attributes)}
                        for annotation in gold.entities(SEIZURE_FREQUENCY.name)
                    ],
                    "predicted_mentions": [
                        {"text": annotation.text, "attributes": dict(annotation.attributes)}
                        for annotation in pred.entities(SEIZURE_FREQUENCY.name)
                    ],
                }
            )
        )
    return "\n".join(lines) + "\n"


def dev_reference(
    architecture: str, model: str, registry_path: Path
) -> dict[str, tuple[float, float]] | None:
    if architecture == "rules":
        dev = load_letters_for_split("dev")
        pred, _ = run_rules_predictions(dev)
        scores = score_all(dev, pred)
        return {
            name: (round(score.per_item.f1, 4), round(score.per_letter.f1, 4))
            for name, score in scores.items()
        }

    family = PIPELINE_FAMILY[architecture]
    best: dict | None = None
    for line in registry_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        if (
            row.get("pipeline_family") == family
            and row.get("model") == model
            and row.get("split") == "dev"
        ):
            if best is None or int(row.get("row_count", 0)) > int(best.get("row_count", 0)):
                best = row
    if best is None:
        return None
    primary_metrics = best.get("primary_metrics", {})
    out: dict[str, tuple[float, float]] = {}
    for name, _ in CONFIGS:
        per_item = primary_metrics.get(f"{name}_per_item_f1")
        per_letter = primary_metrics.get(f"{name}_per_letter_f1")
        if per_item is not None and per_letter is not None:
            out[name] = (float(per_item), float(per_letter))
    return out or None


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
    per_item = headline.per_item.f1
    per_letter = headline.per_letter.f1
    ci_per_item = ci["per_item"]
    ci_per_letter = ci["per_letter"]
    beat_item = ci_per_item[0] > PUBLISHED_PER_ITEM_F1
    beat_letter = ci_per_letter[0] > PUBLISHED_PER_LETTER_F1

    def verdict(point: float, target: float, lower: float) -> str:
        if lower > target:
            return f"**clears** {target:.2f} (CI lower {lower:.3f} > target)"
        if point > target:
            return f"point estimate {point:.3f} > {target:.2f} but CI includes it (lo {lower:.3f})"
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
        f"- **Per-item F1 {per_item:.3f}** (95% CI {ci_per_item[0]:.3f}–{ci_per_item[1]:.3f}) — "
        f"{verdict(per_item, PUBLISHED_PER_ITEM_F1, ci_per_item[0])}",
        f"- **Per-letter F1 {per_letter:.3f}** (95% CI {ci_per_letter[0]:.3f}–{ci_per_letter[1]:.3f}) — "
        f"{verdict(per_letter, PUBLISHED_PER_LETTER_F1, ci_per_letter[0])}",
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
    for name, _ in CONFIGS:
        score = scores[name]
        dev_item = _fmt_gap(score.per_item.f1, dev_ref.get(name, (None, None))[0])
        dev_letter = _fmt_gap(score.per_letter.f1, dev_ref.get(name, (None, None))[1])
        bold = "**" if name == "sf_benchmark" else ""
        lines.append(
            f"| {bold}`{name}`{bold} "
            f"| {score.per_item.precision:.3f} | {score.per_item.recall:.3f} "
            f"| {bold}{score.per_item.f1:.3f}{bold} "
            f"| {score.per_letter.precision:.3f} | {score.per_letter.recall:.3f} "
            f"| {bold}{score.per_letter.f1:.3f}{bold} "
            f"| {dev_item} | {dev_letter} |"
        )

    semantic_tp = scores["sf_semantic"].per_item.tp
    benchmark_tp = scores["sf_benchmark"].per_item.tp
    if benchmark_tp == 0 and semantic_tp > 0:
        lines += [
            "",
            "## CUI note (why the headline is 0.000)",
            "",
            "This architecture does **not emit the `CUI` attribute**. The headline "
            "`sf_benchmark` config keeps CUI (protocol §2, user-pinned), so no "
            "prediction can match the gold CUI and the headline collapses to 0.000 "
            "even though phrase and semantic-attribute extraction are non-trivial "
            f"(`sf_semantic` keeps {semantic_tp} per-item matches; `phrase_only` keeps "
            f"{scores['phrase_only'].per_item.tp}). Read `sf_semantic` (CUI dropped) "
            "as this architecture's attribute-level quality. This is the exact "
            "CUI-divergence §2 made the headline policy guard against — surfaced, "
            "not hidden.",
        ]

    lines += ["", "## Gates & reliability trail (protocol §5)", ""]
    for key, value in gates.items():
        if value is None or value == {} or value == "":
            continue
        lines.append(f"- `{key}`: {value}")

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


def append_registry_row(
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
    primary: dict[str, Any] = {"git_head": git_head, "authorization": AUTHORIZATION}
    for name, _ in CONFIGS:
        score = scores[name]
        primary[f"{name}_per_item_f1"] = round(score.per_item.f1, 4)
        primary[f"{name}_per_letter_f1"] = round(score.per_letter.f1, 4)
    primary["sf_benchmark_per_item_ci"] = list(ci["per_item"])
    primary["sf_benchmark_per_letter_ci"] = list(ci["per_letter"])
    if meta.get("prompt_version"):
        primary["prompt_version"] = meta["prompt_version"]
    for key in ("call_failures", "parse_failures"):
        if key in meta.get("gates", {}):
            primary[key] = meta["gates"][key]

    row = {
        "run_id": run_id,
        "artifact_paths": [str(md_path).replace("\\", "/"), str(jsonl_path).replace("\\", "/")],
        "date": generated_on,
        "pipeline_family": pipeline_family,
        "split": AUDIT_SURFACE,
        "row_count": n_letters,
        "model": meta.get("model"),
        "mode": meta.get("mode"),
        "replay_status": meta.get("replay_status", "live"),
        "decision": "historical",
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
    with registry_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row) + "\n")
    return run_id


def write_audit_artifacts(
    *,
    jsonl_path: Path,
    md_path: Path,
    jsonl_content: str | None,
    markdown: str,
) -> None:
    artifacts: dict[Path, str] = {md_path: markdown}
    if jsonl_content is not None:
        artifacts[jsonl_path] = jsonl_content
    write_artifact_bundle(artifacts)
