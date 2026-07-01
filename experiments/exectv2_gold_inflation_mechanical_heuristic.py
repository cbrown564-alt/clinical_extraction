"""Item 4 of
``docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md``.

Question: can a MECHANICAL (zero-LLM) heuristic pull an ``H3_ORTHOGRAPHIC`` bucket out of
the existing ``H2_GENUINE_DIVERGENCE`` rows across all four ``*_ev_recall_consolidation_check``
family adjudications, so that a future family's evidence-recall gap can be triaged for the
Prescription-style "gold/letter typo breaks ``source_near``'s substring match" mechanism
*before* paying for LLM adjudication?

Method: for every H2_GENUINE_DIVERGENCE row, take the missed gold evidence span and compare
it (via edit distance over "content" tokens -- alphabetic tokens with >= 4 letters, so units/
doses/short test-type abbreviations don't dominate the comparison) against every candidate span
already produced by the model for the SAME letter and SAME family (Prescription/Investigations:
``pred_family_all`` from ``_cases.json``; SeizureFrequency: ``pred_sf_all``; Diagnosis: the
cached GEPA run's predicted Diagnosis mention texts for that letter, since the Dx ev-recall
artifact only stores canonicalized concept labels, not raw spans). A row is flagged
``H3_ORTHOGRAPHIC`` if the closest such pair is a near-miss: edit distance <= 2, OR edit
distance <= 15% of the longer token's length (transposition/deletion/substitution typos on
short drug names need the absolute floor; longer multi-syllable names need the relative one).
This mechanical span-similarity signal is the ONLY one usable pre-flight, before any adjudication
exists. A secondary, retrospective-only signal -- does the adjudicator's free-text ``reason``
column contain spelling/typo-indicative language -- is also computed and reported separately for
corroboration, but is NOT folded into the pre-flight-usable verdict (reason text doesn't exist
until after adjudication has already been paid for).

Inputs (all already on disk, zero LLM calls, zero re-adjudication):
  - ``_sf_ev_recall/_adjudication.csv`` + ``_sf_ev_recall/_cases.json``
  - ``_rx_inv_ev_recall/_adjudication.csv`` + ``_rx_inv_ev_recall/_cases.json``
  - ``experiments/exectv2_dx_evidence_recall_consolidation_check.json`` (Diagnosis has no
    standalone ev-recall CSV -- confirmed by reading
    ``experiments/exectv2_dx_evidence_recall_consolidation_check.py``: it writes only this
    JSON, reusing ``_dx_canonical/_adjudication.csv`` for verdicts and
    ``_dx_canonical/_index.json`` for canonicalized concept labels)
  - ``_dx_canonical/_adjudication.csv`` (reason text for the Dx secondary signal)
  - Gold dev letters (``gepa_data.load_dev_letters()``) and the cached GEPA prediction jsonl
    (``exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628.jsonl``) -- both already-on-disk
    deterministic artifacts, read the same way the Dx ev-recall script itself reads them; no LLM
    calls, no new predictions generated.

Output: ``experiments/exectv2_gold_inflation_mechanical_heuristic_output.csv`` -- one row per
H2_GENUINE_DIVERGENCE case across all four families, with the computed distance, the flag, and
the original verdict for cross-tabulation.

Usage: uv run python experiments/exectv2_gold_inflation_mechanical_heuristic.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"

SF_DIR = ROOT / "_sf_ev_recall"
RXINV_DIR = ROOT / "_rx_inv_ev_recall"
DX_CANONICAL = ROOT / "_dx_canonical"
DX_JSON = EXPERIMENTS / "exectv2_dx_evidence_recall_consolidation_check.json"
DX_PRED_RUN_ID = "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628"

OUT_CSV = EXPERIMENTS / "exectv2_gold_inflation_mechanical_heuristic_output.csv"

H1 = "H1_CARDINALITY"
H2 = "H2_GENUINE_DIVERGENCE"
H3 = "H3_ORTHOGRAPHIC"

# Distance thresholds (see module docstring). Absolute floor handles short-word single-edit
# typos (transposition/substitution) where the relative threshold would be too strict at low
# token lengths; relative ceiling handles longer names where >2 edits can still be one obvious
# typo relative to the word length.
ABS_DISTANCE_THRESHOLD = 2
REL_DISTANCE_THRESHOLD = 0.15
MIN_CONTENT_TOKEN_ALPHA = 4

REASON_TYPO_KEYWORDS = ("spell", "typo", "misspel", "transcri", "orthograph")


# --------------------------------------------------------------------------- #
# Edit distance (optimal string alignment: Levenshtein + adjacent transposition).
# No fuzzy-matching package (rapidfuzz / python-Levenshtein) is installed in this
# environment -- implemented directly rather than adding a new dependency for one script.
# --------------------------------------------------------------------------- #
def osa_distance(a: str, b: str) -> int:
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    d = [[0] * (lb + 1) for _ in range(la + 1)]
    for i in range(la + 1):
        d[i][0] = i
    for j in range(lb + 1):
        d[0][j] = j
    for i in range(1, la + 1):
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + cost)
    return d[la][lb]


def content_tokens(text: str) -> list[str]:
    """Alphabetic tokens with >= MIN_CONTENT_TOKEN_ALPHA letters (drops dose/unit/frequency
    noise like '250mg', 'bd', 'twice'-adjacent digits). Falls back to the full unfiltered token
    list when nothing survives the filter (needed for short entity names like 'MRI'/'EEG'/'CT'
    in Investigations, which would otherwise be dropped entirely)."""
    toks = normalize_phrase(text).split()
    filtered = [t for t in toks if sum(ch.isalpha() for ch in t) >= MIN_CONTENT_TOKEN_ALPHA]
    return filtered if filtered else toks


def best_orthographic_match(
    missed_texts: list[str], candidate_texts: list[str]
) -> dict | None:
    """Minimum edit-distance token pair across every (missed span, candidate span) combination.
    Returns None if either side has no usable tokens at all."""
    best = None
    for mt in missed_texts:
        for m_tok in content_tokens(mt):
            for ct in candidate_texts:
                for c_tok in content_tokens(ct):
                    dist = osa_distance(m_tok, c_tok)
                    ratio = dist / max(len(m_tok), len(c_tok))
                    if best is None or (dist, ratio) < (best["distance"], best["ratio"]):
                        best = {
                            "distance": dist,
                            "ratio": ratio,
                            "missed_token": m_tok,
                            "candidate_token": c_tok,
                            "candidate_text": ct,
                        }
    return best


def qualifies_h3(best: dict | None) -> bool:
    if best is None or best["distance"] == 0:
        return False
    return best["distance"] <= ABS_DISTANCE_THRESHOLD or best["ratio"] <= REL_DISTANCE_THRESHOLD


def reason_keyword_hit(reason: str) -> bool:
    low = reason.lower()
    return any(kw in low for kw in REASON_TYPO_KEYWORDS)


# --------------------------------------------------------------------------- #
# Per-family row extraction
# --------------------------------------------------------------------------- #
def sf_rows() -> list[dict]:
    adjud = list(csv.DictReader((SF_DIR / "_adjudication.csv").open(encoding="utf-8")))
    cases = {c["case_id"]: c for c in json.loads((SF_DIR / "_cases.json").read_text(encoding="utf-8"))}
    out = []
    for row in adjud:
        if row["mechanism"] != H2:
            continue
        case = cases[int(row["case_id"])]
        missed_texts = [case["gold_missed"]["text"]]
        candidate_texts = [p["text"] for p in case["pred_sf_all"]]
        out.append({
            "family": "SeizureFrequency",
            "letter_id": row["letter"],
            "row_key": row["case_id"],
            "verdict": row["verdict"],
            "missed_text": missed_texts[0],
            "candidate_texts": candidate_texts,
            "reason": row.get("reason", ""),
        })
    return out


def rx_inv_rows(entity: str) -> list[dict]:
    adjud = list(csv.DictReader((RXINV_DIR / "_adjudication.csv").open(encoding="utf-8")))
    cases = {
        (c["entity"], c["case_id"]): c
        for c in json.loads((RXINV_DIR / "_cases.json").read_text(encoding="utf-8"))
    }
    out = []
    for row in adjud:
        if row["entity"] != entity or row["mechanism"] != H2:
            continue
        case = cases[(entity, int(row["case_id"]))]
        missed_texts = [case["gold_missed"]["text"]]
        candidate_texts = [p["text"] for p in case["pred_family_all"]]
        out.append({
            "family": entity,
            "letter_id": row["letter"],
            "row_key": row["case_id"],
            "verdict": row["verdict"],
            "missed_text": missed_texts[0],
            "candidate_texts": candidate_texts,
            "reason": row.get("reason", ""),
        })
    return out


def dx_rows() -> list[dict]:
    dx_json = json.loads(DX_JSON.read_text(encoding="utf-8"))
    dx_reason = {
        (r["letter"], r["concept"]): r["reason"]
        for r in csv.DictReader((DX_CANONICAL / "_adjudication.csv").open(encoding="utf-8"))
        if r["direction"] == "MISSED"
    }

    gold_letters = {g.letter_id: g for g in gepa_data.load_dev_letters()}
    pred_rows = [
        json.loads(line)
        for line in (EXPERIMENTS / f"{DX_PRED_RUN_ID}.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    pred_dx_texts_by_letter: dict[str, list[str]] = {}
    for r in pred_rows:
        pred_dx_texts_by_letter[r["letter_id"]] = [
            m.get("text", "") for m in r.get("predicted_mentions", []) if m["entity"] == "Diagnosis"
        ]

    out = []
    for row in dx_json["rows"]:
        if row["mechanism"] != H2:
            continue
        letter_id, concept = row["letter_id"], row["concept"]
        gold_letter = gold_letters[letter_id]
        missed_texts = [
            a.text for a in gold_letter.entities("Diagnosis")
            if canonicalize_diagnosis_concept(a.text) == concept
        ]
        candidate_texts = pred_dx_texts_by_letter.get(letter_id, [])
        out.append({
            "family": "Diagnosis",
            "letter_id": letter_id,
            "row_key": concept,
            "verdict": row["adjudication_verdict"],
            "missed_text": missed_texts[0] if missed_texts else concept,
            "candidate_texts": candidate_texts,
            "reason": dx_reason.get((letter_id, concept), ""),
        })
    return out


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    all_rows = sf_rows() + rx_inv_rows("Prescription") + rx_inv_rows("Investigations") + dx_rows()

    out_records = []
    for row in all_rows:
        best = best_orthographic_match([row["missed_text"]], row["candidate_texts"])
        sim_hit = qualifies_h3(best)
        kw_hit = reason_keyword_hit(row["reason"])
        revised_mechanism = H3 if sim_hit else H2
        out_records.append({
            "family": row["family"],
            "letter_id": row["letter_id"],
            "row_key": row["row_key"],
            "original_mechanism": H2,
            "verdict": row["verdict"],
            "missed_text": row["missed_text"],
            "best_candidate_text": best["candidate_text"] if best else "",
            "best_missed_token": best["missed_token"] if best else "",
            "best_candidate_token": best["candidate_token"] if best else "",
            "edit_distance": best["distance"] if best else "",
            "distance_ratio": f"{best['ratio']:.3f}" if best else "",
            "text_similarity_hit": sim_hit,
            "reason_keyword_hit": kw_hit,
            "revised_mechanism": revised_mechanism,
            "reason": row["reason"],
        })

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_records[0].keys()))
        writer.writeheader()
        writer.writerows(out_records)
    print(f"Wrote {OUT_CSV} ({len(out_records)} rows)")

    # ------------------------------------------------------------------- #
    # Report: per-family before/after + verdict cross-tab
    # ------------------------------------------------------------------- #
    families = ["Diagnosis", "SeizureFrequency", "Prescription", "Investigations"]
    print("\n=== PER-FAMILY H2 -> H3 RECLASSIFICATION ===")
    print(f"{'family':<18}{'n_H2':>6}{'n_H3_sim':>10}{'n_H3_kw_only':>14}{'n_residual_H2':>16}")
    for fam in families:
        fam_rows = [r for r in out_records if r["family"] == fam]
        n_h2 = len(fam_rows)
        n_h3_sim = sum(1 for r in fam_rows if r["text_similarity_hit"])
        n_h3_kw_only = sum(1 for r in fam_rows if r["reason_keyword_hit"] and not r["text_similarity_hit"])
        n_residual = n_h2 - n_h3_sim
        print(f"{fam:<18}{n_h2:>6}{n_h3_sim:>10}{n_h3_kw_only:>14}{n_residual:>16}")

    print("\n=== VERDICT CROSS-TAB OF text_similarity_hit FLAGS (mechanical signal only) ===")
    print(f"{'family':<18}{'verdict':<20}{'flagged':>8}{'not_flagged':>12}")
    for fam in families:
        fam_rows = [r for r in out_records if r["family"] == fam]
        verdicts = sorted({r["verdict"] for r in fam_rows})
        for v in verdicts:
            sub = [r for r in fam_rows if r["verdict"] == v]
            flagged = sum(1 for r in sub if r["text_similarity_hit"])
            print(f"{fam:<18}{v:<20}{flagged:>8}{len(sub) - flagged:>12}")

    # ------------------------------------------------------------------- #
    # Kill-criterion: Prescription's 8 known MODEL_DEFENSIBLE H2 cases
    # (case_ids 1, 8, 9, 10, 11, 13, 17, 23 / letters EA0014, EA0056, EA0061, EA0072,
    # EA0093, EA0117, EA0152, EA0199 -- confirmed against
    # docs/experiments/exectv2/exectv2_rx_inv_ev_recall_consolidation_check_2026-06-30.md
    # lines 81-93). Of these, 7 are genuine spelling/transcription typos; EA0093 is a
    # brand/generic name split (Episenta vs Valproate) -- NOT an orthographic variant, so a
    # correct edit-distance heuristic should NOT flag it.
    # ------------------------------------------------------------------- #
    known_typo_case_ids = {"1", "8", "9", "10", "13", "17", "23"}  # 7 genuine typos
    known_brand_generic_case_id = "11"  # EA0093, expected NOT flagged

    rx_rows = [r for r in out_records if r["family"] == "Prescription"]
    rx_by_case = {r["row_key"]: r for r in rx_rows}

    print("\n=== KILL-CRITERION: Prescription known typo cases ===")
    recovered = []
    missed = []
    for cid in sorted(known_typo_case_ids, key=int):
        r = rx_by_case[cid]
        hit = r["text_similarity_hit"]
        (recovered if hit else missed).append((cid, r["letter_id"], r["missed_text"]))
        print(f"  case_id={cid:<3} letter={r['letter_id']:<8} missed={r['missed_text']!r:<28} "
              f"best_candidate={r['best_candidate_text']!r:<20} dist={r['edit_distance']} "
              f"ratio={r['distance_ratio']} -> {'RECOVERED' if hit else 'MISSED'}")
    bg = rx_by_case[known_brand_generic_case_id]
    print(f"  case_id={known_brand_generic_case_id} (EA0093, brand/generic, expected NOT flagged): "
          f"missed={bg['missed_text']!r} best_candidate={bg['best_candidate_text']!r} "
          f"dist={bg['edit_distance']} ratio={bg['distance_ratio']} -> "
          f"{'FLAGGED (unexpected)' if bg['text_similarity_hit'] else 'not flagged (as expected)'}")

    print(f"\nRecovered {len(recovered)}/7 genuine typo cases.")
    if missed:
        print(f"Missed: {missed}")

    inv_rows = [r for r in out_records if r["family"] == "Investigations"]
    inv_false_positives = [r for r in inv_rows if r["text_similarity_hit"]]
    print(f"\nInvestigations false positives (any H2 row flagged H3; family's H2 bucket is "
          f"100% GOLD_RIGHT per the source doc so ANY flag here is a false positive): "
          f"{len(inv_false_positives)}/{len(inv_rows)}")
    for r in inv_false_positives:
        print(f"  letter={r['letter_id']} missed={r['missed_text']!r} "
              f"best_candidate={r['best_candidate_text']!r} dist={r['edit_distance']} "
              f"ratio={r['distance_ratio']} verdict={r['verdict']}")

    # Secondary due-diligence: flags landing on GOLD_RIGHT-verdict rows in any family
    # (SF, Diagnosis, Prescription itself) are also mechanical-heuristic false positives,
    # since GOLD_RIGHT means the adjudicator already ruled the miss genuine.
    print("\n=== SECONDARY FALSE-POSITIVE CHECK: flags on GOLD_RIGHT-verdict rows, all families ===")
    gold_right_fp = [r for r in out_records if r["text_similarity_hit"] and r["verdict"] == "GOLD_RIGHT"]
    print(f"Total: {len(gold_right_fp)}")
    for r in gold_right_fp:
        print(f"  family={r['family']:<16} letter={r['letter_id']:<8} missed={r['missed_text']!r:<28} "
              f"best_candidate={r['best_candidate_text']!r:<20} dist={r['edit_distance']} ratio={r['distance_ratio']}")


if __name__ == "__main__":
    main()
