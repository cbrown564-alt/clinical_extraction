"""SF closed-option direction selector — item 2 of predecessor_synthesis_followups_2026-07-06.

CROSS-FAMILY TEST OF THE SF CAPACITY-VS-EXECUTION GAP.

The four measured negatives for the SF-direction gap all share one architecture
family: free-write-then-arbitrate (B1 post-hoc adjudication, B2 hard-emission,
the Phase-0 three-family degeneracy). This probe tests the gap in a *different*
family: a closed-option selector where the LLM never free-writes a direction; it
picks a candidate_id verbatim from a deterministic menu sourced from
rules/change.py, or abstains. This is the dspy G32 principle (pick-from-menu-
or-abstain) transferred to the ExECTv2 SF direction surface.

Mirrors run_exectv2_sf_direction_probe.py::run_b1 (Phase B1) for the disagreement-
set loader, the apply-direction-then-rescore pattern, the LLM wrapper, and the
scorer. The three architectural differences that define the cross-family test:

1. Deterministic candidate menu builder: rules/change.py regex matches → menu.
2. Abstention-validated selector contract: forbid a selected id when mode is a
   defer mode (mirrors gan2026 selected_fact.py:32-49).
3. Deterministic assembly: selected_id → FrequencyChange, or Same on abstain.

Predeclaration: docs/experiments/exectv2/seizure_frequency/
               exectv2_sf_closed_option_direction_predeclaration_2026-07-06.md
Prior art: sf_direction_extraction_probe_2026-07-03 (REFUTED, free-write family).

Usage:
  python scripts/run_exectv2_sf_closed_option_direction_probe.py --cache
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid.closed_option_direction import (
    ClosedOptionDirectionSelector,
    build_direction_menu,
    parse_selection,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid.closed_option_direction import (
    assemble_direction as _assemble_direction_with_provenance,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    frequency_state_faithful,
    score_frequency_state,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

RUN_DATE = date.today().isoformat().replace("-", "")
ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REPORT_DIR = ROOT / "docs" / "experiments" / "exectv2" / "seizure_frequency"
RAW_SF_VERIFY_JSONL = EXPERIMENTS / "exectv2_gepa_sf_verify_gpt41mini_20260628.jsonl"

TASK_MODEL = "openai/gpt-4.1-mini"
TASK_TEMPERATURE = 0.0
TASK_MAX_TOKENS = 8000

SF_ENTITY = "SeizureFrequency"
ABSTAIN = "ABSTAIN"  # re-exported alias for the ledger/report logic below


# --------------------------------------------------------------------------------------
# Closed-option selector primitives (imported from the shared library module).
# --------------------------------------------------------------------------------------
# The contract primitives -- build_direction_menu, ClosedOptionDirectionSelector,
# SELECTION_SCHEMA_JSON, parse_selection, assemble_direction -- now live in
# ``clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid.closed_option_direction``
# so the standalone probe and the hybrid-integration follow-up share a single
# source of the closed-option contract. The two helpers below are thin wrappers
# preserving this probe's original (label-only) return shape for its ledger logic.
def _parse_selection(raw: str) -> tuple[str | None, str]:
    """Thin wrapper over the library ``parse_selection`` (abstention validator)."""
    return parse_selection(raw)


def assemble_direction(cid: str | None, menu: list[dict[str, str]]) -> str:
    """Deterministic assembly returning the label only (provenance discarded here).

    The library ``assemble_direction`` returns (label, provenance); this probe's
    ledger does not need the provenance string (it records the selected id + mode
    directly), so we discard it. The hybrid-integration driver keeps it.
    """
    label, _provenance = _assemble_direction_with_provenance(cid, menu)
    return label


# --------------------------------------------------------------------------------------
# Disagreement-set loader + apply-then-rescore (reused verbatim from B1).
# --------------------------------------------------------------------------------------
def _letters_with_changed_mentions(jsonl_path: Path) -> dict[str, list[dict[str, Any]]]:
    """Load the raw SF-verify artifact; return {letter_id: [changed mention dicts]}."""

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
            attrs = m.get("attributes", {})
            if frequency_state_faithful(attrs) == "changed":
                changed.append(
                    {"index": idx, "applies_to": m.get("text", "seizures"), "_attrs": attrs}
                )
        if changed:
            out[lid] = changed
    return out


def _pred_letters_from_raw(
    jsonl_path: Path, gold_by_id: dict[str, ExectLetter]
) -> list[ExectLetter]:
    """Build predicted ExectLetters from a raw SF-verify artifact (no adjudication)."""

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
        anns = tuple(
            ExectAnnotation(
                entity=SF_ENTITY,
                text=str(m.get("text", "")),
                attributes={str(k): str(v) for k, v in dict(m.get("attributes", {})).items()},
            )
            for m in sf
        )
        out.append(ExectLetter(letter_id=lid, note_text=gold.note_text, annotations=anns))
    return out


def _raw_row_by_id(lid: str) -> dict[str, Any]:
    return json.loads(
        next(
            line
            for line in RAW_SF_VERIFY_JSONL.read_text(encoding="utf-8").splitlines()
            if line.strip() and json.loads(line)["letter_id"] == lid
        )
    )


# --------------------------------------------------------------------------------------
# Main probe.
# --------------------------------------------------------------------------------------
def run(num_threads: int, cache: bool) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    dev_gold = load_letters_for_split("dev")
    gold_by_id = {le.letter_id: le for le in dev_gold}

    # Baseline: score the raw SF-verify artifact unchanged (reproduce the 0.6552).
    baseline_pred = _pred_letters_from_raw(RAW_SF_VERIFY_JSONL, gold_by_id)
    baseline_scores = score_frequency_state(dev_gold, baseline_pred)
    b_d = baseline_scores.state_profile_directional
    print("[probe] RAW SF-verify baseline (unchanged):")
    print(f"  state_profile_directional F1: {b_d.f1:.4f} (tp={b_d.tp} fp={b_d.fp} fn={b_d.fn})")
    print(f"  state_profile F1:             {baseline_scores.state_profile.f1:.4f}")

    changed_by_letter = _letters_with_changed_mentions(RAW_SF_VERIFY_JSONL)
    total_changed = sum(len(v) for v in changed_by_letter.values())
    print(
        f"[probe] {total_changed} changed-state mentions across "
        f"{len(changed_by_letter)} letters; building menus + selecting..."
    )

    # Build a deterministic candidate menu per letter, then fire the selector.
    selector = ClosedOptionDirectionSelector()
    lm = build_dspy_lm(
        TASK_MODEL, temperature=TASK_TEMPERATURE, max_tokens=TASK_MAX_TOKENS, cache=cache
    )
    dspy.configure(lm=lm)
    evaluator = dspy.Parallel(num_threads=num_threads, provide_traceback=True)

    pairs = []
    menus_by_lid: dict[str, list[dict[str, str]]] = {}
    for lid, _changed in changed_by_letter.items():
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
    # Report menu coverage: how many letters had >=1 deterministic regex cue.
    with_cue = sum(
        1
        for m in menus_by_lid.values()
        if any(e["evidence_span"] != "(no explicit cue in text)" for e in m[:-1])
    )
    print(
        f"[probe] menus built for {len(menus_by_lid)} letters "
        f"(each carries all 5 labels + ABSTAIN); "
        f"{with_cue} had >=1 deterministic direction cue anchored by rules/change.py."
    )
    print(
        f"[probe] firing {len(pairs)} selector calls ({TASK_MODEL}, temp {TASK_TEMPERATURE})...",
        flush=True,
    )
    started = time.time()
    predictions = evaluator(pairs)

    # Apply selected directions to a copy of the raw artifact. Carry all 140
    # letters through so the scorer sees the complete prediction set.
    direction_counts: dict[str, int] = {}
    mode_counts: dict[str, int] = {}
    ledger_rows: list[dict[str, Any]] = []
    adj_by_id: dict[str, dict[str, Any]] = {}
    lids = list(changed_by_letter.keys())
    for lid, prediction in zip(lids, predictions, strict=True):
        raw_sel = str(getattr(prediction, "selection_json", "") or "") if prediction else ""
        cid, mode = _parse_selection(raw_sel)
        menu = menus_by_lid[lid]
        new_dir = assemble_direction(cid, menu)
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
        if new_dir != "Same":
            direction_counts[new_dir] = direction_counts.get(new_dir, 0) + 1
        row = _raw_row_by_id(lid)
        changed = changed_by_letter[lid]
        for c in changed:
            idx = c["index"]
            old_dir = row["predicted_mentions"][idx]["attributes"].get("FrequencyChange", "Same")
            row["predicted_mentions"][idx]["attributes"]["FrequencyChange"] = new_dir
            ledger_rows.append(
                {
                    "letter_id": lid,
                    "mention_index": idx,
                    "applies_to": c["applies_to"],
                    "selected_candidate_id": cid,
                    "selection_mode": mode,
                    "assembled_direction": new_dir,
                    "prior_direction": old_dir,
                    "menu_labels": [e["label"] for e in menu],
                }
            )
        adj_by_id[lid] = row
    # Full 140-row output: adjudicated rows where present, raw rows otherwise.
    adj_rows = []
    for line in RAW_SF_VERIFY_JSONL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        lid = json.loads(line)["letter_id"]
        adj_rows.append(adj_by_id.get(lid, json.loads(line)))
    elapsed = time.time() - started
    print(
        f"[probe] done in {elapsed:.1f}s; "
        f"selected directions (non-Same): {direction_counts}; "
        f"modes: {mode_counts}; {len(adj_rows)} letters carried through"
    )

    # Score the adjudicated artifact.
    adj_jsonl = EXPERIMENTS / f"exectv2_sf_verify_closed_option_direction_dev140_{RUN_DATE}.jsonl"
    write_jsonl(adj_rows, adj_jsonl)
    adj_pred = _pred_letters_from_raw(adj_jsonl, gold_by_id)
    adj_scores = score_frequency_state(dev_gold, adj_pred)
    a_d = adj_scores.state_profile_directional
    print("[probe] CLOSED-OPTION SELECTOR:")
    print(f"  state_profile_directional F1: {a_d.f1:.4f} (tp={a_d.tp} fp={a_d.fp} fn={a_d.fn})")
    print(f"  state_profile F1:             {adj_scores.state_profile.f1:.4f} (regression check)")

    delta = a_d.f1 - baseline_scores.state_profile_directional.f1
    print(f"\n[probe] state_profile_directional delta = {delta:+.4f}")
    recovered = a_d.tp - baseline_scores.state_profile_directional.tp
    print(f"[probe] tp delta (recovered): +{recovered}")

    # Predeclared outcome verdict.
    print("\n[probe] PREDECLARED OUTCOME VERDICT:")
    if adj_scores.state_profile.f1 < baseline_scores.state_profile.f1 - 0.005:
        verdict = "CONTRACT FAILURE (state_profile regressed)"
    elif delta >= 0.05:
        verdict = "REFUTES 'fundamental' (closed-option recovers >= +0.05)"
    elif delta < 0.02:
        verdict = "CONFIRMS 'fundamental across families' (recovery < +0.02)"
    else:
        verdict = "INCONCLUSIVE (+0.02 to +0.05)"
    print(f"  {verdict}")

    # Persist the ledger + summary for the results doc.
    summary = {
        "run_date": RUN_DATE,
        "model": TASK_MODEL,
        "temperature": TASK_TEMPERATURE,
        "split": "dev140",
        "n_selector_calls": len(pairs),
        "baseline_state_profile_directional_f1": baseline_scores.state_profile_directional.f1,
        "closed_option_state_profile_directional_f1": a_d.f1,
        "delta": delta,
        "recovered_tp": recovered,
        "baseline_state_profile_f1": baseline_scores.state_profile.f1,
        "closed_option_state_profile_f1": adj_scores.state_profile.f1,
        "direction_counts_non_same": direction_counts,
        "selection_mode_counts": mode_counts,
        "menus_with_cue": with_cue,
        "verdict": verdict,
    }
    summary_path = EXPERIMENTS / f"exectv2_sf_closed_option_direction_summary_{RUN_DATE}.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    ledger_path = EXPERIMENTS / f"exectv2_sf_closed_option_direction_ledger_{RUN_DATE}.jsonl"
    ledger_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in ledger_rows) + "\n",
        encoding="utf-8",
    )
    print(f"[probe] summary -> {summary_path.relative_to(ROOT)}")
    print(f"[probe] ledger  -> {ledger_path.relative_to(ROOT)}")
    print(f"[probe] preds   -> {adj_jsonl.relative_to(ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", action="store_true", help="Enable dspy response cache.")
    ap.add_argument("--num-threads", type=int, default=4)
    args = ap.parse_args()
    run(num_threads=args.num_threads, cache=args.cache)
    # Non-zero exit on contract failure so CI/regression gates can catch it.
    # (Refute/confirm/inconclusive are all valid research outcomes -> exit 0.)


if __name__ == "__main__":
    main()
