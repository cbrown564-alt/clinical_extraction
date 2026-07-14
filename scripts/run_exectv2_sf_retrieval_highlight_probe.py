"""SF retrieval-highlight salience priming — item 3 of predecessor_synthesis_followups_2026-07-06.

ORTHOSECOND LEG OF THE CROSS-FAMILY BET ON THE SF CAPACITY-VS-EXECUTION GAP.

Item 2 (closed-option selector) tested the *generation-contract* axis and REFUTED
"fundamental" (+0.0552): the gap does not survive a change of contract. This probe
tests the orthogonal *input* axis: priming direction-relevant spans BEFORE the
coupled extraction call. If the gap is about coupling cognitive load, priming the
relevant spans first could deploy the capacity that call-restructuring and
contract-constraining deploy from the other axes.

Motivating predecessor finding (dissertation-recursive): Gan winner
`gpt_5_5 + Gan_retrieval_highlight` scored Pragmatic µF1 0.840 vs 0.760 for
`cot_label`; the decisive evidence is the ablation `Gan_retrieval_only_ablation`
(spans only, no full letter) scored 0.520 — a -32pp drop proving retrieval works
by salience-priming the input, not by direct lookup.

Three arms on the same SF disagreement set (the only difference is the
`letter_text` field fed to the LLM):
  Arm A (baseline, control):  raw letter_text, neutral instruction. Reproduces B1.
  Arm B (highlight):          letter_text with deterministic direction/temporal
                              spans wrapped in [[HL]]...[[/HL]].
  Arm C (highlight-only):     only the highlighted span evidence texts.

The adjudicator free-writes a 5-way direction label per changed mention — the
SAME output contract as B1's DirectionAdjudicationSignature. The lever under test
is the *input*, not the generation contract (that was item 2). The two items are
independent orthogonal levers on the same null hypothesis and must not be conflated.

Mirrors run_exectv2_sf_closed_option_direction_probe.py (item 2) and
run_exectv2_sf_direction_probe.py::run_b1 for the disagreement-set loader, the
apply-direction-then-rescore pattern, the LLM wrapper, and the scorer.

Predeclaration: docs/experiments/exectv2/seizure_frequency/
               exectv2_sf_retrieval_highlight_predeclaration_2026-07-06.md

Usage:
  python scripts/run_exectv2_sf_retrieval_highlight_probe.py --cache
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rule_metadata import (
    DEFAULT_ABLATION,
    ExtractionContext,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.adapters.extraction import (  # noqa: E501
    CHANGE_RULES,
    TEMPORAL_RULES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    extract_json_object,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    frequency_state_faithful,
    score_frequency_state,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows as write_jsonl,
)

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

# Highlight markers (the tokens named in the umbrella plan). Inserted right-to-
# left by char offset so earlier offsets stay valid as later ones are wrapped.
HL_OPEN = "[[HL]]"
HL_CLOSE = "[[/HL]]"

# The deterministic rule bank sourcing direction/temporal salience spans. This is
# the ExECTv2 analogue of dissertation-recursive's `retrieve_frequency_spans()`
# over its `_FREQUENCY_SENTENCE_PATTERNS` regex bank.
HIGHLIGHT_RULES = [*CHANGE_RULES, *TEMPORAL_RULES]


# --------------------------------------------------------------------------------------
# Deterministic span selection (the retrieval-highlight substrate).
# --------------------------------------------------------------------------------------
class HighlightSpan(dict):
    """A char-offset salience span: {start, end, evidence, rule_id}.

    Kept as a dict subclass so it serializes to JSON unchanged in the ledger.
    """


def select_highlight_spans(note_text: str) -> list[HighlightSpan]:
    """Run the deterministic direction/temporal rule bank over one letter.

    Returns char-offset spans with evidence text + rule_id, deduped so no two
    spans overlap (earliest-start wins; an enclosing span wins over a later one
    that starts within it). If no rule matches, returns [] — Arm B then runs
    with zero highlights (the LLM sees a clean letter, equivalent to Arm A),
    which is the honest "no deterministic cue" case, mirroring item 2's decision
    to always offer the full menu rather than gating the experiment on cue
    presence.
    """

    raw: list[HighlightSpan] = []
    ctx = ExtractionContext(text=note_text)
    for spec in HIGHLIGHT_RULES:
        for built in spec.apply(ctx, DEFAULT_ABLATION):
            if built is None:
                continue
            span = getattr(built, "span", None)
            evidence = getattr(built, "evidence", None)
            rule_id = getattr(built, "rule_id", None) or spec.rule_id
            if span is None or evidence is None:
                continue
            start, end = span
            raw.append(
                HighlightSpan(
                    start=int(start),
                    end=int(end),
                    evidence=str(evidence),
                    rule_id=str(rule_id),
                )
            )
    # Deterministic order then greedy non-overlapping keep (earliest start wins).
    raw.sort(key=lambda s: (s["start"], s["end"]))
    kept: list[HighlightSpan] = []
    for s in raw:
        if kept and s["start"] < kept[-1]["end"]:
            # Overlaps the last kept span (which started earlier or at the same
            # point). Drop the later/contained one.
            continue
        kept.append(s)
    return kept


def render_highlighted_text(note_text: str, spans: list[HighlightSpan]) -> str:
    """Wrap the selected spans in [[HL]]...[[/HL]] markers.

    Insert right-to-left by char offset so earlier offsets stay valid. Spans are
    assumed non-overlapping (select_highlight_spans dedups), but the right-to-
    left insertion is correct regardless and is the safe ordering.
    """

    out = note_text
    for s in sorted(spans, key=lambda x: x["start"], reverse=True):
        out = out[: s["start"]] + HL_OPEN + out[s["start"] : s["end"]] + HL_CLOSE + out[s["end"] :]
    return out


def render_highlight_only(spans: list[HighlightSpan]) -> str:
    """Concatenate the highlighted span evidence texts (Arm C: no full letter).

    Join with newlines. If no spans matched, returns a short explicit note so the
    Arm C call is not a literal empty string.
    """

    if not spans:
        return "(no direction or temporal cues were found in this letter)"
    return "\n".join(s["evidence"] for s in spans)


# --------------------------------------------------------------------------------------
# Highlight direction adjudicator (free-write contract, mirrors B1 exactly).
# --------------------------------------------------------------------------------------
class HighlightDirectionAdjudicatorSignature(dspy.Signature):
    """You read a clinical letter and a list of seizure-frequency change mentions.

    For each change mention, determine the DIRECTION of the change as one of:
    Increased, Decreased, Frequent, Infrequent, Same. Judge direction by comparing
    the CURRENT frequency to the PRIOR frequency described in the letter. If the
    letter does not state a direction, use Same. Return a JSON object mapping each
    change mention (by index) to its direction.

    If the letter contains highlighted spans marked [[HL]]...[[/HL]], those spans
    are the clinically relevant direction cues; weigh them when extracting.
    """

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    change_mentions: str = dspy.InputField(
        desc="JSON list of {index, applies_to} for each change mention to adjudicate."
    )
    instruction: str = dspy.InputField(desc="Per-arm guidance on how to use the input.")
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    directions_json: str = dspy.OutputField(
        desc='One JSON object {"directions": [{"index": 0, "direction": '
        '"Increased|Decreased|Frequent|Infrequent|Same"}]}. No markdown.'
    )


DIRECTION_SCHEMA_JSON = json.dumps(
    {
        "directions": [
            {
                "index": "the change mention index",
                "direction": "Increased | Decreased | Frequent | Infrequent | Same",
            }
        ]
    },
    ensure_ascii=False,
    sort_keys=True,
)

# Per-arm instructions. Arm A is neutral (no mention of highlights); Arms B/C tell
# the model the highlights are direction cues.
INSTRUCTION_A = "Adjudicate the direction of each change mention from the letter."
INSTRUCTION_BC = (
    "The highlighted spans (marked [[HL]]...[[/HL]]) are the clinically relevant "
    "direction cues; weigh them when extracting the direction of each change mention."
)


class HighlightDirectionAdjudicator(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.adjudicate = dspy.Predict(HighlightDirectionAdjudicatorSignature)

    def forward(self, letter_text: str, change_mentions: str, instruction: str) -> dspy.Prediction:
        out = self.adjudicate(
            letter_text=letter_text,
            change_mentions=change_mentions,
            instruction=instruction,
            output_schema=DIRECTION_SCHEMA_JSON,
        )
        return dspy.Prediction(directions_json=str(getattr(out, "directions_json", "") or ""))


def _parse_directions(raw: str) -> dict[int, str]:
    """Parse {index: direction} from the adjudicator output and normalize to vocab.

    Verbatim from B1 (run_exectv2_sf_direction_probe.py:149-170): the model
    free-writes a label, we title-case-match it against the closed vocab.
    """

    try:
        payload = json.loads(extract_json_object(raw))
    except Exception:
        return {}
    out: dict[int, str] = {}
    for d in payload.get("directions", []):
        if not isinstance(d, dict):
            continue
        try:
            idx = int(d.get("index"))
        except (TypeError, ValueError):
            continue
        direction = str(d.get("direction", "")).strip()
        for v in DIRECTION_VOCAB:
            if direction.lower() == v.lower():
                out[idx] = v
                break
    return out


# --------------------------------------------------------------------------------------
# Disagreement-set loader + apply-then-rescore (reused verbatim from item 2 / B1).
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
# Per-arm run: build inputs, fire the adjudicator, apply, rescore.
# --------------------------------------------------------------------------------------
def _run_arm(
    arm: str,
    instruction: str,
    letter_text_for: Any,  # callable(lid, note_text, spans) -> str
    changed_by_letter: dict[str, list[dict[str, Any]]],
    gold_by_id: dict[str, ExectLetter],
    spans_by_lid: dict[str, list[HighlightSpan]],
    adjudicator: HighlightDirectionAdjudicator,
    evaluator: Any,
    dev_gold: list[ExectLetter],
    ledger_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Run one arm end-to-end and return its score summary.

    `letter_text_for(lid, note_text, spans)` returns the per-letter text to feed
    the adjudicator for this arm (raw / highlighted / highlight-only).
    """

    pairs = []
    for lid, changed in changed_by_letter.items():
        note_text = gold_by_id[lid].note_text
        text_for_llm = letter_text_for(lid, note_text, spans_by_lid[lid])
        mentions_json = json.dumps(
            [{"index": c["index"], "applies_to": c["applies_to"]} for c in changed]
        )
        pairs.append(
            (
                adjudicator,
                {
                    "letter_text": text_for_llm,
                    "change_mentions": mentions_json,
                    "instruction": instruction,
                },
            )
        )
    print(
        f"[probe][{arm}] firing {len(pairs)} adjudicator calls "
        f"({TASK_MODEL}, temp {TASK_TEMPERATURE})...",
        flush=True,
    )
    started = time.time()
    predictions = evaluator(pairs)

    # Apply adjudicated directions to a copy of the raw artifact; carry all 140.
    direction_counts: dict[str, int] = {}
    adj_by_id: dict[str, dict[str, Any]] = {}
    lids = list(changed_by_letter.keys())
    for lid, prediction in zip(lids, predictions, strict=True):
        dirs = (
            _parse_directions(str(getattr(prediction, "directions_json", "") or ""))
            if prediction
            else {}
        )
        changed = changed_by_letter[lid]
        row = _raw_row_by_id(lid)
        for c in changed:
            idx = c["index"]
            old_dir = row["predicted_mentions"][idx]["attributes"].get("FrequencyChange", "Same")
            new_dir = dirs.get(idx)
            if new_dir and new_dir != "Same":
                row["predicted_mentions"][idx]["attributes"]["FrequencyChange"] = new_dir
                direction_counts[new_dir] = direction_counts.get(new_dir, 0) + 1
            ledger_rows.append(
                {
                    "letter_id": lid,
                    "arm": arm,
                    "mention_index": idx,
                    "applies_to": c["applies_to"],
                    "adjudicated_direction": new_dir or old_dir,
                    "prior_direction": old_dir,
                    "n_highlight_spans": len(spans_by_lid[lid]),
                    "highlight_evidence": [s["evidence"] for s in spans_by_lid[lid]],
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
        f"[probe][{arm}] done in {elapsed:.1f}s; "
        f"adjudicated directions (non-Same): {direction_counts}; "
        f"{len(adj_rows)} letters carried through"
    )

    # Score.
    adj_jsonl = EXPERIMENTS / f"exectv2_sf_verify_retrieval_highlight_{arm}_dev140_{RUN_DATE}.jsonl"
    write_jsonl(adj_rows, adj_jsonl)
    adj_pred = _pred_letters_from_raw(adj_jsonl, gold_by_id)
    scores = score_frequency_state(dev_gold, adj_pred)
    d = scores.state_profile_directional
    print(
        f"[probe][{arm}] state_profile_directional F1: {d.f1:.4f} (tp={d.tp} fp={d.fp} fn={d.fn})"
    )
    print(
        f"[probe][{arm}] state_profile F1:             {scores.state_profile.f1:.4f} "
        f"(regression check)"
    )
    return {
        "arm": arm,
        "directional_f1": d.f1,
        "directional_tp": d.tp,
        "directional_fp": d.fp,
        "directional_fn": d.fn,
        "state_profile_f1": scores.state_profile.f1,
        "direction_counts_non_same": direction_counts,
        "pred_jsonl": str(adj_jsonl.relative_to(ROOT)),
    }


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
        f"{len(changed_by_letter)} letters; selecting highlight spans..."
    )

    # Build deterministic highlight spans per letter (shared across all arms).
    spans_by_lid: dict[str, list[HighlightSpan]] = {}
    for lid in changed_by_letter:
        spans_by_lid[lid] = select_highlight_spans(gold_by_id[lid].note_text)
    letters_with_spans = sum(1 for s in spans_by_lid.values() if s)
    total_spans = sum(len(s) for s in spans_by_lid.values())
    print(
        f"[probe] highlight spans: {total_spans} spans across {len(changed_by_letter)} letters "
        f"({letters_with_spans} letters had >=1 deterministic direction/temporal cue)."
    )

    # Configure the shared adjudicator + LM (same model/temp as item 2 / B1).
    adjudicator = HighlightDirectionAdjudicator()
    lm = build_dspy_lm(
        TASK_MODEL, temperature=TASK_TEMPERATURE, max_tokens=TASK_MAX_TOKENS, cache=cache
    )
    dspy.configure(lm=lm)
    evaluator = dspy.Parallel(num_threads=num_threads, provide_traceback=True)

    ledger_rows: list[dict[str, Any]] = []

    # Arm A (baseline, control): raw letter_text, neutral instruction. Reproduces B1.
    print("\n[probe] === ARM A (baseline, control) ===")
    arm_a = _run_arm(
        "A",
        INSTRUCTION_A,
        lambda lid, note_text, spans: note_text,
        changed_by_letter,
        gold_by_id,
        spans_by_lid,
        adjudicator,
        evaluator,
        dev_gold,
        ledger_rows,
    )

    # CONTRACT FAILURE gate: Arm A must reproduce B1 (~0.7254). If it is far below,
    # the run is not a valid baseline and we do not interpret B/C.
    if arm_a["directional_f1"] < 0.68:
        print(
            f"\n[probe] CONTRACT FAILURE: Arm A baseline {arm_a['directional_f1']:.4f} "
            f"<< B1 reference 0.7254 — baseline did not reproduce; B/C not interpreted."
        )
        summary = {
            "run_date": RUN_DATE,
            "model": TASK_MODEL,
            "temperature": TASK_TEMPERATURE,
            "split": "dev140",
            "baseline_raw_directional_f1": baseline_scores.state_profile_directional.f1,
            "arms": {"A": arm_a},
            "verdict": "CONTRACT FAILURE (Arm A did not reproduce B1 baseline)",
        }
        _persist(summary, ledger_rows[:0])
        return

    # Arm B (highlight): letter_text with [[HL]]...[[/HL]] around the selected spans.
    print("\n[probe] === ARM B (highlight: full letter + highlighted spans) ===")
    arm_b = _run_arm(
        "B",
        INSTRUCTION_BC,
        lambda lid, note_text, spans: render_highlighted_text(note_text, spans),
        changed_by_letter,
        gold_by_id,
        spans_by_lid,
        adjudicator,
        evaluator,
        dev_gold,
        ledger_rows,
    )

    # Arm C (highlight-only ablation): only the highlighted span evidence texts.
    print("\n[probe] === ARM C (highlight-only ablation: spans, no full letter) ===")
    arm_c = _run_arm(
        "C",
        INSTRUCTION_BC,
        lambda lid, note_text, spans: render_highlight_only(spans),
        changed_by_letter,
        gold_by_id,
        spans_by_lid,
        adjudicator,
        evaluator,
        dev_gold,
        ledger_rows,
    )

    # Outcome verdicts (predeclared).
    b_minus_a = arm_b["directional_f1"] - arm_a["directional_f1"]
    c_minus_b = arm_c["directional_f1"] - arm_b["directional_f1"]
    print(f"\n[probe] Arm B - Arm A (primary input-lever delta) = {b_minus_a:+.4f}")
    print(f"[probe] Arm C - Arm B (mechanism: priming vs lookup) = {c_minus_b:+.4f}")

    print("\n[probe] PREDECLARED OUTCOME VERDICT (input lever):")
    if arm_b["state_profile_f1"] < baseline_scores.state_profile.f1 - 0.005:
        verdict = "CONTRACT FAILURE (Arm B state_profile regressed vs raw)"
    elif b_minus_a >= 0.05:
        verdict = "INPUT-SCAFFOLDING DEPLOYS CAPACITY (Arm B - Arm A >= +0.05)"
    elif b_minus_a < 0.02:
        verdict = (
            "HIGHLIGHT IS NOT THE LEVER (Arm B - Arm A < +0.02; Gan finding does not transfer)"
        )
    else:
        verdict = "INCONCLUSIVE (+0.02 to +0.05)"
    print(f"  {verdict}")

    print("[probe] MECHANISM (Arm C ablation):")
    if arm_c["directional_f1"] >= arm_b["directional_f1"] - 0.05:
        mechanism = "LOOKUP (Arm C ~= Arm B; retrieval works by direct lookup, different from Gan)"
    else:
        mechanism = "PRIMING (Arm C << Arm B; replicates dissertation-recursive -32pp mechanism)"
    print(f"  {mechanism}")

    summary = {
        "run_date": RUN_DATE,
        "model": TASK_MODEL,
        "temperature": TASK_TEMPERATURE,
        "split": "dev140",
        "n_letters_changed": len(changed_by_letter),
        "n_adjudicator_calls_per_arm": len(changed_by_letter),
        "baseline_raw_directional_f1": baseline_scores.state_profile_directional.f1,
        "baseline_raw_state_profile_f1": baseline_scores.state_profile.f1,
        "letters_with_deterministic_cue": letters_with_spans,
        "total_highlight_spans": total_spans,
        "arms": {"A": arm_a, "B": arm_b, "C": arm_c},
        "arm_b_minus_arm_a_directional": b_minus_a,
        "arm_c_minus_arm_b_directional": c_minus_b,
        "verdict": verdict,
        "mechanism": mechanism,
    }
    _persist(summary, ledger_rows)


def _persist(summary: dict[str, Any], ledger_rows: list[dict[str, Any]]) -> None:
    summary_path = EXPERIMENTS / f"exectv2_sf_retrieval_highlight_summary_{RUN_DATE}.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    ledger_path = EXPERIMENTS / f"exectv2_sf_retrieval_highlight_ledger_{RUN_DATE}.jsonl"
    ledger_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in ledger_rows) + "\n",
        encoding="utf-8",
    )
    print(f"[probe] summary -> {summary_path.relative_to(ROOT)}")
    print(f"[probe] ledger  -> {ledger_path.relative_to(ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", action="store_true", help="Enable dspy response cache.")
    ap.add_argument("--num-threads", type=int, default=4)
    args = ap.parse_args()
    run(num_threads=args.num_threads, cache=args.cache)
    # Non-zero exit only on contract failure is not raised here: the verdict is a
    # research outcome (refute/confirm/inconclusive are all valid). The
    # contract-failure case returns early after persisting a diagnostic summary.


if __name__ == "__main__":
    main()
