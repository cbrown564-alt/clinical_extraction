#!/usr/bin/env python3
"""No-call Qwen rescue-overfiring audit on Gan dev750.

See docs/research/gan2026/qwen_rescue_overfiring_protocol_2026-08-15.md.
Zero model calls. Never loads locked test450 rows.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import statistics
import subprocess
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence import (
    selected_evidence_derivation as _evidence_mod,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = REPO_ROOT / "docs/research/gan2026/qwen_rescue_overfiring_protocol_2026-08-15.md"
OUTPUT_PATH = REPO_ROOT / "experiments/gan2026_qwen_rescue_overfiring_20260815.json"
CURRENT_STACK_DIR = (
    REPO_ROOT / "experiments/gan2026_six_model_current_stack_dev750_replay_20260813"
)
FILLS_PATH = REPO_ROOT / "experiments/current_stack/latest/fills.json"
PANEL_PATH = REPO_ROOT / "experiments/current_stack/latest/panel_aggregate.json"
V05_DEV750_DIR = (
    REPO_ROOT / "scratch/validation/gan2026_matched_v05_dev750_20260727"
)
V05_PROMPT = "gan2026_hybrid_structured_events_v0.5"
V05_MINI = (
    CURRENT_STACK_DIR / "gpt41mini_v05_june07" / "validation750.rows.jsonl"
)
V05_GEMINI = CURRENT_STACK_DIR / "gemini37flash" / "validation750.rows.jsonl"
EXAMPLES_PER_KEY = 2

_ABLATION_PATH = REPO_ROOT / "scripts/build_gan2026_hybrid_stage_ablation.py"
_SPEC = importlib.util.spec_from_file_location("gan_hybrid_stage_ablation", _ABLATION_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Cannot import helpers from {_ABLATION_PATH}")
ablation = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(ablation)

_HS_PATH = REPO_ROOT / "scripts/build_six_model_hard_slice_error_modes.py"
_HS_SPEC = importlib.util.spec_from_file_location("hard_slice_error_modes", _HS_PATH)
if _HS_SPEC is None or _HS_SPEC.loader is None:
    raise RuntimeError(f"Cannot import helpers from {_HS_PATH}")
hs = importlib.util.module_from_spec(_HS_SPEC)
_HS_SPEC.loader.exec_module(hs)

V05_MODELS = (
    ("gpt41mini", "GPT-4.1-mini", "v0.5"),
    ("gpt56luna", "GPT-5.6 Luna", "v0.5"),
    ("gpt56sol", "GPT-5.6 Sol", "v0.5"),
    ("deepseek_v4_flash", "DeepSeek V4 Flash", "v0.5"),
    ("qwen36_35b", "Qwen 3.6:35B", "v0.5"),
    ("gemma4_26b", "Gemma 4 26B", "v0.5"),
    ("gemini37flash", "Gemini 3.7 Flash", "v0.5"),
)
ALL_MODELS = V05_MODELS
V05_SLUGS = tuple(slug for slug, _, _ in V05_MODELS)
FOCUS_SLUG = "qwen36_35b"
PEER_V05_SLUGS = tuple(slug for slug in V05_SLUGS if slug != FOCUS_SLUG)

REPAIR_STAGE_ORDER = ablation.REPAIR_STAGE_ORDER
BAND_ORDER = ablation.BAND_ORDER
STAGE_BAND = ablation.STAGE_BAND

ARMS = (
    "baseline",
    "evidence_same_family_only",
    "no_unknown_override",
    "exact_span_only",
)

BREAKTHROUGH_RE = re.compile(
    r"\bbreakthrough\b|"
    r"\bexcept\s+for\b|"
    r"\bthen\s+(?:had|experienced|suffered)\b|"
    r"seizure[-\s]free.{0,80}\b(?:then|until|before|followed|after which)\b",
    re.IGNORECASE | re.DOTALL,
)

JULY27_V05_DEV750_PURIST = {
    "gpt41mini": 668,
    "gpt56luna": 646,
    "gpt56sol": 656,
    "deepseek_v4_flash": 619,
    "qwen36_35b": 660,
    "gemma4_26b": 643,
}

def _git_note() -> dict[str, Any]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty_tree": None}
    return {"commit": commit, "dirty_tree": dirty}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line
    ]


def _source_path(slug: str) -> Path:
    if slug == "gemini37flash":
        return V05_GEMINI
    scratch = V05_DEV750_DIR / slug / "validation750.rows.jsonl"
    if scratch.is_file():
        return scratch
    if slug == "gpt41mini":
        return V05_MINI
    raise FileNotFoundError(
        f"matched v0.5 dev750 raw missing for {slug}: "
        f"{scratch.relative_to(REPO_ROOT).as_posix()} "
        "(Decision 0043; do not fall back to July 18 v0.7)"
    )


def _prompt_versions(path: Path) -> set[str]:
    return {str(row.get("prompt_version") or "") for row in _read_jsonl(path)}


def _available_models() -> tuple[tuple[str, str, str], ...]:
    found: list[tuple[str, str, str]] = []
    for slug, display, prompt in ALL_MODELS:
        try:
            path = _source_path(slug)
        except FileNotFoundError:
            continue
        if not path.is_file():
            continue
        versions = _prompt_versions(path)
        if versions != {V05_PROMPT}:
            raise SystemExit(
                f"{path.relative_to(REPO_ROOT).as_posix()} prompt {versions} != {V05_PROMPT}"
            )
        found.append((slug, display, prompt))
    return tuple(found)


def _label_kind(label: str | None) -> str | None:
    if label is None or not str(label).strip():
        return None
    try:
        return str(label_to_frequency_record(str(label)).kind)
    except (TypeError, ValueError):
        return "unparsed"


def _purist_ok(pred: str | None, gold: str) -> bool:
    return bool(ablation._purist_correct(pred, gold))


def _truncate(text: str | None, limit: int = 220) -> str | None:
    return ablation._truncate(text, limit)


def _selection_and_note(row: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    record = ablation._model_prediction_record(row)
    note = ablation._note_text(row)
    if record is None:
        return None, None, note
    selection = record.get("selection") or {}
    evidence = selection.get("evidence")
    final_label = selection.get("final_label")
    return (
        str(final_label) if final_label is not None else None,
        str(evidence) if evidence is not None else None,
        note,
    )


def _omit_for_arm(
    arm: str,
    *,
    resolved: str | None,
    evidence: str | None,
    note: str | None,
) -> frozenset[str]:
    if arm == "baseline" or resolved is None:
        return frozenset()
    resolved_kind = _label_kind(resolved)
    if arm == "no_unknown_override" and resolved_kind in {
        FrequencyLabelKind.UNKNOWN,
        FrequencyLabelKind.NO_REFERENCE,
    }:
        return frozenset(REPAIR_STAGE_ORDER)
    if arm == "exact_span_only":
        if not evidence or not note or not evidence_is_substring(note, evidence):
            return frozenset({"repair.selected_evidence"})
        return frozenset()
    if arm == "evidence_same_family_only":
        derived = _evidence_mod.prediction_label_from_selected_evidence(
            evidence or "", note
        )
        if derived and _label_kind(derived) != resolved_kind:
            return frozenset({"repair.selected_evidence"})
        return frozenset()
    return frozenset()


def _first_changer_class(
    changes: list[dict[str, str]],
    resolved: str | None,
) -> str | None:
    if not changes:
        return None
    first = changes[0]
    stage = first["stage"]
    if stage == "repair.selected_evidence":
        before_kind = _label_kind(resolved)
        after_kind = _label_kind(first.get("after"))
        parsed = {
            str(FrequencyLabelKind.FREQUENCY),
            str(FrequencyLabelKind.SEIZURE_FREE),
            str(FrequencyLabelKind.UNKNOWN),
            str(FrequencyLabelKind.NO_REFERENCE),
            str(FrequencyLabelKind.UNRESOLVED_MULTIPLE),
        }
        if before_kind not in parsed:
            return "render_unparsed"
        if after_kind == before_kind:
            return "render_same_family"
        return "family_rewrite"
    if stage == "repair.elapsed_anchor":
        return "compose_free_interval"
    return "clinical_reselect"


def _breakthrough_marked(evidence: str | None, note: str | None) -> bool:
    haystack = f"{evidence or ''}\n{note or ''}"
    return bool(BREAKTHROUGH_RE.search(haystack))


def _empty_stage_stats() -> dict[str, Any]:
    return {
        "fires": 0,
        "first_changer": 0,
        "first_rescue": 0,
        "first_harm": 0,
        "any_rescue": 0,
        "any_harm": 0,
    }


def _empty_model_acc() -> dict[str, int]:
    return {
        "n": 0,
        "replayable": 0,
        "unreplayable": 0,
        "model_final_purist": 0,
        "representation_purist": 0,
        "evidence_reconcile_purist": 0,
        "clinical_selection_purist": 0,
        "free_interval_purist": 0,
        "final_purist": 0,
        "final_pragmatic": 0,
        "rescue_dependence_from_model_final": 0,
        "rescue_dependence_from_representation": 0,
        "exact_evidence_rows": 0,
        "inexact_evidence_rows": 0,
        "inexact_final_correct": 0,
        "inexact_rescued_from_representation": 0,
        "masked_final_correct": 0,
        "breakthrough_marked": 0,
        "breakthrough_final_correct": 0,
        "unknown_gold": 0,
        "unknown_gold_final_correct": 0,
        "unknown_gold_false_rate_or_free": 0,
    }


def _published_holdout_aggregates() -> dict[str, Any]:
    fills = _load_json(FILLS_PATH)
    panel = _load_json(PANEL_PATH)
    hybrid = (fills.get("hybrid") or {}).get("gan_test450") or {}
    hybrid_out: dict[str, Any] = {}
    for slug, cell in hybrid.items():
        if not isinstance(cell, dict):
            continue
        hybrid_out[slug] = {
            "purist": int(cell["purist"]),
            "pragmatic": int(cell.get("pragmatic") or 0),
            "n": int(cell["n"]),
            "purist_rate": cell.get("purist_rate"),
            "row_policy": "aggregate_only",
            "source": "experiments/current_stack/latest/fills.json",
            "prompt_identity": "gan2026_hybrid_structured_events_v0.5",
        }
    llm_only: dict[str, Any] = {}
    for condition in panel.get("conditions") or []:
        slug = str(condition.get("slug") or "")
        gan = (condition.get("gan2026") or {}).get("test450") or {}
        if not gan:
            continue
        llm_only[slug] = {
            "purist_rate": gan.get("llm_purist_accuracy"),
            "n": gan.get("row_count"),
            "row_policy": gan.get("row_policy"),
            "source": "experiments/current_stack/latest/panel_aggregate.json",
        }
        if gan.get("row_count") and gan.get("llm_purist_accuracy") is not None:
            llm_only[slug]["purist"] = int(
                round(float(gan["llm_purist_accuracy"]) * int(gan["row_count"]))
            )
    return {
        "hybrid_test450": hybrid_out,
        "llm_only_test450": llm_only,
        "historical_v05_dev750_purist": JULY27_V05_DEV750_PURIST,
        "historical_v05_dev750_source": (
            "July 27 matched v0.5 panel, not current-stack remasured; "
            "cited from scripts/replay_gan2026_six_model_current_stack_dev750.py"
        ),
    }


def _cell_example(
    *,
    slug: str,
    index: int,
    gold: str,
    bucket: str,
    replay: dict[str, Any],
    evidence: str | None,
    exact: bool,
    rescue_class: str | None,
    masked: bool,
) -> dict[str, Any]:
    return {
        "model_slug": slug,
        "source_row_index": index,
        "gold_label": gold,
        "a_priori_bucket": bucket,
        "model_final": replay.get("model_final"),
        "resolved": replay.get("resolved"),
        "final": replay.get("final"),
        "first_stage": (replay.get("changes") or [{}])[0].get("stage")
        if replay.get("changes")
        else None,
        "rescue_class": rescue_class,
        "selected_evidence": _truncate(evidence),
        "exact_source_span": exact,
        "masked": masked,
        "pathway": ablation._pathway_key(list(replay.get("changes") or [])),
    }


def build_artifact() -> dict[str, Any]:
    gold_index = hs._gan_gold_index()
    published = _published_holdout_aggregates()
    models = _available_models()
    if not models:
        raise SystemExit("no matched v0.5 dev750 sources found")
    missing = [slug for slug, _, _ in ALL_MODELS if slug not in {item[0] for item in models}]

    per_model: dict[str, dict[str, Any]] = {}
    stage_by_model: dict[str, dict[str, dict[str, int]]] = {}
    class_by_model: dict[str, Counter[str]] = {}
    examples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    qwen_rescues_sol_already_ok = 0
    qwen_rescues_total = 0
    sol_representation_ok: dict[int, bool] = {}
    qwen_cells: dict[int, dict[str, Any]] = {}

    for slug, display, prompt in models:
        rows = _read_jsonl(_source_path(slug))
        acc = _empty_model_acc()
        stages = {stage: _empty_stage_stats() for stage in REPAIR_STAGE_ORDER}
        classes: Counter[str] = Counter()
        acc["n"] = len(rows)
        acc["display"] = display
        acc["prompt_identity"] = prompt
        acc["source_artifact"] = _source_path(slug).relative_to(REPO_ROOT).as_posix()

        for row in rows:
            index = int(row["source_row_index"])
            meta = gold_index[index]
            gold = str(meta["gold_label"])
            bucket = str(meta["a_priori_bucket"])
            gold_kind = str(meta["gold_label_kind"])
            _model_label, evidence, note = _selection_and_note(row)
            baseline = ablation.replay_row(row)
            if baseline is None or not baseline.get("replayable"):
                acc["unreplayable"] += 1
                continue
            acc["replayable"] += 1
            resolved = baseline.get("resolved")
            final = baseline.get("final")
            band = baseline["band_labels"]
            model_ok = _purist_ok(band.get("model_final"), gold)
            resolve_ok = _purist_ok(band.get("representation"), gold)
            evidence_ok = _purist_ok(band.get("evidence_reconcile"), gold)
            clinical_ok = _purist_ok(band.get("clinical_selection"), gold)
            final_ok = _purist_ok(band.get("free_interval"), gold)
            acc["model_final_purist"] += int(model_ok)
            acc["representation_purist"] += int(resolve_ok)
            acc["evidence_reconcile_purist"] += int(evidence_ok)
            acc["clinical_selection_purist"] += int(clinical_ok)
            acc["free_interval_purist"] += int(final_ok)
            acc["final_purist"] += int(final_ok)
            comparison = row.get("comparison") or {}
            if "pragmatic_correct" in comparison and final == (
                ((row.get("structured_record") or {}).get("selection") or {}).get(
                    "final_label"
                )
            ):
                acc["final_pragmatic"] += int(bool(comparison.get("pragmatic_correct")))
            exact = bool(evidence and note and evidence_is_substring(note, evidence))
            acc["exact_evidence_rows"] += int(exact)
            acc["inexact_evidence_rows"] += int(not exact)
            if not exact and final_ok:
                acc["inexact_final_correct"] += 1
            if not exact and final_ok and not resolve_ok:
                acc["inexact_rescued_from_representation"] += 1
            if final_ok and not model_ok:
                acc["rescue_dependence_from_model_final"] += 1
            if final_ok and not resolve_ok:
                acc["rescue_dependence_from_representation"] += 1

            resolved_kind = _label_kind(resolved)
            first_class = _first_changer_class(list(baseline.get("changes") or []), resolved)
            if first_class:
                classes[first_class] += 1
            breakthrough = _breakthrough_marked(evidence, note)
            acc["breakthrough_marked"] += int(breakthrough)
            if breakthrough and final_ok:
                acc["breakthrough_final_correct"] += 1
            if bucket == "unknown_sentinel":
                acc["unknown_gold"] += 1
                acc["unknown_gold_final_correct"] += int(final_ok)
                if (not final_ok) and resolved_kind in {
                    str(FrequencyLabelKind.FREQUENCY),
                    str(FrequencyLabelKind.SEIZURE_FREE),
                    str(FrequencyLabelKind.UNRESOLVED_MULTIPLE),
                }:
                    acc["unknown_gold_false_rate_or_free"] += 1
                elif (not final_ok) and _label_kind(final) in {
                    str(FrequencyLabelKind.FREQUENCY),
                    str(FrequencyLabelKind.SEIZURE_FREE),
                    str(FrequencyLabelKind.UNRESOLVED_MULTIPLE),
                }:
                    acc["unknown_gold_false_rate_or_free"] += 1

            masked = bool(
                final_ok
                and (
                    resolved_kind != gold_kind
                    or not exact
                    or (
                        bucket == "unknown_sentinel"
                        and first_class in {"family_rewrite", "clinical_reselect"}
                    )
                )
            )
            if masked:
                acc["masked_final_correct"] += 1

            changes = list(baseline.get("changes") or [])
            first_stage = changes[0]["stage"] if changes else None
            for hop in changes:
                stage = hop["stage"]
                stages[stage]["fires"] += 1
                before_ok = _purist_ok(hop.get("before"), gold)
                after_ok = _purist_ok(hop.get("after"), gold)
                if after_ok and not before_ok:
                    stages[stage]["any_rescue"] += 1
                if before_ok and not after_ok:
                    stages[stage]["any_harm"] += 1
            if first_stage:
                stages[first_stage]["first_changer"] += 1
                if final_ok and not resolve_ok:
                    stages[first_stage]["first_rescue"] += 1
                if resolve_ok and not final_ok:
                    stages[first_stage]["first_harm"] += 1

            if slug == "gpt56sol":
                sol_representation_ok[index] = resolve_ok
            if slug == FOCUS_SLUG:
                qwen_cells[index] = {
                    "final_ok": final_ok,
                    "resolve_ok": resolve_ok,
                    "model_ok": model_ok,
                    "masked": masked,
                    "first_class": first_class,
                    "first_stage": first_stage,
                    "exact": exact,
                    "breakthrough": breakthrough,
                    "bucket": bucket,
                }
                if final_ok and not resolve_ok:
                    qwen_rescues_total += 1

            key = None
            if slug == FOCUS_SLUG and final_ok and not resolve_ok:
                key = f"qwen_first_rescue:{first_class or 'unknown'}"
            elif slug == FOCUS_SLUG and masked:
                key = "qwen_masked"
            elif slug == FOCUS_SLUG and breakthrough and bucket == "unknown_sentinel":
                key = "qwen_breakthrough_unknown"
            if key and len(examples[key]) < EXAMPLES_PER_KEY:
                examples[key].append(
                    _cell_example(
                        slug=slug,
                        index=index,
                        gold=gold,
                        bucket=bucket,
                        replay=baseline,
                        evidence=evidence,
                        exact=exact,
                        rescue_class=first_class,
                        masked=masked,
                    )
                )

        per_model[slug] = acc
        stage_by_model[slug] = stages
        class_by_model[slug] = classes

    for index, cell in qwen_cells.items():
        if cell["final_ok"] and not cell["resolve_ok"] and sol_representation_ok.get(index):
            qwen_rescues_sol_already_ok += 1

    overfire: list[dict[str, Any]] = []
    for stage in REPAIR_STAGE_ORDER:
        peer_rates = []
        peer_slugs = [
            slug for slug, _, _ in models if slug != FOCUS_SLUG and slug in per_model
        ]
        for slug in peer_slugs:
            n = max(per_model[slug]["replayable"], 1)
            peer_rates.append(stage_by_model[slug][stage]["fires"] / n)
        if FOCUS_SLUG not in per_model:
            break
        qwen_n = max(per_model[FOCUS_SLUG]["replayable"], 1)
        qwen_fires = stage_by_model[FOCUS_SLUG][stage]["fires"]
        qwen_rate = qwen_fires / qwen_n
        median_peer = statistics.median(peer_rates) if peer_rates else 0.0
        ratio = (qwen_rate / median_peer) if median_peer > 0 else None
        flagged = bool(qwen_fires >= 10 and ratio is not None and ratio >= 1.5)
        overfire.append(
            {
                "stage": stage,
                "qwen_fires": qwen_fires,
                "qwen_rate": round(qwen_rate, 6),
                "peer_median_rate": round(median_peer, 6),
                "ratio_vs_peer_median": None if ratio is None else round(ratio, 4),
                "overfire_flag": flagged,
            }
        )

    arms: dict[str, Any] = {}
    for arm in ARMS:
        arm_models: dict[str, dict[str, int]] = {}
        for slug, _display, _prompt in models:
            rows = _read_jsonl(_source_path(slug))
            correct = 0
            replayable = 0
            vs_baseline_rescue = 0
            vs_baseline_harm = 0
            for row in rows:
                index = int(row["source_row_index"])
                gold = str(gold_index[index]["gold_label"])
                _model_label, evidence, note = _selection_and_note(row)
                seed = ablation.replay_row(row, omit_stages=frozenset())
                if seed is None or not seed.get("replayable"):
                    continue
                omit = _omit_for_arm(
                    arm,
                    resolved=seed.get("resolved"),
                    evidence=evidence,
                    note=note,
                )
                replay = (
                    seed
                    if arm == "baseline"
                    else ablation.replay_row(row, omit_stages=omit)
                )
                if replay is None or not replay.get("replayable"):
                    continue
                replayable += 1
                arm_ok = _purist_ok(replay.get("final"), gold)
                base_ok = _purist_ok(seed.get("final"), gold)
                correct += int(arm_ok)
                vs_baseline_rescue += int(arm_ok and not base_ok)
                vs_baseline_harm += int(base_ok and not arm_ok)
            arm_models[slug] = {
                "replayable": replayable,
                "purist": correct,
                "vs_baseline_rescue": vs_baseline_rescue,
                "vs_baseline_harm": vs_baseline_harm,
                "purist_delta_vs_baseline": correct
                - (per_model[slug]["final_purist"] if arm != "baseline" else correct),
            }
        arms[arm] = {"models": arm_models}

    def _rate(correct: int, n: int) -> float:
        return round(correct / n, 6) if n else 0.0

    cliffs: dict[str, Any] = {}
    hybrid_holdout = published["hybrid_test450"]
    for slug, _display, prompt in models:
        dev_n = per_model[slug]["replayable"]
        dev_correct = per_model[slug]["final_purist"]
        hold = hybrid_holdout.get(slug) or {}
        hold_n = int(hold.get("n") or 0)
        hold_correct = int(hold.get("purist") or 0)
        printed = {
            "dev750_prompt": prompt,
            "dev750_purist": dev_correct,
            "dev750_n": dev_n,
            "dev750_rate": _rate(dev_correct, dev_n),
            "test450_prompt": hold.get("prompt_identity"),
            "test450_purist": hold_correct,
            "test450_n": hold_n,
            "test450_rate": _rate(hold_correct, hold_n),
            "printed_drop": round(_rate(dev_correct, dev_n) - _rate(hold_correct, hold_n), 6),
        }
        historical = JULY27_V05_DEV750_PURIST.get(slug)
        same_prompt_v05 = None
        if historical is not None and hold_n:
            same_prompt_v05 = {
                "dev750_source": "july27_v05_panel_not_current_stack",
                "dev750_purist": historical,
                "dev750_n": 750,
                "dev750_rate": _rate(historical, 750),
                "test450_purist": hold_correct,
                "test450_n": hold_n,
                "test450_rate": _rate(hold_correct, hold_n),
                "drop": round(_rate(historical, 750) - _rate(hold_correct, hold_n), 6),
            }
        llm_hold = (published["llm_only_test450"].get(slug) or {})
        llm_dev_rate = None
        # Living panel still carries a 3 Aug hybrid snapshot; LLM-only rates are
        # the published comparator, not this study's hybrid replay.
        for condition in _load_json(PANEL_PATH).get("conditions") or []:
            if condition.get("slug") == slug:
                llm_dev_rate = ((condition.get("gan2026") or {}).get("dev750") or {}).get(
                    "llm_purist_accuracy"
                )
                break
        cliffs[slug] = {
            "printed_mixed_prompt": printed,
            "same_prompt_historical_v05": same_prompt_v05,
            "llm_only_dev750_rate": llm_dev_rate,
            "llm_only_test450": llm_hold,
        }

    payload = {
        "schema_version": "gan2026.qwen_rescue_overfiring.v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "protocol": PROTOCOL.relative_to(REPO_ROOT).as_posix(),
        "git": _git_note(),
        "dataset": "Gan 2026",
        "split": "dev750",
        "split_machine": "validation",
        "method": "llm_with_rules",
        "call_mode": "saved_raw_output_no_call",
        "holdout_policy": "aggregate_only_published_fills",
        "claim_boundary": (
            "Development no-call mechanism audit. Holdout figures are copied "
            "from published aggregates. Not a paper performance claim. "
            "Production rules unchanged."
        ),
        "models": {
            slug: {
                "display": display,
                "prompt_identity": prompt,
                **{
                    key: value
                    for key, value in per_model[slug].items()
                    if key not in {"display", "prompt_identity"}
                },
                "rates": {
                    "model_final": _rate(
                        per_model[slug]["model_final_purist"],
                        per_model[slug]["replayable"],
                    ),
                    "representation": _rate(
                        per_model[slug]["representation_purist"],
                        per_model[slug]["replayable"],
                    ),
                    "evidence_reconcile": _rate(
                        per_model[slug]["evidence_reconcile_purist"],
                        per_model[slug]["replayable"],
                    ),
                    "final": _rate(
                        per_model[slug]["final_purist"], per_model[slug]["replayable"]
                    ),
                    "rescue_dependence_from_representation": _rate(
                        per_model[slug]["rescue_dependence_from_representation"],
                        per_model[slug]["final_purist"],
                    ),
                    "masked_among_final_correct": _rate(
                        per_model[slug]["masked_final_correct"],
                        per_model[slug]["final_purist"],
                    ),
                    "inexact_evidence": _rate(
                        per_model[slug]["inexact_evidence_rows"],
                        per_model[slug]["replayable"],
                    ),
                    "inexact_and_final_correct": _rate(
                        per_model[slug]["inexact_final_correct"],
                        per_model[slug]["replayable"],
                    ),
                },
                "first_changer_classes": dict(class_by_model[slug]),
                "stages": stage_by_model[slug],
            }
            for slug, display, prompt in models
        },
        "missing_v05_sources": missing,
        "prompt_identity": V05_PROMPT,
        "overfire_vs_v05_peer_median": overfire,
        "qwen_peer_competence": {
            "qwen_representation_rescues": qwen_rescues_total,
            "qwen_rescues_where_sol_already_correct_at_representation": (
                qwen_rescues_sol_already_ok
            ),
        },
        "counterfactual_arms": arms,
        "published_holdout_aggregates": published,
        "generalization_cliffs": cliffs,
        "examples": {key: value for key, value in examples.items()},
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    if not PROTOCOL.exists():
        raise SystemExit(f"predeclared protocol missing: {PROTOCOL}")
    payload = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    qwen = payload["models"].get(FOCUS_SLUG)
    print(
        json.dumps(
            {
                "status": "pass",
                "output": args.output.relative_to(REPO_ROOT).as_posix(),
                "prompt_identity": payload.get("prompt_identity"),
                "models": sorted(payload["models"]),
                "missing_v05_sources": payload.get("missing_v05_sources"),
                "qwen_replayable": None if qwen is None else qwen["replayable"],
                "qwen_final": None if qwen is None else qwen["final_purist"],
                "overfire_flags": [
                    row["stage"]
                    for row in payload.get("overfire_vs_v05_peer_median") or []
                    if row["overfire_flag"]
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
