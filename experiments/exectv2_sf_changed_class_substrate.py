"""Build the per-letter substrate for the SF `changed`-class row-by-row adjudication.

For every dev letter where gold OR the P2-mini verify run emits a SeizureFrequency
`changed` state, dump: full note text, all gold SF mentions (offsets, FC, N, CUI,
derived state), all pred SF mentions, the changed-class diff (TP/FP/FN), and a
change-lexeme scan. Writes one markdown file per letter into the output dir + an index.

Usage:  uv run python experiments/exectv2_sf_changed_class_substrate.py [OUTPUT_DIR]
        (default OUTPUT_DIR = ./_sf_changed_letters)

Doc: docs/experiments/exectv2/seizure_frequency/exectv2_sf_changed_class_row_analysis_2026-06-29.md
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import frequency_state_faithful

ROOT = Path(__file__).resolve().parents[1]
RUN_PATH = ROOT / "experiments" / "exectv2_gepa_sf_verify_gpt41mini_20260628.jsonl"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("_sf_changed_letters")

LEXEMES = [
    r"decreas\w*",
    r"reduc\w*",
    r"improv\w*",
    r"declin\w*",
    r"lessen\w*",
    r"better\b",
    r"increas\w*",
    r"worsen\w*",
    r"escalat\w*",
    r"ris\w*",
    r"more frequent",
    r"less frequent",
    r"unchanged",
    r"stable",
    r"the same",
    r"no change",
    r"settl\w*",
    r"well controlled",
    r"poorly controlled",
    r"infrequent\w*",
    r"frequent\w*",
    r"\brare\b",
    r"rarely",
    r"best it'?s ever",
    r"deteriorat\w*",
    r"under control",
    r"breakthrough",
]
LEX_RE = re.compile("|".join(LEXEMES), re.IGNORECASE)


def state_of(attrs: dict) -> str:
    return frequency_state_faithful({str(k): str(v) for k, v in attrs.items()})


def load_preds(path: Path) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            out[row["letter_id"]] = row.get("predicted_mentions", [])
    return out


def fmt_gold(e) -> dict:
    a = {str(k): str(v) for k, v in e.attributes.items()}
    return {
        "text": e.raw_text,
        "span": [e.start_index, e.end_index],
        "FC": a.get("FrequencyChange", ""),
        "N": a.get("NumberOfSeizures", ""),
        "Lo": a.get("LowerNumberOfSeizures", ""),
        "Hi": a.get("UpperNumberOfSeizures", ""),
        "CUI": a.get("CUI", ""),
        "state": state_of(e.attributes),
    }


def fmt_pred(m: dict) -> dict:
    a = {str(k): str(v) for k, v in m.get("attributes", {}).items()}
    return {
        "text": m.get("text", ""),
        "FC": a.get("FrequencyChange", ""),
        "N": a.get("NumberOfSeizures", ""),
        "CUI": a.get("CUI", ""),
        "state": state_of(m.get("attributes", {})),
        "evidence": m.get("evidence", m.get("text", "")),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    letters = list(gepa_data.load_dev_letters())
    preds = load_preds(RUN_PATH)
    index = []

    for g in letters:
        gold_sf = list(g.entities("SeizureFrequency"))
        pred_sf = [m for m in preds.get(g.letter_id, []) if m.get("entity") == "SeizureFrequency"]
        gold_states = {state_of(e.attributes) for e in gold_sf}
        pred_states = {state_of(m.get("attributes", {})) for m in pred_sf}
        if "changed" not in (gold_states | pred_states):
            continue
        if "changed" in gold_states and "changed" in pred_states:
            verdict = "TP"
        elif "changed" in pred_states:
            verdict = "FP"
        else:
            verdict = "FN"

        gold_dump = [fmt_gold(e) for e in gold_sf]
        pred_dump = [fmt_pred(m) for m in pred_sf]
        hits = [(m.group(0), m.start()) for m in LEX_RE.finditer(g.note_text)]
        index.append(
            {
                "letter_id": g.letter_id,
                "verdict": verdict,
                "gold_states": sorted(gold_states),
                "pred_states": sorted(pred_states),
            }
        )

        lines = [
            f"# {g.letter_id} — changed-class {verdict}\n",
            f"gold_states = {sorted(gold_states)}",
            f"pred_states = {sorted(pred_states)}\n",
            "## GOLD SeizureFrequency mentions\n",
        ]
        lines += [
            f"- text={d['text']!r} state={d['state']} FC={d['FC'] or '-'} N={d['N'] or '-'} "
            f"Lo/Hi={d['Lo'] or '-'}/{d['Hi'] or '-'} CUI={d['CUI'] or '-'} span={d['span']}"
            for d in gold_dump
        ] or ["(none)"]
        lines += ["", "## PRED SeizureFrequency mentions\n"]
        lines += [
            f"- text={d['text']!r} state={d['state']} FC={d['FC'] or '-'} N={d['N'] or '-'} "
            f"CUI={d['CUI'] or '-'} evidence={d['evidence']!r}"
            for d in pred_dump
        ] or ["(none)"]
        lines += ["", "## Change-lexeme scan (full note)\n"]
        if hits:
            for tok, pos in hits:
                ctx = g.note_text[max(0, pos - 60) : pos + 60].replace("\n", " ")
                lines.append(f"- {tok!r} @ {pos}: ...{ctx}...")
        else:
            lines.append("(no explicit change lexeme found in note)")
        lines += ["", "## FULL LETTER TEXT\n", "```", g.note_text, "```"]
        (OUT / f"{g.letter_id}.md").write_text("\n".join(lines), encoding="utf-8")

    index.sort(key=lambda r: (r["verdict"], r["letter_id"]))
    (OUT / "_index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    from collections import Counter

    print(f"Wrote {len(index)} letters to {OUT}")
    print("verdicts:", dict(Counter(r["verdict"] for r in index)))


if __name__ == "__main__":
    main()
