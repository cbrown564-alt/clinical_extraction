"""Reproduce a development-only wording screen; this is not clinical annotation."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

MARKERS = (
    r"\b(?:no|not|never|neither|nor|none|without|den\w*|absen\w*|free|ceased|stopped|resolved|"
    r"less|fewer|rare\w*|infrequent\w*)\b|n['’]t"
)
NEGATIVE = r"\b(?:no|not|never|neither|nor|without|denies|deny|denied)\b|n['’]t"
STRONG = r"\b(?:not|never|neither|nor|denies|deny|denied)\b|n['’]t"
RATE = (
    r"\b(?:daily|weekly|monthly|yearly|frequency|frequent|rate|count|cadence|cluster\w*|"
    r"per|times|twice|once|every|more|less|fewer)\b"
)
EXAMPLES = [
    (16961, "no more than twice weekly", "upper_bound"),
    (1772, "These were not clustered", "qualitative_pattern"),
    (6029, "less frequent but not absent", "qualitative_frequency"),
    (9496, "No generalised tonic-clonic seizures since March 2018", "event_scoped_seizure_freedom"),
    (763, "no change in the weekly occurrence of events", "unchanged_frequency"),
    (10003, "number per cluster not documented", "missing_measurement"),
]


def main() -> None:
    manifest_path = Path("data/Gan (2026)/splits/gan2026_split_v1.json")
    manifest = json.loads(manifest_path.read_text())
    data_path = Path(manifest["dataset_path"])
    raw = data_path.read_bytes()
    data_hash = hashlib.sha256(raw).hexdigest()
    assert data_hash == manifest["dataset_sha256"]
    eligible = set(manifest["splits"]["validation"]["source_row_indices"])
    rows = [r for r in json.loads(raw) if r["source_row_index"] in eligible]
    assert len(rows) == len(eligible) == 750
    markers = re.compile(MARKERS, re.I)
    negative = re.compile(NEGATIVE, re.I)
    strong = re.compile(STRONG, re.I)
    rate = re.compile(RATE, re.I)
    hits, forward, backward = [], [], []
    for row in rows:
        for match in re.finditer(r"[^.!?\n]+(?:[.!?]|$)", row["clinic_date"]):
            sentence = match.group().strip()
            if not markers.search(sentence):
                continue
            hit = {"source_row_index": row["source_row_index"], "sentence": sentence}
            hits.append(hit)
            if any(
                rate.search(sentence[n.start() : n.end() + 95]) for n in negative.finditer(sentence)
            ):
                forward.append(hit)
            elif any(
                rate.search(sentence[max(0, n.start() - 95) : n.end() + 40])
                for n in strong.finditer(sentence)
            ):
                backward.append(hit)
    by_id = {r["source_row_index"]: r for r in rows}
    examples = []
    for identifier, quote, interpretation in EXAMPLES:
        assert quote in by_id[identifier]["clinic_date"]
        examples.append(
            {
                "source_row_index": identifier,
                "quote": quote,
                "representation_without_negation_field": interpretation,
            }
        )
    local = Path("runs/one_shot_frequency_v2_measurements/negation_audit")
    local.mkdir(parents=True, exist_ok=True)
    (local / "review_candidates.json").write_text(json.dumps(forward + backward, indent=2) + "\n")
    summary = {
        "dataset": "Gan 2026 synthetic",
        "split": "dev750",
        "rows_screened": len(rows),
        "row_policy": "all dev750, including row_ok=False; excluded splits not inspected",
        "row_ok_false_included": sum(not r["row_ok"] for r in rows),
        "dataset_sha256": data_hash,
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "method": "sentence/line lexical screen then forward/backward rate-adjacent candidates",
        "patterns": {"markers": MARKERS, "negative": NEGATIVE, "strong": STRONG, "rate": RATE},
        "marker_sentence_hits": len(hits),
        "letters_with_markers": len({h["source_row_index"] for h in hits}),
        "forward_candidates": len(forward),
        "additional_backward_candidates": len(backward),
        "candidate_sentences": len(forward) + len(backward),
        "examples": examples,
        "limits": "Targeted lexical screen, not exhaustive linguistic or clinical annotation. "
        "Counts are retrieval counts, not prevalence estimates for negation.",
        "scoring": "none; no gold labels, predictions or scorer used",
        "model_calls": 0,
    }
    output = Path(
        "results/letter-benchmarks/gan/one_shot_frequency_v2_no_call/dev750_negation_audit.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: summary[k]
                for k in (
                    "rows_screened",
                    "row_ok_false_included",
                    "marker_sentence_hits",
                    "candidate_sentences",
                )
            }
        )
    )


if __name__ == "__main__":
    main()
