"""Canonical, bulletproof SF row-by-row analysis on EXACTLY the scored metric.

For EVERY dev140 letter, under the *direction-blind* ``state_profile`` metric (the one
we actually evaluate on — per-letter de-duplicated set of frequency_state_faithful states
in {seizure-free, active-rate, changed, unknown}, type-agnostic), this script captures and
projects:

* GOLD   — the ExECTv2 annotations' SF state set.
* STAGE 1 — the first LLM (the ``generate`` signature) output, projected.
* STAGE 2 — the verifier (the ``verify`` signature) output, projected.

Canonical run = the P2 gpt-4.1-mini two-stage SF program (run_id
``exectv2_gepa_sf_verify_gpt41mini_20260628``, state_profile 0.7413). Single model for both
stages, so the stage-1 -> stage-2 delta isolates the *verify step itself*, not a model swap.
The evolved instructions are read from the run's ``.instruction.txt``; both stages re-run with
``cache=True`` so this reproduces the stored stage-2 output near-exactly and is ~free.

Outputs (to ``OUT`` dir, default ``_sf_canonical``):
* ``_index.json``     — per-letter gold/s1/s2 state sets + tp/fp/fn + verdicts + verify-effect.
* ``_summary.json``   — aggregate stage-1 vs stage-2 state_profile + per-state confusion +
                        verify fixed/broke/left counts + reproduction checks.
* ``<letter>.md``     — per-letter substrate (letter text, gold/s1/s2 facts w/ all attributes,
                        projected states, the diff) for clinical adjudication. Written for every
                        letter where gold != stage-2 OR gold != stage-1 (the rows to adjudicate).

Usage:  uv run python experiments/exectv2_sf_canonical_row_analysis.py [OUT_DIR]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import dotenv
import dspy

from clinical_extraction.core.scoring import multiset_prf1, prf1_from_counts
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_sf_verify import (
    EVENT_SCHEMA_JSON,
    SfVerifyExtractor,
    events_to_sf_facts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.parsing import (
    parse_dedup_clinical_facts_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.projection import (
    to_predicted_letter_from_dedup_facts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    frequency_state_faithful,
    score_frequency_state,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "exectv2_gepa_sf_verify_gpt41mini_20260628"
INSTRUCTION_PATH = ROOT / "experiments" / f"{RUN_ID}.instruction.txt"
STORED_S2_JSONL = ROOT / "experiments" / f"{RUN_ID}.jsonl"
REASONER_EX_JSONL = (
    ROOT / "experiments" / "exectv2_gepa_sf_verify_p5_reasoner_reasoner_ex_20260629.jsonl"
)
MODEL = "openai/gpt-4.1-mini"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_sf_canonical"

STATE_ORDER = ["active-rate", "seizure-free", "changed", "unknown"]


def parse_instructions(path: Path) -> tuple[str, str]:
    """Split the run's combined ``=== generate === / === verify ===`` instruction file."""

    text = path.read_text(encoding="utf-8")
    gen_marker, ver_marker = "=== generate ===", "=== verify ==="
    gi, vi = text.index(gen_marker), text.index(ver_marker)
    generate = text[gi + len(gen_marker) : vi].strip()
    verify = text[vi + len(ver_marker) :].strip()
    return generate, verify


def states_of_entities(entities) -> list[str]:
    """The metric's per-letter key set: de-duplicated frequency_state_faithful states."""

    return list(dict.fromkeys(frequency_state_faithful(a.attributes) for a in entities))


def project_events(letter, events_json: str):
    """Mirror the metric projection: events JSON -> SF facts -> projected ExectLetter.

    Returns (pred_exect_letter, emitted_facts, kept_states, dropped_count).
    A fact is 'dropped' when projection (evidence-substring gating / adapter) removes it.
    """

    facts = events_to_sf_facts(events_json)
    raw = json.dumps({"clinical_facts": facts}, ensure_ascii=False)
    record, _errors = parse_dedup_clinical_facts_json(raw) if facts else (None, ["empty"])
    if record is None:
        predicted = PredictedLetter(letter_id=letter.letter_id, mentions=())
    else:
        predicted, *_ = to_predicted_letter_from_dedup_facts(letter, record)
    pred_exect = to_exect_letter(predicted)
    kept = pred_exect.entities("SeizureFrequency")
    return pred_exect, facts, kept


def gold_mentions_dump(letter) -> list[dict]:
    out = []
    for e in letter.entities("SeizureFrequency"):
        a = {str(k): str(v) for k, v in e.attributes.items()}
        out.append(
            {
                "text": e.raw_text,
                "state": frequency_state_faithful(e.attributes),
                "FC": a.get("FrequencyChange", ""),
                "N": a.get("NumberOfSeizures", ""),
                "Lo": a.get("LowerNumberOfSeizures", ""),
                "Hi": a.get("UpperNumberOfSeizures", ""),
                "CUI": a.get("CUI", ""),
                "CUIPhrase": a.get("CUIPhrase", ""),
            }
        )
    return out


def fact_dump(facts: list[dict], kept_entities) -> list[dict]:
    """Annotate each emitted fact with its projected state and whether projection kept it."""

    kept_states = [frequency_state_faithful(e.attributes) for e in kept_entities]
    out = []
    for f in facts:
        ev = f.get("evidence", "")
        out.append(
            {
                "applies_to": f.get("seizure_type", ""),
                "state": f.get("state", ""),
                "evidence": ev,
            }
        )
    return out, kept_states


def per_letter_prf1(gold_states, pred_states):
    p = multiset_prf1(gold_states, pred_states)
    return p.tp, p.fp, p.fn


def load_jsonl_states(path: Path, letters_by_id) -> dict[str, list[str]]:
    """Project a stored run jsonl's predicted_mentions to per-letter SF state sets."""

    out: dict[str, list[str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        lid = row["letter_id"]
        letters_by_id.get(lid)
        sf = [m for m in row.get("predicted_mentions", []) if m.get("entity") == "SeizureFrequency"]
        # Build an ExectLetter via the same projection used by the metric.
        [
            {
                "family": "seizure_frequency",
                "seizure_type": m.get("text", "seizures"),
                "state": frequency_state_faithful(m.get("attributes", {})),
                "evidence": m.get("text", ""),
            }
            for m in sf
        ]
        # The stored mentions are ALREADY projected (post-adapter), so derive states directly.
        states = list(dict.fromkeys(frequency_state_faithful(m.get("attributes", {})) for m in sf))
        out[lid] = states
    return out


def main() -> None:
    dotenv.load_dotenv(ROOT / ".env")
    OUT.mkdir(parents=True, exist_ok=True)

    generate_seed, verify_seed = parse_instructions(INSTRUCTION_PATH)
    lm = build_dspy_lm(MODEL, temperature=0.0, max_tokens=8000, cache=True)
    dspy.configure(lm=lm)
    program = SfVerifyExtractor(
        generate_seed=generate_seed,
        verify_seed=verify_seed,
        generate_lm=lm,
        verify_lm=lm,
    )

    letters = gepa_data.load_dev_letters()
    letters_by_id = {le.letter_id: le for le in letters}
    # Mark trainset membership (dev140 superset of valset; trainset letters are optimizer-seen).
    trainset_ids = {
        le.letter_id for le in gepa_data._shuffled_dev()[: gepa_data.DEFAULT_TRAINSET_SIZE]
    }

    stored_s2 = load_jsonl_states(STORED_S2_JSONL, letters_by_id)
    reasoner_ex = (
        load_jsonl_states(REASONER_EX_JSONL, letters_by_id) if REASONER_EX_JSONL.exists() else {}
    )

    gold_list, s1_pred_list, s2_pred_list = [], [], []
    index = []
    s1_tp = s1_fp = s1_fn = 0
    s2_tp = s2_fp = s2_fn = 0
    # Per-state confusion (stage 2).
    state_conf = {s: {"tp": 0, "fp": 0, "fn": 0} for s in STATE_ORDER}
    verify_effect = {
        "fixed": 0,
        "broke": 0,
        "same_correct": 0,
        "same_wrong": 0,
        "changed_partial": 0,
    }
    s2_repro_match = 0

    n = len(letters)
    for i, letter in enumerate(letters, 1):
        drafted = program.generate(letter_text=letter.note_text, output_schema=EVENT_SCHEMA_JSON)
        draft_json = str(getattr(drafted, "events_json", "") or "")
        verified = program.verify(
            letter_text=letter.note_text,
            draft_events_json=draft_json,
            output_schema=EVENT_SCHEMA_JSON,
        )
        verify_json = str(getattr(verified, "events_json", "") or "")

        s1_letter, s1_facts, s1_kept = project_events(letter, draft_json)
        s2_letter, s2_facts, s2_kept = project_events(letter, verify_json)

        gold_states = states_of_entities(letter.entities("SeizureFrequency"))
        s1_states = states_of_entities(s1_kept)
        s2_states = states_of_entities(s2_kept)

        gold_list.append(letter)
        s1_pred_list.append(s1_letter)
        s2_pred_list.append(s2_letter)

        a, b, c = per_letter_prf1(gold_states, s1_states)
        s1_tp += a
        s1_fp += b
        s1_fn += c
        d, e, f = per_letter_prf1(gold_states, s2_states)
        s2_tp += d
        s2_fp += e
        s2_fn += f

        gset, s2set = set(gold_states), set(s2_states)
        for s in STATE_ORDER:
            if s in gset and s in s2set:
                state_conf[s]["tp"] += 1
            elif s in s2set:
                state_conf[s]["fp"] += 1
            elif s in gset:
                state_conf[s]["fn"] += 1

        # Verify effect: per-letter F1 stage1 vs stage2.
        s1_f1 = prf1_from_counts(a, b, c).f1
        s2_f1 = prf1_from_counts(d, e, f).f1
        if s1_f1 >= 0.999 and s2_f1 >= 0.999:
            verify_effect["same_correct"] += 1
        elif s2_f1 > s1_f1 + 1e-9:
            verify_effect["fixed"] += 1
        elif s2_f1 < s1_f1 - 1e-9:
            verify_effect["broke"] += 1
        elif s1_f1 < 0.999 and abs(s1_f1 - s2_f1) <= 1e-9 and set(s1_states) != set(s2_states):
            verify_effect["changed_partial"] += 1
        else:
            verify_effect["same_wrong"] += 1

        # Reproduction check vs stored stage-2 jsonl.
        if set(s2_states) == set(stored_s2.get(letter.letter_id, [])):
            s2_repro_match += 1

        s1_correct = set(s1_states) == gset
        s2_correct = s2set == gset
        rec = {
            "letter_id": letter.letter_id,
            "in_trainset": letter.letter_id in trainset_ids,
            "gold_states": sorted(gold_states),
            "s1_states": sorted(s1_states),
            "s2_states": sorted(s2_states),
            "s1_exact": s1_correct,
            "s2_exact": s2_correct,
            "s2_tp_fp_fn": [d, e, f],
            "s2_missed": sorted(gset - s2set),
            "s2_spurious": sorted(s2set - gset),
            "reasoner_ex_states": sorted(reasoner_ex.get(letter.letter_id, [])),
        }
        index.append(rec)

        # Write substrate for any letter the model got wrong at either stage.
        if not s1_correct or not s2_correct:
            write_substrate(
                OUT,
                letter,
                rec,
                gold_mentions_dump(letter),
                fact_dump(s1_facts, s1_kept),
                fact_dump(s2_facts, s2_kept),
                draft_json,
                verify_json,
            )
        if i % 20 == 0:
            print(f"  ...{i}/{n}", flush=True)

    s1 = prf1_from_counts(s1_tp, s1_fp, s1_fn)
    s2 = prf1_from_counts(s2_tp, s2_fp, s2_fn)
    # Cross-validate stage-2 against the real metric.
    official = score_frequency_state(gold_list, s2_pred_list).state_profile
    official_s1 = score_frequency_state(gold_list, s1_pred_list).state_profile

    s1_exact = sum(1 for r in index if r["s1_exact"])
    s2_exact = sum(1 for r in index if r["s2_exact"])

    def conf_f1(d):
        return prf1_from_counts(d["tp"], d["fp"], d["fn"]).model_dump()

    summary = {
        "run_id": RUN_ID,
        "model": MODEL,
        "n_letters": n,
        "stage1_generate_state_profile": s1.model_dump(),
        "stage2_verify_state_profile": s2.model_dump(),
        "official_state_profile_stage2": official.model_dump(),
        "official_state_profile_stage1": official_s1.model_dump(),
        "decomposition_matches_official_stage2": abs(official.f1 - s2.f1) < 1e-9,
        "stage1_exact_letter_match": s1_exact,
        "stage2_exact_letter_match": s2_exact,
        "stage1_exact_rate": round(s1_exact / n, 4),
        "stage2_exact_rate": round(s2_exact / n, 4),
        "verify_effect": verify_effect,
        "per_state_confusion_stage2": {s: conf_f1(state_conf[s]) for s in STATE_ORDER},
        "stage2_reproduces_stored_jsonl": f"{s2_repro_match}/{n}",
    }
    (OUT / "_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (OUT / "_index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")

    print("\n=== CANONICAL SF STATE_PROFILE ANALYSIS ===")
    print(
        f"STAGE 1 (generate): F1={s1.f1:.4f} P={s1.precision:.4f} R={s1.recall:.4f}  "
        f"(tp={s1.tp} fp={s1.fp} fn={s1.fn})"
    )
    print(
        f"STAGE 2 (verify)  : F1={s2.f1:.4f} P={s2.precision:.4f} R={s2.recall:.4f}  "
        f"(tp={s2.tp} fp={s2.fp} fn={s2.fn})"
    )
    print(
        f"official metric stage2 F1={official.f1:.4f} (decomposition matches: "
        f"{summary['decomposition_matches_official_stage2']})"
    )
    print(
        f"per-letter EXACT match: stage1 {s1_exact}/{n} ({s1_exact / n:.1%})  "
        f"stage2 {s2_exact}/{n} ({s2_exact / n:.1%})"
    )
    print(f"verify effect: {verify_effect}")
    print(f"stage2 reproduces stored jsonl: {s2_repro_match}/{n}")
    print("per-state confusion (stage2):")
    for s in STATE_ORDER:
        c = state_conf[s]
        pr = prf1_from_counts(c["tp"], c["fp"], c["fn"])
        print(
            f"  {s:12s} tp={c['tp']:3d} fp={c['fp']:3d} fn={c['fn']:3d}  "
            f"P={pr.precision:.2f} R={pr.recall:.2f} F1={pr.f1:.2f}"
        )
    print(
        f"\nWrote per-letter substrate for {sum(1 for r in index if not r['s2_exact'] or not r['s1_exact'])} "
        f"letters + _index.json + _summary.json to {OUT}"
    )


def write_substrate(out_dir, letter, rec, gold_dump, s1_dump, s2_dump, draft_json, verify_json):
    s1_facts, s1_states = s1_dump
    s2_facts, s2_states = s2_dump
    lines = [
        f"# {letter.letter_id} — gold={rec['gold_states']} s1={rec['s1_states']} s2={rec['s2_states']}"
        f"  (s1_exact={rec['s1_exact']} s2_exact={rec['s2_exact']}, trainset={rec['in_trainset']})\n",
        f"stage2 missed={rec['s2_missed']} spurious={rec['s2_spurious']}\n",
        "## GOLD SeizureFrequency mentions",
    ]
    lines += [
        f"- {d['text']!r} -> state={d['state']} | FC={d['FC'] or '-'} N={d['N'] or '-'} "
        f"Lo/Hi={d['Lo'] or '-'}/{d['Hi'] or '-'} CUI={d['CUI'] or '-'} ({d['CUIPhrase'] or '-'})"
        for d in gold_dump
    ] or ["(none)"]
    lines += ["", "## STAGE 1 (generate) facts — projected states: " + str(s1_states)]
    lines += [
        f"- applies_to={d['applies_to']!r} state={d['state']} evidence={d['evidence']!r}"
        for d in s1_facts
    ] or ["(none)"]
    lines += ["", "## STAGE 2 (verify) facts — projected states: " + str(s2_states)]
    lines += [
        f"- applies_to={d['applies_to']!r} state={d['state']} evidence={d['evidence']!r}"
        for d in s2_facts
    ] or ["(none)"]
    lines += ["", "## RAW stage-1 events_json", "```json", draft_json.strip(), "```"]
    lines += ["", "## RAW stage-2 events_json", "```json", verify_json.strip(), "```"]
    lines += ["", "## FULL LETTER TEXT", "```", letter.note_text, "```"]
    (out_dir / f"{letter.letter_id}.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
