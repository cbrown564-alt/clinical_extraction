#!/usr/bin/env python3
"""SF magnitude gold-annotation audit (pathway #2, zero LLM calls).

Pathway #2 of the 2026-07-08 SF follow-up queue. The vocab-deconflation probe
(entry 38) showed the ``FrequencyChange`` magnitude/direction conflation explains
~60% of the integration gap but left a residual direction gap (+0.0226). This
audit asks the orthogonal gold-level question: are the magnitude labels
(``Frequent``/``Infrequent``) themselves predominantly **mislabeled direction**
(a gold-annotation defect worth a manuscript caveat) or **genuine magnitude**
(the conflation is by design)?

Frozen surface: dev140 only (test59/full-200 stay locked). Zero LLM calls, zero
scorer/gold changes. This driver is read-only inspection of the gold annotations
plus their source text; the verdict is a classification of each magnitude label.

The audit *reproduces* the magnitude-label count (Frequent 12 / Infrequent 7 =
19 total) from the gold files and prints, for each, the full sentence context
needed to classify it. It does not score anything; it produces the substrate
for the manual classification recorded in the results doc.
"""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = REPO_ROOT / "experiments" / "exectv2_sf_magnitude_gold_audit_20260708.jsonl"

MAGNITUDE_VALUES = {"Frequent", "Infrequent"}


def _sentence_window(note_text: str, start: int, end: int, *, pad: int = 220) -> str:
    """Return a generous window around [start, end) with the span fenced.

    Gold ``start_index``/``end_index`` drift against ``note_text`` (spelling was
    corrected in the .txt files after annotation without updating offsets), so we
    do not trust the slice exactly; the window is deliberately generous and the
    raw annotation ``text`` is printed alongside for cross-reference.
    """
    lo = max(0, start - pad)
    hi = min(len(note_text), end + pad)
    pre = note_text[lo:start]
    mid = note_text[start:end]
    post = note_text[end:hi]
    return f"{pre}>>{mid}<<{post}"


def main() -> None:
    letters = load_letters_for_split("dev")
    rows: list[dict] = []

    for letter in letters:
        note_text = letter.note_text
        for ann in letter.entities("SeizureFrequency"):
            change = ann.attributes.get("FrequencyChange")
            if change not in MAGNITUDE_VALUES:
                continue
            try:
                start = int(ann.start_index)
                end = int(ann.end_index)
            except (TypeError, ValueError):
                start, end = -1, -1
            row = {
                "letter_id": letter.letter_id,
                "frequency_change": change,
                "annotation_text": ann.text,
                "raw_text": ann.raw_text,
                "cuiphrase": ann.attributes.get("CUIPhrase"),
                "start_index": start,
                "end_index": end,
                "offset_slice": note_text[start:end] if start >= 0 else "",
                "context": (
                    _sentence_window(note_text, start, end) if start >= 0 else note_text[:400]
                ),
            }
            rows.append(row)

    rows.sort(key=lambda r: (r["frequency_change"], r["letter_id"]))

    print(f"# dev140 magnitude FrequencyChange annotations: {len(rows)}")
    counts = {"Frequent": 0, "Infrequent": 0}
    for r in rows:
        counts[r["frequency_change"]] += 1
    print(f"# Frequent={counts['Frequent']}  Infrequent={counts['Infrequent']}")
    print()

    for i, r in enumerate(rows, 1):
        print(f"--- [{i:02d}] {r['letter_id']} | {r['frequency_change']} ---")
        print(f"annotation text : {r['annotation_text']!r}")
        print(f"cuiphrase       : {r['cuiphrase']!r}")
        print(f"start/end       : {r['start_index']}/{r['end_index']}")
        print(f"offset slice    : {r['offset_slice']!r}")
        ctx = " ".join(r["context"].split())
        print(f"context         : {ctx}")
        print()

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY_PATH.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"# wrote {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
