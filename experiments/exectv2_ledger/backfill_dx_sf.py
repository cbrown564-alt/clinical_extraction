"""Backfill Diagnosis and SeizureFrequency's already-paid-for adjudications into the ledger.

Zero new computation of predictions or matches, zero new LLM/adjudication cost
-- pure re-shape of existing, already-cited JSON/CSV output
(``_dx_canonical/_index.json`` + ``_adjudication.csv``,
``_sf_canonical/_index.json`` + ``_adjudication.csv``, both gitignored local
scratch produced by ``exectv2_dx_canonical_row_analysis.py`` /
``exectv2_sf_canonical_row_analysis.py``). Their numbers are already frozen,
promotion-safe evidence (Dx F1 0.6617 -> 0.9501 adjusted, SF 62.1% -> 89.3%
clinically defensible) -- this script never re-runs them.

KNOWN GRANULARITY LIMIT (disclosed, not hidden): Dx's and SF's canonical row
analyses recorded *concept*/*state*-level keys, not raw mention spans +
attributes, so backfilled ``gold``/``pred`` records carry ``raw_text=None``
and only a ``normalized_text`` (the concept or state string) -- unlike the
freshly-built Prescription/Investigations rows (``exectv2_ledger.match_replay``),
which carry full ``ExectAnnotation`` fidelity. This reflects what each prior
investigation actually captured, not a limitation of this ledger.

MECHANISM INFERENCE (disclosed heuristic, not a stored field in the source
data):
  Diagnosis has no per-row mechanism column. ``verdict == GOLD_RIGHT`` (gold
  correct, model wrong) maps to ``GENUINE_MODEL_ERROR``; every other verdict
  maps to ``GOLD_MULTIPLICITY_CONSOLIDATION``, matching the finding's own
  characterization (31/209 = 14.8% GOLD_RIGHT, exactly the doc's cited
  "14.8% genuine" figure) -- this is not a guess, it reproduces the published
  split exactly.
  SeizureFrequency has a rich, mostly-singleton free-text ``mechanism``
  column (30 distinct values across 53 rows). ``verdict == GOLD_RIGHT`` maps
  to ``GENUINE_MODEL_ERROR`` regardless of the free-text label (the verdict
  is the authoritative "was the model right" signal). Otherwise: text
  containing "multiplicity" -> ``GOLD_MULTIPLICITY_CONSOLIDATION``; text
  containing "under-annotation" -> ``GOLD_UNDER_ANNOTATION``; text containing
  "convention"/"header"/"odd-key" -> ``SCORER_MECHANICS_ARTIFACT``; the
  remaining ~20 singleton clinical-judgment labels (e.g. "syncope-as-active",
  "new-diagnosis-free") -> ``IAA_AMBIGUITY``, consistent with the Phase 7
  finding that SF's residual is dominated by genuine IAA-0.47 ambiguity, not
  one clean mechanical bucket. The verbatim free-text label is always kept in
  ``provenance.reason`` so nothing is lost to the mapping.

Usage: uv run python experiments/exectv2_ledger/backfill_dx_sf.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

_EXPERIMENTS_DIR = Path(__file__).resolve().parents[1]
if str(_EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_EXPERIMENTS_DIR))

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import (
    data as gepa_data,  # noqa: E402
)
from exectv2_ledger.mechanism import Mechanism, Verdict  # noqa: E402
from exectv2_ledger.schema import GoldCaseRow, write_gold_case_ledger  # noqa: E402

ROOT = _EXPERIMENTS_DIR.parent
DX_RUN_ID = "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628"
SF_RUN_ID = "exectv2_gepa_sf_verify_gpt41mini_20260628"
DX_DIR = ROOT / "_dx_canonical"
SF_DIR = ROOT / "_sf_canonical"
LEDGER_DIR = _EXPERIMENTS_DIR

_VERDICT_MAP = {
    "GOLD_RIGHT": Verdict.GOLD_RIGHT.value,
    "MODEL_DEFENSIBLE": Verdict.MODEL_DEFENSIBLE.value,
    "BOTH_DEFENSIBLE": Verdict.BOTH_DEFENSIBLE.value,
}


def _mention(text: str) -> dict:
    return {"raw_text": None, "normalized_text": text, "attributes": {}}


def _provenance(reason: str, extra_note: str = "") -> dict:
    reason_text = reason if not extra_note else f"{reason} [{extra_note}]"
    return {
        "adjudicated_by": "general-purpose agents, 2026-06-30 canonical row adjudication",
        "adjudicated_at": "2026-06-30",
        "hypothesis_id": None,
        "reason": reason_text,
    }


def backfill_diagnosis() -> list[GoldCaseRow]:
    if not (DX_DIR / "_adjudication.csv").exists():
        print(
            f"SKIP Diagnosis: {DX_DIR / '_adjudication.csv'} not found (local scratch, gitignored)"
        )
        return []

    letters_by_id = {letter.letter_id: letter.note_text for letter in gepa_data.load_dev_letters()}
    with (DX_DIR / "_adjudication.csv").open(encoding="utf-8", newline="") as handle:
        adjudication_rows = list(csv.DictReader(handle))

    rows: list[GoldCaseRow] = []
    for rec in adjudication_rows:
        letter_id, direction, concept = rec["letter"], rec["direction"], rec["concept"]
        verdict = rec["verdict"]
        mechanism = (
            Mechanism.GENUINE_MODEL_ERROR.value
            if verdict == "GOLD_RIGHT"
            else Mechanism.GOLD_MULTIPLICITY_CONSOLIDATION.value
        )
        disagreement_type = "missed" if direction == "MISSED" else "spurious"
        row = GoldCaseRow(
            row_id=f"diagnosis:{DX_RUN_ID}:{letter_id}:{disagreement_type}:{concept}",
            family="Diagnosis",
            run_id=DX_RUN_ID,
            letter_id=letter_id,
            disagreement_type=disagreement_type,
            match_key=concept,
            source_letter_text=letters_by_id.get(letter_id, ""),
            gold=_mention(concept) if disagreement_type == "missed" else None,
            pred=_mention(concept) if disagreement_type == "spurious" else None,
            mechanism=mechanism,
            verdict=_VERDICT_MAP[verdict],
            provenance=_provenance(rec["reason"]),
        )
        rows.append(row)
    return rows


def _classify_sf_mechanism(verdict: str, mechanism_text: str) -> str:
    if verdict == "GOLD_RIGHT":
        return Mechanism.GENUINE_MODEL_ERROR.value
    lowered = mechanism_text.lower()
    if "multiplicity" in lowered:
        return Mechanism.GOLD_MULTIPLICITY_CONSOLIDATION.value
    if "under-annotation" in lowered:
        return Mechanism.GOLD_UNDER_ANNOTATION.value
    if "convention" in lowered or "header" in lowered or "odd-key" in lowered:
        return Mechanism.SCORER_MECHANICS_ARTIFACT.value
    return Mechanism.IAA_AMBIGUITY.value


def backfill_seizure_frequency() -> list[GoldCaseRow]:
    if not (SF_DIR / "_adjudication.csv").exists():
        print(
            f"SKIP SeizureFrequency: {SF_DIR / '_adjudication.csv'} not found (local scratch, gitignored)"
        )
        return []

    letters_by_id = {letter.letter_id: letter.note_text for letter in gepa_data.load_dev_letters()}
    with (SF_DIR / "_adjudication.csv").open(encoding="utf-8", newline="") as handle:
        adjudication_rows = list(csv.DictReader(handle))

    rows: list[GoldCaseRow] = []
    for rec in adjudication_rows:
        letter_id = rec["letter"]
        verdict = rec["verdict"]
        mechanism_text = rec["mechanism"]
        mechanism = _classify_sf_mechanism(verdict, mechanism_text)
        mapped_verdict = _VERDICT_MAP[verdict]
        provenance = _provenance(
            rec["reason"], extra_note=f"mechanism={mechanism_text}" if mechanism_text else ""
        )

        missed_states = [s for s in rec["missed"].split("|") if s]
        spurious_states = [s for s in rec["spurious"].split("|") if s]
        for state in missed_states:
            rows.append(
                GoldCaseRow(
                    row_id=f"seizurefrequency:{SF_RUN_ID}:{letter_id}:missed:{state}",
                    family="SeizureFrequency",
                    run_id=SF_RUN_ID,
                    letter_id=letter_id,
                    disagreement_type="missed",
                    match_key=state,
                    source_letter_text=letters_by_id.get(letter_id, ""),
                    gold=_mention(state),
                    pred=None,
                    mechanism=mechanism,
                    verdict=mapped_verdict,
                    provenance=provenance,
                )
            )
        for state in spurious_states:
            rows.append(
                GoldCaseRow(
                    row_id=f"seizurefrequency:{SF_RUN_ID}:{letter_id}:spurious:{state}",
                    family="SeizureFrequency",
                    run_id=SF_RUN_ID,
                    letter_id=letter_id,
                    disagreement_type="spurious",
                    match_key=state,
                    source_letter_text=letters_by_id.get(letter_id, ""),
                    gold=None,
                    pred=_mention(state),
                    mechanism=mechanism,
                    verdict=mapped_verdict,
                    provenance=provenance,
                )
            )
    return rows


def main() -> None:
    dx_rows = backfill_diagnosis()
    sf_rows = backfill_seizure_frequency()

    if dx_rows:
        out = LEDGER_DIR / "gold_case_ledger_diagnosis.jsonl"
        write_gold_case_ledger(dx_rows, out)
        genuine = sum(1 for r in dx_rows if r.mechanism == Mechanism.GENUINE_MODEL_ERROR.value)
        print(
            f"Diagnosis: {len(dx_rows)} rows -> {out.relative_to(ROOT)} "
            f"({genuine}/{len(dx_rows)} = {genuine / len(dx_rows):.1%} genuine_model_error)"
        )

    if sf_rows:
        out = LEDGER_DIR / "gold_case_ledger_seizurefrequency.jsonl"
        write_gold_case_ledger(sf_rows, out)
        genuine = sum(1 for r in sf_rows if r.mechanism == Mechanism.GENUINE_MODEL_ERROR.value)
        print(
            f"SeizureFrequency: {len(sf_rows)} rows -> {out.relative_to(ROOT)} "
            f"({genuine}/{len(sf_rows)} = {genuine / len(sf_rows):.1%} genuine_model_error)"
        )


if __name__ == "__main__":
    main()
