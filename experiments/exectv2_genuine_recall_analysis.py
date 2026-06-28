"""Characterize the GENUINE recall misses on saved GEPA predictions (zero-LLM).

After the convention-tax analysis showed convention is only ~+0.02 of the gap to the
v08 hybrid (0.9155) and the rest is genuine recall, this script characterizes WHAT the
model fails to extract: headline false negatives with NO overlapping prediction at all
(genuine misses, not surface mismatches). It clusters Diagnosis and SeizureFrequency
genuine misses into recoverable patterns and prints concrete letter context, so we can
see what a recall-recovery stage (the work the hybrid's verify/arbitrate do) must add.

Usage:
    uv run python experiments/exectv2_genuine_recall_analysis.py
    uv run python experiments/exectv2_genuine_recall_analysis.py --show 12
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
    is_epilepsy_seizure_type,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    concept_keys,
    frequency_state_keys,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
DEFAULT_RUN = "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628"


def _pred_letters(run_id: str) -> dict[str, ExectLetter]:
    rows = [
        json.loads(line)
        for line in (EXPERIMENTS / f"{run_id}.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    letters: dict[str, ExectLetter] = {}
    for row in rows:
        anns = tuple(
            ExectAnnotation(
                entity=m["entity"],
                text=m.get("text", ""),
                attributes={str(k): str(v) for k, v in (m.get("attributes") or {}).items()},
            )
            for m in row.get("predicted_mentions", [])
        )
        letters[row["letter_id"]] = ExectLetter(letter_id=row["letter_id"], note_text="", annotations=anns)
    return letters


def _context(note: str, ann: ExectAnnotation, width: int = 55) -> str:
    # Gold offsets are the reliable locator; fall back to de-hyphenated text search.
    note_low = note.lower()
    pos = -1
    if ann.start_index is not None and 0 <= ann.start_index < len(note):
        pos = ann.start_index
        span_len = (ann.end_index or pos) - pos
    else:
        for probe in (ann.raw_text or "", ann.text, ann.text.replace("-", " ")):
            if probe:
                pos = note_low.find(probe.lower()[:30])
                span_len = len(probe)
                if pos >= 0:
                    break
    if pos < 0:
        # Last resort: locate the first content word of the concept.
        head = ann.text.replace("-", " ").split()[0] if ann.text else ""
        pos = note_low.find(head.lower()) if head else -1
        span_len = len(head)
        if pos < 0:
            return "(not located)"
    start = max(0, pos - width)
    end = min(len(note), pos + span_len + width)
    return "…" + " ".join(note[start:end].split()) + "…"


def _dx_category(concept: str) -> str:
    if concept == "epilepsy":
        return "generic 'epilepsy'"
    if is_epilepsy_seizure_type(concept):
        return "named seizure type"
    if "epilep" in concept:
        return "specific epilepsy syndrome"
    return "other"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default=DEFAULT_RUN)
    parser.add_argument("--show", type=int, default=10, help="examples to print per family")
    args = parser.parse_args()

    gold = gepa_data.load_dev_letters()
    pred_by_id = _pred_letters(args.run)

    # --- Diagnosis genuine misses ---------------------------------------------
    dx_cat = Counter()
    dx_concept = Counter()
    dx_examples: list[tuple[str, str, str]] = []
    dx_letter_had_some_pred = 0
    dx_total_genuine = 0
    for g in gold:
        p = pred_by_id.get(g.letter_id)
        gold_anns = list(g.entities("Diagnosis"))
        pred_anns = list(p.entities("Diagnosis")) if p else []
        missed = set(concept_keys(gold_anns, "Diagnosis", "negation")) - set(
            concept_keys(pred_anns, "Diagnosis", "negation")
        )
        pred_phrases = [normalize_phrase(a.text) for a in pred_anns if a.text]
        for ann in gold_anns:
            for key in concept_keys([ann], "Diagnosis", "negation"):
                if key not in missed:
                    continue
                gp = normalize_phrase(ann.text)
                if any(gp and (gp in pp or pp in gp) for pp in pred_phrases):
                    continue  # convention miss, not genuine
                dx_total_genuine += 1
                concept = canonicalize_diagnosis_concept(ann.text)
                dx_concept[concept] += 1
                dx_cat[_dx_category(concept)] += 1
                if pred_anns:
                    dx_letter_had_some_pred += 1
                dx_examples.append((g.letter_id, concept, _context(g.note_text, ann)))

    print(f"# Genuine-recall-miss analysis — {args.run} (dev140)\n")
    print(f"## Diagnosis genuine misses (no overlapping prediction): {dx_total_genuine}")
    print(f"  ({dx_letter_had_some_pred} occurred in letters where the model DID emit other Dx — "
          "so it's a per-concept omission, not a blank letter)")
    print("  by category:")
    for cat, n in dx_cat.most_common():
        print(f"    {cat:<28}{n:>3} ({100 * n / dx_total_genuine:.0f}%)")
    print("  most-missed concepts:")
    for concept, n in dx_concept.most_common(10):
        print(f"    {concept:<40}{n:>3}")
    print(f"\n  examples (first {args.show}):")
    for lid, concept, ctx in dx_examples[: args.show]:
        print(f"    [{lid}] MISSED {concept!r}\n      {ctx}")

    # --- SeizureFrequency genuine misses --------------------------------------
    sf_state = Counter()
    sf_examples: list[tuple[str, str, str]] = []
    sf_total_genuine = 0
    sf_letter_had_some_pred = 0
    for g in gold:
        p = pred_by_id.get(g.letter_id)
        gold_anns = list(g.entities("SeizureFrequency"))
        pred_anns = list(p.entities("SeizureFrequency")) if p else []
        missed = set(frequency_state_keys(gold_anns, "clinical_headline")) - set(
            frequency_state_keys(pred_anns, "clinical_headline")
        )
        pred_phrases = [normalize_phrase(a.text) for a in pred_anns if a.text]
        for ann in gold_anns:
            for key in frequency_state_keys([ann], "clinical_headline"):
                if key not in missed:
                    continue
                gp = normalize_phrase(ann.text)
                if any(gp and (gp in pp or pp in gp) for pp in pred_phrases):
                    continue
                sf_total_genuine += 1
                attrs = ann.attributes
                if any(attrs.get(k) == "0" for k in ("NumberOfSeizures", "LowerNumberOfSeizures")):
                    state = "seizure_free"
                elif any(attrs.get(k) for k in ("NumberOfSeizures", "LowerNumberOfSeizures", "UpperNumberOfSeizures")):
                    state = "active_rate"
                elif attrs.get("FrequencyChange"):
                    state = "changed"
                else:
                    state = "other"
                sf_state[state] += 1
                if pred_anns:
                    sf_letter_had_some_pred += 1
                sf_examples.append((g.letter_id, f"{ann.text} [{state}]", _context(g.note_text, ann)))

    print(f"\n## SeizureFrequency genuine misses (no overlapping prediction): {sf_total_genuine}")
    print(f"  ({sf_letter_had_some_pred} in letters where the model DID emit other SF)")
    print("  by gold state:")
    for state, n in sf_state.most_common():
        print(f"    {state:<28}{n:>3} ({100 * n / sf_total_genuine:.0f}%)")
    print(f"\n  examples (first {args.show}):")
    for lid, label, ctx in sf_examples[: args.show]:
        print(f"    [{lid}] MISSED {label}\n      {ctx}")


if __name__ == "__main__":
    main()
