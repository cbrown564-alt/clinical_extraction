"""``GoldCaseRow``: one clinical_headline disagreement, self-contained for adjudication.

Scope (deliberate v1 boundary): rows cover the ``clinical_headline`` layer only
-- the primary scored surface (ADR 0027) the medication-F1 question is actually
about -- not the full phrase/semantic/benchmark ladder. Only *disagreements*
(missed/spurious) are recorded, not every true positive; that's what the
existing Dx/SF/Rx/Inv row-analysis scripts already scope their substrate to,
and it's what a mechanism-share rollup needs.

Mirrors ``core/registry.py``'s read/write shape (full-rewrite sorted by id)
for consistency with the existing run registry.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .mechanism import MECHANISM_VALUES, VERDICT_VALUES, Mechanism, Verdict

#: A mention side of a disagreement: {"raw_text": str, "normalized_text": str,
#: "attributes": dict[str, str]}. ``None`` when that side is genuinely absent
#: (a "missed" row has no predicted mention carrying the key at all; a
#: "spurious" row has no gold mention carrying the key).
MentionRecord = dict[str, Any]

DisagreementType = str  # "missed" (FN: gold present, no matching prediction) | "spurious" (FP)

_DISAGREEMENT_TYPES: frozenset[str] = frozenset({"missed", "spurious"})


@dataclass(frozen=True)
class GoldCaseRow:
    """One clinical_headline disagreement for one (family, run_id, letter)."""

    row_id: str
    family: str
    run_id: str
    letter_id: str
    disagreement_type: DisagreementType
    match_key: str
    source_letter_text: str
    gold: MentionRecord | None
    pred: MentionRecord | None
    mechanism: str = Mechanism.UNADJUDICATED.value
    verdict: str = Verdict.UNADJUDICATED.value
    provenance: dict[str, Any] = field(
        default_factory=lambda: {
            "adjudicated_by": None,
            "adjudicated_at": None,
            "hypothesis_id": None,
            "reason": "",
        }
    )

    def to_json_record(self) -> dict[str, Any]:
        self.validate()
        return {
            "row_id": self.row_id,
            "family": self.family,
            "run_id": self.run_id,
            "letter_id": self.letter_id,
            "disagreement_type": self.disagreement_type,
            "match_key": self.match_key,
            "source_letter_text": self.source_letter_text,
            "gold": self.gold,
            "pred": self.pred,
            "mechanism": self.mechanism,
            "verdict": self.verdict,
            "provenance": self.provenance,
        }

    def validate(self) -> None:
        if self.disagreement_type not in _DISAGREEMENT_TYPES:
            raise ValueError(f"disagreement_type must be one of {sorted(_DISAGREEMENT_TYPES)}")
        if self.mechanism not in MECHANISM_VALUES:
            raise ValueError(f"mechanism must be one of {sorted(MECHANISM_VALUES)}")
        if self.verdict not in VERDICT_VALUES:
            raise ValueError(f"verdict must be one of {sorted(VERDICT_VALUES)}")
        if self.disagreement_type == "missed" and self.gold is None:
            raise ValueError("a 'missed' row must carry the gold mention it missed")
        if self.disagreement_type == "spurious" and self.pred is None:
            raise ValueError("a 'spurious' row must carry the spurious prediction")
        required = {"row_id": self.row_id, "family": self.family, "run_id": self.run_id,
                    "letter_id": self.letter_id, "match_key": self.match_key}
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise ValueError(f"gold case row missing required field(s): {', '.join(missing)}")


def gold_case_row_from_json_record(record: dict[str, Any]) -> GoldCaseRow:
    row = GoldCaseRow(
        row_id=record["row_id"],
        family=record["family"],
        run_id=record["run_id"],
        letter_id=record["letter_id"],
        disagreement_type=record["disagreement_type"],
        match_key=record["match_key"],
        source_letter_text=record["source_letter_text"],
        gold=record.get("gold"),
        pred=record.get("pred"),
        mechanism=record.get("mechanism", Mechanism.UNADJUDICATED.value),
        verdict=record.get("verdict", Verdict.UNADJUDICATED.value),
        provenance=record.get("provenance") or {
            "adjudicated_by": None, "adjudicated_at": None, "hypothesis_id": None, "reason": "",
        },
    )
    row.validate()
    return row


def load_gold_case_ledger(path: Path) -> list[GoldCaseRow]:
    """Load one family's newline-delimited gold case ledger."""

    if not path.exists():
        return []
    rows: list[GoldCaseRow] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(gold_case_row_from_json_record(json.loads(line)))
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid gold case row at {path}:{line_number}: {exc}") from exc
    return rows


def write_gold_case_ledger(rows: Sequence[GoldCaseRow], path: Path) -> None:
    """Write one family's ledger, sorted by row_id, full rewrite."""

    row_ids = [row.row_id for row in rows]
    duplicates = sorted({row_id for row_id in row_ids if row_ids.count(row_id) > 1})
    if duplicates:
        raise ValueError(f"duplicate row_id(s): {', '.join(duplicates)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(rows, key=lambda row: row.row_id)
    lines = [json.dumps(row.to_json_record(), ensure_ascii=False, sort_keys=True) for row in ordered]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
