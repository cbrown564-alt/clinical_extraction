"""SF closed-option magnitude complement (2026-07-08 pathway #1).

CANDIDATE WORK: the highest-leverage production pathway from the 07-08 queue.
The deconflation probe (``sf_direction_vocab_deconflation_2026-07-08``)
measured that the closed-option selector drops 13 magnitude facts the
deterministic rules catch (magnitude recall 0.845 vs 0.957), but its magnitude
*precision* is higher (0.9515 vs 0.9328). This driver tests the complement
design that asymmetry implies: fire a magnitude-only selector **only** on
letters where the deterministic magnitude regexes (``change.frequent`` /
``change.infrequent``) had no match, letting the rules own magnitude
everywhere they already fire and the LLM complement them where they are
silent.

REPLAY MODE (the only mode here; cleanest attribution). Load the saved v08
hybrid SF artifact (carries ``FrequencyChange`` in ``predicted_mentions`` from
``rules/change.py``), identify the direction-in-play subset, restrict to the
letters where ``has_magnitude_regex_match`` is False (the complement subset),
fire the magnitude selector once per such letter, OVERWRITE
``FrequencyChange`` on those letters' SF mentions with the selector's
magnitude pick, carry all 140 letters through, re-score via
``score_frequency_state``. The only thing that changes is the
``FrequencyChange`` provenance on the complement subset. The v08 artifact and
the production ``run_split`` path are untouched.

The headline metric is ``state_profile_magnitude`` (the magnitude-only
companion the deconflation probe added), compared against the rules' 0.9447.
The conflated ``state_profile_directional`` (0.8897) is the anchor; the
direction- and magnitude-blind ``state_profile`` (0.9338) is the byte-identical
regression guard.

Predeclaration:
  docs/experiments/exectv2/seizure_frequency/
  exectv2_sf_magnitude_complement_predeclaration_2026-07-08.md
Prior art: ``run_exectv2_sf_direction_vocab_deconflation.py`` (the decomposition
that motivated this probe) and ``run_exectv2_sf_closed_option_hybrid_integration.py``
(the replay-mode template this driver mirrors).

Usage:
  python scripts/run_exectv2_sf_magnitude_complement.py --cache
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid.closed_option_direction import (
    ClosedOptionMagnitudeSelector,
    assemble_direction,
    build_magnitude_menu,
    has_magnitude_regex_match,
    parse_selection,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    frequency_state_faithful,
    score_frequency_state,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

# Fixed literal date to avoid the integration probe's date-wrinkle (its RUN_DATE
# resolved to 20260707 while its results doc was named 2026-07-06).
DATESTR = "20260708"
ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
# The saved v08 hybrid SF output -- carries FrequencyChange in predicted_mentions,
# sourced from deterministic rules/change.py. The same rules-arm artifact the
# deconflation probe reads; this is the 0.8897 / 0.9447-reference surface.
HYBRID_SF_ARTIFACT = EXPERIMENTS / "exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl"

TASK_MODEL = "openai/gpt-4.1-mini"
TASK_TEMPERATURE = 0.0
TASK_MAX_TOKENS = 8000

SF_ENTITY = "SeizureFrequency"

# Predeclared reference numbers (all dev140, reproduced in-run).
EXPECTED_BASELINE_DIRECTIONAL_F1 = 0.8897  # rules state_profile_directional
EXPECTED_BASELINE_MAGNITUDE_F1 = 0.9447  # rules state_profile_magnitude
EXPECTED_BASELINE_STATE_PROFILE_F1 = 0.9338  # byte-identical regression guard
ANCHOR_TOLERANCE = 0.0001
# Verdict band thresholds (predeclared).
BAND_TOLERANCE = 0.005
REGRESSION_TOLERANCE = 0.005


# --------------------------------------------------------------------------------------
# Disagreement-set loader (reused definition from the integration probe).
# --------------------------------------------------------------------------------------
def _letters_with_direction_in_play(jsonl_path: Path) -> dict[str, list[dict[str, Any]]]:
    """Return {letter_id: [sf mention dicts]} for letters whose v08 hybrid output
    carries a FrequencyChange-bearing or changed-state SF mention.

    Same definition as ``run_exectv2_sf_closed_option_hybrid_integration``: the set
    of letters where the direction/magnitude source matters. A mention qualifies if
    its attributes carry a ``FrequencyChange`` key OR resolve to a ``changed`` state
    under ``frequency_state_faithful``.
    """

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
                changed.append({"index": idx, "text": m.get("text", "seizures"), "_attrs": attrs})
        if changed:
            out[lid] = changed
    return out


def _pred_letters_from_hybrid(
    jsonl_path: Path, gold_by_id: dict[str, ExectLetter], *, override: dict[str, str] | None = None
) -> list[ExectLetter]:
    """Build predicted ExectLetters from the v08 hybrid artifact.

    ``override`` -- optional {letter_id: FrequencyChange_label}; when set, the
    selector's magnitude pick replaces the deterministic value on that letter's SF
    mentions. Same apply-then-rescore pattern as the integration probe.
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
            ExectLetter(letter_id=lid, note_text=gold.note_text, annotations=tuple(anns_list))
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


def _prf1_block(prefix: str, score: Any) -> dict[str, Any]:
    return {
        f"{prefix}_f1": round(score.f1, 4),
        f"{prefix}_precision": round(score.precision, 4),
        f"{prefix}_recall": round(score.recall, 4),
        f"{prefix}_tp": score.tp,
        f"{prefix}_fp": score.fp,
        f"{prefix}_fn": score.fn,
    }


# --------------------------------------------------------------------------------------
# Replay mode (the complement probe).
# --------------------------------------------------------------------------------------
def run_replay(num_threads: int, cache: bool) -> None:
    dev_gold = load_letters_for_split("dev")
    gold_by_id = {le.letter_id: le for le in dev_gold}

    # Baseline: score the v08 hybrid artifact UNCHANGED -> must reproduce 0.8897 /
    # 0.9447 / 0.9338.
    baseline_pred = _pred_letters_from_hybrid(HYBRID_SF_ARTIFACT, gold_by_id)
    baseline_scores = score_frequency_state(dev_gold, baseline_pred)
    b_d = baseline_scores.state_profile_directional
    b_m = baseline_scores.state_profile_magnitude
    b_s = baseline_scores.state_profile
    print("[complement] v08 hybrid SF baseline (unchanged):")
    print(f"  state_profile_directional F1: {b_d.f1:.4f} (tp={b_d.tp} fp={b_d.fp} fn={b_d.fn})")
    print(f"  state_profile_magnitude F1:    {b_m.f1:.4f} (tp={b_m.tp} fp={b_m.fp} fn={b_m.fn})")
    print(f"  state_profile F1:              {b_s.f1:.4f}")

    # Anchor reproduction (contract check).
    directional_drift = abs(b_d.f1 - EXPECTED_BASELINE_DIRECTIONAL_F1)
    magnitude_drift = abs(b_m.f1 - EXPECTED_BASELINE_MAGNITUDE_F1)
    state_drift = abs(b_s.f1 - EXPECTED_BASELINE_STATE_PROFILE_F1)
    anchors_ok = (
        directional_drift <= ANCHOR_TOLERANCE
        and magnitude_drift <= ANCHOR_TOLERANCE
        and state_drift <= ANCHOR_TOLERANCE
    )
    print(
        "[complement] anchor reproduction: "
        f"directional drift {directional_drift:.4f}, "
        f"magnitude drift {magnitude_drift:.4f}, "
        f"state_profile drift {state_drift:.4f} -> "
        f"{'OK' if anchors_ok else 'CONTRACT FAILURE'}"
    )
    if not anchors_ok:
        print("[complement] ABORT: baseline anchors did not reproduce; do not report complement.")
        return

    # Direction-in-play set, then restrict to the complement subset (no magnitude
    # regex match). This is the set the magnitude selector fires on.
    in_play = _letters_with_direction_in_play(HYBRID_SF_ARTIFACT)
    total_in_play = len(in_play)
    complement_lids = [
        lid for lid in in_play if not has_magnitude_regex_match(gold_by_id[lid].note_text)
    ]
    covered_lids = [lid for lid in in_play if has_magnitude_regex_match(gold_by_id[lid].note_text)]
    print(
        f"[complement] {total_in_play} direction-in-play letters; "
        f"{len(covered_lids)} covered by a magnitude regex (rules own), "
        f"{len(complement_lids)} NOT covered (complement fires here)."
    )

    selector = ClosedOptionMagnitudeSelector()
    lm = build_dspy_lm(
        TASK_MODEL, temperature=TASK_TEMPERATURE, max_tokens=TASK_MAX_TOKENS, cache=cache
    )
    dspy.configure(lm=lm)
    evaluator = dspy.Parallel(num_threads=num_threads, provide_traceback=True)

    pairs = []
    menus_by_lid: dict[str, list[dict[str, str]]] = {}
    for lid in complement_lids:
        letter = gold_by_id[lid]
        menu = build_magnitude_menu(letter.note_text)
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
        f"[complement] firing {len(pairs)} magnitude-selector calls "
        f"({TASK_MODEL}, temp {TASK_TEMPERATURE})...",
        flush=True,
    )
    started = time.time()
    predictions = evaluator(pairs)

    # Apply selected magnitudes; build the override map + ledger.
    magnitude_counts: dict[str, int] = {}
    mode_counts: dict[str, int] = {}
    ledger_rows: list[dict[str, Any]] = []
    override: dict[str, str] = {}
    for lid, prediction in zip(complement_lids, predictions, strict=True):
        raw_sel = str(getattr(prediction, "selection_json", "") or "") if prediction else ""
        cid, mode = parse_selection(raw_sel)
        menu = menus_by_lid[lid]
        new_mag, _prov = assemble_direction(cid, menu)
        override[lid] = new_mag
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
        if new_mag != "Same":
            magnitude_counts[new_mag] = magnitude_counts.get(new_mag, 0) + 1
        row = _raw_row_by_id(lid)
        mentions = in_play[lid]
        for c in mentions:
            idx = c["index"]
            old_val = row["predicted_mentions"][idx]["attributes"].get("FrequencyChange", "(none)")
            ledger_rows.append(
                {
                    "letter_id": lid,
                    "mention_index": idx,
                    "applies_to": c["text"],
                    "selected_candidate_id": cid,
                    "selection_mode": mode,
                    "assembled_magnitude": new_mag,
                    "prior_frequency_change": old_val,
                    "menu_labels": [e["label"] for e in menu],
                }
            )
    elapsed = time.time() - started
    print(
        f"[complement] done in {elapsed:.1f}s; "
        f"selected magnitudes (non-Same): {magnitude_counts}; "
        f"modes: {mode_counts}"
    )

    # Score the overriden artifact.
    adj_pred = _pred_letters_from_hybrid(HYBRID_SF_ARTIFACT, gold_by_id, override=override)
    adj_scores = score_frequency_state(dev_gold, adj_pred)
    a_d = adj_scores.state_profile_directional
    a_m = adj_scores.state_profile_magnitude
    a_s = adj_scores.state_profile
    print("[complement] HYBRID + LLM MAGNITUDE COMPLEMENT:")
    print(f"  state_profile_magnitude F1:    {a_m.f1:.4f} (tp={a_m.tp} fp={a_m.fp} fn={a_m.fn})")
    print(f"  state_profile_directional F1: {a_d.f1:.4f}")
    print(f"  state_profile F1:             {a_s.f1:.4f} (regression check)")

    mag_delta = a_m.f1 - b_m.f1
    print(f"\n[complement] state_profile_magnitude delta = {mag_delta:+.4f} vs rules {b_m.f1:.4f}")

    # Byte-identical regression check on state_profile (the blind metric).
    state_byte_identical = (
        a_s.f1 == b_s.f1 and a_s.tp == b_s.tp and a_s.fp == b_s.fp and a_s.fn == b_s.fn
    )

    # Predeclared outcome verdict (on state_profile_magnitude vs rules 0.9447).
    print("\n[complement] PREDECLARED OUTCOME VERDICT:")
    if not state_byte_identical and abs(a_s.f1 - b_s.f1) > REGRESSION_TOLERANCE:
        verdict = "CONTRACT FAILURE (state_profile regressed)"
    elif a_s.f1 < b_s.f1 - REGRESSION_TOLERANCE:
        verdict = "CONTRACT FAILURE (state_profile regressed)"
    elif a_m.f1 > EXPECTED_BASELINE_MAGNITUDE_F1 + BAND_TOLERANCE:
        verdict = "COMPLEMENT BEATS RULES (magnitude F1 > 0.9447 + 0.005)"
    elif a_m.f1 >= EXPECTED_BASELINE_MAGNITUDE_F1 - BAND_TOLERANCE:
        verdict = "COMPLEMENT APPROACHES RULES (magnitude F1 within +/-0.005 of 0.9447)"
    else:
        verdict = "COMPLEMENT TRAILS RULES (magnitude F1 < 0.9447 - 0.005)"
    print(f"  {verdict}")

    # Persist artifacts.
    summary = {
        "date": "2026-07-08",
        "split": "dev140",
        "mode": "replay",
        "model": TASK_MODEL,
        "temperature": TASK_TEMPERATURE,
        "input_artifact": HYBRID_SF_ARTIFACT.name,
        "n_direction_in_play_letters": total_in_play,
        "n_magnitude_covered_letters": len(covered_lids),
        "n_complement_letters": len(complement_lids),
        "n_selector_calls": len(pairs),
        "baseline": {
            **_prf1_block("state_profile_directional", b_d),
            **_prf1_block("state_profile_magnitude", b_m),
            **_prf1_block("state_profile", b_s),
        },
        "complement": {
            **_prf1_block("state_profile_directional", a_d),
            **_prf1_block("state_profile_magnitude", a_m),
            **_prf1_block("state_profile", a_s),
        },
        "anchor_check": {
            "expected_directional_f1": EXPECTED_BASELINE_DIRECTIONAL_F1,
            "expected_magnitude_f1": EXPECTED_BASELINE_MAGNITUDE_F1,
            "expected_state_profile_f1": EXPECTED_BASELINE_STATE_PROFILE_F1,
            "directional_drift": directional_drift,
            "magnitude_drift": magnitude_drift,
            "state_profile_drift": state_drift,
            "anchors_reproduced": anchors_ok,
        },
        "magnitude_delta_vs_rules": round(mag_delta, 4),
        "state_profile_byte_identical": state_byte_identical,
        "magnitude_counts_non_same": magnitude_counts,
        "selection_mode_counts": mode_counts,
        "verdict": verdict,
    }
    summary_path = EXPERIMENTS / f"exectv2_sf_magnitude_complement_summary_{DATESTR}.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )
    ledger_path = EXPERIMENTS / f"exectv2_sf_magnitude_complement_ledger_{DATESTR}.jsonl"
    ledger_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in ledger_rows) + "\n",
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
    adj_jsonl = EXPERIMENTS / f"exectv2_sf_magnitude_complement_dev140_{DATESTR}.jsonl"
    write_jsonl(override_rows, adj_jsonl)
    print(f"[complement] summary -> {summary_path.relative_to(ROOT)}")
    print(f"[complement] ledger  -> {ledger_path.relative_to(ROOT)}")
    print(f"[complement] preds   -> {adj_jsonl.relative_to(ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", action="store_true", help="Enable dspy response cache.")
    ap.add_argument("--num-threads", type=int, default=4)
    args = ap.parse_args()
    run_replay(num_threads=args.num_threads, cache=args.cache)


if __name__ == "__main__":
    main()
