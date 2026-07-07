"""SF closed-option direction selector -- hybrid-lane integration (item 2 follow-up).

CANDIDATE WORK: substrate-integration follow-up to the standalone closed-option
direction probe (item 2), which REFUTED "fundamental" at +0.0552 on the raw
SF-verify artifact. This driver wires the SAME closed-option selector as a
candidate direction source on the **hybrid SF lane** (the v08 production
surface), re-scoring ``state_profile_directional`` against the **0.8897** hybrid
reference (direction sourced from deterministic ``rules/change.py``).

REPLAY MODE (the headline, cleanest attribution). Load the saved v08 hybrid SF
artifact (which carries ``FrequencyChange`` in ``predicted_mentions`` from
``rules/change.py``), fire the closed-option selector once per qualifying letter
(same disagreement definition as the standalone probe: letters with a kept SF
fact carrying a ``FrequencyChange`` suggestion or a ``changed`` state),
OVERWRITE ``FrequencyChange`` on those letters' SF mentions with the selector's
pick, carry all 140 letters through, re-score via ``score_frequency_state``. The
only thing that changes is the direction-attribute provenance.

LIVE MODE (cross-check, noisier). Call
``run_split(direction_selector="llm_closed_option")`` end-to-end. More calls
(~140); conflates assessment variance with direction-source variance. Implemented
via the opt-in parameter wired into ``hybrid.clinical_assessment.run_split``.

Predeclaration:
  docs/experiments/exectv2/seizure_frequency/
  exectv2_sf_closed_option_hybrid_integration_predeclaration_2026-07-06.md
Prior art: ``run_exectv2_sf_closed_option_direction_probe.py`` (standalone, +0.0552).

Usage:
  python scripts/run_exectv2_sf_closed_option_hybrid_integration.py --cache --mode replay
  python scripts/run_exectv2_sf_closed_option_hybrid_integration.py --cache --mode live
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import date
from pathlib import Path
from typing import Any

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid.clinical_assessment import (
    run_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid.closed_option_direction import (
    ClosedOptionDirectionSelector,
    assemble_direction,
    build_direction_menu,
    parse_selection,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    score_frequency_state,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

RUN_DATE = date.today().isoformat().replace("-", "")
ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REPORT_DIR = ROOT / "docs" / "experiments" / "exectv2" / "seizure_frequency"
# The saved v08 hybrid SF output -- carries FrequencyChange in predicted_mentions,
# sourced from deterministic rules/change.py. This is the 0.8897-reference surface.
HYBRID_SF_ARTIFACT = (
    EXPERIMENTS / "exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl"
)

TASK_MODEL = "openai/gpt-4.1-mini"
TASK_TEMPERATURE = 0.0
TASK_MAX_TOKENS = 8000

SF_ENTITY = "SeizureFrequency"


# --------------------------------------------------------------------------------------
# Disagreement-set loader (the qualifying-letter definition, shared with the
# standalone probe + the run_split wiring).
# --------------------------------------------------------------------------------------
def _letters_with_direction_in_play(jsonl_path: Path) -> dict[str, list[dict[str, Any]]]:
    """Return {letter_id: [sf mention dicts]} for letters whose v08 hybrid output
    carries a FrequencyChange-bearing or changed-state SF mention.

    This is the integration-surface analogue of the standalone probe's
    ``_letters_with_changed_mentions``: the set of letters where the direction
    source matters. A mention qualifies if its attributes carry a
    ``FrequencyChange`` key (the v08 hybrid sourced it from rules/change.py) OR
    its attributes resolve to a ``changed`` state under
    ``frequency_state_faithful``.
    """

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
        frequency_state_faithful,
    )

    out: dict[str, list[dict[str, Any]]] = {}
    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        lid = row["letter_id"]
        changed: list[dict[str, Any]] = []
        for idx, m in enumerate(row.get("predicted_mentions", [])):
            if m.get("entity") != SF_ENTITY:
                continue
            attrs = m.get("attributes") or {}
            if "FrequencyChange" in attrs or frequency_state_faithful(attrs) == "changed":
                changed.append(
                    {"index": idx, "text": m.get("text", "seizures"), "_attrs": attrs}
                )
        if changed:
            out[lid] = changed
    return out


def _pred_letters_from_hybrid(
    jsonl_path: Path, gold_by_id: dict[str, ExectLetter], *, override: dict[str, str] | None = None
) -> list[ExectLetter]:
    """Build predicted ExectLetters from the v08 hybrid artifact.

    ``override`` -- optional {letter_id: FrequencyChange_label}; when set, the
    selector's pick replaces the deterministic direction on that letter's SF
    mentions. This is the apply-then-rescore step.
    """

    out: list[ExectLetter] = []
    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        lid = row["letter_id"]
        gold = gold_by_id.get(lid)
        if gold is None:
            continue
        sf = [m for m in row.get("predicted_mentions", []) if m.get("entity") == SF_ENTITY]
        anns_list = []
        for m in sf:
            attrs = {str(k): str(v) for k, v in dict(m.get("attributes", {})).items()}
            if override is not None and lid in override:
                attrs["FrequencyChange"] = override[lid]
            anns_list.append(
                ExectAnnotation(
                    entity=SF_ENTITY,
                    text=str(m.get("text", "")),
                    attributes=attrs,
                )
            )
        out.append(
            ExectLetter(
                letter_id=lid, note_text=gold.note_text, annotations=tuple(anns_list)
            )
        )
    return out


def _raw_row_by_id(lid: str) -> dict[str, Any]:
    return json.loads(
        next(
            line
            for line in HYBRID_SF_ARTIFACT.read_text(encoding="utf-8").splitlines()
            if line.strip() and json.loads(line)["letter_id"] == lid
        )
    )


# --------------------------------------------------------------------------------------
# Replay mode (the headline).
# --------------------------------------------------------------------------------------
def run_replay(num_threads: int, cache: bool) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    dev_gold = load_letters_for_split("dev")
    gold_by_id = {le.letter_id: le for le in dev_gold}

    # Baseline: score the v08 hybrid artifact UNCHANGED -> must reproduce 0.8897.
    baseline_pred = _pred_letters_from_hybrid(HYBRID_SF_ARTIFACT, gold_by_id)
    baseline_scores = score_frequency_state(dev_gold, baseline_pred)
    b_d = baseline_scores.state_profile_directional
    print("[integration] v08 hybrid SF baseline (unchanged):")
    print(
        f"  state_profile_directional F1: {b_d.f1:.4f} (tp={b_d.tp} fp={b_d.fp} fn={b_d.fn})"
    )
    print(f"  state_profile F1:             {baseline_scores.state_profile.f1:.4f}")

    in_play = _letters_with_direction_in_play(HYBRID_SF_ARTIFACT)
    total_mentions = sum(len(v) for v in in_play.values())
    print(
        f"[integration] {total_mentions} direction-in-play SF mentions across "
        f"{len(in_play)} letters; building menus + selecting..."
    )

    selector = ClosedOptionDirectionSelector()
    lm = build_dspy_lm(
        TASK_MODEL, temperature=TASK_TEMPERATURE, max_tokens=TASK_MAX_TOKENS, cache=cache
    )
    dspy.configure(lm=lm)
    evaluator = dspy.Parallel(num_threads=num_threads, provide_traceback=True)

    pairs = []
    menus_by_lid: dict[str, list[dict[str, str]]] = {}
    for lid in in_play:
        letter = gold_by_id[lid]
        menu = build_direction_menu(letter.note_text)
        menus_by_lid[lid] = menu
        pairs.append(
            (
                selector,
                {
                    "letter_text": letter.note_text,
                    "candidate_menu": json.dumps(menu, ensure_ascii=False),
                },
            )
        )
    print(
        f"[integration] firing {len(pairs)} selector calls "
        f"({TASK_MODEL}, temp {TASK_TEMPERATURE})...",
        flush=True,
    )
    started = time.time()
    predictions = evaluator(pairs)

    # Apply selected directions; build the override map + ledger.
    direction_counts: dict[str, int] = {}
    mode_counts: dict[str, int] = {}
    ledger_rows: list[dict[str, Any]] = []
    override: dict[str, str] = {}
    lids = list(in_play.keys())
    for lid, prediction in zip(lids, predictions, strict=True):
        raw_sel = str(getattr(prediction, "selection_json", "") or "") if prediction else ""
        cid, mode = parse_selection(raw_sel)
        menu = menus_by_lid[lid]
        new_dir, _prov = assemble_direction(cid, menu)
        override[lid] = new_dir
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
        if new_dir != "Same":
            direction_counts[new_dir] = direction_counts.get(new_dir, 0) + 1
        row = _raw_row_by_id(lid)
        mentions = in_play[lid]
        for c in mentions:
            idx = c["index"]
            old_dir = row["predicted_mentions"][idx]["attributes"].get(
                "FrequencyChange", "(none)"
            )
            ledger_rows.append(
                {
                    "letter_id": lid,
                    "mention_index": idx,
                    "applies_to": c["text"],
                    "selected_candidate_id": cid,
                    "selection_mode": mode,
                    "assembled_direction": new_dir,
                    "prior_direction": old_dir,
                    "menu_labels": [e["label"] for e in menu],
                }
            )
    elapsed = time.time() - started
    print(
        f"[integration] done in {elapsed:.1f}s; "
        f"selected directions (non-Same): {direction_counts}; "
        f"modes: {mode_counts}"
    )

    # Score the overriden artifact.
    adj_pred = _pred_letters_from_hybrid(HYBRID_SF_ARTIFACT, gold_by_id, override=override)
    adj_scores = score_frequency_state(dev_gold, adj_pred)
    a_d = adj_scores.state_profile_directional
    print("[integration] HYBRID + LLM CLOSED-OPTION DIRECTION:")
    print(
        f"  state_profile_directional F1: {a_d.f1:.4f} (tp={a_d.tp} fp={a_d.fp} fn={a_d.fn})"
    )
    print(f"  state_profile F1:             {adj_scores.state_profile.f1:.4f} (regression check)")

    delta = a_d.f1 - baseline_scores.state_profile_directional.f1
    print(f"\n[integration] state_profile_directional delta = {delta:+.4f} vs hybrid 0.8897")

    # Predeclared outcome verdict.
    print("\n[integration] PREDECLARED OUTCOME VERDICT:")
    if adj_scores.state_profile.f1 < baseline_scores.state_profile.f1 - 0.005:
        verdict = "CONTRACT FAILURE (state_profile regressed)"
    elif a_d.f1 >= 0.8897 - 0.005:
        verdict = "MATCHES the deterministic rules (>= 0.8897)"
    elif a_d.f1 < 0.7103:
        verdict = "REGRESSES below the standalone probe (< 0.7103)"
    else:
        verdict = "APPROACHES but does not match (0.7103 <= x < 0.8897)"
    print(f"  {verdict}")

    # Persist artifacts.
    summary = {
        "run_date": RUN_DATE,
        "mode": "replay",
        "model": TASK_MODEL,
        "temperature": TASK_TEMPERATURE,
        "split": "dev140",
        "input_artifact": HYBRID_SF_ARTIFACT.name,
        "n_selector_calls": len(pairs),
        "baseline_state_profile_directional_f1": baseline_scores.state_profile_directional.f1,
        "closed_option_hybrid_state_profile_directional_f1": a_d.f1,
        "delta_vs_hybrid": delta,
        "baseline_state_profile_f1": baseline_scores.state_profile.f1,
        "closed_option_hybrid_state_profile_f1": adj_scores.state_profile.f1,
        "direction_counts_non_same": direction_counts,
        "selection_mode_counts": mode_counts,
        "verdict": verdict,
    }
    summary_path = (
        EXPERIMENTS / f"exectv2_sf_closed_option_hybrid_integration_summary_{RUN_DATE}.json"
    )
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    ledger_path = (
        EXPERIMENTS / f"exectv2_sf_closed_option_hybrid_integration_ledger_{RUN_DATE}.jsonl"
    )
    ledger_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in ledger_rows) + "\n",
        encoding="utf-8",
    )
    # Persist the overriden predictions for reproducibility.
    override_rows = []
    for line in HYBRID_SF_ARTIFACT.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        lid = row["letter_id"]
        if lid in override:
            for m in row.get("predicted_mentions", []):
                if m.get("entity") == SF_ENTITY:
                    (m.setdefault("attributes", {}))["FrequencyChange"] = override[lid]
        override_rows.append(row)
    adj_jsonl = (
        EXPERIMENTS
        / f"exectv2_sf_closed_option_hybrid_integration_dev140_{RUN_DATE}.jsonl"
    )
    write_jsonl(override_rows, adj_jsonl)
    print(f"[integration] summary -> {summary_path.relative_to(ROOT)}")
    print(f"[integration] ledger  -> {ledger_path.relative_to(ROOT)}")
    print(f"[integration] preds   -> {adj_jsonl.relative_to(ROOT)}")


# --------------------------------------------------------------------------------------
# Live mode (cross-check).
# --------------------------------------------------------------------------------------
def run_live(cache: bool, checkpoint: Path | None) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    dev_gold = load_letters_for_split("dev")
    print(
        f"[integration-live] running run_split(direction_selector='llm_closed_option') "
        f"end-to-end on {len(dev_gold)} dev140 letters..."
    )
    rows, metadata = run_split(
        dev_gold,
        split="dev",
        model=TASK_MODEL,
        temperature=TASK_TEMPERATURE,
        max_tokens=TASK_MAX_TOKENS,
        mode="live",
        dspy_cache=cache,
        direction_selector="llm_closed_option",
        checkpoint_jsonl_path=checkpoint,
        progress_every=20,
    )
    out_jsonl = (
        EXPERIMENTS / f"exectv2_sf_closed_option_hybrid_integration_live_{RUN_DATE}.jsonl"
    )
    write_jsonl(rows, out_jsonl)
    n_sel = sum(1 for r in rows if r.get("direction_selection"))
    print(f"[integration-live] {n_sel}/{len(rows)} letters fired the selector")
    print(f"[integration-live] wrote {out_jsonl.relative_to(ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", action="store_true", help="Enable dspy response cache.")
    ap.add_argument(
        "--mode", choices=["replay", "live"], default="replay", help="replay (default) or live"
    )
    ap.add_argument("--num-threads", type=int, default=4)
    ap.add_argument(
        "--live-checkpoint",
        type=Path,
        default=None,
        help="live-mode resume checkpoint path",
    )
    args = ap.parse_args()
    if args.mode == "replay":
        run_replay(num_threads=args.num_threads, cache=args.cache)
    else:
        run_live(cache=args.cache, checkpoint=args.live_checkpoint)


if __name__ == "__main__":
    main()
