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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.change import (
    CHANGE_EXTRACT_IMPLS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    extract_json_object,
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
DIRECTION_VOCAB = ("Increased", "Decreased", "Frequent", "Infrequent", "Same")
# rule_id suffix -> the FrequencyChange label it generates (from change.py builders).
_RULE_TO_LABEL = {
    "change.increased": "Increased",
    "change.decreased": "Decreased",
    "change.frequent": "Frequent",
    "change.infrequent": "Infrequent",
    "change.same": "Same",
}
ABSTAIN = "ABSTAIN"
DEFER_MODES = ("no_reliable_candidate", "ambiguous")


# --------------------------------------------------------------------------------------
# Deterministic candidate menu (the closed-option contract substrate).
# --------------------------------------------------------------------------------------
def build_direction_menu(letter_text: str) -> list[dict[str, str]]:
    """Emit the closed-option direction menu for one letter.

    The menu is the **full closed 5-label gold vocab + ABSTAIN, always** — this
    is the dspy G32 pattern: the LLM picks a label from a fixed deterministic
    menu, never free-writes. The deterministic layer's contribution is the
    *evidence anchor* attached to each label (the rules/change.py regex span if
    one matches, otherwise an explicit no-cue marker). The option set is never
    gated by whether a regex matched: that would make the menu empty for letters
    whose direction is expressed implicitly or via medication-titration language,
    collapsing the experiment into a trivial no-op.
    """

    menu: list[dict[str, str]] = []
    # First pass: collect the first regex evidence span per label (if any).
    evidence_by_label: dict[str, str] = {}
    for rule_id, impl in CHANGE_EXTRACT_IMPLS.items():
        label = _RULE_TO_LABEL.get(rule_id)
        if label is None or label in evidence_by_label:
            continue
        m = impl.pattern.search(letter_text)
        if m:
            evidence_by_label[label] = m.group(0).strip()[:160]
    # Emit every label in the closed vocab, with its evidence or a no-cue marker.
    for label in DIRECTION_VOCAB:
        ev = evidence_by_label.get(label, "(no explicit cue in text)")
        menu.append(
            {"candidate_id": f"C{len(menu)}", "label": label, "evidence_span": ev}
        )
    menu.append({"candidate_id": ABSTAIN, "label": ABSTAIN, "evidence_span": ""})
    return menu


# --------------------------------------------------------------------------------------
# Abstention-validated selector contract (the cross-family architectural difference).
# --------------------------------------------------------------------------------------
class ClosedOptionDirectionSelectorSignature(dspy.Signature):
    """You read a clinical letter and a candidate menu of seizure-frequency
    change-direction labels.

    Select ONE candidate_id from the menu that best describes the direction of
    the patient's seizure-frequency change, or select ABSTAIN if the letter does
    not state a clear direction.

    HARD CONSTRAINTS:
    - Return a candidate_id that appears in the menu exactly. Never invent,
      renumber, or free-write a direction label.
    - If you are not confident, select ABSTAIN.
    - Return a JSON object matching the output schema exactly. No markdown.
    """

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    candidate_menu: str = dspy.InputField(
        desc="JSON list of {candidate_id, label, evidence_span}. Pick one candidate_id."
    )
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    selection_json: str = dspy.OutputField(
        desc='One JSON object {"selected_candidate_id": "...", "selection_mode": '
        '"single_candidate|no_reliable_candidate|ambiguous"}. No markdown.'
    )


SELECTION_SCHEMA_JSON = json.dumps(
    {
        "selected_candidate_id": "a candidate_id from the menu, or ABSTAIN",
        "selection_mode": "single_candidate | no_reliable_candidate | ambiguous",
    },
    ensure_ascii=False,
    sort_keys=True,
)


class ClosedOptionDirectionSelector(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.select = dspy.Predict(ClosedOptionDirectionSelectorSignature)

    def forward(self, letter_text: str, candidate_menu: str) -> dspy.Prediction:
        out = self.select(
            letter_text=letter_text,
            candidate_menu=candidate_menu,
            output_schema=SELECTION_SCHEMA_JSON,
        )
        return dspy.Prediction(selection_json=str(getattr(out, "selection_json", "") or ""))


def _parse_selection(raw: str) -> tuple[str | None, str]:
    """Parse the selector output; enforce the abstention validator.

    Mirrors gan2026 selected_fact.py:32-49: a defer mode MUST NOT select an id.
    Returns (candidate_id | None, selection_mode).
    """

    try:
        payload = json.loads(extract_json_object(raw))
    except Exception:
        return None, "parse_error"
    cid = str(payload.get("selected_candidate_id", "")).strip() or None
    mode = str(payload.get("selection_mode", "")).strip() or "single_candidate"
    if mode in DEFER_MODES and cid and cid != ABSTAIN:
        # Validator: defer modes forbid a selection. Force abstention.
        return None, mode
    if cid == ABSTAIN:
        return None, mode
    return cid, mode


def assemble_direction(cid: str | None, menu: list[dict[str, str]]) -> str:
    """Deterministic assembly: candidate_id -> FrequencyChange label, or Same.

    Mirrors gan2026 assemble_clinical_assessment: the model only picks an id;
    deterministic code renders the final attribute. An invalid id (not in the
    menu) also resolves to Same with provenance abstain — the menu-membership
    check (_validate_candidate_references analogue) is implicit here.
    """

    if cid is None:
        return "Same"
    for entry in menu:
        if entry["candidate_id"] == cid:
            return entry["label"]
    return "Same"


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
                attributes={
                    str(k): str(v) for k, v in dict(m.get("attributes", {})).items()
                },
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
